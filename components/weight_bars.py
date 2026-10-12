"""WeightBars: labeled vertical bars for a small vector of values (signed allowed).

Good for: probability distributions, softmax outputs, scores, losses per item,
any 3-10 element vector whose values change during the explanation.

    bars = WeightBars([1.33, 0.08, -0.25, 0.69], labels=["cat", "on", "the", "mat"],
                      value_range=(-0.5, 4.0), color=style.ORANGE)
    self.play(FadeIn(bars))
    self.play(*bars.animate_to([3.78, 1.08, 0.78, 1.99]))     # bars + numbers morph

`value_range` fixes the vertical scale so that successive `animate_to` calls are
visually comparable; choose it to cover every value the bars will take.
To switch to a different scale (e.g. scores -> probabilities), build a second
WeightBars with the same `label_depth`, `move_baseline_to` the same point and
ReplacementTransform into it: labels stay put, bars rescale.
"""

from __future__ import annotations

from collections.abc import Sequence

from manim import DOWN, UP, Line, Rectangle, Text, Transform, VGroup

from . import style


class WeightBars(VGroup):
    def __init__(
        self,
        values: Sequence[float],
        labels: Sequence[str] | None = None,
        value_range: tuple[float, float] = (0.0, 1.0),
        max_height: float = 2.5,
        bar_width: float = 0.6,
        spacing: float = 1.1,
        color=style.BLUE,
        colors: Sequence | None = None,  # per-bar colors override `color`
        fmt: str = "{:.2f}",
        show_values: bool = True,
        label_color=style.TEXT,
        font_size: int = style.LABEL_SIZE,
        label_depth: float | None = None,  # fixed label distance below baseline
    ):
        super().__init__()
        self.values = list(values)
        self.vmin, self.vmax = min(value_range[0], 0.0), value_range[1]
        self.unit = max_height / (self.vmax - self.vmin)
        self.bar_width, self.spacing, self.fmt = bar_width, spacing, fmt
        self.colors = list(colors) if colors else [color] * len(values)
        self.font_size, self.show_values = font_size, show_values
        n = len(values)
        width = (n - 1) * spacing + bar_width + 0.4

        self.baseline = Line([-width / 2, 0, 0], [width / 2, 0, 0], stroke_color=style.GRID, stroke_width=2)
        self.bars, self.value_labels = self._build(self.values)
        self.labels = VGroup()
        if labels:
            # room for the deepest negative bar plus its value label underneath
            auto = -self.vmin * self.unit + (0.45 if self.vmin < 0 else 0) + style.BUFF
            depth = label_depth if label_depth is not None else auto
            for k, txt in enumerate(labels):
                lab = Text(txt, font=style.FONT, font_size=font_size, color=label_color)
                # bottom-aligned: approximates a shared baseline (wrong only for descenders)
                lab.move_to([self._x(k), -depth - 0.25, 0], aligned_edge=DOWN)
                self.labels.add(lab)
        self.add(self.baseline, self.bars, self.value_labels, self.labels)

    def _x(self, k: int) -> float:
        return (k - (len(self.values) - 1) / 2) * self.spacing

    def _build(self, values):
        origin = self.baseline.get_center()
        bars, nums = VGroup(), VGroup()
        for k, v in enumerate(values):
            h = max(abs(v) * self.unit, 0.02)
            bar = Rectangle(width=self.bar_width, height=h, stroke_width=0)
            bar.set_fill(self.colors[k], opacity=0.85 if v >= 0 else 0.45)
            sign = 1 if v >= 0 else -1
            bar.move_to(origin + [self._x(k), sign * h / 2, 0])
            bars.add(bar)
            num = Text(
                self.fmt.format(v + 0.0), font=style.FONT, font_size=self.font_size - 2, color=style.TEXT
            )
            num.next_to(bar, UP if v >= 0 else DOWN, buff=style.BUFF_TIGHT)
            if not self.show_values:
                num.set_opacity(0)
            nums.add(num)
        return bars, nums

    def move_baseline_to(self, point) -> WeightBars:
        """Position by the baseline's center (stable when values change)."""
        return self.shift(point - self.baseline.get_center())

    def bar_group(self, k: int) -> VGroup:
        """Bar k with its value and label, e.g. for highlighting."""
        parts = [self.bars[k], self.value_labels[k]]
        if len(self.labels):
            parts.append(self.labels[k])
        return VGroup(*parts)

    def animate_to(self, values: Sequence[float]) -> list:
        """Transforms that morph bars and their numbers to new `values`."""
        bars, nums = self._build(values)
        self.values = list(values)
        return [Transform(b, t) for b, t in zip(self.bars, bars, strict=True)] + [
            Transform(n, t) for n, t in zip(self.value_labels, nums, strict=True)
        ]
