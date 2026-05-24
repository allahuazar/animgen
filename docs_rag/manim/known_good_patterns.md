# Known Good Manim Patterns

## Basic GeneratedScene
```python
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        t = Text("Hello", font_size=48)
        self.play(Write(t))
        self.wait(2)
```

## Text title and subtitle
```python
title = Text("Linear Equations", font_size=44, color=BLUE)
title.to_edge(UP)
self.play(Write(title))
```

## Text equation steps
```python
eq = Text("x + 5 = 12", font_size=40)
self.play(Write(eq))
self.wait(1)
step2 = Text("x = 7", font_size=40, color=GREEN)
self.play(Transform(eq, step2))
```

## VGroup
```python
t1 = Text("Step 1", font_size=32)
t2 = Text("Step 2", font_size=32)
group = VGroup(t1, t2).arrange(DOWN, buff=0.5)
self.play(Write(group))
```

## Arrow between objects
```python
a = Text("2x + 3", font_size=36)
b = Text("= 7", font_size=36).next_to(a, RIGHT)
arrow = Arrow(a.get_right(), b.get_left(), color=YELLOW)
self.play(Write(a), Write(b))
self.play(Create(arrow))
```

## NumberLine and Dot
```python
nl = NumberLine(x_range=[-5, 5], length=8, include_numbers=True)
dot = Dot(nl.n2p(2), color=RED)
label = Text("x = 2", font_size=24).next_to(dot, UP)
self.play(Create(nl), Create(dot), Write(label))
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

## Transform
```python
start = Text("2x + 3 = 7", font_size=36)
result = Text("x = 2", font_size=36, color=GREEN)
self.play(Transform(start, result))
```

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
obj.to_edge(UP)
obj.next_to(other, DOWN, buff=0.5)
obj.shift(LEFT * 2)
VGroup(a, b).arrange(DOWN)
```

## Complete equation solving example
```python
from manim import *

class GeneratedScene(Scene):
    def construct(self):
        title = Text("Solve x + 5 = 12", font_size=40, color=BLUE)
        title.to_edge(UP)
        self.play(Write(title))

        eq = Text("x + 5 = 12", font_size=44)
        self.play(FadeIn(eq))
        self.wait(1)

        step1 = Text("Subtract 5 from both sides", font_size=28, color=YELLOW)
        step1.next_to(eq, DOWN, buff=0.8)
        self.play(Write(step1))

        eq2 = Text("x = 7", font_size=44, color=GREEN)
        eq2.next_to(step1, DOWN, buff=0.8)
        self.play(Transform(eq.copy(), eq2))
        self.wait(1)

        nl = NumberLine(x_range=[0, 10], length=8, include_numbers=True)
        nl.next_to(eq2, DOWN, buff=0.8)
        dot = Dot(nl.n2p(7), color=RED)
        label = Text("x = 7", font_size=24).next_to(dot, UP)
        self.play(Create(nl), Create(dot), Write(label))
        self.wait(2)
```
