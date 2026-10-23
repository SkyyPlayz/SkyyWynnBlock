"""Harness for SkyyPets 0.4.15 (the summon slot from Beastmastery 10 + every dragon FIGHTER + MOUNT; tools/pets_0_4_15_patch.py). Build first:
    python tools/pets_0_4_15_patch.py && python SkyyPets/build_skyypets_0.4.15.py
    python SkyyPets/test_skyypets_0.4.15.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; one class added (PetsMigS2), no system / command; setup MigP5 -> MigS2 -> load;
                 line endings kept; the jar: only PetsMigS2.class added, the only changed non-class entry = manifest.json; the rows
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.14 -> 0.4.15, engine-access audit
  SL    EXECUTED the level gate on real records with a fake SkyySkills skill:fn:run: level 9 locked ("It opens at Beastmastery 10.") /
                 10 open; the cache (no bridge read per look; TTL; bmSeen re-read + the one chat line on crossing, none when a quest already
                 opened it; bmForget = the join re-check); quest-opened profiles stay open at Lv 1; modes always / off / quest; the row
                 live (5); absent / null / throwing / other-skill answers = locked + "(level unknown)", one WARN, never throws; toSlot's
                 refusal text; applyScalars: default level / 10, an unknown mode -> level
  MIG   EXECUTED PetsMigS2: untouched quest -> level (LF, CRLF, spaces, QUEST), hand-set always / off / level kept (note for always / off),
                 a continued line kept, no line = nothing; sameAfter; run(): History copy, one Changes line, marker; a second run = nothing
                 (bytes identical); a fresh home = marker only
  DR    EXECUTED every dragon FIGHTER + MOUNT: a Lv 1 and a Lv 12 dragon's type line, the RIDING lines (locked / unlocked), riding off;
                 the Pets role filter (Fighters + Mounts list dragons, Bonus not); isMount(dragon) stays false (display only)
  T/R/M/F/DG/VW/ST/EL410  0.4.14's phases EXECUTED on this jar (0.4.14's two dragon "FIGHTER - Class" checks now expect FIGHTER + MOUNT)
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyPets: start 1 may only touch config files (the S2 update), start 2 writes nothing
NOT COVERED (UNVERIFIED in game): the chat line's look, the Server Setup page showing the new choice + row, SkyySkills' real skill:fn:run
answer for Beastmastery in a running server (the shape is read from SkyySkills 0.4.64's build script).
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util, subprocess, inspect

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "pets0415", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s414 = importlib.util.spec_from_file_location("test_skyypets_0_4_14", os.path.join(HERE, "test_skyypets_0.4.14.py"))
T414 = importlib.util.module_from_spec(_s414)
_s414.loader.exec_module(T414)
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T413, T412, T411, T410, T44, T41 = T414.T413, T414.T412, T414.T411, T414.T410, T414.T44, T414.T41

VERSION = "0.4.15"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.14.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.14.py")
PATCH = os.path.join(TOOLS, "pets_0_4_15_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
for _m in (T414, T413, T412, T411, T410, T44):
    _m.PKG = PKG
for _m in (T414, T413, T412, T411):
    _m.JAR, _m.OLD_JAR = JAR, OLD_JAR
T414.GEN = GEN
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],          # the kit's row tables (the new choice + row)
    "PetsCfg": ["+f SLOT2_LEVEL", "~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"], "PetsMigP5": ["~m mgLog", "~m run"],   # VERSION / the rows
    "PetBuff": ["+f BMLV", "+f BM_GAP", "+f BM_READS", "+f BM_SKILL", "+f BM_TTL", "+f BM_WARNED", "+m bmCached", "+m bmForget", "+m bmLevel",
                "+m bmRead", "+m bmSeen", "+m levelMode", "+m lockedWhy", "~<clinit>", "~m lockedWhy", "~m slot2Open"],     # lockedWhy(PetRec) added, lockedWhy() changed
    "PetBm": ["~m add"], "PetQuit": ["~m accept"],
    "PetOps": ["+m ridable", "~m tmount", "~m admin", "~m loadoutSet", "~m toSlot"],
    "PetsPage": ["~m build", "~m roleOk", "~m tip"],
    "SkyyPetsPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["PetsMigS2"]
C_FIGHT, C_MOUNT, C_DIM, C_SOFT, C_GOLD, C_RED, C_OK = "#e8554a", "#4fc3d9", "#7f93a6", "#d6e4ee", "#e8c25a", "#ff7a7a", "#39f493"
col = lambda c, t: '<color is="%s">%s</color>' % (c, t)
FM = col(C_FIGHT, "FIGHTER") + col(C_DIM, " + ") + col(C_MOUNT, "MOUNT")


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.15 - build script') and g.count('VERSION = "0.4.15"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls(") + 1,
            "S one class added (PetsMigS2), no system or command")
    su = g[g.index("PetsCfgMig.run(mods"):]
    K.check(su.index("PetsMigP5.run(") < su.index("PetsMigS2.run(") < su.index("PetsCfg.load(mods)"), "S setup: MigP5 -> MigS2 -> load")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z, oz = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(z.namelist()) - set(oz.namelist())), ["com/skyy/pets/PetsMigS2.class"], "S the only new entry = PetsMigS2.class")
    K.eq(sorted(set(oz.namelist()) - set(z.namelist())), [], "S no entry removed")
    ch = sorted(n for n in set(z.namelist()) & set(oz.namelist()) if not n.endswith(".class") and not n.endswith("/") and z.read(n) != oz.read(n))
    K.eq(ch, ["manifest.json"], "S the only changed non-class entry = manifest.json")
    K.check('("pets.slot2.unlock", "Summon slot unlock", "pets", "choice", "level", "", "", "level|Beastmastery level,quest|Stable quest,always|Always open,off|Closed"' in g
            and '("pets.slot2.level", "Summon slot Beastmastery level", "pets", "int", "10", "1", "1000"' in g, "S the rows: level = the default choice, pets.slot2.level 10")
    K.check("Zone 2 Stable quest" in g and "It opens at Beastmastery " in g, "S the locked texts")
    K.save()


# ======================================================================================================== SL: the level gate, EXECUTED
def run_sl(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "sl")
    K, JClass, JProxy, BR = W["K"], W["JClass"], W["JProxy"], W["BR"]
    P_ = lambda n: JClass(PKG + n)
    Cfg, Buff, Ops, Log, Eng = P_("PetsCfg"), P_("PetBuff"), P_("PetOps"), P_("PetsLog"), P_("PetsEng")
    Integer, Long, Bool, Obj = JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean"), JClass("java.lang.Object")
    K.eq((str(Cfg.SLOT2_MODE), int(Cfg.SLOT2_LEVEL)), ("level", 10), "SL the defaults: mode level, row 10")
    told = []
    names = W["names"]
    Eng.API = JProxy(PKG + "PetsApi", dict={"online": lambda: T41._uarr(JClass, list(names)), "byName": lambda n: None,
                                            "nameOf": lambda u: names.get(str(u), str(u)), "tell": lambda u, t, c: told.append((str(u), str(t)))})
    LV = {}            # profile key -> Beastmastery level (missing = SkyySkills answers null, as for an unknown skill)
    ASKED = []
    mode = {"m": "ok"}

    def fake_run(a):
        ASKED.append((str(a[0]), str(a[1])))
        if mode["m"] == "throw":
            raise RuntimeError("boom")
        if mode["m"] == "other":
            return JClass("java.lang.Object[]")([Integer(50), Integer(50), Long(0), Long(0), Bool(True), "Mining"])
        if str(a[1]) != "Beastmastery" or str(a[0]) not in LV:
            return None
        return JClass("java.lang.Object[]")([Integer(LV[str(a[0])]), Integer(50), Long(0), Long(0), Bool(True), "Beastmastery"])
    BR.put("skill:fn:run", JProxy("java.util.function.Function", dict={"apply": fake_run}))
    u, k, r = T44._mk(W, 9601)
    LV[k] = 9
    K.check(not bool(Buff.slot2Open(r)), "SL Beastmastery 9: the summon slot is locked")
    K.eq(str(Buff.lockedWhy(r)), "It opens at Beastmastery 10.", "SL the locked line (live number)")
    wolf = str(Ops.createR(r, None, "Wolf", 2, 5, 0, 0, "test", "harness", False))
    K.eq(str(Ops.toSlot(u, wolf, 2, "harness")), "-The summon slot is locked. It opens at Beastmastery 10.", "SL toSlot refuses with the line")
    n0 = len(ASKED)
    for _ in range(50):
        Buff.slot2Open(r)
    K.eq(len(ASKED), n0, "SL 50 looks = no bridge read (cached; no per-tick cost)")
    LV[k] = 10
    K.check(not bool(Buff.slot2Open(r)), "SL (still the cached 9 until a re-check)")
    now = int(W["now"]())
    Buff.BMLV.put(k, JClass("long[]")([now - 5000, 9]))     # the last read 5 s ago (past BM_GAP)
    Buff.bmSeen(u, k)
    K.check(bool(Buff.slot2Open(r)), "SL Beastmastery 10 after the level-up re-check (bmSeen): open")
    K.check(len(told) == 1 and "Beastmastery 10: your summon slot is open!" in told[0][1], "SL one chat line on crossing: %s" % told)
    K.check(str(Ops.toSlot(u, wolf, 2, "harness")).startswith("+"), "SL a Fighter goes into the open summon slot")
    Buff.bmSeen(u, k)
    K.eq(len(told), 1, "SL a second grant within 2 s: no re-read, no second line")
    Buff.BMLV.put(k, JClass("long[]")([now - 5000, 10]))
    Buff.bmSeen(u, k)
    K.eq(len(told), 1, "SL already open: no second line")
    # TTL: a level drop (rebirth) is seen within a minute
    LV[k] = 0
    Buff.BMLV.put(k, JClass("long[]")([now - 61000, 10]))
    K.check(not bool(Buff.slot2Open(r)), "SL after the 60 s TTL the level is read again (a rebirth to 0 locks it)")
    # join re-check: bmForget drops the cache
    LV[k] = 12
    Buff.bmForget(u)
    K.check(not Buff.BMLV.containsKey(k) and bool(Buff.slot2Open(r)), "SL bmForget (quit) -> the next look reads fresh (= join)")
    # the row is live
    LV[k] = 9
    Buff.BMLV.clear()
    Cfg.SLOT2_LEVEL = 5
    K.check(bool(Buff.slot2Open(r)), "SL the row at 5: Beastmastery 9 opens it")
    Cfg.SLOT2_LEVEL = 10
    K.check(not bool(Buff.slot2Open(r)), "SL back to 10: locked")
    # a quest-opened profile keeps it at Lv 1; no chat line for it
    u2, k2, r2 = T44._mk(W, 9602)
    r2.set("slot2.unlocked", "true")
    LV[k2] = 1
    K.check(bool(Buff.slot2Open(r2)), "SL a quest-opened profile (slot2.unlocked) keeps the slot at Beastmastery 1")
    LV[k2] = 10
    Buff.BMLV.put(k2, JClass("long[]")([now - 5000, 1]))
    Buff.bmSeen(u2, k2)
    K.eq(len(told), 1, "SL crossing 10 when the quest already opened it: no chat line")
    # the modes
    Cfg.SLOT2_MODE = "quest"
    K.check(bool(Buff.slot2Open(r2)) and not bool(Buff.slot2Open(r)) and "Zone 2 Stable quest" in str(Buff.lockedWhy(r)), "SL mode quest: only unlocked profiles, the quest line")
    LV[k] = 50
    Buff.BMLV.clear()
    K.check(not bool(Buff.slot2Open(r)), "SL mode quest: Beastmastery 50 does not open it")
    Cfg.SLOT2_MODE = "always"
    K.check(bool(Buff.slot2Open(r)), "SL mode always: open")
    Cfg.SLOT2_MODE = "off"
    K.check(not bool(Buff.slot2Open(r2)) and "closed on this server" in str(Buff.lockedWhy(r2)), "SL mode off: closed even for a quest-opened profile")
    Cfg.SLOT2_MODE = "level"
    # absent / unreadable SkyySkills
    u3, k3, r3 = T44._mk(W, 9603)
    r3.set("slot2.unlocked", "true")
    Log.LINES.clear()
    BR.remove("skill:fn:run")
    Buff.BMLV.clear()
    Buff.BM_WARNED = False
    ok = True
    try:
        a1 = bool(Buff.slot2Open(r))
        w1 = str(Buff.lockedWhy(r))
    except Exception as e:
        ok, a1, w1 = False, True, repr(e)
    K.check(ok and not a1 and w1 == "It opens at Beastmastery 10 (level unknown).", "SL no SkyySkills: locked + the clear line, no throw: %s" % w1)
    K.check(bool(Buff.slot2Open(r3)), "SL no SkyySkills: a quest-opened profile stays open")
    warns = [str(x) for x in Log.LINES if "Beastmastery level mode" in str(x)]
    Buff.BMLV.clear()
    Buff.slot2Open(r)
    warns2 = [str(x) for x in Log.LINES if "Beastmastery level mode" in str(x)]
    K.check(len(warns) == 1 and len(warns2) == 1, "SL one WARN, logged once: %s" % warns[:1])
    BR.put("skill:fn:run", JProxy("java.util.function.Function", dict={"apply": fake_run}))
    for m_, what in (("throw", "a throwing skill:fn:run"), ("other", "an answer for another skill")):
        mode["m"] = m_
        Buff.BMLV.clear()
        try:
            got = bool(Buff.slot2Open(r)), str(Buff.lockedWhy(r))
        except Exception as e:
            got = (True, repr(e))
        K.check(got == (False, "It opens at Beastmastery 10 (level unknown)."), "SL %s: locked + level unknown: %s" % (what, got))
    mode["m"] = "ok"
    LV.pop(k, None)
    Buff.BMLV.clear()
    K.check(not bool(Buff.slot2Open(r)) and int(Buff.bmLevel(r)) == -1, "SL an older SkyySkills (null for Beastmastery): locked, level -1")
    Buff.bmSeen(None, None)
    Buff.bmSeen(u, None)
    K.check(not bool(Buff.slot2Open(None)) and str(Buff.lockedWhy()) == "It opens at Beastmastery 10.", "SL null-safe")
    # PetBm.add -> bmSeen (the level-up hook): a grant SkyySkills accepts re-reads the level
    LV[k] = 11
    Buff.BMLV.put(k, JClass("long[]")([now - 5000, 9]))
    BR.put("skill:fn:addxp", JProxy("java.util.function.Function", dict={"apply": lambda a: Bool(True)}))
    W["keys"][str(u)] = k
    sent = int(P_("PetBm").add(u, 5.0))
    K.check(sent == 5 and bool(Buff.slot2Open(r)), "SL PetBm.add (Beastmastery XP accepted) re-checks the level: open (sent %d)" % sent)
    # applyScalars: defaults + an unknown mode
    Props = JClass("java.util.Properties")
    Cfg.applyScalars(Props())
    K.eq((str(Cfg.SLOT2_MODE), int(Cfg.SLOT2_LEVEL)), ("level", 10), "SL applyScalars on an empty file: level / 10")
    pp = Props()
    pp.setProperty("pets.slot2.unlock", "bogus")
    pp.setProperty("pets.slot2.level", "25")
    Cfg.applyScalars(pp)
    K.eq((str(Cfg.SLOT2_MODE), int(Cfg.SLOT2_LEVEL)), ("level", 25), "SL an unknown mode -> level; the row read")
    pp.setProperty("pets.slot2.unlock", "quest")
    Cfg.applyScalars(pp)
    K.eq(str(Cfg.SLOT2_MODE), "quest", "SL a hand-set quest stays quest")
    K.check("pets.slot2.unlock=level" in str(Cfg.DEFAULT_TEXT) and "pets.slot2.level=10" in str(Cfg.DEFAULT_TEXT), "SL the fresh config file: level + 10")
    Cfg.reloadAll()
    K.save()


# ======================================================================================================== MIG: PetsMigS2, EXECUTED
def run_mig(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Mg, Log = P_("PetsMigS2"), P_("PetsLog")
    Log.LINES = JClass("java.util.ArrayList")()

    def upd(t):
        r = Mg.mgUpdate(JString(t))
        return str(r[0]), int(r[1]), str(r[2]), str(r[3])
    src = "# SkyyPets\npets.enabled=true\npets.slot2.unlock=quest\npets.slot2.buffPercent=50\n"
    t1, n1, no1, o1 = upd(src)
    K.check(n1 == 1 and t1 == src.replace("unlock=quest", "unlock=level") and no1 == "" and o1 == "quest", "MIG untouched quest -> level, nothing else")
    t2, n2, _, _ = upd(src.replace("\n", "\r\n"))
    K.check(n2 == 1 and t2 == t1.replace("\n", "\r\n"), "MIG CRLF kept")
    t3, n3, _, o3 = upd(src.replace("pets.slot2.unlock=quest", "pets.slot2.unlock = QUEST  "))
    K.check(n3 == 1 and "pets.slot2.unlock = level  \n" in t3 and o3 == "QUEST", "MIG spaces kept, QUEST counts as the old default: %r" % t3)
    for v in ("always", "off"):
        tv, nv, nov, _ = upd(src.replace("unlock=quest", "unlock=" + v))
        K.check(nv == 0 and tv == src.replace("unlock=quest", "unlock=" + v) and ("kept hand-set pets.slot2.unlock=" + v) in nov, "MIG hand-set %s kept + noted" % v)
    tl, nl, nol, _ = upd(src.replace("unlock=quest", "unlock=level"))
    K.check(nl == 0 and nol == "", "MIG already level: nothing, no note")
    K.eq(upd(src.replace("unlock=quest", "unlock=que\\\nst"))[1], 0, "MIG a continued line is kept")
    K.eq(upd("pets.enabled=true\n")[1], 0, "MIG no line = nothing (the new default applies)")
    two = src + "pets.slot2.unlock=always\n"
    K.eq(upd(two)[1], 0, "MIG the LAST live line counts (always wins over an earlier quest)")
    old_b = src.encode("latin-1")
    K.check(bool(Mg.sameAfter(old_b, t1.encode("latin-1"))) and not bool(Mg.sameAfter(old_b, (t1 + "x=1\n").encode("latin-1")))
            and not bool(Mg.sameAfter(old_b, t1.replace("enabled=true", "enabled=false").encode("latin-1"))), "MIG sameAfter: only the planned line may change")
    Paths = JClass("java.nio.file.Paths")
    for tag, data, moved in (("untouched", src.replace("\n", "\r\n").encode("latin-1"), True), ("hand", src.replace("unlock=quest", "unlock=off").encode("latin-1"), False)):
        d = os.path.join(scratch, "mig-" + tag, "Skyy_SkyyPets")
        os.makedirs(d, exist_ok=True)
        cfg = os.path.join(d, "config.properties")
        open(cfg, "wb").write(data)
        m1 = str(Mg.run(Paths.get(d)))
        after1 = open(cfg, "rb").read()
        want = data.replace(b"unlock=quest", b"unlock=level") if moved else data
        K.check(after1 == want and os.path.isfile(os.path.join(d, "migrations", "pets-s2.done")), "MIG run() %s: file %s, marker written: %s" % (tag, "updated" if moved else "kept", m1[:140]))
        lg = os.path.join(d, "config-changes.log")
        lines = [l for l in open(lg, encoding="utf-8").read().splitlines() if "\tupdate\tpets.slot2.unlock\t" in l] if os.path.isfile(lg) else []
        if moved:
            K.check(len(lines) == 1 and lines[0].endswith("\tSkyyPets 0.4.15\t-\tupdate\tpets.slot2.unlock\tquest\tlevel\tok"),
                    "MIG one Changes line (Undo in Server Setup): %s" % lines)
            hd = os.path.join(d, "config-history")
            hist = [os.path.join(dp, f) for dp, _dn, fs in os.walk(hd) for f in fs] if os.path.isdir(hd) else []
            K.check(any(open(h, "rb").read() == data for h in hist), "MIG the History copy holds the old bytes (%d files)" % len(hist))
            K.check("summon slot opens at the Beastmastery level of pets.slot2.level" in m1, "MIG the INFO line")
        else:
            K.check(lines == [] and "kept hand-set pets.slot2.unlock=off" in m1, "MIG hand-set off: no Changes line, the note: %s" % m1[-120:])
        m2 = str(Mg.run(Paths.get(d)))
        K.check(m2 == "" and open(cfg, "rb").read() == after1, "MIG %s: a second run = nothing (marker; bytes identical)" % tag)
        if moved:
            lines2 = [l for l in open(lg, encoding="utf-8").read().splitlines() if "\tupdate\tpets.slot2.unlock\t" in l]
            K.eq(len(lines2), 1, "MIG twice = once: still one Changes line")
    d2 = os.path.join(scratch, "mig-fresh", "Skyy_SkyyPets")
    os.makedirs(d2, exist_ok=True)
    K.check("default (Beastmastery level) applies" in str(Mg.run(Paths.get(d2))) and os.path.isfile(os.path.join(d2, "migrations", "pets-s2.done"))
            and not os.path.isfile(os.path.join(d2, "config.properties")), "MIG a fresh home: marker only")
    K.save()


# ======================================================================================================== DR: every dragon FIGHTER + MOUNT
def run_dr(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "dr")
    K, JClass = W["K"], W["JClass"]
    P_ = lambda n: JClass(PKG + n)
    Cfg, Ops, Page, Rd = P_("PetsCfg"), P_("PetOps"), P_("PetsPage"), P_("PetRide")
    u, k, r = T44._mk(W, 9701)
    rl = int(Rd.rideLevel())
    K.eq(rl, 10, "DR the ride level is 10")
    d1 = str(Ops.createR(r, None, "DragonPlain", 4, 1, 0, 0, "test", "harness", False))
    K.check(not d1.startswith("-"), "DR (an Epic Plain Dragon Lv 1: %s)" % d1)
    t = str(Page.tip(r, d1, 0))
    K.eq(t.split("\n")[0], FM, "DR Lv 1 dragon: FIGHTER + MOUNT (Skyy: both a fighter and a mount)")
    K.check((col(C_SOFT, "Ride it from Lv ") + col(C_GOLD, "10") + "  " + col(C_RED, "locked")) in t and "Jump to" not in t and "Fights when you are not riding it" not in t,
            "DR Lv 1: RIDING keeps 'Ride it from Lv 10 locked'")
    r.set("pet.%s.level" % d1, "12")
    t = str(Page.tip(r, d1, 0))
    K.eq(t.split("\n")[0], FM, "DR Lv 12 dragon: FIGHTER + MOUNT")
    K.check((col(C_SOFT, "Ride it from Lv ") + col(C_GOLD, "10") + "  " + col(C_OK, "unlocked")) in t and col(C_SOFT, "Jump to take off and fly") in t,
            "DR Lv 12: RIDING unlocked + the fly line")
    Cfg.DRAGON_RIDE = False
    t = str(Page.tip(r, d1, 0))
    K.check(t.split("\n")[0] == FM and col(C_DIM, "Riding is off on this server.") in t, "DR riding off: still FIGHTER + MOUNT, the RIDING line says off")
    Cfg.reloadAll()
    for kd in ("DragonPlain", "DragonTundra", "DragonFire", "DragonStorm", "DragonSky"):
        K.check(str(Ops.typeLine(kd, 1)) == FM and str(Ops.typeLine(kd, 100)) == FM, "DR typeLine %s Lv 1 / 100 = FIGHTER + MOUNT" % kd)
        K.check(bool(Page.roleOk(kd, 2)) and bool(Page.roleOk(kd, 3)) and not bool(Page.roleOk(kd, 1)), "DR filter: %s under Fighters AND Mounts, not Bonus" % kd)
        K.check(not bool(Cfg.isMount(kd)) and not bool(Ops.ridable(kd, 1)) and bool(Ops.ridable(kd, 10)), "DR %s: the mount role stays off (display only); ridable from Lv 10" % kd)
    K.check(bool(Page.roleOk("Horse", 3)) and not bool(Page.roleOk("Wolf", 3)) and bool(Page.roleOk("Wolf", 2)) and bool(Page.roleOk("Rat", 1)), "DR the other kinds' filters unchanged")
    K.check(str(Ops.typeLine("Wolf", 50)) == col(C_FIGHT, "FIGHTER") + col(C_DIM, " - ") + col(C_SOFT, "Class"), "DR a Wolf stays FIGHTER - Class")
    K.save()


# ======================================================================================================== reused 0.4.14 phases
_swap = T414._swap


def run_t(out, jar, scratch, home):
    f = _swap(T414.run_t, T414, [
        ('''K.eq(tl(t), col(C_FIGHT, "FIGHTER") + col(C_DIM, " - ") + col(C_SOFT, "Class"), "T dragon below Lv %d: FIGHTER - Class" % rl)''',
         '''K.eq(tl(t), col(C_FIGHT, "FIGHTER") + col(C_DIM, " + ") + col(C_MOUNT, "MOUNT"), "T dragon below Lv %d: FIGHTER + MOUNT (0.4.15)" % rl)'''),
        ('''K.check(tl(t) == col(C_FIGHT, "FIGHTER") + col(C_DIM, " - ") + col(C_SOFT, "Class") and col(C_DIM, "Riding is off on this server.") in t, "T dragon riding off: FIGHTER only + the line")''',
         '''K.check(tl(t) == col(C_FIGHT, "FIGHTER") + col(C_DIM, " + ") + col(C_MOUNT, "MOUNT") and col(C_DIM, "Riding is off on this server.") in t, "T dragon riding off: FIGHTER + MOUNT (0.4.15) + the line")''')])
    f(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Mig, Mig2, MgP5, MgS2, Log = P_("PetsCfg"), P_("PetStore"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("PetsMigP5"), P_("PetsMigS2"), P_("PetsLog")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    t0 = T41.tree(home)
    cfg = os.path.join(home, "config.properties")
    before = open(cfg, encoding="latin-1").read() if os.path.isfile(cfg) else ""
    m = re.findall(r"(?m)^\s*pets\.slot2\.unlock\s*[=:]\s*(\S*)\s*$", before)

    def start():
        Mig.run(Paths.get(home))
        Mig2.run(Paths.get(home))
        MgP5.run(Paths.get(home))
        s = str(MgS2.run(Paths.get(home)))
        Cfg.load(Paths.get(mods))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return s, [int(x) for x in Store.scanAll()]
    s1, sc1 = start()
    t1 = T41.tree(home)
    changed = sorted(x for x in set(t0) | set(t1) if t0.get(x) != t1.get(x) and not x.startswith(("config-history", "migrations", "config.properties", "config-changes")))
    K.eq(changed, [], "LIVE start 1 touches only config files")
    print("   live: pets.slot2.unlock lines %s; PetsMigS2: %s" % (m, s1[:200] or "(already done)"))
    if m and m[-1].lower() == "quest":
        K.check(str(Cfg.SLOT2_MODE) == "level" and "-> level" in s1, "LIVE the live quest line moved to level")
    elif m:
        K.check(str(Cfg.SLOT2_MODE) == (m[-1].lower() if m[-1].lower() in ("level", "always", "off") else "level"), "LIVE a hand-set %s stays" % m[-1])
    K.check(sc1[2] == 0 and sc1[3] == 0, "LIVE every pet file reads (%s)" % sc1)
    s2, sc2 = start()
    K.check(s2 == "" and T41.tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("sl", run_sl), ("mig", run_mig), ("dr", run_dr), ("t", run_t), ("r", T414.run_r), ("m", T412.run_m),
                   ("f", T414.run_f), ("dg", T414.run_dg), ("vw", T411.run_vw), ("st", T414.run_st), ("el410", T414.run_el), ("live", run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
