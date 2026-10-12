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
That file drives frame extraction (myanim review) and is the hook for a
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
    DecimalNumber,
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
from manim.mobject.mobject import _AnimationBuilder

from . import style
from .fonts import check_families

# --- pending `.animate` builders -------------------------------------------------------------
# `mob.animate` writes its target into `mob.target`; the animation is assembled only when
# played. A second `.animate` on the same mobject before the first is played overwrites that
# shared target, so the first animation silently goes to the second destination. We count
# unplayed builders per mobject and report the overlap as `pending_animate`.
_PENDING: dict[int, int] = {}
_PENDING_HITS: list[str] = []
_orig_builder_init = _AnimationBuilder.__init__
_orig_builder_build = _AnimationBuilder.build


def _tracked_init(self, mobject):
    _orig_builder_init(self, mobject)
    key = id(mobject)
    if _PENDING.get(key, 0) > 0:
        _PENDING_HITS.append(type(mobject).__name__)
    _PENDING[key] = _PENDING.get(key, 0) + 1
    self._pending_key = key


def _tracked_build(self):
    key = getattr(self, "_pending_key", None)
    if key is not None and _PENDING.get(key, 0) > 0:
        _PENDING[key] -= 1
        self._pending_key = None
    return _orig_builder_build(self)


_AnimationBuilder.__init__ = _tracked_init
_AnimationBuilder.build = _tracked_build


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
    WRITE_REPORT: bool = True  # False for QA dry runs (`myanim check`): keep the render's event log

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
        if _PENDING_HITS:
            self._warn(
                event_id,
                "pending_animate",
                f".animate created again on a {_PENDING_HITS[0]} before its previous .animate was "
                f"played (shared mob.target: the earlier move goes to the later target). "
                f"Use Transform(mob, mob.copy()...) for moves built up front.",
            )
            _PENDING_HITS.clear()
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
        stale_start: ≥ 2 ChangeDecimalToValue on one number in a beat; each reads its start
          value at construction, so chained steps restart from the old value. Use count_to().
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

        # Morphing one piece of prose into a different one scrambles glyph outlines.
        for a, _ in leaves:
            tgt = getattr(a, "target_mobject", None)
            if tgt is None or type(a).__name__ not in ("Transform", "ReplacementTransform"):
                continue
            src_txt, tgt_txt = _first_text(a.mobject), _first_text(tgt)
            if src_txt and tgt_txt and src_txt != tgt_txt and (_has_words(src_txt) or _has_words(tgt_txt)):
                self._warn(
                    event_id,
                    "text_morph",
                    f"Transform {src_txt[:20]!r} -> {tgt_txt[:20]!r}: crossfade words instead "
                    f"(FadeOut old, FadeIn new); morphing is fine for numbers",
                )

        decimal_steps = [a.mobject for a, _ in leaves if type(a).__name__ == "ChangeDecimalToValue"]
        for mob in {id(m): m for m in decimal_steps}.values():
            if sum(m is mob for m in decimal_steps) > 1:
                self._warn(
                    event_id,
                    "stale_start",
                    f"{sum(m is mob for m in decimal_steps)}x ChangeDecimalToValue on one number",
                )

        outgoing = [(a.mobject, p) for a, p in leaves if type(a).__name__ in _OUTGOING]
        incoming = [(a.mobject, p) for a, p in leaves if type(a).__name__ in _INCOMING]
        for m_in, p_in in incoming:
            for m_out, p_out in outgoing:
                if m_in is not m_out and concurrent(p_in, p_out) and _overlap_ratio(m_in, m_out) > 0:
                    self._warn(
                        event_id,
                        "crossfade_overlap",
                        f"{self._describe(m_in)} appears over fading {self._describe(m_out)}",
                    )
                    break

        # Movers: animations that move/morph an object (not pure fades/creates).
        movers = [
            a for a, _ in leaves if type(a).__name__ not in _OUTGOING | _INCOMING and a.mobject is not None
        ]

        def swept(a):  # bounding regions the mover occupies: start and (if known) end state
            regions = [a.mobject]
            target = getattr(a, "target_mobject", None) or getattr(a.mobject, "target", None)
            return regions + ([target] if target is not None else [])

        on_screen = {id(m) for top in self.mobjects for m in top.get_family()}
        for a, _ in leaves:
            m = a.mobject
            if m is None or id(m) in on_screen or not m.submobjects:
                continue
            if not any(id(sub) in on_screen for sub in m.get_family()[1:]):
                continue
            # Re-adding only matters if something moves across the regrouped objects.
            family = {id(x) for x in m.get_family()}
            crossing = [
                mv
                for mv in movers
                if id(mv.mobject) not in family and any(_overlap_ratio(r, m) > 0 for r in swept(mv))
            ]
            if crossing:
                self._warn(
                    event_id,
                    "regrouped_onscreen",
                    f"{type(a).__name__}({self._describe(m)}) re-adds on-screen objects on top of "
                    f"moving {self._describe(crossing[0].mobject)}",
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
        raw: list[Mobject] = []
        seen_ids: set[int] = set()  # Manim can list one mobject twice at top level
        for top in self.mobjects:
            for m in top.get_family():
                if id(m) in seen_ids:
                    continue
                seen_ids.add(id(m))
                if (
                    (
                        getattr(m, "text_unit", False)
                        or isinstance(m, (Text, MathTex, Tex, SingleStringMathTex, DecimalNumber))
                    )
                    and not getattr(m, "qa_ignore", False)
                    and _visible_opacity(m) > 0.05
                ):
                    raw.append(m)
        for t in raw:  # a lone Latin letter in prose is a symbol: it belongs in math mode
            is_code = style.MONO_FONT.split(",")[0] in str(getattr(t, "font", ""))  # code may say N, x...
            if isinstance(t, Text) and not is_code and _LONE_LETTER.search(getattr(t, "text", "")):
                self._warn(
                    event_id,
                    "symbol_in_text",
                    f"{self._describe(t)}: lone letter in body text; use $...$ (mixed/caption) or math_label",
                )
        # one unit per text: a mixed() line or a formula is checked as a whole, not piece by piece
        texts = [t for t in raw if not any(t is not o and t in o.get_family() for o in raw)]
        for i, a in enumerate(texts):
            for b in texts[i + 1 :]:
                if _overlap_ratio(a, b, pad=MIN_TEXT_GAP / 2) == 0:
                    continue
                # bounding boxes are coarse (a fraction makes a formula tall): decide on glyphs
                ga, gb = _glyphs(a), _glyphs(b)
                worst = max((_overlap_ratio(x, y) for x in ga for y in gb), default=0.0)
                if worst > 0.02:  # glyph boxes are tight: any real overlap is a defect
                    self._warn(
                        event_id, "text_overlap", f"{self._describe(a)} x {self._describe(b)} ({worst:.0%})"
                    )
                elif any(_overlap_ratio(x, y, pad=MIN_TEXT_GAP / 2) > 0 for x in ga for y in gb):
                    self._warn(
                        event_id,
                        "text_crowding",
                        f"{self._describe(a)} x {self._describe(b)} (gap < {MIN_TEXT_GAP})",
                    )
        # text that straddles a box outline: some glyph is partly inside, partly outside
        # (a box drawn around part of a formula is fine: its glyphs are fully in or fully out)
        boxes = [
            m
            for _, m in self._visible_family()
            if isinstance(m, Rectangle) and m.get_stroke_opacity() > 0.05 and m.get_stroke_width() > 0
        ]
        for t in texts:
            for box in boxes:
                if _overlap_ratio(t, box) == 0 or _contains(t, box):
                    continue
                if any(_overlap_ratio(x, box) > 0 and not _contains(box, x) for x in _glyphs(t)):
                    self._warn(event_id, "text_crosses_box", f"{self._describe(t)} x {type(box).__name__}")

    @staticmethod
    def _describe(m: Mobject) -> str:
        """Type plus the first text found in the family, so groups are identifiable."""
        for sub in m.get_family():
            label = getattr(sub, "text", None) or getattr(sub, "tex_string", None)
            if label:
                return f"{type(m).__name__}({label[:30]!r})"
        return type(m).__name__

    def _warn(self, event_id: str, kind: str, detail: str):
        entry = {"event": event_id, "kind": kind, "detail": detail}
        if not any(w["kind"] == kind and w["detail"] == detail for w in self._warnings):
            self._warnings.append(entry)

    # --- output -------------------------------------------------------------
    def tear_down(self):
        if not self._project or not self.WRITE_REPORT:
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


def _glyphs(m) -> list:
    """Drawn leaves of a text-like mobject (one per glyph / stroke piece)."""
    return [x for x in m.family_members_with_points() if _visible_opacity(x) > 0.05]


def _visible_opacity(m) -> float:
    """Opacity of what is actually drawn: MathTex/VGroup parents report 0, their glyphs don't."""
    leaves = m.family_members_with_points()
    return max((max(x.get_fill_opacity(), x.get_stroke_opacity()) for x in leaves), default=0.0)


def _first_text(m) -> str | None:
    for sub in m.get_family():
        t = getattr(sub, "text", None) or getattr(sub, "tex_string", None)
        if t:
            return t
    return None


def _has_words(s: str) -> bool:
    """Letters or CJK, i.e. not just digits/signs (numbers may morph)."""
    return any(ch.isalpha() for ch in s)


_LONE_LETTER = __import__("re").compile(r"(?<![A-Za-z])(?![aAI](?![A-Za-z]))[A-Za-z](?![A-Za-z])")

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
