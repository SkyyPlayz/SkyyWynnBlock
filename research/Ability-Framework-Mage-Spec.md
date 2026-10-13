# Ability framework + the Mage, end to end (build spec, 2026-10-13)

Skyy: "Should we build the abilitys all in one go? Or start with one class, refine it, then move on to the next?" -> popup
**"Mage (Recommended)"**: the shared ability framework with ONE class end to end - Mage first - Skyy tests, we refine, then the other
classes in batches of 2-3 (`docs/answered/classes.md` 2026-10-13 ABILITY BUILD ORDER).

Spec only (no build). Marks: **LIVE** = in the SET today (`tools/deploy_set.py`: SkyyClasses 0.1.19, SkyyHud 0.3.18, SkyySkills 0.4.31,
SkyyArmory 0.1.22, SkyyProfiles 0.1.10, SkyyTrees 0.3.5, SkyyGear 0.2.24). **VERIFIED** = read in a live build script or in the Hytale
0.7.0 release jar / Assets.zip (read-only). **UNVERIFIED** = needs the game (section 9, each with a probe step). Skyy's locked words win
over every older draft; where this spec and `research/cloud/*` drafts differ, this spec is newer.

## 0. Read this first - most of the framework is already LIVE

| Piece | State | Where |
|---|---|---|
| Ability registry (Mage 5 + Priest 5), per-profile loadout, `/cast 1-4`, `/cast list / swap / page`, Mana + Stamina costs, cooldowns in memory, refusal sounds + lines | **LIVE** (SkyyClasses 0.1.16-0.1.19) | `SkyyClasses/build_skyyclasses_0.1.19.py` header; rows lines 513-723 |
| Shapes: walking / sprinting / mid-air (primary) + crouch (alt), per-shape cost + cooldown rows, `/classadmin shape` | **LIVE** (0.1.18) | same |
| Mage abilities: Meteor, Mana Barrier, Frost Nova, Starfall, Arcane Beam - all 4 shapes each | **LIVE** (0.1.16-0.1.18), **never tested by Skyy** (`TEST-CHECKLIST.md` item 11 still open) | `docs/tests/2026-10.md` lines 1080, 1158, 1229 |
| Abilities HUD widget (icon + name + cost / countdown, vanilla ProgressBar, alts while crouching) | **LIVE** (SkyyHud 0.3.18, bridge `class:fn:abil`, 48 fields) | `SkyyHud/build_skyyhud_0.3.18.py` 693-717, 1622-1632 |
| Ability damage = class damage (kill XP, class perk) | **LIVE** (SkyySkills 0.4.28 `class:fn:abilhit`) | `SkyySkills/build_skyyskills_0.4.31.py` header 0.4.28 |
| Loadouts (abilities per wardrobe loadout) | **LIVE** (SkyyWardrobe 0.2.1 + `class:fn:loadoutGet/Set`) | SkyyClasses 0.1.19 header |
| Mage weapons: 8 ladder staffs (blink + light trail, quick shot), 7 spellbooks (Page Burst + Levitate) | **LIVE** (SkyyArmory 0.1.22 = a 0.6-asset jar recompiled for 0.7; the full 0.7 port = round `armory0123`, running) | `SkyyArmory/build_skyyarmory_0.1.21.py` header |
| Mana on 0.7: pools 45 + 10 / Sorcery level (Mage), regen 5 / s, 75 % in combat, Mana.json override | **LIVE** (SkyySkills 0.4.31) | `tools/skills_0_4_31_patch.py` header |
| **Real keys (Use Ability 2 / 3 = the 0.7 rune keys)** | **NOT BUILT** - engine plan round R4 "waits for Hytale 0.7"; 0.7 is out since 2026-10-12 | this spec, section 3 |
| Ability levels by use, modifier trees, Echo | **NOT BUILT** (R8) | section 6 |
| Class-tree ability nodes (Mage R3 Phase Step, C3 Charged Dome ...) | **NOT BUILT** (SkyyTrees shows them "Comes with the class abilities") | section 6.3 |
| Rune sections -11 / -12 in the SkyyProfiles snapshot | **NOT BUILT** (0.1.10 saves 6 sections; no `AbilitySlots` in its script - VERIFIED grep) | section 3.4 |

So "build the framework with the Mage" = (1) put the Mage on the real keys on 0.7, (2) let Skyy play the five Mage abilities and refine
the numbers, (3) add the two missing framework layers (levels + modifiers + Echo; tree nodes) on the Mage first, (4) batches of 2-3
classes on the proven engine. Nothing already built is thrown away.

## 1. Locks this follows (newest wins; `docs/answered/classes.md` + `skills.md` + `ui.md`)

| Skyy's words (date) | What it fixes here |
|---|---|
| "we decided 4 ability's, 2 active at a time. the 2 you pick are your primary ability's ... thew other 2 are set to crouch" (2026-10-08) | Ability 2 / 3 = primaries; crouch + Ability 2 / 3 = alts |
| "we can still do same ability 4 shapes. walking sprinting and mid air, crouch" + "depends on what they change about the ability" + "im fine with it casting mid roll" + "if it doesnt we can just skip mid roll cast" (2026-10-08) | 4 shapes, cost / cooldown per shape, mid-roll cast if the press reaches the server (probe P1) |
| "but id like to find a way to add out own hotkeys" -> popup batch 1 "Yes to all": keys only, no hotbar ability items for now, swap primaries out of combat, HUD swaps to alts while crouching, Mage + Priest built first (2026-10-08) | input = the two keys + `/cast` |
| "hmmm i dont really like either option, we will need the ability keys later. ... (dont rebind sprint, leave it.)" (2026-10-08) | the roll stays on the sprint press; never touch Skyy's binds |
| "2 class abilities per class (the two rune lines) ... built on runes" (2026-10-04) | the 0.7 rune system IS the input (section 3) |
| "each ability gets its own upgrade tree where you unlock the modifiers. ability upgrade points are gained by using the ability." + 2 modifiers equipped, no doubling, shared pool levelled per ability (2026-10-04) | section 6.1-6.2 |
| class-tree paths change HOW an ability works; "the shield moving with you will be a modifier, not a class tree upgrade" (2026-10-04) + Mana Barrier Follow = modifier AND one tree node (2026-10-07) | section 6.3 |
| Meteor + Echo; Mana Barrier "at least 12 seconds keep the mana drain"; placed dome + Follow; "visible, but still easily see through"; Starfall / Arcane Beam / Frost Nova approved (2026-10-07 / 10-08) | section 5 |
| Mage = glass cannon: "they should have a little higher damage to mana cost ratio ... really low defense and health, and really high damage" (2026-10-03); "mage can have the spell book"; Priest = wands + Soul Orb (2026-10-04) | Mage weapons = staffs + spellbooks; the wand is the Priest's |
| Mage / Stamina split 75 / 25, costs 78 / 22, "all ability's should be affordable when unlocked"; unlock levels 1 / 10 / 20 / 30 (2026-10-08) | section 5.2 numbers |
| "make sure the keep the class balance sheet updated with fresh numbers when things change" (2026-10-08) | every number here = the chart (`tools/dev/scratch/classchart/class-balance.html` lines 504-508); the chart is republished after the refine round |
| In-combat Mana regen 75 %, Mana on hit (melee + Archer only), keep 5 Mana / s on 0.7 [default] (2026-10-08 / 10-13) | section 5.3 |
| "dont put any void protection on any traversal" (2026-10-07) | abilities never move the caster, so no void rule applies to them; mobs pushed by Knockback+ stop at the edge [default, Question 6] |
| UI = vanilla look, inline pages, `tools/skyyui.py`; HUD boxes small, same padding on all sides (2026-09-28 / 10-03) | the Abilities widget + page stay on the kit |
| No per-tick work for idle players, no world-thread I/O, lock-free bridge (`research/Code-Structure-Audit.md`, Skyy 2026-10-13) | section 3.9 |

## 2. Existing mods checked first (PROJECT-RULES 2)

`python tools/mod_check.py - ability / spell / rune / exotic / hexcode / arcane` + `research/Mod-Database.md` + the Mods folder (read only):

| Mod (installed) | What it has | Verdict |
|---|---|---|
| **Hytale 0.7 Runes** (vanilla `Hytale:Abilities` plugin: 7 ability runestones, 11 modifier runestones, the Runebinder's Lattice, two HUD slots, the Use Ability 2 / 3 keys, cast chains with `LaunchAbilityProjectile`, `SpawnAbilityEntity`, `GrantAbilityCharges`, `TriggerAbilityFX`, elements Fire / Water / Earth / Wind / Lightning) | the real thing, free | **BUILD ON IT** for input + HUD + icons; copy its cast chains for animation / particle / sound recipes (section 3.6). Our numbers stay in our engine (they change with levels, modifiers, tree, Server Setup) |
| Hexcode 0.10.1 (Riprod, `^0.6.0`, 910 classes, hex books + pages, 64 animations) | a spell-book casting system with its own UI | not packed (0.6 only, licence not on its page); **study only** for how it animates book casts (read-only jar) |
| Darkhax Spellbook 2026.2.20 (25 classes, 4 test items) | a tiny interaction test library | nothing to reuse |
| SLVR Robes & Spells 1.2.0 (asset-only, `^0.5.4`), Arcane Power 3.2.0 (Tayko, ARR, asset-only), Unified Magic Theory (crystal ingredients) | cloth armor + spell items, no engine | nothing for the framework; Mage cloth armor ideas later |
| MMOSkillTree 1.7.0 (Ziggfreed, `<0.7.0`), RPGLeveling 0.3.13, ProficiencyLevels 2.0.1 | levels / skill trees, no class abilities | no fit (SkyyTrees + SkyySkills already own this) |
| StunningCombat 1.4.0 (DanBagh, `^0.6.0-pre.13.1`) | stun effects on hits | learn only: Frost Nova / breakout use the vanilla Stun / Freeze effects already (SkyyArmory's stunlock clock is live) |
| FL's Exotic Weaponry (FalemLeaf, ARR) | exotic weapons with unique moves | **not installed** (Skyy 2026-10-12: "Fl's well just study the animations and the kinds sof moves they have") - Skyy installs it, then a read-only study of its interaction chains / animations feeds the Mage polish round (section 7, phase C) |

Conclusion: no installed mod gives a class-ability framework; ours is already live. We reuse the vanilla 0.7 rune system for keys, HUD,
icons and cast-chain recipes, and learn from Hexcode / Exotic Weaponry for looks only.

## 3. The shared framework (every class uses exactly this)

### 3.1 Ability definition data - one table per class

One Python table per class in the SkyyClasses build script (today: `ABILS` list line 498 + per-ability rows 542-723 + the shape tables
609-637). A new class = a new table + its executors; nothing else changes. Columns (all read into `AbilDef` at build time, numbers into
Server Setup rows):

| Column | Meaning | Mage example |
|---|---|---|
| `id` / name / class / slot | slot 0 = A1, 1 = A2, 2 = A2-alt, 3 = A1-alt A, 4 = A1-alt B | `Meteor` / Mage / 0 |
| `key` | which press: A1 + A2 = primaries (Ability 2 / 3, order swappable); A2-alt + the picked A1-alt = alts (crouch) | Meteor = Ability 2 by default |
| weapon types | the class's weapon rule (`ClassRules.allowed`) - checked at the CAST only | staff, spellbook |
| cost per shape | Mana + Stamina for walking / sprinting / mid-air / crouch (the class's cost split, section 5.2) | 23 + 2 / 23 + 2 / 23 + 2 / 20 + 1 |
| cooldown per shape | seconds | 14 / 14 / 16 / 14 |
| cast type | **instant**, **delayed** (Meteor 1 s), **zone** (placed, ticks), **channel** (Arcane Beam), **passive** (Guardian Spirit), later toggle / snapshot buff / aura / chain / charge | Meteor = delayed |
| targeting | look point within `range`, self, cone, sphere around the caster, landing spot (mid-air), N blocks ahead (sprint) | look point, 25 blocks |
| damage / heal formula | multiples of **H** = one charged shot of the held weapon (`armory:fn:info` element 3 x tune %, fallback `abil.hitFallback` 25) x ability level x modifiers x tree; heals in % of max Health | 3.0 H in 4 blocks |
| per-level gain + cap | section 6.1 | +2 % damage / level, cap at Lv 15 |
| modifiers offered (4-5) | from the shared pool | Radius+, Power+, Lingering, Split, Echo |
| uses that count | section 6.1 | hits >= 1 enemy |
| sounds / particles / animation | vanilla ids (section 3.6) | ring warning, fire impact |

### 3.2 Input on Hytale 0.7 - the rune route (round R4, the one missing framework piece)

**How 0.7 casts** (VERIFIED in the release jar `InteractionContext`: strings `Ability2`, `Ability3`, `AbilitySlots`, `abilityStack`,
`canUseWith`, `heldWeaponStack`): the Use Ability 2 / 3 keys cast the rune in `AbilitySlots` slot 0 / 3 while ANY item is held; the
rune needs a weapon in hand. Ability 1 stays the weapon signature (wand ricochet, vanilla meters). Ability 4 = the crossbow reload.

**Release changes vs the pre.4 research** (`research/Hytale-Runes-Research.md` is pre-release; re-read on the release Assets.zip):

| pre.4 | 0.7.0 release (VERIFIED) | Effect on us |
|---|---|---|
| `Slot: Primary / Support` | `Slot: Core / Support` (`protocol/AbilitySlot` enum = Core, Support) | our rune items say `Core` |
| `Tags: [...]`, modifier `AppliesTo` | `AbilityKeywords: ["Damage", "Fire", "Projectile" ...]`, modifier `RequiresAnyAbilityKeyword` / `ExcludesAnyAbilityKeyword` | our class keyword e.g. `SkyyMage`; our own modifier runes (if ever) require it |
| `Weapons: [families]` on a rune | **not seen** in the release `ItemAbility` strings (only `abilityKeywords`, `Slot`, `Cost`, `Cooldown`, `Cast`, `Attributes`) | the class gate is OUR code (cancel the chain), never the rune's data - UNVERIFIED U1 |
| vanilla rune costs 10-30, cooldowns 6-18 s | costs 30-50 Mana, cooldowns **2-6 s**, on a 100 pool | vanilla runes are blocked for classed players [Question 2]; our costs stay ours |
| `Mana.json` 100 / 100, regen 0.3 s | same; SkyySkills 0.4.31 overrides it (0 base, 0.2 s, NoDamageTaken 6 s) | done |

**Design (SkyyClasses 0.1.20, asset pack ON for the first time):**

1. **One rune item per ability**: `SkyyAbility_<Class>_<Id>` (Mage 5 now; 35 later), `Ability { Slot: Core, Cost: 0, CostType: None,
   Cooldown: 0.25, AbilityKeywords: ["SkyyClass", "SkyyMage"], Cast: Root_SkyyAbility_Cast_<line> }`, `Quality: Developer`-like hidden
   item (no recipe, not in creative lists), icon `Common/Icons/Abilities/SkyyAbility_<Class>_<Id>.png` from `art/ability-icons/` (the
   HUD widget already ships these; the vanilla HUD reads `Icons/Abilities/<itemId>.png` - UNVERIFIED U2).
2. **The cast root** = one tiny chain: `ApplyEffect SkyyAbility_Cast_1` / `_2` (an invisible 0.2 s marker), `RequireNewClick: true`
   (one cast per press). Cost 0 / None so the vanilla gate never refuses; OUR pipeline decides.
3. **Hook**: `EntityEventSystem<InteractionChainStartEvent>` (VERIFIED class: `getType`, `getContext`, `getRootInteractionId`,
   `getInitialRootInteraction`): type Ability2 / Ability3 + held section -11 + a `SkyyAbility_` id -> the shape resolver reads crouch /
   air / sprint at the press (built) -> `Abil.cast` (built). Refusal = cancel the event (the server sends the client a cancel packet;
   no animation, no vanilla cooldown fill) + the fail sound + the throttled line. **Fallback** if the event does not fire or cancelling
   leaves a stuck animation (U3): poll the marker effect in AbilTick for players WITH a loadout only (the Grapple Bolt click trick).
4. **Mirror, not inventory**: the engine writes the two equipped primaries into AbilitySlots 0 and 3 on PlayerReady, on `/cast swap`,
   on the page, on a profile / class switch; modifier slots 1-2 / 4-5 stay EMPTY (our modifiers are levelled data, section 6.2).
   An `InventoryChangeEvent` guard on AbilitySlots / RuneBag puts the mirror back when a player drags a Skyy rune out, and deletes any
   `SkyyAbility_` stack found anywhere else (count before / after). Crouch + the key casts the ALT although the slot holds the primary
   (the slot is a picture; the loadout decides).
5. **Vanilla runes**: a classed player's Ability2 / 3 chain whose rune is not ours -> cancelled + the weapon-lock popup; the Runebinder's
   Lattice stays usable (nothing to put in it) [Question 2]. Classless players keep vanilla runes.
6. **`/cast 1-4` stays forever** (controllers, macros, a key probe): one pipeline, two doors. Row `abil.input` = both / rune / command.
7. **Never name a command `/abilities`** (vanilla owns it).
8. **Mid-roll cast**: the roll is the sprint PRESS (SkyySkills); a press of Ability 2 in the same tick casts with the sprinting shape
   if the event reaches us (U4), else nothing special - "we can just skip mid roll cast".

Clash check: no SkyWynn item binds Ability2 / Ability3 (VERIFIED grep of the build scripts, 2026-09-30); on 0.7 any pack item that did
is dead for everyone anyway (the engine routes those keys to the rune). Ability 1 (signature) and Ability 4 (crossbow) are untouched.

### 3.3 Cooldown + Mana + Stamina - one place (LIVE: `Abil.cast`, SkyyClasses 0.1.19 line ~5281)

```
press (rune event / marker / /cast) -> shape (air > crouch > sprint > walk) -> gate: part.abilities, class, alive, not creative-free,
  loadout loaded -> slot: owned + unlocked (1 / 10 / 20 / 30) -> weapon: ClassRules.allowed(main hand) -> cooldown (memory, per pkey)
  -> cost: Mana >= cost x Efficiency AND Stamina >= cost (creative = free) -> snapshot numbers -> pay (subtractStatValue, world thread)
  -> arm cooldown -> run the executor -> (R8) count the use when it did something; refund on an executor failure (built)
```

Rules: refusals cost nothing and start no cooldown; a cast that does nothing still costs; a running effect keeps its snapshot (a row
change applies to the NEXT cast); cooldowns live for the JVM (relog keeps them, restart resets them) [Question 5]; Mana regen keeps
running under every effect; every number in SECONDS in Server Setup.

### 3.4 Per-profile data (`tools/PROFILES-CONTRACT.md`)

| Data | Where | Note |
|---|---|---|
| owned / unlocked, A1-alt pick, key order, grant flag | `Skyy_SkyyClasses/abilities/<pkey>.properties` (LIVE) | atomic tmp + move, private writer, dirty-flag flush (built) |
| (R8) use counts, ability levels, modifier levels + equipped pair | same file, `use.<id>`, `mod.<id>.<m>`, `mods.<id>` | flushed every 30 s + on quit / switch; never on the world thread |
| cooldowns | memory, key pkey + ability | profile 2 has its own |
| loadouts | SkyyWardrobe via `class:fn:loadoutGet/Set` (LIVE) | modifiers join the snapshot in R8 |
| rune sections -11 / -12 | **SkyyProfiles must snapshot them** (0.1.10 saves 6 sections: Hotbar, Storage, Backpack, Armor, Utility, Tool) | without it a Mage's runes show on the Warrior profile; the mirror rewrites 0 / 3 on every switch anyway, so the leak is cosmetic for OUR runes and real for vanilla ones (U5) |

### 3.5 HUD: the Abilities widget + cooldown display

- **SkyyHud Abilities widget (LIVE)**: two rows (icon, name, "23 Mana" or a countdown with the vanilla ProgressBar), grey when
  unaffordable / locked, alts while crouching, hidden without a class; 1 s HUD tick, text sets only. Default spot tl 8,760; the 2026-10-13
  mockup review moves it to br 460,21 after the real-HUD measurement (ui.md 2026-10-13).
- **Vanilla rune HUD (0.7)**: the two slots show our icons once the mirror is in. The cooldown FILL only follows if we also arm the
  engine's `CooldownHandler` (VERIFIED class, methods `cooldown`, `getCooldown`, `hasCooldown`, `isOnCooldown`, `resetCooldown`, `force`,
  `maxTime`, keyed by the cast root id) with our length after our own cooldown arms (U6). If it works, the widget stays for stacks / alts
  and can be hidden per player; if not, the widget is the display. Fail sounds come from the vanilla HUD on a cancelled chain (U3).
- Refusal lines: throttled `abil.refuse` 1 s, player switch `classes.abilCdChat`.

### 3.6 Sounds / particles / animations - vanilla first

| Need | Vanilla asset (release Assets.zip, VERIFIED path unless marked) | Use |
|---|---|---|
| cast animation (staff) | the staff set's `CastSummonCharged` (used by the blink) | every Mage cast; spellbook = the book set's cast |
| cast particle in hand | `Fireball_Cast_Charge` on node `R-Hand`, scale 0.4 (from `Ability_Fireball_Cast.json`) | Meteor / Starfall / Beam |
| cast camera | `CameraShake Ability_Cast_Generic` | every damage cast |
| fail sounds | the client's `ErrorWrongWeaponSound` / `ErrorCooldownSound` / `ErrorResourceSound` on a cancelled chain (U3); else our click | refusals |
| Meteor warning + impact | the ring built in 0.1.16; impact = the Fireball rune's impact FX system (`Ability_Fireball_Impact`'s `TriggerAbilityFX` SystemId / sound - ids listed by the build, U7) | section 5 |
| Starfall stars | the Fireball projectile config at scale 0.5 (`Projectile_Config_Ability_Fireball`) | 12 small impacts |
| Frost Nova | the Charged Shot rune's frost effects (`Server/Entity/Effects/Abilities/` chill / freeze / slow) - vanilla Freeze + Slow already used in 0.1.18 | freeze + chill |
| Mana Barrier dome | particle ring, faint, 0.5 s, built; a transparent dome MODEL only if Skyy wants it after seeing the ring | "visible but easy to see through" |
| Arcane Beam | a line of `TrailParticles` (the `LaunchAbilityProjectile` trail fields) or the staff's own beam particles - built as a particle line in 0.1.18 | polish in phase C |
| sounds | `SFX_Staff_Ice_Shoot` (staff cast), `SFX_Ability_*` (the rune set) | per ability |

Rule: no new art / particle systems until Skyy has seen the vanilla ones (visuals go-ahead 2026-10-13 lets the cloud draw icons; the
Mage icons already exist in `art/ability-icons/`).

### 3.7 Scaling: class level, gear, ability level, modifiers, tree

| Layer | How | Owner |
|---|---|---|
| gear | H = the held weapon's charged shot (`armory:fn:info`), already level-scaled by SkyyGear | SkyyArmory + SkyyGear |
| class level | unlocks (1 / 10 / 20 / 30), the pool (+10 Mana / Sorcery level), regen (+7 % per level above 20), the class balance boost | SkyySkills |
| ability level (R8) | +2 % of the main effect per level, Lv 15 cap (+28 %); uses for level n = round(4.5 n^1.5) (Lv 15 = 1,570 uses) | SkyyClasses |
| modifiers (R8) | 2 equipped, 5 levels, steps per `research/cloud/Modifier-Pool-Spec.md` 2 (Power+ 5-25 %, Echo 20-30 % repeat ...) | SkyyClasses |
| class tree | `tree:fn:bonus` read at the cast (behaviour changes, trade-offs) | SkyyTrees nodes, SkyyClasses reads |
| budget | an ability at its limit <= 2.0x its Lv 1 effect; Mage = at most 2.0x the staff's damage per Mana (chart 5.2) | the chart |

### 3.8 PvP vs PvE (the SkyyArmory rule, `research/Magic-Traversal-Spec.md` 1.3, LIVE in the executors)

- Hostile = an NPC with stats that is not a pet / mount / `abil.safeWords` role; a player only when the world's PvP flag is on AND
  `trav.players`-style row on AND not in the caster's party. The engine itself cancels player-on-player damage with PvP off.
- Ally = self + party (`class:fn:ally`); "players around you" = non-hostile players in range. Hostile effects never touch party members.
- Mana Barrier converts damage only for its own Mage (Ward: allies get a small shield, not the conversion). Frost Nova freezes players
  only where PvP is on. Bosses: Frost Nova feeds the shared stunlock clock (`armory:fn:stunhit`, published by the armory0123 round).

### 3.9 Lag rules (`research/Code-Structure-Audit.md`)

- Event-driven input: the rune hook runs only on a chain start of type Ability2 / 3; the AbilitySlots guard only on an inventory change.
  No per-tick polling for idle players; the marker-effect fallback polls only players whose loadout is loaded.
- AbilTick = one `EntityTickingSystem` on players, `isParallel` false, one `AbilWorld` list per world behind a tick-stamp guard; zones
  tick every `abil.tick` 0.25 s, damage inside a zone 1 Hz; `abil.maxLive` 48 per world, `abil.maxZones` 2 per player (refuse, never drop a
  paid cast); particles at most every 0.5 s per effect. The HUD sample runs only for players whose HUD asked within 5 s (built).
- No disk I/O on a world thread: the abilities file goes through the private writer (built); the next SkyyClasses build picks up the
  lock-free `bridge()` snippet from `tools/skyycfg.py` (2026-10-13 quick win) automatically.
- Budget: < 1 ms per world tick at 20 players each with a zone + an aura (engine spec 14); measured by probe P13 (section 9).

### 3.10 Server Setup rows (`tools/CONFIG-CONTRACT.md`; SkyWynn Menu -> Server Setup -> Classes; KEEP 10; seconds)

LIVE today: `part.abilities`, `abil.creativeFree`, `abil.castChat`, `abil.refuse`, `abil.cdMessage`, `abil.healCap`, `abil.unlock.a1 /
a2 / a2alt / a1alt`, `abil.hitFallback`, `abil.maxLive`, `abil.safeWords`, `abil.tick`, `abil.maxZones`, `abil.shapes / .sprint / .air`,
`abil.crouchMin`, `abil.airMin`, `abil.landWait`, `abil.ahead`, `abil.channelMove`, `ab.<Ability>.<shape>.mana / .stamina / .cooldown`
and every per-ability number (Meteor power / radius / delay / range, Mana Barrier time / radius / range / ratio / keep / maxAbsorb,
Frost Nova 15 rows, Starfall, Arcane Beam ...).

| New row | Round | Type / default | What |
|---|---|---|---|
| `abil.input` | R4 | choice both / rune / command | which doors cast |
| `abil.vanillaRunes` | R4 | choice block / allow, default block | vanilla runes for classed players |
| `abil.runeHud` | R4 | bool true | mirror the primaries into the vanilla slots |
| `abil.runeCooldownFill` | R4 | bool true (adv) | arm the engine cooldown for the HUD fill (off if U6 fails) |
| `abil.rollCast` | R4 | bool true | a press during the roll casts (sprint shape) |
| `abil.usesCoef / usesExp / maxLevel` | R8 | dec 4.5 / dec 1.5 / int 15 | ability levels by use |
| `abil.useEvery` | R8 | dec 3 s | one counted use per ability per 3 s |
| `abil.perLevel` | R8 | dec 2 % | gain per ability level |
| `mods.pointCosts`, `mods.<id>.steps`, `mods.echo.steps`, `abil.echoDelay` 1 s | R8 | text / dec | the pool spec's numbers |
| `abil.mobVoidStop` | R8 | bool true | Knockback+ / Pull stop mobs at the void edge [Question 6] |
| `abil.costScale` | refine | choice flat / weapon, default flat | ability Mana cost follows the held staff's metal (section 5.4 finding) [Question 3] |

Player `/settings` (Classes): cooldown messages (LIVE), ready sound + flash, hints, hide the Abilities widget when the vanilla slots fill.

## 4. Mage weapons (the magic trio; numbers LIVE in SkyyArmory 0.1.21 / 0.1.22)

Skyy's lock: **Mage = staffs + spellbooks; the wand is the Priest's** (2026-10-04). The framework still knows all three (H and costs come
from one bridge, `armory:fn:info`), so a later "wand for Mages" is a one-line class-rule change [Question 1].

| Weapon | Tap | Hold (= traversal = attack) | Mana (charged) by metal | H = charged damage (no gear level; staff tune 100 % live, 120-125 % next Armory build) |
|---|---|---|---|---|
| **Staff** (Wood .. Onyxium, 8) | quick shot, 1/5 Mana, no pierce, 24 blocks, +15 % per Mana vs the wand | BLINK 16 blocks the way you look (up too, no void check) + a light trail 3 s / 1.5 wide / 30 % of H per second; costs the staff's Mana + 5 Stamina (2 : 1), nothing if it does not move you | Wood 10, Copper 20, Iron 30, Thorium 50, Cobalt 80, Adamantite 120, Mithril / Onyxium 170 | 25 / 56 / 88 / 150 / 244 / 369 / 525 / 525 (x tune) |
| **Spellbook** (Copper .. Onyxium, 7) | - | key 0 PAGE BURST (lobbed orb, area, per-target k = 0.4 x the staff's damage per Mana) 0.5 s between casts; 1 s hold = LEVITATE (up ~8, hover ~3 s, no fall damage) | Burst B = ~30 % of the pool at the band: Copper 40, Iron 55 ... Mithril / Onyxium 130 | **H = the same-metal staff** (SkyyClasses 0.1.16 fix round) |
| Wand (Priest) | quick shot pierces, 32 blocks, 50 % past 16 | hop back + orb burst + heal aura where you land (5 s); signature = ricochet 8 | Wood 5, Copper 10, Iron 15, Thorium 25, Cobalt 40, Adamantite 60, Mithril / Onyxium 85 | 25 / 56 / 88 / 150 / 244 / 369 / 525 |

Every Mage ability reads H from the weapon in hand at the cast; after that the weapon may be swapped (the Meteor still lands, a Beam
channel ends on a swap).

## 5. The Mage on the framework

### 5.1 Role + identity

Burst damage + survival, glass cannon (Skyy): high damage per Mana, range + mobility (blink, Levitate), low Health + defence (Cloth).
Owns 4: A1 Meteor, A2 Mana Barrier, A2-alt Frost Nova, A1-alt = Starfall OR Arcane Beam (pick locks the other). Equips 2 primaries
(default Meteor + Mana Barrier) + 2 alts on crouch. Priest heals keep the Mage alive in a party; solo the Mage lives on Mana Barrier +
Frost Nova + blink.

### 5.2 The five abilities, every shape (LIVE numbers = the chart; costs = Mage split 78 / 22 of the "power" number)

Power = the old Mana-only number; Mana = power x 0.78, Stamina = power x 0.22 / 4, rounded, min 1 (`research/Class-Power-Split.md`).

| Ability | Shape | Cost (Mana + Stamina) / CD | What it does |
|---|---|---|---|
| **A1 Meteor** (Lv 1) | walking | 23 + 2 / 14 s | spot within 25 blocks; after 1 s a meteor hits 4 blocks for **3.0 H** |
| | sprinting "Comet" | 23 + 2 / 14 | lands 1 s later 6 blocks ahead of your run, 3 blocks |
| | mid-air "Under Me" | 23 + 2 / 16 | lands where you land, with your landing (waits at most 2 s) |
| | crouch alt "Meteor on Me" | 20 + 1 / 14 | on you, 0.5 s, 5 blocks, 2.5 H, you take none |
| **A2 Mana Barrier** (Lv 10) | walking | 16 + 1 / 30 s | a see-through dome where you look (<= 8 blocks), 4 blocks, **12 s**; inside, damage to you costs **Mana instead of Health, 1 Mana per 2 HP**; ends at 0 Mana (keeps 4) / 100 % max Health soaked / 12 s |
| | sprinting "Barrier Ahead" | 16 + 1 / 30 | 6 blocks ahead on your path |
| | mid-air "Landing Dome" | 16 + 1 / 30 | at your landing spot |
| | crouch alt "Pocket Dome" | 14 + 1 / 28 | 4 blocks on you, 10 s, 2.5 HP per Mana |
| **A2-alt Frost Nova** (Lv 20) | walking | 19 + 1 / 22 s | freeze enemies within 5 blocks 2 s (a hit breaks it after 1 s, +0.5 H), then Chill 3 s; **1.0 H**; bosses only chilled until the stun clock bridge lands |
| | sprinting "Frost Wake" | 19 + 1 / 22 | a 2 x 8 freezing strip behind you for 3 s, freeze 1.5 s |
| | mid-air "Frost Drop" | 19 + 1 / 24 | the nova on landing, 6 blocks, 1-block push |
| | crouch alt "Deep Freeze" | 20 + 1 / 24 | 4 blocks, freeze 3 s, unbreakable 2 s |
| **A1-alt A Starfall** (Lv 30) | walking | 28 + 2 / 18 s | 12 stars over 3 s on 6 blocks you aim at, each **0.3 H** (~4 hit one enemy = 3.6 H) |
| | sprinting "Star Trail" | 28 + 2 / 18 | the stars fall along your path |
| | mid-air "Starfall Below" | 28 + 2 / 20 | under you, 7 blocks, 12 stars in 2 s |
| | crouch alt "Star Shower" | 31 + 2 / 22 | on you, 6 blocks, 16 stars over 4 s, you cannot move |
| **A1-alt B Arcane Beam** (Lv 30) | walking | 23 + 2 / 18 s | channel a 20-block beam up to 3 s, ramp 0.5 / 1.0 / 1.5 H per second = **3.0 H**, single target; ends on a swap / move past `abil.channelMove` |
| | sprinting "Sweep Beam" | 22 + 2 / 18 | 15 blocks, 2 s, flat 1.5x, wider, you keep moving |
| | mid-air "Beam Down" | 23 + 2 / 20 | aimed below, 12 blocks, 2 s, slow-fall while channelling |
| | crouch alt "Focused Beam" | 27 + 2 / 22 | 25 blocks, 4 s, ramp to 3.5x, you cannot move |

Per ability level (R8): +2 % damage (Meteor Lv 15 = 3.84 H); Mana Barrier +0.05 HP per Mana (2.0 -> 2.7); Frost Nova freeze +0.03 s.
Modifiers offered (R8): Meteor = Radius+ / Power+ / Lingering / Split / Echo; Starfall = Duration+ / Radius+ / Echo / Power+; Arcane
Beam = Pierce / Duration+ / Power+ / Slow; Mana Barrier = Duration+ / Power+ / Ward / Follow / Knockback+; Frost Nova = Radius+ /
Duration+ / Slow / Power+ (`research/classes/Mage.md`).

### 5.3 How the Mage plays at level 1 / 25 / 50 (derived; Sorcery level = gear level, Overall = half)

| | Sorcery 1 | Sorcery 25 | Sorcery 50 |
|---|---|---|---|
| Max Mana (45 + 10 L, + 0.2 per Overall level) | **55** | **~300** | **~550** |
| Mana regen out of / in combat (5 / s x (1 + 7 % per level above 20) x 0.75 in combat) | 5.0 / 3.75 per s | 6.75 / 5.1 | 15.5 / 11.6 |
| Max Stamina (10 + 4 + 0.05 L) | 14 | 15 | 16.5 |
| Weapon (band) | Wood staff (1-13), 10 Mana a charged shot, 2 a tap; Copper spellbook from Lv 10 | Cobalt staff (25-38), 80 Mana; Cobalt spellbook B ~75 | Mithril staff (40-49), 170 Mana; Mithril spellbook B 130 |
| H (one charged shot, with SkyyGear level, tune 100 %) | ~25 | ~650 | ~1,800-1,900 |
| Charged shots from a full pool | 5 | 3 | 3 |
| Meteor damage / casts from a full pool | ~75 in 4 blocks / 2 | ~1,950 / 13 | ~5,500 / 23 |
| Owned abilities | Meteor only (Mana Barrier at 10) | Meteor, Mana Barrier, Frost Nova (alt on crouch) | all 4 (one A1-alt picked at 30) |
| Mana Barrier soaks | 2 HP per Mana: ~110 HP from the pool, capped at 100 % max Health (~125) | ~600 HP, cap = max Health (~470) | cap = max Health (~1,500) |
| Feel | one Meteor, a few shots, blink away, regen 6 s to a full pool: pokes and runs | Meteor on cooldown (14 s) with Mana to spare, charged shots are the expensive big hit, Frost Nova covers the retreat | the pool is never the limit; cooldowns are. Starfall vs Beam = AoE vs boss; Pocket Dome = the "oh no" button |

Reading: at Lv 1 the Mage is Mana-limited (the lock "affordable when unlocked" holds: 2 Meteors from a full pool); from Lv 25 the
cooldowns limit, as intended for a burst class.

### 5.4 Balance findings for the refine round (numbers, not builds)

1. **Flat ability costs vs the metal ladder.** The chart's "2.0x the staff's damage per Mana" cap was computed at the Wood staff (0.10 H
   per Mana). At Cobalt a charged shot is 1 H for 80 Mana (0.0125 H per Mana) while Meteor stays 3 H for 23 Mana = **10x** the staff's
   damage per Mana; at Mithril 25x. Mana then limits only the weapon, never the abilities. Options: (a) keep flat costs - abilities are the
   Mage's Mana sink, charged shots the expensive nuke [default until Skyy has felt Lv 25]; (b) `abil.costScale = weapon`: ability Mana =
   power x (the held staff's charged Mana / 10), i.e. Meteor 23 at Wood, 46 Copper, 69 Iron, 115 Thorium, 184 Cobalt, 276 Adamantite,
   391 Mithril - at Lv 25 (300 pool) 1.6 Meteors, at Lv 50 (550) 1.4 - too harsh; (c) a gentler `abil.costScale = level`: cost x (1 +
   0.03 x Sorcery level) (Lv 25 Meteor 40, Lv 50 58) keeps ~7-9 casts per pool. [Question 3: default (a) now, (c) if Skyy says
   abilities feel free at Lv 25]. The chart gets a "Mana per cast vs pool by level" line either way.
2. **Staff tune 120-125 %** (Skyy 2026-10-03) is still 100 in the live file; the armory0123 round ships the new default. H in 5.3 grows
   ~22 % then; the ability multiples do not change.
3. **Mana Barrier cap** 100 % max Health per cast = "one health bar"; with a Mithril pool (550 x 2 = 1,100 HP) the cap binds before the
   Mana does - fine (the Arcanist C3 node later trades the ratio for a burst).
4. **Starfall vs Beam**: 3.6 H spread vs 3.0 H single; with +2 % per level both end ~4.6 / 3.84 H; Beam's crouch shape (ramp 3.5x over
   4 s = ~5 H) is the biggest single-target number the Mage has - watch it in the test.

## 6. The two missing framework layers (built on the Mage first)

### 6.1 Ability levels by use (R8a, SkyyClasses)

- A use counts when the ability **did something** (Meteor / Starfall / Beam / Frost Nova: hit >= 1 enemy; Mana Barrier: soaked >= 4 HP),
  at most one per `abil.useEvery` 3 s; echoes never count. Level n at round(4.5 n^1.5) uses (Lv 2 13, Lv 5 50, Lv 10 142, Lv 15 261;
  1,570 total). Each level = +`abil.perLevel` 2 % of the main effect (cap Lv 15) and 1 modifier point from Lv 2 (14 points).
- Saved per profile in the abilities file (section 3.4); the Abilities page shows "Meteor Lv 4 - 37 / 50 uses"; the HUD widget shows
  the level next to the name (text only).

### 6.2 Modifiers + Echo (R8b)

- Per ability: 4-5 offered (Mage list in 5.2), each unlocked and levelled with THAT ability's points (Lv 1-3 cost 1, Lv 4-5 cost 2 = 7 to
  max one; 14 points = two maxed), 2 equipped at a time, swap free out of combat, no doubling. Forbidden pairs refused at equip.
- Steps = `research/cloud/Modifier-Pool-Spec.md` section 2 (Power+ +5 / 10 / 15 / 20 / 25 %, Radius+ +0.5 block per level, Duration+,
  Efficiency -5 .. -25 % never below 50 % cost, Split 3 copies @ 45 %, Lingering zone, Slow, Knockback+, Ward, Follow, Pierce +1 / level).
- **Echo** = the same executor runs again `abil.echoDelay` 1 s later at 20 / 22.5 / 25 / 27.5 / 30 % strength, without the other
  equipped modifier, costs nothing, no cooldown, never counts as a use, never echoes an echo; dropped if the caster is gone. Meteor:
  repeat at the same spot; Starfall: a second, weaker shower.
- Numbers resolve once at the cast: `F = base x (1 + perLevel x (level - 1)) x tree(F) x mod(F)`; different fields multiply, the same
  field adds; the chart's caps hold (Meteor + Power+ 5 + Echo 5 = 1.98x per Mana).
- Page: the LIVE `/cast page` grows a "Modifiers" card per owned ability (inline, `tools/skyyui.py`, out of combat only). Loadouts
  (SkyyWardrobe) carry the equipped pair (the `mods` part of `class:fn:loadoutGet/Set` is already reserved).

### 6.3 Class-tree ability nodes (R9, SkyyTrees 0.3.6 texts + SkyyClasses reads; `research/cloud/Class-Tree-Paths.md` section 3)

Mage nodes the engine reads at the cast through `tree:fn:bonus` and lists in `tree:reads:SkyyClasses`: T4 Barrier Lore (ratio +0.2),
T6 Quick Hands (-5 % cooldowns), R3 Phase Step (cast = blink 5 back + the dome follows you at full strength; Follow modifier then not
equippable; dome 10 s), R4 Meteor from the Rift, L2 Prism (Starfall stars split), L3 Beam Focus (refracts to a second target), L4
Brilliance (10 % Mana back on 3+ enemies), L5 Sunburst, C1 Overcharge (+15 % at full Mana), C2 Siphon (kills +3 Mana), C3 Charged Dome
(the dome stores the drain and bursts 50 % on end; ratio 1 per 1.5), C4 Deep Beam (ramp 4x, +0.5 s, +10 Mana), C5 Arch-Mage (star well
pull). Blink / trail nodes stay SkyyArmory's (live since 0.1.9). Node ids never change; texts that differ from the live 0.3.5 are the
Class-Tree-Build-Map section 9 list.

## 7. Build phases (rounds; every round = patch script on the previous generated script, harness, review, crosscheck, lint, smoke)

| Phase | Round | Mods | What | Size |
|---|---|---|---|---|
| **A. Mage weapons on 0.7** | `armory0123` (RUNNING) | SkyyArmory 0.1.23 | the full build script on the 0.7 assets (staff vars, particles, wand timing), staff tune 120-125 % default, `armory:fn:stunhit` published, TravTick gated on "Armory item in hand" | full (running) |
| **B0. First Mage test on `/cast`** | none (Skyy) | - | Skyy runs `TEST-CHECKLIST` item 11 on 0.7 today (section 8 part 1) - the five abilities are live; the keys are not needed to feel the numbers | - |
| **B1. 0.7 ability probe** | `abilprobe` | NEW SkyyAbilityProbe 0.1 (admin, removed after) | P1 chain event + cancel, P3 CooldownHandler fill, P4 slot writes survive death / world / relog, P14 profile leak, P15 Mana max, P13 scan cost; ~8 min for Skyy (`research/cloud/Ability-Probe-Plan.md` session B) | lean |
| **B2. The real keys** | `abil04` | SkyyClasses 0.1.20 (+ SkyyProfiles 0.1.11 if P14 shows the leak; SkyyHud 0.3.19 if the vanilla fill works and the widget needs a "hide when vanilla shows" switch) | section 3.2: asset pack on, 5 Mage rune items + icons, cast roots, the chain-start hook + cancel, the slot mirror + guard, vanilla-rune block, `abil.input / vanillaRunes / runeHud / runeCooldownFill / rollCast`; Priest runes ride along (their abilities are live too) | **full** (items, several hooks, saved data) |
| **C. Mage refine** | `mage-refine` (after Skyy's B0 + B2 tests) | SkyyClasses 0.1.21, SkyyArmory if weapon numbers move | every number Skyy names; `abil.costScale` if asked; visuals from the vanilla rune FX + the Exotic Weaponry study; chart republished | lean, repeated |
| **D. Levels + modifiers + Echo** | `abil-mods` | SkyyClasses 0.1.22 (+ SkyyWardrobe 0.2.2 for the `mods` part) | section 6.1-6.2, Mage + Priest modifier lists, the Modifiers card; `simplify: 2` | full (saved data, new system) |
| **E. Tree nodes** | `abil-tree` | SkyyTrees 0.3.6 + SkyyClasses 0.1.23 | section 6.3; Mage first, Priest with it | full (2 mods) |
| **F. Batches** | one round per batch | SkyyClasses + the class's weapon mod | Monk + Assassin (crouch = precise; needs the Armory stun bridge), Warrior + Berserker (snapshot buff / toggle / aura kinds, SkyyGear haste tier bump), Archer (+ Spellblade later) - each batch = its table, executors, shapes, icons, the chart | full per batch |

Deploy order inside a batch: SkyyClasses before SkyyHud (the widget hides without the bridge); SkyyProfiles with B2 if the leak is real.
Rollback floor after B2: once Skyy runes exist in player slots, never roll SkyyClasses below 0.1.20 without `abil.runeHud` off and one
login (the guard deletes stray `SkyyAbility_` stacks; an older jar would leave them as dead items).

## 8. Test plan for Skyy (exact in-game steps)

**Part 1 - today, `/cast`, Mage on 0.7** (SkyyClasses 0.1.19 is in the SET and crosschecked on 0.7)

1. Be a Mage (any profile), hold a staff, type `/cast list`. Meteor "ready (23 Mana + 2 Stamina, cooldown 14 s)"; the others show "Lv 10 / 20 / 30". Below those levels: `/classadmin abil <you> grant` (admin) unlocks all four for testing.
2. Look at the ground near mobs ~10 blocks away, `/cast 1`. A ring where you look; ~1 s later the explosion; chat "Meteor hit N enemies (X damage each)"; Mana -23, Stamina -2. Tell me X and your staff's charged-shot damage (tooltip): X should be ~3x.
3. `/cast 1` again at once -> "Meteor is ready in 14 s" + a click. Hold food, `/cast 1` -> "Hold your Mage weapon".
4. Hold a spellbook, cast Meteor: X matches the same-metal staff.
5. `/cast 2` (Mana Barrier): a faint ring where you look. Stand in it, let a mob hit you: Health stays, Mana drops ~1 per 2 damage; step out: Health drops. Stay until Mana runs out: the dome ends with a line. Is the ring "visible but easy to see through"?
6. Hold crouch, `/cast 1` (= Deep Freeze if Frost Nova is unlocked, else "No alt yet"): mobs around you freeze ~3 s. If chat typing drops your crouch, use `/cast 3`.
7. `/classadmin shape 3 walk` next to mobs: frozen ~2 s, then slowed; a hit breaks the ice (+ a little damage). A boss: only slowed (expected until the Armory stun bridge).
8. `/classadmin shape 1 sprint` while running: the meteor lands ~6 blocks ahead. `/classadmin shape 1 air`, jump: it falls where you land.
9. Look at the ground, `/classadmin shape 4 walk`: Starfall - ~12 small explosions over 3 s. `/cast page` -> Ability 1 alt card -> Switch -> Arcane Beam -> `/classadmin shape 4 walk` at a mob: damage grows each second; swap to food: it stops.
10. Open `/skyyhud`: the Abilities box shows Meteor + Mana Barrier with costs; after a cast the row counts down with a bar; crouch ~2 s: the rows change to your alts.
11. Server Setup -> Classes -> Ability numbers: set Meteor cooldown 0, cast three times from full at Sorcery 1-5: the third says "Not enough Mana". Put it back to 14.
12. Log out and in: `/cast 1` still shows the cooldown left.
13. Say what felt wrong: damage too high / low, Meteor too slow, the dome too faint, costs. Those become phase C.

**Part 2 - after B2 (the keys)**

14. Mage with a staff: press your Use Ability 2 key (Q on your binds): Meteor casts, no typing. Use Ability 3 (your bind): Mana Barrier. The game's two ability slots beside the signature meter show the Meteor and Barrier icons. Does the slot fill with the cooldown, or only our widget?
15. Hold crouch + Ability 2: Deep Freeze (or "No alt yet" below Sorcery 20). Crouch + Ability 3 at Sorcery 30: your picked A1-alt.
16. Press Ability 2 with no weapon / with food: nothing happens, a fail sound, one line.
17. Press sprint and Ability 2 together: you roll and the Comet casts (or only the roll - tell me; then mid-roll cast is dropped).
18. Open the Runebinder's Lattice (`/abilities` as admin or the bench): the two Skyy runes sit in the Ability 1 / 2 slots; drag one to the bag - it snaps back. `/abilities give` a vanilla Fireball, slot it: refused with the weapon-lock popup.
19. Switch to another profile (Warrior): the slots are empty / the Warrior's; back to the Mage: Meteor + Barrier again.
20. Die, change world (`/hub`, `/island`), relog: the slots and `/cast list` are unchanged.

**Part 3 - after D (levels + modifiers)**

21. Cast Meteor on mobs 13 times over a few minutes (one counted use per 3 s): `/cast page` shows "Meteor Lv 2, 1 point". Unlock Power+ (Lv 1), equip it: the damage line is +5 %.
22. Unlock Echo on Meteor, equip Power+ + Echo: a second, weaker meteor 1 s after the first on the same spot; the use count does not rise for the echo.
23. Try to equip a third modifier: refused. Swap the pair in combat: "Leave combat first".

## 9. Risks

| Risk | Why | Mitigation |
|---|---|---|
| The release's rune codec differs from the pre.4 research (Core / AbilityKeywords; no `Weapons`) | the research is from 0.7.0-pre.4 | the build reads the release `ItemAbility` codec at build time and stops on an unknown shape; the class gate is code, not data |
| Cancelling a chain leaves a stuck client animation | UNVERIFIED (U3) | fallback: cost 0 roots do nothing on their own; refuse in our pipeline with the sound only |
| The vanilla slot fill never shows our cooldown | `CooldownHandler` access path INFERRED | the SkyyHud widget is the display; the slot still shows the icon |
| Runes leak across profiles | SkyyProfiles saves 6 sections | the mirror rewrites 0 / 3 on every switch; vanilla runes blocked for classed players; SkyyProfiles -11 / -12 snapshot in B2 if P14 fails |
| Flat ability costs make the Mage's charged shots pointless past Lv 25 | section 5.4 | Question 3; a row flips it |
| Mobs pushed into the void by Knockback+ (D) | Skyy's "no void protection" is for traversals (players) | `abil.mobVoidStop` true [Question 6] |
| The Abilities widget + the vanilla slots show the same thing twice | two displays | player switch to hide the widget once the vanilla fill works |
| A dragged-out Skyy rune ends in a chest / AH | guard misses a path | the guard deletes every `SkyyAbility_` stack outside section -11; SkyyGear / Bazaar / AH skip items with an `Ability` block (Runes research 4.3) |
| SkyyClasses ships an asset pack for the first time | new to this mod | the Armory / Skills pack pattern (`IncludesAssetPack` true, clash check against every live-set jar) |

## 10. UNVERIFIED items - each with its probe step (SkyyAbilityProbe 0.1 on 0.7, one ~8 minute session; Skyy 2026-10-08: "wait till 0.7")

| # | Item | Probe |
|---|---|---|
| U1 | the release rune has no `Weapons` field; a `Cost 0 / CostType None` Core rune with a 1-step marker root shows in the HUD and casts with any weapon | B2 build-time codec read + P1 in game: `/aprobe p1`, press both keys, read the `[AbilityProbe] Ability2 / Ability3` lines |
| U2 | the vanilla HUD loads `Icons/Abilities/<RuneItemId>.png` from our asset pack | B2 first run: the two slots show our icons (else the generic rune icon) |
| U3 | `InteractionChainStartEvent` fires for the rune keys on the release jar and cancelling it leaves no stuck animation / no vanilla cooldown / no Mana spent | `/aprobe p1 cancel`, press a key: no animation, "PASS: nothing spent" |
| U4 | an Ability press during the sprint-press roll reaches the server with `sprinting` set | `/aprobe p1`, sprint + Q together: a line with "sprinting y" and "rolling y" |
| U5 | rune sections -11 / -12 follow the player across SkyyProfiles profiles | `/aprobe p14`, switch profile, `/aprobe p14` |
| U6 | the player's `CooldownHandler` is reachable and a code-set cooldown (root id, seconds) fills the vanilla slot | `/aprobe p3`, cast a vanilla rune, `/aprobe p3 read <Cast id>`, then `/aprobe p3 cooldown <Cast id> 8` - does the slot fill 8 s? |
| U7 | the Fireball impact FX / sound ids and the frost effect ids exist under the same names on the release | the build lists them (`/aprobe info`); a missing id = the build stops |
| U8 | AbilitySlots writes from code respect the slot filters and survive death / world switch / relog; `InventoryChangeEvent` fires for bench drags | `/aprobe p4 put 0 <rune>`, die / `/hub` / relog, `/aprobe p4 read`; `/aprobe p4 watch` + a drag |
| U9 | `/skills mana` max = 45 + 10 L on 0.7 (the vanilla 100 not added) | `/aprobe p15` + `/skills mana` |
| U10 | sphere-scan cost at 48 zones x 4 Hz on Skyy's PC; world ticks per second | `/aprobe p13` among mobs: "PASS" + the TPS line |
| U11 | Ability 3's default bind on a stock client (Skyy: Q = Ability 2, Mouse 5 = Ability 1 - log 2026-10-08) | Skyy reads Settings -> Controls once; hints name the ACTION, not a key |

## 11. Questions for Skyy (each with a recommended default)

| # | Question | Recommended default |
|---|---|---|
| 1 | Mage weapons stay staffs + spellbooks (the wand is the Priest's)? The framework can give Mages wands with one class-rule line. | **[Keep the lock: staffs + spellbooks]** |
| 2 | Vanilla 0.7 runes (Fireball, Chain Hook ...) for players who have a class: blocked, or usable next to class abilities? | **[Blocked - class abilities only; classless players keep them]** |
| 3 | Ability Mana costs: flat (Meteor 23 at every level, abilities = the Mana sink, charged shots = the expensive nuke), or growing with Sorcery level (~+3 % per level: 40 at Lv 25, 58 at Lv 50)? | **[Flat now; decide after you feel Lv 25 in the test]** |
| 4 | Test order: run the five Mage abilities with `/cast` today (part 1), then the keys round, or wait for the keys before testing anything? | **[Test with /cast today - the numbers do not need the keys]** |
| 5 | Cooldowns survive a relog but reset on a server restart? | **[Yes, memory only]** |
| 6 | Knockback+ / Pull on mobs near the void: stop them at the edge, or let them fall (like "no void protection")? | **[Stop at the edge; one row flips it]** |
| 7 | When the vanilla ability slots show our icons + cooldown fill, keep the SkyyHud Abilities widget on by default (it also shows alts, levels, stacks) or hide it? | **[On by default; a player switch hides it]** |
| 8 | Ability levels: cap 15 and 14 points (= two modifiers maxed per ability)? | **[Yes, 15 / 14]** |
| 9 | Echo strength 20-30 % on every Echo (keeps Meteor + Power+ + Echo inside the 2.0x per-Mana cap)? | **[Yes, 20 / 22.5 / 25 / 27.5 / 30 %]** |
| 10 | Batch order after the Mage: Priest (already built, same engine) + Monk + Assassin, then Warrior + Berserker, then Archer (+ Spellblade when its weapons exist)? | **[Yes, in that order]** |
| 11 | Mana regen on 0.7: keep 5 / s (our tuned rate) or vanilla 0.7's 3.3 / s? (open since SkyySkills 0.4.31) | **[Keep 5 / s]** |

Change log: 2026-10-13 file created (Fable spec round; sources read read-only: docs/answered classes / skills / ui, research/classes/Mage.md,
Class-Roles-Ideas, Mana-Cost-And-Regen-Research, Swing-Speed-Spec, Code-Structure-Audit, Inventory-Offhand-0.7, Hytale-Runes-Research,
Class-Power-Split, research/cloud Class-Ability-Engine-Spec / Spec-Draft / Shapes / Ability-Engine-Plan / Ability-Input-Design /
Ability-Probe-Plan / Modifier-Pool-Spec / Class-Tree-Paths, the live build scripts of SkyyClasses 0.1.19, SkyySkills 0.4.31, SkyyArmory
0.1.21 / 0.1.22, SkyyHud 0.3.18, tools/skyyui.py, CONFIG-CONTRACT, PROFILES-CONTRACT, the class balance chart, Mod-Database + mod_check, and
the Hytale 0.7.0 release Assets.zip + HytaleServer.jar strings).
