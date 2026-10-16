"""Harness for SkyyCooking 0.1.9 (tools/cooking_0_1_9_patch.py): FOOD STRENGTH DURATION (lean round small01) on top of the 0.1.8
FOOD FAMILIES checks (copied from test_skyycooking_0.1.8.py). 0.1.9: the Strength buff lasts 360 x 2^(g/5) capped at 600 s (Skyy
2026-10-16 "scale with grade. 10 minuet cap"); the +20 % cap stays.
Build first: python tools/cooking_0_1_9_patch.py && python SkyyCooking/build_skyycooking_0.1.9.py

    python SkyyCooking/test_skyycooking_0.1.9.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py; game files only through the CACHED copies of tools/serverjar.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.8 -> 0.1.9: only version texts in classes; non-class entries: manifest + lang + item files only (SkyyCook items +
               the vanilla override paths); nothing gone; every effect and interaction file byte-equal to 0.1.8
  FX  assets   (pure Python, its OWN copy of the rules - independent of the build script) against the cached 0.7 Assets.zip:
               R  every effect / interaction / root / item / Common file a generated asset names exists (jar or Assets.zip)
               F  every dish's families from its recipe (vanilla Recipe / our recipe) = the table; ingredient -> family rules
               N  every food item (22 overrides, 11 own Grade 0, 312 graded): the inline instant = base x weight x (1 + 0.32 g) (caps),
                  the applied over-time effect per bar within half a ladder step of base x weight x S(g), its Duration = 360 x 2^(g/5) (Strength: capped at 600 s);
                  the applied effect's JSON (Health regen + max health, Mana regen, max Stamina + regen, Strength = OutgoingDamage)
               K  stacking: every check of a bar lists exactly the stronger levels (EffectCondition Match None) and clears exactly the
                  weaker ones, then Replaces the bar's var; every item carrying a check carries the matching var
               O  the 22 overrides = the vanilla item except InteractionVars Effect / Consume_Charge / Skyy_Cook_Apply_* and the
                  description key (Recipe, Parent, model, Quality unchanged)
               E  eating: the fast charge = vanilla Consume_Charge_Food_T1_Inner with its time x 0.75 and FailOnDamage false; every food
                  item of the jar eats through it; no potion / root interaction is in the jar
               L  the 144 legacy effect files and every 0.1.7 item id (180 graded + 3 recipes) are still in the jar
  J   java     EXECUTES the new Java paths (bare JVM, -Xverify:all): CookCfg.load on scratch files (missing file -> the 0.1.8 default
               text with gradedOwn=true and every dish graded; a live-shape graded= of the 15 vanilla dishes -> own dishes graded through
               gradedOwn; gradedOwn=false -> own dishes plain; bad value -> default), tierOf, xpFor of the own dishes, CookHooks.checkGraded
  D   live     setup()'s data steps (4 one-time updates, CookCfg.load, CookSnd.load, CfgPub.start) TWICE on a scratch COPY of the live
               Skyy_SkyyCooking (world NewBetaTest): no update runs, cooking.properties untouched, own dishes graded, second start = nothing
  AA  engine-access audit
NOT testable here (UNVERIFIED until the game loads it): the engine applying the inline instant / the Replace'd ApplyEffect with Duration
(vanilla shapes), the client drawing the eat time / tooltips, the override files winning over Assets.zip in this pack (precedent: SkyyArmory).
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, math, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import serverjar as SJ

VERSION = "0.1.9"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCooking-0.1.8.jar")
OLD7_JAR = os.path.join(HERE, "SkyyCooking-0.1.7.jar")        # the L (legacy) checks keep comparing with 0.1.7
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "small01", "cook")))
PKG = "com.skyy.cooking."
LIVE_DIR = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData", "Saves", "NewBetaTest", "mods", "Skyy_SkyyCooking")
EXPECT = {
    # 0.1.9: the "SkyyCooking 0.1.9" version text only (default file header, kit header / export, migration WHO, ready line)
    "CookCfg": ["~m load"], "CookMig": ["~m logLine", "~m migrate"], "CookXpMig": ["~m migrate"], "CookTblMig": ["~m migrate"],
    "CookIngMig": ["~m migrate"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "SkyyCookingPlugin": ["~m setup"],
}
ADDED = []
EFF, INT, ITM = "Server/Entity/Effects/SkyyCook/", "Server/Item/Interactions/SkyyCook/", "Server/Item/Items/SkyyCook/"

# ---- the rules, written out again (independent of the build script)
DISHES = ["Food_Wildmeat_Cooked", "Food_Fish_Grilled", "Food_Vegetable_Cooked", "Food_Bread", "Food_Kebab_Fruit", "Food_Kebab_Meat",
          "Food_Kebab_Mushroom", "Food_Kebab_Vegetable", "Food_Salad_Berry", "Food_Salad_Mushroom", "Food_Popcorn", "Food_Pie_Apple",
          "Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Salad_Caesar"]
OWN = {"Food_Skyy_Garden_Skewer": (2, ["Veggie", "Fruit"]), "Food_Skyy_Hunter_Skewer": (2, ["Veggie", "Meat"]),
       "Food_Skyy_Forest_Skewer": (2, ["Meat", "Mushroom"]), "Food_Skyy_Woodland_Skewer": (2, ["Fruit", "Mushroom"]),
       "Food_Skyy_Omelette": (2, ["Veggie", "Dairy"]), "Food_Skyy_Rice_Bowl": (3, ["Veggie", "Grain"]), "Food_Skyy_Fruit_Medley": (3, ["Fruit"]),
       "Food_Skyy_Chilli_Pot": (3, ["Veggie", "Meat"]), "Food_Skyy_Mushroom_Stew": (3, ["Veggie", "Mushroom"]),
       "Food_Skyy_Hearty_Stew": (3, ["Veggie", "Meat", "Mushroom"]), "Food_Skyy_Lunch_Tray": (3, ["Fruit", "Meat", "Mushroom", "Grain"])}
FAMS_V = {"Food_Wildmeat_Cooked": ["Meat"], "Food_Fish_Grilled": ["Dairy"], "Food_Vegetable_Cooked": ["Veggie"], "Food_Bread": ["Grain"],
          "Food_Kebab_Fruit": ["Fruit"], "Food_Kebab_Meat": ["Meat"], "Food_Kebab_Mushroom": ["Mushroom"], "Food_Kebab_Vegetable": ["Veggie"],
          "Food_Salad_Berry": ["Veggie", "Fruit"], "Food_Salad_Mushroom": ["Veggie", "Mushroom"], "Food_Popcorn": ["Grain"],
          "Food_Pie_Apple": ["Fruit", "Grain"], "Food_Pie_Meat": ["Meat", "Grain"], "Food_Pie_Pumpkin": ["Veggie", "Grain"],
          "Food_Salad_Caesar": ["Veggie", "Meat", "Dairy"]}
RAW = {"Food_Beef_Raw": ("Meat", 0.5), "Food_Chicken_Raw": ("Meat", 0.5), "Food_Pork_Raw": ("Meat", 0.5), "Food_Wildmeat_Raw": ("Meat", 0.5),
       "Food_Fish_Raw": ("Dairy", 0.5), "Food_Egg": ("Dairy", 0.5), "Food_Cheese": ("Dairy", 1.0)}
PART = {"Veggie": {"Health": 1.0}, "Fruit": {"Mana": 1.0}, "Meat": {"Stamina": 1.0}, "Mushroom": {"Strength": 1.0},
        "Grain": {"Health": 0.5, "Stamina": 0.5}, "Dairy": {"Mana": 0.5, "Stamina": 0.5}}
SHARE = {1: 1.0, 2: 0.6, 3: 0.45, 4: 0.36}
ALL = {1: 0.0, 2: 0.15, 3: 0.25}
INST = {"Health": (5.0, 8.0, 12.0), "Mana": (5.0, 8.0, 12.0), "Stamina": (10.0, 20.0, 30.0)}
ICAP = {"Health": 60.0, "Mana": 100.0, "Stamina": 100.0}
OVER = {"Health": (0.5, 0.8, 1.2), "Mana": (0.5, 0.8, 1.2), "Stamina": (10.0, 20.0, 30.0), "Strength": (2.0, 4.0, 6.0)}
OCAP = {"Health": 6.0, "Mana": 6.0, "Stamina": 150.0, "Strength": 20.0}
STEP = math.log(1.05)


def S(g):
    return 1.0 + 0.32 * g


def weights(fams, tier, raw=False):
    w = {}
    for f in fams:
        for b, x in PART[f].items():
            w[b] = w.get(b, 0.0) + SHARE[len(fams)] * x
    if not raw:
        for b in ("Health", "Mana", "Stamina"):
            if b not in w and ALL[tier]:
                w[b] = ALL[tier]
    return w


def run_assets(out, jar, scratch, _home):
    K = HK.Child(out)
    AZ = zipfile.ZipFile(SJ.assets_zip())
    an = AZ.namelist()

    def ids(prefix):
        return dict((os.path.basename(n)[:-5], n) for n in an if n.startswith(prefix) and n.endswith(".json"))
    VE, VI, VR, VIT, VRT = ids("Server/Entity/Effects/"), ids("Server/Item/Interactions/"), ids("Server/Item/RootInteractions/"), ids("Server/Item/Items/"), ids("Server/Item/ResourceTypes/")
    common = set(n for n in an if n.startswith("Common/"))
    vrd = lambda n: json.loads(AZ.read(n).decode("utf-8-sig"))
    Z, Z7 = zipfile.ZipFile(jar), zipfile.ZipFile(OLD7_JAR)
    rd = lambda z, n: json.loads(z.read(n).decode("utf-8-sig"))

    def gen(z, pre, deep=False):
        return dict((os.path.basename(n)[:-5], n) for n in z.namelist() if n.startswith(pre) and n.endswith(".json") and (deep or "/" not in n[len(pre):]))
    GE, GI = gen(Z, EFF), gen(Z, INT)
    GD = gen(Z, ITM, deep=True)
    OV = dict((i, VIT[i]) for i in list(FAMS_V) + list(RAW) if VIT.get(i) in Z.namelist())
    ITEMS = dict(GD)
    ITEMS.update(OV)
    # ---------------- R
    errs = []

    def need(pool, gpool, i, where):
        if not isinstance(i, str) or (i not in pool and i not in gpool):
            errs.append("%s -> %r" % (where, i))

    def walk(node, where):
        if isinstance(node, str):
            need(VI, GI, node, where)
            return
        if isinstance(node, list):
            for x in node:
                walk(x, where)
            return
        if not isinstance(node, dict):
            return
        for k, v in node.items():
            if k == "EffectId" and isinstance(v, dict):
                continue
            if k in ("EffectId", "EntityEffectId"):
                need(VE, GE, v, where)
            elif k == "EntityEffectIds":
                for x in v:
                    need(VE, GE, x, where)
            elif k == "Parent":
                need(VI, GI, v, where)
            elif k in ("Interactions", "Next", "Failed"):
                walk(v if not (k == "Next" and isinstance(v, dict) and "Type" not in v and "Parent" not in v) else list(v.values()), where)
            elif k == "DefaultValue" and str(node.get("Var", "")).startswith("Skyy_Cook_Apply_"):
                walk(v.get("Interactions", []), where)
    for i, n in GI.items():
        walk(rd(Z, n), "interaction " + i)
    for i, n in GE.items():
        p = rd(Z, n).get("StatusEffectIcon")
        if p and "Common/" + p not in common:
            errs.append("effect %s icon %s" % (i, p))
    for i, n in ITEMS.items():
        o = rd(Z, n)
        if o.get("Parent"):
            need(VIT, ITEMS, o.get("Parent"), "item %s Parent" % i)
        for typ, root in (o.get("Interactions") or {}).items():
            if isinstance(root, str):
                need(VR, {}, root, "item %s %s" % (i, typ))
            else:
                walk(root, "item %s %s" % (i, typ))
        for var, vv in (o.get("InteractionVars") or {}).items():
            walk(vv.get("Interactions", []), "item %s %s" % (i, var))
        for p in [o.get("Icon"), (o.get("BlockType") or {}).get("CustomModel")] + [t.get("Texture") for t in (o.get("BlockType") or {}).get("CustomModelTexture", [])]:
            if p and "Common/" + p not in common:
                errs.append("item %s file Common/%s" % (i, p))
        for inp in (o.get("Recipe") or {}).get("Input", []):
            if "ItemId" in inp:
                need(VIT, ITEMS, inp["ItemId"], "recipe %s input" % i)
            elif inp.get("ResourceTypeId") not in VRT:
                errs.append("recipe %s resource type %s" % (i, inp.get("ResourceTypeId")))
    K.check(not errs, "R: every id / Common file named by the %d effects, %d interactions, %d items exists in the jar or the cached Assets.zip: %s"
            % (len(GE), len(GI), len(ITEMS), errs[:8]))
    # ---------------- F: families from the recipes
    def fam(kind, i):
        if kind == "R":
            return {"Meats": "Meat", "Vegetables": "Veggie", "Fruits": "Fruit", "Mushrooms": "Mushroom", "Fuel": None, "Flowers": None}[i]
        if i in ("Food_Fish_Raw", "Food_Egg", "Food_Cheese"):
            return "Dairy"
        if i in ("Ingredient_Dough", "Ingredient_Flour", "Plant_Crop_Corn_Item", "Plant_Crop_Rice_Item", "Plant_Crop_Wheat_Item"):
            return "Grain"
        if i in ("Ingredient_Stick", "Ingredient_Salt", "Ingredient_Spices"):
            return None
        if i.startswith("Plant_Fruit_"):
            return "Fruit"
        if i.startswith("Plant_Crop_"):
            return "Veggie"
        raise KeyError(i)
    fbad = []
    order = ["Veggie", "Fruit", "Meat", "Mushroom", "Grain", "Dairy"]
    for d in list(FAMS_V) + list(OWN):
        r = (vrd(VIT[d]) if d in FAMS_V else rd(Z, GD[d])).get("Recipe")
        fs = []
        for x in r["Input"]:
            f = fam("R", x["ResourceTypeId"]) if "ResourceTypeId" in x else fam("I", x["ItemId"])
            if f and f not in fs:
                fs.append(f)
        want = FAMS_V[d] if d in FAMS_V else OWN[d][1]
        if sorted(fs, key=order.index) != sorted(want, key=order.index):
            fbad.append((d, fs, want))
    K.check(not fbad, "F: the families of all 26 dishes, read from their recipes, = the table: %s" % fbad)
    # ---------------- N: numbers of every food item
    def tier_of(o):
        return int(re.match(r"^Root_Secondary_Consume_Food_T([123])$", (o.get("Interactions") or {}).get("Secondary") or "Root_Secondary_Consume_Food_T1").group(1))

    def fx_of(eid):
        return rd(Z, GE[eid])

    def check_item(i, o, fams, tier, g, raw=None):
        bad = []
        w = weights(fams, tier, raw is not None)
        iv = o["InteractionVars"]
        ch = iv["Effect"]["Interactions"]
        inst = ch[0]["EffectId"] if isinstance(ch[0], dict) else None
        for b in ("Health", "Mana", "Stamina"):
            want = min(INST[b][tier - 1] * w[b] * S(g) * (raw if raw is not None else 1.0), ICAP[b]) if b in w else None
            got = (inst or {}).get("StatModifiers", {}).get(b)
            if (want is None) != (got is None) or (want is not None and abs(got - want) > 0.0051):
                bad.append("%s instant %s %s != %s" % (i, b, got, want))
        if inst and (inst.get("ValueType") != "Percent" or inst.get("Duration") != 0.1 or inst.get("DamageCalculatorCooldown") != 0):
            bad.append("%s instant shape %s" % (i, inst))
        chks = [x for x in ch[1:]]
        for b in ("Health", "Mana", "Stamina", "Strength"):
            mine = [c for c in chks if c.startswith("Skyy_Cook_Chk_%s_" % b)]
            if raw is not None or b not in w:
                if mine or ("Skyy_Cook_Apply_" + b) in iv:
                    bad.append("%s has a %s over-time part it should not" % (i, b))
                continue
            want = min(OVER[b][tier - 1] * w[b] * S(g), OCAP[b])
            ap = iv.get("Skyy_Cook_Apply_" + b, {}).get("Interactions", [{}])[0]
            if len(mine) != 1 or ap.get("Type") != "ApplyEffect" or ap.get("EffectId") != "Skyy_Cook_Fx_%s_%s" % (b, mine[0].rsplit("_", 1)[1]):
                bad.append("%s %s check / var mismatch %s %s" % (i, b, mine, ap))
                continue
            if abs(ap["Duration"] - (min(round(360.0 * 2 ** (g / 5.0), 2), 600.0) if b == "Strength" else round(360.0 * 2 ** (g / 5.0), 2))) > 0.011:
                bad.append("%s %s duration %s" % (i, b, ap["Duration"]))
            e = fx_of(ap["EffectId"])
            if b == "Health":
                v = e["StatModifiers"]["Health"]
                ok = e.get("ValueType") == "Percent" and e.get("DamageCalculatorCooldown") == 2 and \
                    abs(e["RawStatModifiers"]["Health"][0]["Amount"] - (1 + min(v * 10 / 1.2, 50) / 100)) < 1e-4
            elif b == "Mana":
                v = e["StatModifiers"]["Mana"]
                ok = e.get("ValueType") == "Percent" and e.get("DamageCalculatorCooldown") == 2 and list(e["StatModifiers"]) == ["Mana"]
            elif b == "Stamina":
                v = (e["RawStatModifiers"]["Stamina"][0]["Amount"] - 1) * 100
                ok = abs(e["StatModifiers"]["Stamina"] - v / 600) < 1e-4 and e.get("DamageCalculatorCooldown") == 0.1 and "ValueType" not in e
            else:
                od = e["OutgoingDamage"]
                v = od["Physical"][0]["Amount"] * 100
                ok = sorted(od) == ["Elemental", "Physical", "Projectile"] and all(od[c] == [{"CalculationType": "Percent", "Amount": od["Physical"][0]["Amount"]}] for c in od)
            if not ok or abs(math.log(v / want)) > STEP / 2 + 1e-3:
                bad.append("%s %s over time %s vs %s (%s)" % (i, b, v, want, ok))
        return bad
    nbad, n_items = [], 0
    for d in DISHES + list(OWN):
        fams, tier = (FAMS_V[d], tier_of(vrd(VIT[d]))) if d in FAMS_V else (OWN[d][1], OWN[d][0])
        src = OV[d] if d in FAMS_V else GD[d]
        nbad += check_item(d, rd(Z, src), fams, tier, 0)
        n_items += 1
        for g in range(1, 13):
            gid = "Skyy_Cook_%s_G%d" % (d, g)
            o = rd(Z, GD[gid])
            nbad += check_item(gid, o, fams, tier, g)
            if tier_of(o) != tier or "Recipe" in o or o.get("Parent") != "Template_Food":
                nbad.append("%s tier / recipe / parent" % gid)
            n_items += 1
    for r, (f, fac) in RAW.items():
        nbad += check_item(r, rd(Z, OV[r]), [f], 1, 0, raw=fac)
        n_items += 1
    K.check(not nbad and n_items == 15 * 13 + 11 * 13 + 7, "N: all %d food items: instant = base x weight x (1 + 0.32 g) (caps), each over-time bar "
            "within half a ladder step of base x weight x S(g), Duration 360 x 2^(g/5) (Strength max 600 s), effect shapes: %s" % (n_items, nbad[:6]))
    # samples for the report
    def sample(d, g):
        o = rd(Z, OV[d] if (g == 0 and d in OV) else GD[d if g == 0 else "Skyy_Cook_%s_G%d" % (d, g)])
        iv = o["InteractionVars"]
        ins = iv["Effect"]["Interactions"][0]["EffectId"]["StatModifiers"]
        ov = {}
        for b in ("Health", "Mana", "Stamina", "Strength"):
            ap = iv.get("Skyy_Cook_Apply_" + b)
            if ap:
                e = fx_of(ap["Interactions"][0]["EffectId"])
                ov[b] = e["StatModifiers"][b] if b in ("Health", "Mana") else (round((e["RawStatModifiers"]["Stamina"][0]["Amount"] - 1) * 100, 1) if b == "Stamina" else round(e["OutgoingDamage"]["Physical"][0]["Amount"] * 100, 2))
        return "%s G%d instant %s over %s" % (d, g, ins, ov)
    for d in ("Food_Vegetable_Cooked", "Food_Pie_Meat", "Food_Skyy_Garden_Skewer"):
        for g in (0, 5, 10):
            K.notes.append(sample(d, g))
    # ---------------- K: stacking checks
    kbad = []
    levels = {}
    for i in GE:
        m = re.match(r"^Skyy_Cook_Fx_(Health|Mana|Stamina|Strength)_(\d+)$", i)
        if m:
            levels.setdefault(m.group(1), []).append(int(m.group(2)))
    for b, ks in levels.items():
        ks.sort()
        for k in ks:
            c = rd(Z, GI["Skyy_Cook_Chk_%s_%d" % (b, k)])
            above = ["Skyy_Cook_Fx_%s_%d" % (b, x) for x in ks if x > k]
            below = ["Skyy_Cook_Fx_%s_%d" % (b, x) for x in ks if x < k]
            ser = c
            if above:
                if c.get("Type") != "EffectCondition" or c.get("Match") != "None" or c.get("EntityEffectIds") != above or c.get("Failed", {}).get("Type") != "Simple":
                    kbad.append("%s %d condition" % (b, k))
                ser = c["Next"]
            elif c.get("Type") != "Serial":
                kbad.append("%s %d top must be Serial" % (b, k))
            its = ser["Interactions"]
            ext = {"Health": ["HealthRegen_Buff_Raw", "HealthRegen_Buff_T1", "HealthRegen_Buff_T2", "HealthRegen_Buff_T3", "Meat_Buff_T1", "Meat_Buff_T2", "Meat_Buff_T3"] +
                   ["Skyy_Cook_%s_Buff_T%d_G%d" % (f, tt, gg) for f in ("HealthRegen", "Meat") for tt in (1, 2, 3) for gg in range(1, 13)],
                   "Stamina": ["FruitVeggie_Buff_T%d" % tt for tt in (1, 2, 3)] + ["Skyy_Cook_FruitVeggie_Buff_T%d_G%d" % (tt, gg) for tt in (1, 2, 3) for gg in range(1, 13)]}.get(b, [])
            if sorted(x.get("EntityEffectId") for x in its[:-1]) != sorted(below + ext) or any(x.get("Type") != "ClearEntityEffect" for x in its[:-1]) \
                    or its[-1].get("Type") != "Replace" or its[-1].get("Var") != "Skyy_Cook_Apply_" + b \
                    or its[-1]["DefaultValue"]["Interactions"][0]["EffectId"] != "Skyy_Cook_Fx_%s_%d" % (b, k):
                kbad.append("%s %d serial" % (b, k))
        # strength order = level order
        vals = []
        for k in ks:
            e = fx_of("Skyy_Cook_Fx_%s_%d" % (b, k))
            vals.append(e["StatModifiers"][b] if b in ("Health", "Mana") else (e["RawStatModifiers"]["Stamina"][0]["Amount"] if b == "Stamina" else e["OutgoingDamage"]["Physical"][0]["Amount"]))
        if vals != sorted(vals) or len(set(vals)) != len(vals):
            kbad.append("%s levels not strictly increasing" % b)
    K.check(not kbad and sorted(levels) == ["Health", "Mana", "Stamina", "Strength"] and
            len([i for i in GI if i.startswith("Skyy_Cook_Chk_")]) == sum(len(v) for v in levels.values()),
            "K: stacking - %s levels; every check names exactly the stronger levels (Match None), clears exactly the weaker ones (+ the vanilla "
            "regen / max-health buffs and the 0.1.7 buffs of its bar for Health and Stamina), then Replaces its bar's var: %s" % (dict((b, len(v)) for b, v in levels.items()), kbad[:6]))
    # ---------------- O: overrides
    obad = []
    for i, n in OV.items():
        a, v = rd(Z, n), vrd(VIT[i])
        aa, vv = json.loads(json.dumps(a)), json.loads(json.dumps(v))
        for x in (aa, vv):
            tp = x.pop("TranslationProperties", {}) or {}
            tp.pop("Description", None)
            x["_tp"] = tp
            for k in [k for k in x.get("InteractionVars", {}) if k in ("Effect", "Consume_Charge") or k.startswith("Skyy_Cook_Apply_")]:
                del x["InteractionVars"][k]
        if aa != vv or a["TranslationProperties"]["Description"] != "server.items.Skyy_Cook_%s_G0.description" % i or a.get("Recipe") != v.get("Recipe"):
            obad.append(i)
    K.check(len(OV) == 22 and not obad, "O: the %d vanilla overrides (15 dishes + 7 raw) sit at the vanilla path and change only the eat vars + the "
            "description key (Recipe, Parent, model, Quality kept): %s" % (len(OV), obad))
    # ---------------- E: eating
    van = vrd(VI["Consume_Charge_Food_T1_Inner"])
    fast = rd(Z, GI["Skyy_Cook_Consume_Charge_Food_T1_Inner_Fast"])
    t0 = list(van["Next"])[0]
    w = json.loads(json.dumps(van))
    w["Next"] = {"%g" % (float(t0) * 0.75): w["Next"][t0]}
    w["FailOnDamage"] = False
    K.check(fast == w and van.get("FailOnDamage") is False and t0 == "2.5" and list(fast["Next"]) == ["1.875"],
            "E: the fast charge = vanilla T1_Inner (2.5 s, FailOnDamage false) with 1.875 s, FailOnDamage false")
    ebad = [i for i, n in ITEMS.items() if "Recipes/" not in n and
            [e.get("Parent") for e in rd(Z, n)["InteractionVars"]["Consume_Charge"]["Interactions"]] != ["Skyy_Cook_Consume_Charge_Food_T1_Inner_Fast"]]
    K.check(not ebad, "E: every food item of the jar eats through the fast charge: %s" % ebad[:5])
    K.check(not [n for n in Z.namelist() if "RootInteractions" in n or "Potion" in os.path.basename(n)], "E: no root interaction / potion file in the jar (potions keep vanilla)")
    # ---------------- T (0.1.9): tooltips - the Strength line names its own time exactly when the 10 min cap binds
    lang = Z.read("Server/Languages/en-US/server.lang").decode("utf8")
    tbad, tn = [], 0
    for mm in re.finditer(r"^items\.(Skyy_Cook_Food_\w+?_G(\d+))\.description=(.*)$", lang, re.M):
        txt, g = mm.group(3), int(mm.group(2))
        if "Strength +" not in txt: continue
        tn += 1
        capped = 360.0 * 2 ** (g / 5.0) > 600.5
        if (", for 10:00)" in txt) != capped: tbad.append(mm.group(1))
    K.check(tn > 0 and not tbad, "T: %d graded Strength tooltips; ', for 10:00' exactly on the capped Grades (G4+): %s" % (tn, tbad[:5]))
    # ---------------- L: legacy
    l7 = gen(Z7, EFF)
    K.check(len(l7) == 144 and all(i in GE and Z.read(GE[i]) == Z7.read(n) for i, n in l7.items()), "L: the 144 0.1.7 effect files are byte-equal in 0.1.8")
    i7 = gen(Z7, ITM, deep=True)
    K.check(len(i7) == 183 and all(i in GD for i in i7), "L: every 0.1.7 item id (180 graded + 3 recipe variants) is still in the jar")
    K.check(all(Z.read(GD[i]) == Z7.read(n) for i, n in i7.items() if i.startswith("Skyy_Cook_Recipe_")), "L: the 3 recipe variants are byte-equal")
    K.save()


def run_java(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Hk = J("CookCfg"), J("CookHooks")
    Paths = JClass("java.nio.file.Paths")
    d = os.path.join(scratch, "java", "Skyy_SkyyCooking")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "cooking.properties")
    Cfg.FILE = Paths.get(f)
    own = list(OWN)
    # missing file -> the default text
    s = str(Cfg.load())
    t = open(f, encoding="latin-1").read()
    K.check("gradedOwn=true" in t and ("graded=" + ",".join(DISHES + own)) in t and bool(Cfg.OWN_GRADED) and "own dishes always graded" in s,
            "J1 missing file: written with gradedOwn=true and every dish on graded=; load says %s" % s[:120])
    K.check(all(int(Cfg.tierOf(o)) == OWN[o][0] for o in own) and int(Cfg.tierOf("Food_Pie_Meat")) == 3 and int(Cfg.tierOf("Food_Cheese")) == 0,
            "J1 tierOf: own dishes their tier, vanilla dishes theirs, a non-dish 0")
    K.check(all(int(Cfg.xpFor(o)) > 0 for o in own) and int(Cfg.xpFor("Food_Skyy_Garden_Skewer")) == int(Cfg.xpFor("Food_Kebab_Vegetable")),
            "J1 xpFor: every own dish has a built-in XP value (Garden Skewer = Vegetable Skewer, same raw count)")
    # live shape: graded= lists only the 15 vanilla dishes, no gradedOwn line
    live = t.replace("graded=" + ",".join(DISHES + own), "graded=" + ",".join(DISHES)).replace("gradedOwn=true\n", "")
    open(f, "w", encoding="latin-1", newline="").write(live)
    s = str(Cfg.load())
    K.check(bool(Cfg.OWN_GRADED) and all(int(Cfg.tierOf(o)) == OWN[o][0] for o in own) and int(Cfg.tierOf("Food_Bread")) == 2,
            "J2 a 0.1.7-shape file (graded= 15 vanilla dishes, no gradedOwn line): own dishes still graded: %s" % s[:100])
    K.check(open(f, encoding="latin-1").read() == live, "J2 load never rewrites the file")
    open(f, "w", encoding="latin-1", newline="").write(live + "gradedOwn=false\n")
    Cfg.load()
    K.check(not bool(Cfg.OWN_GRADED) and all(int(Cfg.tierOf(o)) == 0 for o in own) and int(Cfg.tierOf("Food_Bread")) == 2,
            "J3 gradedOwn=false: own dishes plain unless the list names them, vanilla dishes by the list")
    open(f, "w", encoding="latin-1", newline="").write(live.replace("graded=" + ",".join(DISHES), "graded=Food_Bread," + own[0]) + "gradedOwn=false\n")
    Cfg.load()
    K.check(int(Cfg.tierOf(own[0])) == 2 and int(Cfg.tierOf(own[1])) == 0 and int(Cfg.tierOf("Food_Pie_Meat")) == 0,
            "J4 gradedOwn=false + an own dish on the list: that one graded, the others plain")
    open(f, "w", encoding="latin-1", newline="").write(live + "gradedOwn=maybe\n")
    Cfg.load()
    K.check(bool(Cfg.OWN_GRADED), "J5 a bad gradedOwn value = the default (on)")
    K.check(Hk.checkGraded("graded", ",".join(DISHES + own)) is None and Hk.checkGraded("graded", "Food_Cheese") is not None,
            "J6 CookHooks.checkGraded accepts every graded dish, refuses a non-dish")
    K.check(list(Cfg.DISHES) == DISHES + own and int(Cfg.N_VAN) == 15, "J7 CookCfg.DISHES = 15 vanilla then the 11 own dishes")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Snd, CP = J("CookCfg"), J("CookSnd"), J("CfgPub")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    c0 = open(os.path.join(home, "cooking.properties"), "rb").read()
    snaps, migs = [], []
    import time
    for start in (1, 2):
        Cfg.FILE = Paths.get(os.path.join(home, "cooking.properties"))
        migs.append([str(J(m).migrate()) for m in ("CookMig", "CookXpMig", "CookTblMig", "CookIngMig")])
        s = str(Cfg.load())
        Snd.load(Paths.get(home))
        CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCooking"))
        K.check(all(int(Cfg.tierOf(o)) == OWN[o][0] for o in OWN), "DS%d: own dishes come out graded on the live file (%s)" % (start, s[:90]))
        CP.flush()
        time.sleep(0.6)
        CP.shutdown()
        snaps.append(HK.tree_hash(home))
        time.sleep(1.1)
    K.check(migs == [["", "", "", ""], ["", "", "", ""]], "DS: no one-time update runs on the live cooking.properties: %s" % migs)
    K.check(open(os.path.join(home, "cooking.properties"), "rb").read() == c0, "DS: the live cooking.properties is byte-identical after two starts")
    K.check(snaps[0] == snaps[1], "DS: the second start changes nothing")
    K.notes.append("live tree first start %s" % ("unchanged" if snaps[0] == h0 else "changed (kit files)"))
    K.save()


# ---- C: non-class entries: manifest, lang, the SkyyCook asset folders and the 22 override paths; the 108 old checks gone
_orig_compare = HK.run_compare
OVR_PATHS = None


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    orig_eq = HK.Child.eq

    def eq(self, got, want, what):
        if what != "C: non-class entries changed":
            return orig_eq(self, got, want, what)
        za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
        AZ = zipfile.ZipFile(SJ.assets_zip())
        van = set(n for n in AZ.namelist() if n.startswith("Server/Item/Items/"))
        ovr = sorted(n for n in zb.namelist() if n in van)
        ok = all(n in ("manifest.json", "Server/Languages/en-US/server.lang") or n.startswith(ITM) or n in ovr for n in got)
        gone = sorted(n for n in za.namelist() if n not in zb.namelist())
        ok = ok and len(ovr) == 22 and not gone
        ok = ok and not any(n.startswith((EFF, INT)) and za.read(n) != zb.read(n) for n in za.namelist() if n.startswith((EFF, INT)))
        return self.check(ok and "manifest.json" in got, "C: non-class entries changed = manifest + lang + item files only (SkyyCook items + "
                          "%d vanilla override paths); nothing gone; every effect + interaction byte-equal: %d changed, %d gone" % (len(ovr), len(got), len(gone)))
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = orig_eq


HK.run_compare = _compare

if __name__ == "__main__":
    HK.run(name="SkyyCooking", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("assets", run_assets), ("java", run_java), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyCooking"))
