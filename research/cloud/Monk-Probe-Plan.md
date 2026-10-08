# Monk probe plan (SkyyMonkProbe 0.1: the 13 engine checks before the Monk build)

Cloud draft, 2026-10-08. Turns `research/cloud/Monk-Kit-Spec.md` section 5 into one throwaway probe jar, built the same way as
SkyyGatherProbe / SkyyReelProbe. Draft code (in a pull request, **UNTESTED**: there is no `HytaleServer.jar` in the cloud):
`SkyyMonkProbe/build_skyymonkprobe_0.1.py` + `SkyyMonkProbe/test_skyymonkprobe_0.1.py`. **Never pin or deploy it until the local session
has built it, reviewed it and run its harness.**

## Decisions this follows

| Source | What it locks |
|---|---|
| `docs/answered/classes.md` line 34 | Bo staff charged attack = lunge + Pole-Vault, kick 2x a normal hit (vault only), slower "flowing" fall, skipping bounds on a jump right at landing, more Stamina than a jump |
| `docs/answered/classes.md` line 35 | ONE free mid-air jump after the vault; a timed ground jump takes NO fall damage; further fall = further bound |
| `docs/answered/classes.md` line 39 | Rising Strike: hang at the top for you + knocked-up enemies, air hits fling them, CROUCH near the top = Plunge Punch dragging them down; both Monk falls ~15% slower + 15% less fall damage; the slam = no fall damage, NO Acrobatics XP |
| `docs/answered/classes.md` line 96 | every traversal costs Mana AND Stamina; physical (Monk) = more Stamina than Mana; no cooldowns |
| `docs/answered/classes.md` line 128 | Flowing Form: every hit = 1 combo stack (max 20, each decays 5 s) |
| `research/cloud/Monk-Kit-Spec.md` section 3 | the probe numbers (vault 4.5 up / 7 forward, bound 5 + 0.5 per block cap +8, rise 6 up, hang 1.2 s, plunge 14 b/s, costs) |

## 1. The probe jar in one table

One op-only command `/mprobe` (alias `/monkprobe`, node `skyymonkprobe.admin`, empty permission groups like every probe). Every chat line
also goes to the server log as `[SkyyMonkProbe] ...`, so the log alone carries the results. State is memory only, per player.

| # | Probe | Command | Engine API | Already used by a Skyy mod? |
|---|---|---|---|---|
| 1 | Slow fall | `/mprobe m1 0`, `m1 15`, `m1cap 6` | `Velocity.addInstruction(.., null, Set)` every tick | YES - SkyyArmory Levitate float cap (`SkyyArmory/build_skyyarmory_0.1.7.py` line 6811, via `Leap.vel` line 6372) |
| 2 | Jump at landing | `/mprobe m2 log`, `/mprobe m2` | `MovementStates.onGround / jumping` edges, `Player.getCurrentFallDistance` | YES - SkyySkills `airTrack` (`SkyySkills/build_skyyskills_0.4.20.py` line 9652), `RollSys` (line 10711) |
| 3 | Mid-air jump | `/mprobe m3`, `m3 crouch` | `jumping / crouching / extraJumpsUsed` in the air + a Set | YES - SkyySkills double jump (line 9655 edges, line 9737 the Set); `research/Double-Jump-Spec.md` |
| 4 | Fall damage cancel | `/mprobe m4 0`, `m4 85` | `DamageEventSystem` in the Filter group, cause FALL, `setCancelled` / `setAmount` | YES - SkyyArmory `GrappleFallSys` (line 8620), SkyySkills `AcroFallSys` (line 10573) |
| 5 | Push (lunge / vault / rise) | `/mprobe m5 vault`, `lunge`, `rise` | one `Velocity` Set from the look (`TargetUtil.getLook`) | YES - SkyySkills air jump (line 9737), SkyyArmory hop / leap (line 6372), look (line 6437) |
| 6 | Path sweep, once per enemy | `/mprobe m6` | `TargetUtil.getAllEntitiesInSphere` per tick + `DamageSystems.executeDamage` | YES - SkyyArmory `ArmoryTrav.near` (line 6174), `ArmoryTrav.hit` (line 6152) |
| 7 | Knock up + hang | `/mprobe m7` | NPC `Velocity` Set with the vanilla dagger dash VelocityConfig, every tick | PARTLY - SkyyArmory grapple yank Sets NPC velocity (line 8045) but only to DRAG mobs along; **holding a mob in mid-air is NEW** |
| 8 | Drag down | inside `m7` (crouch at the top) | NPC Set (0, -14, 0) every tick until you land | PARTLY - same API as 7; **dragging mobs down is NEW** |
| 9 | Stamina + Mana costs | `/mprobe m9 on` | `EntityStatMap.subtractStatValue` on Stamina / Mana | YES - SkyyArmory `Leap.take` (line 6396) |
| 10 | Crouch near the top | inside `m7` / `m3` | `MovementStates.crouching` while airborne | YES - SkyyArmory Levitate (line 6661), SkyySkills double jump (line 9653) |
| 11 | No Acrobatics XP for the slam | inside `m7` + `/mprobe xp` | SkyySkills bridge `skill:fn:xp` before / after | YES - published by SkyySkills (line 16861), read by SkyyTrees |
| 12 | Flowing Form aura + combo | `/mprobe m12` | sphere scan every 1 s + a `DamageEventSystem` in the Inspect group (attacker = `Damage$EntitySource.getRef`) | YES - SkyySkills `AcroFallSeenSys` (Inspect group, line 10591), SkyyArmory `ArmoryHitSys` |
| 13 | Vanilla Bo staff behaviour | `/mprobe m13` (+ the build prints a desk read) | `Item.getWeapon`, Assets.zip `Weapon_Staff_Bo_*` json | YES - SkyyGatherProbe reads `getWeapon`; the Bo json read is build-time only |
| - | Slow effect on a mob (extra) | `/mprobe slowfx <EffectId>` | `EffectControllerComponent.addEffect` on an NPC | API YES (SkyyArmory line 6060, on players); **a vanilla slow effect id: UNVERIFIED** |

## 2. Each probe: what it measures, pass / fail, and the fallback

Numbers (python3, g = `PhysicsConstants.GRAVITY_ACCELERATION` = 32, no air drag): launch speed for a height h = sqrt(2 g h): vault 4.5 ->
**16.97 b/s**, rise 6 -> **19.60 b/s**, knock-up 5 -> 17.89 b/s. Ground-to-ground time = 2 vy / g: vault **1.06 s**, so 7 blocks forward =
**6.60 b/s**. Bound: jump 11.8 x sqrt(1.4) = **13.96 b/s**, air 0.87 s, 5 blocks = 5.73 b/s, 13 blocks (cap) = 14.9 b/s. 15% slower fall
= gravity x 0.85 -> fall time x 1/sqrt(0.85) = **x 1.085** (a 4.5-block drop: 530 ms -> 575 ms).

| # | Measures | Pass | Fail -> what the Monk kit does |
|---|---|---|---|
| 1 | Launch 4.5 up; from the top the fall speed is SET every tick to 0.85 x g x t (`m1 15`) or capped (`m1cap 6`). Prints fall ms, the vanilla formula ms, the ratio, Sets sent, server us per tick. Run `m1 0` first as the baseline (air drag). | `m1 15` fall time = baseline x 1.085 (+-10%), looks smooth (no stutter / rubber-band), < 200 us per tick | Use the cap way (SkyyArmory Levitate, already live) with a cap tuned to "feels 15% slower"; if both stutter: drop the slow fall, keep only the -15% fall damage (probe 4) |
| 2 | Every landing: blocks fallen (our top-y + `getCurrentFallDistance`), whether a FALL damage came BEFORE the landing tick, the jump's ms after the landing; an air press is logged as "early". `m2` (no `log`) runs the real bounds. | A jump pressed right at landing shows up 0-100 ms after the landing tick, the fall height is right (+-0.5 block), bounds chain | If the landing tick is hidden (the client jumps straight from the air - the probe says "landing hidden") the bound triggers on that fresh jump instead (built into the probe). If no jump shows at all: trigger bounds by CROUCH at landing (the SkyySkills double jump trigger) |
| 3 | Airborne jump / crouch / `extraJumpsUsed` edges; the first one gives a free air jump (normal jump speed). | `m3`: pressing JUMP in mid-air prints a "jump edge IN THE AIR" and you jump | Expected FAIL for the jump key (the 2026-09-24 double-jump research: `jumping` = rising after a ground jump). Then the free air jump = **CROUCH in mid-air** (`m3 crouch`, the live SkyySkills double-jump trigger, bridge `skill:dj:key`) |
| 4 | `m4 0`: every FALL damage cancelled; `m4 85`: x 0.85. Both amounts printed. | Health unchanged after a 6+ block drop (`m4 0`); 85% of the damage with `m4 85` | Very unlikely (SkyyArmory and SkyySkills do this live). Fallback: a short Health top-up after the landing |
| 5 | Distance, height and air time of each push vs its target (vault 7 / 4.5, lunge 3, rise 1.5 / 6). | Within +-25% of the target, no rubber-band | Tune the numbers (air drag); lunge without leaving the ground fails first -> use the dagger dash VelocityConfig on the player too (SkyyArmory hop). Last resort: per-tick Sets along the path (the SkyyArmory leap rise path) |
| 6 | A vault through mobs: every enemy within 1.5 blocks of you on the way takes 2 x the probe hit, once each. | Each mob in the path hit exactly once; no hit through walls | Widen the radius / sample between ticks (a fast vault moves ~0.2-0.6 blocks per tick); if the per-tick scan costs too much, scan every 2nd tick |
| 7 | Rising Strike: cone 3 x 1.5 in front hit for 1.2 x hit and Set up 17.9 b/s; at the top a 1.2 s hang (you Set to -1 b/s, the mobs too, every tick); your hits on them during the hang fling them 12 b/s along your look. Prints the mobs' lowest / highest y during the hang. | Mobs rise with you, stay within ~1 block during the hang, fly ~6 blocks when hit | **NEW**: if NPC motion fights the per-tick Set (mobs drop or jitter): no mob hang - the mobs only get the knock-up + a slow effect (probe `slowfx`), and the Monk hangs alone |
| 8 | Crouch at the top: you + the knocked-up mobs Set to -14 b/s every tick until you land; slam 1.0 x hit in 3 blocks. Prints how many came down with you. | All knocked-up mobs land within 2 blocks of your height | **NEW**: if mobs do not follow: the slam damages everything within 3 blocks of where you land (no drag) |
| 9 | With `m9 on`: vault 7 + 3, rise 8 + 4, bound 3 + 1 (Stamina + Mana) taken and printed; too little = refused, a bound chain ends. | Values drop by exactly the cost; at 0 Stamina the chain ends with the line | Very unlikely (SkyyArmory does it live). Note: Monk Stamina ~12 -> a vault + 1 bound = 10 (`research/cloud/Monk-Kit-Spec.md` finding 1) |
| 10 | The crouch edge near the top (rising slower than 3 b/s, or in the hang) starts the plunge. | Crouch reliably starts it, within 1 tick | Already live in SkyyArmory Levitate ("crouch ends the hover"); fallback = a second charged-attack press |
| 11 | Acrobatics XP read before the plunge and 2.5 s after the landing. The slam's FALL damage is cancelled, so SkyySkills' `AcroFallSeenSys` (Inspect group, skips cancelled damage) pays nothing. | XP unchanged (PASS line) | **Risk found**: SkyySkills `RollSys` (line 10685) pays ROLL-landing XP straight from the input queue, even when the damage is cancelled - if you are still holding crouch at landing the engine rolls. The probe prints "rolling at landing YES". Fix then: SkyySkills reads a bridge flag "no fall XP for <uuid> until <time>" set by the Monk code (a SkyySkills change) |
| 12 | Every 1 s: enemies within 5 blocks + the scan's cost; every landed hit = 1 combo stack (5 s each, max 20). | Each hit +1, stacks fall off after 5 s, scan < 0.5 ms | Scan every 2 s, or only count hits (no aura scan) |
| 13 | Item in hand + the desk read of both vanilla Bo staffs (their Interactions keys, any "charg" strings). | We know whether the Bo staffs already have a charged attack | If they have none: SkyyArmory overrides the Bo staff's root interaction by id (the bow-leap pattern), like the wands / bows |

### How the bounds handle the fall damage (built into probe 2)

The engine makes a landing's FALL damage from the queued client input BEFORE the input is applied (`DamageSystems$FallDamagePlayers` runs
before `PlayerSystems$ProcessPlayerInput` - asserted in `SkyySkills/build_skyyskills_0.4.20.py` around line 1290 and in the probe harness).
So a jump pressed 0.10 s AFTER landing arrives after the damage. The probe therefore HOLDS every FALL damage during a chain for 100 ms: a
timed bound forgives it, a missed landing re-deals it at 85% (`Damage` FALL with the player as its own source - **NEW**, UNVERIFIED that
the PvP / self filters let it through; fallback: subtract Health directly).

## 3. Test script for Skyy (in game, ~15 minutes)

Before: deploy the probe for ONE session (local session pins it), be op, stand on flat open ground near a 6+ block drop and a few weak mobs
(weak hostile mobs, not traders or pets). Do NOT play normally with it on. Afterwards: `/mprobe stats`, then send the server log.

| Step | Do | Look for |
|---|---|---|
| 1 | `/mprobe kit`, hold the Wood Bo staff, `/mprobe m13` | the lines about the Bo staff; tap / hold attack: any charged move? |
| 2 | `/mprobe m1 0`, wait to land; `/mprobe m1 15`; `/mprobe m1cap 6` | three "M1" lines; did 15 look smooth? |
| 3 | `/mprobe m4 0`, jump off the drop; `/mprobe m4 85`, jump again | Health unchanged, then a small loss |
| 4 | `/mprobe m2 log`, jump around + drop off the edge | landing lines; jump timing lines |
| 5 | `/mprobe m3`, jump and press JUMP in mid-air; `/mprobe m3 crouch`, jump and CROUCH in mid-air | does either give an air jump? |
| 6 | `/mprobe m5 lunge`, `/mprobe m5 vault`, `/mprobe m5 rise` (look forward each time) | distance / height lines (PASS / OFF) |
| 7 | `/mprobe m9 on`, `/mprobe m2`, then jump off the drop and press jump right as you land, again and again | BOUND lines, Stamina going down, "chain ENDED" |
| 8 | `/mprobe m6`, aim the vault through 2-3 mobs | each mob kicked once |
| 9 | `/mprobe m7` facing 1-3 mobs; at the top hit them once, then crouch | knock-up, hang, fling, plunge, "M11: ... PASS" |
| 10 | `/mprobe m7` again, do NOT crouch | the flowing fall line |
| 11 | `/mprobe m12`, fight mobs for 30 s with the Bo staff | combo lines, the aura count |
| 12 | `/mprobe stats`, `/mprobe stop`; send the log + what looked wrong | |

## 4. Probes that rely on APIs no existing Skyy script uses

| What | Probe | Why it is new | Risk |
|---|---|---|---|
| Holding a MOB in mid-air with a per-tick Velocity Set (hang) | 7 | SkyyArmory only Sets NPC velocity to drag a mob along the ground (grapple yank) | NPC motion controller may fight it (drop / jitter) |
| Dragging mobs DOWN at 14 b/s | 8 | same | as above |
| A vanilla slow effect on a mob | `slowfx` | no Skyy mod puts a vanilla effect on a mob; the effect id is unknown here | needs the id from Assets.zip |
| Re-dealing a held FALL damage with the player as its own source | 2 (bounds) | Skyy mods only scale / cancel FALL damage | self-damage may be filtered |
| Melee damage cause | 6 / 7 / 8 | the probe uses `DamageCause.PROJECTILE` (the only non-fall cause any Skyy script names) | the real kit wants the melee cause (UNVERIFIED name) |

Everything else (player Velocity Sets, movement edges, FALL filters, sphere scans, damage through the pipeline, Stamina / Mana costs, the
`skill:fn:xp` bridge) is already used by a live Skyy mod - see the file + line column in section 1.

## 5. Findings

| # | Finding |
|---|---|
| 1 | The spec's vault "7 blocks over about 0.8 s" does not fit a 4.5-block rise: a ballistic 4.5-block vault lands after ~1.06 s. The probe uses the height and distance and measures the time. |
| 2 | Slow fall has no engine field (SkyyArmory asserts that, `SkyyArmory/build_skyyarmory_0.1.7.py` line 3942) - it must be per-tick Sets. The probe tries two ways: analytic speed from the top (independent of the stale client speed) and the live cap way. |
| 3 | Right after a Set the client's reported speed is stale for a few ticks (ping); every "top" check in the probe waits until the client has been seen RISING first - the real kit needs the same guard. |
| 4 | A timed bound pressed after landing comes after the FALL damage (finding in section 2) - the kit must hold the damage, not just cancel it on the jump. |
| 5 | The slam's "no Acrobatics XP" can leak through SkyySkills' roll-landing XP when crouch is still held at landing (probe 11). |

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Is a CROUCH in mid-air OK as the Monk's free air jump if the jump key cannot be seen in the air (like the Acrobatics double jump)? | [yes, crouch - same key as the double jump] |
| 2 | If mobs cannot be held in the air during the Rising Strike hang, should they just get a short slow instead (you still hang)? | [yes, slow instead of hold] |
| 3 | If the 15% slower fall stutters on a laggy link, keep only the 15% less fall damage? | [yes] |
| 4 | Plunge + roll: should holding crouch through the slam landing be allowed to roll (and pay roll XP), or no XP at all as locked? | [no XP at all, as locked - needs a small SkyySkills change] |

## For the local session

| # | Check (UNVERIFIED here - needs `HytaleServer.jar` / `Assets.zip`) |
|---|---|
| 1 | Build `SkyyMonkProbe/build_skyymonkprobe_0.1.py` (javassist) and run `SkyyMonkProbe/test_skyymonkprobe_0.1.py`; the cloud only compiled the generated Java with `javac` against hand-written stubs (no errors) and ran the pure `MpLogic` numbers. |
| 2 | `Damage$EntitySource` / `DamageSystems.executeDamage` / `TargetUtil.getAllEntitiesInSphere` signatures are probed at build time (copied from SkyyArmory) - confirm they pass. |
| 3 | The vanilla Bo staffs' interactions (the build prints an "M13 desk read" line) - charged attack or not. |
| 4 | A vanilla slow entity effect id for `/mprobe slowfx` (search `Server/Entity/Effects` in Assets.zip). |
| 5 | The melee `DamageCause` name (only FALL and PROJECTILE are used by Skyy scripts today). |
| 6 | Whether a FALL `Damage` with the player as its own `EntitySource` passes the damage filters (probe 2's re-dealt fall). |
| 7 | Review, then pin SkyyMonkProbe 0.1 for ONE test session only (like SkyyGatherProbe), run section 3 with Skyy, remove it again. |
| 8 | The jar ships no assets but `tools/skyybuild.py` `manifest()` always says `IncludesAssetPack: true` - check the server accepts an empty asset pack (else add one harmless lang line). |
