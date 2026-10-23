# UT build sheet - the first 28 Untiered (UT) items (12 armor sets + 16 weapons)

Cloud draft, 2026-10-23. A BUILD sheet for the local session: ids, stat bands, the exact `utfx` input the balance fit reads, drop sources,
lang keys, harness checks, builder split, rollback notes, test steps. Source design: `research/cloud/UT-Design-Draft.md` (its defaults taken;
nothing in `docs/answered/` overrides them - the draft is newer than every UT line there). Nothing here is built. Every engine fact that needs
`Assets.zip` / `HytaleServer.jar` is **UNVERIFIED** and listed at the end. Numbers are START values inside a band; the build's own fit
(section 3) sets the body power, Skyy tunes the rest in Server Setup.

## 0. Decisions followed (newest wins; not re-decided)

| File : line | Skyy's lock (short) | Used here |
|---|---|---|
| `docs/answered/gear.md` 123, 124 | RotMG-style UT: good in its band, never strictly better; orange | every row = one upside + one real downside |
| `docs/answered/gear.md` 126, 127 | UT only from mob drops, loot chests, bosses, quests; never crafted, never in shops | drop column; no recipe, no shop |
| `docs/answered/gear.md` 137 | UT drops through the orange Mystery Bag; direct trade OK, never Bazaar / Auctions | sources section 5 |
| `docs/answered/economy.md` 89 | market wall: Mythic + UT + Sets | automatic for the `untiered` rarity |
| `docs/answered/gear.md` 253 | UT per ZONE, at the zone's top tier | one band per zone |
| `docs/answered/gear.md` 270 | per zone 3 UT armor sets (Cloth / Light / Heavy) + 1 UT weapon per class | the 12 sets; Spellblade Z1 slot |
| `docs/answered/gear.md` 271 | the 5 Armory UTs ship as drafted (Hepta Axe = Berserker Z4) | Hepta not rebuilt; no duplicate |
| `docs/answered/gear.md` 272 | the class weapon alternates primary / alt: Z1 P, Z2 alt, Z3 P, Z4 alt, Z5 P | weapon types below |
| `docs/answered/gear.md` 273 | UT = trade-off (examples incl. robes with less Mana but HP / defence, heavy the opposite) | A1 / A3 |
| `docs/answered/gear.md` 274 | elements first, UTs use them | element fixed lines on weapons |
| `docs/answered/gear.md` 285 | UT = the zone's alloy, late zone; sources = elites, mini bosses, dungeons; Mythic = full bosses | tier tag + source |
| `docs/answered/gear.md` 313 | every UT tuned to at least Fabled (per-item `utpow`) | section 3 fit, no hand power |
| `docs/answered/gear.md` 314 | UT bands move to the END of each zone | bands from `tools/tier_tags.py` METAL_BANDS |
| `docs/answered/gear.md` 316 | UT drop rate = the P5 UT meter (36 points, elite 1 / mini 5 / dungeon boss 10) | no new drop odds |
| `docs/answered/gear.md` 319 | crafted items never UT / Mythic | build asserts no recipe |
| popup 2026-10-23 (not yet in `docs/answered/gear.md` - local session records it) | Q "The 12 new UT armor sets + 32 UT weapons (Zones 2-5): what naming style?" -> "Zone lore names" (not office jokes) | all 28 renamed from zone lore (section 2); ids carry the lore word, no joke |
| `docs/answered/world.md` 59 | Zone 1 final quest UT reward = choose 1 of 3 (class UT weapon or a UT chest piece) | The Azure Arc becomes the Spellblade's pick |

Also followed: `PROJECT-RULES.md` (tier tag first in flavor text, four power sources, sort by tier, everything editable in Server Setup,
one-time migrations, no dev gates: rows ship ON), `research/Vanilla-UI-Style-Guide.md` section 15 (orange name, green upside, red downside),
`tools/CONFIG-CONTRACT.md` (table entries + new scalar rows), `tools/AGENT-BRIEF.md` (builder rules). No new menu (`research/Menu-Pattern.md`):
everything appears in the existing Gear tooltip, `/gear ut`, and Server Setup -> Gear -> Rarity.

## 1. Which 28, and why

The draft gives its own order in `research/cloud/UT-Design-Draft.md` section 5 ("Build order"): **step 1 = rows-only items** (the 12 armor sets
and every weapon whose upside is already a `utfx` key), **step 2 = items that need new engine**; and its Question 6 default **parks 4 weapons**
(The Rubber Stamp, The Firewall, The Resignation, Hot Desking). Applied in that order:

1. **All 12 armor sets (A1-A12)** - every one is rows-only in today's grammar (A11's optional dodge bonus left out). Skyy's 270 target lists
   armor first, and all three categories per zone then exist for Zones 2-5.
2. **The 11 weapons whose upside the draft names as a utfx key** (pierce, back, lowhp, dmg, heal, kb, swing, life steal) - draft names
   Reorg, Cc Line, Two Weeks' Notice, Hard Stop, Fire Drill, Off The Record, Second Shift, Exit Interview, Open Door, Handshake, Stress Ball, plus
   Style Guide (the draft counts its "range" as a key) = 12 (now rows 14, 15, 17-21, 24-28 under their new lore names, section 2).
3. **4 more to reach 28**, smallest engine first, never a parked one: draft **The Long Meeting** = **The Azure Arc** (fills the only missing Zone 1
   slot, Spellblade - gear.md 270; rows-only if the vanilla longsword sweep already hits several targets), draft **The Paper Cut** = **Scarak
   Stinger** (its "bleed" becomes the live 0.3.39 Poison line - rows-only), draft **Hostile Takeover + Deadline** = **Raptorfang + Bonewhistle**
   (share ONE new trick pair, target Health).

Left for the next batch: Sticky Note, Red Tape, Quarterly Review, Final Notice, Escalation, Reply All, Stapler, Overbooked, Conference Call,
Lost & Found, Retention Plan, Coat Check (12 weapons that need class / engine work) + the 4 parked = 16 weapons. Hepta Axe exists already.

**Grammar corrections** (the draft assumed keys that do not mean what it needs - checked in `SkyyGear/build_skyygear_0.3.40.py` 1767-1777):
`range+N` is a LIMIT (a shot past N blocks deals nothing), not more reach; `kb+N` is knockback DEALT, not knockback resist. So:
A4 "range +" becomes Speed +; A6 loses "knockback resist"; Sandscript Codex (draft Style Guide) loses "spell range +" (keeps cheaper Mana);
Stormfossil (draft Off The Record) loses "echo"; Hotspring Blessing's (draft Second Shift) "heals nearby allies" needs a new `aura` trick
(otherwise it copies The Second Opinion). See Question 2.

## 2. The 28 rows

Size classes (draft section 2): S = Filing Cabinet Head / Hands size, M = Chest / Legs size, L = twice M (weapons only). Armor values are PER
PIECE: Head / Hands get the S line, Chest / Legs the M line (Filing Cabinet pattern, `SkyyGear/build_skyygear_0.3.40.py` 5626-5629).
**Engine:** R = rows only (today's keys); T = needs a new trick word (section 4); U = rows only IF an UNVERIFIED reader exists (section 9).
The `utfx` column is the exact balance input: `<body stat keys>,<fixed lines + tricks>` (Head/Hands | Chest/Legs for armor).

### 2.1 Armor sets (owner SkyyGear; ids `Armor_UT_<Set>_<Head|Chest|Hands|Legs>`)

| # | Set id word / name (pieces) | Slot / type | Tier tag, band | Stat bands per piece (S / M) | utfx input S \| M | Engine | Drop source |
|---|---|---|---|---|---|---|---|
| 1 | `OasisWarden` Oasis Warden's (Hood / Robe / Cuffs / Skirt) | Cloth | `T6 Dusk`, 35-43 | hp +3..+8 %, def +1..+4 / mregen -6..-15 % | `mp def,hp+4 def+2 mregen-8` \| `mp def,hp+6 def+3 mregen-12` | R | Z2 elites / mini bosses / dungeon boss, Lv 35-43 |
| 2 | `ScarakStalker` Scarak Stalker's (Cap / Vest / Gloves / Pants) | Light | `T6 Dusk`, 35-43 | back +6..+15 %, cc +1..+2 / front -4..-10 % | `cc cd,back+8 cc+1 front-6` \| `cc cd,back+12 cc+2 front-8` | U (back / front on armor) | Z2 as row 1 |
| 3 | `RedDuneSentinel` Red Dune Sentinel (Helm / Plate / Gauntlets / Greaves) | Heavy | `T6 Dusk`, 35-43 | mp +1..+4, mregen +5..+12 % / hp -2..-5 %, taken +1..+3 % | `def mp,mp+2 mregen+6 hp-3` \| `def mp,mp+3 mregen+10 hp-4 taken+2` | R | Z2 as row 1 |
| 4 | `EverfrostWanderer` Everfrost Wanderer's (Hood / Shroud / Wraps / Hem) | Cloth | `T9 Azurvane`, 55-63 | spd +1..+3, mp +1..+4 / hp -3..-8 % | `mp,spd+1 mp+2 hp-4` \| `mp,spd+2 mp+3 hp-6` | R | Z3 elites / mini bosses / dungeon boss, Lv 55-63 |
| 5 | `YetiHunter` Yeti Hunter's (Cap / Vest / Gloves / Chaps) | Light | `T9 Azurvane`, 55-63 | lsteal +1..+3 %, cc +1 / hprp -3..-8 %, taken +1..+4 % | `cc cd,lsteal+1 cc+1 hprp-4 taken+2` \| `cc cd,lsteal+2 cc+1 hprp-6 taken+3` | R | Z3 as row 4 |
| 6 | `GlacierBulwark` Glacier Bulwark (Helm / Plate / Gauntlets / Greaves) | Heavy | `T9 Azurvane`, 55-63 | taken -2..-6 % / spd -1..-2, stam -1 | `def,taken-3 spd-1` \| `def,taken-5 spd-2 stam-1` | R | Z3 as row 4 |
| 7 | `GhostGroveMystic` Ghost Grove Mystic's (Hood / Robe / Cuffs / Skirt) | Cloth | `T12 Cinder`, 75-83 | dmg +5 % / mregen -10 % (all pieces, as drafted in `research/UT-Lines-Draft.md` 3) | `mp stam,dmg+5 mregen-10` (all 4) | R | Z4 elites / mini bosses / dungeon boss, Lv 75-83 |
| 8 | `GeyserRunner` Geyser Runner's (Hat / Duster / Gloves / Boots) | Light | `T12 Cinder`, 75-83 | spd +1..+4, stam +1..+2 / dmg -1..-3 %, hp -1..-3 % | `cc,spd+2 stam+1 dmg-1` \| `cc,spd+3 stam+1 dmg-2 hp-2` | R | Z4 as row 7 |
| 9 | `CalderaGuard` Caldera Guard (Helm / Plate / Gauntlets / Greaves) | Heavy | `T12 Cinder`, 75-83 | def +2..+6, hprp +3..+8 % / spd -1, lowtaken +5..+15 % | `def,def+3 hprp+4 spd-1 lowtaken+6` \| `def,def+5 hprp+6 spd-1 lowtaken+10` | T (`lowtaken`) | Z4 as row 7 |
| 10 | `FossilSeer` Fossil Seer's (Cowl / Mantle / Sleeves / Train) | Cloth | `T15 Lumen`, 95-103 | lowhp +5..+12 %, mp +1..+4 / hp -3..-8 % | `mp,lowhp+6 mp+2 hp-4` \| `mp,lowhp+10 mp+3 hp-6` | U (lowhp on armor) | Z5 elites / mini bosses / dungeon boss, Lv 95-103 |
| 11 | `Raptorhide` Raptorhide (Hood / Coat / Gloves / Boots) | Light | `T15 Lumen`, 95-103 | spd +1..+3, stam +1..+2 / taken +1..+4 %, hp -1..-4 % | `cc,spd+2 stam+1 taken+2 hp-2` \| `cc,spd+3 stam+2 taken+3 hp-3` | R | Z5 as row 10 |
| 12 | `LavaBastion` Lava Lake Bastion (Helm / Plate / Gauntlets / Greaves) | Heavy | `T15 Lumen`, 95-103 | hp +4..+8 %, def +2..+5, taken -1..-3 % / mregen -6..-15 %, spd -1 | `def,hp+5 def+2 taken-1 mregen-8 spd-1` \| `def,hp+7 def+4 taken-2 mregen-12 spd-1` | R | Z5 as row 10 |

### 2.2 Weapons (owner = the mod that builds that family's base item today - UT_ROWS rule; see section 7)

| # | Id | Name | Class / type (P / alt) | Tier tag, band | Stat bands | utfx input | Engine | Drop source |
|---|---|---|---|---|---|---|---|---|
| 13 | `Weapon_Longsword_UT_AzureArc` | The Azure Arc | Spellblade 2h sword (P) | `T3 Bronze`, 15-23 | fAir +3..+6 % / swing Slow (fewer hits = Momentum builds slower) | `str cc,fAir+4 swing=slow` | U (vanilla sweep) | Z1 elites / mini bosses / dungeon boss Lv 15-23 + Z1 final quest pick |
| 14 | `Weapon_Spellbook_UT_SandscriptCodex` | The Sandscript Codex | Mage spellbook (alt) | `T6 Dusk`, 35-43 | mcost -20..-35 % / dmg -15..-25 % | `mp cc,mcost-25 dmg-20` | T (`mcost`) | Z2 as row 1 |
| 15 | `Weapon_Fist_UT_SteppeWind` | Steppe Wind Wraps | Monk fist (alt) | `T6 Dusk`, 35-43 | swing Fast / dmg -5..-12 % | `str cc,swing=fast dmg-8` | U (speed tier on fist) | Z2 as row 1 |
| 16 | `Weapon_Kunai_UT_ScarakStinger` | Scarak Stinger | Assassin kunai (alt) | `T6 Dusk`, 35-43 | poison +8..+16 % (over poison.time 10 s) / dmg -15..-25 % | `cc cd,poison+12 dmg-20` | R | Z2 as row 1 |
| 17 | `Weapon_Wand_UT_HotspringBlessing` | Hotspring Blessing | Priest wand (P) | `T9 Azurvane`, 55-63 | aura +30..+60 % (heal orb also heals party in 8 blocks) / dmg -20..-30 % | `mp hpr,aura+50 dmg-25` | T (`aura`) | Z3 as row 4 |
| 18 | `Weapon_Spear_UT_MagmaLance` | Magma Lance | Warrior spear (alt) | `T12 Cinder`, 75-83 | pierce + fFire +2..+4 % / dmg -20..-30 % | `str cc,pierce+1 dmg-25 fFire+3` | U (pierce on a spear) | Z4 as row 7 |
| 19 | `Weapon_Crossbow_UT_Stormvent` | Stormvent | Archer crossbow (alt) | `T12 Cinder`, 75-83 | pierce + fThunder +2..+4 % / range cap 16..24 blocks, dmg -15..-25 % | `str cc,pierce+1 range+20 dmg-20 fThunder+3` | U (pierce on bolts) | Z4 as row 7 |
| 20 | `Weapon_Spellbook_UT_AshfallGrimoire` | Ashfall Grimoire | Mage spellbook (alt) | `T12 Cinder`, 75-83 | dmg +15..+25 %, fFire +2..+4 % / mcost +25..+40 % | `mp cc,dmg+20 mcost+30 fFire+3` | T (`mcost`) | Z4 as row 7 |
| 21 | `Weapon_Fist_UT_EmberrootWraps` | Emberroot Wraps | Monk fist (alt) | `T12 Cinder`, 75-83 | lsteal +3..+5 % / dmg -15..-25 % | `str cc,lsteal+4 dmg-20` | R | Z4 as row 7 |
| 22 | `Weapon_Sword_UT_Raptorfang` | Raptorfang | Warrior sword (P) | `T15 Lumen`, 95-103 | tgtlow +40..+60 % / tgtfull -20..-30 % | `str cd,tgtlow+50 tgtfull-25` | T (`tgtlow`/`tgtfull`) | Z5 as row 10 |
| 23 | `Weapon_Shortbow_UT_Bonewhistle` | Bonewhistle | Archer shortbow (P) | `T15 Lumen`, 95-103 | tgtfull +50..+70 % / tgtlow -10..-20 % | `str cc,tgtfull+60 tgtlow-15` | T (same pair) | Z5 as row 10 |
| 24 | `Weapon_Daggers_UT_DeepcaveShadow` | Deepcave Shadow | Assassin daggers (P) | `T15 Lumen`, 95-103 | back +70..+100 % / front -40..-60 % | `cc cd,back+80 front-50` | R | Z5 as row 10 |
| 25 | `Weapon_Axe_UT_PrimalCleaver` | Primal Cleaver | Berserker axe (P) | `T15 Lumen`, 95-103 | lowhp +40..+60 %, lsteal +2..+4 % / hp -10..-15 % | `str lsteal,lowhp+50 lsteal+3 hp-12` | R | Z5 as row 10 |
| 26 | `Weapon_Staff_UT_Stormfossil` | The Stormfossil | Mage staff (P) | `T15 Lumen`, 95-103 | pierce + fThunder +2..+4 % / taken +5..+10 % | `mp cc,pierce+1 taken+8 fThunder+3` | R | Z5 as row 10 |
| 27 | `Weapon_Wand_UT_Cavewind` | Cavewind | Priest wand (P) | `T15 Lumen`, 95-103 | dmg +20..+30 %, fAir +2..+4 % / heal orb off (heal -100) | `mp cc,dmg+25 heal-100 fAir+3` | R (+ optional pierce off, U) | Z5 as row 10 |
| 28 | `Weapon_Bo_UT_CrushingTail` | Crushing Tail | Monk Bo (P) | `T15 Lumen`, 95-103 | kb +100..+200 %, fAir +2..+4 % / boss -20..-40 % | `str cc,kb+150 boss-30 fAir+3` | T (`boss`) | Z5 as row 10 |

Counts: 12 sets (48 ids) + 16 weapons = **64 new ids, 28 items**. Classes covered by the 16 weapons: Spellblade 1, Mage 3, Monk 3, Priest 2,
Assassin 2, Archer 2, Warrior 2, Berserker 1. Element lines per the draft's Element column (Question 4 default).

**Where each name comes from** (Skyy 2026-10-23 "Zone lore names"; zone and place names from `research/cloud/Story-Script-Zones-2-5.md`
section 0, `research/cloud/Outposts-List.md` and `research/cloud/Zone-Archipelago-Spec.md`; the item names themselves are NEW and UNVERIFIED):

| Zone (lore) | Lore anchors used | Items |
|---|---|---|
| Z1 Emerald Wilds | the Azure forest (blue forest outpost) | 13 The Azure Arc |
| Z2 Howling Sands | Oasis, the Scarak nest + Broodmother (Poison zone), Red Dune, the Golden Steppes, sandstone records hall | 1 Oasis Warden's, 2 Scarak Stalker's, 3 Red Dune Sentinel, 14 Sandscript Codex, 15 Steppe Wind Wraps, 16 Scarak Stinger |
| Z3 Whisperfrost Frontiers | Everfrost Edge, the Yeti guardian's land, Glacier Gate, Hotspring Hostel | 4 Everfrost Wanderer's, 5 Yeti Hunter's, 6 Glacier Bulwark, 17 Hotspring Blessing |
| Z4 Devastated Lands | Ghost Grove, Wastes_Geysers, the caldera path, Ashfall island, Magma Mile, Ember Roots, steam vents | 7 Ghost Grove Mystic's, 8 Geyser Runner's, 9 Caldera Guard, 18 Magma Lance, 19 Stormvent, 20 Ashfall Grimoire, 21 Emberroot Wraps |
| Z5 Dinosaur Caves | the raptor cavern, Fossil Pit, Lava Lake Landing, deep caves | 10 Fossil Seer's, 11 Raptorhide, 12 Lava Lake Bastion, 22 Raptorfang, 23 Bonewhistle, 24 Deepcave Shadow, 25 Primal Cleaver, 26 The Stormfossil, 27 Cavewind, 28 Crushing Tail |

Old working names (draft and first version of this sheet) map 1:1 by row number to the draft rows: A1-A12 = rows 1-12; rows 13-28 = Long Meeting,
Style Guide, Handshake, Paper Cut, Second Shift, Reorg, Cc Line, Fire Drill, Stress Ball, Hostile Takeover, Deadline, Two Weeks' Notice,
Hard Stop, Off The Record, Exit Interview, Open Door. None of them was a live id (no match in `SkyyGear/build_skyygear_0.3.40.py`,
`SkyyArmory/build_skyyarmory_0.1.43.py` or `tools/pack_drops.py`), so nothing in game is renamed. The Zone 1 live UTs keep their office names.

Overlap notes (no-duplicates rule, `PROJECT-RULES.md` 2): Oasis Warden's is the mirror of the Z1 Intern (Skyy asked for exactly that, gear.md 273);
Glacier Bulwark (row 6) repeats Ghost Rook's trade (less damage taken, slower) in a later zone (Question 3); Deepcave Shadow and Primal Cleaver
are bigger Z5 cousins of the Pocket Knife and Overtime (same axis, a different zone, plus Life Steal on Primal Cleaver); Crushing Tail differs
from the Turnstile by the boss-only penalty; Cavewind differs from Second Opinion by giving up the heal entirely. No new name reuses a Mythic,
boss, quest-item or pack-mod name (grep of `research/` + `docs/`): the zone guardians (Broodmother, Yeti, Ember Warden, Dragon) and the
Dragon armor idea (gear.md 156) stay free for Mythic boss gear.

## 3. Balance input (how the numbers are checked)

`tools/balance_model.py` has NO per-item UT input; it models UT only as the drop meter (`P5_UT` line 1514, `p5_ut_sim` 1520). The per-item power
check lives in the SkyyGear build, which imports the model as BM: `SkyyGear/build_skyygear_0.3.40.py` 9433-9500 (`utp_net`) evaluates each
`utfx` line with `BM.p5_dps` / `BM.p5_ehp` (`tools/balance_model.py` 1308-1323), `BM.P5_SLOT_POWER` (1246) and `BM.p5_roll_table()` Fabled
reference, then raises the item's `utpow` in 5 % steps from 70 to `UTP_CAP` 600 until it reaches Fabled (a weapon vs a Fabled weapon, a piece vs
a quarter Fabled set). The build asserts none is short (`UTP_SHORT`) or dead (`UTP_DEAD`).

So **the input per row = its `utfx` line in section 2**; `utpow` comes out of the build, never by hand. What the fit counts today:
body keys; fixed `dmg str mp cc cd lsteal hprp def tdmg` and the element `f*` lines (P5_PCT_LINES, line 1248); tricks `hp`, `taken`, `lowhp`
(x 0.5 share), `back` (x 0.25), `front` (x 0.5). NOT counted (`_UTP_UNMOD`): `swing range pierce heal kb mregen`; `spd`, `stam`, `poison` and `hpr`
are ignored by p5_dps / p5_ehp.

The builder adds the new tricks to `utp_net` (shares are **GUESS**, `research/balance/` has no source): `tgtlow` dm x (1 + 0.30 n / 100),
`tgtfull` dm x (1 + 0.15 n / 100), `boss` dm x (1 + 0.20 n / 100), `lowtaken` em / (1 + 0.5 n / 100), `poison` dm x (1 + 0.8 n / 100) (inside
utp_net only - not a model change); `mcost` and `aura` join `_UTP_UNMOD`. After the round: `python tools/balance_model.py --p9 --check` (must
still exit 0; UT meter rows unchanged) and republish the Class Balance Workbench. Do not copy any value from this file into
`research/balance/targets.md`.

Flag to review in the build report: any new row with `utpow` above 300 % - its upside is unmodelled, so the fit hands it free body power
(rows 13, 15, 17-19, 26-27 are the likely ones). Skyy can lower that row's `utpow` in Server Setup.

## 4. New trick words (inside `utfx`, no new item data)

| Word | Meaning | Read by | Rows |
|---|---|---|---|
| `tgtlow+N` | +N % damage vs a target under `utline.lowTarget` % Health | SkyyGear (damage system, like `lowhp`) | 22, 23 |
| `tgtfull+N` | +N % damage vs a target at or above `utline.fullTarget` % Health | SkyyGear | 22, 23 |
| `boss+N` | +N % damage vs a target in SkyyGear `bosses.roles` (full bosses + mini bosses) | SkyyGear | 28 |
| `lowtaken+N` | +N % damage taken while the wearer is under half Health (sibling of `lowhp` + `taken`) | SkyyGear | 9 |
| `mcost+N` | spell / shot Mana cost +N % (negative = cheaper) | SkyyArmory through `gear:fn:utfx` (like `pierce` / `heal`) | 14, 20 |
| `aura+N` | the heal orb also heals party members within `utline.auraReach` blocks at N % of its heal | SkyyArmory through `gear:fn:utfx` | 17 |

`GearUtFx.checkRow` must accept them (and refuse a typo). `part.utLines` off = all of them off, like the rest.

## 5. Drop sources (no new odds)

All 28: the P5 UT meter (Gear 0.3.35: 2.5 % a point, sure at 36; elite 1 / mini boss 5 / dungeon boss 10 points) -> an orange Mystery Bag
whose identify picks a `ut.<id>` row whose band holds the mob level (armor `utbag.armorShare` 50 %, weapons weighted x `utbag.classLean` 3 for
the killer's class), plus fresh-chest bags (`utdrop.chest`), Unclaimed Luggage (`utdrop.luggage`) and quests (`gear:fn:grant`). Never crafted,
bought, or listed. Mob-to-set mapping = the draft's Question 3 default (any elite / mini boss / dungeon of the zone, even weights). Row 13 also
joins the Zone 1 final quest's "choose 1 of 3" as the Spellblade's class weapon (`docs/answered/world.md` 59; SkyyQuests owns that reward -
not part of this round unless its reward reads the class's UT row automatically, UNVERIFIED).

## 6. Lang keys, tier tags, Server Setup rows

**Lang** (one writer per key; the mod that builds the copy writes it, `tools/ci/langdup.py` must stay clean):
- `items.<id>.name = <Name> <Piece>` e.g. `items.Armor_UT_OasisWarden_Head.name = Oasis Warden's Hood`; weapons `items.Weapon_Kunai_UT_ScarakStinger.name = Scarak Stinger`.
- `items.<id>.description = <tag> - Untiered <kind>.` built with `TT.described(id, "Untiered cloth armor.")` -> `T6 Dusk - Untiered cloth armor.`
  (kinds: cloth armor / light armor / heavy armor / sword / spear / longsword / crossbow / bow / kunai / daggers / axe / staff / wand / spellbook / fist weapon / bo staff).
- The ONE orange trade-off line is NOT a lang key: it is the text column of the `ut.<id>` row (`GearUt.note`, max 110 ASCII, no comma, no `=`), e.g.
  `ut.Armor_UT_OasisWarden_Head=35,43,Oasis warden: +4% max Health and +2 Defense but 8% slower Mana regen per piece.`
  Weapons e.g. `ut.Weapon_Kunai_UT_ScarakStinger=35,43,Every hit poisons (12% of the hit over 10 s). 20% less damage.`
  The builder writes each text from the FINAL numbers (Style Guide section 15 colours: orange name, green upside, red downside).

**Tier tags** (`tools/tier_tags.py`): a new family `ut` - 48 armor ids + 16 weapon ids, `_add(id, t, "ut", owner)` with t = 3 (Z1), 6, 9, 12, 15;
owner `SkyyGear` or `SkyyArmory` (section 7). One edit by the Gear builder; `python tools/test_tier_tags.py` must pass.

**Server Setup** (Gear -> Rarity; `tools/CONFIG-CONTRACT.md` rules; nothing new on the menu side):
- New ENTRIES (not rows) in the existing tables: `ut.<id>` (band lo / hi / trade-off text), `utfx.<id>` (section 2), `utpow.<id>` (the fit's %).
  Added by a one-time pure-addition migration (`migrate41`-style: verified History copy first, only keys the file lacks, kept + logged when an
  admin already has one, run-once marker, file bytes and line endings kept; no `utpow` lines when the file's `utline.power` is an admin value - the
  0.3.36 rule). A change-log line with Undo.
- New scalar rows (keys under `utline.` - the `ut.` prefix belongs to the table):

| Key | Label (<= 40) | Type | Default | Min | Max | Unit | Flags | Help (<= 100) |
|---|---|---|---|---|---|---|---|---|
| `utline.lowTarget` | Untiered: low target Health | int | 50 | 1 | 99 | % | live | Targets under this % Health count as low for tgtlow lines. |
| `utline.fullTarget` | Untiered: full target Health | int | 90 | 50 | 100 | % | live | Targets at or above this % Health count as full for tgtfull lines. |
| `utline.auraReach` | Untiered: heal aura reach | int | 8 | 1 | 32 | blocks | live | How far the aura heal of an Untiered wand reaches party members. |

(Times: Scarak Stinger uses the existing `poison.time`, 10 s - no new time row.)

## 7. Builder split (one mod per builder; run in this order)

| Builder | Mod (pin -> new, UNVERIFIED next number) | Does | Rows |
|---|---|---|---|
| A (Opus) | SkyyGear 0.3.40 -> 0.3.41 (`tools/gear_0_3_41_patch.py` reading the 0.3.40 generated script) | ALL 28 `ut` / `utfx` table entries + the fit; the gear-owned copies; tricks `tgtlow`, `tgtfull`, `boss`, `lowtaken` (+ utp_net weights); 3 scalar rows; migration; `tools/tier_tags.py` rows for all 64 ids; UT bag types for any family not yet in the bag type list (spellbook, kunai, fist, spear, crossbow, longsword, axe - UNVERIFIED which exist); `gear:fn:utfx` answers the new words | 1-12, and the weapons whose base family Gear builds (likely 13, 18, 19, 22-25) |
| B (Opus) | SkyyArmory 0.1.43 -> 0.1.44 (its own patch script) | the armory-owned copies (`UT_ITEMS` pattern, `SkyyArmory/build_skyyarmory_0.1.43.py` 6095); tricks `mcost`, `aura`; `pierce` for its spear / crossbow if it owns them; its lang keys with the tag first (the new ids must NOT join the `_untag39` untagged list) | 14-17, 20, 21, 26-28 (+ 18 / 19 if Armory owns those families) |

B starts after A's `tools/tier_tags.py` edit lands (one writer). Each builder: harness (section 8) + one review; then cross-check both jars
together. This is a **full round** (`PROJECT-RULES.md` 4: new items, saved-data migration, several mods) - not lean.

## 8. Harness checks (build-time asserts + a test script per mod)

1. 64 new ids unique, all contain `_UT_`, none in `Assets.zip` / any SET jar, no recipe anywhere (assert like `SkyyGear/build_skyygear_0.3.40.py` 5648-5652).
2. `utp_slot(id)` gives the intended slot for all 48 armor ids (no set word collides with Head / Helm / Cap / Hood / Robe / Plate / Boots ... words).
3. Each `ut.<id>` band = `UT_BANDS[zone]` (15-23 / 35-43 / 55-63 / 75-83 / 95-103) and the tag tier = `TT.tier_for_level(band lo)`.
4. Trade-off texts: ASCII, no comma, no `=`, <= 110 chars; one per id.
5. `GearUtFx.checkRow` accepts every section 2 line and refuses `tgtlo+5`, `mcost`, `aura+x` (typo / missing number).
6. utpow fit: no new row in `UTP_SHORT` / `UTP_DEAD`; print the 28 utpow values; list any > 300 % for the review.
7. Each row has exactly one green and one red part: at least one positive and one negative fixed word (swing=slow / heal-100 / range+N count as negative).
8. Migration: on a copy of the live config - adds exactly the missing keys, keeps admin values, History copy present, marker written, every other byte kept; a second run changes nothing.
9. `tools/test_tier_tags.py` passes; `python tools/ci/langdup.py` 0 duplicates; `TT.described` puts the tag first.
10. Every new id is `untiered` rarity -> market wall refuses Bazaar / Auctions / merchants; not in the normal random bag pool; never in an NPC shop list.
11. `python tools/ci/crosscheck.py --jar <both new jars> --baseline` and `python tools/ci/lint.py` 0 fails; `python tools/balance_model.py --p9 --check` exit 0.
12. Smoke test (`python tools/smoke_test.py --jar ...`): every `[Skyy...] ready` line, no asset-validation failure, no SEVERE.

## 9. Rollback / FLOOR notes (for the local session to add to `tools/deploy_set.py`; not edited here)

Today's pins: SkyyGear 0.3.40, SkyyArmory 0.1.43 (both above every listed floor: P5 Gear 0.3.35 / Armory 0.1.43, P6 Gear 0.3.36, P7 0.3.37,
packprep 0.3.38, elem1 0.3.39). Proposed comment:

`# FLOOR (UT 28): SkyyGear 0.3.41 + SkyyArmory 0.1.44 pin + roll back TOGETHER (Armory reads the new mcost / aura words through gear:fn:utfx).
NEVER roll either below once one of the 64 new UT ids exists in a player's hands, the Vault or a chest (unknown items to older jars - treat as
lost). Before a rollback Undo the migrate41 rows in Server Setup -> Changes (older Gear reads the ut / utfx / utpow entries for ids it lacks:
GearUt.ok refuses them, WARN only). No player-saved data changes (UT lines live in config); the skyygear_ut_hp modifier is recomputed within 1 s of join.`

## 10. In-game test steps (after deploy)

1. `/gear ut` lists 28 new usable rows (64 ids) with their zone bands; none says "unknown item" or "craftable".
2. `/gear ut give Armor_UT_OasisWarden_Chest 40`: orange name; flavor text starts `T6 Dusk - Untiered cloth armor.`; one orange trade-off line, green / red parts.
3. Wear the full Oasis Warden's set: max Health goes up, Mana regen visibly slower than without it (Stats page).
4. Scarak Stalker's set (row 2): hit a mob from behind, then from the front - the back hits are bigger (this tests back / front on armor).
5. Caldera Guard set (row 9): drop under half Health - damage taken goes up (compare one mob hit above / below half).
6. Fossil Seer's set (row 10): under half Health your hits get bigger.
7. Scarak Stinger: hits leave Poison ticking about 10 s; the hit itself is smaller than a Dusk kunai of the same level.
8. The Sandscript Codex vs the Ashfall Grimoire: cast the same spell - the Codex costs less Mana, the Grimoire costs more but hits harder.
9. Hotspring Blessing with a party member within 8 blocks: the heal orb heals them too. Change `utline.auraReach` to 2 in Server Setup and step away - no heal.
10. Raptorfang on a fresh mob (smaller hits) vs a mob under half Health (big hits); Bonewhistle the opposite.
11. Crushing Tail: big knockback on normal mobs; on a boss (or mini boss) the hits are clearly smaller.
12. Magma Lance / Stormvent / The Stormfossil: hit a line of 3 mobs - all three take the hit. Stormvent bolts past 20 blocks deal nothing.
13. The Azure Arc (Spellblade): one sweep hits several mobs; swings slow; Air damage numbers show.
14. Kill Zone 2 elites (Lv 35-43) until an orange bag drops; identify - it shows one of the Z2 rows (1-3, 14-16).
15. Try to list any new UT on the Bazaar / Auction House: refused. Direct trade to a second player: works.
16. Server Setup -> Gear -> Rarity: the new `utpow` / `utfx` entries are there and editable; Changes shows the migration line with Undo.

## Questions for Skyy

1. **Which 28 first:** 12 armor sets + 16 weapons (this sheet, the draft's rows-first order), or the draft's Question 6 list (28 weapons, no armor)?
   **Default: this sheet - every zone gets its 3 armor sets now; the rest of the weapons come with the class engine rounds.**
2. **Grammar changes:** A4 gets Speed instead of range, A6 drops knockback resist, A11 drops the dodge bonus, Sandscript Codex drops spell range,
   Stormfossil drops echo, Hotspring Blessing gets a party heal aura. OK? **Default: yes; add the dropped parts when their engine exists.**
3. **Glacier Bulwark vs Ghost Rook** (both: take less damage, move slower). Keep both, or change Glacier Bulwark's downside to Stamina only?
   **Default: keep both - different zones, and Ghost Rook is a Zone 1 Armory extra.**
4. **Elements on UT weapons** (draft Question 4): **Default: ship the single flat element line (+3 %), none on armor.**
5. **Which mobs feed which set** (draft Question 3): **Default: any elite / mini boss / dungeon of the zone, even weights.**
6. **Hepta Axe** (draft Question 1, not built here): **Default: keep it as the Berserker's Zone 4 UT (band 75-83).**

## For the local session (UNVERIFIED)

- Base items: zone cloth / light / heavy armor ids for Zones 2, 3, 5 (Z1 uses `Armor_Cloth_Cotton_` / `Armor_Leather_Medium_` / `Armor_Iron_`;
  Z4 cloth = `Armor_Cloth_Cindercloth_` per `research/UT-Lines-Draft.md` 3); the weapon base per family at the zone alloy (or Iron + recolour as in 0.2.16).
- Which mod builds each family's base today (longsword, spear, crossbow, axe, kunai, spellbook, fist wraps vs gauntlets) - decides owner A / B for rows 13, 15, 18, 19, 21.
- Which weapon types the UT bag can already hold (0.2.16 added `Weapon_Bo`); spellbook / kunai / fist / spear / crossbow / longsword / axe may be missing.
- `back`, `front`, `lowhp` and `taken` on worn ARMOR (the grammar says "held weapon + worn armor" - confirm in GearUt / the damage system).
- `pierce` on a spear and on crossbow bolts (today read by SkyyArmory for staff quick shots and wand taps only).
- `swing=fast` on fist weapons (speed tier families) and whether a fast tier is a real upside (tiers are same-DPS by design).
- The vanilla longsword sweep: does one swing already hit several targets (row 13's upside depends on it)?
- Whether SkyyClasses Momentum counts hits (then swing=slow builds it slower with no new code).
- Whether `p5_dps` should count `poison`; the GUESS shares for `tgtlow` / `tgtfull` / `boss` / `lowtaken` in utp_net.
- How the 10 live Z1 UTs are tier-tagged today (`SkyyArmory/build_skyyarmory_0.1.43.py` 6803-6813 lists the 3 Armory UTs as untagged) - the new rows carry tags; the old ones may need a follow-up.
- The UT level-up cap per rarity after the 0.3.36 +10 change (G1 had UT +3).
- Whether the Zone 1 final quest reward (SkyyQuests 0.4.3) picks the class UT row by itself (then row 13 needs no Quests change).
- Lang file path / key prefix for the copies (`server.items.<id>.name` via TranslationProperties, as in `SkyyGear/build_skyygear_0.3.40.py` 6150).
- Next free version numbers (SkyyGear 0.3.41, SkyyArmory 0.1.44) and the migration marker name.
- Record Skyy's 2026-10-23 naming answer in `docs/answered/gear.md` (`python tools/qa_append.py ...`); this sheet cites the popup only.
- ALL 28 item names are invented from zone lore and UNVERIFIED (Skyy may rename): Oasis Warden's, Scarak Stalker's, Red Dune Sentinel,
  Everfrost Wanderer's, Yeti Hunter's, Glacier Bulwark, Ghost Grove Mystic's, Geyser Runner's, Caldera Guard, Fossil Seer's, Raptorhide,
  Lava Lake Bastion, The Azure Arc, Sandscript Codex, Steppe Wind Wraps, Scarak Stinger, Hotspring Blessing, Magma Lance, Stormvent,
  Ashfall Grimoire, Emberroot Wraps, Raptorfang, Bonewhistle, Deepcave Shadow, Primal Cleaver, The Stormfossil, Cavewind, Crushing Tail.
  The zone / place words come from working-name docs (Story script, Outposts list) that may still change.
- `research/UT-Lines-Draft.md` section 3 names the Z4 cloth candidate "The Auditor's" (`Armor_UT_Auditor_*`, never built); this sheet replaces it
  with Ghost Grove Mystic's (`Armor_UT_GhostGroveMystic_*`), same numbers - that draft's id is not to be built.
- "Scarak", "Kweebec", "Trork" are vanilla Hytale faction words: using one in an item NAME is fine (no file copied), but confirm no vanilla
  item id or lang key already uses `ScarakStalker` / `ScarakStinger`.
- Elites exist at Lv 35-43 / 55-63 / 75-83 / 95-100 in the SkyyMobs 0.1.18 tables (else a band never drops).
