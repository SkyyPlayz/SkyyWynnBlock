"""SkyyCooking 0.1.16 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.15.py by tools/cooking_0_1_16_patch.py
0.1.16 (2026-10-21) = COOKING ING_TIER v3 (lean round cook016; docs/log 2026-10-18 "REVIEW SHIP Cooking 0.1.12 ... Follow-up: ING_TIER
  lacks Mango / Coconut / Tomato / Turnip (Tropical Smoothie XP low)"; RESUME "Cooking ING_TIER v3"). Skyy: "keep going down the list".
  1. ONE INGREDIENT TIER TABLE (ING_TIER_V3, the tools/tier_tags.py TT_VERSION 3 ladder T1-T15): every raw ingredient of every Cooking Bench
     recipe (vanilla + ours) resolves to a tier - the tier_tags row where there is one (Tomato T9, Turnip T6, Potato T13 ...); a fruit
     without a row = its tree's tier_tags log tier (Apple = Apple T2, Coconut = Palm T4 (Zone 2 islands), Mango + Pinkberry = Jungle T13
     (Jungle / Jungle crystal prefabs)); Red Berries T1 (Zone 1 bushes), Milk T2 (Zone 1 livestock, the old row), egg / rock salt / stick /
     water T1, resource groups T1 (P3 spec). The build stops on any ingredient without a tier. The 0.1.5 table (Corn / Pumpkin / Apple /
     Milk only, Bazaar steps) stays ING_TIER for the older self-checks.
  2. BOTH TIER TERMS READ IT: the P3 tier factor F(T) (T = the best ingredient tier in the whole chain, now incl. fruit + Milk - 0.1.15 read
     tier_tags only, so fruit / Milk dishes paid T1) and the difficulty share's tier step, now 5 % (dish) / 1.5 % (ingredient craft) per
     ZONE above 1 (3 tiers a zone; the 0.1.5 step was a Bazaar zone-sized step and F(T) already pays the full 15-step tier). K stays 100
     (the Vegetable Skewer + Meat Pie rate check is unchanged: both stay T1, same share). Every craft whose tiers did not move keeps its
     exact 0.1.15 number (asserted).
  3. ONE-TIME UPDATE (new class CookV3Mig = CookP3Mig's reviewed text step + History / change-log path; setup() runs ... -> CookP3Mig ->
     CookV3Mig -> CookCfg.load): every xp.<k> whose LAST entry is a one-line entry holding exactly its 0.1.15 default -> the v3 value
     (value text only); an admin's value kept (INFO); the help line about the tier step reworded 1:1; run-once marker V3_MARK above the xp
     block's comment run (a fresh file carries it); config-history copy first (verified), one change-log row per line (Undo).
  No saved-data, command, system or item change. ROLLBACK to 0.1.15: plain; Server Setup -> Changes -> Undo (or the config-history copy)
  puts the old xp lines back.
  CHECKED: SkyyCooking/test_skyycooking_0.1.16.py.
0.1.15 was DERIVED from build_skyycooking_0.1.14.py by tools/cooking_0_1_15_patch.py:
0.1.15 (2026-10-20) = BALANCE PASS P3 - XP, the SkyyCooking part (research/Balance-P3-XP-Spec.md 3.5; with SkyySkills 0.4.57 - deploy
  together). Skyy (2026-10-18): "lets try to balance the xp gain, and how much more each level costs to make all skills, and your class level
  pretty close to the same rate" + popup 2026-10-20 "Middle: Lv 50 at ~33 h".
  1. COOKING XP x THE TIER FACTOR: every xp.<dish / ingredient> default = the 0.1.14 formula (chain raw x K x the difficulty share) x F(T),
     T = the highest tools/tier_tags.py tier among the craft's whole ingredient chain (untagged items and resource groups = T1; F = the spec
     section 3 table: T1 1.00 ... T15 48.56). K (was 950) is set so the build's rate check (ITEMS_PER_HOUR 1800 raw items an hour) pays
     48,000 x F(T) Cooking XP an hour on the Vegetable Skewer after xpMultiplier 0.5 (the model's 60 dishes x 800 x F); the build prints
     the pie's rate too (harder dishes keep paying more per item - Skyy's difficulty rule). LV50 = 487,440 (SkyySkills 0.4.57's list, levels
     1-50 at levels.scale 120 %). maxXpPerMinute stays 0 (0.1.13), campfire.xpFactor 0.25 and xpMultiplier 0.5 stay.
  2. ONE-TIME UPDATE (new class CookP3Mig = CookIngMig's reviewed text step + History / change-log path; setup() runs ... -> CookNcMig ->
     CookP3Mig -> CookCfg.load): every xp.<k> whose LAST entry is a one-line entry holding exactly its 0.1.14 default -> the P3 value
     (value text only); an admin's value kept (INFO); the xp block's help line about the formula reworded 1:1; run-once marker P3_MARK above
     the xp block's comment run (a fresh file carries it); config-history copy first (verified), one change-log row per line (Undo).
  ROLLBACK to 0.1.14: plain; Server Setup -> Changes -> Undo (or the config-history copy) puts the old xp lines back.
  CHECKED: SkyyCooking/test_skyycooking_0.1.15.py.
0.1.14 was DERIVED from build_skyycooking_0.1.13.py by tools/cooking_0_1_14_patch.py:
0.1.14 (2026-10-20) = SKILL TREES 3 R3b, the SkyyCooking part (tools/trees_v3_effects.py). Skyy (2026-10-18): "i want all the skill
  trees to follow the same general pattern. drop the dust" - SkyyTrees 0.4.0 replaced the 12-node Cooking tree; five of the 0.3 nodes
  SkyyCooking read have no v3 upgrade any more (SkyyTrees always answers 0 for them):
  1. DEAD NODES DROPPED: Grill / Prep / Baker Mastery (CGrill / CPrep / CBaker: +1 Grade chances on T1 / T2 / T3 dishes) and Master Chef
     (CMaster: +1 guaranteed Grade) are never asked from SkyyTrees again (their level is 0; the dish roll, the bench Grade and the Grade
     11-12 path stay: Gourmet / Gourmet II / Signature Dish = the v3 upgrades Seasoned / Gourmet Touch / Signature Dish still reach Grade 12).
     Their tree.<Id>.per lines and the Server Setup "Skill tree" entries stay (an admin's value kept - no config change); fixer
     2026-10-20: the Server Setup row's help and a NEW file's comments now say they are unused since SkyyTrees 0.4 and that CIngr is
     Forager's Larder (the SkyyExploration Scavenger row's wording).
  2. PREP COOK MOVES TO FORAGER'S LARDER (Pantry b2 r1a, "+3% ingredient yield/rank"): the chance an ingredient craft (flour, dough, salt,
     spices) gives double output = Forager's Larder's rank x tree.CIngr.per (default 0.03 = the upgrade's +3 % a rank), read from SkyyTrees
     tree:fn:level { UUID, "Skill.Cooking.b2.r1a" } (clamped to its max 3; SkyyTrees 0.4.0 answers 0 until its v3
     hook build) - never the dead "Cooking.CIngr". tree:reads:SkyyCooking = "Skill.Cooking.b2.r1a" (put at setup, our value removed at
     shutdown).
  Gourmet (CGourmet), Batch Cook (CBatch), Frugal (CFrugal), Gourmet II (CGourmet2) and Signature Dish (CSig) are read exactly as before.
  No saved data, config row, command or system change. ROLLBACK to 0.1.13: safe (0.1.13 asks the dead nodes again; SkyyTrees answers 0).
0.1.13 was DERIVED from build_skyycooking_0.1.12.py by tools/cooking_0_1_13_patch.py
(0.1.12 / 0.1.11 / 0.1.10 / 0.1.9 / 0.1.8 / 0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by
tools/cooking_0_1_12_patch.py / _0_1_11_patch.py / _0_1_10_patch.py / _0_1_9_patch.py / _0_1_8_patch.py / _0_1_7_patch.py / _0_1_6_patch.py /
_0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.13.py           -> SkyyCooking/SkyyCooking-0.1.13.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

0.1.13 = NO XP CAPS (lean round xpc). SKYY'S WORDS (docs/answered/skills.md 2026-10-18 'NO XP CAPS'): "is there a cap on acrobatics xp
 gain? or any other xp gain? if so remove all caps" -> every XP gain cap goes (0 = no cap); 2026-10-19: "work through the bugs one at a time
 until you run out". SkySkills 0.4.53 did its own caps; this is the Cooking part (RESUME: "XP caps in Cooking / Guilds / Exploration -> 0").
 1. THE ONE COOKING XP CAP: maxXpPerMinute (base Cooking XP per player per minute, bench dishes + Campfire accessory batches share it) -
    default 1,500,000 -> 0. 0 already meant "no cap" (Cook.allowXp / allowXpPart return at once, the row's help says "0 = no cap"), so no
    code path changes: only the default (row, loader fallback CookCfg.DEF_MAX_PER_MIN, field, the generated cooking.properties line).
    Nothing else in SkyyCooking caps XP (campfire.xpFactor is a share, not a cap; the Supplies / Grade / effect caps are not XP).
 2. ONE-TIME UPDATE of an existing cooking.properties (new class CookNcMig = CookXpMig's reviewed text step, same CookMig.kit / saved /
    logLine machinery; setup() runs CookMig -> CookXpMig -> CookTblMig -> CookIngMig -> CookNcMig -> CookCfg.load -> CfgPub.start): a
    one-line maxXpPerMinute entry still holding the old default 1500000 becomes 0 (value text only: key, separator, CR kept); a hand-set
    value is kept and logged (INFO "... kept (custom)"); no line = nothing (the default 0 applies). History copy "before the 0.1.13 no XP
    caps update" first, verified byte for byte (else WARN, file untouched, the next start tries again); one config-changes.log line
    (Server Setup -> Changes -> Undo); run-once marker NC_MARK above the entry's help comment (a fresh file carries it). Bytes and line
    endings kept (ISO-8859-1 in and out, CR per line as found).
 3. The build's own self-check of Cook.allowXpPart now sets the old 1.5M window for its test and checks that 0 pays a whole batch.
 ROLLBACK to 0.1.12: plain (redeploy SkyyCooking-0.1.12.jar). 0.1.12 reads maxXpPerMinute=0 as "no cap" too; to bring the old cap back
    Undo the 0.1.13 line in Server Setup -> Changes (or set XP cap per minute = 1500000). No saved-data change.

0.1.12 = OUR OWN PIES, SALAD, DRINKS, BUTTER + SLICED BREAD (lean round cook12). SKYY'S WORDS (docs/answered/project.md 2026-10-18, popup):
 Q "Connor's More Food Stuff has no licence and uses heal effects missing from the current game, so it can't be packed yet. What now?"
 -> "Make our own dishes" (earlier the same day, on its CurseForge page: "this would be good too, if we can use it"). That mod is All
 Rights Reserved: NOTHING of it is used - no file opened, no id, recipe, number or name; research/Farming-Mods-Survey.md section 1 only
 told us the KINDS of food (pies, a salad, drinks, butter, sliced bread). Every dish below is ours: our names, our recipes from vanilla
 ingredients only, our numbers from SkyyCooking's own food-family rules, vanilla models / icons / sounds read from Assets.zip at build time.
 1. TWELVE NEW OWN DISHES (OWN list, Cooking Bench, graded G0-G12 like every own dish, gradedOwn): base ids Food_Skyy_<Name> (graded
    copies Skyy_Cook_Food_Skyy_<Name>_G<g>, so cook:prefix / the Farming sack / the Food Pouch take them with no change):
      tier  dish                 bench      recipe (vanilla ids)                                                     makes
      T1    Butter               Prepared 3s  1 Milk Bucket (resource Milk_Bucket)                                    1 + the bucket back
      T1    Sliced Bread         Baked 3s     1 Ingredient_Dough + 2 Fuel                                             2
      T1    Berry Cordial        Prepared 1s  1 water Tankard (*Deco_Tankard_State_Filled_Water) + 3 Red Berries      1 + the Tankard back
      T1    Vegetable Broth      Baked 3s     1 water Tankard + 1 Carrot + 1 Onion + 1 Salt + 1 Fuel                  1 + the Tankard back
      T2    Farmhouse Salad      Prepared 1s  1 Lettuce + 1 Tomato + 1 Turnip + 1 Cheese                              1
      T2    Spiced Cider         Prepared 2s  1 water Tankard + 2 Apples + 1 Spices                                   1 + the Tankard back
      T2    Pinkberry Milkshake  Prepared 2s  1 Milk Bucket + 2 Pinkberries                                           1 + the bucket back
      T3    Tropical Smoothie    Prepared 2s  1 Milk Bucket + 1 Mango + 1 Coconut + 2 Red Berries                     1 + the bucket back
      T3    Cottage Pie          Baked 5s     1 Dough + 1 Meats + 2 Potatoes + 3 Fuel                                 1
      T3    Fisherman's Pie      Baked 5s     1 Dough + 2 Raw Fish + 1 Onion + 3 Fuel                                 1
      T3    Coconut Cream Pie    Baked 5s     1 Dough + 1 Coconut + 1 Milk Bucket + 3 Fuel                            1 + the bucket back
      T3    Forager's Pie        Baked 5s     1 Dough + 2 Mushrooms + 1 Cauliflower + 3 Fuel                          1
    Containers come back like vanilla's own recipes do (Food_Cheese returns Container_Bucket, Ingredient_Dough returns the empty
    Deco_Tankard): own_returns() adds them from the inputs, so nothing is lost and no new container item exists.
 2. NUMBERS = SkyyCooking's food-family rules, nothing new (0.1.8 / 0.1.10, unchanged): the recipe's ingredient families set the bars
    (Veggie Health, Fruit Mana, Meat Stamina, Mushroom Strength, Grain = half Health + half Stamina, Dairy, Egg & Fish = half Stamina +
    half Mana; share per family 1 / 0.6 / 0.45 for 1 / 2 / 3 families), the tier sets the size (instant Health / Mana 5 / 8 / 12 %, Stamina
    10 / 20 / 30 %; over time 0.5 / 0.8 / 1.2 % every 2 s, Stamina +10 / 20 / 30 % max, Strength +2 / 4 / 6), Grade x (1 + 0.32 g), 6:00
    x 2^(g/5). Grade 0 values (instant; over time), printed by the build ("0.1.12 new dishes"):
      (now = instant, % of max; then = the over-time buff, 6:00 at Grade 0; XP = base Cooking XP per craft)
      T1 Butter               Dairy                now Mana 2.5%, Stamina 5%              then Mana 0.3%/2s, Stamina +5%                           850 XP
      T1 Sliced Bread         Grain                now Health 2.5%, Stamina 5%            then Health 0.3%/2s, Stamina +5%                        8850 XP
      T1 Berry Cordial        Fruit                now Mana 5%                            then Mana 0.5%/2s                                        850 XP
      T1 Vegetable Broth      Veggie               now Health 5%                          then Health 0.5%/2s                                     1350 XP
      T2 Farmhouse Salad      Veggie+Dairy         now Health 4.8%, Mana 2.4%, Stamina 6% then Health 0.5%/2s, Mana 0.2%/2s, Stamina +6%          2550 XP
      T2 Spiced Cider         Fruit                now Mana 8%                            then Mana 0.8%/2s                                       3650 XP
      T2 Pinkberry Milkshake  Fruit+Dairy          now Mana 7.2%, Stamina 6%              then Mana 0.7%/2s, Stamina +6%                          1400 XP
      T3 Tropical Smoothie    Fruit+Dairy          now Mana 10.8%, Stamina 9%             then Mana 1.1%/2s, Stamina +8.9%                        2000 XP
      T3 Cottage Pie          Veggie+Meat+Grain    now Health 8.1%, Stamina 20.2%         then Health 0.8%/2s, Stamina +20.4%                    11100 XP
      T3 Fisherman's Pie      Veggie+Grain+Dairy   now Health 8.1%, Mana 2.7%, Stamina 13.5% then Health 0.8%/2s, Mana 0.3%/2s, Stamina +13.8%      14950 XP
      T3 Coconut Cream Pie    Fruit+Grain+Dairy    now Health 2.7%, Mana 8.1%, Stamina 13.5% then Health 0.3%/2s, Mana 0.8%/2s, Stamina +13.8%      12350 XP
      T3 Forager's Pie        Veggie+Mushroom+Grain now Health 8.1%, Stamina 6.8%          then Health 0.8%/2s, Stamina +6.6%, Strength +2.8      10850 XP
    BALANCE (vs the existing dishes): the tiers sit where their effort sits - T1 = one cheap step (one bucket of milk, one dough, one
    tankard of water: the price of vanilla's T1 Roast Vegetable / Grilled Fish up to a little more), T2 = 3-4 ingredients like the vanilla
    skewers and salads, T3 = a dough + 3 fuel pie or a 4-ingredient smoothie like vanilla's T3 pies / Caesar / Popcorn. Sliced Bread: one
    dough + 2 fuel gives TWO T1 slices; bread (T2) is one dough + 3 fuel for ONE loaf: the two slices restore about what the loaf does at once
    (2 x 2.5 % health + 2 x 5 % stamina vs 4 % + 10 %) but only a T1 buff (one buff per bar - a second slice never adds a second buff), so
    slicing is a convenience, not a gain. Butter (one milk) is a weaker cousin of Cheese's role with a small buff (Cheese stays a raw
    snack). No new effect: the instant part is the same inline copy of vanilla Food_Instant_Heal_T1 every dish uses, the over-time parts are
    this jar's Skyy_Cook_Fx_<bar>_<k> ladder (new dishes only add ladder steps their weights need; Food_Instant_Heal_T2 / T3 - missing
    from the current game - are never named).
    COOKING XP = the LOCKED difficulty rule (Skyy 2026-10-04: "the easier to craft the less xp. the harder to craft the more."): chain raw x
    950 x (20 % + 15 % per extra crafting step + 5 % Prepared / 10 % Baked + 5 % per ingredient tier above 1, Milk T2), x the craft's
    output count (new: Sliced Bread makes 2 - every other own dish makes 1, so their XP is unchanged). The build's checks still hold: an
    easy dish pays less than any 3-step one, no own dish is a much faster levelling route than the vanilla best (<= 1.15 x), the meat-pie
    route keeps level 50 in 25-30 h. Values printed by the build ("0.1.8 own dish XP").
 3. LOOKS (vanilla, read from Assets.zip at build time, never committed): pies = the Pie model (Forager's Pie with the vanilla Mushroom pie
    texture), salad = the Caesar salad, Sliced Bread = the bread, Butter = the Cheese model, drinks = the vanilla filled Tankard (Cordial,
    Broth, Cider) / filled Mug (Milkshake, Smoothie) model, icon, icon angle and the vanilla drink animation (Deco_Tankard's
    PlayerAnimationsId; the eat charge plays its "Consume" animation like Template_Food's, no mouth crumbs) + drink sounds (SFX_Health_Potion_Low_Drink_Local while drinking, SFX_Water_MoveOut when done). Drinks still eat
    through the food chain (Cooking's 1.875 s fast eat, never cancelled by a hit) so the Food Pouch takes them like any dish. Quality by
    tier: T1 Common, T2 Uncommon, T3 Rare (the vanilla dishes' pattern). Art of our own = follow-up.
 4. ORDER: the OWN list is sorted by tier, then name (PROJECT-RULES "sort by tier everywhere"): the Server Setup graded list, /cook's dish
    list and the Food Pouch's tie order follow it. The Cooking Bench's own recipe order is the engine's (UNVERIFIED).
 5. NOT TIER-TAGGED: food is "left untagged on purpose" in tools/tier_tags.py (its docstring), so no tier tag row is added; the tooltip
    shows the tier through the Quality colour like every dish.
 6. SAVED DATA: none changes. New item ids only; cooking.properties is not rewritten (xp.<new dish> lines missing = the built-in value,
    the loader's rule since 0.1; gradedOwn grades them even when a live graded= line lists only the old dishes); supplies files untouched.
 ROLLBACK: to 0.1.11 = redeploy SkyyCooking-0.1.11.jar. Safe until players own a new dish; after that the new dishes (and Food Pouch
    stores holding them: pouch.<id> lines stay in the store file, unusable, and come back when 0.1.12+ returns) become Invalid Items -
    deploy-forward only once they exist in the world. No config / saved-data migration to undo.

0.1.11 = POTION FLASK + FOOD POUCH (round FP1; research/Flask-Pouch-Spec.md sections 1-4 + 6; the FP0 probe SkyyFlaskProbe 0.1.0 passed in
 game 2026-10-17, docs/log/2026-10.md). SKYY'S WORDS (docs/answered/skills.md 2026-10-16): "a healing potion that holds all the healing
 options you have (they do in automatically like our pockets.) and when you right click it it drinks a potion. (sorted from worst to best.
 and drinks the first first.) id like to do that for healing potions and food." + "(takes the normal eat/drink time to consume.)" + popups
 "Two items", "Healing only", "Yes, lifelong", "auto like the void, with a toggle." + answers "all food, we will add a good way to swap
 between health stamina and mana" (worst first across ALL food), "Storage > Supplies", "Fixed for now" (Flask 64, Pouch 256, Server
 Setup), "Cooked only" (raw stays in the Void; Server Setup switch supplies.pouchRaw, default OFF).
 1. TWO LIFELONG ITEMS: Skyy_Flask_Empty / Skyy_Flask_V_<PotionId> (the 5 vanilla healing potions - every item whose Secondary is
    Root_Secondary_Consume_Potion_Health, asserted 5) and Skyy_Food_Pouch_Empty / Skyy_Food_Pouch_V_<FoodId> (every food this build
    ships: the 15 vanilla dish overrides, the 11 own dishes, every graded copy G1-G12 and the 7 raw-snack overrides; the raw ones only
    fill while supplies.pouchRaw is ON). The loaded ids are generated IN THIS BUILD from its own item JSON (spec 3.1 "one writer") - the
    FP0 probe's flat() / swap_modify() / charge_copy() / loaded_item(): a copy of the item's InteractionVars + animation fields; the ONE
    "ModifyInventory AdjustHeldItemQuantity -1" step of the charge is swapped for "ApplyEffect Skyy_Supply_Used" (the marker) followed by
    the same Next - so the effect, the eat / drink time (Cooking's 1.875 s fast eat, the 1.5 s potion), FailOnDamage false and the vanilla
    15 s potion cooldown (Skyy_Supply_Cond_Potion_Health keeps CooldownCondition Potion_Consume_Health) are exactly the item's own. Charge
    copies: Skyy_Supply_Charge_Potion_Fast (of vanilla Consume_Charge_Potion_Fast) and Skyy_Supply_Charge_Food_T<n>_Inner (of Cooking's
    Skyy_Cook_Consume_Charge_Food_T<n>_Inner_Fast); roots Skyy_Supply_Root_Potion_Health / _Root_Food_T<n> / _Root_Empty (RequireNewClick
    kept: every drink / bite is its own hold - FP0 finding 4). Crouch + right click = OpenCustomUI page "SkyySupplies" (the condition's
    Failed branch -> Skyy_Supply_Open; vanilla's Failed was Block_Secondary). The Empty items: right click = marker Skyy_Supply_Empty ->
    the "your Flask is empty" popup. FP0 findings applied: no BlockType on any of our items, Skyy_Cook_Recipe_* never a pouch source, the
    held item becomes the Empty id when the store reaches 0. Shared model / icon (no new texture), MaxStack 1, DropOnDeath false, no
    Recipe / Tags / Quality, untiered (no tier tag). One shared name / description key each (Skyy_Flask, Skyy_Food_Pouch); the live line
    is ItemDisplay metadata (the SkyyRolls way): "Potion Flask (12)" / "Next: Small Health Potion - then 4 more kinds. ...".
    Build self-checks (the probe's): every loaded id's vars = its source's flattened vars except the charge Parent; every referenced id
    exists; no path overrides Assets.zip or this jar; no id clash; the charge copies have no ModifyInventory and carry the marker.
 2. ORDER worst first (spec 3.2): Flask by total healing (instant + regen pulses x amount, from the effect assets; asserted Lesser first),
    then ItemLevel, then name. Pouch across ALL food: Grade low -> high, raw snacks first inside Grade 0, then this build's numbers()
    restore value (instant % + over-time strength), then name. The page and right click use the same order.
 3. THE STORE (per profile, tools/PROFILES-CONTRACT.md): Skyy_SkyyCooking/supplies/<pkey>.properties = flask.auto, pouch.auto,
    given.flask, given.pouch, flask.<id>=n, pouch.<id>=n, skip.<id>=true, res.<seq>=<store>|<id> (an open use), paid=<seq> ... (the
    open journal entries whose effect is in this file). Atomic write (tmp + fsync + ATOMIC_MOVE); a History copy
    (supplies/history/<pkey>-<stamp>.properties, fsynced, read back, newest 10 kept) before the first write of each session. Cached by
    the pkey String. Nothing moves while profile:busy:<uuid> is set (the task retries every 2 s, 30 times).
    JOURNAL Skyy_SkyyCooking/supplies/journal.log (fsynced, one line per change WITH its undo):
      kind|seq|pkey|store|itemId|qty|n0|timeMs|text   kinds C fill (inventory -> store; n0 = that id's inventory count before),
      T take out (store -> inventory; n0 = the count before), Q amend the qty of seq, D settled, X cancelled / undone, R reserve,
      U use, B returned, S setting, G first give.
    CRASH SAFETY = SkyySacks 0.8.17's VoidStore journal + credit-delay pattern (classes VoidStore.appendJournal / readJournal / recover /
    settleDue / settle + SackPool.credit / paidHas / unpaid, the ~v2paid ledger), adapted: the C / T line is fsynced BEFORE the item
    moves; the store change and its seq go into the store file in ONE atomic write (the paid ledger - idempotent); the entry stays open
    for SETTLE_MS = 30 s (3 engine player saves) and is then settled (D) by a 10 s timer. An entry still open at the next start (a crash /
    stop inside the window) is RECOVERED on that profile's first task, before anything else, from the live inventory (the Sacks count
    rule): C - that id's count <= n0 - qty means the removal was saved (keep / credit now), else undo the credit; T - count >= n0 + qty
    means the give was saved (keep / debit now), else credit it back. Open uses (res.*) at start-up are returned. EXACTLY ONCE: counts
    are read before and after every move and only what really moved is credited; plain stacks only (an item with metadata is never
    taken). Fills credit at once (usable at once); the 30 s window only decides what a crash undoes.
 4. USE (spec 3.3, the FP0 runtime): SupStartSys (EntityEventSystem<InteractionChainStartEvent>) on a Secondary chain of a held loaded
    id: crouching = nothing (the page opens), creative = nothing; else reserve 1 of THAT id (store -1, res.<seq>, journal R) or cancel
    the event when the store has none (+ sync). SupTick (players with an open use / a sync / an Empty click only): the marker seen ->
    commit (U); the chain gone from getChains() 250 ms with no marker -> return (B; a cancelled tap = nothing used). The held item is
    synced (ItemContainer.replaceItemStackInSlot compare-and-swap, new ItemStack(id, 1) + ItemDisplay) only when no Secondary chain runs
    and no use is open, so the effect that ran and the item paid are always the same one.
 5. AUTO-FILL like the Void (spec 2.3): InventoryChangeEvent (SupInvSys) + PlayerReady 1.5 s later -> ONE deduplicated world-thread task
    per player (the skyyonce task pattern); from main storage + backpack ONLY (the hotbar is never touched); per store Auto-fill
    (default ON) + per item "Auto-fill this"; full = the rest stays, one popup per supplies.fullNoticeSeconds. supplies.on OFF = the
    items only open the page (they show the Empty id), nothing fills; take-out still works.
 6. BRIDGE (plain java.lang types, put in setup, removed in shutdown only while still ours): supply:fn:claims = Function(Object[]
    {UUID, String itemId}) -> Boolean.TRUE when the Flask / Pouch takes that id NOW (supplies.on, a fillable id - raw only with
    pouchRaw -, that store's Auto-fill ON for the player's CURRENT profile, the id not skipped, the store not full, not busy); answered
    from memory only (the per-player profile cache + the store cache; FALSE when either is not known yet) - cheap and thread-safe;
    supply:fn:counts = Function(UUID) -> HashMap itemId -> Long (null = busy / not loaded); hub:tab:storage:supplies (HUBS-CONTRACT).
 7. LIFELONG (tools/skyyonce.py PREFIX MODE: FlaskOnce* item_prefix Skyy_Flask_, PouchOnce* item_prefix Skyy_Food_Pouch_; switch
    supplies.lifelong). Cooking itself gives every profile one of each ONCE (given.flask / given.pouch, storage first, existing profiles
    too, profile:busy respected; a full inventory = a line naming /flask or /pouch).
 8. THE PAGE Storage > Supplies (kit 1.7 SUI.hub_page 1600 x 980, research/Menu-Pattern.md 3): sub-tabs [Potion Flask] [Food Pouch] + the
    store's Auto-fill switch on the right of the sub row; a scroll_list of list_card rows (worst -> best, the first one "Next"); the
    456 px detail panel (Take 1 = Primary, Take all, Auto-fill this: ON / OFF); footer: the status line + Put all in. No back buttons,
    inline only, icons are plain ids (never an ItemGridSlot). /flask and /pouch (hytale:Adventurer): give one back when you hold none,
    else open the page on that tab (HANDOFF 3 rule 3: nothing else added).
 REVIEW FIXES (critic round): recovery decides the open entries of one (profile, id) as a CHAIN in time order (SupOps.chainCut: the live
    count = the state the inventory was saved at; no match = the per-entry rule) - a take + re-fill or a fill + take before a crash is
    never doubled or lost; a Take keeps that id out of auto-fill and supply:fn:claims for 60 s (SupStore.MUTE; Skyy on the Void: "make it
    so, if you click take out, the auto store doesn't put it back in automatically."); a recovered entry whose D / X line cannot be
    written stays OPEN; a use's store write is retried and then logged loudly (saveHard); the store's dirty flag is a version counter.
    supply:fn:claims stays by id; SkyySacks 0.8.18 asks it only for plain stacks in storage / backpack (and pickups, which land in the
    storage), so a hotbar or metadata stack is never stranded.
 9. SERVER SETUP (Cooking > Supplies, new file Skyy_SkyyCooking/supplies.properties, written from its defaults when missing - no migration):
    supplies.on, supplies.lifelong, supplies.flaskCap 64, supplies.pouchCap 256, supplies.pouchRaw false, supplies.fullNoticeSeconds 60.

0.1.10 = ONE FOOD TYPE (lean round cook0110; docs/answered/skills.md 2026-10-16, Skyy on a screenshot of an Uncommon Vegetable Skewer
 'Health food (Veggie)' restoring health, mana and stamina: "why do vegetables give health mana and stamina? this is 1 food type. not all 3").
 The 0.1.8 higher-tier all-round share (ALLROUND T2 0.15 / T3 0.25 on every bar the families leave empty) is gone: ALLROUND = 0 at every
 tier, so a dish restores ONLY its own families' bars - Veggie = Health, Fruit = Mana, Meat = Stamina, Mushroom = Strength; Grain
 (half Health + half Stamina) and Dairy, Egg & Fish (half Stamina + half Mana) keep their own mixed shares; a dish of several families
 still splits between them (SHARE unchanged). The instant restore, the over-time buffs and every tooltip follow (no Mana Regen / Stamina
 Boost line on a Veggie dish); a Mushroom-only dish (Mushroom Skewer) now restores no bar at once - only its Strength buff (tooltip
 "Grants:"; its eat chain is just the Strength check). Same item ids: food players already hold is the rebuilt item and follows on the next start.
 Running buffs: the over-time levels only the all-round share used (ALLROUND_0_1_9) stay in the jar as effect + check files (the bar
 ladders are byte-equal to 0.1.9), so a buff still running from a 0.1.9 dish keeps loading, still stacks by the one-buff-per-bar rule
 and runs out. No saved data, no id, no class logic changes (only the version texts).

0.1.9 = FOOD STRENGTH DURATION (lean round small01; docs/answered/skills.md 2026-10-16 "FOOD STRENGTH DURATION": popup Q "FOOD: mushroom
 dishes' Strength buff lasts a flat 6 min at every Grade, capped at +20% ..." -> Skyy: "scale with grade. 10 minuet cap").
 The Strength bar's over-time buff lasts 360 s x 2^(Grade/5) again (the same Grade rule as every other bar) but never longer than
 STRENGTH_DURATION_S = 600 s (10:00): G0 6:00, G1 6:54, G2 7:55, G3 9:05, G4+ 10:00. The +20 % Strength cap (OVER_CAP) stays. Build
 constants only (baked into the item assets like every food number); the tooltip's Strength line shows its own duration whenever the
 cap makes it shorter than the dish's "Duration:". No saved data, no id, no class logic changes (only the version texts).

0.1.8 = FOOD FAMILIES (round cook018; docs/answered/skills.md 2026-10-16 "BUILD FOOD FAMILIES" + "FOOD POPUP ANSWERS"; spec
 research/cloud/Food-Expansion-Draft.md sections 1-5, 9, 10, the popup answers win). Skyy quoted the 2026-10-06 decision ("Food = mixed,
 with combos / Food is the main way to heal. / The ingredient family sets what a dish restores: Veggies restore Health ... Fruit restores
 Mana. Meat restores Stamina. Mushrooms give bonus effects, like temporary Strength or crit damage.") and said "lets build this in.";
 popups: "faster eating. never cancel." / "No Sated" / in-between foods = "Own families" / mushrooms = "Strength (Recommended)".
 1. FAMILIES. Every dish's restore comes from its recipe's ingredient families (read from the recipe at build time, asserted against the
    table below): Veggie = Health, Fruit = Mana, Meat = Stamina, Mushroom = Strength (+1 % damage each, temporary), and the two own
    in-between families: Grain (wheat, flour, dough, bread, corn, rice) = half Health + half Stamina; Dairy, Egg & Fish (milk, cheese,
    eggs, fish) = half Stamina + half Mana. Salt, spices, sticks, fuel, water: no family. A dish of N families gives each family a share
    (1 family 1.00, 2 = 0.60 each, 3 = 0.45, 4 = 0.36 - more total, spread thinner). Higher tiers also give a small part of every bar
    the families leave empty (Health / Mana / Stamina): T2 0.15, T3 0.25 ("better foods give smaller instant + over-time boosts to all
    three"). Per bar, Grade 0, weight 1.00 (x weight x (1 + 0.32 x Grade), duration 360 s x 2^(Grade/5) - the Grade rules unchanged):
      Health   instant 5 / 8 / 12 % max health (T1 / T2 / T3, cap 60 %); over time 0.5 / 0.8 / 1.2 % every 2 s + max health
               (+8.33 % per 1 % pulse: T3 = +10 %, cap +50 %; pulse cap 6 %)
      Mana     instant 5 / 8 / 12 % max mana (cap 100 %); over time 0.5 / 0.8 / 1.2 % every 2 s (cap 6 %) - SkyyCooking alone
      Stamina  instant 10 / 20 / 30 % max stamina (cap 100 %); over time +10 / +20 / +30 % max stamina + (that / 600) stamina every
               0.1 s (cap +150 %)
      Strength over time +2 / +4 / +6 Strength = +2 / +4 / +6 % outgoing damage (engine OutgoingDamage, Physical / Projectile /
               Elemental - three disjoint damage roots, one hit counts once; cap 20 = OVER_CAP; FLAT 360 s at every Grade =
               STRENGTH_DURATION_S / STRENGTH_GRADE_DURATION False - critic default, open question for Skyy)
    Stacking (vanilla rule kept): one over-time buff per bar; a weaker one never replaces a stronger one (EffectCondition on every
    stronger level -> clear every weaker level -> apply). Buffs of different bars stack (a Veggie + a Fruit dish = Health + Mana).
    A Health dish also clears vanilla HealthRegen_Buff_Raw / _T1-T3 + Meat_Buff_T1-T3 and the 0.1.7 Skyy_Cook_HealthRegen / Meat buffs; a
    Stamina dish clears vanilla FruitVeggie_Buff_T1-T3 + the 0.1.7 Skyy_Cook_FruitVeggie buffs (VANILLA_CLEAR / LEGACY_CLEAR). A raw vanilla
    crop / fruit eaten AFTER a dish still adds its own HealthRegen_Buff_Raw (vanilla's own check) - it stacks until it runs out (60 s).
 2. EVERY VANILLA FOOD: the 15 cooked vanilla dishes AND the raw meats (beef, chicken, pork, wildmeat), raw fish, egg and cheese are
    pack overrides of the vanilla item (same path + id; only InteractionVars Effect / Consume_Charge / Skyy_Cook_Apply_* and the
    description key change, the Recipe, model, Quality stay) - so food already in chests, made at a Campfire or dropped by mobs follows
    the families at Grade 0. Proof a pack item file wins over the vanilla one: SkyyArmory's overrides of the vanilla Weapon_Staff_<metal>
    items (docs/log 2026-10-08: "players always had Armory's staffs"). Raw snacks: instant only (raw meat / fish / egg 0.5 x T1, cheese
    1.0 x T1), no over-time buff. NOT overridden (follow-up): raw crops + raw fruit (Template_Crop_Item / Template_Fruit children -
    DynamicSeasons patches 14 crops + apple + coconut and overrides Root_Secondary_Consume_Food_T1, and Orchard / DynamicSeasons /
    BetterBiomes fruits inherit Template_Fruit, so an override there would change pack mods' content); mushrooms (not edible in vanilla;
    the glowing ones poison); Candy Cane (event treat). They keep vanilla (5 % heal + raw regen).
 3. EATING: every food above eats 25 % faster (our copies Skyy_Cook_Consume_Charge_Food_T<n>_Inner_Fast of the vanilla charge, 2.5 s ->
    1.875 s) and getting hit NEVER cancels eating (FailOnDamage false - already vanilla 0.7's value, asserted and written explicitly).
    Potions are untouched (vanilla rule). No Sated window (Skyy: "No Sated").
 4. NEW DISHES (Cooking Bench, graded G0-G12 like the vanilla ones, XP by the LOCKED difficulty rule - easier = less XP): Garden /
    Hunter's / Forest / Woodland Skewer, Omelette, Rice Bowl, Fruit Medley, Chilli Pot, Mushroom Stew, Hearty Stew, Lunch Tray. Base ids
    Food_Skyy_<Name> (so graded copies are Skyy_Cook_Food_Skyy_<Name>_G<g> and keep the cook:prefix Skyy_Cook_Food_); models / icons
    borrowed from a vanilla dish (art = follow-up).
 5. MANA + STRENGTH: done with effects alone (Mana over time, OutgoingDamage). Follow-up bridge (DEFINED here, built nowhere yet):
      cook:fn:bonus  java.util.function.Function, apply(Object[] { java.util.UUID player }) on that player's world thread ->
                     Object[] { Double strength (Strength points of the active Skyy_Cook_Fx_Strength_<k>, 0.0 = none),
                                Double manaRegenPct (food Mana Regen %, 0.0 until SkyySkills reads it), Long msLeft (longest of the two) }
                     or null (offline / not on the world thread). SkyyGear would show Strength on the Stats page and, if it then
                     counts it, the Strength effect's OutgoingDamage must be dropped (build switch FOOD_STRENGTH_EFFECT) - never both.
      food Mana Regen %: SkyySkills adds manaRegenPct into its own Mana-regen sum (so the in-combat 50 % applies); then the Mana
                     over-time effect becomes a marker (no StatModifiers) the same round.
 6. SAVED DATA: no item id disappears (the 180 graded ids stay, now with family chains); the 144 0.1.7 effect files stay in the jar
    (a buff running from a 0.1.7 dish still loads and runs out); cooking.properties is NOT rewritten: the new gradedOwn line ("Own
    dishes graded", default on = missing line) grades the new dishes even when a live graded= line lists only the 15 vanilla ones;
    xp.<new dish> lines missing = the built-in value (the loader's rule since 0.1). Rollback to 0.1.7: the new dishes become Invalid
    Items (their asset ids are gone) - deploy-forward only once players own them.
 7. SERVER SETUP: + "Own dishes graded" (gradedOwn, live). The family numbers, eating speed and caps are BUILD constants baked into the
    item / effect assets (like the Grade numbers since 0.1): the engine reads them when assets load, so no live row can change them.

0.1.7 = SOUND PASS ROUND 2, the SkyyCooking part (2026-10-14; research/Sound-Pass-Plan.md; Skyy 2026-10-14 ~18:30 "do 1. 3. 6. 7. 8. and
 9." - item 6 = sound pass rounds 2-4 + a per-player sound switch). The round 1 recipe (SkyyQuests 0.3.1), generated by tools/soundpass_gen.py:
 1. ONE SOUND - MEAL DONE: a Cooking Bench craft that gave a GRADED dish plays SFX_Furnace_Bench_Processing_Complete to the cook only
    (2D, category UI), from CookXpTask (the world-thread task after the craft, next to the Grade / proc chat lines). Ingredient crafts
    (flour, dough ...), plain food (graded cooking off / no SkyySkills) and the Campfire accessory's quick cooking (SkyySacks' /craft
    page plays its own craft click) stay silent.
 2. CookSnd (the one helper; never throws; a missing id = one WARN; 0.5 s per player, so a batch is one sting) + the PER-PLAYER SWITCH:
    the bridge key settings:sounds:<uuid> (Boolean, SkyyMenu 0.3.25 /settings) FALSE = that player hears no SkyWynn sound.
 3. SERVER SETUP -> Cooking -> new category "Sounds" (3 rows, all live): Sounds (master) + "Meal done" on / off + its id (check=
    CookSnd.check). File: Skyy_SkyyCooking/sounds.properties (written with the defaults when missing; cooking.properties untouched).
 4. Config kit KEEP 20 -> 10 (AGENT-BRIEF: the kit default since 2026-10-05, Skyy): Server Setup keeps the 10 newest History versions.
 5. No saved-data change, no new command, no bridge key written. ROLLBACK to 0.1.6: safe (0.1.6 never reads sounds.properties).

0.1.7 also = FOOD REMAP TO HYTALE 0.7 (round cook017; docs/answered/skills.md 2026-10-14 popup COOKING, Skyy: "Map to 0.7 foods
 (Recommended)" -> point each graded dish at the closest new 0.7 food effect (Food_Health_Restore_* etc.), keep our grade scaling on top).
 The 0.7 build stopped at "vanilla effect missing": Hytale 0.7 removed Food_Instant_Heal_T2 / T3 / Bread (it now heals EVERY plain dish
 with Food_Instant_Heal_T1 = 5 %), stretched the T1 / T2 buffs to 360 s and put four dishes under Parent Food_Pie_Apple.
 6. HEAL: each graded dish keeps the heal tier it had in 0.1.6 (DISH_HEAL_06, read from the live 0.1.6 jar), pointed at the closest 0.7
    effect (player Max Health = 100, Server/Entity/Stats/Health.json, so +10 HP = the old 10 %):
      Food_Instant_Heal_T1    5 % of max health  -> Food_Instant_Heal_T1        (still in 0.7, kept)      Wildmeat / Fish / Vegetable
      Food_Instant_Heal_T2   10 % of max health  -> Food_Health_Restore_Small   (+10 health, instant)     kebabs x4, Berry / Mushroom salad
      Food_Instant_Heal_T3   15 % of max health  -> Food_Health_Restore_Medium  (+15 health, instant)     pies x3, Popcorn, Caesar salad
      Food_Instant_Heal_Bread 15 % of max health -> Food_Health_Restore_Medium  (+15 health, instant)     Bread
    The Grade scaling is unchanged on top: heal x S(g) = 1 + 0.32 x Grade (Restore Medium at Grade 12 = 72.6 health; cap 100, never
    binds). The effect assets are now Skyy_Cook_Food_Health_Restore_<Small|Medium>_G<g> (12 bases x 12 = 144, was 13 x 12 = 156).
 7. BUFFS: HealthRegen / Meat / FruitVeggie _Buff_T1-T3 still exist; the build follows 0.7's numbers (T1 / T2 now last 360 s like T3;
    strengths unchanged), Duration x D(g) = 2^(Grade/5) on top as before. 0.7's new HealthRegen_Buff_Raw (raw food, 1 % / 2 s, 60 s) joins
    the HealthRegen family as its weakest member: every graded regen clears it (vanilla T1-T3 do the same).
 8. PARENT: Food_Salad_Berry / _Mushroom / _Caesar and Food_Pie_Meat now have Parent Food_Pie_Apple. A graded copy never sits under a
    vanilla dish (its Recipe could be inherited - Cooking spec 5): the parent dish's own keys (minus Recipe / names) are merged in field
    by field (the engine's Parent merge) and the copy keeps Parent Template_Food (so it still gets Consumable, Scale, Gathering ...).
 9. Assets.zip is read from the CACHED copy (tools/serverjar.py), never the installed game file (also the sound fragment's id check).
 Item ids, recipes, XP, Grades, saved data and every Java class except the sound pass ones are unchanged; a self-check proves no
 generated file names Food_Instant_Heal_T2 / T3 / Bread and every referenced effect / interaction / item exists in 0.7.

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

GENERATED ASSETS - 0.1.8: the dish chains, effects and checks below were REPLACED by the FOOD FAMILIES assets (see the 0.1.8 note at the
top and the build's "0.1.8 assets" line); the 144 effect files stay (legacy), the 108 family checks are gone. The 0.1.7 text follows:
GENERATED ASSETS (asset pack in this jar, all copied from the game's own shapes in Assets.zip, 435 JSON files since 0.1.7):
 - Server/Entity/Effects/SkyyCook/Skyy_Cook_<Base>_G<g>.json      12 vanilla food effects x Grades 1-12 = 144 (0.1.7; was 13 = 156)
   (0.1.7: Food_Instant_Heal_T1 + Food_Health_Restore_Small / _Medium (Hytale 0.7 removed Food_Instant_Heal_T2/T3/Bread - see the
   0.1.7 FOOD REMAP note), HealthRegen_Buff_T1-3, Meat_Buff_T1-3, FruitVeggie_Buff_T1-3; vanilla JSON with ONLY the
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

VERSION = "0.1.16"
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
import serverjar as _SJ                     # 0.1.7: the CACHED Assets.zip (tools/serverjar.py) - never the installed game file
AZ = zipfile.ZipFile(_SJ.assets_zip())
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
# 0.1.7 FOOD REMAP (Skyy 2026-10-14 popup COOKING: "Map to 0.7 foods (Recommended)" - point each graded dish at the closest new 0.7 food
# effect, keep our grade scaling on top). Hytale 0.7 removed Food_Instant_Heal_T2 / T3 / Bread and heals every plain dish with
# Food_Instant_Heal_T1 (5 %); a graded dish keeps the heal tier it had in 0.1.6 (DISH_HEAL_06), on the closest 0.7 effect (HEAL_07).
# Player Max Health = 100 (Server/Entity/Stats/Health.json), so the flat +10 / +15 health of Food_Health_Restore_Small / _Medium = the old 10 / 15 %.
HEAL_07 = {"Food_Instant_Heal_T1": "Food_Instant_Heal_T1",            # 5 % of max health - still in 0.7, kept
           "Food_Instant_Heal_T2": "Food_Health_Restore_Small",       # 10 % -> +10 health (instant)
           "Food_Instant_Heal_T3": "Food_Health_Restore_Medium",      # 15 % -> +15 health (instant)
           "Food_Instant_Heal_Bread": "Food_Health_Restore_Medium"}   # 15 % -> +15 health (instant)
DISH_HEAL_06 = {'Food_Wildmeat_Cooked': 'Food_Instant_Heal_T1', 'Food_Fish_Grilled': 'Food_Instant_Heal_T1', 'Food_Vegetable_Cooked': 'Food_Instant_Heal_T1', 'Food_Bread': 'Food_Instant_Heal_Bread', 'Food_Kebab_Fruit': 'Food_Instant_Heal_T2', 'Food_Kebab_Meat': 'Food_Instant_Heal_T2', 'Food_Kebab_Mushroom': 'Food_Instant_Heal_T2', 'Food_Kebab_Vegetable': 'Food_Instant_Heal_T2', 'Food_Salad_Berry': 'Food_Instant_Heal_T2', 'Food_Salad_Mushroom': 'Food_Instant_Heal_T2', 'Food_Popcorn': 'Food_Instant_Heal_T3', 'Food_Pie_Apple': 'Food_Instant_Heal_T3', 'Food_Pie_Meat': 'Food_Instant_Heal_T3', 'Food_Pie_Pumpkin': 'Food_Instant_Heal_T3', 'Food_Salad_Caesar': 'Food_Instant_Heal_T3'}
assert sorted(DISH_HEAL_06) == sorted(DISHES)
INSTANT = ["Food_Instant_Heal_T1", "Food_Health_Restore_Small", "Food_Health_Restore_Medium"]
assert sorted(set(HEAL_07.values())) == sorted(INSTANT)
FAMILIES = ["HealthRegen", "Meat", "FruitVeggie"]
BASES = INSTANT + ["%s_Buff_T%d" % (f, t) for f in FAMILIES for t in (1, 2, 3)]
# the vanilla numbers this build was written for (Cooking spec 4.1, re-read from Assets.zip 2026-09-24; 0.1.7: the Hytale 0.7.2 numbers -
# the T1 / T2 buffs now last 360 s like T3, strengths unchanged; the two Restore heals are flat health) - self-check 4
EXPECT = {
    "Food_Instant_Heal_T1": ("heal", 5.0, None),
    "Food_Health_Restore_Small": ("restore", 10.0, None), "Food_Health_Restore_Medium": ("restore", 15.0, None),
    "HealthRegen_Buff_T1": ("regen", 1.0, 360.0), "HealthRegen_Buff_T2": ("regen", 1.5, 360.0), "HealthRegen_Buff_T3": ("regen", 2.0, 360.0),
    "Meat_Buff_T1": ("maxHealth", 1.05, 360.0), "Meat_Buff_T2": ("maxHealth", 1.10, 360.0), "Meat_Buff_T3": ("maxHealth", 1.15, 360.0),
    "FruitVeggie_Buff_T1": ("maxStamina", 1.10, 360.0), "FruitVeggie_Buff_T2": ("maxStamina", 1.20, 360.0),
    "FruitVeggie_Buff_T3": ("maxStamina", 1.30, 360.0),
}
CAP_HEAL, CAP_REGEN, CAP_MULT, CAP_RES, CAP_DUR = 100.0, 12.0, 2.5, 0.5, 2400.0
CAP_RESTORE = 100.0   # 0.1.7: flat instant health (Restore Medium x4.84 at Grade 12 = 72.6 - never binds, the 0.1.4 self-check proves it)

def r4(v): return float("%.4f" % v)
VBASE = {}
for b in BASES:
    if b not in V_EFFECTS: raise SystemExit("vanilla effect missing: " + b)
    d = rd(V_EFFECTS[b])
    kind, amount, dur = EXPECT[b]
    if kind == "heal":
        ok = d.get("ValueType") == "Percent" and abs(d["StatModifiers"]["Health"] - amount) < 1e-9 and d.get("Duration", 0) <= 0.5
    elif kind == "restore":   # 0.1.7: flat health (no ValueType = Absolute), instant
        ok = (d.get("ValueType", "Absolute") == "Absolute" and list(d["StatModifiers"]) == ["Health"]
              and abs(d["StatModifiers"]["Health"] - amount) < 1e-9 and d.get("Duration", 0) <= 0.5)
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
# 0.1.7: Hytale 0.7's HealthRegen_Buff_Raw (raw food) = the weakest HealthRegen member; vanilla T1-T3 clear it, so every graded regen does too
RAW_REGEN = rd(V_EFFECTS["HealthRegen_Buff_Raw"]) if "HealthRegen_Buff_Raw" in V_EFFECTS else None
if RAW_REGEN is None or not (RAW_REGEN.get("ValueType") == "Percent" and RAW_REGEN["StatModifiers"]["Health"] <= VBASE["HealthRegen_Buff_T1"]["StatModifiers"]["Health"]
                             and RAW_REGEN["Duration"] < VBASE["HealthRegen_Buff_T1"]["Duration"]):
    raise SystemExit("self-check 4 (0.1.7): HealthRegen_Buff_Raw is missing or no longer weaker than HealthRegen_Buff_T1: %s" % json.dumps(RAW_REGEN))

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
        elif instant: nv = min(nv, CAP_RESTORE)   # 0.1.7: flat instant health (Food_Health_Restore_*)
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

# =====================================================================================================================
# 0.1.8 FOOD FAMILIES (round cook018 - see the 0.1.8 note in the docstring). The 0.1.7 graded effects built just above (G_EFFECTS, 144
# files) stay in the jar as LEGACY files: a buff a player still has running from a 0.1.7 dish keeps loading and runs out. Nothing
# references them any more; the 108 family checks of 0.1.4-0.1.7 are gone (interactions are never saved).
# =====================================================================================================================
LEGACY_EFFECTS = sorted(G_EFFECTS)
FAMS = ["Veggie", "Fruit", "Meat", "Mushroom", "Grain", "Dairy"]
FAM_LABEL = {"Veggie": "Veggie", "Fruit": "Fruit", "Meat": "Meat", "Mushroom": "Mushroom", "Grain": "Grain", "Dairy": "Dairy, Egg & Fish"}
BARS = ["Health", "Mana", "Stamina", "Strength"]
FAM_BARS = {"Veggie": {"Health": 1.0}, "Fruit": {"Mana": 1.0}, "Meat": {"Stamina": 1.0}, "Mushroom": {"Strength": 1.0},
            "Grain": {"Health": 0.5, "Stamina": 0.5}, "Dairy": {"Stamina": 0.5, "Mana": 0.5}}
SHARE = {1: 1.0, 2: 0.6, 3: 0.45, 4: 0.36}             # per family, by the number of families in the dish (draft section 2)
ALLROUND_0_1_9 = {1: 0.0, 2: 0.15, 3: 0.25}            # 0.1.8-0.1.9: higher tiers gave this weight on every bar the families left empty
ALLROUND = {1: 0.0, 2: 0.0, 3: 0.0}                    # 0.1.10 (Skyy 2026-10-16: "this is 1 food type. not all 3"): only the families' bars
assert not any(ALLROUND.values()), "0.1.10: no all-round share at any tier"
INSTANT_BASE = {"Health": {1: 5.0, 2: 8.0, 3: 12.0}, "Mana": {1: 5.0, 2: 8.0, 3: 12.0}, "Stamina": {1: 10.0, 2: 20.0, 3: 30.0}}  # % of max
OVER_BASE = {"Health": {1: 0.5, 2: 0.8, 3: 1.2},       # % of max health every 2 s (+ max health, HP_MAX_PER_PULSE)
             "Mana": {1: 0.5, 2: 0.8, 3: 1.2},         # % of max mana every 2 s
             "Stamina": {1: 10.0, 2: 20.0, 3: 30.0},   # % more max stamina (+ that x ST_REGEN_PER_PCT stamina every 0.1 s)
             "Strength": {1: 2.0, 2: 4.0, 3: 6.0}}     # Strength points = % more outgoing damage
INSTANT_CAP = {"Health": 60.0, "Mana": 100.0, "Stamina": 100.0}
OVER_CAP = {"Health": 6.0, "Mana": 6.0, "Stamina": 150.0, "Strength": 20.0}   # critic 2: Strength cap 20 (was 30) until Skyy decides
HP_MAX_PER_PULSE, HP_MAX_CAP = 10.0 / 1.2, 50.0        # T3 Veggie (1.2 % pulse) = +10 % max health at Grade 0
ST_REGEN_PER_PCT = 1.0 / 600.0                         # +30 % max stamina -> +0.05 stamina every 0.1 s (vanilla FruitVeggie T3's regen)
BUFF_BASE_S = 360.0                                    # Hytale 0.7's food buff duration (every tier), x D(g) (unchanged rule)
STRENGTH_DURATION_S = 600.0                            # 0.1.9 (Skyy 2026-10-16: "scale with grade. 10 minuet cap"): Strength lasts
STRENGTH_GRADE_DURATION = True                         #   360 s x 2^(Grade/5) like every bar, but at most STRENGTH_DURATION_S (10:00)
# vanilla / 0.1.7 buffs one of our bars replaces (critic 1; 0.1.7 cleared vanilla regen the same way): eating a dish of that bar clears them
VANILLA_CLEAR = {"Health": ["HealthRegen_Buff_Raw"] + ["HealthRegen_Buff_T%d" % t for t in (1, 2, 3)] + ["Meat_Buff_T%d" % t for t in (1, 2, 3)],
                 "Stamina": ["FruitVeggie_Buff_T%d" % t for t in (1, 2, 3)]}
LEGACY_CLEAR = {"Health": ["HealthRegen", "Meat"], "Stamina": ["FruitVeggie"]}   # + the 0.1.7 Skyy_Cook_<fam>_Buff_T<t>_G<g> files
def bar_dur(bar, dur):
    if bar != "Strength": return dur
    return min(dur, STRENGTH_DURATION_S) if STRENGTH_GRADE_DURATION else STRENGTH_DURATION_S   # 0.1.9: the 10 min cap
assert STRENGTH_GRADE_DURATION and STRENGTH_DURATION_S == 600.0, "0.1.9: Strength duration Grade-scaled, 10 min cap"
assert [bar_dur("Strength", 360.0), bar_dur("Strength", 360.0 * 2 ** 0.8), bar_dur("Health", 1900.0)] == [360.0, 600.0, 1900.0], "0.1.9 bar_dur"
LADDER_R = 1.05                                        # over-time strengths snap to L0 x 1.05^k (<= 2.5 % off; S(12) / S(11) = 1.07 > 1.05)
LADDER_L0 = {"Health": 0.01, "Mana": 0.01, "Stamina": 0.1, "Strength": 0.1}
EAT_SPEED = 0.75                                       # Skyy 2026-10-16 popup: "faster eating. never cancel."
FOOD_STRENGTH_EFFECT = True                            # Strength through the engine's OutgoingDamage (False once SkyyGear counts cook:fn:bonus)
RAW = {"Food_Beef_Raw": ("Meat", 0.5), "Food_Chicken_Raw": ("Meat", 0.5), "Food_Pork_Raw": ("Meat", 0.5), "Food_Wildmeat_Raw": ("Meat", 0.5),
       "Food_Fish_Raw": ("Dairy", 0.5), "Food_Egg": ("Dairy", 0.5), "Food_Cheese": ("Dairy", 1.0)}    # raw snacks: instant only, x factor of T1
APPLY_VAR = dict((b, "Skyy_Cook_Apply_" + b) for b in BARS)
def fx_id(bar, k): return "Skyy_Cook_Fx_%s_%d" % (bar, k)
def chk_id(bar, k): return "Skyy_Cook_Chk_%s_%d" % (bar, k)
def r2(v): return float("%.2f" % v)

# ---- ingredient -> family (every recipe input must be known: an unknown input stops the build)
FAM_RT = {"Meats": "Meat", "Vegetables": "Veggie", "Fruits": "Fruit", "Mushrooms": "Mushroom", "Milk_Bucket": "Dairy", "Milk_Mosshorn_Bucket": "Dairy",
          "Fish": "Dairy", "Fish_Common": "Dairy", "Fish_Uncommon": "Dairy", "Fish_Rare": "Dairy", "Fish_Epic": "Dairy", "Fish_Legendary": "Dairy"}
NO_FAM_RT = ["Fuel", "Flowers"]
FAM_ITEM = {"Food_Fish_Raw": "Dairy", "Food_Egg": "Dairy", "Food_Cheese": "Dairy", "Ingredient_Flour": "Grain", "Ingredient_Dough": "Grain",
            "Food_Bread": "Grain", "Plant_Crop_Wheat_Item": "Grain", "Plant_Crop_Corn_Item": "Grain", "Plant_Crop_Rice_Item": "Grain"}
NO_FAM_ITEM = ["Ingredient_Stick", "Ingredient_Salt", "Ingredient_Spices", "*Deco_Tankard_State_Filled_Water"]
def fam_of(kind, i):
    if kind == "R":
        if i in FAM_RT: return FAM_RT[i]
        if i in NO_FAM_RT: return None
    else:
        if i in FAM_ITEM: return FAM_ITEM[i]
        if i in NO_FAM_ITEM: return None
        if i.startswith("Plant_Fruit_"): return "Fruit"
        if i.startswith("Plant_Crop_") and i.endswith("_Item"): return "Veggie"
        if i.startswith("Food_") and i.endswith("_Raw"): return "Meat"
    raise SystemExit("0.1.8: no food family for the recipe input %s %s - add it to FAM_RT / FAM_ITEM / NO_FAM_*" % (kind, i))
def inputs_of(r):
    return [(("R", x["ResourceTypeId"]) if x.get("ResourceTypeId") else ("I", x["ItemId"])) + (int(x.get("Quantity", 1) or 1),) for x in r.get("Input", [])]
def fams_of(ins):
    out = []
    for kind, i, n in ins:
        f = fam_of(kind, i)
        if f and f not in out: out.append(f)
    return sorted(out, key=FAMS.index)

# ---- our own new dishes (draft section 5; Skyy's words: "lets build this in."): (id, name, tier, Cooking Bench category, seconds,
# vanilla look donor (model / icon - art is a follow-up), inputs)
OWN = [
    ("Food_Skyy_Garden_Skewer", "Garden Skewer", 2, "Prepared", 1, "Food_Kebab_Vegetable", [("I", "Ingredient_Stick", 1), ("R", "Vegetables", 2), ("R", "Fruits", 2)]),
    ("Food_Skyy_Hunter_Skewer", "Hunter's Skewer", 2, "Prepared", 1, "Food_Kebab_Meat", [("I", "Ingredient_Stick", 1), ("R", "Meats", 2), ("R", "Vegetables", 2)]),
    ("Food_Skyy_Forest_Skewer", "Forest Skewer", 2, "Prepared", 1, "Food_Kebab_Mushroom", [("I", "Ingredient_Stick", 1), ("R", "Meats", 2), ("R", "Mushrooms", 2)]),
    ("Food_Skyy_Woodland_Skewer", "Woodland Skewer", 2, "Prepared", 1, "Food_Kebab_Fruit", [("I", "Ingredient_Stick", 1), ("R", "Fruits", 2), ("R", "Mushrooms", 2)]),
    ("Food_Skyy_Omelette", "Omelette", 2, "Baked", 3, "Food_Vegetable_Cooked", [("I", "Food_Egg", 2), ("R", "Vegetables", 1), ("I", "Food_Cheese", 1), ("R", "Fuel", 1)]),
    ("Food_Skyy_Rice_Bowl", "Rice Bowl", 3, "Baked", 5, "Food_Salad_Caesar", [("I", "Plant_Crop_Rice_Item", 2), ("R", "Vegetables", 2), ("I", "Ingredient_Salt", 1), ("R", "Fuel", 2)]),
    ("Food_Skyy_Fruit_Medley", "Fruit Medley", 3, "Prepared", 2, "Food_Salad_Berry", [("R", "Fruits", 4), ("I", "Plant_Fruit_Berries_Red", 2), ("I", "Ingredient_Spices", 1)]),
    ("Food_Skyy_Chilli_Pot", "Chilli Pot", 3, "Baked", 5, "Food_Pie_Meat", [("R", "Meats", 1), ("I", "Plant_Crop_Chilli_Item", 1), ("I", "Plant_Crop_Tomato_Item", 1), ("I", "Ingredient_Spices", 1), ("R", "Fuel", 3)]),
    ("Food_Skyy_Mushroom_Stew", "Mushroom Stew", 3, "Baked", 5, "Food_Salad_Mushroom", [("R", "Mushrooms", 3), ("I", "Plant_Crop_Potato_Item", 1), ("I", "Ingredient_Salt", 1), ("R", "Fuel", 3)]),
    ("Food_Skyy_Hearty_Stew", "Hearty Stew", 3, "Baked", 5, "Food_Pie_Pumpkin", [("R", "Meats", 1), ("R", "Vegetables", 2), ("R", "Mushrooms", 1), ("I", "Ingredient_Salt", 1), ("R", "Fuel", 3)]),
    ("Food_Skyy_Lunch_Tray", "Lunch Tray", 3, "Baked", 5, "Food_Popcorn", [("I", "Ingredient_Dough", 1), ("R", "Meats", 1), ("R", "Fruits", 1), ("R", "Mushrooms", 1), ("R", "Fuel", 3)]),
]
# ---- 0.1.12 (Skyy 2026-10-18 popup: "Make our own dishes"): our own pies, salad, drinks, butter and sliced bread - our names, recipes and
# numbers, vanilla ingredients only (see the 0.1.12 note at the top). _TW = a tankard of water (the vanilla Ingredient_Dough input form).
_TW = "*Deco_Tankard_State_Filled_Water"
NEW_OWN = [
    ("Food_Skyy_Butter", "Butter", 1, "Prepared", 3, "Food_Bread", [("R", "Milk_Bucket", 1)]),
    ("Food_Skyy_Sliced_Bread", "Sliced Bread", 1, "Baked", 3, "Food_Bread", [("I", "Ingredient_Dough", 1), ("R", "Fuel", 2)]),
    ("Food_Skyy_Berry_Cordial", "Berry Cordial", 1, "Prepared", 1, "Food_Kebab_Fruit", [("I", _TW, 1), ("I", "Plant_Fruit_Berries_Red", 3)]),
    ("Food_Skyy_Vegetable_Broth", "Vegetable Broth", 1, "Baked", 3, "Food_Vegetable_Cooked", [("I", _TW, 1), ("I", "Plant_Crop_Carrot_Item", 1), ("I", "Plant_Crop_Onion_Item", 1), ("I", "Ingredient_Salt", 1), ("R", "Fuel", 1)]),
    ("Food_Skyy_Farmhouse_Salad", "Farmhouse Salad", 2, "Prepared", 1, "Food_Salad_Caesar", [("I", "Plant_Crop_Lettuce_Item", 1), ("I", "Plant_Crop_Tomato_Item", 1), ("I", "Plant_Crop_Turnip_Item", 1), ("I", "Food_Cheese", 1)]),
    ("Food_Skyy_Spiced_Cider", "Spiced Cider", 2, "Prepared", 2, "Food_Kebab_Fruit", [("I", _TW, 1), ("I", "Plant_Fruit_Apple", 2), ("I", "Ingredient_Spices", 1)]),
    ("Food_Skyy_Pinkberry_Milkshake", "Pinkberry Milkshake", 2, "Prepared", 2, "Food_Kebab_Fruit", [("R", "Milk_Bucket", 1), ("I", "Plant_Fruit_Pinkberry", 2)]),
    ("Food_Skyy_Tropical_Smoothie", "Tropical Smoothie", 3, "Prepared", 2, "Food_Salad_Berry", [("R", "Milk_Bucket", 1), ("I", "Plant_Fruit_Mango", 1), ("I", "Plant_Fruit_Coconut", 1), ("I", "Plant_Fruit_Berries_Red", 2)]),
    ("Food_Skyy_Cottage_Pie", "Cottage Pie", 3, "Baked", 5, "Food_Pie_Meat", [("I", "Ingredient_Dough", 1), ("R", "Meats", 1), ("I", "Plant_Crop_Potato_Item", 2), ("R", "Fuel", 3)]),
    ("Food_Skyy_Fisherman_Pie", "Fisherman's Pie", 3, "Baked", 5, "Food_Pie_Pumpkin", [("I", "Ingredient_Dough", 1), ("I", "Food_Fish_Raw", 2), ("I", "Plant_Crop_Onion_Item", 1), ("R", "Fuel", 3)]),
    ("Food_Skyy_Coconut_Cream_Pie", "Coconut Cream Pie", 3, "Baked", 5, "Food_Pie_Apple", [("I", "Ingredient_Dough", 1), ("I", "Plant_Fruit_Coconut", 1), ("R", "Milk_Bucket", 1), ("R", "Fuel", 3)]),
    ("Food_Skyy_Forager_Pie", "Forager's Pie", 3, "Baked", 5, "Food_Pie_Meat", [("I", "Ingredient_Dough", 1), ("R", "Mushrooms", 2), ("I", "Plant_Crop_Cauliflower_Item", 1), ("R", "Fuel", 3)]),
]
NEW_IDS = [o[0] for o in NEW_OWN]
assert len(NEW_IDS) == 12 and not set(NEW_IDS) & set(o[0] for o in OWN) and len(set(o[1] for o in OWN + NEW_OWN)) == len(OWN) + 12, "0.1.12: 12 new ids + names"
OWN_QTY = {"Food_Skyy_Sliced_Bread": 2}                 # makes 2 (every other own dish 1)
# looks: (kind, pie texture) - kind "tankard" / "mug" = the vanilla filled drink item's model + icon + drink animation + drink sounds,
# "cheese" = the vanilla Cheese model + icon; None = the donor dish's own look
NEW_LOOK = {"Food_Skyy_Butter": ("cheese", None), "Food_Skyy_Berry_Cordial": ("tankard", None), "Food_Skyy_Vegetable_Broth": ("tankard", None),
            "Food_Skyy_Spiced_Cider": ("tankard", None), "Food_Skyy_Pinkberry_Milkshake": ("mug", None), "Food_Skyy_Tropical_Smoothie": ("mug", None),
            "Food_Skyy_Forager_Pie": (None, "Items/Consumables/Food/Pie_Textures/Mushroom.png")}
TIER_QUALITY = {1: "Common", 2: "Uncommon", 3: "Rare"}
DRINK_SFX, DRINK_DONE_SFX = "SFX_Health_Potion_Low_Drink_Local", "SFX_Water_MoveOut"
_SND = set(os.path.basename(n)[:-5] for n in ANAMES if n.startswith("Server/Audio/SoundEvents/") and n.endswith(".json"))
assert DRINK_SFX in _SND and DRINK_DONE_SFX in _SND, "0.1.12: a drink sound is missing from Assets.zip"
RETURNS = {("R", "Milk_Bucket"): "Container_Bucket", ("I", _TW): "Deco_Tankard"}   # vanilla Food_Cheese / Ingredient_Dough return these
for _rid in RETURNS.values(): assert _rid in V_ITEMS, "0.1.12: container %s missing" % _rid
assert "Filled_Water" in (rd(V_ITEMS["Deco_Tankard"]).get("State") or {}), "0.1.12: the water Tankard state is gone"
def own_returns(ins):
    out = []
    for k, x, q in ins:
        if (k, x) in RETURNS: out.append({"ItemId": RETURNS[(k, x)], "Quantity": q})
    return out
def own_look(oid, t, v):
    """0.1.12: a new dish's vanilla look (model / texture / icon / animation / sounds) + its tier's Quality, on the flat donor JSON v"""
    if oid not in NEW_IDS: return
    v["Quality"] = TIER_QUALITY[t]
    kind, tex = NEW_LOOK.get(oid, (None, None))
    bt = v.setdefault("BlockType", {})
    if tex:
        bt["CustomModelTexture"] = [{"Texture": tex, "Weight": 1}]
    if kind == "cheese":
        ch = rd(V_ITEMS["Food_Cheese"])
        v["BlockType"] = dict((k, copy.deepcopy(x)) for k, x in ch["BlockType"].items())
        v["Icon"], v["Scale"] = ch["Icon"], ch["Scale"]
        v.pop("IconProperties", None)
    elif kind in ("tankard", "mug"):
        src = rd(V_ITEMS["Deco_Tankard" if kind == "tankard" else "Deco_Mug"])
        st = src["State"]["Filled_Water"]
        for k in ("CustomModel", "CustomModelTexture", "CustomModelScale", "CustomModelAnimation", "Opacity", "HitboxType"):
            bt.pop(k, None)
            if k in st["BlockType"]: bt[k] = copy.deepcopy(st["BlockType"][k])
        v["Icon"], v["Scale"], v["IconProperties"] = st["Icon"], st["Scale"], copy.deepcopy(st["IconProperties"])
        v["PlayerAnimationsId"] = copy.deepcopy(src["PlayerAnimationsId"])
        iv = v.setdefault("InteractionVars", {})
        # the charge plays the item's own "Consume" animation (= the drink animation above), like Template_Food's charge; the donor's
        # side-bite animation + mouth crumbs are dropped
        iv["Consume_Charge"] = {"Interactions": [{"Parent": "Consume_Charge_Food_T1_Inner", "Effects": {"ItemAnimationId": "Consume"}}]}
        iv["ConsumeSFX"] = {"Interactions": [{"Parent": "Consume_SFX", "Effects": {"LocalSoundEventId": DRINK_SFX}}]}
        iv["ConsumedSFX"] = {"Interactions": [{"Parent": "Consumed_SFX", "Effects": {"LocalSoundEventId": DRINK_DONE_SFX}}]}
    for p in [v.get("Icon"), bt.get("CustomModel"), bt.get("CustomModelAnimation")] + [x.get("Texture") for x in bt.get("CustomModelTexture", [])]:
        if p and "Common/" + p not in V_COMMON: raise SystemExit("0.1.12: %s's look file %s is not in Assets.zip" % (oid, p))
    an = (v.get("PlayerAnimationsId") or {}).get("Animations", {}) if isinstance(v.get("PlayerAnimationsId"), dict) else {}
    for a in an.values():
        for k in ("FirstPerson", "ThirdPerson"):
            if a.get(k) and "Common/" + a[k] not in V_COMMON: raise SystemExit("0.1.12: %s's animation %s is not in Assets.zip" % (oid, a[k]))
OWN = OWN + NEW_OWN
OWN.sort(key=lambda o: (o[2], o[1]))                  # PROJECT-RULES: sort by tier, then name
OWN_IDS = [o[0] for o in OWN]
GDISHES = DISHES + OWN_IDS                              # every graded dish (Java CookCfg.DISHES); DISHES stays the 15 vanilla ones
OWN_RECIPE = {}
for oid, nm, t, cat, sec, donor, ins in OWN:
    if oid in V_ITEMS: raise SystemExit("0.1.8: own dish id %s collides with a vanilla item" % oid)
    if donor not in DISHES: raise SystemExit("0.1.8: %s's look donor %s is not a vanilla dish" % (oid, donor))
    OWN_RECIPE[oid] = {"Input": [({"ResourceTypeId": x, "Quantity": q} if k == "R" else {"ItemId": x, "Quantity": q}) for k, x, q in ins],
                       "Output": [{"ItemId": oid, "Quantity": OWN_QTY.get(oid, 1)}] + own_returns(ins),   # 0.1.12: + containers back
                       "BenchRequirement": [{"Type": "Crafting", "Id": "Cookingbench", "Categories": [cat]}], "TimeSeconds": sec}
# the family table this build was written for (vanilla recipes read from Assets.zip; a Hytale recipe change stops the build here)
EXPECT_FAMS = {"Food_Wildmeat_Cooked": ["Meat"], "Food_Fish_Grilled": ["Dairy"], "Food_Vegetable_Cooked": ["Veggie"], "Food_Bread": ["Grain"],
               "Food_Kebab_Fruit": ["Fruit"], "Food_Kebab_Meat": ["Meat"], "Food_Kebab_Mushroom": ["Mushroom"], "Food_Kebab_Vegetable": ["Veggie"],
               "Food_Salad_Berry": ["Veggie", "Fruit"], "Food_Salad_Mushroom": ["Veggie", "Mushroom"], "Food_Popcorn": ["Grain"],
               "Food_Pie_Apple": ["Fruit", "Grain"], "Food_Pie_Meat": ["Meat", "Grain"], "Food_Pie_Pumpkin": ["Veggie", "Grain"],
               "Food_Salad_Caesar": ["Veggie", "Meat", "Dairy"],
               "Food_Skyy_Garden_Skewer": ["Veggie", "Fruit"], "Food_Skyy_Hunter_Skewer": ["Veggie", "Meat"], "Food_Skyy_Forest_Skewer": ["Meat", "Mushroom"],
               "Food_Skyy_Woodland_Skewer": ["Fruit", "Mushroom"], "Food_Skyy_Omelette": ["Veggie", "Dairy"], "Food_Skyy_Rice_Bowl": ["Veggie", "Grain"],
               "Food_Skyy_Fruit_Medley": ["Fruit"], "Food_Skyy_Chilli_Pot": ["Veggie", "Meat"], "Food_Skyy_Mushroom_Stew": ["Veggie", "Mushroom"],
               "Food_Skyy_Hearty_Stew": ["Veggie", "Meat", "Mushroom"], "Food_Skyy_Lunch_Tray": ["Fruit", "Meat", "Mushroom", "Grain"]}
EXPECT_FAMS.update({"Food_Skyy_Butter": ["Dairy"], "Food_Skyy_Sliced_Bread": ["Grain"], "Food_Skyy_Berry_Cordial": ["Fruit"],   # 0.1.12
                    "Food_Skyy_Vegetable_Broth": ["Veggie"], "Food_Skyy_Farmhouse_Salad": ["Veggie", "Dairy"], "Food_Skyy_Spiced_Cider": ["Fruit"],
                    "Food_Skyy_Pinkberry_Milkshake": ["Fruit", "Dairy"], "Food_Skyy_Tropical_Smoothie": ["Fruit", "Dairy"],
                    "Food_Skyy_Cottage_Pie": ["Veggie", "Meat", "Grain"], "Food_Skyy_Fisherman_Pie": ["Veggie", "Grain", "Dairy"],
                    "Food_Skyy_Coconut_Cream_Pie": ["Fruit", "Grain", "Dairy"], "Food_Skyy_Forager_Pie": ["Veggie", "Mushroom", "Grain"]})
DISH_FAMS = {}
for dish in DISHES:
    if dish not in V_ITEMS: raise SystemExit("vanilla dish missing: " + dish)
    DISH_FAMS[dish] = fams_of(inputs_of(rd(V_ITEMS[dish]).get("Recipe") or {}))
for oid in OWN_IDS:
    DISH_FAMS[oid] = fams_of(inputs_of(OWN_RECIPE[oid]))
if DISH_FAMS != EXPECT_FAMS:
    raise SystemExit("0.1.8: the dish families read from the recipes are not the build's table: %s" % dict((d, DISH_FAMS[d]) for d in DISH_FAMS if DISH_FAMS[d] != EXPECT_FAMS.get(d)))

def bar_weights(fams, tier, raw=False):
    sh = SHARE[len(fams)]
    w = {}
    for f in fams:
        for b, x in FAM_BARS[f].items(): w[b] = w.get(b, 0.0) + sh * x
    if not raw:
        for b in ("Health", "Mana", "Stamina"):
            if b not in w and ALLROUND[tier] > 0: w[b] = ALLROUND[tier]
    return dict((b, round(x, 6)) for b, x in w.items())
def bars_title(fams):
    bs = []
    for f in fams:
        for b in FAM_BARS[f]:
            if b not in bs: bs.append(b)
    return " + ".join(sorted(bs, key=BARS.index)) + " food"
def snap(bar, v):
    k = int(round(math.log(v / LADDER_L0[bar]) / math.log(LADDER_R)))
    return k, float("%.4f" % (LADDER_L0[bar] * LADDER_R ** k))
def numbers(fams, tier, g, raw_factor=None):
    """(weights, instant % per bar, over-time nominal per bar, over-time snapped (k, v) per bar, duration s)"""
    w = bar_weights(fams, tier, raw=raw_factor is not None)
    inst = {}
    for b in ("Health", "Mana", "Stamina"):
        if b in w: inst[b] = r2(min(INSTANT_BASE[b][tier] * w[b] * SF(g) * (raw_factor if raw_factor is not None else 1.0), INSTANT_CAP[b]))
    over, sn = {}, {}
    if raw_factor is None:
        for b in BARS:
            if b in w:
                over[b] = min(OVER_BASE[b][tier] * w[b] * SF(g), OVER_CAP[b])
                sn[b] = snap(b, over[b])
    return w, inst, over, sn, float("%.2f" % min(BUFF_BASE_S * DF(g), CAP_DUR))

# ---- eating: our copies of the vanilla charge interactions, x EAT_SPEED, FailOnDamage false (vanilla 0.7 already false - asserted)
V_TF = rd(V_ITEMS["Template_Food"])
FAST = {}
def fast_inner(parent):
    fid = "Skyy_Cook_%s_Fast" % parent
    if parent not in FAST:
        if parent not in V_INTER: raise SystemExit("0.1.8: vanilla charge interaction %s is missing" % parent)
        v = rd(V_INTER[parent])
        nx = v.get("Next") or {}
        if v.get("Type") != "Charging" or v.get("FailOnDamage") is not False or len(nx) != 1:
            raise SystemExit("0.1.8: %s is no longer a one-step Charging with FailOnDamage false: %s" % (parent, json.dumps(v)[:300]))
        t0 = list(nx)[0]
        t1 = float(t0) * EAT_SPEED
        o = copy.deepcopy(v)
        o["FailOnDamage"] = False
        o["Next"] = {("%g" % t1): copy.deepcopy(nx[t0])}
        G_INTER[fid] = o
        files["Server/Item/Interactions/SkyyCook/%s.json" % fid] = json.dumps(o, indent=2)
        FAST[parent] = (float(t0), t1)
    return fid
def fast_charge(iv):
    """an item's (effective) Consume_Charge var with every entry's Parent pointed at our fast copy"""
    cv = copy.deepcopy(iv.get("Consume_Charge") or V_TF["InteractionVars"]["Consume_Charge"])
    for e in cv.get("Interactions", []):
        if not (isinstance(e, dict) and re.match(r"^Consume_Charge_Food_T[123]_Inner$", str(e.get("Parent")))):
            raise SystemExit("0.1.8: unexpected Consume_Charge entry %s" % json.dumps(e))
        e["Parent"] = fast_inner(e["Parent"])
    return cv

# ---- the eat chain + its vars (the over-time levels are collected in USED; the checks are written once every item is known)
I0 = VBASE["Food_Instant_Heal_T1"]
assert sorted(I0) == ["DamageCalculatorCooldown", "Duration", "OverlapBehavior", "StatModifiers", "ValueType"] and I0["ValueType"] == "Percent"
USED = dict((b, set()) for b in BARS)
def eat_parts(fams, tier, g, raw_factor=None):
    w, inst, over, sn, dur = numbers(fams, tier, g, raw_factor)
    chain = []
    if inst:
        ie = copy.deepcopy(I0)
        ie["StatModifiers"] = dict((b, inst[b]) for b in ("Health", "Mana", "Stamina") if b in inst)
        chain.append({"Type": "ApplyEffect", "EffectId": ie})     # inline (vanilla Food_Candy_Cane does the same) - no file, no id
    vs = {}
    for b in BARS:
        if b in sn:
            k = sn[b][0]
            USED[b].add(k)
            chain.append(chk_id(b, k))
            vs[APPLY_VAR[b]] = {"Interactions": [{"Type": "ApplyEffect", "EffectId": fx_id(b, k), "Duration": bar_dur(b, dur)}]}
    return chain, vs, (w, inst, over, sn, dur)
def set_food(o, chain, vs, iv_src):
    iv = o.setdefault("InteractionVars", {})
    ev = dict(iv.get("Effect") or {})
    ev["Interactions"] = chain
    iv["Effect"] = ev
    for k in list(iv):
        if k.startswith("Skyy_Cook_Apply_"): del iv[k]
    for k, x in vs.items(): iv[k] = x
    iv["Consume_Charge"] = fast_charge(iv_src)

# ---- tooltips
def buff_dur(sn, dur):   # 0.1.9: the dish's "Duration:" = its longest buff (a Strength-only dish shows the 10 min cap)
    return max([bar_dur(b, dur) for b in sn] or [dur])
def fx_bullets(n):
    w, inst, over, sn, dur = n
    out = []
    if "Health" in sn:
        v = sn["Health"][1]
        out.append("• " + W % "Health Regen" + " (%s%% health every 2 s, +%s%% max health)" % (pct_s(v), pct_s(min(v * HP_MAX_PER_PULSE, HP_MAX_CAP))))
    if "Mana" in sn:
        out.append("• " + W % "Mana Regen" + " (%s%% mana every 2 s)" % pct_s(sn["Mana"][1]))
    if "Stamina" in sn:
        v = sn["Stamina"][1]
        out.append("• " + W % "Stamina Boost" + " (+%s%% max stamina, +%s stamina every 0.1 s)" % (pct_s(v), num_s(v * ST_REGEN_PER_PCT)))
    if "Strength" in sn:
        v = sn["Strength"][1]
        sd = bar_dur("Strength", dur)   # 0.1.9: its own time only when the 10 min cap makes it shorter than the dish's Duration
        out.append("• " + W % ("Strength +" + pct_s(v)) + " (%s%% more damage%s)" % (pct_s(v), "" if abs(sd - buff_dur(sn, dur)) < 0.5 else ", for " + mmss(sd)))
    return out
def food_text(fams, n, raw=False):
    w, inst, over, sn, dur = n
    t = W % bars_title(fams) + " (" + ", ".join(FAM_LABEL[f] for f in fams) + ")" + (" - a raw snack." if raw else ".")
    parts = [W % (pct_s(inst[b]) + "%") + " " + b.lower() for b in ("Health", "Mana", "Stamina") if b in inst]
    bl = fx_bullets(n)
    if parts:
        body = "Instantly restores " + (", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]) + (" and grants:" if bl else ".")
    else:   # 0.1.10: a Mushroom-only dish restores no bar - only its Strength buff
        body = "Grants:"
    if bl:
        body += "\\n\\n" + "\\n".join(bl) + "\\n\\nDuration: " + W % mmss(buff_dur(sn, dur))
    return t + "\\n\\n" + body + "\\n\\nEats 25% faster; getting hit never stops you eating."
def grade_head(g):
    if g <= 10:
        h = "Grade %d food - Cooking %d, or sooner with Cooking tree bonuses." % (g, g * 10)
    else:
        h = "Grade %d food - only a Cooking skill tree bonus reaches it." % g
    return h + " Heal and buffs " + W % ("x%.2f" % SF(g)) + " stronger, buffs last " + W % ("x%.2f" % DF(g)) + " longer."
def add_lang(item_id, name, desc):
    for pre in ("items.", "server.items."):
        if name is not None: lang.append("%s%s.name=%s" % (pre, item_id, name))
        lang.append("%s%s.description=%s" % (pre, item_id, desc))

# ---- graded dishes (vanilla + own) and the Grade 0 items
QORDER = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
for q in QORDER: assert q in V_QUAL, "vanilla quality missing: " + q
def grade_quality(g): return "Uncommon" if g <= 2 else ("Rare" if g <= 5 else ("Epic" if g <= 8 else "Legendary"))
ROMAN = {1: "I", 2: "II", 3: "III"}
def pct_s(v): return ("%.1f" % v).rstrip("0").rstrip(".")
def num_s(v): return ("%.3f" % v).rstrip("0").rstrip(".")
def mmss(sec):
    s = int(round(sec)); return "%d:%02d" % (s // 60, s % 60)
DISH_TIER, DISH_NAME, DISH_NUM = {}, {}, {}
lang = []
W = '<color is="#ffffff">%s</color>'
def deep_under(base, top):
    """0.1.7: top's keys over base's, merged field by field like the engine's Parent merge (research/Collections-Spec.md); lists replace"""
    o = copy.deepcopy(base)
    for k, x in top.items():
        o[k] = deep_under(o[k], x) if (isinstance(x, dict) and isinstance(o.get(k), dict)) else copy.deepcopy(x)
    return o
def flat_dish(dish):
    """0.1.7: Hytale 0.7 put Food_Salad_Berry / _Mushroom / _Caesar and Food_Pie_Meat under Parent Food_Pie_Apple. A graded copy never sits
    under a vanilla dish (its Recipe could be inherited - Cooking spec 5): the parent dish's own keys (minus Recipe and names) are merged in
    and the copy keeps Parent Template_Food (so it still gets Consumable, Scale, BlockType Gathering ... exactly like the vanilla dish)."""
    v = rd(V_ITEMS[dish])
    p = v.get("Parent")
    if p != "Template_Food" and p in V_ITEMS:
        pv = rd(V_ITEMS[p])
        if p not in DISHES or pv.get("Parent") != "Template_Food":
            raise SystemExit("self-check 4 (0.1.7): %s's Parent %s is not a graded Template_Food dish" % (dish, p))
        v = deep_under(dict((k, x) for k, x in pv.items() if k not in ("Recipe", "TranslationProperties", "Parent")), v)
        v["Parent"] = "Template_Food"
    return v
FLATTENED = [d for d in DISHES if rd(V_ITEMS[d]).get("Parent") != "Template_Food"] if all(d in V_ITEMS for d in DISHES) else []
OVERRIDES = {}       # vanilla item id -> its Assets.zip path (the override file goes to the same path)
BASE_JSON = {}       # graded dish -> its flat Grade 0 JSON (the source of the graded copies)
for dish in DISHES:
    v = flat_dish(dish)
    sec = (v.get("Interactions") or {}).get("Secondary")
    m = re.match(r"^Root_Secondary_Consume_Food_T([123])$", str(sec))
    if v.get("Parent") != "Template_Food" or not m:
        raise SystemExit("self-check 4: %s is no longer a Template_Food dish with a T1-T3 eat root (%s, %s)" % (dish, v.get("Parent"), sec))
    DISH_TIER[dish] = int(m.group(1))
    DISH_NAME[dish] = VLANG.get("items.%s.name" % dish) or dish
    chain0 = v["InteractionVars"]["Effect"]["Interactions"]
    if not chain0 or chain0[0] != {"Type": "ApplyEffect", "EffectId": "Food_Instant_Heal_T1"} or \
            any(not re.match(r"^(HealthRegen|Meat|FruitVeggie)_TierCheck_T[123]$", str(e)) for e in chain0[1:]):
        raise SystemExit("self-check 4: unexpected eat chain in %s: %s" % (dish, json.dumps(chain0)))
    BASE_JSON[dish] = v
    # Grade 0 = a pack override of the vanilla item itself (Parent / Recipe / model / Quality kept; chain, charge, description key ours)
    ov = rd(V_ITEMS[dish])
    ch, vs, n = eat_parts(DISH_FAMS[dish], DISH_TIER[dish], 0)
    set_food(ov, ch, vs, v["InteractionVars"])
    ov["TranslationProperties"] = dict(ov.get("TranslationProperties") or {}, Description="server.items.Skyy_Cook_%s_G0.description" % dish)
    G_ITEMS[dish] = ov
    OVERRIDES[dish] = V_ITEMS[dish]
    files[V_ITEMS[dish]] = json.dumps(ov, indent=2)
    add_lang("Skyy_Cook_%s_G0" % dish, None, food_text(DISH_FAMS[dish], n))
    DISH_NUM[(dish, 0)] = n
for oid, nm, t, cat, sec, donor, ins in OWN:
    v = flat_dish(donor)
    v.pop("Recipe", None)
    own_look(oid, t, v)                                # 0.1.12: the new dishes' vanilla looks + Quality by tier (no-op for the older ones)
    v["TranslationProperties"] = {"Name": "server.items.%s.name" % oid, "Description": "server.items.%s.description" % oid}
    v.setdefault("Interactions", {})["Secondary"] = "Root_Secondary_Consume_Food_T%d" % t
    DISH_TIER[oid], DISH_NAME[oid] = t, nm
    BASE_JSON[oid] = copy.deepcopy(v)
    o = copy.deepcopy(v)
    o["Recipe"] = OWN_RECIPE[oid]
    ch, vs, n = eat_parts(DISH_FAMS[oid], t, 0)
    set_food(o, ch, vs, v["InteractionVars"])
    G_ITEMS[oid] = o
    files["Server/Item/Items/SkyyCook/Dishes/%s.json" % oid] = json.dumps(o, indent=2)
    add_lang(oid, nm, food_text(DISH_FAMS[oid], n))
    DISH_NUM[(oid, 0)] = n
for dish in GDISHES:
    v = BASE_JSON[dish]
    for g in range(1, GEN_MAX + 1):
        gid = dish_id(dish, g)
        o = copy.deepcopy(v)
        o.pop("Recipe", None)
        o["TranslationProperties"] = {"Name": "server.items.%s.name" % gid, "Description": "server.items.%s.description" % gid}
        vq = v.get("Quality", "Common")
        o["Quality"] = vq if (vq in QORDER and QORDER.index(vq) >= QORDER.index(grade_quality(g))) else grade_quality(g)
        ch, vs, n = eat_parts(DISH_FAMS[dish], DISH_TIER[dish], g)
        set_food(o, ch, vs, v["InteractionVars"])
        G_ITEMS[gid] = o
        files["Server/Item/Items/SkyyCook/%s.json" % gid] = json.dumps(o, indent=2)
        add_lang(gid, "%s (Grade %d)" % (DISH_NAME[dish], g), grade_head(g) + "\\n\\n" + food_text(DISH_FAMS[dish], n))
        DISH_NUM[(dish, g)] = n
# raw snacks: overrides of the vanilla raw items, instant only
for rid, (fam, fac) in sorted(RAW.items()):
    if rid not in V_ITEMS: raise SystemExit("0.1.8: vanilla raw food %s is missing" % rid)
    ov = rd(V_ITEMS[rid])
    if ov.get("Parent") != "Template_Food" or (ov.get("InteractionVars") or {}).get("Effect") != {"Interactions": [{"Type": "ApplyEffect", "EffectId": "Food_Instant_Heal_T1"}]}:
        raise SystemExit("0.1.8: %s is no longer a plain Template_Food snack (Food_Instant_Heal_T1 only): %s" % (rid, json.dumps(ov.get("InteractionVars"))[:300]))
    ch, vs, n = eat_parts([fam], 1, 0, raw_factor=fac)
    assert not vs and len(ch) == 1
    set_food(ov, ch, vs, ov["InteractionVars"])
    ov["TranslationProperties"] = dict(ov.get("TranslationProperties") or {}, Description="server.items.Skyy_Cook_%s_G0.description" % rid)
    G_ITEMS[rid] = ov
    OVERRIDES[rid] = V_ITEMS[rid]
    files[V_ITEMS[rid]] = json.dumps(ov, indent=2)
    add_lang("Skyy_Cook_%s_G0" % rid, None, food_text([fam], n, raw=True))
    DISH_NUM[(rid, 0)] = n

# ---- over-time effects (one file per bar level) and the stacking checks (one per bar level)
FX_ICON = {"Health": "UI/StatusEffects/HealthRegen.png", "Mana": "Icons/ItemsGenerated/Potion_Regen_Mana.png",
           "Stamina": "UI/StatusEffects/Stamina/Small.png", "Strength": "Icons/ItemsGenerated/Food_Kebab_Mushroom.png"}
def fx_json(bar, v):
    if bar == "Health":
        return {"StatModifiers": {"Health": v}, "ValueType": "Percent",
                "RawStatModifiers": {"Health": [{"Amount": r4(1.0 + min(v * HP_MAX_PER_PULSE, HP_MAX_CAP) / 100.0), "CalculationType": "Multiplicative", "Target": "Max"}]},
                "OverlapBehavior": "Overwrite", "Duration": BUFF_BASE_S, "DamageCalculatorCooldown": 2, "StatusEffectIcon": FX_ICON[bar]}
    if bar == "Mana":
        return {"StatModifiers": {"Mana": v}, "ValueType": "Percent", "OverlapBehavior": "Overwrite", "Duration": BUFF_BASE_S,
                "DamageCalculatorCooldown": 2, "StatusEffectIcon": FX_ICON[bar]}
    if bar == "Stamina":
        return {"StatModifiers": {"Stamina": r4(v * ST_REGEN_PER_PCT)},
                "RawStatModifiers": {"Stamina": [{"Amount": r4(1.0 + v / 100.0), "CalculationType": "Multiplicative", "Target": "Max"}]},
                "OverlapBehavior": "Overwrite", "Duration": BUFF_BASE_S, "DamageCalculatorCooldown": 0.1, "StatusEffectIcon": FX_ICON[bar]}
    o = {"OverlapBehavior": "Overwrite", "Duration": BUFF_BASE_S, "Debuff": False, "StatusEffectIcon": FX_ICON[bar]}
    if FOOD_STRENGTH_EFFECT:
        o["OutgoingDamage"] = dict((c, [{"CalculationType": "Percent", "Amount": r4(v / 100.0)}]) for c in ("Physical", "Projectile", "Elemental"))
    return o
_AR_NOW, ALLROUND = ALLROUND, ALLROUND_0_1_9          # 0.1.10: the 0.1.9 levels (bar_weights reads the module-level ALLROUND)
USED_0_1_9 = dict((b, set()) for b in BARS)
for (_d, _g) in list(DISH_NUM):
    if _d in RAW or _d in NEW_IDS: continue            # 0.1.12: the new dishes never had an all-round share
    for _b, (_k, _v) in numbers(DISH_FAMS[_d], DISH_TIER[_d], _g)[3].items(): USED_0_1_9[_b].add(_k)
ALLROUND = _AR_NOW
USED_NEW = dict((b, set()) for b in BARS)              # 0.1.12: the ladder steps the new dishes apply
for (_d, _g) in list(DISH_NUM):
    if _d in NEW_IDS:
        for _b, (_k, _v) in DISH_NUM[(_d, _g)][3].items(): USED_NEW[_b].add(_k)
LEGACY_FX = dict((b, sorted(USED_0_1_9[b] - USED[b])) for b in BARS)
assert all(USED[b] - USED_NEW[b] <= USED_0_1_9[b] for b in BARS) and not LEGACY_FX["Strength"], "0.1.10: the families' own levels are a subset of 0.1.9's"
print("0.1.12 new ladder steps (only the new dishes need them): " + ", ".join("%s %s" % (b, sorted(USED[b] - USED_0_1_9[b])) for b in BARS))
for b in BARS: USED[b] |= USED_0_1_9[b]
print("0.1.10 legacy all-round levels kept (no item applies them; running 0.1.9 buffs run out): " + ", ".join("%s %d" % (b, len(LEGACY_FX[b])) for b in BARS))
max_clears = 0
for b in BARS:
    ks = sorted(USED[b])
    for k in ks:
        e = fx_json(b, float("%.4f" % (LADDER_L0[b] * LADDER_R ** k)))
        G_EFFECTS[fx_id(b, k)] = e
        files["Server/Entity/Effects/SkyyCook/%s.json" % fx_id(b, k)] = json.dumps(e, indent=2)
    for k in ks:
        above = [fx_id(b, x) for x in ks if x > k]
        below = [fx_id(b, x) for x in ks if x < k]
        _ext = [x for x in VANILLA_CLEAR.get(b, []) if x in V_EFFECTS] + [x for x in LEGACY_EFFECTS if any(x.startswith("Skyy_Cook_%s_Buff_" % f) for f in LEGACY_CLEAR.get(b, []))]
        serial = {"Type": "Serial", "Interactions": [{"Type": "ClearEntityEffect", "EntityEffectId": x} for x in below + _ext] +
                  [{"Type": "Replace", "Var": APPLY_VAR[b], "DefaultOk": True,
                    "DefaultValue": {"Interactions": [{"Type": "ApplyEffect", "EffectId": fx_id(b, k), "Duration": BUFF_BASE_S}]}}]}
        max_clears = max(max_clears, len(below))
        node = serial if not above else {"Type": "EffectCondition", "EntityEffectIds": above, "Match": "None", "Next": serial,
                                         "Failed": {"Type": "Simple", "RunTime": 0}}
        G_INTER[chk_id(b, k)] = node
        files["Server/Item/Interactions/SkyyCook/%s.json" % chk_id(b, k)] = json.dumps(node, indent=2)

# ---- Cooking Bench recipes for the 3 Campfire dishes (vanilla Variant-recipe shape, Ingredient_Life_Essence_Wheat.json) - unchanged
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
# BUILD-TIME SELF-CHECK: every generated item / interaction references ids that exist (0.1.8: + inline instant effects, Replace vars,
# vanilla overrides, own dishes)
# =====================================================================================================================
errs = []
def need(kind, i, where):
    pools = {"effect": (V_EFFECTS, G_EFFECTS), "inter": (V_INTER, G_INTER), "root": (V_ROOTS, {}), "item": (V_ITEMS, G_ITEMS)}[kind]
    if not isinstance(i, str) or (i not in pools[0] and i not in pools[1]):
        errs.append("%s: unknown %s id %r" % (where, kind, i))
def need_common(path, where):
    if path and "Common/" + path not in V_COMMON: errs.append("%s: missing file Common/%s" % (where, path))
def walk_inter(node, where):
    """an interaction reference: a string id or an inline interaction object (vanilla item / interaction JSON shape)"""
    if isinstance(node, str):
        need("inter", node, where); return
    if not isinstance(node, dict):
        errs.append("%s: unexpected interaction node %r" % (where, node)); return
    for k, v in node.items():
        if k == "Parent": need("inter", v, where)
        elif k == "EffectId":
            if isinstance(v, dict):   # 0.1.8: an inline instant effect (vanilla Food_Candy_Cane's shape)
                if sorted(v) != sorted(I0) or any(s not in ("Health", "Mana", "Stamina") for s in v["StatModifiers"]): errs.append("%s: bad inline effect %r" % (where, v))
            else: need("effect", v, where)
        elif k == "EntityEffectId": need("effect", v, where)
        elif k == "EntityEffectIds":
            for x in v: need("effect", x, where)
        elif k == "Interactions":
            for x in v: walk_inter(x, where)
        elif k == "DefaultValue" and isinstance(v, dict) and str(node.get("Var", "")).startswith("Skyy_Cook_Apply_"):   # our Replace (vanilla ones name placeholder vars)
            for x in v.get("Interactions", []): walk_inter(x, where)
        elif k in ("Next", "Failed"):
            if isinstance(v, str): need("inter", v, where)
            elif isinstance(v, dict) and ("Type" in v or "Parent" in v): walk_inter(v, where)
            elif isinstance(v, dict):
                for tk, tv in v.items(): walk_inter(tv, where)   # Charging: {"2.5": {...}}
for cid, node in G_INTER.items():
    walk_inter(node, "interaction " + cid)
for eid, e in G_EFFECTS.items():
    need_common(e.get("StatusEffectIcon"), "effect " + eid)
LANG_KEYS = set(l.split("=", 1)[0] for l in lang)
def lang_ok(iid, desc_only=False):
    for suf in (("description",) if desc_only else ("name", "description")):
        for pre in ("items.", "server.items."):
            if "%s%s.%s" % (pre, iid, suf) not in LANG_KEYS: errs.append("no lang line %s%s.%s" % (pre, iid, suf))
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
        lang_ok(iid)
    elif iid in OVERRIDES:
        v0 = rd(OVERRIDES[iid])
        a, b = copy.deepcopy(node), copy.deepcopy(v0)
        for x in (a, b):
            x.pop("TranslationProperties", None)
            for k in [k for k in x.get("InteractionVars", {}) if k in ("Effect", "Consume_Charge") or k.startswith("Skyy_Cook_Apply_")]: del x["InteractionVars"][k]
        if a != b or dict(node["TranslationProperties"], Description=None) != dict(v0.get("TranslationProperties") or {}, Description=None):
            errs.append("override %s changes more than InteractionVars Effect / Consume_Charge / Skyy_Cook_Apply_* and the description key" % iid)
        lang_ok("Skyy_Cook_%s_G0" % iid, desc_only=True)
    elif iid in OWN_IDS:
        rc = node["Recipe"]
        if rc["Output"][0]["ItemId"] != iid or rc["Output"][1:] != own_returns(inputs_of(rc)): errs.append("own dish %s: its recipe must output itself (+ its containers)" % iid)
        for inp in rc["Input"]:
            if "ItemId" in inp and inp["ItemId"].startswith("*"):   # 0.1.12: '*<Item>_State_<State>' (vanilla Ingredient_Dough's form)
                _m = re.match(r"^\*(\w+?)_State_(\w+)$", inp["ItemId"])
                if not _m or _m.group(1) not in V_ITEMS or _m.group(2) not in (rd(V_ITEMS[_m.group(1)]).get("State") or {}):
                    errs.append("recipe %s: unknown state input %r" % (iid, inp["ItemId"]))
            elif "ItemId" in inp: need("item", inp["ItemId"], "recipe " + iid)
            elif inp.get("ResourceTypeId") not in V_RTYPES: errs.append("recipe %s: unknown resource type %r" % (iid, inp.get("ResourceTypeId")))
        for br in rc["BenchRequirement"]:
            if br["Id"] != "Cookingbench" or any(c not in BENCH_CATS for c in br.get("Categories", [])): errs.append("recipe %s: bad bench %r" % (iid, br))
        lang_ok(iid)
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
        ok = (i.startswith("Skyy_Cook_") and i not in van) or (kind == "item" and i in OVERRIDES and i in van) or \
             (kind == "item" and i in OWN_IDS and i.startswith("Food_Skyy_") and i not in van)
        if not ok: errs.append("generated %s id %s collides with vanilla or lacks the Skyy_Cook_ / Food_Skyy_ prefix (self-check 5)" % (kind, i))
# every food item eats through our fast charge, every check pairs with exactly the var its items carry
for iid, node in G_ITEMS.items():
    if iid.startswith("Skyy_Cook_Recipe_"): continue
    iv = node["InteractionVars"]
    if any(not str(e.get("Parent", "")).endswith("_Fast") for e in iv["Consume_Charge"]["Interactions"]):
        errs.append("%s does not eat through the fast charge" % iid)
    for x in iv["Effect"]["Interactions"]:
        if isinstance(x, str):
            b, k = re.match(r"^Skyy_Cook_Chk_(Health|Mana|Stamina|Strength)_(\d+)$", x).groups()
            if iv.get(APPLY_VAR[b]) is None or iv[APPLY_VAR[b]]["Interactions"][0]["EffectId"] != fx_id(b, int(k)):
                errs.append("%s: %s without the matching %s var" % (iid, x, APPLY_VAR[b]))
if errs:
    raise SystemExit("ASSET SELF-CHECK FAILED (%d):\n  " % len(errs) + "\n  ".join(errs[:60]))
N_FX = sum(len(USED[b]) for b in BARS)
N_DISH = len([i for i in G_ITEMS if i.startswith("Skyy_Cook_Food_")])
N_VAR = len(VARIANTS)
assert len(LEGACY_EFFECTS) == 12 * GEN_MAX and len(G_EFFECTS) == len(LEGACY_EFFECTS) + N_FX and len(G_INTER) == N_FX + len(FAST)
assert N_DISH == len(GDISHES) * GEN_MAX and len(OVERRIDES) == len(DISHES) + len(RAW) and N_VAR == 3
# monotone: a higher Grade of the same dish is never weaker on any bar (instant or over time) and lasts at least as long
for dish in GDISHES:
    for g in range(1, GEN_MAX + 1):
        a, b = DISH_NUM[(dish, g - 1)], DISH_NUM[(dish, g)]
        if any(b[1][x] < a[1][x] for x in a[1]) or any(b[3][x][0] <= a[3][x][0] and b[2][x] < OVER_CAP[x] for x in a[3]) or b[4] < a[4]:
            raise SystemExit("0.1.8: %s Grade %d is not stronger than Grade %d: %s / %s" % (dish, g, g - 1, b, a))
# snapping stays within half a ladder step
for (dish, g), n in DISH_NUM.items():
    for b, (k, v) in n[3].items():
        if abs(math.log(v / n[2][b])) > math.log(LADDER_R) / 2 + 1e-9: raise SystemExit("0.1.8: %s G%d %s snapped too far" % (dish, g, b))
# 0.1.7 self-check kept: no generated file names an effect Hytale 0.7 removed
_REMOVED_07 = ["Food_Instant_Heal_T2", "Food_Instant_Heal_T3", "Food_Instant_Heal_Bread"]
for _n, _t in files.items():
    for _r in _REMOVED_07:
        if _r in _t: raise SystemExit("self-check 0.1.7: %s still names the removed 0.7 effect %s" % (_n, _r))
for dish in DISHES:
    for g in range(1, GEN_MAX + 1):
        _o = G_ITEMS[dish_id(dish, g)]
        if _o.get("Parent") != "Template_Food" or "Recipe" in _o:
            raise SystemExit("self-check 0.1.7: %s G%d Parent %s / Recipe" % (dish, g, _o.get("Parent")))
for dish in FLATTENED:
    _pv = rd(V_ITEMS[rd(V_ITEMS[dish])["Parent"]])
    _miss = [k for k in _pv if k not in ("Recipe", "TranslationProperties", "Parent") and k not in G_ITEMS[dish_id(dish, 1)]]
    if _miss: raise SystemExit("self-check 0.1.7: flattened %s G1 lacks its parent dish's keys %s" % (dish, _miss))
# =====================================================================================================================
# 0.1.11 SUPPLIES (round FP1, research/Flask-Pouch-Spec.md 1 + 3.1 + 3.2): the Potion Flask + Food Pouch assets, generated HERE from this
# build's own item JSON (G_ITEMS - spec 3.1 "one writer"). Mechanics = the FP0 probe's (SkyyFlaskProbe 0.1.0, proven in game 2026-10-17).
# =====================================================================================================================
import skyyui as SUI
SUI.verify()
SUP_FPRE, SUP_PPRE = "Skyy_Flask_", "Skyy_Food_Pouch_"
SUP_FEMPTY, SUP_PEMPTY = SUP_FPRE + "Empty", SUP_PPRE + "Empty"
SUP_MARK, SUP_MARK_E = "Skyy_Supply_Used", "Skyy_Supply_Empty"
SUP_PAGE = "SkyySupplies"
SUP_OPEN = "Skyy_Supply_Open"
SUP_ROOT_POT, SUP_COND_POT = "Skyy_Supply_Root_Potion_Health", "Skyy_Supply_Cond_Potion_Health"
SUP_ROOT_EMPTY, SUP_COND_EMPTY = "Skyy_Supply_Root_Empty", "Skyy_Supply_Cond_Empty"
SUP_V_ROOT_POT, SUP_V_COND_POT, SUP_V_CHARGE_POT = "Root_Secondary_Consume_Potion_Health", "Condition_Consume_Potion_Health", "Consume_Charge_Potion_Fast"
SUP_ITEM_DIR = "Server/Item/Items/SkyyCook/Supplies"
SUP_INT_DIR = "Server/Item/Interactions/SkyyCook/Supplies"
SUP_ROOT_DIR = "Server/Item/RootInteractions/SkyyCook/Supplies"
SUP_FX_DIR = "Server/Entity/Effects/SkyyCook/Supplies"
SUP_KEY = {0: "Skyy_Flask", 1: "Skyy_Food_Pouch"}
SUP_LOOK = {0: {"Model": "Items/Consumables/Potions/Potion_Large.blockymodel", "Texture": "Items/Consumables/Potions/Potion_Textures/Red.png",
                "Icon": "Icons/ItemsGenerated/Potion_Health_Large.png"},
            1: {"Model": "Items/Consumables/Food/Food_Bag.blockymodel", "Texture": "Items/Consumables/Food/Food_Bag_Texture.png",
                "Icon": "Icons/ItemsGenerated/Food_Bread.png"}}
SUP_COPY_KEYS = ("PlayerAnimationsId", "IconProperties", "InteractionConfig", "Consumable")   # spec 3.1: Quality / model / recipe are the item's own
SUP_FILES = {}
for _k in SUP_LOOK:
    for _f in ("Model", "Texture", "Icon"):
        assert "Common/" + SUP_LOOK[_k][_f] in V_COMMON, "0.1.11: the shared look file %s is not in Assets.zip" % SUP_LOOK[_k][_f]


def sup_put(path, obj):
    if path in files or path in SUP_FILES:
        raise SystemExit("0.1.11: duplicate asset path %s" % path)
    files[path] = SUP_FILES[path] = json.dumps(obj, indent=2)


_SUP_V = {}


def sup_raw(iid):
    if iid in G_ITEMS:
        return copy.deepcopy(G_ITEMS[iid])
    if iid not in V_ITEMS:
        raise SystemExit("0.1.11: item %s is neither in this build nor in Assets.zip" % iid)
    if iid not in _SUP_V:
        _SUP_V[iid] = rd(V_ITEMS[iid])
    return copy.deepcopy(_SUP_V[iid])


SUP_MERGE = ("Interactions", "InteractionVars", "TranslationProperties")


def sup_flat(iid, depth=0):
    """the EFFECTIVE item (this build's file wins over Assets.zip) resolved through its Parent chain (the probe's flat())"""
    if depth > 8:
        raise SystemExit("0.1.11: Parent chain too deep at %s" % iid)
    d = sup_raw(iid)
    p = d.pop("Parent", None)
    if not p:
        return d
    base = sup_flat(p, depth + 1)
    for k, v in d.items():
        if k in SUP_MERGE and isinstance(v, dict) and isinstance(base.get(k), dict):
            m = dict(base[k])
            m.update(v)
            base[k] = m
        else:
            base[k] = v
    return base


def sup_inter(i):
    if i in G_INTER:
        return copy.deepcopy(G_INTER[i])
    if i in V_INTER:
        return rd(V_INTER[i])
    raise SystemExit("0.1.11: interaction %s is missing" % i)


SUP_CHARGES = {}       # source charge id -> our copy
SUP_CHARGE_T = {}      # our copy -> seconds


def sup_swap(o, out):
    """every {"Type": "ModifyInventory", "AdjustHeldItemQuantity": -1, "Next": X} -> {"Type": "ApplyEffect", "EffectId": MARK, "Next": X}"""
    if isinstance(o, dict):
        if o.get("Type") == "ModifyInventory":
            if o.get("AdjustHeldItemQuantity") != -1 or sorted(o) != ["AdjustHeldItemQuantity", "Next", "Type"]:
                raise SystemExit("0.1.11: unexpected ModifyInventory shape %s" % json.dumps(o)[:300])
            out[0] += 1
            return {"Type": "ApplyEffect", "EffectId": SUP_MARK, "Next": sup_swap(o["Next"], out)}
        return dict((k, sup_swap(v, out)) for k, v in o.items())
    if isinstance(o, list):
        return [sup_swap(v, out) for v in o]
    return o


def sup_charging(o):
    if o.get("Type") == "Charging":
        return o
    cs = [x for x in o.get("Interactions", []) if isinstance(x, dict) and x.get("Type") == "Charging"]
    if o.get("Type") != "Serial" or len(cs) != 1:
        raise SystemExit("0.1.11: charge shape changed: %s" % json.dumps(o)[:300])
    return cs[0]


def sup_charge(src_id):
    if src_id in SUP_CHARGES:
        return SUP_CHARGES[src_id]
    if src_id == SUP_V_CHARGE_POT:
        our = "Skyy_Supply_Charge_Potion_Fast"
    else:
        m = re.match(r"^Skyy_Cook_Consume_Charge_Food_T([123])_Inner_Fast$", src_id)
        if not m:
            raise SystemExit("0.1.11: a food eats through %s, not Cooking's fast charge" % src_id)
        our = "Skyy_Supply_Charge_Food_T%s_Inner" % m.group(1)
    v = sup_inter(src_id)
    if "Parent" in v:
        raise SystemExit("0.1.11: charge %s has a Parent" % src_id)
    ch = sup_charging(v)
    nx = ch.get("Next") or {}
    if ch.get("FailOnDamage") is not False or len(nx) != 1:
        raise SystemExit("0.1.11: %s is no longer a one-step Charging with FailOnDamage false" % src_id)
    n = [0]
    o = sup_swap(copy.deepcopy(v), n)
    if n[0] != 1:
        raise SystemExit("0.1.11: %s: expected exactly one ModifyInventory step, found %d" % (src_id, n[0]))
    sup_put("%s/%s.json" % (SUP_INT_DIR, our), o)
    SUP_CHARGES[src_id] = our
    SUP_CHARGE_T[our] = float(list(nx)[0])
    return our


# ---- the crouch branch (page) and the markers
sup_put("%s/%s.json" % (SUP_INT_DIR, SUP_OPEN), {"Type": "Condition", "Crouching": True, "Next": {"Type": "OpenCustomUI", "Page": {"Id": SUP_PAGE}},
                                                  "Failed": {"Type": "Simple"}})
sup_put("%s/%s.json" % (SUP_FX_DIR, SUP_MARK), {"Duration": 0.5, "OverlapBehavior": "Overwrite"})
sup_put("%s/%s.json" % (SUP_FX_DIR, SUP_MARK_E), {"Duration": 0.5, "OverlapBehavior": "Overwrite"})
# ---- potions: root -> condition (cooldown kept, Failed = the page) -> our charge
_vrp, _vcp = rd(V_ROOTS[SUP_V_ROOT_POT]), rd(V_INTER[SUP_V_COND_POT])
if _vrp != {"RequireNewClick": True, "Interactions": [SUP_V_COND_POT]}:
    raise SystemExit("0.1.11: %s changed: %s" % (SUP_V_ROOT_POT, _vrp))
if _vcp.get("Type") != "Condition" or _vcp.get("Crouching") is not False or _vcp.get("Failed") != "Block_Secondary" or \
        _vcp["Next"].get("Type") != "CooldownCondition" or _vcp["Next"].get("Id") != "Potion_Consume_Health" or _vcp["Next"].get("Next") != SUP_V_CHARGE_POT:
    raise SystemExit("0.1.11: %s changed: %s" % (SUP_V_COND_POT, json.dumps(_vcp)))
_cp = copy.deepcopy(_vcp)
_cp["Next"]["Next"] = sup_charge(SUP_V_CHARGE_POT)
_cp["Failed"] = SUP_OPEN
sup_put("%s/%s.json" % (SUP_INT_DIR, SUP_COND_POT), _cp)
sup_put("%s/%s.json" % (SUP_ROOT_DIR, SUP_ROOT_POT), {"RequireNewClick": True, "Interactions": [SUP_COND_POT]})
# ---- food roots: the vanilla T1-T3 roots / conditions with Failed = the page (Next = the vanilla charge, which reads the HELD item's
# Consume_Charge var = our marker copy)
SUP_FOOD_ROOT = {}
for _t in (1, 2, 3):
    _vr, _vc = "Root_Secondary_Consume_Food_T%d" % _t, "Condition_Consume_Food_T%d" % _t
    _r, _c = rd(V_ROOTS[_vr]), rd(V_INTER[_vc])
    if _r != {"RequireNewClick": True, "Interactions": [_vc]} or _c.get("Type") != "Condition" or _c.get("Crouching") is not False or \
            _c.get("Failed") != "Block_Secondary" or _c.get("Next") != "Consume_Charge_Food_T%d" % _t:
        raise SystemExit("0.1.11: the vanilla T%d food root / condition changed: %s / %s" % (_t, _r, _c))
    _c = copy.deepcopy(_c)
    _c["Failed"] = SUP_OPEN
    sup_put("%s/Skyy_Supply_Cond_Food_T%d.json" % (SUP_INT_DIR, _t), _c)
    sup_put("%s/Skyy_Supply_Root_Food_T%d.json" % (SUP_ROOT_DIR, _t), {"RequireNewClick": True, "Interactions": ["Skyy_Supply_Cond_Food_T%d" % _t]})
    SUP_FOOD_ROOT[_vr] = "Skyy_Supply_Root_Food_T%d" % _t
# ---- the Empty items: right click = the empty marker (the popup), crouch = the page
sup_put("%s/%s.json" % (SUP_INT_DIR, SUP_COND_EMPTY), {"Type": "Condition", "Crouching": False, "Next": {"Type": "ApplyEffect", "EffectId": SUP_MARK_E},
                                                        "Failed": SUP_OPEN})
sup_put("%s/%s.json" % (SUP_ROOT_DIR, SUP_ROOT_EMPTY), {"RequireNewClick": True, "Interactions": [SUP_COND_EMPTY]})


def sup_base(kind):
    look = SUP_LOOK[kind]
    return {"TranslationProperties": {"Name": "server.items.%s.name" % SUP_KEY[kind], "Description": "server.items.%s.description" % SUP_KEY[kind]},
            "Icon": look["Icon"], "Model": look["Model"], "Texture": look["Texture"], "MaxStack": 1, "DropOnDeath": False}


def sup_loaded(kind, src, f):
    d = sup_base(kind)
    for k in SUP_COPY_KEYS:
        if k in f:
            d[k] = copy.deepcopy(f[k])
    iv = copy.deepcopy(f.get("InteractionVars") or {})
    if kind == 0:
        d["Interactions"] = {"Secondary": SUP_ROOT_POT}
        ch = SUP_CHARGES[SUP_V_CHARGE_POT]
    else:
        sec = f["Interactions"]["Secondary"]
        d["Interactions"] = {"Secondary": SUP_FOOD_ROOT[sec]}
        cc = iv.get("Consume_Charge")
        if not cc or not cc.get("Interactions"):
            raise SystemExit("0.1.11: food %s has no Consume_Charge var" % src)
        ch = None
        for e in cc["Interactions"]:
            if not isinstance(e, dict) or not e.get("Parent"):
                raise SystemExit("0.1.11: food %s: unexpected Consume_Charge entry %s" % (src, json.dumps(e)[:200]))
            e["Parent"] = sup_charge(e["Parent"])
            ch = e["Parent"]
    d["InteractionVars"] = iv
    return d, ch


def sup_fx_ids(o, out):
    if isinstance(o, dict):
        if o.get("Type") == "ApplyEffect" and isinstance(o.get("EffectId"), str):
            out.append(o["EffectId"])
        for v in o.values():
            sup_fx_ids(v, out)
    elif isinstance(o, list):
        for v in o:
            sup_fx_ids(v, out)


def sup_heal(f):
    """(instant %, regen % in total) of a healing potion, from its effect assets"""
    ids, inst, regen = [], 0.0, 0.0
    sup_fx_ids(f["InteractionVars"]["Effect"], ids)
    for e in ids:
        d = rd(V_EFFECTS[e])
        h = float((d.get("StatModifiers") or {}).get("Health", 0))
        if float(d.get("Duration", 0)) <= 0.5:
            inst += h
        else:
            cd = float(d.get("DamageCalculatorCooldown") or 0)
            regen += h * (max(1, int(float(d["Duration"]) / cd)) if cd > 0 else 1)
    return inst, regen


SUP_LOADED = {0: [], 1: []}     # kind -> [(source id, loaded id, charge id)], worst first
SUP_VARS = {}
lang_sup = []
# ---- the flask: every vanilla healing potion, worst first
_pots = sorted(i for i in V_ITEMS if (sup_flat(i).get("Interactions") or {}).get("Secondary") == SUP_V_ROOT_POT and not i.endswith("_Template"))
if len(_pots) != 5:
    raise SystemExit("0.1.11: expected 5 healing potions with %s, found %s" % (SUP_V_ROOT_POT, _pots))
SUP_F = []
for _s in _pots:
    _f = sup_flat(_s)
    _i, _r = sup_heal(_f)
    if _i <= 0 or _r <= 0:
        raise SystemExit("0.1.11: %s heals nothing? (%s, %s)" % (_s, _i, _r))
    _nm = VLANG.get("items.%s.name" % _s) or _s
    SUP_F.append({"src": _s, "total": _i + _r, "lv": int(_f.get("ItemLevel") or 0), "name": _nm, "q": _f.get("Quality", "Common"),
                  "desc": "Heals %s%% of your health: %s%% at once + %s%% over 5 s. Shares the potion cooldown." % (pct_s(_i + _r), pct_s(_i), pct_s(_r))})
SUP_F.sort(key=lambda e: (e["total"], e["lv"], e["name"]))
assert SUP_F[0]["src"] == "Potion_Health_Lesser", ("0.1.11: Lesser must come first", [e["src"] for e in SUP_F])
for _e in SUP_F:
    _f = sup_flat(_e["src"])
    _d, _ch = sup_loaded(0, _e["src"], _f)
    _lid = SUP_FPRE + "V_" + _e["src"]
    sup_put("%s/%s.json" % (SUP_ITEM_DIR, _lid), _d)
    SUP_LOADED[0].append((_e["src"], _lid, _ch))
    SUP_VARS[_lid] = _f.get("InteractionVars") or {}
# ---- the pouch: every food this build ships (never a Skyy_Cook_Recipe_* - FP0 finding 3), worst first across ALL food
SUP_P = []
for _s in sorted(G_ITEMS):
    if _s.startswith("Skyy_Cook_Recipe_"):
        continue
    _f = sup_flat(_s)
    if not re.match(r"^Root_Secondary_Consume_Food_T[123]$", str((_f.get("Interactions") or {}).get("Secondary"))):
        continue
    if _s in RAW:
        _dish, _g, _raw = _s, 0, True
    elif _s in DISHES or _s in OWN_IDS:
        _dish, _g, _raw = _s, 0, False
    else:
        _m = re.match(r"^Skyy_Cook_(.+)_G(\d+)$", _s)
        if not _m:
            raise SystemExit("0.1.11: food item %s is not a dish / graded dish / raw snack" % _s)
        _dish, _g, _raw = _m.group(1), int(_m.group(2)), False
    _n = DISH_NUM[(_dish, _g)]
    _val = sum(_n[1].values()) + sum(_n[2].values())
    if _raw:
        _nm = VLANG.get("items.%s.name" % _s) or _s
        _ds = "Raw snack - " + bars_title([RAW[_s][0]])
    else:
        _nm = DISH_NAME[_dish] + ((" (Grade %d)" % _g) if _g else "")
        _ds = bars_title(DISH_FAMS[_dish]) + (" - Grade %d" % _g if _g else "")
    _inst = ", ".join("%s%% %s" % (pct_s(_n[1][b]), b.lower()) for b in ("Health", "Mana", "Stamina") if b in _n[1])
    _ds += (" - restores " + _inst + " at once" if _inst else "") + (" + buffs for " + mmss(buff_dur(_n[3], _n[4])) if _n[3] else "")
    SUP_P.append({"src": _s, "g": _g, "raw": _raw, "val": _val, "name": _nm, "q": _f.get("Quality", "Common"), "desc": _ds})
SUP_P.sort(key=lambda e: (e["g"], 0 if e["raw"] else 1, e["val"], e["name"]))
if len(SUP_P) != len(DISHES) + len(RAW) + len(OWN_IDS) + len(GDISHES) * GEN_MAX:
    raise SystemExit("0.1.11: %d pouch sources, expected %d" % (len(SUP_P), len(DISHES) + len(RAW) + len(OWN_IDS) + len(GDISHES) * GEN_MAX))
assert SUP_P[0]["raw"] and all(e["g"] == 0 for e in SUP_P[:len(RAW) + len(DISHES) + len(OWN_IDS)]), "0.1.11: raw snacks, then Grade 0, first"
for _e in SUP_P:
    _f = sup_flat(_e["src"])
    _d, _ch = sup_loaded(1, _e["src"], _f)
    _lid = SUP_PPRE + "V_" + _e["src"]
    sup_put("%s/%s.json" % (SUP_ITEM_DIR, _lid), _d)
    SUP_LOADED[1].append((_e["src"], _lid, _ch))
    SUP_VARS[_lid] = _f.get("InteractionVars") or {}
for _k in (0, 1):
    _d = sup_base(_k)
    _d["Interactions"] = {"Secondary": SUP_ROOT_EMPTY}
    sup_put("%s/%s.json" % (SUP_ITEM_DIR, SUP_FEMPTY if _k == 0 else SUP_PEMPTY), _d)
for _pre in ("items.", "server.items."):
    lang_sup.append("%s%s.name=Potion Flask" % (_pre, SUP_KEY[0]))
    lang_sup.append("%s%s.description=Holds your healing potions - they go in by themselves. Right click: drink the weakest first. Crouch + right click: open it (Storage > Supplies, /flask)." % (_pre, SUP_KEY[0]))
    lang_sup.append("%s%s.name=Food Pouch" % (_pre, SUP_KEY[1]))
    lang_sup.append("%s%s.description=Holds your cooked food - it goes in by itself. Right click: eat the weakest first. Crouch + right click: open it (Storage > Supplies, /pouch)." % (_pre, SUP_KEY[1]))
for _l in lang_sup:
    if _l.split("=", 1)[0] in LANG_KEYS:
        raise SystemExit("0.1.11: lang key %s exists already" % _l.split("=", 1)[0])
lang.extend(lang_sup)
# ---- self-checks (the probe's)
for _p in SUP_FILES:
    if _p in V_COMMON or _p in set(V_ITEMS.values()) | set(V_INTER.values()) | set(V_ROOTS.values()) | set(V_EFFECTS.values()):
        raise SystemExit("0.1.11: asset path %s overrides Assets.zip" % _p)
_ours = dict((p.rsplit("/", 1)[1][:-5], p) for p in SUP_FILES)
for _i in _ours:
    if _i in V_ITEMS or _i in G_ITEMS or _i in V_INTER or _i in G_INTER or _i in V_ROOTS or _i in V_EFFECTS or _i in G_EFFECTS or _i.startswith("Skyy_Probe_"):
        raise SystemExit("0.1.11: id %s clashes with a vanilla / Cooking / probe id" % _i)
_SUP_KI = set(V_INTER) | set(G_INTER) | set(V_ROOTS) | set(i for i, p in _ours.items() if p.startswith((SUP_INT_DIR, SUP_ROOT_DIR)))
_SUP_KF = set(V_EFFECTS) | set(G_EFFECTS) | {SUP_MARK, SUP_MARK_E}
_sup_miss = set()


def sup_refs(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("PlayerAnimationsId", "DefaultValue"):     # an animation-set Parent / a vanilla Replace fallback (unchecked, as vanilla)
                continue
            if k in ("Parent", "Next", "Failed", "Secondary", "Primary") and isinstance(v, str):
                if v not in _SUP_KI:
                    _sup_miss.add(("interaction", v))
            elif k == "Next" and isinstance(v, dict) and v and all(re.match(r"^[0-9.]+$", x) for x in v):
                for x in v.values():
                    if isinstance(x, str) and x not in _SUP_KI:
                        _sup_miss.add(("interaction", x))
                    sup_refs(x)
                continue
            elif k == "Interactions" and isinstance(v, list):
                for x in v:
                    if isinstance(x, str) and x not in _SUP_KI:
                        _sup_miss.add(("interaction", x))
            elif k in ("EffectId", "EntityEffectId") and isinstance(v, str):
                if v not in _SUP_KF:
                    _sup_miss.add(("effect", v))
            elif k == "EntityEffectIds" and isinstance(v, list):
                for x in v:
                    if x not in _SUP_KF:
                        _sup_miss.add(("effect", x))
            if isinstance(v, (dict, list)):
                sup_refs(v)
    elif isinstance(o, list):
        for x in o:
            sup_refs(x)


for _p, _t in SUP_FILES.items():
    sup_refs(json.loads(_t))
if _sup_miss:
    raise SystemExit("0.1.11: referenced ids that exist nowhere: %s" % sorted(_sup_miss)[:20])
for _k in (0, 1):
    for _s, _lid, _ch in SUP_LOADED[_k]:
        _o = json.loads(SUP_FILES["%s/%s.json" % (SUP_ITEM_DIR, _lid)])
        _w = copy.deepcopy(SUP_VARS[_lid])
        if _k == 1:
            for _e in _w["Consume_Charge"]["Interactions"]:
                _e["Parent"] = SUP_CHARGES[_e["Parent"]]
        if json.dumps(_o["InteractionVars"], sort_keys=True) != json.dumps(_w, sort_keys=True):
            raise SystemExit("0.1.11: %s vars differ from %s beyond the charge" % (_lid, _s))
        if any(x in _o for x in ("BlockType", "Recipe", "Tags", "Categories", "Quality")) or _o["MaxStack"] != 1 or _o["DropOnDeath"] is not False:
            raise SystemExit("0.1.11: %s must have no BlockType / Recipe / Tags / Quality, MaxStack 1, DropOnDeath false (FP0 finding 2)" % _lid)
for _our in SUP_CHARGES.values():
    _t = SUP_FILES["%s/%s.json" % (SUP_INT_DIR, _our)]
    if "ModifyInventory" in _t or SUP_MARK not in _t:
        raise SystemExit("0.1.11: %s still removes the held item / has no marker" % _our)
assert json.loads(SUP_FILES["%s/%s.json" % (SUP_INT_DIR, SUP_COND_POT)])["Next"]["Id"] == "Potion_Consume_Health", "0.1.11: the flask shares the vanilla potion cooldown"
print("0.1.11 supplies: %d flask + %d pouch loaded ids + 2 empty = %d items, charges %s, %d files (%d bytes), %d lang lines" % (
    len(SUP_LOADED[0]), len(SUP_LOADED[1]), len(SUP_LOADED[0]) + len(SUP_LOADED[1]) + 2, dict((c, SUP_CHARGE_T[c]) for c in SUP_CHARGES.values()),
    len(SUP_FILES), sum(len(v) for v in SUP_FILES.values()), len(lang_sup)))
print("0.1.11 flask order (worst first): " + ", ".join("%s %s%%" % (e["src"], pct_s(e["total"])) for e in SUP_F))
print("0.1.11 pouch order (worst first, first 12 + last 3): " + ", ".join(e["src"] for e in SUP_P[:12]) + " ... " + ", ".join(e["src"] for e in SUP_P[-3:]))
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"
print("0.1.8 assets: %d legacy 0.1.7 effects + %d bar levels (%s) as effects + %d stacking checks + %d fast eat charges (%s) + %d graded "
      "dishes (%d dishes x %d Grades) + %d own Grade 0 dishes + %d vanilla overrides (%d dishes + %d raw) + %d recipe variants = %d JSON, "
      "%d lang lines; longest check clears %d; self-check OK"
      % (len(LEGACY_EFFECTS), N_FX, ", ".join("%s %d" % (b, len(USED[b])) for b in BARS), N_FX, len(FAST),
         ", ".join("%s %gs -> %gs" % (p, t[0], t[1]) for p, t in sorted(FAST.items())), N_DISH, len(GDISHES), GEN_MAX, len(OWN_IDS),
         len(OVERRIDES), len(DISHES), len(RAW), N_VAR, len([n for n in files if n.endswith(".json")]), len(lang), max_clears))
print("0.1.8 families: " + "; ".join("%s %s T%d %s" % (DISH_NAME.get(d, d), "+".join(DISH_FAMS[d]), DISH_TIER[d],
      ",".join("%s %.2f" % (b[:3], x) for b, x in sorted(bar_weights(DISH_FAMS[d], DISH_TIER[d]).items(), key=lambda t: BARS.index(t[0]))))
      for d in GDISHES))
def _sample(d, g):
    w, inst, over, sn, dur = DISH_NUM[(d, g)]
    return "%s G%d: %s; %s; %s" % (DISH_NAME.get(d, d), g, "/".join("%s %s%%" % (b[0], pct_s(inst[b])) for b in inst),
                                   "/".join("%s %s" % (b[:3], pct_s(sn[b][1])) for b in sn) or "-", mmss(dur) if sn else "-")
print("0.1.8 samples (instant %; over time: He/Ma % per 2 s, St % max stamina, Str points; duration): " +
      " | ".join(_sample(d, g) for d in ("Food_Vegetable_Cooked", "Food_Kebab_Fruit", "Food_Pie_Meat", "Food_Skyy_Garden_Skewer", "Food_Skyy_Lunch_Tray") for g in (0, 5, 10)))
print("grade factors (strength / duration): " + ", ".join("G%d x%.2f/x%.2f" % (g, SF(g), DF(g)) for g in range(0, GEN_MAX + 1)))
# 0.1.4 self-check, on the LEGACY files: every 0.1.7 effect is still the vanilla one with ONLY its strength fields x S(g) and Duration x D(g)
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
    raise SystemExit("self-check 0.1.4: these legacy effects are not exactly vanilla x S(g) / x D(g): %s" % _capped)
print("0.1.4 (legacy files): all %d 0.1.7 effects = vanilla strength x (1 + 0.32 x Grade), Duration x 2^(Grade/5)" % len(LEGACY_EFFECTS))

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
    _rc = OWN_RECIPE[out] if out in OWN_RECIPE else rd(V_ITEMS[out])["Recipe"]   # 0.1.8: own dishes carry their recipe in the build
    cats = [c for b in (_rc.get("BenchRequirement") or []) if b.get("Id") == "Cookingbench" for c in (b.get("Categories") or [])]
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
# ---- 0.1.8: our own dishes, by the LOCKED difficulty rule (Skyy 2026-10-04: "the easier to craft the less xp. the harder to craft the
# more.") - chain raw x 950 x (20% + 15% per extra crafting step + 5% Prepared / 10% Baked + 5% per ingredient tier above 1), like every dish
for _oid in OWN_IDS:
    _r = OWN_RECIPE[_oid]
    COOK[_oid] = (inputs_of(_r), int(_r["Output"][0]["Quantity"]), float(_r["TimeSeconds"]), False)   # 0.1.12: Sliced Bread makes 2
for _oid in OWN_IDS:
    DIFF[_oid] = diff_share(_oid)
    XP[_oid] = rnd_to(K_XP * DIFF[_oid] * chain_raw(_oid) * COOK[_oid][1] / 100.0, 50)   # 0.1.12: x the output count (1 = unchanged)
_easy8 = [d for d in GDISHES if len(chain_crafts(d)) == 1 and not COOK[d][3]]
_hard8 = [d for d in GDISHES if len(chain_crafts(d)) >= 3]
assert max(XP[d] for d in _easy8) < min(XP[d] for d in _hard8), "0.1.8: an easy dish pays as much as a multi-step one"
for _oid in OWN_IDS:   # a skewer of ours pays like the vanilla skewer with the same raw count; a dish with a crafted input pays more per raw item
    assert XP[_oid] > 0 and (len(chain_crafts(_oid)) == 1 or XP[_oid] / chain_raw(_oid) > XP["Food_Kebab_Vegetable"] / chain_raw("Food_Kebab_Vegetable")), _oid
print("0.1.12 new dishes (tier, families, instant %; over time; XP per craft): " + "; ".join("%s T%d %s inst %s; over %s; %d XP" % (
    _oid, DISH_TIER[_oid], "+".join(DISH_FAMS[_oid]), ", ".join("%s %s" % (b, pct_s(v)) for b, v in DISH_NUM[(_oid, 0)][1].items()),
    ", ".join("%s %s" % (b, pct_s(v[1])) for b, v in DISH_NUM[(_oid, 0)][3].items()), XP[_oid]) for _oid in NEW_IDS))
print("0.1.8 own dish XP (difficulty share %, chain raw -> XP): " + ", ".join("%s %d%% %.1f -> %d" % (_oid, DIFF[_oid], chain_raw(_oid), XP[_oid]) for _oid in OWN_IDS))
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
assert _best in GDISHES, "0.1.6: the fastest route must be a dish, not %s" % _best
assert max(RATE[i] for i in INGS) < min(RATE[d] for d in GDISHES), "0.1.6: an ingredient spam route levels as fast as a dish"
assert RATE[_best] <= 1.15 * max(RATE[d] for d in DISHES), "0.1.8: an own dish must not become a much faster levelling route than the vanilla best"
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
MAX_PER_MIN_OLD = MAX_PER_MIN   # 0.1.13: the old default CookNcMig moves to 0 once
MAX_PER_MIN = 0                 # 0.1.13 NO XP CAPS (Skyy 2026-10-18: "if so remove all caps"): 0 = no cap
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
# 0.1.15 BALANCE P3 (research/Balance-P3-XP-Spec.md 3.5; tools/cooking_0_1_15_patch.py): XP_P3 = the 0.1.14 formula x F(T of the craft's best
# ingredient) with K_P3 (the tables above stay the 0.1.14 ones: every older update / self-check reads them; XP_P3 is what the jar pays)
# =====================================================================================================================
import tier_tags as _TT15
P3_FT = [1.0, 2.11, 3.6, 4.91, 7.43, 10.04, 12.15, 15.95, 19.68, 22.59, 27.67, 32.52, 36.23, 42.59, 48.56, 53.07]   # the spec's F(T) table
LV50_P3 = 487440   # SkyySkills 0.4.57: levels 1-50 of the P3 list at levels.scale 120 %
def p3_tier(out, depth=0):
    """the highest tier_tags tier among the craft's whole ingredient chain (untagged items and resource groups = T1)"""
    assert depth < 8, out
    t = 1
    for kind, i, n in COOK[out][0]:
        if kind == "I" and i in COOK and i != out: t = max(t, p3_tier(i, depth + 1))
        elif kind == "I": t = max(t, _TT15.tier(i) or 1)
    return t
def p3_raw(k):
    """the 0.1.14 formula before rounding (K_XP = 950)"""
    if k in OWN_IDS: return K_XP * DIFF[k] * chain_raw(k) * COOK[k][1] / 100.0
    if k in DISHES: return K_XP * DIFF[k] * chain_raw(k) / 100.0
    if k in INGS: return K_XP * ING_PM[k] * direct_raw(k) / 1000.0
    raise SystemExit("0.1.15: no formula for " + k)
P3_T = dict((k, p3_tier(k)) for k in XP)
def p3_table(kk):
    # rounded like 0.1.14 (5 for ingredient crafts, 50 for dishes), never below one step (a craft that paid XP keeps paying some)
    return dict((k, max(5 if k in INGS else 50, rnd_to(p3_raw(k) * kk / K_XP * P3_FT[P3_T[k] - 1], 5 if k in INGS else 50))) for k in XP)
def p3_rate(tab, out):
    def cx(o, depth=0):
        ins, q, _, _ = COOK[o]
        x = tab[o] / float(q)
        for kind, i, n in ins:
            if kind == "I" and i in COOK and i != o: x += cx(i, depth + 1) * n
        return x
    return ITEMS_PER_HOUR / chain_raw(out) * cx(out)
P3_XPM = 0.5   # xpMultiplier's default (asserted = XP_MULT_DEF below)
P3_TARGET = 48000.0 / P3_XPM   # base XP an hour (before xpMultiplier 0.5) per F(T): the model's 60 dishes x 800 x F after it
_kv, _kp = "Food_Kebab_Vegetable", "Food_Pie_Meat"
# Skyy's difficulty rule (0.1.5: "the easier to craft the less xp. the harder to craft the more.") makes the pie pay ~4.5x the skewer per raw
# item, so ONE K cannot put both on 48,000 x F: K puts their GEOMETRIC MEAN on it (the skewer route ~0.47x, the pie route ~2.1x the target)
_g = (p3_rate(p3_table(K_XP), _kv) * p3_rate(p3_table(K_XP), _kp)) ** 0.5
assert P3_T[_kv] == 1 and P3_T[_kp] == 1
K_P3 = float(int(round(K_XP * P3_TARGET / _g)))
XP_P3 = p3_table(K_P3)
_rk, _rp = p3_rate(XP_P3, _kv), p3_rate(XP_P3, _kp)
assert abs((_rk * _rp) ** 0.5 / P3_TARGET - 1.0) < 0.05, "0.1.15: skewer x pie routes must average (geometric) ~48,000 x F an hour after xpMultiplier (%.0f / %.0f)" % (_rk, _rp)
assert 0.3 * P3_TARGET <= _rk <= P3_TARGET <= _rp <= 3.5 * P3_TARGET, "0.1.15: the skewer route at or below the target, the pie route at or above (%.0f / %.0f)" % (_rk, _rp)
assert sorted(XP_P3) == sorted(XP) and all(v > 0 for v in XP_P3.values()) and max(XP_P3.values()) < 9000000
print("0.1.15 Balance P3: K %d -> %d; Vegetable Skewer %.0f / Meat Pie %.0f base XP/h at %d items/h (x%s after xpMultiplier = %.0f / %.0f; target 48,000 x F); "
      "Cooking 50 = %d XP in ~%.1f h on skewers, ~%.1f h on pies"
      % (K_XP, K_P3, _rk, _rp, ITEMS_PER_HOUR, repr(P3_XPM), _rk * P3_XPM, _rp * P3_XPM, LV50_P3, LV50_P3 / _rk, LV50_P3 / _rp))
print("0.1.15 XP per craft (tier: 0.1.14 -> P3): " + ", ".join("%s T%d %d -> %d" % (k, P3_T[k], XP[k], XP_P3[k]) for k in sorted(XP, key=lambda k: XP_P3[k])))

# =====================================================================================================================
# 0.1.16 ING_TIER v3 (tools/cooking_0_1_16_patch.py): ONE tier per raw ingredient on the tools/tier_tags.py ladder (TT_VERSION 3); the P3
# tier factor AND the difficulty share's tier step (per zone) read it. XP_V3 is what the jar pays (XP_P3 stays: CookP3Mig + its checks)
# =====================================================================================================================
assert _TT15.TT_VERSION == "3", "0.1.16: ING_TIER v3 is the TT_VERSION 3 ladder (tier_tags is %s)" % _TT15.TT_VERSION
ING_TIER_V1 = dict(ING_TIER)   # the 0.1.5 Bazaar rows - every older section + self-check above reads ING_TIER as it was
assert ING_TIER_V1 == {"Plant_Crop_Corn_Item": 2, "Plant_Crop_Pumpkin_Item": 4, "Plant_Fruit_Apple": 2, "Milk_Bucket": 2}
# a fruit without a tier_tags row = the tier_tags tier of the tree it grows on (Assets.zip: apple trees; Palm / Palm_Green prefabs + the Zone 2
# island covers; Jungle2 boulder trees; Jungle + Jungle_Crystal prefabs - the lowest of Jungle T13 / Crystal T15)
FRUIT_TREE = {"Plant_Fruit_Apple": "Wood_Apple_Trunk", "Plant_Fruit_Coconut": "Wood_Palm_Trunk", "Plant_Fruit_Mango": "Wood_Jungle_Trunk",
              "Plant_Fruit_Pinkberry": "Wood_Jungle_Trunk"}
# the rest without a tier_tags row (zone tiers, research/Zone-Tiers-Idea.md: 3 tiers a zone, Zone 1 = T1-T3): Red Berries = Zone 1 bushes,
# Milk = Zone 1 livestock one step up (the 0.1.5 row: "Milk needs livestock"), the Zone 1 basics; resource groups = T1 (P3 spec 3.5)
ING_OWN_T = {"Plant_Fruit_Berries_Red": 1, "Milk_Bucket": 2, "Food_Egg": 1, "Rock_Salt": 1, "Ingredient_Stick": 1, "*Deco_Tankard_State_Filled_Water": 1}
RES_T1 = ("Fish", "Fish_Uncommon", "Fish_Rare", "Fish_Epic", "Fish_Legendary", "Flowers", "Fruits", "Fuel", "Meats", "Mushrooms", "Vegetables")
for _i in list(FRUIT_TREE) + list(ING_OWN_T):
    assert not _TT15.tier(_i), "0.1.16: %s has a tier_tags row now - drop the Cooking fallback (the one tier table wins)" % _i
    assert _i in V_ITEMS or _i in V_RTYPES or _i.startswith("*"), "0.1.16: tier id %s is not in Assets.zip" % _i
for _i, _w in FRUIT_TREE.items(): assert _TT15.family(_w) == "log" and _TT15.tier(_w), "0.1.16: %s's tree %s has no tier_tags log row" % (_i, _w)
RAW_V3 = sorted(set((k, i) for o in COOK for k, i, n in COOK[o][0] if not (k == "I" and i in COOK)))
ING_TIER_V3, ING_SRC_V3 = {}, {}
for _k, _i in RAW_V3:
    if _k == "I" and _TT15.tier(_i): ING_TIER_V3[_i], ING_SRC_V3[_i] = _TT15.tier(_i), "tier_tags"
    elif _i in FRUIT_TREE: ING_TIER_V3[_i], ING_SRC_V3[_i] = _TT15.tier(FRUIT_TREE[_i]), "tree " + FRUIT_TREE[_i]
    elif _i in ING_OWN_T: ING_TIER_V3[_i], ING_SRC_V3[_i] = ING_OWN_T[_i], "zone"
    elif _k == "R" and _i in RES_T1: ING_TIER_V3[_i], ING_SRC_V3[_i] = 1, "group"
    else: raise SystemExit("0.1.16: the raw ingredient %s %s has no tier - add a tools/tier_tags.py row (or FRUIT_TREE / ING_OWN_T)" % (_k, _i))
assert set(FRUIT_TREE) | set(ING_OWN_T) <= set(ING_TIER_V3), "0.1.16: a fallback row no recipe uses"
assert all(1 <= t <= 15 for t in ING_TIER_V3.values()) and len(set(i for k, i in RAW_V3)) == len(RAW_V3)
assert (ING_TIER_V3["Plant_Crop_Tomato_Item"], ING_TIER_V3["Plant_Crop_Turnip_Item"], ING_TIER_V3["Plant_Fruit_Mango"],
        ING_TIER_V3["Plant_Fruit_Coconut"], ING_TIER_V3["Plant_Fruit_Apple"]) == (9, 6, 13, 4, 2), "0.1.16: the documented rows"
def v3_zone(t): return (t + 2) // 3            # T1-3 = zone 1 ... T13-15 = zone 5
def v3_tier(out, depth=0):
    """the highest ING_TIER_V3 tier among the craft's whole ingredient chain"""
    assert depth < 8, out
    t = 1
    for kind, i, n in COOK[out][0]:
        if kind == "I" and i in COOK:
            if i != out: t = max(t, v3_tier(i, depth + 1))
        else: t = max(t, ING_TIER_V3[i])
    return t
V3_T = dict((k, v3_tier(k)) for k in XP)
DIFF_V3 = dict((o, DIFF[o] + DIFF_TIER * ((v3_zone(V3_T[o]) - 1) - (chain_tier(o) - 1))) for o in DIFF)
ING_PM_V3 = dict((o, ING_PM[o] + ING_TIERW * ((v3_zone(V3_T[o]) - 1) - (chain_tier(o) - 1))) for o in ING_PM)
for _o in DIFF: assert DIFF_V3[_o] == diff_share(_o) - DIFF_TIER * (chain_tier(_o) - 1) + DIFF_TIER * (v3_zone(V3_T[_o]) - 1) > 0
assert sorted(DIFF_V3) == sorted(GDISHES) and sorted(ING_PM_V3) == sorted(INGS) and min(ING_PM_V3.values()) >= ING_BASE
def v3_raw(k):
    """p3_raw with the v3 shares"""
    if k in OWN_IDS: return K_XP * DIFF_V3[k] * chain_raw(k) * COOK[k][1] / 100.0
    if k in DISHES: return K_XP * DIFF_V3[k] * chain_raw(k) / 100.0
    if k in INGS: return K_XP * ING_PM_V3[k] * direct_raw(k) / 1000.0
    raise SystemExit("0.1.16: no formula for " + k)
XP_V3 = dict((k, max(5 if k in INGS else 50, rnd_to(v3_raw(k) * K_P3 / K_XP * P3_FT[V3_T[k] - 1], 5 if k in INGS else 50))) for k in XP)
# the formula is P3's: every craft whose tier and share did not move keeps its exact 0.1.15 number; K's two rate routes are among them
for _k in XP:
    if V3_T[_k] == P3_T[_k] and DIFF_V3.get(_k) == DIFF.get(_k) and ING_PM_V3.get(_k) == ING_PM.get(_k):
        assert XP_V3[_k] == XP_P3[_k], "0.1.16: %s did not move but pays %d, not %d" % (_k, XP_V3[_k], XP_P3[_k])
assert V3_T[_kv] == V3_T[_kp] == 1 and XP_V3[_kv] == XP_P3[_kv] and XP_V3[_kp] == XP_P3[_kp], "0.1.16: K's rate routes must not move"
assert abs((p3_rate(XP_V3, _kv) * p3_rate(XP_V3, _kp)) ** 0.5 / P3_TARGET - 1.0) < 0.05
assert V3_T["Food_Skyy_Tropical_Smoothie"] == 13 and XP_V3["Food_Skyy_Tropical_Smoothie"] > 10 * XP_P3["Food_Skyy_Tropical_Smoothie"], "0.1.16: the smoothie"
assert sorted(XP_V3) == sorted(XP) and all(v > 0 for v in XP_V3.values()) and max(XP_V3.values()) < 9000000
V3_KEYS = sorted(k for k in XP if XP_V3[k] != XP_P3[k])
assert V3_KEYS, "0.1.16: nothing changed"
print("0.1.16 ING_TIER v3 (%d raw ingredients): " % len(ING_TIER_V3) + ", ".join("%s T%d (%s)" % (i, ING_TIER_V3[i], ING_SRC_V3[i]) for i in sorted(ING_TIER_V3, key=lambda i: (ING_TIER_V3[i], i))))
print("0.1.16 XP per craft that moved (tier, share: 0.1.15 -> v3): " + ", ".join("%s T%d->T%d %s->%s %d -> %d" % (
    k, P3_T[k], V3_T[k], DIFF.get(k, ING_PM.get(k)), DIFF_V3.get(k, ING_PM_V3.get(k)), XP_P3[k], XP_V3[k]) for k in sorted(V3_KEYS, key=lambda k: XP_V3[k])))

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
def _bonus(n):   # 0.1.8: the nominal (unsnapped) numbers of one dish at one Grade
    return [n[1][b] for b in sorted(n[1])] + [n[2][b] for b in sorted(n[2])]
for d in CAMP_DISHES:
    if DISH_TIER[d] != 1 or XP.get(d, 0) <= 0:
        raise SystemExit("self-check 0.1.1: campfire dish %s must be a T1 graded dish with Cooking XP (tier %s, xp %s)" % (d, DISH_TIER[d], XP.get(d)))
    for g in range(1, GEN_MAX + 1):
        if dish_id(d, g) not in G_ITEMS: raise SystemExit("self-check 0.1.1: no Grade asset " + dish_id(d, g))
    # its heal and buffs scale by exactly S(g) and its durations by D(g) (no cap binds on T1 numbers), so the strength the mapping compares
    # is the real one
    _b0 = _bonus(DISH_NUM[(d, 0)])
    for g in range(1, GEN_MAX + 1):
        _bg, _n = _bonus(DISH_NUM[(d, g)]), DISH_NUM[(d, g)]
        if any(abs(x - y * SF(g)) > 0.0102 for x, y in zip(_bg, _b0)) or abs(_n[4] - DISH_NUM[(d, 0)][4] * DF(g)) > 0.01:
            raise SystemExit("self-check 0.1.1: Grade %d of %s hits a cap - the campfire mapping would not be x%.2f" % (g, d, SF(g)))
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
# 0.1.13 run-once marker of the no XP caps update (CookNcMig): own line, plain ASCII, no '=' (never a #key=value template line)
NC_MARK_ID = "SkyyCooking 0.1.13 no XP caps"
NC_MARK = "# SkyyCooking 0.1.13 no XP caps (Skyy 2026-10-18: remove all caps) - a maxXpPerMinute line still on the old default 1500000 was set to 0 once (0 means no cap)"
assert all(32 <= ord(_c) < 127 for _c in NC_MARK) and "=" not in NC_MARK and NC_MARK.startswith("# " + NC_MARK_ID)
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
         ("CGrill", 15, 0.02, "unused since SkyyTrees 0.4 (no Skill Trees 3 upgrade; kept for later)"),
         ("CPrep", 10, 0.03, "unused since SkyyTrees 0.4 (no Skill Trees 3 upgrade; kept for later)"),
         ("CBaker", 10, 0.03, "unused since SkyyTrees 0.4 (no Skill Trees 3 upgrade; kept for later)"),
         ("CIngr", 10, 0.03, "Forager's Larder (Cooking tree, Pantry): chance per rank an ingredient craft (flour, dough, salt, spices) gives double output"),
         ("CGourmet2", 20, 0.01, "chance of +1 Grade on any dish (adds to CGourmet)"),
         ("CSig", 10, 0.01, "chance of +2 Grades"), ("CMaster", 5, 0.05, "unused since SkyyTrees 0.4 (no Skill Trees 3 upgrade; kept for later)")]
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
      NC_MARK,   # 0.1.13
      "# safety net: base Cooking XP per player per minute (counted before xpMultiplier); 0 = off. The dish is always given.",
      "maxXpPerMinute=%d" % MAX_PER_MIN,
      "# chat lines for tree bonuses and a new Grade",
      "messages=true",
      "# dishes that come out graded (must be dishes this jar generated assets for; others always come out plain)",
      "graded=" + ",".join(GDISHES),
      "# true = SkyyCooking's own dishes (Garden Skewer, Rice Bowl ...) always come out graded, whatever the graded list says (0.1.8)",
      "gradedOwn=true"] + CAMP_LINES + [
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
assert XP_MULT_DEF == P3_XPM, "0.1.15: the rate target assumes xpMultiplier 0.5"
DEFAULTS_TEXT_014 = DEFAULTS_TEXT   # 0.1.15: the 0.1.14 default file - the older updates' self-checks below read it
# 0.1.15 run-once marker of the Balance P3 Cooking XP update (CookP3Mig) + the reworded help line about the formula (1:1)
P3_MARK_ID = "SkyyCooking 0.1.15 Balance P3 Cooking XP"
P3_MARK = "# SkyyCooking 0.1.15 Balance P3 Cooking XP (Skyy 2026-10-18): dishes pay more for higher tier ingredients - the xp lines still on the old defaults were updated once"
assert all(32 <= ord(_c) < 127 for _c in P3_MARK) and "=" not in P3_MARK and P3_MARK.startswith("# " + P3_MARK_ID)
XP_HELP_P3 = [XP_HELP_016[0],
              "# pays the raw gathering in its whole ingredient chain x %d per item x 20%% + 15%% per extra crafting step + 25%% recipe knowledge + 5%% Prepared" % int(K_P3),
              "# / 10% Baked + 5% per tier above 1, x the tier factor of its best ingredient (P3). An ingredient craft pays 1.5% of its own inputs (more per step)."]
assert XP_HELP_P3[1] != XP_HELP_016[1] and all(32 <= ord(_c) < 127 for _l in XP_HELP_P3 for _c in _l)
P3_KEYS = sorted(k for k in XP if XP_P3[k] != XP[k])
def p3_text(t):
    """the Python twin of CookP3Mig.update on an LF default file (the build checks the compiled update gives the same text)"""
    ls = t.split("\n")
    out = []
    for ln in ls:
        if ln.startswith("#") and ln in XP_HELP_016 and XP_HELP_P3[XP_HELP_016.index(ln)] != ln:
            out.append(XP_HELP_P3[XP_HELP_016.index(ln)])
            continue
        if not ln.startswith("#") and "=" in ln:
            k_, v_ = ln.split("=", 1)
            if k_.startswith("xp.") and k_[3:] in P3_KEYS and v_ == str(XP[k_[3:]]):
                out.append(k_ + "=" + str(XP_P3[k_[3:]]))
                continue
        out.append(ln)
    at = [i for i, l in enumerate(out) if l.startswith("xp.")][0]
    while at > 0 and out[at - 1].startswith("#") and out[at - 1].strip():
        at -= 1
    out.insert(at, P3_MARK)
    return "\n".join(out)
DEFAULTS_TEXT = p3_text(DEFAULTS_TEXT_014)
assert DEFAULTS_TEXT.count(P3_MARK + "\n" + XP_ING_MARK + "\n") == 1 and all(DEFAULTS_TEXT.count("\nxp.%s=%d\n" % (k, v)) == 1 for k, v in XP_P3.items())
DEFAULTS_TEXT_015 = DEFAULTS_TEXT   # 0.1.16: the 0.1.15 default file - CookP3Mig's self-checks below read it
# 0.1.16 run-once marker of the ING_TIER v3 Cooking XP update (CookV3Mig) + the reworded help line about the tier step (1:1)
V3_MARK_ID = "SkyyCooking 0.1.16 ingredient tiers v3"
V3_MARK = "# SkyyCooking 0.1.16 ingredient tiers v3 (2026-10-21): every ingredient has a tier now (fruit, milk) - the xp lines still on the old defaults were updated once"
assert all(32 <= ord(_c) < 127 for _c in V3_MARK) and "=" not in V3_MARK and V3_MARK.startswith("# " + V3_MARK_ID)
assert V3_MARK_ID not in P3_MARK and P3_MARK_ID not in V3_MARK and XP_ING_MARK_ID not in V3_MARK and XP_TBL_MARK_ID not in V3_MARK and XP_MARK_ID not in V3_MARK
XP_HELP_V3 = [XP_HELP_P3[0], XP_HELP_P3[1],
              "# / 10% Baked + 5% per zone above 1, x the tier factor of its best ingredient (P3). An ingredient craft pays 1.5% of its own inputs (more per step)."]
assert XP_HELP_V3[2] != XP_HELP_P3[2] and all(32 <= ord(_c) < 127 for _l in XP_HELP_V3 for _c in _l) and len(XP_HELP_V3[2]) <= len(XP_HELP_P3[2])
def v3_text(t):
    """the Python twin of CookV3Mig.update on an LF default file (the build checks the compiled update gives the same text)"""
    out = []
    for ln in t.split("\n"):
        if ln.startswith("#") and ln in XP_HELP_P3 and XP_HELP_V3[XP_HELP_P3.index(ln)] != ln:
            out.append(XP_HELP_V3[XP_HELP_P3.index(ln)])
            continue
        if not ln.startswith("#") and "=" in ln:
            k_, v_ = ln.split("=", 1)
            if k_.startswith("xp.") and k_[3:] in V3_KEYS and v_ == str(XP_P3[k_[3:]]):
                out.append(k_ + "=" + str(XP_V3[k_[3:]]))
                continue
        out.append(ln)
    at = [i for i, l in enumerate(out) if l.startswith("xp.")][0]
    while at > 0 and out[at - 1].startswith("#") and out[at - 1].strip():
        at -= 1
    out.insert(at, V3_MARK)
    return "\n".join(out)
DEFAULTS_TEXT = v3_text(DEFAULTS_TEXT_015)
assert DEFAULTS_TEXT.count(V3_MARK + "\n" + P3_MARK + "\n" + XP_ING_MARK + "\n") == 1 and all(DEFAULTS_TEXT.count("\nxp.%s=%d\n" % (k, v)) == 1 for k, v in XP_V3.items())
assert DEFAULTS_TEXT.count(XP_HELP_V3[2] + "\n") == 1 and XP_HELP_P3[2] not in DEFAULTS_TEXT

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
# ================= 0.1.7 SOUND PASS ROUND 2: CookSnd (pasted by tools/cooking_0_1_7_patch.py from tools/soundpass_gen.py - research/Sound-Pass-Plan.md) =================
# Vanilla sound event ids played BY ID, 2D to that player only (category UI); never throws; 0.5 s per player per sound; the per-player
# switch settings:sounds:<uuid> (Boolean FALSE on the bridge = silent; SkyyMenu 0.3.25 /settings); Skyy_SkyyCooking/sounds.properties.
import zipfile as _sndzf, jpype as _sndjp
_SNDZ = _SJ.assets_zip()   # read-only (0.1.7: the cached copy)
SOUND_IDS = set(os.path.basename(_n)[:-5] for _n in _sndzf.ZipFile(_SNDZ).namelist() if _n.startswith("Server/Audio/SoundEvents/") and _n.endswith(".json"))
SND_SOUNDS = [["meal", "MEAL", "Meal done", "SFX_Furnace_Bench_Processing_Complete"]]
for _s in SND_SOUNDS:
    assert _s[3] in SOUND_IDS, "0.1.7: sound event %s is not in Assets.zip" % _s[3]
_SND_PKG = (PKG).rstrip(".")
_SND_FIELDS = [
    "public static volatile boolean ON = true;",
    "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();",
    "public static final java.util.concurrent.ConcurrentHashMap WARNED = new java.util.concurrent.ConcurrentHashMap();",
    "public static final java.util.concurrent.atomic.AtomicLong PLAYED = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong MUTED = new java.util.concurrent.atomic.AtomicLong();",
    "public static final java.util.concurrent.atomic.AtomicLong WARNS = new java.util.concurrent.atomic.AtomicLong();",
    "public static final long GAP_MS = 500L;",
    "public static final String MUTE_KEY = \"settings:sounds:\";",
    "public static java.nio.file.Path FILE;",
    "public static volatile boolean S_MEAL = true;",
    "public static volatile String S_MEAL_ID = \"SFX_Furnace_Bench_Processing_Complete\";",
    "public static final String DEFAULT_TEXT = \"# SkyyCooking sounds (SkyWynn sound pass). Change them in game: SkyWynn Menu -> Server Setup -> Cooking -> Sounds,\\n# or edit here and press Reload there. Each id is a vanilla sound event id (try one in game with /soundtest <id>);\\n# an empty id = that sound off. Every player can also switch all SkyWynn sounds off for themselves in /settings.\\nsounds.enabled=true\\n# Meal done: A Cooking Bench craft gave a graded dish (not ingredients, not plain food).\\nsound.meal=true\\nsound.meal.id=SFX_Furnace_Bench_Processing_Complete\\n\";",
]
_SND_METHODS = [
    r'''
public static void warn(String msg) {
  WARNS.incrementAndGet();
  try { com.hypixel.hytale.logger.HytaleLogger.get("SkyyCooking").at(java.util.logging.Level.WARNING).log("[SkyyCooking] " + msg); } catch (Throwable t) { }
}''',
    r'''
public static int idx(String id) {
  if (id == null) return Integer.MIN_VALUE;
  String v = id.trim();
  if (v.length() == 0) return Integer.MIN_VALUE;
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    return m == null ? Integer.MIN_VALUE : m.getIndex(v);
  } catch (Throwable t) { return Integer.MIN_VALUE; }
}''',
    r'''
public static String err(String value) {
  if (value == null) return null;
  String v = value.trim();
  if (v.length() == 0) return null;
  if (v.length() > 120) return "A sound id is at most 120 characters.";
  for (int i = 0; i < v.length(); i++) {
    char c = v.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_')) return "A sound id is letters, digits and _ only (like SFX_Coins_Land).";
  }
  try {
    com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap m = com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent.getAssetMap();
    if (m != null && m.getIndex(v) == Integer.MIN_VALUE) return "The game has no sound event '" + v + "' - find ids with /soundtest list, or leave it empty for no sound.";
  } catch (Throwable t) { }
  return null;
}''',
    r'''
public static String check(String key, String value) {
  return err(value);
}''',
    r'''
public static boolean word(String v, boolean d) {
  if (v == null) return d;
  String t = v.trim().toLowerCase();
  if (t.equals("true") || t.equals("on") || t.equals("yes") || t.equals("1")) return true;
  if (t.equals("false") || t.equals("off") || t.equals("no") || t.equals("0")) return false;
  return d;
}''',
    r'''
public static String id(int w) {
  if (!ON) return null;
  boolean on = false;
  String v = null;
  if (w == 0) { on = S_MEAL; v = S_MEAL_ID; }
  if (!on || v == null) return null;
  v = v.trim();
  return v.length() == 0 ? null : v;
}''',
    r'''
public static java.util.Map bridge() {
  try {
    Object o = System.getProperties().get("skyy.bridge");
    return o instanceof java.util.Map ? (java.util.Map) o : null;
  } catch (Throwable t) { return null; }
}''',
    r'''
public static boolean muted(java.util.UUID u) {
  if (u == null) return false;
  try {
    java.util.Map b = bridge();
    if (b == null) return false;
    Object o = b.get(MUTE_KEY + u.toString());
    return (o instanceof Boolean) && !((Boolean) o).booleanValue();
  } catch (Throwable t) { return false; }
}''',
    r'''
public static boolean gate(String key, long now) {
  Object o = LAST.get(key);
  if (o instanceof Long) { long d = now - ((Long) o).longValue(); if (d >= 0L && d < GAP_MS) return false; }
  if (LAST.size() > 4096) LAST.clear();
  LAST.put(key, Long.valueOf(now));
  return true;
}''',
    r'''
public static com.hypixel.hytale.server.core.universe.PlayerRef ref(java.util.UUID u) {
  if (u == null) return null;
  try {
    com.hypixel.hytale.server.core.universe.Universe uni = com.hypixel.hytale.server.core.universe.Universe.get();
    return uni == null ? null : uni.getPlayer(u);
  } catch (Throwable t) { return null; }
}''',
    r'''
public static boolean playTo(com.hypixel.hytale.server.core.universe.PlayerRef pr, int w) {
  if (pr == null) return false;
  String id = id(w);
  if (id == null) return false;
  try {
    if (!pr.isValid()) return false;
    java.util.UUID u = pr.getUuid();
    if (muted(u)) { MUTED.incrementAndGet(); return false; }
    int i = idx(id);
    if (i == Integer.MIN_VALUE || i == 0) {
      if (WARNED.putIfAbsent(id, Boolean.TRUE) == null) warn("sound event '" + id + "' is not in the game assets - it is not played (Server Setup -> Sounds)");
      return false;
    }
    if (!gate(String.valueOf(u) + "|" + w, System.currentTimeMillis())) return false;
    com.hypixel.hytale.server.core.universe.world.SoundUtil.playSoundEvent2dToPlayer(pr, i, com.hypixel.hytale.protocol.SoundCategory.UI);
    PLAYED.incrementAndGet();
    return true;
  } catch (Throwable t) {
    if (WARNED.putIfAbsent("!play", Boolean.TRUE) == null) warn("could not play a sound (logged once): " + t);
    return false;
  }
}''',
    r'''
public static boolean play(java.util.UUID u, int w) {
  if (u == null || id(w) == null) return false;
  return playTo(ref(u), w);
}''',
    r'''
public static boolean ok(java.util.UUID u, String res, int w) {
  if (res == null || !res.startsWith("+")) return false;
  return play(u, w);
}''',
    r'''
public static boolean meal(com.hypixel.hytale.server.core.universe.PlayerRef pr, boolean gave) {
  if (!gave) return false;
  return playTo(pr, 0);
}''',
    r'''
public static String text() {
  int n = 0;
  if (S_MEAL && S_MEAL_ID != null && S_MEAL_ID.trim().length() > 0) n++;
  return "sounds " + (ON ? "on" : "off") + " (" + n + " of 1)";
}''',
    r'''
public static String load(java.nio.file.Path dir) {
  if (dir == null) return text();
  FILE = dir.resolve("sounds.properties");
  try {
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = dir.resolve("sounds.properties.tmp");
      java.nio.file.Files.write(tmp, DEFAULT_TEXT.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    ON = word(p.getProperty("sounds.enabled"), true);
    S_MEAL = word(p.getProperty("sound.meal"), true);
    S_MEAL_ID = p.getProperty("sound.meal.id", "SFX_Furnace_Bench_Processing_Complete").trim();
  } catch (Throwable t) { warn("could not read sounds.properties (the sounds keep their defaults): " + t); }
  return text();
}''',
]
_snd_cls = pool.makeClass(_SND_PKG + ".CookSnd")
for _src in _SND_FIELDS:
    _snd_cls.addField(_sndjp.JClass("javassist.CtField").make(_src.replace("@SPKG@", _SND_PKG), _snd_cls))
for _src in _SND_METHODS:
    _snd_cls.addMethod(_sndjp.JClass("javassist.CtNewMethod").make(_src.replace("@SPKG@", _SND_PKG), _snd_cls))
_snd_cls.writeFile(OUT)
print("CookSnd: 1 sound(s), every default id is in Assets.zip")

def F(cls, decl): cls.addField(CtField.make(decl, cls))
def Mk(cls, src): cls.addMethod(CtNewMethod.make(jsrc(src), cls))
def Ct(cls, src): cls.addConstructor(CtNewConstructor.make(jsrc(src), cls))

# ================= CookCfg: cooking.properties + build-time constants =================
F(cfg, "public static %s LOG;" % LOG)
F(cfg, "public static java.nio.file.Path FILE;")
F(cfg, "public static final int GEN_MAX = %d;" % GEN_MAX)
F(cfg, "public static final String[] DISHES = %s;" % jstr_arr(GDISHES))   # 0.1.8: the 15 vanilla dishes, then our own
F(cfg, "public static final int[] TIER = %s;" % jint_arr([DISH_TIER[d] for d in GDISHES]))
F(cfg, "public static final String[] NAMES = %s;" % jstr_arr([DISH_NAME[d] for d in GDISHES]))
F(cfg, "public static final int N_VAN = %d;" % len(DISHES))                # 0.1.8: DISHES[N_VAN..] = SkyyCooking's own dishes
F(cfg, "public static volatile boolean OWN_GRADED = true;")                 # 0.1.8: gradedOwn (missing line = true)
F(cfg, "public static final String[] INGR = %s;" % jstr_arr(INGREDIENTS))
F(cfg, "public static final String[] NODES = %s;" % jstr_arr([n[0] for n in NODES]))
F(cfg, "public static final int[] NODE_MAX = %s;" % jint_arr([n[1] for n in NODES]))
F(cfg, "public static final double[] NODE_DEF = %s;" % jdbl_arr([n[2] for n in NODES]))
F(cfg, "public static final double[] SF = %s;" % jdbl_arr([round(SF(g), 4) for g in range(GEN_MAX + 1)]))
F(cfg, "public static final double[] DF = %s;" % jdbl_arr([round(DF(g), 4) for g in range(GEN_MAX + 1)]))
F(cfg, "public static final String[] XP_IDS = %s;" % jstr_arr(sorted(XP)))
F(cfg, "public static final long[] XP_VALS = %s;" % jlong_arr([XP_V3[k] for k in sorted(XP)]))   # 0.1.16: the ING_TIER v3 table
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
  if (!GRADED.contains(id) && !(i >= N_VAN && OWN_GRADED)) return 0;
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
    OWN_GRADED = bool(p, "gradedOwn", true);
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
    return (ENABLED ? "on" : "OFF") + ", " + gr.size() + " graded dishes (own dishes " + (OWN_GRADED ? "always graded" : "by the list") + "), max Grade " + MAX_GRADE + ", " + xp.size() + " XP keys, xpMultiplier " + XP_MULT + ", cap " + MAX_PER_MIN + "/min, campfire accessory x" + CAMP_BUFF + " Grade bonus x" + CAMP_XP + " XP" + (bad > 0 ? ", " + bad + " bad line(s) skipped" : "");
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
    ("graded", "Graded dishes", "grades", "items", ",".join(GDISHES), "0", str(len(GDISHES)), "", "", "live",
     "Dishes that come out graded - only the %d dishes this jar has Grade assets for." % len(GDISHES),
     "reload@cooking.properties:graded;check=CookHooks.checkGraded"),
    ("gradedOwn", "Own dishes graded", "grades", "bool", "true", "", "", "", "", "live",
     "On: SkyyCooking's own dishes (Garden Skewer ...) are always graded, whatever the list above says.",
     "reload@cooking.properties:gradedOwn"),
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
     "Per level (0.01 = 1%). CIngr = Forager's Larder; CGrill/CPrep/CBaker/CMaster unused (SkyyTrees 0.4).",          # 0.1.14 fixer: the dead nodes named
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
# 0.1.7 sound pass round 2: Server Setup -> Cooking -> Sounds (Skyy_SkyyCooking/sounds.properties); KEEP 20 -> 10 (the kit default)
COOK_CFG_CATS = COOK_CFG_CATS + [("sounds", "Sounds")]
COOK_CFG_ROWS = COOK_CFG_ROWS + [('sounds.enabled', 'Sounds', 'sounds', 'bool', 'true', '', '', '', '', 'live', 'Off = SkyyCooking plays no sound at all. Players can also mute every sound in /settings.', 'field:CookSnd.ON@Skyy_SkyyCooking/sounds.properties:sounds.enabled'), ('sound.meal', 'Meal done sound', 'sounds', 'bool', 'true', '', '', '', '', 'live', 'A Cooking Bench craft gave a graded dish (not ingredients, not plain food). Off = silent.', 'field:CookSnd.S_MEAL@Skyy_SkyyCooking/sounds.properties:sound.meal'), ('sound.meal.id', 'Meal done sound id', 'sounds', 'text', 'SFX_Furnace_Bench_Processing_Complete', '', '120', '', '', 'live', 'A vanilla sound event id (try it with /soundtest). Empty = no sound.', 'field:CookSnd.S_MEAL_ID@Skyy_SkyyCooking/sounds.properties:sound.meal.id;check=CookSnd.check')]
# ================= 0.1.11 SUPPLIES: SupCfg (supplies.properties) + Server Setup > Cooking > Supplies (spec 4.4) =================
SUP_DEFAULTS_TEXT = "\n".join([
    "# SkyyCooking %s - supplies.properties: the Potion Flask + Food Pouch. Change them in game: SkyWynn Menu -> Server Setup -> Cooking ->" % VERSION,
    "# Supplies, or edit here and press Reload there.",
    "# off = the Flask / Pouch only open their page (they show empty); nothing new goes in; taking out still works",
    "supplies.on=true",
    "# the two items are lifelong: one each per profile, never dropped, stored or sold (/flask and /pouch give them back)",
    "supplies.lifelong=true",
    "# how many potions the Potion Flask holds (1-10000)",
    "supplies.flaskCap=64",
    "# how many foods the Food Pouch holds (1-10000)",
    "supplies.pouchCap=256",
    "# raw meat, fish, eggs and cheese go in the Food Pouch too (off = they stay ingredients for the Void)",
    "supplies.pouchRaw=false",
    "# how often (seconds) a full Flask / Pouch is mentioned (0 = every time)",
    "supplies.fullNoticeSeconds=60"]) + "\n"
supc = pool.makeClass(PKG + ".SupCfg")
for _d in ("public static volatile boolean ON = true;", "public static volatile boolean LIFELONG = true;", "public static volatile int FLASK_CAP = 64;",
           "public static volatile int POUCH_CAP = 256;", "public static volatile boolean POUCH_RAW = false;",
           "public static volatile long FULL_NOTICE_MS = 60000L;", "public static volatile java.nio.file.Path FILE;",
           "public static final String DEFAULTS = %s;" % json.dumps(SUP_DEFAULTS_TEXT)):
    supc.addField(CtField.make(_d, supc))
Mk(supc, """
public static int cap(int k) { return k == 0 ? FLASK_CAP : POUCH_CAP; }""")
Mk(supc, """
public static int num(String v, int def, int lo, int hi) {
  if (v == null) return def;
  try { int n = Integer.parseInt(v.trim()); if (n < lo) return lo; if (n > hi) return hi; return n; } catch (Throwable t) { return def; }
}""")
Mk(supc, """
public static boolean bool(String v, boolean def) {
  if (v == null) return def;
  String t = v.trim().toLowerCase(java.util.Locale.ROOT);
  if (t.equals("true") || t.equals("on") || t.equals("1")) return true;
  if (t.equals("false") || t.equals("off") || t.equals("0")) return false;
  return def;
}""")
# the file is written from DEFAULTS only when it is missing (a new file: no migration); a hand-edited file is only read
Mk(supc, """
public static String load(java.nio.file.Path dir) {
  try {
    FILE = dir.resolve("supplies.properties");
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Files.write(FILE, DEFAULTS.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    ON = bool(p.getProperty("supplies.on"), true);
    LIFELONG = bool(p.getProperty("supplies.lifelong"), true);
    FLASK_CAP = num(p.getProperty("supplies.flaskCap"), 64, 1, 10000);
    POUCH_CAP = num(p.getProperty("supplies.pouchCap"), 256, 1, 10000);
    POUCH_RAW = bool(p.getProperty("supplies.pouchRaw"), false);
    FULL_NOTICE_MS = (long) num(p.getProperty("supplies.fullNoticeSeconds"), 60, 0, 3600) * 1000L;
    return "supplies " + (ON ? "on" : "OFF") + ", lifelong " + LIFELONG + ", flask " + FLASK_CAP + ", pouch " + POUCH_CAP + ", raw " + POUCH_RAW;
  } catch (Throwable t) {
    return "supplies.properties could not be read (the defaults run): " + t;
  }
}""")
_SUPF = "@Skyy_SkyyCooking/supplies.properties:"
COOK_CFG_CATS = COOK_CFG_CATS + [("supplies", "Supplies")]
COOK_CFG_ROWS = COOK_CFG_ROWS + [
    ("supplies.on", "Potion Flask + Food Pouch", "supplies", "bool", "true", "", "", "", "", "live",
     "Off: the two items only open their page; nothing new goes in. Taking out still works.", "field:SupCfg.ON" + _SUPF + "supplies.on"),
    ("supplies.lifelong", "Lifelong Flask + Pouch", "supplies", "bool", "true", "", "", "", "", "live",
     "On: one each per profile - never dropped, stored or sold. /flask and /pouch give them back.", "field:SupCfg.LIFELONG" + _SUPF + "supplies.lifelong"),
    ("supplies.flaskCap", "Potion Flask size", "supplies", "int", "64", "1", "10000", "step=1", "", "live",
     "How many potions the Potion Flask holds. Lowering it never removes any.", "field:SupCfg.FLASK_CAP" + _SUPF + "supplies.flaskCap"),
    ("supplies.pouchCap", "Food Pouch size", "supplies", "int", "256", "1", "10000", "step=1", "", "live",
     "How many foods the Food Pouch holds. Lowering it never removes any.", "field:SupCfg.POUCH_CAP" + _SUPF + "supplies.pouchCap"),
    ("supplies.pouchRaw", "Raw food in the Pouch", "supplies", "bool", "false", "", "", "", "", "live",
     "On: raw meat, fish, eggs and cheese go in the Food Pouch too. Off: they stay in the Void.", "field:SupCfg.POUCH_RAW" + _SUPF + "supplies.pouchRaw"),
    ("supplies.fullNoticeSeconds", "Full notice every", "supplies", "int", "60", "0", "3600", "step=1", "s", "live",
     "How often a full Flask / Pouch is mentioned, in seconds. 0 = every time.", "field:SupCfg.FULL_NOTICE_MS*1000" + _SUPF + "supplies.fullNoticeSeconds"),
]
_sdp = CFG.parse_props(SUP_DEFAULTS_TEXT)
for _t in COOK_CFG_ROWS[-6:]:
    assert _t[0] in _sdp and _sdp[_t[0]] == _t[4], ("0.1.11: the supplies row default = its file line", _t[0])
CFG_KIT = CFG.emit(pool, PKG, MOD="SkyyCooking", TITLE="Cooking", VERSION=VERSION, NODE="skyycooking.admin", CATS=COOK_CFG_CATS,
                   ROWS=COOK_CFG_ROWS, FILES=[COOK_FILE, "Skyy_SkyyCooking/sounds.properties", "Skyy_SkyyCooking/supplies.properties"], NOTE="Also: /cookadmin reload re-reads the file; /cookadmin give and campfire hand out test dishes.",
                   RELOAD="CookCfg.load", KEEP=10, ITEMS=set(V_ITEMS) | set(G_ITEMS), DEFAULTS={"cooking.properties": DEFAULTS_TEXT, "supplies.properties": SUP_DEFAULTS_TEXT, "sounds.properties": '# SkyyCooking sounds (SkyWynn sound pass). Change them in game: SkyWynn Menu -> Server Setup -> Cooking -> Sounds,\n# or edit here and press Reload there. Each id is a vanilla sound event id (try one in game with /soundtest <id>);\n# an empty id = that sound off. Every player can also switch all SkyWynn sounds off for themselves in /settings.\nsounds.enabled=true\n# Meal done: A Cooking Bench craft gave a graded dish (not ingredients, not plain food).\nsound.meal=true\nsound.meal.id=SFX_Furnace_Bench_Processing_Complete\n'})

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

# ================= CookNcMig (0.1.13): the one-time maxXpPerMinute 1500000 -> 0 update (no XP caps) - a clone of CookXpMig (the same text step and History / change-log path), see the header =================
nmig = pool.makeClass(PKG + ".CookNcMig")
F(nmig, "public static final String KEY = \"maxXpPerMinute\";")
F(nmig, "public static final String OLD = %s;" % json.dumps(str(MAX_PER_MIN_OLD)))   # "1500000": every generated cooking.properties up to 0.1.12
F(nmig, "public static final String OLD2 = %s;" % json.dumps(str(MAX_PER_MIN_OLD)))  # the kit writes a long the same way
F(nmig, "public static final String NEW = %s;" % json.dumps(str(MAX_PER_MIN)))
F(nmig, "public static final String WHAT = \"before the 0.1.13 no XP caps update\";")
F(nmig, "public static final String MARK = %s;" % json.dumps(NC_MARK))
F(nmig, "public static final String MARK_ID = %s;" % json.dumps(NC_MARK_ID))
Mk(nmig, r"""
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
Mk(nmig, r"""
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
    kept = KEY + "=" + @PKG@.CfgRows.oneLine(eff) + " kept (custom) - the 0.1.13 default is " + NEW + " (no cap)";
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
# (CookNcMig.migrate below)
# setup(), right after CookMig.migrate and BEFORE CookCfg.load() + CfgPub.start: the file before this update becomes a History version
# (verified by CookMig.saved before the rewrite), the new text is written with the kit's atomicWrite (ISO-8859-1 bytes), one change-log
# line when the value changed, one INFO line (+ one for a kept custom value). Returns the INFO line(s) joined by \n ("" = nothing done: no
# file, marker already there, or a failure - WARN, file untouched, the next start tries again)
Mk(nmig, r"""
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
      @PKG@.CookCfg.warn("cooking.properties NOT updated for 0.1.13 (no XP caps): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(@PKG@.CookMig.logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String kept = (String) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "cooking.properties updated for 0.1.13: " + chg + " (Skyy 2026-10-18: no XP caps - 0 means no cap; the old file is in config-history; Server Setup -> Changes can undo it)";
    else if (kept != null) msg = "cooking.properties: maxXpPerMinute was changed by hand - kept, nothing changed (0.1.13 no XP caps marker added)";
    else if (r[4] == null) msg = "cooking.properties: no maxXpPerMinute line (the default " + NEW + " = no cap applies) - nothing changed (0.1.13 no XP caps marker added)";
    else msg = "cooking.properties: maxXpPerMinute is already " + NEW + " (no cap) - kept, nothing changed (0.1.13 no XP caps marker added)";
    @PKG@.CookCfg.info(msg);
    if (kept == null) return msg;
    @PKG@.CookCfg.info(kept);
    return msg + "\n" + kept;
  } catch (Throwable t) {
    @PKG@.CookCfg.warn("could not update cooking.properties for 0.1.13 (no XP caps; the file is used as it is): " + t);
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

# ================= CookP3Mig (0.1.15): the one-time Balance P3 Cooking XP update of an existing cooking.properties (CookIngMig's text step, see the header) =================
# CookMig's reviewed machinery for the xp.<ingredient> table lines: the same pure text step on the kit's parser, the same History / atomic write /
# change-log path (CookMig.kit / saved / logLine - same WHO), its own run-once marker XP_ING_MARK. Compiled after CookTblMig and before the
# plugin: setup() calls it right after CookTblMig.migrate, BEFORE CookCfg.load + CfgPub.start.
_P3K = list(P3_KEYS)
pmig = pool.makeClass(PKG + ".CookP3Mig")
F(pmig, "public static final String[] KEYS = %s;" % jstr_arr(["xp." + d for d in _P3K]))
F(pmig, "public static final String[] LOGKEYS = %s;" % jstr_arr(["xp[" + d + "]" for d in _P3K]))
F(pmig, "public static final String[] OLDS = %s;" % jstr_arr([str(XP[d]) for d in _P3K]))
F(pmig, "public static final String[] STOPS = %s;" % jstr_arr(["" for d in _P3K]))
F(pmig, "public static final String[] NEWS = %s;" % jstr_arr([str(XP_P3[d]) for d in _P3K]))
F(pmig, "public static final String[] HELP_OLD = %s;" % jstr_arr([_h for _h, _n in zip(XP_HELP_016, XP_HELP_P3) if _h != _n]))
F(pmig, "public static final String[] HELP_NEW = %s;" % jstr_arr([_n for _h, _n in zip(XP_HELP_016, XP_HELP_P3) if _h != _n]))
F(pmig, "public static final String WHAT = \"before the 0.1.15 Balance P3 Cooking XP update\";")
F(pmig, "public static final String MARK = %s;" % json.dumps(P3_MARK))
F(pmig, "public static final String MARK_ID = %s;" % json.dumps(P3_MARK_ID))
Mk(pmig, r"""
public static int idx(String key) {
  if (key == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(key)) return i;
  return -1;
}""")
Mk(pmig, r"""
public static boolean isOld(int i, String v) {
  if (i < 0 || v == null) return false;
  return v.equals(OLDS[i]) || (STOPS[i].length() > 0 && v.equals(STOPS[i]));
}""")
Mk(pmig, r"""
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
Mk(pmig, r"""
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
      kept.append(KEYS[i]).append("=").append(@PKG@.CfgRows.oneLine(v)).append(" kept (custom) - the 0.1.15 default is ").append(NEWS[i]);
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
Mk(pmig, r"""
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
      @PKG@.CookCfg.warn("cooking.properties NOT updated to the 0.1.15 Balance P3 Cooking XP: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(@PKG@.CookMig.logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String kept = (String) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "cooking.properties updated to the 0.1.15 Balance P3 Cooking XP (" + (rows.length / 3) + " XP line(s) on old defaults; dishes pay more for higher tier ingredients; the old file is in config-history; Server Setup -> Changes can undo each line)";
    else if (kept != null) msg = "cooking.properties: the XP lines were changed by hand - kept, nothing changed (0.1.15 Balance P3 Cooking XP marker added)";
    else msg = "cooking.properties: no XP line on an old default - nothing changed (0.1.15 Balance P3 Cooking XP marker added)";
    @PKG@.CookCfg.info(msg);
    if (kept == null) return msg;
    String[] ks = kept.split("\n");
    for (int i = 0; i < ks.length; i++) @PKG@.CookCfg.info(ks[i]);
    return msg + "\n" + kept;
  } catch (Throwable t) {
    @PKG@.CookCfg.warn("could not update cooking.properties to the 0.1.15 Balance P3 Cooking XP (the file is used as it is): " + t);
    return "";
  }
}""")

# ================= CookV3Mig (0.1.16): the one-time ING_TIER v3 Cooking XP update of an existing cooking.properties (CookP3Mig's text step, see the header) =================
# CookMig's reviewed machinery for the xp.<ingredient> table lines: the same pure text step on the kit's parser, the same History / atomic write /
# change-log path (CookMig.kit / saved / logLine - same WHO), its own run-once marker XP_ING_MARK. Compiled after CookTblMig and before the
# plugin: setup() calls it right after CookTblMig.migrate, BEFORE CookCfg.load + CfgPub.start.
_V3K = list(V3_KEYS)
vmig = pool.makeClass(PKG + ".CookV3Mig")
F(vmig, "public static final String[] KEYS = %s;" % jstr_arr(["xp." + d for d in _V3K]))
F(vmig, "public static final String[] LOGKEYS = %s;" % jstr_arr(["xp[" + d + "]" for d in _V3K]))
F(vmig, "public static final String[] OLDS = %s;" % jstr_arr([str(XP_P3[d]) for d in _V3K]))
F(vmig, "public static final String[] STOPS = %s;" % jstr_arr(["" for d in _V3K]))
F(vmig, "public static final String[] NEWS = %s;" % jstr_arr([str(XP_V3[d]) for d in _V3K]))
F(vmig, "public static final String[] HELP_OLD = %s;" % jstr_arr([_h for _h, _n in zip(XP_HELP_P3, XP_HELP_V3) if _h != _n]))
F(vmig, "public static final String[] HELP_NEW = %s;" % jstr_arr([_n for _h, _n in zip(XP_HELP_P3, XP_HELP_V3) if _h != _n]))
F(vmig, "public static final String WHAT = \"before the 0.1.16 ingredient tiers v3 Cooking XP update\";")
F(vmig, "public static final String MARK = %s;" % json.dumps(V3_MARK))
F(vmig, "public static final String MARK_ID = %s;" % json.dumps(V3_MARK_ID))
Mk(vmig, r"""
public static int idx(String key) {
  if (key == null) return -1;
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(key)) return i;
  return -1;
}""")
Mk(vmig, r"""
public static boolean isOld(int i, String v) {
  if (i < 0 || v == null) return false;
  return v.equals(OLDS[i]) || (STOPS[i].length() > 0 && v.equals(STOPS[i]));
}""")
Mk(vmig, r"""
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
Mk(vmig, r"""
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
      kept.append(KEYS[i]).append("=").append(@PKG@.CfgRows.oneLine(v)).append(" kept (custom) - the 0.1.16 default is ").append(NEWS[i]);
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
Mk(vmig, r"""
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
      @PKG@.CookCfg.warn("cooking.properties NOT updated to the 0.1.16 ingredient tiers v3 Cooking XP: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(@PKG@.CookMig.logLine(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String kept = (String) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "cooking.properties updated to the 0.1.16 ingredient tiers v3 Cooking XP (" + (rows.length / 3) + " XP line(s) on old defaults; every ingredient has a tier now - fruit and milk dishes pay their tier; the old file is in config-history; Server Setup -> Changes can undo each line)";
    else if (kept != null) msg = "cooking.properties: the XP lines were changed by hand - kept, nothing changed (0.1.16 ingredient tiers v3 Cooking XP marker added)";
    else msg = "cooking.properties: no XP line on an old default - nothing changed (0.1.16 ingredient tiers v3 Cooking XP marker added)";
    @PKG@.CookCfg.info(msg);
    if (kept == null) return msg;
    String[] ks = kept.split("\n");
    for (int i = 0; i < ks.length; i++) @PKG@.CookCfg.info(ks[i]);
    return msg + "\n" + kept;
  } catch (Throwable t) {
    @PKG@.CookCfg.warn("could not update cooking.properties to the 0.1.16 ingredient tiers v3 Cooking XP (the file is used as it is): " + t);
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
# 0.1.14 SKILL TREES 3: the 0.3 nodes SkyyTrees 0.4.0 no longer feeds (never asked again) and Prep Cook's new source, Forager's Larder
_DEAD14 = ['CBaker', 'CFed', 'CGrill', 'CIngr', 'CMaster', 'CPrep']
assert all(_d in [_n[0] for _n in NODES] for _d in _DEAD14 if _d != "CFed") and "CIngr" in _DEAD14
F(ck, "public static final boolean[] DEAD = new boolean[] { %s };" % ", ".join("true" if _n[0] in _DEAD14 else "false" for _n in NODES))
F(ck, "public static final int I_INGR = %d;" % [_n[0] for _n in NODES].index("CIngr"))
F(ck, "public static final String FL_KEY = \"Skill.Cooking.b2.r1a\";")
F(ck, "public static final int FL_MAX = 3;")
F(ck, "public static final String READS = \"Skill.Cooking.b2.r1a\";")
# the Forager's Larder rank (0 = none / not live / no SkyyTrees / a bad answer), clamped to its max
Mk(ck, """
public static int larder(java.util.UUID u) {
  if (u == null) return 0;
  try {
    Object f = bridge().get("tree:fn:level");
    if (!(f instanceof java.util.function.Function)) return 0;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, FL_KEY });
    if (!(r instanceof Number)) return 0;
    int v = ((Number) r).intValue();
    if (v <= 0) return 0;
    return v > FL_MAX ? FL_MAX : v;
  } catch (Throwable x) { return 0; }
}""")
Mk(ck, """
public static void reads(boolean on) {
  try {
    if (on) bridge().put("tree:reads:SkyyCooking", READS);
    else bridge().remove("tree:reads:SkyyCooking", READS);
  } catch (Throwable t) { }
}""")
# Cooking tree node levels from SkyyTrees (bridge tree:fn:level (UUID, "Cooking.<Id>") -> Integer), clamped to each node's max; 0.1.14: a
# DEAD node stays 0 (never asked), Prep Cook's slot = the Forager's Larder rank
Mk(ck, """
public static int[] tree(java.util.UUID u) {
  int n = @PKG@.CookCfg.NODES.length;
  int[] t = new int[n];
  Object f = null;
  try { f = bridge().get("tree:fn:level"); } catch (Throwable x) { f = null; }
  if (I_INGR >= 0 && I_INGR < n) t[I_INGR] = larder(u);
  if (!(f instanceof java.util.function.Function)) return t;
  for (int i = 0; i < n; i++) {
    if (DEAD[i]) continue;
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
    if (i == I_INGR) { v = (double) t[i] * p[i]; got = true; }          // 0.1.14: Forager's Larder rank x tree.CIngr.per (never Cooking.CIngr)
    else if (DEAD[i]) { got = true; }          // 0.1.14: a dead node (its level is 0 anyway)
    if (!got && f instanceof java.util.function.Function) {
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
    @PKG@.CookSnd.meal(pr, this.gave);   // 0.1.7 sound pass: meal done (a graded dish came out; the cook only)
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
  this.dishArg = withRequiredArg("dish", "Food_Pie_Meat, pie_meat, Skyy_Garden_Skewer, ... (every graded dish)", @ATY@.STRING);
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

# ================= 0.1.11 SUPPLIES JAVA (round FP1, research/Flask-Pouch-Spec.md; pasted by tools/cooking_0_1_11_patch.py) =================
# Classes (methods before callers): SupLog, SupDefs, SupData, SupStore, SupEng, FlaskOnce* / PouchOnce* (tools/skyyonce.py PREFIX MODE),
# SupOps, SupTask, SupSettle, SupCore, SupStartSys, SupTick, SupInvSys, SupReady, SupClaimsFn, SupCountsFn, HubBar (kit), SupPage,
# SupPageFactory, SupHubOpen, SupOpen, SupFlaskCmd, SupPouchCmd. Crash safety copies SkyySacks 0.8.17 VoidStore.appendJournal /
# readJournal / recover / settleDue / settle and SackPool.credit / paidHas / unpaid (see the header, point 3).
import skyyonce as ONCE
T.update({
    "INV": INV, "PRE": "com.hypixel.hytale.server.core.event.events.player.PlayerReadyEvent",
    "ICE": "com.hypixel.hytale.server.core.event.events.ecs.InventoryChangeEvent",
    "ICSE": "com.hypixel.hytale.server.core.modules.interaction.event.InteractionChainStartEvent",
    "ICHN": "com.hypixel.hytale.server.core.entity.InteractionChain",
    "IMOD": "com.hypixel.hytale.server.core.modules.interaction.InteractionModule",
    "IMGR": "com.hypixel.hytale.server.core.entity.InteractionManager",
    "ITYP": "com.hypixel.hytale.protocol.InteractionType",
    "ECC": "com.hypixel.hytale.server.core.entity.effect.EffectControllerComponent",
    "EFX": "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect",
    "MSC": "com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent",
    "OCU": "com.hypixel.hytale.server.core.modules.interaction.interaction.config.server.OpenCustomUIInteraction",
    "IDM": "com.hypixel.hytale.server.core.asset.type.item.config.metadata.ItemDisplayMetadata",
    "NTU": "com.hypixel.hytale.server.core.util.NotificationUtil",
    "NST": "com.hypixel.hytale.protocol.packets.interface_.NotificationStyle",
    "ISST": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackSlotTransaction",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
    "UCB": "com.hypixel.hytale.server.core.ui.builder.UICommandBuilder",
    "UEB": "com.hypixel.hytale.server.core.ui.builder.UIEventBuilder",
    "EVD": "com.hypixel.hytale.server.core.ui.builder.EventData",
    "BTY": "com.hypixel.hytale.protocol.packets.interface_.CustomUIEventBindingType",
    "LIFE": "com.hypixel.hytale.protocol.packets.interface_.CustomPageLifetime",
    "PAGE": "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage",
    "COLOK": SUI.COLOR["success"], "COLERR": SUI.COLOR["error"], "COLINFO": SUI.STATUS_INFO["gold"],
})
for c_, m_ in ((T["ICSE"], "getType"), (T["ICSE"], "getContext"), (T["ICSE"], "getChain"), (T["ICSE"], "setCancelled"),
               ("com.hypixel.hytale.server.core.entity.InteractionContext", "getHeldItem"), (T["ICHN"], "getType"), (T["IMOD"], "get"),
               (T["IMOD"], "getInteractionManagerComponent"), (T["IMGR"], "getChains"), (T["ITYP"], "Secondary"), (T["ECC"], "getComponentType"),
               (T["ECC"], "hasEffect"), (T["ECC"], "removeEffect"), (T["EFX"], "getAssetMap"),
               ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getIndex"), (T["MSC"], "getComponentType"),
               (T["MSC"], "getMovementStates"), (T["OCU"], "registerSimple"), (T["IDM"], "KEYED_CODEC"), (IS, "withMetadata"), (IS, "getMetadata"),
               (IS, "isEmpty"), (IC, "replaceItemStackInSlot"), (IC, "removeItemStackFromSlot"), (IC, "addItemStack"), (IC, "getCapacity"),
               (IC, "getItemStack"), (T["ISST"], "succeeded"), (T["NTU"], "sendNotification"), (PR, "getPacketHandler"), (PR, "getWorldUuid"),
               (PLA, "getPageManager"), (PLA, "isWaitingForClientReady"), (INV, "getStorage"), (INV, "getBackpack"), (INV, "getHotbar"),
               (INV, "getUtility"), (INV, "getTools"), (INV, "getItemInHand"), (T["HSV"], "SCHEDULED_EXECUTOR"), (T["PRE"], "getPlayerRef"),
               (PB, "getEventRegistry")):
    B.probe(pool, c_, m_)
assert pool.get(T["ICSE"]).subtypeOf(pool.get(CEV)), "0.1.11: the chain start event is cancellable (FP0)"
assert "crouching" in [str(f_.getName()) for f_ in pool.get("com.hypixel.hytale.protocol.MovementStates").getFields()], "0.1.11: MovementStates.crouching"
assert "Default" in [str(f_.getName()) for f_ in pool.get(T["NST"]).getFields()], "0.1.11: NotificationStyle.Default"


def sup_F(c, s):
    try:
        c.addField(CtField.make(jsrc(s), c))
    except Exception as e:
        raise SystemExit("0.1.11 field failed in %s:\n%s\n---\n%s" % (c.getName(), e, jsrc(s)[:600]))


def sup_Mr(c, src):
    try:
        c.addMethod(CtNewMethod.make(src, c))
    except Exception as e:
        raise SystemExit("0.1.11 compile failed in %s:\n%s\n---\n%s" % (c.getName(), e, src[:4000]))


def sup_M(c, s):
    sup_Mr(c, jsrc(s))


def sup_C(c, s):
    try:
        c.addConstructor(CtNewConstructor.make(jsrc(s), c))
    except Exception as e:
        raise SystemExit("0.1.11 constructor failed in %s:\n%s\n---\n%s" % (c.getName(), e, jsrc(s)[:1500]))


def smk(name, sup=None, iface=None):
    c = pool.makeClass(PKG + "." + name, pool.get(sup)) if sup else pool.makeClass(PKG + "." + name)
    if iface:
        c.addInterface(pool.get(iface))
    return c


def sjarr(xs):
    return "new String[] { %s }" % ", ".join(json.dumps(x) for x in xs)


SUP_CLASSES = [supc]   # SupCfg (made before the config kit binds its fields)
# ---------------------------------------------------------------- SupLog: log, chat, popup, bridge, busy
slog = smk("SupLog")
SUP_CLASSES.append(slog)
sup_F(slog, "public static volatile @LOG@ LOG;")
sup_F(slog, "public static final java.util.concurrent.ConcurrentHashMap ONCE = new java.util.concurrent.ConcurrentHashMap();")
sup_F(slog, "public static final java.util.concurrent.ConcurrentHashMap TOLD = new java.util.concurrent.ConcurrentHashMap();")
sup_F(slog, 'public static final String OK = "@COLOK@";')
sup_F(slog, 'public static final String ERR = "@COLERR@";')
sup_F(slog, 'public static final String INFO = "@COLINFO@";')
sup_M(slog, r"""
public static void info(String s) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyCooking] Supplies: " + s); } catch (Throwable t) { }
}""")
sup_M(slog, r"""
public static void warn(String s) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyCooking] Supplies: " + s); } catch (Throwable t) { }
}""")
sup_M(slog, r"""
public static void warnOnce(String k, String s) {
  if (ONCE.putIfAbsent(k, Boolean.TRUE) == null) warn(s + " (logged once)");
}""")
sup_M(slog, r"""
public static java.util.Map bridge() { return @PKG@.Cook.bridge(); }""")
sup_M(slog, r"""
public static boolean busy(java.util.UUID u) {
  if (u == null) return true;
  try { return bridge().get("profile:busy:" + u.toString()) != null; } catch (Throwable t) { return false; }
}""")
sup_M(slog, r"""
public static void tell(@PR@ pr, String s, String col) {
  try { if (pr != null) pr.sendMessage(@MSG@.raw(s).color(col)); } catch (Throwable t) { }
}""")
# at most once per ms per player and key (chat / popup spam guard)
sup_M(slog, r"""
public static boolean due(java.util.UUID u, String key, long ms) {
  if (u == null) return false;
  String k = u.toString() + ":" + key;
  long now = System.currentTimeMillis();
  Long last = (Long) TOLD.get(k);
  if (last != null && now - last.longValue() < ms) return false;
  TOLD.put(k, Long.valueOf(now));
  return true;
}""")
sup_M(slog, r"""
public static void pop(@PR@ pr, String title, String body) {
  if (pr == null) return;
  try { @NTU@.sendNotification(pr.getPacketHandler(), @MSG@.raw(title), @MSG@.raw(body), @NST@.Default); }
  catch (Throwable t) { tell(pr, "[Cooking] " + title + " - " + body, INFO); }
}""")

# ---------------------------------------------------------------- SupDefs: the build-time tables (worst first) + pure id logic
sdef = smk("SupDefs")
SUP_CLASSES.append(sdef)
sup_F(sdef, 'public static final String FPRE = "%s";' % SUP_FPRE)
sup_F(sdef, 'public static final String PPRE = "%s";' % SUP_PPRE)
sup_F(sdef, 'public static final String FEMPTY = "%s";' % SUP_FEMPTY)
sup_F(sdef, 'public static final String PEMPTY = "%s";' % SUP_PEMPTY)
sup_F(sdef, 'public static final String MARK = "%s";' % SUP_MARK)
sup_F(sdef, 'public static final String MARK_E = "%s";' % SUP_MARK_E)
sup_F(sdef, "public static final String[] FSRC = %s;" % sjarr([e["src"] for e in SUP_F]))
sup_F(sdef, "public static final String[] FNAME = %s;" % sjarr([e["name"] for e in SUP_F]))
sup_F(sdef, "public static final String[] FDESC = %s;" % sjarr([e["desc"] for e in SUP_F]))
sup_F(sdef, "public static final String[] FCOL = %s;" % sjarr([SUI.QUALITY.get(e["q"], SUI.QUALITY["Common"]) for e in SUP_F]))
sup_F(sdef, "public static final String[] PSRC = %s;" % sjarr([e["src"] for e in SUP_P]))
sup_F(sdef, "public static final String[] PNAME = %s;" % sjarr([e["name"] for e in SUP_P]))
sup_F(sdef, "public static final String[] PDESC = %s;" % sjarr([e["desc"] for e in SUP_P]))
sup_F(sdef, "public static final String[] PCOL = %s;" % sjarr([SUI.QUALITY.get(e["q"], SUI.QUALITY["Common"]) for e in SUP_P]))
sup_F(sdef, "public static final boolean[] PRAW = new boolean[] { %s };" % ", ".join("true" if e["raw"] else "false" for e in SUP_P))
sup_F(sdef, "public static volatile java.util.HashMap IX0 = null;")
sup_F(sdef, "public static volatile java.util.HashMap IX1 = null;")
sup_M(sdef, r"""
public static java.util.HashMap mk(String[] a) {
  java.util.HashMap m = new java.util.HashMap();
  for (int i = 0; i < a.length; i++) m.put(a[i], Integer.valueOf(i));
  return m;
}""")
sup_M(sdef, r"""
public static String[] srcs(int k) { return k == 0 ? FSRC : PSRC; }""")
sup_M(sdef, r"""
public static int idx(int k, String src) {
  if (src == null) return -1;
  java.util.HashMap m = k == 0 ? IX0 : IX1;
  if (m == null) {
    m = mk(srcs(k));
    if (k == 0) IX0 = m; else IX1 = m;
  }
  Object o = m.get(src);
  return o == null ? -1 : ((Integer) o).intValue();
}""")
sup_M(sdef, r"""
public static String name(int k, String src) {
  int i = idx(k, src);
  if (i < 0) return String.valueOf(src);
  return k == 0 ? FNAME[i] : PNAME[i];
}""")
sup_M(sdef, r"""
public static String desc(int k, String src) {
  int i = idx(k, src);
  if (i < 0) return "";
  return k == 0 ? FDESC[i] : PDESC[i];
}""")
sup_M(sdef, r"""
public static String col(int k, String src) {
  int i = idx(k, src);
  if (i < 0) return k == 0 ? FCOL[0] : PCOL[0];
  return k == 0 ? FCOL[i] : PCOL[i];
}""")
# 0 = a Flask id, 1 = a Pouch id, -1 = not ours
sup_M(sdef, r"""
public static int kindOf(String id) {
  if (id == null) return -1;
  if (id.startsWith(FPRE)) return 0;
  if (id.startsWith(PPRE)) return 1;
  return -1;
}""")
# the source a loaded id carries; "" = the Empty id; null = not ours / unknown shape
sup_M(sdef, r"""
public static String srcOf(String id) {
  int k = kindOf(id);
  if (k < 0) return null;
  String rest = id.substring((k == 0 ? FPRE : PPRE).length());
  if (rest.equals("Empty")) return "";
  if (!rest.startsWith("V_") || rest.length() < 3) return null;
  return rest.substring(2);
}""")
sup_M(sdef, r"""
public static String loadedId(int k, String src) {
  if (src == null || src.length() == 0) return k == 0 ? FEMPTY : PEMPTY;
  return (k == 0 ? FPRE : PPRE) + "V_" + src;
}""")
# the store an id may fill now (0 flask, 1 pouch, -1 none); raw snacks only with supplies.pouchRaw
sup_M(sdef, r"""
public static int fillKind(String id) {
  if (id == null) return -1;
  if (idx(0, id) >= 0) return 0;
  int i = idx(1, id);
  if (i < 0) return -1;
  if (PRAW[i] && !@PKG@.SupCfg.POUCH_RAW) return -1;
  return 1;
}""")
sup_M(sdef, r"""
public static boolean isRawSrc(int k, String src) { int i = idx(1, src); return k == 1 && i >= 0 && PRAW[i]; }""")
sup_M(sdef, r"""
public static String kindName(int k) { return k == 0 ? "Potion Flask" : "Food Pouch"; }""")
sup_M(sdef, r"""
public static String cmd(int k) { return k == 0 ? "/flask" : "/pouch"; }""")
sup_M(sdef, r"""
public static String what(int k) { return k == 0 ? "healing potions" : "cooked food"; }""")

# ---------------------------------------------------------------- SupData: one profile's store (memory; world thread writes, any thread reads)
sdat = smk("SupData")
SUP_CLASSES.append(sdat)
for _d in ("public String key;", "public java.util.concurrent.ConcurrentHashMap f;", "public java.util.concurrent.ConcurrentHashMap p;",
           "public java.util.concurrent.ConcurrentHashMap skip;", "public volatile boolean fAuto;", "public volatile boolean pAuto;",
           "public volatile boolean givenF;", "public volatile boolean givenP;", "public volatile boolean ready;", "public volatile boolean bad;",
           "public volatile long fTot;", "public volatile long pTot;", "public java.util.LinkedHashMap res;", "public java.util.HashSet paid;",
           "public boolean snapped;", "public volatile long ver;", "public volatile long saved;"):
    sup_F(sdat, _d)
sup_C(sdat, r"""
public SupData(String k) {
  this.key = k;
  this.f = new java.util.concurrent.ConcurrentHashMap();
  this.p = new java.util.concurrent.ConcurrentHashMap();
  this.skip = new java.util.concurrent.ConcurrentHashMap();
  this.fAuto = true; this.pAuto = true; this.givenF = false; this.givenP = false; this.ready = false; this.bad = false;
  this.fTot = 0L; this.pTot = 0L; this.res = new java.util.LinkedHashMap(); this.paid = new java.util.HashSet(); this.snapped = false; this.ver = 0L; this.saved = 0L;
}""")
sup_M(sdat, r"""
public java.util.concurrent.ConcurrentHashMap map(int k) { return k == 0 ? this.f : this.p; }""")
sup_M(sdat, r"""
public long get(int k, String src) {
  if (src == null) return 0L;
  Object o = map(k).get(src);
  return o instanceof Long ? ((Long) o).longValue() : 0L;
}""")
sup_M(sdat, r"""
public long tot(int k) { return k == 0 ? this.fTot : this.pTot; }""")
sup_M(sdat, r"""
public void retot() {
  long a = 0L;
  java.util.Iterator it = this.f.values().iterator();
  while (it.hasNext()) a = a + ((Long) it.next()).longValue();
  long b = 0L;
  it = this.p.values().iterator();
  while (it.hasNext()) b = b + ((Long) it.next()).longValue();
  this.fTot = a;
  this.pTot = b;
}""")
# +d (or -d); never below 0 (answers what could not be taken)
sup_M(sdat, r"""
public long add(int k, String src, long d) {
  long n = get(k, src) + d;
  long short_ = 0L;
  if (n < 0L) { short_ = -n; n = 0L; }
  if (n == 0L) map(k).remove(src);
  else map(k).put(src, Long.valueOf(n));
  retot();
  this.ver = this.ver + 1L;
  return short_;
}""")
sup_M(sdat, r"""
public boolean auto(int k) { return k == 0 ? this.fAuto : this.pAuto; }""")
sup_M(sdat, r"""
public void setAuto(int k, boolean v) { if (k == 0) this.fAuto = v; else this.pAuto = v; this.ver = this.ver + 1L; }""")
sup_M(sdat, r"""
public boolean given(int k) { return k == 0 ? this.givenF : this.givenP; }""")
sup_M(sdat, r"""
public void setGiven(int k) { if (k == 0) this.givenF = true; else this.givenP = true; this.ver = this.ver + 1L; }""")
sup_M(sdat, r"""
public void touch() { this.ver = this.ver + 1L; }""")
sup_M(sdat, r"""
public boolean isDirty() { return this.ver != this.saved; }""")
sup_M(sdat, r"""
public boolean skipped(String src) { return src != null && this.skip.containsKey(src); }""")
# the next item a right click uses: the first of the build-time order (worst first) the store holds
sup_M(sdat, r"""
public String next(int k) {
  String[] a = @PKG@.SupDefs.srcs(k);
  for (int i = 0; i < a.length; i++) if (get(k, a[i]) > 0L) return a[i];
  return null;
}""")
sup_M(sdat, r"""
public int kinds(int k) {
  String[] a = @PKG@.SupDefs.srcs(k);
  int n = 0;
  for (int i = 0; i < a.length; i++) if (get(k, a[i]) > 0L) n++;
  return n;
}""")

# ---------------------------------------------------------------- SupStore: files, journal, open entries, per-player runtime maps
ssto = smk("SupStore")
SUP_CLASSES.append(ssto)
for _d in ("public static volatile java.nio.file.Path DIR = null;",
           "public static final java.util.concurrent.ConcurrentHashMap DATA = new java.util.concurrent.ConcurrentHashMap();",   # pkey -> SupData
           # seq -> Object[] { String kind C/T, String pkey, Integer store, String id, Long qty, Long n0, Long timeMs, Boolean thisJvm }
           "public static final java.util.concurrent.ConcurrentHashMap OPEN = new java.util.concurrent.ConcurrentHashMap();",
           # uuid -> Object[] { Integer store, String id, Object chain, Long t0, Long goneSince, String seq, String pkey }
           "public static final java.util.concurrent.ConcurrentHashMap RES = new java.util.concurrent.ConcurrentHashMap();",
           "public static final java.util.concurrent.ConcurrentHashMap SYNC = new java.util.concurrent.ConcurrentHashMap();",    # uuid -> TRUE
           "public static final java.util.concurrent.ConcurrentHashMap WATCH = new java.util.concurrent.ConcurrentHashMap();",   # uuid -> Object[] { Long t, Integer store }
           "public static final java.util.concurrent.ConcurrentHashMap PEND = new java.util.concurrent.ConcurrentHashMap();",    # uuid -> TRUE (a task is queued)
           "public static final java.util.concurrent.atomic.AtomicLong SEQ = new java.util.concurrent.atomic.AtomicLong(0L);",
           # 0 fills, 1 takes, 2 uses, 3 returns, 4 reserves, 5 cancels, 6 free uses, 7 recovered, 8 save failures, 9 settled, 10 tasks
           "public static final java.util.concurrent.atomic.AtomicLongArray N = new java.util.concurrent.atomic.AtomicLongArray(11);",
           "public static volatile long SETTLE_MS = 30000L;", "public static volatile int HIST_KEEP = 10;"):
    sup_F(ssto, _d)
sup_F(ssto, "public static final java.util.concurrent.ConcurrentHashMap MUTE = new java.util.concurrent.ConcurrentHashMap();")   # pkey|id -> Long until (Take)
sup_F(ssto, "public static volatile long MUTE_MS = 60000L;")
# Skyy (the Void, same wish): "make it so, if you click take out, the auto store doesn't put it back in automatically." - a Take keeps
# that id out of auto-fill (and supply:fn:claims) for MUTE_MS; Put all in still takes it
sup_M(ssto, r"""
public static void mute(String key, String id) { MUTE.put(key + "|" + id, Long.valueOf(System.currentTimeMillis() + MUTE_MS)); }""")
sup_M(ssto, r"""
public static boolean muted(String key, String id) {
  if (key == null || id == null || MUTE.isEmpty()) return false;
  Object o = MUTE.get(key + "|" + id);
  if (!(o instanceof Long)) return false;
  if (((Long) o).longValue() > System.currentTimeMillis()) return true;
  MUTE.remove(key + "|" + id);
  return false;
}""")
sup_M(ssto, r"""
public static String nextSeq() { return "s" + Long.toString(System.currentTimeMillis(), 36) + "n" + SEQ.incrementAndGet(); }""")
sup_M(ssto, r"""
public static String clean(String s) {
  if (s == null) return "";
  return s.replace('|', '/').replace('\n', ' ').replace('\r', ' ');
}""")
sup_M(ssto, r"""
public static String safeKey(String k) {
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < k.length() && i < 80; i++) {
    char c = k.charAt(i);
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '-') sb.append(c); else sb.append('_');
  }
  return sb.toString();
}""")
sup_M(ssto, r"""
public static String line(String kind, String seq, String key, int store, String id, long qty, long n0, String text) {
  return kind + "|" + seq + "|" + clean(key) + "|" + store + "|" + clean(id) + "|" + qty + "|" + n0 + "|" + System.currentTimeMillis() + "|" + clean(text);
}""")
# THE journal append: one line, flushed + fsynced (SkyySacks VoidStore.appendJournal); false = the caller does not move anything
sup_M(ssto, r"""
public static synchronized boolean append(String line) {
  if (DIR == null) return false;
  try {
    java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
    java.io.FileOutputStream out = new java.io.FileOutputStream(DIR.resolve("journal.log").toFile(), true);
    try { out.write((line + "\n").getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
    return true;
  } catch (Throwable t) {
    @PKG@.SupLog.warnOnce("journal", "could not write supplies/journal.log - that move was not done: " + t);
    return false;
  }
}""")
sup_M(ssto, r"""
public static void jopen(String seq, String kind, String key, int store, String id, long qty, long n0) {
  OPEN.put(seq, new Object[] { kind, key, Integer.valueOf(store), id, Long.valueOf(qty), Long.valueOf(n0), Long.valueOf(System.currentTimeMillis()), Boolean.TRUE });
}""")
sup_M(ssto, r"""
public static void amend(String seq, long qty) {
  Object[] e = (Object[]) OPEN.get(seq);
  if (e != null) e[4] = Long.valueOf(qty);
}""")
sup_M(ssto, r"""
public static long num(String s, long def) {
  try { return Long.parseLong(s.trim()); } catch (Throwable t) { return def; }
}""")
# start-up: every C / T line without its D / X is an OPEN entry of an earlier run (recovered on that profile's first task); a journal
# above 4 MB moves to journal-<stamp>.old and the open entries are written again into the new one (nothing is deleted)
sup_M(ssto, r"""
public static int readJournal() {
  if (DIR == null) return 0;
  java.nio.file.Path f = DIR.resolve("journal.log");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return 0;
    java.util.List lines = java.nio.file.Files.readAllLines(f, java.nio.charset.StandardCharsets.UTF_8);
    for (int i = 0; i < lines.size(); i++) {
      String ln = ((String) lines.get(i)).trim();
      if (ln.length() == 0 || ln.startsWith("#")) continue;
      String[] a = ln.split("\\|", -1);
      if (a.length < 2) continue;
      if ((a[0].equals("C") || a[0].equals("T")) && a.length >= 9) {
        OPEN.put(a[1], new Object[] { a[0], a[2], Integer.valueOf((int) num(a[3], 0L)), a[4], Long.valueOf(num(a[5], 0L)), Long.valueOf(num(a[6], 0L)), Long.valueOf(num(a[7], 0L)), Boolean.FALSE });
      } else if (a[0].equals("Q") && a.length >= 6) {
        Object[] e = (Object[]) OPEN.get(a[1]);
        if (e != null) e[4] = Long.valueOf(num(a[5], 0L));
      } else if (a[0].equals("D") || a[0].equals("X")) {
        OPEN.remove(a[1]);
      }
    }
    if (java.nio.file.Files.size(f) > 4000000L) {
      String stamp = new java.text.SimpleDateFormat("yyyyMMdd-HHmmss").format(new java.util.Date());
      java.nio.file.Files.move(f, DIR.resolve("journal-" + stamp + ".old"), new java.nio.file.CopyOption[0]);
      append("# journal continued from journal-" + stamp + ".old - the entries still open are copied below");
      java.util.Iterator it = OPEN.entrySet().iterator();
      while (it.hasNext()) {
        java.util.Map.Entry me = (java.util.Map.Entry) it.next();
        Object[] e = (Object[]) me.getValue();
        append(e[0] + "|" + me.getKey() + "|" + e[1] + "|" + e[2] + "|" + e[3] + "|" + e[4] + "|" + e[5] + "|" + e[6] + "|carried over (still open)");
      }
    }
    return OPEN.size();
  } catch (Throwable t) {
    @PKG@.SupLog.warn("could not read supplies/journal.log (" + t + ") - open entries of the last run are not recovered");
    return -1;
  }
}""")
sup_M(ssto, r"""
public static java.nio.file.Path fileOf(String key) { return DIR.resolve(safeKey(key) + ".properties"); }""")
# History copy of the store file before its first write of a session (fsynced, read back; newest HIST_KEEP per profile kept)
sup_M(ssto, r"""
public static boolean snapshot(@PKG@.SupData d) {
  if (d.snapped) return true;
  try {
    java.nio.file.Path f = fileOf(d.key);
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.nio.file.Path hd = DIR.resolve("history");
      java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
      String stamp = new java.text.SimpleDateFormat("yyyyMMdd-HHmmss-SSS").format(new java.util.Date());
      byte[] raw = java.nio.file.Files.readAllBytes(f);
      java.nio.file.Path h = hd.resolve(safeKey(d.key) + "-" + stamp + ".properties");
      java.io.FileOutputStream out = new java.io.FileOutputStream(h.toFile());
      try { out.write(raw); out.flush(); out.getFD().sync(); } finally { out.close(); }
      if (!java.util.Arrays.equals(raw, java.nio.file.Files.readAllBytes(h))) throw new java.io.IOException("the History copy does not match");
      java.io.File[] all = hd.toFile().listFiles();
      java.util.ArrayList mine = new java.util.ArrayList();
      String pre = safeKey(d.key) + "-";
      for (int i = 0; all != null && i < all.length; i++) if (all[i].getName().startsWith(pre) && all[i].getName().endsWith(".properties")) mine.add(all[i].getName());
      java.util.Collections.sort(mine);
      for (int i = 0; i < mine.size() - HIST_KEEP; i++) java.nio.file.Files.deleteIfExists(hd.resolve((String) mine.get(i)));
    }
    d.snapped = true;
    return true;
  } catch (Throwable t) {
    @PKG@.SupLog.warnOnce("hist:" + d.key, "could not make the History copy of supplies/" + d.key + ".properties - nothing is written to it until it works: " + t);
    return false;
  }
}""")
sup_M(ssto, r"""
public static String text(@PKG@.SupData d) {
  java.util.TreeMap m = new java.util.TreeMap();
  m.put("flask.auto", String.valueOf(d.fAuto));
  m.put("pouch.auto", String.valueOf(d.pAuto));
  m.put("given.flask", String.valueOf(d.givenF));
  m.put("given.pouch", String.valueOf(d.givenP));
  java.util.Iterator it = d.f.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put("flask." + e.getKey(), String.valueOf(e.getValue())); }
  it = d.p.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put("pouch." + e.getKey(), String.valueOf(e.getValue())); }
  it = d.skip.keySet().iterator();
  while (it.hasNext()) m.put("skip." + it.next(), "true");
  it = d.res.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put("res." + e.getKey(), String.valueOf(e.getValue())); }
  StringBuilder pb = new StringBuilder();
  it = d.paid.iterator();
  while (it.hasNext()) {
    String s = (String) it.next();
    if (!OPEN.containsKey(s)) { it.remove(); continue; }
    if (pb.length() > 0) pb.append(' ');
    pb.append(s);
  }
  if (pb.length() > 0) m.put("paid", pb.toString());
  StringBuilder sb = new StringBuilder();
  sb.append("# SkyyCooking Supplies - the Potion Flask + Food Pouch store of profile ").append(d.key).append(" (written by the server; do not edit while it runs)\n");
  it = m.entrySet().iterator();
  while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); sb.append(e.getKey()).append('=').append(e.getValue()).append('\n'); }
  return sb.toString();
}""")
# atomic write: tmp + fsync + ATOMIC_MOVE (plain replace fallback), 5 x 20 ms retries; never over a file that could not be read
sup_M(ssto, r"""
public static boolean save(@PKG@.SupData d) {
  if (d == null || d.bad || DIR == null) return false;
  if (!snapshot(d)) { N.incrementAndGet(8); return false; }
  java.nio.file.Path f = fileOf(d.key);
  java.nio.file.Path tmp = DIR.resolve(safeKey(d.key) + ".properties.tmp");
  long v0 = d.ver;   // what this write holds; a change after it keeps the store dirty (LOW 10)
  String t = text(d);
  for (int a = 0; a < 5; a++) {
    try {
      java.nio.file.Files.createDirectories(DIR, new java.nio.file.attribute.FileAttribute[0]);
      java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
      try { out.write(t.getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
      try { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.ATOMIC_MOVE, java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
      catch (java.nio.file.AtomicMoveNotSupportedException x) { java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
      d.saved = v0;
      return true;
    } catch (java.nio.file.FileSystemException x) {
      try { Thread.sleep(20L); } catch (Throwable s) { }
    } catch (Throwable x) {
      @PKG@.SupLog.warnOnce("save:" + d.key, "could not write supplies/" + d.key + ".properties: " + x);
      break;
    }
  }
  N.incrementAndGet(8);
  return false;
}""")
# load one profile's store; open uses (res.*) of a run that stopped mid-drink are returned (journal B, then the file is written)
sup_M(ssto, r"""
public static boolean saveHard(@PKG@.SupData d, String what) {
  if (save(d)) return true;
  try { Thread.sleep(20L); } catch (Throwable t) { }
  if (save(d)) return true;
  @PKG@.SupLog.warn("COULD NOT WRITE supplies/" + (d == null ? "?" : d.key) + ".properties after " + what + " - the change is kept in memory and written with the next change (or at shutdown)");
  return false;
}""")
sup_M(ssto, r"""
public static @PKG@.SupData load(String key) {
  @PKG@.SupData d = new @PKG@.SupData(key);
  if (DIR == null) { d.bad = true; return d; }
  java.nio.file.Path f = fileOf(key);
  java.util.ArrayList back = new java.util.ArrayList();
  try {
    if (java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.util.Properties p = new java.util.Properties();
      java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
      try { p.load(new java.io.InputStreamReader(in, java.nio.charset.StandardCharsets.UTF_8)); } finally { in.close(); }
      java.util.Iterator it = p.stringPropertyNames().iterator();
      while (it.hasNext()) {
        String k = (String) it.next();
        String v = p.getProperty(k).trim();
        if (k.equals("flask.auto")) d.fAuto = !v.equals("false");
        else if (k.equals("pouch.auto")) d.pAuto = !v.equals("false");
        else if (k.equals("given.flask")) d.givenF = v.equals("true");
        else if (k.equals("given.pouch")) d.givenP = v.equals("true");
        else if (k.equals("paid")) { String[] a = v.split(" "); for (int i = 0; i < a.length; i++) if (a[i].length() > 0) d.paid.add(a[i]); }
        else if (k.startsWith("skip.")) { if (v.equals("true")) d.skip.put(k.substring(5), Boolean.TRUE); }
        else if (k.startsWith("res.")) back.add(new String[] { k.substring(4), v });
        else if (k.startsWith("flask.") || k.startsWith("pouch.")) {
          long n = num(v, -1L);
          if (n > 0L) (k.startsWith("flask.") ? d.f : d.p).put(k.substring(6), Long.valueOf(n));
        }
      }
    }
  } catch (Throwable t) {
    d.bad = true;
    @PKG@.SupLog.warn("supplies/" + key + ".properties could not be read - that profile's Flask / Pouch is paused and the file is never written over: " + t);
    return d;
  }
  d.retot();
  for (int i = 0; i < back.size(); i++) {
    String[] r = (String[]) back.get(i);
    int bar = r[1].indexOf('|');
    if (bar < 0) continue;
    int k = (int) num(r[1].substring(0, bar), 0L);
    String id = r[1].substring(bar + 1);
    d.add(k, id, 1L);
    append(line("B", r[0], key, k, id, 1L, 0L, "start-up: a use that never finished (the server stopped mid-drink) - 1 x " + id + " went back to the store (undo: none)"));
    N.incrementAndGet(3);
  }
  if (!back.isEmpty()) save(d);
  return d;
}""")
sup_M(ssto, r"""
public static @PKG@.SupData peek(String key) { return key == null ? null : (@PKG@.SupData) DATA.get(key); }""")
sup_M(ssto, r"""
public static @PKG@.SupData get(String key) {
  if (key == null) return null;
  @PKG@.SupData d = (@PKG@.SupData) DATA.get(key);
  if (d != null) return d;
  d = load(key);
  Object o = DATA.putIfAbsent(key, d);
  return o != null ? (@PKG@.SupData) o : d;
}""")
# the 10 s timer: an entry of THIS run 30 s old is settled (the engine saved the inventory meanwhile) - D line; a failed append retries
sup_M(ssto, r"""
public static int settle(long now) {
  int n = 0;
  java.util.Iterator it = OPEN.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry me = (java.util.Map.Entry) it.next();
    Object[] e = (Object[]) me.getValue();
    if (!((Boolean) e[7]).booleanValue() || ((Long) e[6]).longValue() + SETTLE_MS > now) continue;
    @PKG@.SupData dd = (@PKG@.SupData) DATA.get(e[1]);
    if (dd != null && dd.isDirty()) continue;   // the store file does not hold this change yet (a failed write): never settle it
    if (!append(line("D", (String) me.getKey(), (String) e[1], ((Integer) e[2]).intValue(), (String) e[3], ((Long) e[4]).longValue(), ((Long) e[5]).longValue(), "settled"))) break;
    it.remove();
    n++;
    N.incrementAndGet(9);
  }
  return n;
}""")

# ---------------------------------------------------------------- SupEng: engine helpers (world thread)
seng = smk("SupEng")
SUP_CLASSES.append(seng)
sup_F(seng, "public static volatile int MI_U = -1;")
sup_F(seng, "public static volatile int MI_E = -1;")
sup_M(seng, r"""
public static int markIndex(boolean empty) {
  int i = empty ? MI_E : MI_U;
  if (i >= 0) return i;
  try { i = @EFX@.getAssetMap().getIndex(empty ? @PKG@.SupDefs.MARK_E : @PKG@.SupDefs.MARK); } catch (Throwable t) { i = -1; }
  if (i >= 0) { if (empty) MI_E = i; else MI_U = i; }
  return i;
}""")
sup_M(seng, r"""
public static boolean takeMarker(@ST@ st, @REF@ r, @CAC@ acc, boolean empty) {
  int i = markIndex(empty);
  if (i < 0) return false;
  @ECC@ e = (@ECC@) st.getComponent(r, @ECC@.getComponentType());
  if (e == null || !e.hasEffect(i)) return false;
  e.removeEffect(r, i, acc);
  return true;
}""")
sup_M(seng, r"""
public static java.util.Map chains(@ST@ st, @REF@ r) {
  Object im = st.getComponent(r, @IMOD@.get().getInteractionManagerComponent());
  if (!(im instanceof @IMGR@)) return null;
  return (java.util.Map) ((@IMGR@) im).getChains();
}""")
sup_M(seng, r"""
public static boolean alive(@ST@ st, @REF@ r, Object chain) {
  if (chain == null) return false;
  java.util.Map m = chains(st, r);
  if (m == null) return false;
  java.util.Iterator it = m.values().iterator();
  while (it.hasNext()) if (it.next() == chain) return true;
  return false;
}""")
sup_M(seng, r"""
public static boolean secondaryRunning(@ST@ st, @REF@ r) {
  try {
    java.util.Map m = chains(st, r);
    if (m == null) return false;
    java.util.Iterator it = m.values().iterator();
    while (it.hasNext()) {
      Object c = it.next();
      if (c instanceof @ICHN@ && ((@ICHN@) c).getType() == @ITYP@.Secondary) return true;
    }
  } catch (Throwable t) { }
  return false;
}""")
sup_M(seng, r"""
public static boolean crouching(@ST@ st, @REF@ r) {
  try {
    @MSC@ m = (@MSC@) st.getComponent(r, @MSC@.getComponentType());
    return m != null && m.getMovementStates() != null && m.getMovementStates().crouching;
  } catch (Throwable t) { return false; }
}""")
sup_M(seng, r"""
public static @WLD@ worldOf(@ST@ st) {
  try { Object ext = st == null ? null : st.getExternalData(); return ext instanceof @EST@ ? ((@EST@) ext).getWorld() : null; } catch (Throwable t) { return null; }
}""")
# the player's sections: 0 hotbar, 1 storage, 2 backpack, 3 utility, 4 tools (moves only ever use 1 + 2; a give 1, 0, 2)
sup_M(seng, r"""
public static @IC@[] secs(@INV@ inv) {
  if (inv == null) return new @IC@[0];
  return new @IC@[] { inv.getHotbar(), inv.getStorage(), inv.getBackpack(), inv.getUtility(), inv.getTools() };
}""")
sup_M(seng, r"""
public static boolean plain(@IS@ s) {
  try { org.bson.BsonDocument d = s.getMetadata(); return d == null || d.isEmpty(); } catch (Throwable t) { return false; }
}""")
sup_M(seng, r"""
public static int qtyOf(@IC@ c, short sl, String id) {
  try {
    @IS@ s = c.getItemStack(sl);
    return s != null && !s.isEmpty() && id.equals(s.getItemId()) ? s.getQuantity() : 0;
  } catch (Throwable t) { return 0; }
}""")
# that id in hotbar + storage + backpack (every stack) - the before / after counts and the recovery rule
sup_M(seng, r"""
public static long countId(@IC@[] cs, String id) {
  long n = 0L;
  for (int c = 0; c < 3 && c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) n = n + qtyOf(cs[c], s, id);
  }
  return n;
}""")
sup_M(seng, r"""
public static int ours(@IC@[] cs, int k) {
  int n = 0;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[c].getItemStack(s);
      if (it != null && !it.isEmpty() && @PKG@.SupDefs.kindOf(it.getItemId()) == k) n++;
    }
  }
  return n;
}""")
sup_M(seng, r"""
public static String nameText(int k, @PKG@.SupData d) {
  return @PKG@.SupDefs.kindName(k) + " (" + (d == null ? 0L : d.tot(k)) + ")";
}""")
sup_M(seng, r"""
public static String descText(int k, @PKG@.SupData d) {
  String nx = d == null ? null : d.next(k);
  if (!@PKG@.SupCfg.ON) return "Switched off on this server. Crouch + right click: see what is inside.";
  if (nx == null) return "Empty - " + @PKG@.SupDefs.what(k) + " in your storage go in by themselves" + (d != null && d.auto(k) ? "" : " once Auto-fill is ON") + ". Crouch + right click: open.";
  int more = d.kinds(k) - 1;
  return "Next: " + @PKG@.SupDefs.name(k, nx) + (more > 0 ? " - then " + more + " more kind" + (more == 1 ? "" : "s") : "") + ". Right click: " + (k == 0 ? "drink" : "eat") + ". Crouch + right click: open.";
}""")
# the held copy's stack: the loaded id of the next item (Empty when there is none or the switch is off) + the ItemDisplay name / line
sup_M(seng, r"""
public static @IS@ display(int k, @PKG@.SupData d) {
  String nx = (d == null || !@PKG@.SupCfg.ON) ? null : d.next(k);
  @IS@ s = new @IS@(@PKG@.SupDefs.loadedId(k, nx), 1);
  return s.withMetadata(@IDM@.KEYED_CODEC, new @IDM@(@MSG@.raw(nameText(k, d)), @MSG@.raw(descText(k, d))));
}""")
sup_M(seng, r"""
public static boolean sameMeta(@IS@ a, @IS@ b) {
  try {
    org.bson.BsonDocument x = a.getMetadata();
    org.bson.BsonDocument y = b.getMetadata();
    if (x == null) return y == null || y.isEmpty();
    return x.equals(y);
  } catch (Throwable t) { return false; }
}""")
# every copy (any section) -> its display stack; only when the id or the text changed; compare-and-swap (FP0 replaceItemStackInSlot)
sup_M(seng, r"""
public static int sync(@IC@[] cs, @PKG@.SupData d) {
  int n = 0;
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ old = cs[c].getItemStack(s);
      if (old == null || old.isEmpty()) continue;
      int k = @PKG@.SupDefs.kindOf(old.getItemId());
      if (k < 0) continue;
      @IS@ want = display(k, d);
      if (want.getItemId().equals(old.getItemId()) && sameMeta(old, want)) continue;
      try {
        @ISST@ tx = cs[c].replaceItemStackInSlot(s, old, want);
        if (tx != null && tx.succeeded()) n++;
      } catch (Throwable t) { @PKG@.SupLog.warnOnce("sync", "the held Flask / Pouch could not be updated: " + t); }
    }
  }
  return n;
}""")

# ---------------------------------------------------------------- the lifelong items (tools/skyyonce.py PREFIX MODE)
LIFE_F = ONCE.emit(pool, PKG, "FlaskOnce", item=SUP_FEMPTY, name="Potion Flask", tag="[Cooking]", recall="/flask", mod="SkyyCooking",
                   on_expr=PKG + ".SupCfg.LIFELONG", info_col=SUI.COLOR["success"], warn_col=SUI.STATUS_INFO["gold"], item_prefix=SUP_FPRE)
LIFE_P = ONCE.emit(pool, PKG, "PouchOnce", item=SUP_PEMPTY, name="Food Pouch", tag="[Cooking]", recall="/pouch", mod="SkyyCooking",
                   on_expr=PKG + ".SupCfg.LIFELONG", info_col=SUI.COLOR["success"], warn_col=SUI.STATUS_INFO["gold"], item_prefix=SUP_PPRE)
SUP_LIFE_SETUP = LIFE_F["setup"] + LIFE_P["setup"]
SUP_LIFE_SHUTDOWN = LIFE_F["shutdown"] + LIFE_P["shutdown"]
SUP_CLASSES.extend(LIFE_F["classes"] + LIFE_P["classes"])

# ---------------------------------------------------------------- SupOps: recover, fill, take, first give, the sweep
sops = smk("SupOps")
SUP_CLASSES.append(sops)
sup_F(sops, "public static final java.util.concurrent.ConcurrentHashMap PKC = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> Object[] { epoch, pkey }
# the profile key + this mod's cache of it (supply:fn:claims answers only for the profile the cache knows)
sup_M(sops, r"""
public static String pkey(java.util.UUID u) {
  Object ep = null;
  try { ep = @PKG@.SupLog.bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { ep = null; }
  String k = @PKG@.Cook.pkey(u);
  PKC.put(u, new Object[] { ep, k });
  return k;
}""")
sup_M(sops, r"""
public static String cachedKey(java.util.UUID u) {
  Object[] c = (Object[]) PKC.get(u);
  if (c == null) return null;
  Object ep = null;
  try { ep = @PKG@.SupLog.bridge().get("profile:epoch:" + u.toString()); } catch (Throwable t) { ep = null; }
  if (c[0] == null ? ep != null : !c[0].equals(ep)) return null;
  return (String) c[1];
}""")
# the recovery rule (pure): was the move of an open entry saved with the inventory? C: count <= n0 - qty; T: count >= n0 + qty
sup_M(sops, r"""
public static boolean saved(String kind, long cnt, long n0, long q) {
  return kind.equals("C") ? cnt <= n0 - q : cnt >= n0 + q;
}""")
# apply one recovery decision; the paid flag after the save = "the store file holds this entry's effect" (idempotent if it runs again)
sup_M(sops, r"""
public static String settleOne(@PKG@.SupData d, String seq, Object[] e, boolean ok) {
  String kind = (String) e[0];
  int k = ((Integer) e[2]).intValue();
  String id = (String) e[3];
  long q = ((Long) e[4]).longValue();
  boolean paid = d.paid.contains(seq);
  String what;
  if (kind.equals("C")) {
    if (ok) { if (!paid) { d.add(k, id, q); d.paid.add(seq); } what = "kept: " + q + " x " + id + " left the inventory before the stop" + (paid ? "" : " - credited now"); }
    else { if (paid) { d.add(k, id, -q); d.paid.remove(seq); } what = "undone: the inventory came back with the " + q + " x " + id + (paid ? " - the store credit was taken back" : ""); }
  } else {
    if (ok) { if (!paid) { d.add(k, id, -q); d.paid.add(seq); } what = "kept: " + q + " x " + id + " reached the inventory before the stop" + (paid ? "" : " - debited now"); }
    else { if (paid) { d.add(k, id, q); d.paid.remove(seq); } what = "undone: the inventory came back without the " + q + " x " + id + (paid ? " - they went back to the store" : ""); }
  }
  return what;
}""")
# HIGH 1 (critic): the open entries of ONE (profile, id) are a chain in time order - state_0 = the first entry's n0, state_j = state_(j-1)
# + (C: -qty, T: +qty). The live count names the state the inventory was saved at: the largest j with count == state_j -> entries 1..j
# were saved, the rest undone. No j matches -> the per-entry rule (saved()). Pure (the harness calls it); -1 = no match.
sup_M(sops, r"""
public static int chainCut(java.util.ArrayList l, long cnt) {
  if (l == null || l.isEmpty()) return -1;
  Object[] e0 = (Object[]) ((Object[]) l.get(0))[1];
  long st = ((Long) e0[5]).longValue();
  int best = st == cnt ? 0 : -1;
  for (int x = 0; x < l.size(); x++) {
    Object[] e = (Object[]) ((Object[]) l.get(x))[1];
    long q = ((Long) e[4]).longValue();
    st = st + (((String) e[0]).equals("C") ? -q : q);
    if (st == cnt) best = x + 1;
  }
  return best;
}""")
# time order (then seq) - a plain insertion sort of { seq, entry } pairs
sup_M(sops, r"""
public static void byTime(java.util.ArrayList l) {
  for (int i = 1; i < l.size(); i++) {
    Object[] a = (Object[]) l.get(i);
    int j = i - 1;
    while (j >= 0) {
      Object[] b = (Object[]) l.get(j);
      long ta = ((Long) ((Object[]) a[1])[6]).longValue();
      long tb = ((Long) ((Object[]) b[1])[6]).longValue();
      if (tb < ta || (tb == ta && ((String) b[0]).compareTo((String) a[0]) <= 0)) break;
      l.set(j + 1, b);
      j--;
    }
    l.set(j + 1, a);
  }
}""")
sup_M(sops, r"""
public static int recover(@IC@[] cs, @PKG@.SupData d) {
  java.util.TreeMap byId = new java.util.TreeMap();
  java.util.Iterator it = @PKG@.SupStore.OPEN.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry me = (java.util.Map.Entry) it.next();
    Object[] e = (Object[]) me.getValue();
    if (!d.key.equals(e[1]) || ((Boolean) e[7]).booleanValue()) continue;
    java.util.ArrayList l = (java.util.ArrayList) byId.get(e[3]);
    if (l == null) { l = new java.util.ArrayList(); byId.put(e[3], l); }
    l.add(new Object[] { me.getKey(), e });
  }
  if (byId.isEmpty()) return 0;
  java.util.ArrayList done = new java.util.ArrayList();
  java.util.Iterator ii = byId.entrySet().iterator();
  while (ii.hasNext()) {
    java.util.Map.Entry ie = (java.util.Map.Entry) ii.next();
    java.util.ArrayList l = (java.util.ArrayList) ie.getValue();
    byTime(l);
    long cnt = @PKG@.SupEng.countId(cs, (String) ie.getKey());
    int cut = chainCut(l, cnt);
    for (int x = 0; x < l.size(); x++) {
      String seq = (String) ((Object[]) l.get(x))[0];
      Object[] e = (Object[]) ((Object[]) l.get(x))[1];
      boolean ok = cut >= 0 ? x < cut : saved((String) e[0], cnt, ((Long) e[5]).longValue(), ((Long) e[4]).longValue());
      String what = settleOne(d, seq, e, ok) + (cut >= 0 ? " (chain of " + l.size() + ", inventory " + cnt + ")" : " (per entry, inventory " + cnt + ")");
      done.add(new Object[] { seq, e, Boolean.valueOf(ok), what });
    }
  }
  if (!@PKG@.SupStore.save(d)) return -1;
  int n = 0;
  for (int i = 0; i < done.size(); i++) {
    Object[] x = (Object[]) done.get(i);
    Object[] e = (Object[]) x[1];
    if (!@PKG@.SupStore.append(@PKG@.SupStore.line(((Boolean) x[2]).booleanValue() ? "D" : "X", (String) x[0], d.key, ((Integer) e[2]).intValue(), (String) e[3], ((Long) e[4]).longValue(), ((Long) e[5]).longValue(), "recovered at start-up - " + x[3]))) continue;   // LOW 8: stays OPEN (+ paid) - the next run decides it again, the same way
    @PKG@.SupStore.OPEN.remove(x[0]);
    d.paid.remove(x[0]);
    n++;
    @PKG@.SupStore.N.incrementAndGet(7);
    @PKG@.SupLog.info("recovered " + x[0] + " (" + d.key + "): " + x[3]);
  }
  return n;
}""")
sup_M(sops, r"""
public static void fullNotice(@PR@ pr, @PKG@.SupData d, int k) {
  if (pr == null) return;
  long ms = @PKG@.SupCfg.FULL_NOTICE_MS;
  if (!@PKG@.SupLog.due(pr.getUuid(), "full" + k, ms <= 0L ? 1L : ms)) return;
  @PKG@.SupLog.pop(pr, "Your " + @PKG@.SupDefs.kindName(k) + " is full", d.tot(k) + " / " + @PKG@.SupCfg.cap(k) + " - the rest stays in your inventory.");
}""")
# THE FILL (auto-fill and Put all in): main storage + backpack ONLY (cs[1], cs[2]; never the hotbar), plain stacks of a fillable id;
# per stack: journal C (fsynced) -> remove -> read back -> credit only what left (Q amends a short removal) -> ONE store write at the end
sup_M(sops, r"""
public static int fill(@PR@ pr, @IC@[] cs, @PKG@.SupData d, int k, boolean manual) {
  if (d == null || d.bad || cs.length < 3) return 0;
  long cap = (long) @PKG@.SupCfg.cap(k);
  int moved = 0;
  boolean full = false;
  boolean stop = false;
  for (int c = 1; c <= 2 && !full && !stop; c++) {
    @IC@ ic = cs[c];
    if (ic == null) continue;
    short capn = ic.getCapacity();
    for (short s = 0; s < capn; s++) {
      @IS@ it = ic.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (@PKG@.SupDefs.fillKind(id) != k) continue;
      if (!manual && (d.skipped(id) || @PKG@.SupStore.muted(d.key, id))) continue;   // HIGH 2: a Take keeps it out for 60 s
      if (!@PKG@.SupEng.plain(it)) continue;
      long room = cap - d.tot(k);
      if (room <= 0L) { full = true; break; }
      int q = it.getQuantity();
      if ((long) q > room) q = (int) room;
      long n0 = @PKG@.SupEng.countId(cs, id);
      String seq = @PKG@.SupStore.nextSeq();
      if (!@PKG@.SupStore.append(@PKG@.SupStore.line("C", seq, d.key, k, id, (long) q, n0, (manual ? "put in" : "auto-fill") + ": " + q + " x " + id + " from " + (c == 1 ? "storage" : "backpack") + " slot " + s + " into the " + @PKG@.SupDefs.kindName(k) + " (undo: take " + q + " out on the Supplies page)"))) { stop = true; break; }
      @PKG@.SupStore.jopen(seq, "C", d.key, k, id, (long) q, n0);
      int b = @PKG@.SupEng.qtyOf(ic, s, id);
      try { ic.removeItemStackFromSlot(s, q); } catch (Throwable t) { }
      int r = b - @PKG@.SupEng.qtyOf(ic, s, id);
      if (r <= 0) {
        @PKG@.SupStore.append(@PKG@.SupStore.line("X", seq, d.key, k, id, (long) q, n0, "nothing left the slot - cancelled"));
        @PKG@.SupStore.OPEN.remove(seq);
        continue;
      }
      if (r != q) {
        @PKG@.SupStore.amend(seq, (long) r);
        @PKG@.SupStore.append(@PKG@.SupStore.line("Q", seq, d.key, k, id, (long) r, n0, "only " + r + " of " + q + " left the slot"));
      }
      d.add(k, id, (long) r);
      d.paid.add(seq);
      moved = moved + r;
      @PKG@.SupStore.N.incrementAndGet(0);
    }
  }
  if (moved > 0) @PKG@.SupStore.save(d);
  if (full) fullNotice(pr, d, k);
  return moved;
}""")
# TAKE OUT: journal T (fsynced) -> debit + paid in ONE store write -> give storage first (storage, hotbar, backpack), counted -> whatever
# did not fit goes back to the store (Q amends, X when nothing moved)
sup_M(sops, r"""
public static String take(@IC@[] cs, @PKG@.SupData d, int k, String id, long n) {
  if (d == null || d.bad || id == null || id.length() == 0 || cs.length < 3) return "-Pick an item first.";
  long have = d.get(k, id);
  long q = n < have ? n : have;
  if (q <= 0L) return "-None left.";
  if (q > 100000L) q = 100000L;
  long n0 = @PKG@.SupEng.countId(cs, id);
  String seq = @PKG@.SupStore.nextSeq();
  if (!@PKG@.SupStore.append(@PKG@.SupStore.line("T", seq, d.key, k, id, q, n0, "take out: " + q + " x " + id + " from the " + @PKG@.SupDefs.kindName(k) + " into the inventory (undo: put them back - Put all in)"))) return "-Could not write the journal - nothing was taken.";
  @PKG@.SupStore.jopen(seq, "T", d.key, k, id, q, n0);
  d.add(k, id, -q);
  d.paid.add(seq);
  if (!@PKG@.SupStore.save(d)) {
    d.add(k, id, q);
    d.paid.remove(seq);
    @PKG@.SupStore.append(@PKG@.SupStore.line("X", seq, d.key, k, id, q, n0, "the store could not be written - nothing taken"));
    @PKG@.SupStore.OPEN.remove(seq);
    return "-Your store could not be saved - nothing was taken.";
  }
  int[] order = new int[] { 1, 0, 2 };
  long left = q;
  for (int o = 0; o < order.length && left > 0L; o++) {
    @IC@ ic = cs[order[o]];
    if (ic == null) continue;
    long b = @PKG@.SupEng.countId(cs, id);
    try { ic.addItemStack(new @IS@(id, (int) left)); } catch (Throwable t) { @PKG@.SupLog.warnOnce("give", "adding to the inventory failed: " + t); }
    long got = @PKG@.SupEng.countId(cs, id) - b;
    if (got > 0L) left = left - got;
  }
  long given = q - left;
  if (left > 0L) {
    d.add(k, id, left);
    if (given <= 0L) {
      d.paid.remove(seq);
      @PKG@.SupStore.save(d);
      @PKG@.SupStore.append(@PKG@.SupStore.line("X", seq, d.key, k, id, q, n0, "no room in the inventory - nothing moved"));
      @PKG@.SupStore.OPEN.remove(seq);
      return "-No room in your inventory - nothing was taken.";
    }
    @PKG@.SupStore.amend(seq, given);
    @PKG@.SupStore.append(@PKG@.SupStore.line("Q", seq, d.key, k, id, given, n0, "only " + given + " of " + q + " fitted - the rest stayed in the store"));
    @PKG@.SupStore.save(d);
  }
  @PKG@.SupStore.N.incrementAndGet(1);
  @PKG@.SupStore.mute(d.key, id);
  return "+Took " + given + " x " + @PKG@.SupDefs.name(k, id) + (left > 0L ? " - no room for " + left + " more" : "") + ". It stays out of Auto-fill for now (Put all in puts it back).";
}""")
# the first give: each profile gets one of each ONCE (given.* marker; existing profiles too), storage first through the lifelong recall
sup_M(sops, r"""
public static void give(@PR@ pr, @INV@ inv, @PKG@.SupData d) {
  for (int k = 0; k < 2; k++) {
    if (d.given(k)) continue;
    String rr = k == 0 ? @PKG@.FlaskOnce.recall(pr, @PKG@.FlaskOnce.secs(inv)) : @PKG@.PouchOnce.recall(pr, @PKG@.PouchOnce.secs(inv));
    if ("+given".equals(rr) || "=have".equals(rr)) {
      d.setGiven(k);
      @PKG@.SupStore.save(d);
      @PKG@.SupStore.append(@PKG@.SupStore.line("G", @PKG@.SupStore.nextSeq(), d.key, k, @PKG@.SupDefs.loadedId(k, null), 1L, 0L, ("+given".equals(rr) ? "first " + @PKG@.SupDefs.kindName(k) + " given" : "the profile already had one") + " (undo: none - it is lifelong; " + @PKG@.SupDefs.cmd(k) + " gives it back)"));
      if ("+given".equals(rr)) @PKG@.SupLog.tell(pr, "[Cooking] You got a " + @PKG@.SupDefs.kindName(k) + " (in your storage - drag it to your hotbar). " + (k == 0 ? "Healing potions" : "Cooked food") + " you pick up go in by themselves; right click " + (k == 0 ? "drinks" : "eats") + " the weakest first. Crouch + right click opens it.", @PKG@.SupLog.OK);
    } else if ("-full".equals(rr) && @PKG@.SupLog.due(pr.getUuid(), "givefull" + k, 600000L)) {
      @PKG@.SupLog.tell(pr, "[Cooking] Your " + @PKG@.SupDefs.kindName(k) + " is waiting - make room in your inventory and type " + @PKG@.SupDefs.cmd(k) + ".", @PKG@.SupLog.INFO);
    }
  }
}""")
sup_M(sops, r"""
public static boolean syncNow(@ST@ st, @REF@ r, java.util.UUID u, @IC@[] cs, @PKG@.SupData d) {
  if (@PKG@.SupStore.RES.get(u) != null || @PKG@.SupEng.secondaryRunning(st, r)) { @PKG@.SupStore.SYNC.put(u, Boolean.TRUE); return false; }
  @PKG@.SupEng.sync(cs, d);
  return true;
}""")
# THE SWEEP (world thread, the player's own task): busy -> later; load + recover the profile's store; first gives; auto-fill; sync
sup_M(sops, r"""
public static String sweep(@PR@ pr, @PLA@ p, @ST@ st, @REF@ r) {
  java.util.UUID u = pr.getUuid();
  if (@PKG@.SupLog.busy(u)) return "busy";
  String k = pkey(u);
  @PKG@.SupData d = @PKG@.SupStore.get(k);
  if (d == null || d.bad) return "bad";
  @INV@ inv = p.getInventory();
  @IC@[] cs = @PKG@.SupEng.secs(inv);
  if (!d.ready) {
    if (recover(cs, d) < 0) return "busy";
    d.ready = true;
  }
  give(pr, inv, d);
  if (@PKG@.SupCfg.ON) {
    for (int kk = 0; kk < 2; kk++) if (d.auto(kk)) fill(pr, cs, d, kk, false);
  }
  syncNow(st, r, u, cs, d);
  return "ok";
}""")
sup_M(sops, r"""
public static java.util.ArrayList rows(@PKG@.SupData d, int k) {
  java.util.ArrayList l = new java.util.ArrayList();
  if (d == null) return l;
  String[] a = @PKG@.SupDefs.srcs(k);
  for (int i = 0; i < a.length; i++) if (d.get(k, a[i]) > 0L) l.add(a[i]);
  return l;
}""")
sup_M(sops, r"""
public static boolean anyFillable(@IC@[] cs, @PKG@.SupData d) {
  for (int c = 1; c <= 2 && c < cs.length; c++) {
    if (cs[c] == null) continue;
    short cap = cs[c].getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cs[c].getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      int k = @PKG@.SupDefs.fillKind(it.getItemId());
      if (k >= 0 && d.auto(k) && !d.skipped(it.getItemId()) && !@PKG@.SupStore.muted(d.key, it.getItemId())) return true;
    }
  }
  return false;
}""")

# ---------------------------------------------------------------- SupTask: ONE deduplicated world-thread task per player (the skyyonce pattern)
stask = smk("SupTask", None, "java.lang.Runnable")
SUP_CLASSES.append(stask)
for _d in ("public @PR@ pr;", "public @WLD@ world;", "public java.util.UUID wu;", "public int tries;"):
    sup_F(stask, _d)
sup_C(stask, "public SupTask(@PR@ pr, @WLD@ w, java.util.UUID wu, int tries) { this.pr = pr; this.world = w; this.wu = wu; this.tries = tries; }")
sup_M(stask, r"""
public static boolean schedule(@PR@ pr, @WLD@ w, long delay, int tries) {
  if (pr == null || w == null) return false;
  java.util.UUID u = null;
  try { u = pr.getUuid(); } catch (Throwable t) { return false; }
  if (u == null || @PKG@.SupStore.PEND.putIfAbsent(u, Boolean.TRUE) != null) return false;
  try {
    @PKG@.SupTask t = new @PKG@.SupTask(pr, w, pr.getWorldUuid(), tries);
    if (delay <= 0L) w.execute(t);
    else java.util.concurrent.CompletableFuture.delayedExecutor(delay, java.util.concurrent.TimeUnit.MILLISECONDS, (java.util.concurrent.Executor) w).execute(t);
    return true;
  } catch (Throwable x) { @PKG@.SupStore.PEND.remove(u); @PKG@.SupLog.warnOnce("sched", "a world task could not be queued: " + x); return false; }
}""")
sup_M(stask, r"""
public void run() {
  java.util.UUID u = null;
  try {
    u = this.pr.getUuid();
    @PKG@.SupStore.PEND.remove(u);
    if (!this.pr.isValid()) return;
    java.util.UUID nw = this.pr.getWorldUuid();
    if (nw == null || !nw.equals(this.wu)) return;
    @REF@ r = this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null || !st.isInThread()) return;
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null) return;
    @PKG@.SupStore.N.incrementAndGet(10);
    String res = p.isWaitingForClientReady() ? "busy" : @PKG@.SupOps.sweep(this.pr, p, st, r);
    if ("busy".equals(res) && this.tries < 30) schedule(this.pr, this.world, 2000L, this.tries + 1);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("task", "the Supplies world task failed: " + t); }
}""")
sset = smk("SupSettle", None, "java.lang.Runnable")
SUP_CLASSES.append(sset)
sup_C(sset, "public SupSettle() { }")
sup_M(sset, r"""
public void run() {
  try { @PKG@.SupStore.settle(System.currentTimeMillis()); } catch (Throwable t) { @PKG@.SupLog.warnOnce("settle", "the journal settle timer failed: " + t); }
}""")

# ---------------------------------------------------------------- SupCore: the use (reserve / commit / return) - the FP0 runtime
score = smk("SupCore")
SUP_CLASSES.append(score)
sup_M(score, r"""
public static boolean reserve(java.util.UUID u, @PKG@.SupData d, int k, String id, Object chain) {
  String seq = @PKG@.SupStore.nextSeq();
  d.add(k, id, -1L);
  d.res.put(seq, k + "|" + id);
  if (!@PKG@.SupStore.save(d)) { d.add(k, id, 1L); d.res.remove(seq); return false; }
  @PKG@.SupStore.append(@PKG@.SupStore.line("R", seq, d.key, k, id, 1L, 0L, "use: 1 x " + id + " reserved for a " + (k == 0 ? "drink" : "bite") + " (undo: it goes back when the use is let go, or at start-up)"));
  @PKG@.SupStore.RES.put(u, new Object[] { Integer.valueOf(k), id, chain, Long.valueOf(System.currentTimeMillis()), Long.valueOf(0L), seq, d.key });
  @PKG@.SupStore.N.incrementAndGet(4);
  return true;
}""")
sup_M(score, r"""
public static void commit(java.util.UUID u, Object[] res) {
  @PKG@.SupStore.RES.remove(u);
  @PKG@.SupData d = @PKG@.SupStore.peek((String) res[6]);
  if (d != null) {
    d.res.remove(res[5]);
    d.touch();
    @PKG@.SupStore.saveHard(d, "a use");
  }
  @PKG@.SupStore.append(@PKG@.SupStore.line("U", (String) res[5], (String) res[6], ((Integer) res[0]).intValue(), (String) res[1], 1L, 0L, "use: 1 x " + res[1] + " used (undo: none - it was drunk / eaten)"));
  @PKG@.SupStore.N.incrementAndGet(2);
  @PKG@.SupStore.SYNC.put(u, Boolean.TRUE);
}""")
sup_M(score, r"""
public static void giveBack(java.util.UUID u, Object[] res, String why) {
  @PKG@.SupStore.RES.remove(u);
  @PKG@.SupData d = @PKG@.SupStore.peek((String) res[6]);
  if (d != null) {
    d.res.remove(res[5]);
    d.add(((Integer) res[0]).intValue(), (String) res[1], 1L);
    @PKG@.SupStore.saveHard(d, "a returned use");
  }
  @PKG@.SupStore.append(@PKG@.SupStore.line("B", (String) res[5], (String) res[6], ((Integer) res[0]).intValue(), (String) res[1], 1L, 0L, "returned: " + why + " - 1 x " + res[1] + " back in the store (nothing used)"));
  @PKG@.SupStore.N.incrementAndGet(3);
  @PKG@.SupStore.SYNC.put(u, Boolean.TRUE);
}""")
sup_M(score, r"""
public static void onStart(@ICSE@ e, @REF@ r, @ST@ st, @CB@ buf) {
  if (!"Secondary".equals(String.valueOf(e.getType()))) return;
  @IS@ held = e.getContext() == null ? null : e.getContext().getHeldItem();
  String id = held == null || held.isEmpty() ? null : held.getItemId();
  int k = @PKG@.SupDefs.kindOf(id);
  if (k < 0) return;
  @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
  if (pr == null) return;
  java.util.UUID u = pr.getUuid();
  String src = @PKG@.SupDefs.srcOf(id);
  if (src == null) return;
  if (src.length() == 0) { @PKG@.SupStore.WATCH.put(u, new Object[] { Long.valueOf(System.currentTimeMillis()), Integer.valueOf(k) }); return; }
  if (@PKG@.SupEng.crouching(st, r)) return;
  if (@PKG@.Cook.creative(st, r)) return;
  Object[] res = (Object[]) @PKG@.SupStore.RES.get(u);
  if (res != null) {
    if (@PKG@.SupEng.takeMarker(st, r, (@CAC@) buf, false)) commit(u, res);
    else if (!@PKG@.SupEng.alive(st, r, res[2])) giveBack(u, res, "the last use ended before it finished");
    else { e.setCancelled(true); @PKG@.SupStore.N.incrementAndGet(5); return; }
  }
  if (!@PKG@.SupCfg.ON || @PKG@.SupLog.busy(u)) { e.setCancelled(true); @PKG@.SupStore.SYNC.put(u, Boolean.TRUE); return; }
  @PKG@.SupData d = @PKG@.SupStore.peek(@PKG@.SupOps.pkey(u));
  if (d == null || !d.ready || d.bad) {
    e.setCancelled(true);
    @PKG@.SupStore.N.incrementAndGet(5);
    @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0);
    return;
  }
  if (d.get(k, src) <= 0L) { e.setCancelled(true); @PKG@.SupStore.N.incrementAndGet(5); @PKG@.SupStore.SYNC.put(u, Boolean.TRUE); return; }
  if (!reserve(u, d, k, src, e.getChain())) { e.setCancelled(true); @PKG@.SupStore.N.incrementAndGet(5); }
}""")
sup_M(score, r"""
public static void emptyLine(@PR@ pr, int k) {
  if (!@PKG@.SupLog.due(pr.getUuid(), "empty" + k, 2000L)) return;
  @PKG@.SupData d = @PKG@.SupStore.peek(@PKG@.SupOps.cachedKey(pr.getUuid()));
  String nm = @PKG@.SupDefs.kindName(k);
  if (!@PKG@.SupCfg.ON) { @PKG@.SupLog.pop(pr, nm, "Switched off on this server. Crouch + right click to see what is inside."); return; }
  boolean auto = d == null || d.auto(k);
  @PKG@.SupLog.pop(pr, "Your " + nm + " is empty", (k == 0 ? "Healing potions go in by themselves" : "Cooked food goes in by itself") + (auto ? " (Auto-fill ON)" : " once Auto-fill is ON") + ". Crouch + right click to open it.");
}""")
sup_M(score, r"""
public static void tick(@REF@ r, @ST@ st, @CB@ cb, @PR@ pr) {
  java.util.UUID u = pr.getUuid();
  Object[] res = (Object[]) @PKG@.SupStore.RES.get(u);
  Object[] w = (Object[]) @PKG@.SupStore.WATCH.get(u);
  if (res == null && w == null && @PKG@.SupStore.SYNC.get(u) == null) return;
  long now = System.currentTimeMillis();
  if (res != null) {
    if (@PKG@.SupEng.takeMarker(st, r, (@CAC@) cb, false)) commit(u, res);
    else {
      long t0 = ((Long) res[3]).longValue();
      if (@PKG@.SupEng.alive(st, r, res[2]) && now - t0 < 30000L) res[4] = Long.valueOf(0L);
      else {
        long gone = ((Long) res[4]).longValue();
        if (gone == 0L) res[4] = Long.valueOf(now);
        else if (now - gone >= 250L) giveBack(u, res, "let go before it finished");
      }
    }
  }
  if (w != null) {
    if (@PKG@.SupEng.takeMarker(st, r, (@CAC@) cb, true)) { @PKG@.SupStore.WATCH.remove(u); emptyLine(pr, ((Integer) w[1]).intValue()); }
    else if (now - ((Long) w[0]).longValue() > 3000L) @PKG@.SupStore.WATCH.remove(u);
  }
  if (@PKG@.SupStore.SYNC.get(u) != null && @PKG@.SupStore.RES.get(u) == null && !@PKG@.SupEng.secondaryRunning(st, r)) {
    @PKG@.SupStore.SYNC.remove(u);
    if (!@PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0)) @PKG@.SupStore.SYNC.put(u, Boolean.TRUE);
  }
}""")

# ---------------------------------------------------------------- the four hooks (ONE registerSystem per class)
sss = smk("SupStartSys", EES)
SUP_CLASSES.append(sss)
sup_C(sss, "public SupStartSys() { super(@ICSE@.class); }")
sup_M(sss, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
sup_M(sss, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (chunk == null || !(ev instanceof @ICSE@)) return;
    @PKG@.SupCore.onStart((@ICSE@) ev, chunk.getReferenceTo(idx), st, buf);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("start", "the Flask / Pouch use hook failed: " + t); }
}""")
stk = smk("SupTick", "com.hypixel.hytale.component.system.tick.EntityTickingSystem")
SUP_CLASSES.append(stk)
sup_C(stk, "public SupTick() { super(); }")
sup_M(stk, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
sup_M(stk, "public boolean isParallel(int a, int b) { return false; }")
sup_M(stk, r"""
public void tick(float dt, int idx, @ACH@ chunk, @ST@ store, @CB@ cb) {
  try {
    if (chunk == null) return;
    if (@PKG@.SupStore.RES.isEmpty() && @PKG@.SupStore.SYNC.isEmpty() && @PKG@.SupStore.WATCH.isEmpty()) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) store.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.SupCore.tick(r, store, cb, pr);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("tick", "the Flask / Pouch tick failed: " + t); }
}""")
sinv = smk("SupInvSys", EES)
SUP_CLASSES.append(sinv)
sup_C(sinv, "public SupInvSys() { super(@ICE@.class); }")
sup_M(sinv, "public @QRY@ getQuery() { return (@QRY@) @PLA@.getComponentType(); }")
sup_M(sinv, r"""
public void handle(int idx, @ACH@ chunk, @ST@ st, @CB@ buf, @EV@ ev) {
  try {
    if (!(ev instanceof @ICE@)) return;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    java.util.UUID u = pr.getUuid();
    if (u == null || @PKG@.SupStore.PEND.containsKey(u)) return;
    String k = @PKG@.SupOps.cachedKey(u);
    @PKG@.SupData d = @PKG@.SupStore.peek(k);
    if (d == null || !d.ready || !d.givenF || !d.givenP) { @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0); return; }
    if (!@PKG@.SupCfg.ON || (!d.fAuto && !d.pAuto)) return;
    @PLA@ p = (@PLA@) chunk.getComponent(idx, @PLA@.getComponentType());
    if (p == null) return;
    if (@PKG@.SupOps.anyFillable(@PKG@.SupEng.secs(p.getInventory()), d)) @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("inv", "the Flask / Pouch inventory hook failed: " + t); }
}""")
srdy = smk("SupReady", None, "java.util.function.Consumer")
SUP_CLASSES.append(srdy)
sup_C(srdy, "public SupReady() { }")
sup_M(srdy, r"""
public void accept(Object o) {
  try {
    if (!(o instanceof @PRE@)) return;
    @REF@ r = ((@PRE@) o).getPlayerRef();
    if (r == null || !r.isValid()) return;
    @ST@ st = r.getStore();
    if (st == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;
    @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 1500L, 0);
  } catch (Throwable t) { @PKG@.SupLog.warnOnce("ready", "the ready hook failed: " + t); }
}""")

# ---------------------------------------------------------------- the bridge functions (plain java.lang types; memory only)
scl = smk("SupClaimsFn", None, "java.util.function.Function")
SUP_CLASSES.append(scl)
sup_C(scl, "public SupClaimsFn() { }")
sup_M(scl, r"""
public Object apply(Object o) {
  try {
    if (!@PKG@.SupCfg.ON || !(o instanceof Object[])) return Boolean.FALSE;
    Object[] a = (Object[]) o;
    if (a.length < 2 || !(a[0] instanceof java.util.UUID) || !(a[1] instanceof String)) return Boolean.FALSE;
    java.util.UUID u = (java.util.UUID) a[0];
    String id = (String) a[1];
    int k = @PKG@.SupDefs.fillKind(id);
    if (k < 0 || @PKG@.SupLog.busy(u)) return Boolean.FALSE;
    @PKG@.SupData d = @PKG@.SupStore.peek(@PKG@.SupOps.cachedKey(u));
    if (d == null || !d.ready || d.bad || !d.auto(k) || d.skipped(id) || @PKG@.SupStore.muted(d.key, id)) return Boolean.FALSE;
    return d.tot(k) < (long) @PKG@.SupCfg.cap(k) ? Boolean.TRUE : Boolean.FALSE;
  } catch (Throwable t) { return Boolean.FALSE; }
}""")
scn = smk("SupCountsFn", None, "java.util.function.Function")
SUP_CLASSES.append(scn)
sup_C(scn, "public SupCountsFn() { }")
sup_M(scn, r"""
public Object apply(Object o) {
  try {
    java.util.UUID u = o instanceof Object[] && ((Object[]) o).length > 0 ? (java.util.UUID) ((Object[]) o)[0] : (java.util.UUID) o;
    if (u == null || @PKG@.SupLog.busy(u)) return null;
    @PKG@.SupData d = @PKG@.SupStore.peek(@PKG@.SupOps.cachedKey(u));
    if (d == null || !d.ready || d.bad) return null;
    java.util.HashMap m = new java.util.HashMap();
    java.util.Iterator it = d.f.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put(e.getKey(), e.getValue()); }
    it = d.p.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); m.put(e.getKey(), e.getValue()); }
    return m;
  } catch (Throwable t) { return null; }
}""")

# ---------------------------------------------------------------- THE PAGE: Storage > Supplies (kit 1.7 hub page; Menu-Pattern 3)
shubb = SUI.install_hub_bar(pool, PKG + ".HubBar", CtField, CtNewMethod, row=True, page=True)
SUP_CLASSES.append(shubb)
_SHROW = [r_ for r_ in SUI.HUB_TABS if r_[0] == "storage" and r_[1] == "supplies"]
assert len(_SHROW) == 1 and _SHROW[0][3] == "SkyyCooking" and _SHROW[0][5] == "flask", ("0.1.11: Storage > Supplies is SkyyCooking's contract tab", _SHROW)
SSH = SUI.hub_page("SkyySu", "storage", sub=True, footer=True, content_id="SkyySuC")
assert (SSH.w, SSH.h) == (SUI.HUB_PAGE_W, SUI.HUB_PAGE_H) and SSH.content_h == 676, ("0.1.11: the hub page", SSH.content_h)
SUP_HUBJ = SUI.java_hub_page(SSH, "supplies", cls="@PKG@.HubBar")
SIW, SCH = SSH.content_w, SSH.content_h
SUP_SUBW, SUP_AUTO_W = SUI.SUB_TAB_W, 260
SUP_SUBF = SIW - 2 * SUP_SUBW - SUI.SUB_TAB_GAP - SUP_AUTO_W
SUP_DW = SUI.DETAIL_W
SUP_DIN = SUP_DW - 32
SUP_LW = SIW - SUP_DW - 16
SUP_RW = SUP_LW - 2 * SUI.WELL_LIST_PAD - SUI.SCROLL_SIZE - SUI.SCROLL_SPACING
SUP_ROWMAX = 120          # rows drawn at most (a packet-size cap like SkyySacks' 150); the status line says how many more there are
SUP_PUT_W = 260
SUP_HINT_W = SIW - SUP_PUT_W - SUI.FOOT_GAP
assert SUI.assert_sub_tabs_fit(["Potion Flask", "Food Pouch"]) + SUP_SUBF + SUP_AUTO_W == SIW, "0.1.11: the sub row fits 1552"
assert SUP_SUBF > 0 and SUP_RW >= 600, ("0.1.11: list width", SUP_RW)
_J = SUI.J


def sjl(parent, mk):
    return SUI.java_append(parent, mk, page_root=True)


SPK = {
    "SUBF": SUI.spacer(w=SUP_SUBF),
    "AUTO": SUI.button("SkyySuAuto", "", "secondary", "small", w=SUP_AUTO_W, fit=False),
    "MAIN": SUI.group("SkyySuMain", "Left", w=SIW, h=SCH),
    "LS": SUI.scroll_list("SkyySuLs", h=SCH, w=SUP_LW, well=True),
    "DET": SUI.group("SkyySuD", "Top", w=SUP_DW, h=SCH, anchor={"left": 16}, pad=16, bg="well"),
    "EMPTY": SUI.empty_state("SkyySuEm", w=SUP_RW),
    "DIC": SUI.icon_cell("SkyySuDIc", item=_J("dic", "Potion_Health_Small"), size=96, state="static", look="plain"),
    "DNM": SUI.label("SkyySuDNm", "", "strong", w=SUP_DIN, h=30, col=_J("dcol", SUI.QUALITY["Common"]), anchor={"top": 10}, fit=False),
    "DCT": SUI.label("SkyySuDCt", "", "bold", w=SUP_DIN, h=24, fit=False),
    "DTX": SUI.label("SkyySuDTx", "", "caption", w=SUP_DIN, h=150, wrap=True, fit=False),
    "DHINT": SUI.label("SkyySuDHn", "", "caption", w=SUP_DIN, h=150, wrap=True, anchor={"top": 10}, fit=False),
    "T1": SUI.button("SkyySuT1", "Take 1", "primary", w=SUP_DIN, anchor={"top": 8}),
    "TA": SUI.button("SkyySuTa", "Take all", "secondary", w=SUP_DIN, anchor={"top": 8}),
    "SK": SUI.button("SkyySuSk", "", "secondary", w=SUP_DIN, anchor={"top": 8}, fit=False),
}
SUP_FOOT = [SUI.foot_info("SkyySuSt", SUP_HINT_W), SUI.spacer(w=SUI.FOOT_GAP), SUI.foot_button("SkyySuPut", "Put all in", SUP_PUT_W)]
SUP_CARD = SUI.list_card("SkyySuLs", "SkyySuR" + _J("i", "0"), SUP_RW, [
    {"id": "Nm", "text": _J("rnm", "Lesser Health Potion"), "kind": "rowName", "h": 26, "col": _J("rcol", SUI.QUALITY["Common"]),
     "tag": {"id": "Tg", "text": _J("rtg", "Next  -  x12"), "col": "value", "w": 200, "kind": "bold"}},
    {"id": "Sb", "text": _J("rsb", "Heals 30% of your health"), "kind": "rowSub", "h": 44, "col": "rowSub", "wrap": True}],
    look=[("selected", "i == selI"), "normal"], icon_item=_J("ric", "Potion_Health_Small"), var="card",
    action=SUI.list_card_button("SkyySuRb" + _J("i", "0"), "Details"))
SPP = {"SHELL": SSH.java("b"), "SUBF": sjl(SSH.sub, SPK["SUBF"]), "AUTO": sjl(SSH.sub, SPK["AUTO"]),
       "MAIN": "\n".join([sjl(SSH.content, SPK["MAIN"]), sjl("SkyySuMain", SPK["LS"]), sjl("SkyySuMain", SPK["DET"])]),
       "CARD": SUP_CARD.java("b"), "EMPTY": sjl("SkyySuLs", SPK["EMPTY"]),
       "DETON": "\n".join(sjl("SkyySuD", SPK[x]) for x in ("DIC", "DNM", "DCT", "DTX", "T1", "TA", "SK")),
       "DETOFF": sjl("SkyySuD", SPK["DHINT"]),
       "FOOT": "\n".join(sjl(SSH.foot, m_) for m_ in SUP_FOOT)}
# build-time check of the page (kit 1.7 recipe): the shell + rows 1 + 2 + the sub row + content + footer = 1600 x 980, no back / pager
_spv = SUI.hub_page_preview(SSH, tabs=[(r_[0], SUI.hub_tab_label("storage", r_[0])) for r_ in SUI.hub_page_tabs("storage")], my_tab="supplies")
_spv.extend(SUI.sub_tabs_preview("SkyySu", ["Potion Flask", "Food Pouch"], 0))
for _p_, _k_ in ((SSH.sub, "SUBF"), (SSH.sub, "AUTO"), (SSH.content, "MAIN"), ("SkyySuMain", "LS"), ("SkyySuMain", "DET"), ("SkyySuLs", "EMPTY"),
                 ("SkyySuD", "DIC"), ("SkyySuD", "DNM"), ("SkyySuD", "DCT"), ("SkyySuD", "DTX"), ("SkyySuD", "T1"), ("SkyySuD", "TA"), ("SkyySuD", "SK")):
    _spv.append((_p_, SPK[_k_]))
_spv.extend(list(SUP_CARD))
for _m in SUP_FOOT:
    _spv.append((SSH.foot, _m))
SUI.check_page(_spv, "SkyySu")
SUI.assert_proven(_spv, what="Supplies hub page")
SUI.check_sky_paths(_spv, tab_icons=True)
_smp = SUI.assert_menu_page(_spv, SSH, what="Supplies hub page")
assert _smp["rows"] == 2 and _smp["subs"] == 1, _smp
assert SUI.used_width(_spv, SSH.foot) <= SIW and SUI.used_width(_spv, SSH.sub) == SIW, "0.1.11: the footer / sub row fit 1552"
del _spv, _smp

spg = smk("SupPage", T["PAGE"])
SUP_CLASSES.append(spg)
for _d in ("public int tab;", "public String selSrc;", "public String info;",
           "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();"):
    sup_F(spg, _d)
sup_C(spg, r"""
public SupPage(@PR@ pr, int tab) {
  super(pr, @LIFE@.CanDismiss);
  this.tab = tab == 1 ? 1 : 0; this.selSrc = ""; this.info = "";
}""")
for _l in SUI.java_status_methods():
    sup_M(spg, _l)
sup_M(spg, r"""
public static String jsonStr(String data, String key) {
  if (data == null || key == null) return "";
  String qt = String.valueOf((char) 34);
  int i = data.indexOf(qt + key + qt);
  if (i < 0) return "";
  i = data.indexOf(':', i + key.length() + 2);
  if (i < 0) return "";
  i++;
  while (i < data.length() && Character.isWhitespace(data.charAt(i))) i++;
  if (i >= data.length() || data.charAt(i) != 34) return "";
  i++;
  StringBuilder sb = new StringBuilder();
  while (i < data.length() && sb.length() < 200) {
    char c = data.charAt(i);
    if (c == 34) break;
    if (c == 92 && i + 1 < data.length()) { sb.append(data.charAt(i + 1)); i += 2; continue; }
    sb.append(c);
    i++;
  }
  return sb.toString();
}""")
sup_M(spg, r"""
public static int toInt(String s) {
  try { return Integer.parseInt(s.trim()); } catch (Throwable t) { return -1; }
}""")
SUP_BUILD = r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PKG@.SupData d = @PKG@.SupStore.get(@PKG@.SupOps.pkey(u));
  if (d != null && !d.ready && !d.bad && !@PKG@.SupLog.busy(u)) {
    try { @PLA@ p0 = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); if (p0 != null) @PKG@.SupOps.sweep(this.playerRef, p0, st, ref); } catch (Throwable t) { }
  }
  boolean ok = d != null && d.ready && !d.bad;
  int kk = this.tab;
  java.util.ArrayList rows = ok ? @PKG@.SupOps.rows(d, kk) : new java.util.ArrayList();
  int shown = rows.size() < @ROWMAX@ ? rows.size() : @ROWMAX@;
  int selI = -1;
  for (int x = 0; x < shown; x++) if (((String) rows.get(x)).equals(this.selSrc)) selI = x;
  if (selI < 0 && shown > 0) { selI = 0; this.selSrc = (String) rows.get(0); }
  if (shown == 0) this.selSrc = "";
{{SHELL}}
  @HUBJAVA@
  @PKG@.HubBar.subTab(b, ev, "SkyySu", 0, "Potion Flask", kk == 0, "tab0", @SUBW@);
  @PKG@.HubBar.subTab(b, ev, "SkyySu", 1, "Food Pouch", kk == 1, "tab1", @SUBW@);
{{SUBF}}
{{AUTO}}
  b.set("#SkyySuAuto.Text", "Auto-fill: " + (ok && d.auto(kk) ? "ON" : "OFF"));
  ev.addEventBinding(@BTY@.Activating, "#SkyySuAuto", @EVD@.of("a", "auto"));
{{MAIN}}
  for (int i = 0; i < shown; i++) {
    String src = (String) rows.get(i);
    String ric = src;
    String rnm = @PKG@.SupDefs.name(kk, src);
    String rcol = @PKG@.SupDefs.col(kk, src);
    String rtg = (i == 0 ? "Next  -  x" : "x") + d.get(kk, src);
    String rsb = @PKG@.SupDefs.desc(kk, src) + (d.skipped(src) ? "  -  Auto-fill OFF for this one" : "");
{{CARD}}
    ev.addEventBinding(@BTY@.Activating, "#SkyySuRb" + i, @EVD@.of("a", "sel").append("i", String.valueOf(i)));
  }
  if (shown == 0) {
{{EMPTY}}
    b.set("#SkyySuEm.Text", !ok ? "Your Supplies are still loading - open the page again in a moment." : (kk == 0 ? "No healing potions yet - drink-ready potions you pick up go in here." : "No food yet - cooked food you pick up goes in here."));
  }
  if (selI >= 0) {
    String dic = this.selSrc;
    String dcol = @PKG@.SupDefs.col(kk, dic);
{{DETON}}
    b.set("#SkyySuDNm.Text", @PKG@.SupDefs.name(kk, dic));
    b.set("#SkyySuDCt.Text", "You have " + d.get(kk, dic) + (selI == 0 ? "  -  used next" : ""));
    b.set("#SkyySuDTx.Text", @PKG@.SupDefs.desc(kk, dic) + (@PKG@.SupDefs.isRawSrc(kk, dic) ? " Raw food goes in only while the server's Raw food in the Pouch switch is on." : ""));
    b.set("#SkyySuSk.Text", "Auto-fill this: " + (d.skipped(dic) ? "OFF" : "ON"));
    ev.addEventBinding(@BTY@.Activating, "#SkyySuT1", @EVD@.of("a", "t1"));
    ev.addEventBinding(@BTY@.Activating, "#SkyySuTa", @EVD@.of("a", "ta"));
    ev.addEventBinding(@BTY@.Activating, "#SkyySuSk", @EVD@.of("a", "sk"));
  } else {
{{DETOFF}}
    b.set("#SkyySuDHn.Text", "Right click your " + @PKG@.SupDefs.kindName(kk) + " to " + (kk == 0 ? "drink" : "eat") + " the weakest first. It takes the normal " + (kk == 0 ? "drink" : "eat") + " time; getting hit does not stop it.");
  }
{{FOOT}}
  long cap = (long) @PKG@.SupCfg.cap(kk);
  String st0 = !ok ? "=Loading your Supplies." : (@PKG@.SupDefs.kindName(kk) + ": " + d.tot(kk) + " / " + cap + "  -  " + (!@PKG@.SupCfg.ON ? "switched off on this server (taking out still works)." : (d.auto(kk) ? "Auto-fill ON: " + @PKG@.SupDefs.what(kk) + " in your storage and backpack go in by themselves (never from the hotbar)." : "Auto-fill OFF - use Put all in.")) + (rows.size() > shown ? "  Showing the first " + shown + " of " + rows.size() + " kinds." : ""));
  b.set("#SkyySuSt.Text", this.info.length() > 0 ? textOf(this.info) : st0);
  ev.addEventBinding(@BTY@.Activating, "#SkyySuPut", @EVD@.of("a", "put"));
}"""
SUP_BUILD = jsrc(SUP_BUILD.replace("@HUBJAVA@", "@HUBJAVAX@").replace("@ROWMAX@", str(SUP_ROWMAX)).replace("@SUBW@", str(SUP_SUBW)).replace("@HUBJAVAX@", "{{HUBJAVA}}"))
SPP["HUBJAVA"] = jsrc(SUP_HUBJ)
for _k, _v in SPP.items():
    _tag = "{{%s}}" % _k
    assert SUP_BUILD.count(_tag) == 1, _tag
    SUP_BUILD = SUP_BUILD.replace(_tag, _v)
assert "{{" not in SUP_BUILD and "ItemGridSlot" not in SUP_BUILD, "0.1.11: every block placed, never an ItemGridSlot (HANDOFF 2)"
assert "_" not in "".join(re.findall(r"#(SkyySu\w*)", SUP_BUILD.replace("\\", ""))), "0.1.11: no underscores in element ids (HANDOFF 2)"
assert not [t_ for t_ in re.findall(r'Text: \\?"([^"\\]*)', SUP_BUILD) if SUI.MENU_BACK_RE.match(t_) or SUI.MENU_PAGER_RE.match(t_)], "0.1.11: no back / pager text"
sup_Mr(spg, SUP_BUILD)
sup_M(spg, r"""
public void hubAck() {
  try {
    @REF@ hr = this.playerRef.getReference();
    if (hr == null || !hr.isValid()) return;
    @ST@ hs = hr.getStore();
    if (hs == null) return;
    @PLA@ hp = (@PLA@) hs.getComponent(hr, @PLA@.getComponentType());
    if (hp == null || hp.getPageManager() == null || hp.getPageManager().getCustomPage() != this) return;
    @UCB@ hb = new @UCB@();
    hb.set("#SkyySuTitle.Text", "Storage");
    sendUpdate(hb, false);
  } catch (Throwable t) { }
}""")
# one click = one store op (world thread: page events run there), then the held item is synced and the page rebuilt ONCE
sup_M(spg, r"""
public String act(@PLA@ p, @ST@ st, @REF@ ref, String a, int i) {
  java.util.UUID u = this.playerRef.getUuid();
  if (p == null) return "-Could not find you - try again.";
  if (@PKG@.SupLog.busy(u)) return "=Your profile is still loading - try again in a moment.";
  @PKG@.SupData d = @PKG@.SupStore.get(@PKG@.SupOps.pkey(u));
  if (d == null || d.bad) return "-Your Supplies could not be read - nothing was changed (the server log has the details).";
  if (!d.ready) @PKG@.SupOps.sweep(this.playerRef, p, st, ref);
  if (!d.ready) return "=Still loading - try again in a moment.";
  int k = this.tab;
  @IC@[] cs = @PKG@.SupEng.secs(p.getInventory());
  String r = "";
  if (a.equals("sel")) {
    java.util.ArrayList rows = @PKG@.SupOps.rows(d, k);
    if (i >= 0 && i < rows.size()) this.selSrc = (String) rows.get(i);
    return "";
  } else if (a.equals("auto")) {
    boolean v = !d.auto(k);
    d.setAuto(k, v);
    @PKG@.SupStore.save(d);
    @PKG@.SupStore.append(@PKG@.SupStore.line("S", @PKG@.SupStore.nextSeq(), d.key, k, "auto", v ? 1L : 0L, 0L, @PKG@.SupDefs.kindName(k) + " Auto-fill " + (v ? "ON" : "OFF") + " (undo: press Auto-fill again)"));
    int n = v && @PKG@.SupCfg.ON ? @PKG@.SupOps.fill(this.playerRef, cs, d, k, false) : 0;
    r = "+Auto-fill " + (v ? "ON" : "OFF") + (n > 0 ? " - " + n + " went in." : ".");
  } else if (a.equals("t1") || a.equals("ta")) {
    r = @PKG@.SupOps.take(cs, d, k, this.selSrc, a.equals("t1") ? 1L : d.get(k, this.selSrc));
  } else if (a.equals("sk")) {
    if (this.selSrc.length() == 0) return "-Pick an item first.";
    boolean off = !d.skipped(this.selSrc);
    if (off) d.skip.put(this.selSrc, Boolean.TRUE); else d.skip.remove(this.selSrc);
    d.touch();
    @PKG@.SupStore.save(d);
    @PKG@.SupStore.append(@PKG@.SupStore.line("S", @PKG@.SupStore.nextSeq(), d.key, k, this.selSrc, off ? 0L : 1L, 0L, "Auto-fill this " + (off ? "OFF" : "ON") + " for " + this.selSrc + " (undo: press it again)"));
    r = "+" + @PKG@.SupDefs.name(k, this.selSrc) + (off ? " no longer goes in by itself (you can still use it)." : " goes in by itself again.");
  } else if (a.equals("put")) {
    if (!@PKG@.SupCfg.ON) return "-The " + @PKG@.SupDefs.kindName(k) + " is switched off on this server - nothing goes in.";
    int n = @PKG@.SupOps.fill(this.playerRef, cs, d, k, true);
    r = n > 0 ? "+Put " + n + " in." : (d.tot(k) >= (long) @PKG@.SupCfg.cap(k) ? "-Your " + @PKG@.SupDefs.kindName(k) + " is full." : "=Nothing in your storage or backpack can go in (the hotbar is never touched).");
  } else return "";
  @PKG@.SupOps.syncNow(st, ref, u, cs, d);
  return r;
}""")
sup_M(spg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  String hr = null;
  try { hr = @PKG@.HubBar.route(this.playerRef, data, "storage", "supplies"); } catch (Throwable th) { hr = null; }
  if (hr != null) {
    if (hr.equals("close")) { close(); return; }
    if (hr.equals("self")) { this.info = ""; rebuild(); return; }
    if (hr.equals("back") || hr.equals("bridge") || hr.equals("command")) { hubAck(); return; }
    this.info = "-That tab could not open right now - try again.";
    rebuild();
    return;
  }
  String a = jsonStr(data, "a");
  if (a.equals("close")) { close(); return; }
  if (a.equals("tab0") || a.equals("tab1")) {
    int t = a.equals("tab0") ? 0 : 1;
    if (t != this.tab) { this.tab = t; this.selSrc = ""; }
    LAST.put(this.playerRef.getUuid(), Integer.valueOf(t));
    this.info = "";
    rebuild();
    return;
  }
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  try { this.info = act(p, st, ref, a, toInt(jsonStr(data, "i"))); }
  catch (Throwable t) { this.info = "-Something went wrong - nothing more was changed."; @PKG@.SupLog.warn("Supplies page click " + a + " failed: " + t); }
  rebuild();
}""")
# OpenCustomUI "SkyySupplies" (crouch + right click on the item): the tab of the item in the hand
spf = smk("SupPageFactory", None, "java.util.function.Function")
SUP_CLASSES.append(spf)
sup_C(spf, "public SupPageFactory() { }")
sup_M(spf, r"""
public Object apply(Object o) {
  @PR@ pr = (@PR@) o;
  int k = -1;
  try {
    @REF@ r = pr.getReference();
    @PLA@ p = (@PLA@) r.getStore().getComponent(r, @PLA@.getComponentType());
    @IS@ h = p.getInventory().getItemInHand();
    if (h != null && !h.isEmpty()) k = @PKG@.SupDefs.kindOf(h.getItemId());
  } catch (Throwable t) { k = -1; }
  if (k < 0) { Object l = @PKG@.SupPage.LAST.get(pr.getUuid()); k = l instanceof Integer ? ((Integer) l).intValue() : 0; }
  return new @PKG@.SupPage(pr, k);
}""")
sho = smk("SupHubOpen", None, "java.util.function.Function")
SUP_CLASSES.append(sho)
sup_C(sho, "public SupHubOpen() { }")
sup_M(sho, r"""
public Object apply(Object o) {
  if (!(o instanceof java.util.UUID)) return Boolean.FALSE;
  try {
    @PR@ pr = @UNI@.get().getPlayer((java.util.UUID) o);
    if (pr == null || !pr.isValid()) return Boolean.FALSE;
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return Boolean.FALSE;
    @ST@ st = r.getStore();
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    if (p == null || p.getPageManager() == null) return Boolean.FALSE;
    Object l = @PKG@.SupPage.LAST.get(pr.getUuid());
    p.getPageManager().openCustomPage(r, st, new @PKG@.SupPage(pr, l instanceof Integer ? ((Integer) l).intValue() : 0));
    return Boolean.TRUE;
  } catch (Throwable t) { @PKG@.SupLog.warn("the Storage > Supplies tab could not open its page: " + t); return Boolean.FALSE; }
}""")
# ---------------------------------------------------------------- SupOpen: start / stop, the bridge, the two commands' body
sopn = smk("SupOpen")
SUP_CLASSES.append(sopn)
sup_F(sopn, "public static volatile Object CLAIMS = null;")
sup_F(sopn, "public static volatile Object COUNTS = null;")
sup_F(sopn, "public static volatile java.util.concurrent.ScheduledFuture TIMER = null;")
sup_M(sopn, r"""
public static void start(java.nio.file.Path dir, @LOG@ log) {
  @PKG@.SupLog.LOG = log;
  String c = @PKG@.SupCfg.load(dir);
  @PKG@.SupStore.DIR = dir.resolve("supplies");
  int open = @PKG@.SupStore.readJournal();
  try { TIMER = @HSV@.SCHEDULED_EXECUTOR.scheduleAtFixedRate(new @PKG@.SupSettle(), 10L, 10L, java.util.concurrent.TimeUnit.SECONDS); }
  catch (Throwable t) { @PKG@.SupLog.warn("the journal settle timer did not start (entries settle at the next start instead): " + t); }
  @PKG@.SupLog.info("Potion Flask (" + @PKG@.SupDefs.FSRC.length + " healing potions) + Food Pouch (" + @PKG@.SupDefs.PSRC.length + " foods) - " + c + "; " + open + " journal entries of the last run to recover; /flask /pouch; Storage > Supplies");
}""")
sup_M(sopn, r"""
public static void publish() {
  java.util.Map b = @PKG@.SupLog.bridge();
  CLAIMS = new @PKG@.SupClaimsFn();
  COUNTS = new @PKG@.SupCountsFn();
  b.put("supply:fn:claims", CLAIMS);
  b.put("supply:fn:counts", COUNTS);
  Object[] e = @PKG@.HubBar.put("storage", "supplies", "SkyyCooking", "@HUBLABEL@", @HUBORDER@, "@HUBCMD@", new @PKG@.SupHubOpen(), null);
  if (e == null) @PKG@.SupLog.warn("the Storage > Supplies hub tab could not be put");
}""".replace("@HUBLABEL@", _SHROW[0][4]).replace("@HUBORDER@", str(_SHROW[0][2])).replace("@HUBCMD@", _SHROW[0][5]))
sup_M(sopn, r"""
public static void stop() {
  try { if (TIMER != null) TIMER.cancel(false); } catch (Throwable t) { }
  try {
    java.util.Map b = @PKG@.SupLog.bridge();
    if (CLAIMS != null) b.remove("supply:fn:claims", CLAIMS);
    if (COUNTS != null) b.remove("supply:fn:counts", COUNTS);
  } catch (Throwable t) { }
  try { @PKG@.HubBar.removeAll(); } catch (Throwable t) { }
  java.util.Iterator it = @PKG@.SupStore.DATA.values().iterator();
  while (it.hasNext()) { @PKG@.SupData d = (@PKG@.SupData) it.next(); if (d.isDirty()) @PKG@.SupStore.save(d); }
}""")
# /flask and /pouch: give one back when you hold none (the lifelong recall, storage first), else open the page on that tab
sup_M(sopn, r"""
public static void cmd(@PR@ pr, @ST@ st, @REF@ ref, int k) {
  try {
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { @PKG@.SupLog.tell(pr, "[Cooking] player not found", @PKG@.SupLog.ERR); return; }
    String rr = k == 0 ? @PKG@.FlaskOnce.recall(pr, @PKG@.FlaskOnce.secs(p.getInventory())) : @PKG@.PouchOnce.recall(pr, @PKG@.PouchOnce.secs(p.getInventory()));
    if ("=have".equals(rr)) {
      p.getPageManager().openCustomPage(ref, st, new @PKG@.SupPage(pr, k));
      return;
    }
    String t = k == 0 ? @PKG@.FlaskOnce.recallText(rr) : @PKG@.PouchOnce.recallText(rr);
    if (t != null) @PKG@.SupLog.tell(pr, t, "+given".equals(rr) ? @PKG@.SupLog.OK : @PKG@.SupLog.INFO);
    if ("+given".equals(rr)) @PKG@.SupTask.schedule(pr, @PKG@.SupEng.worldOf(st), 0L, 0);
  } catch (Throwable t) { @PKG@.SupLog.warn(@PKG@.SupDefs.cmd(k) + " failed: " + t); @PKG@.SupLog.tell(pr, "[Cooking] something went wrong - see the server log", @PKG@.SupLog.ERR); }
}""")
for _cn, _w, _k, _d in (("SupFlaskCmd", "flask", 0, "Your Potion Flask: gives it back when you have none, else opens it (Storage > Supplies)"),
                        ("SupPouchCmd", "pouch", 1, "Your Food Pouch: gives it back when you have none, else opens it (Storage > Supplies)")):
    _c = smk(_cn, APC)
    SUP_CLASSES.append(_c)
    sup_C(_c, r"""
public %s() {
  super("%s", "%s");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""" % (_cn, _w, _d))
    sup_M(_c, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  @PKG@.SupOpen.cmd(pr, store, ref, %d);
}""" % _k)

for _c in SUP_CLASSES:
    _c.writeFile(OUT)
print("0.1.11 supplies classes written: %d (+ HubBar, %d lifelong classes)" % (len(SUP_CLASSES), len(LIFE_F["classes"]) + len(LIFE_P["classes"])))
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
  @PKG@.CookNcMig.migrate();   // 0.1.13: an untouched maxXpPerMinute 1500000 -> 0 (no cap), once; History first
  @PKG@.CookP3Mig.migrate();   // 0.1.15: the xp lines still on the 0.1.14 defaults -> Balance P3 (x tier factor), once; History first
  @PKG@.CookV3Mig.migrate();   // 0.1.16: the xp lines still on the 0.1.15 defaults -> ING_TIER v3 (fruit / milk tiers), once; History first
  String s = @PKG@.CookCfg.load();
  getEntityStoreRegistry().registerSystem(new @PKG@.CookSys());
  getCommandRegistry().registerCommand(new @PKG@.CookingCmd());
  getCommandRegistry().registerCommand(new @PKG@.CookAdminCmd());
  // 0.1.11 SUPPLIES (round FP1): config, store + journal, the four systems (one registerSystem per class), the page, /flask /pouch, bridge, hub tab
  try {
    @PKG@.SupOpen.start(getDataDirectory().resolveSibling("Skyy_SkyyCooking"), getLogger());
    getEntityStoreRegistry().registerSystem(new @PKG@.SupStartSys());
    getEntityStoreRegistry().registerSystem(new @PKG@.SupTick());
    getEntityStoreRegistry().registerSystem(new @PKG@.SupInvSys());
    getEventRegistry().registerGlobal(@PRE@.class, new @PKG@.SupReady());
    @OCU@.registerSimple(this, @PKG@.SkyyCookingPlugin.class, "SkyySupplies", new @PKG@.SupPageFactory());
    getCommandRegistry().registerCommand(new @PKG@.SupFlaskCmd());
    getCommandRegistry().registerCommand(new @PKG@.SupPouchCmd());
    @PKG@.SupOpen.publish();
  } catch (Throwable tSup) { @PKG@.CookCfg.warn("Supplies (Potion Flask + Food Pouch) setup failed: " + tSup); }
""" + SUP_LIFE_SETUP + """  java.util.Map b = @PKG@.Cook.bridge();
  b.put("cook:fn:grade", new @PKG@.CookGradeFn());
  b.put("cook:fn:out", new @PKG@.CookOutFn());
  b.put("cook:prefix", "Skyy_Cook_Food_");
  b.put("skill:stats:Cooking", new @PKG@.CookStatsFn());
  b.put("cook:fn:campfire", new @PKG@.CookCampFn());
  b.put("cook:campfire:ids", @PKG@.CookCfg.campList());
  b.put("cook:fn:campfactors", new @PKG@.CookCampInfoFn());
  @PKG@.Cook.reads(true);   // 0.1.14: tree:reads:SkyyCooking (Forager's Larder)
  @PKG@.Cook.regSetting("cooking.grade", "Food Grade changes", "cooking", true, "Your food now comes out Grade 3 - and the campfire accessory hint");
  @PKG@.Cook.regSetting("cooking.procs", "Cooking bonus procs", "cooking", true, "Gourmet!, Signature Dish!, Batch Cook!, Prep Cook! and Frugal!");
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCooking] @VERSION@ ready - Cooking Bench crafts give graded dishes (Grade = Cooking level / 10; heal and buffs x(1 + 0.32 x Grade) - x2.6 at 50, x4.2 at 100 - lasting x2^(Grade/5) - x2 at 50, x4 at 100; Grades 11-12 from the SkyyTrees Cooking tree) and Cooking XP through SkyySkills; Campfire accessory bridge cook:fn:campfire (" + @PKG@.CookCfg.campList() + "); /cooking; player switches cooking.grade + cooking.procs (/settings); in-game config: SkyWynn Menu Server Setup (/modconfig cooking); config: " + s + "; SkyySkills " + (b.get("skill:fn:level") != null ? "found" : "not loaded yet (plain food and no XP without it)"));
  @PKG@.CookSnd.load(getDataDirectory().resolveSibling("Skyy_SkyyCooking"));   // 0.1.7 sound pass: sounds.properties (before the kit)
  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());
}""")
Mk(pl, """
protected void shutdown() {
  try { java.util.Map b = @PKG@.Cook.bridge(); b.remove("cook:fn:grade"); b.remove("cook:fn:out"); b.remove("cook:prefix"); b.remove("skill:stats:Cooking"); b.remove("cook:fn:campfire"); b.remove("cook:campfire:ids"); b.remove("cook:fn:campfactors"); } catch (Throwable t) { }
  @PKG@.Cook.reads(false);   // 0.1.14: only our own value (never throws)
  try { @PKG@.CfgPub.shutdown(); } catch (Throwable t) { }
  try { @PKG@.SupOpen.stop(); } catch (Throwable t) { }   // 0.1.11: bridge keys (only while ours), hub tab, settle timer
""" + SUP_LIFE_SHUTDOWN + """  super.shutdown();
}""")

for c in (cfg, hk, mig, xmig, tmig, imig, nmig, pmig, vmig, ck, xpt, csy, gfn, ofn, sfn, cfn, ifn, gcmd, rcmd, fcmd, acmd, ccmd, pl):
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
_cap = MAX_PER_MIN_OLD               # 0.1.13: the default is 0 (no cap) - the window logic is checked at the old 1.5M
_JCfg.MAX_PER_MIN = _cap
_uu = jpype.JClass("java.util.UUID").randomUUID()
_parts = (int(_JCook.allowXpPart(_uu, _cap - 1000)), int(_JCook.allowXpPart(_uu, 5000)), int(_JCook.allowXpPart(_uu, 5000)), int(_JCook.allowXpPart(_uu, 0)))
if _parts != (_cap - 1000, 1000, 0, 0):
    raise SystemExit("self-check 0.1.1: compiled Cook.allowXpPart must pay what fits the %d/min window: got %s" % (_cap, _parts))
_uu = jpype.JClass("java.util.UUID").randomUUID()
if int(_JCook.allowXpPart(_uu, _cap + 800)) != _cap:
    raise SystemExit("self-check 0.1.1: compiled Cook.allowXpPart drops a whole batch that is bigger than the window")
_JCfg.MAX_PER_MIN = MAX_PER_MIN
_uu = jpype.JClass("java.util.UUID").randomUUID()
if MAX_PER_MIN != 0 or int(_JCfg.DEF_MAX_PER_MIN) != 0 or int(_JCook.allowXpPart(_uu, 50000000)) != 50000000 or not bool(_JCook.allowXp(_uu, 90000000)):
    raise SystemExit("self-check 0.1.13: maxXpPerMinute default 0 must pay every batch / dish (no cap)")
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
if [str(x) for x in _JCfg.DISHES] != GDISHES or int(_JCfg.N_VAN) != len(DISHES) or [int(x) for x in _JCfg.TIER] != [DISH_TIER[d] for d in GDISHES]:
    raise SystemExit("self-check 0.1.8: compiled CookCfg.DISHES / N_VAN / TIER are not the build's")
_gr0 = _JCfg.GRADED
_JCfg.GRADED = jpype.JClass("java.util.HashSet")()
_JCfg.GRADED.add("Food_Bread")
_t8 = []
for _own in (True, False):
    _JCfg.OWN_GRADED = _own
    _t8.append((int(_JCfg.tierOf("Food_Bread")), int(_JCfg.tierOf("Food_Pie_Meat")), int(_JCfg.tierOf(OWN_IDS[0])), int(_JCfg.tierOf("Food_Cheese"))))
_JCfg.GRADED, _JCfg.OWN_GRADED = _gr0, True
if _t8 != [(2, 0, DISH_TIER[OWN_IDS[0]], 0), (2, 0, 0, 0)]:
    raise SystemExit("self-check 0.1.8: compiled CookCfg.tierOf with graded=Food_Bread, gradedOwn on / off: %s" % _t8)
print("0.1.8 checks: compiled CookCfg.DISHES = %d graded dishes (%d vanilla + %d own); tierOf: an own dish is graded with gradedOwn on even when "
      "the graded list names only Food_Bread, plain with it off; a vanilla dish follows the list" % (len(GDISHES), len(DISHES), len(OWN_IDS)))
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
if DEFAULTS_TEXT_014.count(_XPN) != 1 or DEFAULTS_TEXT_014.count(CAMP_MARK + "\n# campfire.xpFactor = share") != 1 or CAMP_BLOCK_TEXT.count(CAMP_MARK + "\n") != 1:
    raise SystemExit("self-check 0.1.3: the default text / 0.1 append block must carry campfire.xpFactor=0.25 with the marker right above its help line")
def _mig(t):
    r = _JMig.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]], None if r[4] is None else str(r[4]))
_f012 = DEFAULTS_TEXT_014.replace(CAMP_MARK + "\n", "").replace(_XPN, _XPO)          # a fresh 0.1.2 file (header line aside)
if _mig(_f012) != (DEFAULTS_TEXT_014, "campfire.xpFactor 0.5 -> 0.25", None, ["campfire.xpFactor", "0.5", "0.25"], "0.5"):
    raise SystemExit("self-check 0.1.3: CookMig.update of a fresh 0.1.2 file is not exactly the 0.1.3 default text: %r" % (_mig(_f012),))
if _JMig.update(DEFAULTS_TEXT_014) is not None or _JMig.update("enabled=true\nxp.default=1000\n") is not None:
    raise SystemExit("self-check 0.1.3: CookMig.update must leave a marked file and a file without campfire lines alone")
_b011 = CAMP_BLOCK_TEXT.replace(CAMP_MARK + "\n", "").replace(_XPN, _XPO)        # the block 0.1.1 appended to a 0.1 file (the live shape)
for _nl in ("\n", "\r\n"):
    _head = "# SkyyCooking 0.1 - cooking.properties\nenabled=true\nxp.default=1000\ntree.CMaster.per=0.05\n"
    _in, _want = (_head + _b011).replace("\n", _nl), (_head + CAMP_BLOCK_TEXT).replace("\n", _nl)
    if _mig(_in) != (_want, "campfire.xpFactor 0.5 -> 0.25", None, ["campfire.xpFactor", "0.5", "0.25"], "0.5"):
        raise SystemExit("self-check 0.1.3: CookMig.update of the 0.1 + 0.1.1-block shape (%r) is wrong: %r" % (_nl, _mig(_in)))
_cus = _mig(_f012.replace(_XPO, "campfire.xpFactor=0.3\n"))
if _cus != (DEFAULTS_TEXT_014.replace(_XPN, "campfire.xpFactor=0.3\n"), "", "campfire.xpFactor=0.3 kept (custom) - the 0.1.3 default is 0.25", [], "0.3"):
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
if DEFAULTS_TEXT_014.count(_XMN) != 1 or DEFAULTS_TEXT_014.count(XP_MARK + "\n" + XP_HELP_LINE + "\n" + _XMN) != 1 or "xpMultiplier=1" in DEFAULTS_TEXT_014:
    raise SystemExit("self-check 0.1.4: the default text must carry xpMultiplier=0.5 with the marker right above its help line")
def _xm(t):
    r = _JXm.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]], None if r[4] is None else str(r[4]))
_f013 = DEFAULTS_TEXT_014.replace(XP_MARK + "\n", "").replace(_XMN, _XMO)            # a fresh 0.1.3 file (header line aside)
for _old in XP_MULT_OLD:
    _in = _f013.replace(_XMO, "xpMultiplier=%s\n" % _old)
    if _xm(_in) != (DEFAULTS_TEXT_014, "xpMultiplier %s -> 0.5" % _old, None, ["xpMultiplier", _old, "0.5"], _old):
        raise SystemExit("self-check 0.1.4: CookXpMig.update of a fresh 0.1.3 file with xpMultiplier=%s is not the 0.1.4 default text: %r" % (_old, _xm(_in)))
for _v in ("0.5", "0.7", "1.00", "2", "0"):
    _in = _f013.replace(_XMO, "xpMultiplier=%s\n" % _v)
    _note = None if _v == "0.5" else "xpMultiplier=%s kept (custom) - the 0.1.4 default is 0.5" % _v
    if _xm(_in) != (DEFAULTS_TEXT_014.replace(_XMN, "xpMultiplier=%s\n" % _v), "", _note, [], _v):
        raise SystemExit("self-check 0.1.4: a hand-set xpMultiplier=%s must be kept (marker only): %r" % (_v, _xm(_in)))
if _JXm.update(DEFAULTS_TEXT_014) is not None:
    raise SystemExit("self-check 0.1.4: CookXpMig.update must leave a marked file alone")
for _nl in ("\n", "\r\n"):
    _h = "# SkyyCooking 0.1 - cooking.properties\nenabled=true\n" + XP_HELP_LINE + "\nxpMultiplier=1.0\nmaxXpPerMinute=1500000\n"
    _in = _h.replace("\n", _nl)
    _want = _h.replace(XP_HELP_LINE, XP_MARK + "\n" + XP_HELP_LINE).replace("xpMultiplier=1.0", "xpMultiplier=0.5").replace("\n", _nl)
    if _xm(_in) != (_want, "xpMultiplier 1.0 -> 0.5", None, ["xpMultiplier", "1.0", "0.5"], "1.0"):
        raise SystemExit("self-check 0.1.4: CookXpMig.update of the live 0.1 shape (%r) is wrong: %r" % (_nl, _xm(_in)))
if _xm("enabled=true\nmaxGrade=12\n") != (XP_MARK + "\nenabled=true\nmaxGrade=12\n", "", None, [], None) or _xm("") != (XP_MARK + "\n", "", None, [], None):
    raise SystemExit("self-check 0.1.4: a file without an xpMultiplier line must get only the marker (above its first entry / on top)")
_JNm = jpype.JClass(PKG + ".CookNcMig", loader=_ld)
def _nm(t):
    r = _JNm.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]], None if r[4] is None else str(r[4]))
_NCN, _NCO = "maxXpPerMinute=0\n", "maxXpPerMinute=1500000\n"
if DEFAULTS_TEXT_014.count(_NCN) != 1 or DEFAULTS_TEXT_014.count(NC_MARK + "\n# safety net:") != 1 or _JNm.update(DEFAULTS_TEXT_014) is not None:
    raise SystemExit("self-check 0.1.13: the default text must carry maxXpPerMinute=0 with the marker above its help line (and stay untouched)")
_f012 = DEFAULTS_TEXT_014.replace(NC_MARK + "\n", "").replace(_NCN, _NCO)
for _nl in ("\n", "\r\n"):
    if _nm(_f012.replace("\n", _nl)) != (DEFAULTS_TEXT_014.replace("\n", _nl), "maxXpPerMinute 1500000 -> 0", None, ["maxXpPerMinute", "1500000", "0"], "1500000"):
        raise SystemExit("self-check 0.1.13: CookNcMig.update of a 0.1.12 file (%r) is not the 0.1.13 default text" % _nl)
for _v in ("2000000", "0", "750000"):
    _note = None if _v == "0" else "maxXpPerMinute=%s kept (custom) - the 0.1.13 default is 0 (no cap)" % _v
    if _nm(_f012.replace(_NCO, "maxXpPerMinute=%s\n" % _v)) != (DEFAULTS_TEXT_014.replace(_NCN, "maxXpPerMinute=%s\n" % _v), "", _note, [], _v):
        raise SystemExit("self-check 0.1.13: a hand-set maxXpPerMinute=%s must be kept (marker only)" % _v)
print("0.1.13 checks: maxXpPerMinute default 0 (no cap); CookNcMig.update: 0.1.12 file LF / CRLF -> the 0.1.13 default text, hand-set kept, marked file untouched")
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
        or sum(1 for l in _LANG if "or sooner with Cooking tree bonuses." in l) != 2 * len(GDISHES) * 10:
    raise SystemExit("self-check 0.1.4: the dish tooltip head is not the new wording (%s...)" % _HEAD2[:120])
print("0.1.4 checks: SF / MUL = 1 + 0.32 x Grade, DF = 2^(Grade/5) (compiled); xpMultiplier default 0.5 (row + help, loader fallback, field, "
      "default text with the marker); CookXpMig.update: a fresh 0.1.3 file with 1.0 or 1 -> the 0.1.4 default text, the live 0.1 shape (LF + "
      "CRLF) -> 0.5 + marker, 0.5 / 0.7 / 1.00 / 2 / 0 kept, marked file untouched, no line -> marker only; Cook.sd / sdShort / campText; "
      "tooltip 'Grade 2 food - Cooking 20, or sooner with Cooking tree bonuses' (%d lines)" % (2 * len(GDISHES) * 10))

DEFAULTS_015 = DEFAULTS_TEXT_014.replace(XP_ING_MARK + "\n" + XP_TBL_MARK + "\n" + "\n".join(XP_HELP_016) + "\n", XP_TBL_MARK + "\n" + "\n".join(XP_HELP_015) + "\n")
for _i in INGS:
    DEFAULTS_015 = DEFAULTS_015.replace("\nxp.%s=%d\n" % (_i, XP[_i]), "\nxp.%s=%d\n" % (_i, XP_015[_i]))
assert DEFAULTS_015.count(XP_TBL_MARK + "\n" + "\n".join(XP_HELP_015) + "\nxp.default=") == 1 and XP_ING_MARK not in DEFAULTS_015 \
    and all(DEFAULTS_015.count("\nxp.%s=%d\n" % (k, v)) == 1 for k, v in XP_015.items()), "0.1.6: DEFAULTS_015 is not the 0.1.5 shape"
# 0.1.5 self-check: the compiled XP table, the default text (marker + new help above the xp block), and the COMPILED one-time update
# (CookTblMig.update, the pure text step) on the shapes it meets in the field. The harness (SkyyCooking/test_skyycooking_0.1.5.py) runs
# migrate() itself on scratch copies of the live file.
_JTm = jpype.JClass(PKG + ".CookTblMig", loader=_ld)
if dict(zip([str(x) for x in _JCfg.XP_IDS], [int(x) for x in _JCfg.XP_VALS])) != XP_V3:   # 0.1.16: the jar pays the ING_TIER v3 table
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
if DEFAULTS_TEXT_014.count(_blk16) != 1 or any(h in DEFAULTS_TEXT_014 for h in XP_HELP_015 + XP_HELP_OLD) \
        or not all(DEFAULTS_TEXT_014.count("\nxp.%s=%d\n" % (k, v)) == 1 for k, v in XP.items()):
    raise SystemExit("self-check 0.1.6: the default text must carry both markers + the 0.1.6 help right above xp.default and the 0.1.6 table")
def _im(t):
    r = _JIm.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]])
_chg16 = ", ".join("xp.%s %d -> %d" % (i, XP_015[i], XP[i]) for i in _ING)
_rows16 = [x for i in _ING for x in ("xp[%s]" % i, str(XP_015[i]), str(XP[i]))]
if _im(DEFAULTS_015) != (DEFAULTS_TEXT_014, _chg16, None, _rows16):
    raise SystemExit("self-check 0.1.6: CookIngMig.update of the fresh 0.1.5 file is not exactly the 0.1.6 default text: %r" % (_im(DEFAULTS_015),)[:600])
_r = _tm(_f014(XP_OLD))           # a 0.1.4 file: CookTblMig then CookIngMig (setup()'s order) -> the 0.1.6 default text
if _r is None or _im(_r[0]) != (DEFAULTS_TEXT_014, _chg16, None, _rows16):
    raise SystemExit("self-check 0.1.6: a 0.1.4 file through CookTblMig + CookIngMig is not the 0.1.6 default text")
_cu = DEFAULTS_015.replace("\nxp.Ingredient_Flour=1425\n", "\nxp.Ingredient_Flour=500\n").replace("\nxp.Ingredient_Salt=140\n", "\nxp.Ingredient_Salt=%d\n" % XP["Ingredient_Salt"])
_r = _im(_cu)
if _r is None or "\nxp.Ingredient_Flour=500\n" not in _r[0] or _r[2] != "xp.Ingredient_Flour=500 kept (custom) - the 0.1.6 default is %d" % XP["Ingredient_Flour"] \
        or len(_r[3]) != 3 * (len(_ING) - 2) or "xp.Ingredient_Salt" in _r[1]:
    raise SystemExit("self-check 0.1.6: a hand-set value must be kept + noted, a value already on 0.1.6 kept silently: %r" % (_r,))
if _JIm.update(DEFAULTS_TEXT_014) is not None:
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

# 0.1.15 self-check: the compiled CookP3Mig tables + the COMPILED update (CookP3Mig.update) on the 0.1.14 default file and the shapes it meets
_JPm = jpype.JClass(PKG + ".CookP3Mig", loader=_ld)
def _pm(t):
    r = _JPm.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]])
if [str(x) for x in _JPm.KEYS] != ["xp." + k for k in P3_KEYS] or [str(x) for x in _JPm.NEWS] != [str(XP_P3[k]) for k in P3_KEYS] \
        or [str(x) for x in _JPm.OLDS] != [str(XP[k]) for k in P3_KEYS] or str(_JPm.MARK) != P3_MARK:
    raise SystemExit("self-check 0.1.15: compiled CookP3Mig tables are not the build's (%d keys)" % len(P3_KEYS))
for _nl in ("\n", "\r\n"):
    _r = _pm(DEFAULTS_TEXT_014.replace("\n", _nl))
    if _r is None or _r[0] != DEFAULTS_TEXT_015.replace("\n", _nl) or len(_r[3]) != 3 * len(P3_KEYS) or _r[2] is not None:
        raise SystemExit("self-check 0.1.15: CookP3Mig.update of the 0.1.14 default file (%r) is not the 0.1.15 default text" % _nl)
_cu = DEFAULTS_TEXT_014.replace("\nxp.Food_Pie_Meat=%d\n" % XP["Food_Pie_Meat"], "\nxp.Food_Pie_Meat=30000\n")
_r = _pm(_cu)
if _r is None or "\nxp.Food_Pie_Meat=30000\n" not in _r[0] or _r[2] != "xp.Food_Pie_Meat=30000 kept (custom) - the 0.1.15 default is %d" % XP_P3["Food_Pie_Meat"] or len(_r[3]) != 3 * (len(P3_KEYS) - 1):
    raise SystemExit("self-check 0.1.15: a hand-set value must be kept + noted: %r" % (_r[2] if _r else None,))
if _JPm.update(DEFAULTS_TEXT_015) is not None or _JPm.update(DEFAULTS_TEXT) is not None:
    raise SystemExit("self-check 0.1.15: CookP3Mig.update must leave a marked file alone")
_r = _im(_tm(_f014(XP_OLD))[0])   # a 0.1.4 file through every update in setup()'s order -> the 0.1.15 default text (header line aside)
if _r is None or _pm(_r[0]) is None or _pm(_r[0])[0] != DEFAULTS_TEXT_015:
    raise SystemExit("self-check 0.1.15: a 0.1.4 file through CookTblMig + CookIngMig + CookP3Mig is not the 0.1.15 default text")
print("0.1.15 checks: CookP3Mig.update: the 0.1.14 default file (LF + CRLF) -> the 0.1.15 default text "
      "(%d xp lines), hand-set 30000 kept + noted, marked file untouched, a 0.1.4 file through every update -> the same" % len(P3_KEYS))
# 0.1.16 self-check: the compiled CookV3Mig tables + the COMPILED update (CookV3Mig.update) on the 0.1.15 default file and the shapes it meets
_JVm = jpype.JClass(PKG + ".CookV3Mig", loader=_ld)
def _vm(t):
    r = _JVm.update(t)
    return None if r is None else (str(r[0]), str(r[1]), None if r[2] is None else str(r[2]), [str(x) for x in r[3]])
if [str(x) for x in _JVm.KEYS] != ["xp." + k for k in V3_KEYS] or [str(x) for x in _JVm.NEWS] != [str(XP_V3[k]) for k in V3_KEYS] \
        or [str(x) for x in _JVm.OLDS] != [str(XP_P3[k]) for k in V3_KEYS] or str(_JVm.MARK) != V3_MARK \
        or [str(x) for x in _JVm.HELP_OLD] != [XP_HELP_P3[2]] or [str(x) for x in _JVm.HELP_NEW] != [XP_HELP_V3[2]]:
    raise SystemExit("self-check 0.1.16: compiled CookV3Mig tables are not the build's (%d keys)" % len(V3_KEYS))
for _nl in ("\n", "\r\n"):
    _r = _vm(DEFAULTS_TEXT_015.replace("\n", _nl))
    if _r is None or _r[0] != DEFAULTS_TEXT.replace("\n", _nl) or len(_r[3]) != 3 * len(V3_KEYS) or _r[2] is not None:
        raise SystemExit("self-check 0.1.16: CookV3Mig.update of the 0.1.15 default file (%r) is not the 0.1.16 default text" % _nl)
_k0 = "Food_Skyy_Tropical_Smoothie"
_cu = DEFAULTS_TEXT_015.replace("\nxp.%s=%d\n" % (_k0, XP_P3[_k0]), "\nxp.%s=30000\n" % _k0)
_r = _vm(_cu)
if _r is None or ("\nxp.%s=30000\n" % _k0) not in _r[0] or _r[2] != "xp.%s=30000 kept (custom) - the 0.1.16 default is %d" % (_k0, XP_V3[_k0]) or len(_r[3]) != 3 * (len(V3_KEYS) - 1):
    raise SystemExit("self-check 0.1.16: a hand-set value must be kept + noted: %r" % (_r[2] if _r else None,))
if _JVm.update(DEFAULTS_TEXT) is not None:
    raise SystemExit("self-check 0.1.16: CookV3Mig.update must leave a marked file alone")
_r = _pm(DEFAULTS_TEXT_014)   # a 0.1.14 file through CookP3Mig + CookV3Mig (setup()'s order) -> the 0.1.16 default text
if _r is None or _vm(_r[0]) is None or _vm(_r[0])[0] != DEFAULTS_TEXT:
    raise SystemExit("self-check 0.1.16: a 0.1.14 file through CookP3Mig + CookV3Mig is not the 0.1.16 default text")
_r = _im(_tm(_f014(XP_OLD))[0])   # a 0.1.4 file through every update in setup()'s order -> the 0.1.16 default text (header line aside)
if _r is None or _pm(_r[0]) is None or _vm(_pm(_r[0])[0]) is None or _vm(_pm(_r[0])[0])[0] != DEFAULTS_TEXT:
    raise SystemExit("self-check 0.1.16: a 0.1.4 file through every update is not the 0.1.16 default text")
print("0.1.16 checks: compiled XP table = the ING_TIER v3 table; CookV3Mig.update: the 0.1.15 default file (LF + CRLF) -> the 0.1.16 default text "
      "(%d xp lines), hand-set 30000 kept + noted, marked file untouched, 0.1.14 and 0.1.4 files through every update -> the same" % len(V3_KEYS))

# 0.1.11: the Sky Window kit art (the Supplies hub page; HUBS-CONTRACT 2.7) - all 59 files, under Common/UI/Custom/SkyyKit/ only
_kit = SUI.kit_texture_files()
assert len(_kit) == len(SUI.SKY_FILES) == 59 and all(p_.startswith("Common/UI/Custom/SkyyKit/") and p_ not in files for p_ in _kit), "0.1.11: the kit art"
files.update(_kit)
jar = os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)
B.assemble(jar, B.manifest("SkyyCooking", VERSION, "SkyWynn Cooking: food families - Veggie dishes restore Health, Fruit Mana, Meat Stamina, Mushrooms give Strength, Grain and Dairy / Egg / Fish a mix, combos give each family's part; every vanilla dish and raw meat follows them, eating is 25% faster and hits never stop it; 11 new dishes. Dishes cooked at the Cooking Bench come out graded by your Cooking level (SkyySkills) - Grade = level / 10, heal and buffs +32% stronger per Grade (x2.6 at level 50, x4.2 at 100) and lasting x2 longer at level 50 (x4 at 100), Grades 11-12 from the SkyyTrees Cooking tree; the Campfire dishes can be cooked at the Cooking Bench too, or instantly through the Campfire accessory in /craft (SkyySacks) as an emergency cook at 75% of the Grade bonus and 25% of the XP; Cooking XP goes to SkyySkills. /cooking; admins change its settings in game (SkyWynn Menu Server Setup, /modconfig cooking) and players hide its chat lines in /settings. Zero dependencies (without SkyySkills food stays plain).", PKG + ".SkyyCookingPlugin"), OUT, files)
if "--deploy" in sys.argv:
    B.deploy(jar, "SkyyCooking.jar")
    B.enable_in_world("HUD mod", "Skyy:%s SkyyCooking" % VERSION, disable_prefix="Skyy:")
