# Pack armor (and The Armory weapons) - plan

*Written 2026-10-08. Planning only: nothing built, deployed or committed. Owner: Skyy (they/them).*

Skyy (docs/answered/gear.md, 2026-10-08): "my idea is, instead of wasting time making a ton of our own gear, letsd focus mostly on the
classes, and weapons. and use mods like this. take there armor, and based on looks, and specs sort them by Cloth, Light and heavy armor.
then make most of them mob drops for tons of variety. random drops, and special sets."

Later the same day: "longswords for warrior, flails for berserker, specials as boss drops (we can make our own specals too, so we dont
have some classes with a ton more weapons than others." and "might add another class that uses flails and whips later." Then: "zweihander for warrior, dual swords for assassin."

**Rules (PROJECT-RULES 2):** we react to other mods' item ids at runtime only. We never ship a file that overrides their ids, and we never
copy their recipes, numbers, models or textures. This file names ids and gives our own classification. Stats below are short summaries.

Data: a read-only scan of every archive in Skyy's `UserData/Mods` folder (Parent chains resolved through Assets.zip) on 2026-10-08.

---

## 0. Plain words (for Skyy)

- The Armory has **1,019 armor items + 282 weapons = 1,301** (their "over 1300"). But most are **colour swaps**: only **91 different
  armor models**. 946 armor pieces are made by swapping colours at their Alteration Table; only **57** have a real recipe.
- **Today SkyyGear ignores almost all of it.** SkyyGear only treats ids starting with `Armor_` / `Weapon_` as gear. Only 97 Armory armor
  ids (the Iron recolours) and 125 weapon ids qualify. The other ~1,050 would show vanilla stats, no rarity, no level.
- **The Armory is installed but switched OFF** in the test world ("HUD mod"). It is not in PACK.md. Step 1 is to switch it on and add it.
- **Licence: CC Attribution-NonCommercial** (their CurseForge FAQ): we may use it in the pack if we credit it and never sell it; changing
  its stats / recipes is allowed (their page suggests ItemForge). There is no in-mod config for it - a change means an override (section 4).
- **It already puts its items into world chests** (it patches 52 vanilla prefab chest drop lists with 4 zone loot lists, 145 armor ids).
- We can make all of it work **from our own code**: one id table (type + level band + drop group), our own drop roll, our own set bonuses.
- Recommended pool: The Armory + SLVR Arcane Robes + Arcane Power + Voidcloak = **1,052 pieces: Heavy 499 / Cloth 278 / Light 275**.

---

## 1. Inventory

### 1.1 Counts per mod (armor items; "Use" = our recommendation)

| Mod (file) | Pieces | Head / Chest / Hands / Legs | Their recipe bench | Use |
|---|---|---|---|---|
| **The Armory** (TheArmoryMod-1.22.0.jar, LadyPaladra) | 1,019 (1,010 armor + 9 Kanohi props) | 544 / 244 / 93 / 129 | Alteration Table 946, Armor Bench 57, none 16 | **Yes** (main pool) |
| SLVR Arcane Robes & Spells (SlverSkull) | 24 | 6 / 6 / 6 / 6 | SLVR Loombench | **Yes** (Cloth ladder) |
| Arcane Power (Tayko) | 14 | 6 / 2 / 2 / 4 | Runecrafter's Table | **Yes** (Cloth, high) |
| Voidcloak Armory (Vortex) | 4 | 1 / 1 / 1 / 1 | Armor Bench | **Yes** (Light set) |
| PJ-HyperGlowingArmors (Pedrijoe) | 64 | 16 each | Armor Bench | Maybe (glowing vanilla metals; the 32 "_2x" double-stat pieces: no) |
| TerrariaToolsWeapons (Markebarca) | 20 | 5 each | own workbench / Lead + Iron anvils | Maybe (early Heavy) |
| MajorDungeons (MAJOR76) | 18 | 4 / 6 / 5 / 3 | their dungeon coin shop / furnace | Maybe (leave as their dungeon rewards) |
| Marsi Dungeon | 12 | 6 / 2 / 2 / 2 | Armor Bench | Maybe (their dungeon) |
| Fullmetal Labyrinth (Lunaronin777) | 8 | 2 each | Armor Bench | Maybe (their dungeon) |
| Aures Rare Monsters | 6 | 6 / 0 / 0 / 0 | Armor Bench | Maybe (horn helms) |
| MoreBoots (Wyyne) | 5 | legs slot only | Armor Bench | Maybe (effect boots) |
| Hylamity (Wulfrum set) | 4 | 1 each | own bench | Maybe |
| TerrariaAddons | 2 | heads | Armor Bench | Maybe (Wizard Hat only) |
| NecromancerSpire | 1 | Necrotic Crown | none (drop) | Maybe (boss drop already) |
| LOTR Project | 37 | 12 / 9 / 8 / 8 | Elven Armor Bench | No (Tolkien theme) |
| CD Tritale (Zelda tunics) | 32 | 4 / 4 / 12 / 12 | Tritale offering | No (Zelda theme, own dungeon) |
| UnstableRifts (ninesliced) | 24 | 6 each | Armor Bench | No (own rift loot + set abilities - would double up with ours) |
| MMOSkillTree capes | 22 | chest | "TODO" | No (another skill mod's capes, Lv 100-200) |
| EndgameAndQoL (Lewai) | 20 | 5 each | Armor / Endgame Bench | No (OVERRIDES 20 vanilla ids) |
| Skyys-HyMax (Skyy's old pack) | 20 | 5 each | Armor Bench | No (OVERRIDES 20 vanilla ids) |
| TheLostWorlds | 20 | 5 each | Loombench_Test | No (OVERRIDES 20 vanilla cloth ids) |
| Mermaids | 11 | chest | own workbench | No (theme) |
| Captain America Suit | 8 | 2 each | Armor Bench | No (Marvel) |
| StarTale (Beskar, Stormtrooper) | 8 | 2 each | own benches | No (Star Wars) |
| ArmCannons | 4 | chest | Armor Bench | No (Mega Man) |
| VoidAsylum (Geared Cent) | 4 | 1 each | Armor Bench | No ("Developer" quality) |
| Below Every Heaven (Holloway) | 4 | 1 each | Cursed Altar | No (Lv 75, their boss content) |
| Zorras ScubaGear | 4 | 1 each | Armor Bench | No (utility; same look as vanilla diving) |
| Oasis / PJ-ForgottenCreatures / Skyys-Modpack | 4 + 3 + 3 | Bramblekin | Armor Bench | No (same `Armor_Bramblekin_*` ids in 3 mods - clash) |
| Mort's Wandering Merchant | 3 | hats | none | No (trader stock) |
| Jetpacks | 3 | chest | Armor Bench | No (utility, 2 cosmetic-only) |
| NoCube Bakehouse | 2 | baker outfit | own bench | No |
| DynamicSeasons, Spark Lantern Pets, SkyyKeyProbe | 1 each | - | - | No (basket / pet backpack / our probe; cosmetic-only) |
| **Total** | **1,440** | | | |

**No armor items:** [Dray's] Leather+ (a Tanning Table + leather conversions), BetterWardrobes (wardrobe furniture), ZetsMysticWeapons,
Neymeros, Dragonstone, Rogue, Aetherhaven, UltimateBossFight, Skyreach Ravines. *Correction to research/Existing-Mods-Gear-Survey.md:*
PJ-HyperGlowingArmors uses its own `HyperGlowingArmors_*` ids (no vanilla override). The real vanilla-id overriders are EndgameAndQoL,
Skyys-HyMax and TheLostWorlds.

**Cosmetic-only (no stats at all):** 2 jetpacks, the foraging basket, the pet backpack, SkyyKeyProbe's helmet. The Armory has none: every
colour swap carries the stats of its base piece.

### 1.2 The Armory in detail (armor)

Their sets (their "SubCategory"), with our reading of their claims. "Lv" = their ItemLevel. Stats summarised.

| Set | Pieces | Slots (H/C/Ha/L) | Lv | Their tier claim | Stats in short | Recipe |
|---|---|---|---|---|---|---|
| Calvary Set | 179 | 76/51/26/26 | 20 | Iron, heavy sound | = vanilla Iron | 4 base at Armor Bench (iron + medium leather + gold / silver / linen), rest alteration; 4 Ghost pieces no recipe |
| Jester Set | 144 | 90/18/0/36 | 15 | Leather | low (about a third of Iron) | 3 base (light leather + linen + wool) |
| Vanilla Recolor Iron (`Armor_Iron_*_<colour>`) | 97 | 20/28/20/29 | 20 | Iron | = vanilla Iron | alteration of vanilla Iron armor |
| Grand Lich Hood | 68 | 34/34/0/0 | 40 | Adamantite | Adamantite-level + a Mana multiplier | 1 base (void essence + shadoweave + voidheart) |
| Skull Masks | 57 | head | 20 | Iron | Iron head | 1 base (iron + light leather + bone) |
| Priest Set | 56 | 16/24/8/8 | 40 | Adamantite | low defence, +Mana | 4 base (gold + wool + cindercloth) |
| Rook Set | 50 | 20/10/10/10 | 20 | Iron | = Iron | 4 base (iron + light leather + linen); 10 Ghost / Wraith no recipe |
| Elite Rook Set | 46 | 18/9/9/10 | 20 (5 at 50) | Iron | above Iron (about Cobalt level) | Rook piece + ruby |
| Crowns | 41 | head | 20 | Iron | Iron head | 1 base (iron + gold + linen) |
| Cobalt Dragon Set | 40 | 22/14/2/2 | 35 | Cobalt | Cobalt-level + ice resistance | Iron Dragon piece + cobalt + life essence |
| Antique Dragon Set | 37 | 28/7/1/1 | 5 | wood / iron | early | wood + iron + life essence |
| Academy Set | 27 | 9/9/9/0 | 40 | Adamantite | Mana, one piece with elemental resistance | adamantite + wool + light leather |
| Daemon Set | 27 | 18/3/3/3 | 40 | Adamantite | Adamantite-level + fire resistance + Mana | adamantite + fire essence + cindercloth |
| Iron Dragon Set | 23 | 14/7/1/1 | 5 | iron | better than Iron | Antique Dragon piece + iron + life essence |
| Scorpion Helms / Elite | 23 + 21 | head | 40 | Adamantite | poison resistance | adamantite + heavy leather + venom; Elite = upgrade |
| Potion Bandolier | 19 | chest | 25 | Cotton cloth | low + poison resistance | antidote + wool + medium leather |
| Scarecrow | 19 | head | 10 | Copper | low + Mana | from the Scarecrow deco |
| Warden Set | 18 | 9/3/3/3 | 20 | Iron | projectile resistance + Arrow Damage (their own stat) | iron + medium leather + shadoweave |
| Amulets | 8 | 4 head / 4 chest | 20 | Iron | Iron head | iron + green crystal |
| Tribal Masks | 3 | head | 5 | - | negative Health, one element resistance each | wood + fibre + life essence |
| Engineering Rig | 2 | chest | 45 | - | Move Speed + Jump Height (their own stats) | iron + heavy leather + copper + life essence |
| Battlegrounds (Tarnished Crown, Verdant Amulet) | 2 | head / chest | 20 | Iron | Iron | none (Legendary, no recipe) |
| Bramblekin Mask / Bracers, Relentless (quiver) | 3 | | 20-40 | | | Armor Bench |
| Kanohi | 9 | - | - | - | placeable props, not armor | - |

Other things in the jar that matter to us:
- Their **own stats**: `Move_Speed`, `Jump_Height`, `Arrow_Damage_Bonus` (their stats module applies them). Some pieces use
  **multiplicative** Mana / speed modifiers.
- **Alteration Table** (`ArmoryAlteration` bench): swaps a piece for another colour of the same family. It carries the item's metadata
  over (with some keys excluded) and fires the engine's craft events.
- **Loot**: `Server/Drops/TheArmory/Armory_Zone1-4_Loot` + 52 patches into vanilla prefab chest lists (Patchly is bundled in the jar).
- The jar also bundles **telemetry** (alecstelemetry, with a consent step) and a metrics properties file. Worth knowing for a public pack.
- Manifest: no licence field; the licence is on the CurseForge page (CC BY-NC, section 4).

### 1.3 The Armory weapons (282)

| Group | Count | Moveset | Our class | SkyyGear today |
|---|---|---|---|---|
| `Longsword_<Iron / Cobalt>_<colour>` | 20 | Longsword | Warrior | not gear (no `Weapon_` prefix), free for every class |
| `Sword_<metal>_<colour>` | 40 | sword | Warrior | not gear, free |
| `Dagger_<metal>_<colour>` | 40 | daggers | Assassin | not gear, free. Three ids are misspelt (`Throium`, `Throrium`) |
| `Mace_<metal>_<colour>` | 30 | mace | Berserker | not gear, free |
| `Weapon_Battleaxe_<metal>_<colour>` | 40 | battleaxe | Berserker | **gear** (Berserker gate, metal band) |
| `Weapon_Shield_<metal>_<colour / Alt / Pat>` | 85 | shield | free (Warrior lean) | **free shield** (off-hand) |
| Antique Shield + 5 colours | 6 | shield | free (Warrior lean) | not a `Weapon_Shield_` id: no off-hand rule |
| FireWhip, ScorpianFlail | 2 | Club_Flail (Lv 15) | Berserker for now | not gear, free |
| Weapon_Elemental_Flame / Ice / Poison / Gravity | 4 | Longsword (Lv 35) | Warrior (boss drops) | gear (Warrior gate: `Weapon_Elemental_` matches no class rule -> free today) |
| RuneBladeStage1 / 2 / 3 | 3 | club / battleaxe / mace (Lv 40) | Berserker (boss chain) | not gear |
| DualRuneBlade | 1 | daggers (Lv 40) | Assassin (boss drop) | not gear |
| LahatChereb | 1 | Adamantite mace (Lv 40, Legendary) | see 9.2 | not gear |
| Hepta_Axe | 1 | battleaxe (Developer quality, no recipe) | Berserker (boss drop) | not gear |
| Zweihander | 1 | mace template (Lv 40) | **Warrior** (Skyy 2026-10-08) | not gear |
| Weapon_Dualswords_Iron | 1 | daggers template ("Developer" quality) | **Assassin** (Skyy 2026-10-08) - but unfinished, see below | gear (free today) |
| Fist | 1 | sword template (Lv 40) | Monk? (question) | not gear |
| GhostSword | 1 | ghost sword (no recipe) | Warrior special | not gear |
| EmptySign, Love / Hate Kweebec Sign | 3 | mace (Junk) | joke items - leave out | - |
| TestBroom, RookEliteBootsCharred2 | 2 | test / odd | leave out | - |

---

## 2. Classification: Cloth / Light / Heavy

### 2.1 The rule

1. **Look first** (model folder, texture, set theme, their ids): robes, hoods, hats, tunics, bandoliers, crowns / amulets = **Cloth**;
   leather, masks, bracers, scale, rangers, cloaks = **Light**; plate, knights, dragon / demon armor = **Heavy**.
2. **Specs second** (their resistance + Health compared with vanilla at the same slot): about vanilla metal numbers or more = Heavy;
   below that with speed / crit / projectile stats = Light; lowest defence or any +Mana = Cloth. Their sound set (ISS_Armor_Cloth /
   Leather / Heavy) is NOT reliable: The Armory gives Heavy sound to almost everything, robes included.
3. **Tier** = their materials (recipe bars, family tag, metal word in the id), else their ItemLevel mapped onto our ladder.
   Their stats never decide our numbers: SkyyGear sets Health / resistance from the item LEVEL (the armor box is hidden, LOCKED 2026-10-05).

Our ladder (SkyyGear live defaults, `level.material.*`): Crude 1-13, Copper 10-18 (copper armor 1-18), Iron / Bronze 15-23, Thorium
20-28, Cobalt 25-38, Adamantite 35-43, Mithril / Onyxium 40-49. Items above 49 wait for our Lv 50+ content.

### 2.2 Result, recommended pool (1,052 pieces)

| Type | Pieces | Different models | Crude | Copper | Iron | Thorium | Cobalt | Adamantite |
|---|---|---|---|---|---|---|---|---|
| **Heavy** | 499 | 41 | 37 | - | 349 | 46 | 40 | 27 |
| **Cloth** | 278 | 51 | 4 | 23 | 74 | 11 | 60 | 106 |
| **Light** | 275 | 32 | 3 | 144 | 77 | 2 | 4 | 45 |

The Armory alone: Heavy 499 / Light 271 / Cloth 240 (+9 props). All mods scanned: Heavy 751 / Cloth 348 / Light 326 / none 15.

Per-set calls for The Armory (every id is in Appendix A):

| Type | Sets (band) |
|---|---|
| Heavy | Antique Dragon (Crude), Calvary + Rook + Vanilla Recolor Iron (Iron), Iron Dragon (Iron, special), Elite Rook (Thorium, special), Cobalt Dragon (Cobalt, special), Daemon (Adamantite, special) |
| Light | Tribal Masks (Crude), Jester (Copper), Skull Masks + Bramblekin + Warden (Iron; Warden = Archer special), Engineering Rig (Thorium, special), Scorpion + Elite Scorpion helms + Relentless quiver (Adamantite) |
| Cloth | Scarecrow (Copper), Crowns + Amulets + Potion Bandolier + Battlegrounds (Iron), Priest (Cobalt, special), Academy + Grand Lich (Adamantite, special) |

Other recommended mods: SLVR robes = a full Cloth ladder (Wool Crude, Linen Copper, Cotton Iron, Silk Thorium, Raven Cobalt,
Cindercloth Adamantite); Arcane Power = Cloth Thorium (Manathread) + Adamantite (Arcaneweave); Voidcloak = Light Cobalt.

### 2.3 Gaps the pool leaves

- **Mithril / Onyxium (40-49) has almost nothing** outside the "Maybe" dungeon mods. Vanilla Mithril / Onyxium / Prisma cover Heavy there;
  Light and Cloth have nothing at 40-49.
- **Light is thin above Iron** (Thorium 2, Cobalt 4). Our planned Light ladder (black leather + metal, Copper..Onyxium) fills exactly that.
- **Hands and Legs are rare** in The Armory (93 / 129 vs 544 heads). Many Armory "sets" are mostly helmets in many colours.
- The Armory is mostly Lv 15-20 by count (Calvary, Jester, Iron recolours). The drop table must weight by SET, not by piece, or
  everything that drops will be an Iron-band helmet.

---

## 3. How it works with our mods at runtime (no file overrides)

### 3.1 What SkyyGear does today (0.2.10, `SkyyGear/build_skyygear_0.2.10.py`)

- **Gear = id prefix.** `GearData.isGear`: every `Armor_*`, every `Weapon_*` that is not ammo; plus ids matching a `gear.include` prefix
  (Server Setup; at least 6 characters; not bare `Armor_` / `Weapon_` / `Skyy_` / `Tool_`). An included id without those prefixes is
  kind "equipment" unless a `kind.prefix` row says `combat`. `armorItem()` already treats an included id with an engine armor asset as armor.
- **So of The Armory's armor only the 97 `Armor_Iron_*` recolours are gear today** (Iron 15-23 by the word "Iron"). The other 913 armor
  pieces get no rarity, no level, no modifiers, and keep their vanilla box. Of the weapons, the 125 `Weapon_Battleaxe_` / `Weapon_Shield_`
  ids (+ Elemental, Dualswords) are gear; `Sword_` / `Dagger_` / `Mace_` / `Longsword_` (130) and the named specials are not.
- **Level band lookup** (`GearLevel.band`): (1) `level.item.<id>` exact level, (2) the first id word (split on `_`) matching a
  `level.material` row -> that band, (3) the item's own ItemLevel, (4) the default. Armory ids are mostly CamelCase (`CobaltDragonChestPlateBlackGreen`)
  so step 2 misses them and they would fall back to THEIR ItemLevel (an exact level, no band). SLVR / Arcane Power ids do contain cloth words
  (`SLVR_Armor_Cloth_Linen_Chest` -> the Linen row) once they are included.
- **Hidden armor box** (`GearABox.target`): only gear armor of an enforced kind (combat / equipment), Head / Chest / Legs / Hands, with
  ADDITIVE stat modifiers only. Armory pieces with multiplicative Mana / Move_Speed / Jump_Height / Arrow_Damage keep their vanilla box and
  their stats on top of ours. Armor knockback / DamageClassEnhancement lines stay with the engine.
- **Drops today:** `part.drops` tags vanilla gear that drops from mobs as unidentified (`GearDeathMark` + `GearDropSys`); chests tag gear
  added by the stash roll (`GearChestMark` / `GearChestTag`). `gear:fn:unid` (mode 9) makes a stack unidentified (no callers yet).
  The **extra 4% drop per levelled kill, the mystery boxes and the shared item picker are NOT built** (research/Loot-Unid-Spec.md 3.3 + the
  2026-10-06 revision; queued as the loot round). Its picker already plans `loot.include` + a `gear:loot:add:<Mod>` bridge for other mods'
  ids - that is the hook for pack armor.
- **Set rarity exists, set bonuses do not.** The rarity ladder has "Set" (green); the document has a reserved `set` field; no bonus code.
- **SkyyMobs 0.1.4**: `mob:fn:level` (mob level) and `mob:fn:info`. Bosses (Goblin_Duke, Trork_Chieftain, Dragon_*, Skeleton_Elite) are
  excluded from levels until the boss stage (`scale.role` table is ready but empty). No elites yet.
- **SkyyClasses 0.1.14** gates weapons by **hard-coded id prefixes** (`RULES`); an id no rule matches is FREE for all classes.

### 3.2 What we add (our code only)

1. **One pack-armor table** (new data file in SkyyGear, editable in Server Setup like the level rows), one line per id or per id prefix:
   `armor.pack.<id>=<Cloth|Light|Heavy>,<band min>,<band max>,<drop group>,<set id or ->`. Built from Appendix A at build time from the
   ids only (the build reads the installed jar's id list to check the ids exist; nothing of theirs is written into our jar).
   It plugs into:
   - `isGear` (an id in the table = gear armor, kind combat - no need for 6-char include prefixes),
   - `GearLevel.band` (step 0: the table band beats the ItemLevel fallback),
   - the ARMOR TYPES build (Heavy slower / more Defense + HP; Light faster + attack speed / crit chance; Cloth Health + Mana + speed, least
     Defense - LOCKED 2026-10-05): vanilla ids get their type from the family word, pack ids from this table,
   - the loot picker (`loot.include` source + drop group), and the set-bonus system (set id).
2. **Mob drops** (the loot round): on each levelled kill the extra roll (4%, LOCKED) picks armor half the time (`loot.armorShare`).
   With the pack table, the armor candidates at mob level L = every table id whose band holds L, **grouped by set first** (pick a set by
   weight, then a piece), plus the vanilla candidates. Zone lean: a `drop group` (e.g. `undead`, `trork`, `desert`, `knight`) can be
   weighted up by mob role prefix (Skeleton_* -> undead: Skull Masks, Grand Lich, Rook Ghost / Wraith; Trork_* -> tribal / scarecrow ...).
   The drop is a mystery item (Wynn style); WHICH Armory piece it becomes is decided at identify (2026-10-06 lock).
3. **Special sets**: full named sets as rarer drops. Each special set = a set id in the table, a source (boss role / elite / dungeon chest),
   a drop chance per kill, and a set bonus (2 / 4 pieces) applied by SkyyGear's existing stat path (lock modifiers + the armor pass), the
   same way it applies rolled modifiers. Rarity "Set" for those pieces. Suggested first five (one per type mix, each with all 4 slots):
   Calvary (Heavy, Iron, Goblin_Duke), Warden (Light, Iron, Archer, Trork_Chieftain), Priest (Cloth, Cobalt, Priest), Cobalt Dragon
   (Heavy, Cobalt, Dragon_Frost), Academy (Cloth, Adamantite, Mage). Ghost / Wraith Rook and Ghost Calvary (no recipe in their mod) are
   natural "ghost" boss / night drops.
4. **Their own chest loot** (Armory zone lists in prefab chests): leave it. SkyyGear tags chest gear as unidentified only when it is gear,
   so once the table makes the ids gear, those chest pieces become unidentified too (no change to their files).

### 3.3 Weapons (Skyy's 2026-10-08 additions)

- **(a) Longswords -> Warrior, flails / whips -> Berserker.** SkyyClasses gates by hard-coded prefixes, so add a small editable
  **class weapon table** (new SkyyClasses row, like `kind.prefix`): `class.weapons.<id prefix>=<Class>`. Entries:
  `Longsword_=Warrior`, `Sword_=Warrior`, `Dagger_=Assassin`, `Mace_=Berserker`, `FireWhip=Berserker`, `ScorpianFlail=Berserker`,
  `Weapon_Elemental_=Warrior` ... Flails / whips get ONE entry each (a "flails" group), so when the future flail / whip class arrives only
  that row changes - nothing hard-coded. SkyyGear needs the same ids as gear: `gear.include` rows (`Longsword_`, `Dagger_`, ... all 6+
  characters) + `kind.prefix ...=combat`, or the same pack table with a weapon section. Levels: the metal word is in these ids
  (`Sword_Iron_Black` -> Iron), except the misspelt Thorium daggers (give them `level.item` rows).
- **(b) Specials = boss drops** (rare, "Set"-like Legendary rarity; drop-only; their recipes stay unless the author agrees):

| Special | Class (by moveset) | Suggested source |
|---|---|---|
| Weapon_Elemental_Flame | Warrior | Dragon_Fire |
| Weapon_Elemental_Ice | Warrior | Dragon_Frost |
| Weapon_Elemental_Poison | Warrior | Scarak_Broodmother |
| Weapon_Elemental_Gravity | Warrior | Golem_Guardian_Void |
| RuneBladeStage1 -> 2 -> 3 | Berserker (club -> battleaxe -> mace) | Stage 1 Skeleton_Elite (0.7); stages 2 / 3 = upgrade at our bench with a boss core (later) |
| Hepta_Axe | Berserker | Trork_Chieftain |
| LahatChereb | Berserker by moveset (mace) - or Warrior if Skyy wants it as a holy sword | Goblin_Duke |
| DualRuneBlade | Assassin | Yeti (or a night elite) |
| GhostSword | Warrior | ghost / undead elite at night |
| Zweihander | Warrior (Skyy) | Golem_Firesteel |
| Weapon_Dualswords_Iron | Assassin (Skyy) | none yet - unfinished item (below) |

- **(c) Fairness - weapon ids per class** (prefix count; vanilla counts include a few unobtainable / test ids):

| Class | Vanilla | Ours (SkyyArmory) + Crossbow Tiers | The Armory recolours | Armory specials | Total | Add our own specials? |
|---|---|---|---|---|---|---|
| Warrior | 58 | 0 | 60 (swords + longswords) | 6 (4 Elemental + Ghost + Zweihander) | 124 | no |
| Berserker | 62 | 0 | 70 (battleaxes + maces) | 6 (Rune Blade x3, Hepta, Lahat, + 2 flails / whips) | 140 | no (flails move to the future class) |
| Assassin | 17 | 8 kunai | 40 daggers | 1 (Dual Rune Blade; + dual swords once finished) | 66 | yes, 3 |
| Mage | 29 | 15 staffs / spellbooks | 0 | 0 | 44 | yes, 4 |
| Archer | 21 | 2 + 4 crossbows | 0 | 0 | 27 | yes, 4 (+ Warden set already) |
| Priest | 6 | 7 wands | 0 | 0 | 13 | yes, 4 |
| Monk | 2 | 21 bo / fists | 0 | 0-1 (Fist?) | 23-24 | yes, 3 |
| Shields (all) | vanilla shields | - | 91 | - | - | Warrior lean in the drop picker |

  "Count" here = ids, mostly colours. The fair measure is **different weapons a player can chase**: specials per class. Target: every class
  ends with **4-6 boss specials**. Warrior has 6, Berserker 5 (+2 flails until the new class). Our own specials to make: Mage 4,
  Priest 4, Archer 4, Monk 3-4, Assassin 3. Recolour drops do not count toward fairness (variety only).
- **(d) Recolours as random mob-drop variety:** swords / longswords / daggers / maces / battleaxes / shields of a metal join the drop picker
  at that metal's band (the same picker as armor; the class lean already planned in Loot-Unid-Spec 3.3 applies). Shields: free for all,
  weighted towards Warrior kills in the lean.
- **(e) Dual swords + Zweihander** - Skyy 2026-10-08: "zweihander for warrior, dual swords for assassin."
  Class table rows: `Zweihander=Warrior`, `Weapon_Dualswords_=Assassin`, `DualRuneBlade=Assassin`.
  **The dual swords item is NOT finished (checked in the jar):** "Developer" quality; no model or texture of its own - it points at the
  VANILLA Iron Sword model, texture and icon and even uses the vanilla Iron Sword's name ("Iron Sword"); it runs on the vanilla daggers
  moveset (one sword model in the hand, so it will not look dual-wielded); its recipe has a bench TYPE but no bench id (likely uncraftable);
  it is in none of their loot lists and has no translation of its own. So: keep it out of drops for now, ask LadyPaladra whether it is
  planned, and treat Dual Rune Blade (finished, Epic, Weapon Bench) as the Assassin's Armory special. If Skyy wants real dual swords soon,
  that is one of OUR Assassin specials (SkyyArmory, our own art).

---

## 4. What needs the author (LadyPaladra) - and the others

**Licence (CurseForge page FAQ, checked 2026-10-08, recorded in PACK.md):** The Armory is **Creative Commons Attribution-NonCommercial**.
Modpack use is allowed if we **credit The Armory** and do **not sell it**. The page itself points to ItemForge for changing its stats /
recipes, so stat and recipe changes are expected. (The jar's manifest has no licence field - the page is the source.)

So:
- **Credit:** a line for The Armory (LadyPaladra, link to the CurseForge page) in PACK.md and in our pack credits page. Needed - not optional.
- **No selling:** only monetisation needs LadyPaladra's OK. If the SkyWynn server ever sells anything that gives or unlocks Armory items
  (ranks with gear, paid crates, a paid pack), ask first. Plain play on a free server is fine.
- **Recipes / benches / stats:** the licence allows changing them. The Armory has **no config file or setting** for it
  (`AlterationConfig`, `ScribingConfig`, `ParrySettings` are constants compiled into the jar), so a change means an override of their
  recipe / item files - the ItemForge way. Our own rule still applies: **never copy their files into our public repo**. If Skyy wants
  drop-only Armory pieces, the safe path is an override written by us at build time from the ids (only the changed fields, nothing of
  theirs committed), generated into a jar we do not commit - a main-session decision because PROJECT-RULES 2 ("never ship a file
  overriding their item ids") would need a licence exception line for CC-BY-NC mods. Until then: runtime only (sections 2-3).
- **Their chest loot lists** (zone loot + prefab patches): same - allowed to change, but leaving them on costs nothing.

Still worth one friendly message to LadyPaladra (not required by the licence):
- Tell them SkyWynn lists The Armory with credit (players install it from CurseForge; we never re-upload it).
- Ask whether **item ids are stable** between versions (we key everything on ids) and whether they could announce renames.
- Ask whether a **config switch** for "no Armor / Weapon Bench recipes" and "no chest loot" is planned (would save us an override).
- Ask whether the Alteration Table is meant to carry other mods' item metadata (our rarity / level document) and whether `Weapon_Dualswords_Iron`
  is planned (it is unfinished, 3.3 e).
- Optional: how a server owner turns its telemetry off, so we can document it.

Other mods (SlverSkull's SLVR robes, Tayko's Arcane Power, Vortex's Voidcloak): their licences are not checked yet - read each page's
licence / FAQ before listing them; if none is stated, ask before listing. If an author says no or does not answer: leave that mod out.

---

## 5. Plan

### 5.1 Phases (round sizes per PROJECT-RULES 4)

| Phase | What | Mods | Round |
|---|---|---|---|
| P0 | Switch The Armory on in the world (PACK_THIRD_PARTY + PACK.md row), play one session, read logs. Check: load errors, its telemetry prompt, conflicts with SkyyGear / SkyyClasses, the Alteration Table on a SkyyGear-rolled `Armor_Iron_*` piece | deploy_set.py, PACK.md | no agents (config) + Skyy test |
| P1 | Credit line (PACK.md + credits page); friendly note to LadyPaladra; check SLVR / Arcane Power / Voidcloak licences | PACK.md | no agents |
| P2 | Pack id table + ARMOR TYPES: SkyyGear reads the table (gear, kind, band, type); Heavy / Light / Cloth stats for vanilla + pack ids | SkyyGear | **Full round** (new system, saved data per stack) - fold into the planned ARMOR TYPES round |
| P3 | Weapons: SkyyClasses class weapon table (flails one movable entry) + SkyyGear include / kind / level rows for the Armory weapons | SkyyClasses + SkyyGear | Full round (permissions-like gate, several mods) |
| P4 | Loot round with pack ids: extra 4% drop, mystery boxes, picker by set + band + drop group, recolour weapons | SkyyGear (+ SkyyMobs role lean) | **Ultracode** (loot, dupes, several mods) - the already-queued loot round |
| P5 | Special sets + set bonuses + boss specials (needs SkyyMobs bosses / elites) | SkyyGear + SkyyMobs | Ultracode |
| P6 | Our own specials for Mage / Priest / Archer / Monk / Assassin (fairness) | SkyyArmory | Full rounds, art proof first |

### 5.2 Risks

- **Their ids change between versions** (they already have typos like `Throium`). Mitigation: the table loader skips unknown ids with one
  WARN each; a build check lists missing / new ids against the installed jar; unidentified boxes store the real id only at identify.
  An owned piece whose id vanished becomes an unknown item - same as any removed mod.
- **Hytale 0.7 (2026-10-12)** may break The Armory (custom plugin code, Patchly patches, their stats module) before LadyPaladra updates.
  Do P0 on 0.6, but hold P2+ until The Armory loads cleanly on 0.7.
- **Players / servers without the mod**: every lookup is "id exists in the live item map" - no Armory = no Armory drops, nothing breaks.
- **Alteration Table = re-roll / XP farm?** It fires craft events. If SkyyGear treats the output as a fresh craft, a player could re-roll
  rarity or farm Smithing XP by swapping colours back and forth. If the metadata carries over, a rolled piece just changes colour (good).
  UNVERIFIED - test in P0; if needed SkyyGear skips craft rolls / XP for `ArmoryAlteration` recipes.
- **Double stats**: pieces with multiplicative or custom stats (Mana x, Move_Speed, Jump_Height, Arrow_Damage_Bonus) keep their own box and
  apply on top of SkyyGear's levelled stats. Decide per piece: accept, or exclude them from drops.
- **Helmet flood**: 544 heads vs 93 hands. Weight by set, not by piece.
- **Their crafting stays** until we decide on an override (section 4): Armory base pieces stay craftable at the Armor Bench (crafted at your level by
  SkyyGear once they are gear). Drops are then "more variety", not the only source.
- **IP-themed mods** (LOTR, Marvel, Star Wars, Zelda, Mega Man) are left out by default for a public server pack.
- **Vanilla-id overriders** (EndgameAndQoL, Skyys-HyMax, TheLostWorlds) must stay off next to our armor types.

---

## 6. Questions for Skyy (each with a recommended default)

1. **Which mods?** [The Armory + SLVR Robes + Arcane Power + Voidcloak. Maybe later: HyperGlowing (not the 2x), TerrariaToolsWeapons.
   Leave dungeon mods' armor as their own dungeon rewards. No IP-themed mods.]
2. **Their crafting:** keep it or drops only? [Keep it for now. The licence allows a recipe override later (section 4), but that needs a
   PROJECT-RULES exception for CC BY-NC mods first.]
3. **Monetisation:** will SkyWynn ever sell ranks / crates / packs? [No paid access to Armory items; ask LadyPaladra before any.]
4. **Drop rate:** [keep the LOCKED 4% extra roll per levelled kill, armor half of it; pack pieces share the armor half with vanilla, picked
   by set. Special sets 1 in 50 per boss kill to start.]
5. **How many special sets first?** [5: Calvary, Warden, Priest, Cobalt Dragon, Academy - with 2-piece / 4-piece bonuses.]
6. **Colour variants:** drop any colour at random, or only the base colour (and the Alteration Table for the rest)? [random colour = more
   variety, matches "tons of variety".]
7. **Crowns / amulets / bandoliers count as Cloth?** [yes - they get no class bonus for Heavy / Light wearers.]
8. **Our own armor plans** (Heavy Leather, Crude Robe, the Light black-leather ladder, the art agent's Dark Leather design): [keep the TIER 1
   pieces (Heavy Leather, Crude Robe) and the Light metal ladder (Light has almost nothing above Iron in the pack mods); pause the extra
   designs (Dark Leather candidate, mining / foraging armor art) until the pack armor is in.]
9. **Lv 40-49 Light / Cloth gap:** [our Light ladder + vanilla Silk / Cindercloth cover it; no new mods for it.]
10. **Multiplicative-stat pieces** (Grand Lich, Academy, Engineering Rig, Warden arrow bonus): [allow them as special-set pieces only.]
11. **Lahat Chereb:** [Berserker (mace moveset) - say if it should be a Warrior holy sword.]
12. **Fist (Armory):** [Monk, boss drop - it uses a sword template, so check it in game first.]
13. **Flails / whips:** [Berserker now, one table row each so the future flail class can take them.]

---

## Appendix A - armor ids + our classification (ids only, no copied data)

Columns: Set (their set name, or the id without its slot word), Type, Band (our ladder), Use (Drop = random drops, Special = special set /
rarer drop, Yes = mod recommended, Maybe / No = see 1.1), Ids.

### 0.6.1_Aures_Rare_Monsters_28_08_2026.zip (6)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Aures_Armor_Gold_Horns | Heavy | Adamantite | Maybe | Aures_Armor_Gold_Horns_Head |
| Aures_Armor_Gold_Horns_No_Skull | Heavy | Adamantite | Maybe | Aures_Armor_Gold_Horns_Head_No_Skull |
| Aures_Armor_Gold_Horns_Small | Heavy | Adamantite | Maybe | Aures_Armor_Gold_Horns_Head_Small |
| Aures_Armor_Silver_Horns | Heavy | Adamantite | Maybe | Aures_Armor_Silver_Horns_Head |
| Aures_Armor_Silver_Horns_No_Skull | Heavy | Adamantite | Maybe | Aures_Armor_Silver_Horns_Head_No_Skull |
| Aures_Armor_Silver_Horns_Small | Heavy | Adamantite | Maybe | Aures_Armor_Silver_Horns_Head_Small |

### 1.0.2 Multilanguage Spark Lantern Pets.zip (1)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Wearable_Backpack_Copper_Small_Pet | - | - | No | Wearable_Backpack_Copper_Small_Pet |

### Arcane_Power_V3.1.1.zip (14)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| ArcanePower_Armor_Cloth_Arcaneweave | Cloth | Adamantite | Yes | ArcanePower_Armor_Cloth_Arcaneweave_Chest, ArcanePower_Armor_Cloth_Arcaneweave_Hands, ArcanePower_Armor_Cloth_Arcaneweave_Head, ArcanePower_Armor_Cloth_Arcaneweave_Legs |
| ArcanePower_Armor_Cloth_Arcaneweave_Breathing | Cloth | Adamantite | Yes | ArcanePower_Armor_Cloth_Arcaneweave_Head_Breathing |
| ArcanePower_Armor_Cloth_Arcaneweave_Glow | Cloth | Adamantite | Yes | ArcanePower_Armor_Cloth_Arcaneweave_Head_Glow |
| ArcanePower_Armor_Cloth_Arcaneweave_Speed | Cloth | Adamantite | Yes | ArcanePower_Armor_Cloth_Arcaneweave_Legs_Speed |
| ArcanePower_Armor_Cloth_Manathread | Cloth | Thorium | Yes | ArcanePower_Armor_Cloth_Manathread_Chest, ArcanePower_Armor_Cloth_Manathread_Hands, ArcanePower_Armor_Cloth_Manathread_Head, ArcanePower_Armor_Cloth_Manathread_Legs |
| ArcanePower_Armor_Cloth_Manathread_Breathing | Cloth | Thorium | Yes | ArcanePower_Armor_Cloth_Manathread_Head_Breathing |
| ArcanePower_Armor_Cloth_Manathread_Glow | Cloth | Thorium | Yes | ArcanePower_Armor_Cloth_Manathread_Head_Glow |
| ArcanePower_Armor_Cloth_Manathread_Speed | Cloth | Thorium | Yes | ArcanePower_Armor_Cloth_Manathread_Legs_Speed |

### ArmCannons-v0.6.2.zip (4)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Xover_MMBNAqua | Heavy | Cobalt | No | Armor_Xover_MMBNAqua |
| Armor_Xover_MMBNElec | Heavy | Cobalt | No | Armor_Xover_MMBNElec |
| Armor_Xover_MMBNFire | Heavy | Cobalt | No | Armor_Xover_MMBNFire |
| Armor_Xover_MMBNWood | Heavy | Cobalt | No | Armor_Xover_MMBNWood |

### Below-Every-Heaven-1.5.1.jar (4)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Holloway | Heavy | 50+ | No | Armor_Holloway_Chest, Armor_Holloway_Hands, Armor_Holloway_Head, Armor_Holloway_Legs |

### CD_Tritale_Pack_1.0.4.zip (32)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Tritale_Blue_Tunic | Light | Iron | No | Tritale_Blue_Tunic_Chest, Tritale_Blue_Tunic_Hands, Tritale_Blue_Tunic_Head, Tritale_Blue_Tunic_Legs |
| Tritale_Blue_Tunic_Gold | Light | Iron | No | Tritale_Blue_Tunic_Hands_Gold, Tritale_Blue_Tunic_Legs_Gold |
| Tritale_Blue_Tunic_Silver | Light | Iron | No | Tritale_Blue_Tunic_Hands_Silver, Tritale_Blue_Tunic_Legs_Silver |
| Tritale_Green_Tunic | Light | Iron | No | Tritale_Green_Tunic_Chest, Tritale_Green_Tunic_Hands, Tritale_Green_Tunic_Head, Tritale_Green_Tunic_Legs |
| Tritale_Green_Tunic_Gold | Light | Iron | No | Tritale_Green_Tunic_Hands_Gold, Tritale_Green_Tunic_Legs_Gold |
| Tritale_Green_Tunic_Silver | Light | Iron | No | Tritale_Green_Tunic_Hands_Silver, Tritale_Green_Tunic_Legs_Silver |
| Tritale_Purple_Tunic | Light | Iron | No | Tritale_Purple_Tunic_Chest, Tritale_Purple_Tunic_Hands, Tritale_Purple_Tunic_Head, Tritale_Purple_Tunic_Legs |
| Tritale_Purple_Tunic_Gold | Light | Iron | No | Tritale_Purple_Tunic_Hands_Gold, Tritale_Purple_Tunic_Legs_Gold |
| Tritale_Purple_Tunic_Silver | Light | Iron | No | Tritale_Purple_Tunic_Hands_Silver, Tritale_Purple_Tunic_Legs_Silver |
| Tritale_Red_Tunic | Light | Iron | No | Tritale_Red_Tunic_Chest, Tritale_Red_Tunic_Hands, Tritale_Red_Tunic_Head, Tritale_Red_Tunic_Legs |
| Tritale_Red_Tunic_Gold | Light | Iron | No | Tritale_Red_Tunic_Hands_Gold, Tritale_Red_Tunic_Legs_Gold |
| Tritale_Red_Tunic_Silver | Light | Iron | No | Tritale_Red_Tunic_Hands_Silver, Tritale_Red_Tunic_Legs_Silver |

### Captain America Suit 1.2.1 by Kleinstadtfrettchen Update 6.zip (8)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Anti_Cap | Heavy | Mithril | No | Anti_Cap_Chest, Anti_Cap_Gloves, Anti_Cap_Head, Anti_Cap_Legs |
| Cap | Heavy | Mithril | No | Cap_Chest, Cap_Gloves, Cap_Head, Cap_Legs |

### DynamicSeasons-6.1.3.jar (1)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Foraging_Basket | - | - | No | Foraging_Basket |

### EndgameAndQoL5.4.2.jar (20)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Adamantite | Heavy | Mithril | No | Armor_Adamantite_Chest, Armor_Adamantite_Hands, Armor_Adamantite_Head, Armor_Adamantite_Legs |
| Armor_Diving_Crude | Heavy | Mithril | No | Armor_Diving_Crude_Chest, Armor_Diving_Crude_Hands, Armor_Diving_Crude_Head, Armor_Diving_Crude_Legs |
| Armor_Mithril | Heavy | Mithril | No | Armor_Mithril_Chest, Armor_Mithril_Hands, Armor_Mithril_Head, Armor_Mithril_Legs |
| Armor_Onyxium | Heavy | Mithril | No | Armor_Onyxium_Chest, Armor_Onyxium_Hands, Armor_Onyxium_Head, Armor_Onyxium_Legs |
| Armor_Prisma | Heavy | Mithril | No | Armor_Prisma_Chest, Armor_Prisma_Hands, Armor_Prisma_Head, Armor_Prisma_Legs |

### Hylamity-0.2.0.jar (4)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Wulfrum | Heavy | Thorium | Maybe | Armor_Wulfrum_Chest, Armor_Wulfrum_Hands, Armor_Wulfrum_Head, Armor_Wulfrum_Legs |

### Jetpacks-1.5.0.jar (3)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Infinity_Jetpack | - | - | No | Infinity_Jetpack |
| Rusty_Jetpack | - | - | No | Rusty_Jetpack |
| Uranium_Jetpack | - | - | No | Uranium_Jetpack |

### LOTR_Project_1.17.1_.zip (37)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Gondor_Islidur | Heavy | Adamantite | No | Armor_Gondor_Islidur_Chest, Armor_Gondor_Islidur_Hands, Armor_Gondor_Islidur_Head, Armor_Gondor_Islidur_Legs |
| Armor_Sauron | Heavy | Adamantite | No | Armor_Sauron_Chest, Armor_Sauron_Hands, Armor_Sauron_Head, Armor_Sauron_Legs |
| Armor_Cloth_Nazgul | Cloth | Mithril | No | Armor_Cloth_Nazgul_Chest, Armor_Cloth_Nazgul_Hands, Armor_Cloth_Nazgul_Head, Armor_Cloth_Nazgul_Legs |
| Armor_Nazgul_King | Cloth | Mithril | No | Armor_Nazgul_King_Head |
| Armor_Dwarven_Royal | Heavy | Cobalt | No | Armor_Dwarven_Royal_Chest, Armor_Dwarven_Royal_Hands, Armor_Dwarven_Royal_Head, Armor_Dwarven_Royal_Legs |
| Armor_Elven | Heavy | Cobalt | No | Armor_Elven_Chest, Armor_Elven_Hands, Armor_Elven_Head, Armor_Elven_Legs |
| Armor_Dwarven | Heavy | Iron | No | Armor_Dwarven_Chest, Armor_Dwarven_Hands, Armor_Dwarven_Head, Armor_Dwarven_Legs |
| Armor_Gondor | Heavy | Iron | No | Armor_Gondor_Chest, Armor_Gondor_Hands, Armor_Gondor_Head, Armor_Gondor_Legs |
| Armor_Orc | Heavy | Iron | No | Armor_Orc_Head |
| Armor_Orc_Mordor | Heavy | Iron | No | Armor_Orc_Head_Mordor |
| Armor_Rohan | Heavy | Iron | No | Armor_Rohan_Chest, Armor_Rohan_Hands, Armor_Rohan_Head, Armor_Rohan_Legs |
| Armor_Uruk | Heavy | Iron | No | Armor_Uruk_Chest, Armor_Uruk_Head |

### Lunaronin777.Fullmetal_Labyrinth.1.10.8.zip (8)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Fullmetal_Legion | Heavy | Thorium | Maybe | Armor_Fullmetal_Chest_Legion, Armor_Fullmetal_Hands_Legion, Armor_Fullmetal_Head_Legion, Armor_Fullmetal_Legs_Legion |
| Armor_Fullmetal_Legion_Upgrade | Heavy | Mithril | Maybe | Armor_Fullmetal_Chest_Legion_Upgrade, Armor_Fullmetal_Hands_Legion_Upgrade, Armor_Fullmetal_Head_Legion_Upgrade, Armor_Fullmetal_Legs_Legion_Upgrade |

### MMOSkillTree-1.6.2.jar (22)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Cape_Master | Cloth | 50+ | No | Cape_Master |
| Cape_Skill_Acrobatics | Cloth | 50+ | No | Cape_Skill_Acrobatics |
| Cape_Skill_Archery | Cloth | 50+ | No | Cape_Skill_Archery |
| Cape_Skill_Artillery | Cloth | 50+ | No | Cape_Skill_Artillery |
| Cape_Skill_Axes | Cloth | 50+ | No | Cape_Skill_Axes |
| Cape_Skill_Blunt | Cloth | 50+ | No | Cape_Skill_Blunt |
| Cape_Skill_Building | Cloth | 50+ | No | Cape_Skill_Building |
| Cape_Skill_Crafting | Cloth | 50+ | No | Cape_Skill_Crafting |
| Cape_Skill_Daggers | Cloth | 50+ | No | Cape_Skill_Daggers |
| Cape_Skill_Defense | Cloth | 50+ | No | Cape_Skill_Defense |
| Cape_Skill_Excavation | Cloth | 50+ | No | Cape_Skill_Excavation |
| Cape_Skill_Fishing | Cloth | 50+ | No | Cape_Skill_Fishing |
| Cape_Skill_Harvesting | Cloth | 50+ | No | Cape_Skill_Harvesting |
| Cape_Skill_Magic | Cloth | 50+ | No | Cape_Skill_Magic |
| Cape_Skill_Mining | Cloth | 50+ | No | Cape_Skill_Mining |
| Cape_Skill_Polearms | Cloth | 50+ | No | Cape_Skill_Polearms |
| Cape_Skill_Staves | Cloth | 50+ | No | Cape_Skill_Staves |
| Cape_Skill_Swords | Cloth | 50+ | No | Cape_Skill_Swords |
| Cape_Skill_Unarmed | Cloth | 50+ | No | Cape_Skill_Unarmed |
| Cape_Skill_Woodcutting | Cloth | 50+ | No | Cape_Skill_Woodcutting |
| Mmo_Keepers_Hood | Cloth | 50+ | No | Mmo_Keepers_Hood |
| Mmo_Keepers_Robe | Cloth | 50+ | No | Mmo_Keepers_Robe |

### MajorDungeons-0.4.13.jar (18)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Cloth_Cultist | Cloth | Mithril | Maybe | Armor_Cloth_Cultist_Chest, Armor_Cloth_Cultist_Hands, Armor_Cloth_Cultist_Head, Armor_Cloth_Cultist_Legs |
| Armor_Cloth_Cultist_Superior | Cloth | Mithril | Maybe | Armor_Cloth_Cultist_Hands_Superior |
| Armor_DarkSilver | Heavy | Mithril | Maybe | Armor_DarkSilver_Chest, Armor_DarkSilver_Hands, Armor_DarkSilver_Head, Armor_DarkSilver_Legs |
| Armor_DarkSilver_ChestCape | Heavy | Mithril | Maybe | Armor_DarkSilver_ChestCape |
| Armor_DarkSilver_Charged | Heavy | Mithril | Maybe | Armor_DarkSilver_Charged_Chest, Armor_DarkSilver_Charged_Hands, Armor_DarkSilver_Charged_Head, Armor_DarkSilver_Charged_Legs |
| Armor_DarkSilver_Charged_ChestCape | Heavy | Mithril | Maybe | Armor_DarkSilver_Charged_ChestCape |
| Armor_DyingStar | Heavy | Mithril | Maybe | Armor_DyingStar_Hands |
| Armor_FallenKnight_ChestWings | Heavy | Mithril | Maybe | Armor_FallenKnight_ChestWings |
| Armor_Cloth_NightAssasin | Light | Mithril | Maybe | Armor_Cloth_NightAssasin_Head |

### Marsi_Dungeon-0.4.0.zip (12)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Dungeon_Hunter | Light | Adamantite | Maybe | Dungeon_Hunter_Helmet |
| Dungeon_Mimic | Light | Adamantite | Maybe | Dungeon_Mimic_Helmet |
| Dungeon_Mimic_Backup | Light | Adamantite | Maybe | Dungeon_Mimic_Helmet_Backup |
| Dungeon_Statue_Armor | Heavy | Adamantite | Maybe | Dungeon_Statue_Armor_Chest, Dungeon_Statue_Armor_Hands, Dungeon_Statue_Armor_Head, Dungeon_Statue_Armor_Legs |
| Dungeon_Statue_Armor_Boss | Heavy | Adamantite | Maybe | Dungeon_Statue_Armor_Head_Boss |
| Dungeon_Dormant | Heavy | Mithril | Maybe | Dungeon_Dormant_Chest, Dungeon_Dormant_Hands, Dungeon_Dormant_Head, Dungeon_Dormant_Legs |

### Mermaids-4.0.1.jar (11)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Mermaids_Black_Seashell_Bra | Cloth | Copper | No | Mermaids_Black_Seashell_Bra |
| Mermaids_Blue_Seashell_Bra | Cloth | Copper | No | Mermaids_Blue_Seashell_Bra |
| Mermaids_Cyan_Seashell_Bra | Cloth | Copper | No | Mermaids_Cyan_Seashell_Bra |
| Mermaids_Gray_Seashell_Bra | Cloth | Copper | No | Mermaids_Gray_Seashell_Bra |
| Mermaids_Green_Seashell_Bra | Cloth | Copper | No | Mermaids_Green_Seashell_Bra |
| Mermaids_Light_Blue_Seashell_Bra | Cloth | Copper | No | Mermaids_Light_Blue_Seashell_Bra |
| Mermaids_Pink_Seashell_Bra | Cloth | Copper | No | Mermaids_Pink_Seashell_Bra |
| Mermaids_Purple_Seashell_Bra | Cloth | Copper | No | Mermaids_Purple_Seashell_Bra |
| Mermaids_Rose_Seashell_Bra | Cloth | Copper | No | Mermaids_Rose_Seashell_Bra |
| Mermaids_Seashell_Bra | Cloth | Copper | No | Mermaids_Seashell_Bra |
| Mermaids_Sirens_Prisma_Seashell_Bra | Cloth | Copper | No | Mermaids_Sirens_Prisma_Seashell_Bra |

### MoreBoots-0.0.3.jar (5)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Froggy | Light | Iron | Maybe | Froggy_Boots |
| Frost | Light | Iron | Maybe | Frost_Boots |
| Magma | Light | Iron | Maybe | Magma_Boots |
| Mega_Speed | Light | Iron | Maybe | Mega_Speed_Boots |
| Void | Light | Iron | Maybe | Void_Boots |

### Mort's Wandering Merchant1.2.3.7hotfix.zip (3)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Rattan | Cloth | Iron | No | Armor_Rattan_Head |
| Armor_WinterHat | Cloth | Iron | No | Armor_WinterHat_Head |
| Armor_WinterHat_Bugmen | Cloth | Iron | No | Armor_WinterHat_Head_Bugmen |

### NecromancerSpire-0.2.0.jar (1)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Necrotic_Crown | Cloth | Mithril | Maybe | Necrotic_Crown |

### NoCube_Bakehouse_0.1.0.zip (2)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| NoCube_Armor_Bakers | Cloth | Copper | No | NoCube_Armor_Bakers_Chest, NoCube_Armor_Bakers_Head |

### Oasis' More to Exlpore.zip (4)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Bramblekin | Light | Copper | No | Armor_Bramblekin_Chest, Armor_Bramblekin_Hands, Armor_Bramblekin_Head |
| Armour_Bramblekin_Horns | Light | Copper | No | Armour_Bramblekin_Horns |

### PJ-ForgottenCreatures-1.3.1.zip (3)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Bramblekin | Light | Copper | No | Armor_Bramblekin_Chest, Armor_Bramblekin_Hands, Armor_Bramblekin_Head |

### PJ-HyperGlowingArmors-1.1.9.zip (64)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| HyperGlowingArmors_Adamantite | Heavy | by metal | Maybe | HyperGlowingArmors_Adamantite_Chest, HyperGlowingArmors_Adamantite_Hands, HyperGlowingArmors_Adamantite_Head, HyperGlowingArmors_Adamantite_Legs |
| HyperGlowingArmors_Adamantite_2x | Heavy | by metal | No | HyperGlowingArmors_Adamantite_Chest_2x, HyperGlowingArmors_Adamantite_Hands_2x, HyperGlowingArmors_Adamantite_Head_2x, HyperGlowingArmors_Adamantite_Legs_2x |
| HyperGlowingArmors_Cobalt | Heavy | by metal | Maybe | HyperGlowingArmors_Cobalt_Chest, HyperGlowingArmors_Cobalt_Hands, HyperGlowingArmors_Cobalt_Head, HyperGlowingArmors_Cobalt_Legs |
| HyperGlowingArmors_Cobalt_2x | Heavy | by metal | No | HyperGlowingArmors_Cobalt_Chest_2x, HyperGlowingArmors_Cobalt_Hands_2x, HyperGlowingArmors_Cobalt_Head_2x, HyperGlowingArmors_Cobalt_Legs_2x |
| HyperGlowingArmors_Copper | Heavy | by metal | Maybe | HyperGlowingArmors_Copper_Chest, HyperGlowingArmors_Copper_Hands, HyperGlowingArmors_Copper_Head, HyperGlowingArmors_Copper_Legs |
| HyperGlowingArmors_Copper_2x | Heavy | by metal | No | HyperGlowingArmors_Copper_Chest_2x, HyperGlowingArmors_Copper_Hands_2x, HyperGlowingArmors_Copper_Head_2x, HyperGlowingArmors_Copper_Legs_2x |
| HyperGlowingArmors_Iron | Heavy | by metal | Maybe | HyperGlowingArmors_Iron_Chest, HyperGlowingArmors_Iron_Hands, HyperGlowingArmors_Iron_Head, HyperGlowingArmors_Iron_Legs |
| HyperGlowingArmors_Iron_2x | Heavy | by metal | No | HyperGlowingArmors_Iron_Chest_2x, HyperGlowingArmors_Iron_Hands_2x, HyperGlowingArmors_Iron_Head_2x, HyperGlowingArmors_Iron_Legs_2x |
| HyperGlowingArmors_Mithril | Heavy | by metal | Maybe | HyperGlowingArmors_Mithril_Chest, HyperGlowingArmors_Mithril_Hands, HyperGlowingArmors_Mithril_Head, HyperGlowingArmors_Mithril_Legs |
| HyperGlowingArmors_Mithril_2x | Heavy | by metal | No | HyperGlowingArmors_Mithril_Chest_2x, HyperGlowingArmors_Mithril_Hands_2x, HyperGlowingArmors_Mithril_Head_2x, HyperGlowingArmors_Mithril_Legs_2x |
| HyperGlowingArmors_Onyxium | Heavy | by metal | Maybe | HyperGlowingArmors_Onyxium_Chest, HyperGlowingArmors_Onyxium_Hands, HyperGlowingArmors_Onyxium_Head, HyperGlowingArmors_Onyxium_Legs |
| HyperGlowingArmors_Onyxium_2x | Heavy | by metal | No | HyperGlowingArmors_Onyxium_Chest_2x, HyperGlowingArmors_Onyxium_Hands_2x, HyperGlowingArmors_Onyxium_Head_2x, HyperGlowingArmors_Onyxium_Legs_2x |
| HyperGlowingArmors_Prisma | Heavy | by metal | Maybe | HyperGlowingArmors_Prisma_Chest, HyperGlowingArmors_Prisma_Hands, HyperGlowingArmors_Prisma_Head, HyperGlowingArmors_Prisma_Legs |
| HyperGlowingArmors_Prisma_2x | Heavy | by metal | No | HyperGlowingArmors_Prisma_Chest_2x, HyperGlowingArmors_Prisma_Hands_2x, HyperGlowingArmors_Prisma_Head_2x, HyperGlowingArmors_Prisma_Legs_2x |
| HyperGlowingArmors_Thorium | Heavy | by metal | Maybe | HyperGlowingArmors_Thorium_Chest, HyperGlowingArmors_Thorium_Hands, HyperGlowingArmors_Thorium_Head, HyperGlowingArmors_Thorium_Legs |
| HyperGlowingArmors_Thorium_2x | Heavy | by metal | No | HyperGlowingArmors_Thorium_Chest_2x, HyperGlowingArmors_Thorium_Hands_2x, HyperGlowingArmors_Thorium_Head_2x, HyperGlowingArmors_Thorium_Legs_2x |

### SLVR_Arcane_Robes__Spells_v1.2.0.zip (24)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| SLVR_Armor_Cloth_Cindercloth | Cloth | Adamantite | Yes | SLVR_Armor_Cloth_Cindercloth_Chest, SLVR_Armor_Cloth_Cindercloth_Hands, SLVR_Armor_Cloth_Cindercloth_Head, SLVR_Armor_Cloth_Cindercloth_Legs |
| SLVR_Armor_Cloth_Cotton | Cloth | Iron | Yes | SLVR_Armor_Cloth_Cotton_Chest, SLVR_Armor_Cloth_Cotton_Hands, SLVR_Armor_Cloth_Cotton_Head, SLVR_Armor_Cloth_Cotton_Legs |
| SLVR_Armor_Cloth_Linen | Cloth | Copper | Yes | SLVR_Armor_Cloth_Linen_Chest, SLVR_Armor_Cloth_Linen_Hands, SLVR_Armor_Cloth_Linen_Head, SLVR_Armor_Cloth_Linen_Legs |
| SLVR_Armor_Cloth_Raven | Cloth | Cobalt | Yes | SLVR_Armor_Cloth_Raven_Chest, SLVR_Armor_Cloth_Raven_Hands, SLVR_Armor_Cloth_Raven_Head, SLVR_Armor_Cloth_Raven_Legs |
| SLVR_Armor_Cloth_Silk | Cloth | Thorium | Yes | SLVR_Armor_Cloth_Silk_Chest, SLVR_Armor_Cloth_Silk_Hands, SLVR_Armor_Cloth_Silk_Head, SLVR_Armor_Cloth_Silk_Legs |
| SLVR_Armor_Wool | Cloth | Crude | Yes | SLVR_Armor_Wool_Chest, SLVR_Armor_Wool_Hands, SLVR_Armor_Wool_Head, SLVR_Armor_Wool_Legs |

### SkyyKeyProbe.jar (1)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| SkyyKeyProbe | - | - | No | SkyyKeyProbe_Helmet |

### Skyys-HyMax.zip (20)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Diving_Crude | Heavy | by metal | No | Armor_Diving_Crude_Chest, Armor_Diving_Crude_Hands, Armor_Diving_Crude_Head, Armor_Diving_Crude_Legs |
| Armor_Onyxium | Heavy | by metal | No | Armor_Onyxium_Chest, Armor_Onyxium_Hands, Armor_Onyxium_Head, Armor_Onyxium_Legs |
| Armor_Prisma | Heavy | by metal | No | Armor_Prisma_Chest, Armor_Prisma_Hands, Armor_Prisma_Head, Armor_Prisma_Legs |
| Armor_Steel | Heavy | by metal | No | Armor_Steel_Chest, Armor_Steel_Hands, Armor_Steel_Head, Armor_Steel_Legs |
| Armor_Wool | Heavy | by metal | No | Armor_Wool_Chest, Armor_Wool_Hands, Armor_Wool_Head, Armor_Wool_Legs |

### Skyys-Modpack.jar (3)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Bramblekin | Light | Copper | No | Armor_Bramblekin_Chest, Armor_Bramblekin_Hands, Armor_Bramblekin_Head |

### StarTale-V1.4.0.zip (8)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Beskar | Heavy | Adamantite | No | BeskarChest, BeskarGauntlets, BeskarHead, BeskarThighs |
| Stormtrooper | Heavy | Iron | No | StormtrooperArms, StormtrooperChest, StormtrooperHelmet, StormtrooperLegs |

### TerrariaAddons-1.7.4.jar (2)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Mining | Heavy | Iron | No | Mining_Helmet |
| Wizard_Hat | Cloth | Iron | Maybe | Wizard_Hat |

### TerrariaToolsWeapons-0.5.0.jar (20)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Cactus | Heavy | Crude | Maybe | Armor_Cactus_Chest, Armor_Cactus_Hands, Armor_Cactus_Head, Armor_Cactus_Legs |
| Armor_Crimson | Heavy | Cobalt | Maybe | Armor_Crimson_Chest, Armor_Crimson_Hands, Armor_Crimson_Head, Armor_Crimson_Legs |
| Armor_Lead | Heavy | Copper | Maybe | Armor_Lead_Chest, Armor_Lead_Hands, Armor_Lead_Head, Armor_Lead_Legs |
| Armor_Silver | Heavy | Copper | Maybe | Armor_Silver_Chest, Armor_Silver_Hands, Armor_Silver_Head, Armor_Silver_Legs |
| Armor_Wooden | Heavy | Crude | Maybe | Armor_Wooden_Chest, Armor_Wooden_Hands, Armor_Wooden_Head, Armor_Wooden_Legs |

### TheArmoryMod-1.22.0.jar (1019)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Academy Set | Cloth | Adamantite | Special | AcademyHat, BlackAcademyHat, BlackWizenedJacket, BlackWizenedSleeves, BlueWizenedJacket, BlueWizenedSleeves, BrownAcademyHat, BrownWizenedJacket, BrownWizenedSleeves, GreenAcademyHat, GreenWizenedJacket, GreenWizenedSleeves, PinkAcademyHat, PinkWizenedJacket, PinkWizenedSleeves, PurpleAcademyHat, PurpleWizenedJacket, PurpleWizenedSleeves, RedAcademyHat, RedWizenedJacket, RedWizenedSleeves, WhiteAcademyHat, WhiteWizenedJacket, WhiteWizenedSleeves, YellowAcademyHat, YellowWizenedJacket, YellowWizenedSleeves |
| Skull Masks | Light | Iron | Drop | Alt1_SkullMaskBlack, Alt1_SkullMaskBlue, Alt1_SkullMaskCyan, Alt1_SkullMaskDarkBlue, Alt1_SkullMaskDarkCyan, Alt1_SkullMaskDarkGreen, Alt1_SkullMaskDarkMagenta, Alt1_SkullMaskDarkPurple, Alt1_SkullMaskDarkRed, Alt1_SkullMaskDarkWhite, Alt1_SkullMaskDarkYellow, Alt1_SkullMaskGreen, Alt1_SkullMaskMagenta, Alt1_SkullMaskPurple, Alt1_SkullMaskRed, Alt1_SkullMaskYellow, Alt2_SkullMaskBlack, Alt2_SkullMaskBlue, Alt2_SkullMaskCyan, Alt2_SkullMaskDarkBlue, Alt2_SkullMaskDarkCyan, Alt2_SkullMaskDarkGreen, Alt2_SkullMaskDarkMagenta, Alt2_SkullMaskDarkPurple, Alt2_SkullMaskDarkRed, Alt2_SkullMaskDarkWhite, Alt2_SkullMaskDarkYellow, Alt2_SkullMaskGreen, Alt2_SkullMaskMagenta, Alt2_SkullMaskPurple, Alt2_SkullMaskRed, Alt2_SkullMaskYellow, Alt3_SkullMaskBlack, Alt3_SkullMaskBlue, Alt3_SkullMaskCyan, Alt3_SkullMaskDarkBlue, Alt3_SkullMaskDarkCyan, Alt3_SkullMaskDarkGreen, Alt3_SkullMaskDarkMagenta, Alt3_SkullMaskDarkPurple, Alt3_SkullMaskDarkRed, Alt3_SkullMaskDarkWhite, Alt3_SkullMaskDarkYellow, Alt3_SkullMaskGreen, Alt3_SkullMaskMagenta, Alt3_SkullMaskPurple, Alt3_SkullMaskRed, Alt3_SkullMaskYellow, SkullMask, SkullMaskBlack, SkullMaskBlue, SkullMaskCyan, SkullMaskGreen, SkullMaskMagenta, SkullMaskPurple, SkullMaskRed, SkullMaskWhite |
| Vanilla Recolor Iron | Heavy | Iron | Drop | Armor_Iron_Chest_Black, Armor_Iron_Chest_Black_Alt, Armor_Iron_Chest_Black_Fab, Armor_Iron_Chest_Blue, Armor_Iron_Chest_Blue_Alt, Armor_Iron_Chest_Blue_Fab, Armor_Iron_Chest_Cyan, Armor_Iron_Chest_Cyan_Alt, Armor_Iron_Chest_Cyan_Fab, Armor_Iron_Chest_Green, Armor_Iron_Chest_Green_Alt, Armor_Iron_Chest_Green_Fab, Armor_Iron_Chest_Magenta, Armor_Iron_Chest_Magenta_Alt, Armor_Iron_Chest_Magenta_Fab, Armor_Iron_Chest_Purple, Armor_Iron_Chest_Purple_Alt, Armor_Iron_Chest_Purple_Fab, Armor_Iron_Chest_Red, Armor_Iron_Chest_Red_Alt, Armor_Iron_Chest_Rusty, Armor_Iron_Chest_Stone, Armor_Iron_Chest_White, Armor_Iron_Chest_White_Alt, Armor_Iron_Chest_White_Fab, Armor_Iron_Chest_Yellow, Armor_Iron_Chest_Yellow_Alt, Armor_Iron_Chest_Yellow_Fab, Armor_Iron_Hands_Black, Armor_Iron_Hands_Black_Alt, Armor_Iron_Hands_Blue, Armor_Iron_Hands_Blue_Alt, Armor_Iron_Hands_Cyan, Armor_Iron_Hands_Cyan_Alt, Armor_Iron_Hands_Green, Armor_Iron_Hands_Green_Alt, Armor_Iron_Hands_Magenta, Armor_Iron_Hands_Magenta_Alt, Armor_Iron_Hands_Purple, Armor_Iron_Hands_Purple_Alt, Armor_Iron_Hands_Red, Armor_Iron_Hands_Red_Alt, Armor_Iron_Hands_Rusty, Armor_Iron_Hands_Stone, Armor_Iron_Hands_White, Armor_Iron_Hands_White_Alt, Armor_Iron_Hands_Yellow, Armor_Iron_Hands_Yellow_Alt, Armor_Iron_Head_Black, Armor_Iron_Head_Black_Alt, Armor_Iron_Head_Blue, Armor_Iron_Head_Blue_Alt, Armor_Iron_Head_Cyan, Armor_Iron_Head_Cyan_Alt, Armor_Iron_Head_Green, Armor_Iron_Head_Green_Alt, Armor_Iron_Head_Magenta, Armor_Iron_Head_Magenta_Alt, Armor_Iron_Head_Purple, Armor_Iron_Head_Purple_Alt, Armor_Iron_Head_Red, Armor_Iron_Head_Red_Alt, Armor_Iron_Head_Rusty, Armor_Iron_Head_Stone, Armor_Iron_Head_White, Armor_Iron_Head_White_Alt, Armor_Iron_Head_Yellow, Armor_Iron_Head_Yellow_Alt, Armor_Iron_Legs_Black, Armor_Iron_Legs_Black_Alt, Armor_Iron_Legs_Black_Fab, Armor_Iron_Legs_Blue, Armor_Iron_Legs_Blue_Alt, Armor_Iron_Legs_Blue_Fab, Armor_Iron_Legs_Cyan, Armor_Iron_Legs_Cyan_Alt, Armor_Iron_Legs_Cyan_Fab, Armor_Iron_Legs_Green, Armor_Iron_Legs_Green_Alt, Armor_Iron_Legs_Green_Fab, Armor_Iron_Legs_Magenta, Armor_Iron_Legs_Magenta_Alt, Armor_Iron_Legs_Magenta_Fab, Armor_Iron_Legs_Purple, Armor_Iron_Legs_Purple_Alt, Armor_Iron_Legs_Purple_Fab, Armor_Iron_Legs_Red, Armor_Iron_Legs_Red_Alt, Armor_Iron_Legs_Red_Fab, Armor_Iron_Legs_Rusty, Armor_Iron_Legs_Stone, Armor_Iron_Legs_White, Armor_Iron_Legs_White_Alt, Armor_Iron_Legs_White_Fab, Armor_Iron_Legs_Yellow, Armor_Iron_Legs_Yellow_Alt, Armor_Iron_Legs_Yellow_Fab |
| Amulets | Cloth | Iron | Drop | BlueAmulet, BlueAmuletHead, GreenAmulet, GreenAmuletHead, PurpleAmulet, PurpleAmuletHead, YellowAmulet, YellowAmuletHead |
| Crowns | Cloth | Iron | Drop | BlueCrown, BlueCrownAlt, BlueCrownEvil, GreenCrown, GreenCrownAlt, GreenCrownEvil, IronCrown, IronCrownAlt, IronCrownBlueDiadem, IronCrownBlueDiademAlt, IronCrownEvil, IronCrownGreenDiadem, IronCrownGreenDiademAlt, IronCrownGreenDiademEvil, IronCrownPurpleDiadem, IronCrownPurpleDiademAlt, IronCrownPurpleDiademEvil, IronCrownRedDiadem, IronCrownRedDiademAlt, IronCrownRedDiademEvil, IronCrownYellowDiadem, IronCrownYellowDiademAlt, IronCrownYellowDiademEvil, LichCrown, LichCrownAlt, LichCrownEvil, PurpleCrown, PurpleCrownAlt, PurpleCrownEvil, RedCrown, RedCrownAlt, RedCrownEvil, RustedCrown, RustedCrownAlt, RustedCrownEvil, WhiteCrown, WhiteCrownAlt, WhiteCrownEvil, YellowCrown, YellowCrownAlt, YellowCrownEvil |
| Misc | Light | Iron | Drop | BramblekinBracers, BramblekinMask |
| Daemon Set | Heavy | Adamantite | Special | CyclopsHelm, CyclopsHelmCyan, CyclopsHelmOpened, CyclopsHelmOpenedCyan, CyclopsHelmOpenedPurple, CyclopsHelmPurple, DemonChestplate, DemonChestplateCyan, DemonChestplatePurple, DemonGauntlets, DemonGauntletsCyan, DemonGauntletsPurple, DemonHelm, DemonHelmCyan, DemonHelmOpened, DemonHelmOpenedCyan, DemonHelmOpenedPurple, DemonHelmPurple, DemonLeggings, DemonLeggingsCyan, DemonLeggingsPurple, GluttonHelm, GluttonHelmCyan, GluttonHelmOpened, GluttonHelmOpenedCyan, GluttonHelmOpenedPurple, GluttonHelmPurple |
| Elite Scorpion Helms | Light | Adamantite | Special | EliteScorpianAllBlack, EliteScorpianAllBlue, EliteScorpianAllGreen, EliteScorpianAllPink, EliteScorpianAllPurple, EliteScorpianAllRed, EliteScorpianAllYellow, EliteScorpianBlack, EliteScorpianBlackBraid, EliteScorpianBlue, EliteScorpianBlueBraid, EliteScorpianGingerBraid, EliteScorpianGreen, EliteScorpianGreenBraid, EliteScorpianHelm, EliteScorpianPink, EliteScorpianPurple, EliteScorpianPurpleBraid, EliteScorpianRed, EliteScorpianWhite, EliteScorpianYellow |
| Engineering Rig | Light | Thorium | Special | EngineeringRig, EngineeringRigAlt |
| Grand Lich Hood | Cloth | Adamantite | Special | GrandLichHoodBlackAlt, GrandLichHoodBlackAltVeiless, GrandLichHoodBlue, GrandLichHoodBlueAlt, GrandLichHoodBlueAltVeiless, GrandLichHoodBlueVeiless, GrandLichHoodCyan, GrandLichHoodCyanAlt, GrandLichHoodCyanAltVeiless, GrandLichHoodCyanVeiless, GrandLichHoodDown, GrandLichHoodDownBlackAlt, GrandLichHoodDownBlue, GrandLichHoodDownBlueAlt, GrandLichHoodDownCyan, GrandLichHoodDownCyanAlt, GrandLichHoodDownGreen, GrandLichHoodDownGreenAlt, GrandLichHoodDownMagenta, GrandLichHoodDownMagentaAlt, GrandLichHoodDownPurple, GrandLichHoodDownPurpleAlt, GrandLichHoodDownRed, GrandLichHoodDownWhite, GrandLichHoodDownWhiteAlt, GrandLichHoodDownYellow, GrandLichHoodDownYellowAlt, GrandLichHoodGreen, GrandLichHoodGreenAlt, GrandLichHoodGreenAltVeiless, GrandLichHoodGreenVeiless, GrandLichHoodMagenta, GrandLichHoodMagentaAlt, GrandLichHoodMagentaAltVeiless, GrandLichHoodMagentaVeiless, GrandLichHoodPurple, GrandLichHoodPurpleAlt, GrandLichHoodPurpleAltVeiless, GrandLichHoodPurpleVeiless, GrandLichHoodRed, GrandLichHoodRedVeiless, GrandLichHoodStandard, GrandLichHoodVieless, GrandLichHoodWhite, GrandLichHoodWhiteAlt, GrandLichHoodWhiteAltVeiless, GrandLichHoodWhiteVeiless, GrandLichHoodYellow, GrandLichHoodYellowAlt, GrandLichHoodYellowAltVeiless, GrandLichHoodYellowVeiless, GrandLichHoodless, GrandLichHoodlessBlackAlt, GrandLichHoodlessBlue, GrandLichHoodlessBlueAlt, GrandLichHoodlessCyan, GrandLichHoodlessCyanAlt, GrandLichHoodlessGreen, GrandLichHoodlessGreenAlt, GrandLichHoodlessMagenta, GrandLichHoodlessMagentaAlt, GrandLichHoodlessPurple, GrandLichHoodlessPurpleAlt, GrandLichHoodlessRed, GrandLichHoodlessWhite, GrandLichHoodlessWhiteAlt, GrandLichHoodlessYellow, GrandLichHoodlessYellowAlt |
| Jester Set | Light | Copper | Drop | JesterChest, JesterChestBlackBlue, JesterChestBlackCyan, JesterChestBlackGreen, JesterChestBlackMagenta, JesterChestBlackRed, JesterChestBlackWhite, JesterChestBlackYellow, JesterChestBlueMagenta, JesterChestCyanGreen, JesterChestCyanMagenta, JesterChestCyanYellow, JesterChestPurpleMagenta, JesterChestRedGreen, JesterChestYellowBlue, JesterChestYellowGreen, JesterChestYellowMagenta, JesterChestYellowPurple, JesterHatDouble, JesterHatDoubleBlackBlue, JesterHatDoubleBlackCyan, JesterHatDoubleBlackGreen, JesterHatDoubleBlackMagenta, JesterHatDoubleBlackRed, JesterHatDoubleBlackWhite, JesterHatDoubleBlackYellow, JesterHatDoubleBlueMagenta, JesterHatDoubleCyanGreen, JesterHatDoubleCyanMagenta, JesterHatDoubleCyanYellow, JesterHatDoublePurpleMagenta, JesterHatDoubleRedGreen, JesterHatDoubleYellowBlue, JesterHatDoubleYellowGreen, JesterHatDoubleYellowMagenta, JesterHatDoubleYellowPurple, JesterHatQuad, JesterHatQuadBlackBlue, JesterHatQuadBlackCyan, JesterHatQuadBlackGreen, JesterHatQuadBlackMagenta, JesterHatQuadBlackRed, JesterHatQuadBlackWhite, JesterHatQuadBlackYellow, JesterHatQuadBlueMagenta, JesterHatQuadCyanGreen, JesterHatQuadCyanMagenta, JesterHatQuadCyanYellow, JesterHatQuadPurpleMagenta, JesterHatQuadRedGreen, JesterHatQuadYellowBlue, JesterHatQuadYellowGreen, JesterHatQuadYellowMagenta, JesterHatQuadYellowPurple, JesterHatReverse, JesterHatReverseBlackBlue, JesterHatReverseBlackCyan, JesterHatReverseBlackGreen, JesterHatReverseBlackMagenta, JesterHatReverseBlackRed, JesterHatReverseBlackWhite, JesterHatReverseBlackYellow, JesterHatReverseBlueMagenta, JesterHatReverseCyanGreen, JesterHatReverseCyanMagenta, JesterHatReverseCyanYellow, JesterHatReversePurpleMagenta, JesterHatReverseRedGreen, JesterHatReverseYellowBlue, JesterHatReverseYellowGreen, JesterHatReverseYellowMagenta, JesterHatReverseYellowPurple, JesterHatSingle, JesterHatSingleBlackBlue, JesterHatSingleBlackCyan, JesterHatSingleBlackGreen, JesterHatSingleBlackMagenta, JesterHatSingleBlackRed, JesterHatSingleBlackWhite, JesterHatSingleBlackYellow, JesterHatSingleBlueMagenta, JesterHatSingleCyanGreen, JesterHatSingleCyanMagenta, JesterHatSingleCyanYellow, JesterHatSinglePurpleMagenta, JesterHatSingleRedGreen, JesterHatSingleYellowBlue, JesterHatSingleYellowGreen, JesterHatSingleYellowMagenta, JesterHatSingleYellowPurple, JesterHatSinister, JesterHatSinisterBlackBlue, JesterHatSinisterBlackCyan, JesterHatSinisterBlackGreen, JesterHatSinisterBlackMagenta, JesterHatSinisterBlackRed, JesterHatSinisterBlackWhite, JesterHatSinisterBlackYellow, JesterHatSinisterBlueMagenta, JesterHatSinisterCyanGreen, JesterHatSinisterCyanMagenta, JesterHatSinisterCyanYellow, JesterHatSinisterPurpleMagenta, JesterHatSinisterRedGreen, JesterHatSinisterYellowBlue, JesterHatSinisterYellowGreen, JesterHatSinisterYellowMagenta, JesterHatSinisterYellowPurple, JesterLegs, JesterLegsAlt, JesterLegsAltBlackBlue, JesterLegsAltBlackCyan, JesterLegsAltBlackGreen, JesterLegsAltBlackMagenta, JesterLegsAltBlackRed, JesterLegsAltBlackWhite, JesterLegsAltBlackYellow, JesterLegsAltBlueMagenta, JesterLegsAltCyanGreen, JesterLegsAltCyanMagenta, JesterLegsAltCyanYellow, JesterLegsAltPurpleMagenta, JesterLegsAltRedGreen, JesterLegsAltYellowBlue, JesterLegsAltYellowGreen, JesterLegsAltYellowMagenta, JesterLegsAltYellowPurple, JesterLegsBlackBlue, JesterLegsBlackCyan, JesterLegsBlackGreen, JesterLegsBlackMagenta, JesterLegsBlackRed, JesterLegsBlackWhite, JesterLegsBlackYellow, JesterLegsBlueMagenta, JesterLegsCyanGreen, JesterLegsCyanMagenta, JesterLegsCyanYellow, JesterLegsPurpleMagenta, JesterLegsRedGreen, JesterLegsYellowBlue, JesterLegsYellowGreen, JesterLegsYellowMagenta, JesterLegsYellowPurple |
| Kanohi | - | - | No | KanohiHau, KanohiHauBlack, KanohiHauBlue, KanohiHauBrown, KanohiHauGold, KanohiHauGreen, KanohiHauRusted, KanohiHauSilver, KanohiHauWhite |
| Potion Bandolier | Cloth | Iron | Drop | PotionBandolierBeltBlue, PotionBandolierBeltPink, PotionBandolierBeltPurple, PotionBandolierBeltRed, PotionBandolierBlue, PotionBandolierBlueClip, PotionBandolierBurntSkeleton, PotionBandolierGreen, PotionBandolierGreenClip, PotionBandolierPink, PotionBandolierPinkClip, PotionBandolierPurple, PotionBandolierPurpleClip, PotionBandolierRed, PotionBandolierRedClip, PotionBeltBlueClip, PotionBeltPinkClip, PotionBeltPurpleClip, PotionBeltRedClip |
| Priest Set | Cloth | Cobalt | Special | PriestChest, PriestChestAlt, PriestChestAltBlack, PriestChestAltBlue, PriestChestAltGreen, PriestChestAltPink, PriestChestAltPurple, PriestChestAltWhite, PriestChestAltYellow, PriestChestBlack, PriestChestBlue, PriestChestGreen, PriestChestPink, PriestChestPurple, PriestChestWhite, PriestChestYellow, PriestHelm, PriestHelmBlack, PriestHelmBlue, PriestHelmGreen, PriestHelmOpen, PriestHelmOpenBlack, PriestHelmOpenBlue, PriestHelmOpenGreen, PriestHelmOpenPink, PriestHelmOpenPurple, PriestHelmOpenWhite, PriestHelmOpenYellow, PriestHelmPink, PriestHelmPurple, PriestHelmWhite, PriestHelmYellow, PriestRobes, PriestRobesBlack, PriestRobesBlue, PriestRobesGreen, PriestRobesPink, PriestRobesPurple, PriestRobesWhite, PriestRobesYellow, PriestSleeves, PriestSleevesBlack, PriestSleevesBlue, PriestSleevesGreen, PriestSleevesPink, PriestSleevesPurple, PriestSleevesWhite, PriestSleevesYellow, PriestTunic, PriestTunicBlack, PriestTunicBlue, PriestTunicGreen, PriestTunicPink, PriestTunicPurple, PriestTunicWhite, PriestTunicYellow |
| Misc | Light | Adamantite | Special | Relentless |
| Tribal Masks | Light | Crude | Drop | RhinoMask, SnowLeopardMask, VultureMask |
| Rook Set | Heavy | Iron | Drop | RookBootsAzure, RookBootsBlack, RookBootsFrosty, RookBootsGhost, RookBootsGoth, RookBootsGreen, RookBootsPurple, RookBootsRed, RookBootsRusty, RookBootsWraith, RookChestAzure, RookChestBlack, RookChestFrosty, RookChestGhost, RookChestGoth, RookChestGreen, RookChestPurple, RookChestRed, RookChestRusty, RookChestWraith, RookGauntletsAzure, RookGauntletsBlack, RookGauntletsFrosty, RookGauntletsGhost, RookGauntletsGoth, RookGauntletsGreen, RookGauntletsPurple, RookGauntletsRed, RookGauntletsRusty, RookGauntletsWraith, RookHelmAzure, RookHelmAzureOpen, RookHelmBlack, RookHelmBlackOpen, RookHelmFrosty, RookHelmFrostyOpen, RookHelmGhost, RookHelmGhostOpen, RookHelmGoth, RookHelmGothOpen, RookHelmGreen, RookHelmGreenOpen, RookHelmPurple, RookHelmPurpleOpen, RookHelmRed, RookHelmRedOpen, RookHelmWraith, RookHelmWraithOpen, RookRustyHelm, RookRustyOpen |
| Elite Rook Set | Heavy | Thorium | Special | RookEliteBootsCharred, RookEliteBootsCharred2, RookEliteBootsIradescent, RookEliteBootsMarble, RookEliteBootsMonster, RookEliteBootsRainbow, RookEliteBootsRuby, RookEliteBootsSapphire, RookEliteBootsStone, RookEliteBootsVerdan, RookEliteChestCharred, RookEliteChestIradescent, RookEliteChestMarble, RookEliteChestMonster, RookEliteChestRainbow, RookEliteChestRuby, RookEliteChestSapphire, RookEliteChestStone, RookEliteChestVerdan, RookEliteGauntletsCharred, RookEliteGauntletsIradescent, RookEliteGauntletsMarble, RookEliteGauntletsMonster, RookEliteGauntletsRainbow, RookEliteGauntletsRuby, RookEliteGauntletsSapphire, RookEliteGauntletsStone, RookEliteGauntletsVerdan, RookEliteHelmCharred, RookEliteHelmCharredOpen, RookEliteHelmIradescent, RookEliteHelmIradescentOpen, RookEliteHelmMarble, RookEliteHelmMarbleOpen, RookEliteHelmMonster, RookEliteHelmMonsterOpen, RookEliteHelmRainbow, RookEliteHelmRainbowOpen, RookEliteHelmRuby, RookEliteHelmRubyOpen, RookEliteHelmSapphire, RookEliteHelmStone, RookEliteHelmStoneOpen, RookEliteHelmVerdan, RookEliteHelmVerdanOpen, RookEliteSapphireOpen |
| Scarecrow | Cloth | Copper | Drop | ScareCrowHatBlack, ScareCrowHatBlue, ScareCrowHatEvil, ScareCrowHatGreen, ScareCrowHatMagenta, ScareCrowHatPurple, ScareCrowHatRed, ScareCrowHatWhite, ScareCrowHatYellow, ScareCrowHelm, ScareCrowHelmBlack, ScareCrowHelmCyan, ScareCrowHelmEvil, ScareCrowHelmGreen, ScareCrowHelmMagenta, ScareCrowHelmPurple, ScareCrowHelmRed, ScareCrowHelmWhite, ScareCrowHelmYellow |
| Scorpion Helms | Light | Adamantite | Drop | ScorpianAllBlack, ScorpianAllBlue, ScorpianAllGreen, ScorpianAllPink, ScorpianAllPurple, ScorpianAllRed, ScorpianAllYellow, ScorpianBlackBraid, ScorpianBlueBraid, ScorpianBraidPurple, ScorpianGingerBraid, ScorpianGreenBraid, ScorpianHelm, ScorpianHelmBlack, ScorpianHelmBlue, ScorpianHelmGreen, ScorpianHelmPink, ScorpianHelmPurple, ScorpianHelmRed, ScorpianHelmWhite, ScorpianHelmYellow, ScorpianPinkBraid, ScorpianWhiteBraid |
| Battlegrounds | Cloth | Iron | Special | TarnishedCrown, VerdantAmulet |
| Warden Set | Light | Iron | Special | WardenChest, WardenChestDesert, WardenChestFire, WardenHelm, WardenHelmDesert, WardenHelmDesertOpen, WardenHelmDesertOpenAlt, WardenHelmFire, WardenHelmFireOpen, WardenHelmFireOpenAlt, WardenHelmOpen, WardenHelmOpenAlt, WardenLeggings, WardenLeggingsDesert, WardenLeggingsFire, WardenSleeves, WardenSleevesDesert, WardenSleevesFire |
| Calvary Set | Heavy | Iron | Drop | CalvaryChestAltBlack, CalvaryChestAltBlackBlack, CalvaryChestAltBlackBlue, CalvaryChestAltBlackCyan, CalvaryChestAltBlackGreen, CalvaryChestAltBlackMagenta, CalvaryChestAltBlackPurple, CalvaryChestAltBlackRed, CalvaryChestAltBlackYellow, CalvaryChestAltBlue, CalvaryChestAltCyan, CalvaryChestAltGoldBlack, CalvaryChestAltGoldBlue, CalvaryChestAltGoldCyan, CalvaryChestAltGoldGreen, CalvaryChestAltGoldMagenta, CalvaryChestAltGoldPurple, CalvaryChestAltGoldRed, CalvaryChestAltGoldYellow, CalvaryChestAltGreen, CalvaryChestAltMagenta, CalvaryChestAltPurple, CalvaryChestAltRed, CalvaryChestAltWhite, CalvaryChestAltYellow, CalvaryChestBlack, CalvaryChestBlackBlack, CalvaryChestBlackBlue, CalvaryChestBlackCyan, CalvaryChestBlackGreen, CalvaryChestBlackMagenta, CalvaryChestBlackPurple, CalvaryChestBlackRed, CalvaryChestBlackYellow, CalvaryChestBlue, CalvaryChestCyan, CalvaryChestGoldBlack, CalvaryChestGoldBlue, CalvaryChestGoldCyan, CalvaryChestGoldGreen, CalvaryChestGoldMagenta, CalvaryChestGoldPurple, CalvaryChestGoldRed, CalvaryChestGoldYellow, CalvaryChestGreen, CalvaryChestMagenta, CalvaryChestPurple, CalvaryChestRed, CalvaryChestWhite, CalvaryChestYellow, CalvaryGauntletBlack, CalvaryGauntletBlue, CalvaryGauntletsBlackBlack, CalvaryGauntletsBlackBlue, CalvaryGauntletsBlackCyan, CalvaryGauntletsBlackGreen, CalvaryGauntletsBlackMagenta, CalvaryGauntletsBlackPurple, CalvaryGauntletsBlackRed, CalvaryGauntletsBlackYellow, CalvaryGauntletsCyan, CalvaryGauntletsGoldBlack, CalvaryGauntletsGoldBlue, CalvaryGauntletsGoldCyan, CalvaryGauntletsGoldGreen, CalvaryGauntletsGoldMagenta, CalvaryGauntletsGoldPurple, CalvaryGauntletsGoldRed, CalvaryGauntletsGoldYellow, CalvaryGauntletsGreen, CalvaryGauntletsMagenta, CalvaryGauntletsPurple, CalvaryGauntletsRed, CalvaryGauntletsWhite, CalvaryGauntletsYellow, CalvaryHeadAlt2Black, CalvaryHeadAlt2BlackBlack, CalvaryHeadAlt2BlackBlue, CalvaryHeadAlt2BlackCyan, CalvaryHeadAlt2BlackGreen, CalvaryHeadAlt2BlackMagenta, CalvaryHeadAlt2BlackPurple, CalvaryHeadAlt2BlackRed, CalvaryHeadAlt2BlackYellow, CalvaryHeadAlt2Blue, CalvaryHeadAlt2Cyan, CalvaryHeadAlt2GoldBlack, CalvaryHeadAlt2GoldBlue, CalvaryHeadAlt2GoldCyan, CalvaryHeadAlt2GoldGreen, CalvaryHeadAlt2GoldMagenta, CalvaryHeadAlt2GoldPurple, CalvaryHeadAlt2GoldRed, CalvaryHeadAlt2GoldYellow, CalvaryHeadAlt2Green, CalvaryHeadAlt2Magenta, CalvaryHeadAlt2Purple, CalvaryHeadAlt2Red, CalvaryHeadAlt2White, CalvaryHeadAlt2Yellow, CalvaryHeadAltBlack, CalvaryHeadAltBlackBlack, CalvaryHeadAltBlackBlue, CalvaryHeadAltBlackCyan, CalvaryHeadAltBlackGreen, CalvaryHeadAltBlackMagenta, CalvaryHeadAltBlackPurple, CalvaryHeadAltBlackRed, CalvaryHeadAltBlackYellow, CalvaryHeadAltBlue, CalvaryHeadAltCyan, CalvaryHeadAltGoldBlack, CalvaryHeadAltGoldBlue, CalvaryHeadAltGoldCyan, CalvaryHeadAltGoldGreen, CalvaryHeadAltGoldMagenta, CalvaryHeadAltGoldPurple, CalvaryHeadAltGoldRed, CalvaryHeadAltGoldYellow, CalvaryHeadAltGreen, CalvaryHeadAltMagenta, CalvaryHeadAltPurple, CalvaryHeadAltRed, CalvaryHeadAltWhite, CalvaryHeadAltYellow, CalvaryHeadBlack, CalvaryHeadBlackBlack, CalvaryHeadBlackBlue, CalvaryHeadBlackCyan, CalvaryHeadBlackGreen, CalvaryHeadBlackMagenta, CalvaryHeadBlackPurple, CalvaryHeadBlackRed, CalvaryHeadBlackYellow, CalvaryHeadBlue, CalvaryHeadCyan, CalvaryHeadGoldBlack, CalvaryHeadGoldBlue, CalvaryHeadGoldCyan, CalvaryHeadGoldGreen, CalvaryHeadGoldMagenta, CalvaryHeadGoldPurple, CalvaryHeadGoldRed, CalvaryHeadGoldYellow, CalvaryHeadGreen, CalvaryHeadMagenta, CalvaryHeadPurple, CalvaryHeadRed, CalvaryHeadWhite, CalvaryHeadYellow, CalvaryLeggingsBlack, CalvaryLeggingsBlue, CalvaryLegsBlackBlack, CalvaryLegsBlackBlue, CalvaryLegsBlackCyan, CalvaryLegsBlackGreen, CalvaryLegsBlackMagenta, CalvaryLegsBlackPurple, CalvaryLegsBlackRed, CalvaryLegsBlackYellow, CalvaryLegsCyan, CalvaryLegsGoldBlack, CalvaryLegsGoldBlue, CalvaryLegsGoldCyan, CalvaryLegsGoldGreen, CalvaryLegsGoldMagenta, CalvaryLegsGoldPurple, CalvaryLegsGoldRed, CalvaryLegsGoldYellow, CalvaryLegsGreen, CalvaryLegsMagenta, CalvaryLegsPurple, CalvaryLegsRed, CalvaryLegsWhite, CalvaryLegsYellow, GhostCalvaryChest, GhostCalvaryGauntlets, GhostCalvaryHelm, GhostCalvaryLeggings |
| Cobalt Dragon Set | Heavy | Cobalt | Special | CobaltDragonChestPlateBlackGreen, CobaltDragonChestPlateBlackMagenta, CobaltDragonChestPlateBlackPurple, CobaltDragonChestPlateBlackRed, CobaltDragonChestPlateBlackYellow, CobaltDragonChestPlateCyan, CobaltDragonChestPlateGreen, CobaltDragonChestPlatePurple, CobaltDragonChestPlateRed, CobaltDragonChestPlateWhite, CobaltDragonChestPlateYellow, CobaltDragonChestplate, CobaltDragonChestplateBlackBlue, CobaltDragonChestplateBlackCyan, CobaltDragonGauntlets, CobaltDragonGauntletsBlack, CobaltDragonHelm, CobaltDragonHelmAltBlue, CobaltDragonHelmAltCyan, CobaltDragonHelmAltGreen, CobaltDragonHelmAltMagenta, CobaltDragonHelmAltPurple, CobaltDragonHelmAltRed, CobaltDragonHelmAltWhite, CobaltDragonHelmAltYellow, CobaltDragonHelmBlackBlue, CobaltDragonHelmBlackCyan, CobaltDragonHelmBlackGreen, CobaltDragonHelmBlackMagenta, CobaltDragonHelmBlackPurple, CobaltDragonHelmBlackRed, CobaltDragonHelmBlackYellow, CobaltDragonHelmCyan, CobaltDragonHelmGreen, CobaltDragonHelmPurple, CobaltDragonHelmRed, CobaltDragonHelmWhite, CobaltDragonHelmYellow, CobaltDragonLeggings, CobaltDragonLeggingsBlack |
| Iron Dragon Set | Heavy | Iron | Special | IronDragonChesplateWhite, IronDragonChestplate, IronDragonChestplateCyan, IronDragonChestplateGreen, IronDragonChestplatePurple, IronDragonChestplateRed, IronDragonChestplateYellow, IronDragonGauntlets, IronDragonHelm, IronDragonHelmCyan, IronDragonHelmCyanOpen, IronDragonHelmGreen, IronDragonHelmGreenOpen, IronDragonHelmOpen, IronDragonHelmPurple, IronDragonHelmPurpleOpen, IronDragonHelmRed, IronDragonHelmRedOpen, IronDragonHelmWhite, IronDragonHelmWhiteOpen, IronDragonHelmYellow, IronDragonHelmYellowOpen, IronDragonLeggings |
| Antique Dragon Set | Heavy | Crude | Drop | AntigueDragonHelmBlueHorned, AntigueDragonHelmBlueHornedForward, AntigueDragonHelmCyanHorned, AntigueDragonHelmCyanHornedForward, AntigueDragonHelmGreenHorned, AntigueDragonHelmGreenHornedForward, AntigueDragonHelmPurpleHorned, AntigueDragonHelmPurpleHornedForward, AntigueDragonHelmRedHorned, AntigueDragonHelmRedHornedForward, AntigueDragonHelmWhiteHorned, AntigueDragonHelmWhiteHornedForward, AntigueDragonHelmYellowHorned, AntigueDragonHelmYellowHornedForward, AntiqueDragonChestplate, AntiqueDragonChestplateCyan, AntiqueDragonChestplateGreen, AntiqueDragonChestplatePurple, AntiqueDragonChestplateRed, AntiqueDragonChestplateWhite, AntiqueDragonChestplateYellow, AntiqueDragonGuantlets, AntiqueDragonHelm, AntiqueDragonHelmCyan, AntiqueDragonHelmCyanOpen, AntiqueDragonHelmGreen, AntiqueDragonHelmGreenOpen, AntiqueDragonHelmOpen, AntiqueDragonHelmPurple, AntiqueDragonHelmPurpleOpen, AntiqueDragonHelmRed, AntiqueDragonHelmRedOpen, AntiqueDragonHelmWhite, AntiqueDragonHelmWhiteOpen, AntiqueDragonHelmYellow, AntiqueDragonHelmYellowOpen, AntiqueDragonLeggings |

### TheLostWorldsV0.5.1.zip (20)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Cloth_Cotton | Cloth | by cloth | No | Armor_Cloth_Cotton_Chest, Armor_Cloth_Cotton_Hands, Armor_Cloth_Cotton_Head, Armor_Cloth_Cotton_Legs |
| Armor_Cloth_Linen | Cloth | by cloth | No | Armor_Cloth_Linen_Chest, Armor_Cloth_Linen_Hands, Armor_Cloth_Linen_Head, Armor_Cloth_Linen_Legs |
| Armor_Cloth_Silk | Cloth | by cloth | No | Armor_Cloth_Silk_Chest, Armor_Cloth_Silk_Hands, Armor_Cloth_Silk_Head, Armor_Cloth_Silk_Legs |
| Armor_Cloth_Wool | Cloth | by cloth | No | Armor_Cloth_Wool_Chest, Armor_Cloth_Wool_Hands, Armor_Cloth_Wool_Head, Armor_Cloth_Wool_Legs |
| Armor_Wool | Cloth | by cloth | No | Armor_Wool_Chest, Armor_Wool_Hands, Armor_Wool_Head, Armor_Wool_Legs |

### UnstableRifts-1.2.1.jar (24)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Armor_Bone_UnstableRifts | Heavy | by item | No | Armor_Bone_Boots_UnstableRifts, Armor_Bone_Chest_UnstableRifts, Armor_Bone_Head_UnstableRifts, Armor_Bone_Legs_UnstableRifts |
| Armor_Crystal_UnstableRifts | Heavy | by item | No | Armor_Crystal_Boots_UnstableRifts, Armor_Crystal_Chest_UnstableRifts, Armor_Crystal_Head_UnstableRifts, Armor_Crystal_Legs_UnstableRifts |
| Armor_Shale_UnstableRifts | Heavy | by item | No | Armor_Shale_Boots_UnstableRifts, Armor_Shale_Chest_UnstableRifts, Armor_Shale_Head_UnstableRifts, Armor_Shale_Legs_UnstableRifts |
| Armor_Vine_UnstableRifts | Heavy | by item | No | Armor_Vine_Boots_UnstableRifts, Armor_Vine_Chest_UnstableRifts, Armor_Vine_Head_UnstableRifts, Armor_Vine_Legs_UnstableRifts |
| Armor_Void_UnstableRifts | Heavy | by item | No | Armor_Void_Boots_UnstableRifts, Armor_Void_Chest_UnstableRifts, Armor_Void_Head_UnstableRifts, Armor_Void_Legs_UnstableRifts |
| Armor_Warden_UnstableRifts | Heavy | by item | No | Armor_Warden_Boots_UnstableRifts, Armor_Warden_Chest_UnstableRifts, Armor_Warden_Head_UnstableRifts, Armor_Warden_Legs_UnstableRifts |

### VoidAsylum-1.1.4.jar (4)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| GearedCent_Glow | Heavy | Thorium | No | GearedCent_Chest_Glow, GearedCent_Legs_Glow |
| Geared_Cent_Glow | Heavy | Thorium | No | Geared_Cent_Hands_Glow, Geared_Cent_Head_Glow |

### Vort.VoidcloakArmory1.1.0.zip (4)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| VC_Armor_Shadow | Light | Cobalt | Yes | VC_Armor_Shadow_Chest, VC_Armor_Shadow_Hands, VC_Armor_Shadow_Head, VC_Armor_Shadow_Legs |

### Zorras-ScubaGear.zip (4)

| Set | Type | Band | Use | Ids |
|---|---|---|---|---|
| Diving_Crude | Heavy | Iron | No | Diving_Crude_Chest, Diving_Crude_Hands, Diving_Crude_Head, Diving_Crude_Legs |

## Appendix B - The Armory weapons (ids + our classification only)

| Group | Class | Use | Count | Ids |
|---|---|---|---|---|
| Antique Shield | free (Warrior lean) | Drop | 6 | AntiqueShieldBlue, AntiqueShieldGreen, AntiqueShieldRed, AntiqueShieldWhite, AntiqueShieldYellow, Antique_Shield |
| Battleaxe recolors | Berserker | Drop | 40 | Weapon_Battleaxe_Adamantite_Black, Weapon_Battleaxe_Adamantite_Blue, Weapon_Battleaxe_Adamantite_Cyan, Weapon_Battleaxe_Adamantite_Gray, Weapon_Battleaxe_Adamantite_Green, Weapon_Battleaxe_Adamantite_Magenta, Weapon_Battleaxe_Adamantite_Purple, Weapon_Battleaxe_Adamantite_Rusty, Weapon_Battleaxe_Adamantite_White, Weapon_Battleaxe_Adamantite_Yellow, Weapon_Battleaxe_Cobalt_Black, Weapon_Battleaxe_Cobalt_Cyan, Weapon_Battleaxe_Cobalt_Gray, Weapon_Battleaxe_Cobalt_Green, Weapon_Battleaxe_Cobalt_Magenta, Weapon_Battleaxe_Cobalt_Purple, Weapon_Battleaxe_Cobalt_Red, Weapon_Battleaxe_Cobalt_Rusty, Weapon_Battleaxe_Cobalt_White, Weapon_Battleaxe_Cobalt_Yellow, Weapon_Battleaxe_Iron_Black, Weapon_Battleaxe_Iron_Blue, Weapon_Battleaxe_Iron_Cyan, Weapon_Battleaxe_Iron_Green, Weapon_Battleaxe_Iron_Magenta, Weapon_Battleaxe_Iron_Purple, Weapon_Battleaxe_Iron_Red, Weapon_Battleaxe_Iron_Rusty, Weapon_Battleaxe_Iron_White, Weapon_Battleaxe_Iron_Yellow, Weapon_Battleaxe_Thorium_Black, Weapon_Battleaxe_Thorium_Blue, Weapon_Battleaxe_Thorium_Cyan, Weapon_Battleaxe_Thorium_Gray, Weapon_Battleaxe_Thorium_Magenta, Weapon_Battleaxe_Thorium_Purple, Weapon_Battleaxe_Thorium_Red, Weapon_Battleaxe_Thorium_Rusty, Weapon_Battleaxe_Thorium_White, Weapon_Battleaxe_Thorium_Yellow |
| Dagger recolors (incl. misspelt Throium / Throrium ids) | Assassin | Drop | 40 | Dagger_Adamantite_Black, Dagger_Adamantite_Blue, Dagger_Adamantite_Cyan, Dagger_Adamantite_Gray, Dagger_Adamantite_Green, Dagger_Adamantite_Magenta, Dagger_Adamantite_Purple, Dagger_Adamantite_Rusty, Dagger_Adamantite_White, Dagger_Adamantite_Yellow, Dagger_Cobalt_Black, Dagger_Cobalt_Cyan, Dagger_Cobalt_Gray, Dagger_Cobalt_Green, Dagger_Cobalt_Magenta, Dagger_Cobalt_Purple, Dagger_Cobalt_Red, Dagger_Cobalt_Rusty, Dagger_Cobalt_White, Dagger_Cobalt_Yellow, Dagger_Iron_Black, Dagger_Iron_Blue, Dagger_Iron_Cyan, Dagger_Iron_Green, Dagger_Iron_Magenta, Dagger_Iron_Purple, Dagger_Iron_Red, Dagger_Iron_Rusty, Dagger_Iron_White, Dagger_Iron_Yellow, Dagger_Thorium_Black, Dagger_Thorium_Gray, Dagger_Thorium_Magenta, Dagger_Thorium_Purple, Dagger_Thorium_Red, Dagger_Thorium_White, Dagger_Thorium_Yellow, Dagger_Throium_Blue, Dagger_Throium_Cyan, Dagger_Throrium_Rusty |
| Longsword recolors | Warrior | Drop | 20 | Longsword_Cobalt_Black, Longsword_Cobalt_Cyan, Longsword_Cobalt_Gray, Longsword_Cobalt_Green, Longsword_Cobalt_Magenta, Longsword_Cobalt_Purple, Longsword_Cobalt_Red, Longsword_Cobalt_Rusty, Longsword_Cobalt_White, Longsword_Cobalt_Yellow, Longsword_Iron_Black, Longsword_Iron_Blue, Longsword_Iron_Cyan, Longsword_Iron_Green, Longsword_Iron_Magenta, Longsword_Iron_Purple, Longsword_Iron_Red, Longsword_Iron_Rusty, Longsword_Iron_White, Longsword_Iron_Yellow |
| Mace recolors | Berserker | Drop | 30 | Mace_Cobalt_Black, Mace_Cobalt_Cyan, Mace_Cobalt_Gray, Mace_Cobalt_Green, Mace_Cobalt_Magenta, Mace_Cobalt_Purple, Mace_Cobalt_Red, Mace_Cobalt_Rusty, Mace_Cobalt_White, Mace_Cobalt_Yellow, Mace_Iron_Black, Mace_Iron_Blue, Mace_Iron_Cyan, Mace_Iron_Green, Mace_Iron_Magenta, Mace_Iron_Purple, Mace_Iron_Red, Mace_Iron_Rusty, Mace_Iron_White, Mace_Iron_Yellow, Mace_Thorium_Black, Mace_Thorium_Blue, Mace_Thorium_Cyan, Mace_Thorium_Gray, Mace_Thorium_Magenta, Mace_Thorium_Purple, Mace_Thorium_Red, Mace_Thorium_Rusty, Mace_Thorium_White, Mace_Thorium_Yellow |
| Shield recolors | free (Warrior lean) | Drop | 85 | Weapon_Shield_Adamantite_Black, Weapon_Shield_Adamantite_Blue, Weapon_Shield_Adamantite_Blue_Alt, Weapon_Shield_Adamantite_Cyan, Weapon_Shield_Adamantite_Cyan_Alt, Weapon_Shield_Adamantite_Gray, Weapon_Shield_Adamantite_Green, Weapon_Shield_Adamantite_Green_Alt, Weapon_Shield_Adamantite_Magenta, Weapon_Shield_Adamantite_Magenta_Alt, Weapon_Shield_Adamantite_Purple, Weapon_Shield_Adamantite_Purple_Alt, Weapon_Shield_Adamantite_Red_Alt, Weapon_Shield_Adamantite_Rusty, Weapon_Shield_Adamantite_White, Weapon_Shield_Adamantite_Yellow, Weapon_Shield_Cobalt_Black, Weapon_Shield_Cobalt_Black_Pat, Weapon_Shield_Cobalt_Blue_Pat, Weapon_Shield_Cobalt_Cyan, Weapon_Shield_Cobalt_Cyan_Pat, Weapon_Shield_Cobalt_Green, Weapon_Shield_Cobalt_Green_Pat, Weapon_Shield_Cobalt_Inverse, Weapon_Shield_Cobalt_Magenta, Weapon_Shield_Cobalt_Magenta_Pat, Weapon_Shield_Cobalt_Purple, Weapon_Shield_Cobalt_Purple_Pat, Weapon_Shield_Cobalt_Red, Weapon_Shield_Cobalt_Red_Pat, Weapon_Shield_Cobalt_Rusty, Weapon_Shield_Cobalt_White, Weapon_Shield_Cobalt_Yellow, Weapon_Shield_Cobalt_Yellow_Pat, Weapon_Shield_Iron_Black, Weapon_Shield_Iron_Black_Alt, Weapon_Shield_Iron_Black_Pat, Weapon_Shield_Iron_Blue, Weapon_Shield_Iron_Blue_Alt, Weapon_Shield_Iron_Blue_Pat, Weapon_Shield_Iron_Cyan, Weapon_Shield_Iron_Cyan_Alt, Weapon_Shield_Iron_Cyan_Pat, Weapon_Shield_Iron_Green, Weapon_Shield_Iron_Green_Alt, Weapon_Shield_Iron_Green_Pat, Weapon_Shield_Iron_Magenta, Weapon_Shield_Iron_Magenta_Alt, Weapon_Shield_Iron_Magenta_Pat, Weapon_Shield_Iron_Purple, Weapon_Shield_Iron_Purple_Alt, Weapon_Shield_Iron_Purple_Pat, Weapon_Shield_Iron_Red, Weapon_Shield_Iron_Red_Alt, Weapon_Shield_Iron_Red_Pat, Weapon_Shield_Iron_Rusty, Weapon_Shield_Iron_White, Weapon_Shield_Iron_White_Alt, Weapon_Shield_Iron_Yellow, Weapon_Shield_Iron_Yellow_Alt, Weapon_Shield_Iron_Yellow_Pat, Weapon_Shield_Thorium_Black, Weapon_Shield_Thorium_Black_Pat, Weapon_Shield_Thorium_Blue, Weapon_Shield_Thorium_Blue_Alt, Weapon_Shield_Thorium_Blue_Pat, Weapon_Shield_Thorium_Cyan, Weapon_Shield_Thorium_Cyan_Alt, Weapon_Shield_Thorium_Cyan_Pat, Weapon_Shield_Thorium_Gray, Weapon_Shield_Thorium_Green_Alt, Weapon_Shield_Thorium_Green_Pat, Weapon_Shield_Thorium_Magenta, Weapon_Shield_Thorium_Magenta_Alt, Weapon_Shield_Thorium_Magenta_Pat, Weapon_Shield_Thorium_Purple, Weapon_Shield_Thorium_Purple_Alt, Weapon_Shield_Thorium_Purple_Pat, Weapon_Shield_Thorium_Red, Weapon_Shield_Thorium_Red_Alt, Weapon_Shield_Thorium_Red_Pat, Weapon_Shield_Thorium_Rusty, Weapon_Shield_Thorium_White, Weapon_Shield_Thorium_Yellow, Weapon_Shield_Thorium_Yellow_Pat |
| Sword recolors | Warrior | Drop | 40 | Sword_Adamantite_Black, Sword_Adamantite_Blue, Sword_Adamantite_Cyan, Sword_Adamantite_Gray, Sword_Adamantite_Green, Sword_Adamantite_Magenta, Sword_Adamantite_Purple, Sword_Adamantite_Rusty, Sword_Adamantite_White, Sword_Adamantite_Yellow, Sword_Cobalt_Black, Sword_Cobalt_Cyan, Sword_Cobalt_Gray, Sword_Cobalt_Green, Sword_Cobalt_Magenta, Sword_Cobalt_Purple, Sword_Cobalt_Red, Sword_Cobalt_Rusty, Sword_Cobalt_White, Sword_Cobalt_Yellow, Sword_Iron_Black, Sword_Iron_Blue, Sword_Iron_Cyan, Sword_Iron_Green, Sword_Iron_Magenta, Sword_Iron_Purple, Sword_Iron_Red, Sword_Iron_Rusty, Sword_Iron_White, Sword_Iron_Yellow, Sword_Thorium_Black, Sword_Thorium_Blue, Sword_Thorium_Cyan, Sword_Thorium_Gray, Sword_Thorium_Magenta, Sword_Thorium_Purple, Sword_Thorium_Red, Sword_Thorium_White, Sword_Thorium_Yellow, Sword_Throrium_Rusty |
