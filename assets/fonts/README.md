# Fonts

Font files are **downloaded, not stored in git**. `fonts.toml` pins every file to an
upstream release/tag with a sha256 checksum; `myanim fonts` fetches and verifies them.
`components/fonts.py` registers whatever is here with Pango at import time, so renders do
not depend on system-installed fonts.

```bash
myanim fonts sync      # after cloning: core fonts + CJK regions used by any project
myanim fonts list      # status
myanim fonts verify    # re-check checksums
```
If fonts are missing, importing `components` fails with the exact command to run.

| family | files | role | upstream (pinned) | license |
|---|---|---|---|---|
| Libertinus Serif | Regular, Italic, Semibold, SemiboldItalic, Bold, BoldItalic | all normal text | `alerque/libertinus` release v7.051 (zip) | OFL 1.1, `OFL-Libertinus.txt` |
| IBM Plex Mono | Regular, Italic, SemiBold, Bold | code / monospace | `IBM/plex` tag `@ibm/plex-mono@2.5.0` | OFL 1.1, `OFL-IBMPlexMono.txt` |
| Noto Serif CJK | Regular, SemiBold per region (~24 MB each) | CJK fallback in both tokens | `notofonts/noto-cjk` tag `Serif2.003` | OFL 1.1, `OFL-NotoSerifCJK.txt` |

## CJK regions
Default glyph forms: Simplified Chinese (SC). A project selects another region in its
`project.toml`; `sync` then fetches it automatically (or `add-cjk JP` explicitly):
```toml
[style]
cjk = "JP"        # SC | TC | HK | JP | KR
```
Changing `cjk` re-renders all of that project's scenes.
Known gap: with SC, Hangul does not render in semibold; Korean projects should use `cjk = "KR"`.

## Changing or upgrading a font
Edit the entries in `fonts.toml` (URL + sha256; `sha256sum` of the final .otf), run
`sync`, re-render, and review the contact sheets: metric changes shift layouts.
Font tokens live in `components/style.py`.
