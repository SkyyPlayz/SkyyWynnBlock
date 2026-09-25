"""Bare-JVM check for SkyyClasses 0.1.6 (kept next to the build so the build report's JVM claim can be re-run).

    python SkyyClasses/test_skyyclasses_0.1.6.py [--jar <SkyyClasses-0.1.6.jar>] [--dir <scratch folder>] [--keep]

Build the jar first (python tools/classes_0_1_6_patch.py, then python SkyyClasses/build_skyyclasses_0.1.6.py). A child process starts a
fresh JVM (the game's own JRE, -Xverify:all, HytaleServer.jar + the jar + tools/javassist.jar on the classpath) and checks
(research/Classes-Berserker-Priest-Spec.md 7.1):
  A  every class loads and verifies
  B  defaults of the 0.1.5 keys are identical to 0.1.5; the new keys = the row defaults
  C  a missing file is written with the defaults; a 0.1.5 file keeps working (new keys = code defaults); hand-typed new keys are clamped
  D  the 0.1.5 default file under the config kit (4 categories, 28 rows, no rewrite at start)
  E  get / set per row (old rows as 0.1.5; kits.enabled + priestHeal.enabled part switches, int/dec bounds, items rows)
  F  line-preserving writes (new keys appended under the kit header), the change log, history copies
  G  hand edits + the kit's reload op (new keys clamped by ClassCfg.load); loadInert never touches a bound field
  H  player Settings: notifyOn / regSetting, the ClassRules gates before their throttles
  I  setup() order: load -> KitMigrate.runOnce -> bridge puts (class:fn:kitnew) -> ... 3 systems -> regSetting x4 -> CfgPub.start last
  J  permissions with the engine's own AbstractCommand code: /class kit in hytale:Adventurer, /classadmin (+ kit) in no group
  K  garbage ops never throw
  L  kit parse (bad entries, 9999, the 9-stack cap, texts)
  M  class:fn:kitnew state table (absent -> pending, old/given/off/owed/pending unchanged, kits off -> off, unreadable -> FALSE, bad keys)
  N  the 'picked before kits' migration (class -> old, no class untouched, marker, second start no-op, a failure retries)
  O  setClassKey marks the first class pending in the same write; kit state writes (begin / end / claim / merge) and texts; an
     interrupted give (texts, cleared by a same-class admin re-give)
  P  Priest heal math (share, self %, per-hit cap, overheal clamp, the 1 s budget across two Priests) and the chat aggregator
  Q  checkKit questions (another class's weapon, unowned weapons, free items); "Use my hotbar" second-click confirm (KitHotbarTask)
  T  roster: order, class:list, weapon prefixes, owners (hatchets free), block texts, allowed()
Not testable without the game (listed as UNVERIFIED in the build report): the Inspect-group heal on a real hit, addStatValue on another
player, inventory adds / remainders, the kit tick with real players and SkyyProfiles epochs, popups, the pages on a client.
Nothing is deployed. Default scratch folder: tools/dev/scratch/r6-skyyclasses (git-ignored), deleted at the end unless --keep; TEMP/TMP
and java.io.tmpdir point into it. Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.1.6"
PKG = "com.skyy.classes."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "r6-skyyclasses")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def old_defaults():
    """The 0.1.5 build script's DEF_* values and default file lines (the script is only read, never run)."""
    src = open(os.path.join(HERE, "build_skyyclasses_0.1.5.py"), encoding="utf8").read()
    ns = {}
    for m in re.finditer(r"^(DEF_[A-Z_]+) = (.+)$", src, re.M):
        ns[m.group(1)] = eval(m.group(2), {}, {})
    m = re.search(r"^CFG_LINES = (\[.*?^\])", src, re.M | re.S)
    lines = eval(m.group(1), {}, dict(ns))
    return ns, lines


def props_of(text):
    out = {}
    for l in text.replace("\r\n", "\n").split("\n"):
        s = l.strip()
        if not s or s[0] in "#!" or "=" not in s:
            continue
        k, v = s.split("=", 1)
        out[k.strip()] = v.strip()
    return out


NEW_ROWS = [  # (key, cat, type, default, min, max, opts, unit, flags) - spec 2.5
    ("kits.enabled", "kits", "bool", "true", "", "", "", "", "live,part,danger"),
    ("kit.Archer", "kits", "items", "Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64", "0", "9", "qty", "", "new"),
    ("kit.Archer.fromHotbar", "kits", "action", "", "", "", "Use my hotbar", "", "new,danger"),
    ("kit.Warrior", "kits", "items", "Weapon_Sword_Crude:1", "0", "9", "qty", "", "new"),
    ("kit.Warrior.fromHotbar", "kits", "action", "", "", "", "Use my hotbar", "", "new,danger"),
    ("kit.Mage", "kits", "items", "Weapon_Staff_Wood:1", "0", "9", "qty", "", "new"),
    ("kit.Mage.fromHotbar", "kits", "action", "", "", "", "Use my hotbar", "", "new,danger"),
    ("kit.Berserker", "kits", "items", "Weapon_Battleaxe_Crude:1", "0", "9", "qty", "", "new"),
    ("kit.Berserker.fromHotbar", "kits", "action", "", "", "", "Use my hotbar", "", "new,danger"),
    ("kit.Priest", "kits", "items", "Weapon_Wand_Wood:1", "0", "9", "qty", "", "new"),
    ("kit.Priest.fromHotbar", "kits", "action", "", "", "", "Use my hotbar", "", "new,danger"),
    ("kit.Assassin", "kits", "items", "Weapon_Daggers_Crude:1", "0", "9", "qty", "", "new,adv"),
    ("kit.Assassin.fromHotbar", "kits", "action", "", "", "", "Use my hotbar", "", "new,danger,adv"),
    ("kit.Shaman", "kits", "items", "", "0", "9", "qty", "", "new,adv"),
    ("kit.Shaman.fromHotbar", "kits", "action", "", "", "", "Use my hotbar", "", "new,danger,adv"),
    ("priestHeal.enabled", "priest", "bool", "true", "", "", "", "", "live,part,danger"),
    ("priestHeal.sharePercent", "priest", "int", "25", "0", "500", "", "%", "live"),
    ("priestHeal.selfPercent", "priest", "int", "50", "0", "100", "", "%", "live"),
    ("priestHeal.radius", "priest", "dec", "16", "1", "64", "", "blocks", "live"),
    ("priestHeal.maxPerHit", "priest", "dec", "10", "0.5", "1000", "", "", "live"),
    ("priestHeal.maxPerSecond", "priest", "dec", "10", "0.5", "1000", "", "", "live"),
    ("priestHeal.messages", "priest", "bool", "true", "", "", "", "", "live"),
    ("priestHeal.feedbackMs", "priest", "int", "10000", "1000", "60000", "", "ms", "live,adv"),
]
DEF16 = "switchCost=5000 cooldownMinutes=60 requireClass=false unassignedBlocked=true promptEveryLogin=true openDelayMillis=2000" \
        " kits=on priestHeal=on healShare=25% self=50% radius=16"


# ============================================================================================================== child: the checks
def run(jar):
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JObject, JImplements, JOverride, JFloat, JInt
    import zipfile
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
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

    Cfg, Rows, Pub, Hooks, Rules = (JClass(PKG + "ClassCfg"), JClass(PKG + "CfgRows"), JClass(PKG + "CfgPub"), JClass(PKG + "ClassHooks"),
                                    JClass(PKG + "ClassRules"))
    KitCfg, KitHooks, Store, Defs = JClass(PKG + "KitCfg"), JClass(PKG + "KitHooks"), JClass(PKG + "ClassStore"), JClass(PKG + "ClassDefs")
    UUID, Paths, Integer = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Integer")

    def jarr(*xs):
        a = JArray(JObject)(len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a

    # ---------------- B. defaults: 0.1.5 keys unchanged, new keys = row defaults
    ns, lines15 = old_defaults()
    check(int(Cfg.SWITCH_COST) == ns["DEF_SWITCH_COST"] and int(Cfg.COOLDOWN_MIN) == ns["DEF_COOLDOWN_MIN"]
          and bool(Cfg.REQUIRE_CLASS) == ns["DEF_REQUIRE_CLASS"] and bool(Cfg.UNASSIGNED_BLOCKED) == ns["DEF_UNASSIGNED_BLOCKED"]
          and bool(Cfg.PROMPT_EVERY_LOGIN) == ns["DEF_PROMPT_EVERY_LOGIN"] and int(Cfg.OPEN_DELAY_MS) == ns["DEF_OPEN_DELAY_MS"],
          "field defaults = 0.1.5 DEF_* %s" % (ns,))
    check(not bool(Cfg.ALLOW_SWITCH), "ALLOW_SWITCH is false (design lock)")
    text15 = "".join(l + "\n" for l in lines15)
    text16 = "".join(str(l) + "\n" for l in Cfg.DEFAULT_LINES)
    p15, p16 = props_of(text15), props_of(text16)
    check(all(p16.get(k) == v for k, v in p15.items()), "0.1.5 keys + values unchanged in the default file")
    check(list(p16)[:len(p15)] == list(p15), "0.1.5 keys keep their order (new keys after them)")
    for r in NEW_ROWS:
        if r[2] not in ("action",):
            check(p16.get(r[0]) == r[3], "default file %s = row default %r (got %r)" % (r[0], r[3], p16.get(r[0])))
    check(set(p16) - set(p15) == set(r[0] for r in NEW_ROWS if r[2] != "action"), "the default file adds exactly the new row keys")
    check([str(x) for x in Rows.defLines(0)] == [str(x) for x in Cfg.DEFAULT_LINES], "kit DEFAULTS text = ClassCfg.DEFAULT_LINES")
    check(bool(KitCfg.ON) and int(Cfg.HEAL_SHARE_PCT) == 25 and int(Cfg.HEAL_SELF_PCT) == 50 and float(Cfg.HEAL_RADIUS) == 16.0
          and float(Cfg.HEAL_MAX_HIT) == 10.0 and float(Cfg.HEAL_MAX_SEC) == 10.0 and bool(Cfg.HEAL_ON) and bool(Cfg.HEAL_MSG)
          and int(Cfg.HEAL_MSG_MS) == 10000, "new field defaults (spec 2.5)")
    print("B. defaults done")

    work = os.path.join(SCRATCH, "work")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)

    # ---------------- C. missing file / a 0.1.5 file / hand-typed new keys
    fresh = os.path.join(work, "fresh", "Skyy_SkyyClasses", "config.properties")
    Cfg.FILE = Paths.get(fresh)
    r = str(Cfg.load())
    check(os.path.isfile(fresh) and open(fresh, encoding="utf8").read() == text16, "missing file written with DEFAULT_LINES")
    check(r == str(Cfg.summary()) and r == DEF16, "load() text = summary() = the defaults: %s" % r)
    custom = os.path.join(work, "custom", "Skyy_SkyyClasses", "config.properties")
    os.makedirs(os.path.dirname(custom))
    open(custom, "w", newline="\n").write("switchCost=-5\ncooldownMinutes=abc\nrequireClass=yes\nunassignedBlocked=off\npromptEveryLogin=0\n"
                                          "openDelayMillis=100\nallowSwitch=true\nclassSwitching=true\n")
    Cfg.FILE = Paths.get(custom)
    Cfg.load()
    check(int(Cfg.SWITCH_COST) == 0 and int(Cfg.COOLDOWN_MIN) == 60 and bool(Cfg.REQUIRE_CLASS) and not bool(Cfg.UNASSIGNED_BLOCKED)
          and not bool(Cfg.PROMPT_EVERY_LOGIN) and int(Cfg.OPEN_DELAY_MS) == 250, "0.1.5 clamps and words: %s" % Cfg.summary())
    check(bool(KitCfg.ON) and int(Cfg.HEAL_SHARE_PCT) == 25 and str(KitCfg.K_PRIEST) == "Weapon_Wand_Wood:1" and str(KitCfg.K_SHAMAN) == "",
          "a file without the new keys = code defaults")
    check(not bool(Cfg.ALLOW_SWITCH) and str(Hooks.customGet("classSwitching")) == "false", "allowSwitch / classSwitching lines never turn switching on")
    r = Hooks.customSet("classSwitching", "true")
    check(str(r[0]) == "bad" and r[1] is None and "design lock" in str(r[2]), "ClassHooks.customSet always refuses")
    typed = os.path.join(work, "typed", "Skyy_SkyyClasses", "config.properties")
    os.makedirs(os.path.dirname(typed))
    open(typed, "w", newline="\n").write("kits.enabled=off\nkit.Archer=  Weapon_Sword_Crude:2  \npriestHeal.enabled=no\npriestHeal.sharePercent=900\n"
                                         "priestHeal.selfPercent=-5\npriestHeal.radius=0.2\npriestHeal.maxPerHit=5000\npriestHeal.maxPerSecond=abc\n"
                                         "priestHeal.messages=0\npriestHeal.feedbackMs=10\n")
    Cfg.FILE = Paths.get(typed)
    Cfg.load()
    check(not bool(KitCfg.ON) and str(KitCfg.K_ARCHER) == "Weapon_Sword_Crude:2" and not bool(Cfg.HEAL_ON) and int(Cfg.HEAL_SHARE_PCT) == 500
          and int(Cfg.HEAL_SELF_PCT) == 0 and float(Cfg.HEAL_RADIUS) == 1.0 and float(Cfg.HEAL_MAX_HIT) == 1000.0
          and float(Cfg.HEAL_MAX_SEC) == 10.0 and not bool(Cfg.HEAL_MSG) and int(Cfg.HEAL_MSG_MS) == 1000,
          "hand-typed new keys: words, trims and the row bounds as clamps (%s)" % Cfg.summary())
    Cfg.FILE = Paths.get(fresh)
    Cfg.load()
    check(str(Cfg.summary()) == DEF16, "back to the defaults")
    print("C. load paths done")

    # ---------------- D. the 0.1.5 default file under the kit
    mods = os.path.join(work, "mods")
    home = os.path.join(mods, "Skyy_SkyyClasses")
    os.makedirs(home)
    cfgp = os.path.join(home, "config.properties")
    open(cfgp, "w", newline="\n").write(text15)          # exactly what 0.1.5 wrote when the file was missing
    Cfg.FILE = Paths.get(cfgp)
    Cfg.load()
    check(str(Cfg.summary()) == DEF16, "0.1.5 file read back to the defaults")
    Pub.start(Paths.get(mods), None)
    bridge = Cfg.bridge()
    fn = bridge.get("config:fn:SkyyClasses")
    hdr = bridge.get("config:def:SkyyClasses")
    check(fn is not None and hdr is not None, "config:fn + config:def published")
    check(str(bridge.get("config:epoch:SkyyClasses")) == "0", "epoch starts at 0")
    check(len(hdr) == 10 and str(hdr[0]) == "1" and str(hdr[1]) == "SkyyClasses" and str(hdr[2]) == "Classes" and str(hdr[3]) == VERSION
          and str(hdr[4]) == "skyyclasses.admin", "header 0-4 %s" % ([str(hdr[i]) for i in range(5)],))
    check([str(x) for x in hdr[5]] == ["lock", "picker", "kits", "priest"]
          and [str(x) for x in hdr[6]] == ["Weapon lock", "Class picker", "Class kits", "Priest heal"], "categories")
    check(str(hdr[8]) == "Skyy_SkyyClasses/config.properties" and 0 < len(str(hdr[9])) <= 100 and "kit" in str(hdr[9]), "files + note")
    rows = [[str(x) for x in row] for row in hdr[7]]
    want = [("requireClass", "lock", "bool", "false", "", "", "", "", "live,danger"),
            ("unassignedBlocked", "lock", "bool", "true", "", "", "", "", "live"),
            ("promptEveryLogin", "picker", "bool", "true", "", "", "", "", "live"),
            ("openDelayMillis", "picker", "int", "2000", "250", "60000", "step=250", "ms", "live,adv"),
            ("classSwitching", "picker", "bool", "false", "", "", "", "", "ro")] + NEW_ROWS
    check(len(rows) == 28 and all(len(x) == 11 for x in rows), "28 rows of 11 (%d)" % len(rows))
    for got, w in zip(rows, want):
        check((got[0], got[2], got[3], got[4], got[5], got[6], got[7], got[8], got[9]) == w, "row %s = %s (got %s)" % (w[0], w, got))
    check(all(len(x[10]) <= 100 and len(x[1]) <= 40 for x in rows), "labels <= 40, help <= 100")
    check(not any(x[0] in ("switchCost", "cooldownMinutes") for x in rows), "switchCost / cooldownMinutes are not rows")
    Pub.flush()
    time.sleep(0.3)
    Pub.flush()
    check(open(cfgp, "rb").read().decode("latin-1") == text15, "the kit does not rewrite the 0.1.5 file at start")
    print("D. kit header done")

    def op(*args):
        return fn.apply(jarr(*args))

    def R(r):
        return (str(r[0]), None if r[1] is None else str(r[1]), str(r[2])) if r is not None else None

    def get(k):
        v = op("get", k)
        return None if v is None else str(v)

    def cset(k, v, confirm="yes"):   # the server console (no permission provider in a bare JVM)
        return R(op("set", k, v, None, None, confirm, "console"))

    def settle():
        Pub.flush()
        time.sleep(0.4)
        Pub.flush()

    def logs():
        return [str(x) for x in op("log", Integer.valueOf(200))]

    # ---------------- E. get / set
    check((get("requireClass"), get("unassignedBlocked"), get("promptEveryLogin"), get("openDelayMillis"), get("classSwitching"))
          == ("false", "true", "true", "2000", "false"), "initial gets")
    check((get("kits.enabled"), get("kit.Priest"), get("kit.Shaman"), get("priestHeal.sharePercent"), get("priestHeal.radius"),
           get("priestHeal.maxPerHit"), get("priestHeal.feedbackMs"), get("kit.Priest.fromHotbar"))
          == ("true", "Weapon_Wand_Wood:1", "", "25", "16", "10", "10000", ""), "initial gets of the new rows (a 0.1.5 file = defaults)")
    check(get("switchCost") is None and get("nope") is None, "non-row keys are unknown to get")
    r = cset("requireClass", "true", confirm="")
    check(r[0] == "confirm" and not bool(Cfg.REQUIRE_CLASS), "requireClass ON asks first, nothing changed: %s" % (r,))
    r = cset("requireClass", "true")
    check(r[0] == "ok" and r[1] == "true" and bool(Cfg.REQUIRE_CLASS), "requireClass ON with yes: %s" % (r,))
    r = cset("requireClass", "false", confirm="")
    check(r[0] == "confirm" and bool(Cfg.REQUIRE_CLASS), "requireClass OFF asks too (danger, both ways): %s" % (r,))
    r = cset("requireClass", "off")
    check(r[0] == "ok" and r[1] == "false" and not bool(Cfg.REQUIRE_CLASS), "requireClass OFF with yes (typed 'off'): %s" % (r,))
    r = cset("unassignedBlocked", "false", confirm="")
    check(r[0] == "ok" and not bool(Cfg.UNASSIGNED_BLOCKED), "unassignedBlocked asks nothing: %s" % (r,))
    r = cset("promptEveryLogin", "false", confirm="")
    check(r[0] == "ok" and not bool(Cfg.PROMPT_EVERY_LOGIN), "promptEveryLogin: %s" % (r,))
    check(cset("openDelayMillis", "100")[0] == "bad" and cset("openDelayMillis", "60250")[0] == "bad" and int(Cfg.OPEN_DELAY_MS) == 2000,
          "openDelayMillis outside 250-60000 refused (typed values are never clamped)")
    r = cset("openDelayMillis", "3000", confirm="")
    check(r[0] == "ok" and r[1] == "3000" and int(Cfg.OPEN_DELAY_MS) == 3000, "openDelayMillis live: %s" % (r,))
    r = cset("classSwitching", "true")
    check(r[0] == "bad" and not bool(Cfg.ALLOW_SWITCH) and get("classSwitching") == "false", "read-only row refused: %s" % (r,))
    check(cset("switchCost", "1")[0] == "unknown", "switchCost cannot be set through the kit")
    # new rows: part switches ask only when switched OFF
    r = cset("kits.enabled", "false", confirm="")
    check(r[0] == "confirm" and bool(KitCfg.ON), "kits.enabled OFF asks first (part switch): %s" % (r,))
    r = cset("kits.enabled", "false")
    check(r[0] == "ok" and not bool(KitCfg.ON), "kits.enabled OFF with yes: %s" % (r,))
    r = cset("kits.enabled", "true", confirm="")
    check(r[0] == "ok" and bool(KitCfg.ON), "kits.enabled ON asks nothing: %s" % (r,))
    check(cset("priestHeal.enabled", "false", confirm="")[0] == "confirm" and bool(Cfg.HEAL_ON), "priestHeal.enabled OFF asks first")
    check(cset("priestHeal.sharePercent", "600")[0] == "bad" and int(Cfg.HEAL_SHARE_PCT) == 25, "sharePercent above 500 refused")
    r = cset("priestHeal.sharePercent", "50%", confirm="")
    check(r[0] == "ok" and r[1] == "50" and int(Cfg.HEAL_SHARE_PCT) == 50, "sharePercent live (typed 50%%): %s" % (r,))
    check(cset("priestHeal.radius", "0.5")[0] == "bad" and cset("priestHeal.radius", "65")[0] == "bad", "radius outside 1-64 refused")
    r = cset("priestHeal.radius", "20.50", confirm="")
    check(r[0] == "ok" and r[1] == "20.5" and float(Cfg.HEAL_RADIUS) == 20.5, "radius dec live: %s" % (r,))
    check(cset("priestHeal.feedbackMs", "500")[0] == "bad", "feedbackMs below 1000 refused")
    r = cset("priestHeal.feedbackMs", "2000", confirm="")
    check(r[0] == "ok" and int(Cfg.HEAL_MSG_MS) == 2000, "feedbackMs live (ms field, no scale): %s" % (r,))
    r = cset("kit.Priest", "Weapon_Wand_Wood:1,Weapon_Wand_Wood:2")
    check(r[0] == "bad", "a kit listing an item twice is refused: %s" % (r,))
    r = cset("kit.Priest", "Weapon_Wand_Wood:1,A:1,B:1,C:1,D:1,E:1,F:1,G:1,H:1,I:1")
    check(r[0] == "bad" and str(KitCfg.K_PRIEST) == "Weapon_Wand_Wood:1", "more than 9 stacks refused: %s" % (r,))
    r = cset("kit.Priest", "Weapon_Wand_Wood:1,Weapon_Spellbook_Frost:1")
    check(r[0] == "bad" and "Unknown item" in r[2], "bare JVM has no item map: typed kits are refused as unknown items (in game they "
          "validate against Item.getAssetMap): %s" % (r,))
    A = UUID.fromString("00000000-0000-0000-0000-0000000000aa")
    check(R(op("set", "unassignedBlocked", "true", A, "Someone", "yes", "menu"))[0] == "denied" and not bool(Cfg.UNASSIGNED_BLOCKED),
          "a player without skyyclasses.admin is denied")
    check(R(op("set", "unassignedBlocked", "true", None, "Ghost", "yes", "command"))[0] == "denied", "null who via command is denied")
    r = R(op("action", "kit.Archer.fromHotbar", None, "Console", "yes", "console"))
    check(r is not None and r[0] == "bad" and "in game" in r[2], "Use my hotbar from the console: refused (needs an admin in game): %s" % (r,))
    check(int(str(bridge.get("config:epoch:SkyyClasses"))) == 10, "epoch counts the 10 applied changes (%s)" % bridge.get("config:epoch:SkyyClasses"))
    print("E. get/set done")

    # ---------------- F. files
    settle()
    t = open(cfgp, "rb").read().decode("latin-1")
    exp = (text15.replace("unassignedBlocked=true", "unassignedBlocked=false").replace("promptEveryLogin=true", "promptEveryLogin=false")
           .replace("openDelayMillis=2000", "openDelayMillis=3000"))
    check(t.startswith(exp), "0.1.5 lines: only the changed ones changed (comments, order kept):\n%s" % t)
    tail = [l for l in t[len(exp):].split("\n") if l]
    check(tail[:1] == ["# ---- changed in game (SkyWynn Menu) ----"] and set(tail[1:]) == {"kits.enabled=true", "priestHeal.sharePercent=50",
          "priestHeal.radius=20.5", "priestHeal.feedbackMs=2000"}, "new keys appended once under the kit header: %s" % tail)
    lg = logs()
    check(any(l.split("\t")[1:] == ["console", "-", "console", "requireClass", "true", "false", "ok"] for l in lg)
          and any(l.split("\t")[1:] == ["console", "-", "console", "priestHeal.radius", "16", "20.5", "ok"] for l in lg),
          "changes logged (console) %s" % lg[:6])
    check(os.path.isfile(os.path.join(home, "config-changes.log")), "config-changes.log written")
    v = op("versions")
    check(v is not None and len(v) >= 1 and os.path.isdir(os.path.join(home, "config-history")), "history copy made")
    print("F. files done")

    # ---------------- G. hand edits: loadInert, the kit's reload op
    open(cfgp, "w", newline="\n").write(t.replace("switchCost=5000", "switchCost=777").replace("cooldownMinutes=60", "cooldownMinutes=-3")
                                        .replace("requireClass=false", "requireClass=true").replace("openDelayMillis=3000", "openDelayMillis=100"))
    Cfg.loadInert()
    check(int(Cfg.SWITCH_COST) == 777 and int(Cfg.COOLDOWN_MIN) == 0, "loadInert re-reads switchCost / cooldownMinutes with the clamps")
    check(not bool(Cfg.REQUIRE_CLASS) and int(Cfg.OPEN_DELAY_MS) == 3000 and int(Cfg.HEAL_SHARE_PCT) == 50, "loadInert never touches a bound field")
    r = R(op("reload", None, None, "console"))
    check(r is not None and r[0] == "ok" and r[1] == "2" and "2 values changed by hand" in r[2], "reload op counts the 2 row edits: %s" % (r,))
    settle()
    check(bool(Cfg.REQUIRE_CLASS) and int(Cfg.OPEN_DELAY_MS) == 250, "ClassCfg.load applied them with its clamp: %s" % Cfg.summary())
    check(int(Cfg.HEAL_SHARE_PCT) == 50 and float(Cfg.HEAL_RADIUS) == 20.5 and int(Cfg.HEAL_MSG_MS) == 2000,
          "the kit's RELOAD (ClassCfg.load) keeps the in-game values of the new rows")
    t2 = open(cfgp, "rb").read().decode("latin-1")
    open(cfgp, "w", newline="\n").write(t2 + "priestHeal.selfPercent=150\nkits.enabled=off\n")
    r = R(op("reload", None, None, "console"))
    settle()
    check(r[0] == "ok" and r[1] == "2" and int(Cfg.HEAL_SELF_PCT) == 100 and not bool(KitCfg.ON) and get("priestHeal.selfPercent") == "100",
          "hand-typed new keys: reload applies them, ClassCfg.load clamps selfPercent to 100: %s %s" % (r, Cfg.summary()))
    lg = logs()
    check(any(l.split("\t")[3:7] == ["file", "priestHeal.selfPercent", "50", "150"] for l in lg), "new-key hand edit logged via=file %s" % lg[:4])
    check(cset("kits.enabled", "on", confirm="")[0] == "ok" and bool(KitCfg.ON), "kits back ON")
    r = cset("requireClass", "false")
    check(r[0] == "ok" and not bool(Cfg.REQUIRE_CLASS), "back to OFF")
    settle()
    s = [str(x) for x in op("status")]
    check(s[0] == "ok", "status ok %s" % s)
    print("G. hand edits done")

    # ---------------- H. player Settings
    U = UUID.fromString("00000000-0000-0000-0000-0000000000bb")
    check(bool(Cfg.notifyOn(U, "classes.blockedChat")) and bool(Cfg.notifyOn(None, "classes.blockedChat")), "no SkyyMenu = ON")

    @JImplements("java.util.function.Function")
    class FakeGet(object):
        def __init__(self):
            self.off, self.mode = set(), "bool"

        @JOverride
        def apply(self, o):
            if self.mode == "throw":
                raise RuntimeError("boom")
            if self.mode == "null":
                return None
            return JClass("java.lang.Boolean").valueOf(str(o[1]) not in self.off)

    @JImplements("java.util.function.Function")
    class FakeReg(object):
        def __init__(self):
            self.got = []

        @JOverride
        def apply(self, o):
            self.got.append([str(x) for x in o])
            return None

    fg, fr = FakeGet(), FakeReg()
    bridge.put("settings:fn:get", fg)
    bridge.put("settings:fn:register", fr)
    Cfg.regSetting("classes.healGiven", "Priest heals - your heals", "combat", True, "help")
    d = bridge.get("settings:def:classes.healGiven")
    want_d = ["SkyyClasses", "classes.healGiven", "Priest heals - your heals", "combat", "true", "help"]
    got_d = None if d is None else [str(x).lower() if i == 4 else str(x) for i, x in enumerate(d)]
    check(got_d == want_d and len(fr.got) == 1, "regSetting writes settings:def and calls settings:fn:register: %s" % (got_d,))
    fg.off.add("classes.blockedChat")
    check(not bool(Cfg.notifyOn(U, "classes.blockedChat")) and bool(Cfg.notifyOn(U, "classes.blockedPopup")), "chat OFF, popup still ON")
    fg.mode = "throw"
    check(bool(Cfg.notifyOn(U, "classes.blockedChat")), "a throwing Settings function = ON")
    fg.mode = "bool"
    Rules.WARNED.remove(U)
    Rules.POPPED.remove(U)
    try:
        Rules.tell(None, U, "x")
    except Exception as ex:
        print("tell with chat OFF threw", ex)
    check(not Rules.WARNED.containsKey(U), "tell gate sits before the 3 s throttle")
    fg.off.add("classes.blockedPopup")
    Rules.popup(None, U, "Weapon_Sword_Iron", "x")
    check(not Rules.POPPED.containsKey(U), "popup gate sits before the 1.5 s throttle")
    fg.off.clear()
    # heal lines: the admin switch and the player's switch are checked before the line's timestamp (a hidden line stamps nothing)
    Msg = JClass(PKG + "HealMsg")
    P1 = UUID.fromString("00000000-0000-0000-0000-00000000c001")
    Msg.forget(P1)
    Msg.given(P1, P1, 6.0)
    Cfg.HEAL_MSG = False
    Msg.flushDue()
    check(not Msg.GIVEN.containsKey(P1) and not Msg.LASTG.containsKey(P1), "priestHeal.messages OFF: the line is dropped, no timestamp used")
    Cfg.HEAL_MSG = True
    Msg.given(P1, P1, 6.0)
    fg.off.add("classes.healGiven")
    Msg.flushDue()
    check(not Msg.GIVEN.containsKey(P1) and not Msg.LASTG.containsKey(P1), "classes.healGiven OFF: dropped, no timestamp used")
    fg.off.clear()
    bridge.remove("settings:fn:get")
    bridge.remove("settings:fn:register")
    bridge.remove("settings:def:classes.healGiven")
    print("H. settings done")

    # ---------------- I. bytecode order in setup() / shutdown()
    Pool, IP, PS, BOS = (JClass("javassist.ClassPool"), JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"),
                         JClass("java.io.ByteArrayOutputStream"))
    pool = Pool(False)
    pool.appendClassPath(jar)
    pool.appendSystemPath()

    def code(cls, meth):
        cc = pool.get(PKG + cls)
        mm = cc.getDeclaredConstructors()[0] if meth == "<init>" else cc.getDeclaredMethod(meth)
        bos = BOS()
        IP(PS(bos)).print_(mm)
        return str(bos.toString()).splitlines()

    su = code("SkyyClassesPlugin", "setup")

    def idx(pat, lines=su):
        return [i for i, l in enumerate(lines) if pat in l]

    ld, st, rg, mig = idx("ClassCfg.load("), idx("CfgPub.start("), idx("ClassCfg.regSetting("), idx("KitMigrate.runOnce(")
    puts = idx("Map.put(")
    reg = idx("registerCommand(") + idx("registerGlobal(") + idx("registerSystem(") + idx("scheduleAtFixedRate(")
    check(len(ld) == 1 and len(st) == 1 and len(rg) == 4 and len(mig) == 1, "setup: one load, one migration, one CfgPub.start, four regSetting")
    check(ld and mig and puts and ld[0] < mig[0] < min(puts), "setup order: ClassCfg.load -> KitMigrate.runOnce -> the bridge puts")
    check(st and rg and ld[0] < min(rg) and max(rg) < st[0] and max(reg) < st[0], "setup order: registrations -> regSetting x4 -> CfgPub.start")
    check(len(idx("registerSystem(")) == 3 and idx("PriestHealSys.<init>"), "three systems (ShotTrack, DamageLock, PriestHealSys), one each")
    txt = "\n".join(su)
    for s_ in ('"class:fn:kitnew"', '"classes.healGiven"', '"classes.healTaken"', '"Priest heals - your heals"', '"Priest heals - healed by others"'):
        check(s_ in txt, "setup has %s" % s_)
    after = [l for l in su[st[0] + 1:] if "invoke" in l]
    check(not any(("register" in l) or ("CfgPub" in l) or ("regSetting" in l) for l in after), "nothing is registered after CfgPub.start")
    sd = code("SkyyClassesPlugin", "shutdown")
    ps, ss = idx("CfgPub.shutdown(", sd), idx("JavaPlugin.shutdown(", sd)
    check(len(ps) == 1 and len(ss) == 1 and ps[0] < ss[0], "shutdown flushes the kit before super.shutdown()")
    gr = code("PriestHealSys", "getGroup")
    check(idx("getInspectDamageGroup(", gr) and not idx("getFilterDamageGroup(", gr), "PriestHealSys runs in the Inspect group (after ApplyDamage)")
    tk = code("ClassTick", "run")
    a1, a2, a3 = idx("Kit.tick(", tk), idx("HealMsg.flushDue(", tk), idx("ClassCfg.profilesOn(", tk)
    check(a1 and a2 and a3 and a1[0] < a2[0] < a3[0], "ClassTick: kit tick + heal lines run before the SkyyProfiles-only epoch check")
    print("I. bytecode order done")

    # ---------------- J. permissions: the engine's own AbstractCommand code
    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyClasses"

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
    class Sender(object):
        def __init__(self, nodes):
            self.nodes = nodes

        def _has(self, q):
            n = str(q) if isinstance(q, str) else str(q.getId())
            return "*" in self.nodes or n in self.nodes

        @JOverride
        def hasPermission(self, *a):
            return self._has(a[0])

        @JOverride
        def getUsername(self):
            return "tester"

        @JOverride
        def getUuid(self):
            return U

        @JOverride
        def sendMessage(self, m):
            pass

    try:
        uf = JClass("java.lang.Class").forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
        uf.setAccessible(True)
        own = uf.get(None).allocateInstance(JClass("com.hypixel.hytale.server.core.command.system.CommandManager").class_)
    except Exception as ex:
        print("no CommandManager owner (%s) - using a plain CommandOwner" % ex)
        own = Owner()
    adm, pc = JClass(PKG + "ClassAdminCmd")(), JClass(PKG + "ClassCmd")()
    def submap(c):
        mm_ = c.getSubCommands()
        return dict((str(k), mm_.get(k)) for k in mm_.keySet())

    subs, psubs = submap(adm), submap(pc)
    for c_ in [adm, pc] + list(subs.values()) + list(psubs.values()):
        c_.setOwner(own)
    check(str(adm.getPermission()) == "skyyclasses.admin" and adm.getPermissionGroups() is None, "/classadmin: requirePermission, no groups")
    check(sorted(subs) == ["info", "kit", "reload", "reset", "set"], "/classadmin sub-commands %s" % sorted(subs))
    ak = subs.get("kit")
    check(ak is not None and str(ak.getPermission()) == "skyyclasses.admin" and ak.getPermissionGroups() is not None
          and len(ak.getPermissionGroups()) == 0, "/classadmin kit: requirePermission skyyclasses.admin + cleared groups")
    # "/classadmin kit <player> <class>": optional args are not positional, so it is a usage variant picked by its 2 required args
    try:
        vf = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand").class_.getDeclaredField("variantCommands")
        vf.setAccessible(True)
        vm = vf.get(ak)
        v2 = vm.get(JInt(2)) if vm is not None else None           # fastutil Int2ObjectMap: the int overload
        if v2 is not None:
            v2.setOwner(own)
        check(v2 is not None and str(v2.getPermission()) == "skyyclasses.admin" and v2.getPermissionGroups() is not None
              and len(v2.getPermissionGroups()) == 0 and str(v2.getClass().getSimpleName()) == "AdminKitClassCmd",
              "/classadmin kit <player> <class> = the usage variant AdminKitClassCmd (2 required args, admin node, no groups): %s" % vm)
    except Exception as ex:
        check(False, "could not read the kit usage variant: %s" % ex)
    check(all(subs[n].getPermissionGroups() is None and subs[n].getPermission() is not None for n in ("set", "reset", "info", "reload")),
          "set / reset / info / reload: auto nodes, no groups (as 0.1.5)")
    m = adm.getPermissionGroupsRecursive()
    check(m.size() == 0, "/classadmin and its sub-commands put their nodes into NO permission group: %s" % m)
    check(sorted(psubs) == ["kit"], "/class has the kit sub-command")
    mp = pc.getPermissionGroupsRecursive()
    allnodes = [str(x) for k in mp.keySet() for x in mp.get(k)]
    kitnode = str(psubs["kit"].getPermission())
    check(list(str(k) for k in mp.keySet()) == ["hytale:Adventurer"] and not any("admin" in n for n in allnodes) and kitnode in allnodes,
          "/class + /class kit give hytale:Adventurer only player nodes: %s" % mp)
    everyone = Sender(set(allnodes))
    check(bool(pc.hasPermission(everyone)) and bool(psubs["kit"].hasPermission(everyone)) and not bool(adm.hasPermission(everyone))
          and not bool(ak.hasPermission(everyone)), "an Adventurer may run /class and /class kit, not /classadmin (kit)")
    check(all(bool(x.hasPermission(Sender({"*"}))) for x in [adm] + list(subs.values())), "an op ('*') may run /classadmin and every sub-command")
    print("J. permissions done (hytale:Adventurer gets: %s)" % ", ".join(sorted(allnodes)))

    # ---------------- K. garbage never throws
    thrown = 0
    for g in [None, [], ["nope"], ["set"], ["get"], ["get", 7], ["set", "requireClass", 5, None, None, "yes", "console"],
              ["set", "requireClass", "true", "notauuid", "n", "yes", "menu"], ["reload"], ["reload", "x", "n"], ["log", "abc"], ["status", 1],
              ["action", "kit.Priest.fromHotbar"], ["action", 5, 6]]:
        try:
            fn.apply(None if g is None else jarr(*g))
        except Exception as ex:
            thrown += 1
            print("threw", g, ex)
    check(thrown == 0, "garbage ops never throw")
    check(not bool(Cfg.REQUIRE_CLASS), "garbage changed nothing")
    Pub.shutdown()
    print("K. garbage done")

    # ---------------- L. kit parse
    def parse(text, mx=9):
        o = KitCfg.parse(text, None, mx)
        return [str(x) for x in o[0]], [int(x) for x in o[1]]

    ids, qs = parse("Weapon_Sword_Crude:1, bad entry:x, :5, Weapon_Arrow_Crude:10000, Food_Bread:9999,Rock,Weapon_Axe_Iron:0,,x:y")
    check(ids == ["Weapon_Sword_Crude", "Food_Bread", "Rock"] and qs == [1, 9999, 1], "bad entries skipped, 9999 kept, no amount = 1: %s %s" % (ids, qs))
    ids, qs = parse(",".join("I%d:1" % i for i in range(12)))
    check(len(ids) == 9 and ids[-1] == "I8", "at most 9 stacks (the rest skipped)")
    check(parse("") == ([], []) and parse(None) == ([], []), "empty kit")
    check([str(KitCfg.textOf(i)) for i in range(7)] == ["Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64", "Weapon_Sword_Crude:1", "Weapon_Staff_Wood:1",
                                                         "Weapon_Battleaxe_Crude:1", "Weapon_Wand_Wood:1", "Weapon_Daggers_Crude:1", ""]
          and str(KitCfg.textOf(9)) == "", "textOf per class index = the kit fields")
    SA, IA = JArray(JClass("java.lang.String")), JArray(JInt)
    kids, kq = SA(["Weapon_Shortbow_Crude", "Weapon_Arrow_Crude"]), IA([1, 64])
    check(str(KitCfg.listText(kids, kq)) == "Shortbow Crude x1, Arrow Crude x64" and str(KitCfg.join(kids, kq)) == "Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64"
          and str(KitCfg.rest(kids, kq, IA([1, 50]))) == "Weapon_Arrow_Crude:14" and int(KitCfg.total(kq)) == 65
          and str(KitCfg.name("Tool_Hatchet_Iron")) == "Tool Hatchet Iron" and str(KitCfg.namesText(kids, IA([0, 3]))) == "Arrow Crude",
          "kit texts (names without Weapon_, remainder, totals)")
    check(not bool(KitCfg.known("Weapon_Sword_Crude")), "bare JVM: no item map (known() is false; in game it asks Item.getAssetMap)")
    print("L. kit parse done")

    # ---------------- M. class:fn:kitnew state table
    Kit = JClass(PKG + "Kit")
    kn = bridge.get("class:fn:kitnew")
    check(kn is None, "class:fn:kitnew is put in setup() (not by static init)")
    kn = JClass(PKG + "KitNewFn")()
    pdir = os.path.join(work, "m", "Skyy_SkyyClasses", "players")
    os.makedirs(pdir)
    Store.DIR = Paths.get(pdir)

    def fileprops(k, d=pdir):
        f = os.path.join(d, k + ".properties")
        import skyycfg                         # java.util.Properties escapes (store() writes "\:")
        return skyycfg.parse_props(open(f, encoding="latin-1").read()) if os.path.isfile(f) else None

    def call(u, k, c):
        rr = kn.apply(jarr(u, k, c))
        return None if rr is None else str(rr).lower()       # JPype hands java.lang.Boolean back as a Python bool

    u1 = UUID.fromString("00000000-0000-0000-0000-00000000d001")
    k1 = str(u1)
    r = call(u1, k1, "Priest")
    fp = fileprops(k1)
    check(str(r) == "true" and fp is not None and fp.get("kit") == "pending" and fp.get("kitClass") == "Priest" and "kitAt" in fp
          and str(Store.KITQ.get(k1)) == "pending", "absent -> pending (+ kitClass, kitAt, KITQ): %s %s" % (r, fp))
    at = fp.get("kitAt")
    r = call(u1, k1, "Archer")
    check(str(r) == "true" and fileprops(k1).get("kit") == "pending" and fileprops(k1).get("kitAt") == at and fileprops(k1).get("kitClass") == "Priest",
          "a second call changes nothing (still TRUE)")
    for n_, stt in enumerate(("old", "given", "off", "owed")):
        uu = UUID.fromString("00000000-0000-0000-0000-00000000d1%02d" % n_)
        kk = str(uu) + "-p2"
        open(os.path.join(pdir, kk + ".properties"), "w").write("class=Warrior\nkit=%s\n" % stt)
        r = call(uu, kk, "Warrior")
        check(str(r) == "true" and fileprops(kk).get("kit") == stt and fileprops(kk).get("class") == "Warrior", "%s stays %s (TRUE)" % (stt, stt))
    KitCfg.ON = False
    u2 = UUID.fromString("00000000-0000-0000-0000-00000000d002")
    r = call(u2, str(u2) + "-p3", "Berserker")
    check(str(r) == "true" and fileprops(str(u2) + "-p3").get("kit") == "off" and not Store.KITQ.containsKey(str(u2) + "-p3"),
          "kits off -> off (never automatic), not queued")
    KitCfg.ON = True
    u3 = UUID.fromString("00000000-0000-0000-0000-00000000d003")
    os.makedirs(os.path.join(pdir, str(u3) + ".properties"))          # a folder with the file's name: unreadable
    check(str(call(u3, str(u3), "Mage")) == "false", "an unreadable class file -> FALSE (nothing written)")
    check(str(call(u1, str(u2), "Mage")) == "false" and str(call(u1, k1 + "-px", "Mage")) == "false" and str(call(u1, "../" + k1, "Mage")) == "false"
          and str(call(u1, k1 + "-p12345", "Mage")) == "false", "a key that is not this player's profile key -> FALSE")
    thrown = 0
    for g in [None, [], [u1], [u1, k1], ["x", k1, "Mage"], [u1, 5, "Mage"], [None, None, None]]:
        try:
            rr = kn.apply(None if g is None else jarr(*g))
            if str(rr).lower() != "false":
                thrown += 1
                print("garbage kitnew answered", rr, g)
        except Exception as ex:
            thrown += 1
            print("kitnew threw", g, ex)
    check(thrown == 0, "kitnew garbage -> FALSE, never throws")
    u4 = UUID.fromString("00000000-0000-0000-0000-00000000d004")
    check(str(call(u4, str(u4) + "-p2", "Druid")) == "true" and fileprops(str(u4) + "-p2").get("kitClass") == "Druid",
          "an unknown class name is still recorded (delivery uses the profile's class)")
    print("M. kitnew done")

    # ---------------- N. migration
    Mig = JClass(PKG + "KitMigrate")
    mdir = os.path.join(work, "n", "Skyy_SkyyClasses", "players")
    os.makedirs(mdir)
    open(os.path.join(mdir, "a.properties"), "w").write("class=Archer\nplayed=Archer\n")
    open(os.path.join(mdir, "b.properties"), "w").write("played=Archer\n")
    open(os.path.join(mdir, "c.properties"), "w").write("class=Warrior\nkit=given\n")
    open(os.path.join(mdir, "d.properties"), "w").write("class=  \n")
    Store.DIR = Paths.get(mdir)
    Mig.runOnce()
    marker = os.path.join(os.path.dirname(mdir), "kits.properties")
    mk = props_of(open(marker, encoding="latin-1").read()) if os.path.isfile(marker) else {}
    check(fileprops("a", mdir).get("kit") == "old" and fileprops("a", mdir).get("played") == "Archer" and "kit" not in fileprops("b", mdir)
          and fileprops("c", mdir).get("kit") == "given" and "kit" not in fileprops("d", mdir), "files with a class -> old, others untouched")
    check(mk.get("marked") == "1" and mk.get("files") == "4" and mk.get("version") == VERSION, "kits.properties written: %s" % mk)
    open(os.path.join(mdir, "e.properties"), "w").write("class=Mage\n")
    Mig.runOnce()
    check("kit" not in fileprops("e", mdir), "second start: no-op (the marker exists)")
    mdir2 = os.path.join(work, "n2", "Skyy_SkyyClasses", "players")
    os.makedirs(os.path.join(mdir2, "x.properties"))
    open(os.path.join(mdir2, "f.properties"), "w").write("class=Archer\n")
    Store.DIR = Paths.get(mdir2)
    Mig.runOnce()
    marker2 = os.path.join(os.path.dirname(mdir2), "kits.properties")
    check(not os.path.exists(marker2) and fileprops("f", mdir2).get("kit") == "old", "a failure leaves the marker unwritten (others still marked)")
    os.rmdir(os.path.join(mdir2, "x.properties"))
    Mig.runOnce()
    check(os.path.isfile(marker2) and props_of(open(marker2, encoding="latin-1").read()).get("marked") == "0", "the next start retries and writes the marker")
    Store.DIR = Paths.get(os.path.join(work, "n3", "nothing", "players"))
    Mig.runOnce()
    check(os.path.isfile(os.path.join(work, "n3", "nothing", "kits.properties")), "no players folder yet (new server): marker written, 0 marked")
    print("N. migration done")

    # ---------------- O. setClassKey marking + kit state writes
    odir = os.path.join(work, "o", "Skyy_SkyyClasses", "players")
    os.makedirs(odir)
    Store.DIR = Paths.get(odir)
    names16 = [str(x) for x in Defs.NAMES]
    PR_, WA, AR, BE = names16.index("Priest"), names16.index("Warrior"), names16.index("Archer"), names16.index("Berserker")
    ko1 = "00000000-0000-0000-0000-00000000e001"
    check(bool(Store.setClassKey(ko1, PR_, True, False)), "first choice saved")
    fp = fileprops(ko1, odir)
    check(fp.get("class") == "Priest" and fp.get("kit") == "pending" and fp.get("kitClass") == "Priest" and str(Store.KITQ.get(ko1)) == "pending",
          "first class of a flagless file -> kit pending in the same write: %s" % fp)
    ko2 = "00000000-0000-0000-0000-00000000e002"
    open(os.path.join(odir, ko2 + ".properties"), "w").write("kit=old\nplayed=Archer\n")      # reset after the migration
    Store.setClassKey(ko2, WA, False, False)
    check(fileprops(ko2, odir).get("kit") == "old" and fileprops(ko2, odir).get("class") == "Warrior" and not Store.KITQ.containsKey(ko2),
          "a choice after a reset of an old profile stays old")
    ko3 = "00000000-0000-0000-0000-00000000e003"
    KitCfg.ON = False
    Store.setClassKey(ko3, AR, True, False)
    KitCfg.ON = True
    check(fileprops(ko3, odir).get("kit") == "off" and not Store.KITQ.containsKey(ko3), "kits off at the pick -> off")
    ko4 = "00000000-0000-0000-0000-00000000e004"
    open(os.path.join(odir, ko4 + ".properties"), "w").write("class=Archer\n")
    Store.setClassKey(ko4, WA, False, False)
    check("kit" not in fileprops(ko4, odir), "a file that already had a class gets no kit flag")
    Store.setClassKey(ko1, -1, False, False)
    Store.setClassKey(ko1, BE, True, False)
    check(fileprops(ko1, odir).get("kit") == "pending" and fileprops(ko1, odir).get("kitClass") == "Priest", "reset + a new pick never re-marks")
    ko5 = "00000000-0000-0000-0000-00000000e005"
    check(bool(Store.kitBegin(ko5, "Archer", "Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64")), "kitBegin")
    fp = fileprops(ko5, odir)
    check(fp.get("kit") == "given" and fp.get("kitOwed") == fp.get("kitItems") == "Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64" and "kitGivenAt" in fp,
          "kitBegin writes given + the in-flight list first")
    check("interrupted while giving" in str(Store.kitText(Store.loadKey(ko5))), "an interrupted give shows in /classadmin info")
    Store.kitEnd(ko5, "Weapon_Arrow_Crude:14")
    check(fileprops(ko5, odir).get("kit") == "owed" and str(Store.kitText(Store.loadKey(ko5))) == "kit owed: Weapon_Arrow_Crude x14 (Archer)",
          "a remainder becomes a claim: %s" % Store.kitText(Store.loadKey(ko5)))
    Kit.requeue(ko5)
    check(str(Store.KITQ.get(ko5)) == "owed", "requeue: owed")
    check(str(Store.kitClaimBegin(ko5)) == "Weapon_Arrow_Crude:14" and fileprops(ko5, odir).get("kit") == "given", "claim begins: owed -> given")
    Store.kitEnd(ko5, "")
    Kit.requeue(ko5)
    fp = fileprops(ko5, odir)
    check(fp.get("kit") == "given" and "kitOwed" not in fp and not Store.KITQ.containsKey(ko5), "claim done: nothing owed, not queued")
    line = str(Kit.stateLine(Store.loadKey(ko5)))
    check(line.startswith("Nothing is waiting. Your Archer kit (Shortbow Crude x1, Arrow Crude x64) was given on 20"), "/class kit text: %s" % line)
    check(Store.kitClaimBegin(ko5) is None, "nothing owed -> no claim")
    Store.kitMerge(ko5, "Archer", "Weapon_Arrow_Crude:3")
    Store.kitMerge(ko5, "Archer", "Weapon_Arrow_Crude:2")
    check(fileprops(ko5, odir).get("kitOwed") == "Weapon_Arrow_Crude:3,Weapon_Arrow_Crude:2", "admin kits on a given profile: remainders add up")
    check(bool(Store.kitMerge(ko5, "Archer", "")), "an admin kit that fit changes nothing")
    # review fix: a give interrupted between kitBegin and kitEnd (crash) - the texts say it may or may not have landed; a same-class admin
    # re-give clears the in-flight record, another class's admin kit leaves it
    ko6 = "00000000-0000-0000-0000-00000000e006"
    check(bool(Store.kitBegin(ko6, "Priest", "Weapon_Wand_Wood:1")), "kitBegin (interrupted give)")
    check("may or may not have landed" in str(Store.kitText(Store.loadKey(ko6))), "info: an interrupted give is ambiguous: %s" % Store.kitText(Store.loadKey(ko6)))
    check("server stopped" in str(Kit.stateLine(Store.loadKey(ko6))), "/class kit tells the player about an interrupted give: %s" % Kit.stateLine(Store.loadKey(ko6)))
    check(bool(Store.kitMerge(ko6, "Archer", "")) and fileprops(ko6, odir).get("kitOwed") == "Weapon_Wand_Wood:1", "another class's admin kit keeps the in-flight record")
    check(bool(Store.kitMerge(ko6, "Priest", "")) and "kitOwed" not in fileprops(ko6, odir) and fileprops(ko6, odir).get("kit") == "given",
          "a same-class admin re-give clears the in-flight record: %s" % fileprops(ko6, odir))
    line = str(Kit.stateLine(Store.loadKey(ko6)))
    check(line.startswith("Nothing is waiting. Your Priest kit (Wand Wood x1) was given on 20") and "interrupted" not in str(Store.kitText(Store.loadKey(ko6))),
          "... and the texts are normal again: %s" % line)
    ko7 = "00000000-0000-0000-0000-00000000e007"
    Store.kitBegin(ko7, "Priest", "Weapon_Wand_Wood:1,Weapon_Spellbook_Frost:1")
    Store.kitMerge(ko7, "Priest", "Weapon_Spellbook_Frost:1")
    fp = fileprops(ko7, odir)
    check(fp.get("kit") == "owed" and fp.get("kitOwed") == "Weapon_Spellbook_Frost:1", "same-class re-give with a remainder: only the remainder is owed: %s" % fp)
    for st_, want_ in (("old", "chose its class before class kits existed"), ("off", "Class kits were off"), ("pending", "is on its way")):
        pp = JClass("java.util.Properties")()
        pp.setProperty("kit", st_)
        pp.setProperty("kitClass", "Priest")
        check(want_ in str(Kit.stateLine(pp)), "/class kit text for %s" % st_)
    check(str(Store.kitText(JClass("java.util.Properties")())) == "no kit yet", "info: no kit yet")
    print("O. kit state done")

    # ---------------- P. heal math + aggregator
    HT, HB = JClass(PKG + "HealTask"), JClass(PKG + "HealBudget")
    check(float(HT.want(40.0, 25, 10.0)) == 10.0 and float(HT.want(20.0, 25, 10.0)) == 5.0 and float(HT.want(0.0, 25, 10.0)) == 0.0
          and float(HT.want(20.0, 0, 10.0)) == 0.0 and float(HT.want(6.0, 500, 1000.0)) == 30.0, "member share = min(damage x %, per-hit cap)")
    check(float(HT.selfWant(5.0, 50)) == 2.5 and float(HT.selfWant(5.0, 0)) == 0.0 and float(HT.selfWant(5.0, 100)) == 5.0, "Priest self %")
    check(float(HT.room(5.0, JFloat(98.0), JFloat(100.0))) == 2.0 and float(HT.room(5.0, JFloat(100.0), JFloat(100.0))) == 0.0
          and float(HT.room(5.0, JFloat(0.0), JFloat(100.0))) == 0.0 and float(HT.room(1.5, JFloat(50.0), JFloat(100.0))) == 1.5,
          "overheal clamp (full = 0, dead = 0)")
    T1 = UUID.fromString("00000000-0000-0000-0000-00000000f001")
    HB.forget(T1)
    a_ = float(HB.take(T1, 6.0, 1000, 10.0))
    b_ = float(HB.take(T1, 6.0, 1500, 10.0))                # a second Priest in the same second
    c_ = float(HB.take(T1, 1.0, 1999, 10.0))
    d_ = float(HB.take(T1, 6.0, 2000, 10.0))                # next window
    check((a_, b_, c_, d_) == (6.0, 4.0, 0.0, 6.0), "1 s budget per target shared by all Priests: %s" % ((a_, b_, c_, d_),))
    check(float(HB.take(T1, -1.0, 5000, 10.0)) == 0.0 and float(HB.take(None, 1.0, 5000, 10.0)) == 0.0, "budget garbage = 0")
    Msg.forget(P1)
    A1, A2 = UUID.fromString("00000000-0000-0000-0000-00000000f0a1"), UUID.fromString("00000000-0000-0000-0000-00000000f0a2")
    P2 = UUID.fromString("00000000-0000-0000-0000-00000000c002")
    for u_ in (A1, A2, P2):
        Msg.forget(u_)
    Msg.given(P1, P1, 6.0)
    Msg.given(P1, A1, 12.0)
    Msg.given(P1, A2, 11.0)
    Msg.taken(A1, P1, "Skyy", 12.0)
    Msg.taken(A2, P1, "Skyy", 7.0)
    Msg.taken(A2, P2, "Other", 4.0)
    d = [[str(x) for x in e][:3] for e in Msg.due(10000, 5000)]
    check([str(P1), "Heals: +23 HP to your party (2 players) and +6 HP to you", "classes.healGiven"] in d, "Priest line: %s" % d)
    check([str(A1), "Skyy healed you +12 HP", "classes.healTaken"] in d and [str(A2), "Priests healed you +11 HP", "classes.healTaken"] in d,
          "member lines (one healer by name, several = Priests): %s" % d)
    check(str(Msg.givenText(0.0, 0, 2.54)) == "Heals: +2.5 HP to you" and Msg.givenText(0.0, 0, 0.0) is None
          and str(Msg.givenText(3.0, 1, 0.0)) == "Heals: +3 HP to your party (1 player)", "solo Priest / nothing / one member")
    Msg.LASTG.put(P1, JClass("java.lang.Long").valueOf(9000))
    Msg.given(P1, P1, 1.0)
    check(len(Msg.due(10000, 5000)) == 0 and Msg.GIVEN.containsKey(P1), "a line waits for its interval (heals keep adding up)")
    check(len(Msg.due(14000, 5000)) == 1, "then it is due")
    print("P. heal math done")

    # ---------------- Q. checkKit
    Cfg.UNASSIGNED_BLOCKED = True
    q = KitHooks.checkKit("kit.Archer", "Weapon_Sword_Crude:1")
    check(q is not None and str(q) == "?Weapon_Sword_Crude is a Warrior weapon - an Archer cannot fight with it. Save anyway?", "Archer kit + sword: %s" % q)
    q = KitHooks.checkKit("kit.Priest", "Weapon_Sword_Crude:1")
    check(str(q) == "?Weapon_Sword_Crude is a Warrior weapon - a Priest cannot fight with it. Save anyway?", "the spec's example: %s" % q)
    check(KitHooks.checkKit("kit.Priest", "Weapon_Wand_Wood:1,Weapon_Spellbook_Frost:1") is None, "Priest kit with Priest weapons: fine")
    q = KitHooks.checkKit("kit.Archer", "Weapon_Bomb:3")
    check(q is not None and "no class owns" in str(q), "an unowned weapon while unassignedBlocked is on asks: %s" % q)
    Cfg.UNASSIGNED_BLOCKED = False
    check(KitHooks.checkKit("kit.Archer", "Weapon_Bomb:3") is None, "... and is fine while unassignedBlocked is off")
    Cfg.UNASSIGNED_BLOCKED = True
    check("is a Priest weapon - a Shaman" in str(KitHooks.checkKit("kit.Shaman", "Weapon_Wand_Wood:1")), "Shaman kit + wand asks")
    check(KitHooks.checkKit("kit.Archer", "Food_Bread:5,Tool_Hatchet_Crude:1,Weapon_Shield_Iron:1") is None, "free items (food, hatchet, shield): fine")
    check(KitHooks.checkKit("kit.Assassin", "Weapon_Daggers_Crude:1") is None, "a disabled class's own weapon in its own kit: fine")
    check("(and 1 more)" in str(KitHooks.checkKit("kit.Archer", "Weapon_Sword_Crude:1,Weapon_Axe_Iron:1")), "two problems: the first + (and 1 more)")
    check(KitHooks.checkKit("kit.Archer", None) is None and KitHooks.checkKit("nope", "Weapon_Sword_Crude:1") is None, "null value / unknown key")
    r = KitHooks.hbArcher(None, "Console")
    check(str(r[0]) == "bad", "Use my hotbar without an admin in game: refused")
    # review fix: "Use my hotbar" no longer pre-answers the kit check's question - a second click (same admin, kit, hotbar, within 60 s) does
    KHT = JClass(PKG + "KitHotbarTask")
    KHT.ASKED.clear()
    ka = KHT.askKey(P1, "Archer")
    check(int(KHT.ASK_MS) == 60000 and not bool(KHT.again(ka, "Weapon_Sword_Crude:1", 1000)), "first click: not asked yet -> confirm is not pre-set")
    KHT.asked(ka, "Weapon_Sword_Crude:1", 1000)
    check(bool(KHT.again(ka, "Weapon_Sword_Crude:1", 30000)), "second click, same hotbar, in time = Save anyway")
    check(not bool(KHT.again(ka, "Weapon_Sword_Crude:2", 30000)), "a changed hotbar asks again")
    check(not bool(KHT.again(KHT.askKey(P1, "Priest"), "Weapon_Sword_Crude:1", 30000)), "another kit asks again")
    check(not bool(KHT.again(ka, "Weapon_Sword_Crude:1", 61001)) and not KHT.ASKED.containsKey(ka), "too late asks again (and forgets)")
    check(not bool(KHT.again(None, "x", 1)) and not bool(KHT.again(ka, None, 1)), "again garbage = false")
    t_ = str(KHT.askText("Archer", "Weapon_Sword_Crude is a Warrior weapon - an Archer cannot fight with it. Save anyway?"))
    check(t_ == "The Archer kit was NOT changed: Weapon_Sword_Crude is a Warrior weapon - an Archer cannot fight with it. To save it anyway, "
          "click Use my hotbar on the Archer kit again within 60 s with the same hotbar.", "the chat question: %s" % t_)
    KHT.ASKED.clear()
    print("Q. checkKit done")

    # ---------------- T. roster
    check(names16 == ["Archer", "Warrior", "Mage", "Berserker", "Priest", "Assassin", "Shaman"], "roster order %s" % names16)
    check([bool(x) for x in Defs.ENABLED] == [True, True, True, True, True, False, False], "playable: the five, Assassin + Shaman later")
    check(str(Defs.listText()) == "Archer:Archery,Warrior:Swordsmanship,Mage:Sorcery,Berserker:Fury,Priest:Divinity", "class:list %s" % Defs.listText())
    check([str(x) for x in Defs.SKILLS][3:5] == ["Fury", "Divinity"] and str(Defs.ROLES[PR_]) == "AoE healer / support" and int(Defs.PRIEST) == PR_,
          "skills, Priest role and index")
    check(set(str(Defs.prefixesOf(BE)).split(",")) == {"Weapon_Axe_", "Weapon_Battleaxe_", "Weapon_Mace_", "Weapon_Club_"}
          and str(Defs.prefixesOf(PR_)) == "Weapon_Spellbook_,Weapon_Wand_", "class:weapons:Berserker / Priest")
    own = {"Weapon_Axe_Iron": BE, "Weapon_Battleaxe_Crude": BE, "Weapon_Mace_Prisma": BE, "Weapon_Club_Steel_Flail_Rusty": BE,
           "Weapon_Wand_Root": PR_, "Weapon_Spellbook_Rekindle_Embers": PR_, "Tool_Hatchet_Iron": -1, "Weapon_Shield_Iron": -1,
           "Weapon_Deployable_Healing_Totem": -2, "Weapon_Staff_Wood": names16.index("Mage")}
    check(all(int(Defs.ownerOf(k)) == v for k, v in own.items()), "owners (hatchets free, healing totem unassigned): %s"
          % {k: int(Defs.ownerOf(k)) for k in own})
    check(int(Defs.indexOf("fury")) == BE and int(Defs.indexOf("Divinity")) == PR_ and int(Defs.indexOf("priests")) == PR_, "indexOf by skill / plural")
    Store.DIR = Paths.get(odir)
    uw, ua, up, ub = (UUID.fromString("00000000-0000-0000-0000-0000000001%02d" % i) for i in range(4))
    Store.setClassKey(str(uw), WA, True, False)
    Store.setClassKey(str(ua), AR, True, False)
    Store.setClassKey(str(up), PR_, True, False)
    Store.setClassKey(str(ub), BE, True, False)
    check(str(Rules.blockText(uw, "Weapon_Wand_Wood", False)) == "Only Priests can use wands. You are a Warrior - /class shows your weapons.",
          "wand text: %s" % Rules.blockText(uw, "Weapon_Wand_Wood", False))
    check(str(Rules.blockText(ua, "Weapon_Axe_Iron", False)) == "Only Berserkers can use axes. You are an Archer - /class shows your weapons.",
          "axe text: %s" % Rules.blockText(ua, "Weapon_Axe_Iron", False))
    check(bool(Rules.allowed(ub, "Weapon_Axe_Iron")) and bool(Rules.allowed(up, "Weapon_Wand_Wood")) and bool(Rules.allowed(up, "Weapon_Spellbook_Frost"))
          and not bool(Rules.allowed(up, "Weapon_Axe_Iron")) and not bool(Rules.allowed(ub, "Weapon_Wand_Wood"))
          and bool(Rules.allowed(ua, "Tool_Hatchet_Iron")) and bool(Rules.allowed(up, "Tool_Hatchet_Iron")), "allowed(): the new classes + free hatchets")
    check(not bool(Rules.allowed(up, "Weapon_Deployable_Healing_Totem")), "the Healing Totem stays unassigned (blocked while unassignedBlocked)")
    print("T. roster done")


def main():
    if "--run" in sys.argv:
        run(arg("--run"))
        print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.exit(1 if FAILS else 0)
    if not os.path.isfile(JAR):
        sys.exit("no jar at %s - build it first (python SkyyClasses/build_skyyclasses_%s.py)" % (JAR, VERSION))
    os.makedirs(SCRATCH, exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.makedirs(env["TEMP"], exist_ok=True)
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--run", JAR, "--dir", SCRATCH], env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyClasses %s bare-JVM check:" % VERSION, "PASS" if p.returncode == 0 else "FAIL")
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
