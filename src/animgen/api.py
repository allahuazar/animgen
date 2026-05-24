from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .pipeline import generate_and_render, generate_manim, render_manim
from .router import route_prompt
from .runner import find_latest_video
from .docs_search import search_docs

app = FastAPI(title="Animgen API", version="0.5.0")


class PromptRequest(BaseModel):
    prompt: str


class SearchRequest(BaseModel):
    queries: list[str]


def _ok(data: dict, status: int = 200) -> JSONResponse:
    return JSONResponse(content={"ok": True, **data}, status_code=status)


def _err(msg: str, status: int = 400, details: list | None = None) -> JSONResponse:
    return JSONResponse(content={"ok": False, "error": msg, "details": details or []}, status_code=status)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/route")
def route(req: PromptRequest):
    result = route_prompt(req.prompt)
    return _ok(result)


@app.post("/search-docs")
def search_docs_endpoint(req: SearchRequest):
    snippets = search_docs(req.queries)
    return _ok({"snippets": snippets, "count": len(snippets)})


@app.post("/generate-manim")
def generate_manim_endpoint(req: PromptRequest):
    result = generate_manim(req.prompt)
    if not result["ok"]:
        return _err(result.get("error", "Generation failed"))
    return _ok({
        "router": result["router"],
        "snippets": result["snippets"],
        "code": result["code"],
        "warnings": result["warnings"],
    })


@app.post("/render-manim")
def render_manim_endpoint():
    result = render_manim()
    if not result["ok"]:
        return _err(result["error"], status=500)
    return _ok(result)


@app.post("/generate-and-render")
def generate_and_render_endpoint(req: PromptRequest):
    result = generate_and_render(req.prompt)
    if not result["ok"]:
        return _err(result.get("error", "Pipeline failed"), details=result.get("details"))
    return _ok({
        "router": result["router"],
        "code": result["code"],
        "warnings": result["warnings"],
        "video_url": result.get("video_url"),
        "render": result.get("render"),
        "repaired": result.get("repaired"),
    })


@app.get("/files")
def list_files():
    output_files = []
    if config.GENERATED_SCENE_PATH.exists():
        output_files.append({
            "name": "generated_scene.py",
            "path": "output/generated_scene.py",
            "size": config.GENERATED_SCENE_PATH.stat().st_size,
        })
    video_url = find_latest_video()
    return _ok({
        "output": output_files,
        "video_url": video_url,
    })


if config.OUTPUT_DIR.exists():
    app.mount("/output", StaticFiles(directory=str(config.OUTPUT_DIR)), name="output")

if config.MEDIA_DIR.exists():
    app.mount("/media", StaticFiles(directory=str(config.MEDIA_DIR)), name="media")

FRONTEND_DIR = config.PROJECT_ROOT / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
