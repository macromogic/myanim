"""One minimal, working demo per shared component (also the usage examples).

Render:  myanim previews
"""

from manim import (
    DOWN,
    UP,
    Create,
    FadeIn,
    Integer,
    Line,
    ReplacementTransform,
    Succession,
    SurroundingRectangle,
    Write,
)

from components import (
    EduScene,
    Formula,
    MatrixGrid,
    WeightBars,
    baseline_y,
    caption,
    code_block,
    count_to,
    mixed,
    scene_title,
    source_tag,
    style,
)


class MatrixGridDemo(EduScene):
    def construct(self):
        g = MatrixGrid(
            [[0.9, 0.1, 0.0], [0.2, 0.7, 0.1], [0.0, 0.3, 0.7]],
            row_labels=["A", "B", "C"],
            col_labels=["A", "B", "C"],
            heat=style.PINK,
            heat_range=(0, 1),
            brackets=True,
        )
        self.beat("show", FadeIn(g), run=0.8, wait=0.3)
        box = g.highlight_row(1)
        self.beat("highlight_row", Create(box), run=0.6, wait=0.3)
        self.beat(
            "update",
            *g.animate_values([[0.5, 0.5, 0.0], [0.3, 0.4, 0.3], [0.1, 0.1, 0.8]]),
            run=1.0,
            wait=0.8,
        )


class WeightBarsDemo(EduScene):
    def construct(self):
        kw = dict(labels=["a", "b", "c", "d"], label_depth=0.9, max_height=2.6)
        bars = WeightBars([1.2, -0.3, 0.4, 0.8], value_range=(-0.5, 3.5), color=style.ORANGE, **kw)
        bars.move_baseline_to([0, -1.0, 0])
        self.beat("show", FadeIn(bars), run=0.8, wait=0.3)
        self.beat("animate_to", *bars.animate_to([3.3, 0.7, 1.5, 2.2]), run=1.0, wait=0.3)
        probs = WeightBars([0.43, 0.09, 0.19, 0.29], value_range=(0, 0.5), color=style.PINK, **kw)
        probs.move_baseline_to([0, -1.0, 0])
        self.beat("rescale", ReplacementTransform(bars, probs), run=1.0, wait=0.8)


class FormulaDemo(EduScene):
    def construct(self):
        f = Formula(
            [
                ("w", "w_i"),
                ("eq", r"= \frac{"),
                ("num", r"e^{s_i}"),
                ("bar", "}{"),
                ("den", r"\sum_j e^{s_j}"),
                ("end", "}"),
            ],
            colors={"w": style.PINK},
            font_size=56,
        )
        self.beat("write", Write(f), run=1.0, wait=0.3)
        box = f.box("num")
        self.beat("box_numerator", Create(box), run=0.6, wait=0.3)
        self.beat("box_denominator", box.animate.become(f.box("den")), run=0.8, wait=0.8)


class TextDemo(EduScene):
    def construct(self):
        title = scene_title("Scene title", "Optional subtitle in muted text")
        tag = source_tag("source §2.1")
        cap = caption("One short caption per idea, bottom center")
        self.beat(
            "show",
            FadeIn(title, shift=0.2 * DOWN),
            FadeIn(tag),
            FadeIn(cap, shift=0.2 * UP),
            run=0.8,
            wait=1.0,
        )


class MixedDemo(EduScene):
    def construct(self):
        line = mixed(r"长度为 $\ell$ 的循环需要 $\ell + 1$ 次调用", size=34)
        y = baseline_y(line)
        rule = Line(
            [line.get_left()[0] - 0.2, y, 0],
            [line.get_right()[0] + 0.2, y, 0],
            color=style.GRID,
            stroke_width=1,
        )
        rule.qa_ignore = True  # baseline guide, deliberately under text
        num = Integer(0, font_size=48).next_to(line, DOWN, buff=0.6)
        self.beat("show", FadeIn(line), FadeIn(rule), FadeIn(num), run=0.8, wait=0.3)
        self.beat("count_to", Succession(*(count_to(num, i, i + 1) for i in range(5))), run=1.5, wait=0.8)


class CodeBlockDemo(EduScene):
    def construct(self):
        block = code_block(
            [
                "auto H = std::gcd(n + m, k + m);  // 只扫描前 g 个位置",
                "for (auto pos = 0ULL; pos < H; pos++) {",
                "    walk_cycle(pos);",
                "}",
            ]
        )
        self.beat("show", FadeIn(block), run=0.8, wait=0.3)
        self.beat(
            "highlight",
            Create(SurroundingRectangle(block.lines[0], color=style.YELLOW, buff=0.06)),
            run=0.6,
            wait=0.8,
        )
