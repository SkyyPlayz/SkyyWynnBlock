"""Harness for SkyyCollections 0.2.25 (round ores01: the Lead / Chromium / Slag / Titanium ore collections + the Charcoal collection, the
coll:fn:add source sacks:furnace, five Enchanted items (tools/skyyench.py TABLE_ORES), their tier rewards; tools/collections_0_2_25_patch.py).
Build first:
    python tools/collections_0_2_25_patch.py && python SkyyCollections/build_skyycollections_0.2.25.py

    python SkyyCollections/test_skyycollections_0.2.25.py [--jar <SkyyCollections-0.2.25.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.24 -> 0.2.25: exactly the listed members differ; non-class entries: manifest.json, server.lang and the five new Enchanted
                items' JSON / icon / texture - every other file byte-identical
  J    jar      107 Enchanted items (+ the retired one, still without a recipe); the five new ones: 100 ingots / Charcoal -> 1, KnowledgeRequired,
                their own (tinted) art; names; the ready line names 0.2.25
  X    exec     the default registry (each zone metal right after its partner, Charcoal at the end of Mining, curves R / R / E / E / S, Charcoal
                tier VII = 5,000); coll:fn:tier answers the Charcoal tier (0 .. 7 .. 9) from a counts file; ADD_SOURCES has sacks:furnace by
                default, bridge.add.furnace=false drops it; the Enchanted alias (100 x the raw ore / Charcoal); the default rewards of the five
                (grammar + sizing); the Enchanted unlock tiers (III / II); mergeNew on the LIVE collections.properties text (read only) and on
                hand-edited texts (an own hidden line kept, an item used elsewhere = not added, partner missing = after the category)
  T    migr     CollRw25Mig on the 0.2.24 default (from the 0.2.24 jar), on the LIVE rewards.properties text (read only) after the older
                updates, CRLF, no final newline, a line an admin wrote kept, a 2nd run = nothing, the fresh 0.2.25 default = nothing
  D    live     the setup order on a scratch COPY of the live Skyy_SkyyCollections, started twice: CollRw25Mig once (History copy, 34 Undo
                rows, migration-ores25.log), collections.properties untouched, the 2nd start changes nothing
  DP   live     every live profile's collection pages build (the 0.2.24 live page phase, with CollRw25Mig in the setup order)
  M    pages    the 0.2.23 page phase on this jar (assert_menu_page on every view)
  AA   audit    the engine-access audit
Scratch: tools/dev/scratch/ores-b4/coll (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN

VERSION = "0.2.25"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.24.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "ores-b4", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
LANG = "Server/Languages/en-US/server.lang"
RET = "Skyy_Ench_LifeEssence"
NEW = ["Lead", "Chromium", "Slag", "Titanium", "Charcoal"]
AFTER = {"Lead": "Thorium", "Chromium": "Cobalt", "Slag": "Adamantite", "Titanium": "Mithril", "Charcoal": "Gemstone"}
CURVE = {"Lead": "R", "Chromium": "R", "Slag": "E", "Titanium": "E", "Charcoal": "S"}
FIRST = {"Lead": "Ore_Lead_SkyWynn", "Chromium": "Ore_Chromium_SkyWynn", "Slag": "Ore_Slag_SkyWynn", "Titanium": "Ore_Titanium_SkyWynn",
         "Charcoal": "Ingredient_Charcoal"}
NEW_IDS = [EN.PREFIX + k for k in NEW]
EXPECT = {}
ADDED = ["CollRw25Mig"]

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            exp = sorted(["manifest.json", LANG] + ["Server/Item/Items/SkyyCollections/%s.json" % i for i in NEW_IDS]
                         + ["Common/Icons/ItemsGenerated/SkyyCollections_Ench_%s.png" % k for k in NEW]
                         + ["Common/Items/SkyyCollections/Ench/%s.png" % k for k in NEW])
            return self.check(sorted(got) == exp, "C: non-class entries changed = manifest.json + server.lang + the five new Enchanted items' JSON / icon / texture (extra %s, missing %s)" % (
                sorted(set(got) - set(exp))[:5], sorted(set(exp) - set(got))[:5]))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def T21():
    return _mod("t21", os.path.join(HERE, "test_skyycollections_0.2.21.py"))


def T23():
    return _mod("t23", os.path.join(HERE, "test_skyycollections_0.2.23.py"))


def T24():
    return _mod("t24", os.path.join(HERE, "test_skyycollections_0.2.24.py"))


def P(n):
    from jpype import JClass
    return JClass(PKG + n)


CURVES = {"B": [50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000], "S": [50, 100, 250, 500, 1000, 2500, 5000, 10000, 20000],
          "R": [25, 50, 100, 250, 500, 1000, 2500, 5000], "E": [10, 25, 50, 100, 250, 500, 1000]}


def want_rewards(cid):
    """the 0.2.25 grammar in Python: tier -> (item, n) for every tier but the Enchanted one"""
    a = CURVES[CURVE[cid]]
    e = EN.row(cid)[4]
    out = {}
    for t in range(1, len(a) + 1):
        if t == e:
            continue
        st = a[t - 1] - (a[t - 2] if t > 1 else 0)
        n = EN.gift_size(st, min(64, 2 * t))
        out[t] = (EN.PREFIX + cid, n) if n > 0 else (FIRST[cid], EN.base_gift_size(st))
    return out


# ------------------------------------------------------------------------------------------------------------------- J: the jar
def run_jar(out, jar, scratch, _home):
    K = HK.Child(out)
    z, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    its = dict((n.rsplit("/", 1)[1][:-5], json.loads(z.read(n))) for n in z.namelist() if n.startswith("Server/Item/Items/SkyyCollections/"))
    K.eq(sorted(its), sorted(EN.IDS + [RET]), "J the Enchanted item JSONs = the live 107 + the retired one")
    K.check(len(EN.IDS) == 107 and EN.IDS[-5:] == NEW_IDS, "J skyyench: 107 rows, the five ores01 rows last")
    K.check("Recipe" not in its[RET] and z.read("Server/Item/Items/SkyyCollections/%s.json" % RET) == zo.read("Server/Item/Items/SkyyCollections/%s.json" % RET),
            "J the retired item: unchanged from 0.2.24 (no recipe)")
    want_in = {"Lead": "Ingredient_Bar_Lead_SkyWynn", "Chromium": "Ingredient_Bar_Chromium_SkyWynn", "Slag": "Ingredient_Bar_Slag_SkyWynn",
               "Titanium": "Ingredient_Bar_Titanium_SkyWynn", "Charcoal": "Ingredient_Charcoal"}
    for k in NEW:
        r = its[EN.PREFIX + k].get("Recipe") or {}
        K.check(r.get("Input") == [{"ItemId": want_in[k], "Quantity": 100}] and r.get("KnowledgeRequired") is True and r.get("OutputQuantity") == 1
                and r.get("BenchRequirement") == [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_SkyyCompressing"]}],
                "J Enchanted %s: 100 %s -> 1 at the Workbench Compressing tab, KnowledgeRequired" % (k, want_in[k]))
    # own art: the four tinted ingots differ from each other and from the Enchanted Iron ingot; Charcoal = the vanilla charcoal block model
    ic = dict((k, z.read("Common/Icons/ItemsGenerated/SkyyCollections_Ench_%s.png" % k)) for k in NEW + ["Iron"])
    K.check(len(set(ic.values())) == 6, "J the five new icons are their own (tinted ingots differ from Enchanted Iron and each other)")
    K.check(its["Skyy_Ench_Charcoal"]["Model"] == "Blocks/Stone/Rubble_Charcoal.blockymodel" and its["Skyy_Ench_Lead"]["Model"] == its["Skyy_Ench_Iron"]["Model"],
            "J Enchanted Charcoal = the charcoal model, the ingots = the ingot model")
    lang = dict(l.split("=", 1) for l in z.read(LANG).decode("utf-8").split("\n") if "=" in l)
    lo = dict(l.split("=", 1) for l in zo.read(LANG).decode("utf-8").split("\n") if "=" in l)
    ch = sorted(k for k in set(lang) | set(lo) if lang.get(k) != lo.get(k))
    K.check(all(any(i in k for i in NEW_IDS) for k in ch) and len(ch) == 20, "J lang: only the five new items' names + descriptions added (%d keys)" % len(ch))
    K.check(lang["server.items.Skyy_Ench_Lead.name"] == "Enchanted Lead Ingot" and lang["server.items.Skyy_Ench_Charcoal.name"] == "Enchanted Charcoal"
            and "100 Lead Ingots pressed into one" in lang["server.items.Skyy_Ench_Lead.description"],
            "J names + descriptions: %s / %s" % (lang["server.items.Skyy_Ench_Lead.name"], lang["server.items.Skyy_Ench_Lead.description"][:60]))
    plug = z.read("com/skyy/collections/SkyyCollectionsPlugin.class")
    K.check(re.search(rb"\[SkyyCollections\] 0\.2\.25 ready", plug) is not None and b"107 Enchanted materials" in plug, "J the ready line names 0.2.25 and 107 Enchanted materials")
    man = json.loads(z.read("manifest.json"))
    K.check(str(man.get("Version")) == VERSION and "107 Enchanted" in json.dumps(man) and "deploy with SkyyWorldGen 0.7.3+" in json.dumps(man)
            and "Zero dependencies" not in json.dumps(man), "J manifest: version 0.2.25, 107 Enchanted, names the SkyyWorldGen 0.7.3 soft need")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Store, Util, En, Fn = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollEnch"), P("CollFn")
    base = t21.fresh(scratch, "x")
    R = Reg.D
    ids = [str(R.id[c]) for c in range(R.n)]
    BY = dict((i, c) for c, i in enumerate(ids))
    K.eq([ids[ids.index(c) - 1] for c in NEW], [AFTER[c] for c in NEW], "X the default registry: each new collection right after its partner")
    K.check(all(str(Reg.CATS[R.cat[BY[c]]]) == "Mining" and not bool(R.hidden[BY[c]]) and [str(x) for x in R.items[BY[c]]] == [FIRST[c]] for c in NEW),
            "X the five: visible Mining collections of one item each (the raw ore / Ingredient_Charcoal)")
    K.eq([[int(Reg.threshold(R, BY[c], t)) for t in range(1, int(Reg.maxTier(R, BY[c])) + 1)] for c in NEW], [CURVES[CURVE[c]] for c in NEW],
         "X curves: Rare, Rare, Elite, Elite, Standard")
    K.eq(int(Reg.threshold(R, BY["Charcoal"], 7)), 5000, "X Charcoal tier VII = 5,000 (the Eternal Flame gate)")
    K.eq(int(Reg.MERGED), 0, "X a fresh file has the five lines (nothing merged)")
    # coll:fn:tier {UUID, "Charcoal"} from a counts file
    UUID = JClass("java.util.UUID")
    fn = Fn("tier")
    got = []
    for i, n in enumerate((0, 49, 50, 4999, 5000, 20000)):
        u = UUID.fromString("00000000-0000-0000-0000-0000000e25%02d" % i)
        t21.counts(base, str(Util.pkey(u)), [("Ingredient_Charcoal", n)] if n else [])
        Store.DATA.remove(str(Util.pkey(u)))
        r = fn.apply(JArray(JClass("java.lang.Object"))([u, JString("Charcoal")]))
        got.append(None if r is None else int(r))
    K.eq(got, [0, 0, 1, 6, 7, 9], "X coll:fn:tier {UUID, Charcoal}: 0 / 49 / 50 / 4,999 / 5,000 / 20,000 Charcoal -> tier 0 / 0 / 1 / 6 / 7 / 9")
    K.check(fn.apply(JArray(JClass("java.lang.Object"))([UUID.fromString("00000000-0000-0000-0000-0000000e2500"), JString("charcoal")])) is not None,
            "X coll:fn:tier takes the id in any case")
    # sacks:furnace
    K.check(bool(Reg.ADD_SOURCES.contains("sacks:furnace")) and bool(Reg.ADD_SOURCES.contains("skills:felled")) and bool(R.itemColl.containsKey("Ingredient_Charcoal")),
            "X coll:fn:add accepts sacks:furnace by default; Ingredient_Charcoal belongs to a collection")
    cfg = os.path.join(base, "config.properties")
    txt = open(cfg, encoding="latin-1").read()
    K.check("bridge.add.furnace=true" in txt and "bridge.add.sources=skills:double,skills:felled,shard\n" in txt, "X the fresh config.properties: bridge.add.furnace=true, the sources list unchanged")
    open(cfg, "w", encoding="latin-1").write(txt.replace("bridge.add.furnace=true", "bridge.add.furnace=false"))
    note_off = str(Reg.loadConfig())
    off = bool(Reg.ADD_SOURCES.contains("sacks:furnace"))
    open(cfg, "w", encoding="latin-1").write(txt.replace("bridge.add.furnace=true\n", "").replace("bridge.add.sources=skills:double,skills:felled,shard", "bridge.add.sources=skills:double"))
    Reg.loadConfig()
    old_file = bool(Reg.ADD_SOURCES.contains("sacks:furnace"))
    open(cfg, "w", encoding="latin-1").write(txt)
    Reg.loadConfig()
    K.check(not off and "furnace=false" in note_off and old_file, "X bridge.add.furnace=false drops sacks:furnace; an older file (no line, sources without it) still accepts it")
    # the Enchanted alias: 100 x the collection's first item
    al = [(str(a[0]), int(a[1])) for a in (En.alias(i, JLong(2)) for i in NEW_IDS)]
    K.eq(al, [(FIRST[c], 200) for c in NEW], "X the Enchanted alias: 2 Enchanted = 200 raw ore / Charcoal to the collection")
    # the default rewards of the five
    bad = []
    for c in NEW:
        w = want_rewards(c)
        for t in range(1, len(CURVES[CURVE[c]]) + 1):
            it = Reg.itemAt(R, BY[c], t)
            toks = [str(x) for x in (Reg.REWARDS.get(c.lower() + "." + str(t)) or [])]
            g = None if it is None else (str(it[0]), int(it[1]))
            if g != w.get(t) or len(toks) != (1 if t in w else 0):
                bad.append((c, t, g, w.get(t), toks))
    K.check(not bad, "X the five collections' tier rewards = the grammar (own Enchanted gift <= 10%% of the step, else the base item; none at the Enchanted tier): %s" % bad[:3])
    # the Enchanted unlock tiers
    keys = [str(x) for x in En.KEY]
    K.eq([int(En.TIER[keys.index(k)]) for k in NEW], [3, 3, 2, 2, 3], "X Enchanted recipe tiers: Lead III, Chromium III, Slag II, Titanium II, Charcoal III")
    # mergeNew on the LIVE collections.properties text (read only) and on hand-edited texts
    live = open(os.path.join(LIVE_DIR, "collections.properties"), "rb").read().decode("latin-1")
    L = JClass("java.util.ArrayList")

    def parse(t_):
        lst = L()
        for l_ in t_.split("\n"):
            lst.add(l_.rstrip("\r"))
        r_ = Reg.parseReg(lst)
        return r_, [str(r_.id[i]) for i in range(r_.n)], int(Reg.MERGED)
    lr, lids, lm = parse(live)
    had = [c for c in NEW if ("coll.%s=" % c) in live]
    K.check(lm == 5 - len(had) and all(lids[lids.index(c) - 1] == AFTER[c] for c in NEW) and lr.n == R.n,
            "X the LIVE collections.properties: %d merged at load, each after its partner (%d collections = the default %d)" % (lm, lr.n, R.n))
    K.check(all(str(lr.from_[lids.index(c)]) == str(R.from_[BY[c]]) and int(lr.curve[lids.index(c)]) == int(R.curve[BY[c]]) for c in NEW)
            if hasattr(lr, "from_") else True, "X merged lines = the default lines")
    hid = live.replace("coll.Mithril=", "coll.Lead=Mining|R|Lead Ore|Ore_Lead_SkyWynn|Ore_Lead_SkyWynn|hidden|mine\ncoll.Mithril=", 1)
    hr, hids, hm = parse(hid)
    K.check(hm == 4 and bool(hr.hidden[hids.index("Lead")]) and hids.index("Lead") < hids.index("Mithril"), "X an admin's own (hidden) Lead line wins: kept where it is, 4 merged")
    use = live.replace("|Ore_Mithril||", "|Ore_Mithril,Ingredient_Charcoal||", 1)
    ur, uids, um = parse(use)
    K.check(um == 4 and "Charcoal" not in uids, "X Ingredient_Charcoal already in another collection: no Charcoal collection merged (%d merged, Charcoal %s, Mithril items %s)" % (
        um, "Charcoal" in uids, [str(x) for x in ur.items[uids.index("Mithril")]]))
    parse(use)
    K.check(bool(Reg.SKIPWARN.contains("Charcoal")) and not bool(Reg.SKIPWARN.contains("Lead")) and int(Reg.SKIPWARN.size()) == 1,
            "X the item-in-use skip WARNs once (Charcoal listed once after two parses); an own line (Lead) is no warning")
    nop = "\n".join(l_ for l_ in live.split("\n") if not l_.startswith(("coll.Thorium=", "coll.Gemstone=")))
    nr, nids, nm = parse(nop)
    mining = [i for i in nids if str(Reg.CATS[nr.cat[nids.index(i)]]) == "Mining"]
    K.check(nm == 5 and nids.index("Lead") == nids.index(mining[-2]) and mining[-1] == "Charcoal", "X partner lines gone: Lead / Charcoal after the last Mining line")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- T: migr
def run_migr(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Cob, Rw, R24, R21, Tm = P("CollReg"), P("CollCobMig"), P("CollRw25Mig"), P("CollRw24Mig"), P("CollRw21Mig"), P("CollToolMig")
    t21.fresh(scratch, "t")
    U_ = JClass("java.net.URL")
    srv = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
    L = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(OLD_JAR).toURI().toURL()]), srv)
    OLDDEF = str(JClass(PKG + "CollReg", loader=L).rewardsText())          # the 0.2.24 default
    DEF = str(Reg.rewardsText())

    def table(t_):
        return dict((str(k), [str(x) for x in v]) for k, v in Cob.table(JArray(JString)([l_.rstrip("\r") for l_ in t_.split("\n")])).items())

    def upd(t_):
        r_ = Rw.update(t_)
        return None if r_ is None else (str(r_[0]), [str(x) for x in r_[1]], str(r_[2]), int(r_[3]), int(r_[4]), bool(r_[5]), int(r_[6]))
    nk = len(Rw.K)
    K.eq(nk, 34, "T CollRw25Mig: 34 new tier entries (Lead 7, Chromium 7, Slag 6, Titanium 6, Charcoal 8)")
    K.check(all(str(x) == "" for x in Rw.OLDV) and all(str(k).split(".")[0] in NEW for k in Rw.K), "T every entry is new (no old value) and belongs to one of the five")
    K.check(Rw.update(DEF) is None and R24.update(DEF) is None and R21.update(DEF) is None and Tm.update(DEF) is None, "T a fresh 0.2.25 rewards.properties: every update = nothing (markers)")
    u0 = upd(OLDDEF)
    K.check(u0 is not None and u0[5] and u0[3] == nk and u0[4] == 0 and table(u0[0]) == table(DEF) and upd(u0[0]) is None,
            "T the 0.2.24 default -> the loader reads exactly the 0.2.25 default (%d entries added); a 2nd run = nothing" % nk)
    tab0, tabn = table(OLDDEF), table(u0[0])
    K.check(all(tab0[k] == tabn[k] for k in tab0) and sorted(set(tabn) - set(tab0)) == sorted(str(k).lower() for k in Rw.K),
            "T nothing else changed: every old entry the same, only the 34 new keys added")
    K.check(OLDDEF in u0[0] or u0[0].startswith(OLDDEF.split("# coll24")[0]), "T the old text kept byte for byte up to the marker")
    rows = u0[1]
    K.check(len(rows) == 3 * nk and all(rows[i + 1] == "(none)" for i in range(0, len(rows), 3)), "T one Undo row per added entry, old = (none)")
    # the LIVE text (read only): the older updates first, like setup
    live = open(os.path.join(LIVE_DIR, "rewards.properties"), "rb").read().decode("latin-1")
    t_ = live
    for M_ in (Tm, R21, R24):
        r_ = M_.update(t_)
        t_ = t_ if r_ is None else str(r_[0])
    u1 = upd(t_)
    K.check(u1 is not None and u1[5] and upd(u1[0]) is None, "T the LIVE file: %d entries added, %d kept; the loader reads the old table + those; a 2nd run = nothing" % (u1[3], u1[4]))
    mk = str(Rw.MARK5)
    K.check(u1[0].replace(mk + "\n", "", 1).replace(mk + "\r\n", "", 1).startswith(t_.rstrip("\r\n")) and u1[0].count(mk) == 1,
            "T the LIVE file: its text is kept (+ the marker line), the new section appended")
    crlf = t_.replace("\r\n", "\n").replace("\n", "\r\n")
    uc = upd(crlf)
    K.check(uc[5] and uc[0].count("\r\n") == uc[0].count("\n") and uc[3] == u1[3], "T CRLF kept on every line")
    une = upd(t_.rstrip("\n"))
    K.check(une[5] and not une[0].endswith("\n") and une[3] == u1[3], "T no final newline stays none")
    own = t_ + ("" if t_.endswith("\n") else "\n") + "Lead.1=coins:7\n"
    uo = upd(own)
    K.check(uo[5] and uo[3] == u1[3] - 1 and uo[4] == 1 and table(uo[0])["lead.1"] == ["coins:7"] and "kept hand-edited line" in uo[2],
            "T a Lead.1 line an admin already wrote: kept + logged, the other 33 added")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Reg, Store = P("CollReg"), P("CollStore")
    b_ = JClass("java.nio.file.Paths").get(home)
    h0 = HK.tree_hash(home)
    coll0 = open(os.path.join(home, "collections.properties"), "rb").read()
    msgs, hs, merged = [], [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        P("CollBagMigrate").run(b_)
        P("CollBypassMig").run(b_)
        P("CollCoinMig").run(b_)
        Reg.loadAll()
        merged.append(int(Reg.MERGED))
        for m in ("CollCobMig", "CollSigMig", "CollShardMig", "CollToolMig", "CollRw21Mig", "CollRw24Mig"):
            P(m).run(b_)
        msgs.append(str(P("CollRw25Mig").run(b_)))
        hs.append(HK.tree_hash(home))
    ch1 = sorted(k for k, v in hs[0].items() if h0.get(k) != v)
    K.check(msgs[0].startswith("tier rewards added for the new Lead") and msgs[1] == "" and hs[0] == hs[1],
            "D the 1st start adds the new rewards once (%s), the 2nd changes nothing" % msgs[0][:120])
    K.check("rewards.properties" in ch1 and "migration-ores25.log" in ch1 and all(c in ("rewards.properties", "migration-ores25.log", "config-changes.log") or c.startswith("config-history") for c in ch1),
            "D only rewards.properties, its history copy, config-changes.log and migration-ores25.log changed: %s" % ch1[:6])
    K.check(open(os.path.join(home, "collections.properties"), "rb").read() == coll0 and merged[0] == merged[1] and merged[0] >= 0,
            "D collections.properties untouched; %d collections merged at load (both starts)" % merged[0])
    R = Reg.D
    ids = [str(R.id[c]) for c in range(R.n)]
    K.check(all(c in ids for c in NEW) and all(Reg.REWARDS.get(c.lower() + ".1") is not None for c in NEW), "D the live registry + rewards hold the five")
    chg = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read()
    rows = [l_ for l_ in chg.split("\n") if "SkyyCollections 0.2.25" in l_]
    K.check(len(rows) == 34 and all("\trewards[" in l_ and "\t(none)\t" in l_ for l_ in rows), "D 34 Undo rows (rewards[<entry>], old (none))")
    hist = os.path.join(home, "config-history")
    K.check(os.path.isdir(hist) and any(open(os.path.join(hist, f), "rb").read() == open(os.path.join(LIVE_DIR, "rewards.properties"), "rb").read()
                                        for f in os.listdir(hist) if f.startswith("Skyy_SkyyCollections~rewards.properties")),
            "D config-history holds the old rewards.properties byte for byte")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- DP + M: pages
def run_livepages(out, jar, scratch, home):
    """the 0.2.24 live page phase as it is (its setup order ends at CollRw24Mig: the five merged collections build without reward lines too)"""
    T24().run_livepages(out, jar, scratch, home)


def run_pages(out, jar, scratch, home):
    """the 0.2.23 page phase as it is; its one version check (the ready line names 0.2.23) asks for 0.2.25 instead"""
    ck0 = HK.Child.check
    plug = zipfile.ZipFile(jar).read("com/skyy/collections/SkyyCollectionsPlugin.class")

    def ck(self, cond, what):
        if what == "PAGE the ready line names 0.2.23":
            return ck0(self, re.search(rb"\[SkyyCollections\] 0\.2\.25 ready", plug) is not None, "PAGE the ready line names 0.2.25")
        return ck0(self, cond, what)
    HK.Child.check = ck
    T23().run_pages(out, jar, scratch, home)


EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the kit's version texts + the bridge.add.furnace row
    "CollEnch": ["~<clinit>"],                                                # the 107-row Enchanted table
    "CollReg": ["+f MERGED", "+f NEW_AFTER", "+f NEW_CAT", "+f NEW_ID", "+f NEW_ITEMS", "+f NEW_VAL", "+f SKIPWARN", "+m mergeNew", "~<clinit>",
                "~m configText", "~m loadConfig", "~m parseReg", "~m regText", "~m rewardsText"],   # the five collections, sacks:furnace, defaults
    "CollTier": ["~<clinit>"],                                                # tier tags of the new Enchanted ingots
    "EnchRank": ["~<clinit>"],                                                # the Compressing tab order (107 rows)
    "SkyyCollectionsPlugin": ["~m setup"],                                    # CollRw25Mig + the ready line
}

if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("jar", run_jar), ("exec", run_exec), ("migr", run_migr), ("pages", run_pages),
            ("live", run_live), ("livepages", run_livepages)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
