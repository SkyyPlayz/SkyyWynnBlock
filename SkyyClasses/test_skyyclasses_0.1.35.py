"""Harness for SkyyClasses 0.1.35 (the waiting class-tree nodes: Priest PA2 Radiant Pulse, Priest PB2 Elemental Bubble, Mage PC2 Siphon;
tools/classes_0_1_35_patch.py; round trees21 with SkyyTrees 0.3.21). Build first:
    python tools/classes_0_1_35_patch.py && python SkyyClasses/build_skyyclasses_0.1.35.py
    python SkyyClasses/test_skyyclasses_0.1.35.py [--keep]
Phases (tools/harness_kit.py, fresh child JVMs, -Xverify:all, TEMP / TMP in tools/dev/scratch/trees21/cls):
  A   verify   every class loads + initialises
  C   compare  0.1.34 -> 0.1.35: exactly the planned members (EXPECT)
  BR  the reader list (tree:reads:SkyyClasses text in the jar) names Priest PA2 + PB2 and Mage PC2, not Mage PA4
  X   exec     on the engine stand-ins of test_skyyclasses_0.1.25.py (its N0 set-up, executed from that file):
               X1 RADIANT PULSE: Sacred Heal with PA2 = +3 s cooldown, a second heal job 2 s later (a pulse, 50 %), it heals half the
                  first heal and says "Radiant Pulse:", never pulses again; without the node: none
               X2 ELEMENTAL BUBBLE: the pick (Fire first, Change cycles, refused without the node / in combat / class trees off), the
                  panel's element line (o[111] the bubble row, o[129] the text), the first bubble LOCKS it, locked = refused, thorns put
                  the element's status on the attacker (Earth = Stagger, Fire = Burn), without PB2 plain thorns, a respec frees it
               X3 SIPHON: a mob killed by the Mage (weapon or ability hit) = +3 Mana once; alive / no node / another class / class trees
                  off = nothing; the cast and the panel turn the hook on; AbilFrostSys calls it (bytecode)
  ST1 / ST2  START TWICE on a scratch COPY of the live Skyy_SkyyClasses folder (setup's order): nothing written; the live folder only read
  AA  engine-access audit
"""
import os, sys, json, shutil, zipfile, hashlib, textwrap, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import deploy_set as DS
import perfworld_kit as PW

VERSION, OLD = "0.1.35", "0.1.34"
JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
PKG = "com.skyy.classes."
SCRATCH = os.path.join(TOOLS, "dev", "scratch", "trees21", "cls")
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyClasses")
T25 = os.path.join(HERE, "test_skyyclasses_0.1.25.py")
ADDED = []
EXPECT = {
    "Abil": ["+f BUBELEMS", "+f PULSES", "+f SIPH", "+f SIPHONS", "+f SIPH_ON", "+m bubCast", "+m bubFree", "+m bubLocked", "+m bubOf", "+m bubPick",
             "+m bubStatus", "+m bubText", "+m pulseJob", "+m siphonHit", "~<clinit>", "~m attune", "~m bubbleAt", "~m healAt", "~m healCast",
             "~m panel", "~m thorns", "~m treeApply", "+m foe", "+m siphPrune", "~m pruneMobs"],
    "AbilCtx": ["+f pulse"],                       # a Radiant Pulse heal
    "AbilFrostSys": ["~m handle"],                 # + siphonHit
    "SkyyClassesPlugin": ["~m setup"],             # the reader list (tree:reads:SkyyClasses) + the version text
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "KitMigrate": ["~m runOnce"],          # the version text only
}


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_exec(out, jar, scratch, _home):
    stats_zip = os.path.join(scratch, "stats.zip")
    with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as zi, \
            zipfile.ZipFile(stats_zip, "w") as zo:
        for n in zi.namelist():
            if n.startswith("Server/Entity/Stats/") and n.endswith(".json"):
                zo.writestr(n, zi.read(n))
    lines = open(T25, encoding="utf8").read().split("\n")
    a = lines.index("def run_exec(out, jar, scratch, _home):") + 1
    b = [i for i, l in enumerate(lines) if l.strip() == "# ---------------- X1 the pure rules"][0]
    ns = {"out": out, "jar": jar, "scratch": scratch, "_home": _home, "HK": HK, "B": B, "PKG": PKG, "ASSETS": stats_zip, "os": os, "sys": sys,
          "json": json, "shutil": shutil, "zipfile": zipfile, "time": time, "__name__": "t25setup"}
    exec(compile(textwrap.dedent("\n".join(lines[a:b])), T25 + " (N0 set-up)", "exec"), ns)
    g = lambda n: ns[n]
    K, C, ck = g("K"), g("C"), g("ck")
    from jpype import JClass, JArray, JString, JFloat, JLong
    A, AS, AD, AW, Defs, Cfg = g("A"), g("AS"), g("AD"), g("AW"), g("Defs"), g("Cfg")
    tst, tbuf, world, TBf, tick = g("tst"), g("tbuf"), g("world"), g("TBf"), g("tick")
    npc, put, said, unthrottle, cast, mana = g("npc"), g("put"), g("said"), g("unthrottle"), g("cast"), g("mana")
    MANA, HP, TREE, COMBAT = g("MANA"), g("HP"), g("TREE"), g("COMBAT")
    mu, mr, mpr, mm = g("mu"), g("mr"), g("mpr"), g("mm")
    pu, pr_r, ppr, pm = g("pu"), g("pr_r"), g("ppr"), g("pm")
    ci_m, ci_p, SACRED, METEOR = g("ci_m"), g("ci_p"), g("SACRED"), g("METEOR")
    ID = g("ID")
    BUBBLE = ID["ShieldBubble"]
    now_ms = lambda: int(time.time() * 1000)
    aw = AW.of("abil-test")
    DENTc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage$EntitySource")
    Dm_ = JClass("com.hypixel.hytale.server.core.modules.entity.damage.Damage")
    DCSc = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DamageCause")
    kP, kM = str(Cfg.pkey(pu)), str(Cfg.pkey(mu))

    def dmg(src, amt):
        return Dm_(DENTc(src), DCSc.PROJECTILE, JFloat(amt))

    def tree(csv):
        TREE["csv"] = csv
        AS.TREEC.clear()

    def setp(k__, kv):
        AS.set(k__, JArray(JString)(list(kv.keys())), JArray(JString)([None if v is None else str(v) for v in kv.values()]))

    def preset():
        AS.clearCd(kP)
        mana(pm, 400.0)
        unthrottle()
        said()
        AS.LASTUSE.clear()
        aw.jobs.clear()
        for z_ in list(aw.zoneArr()):
            aw.dropZone(z_)
        TBf.EVENTS.clear()

    sl_p = [str(x) for x in AS.slots(kP, ci_p)]
    hkey, bkey = str(sl_p.index("SacredHeal") + 1), str(sl_p.index("ShieldBubble") + 1)
    BASE = "A1,A2,A3,A4a,A4b"
    # ================================================================ X1 RADIANT PULSE
    ck(int(A.ctxFor(pu, kP, SACRED, 0, BASE + ",PA2").cdAdd) - int(A.ctxFor(pu, kP, SACRED, 0, BASE).cdAdd) == 3000,
       "X1: Radiant Pulse - Sacred Heal's cooldown +3 s")
    preset()
    tree(BASE + ",PA2")
    pm.setStatValue(HP, JFloat(10.0))
    h0 = float(pm.get(HP).get())
    r_ = cast("Priest1", hkey)
    h1 = float(pm.get(HP).get())
    first = h1 - h0
    pj = [j for j in list(aw.jobs) if int(j.kind) == 10 and int(j.ai) == SACRED]
    ck(r_.startswith("ok:SacredHeal") and first > 0.0 and len(pj) == 1 and bool(pj[0].cx.pulse) and bool(pj[0].cx.echo)
       and 1900 <= int(pj[0].at) - now_ms() <= 2000, "X1: the cast heals (+%.2f) and queues ONE pulse 2 s later (%s)" % (first, r_))
    ck(abs(float(pj[0].cx.main) / float(A.ctxFor(pu, kP, SACRED, 0, BASE + ",PA2").main) - 0.5) < 1e-9 if pj else False,
       "X1: the pulse works at 50 % of the main heal")
    for j in list(aw.jobs):
        j.at = JLong(now_ms() + 600000)
    if pj:
        pj[0].at = JLong(now_ms() - 10)
    said()
    pm.setStatValue(HP, JFloat(10.0))
    aw.lastNs = 0
    tick.tick(JFloat(0.05), 0, None, tst, tbuf)
    second = float(pm.get(HP).get()) - 10.0
    sd = said()
    ck(abs(second - first * 0.5) < 0.02 and any(x.startswith("Radiant Pulse: ") for x in sd), "X1: the pulse heals half (+%.2f of +%.2f) and says so: %s" % (second, first, sd[-1:]))
    ck(not [j for j in list(aw.jobs) if int(j.kind) == 10 and int(j.ai) == SACRED and int(j.at) < now_ms() + 300000],
       "X1: the pulse never pulses again (no new pulse / echo job)")
    preset()
    tree(BASE)
    cast("Priest1", hkey)
    ck(not [j for j in list(aw.jobs) if int(j.kind) == 10 and int(j.ai) == SACRED], "X1: without the node: no pulse")
    # ================================================================ X2 ELEMENTAL BUBBLE
    preset()
    setp(kP, {"bub.el": None, "bub.lock": None})
    csvE = BASE + ",PB1,PB2"
    tree(csvE)
    ck(str(A.bubText(kP)).startswith("Bubble element: Fire (Burn) - Change picks"), "X2: Fire until picked: %s" % A.bubText(kP))
    r1, r2 = str(A.bubPick(pu, csvE)), str(A.bubPick(pu, csvE))
    ck(r1.startswith("+Elemental Bubble: Water (Chill)") and r2.startswith("+Elemental Bubble: Earth (Stagger)") and int(A.bubOf(kP)) == 2,
       "X2: Change cycles Fire -> Water -> Earth (%s / %s)" % (r1, r2))
    ck(str(A.bubPick(pu, BASE + ",PB1")).startswith("-The bubble element comes with Elemental Bubble"), "X2: refused without the node")
    COMBAT[str(pu)] = 5000
    ck(str(A.bubPick(pu, csvE)).startswith("-Leave combat first"), "X2: refused in combat")
    COMBAT.pop(str(pu), None)
    tree(None)
    ck(str(A.bubPick(pu, None)).startswith("-The bubble element comes with"), "X2: class trees off (no tree list) = refused")
    tree(csvE)
    ck(str(A.doAction(pu, "attune", "next", "1", csvE)).startswith("+Elemental Bubble: Lightning"), "X2: the Lattice's Change (class:fn:abilDo attune) picks for a Priest")
    A.bubPick(pu, csvE)
    A.bubPick(pu, csvE)
    A.bubPick(pu, csvE)   # Lightning -> Wind -> Fire -> Water
    A.bubPick(pu, csvE)   # -> Earth
    ck(int(A.bubOf(kP)) == 2, "X2: back on Earth")
    o = A.panel(pu, csvE, True)
    ck(len(o) == 130 and int(o[111]) == sl_p.index("ShieldBubble") and str(o[112]) == "Earth" and str(o[129]).startswith("Bubble element: Earth (Stagger) - Change picks"),
       "X2: the panel - o[111] = the bubble's row, o[112] Earth, o[129] the line: %s" % o[129])
    o2 = A.panel(pu, BASE + ",PB1", True)
    ck(int(o2[111]) == -1 and str(o2[129]) == "", "X2: the panel without the node: no element row")
    om = A.panel(mu, "A1", True)
    ck(str(om[129]) == "" and int(om[111]) == -1, "X2: a Mage's panel has no element line")
    preset()
    tree(csvE)
    r_ = cast("Priest1", bkey)
    sd = said()
    bz = [z_ for z_ in list(aw.zoneArr()) if int(z_.kind) == 2 and str(z_.caster) == str(pu)]
    ck(r_.startswith("ok:ShieldBubble") and len(bz) == 1 and bool(A.bubLocked(kP)) and any("Elemental: Earth (Stagger) - now locked" in x for x in sd),
       "X2: the first bubble with the node LOCKS the element (%s)" % sd[-1:])
    ck(str(A.bubPick(pu, csvE)).startswith("-Your bubble element is Earth - it is locked") and str(A.bubText(kP)).endswith("locked, a class respec frees it"),
       "X2: locked = Change refused; the line says a respec frees it")
    mob = npc(951, 3.5, 64.0, 1.5, hp=200.0)
    AS.STAGD.clear()
    ok_ = bool(A.thorns(tbuf, bz[0], dmg(mob, 10.0))) if bz else False
    ck(ok_ and TBf.EVENTS.size() >= 1 and AS.STAGD.get(mob) is not None and int(A.BUBELEMS) >= 1,
       "X2: Thorned Bubble's hit + the element's status on the attacker (Earth = Stagger)")
    bz[0].cx.tree = JString(BASE + ",PB1")
    AS.STAGD.clear()
    TBf.EVENTS.clear()
    ok2 = bool(A.thorns(tbuf, bz[0], dmg(mob, 10.0)))
    ck(ok2 and TBf.EVENTS.size() == 1 and AS.STAGD.get(mob) is None, "X2: a bubble cast without PB2: plain thorns, no element")
    A.panel(pu, BASE + ",PB1", True)   # the tree list without PB2 = a respec
    ck(not bool(A.bubLocked(kP)) and int(A.bubOf(kP)) == 2, "X2: a respec (the list without PB2) frees the pick; the element stays as the start")
    A.panel(pu, None, True)
    ck(str(A.bubPick(pu, csvE)).startswith("+Elemental Bubble: Lightning"), "X2: after the respec Change works again")
    A.bubPick(pu, csvE)
    A.bubPick(pu, csvE)   # Wind -> Fire
    preset()
    tree(csvE)
    cast("Priest1", bkey)
    bz = [z_ for z_ in list(aw.zoneArr()) if int(z_.kind) == 2 and str(z_.caster) == str(pu)]
    AS.DOTS.clear()
    A.thorns(tbuf, bz[0], dmg(mob, 10.0))
    ck(bool(A.bubLocked(kP)) and int(A.bubOf(kP)) == 0 and AS.DOTS.get(mob) is not None, "X2: re-picked Fire, locked by the next bubble, thorns Burn the attacker")
    rf = str(A.bubPick(pu, BASE + ",PB1"))
    ck(rf.startswith("-The bubble element comes with") and not bool(A.bubLocked(kP)), "X2 (fix): Change after a respec frees the lock (no panel needed)")
    preset()
    tree(csvE)
    cast("Priest1", bkey)
    ck(bool(A.bubLocked(kP)), "X2 (fix): locked again by a bubble")
    preset()
    tree(BASE)
    cast("Priest1", hkey)
    ck(not bool(A.bubLocked(kP)), "X2 (fix): any Priest cast after a respec (no PB2 in the list) frees it")
    preset()
    tree(csvE)
    cast("Priest1", bkey)
    preset()
    tree(BASE + ",PB1")
    cast("Priest1", bkey)
    ck(not bool(A.bubLocked(kP)), "X2 (fix): a bubble cast after a respec frees it")
    preset()
    setp(kP, {"bub.el": None, "bub.lock": None})
    # ================================================================ X3 SIPHON
    tree("A1,PC2")
    A.SIPH_ON = False
    A.ctxFor(mu, kM, METEOR, 0, "A1,PC2")
    ck(bool(A.SIPH_ON), "X3: a Mage cast with Siphon turns the kill hook on")
    A.SIPH_ON = False
    A.panel(mu, "A1,PC2", True)
    ck(bool(A.SIPH_ON), "X3: ... and so does the class tree panel")
    A.SIPH.clear()
    dead = npc(961, 1.5, 64.0, 1.5, hp=0.0)
    alive_ = npc(962, 1.5, 64.0, 2.5, hp=100.0)
    mm.setStatValue(MANA, JFloat(100.0))
    s1 = A.siphonHit(tbuf, dead, dmg(mr, 5.0), JLong(now_ms()))
    m1 = float(mm.get(MANA).get())
    ck(str(s1) == "siphon" and abs(m1 - 103.0) < 1e-6, "X3: a mob the Mage killed = +3 Mana (%s, %.1f)" % (s1, m1))
    s2 = A.siphonHit(tbuf, dead, dmg(mr, 5.0), JLong(now_ms()))
    ck(s2 is None and abs(float(mm.get(MANA).get()) - 103.0) < 1e-6, "X3: the same mob again = nothing (once per mob)")
    ck(A.siphonHit(tbuf, alive_, dmg(mr, 5.0), JLong(now_ms())) is None, "X3: a mob still alive = nothing")
    d_ab = dmg(mr, 5.0)
    C("AbilDmg").tag(d_ab, mu, "Meteor")
    dead2 = npc(963, 1.5, 64.0, 3.5, hp=0.0)
    ck(str(A.siphonHit(tbuf, dead2, d_ab, JLong(now_ms()))) == "siphon" and abs(float(mm.get(MANA).get()) - 106.0) < 1e-6, "X3: an ABILITY kill counts too")
    dead3 = npc(964, 1.5, 64.0, 4.5, hp=0.0)
    tree("A1")
    ck(A.siphonHit(tbuf, dead3, dmg(mr, 5.0), JLong(now_ms())) is None, "X3: without the node = nothing")
    tree(None)
    ck(A.siphonHit(tbuf, dead3, dmg(mr, 5.0), JLong(now_ms())) is None, "X3: class trees off = nothing")
    tree("A1,PC2")
    ck(A.siphonHit(tbuf, dead3, dmg(pr_r, 5.0), JLong(now_ms())) is None, "X3: a Priest's kill = nothing (Mage only)")
    ck(abs(float(mm.get(MANA).get()) - 106.0) < 1e-6, "X3: Mana unchanged by the refused kills")
    INVUc = JClass("com.hypixel.hytale.server.core.modules.entity.component.Invulnerable")
    dead4 = npc(965, 1.5, 64.0, 5.5, hp=0.0, invu=True)
    ck(A.siphonHit(tbuf, dead4, dmg(mr, 5.0), JLong(now_ms())) is None, "X3 (fix): a non-hostile (invulnerable) NPC gives nothing")
    A.SIPH_ON = False
    dead5 = npc(966, 1.5, 64.0, 6.5, hp=0.0)
    ck(str(A.siphonHit(tbuf, dead5, dmg(mr, 5.0), JLong(now_ms()))) == "siphon", "X3 (fix): no cast / panel since the start (SIPH_ON off) - a weapon kill still counts")
    n0 = A.SIPH.size()
    A.siphPrune(JLong(now_ms() + 31000))
    ck(n0 >= 3 and A.SIPH.size() == 0, "X3 (fix): the once-per-mob map is pruned by time (%d -> %d)" % (n0, A.SIPH.size()))
    ck(PKG + "Abil.siphPrune" in PW.calls(jar).get("Abil.pruneMobs", set()), "X3 (fix): pruneMobs (the 1 s timer) prunes it (bytecode)")
    tree(None)
    gr = PW.calls(jar)
    ck(PKG + "Abil.siphonHit" in gr.get("AbilFrostSys.handle", set()), "X3: AbilFrostSys (the landed-hit hook) calls siphonHit (bytecode)")
    ck(PKG + "Abil.bubStatus" in gr.get("Abil.thorns", set()) and PKG + "Abil.pulseJob" in gr.get("Abil.healAt", set())
       and PKG + "Abil.bubPick" in gr.get("Abil.attune", set()) and PKG + "Abil.bubCast" in gr.get("Abil.bubbleAt", set()),
       "X: thorns -> bubStatus, healAt -> pulseJob, attune -> bubPick, bubbleAt -> bubCast (bytecode)")
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
    o = {"m10": str(Cfg.migrate0110()), "m29": str(Cfg.migrate0129()), "m32": str(Cfg.migrate0132()), "load": str(Cfg.load())}
    AS.DIR = Paths.get(os.path.join(base, "abilities"))
    Pub.start(Paths.get(home), None)
    Pub.flush()
    Pub.shutdown()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    K.check(not ch and o["m32"] == "", "ST start %s on a scratch COPY of the live data: nothing written (%s)" % (step, ch))
    if step == "2":
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyClasses folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


def reads_text(j):
    sys.path.insert(0, os.path.join(TOOLS, "dev"))
    from cpstrings import read_utf8_constants
    out = set()
    with zipfile.ZipFile(j) as z:
        for n in z.namelist():
            if n.endswith(".class"):
                out |= set(s for s in read_utf8_constants(z.read(n)) if "Class.Mage.A1" in s)
    return out


if __name__ == "__main__":
    if "--phase" not in sys.argv:
        rt = reads_text(JAR)
        rs = [s for s in rt if "Class.Priest." in s]
        ok = len(rs) == 1 and all(("Class.%s," % x) in rs[0] + "," for x in ("Priest.PA2", "Priest.PB2", "Mage.PC2")) and "Class.Mage.PA4," not in rs[0] + ","
        HK.check(ok, "BR: tree:reads:SkyyClasses lists Priest PA2 + PB2 and Mage PC2, not Mage PA4")
        old = [s for s in reads_text(OLD_JAR) if "Class.Priest." in s]
        HK.check(len(old) == 1 and set(rs[0].split(",")) - set(old[0].split(",")) == {"Class.Priest.PA2", "Class.Priest.PB2", "Class.Mage.PC2"},
                 "BR: exactly those three are new (%s)" % sorted(set(rs[0].split(",")) - set(old[0].split(","))) if rs and old else "BR: the reader text")
        print("BR. reader list: + %s" % (sorted(set(rs[0].split(",")) - set(old[0].split(","))) if rs and old else "?"))
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("st1", run_st1), ("st2", run_st2)], script=__file__)
