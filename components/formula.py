r"""Formula: MathTex whose pieces are addressable by name.

Why: explanations repeatedly point at *parts* of a formula ("this denominator is
the scaling"). Naming the parts keeps scene code readable and robust to edits of
the TeX, unlike numeric submobject indices.

    f = Formula([("sm", r"\mathrm{softmax}\!\left("), ("qk", r"QK^\top"),
                 ("div", r"/\sqrt{d_k}"), ("rp", r"\right)"), ("v", "V")],
                colors={"qk": style.ORANGE, "v": style.GREEN})
    self.play(Write(f))
    self.play(Create(f.box("div")))      # outline one part
    f["qk"]                               # the sub-mobject for that part

Parts are joined and compiled as ONE expression (Manim >= 0.18 marks part
boundaries internally), so a part may contain unbalanced braces, e.g.
[("lhs", "w_i = \frac{"), ("num", "e^{s_i}"), ("mid", "}{"), ("den", r"\sum_j e^{s_j}"), ("end", "}")]
-- here "mid" is the fraction bar. `\left(` ... `\right)` across parts also works.
"""

from __future__ import annotations

from collections.abc import Sequence

from manim import MathTex, SurroundingRectangle

from . import style


class Formula(MathTex):
    def __init__(
        self,
        parts: Sequence[tuple[str, str]],
        colors: dict | None = None,
        font_size: int = style.MATH_SIZE,
        color=style.TEXT,
        **kw,
    ):
        self.keys = [k for k, _ in parts]
        if len(set(self.keys)) != len(self.keys):
            raise ValueError(f"duplicate formula part keys: {self.keys}")
        super().__init__(*(tex for _, tex in parts), font_size=font_size, color=color, **kw)
        for key, col in (colors or {}).items():
            self[key].set_color(col)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.submobjects[self.keys.index(key)]
        return super().__getitem__(key)

    def box(self, *keys: str, color=style.YELLOW, buff: float = 0.08) -> SurroundingRectangle:
        from manim import VGroup

        target = VGroup(*(self[k] for k in keys))
        return SurroundingRectangle(target, color=color, buff=buff, stroke_width=3, corner_radius=0.05)
