<!-- made by tools/make_readmes.py - edit that script, not this file -->
# research/

Specs, plans, surveys and Skyy's ideas - paper design, nothing here is code.

## Where things are
- `research/<Feature>-Spec.md` = a buildable spec (decisions it follows, numbers, build rounds, questions with defaults).
- `research/classes/<Class>.md` = one file per class (+ `README.md`); `research/cloud/` = cloud sessions' drafts + `research/cloud/LOG.md` / `research/cloud/OUTBOX.md`.
- Search: `grep -l "<word>" research/*.md`; the index of every big file is `INDEX.md`.

## Where new things go
- A new spec: `research/<Feature>-Spec.md`, and add it to the `research/` row in `INDEX.md`.
- Skyy's ideas go here too (even 'just ideas'); their ANSWERS go to `docs/answered/<topic>.md`, open questions to `OPEN-QUESTIONS.md`.
- Never edit `SkyyGear-Plan.md` / `SkyyGear-Stat-Catalog.md` (Skyy's own design docs).

Map of the whole repo: `INDEX.md`. Rules: `PROJECT-RULES.md`.
