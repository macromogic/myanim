"""Reusable Manim components. Import in scenes with `from components import *`.

Catalog with parameters, previews and limitations: components/README.md
"""

from manim import config as _config

from . import style
from .fonts import check_families, register_project_fonts
from .formula import Formula
from .matrix_grid import MatrixGrid
from .scene import EduScene
from .text import caption, label, math, math_label, place_caption, scene_title, source_tag
from .weight_bars import WeightBars

# Side effects at import time; importing the modules above builds no Text, so this order is safe.
register_project_fonts()  # before any Text is built
check_families(style.FONT, style.MONO_FONT)
_config.tex_template = style.TEX_TEMPLATE

__all__ = [
    "style",
    "EduScene",
    "Formula",
    "MatrixGrid",
    "WeightBars",
    "caption",
    "label",
    "math",
    "math_label",
    "place_caption",
    "scene_title",
    "source_tag",
]
