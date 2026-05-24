import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from animgen.docs_search import search_docs, format_snippets

queries = sys.argv[1:] or ["Text", "Transform", "NumberLine"]
snippets = search_docs(queries)
print(f"Found {len(snippets)} snippet(s)")
for s in snippets:
    print(f"\n--- {s['source']} ---")
    print(s['snippet'][:500])
