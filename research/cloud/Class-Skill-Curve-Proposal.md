# Class skill XP curve proposal

> **Skyy's decisions 2026-10-02 win over this draft:** OPEN-QUESTIONS.md, section "Q&A with Skyy 2026-10-02", rounds 1 (approved as written, class skills only).

Cloud draft, 2026-10-02. Nothing built or tested. Feeds the next big round (SkySkills flatter curve).
Skyy's goal (OPEN-QUESTIONS 2026-10-01): class skill **20 in a few hours of play, 40 in days, skills go to 100**.

## 1. Where we are today (read from `SkyySkills/build_skyyskills_0.4.11.py`, VERIFIED by reading)

| Fact | Value | Where |
|---|---|---|
| XP table | `LEVELS`: Hypixel table to 60, then +300,000 per level; same table for **every** skill | build script line ~1020 |
| Totals | skill 15 = 67,425; 20 = 522,425; 25 = 3,022,425; 40 = 25,522,425; 60 = 111,672,425; 100 = 637,672,425 | sums of `LEVELS` |
| Kill XP | NPC max health x `combat.perHealth` 0.2, clamped `combat.min` 1 .. `combat.max` 500, then x `classSkill.xpMultiplier` (3) | lines ~1051-1056, 0.4.10 notes |
| Existing knobs | `levels` (the list), `levels.max` (1-100), `levels.scale` (% of the default curve, 10-1000) in Server Setup, both `live,danger` | rows ~10376-10378 |
| Kill rates (Gear-Levels-Wynn-Spec) | about **45 XP** per Zone 1 kill and **105** per Zone 2 kill at x3 | spec section 0 |

Problem: one table for all skills. Class skills only get kills, so 20 = 522k XP = about 5,000 Zone 2 kills.

## 2. The proposal

**One new, separate table for class skills only** (gathering, Alchemy, Smithing, Cooking, Exploration keep the Hypixel table).

`XP to go from level L-1 to L  =  round( 50 x L  +  0.25 x L^3 )`, rounded to a "nice" step (10 below 1,000; 50 below 10,000; 500 below 100,000; 5,000 above).

| Level | Needs | Total | Old total |
|---|---|---|---|
| 10 | 750 | 3,510 | 9,925 |
| 20 | 3,000 | 21,540 | 522,425 |
| 30 | 8,250 | 77,290 | 8,022,425 |
| 40 | 18,000 | 209,090 | 25,522,425 |
| 60 | 57,000 | 929,090 | 111,672,425 |
| 100 | 255,000 | 6,627,590 | 637,672,425 |

(Per-level numbers for the build are in section 5.)

Why this shape: it starts close to the old table (level 1 needs 50, same as today), is polynomial (smooth, no jumps), and
grows to 255,000 for level 100 (old: 19,000,000). The cube term makes 40 to 100 a real endgame instead of a wall.

### Pacing check (assumptions are mine - **UNVERIFIED**, playtest to confirm)

Assumed 120 kills an hour (one every 30 seconds), x3 multiplier, today's kill XP. Base kill XP per zone (before x3):
Zone 1 = 15, Zone 2 = 35, Zone 3 = 42, Zone 4 = 100 (from Mob-Levels-Plan section 7 ranges). Hours are cumulative, fighting the zone whose band
contains the level you are earning (Z1 1-20, Z2 21-30, Z3 31-45, Z4 46-60, Z4 rates after 60).

| Goal | Today's kill XP | With SkyyMobs level bonus (+4% health per mob level) |
|---|---|---|
| Skill 10 | 0.6 hours | 0.5 hours |
| Skill 20 | about 4 hours | about 3 hours |
| Skill 30 | about 8 hours | about 5 hours |
| Skill 40 | about 17 hours (a few days at 4-5 hours a day) | about 9 hours |
| Skill 45 | about 24 hours | about 12 hours |
| Skill 60 | about 41 hours | about 17 hours |
| Skill 100 | about 200 hours | about 69 hours |

This fits "20 in a few hours, 40 in days". Skill 100 stays a long project. If Skyy wants it quicker or slower,
change **one number**: the `0.25` cube term (0.20 gives skill 40 in about 15 h, 0.30 in about 20 h) - all three options keep every level cheaper than today.

## 3. Existing XP (levels only go up)

- The new cumulative table is **at or below the old one at every level 1-100** (checked by script). So recomputing the level from the stored
  total XP can only raise it - levels only go up, no special case. A quick guard in the build ("level = max(stored level, new level)") is still cheap insurance.
- Stored data: SkySkills saves total XP per slot, so no data rewrite is needed - the level is derived. Mark as UNVERIFIED for the local session (check `SkillStore`).
- Players keep a lot of "new" progress: someone at old level 15 (67k XP) lands at about new level 28.
- Level-up rewards (max health per level, class damage per level) are per level, so those players jump up in power. Give a one-time chat line
  ("class skill curve updated, your level is now N"). Existing one-time-migration rule applies (PROJECT-RULES section 4): only rewrite a
  `levels` line still holding the old default; a hand-edited list is kept and logged; History snapshot, marker, keep line endings.

## 4. Server Setup rows (Skills tab, Levels group)

| Row key | Name | Type | Default | Notes |
|---|---|---|---|---|
| `levels.class` | Class skill XP table | list (100 numbers) | the table in section 5 | same `custom:` list editor as `levels` |
| `levels.class.scale` | Class level curve size | int % | 100 | like `levels.scale` |
| `levels.class.max` | Class max level | int | 100 | 1-100 |
| `levels.class.sameAsOthers` | Class skills use the normal table | switch | off | escape hatch back to today's behaviour |

Danger prompts as for the existing `levels` rows (curves ask for a confirm - PROJECT-RULES / OPEN-QUESTIONS 297).

## 5. Per-level table (levels 1-100)

Columns: XP for that level, total, old total, then **minutes to earn that one level** fighting at each zone's
kill rate (120 kills an hour, x3, today's kill XP), then cumulative hours following the zone path (today's XP / with SkyyMobs level bonus).

| L | XP for level | Total | Old total | Min at Z1 | Min at Z2 | Min at Z3 | Min at Z4 | Hours (today) | Hours (+Mobs) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 50 | 50 | 50 | 0.6 | 0.2 | 0.2 | 0.1 | 0.0 | 0.0 |
| 2 | 100 | 150 | 175 | 1 | 0.5 | 0.4 | 0.2 | 0.0 | 0.0 |
| 3 | 160 | 310 | 375 | 2 | 0.8 | 0.6 | 0.3 | 0.1 | 0.0 |
| 4 | 220 | 530 | 675 | 2 | 1 | 0.9 | 0.4 | 0.1 | 0.1 |
| 5 | 280 | 810 | 1,175 | 3 | 1 | 1 | 0.5 | 0.1 | 0.1 |
| 6 | 350 | 1,160 | 1,925 | 4 | 2 | 1 | 0.6 | 0.2 | 0.2 |
| 7 | 440 | 1,600 | 2,925 | 5 | 2 | 2 | 0.7 | 0.3 | 0.2 |
| 8 | 530 | 2,130 | 4,425 | 6 | 3 | 2 | 0.9 | 0.4 | 0.3 |
| 9 | 630 | 2,760 | 6,425 | 7 | 3 | 2 | 1 | 0.5 | 0.4 |
| 10 | 750 | 3,510 | 9,925 | 8 | 4 | 3 | 1 | 0.6 | 0.5 |
| 11 | 880 | 4,390 | 14,925 | 10 | 4 | 3 | 1 | 0.8 | 0.6 |
| 12 | 1,050 | 5,440 | 22,425 | 12 | 5 | 4 | 2 | 1.0 | 0.7 |
| 13 | 1,200 | 6,640 | 32,425 | 13 | 6 | 5 | 2 | 1.2 | 0.9 |
| 14 | 1,400 | 8,040 | 47,425 | 16 | 7 | 6 | 2 | 1.5 | 1.1 |
| 15 | 1,600 | 9,640 | 67,425 | 18 | 8 | 6 | 3 | 1.8 | 1.3 |
| 16 | 1,800 | 11,440 | 97,425 | 20 | 9 | 7 | 3 | 2.1 | 1.6 |
| 17 | 2,100 | 13,540 | 147,425 | 23 | 10 | 8 | 4 | 2.5 | 1.8 |
| 18 | 2,350 | 15,890 | 222,425 | 26 | 11 | 9 | 4 | 2.9 | 2.2 |
| 19 | 2,650 | 18,540 | 322,425 | 29 | 13 | 11 | 4 | 3.4 | 2.5 |
| 20 | 3,000 | 21,540 | 522,425 | 33 | 14 | 12 | 5 | 4.0 | 2.9 |
| 21 | 3,350 | 24,890 | 822,425 | 37 | 16 | 13 | 6 | 4.3 | 3.1 |
| 22 | 3,750 | 28,640 | 1,222,425 | 42 | 18 | 15 | 6 | 4.6 | 3.2 |
| 23 | 4,200 | 32,840 | 1,722,425 | 47 | 20 | 17 | 7 | 4.9 | 3.4 |
| 24 | 4,650 | 37,490 | 2,322,425 | 52 | 22 | 18 | 8 | 5.3 | 3.6 |
| 25 | 5,150 | 42,640 | 3,022,425 | 57 | 25 | 20 | 9 | 5.7 | 3.8 |
| 26 | 5,700 | 48,340 | 3,822,425 | 63 | 27 | 23 | 10 | 6.1 | 4.0 |
| 27 | 6,250 | 54,590 | 4,722,425 | 69 | 30 | 25 | 10 | 6.6 | 4.3 |
| 28 | 6,900 | 61,490 | 5,722,425 | 77 | 33 | 27 | 12 | 7.2 | 4.6 |
| 29 | 7,550 | 69,040 | 6,822,425 | 84 | 36 | 30 | 13 | 7.8 | 4.9 |
| 30 | 8,250 | 77,290 | 8,022,425 | 92 | 39 | 33 | 14 | 8.4 | 5.2 |
| 31 | 9,000 | 86,290 | 9,322,425 | 100 | 43 | 36 | 15 | 9.0 | 5.4 |
| 32 | 9,800 | 96,090 | 10,722,425 | 109 | 47 | 39 | 16 | 9.7 | 5.7 |
| 33 | 10,500 | 106,590 | 12,222,425 | 117 | 50 | 42 | 18 | 10.4 | 6.0 |
| 34 | 11,500 | 118,090 | 13,822,425 | 128 | 55 | 46 | 19 | 11.1 | 6.3 |
| 35 | 12,500 | 130,590 | 15,522,425 | 139 | 60 | 50 | 21 | 11.9 | 6.6 |
| 36 | 13,500 | 144,090 | 17,322,425 | 150 | 64 | 54 | 22 | 12.8 | 7.0 |
| 37 | 14,500 | 158,590 | 19,222,425 | 161 | 69 | 58 | 24 | 13.8 | 7.4 |
| 38 | 15,500 | 174,090 | 21,222,425 | 172 | 74 | 62 | 26 | 14.8 | 7.8 |
| 39 | 17,000 | 191,090 | 23,322,425 | 189 | 81 | 67 | 28 | 15.9 | 8.3 |
| 40 | 18,000 | 209,090 | 25,522,425 | 200 | 86 | 71 | 30 | 17.1 | 8.8 |
| 41 | 19,500 | 228,590 | 27,822,425 | 217 | 93 | 77 | 32 | 18.4 | 9.3 |
| 42 | 20,500 | 249,090 | 30,222,425 | 228 | 98 | 81 | 34 | 19.8 | 9.8 |
| 43 | 22,000 | 271,090 | 32,722,425 | 244 | 105 | 87 | 37 | 21.2 | 10.4 |
| 44 | 23,500 | 294,590 | 35,322,425 | 261 | 112 | 93 | 39 | 22.8 | 11.1 |
| 45 | 25,000 | 319,590 | 38,072,425 | 278 | 119 | 99 | 42 | 24.4 | 11.8 |
| 46 | 26,500 | 346,090 | 40,972,425 | 294 | 126 | 105 | 44 | 25.2 | 12.0 |
| 47 | 28,500 | 374,590 | 44,072,425 | 317 | 136 | 113 | 48 | 26.0 | 12.3 |
| 48 | 30,000 | 404,590 | 47,472,425 | 333 | 143 | 119 | 50 | 26.8 | 12.5 |
| 49 | 32,000 | 436,590 | 51,172,425 | 356 | 152 | 127 | 53 | 27.7 | 12.8 |
| 50 | 34,000 | 470,590 | 55,172,425 | 378 | 162 | 135 | 57 | 28.6 | 13.1 |
| 51 | 35,500 | 506,090 | 59,472,425 | 394 | 169 | 141 | 59 | 29.6 | 13.5 |
| 52 | 38,000 | 544,090 | 64,072,425 | 422 | 181 | 151 | 63 | 30.7 | 13.8 |
| 53 | 40,000 | 584,090 | 68,972,425 | 444 | 190 | 159 | 67 | 31.8 | 14.2 |
| 54 | 42,000 | 626,090 | 74,172,425 | 467 | 200 | 167 | 70 | 33.0 | 14.6 |
| 55 | 44,500 | 670,590 | 79,672,425 | 494 | 212 | 177 | 74 | 34.2 | 15.0 |
| 56 | 46,500 | 717,090 | 85,472,425 | 517 | 221 | 185 | 78 | 35.5 | 15.4 |
| 57 | 49,000 | 766,090 | 91,572,425 | 544 | 233 | 194 | 82 | 36.8 | 15.8 |
| 58 | 51,500 | 817,590 | 97,972,425 | 572 | 245 | 204 | 86 | 38.3 | 16.3 |
| 59 | 54,500 | 872,090 | 104,672,425 | 606 | 260 | 216 | 91 | 39.8 | 16.8 |
| 60 | 57,000 | 929,090 | 111,672,425 | 633 | 271 | 226 | 95 | 41.4 | 17.3 |
| 61 | 60,000 | 989,090 | 118,972,425 | 667 | 286 | 238 | 100 | 43.0 | 17.9 |
| 62 | 62,500 | 1,051,590 | 126,572,425 | 694 | 298 | 248 | 104 | 44.8 | 18.4 |
| 63 | 65,500 | 1,117,090 | 134,472,425 | 728 | 312 | 260 | 109 | 46.6 | 19.0 |
| 64 | 68,500 | 1,185,590 | 142,672,425 | 761 | 326 | 272 | 114 | 48.5 | 19.7 |
| 65 | 72,000 | 1,257,590 | 151,172,425 | 800 | 343 | 286 | 120 | 50.5 | 20.3 |
| 66 | 75,000 | 1,332,590 | 159,972,425 | 833 | 357 | 298 | 125 | 52.6 | 21.0 |
| 67 | 78,500 | 1,411,090 | 169,072,425 | 872 | 374 | 312 | 131 | 54.8 | 21.7 |
| 68 | 82,000 | 1,493,090 | 178,472,425 | 911 | 390 | 325 | 137 | 57.0 | 22.5 |
| 69 | 85,500 | 1,578,590 | 188,172,425 | 950 | 407 | 339 | 142 | 59.4 | 23.3 |
| 70 | 89,000 | 1,667,590 | 198,172,425 | 989 | 424 | 353 | 148 | 61.9 | 24.1 |
| 71 | 93,000 | 1,760,590 | 208,472,425 | 1033 | 443 | 369 | 155 | 64.5 | 24.9 |
| 72 | 97,000 | 1,857,590 | 219,072,425 | 1078 | 462 | 385 | 162 | 67.2 | 25.8 |
| 73 | 100,000 | 1,957,590 | 229,972,425 | 1111 | 476 | 397 | 167 | 69.9 | 26.7 |
| 74 | 105,000 | 2,062,590 | 241,172,425 | 1167 | 500 | 417 | 175 | 72.9 | 27.7 |
| 75 | 110,000 | 2,172,590 | 252,672,425 | 1222 | 524 | 437 | 183 | 75.9 | 28.7 |
| 76 | 115,000 | 2,287,590 | 264,472,425 | 1278 | 548 | 456 | 192 | 79.1 | 29.7 |
| 77 | 120,000 | 2,407,590 | 276,572,425 | 1333 | 571 | 476 | 200 | 82.4 | 30.8 |
| 78 | 125,000 | 2,532,590 | 288,972,425 | 1389 | 595 | 496 | 208 | 85.9 | 32.0 |
| 79 | 125,000 | 2,657,590 | 301,672,425 | 1389 | 595 | 496 | 208 | 89.4 | 33.1 |
| 80 | 130,000 | 2,787,590 | 314,672,425 | 1444 | 619 | 516 | 217 | 93.0 | 34.3 |
| 81 | 135,000 | 2,922,590 | 327,972,425 | 1500 | 643 | 536 | 225 | 96.7 | 35.5 |
| 82 | 140,000 | 3,062,590 | 341,572,425 | 1556 | 667 | 556 | 233 | 100.6 | 36.8 |
| 83 | 145,000 | 3,207,590 | 355,472,425 | 1611 | 690 | 575 | 242 | 104.7 | 38.1 |
| 84 | 150,000 | 3,357,590 | 369,672,425 | 1667 | 714 | 595 | 250 | 108.8 | 39.5 |
| 85 | 160,000 | 3,517,590 | 384,172,425 | 1778 | 762 | 635 | 267 | 113.3 | 41.0 |
| 86 | 165,000 | 3,682,590 | 398,972,425 | 1833 | 786 | 655 | 275 | 117.9 | 42.5 |
| 87 | 170,000 | 3,852,590 | 414,072,425 | 1889 | 810 | 675 | 283 | 122.6 | 44.0 |
| 88 | 175,000 | 4,027,590 | 429,472,425 | 1944 | 833 | 694 | 292 | 127.4 | 45.6 |
| 89 | 180,000 | 4,207,590 | 445,172,425 | 2000 | 857 | 714 | 300 | 132.4 | 47.3 |
| 90 | 185,000 | 4,392,590 | 461,172,425 | 2056 | 881 | 734 | 308 | 137.6 | 49.0 |
| 91 | 195,000 | 4,587,590 | 477,472,425 | 2167 | 929 | 774 | 325 | 143.0 | 50.8 |
| 92 | 200,000 | 4,787,590 | 494,072,425 | 2222 | 952 | 794 | 333 | 148.5 | 52.6 |
| 93 | 205,000 | 4,992,590 | 510,972,425 | 2278 | 976 | 813 | 342 | 154.2 | 54.5 |
| 94 | 210,000 | 5,202,590 | 528,172,425 | 2333 | 1000 | 833 | 350 | 160.1 | 56.4 |
| 95 | 220,000 | 5,422,590 | 545,672,425 | 2444 | 1048 | 873 | 367 | 166.2 | 58.4 |
| 96 | 225,000 | 5,647,590 | 563,472,425 | 2500 | 1071 | 893 | 375 | 172.4 | 60.4 |
| 97 | 235,000 | 5,882,590 | 581,572,425 | 2611 | 1119 | 933 | 392 | 179.0 | 62.6 |
| 98 | 240,000 | 6,122,590 | 599,972,425 | 2667 | 1143 | 952 | 400 | 185.6 | 64.8 |
| 99 | 250,000 | 6,372,590 | 618,672,425 | 2778 | 1190 | 992 | 417 | 192.6 | 67.1 |
| 100 | 255,000 | 6,627,590 | 637,672,425 | 2833 | 1214 | 1012 | 425 | 199.7 | 69.4 |

## 6. For the local session (UNVERIFIED - needs the game / jar)

| # | Check |
|---|---|
| 1 | How `SkillStore` / `SkillXp.gain4` store XP (total vs level) and whether a per-slot table can replace the one global `SkillDefs.PER/CUM` (those are single static arrays - the build needs per-slot tables, or a `levelOf(slot, total)`). |
| 2 | Real kills an hour and real kill XP in Zone 1 and 2 - my 120 an hour is a guess. Ask Skyy for a timed 10-minute kill run. |
| 3 | Whether anything else reads `SkillDefs.CUM` (HUD bar, SkyyGuilds sum of skills, bridge `skill:fn:xp`) and needs the slot. |
| 4 | Overall Level (average of skill levels) will rise for classes - check the Overall spec numbers (0.5 health per level) are still fine. |
| 5 | Interaction with `combat.levelBonus` idea in Mob-Levels-Plan section 7: with this curve it is not needed. Recommend dropping it. |

## 7. Questions for Skyy

1. Is 4 hours to class skill 20 and about 17 hours to 40 the right feel? (Recommended: yes. Change the 0.25 term if not.)
2. Should the other skills (Mining, Foraging, Farming ...) also get a flatter curve later? Today only class skills were mentioned.
