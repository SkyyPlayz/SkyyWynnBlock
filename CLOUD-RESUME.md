# CLOUD-RESUME - rolling to-do for cloud sessions

Work a cloud session can do while the local session waits (usage limits, Skyy away). Started 2026-10-02.

## How this file works (read every time)

- **Rolling list:** do the top open task, then mark it `[x]` with the date and the output file. When you open this file and see `[x]`
  items, first add one line per item to `research/cloud/LOG.md`, then DELETE those items here and top the list back up to about 8
  open tasks (ideas: RESUME.md 'Next', OPEN-QUESTIONS.md (open only), the plans in `research/` + `docs/plans/`). Keep this file under ~110 lines.
- **Cloud limits:** no access to Skyy's PC, the Hytale game files (`HytaleServer.jar`, `Assets.zip`), installed mods or the test world.
  You cannot build, test or deploy. Skyy 2026-10-19: "grokbot wont be working on the project. every resume list is yours for now." - this list is Claude's (local + cloud). Otherwise only add tasks that need none of that. Any fact you cannot check without the game files: mark it
  **UNVERIFIED** and list it under "For the local session" in your output.
- **Where results go:** new files in `research/cloud/` (one file per task). You may push straight to `main` ONLY changes to this file and
  to `research/cloud/` (always `git pull --rebase --autostash` first). Any change to another file goes through a pull request.
- **Never touch:** build / patch scripts, `tools/deploy_set.py`, jars, `SkyyGear-Plan.md`, `SkyyGear-Stat-Catalog.md`.
- **Reminder (local session 2026-10-06):** commit 1cc3116 edited `research/Booster-Accessories-Spec.md` straight on main - accepted
  this once, but files OUTSIDE `research/cloud/` and this file always go through a pull request.
- **Before every push (local session 2026-10-06):** run `python tools/docs_check.py` - it must print OK (needs only git + Python).
  Write file mentions as FULL repo paths (e.g. `research/classes/Monk.md`, never the bare file name); a planned output of a task named here is fine.
- **Every draft:** start with the decisions it follows (docs/answered/<topic>.md lines), end with "Questions for Skyy" (each with a
  recommended default) and "For the local session" (every UNVERIFIED item needing Assets.zip / HytaleServer.jar). Don't re-decide LOCKED lines.
- **Agents (Skyy 2026-10-06):** you may use sub agents - for research fan-outs AND for programming (drafting code in PRs). Always pick the
  right agent + effort for the job, as good as possible without wasting tokens: Haiku for tiny lookups, Sonnet for research / reviews /
  straightforward drafts, Opus for code and hard specs, Fable only where it is clearly necessary (hardest spec synthesis / engine design).
  Name the model per agent. Code you write cannot be compiled or tested here (no HytaleServer.jar) - mark it UNTESTED in the PR.
- **OpenRouter / Jev for cheap side jobs (Skyy 2026-10-13: "make sure the cloud agent knows they can use JEV too, and the rules on using
  jev"):** `python tools/llm.py "question" --file F ...` (research/OpenRouter-Jev-Plan.md). Rules:
  - Use it for BULK reading / sorting / first drafts (mod lists, long docs, surveys, summaries) to save Claude tokens; Claude still
    checks the answer - a model's output is a lead or a draft, never a fact or a commit.
  - Models: Jev (`typesafe/jev-router`) by default. Since 2026-10-19 every call is ZDR with no training (llm.py sends
    provider zdr + data_collection deny); free models are refused (no ZDR endpoints). Skyy's budget is $20 / month (7 requests so far cost $0.01). Never pick another paid model without asking Skyy.
  - The key is NEVER in the repo, chat, a log or output, and never printed. llm.py reads Windows Credential Manager locally, else the
    environment variable OPENROUTER_API_KEY. If the cloud environment has no OPENROUTER_API_KEY, skip OpenRouter (do the job yourself)
    and note "OpenRouter key not set in the cloud environment" in OUTBOX for Skyy.
  - Keep redaction ON (no `--no-redact`): no personal data, chat, player names or emails go out; redaction stays on even with ZDR.
    Never send game files or other authors' files (llm.py refuses Assets.zip / HytaleServer.jar).
- **Art:** before drawing ANY concept sheet or icon, read `.claude/skills/skywynn-art/SKILL.md` (Skyy's art rules, 2026-10-06).
- Follow `PROJECT-RULES.md`. Skyy uses they/them. Plain English, tables, short.

- **Answering the local session (2026-10-07):** messages from the local session arrive by SendMessage; reply by appending a
  "## <date time> <title>" block to `research/cloud/OUTBOX.md` and pushing to main (the local cloud-link mod picks it up in ~3 min).

## Cloud build trial - ENDED

The trial ended (Skyy 2026-10-19: "grokbot wont be working on the project. every resume list is yours for now."); builds run locally (plain Agent builders or the saved workflow `skywynn-round`, PROJECT-RULES section 4). History: docs/answered/project.md 2026-10-17 lines.

## Open tasks (top = next)

<!-- 2026-10-24 local session: the 10-23 list (8 specs) is DONE + logged in research/cloud/LOG.md; older comment history trimmed (git history).
New list from RESUME.md 'Next'. Each = no-game-file draft in research/cloud/, decisions followed first, end with 'Questions for Skyy' (defaults) + 'For the local session'. -->
- [ ] Starter archipelago R4 quests build sheet (SkyyQuests 0.4.4 `archipelago` line: steps, texts, rewards, Ranching walkthrough) -> `research/cloud/Archipelago-Quests-R4.md` from research/Starter-Archipelago-Spec.md sections 11-12.
- [ ] Starter archipelago R5 combat shard islands (one island per zone, mob pools, always night, upper + deep-cavern halves, upgrade rows) -> `research/cloud/Combat-Shard-Islands-R5.md` from research/Starter-Archipelago-Spec.md section 10.
- [ ] Ranching XP R6 (eggs / wool / milk / taming XP numbers vs research/balance) -> `research/cloud/Ranching-XP-R6.md`.
- [ ] Weaponcraft x1.5 balance notes (which Gear / Mobs / Pets / Accessories numbers move, before / after table) -> `research/cloud/Weaponcraft-x1.5-Notes.md`.
- [ ] Beastmastery tree nodes (hatch speed + hatchery slots: node ids, costs, Trees + Pets bridge keys) -> `research/cloud/Beastmastery-Nodes.md`.
- [ ] sig3 / sig5 build sheet (UT quirks + Mythic signatures that REPLACE vanilla moves) -> `research/cloud/Sig3-Sig5-Build.md` from research/UT-Mythic-Signatures.md.
- [ ] Spellblade great shield spec (bash attack + 30-block steerable charge) -> `research/cloud/Spellblade-Great-Shield.md`.
- [ ] Price tooltips R1 Auctions / R2 Bazaar build notes (after the R0 probe) -> `research/cloud/Price-Tooltips-R1-R2.md` from research/Price-Tooltips-Spec.md.

## Done (delete after logging - see the rules above)
(none)

## For the local builder (2026-10-16)
- Skyy answered many OPEN-QUESTIONS.md items on 2026-10-15 (see research/cloud/OpenQuestions-Answers-2026-10-15.md). Builder: fold these into OPEN-QUESTIONS.md / docs/answered. Items still open for builder + Skyy: L86/L87, L94, L106, L108, L31.
