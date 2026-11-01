"""Harness for SkyyGear 0.3.54 (gear lane round 2 = gl2: the Trork Warrior set 2 / 4 pieces + the Kweebec 2-piece as THEME SETS by id, out of the
random bags, native drops keep their id - tools/gear_0_3_54_patch.py header; partner SkyyMobs 0.1.24 = the drop rows).
Build first:
    python tools/gear_0_3_54_patch.py && python SkyyGear/build_skyygear_0.3.54.py
    python SkyyGear/test_skyygear_0.3.54.py [--keep]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.53 jar is the compare base):
  S  static   the patch re-runs to identical bytes, line endings kept, ONE new class (GearTheme), no command / system; the jar's non-class files
              = 0.3.53's (only manifest.json changed); the 14 ids are vanilla (Assets.zip, read only) and the tier tags come from their level
              band (tools/tier_tags.py combat_tag: Trork T1, Kweebec T2); the fresh config text carries the 3 rows (no marker, no migration)
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.53 -> 0.3.54 (EXPECT below)
  E  engine   the 0.2.11 harness's bare server boot (vanilla pack + THIS jar) - every new path EXECUTED:
              V  the 14 ids in the real Item store; GearTheme.piece / weapon / setOf
              P  the pool: the 14 ids out of P_ID (Diving / UT looks still out, other Heavy / Light pieces still in)
              N  a native drop: GearTag.unid (mob + chest) keeps the Trork / Kweebec id unidentified (never a bag), a control piece still
                 becomes a bag; GearUnid.fromItem refuses them; GearTag.spread leaves a theme stack alone
              T  GearStats.totals0 on a REAL armor container: 1 / 2 / 3 / 4 Trork pieces (def+3 at 2, + str+2 at 4), Kweebec 2, both sets at
                 once, an unidentified / level-gated piece does not count; GearTheme.hp (8 at 4 pieces) and GearArmor.lockSums0 (the Health
                 lock); activeText; a live Server Setup edit (apply) + an empty row; checkBonus (words, mining words, commas)
              U  a REAL tooltip (GearView.lines): "Set: Trork Warrior (2/4)" + the two tier lines (set colour when reached, grey otherwise),
                 a Kweebec piece, a Trork weapon's grey line, the T1 tag first; the Armor sets block of a set-field piece unchanged
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyGear: the older one-time updates may run once (0.3.5x), none of
              the 3 new keys is written, the defaults are read; the second start changes nothing
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): a real Trork kill dropping a piece through vanilla's list / SkyyMobs 0.1.24's row and SkyyGear's death mark
tagging it in that tick (GearTag.unid is executed here); the client drawing the tooltip block; the Health lock inside a live player tick.
Scratch: tools/dev/scratch/gl2/harness (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.54"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gl2", "harness")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.53.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_54_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.53.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyGear")
ADDED = ["GearTheme"]
EXPECT = {          # the first run's dump, reviewed: the 3 rows (CfgRows / CfgFn / CfgFile, GearCfg fields + apply + defaultsText), the call sites
          # (GearSet.tipLines, GearStats.totals0, GearArmor.lockSums0, GearStamp.scanSome = the inventory scan's note, GearAdmin.me = /gear,
          # GearFx.forget, GearUnid.fromItem, GearTag.spread), the pool tables without the 14 ids (GearPool / GearUt.CRAFTED; GearPack unchanged: the 14 stay in LOOT_IDS = loot only, critic-2 fix), setup
    'CfgFile': ['~<clinit>'], 'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'CfgRows1': ['~<clinit>'], 'CfgRows2': ['~<clinit>'],
    'GearAdmin': ['~m me'], 'GearArmor': ['~m lockSums0'], 'GearCfg': ['+f TH_T0', '+f TH_T1', '+f TH_T2', '~<clinit>', '~m apply', '~m defaultsText'],
    'GearFx': ['~m forget'],
    'GearPool': ['~<clinit>', '~m candM', '~m idIdx', '~m levelsM', '~m liveType', '~m matchM', '~m packText', '~m pickItemM', '~m table', '~m typeOfId', '~m w'],
    'GearSet': ['~m tipLines'], 'GearStamp': ['~m scanSome'], 'GearStats': ['~m totals0'], 'GearTag': ['~m spread'], 'GearUnid': ['~m fromItem'],
    'GearUt': ['~<clinit>'], 'SkyyGearPlugin': ['~m setup'],
}
U = "00000000-0000-0000-0000-000000000354"
TA = ["Armor_Trork_Head", "Armor_Trork_Chest", "Armor_Trork_Hands", "Armor_Trork_Legs"]
TW = ["Weapon_%s_Stone_Trork" % f for f in ("Axe", "Battleaxe", "Club", "Daggers", "Longsword", "Mace", "Spear", "Sword")]
KA = ["Armor_Kweebec_Head", "Armor_Kweebec_Chest"]
IDS = TA + KA + TW
KEYS = ["themeset.trork.2", "themeset.trork.4", "themeset.kweebec.2"]
DEFS = ["def+3", "hp+8 str+2", "spd+1 hpr+1"]


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.54 - build script') and g.count('VERSION = "0.3.54"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("), g.count('mk("') - o.count('mk("')),
         (0, 0, 1), "S one new class (GearTheme), no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    ea = set(n for n in za.namelist() if not n.endswith(".class"))
    eb = set(n for n in zb.namelist() if not n.endswith(".class"))
    K.eq((sorted(eb - ea), sorted(ea - eb), sorted(n for n in ea & eb if za.read(n) != zb.read(n))), ([], [], ["manifest.json"]),
         "S non-class files: none added / removed, only manifest.json changed (no lang, no item file - vanilla ids only)")
    A = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))          # read only
    items = set(os.path.basename(n)[:-5] for n in A.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    K.check(all(i in items for i in IDS), "S the 14 ids are vanilla items: %s" % [i for i in IDS if i not in items])
    K.check(not [n for n in zb.namelist() if any(i in n for i in IDS)], "S the jar ships no file named after a theme id (no override)")
    import importlib
    TT = importlib.import_module("tier_tags")
    K.eq([TT.combat_tag(i, 3) for i in TA + TW] + [TT.combat_tag(i, 10) for i in KA], ["T1 Crude"] * 12 + ["T2 Iron"] * 2,
         "S tier tags by the level band (Trork Lv 3 = T1 Crude, Kweebec Lv 10 = T2 Iron; no tier_tags table row needed)")
    K.check(g.count("TH54_KEYS") >= 3 and "migrate" not in "".join(l for l in g.splitlines() if "0.3.54" in l and "migrate" in l and "no one-time" not in l and "NO one-time" not in l),
            "S no one-time update in 0.3.54")
    K.save()


def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JShort, JFloat, JArray
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng")
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
    H["engine_boot"](KC(K))
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Data, Roll, View, Defs, Pool, Stats, Th, Tag, Unid, Arm, GSet = (P("GearCfg"), P("Gear"), P("GearData"), P("GearRoll"), P("GearView"),
                                                                              P("GearDefs"), P("GearPool"), P("GearStats"), P("GearTheme"), P("GearTag"),
                                                                              P("GearUnid"), P("GearArmor"), P("GearSet"))
    Props = JClass("java.util.Properties")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    AL = JClass("java.util.ArrayList")
    BS = JClass("org.bson.BsonString")
    SysJ = JClass("java.lang.System")
    u = UUID.fromString(U)
    sysp = SysJ.getProperties()
    if sysp.get("skyy.bridge") is None:
        sysp.put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    data = os.path.join(scratch, "data")
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
    K.check(all(("\n%s=%s\n" % (k, v)) in fresh for k, v in zip(KEYS, DEFS)) and [str(Cfg.TH_T0), str(Cfg.TH_T1), str(Cfg.TH_T2)] == DEFS,
            "M the fresh config carries the 3 rows with their defaults; apply reads them")
    pr = Props()
    pr.load(JClass("java.io.StringReader")("\n".join(l for l in fresh.split("\n") if not l.startswith("themeset."))))
    pr.setProperty("part.gate", "false")
    Cfg.apply(pr, False)
    K.eq([str(Cfg.TH_T0), str(Cfg.TH_T1), str(Cfg.TH_T2)], DEFS, "M a file without the 3 lines = the defaults (no one-time update)")
    apply(**BASE)

    # ================================================================================== V the ids
    K.check(not [i for i in IDS if Gear.item(JString(i)) is None], "V the 14 ids are in the real Item store")
    K.eq(([int(Th.piece(JString(i))) for i in TA + KA], [int(Th.weapon(JString(i))) for i in TW], [int(Th.setOf(JString(i))) for i in IDS],
          int(Th.setOf(JString("Armor_Steel_Chest"))), int(Th.setOf(None))),
         (list(range(6)), list(range(8)), [0] * 4 + [1] * 2 + [0] * 8, -1, -1), "V GearTheme.piece / weapon / setOf (Trork 0, Kweebec 1, others -1)")

    # ================================================================================== P the pool
    pid = [str(x) for x in Pool.P_ID]
    K.check(not [i for i in IDS if i in pid], "P the 14 theme ids are out of the random bag pool: %s" % [i for i in IDS if i in pid])
    K.check(not [i for i in pid if i.startswith("Armor_Diving_Crude_")] and [i for i in pid if i.startswith("Armor_Steel_")] and [i for i in pid if i.startswith("Armor_Leather_")],
            "P Crude Diving still out; plain Steel / Leather pieces still in")
    Pack = P("GearPack")
    K.check(all(bool(Pack.inLoot(JString(i))) for i in IDS), "P the 14 theme ids stay loot only (GearPack.inLoot) though out of the bags")
    smc0 = bool(Cfg.SMITH_COMBAT)
    Cfg.SMITH_COMBAT = True
    try:
        ob = (bool(Pack.combatId(JString("Weapon_Axe_Stone_Trork"))), bool(Pack.offBench(JString("Weapon_Axe_Stone_Trork"))))
        K.eq(ob, (False, True), "P fix: Weapon_Axe_Stone_Trork (vanilla bench recipe) stays off the bench - loot only, not a plain Smithing piece")
    finally:
        Cfg.SMITH_COMBAT = smc0

    # ================================================================================== N native drops keep their id
    nb = []
    for i in (TA[1], KA[0], TW[3]):
        for col in (1, 2):
            s0 = IS(JString(i), JInt(1))
            s1 = Tag.unid(s0, JInt(col), JInt(5), JString("mob" if col == 1 else "zone"))
            d1 = Data.gearDoc(s1.getMetadata()) if s1 is not None else None
            if s1 is None or str(s1.getItemId()) != i or bool(Unid.isBox(s1.getItemId())) or d1 is None or bool(Data.identified(d1)):
                nb.append((i, col, None if s1 is None else str(s1.getItemId())))
        if Unid.fromItem(IS(JString(i), JInt(1)), JInt(1), JInt(5), JString("mob")) is not None:
            nb.append((i, "fromItem made a bag"))
    ctl = Tag.unid(IS(JString("Armor_Steel_Chest"), JInt(1)), JInt(1), JInt(20), JString("mob"))
    K.notes.append("N control Armor_Steel_Chest -> %s" % (None if ctl is None else str(ctl.getItemId())))
    if ctl is None or not bool(Unid.isBox(ctl.getItemId())):
        nb.append(("control: a plain Steel chest still becomes a bag", None if ctl is None else str(ctl.getItemId())))
    ch = SIC(JShort(9))
    ch.setItemStackForSlot(JShort(0), IS(JString(TA[0]), JInt(3)))
    sp = int(Tag.spread(ch, JInt(0), JInt(5), JString("zone")))
    s0 = ch.getItemStack(JShort(0))
    if sp != 0 or str(s0.getItemId()) != TA[0] or int(s0.getQuantity()) != 3 or any(ch.getItemStack(JShort(k)) is not None and not ch.getItemStack(JShort(k)).isEmpty() for k in range(1, 9)):
        nb.append(("spread left the theme stack alone", sp))
    K.check(not nb, "N GearTag.unid (mob + chest) keeps a Trork / Kweebec armor / weapon id, unidentified, never a bag; fromItem refuses them; spread "
            "leaves a stack of 3 alone; a plain Steel chest still becomes a bag: %s" % nb)

    # ================================================================================== T totals0 / hp / lockSums0 / activeText / edits / check
    I = dict((str(Defs.S_KEY[i]), i) for i in range(int(Defs.NS)))

    def doc(iid, r=0, ident=True, lv=5):
        d_ = Roll.newDoc(JString(iid), JInt(r), ident, JString("admin"), JInt(lv))
        d_.put("r", BS(Defs.R_ID[r]))
        return d_

    def stack(iid, d_):
        return Data.put(IS(JString(iid), JInt(1)), d_, u)

    def kit(ids, ident=True):
        a = SIC(JShort(4))
        for k, i in enumerate(ids):
            a.setItemStackForSlot(JShort(k), stack(i, doc(i, ident=ident)))
        return a

    def tot(a):
        return [int(x) for x in Stats.totals0(u, None, a, None, False)]
    kits = dict((n, kit(TA[:n])) for n in range(0, 5))          # the SAME stacks for both readings (their rolled lines stay equal)
    kk = kit(KA)
    base = dict((n, tot(kits[n])) for n in range(0, 5))
    bk = tot(kk)

    def delta(a, b):
        return dict((str(Defs.S_KEY[i]), a[i] - b[i]) for i in range(len(a)) if a[i] != b[i])

    def lsum(a):
        m = Arm.lockSums0(u, a, JFloat(1.0))
        return sum(float(m.get(k)) for k in m.keySet())
    tb = []
    ls_on = dict((n, lsum(kits[n])) for n in (2, 4))
    apply(themeset__trork__2="", themeset__trork__4="", themeset__kweebec__2="", **BASE)          # the pieces' own lines without any theme bonus
    raw = dict((n, tot(kits[n])) for n in range(0, 5))
    rk = tot(kk)
    ls_off = dict((n, lsum(kits[n])) for n in (2, 4))
    apply(**BASE)
    want = {0: {}, 1: {}, 2: {"def": 3}, 3: {"def": 3}, 4: {"def": 3, "str": 2}}
    got = dict((n, delta(base[n], raw[n])) for n in range(0, 5))
    if got != want:
        tb.append(("Trork 0-4 pieces: the theme part of the totals", got))
    kw = delta(bk, rk)
    if kw != {"spd": 1, "hpr": 1}:
        tb.append(("Kweebec head + chest = spd+1 hpr+1", kw))
    lsd = dict((n, round(ls_on[n] - ls_off[n], 3)) for n in (2, 4))
    K.notes.append("T lockSums0 theme part (with - without the rows): %s" % lsd)
    if lsd != {2: 0.0, 4: -8.0}:
        tb.append(("GearArmor.lockSums0: the Health lock gets -8 (adds +8 Health) at 4 Trork pieces, nothing at 2", lsd))
    both = kit([TA[0], TA[1], KA[0], KA[1]])
    th_both = JArray(JInt)(int(Defs.NS))
    n_on = int(Th.addTo(th_both, u, both))
    if n_on != 2 or delta([int(x) for x in th_both], [0] * int(Defs.NS)) != {"def": 3, "spd": 1, "hpr": 1}:
        tb.append(("2 Trork + 2 Kweebec = both 2-piece tiers", n_on, delta([int(x) for x in th_both], [0] * int(Defs.NS))))
    unid = SIC(JShort(4))
    for k, i in enumerate(TA[:2]):
        unid.setItemStackForSlot(JShort(k), stack(i, doc(i, ident=(k == 0))))
    if list(Th.counts(u, unid)) != [1, 0]:
        tb.append(("an unidentified piece does not count", list(Th.counts(u, unid))))
    apply(part__gate="true")
    gated = SIC(JShort(4))
    for k, i in enumerate(TA[:2]):
        gated.setItemStackForSlot(JShort(k), stack(i, doc(i, lv=60)))
    gc = list(Th.counts(u, gated))
    apply(**BASE)
    K.notes.append("T level-gated (Lv 60 pieces, part.gate on, no SkyySkills) counts %s" % gc)
    hp4, hp2 = float(Th.hp(u, kit(TA))), float(Th.hp(u, kit(TA[:2])))
    if hp4 != 8.0 or hp2 != 0.0:
        tb.append(("GearTheme.hp: 8 at 4 pieces, 0 at 2", hp4, hp2))
    at4 = str(Th.activeText(u, kit(TA)))
    if at4 != "Trork Warrior 2 pieces: +3 Defense; Trork Warrior 4 pieces: +2 Strength, +8 Health" or str(Th.activeText(u, kit(TA[:1]))) != "none":
        tb.append(("activeText", at4))
    apply(themeset__trork__2="def+10 hp+5", themeset__trork__4="", **BASE)
    ed = JArray(JInt)(int(Defs.NS))
    Th.addTo(ed, u, kit(TA))
    edh = float(Th.hp(u, kit(TA)))
    apply(**BASE)
    if delta([int(x) for x in ed], [0] * int(Defs.NS)) != {"def": 10} or edh != 5.0:
        tb.append(("a live edit (def+10 hp+5 at 2, empty 4-piece row)", delta([int(x) for x in ed], [0] * int(Defs.NS)), edh))
    ck = dict((v, Th.checkBonus(JString("themeset.trork.2"), JString(v))) for v in ("def+3", "hp+8 str+2", "", "def+3,hp+2", "mfort+3", "bogus+2", "dmg+5"))
    if ck["def+3"] is not None or ck["hp+8 str+2"] is not None or ck[""] is not None or ck["def+3,hp+2"] is None or ck["mfort+3"] is None or ck["bogus+2"] is None \
            or ck["dmg+5"] is None or Th.checkBonus(JString("x"), None) is not None:
        tb.append(("checkBonus", dict((k, None if v is None else str(v)[:60]) for k, v in ck.items())))
    K.check(not tb, "T totals0 on a real armor container: Trork 2 pieces def+3, 4 pieces + str+2 (1 / 3 pieces = the lower tier), Kweebec 2 spd+1 hpr+1, "
            "both sets at once; unidentified = no count; hp 8 at 4 (lockSums0 = the Health lock); activeText; a live edit; checkBonus refuses "
            "commas / mining words / unknown or weapon-only keys: %s" % tb)

    # ================================================================================== U the tooltip
    ub = []

    def tip(iid, d_):
        txt, col = AL(), AL()
        View.lines(JString(iid), d_, u, txt, col)
        return [str(x) for x in txt], [None if x is None else str(x) for x in col]
    Th.note(u, kit(TA[:2]))
    tl, tc = tip(TA[1], doc(TA[1]))
    K.notes.append("U Trork chest tooltip (2 worn): %s" % [x.replace(chr(2), "|") for x in tl])
    hexs = str(Defs.R_HEX[int(Defs.R_SET)])
    gray = str(Defs.C_GRAY)
    try:
        i0 = tl.index("Set: Trork Warrior (2/4)")
        if tl[i0 + 1] != "2 pieces: +3 Defense" or tl[i0 + 2] != "4 pieces: +2 Strength, +8 Health" or tc[i0] != hexs or tc[i0 + 1] != hexs or tc[i0 + 2] != gray:
            ub.append(("the block + colours", tl[i0:i0 + 3], tc[i0:i0 + 3]))
    except ValueError:
        ub.append(("no 'Set: Trork Warrior (2/4)' line", tl))
    Th.note(u, kit(TA))
    tl4, tc4 = tip(TA[0], doc(TA[0]))
    if "Set: Trork Warrior (4/4)" not in tl4 or tc4[tl4.index("4 pieces: +2 Strength, +8 Health")] != hexs:
        ub.append(("4 worn: (4/4), the 4-piece line in the set colour", tl4[-6:]))
    Th.note(u, kit(KA))
    tlk, tck = tip(KA[0], doc(KA[0]))
    if "Set: Kweebec (2/2)" not in tlk or "2 pieces: +1 Raw Health Regen, +1 Speed" not in tlk:
        ub.append(("Kweebec block", tlk[-5:]))
    tlw, tcw = tip(TW[1], doc(TW[1]))
    wl = [x for x in tlw if "set weapon" in x]
    if wl != ["Trork Warrior set weapon"] or tcw[tlw.index(wl[0])] != gray:
        ub.append(("the weapon's grey line is exactly 'Trork Warrior set weapon' (fix gl2fix 1)", wl, tlw[-4:]))
    # fix gl2fix 2: a player with no scan yet (no WORN entry) sees "(4 pieces)", never "(0/4)" - the in-game step names both forms
    u0 = UUID.randomUUID()
    tl0 = [str(x) for x in (lambda t, c: (View.lines(JString(TA[1]), doc(TA[1]), u0, t, c), t)[1])(AL(), AL())]
    if "Set: Trork Warrior (4 pieces)" not in tl0 or [x for x in tl0 if x.startswith("Set: Trork Warrior (") and "/" in x]:
        ub.append(("unscanned owner: 'Set: Trork Warrior (4 pieces)' (fix gl2fix 2)", tl0[-4:]))
    Th.note(u0, kit([]))
    tl0b = [str(x) for x in (lambda t, c: (View.lines(JString(TA[1]), doc(TA[1]), u0, t, c), t)[1])(AL(), AL())]
    if "Set: Trork Warrior (0/4)" not in tl0b:
        ub.append(("scanned owner with no pieces: 'Set: Trork Warrior (0/4)' (fix gl2fix 2)", tl0b[-4:]))
    if not any(x.startswith("T1 ") for x in tl[:4]):
        ub.append(("the tier tag first", tl[:4]))
    tls, _c = tip("Armor_Steel_Chest", doc("Armor_Steel_Chest"))
    if [x for x in tls if x.startswith("Set: ") or "pieces: " in x or "set weapon" in x]:
        ub.append(("a non-theme piece shows no set block", tls[-4:]))
    K.check(not ub, "U REAL tooltips: Set: Trork Warrior (x/4) + 2 / 4 pieces lines (set colour when reached, grey otherwise), Kweebec (2/2), the Trork "
            "weapon's grey line, the tier tag first, no block on a plain piece: %s" % ub)
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
    K.check(c0 is not None and b"themeset." not in c0, "D the live copy has a config.properties without themeset lines")
    Paths = JClass("java.nio.file.Paths")
    Cfg.FILE = Paths.get(fc)
    Cfg.DIR = Paths.get(home)
    MIG = ["migrate0326", "migrate0330", "migrateP4", "migrateP5", "migrateP6", "migrateP7", "migrate39", "migrateUt28", "migrateCan2", "migrateAs51",
           "migrateUt53", "migrateMy53"]
    m0 = "\n".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    c1 = open(fc, "rb").read()
    m1 = "".join(str(getattr(Cfg, x)()) for x in MIG if hasattr(Cfg, x))
    Cfg.load()
    K.notes.append("D start 1: older one-time updates said %r" % m0[:600])
    K.check(open(fc, "rb").read() == c1 and m1 == "", "D start 2 changes nothing")
    K.check(b"themeset." not in c1 and [str(Cfg.TH_T0), str(Cfg.TH_T1), str(Cfg.TH_T2)] == DEFS, "D no themeset line is written; the defaults are read")
    t1 = c1.decode("latin-1")
    dl, dn = c0.decode("latin-1").splitlines(), t1.splitlines()
    extra = [l for l in dn if l not in dl]
    allowed = lambda l: (l.strip() == "" or l.startswith(("ut.", "utfx.", "utpow.", "gear.mythicItems=", "stats.as=", "# ---- ")) or "SkyyGear 0.3.5" in l)
    K.check(all(allowed(l) for l in extra), "D only the older 0.3.5x one-time updates may touch the file: %s" % [l for l in extra if not allowed(l)][:5])
    K.save()


def run_compare54(out, jar, old_jar, pkg, expect, added, removed=()):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_
    pa, pb = pool_of(old_jar), pool_of(jar)

    def members(p_, cn):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature()) + " " + str(f_.getModifiers())

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            cpl_ = mi_.getConstPool()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                ln_ = re.sub(r"^ldc_w ", "ldc ", re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))))
                lines_.append(re.sub(r"^((?:if\w*|goto(?:_w)?|jsr(?:_w)?)) -?\d+$", r"\1", ln_))
            return str(b_.getModifiers()) + "\n" + "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_
    na, nb = HK.jar_classes(old_jar), HK.jar_classes(jar)
    K.eq(sorted(set(nb) - set(na)), sorted(pkg + a for a in added), "C: classes added")
    K.eq(sorted(set(na) - set(nb)), sorted(pkg + r for r in removed), "C: classes removed")
    diffs, same = {}, 0
    for cn in sorted(set(na) & set(nb)):
        ma, mb = members(pa, cn), members(pb, cn)
        dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
        if dd:
            diffs[cn[len(pkg):] if cn.startswith(pkg) else cn] = sorted(("+" if k not in ma else ("-" if k not in mb else "~")) + k for k in dd)
        else:
            same += 1
    print("C. class compare %s -> %s: %d classes identical, %d differ" % (os.path.basename(old_jar), os.path.basename(jar), same, len(diffs)))
    got = dict((k, sorted(set(x.split("(")[0] for x in v))) for k, v in diffs.items())
    for k in sorted(got):
        print("   %-22s %s" % (k, ", ".join(got[k])))
    if expect is None:
        json.dump(got, open(os.path.join(os.path.dirname(SCRATCH), "expect54.dump.json"), "w"), indent=1, sort_keys=True)
        K.check(False, "C: no EXPECT yet - wrote expect54.dump.json next to the harness scratch (review it, then paste it as EXPECT)")
    else:
        K.eq(sorted(got), sorted(expect), "C: the classes that differ")
        for k in sorted(expect):
            K.eq(got.get(k, []), sorted(expect[k]), "C: %s members" % k)
    K.notes.append("C: %d identical, changed: %s" % (same, got))
    K.save()


HK.run_compare = run_compare54
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyGear"))
