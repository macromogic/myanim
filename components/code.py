"""code_block(): monochrome code panel that keeps accent colors meaningful.

Why: Manim's `Code` uses Pygments themes that paint keywords/operators in many colors,
which collide with the video's concept colors. `code_block` renders code in the body
color with `//` comments muted, on a SURFACE panel, using the MONO font token (with
CJK fallback, so Chinese comments work).

    block = code_block(["auto H = std::gcd(n + m, k + m);  // 注释",
                        "for (auto pos = 0ULL; pos < H; pos++) {",
                        "    work(pos);",
                        "}"])
    self.play(FadeIn(block))
    self.play(Create(SurroundingRectangle(block.lines[0], color=style.YELLOW)))

Parameters: `lines` (leading spaces = indentation), `size`. Limitations: no syntax
highlighting by design; only `//` line comments are recognized; ≤ ~12 lines.
"""

from __future__ import annotations

from manim import DOWN, LEFT, RIGHT, RoundedRectangle, Text, VGroup

from . import style


def code_block(lines: list[str], size: float = style.LABEL_SIZE) -> VGroup:
    """Monochrome code (body color, `//` comments muted) on a SURFACE panel.

    Unlike Manim's Code + Pygments themes, it uses no accent colors, so accents keep their
    meaning. Leading spaces become indentation. `block.lines[i]` is line i (for highlights).
    """
    char_w = Text("M", font=style.MONO_FONT, font_size=size).width * 1.08
    rows = VGroup()
    for line in lines:
        body, sep, comment = line.partition("//")
        parts = VGroup()
        if body.strip():
            parts.add(Text(body.strip(), font=style.MONO_FONT, font_size=size, color=style.TEXT))
        if sep:
            parts.add(Text("//" + comment, font=style.MONO_FONT, font_size=size, color=style.MUTED))
        parts.arrange(RIGHT, buff=char_w * 2)
        anchor = Text("M", font=style.MONO_FONT, font_size=size).set_opacity(0)  # keeps the line height
        rows.add(VGroup(anchor, parts).arrange(RIGHT, buff=0))
    rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
    for line_mob, line in zip(rows, lines, strict=True):
        indent = len(line) - len(line.lstrip(" "))
        line_mob.shift(RIGHT * indent * char_w)
    panel = RoundedRectangle(
        width=rows.width + 0.6,
        height=rows.height + 0.45,
        corner_radius=0.12,
        fill_color=style.SURFACE,
        fill_opacity=1,
        stroke_color=style.GRID,
        stroke_width=1.5,
    )
    panel.move_to(rows)
    block = VGroup(panel, rows)
    block.lines = rows
    return block
