"""Derive SkyyCooking/build_skyycooking_0.1.8.py from the LIVE SkyyCooking 0.1.7 (build_skyycooking_0.1.7.py = the tools/deploy_set.py SET pin,
DERIVED by tools/cooking_0_1_7_patch.py - never edit a generated script, edit this patch). Every anchor is asserted; at the end every change
is undone on a copy and compared with 0.1.7 (nothing else changed). Line endings kept.
Run:  python tools/cooking_0_1_8_patch.py   then   python SkyyCooking/build_skyycooking_0.1.8.py   (never --deploy)
Check: python SkyyCooking/test_skyycooking_0.1.8.py [--dir <folder inside tools/dev/scratch/>] [--keep]

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
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

P = G.Patch(os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.7.py"), os.path.join(ROOT, "SkyyCooking", "build_skyycooking_0.1.8.py"))
assert P.has('VERSION = "0.1.7"\n') and P.has("DERIVED from build_skyycooking_0.1.6.py by tools/cooking_0_1_7_patch.py") and not P.has("FOOD FAMILIES"), \
    "not the generated SkyyCooking 0.1.7 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.8 = FOOD FAMILIES"):].rstrip() + "\n\n"

# ---------- docstring + version
P.rep('''"""SkyyCooking 0.1.7 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.6.py by tools/cooking_0_1_7_patch.py
(0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_6_patch.py / _0_1_5_patch.py / _0_1_4_patch.py /
_0_1_3_patch.py / _0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.7.py            -> SkyyCooking/SkyyCooking-0.1.7.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''', '''"""SkyyCooking 0.1.8 - build script (javassist via jpype). DERIVED from build_skyycooking_0.1.7.py by tools/cooking_0_1_8_patch.py
(0.1.7 / 0.1.6 / 0.1.5 / 0.1.4 / 0.1.3 / 0.1.2 / 0.1.1 are derived the same way by tools/cooking_0_1_7_patch.py / _0_1_6_patch.py /
_0_1_5_patch.py / _0_1_4_patch.py / _0_1_3_patch.py / _0_1_2_patch.py / _0_1_1_patch.py): edit the patch and re-run it, not this file.
Run:   python build_skyycooking_0.1.8.py            -> SkyyCooking/SkyyCooking-0.1.8.jar
       (never --deploy: tools/deploy_set.py is the only deploy path - HANDOFF section 3)

''' + NOTE)
P.rep('VERSION = "0.1.7"\n', 'VERSION = "0.1.8"\n')
P.rep('''GENERATED ASSETS (asset pack in this jar, all copied from the game's own shapes in Assets.zip, 435 JSON files since 0.1.7):
''', '''GENERATED ASSETS - 0.1.8: the dish chains, effects and checks below were REPLACED by the FOOD FAMILIES assets (see the 0.1.8 note at the
top and the build's "0.1.8 assets" line); the 144 effect files stay (legacy), the 108 family checks are gone. The 0.1.7 text follows:
GENERATED ASSETS (asset pack in this jar, all copied from the game's own shapes in Assets.zip, 435 JSON files since 0.1.7):
''')

# =====================================================================================================================
# the asset block: family checks + graded dishes + recipe variants + self-checks (0.1.7 lines "# ---- family checks ..." through the
# 0.1.4 print) -> the FOOD FAMILIES generation. The 0.1.7 effects (G_EFFECTS, built just above the block) stay as legacy files.
# =====================================================================================================================
A0 = "# ---- family checks: rank = (strength, duration, tier, grade), vanilla Grade 0 members included\n"
A1 = 'print("0.1.4: all %d graded effects = vanilla strength x (1 + 0.32 x Grade), Duration x 2^(Grade/5); no cap binds" % len(G_EFFECTS))\n'
assert P.s.count(A0) == 1 and P.s.count(A1) == 1 and P.s.index(A0) < P.s.index(A1)
OLD_BLOCK = P.s[P.s.index(A0):P.s.index(A1) + len(A1)]
for _must in ("for dish in DISHES:", "VARIANTS = [", "ASSET SELF-CHECK FAILED", "_REMOVED_07", "_capped"):
    assert _must in OLD_BLOCK, _must
NEWGEN = r'''# =====================================================================================================================
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
ALLROUND = {1: 0.0, 2: 0.15, 3: 0.25}                  # higher tiers: this weight on every bar the families leave empty (not Strength)
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
STRENGTH_DURATION_S = 360.0                            # critic 2 (open question for Skyy): Strength lasts a FLAT 360 s at every Grade -
STRENGTH_GRADE_DURATION = False                        #   no x2^(Grade/5) for the Strength bar (its strength still scales x(1 + 0.32 g))
# vanilla / 0.1.7 buffs one of our bars replaces (critic 1; 0.1.7 cleared vanilla regen the same way): eating a dish of that bar clears them
VANILLA_CLEAR = {"Health": ["HealthRegen_Buff_Raw"] + ["HealthRegen_Buff_T%d" % t for t in (1, 2, 3)] + ["Meat_Buff_T%d" % t for t in (1, 2, 3)],
                 "Stamina": ["FruitVeggie_Buff_T%d" % t for t in (1, 2, 3)]}
LEGACY_CLEAR = {"Health": ["HealthRegen", "Meat"], "Stamina": ["FruitVeggie"]}   # + the 0.1.7 Skyy_Cook_<fam>_Buff_T<t>_G<g> files
def bar_dur(bar, dur): return dur if (bar != "Strength" or STRENGTH_GRADE_DURATION) else STRENGTH_DURATION_S
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
OWN_IDS = [o[0] for o in OWN]
GDISHES = DISHES + OWN_IDS                              # every graded dish (Java CookCfg.DISHES); DISHES stays the 15 vanilla ones
OWN_RECIPE = {}
for oid, nm, t, cat, sec, donor, ins in OWN:
    if oid in V_ITEMS: raise SystemExit("0.1.8: own dish id %s collides with a vanilla item" % oid)
    if donor not in DISHES: raise SystemExit("0.1.8: %s's look donor %s is not a vanilla dish" % (oid, donor))
    OWN_RECIPE[oid] = {"Input": [({"ResourceTypeId": x, "Quantity": q} if k == "R" else {"ItemId": x, "Quantity": q}) for k, x, q in ins],
                       "Output": [{"ItemId": oid, "Quantity": 1}],
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
        out.append("• " + W % ("Strength +" + pct_s(v)) + " (%s%% more damage%s)" % (pct_s(v), "" if STRENGTH_GRADE_DURATION else ", for " + mmss(STRENGTH_DURATION_S)))
    return out
def food_text(fams, n, raw=False):
    w, inst, over, sn, dur = n
    t = W % bars_title(fams) + " (" + ", ".join(FAM_LABEL[f] for f in fams) + ")" + (" - a raw snack." if raw else ".")
    parts = [W % (pct_s(inst[b]) + "%") + " " + b.lower() for b in ("Health", "Mana", "Stamina") if b in inst]
    body = "Instantly restores " + (", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0])
    bl = fx_bullets(n)
    if bl:
        body += " and grants:\\n\\n" + "\\n".join(bl) + "\\n\\nDuration: " + W % mmss(dur)
    else:
        body += "."
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
        if [o["ItemId"] for o in rc["Output"]] != [iid]: errs.append("own dish %s: its recipe must output itself" % iid)
        for inp in rc["Input"]:
            if "ItemId" in inp: need("item", inp["ItemId"], "recipe " + iid)
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
'''
P.rep(OLD_BLOCK, NEWGEN)

# ---------- the legacy effect loop stays; its pools must exist before the new block (G_INTER / G_ITEMS are created there already)
assert P.has('files = {}\nG_EFFECTS, G_INTER, G_ITEMS = {}, {}, {}\n')

# ---------- XP: own dishes join the table AFTER the 0.1.5 / 0.1.6 asserts (those pin the vanilla table), by the same LOCKED difficulty rule
P.rep('''def bench_class(out):
    if out in [v[1] for v in VARIANTS]: return "Campfire"
    cats = [c for b in (rd(V_ITEMS[out])["Recipe"].get("BenchRequirement") or []) if b.get("Id") == "Cookingbench" for c in (b.get("Categories") or [])]
''', '''def bench_class(out):
    if out in [v[1] for v in VARIANTS]: return "Campfire"
    _rc = OWN_RECIPE[out] if out in OWN_RECIPE else rd(V_ITEMS[out])["Recipe"]   # 0.1.8: own dishes carry their recipe in the build
    cats = [c for b in (_rc.get("BenchRequirement") or []) if b.get("Id") == "Cookingbench" for c in (b.get("Categories") or [])]
''')
P.rep('''# route estimate: one meat pie with its whole chain (flour, dough, spices, 1/5 of a salt craft)
''', '''# ---- 0.1.8: our own dishes, by the LOCKED difficulty rule (Skyy 2026-10-04: "the easier to craft the less xp. the harder to craft the
# more.") - chain raw x 950 x (20% + 15% per extra crafting step + 5% Prepared / 10% Baked + 5% per ingredient tier above 1), like every dish
for _oid in OWN_IDS:
    _r = OWN_RECIPE[_oid]
    COOK[_oid] = (inputs_of(_r), 1, float(_r["TimeSeconds"]), False)
for _oid in OWN_IDS:
    DIFF[_oid] = diff_share(_oid)
    XP[_oid] = rnd_to(K_XP * DIFF[_oid] * chain_raw(_oid) / 100.0, 50)
_easy8 = [d for d in GDISHES if len(chain_crafts(d)) == 1 and not COOK[d][3]]
_hard8 = [d for d in GDISHES if len(chain_crafts(d)) >= 3]
assert max(XP[d] for d in _easy8) < min(XP[d] for d in _hard8), "0.1.8: an easy dish pays as much as a multi-step one"
for _oid in OWN_IDS:   # a skewer of ours pays like the vanilla skewer with the same raw count; a dish with a crafted input pays more per raw item
    assert XP[_oid] > 0 and (len(chain_crafts(_oid)) == 1 or XP[_oid] / chain_raw(_oid) > XP["Food_Kebab_Vegetable"] / chain_raw("Food_Kebab_Vegetable")), _oid
print("0.1.8 own dish XP (difficulty share %, chain raw -> XP): " + ", ".join("%s %d%% %.1f -> %d" % (_oid, DIFF[_oid], chain_raw(_oid), XP[_oid]) for _oid in OWN_IDS))
# route estimate: one meat pie with its whole chain (flour, dough, spices, 1/5 of a salt craft)
''')
P.rep('''assert _best in DISHES, "0.1.6: the fastest route must be a dish, not %s" % _best
assert max(RATE[i] for i in INGS) < min(RATE[d] for d in DISHES), "0.1.6: an ingredient spam route levels as fast as a dish"
''', '''assert _best in GDISHES, "0.1.6: the fastest route must be a dish, not %s" % _best
assert max(RATE[i] for i in INGS) < min(RATE[d] for d in GDISHES), "0.1.6: an ingredient spam route levels as fast as a dish"
assert RATE[_best] <= 1.15 * max(RATE[d] for d in DISHES), "0.1.8: an own dish must not become a much faster levelling route than the vanilla best"
''')

# ---------- the campfire self-check (0.1.1) on the new numbers: T1 graded, XP, every Grade asset, the strength scales by exactly S(g)
P.rep('''def _bonus(e):
    if e.get("RawStatModifiers"): return list(e["RawStatModifiers"].values())[0][0]["Amount"] - 1.0
    return e["StatModifiers"]["Health"]
''', '''def _bonus(n):   # 0.1.8: the nominal (unsnapped) numbers of one dish at one Grade
    return [n[1][b] for b in sorted(n[1])] + [n[2][b] for b in sorted(n[2])]
''')
P.rep('''    for f in DISH_FX[d]:
        b = f[1] if f[0] == "I" else "%s_Buff_T%d" % (f[1], f[2])
        e0 = scale_effect(b, 0)
        for g in range(1, GEN_MAX + 1):
            eg = scale_effect(b, g)
            if abs(_bonus(eg) - _bonus(e0) * SF(g)) > 0.0002 or (e0.get("Duration", 0) > 0.5 and abs(eg["Duration"] - e0["Duration"] * DF(g)) > 0.01):
                raise SystemExit("self-check 0.1.1: %s Grade %d of %s hits a cap - the campfire mapping would not be x%.2f" % (b, g, d, SF(g)))
''', '''    _b0 = _bonus(DISH_NUM[(d, 0)])
    for g in range(1, GEN_MAX + 1):
        _bg, _n = _bonus(DISH_NUM[(d, g)]), DISH_NUM[(d, g)]
        if any(abs(x - y * SF(g)) > 0.0102 for x, y in zip(_bg, _b0)) or abs(_n[4] - DISH_NUM[(d, 0)][4] * DF(g)) > 0.01:
            raise SystemExit("self-check 0.1.1: Grade %d of %s hits a cap - the campfire mapping would not be x%.2f" % (g, d, SF(g)))
''')

# ---------- cooking.properties: graded= lists every graded dish (new files); gradedOwn (missing line = on) grades ours on a live file
P.rep('''      "# dishes that come out graded (must be dishes this jar generated assets for; others always come out plain)",
      "graded=" + ",".join(DISHES)] + CAMP_LINES + [''', '''      "# dishes that come out graded (must be dishes this jar generated assets for; others always come out plain)",
      "graded=" + ",".join(GDISHES),
      "# true = SkyyCooking's own dishes (Garden Skewer, Rice Bowl ...) always come out graded, whatever the graded list says (0.1.8)",
      "gradedOwn=true"] + CAMP_LINES + [''')

# ---------- Java CookCfg: every graded dish, the vanilla count, the own-dish switch
P.rep('''F(cfg, "public static final String[] DISHES = %s;" % jstr_arr(DISHES))
F(cfg, "public static final int[] TIER = %s;" % jint_arr([DISH_TIER[d] for d in DISHES]))
F(cfg, "public static final String[] NAMES = %s;" % jstr_arr([DISH_NAME[d] for d in DISHES]))
''', '''F(cfg, "public static final String[] DISHES = %s;" % jstr_arr(GDISHES))   # 0.1.8: the 15 vanilla dishes, then our own
F(cfg, "public static final int[] TIER = %s;" % jint_arr([DISH_TIER[d] for d in GDISHES]))
F(cfg, "public static final String[] NAMES = %s;" % jstr_arr([DISH_NAME[d] for d in GDISHES]))
F(cfg, "public static final int N_VAN = %d;" % len(DISHES))                # 0.1.8: DISHES[N_VAN..] = SkyyCooking's own dishes
F(cfg, "public static volatile boolean OWN_GRADED = true;")                 # 0.1.8: gradedOwn (missing line = true)
''')
P.rep('''public static int tierOf(String id) {
  int i = dishIndex(id);
  if (i < 0) return 0;
  if (!GRADED.contains(id)) return 0;
  return TIER[i];
}""")''', '''public static int tierOf(String id) {
  int i = dishIndex(id);
  if (i < 0) return 0;
  if (!GRADED.contains(id) && !(i >= N_VAN && OWN_GRADED)) return 0;
  return TIER[i];
}""")''')
P.rep('''    ENABLED = bool(p, "enabled", true);
''', '''    ENABLED = bool(p, "enabled", true);
    OWN_GRADED = bool(p, "gradedOwn", true);
''')
P.rep('''    return (ENABLED ? "on" : "OFF") + ", " + gr.size() + " graded dishes, max Grade "''',
      '''    return (ENABLED ? "on" : "OFF") + ", " + gr.size() + " graded dishes (own dishes " + (OWN_GRADED ? "always graded" : "by the list") + "), max Grade "''')

# ---------- Server Setup rows
P.rep('''    ("graded", "Graded dishes", "grades", "items", ",".join(DISHES), "0", str(len(DISHES)), "", "", "live",
     "Dishes that come out graded - only the %d dishes this jar has Grade assets for." % len(DISHES),
     "reload@cooking.properties:graded;check=CookHooks.checkGraded"),
''', '''    ("graded", "Graded dishes", "grades", "items", ",".join(GDISHES), "0", str(len(GDISHES)), "", "", "live",
     "Dishes that come out graded - only the %d dishes this jar has Grade assets for." % len(GDISHES),
     "reload@cooking.properties:graded;check=CookHooks.checkGraded"),
    ("gradedOwn", "Own dishes graded", "grades", "bool", "true", "", "", "", "", "live",
     "On: SkyyCooking's own dishes (Garden Skewer ...) are always graded, whatever the list above says.",
     "reload@cooking.properties:gradedOwn"),
''')

# ---------- the kit checks item rows against the CACHED Assets.zip ids + this jar's own items (the new dishes are not in Assets.zip)
P.rep('''                   RELOAD="CookCfg.load", KEEP=10, DEFAULTS={''',
      '''                   RELOAD="CookCfg.load", KEEP=10, ITEMS=set(V_ITEMS) | set(G_ITEMS), DEFAULTS={''')

# ---------- /cookadmin give text (the dish list grew)
P.rep('''  this.dishArg = withRequiredArg("dish", "Food_Pie_Meat, pie_meat, Food_Bread, ... (the 15 graded dishes)", @ATY@.STRING);''',
      '''  this.dishArg = withRequiredArg("dish", "Food_Pie_Meat, pie_meat, Skyy_Garden_Skewer, ... (every graded dish)", @ATY@.STRING);''')

# ---------- 0.1.4 tooltip-count self-check: every graded dish (vanilla + own) carries the head
P.rep('''        or sum(1 for l in _LANG if "or sooner with Cooking tree bonuses." in l) != 2 * len(DISHES) * 10:''',
      '''        or sum(1 for l in _LANG if "or sooner with Cooking tree bonuses." in l) != 2 * len(GDISHES) * 10:''')
P.rep('''      "tooltip 'Grade 2 food - Cooking 20, or sooner with Cooking tree bonuses' (%d lines)" % (2 * len(DISHES) * 10))''',
      '''      "tooltip 'Grade 2 food - Cooking 20, or sooner with Cooking tree bonuses' (%d lines)" % (2 * len(GDISHES) * 10))''')

# ---------- 0.1.8 compiled self-check (after the 0.1.2 hooks check): tierOf for own / vanilla dishes, gradedOwn, the arrays
P.rep('''_JRows = jpype.JClass(PKG + ".CfgRows", loader=_ld)
''', '''_JRows = jpype.JClass(PKG + ".CfgRows", loader=_ld)
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
''')

# ---------- manifest
P.rep('''"SkyWynn Cooking: dishes cooked at the Cooking Bench come out graded by your Cooking level (SkyySkills) - Grade = level / 10,''',
      '''"SkyWynn Cooking: food families - Veggie dishes restore Health, Fruit Mana, Meat Stamina, Mushrooms give Strength, Grain and Dairy / Egg / Fish a mix, combos give each family's part; every vanilla dish and raw meat follows them, eating is 25% faster and hits never stop it; 11 new dishes. Dishes cooked at the Cooking Bench come out graded by your Cooking level (SkyySkills) - Grade = level / 10,''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added"
_i = P.s.index
assert _i("GDISHES = DISHES + OWN_IDS") < _i("def bench_class(out):") < _i("for _oid in OWN_IDS:\n    _r = OWN_RECIPE[_oid]") < _i('"graded=" + ",".join(GDISHES)') \
    < _i('F(cfg, "public static final String[] DISHES = %s;" % jstr_arr(GDISHES))')
P.finish()
