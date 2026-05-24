from pathlib import Path
import pymupdf4llm

PDF_PATH = Path("input/class8_math2.pdf")
OUT_PATH = Path("parsed/class8_math2.md")

OUT_PATH.parent.mkdir(exist_ok=True)

markdown = pymupdf4llm.to_markdown(
    str(PDF_PATH),
    header=False,
    footer=False,
)

OUT_PATH.write_text(markdown, encoding="utf-8")

print(f"Saved: {OUT_PATH}")
