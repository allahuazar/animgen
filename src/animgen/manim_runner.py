import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUTPUT_DIR = ROOT / "output"
MEDIA_DIR = ROOT / "media"

SCENE_CLASS = "GeneratedScene"
SCENE_FILE = OUTPUT_DIR / "generated_scene.py"


def find_video() -> str | None:
    if not MEDIA_DIR.exists():
        return None
    candidates = sorted(MEDIA_DIR.rglob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    for c in candidates:
        if "partial_movie_files" not in c.parts:
            return str(c.relative_to(ROOT))
    return None


def render_manim() -> dict:
    if not SCENE_FILE.exists():
        return {"ok": False, "error": "No generated_scene.py found", "stdout": "", "stderr": ""}
    try:
        result = subprocess.run(
            ["uv", "run", "python", "-m", "manim", "-ql", str(SCENE_FILE), SCENE_CLASS],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Manim render timed out (180s)", "stdout": "", "stderr": ""}
    except FileNotFoundError:
        return {"ok": False, "error": "uv or manim not found. Is the virtualenv active?", "stdout": "", "stderr": ""}

    video_url = find_video()
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
