# Stats page spec - SkyBlock-style "Your Profile -> Stats"

Cloud draft, 2026-10-06. Skyy (2026-10-03, playing): *"this menu should show me all my stats with my current gear, accessories, skill and class bonuses, and everything. Like on SkyBlock it should show health, mana, stamina, strength, crit chance, crit damage, mining and foraging fortune, etc. Pretty much all the stats."*
Today's **Your Profile** tile shows purse / bank / skill levels / bag counts, and its text is cut off ("Skills: Mining 6, Forag...").
**Sources:** a read-only code inventory of the newest build script of every mod (done by a search agent in this session; file:line citations below come from that report and **were not re-checked by me**), plus `research/Tool-Levels-Spec.md`, `docs/answered/gear.md`, `docs/answered/skills.md`, `SkyyGear-Stat-Catalog.md` (read only).
Versions inventoried: SkyyGear 0.2.3, SkyyAccessories 0.5.5, SkyySkills 0.4.16, SkyyClasses 0.1.11, SkyyTrees 0.3.2, SkyyCooking 0.1.6, SkyyMenu 0.3.8, SkyyHud 0.3.13, SkyyExploration 0.2.3, SkyyArmory 0.1.
Everything marked **LIVE** is applied by code today; **PLANNED** exists only in docs or rolls as grey text with no effect.

## 1. Findings that shape the design

| # | Finding |
|---|---|
| 1 | **No mod publishes a combined total.** SkyyGear publishes only its own items (`gear:stats:<uuid>` / `gear:fn:stats`), Accessories publish their part as `gear:extra:<uuid>`, Skills publish levels (`skill:<uuid>`, `skill:overall`), Trees publish `tree:fn:bonus`. A stats page must sum them, or read the real **EntityStatMap** for Health / Mana / Stamina. |
| 2 | **SkyyGear has 41 stat keys; 23 are LIVE, 18 are "coming later"** (grey, no effect): Attack Speed, Ferocity, Thorns, Exploding, Poison, Knockback, Slow / Weaken Enemy, the five Element Defences, Combat Wisdom, Loot Bonus, Loot Quality, Stealing, Trophy Hunter, XP Bonus. |
| 3 | **Dead link: class-tree Strength.** SkyyTrees writes `gear:extras:<uuid>` (plural, a map of sources); SkyyGear reads only `gear:extra:<uuid>` (singular string). So Strength nodes (Warrior / Berserker +25, Archer +23) **apply nothing today**. A stats page would show 0 Strength from the class tree until fixed. |
| 4 | **Dead link: `tree:reads:<Mod>`** is published by nobody. All Alchemy and Smithing nodes except Deep Reserves (`PMana`) and Forge Hardened (`SHealth`) are "coming", and the Archer crossbow nodes R2 / R3 / R4 too. |
| 5 | **Tool stats** (Mining Fortune / Speed / Wisdom on pickaxes, Chopping, Farming Fortune) are **PLANNED only**: SkyyGear 0.2.3 says tools roll no modifiers; the tool level is stored and shown but nothing applies it (Tool-Levels-Spec 5.1 stat keys `mfort mwis mpow ffort fwis cpow afort awis`). |
| 6 | The existing **fortune-like effects are live but live in different places**: skill perks (double-drop per level, cap 100%) in SkyySkills; tree nodes (Mining / Foraging / Farming Fortune, Wisdom) via `skill:bonus` (`dd.<skill>`, `xp.<skill>`). |
| 7 | **Why the Your Profile text is cut off** (SkyyMenu 0.3.8, M:1518-1544 / 4219-4234): the info box has 1 wrapped line + 9 rows, each **20 px, FontSize 14, no wrap**, about **80 characters** wide. The "Skills:" line is one long comma-joined string and "Accessory Bag:" is long too; the 80-char assertion covers only static texts, not the dynamic profile body; more than 10 lines get "   ..." appended. |
| 8 | **Hover tooltips are limited**: the profile tile's full text is in a single vanilla item tooltip, not a table. |
| 9 | There is already a per-skill hook: **`skill:stats:<SkillName>`** = `Function(Object[]{UUID, Integer level, Boolean next}) -> List<String>` (max 5 lines), published by SkyyCooking, read by SkyySkills' Stats page. The new page can reuse the idea. |

## 2. The page

### 2.1 Where and how it opens
`SkyyMenu -> Your Profile -> [Stats]` (a button in the Your Profile info area, a new vanilla-look **inline page**, built with the shared kit `tools/skyyui.py`; style per `research/Vanilla-UI-Style-Guide.md`). Also `/stats` (alias `/profilestats`). Opens on the player's **active profile**; admins can open `/stats <player>` (permission `skymenu.stats.others`).

### 2.2 Layout (about 960 x 800)
```
+------------------------------------------------------------------------------+
| Your Stats - Skyy (Warrior, profile "Fox")                    [Refresh] [x]   |
+-------------+----------------------------------------------------------------+
| Combat      |  Health                    284        (hover: breakdown)         |
| Defense     |  Mana                      40                                    |
| Gathering   |  Stamina                   12.0                                  |
| Movement    |  Strength                  63                                    |
| Magic       |  Crit Chance               14%                                   |
| Skills      |  Crit Damage               36%                                   |
| Overall     |  ...                                                             |
|             |                                                                  |
| [ ] Show    |  (rows: label, total, a small coloured source bar)               |
| "coming     |                                                                  |
|  later"     |                                                                  |
+-------------+----------------------------------------------------------------+
```
- **Left**: category tabs (Primary buttons for the active one, Secondary for the rest, equal widths: the vanilla tab rule), a checkbox "Show coming-later stats" (off by default).
- **Right**: one **row per stat**: *name*, *total*, and a thin **stacked bar** coloured by source group (Gear, Accessories, Skills, Class, Trees, Food, Base). Rows are one-line, under 80 characters, so nothing truncates; the page is **not** the 9-line info box.
- **Hover** (vanilla tooltip) on a row = the **breakdown**: `Strength 63  =  Gear +30 (Iron Sword Lv 22, Copper Chestplate)  +  Accessories +12 (Brawler Legendary)  +  Class tree +21 (not applied yet)`.
- **Header**: class, profile name, level lines: `Overall Level 14  |  Warrior (Swordsmanship 22)`.
- A footer note: "Stats show what is applied right now. Grey rows are planned." and a **Refresh** button (no periodic updates: PageManager drops clicks when a page updates itself, a known rule).

### 2.3 Colours and units
White totals; green for a positive contribution, red for negative; percents shown with `%`; flat as integers (Health and Stamina with one decimal when fractional); the source colours are the vanilla kit colours (Gear = white, Accessories = yellow-gold, Skills = green, Class = blue, Trees = cyan, Food = orange, Base = grey).

## 3. The stat list

Groups: **C** Combat, **D** Defense, **G** Gathering, **M** Movement, **Ma** Magic, **S** Skills / Overall. "Source" says which mod supplies the value today. All entries marked LIVE can be shown in **page version 1**.

### 3.1 Combat and defense
| Stat | Key | Unit | Sources (today) | Status |
|---|---|---|---|---|
| **Health** (max) | `health` | flat | vanilla base + armor level-scaled Health (SkyyGear `skyygear_lock_*`) + Accessories (Vitality 6/12/18/24) + Skills (Foraging 0.1, Farming 0.25, class 0.1 per level, Overall 0.5 per level) + Trees (Forest Vigor, Hearty Harvest, ...) + Class-tree Health | LIVE (read from EntityStatMap) |
| **Strength** | `str` | flat pts (+1% each) | SkyyGear weapon / armor + Brawler accessory + class tree (**dead link, 0**) | LIVE (class tree 0) |
| **Magical Power** | `mp` | flat pts | SkyyGear + Runic accessory | LIVE |
| **Damage %** | `dmg` | % | SkyyGear weapon | LIVE |
| **Crit Chance / Crit Damage** | `cc`, `cd` | % | SkyyGear + Razorfang accessory | LIVE |
| Charged Attack Damage | `chg` | % | SkyyGear | LIVE |
| True Damage | `tdmg` | flat | SkyyGear | LIVE |
| Earth / Thunder / Water / Fire / Air Damage | `fEarth`... | flat | SkyyGear weapon (+ Raw Thunder / Water / Elemental) | LIVE |
| Life Steal / Mana Steal | `lsteal`, `msteal` | % / flat per hit | SkyyGear | LIVE |
| **Defense** | `def` | flat | SkyyGear armor + Stonehide accessory | LIVE |
| Physical / Projectile resistance | `resP` | % | armor base (SkyyGear scales vanilla armor) | LIVE (derived) |
| Health Regen | `hpr`, `hprp` | flat / % | SkyyGear + Regeneration accessory | LIVE |
| Class weapon damage | `classDmg` | % | SkySkills class perk (+0.2% per class level) | LIVE |
| Attack Speed, Ferocity, Thorns, Exploding, Poison, Knockback, Slow / Weaken Enemy, Element Defences, Combat Wisdom | | | SkyyGear rows | **PLANNED (grey)** |
| Dodge Chance | `dodge` | % | SkySkills Acrobatics + tree (the dodge *push* is built, not a chance) | PLANNED |

### 3.2 Mana and Stamina
| Stat | Key | Unit | Sources | Status |
|---|---|---|---|---|
| **Mana** (max) | `mana` | flat | vanilla 0 + Skills base (10; Mage / Priest 30) + class per level (Mage +10, Priest +5) + Overall 0.2 per level + Alchemy 0.2 per level + Accessories (Intelligence %, floor) + Trees (Deep Reserves, class tree Mana) | LIVE |
| Mana Regen | `manaregen` | % | `skill:fn:manaregen` registry (trees "Mana Regen" nodes); in-combat 50% | LIVE |
| Mana cost / Spell Cost % | | | | PLANNED |
| **Stamina** (max) | `stamina` | flat | Skills (Mining 0.05, Exploration 0.1 per level) + Accessories (Endurance) + Trees (Miner Stamina, Second Wind ...) | LIVE |
| Stamina Regen | `stam` | flat | SkyyGear armor + Endurance accessory (% top-up) | LIVE |

### 3.3 Gathering (the three Fortune stats Skyy named)
| Stat | Key | Unit | Sources | Status |
|---|---|---|---|---|
| **Mining Fortune** | `mfort` | % double-drop chance (every 100 = +1 drop) | SkySkills perk `doubleDropPerLevel` 0.5% per Mining level + Tree Mining Fortune (1% per level) | LIVE (as double-drop %) |
| **Foraging Fortune** | `ffort` | % | perk 0.5% per level + Tree Foraging Fortune / Fortune II | LIVE |
| **Farming Fortune** | `afort` | % | perk 0.5% per level + Tree Farming Fortune / II | LIVE |
| Mining / Foraging / Farming Wisdom | `mwis`... | % XP | trees `xp.<skill>` | LIVE |
| Mining Speed / Chopping Speed | `mspeed`, `cspeed` | % swing speed | trees (Mining Speed up to +40%) | LIVE |
| Mining Power / Chopping Power | `mpow`, `cpow` | breaking power | tree Heavy Pick / Heavy Hatchet today; **tool levels PLANNED** (Tool-Levels-Spec) | LIVE (trees), tool part PLANNED |
| Tool Fortune / Speed / Wisdom (from the pickaxe / hatchet / hoe) | | | SkyyGear tool rolls | **PLANNED** |
| Double-drop cap | | | `perk.doubleDropMax` 100% | info |

### 3.4 Movement and traversal
| Stat | Key | Unit | Sources | Status |
|---|---|---|---|---|
| **Speed** | `speed` | % | movement protocol sources: `gear.armor`, `accessories.talismans` (Speed accessory), `skills.acrobatics` (+1% per level), `trees.tools`, `trees.acrobatics` (clamped to 0.3-5x) | LIVE |
| Jump height | `jump` | blocks / % | Acrobatics 0.015 per level + trees + Feather accessory | LIVE |
| Fall damage reduction | `fall` | % (cap 80%) | Acrobatics + Feather + trees | LIVE |
| Double Jump | `djump` | height | tree `RDouble` | LIVE |
| Dodge push | `dodgepush` | | Acrobatics + tree | LIVE |

### 3.5 Skills and character
| Stat | Source |
|---|---|
| Overall Level, average, skills counted | `skill:fn:overall` | 
| Class, class skill level, class tree points | `class:<uuid>`, `skill:`, `tree:<uuid>` |
| Skill levels (all 8 + class) with a small bar | `skill:<uuid>` |
| Potion duration, extra potion chance (Alchemy) | perks |
| Food grade (Cooking: heal and buff x(1 + 0.32 x Grade)) | `cook:fn:grade` |
| Exploration level, zones, secrets | `explore:<uuid>` |
| Coins, bank | purse / bank (as today) |
| Accessory bag: Accessory Power (planned), bench accessories, talismans | `acc:has`, `acc:tal` |

### 3.6 SkyBlock list for comparison (memory, UNVERIFIED)
SkyBlock's Stats page shows: Health, Defense, True Defense, Speed, Strength, Crit Chance, Crit Damage, Attack Speed, Ferocity, Ability Damage, Magic Find, Pet Luck, Intelligence, Mining Speed, Mining Fortune, Farming Fortune, Foraging Fortune, Pristine, Sea Creature Chance, Fishing Speed, Trophy Fish Chance, Vitality, Mending, Swing Range, Breaking Power, Cold Resistance ... SkyWynn's list maps to the first ten plus the three Fortunes and Speed; the rest are planned or not part of the design.

## 4. The bridge contract (so the page stays small and every mod stays standalone)

Rule from PROJECT-RULES: cross-mod calls only through the shared `skyy.bridge` map with plain `java.lang` types; per-profile values follow `tools/PROFILES-CONTRACT.md` (key by UUID, always the **active** profile).

### 4.1 Contribution function (new, one per mod)
`stats:contrib:<Mod>` = `Function`, `apply(UUID) -> String`, **lines separated by `\n`**, each line `key|label|value|unit|source`:
```
str|Strength|30|flat|Gear: Iron Sword Lv 22, Copper Chestplate
str|Strength|12|flat|Accessory: Brawler (Legendary)
health|Health|18.0|flat|Skill levels
```
- `key` = the stat key of section 3 (shared names; SkyyGear's own keys reused), `value` a plain number (may be negative), `unit` one of `flat | pct | fraction`, `source` = free text for the tooltip (max 60 chars).
- Each mod publishes a `stats:contrib:<Mod>` (SkyyGear, SkyyAccessories, SkyySkills, SkyyTrees, SkyyClasses, SkyyCooking, SkyyExploration) **only for what it really applies** (LIVE rows) and tags planned rows with unit `planned` or leaves them out.
- A **registry** key `stats:names` = comma list of mods that publish (like `tree:names`).
- The page (SkyyMenu) **sums by key** and draws the breakdown. Without a contributing mod the rows simply omit it, so the page works with only SkyyMenu + one mod.
- **Stats that the engine owns** (Health / Mana / Stamina max): SkyyMenu reads **EntityStatMap** for the **total** (`getMax` or the max modifier values), then uses contributions only for the **breakdown**; the difference shows as "Base / other".

### 4.2 What exists today and can be reused without a change (**phase 1**)
| Source | Existing key | Gives |
|---|---|---|
| SkyyGear | `gear:stats:<uuid>` String `"key:val,..."` | gear stats (held weapon + active armor), already summed |
| SkyyAccessories | `gear:extra:<uuid>` String `"str:12,cc:8,..."` | the accessory part (str, mp, def, cc, cd only) |
| SkyySkills | `skill:<uuid>`, `skill:overall:<uuid>`, `skill:fn:overall`, `skill:fn:manaregen` (get), `skill:fn:level` | levels, Overall bonuses (health / mana), Mana Regen total |
| SkyyTrees | `tree:fn:bonus(Object[]{UUID, "Mining.MFortune"})`, `tree:<uuid>` | node values by key |
| SkyyClasses | `class:<uuid>`, `class:skill:<uuid>` | class names |
| SkyyCooking | `cook:fn:grade`, `skill:stats:Cooking` | grade |
| Party | `party:stats:<uuid>` | hp, max, stamina, max, mana, max (**a free source for the live max values**) |
| Movement | `move:<uuid>` map | speed by source |
So **phase 1 can ship with no change to the other mods**: Health / Mana / Stamina maxima from `party:stats` or the EntityStatMap, SkyyGear + accessory stats from their strings, Mining / Foraging / Farming Fortune from `skill:` perks + `tree:fn:bonus`, speed from the movement map, levels from `skill:`.
The per-source breakdown of Health / Mana / Stamina needs the `stats:contrib` contract (phase 2).

## 5. Build parts

| Part | Mod and version (suggestion) | Work | Size |
|---|---|---|---|
| **P1** | **SkyyMenu 0.3.9 / 0.4** | the Stats page (inline, kit 1.5), tabs, rows, hover, Refresh, `/stats`; phase-1 sources (section 4.2); fix the Your Profile text: replace the long lines with short lines under 80 chars ("Skills: see Stats" + a top-3 line) and a **[Stats]** button | medium (one build) |
| **P2** | SkyyGear, SkyyAccessories, SkyySkills, SkyyTrees, SkyyClasses, SkyyCooking | each publishes `stats:contrib:<Mod>` (a small function reading its own live numbers; no behaviour change) | small each |
| **P3** (fixes found) | SkyyGear 0.2.x + SkyyTrees 0.3.x | read `gear:extras:<uuid>` (the plural map) **or** make SkyyTrees write `gear:extra:<uuid>`; publish `tree:reads:<Mod>` from the mods that read nodes (Alchemy / Smithing nodes then become live) | small, **bug fixes with value for Skyy's tests** |
| **P4** | SkyyGear tool-levels round | tool stats (`mfort mwis mpow ffort fwis cpow afort awis`) appear automatically through P2 | with the tools round |
Round size (PROJECT-RULES 4): P1 = lean round (one mod, no saved data); P2 + P3 = full round because of cross-mod calls (several mods at once).

## 6. Rules and safety
| Rule | Value |
|---|---|
| Per profile | the page shows the **active** profile; contributions are read through the live per-UUID values |
| Performance | one `Function` call per mod per **open or Refresh** (about 8 calls); no per-tick work; contributions computed on the caller's thread reading cached strings (the same as the existing readers) |
| Privacy | `/stats <player>` needs a permission; the normal page is yours only |
| Integer overflow | clamp values (`+-1e9`) like SkyyGear's totals |
| Planned rows | listed under "Show coming-later stats" in grey with the reason ("not built yet"), so players do not think it is a bug |
| Text length | every row under 80 characters; the tooltip text is split into lines under 80 |
| UI rules | inline page, no `.ui` files, no underscores in ids, a Close button in the footer, vanilla tab rule (HANDOFF section 2) |

## 7. Server Setup rows (sketch)
`stats.enabled`, `stats.showPlanned` (default off), `stats.refreshSeconds` (0 = only on Refresh), `stats.others.perm`, `stats.groups` (order of tabs), `stats.rows.<key>.visible` (so a server can hide stats it does not use), `stats.hideZero` (hide rows with 0 total).

## 8. For the local session (UNVERIFIED)
| # | Check |
|---|---|
| 1 | Re-verify the inventory citations before building (the agent report is from this session; line numbers move). |
| 2 | Whether Health / Mana / Stamina **max** can be read per source from `EntityStatMap` modifiers by key (`skyygear_lock_*`, `skyyacc_*`, `skyyskill_*`, `skyytree_*`): they exist as named modifiers, so a **direct modifier read** may replace the contrib calls for those three stats. |
| 3 | The dead links (3 and 4 above) - confirm in game: Warrior class-tree Strength nodes show but add nothing; Alchemy / Smithing nodes show "coming". |
| 4 | Page size and the vanilla tooltip's line limit for the breakdown. |
| 5 | Whether SkyyHud's skills widget should reuse the same sums (a later small step). |

## 9. Questions for Skyy
1. Phase 1 first (SkyyMenu only, quick) and the contribution contract later - or do both together?
2. Show planned (grey) stats by default or hidden behind the checkbox? (Recommended: hidden.)
3. Fortune stats: show Mining / Foraging / Farming Fortune as **% double-drop chance** (how it works today) or SkyBlock-style (100 = one extra drop)? (Recommended: SkyBlock style so the same number works when tools add Fortune.)
4. Should I list the two dead links (class-tree Strength, Alchemy / Smithing nodes) as bug fixes to schedule? (Recommended: yes, small, high value.)
