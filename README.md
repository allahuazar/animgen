# Animgen

Minimal FastAPI + React frontend for turning textbook content into lesson assets.

## Architecture

```text
PDF textbook
  → PyMuPDF4LLM (markdown extraction)
    → lesson JSON (structured glue)
      → Typst (worksheet PNG)
      → Manim (animation video)
```

The lesson JSON is the shared data structure — edit it once in the UI, render both formats.

## Quick start

```bash
uv sync
```

Install Manim system deps (Arch):

```bash
sudo pacman -S ffmpeg cairo pango texlive-bin texlive-basic texlive-latex texlive-latexrecommended texlive-fontsrecommended texlive-latexextra dvisvgm
```

### Backend

```bash
uv run uvicorn src.animgen.api:app --reload --port 8000
```

### Frontend (dev mode)

```bash
cd frontend && npm run dev
```

Open `http://localhost:5173`.

### Production (single server)

```bash
cd frontend && npm run build
uv run uvicorn src.animgen.api:app --port 8000
```

Open `http://localhost:8000`.

## API

| Method | Path | What it does |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/upload-pdf` | Upload PDF → extract markdown |
| GET | `/markdown` | List / retrieve markdown files |
| POST | `/lesson-json` | Validate and save lesson JSON |
| POST | `/render/typst` | Lesson JSON → Typst source + PNG |
| POST | `/render/manim` | Lesson JSON → Manim scene + MP4 |
| GET | `/files` | List all generated files |

## Project structure

```text
├── src/animgen/
│   ├── api.py              # FastAPI server
│   ├── models.py           # Pydantic Lesson model
│   ├── pdf_to_llm.py       # PDF → markdown (PyMuPDF4LLM)
│   ├── typst_renderer.py   # Lesson → Typst PNG
│   └── manim_renderer.py   # Lesson → Manim video
├── frontend/               # Vite React SPA
│   ├── src/App.jsx         # Main UI component
│   └── vite.config.js      # Dev proxy → :8000
├── input/                  # Uploaded PDFs
├── parsed/                 # Extracted markdown + lesson JSON
├── output/                 # Typst PNGs, generated scene files
├── media/                  # Manim videos
├── pyproject.toml
└── README.md
```

## How it works

1. **Upload a PDF** — the server extracts markdown via PyMuPDF4LLM and saves it to `parsed/`.
2. **Preview the markdown** — select any parsed file in the UI.
3. **Edit the lesson JSON** — the default Photosynthesis example is pre-loaded. Tweak titles, key points, formulas, and quiz questions.
4. **Render Typst** — the server builds a Typst document from the lesson JSON and compiles it to PNG (via `typst-py`). The result appears inline.
5. **Render Manim** — the server generates a Manim Python scene from the lesson JSON and runs the CLI to produce an MP4. The video appears inline.
6. **Browse files** — the Files tab lists everything in `input/`, `parsed/`, `output/`, and `media/` with direct links.

All generation happens server-side. The frontend only sends/receives JSON.

## Notes

Generated files are git-ignored:

```text
input/
parsed/
rag/
output/
media/
typst-output/
```

Keep textbooks and generated content out of the repository unless you have permission to publish them.
