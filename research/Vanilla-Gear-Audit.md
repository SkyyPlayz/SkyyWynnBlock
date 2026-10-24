# Vanilla gear audit - every weapon / armor / shield in Assets.zip vs what we use (2026-10-24)

Where answers go: Skyy's words -> `docs/answered/gear.md`; build steps -> a Gear / Armory round (see "For the local session"). Source: `Assets.zip`
`Server/Item/Items/{Weapon,Armor}/` (read-only; 255 weapon + 119 armor + 5 Hypixel-minigame defs) read against the SET pins (Gear 0.3.44, Armory 0.1.46,
Mobs 0.1.x, Accessories 0.5.32, Quests 0.4.3, Classes 0.1.47). Rule: vanilla first, then packs, then build (PROJECT-RULES 2, AGENT-BRIEF "Vanilla first").

## 0. How to read this (the key finding)

- **Almost every vanilla weapon / armor id is ALREADY in the random mystery-bag pool.** SkyyGear walks all of Assets.zip (`_GEAR_AZ`) and puts every
  piece in `LOOT_POOL` at its material band. Only these are kept out: `gear.exclude` (Shield, Bomb, Gun, Deployable, Dart, Claws, Blowgun, Assault
  Rifle, Handgun, Grenade, Test), `_NPC` / `_Test` / QA / Trooper ids, quality Developer / Debug / Template / Technical, the 6 dev bows, three 0.7 items
  (`Longsword_Ruined_Giant`, `Staff_Voidcrystal`, `Flamethrower_Scrap` = `LOOT_SKIP_07`), every `Armor_Bronze*`, and the 28 Mining metal pieces.
- So "unused" below = **no NAMED role yet** (not craftable on purpose, not UT / Mythic, not a themed mob drop). Nothing here is missing from the game.
- In vanilla, `Bench = TODO` means the recipe points at a bench that does not exist = **not craftable** (all Bronze, Ornate Bronze, Cloth_*, Leather_*,
  Steel_Ancient). "-" = no recipe at all (drop / NPC / creative only). The 7 plain metals (Copper..Mithril) craft at Armor / Weapon Bench.
- Armor stats are flat in vanilla (17 HP, 9% resist) except Copper / Thorium / Cobalt / Adamantite / Mithril; SkyyGear overwrites stats from item
  level anyway, so only look / set / source matter.

## 1. Decisions followed (docs/answered/gear.md)

| Date | Skyy | Effect on this audit |
|---|---|---|
| 10-24 | Ornate Bronze "can be craftable combat gear" (keep our Bronze mining set) | `Armor_Bronze_Ornate_*` -> Smithing > Combat Armor, tier tag |
| 10-24 | "use [Weapon_Daggers_Bronze_Ancient] for a UT or a mythic" | becomes UT / Mythic dagger |
| 10-24 | "check the game for any weapons or armor we overlooked ... fill out the equipment" | this file |
| 10-18 | NO BRONZE ARMOR DROPS (Bronze = T3 Mining set only; Ornate left the bags; `loot.exclude=Armor_Bronze*`) | Ornate Bronze is craft-only; stays out of bags |
| 10-22 | Combat gear into Smithing: only plain metal sets + weapons craftable, rest loot-only; Smithing only (benches refuse) | crafted combat = plain ladders only; no tier-up, Reforge + level + Sigils |
| 10-08 | Mining armor = vanilla metal sets; combat armor = packs (The Armory etc.) as drops; farming / foraging = ours | Armor_Copper..Onyxium + Bronze are Mining, not combat |
| 10-05 | Armor types: Cloth (Wool, Linen, Cotton, Silk, Cindercloth), Light (Leather Soft / Light / Medium / Heavy / Raven), Heavy | those vanilla ladders ARE the starter combat sets |
| 10-05 | Wood armor out of Cloth = first foraging tier; Heavy starter = Heavy Leather | Wood / Heavy Leather used |
| 10-18 / 10-08 | UT = the zone's alloy tier, late zone, elites / mini bosses / dungeons only; Mythic = full bosses only; target per zone 3 armor UT (Cloth / Light / Heavy) + 1 UT weapon per class | roles below |
| 10-08 | Dev bows -> UT / Mythic specials; Dart / Blowgun / Claws / Shield / guns not gear | already done |
| 10-04 | 2 weapon types per class, no sharing (Warrior sword + spear; Berserker axe + mace / club; Archer bow + crossbow; Mage staff + spellbook; Priest wand + spellbook-ish; Monk bo + fist; Assassin dagger + kunai) | role column |
| 10-17 | Zone metals: Z1 Copper / Iron / Bronze, Z2 Thorium / Lead / Dusk, Z3 Cobalt / Chromium / Azurvane, Z4 Adamantite / Slag / Cinder, Z5 Mithril / Titanium / Lumen; Onyxium parked (Z6) | zone column |

## 2. Gaps found (act on these first)

1. **Bronze (Z1 T3) weapons already exist in vanilla for 5 families** and nothing of ours names them: `Weapon_Sword_Bronze`, `Weapon_Spear_Bronze`,
   `Weapon_Shortbow_Bronze`, `Weapon_Staff_Bronze`, `Weapon_Daggers_Bronze` (all Uncommon 25, no recipe, NPC-held). Gear has no `Weapon_*_Bronze*` build
   code, so T3 has no plain weapon yet. Use the vanilla five as the Bronze rung (recipe via Smithing, like the Bronze mining set); build only the missing
   families (Axe, Battleaxe, Club, Mace, Longsword, Wand, Crossbow, Kunai, Spellbook, Bo, Fist).
2. **Vanilla Spear has NO recipe** (Crude is hand-craft, the rest are drop / NPC only). Warrior's second weapon is not craftable at any metal unless our
   Smithing adds recipes. Check `GearPack.combatId` covers `Weapon_Spear_<metal>`.
3. **Ornate Bronze has no Legs** (Head, Chest, Hands only) - Skyy 10-07 already said "Build our own" legs.
4. **Shields are fully outside gear** (17 vanilla ids, `gear.exclude`): no levels, rolls, tier tags, drops. Warrior gets only `Weapon_Shield_Wood`.
5. **Z2 / Z4 UT weapons are free in vanilla**: the Doomed family (Z2) and Saurian family (Z4) cover several classes (section 4).
6. Our "new" Bronze daggers: vanilla `Weapon_Daggers_Bronze` (+ `_Ancient`) already exist and Armory 0.1.46 already treats both as plain signature
   daggers (`SS_SIG_PLAIN`). If a second Bronze dagger was added, drop it and use the vanilla one (no duplicates rule).

## 3. UNUSED vanilla ARMOR (pieces: H head, C chest, A hands, L legs)

| Ids | Name / set | Type | Vanilla tier / source | Suggested role |
|---|---|---|---|---|
| `Armor_Bronze_Ornate_Head / _Chest / _Hands` | Ornate Bronze | Heavy | Rare 28, TODO bench (not craftable), no legs | **Craftable combat Heavy, Z1 T3 Bronze**, Smithing > Combat Armor (Skyy 10-24). Craft only, stays out of bags. Own Legs needed (gap 3). Recipe: our standalone, not the TODO one |
| `Armor_Trork_*` (H C A L) | Trork Warrior | Heavy | Uncommon 25, Trork NPC drops | **Mob drop Z1** from Trork mobs / Chieftain as a themed Set (2-4 pc bonus). Not UT (Z1 Heavy UT = Filing Cabinet) |
| `Armor_Kweebec_Head / _Chest` | Kweebec | Light | Uncommon 20, Kweebec prefab drops, durability 40 | **Mob drop Z1** (Kweebec camps), half set, wardrobe look. Low value |
| `Armor_Steel_*` (H C A L) | Plain Steel | Heavy | Uncommon, no level, no recipe | In Heavy bag already; **normal drop Z1-Z2**. Not craftable |
| `Armor_Prisma_*` (H C A L) | Prisma | Cloth / Light (Mana +20, durability 250) | Common 75, no recipe | **UT Z5 Cloth candidate** (needs trade-off line); Prisma already liked for the Onyxium look (10-07) |
| `Armor_Diving_Crude_*` (H C A L) | Crude Diving | utility | Uncommon 25-30, Oxygen +1000 per piece, NPC prefab only | **Skip for combat bags.** Utility set for SkyyFishing / Exploration (underwater), craft or quest reward |
| `Armor_Wool_*` (H C A L) | Wool (old) | Cloth | Common 30, no recipe | **Skip - duplicate** of `Armor_Cloth_Wool_*` (Gear: "unobtainable"). Leave in pool, never craft |
| `Armor_Onyxium_*` | Onyxium | Heavy | Epic 50, Mana +16, no recipe | Already Mining (Onyxium, parked Z6) - listed for completeness |
| `Armor_QA_*`, `Armor_Trooper_*`, `Debug_Armor_*` | QA / Trooper / debug | - | Debug / Developer | **Skip** (dev, already barred) |

Heavy gap: Z1 Heavy Lv 16-19 had no piece (log 10-19 note) - Ornate Bronze + Trork fill it.

## 4. UNUSED vanilla WEAPONS (by family; class in brackets)

Zone = by metal / level (Copper, Iron, Bronze Z1; Thorium Z2; Cobalt Z3; Adamantite Z4; Mithril Z5). "Pool" = already random-bag drop; "UT" per
10-18 rules (alloy-tier level band, elite / mini boss / dungeon source), "Mythic" = full boss.

| Ids | Name / family | Type [class] | Vanilla tier / source | Suggested role |
|---|---|---|---|---|
| `Sword_Bronze`, `Spear_Bronze`, `Shortbow_Bronze`, `Staff_Bronze` | Bronze tier | sword / spear [Warrior], bow [Archer], staff [Mage] | Uncommon 25, NPC-held, no recipe | **Craftable Z1 T3 Bronze rung** (gap 1) |
| `Sword_Bronze_Ancient` | Ancient Bronze Sword | sword [Warrior] | Uncommon 25, creative only | **UT Z1 Warrior** (matches Skyy's Ancient Bronze Daggers pick) |
| `Daggers_Bronze_Ancient` | Ancient Bronze Daggers | dagger [Assassin] | Uncommon 25, NPC | **UT Z1 Assassin** (Skyy 10-24; Mythic only if Skyy prefers - Q3) |
| `Axe_Doomed`, `Battleaxe_Doomed`, `Club_Doomed`, `Sword_Doomed`, `Daggers_Doomed`, `Daggers_Fang_Doomed`, `Shortbow_Doomed`, `Staff_Doomed`, `Shield_Doomed` | Doomed family | one per class [Berserker x2, Warrior, Assassin x2, Archer, Mage] | Rare 30, undead mob drops (Drops/NPCs) | **UT Z2 line** (Thorium band): one UT weapon per class from one themed family (Berserker Battleaxe, Warrior Sword, Assassin Fang, Archer Shortbow, Mage Staff). Fixes the "33 weapons" shortfall cheaply |
| `Daggers_Adamantite_Saurian`, `Longsword_Adamantite_Saurian`, `Spear_Adamantite_Saurian` | Saurian | dagger [Assassin], longsword + spear [Warrior] | Rare 40, no source in vanilla (creative) | **UT Z4** (Adamantite band); Mythic if given a boss |
| `Sword_Bone`, `Axe_Bone`, `Daggers_Bone`, `Spear_Bone`, `Staff_Bone` | Bone family | sword / spear [Warrior], axe [Berserker], dagger [Assassin], staff [Mage] | Rare 25, skeleton drops | **Z1 named mob drop** (rare). Pool; optionally one Z1 UT from this family |
| `Axe/Battleaxe/Club/Daggers/Longsword/Mace/Spear/Sword _Stone_Trork` | Trork stone | all melee | Uncommon 25, Trork drops | **Z1 Trork mob drops** with the Trork armor set |
| `Club/Mace/Spear/Sword _Scrap`, `Shield_Scrap(_Spiked)`, `Staff_Scrap_Lightbulb` | Goblin scrap | melee, staff | Uncommon 15, Goblin drops | Z1 early normal drops (Pool). Skip for UT |
| `*_Rusty` (`Axe_Iron_`, `Battleaxe_Steel_`, `Club_Iron_`, `Shortbow_Iron_`, `Shield_`) | Rusty trash | melee, bow | Common 15, Skeleton / Trork loot | Z1 trash drops (Pool). Do not craft |
| `Club_Zombie_Frost_Arm/_Leg`, `Club_Zombie_Sand_Arm/_Leg` | Zombie limbs (frost, sand) | club [Berserker] | Common 30, creative / unused | Biome mob drops from frost / sand zombies (Arm / Leg done for normal + burnt via Armory). Pool |
| `Axe_Tribal`, `Battleaxe_Tribal`, `Club_Tribal`, `Longsword_Tribal`, `Spear_Tribal`, `Wand_Tribal`(used) | Tribal | melee [Berserker / Warrior] | Common 15-40, three hand-craft | Z1 starter alternates; Pool. Skip for UT |
| `Longsword_Katana`, `_Void`, `_Scarab` (Armory bench), `Battleaxe_Scarab` (60), `Battleaxe_Scythe_Void`, `Battleaxe_Wood_Fence` (60) | named one-offs | longsword [Warrior], battleaxe [Berserker] | Common 30-60, creative / NPC | **Katana = Z2 normal drop / UT candidate**; Scarab + Void = Z3 drops; Scythe_Void = Mythic candidate (Berserker, void theme); Wood_Fence = skip (joke item) |
| `Sword_Silversteel` | Silversteel | sword [Warrior] | Common 45, creative | **Mythic or Z3-4 UT** (best-named vanilla sword) |
| `Sword_Nexus`, `Sword_Runic`, `Sword_Cutlass`, `Sword_Steel_Incandescent`, `Sword_Wood` | named swords | sword [Warrior] | Common 10-30, creative / NPC | Pool; Nexus + Runic = Z2 normal drops; Wood = skip (starter exists); Cutlass = skip (cosmetic, no level) |
| `Spear_Leaf`, `Spear_Fishbone`, `Spear_Double_Incandescent` | named spears | spear [Warrior] | Unc 15 / Common 25 / Common 30 | Leaf = Z1 Kweebec drop; Fishbone = fishing reward; **Double_Incandescent = Z3 UT** (two-headed, Orbis theme) |
| `Shortbow_Flame`, `Shortbow_Frost` | elemental bows | bow [Archer] | Common 20, creative / NPC | **UT Archer Z1 (Flame) and Z2 (Frost)** or elemental quest rewards |
| `Staff_Crystal_Purple`, `Staff_Crystal_Red`, `Staff_Frost`, `Staff_Wizard`, `Staff_Onion`, `Staff_Cane`, `Staff_Wood_Rotten`, `Staff_Wood_Kweebec`, `Staff_Crystal_Fire_Trork` | named staffs | staff [Mage] | Common 20-40, creative / NPC | Purple + Red = **Mage UT Z3 / Z4**; Frost = Z2 drop; Wizard = Z3 drop; Fire_Trork = Trork Chieftain drop; Cane / Onion / Wood_* = skip (joke / duplicate wood staff) |
| `Halloween_Broomstick` | Broomstick | staff-class [Mage] | Common 40, id has no `Weapon_` prefix | **Skip** (seasonal); event reward later |
| `Spellbook_Demon`, `Spellbook_Grimoire_Purple` | spellbooks | spellbook [Mage] | Common 40, NPC (Purple) | Demon = **Mage UT Z3**; Grimoire_Purple = Z2-3 normal drop. Brown / Fire / Frost / Rekindle already used |
| `Longsword_Ruined_Giant`, `Shield_Ruined_Giant`, `Staff_Voidcrystal` | 0.7 Ruined Giant / Void | longsword [Warrior] | Common 20-40, NPC | Longsword + Voidcrystal are `LOOT_SKIP_07` (held for Skyy's levels) -> **Z3-4 boss drops** (Ruined Giant Mythic Warrior) once Skyy gives levels |
| `Mace_Prisma` | Prisma Mace | mace [Berserker] | Common 50, no recipe | **UT Z5 Berserker** (goes with Prisma UT set) |
| `Weapon_Shield_*` (Wood used) : Copper..Mithril craftable, Onyxium, Doomed, Rusty, Scrap(+Spiked), Praetorian, Ruined_Giant, Orbis_Incandescent, Orbis_Knight | 17 shields | off-hand [Warrior] | Uncommon..Epic; metals craft at Armor Bench | **Needs a decision** (Q2). Default: shield becomes a Warrior off-hand gear slot type with levels / tier tags; metals = craftable ladder, named ones = drops / UT (Orbis_Knight = Z3 UT, Praetorian = Z2, Orbis_Incandescent = Z4) |
| `Weapon_Claws_Tribal`, `Dart_Tribal`, `Blowgun_Tribal` | tribal ranged / fist | none | Common 15-60 | Claws used by Classes (Monk fist); Dart / Blowgun are ammo-style, stay `gear.exclude` |
| `Weapon_Bomb*`, `Bangstick`, `Grenade_Frag`, `Flamethrower_Scrap(_Dungeon)`, `Deployable_*`, `Gun*`, `Assault_Rifle`, `Handgun`, `Test_*_Rifle` | throwables / guns / totems | not class weapons | Hypixel minigame + goblin | **Skip as gear** (already ammo / excluded; guns convert to crossbow + bullets via `pack.convert`). Healing + Slowness Totem are Mage / Accessory items (used) |
| `Template_W_*`, `Debug_*`, `Debug_Stick*` | templates / debug | - | Template / Debug | **Skip** |
| `Weapon_Arrow_Clearshot / Deadeye / Trueshot / Iron` | arrows | ammo | Common 35-75 | Used (ammo; Archer quiver). Nothing to add |
| `Hypixel` Barrier / Lobby / Hyspace | Hypixel minigame props | none | Technical | **Skip** |

## 5. USED ids (reference; named in the SET scripts)

- **Gear:** Mining set pieces (Armor Copper..Onyxium, Bronze via standalone recipe), Cloth / Light / Heavy starter ladders (Wool..Cindercloth, Leather
  Soft..Raven, Wood, Steel Ancient, Heavy Leather), `Weapon_*_Crude`, `Sword_Copper / Iron / Mithril / Onyxium / Steel / Steel_Rusty / Frost / Scrap`,
  `Longsword_Cobalt / Crude / Flame / Ruined_Giant`, `Battleaxe_Crude / Iron`, `Axe_Mithril`, `Mace_Crude / Mithril`, `Staff_*` (Wood, Copper..Onyxium,
  Crystal_Flame / Ice / Fire_Trork, Voidcrystal), `Spellbook_Fire / Rekindle_Embers`, `Wand_Root / Stoneskin / Wood`, the 6 dev bows, `Crossbow_Iron /
  Ancient_Steel`, `Daggers_Stone_Trork`, Arrows, Bombs / Gun / Blunderbuss / Flamethrower (conversion or excluded).
- **Armory:** `Daggers_Bronze / Bronze_Ancient / Claw_Bone / Onyxium / Void_Crystal`, `Club_Zombie_Arm / Burnt_Arm / Burnt_Leg / Leg`, `Longsword_Praetorian(_NPC) /
  Spectral`, `Spellbook_Grimoire_Brown`, `Staff_Bo_Wood / Bo_Bamboo`, `Wand_Wood / Wand_Wood_Rotten / Wand_Tribal`, `Armor_Mithril_Hands / Onyxium_Hands`,
  Kunai, Crossbow_Iron, Shortbow_Crude / Iron / Mithril / Onyxium.
- **Classes:** `Weapon_Sword_Crude`, `Spear_Iron`, `Shield_Wood / Shield_Iron`, `Daggers_Crude / Iron`, `Kunai`, `Bo staff`, `Claws_Tribal`, totems, `Gun / Handgun /
  Assault_Rifle` (kit conversion).
- **Accessories / Quests / Mobs:** `Deployable_Slowness_Totem`; Quests `Weapon_Bomb`, `Kunai`, `Staff_Bo_Bamboo` (starter rewards).
- By family rule (no literal id): every plain metal weapon in the 15-step ladder via `GearPack.combatId`; all pool ids above.

## 6. Duplicates to avoid

| Clash | Keep |
|---|---|
| Bronze weapons: vanilla Sword / Spear / Shortbow / Staff / Daggers_Bronze vs any new Bronze item of ours | **vanilla five**; build only missing families |
| `Armor_Wool_*` vs `Armor_Cloth_Wool_*` (same look) | `Armor_Cloth_Wool_*` |
| `Armor_Steel_*` vs `Armor_Steel_Ancient_*` | both fine (different looks); Ancient = craftable-ladder Heavy, plain Steel = drop |
| Our new Bronze mining set vs Ornate Bronze | both stay (mining vs combat), different looks + ids |
| `Armor_Leather_Heavy` (Heavy ladder start) vs Trork / Steel | Leather Heavy = T1 craft, others = drops |
| Crossbows: vanilla Iron / Ancient Steel vs More Crossbow Tiers vs our TASK-crossbows | per PACK.md, ours replace the mod (one crossbow per metal) |
| Doomed vs Bone vs Trork vs Scrap families (same classes, different zones) | one UT family per zone: Z1 Ancient Bronze, Z2 Doomed, Z4 Saurian; Bone / Trork / Scrap stay normal drops |
| Armory pack shields (91) vs 17 vanilla shields | Armory's are loot; vanilla metal shields = the craftable ladder (per "best version of each") |

## 7. Questions for Skyy (each with today's default)

1. **Ornate Bronze legs:** build our own Legs, or sell the set as 3 pieces? [Build our own Legs, recoloured from `Armor_Bronze_Legs` at build time.]
2. **Shields as gear:** make vanilla shields a real off-hand gear slot (levels, tiers, drops, craft ladder Copper..Mithril)? [Yes: Warrior off-hand; metals craft in Smithing, named ones drop / UT.]
3. **Ancient Bronze Daggers:** UT or Mythic? [UT Z1 Assassin; Mythic sits with bosses, and a Z1 boss drop can come later.] Same call for `Sword_Bronze_Ancient`.
4. **Z2 UT family = Doomed** (one weapon per class) and **Z4 UT family = Saurian + more**? [Yes, Doomed for Z2, Saurian + Prisma / Ruined Giant pieces for Z4-5.]
5. **Trork armor + Trork weapons as a themed Z1 Set** (2 / 4 piece bonus) dropping from Trork mobs? [Yes.]
6. **Diving Crude** as an underwater utility set for Fishing / Exploration (not combat)? [Yes; craft or quest reward, out of combat bags.]
7. **Bronze weapon rung:** use the 5 vanilla Bronze weapons and build only the missing families at T3? [Yes.]
8. **Scythe_Void, Silversteel, Katana as Mythic / UT picks:** which classes get these? [Scythe_Void = Berserker Mythic, Silversteel = Warrior UT Z3-4, Katana = Warrior Z2 drop.]

## 8. For the local session (what the Gear / Armory round must do)

Gear lane (after wc15, per RESUME):
1. **Ornate Bronze craft:** add `Armor_Bronze_Ornate_Head / Chest / Hands` (+ own Legs) to `GearPack.combatId` Heavy list, tier tag via `tools/tier_tags.py`
   (Bronze T3), a standalone Smithing recipe (Bronze bar + Wood + Leather like vanilla, bench TODO replaced; mirror `SkyyGear_Recipe_Armor_Bronze_<Slot>`),
   Heavy weight tag in flavor text, `loot.exclude=Armor_Bronze*` stays (no drops). Update the "no Ornate Bronze" comment/assert in the Heavy ladder.
2. **Bronze weapon rung:** add `Weapon_Sword/Spear/Shortbow/Staff/Daggers_Bronze` to the plain ladder with Smithing recipes (Bronze bars) and band
   Bronze 15-23; build the remaining families only (items missing from `Weapon_<family>_Bronze`). Verify `Weapon_Spear_<metal>` has recipes (gap 2).
3. **UT rows** (`UT_ROWS`): `Daggers_Bronze_Ancient` (+ `Sword_Bronze_Ancient`) as Z1 UT with signature; Z2 Doomed set; Z4 Saurian set; each with the usual
   trade-off line, orange name, elite / dungeon / mini boss source (10-18 rule). Remove the used base from the normal pool when it becomes UT.
4. **Pool tweaks:** exclude `Armor_Diving_Crude_*` (utility) from combat bags; leave `Armor_Wool_*` as is; keep dev bows as is; revisit `LOOT_SKIP_07`.
5. **Shields (if Q2 = yes):** remove `Weapon_Shield_` from `gear.exclude`, add a shield bag type + off-hand slot rules, level bands per metal. Larger: its own round.
6. **Trork set:** a SkyyMobs drop table row (Trork roles) + a Set bonus line in Gear; Kweebec 2-piece likewise.
Armory lane: confirm no second Bronze dagger id is being built (`SS_SIG_PLAIN` already covers vanilla Bronze + Ancient); keep Zombie Frost / Sand limbs as
biome drops. Docs: add a PACK.md-style "Vanilla gear roles" pointer from `INDEX.md`; record Skyy's answers with `skywynn-record`.
