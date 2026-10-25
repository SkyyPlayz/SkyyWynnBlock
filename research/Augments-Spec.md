# Augments - build spec (gear slots: Stat + Elemental augments, real element effects + interactions)

Spec, 2026-10-25. Nothing built. Owner: Skyy (they/them). Where this goes: `research/` (INDEX.md "research"). Answers to "Questions for
Skyy" go to `docs/answered/gear.md` (`python tools/qa_append.py gear ...`); build results to `docs/log/2026-10.md`.
Replaces `research/cloud/Powders-P1-Build.md` + `research/cloud/Powders-Spec-Draft.md` (superseded; their verified code facts and anti-dupe
rules are reused below and marked **P1**). Idea notes: `research/Augments-Idea.md`.
Code facts read from the SET pins of today (`python tools/deploy_set.py --check`: SkyyGear 0.3.46, SkyyClasses 0.1.50, SkyyMobs 0.1.19,
SkyyPets 0.4.18, SkyyAccessories 0.5.32, SkyySacks 0.8.30, SkyyMenu 0.3.47). Vanilla facts read from `Assets.zip` (read-only) today.
Numbers were priced with `tools/balance_model.py` P5 functions (`p5_dps`, `p5_ehp`, `p5_roll`) - read-only import in scratch.

## 0. Decisions this spec follows

| # | Source | Line (short) | Where it lands |
|---|---|---|---|
| D1 | gear.md 2026-10-25 AUGMENTS REPLACE POWDERS | "gear has augment slots ... call them something else ... two types, stat buffs, and elemental ... fuse low level ... into higher ... on weapons they add damage, and on armor they give defense ... have to choose between them ... each buff augment gives 2 stats ... armor, ... weapons, ... tools ... fire will set the enemy on fire, lightning can stager them. air does more knock back ... water would put out a burning enemy, but lighting and ice are more effective against a wet enemy. wind and fire combo ... increasing the intensity and length of the fire ... i want all the elements to interact realistically." | whole spec |
| D2 | gear.md 2026-10-11 GEMS | "most gear has 1 gem slot. legendarys, UTs and specials have between 2 and 3 ... slots cab be added and removed ... gems DO NOT have levels or rarities" | socket table 2.5; add / remove socket 2.6; the "no levels" part only partly kept (Q2) |
| D3 | gear.md 2026-10-23 POWDERS REMOVAL | "Destroyed (Recommended)" | removing an augment destroys it (2.6), row for a refund |
| D4 | gear.md 2026-10-18 ELEMENTS Q1-Q10 + classes.md 212 (IMBUE ALL 5) | Imbue picks 1 of 5 out of combat; charms weak -> powerful; pets add element only if the weapon deals it; per-element hit popups; Defence ON; mob Resist -25 / Weak +25 / boss -50, never immune; plates show the mob's OWN element + strong/weak + reactions charts; Poison Wynn-style X/Ys, no stagger, stacks; "Reactions: later, as tree nodes" | 4.3 no double count; 5 the engine; **Q6 "later" is overridden by D1** (Skyy now wants interactions built in) - tree nodes can still strengthen them later (Q8) |
| D5 | elem1 (docs/log 2026-10-23 01:00 / 02:05) | live: Mobs 0.1.17 element table + plates, Gear 0.3.39 element damage / Defence / Poison % over 10 s / per-element hits, Classes 0.1.46 Imbue via gear:imbue + `classes:fn:dot`, Pets 0.4.10 pet elements, Accessories 0.5.32 element + Prism charms (`Skyy_Talisman_*` / charm lines), Menu 0.3.45 charts | all reused as is; this spec adds sockets + the states engine |
| D6 | gear.md 2026-10-22 UT BANDS + 10-18 UT = ZONE ALLOY TIER | UTs sit at the END of their zone | UT socket rows 2.5 |
| D7 | PROJECT-RULES 4 tier tags + Rarity colours + tooltip layout (2026-10-24) + Style Guide 15 | "T3 Augment - ..." first; rarity colour on icon + popup title; Pets-style sections | 2.3, 2.8 |
| D8 | PROJECT-RULES 4 four power sources; targets.md 137 split 35 / 30 / 20 / 15 | augments are part of the GEAR shares (weapon / armor / tool) | 3.1 budget |
| D9 | PROJECT-RULES 2 "Order: vanilla -> existing mod -> build only what we need" (Skyy 2026-10-24) + "check for an existing mod BEFORE building" | section 1 | survey |
| D10 | gear.md 2026-10-22 CRAFTED ITEMS NEVER UT / MYTHIC; 2026-10-18 SOUL CAGE "use the worst one" | augments are plain items; recipes take the lowest tier match | 2.4 |
| D11 | Menu-Pattern M3 (Anvil = sub-tabs) + HANDOFF 2 UI rules + "replace commands, never add extra" | Anvil > Augments sub-tab, no new command | 2.7 |
| D12 | PROJECT-RULES 4 no dev gates; everything a server owner changes = Server Setup | default ON; every number a row | 6.4 |

## 1. Survey first (PROJECT-RULES 2)

### 1a. Vanilla (Assets.zip, read today)

| Need | Vanilla has | Use |
|---|---|---|
| Gem / socket items | 7 gems `Rock_Gem_Diamond / _Emerald / _Ruby / _Sapphire / _Topaz / _Voidstone / _Zephyr` (ore blocks, Gemstone collection in our Collections spec, booster recipes use 5 of them); 9 crystals `Ingredient_Crystal_*`; essences `Ingredient_Fire / _Water / _Ice / _Lightning / _Void / _Life_Essence`; `Ingredient_Sac_Venom`. **No socket system on gear.** | stat augments are made from gems, elemental ones from essences / crystals / venom (2.4). Icons / models: build-time recolours of the gem + essence models (P1 Sigil pattern, nothing vanilla committed) |
| Vanilla runes | `Rune_*` ability runes + modifiers (`Rune_Convert_Lightning`, `Rune_Convert_Wind`, `ConvertElement`, slot "Support") = the vanilla ABILITY rune system, not gear sockets | not used (name clash avoided: "Runes" stays the class-rune word, classes.md 192) |
| Damage causes | `Server/Entity/Damage/`: Earth, Fire, Ice, Lightning, Water, Wind, Poison, all Parent `Elemental` (text colours Fire #FF6B2B, Water #2B5FCC, Lightning #FFE14D, Wind #A5D8F5, Earth #B2C96B) | DoT / reaction damage uses the element's cause (already done by Classes 0.1.46 via `DamageCause.getAssetMap()`) |
| Burning | `Status/Burn.json` (Parent `Burn_Template`: tint #cf2302, `Effect_Fire` particles, ModelVFX `Burn`, burn sounds, icon, 5 Fire / s, 3 s). `Burn_Template` **already refuses to apply while the target is in Water** (`ApplyConditions InFluid Water Inverse`) and with `Immunity_Fire`; `Lava_Burn`, `Flame_Staff_Burn` | Burning look = a damage-free child `Skyy_Elem_Burning` (Parent `Burn_Template`, `BaseDamage Fire 0`) so vanilla's "no fire in water" rule comes free; damage stays our DoT (probe X1) |
| Frozen / Chill / Slow | `Status/Freeze.json` (DisableAll movement, `Effect_Snow`, ModelVFX `Freeze`), `Ability_Frost_Chill` (speed x0.6, Tag Element Water), `Ability_Frost_Freeze`, `Ability_Frost_Slow`, `Status/Slow.json`, `Immunity_Freeze`, `Immunity_Slow` | Frozen = Classes' existing `freezeOne` (vanilla Freeze + boss clock); Chill = Classes' existing `spdId` slow effect |
| Stagger / stun | `Status/Stun.json`, `Hit_Interrupt_Flinch`, `Hit_Interrupt_Stunned`, `Hazard_Electric_Stun` (yellow tint + `Hazard_Electric_Stun` particles, but 3 s DisableAll + no abilities - too strong for a hit), `Bomb_Explode_Stun` | Thunder flinch = `Hit_Interrupt_Flinch` (probe X2) + the electric particles only; Earth Quake = Classes' existing `stunMob` |
| Wet | **none** (no effect, no state; only Burn's InFluid check and rain ambience) | we build Wet (5.1) |
| Knockback | Classes `push()` + `AbilCfg.PUSH_PER_BLOCK` (live), `Root.json` `KnockbackMultiplier` field | Air knockback = Classes' existing Gust push |
| Poison | `Status/Poison.json`, `Poison_T1..T3`, `Immunity_Poison`, particles `Effect_Poison`, `Status_Poisoned`, `Impact_Poison`; Thorium armor resists Poison | already used by Gear 0.3.39 Poison |
| Weapon auras (on the held item) | `Ability_Wind_Buff.json` = Particles on `TargetEntityPart PrimaryItem` / `TargetNodeName Handle` (`Buff_Windstrikes`); particle systems `FireSword`, `Lightning_Sword`, `Buff_ImbuePoison`, `Buff_Windstrikes`, `Weapon_Frost_Mist`, `Embers` | element aura on a weapon with an elemental augment = our `Skyy_Aug_Aura_<E>` effects built on that pattern (probe X3) |
| Hit / reaction particles (all exist, `.particlesystem`) | Fire `Impact_Fire`, `Fire_AoE_Spawn`, `Embers`; Water `Water_Splash_Soft`, `Water_Dripping`, `Splash`; Ice `Impact_Ice`, `Ice_Blast`, `Block_Break_Ice`, `Ability_Ice_Explosion`; Thunder `Lightning`, `Beam_Lightning2`, `Hazard_Electric_Stun`; Air `Wind`, `Ability_Windstrikes`, `Example_Tornado`; Earth `Block_Hit_Stone`, `Ability_GroundSlam_Spike`, `Block_Land_Soft_Dust`; Steam `Goblin_Decorative_Steam`; Poison `Impact_Poison`, `Status_Poisoned` | section 5 table |

### 1b. Existing mods (Skyy's Mods folder, read-only, + CurseForge)

| Mod | Licence | What it has | Verdict |
|---|---|---|---|
| **Socket Reforge** (iRaiden_, CurseForge, 1.4.5, Hytale 0.7, needs HyUI) | **MIT** | Socket Punch bench (up to 4-5 sockets), 6 essences (Fire / Ice / Lightning / Life / Void / Water) as socket fillers, same-type stacking raises tier, "Resonance" (essence ORDER in a full item = hidden bonus), loot with broken sockets, a hammer clears sockets (10 % durability, may break a socket) | **Learn, do not pack**: it duplicates SkyyGear's Anvil reforge and would add a second socket system on our item docs (no-duplicates rule). Learn: Resonance (Q9 - a later bonus), "socketed loot" (drops may come with a pre-filled augment, 2.4), clear-by-tool idea (we keep a menu button). MIT means its code may be read and folded if ever useful - not needed |
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

## 2. The system

### 2.1 Name

| Option | For | Against |
|---|---|---|
| **Augments** (recommended default) | Skyy's own word; says what it does; no clash inside our pack (Sigils, Runes, Shards, Dust, Charms, Talismans are taken) | EndlessLeveling / roguetale use "augment" for cards (not in our pack) |
| Infusions | fits elements ("Fire Infusion IV") | odd for stat pairs; close to "Imbue" (the Spellblade ability) |
| Facets | gem-like, unique | players may not get it at once |

Items read "Brute Augment III" / "Fire Augment IV"; the socket is an "augment slot".

### 2.2 Kinds and ids (all owned + lang-written by SkyyGear)

Tier n = 1..5 = the zone (Z1 .. Z5), Roman in names. Ids `Skyy_Aug_<Kind>_<n>`.

| Type | Kind (id part) | Fits | Gives (2 stats / element) | Made from (2.4) |
|---|---|---|---|---|
| Stat - weapon | `Brute` | weapons | Strength + Crit Damage | Ruby |
| Stat - weapon | `Edge` | weapons | Damage % + Crit Chance | Topaz |
| Stat - weapon | `Precision` | weapons | Crit Chance + Crit Damage | Voidstone |
| Stat - weapon | `Arcane` | spell weapons (slot "s") | Magical Power + Crit Damage | Sapphire |
| Stat - weapon | `Tempo` | weapons | Attack Speed + Damage % (needs Attack Speed live - Q4; until then Charged Attack Damage + Damage %) | Zephyr |
| Stat - armor | `Bulwark` | combat armor | Defense + Health % | Diamond |
| Stat - armor | `Warrior` | combat armor | Strength + Defense | Ruby |
| Stat - armor | `Swift` | combat armor | Speed + Mana % (new gear key `manap`, delivered like SkyyPets' `mana`) | Zephyr |
| Stat - armor | `Vital` | combat armor | Health % + Health Regen % | Emerald |
| Stat - armor | `Sage` | combat armor | Magical Power + Mana % | Sapphire |
| Stat - tool | `Prospector` | lifelong tools + gathering armor (Q5) | Breaking Speed % + that skill's Fortune | Emerald |
| Stat - tool | `Scholar` | lifelong tools + gathering armor (Q5) | that skill's Wisdom % + Fortune | Topaz |
| Stat - tool | `Delver` | lifelong tools | that skill's Power % + Breaking Speed % | Diamond |
| Elemental | `Earth` `Thunder` `Water` `Fire` `Air` | weapon: element damage + Element Power; armor: element Defence + status resist | 4.1 | Green crystal / Lightning ess. / Water ess. / Fire ess. / Cyan crystal |
| Elemental (status) | `Poison` (Q3) | weapon + combat armor (the live Poison line is "wa") | Poison % (the `poison` key) + Poison Power | Venom Sac |

13 stat kinds x 5 + 6 elemental x 5 = **95 items**. Tool kinds read the skill from the item they sit in (a pickaxe -> Mining Fortune,
a hatchet -> Foraging, hoe / Harvester -> Farming; a multitool socket counts for both sides, as the multitool rule says "no drawbacks").

### 2.3 Tiers, tier tags, rarity

- `tools/tier_tags.py`: `OWN_LADDERS += "Augment"` -> `"T3 Augment"`; TT_VERSION stays "3" (a new word renumbers nothing - **P1**).
  Flavor text first phrase = the tag: `T3 Augment - Brute (weapon).`
- Rarity colour = the item `Quality` by tier: T1 Common, T2 Uncommon, T3 Rare, T4 Epic, T5 Legendary (icon frame + popup title per
  the 2026-10-24 rule; builder maps to the Gear quality ids it already uses). Augments never roll a rarity (D2 "no rarities").
- Sort by tier then kind (Wynn element order for elementals) everywhere: Anvil list, Bazaar, shop, recipe lists.

### 2.4 How you get them

| Route | Stat augments | Elemental augments |
|---|---|---|
| **Craft** (main), vanilla Alchemy Bench recipes (asset only, inputs drawn from the Magic Bags - **P1** 2.4) | T1 = 1 gem + 4 of that zone's ore / bar; T2-T5 = 1 gem + that zone's Enchanted material (the zone gate = the collection ladder) - each tier crafted fresh, no fusing (D2) | T1 = 2 essence / crystal / venom; **fuse**: 3 of tier n -> 1 of n+1 (Wynn-style, Skyy D1) |
| Drops (SkyyMobs) | elites / mini bosses / dungeon bosses: rare T(zone) stat augment; full bosses guarantee 1 | mobs of an element (`elem.mobs`) drop that element's T1 (T2 in their zone's second half); elites x3; bosses 1-2 of T(zone) |
| "Socketed loot" (learned from Socket Reforge) | a dropped Legendary+ item may come with 1 slot pre-filled (row `aug.loot.prefill` 10 %) | same |
| Bazaar / AH | tradable plain items (no metadata); Bazaar entries, Combat bag (`homeOf` startsWith `Skyy_Aug_` -> Combat, **P1** 8) | same |
| Traveling Merchant | T1 only, rotating | T1 only, rotating |

Value check: T1 elemental ~ 225 coins of essence (**P1**), T5 = 81 x T1 with 3:1 fusing.

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

Lifelong tools (by the tool's tier on the 15-step ladder): T1-T3 1, T4-T9 2, T10-T15 3. Gathering armor pieces: 1 from T4 (Zone 2) (Q5).
Unidentified items and bags: 0. Lowering a table keeps saved augments; the extra ones show grey "(no slot)" and count nothing (**P1**).

### 2.6 Socket / unsocket rules

| Action | Rule |
|---|---|
| Add an augment | Anvil > Augments; the augment must fit the item kind (2.2 "Fits"); any element in any slot; atomic take-then-write with re-read + give-back on mismatch, bag take via `sacks:fn:take` / `commit`, stack split like Reforge (**P1** 7.1). Smithing XP `skill:fn:addxp` by tier (5 / 10 / 20 / 40 / 80) |
| Replace / Remove | **destroys the old augment** (D3 still fits: both kinds are craftable, it is the coin sink; confirm "It will be destroyed"). Row `aug.removeRefund` (% chance it returns, default 0). Q1 asks whether stat augments should come back instead |
| Add a slot | +1 max (`aug.extraSlots` 1): coins (2 x the Lv-10 reforge base for the rarity) + Smithing Lv 10 (**P1** rows) |
| Remove a slot | only an empty slot the player added, no refund (D2 "added and removed") |
| Reforge / level-up / Sigil / Upgrade / tier-up of gathering gear | keep `aug` + `augAdd` (doc clone; harness), a gathering-armor tier-up carries them to the new piece (gear.md 2026-10-24 "keeps its upgrades") |
| Salvage / NPC sale / AH | confirm "this item has 2 augments"; AH / trade / Vault / Requip carry the doc (UNVERIFIED X6) |

### 2.7 UI (Menu-Pattern, kit 1.7 hub page, HANDOFF 2)

**Crafting hub > Anvil > Augments** = the third Anvil sub-tab (`mode:7`), no new command (`/reforge` and `/smithing` open the Anvil).
Layout = **P1** section 7 (item list left filtered to `slots > 0`, held item + slot row top right as `ItemGridSlot new ItemStack(id, 1)`,
owned-augment scroll list right middle with "what it gives on THIS item", buttons ADD / REMOVE (confirm) / ADD SLOT / REMOVE SLOT,
result line). Added: a STAT | ELEMENTAL filter (two small sub buttons) over the owned list, and each row shows "Fits: weapon" red when it
does not fit. Fusing is the Alchemy Bench recipe (vanilla first); the page shows "3 make the next tier at the Alchemy Bench".

### 2.8 Tooltips (Style Guide 15 colours, Pets-tooltip sections, gear order rule 2026-10-24)

Item tooltip of a socketed weapon (after the stat lines, before set / flavor):
```
AUGMENTS  2 / 3                                   <- gold heading
 [Brute III]  +2.7 Strength  +3.2% Crit Damage     <- pip in the tier rarity colour; names #d6e4ee, values green bold
 [Fire IV]    +2.8% Fire Damage  Burning (Power 4) <- element name in its colour
 [ empty ]                                         <- dim grey
ELEMENT POWER  Fire 4                              <- only when > 0; "what it does" one line: "Hits set enemies Burning"
```
Augment item tooltip: title in tier colour; `T3 Augment - Brute (weapon)`; GIVES (values); FITS (weapon / armor / tool); USE ("Crafting >
Anvil > Augments", yellow); HOW ("3 make the next tier at the Alchemy Bench" for elementals, grey). Armor elementals add "Burning on you
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
| Tempo (w) | Attack Speed `as` +3 % (Q4) / until then Charged `chg` +3.6 % | Damage `dmg` +3.6 % (with chg) | DPS +4.2 % |
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

### 4.1 Values (per slot)

| Tier | Weapon: element damage (% of the hit, joins `f<E>`) | Weapon: Element Power | Armor: element Defence (joins `d<E>`) | Armor: status resist |
|---|---|---|---|---|
| I | 0.8 % | 1 | 1.5 | via Defence (5.4) |
| II | 1.2 % | 2 | 2.5 | |
| III | 1.8 % | 3 | 3.5 | |
| IV | 2.4 % | 4 | 5 | |
| V | 3.0 % | 5 | 6 | |

A Mythic weapon with 3 x Fire V = +9 % of the hit as Fire (x1.18 weapon slot power is NOT applied - flat) = **DPS +9 %** neutral,
about +11 % vs a Fire-weak mob, **less raw damage than 3 Brute V (+13 %) on purpose: the element pays you back in states and reactions** (the
"choose between them" of D1). Armor: 12 x Fire V = 72 Fire Defence -> `S/(S+D)` = 42 % less Fire damage, Burning on you 42 % shorter.
Poison augment (Q3): weapon +2 % Poison per tier V (the live `poison` key) + Poison Power; armor the same Poison line ("it all stacks", D4).

### 4.2 Element Power (what drives the states)

`P_e` (per hit, per element) = sum of socketed elemental tiers of e on the HELD weapon + 3 for each rolled `f<E>` / `r<E>` line of e
on it + 5 while Imbue of e runs. States scale with `s = min(P_e, 10) / 5` (P 5 = the base numbers in section 5, P 10 = double, cap).
So rolled element lines ALSO make elements "really work" (Skyy "unlike wynncraft where its just another damage number"), augments make
them strong. Charms, pets and `rElem` add DAMAGE only, never Power (they are not on the weapon).

### 4.3 No double counting

| Source | Adds | Rule |
|---|---|---|
| Elemental augment (weapon) | `W_e` (like a rolled `f<E>` line) + Power | joins `addAugE` once; opens the pet gate (`W_e > 0`) like a rolled line - intended (**P1** Q4) |
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
| **Wet** | Water hit (first one); standing in water; rain (Q7) | no damage; Burning can't start; sets up Thunder / Ice | tint #4fa8ff, `Water_Dripping` | 6 s; Fire (Steam), Earth (Mud) |
| **Chilled** | Water hit on a Wet / Chilled target; Air on Wet | -15 % move speed x s, 3 s | live Chill effect, `Impact_Ice`, `Weapon_Frost_Mist` | time; Fire (Thaw) |
| **Frozen** | 3 Chills within 3 s | can't move 1.5 s (vanilla Freeze via `freezeOne`) | `Effect_Snow`, ModelVFX Freeze | time; Fire (Melt), Earth (Shatter) |
| **Shocked** | Thunder hit | 3 s: takes +5 % damage; 30 % x s of the Thunder part jumps to 1 enemy within 3 blocks; **FLINCH** (Skyy "stagger") 0.25 s on every 2nd Thunder hit | `Hazard_Electric_Stun` particles (not the effect), `Lightning` arc, flinch = `Hit_Interrupt_Flinch` (X2) | time; Earth (Grounded) |
| **Quaked** (was "Stagger" in Classes) | every 3rd Earth hit | 0.4 s stun + -10 % Defence 4 s x s | `Ability_GroundSlam_Spike`, `Block_Hit_Stone` | time |
| **Gusted** | Air hit | +1 block knockback x s (Skyy "more knock back"), heavy hits lift; marks "Windswept" 2 s for Fire combos | `Ability_Windstrikes`, `Wind` | 2 s |
| **Poisoned** | Poison line / augment | live Wynn X/10 s DoT, stacks, never staggers (D4) | vanilla Poison look | time; Fire (Toxic Flare) |

A mob never gets its OWN element's state (a Fire mob can't burn, a Water mob is always Wet - the realistic part of the mob table).
Weapon aura: holding a weapon with an elemental augment shows that element on the blade (`FireSword` / `Lightning_Sword` / water drip /
`Buff_Windstrikes` / dust / `Buff_ImbuePoison`), player switch `gear.augFx`.

### 5.2 Interaction matrix (row = the element that HITS, column = a state the target ALREADY has)

| Hits \ has | Burning | Wet | Chilled / Frozen | Shocked | Quaked | Gusted (Windswept) | Poisoned |
|---|---|---|---|---|---|---|---|
| **Fire** | adds a stack | **Steam**: Wet ends, burst +25 % of the Fire part (Fire), no Burn this hit (`Goblin_Decorative_Steam`) | **Thaw / Melt**: Chill or Frozen ends -> Wet; vs Frozen +50 % of the Fire part | - | - | **Fanned**: Burning starts with +1 stack cap (4) and +50 % duration | **Toxic Flare**: 50 % of the poison left dealt at once to the target + a 2-block puff at 50 %; Poison ends |
| **Water** | **Douse**: Burning ends, Steam burst +25 % of the Water part, target Wet | -> Chilled (ice on a wet target - Skyy) | Chill counts **double** toward Frozen | **Conduct**: the Shock jumps to every Wet enemy within 4 (max 3) once | **Mud**: -25 % speed 3 s | - | **Dilute**: poison left -30 % |
| **Thunder** | - | **Electrocute**: Thunder part x1.5, sure flinch 0.4 s, jumps to every Wet enemy within 4 (max 3) | - (ice insulates) | refresh + jump | **Grounded**: Shock ends, its jump damage hits this target instead (+30 % of the Thunder part) | **Storm**: +1 jump, +2 blocks range | - |
| **Earth** | **Smother**: Burning ends, its remaining damage dealt at once | **Mud**: Wet ends, -25 % speed 3 s | **Shatter**: Frozen ends, +50 % of the Earth part | **Grounded** (as above) | counts to the next Quake | **Sandblast**: +20 % of the Earth part, target deals -10 % 3 s | - |
| **Air** | **Fan the flames** (Skyy): +1 stack (cap 4), +50 % time left, burn x1.25; spreads 1 stack to 1 enemy within 3 (**Wildfire**) | **Wind Chill**: Chilled | Chill +1 | **Storm** (as above) | **Sandblast** (as above) | more knockback | **Disperse**: 50 % of the poison spreads to 2 enemies within 3 |
| **Poison** | - | - | - | - | - | - | stacks (live) |

"-" = no reaction (Fire + Thunder, Thunder + Poison, Earth + Poison: nothing real happens). Reaction damage = `round(part x %)` of that
hit's element part after mob Weak / Resist, its own Damage with the element's cause.

### 5.3 Order inside one hit (multi-element weapons)

1. Snapshot the target's states. 2. For each element on the hit (Wynn order Earth, Thunder, Water, Fire, Air, then Poison) check the
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
in the element colour: STEAM, MELT, SHATTER, ELECTROCUTE, GROUNDED, STORM, MUD, WILDFIRE, TOXIC FLARE.

## 6. Build split, saved data, rollback, risks

### 6.1 Rounds (order)

| Round | Mods | Size | Content | Depends |
|---|---|---|---|---|
| P0 | none | main session, no agents | probes X1-X7; `balance_model.py` rows for 3.2 / 4.1 (a builder adds `aug_*` functions in a later model round); this spec's questions | - |
| **A1 effects engine** | SkyyClasses (+ SkyyMobs: Wet from water mobs, `elemOf` for own-element immunity) | **Full round** (ultracode lenses: thread rules, boss lock, PvP, double count, spam) | bridge `classes:fn:elemHit(Object[]{ UUID attacker, UUID victim, int[] power6, double[] parts6, Double hit, Boolean heavy })`; states 5.1 incl. NEW Wet + Gusted + Quaked rename; matrix 5.2; order 5.3; boss / PvP 5.4-5.5; reaction popups; Imbue routed through it; rows `elem.*` | live elem1 set |
| **A2 sockets + items** | SkyyGear + SkyySacks (Combat bag) + `tools/tier_tags.py` | **Full round** (saved item data, item loss / dupe, damage sums, 95 items) | 2.2-2.8, 3, 4: `aug` / `augAdd` doc keys, `addAugE`, Power per hit -> `classes:fn:elemHit`, Anvil Augments tab, tooltips, recipes, auras | A1 pinned (Gear calls the bridge; missing bridge = damage only, ready line says so) |
| A3 sources | SkyyMobs + SkyyMerchants + loot | Lean | drops, pre-filled loot, merchant T1 | A2 |
| A4 charts | SkyyMenu | Lean | Reactions chart = 5.2 (replaces "later"), states list, Element Power on YOUR STATS | A1 |
| A5 | SkyyGear | Lean | Tempo's Attack Speed once `as` is live (Q4), gathering armor slots (Q5) | answers |

A1 + A2 deploy together (one batch, one smoke test by the main session); A3 / A4 can follow. Launch via `skywynn-round` with D1's quote.

### 6.2 Saved data + migrations

- Item doc keys `aug` (BsonArray of BsonString `"S:Brute:3"` / `"E:Fire:4"` / `""` empty) and `augAdd` (Int32). grep 0.3.46 found no
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
`aug.slotLevel` 10, `aug.stat.<Kind>` (T5 pair values), `aug.tierScale` 40 / 55 / 70 / 85 / 100, `aug.elem.weapon` / `aug.elem.armor` /
`aug.elem.power` (4.1), `aug.removeRefund` 0, `aug.xp`, `aug.loot.prefill` 10. Classes: `elem.on`, per state numbers (`elem.burn.*`,
`elem.wet.time`, `elem.chill.*`, `elem.freeze.*`, `elem.shock.*`, `elem.flinch.*`, `elem.quake.*`, `elem.gust.*`), each reaction %
(`elem.react.<Name>`), `elem.reactCd` 1.0 s, `elem.bossImmune` 8 s, `elem.pvp.*`, `elem.rainWet`. Mobs: `aug.drop.*`.

### 6.5 Risks

| Risk | Guard |
|---|---|
| Item dupe / loss on add / remove | **P1** 7.1 atomic order + re-read + harness H1-H9 equivalents |
| CC lock on bosses / players | 5.4 / 5.5 clocks; harness: 1,000 Thunder + Water hits on a boss fixture never exceed the duty cap |
| Particle / packet spam (fast weapons, big packs) | reaction cd 1 s, max 1 reaction popup per hit, chain max 3, particles only for viewers that see the mob |
| Double count with Imbue / pets / charms | 4.3 + harness identity: no augments -> Gear sums byte-identical to 0.3.46 |
| Thread rules | Gear's hit system only queues `classes:fn:elemHit`; all state work on the world thread (Classes' job queue, as `classes:fn:dot`) |
| 95 items + lang keys | one writer (SkyyGear), `tools/ci/langdup.py`, build asserts no vanilla id shadowed |
| Power creep | P0 model sign-off; one T5 weapon slot = +4.2 % DPS cap stays a row |

## 7. Questions for Skyy (defaults in brackets; the build uses the default until answered)

| # | Question | Default |
|---|---|---|
| Q1 | Taking an augment out destroys it (your Powders answer). Keep that for STAT augments too, or give stat ones back? | [destroy both; a refund % row exists] |
| Q2 | Your 2026-10-11 gems idea said "no levels". Stat augments: 5 tiers (one per zone, crafted fresh, never fused) or one flat strength? | [5 tiers, no fusing - they stay useful in every zone] |
| Q3 | Add a Poison augment (from Venom Sacs) next to the 5 elements? | [yes] |
| Q4 | Tempo (Attack Speed + Damage) needs Attack Speed made live on gear first. Build that, or use Charged Damage + Damage until then? | [Charged + Damage now, Attack Speed later] |
| Q5 | Should gathering armor also get augment slots (1 per piece from Zone 2), or only the lifelong tools? | [both] |
| Q6 | Name: Augments, Infusions or Facets? | [Augments] |
| Q7 | Rain makes players and mobs Wet (so Thunder hits harder in storms)? | [yes, row elem.rainWet] |
| Q8 | Interactions now come built in (your new idea replaces "reactions later as tree nodes"). Should class trees still get nodes that make reactions stronger later? | [yes, later] |
| Q9 | Socket Reforge has "Resonance" (a full item with a set order of augments gets a hidden bonus). Want something like it later? | [later, not v1] |

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
| X8 | `manap` (Mana %) on gear: deliver through the same `modPct` path SkyyPets 0.4.8 uses, without a second writer on the Mana stat | read SkyyPets 6389-6391 + SkyySkills mana |
