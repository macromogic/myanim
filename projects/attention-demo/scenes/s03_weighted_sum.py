"""s03_weighted_sum — The output is a weighted average of values.  (storyboard.md, source §3)"""

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MathTex,
    Succession,
    SurroundingRectangle,
    Text,
    Transform,
    VGroup,
    Write,
)

from components import EduScene, Formula, MatrixGrid, place_caption, scene_title, source_tag, style

import data
from shared import KEY, VALUE, WEIGHT

CELL = 0.75
ROW_Y = 0.55  # vertical center of the table row


def header(tex, color):
    return MathTex(tex, font_size=style.MATH_SMALL, color=color)


def caption_text(text, t2c=None):
    return place_caption(
        Text(text, font=style.FONT, font_size=style.CAPTION_SIZE, color=style.TEXT, t2c=t2c or {})
    )


class S03WeightedSum(EduScene):
    SCENE_ID = "s03_weighted_sum"

    def construct(self):
        title = scene_title("3 · Weighted sum of values", "What the query actually receives")
        ref = source_tag("source §3")
        self.beat("title", FadeIn(title, shift=0.2 * DOWN), FadeIn(ref), run=0.8, wait=0.5)

        # --- tables: weights · values = contributions ---------------------------------------
        n = len(data.TOKENS)
        weights = MatrixGrid(
            [[w] for w in data.WEIGHTS],
            row_labels=data.TOKENS,
            col_labels=[header("w_i", WEIGHT)],
            heat=WEIGHT,
            heat_range=(0, 0.5),
            cell_size=CELL,
        )
        values = MatrixGrid(data.VALUES, cell_size=CELL, fmt="{:.1f}", text_color=VALUE)
        contrib = MatrixGrid(data.CONTRIB, cell_size=CELL)
        # one header centered over both columns (MatrixGrid labels are per column)
        for g, tex, color in ((values, "v_i", VALUE), (contrib, r"w_i v_i", style.TEXT)):
            g.col_labels.add(header(tex, color).next_to(g.cells, UP, buff=0.15))
            g.add(g.col_labels)
        dot = MathTex(r"\times", font_size=style.MATH_SIZE, color=style.MUTED)
        eq = MathTex("=", font_size=style.MATH_SIZE, color=style.MUTED)
        row = VGroup(weights, dot, values, eq, contrib).arrange(RIGHT, buff=0.45)
        # align cell rows (labels make the groups different heights)
        for g in (values, contrib):
            g.shift((weights.cells.get_center()[1] - g.cells.get_center()[1]) * UP)
        row.move_to([-1.2, ROW_Y, 0])
        for sym in (dot, eq):
            sym.move_to([sym.get_x(), weights.cells.get_y(), 0])

        self.beat("show_tables", FadeIn(weights), FadeIn(dot), FadeIn(values), run=1.2, wait=1.2)

        # --- contributions, row by row ---------------------------------------------------------
        contrib_nums = [[contrib.cell(i, j)[1] for j in range(2)] for i in range(n)]
        contrib_frame = VGroup(
            *(contrib.cell(i, j)[0] for i in range(n) for j in range(2)), contrib.col_labels
        )
        sel = SurroundingRectangle(
            VGroup(weights.row(0), values.row(0), contrib.row(0)),
            color=style.YELLOW,
            buff=0.08,
            stroke_width=3,
        )
        cap = caption_text(
            "multiply each value by its token's weight", t2c={"value": VALUE, "weight": WEIGHT}
        )
        self.beat(
            "row_cat",
            FadeIn(eq),
            FadeIn(contrib_frame),
            Create(sel),
            FadeIn(cap),
            *(FadeIn(m, shift=0.3 * RIGHT) for m in contrib_nums[0]),
            run=1.4,
            wait=1.4,
        )
        # Succession: each box move starts where the previous one ended (a LaggedStart
        # would start every Transform from row 0, so the box would jump back each time).
        steps = []
        for i in range(1, n):
            target = SurroundingRectangle(
                VGroup(weights.row(i), values.row(i), contrib.row(i)),
                color=style.YELLOW,
                buff=0.08,
                stroke_width=3,
            )
            steps.append(
                LaggedStart(
                    Transform(sel, target),
                    *(FadeIn(m, shift=0.3 * RIGHT) for m in contrib_nums[i]),
                    lag_ratio=0.3,
                )
            )
        self.beat("rows_rest", Succession(*steps), run=2.4, wait=0.6)

        # --- column sums = output ---------------------------------------------------------------
        rule = Line(
            contrib.cells.get_corner(DOWN + LEFT),
            contrib.cells.get_corner(DOWN + RIGHT),
            color=style.TEXT,
            stroke_width=2,
        ).shift(0.18 * DOWN)
        out = MatrixGrid([data.OUTPUT], cell_size=CELL)
        out.next_to(rule, DOWN, buff=0.18).align_to(contrib.cells, LEFT)
        out_box = SurroundingRectangle(out, color=WEIGHT, buff=0.06, stroke_width=4)
        out_label = Text(
            f"output for “{data.QUERY_TOKEN}”", font=style.FONT, font_size=style.LABEL_SIZE, color=WEIGHT
        ).next_to(out_box, RIGHT, buff=0.3)
        top = int(np.argmax(data.WEIGHTS))
        sum_cap = caption_text(
            f"add the rows: mostly the value of “{data.TOKENS[top]}”", t2c={f"“{data.TOKENS[top]}”": VALUE}
        )
        self.beat(
            "sum_columns",
            FadeOut(sel),
            Create(rule),
            FadeIn(out, shift=0.2 * DOWN),
            Create(out_box),
            FadeIn(out_label),
            Transform(cap, sum_cap),
            run=1.6,
            wait=2.0,
        )

        # --- generalize: the matrix formula ------------------------------------------------------
        formula = Formula(
            [
                ("lhs", r"\mathrm{Attention}(Q, K, V) ="),
                ("sm", r"\mathrm{softmax}"),
                ("lp", r"\!\left("),
                ("scores", r"\frac{QK^\top}{\sqrt{d_k}}"),
                ("rp", r"\right)"),
                ("v", "V"),
            ],
            font_size=style.MATH_SIZE + 8,
        ).move_to([-0.6, 0.2, 0])
        new_cap = caption_text("every row of the matrix form is exactly this computation, for one query")
        tables = [
            weights,
            dot,
            values,
            eq,
            *contrib_frame,
            *sum(contrib_nums, []),
            rule,
            out,
            out_box,
            out_label,
        ]
        # clear first, then show: the formula occupies the tables' area
        self.beat(
            "clear_tables", *(FadeOut(m, shift=0.3 * UP) for m in tables), FadeOut(cap), run=0.8, wait=0.2
        )
        self.beat("general_form", Write(formula), FadeIn(new_cap), run=1.6, wait=1.5)

        # --- map formula parts back to scenes 1-3 --------------------------------------------------
        # Labels sit above/below their box and extend *away* from neighbouring boxes.
        def annotate(key, color, text, direction, edge):
            box = formula.box(key, color=color)
            lab = Text(text, font=style.FONT, font_size=style.LABEL_SIZE, color=color)
            lab.next_to(box, direction, buff=0.25, aligned_edge=edge)
            return box, lab

        for event, key, color, text, direction, edge, wait in [
            ("map_scores", "scores", KEY, "1 · scores", UP, 0 * LEFT, 1.2),
            ("map_softmax", "sm", WEIGHT, "2 · weights, row by row", DOWN, RIGHT, 1.2),
            ("map_values", "v", VALUE, "3 · weighted sum", DOWN, LEFT, 3.0),
        ]:
            box, lab = annotate(key, color, text, direction, edge)
            self.beat(
                event,
                Create(box),
                formula[key].animate.set_color(color),
                FadeIn(lab, shift=0.15 * -direction),
                run=0.9,
                wait=wait,
            )
