
#import "@preview/cetz:0.5.2"

#set page(
  paper: "a4",
  margin: 1.5cm,
)

#set text(
  size: 11pt,
)

#set heading(numbering: "1.")

#show heading: it => [
  #v(0.8em)
  #text(size: 15pt, weight: "bold")[#it.body]
  #v(0.4em)
]

#align(center)[
  #text(size: 24pt, weight: "bold")[Photosynthesis]
  #linebreak()
  #text(size: 11pt, fill: gray)[Class 8 • Biology]
]

#v(1em)

#block(
  fill: rgb("#f6f8fa"),
  inset: 12pt,
  radius: 8pt,
)[
  *Summary:* Photosynthesis is the process by which green plants make their own food using sunlight, carbon dioxide, and water.
]

= Key Points

- Plants use chlorophyll to absorb sunlight.
- Carbon dioxide enters the leaf through stomata.
- Water is absorbed by the roots and transported to the leaves.
- The plant produces glucose as food.
- Oxygen is released as a by-product.

= Main Formula

#block(
  fill: rgb("#fff7d6"),
  inset: 12pt,
  radius: 8pt,
)[
  #text(size: 14pt, weight: "bold")[6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂]
]

= Simple Diagram

#cetz.canvas(length: 1cm, {
  import cetz.draw: *

  rect(
    (0, 0),
    (12, 5),
    radius: 0.25,
    fill: rgb("#f4fff2"),
    stroke: rgb("#74a46f"),
  )

  circle(
    (2, 3.5),
    radius: 0.65,
    fill: rgb("#ffd166"),
    stroke: none,
  )
  content((2, 3.5), [Sun])

  line(
    (2.8, 3.4),
    (5, 2.8),
    mark: (end: ">"),
  )
  content((4, 3.35), [light])

  rect(
    (5.2, 1.5),
    (7.2, 3.4),
    radius: 0.25,
    fill: rgb("#95d5b2"),
    stroke: rgb("#40916c"),
  )
  content((6.2, 2.45), [Leaf])

  line(
    (4, 1),
    (5.1, 1.9),
    mark: (end: ">"),
  )
  content((3.6, 0.65), [CO₂])

  line(
    (6.2, 0.4),
    (6.2, 1.45),
    mark: (end: ">"),
  )
  content((6.2, 0.15), [Water])

  line(
    (7.3, 2.8),
    (9.3, 3.6),
    mark: (end: ">"),
  )
  content((9.9, 3.7), [O₂])

  line(
    (7.3, 1.9),
    (9.3, 1.2),
    mark: (end: ">"),
  )
  content((10, 1.1), [Glucose])
})

= Quiz


== Question 1

What is the green pigment in leaves called?

#block(
  fill: rgb("#f3f4f6"),
  inset: 10pt,
  radius: 6pt,
)[
  *Answer:* Chlorophyll
]


== Question 2

Which gas is released during photosynthesis?

#block(
  fill: rgb("#f3f4f6"),
  inset: 10pt,
  radius: 6pt,
)[
  *Answer:* Oxygen
]


== Question 3

What food does the plant produce?

#block(
  fill: rgb("#f3f4f6"),
  inset: 10pt,
  radius: 6pt,
)[
  *Answer:* Glucose
]

