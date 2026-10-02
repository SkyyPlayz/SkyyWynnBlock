# Mob level plan - refit to the new zone bands

> **Skyy's decisions 2026-10-02 win over this draft:** OPEN-QUESTIONS.md, section "Q&A with Skyy 2026-10-02", rounds 5.

Cloud draft, 2026-10-02. Nothing built. Source: `research/Mob-Levels-Plan.md` (read only), OPEN-QUESTIONS LOCKED 2026-10-01 (zone bands),
`research/SkyyWorldGen-Plan.md` 4.5 (ring ladder). All numbers below were computed by script from the plan's own RR formula, then
checked by hand against the old tables (the old tables reproduce exactly with the old formula).

## 1. The change in one table

| Zone | Old band | **New band** | Guardian | Gear you leave with |
|---|---|---|---|---|
| 1 Emerald Wilds | 1-10 | **1-20** | 20 | Wood -> Copper (armor from 1) -> first Iron 15-23 |
| 2 Howling Sands | 15-25 | **20-30** | 30 | Iron -> Thorium 20-28 -> first Cobalt 25-38 |
| 3 Whisperfrost Frontiers | 30-40 | **30-45** | 45 | Cobalt -> Adamantite 35-43 -> Mithril / Onyxium 40-49 |
| 4 Devastated Lands | 45-60 | **45-60 (no change)** | 60 | Mithril to 49, then our own tiers 50+ (later) |

Big structural change: **the gaps are gone.** The old plan had 4-level gaps (11-14, 26-29, 41-44) holding encounters, dungeons and
elites. The new bands touch (20 | 20, 30 | 30, 45 | 45), so those gaps no longer exist. See 5 for what replaces them.

## 2. Formulas (section 3 and 4.2-4.5 of the plan)

| Zone | Old low-level formula | **New** | Why |
|---|---|---|---|
| 1 | 1 + round((RR-1) x 7 / 9) | **1 + round((RR-1) x 17 / 9)** | top 20 (span 20-2-1 = 17) |
| 2 | 15 + round((RR-2) x 8 / 7) | **20 + round((RR-2) x 8 / 7)** | same span, floor +5: every row +5 |
| 3 | 30 + round((RR-2) x 8 / 7) | **30 + round((RR-2) x 13 / 7)** | top 45 (span 45-2-30 = 13) |
| 4 | 45 + round((RR-2) x 13 / 5) | unchanged | already 45-60 |

High end = low + 2 in every zone. Rounding is "half rounds up".

## 3. New biome tables (replace 4.2 - 4.5; RR values are unchanged)

### Zone 1 (was 1-10, now 1-20)

| Biome(s) | RR | Old | **New** |
|---|---|---|---|
| Zone1_Spawn: Plains_Spawn | 0 | 1-2 | **1-3** (fixed start area; my proposal, keeps a 3-level first zone) |
| Tier1: Plains_Smooth | 1 | 1-3 | **1-3** |
| Tier1: Plains_Birch | 2 | 2-4 | **3-5** |
| Tier1: Forest_Birch, Forest_Flower; Mountain_Tier1 / `*_Trork` | 3 | 3-5 | **5-7** |
| Tier2: Plains_Gorge | 4 | 3-5 | **7-9** |
| Tier2: Plains_Tallgrass | 5 | 4-6 | **9-11** |
| Tier2: Forest_Aspen, Forest_Gully; Mountain_Tier2 / `*_Trork` | 6 | 5-7 | **10-12** |
| Tier3: Plains_Gorge | 7 | 6-8 | **12-14** |
| Tier3: Forest_Swamp; Mountain_Tier3 / `*_Trork` | 9 | 7-9 | **16-18** |
| Tier3: Forest_Autumn, Forest_Moss, **Forest_Azure (blue forest)** | 10 | 8-10 | **18-20** |

Fallback rows: `Zone1_Tier1.*` **1-7** (was 1-5), `Zone1_Tier2.*` **7-12** (was 3-7), `Zone1_Tier3.*` **12-20** (was 6-10).

### Zone 2 (was 15-25, now 20-30)

| Biome(s) | RR | Old | **New** |
|---|---|---|---|
| Savannah_Forest / Plains / Boab / Rock, Savannah_Mudflats | 2 | 15-17 | **20-22** |
| `Plateau_*` (savanna env) | 3 | 16-18 | **21-23** |
| Scrub_Bushland | 4 | 17-19 | **22-24** |
| Desert_Oasis / Rock / Springs, Desert_Red, desert overlays | 6 | 20-22 | **25-27** |
| Desert_Barren, Desert_Mushroom | 8 | 22-24 | **27-29** |
| Desolate Basin overlays | 9 | 23-25 | **28-30** |

Fallbacks: `Zone2_Tier1.*` **20-24**, `Zone2_Tier2.*` **25-27**, `Zone2_Tier3.*` **27-30** (were 15-19 / 20-22 / 22-25).

### Zone 3 (was 30-40, now 30-45)

| Biome(s) | RR | Old | **New** |
|---|---|---|---|
| Forest_Redwood, Plains_Shire | 2 | 30-32 | **30-32** |
| Forest_Fir, Forest_Tundra, Plains_Hotsprings | 3 | 31-33 | **32-34** |
| Forest_Cedar | 5 | 33-35 | **36-38** |
| Plains_Frozen, Forest_Cedar_Mixed, Plains_Tundra | 6 | 35-37 | **37-39** |
| Forest_Frozen, Forest_Frozen_Light, Plains_Frozen_Frost | 8 | 37-39 | **41-43** |
| Overlays by region tier (mountains etc.) | T1 3 / T2 6 / T3 9 | 31-33 / 35-37 / 38-40 | **32-34 / 37-39 / 43-45** |

Fallbacks: `Zone3_Tier1.*` **30-34**, `Zone3_Tier2.*` **36-39**, `Zone3_Tier3.*` **41-45**. Outlander villages and undead encounter patches
still add their Bonus (+2) on top.

### Zone 4: no change (all of 4.5 stays: 45-47, 48-50, 53-55, 55-57, 58-60)

## 4. Other tables and numbers that change

### 4.1 Zone band table (plan 4.1) and the short version (section 0)

New text for section 0 "Bands" and table 4.1: Zone 1 1-20, Zone 2 20-30, Zone 3 30-45, Zone 4 45-60. Region bands inside each zone:

| Zone | Region bands (old -> new) |
|---|---|
| 1 | Spawn 1-2 -> 1-3; Drifting Plains 1-5 -> 1-7; Seedling Woods 3-7 -> 7-12; The Fens 6-10 -> 12-20 |
| 2 | Golden Steppes 15-19 -> 20-24; Badlands 20-22 -> 25-27; Desolate Basin 22-25 -> 27-30 |
| 3 | Frostmarch Tundra 30-33 -> 30-34; Boreal Reach 33-37 -> 36-39; The Everfrost 37-40 -> 41-45 |
| 4 | unchanged |
| Deep oceans | 5-10 -> **proposal: 5-20** (few hostile mobs; keep Skyy's call, Question 2 below) |

The "Vanilla ores / SkyyGear level there" column: Zone 1 = copper AND iron, Zone 2 = thorium, cobalt starts at its end, Zone 3 = cobalt,
adamantite, Mithril / Onyxium, Zone 4 = our own tiers later.

### 4.2 Environment table 4.6 (`bands.env`)

Method: Zone 1 = old edges stretched (x -> round(1 + (x-1) x 19/9)); Zone 2 = +5; Zone 3 = old edges stretched
(x -> 30 + round((x-30) x 1.5)); Zone 4 unchanged. Bonus column unchanged. The start-area environments stay low on purpose.

| Zone | Environment | Old | **New** | Bonus |
|---|---|---|---|---|
| 1 | Env_Zone1_Plains, _Shores, _Kweebec | 1-3 | **1-3** (kept: start area) | 0 |
| 1 | Env_Zone1_Forests | 3-5 | **5-9** | 0 |
| 1 | Env_Zone1_Mountains | 3-7 | **5-14** | 0 |
| 1 | Env_Zone1_Trork | 3-8 | **5-16** | 0 |
| 1 | Env_Zone1_Swamps | 7-10 | **14-20** | 0 |
| 1 | Env_Zone1_Autumn, Env_Zone1_Azure | 8-10 | **16-20** | 0 |
| 1 | Env_Zone1_Caves* | 3-7 | **5-14** | 0 |
| 1 | Env_Zone1_Caves_Volcanic_T1 / T2 / T3 | 3-5 / 5-7 / 7-9 | **5-9 / 9-14 / 14-18** | 0 |
| 1 | Env_Zone1_Caves_Goblins, _Mineshafts | 3-8 | **5-16** | +1 |
| 1 | Env_Zone1_Encounters, _Graveyard, _Mage_Towers | 5-9 | **9-18** | +2 |
| 1 | Env_Zone1_Dungeons | 7-10 | **14-20** | +2 |
| 2 | Env_Zone2_Savanna, _Shores | 15-17 | **20-22** | 0 |
| 2 | Env_Zone2_Scrub | 17-19 | **22-24** | 0 |
| 2 | Env_Zone2_Plateaus | 16-22 | **21-27** | 0 |
| 2 | Env_Zone2_Deserts | 20-24 | **25-29** | 0 |
| 2 | Env_Zone2_Oasis | 20-25 | **25-30** | 0 |
| 2 | Env_Zone2_Feran, _Scarak | 18-23 | **23-28** | +1 |
| 2 | Env_Zone2_Caves* (volcanic T1 / T2 / T3: 16-18 / 20-22 / 23-25) | 16-22 | **21-27** (21-23 / 25-27 / 28-30) | 0 |
| 2 | Env_Zone2_Mineshafts, _Caves_Goblins | 18-22 | **23-27** | +1 |
| 2 | Env_Zone2_Encounters, _Mage_Towers | 20-24 | **25-29** | +2 |
| 2 | Env_Zone2_Dungeons | 22-25 | **27-30** | +2 |
| 3 | Env_Zone3_Tundra | 30-33 | **30-35** | 0 |
| 3 | Env_Zone3_Shores | 30-32 | **30-33** | 0 |
| 3 | Env_Zone3_Forests | 30-35 | **30-38** | 0 |
| 3 | Env_Zone3_Mountains | 33-37 | **35-41** | 0 |
| 3 | Env_Zone3_Glacial | 35-40 | **38-45** | 0 |
| 3 | Env_Zone3_Caves* | 31-37 | **32-41** | 0 |
| 3 | Env_Zone3_Trork | 33-38 | **35-42** | +1 |
| 3 | Env_Zone3_Outlander*, _Encounters | 36-40 | **39-45** | +2 |
| 4, 0.7 portals | all rows | | **unchanged** | |

`bands.zone` fallback: Zone1 **1-7** (was 1-5), Zone2 **20-24** (was 15-19), Zone3 **30-34** (was 30-33), Zone4 45-50, Oceans see 4.1.
`bands.default` 1-3 and `bands.islands` 1-3 stay.

### 4.3 Per-level scaling (section 5) - formulas stay, examples change

Health +4% and damage +2% per level, caps x4 / x2.5: unchanged. Because Zone 1 now reaches Lv 20 the Zone 1 top is stronger.

| Level | Health x | Damage x | Bonus-drop chance (1% per level) |
|---|---|---|---|
| 20 | 1.76 | 1.38 | 19% |
| 30 | 2.16 | 1.58 | 29% |
| 45 | 2.76 | 1.88 | 44% |
| 60 | 3.36 | 2.18 | 50% (cap) |

Old plan examples to replace: "Lv 10 x1.36, Lv 15 x1.56, Lv 25 x1.96, Lv 40 x2.56" (still true as numbers, but Lv 10 is now mid-Zone 1;
use the table above in the text). Rarity shift example "Lv 30: Unique+ weights x1.58" is still correct.

Worked examples (base health x multiplier, XP = 0.2 x max health, before the x3 class multiplier):

| Mob | Where | Level | Health | XP (was) |
|---|---|---|---|---|
| Skeleton_Fighter (36) | Drifting Plains / blue forest | 1 / 20 | 36 / 63 | 7 / 13 (7 / 10) |
| Bear_Grizzly (124) | Birch forest / blue forest | 6 / 20 | 149 / 218 | 30 / 44 (29 / 34) |
| Skeleton_Burnt_Praetorian (226) | blue forest | 20 | 398 | 80 (61) |
| Trork_Warrior (61) | Trork camp in The Fens | 17 | 100 | 20 (16) |
| Skeleton_Sand_Guard (61) / Hyena (103) | Golden Steppes | 21 | 110 / 185 | 22 / 37 (20 / 33) |
| Crocodile (145) | hidden oasis, Desolate Basin | 29 | 307 | 61 (56) |
| Skeleton_Frost_Knight (74) / Bear_Polar (103) | The Everfrost | 42 | 195 / 272 | 39 / 54 (37 / 51) |
| Emberwulf (193) / Rex_Cave (400) | Charred Woodlands | 58 | 633 / 1,312 | 127 / 262 (unchanged) |

The "zone step shows in same-kind mobs" sentence (Lv 10 skeleton 49 HP vs Lv 16 sand skeleton 98 HP) becomes: a Lv 20 skeleton (63 HP)
against a Lv 21 sand skeleton (110 HP) - the step is now the species (sand skeleton has more base health), not the level.

### 4.4 Nameplate colours (section 6)

| Old | **New (proposal)** | Colour |
|---|---|---|
| 1-14 | **1-19** | `#d6e4ee` row-name white |
| 15-29 | **20-29** | `#ffcc00` warning yellow |
| 30-44 | 30-44 | `#E8A93B` gold |
| 45-60 | 45-60 | `#ff6b6b` error red |
| 61+ and bosses | 61+ | `#CC66CC` Mythic |

### 4.5 Fit with gear and weapon skill (section 7)

| Zone | Mob levels | Gear you should reach | Skill at the end | Total XP, old Hypixel table | Total XP, proposed flat curve (Class-Skill-Curve-Proposal) |
|---|---|---|---|---|---|
| 1 | 1-20 | Crude -> Copper -> first Iron | 20 | 522,425 | 21,540 |
| 2 | 20-30 | Iron -> Thorium -> first Cobalt | 30 | 8,022,425 | 77,290 |
| 3 | 30-45 | Cobalt -> Adamantite -> Mithril | 45 | 38,072,425 | 319,590 |
| 4 | 45-60 | Mithril to 49, own tiers later | 60 | 111,672,425 | 929,090 |

The "Pacing problem" paragraph (skill 25 = +84,000 kills, skill 40 = +450,000 more) and its three options are **answered**: Skyy chose
"flatten" (OPEN-QUESTIONS 2026-10-01). Question 7 is closed; **drop the `combat.levelBonus` idea** (the level XP bonus) unless a playtest
shows the flat curve is too slow. Section 14 risk "Kill XP pacing" can be marked solved by the curve proposal.

### 4.6 Dungeons, elites, bosses (section 11)

| Item | Old | Proposal | Why |
|---|---|---|---|
| Dungeon bands (gap above the zone) | Z1 11-13, Z2 26-28, Z3 41-43 | **Z1 20-23, Z2 30-33, Z3 45-48** (zone top to top +3, using the +2 Bonus on top) | the gaps are gone; dungeons are the "one zone harder" content |
| Endgame capstone | 61-70 | 61-70 (unchanged) | Zone 4 unchanged |
| Elites | +3 levels | unchanged | Zone 1 elites reach 23, a Zone 4 elite 63 |
| Guardians (`scale.role`) | fixed at top of band | **20 / 30 / 45 / 60** | matches the LOCKED guardians |

### 4.7 Tests (section 13)

| Test | Old | New |
|---|---|---|
| 3 blue forest | mobs Lv 8-10, `/mobs` "Lv 8-10 (Zone 1 - The Fens - Forest Azure)" | **Lv 18-20**, "Lv 18-20 (...)" |
| 5 cave under the blue forest | Lv 8-10 | **Lv 18-20** |
| 6 kill a Lv 10 grizzly | about 34 XP (169 max HP x 0.2); 25 means no modifier | **Lv 20 grizzly: about 44 XP (218 HP x 0.2); 25 means no modifier** |
| 7 Lv 10 skeleton hit, damage x1.18 | | **Lv 20 skeleton: damage x1.38** |
| 2 Drifting Plains | Lv 1-3 | Lv 1-3 (unchanged) |

### 4.8 Self-critique #15 and Questions 1-2 (sections 15, 17)

- #15 ("every zone step is +5 levels: 1-10, 15-25, 30-40, 45-60") is superseded: zones now touch. Mark it as "replaced 2026-10-01".
- Question 1 answer = LOCKED bands above. Question 2 (blue forest 8-10 or strict rarity 7-9): now **18-20 (draft) or 17-19 strict**. Skyy's
  earlier answer "blue forest top of Zone 1" holds; no change needed.

## 5. Findings and open questions

| # | Finding | Who decides |
|---|---|---|
| 1 | **Gap levels no longer exist.** Zone borders now share a level (20, 30, 45). On a plate a Zone 1 summit mob (Lv 20) and a Zone 2 rim mob (Lv 20-22) look equal; the jump is the species and the environment, not the number. Is that what Skyy wants, or should Zone 2 start at 21? | Skyy |
| 2 | Deep-ocean mobs 5-10 look too low next to a Lv 1-20 Zone 1. Proposed 5-20 (few mobs anyway). | Skyy |
| 3 | SkyyWorldGen-Plan table 4.4 gives the Zone 4 guardian **61-63**, while its ladder 4.5 and the LOCKED line say guardian **60**. One of them is stale. | local session / Skyy |
| 4 | SkyyWorldGen rings (4.5) and the classic RR formula differ slightly: ring core of Zone 1 is 14-18, guardian 19-20; the classic top biome (RR 10) is 18-20. Both end at 20, so they agree where it matters. Zone 3 ring core 41-44 vs classic RR 9 = 43-45. | none, FYI |
| 5 | Zone 1 is now 20 levels wide with only 3 vanilla region tiers (about 7 levels each). Mobs of a Tier 1 plains patch run 1-7 (was 1-5). `bands.roleShift` (strong species + levels) may be worth turning on. | Skyy, later |
| 6 | Health at Lv 20 is x1.76 for Zone 1 summit mobs; early gear (copper armor Lv 1-18, Iron 15+) was balanced for Lv 10 max. Check the damage-taken side with SkyyGear numbers during the first playtest. | local session |

## 6. For the local session

| # | Item |
|---|---|
| 1 | All numbers here are paper maths from the plan's formulas. The RR values per biome are the plan's (their area shares are UNVERIFIED until `/mobs survey`). |
| 2 | Rebuild `bands.*` default rows from the tables in 3 and 4.2 when SkyyMobs is built. |
| 3 | Check that the Zone 2 and Zone 3 environment rows still make sense with vanilla spawn tiers (a Tier 3 plains patch inside Zone 1 is now Lv 12-14). |
