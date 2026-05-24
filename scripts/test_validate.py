import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from animgen.validator import validate_code

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/generated_scene.py")
code = path.read_text(encoding="utf-8")
validation = validate_code(code)
print(f"OK: {validation['ok']}")
if validation["errors"]:
    print(f"Errors ({len(validation['errors'])}):")
    for e in validation["errors"]:
        print(f"  - {e}")
if validation["warnings"]:
    print(f"Warnings ({len(validation['warnings'])}):")
    for w in validation["warnings"]:
        print(f"  - {w}")
