"""Project fonts: register assets/fonts/*.otf with Pango so renders don't depend on
system-installed fonts. Runs once when `components` is imported. The files are
downloaded from pinned upstream sources by `scripts/fonts.py sync` (not stored in git).

Font tokens in style.py are Pango *fallback lists*, e.g. "Libertinus Serif, Noto Serif CJK SC":
Latin glyphs come from the first family, CJK glyphs fall through to the second.
Manim warns "Font ... not in [...]" for any list (it only knows single families);
that warning is filtered here, and every family is verified instead.

Only text set with Manim `Text`/`MarkupText`/`Code` uses these. `MathTex` is typeset by
LaTeX and is unaffected.
"""

from __future__ import annotations

import logging
from pathlib import Path

import manimpango

FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


class _FontListWarningFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not (msg.startswith("Font ") and " not in [" in msg and "," in msg.split(" not in [")[0])


def register_project_fonts() -> list[str]:
    registered = []
    for path in sorted(FONT_DIR.glob("*.otf")) + sorted(FONT_DIR.glob("*.ttf")):
        if manimpango.register_font(str(path)):
            registered.append(path.name)
    logging.getLogger("manim").addFilter(_FontListWarningFilter())
    return registered


def check_families(*font_tokens: str) -> None:
    """Raise if any family named in the font tokens is unavailable to Pango."""
    available = set(manimpango.list_fonts())
    missing = sorted({fam.strip() for tok in font_tokens for fam in tok.split(",")} - available)
    if missing:
        cjk = [
            fam.rsplit(" ", 1)[1]
            for fam in missing
            if fam.startswith("Noto Serif CJK ") and not fam.endswith(" SC")
        ]  # SC: synced by default
        fix = "uv run python scripts/fonts.py sync" + (f" --cjk {','.join(cjk)}" if cjk else "")
        raise RuntimeError(
            f"fonts not available to Pango: {missing}. Font files are downloaded, "
            f"not stored in git. Fix: {fix}"
        )
