import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from animgen.pipeline import generate_and_render

prompt = " ".join(sys.argv[1:]) or "Animate solving x + 5 = 12"
print(f"Prompt: {prompt}\n")

result = generate_and_render(prompt)
print(f"OK: {result['ok']}")
print(f"Repaired: {result.get('repaired', False)}")

if result.get("router"):
    print(f"\nRouter:")
    print(json.dumps(result["router"], indent=2))

if result.get("code"):
    print(f"\nCode ({len(result['code'])} chars):")
    print(result['code'])

if result.get("validation"):
    v = result["validation"]
    print(f"\nValidation OK: {v['ok']}")
    if v.get("errors"):
        print(f"Errors: {v['errors']}")
    if v.get("warnings"):
        print(f"Warnings: {v['warnings']}")

if result.get("video_url"):
    print(f"\nVideo: {result['video_url']}")

if result.get("error"):
    print(f"\nError: {result['error']}")
