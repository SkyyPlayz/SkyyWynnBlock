"""Bare-JVM checks for SkyyAccessories 0.5.2, kept next to the build so every claim of the build report can be re-run by anyone.
0.5.2 (the Workbench tab "Accessories & Bags", tools/acc_0_5_2_patch.py): the 0.5.1 harness carried forward - every check below runs
unchanged (0.5.2 changes no class but the plugin) - with Y now comparing 0.5.1 -> 0.5.2 and two new sections:
  W  THE WORKBENCH TAB on real engine objects (tools/skyywbtab.py harness_checks; SkyySacks 0.7.10 on the classpath too): SkyyAccessories
     alone, SkyySacks alone, both in both start orders (this mod's entry + order every time), idempotent, copy-on-write, a second Workbench
     override and the shared state variant, the Furnace untouched, the vanilla Crafting tab untouched, asset / recipe reload listeners,
     WbRank == the Python mirror, a REAL SimpleCraftingWindow's windowData (tabs, name key, icon, craftableRecipes in crafting order)
  L  the start sequence (migrate051, the config loader, notices, WbTab.start; + SkyySacks' WbTab.start) twice on a fresh scratch copy of
     the live Skyy_SkyyAccessories folder: every file byte-identical (no churn)
  Y  COMPARE with the 0.5.1 jar: classes (3 new Wb classes; only the plugin and the kit version change) and assets (the 47 recipe JSONs
     differ only in BenchRequirement; server.lang only in the 2 tab name lines; the tab icon is new; the manifest version)
The 0.5.1 notes:
  H  HIDDEN OLD IDS: the jar's item JSON - the 20 legacy booster ids + 5 retired bench accessories carry "Variant": true and no
     "Categories", the 67 current items Categories ["Items.Tools"] and no Variant; every legacy id still maps to its line and rarity
     (tierOf / familyOf / modernOf / pretty) and keeps the look and name of the rarity it counts as; a legacy stack still converts in
     the bag (AccStore.equipK after modernOf = the page's Equip; a tie refused); the engine proof (Item codec documentation in
     HytaleServer.jar, Item.toPacket copies variant + categories, the client's Show Variants toggle in the Item Library UI - read-only,
     skipped without the client files); no quality has HideFromSearch
  S  THE 0.5.1 STAMINA UPDATE (AccCfg.migrate051, in setup()'s order: migrate051 then load(true)) on a scratch COPY of the live
     Skyy_SkyyAccessories folder when it is a 0.5 folder (else 0.5's own default file from SkyyAccessories-0.5.jar): only the two
     Stamina values and one marker line change (byte compare of every other line), the History copy = the old file byte for byte
     (+ index.log line), two config-changes.log lines in the kit's table format with status ok, the running numbers, the second start
     changes nothing, a value set back to the 0.5 numbers later stays; custom / spaced / duplicated / continued / missing lines, CRLF,
     a file without boost. lines (0.4.x: untouched, then the 0.5 migration writes the 0.5.1 numbers + the marker), a fresh default file,
     a file with no Stamina line (marker only), History that cannot be written (WARN, untouched, retried next start); UNDO through the
     real config kit (CfgPub.start on the scratch folder, op log lists our lines, the inverse tset writes the old value back, the
     running numbers follow, the next start keeps it)
  Y  COMPARE with the 0.5 jar: classes (identical / changed / new, no class gone, MoveSync identical, AccStore only CAMP_XP_TEXT) and
     assets - only the 25 hidden item JSONs (exactly Categories -> Variant), the 16 Stamina lang lines (4 items + 4 legacy ids, items. +
     server.items.), the 2 Campfire Accessory text lines (50% -> 25% Cooking XP, following SkyyCooking 0.1.3) and the manifest version

    python SkyyAccessories/test_skyyaccessories_0.5.2.py [--jar <SkyyAccessories-0.5.2.jar>] [--dir <scratch folder>] [--keep] [--synthetic] [--live <folder>]
    (--synthetic: section M uses the synthetic 0.4.5 folder even while the live one is still a 0.4.x folder)

Build first (python tools/acc_0_5_2_patch.py, python SkyyAccessories/build_skyyaccessories_0.5.2.py, SkyySacks 0.7.10). A child process starts a fresh
JVM (the game's own JRE, -Xverify:all, -XX:-UsePerfData, HytaleServer.jar read-only + the jar + tools/javassist.jar on the classpath;
TEMP / TMP / java.io.tmpdir in the scratch folder) and checks:
  A  every class of the jar loads and verifies
  T  TABLE: the build script's BOOSTER TABLE block (exec'd here, its own rule checks run again) equals the jar's AccDefs / AccCfg arrays
     (lines, ids, source words, id words, rarities, Accessory Power, config entries, units, caps, the live numbers, the defaults)
  F  FOLD: all 25 ids 0.4.5 shipped + the 15 older ids through the jar's tierOf / familyOf / isLegacy / modernOf / rarityOf / pretty /
     groupOf against the script's Python mirror; the equip swap order through AccStore.equipK on a scratch bag (Normal -> Unique swaps,
     the old _Legendary is stored as _Epic and ties with it, a lower rarity is refused); ONLY THE HIGHEST RARITY OF A LINE COUNTS
     (bestTiers / bonusLines with duplicates); the numbers each rarity gives (statParts) and a switched-off line
  M  MIGRATION on a scratch COPY of the live Skyy_SkyyAccessories folder (copied read-only from the HUD mod world; the exact live files):
     the one atomic update (slots 9 -> 18, bonus. lines out, the 0.5 keys in, the .pre-0.5.bak copy byte for byte, config-changes.log
     lines in the kit's format), the second start changes nothing, a later slots=9 stays 9; edited lists (carried as 1st, 2nd, 3rd, 5th,
     capped; unit-changed / not-5-numbers dropped and logged), continuation lines, CRLF files, a file with neither kind of line;
     ROLLBACK: the jar of 0.4.5 (isolated class loader) reads the migrated file and a 0.5 bag of 20 slots, rewrites its 9-slot file, and
     0.5 still finds slots 10-20 in the second file; the kit's RELOAD path (load(false)) clamps hand edits; the check= hook
  P  PAGE: the real build() (the script's ACC PAGE block and ACC_BUILD_SRC compiled again into a probe class; only the engine-state
     lines swapped) against acc_page_state() command for command, for the bag at 18 and at 60 slots on every page, clamped page
     numbers, a lowered limit, the inventory pager, empty / retired / profile / Campfire states; SUI.check_page + assert_proven on each
  C  infoColor on every result text handleDataEvent sets; D safe() on ItemIds; E text fit (client font tables, read-only)
  G  admin give helpers (line names + the old aliases, rarity words, giveable ids, amounts, acc:fn:give without a player), acc:defs,
     /accessories lines (admins see ids, players never see an old name), the notice's old-bag test + notices file round trip, the give
     arithmetic (AccStore.giveCount: addOrDropItemStack's true = dropped); part 2 review: acc:fn:give's -1 = queued (a give task
     that could not hop is not queued) and one log-once flag each for max Health / Stamina / Mana
  B  PART 2 PUBLISHING: the gear:extra text (highest rarity counts, switched-off lines, combatToGear, whole numbers, key order), the
     publisher's rules on the real bridge (write on change only, remove when empty, a foreign text overwritten once, a second writer
     within 5 s = stop, a non-text = stop, a profile switch resumes, prune on leave removes only our text, shutdown), SkyyGear 0.1 and
     0.1.2's OWN GearStats reading our text (their jars, isolated class loaders), the bag page notes (SkyyGear missing, its combat stats
     switch off, combatToGear off, the back-off, SkyySkills missing for Feather), the movement post (Speed + Feather) read by SkyySkills
     0.4.8's OWN MoveSync (fall multiplier with Acrobatics, jump force), the stat pools on a stat map double that follows the engine's
     computeModifiers rules (bytecode: max = type max + ADDITIVE sum, the current value only clamped): added / unchanged / replaced /
     removed, the current value never eaten, a relog (the saved modifier is kept), and a profile switch (SkyyProfiles' key function
     and epoch on the bridge: the active profile's bag decides the text, the rows and the pools)
  X  class byte-compare notes against the 0.4.5 jar (MoveSync must be identical; the rest is listed)
Not testable without the game: the look, clicks, real inventories, the restamp, the give delivery, the Stamina Regen feel, how the jump
and fall parts feel, SkyyGear's damage maths with our text (its own code, unchanged), the engine's own stat map.
Nothing is deployed and nothing under AppData is written. Default scratch folder: tools/dev/scratch/wbtab/acc (git-ignored),
deleted at the end unless --keep. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyywbtab as WB   # 0.5.2: the Workbench tab tables + harness_checks
VERSION = "0.5.2"
BUILD = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
JAR045 = os.path.join(HERE, "SkyyAccessories-0.4.5.jar")
JAR05 = os.path.join(HERE, "SkyyAccessories-0.5.jar")          # section S (its default file)
JAR051 = os.path.join(HERE, "SkyyAccessories-0.5.1.jar")       # 0.5.2: the SET pin (live) - section Y
SACKS_JAR = os.path.join(ROOT, "SkyySacks", "SkyySacks-0.7.10.jar")   # 0.5.2: section W (the other half of the Workbench tab)
GEAR_JARS = [os.path.join(ROOT, "SkyyGear", "SkyyGear-%s.jar" % v) for v in ("0.1", "0.1.2")]   # 0.1 = the SET pin, 0.1.2 = the newest
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.8.jar")                          # the SET pin (fall damage owner)
LIVE = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData", "Saves", "HUD mod", "mods",
                    "Skyy_SkyyAccessories")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "wbtab", "acc")))
LIVE = os.path.abspath(arg("--live", LIVE))   # section M's source folder (read only; default: the HUD mod world's Skyy_SkyyAccessories)
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


BAD_WORDS = ("Vitality", "Endurance", "Intelligence", "Talisman")


def clean(t):
    t = str(t)
    return not any(w in t for w in BAD_WORDS) and "talisman" not in t.lower()


def script_parts():
    """The class-name constants, CAP / PAGE_ROWS / BONUS_MAX, the page block (ACC PAGE BLOCK START up to the verbatim assert after
    ACC_BUILD_SRC) and the booster table block (BOOSTER TABLE START up to the config section, with the Python id mirror)."""
    src = open(BUILD, encoding="utf8").read()
    consts = {}
    for name in ("PKG", "REF", "UCB", "UEB", "ST", "PLA", "BT", "EVD"):
        m = re.search(r'^%s\s*=\s*"([^"]+)"' % name, src, re.M)
        consts[name] = m.group(1)
    for name in ("CAP", "PAGE_ROWS", "BONUS_MAX", "SLOTS_DEF", "MAIN_SLOTS"):
        consts[name] = int(re.search(r"^%s = (\d+)" % name, src, re.M).group(1))
    a = src.index("# ---- ACC PAGE BLOCK START")
    b = src.index("for _piece in (ACC_TOP_JAVA,")
    ta = src.index("# ---- BOOSTER TABLE START")
    tb = src.index("# ---- 0.5 CONFIG")
    return consts, src[a:b], src[ta:tb]


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
                   classpath=[B.SERVER_JAR, jar, SACKS_JAR, B.JAVASSIST], convertStrings=True)

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

    consts, block, table = script_parts()
    P = consts["PKG"]
    Defs, Store, Page, Cfg = JClass(P + ".AccDefs"), JClass(P + ".AccStore"), JClass(P + ".AccPage"), JClass(P + ".AccCfg")
    Admin, Notice, GiveFn = JClass(P + ".AccAdmin"), JClass(P + ".AccNotice"), JClass(P + ".AccGiveFn")
    Gear, Eff, Move = JClass(P + ".AccGear"), JClass(P + ".AccEffects"), JClass(P + ".MoveSync")
    UUID, ArrayList, Paths = JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.nio.file.Paths")
    SUI.verify(quiet=True)

    def jarr(xs):
        a = JArray(JString)(len(xs))
        for i, v in enumerate(xs):
            a[i] = v
        return a

    def jpath(*p):
        return JClass("java.io.File")(os.path.join(*p)).toPath()

    # ---------------- T. the booster table = the jar's arrays
    tns = {"SUI": SUI, "os": os, "HERE": HERE, "print": lambda *a, **k: None, "BONUS_MAX": consts["BONUS_MAX"]}
    exec(compile(table, BUILD + " [BOOSTER TABLE block]", "exec"), tns)
    BO, ENT, KINDS = tns["BOOSTERS"], tns["ENTRIES"], tns["STAT_KINDS"]
    check(list(Defs.FAMILIES) == [b[0] for b in BO], "T family keys")
    check(list(Defs.LINE_ADMIN) == [b[1] for b in BO] and list(Defs.LINE_NAME) == [b[2] for b in BO], "T admin names + line names")
    check(list(Defs.LINE_IDS) == tns["LINE_IDS"] and list(Defs.LINE_SRC) == tns["LINE_SRC"], "T ids + source words")
    check(list(Defs.ID_WORD) == tns["ID_WORD"] and list(Defs.DISPLAY) == tns["DISPLAY"], "T id words + display rarities")
    check(list(Defs.LEGACY_WORD) == [w for w, t in tns["LEGACY_WORDS"]] and list(Defs.LEGACY_TIER) == [t for w, t in tns["LEGACY_WORDS"]],
          "T legacy words")
    check(list(Defs.AP) == tns["ACC_AP"], "T Accessory Power table")
    check(list(Defs.RARITY_COLOR) == tns["RARITY_COLORS"] and [str(c).lower() for c in list(Defs.RARITY_COLOR)[1:]] ==
          [SUI.RARITY[r].lower() for r in tns["DISPLAY"][1:]], "T rarity colours = the kit's")
    check(list(Defs.E_KEYS) == [e[0] for e in ENT] and list(Defs.E_LINE) == [e[1] for e in ENT], "T config entries")
    check(list(Defs.E_UNIT) == [KINDS[e[2]][0] for e in ENT] and list(Defs.E_WHOLE) == [1 if KINDS[e[2]][1] else 0 for e in ENT] and
          [float(x) for x in Defs.E_CAP] == [float(KINDS[e[2]][2]) for e in ENT], "T units / whole / caps")
    check(list(Cfg.BOOST_DEF) == tns["BOOST_DEF"], "T config defaults")
    bo = [float(x) for x in Defs.BOOST]
    check(len(bo) == 5 * len(ENT) and all(bo[e * 5] == 0.0 and bo[e * 5 + 1:e * 5 + 5] == [float(v) for v in ENT[e][3]] for e in range(len(ENT))),
          "T the live numbers = the table (tier 0 = 0)")
    check(int(Store.CAP) == 60 and int(Store.MAIN) == 9 and int(Store.SLOTS) == 18 and int(Defs.BONUS_MAX) == 12, "T CAP 60 / MAIN 9 / SLOTS 18")
    check(set(KINDS) == {"maxHealth", "maxStamina", "staminaRegen", "manaPct", "manaFloor", "healPct", "speedPct",
                         "str", "mp", "def", "cc", "cd", "fallPct", "jumpPct"},
          "T the allowlist holds only stats with working code (part 1 + part 2): %s" % sorted(KINDS))
    check(list(Defs.E_GEAR) == tns["E_GEAR"] and list(Defs.GEAR_KEYS) == ["cc", "cd", "def", "mp", "str"] and
          sorted(x for x in tns["E_GEAR"] if x) == ["cc", "cd", "def", "mp", "str"], "T gear:extra keys = the allowlist str mp def cc cd")
    check(all(KINDS[k][1] for k in ("str", "mp", "def", "cc", "cd")) and not any(g in tns["E_GEAR"] for g in ("spd", "stam", "dmg", "tdmg")),
          "T combat kinds take whole numbers; never spd / stam / dmg / tdmg")
    ek = dict((e[2], i) for i, e in enumerate(ENT))
    check(int(Defs.E_SPEED) == ek["speedPct"] and int(Defs.E_JUMP) == ek["jumpPct"] and int(Defs.E_FALL) == ek["fallPct"], "T movement entries")
    check(bool(Defs.COMBAT_TO_GEAR) and all(bool(Defs.lineOn(i)) for i in range(len(BO))), "T every line and combatToGear on by default")
    check([b[9] for b in BO] == ["word"] * 5 + ["T"] * 5 and all(b[8] is None for b in BO[5:]), "T part 2 lines: _T ids, no recipes")
    print("T. booster table: %d lines, %d entries, %d ids" % (len(BO), len(ENT), len(tns["LINE_IDS"])))

    # ---------------- F. the fold of the 40 old ids
    ids40 = sorted(set(tns["OLD_IDS"] + tns["LEGACY_IDS"]))
    check(len(ids40) == 40, "F 25 + 15 old ids: %d" % len(ids40))
    for i in ids40:
        t = tns["py_tier"](i)
        li = [b[0] for b in BO].index(tns["py_family"](i))
        ok = (int(Defs.tierOf(i)) == t and str(Defs.familyOf(i)) == tns["py_family"](i) and bool(Defs.isLegacy(i)) == tns["py_legacy"](i)
              and str(Defs.modernOf(i)) == tns["py_modern"](i) and int(Defs.rarityOf(i)) == t and str(Defs.rarityName(i)) == tns["DISPLAY"][t]
              and str(Defs.pretty(i)) == "%s %s Accessory" % (tns["DISPLAY"][t], BO[li][2]) and str(Defs.groupOf(i)) == "T:" + BO[li][0])
        check(ok, "F %s -> tier %d %s (%s)" % (i, t, tns["DISPLAY"][t], Defs.pretty(i)))
        check(clean(Defs.pretty(i)) and clean(Defs.rarityName(i)), "F no old name in the name of " + i)
    check(str(Defs.modernOf("Skyy_Talisman_Speed_Legendary")) == "Skyy_Talisman_Speed_Epic" and int(Defs.tierOf("Skyy_Talisman_Speed_Legendary")) == 4,
          "F the old fifth id folds into _Epic (Legendary)")
    check(int(Defs.tierOf("Skyy_Talisman_Strength_T3")) == 3 and str(Defs.familyOf("Skyy_Talisman_Strength_T3")) == "Strength" and
          not bool(Defs.isLegacy("Skyy_Talisman_Strength_T3")) and int(Defs.tailTier("Skyy_Talisman_Strength_T3")) == 3, "F part 2 _T<n> ids parse")
    # part 2: the 20 new ids through the jar's id rules = the Python mirror; they are booster ids, never legacy, never bench ids
    for i in tns["NEW_IDS"]:
        t = tns["py_tier"](i)
        li = [b[0] for b in BO].index(tns["py_family"](i))
        ok = (int(Defs.tierOf(i)) == t and int(Defs.tailTier(i)) == t and str(Defs.familyOf(i)) == BO[li][0] and not bool(Defs.isLegacy(i))
              and str(Defs.modernOf(i)) == i and int(Defs.rarityOf(i)) == t and str(Defs.pretty(i)) == "%s %s Accessory" % (tns["DISPLAY"][t], BO[li][2])
              and str(Defs.groupOf(i)) == "T:" + BO[li][0] and bool(Defs.isBoosterId(i)) and Defs.benchOf(i) is None and
              str(Defs.idOf(li, t)) == i and int(Defs.familyIndex(Defs.familyOf(i))) == li)
        check(ok, "F part 2 %s -> %s (%s)" % (i, tns["DISPLAY"][t], Defs.pretty(i)))
    check(len(tns["NEW_IDS"]) == 20 and int(len(list(Defs.LINE_IDS))) == 40, "F 20 folded + 20 new booster ids")
    for bid, r in (("Skyy_Accessory_Workbench_T1", 1), ("Skyy_Accessory_Workbench_T2", 2), ("Skyy_Accessory_Workbench_T3", 3),
                   ("Skyy_Accessory_Farmingbench_T4", 4), ("Skyy_Accessory_Farmingbench_T7", 4), ("Skyy_Accessory_Omni", 4),
                   ("Skyy_Accessory_Alchemybench_T2", 0), ("Skyy_Accessory_Bag", 0)):
        check(int(Defs.rarityOf(bid)) == r, "F rarity of %s = %d (got %d)" % (bid, r, int(Defs.rarityOf(bid))))
    # the equip swap order on a scratch bag (AccStore.equipK = the page's Equip after modernOf)
    Store.DIR = jpath(SCRATCH, "fold", "bags")
    u = UUID.randomUUID()
    k = str(u)
    tal = lambda f, w: "Skyy_Talisman_%s_%s" % (f, w)
    check(str(Store.equipK(u, k, tal("Vitality", "Common"))) == "", "F equip Normal Health into a free slot")
    check(str(Store.equipK(u, k, tal("Vitality", "Uncommon"))) == tal("Vitality", "Common"), "F Unique swaps in, Normal comes back")
    check(Store.equipK(u, k, tal("Vitality", "Common")) is None, "F a lower rarity is refused")
    put = str(Defs.modernOf(tal("Vitality", "Legendary")))
    check(put == tal("Vitality", "Epic") and str(Store.equipK(u, k, put)) == tal("Vitality", "Uncommon"), "F the old _Legendary is stored as _Epic")
    check(not bool(Store.canEquipK(u, k, str(Defs.modernOf(tal("Vitality", "Legendary"))))) and Store.equipK(u, k, tal("Vitality", "Epic")) is None,
          "F _Epic and the old _Legendary tie: the second one is refused")
    check(not bool(Store.canEquipK(u, k, tal("Vitality", "Artifact"))), "F an old Artifact (Legendary) ties too")
    check(str(Store.equipK(u, k, tal("Speed", "Rare"))) == "" and list(Store.snapshot(u))[:2] == [tal("Vitality", "Epic"), tal("Speed", "Rare")],
          "F other lines stack")
    # part 2 lines swap the same way (Normal -> Unique swaps, equal / lower refused, Legendary ties)
    check(str(Store.equipK(u, k, "Skyy_Talisman_Strength_T1")) == "" and str(Store.equipK(u, k, "Skyy_Talisman_Strength_T2")) ==
          "Skyy_Talisman_Strength_T1" and Store.equipK(u, k, "Skyy_Talisman_Strength_T2") is None and
          Store.equipK(u, k, "Skyy_Talisman_Strength_T1") is None and not bool(Store.canEquipK(u, k, "Skyy_Talisman_Strength_T2")) and
          bool(Store.canEquipK(u, k, "Skyy_Talisman_Strength_T4")), "F part 2: Brawler Normal -> Unique swaps, equal / lower refused")
    # part 1 review finding 5: compared with the BEST slot of the line, the LOWEST slot swapped out (duplicates from stashK)
    ud = UUID.randomUUID()
    kd = str(ud)
    for it_ in (tal("Vitality", "Common"), tal("Vitality", "Epic"), tal("Endurance", "Common"), tal("Endurance", "Uncommon")):
        Store.stashK(ud, kd, it_)
    check(not bool(Store.canEquipK(ud, kd, tal("Vitality", "Rare"))) and Store.equipK(ud, kd, tal("Vitality", "Rare")) is None and
          list(Store.snapshot(ud))[:2] == [tal("Vitality", "Common"), tal("Vitality", "Epic")],
          "F finding 5: a Rare is refused while a Legendary sits in ANOTHER slot of the line (0.4.5 compared the first slot only)")
    check(bool(Store.canEquipK(ud, kd, tal("Endurance", "Rare"))) and str(Store.equipK(ud, kd, tal("Endurance", "Rare"))) == tal("Endurance", "Common")
          and list(Store.snapshot(ud))[2:4] == [tal("Endurance", "Rare"), tal("Endurance", "Uncommon")],
          "F finding 5: every slot lower -> the LOWEST is swapped out: %r" % list(Store.snapshot(ud))[:4])
    # only the highest rarity of a line counts (a duplicate that slipped in through stashK changes nothing)
    s = jarr([tal("Vitality", "Common"), tal("Vitality", "Epic"), tal("Vitality", "Rare"), tal("Vitality", "Ring"), None,
              tal("Endurance", "Uncommon"), tal("Endurance", "Uncommon"), "Skyy_Talisman_Crit_T1", "Skyy_Talisman_Crit_T3",
              "Skyy_Talisman_Crit_T2"] + [None] * 50)
    best = list(Defs.bestTiers(s))
    check(best[0] == 4 and best[1] == 2 and best[2:8] == [0, 0, 0, 0, 0, 0] and best[8] == 3 and best[9] == 0,
          "F bestTiers takes the maximum per line (folded and part 2): %r" % best)
    bl = [str(x) for x in Defs.bonusRows(s)]
    check(bl[:6] == ["Health", "+24 max Health", "Stamina", "+6 max Stamina, +5% Stamina Regen", "Razorfang", "+6% Crit Chance, +12% Crit Damage"]
          and all(x == "" for x in bl[6:]) and len(bl) == 24, "F bonus rows (key, value): %r" % bl[:6])
    exp = {(0, 1): ["+6 max Health"], (0, 4): ["+24 max Health"], (1, 1): ["+3 max Stamina", "+2.5% Stamina Regen"],
           (1, 4): ["+12 max Stamina", "+10% Stamina Regen"], (2, 1): ["+6% max Mana (at least +1)"], (2, 4): ["+24% max Mana (at least +4)"],
           (3, 1): ["Heals 0.25% max Health every 2 s"], (3, 4): ["Heals 1% max Health every 2 s"], (4, 2): ["+5% Speed"], (4, 3): ["+7.5% Speed"],
           (5, 1): ["+3 Strength"], (5, 4): ["+12 Strength"], (6, 2): ["+6 Magical Power"], (6, 4): ["+12 Magical Power"],
           (7, 3): ["+9 Defense"], (8, 1): ["+2% Crit Chance, +4% Crit Damage"], (8, 4): ["+8% Crit Chance, +16% Crit Damage"],
           (9, 1): ["-10% fall damage, +5% jump height"], (9, 4): ["-40% fall damage, +20% jump height"]}
    for (li, t), want in sorted(exp.items()):
        got = [str(x) for x in Defs.statParts(li, t)]
        check(got == want, "F %s at %s gives %r (want %r)" % (BO[li][1], tns["DISPLAY"][t], got, want))
    # a rider at 0 drops out of its part; the main stat at 0 leaves the rider alone on the line
    cc_e, fa_e = ek["cc"], ek["fallPct"]
    b0 = [float(x) for x in Defs.BOOST]
    b1 = JArray(JClass("float"))(len(b0))
    for i2, x in enumerate(b0):
        b1[i2] = x
    b1[cc_e * 5 + 4] = 0.0
    b1[fa_e * 5 + 4] = 0.0
    Defs.BOOST = b1
    check([str(x) for x in Defs.statParts(8, 4)] == ["+16% Crit Damage"] and [str(x) for x in Defs.statParts(9, 4)] == ["+20% jump height"],
          "F a stat set to 0 drops out of its line's text")
    b1[cc_e * 5 + 4] = float(b0[cc_e * 5 + 4])
    b1[fa_e * 5 + 4] = float(b0[fa_e * 5 + 4])
    Defs.BOOST = b1
    Defs.LINE_MANA = False
    sm = jarr([tal("Intelligence", "Rare")] + [None] * 59)
    check([str(x) for x in Defs.bonusRows(sm)][:2] == ["Mana", "switched off"] and not bool(Defs.lineOn(2)) and
          list(Defs.activeTiers(sm))[2] == 0 and list(Defs.bestTiers(sm))[2] == 3, "F a switched-off line says so and counts for nothing")
    Defs.LINE_MANA = True
    # a bag file that cannot be read is never overwritten, and the page refuses moves for that bag (AccStore.isBad)
    ub = UUID.randomUUID()
    kb = str(ub)
    bd = os.path.join(SCRATCH, "badbag", "bags")
    os.makedirs(os.path.join(bd, kb + ".properties"))          # a folder where the bag file should be: reading it fails
    Store.DIR = jpath(bd)
    Store.slotsK(ub, kb)
    check(bool(Store.isBad(kb)) and not bool(Store.isBad(str(UUID.randomUUID()))), "F an unreadable bag file is remembered (isBad)")
    Store.stashK(ub, kb, "Skyy_Accessory_Omni")
    check(os.path.isdir(os.path.join(bd, kb + ".properties")) and not os.path.exists(os.path.join(bd, kb + ".more.properties")),
          "F an unreadable bag file is never overwritten")
    print("F. fold: %d old ids, swap order, highest-counts rule, numbers per rarity, unreadable bag file" % len(ids40))

    # ---------------- M. the config migration on a scratch copy of the live data
    # part 1 review finding 2: the live folder is used only while it is still a 0.4.x one; once a 0.5 build started there (boost. lines,
    # a .pre-0.5.bak or a second bag file), a synthetic 0.4.5 folder (the 0.4.4 default file + 0.4.5-style bag files) is used instead
    mdir = os.path.join(SCRATCH, "live")
    use_live = os.path.isdir(LIVE) and os.path.isfile(os.path.join(LIVE, "config.properties")) and "--synthetic" not in sys.argv
    if "--synthetic" in sys.argv:
        live_note = "--synthetic - "
    elif use_live:
        lcfg = parse_props(open(os.path.join(LIVE, "config.properties"), "rb").read().decode("latin-1"))
        lbags = os.path.join(LIVE, "bags")
        if (any(k2.startswith("boost.") for k2 in lcfg) or os.path.exists(os.path.join(LIVE, "config.properties.pre-0.5.bak")) or
                (os.path.isdir(lbags) and any(f.endswith(".more.properties") for f in os.listdir(lbags)))):
            use_live = False
            live_note = "the live folder is already migrated by a 0.5 build - "
        else:
            live_note = ""
    else:
        live_note = "no live folder - "
    if use_live:
        shutil.copytree(LIVE, mdir)
        live_src = "the live HUD mod world"
    else:
        os.makedirs(os.path.join(mdir, "bags"))
        dtext = OLD_045_DEFAULT                  # the file a fresh 0.4.5 server writes (AccCfg.DEFAULT_TEXT of the real jar) when we have it
        if os.path.exists(JAR045):
            u45 = JArray(JClass("java.net.URL"))(2)
            u45[0] = JClass("java.io.File")(JAR045).toURI().toURL()
            u45[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
            l45 = JClass("java.net.URLClassLoader")(u45, JClass("java.lang.ClassLoader").getPlatformClassLoader())
            dtext = str(JClass(P + ".AccCfg", loader=l45).DEFAULT_TEXT)
        open(os.path.join(mdir, "config.properties"), "w", newline="\n").write(dtext)
        for key0, slots0 in (("0a0a0a0a-0000-0000-0000-000000000001", ["Skyy_Talisman_Vitality_Epic", "Skyy_Accessory_Workbench_T2"]),
                             ("0a0a0a0a-0000-0000-0000-000000000002-p2", ["Skyy_Talisman_Speed_Legendary", None, "Skyy_Talisman_Endurance_Ring"])):
            open(os.path.join(mdir, "bags", key0 + ".properties"), "w", newline="\n").write(
                "#SkyyAccessories bag\n" + "".join("slot%d=%s\n" % (i0, v0) for i0, v0 in enumerate(slots0) if v0))
        live_src = live_note + "a synthetic 0.4.5 folder (%s, 2 bag files)" % (
            "0.4.5's own default file" if dtext != OLD_045_DEFAULT else "a 0.4.4 default file")
    cfgf = os.path.join(mdir, "config.properties")
    orig = open(cfgf, "rb").read()
    oprops = parse_props(orig.decode("latin-1"))
    Cfg.FILE = jpath(cfgf)
    Store.DIR = jpath(mdir, "bags")
    r1 = str(Cfg.load(True))
    new = open(cfgf, "rb").read()
    txt = new.decode("latin-1")
    props = parse_props(txt)
    check("updated to 0.5" in r1, "M first start migrates: " + r1[-160:])
    check(not any(k.startswith("bonus.") for k in props), "M no bonus. line left")
    was9 = oprops.get("slots", "").strip() == "9"
    check(props.get("slots") == ("18" if was9 else oprops.get("slots")), "M slots 9 -> 18 (or kept)")
    check(all(props.get("boost." + e[0]) == tns["BOOST_DEF"][i] for i, e in enumerate(ENT)), "M the 14 boost entries (untouched lists = defaults)")
    check(props.get("notice.boosters") == "true" and all(props.get("line." + b[1]) == "true" for b in BO) and props.get("combatToGear") == "true",
          "M notice, 10 line switches, combatToGear")
    check("Talisman bonuses" not in txt and "Vitality" not in txt and ("1-60" in txt) == ("fill, 1-9." in orig.decode("latin-1")),
          "M old comments out, new comment in")
    check(open(cfgf + ".pre-0.5.bak", "rb").read() == orig, "M config.properties.pre-0.5.bak = the old file, byte for byte")
    logf = os.path.join(mdir, "config-changes.log")
    log1 = open(logf, encoding="utf8").read().splitlines()
    rows = [l.split("\t") for l in log1 if "\tmigration-0.5\t" in l]
    add_keys = [str(x) for x in Cfg.ADD_KEY]
    n_bonus = sum(1 for k2 in oprops if k2.startswith("bonus."))
    n_want = (1 if was9 else 0) + n_bonus + sum(1 for k2 in add_keys if k2 not in oprops)   # never hard-coded from live data
    check(len(add_keys) == 1 + len(BO) + 1 + len(ENT), "M the keys a 0.4.x file gets: notice, 10 line switches, combatToGear, 14 entries")
    check(len(rows) == n_want and all(len(r) == 8 and r[1] == "migration-0.5" and r[2] == "-" and r[3] == "migrate" for r in rows),
          "M %d change-log lines in the kit's format (%d)" % (n_want, len(rows)))
    check(rows[0][4:8] == ["slots", "9", "18", "ok"] if was9 else True, "M the slots line: %r" % (rows[0][4:8] if rows else None))
    check(sum(1 for r in rows if r[4].startswith("bonus.")) == n_bonus and
          sum(1 for r in rows if r[4].startswith("boost[")) == len(ENT), "M %d bonus lines + 14 new boost entries logged" % n_bonus)
    check(int(Store.SLOTS) == int(props["slots"]) and bool(Defs.NOTICE) and all(bool(Defs.lineOn(i)) for i in range(len(BO))), "M the running values")
    r2 = str(Cfg.load(True))
    check(open(cfgf, "rb").read() == new and open(logf, encoding="utf8").read().splitlines() == log1 and
          open(cfgf + ".pre-0.5.bak", "rb").read() == orig and "updated" not in r2, "M second start = no change")
    open(cfgf, "wb").write(new.replace(b"slots=18", b"slots=9"))
    Cfg.load(True)
    check(parse_props(open(cfgf, "rb").read().decode("latin-1")).get("slots") == "9" and int(Store.SLOTS) == 9, "M a later slots=9 stays 9")
    open(cfgf, "wb").write(new)
    Cfg.load(True)
    bag_files = sorted(f for f in os.listdir(os.path.join(mdir, "bags")) if f.endswith(".properties"))
    for f in bag_files:
        key = f[:-len(".properties")]
        want = parse_props(open(os.path.join(mdir, "bags", f), "rb").read().decode("latin-1"))
        sl = list(Store.slotsK(UUID.randomUUID(), key))
        check(len(sl) == 60 and all(sl[i] == want.get("slot%d" % i) for i in range(9)) and all(x is None for x in sl[9:]),
              "M live bag %s reads the same 9 slots (+51 empty)" % f)
    print("M1. live copy (%s): %d config lines, %d bag files, %d log lines" % (live_src, len(txt.splitlines()), len(bag_files), len(rows)))
    # edited lists, continuation lines, CRLF, neither kind of line
    cases = [
        ("edited", "slots=5\nbonus.Vitality=5,5,5,5,5\nbonus.Endurance=2,4,6,8,10\nbonus.Intelligence=3,6,9,12,15\n"
                   "bonus.Regeneration=0.5,1,1.5,2,150\nbonus.Speed=1,2\n",
         {"slots": "5", "boost.Mana.pct": "3,6,9,15", "boost.Regeneration.pct": "0.5,1,1.5,100", "boost.Speed.pct": "2.5,5,7.5,10",
          "boost.Health.flat": "6,12,18,24"},
         [("bonus.Vitality", "invalid"), ("bonus.Endurance", "done"), ("bonus.Intelligence", "done"), ("bonus.Regeneration", "done"),
          ("bonus.Speed", "invalid")]),
        ("continued", "slots=9\nbonus.Speed=1,2,\\\n   3,4,5\n# keep me\nregenEverySeconds=3\n", {"slots": "18", "boost.Speed.pct": "1,2,3,5",
                                                                                            "regenEverySeconds": "3"}, [("bonus.Speed", "done")]),
        ("crlf", "slots=9\r\nbonus.Vitality=2,4,6,8,10\r\n", {"slots": "18"}, [("bonus.Vitality", "done")]),
        ("neither", "slots=7\n", {"slots": "7", "boost.Stamina.regenPct": "2.5,5,7.5,10", "line.Speed": "true", "combatToGear": "true",
                                  "boost.Feather.fallPct": "10,20,30,40"}, []),
    ]
    for name, text, want, logwant in cases:
        d = os.path.join(SCRATCH, "mig-" + name)
        os.makedirs(d)
        f = os.path.join(d, "config.properties")
        open(f, "wb").write(text.encode("latin-1"))
        Cfg.FILE = jpath(f)
        res = str(Cfg.load(True))
        out = open(f, "rb").read().decode("latin-1")
        pr = parse_props(out)
        check(all(pr.get(k2) == v for k2, v in want.items()), "M %s: %r" % (name, dict((k2, pr.get(k2)) for k2 in want)))
        check(not any(k2.startswith("bonus.") for k2 in pr) and "updated to 0.5" in res and os.path.exists(f + ".pre-0.5.bak"), "M %s migrated" % name)
        lrows = [l.split("\t") for l in open(os.path.join(d, "config-changes.log"), encoding="utf8").read().splitlines()]
        got = [(r[4], r[7]) for r in lrows if r[4].startswith("bonus.")]
        check(got == logwant, "M %s log statuses %r" % (name, got))
        if name == "edited":
            lr = dict((r[4], r[6]) for r in lrows)
            check("the 4th, 12, is dropped" in lr.get("bonus.Intelligence", "") and "capped at 100" in lr.get("bonus.Regeneration", "")
                  and "set boost.Health.flat by hand" in lr.get("bonus.Vitality", ""), "M edited: the log explains each value")
        if name == "crlf":
            check("\r\n" in out and "\n" not in out.replace("\r\n", ""), "M CRLF file stays CRLF")
        if name == "continued":
            check("   3,4,5" not in out and "# keep me" in out, "M a continued bonus line leaves with its continuation, comments stay")
        res2 = str(Cfg.load(True))
        check(open(f, "rb").read().decode("latin-1") == out and "updated" not in res2, "M %s second start = no change" % name)
    # part 2: a server that ran PART 1 (its file has the 7 part 1 boost. entries and 5 line switches, slots 9 set by hand): only the
    # missing 0.5 keys are appended - no slots change, nothing removed, no .bak, logged; the second start changes nothing
    d = os.path.join(SCRATCH, "mig-part1")
    os.makedirs(d)
    f = os.path.join(d, "config.properties")
    p1 = ("slots=9\nregenEverySeconds=2\nnotice.boosters=false\n" + "".join("line.%s=true\n" % b[1] for b in BO[:5]) +
          "".join("boost.%s=%s\n" % (e[0], tns["BOOST_DEF"][i]) for i, e in enumerate(ENT[:7])).replace("boost.Speed.pct=2.5,5,7.5,10",
                                                                                                           "boost.Speed.pct=1,2,3,4") +
          "bonus.Speed=9,9,9,9,9\n")
    open(f, "wb").write(p1.encode("latin-1"))
    Cfg.FILE = jpath(f)
    res = str(Cfg.load(True))
    out = open(f, "rb").read().decode("latin-1")
    pr = parse_props(out)
    check(out.startswith(p1) and "missing 0.5 settings added" in res and not os.path.exists(f + ".pre-0.5.bak"),
          "M part 1 file: only appended, no .bak: " + res[-100:])
    check(pr.get("slots") == "9" and pr.get("boost.Speed.pct") == "1,2,3,4" and pr.get("notice.boosters") == "false" and
          pr.get("bonus.Speed") == "9,9,9,9,9", "M part 1 file: slots 9, an edited entry, the switches and a stray bonus. line stay")
    check(all(pr.get("boost." + e[0]) == tns["BOOST_DEF"][i] for i, e in enumerate(ENT) if i >= 7) and
          all(pr.get("line." + b[1]) == "true" for b in BO[5:]) and pr.get("combatToGear") == "true", "M part 1 file: the 13 part 2 keys added")
    lrows = [l.split("\t") for l in open(os.path.join(d, "config-changes.log"), encoding="utf8").read().splitlines()]
    check(len(lrows) == 13 and not any(r[4] in ("slots",) or r[4].startswith("bonus.") for r in lrows), "M part 1 file: 13 log lines, "
          "no slots / bonus lines: %r" % [r[4] for r in lrows])
    res2 = str(Cfg.load(True))
    check(open(f, "rb").read().decode("latin-1") == out and "added" not in res2 and int(Store.SLOTS) == 9 and not bool(Defs.NOTICE),
          "M part 1 file: second start = no change")
    Defs.NOTICE = True
    # the kit's RELOAD path clamps hand edits; the check= hook
    d = os.path.join(SCRATCH, "reload")
    os.makedirs(d)
    f = os.path.join(d, "config.properties")
    open(f, "w", newline="\n").write("slots=99\nregenEverySeconds=0\nboost.Health.flat=1,2,3\nboost.Speed.pct=150,1,2,3\n"
                                     "line.Mana=false\nnotice.boosters=off\nboost.Mana.floor=0,0,0,0\n")
    Cfg.FILE = jpath(f)
    res = str(Cfg.reload())
    b2 = [float(x) for x in Defs.BOOST]
    e = dict((x[0], i) for i, x in enumerate(ENT))
    check(int(Store.SLOTS) == 60 and int(Defs.REGEN_EVERY) == 1, "M reload clamps slots 99 -> 60 and regen 0 -> 1")
    check(b2[e["Health.flat"] * 5 + 1:e["Health.flat"] * 5 + 5] == [6.0, 12.0, 18.0, 24.0], "M a boost line that is not 4 numbers -> built-in")
    check(b2[e["Speed.pct"] * 5 + 1:e["Speed.pct"] * 5 + 5] == [100.0, 1.0, 2.0, 3.0], "M a boost number above the cap -> the cap")
    check(not bool(Defs.lineOn(2)) and not bool(Defs.NOTICE) and "lines switched off: Mana" in res, "M line + notice switches read: " + res[-120:])
    sm2 = jarr([tal("Intelligence", "Rare")] + [None] * 59)
    Defs.LINE_MANA = True
    check([str(x) for x in Defs.statParts(2, 3)] == ["+18% max Mana"], "M Mana floor 0 -> the '(at least)' part goes away")
    ck = Cfg.checkBoost
    check(ck("boost[Health.flat]", "6,12,18,24") is None and ck("boost[Speed.pct]", "1,2,3,100") is None, "M check: valid entries pass")
    for key2, val, bit in (("boost[Health.flat]", "1,2,3", "Needs 4 numbers"), ("boost[Speed.pct]", "1,2,3,101", "from 0 to 100"),
                           ("boost[Health.flat]", "1,2,3,1001", "from 0 to 1000"), ("boost[Nope.flat]", "1,2,3,4", "Unknown entry"),
                           ("boost[Health.flat]", None, "stays"), ("boost[Health.flat]", "1,-2,3,4", "Needs 4 numbers")):
        r = ck(key2, val)
        check(r is not None and bit in str(r) and clean(r), "M check refuses %s=%r: %s" % (key2, val, r))
    # ROLLBACK: the 0.4.5 jar next to the migrated data
    if os.path.exists(JAR045):
        URL = JArray(JClass("java.net.URL"))(2)
        URL[0] = JClass("java.io.File")(JAR045).toURI().toURL()
        URL[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
        l045 = JClass("java.net.URLClassLoader")(URL, JClass("java.lang.ClassLoader").getPlatformClassLoader())
        Cfg45, Store45 = JClass(P + ".AccCfg", loader=l045), JClass(P + ".AccStore", loader=l045)
        check(int(Store45.CAP) == 9, "R the isolated loader really holds 0.4.5 (CAP 9)")
        Cfg45.FILE = jpath(cfgf)
        before = open(cfgf, "rb").read()
        r45 = str(Cfg45.load(False))
        check(int(Store45.SLOTS) == 9 and open(cfgf, "rb").read() == before and "talisman bonuses built-in" in r45,
              "R 0.4.5 reads the migrated file: " + r45)
        rb = os.path.join(SCRATCH, "rollback", "bags")
        Store.DIR = jpath(rb)
        Store45.DIR = jpath(rb)
        u2 = UUID.randomUUID()
        k2 = str(u2)
        items = ["Skyy_Accessory_Workbench_T%d" % (1 + (i % 3)) for i in range(20)]
        check(all(bool(Store.stashK(u2, k2, it)) for it in items), "R 0.5 fills 20 slots")
        main = parse_props(open(os.path.join(rb, k2 + ".properties"), "rb").read().decode("latin-1"))
        more = parse_props(open(os.path.join(rb, k2 + ".more.properties"), "rb").read().decode("latin-1"))
        check(sorted(main) == sorted("slot%d" % i for i in range(9)) and sorted(more) == sorted("slot%d" % i for i in range(9, 20)),
              "R 0.5 splits 20 slots: 9 in the main file, 11 in the second")
        s45 = list(Store45.slotsK(u2, k2))
        check(len(s45) == 9 and s45 == items[:9], "R 0.4.5 sees the first 9 slots")
        check(str(Store45.unequipK(u2, k2, 0)) == items[0], "R 0.4.5 unequips slot 1 and rewrites its file")
        Store.BAGS.clear()
        s5 = list(Store.slotsK(u2, k2))
        check(s5[0] is None and s5[1:9] == items[1:9] and s5[9:20] == items[9:20] and all(x is None for x in s5[20:]),
              "R back on 0.5: slots 10-20 are still there")
        print("R. rollback: 0.4.5 reads the migrated config and the 9-slot file, never touches the second file")
    else:
        check(False, "R no SkyyAccessories-0.4.5.jar next to the build (build 0.4.5 into it or pass the path)")

    # ---------------- P. the real build() against the kit's acc_page_state()
    ns = dict(consts, SUI=SUI, KIT_ID=SUI.kit_id())
    exec(compile(block, BUILD + " [ACC PAGE block]", "exec"), ns)
    src = ns["ACC_BUILD_SRC"]
    swaps = [("public void build(%s ref, %s b, %s ev, %s st) {" % (consts["REF"], consts["UCB"], consts["UEB"], consts["ST"]),
              "public void build(%s b, %s ev) {" % (consts["UCB"], consts["UEB"])),
             ("  java.util.UUID u = this.playerRef.getUuid();\n", ""),
             ("  %s player = (%s) st.getComponent(ref, %s.getComponentType());\n" % (consts["PLA"], consts["PLA"], consts["PLA"]), ""),
             ("  this.key = %s.AccStore.pkey(u);   // 0.4.1\n" % P, ""),
             ("String[] s = %s.AccStore.snapshot(u);" % P, "String[] s = this.snap;"),
             ("%s.AccGear.pageRows(s, u);" % P, "%s.AccGear.pageRows(s, null);" % P),
             ("java.util.ArrayList inv = player == null ? new java.util.ArrayList() : carried(player);", "java.util.ArrayList inv = this.inv;")]
    for a, b in swaps:
        check(src.count(a) == 1, "probe swap anchor once in build(): " + a.strip()[:70])
        src = src.replace(a, b)
    src, n1 = re.subn(r"(?<![\w.])safe\(", P + ".AccPage.safe(", src)
    src, n2 = re.subn(r"(?<![\w.])infoColor\(", P + ".AccPage.infoColor(", src)
    check(n1 == 2 and n2 == 1, "build() calls safe() twice (the 2 ItemIds) and infoColor() once: %d / %d" % (n1, n2))
    check(not any(x in src for x in ("playerRef", "player", "carried(", " st.", "(u)")), "probe: no engine state left in build()")
    pool = JClass("javassist.ClassPool")(True)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    cc = pool.makeClass("skyytest.AccRenderProbe05")
    for fsrc in ("public String info;", "public String[] invIds;", "public String[] snap;", "public java.util.ArrayList inv;",
                 "public int slotPage;", "public int invPage;"):
        cc.addField(CtField.make(fsrc, cc))
    cc.addConstructor(CtNewConstructor.defaultConstructor(cc))
    cc.addMethod(CtNewMethod.make(src, cc))
    out = os.path.join(SCRATCH, "probe-classes")
    os.makedirs(out, exist_ok=True)
    cc.writeFile(out)
    URL = JArray(JClass("java.net.URL"))(1)
    URL[0] = JClass("java.io.File")(out).toURI().toURL()
    Probe = JClass("skyytest.AccRenderProbe05", loader=JClass("java.net.URLClassLoader")(URL, loader))
    UCB, UEB = JClass(consts["UCB"]), JClass(consts["UEB"])
    JRE = SUI._J_RE
    PR_ = consts["PAGE_ROWS"]
    Store.SLOTS = consts["SLOTS_DEF"]

    def java_state(snap, lim, inv, info, sp, ip):
        Store.SLOTS = lim
        p = Probe()
        p.snap = jarr(snap)
        lst = ArrayList()
        for v in inv:
            lst.add(v)
        p.inv = lst
        p.info = info
        p.slotPage = sp
        p.invPage = ip
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
        Store.SLOTS = consts["SLOTS_DEF"]
        return cmds, evs, ids, int(p.slotPage), int(p.invPage)

    def upper(t):
        assert all(ord(c) < 128 for c in str(t)), t
        return str(t).upper()

    def row(i):
        return (SUI.J("v.item", str(Page.safe(i))), SUI.J("v.name", str(Defs.pretty(i))), SUI.J("v.rarity", upper(Defs.rarityName(i))),
                SUI.J("v.colour", str(Defs.rarityColor(i))))

    def expected(snap, lim, inv, info, sp, ip):
        s = jarr(snap)
        Store.SLOTS = lim
        cap = int(Store.capOf(s))
        Store.SLOTS = consts["SLOTS_DEF"]
        shown = [i for i, v in enumerate(snap) if not (i >= cap and v is None)]
        used = sum(1 for v in snap if v is not None)
        pages = max(1, int(math.ceil(len(shown) / float(PR_))))
        sp = min(max(sp, 0), pages - 1)
        ipages = max(1, int(math.ceil(len(inv) / float(PR_))))
        ip = min(max(ip, 0), ipages - 1)
        page_slots = shown[sp * PR_:(sp + 1) * PR_]
        page_inv = list(range(ip * PR_, min(len(inv), (ip + 1) * PR_)))
        bonus = str(Defs.bonusText(s))
        bl = [str(x) for x in Gear.pageRows(s, None)]
        shown_info = info if info else str(Store.campLine(s))
        head = "Bag slots - %d of %d used" % (used, cap)
        scap, icap = "Page %d / %d" % (sp + 1, pages), "Page %d / %d" % (ip + 1, ipages)
        chunks = ns["acc_page_state"](SUI.J("v.bonus", bonus), [(SUI.J("v.bk", bl[2 * k2]), SUI.J("v.bv", bl[2 * k2 + 1]))
                                                                for k2 in range(consts["BONUS_MAX"])], SUI.J("v.info", shown_info),
                                      SUI.J("v.head", head), (SUI.J("v.scap", scap), sp > 0, sp < pages - 1),
                                      (SUI.J("v.icap", icap), ip > 0, ip < ipages - 1),
                                      [(i, None if snap[i] is None else row(snap[i])) for i in page_slots], [(i, row(inv[i])) for i in page_inv],
                                      len(inv))
        ns["acc_page_check"](chunks)
        colour = str(Page.infoColor(info))

        def res(v):
            def sub(m):
                if m.group(1) == ns["ACC_INFO_COLOR"]:
                    return colour
                if m.group(1).startswith("v."):
                    return m.group(2)
                raise AssertionError("unresolved runtime value in the kit markup: " + m.group(1))
            return JRE.sub(sub, v)
        cmds = []
        for ch in chunks:
            for parent, mk in ch:
                cmds.append(("AppendInline", None if parent is None else "#" + parent, res(mk)))
            for ident, prop, val in ch.sets:
                cmds.append(("Set", "#%s.%s" % (ident, prop), res(val)))
        evs = [("Activating", "#SkyyAccUn%d" % i, '{"a": "un:%d"}' % i, True) for i in page_slots if snap[i] is not None]
        evs += [("Activating", "#SkyyAccEq%d" % i, '{"a": "eq:%d"}' % i, True) for i in page_inv]
        evs += [("Activating", "#SkyyAcc%s" % x, '{"a": "%s"}' % y, True) for x, y in (("SpPrev", "sp:prev"), ("SpNext", "sp:next"),
                                                                                      ("IpPrev", "ip:prev"), ("IpNext", "ip:next"))]
        return cmds, evs, list(inv), shown_info, bonus, sp, ip, head, scap, icap, bl

    N = None
    full60 = []
    for bench in ("Workbench", "Furnace", "Tannery", "Armor_Bench", "Weapon_Bench"):
        full60.append("Skyy_Accessory_%s_T1" % bench)
    full60 += tns["LINE_IDS"]
    full60 += list(tns["LEGACY_IDS"][:10]) + ["Skyy_Accessory_Omni", "Skyy_Accessory_Campfire_T1", "Skyy_Accessory_Alchemybench_T1"]
    full60 += ["Skyy_Accessory_Farmingbench_T%d" % t for t in range(1, 8)]
    full60 += ["Skyy_Accessory_Loombench_T1"] * (60 - len(full60))
    full60 = full60[:60]
    inv20 = ["Skyy_Accessory_Furnace_T1", tal("Speed", "Epic"), "Skyy_Accessory_Workbench_T1", tal("Intelligence", "Artifact")] + \
        [tns["LINE_IDS"][i] for i in range(16)]
    base18 = [tal("Vitality", "Epic"), tal("Endurance", "Rare"), N, "Skyy_Accessory_Omni"] + [N] * 56
    why = "bag is full, or the same or a better Health Accessory is already equipped"
    states = [
        ("18 slots page 1", base18, 18, inv20, "equipped Legendary Speed Accessory", 0, 0),
        ("18 slots page 2", base18, 18, inv20[:3], "", 1, 0),
        ("18 slots, page 99 clamps to 2", base18, 18, [], "", 99, 5),
        ("60 slots full, page 1", full60, 60, inv20, "", 0, 0),
        ("60 slots full, page 4", full60, 60, inv20, why, 3, 1),
        ("60 slots full, page 7 (last)", full60, 60, inv20, "", 6, 2),
        ("60 slots full, limit 18 (all shown)", full60, 18, [], "your inventory is full", 6, 0),
        ("empty bag, nothing carried", [N] * 60, 18, [], "", 0, 0),
        ("limit 5, slot 7 filled above it", [tal("Speed", "Rare"), N, "Skyy_Accessory_Workbench_T2", N, N, N, N, tal("Vitality", "Epic")] + [N] * 52,
         5, ["Skyy_Accessory_Furnace_T1", tal("Endurance", "Common")], "your inventory is full", 0, 0),
        ("campfire line", ["Skyy_Accessory_Campfire_T1"] + [N] * 59, 18, [], "", 0, 0),
        ("retired only", [N, "Skyy_Accessory_Alchemybench_T2"] + [N] * 58, 18, ["Skyy_Accessory_Alchemybench_T1", "Skyy_Accessory_Cookingbench_T1"],
         str(Defs.retiredWhy("Skyy_Accessory_Alchemybench_T1")), 0, 0),
        ("profile switched note", [tal("Speed", "Epic")] + [N] * 59, 18, [tal("Speed", "Rare")],
         "your profile changed - this is the bag of your current profile now", 0, 0),
        ("60 slots in 60, 3 filled at the end", [N] * 57 + [tal("Speed", "Common"), N, tal("Regeneration", "Epic")], 60, [], "", 6, 0),
    ]
    total_cmds = 0
    for name, snap, lim, inv, info, sp, ip in states:
        got, gev, gids, gsp, gip = java_state(snap, lim, inv, info, sp, ip)
        exp, eev, eids, shown, bonus, esp, eip, head, scap, icap, bl = expected(snap, lim, inv, info, sp, ip)
        total_cmds += len(got)
        same = got == exp
        if not same:
            for k3 in range(max(len(got), len(exp))):
                g = got[k3] if k3 < len(got) else None
                e2 = exp[k3] if k3 < len(exp) else None
                if g != e2:
                    print("  first difference at command %d:\n    build(): %r\n    kit    : %r" % (k3, g, e2))
                    break
        check(same, "P %s: build() = acc_page_state() (%d / %d commands)" % (name, len(got), len(exp)))
        check(gev == eev, "P %s: events %r" % (name, gev[-6:]))
        check(gids == eids, "P %s: invIds" % name)
        check((gsp, gip) == (esp, eip), "P %s: page numbers clamped to %d / %d (got %d / %d)" % (name, esp, eip, gsp, gip))
        sets = dict((sel, v) for typ, sel, v in got if typ == "Set")
        check(sets.get("#SkyyAccInfo.Text") == shown and sets.get("#SkyyAccBonus.Text") == bonus and sets.get("#SkyyAccSlotsH.Text") == head
              and sets.get("#SkyyAccSpPage.Text") == scap and sets.get("#SkyyAccIpPage.Text") == icap, "P %s: texts" % name)
        check(all(clean(v) for typ, sel, v in got if typ == "Set" and not sel.endswith("Ic.ItemId")), "P %s: no old name on the page" % name)
        for typ, sel, v in got:
            if typ == "AppendInline":
                try:
                    SUI.check_markup(v, ns["ACC_PREFIX"], root=sel is None)
                    OKS[0] += 1
                except Exception as ex:
                    check(False, "P %s: check_markup %s: %s" % (name, sel, ex))
        if name == "60 slots full, page 4":
            check(sum(1 for typ, sel, v in got if typ == "AppendInline" and sel == "#SkyyAccSlotRows") == PR_ and
                  any(sel == "#SkyyAccSlot27" for typ, sel, v in got), "P page 4 of 60 draws slots 28-36")
        if name == "campfire line":
            check(sets.get("#SkyyAccInfo.Text", "").startswith("Campfire quick cook"), "P the Campfire line shows while no result is set")
    print("P. %d states, %d engine commands compared with the kit's output" % (len(states), total_cmds))

    # ---------------- C. infoColor on the real result texts
    OK, NO, EQ = SUI.STATUS["+"], SUI.STATUS["-"], SUI.STATUS["="]
    pv, pe = str(Defs.pretty(tal("Vitality", "Epic"))), str(Defs.pretty(tal("Vitality", "Uncommon")))
    bridge = Store.bridge()
    uu = UUID.randomUUID()
    check(Store.moveBlock(uu) is None, "moveBlock: nothing blocks without SkyyProfiles keys")
    bridge.put("profile:busy:" + str(uu), "1")
    busy = str(Store.moveBlock(uu))
    bridge.remove("profile:busy:" + str(uu))
    bridge.put("profile:fn:key", "x")
    unk = str(Store.moveBlock(uu))
    bridge.remove("profile:fn:key")
    texts = [(None, EQ), ("", EQ), ("your profile changed - this is the bag of your current profile now", EQ),
             (busy, NO), (unk, NO), ("your inventory is full", NO),
             ("your accessory bag file could not be read - nothing was moved, tell an admin (server log)", NO),

             ("unequipped " + pv, OK), ("unequipped " + pv + " - your older copy came back as the current item", OK),
             (str(Defs.retiredWhy("Skyy_Accessory_Alchemybench_T1")), NO), (str(Defs.retiredWhy("Skyy_Accessory_Cookingbench_T1")), NO),
             (why, NO), (why + " - it was kept in a free bag slot", NO), ("could not find " + pv + " in your inventory", NO),
             ("could not give " + pv + " back - inventory and bag full, reported to the server log", NO),
             ("upgraded to " + pv + " - " + pe + " returned", OK), ("upgraded to " + pv + " - " + pe + " kept in the bag - inventory full", OK),
             ("upgraded to " + pv + " - " + pe + " could not be returned - reported to the server log", NO),
             ("equipped " + pv, OK), ("equipped " + pv + " - converted from an older copy", OK)]
    for t, c in texts:
        check(str(Page.infoColor(t)) == c, "C infoColor(%r) = %s" % (t, c))
        check(t is None or clean(t), "C no old name in %r" % t)
    check(str(Defs.lineLabel(tal("Endurance", "Ring"))) == "Stamina Accessory" and str(Defs.lineLabel("Skyy_Accessory_Omni")) == "Omni accessory"
          and str(Defs.lineLabel("Skyy_Accessory_Furnace_T1")) == "bench accessory", "C the refusal names the line")
    print("C. infoColor checked on %d result texts" % len(texts))

    # ---------------- D. safe() still guards the ItemIds written into the markup
    check(str(Page.safe('a,b:c;d{e}"f')) == "a b c d(e) f", "D AccPage.safe unchanged (0.4.4's)")

    # ---------------- G. admin give helpers, acc:defs, /accessories lines, the notice
    for nm, li in (("Health", 0), ("health", 0), ("Vitality", 0), ("Stamina", 1), ("Endurance", 1), ("Intelligence", 2), ("mana", 2),
                   ("Regeneration", 3), ("Speed", 4), ("Strength", 5), ("Brawler", 5), ("MagicPower", 6), ("runic", 6), ("Defense", 7),
                   ("Stonehide", 7), ("Crit", 8), ("Razorfang", 8), ("feather", 9), ("Hawkeye", -1), ("", -1)):
        check(int(Defs.lineOf(nm)) == li, "G lineOf(%r) = %d" % (nm, li))
    for w, t in (("Normal", 1), ("unique", 2), ("Rare", 3), ("LEGENDARY", 4), ("1", 1), ("4", 4), ("5", -1), ("Epic", -1), ("Mythic", -1)):
        check(int(Defs.rarityIndex(w)) == t, "G rarityIndex(%r) = %d" % (w, t))
    check(str(Defs.idOf(1, 4)) == "Skyy_Talisman_Endurance_Epic" and str(Defs.idOf(9, 1)) == "Skyy_Talisman_Feather_T1" and Defs.idOf(10, 1) is None and Defs.idOf(0, 5) is None, "G idOf")
    for gid, ok in ((tal("Speed", "Epic"), True), (tal("Speed", "Legendary"), False), (tal("Speed", "Ring"), False),
                    ("Skyy_Accessory_Workbench_T3", True), ("Skyy_Accessory_Workbench_T4", False), ("Skyy_Accessory_Farmingbench_T7", True),
                    ("Skyy_Accessory_Alchemybench_T1", False), ("Skyy_Accessory_Omni", True), ("Skyy_Accessory_Bag", True),
                    ("Weapon_Sword_Iron", False), ("Skyy_Talisman_Strength_T1", True), ("Skyy_Talisman_Feather_T4", True),
                    ("Skyy_Talisman_Crit_T5", False), ("Skyy_Talisman_Strength_Common", False), ("Skyy_Talisman_Crit_Legendary", False)):
        r = Admin.giveable(gid)
        check((r is None) == ok and (r is None or clean(r)), "G giveable(%s) -> %s" % (gid, r))
    for t, n in (("1", 1), ("64", 64), ("65", -1), ("0", -1), ("x", -1), (" 12 ", 12)):
        check(int(Admin.amountOf(t)) == n, "G amountOf(%r) = %d" % (t, n))
    check(int(Admin.giveFn(UUID.randomUUID(), tal("Speed", "Epic"), 1)) == 0 and int(Admin.giveFn(UUID.randomUUID(), "Weapon_Sword_Iron", 1)) == 0,
          "G acc:fn:give without that player online gives 0")
    Obj = JClass("java.lang.Object")
    argv = JArray(Obj)(3)
    argv[0] = UUID.randomUUID()
    argv[1] = JString(tal("Speed", "Epic"))
    argv[2] = JClass("java.lang.Integer").valueOf(2)
    check(int(GiveFn().apply(argv)) == 0 and int(GiveFn().apply(JString("bad"))) == 0, "G acc:fn:give takes Object[]{UUID, String, Integer}")
    # part 2 review finding 2: off the target's world thread acc:fn:give returns -1 (queued) once world.execute took the give, and 0
    # only when nothing was given AND nothing queued - a retry-on-0 caller can no longer give twice
    GiveTask = JClass(P + ".AccGiveTask")
    gtask = GiveTask(None, None, JString(tal("Speed", "Epic")), 1)
    check(not bool(gtask.queued) and not bool(gtask.onWorld), "G a new give task is not queued")
    gtask.run()
    check(not bool(gtask.queued) and not bool(gtask.onWorld), "G a give task whose player left is not queued (acc:fn:give returns 0 then)")
    gsrc = open(BUILD, encoding="utf8").read()
    gfn_src = gsrc[gsrc.index("public static int giveFn("):gsrc.index("gfn.addInterface(")]
    check(gfn_src.count("return -1;") == 1 and gfn_src.index("gt.run();") < gfn_src.index("if (!gt.queued) {") < gfn_src.index("return -1;")
          and "w.execute(this);\n      this.queued = true;" in gsrc, "G acc:fn:give off the world thread: -1 only after world.execute took it")
    # part 2 review finding 1: max Health, max Stamina and max Mana each have their own log-once flag
    eflags = sorted(str(f.getName()) for f in Cls.forName(P + ".AccEffects", False, loader).getDeclaredFields() if str(f.getName()).startswith("F_"))
    check(eflags == sorted(["F_HEALTH", "F_STAMINA", "F_MANA", "F_STAM", "F_HEAL", "F_MOVE", "F_GEAR", "F_NOTE"]), "G AccEffects log-once flags: %r" % eflags)
    check(all(gsrc.count("if (!%s) { %s = true;" % (f, f)) == 1 for f in eflags) and
          all(gsrc.count("if (!F_%s) { F_%s = true; @PKG@.AccStore.warn(\"max %s from" % (k.upper(), k.upper(), k)) == 1
              for k in ("Health", "Stamina", "Mana")), "G each stat pool logs through its own flag")
    defs = str(Defs.defsText()).split(",")
    check(len(defs) == 4 * len(BO) == 40 and all(len(d.split(":")) == 7 for d in defs), "G acc:defs = 40 records of 7 fields")
    check(defs[3] == "Health:Vitality:4:Skyy_Talisman_Vitality_Epic:Legendary:19:Craft+Boss", "G acc:defs record: " + defs[3])
    check(defs[23] == "Strength:Strength:4:Skyy_Talisman_Strength_T4:Legendary:19:Boss" and
          defs[36] == "Feather:Feather:1:Skyy_Talisman_Feather_T1:Normal:10:Craft", "G acc:defs part 2 records: %s / %s" % (defs[23], defs[36]))
    lp = [str(x) for x in Defs.linesText(False)]
    la = [str(x) for x in Defs.linesText(True)]
    check(len(lp) == len(BO) and all(clean(x) for x in lp), "G /accessories lines for players: no ids, no old names")
    check(lp[1] == "Stamina Accessory (Stamina): Normal +3 max Stamina and +2.5% Stamina Regen | Unique +6 max Stamina and +5% Stamina "
          "Regen | Rare +9 max Stamina and +7.5% Stamina Regen | Legendary +12 max Stamina and +10% Stamina Regen", "G lines text: " + lp[1])
    check(lp[8] == "Razorfang Accessory (Crit): Normal +2% Crit Chance, +4% Crit Damage | Unique +4% Crit Chance, +8% Crit Damage | Rare "
          "+6% Crit Chance, +12% Crit Damage | Legendary +8% Crit Chance, +16% Crit Damage", "G lines text: " + lp[8])
    check(lp[9] == "Feather Accessory (Feather): Normal -10% fall damage, +5% jump height | Unique -20% fall damage, +10% jump height | "
          "Rare -30% fall damage, +15% jump height | Legendary -40% fall damage, +20% jump height", "G lines text: " + lp[9])
    check(len(la) == 2 * len(BO) and la[1] == "    ids: " + " / ".join(tns["LINE_IDS"][0:4]) and
          la[11] == "    ids: " + " / ".join("Skyy_Talisman_Strength_T%d" % t for t in range(1, 5)), "G admins also see the ids")
    # part 1 review finding 1: the give arithmetic (addOrDropItemStack returns TRUE only when it DROPPED the remainder)
    for args, want in (((0, 3, 0, 3), [3, 3, 0, 0]), ((0, 2, 1, 3), [3, 2, 1, 0]), ((0, 0, 3, 3), [3, 0, 3, 0]), ((4, 5, 0, 1), [1, 1, 0, 0]),
                       ((5, 5, 0, 1), [0, 0, 0, 1]), ((2, 1, 0, 1), [0, 0, 0, 1]), ((0, 1, 1, 1), [2, 1, 1, 1])):
        got = [int(x) for x in Store.giveCount(*args)]
        check(got == want, "G giveCount%r = %r (want %r: handed out, arrived, dropped, warn)" % (args, got, want))
    bsrc = open(BUILD, encoding="utf8").read()
    check("if (@SIC@.addOrDropItemStack(st, r, inv.getCombinedStorageHotbarBackpack(), new @IS@(id, 1))) dropped++;" in bsrc and
          "int[] c = giveCount(before, countOf(inv, id), dropped, n);" in bsrc, "G deliver counts the true returns as dropped")
    # part 1 review finding 3: the notice switch is tested BEFORE the player is remembered for the session (and forgotten on leave)
    nsrc = bsrc[bsrc.index("public static void check(@PR@ pr, java.util.UUID u) {"):]
    check(nsrc.index("if (!@PKG@.AccDefs.NOTICE) return;") < nsrc.index("ASKED.put(u, Boolean.TRUE);") < nsrc.index("hasOldBag(u)") and
          "@PKG@.AccNotice.ASKED.keySet().retainAll(online);" in bsrc, "G notice: switch tested first, ASKED pruned on leave")
    ndir = os.path.join(SCRATCH, "live", "bags")
    Store.DIR = jpath(ndir)
    olds = [f[:-11] for f in os.listdir(ndir) if f.endswith(".properties") and not f.endswith(".more.properties")]
    for key in olds:
        check(bool(Notice.hasOldBag(UUID.fromString(key[:36]))), "G notice: a player with a bag file from before (%s) gets it" % key)

    check(not bool(Notice.hasOldBag(UUID.randomUUID())), "G notice: a new player does not")
    open(os.path.join(ndir, "0f0f0f0f-0000-0000-0000-000000000000-p2.properties"), "w").write("slot0=x\n")
    check(bool(Notice.hasOldBag(UUID.fromString("0f0f0f0f-0000-0000-0000-000000000000"))), "G notice: a profile 2 bag counts too")
    open(os.path.join(ndir, "0e0e0e0e-0000-0000-0000-000000000000-p2.more.properties"), "w").write("slot9=x\n")
    check(not bool(Notice.hasOldBag(UUID.fromString("0e0e0e0e-0000-0000-0000-000000000000"))), "G notice: a lone 0.5 second file does not")
    Notice.FILE = jpath(SCRATCH, "notices.properties")
    Notice.SEEN.put("a", "boosters-0.5")
    Notice.SEEN.put("b", "new")
    Notice.DIRTY = True
    Notice.save()
    Notice.SEEN.clear()
    Notice.load()
    check(str(Notice.SEEN.get("a")) == "boosters-0.5" and str(Notice.SEEN.get("b")) == "new", "G notices.properties round trip")
    check("Health, Stamina, Mana, Regeneration and Speed Accessory" in str(Notice.TEXT) and "Vitality" not in str(Notice.TEXT), "G notice text")
    print("G. give helpers, acc:defs, /accessories lines, notice, give arithmetic")

    # ---------------- B. part 2 publishing
    run_publishing(P, consts, tns, BO, ENT, ek, Defs, Store, Gear, Eff, Move, jarr, jpath, UUID)

    # ---------------- E. text fit (client font atlas, read-only)
    fonts = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Client", "Data", "Shared", "UI", "Fonts")
    reg, bold = os.path.join(fonts, "NunitoSans-Medium.json"), os.path.join(fonts, "NunitoSans-ExtraBold.json")
    if os.path.exists(reg) and os.path.exists(bold):
        adv = {}
        for key, path in (("r", reg), ("b", bold)):
            d = json.load(open(path, encoding="utf8"))
            adv[key] = dict((g["unicode"], g["advance"]) for g in d["glyphs"])

        def width(text, size, is_bold=False, up=False):
            a = adv["b" if is_bold else "r"]
            t = text.upper() if up else text
            return sum(a.get(ord(ch), a.get(ord("M"))) for ch in t) * size
        allids = list(ids40) + list(tns["NEW_IDS"])
        for kk in range(len(Defs.BENCH_IDS)):
            for t in range(1, int(Defs.BENCH_MAX[kk]) + 1):
                allids.append("Skyy_Accessory_%s_T%d" % (Defs.BENCH_IDS[kk], t))
        for kk in range(len(Defs.RETIRED)):
            for t in range(1, int(Defs.RETIRED_MAX[kk]) + 1):
                allids.append("Skyy_Accessory_%s_T%d" % (Defs.RETIRED[kk], t))
        allids.append(str(Defs.OMNI))
        tw = ns["ACC_TEXT_W"]
        names = sorted(((width(str(Defs.pretty(i)), SUI.fs(14), True), str(Defs.pretty(i))) for i in allids), reverse=True)
        check(names[0][0] <= tw, "E longest name %r = %.0f px fits the %d px name column" % (names[0][1], names[0][0], tw))
        # the Bonuses well rows: the value = the line's parts joined by ", " (live numbers, up to the caps) or a note; the key = the line
        # name or a note name, bold
        big = [", ".join(str(x) for x in Defs.statParts(li, t)) for li in range(len(BO)) for t in range(1, 5)] + \
            ["switched off", "nothing (its numbers are 0 on this server)", "Heals 100% max Health every 30 s", "+1000 max Health",
             "+100% max Mana (at least +1000)", "+1000 max Stamina, +100% Stamina Regen", "+100% Crit Chance, +100% Crit Damage",
             "-100% fall damage, +100% jump height", "+1000 Magical Power", "not sent - switched off in Server Setup",
             "need SkyyGear, which is not running", "off in SkyyGear (Gear stats in combat)", "paused - another mod writes them (server log)",
             "needs SkyySkills, which is not running"]
        bw = max(width(t, SUI.fs(13)) for t in big)
        check(bw <= ns["ACC_BON_VAL_W"], "E widest bonus value %.0f px fits %d px (%s)" % (bw, ns["ACC_BON_VAL_W"],
                                                                                       max(big, key=lambda t: width(t, SUI.fs(13)))))
        kw = max(width(t, SUI.fs(13), True) for t in [b[2] for b in BO] + ["Combat stats", "Fall damage"])
        check(kw <= ns["ACC_BON_KEY_W"], "E widest bonus key %.0f px fits %d px" % (kw, ns["ACC_BON_KEY_W"]))
        hint = width(ns["ACC_HINT"], 16)
        well_in = 2 * ns["ACC_COL_W"] + ns["ACC_COL_GAP"] - 16
        check(hint <= well_in, "E hint %.0f px fits %d px" % (hint, well_in))
        head = max(width("Bag slots - 60 of 60 used", SUI.fs(13), True, True), width("Accessories in your inventory", SUI.fs(13), True, True))
        check(head <= ns["ACC_COL_IN"] - 2, "E section heads %.0f px fit %d px" % (head, ns["ACC_COL_IN"] - 2))
        capw = width("Page 99 / 99", 16)
        check(capw <= ns["ACC_PG_CAP_W"], "E pager caption %.0f px fits %d px" % (capw, ns["ACC_PG_CAP_W"]))
        check(width("Next >", 14, True, True) <= ns["ACC_PG_BTN_W"] - 2 * SUI.BTN_SMALL_PAD, "E pager buttons fit")
        body = 2 * ns["ACC_COL_W"] + ns["ACC_COL_GAP"]
        longest = names[0][1]
        results = ["upgraded to " + longest + " - " + longest + " could not be returned - reported to the server log",
                   "unequipped " + longest + " - your older copy came back as the current item",
                   "bag is full, or the same or a better Regeneration Accessory is already equipped - it was kept in a free bag slot"]
        res_w = max(width(t, 16, True) for t in results)
        check(res_w <= 2 * body, "E longest result %.0f px fits the two-line result line" % res_w)
        print("E. text fit: name %.0f / %d, bonus value %.0f / %d, key %.0f / %d, hint %.0f / %d, heads %.0f, pager caption %.0f / %d, "
              "result %.0f / %d" % (names[0][0], tw, bw, ns["ACC_BON_VAL_W"], kw, ns["ACC_BON_KEY_W"], hint, well_in, head, capw,
                                    ns["ACC_PG_CAP_W"], res_w, 2 * body))
    else:
        print("E. skipped (no client font atlas)")

    # ---------------- X. class byte-compare notes against the 0.4.5 jar
    if os.path.exists(JAR045):
        za, zb = zipfile.ZipFile(JAR045), zipfile.ZipFile(jar)
        ca = dict((n, za.read(n)) for n in za.namelist() if n.endswith(".class"))
        cb = dict((n, zb.read(n)) for n in zb.namelist() if n.endswith(".class"))
        same = sorted(n for n in ca if n in cb and ca[n] == cb[n])
        changed = sorted(n for n in ca if n in cb and ca[n] != cb[n])
        new_ = sorted(n for n in cb if n not in ca)
        gone = sorted(n for n in ca if n not in cb)
        short = lambda xs: ", ".join(x.split("/")[-1][:-6] for x in xs)
        check("com/skyy/accessories/MoveSync.class" in same, "X MoveSync.class is byte-identical to 0.4.5 (the movement protocol did not change)")
        check(not gone, "X no 0.4.5 class is gone: " + short(gone))
        print("X. byte-compare with 0.4.5: identical %d (%s); changed %d (%s); new %d (%s)" % (len(same), short(same), len(changed),
                                                                                               short(changed), len(new_), short(new_)))

    # ---------------- 0.5.1: H hidden old ids, S the Stamina update + Undo, Y compare with the 0.5 jar
    run_051(P, jar, tns, BO, ENT, Defs, Store, Cfg, jpath, UUID)


def run_051(P, jar, tns, BO, ENT, Defs, Store, Cfg, jpath, UUID):
    """0.5.1: H hidden old ids, S the one-time Stamina update (+ Undo through the real kit), Y compare with the 0.5 jar."""
    import skyybuild as B
    import zipfile
    from jpype import JClass, JArray, JString

    def jobj(*xs):
        a = JArray(JClass("java.lang.Object"))(len(xs))
        for i, v in enumerate(xs):
            a[i] = JString(v) if isinstance(v, str) else v
        return a

    # ---------------- H. the old ids are out of the creative library, still items that map, look and convert as in 0.5
    zb = zipfile.ZipFile(jar)
    items = dict((n.rsplit("/", 1)[1][:-5], json.loads(zb.read(n))) for n in zb.namelist()
                 if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    quals = dict((n.rsplit("/", 1)[1][:-5], json.loads(zb.read(n))) for n in zb.namelist()
                 if n.startswith("Server/Item/Qualities/") and n.endswith(".json"))
    lang = dict(l.split("=", 1) for l in zb.read("Server/Languages/en-US/server.lang").decode("utf8").splitlines() if "=" in l)
    legacy = sorted(tns["LEGACY_IDS"])
    retired = sorted("Skyy_Accessory_%s_T%d" % (str(Defs.RETIRED[k]), t) for k in range(len(Defs.RETIRED))
                     for t in range(1, int(Defs.RETIRED_MAX[k]) + 1))
    hidden = sorted(legacy + retired)
    check(len(legacy) == 20 and len(retired) == 5 and len(set(hidden)) == 25, "H 20 legacy booster ids + 5 retired bench accessories")
    check(sorted(i for i, n in items.items() if "Variant" in n) == hidden, "H exactly the 25 old ids carry Variant: %r" %
          sorted(set(i for i, n in items.items() if "Variant" in n) ^ set(hidden)))
    for i in hidden:
        n = items.get(i, {})
        check(n.get("Variant") is True and "Categories" not in n and "Recipe" not in n and n.get("MaxStack") == 1,
              "H %s: Variant true, no Categories, no Recipe" % i)
    current = sorted(i for i in items if i not in hidden)
    want = set(tns["LINE_IDS"]) | set("Skyy_Accessory_%s_T%d" % (str(Defs.BENCH_IDS[k]), t) for k in range(len(Defs.BENCH_IDS))
                                      for t in range(1, int(Defs.BENCH_MAX[k]) + 1)) | {str(Defs.OMNI), "Skyy_Accessory_Bag"}
    check(set(current) == want and len(current) == 67, "H the current items are the 40 boosters, the bench accessories, Omni and the bag: %r"
          % sorted(set(current) ^ want))
    check(all("Variant" not in items[i] and items[i].get("Categories") == ["Items.Tools"] for i in current), "H the 67 current items stay listed")
    check(len(quals) == 6 and not any("HideFromSearch" in q for q in quals.values()), "H the six qualities hide nothing (shared with current items)")
    check(not any(inp.get("ItemId") in hidden for n in items.values() for inp in (n.get("Recipe") or {}).get("Input", [])),
          "H no recipe takes an old id")
    for i in legacy:
        m = tns["py_modern"](i)
        check(str(Defs.modernOf(i)) == m and bool(Defs.isLegacy(i)) and int(Defs.tierOf(i)) == tns["py_tier"](i) and
              str(Defs.familyOf(i)) == tns["py_family"](i) and str(Defs.pretty(i)) == str(Defs.pretty(m)) and
              str(Defs.groupOf(i)) == str(Defs.groupOf(m)), "H %s still maps to %s (%s)" % (i, m, Defs.pretty(i)))
        check(items[i]["Quality"] == items[m]["Quality"] and items[i]["Icon"] == items[m]["Icon"] and items[i]["Model"] == items[m]["Model"]
              and lang["server.items.%s.name" % i] == lang["server.items.%s.name" % m] == lang["items.%s.name" % i] and
              "An older copy" in lang["server.items.%s.description" % i] and
              lang["server.items.%s.description" % i].split("\\n")[0] == lang["server.items.%s.description" % m].split("\\n")[0],
              "H %s keeps the look, name and tooltip of %s" % (i, m))
    for i in retired:
        check(bool(Defs.isRetired(i)) and "(retired)" in lang["server.items.%s.name" % i], "H %s is still the retired item" % i)
    sd = lang["server.items.Skyy_Talisman_Endurance_Artifact.description"]
    check(sd.startswith('<color is="#ffffff">+12 max Stamina</color> and <color is="#ffffff">+10% Stamina Regen</color>'),
          "H the old Artifact's tooltip prints the 0.5.1 Legendary numbers: " + sd[:90])
    # a legacy stack still converts in the bag: the page's Equip = AccStore.equipK(modernOf(id)), stored as the current id
    Store.DIR = jpath(SCRATCH, "hidden", "bags")
    u = UUID.randomUUID()
    k = str(u)
    put = str(Defs.modernOf("Skyy_Talisman_Endurance_Artifact"))
    check(put == "Skyy_Talisman_Endurance_Epic" and str(Store.equipK(u, k, put)) == "" and list(Store.snapshot(u))[0] == put,
          "H the old Artifact (Skyy saw it twice in creative) equips as the Legendary Stamina Accessory")
    check(Store.equipK(u, k, str(Defs.modernOf("Skyy_Talisman_Endurance_Legendary"))) is None,
          "H an old _Legendary copy ties with it and is refused (0.5 rule)")
    check(str(Store.equipK(u, k, str(Defs.modernOf("Skyy_Talisman_Vitality_Talisman")))) == "" and
          list(Store.snapshot(u))[1] == "Skyy_Talisman_Vitality_Uncommon", "H an old Talisman equips as the Unique Health Accessory")
    brows = [str(x) for x in Defs.bonusRows(Store.snapshot(u))][:4]
    check(brows == ["Health", "+12 max Health", "Stamina", "+12 max Stamina, +10% Stamina Regen"], "H the converted stacks count: %r" % brows)
    # the engine proof (read-only): the Item codec's documentation and Item.toPacket
    icls = zipfile.ZipFile(B.SERVER_JAR).read("com/hypixel/hytale/server/core/asset/type/item/config/Item.class")
    check(b"we filter it out of the item library menu by default, unless the player chooses to display variants" in icls and
          b"A list of categories this item will be shown in on the creative library menu" in icls, "H the Item codec documents Variant + Categories")
    pool = JClass("javassist.ClassPool")(False)
    pool.appendSystemPath()
    pool.appendClassPath(B.SERVER_JAR)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    tp = ""
    for mm in pool.get("com.hypixel.hytale.server.core.asset.type.item.config.Item").getDeclaredMethods():
        if str(mm.getName()) == "toPacket":
            bos = BOS()
            IP(PS(bos)).print_(mm)
            tp += str(bos.toString())
    check("Item.variant(Z)" in tp and "ItemBase.variant(Z)" in tp and "Item.categories(" in tp and "ItemBase.categories(" in tp,
          "H Item.toPacket sends variant and categories to the client")
    cdir = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Client", "Data")
    ui = os.path.join(cdir, "Game", "Interface", "InGame", "Pages", "Inventory", "ItemLibraryPanel.ui")
    cl = os.path.join(cdir, "Shared", "Language", "en-US", "client.lang")
    if os.path.exists(ui) and os.path.exists(cl):
        check("ToggleVariantsButton" in open(ui, encoding="utf8", errors="replace").read() and
              "inventory.itemLibrary.options.showVariants = Show Variants" in open(cl, encoding="utf8", errors="replace").read(),
              "H the client's Item Library has a Show Variants toggle (variants hidden unless it is on)")
        client_note = "client Show Variants toggle found"
    else:
        client_note = "client files not found - toggle not checked"
    print("H. hidden: %d old ids (Variant, no Categories), %d current listed, legacy stacks map + convert, engine proof (%s)" % (
        len(hidden), len(current), client_note))

    # ---------------- S. the 0.5.1 Stamina update (setup()'s order: migrate051, then load(true) = the 0.5 migration + the loader)
    MARK_ID, MARK = str(Cfg.M51_MARK_ID), str(Cfg.M51_MARK)
    OLDV, NEWV = [str(x) for x in Cfg.M51_OLD], [str(x) for x in Cfg.M51_NEW]
    check([str(x) for x in Cfg.M51_KEY] == ["Stamina.flat", "Stamina.regenPct"] and OLDV == ["1.5,3,4.5,6", "5,10,15,20"]
          and NEWV == ["3,6,9,12", "2.5,5,7.5,10"] and str(Cfg.M51_WHO) == "SkyyAccessories 0.5.1", "S the update's data")
    check(MARK in str(Cfg.DEFAULT_TEXT) and "=" not in MARK and MARK.startswith("# " + MARK_ID), "S the 0.5.1 default text carries the marker")
    ef, er = [e[0] for e in ENT].index("Stamina.flat"), [e[0] for e in ENT].index("Stamina.regenPct")

    def nums(e):
        b = [float(x) for x in Defs.BOOST]
        return b[e * 5 + 1:e * 5 + 5]

    def start(fp_):
        Cfg.FILE = jpath(fp_)
        m_ = str(Cfg.migrate051())
        r_ = str(Cfg.load(True))
        return m_, r_

    def hist(d_):
        hd = os.path.join(d_, "config-history")
        return sorted(x for x in os.listdir(hd) if x.endswith(".bak")) if os.path.isdir(hd) else []

    def logl(d_):
        lf = os.path.join(d_, "config-changes.log")
        return open(lf, encoding="utf8").read().splitlines() if os.path.exists(lf) else []

    def expect(text, rows_new, at_key):
        """the Python mirror for the plain files below: the marker above the first line whose key is at_key, the listed lines replaced"""
        out = []
        done = False
        for ln in text.split("\n"):
            body = ln[:-1] if ln.endswith("\r") else ln
            cr = "\r" if ln.endswith("\r") else ""
            if not done and re.match(r"^\s*%s\s*[=:\s]" % re.escape(at_key), body):
                out.append(MARK + cr)
                done = True
            out.append(rows_new.get(body, body) + cr)
        return "\n".join(out)

    # S1: the live folder (a 0.5 folder) or 0.5's own default file, laid out as <mods>/Skyy_SkyyAccessories like a server
    mods = os.path.join(SCRATCH, "s-mods")
    sdir = os.path.join(mods, "Skyy_SkyyAccessories")
    lpath = os.path.join(LIVE, "config.properties")
    ltxt = open(lpath, "rb").read().decode("latin-1") if os.path.isfile(lpath) else ""
    if ltxt and any(k2.startswith("boost.") for k2 in parse_props(ltxt)) and MARK_ID not in ltxt and "--synthetic" not in sys.argv:
        shutil.copytree(LIVE, sdir)
        s_src = "the live HUD mod world (a 0.5 folder)"
    else:
        os.makedirs(sdir)
        txt05 = None
        if os.path.exists(JAR05):
            u5 = JArray(JClass("java.net.URL"))(2)
            u5[0] = JClass("java.io.File")(JAR05).toURI().toURL()
            u5[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
            l5 = JClass("java.net.URLClassLoader")(u5, JClass("java.lang.ClassLoader").getPlatformClassLoader())
            txt05 = str(JClass(P + ".AccCfg", loader=l5).DEFAULT_TEXT)
        check(txt05 is not None, "S no SkyyAccessories-0.5.jar for 0.5's default file")
        open(os.path.join(sdir, "config.properties"), "w", newline="\n").write(txt05 or "")
        s_src = "0.5's own default file (SkyyAccessories-0.5.jar)"
    f = os.path.join(sdir, "config.properties")
    old = open(f, "rb").read()
    otxt = old.decode("latin-1")
    op = parse_props(otxt)
    check(op.get("boost.Stamina.flat", "").replace(" ", "") == "1.5,3,4.5,6" and op.get("boost.Stamina.regenPct", "").replace(" ", "") == "5,10,15,20",
          "S1 the source holds the 0.5 Stamina numbers (%s)" % s_src)
    log0, h0 = logl(sdir), hist(sdir)
    m1, r1 = start(f)
    new = open(f, "rb").read()
    ntxt = new.decode("latin-1")
    want_t = expect(otxt, {"boost.Stamina.flat=1.5,3,4.5,6": "boost.Stamina.flat=3,6,9,12",
                           "boost.Stamina.regenPct=5,10,15,20": "boost.Stamina.regenPct=2.5,5,7.5,10"}, "boost.Stamina.flat")
    check(ntxt == want_t, "S1 only the two Stamina values and one marker line changed (every other byte kept)")
    nl_, ol_ = ntxt.split("\n"), otxt.split("\n")
    check(len(nl_) == len(ol_) + 1 and sum(1 for a in nl_ if a not in ol_) == 3, "S1 diff = 1 marker line + 2 value lines")
    check("updated to the 0.5.1 Stamina defaults: boost.Stamina.flat 1.5,3,4.5,6 -> 3,6,9,12, boost.Stamina.regenPct 5,10,15,20 -> "
          "2.5,5,7.5,10" in m1 and "Changes can undo" in m1, "S1 summary: " + m1[:160])
    h1 = hist(sdir)
    check(len(h1) == len(h0) + 1 and open(os.path.join(sdir, "config-history", h1[-1]), "rb").read() == old,
          "S1 config-history holds the old file byte for byte (%s)" % (h1[-1] if h1 else None))
    idx = open(os.path.join(sdir, "config-history", "index.log"), encoding="utf8").read() if h1 else ""
    stamp = h1[-1][len("Skyy_SkyyAccessories~config.properties."):-4] if h1 else "?"
    check("\tSkyyAccessories 0.5.1\tbefore the 0.5.1 Stamina defaults update" in idx and
          ("Skyy_SkyyAccessories~config.properties#" + stamp) in idx, "S1 index.log names the version (Server Setup -> History)")
    rows = [l.split("\t") for l in logl(sdir)[len(log0):]]
    check(len(rows) == 2 and all(re.match(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$", r[0]) for r in rows) and
          rows[0][1:] == ["SkyyAccessories 0.5.1", "-", "update", "boost[Stamina.flat]", "1.5,3,4.5,6", "3,6,9,12", "ok"] and
          rows[1][1:] == ["SkyyAccessories 0.5.1", "-", "update", "boost[Stamina.regenPct]", "5,10,15,20", "2.5,5,7.5,10", "ok"],
          "S1 two config-changes.log lines in the kit's table format, status ok: %r" % rows)
    check(nums(ef) == [3.0, 6.0, 9.0, 12.0] and nums(er) == [2.5, 5.0, 7.5, 10.0] and "booster numbers built-in" in r1,
          "S1 the loader runs the 0.5.1 numbers: " + r1[:120])
    log1 = logl(sdir)
    m2, r2 = start(f)
    check(m2 == "" and open(f, "rb").read() == new and hist(sdir) == h1 and logl(sdir) == log1, "S1 second start = no change")
    open(f, "wb").write(new.replace(b"boost.Stamina.flat=3,6,9,12", b"boost.Stamina.flat=1.5,3,4.5,6"))
    m3, r3 = start(f)
    check(m3 == "" and b"boost.Stamina.flat=1.5,3,4.5,6" in open(f, "rb").read() and nums(ef) == [1.5, 3.0, 4.5, 6.0] and hist(sdir) == h1,
          "S1 the 0.5 numbers set back by hand later stay (the marker)")
    open(f, "wb").write(new)
    Cfg.load(True)
    print("S1. %s: %d config lines, History %s, %d log lines" % (s_src, len(nl_), h1[-1] if h1 else None, len(rows)))

    # S2: the rules on small files (each in its own folder); (name, text, expected text or None = untouched, summary bits, log rows)
    M = MARK
    BS = chr(92)
    cases = [
        ("custom", "boost.Stamina.flat=2,4,6,8\nboost.Stamina.regenPct=5,10,15,20\nboost.Health.flat=6,12,18,24\n",
         M + "\nboost.Stamina.flat=2,4,6,8\nboost.Stamina.regenPct=2.5,5,7.5,10\nboost.Health.flat=6,12,18,24\n",
         ["boost.Stamina.flat=2,4,6,8 kept (custom) - the 0.5.1 default is 3,6,9,12"], [["boost[Stamina.regenPct]", "5,10,15,20", "2.5,5,7.5,10"]]),
        ("spaced", "slots=18\nboost.Health.flat=6,12,18,24\nboost.Stamina.flat = 1.5, 3, 4.5, 6\nboost.Stamina.regenPct:5,10,15,20.0\n",
         "slots=18\nboost.Health.flat=6,12,18,24\n" + M + "\nboost.Stamina.flat = 3,6,9,12\nboost.Stamina.regenPct:2.5,5,7.5,10\n",
         ["updated to the 0.5.1"], [["boost[Stamina.flat]", "1.5, 3, 4.5, 6", "3,6,9,12"], ["boost[Stamina.regenPct]", "5,10,15,20.0", "2.5,5,7.5,10"]]),
        ("dup-last-default", "boost.Stamina.flat=9,9,9,9\nboost.Stamina.flat=1.5,3,4.5,6\n",
         M + "\nboost.Stamina.flat=9,9,9,9\nboost.Stamina.flat=3,6,9,12\n", ["updated"], [["boost[Stamina.flat]", "1.5,3,4.5,6", "3,6,9,12"]]),
        ("dup-last-custom", "boost.Stamina.flat=1.5,3,4.5,6\nboost.Stamina.flat=9,9,9,9\n",
         M + "\nboost.Stamina.flat=1.5,3,4.5,6\nboost.Stamina.flat=9,9,9,9\n", ["nothing changed", "boost.Stamina.flat=9,9,9,9 kept (custom)"], []),
        ("continued", "boost.Stamina.flat=1.5,3," + BS + "\n  4.5,6\nboost.Stamina.regenPct=5,10,15,20\n",
         M + "\nboost.Stamina.flat=1.5,3," + BS + "\n  4.5,6\nboost.Stamina.regenPct=2.5,5,7.5,10\n",
         ["boost.Stamina.flat=1.5,3,4.5,6 kept (custom)"], [["boost[Stamina.regenPct]", "5,10,15,20", "2.5,5,7.5,10"]]),
        ("crlf", "slots=18\r\nboost.Stamina.flat=1.5,3,4.5,6\r\nboost.Stamina.regenPct=5,10,15,20\r\n",
         "slots=18\r\n" + M + "\r\nboost.Stamina.flat=3,6,9,12\r\nboost.Stamina.regenPct=2.5,5,7.5,10\r\n", ["updated"],
         [["boost[Stamina.flat]", "1.5,3,4.5,6", "3,6,9,12"], ["boost[Stamina.regenPct]", "5,10,15,20", "2.5,5,7.5,10"]]),
        ("crlf-no-final-newline", "slots=18\r\nboost.Stamina.regenPct=5,10,15,20",
         "slots=18\r\n" + M + "\r\nboost.Stamina.regenPct=2.5,5,7.5,10", ["updated"], [["boost[Stamina.regenPct]", "5,10,15,20", "2.5,5,7.5,10"]]),
        ("no-stamina-line", "slots=18\n# Booster numbers\nboost.Health.flat=6,12,18,24\nboost.Speed.pct=1,2,3,4\n",
         "slots=18\n# Booster numbers\n" + M + "\nboost.Health.flat=6,12,18,24\nboost.Speed.pct=1,2,3,4\n", ["nothing changed (0.5.1 Stamina marker added)"], []),
        ("already-0.5.1", "boost.Stamina.flat=3,6,9,12\nboost.Stamina.regenPct=2.5,5,7.5,10\n",
         M + "\nboost.Stamina.flat=3,6,9,12\nboost.Stamina.regenPct=2.5,5,7.5,10\n", ["nothing changed"], []),
        ("marker", "# " + MARK_ID + " (an older note)\nboost.Stamina.flat=1.5,3,4.5,6\n", None, [], []),
        ("not-a-0.5-file", "slots=9\nregenEverySeconds=2\n", None, [], []),
    ]
    for name, text, want_c, bits, want_rows in cases:
        d = os.path.join(SCRATCH, "s2-" + name)
        os.makedirs(d)
        fp = os.path.join(d, "config.properties")
        open(fp, "wb").write(text.encode("latin-1"))
        Cfg.FILE = jpath(fp)
        res = str(Cfg.migrate051())
        out = open(fp, "rb").read().decode("latin-1")
        rws = [l.split("\t")[4:7] for l in logl(d)]
        if want_c is None:
            check(res == "" and out == text and hist(d) == [] and rws == [], "S2 %s: untouched, no History, no log (%r)" % (name, res[:80]))
            continue
        check(out == want_c, "S2 %s: text %r" % (name, out[:200]))
        check(all(b in res for b in bits), "S2 %s: summary %r" % (name, res[:220]))
        check(rws == want_rows and all(l.split("\t")[7] == "ok" for l in logl(d)), "S2 %s: log rows %r" % (name, rws))
        check(len(hist(d)) == 1 and open(os.path.join(d, "config-history", hist(d)[0]), "rb").read() == text.encode("latin-1"),
              "S2 %s: History = the old file" % name)
        res2 = str(Cfg.migrate051())
        check(res2 == "" and open(fp, "rb").read().decode("latin-1") == out and len(hist(d)) == 1, "S2 %s: runs once" % name)
        if name == "spaced":
            pr = parse_props(out)
            Cfg.load(False)
            check(pr.get("boost.Stamina.flat") == "3,6,9,12" and nums(ef) == [3.0, 6.0, 9.0, 12.0] and nums(er) == [2.5, 5.0, 7.5, 10.0],
                  "S2 spaced: the loader reads the new numbers")
        if name == "continued":
            Cfg.load(False)
            check(nums(ef) == [1.5, 3.0, 4.5, 6.0], "S2 continued: the kept continued line still reads 1.5,3,4.5,6")
    # a fresh install: no file -> migrate051 does nothing, load(true) writes the 0.5.1 default file with the marker -> never updated
    d = os.path.join(SCRATCH, "s2-fresh")
    os.makedirs(d)
    fp = os.path.join(d, "config.properties")
    m_, r_ = start(fp)
    ft = open(fp, "rb").read()
    check(m_ == "" and MARK in ft.decode("latin-1") and parse_props(ft.decode("latin-1")).get("boost.Stamina.flat") == "3,6,9,12" and
          str(Cfg.migrate051()) == "" and open(fp, "rb").read() == ft and hist(d) == [], "S2 fresh install: the default file carries the marker")
    # a 0.4.x file: migrate051 leaves it alone, the 0.5 migration writes the 0.5.1 numbers + the marker -> later starts never update
    d = os.path.join(SCRATCH, "s2-04x")
    os.makedirs(d)
    fp = os.path.join(d, "config.properties")
    open(fp, "w", newline="\n").write(OLD_045_DEFAULT)
    m_, r_ = start(fp)
    t4 = open(fp, "rb").read().decode("latin-1")
    p4 = parse_props(t4)
    check(m_ == "" and "updated to 0.5" in r_ and p4.get("boost.Stamina.flat") == "3,6,9,12" and p4.get("boost.Stamina.regenPct") == "2.5,5,7.5,10"
          and t4.count(MARK) == 1 and hist(d) == [], "S2 0.4.x file: the 0.5 update writes the 0.5.1 numbers and the marker")
    check(str(Cfg.migrate051()) == "" and open(fp, "rb").read().decode("latin-1") == t4, "S2 0.4.x file: the next start changes nothing")
    # History that cannot be written: WARN, file untouched, no log line, the next start (History writable again) updates
    d = os.path.join(SCRATCH, "s2-nohist")
    os.makedirs(d)
    fp = os.path.join(d, "config.properties")
    t0 = "boost.Stamina.flat=1.5,3,4.5,6\n"
    open(fp, "w", newline="\n").write(t0)
    open(os.path.join(d, "config-history"), "w").write("not a folder")
    Cfg.FILE = jpath(fp)
    res = str(Cfg.migrate051())
    check(res == "" and open(fp, "rb").read().decode("latin-1") == t0 and logl(d) == [], "S2 History not writable: untouched, nothing logged")
    os.remove(os.path.join(d, "config-history"))
    res = str(Cfg.migrate051())
    check("updated to the 0.5.1" in res and parse_props(open(fp, "rb").read().decode("latin-1")).get("boost.Stamina.flat") == "3,6,9,12" and
          len(hist(d)) == 1, "S2 History writable again: the next start updates")
    print("S2. %d rule cases + fresh install + 0.4.x file + History not writable" % len(cases))

    # S3: UNDO through the real config kit on the S1 server folder (what Server Setup -> Changes does: the kit's inverse tset)
    Cfg.FILE = jpath(f)
    Cfg.load(True)
    Pub, Fn = JClass(P + ".CfgPub"), JClass(P + ".CfgFn")
    Pub.start(jpath(mods), None)
    fnc = Fn()
    lg = [str(x) for x in fnc.apply(jobj("log", JClass("java.lang.Integer").valueOf(50)))]
    ours = [l for l in lg if "\tSkyyAccessories 0.5.1\t" in l]
    check(len(ours) == 2 and all(l.endswith("\tok") for l in ours), "S3 op log lists our two lines (Server Setup -> Changes offers Undo on ok lines)")
    vers = [str(x) for x in fnc.apply(jobj("versions"))]
    check(any("\tSkyyAccessories 0.5.1\tbefore the 0.5.1 Stamina defaults update" in v for v in vers), "S3 op versions lists the History copy")
    r = [str(x) for x in fnc.apply(jobj("tset", "boost", "Stamina.flat", "1.5,3,4.5,6", None, "console", "yes", "console"))]
    Pub.flush()
    ut = open(f, "rb").read().decode("latin-1")
    check(r[0] == "ok" and parse_props(ut).get("boost.Stamina.flat") == "1.5,3,4.5,6" and MARK in ut and nums(ef) == [1.5, 3.0, 4.5, 6.0],
          "S3 the inverse tset (Undo) writes 1.5,3,4.5,6 back and the running numbers follow: %r" % r)
    lg2 = logl(sdir)
    check(lg2[-1].split("\t")[3:8] == ["console", "boost[Stamina.flat]", "3,6,9,12", "1.5,3,4.5,6", "ok"], "S3 the undo is logged: " + lg2[-1])
    check(str(Cfg.migrate051()) == "" and open(f, "rb").read().decode("latin-1") == ut, "S3 the next start keeps the undone value")
    Pub.shutdown()
    print("S3. undo through the kit: log %d lines (2 ours), %d History versions, tset -> %s" % (len(lg), len(vers), r[0]))

    # ---------------- Y. compare with the 0.5.1 jar (the SET pin): classes and assets
    import difflib
    IP_, PS_, BOS_ = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def csig(data):
        cp0 = JClass("javassist.ClassPool")(False)
        cp0.appendSystemPath()
        cp0.appendClassPath(B.SERVER_JAR)
        cc0 = cp0.makeClass(JClass("java.io.ByteArrayInputStream")(data))
        out = {}
        ms = [(str(mm.getName()) + str(mm.getSignature()), mm) for mm in cc0.getDeclaredMethods()]
        ms += [("<init>" + str(kk.getSignature()), kk.toMethod("init_", cc0)) for kk in cc0.getDeclaredConstructors()]
        if cc0.getClassInitializer() is not None:
            ms.append(("<clinit>", cc0.getClassInitializer().toMethod("clinit_", cc0)))
        for nm, mm in ms:
            bos = BOS_()
            IP_(PS_(bos)).print_(mm)
            out["m " + nm] = re.sub(r"#\d+ = ", "", str(bos.toString()))
        for fd in cc0.getDeclaredFields():
            out["f " + str(fd.getName())] = str(fd.getSignature()) + " = " + str(fd.getConstantValue())
        return out

    def norm(code):   # drop the instruction offsets and the absolute branch targets (an inserted block shifts them all)
        lines = [re.sub(r"^\s*\d+:\s*", "", l) for l in code.split("\n") if l.strip()]
        return [re.sub(r"^((?:if\w*|goto\w*|jsr\w*)) -?\d+$", r"\1", l) for l in lines]

    zb = zipfile.ZipFile(jar)
    if os.path.exists(JAR051):
        za = zipfile.ZipFile(JAR051)
        na, nb = set(za.namelist()), set(zb.namelist())
        ca = dict((n, za.read(n)) for n in na if n.endswith(".class"))
        cb = dict((n, zb.read(n)) for n in nb if n.endswith(".class"))
        same = sorted(n for n in ca if n in cb and ca[n] == cb[n])
        changed = sorted(n for n in ca if n in cb and ca[n] != cb[n])
        new_ = sorted(n for n in cb if n not in ca)
        gone = sorted(n for n in ca if n not in cb)
        short = lambda xs: ", ".join(x.split("/")[-1][:-6] for x in xs)
        check(not gone and short(new_) == "WbAssetL, WbRank, WbTab", "Y no class gone; new = WbAssetL, WbRank, WbTab: %s / %s" % (short(gone), short(new_)))
        check(sorted(short(changed).split(", ")) == ["CfgFn", "CfgRows", "SkyyAccessoriesPlugin"],
              "Y changed classes = the plugin (setup + start) and the kit's CfgFn / CfgRows (version): " + short(changed))
        mdiff = {}
        for cn in changed:
            x1, x2 = csig(ca[cn]), csig(cb[cn])
            k2s = sorted(k2 for k2 in set(x1) | set(x2) if x1.get(k2) != x2.get(k2))
            mdiff[cn.split("/")[-1][:-6]] = k2s
            if "Cfg" in cn:
                check(all(x1.get(k2, "").replace("0.5.1", "0.5.2") == x2.get(k2) for k2 in k2s) and k2s,
                      "Y %s differs only in the inlined VERSION 0.5.1 -> 0.5.2: %s" % (cn.split("/")[-1], k2s))
            else:
                check(k2s == ["m setup()V", "m start()V"] and "m start()V" not in x1 and "WbTab.start" in x2["m start()V"],
                      "Y the plugin: setup() changed, start() is new (WbTab.start): %s" % k2s)
                s1 = norm(x1["m setup()V"].replace("0.5.1", "0.5.2"))
                s2 = norm(x2["m setup()V"])
                ops = [o for o in difflib.SequenceMatcher(None, s1, s2, autojunk=False).get_opcodes() if o[0] != "equal"]
                ins = "\n".join(l for o in ops for l in s2[o[3]:o[4]])
                check(all(o[0] == "insert" for o in ops) and "WbAssetL" in ins and "LoadedAssetsEvent" in ins and "WbTab.LOG" in ins,
                      "Y the plugin's setup() = 0.5.1's (version) + the tab logger and listener lines only")
        print("Y. members that differ: " + "; ".join("%s: %s" % (k2, ", ".join(v)) for k2, v in sorted(mdiff.items())))
        assets_a = dict((n, za.read(n)) for n in na if not n.endswith(".class"))
        assets_b = dict((n, zb.read(n)) for n in nb if not n.endswith(".class"))
        ICON = "Common/" + WB.icon_path("SkyyAccessories")
        check(sorted(assets_b) == sorted(list(assets_a) + [ICON]), "Y the 0.5.1 asset files + the tab icon %s" % ICON)
        with zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")) as zz:
            check(assets_b.get(ICON) == zz.read(WB.ICON_SRC), "Y the tab icon = Assets.zip %s byte for byte" % WB.ICON_SRC)
        diff = sorted(n for n in assets_a if assets_a[n] != assets_b.get(n))
        idiff = [n for n in diff if n.startswith("Server/Item/Items/")]
        with_recipe = sorted(n for n in assets_a if n.startswith("Server/Item/Items/") and "Recipe" in json.loads(assets_a[n]))
        check(idiff == with_recipe and len(idiff) == 47, "Y exactly the 47 item JSONs with a recipe differ (%d)" % len(idiff))
        WB0 = {"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}
        WB1 = {"Type": "Crafting", "Id": "Workbench", "Categories": [WB.TAB_ID]}
        FLD = {"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["Tools"]}
        for n in idiff:
            ja, jb = json.loads(assets_a[n]), json.loads(assets_b[n])
            ra, rb = dict(ja["Recipe"]), dict(jb["Recipe"])
            qa, qb = ra.pop("BenchRequirement"), rb.pop("BenchRequirement")
            bag = n.endswith("/Skyy_Accessory_Bag.json")
            check(ra == rb and dict(ja, Recipe=0) == dict(jb, Recipe=0) and
                  ((qa == [FLD] and qb == [FLD, WB1]) if bag else (qa == [WB0] and qb == [WB1])),
                  "Y %s: only BenchRequirement changes (%s)" % (n.rsplit("/", 1)[1], "Fieldcraft kept + the Workbench tab" if bag else "Workbench_Crafting -> " + WB.TAB_ID))
        rest = [n for n in diff if not n.startswith("Server/Item/Items/")]
        check(rest == ["Server/Languages/en-US/server.lang", "manifest.json"], "Y besides the recipe JSONs only server.lang and the manifest differ: %r" % rest)
        la = assets_a["Server/Languages/en-US/server.lang"].decode("utf8").split("\n")
        lb = assets_b["Server/Languages/en-US/server.lang"].decode("utf8").split("\n")
        check(lb == la[:-1] + WB.LANG_LINES + [""], "Y server.lang = 0.5.1's + the 2 tab name lines (%s)" % WB.LANG_LINES[0])
        ma, mb = json.loads(assets_a["manifest.json"]), json.loads(assets_b["manifest.json"])
        check(sorted(k2 for k2 in set(ma) | set(mb) if ma.get(k2) != mb.get(k2)) == ["Name", "Version"] and mb["Version"] == "0.5.2" and
              mb["Name"] == "0.5.2 SkyyAccessories", "Y the manifest differs only in Name / Version")
        print("Y. compare with 0.5.1: classes identical %d, changed %d (%s), new %d (%s); assets: %d recipe JSONs (BenchRequirement only), "
              "server.lang (+2 tab lines), the tab icon, manifest" % (len(same), len(changed), short(changed), len(new_), short(new_), len(idiff)))
    else:
        check(False, "Y no SkyyAccessories-0.5.1.jar next to the build")

    # ---------------- W. the Workbench tab (tools/skyywbtab.py; SkyySacks 0.7.10 on the classpath)
    for l in WB.harness_checks(check, B.SERVER_JAR):
        print(l)

    # ---------------- L. the start sequence twice on a fresh copy of the live data folder: no file churn
    Paths_ = JClass("java.nio.file.Paths")
    if not os.path.isdir(LIVE):
        print("note: no live Skyy_SkyyAccessories folder - L skipped")
    else:
        d = os.path.join(SCRATCH, "l-acc")
        shutil.copytree(LIVE, d)      # read-only source, scratch copy

        def snap(dd):
            out_ = {}
            for root, _ds, fs in os.walk(dd):
                for f in fs:
                    pth = os.path.join(root, f)
                    out_[os.path.relpath(pth, dd)] = open(pth, "rb").read()
            return out_
        before = snap(d)
        P_ = lambda n: JClass("com.skyy.accessories." + n)
        notes = []
        for rnd in (1, 2):
            P_("AccStore").DIR = Paths_.get(os.path.join(d, "bags"))
            P_("AccCfg").FILE = Paths_.get(os.path.join(d, "config.properties"))
            m51 = str(P_("AccCfg").migrate051())
            cs = str(P_("AccCfg").load(True))
            P_("AccNotice").FILE = Paths_.get(os.path.join(d, "notices.properties"))
            P_("AccNotice").load()
            P_("WbTab").start()
            JClass("com.skyy.sacks.WbTab").start()
            notes.append((m51 + " " + cs).strip())
        after = snap(d)
        chg = sorted(k2 for k2 in set(before) | set(after) if before.get(k2) != after.get(k2))
        check(not chg, "L two starts (+ SkyySacks' tab start) on a copy of the live data: no file changed (%d files) %s" % (len(before), chg[:4]))
        print("L. two starts on the live copy: %d files unchanged (%s)" % (len(before), notes[-1][:120]))


def run_publishing(P, consts, tns, BO, ENT, ek, Defs, Store, Gear, Eff, Move, jarr, jpath, UUID):
    """B: part 2's publishing paths on the real bridge (System property skyy.bridge, shared by every class loader of this JVM)."""
    import skyybuild as B
    from jpype import JClass, JArray, JImplements, JOverride

    @JImplements("java.util.function.Function")
    class PyFn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)

    File, URLc, Long = JClass("java.io.File"), JClass("java.net.URL"), JClass("java.lang.Long")
    HashSet, HashMap = JClass("java.util.HashSet"), JClass("java.util.HashMap")
    platform = JClass("java.lang.ClassLoader").getPlatformClassLoader()

    def isolated(jar):
        urls = JArray(URLc)(2)
        urls[0] = File(jar).toURI().toURL()
        urls[1] = File(B.SERVER_JAR).toURI().toURL()
        return JClass("java.net.URLClassLoader")(urls, platform)

    tal = lambda f, w: "Skyy_Talisman_%s_%s" % (f, w)
    bridge = Store.bridge()
    OUTSIDE = ("gear:gates", "gear:fn:stats", "config:fn:SkyyGear", "stat:owner:fallDamage", "profile:fn:key")
    for k0 in OUTSIDE:
        bridge.remove(k0)
    Defs.COMBAT_TO_GEAR = True
    # the built-in numbers again (section M's reload test left its own numbers and switches behind)
    bdef = JArray(JClass("float"))(5 * len(ENT))
    for e, ent in enumerate(ENT):
        for t in range(1, 5):
            bdef[e * 5 + t] = float(ent[3][t - 1])
    Defs.BOOST = bdef
    Defs.REGEN_EVERY = 2
    for b in BO:
        setattr(Defs, "LINE_" + b[1].upper(), True)
    used = []                                   # test uuids: their bridge keys are removed at the end

    def uid():
        x = UUID.randomUUID()
        used.append(x)
        return x

    def bag(*ids):
        return jarr(list(ids) + [None] * (60 - len(ids)))

    def text(s):
        return str(Gear.textOf(Defs.activeTiers(s)))

    # ---- B1. the gear:extra text: the best rarity of each line counts, whole numbers, allowlisted keys in a fixed order
    s1 = bag("Skyy_Talisman_Strength_T4", "Skyy_Talisman_Strength_T1", "Skyy_Talisman_MagicPower_T2", "Skyy_Talisman_Defense_T1",
             "Skyy_Talisman_Crit_T3", "Skyy_Talisman_Crit_T1", tal("Vitality", "Epic"), "Skyy_Talisman_Feather_T4", "Skyy_Talisman_Strength_T2")
    t1 = text(s1)
    check(t1 == "cc:6,cd:12,def:3,mp:6,str:12", "B1 the text: the best rarity of each line, whole numbers, keys in order: " + t1)
    check(text(bag(tal("Vitality", "Epic"), tal("Speed", "Rare"), "Skyy_Talisman_Feather_T2")) == "", "B1 folded lines and Feather send nothing to SkyyGear")
    check(text(bag()) == "" and str(Gear.textOf(None)) == "", "B1 an empty bag sends nothing")
    Defs.LINE_STRENGTH = False
    check(text(s1) == "cc:6,cd:12,def:3,mp:6", "B1 a switched-off line leaves the text")
    Defs.LINE_STRENGTH = True
    Defs.COMBAT_TO_GEAR = False
    check(text(s1) == "", "B1 combatToGear off = nothing is sent")
    Defs.COMBAT_TO_GEAR = True
    b0 = [float(x) for x in Defs.BOOST]
    b1 = JArray(JClass("float"))(len(b0))
    for i, x in enumerate(b0):
        b1[i] = x
    b1[ek["str"] * 5 + 4] = 12.75                 # the loader never lets a decimal in (whole-number entries); the text floors anyway
    b1[ek["cd"] * 5 + 3] = 0.0
    Defs.BOOST = b1
    check(text(s1) == "cc:6,def:3,mp:6,str:12", "B1 decimals are floored, a 0 part is left out: " + text(s1))
    for i, x in enumerate(b0):
        b1[i] = x
    Defs.BOOST = b1
    # SkyyGear's OWN parser reads the text into the right stats (0.1 = the SET pin, 0.1.2 = the newest build), also from the bridge
    for gj in GEAR_JARS:
        if not os.path.exists(gj):
            check(False, "B1 no %s next to the build" % os.path.basename(gj))
            continue
        try:
            lg = isolated(gj)
            GS, GD = JClass("com.skyy.gear.GearStats", loader=lg), JClass("com.skyy.gear.GearDefs", loader=lg)
            keys = [str(x) for x in GD.S_KEY]
            want = {"cc": 6, "cd": 12, "def": 3, "mp": 6, "str": 12}
            arr = [int(x) for x in GS.parseExtra(t1)]
            check(all(arr[keys.index(k2)] == v for k2, v in want.items()) and sum(arr) == sum(want.values()),
                  "B1 %s GearStats.parseExtra(%r) -> %r" % (os.path.basename(gj), t1, dict((k2, arr[keys.index(k2)]) for k2 in want)))
            ug = uid()
            Gear.publish(ug, "GearTest", t1, 0)
            ex = GS.extra(ug)
            check(ex is not None and [int(x) for x in ex] == arr, "B1 %s GearStats.extra(uuid) reads our bridge text" % os.path.basename(gj))
            Gear.publish(ug, "GearTest", "", 1)
            check(GS.extra(ug) is None, "B1 %s: removed = no extra" % os.path.basename(gj))
        except Exception as ex_:
            check(False, "B1 %s could not be read: %s" % (os.path.basename(gj), ex_))

    # ---- B2. the publisher's rules (return codes: 0 nothing, 1 written, 2 removed, 3 foreign text replaced, 4 stopped)
    u = uid()
    key = "gear:extra:" + str(u)
    t0 = 1000000
    check(int(Gear.publish(u, "Tester", "str:3", t0)) == 1 and str(bridge.get(key)) == "str:3", "B2 first text written")
    check(int(Gear.publish(u, "Tester", "str:3", t0 + 1000)) == 0 and str(bridge.get(key)) == "str:3", "B2 the same text a second later: no write")
    check(int(Gear.publish(u, "Tester", "mp:6,str:3", t0 + 2000)) == 1 and str(bridge.get(key)) == "mp:6,str:3", "B2 a changed text is written")
    check(int(Gear.publish(u, "Tester", "", t0 + 3000)) == 2 and bridge.get(key) is None, "B2 empty = the key is removed")
    check(int(Gear.publish(u, "Tester", "", t0 + 4000)) == 0 and bridge.get(key) is None, "B2 empty again = nothing")
    bridge.put(key, "hp:5")                                            # another writer
    check(int(Gear.publish(u, "Tester", "", t0 + 5000)) == 0 and str(bridge.get(key)) == "hp:5", "B2 nothing to send: a foreign text stays")
    check(int(Gear.publish(u, "Tester", "str:3", t0 + 6000)) == 3 and str(bridge.get(key)) == "str:3" and Gear.WARNED.containsKey(u),
          "B2 a foreign text is replaced, with one WARN")
    bridge.put(key, "hp:9")                                            # ... and it writes again, 1 s later
    check(int(Gear.publish(u, "Tester", "str:3", t0 + 7000)) == 4 and str(bridge.get(key)) == "hp:9" and Gear.STOP.containsKey(u) and
          not Gear.LAST.containsKey(u), "B2 changed again within 5 s: writing stops for that player, the other text stays")
    check(int(Gear.publish(u, "Tester", "str:6", t0 + 60000)) == 0 and str(bridge.get(key)) == "hp:9", "B2 stopped: nothing written later either")
    bridge.put("gear:gates", "x")
    check(str(Gear.combatNote(u)).startswith("paused") and str(Gear.combatNote(None)) == "", "B2 the bag page says it is paused")
    bridge.put("profile:epoch:" + str(u), Long.valueOf(2))              # a profile switch
    check(int(Gear.publish(u, "Tester", "str:6", t0 + 61000)) == 3 and str(bridge.get(key)) == "str:6" and not Gear.STOP.containsKey(u),
          "B2 a profile switch: writing again")
    bridge.put(key, "hp:1")                                            # a slow second writer: 6 s after our write
    check(int(Gear.publish(u, "Tester", "str:6", t0 + 67000)) == 3 and str(bridge.get(key)) == "str:6", "B2 a text changed 6 s later is replaced, no stop")
    u2 = uid()
    k2 = "gear:extra:" + str(u2)
    hm = HashMap()
    bridge.put(k2, hm)
    check(int(Gear.publish(u2, "T2", "str:3", t0)) == 4 and bridge.get(k2) is not None and not isinstance(bridge.get(k2), str) and
          Gear.STOP.containsKey(u2), "B2 a value that is not a text (another format) is left alone, writing stops")
    bridge.remove(k2)

    # ---- B3. leave and shutdown: only OUR text goes (Map.remove(key, ourText)); our movement entry goes, other sources stay
    ua, ub, uc = uid(), uid(), uid()
    Gear.publish(ua, "A", "str:3", 0)
    Gear.publish(ub, "B", "def:3", 0)
    Gear.publish(uc, "C", "mp:3", 0)
    bridge.put("gear:extra:" + str(uc), "hp:2")                          # another writer took C's key meanwhile
    Move.post(ub, str(Gear.SOURCE), "pct", 0.1, 0.2, -0.4)
    Gear.MOVED.put(ub, True)
    Move.post(ub, "skills.acrobatics", "flat", 0.5, 1.0, -0.25)
    online = HashSet()
    online.add(ua)
    Gear.prune(online)
    check(str(bridge.get("gear:extra:" + str(ua))) == "str:3" and bridge.get("gear:extra:" + str(ub)) is None and
          str(bridge.get("gear:extra:" + str(uc))) == "hp:2" and bridge.get(key) is None, "B3 leave: the texts of players who left go, "
          "a text another mod wrote stays, the online player's stays")
    mv = Move.sources(ub, False)
    check(mv is not None and not mv.containsKey(str(Gear.SOURCE)) and mv.containsKey("skills.acrobatics") and not Gear.MOVED.containsKey(ub),
          "B3 leave: our movement entry goes, Acrobatics stays")
    check(not Gear.LAST.containsKey(ub) and not Gear.STOP.containsKey(u2) and Gear.LAST.containsKey(ua), "B3 leave: the state is forgotten")
    ud = uid()
    Move.post(ud, str(Gear.SOURCE), "pct", 0.05, 0.0, 0.0)
    Gear.MOVED.put(ud, True)
    Gear.shutdownAll()
    check(bridge.get("gear:extra:" + str(ua)) is None and str(bridge.get("gear:extra:" + str(uc))) == "hp:2" and
          not Move.sources(ud, False).containsKey(str(Gear.SOURCE)) and Gear.LAST.isEmpty() and Gear.MOVED.isEmpty(),
          "B3 shutdown: every text of ours and every movement entry go, others stay")

    # ---- B4. the bag page notes (AccGear.pageRows: one row per line, then the notes)
    for k0 in OUTSIDE:
        bridge.remove(k0)
    sfull = bag(*[tns["LINE_IDS"][li * 4 + 3] for li in range(len(BO))])
    rows = [str(x) for x in Gear.pageRows(sfull, None)]
    check([rows[2 * i] for i in range(len(BO))] == [b[2] for b in BO] and all(rows[2 * i + 1] for i in range(len(BO))) and
          rows[20:24] == ["Combat stats", "need SkyyGear, which is not running", "Fall damage", "needs SkyySkills, which is not running"],
          "B4 ten lines + two notes fill the 12 rows: %r" % rows[16:24])
    check(rows[11] == "+12 Strength" and rows[17] == "+8% Crit Chance, +16% Crit Damage" and rows[19] == "-40% fall damage, +20% jump height",
          "B4 row values: %r" % [rows[11], rows[17], rows[19]])
    bridge.put("gear:gates", "x")
    bridge.put("config:fn:SkyyGear", PyFn(lambda a: "false" if len(a) > 1 and str(a[0]) == "get" and str(a[1]) == "part.stats" else None))
    rows = [str(x) for x in Gear.pageRows(sfull, None)]
    check(rows[20:22] == ["Combat stats", "off in SkyyGear (Gear stats in combat)"], "B4 SkyyGear's Gear stats in combat off: %r" % rows[20:22])
    bridge.put("config:fn:SkyyGear", PyFn(lambda a: "true"))
    rows = [str(x) for x in Gear.pageRows(sfull, None)]
    check(rows[20:24] == ["Fall damage", "needs SkyySkills, which is not running", "", ""], "B4 SkyyGear on: no combat note")
    Defs.COMBAT_TO_GEAR = False
    rows = [str(x) for x in Gear.pageRows(sfull, None)]
    check(rows[20:22] == ["Combat stats", "not sent - switched off in Server Setup"], "B4 combatToGear off: %r" % rows[20:22])
    Defs.COMBAT_TO_GEAR = True
    bridge.put("stat:owner:fallDamage", "SkyySkills")
    rows = [str(x) for x in Gear.pageRows(sfull, None)]
    check(all(x == "" for x in rows[20:]), "B4 SkyyGear + SkyySkills running: no notes")
    bridge.remove("gear:gates")
    bridge.remove("stat:owner:fallDamage")
    rows = [str(x) for x in Gear.pageRows(bag(tal("Vitality", "Epic"), tal("Speed", "Rare")), None)]
    check(rows[:4] == ["Health", "+24 max Health", "Speed", "+7.5% Speed"] and all(x == "" for x in rows[4:]), "B4 folded lines only: no notes")
    rows = [str(x) for x in Gear.pageRows(bag("Skyy_Talisman_Crit_T2"), None)]
    check(rows[:4] == ["Razorfang", "+4% Crit Chance, +8% Crit Damage", "Combat stats", "need SkyyGear, which is not running"], "B4 one combat line")
    Defs.LINE_CRIT = False
    rows = [str(x) for x in Gear.pageRows(bag("Skyy_Talisman_Crit_T2", "Skyy_Talisman_Feather_T1"), None)]
    check(rows[:6] == ["Razorfang", "switched off", "Feather", "-10% fall damage, +5% jump height", "Fall damage",
                       "needs SkyySkills, which is not running"], "B4 a switched-off combat line needs no SkyyGear note: %r" % rows[:6])
    Defs.LINE_CRIT = True
    b1[ek["fallPct"] * 5 + 1] = 0.0
    Defs.BOOST = b1
    rows = [str(x) for x in Gear.pageRows(bag("Skyy_Talisman_Feather_T1"), None)]
    check(rows[:4] == ["Feather", "+5% jump height", "", ""], "B4 Feather with its fall part at 0: no SkyySkills note")
    b1[ek["fallPct"] * 5 + 1] = b0[ek["fallPct"] * 5 + 1]
    Defs.BOOST = b1
    bridge.remove("config:fn:SkyyGear")

    # ---- B5. the movement post (Speed + Feather) read by SkyySkills 0.4.8's OWN MoveSync (the fall-damage owner) and by ours
    um = uid()
    bo = [float(x) for x in Defs.BOOST]
    sp, ju, fa = bo[int(Defs.E_SPEED) * 5 + 4] / 100.0, bo[int(Defs.E_JUMP) * 5 + 4] / 100.0, 0.0 - bo[int(Defs.E_FALL) * 5 + 4] / 100.0
    check(abs(sp - 0.10) < 1e-6 and abs(ju - 0.20) < 1e-6 and abs(fa + 0.40) < 1e-6, "B5 Legendary Speed / Feather: +0.10 speed, +0.20 jump, -0.40 fall")
    Move.post(um, str(Gear.SOURCE), "pct", sp, ju, fa)
    if os.path.exists(SKILLS_JAR):
        try:
            SM = JClass("com.skyy.skills.MoveSync", loader=isolated(SKILLS_JAR))
            r = [float(x) for x in SM.sums(um)]
            check(all(abs(a - b2) < 1e-6 for a, b2 in zip(r, [0.0, 0.10, 0.0, 0.20, 0.0, -0.40])), "B5 SkyySkills 0.4.8 reads our entry: %r" % r)
            check(abs(float(SM.fallMultiplier(SM.sums(um))) - 0.6) < 1e-6, "B5 SkyySkills' fall filter: damage x 0.6 with Legendary Feather")
            SM.post(um, "skills.acrobatics", "flat", 1.0, 1.5, -0.5)                         # Acrobatics 100 (SkyySkills' own post)
            r2 = SM.sums(um)
            check(abs(float(SM.fallMultiplier(r2)) - 0.3) < 1e-6 and abs(float(Move.fallMultiplier(Move.sums(um))) - 0.3) < 1e-6,
                  "B5 with Acrobatics 100: fall damage x 0.3 (x 0.5 x 0.6, spec 1.5) in both copies")
            h0 = 11.8 * 11.8 / 64.0
            jf = math.sqrt(64.0 * ((h0 + 1.5) * 1.2))
            check(abs(float(SM.jumpForce(r2, 11.8)) - jf) < 1e-3 and abs(float(Move.jumpForce(Move.sums(um), 11.8)) - jf) < 1e-3,
                  "B5 jump force with Acrobatics 100 + Legendary Feather = %.3f in both copies (jump height x 1.2)" % jf)
            check(abs(float(SM.speedFactor(r2)) - 2.2) < 1e-5, "B5 speed factor 2.0 x 1.1 = 2.2 (spec 1.5)")
            Move.post(um, str(Gear.SOURCE), "pct", 0.0, 0.0, 0.0)
            r3 = [float(x) for x in SM.sums(um)]
            check(r3[1] == 0.0 and r3[3] == 0.0 and r3[5] == 0.0 and abs(r3[0] - 1.0) < 1e-6, "B5 all zero removes only our entry")
        except Exception as ex_:
            check(False, "B5 SkyySkills 0.4.8's MoveSync could not be used: %s" % ex_)
    else:
        check(False, "B5 no SkyySkills-0.4.8.jar next to its build")

    # ---- B6. the stat pools on a stat map double that follows EntityStatValue.computeModifiers (HytaleServer.jar bytecode: max = the
    # type max + the ADDITIVE MAX amounts, then value = clamp(value, min, max) - a higher max never raises the current value)
    pool = JClass("javassist.ClassPool")(True)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    ESV = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue"
    ESM = "com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap"
    MOD = "com.hypixel.hytale.server.core.modules.entitystats.modifier.Modifier"
    SMO = "com.hypixel.hytale.server.core.modules.entitystats.modifier.StaticModifier"
    MTG, CAL = MOD + "$ModifierTarget", SMO + "$CalculationType"
    fv = pool.makeClass("skyytest.FakeStatValue", pool.get(ESV))
    for fs_ in ("public float cur;", "public float base;", "public float mx;", "public java.util.HashMap mods;"):
        fv.addField(CtField.make(fs_, fv))
    fv.addConstructor(CtNewConstructor.make("public FakeStatValue(float b, float c) { super(); this.base = b; this.cur = c; this.mx = b; "
                                            "this.mods = new java.util.HashMap(); }", fv))
    for ms in ("public float get() { return this.cur; }", "public float getMax() { return this.mx; }",
               "public java.util.Map getModifiers() { return this.mods; }"):
        fv.addMethod(CtNewMethod.make(ms, fv))
    fm = pool.makeClass("skyytest.FakeStatMap", pool.get(ESM))
    for fs_ in ("public skyytest.FakeStatValue[] vals;", "public int puts;", "public int removes;"):
        fm.addField(CtField.make(fs_, fm))
    fm.addConstructor(CtNewConstructor.make("public FakeStatMap(Object[] v) { super(); this.vals = new skyytest.FakeStatValue[v.length]; "
                                            "for (int i = 0; i < v.length; i++) this.vals[i] = (skyytest.FakeStatValue) v[i]; }", fm))
    for ms in ("public static void recompute(skyytest.FakeStatValue v) { float m = v.base; java.util.Iterator it = v.mods.values().iterator(); "
               "while (it.hasNext()) { Object o = it.next(); if (!(o instanceof %s)) continue; %s s = (%s) o; "
               "if (s.getTarget() == %s.MAX && s.getCalculationType() == %s.ADDITIVE) m = m + s.getAmount(); } v.mx = m; "
               "if (v.cur > m) v.cur = m; if (v.cur < 0.0f) v.cur = 0.0f; }" % (SMO, SMO, SMO, MTG, CAL),
               "public %s get(int i) { if (i < 0 || i >= this.vals.length) return null; return this.vals[i]; }" % ESV,
               "public %s getModifier(int i, String k) { if (i < 0 || i >= this.vals.length) return null; return (%s) this.vals[i].mods.get(k); }" % (MOD, MOD),
               "public %s putModifier(int i, String k, %s m) { Object o = this.vals[i].mods.put(k, m); this.puts = this.puts + 1; "
               "recompute(this.vals[i]); return (%s) o; }" % (MOD, MOD, MOD),
               "public %s removeModifier(int i, String k) { Object o = this.vals[i].mods.remove(k); if (o != null) { this.removes = this.removes + 1; "
               "recompute(this.vals[i]); } return (%s) o; }" % (MOD, MOD),
               "public float addStatValue(int i, float a) { skyytest.FakeStatValue v = this.vals[i]; v.cur = v.cur + a; if (v.cur > v.mx) v.cur = v.mx; "
               "return v.cur; }"):
        fm.addMethod(CtNewMethod.make(ms, fm))
    out = os.path.join(SCRATCH, "fake-classes")
    os.makedirs(out, exist_ok=True)
    fv.writeFile(out)
    fm.writeFile(out)
    urls = JArray(URLc)(1)
    urls[0] = File(out).toURI().toURL()
    lf = JClass("java.net.URLClassLoader")(urls, JClass("java.lang.ClassLoader").getSystemClassLoader())
    FV, FM = JClass("skyytest.FakeStatValue", loader=lf), JClass("skyytest.FakeStatMap", loader=lf)
    SM_, MT, CT = JClass(SMO), JClass(MTG), JClass(CAL)
    hv, stv, mnv = FV(100.0, 100.0), FV(10.0, 10.0), FV(30.0, 30.0)
    vals = JArray(JClass("java.lang.Object"))(3)
    vals[0], vals[1], vals[2] = hv, stv, mnv
    m = FM(vals)
    Eff.modAmt(m, 0, "skyyacc_health", 24.0)
    check(int(m.puts) == 1 and float(hv.mx) == 124.0 and float(hv.cur) == 100.0, "B6 equip Legendary Health: max 100 -> 124, current stays 100")
    hv.cur = 124.0
    Eff.modAmt(m, 0, "skyyacc_health", 24.0)
    check(int(m.puts) == 1 and float(hv.cur) == 124.0, "B6 the same bag a second later: no write, a full bar stays full")
    Eff.modAmt(m, 0, "skyyacc_health", 18.0)
    check(int(m.puts) == 2 and int(m.removes) == 0 and float(hv.mx) == 118.0 and float(hv.cur) == 118.0,
          "B6 down to Rare (or a profile switch to a bag with the Rare): replaced in place, never removed first - current only clamped")
    Eff.modAmt(m, 0, "skyyacc_health", 24.0)
    check(int(m.puts) == 3 and float(hv.mx) == 124.0 and float(hv.cur) == 118.0, "B6 back to Legendary: max 124, current not raised")
    Eff.modAmt(m, 0, "skyyacc_health", 0.0)
    Eff.modAmt(m, 0, "skyyacc_health", 0.0)
    check(int(m.removes) == 1 and float(hv.mx) == 100.0 and float(hv.cur) == 100.0 and hv.mods.isEmpty(), "B6 unequip: removed once, max 100")
    hv2 = FV(100.0, 124.0)                         # a relog: EntityStatValue's codec saved the modifier with the player
    hv2.mods.put("skyyacc_health", SM_(MT.MAX, CT.ADDITIVE, 24.0))
    FM.recompute(hv2)
    v2 = JArray(JClass("java.lang.Object"))(1)
    v2[0] = hv2
    m2 = FM(v2)
    Eff.modAmt(m2, 0, "skyyacc_health", 24.0)
    check(int(m2.puts) == 0 and float(hv2.cur) == 124.0 and float(hv2.mx) == 124.0, "B6 relog: the saved modifier is kept, 124 / 124 stays")
    Eff.modAmt(m, 1, "skyyacc_stamina", 1.5)
    check(abs(float(stv.mx) - 11.5) < 1e-6 and float(stv.cur) == 10.0, "B6 Stamina +1.5 (decimals fine), current not raised")
    mnv.mods.put("skyyskills_mana", SM_(MT.MAX, CT.ADDITIVE, 30.0))
    FM.recompute(mnv)
    mnv.cur = float(mnv.mx)
    p0 = int(m.puts)
    Eff.manaMod(m, 2, "skyyacc_mana", 24.0, 4.0)
    Eff.manaMod(m, 2, "skyyacc_mana", 24.0, 4.0)
    got = mnv.mods.get("skyyacc_mana")
    check(int(m.puts) == p0 + 1 and got is not None and abs(float(got.getAmount()) - 7.2) < 1e-4 and float(mnv.cur) == 60.0,
          "B6 Mana: 24% of the other flat Mana (30; the harness has no stat asset map, so the type max counts 0) = 7.2, written once "
          "(ours left out of the base), current kept")
    mnv.mods.remove("skyyskills_mana")
    Eff.manaMod(m, 2, "skyyacc_mana", 6.0, 1.0)
    check(abs(float(mnv.mods.get("skyyacc_mana").getAmount()) - 1.0) < 1e-6, "B6 Mana on a tiny pool: the floor (+1)")

    # ---- B7. a profile switch and a relog (SkyyProfiles' key function + epoch on the bridge): the ACTIVE profile's bag decides
    up = uid()
    keyp = {"k": str(up)}
    Store.DIR = jpath(SCRATCH, "profiles", "bags")
    for it_ in ("Skyy_Talisman_Strength_T4", tal("Vitality", "Rare"), "Skyy_Talisman_Strength_T1"):
        Store.stashK(up, str(up), it_)
    for it_ in ("Skyy_Talisman_MagicPower_T2", "Skyy_Talisman_Crit_T1"):
        Store.stashK(up, str(up) + "-p2", it_)
    bridge.put("profile:fn:key", PyFn(lambda a: keyp["k"]))
    bridge.put("profile:epoch:" + str(up), Long.valueOf(1))
    bridge.put("gear:gates", "x")
    kp = "gear:extra:" + str(up)
    hp = FV(100.0, 100.0)
    vp = JArray(JClass("java.lang.Object"))(1)
    vp[0] = hp
    mp_ = FM(vp)
    he = ek["maxHealth"]

    def tickp(now):
        best = Defs.activeTiers(Store.snapshot(up))
        Eff.modAmt(mp_, 0, "skyyacc_health", float(Defs.BOOST[he * 5 + list(best)[0]]))
        return int(Gear.publish(up, "Prof", str(Gear.textOf(best)), now))

    check(tickp(0) == 1 and str(bridge.get(kp)) == "str:12" and float(hp.mx) == 118.0, "B7 profile 1: str:12 and +18 max Health")
    rows = [str(x) for x in Gear.pageRows(Store.snapshot(up), up)]
    check(rows[:4] == ["Health", "+18 max Health", "Brawler", "+12 Strength"] and rows[4] == "", "B7 profile 1 rows: %r" % rows[:5])
    keyp["k"] = str(up) + "-p2"
    bridge.put("profile:epoch:" + str(up), Long.valueOf(2))
    check(tickp(1000) == 1 and str(bridge.get(kp)) == "cc:2,cd:4,mp:6" and float(hp.mx) == 100.0 and hp.mods.isEmpty(),
          "B7 profile switch: the text follows the new bag (cc:2,cd:4,mp:6), the Health modifier is removed")
    rows = [str(x) for x in Gear.pageRows(Store.snapshot(up), up)]
    check(rows[:4] == ["Runic", "+6 Magical Power", "Razorfang", "+2% Crit Chance, +4% Crit Damage"], "B7 profile 2 rows: %r" % rows[:4])
    check(tickp(2000) == 0, "B7 the next second: nothing new to write")
    Gear.prune(HashSet())                                              # the player logs out
    check(bridge.get(kp) is None and not Gear.LAST.containsKey(up), "B7 logout: the text is gone")
    check(tickp(3000) == 1 and str(bridge.get(kp)) == "cc:2,cd:4,mp:6", "B7 log back in: written again from the active profile")
    # ---- clean-up: nothing of this section stays on the bridge
    Gear.shutdownAll()
    for k0 in OUTSIDE:
        bridge.remove(k0)
    for x in used:
        for pre in ("gear:extra:", "move:", "profile:epoch:", "acc:has:", "acc:tal:"):
            bridge.remove(pre + str(x))
    check(not any(str(k0).startswith("gear:extra:") for k0 in bridge.keySet()), "B no gear:extra key left on the bridge")
    print("B. publishing: gear:extra text + rules + SkyyGear's parser, notes, movement read by SkyySkills 0.4.8, stat pools, profile switch, relog")


OLD_045_DEFAULT = """# SkyyAccessories settings. Change them in game: SkyWynn Menu -> Server Setup -> Accessories (SkyyMenu 0.3), or edit this file
slots=9
regenEverySeconds=2
bonus.Vitality=2,4,6,8,10
bonus.Endurance=2,4,6,8,10
bonus.Intelligence=2,4,6,8,10
bonus.Regeneration=0.5,1,1.5,2,3
bonus.Speed=2,4,6,8,10
"""


def parse_props(text):
    """java.util.Properties-like reader for the plain files the tests write and read (continuations joined, comments skipped)"""
    out = {}
    lines = text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i].lstrip(" \t\f")
        i += 1
        if not ln or ln[0] in "#!":
            continue
        while ln.endswith("\\") and (len(ln) - len(ln.rstrip("\\"))) % 2 == 1 and i < len(lines):
            ln = ln[:-1] + lines[i].lstrip(" \t\f")
            i += 1
        m = re.match(r"([^=:\s]+)\s*[=:\s]\s*(.*)$", ln)
        if m:
            out[m.group(1)] = m.group(2)
        else:
            out[ln] = ""
    return out


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
    for p in (JAR051, SACKS_JAR):
        if not os.path.exists(p):
            raise SystemExit("missing " + p + " (sections Y / W need it)")
    if os.path.getmtime(JAR) < os.path.getmtime(BUILD):
        raise SystemExit("the jar is older than " + os.path.basename(BUILD) + " - rebuild it first")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"))
    env = dict(os.environ, TEMP=os.path.join(SCRATCH, "tmp"), TMP=os.path.join(SCRATCH, "tmp"))
    args = [sys.executable, os.path.abspath(__file__), "--child", "--jar", JAR, "--dir", SCRATCH, "--live", LIVE]
    if "--synthetic" in sys.argv:
        args.append("--synthetic")
    r = subprocess.run(args, env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
