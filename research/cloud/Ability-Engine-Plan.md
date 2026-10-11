# Class ability engine plan (Mage + Priest first)

Cloud draft, 2026-10-09. A BUILD plan: it turns the ability designs into small rounds the local session can build, deploy and Skyy can
test in game. Nothing here is built or tested. Sources (read, not changed): `research/cloud/Class-Ability-Spec-Draft.md` (numbers),
`research/Class-Power-Split.md` (Mana / Stamina split), `research/cloud/Ability-Input-Design.md` (keys), `research/cloud/Class-Ability-Shapes.md`
(the 4 shapes per ability), `research/cloud/Class-Ability-Engine-Spec.md` (engine design), `research/cloud/Ability-Probe-Plan.md` (probes +
Skyy's 2026-10-08 answers), `research/cloud/Echo-Options.md`, `research/cloud/Modifier-Pool-Spec.md`, and READ-ONLY the newest build scripts
`SkyyClasses/build_skyyclasses_0.1.14.py`, `SkyyArmory/build_skyyarmory_0.1.14.py`, `SkyySkills/build_skyyskills_0.4.25.py`,
`SkyyHud/build_skyyhud_0.3.17.py` (the SET pins in `tools/deploy_set.py`).

Marks: **VERIFIED** = read in a live Skyy build script (file + line given). **INFERRED** = follows from verified facts. **UNVERIFIED** = needs
`HytaleServer.jar` / `Assets.zip` / the game (all listed in "For the local session").

## 0. Decisions this follows (`docs/answered/classes.md`, newest wins)

| Line | Skyy's decision | What this plan does with it |
|---|---|---|
| 153 | "we decided 4 ability's, 2 active at a time. the 2 you pick are your primary ability's, and work when walking or sprinting. thew other 2 are set to crouch. so crouching uses your alt ability's." | 4 owned; 2 PRIMARY on Ability 2 / Ability 3; the other 2 = ALT on crouch + Ability 2 / 3 (section 3) |
| 154, 155 | up to 4 SHAPES per ability (walking / sprinting / mid-air as a primary, a crouch shape as an alt); cost / cooldown set PER SHAPE; casting during a roll allowed | the shape resolver (3.2); per-shape cost rows (4.3) |
| 156 | "if it doesnt we can just skip mid roll cast" | mid-roll cast is dropped if the press does not reach the server during a roll - no workaround |
| 151 | roll stays on the SPRINT press, never on an Ability key, never touch Skyy's binds | sprint is only read as a state |
| 172 (popup batch 1, "Yes to all") | mid-air casts primaries; keys only - no hotbar ability items for now; swap primaries out of combat; sprint shapes may step ~2 blocks; cost / cooldown per shape; mid-roll = sprint shape; HUD swaps to alts while crouching; 3 owned = 2 primary + 1 alt; **Mage + Priest built first**; **Guardian Spirit passive first**; swappable key order; toggles only change how they turn on | the whole round order (section 8) |
| 173 | "magic uses have more mana, but their spells take more mana and less stamina ... all ability's should be affordable when unlocked" | costs = power split Mage 78 / 22, Priest 73 / 27 (section 4) |
| 174 (popup batch 6) | ability unlock levels "1/10/20/30" (A1 1, A2 10, A2-alt 20, A1-alt 30) | ownership by class level; python check (4.4) |
| 158 | Mage: Starfall + Arcane Beam (A1-alts) and Frost Nova APPROVED; spellbook Page Burst + Levitate fine for now | Mage kit = Meteor, Mana Barrier, Frost Nova, Starfall / Arcane Beam |
| 175 (popup batch 7) | Priest "Lock all three" (Sanctuary + Martyr's Grace, Guardian Spirit) | Priest kit = Sacred Heal, Shield Bubble, Guardian Spirit, Sanctuary / Martyr's Grace |
| 111, 141, 145 | Echo on Meteor, Sacred Heal, Martyr's Grace, Shield Bubble | Echo comes with the modifier round (R9); strength still open (`research/cloud/Echo-Options.md`, default A) |
| 112-114 | Mana Barrier 12 s; damage drains Mana instead of Health (1 Mana per 2 HP); placed dome + Follow; visible but see-through | R3 |
| 142-147 | Sanctuary 12 s / 8 blocks / 5% per s; Martyr's Grace 30 blocks, 75% -15 per jump, party first, Priest = party; Shield Bubble 6 blocks / 12 s, 4 heal pulses; Guardian Spirit = PASSIVE 30-block aura, save at 30%, per-player cooldown 12 s doubling, party-only toggle | R3, R6, R7 |
| 120, 121 + `research/cloud/Ability-Probe-Plan.md` (Skyy 2026-10-08 "1. yes. 2. yes temporarily, 3. wait till 0.7") | stunlock breakout; ONE shared boss breakout clock (ability stuns feed SkyyArmory's live counter); attack-speed buffs bump the weapon one speed tier for now; **the probe session waits for Hytale 0.7** | Frost Nova feeds the live clock (R6); no 0.6.8 probe SESSION - only desk / smoke checks now (section 7) |
| 116, 117 | no void protection on any traversal | no ability here moves the caster except the sprint step / slow-fall; nothing shortens a move for the void |

## 1. Plain words (for Skyy)

- A Mage or Priest gets **Ability 1 (A1) at class level 1**, A2 at 10, the A2-alt at 20 and one of two A1-alts at 30.
- You pick 2 of your abilities as **primaries**: Ability 2 / Ability 3 cast them (Q / E in your binds). **Crouch + the same key** casts
  the other 2 (the alts). How a primary behaves depends on what you are doing: walking, sprinting or in the air.
- Each cast costs Mana AND a little Stamina (Mage 78 / 22, Priest 73 / 27) and starts a cooldown. Every ability is affordable the moment
  you unlock it (checked below).
- **Until Hytale 0.7 (2026-10-12)** abilities are cast with `/cast 1` and `/cast 2`. The real keys come with 0.7's rune system, which
  gives us the two ability keys and a cooldown HUD for free. Building keys on 0.6.8 now would be thrown away 3 days later (Question 1).
- Round 1 is small: the engine + Meteor + Sacred Heal. Each later round adds 1-4 abilities you can test in one sitting.

## 2. Which mod owns abilities, and why

**SkyyClasses owns the ability engine** (as `research/cloud/Ability-Input-Design.md` section 7 and the engine spec section 15 say). No new mod.

| Why SkyyClasses | Where (VERIFIED, `SkyyClasses/build_skyyclasses_0.1.14.py`) |
|---|---|
| it already owns the class per profile and publishes it | ClassStore 1806, publish of `class:<uuid>` / `class:skill:<uuid>` 1858-1872 |
| per-profile files with the stable folder rule | `getDataDirectory().resolveSibling("Skyy_SkyyClasses")` in setup 4910-4914; `ClassCfg.pkey` 969 |
| the class weapon rule a cast must pass | ClassRules 2401, `class:fn:allowed` (AllowedFn 2461) |
| the damage hooks every ability needs | DamageLock = Filter group 2628-2636 (change damage before it lands); PriestHealSys = Inspect group 3895-3905 (react to landed damage) |
| the Priest heal path abilities must reuse | `HealTask.bridgeHeal` 3774, HealBudget 2794, `class:fn:heal` (HealFn 3879), `class:fn:ally` |
| launch records for projectiles (Shield Bubble's "not yours" test) | ShotRec + ShotTrack 2526-2551 |
| its config kit + player switches | `ClassCfg.bridge()` 937, `ClassCfg.regSetting` 958, setup rows 4937-4940 |
| one system per class registration | 4932-4935 |

What the other mods keep:

| Mod | Keeps | Gives the engine (VERIFIED) |
|---|---|---|
| SkyySkills | Mana / Stamina pools, regen, the roll, double jump, combat state | pools: `CLASS_BASE_DEF` 1993, `CLASS_MANA_DEF` 2131, `P25_STA_BASE` / `P25_STA_PER` 2244-2245, `ClassPower.stamFor` 7488-7493; bridges `skill:fn:combat` 18148, `skill:fn:manaregen` 18147, `skill:fn:level` 18136; movement states read on the world thread in AcroSys (`MovementStatesComponent`, 10019, `onGround` / `sprinting` / `crouching` 10048-10061; crouch / jump edges in the air 10514-10519); roll gate `tap(...)` 10216 |
| SkyyArmory | every traversal (blink, hop, Levitate, Monk moves), the weapons' item JSON, the boss stunlock clock | the shared stunlock clock `Stun.onHit` 11638 / `bossHit` 11669 / `noKnock` 11601, rows 695-700 (stun.perPlayer 3, stun.maxPlayers 4, `stun.bossWords` = who is a boss); helpers to copy: `ArmoryTrav.particle` 7141, `effect` 7156, `spawn` 7212, `kind` (enemy / ally / PvP) 7233, `hit` (executeDamage with the caster as source) 7253, `near` (sphere scan) 7269, `Leap.take` (Stamina + Mana spend) 7525, `Leap.vel` 7501, the vanilla Stun on a mob 6880-6890; the Filter-group order pattern `SystemDependency(BEFORE, ArmorDamageReduction)` in ArmoryTuneSys 11751-11763; an Ability1-3 chain read off the player 8810-8827 |
| SkyyHud | widgets | the Combat widget (ids 628 + `IDS.append` 680, defaults / size 657-666, bridge read + vanilla ProgressBar `combatModelU` 1564) = the template for an Abilities widget |
| SkyyTrees | class trees (path nodes) | read later (R9) through `tree:fn:bonus` |

Already shipped that this plan builds on (so nothing is re-done):

| Shipped | Version | What it means here |
|---|---|---|
| Boss stunlock breakout (Monk combo hits) | SkyyArmory 0.1.7+, live in 0.1.14 | Frost Nova's freeze feeds THIS clock through a new bridge (one clock per boss, Skyy 2026-10-08) |
| Monk moves (Pole-Vault, bounds, Rising Strike, Plunge by crouch) | SkyyArmory 0.1.12 + SkyySkills 0.4.22 | crouch in the AIR belongs to movement; abilities never read it (3.2) |
| Wand signature on Ability 1 (marker projectile caught at SPAWN) | SkyyArmory 0.1.14 (`ArmoryTrav.added` 10133, `Rico.marker` 10037) | proves an Ability-key interaction on OUR items reaches the server - the fallback key route if 0.7 runes fail (3.3) |
| Class power split, Mana on hit, in-combat regen 75% | SkyySkills 0.4.25 | the pools the costs are checked against (section 4) |
| Roll on the sprint press | SkyySkills 0.4.23 | mid-roll cast = sprinting shape if sprint is held |
| SkyyKeyProbe 0.2 (Key Tester) | live, TEST-CHECKLIST 53 / 68 not run yet | answers K1-K12 on 0.6.8 whenever Skyy runs it (section 7) |

## 3. Input: 4 abilities, 2 primary + crouch-alt

### 3.1 The key map (exactly as `research/cloud/Ability-Input-Design.md` + lines 153-156, 172)

| Press | Casts | Shape |
|---|---|---|
| Ability 2 (Skyy: Q) | primary 1 | walking / sprinting / mid-air - read at the press |
| Ability 3 (Skyy: E) | primary 2 | same |
| crouch + Ability 2 | alt 1 | its crouch shape (never moves you) |
| crouch + Ability 3 | alt 2 | its crouch shape |
| Ability 1 (Skyy: Mouse 5) | the weapon signature (vanilla / SkyyArmory) - never a class ability | - |
| sprint press | the roll (SkyySkills) - never an ability | - |
| Primary hold / Secondary | the weapon's traversal-attack / block - never an ability | - |

Owned by class level: Lv 1 = A1; Lv 10 = A1 + A2 (both primaries); Lv 20 = + A2-alt (2 primaries + 1 alt; the empty crouch key says
"No alt yet" once); Lv 30 = + one A1-alt (picking A locks out B). Default primaries = A1 + A2, so nothing needs a page until Lv 20+.
Swapping primaries / key order: only out of combat (`skill:fn:combat` = 0), on the Abilities page (R7).

### 3.2 The shape resolver (one pure function, harness-tested)

Read at the PRESS on the world thread, never re-read during the cast:

| Order | Test (MovementStates, the SkyySkills AcroSys read) | Result |
|---|---|---|
| 1 | not onGround for >= `abil.airMin` (0.15 s) | mid-air shape of the PRIMARY (alts cannot be cast in the air - line 172; crouch in the air = movement) |
| 2 | crouching held >= `abil.crouchMin` (0.1 s) | the ALT's crouch shape |
| 3 | sprinting | sprinting shape (note: the client only sets sprinting while W is held - SkyySkills 0.4.25 test 2026-10-09 - so sprint shapes fire when running forward or forward-diagonal) |
| 4 | else | walking shape |

- Needs a tiny per-player state: when crouch went on and when onGround went off (the SkyySkills edge pattern 10514-10519, copied into
  SkyyClasses' own tick - no cross-mod call per tick).
- A shape not built yet = the walking shape (every ability works from its first round).
- Times are SECONDS in Server Setup (PROJECT-RULES 4); the input design's `abil.crouchMinMs` / `abil.airMinMs` become `abil.crouchMin` 0.1 /
  `abil.airMin` 0.15.

### 3.3 Where the press comes from

| Route | Works on | Plan |
|---|---|---|
| `/cast 1` / `/cast 2` (+ admin `/cast <ability> [walk\|sprint\|air\|crouch]` to force a shape for tests) | 0.6.8 and 0.7 | R1 - always on (also controllers / macros). `AbstractPlayerCommand` + `setPermissionGroups("hytale:Adventurer")` like ClassCmd 4760. Never name a command `/abilities` (vanilla 0.7 owns it) |
| **0.7 rune keys** (Use Ability 2 / 3 cast rune line 1 / 2; our 2 primaries mirrored into AbilitySlots 0 and 3; `InteractionChainStartEvent` read + cancel; crouch at the press -> run the ALT instead) | 0.7 only | R4 - the main route (engine spec 3.2). Needs probes P1, P3, P4, P14 first |
| Fallback A: Ability2 / Ability3 on our own Mage + Priest weapons' item JSON -> a marker projectile caught at SPAWN (the wand signature way, SkyyArmory 10133) -> bridge `class:fn:cast` | 0.6.8 (0.7 sends Ability 2 / 3 to the rune instead - `research/Hytale-Runes-Research.md` 2.3) | only if P1 fails on 0.7, or if Skyy wants keys before 0.7 (Question 1). Every Mage / Priest weapon is ours or already overridden: 7 metal wands, 8 ladder staffs, 7 spellbooks (SkyyArmory), Wood / Rotten / Tribal wands (SkyySkills 0.4.24) - the vanilla Grimoire, other vanilla staffs, the broomstick and the Healing Totem need new overrides |
| Fallback B: an entity-level `Interactions` override on the player (Perfect Dodges way) | 0.6.8 | UNVERIFIED (K13); only if A cannot cover a weapon |

## 4. Cooldowns, Mana and Stamina

### 4.1 Pipeline (engine spec section 4, unchanged except the shape step)

gate (class on, alive, not busy) -> ability owned + slot -> class weapon in hand (`ClassRules.allowed`) -> **shape** (3.2) -> cooldown
-> cost (Mana AND Stamina, creative free) -> snapshot -> pay (`subtractStatValue` after a re-read, the `Leap.take` shape, SkyyArmory 7525)
-> run the kind's executor -> count the use (later). Refusals cost nothing, start no cooldown, play the fail sound and send at most one
notification a second ("Ready in 4 s", "Not enough Mana (23)", "Hold a staff or spellbook").

### 4.2 Rules

| Rule | Plan |
|---|---|
| Cooldown | one clock per ABILITY; the cast shape sets its length; kept in memory per profile key (`pkey|ability`) - a relog does not reset it, a server restart does (engine spec Q5 default) |
| Cost | per SHAPE, Mana + Stamina, both must be there; paid at the cast; creative free |
| Delayed damage (Meteor lands 1 s later, zones tick for 12 s) | the weapon check is at the CAST only. **Finding:** SkyyClasses' own DamageLock (2638-2685) cancels any EntitySource damage while the caster holds a non-class item, so a Mage who swaps to food after casting would see their Meteor do 0. Fix in R1: ability damage is tagged (an identity set of the Damage objects the engine creates) and DamageLock skips tagged damage |
| Regen | untouched (SkyySkills keeps regenerating while zones run) |
| Stamina for movement | ability Stamina costs stay 1-2, so the roll (2 Stamina) and a blink (5) stay possible after a cast |

### 4.3 Costs per shape (power -> Mana + Stamina)

Method (python3, `research/Class-Power-Split.md` rule): power = the old Mana-only number in `research/cloud/Class-Ability-Shapes.md`;
Mana = round(power x 0.78 Mage / 0.73 Priest), Stamina = round(power x 0.22 / 4 Mage, 0.27 / 4 Priest), min 1 each (round half up).
The walking-shape results equal `research/cloud/Class-Ability-Spec-Draft.md` section 2 exactly.

| Class | Ability (unlock) | Walking | Sprinting | Mid-air | Crouch (alt) |
|---|---|---|---|---|---|
| Mage | A1 Meteor (Lv 1) | 23 + 2 / 14 s | 23 + 2 / 14 s (Comet) | 23 + 2 / 16 s (Under Me) | 20 + 1 / 14 s (Meteor on Me) |
| Mage | A2 Mana Barrier (Lv 10) | 16 + 1 / 30 s | 16 + 1 / 30 s (Barrier Ahead) | 16 + 1 / 30 s (landing spot) | 14 + 1 / 28 s (Pocket Dome) |
| Mage | A2-alt Frost Nova (Lv 20) | 19 + 1 / 22 s | 19 + 1 / 22 s (Frost Wake) | 19 + 1 / 24 s (Frost Drop) | 20 + 1 / 24 s (Deep Freeze) |
| Mage | A1-alt A Starfall (Lv 30) | 28 + 2 / 18 s | 28 + 2 / 18 s (Star Trail) | 28 + 2 / 20 s (Starfall Below) | 31 + 2 / 22 s (Star Shower) |
| Mage | A1-alt B Arcane Beam (Lv 30) | 23 + 2 / 18 s | 22 + 2 / 18 s (Sweep Beam) | 23 + 2 / 20 s (Beam Down) | 27 + 2 / 22 s (Focused Beam) |
| Priest | A1 Sacred Heal (Lv 1) | 18 + 2 / 14 s | 18 + 2 / 14 s (Running Blessing) | 18 + 2 / 14 s (Beacon) | 20 + 2 / 16 s (Kneel) |
| Priest | A2 Shield Bubble (Lv 10) | 20 + 2 / 24 s | 20 + 2 / 24 s (Bubble Ahead) | 20 + 2 / 24 s (below on landing) | 20 + 2 / 26 s (Around Me) |
| Priest | A2-alt Guardian Spirit (Lv 20) | PASSIVE: 15 + 1 per save (no press; the key says "Passive - always on" once) | - | - | - |
| Priest | A1-alt A Sanctuary (Lv 30) | 26 + 2 / 28 s | 26 + 2 / 28 s (Pilgrim's Path) | 26 + 2 / 28 s (landing spot) | 26 + 2 / 30 s (Inner Sanctum) |
| Priest | A1-alt B Martyr's Grace (Lv 30) | 22 + 2 / 18 s | 22 + 2 / 18 s (Grace in Motion) | 22 + 2 / 18 s (Descent) | 25 + 2 / 20 s (Martyr's Vow) |

### 4.4 Affordable when unlocked (python3)

Pools as SkyySkills 0.4.25 posts them (VERIFIED: Mana = `mana.classBase` + `mana.classPerLevel` x class level, 1993 + 2131; Stamina =
vanilla 10 + `stamina.classBase` + `stamina.classPerLevel` x level, 2244-2245 + `stamFor` 7488). Conservative: the class-balance boost,
Overall Level, Mining Stamina and gear are left out (they only add). Note: `research/Class-Power-Split.md` calls 45 / 42 the "L1" Mana, but
the code adds the per-level part at level 1 too (L0 45 / 42, L1 55 / 47).

| Class | Lv 0 | Lv 1 | Lv 10 | Lv 20 | Lv 30 |
|---|---|---|---|---|---|
| Mage (Mana / Stamina) | 45 / 14.0 | 55 / 14.05 | 145 / 14.5 | 245 / 15.0 | 345 / 15.5 |
| Priest | 42 / 15.0 | 47 / 15.06 | 92 / 15.6 | 142 / 16.2 | 192 / 16.8 |

| Check (every shape of every ability at its unlock level) | Result |
|---|---|
| Mana cost <= Mana pool AND Stamina cost <= Stamina pool | **all 37 shape rows PASS** |
| A1 casts from a full pool at Lv 1 (Skyy's "main ability at least 2 casts") | Meteor 2 (55 / 23; 9 Mana left), Sacred Heal 2 (47 / 18; 11 left) - **exactly 2, PASS** |
| Casts from full at unlock: Mana Barrier 9-10, Shield Bubble 4, Frost Nova 12, Guardian Spirit 9 saves, Starfall / Arcane Beam 7, Sanctuary 7, Martyr's Grace 7-8 | PASS |
| After 2 x A1 at Lv 1: Mage 9 Mana + 10 Stamina, Priest 11 + 11 | a staff blink / wand hop (10 Mana + 5 Stamina) is just out of reach until regen - fine for Lv 1; the roll (2 Stamina) still works |

## 5. Per-ability engine hooks (Mage + Priest, all 10)

Kinds from the engine spec section 5. "0.6.8" = can be built and tested now with `/cast`; "0.7" = needs Hytale 0.7.

### 5.1 Mage

| Ability | Kind | Shapes (what the executor changes) | Hooks reused (VERIFIED) | New / UNVERIFIED | 0.6.8? |
|---|---|---|---|---|---|
| **A1 Meteor** (3.0 H in 4 blocks, 1 s delay; Echo later) | INSTANT, delayed | walking = look point <= 25 blocks; Comet = your spot + 6 forward, 3 blocks; Under Me = waits for onGround (2 s timeout, then where you are), no extra delay; Meteor on Me = on you, 0.5 s, 5 blocks, 2.5 H, caster immune | aim = `ArmoryTrav.look` 7192 pattern; targets = `near` 7269 + `kind` 7233 (enemy / party / PvP); damage = `hit` 7253 (executeDamage, caster = source -> class XP + level scaling); particles `particle` 7141 | DamageLock skip for tagged damage (4.2); falling visual = particles (a vanilla projectile via `spawn` 7212 optional) - particle ids from Assets.zip UNVERIFIED | yes |
| **A2 Mana Barrier** (12 s dome, damage -> Mana 1 per 2 HP, max 100% max Health absorbed) | ZONE | walking = look point <= 8; Barrier Ahead = 6 ahead; landing spot; Pocket Dome = 4 blocks on you, 10 s, 2.5 HP per Mana | conversion in a NEW Filter-group system declared AFTER ArmorDamageReduction (the ArmoryTuneSys dependency pattern 11751-11763); Mana spend `subtractStatValue` | order vs SkyyGear's GearArmorSys / SkyySkills' DefSys (both also AFTER armour, unordered - P5); see-through dome look = a particle ring (P9, Skyy line 114) | yes |
| **A2-alt Frost Nova** (freeze 2 s in 5, then Chill 3 s; 1.0 H) | INSTANT + status | Frost Wake = a 2 x 8 strip behind you 3 s (a short ZONE); Frost Drop = on landing, 6 blocks, 1-block push; Deep Freeze = 4 blocks, 3 s, hits do not break it for 2 s | freeze = the vanilla Stun effect on a mob (`addEffect ... OVERWRITE`, SkyyArmory 6880-6890; Stun.json DisableAll asserted 4784); targets `near` | **stun clock**: every freeze on a boss goes through SkyyArmory's `Stun.onHit` (11638) via a NEW bridge `armory:fn:stunhit` (SkyyArmory change, plain types: the mob's entity UUID or network id + caster UUID + "ability:FrostNova") - Skyy: one shared clock; a vanilla Slow / Chill effect id UNVERIFIED | yes |
| **A1-alt A Starfall** (12 stars over 3 s, 6 blocks, 0.3 H each) | ZONE (timed shower) | Star Trail = stars along your path 3 s; Starfall Below = under you, 7 blocks, 2 s; Star Shower = on you, 16 stars over 4 s, you cannot move | zone tick in the engine's world tick (EntityTickingSystem on Player, `isParallel` false - TravTick 11539 pattern); `near`, `hit`, `particle` | "cannot move" = the Stun effect on the caster (UNVERIFIED that Stun on a player feels right) or a velocity clamp | yes |
| **A1-alt B Arcane Beam** (20 blocks, up to 3 s, ramp 0.5 / 1.0 / 1.5 H per s) | CHANNEL | Sweep Beam = 15 blocks, 2 s, flat 1.5x, you move; Beam Down = aimed below, 12 blocks, slow-fall while channelling; Focused Beam = 25 blocks, 4 s, ramp to 3.5x, you cannot move | line targets = the Rico aim pattern (cone + line of sight, SkyyArmory 0.1.14 header line 8); slow-fall = `Leap.vel` 7501 each tick (the bow / wand apex hang); ends on stun / death / weapon swap / a new cast | a new kind (CHANNEL); slow-fall cost per tick UNVERIFIED | yes |

### 5.2 Priest

| Ability | Kind | Shapes | Hooks reused (VERIFIED) | New / UNVERIFIED | 0.6.8? |
|---|---|---|---|---|---|
| **A1 Sacred Heal** (25% max Health in 9 blocks, Priest 30%, HoT 40% over 4 s; Echo later) | INSTANT heal + snapshot HoT | Running Blessing = a 6-block circle travels with you 2 s, heals each ally once (20% + HoT); Beacon = drops where you land, 10 blocks; Kneel = 1 s channel, +20%, HoT doubled, you stand still | heals through ONE new method next to `HealTask.bridgeHeal` (3774): world thread, alive / creative checks, party split (`class:fn:ally`), Divinity XP, the heal chat lines - but its OWN cap channel (60% per target per cast, no HealBudget) | the HoT = a Buff record ticked by the engine tick; party test = `class:fn:ally` / SkyyParty | yes |
| **A2 Shield Bubble** (6 blocks, 12 s, HP = 100% caster max Health, 4 heal pulses at 75 / 50 / 25 / 0%; Echo later) | ZONE with HP | Bubble Ahead = 6 ahead; below you on landing; Around Me = 5 blocks on you, HP 110% (Follow later) | absorb in the NEW Filter-group system (same one as Mana Barrier, AFTER armour); pulses through the ability heal method; projectile creators from ShotTrack (2526-2551) / `getCreatorUuid`; removal = `buf.removeEntity(ref, REMOVE)` (SkyyArmory `Rico.marker` 10039) | whether hostile projectiles vanish cleanly when deleted (P10); fallback = cancel projectile damage to allies inside | yes |
| **A2-alt Guardian Spirit** (PASSIVE 30-block aura; someone who would die survives at 30%; 15 Mana + 1 Stamina per save; cooldown per saved player 12 s doubling; reset after 30 s out of combat; party-only toggle) | PASSIVE (event aura) | no press (line 172 "Guardian Spirit passive first"); Spirit Call / Spirit Pulse stay parked | the LAST system in the Filter group: `Damage.setCancelled` + `setStatValue(Health, 30%)` (setStatValue VERIFIED in SkyySkills); out-of-combat reset = `skill:fn:combat` (18148); party = `class:fn:ally` | must run after EVERY other reduction (P5); fallback = the engine's `FilterUnkillable` invulnerability (engine spec 10) | yes |
| **A1-alt A Sanctuary** (12 s, 8 blocks, 5% max Health per s, 10% less damage) | ZONE | Pilgrim's Path = 5 ahead; landing spot; Inner Sanctum = 5 blocks on you, 7% per s, 15% less, 10 s | 1 Hz heal pulses through the ability heal method; damage reduction = an aura Buff read by the same Filter system | - | yes |
| **A1-alt B Martyr's Grace** (30 blocks, 75% then -15 per jump, 5 targets, lowest first, party (incl. the Priest) before others; Echo / Chain later) | CHAIN | Grace in Motion = the first target is the ally you look at; Descent = the chain starts from YOU; Martyr's Vow = 1 s channel, 90% first, -20 per jump | candidates = party via `class:fn:ally` + players in range; heals through the ability heal method with its 75% exception cap | - | yes |

## 6. What works on today's 0.6.8 vs what needs 0.7

| Piece | 0.6.8 now | Needs 0.7 |
|---|---|---|
| Engine core, cooldowns, costs, `/cast`, all 10 ability executors, the heal channel, the Filter-group damage systems, particles, Stun on mobs, the stunlock bridge, the HUD widget | yes (every API is used by a live Skyy mod - section 2) | - |
| Shapes (sprint / air / crouch) | the code yes (forced by the admin `/cast ... <shape>`); **feeling them needs keys** - typing a command in the air does not work | the keys (R4) |
| Ability 2 / 3 keys | only via fallback A / B (3.3), thrown away on 0.7 | the rune route (R4): P1, P4, P14 |
| Vanilla ability HUD with cooldown fill | no | P3 (if it fails: the SkyyHud widget stays the display) |
| SkyyClasses shipping an asset pack (rune items + icons) | possible but not needed before R4 (`IncludesAssetPack` False, 4959) | R4 |
| Mana scale: does 0.7's vanilla Mana max 100 change our pools? | - | P15 (SkyySkills posts `base - typeMax`, `Overall.baseMana` 7178 - should be fine) |
| Ability 4 / a third key | no | K14, not designed on (Ability-Input-Design Q4 default) |

Risk: 0.7 may rename APIs the R1-R3 builds use. Mitigation: R1-R3 use only APIs already in live Skyy mods (their build-time `probe_sig` checks fail loudly on a rename), and the whole SET gets the 0.7 port check anyway.

## 7. Probes to run first (only what does not need 0.7)

Skyy 2026-10-08: "wait till 0.7" for the probe SESSION (`research/cloud/Ability-Probe-Plan.md`, answer 3). So nothing below asks Skyy for an
extra play session; they are desk / smoke checks the local session does alone, plus one test already in Skyy's list.

| # | Check | How (no game session) | Decides |
|---|---|---|---|
| D1 | P5 order: can our Filter system declare AFTER `DamageSystems$ArmorDamageReduction` AND after SkyyGear's GearArmorSys / SkyySkills' DefSys (cross-mod class lookup at setup) | read the jar's `SystemDependency` / group order code (`tools/dev/callers.py` / `reflect.py`); smoke-test server start (allowed, `docs/answered/project.md` popup batch 3) logs the system order | Mana Barrier, Shield Bubble, Guardian Spirit correctness (R3, R6) |
| D2 | P7: our `subtractStatValue` vs SkyySkills' 0.2 s regen write | code read of SkyySkills ManaRegen (made at 3756): it must add / subtract, never set the value, or one write could undo the other | R1 cost bookkeeping |
| D3 | DamageLock bypass: does the same `Damage` object we pass to `executeDamage` reach the Filter group | jar read of `DamageSystems.executeDamage` | R1 (4.2 finding) |
| D4 | P15 desk part: `Mana.json` Max on 0.6.8 vs the 0.7 pre-release | Assets.zip read | cost scale |
| D5 | Particle ids for a ring / dome / meteor / frost / holy light; a vanilla Slow / Chill effect id | Assets.zip listing at build time (the SkyyArmory desk-line pattern) | R1, R3, R6 looks |
| D6 | P10 desk part: does `TargetUtil.getAllEntitiesInSphere` return projectile entities | jar read | Shield Bubble route |
| D7 | NPC entity UUID / network id reachable for the stunlock bridge (plain java types only) | jar read (`UUIDComponent` on NPCs?) | R6 Frost Nova bridge |
| K | SkyyKeyProbe 0.2 (LIVE, TEST-CHECKLIST 53): K1-K4, K11, K12 on 0.6.8 - Ability 2 / 3 seen, states at the press, during a roll | Skyy, about 5 minutes, already deployed - NOT required before R1 (Question 2) | the fallback key route + mid-roll cast |

After 0.7 (one session, as Skyy asked): SkyyAbilityProbe P1-P15 (the probe plan's session A + B merged), SkyyKeyProbe K13-K15. Only P1, P3,
P4, P14 (+ K15) block a round here (R4).

## 8. Round split for the local session

Version names assume nothing else lands first (the Monk "Zen" rename also touches SkyyClasses - then shift by one). Each SkyyClasses
version = `tools/classes_<ver>_patch.py` on the previous GENERATED script; harness `SkyyClasses/test_skyyclasses_<ver>.py` with pure-maths
classes (shape resolver, cost split, cooldown clock, chain order, bubble pulses). Deploy order: SkyyClasses before SkyyHud, SkyyArmory before
SkyyClasses when a round adds an `armory:fn:*` bridge.

### R1 - engine core + Meteor + Sacred Heal (SkyyClasses 0.1.15, FULL round: saved data, new system) - 0.6.8

Builds: `Skyy_SkyyClasses/abilities/<pkey>.properties` (owned by class level, eq1 / eq2 = A1 / A2, atomic write like ClassStore); the
pipeline 4.1; memory cooldowns; Mana + Stamina spend; `/cast 1|2`; admin `/cast <ability> <shape>` and `/classadmin abil <player> grant|reset`
(testing above your level); the AbilTick (EntityTickingSystem on Player, world thread); DamageLock skip for ability damage; ability heal
channel; Meteor + Sacred Heal WALKING shapes; bridge `class:fn:abil` (for R2); rows `part.abilities`, `abil.*` (engine spec 13) +
`ab.Meteor.*` / `ab.SacredHeal.*` per shape (Mana, Stamina, cooldown - category abilx). No asset pack.

What Skyy checks:
1. As a Mage at Sorcery 1+ with a staff: `/cast 1` while looking at mobs ~10 blocks away - after 1 s a meteor hits a 4-block area, Mana drops 23, Stamina 2.
2. `/cast 1` again at once: no cast, the fail sound and "Ready in 13 s" (one line).
3. Cast twice from full Mana (wait out the cooldown): the second still works; a third with ~9 Mana left: "Not enough Mana".
4. Hold food / nothing and `/cast 1`: refused "Hold a staff or spellbook". Cast with the staff, then swap to food before it lands: the meteor still hurts.
5. As a Priest at Divinity 1+ with a wand, hurt, party member nearby: `/cast 1` - both healed (you more), a small heal-over-time after.
6. Log out and back in within the cooldown: still on cooldown.
7. Classless or another class: `/cast 1` says you have no ability yet / not your class.
8. Server Setup -> Classes -> Abilities: rows show; change the Meteor cooldown, cast: the new number applies.

### R2 - Abilities HUD widget (SkyyHud 0.3.18, LEAN: one mod, no saved data) - 0.6.8

Builds: widget id `Abilities` appended to `Widgets.IDS` (the Combat widget's pattern, 628 / 680 / 1564): two rows "name  time" + the
vanilla ProgressBar, read from `class:fn:abil` once a second; hidden without the bridge. (Crouch-swap rows come in R5.)

What Skyy checks:
1. Mage: the widget shows "Meteor" (and "Mana Barrier" at Sorcery 10+) with "Ready".
2. `/cast 1`: the row counts down 14 -> 0 with a shrinking bar, then says Ready.
3. HUD editor: move / hide / show the widget like the others.

### R3 - zones: Mana Barrier + Shield Bubble (SkyyClasses 0.1.16, FULL: damage conversion, Health / Mana) - 0.6.8

Builds: the ZONE kind; the new Filter-group system AFTER armour (D1); Mana Barrier walking shape (dome at the look point <= 8, damage to
the Mage inside -> Mana 1 per 2 HP, ends at 0 Mana or 100% max Health absorbed, see-through particle ring); Shield Bubble walking shape
(HP = your max Health, absorbs for allies inside, 4 heal pulses, hostile projectiles removed or their damage cancelled per D6 / P10).

What Skyy checks:
1. Mage (`/classadmin abil` grant or Sorcery 10): `/cast 2` - a faint dome appears where you look; easy to see through, not flashing.
2. Stand inside, let a mob hit you: Health stays, Mana drops (about 1 per 2 damage). Step outside: Health drops again.
3. Run Mana to 0 inside: the dome ends.
4. Priest: `/cast 2` - bubble where you look; mobs hit you inside: the bubble soaks it; at 75 / 50 / 25 % bubble HP and when it breaks you get a heal pulse (4 in total).
5. A skeleton shoots into the bubble: the arrows vanish (or do no damage) and do not hit you.
6. After 12 s both end on their own; no particles left floating.

### R4 - the real keys on Hytale 0.7 (SkyyClasses 0.1.17, FULL: items, several hooks) - after the 0.7 probe session

Builds: SkyyClasses ships an asset pack for the first time: 10 rune items (Mage + Priest only) + icons generated at build time; the 2
primaries mirrored into AbilitySlots 0 / 3 (PlayerReady, equip, profile / class switch); the `InteractionChainStartEvent` hook (cancel on
refusal); crouch held at the press -> cast the ALT; vanilla runes blocked for classed players (engine spec Q2 default); the AbilitySlots
guard (no dragging our runes out, no copies). SkyyProfiles adds rune sections -11 / -12 to the profile snapshot if P14 shows the leak
(a SkyyProfiles round). Fallback if P1 fails: route A of 3.3 (SkyyArmory + SkyySkills item JSON).

What Skyy checks:
1. Mage: Q casts Meteor, E casts Mana Barrier, no typing. The game's ability slots show the two icons (with the cooldown fill if P3 passed).
2. Crouch + Q at Sorcery 20+: Frost Nova's slot (or "No alt yet" before it exists / below 20).
3. A vanilla rune (if you have one): refused with a message.
4. Switch profile: the other profile's abilities show, not this one's.
5. Sprint + Q together: you roll AND the cast fires (if it does not, mid-roll cast is dropped - line 156).

### R5 - shapes for the 4 abilities (SkyyClasses 0.1.18 + SkyyHud 0.3.19, FULL: 2 mods) - needs R4

Builds: the shape resolver live on the keys; sprinting / mid-air / crouch shapes of Meteor, Sacred Heal, Mana Barrier, Shield Bubble (4.3
table; "on landing" shapes wait for onGround, 2 s timeout; sprint shapes place ahead, the ~2-block step only where a shape says so); the
widget swaps its 2 rows to the alts while crouch is held.

What Skyy checks:
1. Run (W + sprint) + Q: the meteor lands ahead of where you run (Comet).
2. Jump + Q at the top: the meteor lands where you land (Under Me).
3. Crouch + key with Meteor set as an alt: it lands on you, you take nothing.
4. Same for Sacred Heal (Running Blessing / Beacon / Kneel), Mana Barrier (Ahead / landing / Pocket Dome), Shield Bubble.
5. Hold crouch: the HUD rows change to your alts; let go: back to the primaries.
6. Sneaking at a ledge + a key never moves you.

### R6 - the A2-alts: Guardian Spirit + Frost Nova (SkyyArmory 0.1.15 + SkyyClasses 0.1.19, FULL: death / saves, 2 mods)

Builds: Guardian Spirit passive (last Filter system, per-saved-player doubling cooldown in memory, 30 s out-of-combat reset, the class-tree
toggle party-only / everyone read later); Frost Nova all 4 shapes; SkyyArmory's new bridge `armory:fn:stunhit` so freezes on a boss count
on the live stunlock clock. Can split into R6a (Guardian Spirit, SkyyClasses only, lean-sized but FULL by rule: saves) and R6b (Frost Nova + bridge).

What Skyy checks:
1. Priest at Divinity 20 (or granted), a party member nearby takes a killing hit: they stay alive at 30% Health; the Priest pays 15 Mana.
2. The same player "dies" again within 12 s: no save; after 12 s yes, then 24 s, 48 s ...; 30 s out of combat resets it.
3. A non-party player dying near you: not saved (toggle default party only). The Priest themself is saved too.
4. Mage at Sorcery 20: crouch + E (Frost Nova as the alt): mobs within 5 freeze 2 s, then move slower.
5. Freeze a boss repeatedly with a Monk friend comboing it: the boss still breaks out at the shared time (3 s per player).

### R7 - the A1-alts + the Abilities page (SkyyClasses 0.1.20, FULL; split per class if large)

Builds: the Abilities page (inline, vanilla look, `tools/skyyui.py`): owned list, pick 2 primaries, swap key order, the A1-alt pick at Lv 30
(A locks out B), all out of combat only; Starfall (shower ZONE), Arcane Beam (CHANNEL + slow-fall), Sanctuary (ZONE), Martyr's Grace (CHAIN),
all 4 shapes each. R7a = page + Priest pair, R7b = Mage pair.

What Skyy checks:
1. `/class` -> Abilities: your 4 abilities; set primaries and order; in combat the buttons are greyed "Leave combat first".
2. At Lv 30 pick Sanctuary: Martyr's Grace shows locked.
3. Sanctuary: a holy zone 8 blocks, allies heal ~5% a second; Martyr's Grace: the lowest party member gets 75%, then the next lower ones less.
4. Starfall: stars rain on the spot for 3 s; Arcane Beam: hold the cast - damage grows over 3 s; in the air it slows your fall.

### R8+ - later (not Mage / Priest specific)

Ability levels by use + modifier points + Echo (Meteor, Starfall, Sacred Heal, Martyr's Grace, Shield Bubble - strength per
`research/cloud/Echo-Options.md`, default A 20-30%), class-tree path reads (SkyyTrees), then Monk + Assassin, Warrior + Berserker, Archer
(the Class-Ability-Shapes build order).

## 9. Server Setup rows added per round (SkyWynn Menu -> Server Setup -> Classes; `tools/skyycfg.py`, times in seconds)

| Round | Rows |
|---|---|
| R1 | `part.abilities`, `abil.input` (command / both / rune), `abil.tick` 0.25, `abil.maxLive` 48, `abil.healCap` 60, `abil.creativeFree`, `abil.cdMessage`, `abil.refuse` 1 s, `ab.Meteor.<shape>.mana / .stamina / .cooldown`, `ab.SacredHeal.<shape>.*` (+ base numbers: damage, radius, delay, heal %) |
| R3 | `abil.maxZones` 2, `barrier.ratio` 2, `barrier.radius`, `bubble.pulse` 8, `ab.ManaBarrier.*`, `ab.ShieldBubble.*` |
| R4-R5 | `abil.shapes`, `abil.shapes.sprint`, `abil.shapes.air`, `abil.crouchMin` 0.1, `abil.airMin` 0.15, `abil.rollCast`; player switches: sprint / air shapes, hints |
| R6 | `gs.mana` 15, `gs.stamina` 1, `gs.health` 30, `gs.baseCooldown` 12, `gs.resetAfter` 30, `gs.radius` 30, `ab.FrostNova.*` |
| R7 | `ab.Starfall.*`, `ab.ArcaneBeam.*`, `ab.Sanctuary.*`, `ab.MartyrsGrace.*` |

No migration in any round (new keys read their defaults when missing).

## Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | Hytale 0.7 is 3 days out and gives us the real ability keys (Q / E) through its rune system. Until then: test the first abilities with typed `/cast 1` / `/cast 2`, or build temporary Q / E on Mage + Priest weapons now (thrown away when 0.7 lands)? | [/cast until 0.7; keys in the 0.7 round] |
| 2 | Your Key Tester (SkyyKeyProbe, TEST 53) is already live and answers which keys reach the server on 0.6.8. Run it now (about 5 min), or leave it for the one 0.7 probe session? | [Leave it for the 0.7 session - it does not block round 1] |
| 3 | To test Mana Barrier / Shield Bubble before you reach class level 10, an admin-only `/classadmin abil <player> grant` that gives all four abilities? | [Yes, admin only] |
| 4 | A Meteor (or any zone) keeps working after you swap away from your staff - the weapon is only checked when you cast? | [Yes - checked at the cast] |
| 5 | A brand-new Mage / Priest (class level 0) has no ability until level 1 (your 1/10/20/30 lock). OK, or own A1 from the start? | [Keep level 1 - it comes in the first fight] |
| 6 | Guardian Spirit costs 15 Mana + 1 Stamina per save, and its doubling cooldown follows the SAVED player (two Priests cannot double the saves)? | [Yes to both] |
| 7 | Cooldowns survive a relog but reset on a server restart? | [Yes, memory only] |
| 8 | On 0.7, vanilla runes (Fireball ...) for players who have a class: blocked? | [Blocked - class abilities only] |
| 9 | Shield Bubble vs arrows: delete hostile projectiles that enter it, or let them through but cancel their damage to allies inside? | [Delete them if it looks clean in the test, else cancel the damage] |
| 10 | Echo strength (needed only at R8): 20-30% on every Echo (option A)? | [A - decide after you feel the base abilities] |

## For the local session

| # | UNVERIFIED (needs `HytaleServer.jar` / `Assets.zip` / the game) |
|---|---|
| 1 | D1-D7 in section 7 (desk / smoke checks; no session with Skyy) before R1 (D2, D3, D5) and R3 (D1, D6) and R6 (D7). |
| 2 | That ability damage tagged by Damage-object identity reaches SkyyClasses' DamageLock unchanged (D3) - else tag by a custom DamageCause or a short per-attacker window. |
| 3 | How SkyySkills credits class XP for a kill made by ability damage while the caster holds a non-class item (its kill XP judges the hand, `SkyySkills/build_skyyskills_0.4.25.py` 6733-6739): a Meteor kill may pay the wrong skill or none. Decide in R1 (e.g. SkyySkills reads a `class:abilkill:<uuid>` hint) - a cross-mod item. |
| 4 | Particle / effect ids (dome ring, meteor, frost, holy light, a Slow / Chill status) - Assets.zip listing at build time (D5). |
| 5 | Whether the vanilla Stun effect on the CASTER (Star Shower, Focused Beam, Kneel "you cannot move") feels right, or a velocity clamp is better. |
| 6 | 0.7: P1 (rune keys + chain event + cancel), P3 (CooldownHandler HUD fill), P4 (AbilitySlots writes survive death / relog), P14 (rune sections leak across profiles - expected FAIL by code: SkyyProfiles saves 6 sections), P15 (Mana max), K13-K15 - one session after 0.7, as Skyy asked. |
| 7 | 0.7 port: re-run every round's build-time `probe_sig` checks against the 0.7 jar before R4. |
| 8 | Fallback key route A (3.3): the vanilla Grimoire, non-ladder vanilla staffs, the Halloween broomstick and the Healing Totem have no Skyy override today - list them from Assets.zip if route A is ever needed. |
| 9 | `acro.doubleJump.trigger` on Skyy's live SkyySkills file (new files default `jump`, `SkyySkills/build_skyyskills_0.4.25.py` 1842; old files may keep `crouch`) - only matters for the Monk later; Mage / Priest crouch casts are ground-only. |
| 10 | Real H (one charged staff / wand shot at the player's level) from SkyyGear's damage curve - the Meteor 3.0 H etc. are model numbers. |
