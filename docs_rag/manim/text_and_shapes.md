# Manim Text and Shapes

## Text
```python
Text("Hello", font_size=36, color=WHITE)
```

## VGroup
```python
t1 = Text("First")
t2 = Text("Second")
group = VGroup(t1, t2).arrange(DOWN)
```

## Circle and Rectangle
```python
circle = Circle(color=BLUE, fill_opacity=0.5)
rect = Rectangle(width=4, height=3, color=GREEN)
```

## Transform
```python
self.play(Transform(circle, rect))
```

## Fade in/out
```python
self.play(FadeIn(obj))
self.play(FadeOut(obj))
```

## Positioning
```python
obj.to_edge(UP)
obj.next_to(other, DOWN, buff=0.5)
obj.shift(LEFT * 2)
```
