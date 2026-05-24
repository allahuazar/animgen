# Known Good Manim Patterns

## Viewport-safe rules
- Safe x range: -6 to 6
- Safe y range: -3.2 to 3.2
- Use one title at the top with `.to_edge(UP, buff=0.5)`
- Use one main VGroup centered with `.move_to(ORIGIN)`
- Prefer `VGroup(...).arrange(...)` over manual coordinates
- After arranging, use `.move_to(ORIGIN)`
- Keep title font size between 36 and 44
- Keep equation font size between 32 and 40
- Keep explanation font size between 22 and 30
- Break long text into multiple Text objects
- Use `scale_to_fit_width(11)` for wide groups
- Use `scale_to_fit_height(5.8)` for tall groups
- NumberLine length should usually be 8-10, never above 12
- Axes should use reasonable x_length/y_length

## fit_to_screen helper
Always include this helper inside `construct()`:
```python
def fit_to_screen(mobject):
    if mobject.width > 11:
        mobject.scale_to_fit_width(11)
    if mobject.height > 5.8:
        mobject.scale_to_fit_height(5.8)
    return mobject
```
Call `fit_to_screen()` on large VGroups before animating them.

## Basic GeneratedScene
```python
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        def fit_to_screen(mobject):
            if mobject.width > 11:
                mobject.scale_to_fit_width(11)
            if mobject.height > 5.8:
                mobject.scale_to_fit_height(5.8)
            return mobject

        title = Text("Hello", font_size=40).to_edge(UP, buff=0.5)
        body = Text("Welcome", font_size=32)
        body.move_to(ORIGIN)
        fit_to_screen(body)

        self.play(Write(title))
        self.play(Write(body))
        self.wait(2)
```

## Viewport-safe title + centered content
```python
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        def fit_to_screen(mobject):
            if mobject.width > 11:
                mobject.scale_to_fit_width(11)
            if mobject.height > 5.8:
                mobject.scale_to_fit_height(5.8)
            return mobject

        title = Text("Solving x + 5 = 12", font_size=40).to_edge(UP, buff=0.5)

        step1 = Text("x + 5 = 12", font_size=36)
        step2 = Text("x = 12 - 5", font_size=36)
        step3 = Text("x = 7", font_size=40)

        steps = VGroup(step1, step2, step3).arrange(DOWN, buff=0.45)
        steps.move_to(ORIGIN)
        fit_to_screen(steps)

        self.play(Write(title))
        self.play(Write(step1))
        self.play(ReplacementTransform(step1, step2))
        self.play(ReplacementTransform(step2, step3))
        self.wait(1)
```

## Equation step transformations
```python
step1 = Text("x + 5 = 12", font_size=36)
step2 = Text("x = 7", font_size=40, color=GREEN)
self.play(ReplacementTransform(step1, step2))
```
Use `ReplacementTransform(old, new)` not `Transform(old.copy(), new)`.
The `.copy()` leaves the old object on screen.

## NumberLine and Dot
```python
nl = NumberLine(x_range=[-5, 5], length=10, include_numbers=True)
dot = Dot(nl.n2p(2), color=RED)
label = Text("x = 2", font_size=24).next_to(dot, UP)
self.play(Create(nl), Create(dot), Write(label))
```

## Arrow between two labels
```python
a = Text("2x + 3", font_size=36)
b = Text("= 7", font_size=36).next_to(a, RIGHT)
arrow = Arrow(a.get_right(), b.get_left(), color=YELLOW)
self.play(Write(a), Write(b))
self.play(Create(arrow))
```

## VGroup arranged vertically
```python
t1 = Text("Step 1", font_size=32)
t2 = Text("Step 2", font_size=32)
t3 = Text("Step 3", font_size=32)
group = VGroup(t1, t2, t3).arrange(DOWN, buff=0.4)
group.move_to(ORIGIN)
fit_to_screen(group)
self.play(Write(group))
```

## Text title and subtitle
```python
title = Text("Linear Equations", font_size=40, color=BLUE)
title.to_edge(UP, buff=0.5)
self.play(Write(title))
```

## FadeIn / FadeOut
```python
obj = Text("Hello", font_size=36)
self.play(FadeIn(obj, shift=UP))
self.wait(1)
self.play(FadeOut(obj))
```

## Write animation
```python
text = Text("Write this text", font_size=36)
self.play(Write(text))
```

## ReplacementTransform
```python
start = Text("2x + 3 = 7", font_size=36)
result = Text("x = 2", font_size=36, color=GREEN)
self.play(ReplacementTransform(start, result))
```
Do NOT use `Transform(start.copy(), result)` — this leaves `start` visible.

## Create (shapes)
```python
circle = Circle(color=BLUE, fill_opacity=0.3)
self.play(Create(circle))
rect = Rectangle(width=4, height=3, color=GREEN)
self.play(Create(rect))
```

## Simple shapes
```python
square = Square(side_length=2, color=YELLOW)
dot = Dot(color=RED)
arrow = Arrow(LEFT, RIGHT, color=WHITE)
```

## Positioning helpers
```python
obj.to_edge(UP, buff=0.5)
obj.next_to(other, DOWN, buff=0.5)
obj.shift(LEFT * 2)
VGroup(a, b).arrange(DOWN, buff=0.4)
group.move_to(ORIGIN)
```

## Complete viewport-safe equation example
```python
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        def fit_to_screen(mobject):
            if mobject.width > 11:
                mobject.scale_to_fit_width(11)
            if mobject.height > 5.8:
                mobject.scale_to_fit_height(5.8)
            return mobject

        title = Text("Solve x + 5 = 12", font_size=40, color=BLUE)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title))

        eq = Text("x + 5 = 12", font_size=36)
        eq.move_to(ORIGIN)
        self.play(FadeIn(eq))
        self.wait(1)

        step1 = Text("Subtract 5 from both sides", font_size=28, color=YELLOW)
        step1.next_to(eq, DOWN, buff=0.6)
        self.play(Write(step1))

        result = Text("x = 7", font_size=40, color=GREEN)
        result.next_to(step1, DOWN, buff=0.6)
        self.play(ReplacementTransform(eq, result))
        self.wait(1)

        nl = NumberLine(x_range=[0, 10], length=8, include_numbers=True)
        nl.next_to(result, DOWN, buff=0.6)
        dot = Dot(nl.n2p(7), color=RED)
        label = Text("x = 7", font_size=24).next_to(dot, UP)
        self.play(Create(nl), Create(dot), Write(label))
        self.wait(2)
```
