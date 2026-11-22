"""SkyySkills 0.4.73 - harness for COMBAT CLICKER CLASS XP (tools/skills_0_4_73_patch.py). Build first:
    python tools/skills_0_4_73_patch.py && python SkyySkills/build_skyyskills_0.4.73.py
    python SkyySkills/test_skyyskills_0.4.73.py [--keep]
Phases (each a fresh child JVM: -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes, 0.4.72's patch still regenerates 0.4.72, line endings kept, no class / system / command added,
                 below the docstring the script = 0.4.72 except VERSION, ShardLead.classSlot (+ 2 counters) and SkillAddFn.apply
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.4.72 -> 0.4.73: exactly ShardLead (+classSlot, +CLS_OK, +CLS_NO, <clinit>) + SkillAddFn.apply + the VERSION texts
  CX    EXECUTED skill:fn:addxp -> SkillAddFn -> ShardLead.classSlot -> BridgeXp.offerX on a stand-in Universe / PlayerRef / World (the 0.4.70 PATH
                 rig): the Combat shard's class XP for the CURRENT class is queued ONCE per call (one BridgeTask = one kill), = paidY(cls false) =
                 the shard XP rules without a second class multiplier; the name SkyySkills' own skill:fn:run "class" answers (what SkyyShards sends)
                 works for every class (Monk = Combat.Shaman); no class / another class / class change / profile switch (profile:class differs) /
                 another profile key / offline / a non-Combat shard source / a non-shard source / a prefix name / the legacy Combat slot = FALSE,
                 nothing queued; ordinary grants (Mining) unchanged; counters
  FO / PR / SH / HL / PK   the 0.4.72 / 0.4.71 / 0.4.70 cases on THIS jar (regression)
  LIVE  start twice on a scratch COPY of the live Skyy_SkyySkills: no file changes at all; the live Skyy_SkyyShards files (read only) hold no
        owed class XP (owed.xp.Combat.*) - the backlog the round could pay is empty
  AA    engine-access audit
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "clsxp1", "sk")]
_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T72 = _mod(os.path.join(HERE, "test_skyyskills_0.4.72.py"), "test_skyyskills_0_4_72")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T71, T70 = T72.T71, T72.T70
T67, T53 = T70.T67, T70.T53
VERSION = "0.4.73"
PKG = "com.skyy.skills."
GEN = os.path.join(HERE, "build_skyyskills_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyskills_0.4.72.py")
PATCH = os.path.join(TOOLS, "skills_0_4_73_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.72.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T70.LIVE_DIR
ADDED = []
EXPECT = {   # THE changes: ShardLead.classSlot + 2 counters, SkillAddFn.apply; the rest = the VERSION text those members embed (as 0.4.72)
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CurveP9Mig': ['~m run'],
    'ManaGuard': ['~m armReport2', '~m intReport', '~m packReport'],
    'ShardLead': ['+f CLS_NO', '+f CLS_OK', '+m classSlot', '~<clinit>'],
    'SkillAddFn': ['~m apply'],
    'SkillCfg': ['~m load'],
    'SkyySkillsPlugin': ['~m setup'],
}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read().replace("\r\n", "\n")
    o = open(GEN_OLD, encoding="utf8", newline="").read().replace("\r\n", "\n")
    K.check(g.startswith('"""SkyySkills 0.4.73') and g.count('VERSION = "0.4.73"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(")
            and g.count("makeClass(") == o.count("makeClass("), "S no new class, command or system")
    body = lambda t: t[t.index('"""', 3):]
    gx = body(g)
    i0 = gx.index("# 0.4.73 (tools/skills_0_4_73_patch.py): the CLASS slot")
    i1 = gx.index('}"""), lead70))', i0) + len('}"""), lead70))') + 1
    gx = (gx[:i0] + gx[i1:]).replace('VERSION = "0.4.73"', 'VERSION = "0.4.72"')
    a0 = gx.index("    int slot = {PKG}.BridgeXp.grantSlot(String.valueOf(a[1]));\n")
    a1 = gx.index("    return {PKG}.BridgeXp.offer((java.util.UUID) a[0], slot, base, src, expect, null, 0, true) >= 0L ? Boolean.TRUE : Boolean.FALSE;\n", a0)
    ob = body(o)
    b0 = ob.index("    int slot = {PKG}.BridgeXp.grantSlot(String.valueOf(a[1]));\n")
    b1 = ob.index("    return {PKG}.BridgeXp.offer((java.util.UUID) a[0], slot, base, src, expect, null, 0, true) >= 0L ? Boolean.TRUE : Boolean.FALSE;\n", b0)
    K.check(gx[:a0] + gx[a1:] == ob[:b0] + ob[b1:], "S below the docstring the script = 0.4.72 except VERSION, the classSlot block and SkillAddFn.apply's head")
    sa = gx[a0:a1]
    K.check(sa.count("ShardLead.classSlot(") == 1 and sa.count("offerX(") == 1 and ", true, false) >= 0L" in sa, "S SkillAddFn: classSlot only when grantSlot refuses; offerX grant true, cls false")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(TOOLS, "skills_0_4_72_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), [], "S the jar adds / drops no entry")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def run_cx(out, jar, scratch, _home):
    from jpype import JInt, JLong, JClass, JArray, JString
    K = HK.Child(out)
    J = T67._cls(jar)
    SD, ST, LD, BX, SC = J("SkillDefs"), J("SkillStore"), J("ShardLead"), J("BridgeXp"), J("SkillClass")
    T70._load(J, scratch, "cx")
    br = ST.bridge()
    N, MIN = int(SD.N), int(SD.MINING)
    d = JArray(JClass("long"))(2 * N)
    u = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-000000073000")
    k = str(u)
    K.eq(str(ST.pkey(u)), k, "CX the profile key of a player without SkyyProfiles = the UUID")
    ST.DATA.put(k, d)
    fn = J("SkillAddFn")()
    run = J("SkillRunFn")()
    br.put("class:fn:allowed", fn)   # a Function = SkyyClasses is loaded
    WAR, ARC, MONK = int(SD.indexOf("Warrior")), int(SD.indexOf("Archer")), int(SD.indexOf("Monk"))
    K.check(bool(SD.isClass(JInt(WAR))) and bool(SD.isClass(JInt(ARC))) and bool(SD.isClass(JInt(MONK))), "CX Warrior / Archer / Monk are class slots")
    d[WAR] = T70._xp_for(SD, WAR, 12)
    d[ARC] = T70._xp_for(SD, ARC, 30)
    d[MIN] = T70._xp_for(SD, MIN, 45)
    K.check(float(J("SkillCfg").CLASS_MULT) == 3.0, "CX the class skill XP multiplier is x3 (the x3 SkyyShards' click.fight.xpPerHp already holds)")
    # the stand-in Universe / PlayerRef / World (the 0.4.70 PATH rig)
    Unsafe = JClass("sun.misc.Unsafe")
    f = Unsafe.class_.getDeclaredField("theUnsafe")
    f.setAccessible(True)
    un = f.get(None)
    UNI, PR, WLD = (JClass("com.hypixel.hytale.server.core.universe." + n) for n in ("Universe", "PlayerRef", "world.World"))
    HM = JClass("java.util.HashMap")

    def setf(cls, obj, name, val):
        fld = cls.class_.getDeclaredField(name)
        fld.setAccessible(True)
        fld.set(obj, val)

    uni, pr, w = un.allocateInstance(UNI.class_), un.allocateInstance(PR.class_), un.allocateInstance(WLD.class_)
    q = JClass("java.util.ArrayDeque")()
    wid = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000730aa")
    setf(WLD, w, "acceptingTasks", JClass("java.util.concurrent.atomic.AtomicBoolean")(True))
    setf(WLD, w, "taskQueue", q)
    setf(PR, pr, "holder", un.allocateInstance(JClass("com.hypixel.hytale.component.Holder").class_))
    setf(PR, pr, "worldUuid", wid)
    pl, wl = HM(), HM()
    pl.put(u, pr)
    wl.put(wid, w)
    setf(UNI, uni, "playersByUuid", pl)
    setf(UNI, uni, "worldsByUuid", wl)
    setf(UNI, None, "instance", uni)
    Long = JClass("java.lang.Long")
    OA = JArray(JClass("java.lang.Object"))
    BT = J("BridgeTask").class_

    def award(skill, n, src, key=k):
        q.clear()
        args = [u, JString(skill), Long(n), JString(src)] + ([JString(key)] if key is not None else [])
        r = fn.apply(OA(args))
        tasks = []
        while q.size() > 0:
            t = q.pollFirst()
            tasks.append((int(BT.getField("amt").getLong(t)), int(BT.getField("slot").getInt(t)), str(BT.getField("source").get(t)), str(BT.getField("key").get(t))))
        return bool(r), tasks

    def shards_name():   # what SkyyShards' ShClk.classSkill sends: skill:fn:run {UUID, "class"}[5]
        a = run.apply(OA([u, JString("class")]))
        return None if a is None else str(a[5])

    def want(slot, n):
        return int(BX.paidY(u, JInt(slot), JLong(n), True, False, False))

    ok0, no0 = int(LD.CLS_OK.get()), int(LD.CLS_NO.get())
    # 1. Warrior: SkyyShards' own call shape is accepted, queued ONCE, paidY with cls false (no second x3)
    br.put("class:" + k, "Warrior")
    nm = shards_name()
    K.eq(nm, "Combat.Warrior", "CX skill:fn:run class answers the name SkyyShards sends")
    wv = want(WAR, 100)
    K.check(wv > 0 and int(BX.paidY(u, JInt(WAR), JLong(100), True, True, False)) >= 2 * wv, "CX paidY: cls true would multiply again (x3): %d vs %d" % (wv, int(BX.paidY(u, JInt(WAR), JLong(100), True, True, False))))
    ok, ts = award(nm, 100, "shard:" + nm.lower())
    K.check(ok and len(ts) == 1 and ts[0][1] == WAR and ts[0][2] == "shard:combat.warrior" and ts[0][3] == k, "CX Combat.Warrior from shard:combat.warrior: TRUE, ONE BridgeTask into the Warrior slot: %s" % (ts,))
    K.check(len(ts) == 1 and abs(ts[0][0] - wv) <= 1, "CX the queued XP = paidY(grant, cls false) %d (ShardLead x1: the class skill is the class level): %s" % (wv, ts))
    ok, ts = award("Swordsmanship", 100, "shard:combat.warrior")
    K.check(ok and len(ts) == 1 and ts[0][1] == WAR, "CX the label Swordsmanship works too: %s" % (ts,))
    ok, ts = award("combat.warrior", 7, "shard:combat")
    K.check(ok and len(ts) == 1 and ts[0][1] == WAR, "CX any case; source shard:combat: %s" % (ts,))
    # a batch of kills = one call each = one task each, nothing doubled
    q.clear()
    rs = [bool(fn.apply(OA([u, JString(nm), Long(50), JString("shard:combat.warrior"), JString(k)]))) for _ in range(5)]
    K.check(all(rs) and int(q.size()) == 5, "CX 5 kills -> 5 TRUE, exactly 5 tasks queued (%d)" % int(q.size()))
    q.clear()
    K.eq(d[WAR], T70._xp_for(SD, WAR, 12), "CX the data array is written only by the world-thread task (nothing paid on the calling thread)")
    # 2. another class / no class / class change
    ok, ts = award("Combat.Archer", 100, "shard:combat.archer")
    K.check(not ok and ts == [], "CX another class (Archer while Warrior) -> FALSE, nothing queued")
    br.remove("class:" + k)
    K.check(shards_name() is None or shards_name() == "None", "CX no class: skill:fn:run class has no class name (%s)" % shards_name())
    for s in ("Combat.Warrior", "Combat.Archer", "Combat"):
        ok, ts = award(s, 100, "shard:combat.warrior")
        K.check(not ok and ts == [], "CX no class chosen: %s -> FALSE, nothing queued (it keeps waiting in SkyyShards: not banked)" % s)
    br.put("class:" + k, "Archer")
    nm2 = shards_name()
    K.eq(nm2, "Combat.Archer", "CX class change: skill:fn:run follows")
    ok, ts = award(nm2, 100, "shard:" + nm2.lower())
    K.check(ok and len(ts) == 1 and ts[0][1] == ARC and abs(ts[0][0] - want(ARC, 100)) <= 1, "CX after the change Archer is paid: %s" % (ts,))
    ok, ts = award("Combat.Warrior", 100, "shard:combat.warrior")
    K.check(not ok and ts == [], "CX after the change the old class is refused")
    # Monk keeps its saved key Combat.Shaman (what SkyyShards gets from skill:fn:run)
    br.put("class:" + k, "Monk")
    nm3 = shards_name()
    ok, ts = award(nm3, 100, "shard:" + nm3.lower())
    K.check(nm3 == "Combat.Shaman" and ok and len(ts) == 1 and ts[0][1] == MONK, "CX Monk: %s from shard:%s -> paid into the Monk slot: %s" % (nm3, nm3.lower(), ts))
    ok, ts = award("Zen", 100, "shard:combat.shaman")
    K.check(ok and len(ts) == 1 and ts[0][1] == MONK, "CX Monk by its label Zen")
    br.put("class:" + k, "Warrior")
    # 3. profile switch: SkyyProfiles' profile:class differs from class:<uuid> (the class still following) -> refused; another profile key -> refused
    br.put("profile:class:" + k, "Mage")
    ok, ts = award("Combat.Warrior", 100, "shard:combat.warrior")
    K.check(not ok and ts == [], "CX profile switch (class not following yet) -> FALSE, nothing queued")
    br.remove("profile:class:" + k)
    SC.resync(u)
    br.put("profile:class:" + k, "Warrior")
    ok, ts = award("Combat.Warrior", 100, "shard:combat.warrior")
    K.check(ok and len(ts) == 1, "CX profile:class = the class -> paid")
    br.remove("profile:class:" + k)
    ok, ts = award("Combat.Warrior", 100, "shard:combat.warrior", key="00000000-0000-0000-0000-000000073000#2")
    K.check(not ok and ts == [], "CX the click was made on another profile (expect key differs) -> FALSE, nothing queued")
    ok, ts = award("Combat.Warrior", 100, "shard:combat.warrior", key=None)
    K.check(ok and len(ts) == 1, "CX no expect key -> the active profile")
    # 4. sources / names that never pay a class
    for s, src in (("Combat.Warrior", "shard:mining"), ("Combat.Warrior", "shard:farming"), ("Combat.Warrior", "collections"), ("Combat.Warrior", "SHARD:combat.warrior"),
                   ("Combat.Warrior", "pets"), ("Combat.War", "shard:combat.warrior"), ("Warrior", "shard:combat.warrior"), ("Combat", "shard:combat.warrior"),
                   ("Swords", "shard:combat.warrior"), ("", "shard:combat.warrior")):
        ok, ts = award(s, 100, src)
        K.check(not ok and ts == [], "CX %r from %r -> FALSE, nothing queued" % (s, src))
    ok, ts = award("Combat.Warrior", 0, "shard:combat.warrior")
    K.check(not ok and ts == [], "CX 0 XP -> FALSE (as every grant)")
    K.check(fn.apply(OA([u, JString("Combat.Warrior")])) == JClass("java.lang.Boolean").FALSE, "CX a malformed call -> FALSE, no throw")
    K.check(int(LD.classSlot(None, JString("Combat.Warrior"), JString("shard:combat"))) == -1 and int(LD.classSlot(u, None, JString("shard:combat"))) == -1
            and int(LD.classSlot(u, JString("Combat.Warrior"), None)) == -1 and int(LD.classSlot(u, JString("Combat.Warrior"), JString("shard:combat"))) == WAR, "CX classSlot: nulls -> -1; the class slot")
    # 5. ordinary grants unchanged
    ok, ts = award("Mining", 1000, "shard:mining")
    K.check(ok and len(ts) == 1 and ts[0][1] == MIN, "CX an ordinary shard grant (Mining) still paid: %s" % (ts,))
    ok, ts = award("Mining", 1000, "shard:combat.warrior")
    K.check(ok and len(ts) == 1 and ts[0][1] == MIN, "CX a listed skill keeps the grantSlot path whatever the source")
    # 6. offline / the class mod absent
    pl.remove(u)
    ok, ts = award("Combat.Warrior", 100, "shard:combat.warrior")
    K.check(not ok and ts == [], "CX offline -> FALSE, nothing queued")
    pl.put(u, pr)
    br.remove("class:" + k)
    br.remove("class:fn:allowed")
    ok, ts = award("Combat.Warrior", 100, "shard:combat.warrior")
    K.check(not ok and ts == [], "CX SkyyClasses absent (no class:<uuid>) -> FALSE")
    K.check(int(LD.CLS_OK.get()) - ok0 >= 10 and int(LD.CLS_NO.get()) - no0 >= 5, "CX counters (CLS_NO = class-name calls refused: other class, no class, switch, offline) CLS_OK %d / CLS_NO %d" % (int(LD.CLS_OK.get()) - ok0, int(LD.CLS_NO.get()) - no0))
    setf(UNI, None, "instance", None)
    ST.DATA.remove(k)
    K.save()


SHARDS_LIVE = os.path.join(os.path.dirname(LIVE_DIR), "Skyy_SkyyShards")


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    J = T67._cls(jar)
    s0 = T53.snapd(home)
    T67._start(J, home)
    s1 = T53.snapd(home)
    K.eq(sorted(k for k in set(s0) | set(s1) if s0.get(k) != s1.get(k)), [], "LIVE start 1: nothing written")
    T67._start(J, home)
    K.check(T53.snapd(home) == s1, "LIVE start 2 changes nothing")
    owed, files = [], 0
    if os.path.isdir(SHARDS_LIVE):   # READ ONLY
        for dp, _dn, fns in os.walk(SHARDS_LIVE):
            for fn_ in fns:
                if not fn_.endswith(".properties"):
                    continue
                files += 1
                for ln in open(os.path.join(dp, fn_), encoding="latin-1", errors="replace"):
                    if ln.startswith("owed.xp.Combat") or ln.lower().startswith("owed.xp.combat"):
                        owed.append(fn_ + ": " + ln.strip())
    K.notes.append("LIVE Skyy_SkyyShards (read only): %d .properties files, owed class XP lines: %s" % (files, owed))
    K.eq(owed, [], "LIVE the live shard files hold no owed class XP (nothing to pay once)")
    K.save()


if __name__ == "__main__":
    phases = [("static", run_static), ("cx", run_cx), ("fo", T72.run_fo), ("pr", T71.run_pr), ("sh", T70.run_sh), ("hl", T70.run_hl), ("pk", T70.run_pk), ("live", run_live)]
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
