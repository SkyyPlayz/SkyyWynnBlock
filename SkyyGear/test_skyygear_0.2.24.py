"""SkyyGear 0.2.24 - bare-JVM harness for THE HYTALE 0.7.0 PORT (tools/gear_0_2_24_patch.py). Child JVM: the game's own JRE, the 0.7.0
HytaleServer.jar, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch folder. The 0.7.0 engine singletons come
from SkyyProfiles/test_skyyprofiles_0.1.10.py (engine()). The live Skyy_SkyyGear folder is only READ (copied into scratch) and checked.

    python SkyyGear/test_skyygear_0.2.24.py --dir <empty folder inside tools/dev/scratch/> [--keep]
         [--jar SkyyGear-0.2.24.jar] [--prev SkyyGear-0.2.23.jar]

SECTIONS
  CC  CLASS COMPARE 0.2.23 -> 0.2.24: no class added / removed; structural changes only GearCrit.handle (the 0.7.0 CombatTextUpdate
      constructor with its Color); constant-only changes = the version, GearDefs (the "bangstick" ammo token) and the bag pool / own-base
      tables the build derives from 0.7.0's Assets.zip (listed)
  JT  jar entries: the same names as 0.2.23; non-class files byte-identical but the manifest (version) and the asset files the build derives
      from Assets.zip (listed)
  A   every class of both jars loads, verifies (-Xverify:all) and initialises against the 0.7.0 engine
  C   THE CRIT! POPUP EXECUTED: the REAL GearCrit.handle on an ECS shim (a CommandBuffer + ArchetypeChunk subclass), a real Damage
      (Physical, hit angle 30) from a player who sees the mob (a real EntityViewer): the attacker's viewer gets a real 0.7.0
      CombatTextUpdate "CRIT!" at angle 10 with color == null (= the entity style's colour, like vanilla's Physical number); an overcrit
      (level 2) says "CRIT!!"; the popup switch off -> nothing; a mob the attacker cannot see -> nothing (counter 8); vanilla's own
      DamageSystems$EntityUIEvents on the same hit queues its number with the same null colour (the 0.7.0 engine path, no SkyyGear code);
      the packet serialises (hasColor false) and reads back; CONTROL: 0.2.23's GearCrit.handle on 0.7.0 throws NoSuchMethodError
  G   the 0.7.0 content rules: GearData's ammo rule calls Weapon_Bangstick ammo (not gear) and still calls Weapon_Sword_Iron gear
  ST  START TWICE on a scratch COPY of the live Skyy_SkyyGear (quality file, every one-time update, GearCfg.load - setup()'s order): no file
      changed by either start
  AA  python tools/ci/crosscheck.py --jar <0.2.24> --baseline: no FAIL for SkyyGear on 0.7.0, the command tree identical to 0.2.23
"""
import os, sys, re, json, shutil, subprocess, zipfile, importlib.util, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION, PREV_VERSION = "0.2.24", "0.2.23"
PKG = "com.skyy.gear."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pages07", "gear")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
PREV_JAR = os.path.abspath(arg("--prev", os.path.join(HERE, "SkyyGear-%s.jar" % PREV_VERSION)))
APPDATA = os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming")
LIVE = os.path.join(APPDATA, "Hytale", "UserData", "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
SKILLS_HARNESS = os.path.join(ROOT, "SkyySkills", "test_skyyskills_0.4.27.py")
PROF_HARNESS = os.path.join(ROOT, "SkyyProfiles", "test_skyyprofiles_0.1.10.py")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)
    return cond


def mod(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    saved = list(sys.argv)
    sys.argv = [sys.argv[0], "--dir", SCRATCH]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = saved
    m.SCRATCH = SCRATCH
    return m


def snap(d):
    return dict((os.path.relpath(os.path.join(r, f), d).replace(os.sep, "/"), open(os.path.join(r, f), "rb").read())
                for r, _ds, fs in os.walk(d) for f in fs) if os.path.isdir(d) else {}


# ============================================================================================ child (one JVM, -Xverify:all)
def run_e(out):
    import jpype
    from jpype import JClass, JInt, JFloat
    import skyybuild as B
    S = mod(SKILLS_HARNESS, "ts0427")
    TP = mod(PROF_HARNESS, "tp0110")
    hcls = os.path.join(SCRATCH, "hclasses")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(SCRATCH)
    S.jvm_start([hcls])
    R = {"load": {}}
    L = {}
    for tag, j in (("new", JAR), ("prev", PREV_JAR)):
        L[tag] = S.loader(j)
        R["load"][tag] = S.load_all(j, L[tag])
    try:
        N = TP.engine(S, B, hcls, "skyygear07")
        jf, U = N["jf"], N["U"]
        PH = "com.hypixel.hytale."
        HP = JClass("javassist.ClassPool")(False)
        HP.appendSystemPath()
        HP.appendClassPath(B.SERVER_JAR)
        CtNewMethod, CtField = JClass("javassist.CtNewMethod"), JClass("javassist.CtField")

        def hclass(name, sup, fields=(), meths=()):
            c = HP.makeClass(name, HP.get(sup))
            for s_ in fields:
                c.addField(CtField.make(s_, c))
            for s_ in meths:
                c.addMethod(CtNewMethod.make(s_, c))
            c.writeFile(hcls)
        CMP, CTY, RF = PH + "component.Component", PH + "component.ComponentType", PH + "component.Ref"
        hclass(PH + "component.SkyyGear07Buf", PH + "component.CommandBuffer",
               ["public static java.util.IdentityHashMap COMP = new java.util.IdentityHashMap();"],
               ["public %s getComponent(%s r, %s t) { java.util.Map m = (java.util.Map) COMP.get(r); return m == null ? null : (%s) m.get(t); }"
                % (CMP, RF, CTY, CMP)])
        hclass(PH + "component.SkyyGear07Chunk", PH + "component.ArchetypeChunk",
               ["public static %s REF = null;" % RF],
               ["public %s getReferenceTo(int i) { return REF; }" % RF])
        BufC, ChunkC = JClass(PH + "component.SkyyGear07Buf"), JClass(PH + "component.SkyyGear07Chunk")
        buf, chunk = U.allocateInstance(BufC.class_), U.allocateInstance(ChunkC.class_)
        EMc = JClass(PH + "server.core.modules.entity.EntityModule")
        CTc = JClass(CTY)
        ctv = CTc()
        jf(CTc.class_, "index").setInt(ctv, 650)
        jf(CTc.class_, "hashCode").setInt(ctv, 650)
        jf(EMc.class_, "entityViewerComponentType").set(EMc.get(), ctv)
        EUIM = JClass(PH + "server.core.modules.entityui.EntityUIModule")
        euim = U.allocateInstance(EUIM.class_)
        ctl = CTc()
        jf(CTc.class_, "index").setInt(ctl, 651)
        jf(CTc.class_, "hashCode").setInt(ctl, 651)
        jf(EUIM.class_, "uiComponentListType").set(euim, ctl)
        jf(EUIM.class_, "instance").set(None, euim)
        EVW = JClass(PH + "server.core.modules.entity.tracker.EntityTrackerSystems$EntityViewer")
        DMG = JClass(PH + "server.core.modules.entity.damage.Damage")
        DENT = JClass(PH + "server.core.modules.entity.damage.Damage$EntitySource")
        CTU = JClass(PH + "protocol.CombatTextUpdate")
        REFc, STc = JClass(RF), JClass(PH + "component.Store")
        PRc = JClass(PH + "server.core.universe.PlayerRef")
        UUID = JClass("java.util.UUID")
        IdMap = JClass("java.util.IdentityHashMap")
        st0 = U.allocateInstance(STc.class_)

        def ref(i):
            r_ = U.allocateInstance(REFc.class_)
            jf(REFc.class_, "store").set(r_, st0)
            jf(REFc.class_, "index").setInt(r_, i)
            return r_
        att, mob = ref(11), ref(12)
        pr = U.allocateInstance(PRc.class_)
        jf(PRc.class_, "uuid").set(pr, UUID.fromString("00000000-0000-0000-0000-0000000000f1"))
        jf(PRc.class_, "entity").set(pr, att)
        viewer = EVW(JInt(64), None)
        m_att = IdMap()
        m_att.put(N["CT"]["pr"], pr)
        m_att.put(ctv, viewer)
        BufC.COMP.put(att, m_att)
        ChunkC.REF = mob

        def jc(k, n):
            return JClass(PKG + n, loader=L[k])
        for k in ("new", "prev"):
            Cfg = jc(k, "GearCfg")
            Cfg.CRIT_FX, Cfg.CRIT_STYLE, Cfg.CRIT_SPARKS = True, False, "off"
        DCm = JClass(PH + "server.core.modules.entity.damage.DamageCause")

        def hit(k, lv=1, visible=True, angle=30.0, amount=6.0):
            viewer.updates.clear()
            viewer.visible.clear()
            if visible:
                viewer.visible.add(mob)
            d = DMG(DENT(att), JInt(0), JFloat(amount))
            d.putMetaObject(DMG.HIT_ANGLE, JClass("java.lang.Float").valueOf(float(angle)))
            if lv is not None:
                jc(k, "GearHit").CRIT.put(d, JClass("java.lang.Integer").valueOf(lv))
            jc(k, "GearCrit").handle(JInt(0), chunk, buf, d, False)
            eu = viewer.updates.get(mob)
            ups = [] if eu is None else list(eu.toUpdatesArray())
            return [[str(u.getClass().getSimpleName()), str(u.text) if isinstance(u, CTU) else None,
                     round(float(u.hitAngleDeg), 2) if isinstance(u, CTU) else None, (u.color is None) if isinstance(u, CTU) else None] for u in ups], ups
        E = {}
        n1 = int(jc("new", "GearCrit").N[1])
        c1, ups1 = hit("new")
        E["c1"] = [c1, int(jc("new", "GearCrit").N[1]) - n1]
        c2, _u = hit("new", lv=2)
        E["c2"] = c2
        jc("new", "GearCfg").CRIT_FX = False
        c3, _u = hit("new")
        jc("new", "GearCfg").CRIT_FX = True
        E["c3"] = c3
        n8 = int(jc("new", "GearCrit").N[8])
        c4, _u = hit("new", visible=False)
        E["c4"] = [c4, int(jc("new", "GearCrit").N[8]) - n8]
        c5, _u = hit("new", lv=None)
        E["c5"] = c5
        # the packet round trip (0.7.0 serialiser: the nullable colour)
        rt = None
        try:
            MS = JClass("java.lang.foreign.MemorySegment")
            ARENA = JClass("java.lang.foreign.Arena")
            u0 = ups1[0]
            n_ = int(u0.computeSize())
            seg = ARENA.ofAuto().allocate(n_ + 16)
            w_ = int(u0.serialize(seg, 0))
            back = CTU.toObject(seg, 0)
            rt = [n_, w_, bool(CTU.hasColor(seg, 0)), str(back.text), round(float(back.hitAngleDeg), 2), back.color is None]
        except Exception as e_:
            rt = ["error", str(e_)[:300]]
        E["rt"] = rt
        # vanilla's own number on the same hit (DamageSystems$EntityUIEvents.queueUpdateFor) - the colour vanilla uses for a cause without one
        try:
            EUI = JClass(PH + "server.core.modules.entity.damage.DamageSystems$EntityUIEvents")
            viewer.updates.clear()
            viewer.visible.clear()
            viewer.visible.add(mob)
            mq = EUI.class_.getDeclaredMethod("queueUpdateFor", REFc.class_, JClass("java.lang.Float").TYPE, JClass("java.lang.Float").class_,
                                                JClass(PH + "protocol.Color").class_, EVW.class_)
            mq.setAccessible(True)
            mq.invoke(None, mob, JClass("java.lang.Float")(6.0), JClass("java.lang.Float")(30.0), None, viewer)
            eu = viewer.updates.get(mob)
            vu = list(eu.toUpdatesArray())
            E["van"] = [[str(u.text), round(float(u.hitAngleDeg), 2), u.color is None] for u in vu]
        except Exception as e_:
            E["van"] = ["error", str(e_)[:300]]
        # control: 0.2.23 on 0.7.0
        try:
            hit("prev")
            E["c6"] = "no error"
        except Exception as e_:
            E["c6"] = str(e_.getClass().getName()) if hasattr(e_, "getClass") else repr(e_)
        # G: the ammo rule (GearData) for the new bomb
        GD = jc("new", "GearData")
        ammo = [m_ for m_ in GD.class_.getDeclaredMethods() if str(m_.getName()) in ("ammoMs", "ammo")]
        g = {}
        for m_ in ammo:
            ps = [str(p.getSimpleName()) for p in m_.getParameterTypes()]
            for iid, ms in (("Weapon_Bangstick", 5), ("Weapon_Sword_Iron", 1), ("Weapon_Bomb_Fire", 25)):
                try:
                    if ps == ["String", "int"]:
                        g["%s(%s)" % (m_.getName(), iid)] = bool(m_.invoke(None, iid, JInt(ms)))
                    elif ps == ["String"]:
                        g["%s(%s)" % (m_.getName(), iid)] = bool(m_.invoke(None, iid))
                except Exception as e_:
                    g["%s(%s)" % (m_.getName(), iid)] = "error " + str(e_)[:80]
        E["g"] = [g, [str(x) for x in jc("new", "GearDefs").AMMO]]
        # ================================================================================ ST: two starts on a COPY of the live data
        home = os.path.join(SCRATCH, "st", "mods", "Skyy_SkyyGear")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, home)
        else:
            os.makedirs(home)
        Paths = JClass("java.nio.file.Paths")
        Cfg, Qual, Log = jc("new", "GearCfg"), jc("new", "GearQual"), jc("new", "GearLog")
        jc("new", "Gear").LOG = JClass(PH + "logger.HytaleLogger").get("SkyyGearHarness")
        starts = []
        for n_ in range(2):
            b0 = snap(home)
            Cfg.DIR = Paths.get(home)
            Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
            Log.FILE = Paths.get(os.path.join(home, "gear.log"))
            Qual.load(Paths.get(os.path.join(home, "quality.properties")))
            Cfg.importRolls(Cfg.FILE, Paths.get(os.path.join(os.path.dirname(home), "Skyy_SkyyRolls", "reforge.properties")))
            for m_ in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025",
                       "migrate0214", "migrate0215", "migrate0216", "migrate0217", "migrate0218"):
                getattr(Cfg, m_)()
            Cfg.load()
            a0 = snap(home)
            starts.append(sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k)))
        E["st"] = [starts, len(snap(home)), bool(Cfg.CRIT_FX)]
        R["E"] = E
    except Exception:
        import traceback
        R["error"] = traceback.format_exc()[-4000:]
    json.dump(R, open(out, "w"), indent=1, default=str)
    os._exit(0)


def check_e(E):
    c1 = E["c1"]
    check(c1 == [[["CombatTextUpdate", "CRIT!", 10.0, True]], 1], "C1: a crit through the REAL GearCrit.handle: ONE 0.7.0 CombatTextUpdate "
          "'CRIT!' at angle 30 - 20 with color null (the style's colour) to the attacker's viewer, popup counter +1: %s" % c1)
    check(E["c2"] == [["CombatTextUpdate", "CRIT!!", 10.0, True]], "C2: an overcrit says CRIT!!: %s" % E["c2"])
    check(E["c3"] == [], "C3: the popup switch off - nothing queued: %s" % E["c3"])
    check(E["c4"] == [[], 1], "C4: a mob the attacker cannot see - nothing queued (counter 8 +1): %s" % E["c4"])
    check(E["c5"] == [], "C5: a hit that was no crit - nothing: %s" % E["c5"])
    rt = E["rt"]
    check(rt[0] != "error" and rt[2] is False and rt[3:] == ["CRIT!", 10.0, True], "C: the popup packet serialises with no colour and reads back "
          "(%s)" % rt)
    check(E["van"] == [["6", 30.0, True]], "C: vanilla's own number (queueUpdateFor) for a cause without a colour carries color null too: %s" % E["van"])
    check(E["c6"] == "java.lang.NoSuchMethodError", "C6: CONTROL - 0.2.23's GearCrit.handle throws on 0.7.0: %s" % E["c6"])
    g, ammo = E["g"]
    check("bangstick" in ammo and any(k.endswith("(Weapon_Bangstick)") and v is True for k, v in g.items())
          and all(v is False for k, v in g.items() if k.endswith("(Weapon_Sword_Iron)"))
          and any(k.endswith("(Weapon_Bomb_Fire)") and v is True for k, v in g.items()),
          "G: GearData's ammo rule: Weapon_Bangstick = ammo (not gear) like Weapon_Bomb_Fire; Weapon_Sword_Iron stays gear: %s" % g)
    st = E["st"]
    check(len(st[0]) == 2 and st[0] == [[], []] and st[2], "ST: two starts on a COPY of the live Skyy_SkyyGear (%d files): no file changed: %s"
          % (st[1], st[0]))


# ============================================================================================ parent
def main():
    if "--e" in sys.argv:
        return run_e(arg("--out"))
    for j in (JAR, PREV_JAR):
        if not os.path.isfile(j):
            sys.exit("no jar at %s - build it first" % j)
    sroot = os.path.realpath(os.path.join(TOOLS, "dev", "scratch"))
    if not os.path.realpath(SCRATCH).startswith(sroot + os.sep):
        sys.exit("--dir must be inside tools/dev/scratch/ (deleted afterwards): %s" % SCRATCH)
    if os.path.exists(SCRATCH) and os.listdir(SCRATCH):
        sys.exit("%s is not empty - pass an empty --dir" % SCRATCH)
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.makedirs(env["TEMP"], exist_ok=True)
    live_before = snap(LIVE)
    me = os.path.abspath(__file__)
    try:
        # ---- CC
        # the 0.7.0 engine declares getWorld / getStore / getChunkSectionReferenceAtBlock / getGenerator on ChunkGrid (ChunkStore's
        # superclass): the same source compiles to a method ref on ChunkGrid - mapped back so only real changes count as structural
        rules = [[r"storage\.ChunkGrid\.", "storage.ChunkStore."]]
        out_cc = os.path.join(SCRATCH, "cc.json")
        with open(out_cc + ".log", "wb") as lf:
            subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import importlib.util as u; "
                            "s = u.spec_from_file_location('ts', %r); m = u.module_from_spec(s); sys.argv = ['x', '--dir', %r]; "
                            "s.loader.exec_module(m); m.SCRATCH = %r; m.run_cc(%r, %r, %r, %r)" % (
                                TOOLS, SKILLS_HARNESS, SCRATCH, SCRATCH, JAR, PREV_JAR, out_cc,
                                json.dumps({"versions": [VERSION, PREV_VERSION], "rules": rules}))],
                           env=env, stdout=lf, stderr=subprocess.STDOUT, cwd=SCRATCH)
        cc = json.load(open(out_cc)) if os.path.isfile(out_cc) else None
        check(cc is not None, "CC: the compare child ran")
        if cc:
            cls_ = cc["classes"]
            check(cc["added"] == [] and cc["gone"] == [], "CC: no class added / removed: %s %s" % (cc["added"], cc["gone"]))
            check(not [c for c, v in cls_.items() if v["fields_new"] or v["fields_gone"]] and all(v["same_shape"] for v in cls_.values()),
                  "CC: no field added / removed, same supers / interfaces")
            struct = dict((c, sorted(x.split("(")[0] for x in v["structural"])) for c, v in cls_.items() if v["structural"])
            const = dict((c, sorted(m_.split("(")[0] for m_ in v["const_only"])) for c, v in cls_.items() if v["const_only"])
            print("CC. 0.2.23 -> 0.2.24 structural %s; constants only %s" % (struct, const))
            # GearCrit.handle = the constructor; the build-time tables of 0.7.0 content are <clinit> constant arrays
            check(struct.get("GearCrit") == ["handle"] and all(set(m_) <= {"<clinit>"} for c, m_ in struct.items() if c != "GearCrit"),
                  "CC: the only structural method change = GearCrit.handle (+ build-time constant tables in <clinit>): %s" % struct)
        # ---- JT
        zj, zp = zipfile.ZipFile(JAR), zipfile.ZipFile(PREV_JAR)
        # the build copies vanilla weapon interactions / roots / items for the speed variants and the Untiered copies from Assets.zip: 0.7.0's
        # vanilla timings / durability / launch forces come with the rebuild (the 0.2.23 copies would put 0.6's back over 0.7.0's vanilla)
        DERIVED = ("Server/Item/Interactions/SkyyGear/Speed/", "Server/Item/Animations/SkyyGear/", "Server/Item/RootInteractions/Weapons/",
                   "Server/Item/Items/SkyyGear/UT/", "Server/ProjectileConfigs/SkyyGear/")
        nd = sorted(set(zj.namelist()) ^ set(zp.namelist()))
        check(all(n.startswith(DERIVED[0]) and "_Mace_" in n and "_Charged_StaminaCondition_Hold0p" in n for n in nd),
              "JT: entry names differ only for the Mace charged-swing speed copies (0.7.0's hold time 0.2 -> 0.167): %s" % nd)
        diff = sorted(n for n in zj.namelist() if not n.endswith(".class") and n in zp.namelist() and zj.read(n) != zp.read(n))
        print("JT. %d non-class entries differ from 0.2.23 (vanilla-derived at build time): %s" % (len(diff), sorted(set(n.rsplit("/", 1)[0] for n in diff))))
        check("manifest.json" in diff and all(n == "manifest.json" or n.startswith(DERIVED) for n in diff),
              "JT: only the manifest and the vanilla-derived speed / root / Untiered copies differ: %s" % [n for n in diff if n != "manifest.json" and not n.startswith(DERIVED)])
        mn, mpn = json.loads(zj.read("manifest.json")), json.loads(zp.read("manifest.json"))
        check(json.dumps(mn, sort_keys=True) == json.dumps(mpn, sort_keys=True).replace(PREV_VERSION, VERSION), "JT: manifest = 0.2.23's but the version")
        # ---- A + C + G + ST
        out_e = os.path.join(SCRATCH, "e.json")
        with open(out_e + ".log", "wb") as lf:
            subprocess.run([sys.executable, me, "--e", "--out", out_e, "--dir", SCRATCH, "--jar", JAR, "--prev", PREV_JAR],
                           env=env, stdout=lf, stderr=subprocess.STDOUT)
        r = json.load(open(out_e)) if os.path.isfile(out_e) else None
        if r is None:
            print(open(out_e + ".log", encoding="utf8", errors="replace").read()[-3000:])
        check(r is not None and "error" not in r, "E ran: %s" % (r or {}).get("error", "")[-3000:])
        if r:
            for tag, (n_, f_) in r["load"].items():
                check(not f_ and n_ >= 100, "A (%s): %d classes load, verify (-Xverify:all), initialise on 0.7.0 %s" % (tag, n_, f_[:3]))
        if r and "error" not in r:
            check_e(r["E"])
        # ---- AA
        out_aa = os.path.join(SCRATCH, "aa.log")
        with open(out_aa, "wb") as lf:
            subprocess.run([sys.executable, os.path.join(TOOLS, "ci", "crosscheck.py"), "--jar", JAR, "--baseline"], env=env, stdout=lf,
                           stderr=subprocess.STDOUT, cwd=ROOT)
        aa = open(out_aa, encoding="utf8", errors="replace").read()
        mine = [ln for ln in aa.splitlines() if ln.startswith("FAIL") and " SkyyGear " in ln]
        check("access:" in aa and not mine, "AA: crosscheck --jar 0.2.24: no FAIL for SkyyGear on 0.7.0: %s" % mine[:3])
        check("baseline SkyyGear %s -> %s: command / permission tree identical" % (PREV_VERSION, VERSION) in aa, "AA: the command / permission tree = 0.2.23's")
        after = snap(LIVE)
        chg = [k_ for k_ in sorted(set(live_before) | set(after)) if live_before.get(k_) != after.get(k_)]
        if chg:
            print("NOTE: live files changed during the run (the game is running?): %s" % chg[:8])
        check(not [c for c in chg if not c.endswith("gear.log")], "the live Skyy_SkyyGear folder got nothing from the harness: %s" % chg[:5])
    finally:
        if "--keep" not in sys.argv:
            os.chdir(ROOT)
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
