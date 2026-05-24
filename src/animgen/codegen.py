import re

from .docs_search import format_snippets
from .groq_clients import get_manim_client, get_repair_client

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


def strip_markdown_fences(text: str) -> str:
    text = text.strip()
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    return text


def generate_code(prompt: str, router_result: dict, snippets: list[dict]) -> str:
    client, model = get_manim_client()
    docs_text = format_snippets(snippets)
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
    except Exception:
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
    code = strip_markdown_fences(raw)
    return code


def repair_code(prompt: str, bad_code: str, error: str, snippets: list[dict]) -> str:
    client, model = get_repair_client()
    docs_text = format_snippets(snippets)
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
    code = strip_markdown_fences(raw)
    return code
