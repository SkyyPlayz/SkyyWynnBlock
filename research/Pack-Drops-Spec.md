# Pack armor + weapons as mob drops (RESUME NEXT 3) - spec + build notes

*Written 2026-10-17 by the cloud build trial session (Skyy's Grok bot trial). Built: SkyyGear 0.3.19 + SkyyMobs 0.1.10 scripts. NOT built into
jars, NOT deployed - the local session rebuilds against the real install. Owner: Skyy (they/them).*

## 0. The decisions this follows (word for word in `docs/answered/gear.md`, newest wins)

- 2026-10-17 PACK ARMOR AS MOB DROPS: "lets build the arcane robes and armory into the mod so you drop from enemy's with our modifiers next.
  (you already split them into cloth, light and heavy armor category's. split each category into tiers i want a few normal drops in each
  tier. then we need to pick some to make UT items for each tier, and mythic mob drops."
- 2026-10-17 PACK WEAPONS TOO: "and the weapons too".
- 2026-10-17 ARMOR SETS FILL: "fewer at lower tiers on the normal drops keep 2 ut but do 1 mythic. and UT and mythic can reuse looks BUT
  enhanced (if we can.) ... id prefer recolors on ut and more basic sets, so we can save the coolest armor and weapons for mythic".
- 2026-10-17 UT SCOPE: "UT and mythic per zone! not tier. always make the UT and mythic the highest tier of that zone" (5 zones).
- 2026-10-17 ZONE TIERS CORRECTION: "all combat gear is still drops only. and all Ut and mythic are combat gear. not your forever gear you level up."
- 2026-10-17 ZONE METALS: Zone 1 Copper + Iron, Zone 2 Thorium, Zone 3 Cobalt, Zone 4 Adamantite, Zone 5 Mithril (`research/Zone-Tiers-Idea.md`).
- LOCKED 2026-10-08 popup batch 2 (kept): Mythic boss-only, "10% per kill (20% Challenge) per participant with 15% credit + own-class lean x3";
  PACK ARMOR "pool The Armory + SLVR Robes + Arcane Power + Voidcloak, keep their crafting, no paid access, drops picked by set, special sets
  1 in 50 per boss kill, random colour, crowns / amulets = Cloth, multiplicative pieces special sets only, Lahat Chereb Berserker, Armory Fist
  = Monk boss drop".
- LOCKED 2026-10-01 zone bands (`docs/answered/mobs.md`): Zone 1 = Lv 1-20, 2 = 20-30, 3 = 30-45, 4 = 45-60; Zone 5 = Lv 60-75 (`docs/answered/world.md` R8).
- Inputs: `research/Armor-Set-Count.md` (counts, survey, licences), `research/Pack-Armor-Plan.md` (ids, classification, the runtime design), `PACK.md`.

## 1. Plain words (for Skyy)

- The Armory's armor and weapons now drop from your mobs inside the same mystery bags as vanilla gear, with OUR rarity, level and modifiers.
  A bag picks a SET first (so 179 Calvary colourways don't flood the drops), then a random colour.
- Every zone x weight (Heavy / Light / Cloth) and every weapon type has its sets sorted into **normal drops**, **UT candidates** and **one
  Mythic**. The Mythic set only drops from that zone's **bosses** (10% per player who did at least 15% of the damage, own-class weapons x3).
- UT items need their fixed lines + one trade-off from you, so the 6 UT candidates wait (they don't drop as normal gear meanwhile).
- Only The Armory is switched on (its licence allows it with credit). Void Armor is allowed too but its item ids were never scanned. Arcane
  Robes, Fyrrage's two packs, Elemental Knights and stonedturtle's sets are in the table as TODO rows - nothing of theirs is used until the
  authors say yes.
- We never copy their files, models, textures or numbers; we only react to their item ids. If The Armory is switched off, its drops just stop.

## 2. Design

### 2.1 The table - `tools/pack_drops.py`

One row per set (a look): source mod, name, kind (armor or a weapon bag type), weight (Heavy / Light / Cloth), tier (a SkyyGear
`level.material` word), role, ids. `python tools/pack_drops.py` prints the grid and checks it; `--md` prints section 3; `--scan <jar>` lists a
mod's armor / weapon ids read-only (for filling rows). The SkyyGear build imports it, so a table change needs no new patch.

- **Zone** = by tier: Crude / Copper / Iron = 1, Thorium = 2, Cobalt = 3, Adamantite = 4, Mithril / Onyxium = 5 (Skyy's zone metals; zone 1
  goes through Iron). UT and Mythic sets must sit at their zone's TOP tier (checked).
- **Roles:** `drop` (normal mob drops), `ut` (UT candidate: kept out of normal bags; becomes Untiered when its `ut.<id>` + `utfx.<id>` rows
  exist - the 0.2.16 Untiered table, which also refuses any id a recipe makes), `mythic` (boss-only Mythic bag of its zone), `off` (listed,
  never used). At most ONE active Mythic per zone x weight / weapon type (checked).
- **Sources:** status `on` (The Armory), `needs-ids` (Void Armor), `todo` (waiting for the author's OK). Only `on` rows reach the jar.

### 2.2 SkyyGear 0.3.19 (`tools/gear_0_3_19_patch.py` -> `SkyyGear/build_skyygear_0.3.19.py`)

| Part | What it does |
|---|---|
| GearPackId | the table in the jar (packed strings), `has` / `at` / `tier` / `tag` / `swap`; all of it follows `part.packDrops` |
| Gear rules | a table id = gear (single items only), kind combat (a `kind.prefix` row still wins), level band = its tier's `level.material` row (a `level.item` row still wins; never their ItemLevel), armor type = the table weight (not their sound set - The Armory gives robes Heavy sounds) |
| Normal drops | pack rows are appended to the bag pool (`GearPool`); the bag slot = the LIVE item's ArmorSlot (a weapon row only while the live item is a weapon - `Item.getWeapon()`, fix round); weight = `loot.packWeight` per set, split over its live pieces of that slot; missing ids are skipped |
| Mythic bags | `GearPack.bossRoll` from `GearDeathMark`: SkyyMobs' `mob:fn:boss` says boss + zone + credited players; each player with >= 15% credit (in the same world, not Creative) rolls 10% (the killer only when nobody is credited at all); a won bag counts against the hourly extra-bag cap and goes INTO the winner's inventory (`GearPackGive` world task: storage, hotbar, backpack; full = at their feet). The bag (`Skyy_Unid_Bag_Mythic` + `pz` = zone) identifies into one of the zone's Mythic pieces at their band (fix round: no head-count cap on rollers; armor = weight evenly, then a slot of it; a winner who changed worlds before the task = the bag lies at the boss); re-identify keeps the zone; no Mythic piece left (mod off / renamed) = the bag waits, it never becomes a vanilla item |
| Craft block (Skyy 2026-10-17 "Block craft, chest = plain") | a recipe whose output is a UT / Mythic row is refused in CraftRecipeEvent$Pre (benches + SkyySacks /craft; only a same-set Alteration colour swap passes; Creative crafts); such a piece their chests / mobs drop is a plain Normal piece - real Mythic rolls only from boss bags. A boss family (role up to `_Phase`) rolls once per player per 120 s; boss bags are not under the hourly cap |
| Swap guard | a pack recipe that consumes a gear piece (an item OR a resource type a table item carries) is refused while you hold a ROLLED piece of that input; with Normal pieces it runs, no fresh roll, no Smithing XP. The Alteration Table is exempt (it carries the piece's whole document + quality onto the new colour - bytecode of 1.23.0). Crafting pack pieces pays no Smithing XP at all (benches and SkyySacks /craft) |
| Tier tag | our tooltip's flavour line starts with the tier tag (`T3 Iron - ...`, `tools/tier_tags.py` numbering); their lang keys are never written |
| `/gear loot` | adds the pack line: live pieces, missing ids, UT candidates, Mythic pieces per zone, boss counters |

Server Setup -> Gear -> Loot (new keys; a missing line = its default, no one-time update):

| Key | Default | Meaning |
|---|---|---|
| `part.packDrops` | true | the whole feature (off = exactly 0.3.18; documents stay on the stacks) |
| `loot.packWeight` | 1 | one pack set's weight in a bag (1 = one vanilla item) - placeholder |
| `loot.boss.mythic` | 10 | % per credited player per boss kill (LOCKED 10%) |
| `loot.boss.credit` | 15 | % of the boss's damage a player needs (LOCKED 15%) |
| `loot.boss.classLean` | 3 | own-class weapon types count x this (LOCKED x3) |
| `loot.boss.armorShare` | 50 | % of Mythic bags that hold armor - placeholder |

Saved data: a Mythic boss bag carries `pz` (zone) in its SkyyUnid document and in its item's `box`; nothing else is new.
Rollback 0.3.19 -> 0.3.18: safe (0.3.18 ignores `pz`; pack items keep their documents but count as plain items again).
A critic review (Sonnet) found 2 HIGH + 5 MEDIUM issues before hand-off; all were fixed in the patch except the class rules for pack weapons
(question 12) - details in the patch docstring items 5 and 6.

### 2.3 SkyyMobs 0.1.10 (`tools/mobs_0_1_10_patch.py` -> `SkyyMobs/build_skyymobs_0.1.10.py`)

- Bridge `mob:fn:boss`: `Object[] { String world, UUID npc, String role, Number x, y, z }` -> `null` (not a boss / bad args) or
  `Object[] { Integer zone, String role, String[] players, double[] shares }`. Zone = the level band at the boss (as `mob:fn:levelAt`), else
  the NPC's own level, mapped by the zone tops; 0 = unknown. Players / shares = SkyyMobs' kill credit, top first, read-only. A credit entry
  SkyySacks already took in the same death tick stays readable for 10 s (review fix: SkyySacks' death mark may run first).
- Rows (Which mobs tab): `bosses.roles` = `Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*`; `bosses.zoneTops` = `20 30 45 60 75`.
- Rollback 0.1.10 -> 0.1.9: safe (no boss bags any more).

## 3. The grid (`python tools/pack_drops.py --md`)

UT = UT candidate (waits for its lines), MYTHIC = boss drop, [TODO] = author's OK pending, [NEEDS-IDS] = allowed, ids not scanned.

| Zone (top tier) | Heavy | Light | Cloth | Battleaxe | Club | Daggers | Longsword | Mace | Sword |
|---|---|---|---|---|---|---|---|---|---|
| 1 (Iron) | Antique Dragon; Rook; Calvary; Void Copper [NEEDS-IDS]; Void Iron [NEEDS-IDS]; UT Ghost Rook; UT Ghost Calvary; MYTHIC Iron Dragon | Tribal Masks; Jester; Skull Masks; Bramblekin; Ninja [TODO]; MYTHIC Warden | Scarecrow; Crowns; Amulets; Potion Bandolier; SLVR Wool robes [TODO]; SLVR Linen robes [TODO]; UT Battlegrounds; MYTHIC SLVR Cotton robes [TODO] | Armory Iron Battleaxes | MYTHIC Armory flails | Armory Iron Daggers | Armory Iron Longswords | Armory Iron Maces | Armory Iron Swords; UT Ghost Sword |
| 2 (Thorium) | Void Thorium [NEEDS-IDS]; Neptune's Elite [TODO]; Outlanders Berserker [TODO]; MYTHIC Elite Rook | Dune Walker [TODO]; Fen Stalker [TODO]; Outlanders Hunter [TODO]; MYTHIC Engineering Rig; MYTHIC Crystalwood [TODO] | Outlanders Priest [TODO]; MYTHIC SLVR Silk robes [TODO] | Armory Thorium Battleaxes | - | Armory Thorium Daggers | - | Armory Thorium Maces | Armory Thorium Swords |
| 3 (Cobalt) | Frostbite Warden [TODO]; Outlanders Marauder [TODO]; MYTHIC Cobalt Dragon | MYTHIC Outlanders Stalker [TODO] | SLVR Raven robes [TODO]; Outlanders Sorcerer [TODO]; MYTHIC Priest | Armory Cobalt Battleaxes | - | Armory Cobalt Daggers | Armory Cobalt Longswords; MYTHIC Elemental longswords | Armory Cobalt Maces | Armory Cobalt Swords |
| 4 (Adamantite) | Void Adamantite [NEEDS-IDS]; Scorched Heart [TODO]; Elemental Knights (4 sets) [TODO]; Blood Armor [TODO]; MYTHIC Daemon | Scorpion Helms; MYTHIC Elite Scorpion | SLVR Cindercloth robes [TODO]; MYTHIC Grand Lich | Armory Adamantite Battleaxes; UT Hepta Axe | MYTHIC Rune Blade | Armory Adamantite Daggers; MYTHIC Dual Rune Blade | - | MYTHIC Lahat Chereb | Armory Adamantite Swords |
| 5 (Mithril) | Soul Cage armor [TODO]; MYTHIC Void Mithril [NEEDS-IDS] | - | MYTHIC Magical Armor [TODO] | - | - | - | - | MYTHIC Zweihander | Void Mithril weapons [NEEDS-IDS] |

Vanilla gear still drops in every cell through the existing bag pool. Off in the table (never used): Armory Iron recolours (vanilla Iron =
the Mining Set look), shields (no shield bag type), Rune Blade stages 2-3 (an upgrade chain later), Armory Fist (no fist bag type yet),
Iron Dual Swords (unfinished in their mod). Gaps that stay: Light zones 3 and 5, Cloth zones 1-2 Mythic, zone 5 almost everything -
exactly the cells the TODO rows (and our own designs, last resort) fill.

## 4. Licences and credit

- The Armory (LadyPaladra, CC BY-NC 3.0): credit + never sold. Credit is in the `PACK.md` row and now in SkyyGear's manifest description.
  `PACK.md` still says 1.22.0 - Skyy's Mods folder has 1.23.0 (`research/Armor-Set-Count.md` section 3); the local session updates that row.
- Void Armor (Aipoc76, CC BY-NC 3.0): allowed, not packed - needs a `PACK.md` row (credit) when its ids are added.
- Everyone else: All Rights Reserved or unknown - TODO rows only, nothing active, no ids in any jar (the SLVR ids sit in the table as text).
- Never: their models / textures / recipes / numbers / lang, id overrides, recolours of their sets (needs the author's OK).

## 5. Questions for Skyy (each with a recommended default)

1. **UT lines for the 5 UT candidates** (Ghost Rook, Ghost Calvary, Battlegrounds, Ghost Sword, Hepta Axe - none has a recipe; Academy is OFF: all 27 pieces are craftable, and no recipe-free Armory Cloth set exists for Zone 4 Cloth UT) - each needs fixed lines +
   one trade-off, like the first UT batch. [Default: a UT design popup batch next; until then they never drop.]
2. **"Enhanced" UT / Mythic looks** (glow, stylised) on The Armory's own models would be a derivative of their art. [Default: no enhancement
   now - Mythic uses their special sets as they are; ask LadyPaladra with the other asks.]
3. **Their crafting vs "all combat gear is still drops only"** - ANSWERED (Skyy 2026-10-17 popup, word for word: Q "...almost every Armory
   set we planned as MYTHIC (boss-only) or UT can also be CRAFTED at The Armory's own benches ... and The Armory's own chest loot drops
   some of them too..." -> "Block craft, chest = plain (Recommended)"): our code refuses recipes that make a UT / Mythic set piece; their
   chests / mobs give plain unrolled pieces; normal (drop-role) pieces stay craftable and roll like any gear.
15. **The Armory's Salvagebench refunds 100%** - ANSWERED (Skyy 2026-10-17 popup, word for word: Q "...The Armory's own Salvagebench gives
   back 100% of the materials from its pieces ... Block salvaging rolled (dropped / identified) pieces at their bench?" -> "Yes, Requip only
   (Recommended)"): dropped / identified pack pieces salvage only through Requip SALVAGE; crafted pieces still salvage at the bench. Built:
   CraftRecipeEvent$Pre refuses a Salvagebench recipe while such a piece of its input is held (covers SkyySacks /craft, which lists
   Salvagebench recipes as an instant bench). The Salvagebench BLOCK is a Processing bench and fires no CraftRecipeEvent (0.7 bytecode) -
   it is NOT blocked yet; proposed: a ChunkStore tick system before BenchSystems$ProcessingBenchTick that moves such a stack from the
   bench's input to its output container (patch docstring item 10 h).
4. **Armory Iron recolours** (`Armor_Iron_<Slot>_<Colour>`, 97 pieces) look like the vanilla Iron Mining Set. [Default: off.]
5. **Mythic bags go straight into the winner's inventory** (full = at their feet) instead of dropping at the boss (where SkyySacks'
   auto-pickup would give them all to the top damager). [Default: keep it that way.]
6. **Zone levels vs gear bands**: zones 4-5 go to Lv 60-75 but gear bands stop at 49 (Adamantite 35-43, Mithril 40-49), so a Lv 60 zone 4
   boss drops a Lv 35-43 Mythic. [Default: keep the bands until the Zone-Tiers-Idea level change; `loot.levelTop` stays 49.]
7. **Boss list**: `Goblin_Duke*, Trork_Chieftain, Dragon_*, Skeleton_Elite*, *_Boss*`; the 0.7 Gobliterator arena phases are left out.
   [Default: as listed; add more in Server Setup -> Mobs -> Boss roles.]
8. **Armory Fist = Monk boss drop** (10-08 lock) needs a fist bag type first. [Default: off this round; next weapon round adds the type.]
9. **Challenge mode 20%** (10-08 lock) - no Challenge mode exists yet. [Default: later, with the boss round.]
10. **Server Setup -> Mobs -> Which mobs** now has 8 rows (two pages). [Default: fine.]
11. **Ghost Sword tier** - ANSWERED by the 1.23.0 scan: ItemLevel 20 = the Iron recolours' level, so Iron (zone 1).
12. **Class rules for Armory weapons**: their ids have no `Weapon_` prefix (`Sword_Iron_Red`, `LahatChereb`, `Zweihander`), so SkyyClasses'
    prefix rules never match them - every class can use them and no "Class Req" line shows (the 10-08 locks "Lahat Chereb = Berserker",
    "Zweihander = Warrior" are not enforced yet). [Default: a SkyyClasses class-weapon table round next (`research/Pack-Armor-Plan.md` 3.3 a).]
13. **Mythic armor and your class**: the x3 own-class lean applies to weapon types only; Mythic armor picks Heavy / Light / Cloth evenly (built: the weight first, then a slot - fix round).
    [Default: keep - classes have no armor weight yet.]
14. **Boss bags and the hourly cap**: a won Mythic bag counts against `loot.mob.capPerHour` (20). [Default: shared cap, a safety net
    against respawning bosses.]

## 6. For the local session (UNVERIFIED items answered by the local rebuild, 2026-10-17)

Built on a Linux box with only `HytaleServer.jar` 0.7.2 (Maven) - no Assets.zip, no Hytale install, no Mods folder, no previous jars.

**Steps:** review the PR -> merge -> `python tools/gear_0_3_19_patch.py` + `python tools/mobs_0_1_10_patch.py` (must say "wrote ...") ->
`python SkyyGear/build_skyygear_0.3.19.py` + `python SkyyMobs/build_skyymobs_0.1.10.py` (must end "assembled ...jar") -> harnesses
`python SkyyGear/test_skyygear_0.3.19.py` and `python SkyyMobs/test_skyymobs_0.1.10.py` (fix the expected-class lists if only those differ)
-> `python tools/ci/crosscheck.py --jar <both jars> --baseline` + `python tools/ci/lint.py` (0 fails) -> re-scan The Armory 1.23.0
(`python tools/pack_drops.py --scan <Mods>/TheArmoryMod-1.23.0.jar`) and fix renamed ids -> smoke test -> pin both in `tools/deploy_set.py`
(deploy together; either rolls back alone) -> deploy -> `PACK.md` Armory row to 1.23.0.

**Answers (local rebuild of PR #17, 2026-10-17, real install; nothing run in game yet):**
- Builds + harnesses: both build on the real install; full harnesses pass (SkyyGear 1696 ok / 0 fail / 52 waived, SkyyMobs 152 ok);
  crosscheck --baseline 0 fail, lint 0 fail, langdup OK.
- The Armory 1.23.0 scan (`--scan` now follows the Parent chain): all 1,286 table ids present, every armor row has a real ArmorSlot, every
  weapon row a Weapon part (most through `Template_Weapon_<Type>`; Item.getWeapon() non-null), templates match the row kinds. New in 1.23.0,
  left out: KanohiHau + 8 colours (no ArmorSlot / level), three Lv 8 sign maces, TestBroom. Ghost Sword = ItemLevel 20 = Iron.
- Alteration Table (their AlterationTransaction bytecode): fires CraftRecipeEvent$Pre (honours cancel) + $Post; the new colour = the input's
  WHOLE metadata + quality - a rolled piece keeps its roll, so the swap veto skips the ArmoryAlteration bench. Its recipes use
  ResourceTypeId inputs - the swap guard reads those too.
- SkyySacks 0.8.20: PickDeathMark (after TickCorpseRemoval, before DropDeathItems) takes the credit; MobCredit's DEAD copy keeps it readable
  10 s (oldest evicted past 512, never cleared). /craft fires CraftRecipeEvent$Pre (our refusals apply); it lists Armor_Bench /
  Weapon_Bench recipes (bench accessories) on the CRAFTING tab (their ids have no Armor_ / Weapon_ prefix, so gear:fn:classShow is not
  asked there); never the Alteration bench. gear:fn:roll mode 8: no XP for pack pieces, swap / UT / Mythic outputs plain.
- Boss roles in Assets.zip 0.7: Goblin_Duke (+ Phase_2, Phase_3_Fast / Slow), Trork_Chieftain, Dragon_Fire / Frost, Skeleton_Elite
  (+ Phase_2); no in-data phase switch found, so phases may be separate deaths -> one roll per boss family per player per 120 s.
- Void Armor (Aipoc76): not in the Mods folder (the Void* mods there are other authors') - rows stay needs-ids.
- Coin loop: no table id has a Value / Price / Sell / Coin / Worth field (build-time guard while the jar is installed).
- Still open: in-game behaviour + smoke test; The Armory's own multiplicative stats on Mythic / UT pieces; the Salvagebench BLOCK (Q15: no Pre event - tick hook proposed).

**TEST section draft (for `docs/tests/<month>.md` + a `TEST-CHECKLIST.md` line):**
1. The Armory ON. Kill levelled mobs in zone 1 (or `/gear box random 18`): bags of Armory pieces drop; identify one - an Armory piece with
   rarity, `[Lv N]`, modifiers, tooltip flavour starting `T3 Iron`. Expect mostly vanilla + a fair share of Armory sets, not a flood of helmets.
2. Craft an Armory base piece at their bench: it rolls a rarity like any gear. Swap its colour at the Alteration Table: no new roll, no
   Smithing XP (gear.log has no CRAFT line for it).
3. Kill a boss (Trork_Chieftain / Goblin_Duke) with 2 players each doing >= 15%: `/gear loot` shows "boss kills 1, rolls 2"; set
   `loot.boss.mythic` 100 to force it - each gets a Mythic bag IN THEIR INVENTORY (chat line) saying "Boss drop: one of Zone 1's Mythic
   ..."; identify: Iron Dragon / Warden / Armory flails, Mythic, zone kept on re-identify. With SkyySacks pickup on, nobody gets someone
   else's bag.
2b. Hold a rolled (Rare+) Armory piece and try its colour swap at the Alteration Table: refused with a red line; with only a Normal piece
   the swap works.
4. Server Setup -> Gear -> Loot -> Pack armor + weapons drop OFF: Armory pieces show as plain items, no new Armory bags; back ON = stats back.
5. Switch The Armory OFF in the world: no errors, `/gear loot` shows the pack ids as not installed, vanilla bags unchanged.
