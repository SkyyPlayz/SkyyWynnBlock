# Protect Area 0.8.2 - survey (2026-10-18)

Skyy: "check if we can use this in our pack? and edit it incase it doesn't do everything we need" (docs/answered/project.md line 108).

## Verdict (short)
**Do not pack it, do not edit it.** Licence is All Rights Reserved. Build our own SkyyZones (already specced) and learn from its design.

## What it is
- CurseForge "Protect Area" by Slartbartfast (Slart, mag42.dev), v0.8.2 (jar `ProtectAreaPlugin-0.8.2-SNAPSHOT-LogsFix.jar`, 2026-01-29), ~1.3K downloads. SNAPSHOT - the page warns of "data loss or corruption".
- It IS in Skyy's Mods folder (checked: manifest + class list only; a copy was unzipped in scratch, now deleted). No decompiling - the licence forbids it.
- Manifest: `MAG42:ProtectArea`, ServerVersion `*` (no pin, so it loads on 0.7.2; not smoke-tested), no dependencies. Main `dev.mag42.protectedareas.ProtectedAreasPlugin`.
- Systems in the jar: block break / damage / place / use guards, PvP/PvE/EvP damage guard, fall damage, NPC spawn (chunk + spawn-job) guards, damage and stamina modifiers, enter/leave transition (chat + title).
- Cuboid regions only (selection with `/pos1 /pos2 /expand`), several per area, priority 0-100, owners + trusted players, per-area PvP/PvE/EvP, mob-spawn types, fall damage, damage/stamina modifiers, public/trusted permission overrides, enter/leave chat + titles.

## Licence (the deciding point)
"All Rights Reserved": no distribution outside CurseForge without permission, no decompiling, **no modifying code or using it externally**, no commercial use without authorisation. Not MIT / PD / CC BY, no explicit permission, no source repo (only a Discord). PROJECT-RULES section 2: so no fold, no edit, no bundling. Packing it as a stopgap (Skyy installs it, we enable it, like WeaponCustomHUD / Zip Line, also ARR) is allowed as a third-party mod, but "edit it" is not. Only the author can grant edit rights (Discord discord.gg/bnSzM7Fs).

## Commands / clashes
- Top level: `/protect` (many subcommands), plus `/pos1`, `/pos2`, `/expand`, `/contractselection`, `/deselect`. Permission base `protectarea.command.protect[.sub]`; ops bypass everything.
- None of those names is a top-level command of ours (grep of tools/ + HANDOFF section 3: only an inner "expand" tab payload in Guilds). Not run through `tools/ci/crosscheck.py` (needs a built set); recheck there if ever packed. Its commands use its own permission nodes, so the Adventurer-group rule (HANDOFF section 3) is theirs to follow - players would not get them, which is fine (admin tool).
- Selection commands `/pos1 /pos2 /expand` are generic names that could clash with other tools (WorldEdit-style mods) later.

## What WE need protection for (and who does it now)
| Need | Today | Protect Area? |
|---|---|---|
| Player islands (members / trusted / visitors, 14 flags on 8 events, per-world PvP) | SkyyIslands (Island-Settings-Spec) - done | No: roles/co-op are ours; it knows nothing of island roles |
| Server zone worlds: FULL (no break/place/drops) and SKYBLOCK (marked resource blocks drop, placeholder a few seconds, vanishing scaffolding, trees regrow) | **Nothing built**; spec `research/cloud/Zone-Regen-Spec.md` (SkyyZones, world.md lines 63 + 75) | Covers only "no break/place". No resource-block list, no placeholder/regrow, no drops-off, no tree regrow, no skill-level gates: the hard part is missing |
| Hub / Zone 1 town (irregular polygon limit, safe zone, build-protected) | Plan: SkyyTowns (Zone-1-Town-Build-Plan row 7, "events verified, area check is new code") | Cuboids only, no polygon; many cuboids per area could approximate it |
| Shard worlds (SkyyShards) | Instance worlds, protected by the same island/zone guards; PvP via `WorldConfig` | Not needed |
| Arenas / dungeons / Guild Games (per-instance PvP + friendly fire) | `WorldConfig.setPvpEnabled` per instance (Island-Settings-Spec 4.2, Guild-Games-Spec); party friendly-fire in our ability code | Not needed; ours is per-world and party-aware, its PvP/PvE flags are not |
| SkyyMobs spawn suppression in safe zones | Town spec: safe radius row `town.*`; SkyyMobs levels spawns | It has spawn-type flags (all/hostile/neutral/friendly) - useful but SkyyMobs already owns spawns/levels; two spawn controllers could fight |
| Enter / leave titles | No mod of ours shows area titles (grep: only chat welcome lines on islands). Vanilla zone-discovery titles exist (Zone View Control is packed) | Yes, per-area title with icon/duration - a nice feature, but small to build ourselves |
| Fall damage off / damage and stamina modifiers per area | Not planned | Yes, but only matters for special zones (training yard) |
| Server Setup editable in game (PROJECT-RULES: everything editable via skyycfg) | Our rule | No: it has its own `/protect` command text UI, no Server Setup rows, no SkyyMenu page - breaks "one menu pattern" |

Already in the pack that overlaps: none (PACK.md / Mod-Database-Overview have no region-protection mod; surveyed earlier and rejected: OrbisGuard ARR + needs Hyxin, HyProtect 0.1.2 MIT spawn radius only, Block Regen ARR 0.6-only, Aura BlockFill ARR; VoidProtect 1.1.0 is in the Mods folder, a void-fall guard, unrelated).

## Duplicates / per-world setup
- Overlap with SkyyIslands guards: both would cancel the same Break/Place events. If a cuboid sat over an island, two systems would answer; on islands we would have to leave it out entirely. Safe only in zone worlds with no SkyyIslands guard.
- Per-world: its areas are stored by name in its own data file; I could not confirm (without decompiling) whether areas are tied to a world name. Our zones are per zone world and per profile, so this is untested - risk of the same coordinates protecting in every world.
- Per-profile worlds: nothing profile-aware.

## Recommendation
1. **Build our own SkyyZones** (ultracode, as already planned): FULL + SKYBLOCK modes, polygon/cuboid regions, resource list, placeholders, titles, Server Setup rows. This covers everything Protect Area does for us and the large part it cannot.
2. **Ask the author** only if Skyy wants it as a stopgap: permission to edit/fold, or a source licence. Low odds (ARR, snapshot, Discord-only).
3. **Learn from it** (read-only, class names + public page): per-area priority for overlaps, owners vs trusted, public/trusted permission overrides, enter/leave title with icon/duration/fade, `removenpcs`, per-area mob-spawn type flags, op bypass. Fold these ideas into Zone-Regen-Spec (title per region + priority + op bypass are the new ones).
4. Optional stopgap before SkyyZones exists: pack it for test worlds only (Skyy installs, we enable in PACK_THIRD_PARTY). Costs: ARR, snapshot data-loss warning, duplicate guard risk, no Server Setup. Not recommended.

## What we would build on top if it were packed (it can't be edited)
Resource-block list + regrow placeholder, vanishing scaffolding, tree regrow, no-drop mode, skill-level gates, polygon town limit, safe-zone link to SkyyMobs, Server Setup rows + SkyyMenu page, island-role awareness - i.e. almost everything. Packing it would save only the plain "no break/place" and titles.

## Questions for Skyy
1. Build SkyyZones ourselves and skip Protect Area? [yes]
2. Should I message the author (Discord) about edit/fold rights anyway? [no - ARR snapshot, not worth the wait]
3. Add per-region enter/leave titles (with icon) to the SkyyZones spec? [yes, small]
4. Per-region extras from it: priority for overlaps, op bypass, fall damage off for special areas? [priority + op bypass yes; fall damage later]
