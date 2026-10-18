# Wynn elements - BUILD spec (Earth / Thunder / Water / Fire / Air + Poison status)

Build spec, 2026-10-18. Nothing built. Owner: Skyy (they/them). Where this goes: `research/` (INDEX.md "research"); answers to the
Questions at the end go to `docs/answered/gear.md` (`python tools/qa_append.py gear ...`); build results to `docs/log/2026-10.md`.
Design layer: `research/Wynn-Elements-Spec.md` (decisions) on `research/cloud/Element-System-Spec.md` (numbers, statuses, mob table,
probes). This file turns them into one build: data model, formula, each mod's job with exact bridge keys, rows, popups, plates, charts,
tests, builder split. Code facts below were read from the SET pins (`tools/deploy_set.py` 2026-10-18: SkyyGear 0.3.25 pinned, 0.3.26
built and uncommitted; SkyyMobs 0.1.10; SkyyClasses 0.1.38; SkyyAccessories 0.5.26; SkyyPets 0.4.3; SkyyHud 0.3.32; SkyyMenu 0.3.39).
Line numbers are from those scripts; re-verify at build (a builder derives from the pin of its day).

## 0. Decision lines (every one followed here; Skyy's words in `docs/answered/gear.md` 2026-10-18 + `classes.md` 212-213)

| # | Decision (Skyy, 2026-10-18 unless noted) | Where it lands in this spec |
|---|---|---|
| D0 | ELEMENTS FIRST: "get the Windcraft elements built before you go too crazy on the UTs ... I want to use the elements in cool ways with the special items" | this build runs BEFORE the big UT batch; section 11 order |
| D1 | Q1 Imbue: "Pick out of combat" (a menu like the Bubble choice; default Fire; player sets the swap order) | SkyyClasses already does this (0.1.25 attune, out of combat, default Fire); 4.3 keeps it, only the names change |
| D2 | Q2 Charms: "yes, have them start weak but get powerful!" | 4.5: five single-element charm lines on a T1-T5 ladder + the Elemental Power |
| D3 | Q3 Pets: "most pets have an element, and they can have any element. (most pets just boost your elemental defense against that element, and increase your damage (but only if you use its element. so if its +10 fire damage. if you dont have fire damage on your weapon, it doesnt do anything. but if your weapon has 5 fire damage, it does 15)" | 3.2 pet rule (weapon gate); 4.4 pet element table |
| D4 | Q3 (same answer): "show a hit popup per element you did damage in. instead of adding it all together for 1 damage number" | section 7: one coloured number per element dealt |
| D5 | Q4 Defence: "Now" | 3.4 armor element Defence live in this build -> mobs must deal element damage in the SAME build (4.1 mob element hits) |
| D6 | Q5 Mob table: Resist -25 / Weak +25 / boss -50 / never immune / Fire + Frost dragon bosses keep their element: "Yes" | 4.1 `elem.mobs` + the wheel |
| D7 | Q6 Reactions: "Later, as tree nodes" | none built; the reactions chart lists them as "later" (section 9) |
| D8 | Q7 Name plates: "show what elements the mob has/ uses. so if its a fire mob, it shows fire above it, and the player has to know from that, that it is weak to water. (we can make a chart showing which elements each element is strong and weak to. and another showing what reactions cause what" | section 8 plate marker = the mob's OWN element; section 9 two charts |
| D9 | Q8 Poison: "yes do poison. (do it like wynncraft where you get like 50/10 ... procs every second (poison damage doesnt stagger ...) but you can also get poison on your combat armor and it all stacks (hytale already has a poison effect some mobs give. and thorium armor is already resistant to it.)" | 3.5 Poison X/Ys on weapons AND combat armor, stacking, no stagger, vanilla poison look, Thorium resists |
| D10 | Q9 Elemental swords: "Yes, after elements ship" | not in this build (a lean round after, section 11) |
| D11 | Q10 Powders: "Yes, next spec" | not here; 3.1 leaves the per-element split ready for powder lines |
| D12 | classes.md 213 (2026-10-17): Wynn names everywhere, "Lightning -> Thunder, Wind -> Air", Gravity sword = Earth | 2.1 names; SkyyClasses renames its internal Lightning / Wind |
| D13 | classes.md 212: Imbue all 5, each with its status; Poison = a status | 2.1 / 4.3 |
| D14 | `SkyyGear-Plan.md` lock 17 (read only): flat element = weapon only; element damage on its own, then cut / raised by affinity + element defence; single-element defence = armor only; all-element % = class trees; raw elemental spell damage = skill trees + accessories | 3.1-3.4 formula; charms add RAW element (allowed), pets gate on the weapon (D3) |
| D15 | PROJECT-RULES 4: four power sources; everything in Server Setup; no dev gates (default ON); tier tags; no duplicates (one DoT engine, one popup path) | section 5 rows; 4.3 owns every DoT tick; 7 reuses the CRIT! popup path |

## 1. What is live today (read from the pins - do not rebuild)

| Mod | Fact (script, lines) |
|---|---|
| SkyyGear 0.3.26 | weapon lines `fEarth fThunder fWater fFire fAir` (max 6, w 4), `rThunder rWater` (max 6), `rElem` "Raw Elemental Damage" (max 3, counts 5x) - LIVE (2674-2681); armor `dEarth..dAir` "X Defence" max 10 live 0 (2697-2701); `poison` "Poison" w max 20 live 0 (2693). `GearHit.elemSum` = one int (26221), carried in `GearHit.info` slot [5] (26229), swing-weighted by `GearSpeed.scaleInfo` (21541), added AFTER armor + Defense by `GearTrueSys` (28410-28418, "affinities are a later stage"). Stat totals: `GearStats.totals` = rolled gear + `extra(u)` = `gear:extra:<uuid>` string (SkyyAccessories) + `pets:stats:<uuid>` Map (SkyyPets), parsed by SkyyGear stat key - any S_KEY, so `fFire` / `dFire` keys would already flow in (22366-22445). Armor: SkyyGear hides the vanilla armor box and applies EVERY resistance entry itself (Physical / Projectile levelled + Fire / Poison / FLAT per cause) in `GearArmorSys` -> `GearArmor.fix` (1716-1724, 28374-28400): Thorium's `Poison 0.27 Percent` per piece (Assets `Armor_Thorium_Chest.json`, VERIFIED) is applied by us. CRIT! popup = a second `CombatTextUpdate(angle - 20, text, (Color) null)` queued to the attacker's EntityViewer after `viewer.visible.contains(mob)` (28084-28145); `Gear.notifyOn(uuid, "gear.critFx")` = the player switch. `family(cause)`: Physical 1 / Projectile 2 / anything else 0 = not a weapon hit (26268). `mob:fn:levelAt` read; `class:fn:abilhit` NOT read. |
| SkyyClasses 0.1.38 | Imbue ALL 5 + Poison already built (0.1.25): `ELN = Fire, Water, Earth, Lightning, Wind, Poison` / `ELS = Burn, Chill, Stagger, Shock, Gust, Poison` (8453-8454); `attune` out of combat, default Fire, "next" cycles the 5, Twin Attunement = PA1 (att1 / att2 in the ability file); `elemIdx` already accepts "Thunder" / "Air" as aliases (14587-14589); `statusOn` applies the six statuses with boss halving (14735-14816); `dotOn` / `dotTick` = the one DoT engine (per-second ticks, stacks, "ElemBurn" / "ElemPoison") (14684, 14721); every ability / tick hit = `new Damage(EntitySource(caster), PROJECTILE, amt)` tagged by `AbilDmg` (16528-16537); bridge `class:fn:abilhit(Damage) -> UUID caster` (21255); `classes:fn:imbue(uuid) -> "Fire;30"` published (21268); the Spellblade hit multiplier x(1 + 30 %) is applied by Classes UNTIL `gear:imbue` = TRUE on the bridge (15760-15763). Priest Elemental Bubble picks 1 of 5 (bubPick). Rows `ab.Elements.numbers` (burn / chill / freeze / stagger / shock / gust / poison / bossCc). Hub tab `hub:tab:character:class`. |
| SkyyMobs 0.1.10 | no element data. Role glob matcher `MobGlob` (any case, exact, `Prefix*`, `*Part*`), tables `scale.role` (type "table", `check=` hook), rows `bosses.roles` (default `Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*`) + `bosses.zoneTops`; `mob:fn:boss`, `mob:fn:level`, `mob:fn:info`, `mob:fn:levelAt`, `mob:fn:credit`, `mob:fn:setLevel` (5157-5162). Name plate = ONE text: `plateText(level, name)` from `plate.format` "[Lv {level}] {name}" + the TRIAL colour markup (2799-2805; engine `Nameplate.setText(String)` only - VERIFIED reflect). |
| SkyyAccessories 0.5.26 | `gear:extra:<uuid>` text from `AccGear.textOf` with `GEAR_ALLOW = (str, mp, def, cc, cd)` only (1813-1815); lines = `BOOSTERS` (family, admin, line, crystal, gem, entries, sources, flavour, recipes, style "word" = folded 4-step Workbench ladder / "T" = new lines, no recipe, admin give); Accessory Power `PW_TABLE` (15 Powers, `PW_GEARK = def str cc cd mp`); Void Charms hub tab; `acc:fn:has`, `acc:fn:power`. |
| SkyyPets 0.4.3 | `KINDS` (name, skill, rarity, "str:20,cd:15", role, zone) x 39, `STATS` keys with delivery `gear` -> `pets:stats:<uuid>` Map (3749-3795); no element. |
| SkyyHud 0.3.32 | no damage-number code (the CRIT! popup lives in SkyyGear). Nothing to build here. |
| SkyyMenu 0.3.39 | Character > Skills tab holds the sub-tab row YOUR STATS / SKILLS (`ST_SUBTABS`, 2695; one scroll list with headings, Menu-Pattern M4). |
| Engine (HytaleServer.jar 0.7.2, reflect VERIFIED) | `protocol.Color(byte, byte, byte)`; `CombatTextUpdate(float hitAngleDeg, String text, Color color)`; `DamageCause` is an ASSET (`DamageCause.getAssetMap()`, fields PHYSICAL PROJECTILE ... only); Assets `Server/Entity/Damage/`: `Earth Fire Ice Lightning Water Wind Poison Elemental ...` (Fire = Parent Elemental, DamageTextColor #FF6B2B; Poison #228B22); effects `Status/Burn.json` (Fire 5 / s, tint, ModelVFX Burn), `Status/Poison.json` (Poison 10 per 5 s, tint #008000, particles Effect_Poison, 16 s), `Poison_T1..T3`, `Immunity_Poison`. |

## 2. Data model

### 2.1 The elements (one order everywhere on the bridge and in text)

| i | Name (the only spelling in text + bridge) | Gear keys | Engine DamageCause id (ticks only) | Status (SkyyClasses) | Colour (popups, rows, charts) |
|---|---|---|---|---|---|
| 0 | Earth | fEarth / dEarth | Earth | Stagger | #C0905A |
| 1 | Thunder | fThunder, rThunder / dThunder | Lightning | Shock | #FFD84D |
| 2 | Water | fWater, rWater / dWater | Water | Chill -> Freeze | #4FA8FF |
| 3 | Fire | fFire / dFire | Fire | Burn | #FF6A3D |
| 4 | Air | fAir / dAir | Wind | Gust | #A5EDE0 |
| - | Poison (status, never an element) | poison (w + a) | Poison | Poison X/Ys | #7ED957 |

The wheel (Wynncraft's): **Earth > Thunder > Water > Fire > Air > Earth** ("beats" = the target is Weak +25 % to it). So a Fire mob
resists Fire and is weak to Water; Water mob weak to Thunder; Thunder mob weak to Earth; Earth mob weak to Air; Air mob weak to Fire.
Bridge string `mob:elem:wheel` = `"Earth>Thunder>Water>Fire>Air"` (SkyyMobs publishes, SkyyMenu draws the chart from it).
SkyyClasses keeps its own index order internally but every String it puts on the bridge or shows uses the names above (D12).

### 2.2 Per-hit element vector (SkyyGear, in-process only)

`int[5] split` in Wynn order, added to `GearHit.info` as slot **[6]**; slot [5] keeps the sum for old readers. `GearSpeed.scaleInfo`
weights each of the five like the sum. `GearHit.elemSum(t)` stays (= sum of the five with no modifiers - the harness identity).

### 2.3 Saved data

None new. Pets' element and charms' element are build tables + Server Setup rows; a player's Imbue attunement is already in the
SkyyClasses ability file (`att1` / `att2` - the saved words "Lightning" / "Wind" stay readable through `elemIdx`'s aliases and are
rewritten to Thunder / Air on the next attune). Mob element data = config tables only.

## 3. Damage formula (one weapon hit of a PLAYER; all rounding = SkyyGear's `sat` / Java round, as today)

Let `N` = the neutral hit after today's chain (base x level mult x swing weight, Damage %, Strength / Magical Power, charged, crit) -
unchanged, so an empty element build equals 0.3.26 exactly.

### 3.1 Raw element parts (attacker side, GearHitSys)

For each element e (Wynn order):

```
W_e = weapon rolled lines of e            (fX + rX + rElem; ROLLED gear only = totals(withExtra=false))
C_e = charm / Power lines of e            (gear:extra:<uuid> keys fX / rElem - SkyyAccessories; unconditional: lock 17 "raw elemental" on accessories)
P_e = pet line of e                       (pets:stats:<uuid> key fX - SkyyPets)
I_e = Imbue part                          (= round(N x imbuePct / 100) for the ONE element classes:fn:imbue names, else 0; Spellblade weapon hits only)
raw_e = W_e + C_e + (W_e > 0 ? P_e : 0) + I_e          <- D3: the pet counts only when the WEAPON already deals e (+10 pet, 5 weapon = 15; 0 weapon = 0)
```
Then `raw` is swing-weighted (`scaleInfo`, stochastic rounding, as the sum is today). `rElem` counts once per element (5x in the sum,
exactly as today). Ability / DoT Damage (`class:fn:abilhit(d) != null`, or any cause with `family == 0`) gets NO split and no Imbue part
(E1 closed by design: ticks use their element's DamageCause -> family 0 -> never a weapon hit).

### 3.2 Target modifiers (GearTrueSys, after armor and Defense, never crit)

```
mob victim:    dealt_e = round(raw_e x (1 + mod_e / 100))     mod_e = mob:fn:elem(roleId, e) in {+25, -25, -50, 0}; players / unknown = 0
player victim: dealt_e = round(raw_e x S / (S + D_e))         D_e = gear:fn:elemDef(victim, e) (armor dX + pets dX + charms dX), S = elem.defScale (100)
total added  = True Damage + sum(dealt_e)                      (today: True Damage + elemSum)
```
Weak / Resist / boss values live in SkyyMobs (the function returns the final %), so SkyyGear carries no mob numbers. Cache per role id
for 5 s in SkyyGear (`mob:fn:elem` is any-thread, never throws, returns Integer).

Worked example (python3, N = 100, Imbue Fire 30 %, weapon 5 Fire, pet +10 Fire, charm +4 Fire): raw_Fire = 5 + 4 + 10 + 30 = 49 ->
neutral mob 49, Weak (+25) 61, Resist (-25) 37, Fire-boss (-50) 25; popups "100" white + "49 Fire" orange. Same weapon without any Fire
line: raw_Fire = 4 + 0 + 30 = 34 (the pet gives nothing - D3).

### 3.3 Mob -> player element damage (SkyyMobs, needed because Defence is ON now - D5)

A mob whose `elem.mobs` row names an element deals `elem.mobShare` % (default 30) of each of its hits as that element: in SkyyMobs' own
Filter damage system (the one that already scales mob damage; victim = player): `part = amount x share / 100`,
`cut = part x (1 - S / (S + D_e))` with `D_e = gear:fn:elemDef(victim, e)` (null / no SkyyGear = 0), then `d.setAmount(amount - cut)`.
A naked player takes exactly today's damage; element Defence only ever lowers it. No cause change (vanilla Fire resistances keep working
on real Fire-cause hits, which stay untouched). Lava / vanilla Burn are not touched in v1 (E7 later).

### 3.4 Element Defence lines go live (SkyyGear)

`dEarth..dAir` live 0 -> 1 (armor only, max 10, weight 3). Already-rolled items are untouched; new rolls and reforges can roll them. Tooltip
line stays "+8 Fire Defence" (grey "coming later" ends). `gear:fn:elemDef` sums worn active armor dX + `pets:stats` dX + `gear:extra` dX.

### 3.5 Poison (D9) - Wynn X/Ys, weapons AND combat armor, stacks, never staggers, vanilla look

- Gear line `poison` goes live on slot **"wa"** (weapon + armor), value = damage over `poison.time` s (default **10**): "+50 Poison" reads
  "50/10s" on the tooltip (`Poison 50 / 10 s`). Rolls like any flat line (max 20 per line; PLACEHOLDER - Skyy's 50/10 example at Lv 40
  Legendary needs max ~40: row `poison.max`).
- On every weapon hit that lands (GearLeechSys stage, where Life Steal is owed): `P = totals[poison]` (weapon + worn armor + charms + pets,
  the normal totals - "it all stacks") > 0 -> `classes:fn:dot(Object[]{ UUID attacker, UUID victim, "GearPoison", "Poison", Double P / time,
  Double time, Integer poison.stacks (3) })`. SkyyClasses' one DoT engine ticks it every second (stack rule = Burn's: a new application past
  the cap refreshes the oldest). No SkyyClasses on the server = the line does nothing (ready line says so). ONE DoT engine - no duplicate.
- The tick Damage uses the engine DamageCause asset **"Poison"** (`DamageCause.getAssetMap()` lookup by id at start, cached; missing ->
  PROJECTILE + one WARN) so (a) SkyyGear's `family()` = 0 -> no weapon lines on ticks, (b) SkyyGear's own armor pass applies Thorium's
  Poison 27 % per piece (and `Immunity_Poison` mobs take 0 - acceptable, it is vanilla's rule), (c) the death message is vanilla's poison one.
- No stagger: the tick is a plain Damage with no knockback meta and no hurt animation request; UNVERIFIED whether the engine still plays
  the hurt flinch on NPCs for a 0-knockback Damage (probe P3). Vanilla look: apply the vanilla EntityEffect **`Poison`** for the DoT's
  duration ONLY IF a damage-free variant works (probe P4: our own asset `Server/Entity/Effects/Status/SkyyGear_PoisonMark.json` with
  Parent Poison and `DamageCalculator.BaseDamage.Poison 0`); else the tint-only route Classes already uses for ElemPoison (particle FX_TOXIN).
- Popup: each tick shows vanilla's white number (its own Damage). v1 adds no coloured tick numbers (Question Q3).
- Mobs that already poison players (vanilla Poison effects) stay vanilla; Thorium already resists them - nothing to do.

## 4. Each mod's job (bridge = `System.getProperties().get("skyy.bridge")`, plain java.lang types only; every fn any thread, never throws)

### 4.1 SkyyMobs 0.1.11 (builder B1) - the mob side

| Piece | Exact shape |
|---|---|
| Table `elem.mobs` (Server Setup -> Mobs -> Elements) | 1-column table (keeps `\|`; the multi-column text table is UNVERIFIED in the kit - CONFIG-CONTRACT "1-column tables keep `\|`"), one line = `Match\|Element[\|Resist\|Weak]`: Match = MobGlob pattern (same matcher as `levels.roles`); Element = the mob's OWN element (Earth / Thunder / Water / Fire / Air / none); Resist / Weak optional overrides (blank = the wheel: Resist = own element, Weak = the one that beats it). Longest literal match wins, first row on a tie. `check=` hook refuses unknown words. |
| Defaults (from the cloud draft section 6, role ids VERIFIED only where SkyyMobs' built-in list has them - builder fills the rest from `MobCfg.VANILLA`) | `Skeleton*\|none\|none\|Fire` `Zombie*\|none\|none\|Fire` `*Burnt*\|Fire` `Golem_Crystal_Earth*\|Earth` `*Earthen*\|Earth` `Fen_Stalker*\|Water` `Scarak*\|Earth\|Earth\|Water` `Cactee*\|Earth\|Earth\|Water` `Golem_Sandswept*\|Earth\|Earth\|Water` `Yeti*\|Water\|Water\|Fire` `Golem_Frost*\|Water\|Water\|Fire` `Golem_Firesteel*\|Fire` `Emberwulf*\|Fire` `Pterodactyl*\|Air\|Air\|Thunder` `*_Void*\|Thunder\|Thunder\|Fire` `Void_*\|Thunder\|Thunder\|Fire` `Piranha*\|Water\|Water\|Thunder` `Shark*\|Water\|Water\|Thunder` `Dragon_Fire*\|Fire` `Dragon_Frost*\|Water`. Beasts / folk: no row = neutral. |
| Rows | `elem.weak` 25 (0-100 %), `elem.resist` 25 (0-90 %), `elem.bossResist` 50 (0-90 %), `elem.mobShare` 30 (0-100 % of a mob's hit dealt as its element), `elem.plate` bool true (element on the plate), `elem.wheel` text default `Earth>Thunder>Water>Fire>Air` (5 names, each once; `check=`). All live. |
| `mob:fn:elem` | apply(Object[]{ String roleId, String element }) -> Integer: +weak if element == the row's Weak, -bossResist if the role matches `bosses.roles` AND element == its own element, -resist if element == its Resist, else 0. Unknown role / element / bad args -> 0. Cached per (role, element). |
| `mob:fn:elemOf` | apply(String roleId) -> String own element or null. |
| `mob:elem:wheel` | String, the `elem.wheel` value (re-put on edit). |
| Mob element hits | section 3.3 in the existing mob-damage Filter system; reads `gear:fn:elemDef` (absent = 0). |
| Plate | section 8. |
| Ready line | `[SkyyMobs] 0.1.11 ready ... elements: N rows, wheel Earth>...`. |

### 4.2 SkyyGear 0.3.27 (builder B2) - the formula, Defence + Poison live, popups

| Piece | Exact shape |
|---|---|
| Split | 2.2 + 3.1 + 3.2 in `GearHit.weaponHit` / `GearTrueSys`; `GearHit.info` slot [6]; `elemSum` identity kept. |
| Imbue | reads `classes:fn:imbue(uuid)` (String "Fire;30" -> element name (Wynn or old alias), pct); adds `I_e`; then puts `gear:imbue` = Boolean.TRUE on the bridge at start (SkyyClasses then stops its own x1.30 - no double count, 15760). Remove in shutdown. Only when `elem.on`. |
| Defence | 3.4; `gear:fn:elemDef` apply(Object[]{ UUID player, String element }) -> Integer (0 when unknown / offline). |
| Poison | 3.5; calls `classes:fn:dot`; rows `poison.time` 10 s (1-60), `poison.stacks` 3 (1-10), `poison.max` 20 (1-200, the line max). Tooltip "Poison 50 / 10 s". `poison` line slot "wa", live 1. |
| Popups | section 7; row `elem.popup` (off / number / word, default **word**); player switch `gear.elemFx` (settings kit, like `gear.critFx`). |
| Stats | `gear:fn:elemTotals` apply(UUID) -> String `"Earth:3/8,Thunder:0/2,Water:5/0,Fire:49/12,Air:0/0,Poison:50"` = damage/defence totals the player would deal with the held weapon (W + C + gated P, no Imbue) / their Defence; SkyyMenu's rows read it. |
| Tooltip colours | each element line NAME in its colour where the tooltip path takes a colour (E6 - UNVERIFIED; plain text if not). |
| Row `elem.on` | bool true; off = 0.3.26 behaviour (one sum, no modifiers, no Imbue part, no popups; Defence lines still roll - they are items). |
| Crosscheck | `python tools/ci/crosscheck.py --jar SkyyGear/SkyyGear-0.3.27.jar --baseline`; harness identity (section 10). |
| Ready line | `... elements ON (mob:fn:elem found/missing, classes:fn:dot found/missing, imbue via classes:fn:imbue)`. |

### 4.3 SkyyClasses 0.1.39 (builder B3) - names, the DoT bridge, affinity on ability element damage

| Piece | Exact shape |
|---|---|
| Names | `ELN` -> `Fire, Water, Earth, Thunder, Air, Poison` (index order unchanged); `elemIdx` keeps "Lightning" / "Wind" as read aliases; every text (attune reply, panel [112], Bubble row, numbers help) says Thunder / Air (D12). `classes:fn:imbue` returns the new names. |
| `classes:fn:dot` | apply(Object[]{ UUID attacker, UUID victim (an NPC's or a player's entity UUID), String what, String causeId, Double perSec, Double secs, Integer stacks }) -> Boolean (queued; false = bad args / victim not found / abilities off). Runs `dotOn` on the world thread (the WANT / job queue it already has); `what` distinct per caller ("GearPoison" stacks apart from "ElemPoison" - Skyy: "it all stacks"). |
| Tick causes | `dotTick` and `hit()` for status damage use the element's DamageCause ASSET by id (2.1 column 4) when `what` starts with "Elem" / the dot carries a causeId; abilities' direct hits keep PROJECTILE (their lines are the ability's). Lookup once at start (`DamageCause.getAssetMap()`), fallback PROJECTILE + WARN. |
| Affinity on Classes' own element damage | Burn ticks, Shock jump damage, Frost Nova (Water), Meteor (Fire), Bubble damage: x (1 + `mob:fn:elem(role, element)` / 100) when SkyyMobs is there (role via `roleOf`). Gear's split never touches these (3.1). |
| Boss immunity | unchanged (Gust boss-immune, cc halving) - the mob table never makes anything immune (D6). |
| Attunement UI | unchanged (D1 already true). `ab.Elements.numbers` keys unchanged. |

### 4.4 SkyyPets 0.4.4 (builder B4) - one element per pet

| Piece | Exact shape |
|---|---|
| Table `pets.element` (Server Setup -> Pets) | 1-column lines `Kind\|Element` (none = no element). Defaults (D3 "most pets"; PLACEHOLDER): Wolf Air, Fox Fire, Boar Earth, Hawk Air, Ram Earth, Skrill Thunder, Tusker Earth, Mouflon Water, Skeleton none, Goat Earth, Warthog Earth, Bear Earth, Turkey none, Rabbit none, Chicken none, Horse Air, Camel Fire, Rat none, CrystalGolem Earth, Molerat Earth, Moose Water, Owl Air, Antelope Air, Deer none, Mosshorn Earth, Bison Earth; dragons later: Plain = Earth, Tundra = Water (gear.md Q3). |
| Values | two new STATS keys delivered `gear`: `f<E>` (element damage, pet rule gated by SkyyGear) and `d<E>` (element Defence, always). Per rarity at the 0.2.x scale (then `_boost_stats` like every kind): Common 2 / 4, Uncommon 3 / 6, Rare 5 / 10, Epic 8 / 16 (PLACEHOLDER rows `pets.elemDmg` / `pets.elemDef` "2 3 5 8" / "4 6 10 16"). |
| Pets page | the pet card shows "Fire: +8 damage (with a Fire weapon), +16 Fire Defence" in the element colour. |
| Rollback | 0.4.3 ignores the table; SkyyGear 0.3.26 skips the unknown-to-it keys? NO - `fFire` IS a known key in 0.3.26, so an old SkyyGear would count pet Fire damage UNGATED into its sum: deploy Pets 0.4.4 only WITH Gear 0.3.27 (go-together). |

### 4.5 SkyyAccessories 0.5.27 (builder B5) - element charms + the Elemental Power

| Piece | Exact shape |
|---|---|
| Lines | five new `BOOSTERS` of style "T" (no recipe, admin give; acquisition = the next loot pass like every T line): family `Earth` / `Thunder` / `Water` / `Fire` / `Air` ("Earth Charm I..V"? names from `tools/tier_tags.py` rule: tier tag first in flavor text "T1 Charm - ..."). Entries per tier T1..T5 (D2 weak -> powerful; PLACEHOLDER, Server Setup): element damage `f<E>` 2 / 4 / 7 / 11 / 16, element Defence `d<E>` 3 / 6 / 10 / 16 / 25. One per family counts (best tier), as every line. |
| Elemental Power | `PW_TABLE` += ("Elemental", "Elemental", 0, [("hp", 3), ("def", 1), ("rElem", 2), ("mp", 3)]) per 100 AP (Combat group, starter-eligible) - `rElem` = raw all-element, counts once per element in the split. |
| Keys | `GEAR_ALLOW` += fEarth fThunder fWater fFire fAir rElem dEarth dThunder dWater dFire dAir (SkyyGear parses any S_KEY - VERIFIED parseExtra). |
| Tier tags | ids `Skyy_Charm_<E>_T1..T5` into `tools/tier_tags.py` (T1-T5, own ladder "T3 Charm"). |

### 4.6 SkyyMenu 0.3.40 (builder B6) - rows + the two charts (section 9)

### 4.7 Not touched

SkyyHud (no number code), SkyyTrees (reactions / element nodes = later), SkyyArmory (Elemental swords = D10 later), SkyySkills.

## 5. Server Setup rows (times in seconds; every number above is a row - summary)

| Mod | Key | Label | Type | Default | Range |
|---|---|---|---|---|---|
| SkyyMobs | elem.mobs | Mob elements | table (1-col) | section 4.1 | 200 lines |
| SkyyMobs | elem.weak / elem.resist / elem.bossResist | Weak bonus / Resist cut / Boss own-element cut | int % | 25 / 25 / 50 | 0-100 / 0-90 / 0-90 |
| SkyyMobs | elem.mobShare | Mob hit dealt as its element | int % | 30 | 0-100 |
| SkyyMobs | elem.plate | Element on the name plate | bool | true | - |
| SkyyMobs | elem.wheel | Element wheel | text | Earth>Thunder>Water>Fire>Air | 5 names |
| SkyyGear | elem.on | Element system on | bool | true | - |
| SkyyGear | elem.defScale | Element Defence scale | int | 100 | 10-1000 |
| SkyyGear | elem.popup | Element hit numbers | choice | word | off / number / word |
| SkyyGear | poison.time / poison.stacks / poison.max | Poison seconds / stacks / line max | dec / int / int | 10 / 3 / 20 | 1-60 / 1-10 / 1-200 |
| SkyyClasses | ab.Elements.numbers | (existing statuses) | numbers text | unchanged | - |
| SkyyPets | pets.element / pets.elemDmg / pets.elemDef | Pet elements / damage by rarity / Defence by rarity | table / text / text | 4.4 | - |
| SkyyAccessories | charm.elemDmg / charm.elemDef / power rows | Element charm damage T1-T5 / Defence T1-T5 / Elemental Power | text / text / existing | 4.5 | - |
| player Settings (SkyyGear via the settings kit) | gear.elemFx | Coloured element hit numbers | bool | on | - |

## 6. Migrations (one-time, PROJECT-RULES 4 rules: only old-default lines, History snapshot, Undo line, run-once marker)

| Mod | What | Why safe |
|---|---|---|
| SkyyGear | none to files. `dEarth..dAir` + `poison` live flags are build constants (0 -> 1); existing items keep their rolls; "coming later" grey text disappears for these lines. | no saved-data shape change; rollback to 0.3.26 = the lines show grey again, nothing lost |
| SkyyClasses | none. Saved `att1` / `att2` "Lightning" / "Wind" read through aliases; written as Thunder / Air on the next attune. Bubble pick the same. | rollback to 0.1.38 reads "Thunder" / "Air" through its own aliases (14587-14589 - VERIFIED) |
| SkyyMobs / SkyyPets / SkyyAccessories | new rows read with defaults while missing; a fresh file carries them; the kit appends on first edit (the 0.1.10 `bosses.*` pattern). | - |
| Go-together | Gear 0.3.27 + Pets 0.4.4 + Accessories 0.5.27 deploy TOGETHER (4.4 rollback note: an old Gear would count pet / charm element keys ungated); Mobs 0.1.11 + Gear 0.3.27 together (Defence ON needs mob element hits in the same build - D5). | floor comment in `tools/deploy_set.py` |

## 7. Per-element hit popups (D4) - engine facts + design

Facts (SkyyGear 0.2.2 research + 0.2.24, re-asserted at every build): vanilla queues ONE `CombatTextUpdate(hitAngle, text, color)` per
landed hit to the ATTACKER's EntityViewer in `DamageSystems$EntityUIEvents` (Inspect group) with text = the final `d.getAmount()`; a
`Color` of null = the entity's CombatText style colour (white); the client draws one popup per CombatText style the entity carries; the
font is ASCII only (no symbols); `Color(byte, byte, byte)` exists (VERIFIED reflect). Our CRIT! popup is a second update nudged -20 deg.

Design (v1, in `GearCritSys`'s stage - Inspect, BEFORE EntityUIEvents, the same visibility checks):
- vanilla's number stays = the TOTAL (white). SkyyGear adds **one extra `CombatTextUpdate` per element with `dealt_e > 0`**, text
  `"49 Fire"` (`elem.popup` = word) or `"49"` (number), `Color` = the element's colour (2.1), angle `ang - 20 - 25 x k` (k = 0.. in Wynn
  order, so up to five numbers fan out beside the total; the CRIT! popup keeps `ang - 20` and the fan starts at `ang + 20` when a crit is
  shown). At most 5 extra per hit; nothing when the viewer cannot see the mob (`queueUpdate` throws otherwise - the existing check).
- Exactly Wynn-style (neutral white number + element numbers, NO total) needs vanilla's number to show `N` only: probe **P1** - in the
  BEFORE-EUI stage set `d.setAmount(N)`, let EUI queue it, restore the total in an AFTER-EUI Inspect system. UNVERIFIED whether the health
  subtraction and the other Inspect readers (SkyyMobs credit, leech) run after EUI; if P1 passes, row `elem.popup.total` (bool, default
  false = Wynn style) switches it; if not, v1 ships the "total + element numbers" form above and the row stays out.
- Ability / DoT element damage (Classes' own Damage objects) keeps vanilla's white number in v1 (Q3).
- Player switch `gear.elemFx` (off = only vanilla's number); `elem.popup` off = the same server-wide.

## 8. Name plate element marker (D8)

`plate.format` gains the token `{element}`; the new default `"[Lv {level}] {name}{element}"` where `{element}` = `" - Fire"` (the mob's
OWN element from `mob:fn:elemOf`) or `""`. A file whose `plate.format` still holds the old default text gets the token added once
(the SkyyGear 0.1.1 one-time default update rule: only the old-default line, kept + logged otherwise); a custom format without the token
shows no element (the admin adds it). With the TRIAL colour markup on (`plate.colorOn`), the element word takes the element colour; else
plain. A multi-line plate ("Fire" above the name) is UNVERIFIED (does `Nameplate.setText` honour `\n`?) - probe P2; if yes, row
`elem.plateStyle` (suffix / line above). Elites / bosses: the same. No plate change when `elem.plate` is off.

## 9. The two player charts (D8) + the element rows

Where (Menu-Pattern: no new menu, no new command): Character > Skills tab, sub-tab row **YOUR STATS | SKILLS | ELEMENTS** (SkyyMenu
`ST_SUBTABS` + one view; same hub page, same size, the one scroll list with headings).

- YOUR STATS gets a heading **Elements**: one row per element in its colour "Fire  49 damage (+30 Imbue)  12 Defence" from
  `gear:fn:elemTotals` + a Poison row "Poison 50 / 10 s". Reads once on open (never periodic - HANDOFF 2).
- ELEMENTS view, two blocks:
  1. **Strong / weak chart**: a 5 x 5 grid from `mob:elem:wheel` + `elem.weak` / `elem.resist` (Mobs publishes `mob:elem:numbers`
     "25;25;50"): rows = your element, columns = the mob's element; cell text "+25%" (green #39f493), "-25%" (red #ff6b6b), "-50% boss"
     under the diagonal note, "0" grey. Caption: "A mob shows its element on its name plate. Hit it with the element that beats it."
     and the wheel line "Earth > Thunder > Water > Fire > Air > Earth".
  2. **Reactions chart**: the planned pairs as a list, all marked "later (class tree)": Wildfire = Air hit on a Burning enemy (Burn
     spreads); Shatter = Thunder hit on a Frozen enemy (+50 % as Water); Steam = Fire on a Chilled enemy (later); Quake = Earth on a
     Shocked enemy (later). Text only; the list is a build constant until reactions exist (then SkyyTrees publishes it).
- Both views are static kit pages (`tools/skyyui.py`, `SUI.verify()`), ASCII, element colours from one table in `skyyui` (add
  `ELEMENT_COLORS` to the kit + `skyyui_test.py` + the style guide, so SkyyGear tooltips, SkyyPets cards and SkyyMenu share it).

## 10. Test plan

Harness (each builder's `test_<mod>_<ver>.py`, bare JVM where the mod already has one):
1. SkyyGear identity: 1,000 random rolled weapons x 0.3.26 `elemSum` == sum of the 0.3.27 split; with `elem.on` off the `GearTrueSys` add
   equals 0.3.26 byte for byte; `scaleInfo` weights each part (mean exact over 10,000 draws).
2. Pet rule: weapon 5 Fire + pet 10 -> raw 15; weapon 0 + pet 10 -> 0; charm 4 + pet 10, weapon 0 -> 4; rElem 2 enables all five pets.
3. Modifiers: +25 / -25 / -50 / 0 rounding table; player victim with D = 0 / 10 / 100 at S = 100.
4. Poison: totals weapon 20 + armor 30 -> one `classes:fn:dot` call with perSec 5.0, secs 10, stacks 3; no SkyyClasses -> no call, one ready-line note.
5. SkyyClasses: `classes:fn:dot` arg validation (bad -> false, never throws); tick Damage cause id "Poison" / "Fire" when the asset map has
   them, PROJECTILE fallback; `classes:fn:imbue` returns "Thunder;30" for an att1 "Lightning" file.
6. SkyyMobs: `mob:fn:elem` over the default table (Yeti Fire +25, Yeti Water -25, Dragon_Fire Fire -50 with `bosses.roles`, Trork anything 0),
   the override columns, `check=` refusals, the wheel parser; the mob share math.
7. SkyyPets / SkyyAccessories: the published map / text carries `fFire` / `dFire`; SkyyGear's `parseExtra` / `parsePets` read them.
8. `python tools/ci/lint.py` 0 fails; `python tools/ci/crosscheck.py --jar <all new jars> --baseline`; `tools/ci/langdup.py` (new charm lang keys).
Smoke: `python tools/smoke_test.py --jar ...` (game closed) - every ready line, no SEVERE.
In game (TEST-CHECKLIST section, Skyy): (1) hit a Trork with a Fire-line weapon: white total + orange "N Fire"; (2) /mobs: a Yeti plate reads
"[Lv 32] Yeti - Water"; hit it with Water (resist) then Fire (weak) - the Fire number is bigger; (3) Spellblade: attune Thunder (out of
combat), Imbue, hit: "N Thunder" yellow, Shock jumps, Momentum text says Thunder; (4) wear a pet with Fire + a Fire weapon: the Fire number
grows by the pet value; swap to a no-Fire weapon: it does not; (5) reforge armor until a "Fire Defence" rolls; stand in front of a Fire mob:
less damage than naked; (6) a "+20 Poison" weapon: green vanilla ticks for 10 s, a boss keeps attacking (no stagger); Thorium armor on a
test target takes less; (7) Character > Skills > ELEMENTS: both charts; YOUR STATS shows the element rows; (8) Server Setup: edit
`elem.mobs`, add `Trork*|Fire` -> plate + numbers change live.

## 11. Builder split (one mod per builder, Opus; reviews Sonnet; all on this file + `research/cloud/Element-System-Spec.md`)

| # | Builder | Mod -> version | Depends on (runtime only - bridge contract above is fixed, so all build in PARALLEL) | Size |
|---|---|---|---|---|
| B1 | Mobs | SkyyMobs 0.1.10 -> 0.1.11 | reads `gear:fn:elemDef` (optional) | medium |
| B2 | Gear | SkyyGear 0.3.26 -> 0.3.27 (patch `tools/gear_0_3_27_patch.py` from the 0.3.26 generated script; if 0.3.26 is still unpinned at build time, B2 waits for its pin or stacks on it - never from 0.3.25) | reads `mob:fn:elem`, `classes:fn:imbue`, `classes:fn:dot`; publishes `gear:imbue`, `gear:fn:elemDef`, `gear:fn:elemTotals` | LARGE (damage maths: full round + crosscheck) |
| B3 | Classes | SkyyClasses 0.1.38 -> 0.1.39 (patch) | reads `mob:fn:elem`, `gear:imbue`; publishes `classes:fn:dot`, `classes:fn:imbue` (names) | medium |
| B4 | Pets | SkyyPets 0.4.3 -> 0.4.4 (patch) | none (publishes keys) | small |
| B5 | Accessories | SkyyAccessories 0.5.26 -> 0.5.27 (patch) | none (publishes keys); `tools/tier_tags.py` rows | small-medium |
| B6 | Menu | SkyyMenu 0.3.39 -> 0.3.40 | reads `gear:fn:elemTotals`, `mob:elem:wheel`, `mob:elem:numbers`; `skyyui.ELEMENT_COLORS` (B6 adds it to the kit FIRST and tells B2 / B4 the name - or the main session adds it before launch) | medium |

Order: wave 1 = B1 + B2 + B3 (the system; one full round with adversarial critics: damage maths, double-count, boss immunity, popup
spam, thread rules) -> cross-check the three jars together -> pin -> **deploy set 1 = Mobs 0.1.11 + Gear 0.3.27 + Classes 0.1.39
(go-together)**. Wave 2 = B4 + B5 + B6 (power sources + charts; one full round: saved data = none, but Accessory Power rows) -> **deploy
set 2 = Pets 0.4.4 + Accessories 0.5.27 + Menu 0.3.40, only on top of set 1** (4.4 rollback note). If usage allows, run both waves at
once (6 builders ~ one heavy workflow + reviews) and deploy all six together. After: Elemental swords lean round (D10), then the Powders
spec (D11), reactions as SkyyTrees nodes (D7). Refresh the Class Balance Workbench (balance-chart rule) once the numbers are in.

Probes before wave 1 (main session, no agents, `tools/dev/reflect.py` / `bc.py` + smoke test): **P1** vanilla number = neutral only
(section 7); **P2** multi-line Nameplate (section 8); **P3** a 0-knockback Damage tick does not flinch / interrupt an NPC (section 3.5;
= cloud probe E4); **P4** a damage-free child of the vanilla Poison effect keeps the look (section 3.5; = E2 for Poison); **P5**
`DamageCause.getAssetMap()` lookup by id "Poison" / "Fire" from a mod at start; **P6** does an ability Damage (PROJECTILE) reach
`GearHit.weaponHit` today (E1) - if yes, B2's `class:fn:abilhit` guard is mandatory, not optional.

## Questions for Skyy (defaults in brackets; the build uses the default until answered)

| # | Question | Default |
|---|---|---|
| Q1 | Popups: if P1 passes, show Wynn-style (white neutral + coloured element numbers, no total) or keep the white TOTAL plus element numbers? | [Wynn style when P1 passes; else total + elements] |
| Q2 | Popup text "49 Fire" (word) or just the coloured "49"? | [word - readable for colour-blind players; row `elem.popup`] |
| Q3 | Burn / Poison TICKS and ability element hits: coloured numbers too (one more Damage path to touch), or vanilla white in v1? | [white in v1; coloured ticks in the reactions round] |
| Q4 | Mob element share: 30 % of a mob's hit becomes its element (naked player unchanged; Defence lowers it)? | [30 %, row `elem.mobShare`] |
| Q5 | Element charms: 5 single-element ladders T1-T5 (2/4/7/11/16 damage, 3/6/10/16/25 Defence) + Elemental Power (+2 all-element per 100 AP)? Acquisition = the loot pass like other T lines (admin give until then)? | [yes; admin give until the loot pass] |
| Q6 | Pet elements: the default table in 4.4 (Skeleton / Rabbit / Chicken / Turkey / Rat / Deer = none)? | [yes, editable in Server Setup] |
| Q7 | Poison line max 20 per line (so "50/10s" needs weapon + armor stacking) or raise to 40 so one Legendary weapon can hit Skyy's 50/10 example? | [20; row `poison.max`] |
| Q8 | Plate marker as a suffix "- Fire" (sure to work) or a line above the name (if P2 passes)? | [suffix; line-above row if P2 passes] |
| Q9 | Charts live under Character > Skills as an ELEMENTS sub-tab (no new menu, Menu-Pattern) - ok, or on the Class tab? | [Skills sub-tab] |
| Q10 | Yeti / Frost Golem weak to FIRE (theme) instead of the wheel's Thunder - keep the override, or pure wheel so the chart is always right? | [keep the override; the plate shows Water, the chart notes "ice melts: Fire"] |

## UNVERIFIED (each becomes a probe or a build-time assert)

- P1-P6 above (vanilla number neutral-only trick; multi-line plates; tick flinch; damage-free Poison effect child; DamageCause asset lookup
  from a mod; ability hits reaching `weaponHit` today).
- The config kit's multi-column TEXT table (`elem.mobs` as Match | Element | Resist | Weak columns) - the spec uses a 1-column `|` table,
  which CONFIG-CONTRACT says works; a builder may upgrade it if the kit supports text columns.
- Tooltip line colouring (cloud E6) and the TRIAL plate colour markup (SkyyMobs `plate.colorOn` - the client may not draw colours).
- The real role ids of the default `elem.mobs` rows marked with `*` globs (Earthen, Fen Stalker, Yeti, Emberwulf, Pterodactyl, Dragon_Frost,
  Sandswept) - B1 checks each against `MobCfg.VANILLA` (280 ids) and drops rows that match nothing (one build-time print).
- Whether `GearSpeed.scaleInfo`'s stochastic rounding per element keeps the sum's mean exactly when applied to five small parts (harness 1).
- Whether `classes:fn:dot` can target a PLAYER victim (PvP poison) - v1 may limit it to NPCs with a false return.
- The engine's own `DamageTextColor` on the damaged PLAYER's indicator (research says it reaches only the victim's own indicator) - unused here.
- Usage: 6 Opus builders + critics ~ 1-1.5 heavy workflows; check `get_usage` before each wave.
