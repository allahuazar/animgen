from pathlib import Path
import typst

OUT_DIR = Path("typst-output")


def escape_typst(text: str) -> str:
    return (
        str(text)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("#", "\\#")
        .replace("$", "\\$")
    )


def make_bullets(items: list[str]) -> str:
    return "\n".join(f"- {escape_typst(item)}" for item in items)


def make_quiz(items: list[dict[str, str]]) -> str:
    output = []
    for index, item in enumerate(items, start=1):
        question = escape_typst(item["question"])
        answer = escape_typst(item["answer"])
        output.append(
            f"""
== Question {index}

{question}

#block(
  fill: rgb("#f3f4f6"),
  inset: 10pt,
  radius: 6pt,
)[
  *Answer:* {answer}
]
"""
        )
    return "\n".join(output)


def build_typst_source(lesson: dict) -> bytes:
    title = escape_typst(lesson["title"])
    subject = escape_typst(lesson["subject"])
    grade = escape_typst(lesson["grade"])
    summary = escape_typst(lesson["summary"])
    formula = escape_typst(lesson["formula"])

    key_points = make_bullets(lesson["key_points"])
    quiz = make_quiz(lesson["quiz"])

    source = f"""
#import "@preview/cetz:0.5.2"

#set page(
  paper: "a4",
  margin: 1.5cm,
)

#set text(
  size: 11pt,
)

#set heading(numbering: "1.")

#show heading: it => [
  #v(0.8em)
  #text(size: 15pt, weight: "bold")[#it.body]
  #v(0.4em)
]

#align(center)[
  #text(size: 24pt, weight: "bold")[{title}]
  #linebreak()
  #text(size: 11pt, fill: gray)[{grade} • {subject}]
]

#v(1em)

#block(
  fill: rgb("#f6f8fa"),
  inset: 12pt,
  radius: 8pt,
)[
  *Summary:* {summary}
]

= Key Points

{key_points}

= Main Formula

#block(
  fill: rgb("#fff7d6"),
  inset: 12pt,
  radius: 8pt,
)[
  #text(size: 14pt, weight: "bold")[{formula}]
]

= Simple Diagram

#cetz.canvas(length: 1cm, {{
  import cetz.draw: *

  rect(
    (0, 0),
    (12, 5),
    radius: 0.25,
    fill: rgb("#f4fff2"),
    stroke: rgb("#74a46f"),
  )

  circle(
    (2, 3.5),
    radius: 0.65,
    fill: rgb("#ffd166"),
    stroke: none,
  )
  content((2, 3.5), [Sun])

  line(
    (2.8, 3.4),
    (5, 2.8),
    mark: (end: ">"),
  )
  content((4, 3.35), [light])

  rect(
    (5.2, 1.5),
    (7.2, 3.4),
    radius: 0.25,
    fill: rgb("#95d5b2"),
    stroke: rgb("#40916c"),
  )
  content((6.2, 2.45), [Leaf])

  line(
    (4, 1),
    (5.1, 1.9),
    mark: (end: ">"),
  )
  content((3.6, 0.65), [CO₂])

  line(
    (6.2, 0.4),
    (6.2, 1.45),
    mark: (end: ">"),
  )
  content((6.2, 0.15), [Water])

  line(
    (7.3, 2.8),
    (9.3, 3.6),
    mark: (end: ">"),
  )
  content((9.9, 3.7), [O₂])

  line(
    (7.3, 1.9),
    (9.3, 1.2),
    mark: (end: ">"),
  )
  content((10, 1.1), [Glucose])
}})

= Quiz

{quiz}
"""

    return source.encode("utf-8")


def compile_png(source: bytes, output: str | Path | None = None) -> Path:
    if output is None:
        OUT_DIR.mkdir(exist_ok=True)
        output = OUT_DIR / "lesson-page-{n}.png"
    typst.compile(source, output=str(output), format="png", ppi=144.0)
    return Path(str(output).replace("{n}", "1"))


def render_lesson(lesson: dict, out_dir: str | Path = "output") -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    source = build_typst_source(lesson)
    typ_path = out_dir / "lesson.typ"
    typ_path.write_bytes(source)

    png_path = compile_png(source, out_dir / "lesson-page-{n}.png")

    return {
        "typst_source": source.decode("utf-8"),
        "files": [str(typ_path), str(png_path)],
    }


def main() -> None:
    LESSON = {
        "title": "Photosynthesis",
        "subject": "Biology",
        "grade": "Class 8",
        "summary": "Photosynthesis is the process by which green plants make their own food using sunlight, carbon dioxide, and water.",
        "key_points": [
            "Plants use chlorophyll to absorb sunlight.",
            "Carbon dioxide enters the leaf through stomata.",
            "Water is absorbed by the roots and transported to the leaves.",
            "The plant produces glucose as food.",
            "Oxygen is released as a by-product.",
        ],
        "formula": "6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂",
        "quiz": [
            {"question": "What is the green pigment in leaves called?", "answer": "Chlorophyll"},
            {"question": "Which gas is released during photosynthesis?", "answer": "Oxygen"},
            {"question": "What food does the plant produce?", "answer": "Glucose"},
        ],
    }
    result = render_lesson(LESSON)
    print("Done.")
    for f in result["files"]:
        print(f"  {f}")


if __name__ == "__main__":
    main()
