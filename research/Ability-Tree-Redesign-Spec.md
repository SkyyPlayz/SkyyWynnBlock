# Ability tree redesign (Wynncraft style + Lattice slots) - spec

Written 2026-10-15 by the main session from Skyy's fresh-Mage test. Paper design: nothing built. Mods: **SkyyTrees** (tree, AP, page) +
**SkyyClasses** (abilities, modifiers, slots, casting). Saved data + migration + several mods = **full round / ultracode** (PROJECT-RULES 4).
Numbers marked PLACEHOLDER are Server Setup rows (`tools/skyycfg.py`).

## 0. Plain words (for Skyy)

- Your abilities live **in the tree**. Unlocking an ability node unlocks the ability - no separate "Enable".
- Under each ability hang its **modifier nodes**. Each costs 1 Ability Point and unlocks that modifier for good (no second wait for
  the ability's level).
- Every tree (classes AND skills) **branches downward** from the top, and every node gets **our own icon**.
- The **Abilities** column only lists abilities you have. Click one: the others hide, you see that ability, its level, stats and its
  modifiers.
- The right side then turns into a **Lattice view** like the vanilla Runebinder's Lattice: one row per key, each row = an ability slot +
  modifier slots. Click an ability, click its slot. Click a modifier, click a modifier slot. No Swap / Move here / Cancel buttons.
- The Root node is free, so your first Ability Point buys your first ability.
- With every node bought, a class tree costs exactly the 50 AP you have at max level (section 4.3), so choices matter on the way up.

## 1. Decisions followed - `docs/answered/skills.md` (2026-10-15, word for word there)

| Line | Skyy's words (short) | Here |
|---|---|---|
| ABILITY TREE REDESIGN (WYNNCRAFT STYLE) | "id have the ability's actually be in the skill tree. and thats how you unlock them. then each ability branches into its modiferss, and each of those thakes an ability point to unlock. then your abilitys section only shows your unlocked abilitys their level and stats. you click one, and it hides all the others ... when you click an ability you have unlocked in the abilities section, it swaps the menu on the right to something like the vanilla one" + all four popup options (Swap mode, Enable vs Unlock, Root costs my AP, Too many buttons) felt weird | sections 3-6 |
| ABILITY TREE REDESIGN (2) | "so you click an ability, click the slot it goes in, then click a modifer and a slot" (Lattice screenshot) | section 6.3 |
| ABILITY TREE REDESIGN (3) | "modifiers unlocked in the tee, but not in the ability. and id try to make the tree look better. branch down nit side to side, and use our own icons for everything. across all trees." | 3.3, 5, 7 |
| TEST 10-15 | Meteor casts on the Q key ("ability worked!") | casting path stays (6.5) |
| A TREE FOR EVERY SKILL | "eventually i want a tree for every skill." | 5.3 (layout applies to all), TREE buttons fix is a separate small round |

Older locks kept: classes.md 2026-10-04 ability structure (Ability 1 first, then 2, then a swap-out alt, then a late pick); the
per-ability use levels (SkyyClasses 0.1.22: uses for level n = round(4.5 n^1.5), max 25) stay - they now scale POWER only; rebirth
modifier slots 3-4 (one per 5 rebirths) stay.

## 2. What exists today (SkyyClasses 0.1.25 + SkyyTrees 0.3.10, read-only survey)

- Class tree: 44 nodes per class, 2 pages. Page 1 = spine ROOT-P1-P2-P3 (+ X1/X2 pick-one) with ability lines A1-M1A-M1B ... A4-M4A-M4B
  hanging SIDEWAYS; page 2 = trunk T1-T6 (AP 1/1/2/2/2/3), three paths PA/PB/PC x5 (2/2/3/3/4), elements LE/CE/RE (3), Priest TS.
- A and M nodes cost 0 AP (forced), gated by class level (A1 1, A2 10, A3 20, A4 30). **M nodes only open modifier SLOTS**; the
  modifiers themselves unlock at ability level 2/4/6/8/10 (`mods.unlock`) - the "unlocked in the tree but not in the ability" Skyy hit.
- ROOT costs 1 AP. AP = min(50, 1 + level / 2), computed, never stored.
- Abilities column: 4 cards with Swap / Enable / Other alt / Modifiers; right panel = node detail or ability detail with
  Equip / Double / Unequip / Next slot / Max Up / Change element.
- Keys: Ability 2 = Primary 1, Ability 3 = Primary 2, crouch + key = the alt on that key; hidden rune items `SkyyAbility_<Class>_<Id>`
  mirrored into the vanilla AbilitySlots core slots 0 and 3; vanilla runes blocked for classed players; `/cast 1-4` backup.
- Saved: `Skyy_SkyyTrees/players/<pkey>.properties` (`Class.<Class>=<owned ids>`, `.order`, `.respecAt`, `.rb`),
  `Skyy_SkyyClasses/abilities/<pkey>.properties` (`p1,p2,a1,a2` slot ability ids, `alt`, `u.<Id>` uses, `m.<Id>.<Mod>` modifier
  uses, `e.<Id>` slots 1-2, `e2.<Id>` slots 3-4, `att1/att2`, rebirth keys).
- Bridges: `class:fn:abil` (Object[48], SkyyHud), `class:fn:abilPanel` (Object[94]), `class:fn:abilMods`, `class:fn:abilDo`,
  `class:fn:abilUnlock`, `class:fn:loadoutGet/Set`, `tree:fn:abil`, `tree:reads:SkyyClasses`, `rebirth:part:trees` / `:classes`.

Per class the five abilities (A1, A2, A3, A4 alt A / alt B) carry 4-5 modifiers each from Power, Radius, Duration, Efficiency, Pierce,
Chain, Slow, Knockback, Ricochet, Pull, Leech (stackable) and Split, Lingering, Follow, Ward, Echo, Haste, Floor, Seeker (not stackable).
Full table: SkyyClasses `ABILS` + `AB_MODS` (build script ~943-985, ~2026-2095).

## 3. Existing work we learn from (PROJECT-RULES 2)

| What | Licence | Use |
|---|---|---|
| **Wynncraft ability tree** (wiki.gg Ability_Tree) | game design | 1 AP per node for basics, 2 AP for big ones; take only nodes connected to ones you own; some nodes block others; reset = full or free edit in town. We take: connected-node rule, "blocks" for pick-one alts, 1-AP modifiers, a free-edit respec idea (Q4). |
| **Vanilla Runebinder's Lattice** (`Bench_Abilities`, `OpenAbilityBench`, `AbilityBenchWindow`, `InventoryComponent$AbilitySlots` = 6 slots: 2 lines x core + 2 mods, filters `AbilityCoreSlotFilter` / `AbilitySupportSlotFilter`) | vanilla | The window layout is a CLIENT file (`AbilityBenchPanel.ui`), fixed: 2 rows only, cannot be restyled or embedded. So our Lattice view is OUR inline page copying its look (frames, ItemGrid, rows) through `tools/skyyui.py`. The vanilla AbilitySlots mirror for the HUD stays. |
| **MMOSkillTree 1.7.1** (Ziggfreed, in Skyy's Mods folder) | closed (licence gate) | learn only: node cards with an ItemGrid icon + pip frame, a separate bind page, an admin overrides page. Not a point tree. |
| HyARPG, RPG Leveling | not checked / study | nothing does Wynncraft-style points + branching modifiers -> we build our own. |

## 4. The new tree model

### 4.1 Node kinds (per class)

| Kind | Example | Cost | Unlocks |
|---|---|---|---|
| ROOT | class root | **0, owned from class level 1** (Skyy found 1 AP odd) | nothing; it is the top of the tree |
| ABILITY | A1 Meteor | **1 AP** (PLACEHOLDER `class.ap.ability`) | the ability: castable, slottable, listed in Abilities |
| ABILITY ALT | A4 Starfall / A4 Arcane Beam | 1 AP each, **pick one: buying one blocks the other** (Wynncraft "blocks"); respec frees it | the alt |
| MODIFIER | A1 > Power | **1 AP** (`class.ap.modifier`) | that modifier for that ability, usable at once (no ability-level gate) |
| PATH / TRUNK / ELEMENT | T1-T6, PA-PC, LE/CE/RE | unchanged (1-4 AP) | unchanged stats / path effects |

Level gates stay on ABILITY nodes (A1 1, A2 10, A3 20, A4 30) and on trunk / path nodes as today. MODIFIER nodes need only their
ability node (+ AP). Connected-node rule: a node is buyable when its parent is owned (today's rule, kept).

### 4.2 What ability LEVEL still does

Uses still raise the ability's level (round(4.5 n^1.5), max 25) and the level still adds power (+% per level, today's numbers) and
raises modifier levels by use (10/30/60/100 uses -> modifier Lv 2-5, stackable modifiers may double-slot from Lv 2). It no longer
gates which modifiers exist. `mods.unlock` becomes unused (legacy row kept, CONFIG-CONTRACT).

### 4.3 AP budget (python-checked, Mage; the other classes are within +-1)

| Part | AP |
|---|---|
| 4 abilities (A1, A2, A3, one A4 alt) | 4 |
| Modifiers: Meteor 5 + Mana Barrier 5 + Frost Nova 4 + Starfall 4 (or Arcane Beam 4) | 18 |
| Trunk T1-T6 (1+1+2+2+2+3) | 11 |
| One path, 5 nodes (2+2+3+3+4) | 14 |
| Its element node | 3 |
| **Total** | **50** = the AP cap (1 + level/2 reaches 50 at class level 98) |

So a max-level player owns the whole build they chose; on the way up they choose between more modifiers and more path power.
X1/X2 and P1-P4 spine nodes: make them 0 AP connectors (today they hold nothing a player buys for an effect) - Q2.

## 5. Layout - every tree branches DOWN

### 5.1 Class tree, page 1 (abilities) - 9 columns x 6 rows, 92 px cells (today's grid size)

```
row 0               . . . . ROOT . . . .
row 1      A1 Meteor    A2 Barrier    A3 Frost Nova    A4a Starfall | A4b Arcane Beam   (A4 alts side by side, "pick one")
row 2      M Power      M Power       M Power          M Power        M Power
row 3      M Radius     M Duration    M Radius         M Radius       M Duration
row 4      M Split      M Ward        M Duration       M Duration     M Slow
row 5      M Lingering  M Follow      M Slow           M Echo         M Pierce
row 6      M Echo       M Knockback   -                -              -           (a 5th modifier spills to row 6 -> page grid 7 rows, see Q3)
```

Each ability is a column; its modifiers stack straight down under it, joined by a vertical line. Columns 0-1, 2-3, 4-5, 6, 7 (A4 alts
share the right block with a "pick one" bracket). Lines run down only.

### 5.2 Class tree, page 2 (power) - trunk + paths, downward

ROOT at the top, T1..T6 down the middle column, the three paths PA/PB/PC branching down from T1 into columns 1-2 / 4 / 6-7, each path
5 nodes down, its element node at the bottom. Same cells, same lines, no sideways runs except the one fork under T1.

### 5.3 Skill trees (Mining, Foraging, Farming, Cooking, Alchemy, Smithing, Acrobatics, Exploration, Fishing, later Ranching / Orchard / Sorcery)

Same rule: root at the top, branches fan DOWN. The current templates are re-laid (positions only - same node ids, costs, effects,
saved data), so this part has no migration. Done once in SkyyTrees' shared layout code so every tree follows it.

### 5.4 Icons

Every node shows OUR icon (no borrowed vanilla item icons): ability nodes = the ability's own icon (the 40 SkyyAbility rune icons
already exist), modifier nodes = one icon per modifier kind (19 kinds, shared by all classes), stat / path / trunk nodes = one per
effect family, skill-tree nodes = per tree. The art goes through the menu-icons work (`research/Menu-Icons-Plan.md`, skywynn-art skill,
cloud draws -> local review); the build uses placeholders until a sheet is approved, and swapping art in later is asset-only.

## 6. The page

### 6.1 Columns (window 1600 wide, as today)

Left: the tree grid + pager. Middle (262 px): **Abilities** - only OWNED abilities, one compact card each (icon, name, Lv N, uses to
next level, key it sits on). Right (440 px): the detail panel.

### 6.2 Clicking

| Click | Result |
|---|---|
| a tree node | right panel = node detail (what it unlocks, cost, Unlock / Undo) - as today |
| an owned ability card | the other cards hide; the middle shows that ability: level, stats, and its unlocked modifiers as small tiles (locked ones greyed, "buy in the tree"); the right panel switches to the **Lattice view** |
| "Back" (top of the middle column) or Esc-like close of the focus | all owned abilities show again |

### 6.3 Lattice view (right panel)

```
LOADOUT
  Ability 2 key        [ability slot] [mod 1] [mod 2] (+[mod 3] [mod 4] with rebirth slots)
  Ability 3 key        [ability slot] [mod 1] [mod 2]
  Crouch + Ability 2   [ability slot] [mod 1] [mod 2]
  Crouch + Ability 3   [ability slot] [mod 1] [mod 2]
```

- Click an ability (its card or its tile) -> it is "held" (highlighted) -> click an ability slot: it goes there. If that slot held
  another ability, the two trade places (that is the only swap there is, and it needs no button). Same ability can sit in only one row.
- Click a modifier tile -> click one of THAT ability's modifier slots in its row: equipped. A stackable modifier at Lv 2+ may take both
  slots (double effect), as today. Clicking a filled modifier slot with nothing held empties it.
- Out of combat only (today's rule); in combat the panel shows "Change your loadout out of combat".
- Rows: 4 (Q1 default). Today the alts are fixed to crouch rows; the redesign lets any owned ability sit in any of the 4 rows.
  The vanilla AbilitySlots mirror keeps showing rows 1 and 2 on the HUD (vanilla has only 2 lines).
- Imbue's element (Spellblade) shows as a small element picker under its row (today's Change element, moved).

### 6.4 Buttons left

Node detail: Unlock, Undo (newest unlock while the page is open). Footer: Respec, < Skills. Nothing else: Swap, Move here, Cancel,
Enable, Other alt, Modifiers, Next slot, Unequip and Tree node are gone. Max Up (rebirth) moves onto the ability focus view.

### 6.5 Casting

Unchanged: hidden `SkyyAbility_` runes, the AbilRuneSys hook, `/cast 1-4`, vanilla runes blocked for classed players. The 4 rows map
to the existing 4 slot ids (`p1, p2, a1, a2` = Ability 2, Ability 3, crouch+2, crouch+3), so the casting code only reads the slots.

## 7. Saved data and migration (one-time, PROJECT-RULES 4)

New keys (SkyyTrees players file): ability / modifier node ids `A1`, `A4a`, `A4b`, `A1.Power`, `A1.Echo` ... in `Class.<Class>=`.
SkyyClasses abilities file: `p1,p2,a1,a2` keep their meaning (row -> ability id), `e.<Id>` / `e2.<Id>` unchanged.

Migration per profile, run once (marker `abil.tree2=done`), History snapshot of both files first, change-log line with Undo:
1. Owned `ROOT` -> refund its 1 AP (it becomes free).
2. Owned `A1..A4` (+ `alt` A/B) -> the matching ABILITY nodes (`A4a` or `A4b` by `alt`), now 1 AP each.
3. Old `MnA` / `MnB` slot nodes -> removed (slots now come with the ability). Every modifier that was USABLE before (ability level
   reached its `mods.unlock` step) -> its MODIFIER node, owned. Equipped modifiers stay equipped.
4. AP check: nobody can lose a working ability or modifier. If the converted nodes cost more AP than the player has (possible:
   modifiers were free before), the overflow nodes are marked **grandfathered** (`Class.<Class>.gf=<ids>`): they work and show
   "kept from before", cost 0, and are refunded as normal nodes on the next respec (then cost AP). Q5.
5. Old `p1/p2/a1/a2` stay as they are (they already are the 4 rows).
6. A player who never chose a class: nothing to do.
Rebirth parts (`rebirth:part:trees` R5, `:classes` R6) learn the new ids; a rebirth resets ability + modifier nodes like other nodes.
ROLLBACK floor: once migrated, SkyyTrees / SkyyClasses never go below the redesign versions (old code would read `A1.Power` as unknown).

## 8. Bridges

- `class:fn:abil` (SkyyHud, Object[48]) unchanged.
- `class:fn:abilPanel` / `class:fn:abilDo`: new shapes for the focus + Lattice view (actions `hold`, `place`, `mod`, `clearMod`,
  `back`); old actions refused with a log line. Only SkyyTrees calls them.
- `tree:fn:abil` keeps answering owned ids; the new modifier ids are added. `class:fn:abilUnlock` keeps the ability level gates.
- New `tree:fn:modOwned` (UUID, abilityId, mod) -> Boolean, so SkyyClasses gates modifiers by the tree instead of `mods.unlock`.

## 9. Build plan

| Round | Size | Mods | What |
|---|---|---|---|
| R1 layout | full (touches every tree's look) | SkyyTrees | downward layout for every tree (positions only, no data change), placeholder icons hook (asset ids per node) |
| R2 model + migration | **ultracode** | SkyyTrees + SkyyClasses | node kinds 4.1, free ROOT, pick-one alts, modifier nodes, AP rows, migration 7, bridges 8, rebirth parts |
| R3 page | full | SkyyTrees (+ SkyyClasses panel bridge) | Abilities column (owned only), focus view, Lattice view 6.3, 4 rows, button cleanup 6.4 |
| R4 icons | asset round | SkyyTrees (+ SkyyClasses rune icons) | the approved icon sheets |

R1 can run first and alone. R2 and R3 share files -> one after the other (or R2+R3 as one ultracode round). Fuzz for R2: migrate
1000 random old profiles -> no ability / modifier that worked before stops working, AP never negative except grandfathered, equipped
modifiers kept, run twice = no change.

### Probes (UNVERIFIED, before R3)
- P1: a 7-row tree grid (for 5-modifier abilities) still fits 1080p with the pager.
- P2: the held-item highlight + click-to-place feels right with the client's click events on ItemGrid slots vs buttons (the Lattice
  look uses ItemGrid frames; our clicks need TextButtons over them - check hover / click on the overlay).
- P3: hiding cards in the middle column without a page rebuild flicker (or accept one rebuild per click, as today).

## 10. Questions for Skyy (defaults in brackets - they go live if unanswered)

1. Loadout rows: 4 rows (Ability 2, Ability 3, crouch + each), any owned ability in any row? [yes, 4 rows]
2. The spine connectors P1-P4 / X1-X2: free (0 AP) links? [yes, free]
3. Abilities with 5 modifiers: 7-row grid, or the 5th modifier one step to the side? [7 rows if probe P1 fits, else side-step]
4. Respec: keep the coin price (class level x 100) or Wynncraft style (free edits in a town / hub, a price only for a full reset)?
   [keep coins, plus free re-slotting of the loadout at any time out of combat]
5. Migration overflow (modifiers that were free before): grandfather them free until the next respec? [yes]
6. A modifier node unlocks the modifier at once - should its LEVEL (from uses) still start at Lv 1 and grow as today? [yes]
</content>
</invoke>
<invoke name="Bash">
<parameter name="command">cd "/c/Users/SkyLo/Desktop/Hytale mods WORK/SkyWynn PROJECT"; python - <<'EOF'
p='INDEX.md'; b=open(p,'rb').read(); s=b.decode('utf-8')
old="`research/Menu-Icons-Plan.md` = our own icons in every menu: survey + waves)"
new="`research/Menu-Icons-Plan.md` = our own icons in every menu: survey + waves; `research/Ability-Tree-Redesign-Spec.md` = Wynncraft-style class tree, modifier nodes, Lattice loadout, downward trees (R1-R4))"
assert old in s; s=s.replace(old,new,1); open(p,'wb').write(s.encode('utf-8'))
EOF
printf -- "- 2026-10-15 SPEC research/Ability-Tree-Redesign-Spec.md (main session; Skyy's 3 redesign answers): abilities + modifiers as tree nodes (1 AP each, free ROOT, pick-one A4 alts), ability level scales power only, every tree branches down + own icons, owned-only Abilities column with a focus view, Lattice-style 4-row loadout (click ability -> slot, modifier -> slot), migration with grandfathered overflow; rounds R1 layout / R2 model+migration (ultracode) / R3 page / R4 icons; 6 questions with defaults.\n" >> docs/log/2026-10.md; python tools/docs_check.py 2>&1 | tail -2; git add research/Ability-Tree-Redesign-Spec.md INDEX.md docs/log/2026-10.md; git commit -q -m "spec: ability tree redesign (Wynncraft-style nodes, Lattice loadout, downward trees)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git pull --rebase --autostash -q && git push -q; git log --oneline -1