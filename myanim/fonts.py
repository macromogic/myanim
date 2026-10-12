"""Download the project's fonts into assets/fonts/ from pinned upstream sources.

Font files are not kept in git. `assets/fonts/fonts.toml` pins every file to an upstream
release/tag plus a sha256; this script fetches and verifies them.

    myanim fonts sync          # core fonts + every CJK region any project uses
    myanim fonts sync --cjk JP # ... plus JP
    myanim fonts add-cjk KR    # just one region
    myanim fonts list          # what is installed / needed
    myanim fonts verify        # re-check sha256 of installed files

Select a project's CJK region in its project.toml:
    [style]
    cjk = "JP"        # SC (default) | TC | HK | JP | KR
"""

from __future__ import annotations

import argparse
import hashlib
import io
import sys
import tomllib
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"
MANIFEST = FONT_DIR / "fonts.toml"
DEFAULT_CJK = "SC"  # keep in sync with components/style.py DEFAULT_CJK_REGION


def load_manifest() -> list[dict]:
    with open(MANIFEST, "rb") as f:
        return tomllib.load(f)["font"]


def regions() -> list[str]:
    return sorted({e["group"][4:] for e in load_manifest() if e["group"].startswith("cjk-")})


def used_regions() -> set[str]:
    """CJK regions selected by any project (plus the default)."""
    used = {DEFAULT_CJK}
    for cfg in (ROOT / "projects").glob("*/project.toml"):
        with open(cfg, "rb") as f:
            used.add(tomllib.load(f).get("style", {}).get("cjk", DEFAULT_CJK))
    return used


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "myanim-fonts"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def install(groups: set[str]) -> None:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    archives: dict[str, zipfile.ZipFile] = {}
    todo = [e for e in load_manifest() if e["group"] in groups]
    for e in todo:
        dest = FONT_DIR / e["file"]
        if dest.exists() and sha256(dest) == e["sha256"]:
            print(f"= {e['file']}")
            continue
        print(f"> {e['file']}", flush=True)
        if "member" in e:
            if e["url"] not in archives:
                archives[e["url"]] = zipfile.ZipFile(io.BytesIO(_get(e["url"])))
            data = archives[e["url"]].read(e["member"])
        else:
            data = _get(e["url"])
        digest = hashlib.sha256(data).hexdigest()
        if digest != e["sha256"]:
            sys.exit(
                f"!! checksum mismatch for {e['file']} from {e['url']}\n"
                f"   expected {e['sha256']}\n   got      {digest}"
            )
        tmp = dest.with_suffix(".part")
        tmp.write_bytes(data)
        tmp.rename(dest)
        print(f"  {len(data) / 1048576:.1f} MB ok")


def cmd_sync(args):
    wanted = used_regions() | {r.strip().upper() for r in (args.cjk or "").split(",") if r.strip()}
    if bad := wanted - set(regions()):
        sys.exit(f"unknown CJK regions {sorted(bad)}; choose from {regions()}")
    install({"core"} | {f"cjk-{r}" for r in wanted})
    print(f"fonts ready (CJK regions: {', '.join(sorted(wanted))})")


def cmd_add(args):
    region = args.region.upper()
    if region not in regions():
        sys.exit(f"unknown CJK region {region!r}; choose from {regions()}")
    install({f"cjk-{region}"})
    print(f'done. Use it in a project with:  [style]  cjk = "{region}"  (project.toml)')


def cmd_list(_):
    used = used_regions()
    for group in ["core"] + [f"cjk-{r}" for r in regions()]:
        entries = [e for e in load_manifest() if e["group"] == group]
        have = sum((FONT_DIR / e["file"]).exists() for e in entries)
        note = " (used by a project)" if group[4:] in used else ""
        print(f"{group:8s} {have}/{len(entries)} installed{note}")


def cmd_verify(_):
    bad = 0
    for e in load_manifest():
        p = FONT_DIR / e["file"]
        if p.exists() and sha256(p) != e["sha256"]:
            print(f"!! {e['file']}: checksum mismatch")
            bad += 1
    print("all installed fonts verified" if not bad else f"{bad} file(s) differ; run sync")
    sys.exit(1 if bad else 0)


def main(argv: list[str] | None = None):
    ap = argparse.ArgumentParser(
        prog="myanim fonts", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync")
    s.add_argument("--cjk", help="extra CJK regions, comma-separated")
    s.set_defaults(fn=cmd_sync)
    a = sub.add_parser("add-cjk")
    a.add_argument("region")
    a.set_defaults(fn=cmd_add)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
