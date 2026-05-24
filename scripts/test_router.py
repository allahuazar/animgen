import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from animgen.router import route_prompt

prompt = " ".join(sys.argv[1:]) or "Animate solving x + 5 = 12"
result = route_prompt(prompt)
print(f"Intent: {result['intent']}")
print(f"Topic: {result['topic']}")
print(f"Search queries: {result['search_queries']}")
print(f"Scene plan: {result['scene_plan']}")
print(f"Reason: {result['reason']}")
