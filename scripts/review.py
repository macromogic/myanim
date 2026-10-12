"""Inspect rendered scenes: event frames, contact sheets, pacing and layout report.

    uv run python scripts/review.py projects/attention-demo            # all scenes, preview quality
    uv run python scripts/review.py projects/attention-demo -s s02_softmax -q draft

For each scene it writes to <project>/renders/review/:
  <scene_id>/NN_<event>.png   frame right after each beat's animation settles
  <scene_id>_sheet.png        contact sheet of those frames (open this to look)
  <scene_id>_motion.png       mid-animation frames (25/50/75 %) of each beat: jumps,
                              objects passing behind others, overlaps while moving
  report.md                   durations vs. targets, long static holds, layout warnings

Read the contact sheets: a successful render is not a successful explanation.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render import load_project  # noqa: E402

FREEZE_MIN = 3.0  # seconds of no visual change worth flagging


def probe_duration(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        capture_output=True,
        text=True,
    )
    return float(out.stdout.strip() or 0)


def grab(video: Path, t: float, out: Path):
    # Seeking past the last frame's timestamp (e.g. 21.68 s when the last 15 fps frame is at
    # 21.667 s) makes ffmpeg write nothing and still exit 0, so back off and retry.
    out.unlink(missing_ok=True)
    for back in (0.0, 0.1, 0.25, 0.5):
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-ss",
                f"{max(t - back, 0):.3f}",
                "-i",
                str(video),
                "-frames:v",
                "1",
                str(out),
            ],
            check=True,
        )
        if out.exists():
            return
    raise RuntimeError(f"could not extract a frame at {t:.2f}s from {video}")


def freezes(video: Path) -> list[tuple[float, float]]:
    proc = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(video),
            "-vf",
            f"freezedetect=n=0.0003:d={FREEZE_MIN}",
            "-map",
            "0:v",
            "-f",
            "null",
            "-",
        ],
        capture_output=True,
        text=True,
    )
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", proc.stderr)]
    ends += [probe_duration(video)] * (len(starts) - len(ends))
    return list(zip(starts, ends, strict=True))


def contact_sheet(frames: list[tuple[str, Path]], out: Path, cols: int = 3, thumb_w: int = 560):
    if not frames:
        return
    imgs = [Image.open(p) for _, p in frames]
    ratio = imgs[0].height / imgs[0].width
    th = int(thumb_w * ratio)
    label_h = 28
    rows = (len(imgs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (th + label_h)), (40, 40, 40))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for k, ((name, _), img) in enumerate(zip(frames, imgs, strict=True)):
        x, y = (k % cols) * thumb_w, (k // cols) * (th + label_h)
        sheet.paste(img.resize((thumb_w, th)), (x, y + label_h))
        draw.text((x + 6, y + 4), f"{k:02d} {name}", fill=(235, 235, 235), font=font)
    sheet.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path)
    ap.add_argument("-s", "--scenes")
    ap.add_argument("-q", "--quality", default="preview")
    args = ap.parse_args()

    project = args.project.resolve()
    cfg = load_project(project)
    wanted = set(args.scenes.split(",")) if args.scenes else None
    review = project / "renders" / "review"
    review.mkdir(parents=True, exist_ok=True)
    lines = [f"# Review: {cfg['project'].get('title', project.name)} ({args.quality})", ""]
    total = 0.0
    for scene in cfg["scenes"]:
        if wanted and scene["id"] not in wanted:
            continue
        video = project / "renders" / args.quality / f"{scene['id']}.mp4"
        events_file = project / "renders" / "qa" / f"{scene['class']}.events.json"
        if not video.exists():
            lines += [f"## {scene['id']}: NOT RENDERED", ""]
            continue
        dur = probe_duration(video)
        total += dur
        events = (
            json.loads(events_file.read_text()) if events_file.exists() else {"events": [], "warnings": []}
        )
        target = scene.get("target_seconds")
        lines.append(f"## {scene['id']} — {dur:.1f}s" + (f" (target {target}s)" if target else ""))

        frame_dir = review / scene["id"]
        frame_dir.mkdir(exist_ok=True)
        for old in frame_dir.glob("*.png"):
            old.unlink()
        frames = []
        for k, ev in enumerate(events["events"]):
            t = min(ev["anim_end"] + 0.1, max(ev["end"] - 0.05, ev["anim_end"]), dur - 0.05)
            p = frame_dir / f"{k:02d}_{ev['id']}.png"
            grab(video, t, p)
            frames.append((ev["id"], p))
        if not frames:  # no event log: fall back to evenly spaced frames
            for k in range(6):
                p = frame_dir / f"{k:02d}_t{k}.png"
                grab(video, dur * (k + 0.5) / 6, p)
                frames.append((f"t={dur * (k + 0.5) / 6:.1f}s", p))
        sheet = review / f"{scene['id']}_sheet.png"
        contact_sheet(frames, sheet)
        lines.append(f"- contact sheet: `{sheet.relative_to(project)}` ({len(frames)} frames)")

        motion = []
        for k, ev in enumerate(events["events"]):
            span = ev["anim_end"] - ev["start"]
            if span < 0.4:
                continue
            for frac in (0.25, 0.5, 0.75):
                p = frame_dir / f"m{k:02d}_{ev['id']}_{int(frac * 100)}.png"
                grab(video, ev["start"] + frac * span, p)
                motion.append((f"{ev['id']} {int(frac * 100)}%", p))
        if motion:
            msheet = review / f"{scene['id']}_motion.png"
            contact_sheet(motion, msheet, cols=3, thumb_w=420)
            lines.append(f"- motion sheet: `{msheet.relative_to(project)}` ({len(motion)} frames)")

        for a, b in freezes(video):
            ev = next((e["id"] for e in events["events"] if e["start"] <= a + 0.05 <= e["end"]), "?")
            lines.append(f"- static hold {b - a:.1f}s at {a:.1f}s (during `{ev}`): check it is intended")
        for w in events["warnings"]:
            lines.append(f"- LAYOUT {w['kind']} after `{w['event']}`: {w['detail']}")
        lines.append("")
    lines.insert(1, f"Total duration: {total:.1f}s")
    report = review / "report.md"
    report.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nreport -> {report.relative_to(project)}")


if __name__ == "__main__":
    main()
