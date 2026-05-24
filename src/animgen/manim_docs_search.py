import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DOCS_DIR = ROOT / "docs_rag" / "manim"

_FILE_PRIORITY = {
    "known_good_patterns.md": 0,
    "common_errors.md": 1,
}


def _find_files() -> list[Path]:
    if not DOCS_DIR.exists():
        return []
    return sorted(
        p for p in DOCS_DIR.rglob("*") if p.is_file() and p.suffix in (".md", ".txt", ".py")
    )


def _priority(path: Path) -> tuple:
    name = path.name
    order = _FILE_PRIORITY.get(name, 99)
    return (order, str(path))


def _get_snippet_lines(text: str, query_words: set[str], context: int = 3) -> list[str]:
    lines = text.split("\n")
    matched_indices = set()
    query_lower = {q.lower() for q in query_words}
    for i, line in enumerate(lines):
        words = set(re.findall(r"[a-zA-Z_]\w*", line.lower()))
        if words & query_lower:
            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            matched_indices.update(range(start, end))
    if not matched_indices:
        return []
    result = []
    for i in sorted(matched_indices):
        result.append(lines[i])
    return result


def search_manim_docs(queries: list[str], limit_chars: int = 10000) -> list[dict]:
    files = _find_files()
    files.sort(key=_priority)
    query_set = set(queries)
    query_words = set()
    for q in queries:
        query_words.update(re.findall(r"[a-zA-Z_]\w*", q))
    if not query_words:
        query_words = query_set

    results = []
    seen_snippets = set()
    total = 0

    for path in files:
        if total >= limit_chars:
            break
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        snippet_lines = _get_snippet_lines(text, query_words)
        if not snippet_lines:
            continue
        snippet = "\n".join(snippet_lines)
        key = snippet[:200]
        if key in seen_snippets:
            continue
        seen_snippets.add(key)
        rel = str(path.relative_to(ROOT))
        results.append({"source": rel, "query": queries[0], "snippet": snippet})
        total += len(snippet)

    if not results:
        for path in files[:2]:
            try:
                text = path.read_text(encoding="utf-8")
                results.append({"source": str(path.relative_to(ROOT)), "query": queries[0], "snippet": text[:1000]})
            except Exception:
                pass

    return results


def format_docs_snippets(snippets: list[dict]) -> str:
    parts = []
    for s in snippets:
        parts.append(f"--- {s['source']} ---\n{s['snippet']}")
    return "\n\n".join(parts)
