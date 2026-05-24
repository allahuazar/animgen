from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .manim_codegen import check_layout_risks, generate_manim_code, repair_manim_code, validate_manim_code
from .manim_docs_search import search_manim_docs
from .manim_runner import render_manim, SCENE_FILE
from .router import route_prompt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUTPUT_DIR = ROOT / "output"
MEDIA_DIR = ROOT / "media"

for d in [OUTPUT_DIR, MEDIA_DIR]:
    d.mkdir(exist_ok=True)

app = FastAPI(title="Animgen API", version="0.4.0")


class PromptRequest(BaseModel):
    prompt: str


class SearchRequest(BaseModel):
    queries: list[str]


def _ok(data: dict, status: int = 200) -> JSONResponse:
    return JSONResponse(content={"ok": True, **data}, status_code=status)


def _err(msg: str, status: int = 400, details: list | None = None) -> JSONResponse:
    return JSONResponse(content={"ok": False, "error": msg, "warnings": [], "details": details or []}, status_code=status)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/route")
def route(req: PromptRequest):
    result = route_prompt(req.prompt)
    return _ok(result)


@app.post("/search-manim-docs")
def search_docs(req: SearchRequest):
    snippets = search_manim_docs(req.queries)
    return _ok({"snippets": snippets, "count": len(snippets)})


@app.post("/generate-manim")
def generate_manim(req: PromptRequest):
    router_result = route_prompt(req.prompt)
    if router_result.get("intent") == "unsupported":
        return _err(f"Unsupported request: {router_result.get('reason', 'unknown')}")
    snippets = search_manim_docs(router_result.get("search_queries", [req.prompt]))
    try:
        code = generate_manim_code(req.prompt, router_result, snippets)
    except ValueError as e:
        return _err("Unsafe generated code rejected", details=[str(e)])
    warnings = check_layout_risks(code)
    OUTPUT_DIR.mkdir(exist_ok=True)
    SCENE_FILE.write_text(code, encoding="utf-8")
    return _ok({
        "router": router_result,
        "snippets": snippets,
        "code": code,
        "warnings": warnings,
    })


@app.post("/render-manim")
def render_manim_endpoint():
    result = render_manim()
    if not result["ok"]:
        return _err(result["error"], status=500)
    return _ok(result)


@app.post("/generate-and-render-manim")
def generate_and_render(req: PromptRequest):
    router_result = route_prompt(req.prompt)
    if router_result.get("intent") == "unsupported":
        return _err(f"Unsupported request: {router_result.get('reason', 'unknown')}")

    snippets = search_manim_docs(router_result.get("search_queries", [req.prompt]))
    try:
        code = generate_manim_code(req.prompt, router_result, snippets)
    except ValueError as e:
        return _err("Unsafe generated code rejected", details=[str(e)])

    OUTPUT_DIR.mkdir(exist_ok=True)
    SCENE_FILE.write_text(code, encoding="utf-8")

    render_result = render_manim()
    repaired = False

    if not render_result["ok"]:
        error_text = render_result.get("stderr", "") or render_result.get("error", "")
        repair_snippets = search_manim_docs(["error", "fix", "common_errors"])
        try:
            repaired_code = repair_manim_code(req.prompt, code, error_text, repair_snippets)
            SCENE_FILE.write_text(repaired_code, encoding="utf-8")
            code = repaired_code
            render_result = render_manim()
            repaired = True
        except ValueError as e:
            return _err("Generation succeeded but render failed and repair failed", details=[str(e)])

    warnings = check_layout_risks(code)

    return _ok({
        "router": router_result,
        "code": code,
        "warnings": warnings,
        "video_url": render_result.get("video_url"),
        "render": render_result,
        "repaired": repaired,
    })


@app.get("/files")
def list_files():
    output_files = []
    if SCENE_FILE.exists():
        output_files.append({"name": "generated_scene.py", "path": "output/generated_scene.py", "size": SCENE_FILE.stat().st_size})
    video_url = None
    from .manim_runner import find_video
    v = find_video()
    if v:
        video_url = v
    return _ok({
        "output": output_files,
        "video_url": video_url,
    })


if OUTPUT_DIR.exists():
    app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

if MEDIA_DIR.exists():
    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

FRONTEND_DIR = ROOT / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
