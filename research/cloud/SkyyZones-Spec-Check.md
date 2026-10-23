# SkyyZones spec check (2026-10-23)

Cloud/agent check of `research/cloud/Zone-Regen-Spec.md` against what SkyyZones 0.2.0 shipped (read from
`SkyyZones/build_skyyzones_0.2.0.py` header, `docs/tests/2026-10.md` lines 2954-2984, `HANDOFF.md` line 34). Docs only; no game files read.

**Verdict:** the original task ("protected areas + titles plan" vs the spec) is mostly OBSOLETE - protection, area titles and Z2 regrow are
live. What stays useful: the gap list below, the config-key check, and the Z3 / Z4 next steps.

## Decisions followed

- `docs/answered/world.md` line 63 - server zones are hand-built and PROTECTED; only marked resource blocks can be gathered.
- `docs/answered/world.md` line 75 - two protection kinds: FULL (nothing breaks, places, drops) and SKYBLOCK (listed blocks break, placeholder for seconds, scaffolding).
- `docs/answered/world.md` line 115 / 120 - Skyy away 2026-10-20 "figure it out": spec defaults taken (one mod, break gate, bedrock placeholders, 3-15 s regrow).
- `docs/answered/world.md` lines 30 and 64 - zone level bands; walking in stays free ("go explore"), solo pack stays vanilla.
- `docs/answered/gear.md` line 145 - hammers off in protected zones; Vein Mine only on listed same-type ore.
- Skyy 2026-10-18 popup "Build SkyyZones (Recommended)" (logged in `docs/log/2026-10.md`, 10-18 09:20 line): own mod, borrow Protect Area ideas only (titles, priority, op bypass) - see `research/Protect-Area-Survey.md`.

## 1. Spec phase vs what shipped

| Spec phase (section 11) | Status | Notes |
|---|---|---|
| Z0 probes | DONE (jar bytecode) | Z1, Z5, Z5b, Z6, Z9, Z13, Z14, Z18, Z19 answered. Z2, Z3, Z4, Z16, Z17 NOT answered (need a live test). |
| Z1 protection, wand, show / info, builder mode, Server Setup page | LIVE 0.1.0 | Plus extras not in the spec: area titles, bridge `zones:fn:check` / `zones:fn:region` / `zones:build:<uuid>`, region history + change log, fail-closed region files. |
| Z2 regen (stone + ores) | LIVE 0.2.0 | Journal + 60 s snapshot, catch-up on chunk load, `/zones restore`, `/zones audit`. |
| Z3 whole-tree fell, crops | NOT built | logs and crops are held at regrow 0 s. |
| Z3b scaffolding | NOT built | `place.allow` lines are kept verbatim but ignored. |
| Z4 gates + anti-abuse | NOT built | `gate` lines kept but ignored; no `/zones status` anti-abuse counters. |
| Z5 drops to inventory, SkyyTowns uses SkyyZones | NOT built | Bridge `zones:fn:check` exists for it. |

## 2. Gaps and overlaps between spec and shipped code

| # | Item | Spec says | Shipped | Action |
|---|---|---|---|---|
| G1 | Hoe, shovel, bucket, block-state cycling, fertilize, watering can | Section 3.2: all writes guarded | NOT stoppable (no event; probe Z0b). Spec 3.2 still lists them as denied. | Fix spec wording; later: a regrow-style scan of protected regions (0.1.0 header calls Z2 scan "the planned fix" but 0.2.0 did not add it). |
| G2 | Fire spread, source-less explosions, flowing fluid | Z9 asked | Not cancellable (Z9 answered) | Builders keep open water / lava away; consider `WorldConfig.setDisabledFluidTickers` in the world config. |
| G3 | Silver / gold regrow | Q2 has no row | Builder's choice, 6 s | Ask Skyy (Q1 below). |
| G4 | Automatic audit at start | Spec 5.1 | Skipped on purpose (journal is synchronous) | Spec note only. |
| G5 | Enter / leave titles | Not in the spec (idea from Protect Area) | Live: subtitle "Protected area" / "Gathering area", leave notice, `titles.gapSec` | Add to the spec so one file describes the mod. |
| G6 | Commands `/zones place add`, `/zones audit` as spec | Spec 5.1 | `place` not built; `audit <region> [fix]` built (500,000-block cap) | See section 4. |
| G7 | Overlap rule | "higher priority wins; types are the union" | Same, plus tie-break: SKYBLOCK before FULL, then smaller id | Add the tie-break to the spec. |
| G8 | Builder mode HUD tag | Spec: HUD tag | Event title + notice every `build.remindSec` (300); real tag waits for SkyyHud | Main session: SkyyHud reads bridge `zones:build:<uuid>`. |
| G9 | Vanilla TriggerVolumes (box / sphere volumes with NoDestroy, NoBuild, ShowEventTitleEffect) | Not in the spec | Noted in the 0.2.0 header (EXTRA) | Survey: could builders use them for FULL decor areas with no code? No Server Setup or regrow, so ours stays the source of truth. |
| G10 | Overlap with other mods | PROJECT-RULES 2 "no duplicates" | `research/Protect-Area-Survey.md` found Protect Area (ARR) unusable; Rechunk (GPLv3, `docs/answered/world.md` line 67) overlaps only for chunk reset | Record the choice in `PACK.md` if not there yet (UNVERIFIED - I did not open `PACK.md`). |

## 3. Config keys vs `tools/CONFIG-CONTRACT.md`

All keys below are in the shipped build (`SkyyZones/build_skyyzones_0.2.0.py` lines ~698-893, 3297-3362). The contract says every
setting has a Server Setup row, game and file agree, times in seconds, admin commands go through `CfgFn.cmdSet`.

| Key | Default | Spec section | Contract note |
|---|---|---|---|
| `zones.on` | ON | new (part switch) | ok |
| `zones.worlds` | empty | 5.2 | ok |
| `zones.opBypass` | OFF | new (Protect Area idea) | ok |
| `zones.blockMobs` | ON | 3.2 | ok |
| `use.tools` | list | 3.2 | ok |
| `titles.on`, `titles.leave`, `titles.gapSec` | ON, ON, seconds | new | ok (seconds) |
| `build.remindSec` | 300 | new | ok (seconds) |
| `regen.enabled`, `regen.speedMult`, `regen.jitter`, `regen.offlineCounts`, `regen.defaultSec`, `regen.passBatch`, `regen.maxDepleted` | spec 5.2 values | 5.2 | ok |
| `regrow.<type>` table = seconds,placeholder | spec Q2 | 4.2 | ok |
| `regen.restoreAll` (action) | - | new | ok; also `/zones restore all` |

Missing from Server Setup vs spec 5.2 (add with Z3 / Z3b / Z4): `scaffold.lifeSec` 8, `scaffold.maxPerPlayer` 24, `scaffold.reach` 6,
`scaffold.refund`, `scaffold.free`, `tree.maxBlocks` 600, `tree.leafDrops`, `regen.loadBatch` (folded into `regen.passBatch`), all section 7 anti-abuse rows, per-region `gate`.

Contract checks still worth doing: (a) region `world`, `boxes` and new / deleted regions are commands only (need wand corners) - this is
allowed, but the contract wants this stated on the page (UNVERIFIED that it is); (b) region edits are logged by the mod, not the kit's
Changes list with Undo - the contract's "change-log line with Undo" rule (PROJECT-RULES 4) may not be met for region edits; ask for a check.

## 4. Commands

| Spec 5.1 | Shipped | Missing |
|---|---|---|
| `/zones wand` | yes | - |
| `/zones region create / mode / addbox / delete / priority / title / types / flags` | yes | - |
| `/zones place add / remove` | no | Z3b |
| `/zones type add <type> <id or look>` | yes (`/zones type <type> <ids\|none\|look>` too) | - |
| `/zones show`, `/zones info`, `/zones build on/off`, `/zones list`, `/zones reload [clear]` | yes | - |
| `/zones status` | yes (waiting blocks, next due, counters, journal errors) | refused breaks last hour, flagged players (Z4) |
| `/zones restore <id/all>`, `/zones audit <id> [fix]` | yes | - |

## 5. Next steps for Z3 / Z4 (need live probes first)

1. Live probe round (op, scratch world): fell one natural tree - does the engine fell the whole tree (Z2), in how many events, and can we read every block first (Z16)? Rewrite a tree around a standing player (Z17). Crop first-stage id and whether F-harvest fires any event (Z4 / Z0b).
2. Z3 whole-tree: trunks carry Support + Physics and Farming Stages (0.2.0 header). Plan B if the engine will not fell whole trees: record the shape on the first break and remove connected trunk + leaves ourselves.
3. Z3 crops: after the probe, set `regrow.<crop>` above 0 (currently refused in Server Setup until Z3).
4. Z3b scaffolding: needs our own `Skyy_Scaffold` block (no vanilla scaffold, Z14). Per-player cap and vanish timer live in the journal as `T` lines.
5. Z4 gates + anti-abuse: the 0.2.0 journal already refuses double mining of a waiting spot (spec 7 X3). Remaining rules (AFK, rate cap, contested-spot fairness) are Server Setup rows plus `/zones status` counters; small enough for a lean round once Skyy answers Q2.
6. Rollback note to add to `tools/deploy_set.py` for Zones: run `/zones restore all` first (already in the 0.2.0 header).

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | Silver and gold regrow time (the spec has no row; the builder chose 6 s). | [keep 6 s] |
| 2 | Anti-AFK (refuse breaks after 15 min in one spot, cap 300 breaks a minute) and the "turn-taking" limit when a spot is contested (spec Q7 / Q8) - confirm for Z4? | [yes, both, contested only for turn-taking] |
| 3 | Z3 trees: one hit fells the whole tree, even with a small axe; vanilla leaf drops (spec Q13). | [one hit; vanilla leaves] |
| 4 | Scaffolding: scaffolding only, 8 s, 24 at once, player must carry the item (spec Q10). Do you want it, or are islands buildable enough without? | [scaffolding only, 8 s, 24, needs the item] |
| 5 | Drops go straight to the inventory in SKYBLOCK areas (spec Q6) - needs probe Z8. | [yes if the engine allows] |
| 6 | Should region edits show in Server Setup -> Changes with Undo like other settings? | [yes, if the kit can take it] |

## For the local session

UNVERIFIED (needs `HytaleServer.jar` or a live test world):
- Z2 / Z16 / Z17 tree felling and rewrite; Z4 crop stage ids; Z8 cancel-drop-and-give-to-breaker without breaking SkyyCollections stack crediting; Z10 block damage shared vs per-player; Z12 player address.
- Whether vanilla TriggerVolumes (G9) can replace FULL decor regions for builders.
- Whether `PACK.md` already records the protect-area choice (G10) and whether region edits meet the change-log + Undo rule (section 3).
- `research/cloud/Zone-Regen-Spec.md` still reads "Nothing is built yet" - update its header and the 3.2 wording (G1) when convenient (main session; outside `research/cloud/` rules do not apply, it is in `research/cloud/`).
