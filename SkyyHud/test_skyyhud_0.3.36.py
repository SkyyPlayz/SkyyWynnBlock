"""SkyyHud 0.3.36 harness - the HUD Farming line = crop Farming level (tools/hud_0_3_36_patch.py). Built on tools/harness_kit.py: each phase a
fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder).

    python SkyyHud/test_skyyhud_0.3.36.py [--jar SkyyHud-0.3.36.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.35 -> 0.3.36: exactly the listed classes / members differ
  K36  EXECUTED on the real jar classes: Widgets.farmVal + skillsModelU / skillsModelX with a skill:farmavg key that must be IGNORED:
       Farming line alone -> "16 (R 1 / O 0)"; + Ranching line -> "16 (O 0)"; + Orchard line -> "16 (R 1)"; all three -> "16"; a skill
       not published leaves the bracket; no Farming entry -> "-"; the headline; HudMain.build + fill of a real layout send "16 (R 1 / O 0)"
       and never the average; a level-up = one value set, no re-send
  LIVE twice on a scratch COPY of the live Skyy_SkyyHud (NewBetaTest): nothing written either time, every saved line loads as saved
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the look of the line on the real HUD.
Scratch: tools/dev/scratch/hud036/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import harness_kit as HK
import skyybuild as B

VERSION, PREV = "0.3.36", "0.3.35"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD = os.path.join(HERE, "SkyyHud-%s.jar" % PREV)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud036", "h")))
PKG = "com.skyy.hud."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyHud")
FARM, RANCH, ORCH, MINING = 1 << 4, 1 << 11, 1 << 12, 1 << 2


def run_k36(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    UUID, System, CHM, Paths = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.nio.file.Paths")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        k = cls.class_ if hasattr(cls, "class_") else cls
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                f.set(obj, val)
                return
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)
    H = lambda n: JClass(PKG + n)
    Wid, LS, HM, Cfg, HT = H("Widgets"), H("LayoutStore"), H("HudMain"), H("HudCfg"), H("HudThreads")
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(scratch, "k")
    os.makedirs(os.path.join(work, "cfg"), exist_ok=True)
    os.makedirs(os.path.join(work, "layouts"), exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(work, "cfg", "config.properties"))
    Cfg.load()
    HT.EXEC = None
    LS.DIR = Paths.get(os.path.join(work, "layouts"))
    LS.CACHE.clear()
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    mFill = HM.class_.getDeclaredMethod("fill", UCB.class_, JClass("boolean"))
    mFill.setAccessible(True)
    allc = lambda b: " ".join(str(c.text or "") + " " + str(c.data or "") for c in b.getCommands())

    pr = U.allocateInstance(PRef.class_)
    u = UUID(0x336, 1)
    setf(pr, PRef, "uuid", u)
    setf(pr, PRef, "username", "Skyy")
    us = str(u)
    bridge.put("skill:fn:level", JClass("java.lang.Object")())
    bridge.put("skill:" + us, "Mining:3,Foraging:2,Farming:16,Alchemy:0,Fishing:4,Ranching:1,Orchard:0")
    bridge.put("skill:farmavg:" + us, "5")      # SkyySkills still publishes the average - 0.3.36 must ignore it
    bridge.put("skill:overall:" + us, "9")

    P = lambda parts, vis: str(Wid.farmVal(None if parts is None else JArray(JString)(parts), vis))
    pp = ["Mining:3", "Farming:16", "Ranching:1", "Orchard:0"]
    K.eq(P(pp, FARM), "16 (R 1 / O 0)", "FARM: Farming line alone -> crop level + R / O bracket")
    K.eq(P(pp, FARM | RANCH), "16 (O 0)", "FARM: Ranching on its own line leaves the bracket")
    K.eq(P(pp, FARM | ORCH), "16 (R 1)", "FARM: Orchard on its own line leaves the bracket")
    K.eq(P(pp, FARM | RANCH | ORCH), "16", "FARM: both own lines on -> the plain crop level")
    K.eq(P(["Farming:16", "Orchard:7"], FARM), "16 (O 7)", "FARM: Ranching not published -> left out")
    K.eq(P(["Farming:16"], FARM), "16", "FARM: neither published -> plain")
    K.eq(P(["Mining:3", "Ranching:1"], FARM), "- (R 1)", "FARM: no Farming entry -> '-'")
    K.eq(P(None, FARM), "-", "FARM: no skill data -> '-'")

    def lines(mask, x=False):
        m = Wid.skillsModelX(u, mask, True) if x else Wid.skillsModelU(u, mask)
        n = int(str(m[0])[1:]) if str(m[0]).startswith("K") and str(m[0]) != "K0" else 0
        return str(m[0]), (None if m[1] is None else str(m[1])), [(str(m[2 + 2 * i]), str(m[3 + 2 * i])) for i in range(n)]
    s, hl, ln = lines(FARM)
    K.eq((s, hl, ln), ("K1", "Farming 16 (R 1 / O 0)", [("Farming", "16 (R 1 / O 0)")]), "MODEL: Farming only -> 'Farming 16 (R 1 / O 0)' (farmavg 5 ignored)")
    s, hl, ln = lines(FARM | RANCH | ORCH | MINING)
    K.eq(ln, [("Mining", "3"), ("Farming", "16"), ("Ranching", "1"), ("Orchard", "0")], "MODEL: Mining + Farming + Ranching + Orchard lines")
    s, hl, ln = lines(FARM | RANCH)
    K.eq(ln, [("Farming", "16 (O 0)"), ("Ranching", "1")], "MODEL: Farming + Ranching")
    s, hl, ln = lines(FARM | 1, True)
    K.eq(ln, [("Overall Level", "9"), ("Farming", "16 (R 1 / O 0)")], "MODEL: skillsModelX (the HUD path) Overall + Farming")
    s, hl, ln = lines(3)
    K.check(not any("(" in v for _n, v in ln), "MODEL: the default mask (Overall + Class) has no Farming bracket: %s" % ln)

    # a real HUD: the Skills widget with the Farming line, build + the 1 s fill
    mp = LS.get(u)
    sk = mp.get("Skills")
    sk.en = True
    sk.lines = FARM | 1
    h = HM(pr)
    b = UCB()
    mBuild.invoke(h, b)
    t1 = allc(b)
    b2 = UCB()
    mFill.invoke(h, b2, False)
    t2 = allc(b2)
    K.check("16 (R 1 / O 0)" in t1 + t2 and "(F 16" not in t1 + t2 and "5 (F" not in t1 + t2,
            "HUD: build + fill send 'Farming 16 (R 1 / O 0)', never the average: shape %s" % h.shape.get("Skills"))
    bridge.put("skill:" + us, "Mining:3,Farming:17,Ranching:1,Orchard:0")
    b3 = UCB()
    re_ = bool(mFill.invoke(h, b3, False))
    K.check(not re_ and "17 (R 1 / O 0)" in allc(b3), "HUD: a Farming level-up = one value set, no re-send (shape unchanged)")
    sk.lines = FARM | RANCH | ORCH | 1
    h = HM(pr)
    b = UCB()
    mBuild.invoke(h, b)
    b2 = UCB()
    mFill.invoke(h, b2, False)
    t = allc(b) + allc(b2)
    K.check("(R " not in t and "(O " not in t and "16" in t, "HUD: Ranching + Orchard on their own lines -> no bracket, plain 16: %s" % [x for x in t.split("  ") if "16" in x or "(R" in x][:4])
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    LS, Cfg, Pub, Wid = P("LayoutStore"), P("HudCfg"), P("CfgPub"), P("Widgets")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    mods = os.path.dirname(home)
    lyd = os.path.join(home, "layouts")
    players = [f[:-11] for f in sorted(os.listdir(lyd)) if f.endswith(".properties")] if os.path.isdir(lyd) else []
    res = []
    for _n in range(2):
        b0 = HK.tree_hash(mods)
        LS.CACHE.clear()
        LS.DIR = Paths.get(lyd)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        Wid.HUBFILE = Paths.get(os.path.join(mods, "Skyy_SkyyIslands", "hub.properties"))
        Cfg.load()
        Pub.start(Paths.get(mods), None)
        r_ = {}
        for us in players:
            mp = LS.get(UUID.fromString(us))
            r_[us] = dict((str(w_), str(mp.get(w_).ser())) for w_ in Wid.IDS)
        Pub.flush()
        a0 = HK.tree_hash(mods)
        res.append((r_, sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k))))
    K.check(res[0][1] == [] and res[1][1] == [] and res[0][0] == res[1][0],
            "LIVE: two starts on a COPY of the live Skyy_SkyyHud (%d layouts): nothing written, the same layouts: %s" % (len(players), [r[1] for r in res]))
    bad, folded = [], []
    for us in players:
        fl = {}
        for ln in open(os.path.join(lyd, us + ".properties"), encoding="latin-1"):
            if "=" in ln and not ln.startswith("#"):
                k_, v_ = ln.strip().split("=", 1)
                fl[k_] = v_
        r_ = res[0][0][us]
        if not all(r_[w_] == fl[w_] for w_ in r_ if w_ in fl):
            bad.append(us[:8])
        mp = LS.get(UUID.fromString(us))
        if not bool(mp.get("Quest").opt):
            folded.append(us[:8])
        kk = mp.get("Keys")
        K.notes.append("LIVE: player %s...: Keys at %s %d,%d (saved Keys line: %s)" % (us[:8], kk.anchor, kk.dx, kk.dy, "Keys" in fl))
    K.check(not bad, "LIVE: every saved line of every live layout loads exactly as saved (%d players): %s" % (len(players), bad))
    K.check(not folded, "LIVE: every live Quest tracker loads OPEN (no old line reads as folded): %s" % folded)
    K.check(len(players) >= 1, "LIVE: the copy has layouts (%d)" % len(players))
    K.save()


EXPECT = {
    "Widgets": ["-m farmVal", "+m farmVal", "~m skillsModelU"],   # the crop Farming level + the R / O bracket (farmVal's parameters changed)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],   # the config kit's version text
    "SkyyHudPlugin": ["~m setup"],                 # the '[SkyyHud] 0.3.36 ready' version text
}
if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD, PKG, SCRATCH, EXPECT, [], [("k36", run_k36), ("live", run_live)], os.path.abspath(__file__),
           live=(LIVE_DIR, "Skyy_SkyyHud"))
