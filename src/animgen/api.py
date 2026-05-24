from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Query, UploadFile
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

import os

from .models import Lesson
from .pdf_to_llm import extract_markdown
from .typst_renderer import render_lesson as render_typst
from .manim_renderer import render_lesson as render_manim
from .groq_manim import render_lesson as render_ai_manim

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

INPUT_DIR = ROOT / "input"
PARSED_DIR = ROOT / "parsed"
OUTPUT_DIR = ROOT / "output"
MEDIA_DIR = ROOT / "media"
FRONTEND_DIR = ROOT / "frontend" / "dist"

for d in [INPUT_DIR, PARSED_DIR, OUTPUT_DIR, MEDIA_DIR]:
    d.mkdir(exist_ok=True)

app = FastAPI(title="Animgen API", version="0.2.0")


# --- Helpers ---

def _list_files(directory: Path, suffix: str = "", recursive: bool = False) -> list[dict]:
    if not directory.exists():
        return []
    files = []
    it = directory.rglob("*") if recursive else directory.iterdir()
    for f in sorted(it):
        if f.name == ".gitkeep":
            continue
        rel = f.relative_to(ROOT)
        if "partial_movie_files" in rel.parts:
            continue
        if f.is_file() and (not suffix or f.suffix == suffix):
            files.append({
                "name": str(rel),
                "path": str(rel),
                "size": f.stat().st_size,
            })
    return files


def _ok(data: dict, status: int = 200) -> JSONResponse:
    return JSONResponse(content={"ok": True, **data}, status_code=status)


def _err(msg: str, status: int = 400) -> JSONResponse:
    return JSONResponse(content={"ok": False, "error": msg}, status_code=status)


# --- Endpoints ---

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return _err("Only PDF files are allowed")

    dest = INPUT_DIR / file.filename
    content = await file.read()
    dest.write_bytes(content)

    try:
        md = extract_markdown(dest)
    except Exception as e:
        return _err(f"Failed to extract markdown: {e}")

    stem = dest.stem
    md_path = PARSED_DIR / f"{stem}.md"
    md_path.write_text(md, encoding="utf-8")

    return _ok({
        "filename": file.filename,
        "markdown_file": str(md_path.relative_to(ROOT)),
        "markdown": md,
    })


@app.get("/markdown")
def get_markdown(filename: Optional[str] = Query(None)):
    files = _list_files(PARSED_DIR, ".md")
    if filename:
        md_path = PARSED_DIR / filename
        if not md_path.exists():
            return _err(f"Markdown file '{filename}' not found", 404)
        return _ok({
            "files": files,
            "content": md_path.read_text(encoding="utf-8"),
        })
    return _ok({"files": files})


@app.post("/lesson-json")
async def save_lesson_json(data: dict):
    try:
        lesson = Lesson(**data)
    except ValidationError as e:
        return _err(f"Invalid lesson JSON: {e}")

    path = PARSED_DIR / "lesson.json"
    path.write_text(lesson.model_dump_json(indent=2), encoding="utf-8")
    return _ok({"saved": str(path.relative_to(ROOT)), "lesson": lesson.model_dump()})


@app.post("/render/typst")
async def render_typst_endpoint(data: dict):
    try:
        lesson = Lesson(**data)
    except ValidationError as e:
        return _err(f"Invalid lesson JSON: {e}")

    try:
        result = render_typst(lesson.model_dump(), out_dir=OUTPUT_DIR)
    except Exception as e:
        return _err(f"Typst render failed: {e}")

    files = _list_files(OUTPUT_DIR)
    return _ok({
        "files": files,
        "typst_source": result.get("typst_source", ""),
    })


@app.post("/render/manim")
async def render_manim_endpoint(data: dict):
    try:
        lesson = Lesson(**data)
    except ValidationError as e:
        return _err(f"Invalid lesson JSON: {e}")

    try:
        result = render_manim(lesson.model_dump(), out_dir=OUTPUT_DIR)
    except Exception as e:
        return _err(f"Manim render failed: {e}")

    return _ok({
        "files": result.get("files", []),
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "returncode": result.get("returncode", -1),
    })


@app.post("/render/ai-manim")
async def render_ai_manim_endpoint(data: dict):
    try:
        lesson = Lesson(**data)
    except ValidationError as e:
        return _err(f"Invalid lesson JSON: {e}")

    lesson_dict = lesson.model_dump()
    api_key = data.get("groq_key") or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return _err("GROQ_API_KEY not set — pass groq_key in body or set env var")

    prompt = data.get("prompt", "")
    model = data.get("model", "llama-3.3-70b-versatile")

    try:
        result = render_ai_manim(
            lesson_dict,
            api_key=api_key,
            prompt=prompt,
            model=model,
            out_dir=OUTPUT_DIR,
        )
    except Exception as e:
        return _err(f"AI Manim render failed: {e}")

    return _ok({
        "files": result.get("files", []),
        "scene_source": result.get("scene_source", ""),
        "scene_class": result.get("scene_class", ""),
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "returncode": result.get("returncode", -1),
    })


@app.get("/files")
def list_files():
    return _ok({
        "input": _list_files(INPUT_DIR),
        "parsed": _list_files(PARSED_DIR),
        "output": _list_files(OUTPUT_DIR),
        "media": _list_files(MEDIA_DIR, ".mp4", recursive=True),
    })


# Mount static dirs for previews
if OUTPUT_DIR.exists():
    app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

if MEDIA_DIR.exists():
    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

if PARSED_DIR.exists():
    app.mount("/parsed", StaticFiles(directory=str(PARSED_DIR)), name="parsed")

# Serve frontend SPA for any unmatched route
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
