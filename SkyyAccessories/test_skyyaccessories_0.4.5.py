"""Bare-JVM + render check for SkyyAccessories 0.4.5 (the vanilla-look restyle of the Accessory Bag page), kept next to the build so
the build report's JVM and render claims can be re-run by anyone (review fix1b: the first render compare lived in a deleted scratch).

    python SkyyAccessories/test_skyyaccessories_0.4.5.py [--jar <SkyyAccessories-0.4.5.jar>] [--dir <scratch folder>] [--keep]

Build first (python tools/acc_0_4_5_patch.py, then python SkyyAccessories/build_skyyaccessories_0.4.5.py). A child process starts a
fresh JVM (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar read-only + the jar + tools/javassist.jar on the
classpath; TEMP / TMP / java.io.tmpdir in the scratch folder) and checks:
  A  every class of the jar loads and verifies
  B  the page's REAL build(): the build script's ACC PAGE block and ACC_BUILD_SRC are exec'd here (the kit verified first) and the
     build() source is compiled once more into a probe class. Only the state lines are swapped (each asserted once): the player,
     the profile key, the bag snapshot and the carried list come from fields. Everything else runs as built - the kit markup, the
     loops, the 0.4.4 cap rule (the jar's AccStore.capOf with AccStore.SLOTS set per state), the bindings, invIds and the jar's own
     AccDefs / AccStore / AccPage.safe / AccPage.infoColor. For each state the engine's own UICommandBuilder / UIEventBuilder
     output must equal acc_page_state() command for command (appendInline selector + markup, set selector + text); every appended
     markup passes SUI.check_markup and every state SUI.check_page; the events are exactly the filled shown slots (un:<i>) and the
     first 6 inventory rows (eq:<i>), 0.4.4's EventData; invIds = the carried list.
  C  AccPage.infoColor on the real result texts (AccDefs.retiredWhy, AccStore.moveBlock through a bridge map, the handleDataEvent
     texts built from the jar's own names): done green, refused red, notes and the Campfire line info blue
  D  the texts reach the page as they are (commas, colons, quotes: b.set never parses markup); ItemIds in the markup still go
     through AccPage.safe
  E  text fit (only when the client font atlas exists, read-only): every accessory name at 18 px bold fits the 376 px name column,
     the rarity words, heads, hint, bonuses and results fit their labels (Nunito Sans advances: Medium, ExtraBold for bold)
Not testable without the game: the look itself (open the kit's base probe pages first), the client parsing the page, real inventories.
Nothing is deployed. Default scratch folder: tools/dev/scratch/skyyaccessories-045 (git-ignored), deleted at the end unless --keep.
Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.4.5"
BUILD = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "skyyaccessories-045")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def script_parts():
    """The build script's class-name constants, CAP / INV_ROWS and the text from the ACC PAGE block start up to (not including) the
    verbatim assert after ACC_BUILD_SRC - exec'd in the child with SUI verified."""
    src = open(BUILD, encoding="utf8").read()
    consts = {}
    for name in ("PKG", "REF", "UCB", "UEB", "ST", "PLA", "BT", "EVD"):
        m = re.search(r'^%s\s*=\s*"([^"]+)"' % name, src, re.M)
        consts[name] = m.group(1)
    for name in ("CAP", "INV_ROWS"):
        consts[name] = int(re.search(r"^%s = (\d+)" % name, src, re.M).group(1))
    a = src.index("# ---- ACC PAGE BLOCK START")
    b = src.index("for _piece in (ACC_TOP_JAVA,")
    return consts, src[a:b]


# ============================================================================================================== child: the checks
def run(jar):
    import jpype
    import skyybuild as B
    import skyyui as SUI
    from jpype import JClass, JArray, JString
    import zipfile
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, jar, B.JAVASSIST], convertStrings=True)

    # ---------------- A. load + verify
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            FAILS.append("load " + n + ": " + str(e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified %d classes (-Xverify:all)" % len(names))
    if FAILS:
        return

    consts, block = script_parts()
    P = consts["PKG"]
    Defs, Store, Page = JClass(P + ".AccDefs"), JClass(P + ".AccStore"), JClass(P + ".AccPage")
    UUID, ArrayList = JClass("java.util.UUID"), JClass("java.util.ArrayList")
    System = JClass("java.lang.System")

    # ---------------- B. the real build() against the kit's acc_page_state()
    SUI.verify(quiet=True)
    ns = dict(consts, SUI=SUI, KIT_ID=SUI.kit_id())
    exec(compile(block, BUILD + " [ACC PAGE block]", "exec"), ns)
    src = ns["ACC_BUILD_SRC"]
    swaps = [("public void build(%s ref, %s b, %s ev, %s st) {" % (consts["REF"], consts["UCB"], consts["UEB"], consts["ST"]),
              "public void build(%s b, %s ev) {" % (consts["UCB"], consts["UEB"])),
             ("  java.util.UUID u = this.playerRef.getUuid();\n", ""),
             ("  %s player = (%s) st.getComponent(ref, %s.getComponentType());\n" % (consts["PLA"], consts["PLA"], consts["PLA"]), ""),
             ("  this.key = %s.AccStore.pkey(u);   // 0.4.1\n" % P, ""),
             ("String[] s = %s.AccStore.snapshot(u);" % P, "String[] s = this.snap;"),
             ("java.util.ArrayList inv = player == null ? new java.util.ArrayList() : carried(player);", "java.util.ArrayList inv = this.inv;")]
    for a, b in swaps:
        check(src.count(a) == 1, "probe swap anchor once in build(): " + a.strip()[:70])
        src = src.replace(a, b)
    src, n1 = re.subn(r"(?<![\w.])safe\(", P + ".AccPage.safe(", src)
    src, n2 = re.subn(r"(?<![\w.])infoColor\(", P + ".AccPage.infoColor(", src)
    check(n1 == 2 and n2 == 1, "build() calls safe() twice (the 2 ItemIds) and infoColor() once: %d / %d" % (n1, n2))
    check(not any(x in src for x in ("playerRef", "player", "carried(", " st.", "(u)")), "probe: no engine state left in build()")
    check(ns["ACC_INFO_COLOR_SRC"].strip().startswith("public static String infoColor(String t)"), "ACC_INFO_COLOR_SRC is infoColor")
    pool = JClass("javassist.ClassPool")(True)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    cc = pool.makeClass("skyytest.AccRenderProbe")
    for f in ("public String info;", "public String[] invIds;", "public String[] snap;", "public java.util.ArrayList inv;"):
        cc.addField(CtField.make(f, cc))
    cc.addConstructor(CtNewConstructor.defaultConstructor(cc))
    cc.addMethod(CtNewMethod.make(src, cc))
    out = os.path.join(SCRATCH, "probe-classes")
    os.makedirs(out, exist_ok=True)
    cc.writeFile(out)
    URL = JArray(JClass("java.net.URL"))(1)
    URL[0] = JClass("java.io.File")(out).toURI().toURL()
    Probe = JClass("skyytest.AccRenderProbe", loader=JClass("java.net.URLClassLoader")(URL, loader))
    UCB, UEB = JClass(consts["UCB"]), JClass(consts["UEB"])
    JRE = SUI._J_RE        # the kit's J() marker pattern (the harness resolves the one runtime colour J the page keeps)

    for t in ("Skyy_Talisman_Vitality_Legendary", "Skyy_Accessory_Workbench_T3", "Skyy_Accessory_Alchemybench_T2",
              "Skyy_Talisman_Intelligence_Artifact", "Skyy_Accessory_Omni", "Skyy_Accessory_Campfire_T1"):
        check(bool(Defs.isAccessory(t)), "test id is an accessory: " + t)

    def java_state(snap, slots_limit, inv, info):
        Store.SLOTS = slots_limit
        p = Probe()
        arr = JArray(JString)(len(snap))
        for i, v in enumerate(snap):
            arr[i] = v
        p.snap = arr
        lst = ArrayList()
        for v in inv:
            lst.add(v)
        p.inv = lst
        p.info = info
        b, ev = UCB(), UEB()
        p.build(b, ev)
        cmds = []
        for c in b.getCommands():
            typ = str(c.type)
            if typ == "Set":
                cmds.append((typ, str(c.selector), json.loads(str(c.data))["0"]))
            else:
                cmds.append((typ, None if c.selector is None else str(c.selector), str(c.text)))
        evs = [(str(e.type), str(e.selector), str(e.data), bool(e.locksInterface)) for e in ev.getEvents()]
        ids = [None if x is None else str(x) for x in p.invIds]
        Store.SLOTS = consts["CAP"]
        return cmds, evs, ids

    def upper(t):     # Java's toUpperCase on the (ASCII) rarity words; strings arrive as Python str (convertStrings)
        assert all(ord(c) < 128 for c in str(t)), t
        return str(t).upper()

    def row(i):
        """One row's values as build() computes them, each wrapped as a J("v.<what>", value): build() passes runtime values (so its
        texts are ALWAYS b.set, never inline), and the kit output must be made the same way; the value is the J sample, which is
        what the resolved markup shows."""
        return (SUI.J("v.item", str(Page.safe(i))), SUI.J("v.name", str(Defs.pretty(i))), SUI.J("v.rarity", upper(Defs.rarityName(i))),
                SUI.J("v.colour", str(Defs.rarityColor(i))))

    def expected(snap, slots_limit, inv, info):
        s = JArray(JString)(len(snap))
        for i, v in enumerate(snap):
            s[i] = v
        Store.SLOTS = slots_limit
        cap = int(Store.capOf(s))
        Store.SLOTS = consts["CAP"]
        bonus = str(Defs.bonusText(s))
        shown = info if info else str(Store.campLine(s))
        slots = [(i, None if v is None else row(v)) for i, v in enumerate(snap) if not (i >= cap and v is None)]
        chunks = ns["acc_page_state"](SUI.J("v.bonus", bonus), SUI.J("v.info", shown), slots, [row(v) for v in inv])
        ns["acc_page_check"](chunks)
        colour = str(Page.infoColor(info))

        def res(v):
            def sub(m):
                if m.group(1) == ns["ACC_INFO_COLOR"]:
                    return colour              # the one runtime value the kit page keeps: the result line's colour
                if m.group(1).startswith("v."):
                    return m.group(2)          # a state value (its sample is the value)
                raise AssertionError("unresolved runtime value in the kit markup: " + m.group(1))
            return JRE.sub(sub, v)
        cmds = []
        for ch in chunks:
            for parent, mk in ch:
                cmds.append(("AppendInline", None if parent is None else "#" + parent, res(mk)))
            for ident, prop, val in ch.sets:
                cmds.append(("Set", "#%s.%s" % (ident, prop), res(val)))
        evs = [("Activating", "#SkyyAccUn%d" % i, '{"a": "un:%d"}' % i, True) for i, v in slots if v is not None]
        evs += [("Activating", "#SkyyAccEq%d" % i, '{"a": "eq:%d"}' % i, True) for i in range(min(len(inv), consts["INV_ROWS"]))]
        ids = list(inv[:consts["INV_ROWS"]]) + [None] * max(0, len(inv) - consts["INV_ROWS"])
        return cmds, evs, ids, shown, bonus

    N = None
    tal = lambda f, r: "Skyy_Talisman_%s_%s" % (f, r)
    full9 = [tal("Vitality", "Legendary"), tal("Endurance", "Epic"), tal("Intelligence", "Rare"), tal("Regeneration", "Uncommon"),
             tal("Speed", "Common"), "Skyy_Accessory_Workbench_T3", "Skyy_Accessory_Omni", "Skyy_Accessory_Campfire_T1",
             tal("Vitality", "Ring")]
    inv7 = ["Skyy_Accessory_Furnace_T1", tal("Speed", "Epic"), "Skyy_Accessory_Workbench_T1", tal("Intelligence", "Artifact"),
            tal("Endurance", "Legendary"), "Skyy_Accessory_Anvil_T1" if bool(Defs.isAccessory("Skyy_Accessory_Anvil_T1")) else tal("Regeneration", "Rare"),
            "Skyy_Accessory_Alchemybench_T1"]
    why = "bag is full, or the same or a better Vitality talisman is already equipped"
    states = [
        ("full bag + 7 carried", full9, 9, inv7, "equipped " + str(Defs.pretty(tal("Speed", "Epic")))),
        ("empty bag, nothing carried", [N] * 9, 9, [], ""),
        ("cap 5, slot 7 filled above the cap", [tal("Speed", "Rare"), N, "Skyy_Accessory_Workbench_T2", N, N, N, N, tal("Vitality", "Epic"), N],
         5, ["Skyy_Accessory_Furnace_T1", tal("Endurance", "Common")], "your inventory is full"),
        ("campfire line (no result yet)", ["Skyy_Accessory_Campfire_T1"] + [N] * 8, 9, [], ""),
        ("comma-heavy result", [tal("Vitality", "Legendary")] + [N] * 8, 9, ["Skyy_Accessory_Cookingbench_T1", tal("Vitality", "Rare")], why),
        ("retired only", [N, "Skyy_Accessory_Alchemybench_T2"] + [N] * 7, 9, ["Skyy_Accessory_Alchemybench_T1", "Skyy_Accessory_Cookingbench_T1"],
         str(Defs.retiredWhy("Skyy_Accessory_Alchemybench_T1"))),
        ("cap 1, every slot filled", full9, 1, inv7[:6], "upgraded to Legendary Vitality Talisman - Epic Vitality Talisman could not be "
         "returned - reported to the server log"),
        ("profile switched note", [tal("Speed", "Legendary"), N, N] + [N] * 6, 9, [tal("Speed", "Epic")],
         "your profile changed - this is the bag of your current profile now"),
    ]
    total_cmds = 0
    for name, snap, lim, inv, info in states:
        got, gev, gids = java_state(snap, lim, inv, info)
        exp, eev, eids, shown, bonus = expected(snap, lim, inv, info)
        total_cmds += len(got)
        same = got == exp
        if not same:
            for k in range(max(len(got), len(exp))):
                g = got[k] if k < len(got) else None
                e = exp[k] if k < len(exp) else None
                if g != e:
                    print("  first difference at command %d:\n    build(): %r\n    kit    : %r" % (k, g, e))
                    break
        check(same, "B %s: build() = acc_page_state() (%d / %d commands)" % (name, len(got), len(exp)))
        check(gev == eev, "B %s: events %r" % (name, gev))
        check(gids == eids, "B %s: invIds %r" % (name, gids))
        for typ, sel, v in got:
            if typ == "AppendInline":
                try:
                    SUI.check_markup(v, ns["ACC_PREFIX"], root=sel is None)
                    OKS[0] += 1
                except Exception as e:
                    check(False, "B %s: check_markup %s: %s" % (name, sel, e))
        sets = dict((sel, v) for typ, sel, v in got if typ == "Set")
        check(sets.get("#SkyyAccInfo.Text") == shown and sets.get("#SkyyAccBonus.Text") == bonus, "B %s: info / bonus texts" % name)
        if name == "comma-heavy result":            # D: the commas survive now (0.4.4's safe() blanked them)
            check(sets.get("#SkyyAccInfo.Text") == why and "," in sets["#SkyyAccInfo.Text"], "D the result shows its comma")
        if name == "campfire line (no result yet)":
            check(sets.get("#SkyyAccInfo.Text", "").startswith("Campfire quick cook"), "B the Campfire line shows while no result is set")
    print("B. %d states, %d engine commands compared with the kit's output" % (len(states), total_cmds))

    # ---------------- C. infoColor on the real result texts
    OK, NO, EQ = SUI.STATUS["+"], SUI.STATUS["-"], SUI.STATUS["="]
    pv, pe = str(Defs.pretty(tal("Vitality", "Epic"))), str(Defs.pretty(tal("Vitality", "Ring")))
    bridge = Store.bridge()
    u = UUID.randomUUID()
    check(Store.moveBlock(u) is None, "moveBlock: nothing blocks without SkyyProfiles keys")
    bridge.put("profile:busy:" + str(u), "1")
    busy = str(Store.moveBlock(u))
    bridge.remove("profile:busy:" + str(u))
    bridge.put("profile:fn:key", "x")
    unk = str(Store.moveBlock(u))
    bridge.remove("profile:fn:key")
    texts = [(None, EQ), ("", EQ), ("your profile changed - this is the bag of your current profile now", EQ),
             (busy, NO), (unk, NO), ("your inventory is full", NO),
             ("unequipped " + pv, OK), ("unequipped " + pv + " - your old " + pe + " came back as the new upgradable talisman", OK),
             (str(Defs.retiredWhy("Skyy_Accessory_Alchemybench_T1")), NO), (str(Defs.retiredWhy("Skyy_Accessory_Cookingbench_T1")), NO),
             (why, NO), (why + " - it was kept in a free bag slot", NO), ("could not find " + pv + " in your inventory", NO),
             ("could not give " + pv + " back - inventory and bag full, reported to the server log", NO),
             ("upgraded to " + pv + " - " + pe + " returned", OK), ("upgraded to " + pv + " - " + pe + " kept in the bag - inventory full", OK),
             ("upgraded to " + pv + " - " + pe + " could not be returned - reported to the server log", NO),
             ("equipped " + pv, OK), ("equipped " + pv + " - converted from your old " + pe, OK)]
    for t, c in texts:
        check(str(Page.infoColor(t)) == c, "C infoColor(%r) = %s" % (t, c))
    check(busy.startswith("your profile is still loading") and unk.startswith("your profile is not loaded"), "C moveBlock texts")
    print("C. infoColor checked on %d result texts" % len(texts))

    # ---------------- D. safe() still guards the ItemIds written into the markup
    check(str(Page.safe('a,b:c;d{e}"f')) == "a b c d(e) f", "D AccPage.safe unchanged (0.4.4's)")

    # ---------------- E. text fit (client font atlas, read-only)
    fonts = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Client", "Data", "Shared", "UI", "Fonts")
    reg, bold = os.path.join(fonts, "NunitoSans-Medium.json"), os.path.join(fonts, "NunitoSans-ExtraBold.json")
    if not (os.path.exists(reg) and os.path.exists(bold)):
        print("E. skipped (no client font atlas)")
        return
    adv = {}
    for key, path in (("r", reg), ("b", bold)):
        d = json.load(open(path, encoding="utf8"))
        adv[key] = dict((g["unicode"], g["advance"]) for g in d["glyphs"])

    def width(text, size, is_bold=False, upper=False):
        a = adv["b" if is_bold else "r"]
        t = text.upper() if upper else text
        return sum(a.get(ord(ch), a.get(ord("M"))) for ch in t) * size

    ids = []
    for f in Defs.FAMILIES:
        for r in list(Defs.RARITY)[1:]:
            ids.append(tal(str(f), str(r)))
        for tn in list(Defs.TIER_NAMES)[1:]:
            ids.append(tal(str(f), str(tn)))
    for k in range(len(Defs.BENCH_IDS)):
        for t in range(1, int(Defs.BENCH_MAX[k]) + 1):
            ids.append("Skyy_Accessory_%s_T%d" % (Defs.BENCH_IDS[k], t))
    for k in range(len(Defs.RETIRED)):
        for t in range(1, int(Defs.RETIRED_MAX[k]) + 1):
            ids.append("Skyy_Accessory_%s_T%d" % (Defs.RETIRED[k], t))
    ids.append(str(Defs.OMNI))
    check(all(bool(Defs.isAccessory(i)) for i in ids), "E every enumerated id is an accessory")
    tw = ns["ACC_TEXT_W"]
    names = sorted(((width(str(Defs.pretty(i)), SUI.fs(14), True), str(Defs.pretty(i))) for i in ids), reverse=True)
    subs = sorted(((width(upper(Defs.rarityName(i)), SUI.fs(12)), str(Defs.rarityName(i))) for i in ids), reverse=True)
    check(names[0][0] <= tw, "E longest name %r = %.0f px fits the %d px name column" % (names[0][1], names[0][0], tw))
    check(subs[0][0] <= tw, "E longest rarity word %r = %.0f px fits %d px" % (subs[0][1], subs[0][0], tw))
    body = 2 * ns["ACC_COL_W"] + ns["ACC_COL_GAP"]
    well_in = body - 2 * 8
    head_w = ns["ACC_COL_IN"] - 2
    hint_w = width(ns["ACC_HINT"], 16)
    head = max(width("Accessories and talismans in your inventory", SUI.fs(13), True, True), width("Bag slots", SUI.fs(13), True, True))
    btn = width("Unequip", 14, True, True)
    longest = names[0][1]
    s_all = JArray(JString)(len(Defs.FAMILIES))
    for k, f in enumerate(Defs.FAMILIES):
        s_all[k] = tal(str(f), "Legendary")
    bonus_w = width(str(Defs.bonusText(s_all)), SUI.fs(13))
    results = ["upgraded to " + longest + " - " + longest + " could not be returned - reported to the server log",
               "unequipped " + longest + " - your old " + longest + " came back as the new upgradable talisman",
               why.replace("Vitality", "Regeneration") + " - it was kept in a free bag slot",
               "could not give " + longest + " back - inventory and bag full, reported to the server log",
               "Campfire quick cook - graded cooking is off on this server - plain dishes and no Cooking XP"]
    res_w = max(width(t, 16, True) for t in results)
    check(hint_w <= well_in, "E hint %.0f px fits %d px" % (hint_w, well_in))
    check(bonus_w <= well_in, "E all-five-talismans Bonuses line %.0f px fits %d px" % (bonus_w, well_in))
    check(head <= head_w, "E section heads %.0f px fit %d px" % (head, head_w))
    check(btn <= ns["ACC_ACT_W"] - 2 * SUI.BTN_SMALL_PAD, "E UNEQUIP %.0f px fits the %d px button label" % (btn, ns["ACC_ACT_W"] - 2 * SUI.BTN_SMALL_PAD))
    check(res_w <= 2 * body, "E longest result %.0f px fits the two-line result line (%d px a line)" % (res_w, body))
    print("E. text fit: name %.0f / %d, rarity %.0f / %d, heads %.0f / %d, hint %.0f / %d, bonuses %.0f / %d, UNEQUIP %.0f / %d, "
          "longest result %.0f / %d (one line) - %s" % (names[0][0], tw, subs[0][0], tw, head, head_w, hint_w, well_in, bonus_w, well_in,
                                                       btn, ns["ACC_ACT_W"] - 2 * SUI.BTN_SMALL_PAD, res_w, body,
                                                       "wraps to 2" if res_w > body else "one line"))


# ============================================================================================================== parent
def main():
    if "--child" in sys.argv:
        try:
            run(JAR)
        except SystemExit:
            raise
        except Exception as e:
            import traceback
            traceback.print_exc()
            FAILS.append("crash: %s" % e)
        print("%d ok, %d fail" % (OKS[0], len(FAILS)))
        sys.exit(1 if FAILS else 0)
    scratch_root = os.path.join(TOOLS, "dev", "scratch")
    if not os.path.abspath(SCRATCH).startswith(os.path.abspath(scratch_root) + os.sep):
        raise SystemExit("--dir must be a folder inside tools/dev/scratch/: " + SCRATCH)
    if not os.path.exists(JAR):
        raise SystemExit("no jar " + JAR + " - build it first")
    if os.path.getmtime(JAR) < os.path.getmtime(BUILD):
        raise SystemExit("the jar is older than " + os.path.basename(BUILD) + " - rebuild it first")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"))
    args = [sys.executable, os.path.abspath(__file__), "--child", "--jar", JAR, "--dir", SCRATCH]
    r = subprocess.run(args, env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
