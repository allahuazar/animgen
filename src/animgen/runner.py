import subprocess
from pathlib import Path

from . import config


def find_latest_video() -> str | None:
    if not config.MEDIA_DIR.exists():
        return None
    candidates = sorted(config.MEDIA_DIR.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    for c in candidates:
        if "partial_movie_files" not in c.parts:
            return str(c.relative_to(config.PROJECT_ROOT))
    return None


def render_scene(scene_path: Path | None = None) -> dict:
    if scene_path is None:
        scene_path = config.GENERATED_SCENE_PATH
    if not scene_path.exists():
        return {"ok": False, "error": "No generated_scene.py found", "stdout": "", "stderr": ""}
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-m", "manim", "-ql", str(scene_path), "GeneratedScene"],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Manim render timed out (180s)", "stdout": "", "stderr": ""}
    except FileNotFoundError:
        return {"ok": False, "error": "uv or manim not found", "stdout": "", "stderr": ""}

    video_url = find_latest_video()
    if result.returncode != 0:
        return {
            "ok": False,
            "error": f"Manim exited with code {result.returncode}",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "video_url": video_url,
        }
    return {
        "ok": True,
        "video_url": video_url,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
