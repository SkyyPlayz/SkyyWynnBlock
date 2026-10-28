# Augments - build spec (gear slots: Stat + Elemental augments, real element effects + interactions)

Spec, 2026-10-25; **REVISED 2026-10-27** to Skyy's 8 answers of 2026-10-25 (the last 5 lines of `docs/answered/gear.md`; see "Revision" below). Nothing built. Owner: Skyy (they/them). Where this goes: `research/` (INDEX.md "research"). Answers to "Questions for
Skyy" go to `docs/answered/gear.md` (`python tools/qa_append.py gear ...`); build results to `docs/log/2026-10.md`.
Replaces `research/cloud/Powders-P1-Build.md` + `research/cloud/Powders-Spec-Draft.md` (superseded; their verified code facts and anti-dupe
rules are reused below and marked **P1**). Idea notes: `research/Augments-Idea.md`.
Code facts read from the SET pins of today (`python tools/deploy_set.py --check`: SkyyGear 0.3.46, SkyyClasses 0.1.50, SkyyMobs 0.1.19,
SkyyPets 0.4.18, SkyyAccessories 0.5.32, SkyySacks 0.8.30, SkyyMenu 0.3.47). Vanilla facts read from `Assets.zip` (read-only) today.
Numbers were priced with `tools/balance_model.py` P5 functions (`p5_dps`, `p5_ehp`, `p5_roll`) - read-only import in scratch.
Tier counts, fuse ratio and the new drop numbers of the 2026-10-27 revision are PLACEHOLDERS (rows) until P0 re-runs the model.

## Revision 2026-10-27 - what Skyy's answers changed

| # | Answer (gear.md 2026-10-25) | Change in this spec |
|---|---|---|
| R1 | AUGMENT REMOVAL: "cant take it out. once its in, you can only replace it by placing another on top ... for the elemental ones that fuse, this upgrades it if you place the same type on top." | No unsocket and no refund. Replace = the old augment is lost. Same elemental type on top = fuse / upgrade (2.6). `aug.removeRefund` deleted. Old Q1 closed |
| R2 | TIERS + ZONE ELEMENTS: stat augments 5 tiers (one per zone); elemental augments 10 tiers, fused up; drop at the tier of the zone you are in; elemental mobs drop more of their element; one primary element per zone (Zone 1 = Earth) with a higher drop chance even from non-elemental mobs; some mobs of every element in every zone; survey more elemental mobs | Elemental = 10 tiers (2.2, 2.4, 4.1); drop rules + primary element table (2.4); mob survey (1d); round A3 grows (6.1). Old Q2 closed |
| R3 | GATHERING AUGMENTS: "yes! the amount of slots is based on the rarity of the item." | Gathering armor gets slots from its rarity (2.5). Old Q5 closed |
| R4 | POISON AUGMENT: "add it as an augment. but its a weapon modifier. NOT an element." | Poison = a third slot type, MODIFIER, weapons only, no Power, no element Defence, out of the reaction matrix (2.2, 4.1, 5.1-5.2). Old Q3 closed |
| R5 | RAIN = WET: "Yes, with a setting" | `elem.rainWet` stays a row (5.1). Old Q7 closed |
| R6 | REACTION TREE NODES: "Yes, later" | later class-tree nodes strengthen reactions; not in this spec's rounds. Old Q8 closed |
| R7 | TEMPO / ATTACK SPEED: "Build Attack Speed now" | Attack Speed becomes a live gear stat `as` in its own first round A0; Tempo uses it from day one (3.2, 6.1). Old Q4 closed |
| R8 | Name (popup 2026-10-25): "Augments (Recommended)" | name settled (2.1). Old Q6 closed. Q9 Resonance was not asked: default later, not v1 (stays a default) |

Opens that came out of the revision: section 7 (N1-N8, each with a default; the build uses the default).

## 0. Decisions this spec follows

| # | Source | Line (short) | Where it lands |
|---|---|---|---|
| D1 | gear.md 2026-10-25 AUGMENTS REPLACE POWDERS | "gear has augment slots ... call them something else ... two types, stat buffs, and elemental ... fuse low level ... into higher ... on weapons they add damage, and on armor they give defense ... have to choose between them ... each buff augment gives 2 stats ... armor, ... weapons, ... tools ... fire will set the enemy on fire, lightning can stager them. air does more knock back ... water would put out a burning enemy, but lighting and ice are more effective against a wet enemy. wind and fire combo ... increasing the intensity and length of the fire ... i want all the elements to interact realistically." | whole spec |
| D2 | gear.md 2026-10-11 GEMS | "most gear has 1 gem slot. legendarys, UTs and specials have between 2 and 3 ... slots cab be added and removed ... gems DO NOT have levels or rarities" | socket table 2.5; add / remove socket 2.6; the "no levels" part only partly kept (Q2) |
| D3 | gear.md 2026-10-23 POWDERS REMOVAL + 2026-10-25 AUGMENT REMOVAL | "Destroyed (Recommended)"; "cant take it out. once its in, you can only replace it by placing another on top" | no removal at all; replacing destroys the old augment (2.6) |
| D4 | gear.md 2026-10-18 ELEMENTS Q1-Q10 + classes.md 212 (IMBUE ALL 5) | Imbue picks 1 of 5 out of combat; charms weak -> powerful; pets add element only if the weapon deals it; per-element hit popups; Defence ON; mob Resist -25 / Weak +25 / boss -50, never immune; plates show the mob's OWN element + strong/weak + reactions charts; Poison Wynn-style X/Ys, no stagger, stacks; "Reactions: later, as tree nodes" | 4.3 no double count; 5 the engine; **Q6 "later" is overridden by D1** (Skyy now wants interactions built in) - tree nodes can still strengthen them later (Q8) |
| D5 | elem1 (docs/log 2026-10-23 01:00 / 02:05) | live: Mobs 0.1.17 element table + plates, Gear 0.3.39 element damage / Defence / Poison % over 10 s / per-element hits, Classes 0.1.46 Imbue via gear:imbue + `classes:fn:dot`, Pets 0.4.10 pet elements, Accessories 0.5.32 element + Prism charms (`Skyy_Talisman_*` / charm lines), Menu 0.3.45 charts | all reused as is; this spec adds sockets + the states engine |
| D6 | gear.md 2026-10-22 UT BANDS + 10-18 UT = ZONE ALLOY TIER | UTs sit at the END of their zone | UT socket rows 2.5 |
| D7 | PROJECT-RULES 4 tier tags + Rarity colours + tooltip layout (2026-10-24) + Style Guide 15 | "T3 Augment - ..." first; rarity colour on icon + popup title; Pets-style sections | 2.3, 2.8 |
| D8 | PROJECT-RULES 4 four power sources; targets.md 137 split 35 / 30 / 20 / 15 | augments are part of the GEAR shares (weapon / armor / tool) | 3.1 budget |
| D9 | PROJECT-RULES 2 "Order: vanilla -> existing mod -> build only what we need" (Skyy 2026-10-24) + "check for an existing mod BEFORE building" | section 1 | survey |
| D10 | gear.md 2026-10-22 CRAFTED ITEMS NEVER UT / MYTHIC; 2026-10-18 SOUL CAGE "use the worst one" | augments are plain items; recipes take the lowest tier match | 2.4 |
| D11 | Menu-Pattern M3 (Anvil = sub-tabs) + HANDOFF 2 UI rules + "replace commands, never add extra" | Anvil > Augments sub-tab, no new command | 2.7 |
| D12 | PROJECT-RULES 4 no dev gates; everything a server owner changes = Server Setup | default ON; every number a row | 6.4 |
| D13 | gear.md 2026-10-25 AUGMENT TIERS + ZONE ELEMENTS | "the buff augments are 5 tiers. one per zone. but elemental ones have 10, and can be fused together ... they drop the tier of the zone your in, so zone 3 drops T3 ... i want some mobs of every element in every zone. but i want a primary element per zone, and a zone per element eventually. so zone 1 would be earth ... the earth augment drop chance would be higher there. even when fighting non elemental monsters ... look for more monsters of different kinds, for more elemental monsters. like water monsters we can put in the lakes and rivers. more flying monsters for wind and lighting" | 2.2, 2.4, 4.1, 1d |
| D14 | gear.md 2026-10-25 AUGMENT REMOVAL | (see D3) | 2.6, 2.7 |
| D15 | gear.md 2026-10-25 GATHERING AUGMENTS | "yes! the amount of slots is based on the rarity of the item." | 2.5 |
| D16 | gear.md 2026-10-25 POISON AUGMENT | "add it as an augment. but its a weapon modifier. NOT an element." | 2.2, 4.1, 5 |
| D17 | gear.md 2026-10-25 popups RAIN / TREE NODES / TEMPO | Rain Wet with a setting; tree nodes later; "Build Attack Speed now" | 5.1, 6.1 A0, 3.2 |

## 1. Survey first (PROJECT-RULES 2)

### 1a. Vanilla (Assets.zip, read today)

| Need | Vanilla has | Use |
|---|---|---|
| Gem / socket items | 7 gems `Rock_Gem_Diamond / _Emerald / _Ruby / _Sapphire / _Topaz / _Voidstone / _Zephyr` (ore blocks, Gemstone collection in our Collections spec, booster recipes use 5 of them); 9 crystals `Ingredient_Crystal_*`; essences `Ingredient_Fire / _Water / _Ice / _Lightning / _Void / _Life_Essence`; `Ingredient_Sac_Venom`. **No socket system on gear.** | stat augments are made from gems, elemental ones from essences / crystals / venom (2.4). Icons / models: build-time recolours of the gem + essence models (P1 Sigil pattern, nothing vanilla committed) |
| Vanilla runes | `Rune_*` ability runes + modifiers (`Rune_Convert_Lightning`, `Rune_Convert_Wind`, `ConvertElement`, slot "Support") = the vanilla ABILITY rune system, not gear sockets | not used (name clash avoided: "Runes" stays the class-rune word, classes.md 192) |
| Damage causes | `Server/Entity/Damage/`: Earth, Fire, Ice, Lightning, Water, Wind, Poison, all Parent `Elemental` (text colours Fire #FF6B2B, Water #2B5FCC, Lightning #FFE14D, Wind #A5D8F5, Earth #B2C96B) | DoT / reaction damage uses the element's cause (already done by Classes 0.1.46 via `DamageCause.getAssetMap()`) |
| Burning | `vanilla status effect Burn` (Parent `Burn_Template`: tint #cf2302, `Effect_Fire` particles, ModelVFX `Burn`, burn sounds, icon, 5 Fire / s, 3 s). `Burn_Template` **already refuses to apply while the target is in Water** (`ApplyConditions InFluid Water Inverse`) and with `Immunity_Fire`; `Lava_Burn`, `Flame_Staff_Burn` | Burning look = a damage-free child `Skyy_Elem_Burning` (Parent `Burn_Template`, `BaseDamage Fire 0`) so vanilla's "no fire in water" rule comes free; damage stays our DoT (probe X1) |
| Frozen / Chill / Slow | `vanilla status effect Freeze` (DisableAll movement, `Effect_Snow`, ModelVFX `Freeze`), `Ability_Frost_Chill` (speed x0.6, Tag Element Water), `Ability_Frost_Freeze`, `Ability_Frost_Slow`, `vanilla status effect Slow`, `Immunity_Freeze`, `Immunity_Slow` | Frozen = Classes' existing `freezeOne` (vanilla Freeze + boss clock); Chill = Classes' existing `spdId` slow effect |
| Stagger / stun | vanilla status effect `Stun` (Assets.zip Status folder), `Hit_Interrupt_Flinch`, `Hit_Interrupt_Stunned`, `Hazard_Electric_Stun` (yellow tint + `Hazard_Electric_Stun` particles, but 3 s DisableAll + no abilities - too strong for a hit), `Bomb_Explode_Stun` | Thunder flinch = `Hit_Interrupt_Flinch` (probe X2) + the electric particles only; Earth Quake = Classes' existing `stunMob` |
| Wet | **none** (no effect, no state; only Burn's InFluid check and rain ambience) | we build Wet (5.1) |
| Knockback | Classes `push()` + `AbilCfg.PUSH_PER_BLOCK` (live), `Root.json` `KnockbackMultiplier` field | Air knockback = Classes' existing Gust push |
| Poison | `vanilla status effect Poison`, `Poison_T1..T3`, `Immunity_Poison`, particles `Effect_Poison`, `Status_Poisoned`, `Impact_Poison`; Thorium armor resists Poison | already used by Gear 0.3.39 Poison |
| Weapon auras (on the held item) | `Ability_Wind_Buff.json` = Particles on `TargetEntityPart PrimaryItem` / `TargetNodeName Handle` (`Buff_Windstrikes`); particle systems `FireSword`, `Lightning_Sword`, `Buff_ImbuePoison`, `Buff_Windstrikes`, `Weapon_Frost_Mist`, `Embers` | element aura on a weapon with an elemental augment = our `Skyy_Aug_Aura_<E>` effects built on that pattern (probe X3) |
| Hit / reaction particles (all exist, `.particlesystem`) | Fire `Impact_Fire`, `Fire_AoE_Spawn`, `Embers`; Water `Water_Splash_Soft`, `Water_Dripping`, `Splash`; Ice `Impact_Ice`, `Ice_Blast`, `Block_Break_Ice`, `Ability_Ice_Explosion`; Thunder `Lightning`, `Beam_Lightning2`, `Hazard_Electric_Stun`; Air `Wind`, `Ability_Windstrikes`, `Example_Tornado`; Earth `Block_Hit_Stone`, `Ability_GroundSlam_Spike`, `Block_Land_Soft_Dust`; Steam `Goblin_Decorative_Steam`; Poison `Impact_Poison`, `Status_Poisoned` | section 5 table |

### 1b. Existing mods (Skyy's Mods folder, read-only, + CurseForge)

| Mod | Licence | What it has | Verdict |
|---|---|---|---|
| **Socket Reforge** (iRaiden_, CurseForge, 1.4.5, Hytale 0.7, needs HyUI) | **MIT** | Socket Punch bench (up to 4-5 sockets), 6 essences (Fire / Ice / Lightning / Life / Void / Water) as socket fillers, same-type stacking raises tier, "Resonance" (essence ORDER in a full item = hidden bonus), loot with broken sockets, a hammer clears sockets (10 % durability, may break a socket) | **Learn, do not pack**: it duplicates SkyyGear's Anvil reforge and would add a second socket system on our item docs (no-duplicates rule). Learn: Resonance (N8 - a later bonus), "socketed loot" (drops may come with a pre-filled augment, 2.4), clear-by-tool idea (we keep a menu button). MIT means its code may be read and folded if ever useful - not needed |
| RuneCore (kukkie, CurseForge, 1.0.13, Hytale 0.6) | ARR / CC BY-NC (page contradicts itself) | status effects (Burn, Frozen, Electrified, Poison ...), 20 essences, no element reactions, API in testing, 0.6 only | skip (no reactions, wrong game version, unclear licence) |
| Aetherhaven 4.0.3 (in Mods folder) | ARR (Licence-Audit 69) | Jewelry: `JewelryGem`, `JewelryGemTraits`, `ElementAlignment`, rolled traits, tooltip sync | design reference only (gem -> trait table idea = our stat-augment pairs) |
| SimpleEnchantments 1.2.1 (in Mods folder) | not audited | enchanting table, Freeze / Burn / Poison / Knockback / Elemental Heart enchant systems | skip (enchants = another gear-buff system; duplicate of reforge + augments) |
| StunningCombat 1.4.0 | not audited | `DamageTypeGroups/Elemental` (Fire, Ice, Water, Lightning, Void, Life), stun / crit | skip; note: a DamageTypeGroups asset folder exists in 0.7 (could group our causes later) |
| **Perfect Parries** (IN THE PACK) | ARR | posture / stagger (`PP_NPC_Staggered`) | no clash as long as our Thunder flinch is short and boss-limited (5.4); never reuse their effect id (pack rule) |
| Hylamity, Starblight, Spark Lantern Pets, DynamicSeasons | various | "Wet" exists only as a worldgen density / slime name / a pet state / a soil check | nothing to reuse |
| EndlessLeveling, roguetale | ARR | the word "Augment" for level-up / run cards (not in our pack) | name note only (2.1) |

Result: **no mod gives gear sockets + element reactions that fits; vanilla gives the materials, causes, Burn / Freeze / Slow / Stun /
Poison looks and particles; we build only: the socket data + Anvil page (SkyyGear), the items (SkyyGear), Wet + the reaction engine
(SkyyClasses, on its live statuses).**

### 1c. What our mods already have (reuse, do not rebuild)

| Mod (pin) | Live today | Reuse |
|---|---|---|
| SkyyGear 0.3.46 | `STATS` lines `fEarth..fAir` "% of the hit" (max 6), `rElem`, `dEarth..dAir` element Defence (max 10, `S/(S+D)`, S = `elem.defScale` 100), `poison` (w + a, % over `poison.time`); `GearStats.totals0` sums rolled lines through `addModsE` (pet gate reads it); `gear:fn:elemDef`, `gear:fn:elemTotals`, `gear:imbue:v2`; per-element coloured popups; item doc `"SkyyGear"` BsonDocument whose `reforge` / `levelUp` clone keeps unknown keys (**P1**); Anvil sub row Reforge `mode:0` / Identify `mode:5`, `mode:7` free (**P1**, re-grep); Sigil item pattern (`SIG_ITEMS`) | sockets + augment items + Anvil tab live here |
| SkyyClasses 0.1.50 | `ELN` Fire Water Earth Thunder Air Poison / `ELS` Burn Chill Stagger Shock Gust Poison; `statusOn(...)` (Burn DoT 10 % 4 s 3 stacks, Chill -15 % 3 s -> 3 in 3 s = Freeze 1.5 s via `freezeOne` + boss clock, Earth every 3rd hit 0.4 s stun + -10 % Defence 4 s, Shock 40 % jump to 1 enemy in 3 + 5 % taken 3 s, Gust +1 block knockback / bosses immune, Poison 8 % 6 s); one DoT engine `dotOn` / `classes:fn:dot`; `effect()` applies any EntityEffect by id; `particle()`; bossCc 50 %; rows `ab.Elements.*` | the element STATES ENGINE goes here (section 5) - it already owns every status |
| SkyyMobs 0.1.19 | `elem.mobs` table, `mob:fn:elem`, `mob:fn:elemOf`, `mob:elem:wheel` Earth>Thunder>Water>Fire>Air, mob element share of hits on players, plates | mob own element = which state it can't get (5.3); mob element hits put states on players (5.5) |
| SkyyPets 0.4.18 / SkyyAccessories 0.5.32 | pet element dmg (weapon-gated) + Defence; element charm ladders T1-T5 + Prism / Elemental Power | untouched; they add DAMAGE / DEFENCE, never Element Power (4.3) |
| SkyyMenu 0.3.47 | Character > Skills > ELEMENTS charts (strong / weak + "Reactions: later") | Reactions chart becomes the real matrix (6.1 round A4) |

### 1d. Elemental mob survey (added 2026-10-27, Skyy's D13 "look for more monsters of different kinds")

Order per PROJECT-RULES 2: vanilla first, then mods, then build. Sources: `Assets.zip` NPC role names (read-only, today); file NAMES + `manifest.json`
only of the zips / jars in Skyy's Mods folder (nothing extracted or written); CurseForge pages (licences as the page says; "not stated" = the
page / search gave none, "not audited" = not in `research/Licence-Audit.md`). What we already have: SkyyMobs 0.1.19 puts an element on EXISTING
mobs by table (`elem.mobs`, wheel Earth > Thunder > Water > Fire > Air, plates, mob element hits; docs/log 2026-10-22 23:00 + 2026-10-23 01:00
elem1) - it adds no new mob bodies, so a mob mod duplicates nothing of ours; it only supplies bodies to put an element on.

**Vanilla (use first):**

| Element | Vanilla mobs that already fit (NPC roles) |
|---|---|
| Fire | `Emberwulf`, `Spirit_Ember`, `Golem_Crystal_Flame`, `Golem_Firesteel`, `Dragon_Fire`, `Slug_Magma`, `Snail_Magma`, `Toad_Rhino_Magma`, `Shellfish_Lava` |
| Water | `Frostgill`, `Eel_Moray`, `Shark_Hammerhead`, `Tang_Lemon_Peel`, `Crocodile`, `Fen_Stalker` (sea / river / lake bodies; few are hostile) |
| Earth | `Golem_Crystal_Earth`, `Golem_Crystal_Sand`, `Lizard_Sand`, `Spirit_Root`, `Skeleton_Sand_*` / `Zombie_Sand` (desert) |
| Thunder | `Spirit_Thunder`, `Golem_Crystal_Thunder` |
| Air | `Feran_Windwalker` (weak fit), `Bat` / `Bat_Ice`; no real wind mob and no flyer set |
| Ice (not one of our 5 - Chill is a Water state) | `Golem_Crystal_Frost`, `Spirit_Frost`, `Snail_Frost`, `Dragon_Frost`, `Bat_Ice`, `Zombie_Frost`, `Skeleton_Frost_*` -> map to Water (Chill) |

Gaps vanilla leaves: hostile **Water** mobs for lakes / rivers, **Air** and **Thunder** flyers, enough **Earth** variety for a whole zone.

**Mods:**

| Candidate | Author | Licence | What it adds (elemental part) | In Mods folder | Duplicates SkyyMobs elements? | Verdict |
|---|---|---|---|---|---|---|
| **Slime Mobs!** 1.1.4 (CurseForge "lizards-mobs") | lizard (manifest) / bigfknlizard (page) | not stated, not audited | Fire, Ice, Water, Green, Yellow, Ghost, Bomb, King slimes; drops Fire / Ice / Water / Life Essence; Fire slimes in wastes / volcano, Ice in tundra, **Water slimes on the shores of every zone** | yes | no (new bodies); its essence drops overlap our essence-based elemental recipes (2.4) - set drops through our table | **PACK candidate** for Water / Fire bodies if the licence allows (check the page + ask the author); else learn the spawn rules. Compare with Visscas Slime Stuff first (one slime mod only) |
| **More Golems** 1.0.1 | QuickBASIC | All Rights Reserved | wild Earthen, Ember, Sandswept, Thunder golems + Heartfelt, Voidsworn, Snowy; drop 15 crystal shards + a gem | no (web) | vanilla already has Golem_Crystal_Earth / Flame / Thunder / Frost / Sand - mostly re-skins; the gem drops would feed our stat-augment gems | **Skip** (vanilla covers it; ARR) |
| **Will-O-Wisp** | lonegreyw | All Rights Reserved (modpack use stated OK, no asset use without permission) | 4 wisp enemies: Cyan Z1, White Z2, Green Z3, Orange Z4, + a wisp light pet / egg | no (web) | no; the wisp pet would duplicate SkyyPets | **Learn / ask**: a flying light body for Air / Thunder; ask the author before packing; the pet part cannot be hidden -> pick one |
| **The Lost Worlds** 0.5.1 | MrZip | not stated, not audited | sky islands with `Spirit_Thunder_Sky`, Sky Guard, Void Guard | yes | no | **Learn** (Thunder / Air flyer behaviour); no pack (world mod) |
| **Better Mob Expansion** 3.5 | Frah | GPLv3 (Licence-Audit) | ~30 mobs in Zone 1-4 spawns incl. `BME_Airdrop` Frost / Sand, `BME_Elite_Skeleton` Frost / Sand, Fairy, Fen / Elder Crocodile | yes (pack row, OFF until updated for 0.7) | no | **Already decided in the pack** (Skyy 2026-10-09). Map its Frost -> Water, Sand -> Earth through `elem.mobs`; its Airdrop flyers are the closest Air body we have |
| **PJ-ForgottenCreatures** 1.3.2 | Pedrijoe | not audited | Saurian warriors incl. `SaurianWarriorBlueIce`, `SaurianWarriorRedMagma`, Bramblekin, Mushee colours | yes | no | **Learn**: ready-made Water (ice) / Fire (magma) variants of one body; licence check first, no pack yet |
| **Elemental Frogs** | EpicNNG | All Rights Reserved | 14 frogs (Water, Ice, Poison, Sand, Wood, Slime, metals ...), swamp / pond | no (web) | no; material frogs, not elements | **Learn** (Water / Poison frog bodies for lakes); ARR -> ask before packing |
| **Mermaids** 4.1.1 | Siren | not audited | player mermaid transform + mermaid NPCs and companion fish in oceans | yes | no | **Skip** (player transform is not our design); spawn idea only |
| **Hydra StormBosses** 1.0.0 | Hydra | not audited | storm boss encounters, summon beacons (no NPC files in the zip) | yes | no | **Learn** (Thunder / Air boss framing) when we build zone element bosses; overlaps DungeonBosses - one boss mod only |
| **Kami's Ore Golems** 1.0.7 | Kami | not stated | Earth and Volcanic ore golems (copper ... adamantite) in volcanic caves Z1-4 | yes | no; but ore drops would bypass our ore / collection economy | **Skip** for elements |
| **FireMobs** 1.0.2 | HytaleZX | All Rights Reserved | one mob: Fire Queen (Zone 4 wastes), more "planned" | no (web) | no | **Skip** (too small, ARR); re-check later |
| **Element** ("Hytale Elementary" 1.4) | JustLama | All Rights Reserved | elemental swords + very rare drops from "elemental mobs" (none named) | no (web) | duplicates our gear + augments | **Skip** |
| **Four Elements** | not read | not read | player Air / Earth / Water / Fire bending | no (web) | duplicates Classes' element abilities | **Skip** |
| **Fables** (player.games) | not read | not read | elite modifiers + elemental-affinity mobs with core drops | no (web) | duplicates the SkyyMobs element table | **Skip** (concept only) |
| EndlessEliteMobs 5.0.7, Bio's Kobolds 1.4.1 (Fire / Snow / Sand kobold elites), Taintedroots, Aures Rare Monsters, Soulslike Bosses, UnstableRifts, hyrifts | various | various | elites / bosses / re-skins, no element system | yes | no | **Skip** (no element value beyond names) |

**Result:** no mod ships a themed elemental roster (Earth / Thunder / Water / Fire / Air) with hostile lake / river and flying bodies. Plan:
(1) tag vanilla bodies first (table above) and BME's Frost / Sand / Airdrop variants through `elem.mobs`; (2) pack **Slime Mobs!**
for shore Water + Fire slimes if its licence allows; (3) **build only the gaps** - a hostile lake / river Water mob and Air / Thunder
flyers (vanilla `Bat` / `Spirit_Thunder` bodies re-roled or re-skinned, learning from Will-O-Wisp / Lost Worlds, never copying files) - as part of
round A3 (6.1); (4) ask the Will-O-Wisp, Elemental Frogs and More Golems authors only if we later want their bodies. Record the pack choice
in PACK.md and run the no-duplicates check (slime mods, golem mods) before anything is packed. Licence and feature facts here come from the
CurseForge pages / search snippets of 2026-10-27 and may be stale; re-read the page before packing.

## 2. The system

### 2.1 Name

| Option | For | Against |
|---|---|---|
| **Augments** (recommended default) | Skyy's own word; says what it does; no clash inside our pack (Sigils, Runes, Shards, Dust, Charms, Talismans are taken) | EndlessLeveling / roguetale use "augment" for cards (not in our pack) |
| Infusions | fits elements ("Fire Infusion IV") | odd for stat pairs; close to "Imbue" (the Spellblade ability) |
| Facets | gem-like, unique | players may not get it at once |

Items read "Brute Augment III" / "Fire Augment VII"; the socket is an "augment slot". Name settled by Skyy's popup 2026-10-25 ("Augments (Recommended)").

### 2.2 Kinds and ids (all owned + lang-written by SkyyGear)

Stat and Poison augments: tier n = 1..5 = the zone (Z1 .. Z5). **Elemental augments: tier n = 1..10** (Skyy: "elemental ones have 10"); a zone drops/crafts the tier of the zone (Z3 = T3, 5 = most), T6-T10 come ONLY from fusing (2.4). Roman in names. Ids `Skyy_Aug_<Kind>_<n>`.

| Type | Kind (id part) | Fits | Gives (2 stats / element) | Made from (2.4) |
|---|---|---|---|---|
| Stat - weapon | `Brute` | weapons | Strength + Crit Damage | Ruby |
| Stat - weapon | `Edge` | weapons | Damage % + Crit Chance | Topaz |
| Stat - weapon | `Precision` | weapons | Crit Chance + Crit Damage | Voidstone |
| Stat - weapon | `Arcane` | spell weapons (slot "s") | Magical Power + Crit Damage | Sapphire |
| Stat - weapon | `Tempo` | weapons | Attack Speed + Damage % (Attack Speed is made live first, round A0) | Zephyr |
| Stat - armor | `Bulwark` | combat armor | Defense + Health % | Diamond |
| Stat - armor | `Warrior` | combat armor | Strength + Defense | Ruby |
| Stat - armor | `Swift` | combat armor | Speed + Mana % (new gear key `manap`, delivered like SkyyPets' `mana`) | Zephyr |
| Stat - armor | `Vital` | combat armor | Health % + Health Regen % | Emerald |
| Stat - armor | `Sage` | combat armor | Magical Power + Mana % | Sapphire |
| Stat - tool | `Prospector` | lifelong tools + gathering armor (2.5) | Breaking Speed % + that skill's Fortune | Emerald |
| Stat - tool | `Scholar` | lifelong tools + gathering armor (2.5) | that skill's Wisdom % + Fortune | Topaz |
| Stat - tool | `Delver` | lifelong tools | that skill's Power % + Breaking Speed % | Diamond |
| Elemental (10 tiers, fuse) | `Earth` `Thunder` `Water` `Fire` `Air` | weapon: element damage + Element Power; armor: element Defence + status resist | 4.1 | Green crystal / Lightning ess. / Water ess. / Fire ess. / Cyan crystal |
| Modifier (5 tiers, no fuse; D16) | `Poison` | **weapons only** (it is NOT an element: no Power, no element Defence, no reactions) | Poison % (the live `poison` key) | Venom Sac + that zone's material (N4) |

13 stat kinds x 5 + Poison x 5 + 5 elements x 10 = **120 items** (was 95). Tool kinds read the skill from the item they sit in (a pickaxe -> Mining Fortune,
a hatchet -> Foraging, hoe / Harvester -> Farming; a multitool socket counts for both sides, as the multitool rule says "no drawbacks").

### 2.3 Tiers, tier tags, rarity

- `tools/tier_tags.py`: `OWN_LADDERS += "Augment"` -> `"T3 Augment"`; TT_VERSION stays "3" (a new word renumbers nothing - **P1**).
  Flavor text first phrase = the tag: `T3 Augment - Brute (weapon).`
- Rarity colour = the item `Quality` by tier. Stat / Poison (5 tiers): T1 Common, T2 Uncommon, T3 Rare, T4 Epic, T5 Legendary. Elemental (10 tiers): T1-2 Common, T3-4 Uncommon, T5-6 Rare, T7-8 Epic, T9-10 Legendary (icon frame + popup title per
  the 2026-10-24 rule; builder maps to the Gear quality ids it already uses). Augments never roll a rarity (D2 "no rarities").
- Sort by tier then kind (Wynn element order for elementals) everywhere: Anvil list, Bazaar, shop, recipe lists.

### 2.4 How you get them

| Route | Stat augments (5 tiers) | Elemental augments (10 tiers) |
|---|---|---|
| **Craft** (main), vanilla Alchemy Bench recipes (asset only, inputs drawn from the Magic Bags - **P1** 2.4) | T1 = 1 gem + 4 of that zone's ore / bar; T2-T5 = 1 gem + that zone's Enchanted material (the zone gate = the collection ladder) - each tier crafted fresh, never fused | T1 = 2 essence / crystal; **fuse** at the bench: `aug.fuse.n` (default 2, N1) of tier t -> 1 of t+1, up to T10. Zone-5 drops are T5, so T6-T10 are fuse-only |
| **Fuse in the slot** (R1) | - (a stat augment on a filled slot simply replaces it) | place the SAME element, SAME tier on the filled slot -> the slot goes up one tier (see 2.6, N2) |
| **Drops** (D13): the augment is the tier of the ZONE you are in (Zone 3 mobs drop T3) | elites / mini bosses / dungeon bosses: rare T(zone) stat augment; full bosses guarantee 1 | per kill, in order: (a) **element mobs** (`elem.mobs`) drop THEIR element at x`aug.drop.elemMob` (default x3 vs base); (b) the **zone's primary element** drops from ANY mob in that zone at x`aug.drop.primary` (default x2) - even non-elemental ones; (c) base chance for the other elements. Elites x3, bosses 1-2 |
| "Socketed loot" (learned from Socket Reforge) | a dropped Legendary+ item may come with 1 slot pre-filled (row `aug.loot.prefill` 10 %) | same |
| Bazaar / AH | tradable plain items (no metadata); Bazaar entries, Combat bag (`homeOf` startsWith `Skyy_Aug_` -> Combat, **P1** 8) | same |
| Traveling Merchant | T1 only, rotating | T1 only, rotating |

**Primary element per zone (D13; only Zone 1 = Earth is Skyy's words, Z2-Z5 are the default order of the existing mob wheel, N3):**
Z1 Earth, Z2 Thunder, Z3 Water, Z4 Fire, Z5 Air (Z5 = the dinosaur caves, Lv 60-75). "Eventually a zone per element" = this table. Every zone also has
some mobs of every element (SkyyMobs spawn mix, 6.1 A3); the primary element just makes up most of the common mobs and its augment drop rises.
Rows `aug.zoneElement.<1..5>` (editable, so Skyy can reorder), `aug.drop.base`, `aug.drop.elemMob`, `aug.drop.primary`.

Value check: T1 elemental ~ 225 coins of essence (**P1**); with 2:1 fusing a T10 = 512 x T1, with 3:1 it would be 19,683 x T1 (too much for 10
tiers, hence N1). Skyy knows fusing in Zone 1 up to about T5 is "a waste as your weapon wont level with you, but it works" - so the weapon
numbers (4.1) are NOT zone-gated: any tier works on any weapon.

### 2.5 Slots (one pool per item - you choose Stat OR Elemental per slot)

Saved count is NOT stored: `slots(item) = table[rarity][kind] + augAdd` (**P1** 3.1), so a Sigil rarity upgrade or a Server Setup edit
applies at once and **existing gear gets slots with no migration**.

| Rarity (`R_IDS`) | Weapon | Each combat-armor piece | 4-piece set |
|---|---|---|---|
| normal | 1 | 0 | 0 |
| unique | 1 | 1 | 4 |
| rare | 2 | 1 | 4 |
| legendary | 2 | 2 | 8 |
| fabled | 3 | 2 | 8 |
| mythic | 3 | 3 | 12 |
| set | 1 | 1 | 4 |
| untiered | 2 | 1 | 4 (UT rows may override as their trade-off, D6) |

**Gathering armor (Mining / Foraging / Farming / Fishing; D15): slots come from the piece's RARITY with the Each-combat-armor-piece column above** (Skyy: "the amount of slots is based on the rarity of the item"; N5 if a piece has no rarity). Lifelong tools: no answer yet, default = by the tool's tier on the 15-step ladder: T1-T3 1, T4-T9 2, T10-T15 3 (N5).
Unidentified items and bags: 0. Lowering a table keeps saved augments; the extra ones show grey "(no slot)" and count nothing (**P1**).

### 2.6 Socket / replace / fuse rules (R1: there is NO removal)

| Action | Rule |
|---|---|
| Add an augment to an EMPTY slot | Anvil > Augments; the augment must fit the item kind (2.2 "Fits"); any element in any slot; atomic take-then-write with re-read + give-back on mismatch, bag take via `sacks:fn:take` / `commit`, stack split like Reforge (**P1** 7.1). Smithing XP `skill:fn:addxp` by tier (5 / 10 / 20 / 40 / 80; elemental T6-T10 use 80 + 10 per step) |
| Place a DIFFERENT augment on a filled slot | **replaces it; the old augment is destroyed** (Skyy: "you can only replace it by placing another on top"). Confirm dialog "The old augment will be destroyed" |
| Place the SAME elemental type on a filled slot | **fuse**: same tier -> the slot goes up one tier and one item is used (N2 for lower / higher tiers). Stat and Poison augments do not fuse: the same kind just replaces |
| Take an augment out | **not possible** - no REMOVE button, no refund row (`aug.removeRefund` deleted). Only destruction paths: replace, salvage / sale of the item (confirm "this item has 2 augments") |
| Add a slot | +1 max (`aug.extraSlots` 1): coins (2 x the Lv-10 reforge base for the rarity) + Smithing Lv 10 (**P1** rows) |
| Remove a slot | only an EMPTY slot the player added, no refund (kept from D2 "added and removed"; there is nothing to take out, N6) |
| Reforge / level-up / Sigil / Upgrade / tier-up of gathering gear | keep `aug` + `augAdd` (doc clone; harness), a gathering-armor tier-up carries them to the new piece (gear.md 2026-10-24 "keeps its upgrades") |
| AH / trade / Vault / Requip | carry the doc (UNVERIFIED X6) |

### 2.7 UI (Menu-Pattern, kit 1.7 hub page, HANDOFF 2)

**Crafting hub > Anvil > Augments** = the third Anvil sub-tab (`mode:7`), no new command (`/reforge` and `/smithing` open the Anvil).
Layout = **P1** section 7 (item list left filtered to `slots > 0`, held item + slot row top right as `ItemGridSlot new ItemStack(id, 1)`,
owned-augment scroll list right middle with "what it gives on THIS item", buttons ADD (becomes REPLACE on a filled slot, confirm; becomes FUSE for the same element + tier) / ADD SLOT / REMOVE SLOT (empty added slots only); no unsocket button,
result line). Added: a STAT | ELEMENTAL | MODIFIER filter (three small sub buttons) over the owned list, and each row shows "Fits: weapon" red when it
does not fit. Bench fusing is the Alchemy Bench recipe (vanilla first); the page shows "2 make the next tier at the Alchemy Bench" (the live `aug.fuse.n`); fusing into a filled slot is done on this page.

### 2.8 Tooltips (Style Guide 15 colours, Pets-tooltip sections, gear order rule 2026-10-24)

Item tooltip of a socketed weapon (after the stat lines, before set / flavor):
```
AUGMENTS  2 / 3                                   <- gold heading
 [Brute III]  +2.7 Strength  +3.2% Crit Damage     <- pip in the tier rarity colour; names #d6e4ee, values green bold
 [Fire IV]    +0.9% Fire Damage  Burning (Power 4) <- element name in its colour; 10-tier Roman up to X
 [ empty ]                                         <- dim grey
 [Poison III] +1.2% Poison over 10 s                  <- modifier, green (not an element colour)
ELEMENT POWER  Fire 4                              <- only when > 0; "what it does" one line: "Hits set enemies Burning"
```
Augment item tooltip: title in tier colour; `T3 Augment - Brute (weapon)`; GIVES (values); FITS (weapon / armor / tool); USE ("Crafting >
Anvil > Augments", yellow); HOW ("2 make the next tier at the Alchemy Bench" for elementals, grey; the number is the live `aug.fuse.n`). Armor elementals add "Burning on you
lasts 20% less (at full set)" style line. Every number in the item tooltip is the live Server Setup value (signature includes `aug`).

## 3. STAT augments - numbers

### 3.1 Budget (four power sources, D8)

Augments live inside the gear shares. Targets (priced with the P5 model on a Legendary weapon + armor kit, M melee class):
**one T5 weapon slot = +4.2 % DPS**, **one T5 armor slot = +1.2 % EHP (or the same value split DPS / EHP)**, so a full Mythic kit
(3 weapon + 12 armor slots) = about **DPS x1.13, EHP x1.15** - about one rarity step, never more. Tools: one T5 slot = about +2 % of that
zone's Fortune budget (targets.md 1.1). P0 (6.1) re-runs `--power` and the "unluckiest 1 in 10" upgrade clock with these.

Tier scale: T1 40 %, T2 55 %, T3 70 %, T4 85 %, T5 100 % of the T5 value. Values are per slot, flat (NO slot power - a helmet slot gives the
same as a chest slot, so players can read it), one decimal shown.

### 3.2 Tables (T5 value per slot; T1-T4 by the scale; keys = SkyyGear `STATS`)

| Kind | Stat 1 (T5) | Stat 2 (T5) | Model gain per T5 slot |
|---|---|---|---|
| Brute (w) | Strength `str` +4.0 | Crit Damage `cd` +4.8 % | DPS +4.2 % |
| Edge (w) | Damage `dmg` +2.8 % | Crit Chance `cc` +1.4 % | DPS +4.2 % |
| Precision (w) | Crit Chance `cc` +2.8 % | Crit Damage `cd` +5.7 % | DPS +4.2 % |
| Arcane (w, spell) | Magical Power `mp` +4.0 | Crit Damage `cd` +4.8 % | caster DPS +4.2 % (mp = str for casters) |
| Tempo (w) | Attack Speed `as` +3 % (live after round A0, D17) | Damage `dmg` +3.6 % | DPS +4.2 % |
| Bulwark (a) | Defense `def` +0.9 | Health % `hpp` +1.0 % | EHP +1.5 % |
| Warrior (a) | Strength `str` +1.6 | Defense `def` +1.6 | EHP +1.2 %, DPS +1.4 % |
| Swift (a) | Speed `spd` +0.5 | Mana % `manap` +2 % (new key) | utility (not in the DPS / EHP model) |
| Vital (a) | Health % `hpp` +1.3 % | Health Regen % `hprp` +0.8 | EHP +1.2 % |
| Sage (a) | Magical Power `mp` +1.6 | Mana % `manap` +2 % | caster DPS +1.4 % |
| Prospector (t) | Breaking Speed +4 % | Fortune +25 | ~+2 % Fortune budget Z5 + speed |
| Scholar (t) | Wisdom +3 % | Fortune +15 | XP + Fortune |
| Delver (t) | Power +6 % | Breaking Speed +3 % | speed only |

Armor numbers look small because one Defense point is ~0.9 % EHP (110 base). All are PLACEHOLDER rows `aug.stat.<Kind>` until P0 signs
them off. Stat augments add to `GearStats.totals0` in a new `addAugE` right after `addModsE` inside the same `active()` gate (**P1** 4.1:
weapon branch + armor loop), so they behave exactly like rolled lines everywhere (caps, popups, Stats page). Tool kinds feed the
lifelong-tool perk sums (`gear:swing:harvest:`, Fortune, power) through the same reader the tool lines use (builder confirms the entry point).

## 4. ELEMENTAL augments - numbers + stacking

### 4.1 Values (per slot; 10 tiers - PLACEHOLDER rows `aug.elem.*` until P0)

T10 equals the old T5 row (so the power cap of D8 does not move); T1-T5 are the zone range, T6-T10 are the fuse reward.

| Tier | Weapon: element damage (% of the hit, joins `f<E>`) | Weapon: Element Power | Armor: element Defence (joins `d<E>`) |
|---|---|---|---|
| I | 0.3 % | 1 | 0.8 |
| II | 0.5 % | 2 | 1.4 |
| III | 0.7 % | 3 | 2.0 |
| IV | 0.9 % | 4 | 2.6 |
| V | 1.2 % | 5 | 3.2 |
| VI | 1.5 % | 6 | 3.8 |
| VII | 1.9 % | 7 | 4.4 |
| VIII | 2.3 % | 8 | 5.0 |
| IX | 2.6 % | 9 | 5.5 |
| X | 3.0 % | 10 | 6.0 |

Power = the tier number, so one T5 slot gives the old "base numbers" (P 5) and one T10 slot hits the cap (10 = double, section 4.2).
A Mythic weapon with 3 x Fire X = +9 % of the hit as Fire (flat, no slot power) = **DPS +9 %** neutral, about +11 % vs a Fire-weak mob,
**less raw damage than 3 Brute V (+13 %) on purpose: the element pays you back in states and reactions** (the "choose between them" of D1).
Armor: 12 x Fire X = 72 Fire Defence -> `S/(S+D)` = 42 % less Fire damage, Burning on you 42 % shorter. A T5 drop fused up costs
`aug.fuse.n`^5 items, so power from fusing is paid for in farming (Skyy's "faster you can fuse up" in higher zones).

**Poison (modifier, D16):** weapons only; 5 tiers; +0.4 / 0.8 / 1.2 / 1.6 / 2.0 % Poison (the live `poison` key, % over `poison.time`) per slot. No Element Power,
no Defence line, no state in the matrix. A weapon with several Poison slots stacks the % ("it all stacks", D4). Armor keeps its vanilla Poison resistance (Thorium).

### 4.2 Element Power (what drives the states)

`P_e` (per hit, per element) = sum of socketed elemental tier NUMBERS (1-10) of e on the HELD weapon (Poison adds none) + 3 for each rolled `f<E>` / `r<E>` line of e
on it + 5 while Imbue of e runs. States scale with `s = min(P_e, 10) / 5` (P 5 = the base numbers in section 5, P 10 = double, cap).
So rolled element lines ALSO make elements "really work" (Skyy "unlike wynncraft where its just another damage number"), augments make
them strong. Charms, pets and `rElem` add DAMAGE only, never Power (they are not on the weapon).

### 4.3 No double counting

| Source | Adds | Rule |
|---|---|---|
| Elemental augment (weapon) | `W_e` (like a rolled `f<E>` line) + Power (= tier) | joins `addAugE` once; opens the pet gate (`W_e > 0`) like a rolled line - intended (**P1** Q4) |
| Elemental augment (armor) | `D_e` | joins the `gear:fn:elemDef` sum once |
| Imbue (Spellblade) | `I_e` = % of N, + Power 5 | untouched by augments; **one state application per element per hit**: the engine takes `max(P_aug, 5)` and Classes' own `imbueStatus` call is routed through the engine (no second Burn) |
| Charms / Prism / Elemental Power / pets | `C_e` / gated `P_e` damage, `d<E>` | unchanged; no Power |
| Mob Weak / Resist | `dealt_e x (1 + mod/100)` | unchanged; reactions use the element part AFTER this |
| Reaction bonus damage | its own Damage (element cause, family 0) | never re-enters the weapon chain, never crits, never triggers another reaction (5.6) |

## 5. ELEMENT EFFECTS + INTERACTIONS (the engine, SkyyClasses)

### 5.1 The states (on mobs; players see 5.5)

| State | Comes from | What it does (P 5; x `s` where marked) | Look (vanilla ids) | Ends |
|---|---|---|---|---|
| **Burning** | Fire hit | DoT 2 % of the hit a second x s, 4 s, 3 stacks (new hit refreshes the oldest) - Fire cause, never staggers | `Skyy_Elem_Burning` (child of `Burn_Template`: tint, `Effect_Fire`, ModelVFX Burn, burn sound, icon); hit `Impact_Fire` | time; Water / Earth / entering water (vanilla InFluid) |
| **Wet** | Water hit (first one); standing in water; rain (`elem.rainWet`) | no damage; Burning can't start; sets up Thunder / Ice | tint #4fa8ff, `Water_Dripping` | 6 s; Fire (Steam), Earth (Mud) |
| **Chilled** | Water hit on a Wet / Chilled target; Air on Wet | -15 % move speed x s, 3 s | live Chill effect, `Impact_Ice`, `Weapon_Frost_Mist` | time; Fire (Thaw) |
| **Frozen** | 3 Chills within 3 s | can't move 1.5 s (vanilla Freeze via `freezeOne`) | `Effect_Snow`, ModelVFX Freeze | time; Fire (Melt), Earth (Shatter) |
| **Shocked** | Thunder hit | 3 s: takes +5 % damage; 30 % x s of the Thunder part jumps to 1 enemy within 3 blocks; **FLINCH** (Skyy "stagger") 0.25 s on every 2nd Thunder hit | `Hazard_Electric_Stun` particles (not the effect), `Lightning` arc, flinch = `Hit_Interrupt_Flinch` (X2) | time; Earth (Grounded) |
| **Quaked** (was "Stagger" in Classes) | every 3rd Earth hit | 0.4 s stun + -10 % Defence 4 s x s | `Ability_GroundSlam_Spike`, `Block_Hit_Stone` | time |
| **Gusted** | Air hit | +1 block knockback x s (Skyy "more knock back"), heavy hits lift; marks "Windswept" 2 s for Fire combos | `Ability_Windstrikes`, `Wind` | 2 s |
| **Poisoned** (modifier, NOT an element - D16) | Poison line / Poison augment | live Wynn X/10 s DoT, stacks, never staggers (D4); takes part in NO reaction (see 5.2) | vanilla Poison look | time |

Rain makes players and mobs Wet with the setting `elem.rainWet` (default on, D17 "Yes, with a setting"). A mob never gets its OWN element's state (a Fire mob can't burn, a Water mob is always Wet - the realistic part of the mob table).
Weapon aura: holding a weapon with an elemental augment shows that element on the blade (`FireSword` / `Lightning_Sword` / water drip /
`Buff_Windstrikes` / dust / `Buff_ImbuePoison`), player switch `gear.augFx`.

### 5.2 Interaction matrix (row = the element that HITS, column = a state the target ALREADY has)

| Hits \ has | Burning | Wet | Chilled / Frozen | Shocked | Quaked | Gusted (Windswept) |
|---|---|---|---|---|---|---|
| **Fire** | adds a stack | **Steam**: Wet ends, burst +25 % of the Fire part (Fire), no Burn this hit (`Goblin_Decorative_Steam`) | **Thaw / Melt**: Chill or Frozen ends -> Wet; vs Frozen +50 % of the Fire part | - | - | **Fanned**: Burning starts with +1 stack cap (4) and +50 % duration |
| **Water** | **Douse**: Burning ends, Steam burst +25 % of the Water part, target Wet | -> Chilled (ice on a wet target - Skyy) | Chill counts **double** toward Frozen | **Conduct**: the Shock jumps to every Wet enemy within 4 (max 3) once | **Mud**: -25 % speed 3 s | - |
| **Thunder** | - | **Electrocute**: Thunder part x1.5, sure flinch 0.4 s, jumps to every Wet enemy within 4 (max 3) | - (ice insulates) | refresh + jump | **Grounded**: Shock ends, its jump damage hits this target instead (+30 % of the Thunder part) | **Storm**: +1 jump, +2 blocks range |
| **Earth** | **Smother**: Burning ends, its remaining damage dealt at once | **Mud**: Wet ends, -25 % speed 3 s | **Shatter**: Frozen ends, +50 % of the Earth part | **Grounded** (as above) | counts to the next Quake | **Sandblast**: +20 % of the Earth part, target deals -10 % 3 s |
| **Air** | **Fan the flames** (Skyy): +1 stack (cap 4), +50 % time left, burn x1.25; spreads 1 stack to 1 enemy within 3 (**Wildfire**) | **Wind Chill**: Chilled | Chill +1 | **Storm** (as above) | **Sandblast** (as above) | more knockback |

Poison is a weapon MODIFIER (D16), not an element: the 2026-10-25 matrix's Poisoned column and Poison row (Toxic Flare, Dilute, Disperse) are
**removed for v1** (N7). A Poisoned target still takes its DoT; no element reacts with it and it reacts with nothing.

"-" = no reaction (Fire + Thunder: nothing real happens). Reaction damage = `round(part x %)` of that
hit's element part after mob Weak / Resist, its own Damage with the element's cause.

### 5.3 Order inside one hit (multi-element weapons)

1. Snapshot the target's states. 2. For each element on the hit (Wynn order Earth, Thunder, Water, Fire, Air; then Poison, which only applies its DoT) check the
matrix against the SNAPSHOT only - a hit never reacts with a state it applies itself (a Fire + Water weapon alternates Burning / Steam,
it does not cancel itself in one swing). 3. Apply the new states. 4. Per target, each reaction has a cooldown `elem.reactCd` 1.0 s (fast
weapons can't spam bursts). 5. Max 1 reaction popup per hit (the strongest).

### 5.4 Bosses (no hard-lock) and status resist

- Bosses (`mob:fn:boss`): stun / freeze / flinch times x `bossCc` 50 % (live row), then **CC immunity 8 s** (the live boss clock
  extended to flinch and Quake); knockback immune (live Gust rule); damage-over-time and reaction DAMAGE work in full. A boss never
  loses its attack to Thunder: flinch at most once per 4 s, never during a wind-up it already started (UNVERIFIED X2).
- Status resist: a victim's element Defence shortens that element's state: `time x S / (S + D_e)` (the same curve as damage, so no new
  number to learn). Poison uses Thorium's vanilla Poison resistance (live).

### 5.5 Players (PvP) and mob element hits

Same states on players hit by players (where PvP is on) or by element mobs (`elem.mobShare` hits, live): CC x 0.5 (Frozen max 0.75 s,
flinch 0.15 s, Quake 0.2 s), knockback x 0.6, then 5 s CC immunity; Wet player in water / rain + Thunder mob = Electrocute (it is the
risk of swimming in a storm). Rows `elem.pvp.cc` 50, `elem.pvp.kb` 60, `elem.pvp.immune` 5 s, `elem.pvp.on` true.

### 5.6 How it feels (for the test list)

Fire: the enemy lights up and keeps ticking; an Air hit makes it roar brighter and jump to the next mob. Water: first hit soaks
(dripping), keep hitting and it slows, then freezes solid - then an Earth hit shatters it. Thunder: every second hit makes the mob
twitch and arcs to its neighbour; on a soaked group it chains through all of them. Earth: heavy thuds, every third one knocks them
dizzy and cracks their armour; it puts out fire and grounds lightning. Air: things fly back further and fire spreads. Reaction words pop
in the element colour: STEAM, MELT, SHATTER, ELECTROCUTE, GROUNDED, STORM, MUD, WILDFIRE.

## 6. Build split, saved data, rollback, risks

### 6.1 Rounds (order; revised 2026-10-27 - every round lists the mods it touches)

| Round | Mods touched | Size | Content | Depends |
|---|---|---|---|---|
| P0 | none | main session, no agents | probes X1-X10; `balance_model.py` rows for 3.2 / 4.1 (10 elemental tiers, fuse ratio); N1-N8 defaults | - |
| **A0 Attack Speed live** (R7, new) | SkyyGear (+ SkyyClasses if the swing-time hook lives there) | Full round (it changes every class's DPS) | gear stat `as`: totals line, Stats page, caps, tooltips; reuse the hook the live attack-speed buffs use (Warlord's Banner, Blood Frenzy, Flowing Form, weapon speed classes slow / medium / fast; X9) | live set |
| **A1 effects engine** | SkyyClasses (+ SkyyMobs: Wet from water mobs, `elemOf` for own-element immunity) | **Full round** (ultracode lenses: thread rules, boss lock, PvP, double count, spam) | bridge `classes:fn:elemHit(Object[]{ UUID attacker, UUID victim, int[] power5, double[] parts5, Double hit, Boolean heavy })` (5 elements, Poison is not in it); states 5.1 incl. NEW Wet + Gusted + Quaked rename; matrix 5.2 (no Poison); order 5.3; boss / PvP 5.4-5.5; reaction popups; Imbue routed through it; rows `elem.*` incl. `elem.rainWet` | live elem1 set |
| **A2 sockets + items** | SkyyGear + SkyySacks (Combat bag) + `tools/tier_tags.py` | **Full round** (saved item data, item loss / dupe / destroy-on-replace, damage sums, 120 items) | 2.2-2.8, 3, 4: `aug` / `augAdd` doc keys, `addAugE`, Power per hit -> `classes:fn:elemHit`, Anvil Augments tab (replace / fuse, no remove), tooltips, recipes (fuse ratio), auras, gathering-armor slots by rarity | A0 + A1 pinned (Gear calls the bridge; missing bridge = damage only, ready line says so) |
| A3 sources + element mobs | SkyyMobs (drop tables, per-zone primary element, element spawn mix, new Water / Air / Thunder mobs) + SkyyMerchants + loot; PACK.md if Slime Mobs! is packed | **Full round** if new mob bodies are built, else Lean | drops 2.4 (zone tier, element mob x3, primary x2), pre-filled loot, merchant T1, the gaps from 1d | A2 |
| A4 charts | SkyyMenu | Lean | Reactions chart = 5.2 (replaces "later"), states list, Element Power on YOUR STATS, Poison shown as a modifier | A1 |
| A5 | SkyyGear + SkyyClasses | Later | class-tree nodes that strengthen reactions (R6 "Yes, later"); Resonance (N8) | A2-A4 played |

A0 + A1 + A2 deploy together (one batch, one smoke test by the main session); A3 / A4 can follow. Launch via `skywynn-round` with Skyy's
quotes D1 + D13 in `args.quotes` (popup question + answer).

### 6.2 Saved data + migrations

- Item doc keys `aug` (BsonArray of BsonString `"S:Brute:3"` / `"E:Fire:7"` (tier 1-10) / `"M:Poison:3"` / `""` empty) and `augAdd` (Int32). grep 0.3.46 found no
  `aug` key (re-check at build). No slot count stored -> **existing gear gets slots at once, no migration, no file rewrite**.
- Classes: no saved data (states are live only). New rows read defaults while missing (kit rule).
- `tools/tier_tags.py` word only.

### 6.3 Rollback

Gear back to 0.3.46: unknown `aug` keys are kept by the clone rule and ignored (augments stop counting, nothing lost; rolling forward
brings them back). Augment items become unknown ids if the jar that defines them is gone -> deploy floor: never roll SkyyGear below the
A2 version once augments exist in saves (comment in `tools/deploy_set.py`). Classes back to 0.1.50: `classes:fn:elemHit` missing ->
Gear's ready line notes "element states off", damage still works.

### 6.4 Server Setup rows (summary)

Gear: `part.augments` (bool, on), `aug.slots` (table by rarity Weapon | Armor), `aug.slots.tool`, `aug.extraSlots` 1, `aug.slotCost`,
`aug.slotLevel` 10, `aug.stat.<Kind>` (T5 pair values), `aug.tierScale` 40 / 55 / 70 / 85 / 100 (stat + Poison), `aug.elem.weapon` / `aug.elem.armor` /
`aug.elem.power` (4.1, 10 values each), `aug.fuse.n` 2, `aug.poison.<tier>`, `aug.zoneElement.<1..5>`, `aug.xp`, `aug.loot.prefill` 10. Classes: `elem.on`, per state numbers (`elem.burn.*`,
`elem.wet.time`, `elem.chill.*`, `elem.freeze.*`, `elem.shock.*`, `elem.flinch.*`, `elem.quake.*`, `elem.gust.*`), each reaction %
(`elem.react.<Name>`), `elem.reactCd` 1.0 s, `elem.bossImmune` 8 s, `elem.pvp.*`, `elem.rainWet`. Mobs: `aug.drop.base` / `aug.drop.elemMob` / `aug.drop.primary`, element spawn mix per zone. (`aug.removeRefund` is gone: no removal.)

### 6.5 Risks

| Risk | Guard |
|---|---|
| Item dupe / loss on add / remove | **P1** 7.1 atomic order + re-read + harness H1-H9 equivalents |
| CC lock on bosses / players | 5.4 / 5.5 clocks; harness: 1,000 Thunder + Water hits on a boss fixture never exceed the duty cap |
| Particle / packet spam (fast weapons, big packs) | reaction cd 1 s, max 1 reaction popup per hit, chain max 3, particles only for viewers that see the mob |
| Double count with Imbue / pets / charms | 4.3 + harness identity: no augments -> Gear sums byte-identical to 0.3.46 |
| Thread rules | Gear's hit system only queues `classes:fn:elemHit`; all state work on the world thread (Classes' job queue, as `classes:fn:dot`) |
| 120 items + lang keys | one writer (SkyyGear), `tools/ci/langdup.py`, build asserts no vanilla id shadowed |
| Power creep | P0 model sign-off; one T5 weapon slot = +4.2 % DPS cap stays a row; T10 elemental = old T5 value (4.1) |
| Fuse cost / dupe / loss (new) | fusing and replacing are one atomic take-then-write (the P1 order) with re-read; harness: replace destroys exactly 1 item, fuse uses exactly `aug.fuse.n` items, no path gives an augment back (no removal means no dupe-by-unsocket) |
| Players lose an augment by mistake (new) | confirm dialog on replace; the page shows old -> new before OK |

## 7. Questions for Skyy (revised 2026-10-27; defaults in brackets; the build uses the default until answered)

Closed by Skyy's answers of 2026-10-25 (word for word in `docs/answered/gear.md`): Q1 removal (R1), Q2 tiers (R2), Q3 Poison (R4), Q4 Attack Speed (R7),
Q5 gathering (R3), Q6 name, Q7 rain, Q8 tree nodes. Q9 (Resonance) was not asked: [later, not v1] = N8.

| # | Question (ambiguity in the answers) | Default |
|---|---|---|
| N1 | Elemental fusing: how many of tier n make one of tier n+1? 10 tiers at 3:1 would be 19,683 T1 for a T10; Skyy only said "fused together". | [2 : 1 (T10 = 512 T1), row `aug.fuse.n`] |
| N2 | Placing the same element on a filled slot: only EQUAL tiers fuse (slot T4 + item T4 = T5)? What if the item is higher / lower (higher replaces and wastes the old one; lower is refused as a downgrade)? | [equal tier fuses; higher replaces; lower refused with a message] |
| N3 | Primary element of Zones 2-5 (only "Zone 1 = Earth" and "eventually a zone per element" are said). | [Z2 Thunder, Z3 Water, Z4 Fire, Z5 Air = the mob wheel order; editable rows] |
| N4 | Poison augment: "weapon modifier": weapons only, 5 tiers (one per zone), crafted from Venom Sacs and not fused (no "10 tiers, fuse" was said for it)? Or also 10 tiers? | [weapons only, 5 tiers, no fuse, a third slot type next to Stat and Elemental] |
| N5 | "Slots based on the rarity of the item": do gathering armor pieces and lifelong tools HAVE a rarity? (tools were not named in the answer). | [armor: use its Quality through the combat-armor column; tools: keep the tier ladder 1 / 2 / 3] |
| N6 | "Can't take it out": does that also mean an added (empty) slot can still be removed (D2 "slots can be added and removed")? | [yes, only empty slots the player added, no refund] |
| N7 | Poison is not an element: drop the Toxic Flare / Dilute / Disperse reactions (Poison reactions) from v1? | [dropped for v1; may return as tree nodes later] |
| N8 | Socket Reforge's "Resonance" (order of augments = hidden bonus) - want something like it later? (not asked) | [later, not v1] |

## For the local session (UNVERIFIED engine facts - probe or assert before A1 / A2)

| # | Fact | How |
|---|---|---|
| X1 | A damage-free child of `Burn_Template` (`BaseDamage Fire 0`) shows the vanilla Burn look and keeps the InFluid-water refusal | probe (same as the elem1 P4 Poison probe) |
| X2 | `Hit_Interrupt_Flinch` applied by `effect()` makes an NPC flinch without cancelling a boss wind-up; how long it lasts | probe on a Trork + Goblin Duke |
| X3 | Our own EntityEffect with Particles on `TargetEntityPart PrimaryItem` (the `Ability_Wind_Buff` pattern) shows on a held weapon for players and refreshes on hotbar change | probe |
| X4 | Detecting "in water" / "in rain" for Wet from a mod (vanilla `InFluid` is an effect ApplyCondition; weather state API) | reflect `tools/dev/reflect.py` |
| X5 | Can Classes queue a `CombatTextUpdate` (reaction word) itself, or must it hand the word back to Gear's popup stage | reflect / read Gear's critFx path |
| X6 | AH, trade, Vault, Requip, Wardrobe keep the whole SkyyGear doc (`aug`) | in game test steps |
| X7 | `mode:7` still free on the 0.3.46 Anvil; `aug` key unused; the lifelong-tool perk sum entry point for tool augments | grep at build |
| X9 | where live attack speed is applied today (Banner / Blood Frenzy / Flowing Form buffs; weapon speed classes) and whether a gear `as` stat can use the same hook (round A0) | read SkyyClasses + SkyyGear weapon-speed code |
| X10 | per-zone mob spawn mix can be weighted by element in SkyyMobs (primary element majority + a few of every element), and drops can be read per zone for tier | read SkyyMobs spawn / level tables |
| X8 | `manap` (Mana %) on gear: deliver through the same `modPct` path SkyyPets 0.4.8 uses, without a second writer on the Mana stat | read SkyyPets 6389-6391 + SkyySkills mana |
