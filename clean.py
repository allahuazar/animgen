"""
clean.py — Remove generated/cache files safely.

Usage:
    uv run python clean.py          # dry-run + ask confirmation
    uv run python clean.py --yes    # skip confirmation
    uv run python clean.py --dry-run  # list only, no delete
"""

import argparse
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent

SAFETY_MARKERS = [
    HERE / "pyproject.toml",
    HERE / "src" / "animgen",
]


def _in_project_root() -> bool:
    return all(p.exists() for p in SAFETY_MARKERS)


PATTERNS: list[tuple[str, bool]] = [
    # (path/glob, is_dir)
    ("media", True),
    ("output/generated_scene.py", False),
    ("output/*.mp4", False),
    ("output/*.png", False),
    ("output/*.svg", False),
    ("output/*.pdf", False),
    ("output/*.typ", False),
    ("output/*.log", False),
    ("output/*.json", False),
    ("frontend/dist", True),
    ("frontend/node_modules/.vite", True),
    ("frontend/.vite", True),
]

RECURSIVE_DIRS = [
    "__pycache__",
    ".pytest_cache",
]

RECURSIVE_FILES = [
    "*.pyc",
]

KEEP_DIRS = [
    HERE / "output",
    HERE / "media",
]


def _collect_dry_run() -> list[Path]:
    found: list[Path] = []

    for path_str, is_dir in PATTERNS:
        p = HERE / path_str
        if is_dir:
            if p.exists():
                found.append(p)
        else:
            if "*" in path_str or "?" in path_str:
                for match in HERE.glob(path_str):
                    if match.exists():
                        found.append(match)
            elif p.exists():
                found.append(p)

    for dir_name in RECURSIVE_DIRS:
        for p in HERE.rglob(dir_name):
            if p.is_dir():
                found.append(p)

    for pat in RECURSIVE_FILES:
        for p in HERE.rglob(pat):
            if p.is_file():
                found.append(p)

    return sorted(set(found))


def _delete(paths: list[Path]) -> None:
    for p in paths:
        if p.is_dir() and not p.is_symlink():
            shutil.rmtree(p)
        else:
            p.unlink()

    for d in KEEP_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        gitkeep = d / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("")


def main() -> None:
    if not _in_project_root():
        print("ERROR: Must run from project root (pyproject.toml + src/animgen not found).")
        raise SystemExit(1)

    parser = argparse.ArgumentParser(description="Clean generated/cache files from the project.")
    parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    parser.add_argument("--dry-run", action="store_true", help="Only list files, do not delete")
    args = parser.parse_args()

    paths = _collect_dry_run()

    if not paths:
        print("Nothing to clean.")
        return

    print(f"Found {len(paths)} item(s) to clean:")
    for p in paths:
        rel = p.relative_to(HERE)
        print(f"  {rel}{'/' if p.is_dir() else ''}")

    if args.dry_run:
        print("\nDry-run complete. No files deleted.")
        return

    if not args.yes:
        answer = input("\nDelete these files? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Aborted.")
            return

    _delete(paths)
    print("Done. Recreated output/ and media/ with .gitkeep.")


if __name__ == "__main__":
    main()
