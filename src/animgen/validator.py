import re

REQUIRED_PATTERNS = [
    (r"from\s+manim\s+import\s+\*", "missing 'from manim import *'"),
    (r"class\s+GeneratedScene\s*\(\s*Scene\s*\)\s*:", "missing 'class GeneratedScene(Scene):'"),
]

BLOCKING_PATTERNS = [
    (r"\bimport\s+os\b", "import os"),
    (r"\bimport\s+sys\b", "import sys"),
    (r"\bimport\s+subprocess\b", "import subprocess"),
    (r"from\s+pathlib\b", "from pathlib"),
    (r"\bimport\s+pathlib\b", "import pathlib"),
    (r"\bopen\s*\(", "open("),
    (r"\bexec\s*\(", "exec("),
    (r"\beval\s*\(", "eval("),
    (r"\bimport\s+requests\b", "import requests"),
    (r"\bimport\s+socket\b", "import socket"),
    (r"\bimport\s+shutil\b", "import shutil"),
    (r"\b__import__\b", "__import__"),
    (r"\binput\s*\(", "input("),
]


def _check_blocking_errors(code: str) -> list[str]:
    errors = []
    for pattern, label in REQUIRED_PATTERNS:
        if not re.search(pattern, code):
            errors.append(label)
    for pattern, label in BLOCKING_PATTERNS:
        if re.search(pattern, code):
            errors.append(f"unsafe code: {label}")
    return errors


def _check_warnings(code: str) -> list[str]:
    warnings = []
    if not re.search(r"def\s+fit_to_screen\s*\(", code):
        warnings.append("missing fit_to_screen helper")
    for m in re.finditer(r'font_size\s*=\s*(\d+)', code):
        val = int(m.group(1))
        if val > 56:
            warnings.append(f"font_size {val} > 56 may go out of viewport")
    for m in re.finditer(r'NumberLine\([^)]*?length\s*=\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(1))
        if val > 12:
            warnings.append(f"NumberLine length {val} > 12 may go out of viewport")
    for m in re.finditer(r'shift\(\s*(RIGHT|LEFT)\s*\*\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(2))
        if val >= 7:
            warnings.append(f"shift({m.group(1)} * {val}) >= 7 may go out of viewport")
    for m in re.finditer(r'shift\(\s*(UP|DOWN)\s*\*\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(2))
        if val >= 4:
            warnings.append(f"shift({m.group(1)} * {val}) >= 4 may go out of viewport")
    for m in re.finditer(r'x_length\s*=\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(1))
        if val > 12:
            warnings.append(f"x_length {val} > 12 may go out of viewport")
    for m in re.finditer(r'y_length\s*=\s*(\d+(?:\.\d+)?)', code):
        val = float(m.group(1))
        if val > 8:
            warnings.append(f"y_length {val} > 8 may go out of viewport")
    return warnings


def validate_code(code: str) -> dict:
    errors = _check_blocking_errors(code)
    warnings = _check_warnings(code)
    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
