import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from animgen.runner import render_scene

result = render_scene()
print(f"OK: {result['ok']}")
if result.get("video_url"):
    print(f"Video: {result['video_url']}")
if result.get("error"):
    print(f"Error: {result['error']}")
if result.get("stdout"):
    print(f"stdout:\n{result['stdout']}")
if result.get("stderr"):
    print(f"stderr:\n{result['stderr']}")
