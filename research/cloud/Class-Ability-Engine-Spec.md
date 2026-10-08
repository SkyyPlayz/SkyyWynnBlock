# Class ability ENGINE spec - how abilities are cast and run in SkyyClasses

Cloud draft, 2026-10-08. Paper design; nothing built, nothing tested. It answers "how does an ability get CAST and RUN", not "what
are the numbers" (those stay in `research/cloud/Class-Ability-Spec-Draft.md` and `research/cloud/Modifier-Pool-Spec.md`).
It is meant to be built next by the local session, in small versions (section 15).

Marks: **VERIFIED** = read in our own build scripts or in a spec that verified it in the game jar (source named). **INFERRED** = follows
from verified facts. **UNVERIFIED** = needs HytaleServer.jar / Assets.zip / the game (all listed in section 16).

## 0. Decisions this follows (docs/answered/classes.md, newest wins)

| Line(s) | Decision | What the engine must do |
|---|---|---|
| 31 | 2 class abilities equipped (the two rune lines), built on runes, 2 modifiers each, later 3 saved loadouts | two cast inputs, a loadout slot pair per profile |
| 47, 54 | 5 designed per class, 4 owned, 2 equipped; A1 -> A2 -> A2-alt -> one of two A1-alts (locks out the other) | owned / equipped / locked-out data per profile |
| 50, 51 | abilities LEVEL BY USE; levels give points for that ability's own modifier tree; 2 modifiers equipped; no doubling; shared pool, levelled per ability | use counter + modifier levels per ability per profile |
| 52, 54 | class-tree nodes change HOW an ability works (Wynncraft paths) | the engine reads class-tree nodes (SkyyTrees) at cast time |
| 53, 113 | Shield Bubble "moves with you" = Follow modifier; Mana Barrier = placed dome + Follow | placed zones with an optional follow anchor |
| 55 | Ricochet = projectiles only; Chain = effects only | two different code paths |
| 96 | traversal costs Mana + Stamina (2 : 1 magical); no new traversal cooldowns | traversals stay in SkyyArmory; abilities are a separate system |
| 104, 105 | every weapon's charged hold = its traversal AND its attack | right-click / hold are TAKEN - abilities need another input |
| 111, 118, 123, 124, 139, 141, 144, 145, 132 | Echo on Meteor, God Killer, Palm Strike, Still Water, Whirlwind, Sacred Heal, Martyr's Grace, Shield Bubble, Warlord's Banner | Echo is data per ability (section 8) |
| 112-114 | Mana Barrier 12 s, damage drains Mana (1 Mana per 2 HP), ends at 0 Mana; faint see-through dome | a damage-conversion zone |
| 120, 121 | combo hits may stunlock; bosses / mini-bosses break out after 3 s x players stunlocking (cap 4 = 12 s) | stunlock tracker (section 9) |
| 127 | Enrage: targets picked ONCE at activation (players 8, party 16), buff stays - NOT an aura | snapshot buffs |
| 128 | Flowing Form: 1 stack per hit, max 20, each stack decays 5 s after gained | per-stack timestamps |
| 129, 130, 136-138 | Blood Frenzy: TOGGLE, max 25, 6 s decay per stack, Mana + Stamina per attack (hit or miss) + small drain, regen continues; allies by AURA (8 / party 16, only while inside); Floor modifier (min 5 / 10, never with Duration+) | toggle + aura + per-swing cost |
| 132-135 | Warlord's Banner: 30 s, 12 blocks, tiers 8 / 12 / 16 % damage + defence + attack speed; kills extend (+1 / +3 / +5 s, cap 60 s); 40 Mana upfront, regen continues; falls at end OR when the Berserker leaves range | placed zone with owner leash + kill hook |
| 142 | Sanctuary 12 s, 8 blocks, 5% max Health per second, 10% less damage | heal + damage-reduction zone |
| 143, 144 | Martyr's Grace: range 30, 75% first heal, -15 per jump (5 targets), lowest Health first, party (Priest counts as party) before others; Chain modifier up to 10 targets / 7% drop | chain heal |
| 145, 146 | Guardian Spirit = PASSIVE 30-block aura: someone who would die survives at 30% if the Priest has the Mana; per-player cooldown 12 s doubling, reset after 30 s out of combat; tree toggle party-only (default) / all players | lethal-damage hook |
| 147 | Shield Bubble heal pulses at 75 / 50 / 25 / 0 % bubble HP (8% max Health each) | HP-threshold events on a zone |
| 116, 117 | NO void protection on traversals | nothing here moves the player, so no void rule applies to the caster; pushing MOBS is a separate question (note below) |

Note: `research/cloud/Modifier-Pool-Spec.md` 2.1 (refreshed 2026-10-08) keeps "Knockback+ / Pull never push a mob into the void" as
its default and asks Skyy, because lines 116-117 cover traversals (player moves), not mobs. The engine supports both with one row
(`abil.mobVoidStop`, default true = that spec's default) - Question 6.

## 1. Plain words (for Skyy)

- You press one of **two ability keys**. On Hytale 0.7 (Chapter 1, out 2026-10-12) these are the game's own **"Use Ability 2 / 3"**
  rune keys, and your two equipped abilities show in the game's own ability HUD slots. Until then (and as a backup) `/cast 1` and
  `/cast 2` work, and you can bind them to a key with a macro.
- The server checks: right class, a class weapon in hand, the ability is equipped, it is off cooldown, you have the Mana / Stamina.
  Then it pays the cost, starts the cooldown and runs the ability.
- Every ability is one of nine **kinds** (instant, snapshot buff, aura, toggle, placed zone, chain, passive, next-hit charge,
  channel). One engine runs each kind; an ability is just a row of numbers + its kind. That is what keeps 35 abilities buildable.
- **Echo** = "run me again 1 s later, weaker" - written as data, so one switch gives any ability its echo.
- Cooldowns are kept in server memory (a relog does not reset them); your owned abilities, ability levels and modifier points are
  saved per profile.
- Cooldowns show on the game's ability HUD if Hytale lets the server fill it, otherwise in a new SkyyHud **Abilities** widget (like
  the Combat widget).

## 2. What exists today (READ-ONLY survey of the code)

SkyyClasses = `SkyyClasses/build_skyyclasses_0.1.13.py` (SET pin 0.1.13; a running local round classes014 makes Monk + Assassin
playable, so the engine starts on the version after that - section 15). It has **no ability, Mana or Stamina code at all** today.

| Piece | Where | What it gives the engine |
|---|---|---|
| Class per profile, published | ClassStore (lines 1731-1927), bridge `class:<uuid>` / `class:skill:<uuid>` (1792-1797) | who is which class; per-profile file `Skyy_SkyyClasses/players/<pkey>.properties` (header 233-240) |
| Class weapon rule | ClassRules (2326-2378), `class:fn:allowed` (4848) | "holding a class weapon" check for casting |
| Projectile launch records | ShotTrack RefSystem on projectiles, SPAWN / remove (2451-2551) | who launched a projectile with what - reuse for ability projectiles |
| Damage filter hook | DamageLock = DamageEventSystem in `DamageModule.get().getFilterDamageGroup()` (2553-2617) | the place to change damage BEFORE it lands: buffs, Mana Barrier, Shield Bubble absorb, Guardian Spirit |
| Damage inspect hook | PriestHealSys in `getInspectDamageGroup()` (3820-3881) | the place to react to damage that LANDED: combo stacks, use counting, Blood Frenzy hits |
| Heal path | HealTask.bridgeHeal (3696-3745): Priest check, world thread, ready / alive / creative, party split, cap, HealBudget (2719), addStatValue, chat lines, Divinity XP | ability heals reuse this with their own cap channel |
| Bridges for others | `class:fn:heal`, `class:fn:ally` (3788-3815; put at 4851-4852) | party / ally test; heals from SkyyArmory |
| Timers | ONE scheduler tick: ClassTick every 2 s on `HytaleServer.SCHEDULED_EXECUTOR` (4615-4640, scheduled at 4861) | too slow and off the world thread for abilities - the engine needs a world-thread tick |
| Systems registered | 4853-4860 (commands, PlayerReady / Disconnect, 4 ECS systems) | one registerSystem per class (AGENT-BRIEF rule) |
| Config kit | ClassCfg (786), the kit block (1176), player switches regSetting (4862-4865), CfgPub (4866) | Server Setup -> Classes rows; player switches |
| Assets | `m["IncludesAssetPack"] = False` (line 4884) | ability rune items / effects need SkyyClasses to ship an asset pack for the first time (section 3.3) |

Other mods the engine leans on:

| Mod (live build) | What | Where |
|---|---|---|
| SkyySkills 0.4.20 | Mana is the engine's own `Mana` stat; max Mana posted as modifiers (base by class, per class level: Priest 5, Mage 10); regen pulse every 0.2 s incl. 50% in combat; `skill:fn:combat` (ms left in combat) and `skill:fn:manaregen` (regen % registry); `subtractStatValue` / `setStatValue` probed; AcroSys = EntityTickingSystem on Player | `SkyySkills/build_skyyskills_0.4.20.py` header 33-65, 94-133; probe list 1082; AcroSys 3423; ManaRegen 3490; bridges 16869-16870 |
| SkyySkills double jump | the server sees **crouch** and **jump** movement-state edges in mid-air (`MovementStates.crouching` / `.jumping`) | header 575-591 |
| SkyyArmory 0.1.7 | ALL traversals (blink, hop, grapple, kunai, Levitate, Monk moves; Shadow Step queued in armory018); TravTick = EntityTickingSystem on Player, `isParallel` false, per-world lists of trails / orbs, `trav.maxLive` 64; sphere scan `TargetUtil.getAllEntitiesInSphere` | `SkyyArmory/build_skyyarmory_0.1.7.py` 230-245, 4082-4084, 6168-6176, 8678-8680 |
| SkyyArmory click trick | a right click is seen by the server as an `ApplyEffect` marker effect polled each tick (`EffectControllerComponent.hasEffect`) - the Grapple Bolt way | `research/Grapple-Bolt-Spec.md` 2.1 |
| SkyyHud 0.3.16 | widgets; the Combat widget reads a bridge Function from memory on the 1 s HUD tick and drives a vanilla ProgressBar | `SkyyHud/build_skyyhud_0.3.16.py` 152-182 |
| SkyyAccessories | movement speed through the movement protocol, source `accessories.talismans`, % layer (LIVE) | `research/Booster-Accessories-Spec.md` table line 117 |
| SkyyGear 0.2.9 | attack speed = weapon speed TIERS chosen by hidden status effects in replaced Primary roots (discrete factors 1.4 / 1 / 0.7 / 0.5) | `SkyyGear/build_skyygear_0.2.9.py` 77-100 |
| SkyyTrees 0.3.2 | `tree:fn:bonus.apply(Object[]{UUID, "Tree.Node"})` -> Double, `tree:fn:level` -> Integer | `SkyyTrees/build_skyytrees_0.3.2.py` 162-163, 4797 |
| SkyyParty | `party:fn:members` apply(UUID) -> String[] | its build, PartyFn |
| SkyyMobs 0.1.4 | `mob:fn:info` (level, base HP, multipliers); **no elite / boss flag yet** ("NOT IN 0.1: elites ... boss") | `SkyyMobs/build_skyymobs_0.1.4.py` 46-51, 376 |

How abilities differ from what fires today: traversals and quick shots are **weapon interactions** (client-predicted chains in item
JSON, caught server-side at projectile SPAWN or by a marker effect). Abilities have no weapon slot left (lines 104-105: left = attack,
hold = traversal, right = block / grapple / Bo block), so they need their own input (section 3).

## 3. Input: how a cast is started

### 3.1 Options

| # | Input | Evidence | Verdict |
|---|---|---|---|
| I1 | **0.7 rune keys "Use Ability 2 / 3"** (InteractionType Ability2 / Ability3 cast rune line 1 / 2 from the AbilitySlots section -11) | VERIFIED in 0.7.0-pre.4 (`research/Hytale-Runes-Research.md` 2.3: `InteractionContext.forInteraction`, `InteractionChainStartEvent` cancellable with `getType()` and the rune as held item); keys / HUD UNVERIFIED in game; 0.7 ships 2026-10-12 (`research/cloud/Hytale-0.7-Watch.md`) | **RECOMMENDED main input** - it IS Skyy's "built on runes" lock (line 31), gives two keys, a HUD with cooldown fill and fail sounds for free |
| I2 | `/cast 1`, `/cast 2` (player command) | command pattern VERIFIED (HANDOFF section 3) | **always on** - testing, 0.6.8, controllers, macro-bound keys |
| I3 | Ability2 on every item via `Interactions.setInteractionId` on the player (Perfect Dodges way) | VERIFIED API (`research/Grapple-Bolt-Spec.md` 2.5 R4) | no on 0.6.8: Ability2 is a weapon slot ("Q" in Skyy's bindings); on 0.7 I1 replaces it anyway |
| I4 | Right-click / hold with a class weapon | taken by block / grapple / traversals (lines 103-105) | no |
| I5 | Crouch + click combos (Wynncraft R-L-R) | crouch edge VERIFIED server-side (SkyySkills DJ); click edges need the marker-effect trick per weapon | no - class plan says "ability keys, no click combos"; laggy (ping + 1 tick) |
| I6 | A hotbar "ability item" | VERIFIED pattern (right-click item -> interaction) | no - costs a hotbar slot and a weapon swap |
| I7 | SkyWynn Menu button | VERIFIED pages | no for combat (too slow); YES for equipping (section 11) |

### 3.2 The rune route in detail (I1, on 0.7)

1. **One rune item per ability**: `SkyyAbility_<Class>_<Ability>` (35 items), `Ability { Slot: Primary, Cast: Root_SkyyAbility_Cast,
   Cost: 0, CostType: None, Cooldown: 0.25, Weapons: [<the class's weapon families>], Tags: [class.<name>] }`, icon
   `Common/Icons/Abilities/SkyyAbility_<...>.png` generated at build time. Cost / cooldown stay in OUR engine (they change with levels,
   modifiers, tree nodes and Server Setup rows; a rune's numbers are asset constants) - UNVERIFIED alternative in 3.4.
2. **The cast root is one tiny chain**: `ApplyEffect SkyyAbility_Cast_1` (line 1) / `_2` (line 2) - an invisible 0.2 s marker effect,
   the Grapple Bolt click trick. Root uses `RequireNewClick: true` (one cast per press, VERIFIED vanilla rune roots).
3. **Hook, preferred**: an `EntityEventSystem<InteractionChainStartEvent>` (cancellable, VERIFIED in pre.4): `getType()` Ability2 /
   Ability3 + the rune id -> queue a CastReq; when our checks fail we **cancel the event** (the server sends the client a cancel packet,
   VERIFIED `InteractionManager.syncStart`) so no animation plays. **Fallback hook**: the AbilTick polls the two marker effects (3.1
   evidence) and removes them when seen.
4. **Slots are a MIRROR of our data**: the engine writes the two equipped runes into AbilitySlots slots 0 and 3 (section -11) on
   PlayerReady, on equip, and on a profile / class switch; slots 1-2 / 4-5 (modifier rune slots) stay EMPTY in v1 (our modifiers are
   levelled data, not items - 3.4). An `InventoryChangeEvent` guard on the AbilitySlots / RuneBag components puts the mirror back if a
   player drags a Skyy rune out, and deletes any `SkyyAbility_` stack found outside section -11 (count before / after).
   SkyyProfiles needs NO change for our runes (we rewrite them per profile), but section -12 (the vanilla rune bag) still leaks
   across profiles (`research/Hytale-Runes-Research.md` 4.4) - a SkyyProfiles item, flagged in section 16 (P14).
5. **Vanilla runes**: a player WITH a class casting a non-Skyy rune -> cancelled + the weapon-lock style popup [default, Question 2].
6. **Do not name a command `/abilities`**: vanilla 0.7 owns it (opens the bench, VERIFIED pre.4).

### 3.3 Before 0.7 / without runes (I2)

`/cast <1|2>` (+ `/cast <ability name>` for testing, admin only): `AbstractPlayerCommand` with `setPermissionGroups(new String[] {
"hytale:Adventurer" })` on the command and both usage variants (COMMAND RULES 1-2). It queues the same CastReq. The engine never
depends on I1, so everything in sections 4-13 can be built and tested on 0.6.8. Row `abil.input` = `both` (rune + command) /
`command` / `rune`.

### 3.4 Engine-side cooldown vs vanilla rune cooldown (UNVERIFIED choice)

| Way | + | - |
|---|---|---|
| A: our cooldown only (default) | live rows, level / modifier / tree changes, exact | the vanilla HUD fill shows only the 0.25 s anti-spam unless B works |
| B: also arm the engine's `CooldownHandler` (key = the rune's Cast root id) with our length | the vanilla HUD fill matches | needs: the handler reachable from a plugin, a code-set cooldown synced to the client - both UNVERIFIED (probe P3) |
| C: inject our numbers into `ImpactModifiers.CAST_SNAPSHOT` | vanilla cost / cooldown maths | INFERRED only, system order and client prediction unknown; skip |

Plan: build A; if probe P3 passes, add B (one call after our cooldown arms). The SkyyHud widget (section 12) is the fallback.

## 4. The cast pipeline (world thread)

```
input (rune event / marker effect / /cast)  ->  CastReq{uuid, line 1|2, at}  ->  AbilTick (same tick, world thread)
  1 gate     class enabled, part.abilities on, profile not busy (profile:busy), alive, ready, not stunned by us, world not disabled
  2 slot     the line's equipped ability exists, is owned, its kind allows a press (passives: no press)
  3 weapon   main hand passes ClassRules.allowed for the player's class AND is a weapon (vanilla rune rule "must hold a Weapon")
  4 toggle   a toggle that is ON -> switch OFF now (no cost), start its cooldown, done
  5 cooldown now < readyAt[pkey][ability] -> refuse (fail sound + "Ready in 4 s" at most every 1 s)
  6 cost     Mana >= cost x Efficiency, Stamina >= stamina cost; creative = free (vanilla rune rule)
  7 snapshot CastSnap = { ability, level, 2 equipped modifiers + levels, tree nodes read now, resolved numbers }
  8 pay      EntityStatMap.subtractStatValue(Mana / Stamina); arm cooldown (readyAt = now + cd)
  9 run      the kind's executor (section 5) with the snapshot; schedule the Echo if equipped (section 8)
 10 count    the "use that did something" check runs when the effect reports a hit / heal / absorb (section 7.3)
```

- Refusals cost nothing and never start a cooldown. A cast that does nothing still costs (the use just does not count).
- Every number used later (ticks, pulses, echo) comes from the CastSnap, so a tree or row change mid-effect never changes a running
  effect (same rule as SkyyArmory's launch records).
- Latency: rune key -> event is server-side at once; the effect starts on the next world tick (~1 tick + ping, like the wand hop).

## 5. The nine ability kinds (one executor each)

| Kind | Abilities (locked + proposed) | Executor in one line |
|---|---|---|
| **INSTANT** | Shield Shockwave, Iron Chain, Palm Strike, Cyclone Kick, Earthsplitter, Frost Nova, Sacred Heal, Meteor (1 s delayed impact), Toxin vial | resolve targets now (cone / line / sphere / single look target) -> damage / heal / status; Meteor = a delayed INSTANT |
| **SNAPSHOT BUFF** | Enrage, Rallying Guard, Bulwark Stance, Unbreakable, Cloak | pick targets ONCE at activation (Enrage: players 8, party 16 - line 127), attach a Buff record to each for its duration; no re-scan |
| **AURA** | Flowing Form (enemies Awed in 5 blocks), Blood Frenzy allies, Guardian Spirit (30 blocks) | membership re-checked every aura tick; leaving = losing it at once (Blood Frenzy: "only while inside", line 130) |
| **TOGGLE** | Blood Frenzy (line 129) | ON until pressed again or a resource runs out; per-attack cost + small drain; cooldown starts when it turns OFF |
| **ZONE** (placed) | Mana Barrier, Shield Bubble, Sanctuary, Warlord's Banner, Arrow Rain, Hunter's Net, Starfall, Toxin cloud | an effect instance at a point (or following the caster with Follow); ticks; can have HP, a leash and end rules |
| **CHAIN** | Martyr's Grace, (Chain modifier on Iron Chain / Toxin / Guardian Spirit) | build the ordered target list once, apply with a per-jump drop, instant |
| **PASSIVE** | Guardian Spirit (line 145) | nothing on a press; the engine checks it in a damage hook while equipped |
| **CHARGE** (next hit) | Explosive Arrow, God Killer, First Strike, Wind-Strike-like | arm a Charge record; the damage hook spends it on the next qualifying hit (window seconds) |
| **CHANNEL** | Arcane Beam, Rapid Fire, Whirlwind (3 s spin), Still Water (10 s stance) | runs each tick for its time; ends early on stun / death / a new cast / weapon swap |

Engine records (memory only):

| Record | Fields |
|---|---|
| `Fx` (zone / aura / toggle / channel instance) | id, kind, ability, ownerUuid, ownerPkey, worldName, anchor (x, y, z) or follow=true, radius, startAt, until, nextTickAt, tickSec, snap, state (hp, pulsesDone, stacks[], kills, echo=false/true) |
| `Buff` (on a player) | sourceAbility, casterUuid, kind (dmg, def, aspd, mspd, dr, ward), value, until, fromFx (for aura buffs: refreshed each aura tick, expires 0.6 s after the last refresh) |
| `Charge` | ability, ownerUuid, until, multiplier, condition (boss / backstab / charged shot) |
| `Stacks` | per owner: a ring of gain times (Flowing Form 20, Blood Frenzy 25); count = gains newer than now - decay; Floor = max(count, floor once reached) |

Lists: one per world (`AbilWorld`), capped by `abil.maxLive` (48); per player at most `abil.maxZones` (2) placed zones (a 3rd ends
the oldest), 1 toggle, 1 passive. Over the world cap: refuse the cast with a message (never silently drop a paid cast).

## 6. Auras vs activation targeting (the rule)

| Rule | When | Abilities |
|---|---|---|
| **Picked at activation** | buff copied onto each target at cast; it stays wherever they go; a target joining later gets nothing | Enrage (line 127), Rallying Guard, Sacred Heal's HoT, Martyr's Grace |
| **Continuous aura** | membership every `abil.auraTick` (0.25 s); a Buff with `fromFx` set expires 0.6 s after the last refresh, so leaving = off within about 0.6 s | Blood Frenzy (line 130), Flowing Form Awe, Sanctuary, Warlord's Banner, Mana Barrier, Shield Bubble |
| **Event aura** | no tick at all: checked only when the event happens | Guardian Spirit (only on lethal damage) |

Who is an ally / a target (one function, reused): self; **party** = `class:fn:ally` (SkyyParty); **players in range** = any non-hostile
player in the same world; **hostile** = an NPC with an EntityStatMap that is not a pet / ally, or a player only when the world's PvP is
on AND not in your party (the SkyyArmory rule, `research/Magic-Traversal-Spec.md` 1.3 + 2.7, VERIFIED engine filter on top).
Ranges with two values (Enrage / Blood Frenzy: players 8, party 16) test party first, then the shorter range.

## 7. Bookkeeping: cooldowns, Mana / Stamina, uses

### 7.1 Data model

| Data | Where | Saved? | Key |
|---|---|---|---|
| owned abilities, the A1-alt pick (A or B, locks the other), equipped line 1 / 2 | `Skyy_SkyyClasses/abilities/<pkey>.properties` | yes, per profile (PROFILES-CONTRACT rule 1) | `own=A1,A2,A2X`, `alt=A`, `eq1=A1`, `eq2=A2` |
| uses that counted per ability (-> level) | same file | yes, batched (dirty flag, flushed every 30 s + on quit / profile switch; atomic tmp + move like ClassStore) | `use.<ability>=137` |
| modifier levels + which 2 are equipped | same file | yes | `mod.<ability>.<modifier>=3`, `mods.<ability>=Power,Echo` |
| tree path nodes | SkyyTrees (owner) | SkyyTrees saves them | read via `tree:fn:bonus` at cast |
| loadouts (later, line 31) | same file | yes | `lo.<n>=A1,A2;mods...` |
| cooldown ready-times | memory `CD[pkey + "|" + ability]` = absolute ms | **no** (kept for the JVM life, so a relog does NOT reset; a server restart does) | pkey, so profile 2 has its own cooldowns |
| Guardian Spirit save counters | memory `GS[targetUuid]` = {saves, lastSaveAt, readyAt} | no | the TARGET (Question 3) |
| toggle ON state, stacks, Fx, Buffs, Charges | memory | no - a relog / world change / profile switch ends them | owner uuid |
| Mana, Stamina | the engine's own stats (EntityStatMap) | the engine saves them | - |

Rationale for not saving cooldowns: the longest cooldown is 45 s (God Killer), a relog takes longer than most, and keeping them in
memory across a reconnect closes the relog trick anyway. No new data folder: `abilities/` sits next to `players/` (stable
`resolveSibling("Skyy_SkyyClasses")` rule, HANDOFF section 2).

### 7.2 Mana / Stamina rules

| Rule | Detail |
|---|---|
| Spend | on the world thread, `subtractStatValue` after re-reading the value (never below 0); creative = free |
| Regen | untouched: SkyySkills keeps regenerating (also while a toggle / zone runs - lines 129, 135) |
| Drains (Flowing Form, Blood Frenzy small drain) | taken on the aura tick as `rate x elapsed`; when the stat cannot pay, the effect ends (toggle: cooldown starts) |
| Per-attack cost (Blood Frenzy) | each SWING, hit or miss (line 129): on 0.7 count `InteractionChainStartEvent` of type Primary while the toggle is on (UNVERIFIED that Primary chains raise it - probe P2); fallback = count damage events only (misses free) and say so in the row help |
| Mana Barrier conversion | damage hook: `mana = dmg / ratio`; pay what Mana allows, the rest stays Health damage; Mana 0 -> the dome ends |
| Guardian Spirit | Mana paid at the save; not enough = no save |
| Physical classes' Mana pool | still open (`research/cloud/Class-Ability-Spec-Draft.md` 1.2, Q1 there): every cost row has a Mana AND a Stamina column, so either answer is a row change, not code |

### 7.3 Uses that count (levels by use, line 50)

The executor reports "did something" (hit an enemy, healed a hurt ally, absorbed, taunted, ...) per the table in
`research/cloud/Class-Ability-Spec-Draft.md` section 7. The engine adds `use.<ability>` +1 at most once per `abil.useEvery` (3 s) per
ability. Echoes and toggle-ticks never count on their own. Level = from the uses curve in that draft (rows `abil.usesCoef`,
`abil.usesExp`, `abil.maxLevel`).

## 8. Modifiers and Echo as data

### 8.1 How the snapshot resolves numbers

For every numeric field F of an ability (damage, heal, radius, duration, cost, cooldown, hp, stacks ...):
`F = base(row) x (1 + perLevel x (level - 1), capped) x tree(F) x mod(F)` where `mod(F)` comes from the 2 equipped modifiers' level steps
(`research/cloud/Modifier-Pool-Spec.md` 2.1) and the composition rules there (different fields multiply, same field adds, caps).
Shape modifiers set flags the executor reads: `split=3 @ 45%`, `pierce=+2`, `ricochet=+3`, `chain=+2 @ drop 7`, `follow=true`,
`lingering=4 s`, `floor=10`. Forbidden pairs (Floor + Duration+, line 130) are refused at equip time.

### 8.2 Echo (one mechanism, a mode per ability)

When Echo is equipped, step 9 of the pipeline also queues `EchoJob{snap, at = now + abil.echoDelay (1 s), strength = the Echo level's
% from `research/cloud/Modifier-Pool-Spec.md` (refreshed: 20-30%)}`. The echo snapshot = the ability at its own level WITHOUT the other
equipped modifier's bonus (that spec's rule); the SAME executor runs with every power number x strength and `echo=true`. Echoes cost
nothing, start no cooldown, never count as a use, and never queue another echo ("cannot echo an echo"). The mode decides WHAT runs:

| Mode | Meaning | Abilities (lock line) |
|---|---|---|
| `repeat` | the instant effect runs again at the same anchor / target | Meteor (111), Palm Strike - same target if alive (123), Sacred Heal - same circle (141), God Killer - the empowered strike repeats once (118), Whirlwind - a weaker spin 1 s after the spin ENDS (139), Martyr's Grace - a second chain from the same start (145) |
| `reform` | when the zone ends or breaks, a weaker copy forms once in the same place | Shield Bubble (145, Priest file) |
| `linger` | when the zone ends, its buff stays on everyone who was in range for `echo.lingerSec` at reduced strength | Warlord's Banner (132) |
| `window` | a stance's reaction comes back for a few seconds while you move freely | Still Water: counters return ~3 s, block + counter interrupts your own swing (124) |
| `repeatFx` | a zone / shower repeats once | Starfall, Hundred Fists shockwave (Modifier pool) |

`EchoJob` lives in the world list; the caster dead / gone = the echo is dropped (no free effect without a caster). Anchor for
`repeat`: the cast's anchor, or the original single target if it is still valid, else nothing (Echo "needs a living target").

## 9. Stunlock breakout (lines 120-121)

| Piece | Design |
|---|---|
| What counts as "stunlocked" | a mob that keeps getting player hits with gaps under `stun.gap` (0.5 s) - combo hits, Palm Strike, Shockwave; tracked in the inspect damage hook per NPC: `chainStart`, `lastHit`, the set of player UUIDs that hit it in the last 1 s |
| Window | `stun.window` (3 s) x number of players in that set, at most `stun.maxPlayers` (4) -> 3 / 6 / 9 / 12 s |
| Breakout | when the chain is longer than the window and the mob is a boss / mini-boss: the mob gets `stun.immune` (1.5 s) of BREAKOUT - our hits still deal damage but do not interrupt it (no knockback: strip the KnockbackComponent like DamageLock does; no stun effects from abilities) - so its next attack lands ("the boss can hit you to break out", line 121). Chain resets after the breakout |
| Who is a boss | no boss flag exists (SkyyMobs 0.1.4). v1: Server Setup table `stun.bossRoles` (NPC role ids, "boss" / "mini") + later `mob:fn:info` gets a tier element (a SkyyMobs change) |
| What interrupts a mob today | UNVERIFIED: whether vanilla hit-stun comes from knockback, a stagger effect, or the NPC's attack being cancelled by damage (probe P8). The breakout uses whichever it is |
| Cost | one map entry per mob being hit (removed 5 s after its last hit), touched only inside the damage hook - no tick |

## 10. Zones, auras, toggles, passives, chains - per ability engine notes

| Ability | Engine notes |
|---|---|
| **Mana Barrier** (ZONE) | dome radius `barrier.radius` (4 blocks, proposed) at the caster's feet, 12 s; filter-group damage hook: target = the Mage inside her own dome (Ward modifier: allies get a Ward shield, not the conversion) -> convert (7.2); 0 Mana ends it; Follow: anchor = the caster each tick; Knockback+ modifier = push on end. Look: a faint ring + a few slow rim particles every 0.5 s, never a solid model (line 114) - particle pick UNVERIFIED (probe P9) |
| **Shield Bubble** (ZONE with HP) | 6 blocks, 12 s, HP = 100% of the caster's max Health (snapshot); filter hook: damage to an ally inside is taken from bubble HP first (overlapping bubbles: the one with the most HP); pulses: when HP crosses 75 / 50 / 25 / 0% -> heal pulse 8% max Health to everyone inside (through the ability heal path, 10.1); blocks projectiles: each zone tick removes hostile projectiles inside (ShotTrack-style creator check) - UNVERIFIED cost / feel (probe P10); Follow modifier = anchor on caster; Echo `reform` |
| **Sanctuary** (ZONE) | 8 blocks, 12 s, every 1 s heal 5% max Health to allies inside; damage reduction 10% as an aura Buff (`dr`) read by the filter hook |
| **Warlord's Banner** (ZONE + leash) | 12 blocks, 30 s; aura Buffs by tier (you 16 / party 12 / players 8 % for damage, defence and attack speed); leash: the Berserker outside the range for one aura tick = the banner falls; kill hook (inspect group, a DeathComponent on an NPC that died inside): `until += 1 / 3 / 5 s` (normal / mini / boss), total life capped at `banner.cap` (60 s); Echo `linger`; banner model = a vanilla banner block / prop placed as an entity - UNVERIFIED (probe P11), fallback particles |
| **Blood Frenzy** (TOGGLE + AURA) | stacks on the Berserker (25 max, 6 s each); per stack you +1.5% dmg / +1% aspd / +0.5% mspd, allies in the aura half; per-swing cost + `frenzy.drain` per second; Floor modifier: once stacks reached 5 / 10 they never decay below it; off when Mana or Stamina cannot pay; cooldown starts at OFF |
| **Flowing Form** (AURA + stacks) | 30 s, drain Mana + Stamina per second; stacks per landed hit (20, 5 s each); enemies in 5 blocks get Awe: lose target ~1 s (UNVERIFIED target-clear API, probe P12), then -1% defence / -0.5% move per TOTAL combo (caps -20 / -10) for the run + 10 s after |
| **Guardian Spirit** (PASSIVE) | filter-group hook, LAST in the group: target is a player who would die (Health - amount <= 0) AND inside 30 blocks of a Priest who has it equipped AND eligible (party only by default; the class-tree toggle opens it to every player) AND the target's cooldown is ready AND the Priest has the Mana -> cancel the damage, set Health to 30% of max, pay Mana, `readyAt = now + 12 s x 2^(saves)`; counters reset after `gs.resetAfter` (30 s) without combat for the target (`skill:fn:combat`). Several Priests: the nearest one with the Mana pays. Must run after armour / other reductions - group ORDER is UNVERIFIED (probe P5); fallback: an invulnerability effect the engine already honours (`DamageSystems$FilterUnkillable`, VERIFIED reader in `research/Grapple-Bolt-Spec.md` 2.5) |
| **Martyr's Grace** (CHAIN) | candidates = the Priest + party in 30 blocks, then other players in 30 blocks; order: party block first (lowest Health % first; the Priest is a party member), then others (lowest first); heal 75%, 60%, 45% ... (drop 15, or the Chain modifier's smaller drop, up to 10 targets, floor 0); line of sight not needed (proposed); heals go through 10.1 with this ability's exception cap (75%) |
| **Enrage** (SNAPSHOT) | Buffs on targets picked at cast; ramp 10 -> 20% over 10 s, hold 5 s, end (value read from the Buff's age at hit time - no tick) |

### 10.1 Ability heals

All ability heals go through ONE new method next to `HealTask.bridgeHeal` (`SkyyClasses/build_skyyclasses_0.1.13.py` 3696-3745) with
its own cap channel: per target per cast at most `abil.healCap` (60% of max Health; Martyr's Grace 75% exception), no HealBudget
(that is the heal-on-hit channel), Divinity XP 1 per HP on others / 1.25 on self (`research/cloud/Class-Ability-Spec-Draft.md` 2.4),
the same chat lines throttle. Non-party players get `priestHeal.othersPercent` only where the ability says "party more".

### 10.2 Buffs: how a % reaches the game

| Buff | Mechanism | Status |
|---|---|---|
| damage dealt % / damage taken % (defence, DR) | our DamageEventSystem in the FILTER group multiplies `Damage.setAmount` for buffed attackers / targets (the DamageLock hook shape) | VERIFIED hook; order vs SkyyGear / SkyyMobs damage systems UNVERIFIED (multiplication commutes, so order only matters for flat adds and the Guardian Spirit check) |
| move speed % | the movement protocol % layer with our own source `classes.ability` (the SkyyAccessories Speed route) | LIVE route in SkyyAccessories; reuse the same call |
| attack speed % | SkyyGear's swing roots pick timing by hidden effects (4 discrete tiers). Options: (a) round the buff to the next SkyyGear tier step; (b) SkyyGear adds 3 more "ability haste" effects (x0.9 / x0.8 / x0.7) combined with the weapon's own tier | needs SkyyGear (a cross-mod change, probe P6); bows / staffs / fists not covered by SkyyGear tiers yet |
| shields (Ward) | a Buff with HP; the filter hook takes damage from it first; largest one wins, cap 40% max Health (Modifier pool) | INFERRED |

Stacking: the same ability from two casters -> only the strongest Buff counts; different abilities add, then the global caps from
`research/cloud/Class-Ability-Spec-Draft.md` 5 / `research/cloud/Modifier-Pool-Spec.md` (Haste +60% total speed etc.) apply.

## 11. Multiplayer and party rules

| Rule | Default |
|---|---|
| Ally | self + party (`class:fn:ally`); "players around you" = any player in range that is not hostile (6) |
| Friendly fire | hostile effects never touch party members; other players only with world PvP on (engine filter + our check) |
| Heals | everyone in range is healed; party full, others `priestHeal.othersPercent` (50) unless the ability says otherwise (Martyr's Grace orders party first) |
| Same buff from two casters | strongest only |
| Two bubbles / barriers overlapping | damage taken by the one with the most HP; each Mage's barrier converts only for its own Mage |
| Guardian Spirit, two Priests | the nearest with Mana pays; the target's doubling counter is shared (Question 3) |
| Caster dies / logs out / changes world / switches profile or class | their toggles, auras, channels, snapshot buffs THEY receive stay (Enrage stays on allies); their placed zones: Banner falls, Mana Barrier ends; Shield Bubble and Sanctuary finish on their own clock (heals without XP) - the traversal rule `research/Magic-Traversal-Spec.md` 1.3 |
| Equipping / unequipping | only out of combat (`skill:fn:combat` = 0), through the class page / SkyWynn Menu; never mid-fight |
| XP | ability damage uses `Damage$EntitySource(caster)` (or ProjectileSource with a launch record) so class XP, SkyyGear level scaling and the class lock see the caster - same as the blink trail (VERIFIED shape, `research/Magic-Traversal-Spec.md` 2.2) |

## 12. HUD: showing cooldowns

| Option | How | Verdict |
|---|---|---|
| H1: vanilla 0.7 ability HUD | our two runes sit in the slots -> icons show; cooldown fill only if 3.4 B works | **use when P3 passes** (zero UI code, vanilla look) |
| H2: SkyyHud **Abilities** widget | new widget id `Abilities` APPENDED to `Widgets.IDS` (the 0.3.11-0.3.14 rule); reads bridge `class:fn:abil` apply(UUID) -> `Object[]{String name1, Long msLeft1, Long msTotal1, String state1, String name2, ...}` answered from memory, any thread, never throws (the `skill:fn:combat` shape); two rows "Meteor  4s" + a ProgressBar each (the Combat widget's proven bar); state text for toggles / stacks ("Frenzy 17", "Barrier 64 Mana") | **build as fallback + for stacks**; 1 s HUD tick = whole-second countdown, which is fine for 6-45 s cooldowns; text sets only, shape fixed (2 rows) -> no full HUD re-sends |
| H3: chat / notification line | `NotificationUtil.sendNotification` (used by ClassRules.popup) | only for refusals ("Ready in 4 s", "Not enough Mana"), throttled 1 s |
| Action bar | Hytale has no Minecraft-style action bar we can write to (UNVERIFIED; none found in our mods) | no |

## 13. Server Setup rows (SkyWynn Menu -> Server Setup -> Classes; `tools/skyycfg.py`, KEEP 10, times in SECONDS)

New categories: `abil` (Abilities), `abilx` (per-ability numbers, Advanced). All `live` unless noted.

| Key | Label (<= 40) | Type | Default | Range | Unit | Flags |
|---|---|---|---|---|---|---|
| part.abilities | Class abilities | bool | true | - | - | part, danger |
| abil.input | Ability input | choice | both (`both\|Rune keys + /cast,rune\|Rune keys only,command\|/cast only`) | - | - | live |
| abil.tick | Zone and aura tick | dec | 0.25 | 0.1-1 | s | live, adv |
| abil.maxLive | Most ability effects per world | int | 48 | 8-256 | - | live, adv |
| abil.maxZones | Most placed zones per player | int | 2 | 1-4 | - | live |
| abil.echoDelay | Echo delay | dec | 1 | 0.5-3 | s | live |
| abil.useEvery | Count a use at most every | dec | 3 | 0-30 | s | live |
| abil.usesCoef / abil.usesExp / abil.maxLevel | Uses per level (curve) / exponent / max level | dec / dec / int | 4.5 / 1.5 / 15 | - | - | live (draft section 8) |
| abil.healCap | Ability heal cap per cast | int | 60 | 10-100 | % | live |
| abil.creativeFree | Creative casts are free | bool | true | - | - | live |
| abil.cdMessage | Cooldown message | bool | true | - | - | live |
| abil.mobVoidStop | Pushed mobs stop at the void edge | bool | true | - | - | live |
| stun.window | Boss stunlock breakout per player | dec | 3 | 0.5-10 | s | live |
| stun.maxPlayers | Breakout players counted (max) | int | 4 | 1-10 | - | live |
| stun.gap | Stunlock gap that resets the chain | dec | 0.5 | 0.1-3 | s | live, adv |
| stun.immune | Breakout immunity | dec | 1.5 | 0.5-5 | s | live |
| stun.bossRoles | Boss and mini-boss NPC roles | table | (empty) | - | - | live (cols Role\|Tier) |
| gs.baseCooldown | Guardian Spirit first cooldown | dec | 12 | 1-120 | s | live |
| gs.resetAfter | Guardian Spirit reset out of combat | dec | 30 | 5-600 | s | live |
| gs.mana | Guardian Spirit Mana per save | int | 15 (proposed) | 0-200 | - | live |
| gs.health | Guardian Spirit saved Health | int | 30 | 1-100 | % | live |
| banner.killSec / .miniSec / .bossSec / .cap | Banner time per kill / mini-boss / boss / cap | dec | 1 / 3 / 5 / 60 | 0-60 / 0-60 / 0-120 / 10-300 | s | live |
| frenzy.manaPerSwing / .staminaPerSwing / .drain | Blood Frenzy cost per swing / drain | dec | 1 / 0.5 / 0.2 (proposed) | 0-20 | - / - / per s | live |
| frenzy.decay / frenzy.max | Blood Frenzy stack decay / max stacks | dec / int | 6 / 25 | 1-30 / 1-50 | s / - | live |
| flow.decay / flow.max | Flowing Form stack decay / max | dec / int | 5 / 20 | 1-30 / 1-50 | s / - | live |
| barrier.radius / barrier.ratio | Mana Barrier size / HP per Mana | dec | 4 / 2 | 2-12 / 0.5-10 | blocks / x | live |
| bubble.pulse | Shield Bubble heal per pulse | int | 8 | 0-50 | % | live |
| `ab.<Ability>.mana / .stamina / .cooldown / .duration / .radius / .power` | per ability (35 x up to 6, generated from `research/cloud/Class-Ability-Spec-Draft.md` 2.x) | dec | the draft's numbers | - | Mana / Stamina / s / s / blocks / % | live, adv (category abilx) |

Rows read by the CastSnap, so a change applies to the NEXT cast (help text says so). No migration: missing keys read defaults.
Player switch (Settings registry): `classes.abilCdChat` "Ability cooldown messages" (true).

## 14. Performance budget

Model: 20 players in one world, everyone with one placed zone and one aura running at once (a busy party fight, worse than normal).
World tick rate assumed 30 per second (UNVERIFIED). Numbers by python (method: count x Hz):

| Work | Per second | Per tick |
|---|---|---|
| zone scans (`getAllEntitiesInSphere`, 20 zones x 4 Hz) | 80 queries (~2,400 entities looked at if ~30 each) | ~2.7 queries |
| aura membership (players only: 20 auras x 4 Hz x 20 players, a distance check each) | 1,600 distance checks | ~53 |
| world cap worst case (48 zones x 4 Hz) | 192 queries | 6.4 |
| Guardian Spirit | 0 (only on a lethal hit) | - |
| stunlock tracker, Charges, Buff reads | inside existing damage events (map lookups) | - |
| HUD | 20 bridge reads per second (memory), text sets only | - |

Rules that keep it there: aura membership checks PLAYERS from the world's player list (never an entity scan); enemy scans only for zones
that hurt / affect enemies (Banner kill hook uses the death event, not a scan); 4 Hz default (`abil.tick`), damage ticks inside a zone
1 Hz unless the ability says otherwise; one AbilWorld list per world behind a tick-stamp guard (the TravTick pattern); particles at most
every 0.5 s per effect; no disk I/O on the world thread (use counters flushed by the 2 s ClassTick off-thread). Target: under 1 ms per
world tick on Skyy's PC at the model above (measured in probe P13).

## 15. Build plan (small versions)

N = the SkyyClasses version after the SET pin at build time (classes014 is making 0.1.14, so the engine likely starts at 0.1.15).
Every version = `tools/classes_<ver>_patch.py` on the previous GENERATED script (PROJECT-RULES 4), harness
`SkyyClasses/test_skyyclasses_<ver>.py` (bare JVM, pure maths classes: AbilMath, StackMath, ChainMath, CdMath).

| Step | Version | What | Round size |
|---|---|---|---|
| E0 | SkyyAbilityProbe 0.1 (admin-only probe mod, removed after) | probes P1-P13 below on 0.7 | lean (probe) |
| E1 | N | CORE: data file per profile, CastReq + pipeline (4), cooldowns, Mana / Stamina spend, `/cast 1\|2` + admin `/classadmin cast`, rows `part.abilities` + `abil.*`, bridge `class:fn:abil`, AbilTick (EntityTickingSystem on Player, isParallel false), AbilWorld lists; 3 abilities to prove the kinds: **Sacred Heal** (INSTANT heal, 10.1), **Meteor** (delayed INSTANT damage), **Enrage** (SNAPSHOT buff + the damage filter hook); A1 auto-owned + equipped on line 1 for testing | **full** (saved data, new system) |
| E2 | N+1 + SkyyHud next | rune input (3.2) once 0.7 is live: 35 rune items + icons (SkyyClasses ships an asset pack), slot mirror + guards, vanilla-rune gate; SkyyHud Abilities widget (12 H2) | full (items, several mods) |
| E3 | N+2 | ZONES: Mana Barrier (+ Follow), Shield Bubble (HP, pulses, projectile block), Sanctuary, Warlord's Banner (leash, kill extension) | full |
| E4 | N+3 | TOGGLE / AURA / stacks: Blood Frenzy (per-swing cost, Floor), Flowing Form (Awe), move-speed source; attack speed with the SkyyGear change | full (2 mods) |
| E5 | N+4 | PASSIVE + CHAIN: Guardian Spirit (lethal hook, doubling cooldowns), Martyr's Grace; ability heal channel complete | full (death / saves) |
| E6 | N+5 | MODIFIERS + Echo engine (8), ability levels + points, the Abilities page (inline, vanilla look, `tools/skyyui.py`): own / equip / modifiers, out-of-combat equip | full (saved data) |
| E7 | N+6 | CC + stunlock breakout (9), stun / root / slow / knockback / pull, boss role table | full |
| E8+ | N+7 ... | the rest of the 35 abilities, a few per version by class (Warrior, Archer, Assassin, Monk ...), class-tree path reads as SkyyTrees 0.3.3 nodes land | lean per class when no new kind is needed |

Deploy order rule: SkyyClasses before SkyyHud (the widget hides itself without `class:fn:abil`, the Combat widget convention).

## 16. For the local session (UNVERIFIED engine checks)

| # | Probe | Why |
|---|---|---|
| P1 | On the 0.7 release jar: default keys for Use Ability 2 / 3; a rune with `Cost 0 / None` + our 1-step cast root shows in the HUD and casts; `InteractionChainStartEvent` fires for it with `getType()` Ability2 / 3 and cancelling it leaves no stuck animation (`research/Hytale-Runes-Research.md` section 7) | input I1 |
| P2 | `InteractionChainStartEvent` also fires for Primary swings (hit or miss) | Blood Frenzy per-swing cost |
| P3 | The player's `CooldownHandler` reachable from a plugin; a code-set cooldown (our length, the rune's Cast root id) syncs to the client HUD fill | HUD H1 |
| P4 | Writing a Skyy rune into AbilitySlots slots 0 / 3 from code respects the slot filters, survives death / world switch / relog; `InventoryChangeEvent` on the AbilitySlots component fires for player drags | slot mirror |
| P5 | Ordering inside the FILTER damage group (`getDependencies` / system order) so Guardian Spirit and Mana Barrier run after armour and SkyyGear / SkyyMobs systems; how to declare it from javassist | lethal save correctness |
| P6 | Attack speed buff: SkyyGear's hidden-effect swing roots - can 3 extra effects combine with the weapon's tier; cost of more decision branches; bows / staffs / fists | Banner / Blood Frenzy attack speed |
| P7 | `EntityStatMap.subtractStatValue` on Mana / Stamina from our tick while SkyySkills' 0.2 s regen runs (no double-write fight) | cost bookkeeping |
| P8 | What interrupts a mob's attack when hit (knockback, a stagger effect, or damage itself) and how to suppress it for 1.5 s | stunlock breakout |
| P9 | A faint see-through dome look: particle ring vs a transparent model (Skyy: visible but never distracting) | Mana Barrier look |
| P10 | Removing hostile projectiles inside a bubble each 0.25 s tick: cost and whether the client shows them vanish cleanly | Shield Bubble |
| P11 | Placing a banner model as a temporary entity (or a block) and removing it cleanly | Warlord's Banner |
| P12 | Clearing an NPC's current target for ~1 s (Awe "lose their target"); taunt (turn mobs to the Warrior) uses the same API | Flowing Form, Rallying Guard |
| P13 | Real cost of `getAllEntitiesInSphere` at 4 Hz x 48 zones on Skyy's PC; world tick rate | performance budget |
| P14 | SkyyProfiles: add section -12 (vanilla rune bag) to the profile snapshot or confirm we hide vanilla runes | profile leak |
| P15 | Whether vanilla 0.7 Mana max 100 changes SkyySkills' base Mana posting (`research/Hytale-Runes-Research.md` 4.1) - every ability Mana cost depends on it | costs |

## 17. Questions for Skyy

| # | Question | Recommended default |
|---|---|---|
| 1 | Cast input: Hytale 0.7's own two ability keys (the rune keys, HUD slots built in) + `/cast 1` / `/cast 2` as a backup? | [Yes: rune keys main, /cast always works] |
| 2 | Vanilla runes (Fireball, Enrage ...) for players who have a class: blocked, or usable alongside class abilities? | [Blocked - class abilities only] |
| 3 | Guardian Spirit with two Priests: does the doubling cooldown follow the SAVED player (shared) or each Priest separately? | [Shared per saved player - two Priests cannot double the saves] |
| 4 | Guardian Spirit Mana per save (the lock says "if you have the Mana" but no number) | [15 Mana, Server Setup row] |
| 5 | Cooldowns: kept through a relog (memory) but reset by a server restart - OK, or save them to disk too? | [Memory only] |
| 6 | Pushing / pulling MOBS into the void with Knockback+ / Pull: stop them at the edge, or allowed (like "no void protection")? (also asked in `research/cloud/Modifier-Pool-Spec.md`) | [Stop at the edge - the pool spec's default; one row flips it] |
| 7 | Changing equipped abilities / modifiers only out of combat? | [Yes, out of combat only] |
| 8 | Cooldown display: the game's own ability HUD if possible, plus a SkyyHud "Abilities" widget showing stacks (Frenzy 17) and countdowns? | [Both; widget on by default] |
