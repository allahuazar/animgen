from pathlib import Path
import pymupdf4llm


def extract_markdown(pdf_path: str | Path) -> str:
    return pymupdf4llm.to_markdown(
        str(pdf_path),
        header=False,
        footer=False,
    )


def main() -> None:
    pdf = Path("input/class8_math2.pdf")
    out = Path("parsed/class8_math2.md")
    out.parent.mkdir(exist_ok=True)
    md = extract_markdown(pdf)
    out.write_text(md, encoding="utf-8")
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
