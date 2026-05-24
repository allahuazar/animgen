from pathlib import Path
import subprocess
import tempfile

SCENE_TEMPLATE = '''from manim import *


class LessonScene(Scene):
    def construct(self):
{body}
        self.wait(2)
'''


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _build_body(lesson: dict) -> str:
    lines = []
    title = _escape(lesson.get("title", ""))
    subject = _escape(lesson.get("subject", ""))
    summary = _escape(lesson.get("summary", ""))
    formula = _escape(lesson.get("formula", ""))
    key_points = lesson.get("key_points", [])
    quiz = lesson.get("quiz", [])

    lines.append(f'        t = Text("{title}", font_size=44).to_edge(UP)')
    lines.append(f'        s = Text("{subject}", font_size=26).next_to(t, DOWN)')
    lines.append('        self.play(Write(t), FadeIn(s))')
    lines.append('        self.wait(1)')
    lines.append('        self.play(FadeOut(t), FadeOut(s))')
    lines.append('        self.wait(0.5)')

    if summary:
        lines.append(f'        summary = Text("{summary}", font_size=26)')
        lines.append('        self.play(FadeIn(summary))')
        lines.append('        self.wait(2)')
        lines.append('        self.play(FadeOut(summary))')

    if key_points:
        lines.append('        kp_title = Text("Key Points", font_size=32).to_edge(UP)')
        lines.append('        self.play(Write(kp_title))')
        for i, kp in enumerate(key_points):
            text = _escape(kp)
            lines.append(f'        k{i} = Text("{text}", font_size=24)')
            lines.append(f'        k{i}.next_to(kp_title, DOWN, buff=0.4 + 0.6 * {i})')
            lines.append(f'        self.play(FadeIn(k{i}, shift=UP))')
            lines.append('        self.wait(0.3)')
        lines.append('        self.wait(1)')
        lines.append('        self.play(*[FadeOut(m) for m in self.mobjects])')

    if formula:
        lines.append(f'        f = Text("{formula}", font_size=36, color=YELLOW)')
        lines.append('        self.play(FadeIn(f))')
        lines.append('        self.wait(2)')
        lines.append('        self.play(FadeOut(f))')

    if quiz:
        lines.append('        q_title = Text("Quiz", font_size=32).to_edge(UP)')
        lines.append('        self.play(Write(q_title))')
        for i, q in enumerate(quiz):
            q_text = _escape(q.get("question", ""))
            a_text = _escape(q.get("answer", ""))
            lines.append(f'        q{i} = Text("Q{i+1}: {q_text}", font_size=24)')
            lines.append(f'        q{i}.next_to(q_title, DOWN, buff=0.4 + 1.5 * {i})')
            lines.append(f'        self.play(FadeIn(q{i}, shift=UP))')
            lines.append(f'        a{i} = Text("{a_text}", font_size=22, color=GREEN)')
            lines.append(f'        a{i}.next_to(q{i}, DOWN)')
            lines.append(f'        self.play(FadeIn(a{i}, shift=DOWN))')
            lines.append('        self.wait(1)')

    return "\n".join(lines)


def render_lesson(lesson: dict, out_dir: str | Path = "output") -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    body = _build_body(lesson)
    scene_source = SCENE_TEMPLATE.format(body=body)

    scene_path = out_dir / "lesson_scene.py"
    scene_path.write_text(scene_source, encoding="utf-8")

    result = subprocess.run(
        ["uv", "run", "python", "-m", "manim", "-pql", str(scene_path), "LessonScene"],
        capture_output=True,
        text=True,
        timeout=120,
    )

    media_dir = Path("media")
    video_files = list(media_dir.rglob("*.mp4")) if media_dir.exists() else []
    video_files = [f for f in video_files if "partial_movie_files" not in f.parts]

    return {
        "scene_source": scene_source,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
        "files": [str(f) for f in video_files],
    }


def main() -> None:
    lesson = {
        "title": "Photosynthesis",
        "subject": "Biology",
        "summary": "Green plants make food from sunlight.",
        "formula": "6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂",
        "key_points": [
            "Chlorophyll absorbs sunlight.",
            "CO₂ enters through stomata.",
        ],
        "quiz": [
            {"question": "What pigment absorbs light?", "answer": "Chlorophyll"},
        ],
    }
    result = render_lesson(lesson)
    print("Done.")
    for f in result.get("files", []):
        print(f"  {f}")


if __name__ == "__main__":
    main()
