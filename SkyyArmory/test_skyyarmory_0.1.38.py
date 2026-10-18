"""Harness for SkyyArmory 0.1.38 (BETA BUG 20: "Soul Cage recipes will not take Soul Orbs"; tools/armory_0_1_38_patch.py). Build first:
    python tools/armory_0_1_38_patch.py && python SkyyArmory/build_skyyarmory_0.1.38.py      (tier_tags: HEAD's TT_VERSION 2, see the patch)

    python SkyyArmory/test_skyyarmory_0.1.38.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.37 -> 0.1.38: only the version-text members; non-class entries = manifest.json, server.lang, the 16 Soul item files and the 31
               new files (16 resource types + 15 hidden ladder recipes)
  S   static   the jar JSON vs 0.1.37: each Soul item = 0.1.37 + its own ResourceTypes entry, every cage recipe = 0.1.37 with ONLY its first input
               moved to the previous item's resource type (all 15 tiers incl. the 0.1.33 branch cages); the resource type files (icon in the
               jar), names ("Any <item>"); the hidden ladder twins = the 0.1.37 recipes at bench SkyyArmory_SoulLadder; across Assets.zip, every
               SET jar and the installed Mods (read only): no other item carries our types, no other recipe takes them, no block is the twin
               bench, nothing else names it; SkyyGear 0.3.28's Anvil Upgrade ladder (GearUp.cost0 / fromRecipe / fromRecipeAlt, ported) and
               its salvage reader (GearSalvage.recipeIn) give exactly the 0.1.37 costs on every one of the 15 steps (and NONE without the twins)
  E   engine   the real engine on our decoded assets: every new / changed file through its store codec (ResourceType, Item, CraftingRecipe):
               no exception, no validation failure, no unknown key; then, per cage tier, real ItemStacks with SkyyGear documents (Common /
               Uncommon / Rare / Legendary / another level / unidentified / an empty document / plain) in a real CombinedItemContainer
               (backpack + storage + hotbar): the 0.1.37 recipe counts ONLY the plain orb (the bug reproduced), the 0.1.38 recipe counts every
               variant and no other Soul item; the /craft sequence of SkyySacks 0.8.23 (CraftPage.limit, CraftingManager.getInputMaterials,
               canRemoveMaterials, removeMaterials, CraftPage.snapshot / removedItems / reserve) takes exactly one previous item + the bars +
               the essence per craft, gives nothing back, and stops when the last variant is gone (no dupe, no negative)
  AA  audit    the engine-access audit
Not executed here (UNVERIFIED until the game): the client's draw of a resource-type cost (the Weapon Bench shows the type's icon + "Any Soul
Orb"), WHICH variant a craft takes when several are carried (the engine's slot order - noted), the server's own pack load of the new folders.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.38", "0.1.37"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SACKS_JAR = os.path.join(ROOT, "SkyySacks", "SkyySacks-0.8.23.jar")
GEAR_JAR = os.path.join(ROOT, "SkyyGear", "SkyyGear-0.3.28.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "arm38", "harness")))
PKG = "com.skyy.armory."
ASSETS = os.path.join(os.path.dirname(os.path.dirname(B.INSTALLED_SERVER_JAR)), "Assets.zip")
LANG = "Server/Languages/en-US/server.lang"
METALS = ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium") + tuple(w + "_SkyWynn" for w in
                                                                                              ("Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"))
SOUL = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_" + m for m in METALS]
RT = dict((i, "SkyyArmory_Any_" + i[len("Weapon_Wand_"):]) for i in SOUL)
P_ITEM = "Server/Item/Items/Weapon/Wand/%s.json"
P_RT = "Server/Item/ResourceTypes/SkyyArmory/%s.json"
P_LAD = "Server/Item/Recipes/SkyyArmory/SoulLadder/%s.json"
LAD = dict((i, "SkyyArmory_SoulLadder_" + i[len("Weapon_Wand_"):]) for i in SOUL[1:])
BENCH = "SkyyArmory_SoulLadder"
EXPECT = {"SkyyArmoryPlugin": ["~m setup", "~m start"], "ArmoryCheck": ["~m packCheck", "~m packOf"],
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],
          "CfgRows2": ["~<clinit>"], "ArmoryHooks": ["~<clinit>"]}          # the version text; ArmoryHooks = the fixed.soul row words
ADDED = []
NONCLASS = sorted(["manifest.json", LANG] + [P_ITEM % i for i in SOUL] + [P_RT % RT[i] for i in SOUL] + [P_LAD % LAD[i] for i in SOUL[1:]])

_orig_compare = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    E = HK.Child.eq

    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = NONCLASS
        return E(self, got, want, what)
    HK.Child.eq = eq
    try:
        _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.Child.eq = E
HK.run_compare = _compare


def jload(z, n):
    return json.loads(z.read(n).decode("utf-8-sig"))


def lang_of(z):
    return z.read(LANG).decode("utf-8").replace("\r\n", "\n").split("\n")


# ---------------------------------------------------------------------------------------------------------------- the world scan (read only)
def jsons(z, names):
    for n in names:
        if n.endswith(".json") and n.startswith("Server/"):
            try:
                yield n, jload(z, n)
            except Exception:
                continue


def world_sources():
    """(label, zipfile) of Assets.zip, every other SET jar, every installed non-Skyy mod (zip / jar; folders read via a dict) - read only"""
    out = [("Assets.zip", zipfile.ZipFile(ASSETS))]
    dst = open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()
    s0 = dst.index("SET = [")
    for m, v in re.findall(r'\("(Skyy\w+)", "([0-9][0-9.]*)"\)', dst[s0:dst.index("\n]\n", s0)]):
        p = os.path.join(ROOT, m, "%s-%s.jar" % (m, v))
        if m != "SkyyArmory" and os.path.isfile(p):
            out.append(("%s %s" % (m, v), zipfile.ZipFile(p)))
    if os.path.isdir(B.MODS_DIR):
        for f in sorted(os.listdir(B.MODS_DIR)):
            p = os.path.join(B.MODS_DIR, f)
            if f.lower().endswith((".zip", ".jar")) and os.path.isfile(p) and not f.startswith("Skyy"):
                try:
                    out.append(("Mods/" + f, zipfile.ZipFile(p)))
                except Exception:
                    pass
    return out


def scan(label, z, hits):
    for n, d in jsons(z, z.namelist()):
        if not isinstance(d, dict):
            continue
        txt = json.dumps(d)
        if BENCH in txt:
            hits["bench"].append("%s %s" % (label, n))
        if "SkyyArmory_Any_" in txt:
            hits["rt"].append("%s %s" % (label, n))


# ---------------------------------------------------------------------------------------------------------------- SkyyGear's readers, ported
def recipes_of(z):
    """every recipe of a jar the engine way: rid -> {Input, PrimaryOutput} (item Recipe -> <item>_Recipe_Generated_0, output the item x1)"""
    out = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            d = jload(z, n)
            if isinstance(d, dict) and d.get("Recipe"):
                iid = os.path.basename(n)[:-5]
                out[iid + "_Recipe_Generated_0"] = {"Input": d["Recipe"]["Input"], "PrimaryOutput": {"ItemId": iid, "Quantity": 1}}
        elif n.startswith("Server/Item/Recipes/") and n.endswith(".json"):
            out[os.path.basename(n)[:-5]] = jload(z, n)
    return out


def from_recipe(rc, frm, to):
    po = rc.get("PrimaryOutput") or {}
    if po.get("ItemId") != to or int(po.get("Quantity", 1)) != 1:
        return None
    has, ids = False, []
    for q in rc.get("Input") or []:
        iid = q.get("ItemId")
        if iid is None:
            return None          # GearUp.fromRecipe: a resource-type / tag input = this recipe is not a ladder step
        if iid == frm and not has and int(q["Quantity"]) == 1:
            has = True
            continue
        if iid in (frm, to):
            return None
        if int(q["Quantity"]) < 1:
            continue
        ids.append((iid, int(q["Quantity"])))
    return sorted(ids) if has else None


def earlier(x, frm, ladder):
    if x == frm or x not in ladder or frm not in ladder:
        return False
    return ladder.index(x) < ladder.index(frm)


def from_recipe_alt(rc, frm, to, ladder):
    po = rc.get("PrimaryOutput") or {}
    if po.get("ItemId") != to or int(po.get("Quantity", 1)) != 1:
        return None
    x = None
    for q in rc.get("Input") or []:
        iid = q.get("ItemId")
        if iid is None or iid == frm:
            return None
        if int(q["Quantity"]) == 1 and earlier(iid, frm, ladder):
            if x is not None:
                return None
            x = iid
    return None if x is None else (x, from_recipe(rc, x, to))


def cost0(recs, frm, to, ladder):
    best = None
    for rid in sorted(recs):
        r = from_recipe(recs[rid], frm, to)
        if r is not None:
            return ("recipe", rid, r)
    for rid in sorted(recs):
        r = from_recipe_alt(recs[rid], frm, to, ladder)
        if r is not None and r[1] is not None:
            return ("alt " + r[0], rid, r[1])
    return best


def recipe_in(recs, iid):
    """GearSalvage.recipeIn: the lowest recipe id whose primary output is iid x1 -> its ITEM-ID inputs (resource inputs skipped)"""
    for rid in sorted(recs):
        po = recs[rid].get("PrimaryOutput") or {}
        if po.get("ItemId") == iid and int(po.get("Quantity", 1)) == 1:
            return rid, sorted((q["ItemId"], int(q["Quantity"])) for q in recs[rid].get("Input") or [] if q.get("ItemId") and int(q["Quantity"]) >= 1)
    return None


def gear_ladder():
    best = ""
    with zipfile.ZipFile(GEAR_JAR) as z:
        for n in z.namelist():
            if n.endswith(".class"):
                for m in re.findall(rb"Weapon_Wand_SoulOrb>[A-Za-z_>]+", z.read(n)):
                    if len(m) > len(best):
                        best = m.decode()
    return best.split(">")


# ---------------------------------------------------------------------------------------------------------------- S
def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    names = set(zn.namelist())
    ln, lo = lang_of(zn), lang_of(zo)
    lname = dict(l.split(" = ", 1) for l in ln if " = " in l)
    # the items
    prev_of = {}
    for t, i in enumerate(SOUL):
        a, b = jload(zn, P_ITEM % i), jload(zo, P_ITEM % i)
        K.eq(a.get("ResourceTypes"), [{"Id": RT[i]}], "S: %s carries exactly its own resource type" % i)
        a2, b2 = dict(a), dict(b)
        a2.pop("ResourceTypes")
        ra, rb = a2.pop("Recipe"), b2.pop("Recipe")
        K.check(a2 == b2, "S: %s = 0.1.37 apart from ResourceTypes + Recipe" % i)
        if t == 0:
            K.check(ra == rb and all("ItemId" in q for q in ra["Input"]), "S: the Soul Orb's own recipe is unchanged (essence + sticks + fibre)")
            continue
        p = rb["Input"][0]
        K.check(set(p) == {"ItemId", "Quantity"} and p["ItemId"] in SOUL[:t] and p["Quantity"] == 1, "S: 0.1.37 %s took %s by item id" % (i, p))
        prev_of[i] = p["ItemId"]
        K.eq(ra["Input"][0], {"ResourceTypeId": RT[p["ItemId"]], "Quantity": 1}, "S: %s takes ANY %s (resource type %s) x1" % (i, p["ItemId"], RT[p["ItemId"]]))
        K.check(ra["Input"][1:] == rb["Input"][1:] and len(ra["Input"]) == 3 and dict((k, v) for k, v in ra.items() if k != "Input") == dict((k, v) for k, v in rb.items() if k != "Input"),
                "S: %s: bars + essence, bench %s, time, knowledge unchanged" % (i, [x["Id"] for x in ra["BenchRequirement"]]))
    K.eq(len(prev_of), 15, "S: all 15 cage tiers checked")
    K.notes.append("S: tiers %s" % "; ".join("%s <- %s" % (k[len("Weapon_Wand_SoulCage_"):], v[len("Weapon_Wand_"):]) for k, v in prev_of.items()))
    # the resource types + names
    for i in SOUL:
        p = P_RT % RT[i]
        d = jload(zn, p) if p in names else None
        icon = jload(zn, P_ITEM % i)["Icon"]
        K.check(d == {"Icon": icon} and ("Common/" + icon) in names, "S: %s = {Icon: the item's own icon, in the jar}" % p)
        K.eq(lname.get("resourceType.%s.name" % RT[i]), "Any " + lname.get("items.%s.name" % i, "?"), "S: the name of %s" % RT[i])
    K.check(sorted(set(ln) - set(lo)) == sorted("resourceType.%s.name = Any %s" % (RT[i], lname["items.%s.name" % i]) for i in SOUL)
            and not (set(lo) - set(ln)), "S: server.lang = 0.1.37's lines + exactly the 16 resource type names")
    # the twins
    for i in SOUL[1:]:
        p = P_LAD % LAD[i]
        d = jload(zn, p) if p in names else {}
        rb = jload(zo, P_ITEM % i)["Recipe"]
        K.check(d.get("Input") == rb["Input"] and d.get("PrimaryOutput") == {"ItemId": i, "Quantity": 1} and d.get("Output") == [{"ItemId": i, "Quantity": 1}]
                and d.get("BenchRequirement") == [{"Type": "Crafting", "Id": BENCH}] and d.get("TimeSeconds") == rb["TimeSeconds"] and d.get("KnowledgeRequired") is True
                and set(d) == {"Input", "PrimaryOutput", "Output", "BenchRequirement", "TimeSeconds", "KnowledgeRequired"},
                "S: twin %s = the 0.1.37 inputs of %s at the hidden bench" % (LAD[i], i))
    K.eq(sorted(n for n in names if n.startswith("Server/Item/Recipes/")), sorted(P_LAD % LAD[i] for i in SOUL[1:]), "S: the jar's only standalone recipes = the 15 twins")
    K.eq(sorted(n for n in names if n.startswith("Server/Item/ResourceTypes/")), sorted(P_RT % RT[i] for i in SOUL), "S: the jar's only resource types = the 16")
    # our jar: nobody else carries / takes our types
    other = []
    for n, d in jsons(zn, zn.namelist()):
        if not isinstance(d, dict):
            continue
        b = os.path.basename(n)[:-5]
        for x in d.get("ResourceTypes") or []:
            if str(x.get("Id", "")).startswith("SkyyArmory_Any_") and not (n == P_ITEM % b and b in SOUL):
                other.append(n)
        rc = d.get("Recipe") or (d if n.startswith("Server/Item/Recipes/") else {})
        for q in rc.get("Input") or []:
            if str(q.get("ResourceTypeId", "")).startswith("SkyyArmory_Any_") and not (b in prev_of and q["ResourceTypeId"] == RT[prev_of[b]]):
                other.append(n)
    K.eq(other, [], "S: in our jar only the 16 Soul items carry the types and only the 15 cage recipes take them")
    # the world (Assets.zip, the other SET jars, the installed Mods - read only)
    hits = {"bench": [], "rt": []}
    srcs = world_sources()
    for label, z in srcs:
        scan(label, z, hits)
    K.eq(hits, {"bench": [], "rt": []}, "S: no file in %d sources (Assets.zip, SET jars, Mods) names the twin bench or our resource types" % len(srcs))
    benches = set()
    with zipfile.ZipFile(ASSETS) as az:
        for n, d in jsons(az, [x for x in az.namelist() if x.startswith("Server/Item/Items/")]):
            bt = d.get("BlockType") if isinstance(d, dict) else None
            if isinstance(bt, dict) and isinstance(bt.get("Bench"), dict) and bt["Bench"].get("Id"):
                benches.add(bt["Bench"]["Id"])
    K.check(BENCH not in benches and "Weapon_Bench" in benches and len(benches) >= 10, "S: no block is the bench %s (vanilla benches: %d)" % (BENCH, len(benches)))
    # SkyyGear 0.3.28's readers on the 0.1.37 jar vs the 0.1.38 jar
    lad = gear_ladder()
    K.check(len(lad) == 16 and lad[0] == SOUL[0] and set(lad) == set(SOUL), "S: SkyyGear 0.3.28's default Soul Cage ladder = the 16 Soul items (%d)" % len(lad))
    rn, ro = recipes_of(zn), recipes_of(zo)
    rn0 = dict((k, v) for k, v in rn.items() if not k.startswith("SkyyArmory_SoulLadder_"))
    diff, none_wo = [], []
    for k in range(1, len(lad)):
        a, b = cost0(rn, lad[k - 1], lad[k], lad), cost0(ro, lad[k - 1], lad[k], lad)
        if b is None or a is None or a[0] != b[0] or a[2] != b[2] or not a[1].startswith("SkyyArmory_SoulLadder_"):
            diff.append((lad[k], a, b))
        if cost0(rn0, lad[k - 1], lad[k], lad) is not None:
            none_wo.append(lad[k])
    K.eq(diff, [], "S: GearUp.cost0 on 0.1.38 = 0.1.37 for all 15 Anvil Upgrade steps (paid through the hidden twins)")
    K.eq(none_wo, [], "S: control - without the twins every step would be 'No recipe makes <next>' (why the twins exist)")
    sv = [(i, recipe_in(rn, i), recipe_in(ro, i)) for i in SOUL[1:]]
    K.check(all(a is not None and b is not None and a[1] == b[1] and a[0] == LAD[i] for i, a, b in sv),
            "S: GearSalvage.recipeIn (lowest recipe id) = the twin, inputs = 0.1.37's, for all 15 cages")
    K.save()


# ---------------------------------------------------------------------------------------------------------------- E
def run_engine(out, jar, scratch, _home):
    from jpype import JClass, JString, JInt, JShort, JArray, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, SACKS_JAR], verify=True)
    Paths = JClass("java.nio.file.Paths")
    # the 0.1.21 harness's engine setup: server options (a scratch universe) + a stand-in HytaleServer holding an EventBus
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(scratch, "universe")]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    for nm, v in (("eventBus", JClass("com.hypixel.hytale.event.EventBus")(False)),):
        f_ = HS.class_.getDeclaredField(nm)
        f_.setAccessible(True)
        f_.set(hs, v)
    f_ = HS.class_.getDeclaredField("instance")
    f_.setAccessible(True)
    f_.set(None, hs)
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    AEI = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo")
    ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR = JClass("com.hypixel.hytale.codec.util.RawJsonReader")
    ITM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    RTY = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ResourceType")
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    # the stores AssetRegistryLoader.init leaves to the modules (the 0.1.21 harness's reg_ilt): stats + interactions + roots + unarmed
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    ARR = JClass("java.lang.reflect.Array")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None

    @JImplements("java.util.function.Predicate")
    class IsUnknown:
        @JOverride
        def test(self, o): return bool(o.isUnknown())
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."

    def reg_ilt(c, path, codec, unknown=False):
        b_ = HAS.builder(c.class_, ILT(ArrOf(c))).setPath(path).setCodec(codec).setKeyFunction(GetId()).setReplaceOnRemove(NoRep())
        if unknown:
            b_ = b_.setIsUnknown(IsUnknown())
        AR.register(b_.build())
    ESTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.EntityStatType")
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")
    for c_, p_, u_ in ((ESTc, "Entity/Stats", False), (INTc, "Item/Interactions", True), (ROOTc, "Item/RootInteractions", False)):
        if AR.getAssetStore(c_.class_) is None:
            reg_ilt(c_, p_, c_.CODEC, u_)
    if AR.getAssetStore(UIc.class_) is None:
        AR.register(HAS.builder(UIc.class_, DAMc()).setPath("Item/Unarmed/Interactions").setCodec(UIc.CODEC).setKeyFunction(GetId()).build())

    def dec(c, key, text):
        st = AR.getAssetStore(c.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(c.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, "exception " + str(e)[:300]
        prob = []
        vr = ei.getValidationResults()
        if vr is not None and vr.hasFailed():
            prob.append("validation failed %s" % [str(x) for x in (vr.getResults() or [])][:3])
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        return o, "; ".join(prob)
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    bad, items, old_items, twins = [], {}, {}, {}
    for i in SOUL:
        o, why = dec(RTY, RT[i], zn.read(P_RT % RT[i]).decode("utf-8-sig"))
        if o is None or why:
            bad.append("%s: %s" % (RT[i], why))
        for z, dst in ((zn, items), (zo, old_items)):
            d_ = jload(z, P_ITEM % i)
            d_.pop("Interactions")          # (the interaction stores are not built here; 0.1.38 changes only ResourceTypes + Recipe)
            o, why = dec(ITM, i, json.dumps(d_))
            if o is None or why:
                bad.append("%s (%s): %s" % (i, "new" if z is zn else "0.1.37", why))
            dst[i] = o
        if i in LAD:
            o, why = dec(CRR, LAD[i], zn.read(P_LAD % LAD[i]).decode("utf-8-sig"))
            if o is None or why:
                bad.append("%s: %s" % (LAD[i], why))
            twins[i] = o
    K.eq(bad, [], "E: 16 resource types + 16 items + 15 twin recipes decode through the engine codecs (no exception / validation failure / unknown key)")
    if bad:
        K.save()
        return
    rts = dict((i, [str(x.id) for x in (items[i].getResourceTypes() or [])]) for i in SOUL)
    K.check(all(rts[i] == [RT[i]] for i in SOUL) and all(not old_items[i].getResourceTypes() for i in SOUL),
            "E: the decoded items carry exactly their own type (0.1.37: none)")
    tw = [(i, twins[i].getPrimaryOutput().getItemId(), [str(b.id) for b in twins[i].getBenchRequirement()]) for i in LAD]
    K.check(all(str(o) == i and b == [BENCH] for i, o, b in tw), "E: each decoded twin makes its cage at bench %s only" % BENCH)
    # the Item store answers with our decoded items (the store's own map; nothing else of the engine is loaded)
    am = ITM.getAssetMap()
    fm = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap").class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    mp = fm.get(am)
    filler = {}
    for i in SOUL:
        mp.put(JString(i), items[i])
    for z in (zn,):
        for i in SOUL[1:]:
            for q in jload(z, P_ITEM % i)["Recipe"]["Input"][1:]:
                if q["ItemId"] not in filler:
                    it_ = ITM(JString(q["ItemId"]))
                    f_ = ITM.class_.getDeclaredField("maxStack")
                    f_.setAccessible(True)
                    f_.setInt(it_, 100)
                    mp.put(JString(q["ItemId"]), it_)
                    filler[q["ItemId"]] = it_
    K.check(str(JClass("com.hypixel.hytale.server.core.inventory.ItemStack")(JString(SOUL[0]), JInt(1)).getItem().getId()) == SOUL[0], "E: the stand-in Item map answers")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    ICc = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    BD = JClass("org.bson.BsonDocument")
    CRM = JClass("com.hypixel.hytale.builtin.crafting.component.CraftingManager")
    CP = JClass("com.skyy.sacks.CraftPage")
    VARIANTS = [("plain", None), ("empty document", "{}"),
                ("Common", '{"SkyyGear": {"v": 3, "r": "Common", "lv": 3, "lines": []}}'),
                ("Uncommon", '{"SkyyGear": {"v": 3, "r": "Uncommon", "lv": 7, "lines": [{"s": "int", "v": 4}]}}'),
                ("Rare", '{"SkyyGear": {"v": 3, "r": "Rare", "lv": 12, "lines": [{"s": "int", "v": 9}, {"s": "mana", "v": 3}]}}'),
                ("Legendary", '{"SkyyGear": {"v": 3, "r": "Legendary", "lv": 30}}'),
                ("Rare, another level", '{"SkyyGear": {"v": 3, "r": "Rare", "lv": 40}}'),
                ("unidentified", '{"SkyyUnid": {"r": "Epic"}}')]

    def stack(iid, md):
        return IS(JString(iid), JInt(1)) if md is None else IS(JString(iid), JInt(1), BD.parse(JString(md)))

    def counts(c):
        m = {}
        for s in range(int(c.getCapacity())):
            it = c.getItemStack(JShort(s))
            if it is None or it.isEmpty():
                continue
            k = (str(it.getItemId()), None if it.getMetadata() is None else str(it.getMetadata().toJson()))
            m[k] = m.get(k, 0) + int(it.getQuantity())
        return m
    lines, which = [], []
    for t, i in enumerate(SOUL):
        if t == 0:
            continue
        f_ = ITM.class_.getDeclaredField("recipeToGenerate")
        f_.setAccessible(True)
        r_new, r_old = f_.get(items[i]), f_.get(old_items[i])
        prev = str(r_old.getInput()[0].getItemId())
        others = [x for x in SOUL if x != prev]
        # the inventory: backpack (variants), storage (decoys: every OTHER Soul item, rolled), hotbar (the bars + essence for every craft)
        bp, sto, hb = SIC(JShort(len(VARIANTS))), SIC(JShort(len(others))), SIC(JShort(4))
        for s, (nm, md) in enumerate(VARIANTS):
            bp.setItemStackForSlot(JShort(s), stack(prev, md))
        for s, x in enumerate(others):
            sto.setItemStackForSlot(JShort(s), stack(x, VARIANTS[4][1]))
        rest = [(str(q.getItemId()), int(q.getQuantity())) for q in r_new.getInput()[1:]]
        for s, (x, q) in enumerate(rest):
            hb.setItemStackForSlot(JShort(s), IS(JString(x), JInt(q * len(VARIANTS))))
        mats = CIC(JArray(ICc)([bp, sto, hb]))
        old_have = int(mats.countRemovableMaterial(r_old.getInput()[0]))
        new_have = int(mats.countRemovableMaterial(r_new.getInput()[0]))
        dec_have = [(x, int(CIC(JArray(ICc)([sto])).countRemovableMaterial(r_new.getInput()[0]))) for x in others[:1]]
        ok_count = old_have == 1 and new_have == len(VARIANTS) and dec_have[0][1] == 0
        before = counts(bp), counts(sto), counts(hb)
        crafted, gave_back, bad_step = 0, 0, []
        lim0 = int(CP.limit(r_new, mats))
        for n in range(len(VARIANTS) + 1):
            ins = CRM.getInputMaterials(r_new, JInt(1))
            if not mats.canRemoveMaterials(ins):
                break
            snap = CP.snapshot(mats)
            k_ = int(ins.size())
            per = JArray(JInt)([int(ins.get(j).getQuantity()) for j in range(k_)])
            b0 = counts(bp)
            tx = mats.removeMaterials(ins)
            took = CP.removedItems(snap, CP.snapshot(mats))
            left = CP.reserve(took, ins, per, JInt(1))
            gone = dict((k, v) for k, v in b0.items() if counts(bp).get(k, 0) != v)
            if not tx.succeeded() or left is None or int(left.size()) != 0 or sum(b0.values()) - sum(counts(bp).values()) != 1:
                bad_step.append((n, bool(tx.succeeded()), None if left is None else str(left), gone))
            if left is not None:
                gave_back += sum(int(v) for v in dict(left).values())
            which.append((i, [k[1] for k in gone]))
            crafted += 1
        after = counts(bp), counts(sto), counts(hb)
        ok_craft = (crafted == len(VARIANTS) and lim0 == len(VARIANTS) and not bad_step and gave_back == 0 and after[0] == {} and after[1] == before[1]
                    and after[2] == {} and int(CP.limit(r_new, mats)) == 0 and not mats.canRemoveMaterials(CRM.getInputMaterials(r_new, JInt(1))))
        if not (ok_count and ok_craft):
            lines.append("%s: old %d new %d decoy %s; limit %d crafted %d bad %s back %d after %s" % (i, old_have, new_have, dec_have, lim0, crafted, bad_step, gave_back, after))
    K.eq(lines, [], "E: every cage tier: the 0.1.37 recipe counts only the plain %s (1 of %d - the bug), the 0.1.38 recipe counts all %d variants "
                    "and no other Soul item; /craft's sequence crafts exactly %d times, one previous item + the bars + the essence each, nothing given "
                    "back, the decoys untouched, then refuses" % ("previous item", len(VARIANTS), len(VARIANTS), len(VARIANTS)), )
    K.notes.append("E: the craft takes the first matching slot in container order (the backpack, then storage, then the hotbar - "
                   "getCombinedBackpackStorageHotbar): %s" % [w[1] for w in which[:len(VARIANTS)]])
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("engine", run_engine)], script=__file__)
