import os
import re
import subprocess
from pathlib import Path

SYSTEM_PROMPT = """You are an expert Manim animation generator. Given a lesson JSON, write a complete, working Manim scene.

## Rules
- Output ONLY valid Python code with a single class `AIScene(Scene)`.
- Use `from manim import *`.
- The `construct` method must contain all animation logic.
- Use clear, readable code with proper Manim API calls (Text, MathTex, Write, FadeIn, FadeOut, Transform, etc.).
- Make it visually engaging — use colors, positioning, and smooth transitions.
- Keep it under 120 lines. No external imports beyond manim.
- Never use `self.add()` for static elements that should animate in.
- End with `self.wait(2)`.

## Lesson JSON fields
- title: lesson title
- subject: topic area
- grade: grade level
- summary: short description
- key_points: list of bullet points
- formula: a mathematical or scientific formula
- quiz: list of {question, answer} objects

## Custom prompt
If the user provides a custom prompt below, incorporate it into the animation style or content. If not, create a clear pedagogical animation that explains the lesson step by step."""


def _extract_code(text: str) -> str | None:
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if blocks:
        return blocks[0].strip()
    m = re.search(r"class\s+\w+\s*\(.*?\)\s*:", text, re.DOTALL)
    if m:
        return text[m.start():].strip()
    return None


def _find_scene_class(code: str) -> str | None:
    m = re.search(r"class\s+(\w+)\s*\(.*?Scene.*?\)\s*:", code, re.DOTALL)
    return m.group(1) if m else None


def generate_scene_code(
    lesson: dict,
    api_key: str,
    prompt: str = "",
    model: str = "llama-3.3-70b-versatile",
) -> str:
    from groq import Groq

    client = Groq(api_key=api_key)

    lesson_str = (
        f"Title: {lesson.get('title', '')}\n"
        f"Subject: {lesson.get('subject', '')}\n"
        f"Grade: {lesson.get('grade', '')}\n"
        f"Summary: {lesson.get('summary', '')}\n"
        f"Key points: {', '.join(lesson.get('key_points', []))}\n"
        f"Formula: {lesson.get('formula', '')}\n"
        f"Quiz: {', '.join(q.get('question', '') for q in lesson.get('quiz', []))}"
    )

    user_msg = f"Lesson:\n{lesson_str}\n"
    if prompt:
        user_msg += f"\nCustom instructions: {prompt}"

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    raw = completion.choices[0].message.content or ""
    code = _extract_code(raw)
    if not code:
        raise ValueError("Groq did not return valid Python code:\n" + raw[:500])
    return code


def render_generated_code(code: str, out_dir: str | Path = "output") -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scene_class = _find_scene_class(code)
    if not scene_class:
        raise ValueError("No Scene subclass found in generated code")

    scene_path = out_dir / f"{scene_class.lower()}.py"
    scene_path.write_text(code, encoding="utf-8")

    result = subprocess.run(
        ["uv", "run", "python", "-m", "manim", "-pql", str(scene_path), scene_class],
        capture_output=True,
        text=True,
        timeout=120,
    )

    media_dir = Path("media")
    video_files = list(media_dir.rglob("*.mp4")) if media_dir.exists() else []
    video_files = [f for f in video_files if "partial_movie_files" not in f.parts]

    return {
        "scene_source": code,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "files": [str(f) for f in video_files],
        "scene_class": scene_class,
    }


def render_lesson(
    lesson: dict,
    api_key: str,
    prompt: str = "",
    model: str = "llama-3.3-70b-versatile",
    out_dir: str | Path = "output",
) -> dict:
    code = generate_scene_code(lesson, api_key, prompt, model)
    return render_generated_code(code, out_dir)
