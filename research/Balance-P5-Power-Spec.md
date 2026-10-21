# Balance pass P5 - The four power sources (35 / 30 / 20 / 15): weapons / tools, armor, Void Charms, pets, rarity / reforge, UT / Mythic rates (BUILD-READY spec, 2026-10-20)

Phase P5 of research/Balance-Pass-Spec.md section 8 ("Power sources 35/30/20/15: weapons / tools, armor (3x best vs plain), Void Charms, pets,
reforge / rarity, UT / Mythic rates"). Mods: SkyyGear, SkyyArmory, SkyyAccessories, SkyyPets, SkyyMobs (drops) + the two fixes queued for
P5 (SkyyTrees Rich Seams, SkyyGuilds share). Skyy 2026-10-20: "keep going down the list. dont stop until the entire list is done" + "if you
have any doubt, do research to get good data to base your default on". Spec only - nothing built, nothing committed. Where answers go:
docs/answered/gear.md (gear / drops / accessories lines) + docs/answered/pets.md; this file holds the plan (the main session adds it to
INDEX.md under research/). Builds ON research/Balance-P4-Combat-Spec.md Part 5 (P4 must be pinned first: Gear 0.3.34, Mobs 0.1.14, Armory
0.1.42, Trees 0.4.4) and Pets 0.4.7 (the pets047 round).

**Goals used (Skyy's words, docs/answered/skills.md 2026-10-18, lines 187-191):** power split "35/30/20/15 (Rec.)" = weapon / tool 35,
armor 30, accessories 20, pets 15; best gear "About 3x" plain; UT "1-2 per hour" of elite / dungeon hunting in the right zone; "id never let
a player go more than an hour without at least 1 level up somewhere and some sort of gear upgrade"; one armor set "about 45 min -1.5 hours"
of materials; PROJECT-RULES 4 (2026-10-16) "your gear is important, but accessory's and pets are essential too!"; Mythic "1 per 5-10 boss
kills" (docs/answered/economy.md:162 Q17); "Mythic is always full bosses" + UT from "dungeons, mini bosses, and elite mobs" (gear.md
2026-10-18); Fortune "there isnt a cap on any of the fortunes" + tool "+3 a level ... cant get over 100% till you reach T4" (gear.md 288-290);
pet rarity "a small modifier", pet "Back to Lv 1" on pet rebirth (pets.md 2026-10-15); Heavy Lv 16-19 "Leave gap for balance pass"
(project.md:113).

**Legend.** VERIFIED = read in code / live config (cited). DERIVED = the scratch model (tools/dev/scratch/p5/, deleted after; its functions go
into tools/balance_model.py `--power`, section 7.6). PROPOSED = a default this spec picks. UNVERIFIED = needs the game. W = checked on the web
2026-10-20, K = my knowledge, not checked. Live file = UserData/Saves/NewBetaTest/mods/Skyy_<Mod>/ (read only).

---

## 0. For Skyy (plain words)

1. **Today your ARMOR is the biggest damage source, not your weapon.** Four armor pieces each roll Strength / Crit like a weapon, so a full
   Mythic armor set gives x3.5 damage while a Mythic weapon gives x1.5 (DERIVED, 2.1). P5 gives each armor slot a share of one item's
   power (Chest the most, Hands the least) and makes armor roll mostly Defense and a new **Health %** line. Weapon = damage, armor = toughness.
2. **Best vs plain = about 3x at every level:** Mythic weapon x2.2 damage vs a plain one; best armor x1.9 toughness; best Void Charms x1.25
   both ways; best pet x1.2-1.35. Flat bonus numbers (+6 Fire damage, +24 Health, pet +164 Health) stop mattering after Zone 1 - they become
   % so they keep their value at Lv 100.
3. **UTs: a "UT meter" (like SkyBlock's RNG Meter).** Every elite, mini boss and dungeon mob in a UT band fills it; each point has a 2.5 %
   chance, a full meter (36 points) is a sure UT. Hunting elites / dungeons in the right zone = **~1.7 UT an hour, never more than ~55 min dry**.
   Today it is ~0.05 an hour (a 6 % bag roll x a 2 % orange share).
4. **Mythic: 12 % per boss kill + a sure one by the 10th dry kill = about 1 in 6 kills** (target 5-10; today 10 % with no protection =
   1 in 3 players still dry after 10 kills).
5. **Hourly upgrades:** with item level-ups (+1 level for coins), smarter bags (half of them fill your weakest slot) and the UT meter, the
   model never goes past ~45 min without a gear upgrade before the level cap, and the meter covers the cap stretch.
6. **Void Charms grow over all 5 zones:** every line gets Fabled and Mythic (made with Zone 3 / Zone 4 metals); Mythic = today's Legendary
   numbers, so today's Legendary steps down a little and the ladder is longer.
7. **Pets:** combat pets re-weighed to one budget (a Ram no longer gives -55 % damage taken; a Dog gets a bit stronger), rarity worth a bit more
   (Mythic x1.75), gathering pets give real Fortune (up to ~190 at the end), pet XP slowed so a pet reaches its Lv 50 cap around hour 30.
8. **Fortune budget per skill** (end of each zone) follows 35 / 30 / 20 / 15 with your tool's +3 a level as the anchor; armor keeps today's
   numbers where they are already higher (Zones 1-2) and grows later. Rich Seams fixed (+10 -> +2.5 a rank).
9. **Heavy armor Lv 16-19:** Iron Heavy armor stretches to Lv 19 (Bronze stays the Mining set).
10. **Guild XP:** the guild level curve x20 (gathering XP is ~10-30x what it was before P3), the share stays 10 %.

---

## Research (short; W / K marked)

| Game | What it does | What we take |
|---|---|---|
| Hypixel SkyBlock (W: hypixelskyblock.minecraft.wiki/w/Accessory_Powers, Drop_Chance; K numbers) | accessories: only the highest rarity of a line counts; Magical Power by rarity (~3 / 5 / 8 / 12 / 16 / 22, K - wiki did not confirm) feeds a picked Power that scales with it; drops: Rare 5 % / Extraordinary 1 %; RNG Meter: pick a drop, kills fill the meter, full = the next eligible drop is that item | our AP + Powers already copy this; add more rarities so AP keeps growing; the **RNG-Meter idea = the UT meter** |
| Wynncraft (K) | item tiers Normal / Unique / Rare / Legendary / Fabled / Mythic; identifications roll 30-130 % of a base; Mythics are boss / loot-run only and ~2x a Legendary; set bonuses on few sets | our rarity table already is this; Mythic = boss only; best Mythic weapon ~2.2x plain |
| Diablo 3 / 4 (K) | D3 "smart loot": most legendaries roll for your class; a hidden pity timer raises legendary odds the longer you go without one; D4 weapons carry ~2x the affix budget of armor pieces, item power per slot | **smart bags** (half the bags fill your weakest slot, class lean 75 %), weapon slot power 118 % vs armor slots 26-45 % |
| Path of Exile (K) | no bad-luck protection on uniques; deterministic crafting (currency) gives control instead | reforge = our deterministic path (rerolls, level-ups for coins) |
| Destiny 2 (W: gfinityesports Season 11 raid exotics; Steam thread Last Wish) | raid exotics start ~10 % and each clear without it raises the chance (to 50 % after ~20 clears); some caps reach 100 % | **Mythic: 12 % + sure by the 10th dry boss kill** |
| WoW item budget (K) | stat budget per item level x a slot modifier (chest / legs / head big, hands / wrist small) | slot shares Head 0.20 / Chest 0.35 / Legs 0.30 / Hands 0.15 (the same as P4's armor load) |

Sources (W): https://hypixelskyblock.minecraft.wiki/w/Accessory_Powers , https://hypixelskyblock.minecraft.wiki/w/Drop_Chance ,
https://cyberpost.co/?p=362732 (RNG Meter guide) , https://www.gfinityesports.com/destiny/destiny-2-exotic-drop-rate-buff-season-11-anarchy-one-thousand-voices-1k-always-on-time-ps4-pc-xbox/ ,
https://steamcommunity.com/app/1085660/discussions/0/3829790282378385169 .

---

## 1. The budget (PROPOSED; built on P4 Part 5)

"Power" = DPS x EHP (P4). Best / plain = x3 DPS and ~x3 EHP = ~x9 power, split in log space 35 / 30 / 20 / 15. Plain = a fresh Normal /
Common at your level in every source (Normal weapon + armor, Normal Void Charms in the lines you have, a Common pet of your progress);
best = the best you can own at that level (Mythic weapon / armor with a good roll = p90 of rolls, every line at its top rarity, a Mythic pet
with pet rebirths). Expected (P4's x1.73) = Legendary gear, Rare-Legendary charms, a Rare pet.

| Source (share) | best / plain DPS | best / plain EHP | log power (share of ln 9 = 2.197) | How |
|---|---|---|---|---|
| Weapon / tool (35) | **x2.19** (P4 target 2.16) | x1.0 | 0.78 (36 %) | rarity rolls x weapon slot power 118 % (2.1) |
| Armor (30) | x1.05 mean (x1.11 p90) | **x1.87** (P4 1.93) | 0.68 (31 %) | slot power 26 / 45.5 / 39 / 19.5 %, armor pool = Defense + Health % (2.2) |
| Void Charms (20) | x1.25 | x1.21-1.25 | 0.44 (20 %) | line ladder x1 .. x4.0 over 6 rarities + Balance Power (4) |
| Pets (15) | x1.18 offense kinds | x1.18 defense kinds | 0.30 (14 %) with rarity x1.75 + 5 pet rebirths | kind budget (5) |
| **Kit** | **~x3.2** | **~x2.8** | 2.20 | = P4's DPS x3.19 / EHP x2.85 |

Expected kit (P4 used x1.73): DERIVED x1.65 DPS (Legendary weapon 1.31, armor 1.03, charms 1.12, Rare pet 1.09) and x1.72 EHP -> same-level
trash takes ~4.6 hits instead of P4's 4.4 (target 4-6: ok).

**Not in the kit (P4 Part 4 rule kept):** class level, class / skill trees (one branch <= +30 % on its focus) sit UNDER the kit.

### 1.1 Fortune budget per skill (additive, best-in-tier at the END of each tier; PROPOSED)

Anchor = the lifelong tool (Skyy-fixed: +3 Fortune a level, 10 levels a tier = 30 x T, VERIFIED gear.md 289-290, live `lifelong.perkFortune=3`).
Shares 35 / 30 / 20 / 15 of the total -> armor 25.7 T, Void Charms 17.1 T, pets 12.9 T. Tree rows stay at most 40 a skill (TREE_FORT_MAX,
outside the four sources). No source has a cap (Skyy: "there isnt a cap on any of the fortunes").

| End of | Tier T | Tool | Armor (today -> P5) | Void Charms | Pets | Tree | Total | Drops / block |
|---|---|---|---|---|---|---|---|---|
| Zone 1 | 3 (Bronze) | 90 | ~90 -> 90 (keep) | 51 | 39 | 40 | 310 | 4.1 |
| Zone 2 | 6 (Dusk) | 180 | 135 -> 154 | 103 | 77 | 40 | 554 | 6.5 |
| Zone 3 | 9 (Azurvane) | 270 | 170 -> 231 | 154 | 116 | 40 | 811 | 9.1 |
| Zone 4 | 12 (Cinder) | 360 | 200 -> 309 | 206 | 154 | 40 | 1069 | 11.7 |
| Zone 5 | 15 (Lumen) | 450 | 240 -> 386 | 257 | 193 | 40 | 1326 | 14.3 |

Armor keeps today's (10-18 buff) numbers where they are higher (T1-T4: Zone 1 armor > tool, Skyy "armor should be a big part of the
progression"); from T5 armor = 25.7 x T (section 3.5 table). SkyBlock end-game Fortune sits in the 1000s (K), so 1300 at Zone 5 is in range.
**P6 / P7 must price for it** (collections per tier, Bazaar prices): the coins model (targets.md section 3) is already x2-3 over target in
Zones 1-2, ok in 3-5 - P5's extra Fortune lands mostly in Zones 3-5 (+35-60 %).

---

## 2. Weapons + armor rolls (SkyyGear)

### 2.1 Today (VERIFIED + DERIVED)

- Rolls: `rarity.<id>=<mods>,<low %>,<high %>` (live: Normal 1,30,60 ... Mythic 6,60,130); each modifier = a distinct stat of the live pool
  (SkyyGear 0.3.33 `STATS`, pool.later false) at a uniform % of its max (`stats.<k>=max,weight`), x `stat.levelFloor` 25 -> 100 % at
  `stat.levelFull` 40. Hits: `GearHit.hitAmount` (VERIFIED, script ~28480): x (1 + Damage %) x (1 + Strength %) x charged x crit (chance cc,
  x 2 x (1 + cd %)); flat True / element lines added after armor (`GearTrueSys`); totals summed over the held weapon AND all worn armor.
- DERIVED (scratch Monte Carlo, M melee class, mean): weapon alone Normal x1.04 .. Mythic x1.49; **4 armor pieces alone Normal x1.10 ..
  Mythic x3.49 DPS** (Strength / Crit on every piece) and x1.94 EHP. The power split is upside down.
- Flat lines do not scale: `tdmg` 5, `fEarth`..`fAir` 6, `rThunder` / `rWater` 6, `rElem` 3 (flat damage) and `hpr` 2 (flat regen) are
  +60-100 % of a Lv 1 Copper hit (6 / 6 / 11 a swing) and ~0 % at Lv 100 (F(100) = 78.9, P4).
- `stat.levelFull` 40 is the OLD Mithril level; with 20 levels a zone it is mid Zone 2.

### 2.2 THE RULE (PROPOSED)

1. **Slot power** (new table `slot.power.<slot>`, % of a roll that counts; applied when totals are summed - `GearStats.totals` - AND when the
   tooltip draws the line; the stored roll is unchanged, so every existing item follows at once): **Weapon 118, Head 26, Chest 45.5, Legs 39,
   Hands 19.5** (armor = 1.3 items' worth, shares 0.20 / 0.35 / 0.30 / 0.15 = P4's `armor.slotShare`), every other gear kind (tools,
   equipment) 100. Spell weapons count as Weapon.
2. **Armor pool weights** (new table `pool.armor.<key>=<weight>`; absent = the stat's own weight; armor rolls only): `def 120, hpp 120,
   str 1, mp 1, cc 1, cd 1, chg 8, hprp 32, lsteal 16, hpr 16, spd 32, stam 20` (weapons keep `stats.<k>` weights).
3. **New stat `hpp` "Health %"** (STATS row `("hpp", "Health %", "a", "%", 30, 0, 1, "")` - weight 0 for weapons, armor weight above):
   max Health %, applied through the existing ADDITIVE Untiered Health modifier (`skyygear_ut_hp`, pct x the max without it, recomputed
   every second) - one modifier `skyygear_hp` = sum of hpp lines + UT `hp+` tricks (rename keeps removing the old id on join).
4. **Flat lines become %:** `tdmg`, `fEarth`, `fThunder`, `fWater`, `fFire`, `fAir`, `rThunder`, `rWater`, `rElem` = "+N % of the hit as
   True / <element> damage" (GearTrueSys: N % x the hit's amount before armor, still added after armor); `hpr` = N x H(item level) / 2 s
   (base.hpCurve). Stored numbers are kept and READ the new way (no item change). Lang / tooltip text: "+4 % Fire Damage".
5. **Rarity table** (new defaults): `normal 1,40,70  unique 2,45,75  rare 3,50,85  legendary 4,55,95  fabled 5,60,105  mythic 6,75,120
   set 3,55,100` (untiered 0,0,0 unchanged). Narrower low end (no "dead" rolls), Mythic stays the only one past 105 %.
6. **Level ramp:** `stat.levelFloor` 25 -> **60**, `stat.levelFull` 40 -> **15** (full roll power from Lv 15 = Zone 1's alloy / UT band; P4's
   "same kit ratio at every level" from Zone 1's end).

### 2.3 Result (DERIVED, tools/dev/scratch/p5/tune.py `1.18 1.3 0.25`, 3000 rolls each, M melee class)

| Rarity | Weapon DPS mean (p90) | Armor set DPS mean (p90) | Armor set EHP mean (p90) |
|---|---|---|---|
| Normal | 1.07 (1.17) | 1.00 (1.02) | 1.13 (1.20) |
| Unique | 1.14 (1.28) | 1.01 (1.03) | 1.26 (1.35) |
| Rare | 1.24 (1.44) | 1.01 (1.04) | 1.42 (1.53) |
| Legendary | 1.40 (1.66) | 1.02 (1.06) | 1.58 (1.69) |
| Fabled | 1.56 (1.88) | 1.03 (1.07) | 1.74 (1.83) |
| Mythic | 1.85 (2.33) | 1.05 (1.12) | 1.97 (2.07) |

Best / plain: weapon 2.33 / 1.07 = **x2.19**; armor EHP 2.07 / 1.13 = **x1.83-1.87**; armor DPS x1.05-1.11. Casters: `mp` replaces `str`
(same numbers). The P5 build harness re-runs this (section 7.5) and fails outside +-8 %.

### 2.4 Reforge, sets, Untiered, level-ups (PROPOSED)

- **Reforge cost grows with item level** (`cost.reforge.<r>` second column, today 0): normal 250,10 / unique 500,20 / rare 1000,40 /
  legendary 2500,100 / fabled 5000,200 / mythic 10000,400 / set 2500,100 / untiered 5000,200 (Lv 100 Legendary = 12,500; end-of-Zone-5 coin
  target 10 M). P7 may retune; reforge = the deterministic way to "best" (p90 = a few rerolls).
- **Set pieces** (combat sets from quests / bosses): rarity `set` 3,55,100 + the full-set bonus <= +8 % power (ln 0.077) = about a Fabled
  piece; the harness prints every `set.*` combat row's bonus value (mining / foraging / farming sets are Fortune, section 3.5).
- **Untiered = Fabled power, one big trade-off** (Skyy "both better and worse"): the harness prints each `ut.*` / `utfx.*` row's net log power
  (body lines at `utline.power` 70 % x slot power + the fixed lines and tricks, swing tiers from GearSpeed) and flags any outside Fabled mean
  +-15 % (UNVERIFIED swing times: Paperweight "+50 % harder, 40 % slower" + body str / cd may land under). Fixing a flagged row = a Skyy
  question, never automatic.
- **Mythic** = rarity mythic (6 mods 75-120 %) on the boss's zone items; `levelUp.cap.mythic` 2 stays (Skyy).
- **Level-ups** (`reforge.levelUp`, +1 level for coins up to +6) are counted as gear upgrades by the hourly check (section 6).

---

## 3. Drops: bags, UT meter, Mythic pity, Heavy gap (SkyyGear + SkyyMobs + SkyyArmory)

### 3.1 Normal bags (PROPOSED)
- `loot.mob.chance` 6 % and `loot.mob.capPerHour` 20 stay (4 bags / h of blended play, ~9 / h while only fighting).
- **Smart bags** (new row `loot.smart`, 50 %): half the mob bags pick the slot of the killer's WEAKEST worn item (lowest F(item level) x
  rarity mean / F(player level); empty slot first; weapon = the class weapon) instead of a random type (Diablo 3 smart loot, K).
- `loot.classLean` 50 -> **75** (a weapon bag is your class weapon 3 times in 4).

### 3.2 UT meter (PROPOSED; replaces the 6 % x 2 % gate for UT sources)
- A UT source kill (unchanged list: a mini boss / elite - SkyyMobs `mob:fn:info` "rank" from P4 (elite / mini), else the `sigil.miniWords`
  rule as today - or any mob in a dungeon per `utdrop.dungeon`) whose level sits inside an Untiered row band adds points and rolls:
  `utdrop.points` = `elite 1, mini 5, dungeon 0.25, dungeonBoss 10` (dungeon boss = a boss role in a dungeon world).
- Each kill: chance = `utdrop.chance` (2.5 %) x its points (at most 100 %); the meter (per player, per profile) += points; **meter >= `utdrop.pity`
  (36) = a sure orange bag**; any orange bag (rolled, pity, chest) resets the meter to 0. The bag goes into the inventory like the Mythic bag
  (`GearPackGive`, never a ground drop). Not counted against `loot.mob.capPerHour`.
- `utdrop.mob` (2 % of extra mob bags) is REMOVED for UT sources (they use the meter); `utdrop.chest` 2 % (fresh dungeon chests) stays.
- DERIVED (scratch, 300 runs): dungeon / elite hunting at 40 points / h = **1.67 UT / h, longest dry stretch 0.9 h** (target 1-2 / h); normal
  open-world play in a UT band (3 % elites of 150 kills = 4.5 points / h) ~0.2 / h. Without the pity: 0.8 / h and 1 run in 10 dry for 5 h.
- `/gear loot` shows the meter ("UT meter 22 / 36"); the Gear tooltip of an orange bag says "UT meter".

### 3.3 Mythic (PROPOSED)
- `loot.boss.mythic` 10 -> **12** %; new `loot.boss.pity` **10**: a credited player's 10th boss kill in a row without a Mythic bag gives one
  (per profile, per boss ZONE; reset on any Mythic bag of that zone). DERIVED mean **6.0 kills** (target 5-10); max 10.
- SkyyArmory boss Sigils (rarity +1 items, `sigil.chance` Unique 0 / Rare 4 / Legendary 3 / Fabled 1.5 / Mythic 0): Legendary 3 -> **5**,
  Fabled 1.5 -> **3** (an upgrade path for the cap stretch; Mythic Sigil stays 0 = "Mythic only from bosses' own bags").

### 3.4 Saved data (NEW): `Skyy_SkyyGear/luck/<pkey>.properties` (PROFILES-CONTRACT: per profile, written on change + leave, never while
`profile:busy`): `ut=<points, 2 decimals>`, `my.<zone>=<dry boss kills>`. Missing file = 0 (rollback-safe: older Gear ignores it).

### 3.5 Heavy armor Lv 16-19 (PROPOSED)
New row `level.material.Armor_Iron=8,19` (an armor-only band like `Armor_Copper`; Iron weapons keep `Iron=8,15`): Iron Heavy armor drops /
crafts up to Lv 19, Thorium Heavy starts at 20; Bronze armor stays out (`loot.exclude` Armor_Bronze*, gear.md 311). The Zone 1 Heavy UT
(Filing Cabinet, Lv 15-23) also covers 15-19.

### 3.6 Gathering armor Fortune (SkyyGear `garmor.*`, PROPOSED; section 1.1)
Set total = pieces + set bonus (pieces 70 %, set 30 %, as today). T1-T4 unchanged. From T5 every number x (new / today):
lead x1.07, dusk x1.14, cobalt x1.20, chromium x1.29, azurvane x1.36, adamantite x1.43, slag x1.49, cinder x1.54, mithril x1.59, lumen
x1.61, onyxium x1.61; titanium = 360 total (its set row is missing in the live file: the builder writes `set.mining_titanium` = 30 % of 360 =
108); a Bronze mining tier, if its rows exist, = 77 total. Foraging / Farming (`garmor.foraging` / `garmor.farming` Fortune column, 15
tiers, today 42 .. 168 + set): column T = max(today, 25.7 x T x 0.7) for the pieces and the set bonus raised to 30 % of max(today total,
25.7 x T). The build prints the 3 ladders.

---

## 4. Void Charms (SkyyAccessories)

### 4.1 Today (VERIFIED)
10 stat lines (Health flat 6/12/18/24, Strength 3/6/9/12, Crit 2-8 / 4-16, Defense 3-12, Mana %, Regen, Speed, Stamina, Magic Power, Feather)
+ Lantern + drop-only lines + benches; `MAX_LINE_RARITY` 4 (Legendary, Thorium recipes = Zone 2 start) -> **no charm progression in Zones
2-5**; AP per rarity `power.ap` 10 .. 25; M = (AP / 100) ^ 0.6 (cap 20); Powers per 100 AP. DERIVED today Normal -> Legendary x1.20 DPS /
x1.19 EHP at Lv 1-20, and the flat Health part fades to ~1 % at Lv 100.

### 4.2 PROPOSED
1. **Six rarities per line** (`MAX_LINE_RARITY` 4 -> 6; every `boost.<Line>.*` row gets 6 numbers; the Fabled / Mythic quality ids exist:
   `Skyy_Acc_Fabled`, `Skyy_Acc_Mythic`). Line value = Normal x **1 / 1.6 / 2.2 / 2.8 / 3.4 / 4.0** (Mythic = today's Legendary numbers):
   Strength 3 / 4.8 / 6.6 / 8.4 / 10.2 / 12, Defense same, Magic Power same, Crit 2 .. 8 / 4 .. 16, Speed 2.5 .. 10, Stamina 3 .. 12 (+ regen
   2.5 .. 10), Mana % 6 .. 24, Regeneration 0.25 .. 1, Feather 10 .. 40 / 5 .. 20.
2. **Health line = % of max Health** (`boost.Health.pct` 2 / 3.2 / 4.4 / 5.6 / 6.8 / 8; the `skyyacc_health` modifier becomes ADDITIVE pct x
   the max without it, as SkyyGear's UT hp). The skill-tree row Combat Accessory Plates (trees_v3_effects.py, today +2 flat a charm a rank)
   -> +0.5 % max Health a charm a rank (ceiling 7.5 %).
3. **Recipes for the new steps** (CRAFT tab, the upgrade of the previous rarity, never from scratch): Fabled = the Legendary charm +
   4 Skyy_Ench_Cobalt + the line's Legendary extra x2 (Zone 3); Mythic = the Fabled charm + 4 Skyy_Ench_Adamantite + 2 Skyy_Ench_Mithril
   (Zone 4-5). Unique / Rare / Legendary recipes unchanged. Bench accessories (`BENCH_RARITY`) unchanged. Drop-only lines get the same two
   UPGRADE recipes.
4. **Powers: Health in %** - every `pw.<Power>.hp` value becomes % of max Health per 100 AP at half its old number (Tank 6, Balance 2.5,
   Slayer 1, Lucky 2, Magical 2, Fortress 10, Harmony 4, Glass Cannon -2, Blitz -1.5, Arcane 1.5, Jackpot -1.5). The harness checks
   Balance's best / plain = x1.25 +- 0.05 both ways and prints every Power's DPS / EHP (a Power may lean one way; its log total stays within
   +-10 % of Balance's).
5. **Gathering Powers grow with the skill** (new row `power.gatherLevel` 10 = +100 % per 10 skill levels): Fortune = `pw.<Power>.dd` x M x
   (1 + skill level / 10). `pw.Mining.dd.mining` 6 -> **11**, `pw.Foraging.dd.foraging` 6 -> 11, `pw.Farming.dd.farming` 9 -> 16.5,
   `pw.Fishing.dd.fishing` 2 -> 3.7. DERIVED: end of Zone 1 (Rare lines + benches, AP ~210, M 1.56, Mining Lv 17) = 46 Fortune (budget 51);
   end of Zone 5 (AP ~490, M 2.6, Lv 95) = 300 (budget 257 - the harness fits `pw.*.dd` to the 1.1 table +-15 %).
6. AP per rarity (`power.ap` 10,13,16,19,22,25) unchanged - Fabled / Mythic lines now reach 22 / 25.

DERIVED (scratch): Normal lines + Balance at AP 100 = x1.10 DPS / x1.10 EHP; Mythic lines + Omni (AP 393) = x1.37 / x1.33 -> **x1.25 /
x1.21** (target 1.25 / 1.25; Balance hp 2.5 % per 100 AP closes EHP).

---

## 5. Pets (SkyyPets)

### 5.1 Today (VERIFIED, SkyyPets 0.4.6 + live config)
Bonus = kind value (Lv 100) x rarity (`pets.rarity.*` 1 / 1.1 / 1.2 / 1.3 / 1.4 / 1.5) x level / 100 x (1 + 5 % x pet rebirths); cap Lv 50 +
10 a pet rebirth (100 at 5), level back to 1 on rebirth; XP need(L) = 120 (L-1) + 0.08 (L-1)^3 (Lv 50 = 267 k cumulative); XP = own skill XP
x `pets.xp.ownPercent` 100 % + others x `otherPercent` 50 % (P3 made gathering XP ~5-30x bigger: Pets 0.4.7 divides it back). Health / mana are
FLAT; Fortune capped (`pets.fortune.cap` 10, scaled by rarity). DERIVED Lv 100 power at the kind's start rarity: Ram x3.50 (def 133 =
-55 % damage), Mouflon x2.45, Hawk x2.25, Dog x1.28 - no common budget.

### 5.2 THE RULE (PROPOSED)
1. **One budget per combat kind:** a Lv 100 pet at its kind's start rarity gives power = ln(1 + 0.42 x rarity bonus) (Common x1.42, Rare
   x1.55, Epic x1.61 combined DPS x EHP); offense kinds spend it on str / cc / cd / mp, defense kinds on health % / def, mixed kinds split it.
2. **Rarity** rows 1 / 1.1 / 1.2 / 1.3 / 1.4 / 1.5 -> **1 / 1.15 / 1.3 / 1.45 / 1.6 / 1.75** (still "a small modifier"; with 5 pet rebirths
   a Mythic is x2.19 the Common bonus -> best / plain power x1.35, target x1.39).
3. **health = % of max Health, mana = % of max Mana** (ADDITIVE modifiers, like 4.2.2). Values below already converted (old flat / 3.67 =
   % at P4's Lv 50 M max Health 367).
4. **Combat kinds** (`kind.<Kind>`, Lv 100 value before rarity; DERIVED scale in brackets; mana = the scale x 1/2 - P4 Mana budget: no
   Mana-free spell power beyond the 35 %):

| Kind | Start rarity | Today (live) | P5 |
|---|---|---|---|
| Dog | Common | str:20,cd:15,cc:5 | str:29,cd:21.5,cc:7 (x1.44) |
| Fox | Uncommon | str:27.5,cd:20.5,cc:7 | str:28,cd:21,cc:7 (x1.02) |
| Wolf / SkeletonKnight | Rare | str:33.5,cd:25,cc:8.5 | str:27.5,cd:20.5,cc:7 (x0.82) |
| Tusker | Rare | str:50 | str:42 (x0.84) |
| Skeleton | Rare | cc:33.5,cd:41.5 | cc:24,cd:29.5 (x0.71) |
| Hawk | Epic | cc:41,cd:51.5 | cc:23,cd:29 (x0.56) |
| Boar | Uncommon | health:82,def:27.5 | health:18,def:22 (x0.80) |
| VoidCrawler | Rare | health:100,def:33.5 | health:17.5,def:21.5 (x0.65) |
| Ram | Epic | def:102.5,health:164 | def:28,health:12 (x0.27) |
| Mouflon | Epic | mp:61.5,health:102.5 | mp:26,health:11.5 (x0.42) |
| Skrill / VoidEye | Epic | mp:82,mana:82 | mp:42,mana:21 (x0.51) |
| VoidLarva | Uncommon | mp:54.5,mana:54.5 | mp:42,mana:21 (x0.77) |

5. **Gathering Fortune** (section 1.1: pets 12.9 x T): every Fortune kind's `fortune.<skill>` Lv 100 value -> **88** for a Fortune-only kind
   (Rabbit, Bunny, Cat, Corgi, Frog, Mouse, Squirrel, Meerkat, Turkey), **70** + its second stat unchanged for two-stat kinds (Chicken, Goat,
   Warthog, Bear, Mosshorn, Bison, CrystalGolem, Molerat, Moose, Owl) - a skill pet then gives end of Zone 1 (Rare, Lv ~30) ~34 Fortune,
   end of Zone 5 (Mythic r5 Lv 100) ~190. **`pets.fortune.cap` 10 -> 0 (no cap)** (Skyy's no-cap rule; 0 = off). `pets.swing.cap` 5 stays.
   Exploration kinds (speed / stamina) unchanged.
6. **Pet XP pace** (target: a pet in use reaches its Lv 50 cap at ~hour 30 of run 1, i.e. after its skill's ~Lv 45; pet rebirths are the
   cap-stretch / rebirth-run goal): on P3 XP, `pets.xp.ownPercent` 100 -> **50**, `pets.xp.otherPercent` 50 -> **5**, and Pets 0.4.7's
   divisors (if it shipped per-source divisors) go back to x1 - one rule, two Server Setup rows. DERIVED (P3 trace): skill-pet Lv ~25 at
   12 h, ~44 at 26 h, 50 at ~30 h; a combat pet the same (class XP is on the same P3 curve). Pet rebirth 1 (cap 60) needs 463 k more = the
   cap stretch + rebirth run 1. UNVERIFIED: skill:fn:xp keeps growing at the skill cap (P3 "overflow XP"); if not, pets stop at the cap too.
7. Fusing (4 -> 1, up to Legendary), pet rebirth +5 % stats / +10 % XP, hatch times: unchanged.

---

## 6. The 1-hour rule (DERIVED, scratch copy of tools/balance_model.py + tools/dev/scratch/p5/upg.py, 40 seeds)

Player = the P3 level trace (balanced, 45 % class time, cap 50 at 33 h). Gear upgrade = a bag or craft item better than the worn one by 3 %,
an item level-up (coins, up to +6 over its found level, at each class level-up), or (after the cap) a usable UT.

| Case | Longest stretch without a gear upgrade, before the cap (median / p90) | Whole run 0-45 h |
|---|---|---|
| Today: 4 bags / h random slot, crafting each new metal | 2.1 h / 2.9 h | 4.7 h / 8.4 h |
| + smart bags 50 %, class lean 75 | 1.6 h / 2.3 h | 6.0 h / 9.9 h |
| + item level-ups | **0.70 h / 0.72 h** | 8.4 h (cap stretch: no levels) |
| + UT meter while hunting after the cap (1.67 / h, max 0.9 h dry) | 0.70 h / 0.72 h | **<= 0.9 h while hunting** (2.8 h median when the player only does other things) |

Plus not modelled (all extra upgrades): Void Charm crafts (10+ lines x 5 steps ~ 50 upgrades over Zones 1-3), pet levels / fusing, Mythic
boss pity, Sigils. **Verdict: the rule holds** before the cap with level-ups counted, and in the cap stretch while the player hunts UTs /
bosses (Skyy: "unless they are just afk"). The class level-up side is P3's (its 2.96 h worst stretch is a skill-only gap, P9 rechecks).

---

## 7. Files, keys, Server Setup rows, migrations, checks

One FULL round (drops, saved data, several mods). Build -> adversarial review (lenses: dupes / lost items from the meter + Mythic pity;
migrations; P4 interplay) -> fix -> crosscheck -> pin -> deploy, all jars TOGETHER (FLOOR comment in tools/deploy_set.py: Gear 0.3.35 + Accessories
0.5.30 + Pets 0.4.8 + Armory 0.1.43 + Trees 0.4.5 + Guilds 0.1.13; rollback of Gear alone keeps the slot power off = armor x3 again).
P4's six jars and Pets 0.4.7 must be pinned first.

### 7.1 Per mod (new patch script each, from the SET pin; never edit generated scripts)

| Mod (version, patch) | Changes | Anchors to grep in the current generated script |
|---|---|---|
| SkyyGear 0.3.35 (`tools/gear_0_3_35_patch.py` from build_skyygear_0.3.34.py) | 2.2 (slot power, armor pool, `hpp`, flat lines -> %, rarity table, level ramp), 2.4 (reforge per-level costs), 3.1 (`loot.smart`, classLean 75), 3.2 (UT meter: `utdrop.chance` / `utdrop.pity` / `utdrop.points`, source check reads `mob:fn:info` rank), 3.3 (`loot.boss.mythic` 12, `loot.boss.pity`), 3.4 (luck file), 3.5 (`level.material.Armor_Iron`), 3.6 (garmor ladders T5+), `skyygear_hp` modifier; `/gear loot` meter line | `STATS = [` 2945, `RARITY_DEF` / `ODDS_DEF` ~2900, `GearHit.hitAmount` ~28480, `GearTrueSys`, `GearLevel.factor` 16461, `GearUt.source`, `GearPack.bossRoll`, `BOSS_MY` 10088, CFG rows 7540-7800, `skyygear_ut_hp`, `GEAR_MINE` / `garmor.mining.*` defaults, `_DANGER` 8181 |
| SkyyArmory 0.1.43 (`tools/armory_0_1_43_patch.py` from 0.1.42) | `SGL_PCT` [0, 4, 3, 1.5, 0] -> [0, 4, 5, 3, 0]; harness: a charged spell hit goes through `GearHit.hitAmount` (slot power 118 % applies to `mp`) | `SGL_PCT` 1195, `sigil.chance` row 7234 |
| SkyyAccessories 0.5.30 (`tools/accessories_0_5_30_patch.py`) | 4.2 (6 rarities, values, Health %, recipes, Power hp %, `power.gatherLevel`, gathering dd rows) | `MAX_LINE_RARITY` ~298, booster table ~356-366, `PW_DEFS` 3859, `AccPower.tick`, `skyyacc_health`, drop-up recipes ~598 |
| SkyyPets 0.4.8 (`tools/pets_0_4_8_patch.py` from 0.4.7) | 5.2 (kind values, rarity rows, health / mana %, Fortune 88 / 70, cap 0, XP percents, drop 0.4.7 divisors) | `KINDS_*` / `kind.` defaults ~189-235 + 653, `pets.rarity.` ~1265, `pets.fortune.cap`, `pets.xp.ownPercent`, `PetBuff.compute2` |
| SkyyTrees 0.4.5 (`tools/trees_0_4_5_patch.py` + tools/trees_v3_effects.py) | Rich Seams: `nodes.Mining` MFortune.per 0.1 -> **0.025** (+2.5 a rank, 7.5 at rank 3; text "+2.5 Mining Fortune a rank"); Masterwork Pick Fortune 0.075 -> **0.05** (5 / 10 held own pick); Rich Seams counted in `check()` (new READ_OLD-style entry with its max) -> Mining tree Fortune = 7.5 + 10 + 15 + 7.5 = **40** (was 67.5); Combat Accessory Plates -> 0.005 hp % | `FORT323` 2365, MFortune row 2104, trees_v3_effects.py EFFECTS "r6" dd.mining + Plates, `TREE_FORT_MAX` 177 |
| SkyyGuilds 0.1.13 (`tools/guilds_0_1_13_patch.py`) | `levelBase` 100 -> **2000**, `levelStep` 150 -> **3000** (x20: P3 gathering XP per hour is x5 Zone 1, x22 Zone 2, x34 Zone 3 of the old; `xpSharePercent` 10 stays) | `levelBase=100` 1060, CFG row near 1523 |
| SkyyMobs | no build if P4's 0.1.14 `mob:fn:info` answers "rank" (elite / mini / boss); otherwise 0.1.15 adds it (one bridge field) | `mob:fn:info` |

### 7.2 Server Setup rows (tools/skyycfg.py, KEEP=10; Menu-Pattern pages)

| Mod -> page | Row (key) | Type / range | Default |
|---|---|---|---|
| Gear -> Stats | Slot power (`slot.power`: Weapon, Head, Chest, Legs, Hands) | table int 0-300 % | 118 / 26 / 45.5 / 39 / 19.5 (dec) |
| Gear -> Stats | Armor roll weights (`pool.armor`) | table int 0-1000 | 2.2.2 |
| Gear -> Stats | Modifier power at item level 0 / full level (existing) | int | 60 / 15 |
| Gear -> Rarity | Modifiers and roll power (existing `rarity`) | table | 2.2.5 |
| Gear -> Costs | Reforge cost (existing, per-level column) | table | 2.4 |
| Gear -> Loot | Smart bags % (`loot.smart`) / Own-class weapon weight (existing `loot.classLean`) | int 0-100 | 50 / 75 |
| Gear -> Loot | UT chance per point % (`utdrop.chance`), UT meter size (`utdrop.pity`), UT points (`utdrop.points`, text `elite 1, mini 5, dungeon 0.25, dungeonBoss 10`) | dec 0-100 / dec 1-1000 / text | 2.5 / 36 / text |
| Gear -> Loot | Boss Mythic bag chance (existing) / Sure Mythic after dry kills (`loot.boss.pity`, 0 = off) | dec / int 0-100 | 12 / 10 |
| Gear -> Levels | Iron armor band (`level.material.Armor_Iron`) | existing table | 8,19 |
| Armory -> Soul | Boss Sigil drop chance (existing table) | | 0 / 4 / 5 / 3 / 0 |
| Void Charms -> Power | Gathering power per 10 skill levels (`power.gatherLevel`) | int 0-100 | 10 |
| Pets -> Rarity / Kinds / XP | existing rows (new defaults 5.2) | | |
| Trees -> Mining (nodes) | existing MFortune per | | 0.025 |
| Guilds -> XP | existing levelBase / levelStep | | 2000 / 3000 |

### 7.3 One-time migrations (PROJECT-RULES 4; clone the reviewed kits: Gear `migrate0327` / `migrate0328`, Pets `PetsCfgMig2`, Trees `TreeMig323`, Accessories `M518`)

- Only lines still holding the EXACT previous default change (per key; a table row only when its whole old default text matches); a hand-edited
  value is kept + one INFO line; History copy verified first; one config-changes.log line per change (Undo in Server Setup -> Changes); bytes +
  line endings kept; a java.util.Properties check that only the planned keys differ; run-once marker written LAST (`Balance P5 power (SkyyGear
  0.3.35)` / `... (SkyyAccessories 0.5.30)` / `... (SkyyPets 0.4.8)` / `... (SkyyTrees 0.4.5)` / `... (SkyyGuilds 0.1.13)`); a fresh file carries it.
- Gear: `rarity.*` 7 rows, `stat.levelFloor` 25, `stat.levelFull` 40, `cost.reforge.*` (`N,0` rows), `loot.classLean` 50, `loot.boss.mythic` 10,
  `garmor.mining.<tier>` / `set.mining_<tier>` T5+ and `garmor.foraging` / `garmor.farming` (Skyy's live file = the 10-18 buff defaults ->
  migrate); new keys appended (absent = default). Accessories: every `boost.*` 4-number row -> 6 numbers when it still equals the 0.5.29
  default; `pw.*.hp` and the 4 gathering `pw.*.dd` rows. Pets: `kind.<Kind>` rows still at the 0.3.1 defaults (live file: yes), the 6
  `pets.rarity.*`, `pets.fortune.cap` 10, `pets.xp.ownPercent` 100 / `otherPercent` 50 (and 0.4.7's divisor rows if any). Trees: `nodes.Mining`
  MFortune.per 0.1 (the TreeMig323 value). Guilds: levelBase 100 / levelStep 150.
- Copy the live files to `tools/dev/scratch/p5b/` and run each migration in the harness there (LIVE check).
- **Saved items:** nothing rewritten. Existing rolls follow slot power and the %-reading of flat lines at once (a Lv 5 sword's "+6 Fire" =
  +6 %: a nerf in Zone 1, intended); old Legendary charms read the new Legendary numbers (x2.8 instead of x4: a step down, Fabled / Mythic
  now above). Pet records unchanged (values live in config). Guild XP unchanged (levels recomputed from XP -> guilds DROP levels: the harness
  prints old / new level per guild; one chat line to the guild "Guild levels were re-scaled (balance pass)"; levels give nothing yet).

### 7.4 Harness checks (each mod's bare-JVM test, -Xverify:all, then all jars in one JVM)
1. Gear: Monte Carlo of `GearRoll` (the real roll code, 3000 rolls x rarity) through `GearStats.totals` + `hitAmount` -> table 2.3 +-8 %;
   slot power applied to totals AND tooltips; an item rolled before the patch reads the same lines x slot power.
2. Gear UT meter: points / chance / pity on scripted kills (elite, mini, dungeon, boss, outside a UT band = 0); exactly one bag per pity; reset
   on any orange bag; luck file round trip; profile switch keeps meters apart; no bag while `profile:busy` (queued). Mythic pity on the 10th
   dry kill, per zone.
3. Accessories: Balance best / plain 1.25 +- 0.05 both ways; every Power's log total within +-10 % of Balance; gathering Fortune vs table 1.1
   +-15 % at Lv 17 / 95.
4. Pets: every combat kind's Lv 100 power at its start rarity = ln(1 + 0.42 x rarity) +- 5 %; Fortune kinds at the 1.1 targets; XP pace
   trace (P3 numbers) hits Lv 50 at 28-33 h.
5. Trees: `check()` Mining = 40.0 <= TREE_FORT_MAX; Rich Seams text matches.
6. Migrations on fresh / live copy / hand-edited / half-migrated files (marker last).

### 7.5 Model check (DERIVED - the numbers hit the targets)

| Target (source) | Model | OK |
|---|---|---|
| Split 35 / 30 / 20 / 15 (A:190 Q15) | 36 / 31 / 20 / 14 % of ln 9 | yes |
| Best ~3x plain (A:190 Q14) | DPS x3.2, EHP x2.8 (= P4 Part 5) | yes |
| UT 1-2 / h hunting (A:190 Q16) | 1.67 / h, max 0.9 h dry | yes |
| Mythic 1 per 5-10 boss kills (economy.md:162) | mean 6.0, max 10 | yes |
| <= 1 h without a gear upgrade (A:187 Q2) | 0.72 h (p90) before the cap; <= 0.9 h hunting after | yes (cap stretch needs hunting) |
| Armor set 45 min-1.5 h (A:191 Q22) | not changed here (P6 collections; targets.md 2.84 h) | P6 |
| Mining tree Fortune <= 40 (TREE_FORT_MAX) | 40.0 (was 67.5) | yes |
| Accessories / pets essential (PROJECT-RULES 4) | over no charms / no pet: charms x1.10 (Normal) .. x1.37 (Mythic); a pet x1.2 (Common Lv 50) .. x1.9 (Mythic, 5 pet rebirths, Lv 100), DPS x EHP | yes |

### 7.6 balance_model.py (the P5 builder adds `--power`, AFTER P4's commit - P4 is editing it now; never in parallel)
The scratch scripts were deleted (AGENT-BRIEF); rebuild them from this spec into a `power` section: the roll Monte Carlo (2.1 pool + 2.2
rules, DPS / EHP formulas of 2.1 with lsteal 1 pt = +2 % EHP, hprp 1 pt = +0.25 %, charged hits 25 % of hits), the 2.3 table, the 1-hour
check (section 6 rules: bag rate 4.05 / h blended, mob odds + levelShift 0.02, smart 50 %, craft each new metal band, level-ups to +6, 3 %
upgrade threshold, 40 seeds) and the UT / Mythic meter sims (3.2 / 3.3): prints 1, 1.1, 2.3, 4.2 (derived), 5.2 and 6 into research/balance/targets.md ("### 7. Power sources"); the
"UT drops per hour" row uses the meter (40 points / h hunting), "Boss kills per Mythic" = 6.0, "Gear loot bags per hour" gets its upgrade
share; `--check` exits 1 when a row fails. Class Balance Workbench republished after deploy (pets / gear numbers changed).

### 7.7 In-game test steps (TEST-CHECKLIST after deploy)
1. Wear a full armor set of any rarity: the tooltip's Strength / Crit lines read smaller (x slot power); `/gear stats` damage drops, Health
   rises with Health % lines on new drops.
2. A weapon with "+N Fire Damage" now reads "+N % Fire Damage".
3. Kill elites / a dungeon in Zone 1's Lv 15-23 band: `/gear loot` meter climbs; an orange bag within ~36 points.
4. Kill a boss 10 times: a Mythic bag by the 10th at the latest.
5. Void Charms CRAFT: a Legendary charm shows a Fabled upgrade (Cobalt) - Health line in %.
6. Pets: a Ram gives about 12 % Health / 28 Defense at Lv 100 (Lv 50 = half); a Mouse pet's Mining Fortune ~44 at Lv 50 Common.
7. Mining tree: Rich Seams 3 ranks = +7.5 Fortune.
8. Server Setup -> Changes lists every migrated line with Undo.

### 7.8 UNVERIFIED
Distinct stats per item (the model assumes no stat twice - check `GearRoll`); swing / cast times (UT net power); whether skill XP still
flows at the skill cap (pet pace in the cap stretch); how many elites / dungeon mobs a player meets per hour while "hunting" (40 points / h
assumed; if elites are too rare outside dungeons, see Q5); the live `garmor.*` rows after the 10-18 buff for Bronze / Titanium.

---

## Questions for Skyy (each with today's default in [brackets])

1. **Armor = toughness, weapon = damage:** armor pieces roll mostly Defense + a new Health %, each slot a share of one item's power (Chest most,
   Hands least)? Existing armor gets weaker damage lines at once. [yes]
2. **Flat bonus lines become %** ("+6 Fire Damage" -> "+6 % Fire Damage", charm / pet Health -> % of max Health) so they keep working at
   Lv 100 (Zone 1 items with flat lines get weaker)? [yes]
3. **UT meter:** each elite / mini boss / dungeon mob in a UT band = points, 2.5 % a point, a sure UT at 36 points (~1.7 UTs an hour of
   hunting, never ~1 h dry)? [yes]
4. **Mythic: 12 % a boss kill, a sure one by the 10th dry kill** (about 1 in 6)? [yes]
5. **If elites are too rare to "hunt" outside dungeons:** raise the elite spawn chance inside UT bands (3 % -> 8 %)? [no - dungeons + elites as
   they are; revisit after testing]
6. **Void Charms to Mythic:** every line gets Fabled (Cobalt, Zone 3) + Mythic (Adamantite / Mithril, Zone 4-5); Mythic = today's Legendary
   numbers, so today's Legendary charms drop a little? [yes] (alternative: keep Legendary, Fabled / Mythic above it = +35 % stronger charms)
7. **Mythic charms crafted or boss-only?** [crafted with Zone 4-5 metals]
8. **Pet rarity a bit stronger:** x1 / 1.15 / 1.3 / 1.45 / 1.6 / 1.75 (today up to x1.5)? [yes]
9. **Pets re-weighed to one budget** (Ram, Hawk, Mouflon, Skrill weaker; Dog stronger; gathering pets ~9x more Fortune, no Fortune cap)? [yes]
10. **Pet XP:** own skill 50 %, other skills 5 % -> a pet hits its Lv 50 cap around hour 30? [yes]
11. **Fortune grows with the 35 / 30 / 20 / 15 split** (Zone 5 end ~1300 Fortune = ~14 drops a block; armor x1.1-1.6 from Zone 2 on; prices
    follow in P6 / P7)? [yes]
12. **Heavy Lv 16-19:** Iron Heavy armor goes up to Lv 19? [yes]
13. **Guild levels re-scaled** (curve x20, existing guilds drop levels - they give nothing yet)? [yes]
14. **Reforge costs grow with item level** (Lv 100 Legendary 12,500 coins)? [yes - P7 may retune]
