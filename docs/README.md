<!-- made by tools/make_readmes.py - edit that script, not this file -->
# docs/

The project's records: answers, the log, tests, plans, old snapshots.

## Where things are
- `docs/answered/<topic>.md` = every answer Skyy gave, word for word, by topic (`README.md` there lists the topics).
- `docs/log/<YYYY-MM>.md` = one line per build / deploy / test result / decision (append only).
- `docs/tests/` = every in-game test section (`TEST-CHECKLIST.md` at the root = what to test next).
- `docs/plans/`, `docs/handoff/`, `docs/rounds/`, `docs/archive/` = plans, old HANDOFF parts, round briefs, snapshots.

## Where new things go
- Skyy answers a question: `python tools/qa_append.py <topic> <file> --close "<words>"` (writes docs/answered + removes it from `OPEN-QUESTIONS.md`).
- Anything finished: a line in `docs/log/<month>.md`, then `RESUME.md` Now / Next; a deploy: `python tools/record_deploy.py ...`.

Map of the whole repo: `INDEX.md`. Rules: `PROJECT-RULES.md`.
