"""Render a project's scenes, skipping unchanged ones, then concatenate.

    myanim render projects/attention-demo                 # preview (480p15)
    myanim render projects/attention-demo -s s02_softmax  # one scene
    myanim render projects/attention-demo -q final        # 1080p60
    myanim render projects/attention-demo --still         # last frames only

Outputs: <project>/renders/<quality>/<scene_id>.mp4 and full.mp4.
A scene is re-rendered only if its file, the project's shared .py files,
timing.toml or components/ changed since the last successful render (use --force
to override). Errors print a trimmed traceback and stop the run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUALITY = {"preview": "l", "draft": "m", "final": "h", "4k": "k"}


def load_project(project: Path) -> dict:
    with open(project / "project.toml", "rb") as f:
        return tomllib.load(f)


def scene_hash(project: Path, scene: dict) -> str:
    h = hashlib.sha256()
    timing = project / "timing.toml"
    if timing.exists():  # only this scene's section: retiming one scene re-renders one scene
        with open(timing, "rb") as f:
            h.update(json.dumps(tomllib.load(f).get(scene["id"], {}), sort_keys=True).encode())
    with open(project / "project.toml", "rb") as f:  # [style] (e.g. cjk region) affects every scene
        h.update(json.dumps(tomllib.load(f).get("style", {}), sort_keys=True).encode())
    files = [project / scene["file"]]
    files += sorted(p for p in project.glob("*.py"))  # shared project code
    files += sorted((ROOT / "components").glob("*.py"))
    for p in files:
        if p.exists():
            h.update(p.name.encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def manim_env(project: Path) -> dict:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT), str(project), env.get("PYTHONPATH", "")])
    env["PYTHONWARNINGS"] = "ignore::SyntaxWarning"  # pydub noise on 3.12+
    env["COLUMNS"] = "160"  # keep Rich tracebacks readable
    return env


def render_scene(project: Path, scene: dict, quality: str, still: bool) -> Path | None:
    media = project / "renders" / "media"
    cmd = [
        sys.executable,
        "-m",
        "manim",
        f"-q{QUALITY[quality]}",
        "--media_dir",
        str(media),
        "--progress_bar",
        "none",
    ]
    if still:
        cmd += ["-s"]
    cmd += [str(project / scene["file"]), scene["class"]]
    print(f"  $ manim -q{QUALITY[quality]} {scene['file']} {scene['class']}", flush=True)
    proc = subprocess.run(cmd, cwd=project, env=manim_env(project), capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"\n!! {scene['id']} FAILED (exit {proc.returncode})")
        lines = [l for l in proc.stderr.splitlines() if l.strip(" │")]
        print("\n".join(lines[-40:]) or proc.stdout[-3000:])
        return None
    stem = Path(scene["file"]).stem
    pattern = f"images/{stem}/{scene['class']}*.png" if still else f"videos/{stem}/*/{scene['class']}.mp4"
    found = sorted(media.glob(pattern), key=lambda p: p.stat().st_mtime)
    return found[-1] if found else None


def concat(videos: list[Path], out: Path):
    listing = out.with_suffix(".txt")
    listing.write_text("".join(f"file '{v.resolve()}'\n" for v in videos))
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(listing),
            "-c",
            "copy",
            str(out),
        ],
        check=True,
    )
    listing.unlink()


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="myanim render", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("project", type=Path)
    ap.add_argument("-s", "--scenes", help="comma-separated scene ids (default: all)")
    ap.add_argument("-q", "--quality", choices=QUALITY, default="preview")
    ap.add_argument("--force", action="store_true", help="ignore the unchanged-scene cache")
    ap.add_argument("--still", action="store_true", help="render last frame PNG only")
    ap.add_argument("--no-concat", action="store_true")
    args = ap.parse_args(argv)

    project = args.project.resolve()
    cfg = load_project(project)
    scenes = cfg["scenes"]
    wanted = set(args.scenes.split(",")) if args.scenes else None
    if wanted and (unknown := wanted - {s["id"] for s in scenes}):
        sys.exit(f"unknown scene ids: {sorted(unknown)}")

    out_dir = project / "renders" / ("stills" if args.still else args.quality)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    ok = True
    for scene in scenes:
        if wanted and scene["id"] not in wanted:
            continue
        digest = scene_hash(project, scene)
        target = out_dir / (scene["id"] + (".png" if args.still else ".mp4"))
        if not args.force and manifest.get(scene["id"]) == digest and target.exists():
            print(f"= {scene['id']}: unchanged, skipped")
            continue
        print(f"> {scene['id']} [{scene.get('status', 'draft')}]")
        result = render_scene(project, scene, args.quality, args.still)
        if result is None:
            ok = False
            manifest.pop(scene["id"], None)
            break
        shutil.copy2(result, target)
        manifest[scene["id"]] = digest
        print(f"  -> {target.relative_to(project)}")
    manifest_path.write_text(json.dumps(manifest, indent=2))

    if not ok:
        sys.exit(1)
    if not args.still and not args.no_concat:
        videos = [out_dir / f"{s['id']}.mp4" for s in scenes]
        if all(v.exists() for v in videos):
            concat(videos, out_dir / "full.mp4")
            print(f"full video -> {(out_dir / 'full.mp4').relative_to(project)}")
        else:
            print("full.mp4 not built: some scenes have not been rendered at this quality yet")
    qa = project / "renders" / "qa"
    for s in scenes:
        f = qa / f"{s['class']}.events.json"
        if f.exists():
            rep = json.loads(f.read_text())
            warn = f", {len(rep['warnings'])} layout warnings" if rep["warnings"] else ""
            print(f"  {s['id']}: {rep['duration']:.1f}s, {len(rep['events'])} events{warn}")


if __name__ == "__main__":
    main()
