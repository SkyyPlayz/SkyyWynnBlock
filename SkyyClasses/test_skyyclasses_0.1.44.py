"""Harness for SkyyClasses 0.1.44 (BALANCE PASS P4, the SkyyClasses part; tools/classes_0_1_44_patch.py). Build first:
    python tools/classes_0_1_44_patch.py && python SkyyClasses/build_skyyclasses_0.1.44.py
    python SkyyClasses/test_skyyclasses_0.1.44.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/balp4b/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.43 -> 0.1.44: exactly the planned members (EXPECT)
  X   exec     the defaults: abil.costPerLevel per class = tools/balance_model.py (Mage 0, Spellblade 2.5, others 1.5), the Spellblade walking
               Mana 16 / 14 / 18 / 20 / 18 (AbilDefs.mana, every shape x2 of 0.1.43's), UX_DMGCAP 40 / UX_DRCAP 35; costLvl through a fake
               skill:fn:level (Lv 0 / 40 / 100 -> x1 / x1.6 / x2.5, Spellblade x3.5, Mage x1, no SkyySkills = x1); costMana on a real AbilCtx
               (x lvlCost, + the tree's flat cost first, 0 = x1) and echoOf keeps lvlCost; ctxFor sets it; manaCast sends {"cast", UUID}
               (and the real SkyySkills 0.4.58 ManaRegenFn keeps the cast time); T7: mlvlT clamps the use level + tree ranks at 5 (+ the
               rebirth extra), never below the use level; outAbil caps a Deicide-sized bonus at 40
  W   wiring   bytecode: the cast calls manaCast after the Mana is subtracted; ctxFor calls costLvl; costMana reads lvlCost; equipped / ctxFor
               use mlvlT -> modCap; the two damage caps come after the Deicide / Fracture / Dead Eye adds; setup: migrate0141 -> migrateP4 -> load
  MG  migrate  migrateP4 on: the 0.1.43 jar's fresh default file (all 6 rows move, marker once, Properties check = only those keys),
               a hand-edited file (kept + noted, the others move), CRLF (kept), a fresh 0.1.44 file (nothing: the marker), a second run (nothing)
  ST  start twice on a scratch COPY of the live Skyy_SkyyClasses (every one-time update + load + the kit): start 1 moves exactly the 6
      P4 rows (History copy, one change-log line each), start 2 writes nothing
  AA  engine-access audit
NOT COVERED (UNVERIFIED in game): a real cast's Mana at Lv 40+, the refill wait in SkyySkills after a real cast.
"""
import os, sys, json, shutil, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import balance_model as BM

VERSION, OLD = "0.1.44", "0.1.43"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.58.jar")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "balp4b", "cls")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyClasses")
ADDED = []
COSTF = ["COST_LV_" + c.upper() for c in ("Archer", "Warrior", "Assassin", "Monk", "Mage", "Berserker", "Priest", "Spellblade")]
EXPECT = {
    "Abil": ["+m costLvl", "+m manaCast", "+m modCap", "~m castAt0", "~m costMana", "~m ctxFor", "~m mlvlT"],
    "AbilCtx": ["+f lvlCost", "~m copy"],
    "AbilCfg": ["+m costPct", "~<clinit>", "~m read"] + ["+f " + f for f in COSTF],
    "AbilNum": ["~<clinit>", "~m sync"],            # the Spellblade mana + the tree caps defaults
    "UpFx": ["~<clinit>"],                          # DR_CAP / DMG_CAP constants
    "ClassCfg": ["+f MGP4_KEY", "+f MGP4_MARK", "+f MGP4_MARK_ID", "+f MGP4_NEW", "+f MGP4_OLD", "+f MGP4_WHO", "+f MGP4_WHY", "+m migrateP4", "+m p4Same", "~<clinit>"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgRows1": ["~<clinit>"], "CfgRows2": ["~<clinit>"], "CfgFile": ["~<clinit>"],
    "KitMigrate": ["~m runOnce"], "SkyyClassesPlugin": ["~m setup"],
}
SB = [("ArcaneBreach", 16.0), ("ElementalImbue", 14.0), ("Sunder", 18.0), ("RiftCleave", 20.0), ("ShatteringArc", 18.0)]


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, SKILLS_JAR], verify=True)
    J = lambda n: JClass(PKG + n)
    AB, AC, AD, AN, CC, CTX, CD, MD = J("Abil"), J("AbilCfg"), J("AbilDefs"), J("AbilNum"), J("ClassCfg"), J("AbilCtx"), J("ClassDefs"), J("AbilModDefs")
    names = [str(x) for x in CD.NAMES]
    K.eq(dict((c, float(AC.costPct(names.index(c)))) for c in names), dict((c, float(BM.P4_COST_PER_LEVEL.get(c, 1.5))) for c in names),
         "X abil.costPerLevel defaults = balance_model (Mage 0, Spellblade 2.5, others 1.5)")
    K.eq(float(AC.costPct(99)), 0.0, "X costPct of an unknown class index = 0")
    AN.sync()
    for aid, m in SB:
        ai = int(AD.find(aid))
        K.eq(float(AD.mana(ai, 0)), m, "X %s walking Mana %g (spec 3.2 x2)" % (aid, m))
    K.eq((float(AN.UX_DMGCAP), float(AN.UX_DRCAP)), (40.0, 35.0), "X class tree caps: damage 40 %, cuts 35 %")
    # ---- costLvl through a fake skill:fn:level
    br = CC.bridge()
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000000144")
    LV = {"lv": 0}

    @JImplements("java.util.function.Function")
    class Lvl(object):
        @JOverride
        def apply(self, a):
            return JClass("java.lang.Integer").valueOf(LV["lv"])
    br.remove("skill:fn:level")
    war = int(AD.find("ShieldShockwave"))
    K.eq(round(float(AB.costLvl(U, war)), 6), 1.015, "X costLvl without SkyySkills = x1.015 (Abil.level answers abil.unlock.a1 = Lv 1 then)")
    br.put("skill:fn:level", Lvl())
    got = []
    for lv in (0, 40, 100):
        LV["lv"] = lv
        got.append((round(float(AB.costLvl(U, war)), 4), round(float(AB.costLvl(U, int(AD.find("ArcaneBreach")))), 4), round(float(AB.costLvl(U, int(AD.find("Meteor")))), 4)))
    K.eq(got, [(1.0, 1.0, 1.0), (1.6, 2.0, 1.0), (2.5, 3.5, 1.0)], "X costLvl Lv 0 / 40 / 100: Warrior x1 / 1.6 / 2.5, Spellblade x1 / 2 / 3.5, Mage x1")
    K.check(float(AB.costLvl(None, war)) == 1.0 and float(AB.costLvl(U, -1)) == 1.0, "X costLvl: no player / no ability = x1")
    # ---- costMana on a real AbilCtx
    c = CTX()
    c.costMult, c.costAdd = 1.0, 0.0
    w = float(AD.mana(war, 0))
    K.eq(float(AB.costMana(c, war, 0)), w, "X costMana with lvlCost 0 (an old context) = x1")
    c.lvlCost = 2.5
    c.costAdd = 2.0
    K.eq(round(float(AB.costMana(c, war, 0)), 6), round((w + 2.0) * 2.5, 6), "X costMana = (shape cost x mods + the tree's flat cost) x lvlCost")
    e = c.echoOf(0.5)
    K.eq(float(e.lvlCost), 2.5, "X echoOf keeps lvlCost")
    LV["lv"] = 40
    cx = AB.ctxFor(U, None, war, 0, "")
    K.eq(round(float(cx.lvlCost), 4), 1.6, "X ctxFor sets lvlCost from the class level (Lv 40 Warrior x1.6)")
    # ---- manaCast
    calls = []

    @JImplements("java.util.function.Function")
    class Mr(object):
        @JOverride
        def apply(self, a):
            calls.append([str(x) for x in a])
            return JClass("java.lang.Boolean").TRUE
    br.remove("skill:fn:manaregen")
    K.check(not bool(AB.manaCast(U)), "X manaCast without SkyySkills: false, nothing thrown")
    br.put("skill:fn:manaregen", Mr())
    K.check(bool(AB.manaCast(U)) and calls == [["cast", str(U)]] and not bool(AB.manaCast(None)), "X manaCast sends {\"cast\", UUID}: %s" % calls)
    br.put("skill:fn:manaregen", JClass("com.skyy.skills.ManaRegenFn")())
    CS = JClass("com.skyy.skills.ClassStat")
    K.check(bool(AB.manaCast(U)) and 0 <= int(CS.sinceCast(U, JClass("java.lang.System").currentTimeMillis())) < 5000,
            "X with the real SkyySkills 0.4.58 ManaRegenFn: TRUE, ClassStat keeps the cast time")
    # ---- T7: mlvlT clamps at 5 (+ the rebirth extra)
    P = JClass("java.util.Properties")
    mi = int(MD.find("Power"))
    aid = "ArcaneBreach"
    st = [int(x) for x in MD.steps()]
    p = P()
    p.setProperty("m.%s.%s" % (aid, str(MD.MID[mi])), str(st[-1]))   # the use level at its top (5)
    l_use = int(AB.mlvl(p, aid, mi))
    csv5 = "v3,A1,m.%s.%s=5" % (aid, str(MD.MID[mi]))
    csv2 = "v3,A1,m.%s.%s=2" % (aid, str(MD.MID[mi]))
    p0 = P()
    p0.setProperty("m.%s.%s" % (aid, str(MD.MID[mi])), "0")
    r = (l_use, int(AB.mlvlT(p, aid, mi, csv5)), int(AB.mlvlT(p0, aid, mi, csv5)), int(AB.mlvlT(p0, aid, mi, csv2)), int(AB.modCap(p, aid, mi)))
    K.eq(r, (5, 5, 5, 2, 5), "X T7: use level 5 + 5 tree ranks = 5 (was 9); 0 uses + 5 ranks = 5; 0 uses + 2 ranks = 2; the cap 5")
    p.setProperty("rb.modmax.%s.%s" % (aid, str(MD.MID[mi])), "2")
    K.eq((int(AB.modCap(p, aid, mi)), int(AB.mlvlT(p, aid, mi, csv5))), (7, 7), "X T7: + 2 rebirth extra levels -> the cap 7")
    # the Mana budget's input: tools/balance_model.py P4_ABIL = this jar's walking Mana + cooldown of every ability (the pools were fit on it)
    diff = []
    for cls_, rows_ in BM.P4_ABIL.items():
        for aid_, tier_, m_, cd_, ps_ in rows_:
            ai_ = int(AD.find(aid_))
            got_ = (names[int(AD.CLS[ai_])], round(float(AD.mana(ai_, 0)), 3), round(int(AD.cdMs(ai_, 0)) / 1000.0, 3))
            if got_ != (cls_, m_, cd_):
                diff.append((aid_, got_, (cls_, m_, cd_)))
    have = set(a_[0] for r_ in BM.P4_ABIL.values() for a_ in r_)
    left = sorted(str(x) for x in AD.IDS if str(x) not in have)
    K.check(not diff and len(have) >= 36, "X balance_model P4_ABIL = the jar's walking Mana + cooldowns (%d of %d abilities): %s" % (len(have), int(len(AD.IDS)), diff[:3]))
    K.notes.append("X not in the Mana benchmark (the second A1-alts, never owned with the first): %s" % left)
    K.save()


def run_wire(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def code(cn, mn):
        bos = BOS()
        for m in cp.get(PKG + cn).getDeclaredMethods():
            if str(m.getName()) == mn:
                IP(PS(bos)).print_(m)
        return str(bos.toString())
    c = code("Abil", "castAt0")
    K.check("Abil.manaCast" in c and c.index("subtractStatValue") < c.index("Abil.manaCast"), "W the cast (castAt0): subtractStatValue, then manaCast")
    K.check("Abil.costLvl" in code("Abil", "ctxFor") and "AbilCtx.lvlCost" in code("Abil", "costMana"), "W ctxFor -> costLvl; costMana reads lvlCost")
    K.check("Abil.modCap" in code("Abil", "mlvlT"), "W mlvlT -> modCap")
    oa, ow = code("UpFx", "outAbil"), code("UpFx", "outW")
    K.check(oa and oa.rindex("AbilNum.UX_DMGCAP") > max(oa.rindex("AbilNum.CP_DEADEYE"), oa.rindex("AbilNum.CP_GLACIALP"), oa.rindex("AbilStore.SUNDER")),
            "W UpFx.outAbil: the 40 % cap comes after Dead Eye / Glacial / Fracture (they count inside it)")
    K.check(ow and ow.rindex("AbilNum.UX_DMGCAP") > ow.rindex("UpFx.frac") and ow.rindex("AbilNum.UX_DMGCAP") < ow.rindex("AbilNum.UX_LETHAL"),
            "W UpFx.outW: the 40 % cap comes after Deicide (frac) and before Lethal (its own x1.5, spec Part 4 T4)")
    s = code("SkyyClassesPlugin", "setup")
    K.check(s.index("ClassCfg.migrate0141") < s.index("ClassCfg.migrateP4") < s.index("ClassCfg.load"), "W setup: migrate0141 -> migrateP4 -> load")
    K.save()


def run_mg(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "ClassCfg")
    Paths = JClass("java.nio.file.Paths")
    new_text = "".join(str(x) + chr(10) for x in Cfg.DEFAULT_LINES)
    old_text = open(os.path.join(scratch, "old_default.properties"), "rb").read().decode("latin-1")
    keys = [str(x) for x in Cfg.MGP4_KEY]
    olds = [str(x) for x in Cfg.MGP4_OLD]
    news = [str(x) for x in Cfg.MGP4_NEW]

    def props(t):
        pp = JClass("java.util.Properties")()
        pp.load(JClass("java.io.StringReader")(JString(t)))
        return dict((str(k), str(pp.getProperty(k))) for k in pp.stringPropertyNames())

    def run(text, name, crlf=False):
        d = os.path.join(scratch, "mg", name)
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)
        f = os.path.join(d, "config.properties")
        open(f, "wb").write((text.replace("\n", "\r\n") if crlf else text).encode("latin-1"))
        Cfg.FILE = Paths.get(f)
        r = str(Cfg.migrateP4())
        return r, open(f, "rb").read().decode("latin-1"), d
    po = props(old_text)
    K.eq([po.get(k) for k in keys], olds, "MG the 0.1.43 jar's default file holds the 6 old texts")
    r, t, d = run(old_text, "old")
    pa = props(t)
    K.check("updated to the 0.1.44 Balance P4 defaults" in r and [pa.get(k) for k in keys] == news, "MG the 0.1.43 default file: all 6 rows move: %s" % r[:160])
    K.check(dict((k, v) for k, v in pa.items() if k not in keys) == dict((k, v) for k, v in po.items() if k not in keys), "MG nothing else changed (Properties)")
    K.check(t.count(str(Cfg.MGP4_MARK_ID)) == 1 and t.index(str(Cfg.MGP4_MARK)) < t.index("ab.ArcaneBreach.numbers="), "MG the marker once, above the Arcane Breach row")
    cl = open(os.path.join(d, "config-changes.log"), encoding="latin-1").read() if os.path.isfile(os.path.join(d, "config-changes.log")) else ""
    K.check(cl.count("SkyyClasses 0.1.44") == 6 and os.path.isdir(os.path.join(d, "config-history")), "MG one change-log line per row (6) + the History copy")
    r2 = str(Cfg.migrateP4())
    K.eq(r2, "", "MG a second run: nothing (the marker)")
    hand = old_text.replace("ab.ClassTree.numbers=" + olds[-1], "ab.ClassTree.numbers=" + olds[-1].replace("drCap=50", "drCap=45"))
    assert hand != old_text
    r, t, d = run(hand, "hand")
    ph = props(t)
    K.check(ph["ab.ClassTree.numbers"].startswith("drCap=45,dmgCap=80,") and "ab.ClassTree.numbers=" in r and "kept" in r
            and [ph.get(k) for k in keys[:5]] == news[:5], "MG a hand-edited class tree row is kept + noted, the 5 Spellblade rows move")
    r, t, d = run(old_text, "crlf", crlf=True)
    K.check("updated" in r and t.count("\r\n") == t.count("\n") and [props(t).get(k) for k in keys] == news, "MG CRLF: moved, every line ending kept")
    if new_text:
        r, t, d = run(new_text, "fresh")
        K.eq(r, "", "MG a fresh 0.1.44 file: nothing (it carries the marker)")
    K.save()


def dump_old_default(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, OLD_JAR], verify=False)
    t = "".join(str(x) + chr(10) for x in JClass(PKG + "ClassCfg").DEFAULT_LINES)
    open(os.path.join(scratch, "old_default.properties"), "wb").write(t.encode("latin-1"))
    K.check(len(t) > 1000, "MG0 the 0.1.43 default config.properties read (%d chars)" % len(t))
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Pub, AS = JClass(PKG + "ClassCfg"), JClass(PKG + "CfgPub"), JClass(PKG + "AbilStore")
    Paths = JClass("java.nio.file.Paths")
    home = os.path.join(scratch, "st", "mods")
    base = os.path.join(home, "Skyy_SkyyClasses")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "m41": str(Cfg.migrate0141()),
         "p4": str(Cfg.migrateP4()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if step == "1":
        K.notes.append("ST start 1: %s" % o["p4"][:400])
        txt = open(os.path.join(base, "config.properties"), encoding="latin-1").read()
        lines = [l.rstrip("\r") for l in txt.split("\n")]
        livep = open(os.path.join(LIVE, "config.properties"), encoding="latin-1").read().replace("\r", "").split("\n")
        had = [str(k) for k in Cfg.MGP4_KEY if any(l.startswith(str(k) + "=") for l in livep)]
        moved = [str(k) for k, n in zip(Cfg.MGP4_KEY, Cfg.MGP4_NEW) if ("%s=%s" % (str(k), str(n))) in lines]
        K.check(all(k in ("config.properties", "config-changes.log") or k.startswith("config-history/") for k in ch)
                and o["p4"].startswith("config.properties updated to the 0.1.44 Balance P4 defaults"),
                "ST start 1 on a scratch COPY of the live data: the P4 update ran (%s): %s" % (ch, o["p4"][:160]))
        K.eq(moved, had, "ST start 1: every P4 row the live file has moved (%d; a row it lacks reads the new default)" % len(had))
        K.notes.append("ST the live file lacks %s (absent = the 0.1.44 default)" % [str(k) for k in Cfg.MGP4_KEY if str(k) not in had])
    else:
        K.check(not ch and o["p4"] == "" and o["m41"] == "", "ST start 2: nothing written (%s)" % ch)
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("wire", run_wire), ("mg0", dump_old_default), ("mg", run_mg), ("st1", run_st1), ("st2", run_st2)], script=__file__)
