"""Harness for SkyyGear 0.3.57 (round aug1: the augment salvage / sale confirm + socketed loot - tools/gear_0_3_57_patch.py header).
Build first (the build needs Quirk's private art; in a worktree: SKYWYNN_PRIVATE_ART=<path to SkyWynn-PRIVATE-art>):
    python tools/gear_0_3_57_patch.py && python SkyyGear/build_skyygear_0.3.57.py
    python SkyyGear/test_skyygear_0.3.57.py [--keep] [--expect-dump]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.56 jar is the compare base):
  S  static    the patch re-runs to identical bytes, ONE new class (GearAugCntFn), no command / system; gear:fn:augCount put + removed; re-identify
               calls keepAug; the bench tick asks tickCount
  A  verify    every class loads + initialises with -Xverify:all
  C  compare   0.3.56 -> 0.3.57 (EXPECT below)
  E  engine    the 0.2.11 harness's bare server boot (vanilla pack + THIS jar) - every new path EXECUTED:
               C  the fresh config: aug.loot.prefill=10; the loader (absent = 10, clamped 0..100)
               N  GearAug.count (document / item; empty + unreadable entries; no document), tickCount (gear ids only), gear:fn:augCount (ItemStack,
                  {id, BsonDocument}, {id, JSON String}, {id, null}, junk -> null)
               PF socketed loot: prefill on REAL documents (Legendary / Fabled / Mythic / Untiered yes; Normal .. Rare / Set no; crafted no; one there
                  already no; 0 % no; a missed roll counted), the tier = the zone of the level (T1..T5, a 5-tier kind capped), the kind always FITS
                  (300 random rolls on a bow / a sword / an armor piece: Tempo never on a bow, armor kinds on armor), GearUnid.pickZ (the bag open
                  n = 0 prefills, a re-identify n = 1 never), the tooltip shows the socketed augment
               S  gear:fn:salvage: "commit" of an augmented piece refused, "commitAug:<wrong>" / junk refused (stale), "commitAug:<n>" goes on to
                  GearSalv.commit, a piece without augments commits as before; PN[2] counted
               B  the Salvagebench: salvBlocked (augmented vanilla id yes, plain no, pack rules unchanged), GearBench.sweep moves an augmented
                  vanilla sword out of a bench input into the output with its document (AUGN reset), a plain one stays; salvVeto on a REAL
                  CraftingRecipe (bench Salvagebench) + a REAL Inventory: an augmented match refused with the augment text, a plain one / a
                  non-salvage recipe not
               R  keepAug: a re-identified item gets the old item's augments + paid slots (document + stack), nothing to carry = unchanged
  E56 / E55    the 0.3.56 and 0.3.55 harnesses' engine phases against THIS jar (every 0.3.5x check still passes)
  D  live      start twice on a scratch COPY of Skyy's live Skyy_SkyyGear: no one-time update of this round, the second start changes nothing,
               aug.loot.prefill not written (a new key) and read as 10
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): a real Salvagebench tick on a placed bench (sweep itself is executed); the full GearIdn.reroll with coins (keepAug is
executed directly); the client drawing the confirm / tooltip.
Scratch: tools/dev/scratch/aug1/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.57"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "aug1", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.56.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_57_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.56.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
T56 = {"__file__": os.path.join(HERE, "test_skyygear_0.3.56.py"), "__name__": "t56"}
_s = open(T56["__file__"], encoding="utf8").read()
exec(compile(_s[:_s.rindex(chr(10) + 'HK.run_compare = T54["run_compare54"]')], T56["__file__"], "exec"), T56)
T55 = T56["T55"]
T54 = T56["T54"]
for _t in (T54, T55, T56):
    _t["SCRATCH"] = SCRATCH
ADDED = ["GearAugCntFn"]
EXPECT = None if "--expect-dump" in sys.argv else {          # the first run's dump, reviewed: the new row (Cfg*, GearCfg), count / prefill / tickCount (GearAug), the bench (GearBench, GearBenchSys, GearPack),
    # keepAug (GearIdent), commitAug (GearSalvFn), the bag prefill (GearUnid.pickZ), gear:fn:augCount put / removed (the plugin)
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],
    'CfgRows2': ['~<clinit>'],
    'GearAug': ['+f FORCE', '+f PICK', '+f PN', '+f PRER', '+f ZT', '+m count', '+m prefill', '+m tickCount', '+m zoneOf', '~<clinit>'],
    'GearBench': ['+f AUGN', '~<clinit>', '~m sweep', '~m tell'],
    'GearBenchSys': ['~m tick'],
    'GearCfg': ['+f AUG_PREFILL', '~<clinit>', '~m apply', '~m defaultsText'],
    'GearIdent': ['+m keepAug', '~m reroll'],
    'GearPack': ['+m augWhy', '~m salvBlocked', '~m salvVeto'],
    'GearSalvFn': ['~m apply'],
    'GearUnid': ['~m pickZ'],
    'SkyyGearPlugin': ['~m setup', '~m shutdown'],
}
LIVE_DIR = T54["LIVE_DIR"]
U = "00000000-0000-0000-0000-000000000357"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.57 - build script') and g.count('VERSION = "0.3.57"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')), (0, 0, 1),
         "S one new class (GearAugCntFn), no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check('br.put("gear:fn:augCount", new @PKG@.GearAugCntFn());' in g and 'bq.remove("gear:fn:augCount");' in g, "S gear:fn:augCount put at start, removed at shutdown")
    K.check("got = keepAug(got, d, u);" in g and "@PKG@.GearAug.tickCount(s) > 0" in g and 'mode.startsWith("commitAug:")' in g
            and g.count("@PKG@.GearAug.prefill(") == 2, "S re-identify calls keepAug, the bench tick asks tickCount, gear:fn:salvage reads commitAug, pickZ prefills (2 branches)")
    e_ = g.index("@PKG@.GearBench.onBench(pb, chunk, idx, store);")
    tk = g[g.rindex("public void tick(", 0, e_):e_]
    K.check(tk.index("if (!@PKG@.GearBench.isSalv(@PKG@.GearBench.benchId(pb))) return;") < tk.index("@PKG@.GearAug.tickCount(s) > 0") and "if (!any) return;" in tk,
            "S FIXER L1: GearBenchSys.tick checks the bench id (Salvagebench) BEFORE any tickCount metadata read")
    K.save()


# ====================================================================================================== E: engine
def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JImplements, JOverride, JObject, JArray, JLong, JDouble, JBoolean, JFloat, JShort, JByte
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng57")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", jar, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    H.update({"JAR": jar, "SCRATCH": esc, "VERSION": VERSION})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    us = E["us"]
    P = lambda n: JClass(PKG + n)
    Cfg, Data, Roll, View, Defs, Pool, Aug, Unid, Pack, GB, Idn = (P("GearCfg"), P("GearData"), P("GearRoll"), P("GearView"), P("GearDefs"), P("GearPool"),
                                                                 P("GearAug"), P("GearUnid"), P("GearPack"), P("GearBench"), P("GearIdent"))
    Props = JClass("java.util.Properties")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    BA = JClass("org.bson.BsonArray")
    BS = JClass("org.bson.BsonString")
    BI = JClass("org.bson.BsonInt32")
    BD = JClass("org.bson.BsonDocument")
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    AL = JClass("java.util.ArrayList")
    SysJ = JClass("java.lang.System")
    OA = JArray(JObject)
    u = UUID.fromString(U)
    sysp = SysJ.getProperties()
    br = sysp.get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        sysp.put("skyy.bridge", br)
    data = os.path.join(scratch, "data57")
    os.makedirs(data, exist_ok=True)
    Cfg.DIR = Paths.get(data)
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    BASE = {"part__gate": "false"}
    apply(**BASE)

    def fld(cls, name):
        k = cls.class_ if hasattr(cls, "class_") else cls
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)

    def doc(iid, r, lv=20, src="admin"):
        d_ = Roll.newDoc(JString(iid), JInt(r), True, JString(src), JInt(lv))
        d_.put("r", BS(Defs.R_ID[r]))
        return d_

    def stack(iid, d_):
        return Data.put(IS(JString(iid), JInt(1)), d_, u)

    def augs(d_, *codes):
        a_ = BA()
        for c_ in codes:
            a_.add(BS(c_))
        d_.put("aug", a_)
        return d_
    RID = [str(x) for x in Defs.R_ID]
    R = dict((n_, RID.index(n_)) for n_ in RID)
    SW, BOW, CH = "Weapon_Sword_Iron", "Weapon_Shortbow_Iron", "Armor_Iron_Chest"
    for iid in (SW, BOW, CH):
        K.check(bool(Data.isGear(JString(iid))), "E %s is gear in this boot" % iid)

    # ================================================================================== C the fresh config + the loader
    K.check("\naug.loot.prefill=10\n" in fresh, "C the fresh config carries aug.loot.prefill=10")
    K.eq(int(Cfg.AUG_PREFILL), 10, "C the loader reads aug.loot.prefill 10")
    pr0 = Props()
    pr0.load(JClass("java.io.StringReader")("\n".join(l for l in fresh.split("\n") if not l.startswith("aug.loot.prefill"))))
    Cfg.apply(pr0, False)
    a0 = int(Cfg.AUG_PREFILL)
    apply(aug__loot__prefill="999", **BASE)
    a1 = int(Cfg.AUG_PREFILL)
    apply(aug__loot__prefill="-5", **BASE)
    a2 = int(Cfg.AUG_PREFILL)
    apply(**BASE)
    K.eq((a0, a1, a2), (10, 100, 0), "C absent = 10, 999 clamped to 100, -5 clamped to 0")

    # ================================================================================== N count / tickCount / gear:fn:augCount
    nb = []
    d3 = augs(doc(SW, R["legendary"]), "S:Brute:3", "", "E:Fire:2", "junk")
    s3 = stack(SW, d3)
    if int(Aug.count(d3)) != 3 or int(Aug.count(JString(SW), s3.getMetadata())) != 3 or int(Aug.count(JString(SW), None)) != 0 or int(Aug.count(None)) != 0:
        nb.append(("count: 3 occupied (empty skipped, an unreadable one counted), no document 0", int(Aug.count(d3))))
    s0 = stack(SW, doc(SW, R["legendary"]))
    if int(Aug.count(JString(SW), s0.getMetadata())) != 0 or int(Aug.count(JString(SW), IS(JString(SW), JInt(1)).getMetadata())) != 0:
        nb.append("count: no aug list = 0, a plain stack = 0")
    tc = (int(Aug.tickCount(s3)), int(Aug.tickCount(s0)), int(Aug.tickCount(IS(JString("Ore_Copper"), JInt(3)))), int(Aug.tickCount(None)),
          int(Aug.tickCount(Data.put(IS(JString("Rock_Stone"), JInt(1)), d3, u))))
    if tc != (3, 0, 0, 0, 0):
        nb.append(("tickCount: a gear id is read, a plain ore / null / a non-gear id never", tc))
    Fn = P("GearAugCntFn")()
    md3 = s3.getMetadata()
    fa = [Fn.apply(s3), Fn.apply(OA([JString(SW), md3])), Fn.apply(OA([JString(SW), JString(str(md3.toJson()))])), Fn.apply(OA([JString(SW), None])),
          Fn.apply(OA([JString(SW)])), Fn.apply(s0)]
    fb = [Fn.apply(OA([])), Fn.apply(JInt(3)), Fn.apply(None), Fn.apply(OA([JString(SW), JInt(3)])), Fn.apply(OA([JInt(1), md3])),
          Fn.apply(OA([JString(SW), JString("{not json")]))]
    fa_ = [None if x is None else int(x) for x in fa]
    if fa_ != [3, 3, 3, 0, 0, 0] or [x for x in fb if x is not None]:
        nb.append(("gear:fn:augCount: IS / {id, BsonDocument} / {id, JSON} / {id, null} / {id} / no augments; junk -> null", fa_, [str(x) for x in fb]))
    K.check(not nb, "N GearAug.count / tickCount / gear:fn:augCount on REAL documents and stacks: %s" % nb)

    # ================================================================================== PF socketed loot
    pb = []
    apply(aug__loot__prefill="100", **BASE)
    Aug.FORCE = 0.0
    Aug.PICK = 0
    kinds = [str(x) for x in Aug.KIND]
    top = [int(x) for x in Aug.TOP]

    def kt(code):
        p_ = str(code).split(":")
        return kinds.index(p_[1]), int(p_[2])
    for rn in ("legendary", "fabled", "mythic", "untiered"):
        d_ = doc(SW, R[rn], 45, "box")
        c_ = Aug.prefill(JString(SW), d_, JInt(45), JInt(R[rn]))
        if c_ is None or int(Aug.count(d_)) != 1 or str(d_.get("aug").asArray().get(0).asString().getValue()) != str(c_) or kt(c_)[1] != min(3, top[kt(c_)[0]]):
            pb.append((rn, "prefilled at the Zone 3 tier", c_))
    for rn in ("normal", "unique", "rare", "set"):
        d_ = doc(SW, R[rn], 45, "box")
        if Aug.prefill(JString(SW), d_, JInt(45), JInt(R[rn])) is not None or int(Aug.count(d_)) != 0:
            pb.append((rn, "never prefilled"))
    dcr = doc(SW, R["legendary"], 45, "craft")
    if Aug.prefill(JString(SW), dcr, JInt(45), JInt(R["legendary"])) is not None or int(Aug.count(dcr)) != 0:
        pb.append("a crafted document is never prefilled")
    dhas = augs(doc(SW, R["legendary"], 45, "box"), "S:Edge:1")
    if Aug.prefill(JString(SW), dhas, JInt(45), JInt(R["legendary"])) is not None or int(Aug.count(dhas)) != 1 or str(dhas.get("aug").asArray().get(0).asString().getValue()) != "S:Edge:1":
        pb.append("an item that carries one already: untouched")
    apply(aug__loot__prefill="0", **BASE)
    d0 = doc(SW, R["legendary"], 45, "box")
    if Aug.prefill(JString(SW), d0, JInt(45), JInt(R["legendary"])) is not None:
        pb.append("0 % = never")
    apply(aug__loot__prefill="10", **BASE)
    Aug.FORCE = 0.5
    miss0 = int(Aug.PN[1])
    d05 = doc(SW, R["legendary"], 45, "box")
    if Aug.prefill(JString(SW), d05, JInt(45), JInt(R["legendary"])) is not None or int(Aug.PN[1]) != miss0 + 1:
        pb.append("a roll of 0.5 at 10 % misses and is counted")
    Aug.FORCE = 0.05
    if Aug.prefill(JString(SW), doc(SW, R["legendary"], 45, "box"), JInt(45), JInt(R["legendary"])) is None:
        pb.append("a roll of 0.05 at 10 % hits")
    apply(aug__loot__prefill="100", **BASE)
    Aug.FORCE = 0.0
    zt = [(int(Aug.zoneOf(JInt(lv))), lv) for lv in (1, 20, 21, 40, 41, 60, 61, 80, 81, 100, 130)]
    if [z for z, _l in zt] != [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5]:
        pb.append(("zoneOf by tools/tier_tags.py ZONE_TOPS", zt))
    # a 10-tier elemental kind at Lv 100 = T5; a 5-tier stat kind at Lv 100 = T5 (capped)
    el = [k for k in range(len(kinds)) if top[k] == 10]
    seen_t = set()
    for pk in range(0, 40):
        Aug.PICK = pk
        d_ = doc(SW, R["mythic"], 100, "box")
        c_ = Aug.prefill(JString(SW), d_, JInt(100), JInt(R["mythic"]))
        if c_ is not None:
            seen_t.add(kt(c_)[1])
    if seen_t != {5}:
        pb.append(("Lv 100 = T5 for every kind (5-tier capped, 10-tier at 5)", sorted(seen_t)))
    # random rolls: the kind always FITS (Tempo never on a bow; armor kinds on armor)
    Aug.PICK = -1
    bad_fit, got_k = [], {}
    for iid in (SW, BOW, CH):
        got_k[iid] = set()
        for _ in range(300):
            d_ = doc(iid, R["legendary"], 30, "box")
            c_ = Aug.prefill(JString(iid), d_, JInt(30), JInt(R["legendary"]))
            if c_ is None:
                bad_fit.append((iid, "no prefill"))
                break
            k_, t_ = kt(c_)
            got_k[iid].add(kinds[k_])
            if not bool(Aug.fitsAt(JInt(k_), Aug.kindAt(JString(iid), d_), JString(iid))) or t_ != min(2, top[k_]):
                bad_fit.append((iid, str(c_)))
    if "Tempo" in got_k[BOW] or bad_fit or len(got_k[SW]) < 4 or got_k[CH] & set(["Brute", "Tempo", "Edge"]):
        pb.append(("random kinds fit their item", bad_fit[:4], dict((k, sorted(v)) for k, v in got_k.items())))
    K.notes.append("PF kinds seen: %s" % dict((k, sorted(v)) for k, v in got_k.items()))
    # the bag open: GearUnid.pickZ n = 0 prefills, n = 1 (a re-identify) never; the tooltip shows it
    Aug.PICK = 0
    ty = int(Pool.typeOfId(JString(SW)))
    g0 = Unid.pickZ(JInt(ty), JInt(0), JInt(R["legendary"]), JInt(1), JInt(20), JInt(0), u, JInt(0))
    g1 = Unid.pickZ(JInt(ty), JInt(0), JInt(R["legendary"]), JInt(1), JInt(20), JInt(1), u, JInt(0))
    gr = Unid.pickZ(JInt(ty), JInt(0), JInt(R["rare"]), JInt(1), JInt(20), JInt(0), u, JInt(0))
    if g0 is None or g1 is None or gr is None:
        pb.append(("pickZ found no item", ty, g0, g1, gr))
    else:
        c0 = int(Aug.count(JString(str(g0[0])), g0[3].getMetadata()))
        c1 = int(Aug.count(JString(str(g1[0])), g1[3].getMetadata()))
        cr = int(Aug.count(JString(str(gr[0])), gr[3].getMetadata()))
        if (c0, c1, cr) != (1, 0, 0) or int(Aug.count(g0[2])) != 1:
            pb.append(("pickZ: a Legendary bag open prefilled (document + stack), a re-identify never, a Rare never", c0, c1, cr))
        txt, col = AL(), AL()
        View.lines(JString(str(g0[0])), g0[2], u, txt, col)
        tl = [str(x).replace(chr(2), "") for x in txt]
        nm_ = str(Aug.name(JInt(kt(str(g0[2].get("aug").asArray().get(0).asString().getValue()))[0]), JInt(1)))
        hit = [x for x in tl if nm_.split(" ")[0] in x and "[" in x]
        K.notes.append("PF tooltip of the prefilled item: %s" % [x for x in tl if "AUGMENT" in x.upper() or "[" in x][:4])
        if not hit:
            pb.append(("the tooltip shows the socketed augment", nm_, tl[-10:]))
    Aug.FORCE = -1.0
    Aug.PICK = -1
    apply(**BASE)
    K.check(not pb, "PF socketed loot on REAL documents: Legendary+ only, never crafted / already filled / 0 %%, the zone tier, the kind fits, the bag open "
            "(n = 0) prefills and a re-identify never, the tooltip shows it: %s" % pb)

    # ================================================================================== S gear:fn:salvage commitAug
    sb = []
    SF = P("GearSalvFn")()
    ref0 = int(Aug.PN[2])
    dS = augs(doc(SW, R["rare"], 10, "craft"), "S:Brute:1", "E:Fire:3")
    sS = stack(SW, dS)
    mdS = sS.getMetadata()

    def salv(mode, md_=None):
        r_ = SF.apply(OA([u, JString(SW), mdS if md_ is None else md_, JString(mode)]))
        return None if r_[0] is None else str(r_[0])
    w1, w2, w3, w4 = salv("commit"), salv("commitAug:1"), salv("commitAug:x"), salv("commitAug:2")
    if w1 is None or "This item has 2 augments - they would be destroyed" not in w1:
        sb.append(("a plain commit of an augmented piece refused", w1))
    if w2 is None or "changed since you confirmed (1 then, 2 now)" not in w2 or w3 is None or "changed since you confirmed" not in w3:
        sb.append(("a wrong / junk count refused (stale)", w2, w3))
    if w4 is not None and "augment" in w4.lower():
        sb.append(("commitAug:2 reaches GearSalv.commit (no augment refusal)", w4))
    sP = stack(SW, doc(SW, R["rare"], 10, "craft"))
    wp = salv("commit", sP.getMetadata())
    wpa = salv("commitAug:1", sP.getMetadata())
    if (wp is not None and "augment" in wp.lower()) or wpa is None or "changed since you confirmed (1 then, 0 now)" not in wpa:
        sb.append(("a plain piece commits as before; commitAug:1 on it = stale", wp, wpa))
    if int(Aug.PN[2]) != ref0 + 4:
        sb.append(("PN[2] counts the 4 refusals", int(Aug.PN[2]) - ref0))
    K.notes.append("S commitAug:2 answered %r; plain commit answered %r" % (w4, wp))
    K.check(not sb, "S gear:fn:salvage: augments only with the confirmed count (plain / wrong / junk refused, the right count goes on), plain pieces as before: %s" % sb)

    # ================================================================================== B the Salvagebench guard
    bb = []
    dB = augs(doc(SW, R["rare"], 10, "craft"), "S:Brute:2")
    sB = stack(SW, dB)
    sPl = stack(SW, doc(SW, R["rare"], 10, "craft"))
    if not bool(Pack.salvBlocked(JString(SW), sB.getMetadata())) or bool(Pack.salvBlocked(JString(SW), sPl.getMetadata())) or bool(Pack.salvBlocked(None, sB.getMetadata())):
        bb.append("salvBlocked: an augmented vanilla sword yes, a plain one no, no id no")
    GB.COOL.clear()
    blk0 = int(Aug.PN[3])
    in1, out1 = SIC(JShort(1)), SIC(JShort(4))
    in1.setItemStackForSlot(JShort(0), sB)
    n1 = int(GB.sweep(in1, out1, JArray(JClass("com.hypixel.hytale.server.core.universe.PlayerRef"))(0), None, None, JString("test-aug")))
    o0 = out1.getItemStack(JShort(0))
    left = in1.getItemStack(JShort(0))
    if n1 != 1 or (left is not None and not left.isEmpty()) or o0 is None or str(o0.getItemId()) != SW or int(Aug.count(JString(SW), o0.getMetadata())) != 1 \
            or int(GB.AUGN) != 0 or int(Aug.PN[3]) != blk0 + 1:
        bb.append(("sweep moves the augmented sword to the output with its augment; AUGN reset; PN[3] + 1", n1, left, o0, int(GB.AUGN), int(Aug.PN[3]) - blk0))
    GB.COOL.clear()
    in2, out2 = SIC(JShort(1)), SIC(JShort(4))
    in2.setItemStackForSlot(JShort(0), sPl)
    n2 = int(GB.sweep(in2, out2, JArray(JClass("com.hypixel.hytale.server.core.universe.PlayerRef"))(0), None, None, JString("test-plain")))
    if n2 != 0 or in2.getItemStack(JShort(0)) is None or out2.getItemStack(JShort(0)) is not None:
        bb.append(("a plain vanilla sword stays in the bench input", n2))
    # salvVeto on a REAL CraftingRecipe + Inventory
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    SECS = (("hotbar", "Hotbar", 9), ("storage", "Storage", 36), ("backpack", "Backpack", 9), ("armor", "Armor", 4), ("utility", "Utility", 4), ("tools", "Tool", 4))

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        fld(Cc, "inventory").set(o_, cont)
        return o_
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    BRQ = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    BT = JClass("com.hypixel.hytale.protocol.BenchType")

    def recipe(bench):
        mq = MQ(JString(SW), None, None, JInt(1), None)
        brq = BRQ(BT.values()[0], JString(bench), None, JInt(0), None)
        try:
            return CRR(JArray(MQ)([mq]), MQ(JString("Ingredient_Bar_Iron"), None, None, JInt(2), None), JArray(MQ)([]), JInt(1), JArray(BRQ)([brq]), JFloat(1.0), False, JInt(0))
        except Exception as ex_:
            K.notes.append("B CraftingRecipe ctor: %s - field set" % str(ex_)[:160])
            r_ = us.allocateInstance(CRR.class_)
            fld(CRR, "input").set(r_, JArray(MQ)([mq]))
            fld(CRR, "benchRequirement").set(r_, JArray(BRQ)([brq]))
            return r_
    try:
        inv = INV()
        cs = {}
        for f_, kind, n_ in SECS:
            cs[f_] = SIC(JShort(n_))
            try:
                fld(INV, f_).set(inv, comp(kind, cs[f_]))
            except Exception:
                fld(INV, f_).set(inv, cs[f_])
        rS, rX = recipe("Salvagebench"), recipe("Workbench")
        cs["storage"].setItemStackForSlot(JShort(5), sPl)
        v0 = Pack.salvVeto(rS, inv)
        cs["hotbar"].setItemStackForSlot(JShort(2), sB)
        blk1 = int(Aug.PN[3])
        v1 = Pack.salvVeto(rS, inv)
        v2 = Pack.salvVeto(rX, inv)
        K.notes.append("B salvVeto: plain %r / augmented %r / workbench %r" % (v0, v1, v2))
        if v0 is not None or v1 is None or "carries 1 augment - a Salvagebench recipe would destroy it" not in str(v1) or "Requip's SALVAGE button (it asks first)" not in str(v1) \
                or v2 is not None or int(Aug.PN[3]) != blk1 + 1:
            bb.append(("salvVeto: plain = no veto, an augmented match = the augment text, a Workbench recipe = no veto", v0, v1, v2))
    except Exception as ex_:
        bb.append(("salvVeto on a REAL recipe + inventory", str(ex_)[:300]))
    K.check(not bb, "B the Salvagebench guard: salvBlocked, GearBench.sweep (augmented out with its document, plain stays), salvVeto on a REAL recipe: %s" % bb)

    # ================================================================================== B2 FIXER (critic L1): the REAL GearBenchSys.tick checks the bench
    # id FIRST - an augmented Weapon_ stack in a Furnace's input is never read (getMetadata() clones the document); on a Salvagebench it is
    b2 = []
    try:
        fk = os.path.join(esc, "fake57")
        os.makedirs(fk, exist_ok=True)
        cpz = JClass("javassist.ClassPool")(False)
        cpz.appendSystemPath()
        cpz.appendClassPath(JString(B.SERVER_JAR))
        cpz.appendClassPath(JString(jar))
        CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
        CTn, CMPn = "com.hypixel.hytale.component.ComponentType", "com.hypixel.hytale.component.Component"
        fc = cpz.makeClass("skyygear57t.FakeChunk57")
        fc.setSuperclass(cpz.get("com.hypixel.hytale.component.ArchetypeChunk"))
        fc.addField(CtF.make("public java.util.Map comps;", fc))
        fc.addConstructor(CtC.make("public FakeChunk57() { super(null, null); }", fc))          # never run (Unsafe)
        fc.addMethod(CtM.make("public %s getComponent(int i, %s t) { if (this.comps == null) return null; return (%s) this.comps.get(t); }" % (CMPn, CTn, CMPn), fc))
        fc.writeFile(JString(fk))
        cc = cpz.makeClass("skyygear57t.CountStack57")
        cc.setSuperclass(cpz.get("com.hypixel.hytale.server.core.inventory.ItemStack"))
        cc.addField(CtF.make("public static int READS = 0;", cc))
        cc.addConstructor(CtC.make("public CountStack57(String id) { super(id, 1); }", cc))
        cc.addMethod(CtM.make("public org.bson.BsonDocument getMetadata() { READS = READS + 1; return super.getMetadata(); }", cc))
        cc.writeFile(JString(fk))
        fu = cpz.makeClass("skyygear57t.FakeUtil57")          # the 0.2.11 FakeUtil.single (a module singleton + its ComponentType fields, made in Java)
        fu.addMethod(CtM.make("""public static void single(String cn) throws java.lang.Exception {
  java.lang.Class c = java.lang.Class.forName(cn, false, java.lang.ClassLoader.getSystemClassLoader());
  java.lang.reflect.Field uf = java.lang.Class.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe");
  uf.setAccessible(true);
  java.lang.Object us = uf.get(null);
  java.lang.reflect.Method alloc = us.getClass().getMethod("allocateInstance", new java.lang.Class[] { java.lang.Class.class });
  java.lang.reflect.Field f = c.getDeclaredField("instance");
  f.setAccessible(true);
  java.lang.Object o = f.get(null);
  if (o == null) { o = alloc.invoke(us, new java.lang.Object[] { c }); f.set(null, o); }
  java.lang.Class ct = java.lang.Class.forName("com.hypixel.hytale.component.ComponentType");
  java.lang.Class k = c;
  while (k != null && k != java.lang.Object.class) {
    java.lang.reflect.Field[] fs = k.getDeclaredFields();
    for (int i = 0; i < fs.length; i++) {
      if (fs[i].getType() != ct || java.lang.reflect.Modifier.isStatic(fs[i].getModifiers())) continue;
      fs[i].setAccessible(true);
      if (fs[i].get(o) == null) fs[i].set(o, alloc.invoke(us, new java.lang.Object[] { ct }));
    }
    k = k.getSuperclass();
  }
}""", fu))
        fu.writeFile(JString(fk))
        ldr =JClass("java.net.URLClassLoader")(JArray(JClass("java.net.URL"))([JClass("java.io.File")(JString(fk)).toURI().toURL()]), IS.class_.getClassLoader())
        FCh57, CS57 = JClass("skyygear57t.FakeChunk57", loader=ldr), JClass("skyygear57t.CountStack57", loader=ldr)
        PBB = JClass("com.hypixel.hytale.builtin.crafting.component.ProcessingBenchBlock")
        PBN = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.ProcessingBench")
        BNC = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench")
        JClass("skyygear57t.FakeUtil57", loader=ldr).single(JString("com.hypixel.hytale.builtin.crafting.CraftingPlugin"))
        ctp = PBB.getComponentType()

        def cstack():
            s_ = CS57(JString(SW))
            fld(IS, "metadata").set(s_, stack(SW, augs(doc(SW, R["rare"], 10, "craft"), "S:Brute:2")).getMetadata())
            return s_

        def tick_on(bid, s_):
            pb_ = PBB()
            in_, out_ = SIC(JShort(1)), SIC(JShort(4))
            in_.setItemStackForSlot(JShort(0), s_)
            fld(PBB, "inputContainer").set(pb_, in_)
            fld(PBB, "outputContainer").set(pb_, out_)
            bn_ = us.allocateInstance(PBN.class_)
            fld(BNC, "id").set(bn_, JString(bid))
            fld(PBB, "bench").set(pb_, bn_)
            ch_ = us.allocateInstance(FCh57.class_)
            m_ = JClass("java.util.IdentityHashMap")()
            m_.put(ctp, pb_)
            fld(FCh57, "comps").set(ch_, m_)
            CS57.READS = 0
            GB.COOL.clear()
            P("GearBenchSys")(True).tick(JFloat(0.05), JInt(0), ch_, None, None)
            return int(CS57.READS), in_
        sF = cstack()
        k0 = int(Aug.count(JString(SW), sF.getMetadata()))
        rF, inF = tick_on("Furnace", sF)
        rS, inS = tick_on("Salvagebench", cstack())
        K.notes.append("B2 metadata reads by the real tick: Furnace %d, Salvagebench %d (the piece carries %d augments)" % (rF, rS, k0))
        if k0 != 1 or rF != 0 or inF.getItemStack(JShort(0)) is None or inF.getItemStack(JShort(0)).isEmpty():
            b2.append(("a Furnace input: no metadata read, the piece stays", k0, rF))
        if rS < 1:
            b2.append(("a Salvagebench input IS read (tickCount runs there)", rS))
    except Exception as ex_:
        b2.append(("the real GearBenchSys.tick rig", str(ex_)[:400]))
    K.check(not b2, "B2 FIXER L1: the REAL GearBenchSys.tick asks the bench id first - an augmented sword in a Furnace is never read, on a Salvagebench it is: %s" % b2)

    # ================================================================================== R re-identify keeps augments (keepAug)
    rb = []
    old = augs(doc(SW, R["legendary"], 15, "box"), "S:Brute:2", "E:Air:4")
    old.put("augAdd", BI(1))
    gk = Unid.pickZ(JInt(ty), JInt(0), JInt(R["legendary"]), JInt(1), JInt(20), JInt(1), u, JInt(0))
    if gk is None:
        rb.append("pickZ (re-identify shape) found no item")
    else:
        s_before = gk[3]
        k2 = Idn.keepAug(gk, old, u)
        nd = k2[2]
        sm = k2[3].getMetadata()
        if int(Aug.count(nd)) != 2 or int(Aug.added(nd)) != 1 or int(Aug.count(JString(str(k2[0])), sm)) != 2 or SysJ.identityHashCode(k2[3]) == SysJ.identityHashCode(s_before):
            rb.append(("keepAug: 2 augments + 1 paid slot on the new document AND stack", int(Aug.count(nd)), int(Aug.added(nd))))
        gk2 = Unid.pickZ(JInt(ty), JInt(0), JInt(R["legendary"]), JInt(1), JInt(20), JInt(1), u, JInt(0))
        st2 = gk2[3]
        k3 = Idn.keepAug(gk2, doc(SW, R["legendary"], 15, "box"), u)
        if SysJ.identityHashCode(k3[3]) != SysJ.identityHashCode(st2) or int(Aug.count(k3[2])) != 0:
            rb.append("nothing to carry = the result unchanged")
        if Idn.keepAug(None, old, u) is not None:
            rb.append("keepAug(null) = null")
    K.check(not rb, "R re-identify keeps the augments + paid slots (keepAug on REAL pickZ results): %s" % rb)
    K.save()


# ====================================================================================================== D: start twice on the live copy
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg = JClass(PKG + "GearCfg")
    fc = os.path.join(home, "config.properties")
    c0 = open(fc, "rb").read() if os.path.isfile(fc) else None
    K.check(c0 is not None, "D the live copy has a config.properties")
    Paths = JClass("java.nio.file.Paths")
    Cfg.FILE = Paths.get(fc)
    Cfg.DIR = Paths.get(home)
    MIG = ["migrate0326", "migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39", "migrateUt28", "migrateCan2", "migrateAs51",
           "migrateUt53", "migrateMy53", "migrateSig56"]
    m0 = "\n".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    c1 = open(fc, "rb").read()
    m1 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    K.notes.append("D start 1: one-time updates said %r" % m0[-400:])
    K.check(open(fc, "rb").read() == c1 and m1 == "", "D start 2 changes nothing")
    had = b"aug.loot.prefill" in c0
    K.check((b"aug.loot.prefill" in c1) == had, "D aug.loot.prefill is a new key: not written by this round")
    if not had:
        K.eq(int(Cfg.AUG_PREFILL), 10, "D aug.loot.prefill absent in the live file = 10")
    dl, dn = c0.decode("latin-1").splitlines(), c1.decode("latin-1").splitlines()
    extra = [l for l in dn if l not in dl]
    allowed = lambda l: (l.strip() == "" or l.startswith(("ut.", "utfx.", "utpow.", "gear.mythicItems=", "stats.as=", "sig.ut.", "# ---- ")) or "SkyyGear 0.3.5" in l)
    K.check(all(allowed(l) for l in extra), "D only the earlier 0.3.5x one-time updates may touch the file: %s" % [l for l in extra if not allowed(l)][:5])
    K.check(not [l for l in dl if l not in dn], "D no old line removed")
    K.save()


HK.run_compare = T54["run_compare54"]
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("engine56", T56["run_engine"]), ("engine55", T55["run_engine"]), ("live", run_live)], __file__,
       live=(LIVE_DIR, "Skyy_SkyyGear"))
