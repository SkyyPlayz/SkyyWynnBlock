---
name: skywynn-logs
description: After Skyy plays (or says "check the logs"), summarise the newest server + client game logs, find our mods' warnings, recycle old logs. Use instead of hand-grepping logs.
---

# Check the game logs (memory: skywynn-check-logs; PROJECT-RULES 1)

1. `python tools/log_scan.py` (all kinds, grouped, vanilla animation noise dropped) and `python tools/log_scan.py --ours` (only [Skyy...] / Skyy_ lines).
2. Anything ours that is new (compare with `grep -n "<text>" docs/log/*.md`): send it to a Sonnet diagnosis agent (read-only) - or ask Jev:
   `python tools/llm.py "why does X happen" --file <log>` - never read the whole log yourself.
3. Known / not ours: pack-mod asset errors, vanilla NPC animations, pre-semver manifests, The Armory movement WARNs (RESUME NEXT 2).
4. `python tools/log_scan.py --recycle` once read (Recycle Bin, keeps the newest of each folder; Skyy 2026-10-08).
5. One line in `docs/log/<month>.md` (what was found + where the fix goes), commit + push.
