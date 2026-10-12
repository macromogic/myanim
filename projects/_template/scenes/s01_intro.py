"""s01_intro — replace with the first storyboard scene."""

from manim import DOWN, FadeIn

from components import EduScene, WeightBars, caption, scene_title

import data
from shared import CONCEPT_A


class S01Intro(EduScene):
    SCENE_ID = "s01_intro"

    def construct(self):
        title = scene_title("1 · Title", "Subtitle")
        self.beat("title", FadeIn(title, shift=0.2 * DOWN), run=0.8, wait=0.5)
        bars = WeightBars(data.EXAMPLE, labels=["apple", "pear", "plum"], value_range=(0, 3), color=CONCEPT_A)
        self.beat("main_idea", FadeIn(bars), FadeIn(caption(f"total = {data.TOTAL:.2f}")), run=1.0, wait=1.5)
