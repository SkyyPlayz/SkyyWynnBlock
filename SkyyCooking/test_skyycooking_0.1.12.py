"""Harness for SkyyCooking 0.1.12 (tools/cooking_0_1_12_patch.py): OUR OWN PIES, SALAD, DRINKS, BUTTER + SLICED BREAD (lean round cook12),
on top of the 0.1.11 Supplies checks (copied from test_skyycooking_0.1.11.py, counts updated for the 12 new dishes).
Skyy 2026-10-18 (docs/answered/project.md, popup): Q "Connor's More Food Stuff has no licence and uses heal effects missing from the
current game, so it can't be packed yet. What now?" -> "Make our own dishes".
Build first: python tools/cooking_0_1_12_patch.py && python SkyyCooking/build_skyycooking_0.1.12.py

    python SkyyCooking/test_skyycooking_0.1.12.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py; game files only through the CACHED copies of tools/serverjar.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.11 -> 0.1.12: only data / version members differ (the version texts, CookCfg's dish tables, the XP table + default
                lines, the config rows' graded list, SupDefs' pouch table); non-class entries: only the 12 dishes' files (Grade 0, G1-G12,
                their Food Pouch ids), the new ladder steps' effect + check files, the changed ladder checks, manifest + lang; nothing
                gone; every older dish / override / Supplies file byte-equal
  N    dishes   (pure Python, its OWN copy of the rules - independent of the build script) against the cached Assets.zip:
                N1 the 12 ids (Food_Skyy_ prefix, not vanilla), Cooking Bench recipe (vanilla bench + category), every input a real
                   vanilla item / '*'-state / resource type, output = itself (+ Container_Bucket per milk bucket, + Deco_Tankard per water
                   tankard), vanilla ingredients only (no Skyy_ / pack-mod input)
                N2 every look file (icon, model, textures, model animation, player animations) is in Assets.zip and not in the jar;
                   drinks: the vanilla filled Tankard / Mug look, the drink animation, the eat charge's "Consume" animation, drink sounds
                   that exist in Assets.zip; Quality by tier (T1 Common, T2 Uncommon, T3 Rare); eat root Root_Secondary_Consume_Food_T<tier>
                N3 every interaction / effect the 12 x 13 items name exists (jar or Assets.zip); no file of the jar names
                   Food_Instant_Heal_T2 / T3 (missing from the current game)
                N4 numbers: families from the recipe; the inline instant = base x weight x (1 + 0.32 g) (caps); the applied over-time effect
                   within half a ladder step of base x weight x S(g); Duration 360 x 2^(g/5) (cap); the effect JSON shape per bar
                N5 graded copies G1-G12: no Recipe, Quality never below the grade's, lang "<name> (Grade g)"; lang name + description
                   for every id (both prefixes); a tooltip names only its dish's bars
                N6 the Food Pouch has a loaded id for each of the 156 new food items
  J    java     CookCfg (bare JVM, -Xverify:all): DISHES = 15 vanilla, then the 23 own dishes sorted by tier then name; tierOf = tier;
                xpFor = the default file's xp line (built-in, > 0); a live-shape file (old graded= list) still grades the new dishes
  SJ   java     the 0.1.11 Supplies store checks (pouch table now 501 ids)
  LF/LP life    tools/skyyonce_harness.py life_phase for FlaskOnce / PouchOnce
  D    live     setup()'s data steps TWICE on a scratch COPY of the live Skyy_SkyyCooking (world NewBetaTest): no Cooking update runs,
                cooking.properties untouched, the second start changes nothing
  AA   engine-access audit
NOT testable here (UNVERIFIED until the game runs it): the Cooking Bench showing the recipes (and their order), the tankard / bucket
coming back from a real craft, the drink animation + sounds on a food chain, the client drawing the borrowed models. Exit code 1 on any failure.
"""
import os, sys, json, zipfile, re, copy, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import serverjar as SJ

VERSION = "0.1.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCooking-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCooking-0.1.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "cook12", "harness")))
PKG = "com.skyy.cooking."
LIVE_DIR = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData", "Saves", "NewBetaTest", "mods", "Skyy_SkyyCooking")
EXPECT = {
    # 0.1.12: the "SkyyCooking 0.1.12" version text (default file header, kit header / export, migration WHO, ready line, supplies header)
    # + the data tables: CookCfg's DISHES / NAMES / XP tables + default lines, the config rows' graded list, SupDefs' pouch table
    "CookCfg": ["~<clinit>", "~m load"], "CookMig": ["~m logLine", "~m migrate"], "CookXpMig": ["~m migrate"], "CookTblMig": ["~m migrate"],
    "CookIngMig": ["~m migrate"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "SkyyCookingPlugin": ["~m setup"],
    "SupCfg": ["~m load"], "SupDefs": ["~<clinit>"],
}
ADDED = []
SUP = "Server/Item/Items/SkyyCook/Supplies/"
SUPI, SUPR, SUPX = "Server/Item/Interactions/SkyyCook/Supplies/", "Server/Item/RootInteractions/SkyyCook/Supplies/", "Server/Entity/Effects/SkyyCook/Supplies/"
POTIONS = ["Potion_Health_Lesser", "Potion_Health_Small", "Potion_Health", "Potion_Health_Greater", "Potion_Health_Large"]
RAW = ["Food_Beef_Raw", "Food_Chicken_Raw", "Food_Pork_Raw", "Food_Wildmeat_Raw", "Food_Fish_Raw", "Food_Egg", "Food_Cheese"]
N_POUCH = 345 + 12 * 13                       # 0.1.11's 345 + the 12 new dishes x (Grade 0 + G1-G12)
N_SUP = 5 + N_POUCH + 2

# ---- 0.1.12: the new dishes, written out again (independent of the build script): id -> (name, tier, families, kind of look)
NEW = {"Food_Skyy_Butter": ("Butter", 1, ["Dairy"], "cheese"), "Food_Skyy_Sliced_Bread": ("Sliced Bread", 1, ["Grain"], None),
       "Food_Skyy_Berry_Cordial": ("Berry Cordial", 1, ["Fruit"], "tankard"), "Food_Skyy_Vegetable_Broth": ("Vegetable Broth", 1, ["Veggie"], "tankard"),
       "Food_Skyy_Farmhouse_Salad": ("Farmhouse Salad", 2, ["Veggie", "Dairy"], None), "Food_Skyy_Spiced_Cider": ("Spiced Cider", 2, ["Fruit"], "tankard"),
       "Food_Skyy_Pinkberry_Milkshake": ("Pinkberry Milkshake", 2, ["Fruit", "Dairy"], "mug"),
       "Food_Skyy_Tropical_Smoothie": ("Tropical Smoothie", 3, ["Fruit", "Dairy"], "mug"),
       "Food_Skyy_Cottage_Pie": ("Cottage Pie", 3, ["Veggie", "Meat", "Grain"], None), "Food_Skyy_Fisherman_Pie": ("Fisherman's Pie", 3, ["Veggie", "Grain", "Dairy"], None),
       "Food_Skyy_Coconut_Cream_Pie": ("Coconut Cream Pie", 3, ["Fruit", "Grain", "Dairy"], None),
       "Food_Skyy_Forager_Pie": ("Forager's Pie", 3, ["Veggie", "Mushroom", "Grain"], None)}
OLD_OWN = {"Food_Skyy_Garden_Skewer": ("Garden Skewer", 2), "Food_Skyy_Hunter_Skewer": ("Hunter's Skewer", 2), "Food_Skyy_Forest_Skewer": ("Forest Skewer", 2),
           "Food_Skyy_Woodland_Skewer": ("Woodland Skewer", 2), "Food_Skyy_Omelette": ("Omelette", 2), "Food_Skyy_Rice_Bowl": ("Rice Bowl", 3),
           "Food_Skyy_Fruit_Medley": ("Fruit Medley", 3), "Food_Skyy_Chilli_Pot": ("Chilli Pot", 3), "Food_Skyy_Mushroom_Stew": ("Mushroom Stew", 3),
           "Food_Skyy_Hearty_Stew": ("Hearty Stew", 3), "Food_Skyy_Lunch_Tray": ("Lunch Tray", 3)}
VAN_DISHES = ["Food_Wildmeat_Cooked", "Food_Fish_Grilled", "Food_Vegetable_Cooked", "Food_Bread", "Food_Kebab_Fruit", "Food_Kebab_Meat",
              "Food_Kebab_Mushroom", "Food_Kebab_Vegetable", "Food_Salad_Berry", "Food_Salad_Mushroom", "Food_Popcorn", "Food_Pie_Apple",
              "Food_Pie_Meat", "Food_Pie_Pumpkin", "Food_Salad_Caesar"]
ALL_OWN = dict([(i, (v[0], v[1])) for i, v in NEW.items()] + list(OLD_OWN.items()))
OWN_ORDER = sorted(ALL_OWN, key=lambda i: (ALL_OWN[i][1], ALL_OWN[i][0]))
FAMS = ["Veggie", "Fruit", "Meat", "Mushroom", "Grain", "Dairy"]
FAM_ITEM = {"Food_Fish_Raw": "Dairy", "Food_Egg": "Dairy", "Food_Cheese": "Dairy", "Ingredient_Dough": "Grain"}
FAM_RT = {"Meats": "Meat", "Vegetables": "Veggie", "Fruits": "Fruit", "Mushrooms": "Mushroom", "Milk_Bucket": "Dairy"}
NO_FAM = ["Ingredient_Salt", "Ingredient_Spices", "*Deco_Tankard_State_Filled_Water", "Fuel"]
PART = {"Veggie": {"Health": 1.0}, "Fruit": {"Mana": 1.0}, "Meat": {"Stamina": 1.0}, "Mushroom": {"Strength": 1.0},
        "Grain": {"Health": 0.5, "Stamina": 0.5}, "Dairy": {"Mana": 0.5, "Stamina": 0.5}}
SHARE = {1: 1.0, 2: 0.6, 3: 0.45, 4: 0.36}
INST = {"Health": (5.0, 8.0, 12.0), "Mana": (5.0, 8.0, 12.0), "Stamina": (10.0, 20.0, 30.0)}
ICAP = {"Health": 60.0, "Mana": 100.0, "Stamina": 100.0}
OVER = {"Health": (0.5, 0.8, 1.2), "Mana": (0.5, 0.8, 1.2), "Stamina": (10.0, 20.0, 30.0), "Strength": (2.0, 4.0, 6.0)}
OCAP = {"Health": 6.0, "Mana": 6.0, "Stamina": 150.0, "Strength": 20.0}
STEP = math.log(1.05)
QORDER = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]


def S(g):
    return 1.0 + 0.32 * g


def fam_of(inp):
    if inp.get("ResourceTypeId"):
        x = inp["ResourceTypeId"]
        return None if x in NO_FAM else FAM_RT[x]
    x = inp["ItemId"]
    if x in NO_FAM:
        return None
    if x in FAM_ITEM:
        return FAM_ITEM[x]
    if x.startswith("Plant_Fruit_"):
        return "Fruit"
    if x.startswith("Plant_Crop_") and x.endswith("_Item"):
        return "Veggie"
    raise KeyError(x)


def base(n):
    return n.rsplit("/", 1)[1][:-5]


# ================================================================================================= SA: assets (own rules)
def run_assets(out, jar, scratch, _home):
    K = HK.Child(out)
    AZ = zipfile.ZipFile(SJ.assets_zip())
    an = set(AZ.namelist())
    Z = zipfile.ZipFile(jar)
    zn = Z.namelist()
    rdz = lambda n: json.loads(Z.read(n).decode("utf-8-sig"))
    rda = lambda n: json.loads(AZ.read(n).decode("utf-8-sig"))

    def ids(names, pre):
        return dict((base(n), n) for n in names if n.startswith(pre) and n.endswith(".json"))
    VIT, VI, VR, VE = ids(an, "Server/Item/Items/"), ids(an, "Server/Item/Interactions/"), ids(an, "Server/Item/RootInteractions/"), ids(an, "Server/Entity/Effects/")
    JIT, JI, JR, JE = ids(zn, "Server/Item/Items/"), ids(zn, "Server/Item/Interactions/"), ids(zn, "Server/Item/RootInteractions/"), ids(zn, "Server/Entity/Effects/")
    # the jar's own file of a vanilla id (an override) wins
    ITEMS = dict((i, ("a", n)) for i, n in VIT.items())
    for i, n in JIT.items():
        ITEMS[i] = ("j", n)

    def raw(i):
        z, n = ITEMS[i]
        return rdz(n) if z == "j" else rda(n)

    def flat(i, depth=0):
        d = copy.deepcopy(raw(i))
        p = d.pop("Parent", None)
        if not p:
            return d
        b = flat(p, depth + 1)
        for k, v in d.items():
            if k in ("Interactions", "InteractionVars", "TranslationProperties") and isinstance(v, dict) and isinstance(b.get(k), dict):
                m = dict(b[k])
                m.update(v)
                b[k] = m
            else:
                b[k] = v
        return b
    sup_items = sorted(n for n in zn if n.startswith(SUP) and n.endswith(".json"))
    K.eq(len(sup_items), N_SUP, "SA1 %d Supplies items (5 flask + %d pouch + 2 empty)" % (N_SUP, N_POUCH))
    fl = [base(n) for n in sup_items if base(n).startswith("Skyy_Flask_V_")]
    po = [base(n) for n in sup_items if base(n).startswith("Skyy_Food_Pouch_V_")]
    K.eq(sorted(fl), sorted("Skyy_Flask_V_" + p for p in POTIONS), "SA1 one flask id per vanilla healing potion")
    K.check(len(po) == N_POUCH and not [p for p in po if "Recipe" in p], "SA1 %d pouch ids, no Skyy_Cook_Recipe_* (FP0 finding 3): %d" % (N_POUCH, len(po)))
    K.check(all(("Skyy_Food_Pouch_V_" + r) in po for r in RAW), "SA1 the raw snacks have loaded ids too (pouchRaw works without a rebuild)")
    bad = []
    for n in sup_items:
        o = rdz(n)
        if any(x in o for x in ("BlockType", "Recipe", "Tags", "Categories", "Quality")) or o.get("MaxStack") != 1 or o.get("DropOnDeath") is not False:
            bad.append(base(n))
        if o["TranslationProperties"]["Name"] not in ("server.items.Skyy_Flask.name", "server.items.Skyy_Food_Pouch.name"):
            bad.append(base(n) + " name")
    K.check(not bad, "SA2 every Supplies item: MaxStack 1, DropOnDeath false, no BlockType / Recipe / Tags / Quality (FP0 finding 2), the shared name key: %s" % bad[:5])
    # vars = source vars except the charge Parent
    charges = {}
    diff = []
    for lid in fl + po:
        src = lid.split("_V_", 1)[1]
        o = rdz(SUP + lid + ".json")
        f = flat(src)
        want = copy.deepcopy(f.get("InteractionVars") or {})
        if lid in po:
            for e in want["Consume_Charge"]["Interactions"]:
                charges[e["Parent"]] = None
            got = copy.deepcopy(o["InteractionVars"])
            for e in got["Consume_Charge"]["Interactions"]:
                e["Parent"] = re.sub(r"^Skyy_Supply_Charge_Food_T(\d)_Inner$", r"Skyy_Cook_Consume_Charge_Food_T\1_Inner_Fast", e["Parent"])
            sec_ok = o["Interactions"]["Secondary"] == f["Interactions"]["Secondary"].replace("Root_Secondary_Consume_Food_T", "Skyy_Supply_Root_Food_T")
        else:
            got = o["InteractionVars"]
            sec_ok = o["Interactions"]["Secondary"] == "Skyy_Supply_Root_Potion_Health"
        if json.dumps(got, sort_keys=True) != json.dumps(want, sort_keys=True) or not sec_ok:
            diff.append(lid)
        for k in ("PlayerAnimationsId", "IconProperties", "InteractionConfig", "Consumable"):
            if k in f and o.get(k) != f[k]:
                diff.append(lid + " " + k)
    K.check(not diff, "SA3 every loaded id = its source's flattened InteractionVars except the charge Parent, the right root, the animation fields: %s" % diff[:5])
    # the charge copies
    cbad = []
    for src_c in list(charges) + ["Consume_Charge_Potion_Fast"]:
        our = "Skyy_Supply_Charge_Potion_Fast" if src_c == "Consume_Charge_Potion_Fast" else re.sub(r"^Skyy_Cook_Consume_Charge_Food_T(\d)_Inner_Fast$", r"Skyy_Supply_Charge_Food_T\1_Inner", src_c)
        sv = rdz(JI[src_c]) if src_c in JI else rda(VI[src_c])
        ov = rdz(JI[our])
        t = json.dumps(sv)
        t2 = re.sub(r'\{"Type": "ModifyInventory", "AdjustHeldItemQuantity": -1, "Next"', '{"Type": "ApplyEffect", "EffectId": "Skyy_Supply_Used", "Next"', t)
        if t2 == t or json.loads(t2) != ov or "ModifyInventory" in json.dumps(ov):
            cbad.append(our)
    K.check(not cbad, "SA4 the charge copies = the source charge with the ONE ModifyInventory -1 step swapped for the marker (same time, FailOnDamage false): %s" % cbad)
    cp = rdz(JI["Skyy_Supply_Cond_Potion_Health"])
    vcp = rda(VI["Condition_Consume_Potion_Health"])
    K.check(cp["Next"]["Id"] == "Potion_Consume_Health" and cp["Next"]["Type"] == "CooldownCondition" and cp["Next"]["Next"] == "Skyy_Supply_Charge_Potion_Fast"
            and cp["Failed"] == "Skyy_Supply_Open" and dict(cp, Next=None, Failed=None) == dict(vcp, Next=None, Failed=None),
            "SA5 the flask shares the vanilla 15 s potion cooldown (CooldownCondition Potion_Consume_Health), Adventure + not crouching, Failed -> the page")
    op = rdz(JI["Skyy_Supply_Open"])
    K.check(op == {"Type": "Condition", "Crouching": True, "Next": {"Type": "OpenCustomUI", "Page": {"Id": "SkyySupplies"}}, "Failed": {"Type": "Simple"}},
            "SA5 crouch + right click = OpenCustomUI SkyySupplies (vanilla's crouch branch was Block_Secondary)")
    roots_ok = all(rdz(JR[r]) == {"RequireNewClick": True, "Interactions": [c]} for r, c in (("Skyy_Supply_Root_Potion_Health", "Skyy_Supply_Cond_Potion_Health"),
                   ("Skyy_Supply_Root_Empty", "Skyy_Supply_Cond_Empty"), ("Skyy_Supply_Root_Food_T1", "Skyy_Supply_Cond_Food_T1")))
    K.check(roots_ok, "SA5 every root keeps RequireNewClick (each use its own hold - FP0 finding 4)")
    em = rdz(JI["Skyy_Supply_Cond_Empty"])
    K.check(em["Next"] == {"Type": "ApplyEffect", "EffectId": "Skyy_Supply_Empty"} and em["Crouching"] is False and em["Failed"] == "Skyy_Supply_Open"
            and rdz(SUP + "Skyy_Flask_Empty.json")["Interactions"]["Secondary"] == "Skyy_Supply_Root_Empty", "SA5 the Empty items: right click = the empty marker, crouch = the page")
    K.check(rdz(JE["Skyy_Supply_Used"]) == {"Duration": 0.5, "OverlapBehavior": "Overwrite"} and rdz(JE["Skyy_Supply_Empty"])["Duration"] == 0.5, "SA5 the two markers (0.5 s)")
    # every reference exists
    KI, KF = set(VI) | set(JI) | set(VR) | set(JR), set(VE) | set(JE)
    miss = set()

    def refs(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("PlayerAnimationsId", "DefaultValue"):
                    continue
                if k in ("Parent", "Next", "Failed", "Secondary", "Primary") and isinstance(v, str) and v not in KI:
                    miss.add(v)
                elif k == "Interactions" and isinstance(v, list):
                    miss.update(x for x in v if isinstance(x, str) and x not in KI)
                elif k in ("EffectId", "EntityEffectId") and isinstance(v, str) and v not in KF:
                    miss.add(v)
                elif k == "EntityEffectIds":
                    miss.update(x for x in v if x not in KF)
                if isinstance(v, (dict, list)):
                    refs(v)
        elif isinstance(o, list):
            for x in o:
                refs(x)
    for n in zn:
        if n.startswith((SUP, SUPI, SUPR, SUPX)) and n.endswith(".json"):
            refs(rdz(n))
    K.check(not miss, "SA6 every interaction / effect a Supplies asset names exists (jar or Assets.zip): %s" % sorted(miss)[:10])
    ours = [n for n in zn if n.startswith((SUP, SUPI, SUPR, SUPX))]
    K.check(not [n for n in ours if n in an] and not [base(n) for n in ours if base(n) in VIT or base(n) in VI or base(n) in VE or base(n).startswith("Skyy_Probe_")],
            "SA6 no Supplies path / id overrides Assets.zip or reuses a Skyy_Probe_ id (%d files)" % len(ours))
    common = set(n for n in an if n.startswith("Common/"))
    looks = set()
    for n in sup_items:
        o = rdz(n)
        looks.update("Common/" + o[k] for k in ("Model", "Texture", "Icon"))
    K.check(looks <= common and len(looks) == 6, "SA6 two shared looks (model + texture + icon each) from Assets.zip, no new texture: %s" % sorted(looks - common))
    # order: healing from the effect assets
    def heal(p):
        tot = 0.0
        fx = []

        def walk(o):
            if isinstance(o, dict):
                if o.get("Type") == "ApplyEffect" and isinstance(o.get("EffectId"), str):
                    fx.append(o["EffectId"])
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(flat(p)["InteractionVars"]["Effect"])
        for e in fx:
            d = rda(VE[e])
            h = float(d["StatModifiers"]["Health"])
            tot += h if d["Duration"] <= 0.5 else h * max(1, int(d["Duration"] / d["DamageCalculatorCooldown"]))
        return tot
    hs = dict((p, heal(p)) for p in POTIONS)
    K.check(sorted(POTIONS, key=lambda p: hs[p]) == POTIONS and hs["Potion_Health_Lesser"] < hs["Potion_Health_Small"], "SA7 worst first by total healing: %s" % hs)
    lang = Z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    K.check(all(("%sitems.%s.%s=" % (p, k, s)) in lang for p in ("", "server.") for k in ("Skyy_Flask", "Skyy_Food_Pouch") for s in ("name", "description"))
            and "server.items.Skyy_Flask.name=Potion Flask" in lang and "server.items.Skyy_Food_Pouch.name=Food Pouch" in lang, "SA8 one shared name / description key per item")
    K.eq(len([n for n in zn if n.startswith("Common/UI/Custom/SkyyKit/")]), 59, "SA9 the 59 Sky Window kit textures (the hub page)")
    K.save()


# ================================================================================================= SJ: the store on real engine objects
def run_java(out, jar, scratch, _home):
    from jpype import JClass, JShort, JInt, JLong, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Mod = JClass("java.lang.reflect.Modifier")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)

    def jfield(cls, name):
        c = cls.class_ if hasattr(cls, "class_") else cls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    # the test Item map (the skyyonce_harness / SkyyAccessories 0.5.17 pattern)
    Item = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtC = JClass("javassist.CtNewConstructor")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyCookFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyCookFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    astore = us.allocateInstance(fake.toClass(AS.class_))
    dam = DAM()
    jfield(AS, "assetMap").set(astore, dam)
    jfield(Item, "ASSET_STORE").set(None, astore)
    amap = jfield(DAM, "assetMap").get(dam)
    unknown = Item.UNKNOWN

    def mk_item(iid, stack):
        it = us.allocateInstance(Item.class_)
        for f in Item.class_.getDeclaredFields():
            if Mod.isStatic(f.getModifiers()):
                continue
            f.setAccessible(True)
            f.set(it, f.get(unknown))
        jfield(Item, "id").set(it, iid)
        jfield(Item, "maxStack").setInt(it, int(stack))
        amap.put(iid, it)
    for p in POTIONS:
        mk_item(p, 25)
        mk_item("Skyy_Flask_V_" + p, 1)
    for f in ("Food_Bread", "Food_Beef_Raw", "Skyy_Cook_Food_Bread_G3", "Food_Kebab_Mushroom"):
        mk_item(f, 100)
        mk_item("Skyy_Food_Pouch_V_" + f, 1)
    for f in ("Skyy_Flask_Empty", "Skyy_Food_Pouch_Empty"):
        mk_item(f, 1)
    mk_item("Rock_Stone", 100)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    ICA = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    BS = JClass("org.bson.BsonString")
    System, CHM, UUID, Paths = JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.UUID"), JClass("java.nio.file.Paths")
    Boolean, JArr = JClass("java.lang.Boolean"), JClass("java.lang.reflect.Array")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    J = lambda n: JClass(PKG + n)
    Cfg, Defs, Data, Store, Eng, Ops, Core, Log = J("SupCfg"), J("SupDefs"), J("SupData"), J("SupStore"), J("SupEng"), J("SupOps"), J("SupCore"), J("SupLog")
    Log.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCooking")
    home = os.path.join(scratch, "java", "Skyy_SkyyCooking")
    os.makedirs(home, exist_ok=True)
    # ---- SupCfg
    s = str(Cfg.load(Paths.get(home)))
    t = open(os.path.join(home, "supplies.properties"), encoding="latin-1").read()
    K.check(t == str(Cfg.DEFAULTS) and bool(Cfg.ON) and bool(Cfg.LIFELONG) and int(Cfg.FLASK_CAP) == 64 and int(Cfg.POUCH_CAP) == 256 and not bool(Cfg.POUCH_RAW)
            and int(Cfg.FULL_NOTICE_MS) == 60000, "SJ1 a missing supplies.properties is written from its defaults (Flask 64, Pouch 256, raw off, 60 s): %s" % s)
    ed = t.replace("supplies.pouchCap=256", "supplies.pouchCap=3").replace("supplies.fullNoticeSeconds=60", "supplies.fullNoticeSeconds=99999")
    open(os.path.join(home, "supplies.properties"), "w", encoding="latin-1", newline="").write(ed)
    Cfg.load(Paths.get(home))
    K.check(int(Cfg.POUCH_CAP) == 3 and int(Cfg.FULL_NOTICE_MS) == 3600000 and open(os.path.join(home, "supplies.properties"), encoding="latin-1").read() == ed,
            "SJ1 a hand-edited file is read (clamped like the row: 3600 s max) and never rewritten")
    open(os.path.join(home, "supplies.properties"), "w", encoding="latin-1", newline="").write(t)
    Cfg.load(Paths.get(home))
    # ---- SupDefs
    K.check(list(Defs.FSRC) == POTIONS and len(Defs.PSRC) == N_POUCH and str(Defs.PSRC[0]) in RAW, "SJ2 the compiled order: Flask %s, Pouch starts with a raw snack" % list(Defs.FSRC)[:2])
    K.check(int(Defs.kindOf("Skyy_Flask_V_Potion_Health")) == 0 and int(Defs.kindOf("Skyy_Food_Pouch_Empty")) == 1 and int(Defs.kindOf("Skyy_Cook_Food_Bread_G3")) == -1
            and str(Defs.srcOf("Skyy_Flask_V_Potion_Health_Small")) == "Potion_Health_Small" and str(Defs.srcOf("Skyy_Flask_Empty")) == ""
            and Defs.srcOf("Skyy_Flask_X") is None and str(Defs.loadedId(1, None)) == "Skyy_Food_Pouch_Empty" and str(Defs.loadedId(0, "Potion_Health")) == "Skyy_Flask_V_Potion_Health",
            "SJ2 kindOf / srcOf / loadedId")
    K.check(int(Defs.fillKind("Potion_Health_Small")) == 0 and int(Defs.fillKind("Food_Bread")) == 1 and int(Defs.fillKind("Food_Beef_Raw")) == -1
            and int(Defs.fillKind("Rock_Stone")) == -1 and int(Defs.fillKind("Potion_Regen_Health")) == -1, "SJ2 fillKind: potions -> Flask, cooked food -> Pouch, raw OFF by default, others none")
    Cfg.POUCH_RAW = True
    K.check(int(Defs.fillKind("Food_Beef_Raw")) == 1, "SJ2 supplies.pouchRaw ON: raw snacks fill the Pouch")
    Cfg.POUCH_RAW = False
    # ---- the store
    sd = os.path.join(home, "supplies")
    Store.DIR = Paths.get(sd)
    K.eq(int(Store.readJournal()), 0, "SJ3 no journal yet = nothing to recover")

    def new_cs():
        return [SIC(JShort(9)), SIC(JShort(36)), SIC(JShort(9)), SIC(JShort(4)), SIC(JShort(4))]

    def put(c, sl, iid, n, meta=False):
        st = IS(iid, JInt(n))
        if meta:
            st = st.withMetadata(JString("SkyyRolls"), BS("x"))
        c.setItemStackForSlot(JShort(sl), st)

    def arr(cs):
        a = JArr.newInstance(ICA.class_, len(cs))
        for i, c in enumerate(cs):
            JArr.set(a, i, c)
        return a

    def where(cs, iid):
        r = []
        for tag, c in zip("hsbut", cs):
            for i in range(int(c.getCapacity())):
                it = c.getItemStack(JShort(i))
                if it is not None and not it.isEmpty() and str(it.getItemId()) == iid:
                    r.append((tag, i, int(it.getQuantity())))
        return r

    def jlines():
        p = os.path.join(sd, "journal.log")
        return [l.split("|") for l in open(p, encoding="utf8").read().splitlines() if l and not l.startswith("#")] if os.path.exists(p) else []
    cs = new_cs()
    A = arr(cs)
    put(cs[1], 0, "Potion_Health_Small", 3)
    put(cs[2], 1, "Potion_Health_Lesser", 2)
    put(cs[0], 2, "Potion_Health", 1)                 # the hotbar: never touched
    put(cs[1], 5, "Potion_Health_Greater", 1, meta=True)   # metadata: never taken
    put(cs[1], 6, "Food_Bread", 5)
    put(cs[1], 7, "Food_Beef_Raw", 4)
    put(cs[1], 8, "Rock_Stone", 10)
    d = Store.get("u1")
    K.check(not bool(d.bad) and int(d.tot(0)) == 0 and d.next(0) is None, "SJ3 a new profile store is empty")
    n = int(Ops.fill(None, A, d, 0, False))
    K.check(n == 5 and int(d.get(0, "Potion_Health_Small")) == 3 and int(d.get(0, "Potion_Health_Lesser")) == 2 and where(cs, "Potion_Health") == [("h", 2, 1)]
            and where(cs, "Potion_Health_Greater") == [("s", 5, 1)] and not where(cs, "Potion_Health_Small") and not where(cs, "Potion_Health_Lesser"),
            "SJ4 auto-fill takes the potions of storage + backpack (5), never the hotbar, never a stack with metadata")
    K.check(str(d.next(0)) == "Potion_Health_Lesser" and int(d.kinds(0)) == 2, "SJ4 the next drink = the WORST potion held (Lesser before Small)")
    jl = jlines()
    K.check(len([l for l in jl if l[0] == "C"]) == 2 and all("undo:" in l[8] for l in jl) and len(Store.OPEN) == 2 and d.paid.size() == 2,
            "SJ4 one journal C line per stack (with its undo), both entries open, both seqs in the paid ledger")
    ft = open(os.path.join(sd, "u1.properties"), encoding="utf8").read()
    K.check("flask.Potion_Health_Small=3" in ft and "flask.Potion_Health_Lesser=2" in ft and "paid=" in ft and not os.path.exists(os.path.join(sd, "u1.properties.tmp")),
            "SJ4 the store file holds the credit AND the seqs (one atomic write)")
    Cfg.POUCH_CAP = 3
    n = int(Ops.fill(None, A, d, 1, False))
    K.check(n == 3 and int(d.get(1, "Food_Bread")) == 3 and where(cs, "Food_Bread") == [("s", 6, 2)] and where(cs, "Food_Beef_Raw") == [("s", 7, 4)],
            "SJ5 the Pouch takes cooked food up to its cap (pouchCap 3 here: 3 of 5 bread; the rest stays), raw stays (pouchRaw off)")
    Cfg.POUCH_CAP = 256
    Cfg.POUCH_RAW = True
    n = int(Ops.fill(None, A, d, 1, False))
    K.check(n == 6 and int(d.get(1, "Food_Beef_Raw")) == 4 and str(d.next(1)) == "Food_Beef_Raw", "SJ5 pouchRaw ON: raw beef goes in and is eaten first (raw before Grade 0): %d" % n)
    Cfg.POUCH_RAW = False
    put(cs[1], 9, "Skyy_Cook_Food_Bread_G3", 2)
    d.skip.put("Skyy_Cook_Food_Bread_G3", Boolean.TRUE)
    K.check(int(Ops.fill(None, A, d, 1, False)) == 0 and int(Ops.fill(None, A, d, 1, True)) == 2, "SJ5 'Auto-fill this' OFF keeps it out of auto-fill; Put all in still takes it")
    # ---- take out
    r = str(Ops.take(A, d, 0, "Potion_Health_Small", 2))
    r_take = r
    K.check(r.startswith("+Took 2") and int(d.get(0, "Potion_Health_Small")) == 1 and sum(q for t_, i, q in where(cs, "Potion_Health_Small")) == 2
            and all(t_ == "s" for t_, i, q in where(cs, "Potion_Health_Small")), "SJ6 Take: storage first, counted: %s %s" % (r, where(cs, "Potion_Health_Small")))
    K.check([l for l in jlines() if l[0] == "T"] and str(Ops.take(A, d, 0, "Potion_Health_Large", 1)) == "-None left.", "SJ6 a T journal line; nothing to take = refused")
    full_cs = new_cs()
    for c in full_cs[:3]:
        for i in range(int(c.getCapacity())):
            put(c, i, "Rock_Stone", 100)
    fa = arr(full_cs)
    before = int(d.get(0, "Potion_Health_Lesser"))
    r = str(Ops.take(fa, d, 0, "Potion_Health_Lesser", 1))
    K.check(r.startswith("-No room") and int(d.get(0, "Potion_Health_Lesser")) == before and not where(full_cs, "Potion_Health_Lesser"),
            "SJ6 no room = nothing taken, the store unchanged: %s" % r)
    # ---- review HIGH 2: a Take keeps that id out of auto-fill (and claims) for 60 s; Put all in still takes it
    K.check(bool(Store.muted(d.key, "Potion_Health_Small")) and "stays out of Auto-fill" in r_take, "SJ6m after a Take the id is muted for auto-fill + the page says so: %s" % r_take)
    nb = sum(q for t_, i, q in where(cs, "Potion_Health_Small"))
    K.check(int(Ops.fill(None, A, d, 0, False)) == 0 and sum(q for t_, i, q in where(cs, "Potion_Health_Small")) == nb == 2,
            "SJ6m auto-fill does NOT pull the taken potions straight back (Skyy: 'if you click take out, the auto store doesn't put it back in automatically')")
    Store.MUTE.clear()
    dm = Store.get("um")
    csm = new_cs()
    put(csm[1], 0, "Potion_Health", 2)
    Store.mute(JString("um"), JString("Potion_Health"))
    K.check(int(Ops.fill(None, arr(csm), dm, 0, False)) == 0 and int(Ops.fill(None, arr(csm), dm, 0, True)) == 2, "SJ6m muted: auto-fill 0, Put all in 2")
    Store.MUTE.clear()
    # ---- review LOW 10: the version counter
    d.touch()
    dirty1 = bool(d.isDirty())
    Store.save(d)
    K.check(dirty1 and not bool(d.isDirty()), "SJ6v a change marks the store dirty (version counter), a save that holds it clears it")
    # ---- use: reserve / commit / return
    u = UUID.randomUUID()
    lv = int(d.get(0, "Potion_Health_Lesser"))
    K.check(bool(Core.reserve(u, d, 0, "Potion_Health_Lesser", None)) and int(d.get(0, "Potion_Health_Lesser")) == lv - 1 and d.res.size() == 1
            and "res." in open(os.path.join(sd, "u1.properties"), encoding="utf8").read(), "SJ7 reserve: 1 off the store + res.<seq> in the file BEFORE the drink")
    Core.commit(u, Store.RES.get(u))
    K.check(int(d.get(0, "Potion_Health_Lesser")) == lv - 1 and d.res.size() == 0 and Store.RES.get(u) is None and "res." not in open(os.path.join(sd, "u1.properties"), encoding="utf8").read(),
            "SJ7 commit (the marker): used exactly once, the reservation closed")
    Core.reserve(u, d, 0, "Potion_Health_Small", None)
    Core.giveBack(u, Store.RES.get(u), "test")
    K.check(int(d.get(0, "Potion_Health_Small")) == 1 and d.res.size() == 0, "SJ7 return (let go / a cancelled tap): nothing used")
    Core.reserve(u, d, 0, "Potion_Health_Small", None)
    K.check(int(d.get(0, "Potion_Health_Small")) == 0, "SJ7 the open use of a 'crash'")
    Store.DATA.clear()
    Store.RES.clear()
    d = Store.get("u1")
    K.check(int(d.get(0, "Potion_Health_Small")) == 1 and d.res.size() == 0 and [l for l in jlines() if l[0] == "B" and "start-up" in l[8]],
            "SJ7 at start-up an open use is RETURNED (journal B) - nothing lost")
    hist = os.path.join(sd, "history")
    K.check(os.path.isdir(hist) and len([f for f in os.listdir(hist) if f.startswith("u1-")]) >= 1, "SJ8 a History copy of the store file before the first write of the session")
    jl = jlines()
    kinds = set(l[0] for l in jl)
    K.check({"C", "T", "X", "R", "U", "B"} <= kinds and all(len(l) >= 9 for l in jl), "SJ8 journal line kinds %s, every line kind|seq|pkey|store|id|qty|n0|time|text" % sorted(kinds))
    # ---- settle (this run's entries, 30 s old -> D)
    Store.SETTLE_MS = JLong(0)
    nset = int(Store.settle(System.currentTimeMillis() + 1000))
    K.check(nset >= 4 and len([e for e in Store.OPEN.values() if bool(e[7])]) == 0 and [l for l in jlines() if l[0] == "D"], "SJ9 settle: every entry of this run settled (D): %d" % nset)
    Store.save(d)
    K.check("paid=" not in open(os.path.join(sd, "u1.properties"), encoding="utf8").read(), "SJ9 settled seqs leave the paid ledger at the next write")
    # ---- RECOVERY of a crashed run (journal entries without D / X)
    rd2 = os.path.join(scratch, "java", "rec", "supplies")
    os.makedirs(rd2, exist_ok=True)
    jl2 = ["C|c1|u2|0|Potion_Health_Small|3|5|1|fill (saved, paid)", "C|c2|u2|0|Potion_Health_Lesser|2|2|1|fill (NOT saved, paid)",
           "C|c3|u2|1|Food_Bread|4|4|1|fill (saved, not paid)", "T|t1|u2|0|Potion_Health|1|0|1|take (saved, paid)",
           "T|t2|u2|0|Potion_Health_Large|2|0|1|take (NOT saved, paid)", "C|c9|u2|0|Potion_Health|1|1|1|fill", "D|c9|u2|0|Potion_Health|1|1|1|settled",
           "Q|c1|u2|0|Potion_Health_Small|3|5|1|amend"]
    open(os.path.join(rd2, "journal.log"), "w", encoding="utf8").write("\n".join(jl2) + "\n")
    open(os.path.join(rd2, "u2.properties"), "w", encoding="utf8").write(
        "flask.Potion_Health_Small=3\nflask.Potion_Health_Lesser=2\nflask.Potion_Health=4\npaid=c1 c2 t1 t2\ngiven.flask=true\n")
    Store.DIR = Paths.get(rd2)
    Store.OPEN.clear()
    Store.DATA.clear()
    K.eq(int(Store.readJournal()), 5, "SJ10 start-up: 5 open entries of the crashed run (c9 settled)")
    cs2 = new_cs()
    put(cs2[1], 0, "Potion_Health_Small", 2)     # c1: 5 before, 3 removed, 2 left = saved
    put(cs2[1], 1, "Potion_Health_Lesser", 2)    # c2: 2 before, still 2 = the removal was NOT saved
    put(cs2[0], 0, "Potion_Health", 1)           # t1: 0 before + 1 = saved
    #                                              c3: bread 4 before, 0 now = saved, not in paid -> credit now; t2: Large 0 = not saved, paid -> back
    d2 = Store.get("u2")
    n = int(Ops.recover(arr(cs2), d2))
    K.check(n == 5 and int(d2.get(0, "Potion_Health_Small")) == 3 and int(d2.get(0, "Potion_Health_Lesser")) == 0 and int(d2.get(1, "Food_Bread")) == 4
            and int(d2.get(0, "Potion_Health")) == 4 and int(d2.get(0, "Potion_Health_Large")) == 2 and len(Store.OPEN) == 0,
            "SJ10 recovery: C saved+paid kept, C not saved -> credit undone, C saved not paid -> credited now, T saved kept, T not saved -> back to the store")
    rl = [l.split("|") for l in open(os.path.join(rd2, "journal.log"), encoding="utf8").read().splitlines()[len(jl2):]]
    K.check(sorted((l[0], l[1]) for l in rl) == [("D", "c1"), ("D", "c3"), ("D", "t1"), ("X", "c2"), ("X", "t2")], "SJ10 one D / X line per recovered entry: %s" % [(l[0], l[1]) for l in rl])
    Store.DATA.clear()
    Store.OPEN.clear()
    Store.readJournal()
    d3 = Store.get("u2")
    K.check(int(Ops.recover(arr(cs2), d3)) == 0 and int(d3.get(0, "Potion_Health_Small")) == 3 and int(d3.get(1, "Food_Bread")) == 4 and int(d3.get(0, "Potion_Health_Lesser")) == 0,
            "SJ10 a second start finds nothing open and the file holds the recovered counts (idempotent)")
    # recovery runs again after a crash between the store write and the D / X lines: the paid flags keep it exactly-once
    Store.DATA.clear()
    Store.OPEN.clear()
    open(os.path.join(rd2, "journal.log"), "w", encoding="utf8").write("C|c5|u3|1|Food_Bread|2|2|1|fill\n")
    open(os.path.join(rd2, "u3.properties"), "w", encoding="utf8").write("pouch.Food_Bread=2\npaid=c5\n")
    Store.readJournal()
    d4 = Store.get("u3")
    cs4 = new_cs()                                 # bread: 2 before, 0 now = saved, already paid -> kept as is
    Ops.settleOne(d4, "c5", Store.OPEN.get("c5"), True)
    Ops.settleOne(d4, "c5", Store.OPEN.get("c5"), True)
    K.check(int(d4.get(1, "Food_Bread")) == 2, "SJ10 a decision applied twice changes the store once")
    # ---- review HIGH 1: several open entries on ONE (profile, id) are a chain in time order
    rd5 = os.path.join(scratch, "java", "chain", "supplies")
    os.makedirs(rd5, exist_ok=True)
    jl5 = ["T|ta|u5|0|Potion_Health|5|0|100|take 5 (store 5 -> 0)", "C|ca|u5|0|Potion_Health|5|5|200|auto-fill re-absorbs them (store 0 -> 5)",
           "C|cb|u5|0|Potion_Health_Small|5|5|100|fill 5", "T|tb|u5|0|Potion_Health_Small|5|0|200|take them out again",
           "T|tc|u5|0|Potion_Health_Greater|5|0|100|take 5", "C|cc|u5|0|Potion_Health_Greater|5|5|200|fill them back"]
    open(os.path.join(rd5, "journal.log"), "w", encoding="utf8").write("\n".join(jl5) + "\n")
    open(os.path.join(rd5, "u5.properties"), "w", encoding="utf8").write(
        "flask.Potion_Health=5\nflask.Potion_Health_Small=3\nflask.Potion_Health_Greater=5\npaid=ta ca cb tb tc cc\n")
    Store.DIR = Paths.get(rd5)
    Store.OPEN.clear()
    Store.DATA.clear()
    Store.readJournal()
    cs5 = new_cs()
    put(cs5[1], 1, "Potion_Health_Small", 5)     # cb + tb both saved (count 5 = the state after both)
    put(cs5[1], 2, "Potion_Health_Greater", 5)   # tc saved, cc not (5 = the state after tc)
    #                                              Potion_Health 0 = the state after BOTH ta + ca (and before them: the newest state wins)
    d5 = Store.get("u5")
    n = int(Ops.recover(arr(cs5), d5))
    K.check(n == 6 and int(d5.get(0, "Potion_Health")) == 5 and int(d5.get(0, "Potion_Health_Small")) == 3 and int(d5.get(0, "Potion_Health_Greater")) == 0,
            "SJ10c chain recovery: take + re-fill = 5 (no dupe; per entry gave 10), fill + take = 3 (no loss; per entry gave 0), take saved + fill not = 0 with the 5 in the inventory: %s / %s / %s"
            % (d5.get(0, "Potion_Health"), d5.get(0, "Potion_Health_Small"), d5.get(0, "Potion_Health_Greater")))
    Store.DATA.clear()
    Store.OPEN.clear()
    Store.readJournal()
    d6 = Store.get("u5")
    K.check(int(Ops.recover(arr(cs5), d6)) == 0 and int(d6.get(0, "Potion_Health")) == 5 and int(d6.get(0, "Potion_Health_Small")) == 3,
            "SJ10c a second start: nothing open, the same counts (idempotent)")
    # ---- review LOW 8: a recovered entry whose D / X line cannot be written stays OPEN (and is decided the same way next time)
    rd7 = os.path.join(scratch, "java", "nojournal", "supplies")
    os.makedirs(rd7, exist_ok=True)
    open(os.path.join(rd7, "journal.log"), "w", encoding="utf8").write("C|c7|u7|1|Food_Bread|2|2|1|fill\n")
    open(os.path.join(rd7, "u7.properties"), "w", encoding="utf8").write("paid=c7\npouch.Food_Bread=2\n")
    Store.DIR = Paths.get(rd7)
    Store.OPEN.clear()
    Store.DATA.clear()
    Store.readJournal()
    os.remove(os.path.join(rd7, "journal.log"))
    os.makedirs(os.path.join(rd7, "journal.log"))   # the journal cannot be appended now
    d7 = Store.get("u7")
    cs7 = new_cs()
    n1 = int(Ops.recover(arr(cs7), d7))
    keep = Store.OPEN.containsKey("c7")
    os.rmdir(os.path.join(rd7, "journal.log"))
    n2 = int(Ops.recover(arr(cs7), d7))
    K.check(n1 == 0 and keep and n2 == 1 and int(d7.get(1, "Food_Bread")) == 2 and not Store.OPEN.containsKey("c7"),
            "SJ10j a failed D / X append keeps the entry OPEN; the next try settles it once (n %d -> %d, bread %s)" % (n1, n2, d7.get(1, "Food_Bread")))
    bad = Data("bad")
    bad.bad = True
    K.check(not bool(Store.saveHard(bad, "a test")), "SJ10j saveHard answers false (and logs loudly) when the store cannot be written")
    # ---- the bridge (memory only)
    Store.DIR = Paths.get(sd)
    Store.DATA.clear()
    d = Store.get("u1")
    d.ready = True
    pu = UUID.randomUUID()
    bridge.put("profile:fn:key", None) if False else None
    Store.DATA.put(str(pu), d)
    d.key = str(pu)
    Ops.pkey(pu)
    Claims, Counts = J("SupClaimsFn")(), J("SupCountsFn")()
    Arr = lambda *a: JClass("java.lang.Object")[:](list(a))
    K.check(bool(Claims.apply(Arr(pu, "Potion_Health_Small"))) and bool(Claims.apply(Arr(pu, "Food_Bread"))), "SJ11 supply:fn:claims TRUE for a potion / cooked food when Auto-fill is ON")
    K.check(not bool(Claims.apply(Arr(pu, "Rock_Stone"))) and not bool(Claims.apply(Arr(pu, "Food_Beef_Raw"))) and not bool(Claims.apply(Arr(UUID.randomUUID(), "Potion_Health"))),
            "SJ11 claims FALSE for a non-supply id, raw food (pouchRaw off), an unknown player")
    d.skip.put("Food_Bread", Boolean.TRUE)
    c1 = bool(Claims.apply(Arr(pu, "Food_Bread")))
    d.skip.remove("Food_Bread")
    d.fAuto = False
    c2 = bool(Claims.apply(Arr(pu, "Potion_Health")))
    d.fAuto = True
    Cfg.FLASK_CAP = int(d.tot(0))
    c3 = bool(Claims.apply(Arr(pu, "Potion_Health")))
    Cfg.FLASK_CAP = 64
    bridge.put("profile:busy:" + str(pu), Boolean.TRUE)
    c4 = bool(Claims.apply(Arr(pu, "Potion_Health")))
    bridge.remove("profile:busy:" + str(pu))
    bridge.put("profile:epoch:" + str(pu), JLong(7))
    c5 = bool(Claims.apply(Arr(pu, "Potion_Health")))
    bridge.remove("profile:epoch:" + str(pu))
    Cfg.ON = False
    c6 = bool(Claims.apply(Arr(pu, "Potion_Health")))
    Cfg.ON = True
    Store.mute(d.key, JString("Potion_Health"))
    c7 = bool(Claims.apply(Arr(pu, "Potion_Health")))
    Store.MUTE.clear()
    K.check(not c7, "SJ11 claims FALSE for an id the player just took out (review HIGH 2: the Void keeps out of it too)")
    K.check(not (c1 or c2 or c3 or c4 or c5 or c6) and bool(Claims.apply(Arr(pu, "Potion_Health"))),
            "SJ11 claims FALSE when skipped / Auto-fill OFF / full / profile busy / another profile (epoch changed) / supplies off")
    m = Counts.apply(pu)
    K.check(m is not None and int(m.get("Potion_Health_Lesser")) == int(d.get(0, "Potion_Health_Lesser")) and Counts.apply(UUID.randomUUID()) is None,
            "SJ11 supply:fn:counts = HashMap itemId -> Long of the current profile (null = unknown)")
    # ---- the held item sync
    hs = new_cs()
    put(hs[0], 0, "Skyy_Flask_Empty", 1)
    put(hs[1], 3, "Skyy_Food_Pouch_Empty", 1)
    ha = arr(hs)
    K.eq(int(Eng.sync(ha, d)), 2, "SJ12 sync: both copies rewritten")
    f0, p0 = hs[0].getItemStack(JShort(0)), hs[1].getItemStack(JShort(3))
    K.check(str(f0.getItemId()) == "Skyy_Flask_V_" + str(d.next(0)) and str(p0.getItemId()) == "Skyy_Food_Pouch_V_" + str(d.next(1)) and f0.getMetadata() is not None
            and "ItemDisplay" in str(f0.getMetadata().toJson()), "SJ12 the held id = the loaded id of the next item + ItemDisplay metadata: %s" % f0.getItemId())
    K.eq(int(Eng.sync(ha, d)), 0, "SJ12 a second sync changes nothing (only when id or text changed)")
    K.check(str(Eng.nameText(0, d)) == "Potion Flask (%d)" % int(d.tot(0)) and str(Eng.descText(0, d)).startswith("Next: Lesser") or str(Eng.descText(0, d)).startswith("Next: "),
            "SJ12 the name 'Potion Flask (n)' + 'Next: ...': %s / %s" % (Eng.nameText(0, d), Eng.descText(0, d)))
    e = Data("empty")
    Eng.sync(ha, e)
    K.check(str(hs[0].getItemStack(JShort(0)).getItemId()) == "Skyy_Flask_Empty" and str(hs[1].getItemStack(JShort(3)).getItemId()) == "Skyy_Food_Pouch_Empty",
            "SJ12 store 0 -> the held item becomes the Empty id (FP0 finding 1)")
    Cfg.ON = False
    Eng.sync(ha, d)
    K.check(str(hs[0].getItemStack(JShort(0)).getItemId()) == "Skyy_Flask_Empty" and "Switched off" in str(Eng.descText(0, d)), "SJ12 supplies.on OFF = the items show Empty")
    Cfg.ON = True
    K.check(int(Eng.ours(ha, 0)) == 1 and int(Eng.countId(A, "Potion_Health")) == 1, "SJ13 counting helpers (hotbar + storage + backpack)")
    K.check(bool(Ops.saved("C", 2, 5, 3)) and not bool(Ops.saved("C", 3, 5, 3)) and bool(Ops.saved("T", 3, 1, 2)) and not bool(Ops.saved("T", 2, 1, 2)),
            "SJ13 the recovery count rule: C saved when count <= n0 - qty, T saved when count >= n0 + qty")
    K.save()


def run_life(pfx, item, item_prefix):
    def fn(out, jar, scratch, _home):
        import skyyonce_harness as OH
        K = HK.Child(out)
        OH.life_phase(K, jar, PKG, pfx, item, ("SupCfg", "LIFELONG"), os.path.join(scratch, "life" + pfx), "SkyyCooking", item_prefix=item_prefix)
        K.save()
    return fn


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Snd, CP, Sup, Store = J("CookCfg"), J("CookSnd"), J("CfgPub"), J("SupCfg"), J("SupStore")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    c0 = open(os.path.join(home, "cooking.properties"), "rb").read()
    had = os.path.exists(os.path.join(home, "supplies.properties"))
    snaps, migs = [], []
    import time
    for start in (1, 2):
        Cfg.FILE = Paths.get(os.path.join(home, "cooking.properties"))
        migs.append([str(J(m).migrate()) for m in ("CookMig", "CookXpMig", "CookTblMig", "CookIngMig")])
        Cfg.load()
        Snd.load(Paths.get(home))
        s = str(Sup.load(Paths.get(home)))
        Store.DIR = Paths.get(home).resolve("supplies")
        Store.readJournal()
        CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCooking"))
        K.check(bool(Sup.ON) and int(Sup.FLASK_CAP) >= 1, "DS%d: supplies config read: %s" % (start, s))
        CP.flush()
        time.sleep(0.6)
        CP.shutdown()
        snaps.append(HK.tree_hash(home))
        time.sleep(1.1)
    K.check(migs == [["", "", "", ""], ["", "", "", ""]], "DS: no one-time Cooking update runs on the live cooking.properties: %s" % migs)
    K.check(open(os.path.join(home, "cooking.properties"), "rb").read() == c0, "DS: the live cooking.properties is byte-identical after two starts")
    K.check(os.path.exists(os.path.join(home, "supplies.properties")), "DS: supplies.properties exists (created from its defaults: %s)" % ("was there" if had else "new"))
    K.check(snaps[0] == snaps[1], "DS: the second start changes nothing")
    K.save()




# ================================================================================================= N: the 12 new dishes (own rules)
DISH_DIR = "Server/Item/Items/SkyyCook/Dishes/"
GRADED_DIR = "Server/Item/Items/SkyyCook/"
FX_RE = re.compile(r"^Skyy_Cook_Fx_(Health|Mana|Stamina|Strength)_(\d+)$")
L0 = {"Health": 0.01, "Mana": 0.01, "Stamina": 0.1, "Strength": 0.1}


def run_dishes(out, jar, scratch, _home):
    K = HK.Child(out)
    AZ = zipfile.ZipFile(SJ.assets_zip())
    an = AZ.namelist()
    ans = set(an)

    def ids(prefix):
        return dict((os.path.basename(n)[:-5], n) for n in an if n.startswith(prefix) and n.endswith(".json"))
    VE, VI, VR, VIT, VRT = ids("Server/Entity/Effects/"), ids("Server/Item/Interactions/"), ids("Server/Item/RootInteractions/"), ids("Server/Item/Items/"), ids("Server/Item/ResourceTypes/")
    VSND = ids("Server/Audio/SoundEvents/")
    common = set(n for n in an if n.startswith("Common/"))
    vrd = lambda n: json.loads(AZ.read(n).decode("utf-8-sig"))
    Z = zipfile.ZipFile(jar)
    zn = Z.namelist()
    zns = set(zn)
    rdz = lambda n: json.loads(Z.read(n).decode("utf-8-sig"))
    JE = dict((os.path.basename(n)[:-5], n) for n in zn if n.startswith("Server/Entity/Effects/") and n.endswith(".json"))
    JI = dict((os.path.basename(n)[:-5], n) for n in zn if n.startswith("Server/Item/Interactions/") and n.endswith(".json"))
    JIT = dict((os.path.basename(n)[:-5], n) for n in zn if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    bench = vrd(VIT["Bench_Cooking"])["BlockType"]["Bench"]
    cats = set(c["Id"] for c in bench["Categories"])
    lang = Z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    LK = dict(l.split("=", 1) for l in lang.splitlines() if "=" in l and not l.startswith("#"))
    # ---------------- N0 every class but the three data-table ones = 0.1.11's bytes with only the version text changed
    Z0 = zipfile.ZipFile(OLD_JAR)
    cls = [n for n in zn if n.endswith(".class")]
    data_cls = ["com/skyy/cooking/%s.class" % c for c in ("CfgRows", "CookCfg", "SupDefs")]
    vb = [n for n in cls if n not in data_cls and Z0.read(n).replace(b"0.1.11", b"0.1.12") != Z.read(n)]
    K.check(len(cls) == len([n for n in Z0.namelist() if n.endswith(".class")]) and not vb,
            "N0 %d classes: all but CfgRows / CookCfg / SupDefs (the dish, XP and pouch tables) are 0.1.11's bytes with only the version text changed: %s" % (len(cls), vb[:3]))
    tank = vrd(VIT["Deco_Tankard"])
    mug = vrd(VIT["Deco_Mug"])
    # ---------------- N1 ids + recipes
    bad = []
    for i, (nm, t, fams, look) in sorted(NEW.items()):
        if i in VIT or not i.startswith("Food_Skyy_") or (DISH_DIR + i + ".json") not in zns:
            bad.append(i + " id")
            continue
        o = rdz(DISH_DIR + i + ".json")
        r = o.get("Recipe") or {}
        br = r.get("BenchRequirement") or []
        if len(br) != 1 or br[0].get("Id") != "Cookingbench" or br[0].get("Type") != "Crafting" or len(br[0].get("Categories", [])) != 1 or br[0]["Categories"][0] not in cats:
            bad.append(i + " bench %s" % br)
        want_ret = []
        got_fams = []
        for inp in r.get("Input", []):
            q = int(inp.get("Quantity", 1))
            if inp.get("ResourceTypeId"):
                if inp["ResourceTypeId"] not in VRT:
                    bad.append(i + " resource " + inp["ResourceTypeId"])
                if inp["ResourceTypeId"] == "Milk_Bucket":
                    want_ret.append({"ItemId": "Container_Bucket", "Quantity": q})
            else:
                x = inp["ItemId"]
                if x.startswith("*"):
                    m = re.match(r"^\*(\w+?)_State_(\w+)$", x)
                    if not m or m.group(1) not in VIT or m.group(2) not in (vrd(VIT[m.group(1)]).get("State") or {}):
                        bad.append(i + " state input " + x)
                    if x == "*Deco_Tankard_State_Filled_Water":
                        want_ret.append({"ItemId": "Deco_Tankard", "Quantity": q})
                elif x not in VIT or x.startswith("Skyy_") or x.startswith("Food_Skyy_"):
                    bad.append(i + " input " + x + " (not a vanilla item)")
            f = fam_of(inp)
            if f and f not in got_fams:
                got_fams.append(f)
        if sorted(got_fams, key=FAMS.index) != fams:
            bad.append(i + " families %s != %s" % (got_fams, fams))
        outs = r.get("Output") or []
        if not outs or outs[0]["ItemId"] != i or outs[0].get("Quantity", 1) != (2 if i == "Food_Skyy_Sliced_Bread" else 1) or outs[1:] != want_ret:
            bad.append(i + " outputs %s" % outs)
        if o.get("Parent") != "Template_Food" or o["Interactions"]["Secondary"] != "Root_Secondary_Consume_Food_T%d" % t or "Root_Secondary_Consume_Food_T%d" % t not in VR:
            bad.append(i + " parent / eat root")
        if o.get("Quality") != {1: "Common", 2: "Uncommon", 3: "Rare"}[t]:
            bad.append(i + " quality " + str(o.get("Quality")))
    K.check(not bad, "N1 the 12 new dishes: Food_Skyy_ ids (not vanilla), Cooking Bench recipes of vanilla inputs only, containers back, families, eat root, Quality by tier: %s" % bad[:6])
    # ---------------- N2 looks
    bad = []
    for i, (nm, t, fams, look) in sorted(NEW.items()):
        o = rdz(DISH_DIR + i + ".json")
        bt = o.get("BlockType") or {}
        paths = [o.get("Icon"), bt.get("CustomModel"), bt.get("CustomModelAnimation")] + [x.get("Texture") for x in bt.get("CustomModelTexture", [])]
        pa = o.get("PlayerAnimationsId")
        if isinstance(pa, dict):
            for a in pa.get("Animations", {}).values():
                paths += [a.get("FirstPerson"), a.get("ThirdPerson")]
        for p_ in [x for x in paths if x]:
            if "Common/" + p_ not in common or "Common/" + p_ in zns:
                bad.append(i + " " + p_)
        if look in ("tankard", "mug"):
            st = (tank if look == "tankard" else mug)["State"]["Filled_Water"]
            src = tank if look == "tankard" else mug
            if o["Icon"] != st["Icon"] or bt.get("CustomModel") != st["BlockType"]["CustomModel"] or bt.get("CustomModelTexture") != st["BlockType"]["CustomModelTexture"] \
                    or o.get("PlayerAnimationsId") != src["PlayerAnimationsId"] or o.get("IconProperties") != st["IconProperties"]:
                bad.append(i + " drink look")
            iv = o["InteractionVars"]
            cc = iv["Consume_Charge"]["Interactions"]
            if len(cc) != 1 or cc[0].get("Effects") != {"ItemAnimationId": "Consume"}:
                bad.append(i + " drink charge %s" % cc)
            for var, par in (("ConsumeSFX", "Consume_SFX"), ("ConsumedSFX", "Consumed_SFX")):
                e = iv[var]["Interactions"][0]
                if e["Parent"] != par or par not in VI or e["Effects"]["LocalSoundEventId"] not in VSND:
                    bad.append(i + " " + var)
            if "Drink" not in json.dumps(o["PlayerAnimationsId"]):
                bad.append(i + " no drink animation")
        elif look == "cheese":
            ch = vrd(VIT["Food_Cheese"])
            if o["Icon"] != ch["Icon"] or bt != ch["BlockType"]:
                bad.append(i + " cheese look")
    no_common = [n for n in zn if n.startswith("Common/") and not n.startswith("Common/UI/Custom/SkyyKit/")]
    K.check(not bad and not no_common, "N2 every look file is vanilla (in Assets.zip, never in the jar: %d Common files besides the kit), drinks = the filled Tankard / Mug look + drink animation + 'Consume' charge + real drink sounds, Butter = the Cheese look: %s" % (len(no_common), bad[:6]))
    # ---------------- N3 references + no missing vanilla effect
    ALLI = dict(VI); ALLI.update(VR); ALLI.update(JI)
    ALLE = dict(VE); ALLE.update(JE)
    miss = set()

    def refs(o, where):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("PlayerAnimationsId", "TranslationProperties", "BlockType", "Recipe"):
                    continue
                if k in ("Parent", "Next", "Failed") and isinstance(v, str) and v not in ALLI and v not in VIT:
                    miss.add(where + " " + v)
                elif k in ("Secondary", "Primary") and isinstance(v, str) and v not in ALLI:
                    miss.add(where + " " + v)
                elif k == "Interactions" and isinstance(v, list):
                    miss.update(where + " " + x for x in v if isinstance(x, str) and x not in ALLI)
                elif k in ("EffectId", "EntityEffectId") and isinstance(v, str) and v not in ALLE:
                    miss.add(where + " " + v)
                elif k == "EntityEffectIds":
                    miss.update(where + " " + x for x in v if x not in ALLE)
                if isinstance(v, (dict, list)):
                    refs(v, where)
        elif isinstance(o, list):
            for x in o:
                refs(x, where)
    items = []
    for i in NEW:
        items.append((i, DISH_DIR + i + ".json"))
        for g in range(1, 13):
            items.append((i, GRADED_DIR + "Skyy_Cook_%s_G%d.json" % (i, g)))
    gone = [n for _, n in items if n not in zns]
    for _, n in items:
        if n in zns:
            o = rdz(n)
            refs(o, os.path.basename(n))
            for c in [x for x in o["InteractionVars"]["Effect"]["Interactions"] if isinstance(x, str)]:
                refs(rdz(JI[c]), c) if c in JI else miss.add(n + " " + c)
    heal23 = [n for n in zn if n.endswith(".json") and re.search(r'"Food_Instant_Heal_(T2|T3|Bread)"', Z.read(n).decode("utf-8", "replace"))]
    K.check(not gone and not miss and not heal23, "N3 the %d new food items exist, every interaction / effect / item they (and their checks) name exists in the jar or Assets.zip, no file names Food_Instant_Heal_T2 / T3 / Bread: missing %s, refs %s, heal %s"
            % (len(items), gone[:3], sorted(miss)[:5], heal23[:3]))
    # ---------------- N4 numbers
    bad = []
    nchk = 0
    for i, n in items:
        nm, t, fams, look = NEW[i]
        m = re.search(r"_G(\d+)\.json$", n)
        g = int(m.group(1)) if m else 0
        o = rdz(n)
        w = {}
        for f in fams:
            for b, x in PART[f].items():
                w[b] = w.get(b, 0.0) + SHARE[len(fams)] * x
        ch = o["InteractionVars"]["Effect"]["Interactions"]
        inst = [x for x in ch if isinstance(x, dict)]
        want_i = dict((b, round(min(INST[b][t - 1] * w[b] * S(g), ICAP[b]), 2)) for b in ("Health", "Mana", "Stamina") if b in w)
        got_i = inst[0]["EffectId"]["StatModifiers"] if inst else {}
        if set(got_i) != set(want_i) or any(abs(got_i[b] - want_i[b]) > 0.011 for b in want_i):
            bad.append("%s G%d instant %s != %s" % (i, g, got_i, want_i))
        if inst and (inst[0]["EffectId"].get("ValueType") != "Percent" or inst[0]["EffectId"].get("Duration", 1) > 0.5):
            bad.append("%s G%d instant shape" % (i, g))
        bars = set()
        for b in ("Health", "Mana", "Stamina", "Strength"):
            var = o["InteractionVars"].get("Skyy_Cook_Apply_" + b)
            if b not in w:
                if var is not None:
                    bad.append("%s G%d applies %s" % (i, g, b))
                continue
            bars.add(b)
            ap = var["Interactions"][0]
            mm = FX_RE.match(ap["EffectId"])
            want = min(OVER[b][t - 1] * w[b] * S(g), OCAP[b])
            v = L0[b] * 1.05 ** int(mm.group(2))
            if abs(math.log(v / want)) > STEP / 2 + 1e-9:
                bad.append("%s G%d %s %.4f vs %.4f" % (i, g, b, v, want))
            dur = min(360.0 * 2 ** (g / 5.0), 2400.0)
            if b == "Strength":
                dur = min(dur, 600.0)
            if abs(ap["Duration"] - dur) > 0.02:
                bad.append("%s G%d %s duration %s vs %s" % (i, g, b, ap["Duration"], dur))
            fx = rdz(JE[ap["EffectId"]])
            if b == "Health":
                ok = fx["ValueType"] == "Percent" and abs(fx["StatModifiers"]["Health"] - v) < 1e-3 and fx["DamageCalculatorCooldown"] == 2 and fx["RawStatModifiers"]["Health"][0]["Target"] == "Max"
            elif b == "Mana":
                ok = fx["ValueType"] == "Percent" and abs(fx["StatModifiers"]["Mana"] - v) < 1e-3 and fx["DamageCalculatorCooldown"] == 2
            elif b == "Stamina":
                ok = abs(fx["RawStatModifiers"]["Stamina"][0]["Amount"] - (1 + v / 100.0)) < 1e-3 and fx["RawStatModifiers"]["Stamina"][0]["CalculationType"] == "Multiplicative"
            else:
                ok = all(abs(fx["OutgoingDamage"][c][0]["Amount"] - v / 100.0) < 1e-3 for c in ("Physical", "Projectile", "Elemental"))
            if not ok:
                bad.append("%s G%d %s effect shape" % (i, g, b))
            if ("Skyy_Cook_Chk_%s_%s" % (b, mm.group(2))) not in ch:
                bad.append("%s G%d %s check missing" % (i, g, b))
            nchk += 1
    K.check(not bad, "N4 numbers of every new food item (%d over-time parts): instant = base x family weight x (1 + 0.32 g), over time within half a ladder step, durations, effect shapes: %s" % (nchk, bad[:6]))
    # ---------------- N5 graded copies + lang
    bad = []
    for i, n in items:
        nm, t, fams, look = NEW[i]
        m = re.search(r"Skyy_Cook_(Food_Skyy_\w+)_G(\d+)\.json$", n)
        iid = os.path.basename(n)[:-5]
        o = rdz(n)
        for pre in ("items.", "server.items."):
            if pre + iid + ".name" not in LK or pre + iid + ".description" not in LK:
                bad.append(iid + " lang")
        if m:
            g = int(m.group(2))
            gq = "Uncommon" if g <= 2 else ("Rare" if g <= 5 else ("Epic" if g <= 8 else "Legendary"))
            if "Recipe" in o or QORDER.index(o["Quality"]) < QORDER.index(gq) or LK.get("server.items.%s.name" % iid) != "%s (Grade %d)" % (nm, g):
                bad.append(iid + " graded")
        elif LK.get("server.items.%s.name" % iid) != nm:
            bad.append(iid + " name")
        desc = LK.get("server.items.%s.description" % iid, "")
        names = {"Health": "Health Regen", "Mana": "Mana Regen", "Stamina": "Stamina Boost", "Strength": "Strength +"}
        w = set(b for f in fams for b in PART[f])
        for b, word in names.items():
            if (word in desc) != (b in w):
                bad.append(iid + " tooltip " + b)
    K.check(not bad, "N5 graded copies (no Recipe, Quality >= the Grade's, '<name> (Grade g)') and lang (name + description, both prefixes; the tooltip names exactly the dish's bars): %s" % bad[:6])
    # ---------------- N6 the Food Pouch takes them
    po = set(os.path.basename(n)[:-5] for n in zn if n.startswith(SUP + "Skyy_Food_Pouch_V_"))
    missing = [os.path.basename(n)[:-5] for _, n in items if "Skyy_Food_Pouch_V_" + os.path.basename(n)[:-5] not in po]
    K.check(not missing, "N6 the Food Pouch has a loaded id for each of the %d new food items: missing %s" % (len(items), missing[:4]))
    K.save()


# ================================================================================================= J: CookCfg with the new dishes
def run_cookcfg(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, Hk = J("CookCfg"), J("CookHooks")
    Paths = JClass("java.nio.file.Paths")
    d = os.path.join(scratch, "cookcfg", "Skyy_SkyyCooking")
    os.makedirs(d, exist_ok=True)
    f = os.path.join(d, "cooking.properties")
    Cfg.FILE = Paths.get(f)
    s = str(Cfg.load())
    t = open(f, encoding="latin-1").read()
    K.check(list(Cfg.DISHES) == VAN_DISHES + OWN_ORDER and int(Cfg.N_VAN) == 15, "J1 CookCfg.DISHES = the 15 vanilla dishes, then the 23 own dishes sorted by tier then name: %s" % [str(x) for x in Cfg.DISHES][15:20])
    K.check(("graded=" + ",".join(VAN_DISHES + OWN_ORDER)) in t and "gradedOwn=true" in t, "J1 a missing file is written with every dish on graded= (%s)" % s[:80])
    K.check(all(int(Cfg.tierOf(i)) == NEW[i][1] for i in NEW) and all(int(Cfg.tierOf(i)) == OLD_OWN[i][1] for i in OLD_OWN), "J2 tierOf: every own dish its tier")
    xl = dict((l[3:].split("=")[0], int(l.split("=")[1])) for l in t.splitlines() if l.startswith("xp.") and "=" in l)
    K.check(all(i in xl and xl[i] > 0 and int(Cfg.xpFor(i)) == xl[i] for i in NEW), "J3 xpFor: every new dish has a built-in XP value = its default xp line: %s" % dict((i[10:], xl.get(i)) for i in sorted(NEW)))
    K.check(xl["Food_Skyy_Butter"] < xl["Food_Skyy_Cottage_Pie"] and xl["Food_Skyy_Berry_Cordial"] < xl["Food_Skyy_Spiced_Cider"],
            "J3 the difficulty rule: one-step Butter / Cordial pay less than a pie / a two-step cider")
    live = t.replace("graded=" + ",".join(VAN_DISHES + OWN_ORDER), "graded=" + ",".join(VAN_DISHES)).replace("gradedOwn=true\n", "")
    for i in NEW:
        live = re.sub(r"(?m)^xp\.%s=\d+\n" % i, "", live)
    open(f, "w", encoding="latin-1", newline="").write(live)
    Cfg.load()
    K.check(all(int(Cfg.tierOf(i)) == NEW[i][1] for i in NEW) and all(int(Cfg.xpFor(i)) == xl[i] for i in NEW) and open(f, encoding="latin-1").read() == live,
            "J4 a live-shape file (graded= the 15 vanilla dishes, no gradedOwn, no xp lines for the new dishes): the new dishes are graded and pay their built-in XP; the file is never rewritten")
    K.check(Hk.checkGraded("graded", ",".join(VAN_DISHES + OWN_ORDER)) is None, "J5 CookHooks.checkGraded accepts every dish incl. the new ones")
    K.save()


# ---- C: non-class entries: only the new dishes' files, new ladder steps, changed ladder checks, manifest + lang; nothing gone
_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    orig_eq = HK.Child.eq

    def eq(self, got, want, what):
        if what != "C: non-class entries changed":
            return orig_eq(self, got, want, what)
        za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
        na = set(za.namelist())
        new = [n for n in got if n not in na]
        chg = [n for n in got if n in na]
        gone = [n for n in na if n not in zb.namelist()]
        newid = lambda n: any(("/%s.json" % i) in n or ("_%s_G" % i) in n or ("Skyy_Food_Pouch_V_%s.json" % i) in n or ("Skyy_Food_Pouch_V_Skyy_Cook_%s_G" % i) in n for i in NEW)
        ladder = lambda n: re.search(r"/Skyy_Cook_(Fx|Chk)_(Health|Mana|Stamina|Strength)_\d+\.json$", n) is not None
        bad_new = [n for n in new if not (newid(n) or ladder(n))]
        bad_chg = [n for n in chg if n not in ("Server/Languages/en-US/server.lang", "manifest.json") and not re.search(r"/Skyy_Cook_Chk_(Health|Mana)_\d+\.json$", n)]
        return self.check(not bad_new and not bad_chg and not gone and "Server/Languages/en-US/server.lang" in chg,
                          "C: non-class entries: %d added (new dishes / pouch ids / ladder steps only; other: %s), %d changed (lang, manifest, Health / Mana ladder checks only; other: %s), gone %s"
                          % (len(new), bad_new[:3], len(chg), bad_chg[:3], gone[:3]))
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = orig_eq


HK.run_compare = _compare

if __name__ == "__main__":
    HK.run(name="SkyyCooking", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("dishes", run_dishes), ("cookcfg", run_cookcfg), ("assets", run_assets), ("java", run_java),
                   ("lifeflask", run_life("FlaskOnce", "Skyy_Flask_Empty", "Skyy_Flask_")),
                   ("lifepouch", run_life("PouchOnce", "Skyy_Food_Pouch_Empty", "Skyy_Food_Pouch_")), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyCooking"))
