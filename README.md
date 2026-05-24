# Animgen

AI-powered Manim animation generator. Enter a prompt like "Animate solving x + 5 = 12 for Class 8 students" and Animgen uses Groq to plan, generate, and render a Manim animation video.

## Architecture

```
User prompt
  → Router LLM (classifies intent, generates search queries, scene plan)
  → Local docs search (keyword match on docs_rag/manim/)
  → Codegen LLM (generates Manim Python code)
  → Manim renderer (runs manim -ql)
  → MP4 video
```

Generated scenes include `fit_to_screen()` helper and layout warnings to keep animations in the viewport.

## Setup

```bash
uv sync
```

Install Manim system deps (Arch):

```bash
sudo pacman -S ffmpeg cairo pango texlive-bin texlive-basic texlive-latex texlive-latexrecommended texlive-fontsrecommended texlive-latexextra dvisvgm
```

## Environment

Copy `.env.example` to `.env` and set three Groq API keys (can all be the same key):

```
GROQ_ROUTER_API_KEY=gsk_...
GROQ_MANIM_API_KEY=gsk_...
GROQ_REPAIR_API_KEY=gsk_...
GROQ_ROUTER_MODEL=openai/gpt-oss-20b
GROQ_MANIM_MODEL=qwen-2.5-coder-32b
GROQ_REPAIR_MODEL=openai/gpt-oss-20b
```

## Run backend

```bash
uv run uvicorn animgen.api:app --reload --port 8000
```

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Workflow

1. Enter a prompt (e.g. "Animate solving x + 5 = 12 for Class 8 students")
2. Click **Generate + Render** to run the full pipeline
3. Or step through: Route → Search Docs → Generate Code → Render

## Clean generated files

```bash
uv run python clean.py --dry-run    # preview what will be deleted
uv run python clean.py --yes        # delete without confirmation
uv run python clean.py              # interactive mode with confirmation
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/route` | Router LLM → intent + search queries + scene plan |
| POST | `/search-manim-docs` | Keyword search on `docs_rag/manim/` |
| POST | `/generate-manim` | Route + search + generate Manim code |
| POST | `/render-manim` | Render `output/generated_scene.py` to MP4 |
| POST | `/generate-and-render-manim` | Full pipeline + auto-repair on failure |
| GET | `/files` | List generated files |

API responses include `warnings[]` for layout risks (e.g. large font sizes, big shifts, oversized NumberLines).

## Project structure

```
├── src/animgen/
│   ├── api.py              # FastAPI server
│   ├── groq_clients.py     # OpenAI client per role
│   ├── router.py           # Router LLM
│   ├── manim_docs_search.py # Keyword docs search
│   ├── manim_codegen.py    # Code generation + repair + layout validation
│   └── manim_runner.py     # Manim CLI wrapper
├── docs_rag/manim/         # Local Manim reference docs
├── output/                 # Generated .py files
├── media/                  # Rendered MP4 videos
├── frontend/               # Vite React SPA
├── clean.py                # Cleanup script
├── pyproject.toml
└── .env.example
```

## Troubleshooting

- **Video goes out of frame** — regenerate or repair; layout warnings in the UI will show risky code (large font sizes, big shifts, oversized elements)
- **Render fails** — the repair LLM will attempt to fix the code automatically
- **MathTex errors** — prefer Text over MathTex for MVP (avoids LaTeX dependency)

## Limitations

- **Manim-only MVP** — no Typst, no PDF extraction, no textbook RAG
- **Local docs search** — simple keyword/regex matching, no embeddings
- **Generated code is validated** but still experimental — long or complex animations may fail
- **Groq rate limits** — free tier is ~8000 TPM; upgrade for heavier use
- **Repair loop** — if render fails, the repair LLM gets one attempt to fix the code
