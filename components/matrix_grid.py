"""MatrixGrid: a numeric matrix drawn as a grid of cells, with optional heat tint.

Good for: attention matrices, confusion matrices, small tables, DP tables,
any 2-D array where individual cells get highlighted or updated.
Not for: large matrices (> ~8x8 at readable sizes) -- summarize those instead.

    g = MatrixGrid([[0.5, 0.14], [0.1, 0.26]], row_labels=["a", "b"],
                   col_labels=["x", "y"], heat=style.PINK, brackets=True)
    self.play(FadeIn(g))
    box = g.highlight_row(0)          # returns a Rectangle; animate with Create
    self.play(*g.animate_values(new_values))
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Line,
    Mobject,
    Rectangle,
    Square,
    Text,
    Transform,
    VGroup,
)

from . import style


class MatrixGrid(VGroup):
    def __init__(
        self,
        values: Sequence[Sequence[float]],
        fmt: str = "{:.2f}",
        cell_size: float = 0.8,
        font_size: int = style.LABEL_SIZE,
        row_labels: Sequence[str | Mobject] | None = None,
        col_labels: Sequence[str | Mobject] | None = None,
        label_color=style.MUTED,
        heat=None,  # accent color -> tint cells by |value|
        heat_range: tuple[float, float] | None = None,
        brackets: bool = False,
        cell_fill=style.SURFACE,
        border_color=style.GRID,
        text_color=style.TEXT,
    ):
        super().__init__()
        self.values = np.array(values, dtype=float)
        self.fmt, self.cell_size, self.font_size = fmt, cell_size, font_size
        self.heat, self.cell_fill, self.text_color = heat, cell_fill, text_color
        self.heat_range = heat_range or (0.0, float(np.abs(self.values).max() or 1.0))
        n_rows, n_cols = self.values.shape

        self.cells = VGroup()  # VGroup of rows; each row is VGroup of cells
        for i in range(n_rows):
            row = VGroup()
            for j in range(n_cols):
                sq = Square(cell_size, stroke_color=border_color, stroke_width=1.5)
                sq.set_fill(self._fill_for(self.values[i, j]), opacity=1)
                num = self._number(self.values[i, j]).move_to(sq)
                cell = VGroup(sq, num)
                cell.move_to([j * cell_size, -i * cell_size, 0])
                row.add(cell)
            self.cells.add(row)
        self.add(self.cells)

        self.row_labels = VGroup()
        if row_labels:
            for i, txt in enumerate(row_labels):
                lab = _make_label(txt, font_size, label_color)
                lab.next_to(self.cells[i][0], LEFT, buff=style.BUFF)
                self.row_labels.add(lab)
            self.add(self.row_labels)
        self.col_labels = VGroup()
        if col_labels:
            for j, txt in enumerate(col_labels):
                lab = _make_label(txt, font_size, label_color)
                lab.next_to(self.cells[0][j], UP, buff=style.BUFF_TIGHT)
                self.col_labels.add(lab)
            self.add(self.col_labels)
        self.brackets = VGroup()
        if brackets:
            self.brackets = _brackets(self.cells)
            self.add(self.brackets)
        self.center()

    # --- construction helpers ---------------------------------------------------
    def _number(self, v: float) -> Text:
        return Text(
            self.fmt.format(v + 0.0), font=style.FONT, font_size=self.font_size, color=self.text_color
        )

    def _fill_for(self, v: float):
        if self.heat is None:
            return self.cell_fill
        lo, hi = self.heat_range
        alpha = float(np.clip((abs(v) - lo) / max(hi - lo, 1e-9), 0, 1))
        return self.cell_fill.interpolate(self.heat, 0.15 + 0.7 * alpha)

    # --- access -----------------------------------------------------------------
    def cell(self, i: int, j: int) -> VGroup:
        return self.cells[i][j]

    def row(self, i: int) -> VGroup:
        return self.cells[i]

    def col(self, j: int) -> VGroup:
        return VGroup(*(r[j] for r in self.cells))

    # --- highlights (return mobjects; the scene decides how to animate) ----------
    def _box(self, target, color, buff=0.06) -> Rectangle:
        return Rectangle(
            width=target.width + 2 * buff, height=target.height + 2 * buff, stroke_color=color, stroke_width=4
        ).move_to(target)

    def highlight_row(self, i: int, color=style.YELLOW) -> Rectangle:
        return self._box(self.row(i), color)

    def highlight_col(self, j: int, color=style.YELLOW) -> Rectangle:
        return self._box(self.col(j), color)

    def highlight_cell(self, i: int, j: int, color=style.YELLOW) -> Rectangle:
        return self._box(self.cell(i, j), color)

    # --- updates -------------------------------------------------------------------
    def animate_values(self, new_values, recolor: bool = True) -> list:
        """Transforms that morph numbers (and heat tint) to `new_values`."""
        new_values = np.array(new_values, dtype=float)
        anims = []
        for i, row in enumerate(self.cells):
            for j, (sq, num) in enumerate(row):
                target = self._number(new_values[i, j]).move_to(sq)
                anims.append(Transform(num, target))
                if recolor and self.heat is not None:
                    anims.append(sq.animate.set_fill(self._fill_for(new_values[i, j]), opacity=1))
        self.values = new_values
        return anims


def _make_label(x, font_size, color) -> Mobject:
    """Strings become Text; pass a MathTex (or any Mobject) for math labels."""
    if isinstance(x, Mobject):
        return x
    return Text(x, font=style.FONT, font_size=font_size, color=color)


def _brackets(body, pad: float = 0.12, arm: float = 0.15, color=style.TEXT) -> VGroup:
    lo, hi = body.get_corner(DOWN + LEFT), body.get_corner(UP + RIGHT)
    x0, x1 = lo[0] - pad, hi[0] + pad
    y0, y1 = lo[1] - pad, hi[1] + pad
    kw = dict(stroke_color=color, stroke_width=3)
    left = VGroup(
        Line([x0, y0, 0], [x0, y1, 0], **kw),
        Line([x0, y1, 0], [x0 + arm, y1, 0], **kw),
        Line([x0, y0, 0], [x0 + arm, y0, 0], **kw),
    )
    right = VGroup(
        Line([x1, y0, 0], [x1, y1, 0], **kw),
        Line([x1, y1, 0], [x1 - arm, y1, 0], **kw),
        Line([x1, y0, 0], [x1 - arm, y0, 0], **kw),
    )
    return VGroup(left, right)
