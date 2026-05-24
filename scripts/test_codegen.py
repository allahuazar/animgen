import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from animgen.router import route_prompt
from animgen.docs_search import search_docs
from animgen.codegen import generate_code
from animgen.validator import validate_code
from animgen import config

prompt = " ".join(sys.argv[1:]) or "Animate solving x + 5 = 12"
print(f"Prompt: {prompt}\n")

print("--- Router ---")
router_result = route_prompt(prompt)
print(json.dumps(router_result, indent=2))

print("\n--- Search docs ---")
snippets = search_docs(router_result.get("search_queries", [prompt]))
print(f"Found {len(snippets)} snippet(s)")

print("\n--- Generate code ---")
code = generate_code(prompt, router_result, snippets)
print(code)

config.OUTPUT_DIR.mkdir(exist_ok=True)
config.GENERATED_SCENE_PATH.write_text(code, encoding="utf-8")
print(f"\nSaved to {config.GENERATED_SCENE_PATH}")

print("\n--- Validate ---")
validation = validate_code(code)
print(f"OK: {validation['ok']}")
if validation["errors"]:
    print(f"Errors: {validation['errors']}")
if validation["warnings"]:
    print(f"Warnings: {validation['warnings']}")
