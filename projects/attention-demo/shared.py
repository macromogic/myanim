"""Project-level conventions shared by all scenes: concept colors and hand-off objects.

Scenes are rendered as separate videos. When scene N ends on an object that scene
N+1 starts from, both build it with the same function here, so the cut is seamless.
"""

from manim import MathTex

from components import MatrixGrid, style

import data

# Concept -> color. Never reuse these colors for other meanings in this video.
QUERY = style.BLUE
KEY = style.ORANGE
VALUE = style.GREEN
WEIGHT = style.PINK

SCORE_COLUMN_POS = (3.4, -0.55, 0)


def score_column(values=data.RAW, header=r"q \cdot k_i") -> MatrixGrid:
    """4x1 grid of per-token scores (end of s01, start of s02)."""
    col = MatrixGrid(
        [[v] for v in values],
        row_labels=data.TOKENS,
        col_labels=[MathTex(header, font_size=style.MATH_SMALL, color=KEY)],
        cell_size=0.8,
        font_size=style.LABEL_SIZE + 2,
    )
    col.move_to(SCORE_COLUMN_POS)
    return col


def scaled_header() -> MathTex:
    return MathTex("s_i", font_size=style.MATH_SMALL, color=KEY)


def final_score_column() -> MatrixGrid:
    col = score_column(data.SCORES)
    col.col_labels[0].become(scaled_header().move_to(col.col_labels[0]))
    return col
