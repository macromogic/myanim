r"""mixed(): one line of body text (any language, incl. CJK) with inline LaTeX math.

Why: LaTeX here cannot typeset CJK, and Pango cannot typeset math. `mixed()` splits a
string at `$...$`, builds `Text` for prose and `MathTex` for math, and places all pieces on
one shared baseline (measured from an invisible reference "x" in each piece, so
descenders, subscripts and fractions don't shift alignment).

    line = mixed(r"半径为 $r$ 的圆，面积是 $\pi r^2$")
    line = mixed(r"二分查找只需 $\lceil \log_2 n \rceil$ 次比较", size=style.BODY_SIZE)
    line.math[0]          # the MathTex pieces, in order (e.g. to box or recolor one)
    line.prose[0]         # the Text pieces
    baseline_y(line)      # current baseline height

Parameters: `size` (Text font size; math is scaled by style.TEX_SCALE to match),
`color`, `math_color` (default: same), `t2c` (applied to prose pieces), `gap`
(space between pieces, in units of size; spaces at piece edges are dropped by Pango).
Limitations: a single line (no wrapping); `$` cannot appear literally.
"""

from __future__ import annotations

import re

from manim import MathTex, Text, VectorizedPoint, VGroup

from . import style


def _baseline_text(s: str, size: float, color, t2c, weight: str = "NORMAL") -> Text:
    t = Text("x" + s, font=style.FONT, font_size=size, color=color, t2c=t2c or {}, weight=weight)
    ref = t.submobjects[0]
    baseline = ref.get_bottom()[1]
    t.remove(ref)
    t.text = s  # drop the reference "x" from the reported text
    t.baseline = baseline
    return t


def _baseline_math(tex: str, size: float, color) -> MathTex:
    m = MathTex(r"\mathrm{x}", tex, font_size=size * style.TEX_SCALE, color=color)
    ref = m.submobjects[0]
    baseline = ref.get_bottom()[1]
    m.remove(ref)
    m.tex_string = tex  # drop the reference glyph from the reported source
    m.baseline = baseline
    return m


def mixed(
    s: str,
    size: float = style.CAPTION_SIZE,
    color=style.TEXT,
    math_color=None,
    t2c: dict | None = None,
    gap: float = 0.18,
    weight: str = "NORMAL",
) -> VGroup:
    pieces = [p for p in re.split(r"(\$[^$]+\$)", s) if p.strip()]
    line, prose, maths = VGroup(), [], []
    x, space = 0.0, gap * size / 48  # scene units; ~ a space at this size
    for p in pieces:
        if p.startswith("$"):
            mob = _baseline_math(p[1:-1], size, math_color or color)
            maths.append(mob)
        else:
            mob = _baseline_text(p.strip(), size, color, t2c, weight)
            prose.append(mob)
        # left edge to x, baseline to y = 0 (one shift keeps all pieces on one baseline)
        mob.shift([x - mob.get_left()[0], -mob.baseline, 0])
        x = mob.get_right()[0] + space
        line.add(mob)
    # invisible anchor on the baseline: follows every move/scale of the line
    line.baseline_anchor = VectorizedPoint([0.0, 0.0, 0.0])
    line.add(line.baseline_anchor)
    line.prose, line.math = prose, maths
    line.text_unit = True  # layout QA treats the whole line as one piece of text
    line.text = "".join(getattr(p, "text", "") or getattr(p, "tex_string", "") for p in line[:-1])
    return line


def baseline_y(line: VGroup) -> float:
    """Current y of a `mixed()` line's baseline (e.g. to align it with other text)."""
    return line.baseline_anchor.get_y()
