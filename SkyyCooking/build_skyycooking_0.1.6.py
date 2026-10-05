"""SkyyCooking 0.1.6 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.5.py by tools/cooking_0_1_6_patch.py
(0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py /
_0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.6.py            -> SkyyCooking/SkyyCooking-0.1.6.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

0.1.6 = INGREDIENT XP BY DIFFICULTY (Skyy 2026-10-05 LOCKED: "Flour should go way down. The less it takes to craft, and the earlier the
 items are to get, the less xp it should give you").
 - Until 0.1.5 an ingredient craft paid 15% of its own direct raw inputs x 950 (Flour 1,425 - more than a Vegetable Skewer's 1,050). Now an
   ingredient pays its own direct raw inputs x 950 x a small DIFFICULTY SHARE (per mille):
     15 + 15 per earlier crafting step in its chain + 5 per extra distinct input + 15 per ingredient tier above 1 (Milk T2)
   Base XP per craft, 0.1.5 -> 0.1.6 (the dish table is unchanged):
     Ingredient_Salt       140 ->   15   1 salt rock -> 5 salt
     Food_Fish_Raw         285 ->   30   1 fish
     Food_Cheese           430 ->   85   1 milk bucket (T2 livestock), 5 s
     Ingredient_Spices     855 ->  115   1 vegetable + 5 flowers
     Ingredient_Flour    1,425 ->  140   10 wheat (T1)
     Ingredient_Dough      640 ->  170   flour + 2 eggs + water (2nd step)
   Asserted at build time: flour 10-20% of a Vegetable Skewer; every ingredient below its 0.1.5 value and below the cheapest multi-step
   dish; a later step / tier pays more per raw item than flour; spamming any ingredient levels slower than any dish (gathering-limited
   XP/h); the meat-pie route stays in decision 2's 25-30 h window (the ingredient XP inside it shrinks, ~25.2 h -> ~27.6 h).
 - ONE-TIME UPDATE (new class CookIngMig; setup() runs CookMig -> CookXpMig -> CookTblMig -> CookIngMig -> CookCfg.load -> CfgPub.start):
   CookTblMig's reviewed code with the six ingredient keys: a one-line xp.<ingredient> entry holding exactly the 0.1.5 default text (e.g.
   1425) moves to the 0.1.6 value (value text only); a hand-set value / continued entry is KEPT and logged; a missing line stays missing.
   The three 0.1.5 help lines of the xp block (byte-exact) are replaced 1:1. History copy "before the 0.1.6 ingredient Cooking XP update"
   verified first (else WARN, untouched, retried next start); one Undo-able change-log line per changed entry (xp[Ingredient_Flour], 1425,
   140); runs once (marker XP_ING_MARK above the xp block's comment run). Dish lines, xpMultiplier, maxXpPerMinute are never touched.
 Bare-JVM harness: SkyyCooking/test_skyycooking_0.1.6.py.

0.1.5 (previous version, kept below for the record):

0.1.5 = COOKING XP BY CRAFT DIFFICULTY (Skyy 2026-10-04, docs/answered/skills.md LOCKED: "lower the skewers a bit. the easier to craft the
 less xp. the harder to craft the more.").
 - DEFAULT "XP per craft" TABLE (xp.<output> lines; Server Setup -> Cooking -> Cooking XP -> XP per craft). Until 0.1.4 a dish paid 85% of
   the raw gathering in its whole ingredient chain x 950 per item (x1.25 with recipe knowledge): one-step skewers with 4-5 raw items paid
   3,650-5,250. Now a dish pays chain raw x 950 x a DIFFICULTY SHARE:
     share = 20% + 15% per extra crafting step in the chain (distinct crafts: flour, dough, spices, salt, cheese, fish cleaning)
           + 25% recipe knowledge (pies, Caesar salad) + 0% Campfire dish / 5% Cooking Bench Prepared / 10% Cooking Bench Baked (fuel)
           + 5% per ingredient tier above 1 (Bazaar crop ladder 2026-10-04: Corn T2, Pumpkin T4; Apple T2, Milk T2; the rest T1)
   (the Cooking Bench has no tier levels, so "bench tier" = Campfire < Prepared < Baked). Shares: campfire dishes 20% (grilled fish 35%),
   skewers / berry + mushroom salad 25%, popcorn 50%, bread 60%, Caesar 100%, apple pie 105%, meat + pumpkin pie 115%. Ingredient crafts
   keep 15% of their own inputs (unchanged). Base XP per craft, 0.1.4 -> 0.1.5:
     Ingredient_Salt           140 ->    140   (ingredient, unchanged)
     Food_Fish_Raw             285 ->    285   (ingredient, unchanged)
     Food_Vegetable_Cooked   1,200 ->    300
     Food_Wildmeat_Cooked    1,600 ->    400
     Food_Cheese               430 ->    430   (ingredient, unchanged)
     Ingredient_Dough          640 ->    640   (ingredient, unchanged)
     Food_Fish_Grilled       2,000 ->    850
     Food_Kebab_Mushroom     2,850 ->    850   (stopgap 2026-10-04: 1,400)
     Ingredient_Spices         855 ->    855   (ingredient, unchanged)
     Food_Salad_Mushroom     3,250 ->    950
     Food_Kebab_Fruit        3,650 ->  1,050   (stopgap 2026-10-04: 1,800)
     Food_Kebab_Vegetable    3,650 ->  1,050   (stopgap 2026-10-04: 1,800)
     Food_Salad_Berry        4,850 ->  1,400
     Ingredient_Flour        1,425 ->  1,425   (ingredient, unchanged)
     Food_Kebab_Meat         5,250 ->  1,550   (stopgap 2026-10-04: 2,600)
     Food_Popcorn            3,000 ->  1,750
     Food_Bread             12,900 ->  9,100
     Food_Salad_Caesar      11,800 -> 11,100
     Food_Pie_Apple         25,250 -> 24,950
     Food_Pie_Pumpkin       23,200 -> 25,150
     Food_Pie_Meat          23,900 -> 25,900
   Meat-pie route (decision 2, base XP): ~25 focused hours to Cooking 50 (0.1.4: ~27), inside the 25-30 h window. maxXpPerMinute stays
   1,500,000 (pinned: 2x the new bench peak is 1.4M). The weights are the DIFF_* build constants; the in-game editable surface stays the
   per-dish rows (the table is not formula-driven at runtime). xpMultiplier default stays 0.5.
   Skewers per level at Cooking 10 / 11 / 12 (next level costs 5,000 / 7,500 / 10,000; before SkyySkills' own XP multiplier / Wisdom):
     xpMultiplier 0.5 (pack default): Vegetable / Fruit 9.5 / 14.3 / 19.0, Mushroom 11.8 / 17.6 / 23.5, Meat 6.5 / 9.7 / 12.9
     xpMultiplier 0.15 (live row 2026-10-04): Vegetable / Fruit 31.7 / 47.6 / 63.5, Mushroom 39.2 / 58.8 / 78.4, Meat 21.5 / 32.3 / 43.0
 - ONE-TIME UPDATE of an existing cooking.properties (new class CookTblMig; setup() runs CookMig.migrate -> CookXpMig.migrate ->
   CookTblMig.migrate -> CookCfg.load -> CfgPub.start): for every dish whose default changed, the key's LAST entry (what
   java.util.Properties keeps) decides: a one-line entry holding exactly the 0.1.4 default text (e.g. 3650) - or exactly a 2026-10-04
   stopgap value (Food_Kebab_Vegetable / _Fruit 1800, _Mushroom 1400, _Meat 2600) - moves to the 0.1.5 value (every one-line entry of
   that key holding one of those texts is rewritten, value text only: key, separator and CR stay); anything else (a hand-set value, a
   continued entry) is KEPT and logged ("xp.Food_Pie_Meat=30000 kept (custom) - the 0.1.5 default is 25900"); a missing line stays
   missing (the compiled 0.1.5 value applies). The three generated help comment lines above the xp block (byte-exact 0.1-0.1.4 text) are
   replaced 1:1 by the 0.1.5 wording; any other comment stays. CookMig's reviewed machinery (CookMig.kit / saved / logLine): History copy
   "before the 0.1.5 Cooking XP by difficulty update" verified before the rewrite (else WARN, file untouched, next start tries again);
   CfgRows.atomicWrite; one config-changes.log line PER CHANGED ENTRY in the kit's table form (time, SkyyCooking 0.1.5, -, update,
   xp[Food_Kebab_Vegetable], 3650, 1050, ok) so Server Setup -> Changes undoes each with a tset back; one INFO line (+ one per kept
   value). RUNS ONCE: the marker XP_TBL_MARK goes on its own line above the comment block directly on top of the first xp.* entry (no xp
   entry: above the file's first entry, else on top); a file with XP_TBL_MARK_ID in a comment line is never changed again (an Undo back to
   3650 survives restarts). The 0.1.5 default text carries the marker. xpMultiplier, maxXpPerMinute, xp.default and the ingredient lines
   are never touched.
 Nothing else changed (class compare in the harness): grading, rolls, Grades, effects, tooltips, campfire factors, bridge keys, commands,
 permissions, the other rows. The campfire accessory pays campfire.xpFactor x the NEW xp.<dish> value (Cooked Wildmeat 400 x 0.25 = 100).
 Bare-JVM harness: SkyyCooking/test_skyycooking_0.1.5.py.

0.1.4 (previous version, kept below for the record):

0.1.4 = FOOD GRADE STRENGTH +32% PER GRADE, DURATION UNCHANGED, TOOLTIP WORDING, COOKING XP HALVED (Skyy 2026-10-02 from testing,
 OPEN-QUESTIONS LOCKED: "cooking levels really fast" -> "id probably half the speed cooking levels at / your cooking xp gain"; food Grade
 strength "+32% per Grade" - "id leave the duration buff, its good"; "im lvl 15 cooking not 20 and i still got grade 2").
 - STRENGTH AND DURATION ARE SPLIT. Until 0.1.3 one multiplier M = 2^(Grade/5) drove both and was baked into the generated Grade 1-12
   assets. Now STRENGTH S(g) = 1 + 0.32 x g ("+32% per Grade") multiplies the heal %, the regen % per tick, the max-Health / max-Stamina
   bonus (the part above x1), the Stamina per tick and the damage resistance; DURATION D(g) = 2^(g/5) multiplies every buff's Duration
   exactly as before (instant 0.1 s heals keep theirs). SF(g) / DF(g) below; the 156 effect assets, the 108 family checks (re-ranked by
   (strength, duration): a weaker buff still never replaces a stronger one), the 180 dish tooltips and CookCfg.SF / DF follow them. The
   180 dish items themselves (ids, eat chains, Quality) are unchanged. No effect cap binds at any Grade any more (0.1.3 capped Grade 12
   max Stamina at x2.5).
     Grade          1     2     3     4     5     6     7     8     9    10    11    12
     strength    1.32  1.64  1.96  2.28  2.60  2.92  3.24  3.56  3.88  4.20  4.52  4.84   S = 1 + 0.32 x Grade (0.1.3: = duration)
     duration    1.15  1.32  1.52  1.74  2.00  2.30  2.64  3.03  3.48  4.00  4.59  5.28   D = 2^(Grade/5), unchanged
 - CAMPFIRE ACCESSORY: campfire.buffFactor (default 0.75) now works on the STRENGTH part. The dish comes out at the highest Grade c
   whose strength S(c) <= 1 + buffFactor x (S(G) - 1), G = the Cooking Bench Grade; with the linear strength curve that is exactly
   floor(buffFactor x G) ("75% of your Grade, rounded down", build-checked for several factors), and the dish has that Grade's duration
   (the duration gets no share of its own). CookCfg.MUL - what the compiled Cook.campGrade compares - now holds S(g); the method is
   unchanged. Bench Grade -> campfire Grade (0.75):
     G0->0  G1->0  G2->1  G3->2  G4->3  G5->3  G6->4  G7->5  G8->6  G9->6  G10->7  G11->8  G12->9
   (0.1.3: G5->4, G9->7, G10->8, G11->9, G12->10). Cooking 100: bench Grade 10 (x4.20 stronger, x4.00 longer) -> campfire Grade 7 (x3.24
   stronger, x2.64 longer); 0.1.3 gave Grade 8 (x3.03 / x3.03). campfire.xpFactor and every campfire rule are unchanged.
 - TEXTS (strength and duration shown separately everywhere). Dish tooltip head: "Grade 2 food - Cooking 20, or sooner with Cooking tree
   bonuses. Heal and buffs x1.64 stronger, buffs last x1.32 longer." (was "cooked at Cooking 20 or higher", which ignored the tree: Master
   Chef gives Grade 2 at Cooking 10-19, Gourmet / Signature Dish procs give more); Grades 11-12 keep "only a Cooking skill tree bonus
   reaches it". /cooking is now built by Cook.cookingLines(UUID) (CookingCmd only sends the lines, first one coloured as before): the
   "Next" line "Next: Grade 3 (x1.96 stronger and x1.52 longer) at Cooking 20." and the campfire line "... come out Grade 1 (x1.32
   stronger and x1.15 longer) ..." name both factors (Cook.sdShort); the Grade line keeps "heal and buffs x.. stronger, buffs last x..
   longer" (Cook.sd). The campfire chat hint is Cook.campText(g, c): "... Grade 3 (75% of your Grade 5 strength bonus - heal and buffs
   x1.96 stronger, buffs last x1.52 longer) ...". Skills Stats page (skill:stats:Cooking): "Next Grade - Grade 3 at Cooking 20 - x1.96
   stronger and x1.52 longer", "Campfire accessory - Grade 3 food x1.96 stronger and x1.52 longer - 25% of the XP" (was "Campfire
   accessory quick cook - Grade N food x<one number> - ..."; the shorter prefix makes room for the second number). The "Your food now
   comes out Grade N - heal and buffs x.. stronger, buffs last x.. longer" line (CookXpTask, byte-identical) reads the new tables.
 - COOKING XP x0.5: Server Setup -> Cooking -> Cooking XP -> "Cooking XP multiplier" (xpMultiplier) default 1 -> 0.5 = the row default,
   the loader fallback for a missing / unreadable line (CookCfg.DEF_XP_MULT), the running field's start value (CookCfg.XP_MULT) and the
   generated cooking.properties line (xpMultiplier=0.5 with the marker XP_MARK above its help comment); row help "Multiplies every
   Cooking XP award. Default 0.5 = half. SkyySkills' XP multiplier applies on top." It halves bench, cook:fn:out and Campfire accessory
   XP alike (applied after the per-minute cap, before SkyySkills' Wisdom), so the XP table, maxXpPerMinute and campfire.xpFactor stay.
 - ONE-TIME UPDATE of an existing cooking.properties (CookXpMig.migrate; setup() calls it right after CookMig.migrate and BEFORE
   CookCfg.load + CfgPub.start, so the loader and the kit's first read already see the new line): xpMultiplier -> 0.5 ONLY when that
   key's LAST entry (the one java.util.Properties keeps) is a one-line entry holding exactly an old default text: "1.0" (what every
   generated cooking.properties since 0.1 says - the live file) or "1" (the kit's canonical write of the old default, e.g. Server Setup's
   Default button); then every one-line entry of the key holding one of them gets 0.5. Anything else is KEPT: a 0.5 Skyy sets in Server
   Setup before this ships ("already 0.5"), any other hand-set value (0.7, 1.00, 2, ...) or a continued entry (logged once at INFO:
   "xpMultiplier=0.7 kept (custom) - the 0.1.4 default is 0.5"); a missing line stays missing (the fallback 0.5 applies). CookMig's
   reviewed machinery, method for method (it calls CookMig.kit / saved / logLine): the kit's own parser (a continued line is never
   rewritten), only the value text of a changed line is replaced (key, separator and CR stay), every other byte is kept (ISO-8859-1 in
   and out, LF / CRLF per line as found); CfgHist.snapshot keeps the file as it was as a History version ("before the 0.1.4 Cooking XP
   update") and CookMig.saved checks config-history REALLY holds those bytes before anything is rewritten (else WARN, file untouched,
   the next start tries again); CfgRows.atomicWrite writes it; one config-changes.log line (time, "SkyyCooking 0.1.4", -, update,
   xpMultiplier, 1.0, 0.5, ok) so Server Setup -> Changes can Undo it (a plain set back to 1.0 = the kit writes 1); one INFO line
   ("cooking.properties updated to the 0.1.4 Cooking XP default: xpMultiplier 1.0 -> 0.5 ..."). Any failure: WARN, the file stays as it
   was. RUNS ONCE: the marker comment XP_MARK goes on its own line right above the (first) xpMultiplier entry - above its help comment
   when a comment line sits directly on top (where the fresh file has it); no xpMultiplier line -> the same rule at the file's first
   entry (the top of a file without entries), so the marker still records the decision and a 1 an admin sets later is never touched. A
   file whose comment lines hold XP_MARK_ID is never changed again (an Undo back to 1 survives restarts). The 0.1.4 default text carries
   the marker, so a fresh file never updates. The 0.1.3 campfire update (CookMig, unchanged) still runs first for a file that missed it:
   a 0.1.2 file gets both (two History copies, two Undo-able lines). Second start = nothing written.
 Nothing else changed: bench grading and rolls, the XP table, caps, campfire.xpFactor, bridge keys and shapes (cook:fn:grade still returns
 the Integer Grade), commands, permissions, player switches and the other config rows (class compare in the harness: CookXpTask, CookSys,
 the bridge functions, CookHooks and the admin commands are byte-identical). Kit 1.1 classes rebuilt with the same tools/skyycfg.py.
 OTHER MODS (checked 2026-10-02): nothing else computes 2^(Grade/5) or prints a Grade multiplier - SkyySkills 0.4.12 / 0.4.13 show the
  Cooking Stats lines this mod sends (skill:stats:Cooking) plus "Food you cook gets stronger"; SkyyMenu 0.3.5 says "higher Grades heal and
  buff more"; SkyyTrees 0.2.5 node texts are Grade counts; SkyySacks 0.7.12's Campfire tab and SkyyAccessories 0.5.2 / 0.5.3's Campfire
  item text say "75% of your cooking bonus" (still right: the share of the Grade strength bonus) and read the live factors; SkyyHud
  0.3.11 / 0.3.12 show only the Cooking level; nobody calls cook:fn:grade. Their build checks read this script's CAMP_BUFF_DEF /
  CAMP_XP_DEF line, cook:fn:campfactors and the campfire / enabled rows - all unchanged.
 Bare-JVM harness: SkyyCooking/test_skyycooking_0.1.4.py (every graded asset against vanilla x S / x D, the family checks re-derived, the
  tooltips, the campfire pick through the compiled path, the texts, the update on scratch copies of the live file, start twice on a copy
  of the live data folder, random files vs java.util.Properties, class + asset compare with 0.1.3, -Xverify:all).
 TEST (0.1.4, Skyy, one account with op, after a deploy over the live 0.1.3 world):
  1. Server log: "[SkyyCooking] cooking.properties updated to the 0.1.4 Cooking XP default: xpMultiplier 1.0 -> 0.5 ..." then "[SkyyCooking]
     0.1.4 ready ... xpMultiplier 0.5 ..."; cooking.properties: xpMultiplier=0.5 with the 0.1.4 marker comment above its help line, every
     other line as before.
  2. /modconfig cooking -> Cooking XP -> Cooking XP multiplier = 0.5 (help "... Default 0.5 = half ..."); Changes lists "SkyyCooking 0.1.4
     ... xpMultiplier 1.0 -> 0.5" with Undo; History lists "before the 0.1.4 Cooking XP update".
  3. Cook a Vegetable Skewer batch at a Cooking Bench: the Cooking XP per skewer is half of before (Skyy saw ~3,760 per batch).
  4. /cooking (Cooking 15 with Master Chef): "your food comes out Grade 2: heal and buffs x1.64 stronger, buffs last x1.32 longer.",
     "Next: Grade 3 (x1.96 stronger and x1.52 longer) at Cooking 20.", campfire "Grade 1 (x1.32 stronger and x1.15 longer)".
  5. /cookadmin give pie_meat 2 -> tooltip "Grade 2 food - Cooking 20, or sooner with Cooking tree bonuses. Heal and buffs x1.64 stronger,
     buffs last x1.32 longer." then "Instantly restores 24.6% health", Health Regen III 3.3% health every 2 s, Health Boost III +24.6% max
     health and 8.2% less physical and projectile damage, Duration 7:55 (0.1.3 Grade 2: 19.8% / 2.6% / +19.8% / 6.6% / 7:55).
  6. /cookadmin give pie_meat 5 + eat it -> max health +39% (0.1.3: +30%), regen icon still 12:00.
  7. Cooking 50 (or /cookadmin campfire wildmeat_cooked 0 at bench Grade 5): "bench Grade 5 -> campfire Grade 3" (0.1.3: 4).
  8. Restart -> no update line, still 0.5. (Optional: Changes -> Undo -> 1 -> restart -> stays 1; set it back to 0.5.)

0.1.3 = CAMPFIRE XP HALVED (Skyy 2026-10-01, verbatim: "ive been cooking meat using the campfire in the /crafting. and im already cooking
 level 11. my highest level skill. id half the amount of cooking xp you get from the campfire."; OPEN-QUESTIONS LOCKED 2026-10-01).
 - Server Setup -> Cooking -> Campfire accessory -> "Campfire XP share" (campfire.xpFactor) default 0.5 -> 0.25. CAMP_XP_DEF below is the
   row default, the loader fallback for a missing / unreadable line (CookCfg.DEF_CAMP_XP), the running field's start value
   (CookCfg.CAMP_XP), the generated cooking.properties line and the block a 0.1 file gets appended; the row help says "0.25 = a quarter".
   /cooking, the Skills Stats line, the campfire chat hint and /cookadmin campfire print the LIVE share ("25%"), cook:fn:campfactors
   reports the live 0.25. A dish cooked through the Campfire accessory (SkyySacks /craft Campfire tab) now pays a quarter of its Cooking
   Bench XP: Cooked Wildmeat 1,600 -> 400, Grilled Fish 2,000 -> 500, Roast Vegetable 1,200 -> 300 per dish (base XP: xpMultiplier and
   SkyySkills' Cooking Wisdom apply on top, the maxXpPerMinute window as before). The Grade share (campfire.buffFactor 0.75), bench
   cooking and every other row are unchanged.
 - ONE-TIME UPDATE of an existing cooking.properties (CookMig.migrate; setup() calls it right after CookCfg.FILE is set, BEFORE
   CookCfg.load and CfgPub.start, so the loader and the kit's first read already see the new line): campfire.xpFactor=0.5 -> 0.25 ONLY
   when that key's LAST line (the one java.util.Properties keeps = what the loader reads) is a one-line entry holding exactly the old
   default text 0.5 - what 0.1.1 appended, 0.1.2's fresh file and the kit's canonical write all say; then every one-line entry of the key
   holding 0.5 gets 0.25. Anything else is KEPT: a hand-edited value (0.3, 0.50, 1, ...) or a continued entry is logged once at INFO
   ("campfire.xpFactor=0.3 kept (custom) - the 0.1.3 default is 0.25"); a line already on 0.25 is silent; a missing line stays missing
   (the fallback 0.25 applies). The SkyyGear 0.1.1 update machinery (GearCfg.migrateStat011, reviewed), method for method:
   CookMig.update = a pure text step on the config kit's own parser (CfgFile.isComment / end / key / value / valStart: escapes and
   continuation lines as the kit and java.util.Properties read them; a continued line is never rewritten); only the value text of a
   changed line is replaced (its key, separator and CR stay); every other byte is kept (ISO-8859-1 in and out, LF / CRLF per line as
   found). CookMig.migrate: CfgHist.snapshot keeps the file as it was as a History version ("before the 0.1.3 campfire XP update",
   restorable in Server Setup -> History) and CookMig.saved checks that config-history REALLY holds a copy with those bytes before
   anything is rewritten (snapshot swallows its own errors; else WARN, the file is used as it is and the next start tries again);
   CfgRows.atomicWrite writes it (tmp + fsync + ATOMIC_MOVE, retries); one config-changes.log line in the kit's scalar-row format
   (time, "SkyyCooking 0.1.3", -, update, campfire.xpFactor, 0.5, 0.25, ok) so Server Setup -> Changes can Undo it (a plain set back to
   0.5); one INFO line ("cooking.properties updated to the 0.1.3 campfire XP share: campfire.xpFactor 0.5 -> 0.25 ..."). Any failure:
   WARN, the file stays as it was, the loader reads it as it is.
   RUNS ONCE: the marker comment CAMP_MARK (below) goes on its own line right above the campfire.xpFactor entry - above its help comment
   when a comment line sits directly on top (the place the fresh file has it); no xpFactor line -> the same rule at campfire.buffFactor
   (the marker then still records the decision, so a 0.5 an admin types later is never touched). A file whose comment lines hold
   CAMP_MARK_ID is never changed again: a 0.5 set back later (Changes -> Undo, Server Setup, a History restore - the kit restores VALUES
   through its normal line-preserving write, the marker stays) is kept across restarts. The 0.1.3 default text and the campfire block
   a 0.1 file gets appended carry the marker, so a fresh file never updates. A file with neither campfire line (a 0.1 file) is left to
   the loader, which appends the marked 0.1.3 block (0.25). Second start = nothing written.
 Nothing else changed: Grades, bench cooking, the XP table, caps, bridge keys and shapes, commands, permissions, player switches and the
 other config rows are as 0.1.2 (class compare in the build report: Cook, CookXpTask, CookSys, the bridge functions and the commands
 are byte-identical). The config kit classes are rebuilt with the current tools/skyycfg.py = kit 1.1 (tools/CONFIG-CONTRACT.md lists
 SkyyCooking among the adopters that pick up 1.1 at their next version; the 0.1.2 jar carries kit 1.0; KEEP stays 20). Bare-JVM
 harness: SkyyCooking/test_skyycooking_0.1.3.py (XP maths through the compiled cook:fn:campfire, the update on scratch copies of the live
 file, the kit's Changes / Undo path, edge cases against java.util.Properties, class compare).
 OTHER MODS: SkyySacks 0.7.9's Campfire tab reads the live share (cook:fn:campfactors, else config:fn:SkyyCooking get). SkyyAccessories
  0.5 (live pin) still prints "50% Cooking XP ... by default" in the Campfire Accessory item text and logs one start-up warning that
  cooking.properties says 25% (its Accessory Bag page line reads the live share); its build check reads CAMP_XP_DEF from the newest
  SkyyCooking script, so its next build must set CAMP_XP_PCT 50 -> 25.
 TEST (0.1.3, Skyy, one account with op, after a deploy over the live 0.1.2 world): server log "[SkyyCooking] cooking.properties updated
  to the 0.1.3 campfire XP share: campfire.xpFactor 0.5 -> 0.25 ..." then "[SkyyCooking] 0.1.3 ready ... campfire accessory x0.75 Grade
  bonus x0.25 XP"; cooking.properties: campfire.xpFactor=0.25 with the marker comment above its help line, every other line as before;
  /cooking -> "... and pay 25% of the Cooking XP."; /cookadmin campfire wildmeat_cooked 1 -> "Cooking XP sent 400"; /craft Campfire tab
  (Campfire accessory equipped) -> banner "25% Cooking XP, 75% of your cooking bonus" and one Cooked Wildmeat pays 400 base XP;
  /modconfig cooking -> Campfire accessory -> Campfire XP share 0.25; Changes lists "SkyyCooking 0.1.3 ... campfire.xpFactor 0.5 -> 0.25"
  with Undo; History lists "before the 0.1.3 campfire XP update". Restart -> no update line, still 0.25. (Optional: Undo -> 0.5 ->
  restart -> stays 0.5; set it back to 0.25.)

0.1.2 = IN-GAME SETUP + PLAYER SETTINGS (Skyy 2026-09-24: everything a server owner might change must be doable in game; the files stay and
 always match). research/Server-Setup-Spec.md 4.13 + 7 and research/Settings-Spec.md 1.3 + 3.6. GAMEPLAY IS UNCHANGED until an admin changes
 a value or a player flips a switch: every row default is the value the generated cooking.properties writes (build-checked), and without
 SkyyMenu every player switch reads ON.
 ADMIN CONFIG (tools/skyycfg.py, contract tools/CONFIG-CONTRACT.md; SkyyMenu 0.3 Server Setup shows it as "Cooking", /modconfig cooking):
  config:def:SkyyCooking + config:fn:SkyyCooking (+ config:epoch:SkyyCooking) published at the END of setup(), after CookCfg.load(). Node
  skyycooking.admin (the existing /cookadmin node; the kit re-checks it on every change). File Skyy_SkyyCooking/cooking.properties, KEYS
  UNCHANGED. Every row binds reload@cooking.properties: the kit validates, logs (Skyy_SkyyCooking/config-changes.log), keeps versions
  (config-history/), rewrites ONLY the changed line, and after its atomic write runs CookCfg.load() = RELOAD (the same routine /cookadmin
  reload uses; it only parses into volatile fields). Everything is live.
   tab       key (= file key)       type   default        range / flags
   Parts     enabled                bool   true           live, part, danger (asks only when switched OFF): off = plain food, no Cooking XP
   Grades    maxGrade               int    12             0-12 (the loader's clamp; can only LOWER the cap: the jar has Grade 1-12 assets)
             graded                 items  the 15 dishes  check hook CookHooks.checkGraded: only dishes this jar generated Grades for
             creativeGrades         bool   false          live, danger with confirm=on (only turning it ON asks: creative XP farming)
   Cooking XP xpMultiplier          dec    1              0-100 x, live, danger   (0.1.4: default 0.5 - Skyy 2026-10-02)
             maxXpPerMinute         int    (build value)  0-100,000,000 (0 = no cap)
             xp                     table  xp.<id>=<XP>   column XP 0-1,000,000, add typed or held item; check hook CookHooks.checkXp (an
                                                          existing item id or "default"). The entry "default" IS the xp.default line (see
                                                          LEFT OUT). Removing an entry = back to the built-in value (the loader seeds them).
   Campfire  campfire.buffFactor    dec    0.75           0-1
             campfire.xpFactor      dec    0.5            0-1   (0.1.3: default 0.25 - Skyy 2026-10-01)
   Skill tree tree                  table  tree.<Node>.per column Chance per level 0-1, no add (the 10 node entries), adv; check hook
                                                          CookHooks.checkTree. Only a fallback: SkyyTrees' tree:fn:bonus wins when present.
   Chat      messages               bool   true           the admin master switch (it still wins over the player switches)
  /cookadmin reload (skyycooking.admin) keeps working: it clears the asset caches and re-reads the file with CookCfg.load() exactly as
  0.1.1 did (same summary line), THEN runs the kit's reload op with via=command (hand edits are logged via=file and shown in Server Setup ->
  Changes). The command never writes on the world thread (review fix: no CfgPub.flush() here, CONFIG-CONTRACT guarantee 4, the SkyySacks
  0.7.2 lesson): the op only reads the file on the caller's thread and queues the kit's save on HytaleServer.SCHEDULED_EXECUTOR, which
  writes any pending in-game change and then runs CookCfg.load() again. Nothing reverts: reload@ rows only reach the running fields through
  that save, and CookCfg.load is synchronized, so the save task's load always runs after the command's. The reply shows the file as it is
  on disk (hand edits included); a change made in game in the last half second is not in it yet and applies when that save runs.
  /cookadmin give and /cookadmin campfire write no config: unchanged. shutdown() calls CfgPub.shutdown() (pending saves written).
 PLAYER SETTINGS (SkyyMenu 0.2+ registry; bridge settings:fn:get / settings:fn:register / settings:def:<key>):
  Cook.notifyOn(UUID, key) / Cook.regSetting(...) = the Settings-Spec 1.3 helper verbatim (mod "SkyyCooking", creating bridge()).
  Registered in setup(), category cooking, default ON:
   cooking.grade  "Food Grade changes"   help "Your food now comes out Grade 3 - and the campfire accessory hint"
   cooking.procs  "Cooking bonus procs"  help "Gourmet!, Signature Dish!, Batch Cook!, Prep Cook! and Frugal!"
  Cook.tell(pr, msg, force, key): messages=false (admin) still wins first; then the player's switch; THEN the 2.5 s LAST throttle (a hidden
  line never eats the cooldown of a shown one). The 3-argument tell delegates with key null (never gated). Gated sends only - the work
  (XP, dishes, TOLD / CAMP_TOLD latches, logs) runs exactly as before:
   CookXpTask.run  "Your food now comes out Grade N ..."        -> cooking.grade  (TOLD.put stays before it: a hidden Grade counts as told)
   CookXpTask.run  proc note (Gourmet / Signature / Batch / Prep / Frugal) -> cooking.procs
   Cook.campHint   campfire accessory hint                       -> cooking.grade  (CAMP_TOLD.put stays before it)
  Never gated: /cooking, every /cookadmin reply (replies to your own action, Settings-Spec 2.3).
 LEFT OUT (and why):
  - xp.default as its own row (spec 4.13 lists it): the kit's one-owner rule (tools/CONFIG-CONTRACT.md) fails the build when a scalar file key
    lies inside a table's key family, and xp.default is inside xp.; the file key must not change, so it is the xp table's "default" entry.
  - maxGrade minimum 1 (spec 4.13): 0 is used because the loader accepts 0 (every dish plain) and typed values are rejected, never clamped;
    the "can only lower the cap" note is the row's help line (no extra ro row).
  - The three refusing switches (party.invites, tpa.requests, msg.private): not this mod, and not built until Skyy answers refuse-vs-hide.
  - SkyyMenu MENU DATA config/reload fields for Cooking: SkyyMenu's file, not this mod's (spec 7: "only while not adopted").
 BUILD SELF-CHECKS (0.1.2): every scalar row default == the canonical value of its line in the generated cooking.properties; the xp table
  defaults = xp.default + every XP key, the tree table defaults = the 10 nodes, all inside the row bounds; the compiled CookHooks accept the
  defaults and refuse a non-graded dish / an unknown node; the compiled Cook.notifyOn reads ON without SkyyMenu, follows a fake
  settings:fn:get (FALSE -> off, TRUE / null -> on) and Cook.regSetting writes settings:def:<key> (6 elements) and calls
  settings:fn:register; the source keeps the setting check before the LAST throttle; CfgPub.start is the last statement of setup().
 UNVERIFIED (first in-game test): the Cooking page in Server Setup (tabs, table views, confirm texts), a change reaching the running game
  through the reload routine on the server scheduler (the kit's bare-JVM harness proves the kit path, not this mod in game), the two
  switches in /settings -> Cooking.
 TEST (0.1.2, Skyy, one account with op): log "[SkyyCooking] 0.1.2 ready"; /modconfig cooking opens the Cooking page with 6 tabs; Cooking XP
  -> xpMultiplier 2 asks "Change Cooking XP multiplier from 1 x to 2 x?" -> Confirm -> cooking.properties shows xpMultiplier=2 (the only
  changed line, comments kept) and a Meat Pie at a Cooking Bench pays double XP; Default -> back to 1 (the line now reads xpMultiplier=1,
  not the old 1.0: the kit always writes canonical decimals and the loader reads both the same - expected); Campfire -> campfire.xpFactor 1 ->
  /cookadmin campfire wildmeat_cooked 1 pays the full 1,600 XP; Parts -> Graded cooking OFF asks first, then /cooking says graded cooking
  is off and a Cooking Bench dish comes out plain with no XP; ON again asks nothing; Cooking XP -> XP per craft -> set Food_Pie_Meat to
  30000 -> a pie pays 30,000; Remove it -> back to 23,900; edit maxGrade=5 in the file by hand, /cookadmin reload -> the chat line says
  1 value changed by hand and "max Grade 5", Server Setup -> Changes lists it (via file); Changes -> Undo of the xpMultiplier line works.
  Set xpMultiplier 3 in the menu and type /cookadmin reload within a second: no hitch for other players, and a pie pays triple XP
  right after (the kit's save writes the line and re-runs the loader off the world thread).
  /settings -> Cooking: Food Grade changes OFF -> reach a new Grade (or /cookadmin campfire at a new campfire Grade) -> no chat line, but
  the dishes and XP still come; Cooking bonus procs OFF -> Gourmet!/Batch Cook! lines gone, the extra dishes still given; both ON -> lines
  back. A second account without op: /modconfig is refused; its own /settings switches do not change the first account's lines.
 Everything 0.1.1 does is unchanged (its sections follow).


0.1.1 = THE CAMPFIRE ACCESSORY COMES BACK (Skyy 2026-09-24, HANDOFF "Feedback on the build round"): "add the campfire accessory back for
 quick inventory cooking as it already limits what you can make ... 50% xp and 75% of your normal buffs when using it, so its an
 emergency cook". Cooking a Campfire dish THROUGH THE ACCESSORY (SkyySacks' /craft page, instant) gives a graded dish whose Cooking-skill
 bonus is x campfire.buffFactor (0.75) and pays Cooking XP x campfire.xpFactor (0.5; 0.25 since 0.1.3). NO new assets: the 0.1 Grade 1-12 dishes are
 reused. The placed vanilla Campfire is unchanged (plain food, no XP). The Alchemy Bench and Cooking Bench accessories stay retired.
 Everything 0.1 does is unchanged.
 GRADE: G = the Grade a Cooking Bench guarantees right now = min(floor(Cooking level / 10), 10) + 1 if Master Chef (CMaster) >= 1,
  clamped to maxGrade (the number cook:fn:grade and /cooking show). ONE helper computes it: Cook.benchGrade(level, tree) - used by
  guaranteed() (cook:fn:grade), the bench roll(), /cooking, the Skills Stats page and campfire(), and the build runs the compiled one
  against a Python mirror. Target multiplier T = 1 + buffFactor x (M(G) - 1), M(g) = 2^(g/5) (0.1.4: M = the STRENGTH factor
  S(g) = 1 + 0.32 x g, CookCfg.MUL - see the 0.1.4 section).
  The dish comes out at c = the highest Grade 0..G with M(c) <= T (the existing Grade whose multiplier does not exceed the target).
  No chance rolls (Gourmet, Signature Dish, ...) and no tree extras (Batch Cook, Frugal) through the accessory: the emergency cook gets
  the guaranteed Grade only. The 3 campfire dishes are T1 dishes and hit no effect cap, so S / D (0.1.1-0.1.3: M) are their real heal /
  buff strength and duration factors (build self-check).
  Default table 0.1.1-0.1.3 (buffFactor 0.75, M = 2^(g/5); 0.1.4's strength table is in the 0.1.4 section), Cooking Bench Grade ->
  campfire-accessory Grade (printed and asserted by the build):
   G0->0  G1->0  G2->1  G3->2  G4->3  G5->4  G6->4  G7->5  G8->6  G9->7  G10->8  G11->9  G12->10
 BRIDGE (new; published in setup, removed in shutdown):
  cook:fn:campfire   java.util.function.Function, apply(Object[] a) -> String or null
     a[0] java.util.UUID   the crafting player (required)
     a[1] String           the CraftingRecipe id SkyySacks crafted, String.valueOf(recipe.getId()) (required). It must be a
                           Campfire-bench recipe (BenchRequirement Id "Campfire") whose primary output is in cook:campfire:ids. REFUSED
                           (null = give the normal output): a bare dish id such as "Food_Wildmeat_Cooked" (it cannot prove the craft was
                           a Campfire craft) and every Cooking Bench recipe, including this mod's Skyy_Cook_Recipe_Wildmeat / _Fish /
                           _Vegetable (same dishes, full Grade and XP at a real Cooking Bench) - a Cooking Bench craft is never graded
                           as an emergency cook. (Engine recipe ids of item recipes are "<ItemId>_Recipe_Generated_<n>", never a dish id.)
     a[2] Number           finished crafts (1 craft = 1 dish), required. >= 1 = a real craft: pays XP (at most 10,000 crafts' XP per
                           call; above that the extra crafts pay no XP and the log says so every 60 s - send big batches in parts).
                           <= 0 = PREVIEW: returns the id a craft would give now; no XP, no chat, no cap use.
     a[3] String           OPTIONAL expectKey = the profile key (pkey) the caller resolved when the craft started. null or absent = no
                           check. Different from the current key -> plain id and no XP.
     a[4] Boolean          OPTIONAL creative flag (the player's GameMode == Creative). Absent = read from the player's live entity (only
                           possible on that player's world thread).
     RETURNS the item id to hand out INSTEAD of the recipe's primary output id, same quantity (crafts x 1): "Skyy_Cook_<dish>_G<c>" or
      the plain dish id. null = not a campfire dish, malformed arguments or an internal error: give your normal (plain) output.
     THREAD: the player's world thread (SkyySacks' craft page handleDataEvent), after the materials were removed. No disk I/O, no ECS
      writes. The XP grant happens inside the call (skill:fn:addxp, which queues it on the world thread).
     XP: base = round(xp.<dish> x crafts x campfire.xpFactor) (0.1.3 defaults: Cooked Wildmeat 1,600 -> 400, Grilled Fish 2,000 -> 500,
      Roast Vegetable 1,200 -> 300 per dish) -> this mod's maxXpPerMinute window (shared with bench cooking): a batch pays the part that
      still fits this minute and only the rest is dropped (Cook.allowXpPart - cross-check fix: a single "All" click of 1,876+ wildmeat
      used to drop ALL its XP), the dishes always come out graded -> x xpMultiplier -> skill:fn:addxp(Object[]{UUID, "Cooking", Long,
      "cook:campfire:<dish>", pkey}) in parts of <= 400,000 (SkyySkills adds the Cooking tree Wisdom bonus there).
     ONE XP SOURCE PER CRAFT (caller rule): a craft routed through cook:fn:campfire must NOT also be reported to skill:fn:craftxp - this
      call is its only Cooking XP. SkyySacks 0.7.4 does exactly that (no craftxp call for its Campfire tab). Do not rely on SkyySkills'
      RecipeXp.classify paying 0 for Campfire recipes (0.4 does, but it is another mod's table). SkyyCooking cannot probe craftxp at
      start: it has no preview (crafts < 1 counts as 1) and would pay real XP.
     PLAIN id + NO XP (the bench rules): enabled=false; profile:busy:<uuid>; expectKey differs; creative (flag TRUE or read as Creative,
      unless creativeGrades=true); game mode unreadable and no flag passed; SkyySkills missing (no skill:fn:level).
     PLAIN id + XP: campfire Grade 0 (low Cooking level), the dish removed from graded=, or its Grade asset not loaded.
     CHAT: after a real craft, one hint per session (and again when the campfire Grade rises), only with messages=true.
  cook:campfire:ids  String "Food_Wildmeat_Cooked,Food_Fish_Grilled,Food_Vegetable_Cooked" = the dishes cook:fn:campfire grades (every
      vanilla Campfire recipe output, build-checked). It lists OUTPUT ids only, not benches: the Cooking Bench makes the same 3 dishes.
      SkyySacks shows exactly the Campfire-bench recipes (BenchRequirement Id "Campfire") whose primary output is listed.
  cook:fn:campfactors  java.util.function.Function, apply(anything) -> Object[]{ Double buffFactor, Double xpFactor, Boolean enabled } =
      the LIVE campfire.buffFactor / campfire.xpFactor / enabled (after /cookadmin reload too), for a UI line such as SkyySacks' Campfire
      tab banner, so it never shows stale percentages. Any thread, no I/O.
 CONFIG (cooking.properties; appended once to a 0.1 file that lacks both lines): campfire.buffFactor=0.75, campfire.xpFactor=0.25 (0.5
  until 0.1.3)
  (each 0..1, clamped with a log line; /cookadmin reload re-reads them).
 COMMAND: /cookadmin campfire <dish> <count 0-64> (skyycooking.admin) looks up the vanilla Campfire recipe of that dish and runs the
  bridge with that RECIPE id exactly the way /craft calls it (world thread, creative flag read from the Player component and passed as
  a[4]) and gives count x the returned id (no materials used) + the XP; count 0 = preview. Its chat line also names the recipe id and
  says how the bridge reads the game mode WITHOUT a flag (creative / not creative / unreadable). /cooking and the Skills Stats page
  show the campfire Grade and XP share.
 RECOMMENDED CALL (SkyySacks craft page, after removing the materials, done = finished crafts):
  Object id = ((Function) bridge.get("cook:fn:campfire")).apply(new Object[] { u, String.valueOf(r.getId()), Integer.valueOf(done), k,
  Boolean.valueOf(p.getGameMode() == GameMode.Creative) });  -> give (String) id instead of the primary output id when it is a String,
  else the normal output. Show only Campfire-bench recipes (BenchRequirement Id "Campfire") whose primary output is in
  cook:campfire:ids (split on ","); absent key = SkyyCooking missing. Always pass the recipe id, never the bare output id, and do not
  call skill:fn:craftxp for these crafts.
 OTHER MODS (checked 2026-09-24): SkyyAccessories 0.4.3 un-retires Skyy_Accessory_Campfire_T1 (its tooltip numbers are build-checked
  against CAMP_BUFF_DEF / CAMP_XP_DEF below) and SkyySacks 0.7.4 adds the /craft Campfire tab that calls cook:fn:campfire exactly as
  above (recipe id, finished crafts, settled key, creative flag; preview with crafts 0 for the row note; no craftxp for that tab). Its
  tab banner and SkyyAccessories 0.4.3's Accessory Bag line read the live factors from cook:fn:campfactors (cross-checked 2026-09-24:
  names, argument array, return, thread and the then-default x0.5 XP / x0.75 bonus end to end, offline with the three built jars).

WHAT IT IS - research/Cooking-Skill-Spec.md, adapted to the orchestrator's decisions of 2026-09-24:
 (1) Cooking lives in its OWN mod (this one), so its ~450 generated assets can never break SkyySkills if they fail to load.
     SkyySkills 0.4 owns only the Cooking ROW (slot 12) and receives Cooking XP through its XP-grant bridge skill:fn:addxp;
     SkyySkills' own craft system ignores Cookingbench crafts - this mod owns them.
 (2) XP pace re-scaled so the best route reaches Cooking 50 in about the time Alchemy 50 takes (~27 focused hours, Alchemy spec
     4.3), instead of the spec's draft table (which put level 50 at ~550,000 pies). Model in the XP section below (printed at build).
 (3) Grades 11 and 12 come ONLY from the Cooking skill tree, the 4th tree in SkyyTrees, read through bridge tree:fn:level
     (UUID, "Cooking.<NodeId>") -> Integer (research/Skill-Trees-Spec.md section 10, node ids = Cooking spec 7.2).
 Zero hard dependencies: without SkyySkills every dish comes out plain (Grade 0) and cooking pays no XP.

HOW IT PLAYS: cook at a placed vanilla Cooking Bench (its ingredients can come from Magic Bags through the SkyySacks bench link).
Every finished dish pays Cooking XP (SkyySkills shows the +XP line). From Cooking 10 on dishes come out GRADED: "Meat Pie (Grade 5)".
Grade = floor(Cooking level / 10) (max 10 from levels) + Cooking-tree bonuses (cap 12). Since 0.1.4 the Grade sets two factors:
STRENGTH S = 1 + 0.32 x Grade (heal %, regen per tick, max-Health / max-Stamina bonus, damage resistance): x1.32 at Grade 1, x2.60 at
Grade 5 (level 50), x4.20 at Grade 10 (level 100), x4.52 / x4.84 at the tree-only Grades 11 / 12; DURATION D = 2^(Grade/5) of everything
the dish does: x2.00 at Grade 5, x4.00 at Grade 10, x4.59 / x5.28 at Grades 11 / 12 (until 0.1.3 one multiplier M = 2^(Grade/5) set both).
Whoever eats the dish gets the cook's Grade. Same-Grade dishes stack (they are one item id); different Grades do not.

ENGINE PATH (VERIFIED bytecode 2026-09-24, tools/dev/bcfull.py):
 - Cooking Bench = bench id "Cookingbench", Bench.Type Crafting, no tiers. Every vanilla cooking recipe has TimeSeconds 1/2/5, so it
   takes the QUEUED path: CraftingManager.tick removes one unit's inputs, fires new CraftRecipeEvent$Post(job.recipe, job.quantity)
   through ComponentAccessor.invoke(ref, ev) (= CommandBuffer.invoke -> Store.internal_invoke, synchronous), then calls
   giveOutput(ref, accessor, job, n) -> giveOutput(ref, accessor, recipe, 1) ONLY if the event was not cancelled. So one Post per
   finished dish, but getQuantity() is the whole batch: we count 1 unit per Post when TimeSeconds > 0 (instant path: quantity).
 - CookSys (EntityEventSystem on CraftRecipeEvent$Post, the only system class of this mod) grades SYNCHRONOUSLY in the handler: it
   cancels the Post and hands out the graded stacks exactly the way vanilla giveOutput would (SimpleItemContainer.addOrDropItemStack
   with the handler's CommandBuffer), into getCombinedStorageHotbarBackpack (storage first - SkyySacks 0.6.5 lesson). Grade 0 with
   no tree bonus = nothing cancelled, vanilla gives the plain dish. Tree extras (extra dish / ingredient back / double ingredient)
   are given NEXT TO the normal output, never instead of it.
 - The XP award is deferred with world.execute (runs after every other system saw the event, the SkyySkills BreakTask pattern):
   skipped if someone ELSE cancelled the Post, if the profile switched meanwhile (pkey changed), or past the per-minute cap.
 - Eating needs no Java at all: a graded dish is a normal food item whose eat chain (vanilla Root_Secondary_Consume_Food_T<n>)
   points at PRE-SCALED effect assets; vanilla ApplyEffectInteraction looks them up by id (Cooking spec 5.1, VERIFIED bytecode).

GENERATED ASSETS (asset pack in this jar, all copied from the game's own shapes in Assets.zip, 447 JSON files):
 - Server/Entity/Effects/SkyyCook/Skyy_Cook_<Base>_G<g>.json      13 vanilla food effects x Grades 1-12 = 156
   (Food_Instant_Heal_T1/T2/T3/Bread, HealthRegen_Buff_T1-3, Meat_Buff_T1-3, FruitVeggie_Buff_T1-3; vanilla JSON with ONLY the
   strength fields x S and Duration x D (instant 0.1 s effects keep their duration); caps: instant heal <= 100 %, regen <= 12 %
   per tick, max-stat bonus <= +150 %, resistance <= 50 %, Duration <= 2400 s; 0.1.4: none of them binds at any Grade)
 - Server/Item/Interactions/SkyyCook/Skyy_Cook_<Family>_Check_T<t>_G<g>.json   3 families x 3 tiers x 12 = 108
   (vanilla <Family>_TierCheck_T<t> rule "a weaker buff never replaces a stronger one" extended to all 39 members of a family:
   EffectCondition on every stronger member, Match None -> Serial [ClearEntityEffect every weaker member, ApplyEffect this one];
   rank = (strength, duration). Only vanilla interaction types. doTickChain runs instant operations back to back in ONE tick.)
 - Server/Item/Items/SkyyCook/Skyy_Cook_<Dish>_G<g>.json           15 dishes x 12 = 180 (vanilla dish copy: Parent Template_Food,
   every own key EXCEPT Recipe, own name/description/Quality, InteractionVars.Effect -> the Grade assets)
 - Server/Item/Items/SkyyCook/Recipes/Skyy_Cook_Recipe_<X>.json     3 Cooking Bench recipes for the Campfire dishes (vanilla
   "Variant recipe" shape of Ingredient/Life Essence Recipes: Variant true, Parent = the output item, own Recipe with Output)
 - Server/Languages/en-US/server.lang   name + description of every graded dish (items.* and server.items.*, the SkyyAccessories form)
 BUILD-TIME SELF-CHECK (the build fails if one is false): D(5) = 2, D(10) = 4 + Skyy's S(g) (0.1.4); every effect / interaction / root interaction id
 referenced by a generated item or interaction exists (generated or Assets.zip); every item Parent, icon, model and texture exists;
 no graded dish has a Recipe; every recipe variant outputs one of the 15 dishes and uses existing inputs; no generated id collides
 with a vanilla id; the 15 dishes, their eat chains and the 13 base effects still have the numbers this build expects (a Hytale
 update stops the build instead of shipping wrong numbers); every graded item has lang lines; XP keys are real Cookingbench outputs;
 no cooking output feeds a recipe that gives its own inputs back (craft/uncraft loop); XP per call and per minute stay under
 SkyySkills' bridge caps.

GRADED DISHES (15): Food_Wildmeat_Cooked, Food_Fish_Grilled, Food_Vegetable_Cooked (T1, via the new Cooking Bench recipes),
 Food_Bread, the 4 kebabs, Food_Salad_Berry, Food_Salad_Mushroom (T2), Food_Popcorn, the 3 pies, Food_Salad_Caesar (T3).
 NOT graded: Food_Cheese (it is an input by id for Caesar Salad and Potion_Morph_Mouse), ingredients (flour, dough, salt, spices,
 raw fish) - they still pay XP. A placed Campfire has no owner and fires no event (VERIFIED): plain food, no XP.

STACKING WHEN EATING: instant heal every bite; same buff again = timer restarts (Overwrite, never adds); a stronger buff of the same
 family replaces the weaker (cleared); a weaker one while a stronger runs does nothing for that family; different families run side
 by side; vanilla (Grade 0) buffs rank inside the families. KNOWN LIMIT (spec 5.4): a PLAIN vanilla dish eaten while a graded buff
 runs may add its own vanilla buff next to it (vanilla chains only know vanilla ids) - worst case one extra vanilla-strength buff.

SKILL TREE (Cooking spec 7.2, read at craft time; per-level values in cooking.properties tree.<Id>.per):
 CGourmet (25) +0.8 %/lvl chance of +1 Grade; CBatch (20) +1 %/lvl one extra dish (same Grade, no XP); CFrugal (10) +2 %/lvl one
 item-id ingredient back (never Fuel / resource-type inputs); CGrill (15) / CPrep (10) / CBaker (10) +2/3/3 %/lvl +1 Grade on
 T1 / T2 / T3 dishes; CIngr (10) +3 %/lvl double output of an ingredient craft (flour, dough, salt, spices); CGourmet2 (20) +1 %/lvl
 +1 Grade (adds to CGourmet); CSig (10) +1 %/lvl +2 Grades; CMaster (5) level 1 = +1 Grade on every dish, levels 2-5 +5 % each
 chance of one more. One roll per dish: g = level/10 (max 10) + (CMaster >= 1), then +1 on the combined chance or +2 on CSig, cap 12.
 CWisdom (XP %) and CFed (max Health) are SkyyTrees / SkyySkills hooks, not read here: SkyyTrees 0.1 posts Cooking Wisdom as
 xp.cooking in skill:bonus:<uuid>, and SkyySkills 0.4 multiplies the XP this mod sends through skill:fn:addxp by it (BridgeXp.offer,
 only while Cooking is in BOTH bridge.bonus.xpSkills and bridge.bonus.addxpSkills of SkyySkills' xp.properties - both list it by
 default; its bridge.maxXpPerMinute counts the boosted XP: legit peak 708k x 1.15 < 3M).

ANTI-EXPLOIT: creative = vanilla output, no Grade, no XP (creativeGrades=false; on the cook:fn:out bridge too, where an unknown game
 mode without the caller's creative flag also means plain and no XP); 1 unit per queued Post (batch trap); no graded dish
 has a recipe; a Post another system cancelled first is neither graded nor paid; profile:busy:<uuid> (pending crash recovery) =
 plain output and no XP; XP dropped if the profile switched before the award; per-player cap maxXpPerMinute (base XP, counted before
 xpMultiplier) - the dish is still given when it trips; an item id is only ever handed out after Item.getAssetMap() confirmed it
 exists (if the asset pack failed to load, food comes out plain - never an "Invalid Item").

STORAGE: nothing per player on disk. Config Skyy_SkyyCooking/cooking.properties (global). Memory only, per UUID: the XP-per-minute
 window, the chat throttle and the "new Grade" hint (a profile switch does not reset the XP window on purpose). The Grade lives in
 the item id, so it survives chests, trades, drops, relogs and Magic Bags; the XP lives in SkyySkills' per-profile files.

BRIDGE (System.getProperties().get("skyy.bridge")):
 reads  skill:fn:level  (Object[]{UUID, "Cooking"}) -> Integer          SkyySkills 0.4 (absent = no SkyySkills: Grade 0, no XP)
        skill:fn:addxp  (Object[]{UUID, "Cooking", Long baseXp, String source}) -> Boolean   SkyySkills 0.4 (Alchemy spec 7.1;
                        must list Cooking in bridge.addxp.skills - orchestrator decision 6); calls are split at 400,000 XP
        (skill:fn:addxp also gets the profile key captured at craft time as its optional 5th element, expectKey)
        tree:fn:level   (Object[]{UUID, "Cooking.<Id>"}) -> Integer     SkyyTrees 0.1 (absent = every node 0)
        tree:fn:bonus   same argument -> Double chance (level x per from SkyyTrees' trees.properties; Master Chef = (level - 1) x per);
                        preferred for the chances so Skyy tunes them in ONE place; absent -> level x tree.<Id>.per of cooking.properties
        profile:fn:key / profile:busy:<uuid>                             SkyyProfiles contract
 writes cook:fn:grade   apply(UUID) -> Integer  guaranteed Grade now (level/10 + Master Chef) - for the HUD / Menu / Skills Stats page
        cook:fn:out     apply(Object[]{UUID, String recipeId, Number crafts [, String expectKey [, Boolean creative]]}) -> java.util.List
                        of ItemStack: graded outputs + tree extras for a Cookingbench craft ANOTHER mod completed without
                        CraftingManager (SkyySacks /craft), and it pays the Cooking XP itself (SkyySkills ignores Cookingbench crafts,
                        so skill:fn:craftxp pays 0 for them). null = not a Cookingbench recipe (or expectKey mismatch; pass null to
                        skip the key check). Call it on the player's world thread and pass creative = the player's
                        GameMode == Creative. The function also reads the game mode itself (PlayerRef -> Ref -> Store, only when
                        Store.isInThread()). Creative (flag TRUE or read as Creative, unless creativeGrades=true), profile:busy,
                        enabled=false, or a game mode that is unknown with no flag passed -> the plain vanilla outputs and NO XP.
                        Nothing calls it yet (SkyySacks 0.7.3 never crafts Cookingbench recipes).
        cook:prefix     "Skyy_Cook_Food_" (SkyySacks catOf -> Farming bag; Bazaar)
        cook:fn:campfire / cook:campfire:ids / cook:fn:campfactors   0.1.1 Campfire accessory - exact contract in the 0.1.1 section at the top
        skill:stats:Cooking  apply(Object[]{UUID, Integer level, Boolean next}) -> List of String: the Cooking lines of SkyySkills 0.4's
                        Stats page (your Grade and multiplier, next Grade, tree chances; "Level L+1 adds" shows a new Grade at 10, 20 ...)
 All removed again in shutdown().

XP (defaults written to cooking.properties, base XP per finished craft, keyed by the output id; SkyySkills' multiplier on top):
 Meat Pie 23,900 - Apple Pie 25,250 - Pumpkin Pie 23,200 - Bread 12,900 - Caesar Salad 11,800 - Meat Skewer 5,250 - Fruit / Veg
 Skewer 3,650 - Mushroom Skewer 2,850 - Berry Salad 4,850 - Mushroom Salad 3,250 - Popcorn 3,000 - Grilled Fish 2,000 - Cooked
 Wildmeat 1,600 - Roast Vegetable 1,200 - Flour 1,425 - Spices 855 - Dough 640 - Cheese 430 - Raw Fish 285 - Salt 140 - other 1,000.
 Model (printed by the build): meat-pie route = 23.7 weighted raw items -> ~26,850 XP; at the Alchemy spec's 1,800 items/hour that is
 ~2.04M XP/h -> Cooking 50 in ~27 h (vegetable skewers only: ~38 h). Level 10 comes after half a pie and level 20 after ~20 pies
 (the shared curve is steep late, flat early); decision 2 anchors level 50 only. Legit bench peak (Caesar salad, 1 s) = 708k base
 XP/min, under SkyySkills' addxp caps (500k per call, 3M per minute); our own cap defaults to 1.5M/min.

UNVERIFIED (first in-game test): that the 447 generated assets load from this jar (items + lang are proven for Skyy mods; effects and
 interactions from a Skyy jar are new - NotEnoughPotions ships both the same way); that a mod-shipped Variant recipe item shows on the
 Cooking Bench; that dishes given from the Post handler with its CommandBuffer land in the inventory (vanilla does the same call);
 the pace in hours; long family-check Serials (up to 38 ClearEntityEffect + 1 ApplyEffect; doTickChain runs instant operations in
 one tick - VERIFIED bytecode - but a chain this long is new).
TEST (Skyy, after a deploy with SkyySkills 0.4 and optionally SkyyTrees 0.1): server log "[SkyyCooking] 0.1 ready", no asset errors
 naming Skyy_Cook_; /cookadmin give pie_meat 5 -> "Meat Pie (Grade 5)" (Rare) with the tooltip numbers; /cooking at level 0 -> Grade 0;
 cook bread at a placed Cooking Bench with bag ingredients -> plain Bread + Cooking XP; queue 5 skewers -> 5 skewers, 5 x the XP (not
 25x); set Cooking 50 (/skills admin XP helper) and cook a Meat Pie -> exactly one "Meat Pie (Grade 5)"; eat Grade 5 bread at low
 health -> ~30 % heal (0.1.4: ~39 %); eat a Grade 5 Meat Pie -> regen icon 12:00, max health +30 % (0.1.4: +39 %); Grade 10 pie then
 Grade 5 skewer -> the pie's buffs
 stay; Grade 10 pie again -> timer back to 24:00, never added; Grade 5 + Grade 5 stack, Grade 5 + 6 do not; chest + relog keeps the
 Grade; the Cooking Bench lists Cooked Wildmeat / Grilled Fish / Roast Vegetable; placed Campfire -> plain food, no XP; creative ->
 plain, no XP; second player eats your Grade 5 pie -> Grade 5 effects; fresh profile -> plain food; SkyyTrees Master Chef -> +1 Grade.
 0.1.1: log "[SkyyCooking] 0.1.1 ready ... Campfire accessory bridge cook:fn:campfire"; cooking.properties of a 0.1 run gains the
 campfire.* lines once; at Cooking 50 /cookadmin campfire wildmeat_cooked 0 -> "bench Grade 5 -> campfire Grade 4 ... would give
 Skyy_Cook_Food_Wildmeat_Cooked_G4" and no XP; /cookadmin campfire wildmeat_cooked 2 -> 2 x "Cooked Wildmeat (Grade 4)" + 800 Cooking XP
 (0.1.3: a quarter of 2 x 1,600) + the one-time campfire chat hint; at Cooking 100 -> Grade 8; at Cooking 0-19 -> plain dish + a quarter of
 the XP; creative -> plain + 0 XP; campfire.xpFactor=1.0 + /cookadmin reload -> full XP; placed Campfire still plain + no XP. The /cookadmin campfire line
 names the vanilla Campfire recipe id it passed (Food_<dish>_Recipe_Generated_<n>); a bare dish id or a Skyy_Cook_Recipe_* recipe id sent
 to cook:fn:campfire returns null (normal output).

COMMANDS (HANDOFF command rules): /cooking = your Cooking level, Grade, multiplier, next Grade, tree chances (hytale:Adventurer).
 /cookadmin give <dish> <grade> (5 dishes, grade 0-12, dish = Food_Pie_Meat or pie_meat), /cookadmin campfire <dish> <count> (0.1.1),
 /cookadmin reload: requirePermission
 skyycooking.admin + setPermissionGroups(new String[0]). No pages (chat only), so no UI risk.
"""
import sys, os, json, zipfile, copy, re, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyycfg as CFG        # 0.1.2: the admin config kit (research/Server-Setup-Spec.md 1.4, tools/CONFIG-CONTRACT.md)

VERSION = "0.1.6"
HERE = os.path.dirname(os.path.abspath(__file__))
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)

JP  = "com.hypixel.hytale.server.core.plugin.JavaPlugin"
JPI = "com.hypixel.hytale.server.core.plugin.JavaPluginInit"
PR  = "com.hypixel.hytale.server.core.universe.PlayerRef"
REF = "com.hypixel.hytale.component.Ref"
ST  = "com.hypixel.hytale.component.Store"
UNI = "com.hypixel.hytale.server.core.universe.Universe"
WLD = "com.hypixel.hytale.server.core.universe.world.World"
EST = "com.hypixel.hytale.server.core.universe.world.storage.EntityStore"
APC = "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand"
CTX = "com.hypixel.hytale.server.core.command.system.CommandContext"
ATY = "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes"
RA  = "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg"
AC  = "com.hypixel.hytale.server.core.command.system.AbstractCommand"
MSG = "com.hypixel.hytale.server.core.Message"
LOG = "com.hypixel.hytale.logger.HytaleLogger"
PLA = "com.hypixel.hytale.server.core.entity.entities.Player"
GM  = "com.hypixel.hytale.protocol.GameMode"
EES = "com.hypixel.hytale.component.system.EntityEventSystem"
ACH = "com.hypixel.hytale.component.ArchetypeChunk"
CB  = "com.hypixel.hytale.component.CommandBuffer"
CAC = "com.hypixel.hytale.component.ComponentAccessor"
EV  = "com.hypixel.hytale.component.system.EcsEvent"
CEV = "com.hypixel.hytale.component.system.CancellableEcsEvent"
QRY = "com.hypixel.hytale.component.query.Query"
CRE = "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent"
CRP_= "com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Post"   # '$' form only in the class literal (UBP pattern)
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
CRM = "com.hypixel.hytale.builtin.crafting.component.CraftingManager"
BRQ = "com.hypixel.hytale.protocol.BenchRequirement"
MQ  = "com.hypixel.hytale.server.core.inventory.MaterialQuantity"
ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"
IS  = "com.hypixel.hytale.server.core.inventory.ItemStack"
IC  = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
SIC = "com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer"
INV = "com.hypixel.hytale.server.core.inventory.Inventory"
PB  = "com.hypixel.hytale.server.core.plugin.PluginBase"

# API probes (VERIFIED 2026-09-24 with tools/dev/reflect.py + bcfull.py; a Hytale update that renames one stops the build here)
for c, m in ((CRE, "getCraftedRecipe"), (CRE, "getQuantity"), (CEV, "isCancelled"), (CEV, "setCancelled"),
             (CRR, "getInput"), (CRR, "getPrimaryOutput"), (CRR, "getBenchRequirement"), (CRR, "getTimeSeconds"), (CRR, "getId"),
             (CRR, "getAssetMap"), (CRM, "getOutputItemStacks"), (MQ, "getItemId"), (MQ, "getResourceTypeId"), (MQ, "getQuantity"),
             (BRQ, "id"), (ITM, "getAssetMap"), ("com.hypixel.hytale.assetstore.map.DefaultAssetMap", "getAsset"),
             (IS, "getItemId"), (IS, "getQuantity"), (PLA, "getInventory"), (PLA, "getGameMode"), (GM, "Creative"),
             (INV, "getCombinedStorageHotbarBackpack"), (SIC, "addOrDropItemStack"),
             (UNI, "get"), (UNI, "getPlayer"), (PR, "isValid"), (PR, "getUuid"), (PR, "sendMessage"), (PR, "hasPermission"),
             (PR, "getReference"), (REF, "isValid"), (REF, "getStore"), (ST, "isInThread"),
             (MSG, "raw"), (MSG, "color"), (WLD, "execute"), (EST, "getWorld"), (ST, "getExternalData"), (ST, "getComponent"),
             (ACH, "getReferenceTo"), ("com.hypixel.hytale.component.Archetype", "empty"),
             (AC, "setPermissionGroups"), (AC, "requirePermission"), (AC, "addSubCommand"), (AC, "withRequiredArg"), (AC, "addAliases"),
             (ATY, "STRING"), (PB, "shutdown"), (PB, "getEntityStoreRegistry"), (PB, "getCommandRegistry"), (PB, "getDataDirectory"),
             ("com.hypixel.hytale.component.ComponentRegistryProxy", "registerSystem")):
    B.probe(pool, c, m)

PKG = "com.skyy.cooking"
T = {"PKG": PKG, "PR": PR, "REF": REF, "ST": ST, "UNI": UNI, "WLD": WLD, "EST": EST, "CTX": CTX, "ATY": ATY, "RA": RA, "MSG": MSG,
     "PLA": PLA, "GM": GM, "ACH": ACH, "CB": CB, "CAC": CAC, "EV": EV, "QRY": QRY, "CRE": CRE, "CRP": CRP_, "CRR": CRR, "CRM": CRM,
     "BRQ": BRQ, "MQ": MQ, "ITM": ITM, "IS": IS, "IC": IC, "SIC": SIC, "LOG": LOG, "JPI": JPI, "VERSION": VERSION}
def jsrc(s):
    """Java source template: @NAME@ -> constant (keeps Java braces single - no f-string doubling)"""
    def rep(m):
        k = m.group(1)
        if k not in T: raise SystemExit("jsrc: unknown token @%s@" % k)
        return T[k]
    return re.sub(r"@([A-Z_]+)@", rep, s)

# =====================================================================================================================
# ASSET GENERATION (pure Python, before the classes: the Java side bakes in the generated dish list, tiers and factors)
# =====================================================================================================================
AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
ANAMES = AZ.namelist()
def rd(n): return json.loads(AZ.read(n).decode("utf-8-sig"))
def ids_under(prefix):
    out = {}
    for n in ANAMES:
        if n.startswith(prefix) and n.endswith(".json"):
            out[os.path.basename(n)[:-5]] = n
    return out
V_ITEMS = ids_under("Server/Item/Items/")
V_EFFECTS = ids_under("Server/Entity/Effects/")
V_INTER = ids_under("Server/Item/Interactions/")
V_ROOTS = ids_under("Server/Item/RootInteractions/")
V_RTYPES = ids_under("Server/Item/ResourceTypes/")
V_QUAL = ids_under("Server/Item/Qualities/")
V_COMMON = set(n for n in ANAMES if n.startswith("Common/"))
VLANG = {}
for _l in AZ.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
    if "=" in _l and not _l.lstrip().startswith("#"):
        _k, _v = _l.split("=", 1)
        VLANG[_k.strip()] = _v.strip()

GEN_MAX = 12
# 0.1.4 (Skyy 2026-10-02, OPEN-QUESTIONS LOCKED): the ONE multiplier M = 2^(Grade/5) of 0.1-0.1.3 is split in two, both baked into the
# generated assets (a change needs a rebuild):
#  STRENGTH S(g) = 1 + 0.32 x g ("+32% per Grade"): heal %, regen per tick, max-Health / max-Stamina bonus, Stamina per tick, resistance
#  DURATION D(g) = 2^(g/5) ("id leave the duration buff, its good") = the old M, unchanged
COOK_STRENGTH_PER_GRADE = 0.32
def M(g): return 2.0 ** (g / 5.0)              # the duration curve (= the 0.1-0.1.3 multiplier)
def SF(g): return (100 + 32 * g) / 100.0       # strength as an exact decimal quotient: 1.32, 1.64, ... (clean repr in the Java tables)
def DF(g): return M(g)
assert M(5) == 2.0 and M(10) == 4.0, "Duration curve must hit x2 at Grade 5 and x4 at Grade 10"   # self-check 1
assert [SF(g) for g in (0, 1, 2, 5, 10, 11, 12)] == [1.0, 1.32, 1.64, 2.6, 4.2, 4.52, 4.84], "Skyy's strength numbers (0.1.4)"
assert all(abs(SF(g) - (1.0 + COOK_STRENGTH_PER_GRADE * g)) < 1e-12 for g in range(GEN_MAX + 1))

DISHES = ["Food_Wildmeat_Cooked", "Food_Fish_Grilled", "Food_Vegetable_Cooked", "Food_Bread", "Food_Kebab_Fruit", "Food_Kebab_Meat",
          "Food_Kebab_Mushroom", "Food_Kebab_Vegetable", "Food_Salad_Berry", "Food_Salad_Mushroom", "Food_Popcorn", "Food_Pie_Apple",
          "Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Salad_Caesar"]
INGREDIENTS = ["Ingredient_Flour", "Ingredient_Dough", "Ingredient_Salt", "Ingredient_Spices"]   # CIngr (Prep Cook) targets
INSTANT = ["Food_Instant_Heal_T1", "Food_Instant_Heal_T2", "Food_Instant_Heal_T3", "Food_Instant_Heal_Bread"]
FAMILIES = ["HealthRegen", "Meat", "FruitVeggie"]
BASES = INSTANT + ["%s_Buff_T%d" % (f, t) for f in FAMILIES for t in (1, 2, 3)]
# the vanilla numbers this build was written for (Cooking spec 4.1, re-read from Assets.zip 2026-09-24) - self-check 4
EXPECT = {
    "Food_Instant_Heal_T1": ("heal", 5.0, None), "Food_Instant_Heal_T2": ("heal", 10.0, None),
    "Food_Instant_Heal_T3": ("heal", 15.0, None), "Food_Instant_Heal_Bread": ("heal", 15.0, None),
    "HealthRegen_Buff_T1": ("regen", 1.0, 45.0), "HealthRegen_Buff_T2": ("regen", 1.5, 150.0), "HealthRegen_Buff_T3": ("regen", 2.0, 360.0),
    "Meat_Buff_T1": ("maxHealth", 1.05, 45.0), "Meat_Buff_T2": ("maxHealth", 1.10, 150.0), "Meat_Buff_T3": ("maxHealth", 1.15, 360.0),
    "FruitVeggie_Buff_T1": ("maxStamina", 1.10, 45.0), "FruitVeggie_Buff_T2": ("maxStamina", 1.20, 150.0),
    "FruitVeggie_Buff_T3": ("maxStamina", 1.30, 360.0),
}
CAP_HEAL, CAP_REGEN, CAP_MULT, CAP_RES, CAP_DUR = 100.0, 12.0, 2.5, 0.5, 2400.0

def r4(v): return float("%.4f" % v)
VBASE = {}
for b in BASES:
    if b not in V_EFFECTS: raise SystemExit("vanilla effect missing: " + b)
    d = rd(V_EFFECTS[b])
    kind, amount, dur = EXPECT[b]
    if kind == "heal":
        ok = d.get("ValueType") == "Percent" and abs(d["StatModifiers"]["Health"] - amount) < 1e-9 and d.get("Duration", 0) <= 0.5
    elif kind == "regen":
        ok = (d.get("ValueType") == "Percent" and abs(d["StatModifiers"]["Health"] - amount) < 1e-9 and abs(d["Duration"] - dur) < 1e-9
              and d.get("DamageCalculatorCooldown", 0) > 0)
    else:
        stat = "Health" if kind == "maxHealth" else "Stamina"
        m = d["RawStatModifiers"][stat][0]
        ok = (m.get("CalculationType") == "Multiplicative" and m.get("Target") == "Max" and abs(m["Amount"] - amount) < 1e-9
              and abs(d["Duration"] - dur) < 1e-9)
    if not ok:
        raise SystemExit("self-check 4: vanilla effect %s no longer matches this build's expectation (%s %s %s): %s" % (b, kind, amount, dur, json.dumps(d)))
    VBASE[b] = d

def scale_effect(b, g):
    """vanilla effect JSON b scaled to Grade g (g = 0 -> the vanilla JSON itself). Only the strength fields and Duration change."""
    d = VBASE[b]
    if g == 0: return d
    S, D = SF(g), DF(g)
    o = copy.deepcopy(d)
    instant = d.get("Duration", 0) <= 0.5
    pct = d.get("ValueType") == "Percent"
    for k, v in list(o.get("StatModifiers", {}).items()):
        nv = v * S
        if pct: nv = min(nv, CAP_HEAL if instant else CAP_REGEN)
        o["StatModifiers"][k] = r4(nv)
    for stat, lst in o.get("RawStatModifiers", {}).items():
        for m in lst:
            a = m["Amount"]
            if m.get("CalculationType") == "Multiplicative":
                m["Amount"] = r4(min(1.0 + (a - 1.0) * S, CAP_MULT))
            else:
                m["Amount"] = r4(a * S)
    for typ, lst in o.get("DamageResistance", {}).items():
        for m in lst:
            m["Amount"] = r4(min(m["Amount"] * S, CAP_RES))
    if not instant:
        o["Duration"] = float("%.2f" % min(d["Duration"] * D, CAP_DUR))
    return o

def eff_id(b, g): return b if g == 0 else "Skyy_Cook_%s_G%d" % (b, g)
def check_id(fam, t, g): return "Skyy_Cook_%s_Check_T%d_G%d" % (fam, t, g)
def dish_id(dish, g): return "Skyy_Cook_%s_G%d" % (dish, g)

files = {}
G_EFFECTS, G_INTER, G_ITEMS = {}, {}, {}
for b in BASES:
    for g in range(1, GEN_MAX + 1):
        i = eff_id(b, g)
        G_EFFECTS[i] = scale_effect(b, g)
        files["Server/Entity/Effects/SkyyCook/%s.json" % i] = json.dumps(G_EFFECTS[i], indent=2)

# ---- family checks: rank = (strength, duration, tier, grade), vanilla Grade 0 members included
def strength(fam, e):
    if fam == "HealthRegen": return e["StatModifiers"]["Health"]
    if fam == "Meat": return e["RawStatModifiers"]["Health"][0]["Amount"]
    return e["RawStatModifiers"]["Stamina"][0]["Amount"]
max_clears = 0
for fam in FAMILIES:
    members = []
    for t in (1, 2, 3):
        for g in range(0, GEN_MAX + 1):
            e = scale_effect("%s_Buff_T%d" % (fam, t), g)
            members.append(((round(strength(fam, e), 6), round(e["Duration"], 4), t, g), eff_id("%s_Buff_T%d" % (fam, t), g), t, g))
    members.sort()
    keys = [m[0] for m in members]
    assert len(set(keys)) == len(keys)
    for idx, (key, eid, t, g) in enumerate(members):
        if g == 0: continue
        above = [m[1] for m in members[idx + 1:]]
        below = [m[1] for m in members[:idx]]
        serial = {"Type": "Serial", "Interactions": [{"Type": "ClearEntityEffect", "EntityEffectId": x} for x in below] +
                  [{"Type": "ApplyEffect", "EffectId": eid}]}
        max_clears = max(max_clears, len(below))
        node = serial if not above else {"Type": "EffectCondition", "EntityEffectIds": above, "Match": "None", "Next": serial,
                                         "Failed": {"Type": "Simple", "RunTime": 0}}
        cid = check_id(fam, t, g)
        G_INTER[cid] = node
        files["Server/Item/Interactions/SkyyCook/%s.json" % cid] = json.dumps(node, indent=2)

# ---- graded dishes
QORDER = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
for q in QORDER: assert q in V_QUAL, "vanilla quality missing: " + q
def grade_quality(g): return "Uncommon" if g <= 2 else ("Rare" if g <= 5 else ("Epic" if g <= 8 else "Legendary"))
ROMAN = {1: "I", 2: "II", 3: "III"}
def pct_s(v): return ("%.1f" % v).rstrip("0").rstrip(".")
def num_s(v): return ("%.3f" % v).rstrip("0").rstrip(".")
def mmss(sec):
    s = int(round(sec)); return "%d:%02d" % (s // 60, s % 60)
DISH_TIER, DISH_NAME, DISH_FX = {}, {}, {}
lang = []
W = '<color is="#ffffff">%s</color>'
for dish in DISHES:
    if dish not in V_ITEMS: raise SystemExit("vanilla dish missing: " + dish)
    v = rd(V_ITEMS[dish])
    sec = (v.get("Interactions") or {}).get("Secondary")
    m = re.match(r"^Root_Secondary_Consume_Food_T([123])$", str(sec))
    if v.get("Parent") != "Template_Food" or not m:
        raise SystemExit("self-check 4: %s is no longer a Template_Food dish with a T1-T3 eat root (%s, %s)" % (dish, v.get("Parent"), sec))
    DISH_TIER[dish] = int(m.group(1))
    DISH_NAME[dish] = VLANG.get("items.%s.name" % dish) or dish
    fx = []
    for e in v["InteractionVars"]["Effect"]["Interactions"]:
        if isinstance(e, dict) and e.get("Type") == "ApplyEffect" and e.get("EffectId") in INSTANT and len(e) == 2:
            fx.append(("I", e["EffectId"]))
            continue
        mm = re.match(r"^(HealthRegen|Meat|FruitVeggie)_TierCheck_T([123])$", str(e)) if isinstance(e, str) else None
        if not mm:
            raise SystemExit("self-check 4: unexpected entry in %s's eat chain: %s" % (dish, json.dumps(e)))
        fx.append(("F", mm.group(1), int(mm.group(2))))
    if not fx or fx[0][0] != "I":
        raise SystemExit("self-check 4: %s's eat chain does not start with an instant heal" % dish)
    DISH_FX[dish] = fx
    for g in range(1, GEN_MAX + 1):
        gid = dish_id(dish, g)
        o = copy.deepcopy(v)
        o.pop("Recipe", None)
        o["TranslationProperties"] = {"Name": "server.items.%s.name" % gid, "Description": "server.items.%s.description" % gid}
        vq = v.get("Quality", "Common")
        o["Quality"] = vq if (vq in QORDER and QORDER.index(vq) >= QORDER.index(grade_quality(g))) else grade_quality(g)
        chain = []
        bullets, dur = [], 0.0
        heal = None
        for f in fx:
            if f[0] == "I":
                chain.append({"Type": "ApplyEffect", "EffectId": eff_id(f[1], g)})
                heal = scale_effect(f[1], g)["StatModifiers"]["Health"]
            else:
                fam, k = f[1], f[2]
                chain.append(check_id(fam, k, g))
                e = scale_effect("%s_Buff_T%d" % (fam, k), g)
                dur = max(dur, e["Duration"])
                if fam == "HealthRegen":
                    bullets.append("• " + W % ("Health Regen " + ROMAN[k]) + " (%s%% health every %s s)" % (pct_s(e["StatModifiers"]["Health"]), pct_s(e["DamageCalculatorCooldown"])))
                elif fam == "Meat":
                    res = e.get("DamageResistance", {}).get("Physical", [{}])[0].get("Amount")
                    bullets.append("• " + W % ("Health Boost " + ROMAN[k]) + " (+%s%% max health%s)" % (
                        pct_s((e["RawStatModifiers"]["Health"][0]["Amount"] - 1.0) * 100.0),
                        (", %s%% less physical and projectile damage" % pct_s(res * 100.0)) if res else ""))
                else:
                    st = e.get("StatModifiers", {}).get("Stamina")
                    bullets.append("• " + W % ("Stamina Boost " + ROMAN[k]) + " (+%s%% max stamina%s)" % (
                        pct_s((e["RawStatModifiers"]["Stamina"][0]["Amount"] - 1.0) * 100.0),
                        (", +%s stamina every %s s" % (num_s(st), pct_s(e["DamageCalculatorCooldown"]))) if st else ""))
        ev = dict(v["InteractionVars"]["Effect"])
        ev["Interactions"] = chain
        o["InteractionVars"]["Effect"] = ev
        G_ITEMS[gid] = o
        files["Server/Item/Items/SkyyCook/%s.json" % gid] = json.dumps(o, indent=2)
        name = "%s (Grade %d)" % (DISH_NAME[dish], g)
        if g <= 10:   # 0.1.4: the old "cooked at Cooking %d or higher" ignored the tree (Master Chef gives Grade 2 at Cooking 10-19)
            head = "Grade %d food - Cooking %d, or sooner with Cooking tree bonuses." % (g, g * 10)
        else:
            head = "Grade %d food - only a Cooking skill tree bonus reaches it." % g
        head += " Heal and buffs " + W % ("x%.2f" % SF(g)) + " stronger, buffs last " + W % ("x%.2f" % DF(g)) + " longer."
        body = "Instantly restores " + W % (pct_s(heal) + "%") + " health"
        if bullets:
            body += " and grants:\\n\\n" + "\\n".join(bullets) + "\\n\\nDuration: " + W % mmss(dur)
        else:
            body += "."
        desc = head + "\\n\\n" + body
        for pre in ("items.", "server.items."):
            lang.append("%s%s.name=%s" % (pre, gid, name))
            lang.append("%s%s.description=%s" % (pre, gid, desc))

# ---- Cooking Bench recipes for the 3 Campfire dishes (vanilla Variant-recipe shape, Ingredient_Life_Essence_Wheat.json)
BENCH = rd(V_ITEMS["Bench_Cooking"])
BENCH_CATS = [c["Id"] for c in BENCH["BlockType"]["Bench"]["Categories"]]
assert BENCH["BlockType"]["Bench"]["Id"] == "Cookingbench" and BENCH["BlockType"]["Bench"]["Type"] == "Crafting", "Cooking Bench changed"
VARIANTS = [   # (recipe item, output dish, inputs) - Campfire inputs + 1 Fuel (Cooking spec 3.2, [SKYY?] fuel cost)
    ("Skyy_Cook_Recipe_Wildmeat", "Food_Wildmeat_Cooked", [("R", "Meats", 1), ("R", "Fuel", 1)]),
    ("Skyy_Cook_Recipe_Fish", "Food_Fish_Grilled", [("I", "Food_Fish_Raw", 1), ("R", "Fuel", 1)]),
    ("Skyy_Cook_Recipe_Vegetable", "Food_Vegetable_Cooked", [("R", "Vegetables", 1), ("R", "Fuel", 1)]),
]
for rid, outd, ins in VARIANTS:
    v = rd(V_ITEMS[outd])
    camp = v.get("Recipe") or {}
    assert [b.get("Id") for b in camp.get("BenchRequirement", [])] == ["Campfire"], "%s is no longer a Campfire recipe" % outd
    node = {
        "TranslationProperties": {"Name": "server.items.%s.name" % outd, "Description": "server.items.%s.description" % outd},
        "Variant": True,
        "Parent": outd,
        "Icon": v["Icon"],
        "Recipe": {
            "TimeSeconds": camp.get("TimeSeconds", 2),
            "Input": [({"ResourceTypeId": x, "Quantity": q} if k == "R" else {"ItemId": x, "Quantity": q}) for k, x, q in ins],
            "Output": [{"ItemId": outd, "Quantity": 1}],
            "BenchRequirement": [{"Type": "Crafting", "Id": "Cookingbench", "Categories": ["Prepared"]}],
            "OutputQuantity": 1,
        },
    }
    G_ITEMS[rid] = node
    files["Server/Item/Items/SkyyCook/Recipes/%s.json" % rid] = json.dumps(node, indent=2)

# =====================================================================================================================
# BUILD-TIME SELF-CHECK: every generated item / interaction references ids that exist
# =====================================================================================================================
errs = []
def need(kind, i, where):
    pools = {"effect": (V_EFFECTS, G_EFFECTS), "inter": (V_INTER, G_INTER), "root": (V_ROOTS, {}), "item": (V_ITEMS, G_ITEMS)}[kind]
    if not isinstance(i, str) or (i not in pools[0] and i not in pools[1]):
        errs.append("%s: unknown %s id %r" % (where, kind, i))
def walk_inter(node, where):
    """an interaction reference: a string id or an inline interaction object (vanilla item / interaction JSON shape)"""
    if isinstance(node, str):
        need("inter", node, where); return
    if not isinstance(node, dict):
        errs.append("%s: unexpected interaction node %r" % (where, node)); return
    for k, v in node.items():
        if k == "Parent": need("inter", v, where)
        elif k in ("EffectId", "EntityEffectId"): need("effect", v, where)
        elif k == "EntityEffectIds":
            for x in v: need("effect", x, where)
        elif k == "Interactions":
            for x in v: walk_inter(x, where)
        elif k in ("Next", "Failed"):
            if isinstance(v, str): need("inter", v, where)
            elif isinstance(v, dict) and ("Type" in v or "Parent" in v): walk_inter(v, where)
            elif isinstance(v, dict):
                for tk, tv in v.items(): walk_inter(tv, where)   # Charging: {"2.5": {...}}
def need_common(path, where):
    if path and "Common/" + path not in V_COMMON: errs.append("%s: missing file Common/%s" % (where, path))
for cid, node in G_INTER.items():
    walk_inter(node, "interaction " + cid)
for iid, node in G_ITEMS.items():
    need("item", node.get("Parent"), "item " + iid)
    for typ, root in (node.get("Interactions") or {}).items():
        if isinstance(root, str): need("root", root, "item %s Interactions.%s" % (iid, typ))
        else: walk_inter(root, "item %s Interactions.%s" % (iid, typ))
    for var, vv in (node.get("InteractionVars") or {}).items():
        for x in vv.get("Interactions", []): walk_inter(x, "item %s InteractionVars.%s" % (iid, var))
    need_common(node.get("Icon"), "item " + iid)
    bt = node.get("BlockType") or {}
    need_common(bt.get("CustomModel"), "item " + iid)
    for tx in bt.get("CustomModelTexture", []): need_common(tx.get("Texture"), "item " + iid)
    if iid.startswith("Skyy_Cook_Food_"):
        if "Recipe" in node: errs.append("graded dish %s has a Recipe (self-check 3)" % iid)
        for suf in ("name", "description"):
            for pre in ("items.", "server.items."):
                if not any(l.startswith("%s%s.%s=" % (pre, iid, suf)) for l in lang): errs.append("no lang line %s%s.%s" % (pre, iid, suf))
    else:
        rc = node["Recipe"]
        outs = [o["ItemId"] for o in rc["Output"]]
        if len(outs) != 1 or outs[0] not in DISHES: errs.append("recipe variant %s must output one graded dish (self-check 3)" % iid)
        for inp in rc["Input"]:
            if "ItemId" in inp: need("item", inp["ItemId"], "recipe " + iid)
            elif inp.get("ResourceTypeId") not in V_RTYPES: errs.append("recipe %s: unknown resource type %r" % (iid, inp.get("ResourceTypeId")))
        for br in rc["BenchRequirement"]:
            if br["Id"] != "Cookingbench" or any(c not in BENCH_CATS for c in br.get("Categories", [])): errs.append("recipe %s: bad bench %r" % (iid, br))
for kind, gen, van in (("effect", G_EFFECTS, V_EFFECTS), ("interaction", G_INTER, V_INTER), ("item", G_ITEMS, V_ITEMS)):
    for i in gen:
        if not i.startswith("Skyy_Cook_") or i in van: errs.append("generated %s id %s collides with vanilla or lacks the Skyy_Cook_ prefix (self-check 5)" % (kind, i))
if errs:
    raise SystemExit("ASSET SELF-CHECK FAILED (%d):\n  " % len(errs) + "\n  ".join(errs[:60]))
N_EFF, N_INT, N_DISH, N_VAR = len(G_EFFECTS), len(G_INTER), len([i for i in G_ITEMS if i.startswith("Skyy_Cook_Food_")]), len(VARIANTS)
assert (N_EFF, N_INT, N_DISH, N_VAR) == (13 * GEN_MAX, 9 * GEN_MAX, 15 * GEN_MAX, 3), (N_EFF, N_INT, N_DISH, N_VAR)
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
print("assets: %d effects + %d family checks + %d graded dishes + %d recipe variants = %d JSON, %d lang lines; longest check clears %d; self-check OK"
      % (N_EFF, N_INT, N_DISH, N_VAR, N_EFF + N_INT + N_DISH + N_VAR, len(lang), max_clears))
print("grade factors (strength / duration): " + ", ".join("G%d x%.2f/x%.2f" % (g, SF(g), DF(g)) for g in range(0, GEN_MAX + 1)))
# 0.1.4 self-check: every generated effect is the vanilla one with ONLY its strength fields x S(g) and its Duration x D(g) - no cap binds
_capped = []
for b in BASES:
    d0 = VBASE[b]
    for g in range(1, GEN_MAX + 1):
        e, Sg, Dg = G_EFFECTS[eff_id(b, g)], SF(g), DF(g)
        want = copy.deepcopy(d0)
        for k, v in want.get("StatModifiers", {}).items(): want["StatModifiers"][k] = r4(v * Sg)
        for stat, lst in want.get("RawStatModifiers", {}).items():
            for m in lst: m["Amount"] = r4(1.0 + (m["Amount"] - 1.0) * Sg) if m.get("CalculationType") == "Multiplicative" else r4(m["Amount"] * Sg)
        for typ, lst in want.get("DamageResistance", {}).items():
            for m in lst: m["Amount"] = r4(m["Amount"] * Sg)
        if d0.get("Duration", 0) > 0.5: want["Duration"] = float("%.2f" % (d0["Duration"] * Dg))
        if e != want: _capped.append("%s G%d" % (b, g))
if _capped:
    raise SystemExit("self-check 0.1.4: these effects are not exactly vanilla x S(g) / x D(g) (a cap binds?): %s" % _capped)
print("0.1.4: all %d graded effects = vanilla strength x (1 + 0.32 x Grade), Duration x 2^(Grade/5); no cap binds" % len(G_EFFECTS))

# =====================================================================================================================
# XP TABLE (orchestrator decision 2: level 50 in about Alchemy's time, ~27 focused hours on the best route)
# =====================================================================================================================
# Model: a craft's XP follows the raw gathering effort in its whole ingredient chain ("chain raw", in item units weighted by how
# slow they are to get). A finished DISH pays 85 % of its chain's raw value x K (x1.25 for recipes that need recipe knowledge:
# pies, Caesar salad); an INGREDIENT craft (flour, dough, salt, spices, cheese, raw fish) pays 15 % of its own direct raw inputs x K.
# So a whole chain pays ~K per raw unit and no single step is a shortcut (flour spam pays 15 %). Throughput assumption = the Alchemy
# spec's 1,800 gathered items per hour with bags (UNVERIFIED in game). K is chosen so the meat-pie route lands at ~27 h to level 50.
K_XP, DISH_SHARE, ING_SHARE, KNOW_BONUS, ITEMS_PER_HOUR = 950.0, 0.85, 0.15, 1.25, 1800.0
LV50 = 55172425   # SkyySkills table, levels 1-50 (0.3.2 asserts it)
W_ITEM = {"Ingredient_Stick": 0.5, "*Deco_Tankard_State_Filled_Water": 0.5, "Food_Egg": 2.0}
W_RT = {"Fuel": 0.5, "Meats": 1.5, "Milk_Bucket": 3.0, "Fish": 2.0, "Fish_Uncommon": 2.0, "Fish_Rare": 2.0, "Fish_Epic": 2.0, "Fish_Legendary": 2.0}
def recipe_of(item_id):
    r = rd(V_ITEMS[item_id]).get("Recipe")
    return r
def primary(item_id, r):
    po = r.get("PrimaryOutput")   # e.g. Food_Fish_Raw_Uncommon (Variant) -> Food_Fish_Raw x2
    if isinstance(po, dict) and po.get("ItemId"): return po["ItemId"], int(po.get("Quantity", r.get("OutputQuantity", 1)) or 1)
    outs = r.get("Output") or []
    if outs: return outs[0]["ItemId"], int(outs[0].get("Quantity", r.get("OutputQuantity", 1)) or 1)
    return item_id, int(r.get("OutputQuantity", 1) or 1)
COOK = {}   # output id -> (inputs [(kind, id, qty)], out qty, seconds, knowledge)
for iid, path in V_ITEMS.items():
    try: r = rd(path).get("Recipe")
    except Exception: continue
    if not r or not any(b.get("Id") == "Cookingbench" for b in r.get("BenchRequirement") or []): continue
    out, q = primary(iid, r)
    if out in COOK and out != iid: continue      # Food_Fish_Raw_Rare etc. -> keep the base recipe of Food_Fish_Raw
    ins = [(("R", i["ResourceTypeId"]) if i.get("ResourceTypeId") else ("I", i["ItemId"])) + (int(i.get("Quantity", 1) or 1),) for i in r.get("Input", [])]
    COOK[out] = (ins, q, float(r.get("TimeSeconds", 0) or 0), bool(r.get("KnowledgeRequired", False)))
for rid, outd, ins in VARIANTS:
    COOK[outd] = ([(k, x, q) for k, x, q in ins], 1, float(G_ITEMS[rid]["Recipe"]["TimeSeconds"]), False)
for dsh in DISHES: assert dsh in COOK, "no Cookingbench recipe makes " + dsh
def weight(kind, i):
    return W_RT.get(i, 1.0) if kind == "R" else W_ITEM.get(i, 1.0)
_memo = {}
def chain_raw(out, depth=0):
    if out in _memo: return _memo[out]
    assert depth < 8, "recipe cycle at " + out
    ins, q, _, _ = COOK[out]
    tot = 0.0
    for kind, i, n in ins:
        tot += (chain_raw(i, depth + 1) if (kind == "I" and i in COOK and i != out) else weight(kind, i)) * n
    _memo[out] = tot / q
    return _memo[out]
def direct_raw(out):
    ins, q, _, _ = COOK[out]
    return sum(weight(k, i) * n for k, i, n in ins if not (k == "I" and i in COOK))
def rnd_to(v, step): return int(step * round(v / step))
XP = {}
for out in sorted(COOK):
    if out in DISHES:
        XP[out] = rnd_to(K_XP * DISH_SHARE * chain_raw(out) * (KNOW_BONUS if COOK[out][3] else 1.0), 50)
    else:
        XP[out] = rnd_to(K_XP * ING_SHARE * direct_raw(out), 5)
XP_DEFAULT = 1000   # any other Cookingbench output (modded content); the server log names it once
# ---- 0.1.5 (Skyy 2026-10-04): "the easier to craft the less xp. the harder to craft the more." The loop above is the 0.1-0.1.4 table
# (kept as XP_OLD: CookTblMig rewrites only lines still holding these texts). A DISH now pays chain raw x K x a DIFFICULTY SHARE (percent):
#   DIFF_BASE + DIFF_STEP per extra distinct craft in its chain + DIFF_KNOW for recipe knowledge + DIFF_BENCH[class] + DIFF_TIER per
#   ingredient tier above 1. Ingredient crafts keep ING_SHARE of their own inputs. Edit the weights in tools/cooking_0_1_5_patch.py.
XP_OLD = dict(XP)
XP_014 = {'Food_Bread': 12900, 'Food_Cheese': 430, 'Food_Fish_Grilled': 2000, 'Food_Fish_Raw': 285, 'Food_Kebab_Fruit': 3650, 'Food_Kebab_Meat': 5250, 'Food_Kebab_Mushroom': 2850, 'Food_Kebab_Vegetable': 3650, 'Food_Pie_Apple': 25250, 'Food_Pie_Meat': 23900, 'Food_Pie_Pumpkin': 23200, 'Food_Popcorn': 3000, 'Food_Salad_Berry': 4850, 'Food_Salad_Caesar': 11800, 'Food_Salad_Mushroom': 3250, 'Food_Vegetable_Cooked': 1200, 'Food_Wildmeat_Cooked': 1600, 'Ingredient_Dough': 640, 'Ingredient_Flour': 1425, 'Ingredient_Salt': 140, 'Ingredient_Spices': 855}
assert XP_OLD == XP_014, "0.1.5: the 0.1-0.1.4 table changed under the patch (Assets.zip?) - re-check the migration's old texts: %s" % XP_OLD
DIFF_BASE, DIFF_STEP, DIFF_KNOW, DIFF_TIER = 20, 15, 25, 5
DIFF_BENCH = {"Campfire": 0, "Prepared": 5, "Baked": 10}   # the Cooking Bench has no tier levels: Campfire dish < Prepared < Baked (fuel)
# ingredient tiers (docs/answered/economy.md 2026-10-04 Bazaar progression: crops T1 Wheat / Carrot / Lettuce / Potato, T2 Corn ..., T4
# Pumpkin; Apple from a T2 fruit tree; Milk needs livestock); everything else (resource groups, eggs, salt rock, flowers, berries) is T1
ING_TIER = {"Plant_Crop_Corn_Item": 2, "Plant_Crop_Pumpkin_Item": 4, "Plant_Fruit_Apple": 2, "Milk_Bucket": 2}
for _i in ING_TIER:
    assert _i in V_ITEMS or _i in V_RTYPES, "0.1.5: ingredient tier id %s is not in Assets.zip" % _i
STOPGAP_014 = {'Food_Kebab_Vegetable': 1800, 'Food_Kebab_Fruit': 1800, 'Food_Kebab_Mushroom': 1400, 'Food_Kebab_Meat': 2600}    # Skyy's live rows 2026-10-04 (replaceable defaults for CookTblMig)
def bench_class(out):
    if out in [v[1] for v in VARIANTS]: return "Campfire"
    cats = [c for b in (rd(V_ITEMS[out])["Recipe"].get("BenchRequirement") or []) if b.get("Id") == "Cookingbench" for c in (b.get("Categories") or [])]
    assert len(cats) == 1 and cats[0] in DIFF_BENCH, "0.1.5: %s has Cooking Bench categories %s" % (out, cats)
    return cats[0]
def chain_crafts(out, acc=None):
    acc = set() if acc is None else acc
    acc.add(out)
    for kind, i, n in COOK[out][0]:
        if kind == "I" and i in COOK and i != out: chain_crafts(i, acc)
    return acc
def chain_tier(out):
    t = 1
    for kind, i, n in COOK[out][0]:
        t = max(t, chain_tier(i) if (kind == "I" and i in COOK and i != out) else ING_TIER.get(i, 1))
    return t
def diff_share(out):
    return (DIFF_BASE + DIFF_STEP * (len(chain_crafts(out)) - 1) + (DIFF_KNOW if COOK[out][3] else 0) + DIFF_BENCH[bench_class(out)]
            + DIFF_TIER * (chain_tier(out) - 1))
DIFF = {}
for out in DISHES:
    DIFF[out] = diff_share(out)
    XP[out] = rnd_to(K_XP * DIFF[out] * chain_raw(out) / 100.0, 50)
XP_015 = {'Food_Bread': 9100, 'Food_Cheese': 430, 'Food_Fish_Grilled': 850, 'Food_Fish_Raw': 285, 'Food_Kebab_Fruit': 1050, 'Food_Kebab_Meat': 1550, 'Food_Kebab_Mushroom': 850, 'Food_Kebab_Vegetable': 1050, 'Food_Pie_Apple': 24950, 'Food_Pie_Meat': 25900, 'Food_Pie_Pumpkin': 25150, 'Food_Popcorn': 1750, 'Food_Salad_Berry': 1400, 'Food_Salad_Caesar': 11100, 'Food_Salad_Mushroom': 950, 'Food_Vegetable_Cooked': 300, 'Food_Wildmeat_Cooked': 400, 'Ingredient_Dough': 640, 'Ingredient_Flour': 1425, 'Ingredient_Salt': 140, 'Ingredient_Spices': 855}
assert XP == XP_015, "0.1.5: the difficulty table is not the one the patch documents: %s" % XP
print("0.1.5 XP per craft by difficulty (share %, old -> new): " + ", ".join("%s %d%% %d -> %d" % (d, DIFF[d], XP_OLD[d], XP[d]) for d in sorted(DISHES, key=lambda d: XP[d])))
# Skyy's rule as checks: easy (one craft, no knowledge) < multi-step (3+ crafts); skewers clearly under the 2026-10-04 stopgap rows
_easy = [d for d in DISHES if len(chain_crafts(d)) == 1 and not COOK[d][3]]
_hard = [d for d in DISHES if len(chain_crafts(d)) >= 3]
assert _easy and _hard and max(XP[d] for d in _easy) < min(XP[d] for d in _hard), "0.1.5: an easy dish pays as much as a multi-step one"
assert all(XP[d] <= 0.65 * STOPGAP_014[d] for d in STOPGAP_014), "0.1.5: skewers must pay clearly less than the 2026-10-04 stopgap rows"
assert all(XP[d] < XP_OLD[d] for d in _easy), "0.1.5: every easy dish must pay less than in 0.1.4"
assert all(XP[i] == XP_OLD[i] for i in XP if i not in DISHES), "0.1.5: ingredient crafts keep their 0.1.4 values"
# ---- 0.1.6 (Skyy 2026-10-05 LOCKED): "Flour should go way down. The less it takes to craft, and the earlier the items are to get, the less
# xp it should give you". An INGREDIENT craft now pays its own direct raw inputs x K x a small difficulty share (PER MILLE):
#   ING_BASE + ING_STEP per earlier distinct craft in its chain + ING_KIND per extra distinct input + ING_TIERW per ingredient tier above 1
# (the dish shares' idea at ingredient scale; the dish table above is unchanged). Edit the weights in tools/cooking_0_1_6_patch.py.
ING_BASE, ING_STEP, ING_KIND, ING_TIERW = 15, 15, 5, 15
INGS = sorted(o for o in COOK if o not in DISHES)
assert INGS == ['Food_Cheese', 'Food_Fish_Raw', 'Ingredient_Dough', 'Ingredient_Flour', 'Ingredient_Salt', 'Ingredient_Spices'], "0.1.6: the ingredient crafts changed under the patch (Assets.zip?): %s" % INGS
def ing_kinds(out): return len(set((k, i) for k, i, n in COOK[out][0]))
def ing_share(out):
    return ING_BASE + ING_STEP * (len(chain_crafts(out)) - 1) + ING_KIND * (ing_kinds(out) - 1) + ING_TIERW * (chain_tier(out) - 1)
ING_PM = {}
for out in INGS:
    ING_PM[out] = ing_share(out)
    XP[out] = rnd_to(K_XP * ING_PM[out] * direct_raw(out) / 1000.0, 5)
XP_016 = {'Food_Bread': 9100, 'Food_Cheese': 85, 'Food_Fish_Grilled': 850, 'Food_Fish_Raw': 30, 'Food_Kebab_Fruit': 1050, 'Food_Kebab_Meat': 1550, 'Food_Kebab_Mushroom': 850, 'Food_Kebab_Vegetable': 1050, 'Food_Pie_Apple': 24950, 'Food_Pie_Meat': 25900, 'Food_Pie_Pumpkin': 25150, 'Food_Popcorn': 1750, 'Food_Salad_Berry': 1400, 'Food_Salad_Caesar': 11100, 'Food_Salad_Mushroom': 950, 'Food_Vegetable_Cooked': 300, 'Food_Wildmeat_Cooked': 400, 'Ingredient_Dough': 170, 'Ingredient_Flour': 140, 'Ingredient_Salt': 15, 'Ingredient_Spices': 115}
assert XP == XP_016, "0.1.6: the ingredient table is not the one the patch documents: %s" % XP
print("0.1.6 ingredient XP by difficulty (per mille, 0.1.5 -> 0.1.6): " + ", ".join("%s %d %d -> %d" % (i, ING_PM[i], XP_015[i], XP[i]) for i in sorted(INGS, key=lambda i: XP[i])))
# Skyy's rule as checks
_multi = [d for d in DISHES if len(chain_crafts(d)) >= 2]
assert all(XP[d] == XP_015[d] for d in DISHES), "0.1.6: the dish table must stay the 0.1.5 one"
assert all(5 <= XP[i] < XP_015[i] for i in INGS), "0.1.6: every ingredient pays less than in 0.1.5 (and still something)"
assert max(XP[i] for i in INGS) < min(XP[d] for d in _multi), "0.1.6: every ingredient must pay less than the cheapest multi-step dish"
assert 0.10 * XP["Food_Kebab_Vegetable"] <= XP["Ingredient_Flour"] <= 0.20 * XP["Food_Kebab_Vegetable"], "0.1.6: flour = 10-20% of a Vegetable Skewer"
assert all(XP[i] / direct_raw(i) > XP["Ingredient_Flour"] / direct_raw("Ingredient_Flour") for i in INGS if ING_PM[i] > ING_BASE), \
    "0.1.6: a later step / tier / more inputs must pay more per raw item than flour"
assert XP["Ingredient_Dough"] > XP["Ingredient_Flour"], "0.1.6: dough (needs flour) pays more than flour"
# route estimate: one meat pie with its whole chain (flour, dough, spices, 1/5 of a salt craft)
def chain_xp(out, depth=0):
    ins, q, _, _ = COOK[out]
    x = XP[out] / float(q)
    for kind, i, n in ins:
        if kind == "I" and i in COOK and i != out: x += chain_xp(i, depth + 1) * n
    return x
pie_xp, pie_raw = chain_xp("Food_Pie_Meat"), chain_raw("Food_Pie_Meat")
xph = ITEMS_PER_HOUR / pie_raw * pie_xp
HOURS_50 = LV50 / xph
kebab_h = LV50 / (ITEMS_PER_HOUR / chain_raw("Food_Kebab_Vegetable") * chain_xp("Food_Kebab_Vegetable"))
print("XP table (base XP per finished craft): " + ", ".join("%s=%d" % (k, XP[k]) for k in sorted(XP)))
print("pace: meat pie chain = %.1f raw units -> %d XP (%.0f XP/unit); ~%.0f XP/h at %d items/h -> Cooking 50 in ~%.1f h (veg kebabs only: ~%.1f h)"
      % (pie_raw, pie_xp, pie_xp / pie_raw, xph, ITEMS_PER_HOUR, HOURS_50, kebab_h))
assert 25.0 <= HOURS_50 <= 30.0, "decision 2: level 50 must take 25-30 focused hours on the best route (Alchemy's pace), model says %.1f" % HOURS_50
# 0.1.6 route check: spamming one craft (with its whole chain) from gathered items - no ingredient may be a faster way to level than any dish
RATE = dict((o, ITEMS_PER_HOUR / chain_raw(o) * chain_xp(o)) for o in COOK)
_best = max(RATE, key=lambda o: RATE[o])
assert _best in DISHES, "0.1.6: the fastest route must be a dish, not %s" % _best
assert max(RATE[i] for i in INGS) < min(RATE[d] for d in DISHES), "0.1.6: an ingredient spam route levels as fast as a dish"
print("0.1.6 route check (base XP/h from gathered items): best %s %.0f; slowest dish %s %.0f; fastest ingredient %s %.0f (Cooking 50 by it: ~%.0f h)"
      % (_best, RATE[_best], min(DISHES, key=lambda d: RATE[d]), min(RATE[d] for d in DISHES), max(INGS, key=lambda i: RATE[i]),
         max(RATE[i] for i in INGS), LV50 / max(RATE[i] for i in INGS)))
# bench-limited peak (one CraftingManager queue per player): XP per recipe second x 60 - stays under SkyySkills' addxp caps
PEAK = max(XP[o] / max(COOK[o][2], 1.0) * 60.0 for o in COOK)
MAX_PER_MIN = int(math.ceil(PEAK * 2.0 / 100000.0) * 100000)   # 2x the legit bench peak, rounded up to 100k
# 0.1.5: the difficulty table lowers the peak (Caesar 11,100 XP per 1 s craft -> 1.4M); the 0.1.4 default 1,500,000 is kept so no second
# setting changes (it still covers 2x the peak)
assert MAX_PER_MIN <= 1500000, "0.1.5: the bench peak grew past the 0.1.4 maxXpPerMinute default - re-think the pin"
MAX_PER_MIN = 1500000
assert max(XP.values()) <= 400000 and MAX_PER_MIN <= 3000000, "XP must stay under skill:fn:addxp's 500k/call and 3M/min caps"
print("bench peak %.0f base XP/min -> default maxXpPerMinute=%d" % (PEAK, MAX_PER_MIN))
# self-check: craft/uncraft loop - no recipe anywhere takes a cooking output and gives back one of that output's own inputs
ALLREC = []
for iid, path in V_ITEMS.items():
    try: r = rd(path).get("Recipe")
    except Exception: continue
    if r: ALLREC.append((iid, r))
for n in ANAMES:
    if n.startswith("Server/Item/Recipes/") and n.endswith(".json"):
        try: ALLREC.append((os.path.basename(n)[:-5], rd(n)))
        except Exception: pass
for out, (ins, q, _, _) in COOK.items():
    if XP.get(out, 0) <= 0: continue
    mine = set(i for k, i, n in ins if k == "I")
    for rid, r in ALLREC:
        rin = set(i.get("ItemId") for i in r.get("Input", []) if i.get("ItemId"))
        if out not in rin: continue
        routs = set(o.get("ItemId") for o in (r.get("Output") or []))
        if isinstance(r.get("PrimaryOutput"), dict): routs.add(r["PrimaryOutput"].get("ItemId"))
        if not routs: routs = {rid}
        if routs & mine:
            raise SystemExit("self-check: craft/uncraft loop - %s (pays %d XP) feeds %s which returns %s" % (out, XP[out], rid, sorted(routs & mine)))

# =====================================================================================================================
# 0.1.1 CAMPFIRE ACCESSORY (Skyy 2026-09-24): /craft (SkyySacks) cooks the Campfire dishes instantly through the Campfire accessory -
# an emergency cook: the Cooking-skill part of the Grade bonus x campfire.buffFactor, Cooking XP x campfire.xpFactor. Reuses the
# Grade 1-12 assets generated above (no new asset set).
# =====================================================================================================================
# 0.1.3 (Skyy 2026-10-01, "id half the amount of cooking xp you get from the campfire"): CAMP_XP_DEF 0.5 -> 0.25. Keep this exact one-line
# form: SkyySacks' and SkyyAccessories' build checks read the two numbers from it.
CAMP_BUFF_DEF, CAMP_XP_DEF = 0.75, 0.25
CAMP_XP_OLD = 0.5            # the 0.1.1 / 0.1.2 default - CookMig updates a line that still holds exactly repr(CAMP_XP_OLD)
# 0.1.3 run-once marker of the campfire.xpFactor update (CookMig): a comment line on its own, plain ASCII, no '=' (so the kit never takes it
# for a #key=value template line); CookMig looks for CAMP_MARK_ID in COMMENT lines only. The default text and the 0.1 append block carry it.
CAMP_MARK_ID = "SkyyCooking 0.1.3 campfire XP"
CAMP_MARK = ("# %s (Skyy 2026-10-01): campfire accessory dishes pay a quarter of the Cooking Bench XP - campfire.xpFactor default %s, was %s"
             % (CAMP_MARK_ID, repr(CAMP_XP_DEF), repr(CAMP_XP_OLD)))
assert all(32 <= ord(_c) < 127 for _c in CAMP_MARK) and "=" not in CAMP_MARK and CAMP_MARK.startswith("# " + CAMP_MARK_ID)
assert repr(CAMP_XP_DEF) == "0.25" and repr(CAMP_XP_OLD) == "0.5"
_camp_found = []
for rid, r in ALLREC:
    if not any(isinstance(b, dict) and b.get("Id") == "Campfire" for b in (r.get("BenchRequirement") or [])): continue
    po = r.get("PrimaryOutput")
    outs = [po["ItemId"]] if isinstance(po, dict) and po.get("ItemId") else [o.get("ItemId") for o in (r.get("Output") or []) if o.get("ItemId")]
    if not outs: outs = [rid]
    for o in outs:
        if o not in _camp_found: _camp_found.append(o)
CAMP_DISHES = [d for d in DISHES if d in _camp_found]
if sorted(CAMP_DISHES) != sorted(_camp_found):
    raise SystemExit("self-check 0.1.1: a vanilla Campfire recipe makes something that is not a graded dish: %s" % sorted(set(_camp_found) - set(CAMP_DISHES)))
if CAMP_DISHES != ["Food_Wildmeat_Cooked", "Food_Fish_Grilled", "Food_Vegetable_Cooked"]:
    raise SystemExit("self-check 0.1.1: the vanilla Campfire recipe list changed (%s) - re-check the docstring, texts and XP" % CAMP_DISHES)
def _bonus(e):
    if e.get("RawStatModifiers"): return list(e["RawStatModifiers"].values())[0][0]["Amount"] - 1.0
    return e["StatModifiers"]["Health"]
for d in CAMP_DISHES:
    if DISH_TIER[d] != 1 or XP.get(d, 0) <= 0:
        raise SystemExit("self-check 0.1.1: campfire dish %s must be a T1 graded dish with Cooking XP (tier %s, xp %s)" % (d, DISH_TIER[d], XP.get(d)))
    for g in range(1, GEN_MAX + 1):
        if dish_id(d, g) not in G_ITEMS: raise SystemExit("self-check 0.1.1: no Grade asset " + dish_id(d, g))
    # its heal and buffs scale by exactly S(g) and its durations by D(g) (no cap binds on T1 numbers), so the strength the mapping compares
    # is the real one
    for f in DISH_FX[d]:
        b = f[1] if f[0] == "I" else "%s_Buff_T%d" % (f[1], f[2])
        e0 = scale_effect(b, 0)
        for g in range(1, GEN_MAX + 1):
            eg = scale_effect(b, g)
            if abs(_bonus(eg) - _bonus(e0) * SF(g)) > 0.0002 or (e0.get("Duration", 0) > 0.5 and abs(eg["Duration"] - e0["Duration"] * DF(g)) > 0.01):
                raise SystemExit("self-check 0.1.1: %s Grade %d of %s hits a cap - the campfire mapping would not be x%.2f" % (b, g, d, SF(g)))
# 0.1.4: campfire.buffFactor works on the STRENGTH part - CM(g) = SF(g) is what the pick compares (CookCfg.MUL holds it for Cook.campGrade)
def CM(g): return SF(g)
def camp_grade(g, f):
    """Python mirror of Cook.campGrade (Java) - the build runs the compiled one against this"""
    g = max(0, min(int(g), GEN_MAX))
    if g <= 0 or f <= 0.0: return 0
    if f >= 1.0: return g
    target = 1.0 + f * (CM(g) - 1.0) + 1e-9
    c = 0
    for k in range(1, g + 1):
        if CM(k) <= target: c = k
    return c
CAMP_TABLE = [camp_grade(g, CAMP_BUFF_DEF) for g in range(GEN_MAX + 1)]
for g, c in enumerate(CAMP_TABLE):
    tg = 1.0 + CAMP_BUFF_DEF * (CM(g) - 1.0)
    assert c <= g and CM(c) <= tg + 1e-9 and (c == g or CM(c + 1) > tg + 1e-9), (g, c)
    assert g == 0 or CAMP_TABLE[g] >= CAMP_TABLE[g - 1], CAMP_TABLE
# with the linear strength curve the pick is floor(buffFactor x bench Grade) ("75% of your Grade, rounded down") for any factor 0..1
for _f in (CAMP_BUFF_DEF, 0.5, 0.25, 0.9, 0.1, 0.33, 0.6, 0.8):
    if [camp_grade(g, _f) for g in range(GEN_MAX + 1)] != [int(math.floor(_f * g + 1e-9)) for g in range(GEN_MAX + 1)]:
        raise SystemExit("self-check 0.1.4: the campfire pick at buffFactor %s is not floor(buffFactor x Grade)" % _f)
if CAMP_TABLE != [0, 0, 1, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9]:
    raise SystemExit("self-check 0.1.4: campfire Grade table changed: %s (update the docstring table)" % CAMP_TABLE)
print("campfire accessory (buffFactor %s, xpFactor %s), bench Grade -> campfire Grade (strength / duration): " % (CAMP_BUFF_DEF, CAMP_XP_DEF) +
      ", ".join("G%d x%.2f -> G%d x%.2f/x%.2f (target x%.2f)" % (g, SF(g), c, SF(c), DF(c), 1.0 + CAMP_BUFF_DEF * (SF(g) - 1.0)) for g, c in enumerate(CAMP_TABLE)))
print("campfire XP per dish: " + ", ".join("%s %d -> %d" % (d, XP[d], int(round(XP[d] * CAMP_XP_DEF))) for d in CAMP_DISHES))
CAMP_LINES = [
    "# Campfire ACCESSORY (SkyyCooking 0.1.1): the /craft page (SkyySacks) cooks " + ", ".join(CAMP_DISHES) + " instantly - an emergency cook.",
    "# campfire.buffFactor = share of the Cooking-skill part of the Grade STRENGTH bonus: the dish comes out at the highest Grade whose",
    "# strength is <= 1 + buffFactor x (the Cooking Bench strength - 1). %s: bench Grade 5 (x%.2f) -> Grade %d (x%.2f), Grade 10 (x%.2f) -> Grade %d (x%.2f). 0..1"
    % (CAMP_BUFF_DEF, SF(5), CAMP_TABLE[5], SF(CAMP_TABLE[5]), SF(10), CAMP_TABLE[10], SF(CAMP_TABLE[10])),
    "campfire.buffFactor=%s" % repr(CAMP_BUFF_DEF),
    CAMP_MARK,
    "# campfire.xpFactor = share of the Cooking XP the same dish pays at a Cooking Bench (its xp.<dish> line). 0..1",
    "campfire.xpFactor=%s" % repr(CAMP_XP_DEF)]
CAMP_BLOCK_TEXT = "\n" + "\n".join(CAMP_LINES) + "\n"

# 0.1.4 (Skyy 2026-10-02, "cooking levels really fast" -> "half ... your cooking xp gain"): the Cooking XP multiplier default 1 -> 0.5
XP_MULT_DEF = 0.5
XP_MULT_OLD = ("1.0", "1")   # the old default texts CookXpMig updates: every generated file since 0.1 says 1.0, the kit's canonical write 1
XP_HELP_LINE = "# multiplies every Cooking XP award (SkyySkills' own global multiplier applies on top)"   # the file's help comment (unchanged)
XP_HELP_ROW = "Multiplies every Cooking XP award. Default 0.5 = half. SkyySkills' XP multiplier applies on top."
# 0.1.4 run-once marker of the xpMultiplier update (CookXpMig): a comment line on its own, plain ASCII, no '=' (so the kit never takes it for
# a #key=value template line); CookXpMig looks for XP_MARK_ID in COMMENT lines only. The 0.1.4 default text carries it.
XP_MARK_ID = "SkyyCooking 0.1.4 Cooking XP"
# 0.1.5 run-once marker of the XP-per-craft update (CookTblMig) + the xp block's help lines: the byte-exact 0.1-0.1.4 text (CookTblMig
# replaces exactly these, 1:1) and the 0.1.5 wording (the default text and the update write it). Plain ASCII, no '='.
XP_HELP_OLD = ["# Base XP per finished craft at the Cooking Bench, keyed by the craft's primary OUTPUT item id (0 = no XP). Pace (decision 2):", '# the meat-pie route reaches Cooking 50 in about 27 focused hours, like Alchemy 50. A dish pays 85% of the raw gathering in its', '# whole ingredient chain x 950 per item (x1.25 for pies and Caesar salad, which need recipe knowledge); an ingredient craft pays 15% of its own inputs.']
XP_HELP_NEW = ["# Base XP per finished craft at the Cooking Bench, keyed by the craft's primary OUTPUT item id (0 = no XP). By difficulty (0.1.5): a dish", '# pays the raw gathering in its whole ingredient chain x 950 per item x a share - 20% + 15% per extra crafting step + 25% recipe', '# knowledge + 5% Prepared / 10% Baked at the Cooking Bench + 5% per ingredient tier above 1. An ingredient craft pays 15% of its own inputs.']
XP_TBL_MARK_ID = 'SkyyCooking 0.1.5 Cooking XP by difficulty'
XP_TBL_MARK = '# SkyyCooking 0.1.5 Cooking XP by difficulty (Skyy 2026-10-04): easier dishes pay less XP, multi-step dishes more - the xp lines still on the old defaults were updated once'
assert XP_HELP_OLD[1] == "# the meat-pie route reaches Cooking 50 in about 27 focused hours, like Alchemy 50. A dish pays 85% of the raw gathering in its"
# 0.1.6 run-once marker of the ingredient XP update (CookIngMig) + the xp block's help lines: the byte-exact 0.1.5 text (XP_HELP_015 = the
# lines CookTblMig writes; CookIngMig replaces exactly these, 1:1) and the 0.1.6 wording (the default text). Plain ASCII, no '='.
XP_HELP_015 = list(XP_HELP_NEW)
XP_HELP_016 = ["# Base XP per finished craft at the Cooking Bench, keyed by the craft's primary OUTPUT item id (0 = no XP). By difficulty (0.1.6): a dish", '# pays the raw gathering in its whole ingredient chain x 950 per item x 20% + 15% per extra crafting step + 25% recipe knowledge + 5% Prepared', '# / 10% Baked + 5% per tier above 1. An ingredient craft pays only 1.5% of its own inputs (+1.5% per earlier step or tier, +0.5% per extra input).']
XP_ING_MARK_ID = 'SkyyCooking 0.1.6 ingredient Cooking XP'
XP_ING_MARK = '# SkyyCooking 0.1.6 ingredient Cooking XP (Skyy 2026-10-05): early, easy ingredients like flour pay little XP - the ingredient xp lines still on the old defaults were updated once'
assert len(XP_HELP_016) == len(XP_HELP_015) and all(a != b for a, b in zip(XP_HELP_015, XP_HELP_016))
assert XP_ING_MARK_ID not in XP_TBL_MARK and XP_TBL_MARK_ID not in XP_ING_MARK and XP_MARK_ID not in XP_ING_MARK
XP_MARK = ("# %s (Skyy 2026-10-02): cooking levelled too fast - every Cooking XP award is halved - xpMultiplier default %s, was 1"
           % (XP_MARK_ID, repr(XP_MULT_DEF)))
assert all(32 <= ord(_c) < 127 for _c in XP_MARK) and "=" not in XP_MARK and XP_MARK.startswith("# " + XP_MARK_ID)
assert CAMP_MARK_ID not in XP_MARK and XP_MARK_ID not in CAMP_MARK and repr(XP_MULT_DEF) == "0.5" and len(XP_HELP_ROW) <= 100

# ---- the generated cooking.properties (written on first run; comments must stay on their own lines)
NODES = [("CGourmet", 25, 0.008, "chance of +1 Grade"), ("CBatch", 20, 0.01, "chance of one extra dish (same Grade, no XP)"),
         ("CFrugal", 10, 0.02, "chance to get one item ingredient back (never Fuel or resource-type inputs)"),
         ("CGrill", 15, 0.02, "chance of +1 Grade on T1 dishes (cooked meat, grilled fish, roast vegetable)"),
         ("CPrep", 10, 0.03, "chance of +1 Grade on T2 dishes (bread, skewers, berry and mushroom salad)"),
         ("CBaker", 10, 0.03, "chance of +1 Grade on T3 dishes (popcorn, pies, Caesar salad)"),
         ("CIngr", 10, 0.03, "chance an ingredient craft (flour, dough, salt, spices) gives double output"),
         ("CGourmet2", 20, 0.01, "chance of +1 Grade on any dish (adds to CGourmet)"),
         ("CSig", 10, 0.01, "chance of +2 Grades"), ("CMaster", 5, 0.05, "level 1 = +1 Grade on every dish; levels 2-5 = this chance each of one more")]
DL = ["# SkyyCooking %s - cooking.properties (written on first run; comments must stay on their own lines)" % VERSION,
      "# Cooking Bench crafts give graded dishes and Cooking XP (sent to SkyySkills 0.4 through skill:fn:addxp).",
      "enabled=true",
      "# Grade = floor(Cooking level / 10) (max 10) + Cooking skill tree (SkyyTrees). Heal and buffs x(1 + 0.32 x Grade), buffs last",
      "# x2^(Grade/5) - both baked into the generated assets. maxGrade can only LOWER the cap: the jar has Grades 1-%d; a higher value is read as %d." % (GEN_MAX, GEN_MAX),
      "maxGrade=%d" % GEN_MAX,
      "# true = creative-mode crafts get Grades and XP too (default: creative = plain food, no XP)",
      "creativeGrades=false",
      XP_MARK,
      XP_HELP_LINE,
      "xpMultiplier=%s" % repr(XP_MULT_DEF),
      "# safety net: base Cooking XP per player per minute (counted before xpMultiplier); 0 = off. The dish is always given.",
      "maxXpPerMinute=%d" % MAX_PER_MIN,
      "# chat lines for tree bonuses and a new Grade",
      "messages=true",
      "# dishes that come out graded (must be dishes this jar generated assets for; others always come out plain)",
      "graded=" + ",".join(DISHES)] + CAMP_LINES + [
      XP_ING_MARK, XP_TBL_MARK] + XP_HELP_016 + [
      "xp.default=%d" % XP_DEFAULT]
for k in sorted(XP):
    DL.append("xp.%s=%d" % (k, XP[k]))
DL.append("# Cooking skill tree (SkyyTrees node levels, bridge tree:fn:level): value per node level. Max levels: " +
          ", ".join("%s %d" % (n[0], n[1]) for n in NODES))
for nid, mx, per, what in NODES:
    DL.append("# %s: %s" % (nid, what))
    DL.append("tree.%s.per=%s" % (nid, repr(per)))
DEFAULTS_TEXT = "\n".join(DL) + "\n"

# =====================================================================================================================
# JAVA CLASSES (dependency order: every method exists before any caller is compiled)
# =====================================================================================================================
def jstr_arr(lst): return "new String[] { " + ", ".join(json.dumps(x) for x in lst) + " }"
def jint_arr(lst): return "new int[] { " + ", ".join(str(int(x)) for x in lst) + " }"
def jdbl_arr(lst): return "new double[] { " + ", ".join(repr(float(x)) for x in lst) + " }"
def jlong_arr(lst): return "new long[] { " + ", ".join("%dL" % int(x) for x in lst) + " }"

cfg  = pool.makeClass(PKG + ".CookCfg")
ck   = pool.makeClass(PKG + ".Cook")
xpt  = pool.makeClass(PKG + ".CookXpTask")
csy  = pool.makeClass(PKG + ".CookSys", pool.get(EES))
gfn  = pool.makeClass(PKG + ".CookGradeFn")
ofn  = pool.makeClass(PKG + ".CookOutFn")
sfn  = pool.makeClass(PKG + ".CookStatsFn")
cfn  = pool.makeClass(PKG + ".CookCampFn")
ifn  = pool.makeClass(PKG + ".CookCampInfoFn")
gcmd = pool.makeClass(PKG + ".CookGiveCmd", pool.get(APC))
rcmd = pool.makeClass(PKG + ".CookReloadCmd", pool.get(APC))
fcmd = pool.makeClass(PKG + ".CookCampCmd", pool.get(APC))
acmd = pool.makeClass(PKG + ".CookAdminCmd", pool.get(APC))
ccmd = pool.makeClass(PKG + ".CookingCmd", pool.get(APC))
pl   = pool.makeClass(PKG + ".SkyyCookingPlugin", pool.get(JP))

def F(cls, decl): cls.addField(CtField.make(decl, cls))
def Mk(cls, src): cls.addMethod(CtNewMethod.make(jsrc(src), cls))
def Ct(cls, src): cls.addConstructor(CtNewConstructor.make(jsrc(src), cls))

# ================= CookCfg: cooking.properties + build-time constants =================
F(cfg, "public static %s LOG;" % LOG)
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static final int GEN_MAX = %d;" % GEN_MAX)
F(cfg, "public static final String[] DISHES = %s;" % jstr_arr(DISHES))
F(cfg, "public static final int[] TIER = %s;" % jint_arr([DISH_TIER[d] for d in DISHES]))
F(cfg, "public static final String[] NAMES = %s;" % jstr_arr([DISH_NAME[d] for d in DISHES]))
F(cfg, "public static final String[] INGR = %s;" % jstr_arr(INGREDIENTS))
F(cfg, "public static final String[] NODES = %s;" % jstr_arr([n[0] for n in NODES]))
F(cfg, "public static final int[] NODE_MAX = %s;" % jint_arr([n[1] for n in NODES]))
F(cfg, "public static final double[] NODE_DEF = %s;" % jdbl_arr([n[2] for n in NODES]))
F(cfg, "public static final double[] SF = %s;" % jdbl_arr([round(SF(g), 4) for g in range(GEN_MAX + 1)]))
F(cfg, "public static final double[] DF = %s;" % jdbl_arr([round(DF(g), 4) for g in range(GEN_MAX + 1)]))
F(cfg, "public static final String[] XP_IDS = %s;" % jstr_arr(sorted(XP)))
F(cfg, "public static final long[] XP_VALS = %s;" % jlong_arr([XP[k] for k in sorted(XP)]))
F(cfg, "public static final long DEF_XP_DEFAULT = %dL;" % XP_DEFAULT)
F(cfg, "public static final long DEF_MAX_PER_MIN = %dL;" % MAX_PER_MIN)
F(cfg, "public static final String DEFAULTS = %s;" % json.dumps(DEFAULTS_TEXT))
# 0.1.1 Campfire accessory
F(cfg, "public static final String[] CAMP = %s;" % jstr_arr(CAMP_DISHES))
# 0.1.4: MUL = the STRENGTH factors S(g), what Cook.campGrade compares (campfire.buffFactor works on the strength part; until 0.1.3 M(g))
F(cfg, "public static final double[] MUL = %s;" % jdbl_arr([CM(g) for g in range(GEN_MAX + 1)]))
F(cfg, "public static final double DEF_CAMP_BUFF = %s;" % repr(CAMP_BUFF_DEF))
F(cfg, "public static final double DEF_CAMP_XP = %s;" % repr(CAMP_XP_DEF))
F(cfg, "public static volatile double CAMP_BUFF = %s;" % repr(CAMP_BUFF_DEF))
F(cfg, "public static volatile double CAMP_XP = %s;" % repr(CAMP_XP_DEF))
F(cfg, "public static final String CAMP_BLOCK = %s;" % json.dumps(CAMP_BLOCK_TEXT))
F(cfg, "public static volatile boolean ENABLED = true;")
F(cfg, "public static volatile int MAX_GRADE = %d;" % GEN_MAX)
F(cfg, "public static volatile boolean CREATIVE = false;")
F(cfg, "public static final double DEF_XP_MULT = %s;" % repr(XP_MULT_DEF))      # 0.1.4: the xpMultiplier default (was 1.0)
F(cfg, "public static volatile double XP_MULT = %s;" % repr(XP_MULT_DEF))
F(cfg, "public static volatile long MAX_PER_MIN = %dL;" % MAX_PER_MIN)
F(cfg, "public static volatile boolean MESSAGES = true;")
F(cfg, "public static volatile long XP_DEFAULT = %dL;" % XP_DEFAULT)
F(cfg, "public static volatile java.util.HashMap XP = new java.util.HashMap();")
F(cfg, "public static volatile java.util.HashSet GRADED = new java.util.HashSet();")
F(cfg, "public static volatile double[] PER = %s;" % jdbl_arr([n[2] for n in NODES]))
F(cfg, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
F(cfg, "public static final java.util.concurrent.ConcurrentHashMap EVERY = new java.util.concurrent.ConcurrentHashMap();")
Mk(cfg, """
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCooking] " + msg); } catch (Throwable t) { }
}""")
Mk(cfg, """
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyCooking] " + msg); } catch (Throwable t) { }
}""")
Mk(cfg, """
public static void once(String key, String msg) {
  if (ONCE.putIfAbsent(key, Boolean.TRUE) == null) warn(msg);
}""")
Mk(cfg, """
public static void every(String key, long ms, String msg) {
  long now = System.currentTimeMillis();
  Long l = (Long) EVERY.get(key);
  if (l != null && now - l.longValue() < ms) return;
  EVERY.put(key, Long.valueOf(now));
  warn(msg);
}""")
Mk(cfg, """
public static double dbl(java.util.Properties p, String k, double d) {
  try { String v = p.getProperty(k); if (v == null) return d; double x = Double.parseDouble(v.trim()); if (Double.isNaN(x) || Double.isInfinite(x)) return d; return x; } catch (Throwable t) { return d; }
}""")
Mk(cfg, """
public static long lng(java.util.Properties p, String k, long d) {
  try { String v = p.getProperty(k); return v == null ? d : Long.parseLong(v.trim()); } catch (Throwable t) { return d; }
}""")
Mk(cfg, """
public static boolean bool(java.util.Properties p, String k, boolean d) {
  String v = p.getProperty(k);
  if (v == null) return d;
  v = v.trim();
  if (v.equalsIgnoreCase("true")) return true;
  if (v.equalsIgnoreCase("false")) return false;
  return d;
}""")
Mk(cfg, """
public static int dishIndex(String id) {
  if (id == null) return -1;
  for (int i = 0; i < DISHES.length; i++) if (DISHES[i].equals(id)) return i;
  return -1;
}""")
# tier of a dish that comes out GRADED right now (0 = never graded: not generated or removed from graded=)
Mk(cfg, """
public static int tierOf(String id) {
  int i = dishIndex(id);
  if (i < 0) return 0;
  if (!GRADED.contains(id)) return 0;
  return TIER[i];
}""")
Mk(cfg, """
public static boolean isIngredient(String id) {
  if (id == null) return false;
  for (int i = 0; i < INGR.length; i++) if (INGR[i].equals(id)) return true;
  return false;
}""")
Mk(cfg, """
public static String nameOf(String id) {
  if (id == null) return "?";
  int i = dishIndex(id);
  if (i >= 0) return NAMES[i];
  String s = id;
  if (s.startsWith("Skyy_Cook_")) s = s.substring(10);
  if (s.startsWith("Ingredient_")) s = s.substring(11);
  if (s.startsWith("Food_")) s = s.substring(5);
  return s.replace('_', ' ');
}""")
# 0.1.1: the Campfire accessory dishes (cook:campfire:ids)
Mk(cfg, """
public static int campIndex(String id) {
  if (id == null) return -1;
  for (int i = 0; i < CAMP.length; i++) if (CAMP[i].equals(id)) return i;
  return -1;
}""")
Mk(cfg, """
public static String campList() {
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < CAMP.length; i++) {
    if (i > 0) b.append(',');
    b.append(CAMP[i]);
  }
  return b.toString();
}""")
Mk(cfg, """
public static String campNames() {
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < CAMP.length; i++) {
    if (i > 0) {
      if (i == CAMP.length - 1) b.append(" and ");
      else b.append(", ");
    }
    b.append(nameOf(CAMP[i]));
  }
  return b.toString();
}""")
Mk(cfg, """
public static void fillDefaults(java.util.HashMap xp, java.util.HashSet gr) {
  for (int i = 0; i < XP_IDS.length; i++) xp.put(XP_IDS[i], Long.valueOf(XP_VALS[i]));
  for (int i = 0; i < DISHES.length; i++) gr.add(DISHES[i]);
}""")
Mk(cfg, """
public static synchronized String load() {
  int bad = 0;
  java.util.HashMap xp = new java.util.HashMap();
  java.util.HashSet gr = new java.util.HashSet();
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Files.write(FILE, DEFAULTS.getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    ENABLED = bool(p, "enabled", true);
    long mg = lng(p, "maxGrade", (long) GEN_MAX);
    if (mg < 0L) mg = 0L;
    if (mg > (long) GEN_MAX) { warn("maxGrade=" + mg + " is above the " + GEN_MAX + " Grades this jar has assets for - using " + GEN_MAX); mg = (long) GEN_MAX; }
    MAX_GRADE = (int) mg;
    CREATIVE = bool(p, "creativeGrades", false);
    double m = dbl(p, "xpMultiplier", DEF_XP_MULT);
    XP_MULT = m < 0.0 ? 0.0 : m;
    long cap = lng(p, "maxXpPerMinute", DEF_MAX_PER_MIN);
    MAX_PER_MIN = cap < 0L ? 0L : cap;
    MESSAGES = bool(p, "messages", true);
    double cb = dbl(p, "campfire.buffFactor", DEF_CAMP_BUFF);
    if (cb < 0.0 || cb > 1.0) { bad++; warn("campfire.buffFactor=" + cb + " is outside 0..1 - clamped"); cb = cb < 0.0 ? 0.0 : 1.0; }
    CAMP_BUFF = cb;
    double cx = dbl(p, "campfire.xpFactor", DEF_CAMP_XP);
    if (cx < 0.0 || cx > 1.0) { bad++; warn("campfire.xpFactor=" + cx + " is outside 0..1 - clamped"); cx = cx < 0.0 ? 0.0 : 1.0; }
    CAMP_XP = cx;
    if (p.getProperty("campfire.buffFactor") == null && p.getProperty("campfire.xpFactor") == null) {
      try {
        java.nio.file.Files.write(FILE, CAMP_BLOCK.getBytes("UTF-8"), new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.APPEND });
        info("cooking.properties: added the campfire.* lines (0.1.1 Campfire accessory, defaults buffFactor " + DEF_CAMP_BUFF + " / xpFactor " + DEF_CAMP_XP + ")");
      } catch (Throwable t) { warn("could not add the campfire.* lines to cooking.properties (the defaults are used): " + t); }
    }
    long xd = lng(p, "xp.default", DEF_XP_DEFAULT);
    XP_DEFAULT = xd < 0L ? 0L : xd;
    for (int i = 0; i < XP_IDS.length; i++) xp.put(XP_IDS[i], Long.valueOf(XP_VALS[i]));
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) {
      String k = String.valueOf(en.nextElement()).trim();
      if (!k.startsWith("xp.") || k.equals("xp.default") || k.length() <= 3) continue;
      try {
        long v = Long.parseLong(p.getProperty(k).trim());
        if (v < 0L) v = 0L;
        xp.put(k.substring(3), Long.valueOf(v));
      } catch (Throwable t) { bad++; warn("bad line " + k + "=" + p.getProperty(k) + " (want a whole number)"); }
    }
    String gl = p.getProperty("graded");
    if (gl == null) { for (int i = 0; i < DISHES.length; i++) gr.add(DISHES[i]); }
    else {
      String[] parts = gl.split(",");
      for (int i = 0; i < parts.length; i++) {
        String id = parts[i].trim();
        if (id.length() == 0) continue;
        if (dishIndex(id) >= 0) gr.add(id);
        else { bad++; warn("graded: " + id + " has no generated Grade assets in this jar - ignored"); }
      }
    }
    double[] per = new double[NODES.length];
    for (int i = 0; i < NODES.length; i++) {
      double v = dbl(p, "tree." + NODES[i] + ".per", NODE_DEF[i]);
      if (v < 0.0) v = 0.0;
      if (v > 1.0) v = 1.0;
      per[i] = v;
    }
    XP = xp; GRADED = gr; PER = per;
    return (ENABLED ? "on" : "OFF") + ", " + gr.size() + " graded dishes, max Grade " + MAX_GRADE + ", " + xp.size() + " XP keys, xpMultiplier " + XP_MULT + ", cap " + MAX_PER_MIN + "/min, campfire accessory x" + CAMP_BUFF + " Grade bonus x" + CAMP_XP + " XP" + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");
  } catch (Throwable t) {
    warn("could not load cooking.properties (using the built-in defaults): " + t);
    java.util.HashMap dx = new java.util.HashMap();
    java.util.HashSet dg = new java.util.HashSet();
    fillDefaults(dx, dg);
    XP = dx; GRADED = dg;
    return "load failed, defaults in use: " + t;
  }
}""")
Mk(cfg, """
public static long xpFor(String out) {
  if (out == null) return 0L;
  Long v = (Long) XP.get(out);
  if (v != null) return v.longValue();
  if (ONCE.putIfAbsent("xp:" + out, Boolean.TRUE) == null) info("no xp." + out + " line - paying xp.default=" + XP_DEFAULT + " per craft (add the line to cooking.properties to change it)");
  return XP_DEFAULT;
}""")

# =====================================================================================================================
# 0.1.2 ADMIN CONFIG (research/Server-Setup-Spec.md 4.13 + 7, tools/CONFIG-CONTRACT.md): the tools/skyycfg.py kit on cooking.properties.
# Every row binds reload@cooking.properties:<file key> (keys unchanged); RELOAD = CookCfg.load (the /cookadmin reload routine: it only
# parses the file into volatile fields, so it is safe on the scheduler thread the kit runs it on). Shows in SkyyMenu 0.3 Server Setup.
# =====================================================================================================================
B.probe(pool, PR, "getUsername")
COOK_FILE = "Skyy_SkyyCooking/cooking.properties"
COOK_CFG_CATS = [("parts", "Parts"), ("grades", "Grades"), ("xp", "Cooking XP"), ("campfire", "Campfire accessory"),
                 ("tree", "Skill tree"), ("chat", "Chat")]
COOK_CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("enabled", "Graded cooking", "parts", "bool", "true", "", "", "", "", "live,part,danger",
     "Off: every dish comes out plain and cooking pays no Cooking XP. Nothing is deleted.",
     "reload@cooking.properties:enabled"),
    ("maxGrade", "Highest Grade", "grades", "int", str(GEN_MAX), "0", str(GEN_MAX), "step=1", "", "live",
     "Can only lower the cap: this jar has Grade 1-%d assets. 0 = every dish comes out plain." % GEN_MAX,
     "reload@cooking.properties:maxGrade"),
    ("graded", "Graded dishes", "grades", "items", ",".join(DISHES), "0", str(len(DISHES)), "", "", "live",
     "Dishes that come out graded - only the %d dishes this jar has Grade assets for." % len(DISHES),
     "reload@cooking.properties:graded;check=CookHooks.checkGraded"),
    ("creativeGrades", "Grades and XP in creative", "grades", "bool", "false", "", "", "", "", "live,danger",
     "On: creative-mode crafts get Grades and Cooking XP too. Off = plain food and no XP.",
     "reload@cooking.properties:creativeGrades;confirm=on"),
    ("xpMultiplier", "Cooking XP multiplier", "xp", "dec", repr(XP_MULT_DEF), "0", "100", "", "x", "live,danger",
     XP_HELP_ROW,
     "reload@cooking.properties:xpMultiplier"),
    ("maxXpPerMinute", "XP cap per minute", "xp", "int", str(MAX_PER_MIN), "0", "100000000", "", "", "live",
     "Base Cooking XP per player per minute, before the multiplier. 0 = no cap. Dishes are still given.",
     "reload@cooking.properties:maxXpPerMinute"),
    ("xp", "XP per craft", "xp", "table", "", "0", "1000000", "int;both;XP", "", "live",
     "Base XP per finished craft by output item id. default = any other output. Remove = built-in value.",
     "reload@cooking.properties:xp.;check=CookHooks.checkXp"),
    ("campfire.buffFactor", "Campfire Grade share", "campfire", "dec", repr(CAMP_BUFF_DEF), "0", "1", "", "", "live",
     "Share of the Cooking Grade bonus a campfire-accessory dish keeps (0.75 = 75%).",
     "reload@cooking.properties:campfire.buffFactor"),
    ("campfire.xpFactor", "Campfire XP share", "campfire", "dec", repr(CAMP_XP_DEF), "0", "1", "", "", "live",
     "Share of the Cooking XP a campfire-accessory dish pays (0.25 = a quarter).",
     "reload@cooking.properties:campfire.xpFactor"),
    ("tree", "Node chance per level", "tree", "table", "", "0", "1", "dec;none;Chance per level", "", "live,adv",
     "Chance per node level (0.01 = 1%). Only a fallback: SkyyTrees' own numbers win when it runs.",
     "reload@cooking.properties:tree.;check=CookHooks.checkTree"),
    ("messages", "Cooking chat lines", "chat", "bool", "true", "", "", "", "", "live",
     "Off: no [Cooking] Grade, bonus or campfire lines for anyone. Players can hide them in /settings.",
     "reload@cooking.properties:messages"),
]
# build check (default behaviour must stay identical): every scalar row default is the canonical value of its line in the generated
# cooking.properties, and the two tables' default entries are exactly the lines the loader reads, inside the row bounds
_DP = CFG.parse_props(DEFAULTS_TEXT)
for _t in COOK_CFG_ROWS:
    _r = CFG._row_dict(_t)
    _fk = _r["bind"].split(";")[0].split(":", 1)[1]
    if _r["type"] in CFG.SCALAR:
        if _fk not in _DP:
            raise SystemExit("self-check 0.1.2: row %s binds %s, which the generated cooking.properties does not write" % (_r["key"], _fk))
        _a, _wa = CFG.py_validate(_r, _DP[_fk])
        _b, _wb = CFG.py_validate(_r, _r["default"])
        if _a is None or _b is None or _a != _b:
            raise SystemExit("self-check 0.1.2: row %s default %r (%s) differs from the file's %s=%r (%s)" % (_r["key"], _r["default"], _wb, _fk, _DP[_fk], _wa))
    elif _r["type"] == "table":
        _ents = sorted(k[len(_fk):] for k in _DP if k.startswith(_fk))
        _want = sorted(["default"] + list(XP)) if _fk == "xp." else sorted(n[0] + ".per" for n in NODES)
        if _ents != _want:
            raise SystemExit("self-check 0.1.2: table %s default entries %s != %s" % (_r["key"], _ents, _want))
        for _e in _ents:
            _v = float(_DP[_fk + _e])
            if _v < float(_r["min"]) or _v > float(_r["max"]) or (_fk == "xp." and _v != int(_v)):
                raise SystemExit("self-check 0.1.2: table %s entry %s=%s is outside its row (%s..%s)" % (_r["key"], _e, _DP[_fk + _e], _r["min"], _r["max"]))
print("config rows: %d (%s) - every default matches the generated cooking.properties" % (len(COOK_CFG_ROWS), ", ".join(t[0] for t in COOK_CFG_ROWS)))
CFG_KIT = CFG.emit(pool, PKG, MOD="SkyyCooking", TITLE="Cooking", VERSION=VERSION, NODE="skyycooking.admin", CATS=COOK_CFG_CATS,
                   ROWS=COOK_CFG_ROWS, FILES=[COOK_FILE], NOTE="Also: /cookadmin reload re-reads the file; /cookadmin give and campfire hand out test dishes.",
                   RELOAD="CookCfg.load", KEEP=20, DEFAULTS={"cooking.properties": DEFAULTS_TEXT})

# ================= CookHooks: the kit's check= hooks (static String m(String key, String value): null = fine, text = refused) =================
hk = pool.makeClass(PKG + ".CookHooks")
# a table hook gets "tableKey[entry]"
Mk(hk, """
public static String entryOf(String key) {
  if (key == null) return null;
  int a = key.indexOf('[');
  int b = key.lastIndexOf(']');
  if (a < 0 || b <= a) return null;
  return key.substring(a + 1, b);
}""")
# graded=: the kit already checked that every id is a real item; the loader only grades dishes this jar generated assets for
Mk(hk, """
public static String checkGraded(String key, String value) {
  if (value == null) return null;
  String[] parts = value.split(",");
  for (int i = 0; i < parts.length; i++) {
    String id = parts[i].trim();
    if (id.length() == 0) continue;
    if (@PKG@.CookCfg.dishIndex(id) < 0) return id + " has no Grade assets in this jar - only the " + @PKG@.CookCfg.DISHES.length + " dishes of the default list can be graded.";
  }
  return null;
}""")
# xp.<entry>: an existing item id (a craft's primary output) or "default" (= the xp.default line); a removal (value null) is always fine
Mk(hk, """
public static String checkXp(String key, String value) {
  if (value == null) return null;
  String e = entryOf(key);
  if (e == null || e.equals("default")) return null;
  boolean ok = false;
  try { ok = @ITM@.getAssetMap().getAsset(e) != null; } catch (Throwable t) { ok = false; }
  if (!ok) return "Unknown item: " + e + ". Use the item id a craft makes, or default for every other output.";
  return null;
}""")
# tree.<entry>: one of the 10 Cooking tree nodes as <Node>.per (the only lines the loader reads). A REMOVAL of an unknown entry is allowed
# on purpose: the kit refuses removing an entry that is not in the file ("X is not in Node chance per level.") before it calls this hook,
# so a removal only reaches here for a line that IS in the file - a hand-added stray tree.<x> line the loader ignores - and removing it
# is the admin's way to clean it up (a set of an unknown entry is still refused)
Mk(hk, """
public static String checkTree(String key, String value) {
  String e = entryOf(key);
  if (e == null) return null;
  for (int i = 0; i < @PKG@.CookCfg.NODES.length; i++) if (e.equals(@PKG@.CookCfg.NODES[i] + ".per")) return null;
  if (value == null) return null;
  return "Not a Cooking tree node: " + e + ". The entries are <Node>.per, for example CGourmet.per.";
}""")

# ================= CookMig (0.1.3): the one-time campfire.xpFactor update of an existing cooking.properties (see the header) =================
# The SkyyGear 0.1.1 GearCfg.migrateStat011 machinery, method for method. Compiled after the kit (it uses CfgFile / CfgHist / CfgLog /
# CfgRows) and before the plugin (setup() calls migrate() BEFORE CookCfg.load + CfgPub.start). No mod code runs under a kit monitor here:
# the kit has not started yet, nothing else touches the file during setup().
mig = pool.makeClass(PKG + ".CookMig")
F(mig, "public static final String WHO = %s;" % json.dumps("SkyyCooking " + VERSION))
F(mig, "public static final String KEY = \"campfire.xpFactor\";")
F(mig, "public static final String BKEY = \"campfire.buffFactor\";")
F(mig, "public static final String OLD = %s;" % json.dumps(repr(CAMP_XP_OLD)))
F(mig, "public static final String NEW = %s;" % json.dumps(repr(CAMP_XP_DEF)))
F(mig, "public static final String WHAT = \"before the 0.1.3 campfire XP update\";")
F(mig, "public static final String MARK = %s;" % json.dumps(CAMP_MARK))
F(mig, "public static final String MARK_ID = %s;" % json.dumps(CAMP_MARK_ID))
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = nothing to do: CAMP_MARK_ID is already in a
# comment line, or the file has neither a campfire.xpFactor nor a campfire.buffFactor entry (a 0.1 file: the loader appends the marked
# 0.1.3 block). Else Object[]{ new text, "campfire.xpFactor 0.5 -> 0.25" or "", kept note or null, String[] { key, old, new } or {},
# the effective value text or null (no line) }. The LAST entry of the key decides (what java.util.Properties keeps): a one-line entry
# holding exactly OLD -> every one-line entry of the key holding OLD gets NEW (value text only: key, separator and CR stay); anything else
# is kept (a custom value or a continued entry is noted; already NEW or missing is silent). Every line is scanned from the start of a
# logical line, so "a comment right above" is never the tail of a continued entry and a marker inserted there can never be swallowed.
Mk(mig, r"""
public static Object[] update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String eff = null;
  boolean multi = false;
  int ax = -1;
  int ab = -1;
  int com = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      if (s.trim().length() > 0) com = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    int above = (com >= 0 && com == k - 1) ? com : k;
    if (KEY.equals(key)) {
      if (ax < 0) ax = above;
      eff = @PKG@.CfgFile.value(l, k).trim();
      multi = e > k;
    } else if (BKEY.equals(key) && ab < 0) ab = above;
    k = e + 1;
  }
  int at = ax >= 0 ? ax : ab;
  if (at < 0) return null;
  boolean mig = eff != null && !multi && eff.equals(OLD);
  String chg = "";
  String kept = null;
  java.util.ArrayList rows = new java.util.ArrayList();
  if (mig) {
    chg = KEY + " " + OLD + " -> " + NEW;
    rows.add(KEY);
    rows.add(OLD);
    rows.add(NEW);
  } else if (eff != null && (multi || !eff.equals(NEW))) {
    kept = KEY + "=" + @PKG@.CfgRows.oneLine(eff) + " kept (custom) - the 0.1.3 default is " + NEW;
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (mig && e2 == k && KEY.equals(@PKG@.CfgFile.key(s2)) && @PKG@.CfgFile.value(l, k).trim().equals(OLD)) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + NEW + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg, kept, (String[]) rows.toArray(new String[0]), eff };
}""")
# the config kit's own files for the update, before CfgPub.start (which sets the same values again): history + change log live in the
# folder of cooking.properties (the kit's HOME, Skyy_SkyyCooking)
Mk(mig, r"""
public static void kit(java.nio.file.Path home) {
  @PKG@.CfgRows.HOME = home;
  if (@PKG@.CfgRows.LOG == null) @PKG@.CfgRows.LOG = @PKG@.CookCfg.LOG;
  @PKG@.CfgHist.init();
  @PKG@.CfgLog.init();
}""")
# CfgHist.snapshot swallows its own errors, so the update checks that config-history really holds a copy with exactly these bytes (the new
# copy, or the newest one when snapshot skipped an equal file). The copies themselves are checked, not index.log (SkyyGear review finding 3)
Mk(mig, r"""
public static boolean saved(byte[] old) {
  String[] have = @PKG@.CfgHist.list(0);
  for (int i = have.length - 1; i >= 0; i--) {
    try {
      if (java.util.Arrays.equals(java.nio.file.Files.readAllBytes(@PKG@.CfgHist.bak(0, have[i])), old)) return true;
    } catch (Throwable x) { }
  }
  return false;
}""")
# one config-changes.log line in the kit's scalar-row format (CfgLog.add without its per-line INFO; the key column = the row key, so
# Server Setup -> Changes undoes it with a plain set back to the old value)
Mk(mig, r"""
public static String logLine(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\t" + WHO + "\t-\tupdate\t" + @PKG@.CfgRows.oneLine(k) + "\t" + o + "\t" + n + "\tok";
}""")
# setup(), right after CookCfg.FILE is set and BEFORE CookCfg.load() + CfgPub.start: the file before this update becomes a History version
# (KEEP 20, verified by saved() before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log
# line when the value changed, one INFO line (+ one for a kept custom value). Returns the INFO line(s) joined by \n ("" = nothing done: no
# file, marker already there, no campfire line, or a failure - WARN, file untouched, the next start tries again)
Mk(mig, r"""
public static synchronized String migrate() {
  java.nio.file.Path f = @PKG@.CookCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), WHO, WHAT);
    if (!saved(old)) {
      @PKG@.CookCfg.warn("cooking.properties NOT updated to the 0.1.3 campfire XP share: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String kept = (String) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "cooking.properties updated to the 0.1.3 campfire XP share: " + chg + " (Skyy 2026-10-01: campfire cooking pays half the XP it did; the old file is in config-history; Server Setup -> Changes can undo it)";
    else if (kept != null) msg = "cooking.properties: campfire.xpFactor was changed by hand - kept, nothing changed (0.1.3 campfire XP marker added)";
    else if (r[4] == null) msg = "cooking.properties: no campfire.xpFactor line (the default " + NEW + " applies) - nothing changed (0.1.3 campfire XP marker added)";
    else msg = "cooking.properties: campfire.xpFactor is already " + NEW + " - nothing changed (0.1.3 campfire XP marker added)";
    @PKG@.CookCfg.info(msg);
    if (kept == null) return msg;
    @PKG@.CookCfg.info(kept);
    return msg + "\n" + kept;
  } catch (Throwable t) {
    @PKG@.CookCfg.warn("could not update cooking.properties to the 0.1.3 campfire XP share (the file is used as it is): " + t);
    return "";
  }
}""")

# ================= CookXpMig (0.1.4): the one-time xpMultiplier update of an existing cooking.properties (see the header) =================
# CookMig's reviewed machinery for the Cooking XP multiplier: the same pure text step on the kit's parser, the same History / atomic write /
# change-log path (it calls CookMig.kit, CookMig.saved and CookMig.logLine - same WHO), its own run-once marker XP_MARK. Compiled after
# CookMig and before the plugin: setup() calls it right after CookMig.migrate, BEFORE CookCfg.load + CfgPub.start (the kit has not started,
# nothing else touches the file during setup(), no mod code runs under a kit monitor).
xmig = pool.makeClass(PKG + ".CookXpMig")
F(xmig, "public static final String KEY = \"xpMultiplier\";")
F(xmig, "public static final String OLD = %s;" % json.dumps(XP_MULT_OLD[0]))      # "1.0": every generated cooking.properties since 0.1
F(xmig, "public static final String OLD2 = %s;" % json.dumps(XP_MULT_OLD[1]))     # "1": the kit's canonical write of the old default
F(xmig, "public static final String NEW = %s;" % json.dumps(repr(XP_MULT_DEF)))
F(xmig, "public static final String WHAT = \"before the 0.1.4 Cooking XP update\";")
F(xmig, "public static final String MARK = %s;" % json.dumps(XP_MARK))
F(xmig, "public static final String MARK_ID = %s;" % json.dumps(XP_MARK_ID))
Mk(xmig, r"""
public static boolean isOld(String v) {
  return v != null && (v.equals(OLD) || v.equals(OLD2));
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = nothing to do: XP_MARK_ID is already in a comment
# line. Else Object[]{ new text, "xpMultiplier 1.0 -> 0.5" or "", kept note or null, String[] { key, old, new } or {}, the effective value
# text or null (no line) }. The LAST entry of the key decides (what java.util.Properties keeps): a one-line entry holding exactly OLD or
# OLD2 -> every one-line entry of the key holding one of them gets NEW (value text only: key, separator and CR stay); anything else is kept
# (a custom value or a continued entry is noted; already NEW or missing is silent). The marker goes right above the FIRST xpMultiplier
# entry (above a comment line directly on top of it), else the same way above the file's first entry, else on top. Every line is scanned
# from the start of a logical line, so "a comment right above" is never the tail of a continued entry and the marker is never swallowed.
Mk(xmig, r"""
public static Object[] update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  String eff = null;
  boolean multi = false;
  int ax = -1;
  int af = -1;
  int com = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      if (s.trim().length() > 0) com = k;
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    int above = (com >= 0 && com == k - 1) ? com : k;
    if (af < 0) af = above;
    if (KEY.equals(key)) {
      if (ax < 0) ax = above;
      eff = @PKG@.CfgFile.value(l, k).trim();
      multi = e > k;
    }
    k = e + 1;
  }
  int at = 0;
  if (ax >= 0) at = ax;
  else if (af >= 0) at = af;
  boolean mig = eff != null && !multi && isOld(eff);
  String chg = "";
  String kept = null;
  java.util.ArrayList rows = new java.util.ArrayList();
  if (mig) {
    chg = KEY + " " + eff + " -> " + NEW;
    rows.add(KEY);
    rows.add(eff);
    rows.add(NEW);
  } else if (eff != null && (multi || !eff.equals(NEW))) {
    kept = KEY + "=" + @PKG@.CfgRows.oneLine(eff) + " kept (custom) - the 0.1.4 default is " + NEW;
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) { out.add(raw[k]); k++; continue; }
    int e2 = @PKG@.CfgFile.end(l, k);
    if (mig && e2 == k && KEY.equals(@PKG@.CfgFile.key(s2)) && isOld(@PKG@.CfgFile.value(l, k).trim())) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + NEW + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg, kept, (String[]) rows.toArray(new String[0]), eff };
}""")
# (CookXpMig.migrate below; 0.1.5 CookTblMig follows it)
# setup(), right after CookMig.migrate and BEFORE CookCfg.load() + CfgPub.start: the file before this update becomes a History version
# (verified by CookMig.saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log
# line when the value changed, one INFO line (+ one for a kept custom value). Returns the INFO line(s) joined by \n ("" = nothing done: no
# file, marker already there, or a failure - WARN, file untouched, the next start tries again)
Mk(xmig, r"""
public static synchronized String migrate() {
  java.nio.file.Path f = @PKG@.CookCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    @PKG@.CookMig.kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), @PKG@.CookMig.WHO, WHAT);
    if (!@PKG@.CookMig.saved(old)) {
      @PKG@.CookCfg.warn("cooking.properties NOT updated to the 0.1.4 Cooking XP default: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(@PKG@.CookMig.logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String kept = (String) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "cooking.properties updated to the 0.1.4 Cooking XP default: " + chg + " (Skyy 2026-10-02: cooking levelled too fast - every Cooking XP award is halved; the old file is in config-history; Server Setup -> Changes can undo it)";
    else if (kept != null) msg = "cooking.properties: xpMultiplier was changed by hand - kept, nothing changed (0.1.4 Cooking XP marker added)";
    else if (r[4] == null) msg = "cooking.properties: no xpMultiplier line (the default " + NEW + " applies) - nothing changed (0.1.4 Cooking XP marker added)";
    else msg = "cooking.properties: xpMultiplier is already " + NEW + " - kept, nothing changed (0.1.4 Cooking XP marker added)";
    @PKG@.CookCfg.info(msg);
    if (kept == null) return msg;
    @PKG@.CookCfg.info(kept);
    return msg + "\n" + kept;
  } catch (Throwable t) {
    @PKG@.CookCfg.warn("could not update cooking.properties to the 0.1.4 Cooking XP default (the file is used as it is): " + t);
    return "";
  }
}""")

# ================= CookTblMig (0.1.5): the one-time XP-per-craft update of an existing cooking.properties (see the header) =================
# CookMig's reviewed machinery for the xp.<dish> table lines: the same pure text step on the kit's parser, the same History / atomic write /
# change-log path (CookMig.kit / saved / logLine - same WHO), its own run-once marker XP_TBL_MARK. Compiled after CookXpMig and before the
# plugin: setup() calls it right after CookXpMig.migrate, BEFORE CookCfg.load + CfgPub.start.
_TBL = sorted(d for d in DISHES if XP[d] != XP_OLD[d])
tmig = pool.makeClass(PKG + ".CookTblMig")
F(tmig, "public static final String[] KEYS = %s;" % jstr_arr(["xp." + d for d in _TBL]))
F(tmig, "public static final String[] LOGKEYS = %s;" % jstr_arr(["xp[" + d + "]" for d in _TBL]))
F(tmig, "public static final String[] OLDS = %s;" % jstr_arr([str(XP_OLD[d]) for d in _TBL]))
F(tmig, "public static final String[] STOPS = %s;" % jstr_arr([str(STOPGAP_014.get(d, "")) for d in _TBL]))
F(tmig, "public static final String[] NEWS = %s;" % jstr_arr([str(XP[d]) for d in _TBL]))
F(tmig, "public static final String[] HELP_OLD = %s;" % jstr_arr(XP_HELP_OLD))
F(tmig, "public static final String[] HELP_NEW = %s;" % jstr_arr(XP_HELP_NEW))
F(tmig, "public static final String WHAT = \"before the 0.1.5 Cooking XP by difficulty update\";")
F(tmig, "public static final String MARK = %s;" % json.dumps(XP_TBL_MARK))
F(tmig, "public static final String MARK_ID = %s;" % json.dumps(XP_TBL_MARK_ID))
Mk(tmig, r"""
public static int idx(String key) {
  if (key == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(key)) return i;
  return -1;
}""")
Mk(tmig, r"""
public static boolean isOld(int i, String v) {
  if (i < 0 || v == null) return false;
  return v.equals(OLDS[i]) || (STOPS[i].length() > 0 && v.equals(STOPS[i]));
}""")
Mk(tmig, r"""
public static int helpIdx(String s) {
  for (int i = 0; i < HELP_OLD.length; i++) if (HELP_OLD[i].equals(s)) return i;
  return -1;
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = nothing to do: XP_TBL_MARK_ID is already in a
# comment line. Else Object[]{ new text, "xp.A 3650 -> 1050, ..." or "", kept notes joined by \n or null, String[] { logkey, old, new, ... }
# }. Per key the LAST entry decides (what java.util.Properties keeps): a one-line entry holding exactly OLDS[i] or STOPS[i] -> every one-line
# entry of the key holding one of them gets NEWS[i] (value text only: key, separator and CR stay); anything else is kept (a custom value
# or a continued entry is noted; already NEWS[i] or missing is silent). Comment lines equal to HELP_OLD[j] become HELP_NEW[j] (1:1, CR
# kept). The marker goes above the run of non-blank comment lines directly on top of the FIRST xp.* entry (no run: right above it), else
# the same way above the file's first entry, else on top. Every line is scanned from the start of a logical line, so a comment is never
# the tail of a continued entry and the marker is never swallowed.
Mk(tmig, r"""
public static Object[] update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = KEYS.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int ax = -1;
  int af = -1;
  int com = -1;
  int run = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      if (s.trim().length() > 0) {
        if (com < 0 || com != k - 1) run = k;
        com = k;
      }
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    int above = (com >= 0 && com == k - 1) ? run : k;
    if (af < 0) af = above;
    if (ax < 0 && key != null && key.startsWith("xp.")) ax = above;
    int ki = idx(key);
    if (ki >= 0) {
      eff[ki] = @PKG@.CfgFile.value(l, k).trim();
      multi[ki] = e > k;
    }
    k = e + 1;
  }
  int at = 0;
  if (ax >= 0) at = ax;
  else if (af >= 0) at = af;
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  StringBuilder kept = new StringBuilder();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    String v = eff[i];
    if (v == null) continue;
    if (!multi[i] && isOld(i, v)) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(KEYS[i]).append(" ").append(v).append(" -> ").append(NEWS[i]);
      rows.add(LOGKEYS[i]);
      rows.add(v);
      rows.add(NEWS[i]);
    } else if (multi[i] || !v.equals(NEWS[i])) {
      if (kept.length() > 0) kept.append("\n");
      kept.append(KEYS[i]).append("=").append(@PKG@.CfgRows.oneLine(v)).append(" kept (custom) - the 0.1.5 default is ").append(NEWS[i]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) {
      int h = helpIdx(s2);
      if (h >= 0) out.add(HELP_NEW[h] + (raw[k].endsWith("\r") ? "\r" : ""));
      else out.add(raw[k]);
      k++;
      continue;
    }
    int e2 = @PKG@.CfgFile.end(l, k);
    int i2 = idx(@PKG@.CfgFile.key(s2));
    if (i2 >= 0 && mig[i2] && e2 == k && isOld(i2, @PKG@.CfgFile.value(l, k).trim())) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + NEWS[i2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), kept.length() > 0 ? kept.toString() : null, (String[]) rows.toArray(new String[0]) };
}""")
# setup(), right after CookXpMig.migrate and BEFORE CookCfg.load() + CfgPub.start: the file before this update becomes a History version
# (verified by CookMig.saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log
# line per changed entry, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by \n ("" = nothing done: no file,
# marker already there, or a failure - WARN, file untouched, the next start tries again)
Mk(tmig, r"""
public static synchronized String migrate() {
  java.nio.file.Path f = @PKG@.CookCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    @PKG@.CookMig.kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), @PKG@.CookMig.WHO, WHAT);
    if (!@PKG@.CookMig.saved(old)) {
      @PKG@.CookCfg.warn("cooking.properties NOT updated to the 0.1.5 Cooking XP by difficulty: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(@PKG@.CookMig.logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String kept = (String) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "cooking.properties updated to the 0.1.5 Cooking XP by difficulty (" + (rows.length / 3) + " XP per craft line(s) on old defaults): " + chg + " (Skyy 2026-10-04: easier dishes pay less XP, multi-step dishes more; the old file is in config-history; Server Setup -> Changes can undo each line)";
    else if (kept != null) msg = "cooking.properties: the XP per craft lines were changed by hand - kept, nothing changed (0.1.5 Cooking XP by difficulty marker added)";
    else msg = "cooking.properties: no XP per craft line on an old default - nothing changed (0.1.5 Cooking XP by difficulty marker added)";
    @PKG@.CookCfg.info(msg);
    if (kept == null) return msg;
    String[] ks = kept.split("\n");
    for (int i = 0; i < ks.length; i++) @PKG@.CookCfg.info(ks[i]);
    return msg + "\n" + kept;
  } catch (Throwable t) {
    @PKG@.CookCfg.warn("could not update cooking.properties to the 0.1.5 Cooking XP by difficulty (the file is used as it is): " + t);
    return "";
  }
}""")

# ================= CookIngMig (0.1.6): the one-time ingredient XP update of an existing cooking.properties (see the header) =================
# CookMig's reviewed machinery for the xp.<ingredient> table lines: the same pure text step on the kit's parser, the same History / atomic write /
# change-log path (CookMig.kit / saved / logLine - same WHO), its own run-once marker XP_ING_MARK. Compiled after CookTblMig and before the
# plugin: setup() calls it right after CookTblMig.migrate, BEFORE CookCfg.load + CfgPub.start.
_ING = sorted(i for i in INGS if XP[i] != XP_015[i])
imig = pool.makeClass(PKG + ".CookIngMig")
F(imig, "public static final String[] KEYS = %s;" % jstr_arr(["xp." + d for d in _ING]))
F(imig, "public static final String[] LOGKEYS = %s;" % jstr_arr(["xp[" + d + "]" for d in _ING]))
F(imig, "public static final String[] OLDS = %s;" % jstr_arr([str(XP_015[d]) for d in _ING]))
F(imig, "public static final String[] STOPS = %s;" % jstr_arr(["" for d in _ING]))
F(imig, "public static final String[] NEWS = %s;" % jstr_arr([str(XP[d]) for d in _ING]))
F(imig, "public static final String[] HELP_OLD = %s;" % jstr_arr(XP_HELP_015))
F(imig, "public static final String[] HELP_NEW = %s;" % jstr_arr(XP_HELP_016))
F(imig, "public static final String WHAT = \"before the 0.1.6 ingredient Cooking XP update\";")
F(imig, "public static final String MARK = %s;" % json.dumps(XP_ING_MARK))
F(imig, "public static final String MARK_ID = %s;" % json.dumps(XP_ING_MARK_ID))
Mk(imig, r"""
public static int idx(String key) {
  if (key == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(key)) return i;
  return -1;
}""")
Mk(imig, r"""
public static boolean isOld(int i, String v) {
  if (i < 0 || v == null) return false;
  return v.equals(OLDS[i]) || (STOPS[i].length() > 0 && v.equals(STOPS[i]));
}""")
Mk(imig, r"""
public static int helpIdx(String s) {
  for (int i = 0; i < HELP_OLD.length; i++) if (HELP_OLD[i].equals(s)) return i;
  return -1;
}""")
# pure text step (ISO-8859-1 chars in and out; lines read with the kit's own parser). null = nothing to do: XP_ING_MARK_ID is already in a
# comment line. Else Object[]{ new text, "xp.A 3650 -> 1050, ..." or "", kept notes joined by \n or null, String[] { logkey, old, new, ... }
# }. Per key the LAST entry decides (what java.util.Properties keeps): a one-line entry holding exactly OLDS[i] or STOPS[i] -> every one-line
# entry of the key holding one of them gets NEWS[i] (value text only: key, separator and CR stay); anything else is kept (a custom value
# or a continued entry is noted; already NEWS[i] or missing is silent). Comment lines equal to HELP_OLD[j] become HELP_NEW[j] (1:1, CR
# kept). The marker goes above the run of non-blank comment lines directly on top of the FIRST xp.* entry (no run: right above it), else
# the same way above the file's first entry, else on top. Every line is scanned from the start of a logical line, so a comment is never
# the tail of a continued entry and the marker is never swallowed.
Mk(imig, r"""
public static Object[] update(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int n = KEYS.length;
  String[] eff = new String[n];
  boolean[] multi = new boolean[n];
  int ax = -1;
  int af = -1;
  int com = -1;
  int run = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      if (s.trim().length() > 0) {
        if (com < 0 || com != k - 1) run = k;
        com = k;
      }
      k++;
      continue;
    }
    int e = @PKG@.CfgFile.end(l, k);
    String key = @PKG@.CfgFile.key(s);
    int above = (com >= 0 && com == k - 1) ? run : k;
    if (af < 0) af = above;
    if (ax < 0 && key != null && key.startsWith("xp.")) ax = above;
    int ki = idx(key);
    if (ki >= 0) {
      eff[ki] = @PKG@.CfgFile.value(l, k).trim();
      multi[ki] = e > k;
    }
    k = e + 1;
  }
  int at = 0;
  if (ax >= 0) at = ax;
  else if (af >= 0) at = af;
  boolean[] mig = new boolean[n];
  StringBuilder chg = new StringBuilder();
  StringBuilder kept = new StringBuilder();
  java.util.ArrayList rows = new java.util.ArrayList();
  for (int i = 0; i < n; i++) {
    String v = eff[i];
    if (v == null) continue;
    if (!multi[i] && isOld(i, v)) {
      mig[i] = true;
      if (chg.length() > 0) chg.append(", ");
      chg.append(KEYS[i]).append(" ").append(v).append(" -> ").append(NEWS[i]);
      rows.add(LOGKEYS[i]);
      rows.add(v);
      rows.add(NEWS[i]);
    } else if (multi[i] || !v.equals(NEWS[i])) {
      if (kept.length() > 0) kept.append("\n");
      kept.append(KEYS[i]).append("=").append(@PKG@.CfgRows.oneLine(v)).append(" kept (custom) - the 0.1.6 default is ").append(NEWS[i]);
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  k = 0;
  while (k < l.size()) {
    String s2 = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s2)) {
      int h = helpIdx(s2);
      if (h >= 0) out.add(HELP_NEW[h] + (raw[k].endsWith("\r") ? "\r" : ""));
      else out.add(raw[k]);
      k++;
      continue;
    }
    int e2 = @PKG@.CfgFile.end(l, k);
    int i2 = idx(@PKG@.CfgFile.key(s2));
    if (i2 >= 0 && mig[i2] && e2 == k && isOld(i2, @PKG@.CfgFile.value(l, k).trim())) {
      String cr1 = raw[k].endsWith("\r") ? "\r" : "";
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + NEWS[i2] + cr1);
    } else {
      for (int q = k; q <= e2; q++) out.add(raw[q]);
    }
    k = e2 + 1;
  }
  String cr = text.indexOf("\r\n") >= 0 ? "\r" : "";
  String crA = at + 1 < raw.length ? (raw[at].endsWith("\r") ? "\r" : "") : cr;
  out.add(at, MARK + crA);
  StringBuilder sb = new StringBuilder(text.length() + MARK.length() + 16);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), kept.length() > 0 ? kept.toString() : null, (String[]) rows.toArray(new String[0]) };
}""")
# setup(), right after CookTblMig.migrate and BEFORE CookCfg.load() + CfgPub.start: the file before this update becomes a History version
# (verified by CookMig.saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log
# line per changed entry, one INFO line (+ one per kept custom value). Returns the INFO line(s) joined by \n ("" = nothing done: no file,
# marker already there, or a failure - WARN, file untouched, the next start tries again)
Mk(imig, r"""
public static synchronized String migrate() {
  java.nio.file.Path f = @PKG@.CookCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = update(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    @PKG@.CookMig.kit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), @PKG@.CookMig.WHO, WHAT);
    if (!@PKG@.CookMig.saved(old)) {
      @PKG@.CookCfg.warn("cooking.properties NOT updated to the 0.1.6 ingredient Cooking XP: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(@PKG@.CookMig.logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String kept = (String) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "cooking.properties updated to the 0.1.6 ingredient Cooking XP (" + (rows.length / 3) + " ingredient XP line(s) on old defaults): " + chg + " (Skyy 2026-10-05: early, easy ingredients like flour pay little XP; the old file is in config-history; Server Setup -> Changes can undo each line)";
    else if (kept != null) msg = "cooking.properties: the ingredient XP lines were changed by hand - kept, nothing changed (0.1.6 ingredient Cooking XP marker added)";
    else msg = "cooking.properties: no ingredient XP line on an old default - nothing changed (0.1.6 ingredient Cooking XP marker added)";
    @PKG@.CookCfg.info(msg);
    if (kept == null) return msg;
    String[] ks = kept.split("\n");
    for (int i = 0; i < ks.length; i++) @PKG@.CookCfg.info(ks[i]);
    return msg + "\n" + kept;
  } catch (Throwable t) {
    @PKG@.CookCfg.warn("could not update cooking.properties to the 0.1.6 ingredient Cooking XP (the file is used as it is): " + t);
    return "";
  }
}""")

# ================= Cook: grading, tree, giving, XP =================
F(ck, "public static final long CHUNK = 400000L;")
F(ck, "public static final java.util.concurrent.ConcurrentHashMap EXISTS = new java.util.concurrent.ConcurrentHashMap();")
F(ck, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")
F(ck, "public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();")
F(ck, "public static final java.util.HashMap RATE = new java.util.HashMap();")
F(ck, "public static final java.util.concurrent.ConcurrentHashMap CAMP_TOLD = new java.util.concurrent.ConcurrentHashMap();")
Mk(ck, """
public static java.util.Map bridge() {
  synchronized (java.lang.System.class) {
    Object o = System.getProperties().get("skyy.bridge");
    if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
    return (java.util.Map) o;
  }
}""")
# 0.1.2 player Settings registry (research/Settings-Spec.md 1.3 helper, verbatim; SkyyMenu 0.2+). No SkyyMenu = no answer = on (today).
Mk(ck, """
public static boolean notifyOn(java.util.UUID u, String key) {
  if (u == null || key == null) return true;
  try {
    Object f = bridge().get("settings:fn:get");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  return true;
}""")
Mk(ck, """
public static void regSetting(String key, String label, String cat, boolean def, String help) {
  try {
    Object[] a = new Object[] { "SkyyCooking", key, label, cat, Boolean.valueOf(def), help };
    java.util.Map br = bridge();
    br.put("settings:def:" + key, a);
    Object f = br.get("settings:fn:register");
    if (f instanceof java.util.function.Function) ((java.util.function.Function) f).apply(a);
  } catch (Throwable t) { }
}""")
# the contract helper, verbatim (tools/PROFILES-CONTRACT.md)
Mk(ck, """
public static String pkey(java.util.UUID u) {
  try {
    Object f = bridge().get("profile:fn:key");
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(u);
      if (r instanceof String && ((String) r).length() > 0) return (String) r;
    }
  } catch (Throwable t) { }
  return u.toString();
}""")
Mk(ck, """
public static boolean busy(java.util.UUID u) {
  try { return bridge().get("profile:busy:" + u.toString()) != null; } catch (Throwable t) { return false; }
}""")
# Cooking level from SkyySkills 0.4; -1 = no SkyySkills (then: plain food, no XP)
Mk(ck, """
public static int level(java.util.UUID u) {
  try {
    Object f = bridge().get("skill:fn:level");
    if (!(f instanceof java.util.function.Function)) return -1;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, "Cooking" });
    if (!(r instanceof Number)) return 0;
    int v = ((Number) r).intValue();
    if (v < 0) v = 0;
    if (v > 1000) v = 1000;
    return v;
  } catch (Throwable t) { return 0; }
}""")
Mk(ck, """
public static int baseGrade(int level) {
  if (level <= 0) return 0;
  int g = level / 10;
  if (g > 10) g = 10;
  return g;
}""")
Mk(ck, """
public static int clampGrade(int g) {
  int m = @PKG@.CookCfg.MAX_GRADE;
  if (m > @PKG@.CookCfg.GEN_MAX) m = @PKG@.CookCfg.GEN_MAX;
  if (g > m) g = m;
  if (g < 0) g = 0;
  return g;
}""")
# Cooking tree node levels from SkyyTrees (bridge tree:fn:level (UUID, "Cooking.<Id>") -> Integer), clamped to each node's max
Mk(ck, """
public static int[] tree(java.util.UUID u) {
  int n = @PKG@.CookCfg.NODES.length;
  int[] t = new int[n];
  Object f = null;
  try { f = bridge().get("tree:fn:level"); } catch (Throwable x) { f = null; }
  if (!(f instanceof java.util.function.Function)) return t;
  for (int i = 0; i < n; i++) {
    try {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, "Cooking." + @PKG@.CookCfg.NODES[i] });
      if (r instanceof Number) {
        int v = ((Number) r).intValue();
        if (v < 0) v = 0;
        if (v > @PKG@.CookCfg.NODE_MAX[i]) v = @PKG@.CookCfg.NODE_MAX[i];
        t[i] = v;
      }
    } catch (Throwable x) { }
  }
  return t;
}""")
Mk(ck, """
public static boolean anyTree(int[] t) {
  for (int i = 0; i < t.length; i++) if (t[i] > 0) return true;
  return false;
}""")
# the Grade a Cooking Bench guarantees: level/10 (max 10) + 1 with Master Chef (CMaster, node 9) >= 1, clamped to maxGrade
Mk(ck, """
public static int benchGrade(int lv, int[] t) {
  int mc = 0;
  if (t != null && t.length > 9 && t[9] >= 1) mc = 1;
  return clampGrade(baseGrade(lv) + mc);
}""")
Mk(ck, """
public static int guaranteed(java.util.UUID u) {
  int lv = level(u);
  if (lv < 0) return 0;
  return benchGrade(lv, tree(u));
}""")
Mk(ck, """
public static double rnd() {
  return java.util.concurrent.ThreadLocalRandom.current().nextDouble();
}""")
# per-node chance fractions. SkyyTrees 0.1 publishes tree:fn:bonus (same argument -> Double = level x per from ITS trees.properties;
# Master Chef = (level - 1) x per), so Skyy tunes the numbers in one place; without it: level x tree.<Id>.per of cooking.properties.
Mk(ck, """
public static double[] chances(java.util.UUID u, int[] t) {
  int n = t.length;
  double[] c = new double[n];
  double[] p = @PKG@.CookCfg.PER;
  Object f = null;
  try { f = bridge().get("tree:fn:bonus"); } catch (Throwable x) { f = null; }
  for (int i = 0; i < n; i++) {
    double v = 0.0;
    if (t[i] <= 0) { c[i] = 0.0; continue; }
    boolean got = false;
    if (f instanceof java.util.function.Function) {
      try {
        Object r = ((java.util.function.Function) f).apply(new Object[] { u, "Cooking." + @PKG@.CookCfg.NODES[i] });
        if (r instanceof Number) { v = ((Number) r).doubleValue(); got = true; }
      } catch (Throwable x) { got = false; }
    }
    if (!got) v = (i == 9 ? (t[i] - 1) : t[i]) * p[i];
    if (Double.isNaN(v) || v < 0.0) v = 0.0;
    if (v > 1.0) v = 1.0;
    c[i] = v;
  }
  return c;
}""")
# combined +1 Grade chance for a dish tier: Gourmet + Gourmet II + the tier's mastery + Master Chef levels 2-5 (capped at 100 %)
Mk(ck, """
public static double upChance(int tier, double[] c) {
  double v = c[0] + c[7] + c[9];
  if (tier == 1) v = v + c[3];
  else if (tier == 2) v = v + c[4];
  else if (tier == 3) v = v + c[5];
  if (v > 1.0) v = 1.0;
  return v;
}""")
Mk(ck, """
public static double sigChance(double[] c) {
  if (c[8] > 1.0) return 1.0;
  return c[8];
}""")
# one roll per dish (Cooking spec 7.2): g = level/10 (max 10) + Master Chef; +1 on the combined chance, or +2 on Signature Dish
Mk(ck, """
public static int roll(int level, int tier, int[] t, double[] c, int[] bonus) {
  int g = benchGrade(level, t);
  int b = 0;
  double p1 = upChance(tier, c);
  if (p1 > 0.0 && rnd() < p1) b = 1;
  double p2 = sigChance(c);
  if (p2 > 0.0 && rnd() < p2) b = 2;
  bonus[0] = b;
  return clampGrade(g + b);
}""")
Mk(ck, """
public static String gradedId(String dish, int g) {
  return "Skyy_Cook_" + dish + "_G" + g;
}""")
# an id is only ever handed out once the live item asset map has it (asset pack failed = plain food, never an Invalid Item)
Mk(ck, """
public static boolean exists(String id) {
  if (id == null) return false;
  if (EXISTS.containsKey(id)) return true;
  boolean ok = false;
  try { ok = @ITM@.getAssetMap().getAsset(id) != null; } catch (Throwable t) { ok = false; }
  if (ok) EXISTS.put(id, Boolean.TRUE);
  else @PKG@.CookCfg.once("asset:" + id, "item asset " + id + " is not loaded - handing out the plain item instead (did the SkyyCooking asset pack load? check the server log for asset errors)");
  return ok;
}""")
Mk(ck, """
public static boolean isCooking(@CRR@ rc) {
  if (rc == null) return false;
  @BRQ@[] b = rc.getBenchRequirement();
  if (b == null) return false;
  for (int i = 0; i < b.length; i++) if (b[i] != null && "Cookingbench".equals(b[i].id)) return true;
  return false;
}""")
Mk(ck, """
public static String outId(@CRR@ rc) {
  @MQ@ po = rc.getPrimaryOutput();
  if (po == null) return null;
  return po.getItemId();
}""")
Mk(ck, """
public static int outQty(@CRR@ rc) {
  @MQ@ po = rc.getPrimaryOutput();
  if (po == null) return 1;
  int q = po.getQuantity();
  return q < 1 ? 1 : q;
}""")
Mk(ck, """
public static boolean creative(@ST@ st, @REF@ r) {
  if (@PKG@.CookCfg.CREATIVE) return false;
  try {
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    return p != null && p.getGameMode() == @GM@.Creative;
  } catch (Throwable t) { return false; }
}""")
# the same check for a caller that only has the UUID (cook:fn:out): 1 = creative, 0 = not (or creativeGrades=true), -1 = unknown
# (offline, no live entity, or not called on that player's world thread - components are only read on the world thread)
Mk(ck, """
public static int creativeOf(java.util.UUID u) {
  if (@PKG@.CookCfg.CREATIVE) return 0;
  try {
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return -1;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return -1;
    @ST@ st = r.getStore();
    if (st == null || !st.isInThread()) return -1;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return -1;
    return p.getGameMode() == @GM@.Creative ? 1 : 0;
  } catch (Throwable t) { return -1; }
}""")
# Frugal: one random ITEM-id input (never a resource type such as Fuel / Meats, never a '*' state wildcard)
Mk(ck, """
public static String frugalPick(@CRR@ rc) {
  @MQ@[] in = rc.getInput();
  if (in == null) return null;
  java.util.ArrayList c = new java.util.ArrayList();
  for (int i = 0; i < in.length; i++) {
    if (in[i] == null) continue;
    String id = in[i].getItemId();
    if (id == null || id.length() == 0 || id.startsWith("*") || in[i].getResourceTypeId() != null) continue;
    if (exists(id)) c.add(id);
  }
  if (c.isEmpty()) return null;
  int k = (int) (rnd() * c.size());
  if (k >= c.size()) k = c.size() - 1;
  return (String) c.get(k);
}""")
# The plan for `units` finished crafts of rc by u. null = nothing to change (vanilla output, no tree extra).
# [0] = full replacement output List (then the caller cancels the Post) or null, [1] = extra stacks List or null (given NEXT TO the
# output), [2] = chat note or null, [3] = Integer Grade of the last dish.
Mk(ck, """
public static Object[] plan(java.util.UUID u, @CRR@ rc, int units) {
  if (!@PKG@.CookCfg.ENABLED || rc == null) return null;
  int lv = level(u);
  if (lv < 0) return null;
  String out = outId(rc);
  if (out == null) return null;
  int tier = @PKG@.CookCfg.tierOf(out);
  boolean ingr = @PKG@.CookCfg.isIngredient(out);
  int[] t = tree(u);
  boolean tr = anyTree(t);
  if (!tr && (tier == 0 || baseGrade(lv) == 0)) return null;
  double[] ch = new double[t.length];
  if (tr) ch = chances(u, t);
  java.util.ArrayList all = new java.util.ArrayList();
  java.util.ArrayList ex = new java.util.ArrayList();
  boolean changed = false;
  String note = null;
  int lastG = 0;
  int[] bonus = new int[1];
  for (int k = 0; k < units; k++) {
    java.util.List outs = @CRM@.getOutputItemStacks(rc, 1);
    int g = 0;
    bonus[0] = 0;
    if (tier > 0) g = roll(lv, tier, t, ch, bonus);
    lastG = g;
    String dishGiven = null;
    for (int i = 0; outs != null && i < outs.size(); i++) {
      @IS@ s = (@IS@) outs.get(i);
      if (s == null || s.getQuantity() <= 0) continue;
      String id = s.getItemId();
      if (g > 0 && @PKG@.CookCfg.tierOf(id) > 0) {
        String gid = gradedId(id, g);
        if (exists(gid)) { s = new @IS@(gid, s.getQuantity()); changed = true; }
      }
      if (dishGiven == null && id.equals(out)) dishGiven = s.getItemId();
      all.add(s);
    }
    if (bonus[0] > 0 && dishGiven != null && !dishGiven.equals(out)) note = (bonus[0] == 2 ? "Signature Dish! " : "Gourmet! ") + @PKG@.CookCfg.nameOf(out) + " came out Grade " + g;
    if (tier > 0 && ch[1] > 0.0 && dishGiven != null && rnd() < ch[1]) {
      ex.add(new @IS@(dishGiven, outQty(rc)));
      note = "Batch Cook! +" + outQty(rc) + " " + @PKG@.CookCfg.nameOf(out) + (g > 0 ? " (Grade " + g + ")" : "");
    }
    if (ingr && ch[6] > 0.0 && rnd() < ch[6]) {
      ex.add(new @IS@(out, outQty(rc)));
      note = "Prep Cook! double " + @PKG@.CookCfg.nameOf(out);
    }
    if (ch[2] > 0.0 && rnd() < ch[2]) {
      String fid = frugalPick(rc);
      if (fid != null) { ex.add(new @IS@(fid, 1)); note = "Frugal! got 1 " + @PKG@.CookCfg.nameOf(fid) + " back"; }
    }
  }
  if (!changed && ex.isEmpty()) return null;
  Object rep = null;
  if (changed) rep = all;
  Object ext = null;
  if (!ex.isEmpty()) ext = ex;
  return new Object[] { rep, ext, note, Integer.valueOf(lastG) };
}""")
# hand stacks out exactly like vanilla giveOutput (addOrDropItemStack with the caller's accessor), storage first
Mk(ck, """
public static void give(@CAC@ acc, @REF@ r, @IC@ c, java.util.List l) {
  if (l == null) return;
  for (int i = 0; i < l.size(); i++) {
    @IS@ s = (@IS@) l.get(i);
    if (s == null || s.getQuantity() <= 0) continue;
    @SIC@.addOrDropItemStack(acc, r, c, s);
  }
}""")
Mk(ck, """
public static synchronized boolean allowXp(java.util.UUID u, long base) {
  long cap = @PKG@.CookCfg.MAX_PER_MIN;
  if (cap <= 0L) return true;
  long now = System.currentTimeMillis();
  long[] w = (long[]) RATE.get(u);
  if (w == null) { w = new long[] { now, 0L, 0L }; RATE.put(u, w); }
  if (now - w[0] >= 60000L) { w[0] = now; w[1] = 0L; }
  if (w[1] + base > cap) {
    if (now - w[2] >= 60000L) { w[2] = now; @PKG@.CookCfg.warn("Cooking XP cap reached for " + u + " (" + cap + " base XP per minute, maxXpPerMinute) - XP of this craft dropped, the dish was still given"); }
    return false;
  }
  w[1] = w[1] + base;
  return true;
}""")
Mk(ck, """
public static long sendXp(java.util.UUID u, long amt, String src, String key) {
  if (amt <= 0L) return 0L;
  Object f = bridge().get("skill:fn:addxp");
  if (!(f instanceof java.util.function.Function)) {
    @PKG@.CookCfg.once("noaddxp", "SkyySkills' XP bridge skill:fn:addxp is missing - cooking pays no XP (needs SkyySkills 0.4 or newer)");
    return 0L;
  }
  long left = amt;
  long sent = 0L;
  int guard = 0;
  while (left > 0L && guard < 64) {
    guard++;
    long c = left > CHUNK ? CHUNK : left;
    Object ok = null;
    try { ok = ((java.util.function.Function) f).apply(new Object[] { u, "Cooking", Long.valueOf(c), src, key }); } catch (Throwable t) { ok = null; }
    if (!Boolean.TRUE.equals(ok)) {
      @PKG@.CookCfg.every("refused", 60000L, "SkyySkills refused " + c + " Cooking XP for " + u + " (" + src + ") - is Cooking in SkyySkills' bridge.addxp.skills, or was its per-minute bridge cap hit?");
      return sent;
    }
    sent = sent + c;
    left = left - c;
  }
  return sent;
}""")
# 0.1.2: key = the player Settings switch (null = never gated). The admin master switch (messages=) wins first; the player's switch is
# checked BEFORE the LAST throttle, so a hidden line does not use up the 2.5 s cooldown of a line that is shown (Settings-Spec 1.3 / 3.6)
Mk(ck, """
public static void tell(@PR@ pr, String msg, boolean force, String key) {
  if (pr == null || msg == null || !@PKG@.CookCfg.MESSAGES) return;
  if (key != null && !notifyOn(pr.getUuid(), key)) return;
  long now = System.currentTimeMillis();
  Long l = (Long) LAST.get(pr.getUuid());
  if (!force && l != null && now - l.longValue() < 2500L) return;
  LAST.put(pr.getUuid(), Long.valueOf(now));
  pr.sendMessage(@MSG@.raw("[Cooking] " + msg).color("#ffb070"));
}""")
Mk(ck, """
public static void tell(@PR@ pr, String msg, boolean force) {
  tell(pr, msg, force, (String) null);
}""")
Mk(ck, """
public static String x2(double v) {
  long c = Math.round(v * 100.0);
  long f = c % 100L;
  return (c / 100L) + "." + (f < 10L ? "0" : "") + f;
}""")
Mk(ck, """
public static String pc(double v) {
  long c = Math.round(v * 1000.0);
  long f = c % 10L;
  return (c / 10L) + (f == 0L ? "" : "." + f) + "%";
}""")
# 0.1.4: strength and duration shown separately everywhere (CookCfg.SF / DF = the factors baked into the assets). sd = the chat Grade line
# form, sdShort = the short form without a comma (the Skills Stats page uses dashes instead of commas)
Mk(ck, """
public static String sd(int g) {
  return "heal and buffs x" + x2(@PKG@.CookCfg.SF[g]) + " stronger, buffs last x" + x2(@PKG@.CookCfg.DF[g]) + " longer";
}""")
Mk(ck, """
public static String sdShort(int g) {
  return "x" + x2(@PKG@.CookCfg.SF[g]) + " stronger and x" + x2(@PKG@.CookCfg.DF[g]) + " longer";
}""")

# ================= 0.1.1 Campfire accessory (cook:fn:campfire; contract in the 0.1.1 docstring section) =================
# a vanilla Campfire-bench recipe (the only recipes the accessory cooks)
Mk(ck, """
public static boolean isCampfire(@CRR@ rc) {
  if (rc == null) return false;
  @BRQ@[] b = rc.getBenchRequirement();
  if (b == null) return false;
  for (int i = 0; i < b.length; i++) if (b[i] != null && "Campfire".equals(b[i].id)) return true;
  return false;
}""")
# a[1] -> the campfire dish id. ONLY a Campfire-bench RECIPE id whose primary output is listed in CAMP; else null. A bare dish id is
# refused (it cannot prove a Campfire craft - the Cooking Bench makes the same dishes via Skyy_Cook_Recipe_*), and so is every
# Cooking Bench recipe (isCampfire false). Engine ids of item recipes are "<ItemId>_Recipe_Generated_<n>", never a bare dish id.
Mk(ck, """
public static String campRecipeDish(String what) {
  if (what == null) return null;
  String w = what.trim();
  if (w.length() == 0) return null;
  if (@PKG@.CookCfg.campIndex(w) >= 0) {
    @PKG@.CookCfg.once("campfn:bare", "cook:fn:campfire was passed the bare dish id " + w + " - refused (normal output, no XP): pass the Campfire recipe id, String.valueOf(recipe.getId())");
    return null;
  }
  try {
    @CRR@ rc = (@CRR@) @CRR@.getAssetMap().getAsset(w);
    if (rc == null || !isCampfire(rc)) return null;
    String out = outId(rc);
    if (@PKG@.CookCfg.campIndex(out) >= 0) return out;
  } catch (Throwable t) { }
  return null;
}""")
# dish id -> the id of the vanilla Campfire-bench recipe that makes it (for /cookadmin campfire, so it tests the strict path); null = none
Mk(ck, """
public static String campRecipeFor(String dish) {
  if (dish == null) return null;
  try {
    java.util.Iterator it = @CRR@.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @CRR@)) continue;
      @CRR@ rc = (@CRR@) o;
      if (!isCampfire(rc)) continue;
      if (dish.equals(outId(rc))) return String.valueOf(rc.getId());
    }
  } catch (Throwable t) { }
  return null;
}""")
# bench Grade g -> campfire Grade: the highest Grade 0..g whose STRENGTH S <= 1 + f x (S(g) - 1) (0.1.4: CookCfg.MUL = S, until 0.1.3 the
# one multiplier M; this method is unchanged; Python mirror camp_grade)
Mk(ck, """
public static int campGrade(int g, double f) {
  int b = clampGrade(g);
  if (b <= 0 || f <= 0.0) return 0;
  if (f >= 1.0) return b;
  double target = 1.0 + f * (@PKG@.CookCfg.MUL[b] - 1.0) + 1.0E-9;
  int c = 0;
  for (int k = 1; k <= b; k++) if (@PKG@.CookCfg.MUL[k] <= target) c = k;
  return c;
}""")
# 0.1.4: the campfire hint text on its own (the harness runs it) - the campfire Grade with its strength AND duration
Mk(ck, """
public static String campText(int g, int c) {
  String s = "Campfire accessory = quick emergency cooking: your campfire dishes come out ";
  if (c > 0) s = s + "Grade " + c + " (" + pc(@PKG@.CookCfg.CAMP_BUFF) + " of your Grade " + g + " strength bonus - " + sd(c) + ")";
  else if (g > 0) s = s + "plain (" + pc(@PKG@.CookCfg.CAMP_BUFF) + " of your Grade " + g + " bonus rounds down to Grade 0)";
  else s = s + "plain";
  return s + " and pay " + pc(@PKG@.CookCfg.CAMP_XP) + " of the Cooking XP. A Cooking Bench gives the full Grade and XP.";
}""")
# one chat hint per session, and again when the campfire Grade rises (messages=true)
Mk(ck, """
public static void campHint(java.util.UUID u, int g, int c) {
  try {
    if (!@PKG@.CookCfg.MESSAGES) return;
    Integer told = (Integer) CAMP_TOLD.get(u);
    if (told != null && told.intValue() >= c) return;
    CAMP_TOLD.put(u, Integer.valueOf(c));
    @PR@ pr = @UNI@.get().getPlayer(u);
    if (pr == null || !pr.isValid()) return;
    tell(pr, campText(g, c), true, "cooking.grade");
  } catch (Throwable t) { }
}""")
# cross-check fix: the part of `base` that still fits this minute's maxXpPerMinute window (the window allowXp keeps, same lock), booked;
# the rest is dropped with one log line per minute. allowXp is all-or-nothing, which is right for one bench dish per Post but made one
# big instant accessory batch (e.g. "All 2000" raw meat) pay no XP at all.
Mk(ck, """
public static synchronized long allowXpPart(java.util.UUID u, long base) {
  if (base <= 0L) return 0L;
  long cap = @PKG@.CookCfg.MAX_PER_MIN;
  if (cap <= 0L) return base;
  long now = System.currentTimeMillis();
  long[] w = (long[]) RATE.get(u);
  if (w == null) { w = new long[] { now, 0L, 0L }; RATE.put(u, w); }
  if (now - w[0] >= 60000L) { w[0] = now; w[1] = 0L; }
  long room = cap - w[1];
  if (room < 0L) room = 0L;
  long got = base < room ? base : room;
  if (got < base && now - w[2] >= 60000L) { w[2] = now; @PKG@.CookCfg.warn("Cooking XP cap reached for " + u + " (" + cap + " base XP per minute, maxXpPerMinute) - a Campfire accessory batch paid " + got + " of " + base + " base XP, the dishes were still given"); }
  w[1] = w[1] + got;
  return got;
}""")
# THE campfire cook. null = not a campfire dish. Else Object[]{ String id to give, Integer bench Grade G, Integer campfire Grade c,
# Long XP sent to SkyySkills, String why-plain or null }. crafts <= 0 = preview (no XP, no hint).
Mk(ck, """
public static Object[] campfire(java.util.UUID u, String what, int crafts, String expectKey, Boolean creativeFlag) {
  if (u == null) return null;
  String dish = campRecipeDish(what);
  if (dish == null) return null;
  int n = crafts;
  boolean preview = n <= 0;
  if (n > 10000) {
    @PKG@.CookCfg.every("campfn:clamp", 60000L, "cook:fn:campfire: " + n + " crafts of " + dish + " in one call for " + u + " - Cooking XP is paid for 10,000 of them only (the caller hands out all " + n + " dishes); send big batches in parts");
    n = 10000;
  }
  String key = pkey(u);
  String why = null;
  if (!@PKG@.CookCfg.ENABLED) why = "graded cooking is off (enabled=false)";
  else if (busy(u)) why = "profile loading (profile:busy)";
  else if (expectKey != null && !expectKey.equals(key)) why = "the caller's profile key differs";
  else if (!@PKG@.CookCfg.CREATIVE) {
    if (creativeFlag != null && creativeFlag.booleanValue()) why = "creative mode";
    else {
      int cm = creativeOf(u);
      if (cm == 1) why = "creative mode";
      else if (cm < 0 && creativeFlag == null) {
        why = "game mode unreadable (not on the player's world thread)";
        @PKG@.CookCfg.once("campfn:mode", "cook:fn:campfire: cannot read the game mode of " + u + " (not on that player's world thread?) and the caller passed no creative flag - plain dish and no XP. Call it on the world thread or pass Object[]{UUID, id, crafts, expectKey, Boolean creative}.");
      }
    }
  }
  int lv = -1;
  if (why == null) {
    lv = level(u);
    if (lv < 0) why = "SkyySkills is not loaded";
  }
  if (why != null) return new Object[] { dish, Integer.valueOf(0), Integer.valueOf(0), Long.valueOf(0L), why };
  int g = benchGrade(lv, tree(u));
  int c = campGrade(g, @PKG@.CookCfg.CAMP_BUFF);
  String id = dish;
  if (c > 0 && @PKG@.CookCfg.GRADED.contains(dish)) {
    String gid = gradedId(dish, c);
    if (exists(gid)) id = gid;
    else c = 0;
  } else c = 0;
  long sent = 0L;
  if (!preview) {
    long base = Math.round((double) @PKG@.CookCfg.xpFor(dish) * (double) n * @PKG@.CookCfg.CAMP_XP);
    long paid = allowXpPart(u, base);
    if (paid > 0L) sent = sendXp(u, Math.round(paid * @PKG@.CookCfg.XP_MULT), "cook:campfire:" + dish, key);
    campHint(u, g, c);
  }
  return new Object[] { id, Integer.valueOf(g), Integer.valueOf(c), Long.valueOf(sent), null };
}""")
# 0.1.4: the /cooking reply as lines (CookingCmd only sends them; the harness runs this with fake bridge functions). The same lines and
# order as 0.1.3's CookingCmd; the Next and campfire lines now name strength AND duration (sdShort), the Grade line uses sd.
Mk(ck, """
public static java.util.List cookingLines(java.util.UUID u) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (!@PKG@.CookCfg.ENABLED) { out.add("[Cooking] graded cooking is turned off on this server (enabled=false)."); return out; }
  int lv = level(u);
  if (lv < 0) { out.add("[Cooking] SkyySkills is not installed - food comes out plain (Grade 0) and cooking gives no XP."); return out; }
  int[] t = tree(u);
  int base = baseGrade(lv);
  int g = benchGrade(lv, t);
  out.add("[Cooking] Cooking " + lv + " - your food comes out Grade " + g + ": " + sd(g) + ".");
  if (base < 10 && base + 1 <= clampGrade(99)) {
    int ng = clampGrade(base + 1 + (t[9] >= 1 ? 1 : 0));
    out.add("[Cooking] Next: Grade " + ng + " (" + sdShort(ng) + ") at Cooking " + ((base + 1) * 10) + ".");
  } else if (base >= 10) out.add("[Cooking] Grades 11 and 12 come only from the Cooking skill tree (SkyyTrees).");
  int cg = campGrade(g, @PKG@.CookCfg.CAMP_BUFF);
  out.add("[Cooking] Campfire accessory (quick cooking in /craft, an emergency cook): " + @PKG@.CookCfg.campNames() + " come out " + (cg > 0 ? "Grade " + cg + " (" + sdShort(cg) + ")" : "plain") + " and pay " + pc(@PKG@.CookCfg.CAMP_XP) + " of the Cooking XP.");
  if (anyTree(t)) {
    double[] c = chances(u, t);
    String s = "[Cooking] Skill tree - +1 Grade: T1 " + pc(upChance(1, c)) + " T2 " + pc(upChance(2, c)) + " T3 " + pc(upChance(3, c));
    s = s + " - +2 Grades " + pc(sigChance(c)) + " - extra dish " + pc(c[1]) + " - ingredient back " + pc(c[2]) + " - double ingredients " + pc(c[6]);
    if (t[9] >= 1) s = s + " - Master Chef +1 Grade";
    out.add(s);
  }
  out.add("[Cooking] Earn XP at a Cooking Bench (ingredients can come from your bags) - pies and Caesar salad pay the most. A placed Campfire gives plain food and no XP; its dishes are on the Cooking Bench too (full Grade and XP).");
  if (!exists(gradedId(@PKG@.CookCfg.DISHES[3], 1))) out.add("[Cooking] WARNING: the graded dish assets are not loaded - food comes out plain. Tell an admin (server log).");
  return out;
}""")

# ================= CookXpTask: the deferred award (world thread, after every other system saw the Post) =================
xpt.addInterface(pool.get("java.lang.Runnable"))
for _d in ("public %s ev;" % CRE, "public java.util.UUID u;", "public String key;", "public String out;", "public long base;",
           "public boolean gave;", "public String note;", "public int grade;"):
    F(xpt, _d)
Ct(xpt, """
public CookXpTask(@CRE@ ev, java.util.UUID u, String key, String out, long base, boolean gave, String note, int grade) {
  this.ev = ev; this.u = u; this.key = key; this.out = out; this.base = base; this.gave = gave; this.note = note; this.grade = grade;
}""")
Mk(xpt, """
public void run() {
  try {
    if (this.ev != null && this.ev.isCancelled() && !this.gave) return;
    @PR@ pr = @UNI@.get().getPlayer(this.u);
    if (pr == null || !pr.isValid()) return;
    if (!this.key.equals(@PKG@.Cook.pkey(this.u))) return;
    Integer told = (Integer) @PKG@.Cook.TOLD.get(this.u);
    if (this.gave && this.grade > 0 && (told == null || told.intValue() < this.grade)) {
      @PKG@.Cook.TOLD.put(this.u, Integer.valueOf(this.grade));
      @PKG@.Cook.tell(pr, "Your food now comes out Grade " + this.grade + " - heal and buffs x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[this.grade]) + " stronger, buffs last x" + @PKG@.Cook.x2(@PKG@.CookCfg.DF[this.grade]) + " longer. /cooking for details.", true, "cooking.grade");
    } else if (this.note != null) @PKG@.Cook.tell(pr, this.note, false, "cooking.procs");
    if (this.base <= 0L) return;
    if (!@PKG@.Cook.allowXp(this.u, this.base)) return;
    long amt = Math.round(this.base * @PKG@.CookCfg.XP_MULT);
    @PKG@.Cook.sendXp(this.u, amt, "cook:" + this.out, this.key);
  } catch (Throwable t) { @PKG@.CookCfg.warn("cooking XP task failed: " + t); }
}""")

# ================= CookSys: THE craft hook (EntityEventSystem on CraftRecipeEvent$Post; the mod's only system class) =================
Ct(csy, "public CookSys() { super(@CRP@.class); }")
Mk(csy, """
public @QRY@ getQuery() {
  return com.hypixel.hytale.component.Archetype.empty();
}""")
Mk(csy, """
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!@PKG@.CookCfg.ENABLED) return;
    @CRE@ e = (@CRE@) ev;
    @CRR@ rc = e.getCraftedRecipe();
    if (rc == null || !@PKG@.Cook.isCooking(rc)) return;
    if (e.isCancelled()) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    if (@PKG@.Cook.creative(st, r)) return;
    Object ext = st.getExternalData();
    if (!(ext instanceof @EST@)) return;
    @WLD@ w = ((@EST@) ext).getWorld();
    if (w == null) return;
    java.util.UUID u = pr.getUuid();
    if (@PKG@.Cook.busy(u)) return;
    int units = 1;
    if (rc.getTimeSeconds() <= 0.0f) units = Math.max(1, e.getQuantity());
    if (units > 10000) units = 10000;
    String key = @PKG@.Cook.pkey(u);
    String out = @PKG@.Cook.outId(rc);
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    Object[] plan = null;
    if (p != null) plan = @PKG@.Cook.plan(u, rc, units);
    boolean gave = false;
    String note = null;
    int grade = 0;
    if (plan != null) {
      @IC@ c = p.getInventory().getCombinedStorageHotbarBackpack();
      if (plan[0] != null) {
        e.setCancelled(true);
        @PKG@.Cook.give(buf, r, c, (java.util.List) plan[0]);
        gave = true;
      }
      if (plan[1] != null) @PKG@.Cook.give(buf, r, c, (java.util.List) plan[1]);
      note = (String) plan[2];
      grade = ((Integer) plan[3]).intValue();
    }
    long base = @PKG@.CookCfg.xpFor(out) * (long) units;
    w.execute(new @PKG@.CookXpTask(e, u, key, out, base, gave, note, grade));
  } catch (Throwable t) { @PKG@.CookCfg.every("sys", 30000L, "CookSys failed (vanilla output kept unless the Post was already cancelled): " + t); }
}""")

# ================= bridge functions =================
gfn.addInterface(pool.get("java.util.function.Function"))
Ct(gfn, "public CookGradeFn() { }")
Mk(gfn, """
public Object apply(Object arg) {
  try {
    Object a = arg;
    if (a instanceof Object[]) a = ((Object[]) a)[0];
    if (!(a instanceof java.util.UUID)) return Integer.valueOf(0);
    return Integer.valueOf(@PKG@.Cook.guaranteed((java.util.UUID) a));
  } catch (Throwable t) { return Integer.valueOf(0); }
}""")
ofn.addInterface(pool.get("java.util.function.Function"))
Ct(ofn, "public CookOutFn() { }")
Mk(ofn, """
public Object apply(Object arg) {
  try {
    Object[] a = (Object[]) arg;
    java.util.UUID u = (java.util.UUID) a[0];
    @CRR@ rc = (@CRR@) @CRR@.getAssetMap().getAsset(String.valueOf(a[1]));
    if (rc == null || !@PKG@.Cook.isCooking(rc)) return null;
    int n = ((Number) a[2]).intValue();
    if (n < 1) n = 1;
    if (n > 10000) n = 10000;
    String key = @PKG@.Cook.pkey(u);
    if (a.length > 3 && a[3] != null && !String.valueOf(a[3]).equals(key)) return null;
    java.util.ArrayList res = new java.util.ArrayList();
    boolean plain = !@PKG@.CookCfg.ENABLED || @PKG@.Cook.busy(u);
    if (!plain && !@PKG@.CookCfg.CREATIVE) {
      boolean declared = a.length > 4 && a[4] instanceof Boolean;
      if (declared && ((Boolean) a[4]).booleanValue()) plain = true;
      else {
        int cm = @PKG@.Cook.creativeOf(u);
        if (cm == 1) plain = true;
        else if (cm < 0 && !declared) {
          plain = true;
          @PKG@.CookCfg.once("outfn:mode", "cook:fn:out: cannot read the game mode of " + u + " (not on that player's world thread?) and the caller passed no creative flag - plain output and no XP. Pass Object[]{UUID, recipeId, crafts, expectKey, Boolean creative}.");
        }
      }
    }
    if (plain) { res.addAll(@CRM@.getOutputItemStacks(rc, n)); return res; }
    Object[] plan = @PKG@.Cook.plan(u, rc, n);
    if (plan != null && plan[0] != null) res.addAll((java.util.List) plan[0]);
    else res.addAll(@CRM@.getOutputItemStacks(rc, n));
    if (plan != null && plan[1] != null) res.addAll((java.util.List) plan[1]);
    String out = @PKG@.Cook.outId(rc);
    long base = @PKG@.CookCfg.xpFor(out) * (long) n;
    if (base > 0L && @PKG@.Cook.allowXp(u, base)) @PKG@.Cook.sendXp(u, Math.round(base * @PKG@.CookCfg.XP_MULT), "cook:" + out + ":bridge", key);
    return res;
  } catch (Throwable t) { @PKG@.CookCfg.every("outfn", 30000L, "cook:fn:out failed: " + t); return null; }
}""")

# cook:fn:campfire (0.1.1): apply(Object[]{UUID, String recipeOrOutputId, Number crafts [, String expectKey [, Boolean creative]]})
# -> String item id to give (graded or plain) or null (not a campfire dish / malformed / error). World thread. Docstring 0.1.1 section.
cfn.addInterface(pool.get("java.util.function.Function"))
Ct(cfn, "public CookCampFn() { }")
Mk(cfn, """
public Object apply(Object arg) {
  try {
    if (!(arg instanceof Object[])) return null;
    Object[] a = (Object[]) arg;
    if (a.length < 3 || !(a[0] instanceof java.util.UUID) || a[1] == null || !(a[2] instanceof Number)) return null;
    String ek = null;
    if (a.length > 3 && a[3] != null) ek = String.valueOf(a[3]);
    Boolean cf = null;
    if (a.length > 4 && a[4] instanceof Boolean) cf = (Boolean) a[4];
    Object[] r = @PKG@.Cook.campfire((java.util.UUID) a[0], String.valueOf(a[1]), ((Number) a[2]).intValue(), ek, cf);
    if (r == null) return null;
    return r[0];
  } catch (Throwable t) { @PKG@.CookCfg.every("campfn", 30000L, "cook:fn:campfire failed (the caller gives its plain output): " + t); return null; }
}""")
# cook:fn:campfactors (0.1.1): apply(anything) -> Object[]{Double buffFactor, Double xpFactor, Boolean enabled} - the LIVE values (UI text)
ifn.addInterface(pool.get("java.util.function.Function"))
Ct(ifn, "public CookCampInfoFn() { }")
Mk(ifn, """
public Object apply(Object arg) {
  return new Object[] { Double.valueOf(@PKG@.CookCfg.CAMP_BUFF), Double.valueOf(@PKG@.CookCfg.CAMP_XP), Boolean.valueOf(@PKG@.CookCfg.ENABLED) };
}""")

# skill:stats:Cooking (SkyySkills 0.4 Stats page hook): apply(Object[]{UUID, Integer level, Boolean next}) -> List of String (<= 5 lines,
# dashes instead of commas and colons like the rest of that page)
sfn.addInterface(pool.get("java.util.function.Function"))
Ct(sfn, "public CookStatsFn() { }")
Mk(sfn, """
public Object apply(Object arg) {
  java.util.ArrayList out = new java.util.ArrayList();
  try {
    Object[] a = (Object[]) arg;
    java.util.UUID u = (java.util.UUID) a[0];
    int lv = ((Number) a[1]).intValue();
    boolean next = Boolean.TRUE.equals(a[2]);
    if (!@PKG@.CookCfg.ENABLED) { if (!next) out.add("Graded cooking is turned off on this server"); return out; }
    int[] t = @PKG@.Cook.tree(u);
    int m = 0;
    if (t[9] >= 1) m = 1;
    int base = @PKG@.Cook.baseGrade(lv);
    if (next) {
      int nl = lv + 1;
      if (nl % 10 == 0 && nl / 10 <= 10) {
        int ng = @PKG@.Cook.clampGrade(@PKG@.Cook.baseGrade(nl) + m);
        if (ng > @PKG@.Cook.clampGrade(base + m)) out.add("Grade " + ng + " food - heal and buffs x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[ng]) + " stronger and lasting x" + @PKG@.Cook.x2(@PKG@.CookCfg.DF[ng]) + " longer");
      }
      return out;
    }
    int g = @PKG@.Cook.benchGrade(lv, t);
    out.add("Food you cook - Grade " + g + " - heal and buffs x" + @PKG@.Cook.x2(@PKG@.CookCfg.SF[g]) + " stronger - buffs last x" + @PKG@.Cook.x2(@PKG@.CookCfg.DF[g]) + " longer");
    if (base < 10) {
      int ng = @PKG@.Cook.clampGrade(base + 1 + m);
      if (ng > g) out.add("Next Grade - Grade " + ng + " at Cooking " + ((base + 1) * 10) + " - " + @PKG@.Cook.sdShort(ng));
    } else out.add("Grades 11 and 12 come only from the Cooking skill tree");
    int cg = @PKG@.Cook.campGrade(g, @PKG@.CookCfg.CAMP_BUFF);
    out.add("Campfire accessory - " + (cg > 0 ? "Grade " + cg + " food " + @PKG@.Cook.sdShort(cg) : "plain food") + " - " + @PKG@.Cook.pc(@PKG@.CookCfg.CAMP_XP) + " of the XP");
    if (@PKG@.Cook.anyTree(t)) {
      double[] c = @PKG@.Cook.chances(u, t);
      out.add("Skill tree - " + @PKG@.Cook.pc(@PKG@.Cook.upChance(3, c)) + " chance of +1 Grade on pies - " + @PKG@.Cook.pc(@PKG@.Cook.sigChance(c)) + " of +2 - " + @PKG@.Cook.pc(c[1]) + " extra dish - " + @PKG@.Cook.pc(c[2]) + " ingredient back");
    }
    if (!@PKG@.Cook.exists(@PKG@.Cook.gradedId(@PKG@.CookCfg.DISHES[3], 1))) out.add("WARNING - graded dish assets are not loaded - food comes out plain");
  } catch (Throwable t) { }
  return out;
}""")

# ================= commands =================
# /cookadmin give <dish> <grade>
F(gcmd, "public %s dishArg;" % RA)
F(gcmd, "public %s gradeArg;" % RA)
Ct(gcmd, """
public CookGiveCmd() {
  super("give", "(admin) Give 5 dishes of a Grade: /cookadmin give Food_Pie_Meat 5 (grade 0-12, 0 = plain)");
  this.dishArg = withRequiredArg("dish", "Food_Pie_Meat, pie_meat, Food_Bread, ... (the 15 graded dishes)", @ATY@.STRING);
  this.gradeArg = withRequiredArg("grade", "0-12", @ATY@.STRING);
  requirePermission("skyycooking.admin");
  setPermissionGroups(new String[0]);
}""")
Mk(gcmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyycooking.admin")) { pr.sendMessage(@MSG@.raw("[Cooking] no permission (skyycooking.admin)")); return; }
    String d = String.valueOf(ctx.get(this.dishArg)).trim();
    String dish = null;
    for (int i = 0; i < @PKG@.CookCfg.DISHES.length; i++) {
      String x = @PKG@.CookCfg.DISHES[i];
      if (x.equalsIgnoreCase(d) || x.equalsIgnoreCase("Food_" + d)) dish = x;
    }
    if (dish == null) {
      String all = "";
      for (int i = 0; i < @PKG@.CookCfg.DISHES.length; i++) all = all + (i > 0 ? ", " : "") + @PKG@.CookCfg.DISHES[i].substring(5);
      pr.sendMessage(@MSG@.raw("[Cooking] unknown dish '" + d + "'. Dishes: " + all));
      return;
    }
    int g = -1;
    try { g = Integer.parseInt(String.valueOf(ctx.get(this.gradeArg)).trim()); } catch (Throwable t) { g = -1; }
    if (g < 0 || g > @PKG@.CookCfg.GEN_MAX) { pr.sendMessage(@MSG@.raw("[Cooking] grade must be 0-" + @PKG@.CookCfg.GEN_MAX)); return; }
    String id = g == 0 ? dish : @PKG@.Cook.gradedId(dish, g);
    if (!@PKG@.Cook.exists(id)) { pr.sendMessage(@MSG@.raw("[Cooking] item " + id + " is not loaded (asset pack problem - see the server log)")); return; }
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) return;
    @SIC@.addOrDropItemStack(store, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new @IS@(id, 5));
    pr.sendMessage(@MSG@.raw("[Cooking] gave 5 x " + id));
  } catch (Throwable t) { @PKG@.CookCfg.warn("/cookadmin give failed: " + t); pr.sendMessage(@MSG@.raw("[Cooking] give failed: " + t)); }
}""")
Ct(rcmd, """
public CookReloadCmd() {
  super("reload", "(admin) Re-read Skyy_SkyyCooking/cooking.properties");
  requirePermission("skyycooking.admin");
  setPermissionGroups(new String[0]);
}""")
Mk(rcmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  if (!pr.hasPermission("skyycooking.admin")) { pr.sendMessage(@MSG@.raw("[Cooking] no permission (skyycooking.admin)")); return; }
  @PKG@.Cook.EXISTS.clear();
  @PKG@.CookCfg.ONCE.clear();
  String sum = @PKG@.CookCfg.load();
  String k = "";
  if (@PKG@.CfgPub.STARTED) {
    try {
      Object o = new @PKG@.CfgFn().apply(new Object[] { "reload", pr.getUuid(), pr.getUsername(), "command" });
      if (o instanceof Object[] && ((Object[]) o).length > 2 && ((Object[]) o)[2] != null) k = String.valueOf(((Object[]) o)[2]) + " ";
    } catch (Throwable t) { k = "(config kit: " + t + ") "; }
  }
  pr.sendMessage(@MSG@.raw("[Cooking] cooking.properties reloaded: " + k + sum));
}""")
# /cookadmin campfire <dish> <count> (0.1.1): runs cook:fn:campfire exactly as /craft does, gives count x the returned id (no materials)
F(fcmd, "public %s dishArg;" % RA)
F(fcmd, "public %s countArg;" % RA)
Ct(fcmd, """
public CookCampCmd() {
  super("campfire", "(admin) Test the Campfire accessory cook like /craft: /cookadmin campfire wildmeat_cooked 5 (gives the dishes and the XP, uses no materials; 0 = preview)");
  this.dishArg = withRequiredArg("dish", "Food_Wildmeat_Cooked, Food_Fish_Grilled or Food_Vegetable_Cooked (Food_ may be left out)", @ATY@.STRING);
  this.countArg = withRequiredArg("count", "0-64 (0 = preview: shows the Grade, gives nothing, no XP)", @ATY@.STRING);
  requirePermission("skyycooking.admin");
  setPermissionGroups(new String[0]);
}""")
Mk(fcmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!pr.hasPermission("skyycooking.admin")) { pr.sendMessage(@MSG@.raw("[Cooking] no permission (skyycooking.admin)")); return; }
    String d = String.valueOf(ctx.get(this.dishArg)).trim();
    String dish = null;
    for (int i = 0; i < @PKG@.CookCfg.CAMP.length; i++) {
      String x = @PKG@.CookCfg.CAMP[i];
      if (x.equalsIgnoreCase(d) || x.equalsIgnoreCase("Food_" + d)) dish = x;
    }
    if (dish == null) { pr.sendMessage(@MSG@.raw("[Cooking] '" + d + "' is not a campfire dish. Campfire dishes: " + @PKG@.CookCfg.campList())); return; }
    int n = -1;
    try { n = Integer.parseInt(String.valueOf(ctx.get(this.countArg)).trim()); } catch (Throwable t) { n = -1; }
    if (n < 0 || n > 64) { pr.sendMessage(@MSG@.raw("[Cooking] count must be 0-64 (0 = preview)")); return; }
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Cooking] campfire test: no Player component on your entity - nothing done")); return; }
    String rid = @PKG@.Cook.campRecipeFor(dish);
    if (rid == null) { pr.sendMessage(@MSG@.raw("[Cooking] no loaded Campfire-bench recipe makes " + dish + " - nothing done")); return; }
    Boolean cf = Boolean.valueOf(p.getGameMode() == @GM@.Creative);
    int cm = @PKG@.Cook.creativeOf(pr.getUuid());
    Object[] r = @PKG@.Cook.campfire(pr.getUuid(), rid, n, (String) null, cf);
    if (r == null) { pr.sendMessage(@MSG@.raw("[Cooking] the Campfire recipe " + rid + " (" + dish + ") was not accepted by cook:fn:campfire")); return; }
    String id = (String) r[0];
    if (n > 0) @SIC@.addOrDropItemStack(store, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new @IS@(id, n));
    String why = r[4] == null ? "" : " - plain because " + String.valueOf(r[4]);
    String act = n > 0 ? "gave " + n + " x " : "would give ";
    String mode = cm == 1 ? "creative" : (cm == 0 ? "not creative" : "unreadable");
    pr.sendMessage(@MSG@.raw("[Cooking] Campfire accessory test (recipe " + rid + "): bench Grade " + String.valueOf(r[1]) + " -> campfire Grade " + String.valueOf(r[2]) + " (buffFactor " + @PKG@.CookCfg.CAMP_BUFF + ", xpFactor " + @PKG@.CookCfg.CAMP_XP + ") - " + act + id + " - Cooking XP sent " + String.valueOf(r[3]) + why + " - game mode as the bridge reads it without a flag: " + mode));
  } catch (Throwable t) { @PKG@.CookCfg.warn("/cookadmin campfire failed: " + t); pr.sendMessage(@MSG@.raw("[Cooking] campfire test failed: " + t)); }
}""")
Ct(acmd, """
public CookAdminCmd() {
  super("cookadmin", "(admin) SkyyCooking: /cookadmin give <dish> <grade>, /cookadmin campfire <dish> <count>, /cookadmin reload");
  requirePermission("skyycooking.admin");
  setPermissionGroups(new String[0]);
  addSubCommand(new @PKG@.CookGiveCmd());
  addSubCommand(new @PKG@.CookReloadCmd());
  addSubCommand(new @PKG@.CookCampCmd());
}""")
Mk(acmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  pr.sendMessage(@MSG@.raw("[Cooking] /cookadmin give <dish> <grade>  (e.g. /cookadmin give pie_meat 5)  |  /cookadmin campfire <dish> <count>  (e.g. /cookadmin campfire wildmeat_cooked 0)  |  /cookadmin reload"));
}""")
Ct(ccmd, """
public CookingCmd() {
  super("cooking", "Your Cooking level, the Grade of the food you cook and your skill tree chances");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
# 0.1.4: the reply is Cook.cookingLines (the same lines and order as 0.1.3's code here, now naming strength and duration); the first line of
# a full reply keeps its colour, a one-line answer (graded cooking off / no SkyySkills) stays plain as before
Mk(ccmd, """
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    java.util.List l = @PKG@.Cook.cookingLines(pr.getUuid());
    for (int i = 0; i < l.size(); i++) {
      String s = (String) l.get(i);
      if (i == 0 && l.size() > 1) pr.sendMessage(@MSG@.raw(s).color("#ffb070"));
      else pr.sendMessage(@MSG@.raw(s));
    }
  } catch (Throwable t) { @PKG@.CookCfg.warn("/cooking failed: " + t); pr.sendMessage(@MSG@.raw("[Cooking] something went wrong - see the server log")); }
}""")

# ================= plugin =================
Ct(pl, "public SkyyCookingPlugin(@JPI@ init) { super(init); }")
Mk(pl, """
public void setup() {
  @PKG@.CookCfg.LOG = getLogger();
  @PKG@.CookCfg.FILE = getDataDirectory().resolveSibling("Skyy_SkyyCooking").resolve("cooking.properties");
  @PKG@.CookMig.migrate();
  @PKG@.CookXpMig.migrate();
  @PKG@.CookTblMig.migrate();
  @PKG@.CookIngMig.migrate();
  String s = @PKG@.CookCfg.load();
  getEntityStoreRegistry().registerSystem(new @PKG@.CookSys());
  getCommandRegistry().registerCommand(new @PKG@.CookingCmd());
  getCommandRegistry().registerCommand(new @PKG@.CookAdminCmd());
  java.util.Map b = @PKG@.Cook.bridge();
  b.put("cook:fn:grade", new @PKG@.CookGradeFn());
  b.put("cook:fn:out", new @PKG@.CookOutFn());
  b.put("cook:prefix", "Skyy_Cook_Food_");
  b.put("skill:stats:Cooking", new @PKG@.CookStatsFn());
  b.put("cook:fn:campfire", new @PKG@.CookCampFn());
  b.put("cook:campfire:ids", @PKG@.CookCfg.campList());
  b.put("cook:fn:campfactors", new @PKG@.CookCampInfoFn());
  @PKG@.Cook.regSetting("cooking.grade", "Food Grade changes", "cooking", true, "Your food now comes out Grade 3 - and the campfire accessory hint");
  @PKG@.Cook.regSetting("cooking.procs", "Cooking bonus procs", "cooking", true, "Gourmet!, Signature Dish!, Batch Cook!, Prep Cook! and Frugal!");
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCooking] @VERSION@ ready - Cooking Bench crafts give graded dishes (Grade = Cooking level / 10; heal and buffs x(1 + 0.32 x Grade) - x2.6 at 50, x4.2 at 100 - lasting x2^(Grade/5) - x2 at 50, x4 at 100; Grades 11-12 from the SkyyTrees Cooking tree) and Cooking XP through SkyySkills; Campfire accessory bridge cook:fn:campfire (" + @PKG@.CookCfg.campList() + "); /cooking; player switches cooking.grade + cooking.procs (/settings); in-game config: SkyWynn Menu Server Setup (/modconfig cooking); config: " + s + "; SkyySkills " + (b.get("skill:fn:level") != null ? "found" : "not loaded yet (plain food and no XP without it)"));
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""")
Mk(pl, """
protected void shutdown() {
  try { java.util.Map b = @PKG@.Cook.bridge(); b.remove("cook:fn:grade"); b.remove("cook:fn:out"); b.remove("cook:prefix"); b.remove("skill:stats:Cooking"); b.remove("cook:fn:campfire"); b.remove("cook:campfire:ids"); b.remove("cook:fn:campfactors"); } catch (Throwable t) { }
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  super.shutdown();
}""")

for c in (cfg, hk, mig, xmig, tmig, imig, ck, xpt, csy, gfn, ofn, sfn, cfn, ifn, gcmd, rcmd, fcmd, acmd, ccmd, pl):
    c.writeFile(OUT)
CFG_KIT.write(OUT)
print("classes written (+ %d config kit classes)" % len(CFG_KIT.classes))

# 0.1.1 self-check: the COMPILED Cook.campGrade / CookCfg.campList (loaded from build_classes with the server jar) match the Python mirror
import jpype
_URL, _File = jpype.JClass("java.net.URL"), jpype.JClass("java.io.File")
_ld = jpype.JClass("java.net.URLClassLoader")(jpype.JArray(_URL)([_File(OUT).toURI().toURL(), _File(J["server_jar"]).toURI().toURL()]))
_JCook = jpype.JClass(PKG + ".Cook", loader=_ld)
_JCfg = jpype.JClass(PKG + ".CookCfg", loader=_ld)
for _f in (CAMP_BUFF_DEF, 0.5, 0.25, 0.0, 1.0, 0.9):
    _jt = [int(_JCook.campGrade(g, _f)) for g in range(GEN_MAX + 1)]
    _pt = [camp_grade(g, _f) for g in range(GEN_MAX + 1)]
    if _jt != _pt:
        raise SystemExit("self-check 0.1.1: compiled Cook.campGrade(g, %s) = %s but the Python mirror says %s" % (_f, _jt, _pt))
if str(_JCfg.campList()) != ",".join(CAMP_DISHES) or int(_JCfg.campIndex("Food_Pie_Meat")) != -1 or int(_JCfg.campIndex(CAMP_DISHES[0])) != 0:
    raise SystemExit("self-check 0.1.1: compiled CookCfg.campList / campIndex disagree with CAMP_DISHES")
# a bare dish id is never proof of a Campfire craft: the strict resolver and the whole campfire() call refuse it before any asset lookup
for _d in CAMP_DISHES:
    if _JCook.campRecipeDish(_d) is not None or _JCook.campRecipeDish(" " + _d + " ") is not None:
        raise SystemExit("self-check 0.1.1: compiled Cook.campRecipeDish accepts the bare dish id " + _d)
    if _JCook.campfire(jpype.JClass("java.util.UUID").randomUUID(), _d, 1, None, jpype.JClass("java.lang.Boolean").FALSE) is not None:
        raise SystemExit("self-check 0.1.1: compiled Cook.campfire grades the bare dish id " + _d)
if _JCook.campRecipeDish(None) is not None or _JCook.campRecipeDish("  ") is not None:
    raise SystemExit("self-check 0.1.1: compiled Cook.campRecipeDish accepts null / blank")
# the ONE bench-Grade helper: compiled Cook.benchGrade = min(level/10, 10) + (Master Chef >= 1), clamped to 0..min(maxGrade, GEN_MAX)
_mg = min(int(_JCfg.MAX_GRADE), GEN_MAX)
_IA = jpype.JArray(jpype.JInt)
for _lv in list(range(0, 131)) + [-5, 999, 1000]:
    for _mc in (0, 1, 3):
        _t = _IA(len(NODES))
        _t[9] = _mc
        _want = max(0, min((min(_lv // 10, 10) if _lv > 0 else 0) + (1 if _mc >= 1 else 0), _mg))
        if int(_JCook.benchGrade(_lv, _t)) != _want:
            raise SystemExit("self-check 0.1.1: compiled Cook.benchGrade(%d, Master Chef %d) = %d, expected %d" % (_lv, _mc, int(_JCook.benchGrade(_lv, _t)), _want))
if int(_JCook.benchGrade(50, None)) != 5:
    raise SystemExit("self-check 0.1.1: compiled Cook.benchGrade(50, null) must be 5")
_JInfo = jpype.JClass(PKG + ".CookCampInfoFn", loader=_ld)()
_fx = _JInfo.apply(None)
if abs(float(_fx[0]) - CAMP_BUFF_DEF) > 1e-12 or abs(float(_fx[1]) - CAMP_XP_DEF) > 1e-12 or not bool(_fx[2]):
    raise SystemExit("self-check 0.1.1: compiled cook:fn:campfactors returns %s, expected [%s, %s, true]" % (list(_fx), CAMP_BUFF_DEF, CAMP_XP_DEF))
# cross-check fix: an accessory batch pays the XP that still fits the per-minute window (never all-or-nothing), then 0 until it resets
_cap = int(_JCfg.MAX_PER_MIN)
_uu = jpype.JClass("java.util.UUID").randomUUID()
_parts = (int(_JCook.allowXpPart(_uu, _cap - 1000)), int(_JCook.allowXpPart(_uu, 5000)), int(_JCook.allowXpPart(_uu, 5000)), int(_JCook.allowXpPart(_uu, 0)))
if _parts != (_cap - 1000, 1000, 0, 0):
    raise SystemExit("self-check 0.1.1: compiled Cook.allowXpPart must pay what fits the %d/min window: got %s" % (_cap, _parts))
_uu = jpype.JClass("java.util.UUID").randomUUID()
if int(_JCook.allowXpPart(_uu, _cap + 800)) != _cap:
    raise SystemExit("self-check 0.1.1: compiled Cook.allowXpPart drops a whole batch that is bigger than the window")
print("compiled campfire mapping matches the Python mirror (buffFactor 0.75 / 0.5 / 0.25 / 0 / 1 / 0.9); bare dish ids refused; benchGrade "
      "matches min(level/10, 10) + Master Chef (max Grade %d); cook:fn:campfactors = %s; cook:campfire:ids = %s; a batch over the %d XP/min "
      "window pays the part that fits" % (_mg, [str(x) for x in _fx], str(_JCfg.campList()), _cap))

# 0.1.2 self-check: the compiled check hooks, the player Settings helper (with fake SkyyMenu functions on the build JVM's bridge) and
# the kit schema that went into the jar
_JHk = jpype.JClass(PKG + ".CookHooks", loader=_ld)
if _JHk.checkGraded("graded", ",".join(DISHES)) is not None or _JHk.checkGraded("graded", "") is not None:
    raise SystemExit("self-check 0.1.2: CookHooks.checkGraded refuses the default dish list")
if _JHk.checkGraded("graded", "Food_Bread,Food_Cheese") is None:
    raise SystemExit("self-check 0.1.2: CookHooks.checkGraded accepts Food_Cheese (no Grade assets)")
if _JHk.checkTree("tree[CGourmet.per]", "0.5") is not None or _JHk.checkTree("tree[CMaster.per]", None) is not None:
    raise SystemExit("self-check 0.1.2: CookHooks.checkTree refuses a real node")
if _JHk.checkTree("tree[CFoo.per]", "0.5") is None or _JHk.checkTree("tree[CGourmet]", "0.5") is None:
    raise SystemExit("self-check 0.1.2: CookHooks.checkTree accepts an unknown node entry")
if _JHk.checkXp("xp[default]", "900") is not None or _JHk.checkXp("xp[Food_Pie_Meat]", None) is not None:
    raise SystemExit("self-check 0.1.2: CookHooks.checkXp refuses the default entry or a removal")
_JRows = jpype.JClass(PKG + ".CfgRows", loader=_ld)
if [str(x) for x in _JRows.KEYS] != [t[0] for t in COOK_CFG_ROWS] or str(_JRows.NODE) != "skyycooking.admin" or str(_JRows.MOD) != "SkyyCooking" \
        or str(_JRows.RELOAD) != PKG + ".CookCfg.load" or str(_JRows.FILES[0]) != COOK_FILE:
    raise SystemExit("self-check 0.1.2: the compiled kit schema is not the one this script declares")
_Bool = jpype.JClass("java.lang.Boolean")
_calls = []
@jpype.JImplements("java.util.function.Function")
class _FakeFn(object):
    def __init__(self, ans):
        self.ans = ans
    @jpype.JOverride
    def apply(self, a):
        _calls.append([str(x) for x in a])
        return self.ans
_br = _JCook.bridge()
_u = jpype.JClass("java.util.UUID").randomUUID()
for _k in ("settings:fn:get", "settings:fn:register", "settings:def:cooking.grade"):
    _br.remove(_k)
if not _JCook.notifyOn(_u, "cooking.grade") or not _JCook.notifyOn(None, "cooking.grade") or not _JCook.notifyOn(_u, None):
    raise SystemExit("self-check 0.1.2: Cook.notifyOn must read ON without SkyyMenu")
for _ans, _want in ((_Bool.FALSE, False), (_Bool.TRUE, True), (None, True)):
    _br.put("settings:fn:get", _FakeFn(_ans))
    if bool(_JCook.notifyOn(_u, "cooking.procs")) != _want:
        raise SystemExit("self-check 0.1.2: Cook.notifyOn with settings:fn:get answering %s must be %s" % (_ans, _want))
if _calls[-1] != [str(_u), "cooking.procs"]:
    raise SystemExit("self-check 0.1.2: Cook.notifyOn passed %s to settings:fn:get" % _calls[-1])
_br.put("settings:fn:register", _FakeFn(_Bool.TRUE))
_JCook.regSetting("cooking.grade", "Food Grade changes", "cooking", True, "Your food now comes out Grade 3 - and the campfire accessory hint")
_def = _br.get("settings:def:cooking.grade")
_exp = ["SkyyCooking", "cooking.grade", "Food Grade changes", "cooking", "true", "Your food now comes out Grade 3 - and the campfire accessory hint"]
_norm = lambda l: [str(x).lower() if i == 4 else str(x) for i, x in enumerate(l)]   # element 4 = java.lang.Boolean (jpype: True)
if _def is None or _norm(_def) != _exp or _norm(_calls[-1]) != _exp:
    raise SystemExit("self-check 0.1.2: Cook.regSetting wrote %s / registered %s, expected %s" % (None if _def is None else _norm(_def), _calls[-1], _exp))
for _k in ("settings:fn:get", "settings:fn:register", "settings:def:cooking.grade"):
    _br.remove(_k)
print("0.1.2 checks: CookHooks accept the defaults and refuse a non-graded dish / unknown node; kit schema %d rows on %s (node %s, RELOAD "
      "CookCfg.load); Cook.notifyOn ON without SkyyMenu and follows settings:fn:get; Cook.regSetting writes settings:def + registers"
      % (len(COOK_CFG_ROWS), COOK_FILE, str(_JRows.NODE)))

# 0.1.3 self-check: the default (row, compiled fields, campfactors) and the COMPILED one-time update (CookMig.update, the pure text step) on
# the shapes it meets in the field. The harness (SkyyCooking/test_skyycooking_0.1.3.py) runs migrate() itself on scratch copies.
_JMig = jpype.JClass(PKG + ".CookMig", loader=_ld)
if abs(float(_JCfg.DEF_CAMP_XP) - 0.25) > 1e-12 or abs(float(_JCfg.CAMP_XP) - 0.25) > 1e-12 or str(_JMig.NEW) != "0.25" or str(_JMig.OLD) != "0.5" \
        or str(_JMig.WHO) != "SkyyCooking " + VERSION or str(_JMig.MARK) != CAMP_MARK:
    raise SystemExit("self-check 0.1.3: compiled campfire XP default / CookMig constants are not 0.25 / 0.5 / %s" % VERSION)
_xi = [t[0] for t in COOK_CFG_ROWS].index("campfire.xpFactor")
if str(_JRows.DEFS[_xi]) != "0.25" or "0.25 = a quarter" not in str(_JRows.HELPS[_xi]) or len(str(_JRows.HELPS[_xi])) > 100:
    raise SystemExit("self-check 0.1.3: the Campfire XP share row default / help is not 0.25 / 'a quarter'")
_XPN, _XPO = "campfire.xpFactor=0.25\n", "campfire.xpFactor=0.5\n"
if DEFAULTS_TEXT.count(_XPN) != 1 or DEFAULTS_TEXT.count(CAMP_MARK + "\n# campfire.xpFactor = share") != 1 or CAMP_BLOCK_TEXT.count(CAMP_MARK + "\n") != 1:
    raise SystemExit("self-check 0.1.3: the default text / 0.1 append block must carry campfire.xpFactor=0.25 with the marker right above its help line")
def _mig(t):
    r = _JMig.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]], None if r[4] is None else str(r[4]))
_f012 = DEFAULTS_TEXT.replace(CAMP_MARK + "\n", "").replace(_XPN, _XPO)          # a fresh 0.1.2 file (header line aside)
if _mig(_f012) != (DEFAULTS_TEXT, "campfire.xpFactor 0.5 -> 0.25", None, ["campfire.xpFactor", "0.5", "0.25"], "0.5"):
    raise SystemExit("self-check 0.1.3: CookMig.update of a fresh 0.1.2 file is not exactly the 0.1.3 default text: %r" % (_mig(_f012),))
if _JMig.update(DEFAULTS_TEXT) is not None or _JMig.update("enabled=true\nxp.default=1000\n") is not None:
    raise SystemExit("self-check 0.1.3: CookMig.update must leave a marked file and a file without campfire lines alone")
_b011 = CAMP_BLOCK_TEXT.replace(CAMP_MARK + "\n", "").replace(_XPN, _XPO)        # the block 0.1.1 appended to a 0.1 file (the live shape)
for _nl in ("\n", "\r\n"):
    _head = "# SkyyCooking 0.1 - cooking.properties\nenabled=true\nxp.default=1000\ntree.CMaster.per=0.05\n"
    _in, _want = (_head + _b011).replace("\n", _nl), (_head + CAMP_BLOCK_TEXT).replace("\n", _nl)
    if _mig(_in) != (_want, "campfire.xpFactor 0.5 -> 0.25", None, ["campfire.xpFactor", "0.5", "0.25"], "0.5"):
        raise SystemExit("self-check 0.1.3: CookMig.update of the 0.1 + 0.1.1-block shape (%r) is wrong: %r" % (_nl, _mig(_in)))
_cus = _mig(_f012.replace(_XPO, "campfire.xpFactor=0.3\n"))
if _cus != (DEFAULTS_TEXT.replace(_XPN, "campfire.xpFactor=0.3\n"), "", "campfire.xpFactor=0.3 kept (custom) - the 0.1.3 default is 0.25", [], "0.3"):
    raise SystemExit("self-check 0.1.3: a hand-edited campfire.xpFactor must be kept (marker only, noted): %r" % (_cus,))
print("0.1.3 checks: Campfire XP share default 0.25 (row, loader fallback, field, cook:fn:campfactors, default file + 0.1 block with the "
      "marker); campfire XP per dish %s; CookMig.update: fresh 0.1.2 file -> the 0.1.3 default text, the live 0.1 + 0.1.1-block shape "
      "(LF + CRLF) -> 0.25 + marker, custom 0.3 kept, marked file / no campfire line untouched"
      % ", ".join("%s %d -> %d" % (d, XP[d], int(round(XP[d] * CAMP_XP_DEF))) for d in CAMP_DISHES))

# 0.1.4 self-check: the split factors in the compiled tables, the Cooking XP default (row, fields, default text), the compiled text helpers,
# the tooltip wording and the COMPILED one-time xpMultiplier update (CookXpMig.update, the pure text step) on the shapes it meets in the
# field. The harness (SkyyCooking/test_skyycooking_0.1.4.py) runs migrate() itself on scratch copies of the live file.
_JXm = jpype.JClass(PKG + ".CookXpMig", loader=_ld)
_G13 = range(GEN_MAX + 1)
if [float(x) for x in _JCfg.SF] != [SF(g) for g in _G13] or [float(x) for x in _JCfg.MUL] != [SF(g) for g in _G13] \
        or [float(x) for x in _JCfg.DF] != [round(M(g), 4) for g in _G13]:
    raise SystemExit("self-check 0.1.4: compiled CookCfg.SF / MUL must be 1 + 0.32 x Grade and DF 2^(Grade/5): %s / %s / %s"
                     % (list(_JCfg.SF), list(_JCfg.MUL), list(_JCfg.DF)))
if abs(float(_JCfg.DEF_XP_MULT) - XP_MULT_DEF) > 1e-12 or abs(float(_JCfg.XP_MULT) - XP_MULT_DEF) > 1e-12 or str(_JXm.NEW) != "0.5" \
        or (str(_JXm.OLD), str(_JXm.OLD2)) != XP_MULT_OLD or str(_JXm.MARK) != XP_MARK or str(_JXm.MARK_ID) != XP_MARK_ID:
    raise SystemExit("self-check 0.1.4: compiled xpMultiplier default / CookXpMig constants are not 0.5 / 1.0 + 1 / the marker")
_xmi = [t[0] for t in COOK_CFG_ROWS].index("xpMultiplier")
if str(_JRows.DEFS[_xmi]) != "0.5" or str(_JRows.HELPS[_xmi]) != XP_HELP_ROW or str(_JRows.LABELS[_xmi]) != "Cooking XP multiplier":
    raise SystemExit("self-check 0.1.4: the Cooking XP multiplier row default / help is not 0.5 / %r" % XP_HELP_ROW)
_XMN, _XMO = "xpMultiplier=0.5\n", "xpMultiplier=1.0\n"
if DEFAULTS_TEXT.count(_XMN) != 1 or DEFAULTS_TEXT.count(XP_MARK + "\n" + XP_HELP_LINE + "\n" + _XMN) != 1 or "xpMultiplier=1" in DEFAULTS_TEXT:
    raise SystemExit("self-check 0.1.4: the default text must carry xpMultiplier=0.5 with the marker right above its help line")
def _xm(t):
    r = _JXm.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]], None if r[4] is None else str(r[4]))
_f013 = DEFAULTS_TEXT.replace(XP_MARK + "\n", "").replace(_XMN, _XMO)            # a fresh 0.1.3 file (header line aside)
for _old in XP_MULT_OLD:
    _in = _f013.replace(_XMO, "xpMultiplier=%s\n" % _old)
    if _xm(_in) != (DEFAULTS_TEXT, "xpMultiplier %s -> 0.5" % _old, None, ["xpMultiplier", _old, "0.5"], _old):
        raise SystemExit("self-check 0.1.4: CookXpMig.update of a fresh 0.1.3 file with xpMultiplier=%s is not the 0.1.4 default text: %r" % (_old, _xm(_in)))
for _v in ("0.5", "0.7", "1.00", "2", "0"):
    _in = _f013.replace(_XMO, "xpMultiplier=%s\n" % _v)
    _note = None if _v == "0.5" else "xpMultiplier=%s kept (custom) - the 0.1.4 default is 0.5" % _v
    if _xm(_in) != (DEFAULTS_TEXT.replace(_XMN, "xpMultiplier=%s\n" % _v), "", _note, [], _v):
        raise SystemExit("self-check 0.1.4: a hand-set xpMultiplier=%s must be kept (marker only): %r" % (_v, _xm(_in)))
if _JXm.update(DEFAULTS_TEXT) is not None:
    raise SystemExit("self-check 0.1.4: CookXpMig.update must leave a marked file alone")
for _nl in ("\n", "\r\n"):
    _h = "# SkyyCooking 0.1 - cooking.properties\nenabled=true\n" + XP_HELP_LINE + "\nxpMultiplier=1.0\nmaxXpPerMinute=1500000\n"
    _in = _h.replace("\n", _nl)
    _want = _h.replace(XP_HELP_LINE, XP_MARK + "\n" + XP_HELP_LINE).replace("xpMultiplier=1.0", "xpMultiplier=0.5").replace("\n", _nl)
    if _xm(_in) != (_want, "xpMultiplier 1.0 -> 0.5", None, ["xpMultiplier", "1.0", "0.5"], "1.0"):
        raise SystemExit("self-check 0.1.4: CookXpMig.update of the live 0.1 shape (%r) is wrong: %r" % (_nl, _xm(_in)))
if _xm("enabled=true\nmaxGrade=12\n") != (XP_MARK + "\nenabled=true\nmaxGrade=12\n", "", None, [], None) or _xm("") != (XP_MARK + "\n", "", None, [], None):
    raise SystemExit("self-check 0.1.4: a file without an xpMultiplier line must get only the marker (above its first entry / on top)")
_sdl = [str(_JCook.sd(g)) for g in _G13]
if _sdl[0] != "heal and buffs x1.00 stronger, buffs last x1.00 longer" or _sdl[2] != "heal and buffs x1.64 stronger, buffs last x1.32 longer" \
        or _sdl[10] != "heal and buffs x4.20 stronger, buffs last x4.00 longer" or str(_JCook.sdShort(12)) != "x4.84 stronger and x5.28 longer":
    raise SystemExit("self-check 0.1.4: compiled Cook.sd / sdShort: %s / %s" % (_sdl, str(_JCook.sdShort(12))))
_ct = str(_JCook.campText(5, 3))
if _ct != ("Campfire accessory = quick emergency cooking: your campfire dishes come out Grade 3 (75% of your Grade 5 strength bonus - heal and "
           "buffs x1.96 stronger, buffs last x1.52 longer) and pay 25% of the Cooking XP. A Cooking Bench gives the full Grade and XP."):
    raise SystemExit("self-check 0.1.4: compiled Cook.campText(5, 3) = %r" % _ct)
_LANG = files["Server/Languages/en-US/server.lang"].split("\n")
_HEAD2 = ("server.items.%s.description=Grade 2 food - Cooking 20, or sooner with Cooking tree bonuses. Heal and buffs %s stronger, buffs last %s longer."
          % (dish_id("Food_Pie_Meat", 2), W % "x1.64", W % "x1.32"))
if not any(l.startswith(_HEAD2) for l in _LANG) or any("cooked at Cooking" in l for l in _LANG) \
        or sum(1 for l in _LANG if "or sooner with Cooking tree bonuses." in l) != 2 * len(DISHES) * 10:
    raise SystemExit("self-check 0.1.4: the dish tooltip head is not the new wording (%s...)" % _HEAD2[:120])
print("0.1.4 checks: SF / MUL = 1 + 0.32 x Grade, DF = 2^(Grade/5) (compiled); xpMultiplier default 0.5 (row + help, loader fallback, field, "
      "default text with the marker); CookXpMig.update: a fresh 0.1.3 file with 1.0 or 1 -> the 0.1.4 default text, the live 0.1 shape (LF + "
      "CRLF) -> 0.5 + marker, 0.5 / 0.7 / 1.00 / 2 / 0 kept, marked file untouched, no line -> marker only; Cook.sd / sdShort / campText; "
      "tooltip 'Grade 2 food - Cooking 20, or sooner with Cooking tree bonuses' (%d lines)" % (2 * len(DISHES) * 10))

DEFAULTS_015 = DEFAULTS_TEXT.replace(XP_ING_MARK + "\n" + XP_TBL_MARK + "\n" + "\n".join(XP_HELP_016) + "\n", XP_TBL_MARK + "\n" + "\n".join(XP_HELP_015) + "\n")
for _i in INGS:
    DEFAULTS_015 = DEFAULTS_015.replace("\nxp.%s=%d\n" % (_i, XP[_i]), "\nxp.%s=%d\n" % (_i, XP_015[_i]))
assert DEFAULTS_015.count(XP_TBL_MARK + "\n" + "\n".join(XP_HELP_015) + "\nxp.default=") == 1 and XP_ING_MARK not in DEFAULTS_015 \
    and all(DEFAULTS_015.count("\nxp.%s=%d\n" % (k, v)) == 1 for k, v in XP_015.items()), "0.1.6: DEFAULTS_015 is not the 0.1.5 shape"
# 0.1.5 self-check: the compiled XP table, the default text (marker + new help above the xp block), and the COMPILED one-time update
# (CookTblMig.update, the pure text step) on the shapes it meets in the field. The harness (SkyyCooking/test_skyycooking_0.1.5.py) runs
# migrate() itself on scratch copies of the live file.
_JTm = jpype.JClass(PKG + ".CookTblMig", loader=_ld)
if dict(zip([str(x) for x in _JCfg.XP_IDS], [int(x) for x in _JCfg.XP_VALS])) != XP:
    raise SystemExit("self-check 0.1.5: compiled CookCfg.XP_IDS / XP_VALS are not the difficulty table")
if [str(x) for x in _JTm.KEYS] != ["xp." + d for d in _TBL] or [str(x) for x in _JTm.NEWS] != [str(XP[d]) for d in _TBL] \
        or [str(x) for x in _JTm.OLDS] != [str(XP_OLD[d]) for d in _TBL] or str(_JTm.MARK) != XP_TBL_MARK or len(_TBL) != len(DISHES):
    raise SystemExit("self-check 0.1.5: compiled CookTblMig tables are not the build's (%d keys)" % len(_TBL))
_blk_new = XP_TBL_MARK + "\n" + "\n".join(XP_HELP_NEW) + "\nxp.default=%d\n" % XP_DEFAULT
if DEFAULTS_015.count(_blk_new) != 1 or any(h in DEFAULTS_015 for h in XP_HELP_OLD):
    raise SystemExit("self-check 0.1.5: the default text must carry the marker + the new help lines right above xp.default")
def _tm(t):
    r = _JTm.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]])
def _f014(tab):     # a fresh 0.1.4 file (header line aside) with these dish values
    t = DEFAULTS_015.replace(_blk_new, "\n".join(XP_HELP_OLD) + "\nxp.default=%d\n" % XP_DEFAULT)
    for d in DISHES:
        t = t.replace("\nxp.%s=%d\n" % (d, XP[d]), "\nxp.%s=%d\n" % (d, tab[d]))
    return t
_chg = ", ".join("xp.%s %d -> %d" % (d, XP_OLD[d], XP[d]) for d in _TBL)
_rows = [x for d in _TBL for x in ("xp[%s]" % d, str(XP_OLD[d]), str(XP[d]))]
if _tm(_f014(XP_OLD)) != (DEFAULTS_015, _chg, None, _rows):
    raise SystemExit("self-check 0.1.5: CookTblMig.update of a fresh 0.1.4 file is not exactly the 0.1.5 default text: %r" % (_tm(_f014(XP_OLD)),)[:600])
_sg = dict(XP_OLD, **STOPGAP_014)
_r = _tm(_f014(_sg))
if _r is None or _r[0] != DEFAULTS_015 or len(_r[3]) != 3 * len(_TBL) or _r[2] is not None \
        or any("xp[%s]" % d not in _r[3] or str(STOPGAP_014[d]) != _r[3][_r[3].index("xp[%s]" % d) + 1] for d in STOPGAP_014):
    raise SystemExit("self-check 0.1.5: the 2026-10-04 stopgap kebab values must be replaced like old defaults: %r" % (_r,))
_cu = dict(XP_OLD, Food_Pie_Meat=30000, Food_Kebab_Vegetable=1700)
_r = _tm(_f014(_cu))
if _r is None or "\nxp.Food_Pie_Meat=30000\n" not in _r[0] or "\nxp.Food_Kebab_Vegetable=1700\n" not in _r[0] \
        or _r[2] != "xp.Food_Kebab_Vegetable=1700 kept (custom) - the 0.1.5 default is %d\nxp.Food_Pie_Meat=30000 kept (custom) - the 0.1.5 default is %d" % (XP["Food_Kebab_Vegetable"], XP["Food_Pie_Meat"]) \
        or len(_r[3]) != 3 * (len(_TBL) - 2):
    raise SystemExit("self-check 0.1.5: hand-set values must be kept and noted: %r" % (_r,))
if _JTm.update(DEFAULTS_015) is not None:
    raise SystemExit("self-check 0.1.5: CookTblMig.update must leave a marked file alone")
for _nl in ("\n", "\r\n"):
    _h = "# SkyyCooking 0.1 - cooking.properties\nenabled=true\nxpMultiplier=0.5\n" + "\n".join(XP_HELP_OLD) + "\nxp.default=1000\nxp.Food_Bread=12900\nxp.Food_Kebab_Meat=2600\nxp.Ingredient_Flour=1425\n"
    _w = "# SkyyCooking 0.1 - cooking.properties\nenabled=true\nxpMultiplier=0.5\n" + XP_TBL_MARK + "\n" + "\n".join(XP_HELP_NEW) + "\nxp.default=1000\nxp.Food_Bread=%d\nxp.Food_Kebab_Meat=%d\nxp.Ingredient_Flour=1425\n" % (XP["Food_Bread"], XP["Food_Kebab_Meat"])
    if _tm(_h.replace("\n", _nl)) != (_w.replace("\n", _nl), "xp.Food_Bread 12900 -> %d, xp.Food_Kebab_Meat 2600 -> %d" % (XP["Food_Bread"], XP["Food_Kebab_Meat"]), None,
                                      ["xp[Food_Bread]", "12900", str(XP["Food_Bread"]), "xp[Food_Kebab_Meat]", "2600", str(XP["Food_Kebab_Meat"])]):
        raise SystemExit("self-check 0.1.5: CookTblMig.update of the live 0.1 shape (%r) is wrong: %r" % (_nl, _tm(_h.replace("\n", _nl))))
if _tm("enabled=true\nmaxGrade=12\n") != (XP_TBL_MARK + "\nenabled=true\nmaxGrade=12\n", "", None, []) or _tm("") != (XP_TBL_MARK + "\n", "", None, []):
    raise SystemExit("self-check 0.1.5: a file without xp lines must get only the marker (above its first entry / on top)")
print("0.1.5 checks: compiled XP table = the difficulty table (%d dishes changed); default text marker + help; "
      "CookTblMig.update: fresh 0.1.4 file -> the 0.1.5 default text, the 4 stopgap kebab values replaced, hand-set 30000 / 1700 kept + noted, "
      "the live 0.1 shape (LF + CRLF), marked file untouched, no xp line -> marker only" % len(_TBL))

# 0.1.6 self-check: the compiled CookIngMig tables, the default text (both markers + the 0.1.6 help above the xp block) and the COMPILED
# one-time update (CookIngMig.update, the pure text step). The harness (SkyyCooking/test_skyycooking_0.1.6.py) runs migrate() on copies.
_JIm = jpype.JClass(PKG + ".CookIngMig", loader=_ld)
if [str(x) for x in _JIm.KEYS] != ["xp." + i for i in _ING] or [str(x) for x in _JIm.NEWS] != [str(XP[i]) for i in _ING] \
        or [str(x) for x in _JIm.OLDS] != [str(XP_015[i]) for i in _ING] or any(str(x) for x in _JIm.STOPS) or str(_JIm.MARK) != XP_ING_MARK \
        or [str(x) for x in _JIm.HELP_OLD] != XP_HELP_015 or [str(x) for x in _JIm.HELP_NEW] != XP_HELP_016 or len(_ING) != len(INGS):
    raise SystemExit("self-check 0.1.6: compiled CookIngMig tables are not the build's (%d keys)" % len(_ING))
_blk16 = XP_ING_MARK + "\n" + XP_TBL_MARK + "\n" + "\n".join(XP_HELP_016) + "\nxp.default=%d\n" % XP_DEFAULT
if DEFAULTS_TEXT.count(_blk16) != 1 or any(h in DEFAULTS_TEXT for h in XP_HELP_015 + XP_HELP_OLD) \
        or not all(DEFAULTS_TEXT.count("\nxp.%s=%d\n" % (k, v)) == 1 for k, v in XP.items()):
    raise SystemExit("self-check 0.1.6: the default text must carry both markers + the 0.1.6 help right above xp.default and the 0.1.6 table")
def _im(t):
    r = _JIm.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]])
_chg16 = ", ".join("xp.%s %d -> %d" % (i, XP_015[i], XP[i]) for i in _ING)
_rows16 = [x for i in _ING for x in ("xp[%s]" % i, str(XP_015[i]), str(XP[i]))]
if _im(DEFAULTS_015) != (DEFAULTS_TEXT, _chg16, None, _rows16):
    raise SystemExit("self-check 0.1.6: CookIngMig.update of the fresh 0.1.5 file is not exactly the 0.1.6 default text: %r" % (_im(DEFAULTS_015),)[:600])
_r = _tm(_f014(XP_OLD))           # a 0.1.4 file: CookTblMig then CookIngMig (setup()'s order) -> the 0.1.6 default text
if _r is None or _im(_r[0]) != (DEFAULTS_TEXT, _chg16, None, _rows16):
    raise SystemExit("self-check 0.1.6: a 0.1.4 file through CookTblMig + CookIngMig is not the 0.1.6 default text")
_cu = DEFAULTS_015.replace("\nxp.Ingredient_Flour=1425\n", "\nxp.Ingredient_Flour=500\n").replace("\nxp.Ingredient_Salt=140\n", "\nxp.Ingredient_Salt=%d\n" % XP["Ingredient_Salt"])
_r = _im(_cu)
if _r is None or "\nxp.Ingredient_Flour=500\n" not in _r[0] or _r[2] != "xp.Ingredient_Flour=500 kept (custom) - the 0.1.6 default is %d" % XP["Ingredient_Flour"] \
        or len(_r[3]) != 3 * (len(_ING) - 2) or "xp.Ingredient_Salt" in _r[1]:
    raise SystemExit("self-check 0.1.6: a hand-set value must be kept + noted, a value already on 0.1.6 kept silently: %r" % (_r,))
if _JIm.update(DEFAULTS_TEXT) is not None:
    raise SystemExit("self-check 0.1.6: CookIngMig.update must leave a marked file alone")
for _nl in ("\n", "\r\n"):
    _h = "enabled=true\n" + XP_TBL_MARK + "\n" + "\n".join(XP_HELP_015) + "\nxp.default=1000\nxp.Food_Bread=9100\nxp.Ingredient_Flour=1425\nxp.Ingredient_Salt=140\n"
    _w = "enabled=true\n" + XP_ING_MARK + "\n" + XP_TBL_MARK + "\n" + "\n".join(XP_HELP_016) + "\nxp.default=1000\nxp.Food_Bread=9100\nxp.Ingredient_Flour=%d\nxp.Ingredient_Salt=%d\n" % (XP["Ingredient_Flour"], XP["Ingredient_Salt"])
    if _im(_h.replace("\n", _nl)) != (_w.replace("\n", _nl), "xp.Ingredient_Flour 1425 -> %d, xp.Ingredient_Salt 140 -> %d" % (XP["Ingredient_Flour"], XP["Ingredient_Salt"]), None,
                                      ["xp[Ingredient_Flour]", "1425", str(XP["Ingredient_Flour"]), "xp[Ingredient_Salt]", "140", str(XP["Ingredient_Salt"])]):
        raise SystemExit("self-check 0.1.6: CookIngMig.update of the live 0.1.5 shape (%r) is wrong: %r" % (_nl, _im(_h.replace("\n", _nl))))
if _im("enabled=true\nmaxGrade=12\n") != (XP_ING_MARK + "\nenabled=true\nmaxGrade=12\n", "", None, []) or _im("") != (XP_ING_MARK + "\n", "", None, []):
    raise SystemExit("self-check 0.1.6: a file without xp lines must get only the marker")
print("0.1.6 checks: compiled CookIngMig tables (%d ingredient keys); default text (both markers + 0.1.6 help); CookIngMig.update: fresh "
      "0.1.5 file -> the 0.1.6 default text, a 0.1.4 file through both updates -> the same, hand-set 500 kept + noted, the live 0.1.5 shape "
      "(LF + CRLF), marked file untouched, no xp line -> marker only" % len(_ING))

jar = os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyCooking", VERSION, "SkyWynn Cooking: dishes cooked at the Cooking Bench come out graded by your Cooking level (SkyySkills) - Grade = level / 10, heal and buffs +32% stronger per Grade (x2.6 at level 50, x4.2 at 100) and lasting x2 longer at level 50 (x4 at 100), Grades 11-12 from the SkyyTrees Cooking tree; the Campfire dishes can be cooked at the Cooking Bench too, or instantly through the Campfire accessory in /craft (SkyySacks) as an emergency cook at 75% of the Grade bonus and 25% of the XP; Cooking XP goes to SkyySkills. /cooking; admins change its settings in game (SkyWynn Menu Server Setup, /modconfig cooking) and players hide its chat lines in /settings. Zero dependencies (without SkyySkills food stays plain).", PKG + ".SkyyCookingPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyCooking.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyCooking" % VERSION, disable_prefix="Skyy:")
