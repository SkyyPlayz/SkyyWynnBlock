"""Bare-JVM check for SkyyClasses 0.1.10 (kept next to the build so the build report's JVM claim can be re-run). Copied from the 0.1.9
harness. 0.1.10 = the Warrior kit's Wood Shield (into an empty off-hand) + the Priest self-heal default 100 + the one-time update of an
existing config.properties (Skyy 2026-10-01). Checks A-X are 0.1.9's with the two new defaults (B, C, D and the row table), the update
before the loader in setup() (I), the kit give through Kit.putKit (X) and the heal maths at 100% (P). New: parts Z + M (their own child
JVM) and part Y now compares 0.1.9 with 0.1.10 (the /class page must be IDENTICAL) plus the class bytes.

    python SkyyClasses/test_skyyclasses_0.1.10.py [--jar <SkyyClasses-0.1.10.jar>] [--old <SkyyClasses-0.1.9.jar>] [--dir <scratch>]
                                                  [--live <the live Skyy_SkyyClasses folder>] [--keep]

Build the jar first (python tools/classes_0_1_10_patch.py, then python SkyyClasses/build_skyyclasses_0.1.10.py). A child process starts a
fresh JVM (the game's own JRE, -Xverify:all, HytaleServer.jar + the jar + tools/javassist.jar on the classpath) and checks:
  A  every class loads and verifies
  B  defaults of the 0.1.6 keys are identical to Skyy's EDITED 0.1.6 except the two 0.1.10 defaults (kit.Warrior + the Wood Shield,
     priestHeal.selfPercent 100); the new keys = the arrow row defaults; the default file carries the update marker above kit.Warrior
  C  a missing file is written with the defaults; an older file keeps working (new keys = code defaults, incl. the two 0.1.10 ones);
     hand-typed keys are clamped
  D  the edited 0.1.6 default file under the config kit (5 categories, 34 rows incl. the greyed-out switchCost / cooldownMinutes,
     KEEP 10, no rewrite at start); the self-heal row's label (40) + help with Skyy's example
  E  get / set per row (the greyed-out rows refuse; kits.enabled + priestHeal.enabled + arrows.enabled part switches, bounds, items)
  F  line-preserving writes (new keys appended under the kit header), the change log, history copies
  G  hand edits + the kit's reload op (new keys clamped by ClassCfg.load); loadInert never touches a bound field
  H  player Settings: notifyOn / regSetting, the ClassRules gates before their throttles
  I  setup() order: FILE -> ClassCfg.migrate0110 -> load -> KitMigrate.runOnce -> bridge puts (class:fn:kitnew) -> ... 4 systems ->
     regSetting x4 -> CfgPub.start last
  J  permissions with the engine's own AbstractCommand code: /class kit in hytale:Adventurer, /classadmin (+ kit) in no group
  K  garbage ops never throw
  L  kit parse (bad entries, 9999, the 9-stack cap, texts)
  M  class:fn:kitnew state table (absent -> pending, old/given/off/owed/pending unchanged, kits off -> off, unreadable -> FALSE, bad keys)
  N  the 'picked before kits' migration (class -> old, no class untouched, marker, second start no-op, a failure retries)
  O  setClassKey marks the first class pending in the same write; kit state writes (begin / end / claim / merge) and texts; an
     interrupted give (texts, cleared by a same-class admin re-give)
  P  Priest heal math (share, self %, per-hit cap, overheal clamp, the 1 s budget across two Priests, 0.1.10: at 100% the Priest's own
     heal = each member's) and the chat aggregator
  Q  checkKit questions (another class's weapon, unowned weapons, free items); "Use my hotbar" second-click confirm (KitHotbarTask)
  T  roster: order, class:list, weapon prefixes, owners (hatchets free, Healing Totem = Priest), block texts, allowed()
  U  daily Archer arrows: cooldown math, the per-profile state writes (begin / end / claim, cooldown + owed re-checked under the lock,
     in-flight record, other keys kept, unreadable file), admin texts, checkArrow, the crash-safe order in Arrows.use / collect
  V  Healing Totem guard: the deployable table, DeployGuard never throws without the Deployables plugin, remove + lock line order;
     review fix: judged strictly (Priest only - classless loses it too, requireClass on or off; unreadable file = kept, logged once)
  W  self-heal XP: the exact skill:fn:healxp call with the trailing Boolean.TRUE; heals on others keep the 4-element call
  X  kit delivery (bytecode): give -> putKit -> offhand (the utility section only) + put(p, 0 = the hotbar only); the quiet arrival retry
     hotbar only (review fix), hotbar-then-storage for /class kit, no 31 s / 3 s waits, KitSoon right after a pick
A second child JVM (-Xverify:all, same classpath) runs:
  Z  the kit hand-out on REAL engine containers: a Player whose Inventory facade holds two SimpleItemContainers (hotbar 9, storage 36)
     and the REAL InventoryComponent$Utility (DEFAULT_UTILITY_CAPACITY slots, its own Utility.Usable slot filter, its active slot),
     test Items in the Item asset map (shields usable, swords / torches as in Assets.zip), a Store / PacketHandler recording the
     InventoryActiveSlotRequestEvent, the InventorySetActiveSlotEvent, the SetActiveSlot packet and the chat lines: an empty
     off-hand (no active slot: the shield goes into utility slot 0, which becomes the active one the vanilla way; the sword into
     the hotbar; Utility.getActiveItem() = the shield = Inventory.getUtilityItem()), an empty active slot (used as it is, no event),
     a taken off-hand (the shield goes the normal way: the hotbar), taken off-hand + full hotbar (all owed, then /class kit = hotbar
     then storage, never the off-hand), no free utility slot, a cancelled / redirected request event (never a second shield),
     /classadmin kit twice (the second shield goes the normal way), the Archer kit (utility untouched), a torch in a kit (only
     shields), two shields, a non-usable Weapon_Shield_ id (refused by the engine filter -> the hotbar, no double give), garbage;
     item counts before / after in every case (given + owed = the kit); the chat line texts; the heal maths at the 0.1.10 default
  M  the one-time update ClassCfg.migrate0110 on scratch files: a COPY of the live Skyy_SkyyClasses config (config.properties +
     config-changes.log + config-history/, copied read-only from --live) as it is (Skyy's hand-set selfPercent=100 kept silently, no
     kit.Warrior line = the new code default, only the marker added, a verified History version, no change-log line), the same copy
     with untouched old defaults (updated once: value text only, two change-log lines Server Setup can Undo, a History copy of the
     old bytes, second start = no change; an Undo through the config kit sets one back and the next start leaves it), with edited
     values (kept + noted), the 0.1.9 default file LF and CRLF (only the two values + the marker line change), a fresh file (load
     writes the 0.1.10 default with the marker, no update), continued / duplicated entries, separators and spaces, a History failure
     (untouched, retried at the next start), the marker already there (never again), no key at all (marker on line 0)
  Y  the /class page (run in the parent, own child JVMs per jar, -Xverify:all): the 16 page states of 0.1.9's harness built by the REAL
     ClassPage.build of the 0.1.10 AND the 0.1.9 jar must be IDENTICAL (bindings, ids, texts, markup; the a=clsclose handler result);
     the 0.1.9 page checks still hold (92 px cards, the kit Close in #SkyyClsBottom, the footer slot, markup / layout / text width /
     contrast through the kit). The SKYY CARD block: byte-identical here and in build_skyyprofiles_0.1.4.py, = CARD_SHA of the patches
     that define it (classes_0_1_9 + profiles_0_1_4) and the CARD_SHA that classes_0_1_10_patch.py asserts. Class bytes 0.1.9 vs
     0.1.10: exactly SkyyClassesPlugin (setup: the version + the migrate0110 call), ClassCfg (the new default file + selfPercent 100 in
     load + the 6 update methods), Kit (give through putKit, tellGiven with the off-hand line, offhand / select / putKit / givenLine),
     KitCfg (the Warrior kit default), CfgRows (version + the row table), CfgFn / KitMigrate (version only) and manifest.json differ;
     ClassPage.class is byte-identical.
Not testable without the game (listed as UNVERIFIED in the build report): the Inspect-group heal on a real hit, addStatValue on another
player, the client showing the shield in the off-hand after the SetActiveSlot packet, the kit arriving with real players and SkyyProfiles
switches, DeployGuard on a real thrown totem, popups, the pages on a client.
Nothing is deployed and nothing is written outside the scratch folder (the live config is only read, then copied). Default scratch
folder: tools/dev/scratch/cls0110/classes-0110 (git-ignored), deleted at the end unless --keep; TEMP/TMP and java.io.tmpdir point into it.
Exit code 1 on any failure.
"""
import os, sys, re, shutil, subprocess, time, json, zipfile, hashlib, struct, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
VERSION = "0.1.10"
PKG = "com.skyy.classes."


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "cls0110", "classes-0110")))
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
    """Skyy's EDITED 0.1.6 build script (commit ab75b6c): its DEF_* values and default file lines. The script is never run: only its
    pure-Python table part (CLASSES = [ ... up to SYNC_STEADY_MS) is executed, then CFG_LINES is evaluated in that namespace."""
    src = open(os.path.join(HERE, "build_skyyclasses_0.1.6.py"), encoding="utf8").read()
    a, b = src.index("\nCLASSES = ["), src.index("\nSYNC_STEADY_MS = ")
    ns = {}
    exec(src[a:b], ns)
    m = re.search(r"^CFG_LINES = (.*?)\n(?=F\(cfg, )", src, re.M | re.S)     # the whole expression (list + comprehension + list)
    lines = eval(m.group(1), ns)
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


SWITCH_ROWS = [  # 0.1.7 (LOCKED Skyy 2026-09-25): shown greyed out (read only) while class switching is off
    ("switchCost", "picker", "int", "5000", "0", "", "", "coins", "ro"),
    ("cooldownMinutes", "picker", "int", "60", "0", "", "", "min", "ro"),
]
ARROW_ROWS = [  # 0.1.7 daily Archer arrows
    ("arrows.enabled", "arrows", "bool", "true", "", "", "", "", "live,part,danger"),
    ("arrows.item", "arrows", "items", "Weapon_Arrow_Crude", "1", "1", "", "", "live"),
    ("arrows.amount", "arrows", "int", "64", "1", "9999", "", "", "live"),
    ("arrows.cooldownHours", "arrows", "int", "24", "1", "168", "", "h", "live"),
]
NEW_ROWS = [  # (key, cat, type, default, min, max, opts, unit, flags) - the 0.1.6 rows (spec 2.5)
    ("kits.enabled", "kits", "bool", "true", "", "", "", "", "live,part,danger"),
    ("kit.Archer", "kits", "items", "Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64", "0", "9", "qty", "", "new"),
    ("kit.Archer.fromHotbar", "kits", "action", "", "", "", "Use my hotbar", "", "new,danger"),
    ("kit.Warrior", "kits", "items", "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1", "0", "9", "qty", "", "new"),   # 0.1.10: + Wood Shield
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
    ("priestHeal.selfPercent", "priest", "int", "100", "0", "100", "", "%", "live"),                               # 0.1.10: 50 -> 100
    ("priestHeal.radius", "priest", "dec", "16", "1", "64", "", "blocks", "live"),
    ("priestHeal.maxPerHit", "priest", "dec", "10", "0.5", "1000", "", "", "live"),
    ("priestHeal.maxPerSecond", "priest", "dec", "10", "0.5", "1000", "", "", "live"),
    ("priestHeal.messages", "priest", "bool", "true", "", "", "", "", "live"),
    ("priestHeal.feedbackMs", "priest", "int", "10000", "1000", "60000", "", "ms", "live,adv"),
]
DEF16 = "switchCost=5000 cooldownMinutes=60 requireClass=false unassignedBlocked=true promptEveryLogin=true openDelayMillis=2000" \
        " kits=on priestHeal=on healShare=25% self=100% radius=16 arrows=on 64xWeapon_Arrow_Crude/24h"
DEF15 = DEF16.replace("self=100%", "self=50%")      # the edited 0.1.6 default file read as it is (Cfg.load alone never updates a file)
# 0.1.10: the two changed defaults (key, the old default text, the 0.1.10 default text) and the update's marker / name
NEW_DEFAULTS = [("kit.Warrior", "Weapon_Sword_Crude:1", "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"), ("priestHeal.selfPercent", "50", "100")]
MARK_ID = "SkyyClasses 0.1.10 defaults"
MG_WHO = "SkyyClasses 0.1.10"
SELF_LABEL = "Priest self-heal (% of what members get)"
SELF_HELP = "% of what one party member gets. 100 = the Priest heals as much as each party member. 0 = never."


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
    ns, lines15 = old_defaults()          # lines15 / text15 = Skyy's EDITED 0.1.6 default file (the names are kept from the 0.1.6 harness)
    check(int(Cfg.SWITCH_COST) == ns["DEF_SWITCH_COST"] and int(Cfg.COOLDOWN_MIN) == ns["DEF_COOLDOWN_MIN"]
          and bool(Cfg.REQUIRE_CLASS) == ns["DEF_REQUIRE_CLASS"] and bool(Cfg.UNASSIGNED_BLOCKED) == ns["DEF_UNASSIGNED_BLOCKED"]
          and bool(Cfg.PROMPT_EVERY_LOGIN) == ns["DEF_PROMPT_EVERY_LOGIN"] and int(Cfg.OPEN_DELAY_MS) == ns["DEF_OPEN_DELAY_MS"]
          and bool(Cfg.HEAL_ON) == ns["DEF_HEAL_ON"] and int(Cfg.HEAL_SHARE_PCT) == ns["DEF_HEAL_SHARE_PCT"]
          and int(Cfg.HEAL_SELF_PCT) == 100 and ns["DEF_HEAL_SELF_PCT"] == 50 and float(Cfg.HEAL_RADIUS) == ns["DEF_HEAL_RADIUS"]
          and bool(KitCfg.ON) == ns["DEF_KITS_ON"], "field defaults = the edited 0.1.6 DEF_* (0.1.10: selfPercent 50 -> 100)")
    check(str(KitCfg.K_WARRIOR) == "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" and str(KitCfg.K_ARCHER) == "Weapon_Shortbow_Crude:1,Weapon_Arrow_Crude:64"
          and str(KitCfg.K_PRIEST) == "Weapon_Wand_Wood:1", "0.1.10 kit field defaults: the Warrior kit has the Wood Shield, the others are 0.1.9's")
    check(int(Cfg.HEAL_MSG_MS) == 10000 and ns["DEF_HEAL_MSG_MS"] == 10000, "heal chat lines every 10 s (Skyy's edited default, kept)")
    check(not bool(Cfg.ALLOW_SWITCH), "ALLOW_SWITCH is false (design lock)")
    text15 = "".join(l + "\n" for l in lines15)
    text16 = "".join(str(l) + "\n" for l in Cfg.DEFAULT_LINES)
    p15, p16 = props_of(text15), props_of(text16)
    _chg = dict((k_, (o_, n_)) for k_, o_, n_ in NEW_DEFAULTS)
    check(all(p16.get(k) == v for k, v in p15.items() if k not in _chg), "0.1.6 keys + values unchanged in the default file (but the two 0.1.10 defaults)")
    check(all(p15.get(k) == o_ and p16.get(k) == n_ for k, (o_, n_) in _chg.items()),
          "0.1.10: kit.Warrior + priestHeal.selfPercent: the edited 0.1.6 had the old defaults, 0.1.10 writes the new ones")
    _l16 = text16.split("\n")
    _mk = [i for i, l in enumerate(_l16) if MARK_ID in l]
    check(len(_mk) == 1 and _l16[_mk[0]].startswith("# ") and "=" not in _l16[_mk[0]] and _l16[_mk[0] + 1].startswith("kit.Warrior=")
          and str(Cfg.MG_MARK) == _l16[_mk[0]], "0.1.10: the default file carries the update marker (a doc comment) right above kit.Warrior")
    check("off-hand" in text16 and "selfPercent 100" in text16, "0.1.10 default file comments: the off-hand line, selfPercent 100")
    check(list(p16)[:len(p15)] == list(p15), "0.1.6 keys keep their order (new keys after them)")
    check(p15.get("priestHeal.feedbackMs") == "10000" and p16.get("priestHeal.feedbackMs") == "10000", "feedbackMs=10000 in both default files")
    for r in NEW_ROWS + ARROW_ROWS:
        if r[2] not in ("action",):
            check(p16.get(r[0]) == r[3], "default file %s = row default %r (got %r)" % (r[0], r[3], p16.get(r[0])))
    check(set(p16) - set(p15) == set(r[0] for r in ARROW_ROWS), "the default file adds exactly the arrow keys: %s" % sorted(set(p16) - set(p15)))
    check("greyed out" in text16 and "straight into the hotbar" in text16 and "31 s" not in text16, "default file comments: greyed out, hotbar, no 31 s")
    check([str(x) for x in Rows.defLines(0)] == [str(x) for x in Cfg.DEFAULT_LINES], "kit DEFAULTS text = ClassCfg.DEFAULT_LINES")
    check(bool(KitCfg.ON) and int(Cfg.HEAL_SHARE_PCT) == 25 and int(Cfg.HEAL_SELF_PCT) == 100 and float(Cfg.HEAL_RADIUS) == 16.0
          and float(Cfg.HEAL_MAX_HIT) == 10.0 and float(Cfg.HEAL_MAX_SEC) == 10.0 and bool(Cfg.HEAL_ON) and bool(Cfg.HEAL_MSG)
          and int(Cfg.HEAL_MSG_MS) == 10000, "0.1.6 field defaults (spec 2.5)")
    check(bool(Cfg.ARROWS_ON) and str(Cfg.ARROWS_ITEM) == "Weapon_Arrow_Crude" and int(Cfg.ARROWS_AMOUNT) == 64 and int(Cfg.ARROWS_HOURS) == 24,
          "arrow field defaults (64 Crude Arrows every 24 h)")
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
    check(bool(KitCfg.ON) and int(Cfg.HEAL_SHARE_PCT) == 25 and str(KitCfg.K_PRIEST) == "Weapon_Wand_Wood:1" and str(KitCfg.K_SHAMAN) == ""
          and bool(Cfg.ARROWS_ON) and int(Cfg.ARROWS_AMOUNT) == 64 and str(Cfg.ARROWS_ITEM) == "Weapon_Arrow_Crude",
          "a file without the new keys = code defaults")
    check(str(KitCfg.K_WARRIOR) == "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" and int(Cfg.HEAL_SELF_PCT) == 100,
          "0.1.10: a file without kit.Warrior / priestHeal.selfPercent = the new code defaults (Wood Shield, 100%%)")
    check(not bool(Cfg.ALLOW_SWITCH) and str(Hooks.customGet("classSwitching")) == "false", "allowSwitch / classSwitching lines never turn switching on")
    r = Hooks.customSet("classSwitching", "true")
    check(str(r[0]) == "bad" and r[1] is None and "design lock" in str(r[2]), "ClassHooks.customSet always refuses")
    typed = os.path.join(work, "typed", "Skyy_SkyyClasses", "config.properties")
    os.makedirs(os.path.dirname(typed))
    open(typed, "w", newline="\n").write("kits.enabled=off\nkit.Archer=  Weapon_Sword_Crude:2  \npriestHeal.enabled=no\npriestHeal.sharePercent=900\n"
                                         "priestHeal.selfPercent=-5\npriestHeal.radius=0.2\npriestHeal.maxPerHit=5000\npriestHeal.maxPerSecond=abc\n"
                                         "priestHeal.messages=0\npriestHeal.feedbackMs=10\narrows.enabled=off\narrows.item=Weapon_Arrow_Iron:5\n"
                                         "arrows.amount=0\narrows.cooldownHours=500\n")
    Cfg.FILE = Paths.get(typed)
    Cfg.load()
    check(not bool(KitCfg.ON) and str(KitCfg.K_ARCHER) == "Weapon_Sword_Crude:2" and not bool(Cfg.HEAL_ON) and int(Cfg.HEAL_SHARE_PCT) == 500
          and int(Cfg.HEAL_SELF_PCT) == 0 and float(Cfg.HEAL_RADIUS) == 1.0 and float(Cfg.HEAL_MAX_HIT) == 1000.0
          and float(Cfg.HEAL_MAX_SEC) == 10.0 and not bool(Cfg.HEAL_MSG) and int(Cfg.HEAL_MSG_MS) == 1000,
          "hand-typed new keys: words, trims and the row bounds as clamps (%s)" % Cfg.summary())
    check(not bool(Cfg.ARROWS_ON) and str(Cfg.ARROWS_ITEM) == "Weapon_Arrow_Crude" and int(Cfg.ARROWS_AMOUNT) == 1 and int(Cfg.ARROWS_HOURS) == 168,
          "hand-typed arrow keys: off, a bad item (with an amount) falls back, amount / hours clamped (%s)" % Cfg.summary())
    open(typed, "w", newline="\n").write("arrows.item=  Weapon_Arrow_Iron  \narrows.amount=20000\narrows.cooldownHours=0\n")
    Cfg.load()
    check(str(Cfg.ARROWS_ITEM) == "Weapon_Arrow_Iron" and int(Cfg.ARROWS_AMOUNT) == 9999 and int(Cfg.ARROWS_HOURS) == 1,
          "arrow item trimmed, amount / hours clamped to 9999 / 1")
    Cfg.FILE = Paths.get(fresh)
    Cfg.load()
    check(str(Cfg.summary()) == DEF16, "back to the defaults")
    print("C. load paths done")

    # ---------------- D. the 0.1.5 default file under the kit
    mods = os.path.join(work, "mods")
    home = os.path.join(mods, "Skyy_SkyyClasses")
    os.makedirs(home)
    cfgp = os.path.join(home, "config.properties")
    open(cfgp, "w", newline="\n").write(text15)          # exactly what the edited 0.1.6 writes when the file is missing
    Cfg.FILE = Paths.get(cfgp)
    Cfg.load()
    check(str(Cfg.summary()) == DEF15, "0.1.6 file read back as it is (selfPercent=50 in that file; Cfg.load alone never updates a file): %s" % Cfg.summary())
    Pub.start(Paths.get(mods), None)
    bridge = Cfg.bridge()
    fn = bridge.get("config:fn:SkyyClasses")
    hdr = bridge.get("config:def:SkyyClasses")
    check(fn is not None and hdr is not None, "config:fn + config:def published")
    check(str(bridge.get("config:epoch:SkyyClasses")) == "0", "epoch starts at 0")
    check(len(hdr) == 10 and str(hdr[0]) == "1" and str(hdr[1]) == "SkyyClasses" and str(hdr[2]) == "Classes" and str(hdr[3]) == VERSION
          and str(hdr[4]) == "skyyclasses.admin", "header 0-4 %s" % ([str(hdr[i]) for i in range(5)],))
    check([str(x) for x in hdr[5]] == ["lock", "picker", "kits", "priest", "arrows"]
          and [str(x) for x in hdr[6]] == ["Weapon lock", "Class picker", "Class kits", "Priest heal", "Archer arrows"], "categories")
    check(int(Rows.KEEP) == 10, "config history keeps 10 versions (LOCKED 2026-09-25, was 20): %s" % Rows.KEEP)
    check(str(hdr[8]) == "Skyy_SkyyClasses/config.properties" and 0 < len(str(hdr[9])) <= 100 and "kit" in str(hdr[9]), "files + note")
    rows = [[str(x) for x in row] for row in hdr[7]]
    want = [("requireClass", "lock", "bool", "false", "", "", "", "", "live,danger"),
            ("unassignedBlocked", "lock", "bool", "true", "", "", "", "", "live"),
            ("promptEveryLogin", "picker", "bool", "true", "", "", "", "", "live"),
            ("openDelayMillis", "picker", "int", "2000", "250", "60000", "step=250", "ms", "live,adv"),
            ("classSwitching", "picker", "bool", "false", "", "", "", "", "ro")] + SWITCH_ROWS + NEW_ROWS + ARROW_ROWS
    check(len(rows) == 34 and all(len(x) == 11 for x in rows), "34 rows of 11 (%d)" % len(rows))
    for got, w in zip(rows, want):
        check((got[0], got[2], got[3], got[4], got[5], got[6], got[7], got[8], got[9]) == w, "row %s = %s (got %s)" % (w[0], w, got))
    check(all(len(x[10]) <= 100 and len(x[1]) <= 40 for x in rows), "labels <= 40, help <= 100")
    _sp = [x for x in rows if x[0] == "priestHeal.selfPercent"]
    check(len(_sp) == 1 and _sp[0][1] == SELF_LABEL and _sp[0][10] == SELF_HELP and "100 = the Priest heals as much as each party member" in _sp[0][10],
          "0.1.10: the self-heal row label %r + help with Skyy's example %r" % (_sp[0][1] if _sp else None, _sp[0][10] if _sp else None))
    check([x[9] for x in rows if x[0] in ("switchCost", "cooldownMinutes")] == ["ro", "ro"],
          "switchCost / cooldownMinutes are shown greyed out (read-only rows, LOCKED 2026-09-25)")
    Pub.flush()
    time.sleep(0.3)
    Pub.flush()
    check(open(cfgp, "rb").read().decode("latin-1") == text15, "the kit does not rewrite the 0.1.6 file at start")
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
    check(get("switchCost") == "5000" and get("cooldownMinutes") == "60" and get("nope") is None,
          "the greyed-out rows show the live values; unknown keys stay unknown")
    check((get("arrows.enabled"), get("arrows.item"), get("arrows.amount"), get("arrows.cooldownHours")) == ("true", "Weapon_Arrow_Crude", "64", "24"),
          "initial gets of the arrow rows")
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
    r = cset("switchCost", "1")
    check(r[0] == "bad" and "read-only" in r[2] and int(Cfg.SWITCH_COST) == 5000, "switchCost is greyed out: refused (%s)" % (r,))
    r = cset("cooldownMinutes", "5", confirm="")
    check(r[0] == "bad" and int(Cfg.COOLDOWN_MIN) == 60, "cooldownMinutes is greyed out: refused (%s)" % (r,))
    r = R(op("set", "switchCost", None, None, None, "yes", "console"))
    check(r[0] == "bad", "a reset of a greyed-out row is refused too: %s" % (r,))
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
    # arrow rows
    r = cset("arrows.enabled", "false", confirm="")
    check(r[0] == "confirm" and bool(Cfg.ARROWS_ON), "arrows.enabled OFF asks first (part switch): %s" % (r,))
    check(cset("arrows.amount", "0")[0] == "bad" and cset("arrows.amount", "10000")[0] == "bad" and int(Cfg.ARROWS_AMOUNT) == 64, "amount outside 1-9999 refused")
    r = cset("arrows.amount", "100", confirm="")
    check(r[0] == "ok" and int(Cfg.ARROWS_AMOUNT) == 100, "arrows.amount live: %s" % (r,))
    check(cset("arrows.cooldownHours", "200")[0] == "bad" and cset("arrows.cooldownHours", "0")[0] == "bad", "hours outside 1-168 refused")
    r = cset("arrows.cooldownHours", "12h", confirm="")
    check(r[0] == "ok" and r[1] == "12" and int(Cfg.ARROWS_HOURS) == 12, "arrows.cooldownHours live (typed 12h, unit h, no scale): %s" % (r,))
    r = cset("arrows.item", "Weapon_Arrow_Crude,Weapon_Arrow_Iron")
    check(r[0] == "bad" and str(Cfg.ARROWS_ITEM) == "Weapon_Arrow_Crude", "exactly one arrow item: %s" % (r,))
    r = cset("arrows.item", "")
    check(r[0] == "bad", "the arrow item cannot be emptied: %s" % (r,))
    A = UUID.fromString("00000000-0000-0000-0000-0000000000aa")
    check(R(op("set", "unassignedBlocked", "true", A, "Someone", "yes", "menu"))[0] == "denied" and not bool(Cfg.UNASSIGNED_BLOCKED),
          "a player without skyyclasses.admin is denied")
    check(R(op("set", "unassignedBlocked", "true", None, "Ghost", "yes", "command"))[0] == "denied", "null who via command is denied")
    r = R(op("action", "kit.Archer.fromHotbar", None, "Console", "yes", "console"))
    check(r is not None and r[0] == "bad" and "in game" in r[2], "Use my hotbar from the console: refused (needs an admin in game): %s" % (r,))
    check(int(str(bridge.get("config:epoch:SkyyClasses"))) == 12, "epoch counts the 12 applied changes (%s)" % bridge.get("config:epoch:SkyyClasses"))
    print("E. get/set done")

    # ---------------- F. files
    settle()
    t = open(cfgp, "rb").read().decode("latin-1")
    exp = (text15.replace("unassignedBlocked=true", "unassignedBlocked=false").replace("promptEveryLogin=true", "promptEveryLogin=false")
           .replace("openDelayMillis=2000", "openDelayMillis=3000").replace("priestHeal.sharePercent=25", "priestHeal.sharePercent=50")
           .replace("priestHeal.radius=16", "priestHeal.radius=20.5").replace("priestHeal.feedbackMs=10000", "priestHeal.feedbackMs=2000"))
    check(t.startswith(exp), "0.1.6 lines: only the changed ones changed in place (comments, order kept):\n%s" % t)
    tail = [l for l in t[len(exp):].split("\n") if l]
    check(tail[:1] == ["# ---- changed in game (SkyWynn Menu) ----"] and set(tail[1:]) == {"arrows.amount=100", "arrows.cooldownHours=12"},
          "the new arrow keys appended once under the kit header: %s" % tail)
    check("switchCost=5000" in t and "cooldownMinutes=60" in t, "the greyed-out rows never write their lines")
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
    check(get("switchCost") == "777" and get("cooldownMinutes") == "0", "the greyed-out rows show the re-read values")
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
    t3 = open(cfgp, "rb").read().decode("latin-1")
    open(cfgp, "w", newline="\n").write(t3 + "arrows.amount=20000\narrows.enabled=no\n")
    r = R(op("reload", None, None, "console"))
    settle()
    check(r[0] == "ok" and r[1] == "2" and int(Cfg.ARROWS_AMOUNT) == 9999 and not bool(Cfg.ARROWS_ON), "hand-typed arrow keys: reload + clamp (%s %s)" % (r, Cfg.summary()))
    check(cset("arrows.enabled", "on", confirm="")[0] == "ok" and bool(Cfg.ARROWS_ON), "arrows back ON")
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
    upd, fset = idx("ClassCfg.migrate0110("), [i for i in idx("ClassCfg.FILE(") if "putstatic" in su[i]]
    check(len(upd) == 1 and fset and ld and fset[0] < upd[0] < ld[0] and "pop" in su[upd[0] + 1],
          "0.1.10: setup: ClassCfg.FILE -> ClassCfg.migrate0110 (once, result dropped) -> ClassCfg.load (the update before the loader and the kit)")
    check(st and rg and ld[0] < min(rg) and max(rg) < st[0] and max(reg) < st[0], "setup order: registrations -> regSetting x4 -> CfgPub.start")
    check(len(idx("registerSystem(")) == 4 and idx("PriestHealSys.<init>") and idx("DeployGuard.<init>"),
          "four systems (ShotTrack, DamageLock, PriestHealSys, DeployGuard), one registerSystem each")
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

    # ---------------- X. kit delivery (LOCKED 2026-09-25: straight into the hotbar, immediately)
    def before(lines, pat, want, span=3):
        at = idx(pat, lines)
        return bool(at) and all(any(want in l for l in lines[max(0, i - span):i]) for i in at)
    gv, cl, bx, cn = code("Kit", "give"), code("Kit", "claim"), code("Kit", "box"), code("Kit", "consider")
    pk_, oh_ = code("Kit", "putKit"), code("Kit", "offhand")
    check(len(idx("Kit.putKit(", gv)) == 1 and not idx("Kit.put(", gv) and len(idx("Kit.put(", pk_)) == 1 and before(pk_, "Kit.put(", "iconst_0")
          and len(idx("Kit.offhand(", pk_)) == 1, "automatic / admin kits: give -> putKit -> offhand (a shield) + put(p, 0 = the hotbar only, ...)")
    check(idx("Inventory.getUtility(", oh_) and idx("Inventory.getActiveUtilitySlot(", oh_) and idx("addItemStackToSlot(", oh_)
          and idx("Kit.select(", oh_) and not idx("getCombined", oh_), "offhand: the utility section only (never a combined container)")
    # review fix (LOCKED 2026-09-25 "overflow that does not fit still waits on /class kit"): where = quiet ? 0 : 1 -> the quiet arrival
    # retry (KitTask mode 2) fills the hotbar only; only an explicit /class kit goes hotbar, then storage. Bytecode of the ternary:
    # iload_3 (quiet) / ifeq / iconst_0 / goto / iconst_1 / istore <where>; room and put then load <where>.
    wh = [i for i, l in enumerate(cl) if "istore" in l and i >= 5 and "iload_3" in cl[i - 5] and "ifeq" in cl[i - 4]
          and "iconst_0" in cl[i - 3] and "goto" in cl[i - 2] and "iconst_1" in cl[i - 1]]
    ld_ = None
    if len(wh) == 1:
        sl_ = cl[wh[0]].split("istore")[1]
        ld_ = "iload" + sl_.strip() if sl_.startswith("_") else "iload " + sl_.strip()
    check(ld_ is not None and before(cl, "Kit.put(", ld_) and before(cl, "Kit.room(", ld_, 2) and not before(cl, "Kit.put(", "iconst_1")
          and not before(cl, "Kit.room(", "iconst_1", 2),
          "claims: where = quiet ? 0 (arrival retry: hotbar only) : 1 (/class kit: hotbar then storage) -> room / put(p, where, ...)")
    kw_, kc_ = code("KitTask", "work"), code("ClassKitCmd", "execute")
    check(before(kw_, "Kit.claim(", "iconst_1") and len(idx("Kit.claim(", kw_)) == 1 and before(kc_, "Kit.claim(", "iconst_0")
          and len(idx("Kit.claim(", kc_)) == 1, "callers: KitTask mode 2 claims quietly (hotbar only), /class kit loudly (hotbar then storage)")
    check(idx("getHotbar(", bx) and idx("getCombinedHotbarFirst(", bx) and not idx("getCombinedStorageHotbarBackpack(", bx),
          "box: 0 = Inventory.getHotbar, 1 = Inventory.getCombinedHotbarFirst")
    kitcc = pool.get(PKG + "Kit")
    storage_first = []
    for mm in kitcc.getDeclaredMethods():
        bos_ = BOS()
        IP(PS(bos_)).print_(mm)
        if "getCombinedStorageHotbarBackpack(" in str(bos_.toString()):
            storage_first.append(str(mm.getName()))
    check(not storage_first, "no storage-first give left in Kit: %s" % storage_first)
    check(not idx("profileEpoch(", cn) and not idx("EPOCH", cn) and not idx("KITARR", cn) and idx("KitTask.<init>", cn),
          "consider: no 31 s epoch wait, no 3 s same-world wait, still hands a KitTask to the world thread")
    kflds = [str(f.getName()) for f in JClass(PKG + "Kit").class_.getDeclaredFields()]
    check(not any(f in kflds for f in ("KITEP", "KITARR", "EPOCH_WAIT_MS", "SAME_WORLD_MS")) and "INFLIGHT" in kflds, "the wait maps are gone: %s" % kflds)
    ka_, ks_, kr_ = code("KitNewFn", "apply"), code("KitNewFn", "soon"), code("KitSoon", "run")
    check(idx("KitNewFn.soon(", ka_) and idx("KitSoon.<init>", ks_) and idx("SCHEDULED_EXECUTOR", ks_) and idx("Kit.consider(", kr_),
          "class:fn:kitnew -> KitNewFn.soon -> KitSoon (scheduler) -> Kit.consider right after the pick")
    check(not idx("sendMessage(", ka_), "kitnew sends no 'on its way' chat line any more")
    asc = code("AdminSetCmd", "execute")
    check(idx("KitNewFn.soon(", asc) and idx("ClassStore.setClass(", asc)[0] < idx("KitNewFn.soon(", asc)[0], "/classadmin set tries a pending kit right away")
    print("X. kit delivery (bytecode) done")

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
    check(sorted(psubs) == ["arrows", "kit"], "/class has the kit + arrows sub-commands: %s" % sorted(psubs))
    mp = pc.getPermissionGroupsRecursive()
    allnodes = [str(x) for k in mp.keySet() for x in mp.get(k)]
    kitnode = str(psubs["kit"].getPermission())
    arrnode = str(psubs["arrows"].getPermission())
    check(list(str(k) for k in mp.keySet()) == ["hytale:Adventurer"] and not any("admin" in n for n in allnodes) and kitnode in allnodes
          and arrnode in allnodes, "/class + /class kit + /class arrows give hytale:Adventurer only player nodes: %s" % mp)
    everyone = Sender(set(allnodes))
    check(bool(pc.hasPermission(everyone)) and bool(psubs["kit"].hasPermission(everyone)) and bool(psubs["arrows"].hasPermission(everyone))
          and not bool(adm.hasPermission(everyone)) and not bool(ak.hasPermission(everyone)),
          "an Adventurer may run /class, /class kit and /class arrows, not /classadmin (kit)")
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
    _ok100 = all(float(HT.selfWant(HT.want(d_, 25, 10.0), 100)) == float(HT.want(d_, 25, 10.0)) for d_ in (0.5, 1.0, 7.5, 20.0, 39.9, 40.0, 100.0, 5000.0))
    check(_ok100, "0.1.10: at 100%% the Priest's own heal = each party member's heal (share 25%%, per-hit cap 10) for every damage")
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
    check(KitHooks.checkArrow("arrows.item", "Weapon_Arrow_Iron") is None and KitHooks.checkArrow("arrows.item", None) is None, "checkArrow: an arrow is fine")
    q = KitHooks.checkArrow("arrows.item", "Weapon_Sword_Crude")
    check(q is not None and str(q).startswith("?Weapon_Sword_Crude is not an arrow") and str(q).endswith("Save anyway?"), "checkArrow asks for a non-arrow: %s" % q)
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
          and set(str(Defs.prefixesOf(PR_)).split(",")) == {"Weapon_Spellbook_", "Weapon_Wand_", "Weapon_Deployable_Healing_Totem"},
          "class:weapons:Berserker / Priest (+ the Healing Totem): %s" % Defs.prefixesOf(PR_))
    check("Weapon_Deployable_" in str(Defs.prefixesOf(-2)).split(","), "the other deployables stay unassigned")
    own = {"Weapon_Axe_Iron": BE, "Weapon_Battleaxe_Crude": BE, "Weapon_Mace_Prisma": BE, "Weapon_Club_Steel_Flail_Rusty": BE,
           "Weapon_Wand_Root": PR_, "Weapon_Spellbook_Rekindle_Embers": PR_, "Tool_Hatchet_Iron": -1, "Weapon_Shield_Iron": -1,
           "Weapon_Deployable_Healing_Totem": PR_, "Weapon_Deployable_Slowness_Totem": -2, "Weapon_Deployable_Turret": -2,
           "Weapon_Staff_Wood": names16.index("Mage")}
    check(all(int(Defs.ownerOf(k)) == v for k, v in own.items()), "owners (hatchets free, Healing Totem = Priest): %s"
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
    check(bool(Rules.allowed(up, "Weapon_Deployable_Healing_Totem")) and not bool(Rules.allowed(uw, "Weapon_Deployable_Healing_Totem"))
          and not bool(Rules.allowed(ua, "Weapon_Deployable_Healing_Totem")) and not bool(Rules.allowed(ub, "Weapon_Deployable_Healing_Totem")),
          "the Healing Totem is Priest only (LOCKED 2026-09-25)")
    check(str(Rules.blockText(uw, "Weapon_Deployable_Healing_Totem", False)) == "Only Priests can use healing totems. You are a Warrior - /class shows your weapons.",
          "totem text: %s" % Rules.blockText(uw, "Weapon_Deployable_Healing_Totem", False))
    check("Healing Totem" in str(Defs.WTEXT[PR_]) and "Weapon_Deployable_Healing_Totem" in str(Defs.ICONS[PR_]), "Priest card: weapon text + 4th icon")
    check(int(Defs.ARCHER) == AR, "ClassDefs.ARCHER")
    print("T. roster done")

    # ---------------- U. daily Archer arrows (per profile, LOCKED 2026-09-25)
    HOUR = 3600000
    CD = 24 * HOUR
    check(int(Store.arrowsLeft(0, 5, CD)) == 0 and int(Store.arrowsLeft(1000, 1000 + CD - 1, CD)) == 1 and int(Store.arrowsLeft(1000, 1000 + CD, CD)) == 0,
          "rolling cooldown: never claimed = ready, 1 ms short = wait, 24 h later = ready")
    check(int(Store.arrowsLeft(10 * HOUR, 9 * HOUR, CD)) == CD - HOUR and int(Store.arrowsLeft(30 * HOUR, 5 * HOUR, CD)) == 0,
          "clock went back: the rest of the cooldown; back by more than a cooldown = ready")
    udir = os.path.join(work, "u", "Skyy_SkyyClasses", "players")
    os.makedirs(udir)
    Store.DIR = Paths.get(udir)
    kar = "00000000-0000-0000-0000-00000000a001-p2"
    open(os.path.join(udir, kar + ".properties"), "w").write("class=Archer\nkit=given\nkitClass=Archer\nplayed=Archer\n")
    T0 = 1790000000000
    r = int(Store.arrowsBegin(kar, "Weapon_Arrow_Crude:64", T0, CD))
    fp = fileprops(kar, udir)
    check(r == 0 and fp.get("arrowsAt") == str(T0) and fp.get("arrowsN") == "1" and fp.get("arrowsFly") == "Weapon_Arrow_Crude:64"
          and fp.get("class") == "Archer" and fp.get("kit") == "given", "begin: arrowsAt + in-flight record written BEFORE the give, other keys kept: %s" % fp)
    check("interrupted while giving" in str(Store.arrowsText(Store.loadKey(kar), T0 + 5, CD)), "an interrupted refill shows in /classadmin info")
    check(int(Store.arrowsBegin(kar, "Weapon_Arrow_Crude:64", T0 + 1000, CD)) == 1 and fileprops(kar, udir).get("arrowsAt") == str(T0),
          "a second claim inside 24 h is refused under the lock (nothing written)")
    check(bool(Store.arrowsEnd(kar, "")) and "arrowsFly" not in fileprops(kar, udir) and "arrowsOwed" not in fileprops(kar, udir), "end: in-flight record gone")
    at_ = str(Store.arrowsText(Store.loadKey(kar), T0 + HOUR, CD))
    check("1 refills, last 20" in at_ and "(next in 23 h)" in at_, "admin text: %s" % at_)
    check(int(Store.arrowsBegin(kar, "Weapon_Arrow_Crude:64", T0 + CD, CD)) == 0 and fileprops(kar, udir).get("arrowsN") == "2", "24 h later: the next refill")
    Store.arrowsEnd(kar, "Weapon_Arrow_Crude:14")
    fp = fileprops(kar, udir)
    check(fp.get("arrowsOwed") == "Weapon_Arrow_Crude:14" and "arrowsFly" not in fp, "what did not fit becomes arrowsOwed")
    check(int(Store.arrowsBegin(kar, "Weapon_Arrow_Crude:64", T0 + 5 * CD, CD)) == 2, "owed arrows must be collected before the next refill")
    check("owed Weapon_Arrow_Crude x14" in str(Store.arrowsText(Store.loadKey(kar), T0 + 5 * CD, CD)), "admin text shows owed arrows")
    check(str(Store.arrowsClaimBegin(kar)) == "Weapon_Arrow_Crude:14" and "arrowsOwed" not in fileprops(kar, udir)
          and fileprops(kar, udir).get("arrowsFly") == "Weapon_Arrow_Crude:14" and Store.arrowsClaimBegin(kar) is None,
          "a claim moves owed -> in flight (a second claim finds nothing)")
    Store.arrowsEnd(kar, "Weapon_Arrow_Crude:4")
    check(fileprops(kar, udir).get("arrowsOwed") == "Weapon_Arrow_Crude:4", "a claim that still does not fit keeps the rest owed")
    Store.arrowsClaimBegin(kar)
    Store.arrowsEnd(kar, "")
    fp = fileprops(kar, udir)
    check("arrowsOwed" not in fp and "arrowsFly" not in fp and fp.get("arrowsAt") == str(T0 + CD) and fp.get("class") == "Archer",
          "claim done: clean, the cooldown untouched by claims: %s" % fp)
    kbad = "00000000-0000-0000-0000-00000000a002"
    os.makedirs(os.path.join(udir, kbad + ".properties"))
    check(int(Store.arrowsBegin(kbad, "Weapon_Arrow_Crude:64", T0, CD)) == -1 and Store.arrowsClaimBegin(kbad) is None and not bool(Store.arrowsEnd(kbad, "")),
          "an unreadable class file: nothing given, nothing written")
    check("never claimed" in str(Store.arrowsText(JClass("java.util.Properties")(), T0, CD)), "admin text: never claimed")
    Arr = JClass(PKG + "Arrows")
    Cfg.ARROWS_HOURS = 24
    Cfg.ARROWS_AMOUNT = 20000
    check(int(Arr.cooldownMs()) == CD and int(Arr.amount()) == 9999, "Arrows.cooldownMs / amount (clamped)")
    Cfg.ARROWS_AMOUNT = 64
    us_, co_ = code("Arrows", "use"), code("Arrows", "collect")
    def first(lines, pat):
        a_ = idx(pat, lines)
        return a_[0] if a_ else -1

    def last(lines, pat):
        a_ = idx(pat, lines)
        return a_[-1] if a_ else -1
    b_, p_, e_ = first(us_, "ClassStore.arrowsBegin("), first(us_, "Kit.put("), first(us_, "ClassStore.arrowsEnd(")
    check(0 <= first(us_, "Kit.busy(") < first(us_, "ClassStore.classIndex(") < b_ and 0 <= first(us_, "KitCfg.known(") < b_
          and 0 <= first(us_, "Kit.room(") < b_ < p_ < e_ and before(us_, "Kit.put(", "iconst_1"),
          "Arrows.use: busy -> Archer -> known item -> room -> arrowsBegin (written first) -> put (hotbar then storage) -> arrowsEnd")
    check(0 <= first(us_, "Arrows.collect(") < first(us_, "ClassCfg.ARROWS_ON"), "owed arrows are collected before the on/off + class checks")
    check(0 <= first(co_, "Kit.room(") < last(co_, "ClassStore.arrowsClaimBegin(") < first(co_, "Kit.put(") < last(co_, "ClassStore.arrowsEnd(")
          and len(idx("Kit.put(", co_)) == 1, "Arrows.collect: room -> claimBegin (in flight first) -> put -> arrowsEnd")
    print("U. daily arrows done")

    # ---------------- V. Healing Totem guard
    check([str(x) for x in Defs.D_IDS] == ["Healing_Totem"] and [str(x) for x in Defs.D_ITEMS] == ["Weapon_Deployable_Healing_Totem"],
          "DeployGuard table from Assets.zip: Healing_Totem <- Weapon_Deployable_Healing_Totem")
    check(str(Defs.deployItem("Healing_Totem")) == "Weapon_Deployable_Healing_Totem" and Defs.deployItem("Slowness_Totem") is None
          and Defs.deployItem(None) is None, "deployItem")
    DG = JClass(PKG + "DeployGuard")
    why_ = ""
    try:
        dg = DG()
        q_ = dg.getQuery()
        ok_ = q_ is not None and DG.TYPE is None and dg.getQuery().equals(q_) and DG.type() is None
        why_ = "query %s TYPE %s" % (q_, DG.TYPE)
    except Exception as ex:
        ok_ = False
        why_ = "threw %s" % ex
    check(ok_, "DeployGuard never throws without the Deployables plugin (bare JVM: Query.any fallback, type retried later): %s" % why_)
    oe = code("DeployGuard", "onEntityAdded")
    check(0 <= first(oe, "AddReason.SPAWN") < first(oe, "DeployableComponent.getConfig(") < first(oe, "ClassDefs.deployItem(")
          < first(oe, "DeployGuard.judge(") < first(oe, "CommandBuffer.removeEntity(") < first(oe, "DeployGuard.text(") < first(oe, "ClassRules.tell(")
          and first(oe, "ClassRules.popup(") > first(oe, "CommandBuffer.removeEntity("),
          "DeployGuard: SPAWN -> config id -> item -> judge -> remove -> lock text -> chat line + popup")
    check(first(oe, "ClassRules.allowed(") < 0 and before(oe, "CommandBuffer.removeEntity(", "iconst_1", 8),
          "review fix: DeployGuard no longer asks ClassRules.allowed (classless = allowed while requireClass is off); removes only on judge == 1")
    # review fix: judged STRICTLY - only a playable Priest keeps the totem; classless and every other class lose it; an unreadable class
    # file keeps it (never removed on a guess) and is logged once. uw / ua / up / ub = Warrior / Archer / Priest / Berserker files (T).
    TOT = "Weapon_Deployable_Healing_Totem"
    Cfg.REQUIRE_CLASS = False
    vdir = os.path.join(work, "v", "Skyy_SkyyClasses", "players")
    os.makedirs(vdir)
    Store.DIR = Paths.get(vdir)
    uc = UUID.fromString("00000000-0000-0000-0000-0000000002c1")        # no class file: classless
    ux = UUID.fromString("00000000-0000-0000-0000-0000000002c2")        # a folder with the file's name: unreadable
    us = UUID.fromString("00000000-0000-0000-0000-0000000002c3")        # class=Assassin (not playable yet)
    os.makedirs(os.path.join(vdir, str(ux) + ".properties"))
    open(os.path.join(vdir, str(us) + ".properties"), "w").write("class=Assassin\n")
    check(bool(Rules.allowed(uc, TOT)), "the weapon lock still lets a classless player through while requireClass is off (unchanged)")
    check(int(DG.judge(up, TOT)) == 0, "judge: a Priest keeps the totem")
    check(int(DG.judge(uw, TOT)) == 1 and int(DG.judge(ua, TOT)) == 1 and int(DG.judge(ub, TOT)) == 1, "judge: Warrior / Archer / Berserker lose it")
    check(int(DG.judge(uc, TOT)) == 1 and Store.DATA.containsKey(str(uc)), "judge: a CLASSLESS player loses it too (requireClass off)")
    Cfg.REQUIRE_CLASS = True
    check(int(DG.judge(uc, TOT)) == 1 and int(DG.judge(up, TOT)) == 0, "judge: the same with requireClass on")
    Cfg.REQUIRE_CLASS = False
    check(int(DG.judge(us, TOT)) == 1, "judge: a class that is not playable (Assassin) loses it")
    check(not bool(DG.UNREAD), "nothing logged yet")
    check(int(DG.judge(ux, TOT)) == 2 and not Store.DATA.containsKey(str(ux)) and bool(DG.UNREAD),
          "judge: an unreadable class file keeps the totem (never removed on a guess), logged once")
    check(int(DG.judge(ux, TOT)) == 2 and int(DG.judge(None, TOT)) == 0 and int(DG.judge(up, None)) == 0, "judge: again 2 (log flag stays), null-safe")
    t_ = str(DG.text(uc, TOT))
    check(t_ == "Only Priests can use healing totems - choose Priest with /class.", "classless lock line (no SkyyProfiles): %s" % t_)
    bridge.put("profile:fn:key", JClass(PKG + "AllowedFn")())             # any Function: profilesOn() = true for the text only
    t_ = str(DG.text(uc, TOT))
    bridge.remove("profile:fn:key")
    check(t_ == "Only Priests can use healing totems - create a Priest profile with /profiles.", "classless lock line (SkyyProfiles): %s" % t_)
    t_ = str(DG.text(uw, TOT))
    check(t_ == "Only Priests can use healing totems. You are a Warrior - /class shows your weapons.", "a class's lock line = the weapon lock's: %s" % t_)
    check(first(oe, "DeployableComponent.getOwner(") >= 0 and first(oe, "getOwnerUUID(") >= 0 and first(oe, "ShotTrack.SHOTS") >= 0,
          "thrower = owner Ref's PlayerRef, else the owner UUID's ShotTrack launch record")
    print("V. totem guard done")

    # ---------------- W. self-heal XP (the exact round-9 call)
    @JImplements("java.util.function.Function")
    class FakeXp(object):
        def __init__(self):
            self.calls = []

        @JOverride
        def apply(self, o):
            self.calls.append([o[i] for i in range(len(o))])
            return JClass("java.lang.Boolean").TRUE

    fx = FakeXp()
    bridge.put("skill:fn:healxp", fx)
    PU = UUID.fromString("00000000-0000-0000-0000-0000000c0de1")
    HT.xpSelf(PU, 2.5)
    HT.xp(PU, 3.0)
    c1 = fx.calls[0] if len(fx.calls) > 0 else []
    c2 = fx.calls[1] if len(fx.calls) > 1 else []
    check(len(c1) == 5 and str(c1[0]) == str(PU) and float(c1[1]) == 2.5 and str(c1[2]) == "classes:heal:self" and str(c1[3]) == str(PU)
          and str(c1[4]).lower() == "true", "self-heal: apply(Object[]{ u, Double hpOnSelf, \"classes:heal:self\", pkey(u), Boolean.TRUE }): %s" % (c1,))
    check(len(c2) == 4 and str(c2[2]) == "classes:heal" and float(c2[1]) == 3.0, "heals on others keep the 4-element call: %s" % (c2,))
    bridge.remove("skill:fn:healxp")
    try:
        HT.xpSelf(PU, 1.0)
        ok_ = True
    except Exception:
        ok_ = False
    check(ok_, "no SkyySkills: xpSelf does nothing, never throws")
    hr = code("HealTask", "run")
    check(0 <= first(hr, "HealTask.xp(") < first(hr, "HealTask.xpSelf("), "HealTask.run pays others first, then the self-heal")
    print("W. self-heal XP done")


# ============================================================================================================== part Y: ClassPage page
# states, 0.1.8 vs 0.1.9 (0.1.9: taller cards, the footer Close, the footer row - the expected differences are checked, nothing else).
# Child JVMs per jar (-Xverify:all, HytaleServer.jar + ONE mod jar); the parent compares. The markup model, text, contrast and SKYY CARD
# checks below are the SAME code as SkyyProfiles/test_skyyprofiles_0.1.3.py (one shared card component in both mods).
OLD_VERSION = "0.1.9"
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyClasses-%s.jar" % OLD_VERSION)))
PREFIX = "SkyyCls"
PAGE_W, PAGE_H = 1100, 854
BODY_ID, BODY_INNER_H = "SkyyCls", 854 - 38 - 2 * 17        # 782
MIN_CONTRAST = 3.0
EXPECTED_DIFF = {"com/skyy/classes/SkyyClassesPlugin.class", "com/skyy/classes/CfgFn.class", "com/skyy/classes/CfgRows.class",
                 "com/skyy/classes/KitMigrate.class", "com/skyy/classes/ClassCfg.class", "com/skyy/classes/Kit.class",
                 "com/skyy/classes/KitCfg.class", "manifest.json"}    # 0.1.10: exactly these (ClassPage.class is byte-identical)
SCRIPT = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
TWIN = os.path.join(ROOT, "SkyyProfiles", "build_skyyprofiles_0.1.4.py")          # the other script with the SKYY CARD block
PATCHES = [os.path.join(TOOLS, "classes_0_1_9_patch.py"), os.path.join(TOOLS, "profiles_0_1_4_patch.py")]   # the two that define the block
PATCH_NEW = os.path.join(TOOLS, "classes_0_1_10_patch.py")      # 0.1.10 keeps the block (asserts its CARD_SHA, never redefines it)
CARD_H_NEW = 92                                                                   # 0.1.9: the shared card height (0.1.8: 84)
CLOSE_EVENT = ["Activating", "#SkyyClsClose", '{"a": "clsclose"}', True]           # 0.1.9: the new last binding of every state
LOCK_TEXT = "Your class is locked to this profile - a new class means a new profile."
Y_STATES = [
    # (name, class in the class file or None, pending class name or index, info, profile: None | "needs" | (id, class, name),
    #  purse (coins bridge) or None, ENABLED overrides {class name: bool})
    ("no class", None, -1, "", None, None, {}),
    ("warrior", "Warrior", -1, "", None, None, {}),
    ("warrior mage pending coins", "Warrior", "Mage", "", None, 12345, {}),
    ("no class archer pending", None, "Archer", "", None, None, {}),
    ("priest info", "Priest", -1, "You can switch class again in 42 min.", None, 900, {}),
    ("profile berserker", None, -1, "", ("2", "Berserker", "Skyy's Main"), None, {}),
    ("profile assassin", None, -1, "", ("3", "Assassin", ""), None, {}),
    ("needs profile", None, -1, "Create your profile with /profiles - you pick your class there.", "needs", None, {}),
    ("all enabled shaman", "Shaman", "Warrior", "", None, 50, {"Assassin": True, "Shaman": True}),
    ("warrior disabled", "Warrior", -1, "", None, None, {"Warrior": False}),
    ("pending out of range", "Mage", 99, "", None, None, {}),
    ("berserker priest pending", "Berserker", "Priest", "Switching costs 5000 coins - you have 12.", None, 12, {}),
    ("profile priest info", None, "Mage", "Your class is locked to this profile - a new class means a new profile.",
     ("1", "Priest", "Abcdefghijklmnopqrstuvwxyzabcdef"), 5, {}),
    # 0.1.9: the result line in the footer slot at its longest, a huge purse in the footer text, a classless player's result line
    ("warrior long info", "Warrior", -1, "Switching costs 5000 coins but SkyyCoins is not loaded - ask an admin. You can switch class "
                                         "again in 59 min 59 s.", None, 9223372036854775807, {}),
    ("huge purse", "Mage", -1, "", None, 9223372036854775807, {}),
    ("no class info", None, -1, "Assassins are coming soon.", None, 0, {}),
]


def _jvm_start(jars, extra_cp=()):
    import jpype
    import skyybuild as B
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR] + list(jars) + list(extra_cp), convertStrings=True)
    return B


def run_states(jar, out, tag):
    from jpype import JClass, JImplements, JOverride
    _jvm_start([jar])
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    loaded, load_fails = 0, []
    for n in names:
        try:
            Cls.forName(n, True, loader)
            loaded += 1
        except Exception as e:
            load_fails.append("%s: %s" % (n, e))
    res = {"jar": jar, "classes": len(names), "loaded": loaded, "load_fails": load_fails, "states": {}}
    if load_fails:
        json.dump(res, open(out, "w"), indent=1)
        return
    Page, Store, Cfg, Defs = JClass(PKG + "ClassPage"), JClass(PKG + "ClassStore"), JClass(PKG + "ClassCfg"), JClass(PKG + "ClassDefs")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UUID, Paths, Long, Boolean = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def setf(obj, cls, name, val):
        f = cls.class_.getDeclaredField(name)
        f.setAccessible(True)
        f.set(obj, val)

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        def __init__(self, key):
            self.key = key

        @JOverride
        def apply(self, o):
            return self.key

    @JImplements("java.util.function.Function")
    class Purse(object):
        def __init__(self, n):
            self.n = n

        @JOverride
        def apply(self, o):
            return Long(self.n) if not hasattr(o, "__len__") else Boolean.TRUE

    pdir = os.path.join(SCRATCH, "ystates-" + tag, "players")
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = Paths.get(pdir)
    bridge = Cfg.bridge()
    me = UUID(0xc1a55, 18)
    pr = U.allocateInstance(PRef.class_)
    setf(pr, PRef, "uuid", me)
    setf(pr, PRef, "username", "Skyy")
    enabled0 = [bool(x) for x in Defs.ENABLED]
    names_ = [str(x) for x in Defs.NAMES]
    for (name, fcls, pend, info, prof, purse, en) in Y_STATES:
        for k in list(bridge.keySet()):
            if str(k).startswith("profile") or str(k).startswith("coins:") or str(k).startswith("class:"):
                bridge.remove(k)
        for m in (Store.DATA, Store.CLS, Store.FAILAT, Store.KITQ):
            m.clear()
        for fn in os.listdir(pdir):
            os.remove(os.path.join(pdir, fn))
        for i, v in enumerate(enabled0):
            Defs.ENABLED[i] = v
        for cname, v in en.items():
            Defs.ENABLED[names_.index(cname)] = v
        key = str(me)
        if prof == "needs":
            bridge.put("profile:fn:key", KeyFn(key))
        elif prof is not None:
            pid, pcls, pname = prof
            key = str(me) + ("" if pid == "1" else "-p" + pid)
            bridge.put("profile:fn:key", KeyFn(key))
            bridge.put("profile:" + str(me), pid)
            bridge.put("profile:class:" + str(me), pcls)
            if pname:
                bridge.put("profile:name:" + str(me), pname)
        if purse is not None:
            bridge.put("coins:fn:get", Purse(purse))
            bridge.put("coins:fn:take", Purse(purse))
        if fcls:
            open(os.path.join(pdir, key + ".properties"), "w").write("class=%s\n" % fcls)
        page = Page(pr)
        page.pending = names_.index(pend) if isinstance(pend, str) else pend
        page.info = info
        b, ev = UCB(), UEB()
        try:
            page.build(None, b, ev, None)
            err = None
        except Exception as e:
            err = str(e)
        cmds = [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]
        evs = [[str(e.type.name()), None if e.selector is None else str(e.selector), None if e.data is None else str(e.data),
                bool(e.locksInterface)] for e in ev.getEvents()]
        # the handler: a=clsclose (0.1.9: the Close branch, before the profile gates - the page state stays; 0.1.8: the gates answer
        # it like any other click). close() itself needs a live PageManager (it fails quietly inside handleDataEvent's try here).
        info0, pend0 = str(page.info), int(page.pending)
        try:
            page.handleDataEvent(None, None, '{"a":"clsclose"}')
            herr = None
        except Exception as e:
            herr = str(e)
        res["states"][name] = {"error": err, "commands": cmds, "events": evs,
                               "close": {"error": herr, "info_before": info0, "pending_before": pend0, "info": str(page.info),
                                         "pending": int(page.pending)}}
    for i, v in enumerate(enabled0):
        Defs.ENABLED[i] = v
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ child: bytecode method compare (javassist)
def run_bytecode(old, new, out):
    import skyybuild as B
    from jpype import JClass
    _jvm_start([], [B.JAVASSIST])
    ClassPool, BAIS = JClass("javassist.ClassPool"), JClass("java.io.ByteArrayInputStream")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def listing(pool, data):
        cc = pool.makeClass(BAIS(data))
        ms = {}
        behaviors = list(cc.getDeclaredBehaviors())
        if cc.getClassInitializer() is not None:
            behaviors.append(cc.getClassInitializer())
        for mm in behaviors:
            key = "%s%s" % (mm.getName(), mm.getSignature())
            if mm.getMethodInfo().getCodeAttribute() is None:
                ms[key] = ""
                continue
            it = mm.getMethodInfo().getCodeAttribute().iterator()
            cpool = mm.getMethodInfo().getConstPool()
            lines = []
            while it.hasNext():
                ln = str(IP.instructionString(it, it.next(), cpool))
                ln = re.sub(r"#\d+ = ", "", ln).replace("ldc_w ", "ldc ")
                ln = re.sub(r"^(if\w*|goto|goto_w|jsr)\s+\d+", r"\1 N", ln)
                lines.append(ln)
            ms[key] = "\n".join(lines)
        fields = sorted("%s %s" % (f.getName(), f.getSignature()) for f in list(cc.getDeclaredFields()))
        consts = {}
        for f in list(cc.getDeclaredFields()):
            ca = f.getFieldInfo().getConstantValue()
            if ca:
                consts[str(f.getName())] = str(cc.getClassFile().getConstPool().getLdcValue(ca))
        return ms, fields, consts

    zo, zn = zipfile.ZipFile(old), zipfile.ZipFile(new)
    res = {}
    for n in sorted(set(zo.namelist()) & set(zn.namelist())):
        if not n.endswith(".class"):
            continue
        a, b = zo.read(n), zn.read(n)
        if a == b:
            continue
        mo, fo, co = listing(ClassPool(False), a)
        mn, fn, cn = listing(ClassPool(False), b)
        changed = sorted(k for k in set(mo) & set(mn) if mo[k] != mn[k])
        consts = dict((k, [co.get(k), cn.get(k)]) for k in set(co) | set(cn) if co.get(k) != cn.get(k))
        for k in mn:
            if n == "com/skyy/classes/ClassPage.class" and k.startswith("handleDataEvent("):
                res["_handleDataEvent"] = mn[k]
        res[n] = {"changed": changed, "gone": sorted(set(mo) - set(mn)), "new": sorted(set(mn) - set(mo)), "fields_same": fo == fn,
                  "consts": consts, "fields_new": sorted(set(fn) - set(fo)), "fields_gone": sorted(set(fo) - set(fn)),
                  "listings": dict((k, [mo[k], mn[k]]) for k in changed if len(mo[k]) + len(mn[k]) < 400000),
                  "version_only": all(mo[k].replace(OLD_VERSION, "V") == mn[k].replace(VERSION, "V") for k in changed)
                  and all((x or "").replace(OLD_VERSION, "V") == (y or "").replace(VERSION, "V") for x, y in consts.values())}
    json.dump(res, open(out, "w"), indent=1)


# ============================================================================================ parent: markup model (the same code as
# SkyyProfiles/test_skyyprofiles_0.1.3.py - the SKYY CARD component is one component in both mods)
def js(v):
    """The Java string a Set command carries (its data is JSON); non-strings come back as their JSON text."""
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:      # UICommandBuilder.set(String, String) sends {"0": value}
        x = x["0"]
    return x if isinstance(x, str) else v


_OPEN = re.compile(r"([A-Z][A-Za-z]*)(?:\s+#([A-Za-z0-9]+))?\s*\{")
_PROP = re.compile(r"([A-Za-z]+)\s*:")
_ID_RE = re.compile(r"(?:^|[;{}])\s*[A-Z][A-Za-z]*\s+#([A-Za-z0-9]+)\s*\{")
_TEXT_RE = re.compile(r'\bText: "((?:[^"\\]|\\.)*)"')
_COL_RE = re.compile(r"(?:Background|TextColor|Color):\s*(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?(?:\(\s*[0-9.]+\s*\))?)")


def parse_markup(mk):
    """The element tree of one inline markup: [{"type", "id", "props": {name: raw value}, "kids": [...]}] (quotes respected)."""
    pos, n = [0], len(mk)

    def ws():
        while pos[0] < n and mk[pos[0]] in " \t\r\n":
            pos[0] += 1

    def value():
        start, depth = pos[0], 0
        while pos[0] < n:
            c = mk[pos[0]]
            if c == '"':
                pos[0] += 1
                while mk[pos[0]] != '"':
                    pos[0] += 2 if mk[pos[0]] == "\\" else 1
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == ";" and depth == 0:
                v = mk[start:pos[0]].strip()
                pos[0] += 1
                return v
            pos[0] += 1
        raise ValueError("property without ';': %s" % mk[start:start + 60])

    def elem():
        m = _OPEN.match(mk, pos[0])
        if not m:
            raise ValueError("no element at: %s" % mk[pos[0]:pos[0] + 60])
        node = {"type": m.group(1), "id": m.group(2), "props": {}, "kids": []}
        pos[0] = m.end()
        while True:
            ws()
            if pos[0] >= n:
                raise ValueError("unclosed element %s" % node["type"])
            if mk[pos[0]] == "}":
                pos[0] += 1
                return node
            if _OPEN.match(mk, pos[0]):
                node["kids"].append(elem())
                continue
            m2 = _PROP.match(mk, pos[0])
            if not m2:
                raise ValueError("unexpected markup at: %s" % mk[pos[0]:pos[0] + 60])
            pos[0] = m2.end()
            node["props"][m2.group(1)] = value()

    out = []
    while True:
        ws()
        if pos[0] >= n:
            return out
        out.append(elem())


def _pairs(v):
    """'(Width: 10, Top: -3)' -> {"Width": 10, "Top": -3}"""
    out = {}
    if not v:
        return out
    inner = v.strip()
    if inner.startswith("(") and inner.endswith(")"):
        inner = inner[1:-1]
    for part in inner.split(","):
        if ":" in part:
            k, x = part.split(":", 1)
            try:
                out[k.strip()] = int(x.strip())
            except ValueError:
                pass
    return out


def _box4(d, h_key="Horizontal", v_key="Vertical"):
    """Left / Right / Top / Bottom of an Anchor or Padding dict (Full / Horizontal / Vertical expanded; None where unset)."""
    f = d.get("Full")
    hz, vt = d.get(h_key, f), d.get(v_key, f)
    return (d.get("Left", hz), d.get("Right", hz), d.get("Top", vt), d.get("Bottom", vt))


def build_tree(appends):
    """One tree of every (parent, markup) append of a page: returns (root node, {id: node})."""
    ids, root = {}, None
    for parent, mk in appends:
        nodes = parse_markup(mk)
        for nd in nodes:
            stack = [nd]
            while stack:
                x = stack.pop()
                if x["id"]:
                    ids[x["id"]] = x
                stack.extend(x["kids"])
        if parent is None:
            root = nodes[0]
        else:
            ids[parent]["kids"].extend(nodes)
    return root, ids


def layout(root, issues):
    """Place every element (LayoutMode Top / Left / none, Anchor margins, Width / Height, Padding, Full). Records every child that
    leaves its parent's content box in issues (decorations with a negative anchor - the gold ornaments - are skipped). Each node
    gets "box" (x, y, w, h) and "inner" (its content box); returns the node list in placement order."""
    order = []
    a0 = _pairs(root["props"].get("Anchor"))
    todo = [(root, 0, 0, a0.get("Width", 0), a0.get("Height", 0), "root")]
    while todo:
        nd, x, y, w, h, path = todo.pop(0)
        nd["box"] = (x, y, w, h)
        order.append(nd)
        pl, pr_, pt, pb = (v or 0 for v in _box4(_pairs(nd["props"].get("Padding"))))
        ix, iy, iw, ih = x + pl, y + pt, w - pl - pr_, h - pt - pb
        nd["inner"] = (ix, iy, iw, ih)
        mode = nd["props"].get("LayoutMode")
        cur = 0
        name = nd["id"] or nd["type"]
        for k in nd["kids"]:
            a = _pairs(k["props"].get("Anchor"))
            l, r, t, bt = _box4(a)
            kid = "%s>%s" % (path, k["id"] or k["type"])
            if any(v is not None and v < 0 for v in (l, r, t, bt)):
                continue                                     # a decoration (ornament) placed outside on purpose
            if a.get("Full") is not None and mode is None:
                f = a["Full"]
                todo.append((k, ix + f, iy + f, iw - 2 * f, ih - 2 * f, kid))
                continue
            if mode == "Top":
                kw = a.get("Width", iw - (l or 0) - (r or 0))
                kh = a.get("Height")
                if kh is None:
                    kh = ih - cur - (t or 0) - (bt or 0)
                cur += t or 0
                ky, kx = iy + cur, ix + (l or 0)
                cur += kh + (bt or 0)
                if cur > ih:
                    issues.append("%s: children of #%s need %d px of %d (LayoutMode Top)" % (kid, name, cur, ih))
                if (l or 0) + kw + (r or 0) > iw:
                    issues.append("%s: %d px wide in #%s's %d" % (kid, (l or 0) + kw + (r or 0), name, iw))
            elif mode == "Left":
                kh = a.get("Height", ih - (t or 0) - (bt or 0))
                kw = a.get("Width")
                if kw is None:
                    kw = iw - cur - (l or 0) - (r or 0)
                cur += l or 0
                kx, ky = ix + cur, iy + (t or 0)
                cur += kw + (r or 0)
                if cur > iw:
                    issues.append("%s: children of #%s need %d px of %d (LayoutMode Left)" % (kid, name, cur, iw))
                if (t or 0) + kh + (bt or 0) > ih:
                    issues.append("%s: %d px high in #%s's %d" % (kid, (t or 0) + kh + (bt or 0), name, ih))
            else:
                kw, kh = a.get("Width"), a.get("Height")
                if kw is None:
                    kw, kx = iw - (l or 0) - (r or 0), ix + (l or 0)
                else:
                    kx = ix + (l if l is not None else (iw - r - kw if r is not None else (iw - kw) // 2))
                if kh is None:
                    kh, ky = ih - (t or 0) - (bt or 0), iy + (t or 0)
                else:
                    ky = iy + (t if t is not None else (ih - bt - kh if bt is not None else (ih - kh) // 2))
                if kx < ix or ky < iy or kx + kw > ix + iw or ky + kh > iy + ih:
                    issues.append("%s: box %s outside #%s's content box %s" % (kid, (kx, ky, kw, kh), name, (ix, iy, iw, ih)))
            todo.append((k, kx, ky, kw, kh, kid))
        nd["used"] = cur
    return order


def body_fill(ids, body_id):
    """px the LayoutMode Top children of the body take (margins included), and the body's content height."""
    nd = ids[body_id]
    tot = 0
    for k in nd["kids"]:
        a = _pairs(k["props"].get("Anchor"))
        _l, _r, t, bt = _box4(a)
        tot += (t or 0) + a.get("Height", 0) + (bt or 0)
    return tot, nd["inner"][3]


# ---------------------------------------------------------------------------- text (the client's own Nunito Sans glyph advances)
def font_table(bold, secondary=False):
    """({codepoint: advance (em)}, line height (em)) of the client's glyph JSON through the kit (SUI.font_table, read-only); None
    when the client folder is absent."""
    import skyyui as SUI
    return SUI.font_table("Secondary" if secondary else "Default", bold)


def text_w(text, size, bold, upper, secondary=False):
    """The px width of one line - the kit's own measure (SUI.text_width: the client's Nunito Sans / Lexend advances)."""
    import skyyui as SUI
    if font_table(bold, secondary) is None:
        return None
    return SUI.text_width(text, size, bold=bold, font="Secondary" if secondary else "Default", upper=upper)


def wrap_lines(text, width, size, bold, upper):
    """Greedy word wrap at spaces: the number of lines and the widest line (px)."""
    words = text.split(" ")
    lines, cur = [], ""
    for wd in words:
        cand = wd if not cur else cur + " " + wd
        if text_w(cand, size, bold, upper) <= width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    return len(lines), max(text_w(x, size, bold, upper) for x in lines)


def _style(props):
    st = props.get("Style", "")
    fs = re.search(r"FontSize: (\d+)", st)
    col = re.search(r"TextColor: (#[0-9A-Fa-f]{6,8}(?:\([0-9.]+\))?)", st)
    return {"size": int(fs.group(1)) if fs else 16, "bold": "RenderBold: true" in st, "upper": "RenderUppercase: true" in st,
            "wrap": "Wrap: true" in st, "secondary": 'FontName: "Secondary"' in st, "color": col.group(1) if col else None}


def check_texts(name, order, sets, counts):
    """Every label's text fits: one line in its content width; wrapped text in its content height (lines x 1.364 em <= h + 0.1 em);
    a single line needs size + 4 px of height. Buttons: the label fits at the ShrinkTextToFit floor (12 px)."""
    if font_table(False) is None:
        counts["text_skipped"] = True
        return
    for nd in order:
        if nd["type"] == "Label":
            st = _style(nd["props"])
            txt = sets.get(nd["id"]) if nd["id"] and nd["id"] in sets else None
            if txt is None:
                m = re.match(r'"((?:[^"\\]|\\.)*)"', nd["props"].get("Text", '""'))
                txt = m.group(1) if m else ""
            if not txt:
                continue
            _x, _y, w, h = nd["inner"]
            lh = font_table(st["bold"], st["secondary"])[1]
            if st["wrap"]:
                nl, widest = wrap_lines(txt, w, st["size"], st["bold"], st["upper"])
                need = nl * lh * st["size"]
                ok = need <= h + 0.1 * st["size"] and widest <= w
                check(ok, "%s: #%s %d lines need %.1f px of %d (%r)" % (name, nd["id"], nl, need, h, txt))
                counts["wrapped"] += 1
                counts["max_lines_fill"] = max(counts["max_lines_fill"], need / float(h))
            else:
                tw = text_w(txt, st["size"], st["bold"], st["upper"], st["secondary"])
                check(tw <= w, "%s: #%s text %.0f px in %d px (%r)" % (name, nd["id"] or "label", tw, w, txt))
                check(st["size"] + 4 <= h, "%s: #%s a %d px line in %d px" % (name, nd["id"], st["size"], h))
                counts["lines"] += 1
                counts["max_line_fill"] = max(counts["max_line_fill"], tw / float(w))
                if tw / float(w) >= counts["widest"][0]:
                    counts["widest"] = (tw / float(w), "%s #%s %.0f/%d px" % (name, nd["id"], tw, w))
        elif nd["type"] == "TextButton":
            m = re.match(r'"((?:[^"\\]|\\.)*)"', nd["props"].get("Text", '""'))
            txt = m.group(1) if m else ""
            if not txt:
                continue
            _x, _y, w, _h = nd["inner"]
            at17 = text_w(txt, 17, True, True)
            at12 = text_w(txt, 12, True, True)
            check(at12 <= w, "%s: button #%s %r does not fit even at 12 px (%.0f of %d)" % (name, nd["id"], txt, at12, w))
            counts["buttons"] += 1
            if at17 > w:
                counts["shrunk"].add("%s (%.0f/%d)" % (txt, at17, w))


# ---------------------------------------------------------------------------- contrast (WCAG ratio on the effective background)
_PATCH_CENTRE = [None]


def patch_centre():
    """The centre pixel of Common/ContainerPatch.png from Assets.zip (read-only; a tiny PNG decoder: 8-bit RGB / RGBA, no interlace)."""
    if _PATCH_CENTRE[0] is not None:
        return _PATCH_CENTRE[0]
    import skyyui as SUI
    z = zipfile.ZipFile(SUI.ASSETS_ZIP)
    path = SUI._zip_path(SUI.TEX["patch"])
    data = z.read(path if path in z.namelist() else path[:-4] + "@2x.png")          # the client picks the @2x file when only it exists
    pos, idat, w = 8, b"", None
    while pos < len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype, _c, _f, inter = struct.unpack(">IIBBBBB", body)
            assert depth == 8 and ctype in (2, 6) and inter == 0, (depth, ctype, inter)
            bpp = 4 if ctype == 6 else 3
        elif typ == b"IDAT":
            idat += body
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * bpp
    rows, prev, i = [], bytearray(stride), 0
    for _y in range(h):
        f, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b_, c = prev[x], (prev[x - bpp] if x >= bpp else 0)
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b_) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b_) // 2) & 255
            elif f == 4:
                pp = a + b_ - c
                pa, pb, pc = abs(pp - a), abs(pp - b_), abs(pp - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else (b_ if pb <= pc else c))) & 255
        rows.append(line)
        prev = line
    px = rows[h // 2][(w // 2) * bpp:(w // 2) * bpp + 3]
    _PATCH_CENTRE[0] = (px[0], px[1], px[2])
    return _PATCH_CENTRE[0]


def _rgba(c):
    m = re.fullmatch(r"#([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?(?:\(\s*([0-9.]+)\s*\))?", c.strip())
    hx = m.group(1)
    a = float(m.group(3)) if m.group(3) else (int(m.group(2), 16) / 255.0 if m.group(2) else 1.0)
    return int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16), a


def _over(top, base):
    r, g, b, a = top
    return tuple(a * c + (1 - a) * d for c, d in zip((r, g, b), base))


def _lum(rgb):
    def ch(v):
        v = v / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    a, b = _lum(fg), _lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def check_contrast(name, root, counts):
    """Every non-button label: its TextColor on the effective background (ContainerPatch centre under the body, then every colour
    Background above it, alpha-composited) is >= MIN_CONTRAST. The title bar (a texture) and buttons are skipped."""
    import skyyui as SUI
    stack = [(root, None)]
    while stack:
        nd, bg = stack.pop()
        b = nd["props"].get("Background", "")
        if SUI.TEX["patch"] in b:
            bg = patch_centre()
        elif b.startswith("#") and bg is not None:
            bg = _over(_rgba(b), bg)
        elif b and not b.startswith("#"):
            bg = None                                   # another texture (the title bar, a button): not measured
        if nd["type"] == "Label" and bg is not None:
            col = _style(nd["props"])["color"]
            if col:
                r = contrast(_over(_rgba(col), bg), bg)
                check(r >= MIN_CONTRAST, "%s: #%s colour %s on %s = %.2f:1 (< %.1f)" % (
                    name, nd["id"] or "label", col, "#%02x%02x%02x" % tuple(int(round(v)) for v in bg), r, MIN_CONTRAST))
                counts["contrasts"] += 1
                if r < counts["min_contrast"][0]:
                    counts["min_contrast"] = (r, "%s #%s %s" % (name, nd["id"] or "label", col))
        if nd["type"] != "TextButton":
            stack.extend((k, bg) for k in nd["kids"])


# ---------------------------------------------------------------------------- per state
def ids_of(state):
    out = []
    for t, sel, data, text in state["commands"]:
        if t == "AppendInline" and text:
            out += _ID_RE.findall(text)
    return out


def sel_parent(state, ident):
    """The parent selector of the append that creates #ident."""
    for t, sel, data, text in state["commands"]:
        if t == "AppendInline" and text and re.search(r"%s\s*\{" % re.escape(ident), text):
            return sel
    return None


def sets_of(state):
    return dict((sel.lstrip("#")[:-len(".Text")], js(data)) for t, sel, data, text in state["commands"]
                if t == "Set" and sel and sel.endswith(".Text"))


def texts_of(state):
    """Every visible text of a state: inline Text values + b.set .Text values (non-empty)."""
    inl = [x for t, sel, data, text in state["commands"] if t == "AppendInline" and text for x in _TEXT_RE.findall(text) if x]
    return set(inl) | set(v for v in sets_of(state).values() if v)


def compare_state(name, old, new, SUI, counts, data_colors, page_w, page_h, body_id, body_h, expect=None):
    """expect (0.1.9): {"events_added": bindings appended after the old ones, "ids_ok": old ids that may be gone, "text_ok": a predicate
    for old texts that may be gone}; returns (root, ids, sets) of the new page for extra checks (None when it did not build)."""
    ex = expect or {}
    check(old["error"] is None and new["error"] is None, "%s: the page built in both jars (%s / %s)" % (name, old["error"], new["error"]))
    if old["error"] or new["error"]:
        return None
    # C1 bindings: the old ones in their order + the expected new ones after them
    want = old["events"] + list(ex.get("events_added", []))
    check(new["events"] == want, "%s: event bindings = the old %d + %d new (%s)" % (name, len(old["events"]),
                                                                                  len(ex.get("events_added", [])), new["events"][len(old["events"]):]))
    counts["bindings"] += len(new["events"])
    # C2 ids
    oi, ni = ids_of(old), ids_of(new)
    miss = sorted(set(oi) - set(ni) - set(ex.get("ids_ok", ())))
    check(not miss, "%s: no old id missing: %s" % (name, miss))
    counts["ids"] += len(set(oi))
    # C3 texts
    ot, nt = texts_of(old), texts_of(new)
    ok = ex.get("text_ok") or (lambda t: False)
    lost = sorted((t for t in ot - nt if not ok(t)), key=str)
    check(not lost, "%s: old texts no longer shown: %s" % (name, lost))
    counts["texts"] += len(ot)
    # D markup as the client gets it
    ap = SUI.Appends()
    allowed = SUI.allowed_colors() | set(SUI.norm_color(c) for c in data_colors)
    size = 0
    for idx, (t, sel, data, text) in enumerate(new["commands"]):
        if t == "AppendInline":
            parent = None if sel is None else sel.lstrip("#")
            check(idx != 0 or parent is None, "%s: the first append is the page root" % name)
            try:
                SUI.check_markup(text, prefix=PREFIX_OF[0], root=(parent is None))
            except ValueError as e:
                check(False, "%s: check_markup: %s" % (name, e))
            ap.append((parent, text))
            size += len(text)
            for c in _COL_RE.findall(text):
                check(SUI.norm_color(c) in allowed, "%s: colour %s is a kit / data colour" % (name, c))
                counts["colours"] += 1
            for bad in ("Width: 0,", "Width: 0)", "FlexWeight", "WrapMaxLines", "LetterSpacing", "LayoutMode: Right", "LayoutMode: Center",
                        "LayoutMode: Full", "ItemGrid"):
                check(bad not in text, "%s: no %s in %s" % (name, bad.strip(",)"), text[:80]))
        elif t == "Set":
            ident, prop = sel.lstrip("#").rsplit(".", 1)
            ap.sets.append((ident, prop, js(data)))
            size += len(data or "")
    counts["max_payload"] = max(counts["max_payload"], size)
    try:
        SUI.check_page(ap, PREFIX_OF[0])
        counts["check_page"] += 1
    except ValueError as e:
        check(False, "%s: check_page: %s" % (name, e))
    counts["appends"] += len(ap)
    root, ids = build_tree(ap)
    a0 = _pairs(root["props"].get("Anchor"))
    check((a0.get("Width"), a0.get("Height")) == (page_w, page_h), "%s: page root %s x %s (want %d x %d)" % (
        name, a0.get("Width"), a0.get("Height"), page_w, page_h))
    for e in new["events"]:
        check(e[1] and e[1].lstrip("#") in ids, "%s: binding target %s exists" % (name, e[1]))
    issues = []
    order = layout(root, issues)
    check(not issues, "%s: layout: %s" % (name, issues[:4]))
    counts["placed"] += len(order)
    tot, inner = body_fill(ids, body_id)
    check(inner == body_h and tot == body_h, "%s: the body children fill %d px exactly (got %d of %d)" % (name, body_h, tot, inner))
    for nd in order:                                  # the Left rows: record the tightest one
        if nd["props"].get("LayoutMode") == "Left" and nd["kids"]:
            counts["min_row_slack"] = min(counts["min_row_slack"], nd["inner"][2] - nd["used"])
    check_texts(name, order, dict((i, v) for i, p, v in ap.sets if p == "Text"), counts)
    check_contrast(name, root, counts)
    counts["states"] += 1
    return root, ids, dict((i, v) for i, p, v in ap.sets if p == "Text")


PREFIX_OF = [PREFIX]


def new_counts():
    return dict(states=0, bindings=0, ids=0, texts=0, colours=0, check_page=0, appends=0, placed=0, min_row_slack=10 ** 6, wrapped=0,
                lines=0, buttons=0, max_lines_fill=0.0, max_line_fill=0.0, widest=(0.0, ""), shrunk=set(), text_skipped=False,
                contrasts=0, min_contrast=(99.0, ""), max_payload=0)


def report_counts(counts):
    print("B-D. %(states)d states: %(bindings)d bindings as expected, %(ids)d old ids kept, %(texts)d old texts shown (expected changes aside); "
          "%(check_page)d check_page / %(appends)d appends through check_markup, %(colours)d colours audited, %(placed)d elements placed "
          "by the layout model (tightest Left row slack %(min_row_slack)d px), largest payload %(max_payload)d chars" % counts)
    if counts["text_skipped"]:
        print("   text widths: SKIPPED (no client glyph tables)")
    else:
        print("   text: %d single lines (widest %.0f%%: %s), %d wrapped labels (fullest %.0f%% of their height), %d buttons%s" % (
            counts["lines"], 100 * counts["widest"][0], counts["widest"][1], counts["wrapped"], 100 * counts["max_lines_fill"],
            counts["buttons"], (" (shrink-to-fit at 17 px: %s)" % ", ".join(sorted(counts["shrunk"]))) if counts["shrunk"] else ""))
    print("   contrast: %d labels, lowest %.2f:1 (%s), ContainerPatch centre #%02x%02x%02x" % (
        counts["contrasts"], counts["min_contrast"][0], counts["min_contrast"][1], *patch_centre()))


# ---------------------------------------------------------------------------- E: the SKYY CARD block on its own
def card_block(path):
    src = open(path, encoding="utf8").read().replace("\r\n", "\n")
    a = src.index("# =====================================================================================================================\n# SKYY CARD")
    b = src.index("# ======================================================================= (end of the shared SKYY CARD block)")
    return src[a:b + len("# ======================================================================= (end of the shared SKYY CARD block)")]


def patch_card(path):
    s = open(path, encoding="utf8").read()
    a = s.index("CARD_BLOCK = r'''") + len("CARD_BLOCK = r'''")
    sha = re.search(r'^CARD_SHA = "([0-9a-f]{64})"', s, re.M).group(1)
    return s[a:s.index("'''", a)], sha


class _KitRecorder(object):
    """The kit module as the SKYY CARD block sees it, recording every (parent, markup) it hands to java_append."""

    def __init__(self, sui):
        self._sui, self.appends = sui, []

    def __getattr__(self, name):
        return getattr(self._sui, name)

    def java_append(self, parent, markup, b="b", page_root=True):
        self.appends.append((parent, markup))
        return self._sui.java_append(parent, markup, b, page_root)


def check_card_block(SUI, data_colors):
    mine, twin = card_block(SCRIPT), card_block(TWIN)
    check(mine == twin, "E: the SKYY CARD block is byte-identical in %s and %s" % (os.path.basename(SCRIPT), os.path.basename(TWIN)))
    sha = hashlib.sha256(mine.encode("utf8")).hexdigest()
    for p in PATCHES:
        blk, psha = patch_card(p)
        check(blk == mine and psha == sha, "E: %s carries the same block and CARD_SHA (%s)" % (os.path.basename(p), psha[:12]))
    rec = _KitRecorder(SUI)
    ns = {"SUI": rec, "re": re}
    exec(compile(mine, "SKYY CARD", "exec"), ns)
    allowed = SUI.allowed_colors() | set(SUI.norm_color(c) for c in data_colors)
    n = n_mk = 0
    lines = [{"id": "Nm", "text": "safe(t)", "kind": "rowName", "h": 24, "col": SUI.J("col", "#d9443f"),
              "tag": {"id": "Rl", "text": "safe(r)", "col": SUI.J("col", "#d9443f"), "w": 200}},
             {"id": "Sk", "text": "safe(s)", "kind": "fieldLabel", "h": 20, "col": "value"},
             {"id": "Ds", "text": "safe(d)", "kind": "rowSub", "h": 40, "col": "rowSub", "wrap": True}]
    for look in list(ns["CARD_LOOKS"]) + [[("selected", "sel"), ("pending", "pend"), ("normal", "on"), "off"]]:
        for icons, on in ((None, None), ("ic", "on")):
            del rec.appends[:]
            java = ns["card_java"]({"list": PREFIX + "List", "card": PREFIX + "Card" + SUI.J("i", "1"),
                                    "text": PREFIX + "Txt" + SUI.J("i", "1"), "act": PREFIX + "Act" + SUI.J("i", "1")}, 1058, look, lines,
                                   icons=icons,
                                   icon_item=SUI.J("safe(x)", "Weapon_Sword_Crude"), icon_max=3 if icons else 1, on=on)
            check(len(rec.appends) == 12 and java.count("appendInline(") == 12 and java.count(".Text\"") == 4,
                  "E: card_java(%s, %s): 12 appends + 4 b.set texts (got %d / %d)" % (look, icons, len(rec.appends), java.count(".Text\"")))
            for parent, mk in rec.appends:
                try:
                    SUI.check_markup(mk, prefix=PREFIX)
                except ValueError as e:
                    check(False, "E: card markup (%s): %s" % (look, e))
                for v in (mk.variants() if isinstance(mk, SUI.Choice) else [mk]):
                    for c in _COL_RE.findall(SUI.render(v)):
                        check(SUI.norm_color(c) in allowed, "E: card colour %s (%s) is a kit / data colour" % (c, look))
                n_mk += 1
            n += 1
    check(set(ns["CARD_LOOKS"]) == {"selected", "pending", "normal", "off", "empty"}, "E: the five card looks")
    check(ns["CARD_LOOKS"]["selected"] == ("rowPressed", "selected"), "E: the selected look = the row pressed step + the blue bar "
                                                                      "(review fix: contrast)")
    for look, (bg, bar) in ns["CARD_LOOKS"].items():
        check(bg in SUI.COLOR and bar in SUI.COLOR, "E: look %s uses kit colours (%s, %s)" % (look, bg, bar))
    check(ns["CARD_H"] == CARD_H_NEW and ns["card_list_h"](8) == 8 + 8 * (CARD_H_NEW + 4)
          and ns["card_text_w"](1058, 3) == 1058 - 4 - 216 - 200 - 12, "E: card sizes (CARD_H %s)" % ns["CARD_H"])
    print("E. SKYY CARD block: identical in both scripts + both patches (sha %s), %d look x cell variants, %d markups checked"
          % (sha[:12], n, n_mk))


def part_y(env):
    """Part Y in the parent: 0.1.9 vs 0.1.10 - two state children, the bytecode child; the page must be identical, the class bytes
    may differ only where 0.1.10 changed something."""
    me = os.path.abspath(__file__)
    outs = {}
    for tag, j in (("new", JAR), ("old", OLD_JAR)):
        if not os.path.isfile(j):
            check(False, "Y: no jar at %s" % j)
            return
        outs[tag] = os.path.join(SCRATCH, "ystates-%s.json" % tag)
        p = subprocess.run([sys.executable, me, "--states", j, "--out", outs[tag], "--tag", tag, "--dir", SCRATCH], env=env)
        check(p.returncode == 0 and os.path.isfile(outs[tag]), "Y: state child JVM for %s ran" % j)
    bco = os.path.join(SCRATCH, "ybytecode.json")
    p = subprocess.run([sys.executable, me, "--bytecode", OLD_JAR, "--new", JAR, "--out", bco, "--dir", SCRATCH], env=env)
    check(p.returncode == 0 and os.path.isfile(bco), "Y: bytecode child ran")
    if FAILS:
        return
    new, old = json.load(open(outs["new"])), json.load(open(outs["old"]))
    for r in (new, old):
        check(not r["load_fails"] and r["loaded"] == r["classes"], "Y-A: %s: %d / %d classes load under -Xverify:all %s"
              % (os.path.basename(r["jar"]), r["loaded"], r["classes"], r["load_fails"]))
    print("Y-A. -Xverify:all: %s %d / %d, %s %d / %d classes" % (os.path.basename(new["jar"]), new["loaded"], new["classes"],
                                                              os.path.basename(old["jar"]), old["loaded"], old["classes"]))
    import skyyui as SUI
    SUI.verify(quiet=True)
    src = open(SCRIPT, encoding="utf8").read()
    data_colors = eval(re.search(r"^UI_DATA_COLORS = (\[.*?\](?:\s*\+\s*\[.*?\])?)\n", src, re.M | re.S).group(1))
    counts = new_counts()
    extra = {"cards": 0, "close": 0, "slot": 0, "handler": 0, "identical": 0}
    close_mk = SUI.button("SkyyClsClose", "Close", "secondary", w=SUI.BTN_MIN_W, sound="cancel", anchor={"left": 12, "top": 8})
    for st in Y_STATES:
        nm, info = st[0], st[3]
        check(nm in new["states"] and nm in old["states"], "Y-B: state %s built by both jars" % nm)
        if not (nm in new["states"] and nm in old["states"]):
            continue
        ns_, os_ = new["states"][nm], old["states"][nm]
        # 0.1.10 did not touch the page: every command, binding and the handler's answer are 0.1.9's, byte for byte
        check(ns_["commands"] == os_["commands"] and ns_["events"] == os_["events"] and ns_["error"] == os_["error"],
              "Y-B %s: the 0.1.10 page = the 0.1.9 page (commands, bindings)" % nm)
        check(ns_["close"] == os_["close"], "Y-H %s: the a=clsclose handler answers as in 0.1.9 (%s / %s)" % (nm, ns_["close"], os_["close"]))
        extra["identical"] += 1
        got = compare_state(nm, os_, ns_, SUI, counts, data_colors, PAGE_W, PAGE_H, BODY_ID, BODY_INNER_H, None)
        if got is None:
            continue
        root, ids, sets = got
        confirm = any(e[1] == "#SkyyClsYes" for e in ns_["events"])
        # the 0.1.9 page checks still hold for 0.1.10: every class card 92 px high
        cards = [i for i in ids if re.fullmatch(r"SkyyClsCard\d+", i)]
        check(len(cards) == 7 and all(_pairs(ids[c]["props"].get("Anchor")).get("Height") == CARD_H_NEW for c in cards),
              "Y-G %s: 7 class cards %d px high" % (nm, CARD_H_NEW))
        extra["cards"] += len(cards)
        # the Close: the kit's Secondary + cancel sound, the last kid of the footer row, in every state
        mks = [text for t, sel, data, text in ns_["commands"] if t == "AppendInline" and text and "#SkyyClsClose" in text]
        check(mks == [close_mk] and sel_parent(ns_, "#SkyyClsClose") == "#SkyyClsBottom", "Y-G %s: #SkyyClsClose is the kit's "
              "Secondary + cancel button in #SkyyClsBottom (%s)" % (nm, mks))
        check(ns_["events"][-1:] == [CLOSE_EVENT], "Y-G %s: the Close binding is the last one" % nm)
        bottom = ids.get("SkyyClsBottom")
        kids = [k.get("id") for k in bottom["kids"]] if bottom else []
        check(len(kids) == 2 and kids[-1] == "SkyyClsClose", "Y-G %s: the footer row = one slot + Close: %s" % (nm, kids))
        extra["close"] += 1
        want = "SkyyClsConfirm" if confirm else ("SkyyClsInfo" if info else "SkyyClsFoot")
        check(kids[:1] == [want], "Y-G %s: the footer slot shows #%s (got %s)" % (nm, want, kids[:1]))
        extra["slot"] += 1
        cn = ns_["close"]
        check(cn["error"] is None and cn["info"] == cn["info_before"] and cn["pending"] == cn["pending_before"],
              "Y-H %s: a=clsclose leaves the page state alone (the Close branch, before the lock gate): %s" % (nm, cn))
        extra["handler"] += 1
    report_counts(counts)
    print("Y-B/G/H. %(identical)d states identical in 0.1.9 and 0.1.10; still: %(cards)d cards %(h)d px high, the kit Close in the footer "
          "row in %(close)d states, the footer slot right in %(slot)d states, the Close branch first in %(handler)d states" % dict(extra, h=CARD_H_NEW))
    check_card_block(SUI, data_colors)
    _pn = open(PATCH_NEW, encoding="utf8").read()
    _sha_new = re.search(r'^CARD_SHA = "([0-9a-f]{64})"', _pn, re.M).group(1)
    _sha_prof = patch_card(PATCHES[1])[1]
    check(_sha_new == _sha_prof and "CARD_BLOCK = r'''" not in _pn, "E: classes_0_1_10_patch.py asserts SkyyProfiles 0.1.4's CARD_SHA "
          "(%s) and never redefines the block" % _sha_new[:12])
    _p015 = os.path.join(TOOLS, "profiles_0_1_5_patch.py")
    if os.path.isfile(_p015):   # the next SkyyProfiles (in progress elsewhere) - same component, same hash
        _m = re.search(r'^CARD_SHA = "([0-9a-f]{64})"', open(_p015, encoding="utf8").read(), re.M)
        check(_m is not None and _m.group(1) == _sha_new, "E: profiles_0_1_5_patch.py carries the same CARD_SHA")
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    check(sorted(zo.namelist()) == sorted(zn.namelist()), "Y-F: same entries in both jars")
    diff = set(n for n in set(zo.namelist()) & set(zn.namelist()) if zo.read(n) != zn.read(n))
    same = len(set(zo.namelist()) & set(zn.namelist())) - len(diff)
    check(diff == EXPECTED_DIFF, "Y-F: exactly %s differ, got %s" % (sorted(EXPECTED_DIFF), sorted(diff)))
    check("com/skyy/classes/ClassPage.class" not in diff, "Y-F: ClassPage.class is byte-identical (the page did not change)")
    check(not [n for n in zn.namelist() if n.endswith(".ui")], "Y-F: no .ui files in the jar (inline pages only)")
    mo, mn = json.loads(zo.read("manifest.json")), json.loads(zn.read("manifest.json"))
    check(set(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)) <= {"Version", "Name", "Description"} and mn.get("Version") == VERSION
          and "off-hand" in mn.get("Description", ""), "Y-F: manifest: only the version + the description (the off-hand) differ: %s"
          % sorted(k for k in set(mo) | set(mn) if mo.get(k) != mn.get(k)))
    bc = json.load(open(bco))

    def ldiff(cls, meth):
        """(lines only in old, lines only in new) of one changed method, the version strings normalised"""
        lo, ln_ = bc[cls]["listings"][meth]
        a_ = [x.replace(OLD_VERSION, "V") for x in lo.split("\n")]
        b_ = [x.replace(VERSION, "V") for x in ln_.split("\n")]
        import collections
        return list((collections.Counter(a_) - collections.Counter(b_)).elements()), list((collections.Counter(b_) - collections.Counter(a_)).elements())

    sp = bc.get("com/skyy/classes/SkyyClassesPlugin.class", {})
    check(sp.get("changed") == ["setup()V"] and not sp.get("new") and not sp.get("gone") and sp.get("fields_same"),
          "Y-F: SkyyClassesPlugin: only setup() changed: %s" % dict((k, sp.get(k)) for k in ("changed", "new", "gone")))
    if sp.get("changed") == ["setup()V"]:
        o_, n_ = ldiff("com/skyy/classes/SkyyClassesPlugin.class", "setup()V")
        check(not o_ and sorted(n_) == sorted(["invokestatic Method com.skyy.classes.ClassCfg.migrate0110(()Ljava/lang/String;)", "pop"]),
              "Y-F: setup(): the version + ONE added ClassCfg.migrate0110() call (result dropped): -%s +%s" % (o_, n_))
    for k in ("com/skyy/classes/CfgFn.class", "com/skyy/classes/KitMigrate.class"):
        c = bc.get(k, {})
        check(not c.get("new") and not c.get("gone") and c.get("fields_same") and c.get("version_only"),
              "Y-F: %s: only the version string differs: %s" % (k, dict((x, c.get(x)) for x in ("changed", "consts"))))
    kc = bc.get("com/skyy/classes/KitCfg.class", {})
    check(kc.get("changed") == ["<clinit>()V"] and not kc.get("new") and not kc.get("gone") and kc.get("fields_same"), "Y-F: KitCfg: only <clinit> %s" % kc.get("changed"))
    if kc.get("changed") == ["<clinit>()V"]:
        o_, n_ = ldiff("com/skyy/classes/KitCfg.class", "<clinit>()V")
        check(o_ == ['ldc "Weapon_Sword_Crude:1"'] and n_ == ['ldc "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"'],
              "Y-F: KitCfg.<clinit>: only the Warrior kit default (-%s +%s)" % (o_, n_))
    kt = bc.get("com/skyy/classes/Kit.class", {})
    _tg = "(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Ljava/lang/String;[Ljava/lang/String;[I[I"
    check(kt.get("changed") == ["give(Lcom/hypixel/hytale/server/core/universe/PlayerRef;Lcom/hypixel/hytale/server/core/entity/entities/Player;"
                                "Ljava/lang/String;IZLcom/hypixel/hytale/server/core/universe/PlayerRef;)Ljava/lang/String;"]
          and sorted(x.split("(")[0] for x in kt.get("new", [])) == ["givenLine", "offhand", "putKit", "select", "tellGiven"]
          and kt.get("gone") == ["tellGiven" + _tg + ")V"] and [x for x in kt.get("new", []) if x.startswith("tellGiven")] == ["tellGiven" + _tg + "[I)V"]
          and kt.get("fields_new") == ["OFFHAND Ljava/lang/String;"] and not kt.get("fields_gone"),
          "Y-F: Kit: give changed, tellGiven gained the off-hand array, new givenLine / offhand / putKit / select, field OFFHAND: %s"
          % dict((x, kt.get(x)) for x in ("changed", "new", "gone", "fields_new")))
    cc = bc.get("com/skyy/classes/ClassCfg.class", {})
    check(sorted(cc.get("changed", [])) == ["<clinit>()V", "load()Ljava/lang/String;"] and not cc.get("gone")
          and sorted(x.split("(")[0] for x in cc.get("new", [])) == ["mgIdx", "mgKit", "mgLog", "mgSaved", "mgUpdate", "migrate0110"]
          and sorted(x.split(" ")[0] for x in cc.get("fields_new", [])) == ["MG_KEY", "MG_MARK", "MG_MARK_ID", "MG_NEW", "MG_OLD", "MG_WHO", "MG_WHY"]
          and not cc.get("fields_gone"), "Y-F: ClassCfg: <clinit> (default file) + load (the self-heal default) changed, the 6 update methods "
                                         "+ 7 MG_ fields new: %s" % dict((x, cc.get(x)) for x in ("changed", "new", "fields_new")))
    if "load()Ljava/lang/String;" in cc.get("changed", []):
        o_, n_ = ldiff("com/skyy/classes/ClassCfg.class", "load()Ljava/lang/String;")
        check(sorted(o_) == ['ldc "Weapon_Sword_Crude:1"', "ldc2_w long 50"] and sorted(n_) == ['ldc "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"', "ldc2_w long 100"],
              "Y-F: ClassCfg.load: only the two code defaults (kit.Warrior + the Wood Shield, selfPercent 50 -> 100): -%s +%s" % (o_, n_))
    cr = bc.get("com/skyy/classes/CfgRows.class", {})
    check(not cr.get("new") and not cr.get("gone") and cr.get("fields_same") and set(cr.get("changed", [])) <= {"<clinit>()V", "header()[Ljava/lang/Object;"}
          and cr.get("consts") == {"VERSION": [OLD_VERSION, VERSION]}, "Y-F: CfgRows: only <clinit> (the row table, the default file) + the "
          "version: %s %s" % (cr.get("changed"), cr.get("consts")))
    if "header()[Ljava/lang/Object;" in cr.get("changed", []):
        o_, n_ = ldiff("com/skyy/classes/CfgRows.class", "header()[Ljava/lang/Object;")
        check(not o_ and not n_, "Y-F: CfgRows.header: only the version string (-%s +%s)" % (o_, n_))
    if "<clinit>()V" in cr.get("changed", []):
        o_, n_ = ldiff("com/skyy/classes/CfgRows.class", "<clinit>()V")
        # removed: the row's old label / help / default, the old kit.Warrior row default and the old default-file lines; added: the new
        # ones + the 3 new default-file lines (the off-hand comment, the marker, the selfPercent comment = 3 more array stores)
        old_s = sorted(x[4:] for x in o_ if x.startswith("ldc "))
        new_s = sorted(x[4:] for x in n_ if x.startswith("ldc "))
        want_old = sorted(['"Priest heals self"', '"Weapon_Sword_Crude:1"', '"50"',
                           '"The Priest heals this % of what one party member gets. 0 = never heals themself."',
                           '"kit.Warrior=Weapon_Sword_Crude:1"',
                           '"# Numbers locked for now: sharePercent 25, selfPercent 50, radius 16, maxPerHit 10, maxPerSecond 10, party only."',
                           '"priestHeal.selfPercent=50"'])
        want_new = ['"' + SELF_LABEL + '"', '"Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"', '"100"', '"' + SELF_HELP + '"',
                    '"# V (Skyy 2026-10-01): a shield (Weapon_Shield_...) in a kit goes into the off-hand', '"# SkyyClasses V defaults (Skyy 2026-10-01)',
                    '"kit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"', '"# Numbers locked for now: sharePercent 25, selfPercent 100, radius 16',
                    '"# selfPercent = Skyy 2026-10-01: 100 = the Priest heals itself as much as each party member', '"priestHeal.selfPercent=100"']
        other_n = [x for x in n_ if not x.startswith("ldc ")]
        check(len(o_) == len(old_s) and old_s == want_old and len(new_s) == len(want_new)
              and all(any(s_.startswith(w) for s_ in new_s) for w in want_new)
              and set(x.split()[0] for x in other_n) <= {"aastore", "bipush", "dup"} and other_n.count("aastore") == 3,
              "Y-F: CfgRows.<clinit>: only the self-heal row (label / help / default), the kit.Warrior row default and the default file "
              "(2 changed values + 3 new comment lines) changed: -%s +%s" % ([x[:60] for x in o_], [x[:60] for x in n_]))
    print("Y-F. class bytes: %d entries identical, differ: %s; methods: %s" % (
        same, ", ".join(sorted(n.split("/")[-1] for n in diff)),
        "; ".join("%s %s" % (n.split("/")[-1][:-6], dict((x, bc[n][x]) for x in ("changed", "new", "gone", "consts") if bc[n][x]))
                  for n in sorted(bc) if not n.startswith("_"))))


# ============================================================================================================== child: parts Z + M (0.1.10)
LIVE = os.path.abspath(arg("--live", os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Hytale", "UserData", "Saves", "HUD mod",
                                                  "mods", "Skyy_SkyyClasses")))
LIVE_COPY = os.path.join(SCRATCH, "live", "Skyy_SkyyClasses")


def copy_live():
    """Parent: a scratch COPY of the live config folder (config.properties, config-changes.log, config-history/) - the live folder is only
    read (never written: game files + the live world are read-only)."""
    shutil.rmtree(os.path.dirname(LIVE_COPY), ignore_errors=True)
    if not os.path.isfile(os.path.join(LIVE, "config.properties")):
        print("M: no live config at %s - the live-copy checks are skipped (the synthetic ones still run)" % LIVE)
        return
    os.makedirs(LIVE_COPY)
    for f in ("config.properties", "config-changes.log"):
        if os.path.isfile(os.path.join(LIVE, f)):
            shutil.copyfile(os.path.join(LIVE, f), os.path.join(LIVE_COPY, f))
    if os.path.isdir(os.path.join(LIVE, "config-history")):
        shutil.copytree(os.path.join(LIVE, "config-history"), os.path.join(LIVE_COPY, "config-history"))
    print("M: copied the live config (%d bytes) + %d history files from %s" % (
        os.path.getsize(os.path.join(LIVE_COPY, "config.properties")),
        len(os.listdir(os.path.join(LIVE_COPY, "config-history"))) if os.path.isdir(os.path.join(LIVE_COPY, "config-history")) else 0, LIVE))


def defaults_019():
    """The 0.1.9 default config.properties (build_skyyclasses_0.1.9.py's pure-Python table part + CFG_LINES, never run as a build)."""
    src = open(os.path.join(HERE, "build_skyyclasses_0.1.9.py"), encoding="utf8").read()
    a, b = src.index("\nCLASSES = ["), src.index("\nSYNC_STEADY_MS = ")
    ns = {}
    exec(src[a:b], ns)
    m = re.search(r"^CFG_LINES = (.*?)\n(?=F\(cfg, )", src, re.M | re.S)
    return "".join(l + "\n" for l in eval(m.group(1), ns))


def run_z(jar):
    import jpype
    import skyybuild as B
    from jpype import JClass, JArray, JObject, JShort, JByte, JInt, JFloat
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")   # the game's own JRE
    if not os.path.exists(jvm):
        jvm = B._jvm()
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jpype.startJVM(jvm, "-Xverify:all", "-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp,
                   classpath=[B.SERVER_JAR, jar, B.JAVASSIST], convertStrings=True)
    Cls = JClass("java.lang.Class")
    loader = JClass("java.lang.ClassLoader").getSystemClassLoader()
    names = [n[:-6].replace("/", ".") for n in zipfile.ZipFile(jar).namelist() if n.endswith(".class")]
    for n in names:
        try:
            Cls.forName(n, True, loader)
            OKS[0] += 1
        except Exception as e:
            check(False, "Z: load %s: %s" % (n, e))
    if FAILS:
        return
    print("Z. loaded + verified %d classes (-Xverify:all)" % len(names))
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    Mod = JClass("java.lang.reflect.Modifier")

    def jfield(cls, name):
        c = cls.class_ if hasattr(cls, "class_") else cls
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)

    # ---------------- the Item asset map: test items (a bare JVM has no asset store; the SkyyGear harness's fake store + real Item objects)
    Item = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    IU = JClass("com.hypixel.hytale.server.core.asset.type.item.config.ItemUtility")
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(CtC.make("public SkyyTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    astore = us.allocateInstance(fake.toClass(AS.class_))
    dam = DAM()
    jfield(AS, "assetMap").set(astore, dam)
    jfield(Item, "ASSET_STORE").set(None, astore)
    amap = jfield(DAM, "assetMap").get(dam)
    unknown = Item.UNKNOWN

    def mk_item(iid, stack, usable):
        it = us.allocateInstance(Item.class_)
        for f in Item.class_.getDeclaredFields():
            if Mod.isStatic(f.getModifiers()):
                continue
            f.setAccessible(True)
            f.set(it, f.get(unknown))
        u_ = IU()
        jfield(IU, "usable").setBoolean(u_, bool(usable))
        jfield(Item, "id").set(it, iid)
        jfield(Item, "maxStack").setInt(it, int(stack))
        jfield(Item, "utility").set(it, u_)
        amap.put(iid, it)
        return it

    SHIELD, IRON, FAKE, SWORD, TORCH = "Weapon_Shield_Wood", "Weapon_Shield_Iron", "Weapon_Shield_Fake", "Weapon_Sword_Crude", "Furniture_Crude_Torch"
    BOW, ARROW, STICK, WAND = "Weapon_Shortbow_Crude", "Weapon_Arrow_Crude", "Ingredient_Stick", "Weapon_Wand_Wood"
    for iid, st_, usable in ((SHIELD, 1, True), (IRON, 1, True), (FAKE, 1, False), (SWORD, 1, False), (TORCH, 25, True), (BOW, 1, False),
                             (ARROW, 100, False), (STICK, 1, False), (WAND, 1, False)):
        mk_item(iid, st_, usable)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    check(bool(IS(SHIELD, 1).getItem().getUtility().isUsable()) and not bool(IS(SWORD, 1).getItem().getUtility().isUsable())
          and int(IS(TORCH, 1).getItem().getMaxStack()) == 25, "Z: the test items are in the Item asset map (shield usable, sword not)")

    # ---------------- engine containers: hotbar + storage = SimpleItemContainer, the utility = the REAL InventoryComponent$Utility
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    INVC = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent")
    UT = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility")
    UCAP = int(INVC.DEFAULT_UTILITY_CAPACITY)
    INVN = "com.hypixel.hytale.server.core.inventory.Inventory"
    ICN = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"
    UTN = "com.hypixel.hytale.server.core.inventory.InventoryComponent$Utility"
    tinv = jp.makeClass("com.hypixel.hytale.server.core.inventory.SkyyTestInv", jp.get(INVN))
    for f_, t_ in (("h", ICN), ("s", ICN), ("u", UTN)):
        tinv.addField(CtF.make("public %s %s;" % (t_, f_), tinv))
    tinv.addConstructor(CtC.make("public SkyyTestInv(%s h, %s s, %s u) { super(); this.h = h; this.s = s; this.u = u; }" % (ICN, ICN, UTN), tinv))
    for src_ in ("public %s getHotbar() { return this.h; }" % ICN,
                 "public %s getStorage() { return this.s; }" % ICN,
                 "public com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer getCombinedHotbarFirst() { return new "
                 "com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer(new %s[] { this.h, this.s }); }" % ICN,
                 "public %s getUtility() { return this.u.getInventory(); }" % ICN,
                 "public byte getActiveUtilitySlot() { return this.u.getActiveSlot(); }",
                 "public void setActiveUtilitySlot(com.hypixel.hytale.component.Ref r, byte b, com.hypixel.hytale.component.ComponentAccessor a) "
                 "{ this.u.setActiveSlot(b, r, a); }",
                 "public com.hypixel.hytale.server.core.inventory.ItemStack getUtilityItem() { return this.u.getActiveItem(); }"):
        tinv.addMethod(CtM.make(src_, tinv))
    TInv = JClass(tinv.toClass(JClass(INVN).class_))
    # a Store that records every entity event (and can cancel / redirect the active-slot request), a PacketHandler that records packets
    ASREN = "com.hypixel.hytale.server.core.event.events.ecs.InventoryActiveSlotRequestEvent"
    tst = jp.makeClass("com.hypixel.hytale.component.SkyyTestStore", jp.get("com.hypixel.hytale.component.Store"))
    tst.addField(CtF.make("public static java.util.ArrayList EV;", tst))
    tst.addField(CtF.make("public static int MODE;", tst))
    tst.addMethod(CtM.make("public void invoke(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.system.EcsEvent e) { EV.add(e); "
                           "if (e instanceof %s) { %s q = (%s) e; if (MODE == 1) q.setCancelled(true); if (MODE == 2) q.setNewSlot((byte) 3); } }"
                           % (ASREN, ASREN, ASREN), tst))
    TStore = JClass(tst.toClass(JClass("com.hypixel.hytale.component.Store").class_))
    tph = jp.makeClass("com.hypixel.hytale.server.core.io.SkyyTestPH", jp.get("com.hypixel.hytale.server.core.io.PacketHandler"))
    tph.addField(CtF.make("public static java.util.ArrayList OUT;", tph))
    tph.addMethod(CtM.make("public void writeNoCache(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
    tph.addMethod(CtM.make("public void write(com.hypixel.hytale.protocol.ToClientPacket p) { OUT.add(p); }", tph))
    TPH = JClass(tph.toClass(JClass("com.hypixel.hytale.server.core.io.PacketHandler").class_))
    ArrayList, UUID, Paths = JClass("java.util.ArrayList"), JClass("java.util.UUID"), JClass("java.nio.file.Paths")
    TStore.EV = ArrayList()
    TPH.OUT = ArrayList()
    REF, PRN, PLA = JClass("com.hypixel.hytale.component.Ref"), JClass("com.hypixel.hytale.server.core.universe.PlayerRef"), \
        JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    SAS = JClass("com.hypixel.hytale.protocol.packets.inventory.SetActiveSlot")
    SET_EV = JClass("com.hypixel.hytale.server.core.event.events.ecs.InventorySetActiveSlotEvent")
    ASRE = JClass(ASREN)
    SMSG = JClass("com.hypixel.hytale.protocol.packets.interface_.ServerMessage")
    J = lambda n: JClass(PKG + n)
    Kit, Store, KitCfg, Defs, Cfg, HT = J("Kit"), J("ClassStore"), J("KitCfg"), J("ClassDefs"), J("ClassCfg"), J("HealTask")
    pdir = os.path.join(SCRATCH, "z", "players")
    os.makedirs(pdir, exist_ok=True)
    Store.DIR = Paths.get(pdir)
    WAR, ARC = [str(x) for x in Defs.NAMES].index("Warrior"), [str(x) for x in Defs.NAMES].index("Archer")
    ucls = [0]

    def player(hot=(), sto=(), util=(), active=-1, name="Tester"):
        """a Player (Unsafe-allocated, only its inventory field set) + its PlayerRef / Ref / Store / PacketHandler"""
        h, s_, u = SIC(JShort(9)), SIC(JShort(36)), UT(JShort(UCAP))
        for cont, items in ((h, hot), (s_, sto), (u.getInventory(), util)):
            for (sl, iid, q) in items:
                tx = cont.setItemStackForSlot(JShort(sl), IS(iid, q))
                assert tx.succeeded(), (iid, sl)
        jfield(UT, "activeSlot").setByte(u, JByte(active))
        p = us.allocateInstance(PLA.class_)
        jfield(PLA, "inventory").set(p, TInv(h, s_, u))
        stv = us.allocateInstance(TStore.class_)
        ref = us.allocateInstance(REF.class_)
        jfield(REF, "store").set(ref, stv)
        jfield(REF, "index").setInt(ref, 0)
        pr = us.allocateInstance(PRN.class_)
        ucls[0] += 1
        uid = UUID.fromString("00000000-0000-0000-0000-%012x" % (0xa000 + ucls[0]))
        jfield(PRN, "uuid").set(pr, uid)
        jfield(PRN, "username").set(pr, name)
        jfield(PRN, "entity").set(pr, ref)
        jfield(PRN, "packetHandler").set(pr, us.allocateInstance(TPH.class_))
        return p, pr, u

    def counts(p):
        inv = p.getInventory()
        out = {}
        for cont in (inv.getHotbar(), inv.getStorage(), inv.getUtility()):
            for i in range(int(cont.getCapacity())):
                it = cont.getItemStack(JShort(i))
                if it is None or it.isEmpty():
                    continue
                out[str(it.getItemId())] = out.get(str(it.getItemId()), 0) + int(it.getQuantity())
        return out

    def where(p, iid):
        """[(section, slot, qty)] of an item: h = hotbar, s = storage, u = utility"""
        inv = p.getInventory()
        res = []
        for tag, cont in (("h", inv.getHotbar()), ("s", inv.getStorage()), ("u", inv.getUtility())):
            for i in range(int(cont.getCapacity())):
                it = cont.getItemStack(JShort(i))
                if it is not None and not it.isEmpty() and str(it.getItemId()) == iid:
                    res.append((tag, i, int(it.getQuantity())))
        return res

    def delta(a, b):
        return dict((k, b.get(k, 0) - a.get(k, 0)) for k in set(a) | set(b) if b.get(k, 0) != a.get(k, 0))

    JProps = JClass("java.util.Properties")

    def kitfile(k):
        """the profile's class file as java.util.Properties reads it (escapes undone)"""
        f = os.path.join(pdir, k + ".properties")
        if not os.path.isfile(f):
            return {}
        pp = JProps()
        pp.load(JClass("java.io.StringReader")(open(f, encoding="latin-1").read()))
        return dict((str(x), str(pp.getProperty(x))) for x in pp.stringPropertyNames())

    def owed(k):
        o = {}
        for e in [x for x in kitfile(k).get("kitOwed", "").split(",") if x]:
            iid, _, q = e.rpartition(":")
            o[iid] = o.get(iid, 0) + int(q)
        return o

    def evs():
        return [e for e in TStore.EV]

    def packets(pr, cls):
        return [x for x in TPH.OUT if isinstance(x, cls)]

    def chat():
        out = []
        for x in TPH.OUT:
            if isinstance(x, SMSG):
                try:
                    out.append(str(x.message.rawText))
                except Exception:
                    out.append(str(jfield(JClass("com.hypixel.hytale.protocol.FormattedMessage"), "rawText").get(jfield(SMSG, "message").get(x))))
        return out

    def reset(mode=0):
        TStore.EV.clear()
        TPH.OUT.clear()
        TStore.MODE = mode

    def kit_of(cls_i):
        return {str(i): int(q) for i, q in zip(KitCfg.parse(KitCfg.textOf(cls_i), None, 9)[0], KitCfg.parse(KitCfg.textOf(cls_i), None, 9)[1])}

    def give(p, pr, ci, admin=False, by=None, label=""):
        k = str(pr.getUuid())
        if not admin:
            check(int(Store.markKitKey(k, str(Defs.NAMES[ci]))) == 0, "Z %s: the profile is marked pending" % label)
        before = counts(p)
        r = Kit.give(pr, p, k, ci, admin, by)
        after = counts(p)
        kit = kit_of(ci)
        d = delta(before, after)
        o = owed(k)
        ok_ = all(d.get(i, 0) + o.get(i, 0) - (0 if admin else 0) >= q for i, q in kit.items())
        check(r is None, "Z %s: give returned %s" % (label, r))
        check(all(v >= 0 for v in d.values()) and set(d) <= set(kit) and all(d.get(i, 0) + o.get(i, 0) == q for i, q in kit.items()),
              "Z %s: item counts: given %s + owed %s = the kit %s (nothing lost, nothing doubled, nothing else touched)" % (label, d, o, kit))
        return k, d, o

    # ---------------- Z1: an empty off-hand (no active utility slot - a fresh player): the shield becomes the off-hand the vanilla way
    check(str(KitCfg.K_WARRIOR) == "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" and str(Kit.OFFHAND) == "Weapon_Shield_", "Z: the Warrior kit + OFFHAND")
    reset()
    p, pr, u = player()
    k, d, o = give(p, pr, WAR, label="1 empty off-hand")
    check(where(p, SHIELD) == [("u", 0, 1)] and where(p, SWORD) == [("h", 0, 1)], "Z1: the shield in utility slot 0, the sword in the hotbar: %s %s"
          % (where(p, SHIELD), where(p, SWORD)))
    check(int(u.getActiveSlot()) == 0 and u.getActiveItem() is not None and str(u.getActiveItem().getItemId()) == SHIELD
          and str(p.getInventory().getUtilityItem().getItemId()) == SHIELD, "Z1: utility slot 0 is the ACTIVE one = the off-hand holds the shield")
    e_ = evs()
    check(len(e_) == 2 and isinstance(e_[0], ASRE) and isinstance(e_[1], SET_EV), "Z1: the vanilla events: request, then the active-slot change (%s)"
          % [str(x.getClass().getSimpleName()) for x in e_])
    if len(e_) == 2 and isinstance(e_[0], ASRE):
        q_ = e_[0]
        check(int(q_.getInventorySectionId()) == -5 and int(q_.getPreviousSlot()) == -1 and int(q_.getNewSlot()) == 0 and bool(q_.isServerRequest())
              and not bool(q_.isClientRequest()), "Z1: the request: utility section -5, -1 -> 0, serverRequest true (the vanilla move's flag): "
              "%s %s %s %s" % (q_.getInventorySectionId(), q_.getPreviousSlot(), q_.getNewSlot(), q_.isServerRequest()))
    sp_ = packets(pr, SAS)
    check(len(sp_) == 1 and int(sp_[0].inventorySectionId) == -5 and int(sp_[0].activeSlot) == 0, "Z1: one SetActiveSlot(-5, 0) packet to the client")
    kf = kitfile(k)
    check(kf.get("kit") == "given" and not kf.get("kitOwed") and kf.get("kitItems") == "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1",
          "Z1: the kit record: given, nothing owed, the items (%s)" % kf)
    ch = chat()
    check("[Classes] Your Warrior kit is ready: Sword Crude x1 in your hotbar, Shield Wood x1 in your off-hand." in ch and not any("did not fit" in c for c in ch),
          "Z1: the chat line says where the shield went: %s" % ch)
    # ---------------- Z2: an active utility slot that is empty: used as it is (no event, no packet)
    reset()
    p, pr, u = player(util=[(0, TORCH, 3)], active=2)
    give(p, pr, WAR, label="2 empty active slot")
    check(where(p, SHIELD) == [("u", 2, 1)] and int(u.getActiveSlot()) == 2 and str(u.getActiveItem().getItemId()) == SHIELD
          and where(p, TORCH) == [("u", 0, 3)], "Z2: the shield into the empty ACTIVE slot 2 (the torch in slot 0 untouched): %s" % where(p, SHIELD))
    check(not evs() and not packets(pr, SAS), "Z2: no request event, no packet (the active slot did not change)")
    # ---------------- Z3: a taken off-hand (the active slot holds a torch): the shield goes the normal way
    reset()
    p, pr, u = player(util=[(0, TORCH, 5)], active=0)
    give(p, pr, WAR, label="3 taken off-hand")
    check(where(p, SHIELD) == [("h", 1, 1)] and where(p, SWORD) == [("h", 0, 1)] and where(p, TORCH) == [("u", 0, 5)] and int(u.getActiveSlot()) == 0,
          "Z3: the off-hand is taken -> the shield into the hotbar after the sword, the torch stays the off-hand: %s" % where(p, SHIELD))
    check(not evs() and not packets(pr, SAS), "Z3: no event, no packet")
    check(any(c == "[Classes] Your Warrior kit is in your hotbar: Sword Crude x1, Shield Wood x1." for c in chat()), "Z3: the 0.1.7 chat line: %s" % chat())
    # ---------------- Z4: taken off-hand + a full hotbar: everything owed, then /class kit (hotbar then storage - never the off-hand)
    reset()
    p, pr, u = player(hot=[(i, STICK, 1) for i in range(9)], util=[(0, TORCH, 5)], active=0)
    k, d, o = give(p, pr, WAR, label="4 nothing fits")
    check(not d and o == {SWORD: 1, SHIELD: 1} and kitfile(k).get("kit") == "owed", "Z4: nothing landed, the whole kit is owed: %s" % o)
    check(any("did not fit your hotbar" in c for c in chat()), "Z4: the 'did not fit' line")
    b4 = counts(p)
    Kit.claim(pr, p, k, False)
    d4 = delta(b4, counts(p))
    check(d4 == {SWORD: 1, SHIELD: 1} and where(p, SHIELD) == [("s", 1, 1)] and where(p, TORCH) == [("u", 0, 5)] and not owed(k),
          "Z4: /class kit collects both into storage (the hotbar is full; claims never use the off-hand): %s %s" % (d4, where(p, SHIELD)))
    # ---------------- Z5: no active slot and no free utility slot: the normal way
    reset()
    p, pr, u = player(util=[(i, TORCH, 1) for i in range(UCAP)])
    give(p, pr, WAR, label="5 no free utility slot")
    check(where(p, SHIELD) == [("h", 1, 1)] and int(u.getActiveSlot()) == -1 and not evs(), "Z5: every utility slot taken -> the hotbar, no event")
    # ---------------- Z6: another system cancels the request: the shield stays in utility slot 0 (no second shield anywhere)
    reset(mode=1)
    p, pr, u = player()
    give(p, pr, WAR, label="6 request cancelled")
    check(where(p, SHIELD) == [("u", 0, 1)] and int(u.getActiveSlot()) == -1 and not packets(pr, SAS) and len(evs()) == 1,
          "Z6: cancelled -> the shield stays in utility slot 0, no active slot, no packet, ONE shield: %s" % where(p, SHIELD))
    # ---------------- Z7: another system redirects the request (vanilla honours getNewSlot): mirrored, still one shield
    reset(mode=2)
    p, pr, u = player()
    give(p, pr, WAR, label="7 request redirected")
    sp_ = packets(pr, SAS)
    check(where(p, SHIELD) == [("u", 0, 1)] and int(u.getActiveSlot()) == 3 and len(sp_) == 1 and int(sp_[0].activeSlot) == 3,
          "Z7: redirected to slot 3 exactly like the vanilla move (active 3, packet 3), one shield")
    # ---------------- Z8: /classadmin kit twice (KitTask mode 1 -> give(admin)): the first shield into the off-hand, the second the normal way
    reset()
    p, pr, u = player()
    by = player(name="Admin")[1]
    k8 = str(pr.getUuid())
    Store.markKitKey(k8, "Warrior")
    give(p, pr, WAR, admin=True, by=by, label="8a /classadmin kit")
    check(where(p, SHIELD) == [("u", 0, 1)] and int(u.getActiveSlot()) == 0, "Z8: /classadmin kit: the shield into the empty off-hand")
    reset()
    b8 = counts(p)
    r8 = Kit.give(pr, p, k8, WAR, True, None)
    d8 = delta(b8, counts(p))
    check(r8 is None and d8 == {SWORD: 1, SHIELD: 1} and where(p, SHIELD) == [("h", 2, 1), ("u", 0, 1)] and where(p, SWORD) == [("h", 0, 1), ("h", 1, 1)]
          and not evs(),
          "Z8: a second /classadmin kit: the off-hand is taken -> the second shield into the hotbar (%s)" % where(p, SHIELD))
    check(counts(p) == {SWORD: 2, SHIELD: 2} and kitfile(k8).get("kit") == "given", "Z8: two kits = 2 swords + 2 shields, the record given")
    # ---------------- Z9: the Archer kit: the utility section is never touched
    reset()
    p, pr, u = player()
    give(p, pr, ARC, label="9 Archer kit")
    check(where(p, BOW) == [("h", 0, 1)] and sum(q for _t, _i, q in where(p, ARROW)) == 64 and int(u.getActiveSlot()) == -1 and not evs()
          and all(where(p, x) == [] or all(t_ != "u" for t_, _i, _q in where(p, x)) for x in (BOW, ARROW)), "Z9: bow + 64 arrows in the hotbar, utility untouched")
    # ---------------- Z10-Z12: custom Warrior kits (a torch first = not a shield; two shields; a non-usable Weapon_Shield_ id)
    old_k = str(KitCfg.K_WARRIOR)
    for label, text, want_u, want_h in (
            ("10 torch + shield", "Furniture_Crude_Torch:2,Weapon_Shield_Wood:1", {SHIELD: 1}, {TORCH: 2}),
            ("11a two of one shield", "Weapon_Shield_Wood:2", {SHIELD: 1}, {SHIELD: 1}),
            ("11b two shields", "Weapon_Shield_Iron:1,Weapon_Shield_Wood:1,Weapon_Sword_Crude:1", {IRON: 1}, {SHIELD: 1, SWORD: 1}),
            ("12 not usable", "Weapon_Shield_Fake:1,Weapon_Sword_Crude:1", {}, {FAKE: 1, SWORD: 1})):
        KitCfg.K_WARRIOR = text
        reset()
        p, pr, u = player()
        give(p, pr, WAR, label=label)
        inu = {}
        inh = {}
        for iid in (SHIELD, IRON, FAKE, SWORD, TORCH):
            for t_, _i, q in where(p, iid):
                (inu if t_ == "u" else inh)[iid] = (inu if t_ == "u" else inh).get(iid, 0) + q
        check(inu == want_u and inh == want_h, "Z%s: off-hand %s, hotbar %s (want %s / %s)" % (label, inu, inh, want_u, want_h))
    KitCfg.K_WARRIOR = old_k
    # ---------------- Z13: the chat line texts (pure)
    SA, IA = JArray(JClass("java.lang.String")), JArray(JInt)
    ids_ = SA([SWORD, SHIELD])
    check(str(Kit.givenLine("Warrior", ids_, IA([1, 1]), IA([0, 0]))) == "Your Warrior kit is in your hotbar: Sword Crude x1, Shield Wood x1."
          and str(Kit.givenLine("Warrior", ids_, IA([1, 1]), None)) == "Your Warrior kit is in your hotbar: Sword Crude x1, Shield Wood x1."
          and str(Kit.givenLine("Warrior", ids_, IA([1, 1]), IA([0, 1]))) == "Your Warrior kit is ready: Sword Crude x1 in your hotbar, Shield Wood x1 in your off-hand."
          and str(Kit.givenLine("Warrior", ids_, IA([0, 1]), IA([0, 1]))) == "Your Warrior kit is ready: Shield Wood x1 in your off-hand.",
          "Z13: the chat lines (0.1.7 line without an off-hand give; where each part went with one)")
    # ---------------- Z14: garbage never throws, never gives
    p, pr, u = player()
    check(int(Kit.offhand(None, p, SHIELD)) == 0 and int(Kit.offhand(pr, None, SHIELD)) == 0 and int(Kit.offhand(pr, p, None)) == 0
          and int(Kit.offhand(pr, p, SWORD)) == 0 and int(Kit.offhand(pr, p, TORCH)) == 0 and not counts(p), "Z14: offhand garbage / non-shields = 0, nothing added")
    bare = us.allocateInstance(PLA.class_)
    check(int(Kit.offhand(pr, bare, SHIELD)) == 0, "Z14: a player without an inventory = 0")
    check(not bool(Kit.select(us.allocateInstance(PRN.class_), p.getInventory(), 0)), "Z14: select without a live ref = false, no throw")
    print("Z. kit hand-out done (%d test items, utility capacity %d)" % (9, UCAP))

    # ---------------- the heal maths at the 0.1.10 default (a fresh file = the new code default)
    hdir = os.path.join(SCRATCH, "z", "heal", "Skyy_SkyyClasses")
    os.makedirs(hdir)
    Cfg.FILE = Paths.get(os.path.join(hdir, "config.properties"))
    Cfg.load()
    check(int(Cfg.HEAL_SELF_PCT) == 100 and int(Cfg.HEAL_SHARE_PCT) == 25 and float(Cfg.HEAL_MAX_HIT) == 10.0, "Z-heal: fresh file: self 100%%, share 25%%, cap 10")
    rows_ = []
    for d_ in (0.4, 1.0, 4.0, 12.0, 39.0, 40.0, 41.0, 400.0):
        w_ = float(HT.want(d_, int(Cfg.HEAL_SHARE_PCT), float(Cfg.HEAL_MAX_HIT)))
        s_ = float(HT.selfWant(w_, int(Cfg.HEAL_SELF_PCT)))
        rows_.append((d_, w_, s_))
    check(all(abs(w_ - min(d_ * 0.25, 10.0)) < 1e-9 and s_ == w_ for d_, w_, s_ in rows_),
          "Z-heal: the Priest heals itself exactly what each party member gets: %s" % rows_)
    check(float(HT.room(float(HT.selfWant(10.0, 100)), JFloat(95.0), JFloat(100.0))) == 5.0, "Z-heal: the self-heal still stops at max Health")
    print("Z. heal maths at 100%% done: %s" % ", ".join("%g dmg -> %g / %g" % r_ for r_ in rows_))
    run_m(Cfg, J, Paths, jfield)


def run_m(Cfg, J, Paths, jfield):
    """Part M: ClassCfg.migrate0110 on scratch files (same child JVM, after Z)."""
    from jpype import JClass, JArray, JObject
    import collections
    MARK = str(Cfg.MG_MARK)
    WHO = str(Cfg.MG_WHO)
    KitCfg = J("KitCfg")
    check(MARK_ID in MARK and "=" not in MARK and WHO == MG_WHO, "M: the marker (doc comment, no '=') and the update's name")
    mroot = os.path.join(SCRATCH, "mig")

    def setup(name, text=None, copy_from=None):
        home = os.path.join(mroot, name, "Skyy_SkyyClasses")
        if copy_from:
            shutil.copytree(copy_from, home)
        else:
            os.makedirs(home)
        f = os.path.join(home, "config.properties")
        if text is not None:
            open(f, "wb").write(text.encode("latin-1"))
        Cfg.FILE = Paths.get(f)
        return home, f

    def hist(home):
        d = os.path.join(home, "config-history")
        return sorted(x for x in os.listdir(d) if x.endswith(".bak")) if os.path.isdir(d) else []

    def logl(home):
        f = os.path.join(home, "config-changes.log")
        return [l for l in open(f, encoding="utf8").read().split("\n") if l] if os.path.isfile(f) else []

    def rd(f):
        return open(f, "rb").read()

    def mig():
        return str(Cfg.migrate0110())

    def once(name, home, f, before):
        """the second start: nothing more (the marker is there)"""
        b1, h1, l1 = rd(f), hist(home), logl(home)
        r2 = mig()
        check(r2 == "" and rd(f) == b1 and hist(home) == h1 and logl(home) == l1, "M %s: the second start changes nothing (%r)" % (name, r2))

    def saved(home, data):
        return any(open(os.path.join(home, "config-history", x), "rb").read() == data for x in hist(home))

    def ins_marker(text, before_line):
        """text with the marker inserted right above the first line equal to before_line (LF)"""
        ls = text.split("\n")
        i = ls.index(before_line)
        return "\n".join(ls[:i] + [MARK] + ls[i:])

    # ---------------- M1: the scratch COPY of the live config, as it is
    live_ok = os.path.isfile(os.path.join(LIVE_COPY, "config.properties"))
    if live_ok:
        home, f = setup("live-as-is", copy_from=LIVE_COPY)
        b0, h0, l0 = rd(f), hist(home), logl(home)
        t0 = b0.decode("latin-1")
        r = mig()
        t1 = rd(f).decode("latin-1")
        has_war = any(l.strip().startswith("kit.Warrior") for l in t0.split("\n"))
        selfv = [l.split("=", 1)[1].strip() for l in t0.replace("\r", "").split("\n") if l.startswith("priestHeal.selfPercent")]
        print("M1: the live config: kit.Warrior line %s, priestHeal.selfPercent %s, %d history files, %d change-log lines"
              % ("present" if has_war else "absent", selfv or "absent", len(h0), len(l0)))
        if not has_war and selfv == ["100"]:
            check("nothing changed" in r and "kept" not in r, "M1: live copy: nothing to change - Skyy's hand-set 100 is the new default "
                                                               "(silent), no kit.Warrior line (the new code default applies): %r" % r)
            check(t1 == ins_marker(t0, "priestHeal.selfPercent=100"), "M1: live copy: only the marker line was added, right above "
                                                                       "priestHeal.selfPercent=100 (every other byte kept)")
            check(logl(home) == l0, "M1: no change-log line (nothing changed)")
        else:
            check(r != "" and MARK in t1, "M1: live copy updated / marked (%r)" % r)
        check(len(hist(home)) == len(h0) + 1 and saved(home, b0) and all(x in hist(home) for x in h0),
              "M1: one new History version holding the old bytes; the live history copies kept (%d -> %d)" % (len(h0), len(hist(home))))
        idx_ = open(os.path.join(home, "config-history", "index.log"), encoding="utf8").read()
        check(WHO in idx_ and "before the 0.1.10 defaults update" in idx_, "M1: the History index names the update")
        once("1 live", home, f, b0)
        Cfg.load()
        check(str(KitCfg.K_WARRIOR) == "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" and int(Cfg.HEAL_SELF_PCT) == 100,
              "M1: the live copy loads with the Wood Shield kit + self-heal 100 (%s)" % Cfg.summary())
        if "priestHeal.maxPerHit=50" in t0:
            check(float(Cfg.HEAL_MAX_HIT) == 50.0 and float(Cfg.HEAL_MAX_SEC) == 1000.0, "M1: Skyy's other in-game values kept (maxPerHit 50, maxPerSecond 1000)")
        base = t0
    else:
        check(True, "M1 skipped (no live config)")
        base = "# SkyyClasses config\nswitchCost=5000\n\n# ---- changed in game (SkyWynn Menu) ----\npriestHeal.maxPerHit=50\npriestHeal.selfPercent=100\n"

    # ---------------- M2: the live copy with UNTOUCHED old defaults: updated once (value text only, History first, two log lines)
    t2 = base.replace("priestHeal.selfPercent=100", "priestHeal.selfPercent=50")
    if "priestHeal.selfPercent=50" not in t2:
        t2 = t2 + "priestHeal.selfPercent=50\n"
    t2 = t2 + ("" if t2.endswith("\n") else "\n") + "kit.Warrior=Weapon_Sword_Crude:1\n"
    home, f = setup("live-untouched", text=t2, copy_from=LIVE_COPY if live_ok else None)
    if live_ok:
        open(f, "wb").write(t2.encode("latin-1"))
    b2, l2 = rd(f), logl(home)
    r = mig()
    t2n = rd(f).decode("latin-1")
    want2 = ins_marker(t2, "priestHeal.selfPercent=50").replace("priestHeal.selfPercent=50", "priestHeal.selfPercent=100") \
        .replace("kit.Warrior=Weapon_Sword_Crude:1\n", "kit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1\n")
    check(t2n == want2, "M2: untouched lines -> the new defaults, the marker above the first of them, every other byte kept:\n%s" % t2n)
    check("kit.Warrior Weapon_Sword_Crude:1 -> Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" in r and "priestHeal.selfPercent 50 -> 100" in r
          and "kept" not in r, "M2: the INFO line names both changes: %r" % r)
    new_l = logl(home)[len(l2):]
    rows2 = [l.split("\t") for l in new_l]
    check(len(rows2) == 2 and all(len(x) == 8 and x[1:4] == [WHO, "-", "update"] and x[7] == "ok" for x in rows2)
          and sorted((x[4], x[5], x[6]) for x in rows2) == sorted([("kit.Warrior", "Weapon_Sword_Crude:1", "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1"),
                                                                    ("priestHeal.selfPercent", "50", "100")]),
          "M2: two config-changes.log lines in the kit's scalar-row format (Server Setup -> Changes can Undo each): %s" % new_l)
    check(saved(home, b2), "M2: the old file is a History version (verified before the rewrite)")
    once("2 untouched", home, f, b2)
    Cfg.load()
    check(str(KitCfg.K_WARRIOR) == "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" and int(Cfg.HEAL_SELF_PCT) == 100, "M2: loads with the new values")
    m2_home = home

    # ---------------- M3: EDITED values are kept and logged once
    t3 = base.replace("priestHeal.selfPercent=100", "priestHeal.selfPercent=75")
    if "priestHeal.selfPercent=75" not in t3:
        t3 += "priestHeal.selfPercent=75\n"
    t3 += "kit.Warrior=Weapon_Sword_Crude:2\n"
    home, f = setup("edited", text=t3)
    r = mig()
    check(rd(f).decode("latin-1") == ins_marker(t3, "priestHeal.selfPercent=75"), "M3: edited values untouched (only the marker added)")
    check("nothing changed" in r and "kit.Warrior=Weapon_Sword_Crude:2 kept (custom) - the 0.1.10 default is Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" in r
          and "priestHeal.selfPercent=75 kept (custom) - the 0.1.10 default is 100" in r, "M3: both kept values noted: %r" % r)
    check(not logl(home), "M3: no change-log line")
    once("3 edited", home, f, None)

    # ---------------- M4: the 0.1.9 default file, LF and CRLF: only the two values + the marker line change
    d19 = defaults_019()
    check("kit.Warrior=Weapon_Sword_Crude:1\n" in d19 and "priestHeal.selfPercent=50\n" in d19 and MARK_ID not in d19, "M4: the 0.1.9 default file")
    for nl in ("\n", "\r\n"):
        t4 = d19.replace("\n", nl)
        home, f = setup("d019-" + ("crlf" if nl == "\r\n" else "lf"), text=t4)
        r = mig()
        got = rd(f).decode("latin-1")
        want4 = ins_marker(d19, "kit.Warrior=Weapon_Sword_Crude:1").replace("kit.Warrior=Weapon_Sword_Crude:1\n",
                                                                           "kit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1\n") \
            .replace("priestHeal.selfPercent=50\n", "priestHeal.selfPercent=100\n").replace("\n", nl)
        check(got == want4, "M4 %s: the 0.1.9 default file -> the two new values + the marker above kit.Warrior, line ends kept" % repr(nl))
        a_ = collections.Counter(t4.split(nl))
        b_ = collections.Counter(got.split(nl))
        check(sorted((a_ - b_).elements()) == ["kit.Warrior=Weapon_Sword_Crude:1", "priestHeal.selfPercent=50"]
              and sorted((b_ - a_).elements()) == sorted([MARK, "kit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1", "priestHeal.selfPercent=100"]),
              "M4 %s: line diff = exactly the two values + the marker" % repr(nl))
        once("4 " + repr(nl), home, f, None)
        Cfg.load()
        check(str(KitCfg.K_WARRIOR) == "Weapon_Sword_Crude:1,Weapon_Shield_Wood:1" and int(Cfg.HEAL_SELF_PCT) == 100 and float(Cfg.HEAL_RADIUS) == 16.0,
              "M4 %s: loads with the new defaults (the rest unchanged)" % repr(nl))

    # ---------------- M5: a fresh server: no file -> no update; load writes the 0.1.10 default WITH the marker -> never updated
    home, f = setup("fresh")
    check(mig() == "" and not os.path.exists(f) and not os.path.exists(os.path.join(home, "config-history")), "M5: no file = nothing (no file, no history)")
    Cfg.load()
    b5 = rd(f)
    check(MARK in b5.decode("latin-1") and mig() == "" and rd(f) == b5 and not hist(home), "M5: the fresh 0.1.10 default file has the marker: never updated")

    # ---------------- M6-M12: parser cases on the pure step + the file path
    def upd(text):
        r_ = Cfg.mgUpdate(text)
        return None if r_ is None else (str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]])

    t6 = "kit.Warrior=Weapon_Sword_Crude:1,\\\n  Weapon_Arrow_Crude:5\npriestHeal.selfPercent=50\n"
    u6 = upd(t6)
    check(u6 is not None and u6[0] == MARK + "\nkit.Warrior=Weapon_Sword_Crude:1,\\\n  Weapon_Arrow_Crude:5\npriestHeal.selfPercent=100\n"
          and any(x.startswith("kit.Warrior=") and "kept (custom)" in x for x in u6[2]) and u6[3] == ["priestHeal.selfPercent", "50", "100"],
          "M6: a continued kit.Warrior entry is kept (noted), its continuation bytes untouched; selfPercent updated: %r" % (u6,))
    u7 = upd("kit.Warrior=Weapon_Sword_Crude:1\nkit.Warrior=Weapon_Sword_Crude:1\n")
    check(u7[0] == MARK + "\nkit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1\nkit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1\n",
          "M7: two untouched kit.Warrior lines -> both updated")
    u7b = upd("kit.Warrior=Weapon_Sword_Crude:1\nkit.Warrior=Weapon_Sword_Crude:3\n")
    check(u7b[0] == MARK + "\nkit.Warrior=Weapon_Sword_Crude:1\nkit.Warrior=Weapon_Sword_Crude:3\n" and not u7b[3]
          and any("Weapon_Sword_Crude:3 kept" in x for x in u7b[2]), "M7: the LAST line wins (custom) -> nothing rewritten")
    u8 = upd("# help\nkit.Warrior : Weapon_Sword_Crude:1\r\npriestHeal.selfPercent=  50  \r\n")
    check(u8[0] == MARK + "\n# help\nkit.Warrior : Weapon_Sword_Crude:1,Weapon_Shield_Wood:1\r\npriestHeal.selfPercent=  100\r\n",
          "M8: the marker above the help comment that sits right on top of the first entry; separators kept (' : ', '=  '), the "
          "trailing spaces of 50 dropped, CR kept per line: %r" % (u8[0],))
    check(upd("# " + MARK_ID + " (old)\nkit.Warrior=Weapon_Sword_Crude:1\n") is None, "M9: the marker already there = never again (even with old values)")
    u10 = upd("switchCost=5000\nrequireClass=false")
    check(u10[0] == MARK + "\nswitchCost=5000\nrequireClass=false" and not u10[3] and not u10[2], "M10: no key at all -> the marker on line 0, nothing else")
    u10b = upd("")
    check(u10b[0] == MARK + "\n", "M10: an empty file -> just the marker")
    u11 = upd("a=1\\")
    check(u11[0] == MARK + "\na=1\\", "M11: a file ending inside an open continued entry: the marker on line 0 (never swallowed)")
    u12 = upd("priestHeal.selfPercent=100\nkit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1\n")
    check(u12[0] == MARK + "\n" + "priestHeal.selfPercent=100\nkit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1\n" and not u12[2] and not u12[3],
          "M12: values already on the new defaults: silent, only the marker")
    for g_ in ("\n\n\n", "=\n", "\\\n\\\n", "#\n!x=1\n", " kit.Warrior=Weapon_Sword_Crude:1"):
        try:
            Cfg.mgUpdate(g_)
            OKS[0] += 1
        except Exception as e:
            check(False, "M: mgUpdate(%r) threw %s" % (g_, e))
    u13 = upd(" kit.Warrior=Weapon_Sword_Crude:1")
    check(u13[0] == MARK + "\n kit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1", "M13: a leading space before the key (Properties reads it) is kept")

    # ---------------- M14: History cannot be written (config-history is a FILE): untouched, retried at the next start
    t14 = "kit.Warrior=Weapon_Sword_Crude:1\n"
    home, f = setup("nohistory", text=t14)
    open(os.path.join(home, "config-history"), "w").write("not a folder")
    r = mig()
    check(r == "" and rd(f) == t14.encode("latin-1") and not logl(home), "M14: History not writable -> nothing changed (WARN), no log line")
    os.remove(os.path.join(home, "config-history"))
    r = mig()
    check("kit.Warrior Weapon_Sword_Crude:1 -> " in r and rd(f).decode("latin-1") == MARK + "\nkit.Warrior=Weapon_Sword_Crude:1,Weapon_Shield_Wood:1\n"
          and saved(home, t14.encode("latin-1")), "M14: the next start updates it (History copy first)")

    # ---------------- M15: Server Setup Undo (the config kit's own set path, via undo) on M2's folder; the next start leaves it
    Pub = J("CfgPub")
    Cfg.FILE = Paths.get(os.path.join(m2_home, "config.properties"))
    Cfg.load()
    Pub.start(Paths.get(os.path.dirname(m2_home)), None)
    bridge = Cfg.bridge()
    fn = bridge.get("config:fn:SkyyClasses")

    def op(*args):
        a = JArray(JObject)(len(args))
        for i, x in enumerate(args):
            a[i] = x
        return fn.apply(a)

    lg = [str(x) for x in op("log", JClass("java.lang.Integer").valueOf(50))]
    check(any(l.split("\t")[1:7] == [WHO, "-", "update", "priestHeal.selfPercent", "50", "100"] for l in lg),
          "M15: Server Setup -> Changes lists the update lines: %s" % lg[:3])
    # Server Setup -> Changes -> Undo = the kit's own set of the logged OLD value (via "console" here: who == null is only the console
    # in the kit, and a bare JVM has no permission provider for a player UUID)
    r = op("set", "priestHeal.selfPercent", "50", None, None, "yes", "console")
    r2 = op("set", "kit.Warrior", "Weapon_Sword_Crude:1", None, None, "yes", "console")
    Pub.flush()
    time.sleep(0.5)
    Pub.flush()
    t15 = open(os.path.join(m2_home, "config.properties"), "rb").read().decode("latin-1")
    check(str(r[0]) == "ok" and int(Cfg.HEAL_SELF_PCT) == 50 and "priestHeal.selfPercent=50" in t15,
          "M15: Undo of the self-heal line through the kit -> 50 again (%s)" % [str(x) for x in r])
    check(str(r2[0]) == "ok" and str(KitCfg.K_WARRIOR) == "Weapon_Sword_Crude:1" and "kit.Warrior=Weapon_Sword_Crude:1\n" in t15.replace("\r", ""),
          "M15: Undo of the kit line through the kit -> the sword-only kit again (%s)" % [str(x) for x in r2])
    Pub.shutdown()
    b15 = open(os.path.join(m2_home, "config.properties"), "rb").read()
    r = mig()
    check(r == "" and open(os.path.join(m2_home, "config.properties"), "rb").read() == b15, "M15: the next start leaves the undone values (runs once)")
    print("M. one-time update done (live copy: %s)" % ("yes" if live_ok else "no"))


def main():
    if "--run" in sys.argv:
        run(arg("--run"))
        print("%d checks passed, %d failed" % (OKS[0], len(FAILS)))
        for f in FAILS:
            print("  FAILED:", f)
        sys.exit(1 if FAILS else 0)
    if "--states" in sys.argv:
        run_states(arg("--states"), arg("--out"), arg("--tag"))
        return
    if "--bytecode" in sys.argv:
        run_bytecode(arg("--bytecode"), arg("--new"), arg("--out"))
        return
    if "--z" in sys.argv:
        run_z(arg("--z"))
        print("part Z + M: %d checks passed, %d failed" % (OKS[0], len(FAILS)))
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
    copy_live()
    pz = subprocess.run([sys.executable, os.path.abspath(__file__), "--z", JAR, "--dir", SCRATCH], env=env)
    part_y(env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    print("part Y (ClassPage page states, %s vs %s): %d checks passed, %d failed" % (OLD_VERSION, VERSION, OKS[0], len(FAILS)))
    for f in FAILS[:60]:
        print("  FAILED:", f)
    print("child A-X exit %d, child Z + M exit %d" % (p.returncode, pz.returncode))
    ok = p.returncode == 0 and pz.returncode == 0 and not FAILS
    print("SkyyClasses %s bare-JVM check:" % VERSION, "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
