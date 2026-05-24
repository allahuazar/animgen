import re

from .groq_clients import get_manim_client, get_repair_client
from .manim_docs_search import format_docs_snippets

CODEGEN_SYSTEM_PROMPT = """You are a Manim Community Edition v0.20.1 code generator.
Use the provided docs snippets as the source of truth.
Output Python code only.
No markdown fences.
No explanation.

Rules:
- Must start with: from manim import *
- May also use: import math
- Must define exactly: class GeneratedScene(Scene):
- Put all animation inside construct().
- Keep animation under 60 seconds.
- Prefer Text for formulas to avoid LaTeX issues.
- Use MathTex only when necessary.
- Do not use external files, images, audio, network, or user input.
- Do not use unsupported plugins.
- Keep code simple and reliable.
- Make the animation clear for a student.

Viewport-safe layout rules (Manim default frame: x: -6 to 6, y: -3.2 to 3.2):
- Use one title at the top with .to_edge(UP, buff=0.5)
- Use one main VGroup centered with .move_to(ORIGIN)
- Prefer VGroup(...).arrange(...) over manual coordinates
- After arranging, use .move_to(ORIGIN)
- Keep title font size between 36 and 44
- Keep equation font size between 32 and 40
- Keep explanation font size between 22 and 30
- Break long text into multiple Text objects
- NumberLine length should be 8-10, never above 12
- Axes should use reasonable x_length/y_length

Required: include this helper function inside construct():
def fit_to_screen(mobject):
    if mobject.width > 11:
        mobject.scale_to_fit_width(11)
    if mobject.height > 5.8:
        mobject.scale_to_fit_height(5.8)
    return mobject

Call fit_to_screen() on large VGroups before animating them.
Do not place important objects outside the frame.
Avoid large manual shifts — never use shifts greater than 4 units.
Avoid manual coordinates unless necessary for positioning.
Prefer ReplacementTransform(old, new) over Transform(old.copy(), new)."""

REJECTED_PATTERNS = [
    r"\bimport\s+os\b",
    r"\bimport\s+sys\b",
    r"\bimport\s+subprocess\b",
    r"from\s+pathlib\b",
    r"\bimport\s+pathlib\b",
    r"\bopen\s*\(",
    r"\bexec\s*\(",
    r"\beval\s*\(",
    r"\bimport\s+requests\b",
    r"\bimport\s+socket\b",
    r"\bimport\s+shutil\b",
    r"\b__import__\b",
    r"\binput\s*\(",
]

REQUIRED_PATTERNS = [
    r"from\s+manim\s+import\s+\*",
    r"class\s+GeneratedScene\s*\(\s*Scene\s*\)\s*:",
    r"def\s+fit_to_screen\s*\(",
]


def _extract_code(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    return text


def validate_manim_code(code: str) -> None:
    for pattern in REJECTED_PATTERNS:
        if re.search(pattern, code):
            raise ValueError(f"Generated Manim code contains rejected pattern: {pattern}")
    for pattern in REQUIRED_PATTERNS:
        if not re.search(pattern, code):
            raise ValueError(f"Generated Manim code missing required pattern: {pattern}")


def check_layout_risks(code: str) -> list[str]:
    warnings = []
    for m in re.finditer(r'font_size\s*=\s*(\d+)', code):
        val = int(m.group(1))
        if val > 56:
            warnings.append(f"font_size {val} > 56 may go out of viewport")
    for m in re.finditer(r'NumberLine\([^)]*?length\s*=\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(1))
        if val > 12:
            warnings.append(f"NumberLine length {val} > 12 may go out of viewport")
    for m in re.finditer(r'shift\(\s*(RIGHT|LEFT)\s*\*\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(2))
        if val >= 7:
            warnings.append(f"shift({m.group(1)} * {val}) >= 7 may go out of viewport")
    for m in re.finditer(r'shift\(\s*(UP|DOWN)\s*\*\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(2))
        if val >= 4:
            warnings.append(f"shift({m.group(1)} * {val}) >= 4 may go out of viewport")
    for m in re.finditer(r'x_length\s*=\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(1))
        if val > 12:
            warnings.append(f"x_length {val} > 12 may go out of viewport")
    for m in re.finditer(r'y_length\s*=\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(1))
        if val > 8:
            warnings.append(f"y_length {val} > 8 may go out of viewport")
    return warnings


def generate_manim_code(prompt: str, router_result: dict, docs_snippets: list[dict]) -> str:
    client, model = get_manim_client()
    docs_text = format_docs_snippets(docs_snippets)
    scene_plan = "\n".join(f"- {s}" for s in router_result.get("scene_plan", []))
    user_prompt = f"""Topic: {router_result.get('topic', prompt)}

Scene plan:
{scene_plan}

Relevant docs snippets:
{docs_text}

Generate the complete Manim code.
"""
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": CODEGEN_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=4096,
        )
    except Exception as e:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": CODEGEN_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
            max_tokens=4096,
        )
    raw = completion.choices[0].message.content or ""
    code = _extract_code(raw)
    validate_manim_code(code)
    return code


def repair_manim_code(prompt: str, bad_code: str, error: str, docs_snippets: list[dict]) -> str:
    client, model = get_repair_client()
    docs_text = format_docs_snippets(docs_snippets)
    user_prompt = f"""The following Manim code failed to render with this error:

Error:
{error}

Code:
```python
{bad_code}
```

Relevant docs snippets:
{docs_text}

Fix the code so it compiles and renders successfully.
If the content goes out of the viewport:
- Center content with .move_to(ORIGIN)
- Reduce font sizes
- Use VGroup arrange
- Add and call fit_to_screen()
- Avoid large shifts (max 4 units)
- Keep all important objects in the safe frame (x: -6 to 6, y: -3.2 to 3.2)
- Prefer Text over MathTex
Output Python code only. No markdown fences. No explanation.
"""
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": CODEGEN_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
    except Exception:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": CODEGEN_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )
    raw = completion.choices[0].message.content or ""
    code = _extract_code(raw)
    validate_manim_code(code)
    return code
