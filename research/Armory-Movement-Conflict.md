# The Armory vs the Skyy movement protocol - what it writes, and the fix

Research only (2026-10-17, local research agent). No code written. Inputs: `tools/skyymove.py` (protocol v1 source),
`docs/answered/gear.md` 2026-10-09 lock ("yes, lock the armory jump system. we can edit theirs to work with our mods instead of
clashing." -> absorbed at runtime, no shipped edits), `docs/log/2026-10.md` lines 561 / 704 / 787, RESUME NEXT 7, and The Armory
1.23.0 bytecode (jar read-only; classes dumped with the javassist pool from `tools/skyybuild.py`, no scratch files left).

## 1. What The Armory really does (bytecode, 1.23.0)

Two ECS systems in `me.ladypaladra.thearmorymod.stats.systems`, both `EntityTickingSystem`, no ordering dependencies declared, not
parallel. Each ticks EVERY player (PlayerRef + EntityStatMap + MovementManager) EVERY tick - not only when armor is worn.

| System | Reads | Writes (when live differs from target by > 0.0001) | Then |
|---|---|---|---|
| `JumpHeightModifierSystem` | stat `Jump_Height` -> `StatMultiplier.forStat` (1.0 when the stat's max equals its asset max = nobody wears a Jump_Height piece) | `settings.jumpForce = defaultSettings.jumpForce * mult` AND `settings.swimJumpForce = default.swimJumpForce * mult` | `MovementManager.update(packetHandler)` (a packet each time it writes) |
| `GroundMoveSpeedModifierSystem` | stat `Move_Speed` -> same helper | `settings.forwardSprintSpeedMultiplier = default.forwardSprintSpeedMultiplier * mult` ONLY (not baseSpeed) | `update(...)` |

What follows:

1. **The jump system overwrites our jump with the vanilla value on every tick for every player**, mult 1.0 or not. Our applier writes
   `jumpForce = f(bonuses)` once a second (world thread); the Armory resets it within 50 ms and sends its own packet. Our sync sees a
   mismatch every second, strikes 1..5, then rule 4 pauses the player - and the pause covers BOTH baseSpeed and jumpForce, so a
   jump-only fight also kills the speed bonus (talismans, pets, armor Speed). That is the "speed/jump bonus paused" line in the logs.
2. The speed system is NOT a conflict: it writes `forwardSprintSpeedMultiplier`, a different field from our `baseSpeed`. It stacks
   multiplicatively with our baseSpeed bonus (x1.0 for everyone except a wearer of a Move_Speed item). `KNOWN_WRITERS` only names
   `JumpHeightModifierSystem`; nothing breaks, just fix the wording when the table is next touched.
3. Only ONE item in the jar carries the stats: `EngineeringRig` (Move_Speed + Jump_Height Multiplicative 0.2). It is our Zone 2 Light
   MYTHIC set (`tools/pack_drops.py`), so the stat multiplier is 1.0 for everyone until a boss drops it. The fight is therefore about
   the always-on "reset to default", not about the Rig.
4. `swimJumpForce` is also rewritten; the protocol never touches it, so no change needed.
5. UNVERIFIED: `StatMultiplier.fromMaxima(assetMax, valueMax)` reads as `1 + valueMax/assetMax` (1.0 when equal), not
   `valueMax/assetMax`. With the Rig's 0.2 that would be x1.2 only if the engine's Multiplicative modifier makes valueMax = 0.2 x
   assetMax. Needs one in-game number before anything depends on it (test step 3).

## 2. Options

| # | Option | Verdict |
|---|---|---|
| A | **Split the pause per field.** The strike counter / pause in `skyymove.py` `sync()` becomes per field (speed, jump). A jump-only reset pauses jump only; baseSpeed keeps working. | Certain, tiny, no Armory knowledge. Fixes the real damage (lost speed). Jump bonus still lost while the Armory is on. |
| B | **Ride their stat.** When the `Jump_Height` EntityStat asset exists (The Armory loaded), do not write `jumpForce`; instead put one MAX modifier `skyy_move_jump` on the player's `Jump_Height` stat so the Armory's own system produces `default * mult`. Their rig effect and our bonuses then stack in ONE value that their system accepts - nothing fights. Same pattern SkyyGear already uses for `skyygear_ut_hp` (`putModifier(statIdx, key, new StaticModifier(MAX, ADDITIVE, x))`). This is exactly the 10-09 lock: "their armor jump effect still counts, ours too". | **Recommended (with A as the base).** Needs a calibration spike (item 5 above). |
| C | Our own ECS system ordered AFTER theirs that re-writes our jump every tick | Rejected: two `update()` packets per tick per player (40/s), jump visibly flickers on the client. |
| D | Rewrite `MovementManager.getDefaultSettings().jumpForce` so their "default * mult" equals ours | Rejected: the engine rebuilds defaults on world change / respawn / mode change, every other mod (and our Double Jump spec) reads the default as the vanilla base - too invasive. |
| E | Unregister / disable their system at runtime | Rejected: switches off a feature of their mod (PACK.md: react, never override); fragile. |
| F | Switch The Armory off | Rejected: its UT / Mythic sets are the pack plan (Pack-Drops-Spec). |

## 3. Recommended fix: A now + B behind it (one "Movement 2" round)

**What to change.** One file: `tools/skyymove.py` (the shared protocol source). It is baked into 4 jars, so it is a FULL round
(several mods, permissions-free, no saved data): SkyyGear (`GearMove`), SkyySkills, SkyyAccessories (their `MoveSync` copies) and
SkyyCore (`com.skyy.core.move.MoveSync`). Patch scripts `tools/<mod>_<ver>_patch.py` regenerate each; do not hand-edit the generated
builds. No change to the bridge keys (`move:proto` stays 1, the entry format is unchanged - the SkyyPets / other posters need nothing).

**Exact hook** (`skyymove.add_move_sync`, method `sync`):

1. State array `{lastSpeed, lastJump, strikes, tSpeed, tJump, warned}` -> keep it, but strikes are counted per field
   (`strikesSpeed`, `strikesJump`); the 5-strike pause and the one-per-player warning apply to the field that keeps being reset.
   The compare `near(s.baseSpeed, ws)` and `near(s.jumpForce, wj)` are evaluated separately; a pause on jump never stops the
   baseSpeed write.
2. New branch before the jumpForce write: `armoryIdx = EntityStatType.getAssetMap().getIndex("Jump_Height")`. If it is a real
   index (a pack with that stat is loaded - a precise runtime test, better than the plugin-name list), the jump half of the target
   goes into the stat modifier instead of `settings.jumpForce`:
   desired multiplier M = wj / default.jumpForce (our protocol result, rig not included); `EntityStatMap.putModifier(idx, "skyy_move_jump",
   new StaticModifier(MAX, ADDITIVE, A))` with A solved from the Armory formula (A = assetMax * (M - 2) if `1 + max/assetMax` is
   confirmed). Closed loop: the next second read the live `settings.jumpForce` (their system already applied it) and trim A until it
   equals `default * M * rigMult`; three failed trims = fall back to option A (jump yields, ONE warning, speed unaffected).
   M == 1 removes the modifier (`removeModifier`). Written on the world thread like the rest of `sync`.
3. If the Armory is absent the old path is untouched (still the tested one).
4. `KNOWN_WRITERS` row for TheArmory: text becomes "JumpHeightModifierSystem: jumpForce, swimJumpForce (handled by the Jump_Height
   stat ride); GroundMoveSpeedModifierSystem: forwardSprintSpeedMultiplier (no conflict)". The one-time "write directly" warning
   must not fire for it once B is on (otherwise the log keeps the known line Skyy sees every session).
5. Config: one switch in Server Setup (`tools/skyycfg.py`, CONFIG-CONTRACT): `move.armoryJump` = ride (default) / yield / off, times in
   seconds as usual. "No dev gates" rule: ride is ON by default.

**Risks.**
- The stat maths (item 5 in section 1) is read from bytecode only; the loop is calibrated on the live value, so a wrong formula
  costs a fallback to A, not a fight.
- MAX modifier on Jump_Height also changes `maxValue` shown in the stat HUD (it is hidden: `HideFromTooltip` false but not a bar) -
  check no client UI shows it.
- The modifier is saved with the player (like `skyygear_ut_hp`): remove it on leave AND on disable; a rollback floor note:
  rolling back leaves `skyy_move_jump` on a player's stat until a build that knows the key removes it (harmless without the Armory;
  with the Armory it keeps a jump bonus - list it in the deploy floor note).
- Cap: the protocol's own `h0 + 20` jump clamp still applies before the conversion; Armory `Jump_Height` max is 10 (clamped by the
  stat's own Min 1 / Max 10 - ratios above that cannot be reached; our clamp is far lower).
- Four jars change in lockstep (rule: protocol fixes touch every applier). Skip SkyyCore only if it is not an active applier.

**Test steps** (offline smoke server on a COPY of the world, Armory 1.23.0 on, scratch under `tools/dev/scratch/`):
1. Baseline (current jars): join, `/give` a Speed talisman + put Acrobatics levels -> log shows the pause line after ~5 s. Confirms the bug.
2. New jars: same setup -> no "keep being reset" line, baseSpeed shows the bonus in `getSettings()` for 60 s, jumpForce stays at the
   protocol value (log both via the existing `/skills`/debug line or a temporary harness read).
3. Calibrate: with the Armory on and no bonus, read live `jumpForce` vs `default` (must stay equal); give the Rig in Creative and read
   the ratio (answers section 1 item 5: x1.2 or x2.2?).
4. Rig worn + Acrobatics: live jumpForce = default x rigMult x ourM within 0.1 %, no strikes, packet count of `update()` ~1/s not 20/s.
5. Mount / dismount, world change, death: modifier removed or re-applied within 1 s; log has no WARN.
6. Armory removed from the Mods folder (scratch copy): old path works, no stat error.
7. `python tools/ci/crosscheck.py --jar <new jars> --baseline`, `python tools/ci/lint.py`, `python tools/smoke_test.py`.

**Done when:** the three mods' logs show no `keep being reset` / `write ... directly` line with The Armory on, speed bonus
verified, jump bonus verified with and without the Rig.

## 4. If Skyy wants it cheaper still
Ship A alone first (hours, certain): speed returns, jump bonus is simply off while The Armory is on. B follows once the calibration
number from test step 3 exists. Recommended order anyway: A + B in one round, B guarded by the fallback to A.
