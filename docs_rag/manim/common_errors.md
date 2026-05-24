# Common Manim Errors

## MathTex requires LaTeX
MathTex uses LaTeX internally. If TeX packages are missing, it will fail silently or with cryptic errors.
- Prefer Text for MVP formulas: `Text("x + 5 = 12", font_size=40)`
- Only use MathTex when you absolutely need proper math rendering

## MathTex may fail with missing packages
If LaTeX packages (texlive) are not installed, MathTex will raise cryptic errors. Prefer Text for MVP.

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

## Animations going out of viewport
Generated animations may go outside the visible frame if:
- Using large manual shifts (>4 units)
- Using large font sizes (>56)
- Using NumberLine length > 12
- Placing objects with manual coordinates outside safe range

Safe frame: x: -6 to 6, y: -3.2 to 3.2

Solutions:
- Use VGroup arrange + move_to(ORIGIN)
- Always include and call fit_to_screen()
- Keep title at top with .to_edge(UP, buff=0.5)
- Keep content centered

## ReplacementTransform vs Transform with copy
- `ReplacementTransform(old, new)` — properly replaces old with new
- `Transform(old.copy(), new)` — leaves old object visible on screen (old is still there)
- Prefer `ReplacementTransform(old, new)` when replacing

## Common rendering issues
- Missing manim import: add `from manim import *`
- Forgetting `self.play()`: animations must be wrapped in play calls
- Using undefined colors: use Manim built-in colors (RED, BLUE, GREEN, YELLOW, WHITE, BLACK, GRAY, ORANGE, PURPLE)
- Positioning off-screen: use `to_edge()`, `next_to()`, `shift()` helpers
- Not calling `self.wait()`: scene will end immediately

## Generated scene class requirement
The generated scene class must be named `GeneratedScene` extending `Scene`:
```python
class GeneratedScene(Scene):
```
