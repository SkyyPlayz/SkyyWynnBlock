---
name: skywynn-deploy
description: Deploy the SkyWynn set to Skyy's test world the safe way (game closed -> backup -> smoke -> deploy_set -> log -> commit -> tidy). Use when a round is ready or Skyy says "game closed, deploy".
---

# Deploy (PROJECT-RULES section 3)

1. Game closed: `tasklist | grep -i -c -E "^java|hytale"` must print 0. Never kill or start the game.
2. `python tools/backup_deploy.py` (note the `deploy-<stamp>` name).
3. `python tools/smoke_test.py` (~45 s; `--jar <Mod>/<Mod>-<ver>.jar` for an unpinned candidate). Check the log it names:
   `grep -c "\[Skyy.*ready"` (all ours present) and `grep -i -c "SEVERE.*Skyy"` = 0. Errors from other mods are noted, not fixed.
4. `python tools/deploy_set.py --yes` (the ONLY deploy path) - check its LAST line says "deployed N mods" (never pipe it into record_deploy with `| tail`; a STOP line means nothing was deployed, e.g. a builder's smoke server is running - wait and re-run). Third-party pack keys, retired mods, BetterMap worlds and Perfect Parries
   tuning are applied by it.
5. Records: a version change -> `python tools/record_deploy.py --title ... --mod MOD:OLD:NEW --steps <file> --checklist ... --log ...`
   (needs a HANDOFF row for a new mod). Pack-only change -> append one line to `docs/log/<month>.md` + a numbered line in
   TEST-CHECKLIST.md (what Skyy should test). Update RESUME "Now".
6. Commit only those files + push; `python tools/tidy_local.py --yes`.
7. Tell Skyy in 2-4 lines: what is live, what to test (checklist number), anything risky (e.g. a mod capped below the game version).
