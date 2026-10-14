"""SkyyHud 0.3.24 harness - Fishing / Ranching / Orchard lines, the Farming average and the ability levels (tools/hud_0_3_24_patch.py).
Built on tools/harness_kit.py: each phase a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir
in the scratch folder).

    python SkyyHud/test_skyyhud_0.3.24.py [--jar SkyyHud-0.3.24.jar] [--old SkyyHud-0.3.23.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.23 -> 0.3.24: exactly the listed classes / members differ; non-class entries: the manifest
  X20 / X19 / Q / M / QK / ST   EVERY check of the 0.3.23 harness (its x20, x19, quest, msg, qk and live phases) on THIS jar; X20's two E5
       checks read the Skills model at the 10-line indexes ([23] / [32]) - eased there and re-run EXACTLY in E5S with the 13-line ones
  S24  skills   WLayout: 13 lines (Fishing / Ranching / Orchard appended as bits 10-12), default mask 3, all = 8191, box 260 x 266;
                Widgets.skillsModelU on a fake bridge: every line incl. the 3 new ones, the Farming line "12 (F 15 / R 9 / O 12)" with
                skill:farmavg:<uuid>, plain "15" without it, "-" for a missing entry (older SkyySkills), only-new-lines masks, the default
                mask unchanged; linePairs reads the XP flash gain at [28 + k]; Feed.xpShows for the new lines (shown / hidden / temp row);
                the Skills Settings page: 1500 x 998, three Lines rows (ln:0-4 + All on, ln:5-9 + Default, ln:10-12), 20+ px spare,
                toggling ln:10 / ln:12 saves the mask and survives a fresh LayoutStore read
  L24  levels   Widgets.abilModelU with fakes of class:fn:abil (the 48-field 0.1.22 contract) and class:fn:abilPanel (Object[78]):
                "Meteor (Lv 3)" / "Mana Barrier (Lv 12)"; the crouch alts use slots 2 / 3; locked / soon / empty rows keep their name;
                levels off ([8] false), status not "ok", a different slot id, a short answer, a throwing Function, no abilPanel (SkyyClasses
                0.1.21) = the 0.3.23 names; the 5 s cache (one abilPanel call for many model builds, a new call after the TTL);
                the editor sample names carry levels; the real SkyyClasses 0.1.22 / SkyySkills 0.4.37 jars publish the keys the HUD reads
  W24  (in S24 / L24) REVIEW FIX: the worst Farming line (+ an XP flash) and the worst ability rows (Lv 25 + cost + icons) fit their
                clamp boxes (Skills 260, Abilities 290) at 50 / 100 / 170 / 200 % - drawn width == needed width, never cut
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): the look of the longer Farming line / ability names on the real HUD (Skyy looks).
Scratch: tools/dev/scratch/hud24/h (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION, PREV = "0.3.24", "0.3.23"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % PREV)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hud24", "h")))
PKG = "com.skyy.hud."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyHud")
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.37.jar")
CLASSES_JAR = os.path.join(ROOT, "SkyyClasses", "SkyyClasses-0.1.22.jar")
EXPECT = {}
ADDED = []


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def t23():
    return load_module(os.path.join(HERE, "test_skyyhud_0.3.23.py"), "hud0323h")


def ease(out, rules, label, why):
    """rules: [fail-text prefix] - a matching fail of an older harness becomes an ok + a note (re-checked exactly in phase E5S)"""
    d = json.load(open(out))
    keep, eased = [], []
    for f in d["fails"]:
        if any(f.startswith(fr) for fr in rules):
            eased.append(f[:100])
        else:
            keep.append(f)
    d["fails"] = keep
    d["ok"] += len(eased)
    d.setdefault("notes", []).append("%s: %d check(s) eased %s: %s" % (label, len(eased), why, eased))
    json.dump(d, open(out, "w"), indent=1)


E5_SHIFTED = ["E5: BATCH: 40 + 10 Mining XP within 2 s", "E5: 'XP of hidden skills Hide' = no temporary row"]


def run_x20(out, jar, scratch, home):
    t23().run_x20(out, jar, scratch, home)
    ease(out, E5_SHIFTED, "X20", "for 0.3.24's 13 Skills lines (the model's gain slots moved 22 -> 28; re-run exactly with the new indexes in E5S)")


# E5S: the 0.3.20 harness's exec phase with its Skills-model indexes moved to the 13-line layout (gain [22 + k] -> [28 + k], the temp count
# [32] -> [41] = 28 + 13); only its E5 checks count here (every other check runs unchanged in X20)
E5_SUBS = [("m5[23] == \"+50\"", "m5[29] == \"+50\""), ("m5[32] == \"1\" and m5[22] is None", "m5[41] == \"1\" and m5[28] is None"),
           ("m9[23] == \"+1,240\"", "m9[29] == \"+1,240\"")]


def run_e5s(out, jar, scratch, home):
    T = t23()
    sys.argv += ["--old", T.old_jar(scratch, "0.3.19")]
    path = os.path.join(HERE, "test_skyyhud_0.3.20.py")
    src = open(path, encoding="utf8").read()
    for a, b in E5_SUBS:
        assert src.count(a) == 1, a
        src = src.replace(a, b)
    import types
    m = types.ModuleType("hud0320s")
    m.__file__ = path
    exec(compile(src, path, "exec"), m.__dict__)
    m.run_exec(out, jar, os.path.join(scratch, "e5s"), home)
    d = json.load(open(out))
    other = [f for f in d["fails"] if not f.startswith("E5")]
    d["fails"] = [f for f in d["fails"] if f.startswith("E5")]
    d.setdefault("notes", []).append("E5S: the 0.3.20 E5 checks with the 13-line indexes; %d non-E5 fails ignored here (X20 checks them): %s"
                                     % (len(other), [f[:60] for f in other]))
    json.dump(d, open(out, "w"), indent=1)


def run_x19(out, jar, scratch, home):
    t23().run_x19(out, jar, scratch, home)


def run_quest(out, jar, scratch, home):
    t23().run_quest(out, jar, scratch, home)


def run_msg(out, jar, scratch, home):
    t23().run_msg(out, jar, scratch, home)


def run_qk(out, jar, scratch, home):
    t23().run_qk(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    t23().run_live(out, jar, scratch, home)


def _env(scratch):
    """the bare-JVM world the HUD pages need: Unsafe, PlayerRefs, an empty Item asset store, a plugin with an empty huds map"""
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, JAR_IN_USE[0]], verify=True)
    E = {}
    E["UUID"], E["System"], E["CHM"] = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap")
    E["Paths"] = JClass("java.nio.file.Paths")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore24", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore24() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = U.allocateInstance(fake.toClass(AS.class_))
    fm = AS.class_.getDeclaredField("assetMap")
    fm.setAccessible(True)
    fm.set(store, JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")())
    fi_ = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item").class_.getDeclaredField("ASSET_STORE")
    fi_.setAccessible(True)
    fi_.set(None, store)
    H = lambda n: JClass(PKG + n)
    E["H"] = H
    plugin = U.allocateInstance(H("SkyyHudPlugin").class_)
    setf(plugin, H("SkyyHudPlugin"), "huds", E["CHM"]())
    E["plugin"] = plugin
    bridge = E["CHM"]()
    E["System"].getProperties().put("skyy.bridge", bridge)
    E["bridge"] = bridge
    work = os.path.join(scratch, "s24work")
    os.makedirs(work, exist_ok=True)
    E["work"] = work
    H("LayoutStore").DIR = E["Paths"].get(os.path.join(work, "layouts"))
    H("LayoutStore").CACHE.clear()
    cfgdir = os.path.join(work, "cfg")
    os.makedirs(cfgdir, exist_ok=True)
    H("HudCfg").FILE = E["Paths"].get(os.path.join(cfgdir, "config.properties"))
    H("HudCfg").load()

    def pref(n, name="Steve"):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", E["UUID"](0x5ce24, n))
        setf(pr, PRef, "username", name)
        return pr
    E["pref"] = pref

    def page(p):
        b, ev = UCB(), UEB()
        p.build(None, b, ev, None)
        cm = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
               None if c.text is None else str(c.text)] for c in b.getCommands()]
        es = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data)] for e in ev.getEvents()]
        return cm, es
    E["page"] = page
    return E


JAR_IN_USE = [None]


def rows_of(m):
    out = []
    for k in range(13):
        if 3 + 2 * k >= len(m) or m[2 + 2 * k] is None:
            break
        out.append((str(m[2 + 2 * k]), str(m[3 + 2 * k])))
    return out


def run_s24(out, jar, scratch, home):
    from jpype import JClass, JArray, JObject
    JAR_IN_USE[0] = jar
    K = HK.Child(out)
    E = _env(scratch)
    H, bridge = E["H"], E["bridge"]
    WL, Wid, LS, SP, Feed = H("WLayout"), H("Widgets"), H("LayoutStore"), H("SettingsPage"), H("Feed")
    Integer, String = JClass("java.lang.Integer"), JClass("java.lang.String")
    K.eq([str(x) for x in WL.LINE_LABELS], ["Overall Level", "Class skill", "Mining", "Foraging", "Farming", "Alchemy", "Smithing", "Cooking",
                                           "Acrobatics", "Exploration", "Fishing", "Ranching", "Orchard"], "S24 13 lines, the 3 new ones APPENDED (bits 10-12)")
    K.eq((int(WL.LINE_N), int(WL.LINES_DEF), int(WL.LINES_ALL)), (13, 3, 8191), "S24 LINE_N 13, default mask 3 (unchanged), all 8191")
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")
    d = wdef("Skills")
    K.eq((int(d.bw), int(d.bh), int(d.ldef)), (260, 266, 3), "S24 the Skills box 260 x 266 (13 rows; REVIEW FIX: 260 wide, was 180), built-in mask 3")
    me = E["pref"](1, "Mia")
    u = me.getUuid()
    us = str(u)
    # ---- no SkyySkills -> hidden (as before)
    K.eq(str(Wid.skillsModelU(u, 8191)[0]), "K0", "S24 no skill:fn:level -> K0 (hidden)")
    bridge.put("skill:fn:level", String("x"))
    bridge.put("class:list", String("Archer,Mage"))
    bridge.put("class:skill:" + us, String("Archery"))
    bridge.put("skill:overall:" + us, Integer(10))
    full = "Mining:12,Foraging:3,Farming:15,Alchemy:2,Smithing:5,Cooking:11,Acrobatics:7,Exploration:6,Archery:18,Fishing:7,Ranching:9,Orchard:12"
    bridge.put("skill:" + us, String(full))
    bridge.put("skill:farmavg:" + us, Integer(12))
    m = Wid.skillsModelU(u, 8191)
    K.eq(len(m), 28, "S24 the Skills model is String[28] (2 + 2 x 13)")
    K.eq(str(m[0]), "K13", "S24 all lines -> shape K13")
    K.eq(rows_of(m), [("Overall Level", "10"), ("Archery", "18"), ("Mining", "12"), ("Foraging", "3"), ("Farming", "12 (F 15 / R 9 / O 12)"),
                      ("Alchemy", "2"), ("Smithing", "5"), ("Cooking", "11"), ("Acrobatics", "7"), ("Exploration", "6"), ("Fishing", "7"),
                      ("Ranching", "9"), ("Orchard", "12")], "S24 every line; Farming = the average + F / R / O")
    m = Wid.skillsModelU(u, (1 << 10) | (1 << 11) | (1 << 12))
    K.eq((str(m[0]), rows_of(m)), ("K3", [("Fishing", "7"), ("Ranching", "9"), ("Orchard", "12")]), "S24 only the new lines")
    m = Wid.skillsModelU(u, 3)
    K.eq((str(m[0]), rows_of(m)), ("K2", [("Overall Level", "10"), ("Archery", "18")]), "S24 the default mask 3 is unchanged")
    bridge.remove("skill:farmavg:" + us)
    m = Wid.skillsModelU(u, 1 << 4)
    K.eq(rows_of(m), [("Farming", "15")], "S24 no skill:farmavg (SkyySkills older than 0.4.37) -> the plain Farming level")
    bridge.put("skill:farmavg:" + us, String("oops"))
    K.eq(rows_of(Wid.skillsModelU(u, 1 << 4)), [("Farming", "15")], "S24 a broken skill:farmavg -> the plain Farming level")
    bridge.put("skill:farmavg:" + us, Integer(5))
    bridge.put("skill:" + us, String("Mining:12,Farming:15"))
    K.eq(rows_of(Wid.skillsModelU(u, (1 << 4) | (1 << 10) | (1 << 11) | (1 << 12))),
         [("Farming", "5 (F 15 / R - / O -)"), ("Fishing", "-"), ("Ranching", "-"), ("Orchard", "-")], "S24 missing entries -> '-' (older SkyySkills)")
    bridge.put("skill:" + us, String(full))
    bridge.put("skill:farmavg:" + us, Integer(12))
    # ---- linePairs: the XP flash gain of row k at [28 + k]
    lm = list(Wid.skillsModelU(u, 8191)) + [None] * 14
    lm[28 + 12] = "+9"
    lp = [str(x) for x in Wid.linePairs("Skills", JArray(String)(lm))]
    pairs = dict(zip(lp[0::2], lp[1::2]))
    K.check(pairs.get("N12") == "Orchard" and pairs.get("X12") == "+9" and pairs.get("X0") == "" and pairs.get("S4") == "12 (F 15 / R 9 / O 12)",
            "S24 linePairs: N12 Orchard, X12 = the gain at [40], S4 the Farming text: %s" % {k: pairs.get(k) for k in ("N12", "X12", "X0", "S4")})
    # ---- REVIEW FIX W24: the worst Farming row fits the Skills clamp box (never cut) at 50 / 100 / 170 / 200 %
    bridge.put("skill:" + us, String("Mining:12,Foraging:3,Farming:40,Alchemy:2,Smithing:5,Cooking:11,Acrobatics:7,Exploration:6,Archery:18,"
                                     "Fishing:7,Ranching:25,Orchard:34"))
    bridge.put("skill:farmavg:" + us, Integer(33))
    wm = list(Wid.skillsModelU(u, 8191))
    K.eq(dict(rows_of(wm)).get("Farming"), "33 (F 40 / R 25 / O 34)", "W24 the two-digit Farming line")
    wm = wm + [None] * 14
    wm[28 + 4] = "+9,999"                    # an XP flash on the Farming row (row 4 with every line on)
    wm = JArray(String)(wm)
    for sc in (50, 100, 170, 200):
        need = int(Wid.innerW("Skills", wm, sc, 6, True)) + 2 * int(Wid.padMl(sc, 6))
        got = int(Wid.multiW("Skills", d, wm, sc, 6))
        K.check(need <= int(d.bw) * sc // 100 and got == need,
                "W24 Skills at %d %%: 'Farming  33 (F 40 / R 25 / O 34)' + '+9,999' needs %d px, drawn %d, cap %d" % (sc, need, got, int(d.bw) * sc // 100))
        if sc == 100:
            K.check(need > 180, "W24 ... (%d px: the old 180 cap cut it - the fix is needed)" % need)
    bridge.put("skill:" + us, String(full))
    bridge.put("skill:farmavg:" + us, Integer(12))
    # ---- Feed.xpShows for the new skills
    cache = E["CHM"]()
    lay = wdef("Skills")
    lay.lines = 3 | (1 << 10)
    lay.opt = False
    cache.put("Skills", lay)
    LS.CACHE.put(u, cache)
    K.eq([bool(Feed.xpShows(u, s)) for s in ("Fishing", "Ranching", "Orchard", "Archery")], [True, False, False, True],
         "S24 xpShows: Fishing shown (bit 10), Ranching / Orchard not (temp rows off), the class line")
    lay.opt = True
    K.eq([bool(Feed.xpShows(u, s)) for s in ("Ranching", "Orchard")], [True, True], "S24 xpShows: hidden skills as temp rows when opt (Show)")
    LS.CACHE.clear()
    # ---- the Skills Settings page
    E["H"]("LayoutStore").get(u)
    cm, es = E["page"](SP(me, E["plugin"], "Skills"))
    K.check(cm and "Anchor: (Width: 1500, Height: 998)" in (cm[0][3] or ""), "S24 the Skills Settings page is 1500 x 998: %s" % (cm[0][3][:80] if cm else None))
    lnb = [(e[1], e[2]) for e in es if e[1] and e[1].startswith("#SkyySetLn")]
    want = [("#SkyySetLn%d" % k, '"ln:%d"' % k) for k in range(5)] + [("#SkyySetLnAll", '"lnall"')] + \
           [("#SkyySetLn%d" % k, '"ln:%d"' % k) for k in range(5, 10)] + [("#SkyySetLnDef", '"lndef"')] + \
           [("#SkyySetLn%d" % k, '"ln:%d"' % k) for k in range(10, 13)]
    K.check(len(lnb) == len(want) and all(g[0] == w[0] and w[1] in (g[1] or "") for g, w in zip(lnb, want)),
            "S24 three Lines rows: ln:0-4 + All on, ln:5-9 + Default, ln:10-12: %s" % lnb)
    rows = [c[3] for c in cm if c[0] == "AppendInline" and c[1] == "#SkyySet" and c[3] and "SkyySetRowLn" in c[3]]
    K.eq(len([r for r in rows if re.match(r"Group #SkyySetRowLn\d ", r)]), 3, "S24 three #SkyySetRowLn<n> rows")
    K.check(any("TextButton #SkyySetLn12 " in (c[3] or "") and 'Text: "Orchard"' in (c[3] or "") for c in cm), "S24 the Orchard button")
    # the page's rows fit (LayoutMode Top: the direct children of #SkyySet stack)
    root = [c for c in cm if c[0] == "AppendInline" and c[1] is None and c[3] and c[3].startswith("Group #SkyySet {")]
    ph = int(re.search(r"Height: (\d+)\)", root[0][3]).group(1))
    pad = int(re.search(r"Vertical: (\d+)\)", root[0][3]).group(1))
    tot = 0
    for c in cm:
        if c[0] == "AppendInline" and c[1] == "#SkyySet" and c[3]:
            ma = re.match(r"\s*(?:Group|Label|TextButton)(?:\s+#[A-Za-z0-9]+)?\s*\{\s*Anchor: \(([^)]*)\)", c[3])
            hv = re.search(r"Height: (\d+)", ma.group(1)) if ma else None
            tot += int(hv.group(1)) if hv else 0
    spare = ph - 2 * pad - tot
    K.check(spare >= 20 and ph <= 1080, "S24 Settings rows %d + padding 2 x %d in %d -> %d px spare (>= 20), fits 1080" % (tot, pad, ph, spare))
    sp = SP(me, E["plugin"], "Skills")
    sp.handleDataEvent(None, None, '{"a":"ln:10"}')
    sp.handleDataEvent(None, None, '{"a":"ln:12"}')
    K.eq(int(LS.get(u).get("Skills").lines), 3 | (1 << 10) | (1 << 12), "S24 ln:10 + ln:12 -> mask 3 + Fishing + Orchard")
    LS.CACHE.clear()
    K.eq(int(LS.get(u).get("Skills").lines), 3 | (1 << 10) | (1 << 12), "S24 ... saved (a fresh read of the layout file)")
    sp = SP(me, E["plugin"], "Skills")
    sp.handleDataEvent(None, None, '{"a":"lnall"}')
    K.eq(int(LS.get(u).get("Skills").lines), 8191, "S24 All on = all 13 lines")
    lit = sorted(re.search(r"#(SkyySetLn\w+)", c[3]).group(1) for c in E["page"](SP(me, E["plugin"], "Skills"))[0]
                 if c[0] == "AppendInline" and c[3] and "TextButton #SkyySetLn" in c[3] and "Background: #7fe07f" in c[3])
    K.check("SkyySetLnAll" in lit and "SkyySetLn12" in lit and len(lit) == 14, "S24 All on lights 13 lines + All on: %s" % lit)
    K.save()


def _panel(ids, lvls, ok="ok", levels=True, n=78):
    from jpype import JClass, JArray, JObject
    Integer, Boolean, String = JClass("java.lang.Integer"), JClass("java.lang.Boolean"), JClass("java.lang.String")
    a = [None] * n
    if n > 0:
        a[0] = String(ok)
    if n > 8:
        a[8] = Boolean(levels)
    for i in range(4):
        b = 12 + 16 * i
        if b + 6 < n:
            a[b] = String(ids[i])
            a[b + 6] = Integer(lvls[i])
    return JArray(JObject)(a)


def run_l24(out, jar, scratch, home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    JAR_IN_USE[0] = jar
    K = HK.Child(out)
    E = _env(scratch)
    H, bridge = E["H"], E["bridge"]
    Wid = H("Widgets")
    Long, Double, Boolean, String = JClass("java.lang.Long"), JClass("java.lang.Double"), JClass("java.lang.Boolean"), JClass("java.lang.String")

    @JImplements("java.util.function.Function")
    class AbilFake(object):
        """class:fn:abil, the 48-field SkyyClasses 0.1.22 contract (tools/classes_0_1_22_patch.py AbilFn)"""
        def __init__(self):
            self.d = {"names": ["Meteor", "Mana Barrier", "Frost Nova", "Starfall"], "ids": ["Meteor", "ManaBarrier", "FrostNova", "Starfall"],
                      "state": ["ready", "cooldown", "ready", "locked"], "left": [0, 4000, 0, 0], "total": [0, 10000, 0, 0], "crouch": False}

        @JOverride
        def apply(self, x):
            d = self.d
            a = [None] * 48
            for i in range(4):
                a[i * 4] = String(d["names"][i])
                a[i * 4 + 1] = Long(d["left"][i])
                a[i * 4 + 2] = Long(d["total"][i])
                a[i * 4 + 3] = String(d["state"][i])
                a[16 + i] = String(d["ids"][i])
                a[20 + i] = Double(d.get("mana", 23.0))
                a[24 + i] = Double(d.get("stam", 0.0))
                a[28 + i] = Boolean(True)
                a[38 + i] = Long(20)
            a[32] = Boolean(d["crouch"])
            a[33] = String("Mage")
            a[36] = Boolean(False)
            a[37] = String("abil2")
            a[44] = String("walk")
            a[45] = Boolean(True)
            a[46] = String("abil3")
            return JArray(JObject)(a)

    @JImplements("java.util.function.Function")
    class PanelFake(object):
        def __init__(self):
            self.calls = 0
            self.r = None
            self.boom = False

        @JOverride
        def apply(self, x):
            self.calls += 1
            if self.boom:
                raise RuntimeError("boom")
            return self.r
    afn, pfn = AbilFake(), PanelFake()
    me = E["pref"](2, "Ana")
    u = me.getUuid()
    bridge.put("class:fn:abil", afn)

    def names(icons=False):
        Wid.ALVC.clear()
        m = Wid.abilModelU(u, icons)
        return str(m[2]), str(m[7]), str(m[1])
    # ---- no class:fn:abilPanel (SkyyClasses 0.1.21): the 0.3.23 names
    K.eq(names()[:2], ("Meteor", "Mana Barrier"), "L24 no class:fn:abilPanel -> the 0.3.23 names")
    bridge.put("class:fn:abilPanel", pfn)
    pfn.r = _panel(["Meteor", "ManaBarrier", "FrostNova", "Starfall"], [3, 12, 1, 1])
    n0, n1, head = names()
    K.eq((n0, n1), ("Meteor (Lv 3)", "Mana Barrier (Lv 12)"), "L24 the primaries carry their levels")
    K.check(head.startswith("Meteor (Lv 3) "), "L24 the headline too: %s" % head)
    m = Wid.abilModelU(u, False)
    K.check(str(m[8]) == "4s" and m[9] is not None, "L24 the cooldown row keeps its countdown + bar: %s / %s" % (m[8], m[9]))
    afn.d["crouch"] = True
    K.eq(names()[:2], ("Frost Nova (Lv 1)", "Starfall"), "L24 crouch: the alts (slots 2 / 3); locked Starfall keeps its name (its 'Lv 20' = the class level)")
    afn.d["crouch"] = False
    afn.d["state"] = ["soon", "empty", "ready", "ready"]
    K.eq(names()[:2], ("Meteor", "-"), "L24 a Soon row and an empty row get no level")
    afn.d["state"] = ["passive", "cooldown", "ready", "locked"]
    K.eq(names()[0], "Meteor (Lv 3)", "L24 a passive row shows its level")
    afn.d["state"] = ["ready", "cooldown", "ready", "locked"]
    pfn.r = _panel(["Meteor", "ManaBarrier", "FrostNova", "Starfall"], [3, 12, 1, 1], levels=False)
    K.eq(names()[:2], ("Meteor", "Mana Barrier"), "L24 levels off ([8] false) -> no level")
    pfn.r = _panel(["Meteor", "ManaBarrier", "FrostNova", "Starfall"], [3, 12, 1, 1], ok="noabil")
    K.eq(names()[:2], ("Meteor", "Mana Barrier"), "L24 status not 'ok' -> no level")
    pfn.r = _panel(["Starfall", "ManaBarrier", "FrostNova", "Meteor"], [3, 12, 1, 1])
    K.eq(names()[:2], ("Meteor", "Mana Barrier (Lv 12)"), "L24 a different id in the panel slot -> no level on that row")
    pfn.r = _panel(["Meteor", "ManaBarrier", "FrostNova", "Starfall"], [3, 12, 1, 1], n=40)
    K.eq(names()[:2], ("Meteor", "Mana Barrier"), "L24 a short answer -> no level")
    pfn.r = String("odd")
    K.eq(names()[:2], ("Meteor", "Mana Barrier"), "L24 not an Object[] -> no level")
    pfn.r = _panel(["Meteor", "ManaBarrier", "FrostNova", "Starfall"], [0, 12, 1, 1])
    K.eq(names()[:2], ("Meteor", "Mana Barrier (Lv 12)"), "L24 level 0 -> no level on that row")
    pfn.boom = True
    K.eq(names()[:2], ("Meteor", "Mana Barrier"), "L24 a throwing abilPanel -> the 0.3.23 names, no exception")
    pfn.boom = False
    # ---- the 5 s cache
    pfn.r = _panel(["Meteor", "ManaBarrier", "FrostNova", "Starfall"], [3, 12, 1, 1])
    Wid.ALVC.clear()
    c0 = pfn.calls
    for _ in range(25):
        Wid.abilModelU(u, False)
    K.eq(pfn.calls - c0, 1, "L24 25 model builds within 5 s -> ONE abilPanel call")
    pfn.r = _panel(["Meteor", "ManaBarrier", "FrostNova", "Starfall"], [4, 12, 1, 1])
    K.eq(str(Wid.abilModelU(u, False)[2]), "Meteor (Lv 3)", "L24 ... the cached level until the TTL")
    e = Wid.ALVC.get(u)
    e[0] = Long(int(e[0]) - 6000)
    K.eq(str(Wid.abilModelU(u, False)[2]), "Meteor (Lv 4)", "L24 after 5 s a new call -> the level-up shows")
    K.eq(pfn.calls - c0, 2, "L24 ... exactly one more call")
    K.eq(int(Wid.ALV_TTL), 5000, "L24 ALV_TTL 5000 ms")
    # ---- no class:fn:abil -> nothing asked
    bridge.remove("class:fn:abil")
    Wid.ALVC.clear()
    c1 = pfn.calls
    K.eq(str(Wid.abilModelU(u, False)[0]), "A0", "L24 no class:fn:abil -> hidden (A0)")
    K.eq(pfn.calls, c1, "L24 ... and abilPanel is never asked")
    bridge.put("class:fn:abil", afn)
    # ---- the editor / Settings sample
    s = Wid.abilSample(False)
    K.eq((str(s[2]), str(s[7])), ("Meteor (Lv 3)", "Mana Barrier (Lv 1)"), "L24 the sample names carry levels (the real width in the editor)")
    # ---- REVIEW FIX W24: the worst real rows fit the Abilities clamp box (never cut): the longest names at abil.maxLevel 25 with a
    # "NN Mana + N Stam" cost and the icon column, at 50 / 100 / 170 / 200 %
    wdef = getattr(Wid, "def_", None) or getattr(Wid, "def")
    da = wdef("Abilities")
    K.eq((int(da.bw), int(da.bh)), (290, 59), "W24 the Abilities box 290 x 59 (REVIEW FIX: 290 wide, was 220)")
    save = dict(afn.d)
    afn.d.update({"names": ["Shield Bubble", "Martyr's Grace", "Guardian Spirit", "Sanctuary"],
                  "ids": ["ShieldBubble", "MartyrsGrace", "GuardianSpirit", "Sanctuary"],
                  "state": ["ready", "ready", "passive", "ready"], "left": [0, 0, 0, 0], "total": [0, 0, 0, 0], "mana": 99.0, "stam": 9.0})
    pfn.r = _panel(["ShieldBubble", "MartyrsGrace", "GuardianSpirit", "Sanctuary"], [25, 25, 25, 25])
    Wid.ALVC.clear()
    am = list(Wid.abilModelU(u, True))
    K.eq((str(am[2]), str(am[3]), str(am[7])), ("Shield Bubble (Lv 25)", "99 Mana + 9 Stam", "Martyr's Grace (Lv 25)"), "W24 the worst rows")
    am[13] = "1"                             # the icon column on (worst case, whether or not the icons resolve here)
    am = JArray(String)(am)
    for sc in (50, 100, 170, 200):
        need = int(Wid.innerW("Abilities", am, sc, 6, True)) + 2 * int(Wid.padMl(sc, 6))
        got = int(Wid.multiW("Abilities", da, am, sc, 6))
        K.check(need <= int(da.bw) * sc // 100 and got == need,
                "W24 Abilities at %d %%: the Lv 25 rows + cost + icons need %d px, drawn %d, cap %d" % (sc, need, got, int(da.bw) * sc // 100))
        if sc == 100:
            K.check(need > 220, "W24 ... (%d px: the old 220 cap cut it - the fix is needed)" % need)
    afn.d.clear()
    afn.d.update(save)
    Wid.ALVC.clear()
    # ---- the real jars publish what the HUD reads
    def consts(jarp):
        z = zipfile.ZipFile(jarp)
        return b"".join(z.read(n) for n in z.namelist() if n.endswith(".class"))
    if os.path.isfile(CLASSES_JAR):
        cb = consts(CLASSES_JAR)
        K.check(b"class:fn:abilPanel" in cb and b"class:fn:abil" in cb, "L24 SkyyClasses 0.1.22 puts class:fn:abilPanel + class:fn:abil")
    else:
        K.check(False, "L24 SkyyClasses 0.1.22 jar missing: %s" % CLASSES_JAR)
    if os.path.isfile(SKILLS_JAR):
        sb = consts(SKILLS_JAR)
        K.check(b"skill:farmavg:" in sb and b"Ranching" in sb and b"Orchard" in sb and b"Fishing" in sb,
                "L24 SkyySkills 0.4.37 publishes skill:farmavg:<uuid> and the Fishing / Ranching / Orchard labels")
    else:
        K.check(False, "L24 SkyySkills 0.4.37 jar missing: %s" % SKILLS_JAR)
    K.save()


EXPECT.update({
    # the 13 Skills lines: the labels, LINE_N / LINES_ALL (static finals inlined where they are read), the model size 28, the temp slot 41
    "WLayout": ["~<clinit>"],
    "Widgets": ["+f ALVC", "+f ALVCALLS", "+f ALV_TTL", "+m abilLevels", "+m abilLvName", "+m abilLvOf", "+m farmVal", "~<clinit>",
                "~m abilModelU", "~m abilSample", "~m def", "~m innerW", "~m linePairs", "~m model", "~m modelL", "~m skillRows",
                "~m skillsBody", "~m skillsModelU", "~m skillsModelX", "~m skillsSample", "~m skillsVis"],
    "Feed": ["~m xpShows"],                    # LINE_N 13 / the temp-row room (@LN@)
    "HudMain": ["~m feedFill"],                # the flash slots at [28 + k]
    "SettingsPage": ["~m build", "~m handleDataEvent"],   # three Lines rows, 998 px; ln:<k> up to 12, All on = 8191
    # the version string (the kit's header / export, the ready line)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
})

if __name__ == "__main__":
    HK.run("SkyyHud", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("x20", run_x20), ("e5s", run_e5s), ("x19", run_x19), ("quest", run_quest), ("msg", run_msg), ("qk", run_qk), ("s24", run_s24), ("l24", run_l24),
            ("live", run_live)],
           os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyHud"))
