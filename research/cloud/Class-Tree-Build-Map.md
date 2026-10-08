# Class tree build map - path trees into the live SkyyTrees class tree

Written 2026-10-07 (overnight, for "try to get the new updated class skill trees out tonight if you can" - Skyy). Plan only: nothing built.
Design = `research/cloud/Class-Tree-Paths.md` (updated 2026-10-07). Base = SkyyTrees **0.3.2** (the SET pin, class trees ON since 0.3.2),
`research/Skill-Trees-2-Spec.md` sections 5-10 and the notes at the top of `SkyyTrees/build_skyytrees_0.3.2.py` (cited as T:<line>).
Tags: **VERIFIED** = read in a pinned build script; **UNVERIFIED** = needs the game or a probe.

## 0. In one screen

| Question | Recommendation (default) |
|---|---|
| Where do the paths go? | **Replace page 2's three stat lanes** (L / C / R, their element and capstone cells) with **trunk + 3 locked paths**. Page 1 (stat spine ROOT > P1 > P2 > X1/X2 > P3 + the 4 ability rune slots and their modifier slots = the "ability tree" side) stays exactly as live. |
| New version | **SkyyTrees 0.3.3** (patch `tools/trees_0_3_3_patch.py` from the generated 0.3.2), full round / ultracode (saved data + a migration + 7 classes). Ship AFTER the running classes014 round (SkyyClasses 0.1.14 + SkyySkills 0.4.21: Monk "Discipline" + Assassin "Assassination" playable), because the tree needs `skill:fn:level` for those two skills. |
| Path lock | A **new "one path per tree" rule on the existing lane field**: the first OWNED path node picks the path; nodes of the other two paths answer "Path locked". Waiting (skipped) nodes never pick a path. No new saved field. |
| Respec | Keep the **live whole-tree respec** (Respec twice in 10 s, class skill level x `class.respec.perLevel` 100 coins, `respec.cooldownMinutes`) + Undo while the page is open. A cheaper path-only respec is a later option. |
| Waiting nodes | The **live reader-gating + skip mechanism** (0.3 READERS / `tree:reads:<Mod>`, 0.3.1 skip rule). Ability nodes wait for reader **SkyyClasses** with the text "Comes with the class abilities"; traversal nodes wait for **SkyyArmory**; stat nodes nobody applies yet wait for **SkyyGear** / "a later build". |
| Players who already spent AP | Their old lane nodes are retired: the AP comes back by itself (AP is computed), a one-time chat notice + one **free respec** per profile, and a copy of the retired ids is kept in the player file. |
| Live tonight (SkyyTrees alone) | 11 trunk nodes across the 7 classes (Health / Mana / Mana Regen / move speed / fall damage). With a small SkyyArmory reader (0.1.9, after the running Shadow Step build) **+13 more**, incl. most of the Mage **Riftwalker** and Assassin **Blink** paths. Everything else is greyed "Coming". |

## 1. What is live today (VERIFIED, T: = build_skyytrees_0.3.2.py)

- One class map for every class (`CT`, T:1672-1700): **37 nodes on 2 pages of 9 x 6**; ids `ROOT P1 P2 X1 X2 P3` + rune slots `A1-A4`,
  `M1A-M4B` on page 1; `P4` and the lanes `L1-L4 C1-C4 R1-R4`, elements `LE CE RE`, capstones `LS CS RS` on page 2. Parents: up to 2
  (`NPAR1 / NPAR2`, T:2151-2152); Lock: ONE id (`NLOCK`, T:2154 - the X1 / X2 pair); lane + lane count fields.
- **Ability Points** = (L >= 1 ? min(`class.ap.max` 50, `class.ap.first` 1 + L / `class.ap.every` 2) : 0) + `class.debug.extraAp`, L =
  `skill:fn:level(uuid, <class skill>)`; never stored; spent = owned **intact** nodes (T:~300).
- **Unlock rule**: root or an owned (or skipped) parent, Needs owned, no Lock owned, lane count, `class.minLevel`, enough AP, not coming.
- **Waiting nodes** (0.3 + 0.3.1, T:149-170, T:30-50): a node whose `READERS` mod has not listed its key in `tree:reads:<Mod>` (a
  String comma list, read LIVE on every page build / click) shows "Coming" (card) / "Coming with <mod>" (detail), the Coming soon button,
  cannot be bought, costs nothing, gives nothing; nodes of a **skip kind** (today: Strength, crossbow, Mana Regen) are passed through so the
  nodes after them can be bought; when the reader appears they become buyable for their own AP, nothing is refunded or re-counted.
- **Effects SkyyTrees applies itself**: `skyytree_health`, `skyytree_mana`, `skyytree_stamina` stat modifiers (flat, T:2574-2585 in
  0.2.5 numbering); Mana Regen through SkyySkills' registry `skill:fn:manaregen {"add", uuid, "trees", pct}` (live); movement through the
  shared movement protocol (`tools/skyymove.py`: source entries `speed` / `jump` / `fallDamage`, posted every 1 s, SkyySkills +
  SkyyAccessories apply them; today's source "trees.acrobatics"). Strength (`gear:extras`) still waits for SkyyGear (0.2.9 has no reader).
- **Bridge**: `tree:fn:level` / `tree:fn:bonus` answer "Class.<Class>.<Id>" (1 / 0 and the node's Amount) (T:4806, 4820).
- **Saved data** (players/<pkey>.properties, v=2): `Class.<Class>=<owned ids comma list>`, `Class.<Class>.respecAt=<ms>`. On load
  **unknown ids are ignored** ("a removed node refunds itself", T:2933) and the file is written back without them; a Class.* line with a
  field other than "" / respecAt, or of an unknown class, is **kept as it is** (`cextra`, T:2945).
- **Server Setup** (category Class trees, 41 rows): class.enabled (ON since 0.3.2), class.ap.*, class.respec.perLevel, class.undo,
  class.debug.extraAp, the `class.minLevel` table (<Class>.<Id> -> level; live lines Archer.R2=15, R3=15, R4=50), five
  `class.nodes.<Class>` tables (<Id> -> On | Amount | AP).
- **Classes**: `CLASSES = Archer, Warrior, Mage, Berserker, Priest` (T:1663); Assassin / Monk show "no skill tree yet".
- No mod reads a class node yet: SkyyArmory 0.1.7, SkyyClasses 0.1.13, SkyyGear 0.2.9 list no `tree:reads`; SkyySkills 0.4.20 only
  owns the Mana Regen registry (grep, VERIFIED).

## 2. The new page 2 (recommended layout)

Page 1 unchanged. Page 2 (rows r7-r12, columns c1-c9; `+` = junction / corner cell, `|` = bar cell, `.` = empty):

```
      c1    c2    c3    c4    c5    c6    c7    c8    c9
 r7   T1    +     TS*   .     .     .     .     .     P4
 r8   T2    +     PA1   PA2   PA3   PA4   PA5   LE    .
 r9   T3    |     .     .     .     .     .     .     .
 r10  T4    +     PB1   PB2   PB3   PB4   PB5   CE    .
 r11  T5    |     .     .     .     .     .     .     .
 r12  T6    +     PC1   PC2   PC3   PC4   PC5   RE    .
```

- **Trunk** T1 > T2 > ... > T6 down column c1 (a chain; each needs the one above). **T1's parent = ROOT** (page 1), drawn like the live
  P3 > P4 page-break link (no bar; detail "continues on page 1"). Not P4: requiring the whole spine first would make the Lv 5-25 gates
  unreachable (the spine costs 6 AP; AP at Lv 20 = 11).
- **Paths** hang off **T1** through the c2 bar column: corner r7 c2 (left to T1, down), junctions r8 / r10 (up, down, right), corner r12
  (up, right). PA = path A, PB = path B, PC = path C, in the order of Class-Tree-Paths.md. Each path is a chain N1 > N5. The level gates
  (Lv 20 / 30 / 45 / 65 / 75) come from `class.minLevel`, so the parent can be T1.
- **Elements** keep their ids **LE / CE / RE** (= path A / B / C), now after N5 (lane count 5, 3 AP), still "Coming later (needs SkyyGear
  elements)" - never buyable this round. **Capstones LS / CS / RS are retired** (a path's 5th node is its capstone; they were never
  buyable, nobody owns them).
- **P4** stays (a leaf now, still the spine's last stat node, "continues on page 1"); moved to r7 c9 (positions are map data, saved files
  hold ids only).
- **TS** (Priest only, the Guardian Spirit switch): child of T1 through the r7 corner. Other classes: the cell is empty (new per-class
  "hidden" flag; a hidden node is never shown, bought or counted).
- **Totals**: 44 nodes (page 1: 18, page 2: 26). Max ownable AP = page 1 21 (the pair once) + P4 1 + trunk 11 + one path 14 + its element 3
  = **50 = class.ap.max**. Without runes / elements (until 0.7 + SkyyGear elements): spine 6 + trunk 11 + path 14 = 31.
- **New ids**: `T1-T6`, `TS`, `PA1-PA5`, `PB1-PB5`, `PC1-PC5` (all match `[A-Z][A-Z0-9]*`, none collides with a live or retired id).
  Retired: `L1-L4 C1-C4 R1-R4 LS CS RS` (15). The build asserts change: NN 37 -> 44, CT_LINKS, the AP sums, the bar count (reserve new
  `#SkyyTrSeg` ids), the probe's PROBE_OWN (use ROOT P1 P2 X1 P3 P4 T1 T2 PA1).
- Path node ids per class (doc letters -> tree ids): Warrior G / W / J, Archer A / S / B, Mage R / L / C, Priest LB / A / S, Berserker
  W / B / M, Monk D / F / E, Assassin H / V / K -> PA / PB / PC 1-5.

## 3. Rules to add (TreeClass)

1. **One path per tree** (the lock). A node with lane 1-3 (PA*, PB*, PC*, LE / CE / RE) cannot be unlocked while any OWNED intact node has
   a different lane: card "Path locked", detail "You follow <path name> - respec to change paths". Integrity: a file that owns nodes of two
   paths (hand edit, admin) keeps the path with the most owned AP (tie: the lower lane) intact; the other path's nodes break (refund) like any
   broken chain. The X1 / X2 pair keeps its single `NLOCK`. Detail text on every N1: "Picking a path locks the other two".
2. **Skip kinds += ability / traversal / later** so a waiting trunk or path node is passed through (0.3.1 rule): e.g. a Mage can buy
   Riftwalker R1 (live) while T4 (Barrier Lore) waits. Waiting nodes never count as "owning a path".
3. **Lane count** for the elements = 5 (owned + passed path nodes).
4. **Switch node** (TS): 0 AP, Lv 1, bought once, then a player toggle like the template trees' per-node off switch (saved as
   `Class.Priest.off=TS`; 0.3.2 keeps that line as `cextra`, so a rollback keeps it). `tree:fn:bonus("Class.Priest.TS")` = 1 when owned
   AND on, else 0 (0 = party members only, the LOCKED default).
5. **Level ranks**: some Amounts grow with the class skill (Archer T3 bolts +1 / +2 / +3 / +4 at Archery 15 / 30 / 42 / 55; Mage T3 blink
   +2 at 15, +1 more at 30 / 42 / 55). `tree:fn:bonus` answers the ranked Amount, so readers stay simple. A new `class.ranks.<Class>.<Id>`
   row is optional; default = the table above baked in.
6. **New classes**: `CLASSES += Assassin, Monk` (skills Assassination, Discipline; physical spine; icons from SkyyClasses 0.1.14:
   daggers / `Weapon_Staff_Bo_Wood`; colours #b58cff / #f08a30); `classIdx("Shaman")` = Monk (SkyyClasses 0.1.14 alias); tabs ASSASSIN /
   MONK (static buttons like the other five; "ASSASSIN" is shorter than "BERSERKER").
7. Unchanged: AP formula, Undo, the reader contract, class.enabled, the probe, commands, permissions.

## 4. Status legend

| Code | Meaning | Shows as |
|---|---|---|
| **NOW** | SkyyTrees 0.3.3 applies it itself through a proven path (stat modifier, Mana Regen registry, movement protocol source **"trees.class"**, layer flat) | buyable |
| **NOW\*** | NOW, plus a small new check in SkyyTrees' 1 s effect tick (held item / crouch) - UNVERIFIED feel (up to 1 s lag) | buyable |
| **ARM** | the system is live in SkyyArmory 0.1.7; SkyyArmory must read `tree:fn:bonus` per player and list the key in `tree:reads:SkyyArmory` (reader patch **0.1.9**, after the running 0.1.8 Shadow Step round) | "Coming with SkyyArmory" until then, then buyable |
| **ARM\*** | ARM, but the reader also needs a small new behaviour (UNVERIFIED engine part named) | same |
| **XBOW** | SkyySkills crossbow reader (the live 0.3 "crossbow" waiting kind; engine check: can a player's magazine pass 6) | "Coming with SkyySkills" |
| **WAIT-AB** | needs a class ability - none is built | greyed, "Comes with the class abilities" (reader SkyyClasses) |
| **WAIT-MOVE** | needs a weapon move not built yet (Pole-Vault, Rising Strike, skipping bounds, Plunge Punch, Lunge / Whirlwind Dash / Bull Rush / Earthshaker, a custom sword or bow move, the Soul Orb) | "Coming with SkyyArmory" (the key is listed only when the move exists) |
| **WAIT-GEAR** | a SkyyGear stat or damage hook (crit, damage while holding / below X Health, backstab, armour type, damage taken) | "Coming with SkyyGear" |
| **WAIT-HOOK** | a small hook nobody has yet (Stamina regen registry, arrow recovery, blocked-hit, low-Health heal, kill Mana) | "Coming later" |

Percent stats become flat amounts on the proven modifiers (placeholder: 1% of a 100 base = 1 point; a MULTIPLICATIVE modifier is
UNVERIFIED). Nodes whose trade-off is a stat SkyyTrees can apply (e.g. Mage R5 max Mana -10) get that half from SkyyTrees and the
behaviour half from the reader; the node is gated on the reader.

## 5. Every node

### Warrior (Swordsmanship)
| Id | Node | Status | Hook / key |
|---|---|---|---|
| T1 | Shield Training | WAIT-AB | Shield Shockwave; the block-Stamina half is the vanilla guard asset (same for everyone) - WAIT-HOOK |
| T2 | Fortitude | **NOW** | `skyytree_health` +8 |
| T3 | Longer Thrust | WAIT-MOVE | the sword Thrust is a vanilla asset interaction (global, client-predicted); needs the later custom sword traversal |
| T4 | Second Wind | WAIT-HOOK | low-Health trigger + heal (SkyyTrees has no combat code) |
| T5 | Tempered Steel | WAIT-GEAR | percent damage is scrapped in the Stat Catalog -> Strength while holding a sword / spear via `gear:extras` |
| T6 | Veteran | WAIT-AB | ability cooldowns |
| PA1-PA5 | Guardian G1-G5 | WAIT-AB | Rallying Guard, Bulwark Stance, Guardian's Oath (damage share) |
| PB1-PB5 | Warlord W1-W5 | WAIT-AB | Rallying Guard, Iron Chain, Shield Shockwave |
| PC1 | Stalwart | WAIT-HOOK | a "blocked hit" event (UNVERIFIED) |
| PC2 | Last Stand | WAIT-AB | Unbreakable |
| PC3 | Plate Mastery | WAIT-GEAR | armour type Heavy + Defence |
| PC4 | Shockwave Surge | WAIT-AB | Shield Shockwave |
| PC5 | Juggernaut | WAIT-GEAR | damage-taken filter |

### Archer (Archery)
| Id | Node | Status | Hook / key |
|---|---|---|---|
| T1 | Steady Hands | WAIT-MOVE | bow draw timing is the vanilla asset (client-predicted) |
| T2 | Quiver Craft | WAIT-HOOK | arrow recovery on fire / hit |
| T3 | Extra Bolts | XBOW | `Class.Archer.T3`, ranked +1..+4 (Archery 15 / 30 / 42 / 55); replaces Bolt Rack I + II |
| T4 | Light Step | **NOW\*** | "trees.class" speed +0.04 while the held item is `Weapon_Shortbow_*` / `Weapon_Crossbow_*` |
| T5 | Eagle Eye | WAIT-GEAR | crit |
| T6 | Holster Reload | XBOW | `Class.Archer.T6` Amount 30 s, Archery 75; replaces R4 |
| PA1-PA5 | Trapper A1-A5 | WAIT-AB | Pinning Shot, Hunter's Net, Arrow Rain |
| PB1-PB4 | Sharpshooter S1-S4 | WAIT-AB | Pinning Shot / Mark, Rapid Fire |
| PB5 | Executioner | WAIT-GEAR | damage vs low-Health targets |
| PC1-PC5 | Stormbow B1-B5 | WAIT-AB | Rapid Fire, Explosive Arrow (the ability, not the bow leap blast) |

### Mage (Sorcery)
| Id | Node | Status | Hook / key |
|---|---|---|---|
| T1 | Mana Flow | **NOW** | `skill:fn:manaregen` "trees" +10% (the "out of combat" part dropped tonight; the text says so) |
| T2 | Spell Focus | ARM | x1.05 on the staff charged (blink trail, `blink.trailPercent`) and the spellbook Page Burst damage |
| T3 | Long Blink | ARM | `blink.distance` +2 (ranked to +6), `blink.trailSeconds` +1; no void check |
| T4 | Barrier Lore | WAIT-AB | Mana Barrier |
| T5 | Arcane Reserve | **NOW** | `skyytree_mana` +10 |
| T6 | Quick Hands | WAIT-AB | cooldowns |
| PA1 | Blink Slash | ARM | trail damage x1.5, blink Mana cost x1.2 |
| PA2 | Rift Echo | ARM\* | a second blink within 2 s free (no Mana, half Stamina), +3 s blink cooldown after (`blink.cooldown`); new code in the blink handler |
| PA3 | Phase Step | WAIT-AB | Mana Barrier |
| PA4 | Meteor from the Rift | WAIT-AB | Meteor |
| PA5 | Rift Master | ARM\* | blink through a 1-block wall (never lands in a block) + trail slow 25% (vanilla Slow effect id UNVERIFIED); max Mana -10 from SkyyTrees |
| PB1 | Radiant Trail | ARM\* | the trail tick also heals allies 5% max Health / s (reuse the wand heal-orb code); trail damage x0.75 |
| PB2-PB5 | Light Bender L2-L5 | WAIT-AB | Starfall, Arcane Beam, all spells |
| PC1-PC5 | Arcanist C1-C5 | WAIT-AB | all spells, Mana Barrier, Arcane Beam, Meteor (C2 Siphon's kill-Mana is WAIT-HOOK either way) |

### Priest (Divinity)
| Id | Node | Status | Hook / key |
|---|---|---|---|
| T1 | Gentle Hands | ARM | `orb.healPercent` x1.1 (the wand heal orb) |
| T2 | Faith | **NOW** | `skyytree_mana` +5 |
| T3 | Wide Prayer | WAIT-AB | Sacred Heal |
| T4 | Warm Light | WAIT-AB | Sacred Heal |
| T5 | Sustained | **NOW** | Mana Regen +10% ("while not casting 4 s" dropped tonight; a later SkyyArmory last-cast time can add it) |
| T6 | Patient Spirit | WAIT-AB | cooldowns |
| TS | Open Aura (switch) | WAIT-AB | Guardian Spirit reads `Class.Priest.TS` (1 = every player, 0 = party only) |
| PA1-PA5 | Lightbringer LB1-LB5 | WAIT-AB | Sacred Heal (Cleanse), Martyr's Grace, Sanctuary |
| PB1-PB5 | Aegis A1-A5 | WAIT-AB | Shield Bubble (Thorned / Elemental: 1 of 5 elements stored per profile), Guardian Spirit |
| PC1-PC5 | Soulweaver S1-S5 | WAIT-MOVE | the Soul Orb weapon + Bindings + Wings of Fate are not built |

### Berserker (Fury)
| Id | Node | Status | Hook / key |
|---|---|---|---|
| T1 | Thick Skin | **NOW** | `skyytree_health` +6 |
| T2 | Heavy Hands | WAIT-GEAR | charged-swing damage |
| T3 | Warpath | WAIT-MOVE | Lunge (battleaxe), Whirlwind Dash (axe), Bull Rush / Earthshaker (proposed) - none built; axes / maces are vanilla today |
| T4 | Rage Reserve | WAIT-AB | Enrage |
| T5 | Bloodied | WAIT-GEAR | damage below 50% Health |
| T6 | Unyielding | WAIT-AB | cooldowns |
| PA1-PA5 | Warbringer W1-W5 | WAIT-AB | Enrage, Warlord's Banner |
| PB1 | Hunger | WAIT-GEAR | heal from damage dealt |
| PB2-PB4 | Bleed / Crimson Frenzy / Blood Pact | WAIT-AB | Whirlwind, Blood Frenzy, Earthsplitter |
| PB5 | Bloodbound | WAIT-GEAR | lethal-hit filter |
| PC1 | Crushing Blows | WAIT-HOOK | telling a heavy charged hit apart server-side (UNVERIFIED) |
| PC2-PC4 | Seismic / Staggering Spin / Ground Pound | WAIT-AB | Earthsplitter, Whirlwind |
| PC5 | Smasher | WAIT-HOOK | heavy-hit counter + launch |

### Monk (Discipline)
| Id | Node | Status | Hook / key |
|---|---|---|---|
| T1 | Light Step | **NOW** | "trees.class" speed +0.03 |
| T2 | Soft Landing | **NOW** | "trees.class" fallDamage -0.10 (applied by the fall-damage owner, SkyySkills) |
| T3 | Vault Mastery | WAIT-MOVE | Pole-Vault + Rising Strike ("moves later", SkyyArmory 0.1.7 has items only) |
| T4 | Skipping Rhythm | WAIT-MOVE | skipping bounds |
| T5 | Calm Breath | WAIT-HOOK | no Stamina-regen registry (alternative: +max Stamina on `skyytree_stamina` = NOW, Skyy's call) |
| T6 | Master's Poise | WAIT-AB | cooldowns |
| PA1, PA2, PA5 | Airborne / Skip Chain / Wind Master | WAIT-MOVE | vault mid-air jump, bounds, vault chains |
| PA3, PA4 | Aerial Palm / Wind Step | WAIT-AB | Palm Strike, Flowing Form |
| PB1 | Hard Knuckles | ARM\* | +20% on the wraps' power hit / the gauntlets' finisher, -5% other jabs; the jab table is fixed in the asset, so the server damage filter (ArmoryTuneSys) must tell the power hit apart - UNVERIFIED; if it cannot, WAIT-MOVE |
| PB2 | Plunge Power | WAIT-MOVE | Plunge Punch |
| PB3-PB5 | Concussive Palm / Iron Skin / Iron Fist | WAIT-AB | Palm Strike, Flowing Form stacks |
| PC1-PC5 | Serene E1-E5 | WAIT-AB | Flowing Form, Still Water |

### Assassin (Assassination)
| Id | Node | Status | Hook / key |
|---|---|---|---|
| T1 | Quiet Feet | **NOW\*** | "trees.class" speed +0.10 only while crouching (MovementStates read in the 1 s tick) |
| T2 | Sharp Eye | WAIT-GEAR | crit |
| T3 | Long Reach | ARM | `kunai.range` / `kunai.throwRange` +3; the Shadow Step half (24 -> 27, 18 -> 20) is read once SkyyArmory has Shadow Step (0.1.8 running) - the reader lists the key once the kunai part works |
| T4 | Nimble | **NOW** | "trees.class" fallDamage -0.15 |
| T5 | Deadly Focus | WAIT-GEAR | backstab damage |
| T6 | Shadow's Patience | WAIT-AB | cooldowns |
| PA1-PA5 | Shadow H1-H5 | WAIT-AB | Cloak, First Strike, God Killer |
| PB1-PB5 | Venom V1-V5 | WAIT-AB | Toxin (V4's dagger poison stacks come with it) |
| PC1 | Long Throw | ARM | `kunai.range` 20 -> 26, kunai damage x0.9 |
| PC2 | Hard Return | ARM\* | `ret.force` x2, `ret.window` 8 -> 6 s, + a 0.4 s stun (a stun effect is new to SkyyArmory - UNVERIFIED) |
| PC3 | Double Step | ARM\* | a second kunai teleport within 3 s at half Stamina, no Mana; `kunai.cooldown` +3 s after |
| PC4 | Blink Strike | ARM\* | 1.0 H on arrival next to an enemy (kunai now; Shadow Step half when it exists) |
| PC5 | Shadow Blink | WAIT-AB | the cloak is the Cloak ability's invisibility |

**Count**: NOW 11 (Warrior T2; Archer T4; Mage T1 T5; Priest T2 T5; Berserker T1; Monk T1 T2; Assassin T1 T4) - SkyyTrees 0.3.3 alone.
ARM 13 (Mage T2 T3 PA1 PA2 PA5 PB1; Priest T1; Monk PB1; Assassin T3 PC1-PC4) + XBOW 2. Everything else waits. Elements LE / CE / RE:
"Coming later" for every class.

## 6. Reader keys (for the reader builds)

- **SkyyArmory 0.1.9** (`tree:reads:SkyyArmory`, set in setup() after its config load, removed in shutdown, bare mod name, String):
  `Class.Mage.T2,Class.Mage.T3,Class.Mage.PA1,Class.Mage.PA2,Class.Mage.PA5,Class.Mage.PB1,Class.Priest.T1,Class.Monk.PB1,Class.Assassin.T3,Class.Assassin.PC1,Class.Assassin.PC2,Class.Assassin.PC3,Class.Assassin.PC4`
  - list ONLY keys it fully applies (an ARM\* whose engine part fails stays off the list = stays waiting). Read per player through
  `tree:fn:bonus(Object[]{UUID, key})` at the moment of the move (blink start, kunai throw / return, trail tick, orb tick, fist hit), cached
  1 s. Global Server Setup rows stay the base; the node adds on top.
- **SkyySkills** (crossbow, existing contract): `Class.Archer.T3,Class.Archer.T6` (the old R2 / R3 / R4 keys are retired - no reader
  ever listed them).
- **Abilities** (later): the mod that builds the class abilities lists its keys under its own name; READERS for every WAIT-AB node =
  `SkyyClasses` by default (a data edit in a later SkyyTrees if the host differs). Text: card "Coming", detail "Comes with the class
  abilities".
- **SkyyGear**: the WAIT-GEAR keys + the existing `gear:extras` token.

## 7. Saved data, migration, rollback

- **Who is affected**: every profile whose `Class.<Class>=` line holds a retired lane id (`L1-L4 C1-C4 R1-R4`; bought since class trees
  went ON in 0.3.2). `LE CE RE LS CS RS` and the Archer crossbow R2-R4 were never buyable, so nobody owns them.
- **What happens by itself** (0.3.2 code, kept): unknown ids are ignored on load -> their AP is free again (AP is computed), their Health /
  Mana / Mana Regen stops on the next effect tick, the file is written back without them. No coin or item is involved.
- **Add (one-time, per class line, 0.3.3 `ClassMig33`)**: when a loaded line holds retired ids: (1) write `Class.<Class>.retired=<ids>`
  (0.3.2 keeps such a line as `cextra`; it also documents what was refunded); (2) set `Class.<Class>.freeRespec=1` - the next class respec
  is free and skips the cooldown, then the flag is removed; (3) one chat line at the next login: "Your <Class> tree has new paths: <n>
  Ability Points came back from the old lanes. Your next class respec is free."; (4) log one INFO line per player. The `retired` line is
  the run-once marker.
- **Undo** lists are page-local - nothing to migrate.
- **trees.properties** (one-time `TreeMig33`, marker `skyytrees-0.3.3-paths`, the 0.3 TreeMig machinery: History snapshot verified
  first, append-only, the file's own line endings, nothing rewritten): append `class.nodes.<Class>.<Id>=on,<amount>,<ap>` for the new
  ids of all 7 classes and `class.minLevel` defaults (trunk 5 / 10 / 15 / 25 / 40 / 55 - Archer T6 75; paths 20 / 30 / 45 / 65 / 75; TS 1;
  elements 75). The old `class.nodes.<Class>.L1...` lines and `class.minLevel` Archer.R2 / R3 / R4 stay byte for byte and are ignored
  (one INFO "retired line kept: ..."); a hand-edited retired value is reported, never carried to a different node. No `config-changes.log`
  Undo line is needed (no value changes). `TreeKit.checkClassNode` must accept 7 classes; Server Setup gets `class.nodes.Assassin` and
  `class.nodes.Monk` (41 -> 43 rows) and a re-keyed `class.minLevel` table.
- **Rollback 0.3.3 -> 0.3.2**: 0.3.2 ignores the new ids and drops them at the next save (path picks lost; AP computed, nothing else
  lost; respec coins already paid stay paid), keeps `retired` / `freeRespec` / `off` lines as cextra, and shows Assassin / Monk "no tree
  yet". The 0.3 floor stands; add a deploy_set.py comment: "do not roll SkyyTrees below 0.3.3 once paths are bought unless losing the
  picks is fine".
- **Harness** (extend `test_skyytrees_0.3.2.py` -> 0.3.3): the K model at 44 nodes / 7 classes / the path rule / switch / ranks;
  ClassMig33 on scratch COPIES of the live player files (lane owners get the notice + free respec once; a second load does nothing; a
  0.3.2 jar re-reads the result); TreeMig33 on a copy of the live trees.properties; reader gating with a stand-in `tree:reads:SkyyArmory`.

## 8. Open choices (recommended default in brackets)

1. Replace page 2's stat lanes, or add a page 3 and keep them? [replace - the lanes were pure buffs; Skyy's 2026-10-04 lock says the
   class tree changes how things work; one page of paths fits exactly]
2. Paths branch from T1 or from T3? [T1 - the level gates pace it; T3 would make the cheapest trunk nodes mandatory]
3. Path lock = first owned path node (waiting ones do not count)? [yes]
4. Path-only respec (trunk kept, cheaper)? [not tonight; whole-tree respec as live; add a "Change path" button later]
5. Lane owners: automatic refund + free respec + notice? [yes]
6. Percent stats as flat amounts (1 point per 1% of 100)? [yes until a MULTIPLICATIVE modifier is proven]
7. Conditions on stat nodes: held bow (Archer T4) and crouch (Assassin T1) built now; "out of combat" (Mage T1) and "not casting" (Priest
   T5) dropped tonight and named in the text? [yes]
8. Monk T5 Calm Breath: wait for a Stamina-regen hook, or swap to +max Stamina (live)? [wait - keep the design; Skyy can swap]
9. Mage "shorter custom blink distance": a /settings row in SkyyArmory, not a tree node? [yes]
10. Elements after N5 (3 AP, waiting) and capstones retired? [yes]
11. WAIT-AB reader name SkyyClasses with the "Comes with the class abilities" text? [yes]
12. Round shape: SkyyTrees 0.3.3 tonight (after classes014 pins), SkyyArmory 0.1.9 reader as the next round (nodes stay "Coming with
    SkyyArmory" until it ships)? [yes - SkyyTrees alone is safe to ship; the reader adds no saved data]
13. Respec price for Monk / Assassin = the same `class.respec.perLevel`? [yes]

## 9. Text changes for the next SkyyTrees build (added 2026-10-08, cloud)

From research/cloud/Class-Tree-Stale-Fix-1008.md (design in research/cloud/Class-Tree-Paths.md, rows marked "live 0.3.3 text differs").
Live texts = `CPATHS` in `SkyyTrees/build_skyytrees_0.3.3.py` (VERIFIED, read-only). **Ids, kind (K), AP, level gates and Amount 0 stay**:
only the name / effect text in `CPATHS` changes. All four are WAITING nodes (kind K, reader SkyyClasses, "Comes with the class
abilities"), so no player owns them - no migration, no refund, no `trees.properties` line (`class.nodes.<Class>.<Id>` rows hold On / Amount /
AP only). Do it in the next SkyyTrees patch (a lean change riding on whatever round touches SkyyTrees next); waits on Skyy's answers in
research/cloud/Class-Tree-Stale-Fix-1008.md (the defaults are safe to ship).

| Class | Id | Live 0.3.3 name / text | Next build name / text (default) | Why |
|---|---|---|---|---|
| Mage | PA3 | Phase Step - "Mana Barrier: blink 5 blocks back, the dome lands where you land - dome 10 s" | Phase Step - "Mana Barrier: blink 5 blocks back and the dome moves with you at full strength - dome 10 s, no Follow modifier on it" | docs/answered/classes.md L113: Follow is also a skill-tree upgrade |
| Priest | PA2 | Radiant Pulse - "Sacred Heal pulses again after 2 s at 50% - cooldown +3 s" | Guiding Light - "Sacred Heal can be aimed at an ally within 20 blocks: the circle forms on them - cast 0.5 s slower" | copied the Sacred Heal Echo modifier (L141) |
| Berserker | PA2 | Shared Fury - "Allies' kills extend Enrage 1 s each (max +5 s) - cooldown +3 s" | Shared Fury - "Enrage: the ally you look at gets your doubled buff and you get theirs - cooldown +3 s" | copied the Warlord's Banner kill extension (L133) |
| Monk | PC5 | Serenity - "Awed enemies attack 15% slower and hesitate 2 s - max combo 18" | no change (already right) | doc-only cleanup |

Checked, no build change: Berserker PA1 War Horn ("Enrage calls again after 3 s, allies start at +15% - your peak -5") and PB3 Crimson
Frenzy ("Each Blood Frenzy stack heals you 0.5% and allies 0.25% - +20% cost") already match the 2026-10-07 design. Ability side (later,
whoever builds Mana Barrier): owning `Class.Mage.PA3` makes the dome follow at 100% and blocks the Follow modifier on that ability (an
exclusive rule like Floor + Duration+, research/cloud/Modifier-Pool-Spec.md section 3); `Class.Priest.PA2` adds a look-at target to Sacred
Heal; `Class.Berserker.PA2` swaps the self / ally Enrage values for one looked-at party member.
