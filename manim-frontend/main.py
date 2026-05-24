from manim import *


class PhotosynthesisDemo(Scene):
    def construct(self):
        title = Text("Photosynthesis", font_size=48)
        subtitle = Text("How plants make food", font_size=28).next_to(title, DOWN)

        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(1)

        self.play(
            title.animate.to_edge(UP),
            FadeOut(subtitle),
        )

        sun = Circle(radius=0.6, color=YELLOW, fill_opacity=1)
        sun_label = Text("Sun", font_size=24).move_to(sun.get_center())
        sun_group = VGroup(sun, sun_label).to_edge(LEFT).shift(UP)

        leaf = RoundedRectangle(
            width=2.5,
            height=1.4,
            corner_radius=0.3,
            color=GREEN,
            fill_opacity=0.7,
        )
        leaf_label = Text("Leaf", font_size=28).move_to(leaf.get_center())
        leaf_group = VGroup(leaf, leaf_label).move_to(ORIGIN)

        light_arrow = Arrow(
            sun_group.get_right(),
            leaf_group.get_left(),
            buff=0.2,
            color=YELLOW,
        )
        light_text = Text("light", font_size=22).next_to(light_arrow, UP)

        self.play(FadeIn(sun_group), FadeIn(leaf_group))
        self.play(GrowArrow(light_arrow), FadeIn(light_text))
        self.wait(1)

        co2 = Text("CO₂", font_size=32).to_edge(LEFT).shift(DOWN * 1.5)
        water = Text("H₂O", font_size=32).to_edge(DOWN)

        co2_arrow = Arrow(co2.get_right(), leaf_group.get_left(), buff=0.2)
        water_arrow = Arrow(water.get_top(), leaf_group.get_bottom(), buff=0.2)

        self.play(FadeIn(co2), GrowArrow(co2_arrow))
        self.play(FadeIn(water), GrowArrow(water_arrow))
        self.wait(1)

        oxygen = Text("O₂", font_size=32).to_edge(RIGHT).shift(UP)
        glucose = Text("Glucose", font_size=32).to_edge(RIGHT).shift(DOWN)

        oxygen_arrow = Arrow(leaf_group.get_right(), oxygen.get_left(), buff=0.2)
        glucose_arrow = Arrow(leaf_group.get_right(), glucose.get_left(), buff=0.2)

        self.play(GrowArrow(oxygen_arrow), FadeIn(oxygen))
        self.play(GrowArrow(glucose_arrow), FadeIn(glucose))
        self.wait(1)

        formula = MathTex(
            "6CO_2 + 6H_2O",
            "\\rightarrow",
            "C_6H_{12}O_6 + 6O_2",
            font_size=42,
        ).to_edge(DOWN)

        self.play(
            FadeOut(water),
            FadeOut(water_arrow),
            FadeIn(formula),
        )
        self.wait(2)
