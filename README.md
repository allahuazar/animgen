# Animgen

Minimal Python wrappers for turning textbook content into lesson assets.

## What this does

Animgen is an experimental pipeline for educational content generation:

```text
PDF textbook
→ Markdown / RAG chunks
→ Typst worksheet/pages
→ Manim animation
````

## Modules

```text
src/animgen/pdf_to_llm.py      # Convert PDF to Markdown
src/animgen/typst_renderer.py  # Render lesson pages with Typst
src/animgen/manim_renderer.py  # Render lesson animations with Manim
```

## Setup

```bash
uv sync
```

If dependencies are not added yet:

```bash
uv add pymupdf4llm typst manim
```

Manim may also need system packages:

```bash
sudo pacman -S ffmpeg cairo pango texlive-bin texlive-basic texlive-latex texlive-latexrecommended texlive-fontsrecommended texlive-latexextra dvisvgm
```

## Usage

### 1. Convert PDF to Markdown

Put your PDF inside:

```text
input/
```

Then run:

```bash
uv run python src/animgen/pdf_to_llm.py
```

Output:

```text
parsed/
```

### 2. Render Typst lesson page

```bash
uv run python src/animgen/typst_renderer.py
```

Output:

```text
output/
```

### 3. Render Manim animation

```bash
uv run python -m manim -pql src/animgen/manim_renderer.py PhotosynthesisDemo
```

Output:

```text
media/videos/
```

## Project structure

```text
animgen/
├── src/animgen/
│   ├── pdf_to_llm.py
│   ├── typst_renderer.py
│   └── manim_renderer.py
├── input/
├── parsed/
├── rag/
├── output/
├── pyproject.toml
└── README.md
```

## Notes

Generated files are ignored by git:

```text
input/
parsed/
rag/
output/
media/
```

Keep textbooks and generated content out of the repository unless you have permission to publish them.

## Goal

Build a simple local pipeline for creating educational worksheets, previews, and animations from textbook content.
