# Weapon signatures (Ability 1) - inventory, tooltip rule, UT + Mythic plan

Spec, 2026-10-23. No code. Where it goes next: build rounds `sig1`-`sig4` (section 5.1); answers to section 7 go to `docs/answered/gear.md`
(`python tools/qa_append.py gear ...`). Every class file in `research/classes/` has a short "Weapon signature (Ability 1)" section that points here.

Skyy (2026-10-23, docs/answered/classes.md 230 + gear.md 323):
- "i was looking at the priest.md and it doesn't say what the wands ability 1 that is tied to your weapon does."
- "i was thinking, the ability 1 tied to the weapons would be perfect to use for UT and mythic gear to set them apart. some could have a new
  special or different ability. and some could be the same, and just take a lot less to charge! (make sure you include the ability 1
  description in the flavor text of every weapon. what it does, and what iot takes to charge up."

Decisions followed (not re-decided): gear.md 108-110 (every weapon keeps its vanilla signature on Ability 1, charged by use; the charge is
kept per weapon on a swap; wands = ricochet through 8), gear.md 128 popup batch 2 SIGNATURES "Recommended set" (Bo = Whirling Staff,
wraps / gauntlets = Flurry, kunai = Kunai Fan, spellbook = Page Storm - LOCKED 2026-10-08, **never built**, section 1.3), classes.md 153
(Ability 1 = the weapon signature; Ability 2 / 3 = class abilities). **Replaces** one line of `research/cloud/Untiered-Mythic-Spec.md` 2.1
("every Mythic has ONE hook ... never a class ability or a signature"): Skyy's 2026-10-23 words make the signature the UT / Mythic difference.

## 0. How a signature works (VERIFIED in Assets.zip + HytaleServer.jar, 2026-10-23)

- The meter is the player stat `SignatureEnergy` (Min 0 / Max 0). The HELD weapon's `Weapon.StatModifiers.SignatureEnergy` (Additive) sets
  its max = the meter size, per item id, in the item JSON.
- Every vanilla signature root starts with `StatsCondition { Costs: { SignatureEnergy: 100 }, ValueType: Percent }` then `ChangeStat -100 %`:
  it needs a FULL meter and empties it. So **meter size = the charge cost**; a smaller meter = fewer hits.
- It fills from `EntityStatsOnHit { EntityStatId: SignatureEnergy, Amount: N }` on the weapon's damage steps (and on bow projectile configs).
- Bows / crossbows: Ability 1 turns the full meter into `SignatureCharges` (an "armed" big shot); the NEXT primary shot fires it.
- Engine check (bytecode `StatsConditionInteraction.canAfford` + `EntityStatValue.asPercentage`): when max = min = 0, the percentage is 0, so
  a 100 % cost is **never** affordable - a weapon with an Ability 1 root but no meter can never use it (section 1.2 "dead meter").
- The item JSON inheritance is top-level: a child that writes its own `Interactions` or `Weapon` block REPLACES the parent's whole block
  (SkyyArmory `item_resolved`, build_skyyarmory_0.1.43.py 2992). That is why several pack weapons lost their signature (1.2).
- Pack armor note: 179 The Armory armor pieces (Calvary etc.) carry `Regenerating SignatureEnergy 0.5 % / s` - the meter also fills over time
  while worn. A precedent for "charge over time" lines (not ours; runtime-id only).

## 1. Inventory - what each weapon's Ability 1 does today and what charges it

Numbers = vanilla 0.7 (Assets.zip, read-only). "x w" = SkyyGear's swing-tier hit weight (0.2.6 fix round: every per-hit stat gain of a melee
tier hit is multiplied by w, so the meter fills per SECOND the same at every speed tier; `build_skyygear_0.3.41.py` 2290, 10609).

### 1.1 Vanilla families

| Family (class) | Ability 1 = signature | What it does (plain) | Meter | What fills it (per hit that lands) | Hits to full (about) |
|---|---|---|---|---|---|
| Sword (Warrior) | **Vortexstrike** | spin slash around you, then a lunging stab forward | 20 | swing +1, thrust +3 (x w) | 12-20 |
| Battleaxe (Berserker) | **Whirlwind** | spin again and again, hitting everything around you while you move | 9 | swing +1, downstrike +2 (x w) | 5-9 |
| Mace (Berserker) | **Groundslam** | leap up and slam down: hits and knocks up everything around where you land | 8 | swing +1, charged swing +2 (x w) | 4-8 |
| Daggers (Assassin) | **Razorstrike** | lunge, slash, sweep - three fast cuts; from behind they backstab (x1.5) | 27 | swing +1, stab +2, Pounce hit +6 (x w) | 5-27 |
| Shortbow (Archer) | **Volley** | arms the bow: your next arrow fires as a 3-arrow spread | 6 | +1 per FULLY drawn arrow that hits | 6 |
| Crossbow (Archer) | **Big Arrow** | arms one heavy bolt: the next shot hits about 4x harder (Iron 78 vs 20) | 5 | +1 per 3rd bolt in a row on the same target (combo) | 15 bolts |
| Staff - Crystal Flame only (Mage) | **Fire Trap** | places a growing fire circle (5 s, up to 3 traps) | 10 | +1 per fire bolt hit | 10 |
| Dev bow Vampire (Mythic) | **Supershot** | one big life-stealing arrow | 10 | 0.54-3 per arrow by draw (10 steps) | 4-19 |
| Dev bow Bomb (Mythic) | **Boomshot** | an exploding arrow | 10 | as Vampire | 4-19 |
| Dev bow Pull (Mythic) | **Pullshot** | an arrow that pulls the target to you | 10 | as Vampire | 4-19 |
| Dev bow Ricochet (UT) | **Ricochet Trishot** | three arrows that bounce | 10 | as Vampire | 4-19 |
| Dev bow Combat (UT) | **Trishot** | three arrows at once | 10 | as Vampire | 4-19 |
| Dev bow Test Zoom (UT) | **Volley** (template) | as the shortbow | 6 | as the shortbow | 6 |
| Longsword, Spear, Axe, Club, Shield, Staff (others), Spellbook, Wand (vanilla file), Kunai, Claws, Bo (vanilla Bo_Wood / Bamboo) | **none** | the key does nothing | - | - | - |
| Quirks | Blowgun_Tribal inherits the SWORD template (Vortexstrike + meter 20) - a mob weapon; Battleaxe_Scythe_Void has a meter 9 but no Ability 1 (fills for nothing) | | | | |

### 1.2 The Armory (pack, 1.24.2 in Skyy's Mods folder - PACK.md still says 1.23.0; read only, ids only)

| Items | Ability 1 | Meter | State |
|---|---|---|---|
| Recolours `Sword_*` (40), `Mace_*` (30), `Dagger_*` (40), `Weapon_Battleaxe_*` (40), Kweebec signs (3), RuneBladeStage2 / 3 | inherited vanilla (Vortexstrike / Groundslam / Razorstrike / Whirlwind) | vanilla | works as vanilla |
| `Longsword_*` (20), shields (all), `GhostSword` (UT), `Weapon_Elemental_*` x4 (Mythic), `FireWhip` + `ScorpianFlail` (Mythic), `RuneBladeStage1` (Mythic), `Fist`, `TestBroom` | none (own Interactions without Ability 1) | none | the key does nothing |
| `Hepta_Axe` (UT) | none (own Interactions) | 9 (inherited) | meter fills, nothing to spend it on |
| **`Zweihander`** (Mythic), **`LahatChereb`** (Mythic) | Groundslam (inherited) | **0** (own Weapon block has only Health / Stamina) | **dead meter**: the root is there but can never fire (section 0) |
| **`DualRuneBlade`** (Mythic), **`Weapon_Dualswords_Iron`** | Razorstrike (inherited) | **0** (own Weapon block = RenderDualWielded only) | **dead meter** |
| More Crossbow Tiers (Serj, 4 crossbows) | Big Arrow (template) | 5 | works as vanilla |

### 1.3 Our families

| Mod / items | Ability 1 | Meter / fill | Notes |
|---|---|---|---|
| SkyyArmory wands (Copper -> Onyxium + zone metals, 16 incl. UT Second Opinion) + SkyySkills Wood / Rotten / Tribal (0.4.24) | **Ricochet** (`SkyyArmory_Wand_Signature`, 0.1.14) | 20; +1 per quick-shot hit, +2 per charged hit (server side, rows `sig.wand.chargeQuick / chargeCharged`) | a bolt jumps from your aim target to the nearest unhit enemy every 0.15 s, up to 8 hits, 1.5x charged shot, -10 % a bounce; no target = charge back. 12 rows `sig.wand.*` (Server Setup > Armory > "Wand + signature") |
| SkyyArmory zone-metal Sword / Battleaxe / Mace / Daggers / Shortbow / Crossbow (`*_SkyWynn`, `*_Wynn`) | inherited vanilla | vanilla | verified in SkyyArmory-0.1.43.jar |
| SkyyGear UT copies Paperweight (sword), Overtime (battleaxe), Pocket Knife (daggers), Short Notice (shortbow) | inherited vanilla | vanilla | verified in SkyyGear-0.3.41.jar |
| SkyyArmory **Bo** (16 incl. UT Turnstile), **wraps + gauntlets** (20), **kunai** (16), **spellbooks** (15), **staffs** (19 incl. UT Loophole), **Soul Orb + Soul Cages** (16), **Great Shields** (15), zone-metal axes / clubs / longswords / spears / shields | **none** | - | Whirling Staff / Flurry / Kunai Fan / Page Storm were LOCKED 2026-10-08 but never built; staff, soul cage, great shield, axe, club, longsword, spear have no design |
| SkyySkills staff overrides (13), spellbooks (5), Broomstick | none | - | Crystal Flame (vanilla Fire Trap) is not overridden |

### 1.4 What our code already changes

- **SkyyGear 0.2.10** keeps the meter per weapon + hotbar slot across a swap (GearSigSlotSys / GearSigTick / GearSigInvSys; row
  `gear.signatureKeep`, memory only).
- **SkyyGear 0.2.6** multiplies every melee tier hit's `EntityStatsOnHit` (the meter gain) by the swing weight w (`DamageSequence` meta,
  verified bytecode in that round) - the proven hook for "cheaper charge" (section 3.3).
- **SkyyGear 0.2.2** GearBox hides the vanilla "Damage Data - Basic / Signature" box on every gear weapon (empty breakdowns at runtime).
- **SkyyArmory 0.1.14** wand meter + Ricochet; charge added SERVER side (`addStatValue`) on shot hits - the proven hook for our own gains.
- **SkyySkills 0.4.24** Wood wands get the wand signature; 0.4.31 regenerates 0.7's signature "Mana on hit" lines at 1/5 (Groundslam 25 ->
  5 etc.); the crossbow "Crossbows stay loaded" perk keeps the Big Arrow meter.
- Nothing of ours changes a vanilla signature's damage, shape or meter size.

## 2. Tooltip rule - "Ability 1 - <Name>" on every weapon

### 2.1 The block (GearView's Ability section, first in it, above Charged Shot / Charged Attack / Trade-off / Elemental Blade)

```
Ability 1 - Vortexstrike                        bold gold (the section's existing heading style; a UT / Mythic NEW signature: its rarity colour)
Spin slash around you, then a lunging stab.     soft white #d6e4ee, one line, at most ~70 characters
Charge: 20 energy - swing +1, thrust +3         "Charge:" soft white; "20 energy" gold #e8c25a (progress); each +N green #7ee08a
Fills 40% faster (Untiered)                     green - only on a cheaper UT / Mythic (section 3.3), the live % from Server Setup
```
- Weapon with none: one grey `#7f93a6` line `Ability 1 - none` (Skyy: "every weapon").
- Bows: `Charge: 6 energy - +1 per fully drawn hit`. Crossbow: `+1 per 3rd bolt in a row on one target`. Dev bows: `+0.5 to +3 per hit
  (by draw)`. Gains shown AFTER x w and x the cheaper factor, one decimal at most ("+1.4").
- Dead-meter pack Mythics (1.2): the block shows only once `sig.packMeter` gives them a meter (section 3.4); until then `Ability 1 - none`.
- Order and colours = Style Guide section 15; the heading stays the kit's bold gold so the Ability section reads the same on every item.

### 2.2 Who writes it (one writer)

- **SkyyGear GearView** renders the block for every weapon with a gear document (vanilla, ours, pack by runtime id) - the per-stack tooltip
  it already writes (no lang key). It holds the signature TABLE: item id -> signature id, name, one-line text, meter, gains per attack step,
  generated at build time from Assets.zip + the read-only pack jars (asserted against section 1.1 numbers).
- **SkyyArmory** answers for its own signatures through a new bridge `armory:fn:sig` (Object[] {String name, String text, Integer meter,
  String gains, Boolean ready}; plain java.lang types, `skyy.bridge`) - wand Ricochet today, Bo / fists / kunai / spellbooks after `sig2`.
  SkyyGear asks it first for any SkyyArmory-owned id (the `armory:fn:info` pattern) and for the 3 SkyySkills Wood wands.
- **Pack items**: by runtime id only, in SkyyGear's table; never a lang file for their ids.
- **No new lang keys** in either mod (`python tools/ci/langdup.py` stays 0 FAIL). The item's own lang description stays in the flavour slot.
- Unidentified gear: no Ability 1 block (the bag text is fixed when made).

## 3. UT + Mythic signatures

### 3.1 Rule (default)

- **Mythic** (boss chase items) -> a **NEW special signature** where our code owns the item; pack Mythics we cannot re-root -> the same
  signature, **much cheaper**.
- **Untiered** -> mostly the **same signature, cheaper**; a NEW one only where the UT's identity needs it (Second Opinion, Loophole,
  Turnstile below).
- A NEW signature never copies a class ability (Warrior Rallying Guard / Shield Shockwave, Mage Meteor / Mana Barrier / Frost Nova /
  Starfall / Arcane Beam, Priest Sacred Heal / Shield Bubble / Sanctuary / Martyr's Grace / Guardian Spirit, Berserker War Cry / Whirlwind
  (class), Monk Flowing Form / Palm Strike / Hundred Fists / Cyclone Kick / Still Water, Archer Pinning Shot / Rapid Fire / Explosive Arrow,
  Assassin Cloak / Toxin / Shadow Clone / Vanishing Act / God Killer, Spellblade Rift Cleave): a weapon move, damage told as "x one hit",
  charged only by hits, no Mana.
- Four power sources: a signature is part of the WEAPON source; its damage scales with the weapon's levelled hit (like the wand: x its
  charged shot), so gear / accessories / pets that raise damage raise it too - no separate scaling.

### 3.2 Per item

| Item (owner) | Rarity | Today | Plan | Why |
|---|---|---|---|---|
| The Paperweight sword (Gear) | UT | Vortexstrike | **cheaper** | slow heavy swings = fewer hits; cheaper keeps it on par |
| Overtime battleaxe (Gear) | UT | Whirlwind | **cheaper** | |
| The Pocket Knife daggers (Gear) | UT | Razorstrike | **cheaper** | |
| Short Notice shortbow (Gear) | UT | Volley | **cheaper** | |
| The Second Opinion wand (Armory) | UT | Ricochet | **NEW "Second Opinion"**: the ricochet also bounces through ALLIES in range and heals each for the hit it would deal (enemies still take it, -10 % a bounce) | its whole idea is healing; cheap to build (Rico picks allies too) |
| The Loophole staff (Armory) | UT | none | **NEW "Loophole Lance"**: one beam through every enemy in a 24-block line, 2x the charged shot each | staffs have no signature; the UT is "pierce" |
| The Turnstile Bo (Armory) | UT | none | **NEW "Revolving Door"**: Whirling Staff that first pulls enemies in 4 blocks, then flings them out (its knockback x2) | the UT is knockback |
| Dev bows Ricochet / Combat / Test Zoom (vanilla id) | UT | own vanilla | **cheaper** | they are already unique |
| Hepta Axe, Ghost Sword (Armory pack) | UT | none | **none** (shown as `Ability 1 - none`) unless Q4 | no Ability 1 root; we may not ship their files |
| Dev bows Vampire / Bomb / Pull (vanilla id) | Mythic | own vanilla | **cheaper (Mythic %)** | already unique; vanilla files - one writer issue |
| Zweihander, Lahat Chereb (pack) | Mythic | dead Groundslam | **pack meter + cheaper** (3.4) | brings back the signature they were meant to have |
| Dual Rune Blade (pack) | Mythic | dead Razorstrike | **pack meter + cheaper** | |
| Elemental swords x4, flails, Rune Blade 1 (pack) | Mythic | none | **none** unless Q4 | no Ability 1 root |
| UT-28 weapons 13-28 (`research/cloud/UT-28-Build-Sheet.md`) | UT | as their family | **cheaper**, except: 17 Hotspring Blessing -> NEW "Warm Spring" (Ricochet that leaves a 3 s heal puddle at each bounce), 26 The Stormfossil -> NEW "Fossil Storm" (Thunder Loophole Lance), 28 Crushing Tail -> NEW "Tail Sweep" (Whirling Staff, one big knock-down ring) | built in their own round; families without a signature get it once `sig2` / `sig4` lands |
| Own Mythic specials (`research/cloud/Own-Specials-Draft.md`, 21, none built) | Mythic | - | **NEW each**, designed with the item; first ideas in 3.5 | boss chase items |

### 3.3 "Cheaper" = the meter fills faster (Server Setup)

- Implemented as a GAIN multiplier, not a smaller meter: the meter size is client-predicted asset data (a read-only row, like
  `sig.wand` meter), a gain multiplier is server-side and live. Cheaper by p % = every gain x 100 / (100 - p) (40 % -> x1.67, 60 % -> x2.5).
- Rows (SkyyGear, Server Setup > Gear > Rarity, live, new keys - a missing line = the default, no migration):
  - `sig.cheaper.ut` int 0-90 %, default **40** - "Untiered signatures fill this % faster".
  - `sig.cheaper.mythic` int 0-90 %, default **60** - "Mythic signatures fill this % faster".
  - `sig.cheaper.items` text `id:pct,...` (empty) - one item's own %, wins over the rarity row (0 = same as a normal weapon).
  - `sig.tooltip` bool, default on - the Ability 1 block.
- Where: SkyyGear's existing x w step (melee tier hits) gets x cheaperMult(stack rarity / id). Bow / crossbow projectile gains and hits
  outside the tier path (UNVERIFIED that the x w step sees them) get the same extra through a top-up: after the engine's gain, add
  gain x (mult - 1) with `addStatValue` (the SkyyArmory wand pattern), capped at the max. SkyyArmory's own server-side gains (wand +1 / +2,
  later Bo / fist / kunai / book) read the multiplier from a new bridge `gear:fn:sigMult` (Object[] {id, stack metadata} -> Double).
- Never above the meter max; never on a mob holder; the kept-on-swap value (0.2.10) is unaffected.

### 3.4 Dead-meter pack Mythics (no files shipped)

- `sig.packMeter` (SkyyGear, bool, default on) gives the holder of `Zweihander`, `LahatChereb` (meter 8 = Groundslam) and `DualRuneBlade`,
  `Weapon_Dualswords_Iron` (27 = Razorstrike) a named player stat modifier `skyygear_sig` on SignatureEnergy max while that item is held
  (the `skyygear_hp` max-Health modifier pattern). Their inherited signature then charges and fires as vanilla.
- UNVERIFIED: the engine's Recalculate keeps a foreign named modifier on SignatureEnergy (it does for Health); these items have no
  `EntityStatsToClear`, so the meter can carry across a swap (GearSigSlotSys already subtracts a carried value).

### 3.5 New-signature ideas per class (for UT / Mythic and the missing families)

| Class | Family | Family signature (base) | NEW ideas for UT / Mythic |
|---|---|---|---|
| Warrior | sword / spear | Vortexstrike / **spear: "Skewer Charge"** (dash 6 blocks, the first enemy is carried and pinned, 2 hits) | "Guardian Spin" (Vortexstrike that pulls mob aggro to you - tank); "Javelin Volley" (spear: throw 3 spears in a fan); "Guarded Thrust" (the stab + 2 s 20 % less damage taken) |
| Berserker | battleaxe / mace / axe / club | Whirlwind / Groundslam / **axe: "Cleave"** (a 180-degree heavy chop, 3 hits) / **club: "Skull Crack"** (one heavy blow, 1 s stun) | "Tremor Slam" (Groundslam twice, the 2nd ring 1 s later and wider); "Execution Chop" (Cleave +100 % on enemies under 30 % Health); "Iron Whirl" (Whirlwind that stops arrows while spinning). Not "life steal spin" (= class A2 Whirlwind) or a fissure line (= A2-alt Earthsplitter) |
| Assassin | daggers / kunai | Razorstrike / Kunai Fan (LOCKED) | "Shadow Razor" (Razorstrike always crits); "Venom Fan" (Kunai Fan applies Poison); "Tethered Kunai" (one kunai roots the target 1.5 s) |
| Archer | shortbow / crossbow | Volley / Big Arrow | "Seeker Volley" (homing triple - the Aegos idea, gear.md); "Piercing Bolt" (Big Arrow through every enemy in line); "Split Bolt" (Big Arrow bursts into 5 bolts on hit). Not an arrow rain (= A1-alt Arrow Rain) |
| Mage | staff / spellbook | **staff: "Arcane Overload"** (your next 3 quick shots cost no Mana and hit 2x) / Page Storm (LOCKED) | "Chain Spark" (Thunder bolt that jumps 5 enemies); "Ember Rain" (fire patch 4 s); "Frost Lance" (piercing ice line, slows) |
| Priest | wand / soul cage | Ricochet / **soul cage: "Soul Release"** (pop every Binding: each enemy takes its stored damage once, allies near it heal 25 % of that) | "Second Opinion" / "Warm Spring" (3.2); "Sanctified Bolt" (Ricochet that cleanses allies it passes) |
| Monk | Bo / fists | Whirling Staff / Flurry (LOCKED) | "Revolving Door" / "Tail Sweep" (3.2); "Iron Flurry" (Flurry whose last jab rings the ground, 3-block knockback) |
| Spellblade | longsword / great shield | the class file's own picks (`research/classes/Spellblade.md` "Signature ideas"): **longsword "Meridian Cut"**, **great shield "Iron Curtain"** | that file's other options as UT / Mythic NEW ones: "Crescent Wave" (longsword), "Rebound" / "Rally Point" (great shield); "Full Momentum" fits a Mythic Elemental-style sword we own later |

## 4. Engine feasibility - what is proven

| Need | Status | Evidence |
|---|---|---|
| Give OUR item id a meter + an Ability 1 root at build time | **PROVEN, deployed** | SkyyArmory 0.1.14 wands (build_skyyarmory_0.1.43.py 4758-4852), SkyySkills 0.4.24 Wood wands (vanilla-file override, one writer) |
| A NEW signature effect | **PROVEN pattern** | wand: root StatsCondition 100 % -> ChangeStat -100 % -> launches the invisible marker `SkyyArmory_Wand_Ricochet` (code 13000); server code does the effect (Rico, 15067+) |
| Add charge server side | **PROVEN, deployed** | wand +1 / +2 per shot hit (`sig.wand.chargeQuick / chargeCharged`) |
| Scale the vanilla per-hit gain at runtime | **PROVEN for melee tier hits** | SkyyGear 0.2.6 x w on EntityStatsOnHit (10609); projectiles UNVERIFIED -> top-up fallback |
| Keep the meter on a swap | **PROVEN, deployed** | SkyyGear 0.2.10 |
| Change the meter size per stack / live | **not possible** (asset data, client-predicted) | -> gain multiplier instead (3.3) |
| Re-root a PACK item (add Ability 1 to Ghost Sword, Elemental swords, Hepta ...) | **UNVERIFIED, not allowed by default** | no file may be shipped (PACK.md); a runtime edit of the loaded Item's interactions + a fresh item packet (GearBox does this for damage breakdowns only) is untested and touches their data -> Q4 |
| Give a pack item a meter at runtime | **UNVERIFIED** (likely) | named stat modifier, `skyygear_hp` pattern (3.4) |
| Catch the Ability 1 key on an item without a root | **UNVERIFIED (assume no)** | no chain starts -> nothing for an InteractionChainStartEvent hook (SkyyClasses AbilRuneSys works on started chains) |

## 5. Builds, harness, in-game test

### 5.1 Split (SkyyGear 0.3.42 = harvester swing speed, already queued - these come after it)

| Round | Mods / versions | Size | What |
|---|---|---|---|
| `sig1` | SkyyGear **0.3.43** + SkyyArmory **0.1.44** | full round (several mods, every tooltip) - no saved data, no migration | the table + Ability 1 block (2), cheaper rows + multiplier (3.3), `sig.packMeter` (3.4), `armory:fn:sig` + `gear:fn:sigMult` bridges, the wand's gains through the multiplier; families without a signature show `Ability 1 - none` |
| `sig2` | SkyyArmory **0.1.45** | full round (engine) | the 4 LOCKED family signatures: Whirling Staff (Bo), Flurry (wraps / gauntlets, +25 % slower / heavier), Kunai Fan, Page Storm - the wand pattern (root -> marker -> server effect), meter 20, server gains, rows `sig.bo.* / sig.fist.* / sig.kunai.* / sig.book.*`; texts reach SkyyGear through `armory:fn:sig` (no Gear change) |
| `sig3` | SkyyArmory **0.1.46** | full round | UT NEW signatures Second Opinion, Loophole Lance, Revolving Door (3.2) - per item id roots; SkyyGear shows them via the bridge |
| `sig4` | SkyyArmory (+ SkyyGear table for vanilla ids) | after Skyy answers Q2 | base signatures for staff, soul cage, great shield, axe, club, longsword, spear; then each UT-28 / own Mythic round adds its own |

Vanilla axes / clubs / longswords / spears are vanilla files: a new root on them = a vanilla-file override (one writer - SkyySkills /
SkyyArmory already own some weapon files; check `tools/ci/crosscheck.py` for an existing writer first). Our zone-metal copies are ours.

### 5.2 Harness checks (`test_skyygear_0.3.43.py`, `test_skyyarmory_0.1.44.py`)

1. Every weapon id in the gear pool maps to a table row or an explicit "none"; no id without a row.
2. Table numbers equal Assets.zip / the pack jars at build time and section 1.1 (sword 20 +1 / +3, battleaxe 9 +1 / +2, mace 8 +1 / +2,
   daggers 27 +1 / +2 / +6, shortbow 6 full draw, crossbow 5 combo, wand 20 +1 / +2, Crystal Flame 10, dev bows 10 at 0.54-3); a changed
   vanilla number stops the build.
3. Dead-meter list == {Zweihander, LahatChereb, DualRuneBlade, Weapon_Dualswords_Iron}; root-less pack list asserted (a pack update that
   adds an Ability 1 shows up).
4. Multiplier math: 0 -> x1, 40 -> x1.667, 60 -> x2.5, 90 cap; per-item row beats rarity; never above max; mob holder unchanged.
5. Tooltip: the block's colours are the kit tokens (#d6e4ee, #e8c25a, #7ee08a, #7f93a6, gold heading); one text line <= 70 chars; the
   "Fills N% faster" line only for UT / Mythic with p > 0; `sig.tooltip` off = no block.
6. `python tools/ci/langdup.py` 0 FAIL (no new keys); `python tools/ci/lint.py` 0 fails; `python tools/ci/crosscheck.py --jar <new jars> --baseline` READY.
7. Mutants: multiplier skipped / applied twice / bridge returns null (-> "none" line, no crash).
8. `python tools/smoke_test.py --jar SkyyGear/SkyyGear-0.3.43.jar --jar SkyyArmory/SkyyArmory-0.1.44.jar`: both `ready` lines, no SEVERE.

### 5.3 In-game test (sig1)

1. Hover an Iron sword: `Ability 1 - Vortexstrike`, `Charge: 20 energy - swing +1, thrust +3`.
2. Hover a wand, a crossbow, a shortbow, a Bo: Ricochet / Big Arrow / Volley texts; the Bo says `Ability 1 - none`.
3. The Paperweight: the green `Fills 40% faster (Untiered)` line; count swings to the glow vs a normal Iron sword (about 12 vs 20).
4. Server Setup > Gear > Rarity: set `sig.cheaper.ut` to 0 - the line goes, the charge is normal again.
5. A Vampire bow (Mythic): `Fills 60% faster`; it charges in fewer arrows.
6. Zweihander: it now fills and Groundslam fires on Ability 1 (was dead); switch `sig.packMeter` off - back to dead.
7. Swap weapons mid-charge: the kept charge still comes back (0.2.10).
8. Check the server + client logs for our WARN / SEVERE.

## 6. Where things go

- This spec: `research/Weapon-Signatures-Spec.md`. Class summaries: the "Weapon signature (Ability 1)" section at the end of each
  `research/classes/<Class>.md` (then `python tools/class_pages.py`). Older family proposals: `research/cloud/Signature-Proposals.md`.

## 7. Questions for Skyy (defaults in brackets)

1. Rule: Mythic = a NEW signature, UT = mostly the same signature charging faster (a few UTs get a new one)? [yes]
2. Base signatures for the families that have none - staff "Arcane Overload", soul cage "Soul Release", spear "Skewer Charge", axe
   "Cleave", club "Skull Crack", and the Spellblade file's longsword "Meridian Cut" / great shield "Iron Curtain"? [yes to all; build after
   the 4 locked ones]
3. Cheaper by default: UT fills 40 % faster, Mythic 60 % faster (both Server Setup rows)? [40 / 60]
4. Pack weapons with NO Ability 1 (Ghost Sword, Hepta Axe, the 4 Elemental swords, flails, Rune Blade): leave them without one, or try a
   runtime change that gives them a signature (touches The Armory's item data in memory - ask LadyPaladra first)? [leave them; show "none"]
5. Pack Mythics with a dead meter (Zweihander, Lahat Chereb, Dual Rune Blade): give them a meter at runtime so their signature works? [yes]
6. Weapons with no signature: show a grey "Ability 1 - none" line? [yes]
7. The UT NEW ones: Second Opinion heals allies it bounces through, Loophole Lance, Revolving Door (Turnstile)? [yes]
8. The battleaxe's vanilla signature is called Whirlwind - the same name as the Berserker's class A2 (both spin + hit around you). Keep
   both, the tooltip says "Ability 1 - Whirlwind (battleaxe)"? [yes - the class one is longer and heals]

## 8. For the local session (UNVERIFIED)

- The x w gain step covering projectile hits (bows, crossbows, wand shots): else the addStatValue top-up path (3.3).
- A named `skyygear_sig` modifier on SignatureEnergy max surviving the engine's Recalculate and the item swap clear (3.4).
- The Big Arrow / Volley "armed" state (`SignatureCharges`) with the faster meter - no double arming.
- PACK.md lists The Armory 1.23.0; Skyy's Mods folder has **TheArmoryMod-1.24.2.jar** - re-check the pack rows (this inventory used 1.24.2).
- More Perfect mods in the Mods folder (Perfect Dodges 0.5.18, Perfect Utils 1.3.1, Parries 0.9.8 vs PACK 0.9.6) - not checked here.
- 0.7 has an engine rune "CoreItemAbility" system (Ability 2 / 3, SkyyClasses uses it); confirm it never claims Ability 1.
- The vanilla Blowgun_Tribal carries the sword's Vortexstrike - harmless on mobs (they never press Ability 1), check if a player can hold one.
- Whether Skyy tested TEST-CHECKLIST 58-60 (meter kept on swap, wand Ricochet, Wood wands) - the base of sig1.
