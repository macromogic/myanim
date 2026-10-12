"""Design tokens: the single source of truth for color, type, spacing and pacing.

Rules (see references/design-system.md for rationale):
- Colors carry *meaning*. Assign each concept one semantic role per project and
  never reuse that role's color for something else in the same video.
- At most ~3 accent colors on screen at once. Everything else is TEXT or MUTED.
- Sizes are in Manim font_size units for a 1080p frame (14.22 x 8 units).
"""

from manim import ManimColor, TexTemplate

# --- Palette -----------------------------------------------------------------
BG = ManimColor("#0E1117")  # near-black, slightly blue
SURFACE = ManimColor("#1A1F2B")  # panels, cell backgrounds
GRID = ManimColor("#2C3342")  # axes, grid lines, cell borders
TEXT = ManimColor("#E8E6E3")  # primary text / math
MUTED = ManimColor("#8B92A1")  # secondary text, de-emphasized objects
DIM_OPACITY = 0.25  # opacity for "pushed back" objects

# Accents. Generic names; projects map them to concepts (e.g. QUERY = BLUE).
BLUE = ManimColor("#5DA9E9")
ORANGE = ManimColor("#F2A541")
GREEN = ManimColor("#7BC67E")
PINK = ManimColor("#E86A92")
PURPLE = ManimColor("#B48EF0")
YELLOW = ManimColor("#F4D35E")  # reserved for transient "look here" highlights
ACCENTS = [BLUE, ORANGE, GREEN, PINK, PURPLE]

# --- Typography ----------------------------------------------------------------
# Fonts live in assets/fonts/ (downloaded by myanim fonts sync, pinned + checksummed)
# and are registered by components/fonts.py, so renders
# are identical on any machine. Tokens are Pango fallback lists: Latin glyphs from the
# first family, CJK glyphs from Noto Serif CJK in the selected region's glyph forms.
#
# CJK region: default below; a project overrides it in project.toml with
#     [style]
#     cjk = "JP"        # SC | TC | HK | JP | KR
# `myanim fonts sync` fetches every region a project selects.
CJK_REGIONS = {
    "SC": "Noto Serif CJK SC",  # Simplified Chinese (default)
    "TC": "Noto Serif CJK TC",  # Traditional Chinese (Taiwan)
    "HK": "Noto Serif CJK HK",  # Traditional Chinese (Hong Kong)
    "JP": "Noto Serif CJK JP",  # Japanese
    "KR": "Noto Serif CJK KR",  # Korean
}
DEFAULT_CJK_REGION = "SC"


def set_cjk_region(region: str) -> None:
    """Point the font tokens at another CJK region. Call before building any Text."""
    global CJK_REGION, CJK_FONT, FONT, MONO_FONT
    if region not in CJK_REGIONS:
        raise ValueError(f"unknown CJK region {region!r}; choose from {sorted(CJK_REGIONS)}")
    CJK_REGION, CJK_FONT = region, CJK_REGIONS[region]
    FONT = f"Libertinus Serif, {CJK_FONT}"
    MONO_FONT = f"IBM Plex Mono, {CJK_FONT}"


set_cjk_region(DEFAULT_CJK_REGION)
# LaTeX: \text{} inside MathTex uses Libertinus Serif (matches Text); math symbols stay
# Computer Modern. Installed as config.tex_template by components/__init__.py.
TEX_TEMPLATE = TexTemplate()
TEX_TEMPLATE.add_to_preamble(r"\usepackage{libertinus-type1}")
TEX_SCALE = 1.34  # MathTex font_size that matches Text at the same nominal size
TITLE_WEIGHT = "SEMIBOLD"  # available weights: Libertinus Regular/Semibold/Bold; Noto CJK Regular/SemiBold

TITLE_SIZE = 44
HEADING_SIZE = 34
BODY_SIZE = 30
CAPTION_SIZE = 26
LABEL_SIZE = 24  # Libertinus has a small x-height: keep labels >= 24
SMALL_SIZE = 20
MATH_SIZE = 40  # MathTex default for primary formulas
MATH_SMALL = 30

# --- Layout ---------------------------------------------------------------------
FRAME_MARGIN = 0.5  # keep content this far inside the frame edge
BUFF_TIGHT = 0.15
BUFF = 0.3
BUFF_LOOSE = 0.6
CAPTION_Y = -3.35  # baseline zone for the bottom caption strip
TITLE_Y = 3.35

# --- Pacing (seconds) -------------------------------------------------------------
RUN_FAST = 0.6
RUN = 1.0
RUN_SLOW = 1.6
WAIT_SHORT = 0.5
WAIT = 1.0  # default pause after a meaningful event
WAIT_LONG = 2.0  # pause after a key insight lands
