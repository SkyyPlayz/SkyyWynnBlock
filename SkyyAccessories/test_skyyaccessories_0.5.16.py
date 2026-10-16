"""Harness for SkyyAccessories 0.5.16 (THE METAL LANTERNS: the Normal Lantern recipe drops the Deco Lantern; every Lantern's icon + held / worn
texture take its recipe's metal - Normal + Unique Copper, Rare Iron, Legendary Thorium; tools/accessories_0_5_16_patch.py).
Build first: python tools/accessories_0_5_16_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.16.py

    python SkyyAccessories/test_skyyaccessories_0.5.16.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.5.15 -> 0.5.16: the kit's version texts + the WbRank table; non-class entries: manifest.json + the Normal Lantern JSON +
               the 4 Lantern textures / icons + the item JSONs whose ItemLevel moved (the tab order follows the new, cheaper Lantern cost)
  CU  the metal Lanterns, on the JARS (+ the CACHED Assets.zip, read-only):
        - Normal Lantern recipe = Crude Torch x4 + Copper Bar x2 (no Deco Lantern); bench, category, KnowledgeRequired, output, quality,
          names unchanged; every input is a real Assets.zip item; Unique / Rare / Legendary recipes byte-identical (each from the one below)
        - every other changed item JSON differs ONLY in ItemLevel; ItemLevel = 1 .. 51 along the 0.5.16 jar's WbRank.ORDER (loaded in
          the JVM) + Omni, rarity tiers ascending, no ties
        - every Lantern item: Model / Texture / Icon paths are item paths (never under Blocks/, no '../', no backslash), each file in the
          jar or in Assets.zip; the texture is a 64 x 64-class PNG the same size as its vanilla source
        - each rarity: its recipe's metal bar = its look metal; model = the vanilla lantern's; texture = same size + alpha as its vanilla
          texture, the glowing core (Light_On) texels identical, every changed texel on that metal's vanilla gradient, the recoloured mean
          reads as the metal; the icon is new and its metal texels read as the metal (vs 0.5.15); the other 40 own icons byte-identical
  AA  engine-access audit
NOT driven here: the native client's look (Skyy's in-game look decides). No saved-data change -> no live phase.
Exit code 1 on any failure.
"""
import os, sys, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyart as SA
import serverjar

VERSION = "0.5.16"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.15.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "acc0516", "harness")))
PKG = "com.skyy.accessories."
TAB_ID = "Workbench_SkyyAccessories"
OMNI = "Skyy_Accessory_Omni"
QUAL = ["Skyy_Acc_Normal", "Skyy_Acc_Unique", "Skyy_Acc_Rare", "Skyy_Acc_Legendary"]
LAN = ["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Lantern_Uncommon", "Skyy_Talisman_Lantern_Rare", "Skyy_Talisman_Lantern_Epic"]
LAN_JSON = "Server/Item/Items/Utility/%s.json"
RAR = [None, "Normal", "Unique", "Rare", "Legendary"]
METAL = [None, "Copper", "Copper", "Iron", "Thorium"]          # the look = the metal bar of each recipe
VLOOK = [None, "Server/Item/Items/Deco/Deco_Lantern.json", "Server/Item/Items/Furniture/Kweebec/Furniture_Kweebec_Lantern.json",
         "Server/Item/Items/Furniture/Desert/Furniture_Desert_Lantern.json",
         "Server/Item/Items/Furniture/Temple_Light/Furniture_Temple_Light_Lantern.json"]
ART = (["Common/Items/SkyyAccessories/SkyyAccessories_Lantern_%s_Texture.png" % r for r in RAR[1:]] +
       ["Common/Icons/ItemsGenerated/SkyyAccessories_Lantern_%s.png" % r for r in RAR[1:]])
# a texture's recoloured mean / an icon texel "reads as" the metal (independent of the build's gradient code)
HUE = {"Copper": lambda c: c[0] - c[2] > 60 and c[0] > c[1] > c[2],
       "Iron": lambda c: max(c) - min(c) < 30,
       "Thorium": lambda c: c[1] > c[0] + 10}
PIX = {"Copper": lambda c: c[0] - c[2] > 50 and c[0] > c[1] > c[2] and c[1] < 0.7 * c[0],   # g < 0.7 r: copper, not gold
       "Iron": lambda c: max(c[:3]) - min(c[:3]) < 25 and 50 < sum(c[:3]) / 3.0 < 245,
       "Thorium": lambda c: c[1] > c[0] + 15 and c[1] >= c[2] - 10}


def on_gradient(c, grad, tol=3.0):
    """colour c lies on the gradient polyline (within tol per channel = the recolour's rounding)"""
    for i in range(len(grad) - 1):
        a, b = grad[i], grad[i + 1]
        d = [b[k] - a[k] for k in range(3)]
        dd = sum(v * v for v in d)
        u = 0.0 if dd == 0 else max(0.0, min(1.0, sum((c[k] - a[k]) * d[k] for k in range(3)) / dd))
        if all(abs(c[k] - (a[k] + d[k] * u)) <= tol for k in range(3)):
            return True
    return False
EXPECT = {          # the version text "0.5.16" (the same three members every version bump changes, cf. 0.5.15's harness) + the WbRank table
    "SkyyAccessoriesPlugin": ["~m setup"],
    "CfgRows": ["~m header"],
    "CfgFn": ["~m opExport"],
    "WbRank": ["~<clinit>"],   # ORDER / TIER rebuilt from the new Lantern costs (CU: only the Lantern ids moved)
}
ADDED = []


def items_of(jar):
    z = zipfile.ZipFile(jar)
    out = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            out[n] = z.read(n).decode("utf8")
    return out


def level_moved(new, old):
    return sorted(p for p in new if p in old and json.loads(new[p]).get("ItemLevel") != json.loads(old[p]).get("ItemLevel"))


def expected_changed():
    new, old = items_of(JAR), items_of(OLD_JAR)
    return sorted(set(level_moved(new, old)) | {LAN_JSON % LAN[0]} | set(ART))


# C: the kit's compare allows only manifest.json among non-class entries - 0.5.16 also changes the Normal Lantern JSON, the 4 Lantern
# textures + icons and
# the ItemLevel of the recipes the cheaper Lantern passed (each checked in CU), so that one comparison gets those paths added
_ChildBase = HK.Child


class _Child(_ChildBase):
    def eq(self, got, want, what):
        if what == "C: non-class entries changed":
            want = sorted(list(want) + expected_changed())
        return _ChildBase.eq(self, got, want, what)


HK.Child = _Child


def tab_ids(items):
    got = []
    for p, t in items.items():
        r = json.loads(t).get("Recipe") or {}
        if any(TAB_ID in (q.get("Categories") or []) for q in r.get("BenchRequirement") or []):
            got.append(os.path.basename(p)[:-5])
    return sorted(got)


def run_copper(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    L = JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())
    WR = JClass(PKG + "WbRank", loader=L)
    server = [str(x) for x in WR.ORDER] + [OMNI]
    tiers = [int(x) for x in WR.TIER]
    arr2 = JArray(URL)(1)
    arr2[0] = JClass("java.io.File")(OLD_JAR).toURI().toURL()
    L2 = JClass("java.net.URLClassLoader")(arr2, JClass("java.lang.ClassLoader").getSystemClassLoader())
    WR2 = JClass(PKG + "WbRank", loader=L2)
    old_server = [str(x) for x in WR2.ORDER] + [OMNI]
    K.check(server != old_server, "CU control: the 0.5.16 WbRank order differs from 0.5.15's")
    K.eq([i for i in server if i not in LAN], [i for i in old_server if i not in LAN], "CU WbRank: without the 4 Lanterns the order is 0.5.15's")
    K.eq(sorted(server), sorted(old_server), "CU WbRank: the same ids")
    A = zipfile.ZipFile(serverjar.assets_zip())   # the cached copy, read-only
    anames = set(A.namelist())
    vitems = set(os.path.basename(n)[:-5] for n in anames if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nnames = set(zn.namelist())
    new, old = items_of(jar), items_of(OLD_JAR)
    tab = tab_ids(new)
    K.eq(sorted(new), sorted(old), "CU the same item files (ids unchanged)")
    K.eq(tab, tab_ids(old), "CU the same 51 recipes sit in the tab")
    # ---- the recipe
    a, b = json.loads(old[LAN_JSON % LAN[0]]), json.loads(new[LAN_JSON % LAN[0]])
    K.eq(b["Recipe"]["Input"], [{"ItemId": "Furniture_Crude_Torch", "Quantity": 4}, {"ItemId": "Ingredient_Bar_Copper", "Quantity": 2}],
         "CU Normal Lantern = Crude Torch x4 + Copper Bar x2")
    K.check([x for x in a["Recipe"]["Input"] if x.get("ItemId") != "Deco_Lantern"] == b["Recipe"]["Input"] and
            any(x.get("ItemId") == "Deco_Lantern" for x in a["Recipe"]["Input"]), "CU ... = 0.5.15's inputs minus the Deco Lantern (control: 0.5.15 had it)")
    ra, rb = dict(a["Recipe"]), dict(b["Recipe"])
    ra.pop("Input"), rb.pop("Input")
    K.eq(rb, ra, "CU Normal Lantern: bench, category, KnowledgeRequired, time, output unchanged")
    K.check(rb.get("KnowledgeRequired") is True and rb["BenchRequirement"] == [{"Type": "Crafting", "Id": "Workbench", "Categories": [TAB_ID]}],
            "CU ... still the Workbench tab, still unlocked by the Tree Sap collection (KnowledgeRequired)")
    a2, b2 = dict(a), dict(b)
    for d in (a2, b2):
        d.pop("Recipe"), d.pop("ItemLevel")
    K.eq(b2, a2, "CU Normal Lantern: every other key unchanged (quality, model, texture path, icon path, scale)")
    K.eq([x["ItemId"] for x in b["Recipe"]["Input"] if x["ItemId"] not in vitems], [], "CU every input is a real Assets.zip item")
    for t in range(2, 5):
        n = json.loads(new[LAN_JSON % LAN[t - 1]])
        o = json.loads(old[LAN_JSON % LAN[t - 1]])
        K.eq(n["Recipe"], o["Recipe"], "CU %s recipe unchanged" % LAN[t - 1])
        K.eq(n["Recipe"]["Input"][0], {"ItemId": LAN[t - 2], "Quantity": 1}, "CU ... still crafted from the rarity below")
    # ---- every other change = ItemLevel only; the order rule
    changed = sorted(p for p in new if new[p] != old[p])
    bad = []
    for p in changed:
        if p == LAN_JSON % LAN[0]:
            continue
        x, y = json.loads(old[p]), json.loads(new[p])
        x.pop("ItemLevel", None), y.pop("ItemLevel", None)
        if x != y:
            bad.append(os.path.basename(p))
    K.eq(bad, [], "CU every other changed item JSON differs only in ItemLevel")
    node = dict((i, json.loads(new[LAN_JSON % i])) for i in tab)
    lvl = dict((i, node[i]["ItemLevel"]) for i in tab)
    rar = dict((i, QUAL.index(node[i]["Quality"])) for i in tab)
    K.check(sorted(server) == tab and server[0] == "Skyy_Accessory_Workbench_T1", "CU the server order lists every tab recipe once, Workbench I first")
    K.eq([lvl[i] for i in server], list(range(1, 52)), "CU ItemLevel = 1 .. 51 along the 0.5.16 server order (no ties)")
    K.check(all(tiers[k] <= tiers[k + 1] for k in range(len(tiers) - 1)) and tiers[1:] == [rar[i] + 1 for i in server[1:-1]],
            "CU rarity tiers ascending along the order")
    olvl = dict((i, json.loads(old[LAN_JSON % i])["ItemLevel"]) for i in tab)
    K.check(lvl[LAN[0]] < olvl[LAN[0]] and lvl[LAN[1]] <= olvl[LAN[1]], "CU the cheaper Normal / Unique Lanterns move up inside their tier (%d -> %d, %d -> %d)"
            % (olvl[LAN[0]], lvl[LAN[0]], olvl[LAN[1]], lvl[LAN[1]]))
    # ---- paths of every Lantern item
    for i in LAN:
        n = json.loads(new[LAN_JSON % i])
        for k in ("Model", "Texture", "Icon"):
            v = n[k]
            K.check(not v.startswith("Blocks/") or k == "Model", "CU %s %s is not a Blocks/ path (%s)" % (i, k, v))
            K.check(".." not in v and "\\" not in v and not v.startswith("/"), "CU %s %s has no '../' / backslash / leading slash" % (i, k))
            K.check(("Common/" + v) in nnames or ("Common/" + v) in anames, "CU %s %s file exists (jar or Assets.zip): %s" % (i, k, v))
        K.check(n["Texture"].startswith("Items/SkyyAccessories/") and n["Icon"].startswith("Icons/ItemsGenerated/SkyyAccessories_"),
                "CU %s texture / icon are OUR item paths" % i)
    # ---- the art: each rarity's texture + icon in its recipe metal
    other = sorted(nm for nm in nnames | set(zo.namelist()) if not nm.endswith(".class") and not nm.startswith("Server/Item/Items/")
                   and nm != "manifest.json" and (nm not in zo.namelist() or nm not in nnames or zn.read(nm) != zo.read(nm)))
    K.eq(other, sorted(ART), "CU besides item JSONs only the 4 Lantern textures + 4 Lantern icons changed (lang, other icons, models identical)")
    icons = sorted(nm for nm in nnames if nm.startswith("Common/Icons/ItemsGenerated/SkyyAccessories_"))
    K.eq([nm for nm in icons if nm not in ART and zn.read(nm) != zo.read(nm)], [], "CU the other %d own icons are byte-identical" % (len(icons) - 4))
    summary = []
    for t in range(1, 5):
        metal = METAL[t]
        n = json.loads(new[LAN_JSON % LAN[t - 1]])
        bars = [x["ItemId"] for x in n["Recipe"]["Input"] if x.get("ItemId", "").startswith("Ingredient_Bar_")]
        K.eq(bars, ["Ingredient_Bar_" + metal], "CU %s: the recipe's metal bar = the look metal (%s)" % (RAR[t], metal))
        vanilla = json.loads(A.read(VLOOK[t]).decode("utf-8-sig"))["BlockType"]
        K.eq(n["Model"], vanilla["CustomModel"], "CU %s: the model is still the vanilla lantern's" % RAR[t])
        va, vb = SA.png_decode(A.read("Common/" + vanilla["CustomModelTexture"][0]["Texture"])), SA.png_decode(zn.read("Common/" + n["Texture"]))
        K.check((va.w, va.h) == (vb.w, vb.h), "CU %s texture has the vanilla size %dx%d" % (RAR[t], va.w, va.h))
        light = SA.node_rects(A.read("Common/" + n["Model"]), ["Light_On", "Light_Off"])
        grad = SA.metal_gradient(A, metal)
        alpha_bad, light_bad, off, nch = 0, 0, [], 0
        sb = [0, 0, 0]
        for y in range(va.h):
            for x in range(va.w):
                ca, cb = va.get(x, y), vb.get(x, y)
                alpha_bad += ca[3] != cb[3]
                if any(r[0] <= x < r[2] and r[1] <= y < r[3] for r in light):
                    light_bad += ca != cb
                elif ca != cb:
                    nch += 1
                    if not on_gradient(cb, grad):
                        off.append((x, y, cb))
                    for k in range(3):
                        sb[k] += cb[k]
        K.eq(alpha_bad, 0, "CU %s texture: alpha identical to vanilla" % RAR[t])
        K.eq(light_bad, 0, "CU %s texture: the glowing core (Light_On) keeps its vanilla texels (%d light rects)" % (RAR[t], len(light)))
        K.check(nch > 300, "CU %s texture: %d texels recoloured" % (RAR[t], nch))
        K.eq(off[:5], [], "CU %s texture: every recoloured texel lies on the vanilla %s gradient" % (RAR[t], metal))
        mb = [v / float(max(nch, 1)) for v in sb]
        K.check(HUE[metal](mb), "CU %s texture: the recoloured mean %s reads as %s" % (RAR[t], "#%02x%02x%02x" % tuple(int(v) for v in mb), metal))
        p_icon = "Common/" + n["Icon"]
        ic_new, ic_old = SA.png_decode(zn.read(p_icon)), SA.png_decode(zo.read(p_icon))
        K.check((ic_new.w, ic_new.h) == (64, 64) and zn.read(p_icon) != zo.read(p_icon), "CU %s icon is new, 64 x 64" % RAR[t])
        cnt = lambda im: sum(1 for y in range(64) for x in range(64) if im.get(x, y)[3] > 200 and PIX[metal](im.get(x, y)))
        cn, co = cnt(ic_new), cnt(ic_old)
        K.check(cn > co + 250, "CU %s icon's metal is %s (%s-coloured texels %d, 0.5.15 had %d)" % (RAR[t], metal, metal, cn, co))
        summary.append("%s %s (texture %d texels, mean %s; icon %d metal texels)" % (RAR[t], metal, nch, "#%02x%02x%02x" % tuple(int(v) for v in mb), cn))
    print("CU Normal Lantern: %s; ItemLevel %d -> %d; looks: %s" % (
        " + ".join("%s x%d" % (x["ItemId"], x["Quantity"]) for x in b["Recipe"]["Input"]), olvl[LAN[0]], lvl[LAN[0]], " | ".join(summary)))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("copper", run_copper)], script=__file__)
