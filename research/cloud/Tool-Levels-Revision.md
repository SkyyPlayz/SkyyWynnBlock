# Tool levels - revision (speed, Fortune, rarities, Tree Feller, Sickle Range)

Cloud draft, 2026-10-06. Paper design; nothing built. A revision of `research/Tool-Levels-Spec.md` (top note "REVISE FIRST"), not a replacement: every hook, bridge pin, gate and test of that spec stays unless the diff in section 12 changes it.
Inputs read: `docs/answered/gear.md`, `docs/answered/skills.md`, `research/Tool-Levels-Spec.md` (sections 0-9, 13-14), `research/Swing-Speed-Spec.md`, `research/cloud/Gathering-Tiers-Draft.md`, `research/cloud/Collection-Unlocks-Draft.md`,
`research/cloud/Foraging-Armor-Design.md`, `research/cloud/Gathering-Armor-Mining-Farming.md`, `research/Booster-Accessories-Spec.md`, `research/cloud/Pets-Spec.md`, `SkyyGear/build_skyygear_0.2.3.py` (rarity table), `SkyyTrees/build_skyytrees_0.3.py` (Feller rows), `RESUME.md`, `docs/log/2026-10.md`.
Every number is a placeholder and a Server Setup row (times in seconds). All arithmetic python-checked.
Reconciled 2026-10-06, see research/cloud/Gathering-Numbers-Reconciled.md (sections 2, 3, 4, 9, 11, 14 changed).

## 0. The decisions this follows (not re-decided)

| Source | Skyy's words (short) | What it fixes here |
|---|---|---|
| `docs/answered/gear.md` LOCKED 2026-10-02 TOOL LEVELS | "need a to be mining lvl 13 to use a lvl 13 pickaxe" ; pickaxe + shovel = Mining, hatchet = Foraging, hoe + sickle = Farming; "(2) LEVEL raises its breaking speed AND a small Fortune ... hoes / sickles get Fortune only" | gate, skills, hoe / sickle have no speed |
| `docs/answered/gear.md` ANSWERED 2026-10-03 (TOOLS) | "your breaking power makes it take less hits ... once it breaks in 1 hit, you need faster swing speed"; hoe / sickle lock "BUILT AND ON"; "all new tools need a level"; hatchet: "lower the damage so one chop comes later, but increase the swing speed a little earlier" | names Mining / Chopping **Power**; level also gives swing; lenient = old tools only |
| `docs/answered/gear.md` REQUEST 2026-10-05 | "the mining speed and fortune should go up with the level ... they need rarities, and rolls/ reforges ... boost the range of the sickle" | sections 2-10 |
| `docs/answered/gear.md` LOCKED 2026-10-05 (Foraging armor) | "+treefeller on the higher tiers. axes should also get tree feller" (+ NOTE: reuse the SkyyTrees perk) | section 8 |
| `docs/answered/skills.md` LOCKED 2026-09-25 | Tree Feller "extra logs 1 / 2 / 4 / 5 / 6 / 10 at levels 1-6 ... Cooldown 3 s" (live: `feller.logs`, `feller.cooldownSec` in `SkyyTrees/build_skyytrees_0.3.py`) | the only Feller table |
| `docs/answered/gear.md` LOCKED 2026-09-30 | "if its not in the game yet, dont leave it in the reforge list" | a stat rolls only once its code is live |
| `docs/answered/gear.md` LOCKED 2026-10-02 SMITHING / LOCKED 2026-10-04 | reforge "BETTER ROLLS" tree line; Reforge LEVEL UP "+6 levels ... never above the metal's top level or the player's own level" | section 7 |
| `docs/answered/gear.md` R9 | "no sickle / gear swing-speed for now" | kept for **rolls** (no swing roll); the newer 2026-10-03 answer adds swing from the tool **level** |

Bands: the live `level.material` rows. Copper reads **5-18** (Skyy's live edit 2026-10-03, `docs/log/2026-10.md`; the 10-01 lock said 10-18) - this draft reads whatever the row says.

## 1. Tool tiers = gathering tiers (ties to the two cloud drafts)

The recipe for tier N+1 tools appears at the **tier IV** of tier N's key collection (`research/cloud/Collection-Unlocks-Draft.md` 0.2; E curve: III). R3: coins, NPC shops and the Bazaar never skip it.

| Material | Band | Tier (`research/cloud/Gathering-Tiers-Draft.md`) | Pickaxe + shovel recipe | Hatchet recipe | Hoe + sickle recipe | Axe Feller (8) | Foraging armor twin |
|---|---|---|---|---|---|---|---|
| Crude / Wood | 1-13 | start | open | open (Crude: NPC shop) | open | 0 | Wood |
| Copper | 5-18 | T1 | Cobblestone III | Oak IV | Wheat IV | 0 | Softwood |
| Iron | 15-23 | T2 | Copper IV | Birch IV | Carrot IV | 1 | Lightwood |
| Thorium | 20-28 | T3 | Iron IV | Maple IV | Corn VII (draft; move to IV? Q9) | 2 | Hardwood |
| Cobalt | 25-38 | T4 | Thorium IV | Redwood IV | Pumpkin IV | 3 | Drywood |
| Adamantite | 35-43 | T5 | Cobalt IV | Azure IV | Cotton IV | 4 | Darkwood |
| Mithril | 40-49 | T6 | Adamantite III | F5 key IV | Potato IV | 5 | Redwood |
| Onyxium | 40-49 | T7 | Mithril III | later | later | 5 | Goldenwood |
| Cindersteel ... Aetherium (proposal) | 50-100 | T8+ | later | later | later | 6 | - |

Vanilla stops early for farming: hoes Crude / Copper / Iron / Thorium, sickles Crude / Copper / Iron / Steel_Rusty (`research/Tool-Levels-Spec.md` section 1). Cobalt+ hoes and Thorium+ sickles must be **new generated items** (stage 4, Q6); until then a Farming tool tops out at Lv 28 (hoe) / Lv 23 (sickle).

## 2. Level -> speed (per tool type)

Two parts, as Skyy split them: **Power** (fewer hits per block) and **Swing** (faster swings, matters most once a block breaks in 1 hit).

- **Power** = the run-time ladder of `research/Tool-Levels-Spec.md` 3.2 (never below vanilla), with two changes: the material bonus is `tool.matBonus` 1.5 % **per tier** (Copper +1.5 %, Iron +3 %, Mithril +9 %; no longer tied to the band start, so Skyy's band edits do not move it) and hatchets use `tool.power.strength.Hatchet` **50 %** (halfway between vanilla and the ladder - Skyy's "one chop comes later").
  `power = vanilla + (max(vanilla, ladder(L) x (1 + 1.5 % x tier)) - vanilla) x strength`; hits = smallest n with n x power >= 1.
- **Swing %** = min(`tool.swing.max`, floor(`tool.swing.perLevel` x L)). Pickaxe + shovel 0.3 / max 15; hatchet 0.5 / max 20 ("a little earlier"); hoe + sickle 0 (locked: Fortune only).
  Total swing = tree + tool level + armor + pet, each source capped (tool 15 / 20, armor 12, pet 5), **total capped at +40 %** (engine ceiling, `research/Swing-Speed-Spec.md`). Seconds per swing = 0.35 / (1 + swing). A maxed Mining tree (+40 %) leaves no room; Chopping tree max +25 % leaves 15 %.

| Lv | 1 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 | 49 | 60+ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Pickaxe / shovel swing % | 0 | 1 | 3 | 4 | 6 | 7 | 9 | 10 | 12 | 14 | 15 |
| Hatchet swing % | 0 | 2 | 5 | 7 | 10 | 12 | 15 | 17 | 20 | 20 | 20 |

Tool alone, the on-band tool, no tree (time = hits x seconds per swing; vanilla = that material's own vanilla tool):

| Lv (material) | 1 Crude | 5 Crude | 10 Cu | 13 Cu | 15 Iron | 18 Iron | 20 Tho | 25 Cob | 35 Ada | 40 Mith | 49 Mith |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Iron ore: hits / s | 12 / 4.20 | 10 / 3.47 | 8 / 2.72 | 5 / 1.70 | 4 / 1.35 | 3 / 1.00 | 2 / 0.66 | 2 / 0.65 | 2 / 0.64 | 1 / 0.31 | 1 / 0.31 |
| Iron ore vanilla | 12 / 4.20 | 12 / 4.20 | 8 / 2.80 | 8 / 2.80 | 4 / 1.40 | 4 / 1.40 | 2 / 0.70 | 2 / 0.70 | 2 / 0.70 | 1 / 0.35 | 1 / 0.35 |
| Oak log: hits / s | 5 / 1.75 | 5 / 1.72 | 5 / 1.67 | 5 / 1.65 | 4 / 1.31 | 3 / 0.96 | 2 / 0.64 | 2 / 0.62 | 2 / 0.60 | 2 / 0.58 | 2 / 0.58 |
| Oak log vanilla | 5 / 1.75 | 5 / 1.75 | 5 / 1.75 | 5 / 1.75 | 4 / 1.40 | 4 / 1.40 | 2 / 0.70 | 2 / 0.70 | 2 / 0.70 | 2 / 0.70 | 2 / 0.70 |
| Oak log + max Heavy Hatchet | 3 | 3 | 3 | 3 | 2 | 2 | **1** | 1 | 1 | 1 | 1 |

(Crude hatchet "vanilla" = the Lv 1 point lifted to Wood's 0.2, as in `research/Tool-Levels-Spec.md` 3.3.) One-chop with a maxed Heavy Hatchet now starts at **Thorium Lv 20** (vanilla's "top hatchet"), not Iron Lv 20 as in the old spec; every level is still faster than its vanilla tool.

## 3. Level -> Fortune (per tool type)

`Fortune = tool.fortune.perLevel x L x (1 + 2 % x tier)`; pickaxe / shovel / hatchet **0.2**, hoe / sickle **0.3** (they get no speed). 1 Fortune = +1 % chance of one extra drop (= `dd.<skill>` 0.01).

| Lv (tier) | 1 (0) | 10 (1) | 15 (2) | 20 (3) | 25 (4) | 30 (4) | 35 (5) | 40 (6) | 49 (6) | 60 (8) | 100 (11) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Pickaxe / shovel / hatchet | 0.2 | 2.0 | 3.1 | 4.2 | 5.4 | 6.5 | 7.7 | 9.0 | 11.0 | 13.9 | 24.4 |
| Hoe / sickle | 0.3 | 3.1 | 4.7 | 6.4 | 8.1 | 9.7 | 11.6 | 13.4 | 16.5 | 20.9 | 36.6 -> cap 25 |

Old spec: 0.1 x L (Lv 49 Mithril 5.5). Foraging Fortune still doubles **trunks only** (`perk.foraging.doubleDropOnly=_Trunk`, live).

## 4. One shared Fortune rule (tools + armor + skill perk + trees + accessories + pets + collections)

1. **One unit** everywhere: Fortune points, 1 point = +1 % double-drop chance. `research/cloud/Foraging-Armor-Design.md`'s "100 = +1 log per log" is the same unit; percent tables elsewhere are the same numbers.
2. **Add, never multiply.** Each mod posts its own source in `skill:bonus:<uuid>`; SkyySkills sums them (`SkillBonus.sum`, live) and caps the total at `perk.doubleDropMax` **1.0** (live, unchanged).
3. **Each source has its own cap**, enforced by the mod that posts it, so no single source eats the budget:

| Source (bridge source) | Max | Status |
|---|---|---|
| Skill level perk (SkyySkills) | 0.5 a level = 50 at 100 | LIVE |
| Skill trees (`"trees"`) | Mining 20 / Foraging 40 / Farming 45 | LIVE |
| Held tool, level + rolls (`"gear"`) | `tool.fortune.cap` **25** | needs code (this round) |
| Worn gathering armor, all sets (`"gear.armor"`) | `armor.fortune.cap` **15** - one armor ladder 1 / 1.5 / 2.5 / 4 / 5.5 / 7.5 / 10 / 12 for Mining, Foraging AND Farming (`research/cloud/Foraging-Armor-Design.md`'s 4 ... 40 becomes this; Q2). Rarity x1 / 1.1 / 1.2 / 1.3 / 1.3 / 1.3, 4-piece x1.15 before the cap, no 2-piece Fortune | paper |
| Accessories (`"accessories.boosters"`) | 10 (Legendary booster +6 today) | paper |
| Pets | 10 (`research/cloud/Pets-Spec.md`: Legendary Lv 100 +10 / +7; Q1) | paper |
| Maxed collections | 10 per skill (`research/cloud/Collection-Unlocks-Draft.md` 4: ladder 1 / 1 / 1.5 / 2 / 2 / 2.5 = 10, same for Farming) | paper |
| Armor swing (`"gear.armor"`) | `armor.swing.cap` 12 (no rarity multiplier) | paper |
| Pets swing | `pets.swing.cap` 5 | paper |
| Accessories swing | 0 (until Skyy gives a number, Q3 of the reconciliation) | paper |
| Tool Wisdom (rolls) | `tool.wisdom.cap` 15 | paper |
| Armor Wisdom | `armor.wisdom.cap` 10 | paper |

4. **Extra blocks** (Tree Feller logs, Sickle Range crops) roll Fortune at `bonusBlock.fortuneRate` **50 %**, never chain, count once for XP / Collections.
5. Overflow above 100 is wasted (no triple drops) - Q1. The Stats page shows "Mining Fortune 129 (cap 100)".

Progression check (python, `research/cloud/Gathering-Numbers-Reconciled.md` section 2; typical = Rare gear one tier behind, half the tree Fortune; maxed = best possible at that skill): Fortune before the 100 clamp, Mining typical / maxed at skill 10 / 25 / 50 / 75 / 100 = 12.6 / 36.8 / 77.2 / 102.2 / 118.5 and 24.4 / 63.6 / 106.0 / 121.0 / 136.0; Foraging typical 14.3 / 40.9 / 85.6 / 112.2 / 128.5, maxed 30.1 / 77.8 / 126.0 / 141.0 / 156.0; Farming typical 15.7 / 44.7 / 93.3 / 117.0 / 131.0, maxed 32.6 / 84.1 / 131.0 / 146.0 / 161.0. The 100 clamp is first hit by a maxed player at skill 41 (Mining) / 35 (Foraging) / 32 (Farming), by a typical one at 73 / 60 / 56. So Fortune is a mid-game climb; **speed** stays the late-game tool reward.

## 5. Rarity

Same ladder and craft odds as weapons (Normal 60 / Unique 25 / Rare 10 / Legendary 4 / Fabled 1 / Mythic 0, Smithing step-up, max Fabled). Rarity never touches the level line (speed, level Fortune, Feller base) - "same level ~ same tool". It sets:
- **Modifier count** (live `RARITY_DEF`: 1 / 2 / 3 / 4 / 5 / 6) and **roll strength** (30-60 % ... 60-130 % of the stat's max x the level factor 25 % at Lv 0 -> 100 % at Lv 40).
- **Spare-slot boost (new):** a slot the pool cannot fill adds `tool.spareSlotBoost` **+10 %** to every roll (max +30 %). Pickaxe / hatchet / sickle (pool 3): Legendary +10, Fabled +20, Mythic +30 %. Hoe (pool 2): Rare +10 ... Fabled / Mythic +30 %.
- **Axe Tree Feller +1** at Legendary and up (section 8). Frame and name colour as gear (`research/Tool-Levels-Spec.md` 6).

## 6. Modifier pool (a stat rolls only while its code is live)

| Key | Name | Tools | Max at 100 % | Does | Status |
|---|---|---|---|---|---|
| `mfort` | Mining Fortune | pickaxe, shovel | 10 | + `dd.mining` | needs code: SkyyGear `"gear"` source (SkyySkills side LIVE) |
| `mwis` | Mining Wisdom | pickaxe, shovel | 10 | + `xp.mining` | needs code (same) |
| `mpow` | Mining Power | pickaxe, shovel | 30 | power x (1 + v) on rock / ore / soil | needs code (`GearToolHit`) |
| `ffort` / `fwis` | Foraging Fortune / Wisdom | hatchet | 10 / 10 | `dd.foraging` / `xp.foraging` | needs code |
| `cpow` | Chopping Power | hatchet | 30 | power on Woods, blocks only (Heavy Hatchet hard rule) | needs code |
| `afort` / `awis` | Farming Fortune / Wisdom | hoe, sickle | 10 / 10 | `dd.farming` / `xp.farming` | needs code |
| `srng` | **Sickle Range** | sickle only | 3 | harvests extra ripe crops per swing (section 9) | needs code + engine check - rolls only after stage 0 passes |
| - | Swing roll, Mining Spread, Auto Smelt, Timber | - | - | not in the pool (R9; locks 34 / 36 / 39 not built) | never rolls |

Example rolls (python, spare boost in): Fortune Lv 23 Rare 3-5, Mythic 5-12; Lv 49 Mythic 8-17. Power Lv 23 Rare 8-16 %, Mythic 16-35 %. Collections draft key `farmfort` = `afort`.

## 7. Reforge rules

- Same Reforge page and coins (`cost.reforge` x `tool.reforgeCost` 100 %); coins first, refund on failure; Smithing XP `xp.reforge` (live).
- Rarity and level kept; all modifiers re-rolled from that tool's pool; the Smithing tree's better-rolls node applies.
- Reforge LEVEL UP (LOCKED 2026-10-04) covers tools too: +1 level per click, max +6 over the made / found level, never above the band top or your skill.
- A tool that existed before this build (no mark) works at min(its level, your skill); reforging it while you meet its level gives it the mark. Every new tool from any source gets a real level (Skyy 2026-10-03).
- Sickle Range never appears on a non-sickle; a stat switched off server-wide is dropped at the next reforge.

## 8. Tree Feller on axes (reuses SkyyTrees, no second system)

- **Axe Feller level** = `tool.feller.byTier` (table in section 1: Iron 1, Thorium 2, Cobalt 3, Adamantite 4, Mithril / Onyxium 5, T8+ 6) **+1 at Legendary+**, max 6. Logs per level = the live `feller.logs` 1 / 2 / 4 / 5 / 6 / 10.
- **Stacking:** effective level = **MAX**(tree perk, axe, Foraging armor set), never a sum; optional `feller.stackBonus` +1 when all three (default 0); one shared `feller.cooldownSec` **3 s**; same height as the cut; the axe's gate must pass; Feller logs never trigger Feller.
- How: SkyyGear adds `feller.level` to its `"gear"` source; SkyyTrees `TreeAbil.feller` takes the max of its node and every source's `feller.level` - works **without** the perk node.

| Axe | Normal-Rare | Legendary+ | logs |
|---|---|---|---|
| Crude / Wood / Copper | 0 | 0 | - |
| Iron | 1 | 2 | 1 / 2 |
| Thorium | 2 | 3 | 2 / 4 |
| Cobalt | 3 | 4 | 4 / 5 |
| Adamantite | 4 | 5 | 5 / 6 |
| Mithril / Onyxium | 5 | 6 | 6 / 10 |

## 9. Sickle Range

- Range N = the swing also harvests ripe crops up to N blocks left and right of the hit crop, along the swing (+1 = row of 3, +2 = row of 5).
- Rolls (max 3 x rarity x level factor, whole, at least 1): Iron Lv 23 Normal / Unique +1, Rare / Legendary 1-2, Fabled 1-3, Mythic 2-3; Lv 13 Mythic 1-3.
- Cap: tool + Farming armor (`research/cloud/Gathering-Armor-Mining-Farming.md` 2.2) <= min(4, 1 + floor(Farming / 25)) (row of 9 at most); tool part max 3, armor part max 2.
- Extra crops: same ripe / placed rules as a normal harvest, Fortune at 50 % (section 4), Farming XP + Collections only once sickle-swing XP exists (old spec Q3, SkyySkills).

## 10. Tooltip (vanilla look, `GearView.lines`)

```
Iron Pickaxe                                    <- Rare colour
Lv 23 - Requires Mining 23                      <- green; red + " (you: 19)" when too low
Breaks in: Stone 2 hits - Copper Ore 2 - Iron Ore 2
Swing speed at Lv 23: +6%                       <- (max with your tree: +40%)
Mining Fortune at Lv 23: +4.9
Mining Fortune: +4
Mining Power: +12% - fewer hits per block
Mining Wisdom: +3%

RARE TOOL
```
Hatchet adds `Tree Feller II: +2 logs on the cut's level (3 s)`; sickle adds `Sickle Range: +2 (row of 5)`; hoe / sickle show no Breaks-in or swing line.

## 11. Server Setup rows (Gear -> Tools; new or changed vs `research/Tool-Levels-Spec.md` 9)

| Row | Default |
|---|---|
| `tool.power.strength.<Family>` | Pickaxe 100, Shovel 100, Hatchet **50** % |
| `tool.matBonus` | 1.5 % per tier (was 0.3 % x band start) |
| `tool.swing.on` / `tool.swing.perLevel.<Family>` / `tool.swing.max.<Family>` | on / 0.3, 0.3, 0.5 / 15, 15, 20 % |
| `tool.fortune.perLevel.<Family>` / `tool.fortune.cap` | 0.2 (pick, shovel, hatchet), 0.3 (hoe, sickle) / 25 |
| `tool.spareSlotBoost` / max | 10 % / 30 % |
| `tool.feller.on` / `tool.feller.byTier` / rarity step | on / 0,0,0,1,2,3,4,5,5,6 / +1 at Legendary |
| `feller.stackBonus` (SkyyTrees) / `bonusBlock.fortuneRate` | 0 / 50 % |
| `tool.range.on` / `stats.srng` / `tool.range.cap` | off until stage 0 / 3, weight 10 / 4 |
| `armor.fortune.cap`, `pets.fortune.cap`, `coll.fortune.cap`, accessories cap | 15 / 10 / 10 / 10 (each in its own mod) |
| `armor.swing.cap` / `pets.swing.cap` | 12 / 5 |
| `tool.wisdom.cap` / `armor.wisdom.cap` | 15 / 10 |
| `tool.range.capPerFarming` | 25 (range cap = min(4, 1 + floor(Farming / 25))) |
| `tool.popupSec` | 1.5 s (replaces `tool.popupMs`) |
| `tool.farmLock` | **on** (Skyy 2026-10-03) |
| `tool.legacyLenient` | on = tools made before this build only |
| `tool.recipeGate` (SkyyCollections) | on |

## 12. Diff vs `research/Tool-Levels-Spec.md`

| Topic | Old spec | Now |
|---|---|---|
| Stat names | Mining / Chopping **Speed** | Mining / Chopping **Power** (2026-10-03) |
| Swing from level | none (R9) | pickaxe / shovel up to +15 %, hatchet +20 %, shared +40 % cap |
| Hatchet power | full ladder; one-chop Iron Lv 20 (old Q5) | 50 % strength; one-chop Thorium Lv 20 |
| Material bonus | 0.3 % x band start | 1.5 % per tier |
| Level Fortune | 0.1 x L (Lv 49 = 5.5) | 0.2 / 0.3 x L x tier bonus (Lv 49 = 11.0 / 16.5) |
| Fortune caps | only `perk.doubleDropMax` | per-source caps + the global 100 |
| Rarity | count + strength | + spare-slot boost, + axe Feller step |
| Pool | 8 keys, hoe = sickle | + `srng` on sickles |
| Tree Feller | not in spec | axes by tier, MAX rule |
| Old tools (old Q4) | every unmarked tool lenient | only tools made before this build |
| Farm lock (old Q2) | built, OFF | built, ON |
| Recipes | open | behind collection tier IV |
| Popup row | ms | seconds |
| Version | SkyyGear 0.2.2 (shipped other work) | next free SkyyGear (0.2.5 per `RESUME.md` item 5) |

## 13. Build stages

| Stage | What | Round |
|---|---|---|
| 0 | Local checks (UNVERIFIED list 1-4) in the game files, no build | - |
| 1 | SkyyGear: everything of `research/Tool-Levels-Spec.md` 13 with this diff - gate, power, level Fortune, rolls / rarity / reforge, caps, tooltips, `migrate` rows | full (coins, saved data) |
| 2 | SkyyTrees + SkyyGear: tool-level swing tiers, axe `feller.level` (MAX rule) | full (two mods) |
| 3 | Sickle Range (+ SkyySkills sickle-swing XP) | full |
| 4 | SkyyCollections recipe gate + generated Cobalt+ hoes / Thorium+ sickles | full, ultracode (items, several mods) |
| 5 | Per-source Fortune caps in armor / pets / collections as each lands | with those rounds |

## For the local session (UNVERIFIED)

1. Can SkyyGear feed a level part into SkyyTrees' 40 hidden swing-tier effects (pickaxe, hatchet AND shovel roots), so tree + tool + armor pick one tier <= 40?
2. Sickle Range: either generated wider `Sickle_Swing_*_Selector` copies chosen by a hidden effect (the farm-lock trick), or a server-side `FarmingUtil.harvest` on neighbours - a swing fires no event (`research/Tool-Levels-Spec.md` 2.3). Which works, and does the vanilla selector geometry allow a row?
3. `TreeAbil.feller` reading `feller.level` from `skill:bonus:<uuid>`; whether live SkyySkills already rolls double drops on every Feller log (needed for the 50 % rate).
4. Hiding vanilla Workbench tool recipes by collection tier (`coll:recipes`) - today they are open.
5. Re-run the old spec's never-below-vanilla check with the live Copper 5-18 row and the new 1.5 %-per-tier bonus.
6. Model / icon ids for generated Cobalt+ hoes and Thorium+ sickles (art made at build time, nothing committed).
7. What the client draws in a tool tooltip box (old spec stage 0 c).

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | Fortune cap: keep 100 with per-source caps (tool 25, armor 15, accessories / pets / collections 10 each), or let Fortune above 100 give a chance at a 2nd extra drop? (now also Q1 in `research/cloud/Gathering-Numbers-Reconciled.md`) | keep 100, no overflow |
| 2 | One armor Fortune ladder (1 ... 12, cap 15) for all three gathering sets, so Goldenwood = 12 not 40? (see also Q7 in `research/cloud/Gathering-Numbers-Reconciled.md`) | yes |
| 3 | Axe Tree Feller by tier (Iron 1 ... Mithril 5, Legendary+ +1, max 6), MAX with perk and armor? | yes |
| 4 | Hatchet one-chop from Thorium (with max Heavy Hatchet). Note: 2 hits can never beat a vanilla 1-hit (0.25 s swing floor), so "faster" = faster than the same vanilla hatchet. OK? | yes |
| 5 | Sickle Range as a row along the swing, or a square (+1 = 3x3)? | row |
| 6 | Make new Cobalt+ hoes and Thorium+ sickles so Farming tools reach Lv 49? | yes, stage 4 |
| 7 | Spare-slot boost (+10 % rolls per empty slot, max +30 %)? | yes |
| 8 | Drop the "Tree Feller I / II" collection rewards (axes already give it) and use those tiers for something else? | drop |
| 9 | Thorium hoe + sickle at Corn VII (draft) or Corn IV like every other tool? | IV |
