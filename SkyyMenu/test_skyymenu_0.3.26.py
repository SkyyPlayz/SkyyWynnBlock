"""Harness for SkyyMenu 0.3.26 (our own icons, wave 1 - art/menu-icons-2; tools/menu_0_3_26_patch.py).
Build first: python tools/menu_0_3_26_patch.py && python SkyyMenu/build_skyymenu_0.3.26.py

    python SkyyMenu/test_skyymenu_0.3.26.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.25 -> 0.3.26: only MenuData (the icon tables + 2 new constants) and the MenuPage methods that inline the icon constants
  ICON the jar + MenuData read in a JVM: every icon id the menu can put in a slot (E_ICON, PA_ICON, ICON_*, the edit-layout icons, the Mods
       list icons, the pet icons) resolves to a SHIPPED asset - our item JSON (Server/Item/Items/Utility/<id>.json) whose Icon PNG is in the
       jar (64 x 64 RGBA, = art/menu-icons-2 / art/menu-icons byte for byte via the manifests), or a vanilla item of the CACHED Assets.zip;
       the 14 wave-1 icons are ours and hidden (Variant, no Categories / Recipe / Interactions) and named in server.lang; the wave-1 spots
       (main 11, tp 11 / 13 / 15, players 47 / 51, player actions 29 / 30 / 31, Back / Prev / Next / Close / Warp / WarpLocked / NoWarps /
       Player) no longer name the vanilla id they replaced (and 0.3.25 did - control); every other table equals 0.3.25's
  WARP MenuPage.fillWarps EXECUTED with no TeleportPlugin: "No warps yet" lands on NO_WARPS_SLOT with our NoWarps icon; the method's
       bytecode picks ICON_WARP / ICON_WARP_LOCKED by the unlock check (no Tool_Map left)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, hashlib, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.3.26"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.25.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menu0326", "menu")))
PKG = "com.skyy.menu."
EXPECT = {
    "MenuData": ["~<clinit>", "+f ICON_WARP_LOCKED", "+f ICON_NO_WARPS"],
    "MenuPage": ["~m fillWarps", "~m fillPlayers", "~m fillPlayer", "~m nav"],   # the icon constants javassist inlines
    "CfgFn": ["~m opExport"],                         # the version texts
    "CfgRows": ["~m header"],
    "OpsPage": ["~<clinit>"],
    "SkyyMenuPlugin": ["~m setup"],
}
# the jar's non-class entries that may change (tools/harness_kit.py run_compare expects only manifest.json): + the 14 icon items (item
# JSON + PNG each) and server.lang (their names)
NEW_FILES = sorted(["manifest.json", "Server/Languages/en-US/server.lang"] +
                   ["Server/Item/Items/Utility/Skyy_Menu_Icon_%s.json" % n for n in ("MyIsland", "Hub", "Spawn", "Warp", "WarpLocked",
                    "NoWarps", "Shards", "Back", "Prev", "Next", "Close", "Player", "Accept", "Deny")] +
                   ["Common/Icons/ItemsGenerated/Skyy_Menu_Icon_%s.png" % n for n in ("MyIsland", "Hub", "Spawn", "Warp", "WarpLocked",
                    "NoWarps", "Shards", "Back", "Prev", "Next", "Close", "Player", "Accept", "Deny")])
if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            want = NEW_FILES
            what = "C: non-class entries changed (0.3.26: + the 14 icon items + server.lang)"
        return _eq0(self, sorted(got) if isinstance(got, list) else got, want, what)
    HK.Child.eq = _eq
ADDED = []

W1 = [("MyIsland", "Soil_Grass"), ("Hub", "Hub_Portal_Default"), ("Spawn", "Spawn_Portal"), ("Warp", "Tool_Map"), ("WarpLocked", "Tool_Map"),
      ("NoWarps", "Tool_Map"), ("Shards", "Portal_Device"), ("Back", "Weapon_Arrow_Iron"), ("Prev", "Weapon_Arrow_Crude"),
      ("Next", "Weapon_Arrow_Iron"), ("Close", "Furniture_Flag_Small_Red"), ("Player", "Armor_Leather_Light_Head"),
      ("Accept", "Ingredient_Crystal_Green"), ("Deny", "Ingredient_Crystal_Red")]
SPOTS = {("main", 11): "Shards", ("tp", 11): "MyIsland", ("tp", 13): "Hub", ("tp", 15): "Spawn", ("players", 47): "Accept",
         ("players", 51): "Deny"}
PA_SPOTS = {29: "Hub", 30: "Spawn", 31: "MyIsland"}
CHROME = {"ICON_BACK": "Back", "ICON_PREV": "Prev", "ICON_NEXT": "Next", "ICON_CLOSE": "Close", "ICON_WARP": "Warp",
          "ICON_WARP_LOCKED": "WarpLocked", "ICON_NO_WARPS": "NoWarps", "ICON_PLAYER": "Player"}


def png_ok(data):
    return data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR" and struct.unpack(">II", data[16:24]) == (64, 64) and data[24:26] == b"\x08\x06"


def run_icon(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    URL, File = JClass("java.net.URL"), JClass("java.io.File")
    old = JClass("java.net.URLClassLoader")(JArray(URL)([File(OLD_JAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()]),
                                            JClass("java.lang.ClassLoader").getPlatformClassLoader())
    OD = JClass("java.lang.Class").forName(PKG + "MenuData", True, old)
    ND = JClass(PKG + "MenuData").class_

    def arr(C, n):
        return [str(x) for x in C.getField(n).get(None)]

    def sv(C, n):
        return str(C.getField(n).get(None))
    zj = zipfile.ZipFile(jar)
    names = set(zj.namelist())
    lang = zj.read("Server/Languages/en-US/server.lang").decode("utf8").split("\n")
    import serverjar
    az = zipfile.ZipFile(serverjar.assets_zip())
    vanilla = set(os.path.basename(n)[:-5] for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    common = set(n for n in az.namelist() if n.startswith("Common/Icons/"))

    # the art manifests: path (relative to Common/) -> sha256
    shas = {}
    for d in ("art/menu-icons-2", "art/menu-icons"):
        m = json.load(open(os.path.join(ROOT, *(d + "/manifest.json").split("/")), encoding="utf8"))
        for f in m["files"]:
            if f["path"].startswith("Common/") and f.get("sha256"):
                shas[f["path"][7:]] = f["sha256"]
    m2 = json.load(open(os.path.join(ROOT, "art", "menu-icons-2", "manifest.json"), encoding="utf8"))
    K.eq([(i["name"], i["replaces_vanilla_id"]) for i in m2["icons"]], W1, "ICON the manifest lists the 14 wave-1 icons (and what each replaces)")

    def ours(iid):
        p = "Server/Item/Items/Utility/%s.json" % iid
        if p not in names:
            return None
        js = json.loads(zj.read(p).decode("utf8"))
        return js

    def resolves(iid, where):
        js = ours(iid)
        if js is not None:
            ic = js.get("Icon", "")
            ok = ("Common/" + ic) in names and png_ok(zj.read("Common/" + ic))
            K.check(ok, "ICON %s: %s = our item, its Icon %s ships in the jar (64 x 64 RGBA)" % (where, iid, ic))
            return "ours"
        K.check(iid in vanilla, "ICON %s: %s resolves (vanilla item of the cached Assets.zip)" % (where, iid))
        return "vanilla"

    # 1. every id the menu can show
    ids = {}
    for n in ("E_ICON", "PA_ICON", "PET_ICON", "MOD_ICON"):
        try:
            for i, x in enumerate(arr(ND, n)):
                ids.setdefault(x, "%s[%d]" % (n, i))
        except Exception:
            K.check(n == "MOD_ICON", "ICON MenuData.%s exists" % n)
    for f in ND.getFields():
        fn = str(f.getName())
        if fn.startswith("ICON_") and str(f.getType().getName()) == "java.lang.String":
            ids.setdefault(str(f.get(None)), fn)
    kinds = {}
    for iid in sorted(ids):
        kinds[iid] = resolves(iid, ids[iid])
    print("ICON: %d icon ids, %d ours, %d vanilla" % (len(kinds), sum(1 for v in kinds.values() if v == "ours"), sum(1 for v in kinds.values() if v == "vanilla")))

    # 2. the 14 wave-1 icons: ours, hidden, named, = the art byte for byte, no vanilla clash
    for nm, was in W1:
        iid = "Skyy_Menu_Icon_" + nm
        js = ours(iid)
        K.check(js is not None and iid not in vanilla, "ICON %s ships as our item (not a vanilla id)" % iid)
        if js is None:
            continue
        rel = js.get("Icon", "")
        K.check(js.get("Variant") is True and "Categories" not in js and "Recipe" not in js and "Interactions" not in js,
                "ICON %s is hidden from the creative library (Variant, no Categories / Recipe / Interactions)" % iid)
        data = zj.read("Common/" + rel) if ("Common/" + rel) in names else b""
        K.check(rel == "Icons/ItemsGenerated/%s.png" % iid and hashlib.sha256(data).hexdigest() == shas.get(rel) and
                data == open(os.path.join(ROOT, "art", "menu-icons-2", "Common", *rel.split("/")), "rb").read(),
                "ICON %s's PNG = art/menu-icons-2 byte for byte (manifest sha256)" % iid)
        K.check(("Common/" + rel) not in common, "ICON %s's PNG path is not a vanilla file" % iid)
        K.check(any(l.startswith("server.items.%s.name=" % iid) for l in lang), "ICON %s has a name in server.lang" % iid)

    # 3. the wave-1 spots: ours now, the replaced vanilla id before (0.3.25 = control)
    NV, NS, NI = arr(ND, "E_VIEW"), [int(x) for x in ND.getField("E_SLOT").get(None)], arr(ND, "E_ICON")
    OV, OS_, OI = arr(OD, "E_VIEW"), [int(x) for x in OD.getField("E_SLOT").get(None)], arr(OD, "E_ICON")
    was = dict(W1)
    for (v, sl), nm in sorted(SPOTS.items()):
        n_ = [NI[i] for i in range(len(NV)) if NV[i] == v and NS[i] == sl]
        o_ = [OI[i] for i in range(len(OV)) if OV[i] == v and OS_[i] == sl]
        K.eq(n_, ["Skyy_Menu_Icon_" + nm], "ICON %s %d wears Skyy_Menu_Icon_%s" % (v, sl, nm))
        K.eq(o_, [was[nm]], "ICON control: 0.3.25's %s %d wore the vanilla %s" % (v, sl, was[nm]))
    NPS, NPI = [int(x) for x in ND.getField("PA_SLOT").get(None)], arr(ND, "PA_ICON")
    OPS, OPI = [int(x) for x in OD.getField("PA_SLOT").get(None)], arr(OD, "PA_ICON")
    for sl, nm in sorted(PA_SPOTS.items()):
        K.eq(NPI[NPS.index(sl)], "Skyy_Menu_Icon_" + nm, "ICON player action %d reuses Skyy_Menu_Icon_%s" % (sl, nm))
        K.eq(OPI[OPS.index(sl)], was[nm], "ICON control: 0.3.25's player action %d wore %s" % (sl, was[nm]))
    for fn, nm in sorted(CHROME.items()):
        K.eq(sv(ND, fn), "Skyy_Menu_Icon_" + nm, "ICON MenuData.%s = Skyy_Menu_Icon_%s" % (fn, nm))
    for fn in ("ICON_BACK", "ICON_PREV", "ICON_NEXT", "ICON_CLOSE", "ICON_WARP", "ICON_PLAYER"):
        K.check(sv(OD, fn) == was[CHROME[fn]], "ICON control: 0.3.25's %s was the vanilla %s" % (fn, was[CHROME[fn]]))
    # every other entry / player action / table unchanged
    for i in range(len(NV)):
        if (NV[i], NS[i]) not in SPOTS:
            K.check(NI[i] == OI[i], "ICON %s %d keeps its icon %s" % (NV[i], NS[i], OI[i]))
    for i, sl in enumerate(NPS):
        if sl not in PA_SPOTS:
            K.check(NPI[i] == OPI[i], "ICON player action %d keeps %s" % (sl, OPI[i]))
    for n in ("E_VIEW", "E_SLOT", "E_NAME", "E_BODY", "E_FOOT", "E_ACT", "E_PERM", "E_OPEN", "E_NEED", "E_UNLOCK", "E_KEY", "PA_SLOT",
              "PA_NAME", "PA_CMD", "WARP_SLOTS", "PLAYER_SLOTS", "MOD_SLOTS", "PET_ICON", "MOD_NAME"):
        K.eq([str(x) for x in ND.getField(n).get(None)], [str(x) for x in OD.getField(n).get(None)], "ICON MenuData.%s = 0.3.25's" % n)
    K.eq(len([n for n in names if n.startswith("Server/Item/Items/Utility/Skyy_Menu_Icon_")]),
         len([n for n in zipfile.ZipFile(OLD_JAR).namelist() if n.startswith("Server/Item/Items/Utility/Skyy_Menu_Icon_")]) + 14,
         "ICON the jar ships 14 more icon items than 0.3.25")
    K.save()


def run_warp(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hclasses")
    os.makedirs(hcls, exist_ok=True)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, hcls], verify=True)
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    # the item asset stand-ins of test_skyymenu_0.3.16.py (new ItemStack(id, 1) asks Item's asset store; every id = one empty Item)
    HP = JClass("javassist.ClassPool")(False)
    HP.appendSystemPath()
    HP.appendClassPath(B.SERVER_JAR)
    CtNewMethod, CtNewConstructor, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor"), JClass("javassist.CtField")

    def hclass(name, sup, ctor, fields=(), meths=()):
        c = HP.makeClass(name, HP.get(sup))
        for s_ in fields:
            c.addField(CtField.make(s_, c))
        c.addConstructor(CtNewConstructor.make(ctor, c))
        for s_ in meths:
            c.addMethod(CtNewMethod.make(s_, c))
        c.writeFile(hcls)
    hclass("skyymenuharness26.ItemMap", "com.hypixel.hytale.assetstore.map.DefaultAssetMap", "public ItemMap() { super(); }",
           ["public com.hypixel.hytale.assetstore.JsonAsset item;", "public java.util.ArrayList asked;"],
           ["public com.hypixel.hytale.assetstore.JsonAsset getAsset(Object k) { if (this.asked == null) this.asked = new java.util.ArrayList(); "
            "this.asked.add(k); return this.item; }"])
    hclass("skyymenuharness26.Items", "com.hypixel.hytale.assetstore.AssetStore",
           "public Items() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }",
           ["public com.hypixel.hytale.assetstore.AssetMap map;"],
           ["public com.hypixel.hytale.assetstore.AssetMap getAssetMap() { return this.map; }"])
    ITc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    IMAP = U.allocateInstance(JClass("skyymenuharness26.ItemMap").class_)
    IMAP.item = U.allocateInstance(ITc.class_)
    ISTORE = U.allocateInstance(JClass("skyymenuharness26.Items").class_)
    ISTORE.map = IMAP
    MP = JClass(PKG + "MenuPage")
    MD = JClass(PKG + "MenuData")

    def jf(c, name):
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    jf(ITc.class_, "ASSET_STORE").set(None, ISTORE)
    p = U.allocateInstance(MP.class_)
    JA = JClass("java.lang.reflect.Array")
    for fn, t in (("acts", "java.lang.String"), ("names", "java.lang.String"), ("bodies", "java.lang.String")):
        jf(MP.class_, fn).set(p, JA.newInstance(Cls.forName(t), 54))
    for f in MP.class_.getDeclaredFields():
        f.setAccessible(True)
        if f.getType().isArray() and f.get(p) is None and not JClass("java.lang.reflect.Modifier").isStatic(f.getModifiers()):
            f.set(p, JA.newInstance(f.getType().getComponentType(), 54))
    slots = JClass("java.util.ArrayList")()
    for _i in range(54):
        slots.add(None)
    try:
        p.fillWarps(slots)
        gs = slots.get(int(MD.NO_WARPS_SLOT))
        K.check(gs is not None, "WARP no TeleportPlugin: \"No warps yet\" is put on NO_WARPS_SLOT %d" % int(MD.NO_WARPS_SLOT))
        if gs is not None:
            ISc = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
            st = [f.get(gs) for f in [jf(gs.getClass(), str(g.getName())) for g in gs.getClass().getDeclaredFields()]
                  if ISc.class_.isAssignableFrom(f.getType())][0]
            iid = str(st.getItemId())
            K.eq(iid, "Skyy_Menu_Icon_NoWarps", "WARP the \"No warps yet\" tile shows our NoWarps icon (was Tool_Map)")
            K.eq(str(jf(MP.class_, "names").get(p)[int(MD.NO_WARPS_SLOT)]), "No warps yet", "WARP its name")
        K.eq(len([x for x in slots if x is not None]), 1, "WARP nothing else is drawn")
    except Exception as e:
        K.check(False, "WARP fillWarps ran: %s" % e)
    # the warp tile picks open ? ICON_WARP : ICON_WARP_LOCKED (constants inlined by javassist -> ldc strings in fillWarps)
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    CP.appendClassPath(B.SERVER_JAR)
    CP.appendClassPath(jar)
    m = CP.get(PKG + "MenuPage").getDeclaredMethod("fillWarps")
    cpool = m.getMethodInfo().getConstPool()
    strs = set()
    for i in range(1, cpool.getSize()):
        try:
            if cpool.getTag(i) == 8:
                strs.add(str(cpool.getStringInfo(i)))
        except Exception:
            pass
    it = m.getMethodInfo().getCodeAttribute().iterator()
    ldcs = []
    while it.hasNext():
        pos = it.next()
        op = it.byteAt(pos)
        if op in (0x12, 0x13):
            idx = it.byteAt(pos + 1) if op == 0x12 else it.u16bitAt(pos + 1)
            if cpool.getTag(idx) == 8:
                ldcs.append(str(cpool.getStringInfo(idx)))
    for want in ("Skyy_Menu_Icon_Warp", "Skyy_Menu_Icon_WarpLocked", "Skyy_Menu_Icon_NoWarps"):
        K.check(want in ldcs, "WARP fillWarps loads %s" % want)
    K.check("Tool_Map" not in ldcs, "WARP fillWarps names no Tool_Map any more")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("icon", run_icon), ("warp", run_warp)], script=__file__)
