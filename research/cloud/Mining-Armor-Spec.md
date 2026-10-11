# Mining Armor - the vanilla metal sets (Copper to Onyxium) as green Mining Sets

Cloud draft, 2026-10-09. Build spec for **SkyyGear 0.2.15** (right after the rarity G1 round = SkyyGear 0.2.14). Paper design; nothing built.
Every number is a placeholder and a Server Setup row. Arithmetic in python3 (method shown in section 4).

## 0. Decisions this follows (`docs/answered/gear.md`, newest wins; not re-decided)

| Line | Skyy (short) | Used here |
|---|---|---|
| gear.md:116 (2026-10-08) | "use vanilla for mining, and armory for combat gear" | MINING armor = the vanilla metal sets Copper..Onyxium; SkyyGear gives them mining lines (Fortune / speed / Wisdom) "instead of combat stats"; our half-plate mining design is replaced |
| gear.md:125 (2026-10-08) | "gathering armor uses the set label, the full set gives a little bonus gathering fortune ... higher tiers can give a little more like mining /chopping speed, movement speed" | green SET label; full set (all 4) = bonus Mining Fortune; higher tiers add speed + move speed |
| gear.md:128 (2026-10-08 popup batch 2) | "Yes to all" incl. "gathering set table as tabled", "8 colours per vanilla metal, Armory's 20 Iron colours = miner looks, no combat looks on mining sets" | the full-set bonus numbers = `research/cloud/Untiered-Mythic-Spec.md` 3.2 table (locked); looks = later (Recolor) |
| gear.md:77 (2026-10-06) | "mining armor starts at copper" | 7 tiers Copper..Onyxium, no T0 |
| gear.md:72 (2026-10-06) | "make sure that if those mining helmets show a light, it works" | helmet light only as a REAL light through the SkyyAccessories Lantern code; never a fake glow |
| gear.md:118 (2026-10-08) | "allow them to change up the vanilla armor, so miners can be dapper too" | look swaps keep the mining lines (section 6, later round) |
| gear.md:136 (2026-10-09) | "Armory off until 0.7 (Recommended)" | section 5: what OFF means for these items |
| gear.md:138 (2026-10-09) | "We are making the vanilla armor the mining gear so I'd do that first" | this spec = the next SkyyGear round after G1 |
| gear.md:17 (2026-10-02) | tool levels: "need to be mining lvl 13 to use a lvl 13 pickaxe ... crafted tools are made at your level" | gate skill for mining gear = Mining; crafted at your Mining level inside the band |
| gear.md:32 (2026-10-03) | "copper armor is already 1-18" | Copper armor band 1-18 stays |
| gear.md:53 (2026-10-05) | "Yes, hide it" (vanilla armor box) | SkyyGear keeps applying all armor Health / resistance |
| gear.md:56, :59 (2026-10-05) | vanilla metal = HEAVY combat armor "for now" | SUPERSEDED by :116 (newer); kept only as the reason Health stays (section 5) |
| gear.md:90, :91 (2026-10-06) | half-plate mining look | SUPERSEDED by :116 (vanilla models now) |

Older cloud drafts used as inputs: `research/cloud/Untiered-Mythic-Spec.md` (3.1 set table + check, 3.2 gathering set table),
`research/cloud/Gathering-Numbers-Reconciled.md` (caps: armor Fortune 15, armor Wisdom 10, global 100), `research/cloud/Gathering-Armor-Mining-Farming.md`
(old Miner's gear, replaced), `research/cloud/Crop-Armor-Spec.md` (sister family, same row style), `research/cloud/Mining-Lamp-Spec.md`,
`research/Recolor-Plan.md` (looks), `research/Tool-Levels-Spec.md` + `research/cloud/Tool-Levels-Revision.md` (stat keys `mfort` / `mwis` / `mpow`).

## 1. What the code does today (read-only, cited)

| Fact | Where |
|---|---|
| Armor slots are Head / Chest / Hands / Legs - **no Feet slot** | `SkyyGear/build_skyygear_0.2.13.py:1691-1693` ("there is no Feet slot (ItemArmorSlot = Head, Chest, Hands, Legs)"), `:370` |
| Vanilla armor box hidden; SkyyGear applies Health + resistance from the level curve, only for an Armor_ id "of an enforced kind" | `:369-380`, `GearABox` from `:9349` |
| Gate skill per kind: combat = class, mining = Mining; **only combat + equipment are enforced** | `:1376-1381` (`GATE_BY_KIND`, `ENFORCED_KINDS`) |
| `kind.prefix` table (id prefix -> combat / mining / ...), empty by default; every Armor_ is combat | `:3583-3585`, `:3900-3901`, `:7575` |
| Level bands: Armor_Copper 1-18, Iron 15-23, Thorium 20-28, Cobalt 25-38, Adamantite 35-43, Mithril / Onyxium 40-49 | `:1613-1633` (`BANDS` assert) |
| Tool Mining Power = level curve `1:1.0 ... 49:2.2`; Fortune 0.2 x level x (1 + 2% x tier), cap 25 | `:3479-3485`, `GearTool.fortune` `:10431-10439` |
| Tool Fortune reaches SkyySkills as `skill:bonus:<uuid>["gear"]` = { `dd.mining`: Fortune / 100, `only.mining`: "Rock_,Rubble_,Ore_" (pickaxe) / "Soil_" (shovel) } | header `:53-79`, `GearTool.post` `:10488-10515` |
| SkyySkills rolls source "gear" through the Fortune path (cap `perk.fortuneMax` 2, the `only` filter); every other source sums into the old double-drop chance (cap `perk.doubleDropMax`) | `SkyySkills/build_skyyskills_0.4.27.py:9364-9377` (`Perks.fortune`), `:8049-8105` (`dd` / `ddOf` / `ddExcept`) |
| `xp.<skill>` in any skill:bonus source = extra gathering XP (summed, clamped 0..5) | `SkyySkills/build_skyyskills_0.4.27.py:8018` (`xpBonus`), `:764-770` |
| Live Speed stat `spd` (1 point = 1% via `speed.per`) through the movement protocol | `SkyyGear/build_skyygear_0.2.13.py:1336`, `:3775` |
| Rarity `set` exists (Level-up cost row Set 1000 + 200) | `:1688-1689` |
| Loot bag pool = every Assets.zip Weapon_ / Armor_; Heavy / Light / Cloth from the sound set `ISS_Armor_Heavy` ... | `:3359-3388` |
| No Mining Fortune / Wisdom / Power stat is rolled on gear (the STATS table has only combat rows) | `:1320-1366` |
| Lantern light: 4 rarities Normal / Unique / Rare / Legendary, reach rows 6 / 12 / 24 / 48 blocks | `SkyyAccessories/build_skyyaccessories_0.5.9.py:683-692` |
| The G1 set table (SkyyGear 0.2.14) is **not in the repo yet** (running as rar01, `docs/log/2026-10.md:305`) | rows in section 3 use `research/cloud/Untiered-Mythic-Spec.md` 3.1's format; UNVERIFIED against the real 0.2.14 syntax |

## 2. The seven Mining Sets

### 2.1 Ids (vanilla, Assets.zip) - 28 pieces, Head / Chest / Hands / Legs

| Tier | Head | Chest | Hands | Legs | Checked in the repo |
|---|---|---|---|---|---|
| Copper | `Armor_Copper_Head` | `Armor_Copper_Chest` | `Armor_Copper_Hands` | `Armor_Copper_Legs` | build-checked: `SkyyCollections/build_skyycollections_0.2.8.py:450-462` (`REC` -> `must()` against Assets.zip, `:250`) |
| Iron | `Armor_Iron_Head` | `Armor_Iron_Chest` | `Armor_Iron_Hands` | `Armor_Iron_Legs` | same |
| Thorium | `Armor_Thorium_Head` | `Armor_Thorium_Chest` | `Armor_Thorium_Hands` | `Armor_Thorium_Legs` | same (Hands / Legs appear in no doc, only through that loop) |
| Cobalt | `Armor_Cobalt_Head` | `Armor_Cobalt_Chest` | `Armor_Cobalt_Hands` | `Armor_Cobalt_Legs` | same (Head / Hands / Legs only through that loop) |
| Adamantite | `Armor_Adamantite_Head` | `Armor_Adamantite_Chest` | `Armor_Adamantite_Hands` | `Armor_Adamantite_Legs` | same |
| Mithril | `Armor_Mithril_Head` | `Armor_Mithril_Chest` | `Armor_Mithril_Hands` | `Armor_Mithril_Legs` | same |
| Onyxium | `Armor_Onyxium_Head` | `Armor_Onyxium_Chest` | `Armor_Onyxium_Hands` | `Armor_Onyxium_Legs` | Hands build-checked (`SkyyArmory/build_skyyarmory_0.1.12.py:3248`); all 4 in the local mod scan `research/Pack-Armor-Plan.md:480` - **UNVERIFIED** for Head / Chest / Legs until the 0.2.15 harness asserts them |

Not mining: Bronze, Steel, Steel_Ancient, Heavy Leather, Prisma stay combat (Heavy). EndgameAndQoL overrides these vanilla ids and must stay off
(`research/Pack-Armor-Plan.md:365`).

### 2.2 Level bands and gate

| Tier | Band (live rows) | Gate | Crafted at |
|---|---|---|---|
| Copper | 1-18 (`Armor_Copper` row) | Mining level | the crafter's Mining level, clamped into the band (gear lock 2026-10-01 / 10-02) |
| Iron | 15-23 | Mining | same |
| Thorium | 20-28 | Mining | same |
| Cobalt | 25-38 | Mining | same |
| Adamantite | 35-43 | Mining | same |
| Mithril | 40-49 | Mining | same |
| Onyxium | 40-49 | Mining | same (Onyxium beats Mithril by its numbers, same band) |

Under-level piece = inactive: no Health, no resistance, no mining lines, does not count for the set (the existing `level.armorNative` rule).

### 2.3 Per-piece stats (fixed by tier - no rarity roll, no random modifiers)

Rarity is `set` (green) for every new piece; 0 random modifiers; Reforge's modifier tab refuses them; Reforge "Level up" works (cap +6, Set cost row).
Piece share Head 25 / Chest 35 / Legs 25 / Hands 15 %. Mining lines count **only while a pickaxe or shovel is held** (and only on the blocks that
tool's Fortune counts on - rock / ore for a pickaxe, soil for a shovel).

| Tier | Mining Fortune Head / Chest / Legs / Hands (sum) | Mining Wisdom % Head / Chest / Legs / Hands (sum) | Helmet light (Lantern rarity) |
|---|---|---|---|
| Copper | 0.1 / 0.2 / 0.1 / 0.1 (0.5) | - | Normal (torch glow, 6) |
| Iron | 0.2 / 0.3 / 0.2 / 0.1 (0.8) | - | Unique (12) |
| Thorium | 0.3 / 0.5 / 0.3 / 0.2 (1.3) | - | Unique (12) |
| Cobalt | 0.5 / 0.7 / 0.5 / 0.3 (2.0) | 0.5 / 0.7 / 0.5 / 0.3 (2) | Rare (24) |
| Adamantite | 0.7 / 1.0 / 0.7 / 0.4 (2.8) | 1.0 / 1.4 / 1.0 / 0.6 (4) | Rare (24) |
| Mithril | 1.0 / 1.3 / 0.9 / 0.6 (3.8) | 1.5 / 2.1 / 1.5 / 0.9 (6) | Legendary (48) |
| Onyxium | 1.3 / 1.8 / 1.2 / 0.7 (5.0) | 2.0 / 2.8 / 2.0 / 1.2 (8) | Legendary (48) |

- Health + Physical / Projectile resistance: **unchanged** - the same level curve as today (`base.armor` x `base.hpCurve` / `base.resCurve`), times a
  new row `garmor.mining.baseShare` (default 100 %, see section 5). Other vanilla lines (Thorium Poison resistance ...) stay.
- No Mining Power or move speed on single pieces - those are full-set only (Skyy: "higher tiers can give a little more").
- Wisdom ladder = `research/cloud/Gathering-Numbers-Reconciled.md` X3 (Cobalt 2 ... Onyxium 8), under `armor.wisdom.cap` 10.

### 2.4 Full-set bonus (all 4 pieces of the same tier, all active)

The Fortune / speed / move-speed numbers are `research/cloud/Untiered-Mythic-Spec.md` 3.2 (locked "as tabled"). Same "pickaxe or shovel held" rule.

| Tier | Mining Fortune | Mining Power ("speed") | Move speed | Later (hidden until live) |
|---|---|---|---|---|
| Copper | +1 | - | - | - |
| Iron | +1.5 | - | - | - |
| Thorium | +2.5 | +5 % | - | - |
| Cobalt | +4 | +8 % | - | - |
| Adamantite | +5.5 | +10 % | +5 % | - |
| Mithril | +7.5 | +12 % | +8 % | - |
| Onyxium | +10 | +15 % | +10 % | Vein Burst level (SkyyTrees hook, its own round) |

- "Speed" is shipped as **Mining Power** (fewer hits on rock / ore / soil) because that path is LIVE in SkyyGear (`GearToolHitSys`, the same
  DamageBlockEvent multiplier as the tool). The swing-speed version needs SkyyTrees and is not live (Reconciled S3) - question 1.
- 1 to 3 pieces: no bonus (Skyy: "the same as vanilla until you put on all 4"). Mixed tiers: no bonus.
- Tooltip (every piece, green): `Set: Cobalt Mining Set (3/4)` / `Full set: Mining Fortune +4, Mining Power +8% (pickaxe or shovel in hand)`.

## 3. Rows for SkyyGear G1's set table

Format of `research/cloud/Untiered-Mythic-Spec.md` 3.1 (`set.<setId>` = name | pieces | bonus lines stat=value | rarity), plus two columns
mining needs (the builder maps them onto the real 0.2.14 syntax - UNVERIFIED):

- **member** `id` = membership by item id (a crafted vanilla piece counts; no document `set` field needed, so existing pieces count with no
  saved-data rewrite). A piece whose document HAS a `set` field belongs only to that set (so a quest Set on the same base id would never count
  here) - G1's `doc` mode stays the default for quest Sets.
- **need** `mining` = the bonus (and the pieces' mining lines) only apply while a pickaxe or shovel is held.

```
set.mining_copper=Copper Mining Set|Armor_Copper_Head,Armor_Copper_Chest,Armor_Copper_Hands,Armor_Copper_Legs|mfort=1|set|id|mining
set.mining_iron=Iron Mining Set|Armor_Iron_Head,Armor_Iron_Chest,Armor_Iron_Hands,Armor_Iron_Legs|mfort=1.5|set|id|mining
set.mining_thorium=Thorium Mining Set|Armor_Thorium_Head,Armor_Thorium_Chest,Armor_Thorium_Hands,Armor_Thorium_Legs|mfort=2.5,mpow=5|set|id|mining
set.mining_cobalt=Cobalt Mining Set|Armor_Cobalt_Head,Armor_Cobalt_Chest,Armor_Cobalt_Hands,Armor_Cobalt_Legs|mfort=4,mpow=8|set|id|mining
set.mining_adamantite=Adamantite Mining Set|Armor_Adamantite_Head,Armor_Adamantite_Chest,Armor_Adamantite_Hands,Armor_Adamantite_Legs|mfort=5.5,mpow=10,spd=5|set|id|mining
set.mining_mithril=Mithril Mining Set|Armor_Mithril_Head,Armor_Mithril_Chest,Armor_Mithril_Hands,Armor_Mithril_Legs|mfort=7.5,mpow=12,spd=8|set|id|mining
set.mining_onyxium=Onyxium Mining Set|Armor_Onyxium_Head,Armor_Onyxium_Chest,Armor_Onyxium_Hands,Armor_Onyxium_Legs|mfort=10,mpow=15,spd=10|set|id|mining
```

Per-piece rows (new table, Server Setup -> Gear -> Gathering armor -> Mining; `<tier>=fortune H,C,L,Ha|wisdom H,C,L,Ha|lamp 0-4`):

```
garmor.mining.copper=0.1,0.2,0.1,0.1|0,0,0,0|1
garmor.mining.iron=0.2,0.3,0.2,0.1|0,0,0,0|2
garmor.mining.thorium=0.3,0.5,0.3,0.2|0,0,0,0|2
garmor.mining.cobalt=0.5,0.7,0.5,0.3|0.5,0.7,0.5,0.3|3
garmor.mining.adamantite=0.7,1.0,0.7,0.4|1.0,1.4,1.0,0.6|3
garmor.mining.mithril=1.0,1.3,0.9,0.6|1.5,2.1,1.5,0.9|4
garmor.mining.onyxium=1.3,1.8,1.2,0.7|2.0,2.8,2.0,1.2|4
```

New stat keys (gathering lines, never in the random roll pools): `mfort` Mining Fortune (points, 1 = +1 % extra drop), `mwis` Mining Wisdom
(%), `mpow` Mining Power (%). `spd` is the existing live Speed stat.

## 4. Numbers (python3)

Method: pieces total P = half the locked set bonus B, rounded to 0.1, split 25 / 35 / 25 / 15 by largest remainder; full set = P + B. B/P is
about 2 at every tier, so the 4th piece is worth about 2/3 of the set (wear all 4). Cap check against `armor.fortune.cap` 15 (no rarity
multiplier any more - Set items have none).

| Tier | Pieces P | Bonus B | Full set | 3 pieces (no bonus) | Under cap 15 |
|---|---|---|---|---|---|
| Copper | 0.5 | 1 | 1.5 | 0.38 | yes |
| Iron | 0.8 | 1.5 | 2.3 | 0.60 | yes |
| Thorium | 1.3 | 2.5 | 3.8 | 0.98 | yes |
| Cobalt | 2.0 | 4 | 6.0 | 1.50 | yes |
| Adamantite | 2.8 | 5.5 | 8.3 | 2.10 | yes |
| Mithril | 3.8 | 7.5 | 11.3 | 2.85 | yes |
| Onyxium | 5.0 | 10 | **15.0** | 3.75 | yes - exactly the cap, nothing wasted |

The curve (on-level player, Fortune points; perk 0.5 / level, tool 0.2 x L x (1 + 2 % x tier) as live in 0.2.13, armor = full set):

| Tier | Lv | Perk | Tool | Armor | Total | Armor share |
|---|---|---|---|---|---|---|
| Copper | 1 / 18 | 0.5 / 9.0 | 0.2 / 3.7 | 1.5 | 2.2 / 14.2 | 68 % / 11 % |
| Iron | 15 / 23 | 7.5 / 11.5 | 3.1 / 4.8 | 2.3 | 12.9 / 18.6 | 18 % / 12 % |
| Thorium | 20 / 28 | 10.0 / 14.0 | 4.2 / 5.9 | 3.8 | 18.0 / 23.7 | 21 % / 16 % |
| Cobalt | 25 / 38 | 12.5 / 19.0 | 5.4 / 8.2 | 6.0 | 23.9 / 33.2 | 25 % / 18 % |
| Adamantite | 35 / 43 | 17.5 / 21.5 | 7.7 / 9.5 | 8.3 | 33.5 / 39.3 | 25 % / 21 % |
| Mithril | 40 / 49 | 20.0 / 24.5 | 9.0 / 11.0 | 11.3 | 40.3 / 46.8 | 28 % / 24 % |
| Onyxium | 40 / 49 | 20.0 / 24.5 | 9.0 / 11.0 | 15.0 | 44.0 / 50.5 | 34 % / 30 % |

(Trees, pets, accessories, collections come on top, all under the global 100.) A full set is worth about one tool tier, as Untiered-Mythic 3.2
intended. Onyxium tool tier index 6 (same as Mithril) is an assumption - UNVERIFIED.

Mining Power check: hits on a block = ceil(vanilla hits / (tool factor x (1 + armor %))), so a small % only matters at a threshold. Examples
(python3): tool x1.25 on an 8-hit block 7 -> 6 hits from +8 %; tool x1.75 on a 4-hit block 3 -> 2 hits only at +15 %; tool x2.0 never changes
on 4 / 6 / 8-hit blocks. So Mining Power on armor is a small, felt-sometimes bonus (question 1).

## 5. Combat armor and The Armory being OFF until 0.7

| Point | Rule now (Armory off) | When The Armory is back (0.7) |
|---|---|---|
| Who wears metal | anyone; mining lines need Mining level + a pickaxe / shovel in hand | same |
| Health / resistance | **kept at 100 %** (`garmor.mining.baseShare` 100): the mob curve is built on metal armor (`research/cloud/Armor-Types-Spec-Draft.md` "Heavy = today's metal numbers exactly"), and right now metal + Bronze / Steel / Heavy Leather are the only Heavy armor | Skyy may lower `baseShare` (e.g. 60) once Armory Heavy sets drop (question 3) |
| Combat modifiers | new pieces get none (Set, fixed lines) | same |
| Gate | Mining level (a Warrior with Mining 5 cannot use a Lv 30 Cobalt piece) - question 2 | same |
| Old pieces (made before 0.2.15) | **untouched**: their rarity, level and rolled combat modifiers stay (no saved-data rewrite); they count for the set by id and get the mining lines; their gate becomes Mining | same |
| Loot | the 28 ids leave the random combat loot (bag pool, the 4 % unidentified roll, chest extras): "gathering armor never drops unidentified". A vanilla native drop of one = an identified Set piece at the mob level clamped to the band. Heavy bags keep Bronze / Steel / Heavy Leather | The Armory's Heavy sets refill the Heavy bags |
| Looks | no Alteration Table (The Armory off) -> no Iron colours today | The Armory's 20 Iron colours (`Armor_Iron_<Slot>_<Colour>`) count as Iron mining pieces through the `gear:base` map (`research/Recolor-Plan.md` P1); other metals get our 8 recolours (P2) |
| Quest Sets | a quest Set must NOT use these 28 ids (section 3 member rule; question 7) | same |

## 6. Helmet light (feasible now?)

- Vanilla metal helmets have **no lamp** in their model, so nothing "shows a light" falsely; the lock (gear.md:72) is met either way. Skyy still
  wants mining helmets with a working light, so: a REAL light, no new art.
- Reuse the Lantern exactly (`research/cloud/Mining-Lamp-Spec.md` sections 1-2: one light per player, the stronger wins, same solver). To avoid
  new solver rows, a tier maps to one of the 4 existing Lantern rarities (table 2.3: Copper Normal 6, Iron / Thorium Unique 12, Cobalt /
  Adamantite Rare 24, Mithril / Onyxium Legendary 48). The lamp spec's in-between reaches (18 / 34) come later if Skyy wants them.
- Split: **SkyyGear 0.2.15** posts `gear:lamp:<uuid>` = Integer 1-4 (the worn ACTIVE helmet's lamp rarity) on the `skyy.bridge` map and removes it
  when none (logout, profile:busy, helmet off, under-level). Harmless with no reader. **SkyyAccessories 0.5.10** (its own lean round, same day
  or next): the Lantern system uses max(Lantern rarity in the bag, `gear:lamp`), row `lantern.helmet` (on). No fuel, always on while worn; `/lamp`
  toggle later. Works without a pickaxe in hand.
- If 0.5.10 cannot land: the helmets simply give no light (no glow, no text line claiming one - the tooltip line `Lamp: ...` only shows when
  the bridge reader exists, `acc:lamp` = "on" published by 0.5.10).

## 7. Ready-to-paste: SkyyGear 0.2.15 build task

```
SkyyGear 0.2.15 = MINING ARMOR (vanilla metal sets = green Mining Sets). FULL ROUND (economy Fortune, new doc rarity on crafts, loot change).
Derive from the SET pin 0.2.14 with tools/gear_0_2_15_patch.py. Spec: research/cloud/Mining-Armor-Spec.md (sections 2-6 = the numbers).
Skyy's words: "use vanilla for mining, and armory for combat gear. that makes things easy!" (gear.md:116); "yes, gathering armor uses the set
label, the full set gives a little bonus gathering fortune (mining foraging ect.) and the higher tiers can give a little more like mining
/chopping speed, movement speed, ect." (:125); "mining armor starts at copper" (:77); "make sure that if those mining helmets show a light, it
works" (:72); "We we are making the vanilla armor the mining gear so I'd do that first" (:138).
SCOPE (SkyyGear only):
 1. The 28 ids of spec 2.1 = kind mining (default kind.prefix rows, appended once to an existing config: only missing lines). Mining kind is
    ENFORCED for these armor ids: gate = Mining, armor box stays hidden, Health / resistance from the level curve x garmor.mining.baseShare (100).
 2. New crafts / native drops of the 28 ids: rarity set, 0 modifiers, level = Mining level (craft) or mob level, clamped to the band. Never in
    LOOT_POOL (bags, unid roll, chest extras). Reforge modifier tab refuses; Level up allowed (Set cost). Old documents untouched.
 3. Per-piece mining lines (garmor.mining.<tier> rows) + G1 set rows (spec 3, member=id, need=mining). Active only with a pickaxe / shovel held.
 4. Fortune: worn armor Fortune (pieces + full-set bonus, capped armor.fortune.cap 15) ADDED to the held tool's Fortune in the existing
    skill:bonus "gear" source (dd.mining, same only.mining filter) - no SkyySkills change. Post also when the tool part is 0.
 5. Wisdom: xp.mining in the same "gear" source (armor.wisdom.cap 10). Mining Power: GearToolHitSys factor x (1 + mpow/100), pickaxe on rock / ore,
    shovel on soil only. Move speed: spd through the existing movement path, only while the pickaxe / shovel is held.
 6. Tooltip: green Set block (n/4, bonus lines, "(pickaxe or shovel in hand)"), per-piece lines; gear:lamp:<uuid> Integer bridge key (spec 6).
 7. Rows (Server Setup -> Gear -> Gathering armor -> Mining): garmor.mining.enabled, the 7 tier rows, baseShare, armor.fortune.cap 15,
    armor.wisdom.cap 10, lamp map. Off = these ids behave exactly as 0.2.14.
FILES: tools/gear_0_2_15_patch.py, SkyyGear/build_skyygear_0.2.15.py (generated), SkyyGear/test_skyygear_0.2.15.py. Nothing else.
HARNESS (must pass):
 - all 28 ids exist in Assets.zip, ArmorSlot Head/Chest/Hands/Legs, ISS_Armor_Heavy; none in LOOT_POOL; Heavy bag pool still non-empty.
 - table sums = spec 4 (full sets 1.5 / 2.3 / 3.8 / 6.0 / 8.3 / 11.3 / 15.0, all <= 15); Wisdom <= 10.
 - pickaxe + 4 Cobalt worn: "gear" dd.mining = (tool + 6.0) / 100, only.mining = Rock_,Rubble_,Ore_; shovel -> Soil_; hatchet / sword / empty hand
   -> no armor part; 3 of 4 -> no bonus; Cobalt x3 + Mithril -> no bonus; one under-level piece -> its lines 0 and no bonus.
 - xp.mining = Wisdom / 100; mpow multiplies only pickaxe/shovel hits on their own block types; spd on with a pickaxe, gone <= 1 s after a swap.
 - Health / resistance of an active Copper / Iron / Cobalt / Mithril piece at its band start and top = 0.2.14 values exactly (baseShare 100).
 - craft: Armor_Cobalt_Chest by a Mining 30 / class 10 player -> lvl 30, rarity set, 0 mods; by Mining 12 -> lvl 25 (clamp) and inactive.
 - an old 0.2.14 Rare Iron chest document (3 modifiers) reads byte-identical, counts for the Iron set, shows mining lines.
 - kind rows appended once (second run no change; a hand-edited kind.prefix line kept + logged); garmor.mining.enabled=false = 0.2.14 behaviour.
 - gear:lamp posted / removed (helmet on, off, under-level, logout); -Xverify:all; access audit; crosscheck --baseline; lint 0 fails.
SMOKE TEST: "[SkyyGear] 0.2.15 ready" line, no SEVERE, no asset-validation failure.
SKYY CHECKS IN GAME: (1) craft a Copper set: green Set label, "Requires Mining N", Mining Fortune lines; (2) wear 3 -> "Set (3/4)" grey, wear 4 ->
green, bonus listed; (3) mine stone with a pickaxe with / without the full set - more extra drops with it; (4) hold a sword: bonus lines grey;
(5) Health still shown and applied; (6) an old metal piece still works; (7) Heavy loot bags still drop (Bronze / Steel). Lamp: after
SkyyAccessories 0.5.10.
ROLLBACK: to 0.2.14 is safe (Set rarity is live there; kind rows make the ids unenforced mining kind -> 0.2.14 shows the vanilla box again
until rows are removed: note it in deploy_set comments).
```

SkyyAccessories 0.5.10 (lean round, after 0.2.15): read `gear:lamp:<uuid>`, use max with the Lantern rarity, row `lantern.helmet` (on), publish
`acc:lamp` = "on"; harness: Lantern-only behaviour byte-equal to 0.5.9 when the key is absent; Skyy re-runs the 0.5.5 Lantern test list.

## Questions for Skyy

| # | Question | Default |
|---|---|---|
| 1 | The "speed" in the set bonus: ship it now as Mining Power (fewer hits, live, but small % only matters at thresholds), or wait for real swing speed (needs SkyyTrees)? | [Mining Power now] |
| 2 | Metal armor needs your MINING level to wear (a Warrior with Mining 5 can't use Iron) - fine while The Armory is off? | [yes, Mining gate now] |
| 3 | Mining sets keep full Health / resistance (they are the only Heavy armor till 0.7). Lower it later when The Armory's Heavy sets drop? | [keep 100 % now; ask again after 0.7] |
| 4 | Old metal armor already in inventories: leave as is (keeps its combat rolls), or convert to Set (loses the rolls)? | [leave as is] |
| 5 | Mining lines only with a pickaxe or shovel in hand (incl. the move speed)? | [yes] |
| 6 | Helmet light by tier = Lantern Normal / Unique / Unique / Rare / Rare / Legendary / Legendary (Copper..Onyxium)? | [yes] |
| 7 | Vanilla Copper armor is the Copper Mining Set, so the Zone 1 quest Set "Clerk's Copper" (`research/cloud/SkyyQuests-Zone1-Spec.md`, set=copper_quest on Armor_Copper_*) needs other base items - e.g. Heavy Leather or Bronze, or an Armory set after 0.7? | [quest Sets never use the 28 mining ids; Clerk's set on Bronze / Heavy Leather] |
| 8 | Remove metal armor from random combat loot (bags, unidentified drops)? | [yes] |

## For the local session

1. **G1 syntax:** SkyyGear 0.2.14 is not in the repo; map section 3's rows (incl. `member=id` and `need=mining`) onto its real set-table format.
2. **Quest Set clash:** `research/cloud/SkyyQuests-Zone1-Spec.md` proposes "Clerk's Copper" on `Armor_Copper_Head/_Chest/_Hands/_Legs` (set=copper_quest).
   Vanilla Copper armor is the Copper MINING set; the quest Set needs other base items (default Bronze / Heavy Leather), so the two specs don't
   both claim the same ids (question 7).
3. UNVERIFIED: `Armor_Onyxium_Head/_Chest/_Legs` in Assets.zip (only Hands is build-checked) - the 0.2.15 harness asserts all 28.
4. UNVERIFIED: whether an armor id of kind `mining` can join the enforced armor pass (GearABox, lockSums) with a small change, or needs its own
   enforced-kind list for armor.
5. UNVERIFIED: which vanilla mob / chest drop lists contain these 28 ids (`Server/Drops/`), and the Onyxium tool tier index (6 assumed).
6. UNVERIFIED: whether any vanilla helmet already emits light; how the SkyyAccessories 0.5.9 Lantern system picks the rarity per player (where
   `gear:lamp` plugs in).
7. After 0.7: The Armory's `Armor_Iron_<Slot>_<Colour>` ids -> Iron mining pieces (Recolor-Plan P1 `gear:base`); the set check reads the base id.
