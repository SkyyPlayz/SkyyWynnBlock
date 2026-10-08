# Ability probe plan (SkyyAbilityProbe 0.1: engine checks P1-P15 before the class-ability engine)

Cloud draft, 2026-10-08. Turns the 15 engine probes of `research/cloud/Class-Ability-Engine-Spec.md` section 16 (build step E0, section
15) into one throwaway probe jar, built the same way as SkyyGatherProbe / SkyyReelProbe / SkyyMonkProbe (`research/cloud/Monk-Probe-Plan.md`).
Draft code (**UNTESTED**: there is no `HytaleServer.jar` in the cloud): `SkyyAbilityProbe/build_skyyabilityprobe_0.1.py` +
`SkyyAbilityProbe/test_skyyabilityprobe_0.1.py`. **Never pin or deploy it until the local session has built it, reviewed it and run its
harness.** The spec's E0 row lists P1-P13; P14 and P15 are cheap reads, so they are in too.

## Decisions this follows

| Source | What it locks | Probes |
|---|---|---|
| `docs/answered/classes.md` line 31 | 2 class abilities on the two rune lines, built on runes | P1, P3, P4, P14 |
| `docs/answered/classes.md` lines 104-105 | every weapon's hold is its traversal + attack: abilities need their own input | P1 |
| `docs/answered/classes.md` line 96 | traversals cost Mana + Stamina; abilities are a separate system | P7, P15 |
| `docs/answered/classes.md` lines 112-114 | Mana Barrier 12 s, drains Mana instead of Health, a faint see-through dome | P5, P9 |
| `docs/answered/classes.md` lines 120-121 | combo hits may stunlock; bosses break out after 3 s x players | P8 |
| `docs/answered/classes.md` line 129 | Blood Frenzy costs Mana + Stamina per attack, hit or miss | P2, P7 |
| `docs/answered/classes.md` lines 132-135 | Warlord's Banner: 12 blocks, 30 s, attack speed buff, falls at the end | P6, P11 |
| `docs/answered/classes.md` lines 142, 145-147 | Sanctuary 8 blocks; Shield Bubble 6 blocks / 12 s; Guardian Spirit passive save at 30% | P5, P10, P13 |
| `research/cloud/Class-Ability-Engine-Spec.md` sections 3, 10, 12-14, 16 | the input, buff, HUD, rows and performance designs these probes check | all |

## 1. The probe jar in one table

One op-only command `/aprobe` (alias `/abilityprobe`; never `/abilities` - vanilla 0.7 owns it), node `skyyabilityprobe.admin`, empty
permission groups on the root and its 4 usage variants. Every chat line also goes to the server log as `[SkyyAbilityProbe] ...`. State is
memory only, per player, **one timed probe at a time** (section 6).

**Runs on 0.6.8 and 0.7.** Every Hytale 0.7 class (rune system) is reached by reflection at run time, so the jar loads on today's server.
On 0.6.8 the rune probes say "needs Hytale 0.7"; the rest work now.

File + line = a LIVE Skyy build script already calls that API (newest scripts: SkyyClasses 0.1.14, SkyyArmory 0.1.9, SkyyGear 0.2.9,
SkyySkills 0.4.21, SkyyProfiles 0.1.6, SkyyIslands 0.5.5, SkyyHud 0.3.16).

| # | Probe | Command | Engine API | Already used by a Skyy mod? | Runs on |
|---|---|---|---|---|---|
| P1 | Rune keys + chain event + cancel | `p1`, `p1 cancel` | `InteractionChainStartEvent` (EntityEventSystem, event class handed in at run time), `getType` / `getContext().getHeldItem()` / `setCancelled` by reflection | **NO** - UNVERIFIED (`research/Hytale-Runes-Research.md` line 264). EntityEventSystem(Class) itself: `SkyyGear/build_skyygear_0.2.9.py` line 11767 | 0.7 |
| P2 | Swings that miss raise the event | `p2 [secs]` | same event, type `Primary`, vs landed hits (Inspect group) | **NO** for the event; Inspect group YES: `SkyyClasses/build_skyyclasses_0.1.14.py` line 3905, `SkyyArmory/build_skyyarmory_0.1.9.py` line 9769 | 0.7 |
| P3 | CooldownHandler from a plugin + HUD fill | `p3`, `p3 read <rootId>`, `p3 <method> <rootId> <secs>` | InteractionManager component -> a getter returning a `*Cooldown*` type; methods by name | InteractionManager component YES: `SkyyArmory/build_skyyarmory_0.1.9.py` lines 4215-4219, 8302; **CooldownHandler NO** | 0.7 |
| P4 | Writing runes into AbilitySlots | `p4 read / watch / put <slot> <id> / take <slot> / bad <slot>` | `InventoryComponent$AbilitySlots` (reflection) -> `ItemContainer.getItemStack((short))`, `addItemStackToSlot((short), ItemStack)`, `removeItemStackFromSlot`; `InventoryChangeEvent.getItemContainer()` | ItemContainer calls YES: `SkyyClasses/build_skyyclasses_0.1.14.py` lines 3084, 3097; `SkyyProfiles/build_skyyprofiles_0.1.6.py` line 534; the event YES: `SkyyGear/build_skyygear_0.2.9.py` lines 3673, 11779; **AbilitySlots NO** | 0.7 |
| P5 | Filter order + lethal save | `p5 [secs]`, `p5 save` | two DamageEventSystems in the Filter group with `getDependencies` = `SystemDependency(Order.BEFORE / AFTER, DamageSystems$ArmorDamageReduction)`; Inspect group; `Damage.setCancelled`; `EntityStatMap.setStatValue` | YES: ArmoryTuneSys `SkyyArmory/build_skyyarmory_0.1.9.py` lines 9999-10011 (registered 10441-10448); `SkyyGear/build_skyygear_0.2.9.py` lines 3926-3927, 13508-13524; setStatValue `SkyySkills/build_skyyskills_0.4.21.py` line 7568 | both |
| P6 | Attack speed buff vs SkyyGear tiers | `p6 [effectId\|none] [secs]` | `EffectControllerComponent.addEffect(ref, fx, secs, OVERWRITE, acc)` + `getActiveEffects().get(i)`; swing gaps (0.7) + hit gaps | YES: `SkyyArmory/build_skyyarmory_0.1.9.py` line 6373; `SkyyGear/build_skyygear_0.2.9.py` lines 10220-10224 | both (swing gaps 0.7) |
| P7 | Mana / Stamina spend vs SkyySkills regen | `p7 [secs]` | `EntityStatMap.subtractStatValue(int, float)` every 0.25 s | YES: Leap.take `SkyyArmory/build_skyyarmory_0.1.9.py` lines 7005-7024; regen `SkyySkills/build_skyyskills_0.4.21.py` line 3495 (ManaRegen) | both |
| P8 | What stops a mob attacking | `p8 [hits/s] [secs]`, `p8 stun` | `DamageSystems.executeDamage` with `Damage$EntitySource` (no knockback); the vanilla `Stun` effect | YES: ArmoryTrav.hit `SkyyArmory/build_skyyarmory_0.1.9.py` lines 6737-6748; Stun on a mob lines 6366-6376; the LIVE stunlock breakout lines 98-111, 9814-9997 | both |
| P9 | Faint dome look | `p9 <particleId> [radius]` | `ParticleUtil.spawnParticleEffect(String, Vector3dc, ComponentAccessor)` | YES: `SkyyArmory/build_skyyarmory_0.1.9.py` line 6629 (probe 4053) | both |
| P10 | Bubble removes hostile projectiles | `p10 [secs]` | sphere scan + `ProjectileComponent` / `StandardPhysicsProvider.getCreatorUuid` + `CommandBuffer.removeEntity(ref, REMOVE)` | YES: ShotTrack `SkyyClasses/build_skyyclasses_0.1.14.py` lines 2583, 2593-2595; removeEntity `SkyyArmory/build_skyyarmory_0.1.9.py` lines 7133, 7163 | both |
| P11 | Temporary banner block | `p11 <blockId> [secs]` | `World.getChunkIfLoaded(ChunkUtil.indexChunkFromBlock(x, z))`, `WorldChunk.getBlock / setBlock`, `World.execute`, `HytaleServer.SCHEDULED_EXECUTOR` | PARTLY: setBlock / getBlock / getChunkIfLoaded `SkyyIslands/build_skyyislands_0.5.5.py` lines 2712, 2785, 2791 (chunk 0, 0 only); scheduler `SkyyArmory/build_skyyarmory_0.1.9.py` line 10362; **`indexChunkFromBlock` NO** (build-time probe; P11 is left out if missing) | both |
| P12 | NPC target clear / taunt | `p12`, `p12 stun` | dump of NPCEntity / its Role methods named target / mark / lock / aggro ... (reflection, to the log); Stun 1 s | **NO** (no Skyy script touches NPC targeting); Stun YES (P8 row) | both |
| P13 | Sphere-scan cost + tick rate | `p13 [zones] [secs]` | `TargetUtil.getAllEntitiesInSphere` x zones x 4 Hz; ticks per second from our own EntityTickingSystem | YES: `SkyyArmory/build_skyyarmory_0.1.9.py` line 6759; TravTick lines 4398, 9789 | both |
| P14 | Rune sections leak across profiles | `p14` | AbilitySlots / RuneBag (reflection); bridge `profile:key:<uuid>` | bridge YES: `SkyyProfiles/build_skyyprofiles_0.1.6.py` line 1584; **rune sections NO** | 0.7 |
| P15 | Vanilla Mana max 100 vs SkyySkills | `p15` | `EntityStatType.getAssetMap().getAsset(mana).getMax()` + the player's value / max | YES: Overall.typeMax `SkyySkills/build_skyyskills_0.4.21.py` lines 6720-6723; breakdown lines 6997-7012 | both |
| - | info / stats / stop | `info`, `stats`, `stop` | build-time desk reads (particle ids, banner ids, rune Cast ids, Mana Max, CooldownHandler class names) | - | both |

## 2. Each probe: what it measures, pass / fail, and the engine fallback

| # | Measures | Pass | Fail -> what the engine spec does instead |
|---|---|---|---|
| P1 | Every chain start of yours for 60 s: type, root id, held item. With `cancel`, Ability2 / 3 chains are cancelled and your Mana is re-read 1 s later. Skyy reports the default keys. | Rune keys print Ability2 / Ability3 lines; a cancelled cast shows no animation, no cooldown fill, no Mana spent | No event for rune keys: hook by polling the cast root's marker effect (spec 3.2 step 3 fallback, the Grapple Bolt click trick). Cancel leaves a stuck animation: never cancel - let the rune root do nothing and refuse in our pipeline (fail sound only) |
| P1b | Our OWN rune (Cost 0 / None, 1-step root) shows in the HUD and casts | - | **Not in this jar**: it needs a rune item = an asset. Probe it in E2 or a SkyyAbilityProbe 0.2 with assets |
| P2 | Primary chain starts vs your landed hits (20 s). Swing 5 times at air, 5 at a mob. | Swings > hits (`PASS (10 swings, 5 landed hits)`) | Blood Frenzy per-swing cost counts landed hits only (misses free), said in the row help (spec 7.2) |
| P3 | Where the CooldownHandler is (InteractionManager / Player getter), all its methods to the log; `read` = isOnCooldown / getCooldown after a vanilla rune cast; `<method> <rootId> <secs>` calls one method (String = root id, numbers = secs) | A handler is found, `read` shows the vanilla cooldown, and a code-set cooldown makes the rune's HUD slot fill | HUD H1 is out: the SkyyHud Abilities widget (spec 12 H2) shows cooldowns; the vanilla HUD keeps only the 0.25 s anti-spam |
| P4 | `put` a rune by code into slot 0 / 3, then die / change world / relog and `read`; `bad` puts the held NON-rune into a slot; `watch` logs InventoryChangeEvents on AbilitySlots / RuneBag for 60 s | The rune stays through all three; `bad` is refused; a drag in the bench prints an AbilitySlots line | `bad` accepted: our mirror checks item ids itself before writing. No event for drags: the AbilTick re-checks the slots each second. Lost on death / relog: re-mirror on PlayerReady (already planned, spec 3.2 step 4) |
| P5 | Each hit to / from you: amount at our filter BEFORE armour, AFTER armour, and landed. `save`: the next lethal hit is cancelled in the AFTER filter and Health set to 30% | No hit changes after our late filter ("changed AFTER" count 0) and the save keeps you alive | Something runs after us (SkyyGear's GearArmorSys / GearTrueSys are also AFTER armour, unordered vs us): declare Guardian Spirit / Mana Barrier AFTER those classes too (cross-mod class lookup), or use the `FilterUnkillable` invulnerability path (spec 10, Guardian Spirit row) |
| P6 | Average swing gap (0.7) and hit gap; with an effect id, that effect is re-put on you every 0.5 s (1 s long) and every time it vanished early is counted | Baseline vs `p6 SkyyGear_Speed_Fast` (a Medium sword) shows a shorter gap and 0 "taken off" | **Expected FAIL by reading the code**: SkyyGear's `GearSpeed.put` takes every other tier effect off each second (`SkyyGear/build_skyygear_0.2.9.py` lines 10212-10228). Fallback = spec 10.2 option (b): SkyyGear itself reads a bridge "ability haste" value and picks the faster tier (a SkyyGear change) |
| P7 | Every 0.25 s: 0.5 Mana + 0.25 Stamina subtracted (2 Mana + 1 Stamina per second, 20 + 10 in 10 s); each write read back; regen seen between steps | 0 inexact subtracts and Mana regen > 0 meanwhile | A write fight: spend through a SkyySkills bridge instead of our own subtract. No regen while spending: tell Skyy - lines 129 / 135 say regen continues, so SkyySkills must not pause on spends |
| P8 | Probe hits with NO knockback (default 3 a second = 333 ms, about 18 in 6 s) on the nearest mob; how often it still hits you. `stun`: the vanilla Stun 1.5 s instead | Data, not pass / fail: 0 mob hits = damage alone interrupts; > 0 = only knockback / Stun interrupt | Note: the boss breakout is **already live** in SkyyArmory 0.1.9 for Monk combo hits (stun.* rows; it cancels the hit and drops the KnockbackComponent). The engine should feed ability hits into that same counter through a bridge, not build a second tracker (Question 1) |
| P9 | 16 particles on a ground ring + 8 on an upper ring every 0.5 s for 12 s (48 calls a second); `/aprobe info` lists candidate particle ids from Assets.zip | Skyy: "visible but easy to see through" (line 114) | Thin ring only (ground ring, every 1 s); a transparent dome MODEL needs an asset (later) |
| P10 | A 6-block bubble where you stand: every 0.25 s (48 scans in 12 s) projectiles inside that are not yours are removed; scan cost | Arrows vanish cleanly, no hit lands, scan < 0.5 ms | Ghost arrows / hits still land: block at damage time instead (filter hook cancels projectile damage to allies inside the bubble) |
| P11 | A `<blockId>` placed 2 blocks in front of you, read back, removed after 10 s on that world's thread (only if it is still our block) | It appears where expected and vanishes cleanly (`/aprobe stats`: "removed cleanly") | On 0.7 use the vanilla `SpawnAbilityEntity` interaction (a stationary model entity with a Lifetime, `research/Hytale-Runes-Research.md` section 5) from the banner rune's chain - no code; else particles only (spec 10) |
| P12 | Candidate targeting methods of the nearest NPC + its Role (and role parts whose type says Support / Target / Combat / Marked / Sensor) to the log; `stun` = Stun 1 s and its hits on you after | The log names a set / clear target method (the local session then wires `p12` to call it) | Awe = the vanilla Stun 1 s (already live); taunt = damage from the Warrior (mobs usually turn to their attacker) |
| P13 | zones x 4 Hz sphere scans (radius 8) on a 10-block ring around you: 48 zones = 192 scans a second = 6.4 per tick at 30 TPS; average and max scan time per tick; world ticks per second | Under 1 ms per tick at 48 zones; ticks per second about 30 | Lower `abil.maxLive`, zone tick 2 Hz, or scan only zones that hurt enemies (spec 14 rules) |
| P14 | Your rune sections -11 / -12 and SkyyProfiles profile key; switch profile, run again | Different (or empty) runes on the other profile | **Expected FAIL**: SkyyProfiles saves 6 sections only (`SkyyProfiles/build_skyyprofiles_0.1.6.py` line 1789). Fix = SkyyProfiles adds -11 / -12 to the snapshot (before players get runes) |
| P15 | Your Mana value / max, the Mana stat type's own max (desk: 0 on 0.6.8, 100 on 0.7), and max minus it | Your max is what `/skills mana` shows as SkyySkills' base (10 / 20 + class levels): the vanilla 100 is not added on top | SkyySkills' base Mana formula (`base - EntityStatType(Mana).max`, `SkyySkills/build_skyyskills_0.4.21.py` line 225) needs a fix; every ability Mana cost row waits for Skyy's Mana-scale answer (`research/Hytale-Runes-Research.md` 4.1) |

## 3. Test script for Skyy (two short sessions)

Before: the local session pins the probe for ONE session. Be op, on a TEST world, alone, with a few weak hostile mobs and a skeleton
archer nearby. Do not play normally with it on. Afterwards: `/aprobe stop`, then send the server log.

**Session A - today (Hytale 0.6.8), about 12 minutes**

| Step | Do | Look for |
|---|---|---|
| 1 | `/aprobe info` | which probes this server supports; the particle / banner ids to use |
| 2 | `/aprobe p15`, then `/skills mana` | do both show the same max Mana? |
| 3 | `/aprobe p7`, stand still 10 s | "PASS (exact)", regen kept running |
| 4 | `/aprobe p5`, hit a mob, let it hit you | lines "before armour / after armour / landed" |
| 5 | `/aprobe p5 save`, take a big hit (fall from high up) | you survive at 30% Health |
| 6 | Hold a Medium-speed sword: `/aprobe p6` and swing nonstop 20 s; then `/aprobe p6 SkyyGear_Speed_Fast`, same | the two hit gaps; "taken off" count |
| 7 | Hold a non-Monk item: `/aprobe p8` next to a mob; then `/aprobe p8 stun` | does the mob still hit you? |
| 8 | `/aprobe p9 <a ring id from step 1>` | is the dome visible but easy to see through? |
| 9 | `/aprobe p10`, let the skeleton shoot at you | do the arrows vanish cleanly? |
| 10 | Face open flat ground: `/aprobe p11 <a banner id from step 1>`, wait 10 s, `/aprobe stats` | appears, then "removed cleanly" |
| 11 | `/aprobe p12` near a mob, then `/aprobe p12 stun` | does it turn back to you right after? |
| 12 | Stand among some mobs: `/aprobe p13` | "PASS" and the ticks per second |

**Session B - after Hytale 0.7 is live (2026-10-12), about 8 minutes** (get vanilla runes with `/abilities give`, slot two in the bench)

| Step | Do | Look for |
|---|---|---|
| 1 | `/aprobe p1`, press both rune keys, swing | which keys; Ability2 / Ability3 lines |
| 2 | `/aprobe p1 cancel`, press a rune key | no animation, no cooldown fill, "PASS: nothing spent" |
| 3 | `/aprobe p2`, swing 5 times at the air, 5 times at a mob | "PASS (... misses were seen)" |
| 4 | `/aprobe p3`; cast a rune; `/aprobe p3 read <its Cast id from info>` | a handler is found; the cooldown shows |
| 5 | `/aprobe p3 <a method the log names> <Cast id> 8` | does the HUD slot fill for 8 s? |
| 6 | `/aprobe p4 watch`, drag a rune in the bench | an AbilitySlots line |
| 7 | `/aprobe p4 take 0`, `/aprobe p4 put 0 <rune id>`; die, change world, relog, `/aprobe p4 read` after each | the rune stays |
| 8 | Hold a sword, `/aprobe p4 take 3`, `/aprobe p4 bad 3` | "PASS - refused" |
| 9 | `/aprobe p14`, switch profile, `/aprobe p14` | same runes on both profiles = the leak |
| 10 | `/aprobe p15` again, `/skills mana` | max Mana not 100 + base |

## 4. Probes that rely on APIs no existing Skyy script uses

| What | Probe | Why it is new | Risk |
|---|---|---|---|
| `InteractionChainStartEvent` (listen, read type / context, cancel) | P1, P2, P6 swing gaps | 0.7-only; no Skyy mod targets 0.7 yet | Method names differ on the release jar (the harness checks them when the class is present) |
| The player's `CooldownHandler` | P3 | never reached by a Skyy mod; access path INFERRED | Not reachable from the InteractionManager / Player getters; method shapes unknown (P3 calls by name with filled parameters) |
| `InventoryComponent$AbilitySlots` / `$RuneBag` components | P4, P14 | 0.7-only | Slot filters may not guard code writes (P4 `bad`) |
| NPC targeting (clear / set target) | P12 | no Skyy script touches NPC AI | P12 only DUMPS candidate method names; a second pass must call one |
| `ChunkUtil.indexChunkFromBlock` + `WorldChunk.setBlock` outside chunk (0, 0) | P11 | SkyyIslands only writes chunk (0, 0), where local and world coordinates match | World vs chunk-local coordinates; the air block id "Empty" (both UNVERIFIED; P11 reads back and says so) |

Everything else (Filter / Inspect damage systems and their order, probe damage, status effects on mobs and players, particles, sphere
scans, projectile creators and removal, stat spends and sets, the profile bridge, the stat type max) is already used by a live Skyy mod -
see section 1.

## 5. What can share SkyyMonkProbe's code

The draft copies these from SkyyMonkProbe (`git show origin/claude/epic-pasteur-8yx2a8:SkyyMonkProbe/build_skyymonkprobe_0.1.py`), so a
reviewer who checked one has checked both: the log + SINK class, the pure helpers (f1, verdict, number, dnum), prOf / pos / look / enemy /
near / hit (the MINE-marked probe hit), the per-player EntityTickingSystem, the Inspect-group hit hook, the command root + usage variants,
the plugin shape, `IncludesAssetPack` false + its harness check, and the harness J / A / X / P blocks.

| Probe here | Monk probe it overlaps |
|---|---|
| P8 (probe hits on a mob, mob hits on you) | m6 / m7 probe hits (same `hit()`), M12 combo hit hook |
| P13 (sphere-scan cost) | M12 aura scan cost (1 scan a second; P13 is the 4 Hz x 48 zones version) |
| P7 (stat spends) | M9 costs (Leap.take shape) |
| P5 (Filter-group hooks) | M4 FALL filter |
| P12 stun | `slowfx` (a vanilla effect on a mob) |

Both jars can be pinned for the SAME test session (different commands, packages and maps; every hook returns at once while its own
state map is empty). They stay separate jars: each is removed after its test.

## 6. The state-reset rule (the bug class the Monk probe review found)

- ONE timed probe per player. Arming any probe first ENDS the running one (summary line) and then `AbCmds.clear()` resets every probe
  field. `clear()` is GENERATED from the AbState field list, so a new field cannot be forgotten; the harness sets every field to a
  non-rest value and checks `clear()` puts each one back, and checks that arming p2 drops p1's `cancel`, p6 drops p5's `save`, p8 hits
  drop `p8Stun`, p10 drops p9's particle id, a refused plan leaves the state at rest.
- Every hook (chain cancel, lethal save, hit counting, inventory watch) goes through `AbCmds.active()`, which also checks
  `now < modeUntil` - so a probe can never act after its window, even for a player who disconnected (no tick, no summary).
- Leftovers that live outside the state end on their own: P6's effect is 1 s long (re-put every 0.5 s), P8 / P12's Stun is 1-1.5 s,
  P11's block is removed by a scheduled task on its own world thread (and the plugin's shutdown logs any block still out there); P5's
  damage maps are cleared when P5 ends; the global maps are capped at 4,096 entries.
- A world change ends the probe (summary from numbers only) and drops the state.

## 7. Findings

| # | Finding |
|---|---|
| 1 | **The boss stunlock breakout already exists** in SkyyArmory 0.1.9 (`SkyyArmory/build_skyyarmory_0.1.9.py` lines 98-111, rows 657-662, StunRec / Stun 9814-9997, the KnockbackComponent drop 9843-9853) for Monk combo hits. The engine spec section 9 designs a second tracker; it should instead send ability hits into SkyyArmory's counter (a bridge), so one boss has one breakout clock. |
| 2 | SkyyGear removes every speed-tier effect except the weapon's own every second (`GearSpeed.put`, `SkyyGear/build_skyygear_0.2.9.py` lines 10212-10228), so an ability cannot speed up swings by adding a tier effect: spec 10.2 option (b) (SkyyGear reads an "ability haste" bridge value) is the only clean path. P6 confirms it. |
| 3 | P15 is half-answered by code: SkyySkills posts base Mana as `base - EntityStatType(Mana).max` (line 225), so the vanilla 100 should NOT add on top; P15 checks it in game. |
| 4 | P14 is answered by code: SkyyProfiles 0.1.6 saves 6 sections (`SkyyProfiles/build_skyyprofiles_0.1.6.py` line 1789) - runes WILL leak across profiles until it saves -11 / -12. P14 shows it to Skyy. |
| 5 | `IncludesAssetPack: false` is safe: SkyyClasses 0.1.14 is live with it (`SkyyClasses/build_skyyclasses_0.1.14.py` line 4959) - the Monk plan's open item 8 is answered. |
| 6 | P11 has a code-free route on 0.7: the vanilla `SpawnAbilityEntity` interaction spawns a stationary model entity with a lifetime (`research/Hytale-Runes-Research.md` section 5) - the banner can come from its rune's chain instead of server code. |
| 7 | P1's "our own rune" half needs an asset (a rune item), so it cannot be in an asset-free probe; it moves to E2. |
| 8 | Cloud check done: the generated Java was compiled with `javac` against hand-written API stubs (both the P11-built and P11-left-out variants) and the pure logic + the reset rule ran: 55 / 55 pass. That is NOT a javassist build against the real jar. |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Should ability hits (Palm Strike, Shockwave ...) count toward the SAME boss breakout clock as Monk combo hits (one clock per boss)? | [Yes - one shared clock] |
| 2 | If an attack-speed buff (Banner, Blood Frenzy) cannot stack on top of a weapon's speed tier, should the buff move the weapon up to the next faster tier (needs a small SkyyGear change)? | [Yes - next faster tier] |
| 3 | Two short probe sessions: one now (0.6.8, about 12 minutes) and one after Hytale 0.7 is out (about 8 minutes)? | [Yes] |
| 4 | P11 puts a real block in the test world for 10 seconds (removed automatically) and P10 deletes every projectile not yours inside 6 blocks - OK on a test world, alone? | [Yes, test world only, solo] |

## For the local session

| # | Check (UNVERIFIED here - needs `HytaleServer.jar` / `Assets.zip`) |
|---|---|
| 1 | Build `SkyyAbilityProbe/build_skyyabilityprobe_0.1.py` (javassist) on 0.6.8 AND on the 0.7 release jar; run `SkyyAbilityProbe/test_skyyabilityprobe_0.1.py` on both (its E block checks the 0.7 names when the classes exist). Review with the Monk probe review's lens: stale timers / armed flags (section 6). |
| 2 | 0.7 names reached by reflection: `InteractionChainStartEvent` (`getType`, `getContext().getHeldItem()`, `getRootInteractionId` on the event or its context, `setCancelled(boolean)`, `isCancelled`), `InventoryComponent$AbilitySlots` / `$RuneBag` (`getComponentType`, `getInventory`). Fix the strings in the build if the release renamed them. |
| 3 | The CooldownHandler: who owns it (`tools/dev/callers.py` / `reflect.py` on the release jar) and the method that sets a cooldown with a length - then name it in the P3 test step. |
| 4 | NPC targeting: from the P12 log (or `reflect.py` on `NPCEntity` / `Role`), the method that clears or sets a target; wire it into a `p12 clear` in a 0.2 if Skyy wants Awe as "lose target" rather than Stun. |
| 5 | P11: `ChunkUtil.indexChunkFromBlock(int, int)` exists (else the build leaves P11 out and says so); `WorldChunk.setBlock` takes WORLD coordinates outside chunk (0, 0); the air block id is `Empty`. |
| 6 | Whether `TargetUtil.getAllEntitiesInSphere` returns projectile entities (P10 counts "projectiles seen"; 0 with arrows flying = it does not, then scan by the projectile query instead). |
| 7 | The build prints desk lines (particle ids with ring / shield / barrier / bubble ..., ids with "banner", the vanilla rune Cast ids, Mana.json Max, CooldownHandler class names) - give Skyy the ids for steps A8, A10 and B4. |
| 8 | Pin SkyyAbilityProbe 0.1 for ONE session (can share it with SkyyMonkProbe), run section 3 with Skyy, then remove it and record the results in `docs/log/2026-10.md` and the engine spec's section 16. |
| 9 | Fold findings 1 and 2 (section 7) into `research/cloud/Class-Ability-Engine-Spec.md` sections 9 and 10.2 (the cloud did not edit the spec). |
