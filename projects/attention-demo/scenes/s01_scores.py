"""s01_scores — Scores: how well does each key match the query?  (storyboard.md, source §1)"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    UP,
    Arrow,
    Create,
    DashedLine,
    FadeIn,
    FadeOut,
    GrowArrow,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    NumberPlane,
    Text,
    Transform,
    VGroup,
    Write,
)

from components import EduScene, math_label, place_caption, scene_title, source_tag, style

import data
from shared import KEY, QUERY, final_score_column, scaled_header, score_column


class S01Scores(EduScene):
    SCENE_ID = "s01_scores"

    def construct(self):
        title = scene_title("1 · Scores", "How well does each key match the query?")
        ref = source_tag("source §1 · worked example")
        self.beat("title", FadeIn(title, shift=0.2 * DOWN), FadeIn(ref), run=0.8, wait=1.0)

        # --- 2-D picture: query and keys ------------------------------------------
        plane = NumberPlane(
            x_range=[-1, 2, 1],
            y_range=[-1.25, 1.5, 1],
            x_length=5.1,
            y_length=4.675,
            background_line_style={"stroke_color": style.GRID, "stroke_width": 1},
            axis_config={"stroke_color": style.MUTED, "stroke_width": 2},
        ).move_to([-3.1, -0.45, 0])
        origin = plane.c2p(0, 0)

        def vec(xy, color):
            return Arrow(
                origin,
                plane.c2p(*xy),
                buff=0,
                color=color,
                stroke_width=5,
                max_tip_length_to_length_ratio=0.12,
            )

        def tip_label(text, xy, color, direction=None, lab=None):
            if direction is None:
                direction = np.array([*xy, 0.0]) / np.linalg.norm(xy)
            lab = lab or Text(text, font=style.FONT, font_size=style.LABEL_SIZE, color=color)
            return lab.next_to(plane.c2p(*xy), direction, buff=0.12)

        q = vec(data.Q, QUERY).set_z_index(2)  # stays visible over the projection
        # label up-left of the tip: the cat projection (next beats) extends past the tip
        q_lab = tip_label(
            None,
            data.Q,
            QUERY,
            direction=UP + LEFT * 0.6,
            lab=math_label(rf"q\ \text{{({data.QUERY_TOKEN})}}", color=QUERY),
        )
        self.beat("show_query", FadeIn(plane), GrowArrow(q), FadeIn(q_lab), run=1.2, wait=0.8)

        keys = VGroup(*(vec(k, KEY) for k in data.KEYS))
        key_labs = VGroup(*(tip_label(t, k, KEY) for t, k in zip(data.TOKENS, data.KEYS, strict=True)))
        self.beat(
            "show_keys",
            LaggedStart(*(GrowArrow(k) for k in keys), lag_ratio=0.25),
            LaggedStart(*(FadeIn(l) for l in key_labs), lag_ratio=0.25),
            run=1.6,
            wait=0.8,
        )

        # --- projection of the "cat" key onto the query direction ---------------------
        u = np.array(data.Q) / np.linalg.norm(data.Q)
        k0 = np.array(data.KEYS[0])
        foot = (k0 @ u) * u
        drop = DashedLine(plane.c2p(*k0), plane.c2p(*foot), color=style.MUTED, stroke_width=3)
        reach = Line(origin, plane.c2p(*foot), color=style.YELLOW, stroke_width=9)
        reach.set_opacity(0.8)
        self.beat("project_cat", Create(drop), Create(reach), run=1.4, wait=1.4)

        # --- score column -------------------------------------------------------------
        col = score_column()
        numbers = [col.cell(i, 0)[1] for i in range(len(data.TOKENS))]
        frame = VGroup(*(col.cell(i, 0)[0] for i in range(len(data.TOKENS))), col.row_labels, col.col_labels)
        self.beat(
            "score_cat",
            FadeIn(frame),
            FadeIn(numbers[0], scale=1.3),
            Indicate(key_labs[0], color=style.YELLOW),
            run=1.0,
            wait=1.0,
        )
        self.beat(
            "score_rest",
            LaggedStart(*(FadeIn(n, scale=1.3) for n in numbers[1:]), lag_ratio=0.35),
            FadeOut(drop),
            FadeOut(reach),
            run=1.5,
            wait=0.8,
        )

        cap = place_caption(
            Text(
                "aligned → large     perpendicular → ≈ 0     opposed → negative",
                font=style.FONT,
                font_size=style.CAPTION_SIZE,
                color=style.TEXT,
                t2c={"large": KEY, "≈ 0": KEY, "negative": KEY},
            )
        )
        self.beat(
            "alignment",
            FadeIn(cap),
            *(Indicate(m, color=style.YELLOW) for m in (keys[1], key_labs[1], keys[2], key_labs[2])),
            run=1.5,
            wait=1.8,
        )

        # --- scaling by sqrt(d_k) ----------------------------------------------------------
        formula = MathTex(
            r"s_i",
            "=",
            r"{q \cdot k_i",
            r"\over",
            r"\sqrt{d_k}}",
            r"\quad (d_k = 2)",
            font_size=style.MATH_SIZE,
            color=style.TEXT,
        )
        formula[0].set_color(KEY)
        formula[5].set_color(style.MUTED).scale(0.75, about_edge=LEFT)
        formula.next_to(col, UP, buff=0.45)
        target = final_score_column()
        self.beat(
            "scale",
            FadeOut(cap),
            Write(formula),
            *(
                Transform(n, t)
                for n, t in zip(numbers, [target.cell(i, 0)[1] for i in range(len(data.TOKENS))], strict=True)
            ),
            Transform(col.col_labels[0], scaled_header().move_to(col.col_labels[0])),
            run=1.8,
            wait=2.0,
        )

        # --- hand-off: keep only the score column for s02 --------------------------------
        self.beat(
            "handoff",
            *(FadeOut(m) for m in (plane, q, q_lab, *keys, *key_labs, formula, title, ref)),
            run=0.8,
            wait=0.2,
        )
