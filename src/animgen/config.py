import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
MEDIA_DIR = PROJECT_ROOT / "media"
DOCS_DIR = PROJECT_ROOT / "docs_rag" / "manim"
GENERATED_SCENE_PATH = OUTPUT_DIR / "generated_scene.py"

GROQ_ROUTER_API_KEY_ENV = "GROQ_ROUTER_API_KEY"
GROQ_MANIM_API_KEY_ENV = "GROQ_MANIM_API_KEY"
GROQ_REPAIR_API_KEY_ENV = "GROQ_REPAIR_API_KEY"
GROQ_ROUTER_MODEL_ENV = "GROQ_ROUTER_MODEL"
GROQ_MANIM_MODEL_ENV = "GROQ_MANIM_MODEL"
GROQ_REPAIR_MODEL_ENV = "GROQ_REPAIR_MODEL"

for d in [OUTPUT_DIR, MEDIA_DIR]:
    d.mkdir(exist_ok=True)
