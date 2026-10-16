<!-- made by tools/make_readmes.py - edit that script, not this file -->
# art/

Original art for SkyWynn (made by code or by the art agent) - icons, sheets, textures we own.

## Where things are
- `art/<family>/` = one folder per art family: `README.md` (status DRAFT / APPROVED + Skyy's words), `manifest.json`, the PNGs and a `sheet.png` for review.
- Generators live in `tools/art/make_<family>.py` (deterministic). Art rules Skyy approved: `.claude/skills/skywynn-art/SKILL.md`.
- Never commit vanilla-derived pixels or other people's art (references go in `research/refs/`, git-ignored).

## Where new things go
- New art family: `art/<family>/` + `tools/art/make_<family>.py`; add a line to `ART-RESUME.md`.
- Skyy's art reviews: `docs/answered/<topic>.md` (gear / pets / world / ui).

Map of the whole repo: `INDEX.md`. Rules: `PROJECT-RULES.md`.
