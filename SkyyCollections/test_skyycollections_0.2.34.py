"""Harness for SkyyCollections 0.2.34 (round E1: the Enchanted recipes also in the inventory crafting + the reverse recipe 1 -> 100;
tools/collections_0_2_34_patch.py + tools/skyyench.py e1). Build first:
    python tools/collections_0_2_34_patch.py && python SkyyCollections/build_skyycollections_0.2.34.py
      (SkyyGear/SkyyGear-0.3.29.jar gone? set SKYY_GEAR_0329_JAR to a copy extracted from backups/archive/old-jars-20261022.tar.xz)
    python SkyyCollections/test_skyycollections_0.2.34.py [--jar <SkyyCollections-0.2.34.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  S    static   the patch re-runs to identical bytes; line endings kept; no new class / command / system; tools/skyyench.py WITHOUT e1
                rebuilds the 0.2.33 Enchanted item JSONs + lang byte-for-byte (an older pin's rebuild is unchanged) and check_assets(e1=False)
                still refuses a reverse recipe
  J    jar      every non-class entry vs 0.2.33: only the 113 Enchanted item JSONs (+ the inventory bench, nothing else), the lang (the
                113 descriptions only), the new category + 115 recipe files, manifest.json; every reverse recipe = 1 Enchanted -> 100 of
                exactly its forward recipe's input (a resource row: its look item), OPEN (no unlock: spec 4.2); the vanilla pair
                both ways at 100 = the vanilla Farmer's Workbench ratio, open; no class of the jar names a craft event (crafting is no credit)
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.33 -> 0.2.34 (EXPECT below; non-class entries per J)
  KN   EXECUTED CollEnch.wantSig / next on the jar's real tables: the managed known-recipe set holds NO base item id (the reverse
       recipes are open, nothing is managed for them); the Copper / Bronze Enchanted unlock wants only its own forward id; ench.on off =
       the Enchanted part off, the armor entry untouched; next() adds / removes exactly the managed ids and keeps a foreign known id and a
       base item id (Ingredient_Bar_Iron); a second next() on the result = null (stable)
  TAB  EXECUTED EnchRank + EnchTab.sort on real engine BenchRecipeRegistry objects (Workbench + Fieldcraft): both Compressing tabs end
       up as TreeSets in forward-then-reverse order; a foreign recipe id sorts after ours
  LIVE every setup migration + CollReg.loadAll on a scratch COPY of the live Skyy_SkyyCollections (NewBetaTest), twice: the second start
       changes no file (0.2.34 adds no migration)
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD_VERSION = "0.2.34", "0.2.33"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
GEN = os.path.join(HERE, "build_skyycollections_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyycollections_%s.py" % OLD_VERSION)
PATCH = os.path.join(ROOT, "tools", "collections_0_2_34_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ench1", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
# CollTier: the committed tools/tier_tags.py gained rows after 0.2.33 was built (a92da209 fish rows, d8c0b0cc Pets dragon eggs) - the
# sort-only tier table every jar copies, not this round
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "CollTier": ["~<clinit>"],
          "EnchRank": ["~<clinit>"], "EnchTab": ["+f FBENCH", "+f FCAT", "~m sort", "+m sortIn"], "SkyyCollectionsPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
import skyyench as EN


def tmod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    old = sys.argv
    sys.argv = [old[0]]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = old
    return m


T31 = None


def t31():
    global T31
    if T31 is None:
        T31 = tmod(os.path.join(HERE, "test_skyycollections_0.2.31.py"), "tco0231")
    return T31


def live_table():
    """the table the build ships: TABLE + TABLE_ALLOYS (the build appends them to the module lists)"""
    return list(EN.TABLE) + list(EN.TABLE_ALLOYS)


# --------------------------------------------------------------------------------------------------------- C (non-class entries per J)
_KIT_COMPARE = HK.run_compare


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """harness_kit's compare, but the non-class entries are checked by phase J (this round changes assets on purpose): the kit's last
    check (only manifest.json changed) is replaced by J's exact list"""
    real = zipfile.ZipFile

    class _Z(object):
        def __init__(self, p):
            self.z = real(p)
            self.new = os.path.abspath(p) == os.path.abspath(jar)

        def namelist(self):
            return [n for n in self.z.namelist() if n.endswith(".class") or n == "manifest.json"]

        def read(self, n):
            return self.z.read(n)
    HK.zipfile.ZipFile = _Z
    try:
        _KIT_COMPARE(out, jar, old_jar, pkg, expect, added, removed)
    finally:
        HK.zipfile.ZipFile = real


HK.run_compare = _compare


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.count('VERSION = "0.2.34"') == 1 and '[SkyyCollections] 0.2.34 ready (' in g and '[SkyyCollections] 0.2.33 ready' not in g, "S version + ready line")
    for w in ("registerSystem(", "registerCommand(", ' = K("'):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    # skyyench without e1 = what 0.2.33 shipped (the 107 table rows; the build adds the alloys the same way both times)
    import skyyart as SA
    with SA.assets() as z:
        files, lang = EN.build_assets(z, SA)
        oz = zipfile.ZipFile(OLD_JAR)
        bad = [p_ for p_, t in files.items() if p_.startswith("Server/Item/Items/") and oz.read(p_) != (t.encode("utf-8") if isinstance(t, str) else t)]
        K.check(not bad and len([p_ for p_ in files if p_.startswith("Server/Item/Items/")]) == 107, "S skyyench e1=False rebuilds the 107 0.2.33 item JSONs byte-for-byte (%s)" % bad[:3])
        ol = oz.read("Server/Languages/en-US/server.lang").decode("utf-8").split("\n")
        nm = [l for l in lang if ".name=" in l]
        K.check(all(l in ol for l in nm), "S the Enchanted names unchanged")
        ds = [l for l in lang if ".description=" in l]
        K.check(all(any(x.endswith(l.split("=", 1)[1]) and x.startswith(l.split("=", 1)[0]) for x in ol) for l in ds),
                "S the e1=False descriptions = 0.2.33's (behind their tier tag)")
        K.check("e1" not in EN.emit_tab.__code__.co_varnames[:0] and EN.check_assets(files, z).startswith("107 Enchanted items"), "S check_assets(e1=False) passes the old file set")
        bad2 = dict(files)
        bad2[EN.REV_DIR + EN.REV_PREFIX + "Copper.json"] = EN.e1_files(z)[EN.REV_DIR + EN.REV_PREFIX + "Copper.json"]
        try:
            EN.check_assets(bad2, z)
            K.check(False, "S check_assets(e1=False) refuses a reverse recipe")
        except AssertionError:
            K.check(True, "S check_assets(e1=False) refuses a reverse recipe")
    K.save()


def run_jar(out, jar, scratch, home):
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    tab = live_table()
    rows = EN.reverse_rows(tab)
    want_new = set([EN.FIELD_CAT_PATH] + [EN.REV_DIR + r[0] + ".json" for r in rows])
    K.eq(sorted(eb - ea), sorted(want_new), "J new entries = the category + every reverse / pocket recipe")
    K.eq(sorted(ea - eb), [], "J no entry removed")
    ch = sorted(n for n in ea & eb if za.read(n) != zb.read(n))
    items = ["Server/Item/Items/SkyyCollections/%s%s.json" % (EN.PREFIX, t[0]) for t in tab]
    K.eq(sorted(ch), sorted(items + ["Server/Languages/en-US/server.lang", "manifest.json"]), "J changed entries = the 113 Enchanted items + lang + manifest")
    for p in items:
        a, b = json.loads(za.read(p)), json.loads(zb.read(p))
        rb = b["Recipe"].pop("BenchRequirement")
        ra = a["Recipe"].pop("BenchRequirement")
        a["Recipe"].pop("TimeSeconds", None)   # smoke 2026-10-27: Fieldcraft recipes may carry no delay
        if a != b or "TimeSeconds" in b["Recipe"] or ra != rb[:1] or rb[1:] != [{"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["SkyyCompressing"]}]:
            K.check(False, "J %s: only the inventory bench was added" % p)
            break
    else:
        K.check(True, "J the 113 item JSONs: only the inventory crafting bench added (same input, ratio, KnowledgeRequired, id)")
    la = za.read("Server/Languages/en-US/server.lang").decode("utf-8").split("\n")
    lb = zb.read("Server/Languages/en-US/server.lang").decode("utf-8").split("\n")
    dl = sorted(set(la) ^ set(lb))
    keys = set(l.split("=", 1)[0] for l in dl)
    K.check(len(la) == len(lb) and keys == set("%sitems.%s%s.description" % (pre, EN.PREFIX, t[0]) for t in tab for pre in ("", "server.")),
            "J lang: exactly the 226 Enchanted description lines changed (%d keys)" % len(keys))
    K.check(all("Craft it back into 100:" in l and "inventory (Compressing tab)" in l and "/craft" in l for l in lb if l.split("=", 1)[0] in keys),
            "J every new description names the inventory tab, /craft and the way back (fix: /craft kept)")
    # ench1fix2: Style Guide 15 - sectioned lines (lang line breaks) + colour spans; the unlock on the forward line, the way back open
    _nd = [l.split("=", 1)[1] for l in lb if l.split("=", 1)[0] in keys]
    K.check(all(d.count("\\n") == 5 and d.count("<color ") == d.count("</color>") == 6 and '<color is="#e8c25a">once unlocked in /collections</color>' in d
                and '<color is="#7ee08a">anyone, no unlock needed</color>' in d and d.endswith('<color is="#7f93a6">Crafting adds nothing to your collections.</color>')
                and all(ord(c) < 127 for c in d) for d in _nd) and len(_nd) == 226,
            "J every new description: 6 lines, colour coded (unlock gold, way back green, minor info dim), ASCII (ench1fix2)")
    K.check(all(d.split("\\n")[0].endswith(" pressed into one. Spent on tool and gear upgrades.") for d in _nd), "J the first line = what it is (behind the tier tag)")
    tags = dict((l.split("=", 1)[0], re.match(r"^(T\d+ [^-]+?) - ", l.split("=", 1)[1]).group(1)) for l in la
                if l.split("=", 1)[0] in keys and re.match(r"^T\d+ [^-]+? - ", l.split("=", 1)[1]))
    K.check(all(any(x.startswith(k + "=" + v + " - ") for x in lb) for k, v in tags.items()), "J tier tags kept first (%d tagged)" % len(tags))
    # the reverse recipes
    its = dict((EN.PREFIX + t[0], json.loads(zb.read("Server/Item/Items/SkyyCollections/%s%s.json" % (EN.PREFIX, t[0])))) for t in tab)
    n_k = n_open = 0
    bad = []
    for t in tab:
        d = json.loads(zb.read(EN.REV_DIR + EN.REV_PREFIX + t[0] + ".json"))
        f = its[EN.PREFIX + t[0]]["Recipe"]
        fi = f["Input"][0]
        base = fi.get("ItemId") or t[7][1]
        ok = (d["Input"] == [{"ItemId": EN.PREFIX + t[0], "Quantity": 1}] and d["Output"] == [{"ItemId": base, "Quantity": 100}]
              and d["PrimaryOutput"] == {"ItemId": base, "Quantity": 100} and fi["Quantity"] == 100 and d["KnowledgeRequired"] is False
              and f["KnowledgeRequired"] is True and d["BenchRequirement"] == f["BenchRequirement"])
        if fi.get("ResourceTypeId"):
            ok = ok and base in ("Rubble_Stone", "Soil_Sand", "Ingredient_Crystal_Blue")
        if not ok:
            bad.append(t[0])
        n_k += 1
    K.check(not bad, "J %d reverse recipes = 1 Enchanted -> 100 of the forward's input, OPEN (no unlock), both tabs: bad %s" % (n_k, bad[:5]))
    import skyyart as SA
    with SA.assets() as z:
        v = json.loads(z.read([n for n in z.namelist() if n.endswith("/Ingredient_Life_Essence_Concentrated.json")][0]).decode("utf-8-sig"))["Recipe"]
    pk = json.loads(zb.read(EN.REV_DIR + "SkyyCollections_Pack_LifeEssence.json"))
    up = json.loads(zb.read(EN.REV_DIR + "SkyyCollections_Unpack_LifeEssence.json"))
    K.check(v["Input"] == [{"ItemId": "Ingredient_Life_Essence", "Quantity": 100}] and pk["Input"] == v["Input"] and
            pk["Output"] == [{"ItemId": "Ingredient_Life_Essence_Concentrated", "Quantity": 1}] and
            up["Input"] == [{"ItemId": "Ingredient_Life_Essence_Concentrated", "Quantity": 1}] and up["Output"] == [{"ItemId": "Ingredient_Life_Essence", "Quantity": 100}]
            and pk["KnowledgeRequired"] is False and up["KnowledgeRequired"] is False, "J the vanilla pair: 100 Essence <-> 1 Greater Essence both ways (= the vanilla ratio), open")
    cat = json.loads(zb.read(EN.FIELD_CAT_PATH))
    K.check(cat == {"Name": "server.benchCategories.workbench.skyycompressing", "Icon": "Icons/CraftingCategories/SkyyCollections/Compressing.png", "Order": 1}
            and "Common/Icons/CraftingCategories/SkyyCollections/Compressing.png" in eb and "benchCategories.workbench.skyycompressing=Compressing" in lb,
            "J the inventory crafting category: name key (lang 'Compressing'), our icon in the jar, after Tools")
    hits = [n for n in zb.namelist() if n.endswith(".class") and any(w in zb.read(n) for w in (b"CraftRecipeEvent", b"PlayerCraftEvent"))]
    K.check(not hits, "J no class names a craft event - crafting (both ways) is never a collection credit: %s" % hits[:3])
    K.save()


def run_kn(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    E = JClass(PKG + "CollEnch")
    MID, MRID, ID = [str(x) for x in E.MID], [str(x) for x in E.MRID], [str(x) for x in E.ID]
    tab = live_table()
    bases = set(EN.rev_out(t) for t in tab) | set(["Ingredient_Life_Essence", "Ingredient_Life_Essence_Concentrated"])
    K.check(len(MID) == len(MRID) and not (set(MID) & bases), "KN fix: no base item id in the managed known-recipe set (the way back is open): %s" % sorted(set(MID) & bases)[:4])
    K.check(len(set(MID)) == len(MID), "KN every managed known id once")
    K.check(not [f for f in E.class_.getDeclaredFields() if str(f.getName()) == "REV0"], "KN fix: no REV0 block in CollEnch")
    HS = JClass("java.util.HashSet")

    def want(ids, on=True):
        s = HS()
        for i in ids:
            s.add(i)
        E.ON = on
        try:
            return str(E.wantSig(s))
        finally:
            E.ON = True
    cop = "Skyy_Ench_Copper" + EN.RECIPE_SUFFIX
    w = want([cop])
    ones = [MID[k] for k in range(len(MID)) if w[k] == "1"]
    K.eq(sorted(ones), ["Skyy_Ench_Copper"], "KN the Copper Enchanted unlock wants only its forward recipe")
    K.check(set(want([])) == set("0"), "KN nothing unlocked: nothing wanted")
    arm = MRID[len(ID)]          # the first armor piece
    w2 = want([cop, arm], on=False)
    K.check(w2[MRID.index(cop)] == "0" and w2[len(ID)] == "1", "KN ench.on off: the forward locked, the armor entry still follows its unlock")
    bro = "Skyy_Ench_Bronze" + EN.RECIPE_SUFFIX
    w3 = want([bro])
    K.eq(sorted(MID[k] for k in range(len(MID)) if w3[k] == "1"), ["Skyy_Ench_Bronze"], "KN the Bronze alloy unlock wants only its forward recipe")
    known = HS()
    for i in ("Foo_Foreign_Recipe", "Ingredient_Bar_Iron", "Skyy_Ench_Iron"):
        known.add(i)
    ns = E.next(known, JClass("java.lang.String")(w))
    got = sorted(str(x) for x in ns)
    K.eq(got, sorted(["Foo_Foreign_Recipe", "Ingredient_Bar_Iron", "Skyy_Ench_Copper"]), "KN next(): + Copper forward, - Iron forward (not unlocked), the foreign id and a base item id kept")
    K.check(E.next(ns, JClass("java.lang.String")(w)) is None, "KN next() on its own result = null (nothing to send again)")
    K.check(E.next(known, JClass("java.lang.String")(w[:-1])) is None, "KN a want of the wrong length is ignored")
    K.save()


def run_tab(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    T = JClass(PKG + "EnchTab")
    Rk = JClass(PKG + "EnchRank")
    K.eq([str(x) for x in Rk.ORDER], EN.tab_order(live_table()), "TAB EnchRank.ORDER = tools/skyyench.py tab_order (forward, reverse, ... the vanilla pair)")
    BRR = JClass("com.hypixel.hytale.builtin.crafting.BenchRecipeRegistry")
    CRP = JClass("com.hypixel.hytale.builtin.crafting.CraftingPlugin")
    f = CRP.class_.getDeclaredField("registries")
    f.setAccessible(True)
    regs = f.get(None)
    if regs is None:
        regs = JClass("java.util.HashMap")()
        f.set(None, regs)
    cm = BRR.class_.getDeclaredField("categoryMap")
    cm.setAccessible(True)
    ids = ["Foreign_Recipe", EN.REV_PREFIX + "Copper", "Skyy_Ench_Iron" + EN.RECIPE_SUFFIX, EN.REV_PREFIX + "Iron", "Skyy_Ench_Copper" + EN.RECIPE_SUFFIX,
           EN.REV_PREFIX + "LifeEssence", EN.PACK_PREFIX + "LifeEssence"]
    made = {}
    for bench, cat in (("Workbench", "Workbench_SkyyCompressing"), ("Fieldcraft", "SkyyCompressing")):
        r = BRR(bench)
        m = cm.get(r)
        hs = JClass("java.util.HashSet")()
        for i in ids:
            hs.add(i)
        m.put(cat, hs)
        regs.put(bench, r)
        made[bench] = (m, cat)
    s = str(T.sort())
    want = [i for i in EN.tab_order(live_table()) if i in ids] + ["Foreign_Recipe"]
    for bench, (m, cat) in made.items():
        cur = m.get(cat)
        K.check(cur is not None and "TreeSet" in str(cur.getClass().getName()) and [str(x) for x in cur] == want,
                "TAB %s tab sorted: %s" % (bench, [str(x) for x in cur] if cur is not None else None))
    K.check(s.count("table order, 7 recipes") == 2 and "inventory crafting" in s, "TAB sort() reports both tabs: %s" % s)
    K.check(str(T.sort()) == s, "TAB a second sort keeps them (already ordered)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Reg = t31().boot(home)
    P = JClass("java.nio.file.Paths").get(home)
    s0 = t31().snapd(home)
    MIGS = ("CollBagMigrate", "CollBypassMig", "CollCoinMig", "CollEnch28Mig", "CollP6Mig", "CollP6EnchMig", "CollP7Mig")
    msgs = [str(JClass(PKG + cn).run(P)) for cn in MIGS]
    Reg.loadAll()
    s1 = t31().snapd(home)
    K.notes.append("LIVE start 1 changed %s" % sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k))[:8])
    for cn in MIGS:
        JClass(PKG + cn).run(P)
    Reg.loadAll()
    s2 = t31().snapd(home)
    K.check(s1 == s2, "LIVE start 2 changes no file: %s" % sorted(k for k in set(s1) | set(s2) if s1.get(k) != s2.get(k))[:6])
    R = Reg.D
    K.check(R is not None and len(list(R.id)) >= 100, "LIVE the live registry loads (%d collections)" % (len(list(R.id)) if R is not None else 0))
    E = JClass(PKG + "CollEnch")
    K.check(len(E.MID) == len(E.MRID) and "Ingredient_Bar_Copper" not in [str(x) for x in E.MID], "LIVE the managed known-recipe table = 0.2.33's shape (no reverse block)")
    K.save()


def run_jarphase(out, jar, scratch, home):
    run_jar(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyCollections", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("jar", run_jar), ("kn", run_kn), ("tab", run_tab), ("live", run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyCollections"))
