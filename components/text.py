"""Text helpers: consistent titles, captions, labels and source tags."""

from __future__ import annotations

from manim import DOWN, LEFT, UL, UR, MathTex, Text, VGroup, config

from . import style


def label(text: str, color=style.TEXT, size: int = style.LABEL_SIZE, **kw) -> Text:
    return Text(text, font=style.FONT, font_size=size, color=color, **kw)


def math(tex: str, color=style.TEXT, size: int = style.MATH_SIZE, **kw) -> MathTex:
    return MathTex(tex, font_size=size, color=color, **kw)


def math_label(tex: str, color=style.TEXT, size: int = style.LABEL_SIZE, **kw) -> MathTex:
    r"""A label containing symbols, sized to match `label()` text of the same `size`.

    Symbols in math, words in \text{}: `math_label(r"q\ \text{(it)}")`. TeX handles the
    baseline, and \text{} renders in the body font.
    """
    return MathTex(tex, font_size=size * style.TEX_SCALE, color=color, **kw)


def scene_title(text: str, subtitle: str | None = None) -> VGroup:
    """Top-left title. Small enough to stay on screen as an anchor."""
    title = Text(
        text, font=style.FONT, font_size=style.HEADING_SIZE, color=style.TEXT, weight=style.TITLE_WEIGHT
    )
    group = VGroup(title)
    if subtitle:
        sub = Text(subtitle, font=style.FONT, font_size=style.CAPTION_SIZE, color=style.MUTED)
        sub.next_to(title, DOWN, buff=style.BUFF_TIGHT, aligned_edge=LEFT)
        group.add(sub)
    group.to_corner(UL, buff=style.FRAME_MARGIN)
    return group


def caption(
    text: str, color=style.TEXT, size: int = style.CAPTION_SIZE, max_width: float | None = None
) -> Text:
    """Bottom-center one-line explanation. Keep it short: one idea per caption.

    Use **t2c** style coloring by passing `t2c={"query": style.BLUE}` via Text if needed;
    for that, build Text directly and call `place_caption`.
    """
    return place_caption(Text(text, font=style.FONT, font_size=size, color=color), max_width=max_width)


def place_caption(mob, max_width: float | None = None):
    max_width = max_width or config.frame_width - 2 * style.FRAME_MARGIN - 1.0
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    mob.move_to([0, style.CAPTION_Y, 0])
    return mob


def source_tag(ref: str) -> Text:
    """Small top-right reference back to the source material (traceability)."""
    tag = Text(ref, font=style.FONT, font_size=style.SMALL_SIZE, color=style.MUTED)
    tag.set_opacity(0.7)
    return tag.to_corner(UR, buff=style.FRAME_MARGIN * 0.6)
