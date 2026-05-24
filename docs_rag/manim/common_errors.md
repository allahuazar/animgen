# Common Manim Errors

## MathTex requires LaTeX
MathTex uses LaTeX internally. If TeX packages are missing, it will fail silently or with cryptic errors.
- Prefer Text for MVP formulas: `Text("x + 5 = 12", font_size=40)`
- Only use MathTex when you absolutely need proper math rendering

## Scene class must be GeneratedScene
The render command expects exactly this class name:
```python
class GeneratedScene(Scene):
```

## Render command
Always use:
```
uv run python -m manim -ql output/generated_scene.py GeneratedScene
```

## Avoid external dependencies
Do not import or use:
- `import os`
- `import sys`
- `import subprocess`
- `from pathlib import Path`
- `import requests`
- `import socket`
- `import shutil`
- `open(`, `exec(`, `eval(`, `input(`, `__import__(`

## Animation length
Keep total animation under 60 seconds. Manim at -ql (480p15) renders ~1.5x real-time.

## Text vs MathTex
- Text renders reliably on any system
- MathTex requires `texlive` system packages
- For MVP, always use Text for formulas

## Common rendering issues
- Missing manim import: add `from manim import *`
- Forgetting `self.play()`: animations must be wrapped in play calls
- Using undefined colors: use Manim built-in colors (RED, BLUE, GREEN, YELLOW, WHITE, BLACK, GRAY, ORANGE, PURPLE)
- Positioning off-screen: use `to_edge()`, `next_to()`, `shift()` helpers
- Not calling `self.wait()`: scene will end immediately
