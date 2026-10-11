# OpenRouter + Jev: speeding up SkyWynn and saving Claude tokens

Skyy 2026-10-11: "research how we could use JEV and other open router models to speed up our system, and improve token use efficiency.
(and just general ways to use jev that could help us.)"

Researched from OpenRouter's model list and API, the Jev Router page, and TypeSafe's "System One" docs. It cost almost no Claude
usage (curl + reading).

## What we have

- **Key:** in Windows Credential Manager, used by `tools/llm.py`.
  - Spend caps: $10 a month on the key, $50 a month on the workspace. Spent so far: about $0.
  - Not a free-tier account, so we get **1000 free-model requests a day** (`GET /api/v1/key` -> `free_model_daily_requests`).
- **Free models** (19 of them, up to 1M context). `tools/llm.py` tries these first:
  - nemotron-3-ultra :free, then inkling :free, then gemma-4-31b :free, then openrouter/free.
  - If they all fail, it falls back to the paid Jev router.
- **Jev Router** (`typesafe/jev-router`):
  - Picks a model and a reasoning effort for each request.
  - Billed at whatever model it picks.
  - Supports tools, `response_format` and structured outputs.
- **Jev itself** (`typesafe/jev-latest`, Jev 1.13) is NOT a chat model. It is a "System One" decision model:
  - You give it some state plus a question type, and it returns a typed answer with a calibrated probability.
  - Question types: **Choice** (pick one of N), **Score** (a number on a scale), **Noul** (true / false probability).
  - It handles text only and writes no prose or code. It is fast and cheap, and it is made for routing, classifying and gating.
- **Other routers:**
  - `openrouter/fusion`: a panel of models with web search and web fetch, merged into one answer.
  - `openrouter/pareto-code`: strong coding models, filtered by a minimum coding score.
  - `openrouter/auto`.

## Where our Claude tokens go (from the usage notes)

| Job | Claude cost |
|---|---|
| Full round (build, review, fix, cross-check) | ~0.9-1.7M subagent tokens (~0.5-1% weekly) |
| Spec workflow | ~1-2M |
| Ultracode | ~3M+ |
| Main session reading logs, big docs and research | most of the rest |

Builders and reviewers that write or judge our Java must stay on Claude, because they need javassist and the engine facts. The
savings come from moving the **reading, sorting, drafting and second opinions** off Claude.

## Ideas, best first

### 1. Log digest (free, every play session) - biggest easy win

Today I read the server and client logs myself after every session, often 50-150k tokens. Instead, a new log-digest tool (log_digest.py, planned) would:

1. Send each log through `llm.py` (free, 1M context, cleaned of personal data).
2. Use **Jev Noul** for each error / warning group: "is this from a Skyy mod?" and "actionable?".
3. Return about a 30-line digest: our errors with the class / mod, new vanilla noise, counts.

Claude then reads only the digest, and opens the raw log only at the lines it names.

### 2. Pack map summaries (free) - the planned "pack map tool"

A free model writes a one-line summary for every file in the repo. Builders, reviewers and I read the map, not the files: fewer
greps, fewer wrong files opened. Refresh it only for changed files (git diff), so it costs a few free requests a day.

### 3. Free second-opinion review lens (free / cheap) - more bugs found, no Claude cost

A different model family catches different bugs. In `skywynn-round`, after the build, the reviewer runs:

```
python tools/llm.py --free-only --file <patch> "review for bugs..."
```

The reviewer then **verifies** that list. Claude still decides; the outside model only adds leads.

- Free coding models: `cohere/north-mini-code:free`, `poolside/laguna-s-2.1:free`.
- Paid when it matters: `openrouter/pareto-code`.

### 4. Jev as the router for our own decisions (cheap, fast)

- **Round size:** a Choice of lean / full / ultracode from the task text plus the mods it touches. Low confidence -> Claude decides as
  today. This is a second check on my own call, not a replacement.
- **Agent model:** a Choice of haiku / sonnet / opus for each agent prompt.
- **Test feedback triage:** a Choice per line of Skyy's test messages: bug / balance / idea / question.
- **Finding triage:** a Score for each review finding (how likely it is real).
  - Low-score findings get a cheap re-check; high-score ones go straight to the fixer.
  - This trims verify passes.

### 5. Cascade for written content (free first, Jev checks, Claude only if it fails)

Item flavour text, quest dialogue (SkyyQuests), NPC lines, lore, author-request letters, release notes, research summaries:

1. A free model drafts.
2. Jev Noul checks "follows the style guide / facts?".
3. Retry, or escalate to the paid Jev router; Claude only for anything that must match game data.

This is TypeSafe's own "Jev-verified cascade" pattern. Skyy still approves anything players see.

### 6. Web research off Claude (`openrouter/fusion`, paid but small)

Mod surveys, licence checks, Hytale update notes (0.7 on 2026-10-12), tool-mod hunts: today these are Sonnet web agents.

- Fusion searches and fetches the web with several models and returns one merged answer.
- Each call is billed per model used, so it should stay well inside the $10 cap.
- Claude spot-checks the sources it cites.

### 7. Keep working when the Claude week is used up

At 97-98% weekly we stop. A scheduled job (OpenRouter only, no Claude) could still:

- run the log digest;
- refresh the pack map;
- draft content or specs;
- write a "done while you slept" note.

When Claude has usage again, it reviews those drafts.

### 8. Smaller savings

- **Prompt caching:** on paid models, put the fixed brief (AGENT-BRIEF, style guide) FIRST and the changing part last, so the cached
  prefix is reused. OpenRouter routes repeat requests to the same provider ("sticky routing") to keep that cache warm.
- **Structured outputs** (`response_format` JSON schema) for anything a script reads, so there's no re-asking when the format is wrong.
- **Batch small asks:** one request with 50 log groups beats 50 requests (the free limit is 1000 requests a day).

## Rules and limits

- Never send game files, other authors' files or Skyy's personal data. `llm.py` refuses Assets.zip / HytaleServer.jar and cleans
  names, UUIDs, emails, chat lines and user paths. Free models may keep or train on what they are sent.
- OpenRouter models never commit, deploy or edit code. Their output is a lead or a draft that Claude or Skyy checks.
- Spend caps: $10 a month on the key; the free path costs $0.

## Suggested first steps (a lean round each, after the weekly reset)

1. `tools/llm.py`:
   - add `--json <schema>` (structured output);
   - add a `jev(question, kind, options)` helper. One test call to confirm how OpenRouter passes Jev's question types; that is not
     documented on the model page.
2. a new log-digest tool (log_digest.py, planned), plus a change to the check-logs routine so it reads the digest first.
3. Pack map summaries (with the pack map tool already next in RESUME).
4. A `free_lens` option in `skywynn-round` (default on for reviews; off with `free_lens: 0`).

Rough savings: 50-150k Claude tokens per play session (logs), fewer file reads in every round (map), and extra review coverage at no
Claude cost.
