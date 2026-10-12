"""s02_softmax — Softmax turns scores into weights.  (storyboard.md, source §2)"""

import numpy as np
from manim import (
    DOWN,
    UP,
    Create,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    MathTex,
    ReplacementTransform,
    SurroundingRectangle,
    Text,
    Transform,
    Write,
)

from components import EduScene, Formula, WeightBars, place_caption, scene_title, source_tag, style

import data
from shared import KEY, WEIGHT, final_score_column

BASELINE = np.array([-2.6, -1.3, 0])
LABEL_DEPTH = 0.95
BAR_KW = dict(
    labels=data.TOKENS,
    max_height=3.0,
    bar_width=0.7,
    spacing=1.3,
    label_depth=LABEL_DEPTH,
    font_size=style.LABEL_SIZE + 2,
)


def caption_text(text, t2c=None):
    return place_caption(
        Text(text, font=style.FONT, font_size=style.CAPTION_SIZE, color=style.TEXT, t2c=t2c or {})
    )


class S02Softmax(EduScene):
    SCENE_ID = "s02_softmax"

    def construct(self):
        col = final_score_column()  # identical to the last frame of s01
        self.add(col)
        title = scene_title("2 · Softmax", "From scores to weights")
        ref = source_tag("source §2")
        self.beat("title", FadeIn(title, shift=0.2 * DOWN), FadeIn(ref), run=0.8, wait=0.5)

        # --- scores become bars ---------------------------------------------------------
        bars = WeightBars(data.SCORES, value_range=(-0.5, 3.5), color=KEY, **BAR_KW)
        bars.move_baseline_to(BASELINE)
        n = len(data.TOKENS)
        # Two calm steps instead of one busy one: (1) the column lays down into a row on
        # the baseline (numbers resting just above it), (2) bars grow and lift the numbers.
        resting = [
            bars.value_labels[i]
            .copy()
            .next_to(bars.baseline, UP if v >= 0 else DOWN, buff=style.BUFF_TIGHT)
            .set_x(bars.bars[i].get_x())
            for i, v in enumerate(data.SCORES)
        ]
        self.beat(
            "scores_to_row",
            *(Transform(col.cell(i, 0)[1], resting[i]) for i in range(n)),
            *(ReplacementTransform(col.row_labels[i], bars.labels[i]) for i in range(n)),
            *(FadeOut(col.cell(i, 0)[0]) for i in range(n)),
            FadeOut(col.col_labels),
            FadeIn(bars.baseline),
            run=1.2,
            wait=0.3,
        )
        self.beat(
            "grow_bars",
            *(ReplacementTransform(col.cell(i, 0)[1], bars.value_labels[i]) for i in range(n)),
            *(GrowFromEdge(b, DOWN if v >= 0 else UP) for b, v in zip(bars.bars, data.SCORES, strict=True)),
            run=1.0,
            wait=1.0,
        )
        self.consolidate(bars)

        formula = Formula(
            [
                ("w", "w_i"),
                ("eq", r"= \frac{"),
                ("num", r"e^{s_i}"),
                ("bar", "}{"),
                ("den", r"\sum_j e^{s_j}"),
                ("end", "}"),
            ],
            colors={"w": WEIGHT},
            font_size=style.MATH_SIZE + 4,
        ).move_to([3.6, 1.0, 0])
        self.beat("show_formula", Write(formula), run=1.2, wait=0.8)

        # --- step 1: exponentiate -------------------------------------------------------
        box = formula.box("num")
        cap = caption_text(
            "exp: every score becomes positive, and large scores pull ahead",
            t2c={"positive": KEY, "pull ahead": KEY},
        )
        self.beat("exponentiate", Create(box), FadeIn(cap), *bars.animate_to(data.EXPS), run=2.0, wait=1.8)

        # --- step 2: sum ---------------------------------------------------------------
        total = MathTex(
            r"\sum_j e^{s_j} = " + f"{data.EXP_SUM:.2f}", font_size=style.MATH_SMALL, color=style.TEXT
        )
        total.next_to(formula, DOWN, buff=0.6)
        self.beat(
            "sum",
            Transform(box, formula.box("den")),
            FadeOut(cap),
            FadeIn(total, shift=0.2 * UP),
            run=1.2,
            wait=1.0,
        )

        # --- step 3: normalize (new scale: probabilities) -------------------------------
        wbars = WeightBars(data.WEIGHTS, value_range=(0, 0.5), color=WEIGHT, **BAR_KW)
        wbars.move_baseline_to(BASELINE)
        check = MathTex(
            r"\sum_i w_i = " + f"{sum(data.WEIGHTS):.2f}", font_size=style.MATH_SMALL, color=WEIGHT
        )
        check.next_to(total, DOWN, buff=0.35)
        cap = caption_text(
            "divide by the sum: the weights add up to 1", t2c={"weights": WEIGHT, "add up to 1": WEIGHT}
        )
        self.beat(
            "normalize",
            ReplacementTransform(bars, wbars),
            FadeOut(box),
            FadeIn(check, shift=0.2 * UP),
            FadeIn(cap),
            run=2.0,
            wait=1.8,
        )

        # --- interpretation ---------------------------------------------------------------
        top = int(np.argmax(data.WEIGHTS))
        highlight = SurroundingRectangle(
            wbars.bar_group(top), color=style.YELLOW, buff=0.12, corner_radius=0.08
        )
        pct = round(100 * data.WEIGHTS[top])
        new_cap = caption_text(
            f"“{data.QUERY_TOKEN}” pays {pct}% of its attention to “{data.TOKENS[top]}”",
            t2c={f"{pct}%": WEIGHT},
        )
        self.beat("interpret", Create(highlight), Transform(cap, new_cap), run=1.2, wait=2.2)

        self.beat("handoff", *(FadeOut(m) for m in self.mobjects), run=0.8, wait=0.2)
