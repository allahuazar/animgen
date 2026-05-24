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
- Make the animation clear for a student."""

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
