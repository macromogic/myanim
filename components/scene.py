"""EduScene: Scene base class with named timing events, an event log and layout QA.

Usage in a project scene:

    class S01Scores(EduScene):
        SCENE_ID = "s01_scores"          # key in the project's timing.toml

        def construct(self):
            self.beat("show_query", FadeIn(q), run=1.0, wait=0.5)

`beat(event_id, *animations, run=..., wait=...)` plays the animations and then
waits. The defaults written in code can be overridden per event in
`<project>/timing.toml` without touching scene code:

    [s01_scores]
    show_query = { run = 1.5, wait = 2.0 }

Each beat is logged (start, end of animation, end of wait) to
`<project>/renders/qa/<SceneClass>.events.json` together with layout warnings.
That file drives frame extraction (scripts/review.py) and is the hook for a
future narration-sync step.
"""

from __future__ import annotations

import inspect
import json
import tomllib
from pathlib import Path

from manim import (
    Animation,
    AnimationGroup,
    MathTex,
    Mobject,
    Rectangle,
    Scene,
    SingleStringMathTex,
    Succession,
    Tex,
    Text,
    VMobject,
    config,
)
from manim.animation.animation import prepare_animation

from . import style
from .fonts import check_families


def _project_dir(scene_cls: type) -> Path | None:
    """Walk up from the scene's source file to the folder holding project.toml."""
    try:
        path = Path(inspect.getfile(scene_cls)).resolve()
    except (TypeError, OSError):
        return None
    for parent in path.parents:
        if (parent / "project.toml").exists():
            return parent
    return None


class EduScene(Scene):
    SCENE_ID: str = ""  # key into timing.toml; defaults to class name
    CHECK_LAYOUT: bool = True

    def setup(self):
        self.camera.background_color = style.BG
        self._project = _project_dir(type(self))
        self._events: list[dict] = []
        self._warnings: list[dict] = []
        self._timing = self._load_timing()
        self._apply_project_style()

    # --- per-project style overrides (project.toml [style]) ---------------------
    def _apply_project_style(self):
        cfg = {}
        if self._project:
            with open(self._project / "project.toml", "rb") as f:
                cfg = tomllib.load(f).get("style", {})
        style.set_cjk_region(cfg.get("cjk", style.DEFAULT_CJK_REGION))
        check_families(style.FONT, style.MONO_FONT)

    # --- timing -------------------------------------------------------------
    def _load_timing(self) -> dict:
        if not self._project:
            return {}
        path = self._project / "timing.toml"
        if not path.exists():
            return {}
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return data.get(self.SCENE_ID or type(self).__name__, {})

    def timing(self, event_id: str, run: float, wait: float) -> tuple[float, float]:
        override = self._timing.get(event_id, {})
        scale = self._timing.get("_speed", 1.0)  # global per-scene multiplier
        return override.get("run", run) / scale, override.get("wait", wait) / scale

    def beat(
        self,
        event_id: str,
        *animations,
        run: float = style.RUN,
        wait: float = style.WAIT,
        **play_kwargs,
    ):
        """Play one meaningful educational event, then pause. Logged by id."""
        if any(e["id"] == event_id for e in self._events):
            raise ValueError(f"duplicate event id {event_id!r} in {type(self).__name__}")
        run, wait = self.timing(event_id, run, wait)
        animations = [prepare_animation(a) for a in animations]
        self._check_animations(event_id, animations)
        start = self.time
        if animations:
            self.play(*animations, run_time=run, **play_kwargs)
        anim_end = self.time
        if wait > 0:
            self.wait(wait)
        self._events.append(
            {
                "id": event_id,
                "start": round(start, 3),
                "anim_end": round(anim_end, 3),
                "end": round(self.time, 3),
            }
        )
        if self.CHECK_LAYOUT:
            self._check_layout(event_id)

    def consolidate(self, group: Mobject) -> Mobject:
        """Replace loose top-level pieces of `group` with the group itself.

        Needed when a group's parts entered the scene one by one (e.g. as targets
        of separate ReplacementTransforms) and the group is then animated as a
        whole: otherwise the loose pieces stay behind as ghost copies.
        """
        family = set(map(id, group.get_family()))
        self.remove(*(m for m in self.mobjects if id(m) in family))
        self.add(group)
        return group

    # --- animation QA (before playing) ------------------------------------------
    def _check_animations(self, event_id: str, animations):
        """Catch two motion bugs that settled frames never show.

        concurrent_animations: one mobject driven by >1 animation at the same time
          (e.g. several Transform(box, …) in one LaggedStart: every one of them starts
          from the box's *current* position, so the box jumps back each time).
          Chain them with Succession instead.
        regrouped_onscreen: animating a NEW group made of objects already on screen
          re-adds them on top of everything, so objects moving past them slip
          *behind*. Animate the on-screen objects themselves: FadeOut(*parts).
        crossfade_overlap: something appears (FadeIn/Write/Create/Grow…) where something
          else is disappearing (FadeOut/Uncreate…) in the same beat, so the two are drawn
          over each other mid-animation. Clear first, then show (two beats).
        """
        leaves: list[tuple[Animation, tuple]] = []

        def walk(anim, path):
            if isinstance(anim, Succession):
                for k, sub in enumerate(anim.animations):
                    walk(sub, path + ((id(anim), k),))
            elif isinstance(anim, AnimationGroup):
                for sub in anim.animations:
                    walk(sub, path)
            else:
                leaves.append((anim, path))

        for a in animations:
            walk(a, ())

        def concurrent(p, q):  # sequential only if they diverge at the same Succession
            for (sa, ka), (sb, kb) in zip(p, q, strict=False):
                if sa != sb:
                    return True
                if ka != kb:
                    return False
            return True

        for i, (a, pa) in enumerate(leaves):
            for b, pb in leaves[i + 1 :]:
                if a.mobject is b.mobject and concurrent(pa, pb):
                    self._warn(
                        event_id,
                        "concurrent_animations",
                        f"{type(a).__name__} + {type(b).__name__} on {self._describe(a.mobject)}",
                    )

        outgoing = [a.mobject for a, _ in leaves if type(a).__name__ in _OUTGOING]
        incoming = [a.mobject for a, _ in leaves if type(a).__name__ in _INCOMING]
        for m_in in incoming:
            for m_out in outgoing:
                if m_in is not m_out and _overlap_ratio(m_in, m_out) > 0:
                    self._warn(
                        event_id,
                        "crossfade_overlap",
                        f"{self._describe(m_in)} appears over fading {self._describe(m_out)}",
                    )
                    break

        on_screen = {id(m) for top in self.mobjects for m in top.get_family()}
        for a, _ in leaves:
            m = a.mobject
            if m is None or id(m) in on_screen or not m.submobjects:
                continue
            if any(id(sub) in on_screen for sub in m.get_family()[1:]):
                self._warn(
                    event_id,
                    "regrouped_onscreen",
                    f"{type(a).__name__}({type(m).__name__}) re-adds on-screen objects on top",
                )

    # --- layout QA ----------------------------------------------------------
    def _visible_family(self):
        for top in self.mobjects:
            for m in top.get_family():
                if getattr(m, "qa_ignore", False):
                    continue
                if isinstance(m, VMobject) and m.has_points():
                    if max(m.get_fill_opacity(), m.get_stroke_opacity()) > 0.05:
                        yield top, m

    def _check_layout(self, event_id: str):
        half_w = config.frame_width / 2 - style.FRAME_MARGIN * 0.5
        half_h = config.frame_height / 2 - style.FRAME_MARGIN * 0.5
        flagged_out = set()
        texts: list[Mobject] = []
        for top, m in self._visible_family():
            lo, hi = m.get_corner([-1, -1, 0]), m.get_corner([1, 1, 0])
            if (lo[0] < -half_w or hi[0] > half_w or lo[1] < -half_h or hi[1] > half_h) and id(
                top
            ) not in flagged_out:
                flagged_out.add(id(top))
                self._warn(event_id, "out_of_frame", self._describe(top))
        for top in self.mobjects:
            for m in top.get_family():
                if (
                    isinstance(m, (Text, MathTex, Tex, SingleStringMathTex))
                    and not getattr(m, "qa_ignore", False)
                    and m.get_fill_opacity() > 0.05
                ):
                    texts.append(m)
        texts = [t for t in texts if not any(t is not o and t in o.get_family() for o in texts)]
        for i, a in enumerate(texts):
            for b in texts[i + 1 :]:
                ratio = _overlap_ratio(a, b)
                if ratio > 0.02:  # text boxes are tight: any real overlap is a defect
                    self._warn(
                        event_id, "text_overlap", f"{self._describe(a)} x {self._describe(b)} ({ratio:.0%})"
                    )
                elif _overlap_ratio(a, b, pad=MIN_TEXT_GAP / 2) > 0:
                    self._warn(
                        event_id,
                        "text_crowding",
                        f"{self._describe(a)} x {self._describe(b)} (gap < {MIN_TEXT_GAP})",
                    )
        # text that straddles a box outline (partly inside, partly outside)
        boxes = [
            m
            for _, m in self._visible_family()
            if isinstance(m, Rectangle) and m.get_stroke_opacity() > 0.05 and m.get_stroke_width() > 0
        ]
        for t in texts:
            for box in boxes:
                if _overlap_ratio(t, box) > 0 and not _contains(box, t) and not _contains(t, box):
                    self._warn(event_id, "text_crosses_box", f"{self._describe(t)} x {type(box).__name__}")

    @staticmethod
    def _describe(m: Mobject) -> str:
        label = getattr(m, "text", None) or getattr(m, "tex_string", None) or ""
        return f"{type(m).__name__}({label[:30]!r})" if label else type(m).__name__

    def _warn(self, event_id: str, kind: str, detail: str):
        entry = {"event": event_id, "kind": kind, "detail": detail}
        if not any(w["kind"] == kind and w["detail"] == detail for w in self._warnings):
            self._warnings.append(entry)

    # --- output -------------------------------------------------------------
    def tear_down(self):
        if not self._project:
            return
        out = self._project / "renders" / "qa"
        out.mkdir(parents=True, exist_ok=True)
        report = {
            "scene": type(self).__name__,
            "scene_id": self.SCENE_ID or type(self).__name__,
            "duration": round(self.time, 3),
            "events": self._events,
            "warnings": self._warnings,
        }
        (out / f"{type(self).__name__}.events.json").write_text(json.dumps(report, indent=2))


_OUTGOING = {"FadeOut", "Uncreate", "Unwrite", "ShrinkToCenter", "FadeOutAndShift"}
_INCOMING = {
    "FadeIn",
    "Write",
    "Create",
    "DrawBorderThenFill",
    "GrowFromCenter",
    "GrowFromEdge",
    "GrowFromPoint",
    "GrowArrow",
    "SpinInFromNothing",
    "AddTextLetterByLetter",
}

MIN_TEXT_GAP = 0.08  # scene units; closer text reads as one word


def _bounds(m: Mobject, pad: float = 0.0):
    return m.get_corner([-1, -1, 0]) - pad, m.get_corner([1, 1, 0]) + pad


def _contains(outer: Mobject, inner: Mobject, tol: float = 0.02) -> bool:
    (o_lo, o_hi), (i_lo, i_hi) = _bounds(outer), _bounds(inner)
    return bool((i_lo[:2] >= o_lo[:2] - tol).all() and (i_hi[:2] <= o_hi[:2] + tol).all())


def _overlap_ratio(a: Mobject, b: Mobject, pad: float = 0.0) -> float:
    (a_lo, a_hi), (b_lo, b_hi) = _bounds(a, pad), _bounds(b, pad)
    w = min(a_hi[0], b_hi[0]) - max(a_lo[0], b_lo[0])
    h = min(a_hi[1], b_hi[1]) - max(a_lo[1], b_lo[1])
    if w <= 0 or h <= 0:
        return 0.0
    area = lambda lo, hi: max((hi[0] - lo[0]) * (hi[1] - lo[1]), 1e-6)
    return (w * h) / min(area(a_lo, a_hi), area(b_lo, b_hi))
