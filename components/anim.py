"""Small animation helpers that avoid Manim's construction-time pitfalls."""

from __future__ import annotations

from manim import ChangingDecimal, DecimalNumber


def count_to(number: DecimalNumber, start: float, end: float, integer: bool = True) -> ChangingDecimal:
    """Animate a counter from an explicit `start` to `end`.

    Use instead of ChangeDecimalToValue when chaining steps (e.g. in a Succession):
    ChangeDecimalToValue reads the start value when it is *constructed*, so every step
    built up front would restart from the same old value. Integers change at the midpoint.
    """
    if integer:
        return ChangingDecimal(number, lambda a: start if a < 0.5 else end)
    return ChangingDecimal(number, lambda a: start + (end - start) * a)
