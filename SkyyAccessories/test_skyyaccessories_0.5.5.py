"""Bare-JVM checks for SkyyAccessories 0.5.5, kept next to the build so every claim of the build report can be re-run by anyone.
0.5.5 (LANTERN SMOOTH EDGES, tools/acc_0_5_5_patch.py writes this file from test_skyyaccessories_0.5.4.py): every 0.5.4 check below is
carried forward and its Lantern sections run in the 0.5.4 light layout (lantern.height 128, lantern.edge 255, lantern.lights 1 - the
0.5.4 behaviour, proven equal); new:
  Q22 THE SOFT RING: the jar's ring reach / solver = the build's Python bit for bit (+ 24 random settings: every light under the brightness
      cap, never above the height row, never more lights than the row), the default table (Legendary 95 at 52 up + 5 around at 27.5), and
      on the REAL ECS world: six entities (slots 0-5, every part of the 0.5.4 helper, never saved) at their spots, following a walk
      within distance / 50, the swap to Rare (ring gone at once), death, lantern.lights 1, logout, world change both ways, the spawn
      batch limit, and a REAL World + ChunkStore (a ring slot in a non-ticking / missing section has no light until it ticks)
  Q21 + the ring on the REAL entity tracker: all six reach the wearer's client only, white 95, and leave it on unequip
  U   THE ONE-TIME lantern.height UPDATE (AccCfg.m55Update / migrate055): the 0.5.4 default file (128 -> 64 + marker, every other byte
      kept), CRLF, custom / 64 / spaced / continued / duplicated / commented lines, no lantern line (marker at the end), the 0.5.5 default
      text (never updated); on files with the real kit: History copy = the old bytes, the change-log line, the loader, the second start,
      Undo through the kit stays; a scratch copy of the LIVE folder; a fresh install
  L   the start sequence now includes migrate055: the first start may add the marker (config.properties + History only), then no churn
  Y   COMPARE with the 0.5.4 jar (the SET pin): only the Lantern / config / plugin classes change, every asset but the manifest identical
The 0.5.4 notes:
0.5.4 (THE LANTERN LINE REPLACES NIGHT VISION, tools/acc_0_5_4_patch.py): the 0.5.3 harness carried forward - every check below still runs
(the jars it reads are the current SET pins: SkyySacks 0.7.12, SkyyGear 0.1 + 0.2.1, SkyySkills 0.4.15), its counts now hold the four
Lantern items, line, rows and acc:defs records and the retired Night Vision; 0.5.3's N section is replaced by:
  R  THE NIGHT VISION RETIREMENT: the item (0.5.3's look, no recipe, Variant + no Categories, the retired name and tooltip, decoded through
     the engine's Item codec), the id rules (retired: rarity 0, "Does nothing", the retired grey, "Night Vision Accessory - retired"),
     the bag (Equip refused, an old copy counts for nothing, acc:fn:has / acc:tal leave it out, its bag row, Unequip takes it out), a
     scratch copy of the LIVE bags (Skyy's profile 3 holds one), give / givetier / acc:fn:give / lines / defs, no light code left
  Q  THE LANTERN: Q1 the jar's light model and tier table = the build script's Python (exec'd from it) bit for bit, 150 random settings,
     the brightness cap always holds; Q2 the vanilla torch from Assets.zip through the engine's own ColorParseUtil = our default glow,
     the radius-1 owner mark (never a foreign light); Q3 the four items through Item.CODEC; Q4-Q18 A REAL ENGINE ECS WORLD - a
     ComponentRegistry with the engine's component classes registered like EntityModule does, two Stores = two worlds, the jar's
     AccLanternSys + AccLanternHelp ticked by Store.tick with real CommandBuffers: no Lantern / Normal (the glow component, never in the
     saved copy) / Unique (one helper 14 up, light 31, Transform + DynamicLight + NetworkId + Intangible + Despawn + NonSerialized + our
     marker, never saveable, its 5 s dead-man time refreshed every tick) / it follows the player every tick / Rare / Legendary / the world
     top (y 318, the light dimmed so the cap holds) / no room / Server Setup numbers change (re-decided) / the switch / death (off at once,
     back after the respawn) / profile switch (SkyyProfiles' key function + epoch) / unloaded helper replaced (spawn limit) / a parked copy
     removed / two players / foreign and builder lights never touched / logout (removed in its own world, state pruned) / world change both
     ways (each world removes only its own helper) / restart (nothing saveable but the player without the light; fresh ones next start) /
     the spawn limit, the section walk, the placement rules / the bag rules / WbRank; Q19 config (default file, an existing 0.5.3 file
     untouched, hand edits clamped, the Server Setup rows through the real kit moving a live helper); Q20 the jar's bytecode
     THE FIX ROUND (the adversarial review): Q2 the helper light is WHITE and the client's own shader text (HytaleClient.exe, read-only,
     skipped without it) fades each colour channel on its own - the old torch tint would light the far ground red; Q6 a move only past
     height / 50 blocks (0.1 - 1.5) and at once when the helper is below its spot; Q16b 600 ticks at non-binary heights: the light is
     never re-sent ((feet + 123) - feet < 123 in doubles); Q16c sectionOk / sectionMask / pickY on a REAL World + ChunkStore (loaded,
     missing and NonTicking sections, the 20-tick re-check) and through AccLanternSys in a world whose EntityStore has that World;
     Q21 THE REACH LIGHT IS THE WEARER'S OWN on the REAL ENTITY TRACKER (EntityStore.REGISTRY, the engine's NetworkSendableSpatialSystem,
     ClearEntityViewers, CollectVisible, ClearPreviouslyVisible, EnsureVisibleComponent, AddToVisible, RemoveEmptyVisibleComponent,
     DynamicLightTracker, DynamicLightSystems$EntityTrackerRemove, TransformSystems$EntityTrackerUpdate, SendPackets, DespawnSystem + the
     jar's three systems; EntityModule / TimeModule stand-ins hold the harness's component types): the system order (20 shuffles), the
     packets each player's IPacketReceiver gets (the wearer gets the helper and its white light, the other player only the glow),
     lantern.shareReach (everyone gets it; a player who /hide's the wearer does not), the view-radius clamp, a removed glow reaching the
     other client, and the 5 s dead-man: with the jar's systems unregistered the engine's DespawnSystem removes the helper on its own
  Y  COMPARE with the 0.5.3 jar: classes (Night Vision classes gone, Lantern classes new, the rest identical or expected), assets (+ 4
     Lantern JSONs, the Night Vision JSON = Categories -> Variant, server.lang = 4 lines changed in place + 16 at the end, the manifest)
0.5.3 notes (THE NIGHT VISION ACCESSORY, its N section is gone with the light it tested): N1 the item asset, N2 the id, N3 the bag, N4 the
wearer-only light on real EntityViewer / Visible objects, N5 config, N6 bytecode, N7 the tracker system order.
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

    python SkyyAccessories/test_skyyaccessories_0.5.4.py [--jar <SkyyAccessories-0.5.4.jar>] [--dir <scratch folder>] [--keep] [--synthetic] [--live <folder>]
    (--synthetic: section M uses the synthetic 0.4.5 folder even while the live one is still a 0.4.x folder)

Build first (python tools/acc_0_5_4_patch.py, python SkyyAccessories/build_skyyaccessories_0.5.4.py; SkyySacks 0.7.12, SkyyGear 0.1 + 0.2.1,
SkyySkills 0.4.15 and SkyyAccessories 0.4.5 / 0.5 / 0.5.3 jars next to their builds). A child process starts a fresh
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
Nothing is deployed and nothing under AppData is written. Default scratch folder: tools/dev/scratch/acc055/test (git-ignored),
deleted at the end unless --keep. Exit code 1 on any failure.
"""
import os, sys, re, json, shutil, subprocess, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyywbtab as WB   # 0.5.2: the Workbench tab tables + harness_checks
VERSION = "0.5.5"
BUILD = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
JAR045 = os.path.join(HERE, "SkyyAccessories-0.4.5.jar")
JAR05 = os.path.join(HERE, "SkyyAccessories-0.5.jar")          # section S (its default file)
JAR053 = os.path.join(HERE, "SkyyAccessories-0.5.3.jar")       # 0.5.4: sections R, Q19 (a 0.5.3 server's file)
JAR054 = os.path.join(HERE, "SkyyAccessories-0.5.4.jar")       # 0.5.5: the SET pin (live) - sections Y, U (its default file)
SACKS_JAR = os.path.join(ROOT, "SkyySacks", "SkyySacks-0.7.12.jar")   # section W (the other half of the Workbench tab); 0.5.3: the SET pin
GEAR_JARS = [os.path.join(ROOT, "SkyyGear", "SkyyGear-%s.jar" % v) for v in ("0.1", "0.2.1")]   # 0.5.4: 0.2.1 = the SET pin, 0.1 = the first reader
SKILLS_JAR = os.path.join(ROOT, "SkyySkills", "SkyySkills-0.4.15.jar")                        # 0.5.4: the SET pin (fall damage owner)
LIVE = os.path.join(os.environ.get("APPDATA", r"C:\Users\SkyLo\AppData\Roaming"), "Hytale", "UserData", "Saves", "HUD mod", "mods",
                    "Skyy_SkyyAccessories")


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "acc055", "test")))
LIVE = os.path.abspath(arg("--live", LIVE))   # section M's source folder (read only; default: the HUD mod world's Skyy_SkyyAccessories)
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
KEEP = "--keep" in sys.argv
# 0.5.5: tools/tidy_local.py packs old jars into backups/archive/old-jars-*.tar.xz; extract that archive into a scratch folder and pass
# --oldjars <folder> to give sections R / X / S / B1 their old jars (SkyyAccessories 0.4.5 + 0.5, SkyyGear 0.1) again
OLDJARS = arg("--oldjars")
if OLDJARS:
    OLDJARS = os.path.abspath(OLDJARS)
    JAR045 = os.path.join(OLDJARS, "SkyyAccessories", "SkyyAccessories-0.4.5.jar")
    JAR05 = os.path.join(OLDJARS, "SkyyAccessories", "SkyyAccessories-0.5.jar")
    GEAR_JARS[0] = os.path.join(OLDJARS, "SkyyGear", "SkyyGear-0.1.jar")

FAILS = []
OKS = [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


BAD_WORDS = ("Vitality", "Endurance", "Intelligence", "Talisman")
NVID = "Skyy_Talisman_NightVision_Rare"   # 0.5.3: the Night Vision accessory (0.5.4: retired)
LANS = ["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Lantern_Uncommon", "Skyy_Talisman_Lantern_Rare", "Skyy_Talisman_Lantern_Epic"]   # 0.5.4


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
        # 0.5.4: the retired Night Vision (Skyy's live profile 3 still holds one), the Lantern, all ten Legendary lines + both
        ("retired night vision in the bag and the inventory", [NVID, tal("Speed", "Epic")] + [N] * 58, 18, [NVID, "Skyy_Accessory_Furnace_T1"],
         str(Defs.retiredWhy(NVID)), 0, 0),
        ("lantern in the bag and the inventory", [LANS[2], tal("Speed", "Epic")] + [N] * 58, 18, [LANS[3], LANS[0]],
         "equipped Rare Lantern Accessory", 0, 0),
        ("lantern + all ten Legendary lines + the retired night vision", [tns["LINE_IDS"][li * 4 + 3] for li in range(len(BO))] + [LANS[3], NVID] +
         [N] * 48, 18, [], "", 1, 0),
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
        if name == "retired night vision in the bag and the inventory":   # 0.5.4
            check(sets.get("#SkyyAccBk0.Text") == "Speed" and sets.get("#SkyyAccBk1.Text") == "Night Vision" and
                  sets.get("#SkyyAccBon1.Text") == "retired - take it out" and sets.get("#SkyyAccBk2.Text") == "",
                  "P the retired Night Vision row comes after the booster lines: %r" % [sets.get("#SkyyAccBk%d.Text" % q) for q in range(3)])
            check(sets.get("#SkyyAccSlot0Nm.Text") == "Night Vision Accessory - retired" and sets.get("#SkyyAccSlot0Rr.Text") == "DOES NOTHING" and
                  sets.get("#SkyyAccInv0Nm.Text") == "Night Vision Accessory - retired" and sets.get("#SkyyAccInv0Rr.Text") == "DOES NOTHING" and
                  sets.get("#SkyyAccInfo.Text") == str(Defs.retiredWhy(NVID)),
                  "P its rows say '- retired' / DOES NOTHING, the result line the refusal: %r" % [sets.get(x) for x in
                                                                                                ("#SkyyAccSlot0Nm.Text", "#SkyyAccSlot0Rr.Text")])
            check(str(Defs.rarityColor(NVID)).lower() == str(Defs.RETIRED_COLOR).lower() and
                  any(typ == "AppendInline" and str(Defs.RETIRED_COLOR).lower() in v.lower() for typ, sel, v in got),
                  "P its rows are drawn in the retired grey %s" % Defs.RETIRED_COLOR)
        if name == "lantern in the bag and the inventory":   # 0.5.4
            check(sets.get("#SkyyAccBk0.Text") == "Speed" and sets.get("#SkyyAccBk1.Text") == "Lantern" and
                  sets.get("#SkyyAccBon1.Text") == "torch glow, lights about 24 blocks" and sets.get("#SkyyAccBk2.Text") == "",
                  "P the Lantern row comes after the booster lines: %r" % [sets.get("#SkyyAccBon%d.Text" % q) for q in range(2)])
            check(sets.get("#SkyyAccSlot0Nm.Text") == "Rare Lantern Accessory" and sets.get("#SkyyAccSlot0Rr.Text") == "RARE" and
                  sets.get("#SkyyAccInv0Nm.Text") == "Legendary Lantern Accessory" and sets.get("#SkyyAccInv1Nm.Text") == "Normal Lantern Accessory",
                  "P the bag row and the inventory rows: Rare / Legendary / Normal Lantern Accessory")
        if name == "lantern + all ten Legendary lines + the retired night vision":   # 0.5.4
            check([sets.get("#SkyyAccBk%d.Text" % q) for q in range(10)] == [b[2] for b in BO] and sets.get("#SkyyAccBk10.Text") == "Lantern" and
                  sets.get("#SkyyAccBon10.Text") == "torch glow, lights about 48 blocks" and sets.get("#SkyyAccBk11.Text") == "Night Vision",
                  "P 10 lines + the Lantern + the retired Night Vision fill the 12 rows: %r" % [sets.get("#SkyyAccBk%d.Text" % q) for q in (10, 11)])
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
          and str(Defs.lineLabel("Skyy_Accessory_Furnace_T1")) == "bench accessory" and str(Defs.lineLabel(LANS[1])) == "Lantern Accessory",
          "C the refusal names the line (0.5.4: the Lantern too)")
    lwhy = "bag is full, or the same or a better " + str(Defs.lineLabel(LANS[1])) + " is already equipped"
    check(str(Page.infoColor(lwhy)) == NO and str(Page.infoColor("equipped " + str(Defs.pretty(LANS[1])))) == OK and
          str(Page.infoColor("upgraded to " + str(Defs.pretty(LANS[2])) + " - " + str(Defs.pretty(LANS[1])) + " returned")) == OK and
          str(Page.infoColor("unequipped " + str(Defs.pretty(LANS[3])))) == OK and clean(lwhy), "C the Lantern result texts keep their colours")
    check(str(Page.infoColor(str(Defs.retiredWhy(NVID)))) == NO and clean(str(Defs.retiredWhy(NVID))) and clean(str(Defs.retiredChat(NVID))),
          "C the retired Night Vision's refusal is a red refusal line")
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
                    ("Skyy_Talisman_Crit_T5", False), ("Skyy_Talisman_Strength_Common", False), ("Skyy_Talisman_Crit_Legendary", False),
                    (NVID, False), ("Skyy_Talisman_NightVision_Epic", False), ("Skyy_Talisman_NightVision_T3", False),   # 0.5.4: Night Vision retired
                    (LANS[0], True), (LANS[3], True), ("Skyy_Talisman_Lantern_T3", False), ("Skyy_Talisman_Lantern_Legendary", False)):   # + the Lantern
        r = Admin.giveable(gid)
        check((r is None) == ok and (r is None or clean(r)), "G giveable(%s) -> %s" % (gid, r))
    for w, ok in (("NightVision", True), ("nightvision", True), ("Night_Vision", True), ("night-vision", True), ("NV", True), ("nv", True),
                  ("Night", False), ("Vision", False), ("", False), ("Night Vision Accessory", False)):   # the old givetier names (0.5.4: answered "retired")
        check(bool(Defs.isNvName(w)) == ok and int(Defs.lineOf(w)) == -1, "G isNvName(%r) = %s (and no booster line)" % (w, ok))
    for w, ok in (("Lantern", True), ("lantern", True), ("LANTERNS", True), ("Lamp", False), ("", False), ("Lantern Accessory", False)):   # 0.5.4
        check(bool(Defs.isLanName(w)) == ok and int(Defs.lineOf(w)) == -1, "G isLanName(%r) = %s (and no booster line)" % (w, ok))
    check(int(Admin.giveFn(UUID.randomUUID(), NVID, 1)) == 0 and int(Admin.giveFn(UUID.randomUUID(), LANS[2], 1)) == 0 and
          str(Admin.giveable(NVID)) == str(Defs.NV_GIVE), "G acc:fn:give: the retired Night Vision is refused, a Lantern id is taken (0 = that "
          "player is not online); /accessories give answers with the retirement")
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
    check(len(defs) == 4 * len(BO) + 4 == 44 and all(len(d.split(":")) == 7 for d in defs), "G acc:defs = 40 booster records + 4 Lantern records, 7 fields")
    check(defs[40:44] == ["Lantern:Lantern:%d:%s:%s:%d:Craft" % (t, LANS[t - 1], ("Normal", "Unique", "Rare", "Legendary")[t - 1], (10, 13, 16, 19)[t - 1])
                          for t in range(1, 5)], "G acc:defs Lantern records: %r" % defs[40:44])
    check(defs[3] == "Health:Vitality:4:Skyy_Talisman_Vitality_Epic:Legendary:19:Craft+Boss", "G acc:defs record: " + defs[3])
    check(defs[23] == "Strength:Strength:4:Skyy_Talisman_Strength_T4:Legendary:19:Boss" and
          defs[36] == "Feather:Feather:1:Skyy_Talisman_Feather_T1:Normal:10:Craft", "G acc:defs part 2 records: %s / %s" % (defs[23], defs[36]))
    lp = [str(x) for x in Defs.linesText(False)]
    la = [str(x) for x in Defs.linesText(True)]
    check(len(lp) == len(BO) + 1 and all(clean(x) for x in lp), "G /accessories lines for players: no ids, no old names (10 lines + the Lantern)")
    check(lp[10] == "Lantern Accessory (Lantern): Normal glows like a torch, lights about 6 blocks around you | Unique glows like a torch, lights about "
          "12 blocks around you | Rare glows like a torch, lights about 24 blocks around you | Legendary glows like a torch, lights about 48 blocks "
          "around you - everyone sees your glow, only you see the far light", "G the Lantern line: " + lp[10])
    Defs.LAN_SHARE = True
    check(str(Defs.linesText(False)[10]).endswith(" - everyone sees the glow and the far light"), "G lantern.shareReach on: the line says so")
    Defs.LAN_SHARE = False
    check(lp[1] == "Stamina Accessory (Stamina): Normal +3 max Stamina and +2.5% Stamina Regen | Unique +6 max Stamina and +5% Stamina "
          "Regen | Rare +9 max Stamina and +7.5% Stamina Regen | Legendary +12 max Stamina and +10% Stamina Regen", "G lines text: " + lp[1])
    check(lp[8] == "Razorfang Accessory (Crit): Normal +2% Crit Chance, +4% Crit Damage | Unique +4% Crit Chance, +8% Crit Damage | Rare "
          "+6% Crit Chance, +12% Crit Damage | Legendary +8% Crit Chance, +16% Crit Damage", "G lines text: " + lp[8])
    check(lp[9] == "Feather Accessory (Feather): Normal -10% fall damage, +5% jump height | Unique -20% fall damage, +10% jump height | "
          "Rare -30% fall damage, +15% jump height | Legendary -40% fall damage, +20% jump height", "G lines text: " + lp[9])
    check(len(la) == 2 * len(BO) + 2 and la[1] == "    ids: " + " / ".join(tns["LINE_IDS"][0:4]) and
          la[11] == "    ids: " + " / ".join("Skyy_Talisman_Strength_T%d" % t for t in range(1, 5)) and la[-2] == lp[10] and
          la[-1] == "    ids: " + " / ".join(LANS), "G admins also see the ids (the Lantern's last)")
    Defs.LINE_LANTERN = False
    check(str(Defs.linesText(False)[10]).startswith("Lantern Accessory (Lantern) - SWITCHED OFF on this server: Normal"),
          "G a switched-off Lantern says so in /accessories lines")
    Defs.LINE_LANTERN = True
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
        allids += [NVID] + LANS   # 0.5.4: the retired Night Vision's longer name + the four Lantern names
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
             "needs SkyySkills, which is not running", str(Defs.NV_ROW)] + [str(Defs.lanRow(t)) for t in range(1, 5)] + \
            ["torch glow, lights about 64 blocks", "glow 15, lights about 64 blocks", "glows at light 15", "no light"]   # 0.5.4: the Lantern rows
        bw = max(width(t, SUI.fs(13)) for t in big)
        check(bw <= ns["ACC_BON_VAL_W"], "E widest bonus value %.0f px fits %d px (%s)" % (bw, ns["ACC_BON_VAL_W"],
                                                                                       max(big, key=lambda t: width(t, SUI.fs(13)))))
        kw = max(width(t, SUI.fs(13), True) for t in [b[2] for b in BO] + ["Combat stats", "Fall damage", "Night Vision", "Lantern"])
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

    # ---------------- 0.5.4: R the Night Vision retirement, Q the Lantern
    run_retired(P, jar, tns, BO, Defs, Store, Admin, jpath, UUID, jarr)
    run_lantern(P, jar, tns, BO, Defs, Store, Cfg, jpath, UUID, jarr)
    # ---------------- 0.5.5: U the one-time lantern.height update
    run_m55(P, Defs, Cfg, jpath)


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
    hidden = sorted(legacy + retired + [NVID])   # 0.5.4: + the retired Night Vision
    check(len(legacy) == 20 and len(retired) == 5 and len(set(hidden)) == 26, "H 20 legacy booster ids + 5 retired bench accessories + Night Vision")
    check(sorted(i for i, n in items.items() if "Variant" in n) == hidden, "H exactly the 26 old ids carry Variant: %r" %
          sorted(set(i for i, n in items.items() if "Variant" in n) ^ set(hidden)))
    for i in hidden:
        n = items.get(i, {})
        check(n.get("Variant") is True and "Categories" not in n and "Recipe" not in n and n.get("MaxStack") == 1,
              "H %s: Variant true, no Categories, no Recipe" % i)
    current = sorted(i for i in items if i not in hidden)
    want = set(tns["LINE_IDS"]) | set("Skyy_Accessory_%s_T%d" % (str(Defs.BENCH_IDS[k]), t) for k in range(len(Defs.BENCH_IDS))
                                      for t in range(1, int(Defs.BENCH_MAX[k]) + 1)) | {str(Defs.OMNI), "Skyy_Accessory_Bag"} | set(LANS)
    check(set(current) == want and len(current) == 71, "H the current items are the 40 boosters, the bench accessories, Omni, the bag and "
          "(0.5.4) the 4 Lanterns: %r" % sorted(set(current) ^ want))
    check(all("Variant" not in items[i] and items[i].get("Categories") == ["Items.Tools"] for i in current), "H the 71 current items stay listed")
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

    # ---------------- Y. compare with the 0.5.3 jar (the SET pin): classes and assets (0.5.4)
    if os.path.exists(JAR054):
        run_y055(jar)   # 0.5.5 (0.5.4's run_y054 compared 0.5.3 -> 0.5.4)
    else:
        check(False, "Y no SkyyAccessories-0.5.4.jar next to the build")

    # ---------------- W. the Workbench tab (tools/skyywbtab.py; SkyySacks 0.7.12 on the classpath)
    for l in WB.harness_checks(check, B.SERVER_JAR):
        print(l)

    # ---------------- L. the start sequence twice on a fresh copy of the live data folder: no file churn
    Paths_ = JClass("java.nio.file.Paths")
    if not os.path.isdir(LIVE):
        print("note: no live Skyy_SkyyAccessories folder - L skipped")
    else:
        lm = os.path.join(SCRATCH, "l-mods")     # 0.5.3: laid out like a server (<mods>/Skyy_SkyyAccessories) so the config kit starts too
        d = os.path.join(lm, "Skyy_SkyyAccessories")
        shutil.copytree(LIVE, d)      # read-only source, scratch copy

        def snap(dd):
            out_ = {}
            for root, _ds, fs in os.walk(dd):
                for f in fs:
                    pth = os.path.join(root, f)
                    out_[os.path.relpath(pth, dd)] = open(pth, "rb").read()
            return out_
        before0 = snap(d)
        before = None
        m55first = ""
        P_ = lambda n: JClass("com.skyy.accessories." + n)
        notes = []
        for rnd in (0, 1, 2):   # 0.5.5: round 0 = the first 0.5.5 start (the one-time lantern.height update writes once), then no churn
            if rnd == 1:
                before = snap(d)
            P_("AccStore").DIR = Paths_.get(os.path.join(d, "bags"))
            P_("AccCfg").FILE = Paths_.get(os.path.join(d, "config.properties"))
            m51 = str(P_("AccCfg").migrate051())
            m55 = str(P_("AccCfg").migrate055())
            if rnd == 0:
                m55first = m55
            cs = str(P_("AccCfg").load(True))
            P_("AccNotice").FILE = Paths_.get(os.path.join(d, "notices.properties"))
            P_("AccNotice").load()
            P_("WbTab").start()
            JClass("com.skyy.sacks.WbTab").start()
            P_("CfgPub").start(Paths_.get(lm), None)   # the config kit as setup() starts it (0.5.4: the 10 Lantern rows), then its shutdown
            P_("CfgPub").shutdown()
            notes.append((m51 + " " + cs).strip())
        after = snap(d)
        chg = sorted(k2 for k2 in set(before) | set(after) if before.get(k2) != after.get(k2))
        check(not chg, "L two starts (+ SkyySacks' tab start, + the config kit start / shutdown) on a copy of the live data: no file changed (%d files) %s" % (len(before), chg[:4]))
        print("L. two starts on the live copy: %d files unchanged (%s)" % (len(before), notes[-1][:120]))
        ch0 = sorted(k2 for k2 in set(before0) | set(before) if before0.get(k2) != before.get(k2))
        mk0 = str(P_("AccCfg").M55_MARK_ID).encode("latin-1") in before0.get("config.properties", b"")
        check(all(k2 == "config.properties" or k2.startswith("config-history" + os.sep) or k2 == "config-changes.log" for k2 in ch0) and
              (mk0 or (str(P_("AccCfg").M55_MARK_ID).encode("latin-1") in before["config.properties"] and m55first != "")) and
              any(v_ == before0["config.properties"] for k2, v_ in before.items() if k2.startswith("config-history" + os.sep)) == (not mk0),
              "L 0.5.5 the first start on the live copy: only config.properties (the marker / lantern.height), its History copy and the change "
              "log change: %s - %s" % (ch0[:4], m55first[:100]))


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
    # SkyyGear's OWN parser reads the text into the right stats (0.5.3: 0.1 = the first reader, 0.2 = the SET pin), also from the bridge
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

    # ---- B5. the movement post (Speed + Feather) read by SkyySkills' OWN MoveSync (0.5.3: 0.4.12, the SET pin; the fall-damage owner) and by ours
    um = uid()
    bo = [float(x) for x in Defs.BOOST]
    sp, ju, fa = bo[int(Defs.E_SPEED) * 5 + 4] / 100.0, bo[int(Defs.E_JUMP) * 5 + 4] / 100.0, 0.0 - bo[int(Defs.E_FALL) * 5 + 4] / 100.0
    check(abs(sp - 0.10) < 1e-6 and abs(ju - 0.20) < 1e-6 and abs(fa + 0.40) < 1e-6, "B5 Legendary Speed / Feather: +0.10 speed, +0.20 jump, -0.40 fall")
    Move.post(um, str(Gear.SOURCE), "pct", sp, ju, fa)
    if os.path.exists(SKILLS_JAR):
        try:
            SM = JClass("com.skyy.skills.MoveSync", loader=isolated(SKILLS_JAR))
            r = [float(x) for x in SM.sums(um)]
            check(all(abs(a - b2) < 1e-6 for a, b2 in zip(r, [0.0, 0.10, 0.0, 0.20, 0.0, -0.40])), "B5 SkyySkills %s reads our entry: %r" % (os.path.basename(SKILLS_JAR), r))
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
            check(False, "B5 %s's MoveSync could not be used: %s" % (os.path.basename(SKILLS_JAR), ex_))
    else:
        check(False, "B5 no %s next to its build" % os.path.basename(SKILLS_JAR))

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
    print("B. publishing: gear:extra text + rules + SkyyGear's parser, notes, movement read by SkyySkills' own MoveSync (%s), stat pools, profile switch, relog" % os.path.basename(SKILLS_JAR))


def item_codec(zb):
    """the engine's own Item codec on a bare JVM (0.5.3's N1 machinery, shared by R and Q): every asset store Item.processConfig asks for
    is a never-constructed store whose (indexed) map holds exactly the keys that exist - the qualities of Assets.zip + this jar, the vanilla
    animations and item sound sets; the common-asset registry gets the Icon / Model / Texture paths that Assets.zip has. Returns decode()."""
    if "decode" in CODEC:
        return CODEC["decode"], CODEC["quals"]
    import skyybuild as B
    import zipfile
    from jpype import JClass, JArray, JString, JInt, JObject, JImplements, JOverride
    AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    AN = set(AZ.namelist())
    ITM = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    AS, ILT = JClass("com.hypixel.hytale.assetstore.AssetStore"), JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAM = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR, VRc = JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("com.hypixel.hytale.codec.validation.ValidationResults")
    Paths = JClass("java.nio.file.Paths")
    ArrayList = JClass("java.util.ArrayList")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fk = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestLanStore", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fk.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestLanStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fk))
    FKC = fk.toClass(AS.class_)
    F_AM, F_KTI = DAM.class_.getDeclaredField("assetMap"), ILT.class_.getDeclaredField("keyToIndex")
    F_T, F_M = AS.class_.getDeclaredField("tClass"), AS.class_.getDeclaredField("assetMap")
    F_SM = JClass("com.hypixel.hytale.assetstore.AssetRegistry").class_.getDeclaredField("storeMap")
    F_CA = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry").class_.getDeclaredField("assetByNameMap")
    F_VE = VRc.class_.getDeclaredField("validatorExceptions")
    for f_ in (F_AM, F_KTI, F_T, F_M, F_SM, F_CA, F_VE):
        f_.setAccessible(True)

    @JImplements("java.util.function.IntFunction")
    class Arr(object):
        def __init__(self, c):
            self.c = c

        @JOverride
        def apply(self, n):
            return JArray(self.c)(int(n))

    def install(cname, keys):
        C = JClass(cname)
        m = ILT(Arr(C))
        am, kti = F_AM.get(m), F_KTI.get(m)
        for i, k in enumerate(keys):
            am.put(k, US.allocateInstance(C.class_))
            kti.put(JObject(JString(k), JClass("java.lang.Object")), JInt(i + 1))
        st = US.allocateInstance(FKC)
        F_T.set(st, C.class_)
        F_M.set(st, m)
        try:
            fa = C.class_.getDeclaredField("ASSET_STORE")
            fa.setAccessible(True)
            fa.set(None, st)
        except Exception:
            pass
        F_SM.get(None).put(C.class_, st)

    def ids(prefix):
        return sorted(os.path.basename(n)[:-5] for n in AN if n.startswith(prefix) and n.endswith(".json"))

    quals = sorted(set(ids("Server/Item/Qualities/")) | set(n.rsplit("/", 1)[1][:-5] for n in zb.namelist() if n.startswith("Server/Item/Qualities/")))
    install("com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality", quals)
    install("com.hypixel.hytale.server.core.asset.type.itemanimation.config.ItemPlayerAnimations", ids("Server/Item/Animations/"))
    install("com.hypixel.hytale.server.core.asset.type.itemsound.config.ItemSoundSet", ids("Server/Audio/ItemSounds/"))
    CA = F_CA.get(None)

    def decode(txt, key):
        node = json.loads(txt)
        for p_ in (node.get("Icon"), node.get("Model"), node.get("Texture")):
            if p_ and ("Common/" + p_) in AN:
                CA.put(p_, ArrayList())
        regs = []
        for _i in range(12):
            ei = AEI(Paths.get(key + ".json"), ADT(ITM.class_, key, None))
            try:
                o = ITM.CODEC.decodeJsonAsset(RJR.fromJsonString(txt), ei)
            except Exception as e:
                th = e
                while th.getCause() is not None:
                    th = th.getCause()
                fr = list(th.getStackTrace())
                if "AssetRegistry.getAssetStore" in str(th.getMessage()) and fr and str(fr[0].getMethodName()) == "getAssetMap":
                    install(str(fr[0].getClassName()), [])
                    regs.append(str(fr[0].getClassName()).rsplit(".", 1)[1])
                    continue
                return None, ["exception: %s" % str(th)[:200]], [], regs
            ve = F_VE.get(ei.getValidationResults())
            fails = [] if ve is None else [re.search(r"key=([^,\]]+)", str(x)).group(1) + ": " + str(x)[:220] for x in ve]
            return o, fails, [str(x) for x in ei.getUnknownKeys()], regs
        return None, ["too many stores"], [], regs

    CODEC["decode"], CODEC["quals"] = decode, quals
    return decode, quals


CODEC = {}


def jar_code(jar):
    """every method of the jar as InstructionPrinter text: {SimpleClass.method: code}"""
    import skyybuild as B
    import zipfile
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    IPc, PSc, BOSc = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    code = {}
    for n_ in zipfile.ZipFile(jar).namelist():
        if not n_.endswith(".class"):
            continue
        cc = cp.get(n_[:-6].replace("/", "."))
        sname = str(cc.getSimpleName())
        ms = [(str(mm.getName()), mm) for mm in cc.getDeclaredMethods()]
        if cc.getClassInitializer() is not None:
            ms.append(("<clinit>", cc.getClassInitializer().toMethod("clinit_", cc)))
        for mname, mm in ms:
            bos = BOSc()
            IPc(PSc(bos)).print_(mm)
            code[sname + "." + mname] = code.get(sname + "." + mname, "") + str(bos.toString())
    return code


def run_retired(P, jar, tns, BO, Defs, Store, Admin, jpath, UUID, jarr):
    """0.5.4: R - THE NIGHT VISION RETIREMENT (Skyy: "forget night vision, just do the lantern accessory")."""
    import zipfile
    from jpype import JClass
    zb, z3 = zipfile.ZipFile(jar), zipfile.ZipFile(JAR053)
    items = dict((n.rsplit("/", 1)[1][:-5], json.loads(zb.read(n))) for n in zb.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    items3 = dict((n.rsplit("/", 1)[1][:-5], json.loads(z3.read(n))) for n in z3.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    lang = dict(l.split("=", 1) for l in zb.read("Server/Languages/en-US/server.lang").decode("utf8").splitlines() if "=" in l)
    bridge = Store.bridge()
    # ---------------- R1. the item: the same look and Rare frame, no recipe, hidden from the creative library, the retired name + text
    nv, nv3 = items.get(NVID, {}), items3.get(NVID, {})
    check(nv.get("Quality") == "Skyy_Acc_Rare" and "Recipe" not in nv and nv.get("Variant") is True and "Categories" not in nv and
          all(nv.get(k2) == nv3.get(k2) for k2 in ("Icon", "Model", "Texture", "Quality", "MaxStack", "IconProperties")),
          "R1 the Night Vision item keeps 0.5.3's look and Rare frame, no recipe, now Variant + no Categories (out of the creative library)")
    dsc = lang.get("server.items.%s.description" % NVID, "")
    check(lang.get("server.items.%s.name" % NVID) == lang.get("items.%s.name" % NVID) == "Night Vision Accessory (retired)" and
          lang.get("items.%s.description" % NVID) == dsc and "The Lantern Accessory replaced it" in dsc and "Unequip takes it out" in dsc and
          clean(dsc), "R1 name 'Night Vision Accessory (retired)', tooltip: " + dsc[:100])
    decode, quals = item_codec(zb)
    o, fails, uk, regs = decode(zb.read("Server/Item/Items/Utility/%s.json" % NVID).decode("utf8"), NVID)
    check(o is not None and not fails and not uk and bool(o.isVariant()) and len(list(o.getCategories() or [])) == 0 and
          int(o.getQualityIndex()) == quals.index("Skyy_Acc_Rare") + 1, "R1 it still decodes through the engine's Item codec (variant, no "
          "category, Rare): %s" % (fails + uk)[:2])
    # ---------------- R2. the id rules: a retired accessory
    check(bool(Defs.isRetired(NVID)) and int(Defs.rarityOf(NVID)) == 0 and str(Defs.rarityName(NVID)) == "Does nothing" and
          str(Defs.rarityColor(NVID)) == str(Defs.RETIRED_COLOR) and str(Defs.pretty(NVID)) == "Night Vision Accessory - retired" and
          int(Defs.tierOf(NVID)) == 3 and str(Defs.groupOf(NVID)) == "T:NightVision" and not bool(Defs.isBoosterId(NVID)) and
          not bool(Defs.isLantern(NVID)) and not bool(Defs.isLanternId(NVID)) and int(Defs.familyIndex(Defs.familyOf(NVID))) == -1,
          "R2 the id: retired (rarity 0, 'Does nothing', the retired grey), 'Night Vision Accessory - retired', never a booster / Lantern")
    why, chat = str(Defs.retiredWhy(NVID)), str(Defs.retiredChat(NVID))
    check(why == "Retired - the Lantern Accessory replaced it - craft one at a Workbench" and "Lantern Accessory replaced it" in chat and
          "Unequip takes it out" in chat and clean(why) and clean(chat) and not any(c in why for c in ",:()"),
          "R2 Equip refuses it with the reason (page line without , : ( ) + the chat explanation)")
    # ---------------- R3. the bag: never equipped, a copy already in a bag counts for nothing and Unequip takes it out
    Store.DIR = jpath(SCRATCH, "nv-retired", "bags")
    u = UUID.randomUUID()
    k = str(u)
    check(not bool(Store.canEquipK(u, k, NVID)) and Store.equipK(u, k, NVID) is None and all(x is None for x in Store.snapshot(u)),
          "R3 Equip refuses it (canEquipK / equipK), nothing moves")
    check(bool(Store.stashK(u, k, NVID)) and list(Store.snapshot(u))[0] == NVID and not bool(Store.has(u, NVID)) and
          str(bridge.get("acc:tal:" + k)) == "" and str(bridge.get("acc:has:" + k)) == "",
          "R3 an old copy already in the bag (Skyy's profile 3 has one): acc:fn:has says no, acc:tal / acc:has leave it out")
    rows = [str(x) for x in Defs.bonusRows(Store.snapshot(u))]
    check(rows[:2] == ["Night Vision", "retired - take it out"] and all(x == "" for x in rows[2:]) and int(Defs.lanBest(Store.snapshot(u))) == 0,
          "R3 the bag page row says it is retired; it lights nothing (lanBest 0): %r" % rows[:2])
    Store.stashK(u, k, LANS[1])
    rows2 = [str(x) for x in Defs.bonusRows(Store.snapshot(u))]
    check(rows2[:4] == ["Lantern", str(Defs.lanRow(2)), "Night Vision", "retired - take it out"], "R3 next to a Lantern: the Lantern row "
          "first, the retired note after: %r" % rows2[:4])
    check(str(Store.unequipK(u, k, 0)) == NVID and str(Defs.modernOf(NVID)) == NVID, "R3 Unequip takes it out (the page gives the same item back)")
    bridge.remove("acc:has:" + k)
    bridge.remove("acc:tal:" + k)
    # ---------------- R4. Skyy's live bags (a scratch copy): the Night Vision in profile 3 stays where it is and does nothing
    lb = os.path.join(LIVE, "bags")
    hits = []
    if os.path.isdir(lb):
        cpy = os.path.join(SCRATCH, "nv-live-bags")
        shutil.copytree(lb, cpy)
        Store.DIR = jpath(cpy)
        Store.BAGS.clear()
        for f in sorted(os.listdir(cpy)):
            if not f.endswith(".properties") or f.endswith(".more.properties"):
                continue
            key = f[:-11]
            uu = UUID.fromString(key[:36])
            s_ = list(Store.slotsK(uu, key))
            if NVID in s_:
                hits.append((key, s_.index(NVID)))
                check(int(Defs.lanBest(jarr(s_))) == 0 and [str(x) for x in Defs.bonusRows(jarr(s_))][:2] == ["Night Vision", "retired - take it out"]
                      and not bool(Store.canEquipK(uu, key, NVID)), "R4 live bag %s: the Night Vision in slot %d is retired - no light, "
                      "its row says so" % (key, s_.index(NVID) + 1))
        Store.BAGS.clear()
        before = dict((f, open(os.path.join(cpy, f), "rb").read()) for f in os.listdir(cpy))
        check(all(open(os.path.join(lb, f), "rb").read() == before[f] for f in before), "R4 the live bag files were only read (the copy equals them)")
    print("R4. live bags: %s" % (", ".join("%s slot %d" % h_ for h_ in hits) or "no Night Vision found"))
    # ---------------- R5. give / lines / defs
    check(str(Admin.giveable(NVID)) == str(Defs.NV_GIVE) and "Lantern" in str(Defs.NV_GIVE) and int(Admin.giveFn(UUID.randomUUID(), NVID, 1)) == 0,
          "R5 /accessories give and acc:fn:give refuse it: " + str(Defs.NV_GIVE))
    check(all(bool(Defs.isNvName(w)) for w in ("NightVision", "night_vision", "Night-Vision", "NV")) and not bool(Defs.isLanName("NightVision")),
          "R5 the old givetier names are still recognised - the command answers with the retirement")
    gsrc = open(BUILD, encoding="utf8").read()
    gt = gsrc[gsrc.index("public static void giveCmd("):gsrc.index("# acc:fn:give (spec 5.9)")]
    check("if (li < 0 && !lnl && @PKG@.AccDefs.isNvName(tk[1])) { msg(pr, @PKG@.AccDefs.NV_GIVE); return; }" in gt, "R5 givetier NightVision -> the retirement message")
    check("NightVision" not in str(Defs.defsText()) and not any("Night Vision" in str(x) or "NightVision" in str(x) for x in Defs.linesText(True)),
          "R5 acc:defs and /accessories lines no longer list it")
    # ---------------- R6. the jar: no light code left
    names = [n for n in zb.namelist() if n.endswith(".class")]
    code = jar_code(jar)
    check(not any(n.endswith(("/AccNv.class", "/AccNightVision.class")) for n in names) and
          not any("EntityViewer.queueUpdate" in t_ or "EntityViewer.queueRemove" in t_ for t_ in code.values()),
          "R6 AccNv / AccNightVision are gone, nothing queues a light on an entity viewer any more")
    fl = [str(f.getName()) for f in JClass(P + ".AccDefs").class_.getDeclaredFields()] + [str(f.getName()) for f in JClass(P + ".AccCfg").class_.getDeclaredFields()]
    check(not any(x in fl for x in ("LINE_NIGHTVISION", "NV_RADIUS", "NV_RED", "NV_REFRESH", "NV_KEYS", "NV_SWITCH")) and "NV_ID" in fl,
          "R6 the Night Vision settings fields are gone (the id stays)")
    print("R. Night Vision retired: item, id rules, bag, live bags, give / lines / defs, no light code")


def run_lantern(P, jar, tns, BO, Defs, Store, Cfg, jpath, UUID, jarr):
    """0.5.4: Q - THE LANTERN (the light model = the build's, the torch from Assets.zip through the engine's parser, the items through the
    Item codec, and the glow + the helper EXECUTED by the jar's own systems on a REAL engine ECS world)."""
    import skyybuild as B
    import zipfile, random, struct
    from jpype import JClass, JArray, JString, JByte, JLong, JImplements, JOverride
    tal = lambda f, w: "Skyy_Talisman_%s_%s" % (f, w)
    zb = zipfile.ZipFile(jar)
    AZ = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    bridge = Store.bridge()
    Lan, Mark, MarkSup = JClass(P + ".AccLantern"), JClass(P + ".AccLanternMark"), JClass(P + ".AccLanternMarkSup")
    f32 = lambda x: struct.unpack("<f", struct.pack("<f", x))[0]

    # ---------------- Q1. the light model and the tier table = the build script's Python (exec'd from it)
    src = open(BUILD, encoding="utf8").read()
    a_, b_ = src.index("# ---- 0.5.3 NIGHT VISION, RETIRED in 0.5.4"), src.index("CAP = 60          # 0.5: bag STORAGE slots")
    L = {"print": lambda *x, **kw: None}
    exec(compile(src[a_:b_], BUILD + " [LANTERN block]", "exec"), L)
    ll, lml, lre, lso, lke = L["lan_light"], L["lan_maxlevel"], L["lan_reach"], L["lan_solve"], L["lan_key"]
    DEF, FIELDS, KEYS = L["LAN_DEF"], L["LAN_FIELDS"], L["LAN_KEYS"]
    bad, n_ = [], 0
    for lv in list(range(0, 256, 7)) + [11, 15, 31, 72, 208, 255]:
        for d in (-1.0, 0.0, 0.3, 1.5, 2.9, 3.0, 6.99, 7.33, 11.0, 14.2, 35.0, 120.7, 123.0, 160.0, 300.0):
            n_ += 1
            if float(Defs.lanLight(lv, d)) != ll(lv, d):
                bad.append(("light", lv, d))
    for dist in (0.0, 2.0, 11.0, 15.0, 35.0, 120.0, 160.0):
        for cap in (0.0, 0.05, 0.416, 0.551, 0.764, 2.0, 99.0):
            n_ += 1
            if int(Defs.lanMaxLevel(dist, cap)) != lml(dist, cap):
                bad.append(("max", dist, cap))
    for lv in (0, 1, 11, 15, 31, 72, 208, 255):
        for h in (0.0, 5.0, 14.0, 38.0, 123.0, 160.0):
            n_ += 1
            if float(Defs.lanReach(lv, h)) != lre(lv, h):
                bad.append(("reach", lv, h))
    lhk = L["lan_hkey"]
    for lv in range(-3, 300):
        n_ += 2
        if int(Defs.lanKey(lv)) != lke(lv):
            bad.append(("key", lv))
        if int(Defs.lanHKey(lv)) != lhk(lv):
            bad.append(("hkey", lv))
    check(not bad, "Q1 the jar's light model = the build's Python model to the last bit on %d inputs %r" % (n_, bad[:4]))

    def set_lan(vals):
        for f_, v_ in zip(FIELDS, vals):
            setattr(Defs, f_, int(v_))
        Defs.lanTable()

    def tab(t):
        return int(Defs.LAN_TAB_H[t]), int(Defs.LAN_TAB_L[t]), float(Defs.LAN_TAB_R[t])
    DEF054 = [11, 11, 11, 11, 6, 12, 24, 48, 128, 255, 1]   # 0.5.5: the carried 0.5.4 checks run in the 0.5.4 light layout
    check(len(DEF) == 11 and DEF[:8] == DEF054[:8] and DEF[8:] == [64, 96, 7], "Q1 0.5.5 defaults: height 64, edge 96, lights 7 %r" % DEF)
    set_lan(DEF054)
    want0 = [(h, l, f32(r)) for h, l, r in [lso(DEF054[t - 1], DEF054[3 + t], 128) for t in range(1, 5)]]
    check([tab(t) for t in range(1, 5)] == want0 and [h for h, l, r in want0] == [0, 14, 38, 123] and [l for h, l, r in want0] == [0, 31, 72, 208],
          "Q1 the jar's default tier table = the build's: Normal glow only, Unique 31 at 14 up, Rare 72 at 38, Legendary 208 at 123: %r" % [tab(t) for t in range(1, 5)])
    check([int(Defs.lanShown(t)) for t in range(1, 5)] == [6, 12, 24, 48], "Q1 shown reach 6 / 12 / 24 / 48 blocks")
    rnd = random.Random(54)
    badt = []
    for _ in range(150):
        vals = [rnd.randint(0, 15) for _q in range(4)] + [rnd.randint(0, 64) for _q in range(4)] + [rnd.randint(8, 160)]
        set_lan(vals)
        for t in range(1, 5):
            h, l, r = lso(vals[t - 1], vals[3 + t], vals[8])
            if tab(t) != (h, l, f32(r)):
                badt.append((vals, t, tab(t), (h, l, r)))
            if h > 0 and ll(l, h - 3.0) > ll(vals[t - 1] if vals[t - 1] > 0 else 11, 0.3):
                badt.append(("cap broken", vals, t))
    check(not badt, "Q1 150 random settings: the jar's table = the Python solver, and the brightness cap always holds: %r" % badt[:2])
    set_lan([11, 11, 11, 11, 0, 3, 12, 48, 128])
    check(int(Defs.lanShown(1)) == 6 and int(Defs.lanShown(2)) == 6 and "lights about 6 blocks" in str(Defs.lanText(1)) and
          int(Defs.LAN_TAB_H[1]) == 0 and int(Defs.LAN_TAB_H[2]) == 0,
          "Q1 nit: a reach row below the torch glow's own reach (0, 3) shows what the glow lights (about 6 blocks), never 'about 0 blocks'")
    set_lan(DEF054)
    ep = int(Defs.LAN_EPOCH)
    Defs.lanTable()
    check(int(Defs.LAN_EPOCH) == ep, "Q1 the table is only rebuilt when a setting changed (epoch %d)" % ep)

    # ---------------- Q2. the torch: Assets.zip -> the engine's own parser -> our default glow
    CL = JClass("com.hypixel.hytale.protocol.ColorLight")
    CPU = JClass("com.hypixel.hytale.server.core.asset.util.ColorParseUtil")
    lights = {}
    for ti in ("Furniture_Crude_Torch", "Wood_Torch_Wall"):
        nm = [n for n in AZ.namelist() if n.startswith("Server/Item/Items/") and n.endswith("/" + ti + ".json")][0]
        lights[ti] = json.loads(AZ.read(nm).decode("utf-8-sig"))["BlockType"]["Light"]
    c = CL()
    CPU.hexStringToColorLightDirect(c, "#ba9")
    rgb = (int(c.red) & 255, int(c.green) & 255, int(c.blue) & 255)
    check(all(v.get("Color") == "#ba9" and v.get("Radius") == 0 for v in lights.values()) and rgb == (11, 10, 9),
          "Q2 the vanilla torch (Crude Torch, Wooden Torch): Light #ba9 radius 0 -> ColorParseUtil.hexStringToColorLightDirect -> levels %r" % (rgb,))
    bl = lambda x: JByte(x if x < 128 else x - 256)
    g = Defs.lanColor(Defs.lanKey(11))
    check((int(g.radius) & 255, int(g.red) & 255, int(g.green) & 255, int(g.blue) & 255) == (1, 11, 10, 9) and bool(Defs.lanOurs(g)),
          "Q2 the default glow = the torch's 11 / 10 / 9 + radius 1 (the owner mark)")
    check(not bool(Defs.lanOurs(CL(bl(0), bl(11), bl(10), bl(9)))) and not bool(Defs.lanOurs(CL(bl(12), bl(11), bl(10), bl(9)))) and
          not bool(Defs.lanOurs(CL(bl(1), bl(11), bl(11), bl(9)))) and not bool(Defs.lanOurs(None)) and bool(Defs.lanOurs(Defs.lanColor(Defs.lanKey(208)))),
          "Q2 the owner mark: a vanilla torch light (radius 0), a builder light (radius 12) and a near miss are not ours; our glow at any level is")
    check(all(min((int(Defs.lanKey(lv)) >> 16) & 255, (int(Defs.lanKey(lv)) >> 8) & 255, int(Defs.lanKey(lv)) & 255) >= 1 for lv in range(1, 256)),
          "Q2 every channel of every light we send is >= 1, so the radius-1 mark changes nothing on the client (max(channel, radius))")
    # the fix round, review finding 1: the helper's light is WHITE - the client fades each colour channel on its own, so the torch tint
    # (red > green > blue) reached the far ground as red only
    hks = [(lv, int(Defs.lanHKey(lv))) for lv in range(1, 256)]
    check(all((k >> 24) & 255 == 1 and (k >> 16) & 255 == (k >> 8) & 255 == k & 255 == lv for lv, k in hks) and
          int(Defs.lanHKey(0)) == int(Defs.lanHKey(1)) and int(Defs.lanHKey(300)) == int(Defs.lanHKey(255)),
          "Q2 the helper light: red = green = blue = the level (1-255) + the radius-1 mark")
    exe = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Client", "HytaleClient.exe")
    if os.path.exists(exe):
        with open(exe, "rb") as fx:          # read-only
            exb = fx.read()
        i0 = exb.find(b"float getChannelLightNEW(")
        blk = exb[i0:i0 + 3000].decode("latin-1") if i0 >= 0 else ""
        check(i0 >= 0 and "return pow(max(0.0, 1.0 - distanceToLight / maxChannelLight), 1.5f) * maxChannelLight * 0.8;" in blk and
              "float fixedDistanceToLight = distanceToLight  * 0.1f;" in blk and
              all(("currentDynamicLightColor.%s = getChannelLightNEW(fixedDistanceToLight, Color.%s);" % (c, c)) in blk for c in "rgb") and
              "dynamicLightColor = max (dynamicLightColor, currentDynamicLightColor);" in blk,
              "Q2 the client's own shader text (HytaleClient.exe LightCluster, read-only): 0.8 C max(0, 1 - 0.1 d / C)^1.5 for EACH colour "
              "channel with its own C, lights combined with max")
    else:
        print("note: no HytaleClient.exe - the shader text check of Q2 is skipped")
    lrgb = L["lan_rgb"]
    old_, new_ = lrgb(int(Defs.lanKey(208)), 123.0), lrgb(int(Defs.lanHKey(208)), 123.0)
    surf = lambda c3: tuple(round(min(1.0, 3.0 * c_), 2) for c_ in c3)
    check(old_[0] > 0.4 and old_[1] < 0.1 * old_[0] and old_[2] == 0.0 and new_[0] == new_[1] == new_[2] == old_[0],
          "Q2 the ground right under the Legendary helper (123 blocks): the old torch tint lit it red %r (surface %r), the white light "
          "lights every channel alike %r (surface %r)" % (tuple(round(x, 3) for x in old_), surf(old_), tuple(round(x, 3) for x in new_), surf(new_)))
    wb_ = []
    for h_, l_, r_ in L["LAN_TABLE"][2:]:
        for d_ in [float(h_) + k_ * 0.5 for k_ in range(0, int(0.635 * l_ - h_) * 2)]:
            c3 = lrgb(int(Defs.lanHKey(l_)), d_)
            if not c3[0] == c3[1] == c3[2]:
                wb_.append((h_, l_, d_, c3))
    check(not wb_, "Q2 every distance from straight below to the cut-off, all three default helpers: red = green = blue %r" % wb_[:2])

    # ---------------- Q3. the four items through the engine's Item codec
    items = dict((n.rsplit("/", 1)[1][:-5], json.loads(zb.read(n))) for n in zb.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    decode, quals = item_codec(zb)
    for t, i in enumerate(LANS, 1):
        o, fails, uk, regs = decode(zb.read("Server/Item/Items/Utility/%s.json" % i).decode("utf8"), i)
        q = ["Skyy_Acc_Normal", "Skyy_Acc_Unique", "Skyy_Acc_Rare", "Skyy_Acc_Legendary"][t - 1]
        check(o is not None and not fails and not uk and str(o.getId()) == i and not bool(o.isVariant()) and
              [str(x) for x in o.getCategories()] == ["Items.Tools"] and int(o.getQualityIndex()) == quals.index(q) + 1 and
              str(o.getModel()) == items[i]["Model"] and str(o.getModel()).startswith("Blocks/Decorative_Sets/"),
              "Q3 %s decodes through Item.CODEC (a vanilla lantern's block model %s, %s): %s" % (i, items[i]["Model"], q, (fails + uk)[:2]))

    # ---------------- Q4.. THE REAL ENGINE ECS WORLD: a ComponentRegistry with the engine's component classes (registered like EntityModule
    # does: DynamicLight / NetworkId WITHOUT a codec, TransformComponent / Intangible / Despawn with theirs), two Stores = two worlds, the
    # jar's AccLanternSys + AccLanternHelp registered and ticked by Store.tick (real CommandBuffers, real Refs, real archetypes)
    CR = JClass("com.hypixel.hytale.component.ComponentRegistry")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    DLC = JClass("com.hypixel.hytale.server.core.modules.entity.component.DynamicLight")
    NIDC = JClass("com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId")
    INTC = JClass("com.hypixel.hytale.server.core.modules.entity.component.Intangible")
    DESC = JClass("com.hypixel.hytale.server.core.modules.entity.DespawnComponent")
    DTHC = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    PRF = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TRC = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    ES, ERS = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore"), JClass("com.hypixel.hytale.component.EmptyResourceStorage")
    AR, RR = JClass("com.hypixel.hytale.component.AddReason"), JClass("com.hypixel.hytale.component.RemoveReason")
    V3, Duration, HashSet = JClass("org.joml.Vector3d"), JClass("java.time.Duration"), JClass("java.util.HashSet")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    US = uf.get(None)

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def get(self):
            return self.f()

    reg = CR()
    Lan.T_TC = reg.registerComponent(TC, "Transform", TC.CODEC)
    Lan.T_DL = reg.registerComponent(DLC, Sup(lambda: DLC()))
    Lan.T_NID = reg.registerComponent(NIDC, Sup(lambda: NIDC(0)))
    Lan.T_INT = reg.registerComponent(INTC, "Intangible", INTC.CODEC)
    Lan.T_DES = reg.registerComponent(DESC, "Despawn", DESC.CODEC)
    Lan.T_DEATH = reg.registerComponent(DTHC, Sup(lambda: None))     # (the engine's has a codec that needs the item asset store - presence is what counts)
    Lan.T_PR = reg.registerComponent(PRF, Sup(lambda: None))
    Lan.T_MARK = reg.registerComponent(Mark, MarkSup())             # the jar's own Supplier, like setup()
    Lan.R_TIME = reg.registerResource(TRC, "Time", TRC.CODEC)
    reg.registerSystem(JClass(P + ".AccLanternSys")())
    reg.registerSystem(JClass(P + ".AccLanternHelp")())
    wa, wb = reg.addStore(ES(None), ERS.get()), reg.addStore(ES(None), ERS.get())
    NONSER = reg.getNonSerializedComponentType()
    DT = 1.0 / 30.0
    Store.DIR = jpath(SCRATCH, "lantern-bags")
    Store.BAGS.clear()
    Lan.clearAll()

    def player(w, u, name, x, y, z):
        h = reg.newHolder()
        tc = TC()
        tc.setPosition(V3(x, y, z))
        h.addComponent(Lan.T_TC, tc)
        h.addComponent(Lan.T_PR, PRF(None, u, name, "en-US", None, None))
        return w.addEntity(h, AR.SPAWN)

    def tick(w, n=1):
        for _q in range(n):
            w.tick(DT)

    @JImplements("java.util.function.BiConsumer")
    class Collect(object):
        def __init__(self):
            self.refs = []

        @JOverride
        def accept(self, chunk, cb):
            for i_ in range(int(chunk.size())):
                self.refs.append(chunk.getReferenceTo(i_))

    def helpers(w, owner=None):
        cl = Collect()
        w.forEachChunk(Lan.T_MARK, cl)
        out = []
        for r_ in cl.refs:
            m_ = w.getComponent(r_, Lan.T_MARK)
            if owner is None or (m_ is not None and m_.owner is not None and m_.owner.equals(owner)):
                out.append(r_)
        return out

    def gkey(w, r_):
        d_ = w.getComponent(r_, Lan.T_DL)
        return None if d_ is None else int(Defs.lanKeyOf(d_.getColorLight()))

    def pos(w, r_):
        p_ = w.getComponent(r_, Lan.T_TC).getPosition()
        return (float(p_.x()), float(p_.y()), float(p_.z()))

    def move(w, r_, x, y, z):
        w.getComponent(r_, Lan.T_TC).setPosition(V3(x, y, z))

    def decide_now(u):
        cc = Lan.CLK.get(u)
        if cc is not None:
            cc[0] = 1.0

    def unlimit(u):
        Lan.SPAWNT.remove(u)

    cnt = lambda c_: int(getattr(Lan, c_).get())
    K11 = int(Defs.lanKey(11))                                       # the glow on the player: the torch tint
    K31, K72, K208 = [int(Defs.lanHKey(x)) for x in (31, 72, 208)]    # the helper lights: white (the fix round)
    ua, ub, uc = UUID.randomUUID(), UUID.randomUUID(), UUID.randomUUID()
    ka, kb, kc = str(ua), str(ub), str(uc)
    ra = player(wa, ua, "Alice", 10.5, 64.0, -3.25)

    # ---------------- Q4. no Lantern -> nothing; Normal -> the torch glow ON the player, no helper; never saved
    tick(wa, 35)
    check(gkey(wa, ra) is None and not helpers(wa) and int(wa.getEntityCount()) == 1, "Q4 no Lantern: no light, no helper, one entity")
    check(str(Store.equipK(ua, ka, LANS[0])) == "", "Q4 equip the Normal Lantern into a free slot")
    on0 = cnt("GLOW_ON")
    tick(wa)
    check(gkey(wa, ra) == K11 and not helpers(wa) and cnt("GLOW_ON") == on0 + 1, "Q4 one tick later (the bag change pokes the decision): "
          "the player carries a DynamicLight component = the torch light %08x, no helper" % (gkey(wa, ra) or 0))
    sc = wa.copySerializableEntity(ra)
    check(bool(wa.getArchetype(ra).contains(Lan.T_DL)) and not bool(sc.getArchetype().contains(Lan.T_DL)) and bool(sc.getArchetype().contains(Lan.T_TC)),
          "Q4 the player's saved copy (copySerializableEntity, what logout / a chunk save writes) has no light: DynamicLight has no codec")
    tick(wa, 40)
    check(gkey(wa, ra) == K11 and cnt("GLOW_ON") == on0 + 1 and cnt("GLOW_SET") == 0, "Q4 40 more ticks: the light is set once, never re-sent")

    # ---------------- Q5. Unique -> the helper: one hidden entity 14 blocks up with light 31; its parts; never saved
    check(str(Store.equipK(ua, ka, LANS[1])) == LANS[0], "Q5 the Unique Lantern swaps the Normal one out (it comes back)")
    sp0 = cnt("SPAWNS")
    tick(wa)
    hs = helpers(wa)
    check(len(hs) == 1 and cnt("SPAWNS") == sp0 + 1 and gkey(wa, ra) == K11, "Q5 one tick: exactly one helper spawned (CommandBuffer.addEntity), "
          "the glow stays the torch")
    h1 = hs[0] if hs else None
    if h1 is not None:
        arc = wa.getArchetype(h1)
        mk = wa.getComponent(h1, Lan.T_MARK)
        check(pos(wa, h1) == (10.5, 78.0, -3.25) and gkey(wa, h1) == K31, "Q5 the helper sits exactly 14 blocks above the feet with light 31: %r" % (pos(wa, h1),))
        check(all(bool(arc.contains(t_)) for t_ in (Lan.T_TC, Lan.T_DL, Lan.T_NID, Lan.T_INT, Lan.T_DES, Lan.T_MARK, NONSER)) and
              not bool(arc.contains(Lan.T_PR)) and mk.owner.equals(ua) and Lan.HELPER.get(ua) == h1,
              "Q5 its parts: Transform, DynamicLight, NetworkId, Intangible, Despawn, NonSerialized, our marker (owner = the wearer); it is the recorded helper")
        check(not bool(arc.hasSerializableComponents(reg.getData())) and bool(wa.getArchetype(ra).hasSerializableComponents(reg.getData())),
              "Q5 never saved: Archetype.hasSerializableComponents is false for the helper (the chunk saver skips it), true for the player")
        tr = wa.getResource(Lan.R_TIME)
        now0 = tr.getNow()
        check(str(wa.getComponent(h1, Lan.T_DES).getDespawn()) == str(now0.plusSeconds(5)), "Q5 the dead-man DespawnComponent: now + 5 s")
        tr.add(Duration.ofSeconds(3))
        tick(wa)
        check(str(wa.getComponent(h1, Lan.T_DES).getDespawn()) == str(tr.getNow().plusSeconds(5)), "Q5 refreshed every tick (3 s later: new now + 5 s)")
        check(not bool(Mark().owner is not None) and Mark(ua).clone().owner.equals(ua) and MarkSup().get().owner is None,
              "Q5 AccLanternMark: clone keeps the owner, the Supplier makes an empty one (registerComponent's default)")
    # ---------------- Q6. it follows the player every tick
    mv0 = cnt("MOVES")
    path = []
    for step_ in range(1, 31):
        x, y, z = 10.5 + step_ * 0.4, 64.0 + (step_ % 5) * 0.25, -3.25 - step_ * 0.3
        move(wa, ra, x, y, z)
        tick(wa)
        path.append(pos(wa, h1) == (x, y + 14.0, z))
    check(all(path) and cnt("MOVES") == mv0 + 30, "Q6 30 moves, one tick each: the helper is exactly above the player after every tick "
          "(%d of 30 exact, %d moves sent)" % (sum(1 for x_ in path if x_), cnt("MOVES") - mv0))
    move(wa, ra, 22.0, 64.0, -12.0)
    tick(wa)
    mv1 = cnt("MOVES")
    move(wa, ra, 22.005, 64.0, -12.0)
    tick(wa)
    check(cnt("MOVES") == mv1 and pos(wa, h1) == (22.0, 78.0, -12.0), "Q6 a move under 0.02 blocks sends nothing (no needless updates)")
    # the fix round, review finding 3: moved only when more than height / 50 blocks (0.1 - 1.5) off its spot - 14 up: 0.28 - and at once
    # when it is BELOW its spot (closer to the wearer = brighter than the cap allows)
    mvs = []
    for (x_, y_, z_) in ((22.2, 64.0, -12.0), (22.3, 64.0, -12.0), (22.3, 64.05, -12.0), (22.3, 63.85, -12.0)):
        m0_ = cnt("MOVES")
        move(wa, ra, x_, y_, z_)
        tick(wa)
        mvs.append((cnt("MOVES") - m0_, pos(wa, h1)))
    check([m_ for m_, p_ in mvs] == [0, 1, 1, 0] and mvs[0][1] == (22.0, 78.0, -12.0) and mvs[1][1] == (22.3, 78.0, -12.0) and
          mvs[2][1] == (22.3, 78.05, -12.0) and mvs[3][1] == (22.3, 78.05, -12.0),
          "Q6 14 up (threshold 0.28 blocks): 0.2 sideways waits, 0.3 moves, a rise of 0.05 moves at once, a drop of 0.2 waits: %r" % mvs)
    move(wa, ra, 22.0, 64.0, -12.0)
    tick(wa)
    check(pos(wa, h1) == (22.0, 78.0, -12.0), "Q6 back on its spot")
    # ---------------- Q7. Rare, Legendary; the world top; no room
    rl0 = cnt("RELIT")
    Store.equipK(ua, ka, LANS[2])
    tick(wa)
    check(len(helpers(wa)) == 1 and Lan.HELPER.get(ua) == h1 and pos(wa, h1)[1] == 64.0 + 38 and gkey(wa, h1) == K72 and cnt("RELIT") == rl0 + 1,
          "Q7 Rare: the SAME helper moves to 38 up and its light becomes 72 (setColorLight)")
    Store.equipK(ua, ka, LANS[3])
    tick(wa)
    check(pos(wa, h1)[1] == 64.0 + 123 and gkey(wa, h1) == K208, "Q7 Legendary: 123 up, light 208")
    # finding 3 on a walk: 300 ticks at 4.3 blocks a second with the Legendary helper (123 up: threshold 1.5 blocks)
    m0_, off_, low_ = cnt("MOVES"), 0.0, 0.0
    for k_ in range(1, 301):
        x_ = 22.0 + k_ * (4.3 / 30.0)
        move(wa, ra, x_, 64.0, -12.0)
        tick(wa)
        hp_ = pos(wa, h1)
        off_ = max(off_, math.sqrt((hp_[0] - x_) ** 2 + (hp_[1] - 187.0) ** 2 + (hp_[2] + 12.0) ** 2))
        low_ = max(low_, 187.0 - hp_[1])
    nmv = cnt("MOVES") - m0_
    check(nmv <= 32 and off_ <= 1.5 + 1e-9 and low_ <= 0.0, "Q7 a 300-tick walk with Legendary: %d moves sent (the old rule: 300), the helper at "
          "most %.2f blocks off its spot and never below it" % (nmv, off_))
    print("Q7. a 300-tick walk at 4.3 blocks a second with the Legendary helper: %d moves sent (one a tick before the fix round), at most %.2f "
          "blocks off its spot" % (nmv, off_))
    move(wa, ra, 22.0, 64.0, -12.0)
    tick(wa)
    check(pos(wa, h1) == (22.0, 187.0, -12.0), "Q7 back at the start: the helper on its spot again")
    move(wa, ra, 22.0, 300.0, -12.0)
    tick(wa)
    capL = int(Defs.lanMaxLevel(18.0 - 3.0, float(Defs.lanCap(4))))
    check(pos(wa, h1)[1] == 318.0 and gkey(wa, h1) == int(Defs.lanHKey(capL)) and ll(capL, 15.0) <= ll(11, 0.3) and capL < 208,
          "Q7 the wearer at y 300: the helper stops at y 318 (inside the world) and its light drops to %d so the cap still holds" % capL)
    hr0 = cnt("HREMOVES")
    move(wa, ra, 22.0, 316.0, -12.0)
    tick(wa)
    check(not helpers(wa) and Lan.HELPER.get(ua) is None and cnt("HREMOVES") == hr0 + 1 and gkey(wa, ra) == K11,
          "Q7 the wearer at y 316 (2 blocks of room): no helper (removed), the glow stays")
    move(wa, ra, 22.0, 64.0, -12.0)
    unlimit(ua)
    tick(wa)
    hs = helpers(wa)
    h1 = hs[0] if hs else None
    check(len(hs) == 1 and pos(wa, h1) == (22.0, 187.0, -12.0), "Q7 back down: a new helper at 123 up")
    # ---------------- Q8. Server Setup numbers change -> everyone re-decides; the switch
    Defs.LAN_REACH4 = 24
    decide_now(ua)
    tick(wa)
    h, l, r = lso(11, 24, 128)
    check((h, l) == (38, 72) and pos(wa, h1)[1] == 64.0 + h and gkey(wa, h1) == int(Defs.lanHKey(l)), "Q8 Legendary reach set to 24: the table is "
          "rebuilt and the helper drops to %d up, light %d" % (h, l))
    Defs.LAN_GLOW4 = 15
    decide_now(ua)
    gs0 = cnt("GLOW_SET")
    tick(wa)
    h, l, r = lso(15, 24, 128)
    check(gkey(wa, ra) == int(Defs.lanKey(15)) and cnt("GLOW_SET") == gs0 + 1 and gkey(wa, h1) == int(Defs.lanHKey(l)) and pos(wa, h1)[1] == 64.0 + h,
          "Q8 Legendary glow 15: our light on the player changes in place (setColorLight), the helper follows the higher cap (%d at %d)" % (l, h))
    Defs.LAN_GLOW4, Defs.LAN_REACH4 = 11, 48
    Defs.LINE_LANTERN = False
    decide_now(ua)
    tick(wa)
    check(gkey(wa, ra) is None and not helpers(wa), "Q8 line.Lantern off: the glow and the helper go")
    Defs.LINE_LANTERN = True
    decide_now(ua)
    unlimit(ua)
    tick(wa, 2)
    hs = helpers(wa)
    h1 = hs[0] if hs else None
    check(gkey(wa, ra) == K11 and len(hs) == 1 and pos(wa, h1)[1] == 64.0 + 123 and gkey(wa, h1) == K208, "Q8 back on: torch glow + Legendary helper")
    # ---------------- Q9. death: off at once; back after the respawn
    dc = US.allocateInstance(DTHC.class_)
    wa.addComponent(ra, Lan.T_DEATH, dc)
    tick(wa)
    check(gkey(wa, ra) is None and not helpers(wa), "Q9 the player dies (DeathComponent): glow and helper gone the next tick")
    tick(wa, 40)
    check(gkey(wa, ra) is None and not helpers(wa), "Q9 nothing comes back while dead")
    wa.removeComponent(ra, Lan.T_DEATH)
    unlimit(ua)
    tick(wa, 32)
    hs = helpers(wa)
    h1 = hs[0] if hs else None
    check(gkey(wa, ra) == K11 and len(hs) == 1, "Q9 respawned (DeathComponent gone): back within a second")
    # ---------------- Q10. profile switch: the other profile's bag decides (SkyyProfiles' key function + epoch on the bridge)
    @JImplements("java.util.function.Function")
    class Key(object):
        def __init__(self):
            self.k = ka

        @JOverride
        def apply(self, x):
            return JString(self.k) if x is not None and x.equals(ua) else JString(str(x))

    kf = Key()
    bridge.put("profile:fn:key", kf)
    bridge.put("profile:epoch:" + ka, JLong(1))
    Store.checkEpoch(ua)
    tick(wa)
    kf.k = ka + "-p2"
    bridge.put("profile:epoch:" + ka, JLong(2))
    check(bool(Store.checkEpoch(ua)), "Q10 SkyyProfiles switches Alice to profile 2 (epoch 2): AccStore republishes (as AccEffects / AccTick do)")
    tick(wa)
    check(gkey(wa, ra) is None and not helpers(wa), "Q10 profile 2's bag has no Lantern: glow and helper gone the next tick")
    kf.k = ka
    bridge.put("profile:epoch:" + ka, JLong(3))
    Store.checkEpoch(ua)
    unlimit(ua)
    tick(wa)
    hs = helpers(wa)
    h1 = hs[0] if hs else None
    check(gkey(wa, ra) == K11 and len(hs) == 1, "Q10 back on profile 1: back the next tick")
    bridge.remove("profile:fn:key")
    bridge.remove("profile:epoch:" + ka)
    # ---------------- Q11. a helper that disappears (chunk unload / despawn) is replaced; a parked copy that comes back is removed
    SysJ = JClass("java.lang.System")
    tick(wa)                                             # the helper placed in Q10 is seen in the world once (a fresh Ref counts as pending)
    unlimit(ua)
    Lan.maySpawn(ua, SysJ.currentTimeMillis())          # as if the helper had just been placed (the limit runs on real time)
    gone0, lim0, sp1 = cnt("GONE"), cnt("LIMITED"), cnt("SPAWNS")
    wa.removeEntity(h1, RR.UNLOAD)
    tick(wa)
    check(cnt("GONE") == gone0 + 1 and not helpers(wa) and cnt("LIMITED") == lim0 + 1 and cnt("SPAWNS") == sp1, "Q11 the helper was unloaded: "
          "noticed; the spawn limit makes the new one wait (one spawn a second): gone +%d, limited +%d, helpers %d" % (
              cnt("GONE") - gone0, cnt("LIMITED") - lim0, len(helpers(wa))))
    unlimit(ua)
    tick(wa)
    hs = helpers(wa)
    h1 = hs[0] if hs else None
    check(len(hs) == 1 and cnt("SPAWNS") == sp1 + 1 and Lan.HELPER.get(ua) == h1, "Q11 a second later: one new helper (%d helpers, %d spawns)" % (
        len(hs), cnt("SPAWNS") - sp1))
    tick(wa)
    hp_ = Lan.HELPER.get(ua)
    unlimit(ua)
    Lan.maySpawn(ua, SysJ.currentTimeMillis())
    wa.removeEntity(hp_, RR.UNLOAD)
    unlimit(ua)
    Lan.HSTATE.get(ua)[1] = 0                            # (as if it had never been seen: just spawned)
    g1 = cnt("GONE")
    tick(wa, 30)
    gw = cnt("GONE") - g1
    tick(wa)
    hs = helpers(wa)
    h1 = hs[0] if hs else None
    check(gw == 0 and cnt("GONE") - g1 == 1 and len(hs) == 1, "Q11 a helper that vanishes before it was ever seen counts as pending for 30 ticks "
          "(its CommandBuffer may not have run), then as gone and is replaced (%d / %d helpers)" % (gw, len(hs)))
    hold = wa.copyEntity(h1)
    dup = wa.addEntity(hold, AR.LOAD)
    o0 = cnt("ORPHANS")
    check(len(helpers(wa)) == 2 and wa.getComponent(dup, Lan.T_MARK).owner.equals(ua), "Q11 a parked copy of the helper comes back (same owner mark)")
    tick(wa)
    check(len(helpers(wa)) == 1 and helpers(wa)[0] == h1 and not dup.isValid() and cnt("ORPHANS") == o0 + 1,
          "Q11 AccLanternHelp removes the copy (not the recorded helper), the recorded one stays")
    # ---------------- Q12. two players; a foreign light is never touched
    rb = player(wa, ub, "Bob", 40.0, 70.0, 40.0)
    Store.equipK(ub, kb, LANS[1])
    tick(wa)
    hb = helpers(wa, ub)
    check(len(helpers(wa)) == 2 and len(hb) == 1 and pos(wa, hb[0]) == (40.0, 84.0, 40.0) and gkey(wa, hb[0]) == K31 and gkey(wa, rb) == K11 and
          helpers(wa, ua) == [h1], "Q12 Bob (Unique) gets his own helper above him; Alice keeps hers")
    Store.unequipK(ub, kb, 0)
    tick(wa)
    check(not helpers(wa, ub) and gkey(wa, rb) is None and helpers(wa, ua) == [h1] and gkey(wa, ra) == K11, "Q12 Bob unequips: only his light and helper go")
    rc = player(wa, uc, "Carol", -20.0, 64.0, 5.0)
    fl = DLC(CL(bl(0), bl(11), bl(10), bl(9)))
    wa.addComponent(rc, Lan.T_DL, fl)
    f0 = cnt("FOREIGN")
    Store.equipK(uc, kc, LANS[1])
    tick(wa)
    check(gkey(wa, rc) == int(Defs.lanKeyOf(CL(bl(0), bl(11), bl(10), bl(9)))) and wa.getComponent(rc, Lan.T_DL) == fl and cnt("FOREIGN") == f0 + 1 and
          len(helpers(wa, uc)) == 1, "Q12 Carol already carries another mod's light: it is left alone (never changed), her reach helper still comes")
    wa.removeComponent(rc, Lan.T_DL)
    decide_now(uc)
    tick(wa)
    check(gkey(wa, rc) == K11, "Q12 that light goes: ours comes at the next decision")
    wa.removeComponent(rc, Lan.T_DL)
    fl2 = DLC(CL(bl(12), bl(11), bl(10), bl(9)))
    wa.addComponent(rc, Lan.T_DL, fl2)
    Store.unequipK(uc, kc, 0)
    tick(wa)
    check(wa.getComponent(rc, Lan.T_DL) == fl2 and not helpers(wa, uc), "Q12 unequip while a builder light sits on her: that light is never "
          "removed, only our helper goes")
    wa.removeEntity(rc, RR.UNLOAD)
    # ---------------- Q13. logout: the helper is removed in its own world; the state is pruned
    o1 = cnt("ORPHANS")
    wa.removeEntity(ra, RR.UNLOAD)
    tick(wa)
    check(not helpers(wa, ua) and cnt("ORPHANS") == o1 + 1, "Q13 Alice logs out (her entity removed): AccLanternHelp removes her helper the next tick")
    online = HashSet()
    online.add(ub)
    Lan.prune(online)
    check(all(getattr(Lan, m_).get(ua) is None for m_ in ("CLK", "WANT", "HELPER", "HSTATE", "OWNER", "HY", "SPAWNT")),
          "Q13 AccTick's prune forgets every map entry of a player who left")
    # ---------------- Q14. world change both ways: the old world removes its own helper, the new world places one; never across stores
    wa.removeEntity(rb, RR.UNLOAD)                       # Bob leaves world A (one entity per player, as in the game)
    ra = player(wa, ua, "Alice", 0.0, 64.0, 0.0)
    unlimit(ua)
    tick(wa)
    ha = helpers(wa, ua)
    rbb = player(wb, ub, "Bob", 5.0, 64.0, 5.0)
    Store.equipK(ub, kb, LANS[2])
    unlimit(ub)
    tick(wb)
    hbb = helpers(wb, ub)
    check(len(ha) == 1 and len(hbb) == 1, "Q14 Alice in world A, Bob (Rare) in world B, one helper each")
    wa.removeEntity(ra, RR.UNLOAD)
    ra2 = player(wb, ua, "Alice", 6.0, 70.0, 6.0)
    unlimit(ua)
    tick(wb)
    check(len(helpers(wb, ua)) == 1 and pos(wb, helpers(wb, ua)[0]) == (6.0, 70.0 + 123, 6.0) and len(helpers(wa, ua)) == 1 and ha[0].isValid()
          and gkey(wb, ra2) == K11, "Q14 Alice moves to world B (world B ticks first): her glow is back on the first tick (a new entity decides at "
          "once), her new helper is in B, the old one in A is untouched by B's systems")
    tick(wa)
    check(not helpers(wa, ua) and not ha[0].isValid() and len(helpers(wb)) == 2 and helpers(wb, ub) == hbb,
          "Q14 world A's own AccLanternHelp removes the old helper (her entity there is gone); Bob's helper in B is untouched")
    wb.removeEntity(ra2, RR.UNLOAD)
    ra = player(wa, ua, "Alice", 1.0, 64.0, 1.0)
    unlimit(ua)
    tick(wa)
    check(len(helpers(wa, ua)) == 1 and len(helpers(wb, ua)) == 1, "Q14 back to A (A ticks first): a new helper in A, B's still there until B ticks")
    tick(wb)
    check(not helpers(wb, ua) and len(helpers(wa, ua)) == 1 and helpers(wb, ub) == hbb, "Q14 then B removes its stale one")
    # ---------------- Q15. a restart: what the chunk saver would write holds no helper and no light; the next start makes fresh ones
    saved = []
    for r_ in [ra] + helpers(wa):
        hh = wa.copySerializableEntity(r_)
        if bool(hh.getArchetype().hasSerializableComponents(reg.getData())):
            saved.append(hh)
    check(len(saved) == 1 and not bool(saved[0].getArchetype().contains(Lan.T_DL)) and not bool(saved[0].getArchetype().contains(Lan.T_MARK)),
          "Q15 the saveable entities of world A = Alice alone, without the light (the helper has no saveable copy)")
    wc = reg.addStore(ES(None), ERS.get())
    for hh in saved:
        hh.addComponent(Lan.T_PR, PRF(None, ua, "Alice", "en-US", None, None))   # (the player ref is rebuilt by the server on join)
        wc.addEntity(hh, AR.LOAD)
    Lan.clearAll()
    rcz = [r_ for r_ in Collect_all(wc)]
    check(not helpers(wc) and all(gkey(wc, r_) is None for r_ in rcz) and len(rcz) == 1, "Q15 the restarted world: no helper, no light")
    tick(wc, 2)
    check(len(helpers(wc, ua)) == 1 and gkey(wc, rcz[0]) == K11, "Q15 the first ticks: a fresh glow and a fresh helper (she still wears it)")
    # ---------------- Q16. the spawn limit, the section walk, the placement rules (pure parts)
    uu = UUID.randomUUID()
    sq = [bool(Lan.maySpawn(uu, t_)) for t_ in (1000, 1500, 2000, 2999, 3000)]
    check(sq == [True, False, True, False, True], "Q16 one spawn a second: %r" % sq)
    for t_ in range(1, 25):
        Lan.maySpawn(uu, 3000 + t_ * 1000)
    st_ = list(Lan.SPAWNT.get(uu))
    check(not bool(Lan.maySpawn(uu, int(st_[0]) + 5000)) and bool(Lan.maySpawn(uu, int(st_[0]) + 10000)) and bool(Lan.LIMIT_WARNED),
          "Q16 past 20 spawns in a minute: one WARN and one spawn per 10 s")
    check(int(Lan.walk(2, 6, (1 << 2) | (1 << 3) | (1 << 6))) == 6 and int(Lan.walk(2, 6, (1 << 2) | (1 << 4))) == 4 and
          int(Lan.walk(2, 6, 1 << 2)) == 2 and int(Lan.walk(3, 3, 0)) == 3, "Q16 walk: the highest loaded + ticking section from the target down")
    py = lambda feet, want: float(Lan.pickY(uu, None, 0.0, feet, 0.0, want))
    pys = [py(64.0, 14), py(300.0, 123), py(316.0, 14), py(-10.0, 14), py(-20.0, 14), py(-30.0, 14), py(200.0, 4), py(200.0, 5)]
    check(pys == [78.0, 318.0, -1.0, 4.0, -1.0, -1.0, -1.0, 205.0], "Q16 pickY: want blocks up, never above y 318, never below y 1, at least "
          "5 blocks of room: %r" % pys)
    check(all(bool(Lan.sectionOk(None, 0, cy, 0)) for cy in range(10)) and not bool(Lan.sectionOk(None, 0, -1, 0)) and
          not bool(Lan.sectionOk(None, 0, 10, 0)), "Q16 sections 0-9 only (the world's 10 sections)")
    # ---------------- Q16b. the fix round, review finding 4: floating-point noise ((feet + 123) - feet < 123 in doubles) never lowers the
    # level or re-sends the light; pickY keeps 5 blocks of room at noisy heights
    noisy = [5.0 + k_ * 0.37 for k_ in range(330) if (5.0 + k_ * 0.37 + 123.0) - (5.0 + k_ * 0.37) < 123.0]
    nz5 = [f_ for f_ in (1.0 + k_ * 0.0137 for k_ in range(1, 30000)) if (f_ + 5.0) - f_ < 5.0][:60]
    check(len(noisy) > 20 and len(nz5) > 10 and all(float(Lan.pickY(uu, None, 0.0, f_, 0.0, 5)) > 0.0 for f_ in nz5) and
          all(float(Lan.pickY(uu, None, 0.0, f_, 0.0, 123)) == f_ + 123.0 for f_ in noisy),
          "Q16b pickY at %d / %d heights where (feet + want) - feet comes out below want: never 'no room', never moved" % (len(noisy), len(nz5)))
    rw = rcz[0]
    rl1, sp2, hr2 = cnt("RELIT"), cnt("SPAWNS"), cnt("HREMOVES")
    keys_ = set()
    for k_ in range(600):
        f_ = noisy[k_ % len(noisy)]
        move(wc, rw, 3.25, f_, 7.75)
        tick(wc)
        hh_ = helpers(wc, ua)
        keys_.add(gkey(wc, hh_[0]) if hh_ else None)
    print("Q16b. %d of 330 sampled heights round (feet + 123) - feet below 123; 600 ticks across them: %d relights (the light key stays %08x)"
          % (len(noisy), cnt("RELIT") - rl1, K208))
    check(cnt("RELIT") == rl1 and cnt("SPAWNS") == sp2 and cnt("HREMOVES") == hr2 and keys_ == {K208},
          "Q16b 600 ticks of a Legendary wearer moving between those heights: the light stays %08x, never re-sent (relights +%d, spawns +%d, "
          "removals +%d; the first 0.5.4 build re-sent it on about a fifth of these ticks)" % (K208, cnt("RELIT") - rl1, cnt("SPAWNS") - sp2,
                                                                                            cnt("HREMOVES") - hr2))
    # ---------------- Q16c. review finding 6: sectionOk / sectionMask / pickY on a REAL World + ChunkStore (the engine classes; their
    # section map and chunk Store filled the way the ChunkStore keeps them: LoadState -> the section entity's Ref, NonTicking on it)
    WLDc = JClass("com.hypixel.hytale.server.core.universe.world.World")
    CSc = JClass("com.hypixel.hytale.server.core.universe.world.storage.ChunkStore")
    LSc = JClass("com.hypixel.hytale.server.core.universe.world.storage.ChunkStore$LoadState")
    I3c, SLc, NTKc = (JClass("com.hypixel.hytale.math.data.Int3ObjectOpenHashMap"), JClass("java.util.concurrent.locks.StampedLock"),
                      JClass("com.hypixel.hytale.component.NonTicking"))

    def setf(o_, C_, name_, v_):
        f2 = C_.class_.getDeclaredField(name_)
        f2.setAccessible(True)
        f2.set(o_, v_)
    world = US.allocateInstance(WLDc.class_)
    chs = US.allocateInstance(CSc.class_)
    setf(world, WLDc, "chunkStore", chs)
    setf(chs, CSc, "lock", SLc())
    secmap = I3c()
    setf(chs, CSc, "chunkSections", secmap)
    creg = CR()
    cst = creg.addStore(chs, ERS.get())
    setf(chs, CSc, "store", cst)
    lsk = LSc.class_.getDeclaredConstructor()
    lsk.setAccessible(True)

    def section(cx_, cy_, cz_, ticking=True):
        h_ = creg.newHolder()
        if not ticking:
            h_.addComponent(creg.getNonTickingComponentType(), NTKc.get())
        ls_ = lsk.newInstance()
        setf(ls_, LSc, "reference", cst.addEntity(h_, AR.LOAD))
        secmap.put(cx_, cy_, cz_, ls_)
    for cy_ in range(4):
        section(0, cy_, 0)                                # column 0: sections 0-3 loaded + ticking, 4 NonTicking, 5-9 missing
    section(0, 4, 0, False)
    for cy_ in range(3):
        section(1, cy_, 0)                                # column 1: 0-2 loaded, 3 NonTicking, the rest missing
    section(1, 3, 0, False)
    for cy_ in range(10):
        section(3, cy_, 0)                                # column 3: every section loaded and ticking; column 2: nothing
    oks = [bool(Lan.sectionOk(world, 0, cy_, 0)) for cy_ in range(-1, 11)]
    check(world.getChunkStore() == chs and oks == [False, True, True, True, True, False, False, False, False, False, False, False] and
          int(Lan.sectionMask(world, 0, 0, 2, 5)) == (1 << 2) | (1 << 3) and int(Lan.sectionMask(world, 2, 0, 2, 5)) == (1 << 2) and
          int(Lan.sectionMask(world, 3, 0, 2, 5)) == 0b111100,
          "Q16c the real ChunkStore: loaded + ticking sections are ok, a NonTicking one and missing ones are not %r; the masks walk them" % oks)
    pys2 = []
    for x_ in (10.5, 40.5, 70.5, 100.5):
        uq = UUID.randomUUID()
        pys2.append(float(Lan.pickY(uq, world, x_, 64.3, 10.5, 123)))
    check(pys2 == [127.5, 95.5, 95.5, 64.3 + 123.0], "Q16c pickY 123 up from y 64.3: the top of section 3 (4 is NonTicking, 5 missing) = 127.5; "
          "a NonTicking section 3 = 95.5 (the feet section's top); an unloaded column = the feet section (the player stands in it) 95.5; all "
          "loaded = 187.3: %r" % pys2)
    uq = UUID.randomUUID()
    first = float(Lan.pickY(uq, world, 10.5, 64.3, 10.5, 123))
    section(0, 4, 0, True)                               # section 4 finishes loading and ticks
    seq = [float(Lan.pickY(uq, world, 10.5, 64.3, 10.5, 123)) for _q in range(21)]
    check(first == 127.5 and seq[:20] == [127.5] * 20 and seq[20] == 159.5, "Q16c section 4 starts ticking: the cached walk keeps 127.5 for "
          "20 ticks, then the re-check moves the helper up to 159.5 (the top of section 4): %r" % seq[18:])
    section(0, 4, 0, False)
    # through AccLanternSys: a world whose EntityStore has this World
    wsw = reg.addStore(ES(world), ERS.get())
    ud = UUID.randomUUID()
    rd = player(wsw, ud, "Dana", 10.5, 64.3, 10.5)
    Store.equipK(ud, str(ud), LANS[3])
    tick(wsw, 2)
    hd_ = helpers(wsw, ud)
    lv63 = min(208, int(Defs.lanMaxLevel(63.0 - 3.0, float(Defs.lanCap(4)))))
    check(len(hd_) == 1 and pos(wsw, hd_[0]) == (10.5, 127.5, 10.5) and gkey(wsw, hd_[0]) == int(Defs.lanHKey(lv63)) and lv63 < 208 and
          ll(lv63, 63.0 - 3.0) <= ll(11, 0.3), "Q16c AccLanternSys in that world: Dana's Legendary helper waits at y 127.5 (the highest good section) "
          "with its light lowered to %d so the cap still holds" % lv63)
    wsw.removeEntity(rd, RR.UNLOAD)
    tick(wsw)
    check(not helpers(wsw), "Q16c Dana leaves: her helper goes with her")
    # ---------------- Q17. the bag rules for the Lantern
    ue = UUID.randomUUID()
    ke = str(ue)
    check(str(Store.equipK(ue, ke, LANS[1])) == "" and Store.equipK(ue, ke, LANS[1]) is None and Store.equipK(ue, ke, LANS[0]) is None and
          str(Store.equipK(ue, ke, LANS[3])) == LANS[1] and str(Defs.groupOf(LANS[2])) == "T:Lantern",
          "Q17 one Lantern per bag: equal / lower refused, a higher one swaps the lower one out")
    for li in range(len(BO)):
        Store.stashK(ue, ke, tns["LINE_IDS"][li * 4 + 3])
    Store.stashK(ue, ke, "Skyy_Accessory_Omni")
    sn = Store.snapshot(ue)
    check(int(Defs.lanBest(sn)) == 4 and list(Defs.bestTiers(sn)) == [4] * len(BO) and bool(Store.has(ue, LANS[3])) and
          LANS[3] in str(bridge.get("acc:tal:" + ke)).split(","), "Q17 it stacks with all ten Legendary lines and the Omni; acc:fn:has / acc:tal know it")
    check([str(Defs.pretty(i)) for i in LANS] == ["Normal Lantern Accessory", "Unique Lantern Accessory", "Rare Lantern Accessory",
                                                  "Legendary Lantern Accessory"] and [int(Defs.rarityOf(i)) for i in LANS] == [1, 2, 3, 4] and
          [str(Defs.rarityColor(i)).lower() for i in LANS] == [str(Defs.RARITY_COLOR[t]).lower() for t in range(1, 5)],
          "Q17 names and rarities Normal .. Legendary in the gear colours")
    check([str(Defs.lanRow(t)) for t in range(1, 5)] == ["glows like a torch", "torch glow, lights about 12 blocks", "torch glow, lights about 24 blocks",
                                                       "torch glow, lights about 48 blocks"], "Q17 the bag page rows: %r" % [str(Defs.lanRow(t)) for t in range(1, 5)])
    bridge.remove("acc:has:" + ke)
    bridge.remove("acc:tal:" + ke)
    # ---------------- Q18. the Workbench tab: the jar's WbRank files each Lantern into its rarity tier
    WR = JClass(P + ".WbRank")
    rk = [int(WR.rank(i + "_Recipe_Generated_0")) for i in LANS]
    check(rk == [WB.rank_py(i + "_Recipe_Generated_0") for i in LANS] and all(t * 1000000 < r_ < (t + 1) * 1000000 for t, r_ in enumerate(rk, 1)) and
          all(int(WR.rank(tal("Speed", w) + "_Recipe_Generated_0")) < r_ < t * 1000000 + 200000
              for t, (w, r_) in enumerate(zip(("Common", "Uncommon", "Rare", "Epic"), rk), 1)),
          "Q18 WbRank: Normal Lantern after the Normal Speed Accessory, ... each in its tier (= skyywbtab.rank_py): %r" % rk)
    print("Q4-Q18. the real ECS world: %d spawns, %d moves, %d relights, %d helper removals, %d orphans removed, %d gone, %d foreign lights left alone"
          % (cnt("SPAWNS"), cnt("MOVES"), cnt("RELIT"), cnt("HREMOVES"), cnt("ORPHANS"), cnt("GONE"), cnt("FOREIGN")))


    # ---------------- Q22. 0.5.5 THE SOFT RING: model = the build's Python, the default table, the real ECS world
    lso5, lrr = L["lan_solve5"], L["lan_ring_reach"]
    bad, n_ = [], 0
    for lv in (24, 31, 72, 95, 208):
        for h in (14.0, 38.0, 52.0):
            for m in range(3, 9):
                for rho in (0.5, 10.0, 27.5, 41.0):
                    n_ += 1
                    if float(Defs.lanRingReach(lv, h, m, rho)) != lrr(lv, h, m, rho):
                        bad.append((lv, h, m, rho))
    check(not bad and [float(x) for x in Defs.LAN_COS] == L["LAN_COS"] and int(Defs.LAN_RING_MAX) == 8 == int(Lan.RING_MAX),
          "Q22 the jar's ring reach = the build's Python to the last bit on %d inputs; cos(pi / M) the same literals %r" % (n_, bad[:3]))
    set_lan(DEF)
    tab5 = lambda t: (tab(t), int(Defs.LAN_TAB_M[t]), int(Defs.LAN_TAB_P[t]))
    want5 = [((h, l, f32(r)), m, p) for h, l, r, m, p in L["LAN_TABLE5"][1:]]
    check([tab5(t) for t in range(1, 5)] == want5 and [x[0][:2] for x in want5] == [(0, 0), (14, 31), (38, 72), (52, 95)] and
          [x[1:] for x in want5] == [(0, 0), (0, 0), (0, 0), (5, 55)] and [int(Defs.lanShown(t)) for t in range(1, 5)] == [6, 12, 24, 48] and
          str(Defs.lanRow(4)) == "torch glow, lights about 48 blocks",
          "Q22 the default table = the build's: Unique 31 at 14, Rare 72 at 38 (one light each, as in 0.5.4), Legendary 95 at 52 up + 5 around "
          "at 27.5 blocks; shown 6 / 12 / 24 / 48: %r" % [tab5(t) for t in range(1, 5)])
    check(3.0 * ll(208, 0.635 * 208 - 1e-9) > 0.34 and 3.0 * ll(95, 0.635 * 95 - 1e-9) < 0.17 and
          all(ll(95, 52.0 - 3.0) <= ll(11, 0.3) for _q in (0,)),
          "Q22 the step at the edge of the lit ground (3 x the light at the cut-off): 0.5.4's Legendary 0.34, now 0.16; the cap holds")
    rnd5 = random.Random(55)
    badt = []
    for _ in range(24):
        vals = ([rnd5.randint(0, 15) for _q in range(4)] + [rnd5.randint(0, 64) for _q in range(4)] +
                [rnd5.randint(8, 160), rnd5.randint(24, 255), rnd5.randint(1, 9)])
        set_lan(vals)
        for t in range(1, 5):
            h, l, r, m, p = lso5(vals[t - 1], vals[3 + t], vals[8], vals[9], vals[10])
            if tab5(t) != ((h, l, f32(r)), m, p):
                badt.append((vals, t, tab5(t), (h, l, r, m, p)))
            if h > 0 and (ll(l, h - 3.0) > ll(vals[t - 1] if vals[t - 1] > 0 else 11, 0.3) or l > vals[9] or h > vals[8] or 1 + m > vals[10]):
                badt.append(("rule", vals, t))
    check(not badt, "Q22 24 random settings (+ edge, lights): the jar's table = the Python solver; every light under the brightness cap, "
          "never brighter than the edge row, never above the height row, never more lights than the lights row: %r" % badt[:2])
    set_lan([11, 11, 11, 11, 6, 12, 24, 48, 128, 255, 1])
    check([tab5(t) for t in range(1, 5)] == [((h, l, f32(r)), 0, 0) for h, l, r in [lso(11, x, 128) for x in (6, 12, 24, 48)]] and tab(4)[:2] == (123, 208),
          "Q22 edge 255 + lights 1 + height 128 = the 0.5.4 table exactly (one light, 208 at 123 for Legendary)")
    # the ECS world: Dee wears Legendary in the default layout in a third world
    set_lan(DEF)
    wc = reg.addStore(ES(None), ERS.get())
    ug = UUID.randomUUID()
    kg = str(ug)
    rg = player(wc, ug, "Dee", 100.5, 64.0, -40.5)
    slot = lambda w_, r_: int(w_.getComponent(r_, Lan.T_MARK).slot)
    K95 = int(Defs.lanHKey(95))

    def spot(k_, x_=100.5, y_=64.0, z_=-40.5):
        if k_ == 0:
            return (x_, y_ + 52.0, z_)
        a_ = 2 * math.pi * (k_ - 1) / 5
        return (x_ + 27.5 * math.cos(a_), y_ + 52.0, z_ + 27.5 * math.sin(a_))

    def ring_ok(w_, u_, x_, y_, z_, n_=6):
        hs_ = helpers(w_, u_)
        by_ = dict((slot(w_, r_), r_) for r_ in hs_)
        return (len(hs_) == n_ and sorted(by_) == list(range(n_)) and all(gkey(w_, r_) == K95 for r_ in hs_) and
                all(max(abs(a_ - b_) for a_, b_ in zip(pos(w_, by_[k_]), spot(k_, x_, y_, z_))) < 1e-9 for k_ in by_)), by_
    Store.equipK(ug, kg, LANS[3])
    sp5 = cnt("SPAWNS")
    tick(wc)
    ok_, by = ring_ok(wc, ug, 100.5, 64.0, -40.5)
    rs_ = Lan.RING.get(ug)
    check(ok_ and cnt("SPAWNS") == sp5 + 6 and Lan.HELPER.get(ug) == by.get(0) and rs_ is not None and
          all(rs_[k_ - 1] == by.get(k_) for k_ in range(1, 6)) and all(rs_[k_] is None for k_ in range(5, 8)),
          "Q22 Dee equips Legendary: ONE tick -> 6 hidden lights (one batch): slot 0 = 52 up (the recorded helper), slots 1-5 at 27.5 blocks "
          "around it at angles 2 pi k / 5, all white 95, recorded in RING")
    arcs = [wc.getArchetype(r_) for r_ in by.values()]
    check(all(all(bool(a_.contains(t_)) for t_ in (Lan.T_TC, Lan.T_DL, Lan.T_NID, Lan.T_INT, Lan.T_DES, Lan.T_MARK, NONSER)) and
              not bool(a_.contains(Lan.T_PR)) and not bool(a_.hasSerializableComponents(reg.getData())) for a_ in arcs) and
          all(wc.getComponent(r_, Lan.T_MARK).owner.equals(ug) for r_ in by.values()) and
          int(Mark(ug, 3).clone().slot) == 3 and Mark(ug, 3).clone().owner.equals(ug) and int(Mark(ug).slot) == 0 and int(MarkSup().get().slot) == 0,
          "Q22 every ring light is the 0.5.4 helper entity (Transform, DynamicLight, NetworkId, Intangible, Despawn, NonSerialized, our marker "
          "with the owner + its slot), never saved; AccLanternMark.clone keeps the slot")
    tr = wc.getResource(Lan.R_TIME)
    if tr is not None:
        check(all(str(wc.getComponent(r_, Lan.T_DES).getDespawn()) == str(tr.getNow().plusSeconds(5)) for r_ in by.values()),
              "Q22 each ring light carries the 5 s dead-man (refreshed every tick)")
    tick(wc, 40)
    ok2, by2 = ring_ok(wc, ug, 100.5, 64.0, -40.5)
    check(ok2 and by2 == by and cnt("SPAWNS") == sp5 + 6, "Q22 40 ticks standing still: the same six, nothing re-sent")
    # the walk: 300 ticks at 4.3 blocks a second; each ring light at most its distance / 50 (1.18 blocks) off its spot, never below it
    m0_, off_, low_ = cnt("MOVES"), 0.0, 0.0
    thr = math.sqrt(27.5 ** 2 + 52.0 ** 2) / 50.0
    for k_ in range(1, 301):
        x_ = 100.5 + k_ * (4.3 / 30.0)
        move(wc, rg, x_, 64.0, -40.5)
        tick(wc)
        for kk, r_ in by.items():
            if kk == 0:
                continue
            p_, s_ = pos(wc, r_), spot(kk, x_)
            off_ = max(off_, math.sqrt(sum((a_ - b_) ** 2 for a_, b_ in zip(p_, s_))))
            low_ = max(low_, s_[1] - p_[1])
    nmv = cnt("MOVES") - m0_
    check(off_ <= thr + 1e-9 and low_ <= 0.0 and nmv <= 6 * 40, "Q22 a 300-tick walk at 4.3 blocks a second: %d moves for the six lights, a ring "
          "light at most %.2f blocks off its spot (threshold %.2f), never below it" % (nmv, off_, thr))
    print("Q22. a 300-tick walk with the Legendary ring: %d moves for six lights, at most %.2f blocks off" % (nmv, off_))
    move(wc, rg, 100.5, 64.0, -40.5)
    tick(wc)
    check(ring_ok(wc, ug, 100.5, 64.0, -40.5)[0], "Q22 back at the start: every light on its spot")
    # swap to Rare: the ring goes at once, the light above moves to 38 / 72; back to Legendary: the ring is placed again
    hr0 = cnt("HREMOVES")
    snl = [str(x) if x is not None else None for x in Store.snapshot(ug)]
    Store.unequipK(ug, kg, snl.index(LANS[3]))
    check(str(Store.equipK(ug, kg, LANS[2])) == "", "Q22 Dee takes the Legendary Lantern out and puts a Rare one in")
    tick(wc)
    hs_ = helpers(wc, ug)
    check(len(hs_) == 1 and hs_[0] == by[0] and pos(wc, hs_[0])[1] == 64.0 + 38 and gkey(wc, hs_[0]) == int(Defs.lanHKey(72)) and
          cnt("HREMOVES") == hr0 + 5 and Lan.RING.get(ug) is None and Lan.RSTATE.get(ug) is None,
          "Q22 one tick: the 5 ring lights removed (ringDrop), the light above becomes Rare's 72 at 38")
    check(str(Store.equipK(ug, kg, LANS[3])) == LANS[2], "Q22 the Legendary Lantern swaps the Rare one out")
    Lan.RSPAWNT.remove(ug)
    pre_ = bool(Lan.maySpawnRing(ug, JClass("java.lang.System").currentTimeMillis()))   # a batch just now
    tick(wc)
    lim_ = len(helpers(wc, ug))
    Lan.RSPAWNT.remove(ug)
    tick(wc)
    check(pre_ and lim_ == 1 and ring_ok(wc, ug, 100.5, 64.0, -40.5)[0],
          "Q22 back to Legendary within a second of the last batch: the ring waits (one batch a second), then all five come back together")
    uu5 = UUID.randomUUID()
    sq5 = [bool(Lan.maySpawnRing(uu5, t_)) for t_ in (1000, 1500, 2000, 2999, 3000)]
    for t_ in range(1, 25):
        Lan.maySpawnRing(uu5, 3000 + t_ * 1000)
    st5 = list(Lan.RSPAWNT.get(uu5))
    check(sq5 == [True, False, True, False, True] and not bool(Lan.maySpawnRing(uu5, int(st5[0]) + 5000)) and
          bool(Lan.maySpawnRing(uu5, int(st5[0]) + 10000)) and bool(Lan.RLIMIT_WARNED),
          "Q22 the ring's own limit: one batch a second; past 20 in a minute one WARN and one batch per 10 s")
    # death: everything at once; back after the respawn
    dc5 = US.allocateInstance(DTHC.class_)
    wc.addComponent(rg, Lan.T_DEATH, dc5)
    tick(wc)
    check(not helpers(wc, ug) and gkey(wc, rg) is None and Lan.RING.get(ug) is None, "Q22 Dee dies: all six lights and the glow gone the next tick")
    wc.removeComponent(rg, Lan.T_DEATH)
    unlimit(ug)
    Lan.RSPAWNT.remove(ug)
    tick(wc, 32)
    check(ring_ok(wc, ug, 100.5, 64.0, -40.5)[0] and gkey(wc, rg) == K11, "Q22 respawned: the six are back within a second")
    # Server Setup: lantern.lights 1 -> one light (no ring); edge 255 too -> the 0.5.4-style single light (114 at 64: height 64)
    Defs.LAN_LIGHTS = 1
    Defs.lanTable()
    tick(wc)
    hs_ = helpers(wc, ug)
    check(len(hs_) == 1 and slot(wc, hs_[0]) == 0 and pos(wc, hs_[0])[1] == 64.0 + 52 and Lan.RING.get(ug) is None,
          "Q22 Hidden lights: most = 1 (live): the ring goes, the light above stays")
    Defs.LAN_EDGE = 255
    Defs.lanTable()
    tick(wc)
    h64, l64, r64 = lso(11, 48, 64)
    check(len(helpers(wc, ug)) == 1 and pos(wc, helpers(wc, ug)[0])[1] == 64.0 + h64 and gkey(wc, helpers(wc, ug)[0]) == int(Defs.lanHKey(l64)) and
          (h64, l64) == (64, 114), "Q22 + brightest = 255: Skyy's tested option 2 - one light %d at %d up (reach %.1f)" % (l64, h64, r64))
    set_lan(DEF)
    Lan.RSPAWNT.remove(ug)
    tick(wc)
    check(ring_ok(wc, ug, 100.5, 64.0, -40.5)[0], "Q22 back to the defaults: the ring again")
    # logout: AccLanternHelp removes all six in their own world; prune forgets the ring state
    o5 = cnt("ORPHANS")
    wc.removeEntity(rg, RR.UNLOAD)
    tick(wc)
    online5 = HashSet()
    for u_ in (ua, ub, uc):
        online5.add(u_)
    Lan.prune(online5)
    check(not helpers(wc, ug) and cnt("ORPHANS") == o5 + 6 and all(getattr(Lan, m_).get(ug) is None for m_ in ("RING", "RSTATE", "RSEC", "RSPAWNT", "HELPER")),
          "Q22 Dee logs out: AccLanternHelp (keepSlot) removes all six the next tick; prune forgets RING / RSTATE / RSEC / RSPAWNT")
    # world change both ways: each world removes only its own lights
    rg = player(wc, ug, "Dee", 100.5, 64.0, -40.5)
    tick(wc)
    old6 = helpers(wc, ug)
    wc.removeEntity(rg, RR.UNLOAD)
    rg2 = player(wa, ug, "Dee", 200.5, 70.0, 200.5)
    unlimit(ug)
    Lan.RSPAWNT.remove(ug)
    tick(wa)
    check(len(old6) == 6 and ring_ok(wa, ug, 200.5, 70.0, 200.5)[0] and len(helpers(wc, ug)) == 6 and all(bool(r_.isValid()) for r_ in old6),
          "Q22 Dee moves to world A (A ticks first): six new lights in A, the old six in the old world untouched by A's systems")
    tick(wc)
    check(not helpers(wc, ug) and ring_ok(wa, ug, 200.5, 70.0, 200.5)[0], "Q22 the old world's own AccLanternHelp removes its six")
    wa.removeEntity(rg2, RR.UNLOAD)
    tick(wa)
    check(not helpers(wa, ug), "Q22 Dee leaves world A: all six go with her")
    # a REAL World + ChunkStore (Q16c's): a ring slot only goes into a loaded + ticking section, re-checked every 20 ticks
    wsw2 = reg.addStore(ES(world), ERS.get())
    rk0 = cnt("RSKIPPED")
    rg3 = player(wsw2, ug, "Dee", 10.5, 64.3, 10.5)
    unlimit(ug)
    Lan.RSPAWNT.remove(ug)
    tick(wsw2)
    h3 = helpers(wsw2, ug)
    check(len(h3) == 1 and slot(wsw2, h3[0]) == 0 and pos(wsw2, h3[0]) == (10.5, 64.3 + 52.0, 10.5) and cnt("RSKIPPED") >= rk0 + 5,
          "Q22 Dee in the real-ChunkStore world: the light above fits in section 3 of her column (y 116.3); every ring slot lands in a "
          "NonTicking (column 1) or missing section -> no light there")
    section(1, 3, 0, True)                                # column 1's section 3 starts ticking
    tick(wsw2, 23)
    h3 = helpers(wsw2, ug)
    by3 = dict((slot(wsw2, r_), r_) for r_ in h3)
    check(sorted(by3) == [0, 1] and max(abs(a_ - b_) for a_, b_ in zip(pos(wsw2, by3[1]), (38.0, 64.3 + 52.0, 10.5))) < 1e-9,
          "Q22 that section ticks: within the 20-tick re-check slot 1 (toward +x, x 38) gets its light, the others still wait")
    section(1, 3, 0, False)
    wsw2.removeEntity(rg3, RR.UNLOAD)
    tick(wsw2)
    check(not helpers(wsw2, ug), "Q22 Dee leaves: her lights go with her")
    Store.unequipK(ug, kg, 0)
    Lan.prune(online5)
    set_lan([11, 11, 11, 11, 6, 12, 24, 48, 128, 255, 1])   # the carried Q19 continues where 0.5.4's did
    print("Q22. the soft ring: model = Python, defaults, 24 random settings, six lights on the real ECS world (walk, swap, death, settings, "
          "logout, world change, real ChunkStore sections)")

    # ---------------- Q19. config: the default file, the loader (an existing file untouched), the Server Setup rows through the real kit
    dtx = str(Cfg.DEFAULT_TEXT).split("\n")
    i_lc = [i_ for i_, l_ in enumerate(dtx) if l_.startswith("# Lantern Accessory (0.5.5)")]
    lcom = dtx[i_lc[0]:dtx.index("line.Lantern=true")] if i_lc and "line.Lantern=true" in dtx else []
    check(all(("%s=%d" % kv) in dtx for kv in zip(KEYS, DEF)) and "line.Lantern=true" in dtx and "lantern.shareReach=false" in dtx and
          not any(l_.startswith(("nightVision.", "line.NightVision")) for l_ in dtx) and len(lcom) == 9 and lcom[-1] == str(Cfg.M55_MARK) and
          all(l_.startswith("# ") and "=" not in l_ for l_ in lcom) and "only they see" in " ".join(lcom) and "lantern.shareReach" in " ".join(lcom),
          "Q19 a fresh config.properties carries the 13 Lantern keys (+ lantern.shareReach=false) and no Night Vision key (9 comment lines, "
          "none template-looking)")
    u53 = JArray(JClass("java.net.URL"))(2)
    u53[0] = JClass("java.io.File")(JAR053).toURI().toURL()
    u53[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    t053 = str(JClass(P + ".AccCfg", loader=JClass("java.net.URLClassLoader")(u53, JClass("java.lang.ClassLoader").getPlatformClassLoader())).DEFAULT_TEXT)
    d9 = os.path.join(SCRATCH, "lan-cfg")
    os.makedirs(d9)
    f9 = os.path.join(d9, "config.properties")
    open(f9, "w", newline="\n").write(t053)
    Cfg.FILE = jpath(f9)
    Defs.LAN_REACH2 = 33
    Defs.LINE_LANTERN = False
    r9 = str(Cfg.load(True))
    check(open(f9, "rb").read().decode("latin-1") == t053 and not os.path.exists(os.path.join(d9, "config-changes.log")) and
          [int(getattr(Defs, f_)) for f_ in FIELDS] == DEF and bool(Defs.LINE_LANTERN) and "Lantern" not in r9,
          "Q19 a 0.5.3 server's file (with its Night Vision lines): the Lantern defaults apply, the file is not touched, nothing logged")
    open(f9, "w", newline="\n").write(t053 + "line.Lantern=off\nlantern.glow.Rare=20\nlantern.reach.Unique=x\nlantern.height=4\n"
                                             "lantern.reach.Legendary=60\nline.NightVision=false\nnightVision.radius=12\nlantern.shareReach=true\n")
    r9b = str(Cfg.reload())
    check(bool(Defs.LAN_SHARE) and "Lantern reach light shown to everyone" in r9b, "Q19 lantern.shareReach=true through the loader: shared, and said so")
    check(not bool(Defs.LINE_LANTERN) and int(Defs.LAN_GLOW3) == 15 and int(Defs.LAN_REACH2) == 12 and int(Defs.LAN_HEIGHT) == 8 and
          int(Defs.LAN_REACH4) == 60 and "Lantern switched off" in r9b and
          "Lantern numbers custom (lantern.glow.Rare=15, lantern.reach.Legendary=60, lantern.height=8)" in r9b and "Night Vision" not in r9b,
          "Q19 hand edits through the loader: off, glow 20 -> 15, a bad reach -> 12, height 4 -> 8, the old Night Vision keys ignored: " + r9b[-140:])
    open(f9, "w", newline="\n").write(t053)
    Cfg.reload()
    check([int(getattr(Defs, f_)) for f_ in FIELDS] == DEF and bool(Defs.LINE_LANTERN) and not bool(Defs.LAN_SHARE), "Q19 back to the defaults")
    mods9 = os.path.join(SCRATCH, "lan-kit")
    os.makedirs(os.path.join(mods9, "Skyy_SkyyAccessories"))
    fk9 = os.path.join(mods9, "Skyy_SkyyAccessories", "config.properties")
    open(fk9, "w", newline="\n").write(t053)
    Cfg.FILE = jpath(fk9)
    Cfg.load(True)
    Pub, Fn = JClass(P + ".CfgPub"), JClass(P + ".CfgFn")
    Pub.start(jpath(mods9), None)
    hdr = bridge.get("config:def:SkyyAccessories")
    cats, labels = [str(x) for x in hdr[5]], [str(x) for x in hdr[6]]
    krows = [[str(c_) for c_ in r_] for r_ in hdr[7]]
    lr = [r_ for r_ in krows if r_[2] == "lantern"]
    check("lantern" in cats and "nightvision" not in cats and labels[cats.index("lantern")] == "Lantern" and
          [r_[0] for r_ in lr] == ["line.Lantern"] + KEYS + ["lantern.shareReach"] and [r_[3] for r_ in lr] == ["bool"] + ["int"] * 11 + ["bool"] and
          [r_[4] for r_ in lr] == ["true"] + [str(x) for x in DEF] + ["false"] and [r_[8] for r_ in lr] == [""] * 5 + ["blocks"] * 5 + ["", "", ""] and
          [("adv" in r_[9]) for r_ in lr] == [False] * 9 + [True] * 4 and all("live" in r_[9] for r_ in lr) and
          [r_[1] for r_ in lr][1:3] == ["Normal: glow", "Unique: glow"] and lr[-4][1] == "Hidden light: highest" and
          lr[-3][1] == "Hidden lights: brightest" and lr[-2][1] == "Hidden lights: most" and
          lr[-1][1] == "Others see the reach light",
          "Q19 Server Setup -> Accessories -> Lantern: the switch, glow x4, reach x4 (blocks), the highest helper, 0.5.5's brightest / most and the shared reach "
          "(Advanced), all live")
    fnc = Fn()

    def jobj(*xs):
        a = JArray(JClass("java.lang.Object"))(len(xs))
        for i, v in enumerate(xs):
            a[i] = JString(v) if isinstance(v, str) else v
        return a
    R1_ = [str(x) for x in fnc.apply(jobj("set", "lantern.reach.Rare", "30", None, "console", "yes", "console"))]
    h30, l30, r30 = lso(11, 30, 128)
    Defs.lanTable()
    R2_ = fnc.apply(jobj("set", "lantern.reach.Rare", "65", None, "console", "yes", "console"))
    R3_ = fnc.apply(jobj("set", "lantern.glow.Rare", "16", None, "console", "yes", "console"))
    check(R1_[0] == "ok" and int(Defs.LAN_REACH3) == 30 and tab(3)[:2] == (h30, l30) and str(R2_[0]) == "bad" and str(R3_[0]) == "bad" and
          int(Defs.LAN_REACH3) == 30, "Q19 set through the real kit: Rare reach 30 -> the running field and the tier table (%d at %d); 65 and glow 16 refused" % (l30, h30))
    # the ECS world follows the kit: Bob (Rare, world B) re-decides within a second
    decide_now(ub)
    tick(wb)
    hb2 = helpers(wb, ub)
    check(len(hb2) == 1 and pos(wb, hb2[0])[1] == pos(wb, rbb)[1] + h30 and gkey(wb, hb2[0]) == int(Defs.lanHKey(l30)), "Q19 Bob's Rare helper "
          "moves to the new height / light at his next decision")
    Pub.flush()
    kp = parse_props(open(fk9, "rb").read().decode("latin-1"))
    check(kp.get("lantern.reach.Rare") == "30" and open(fk9, "rb").read().decode("latin-1").startswith(t053), "Q19 the kit wrote the changed key "
          "under its header, the 0.5.3 lines unchanged")
    fnc.apply(jobj("set", "lantern.reach.Rare", "24", None, "console", "yes", "console"))
    RS_ = [str(x) for x in fnc.apply(jobj("set", "lantern.shareReach", "true", None, "console", "yes", "console"))]
    sh_on = bool(Defs.LAN_SHARE)
    fnc.apply(jobj("set", "lantern.shareReach", "false", None, "console", "yes", "console"))
    check(RS_[0] == "ok" and sh_on and not bool(Defs.LAN_SHARE), "Q19 lantern.shareReach through the real kit: on, then off again")
    Pub.shutdown()
    Defs.lanTable()

    # ---------------- Q21. the fix round: THE REACH LIGHT IS THE WEARER'S OWN on the real entity tracker (+ view radius, the dead-man)
    run_tracker(P, Defs, Store, UUID, US, ll)

    # ---------------- Q20. the jar's bytecode
    code = jar_code(jar)
    users = lambda needle: sorted(k_ for k_, t_ in code.items() if any(needle in l_ and ("invoke" in l_ or "new " in l_) for l_ in t_.split("\n")))
    check(not any(k_ in code for k_ in ("AccLanternSys.getGroup", "AccLanternSys.isParallel", "AccLanternHelp.getGroup", "AccLanternHelp.isParallel")),
          "Q20 both systems: no group, isParallel not overridden (EntityTickingSystem's false: the world thread, one entity after another)")
    hd_ = code.get("AccLanternHide.<clinit>", "")
    check("EntityTrackerSystems.FIND_VISIBLE_ENTITIES_GROUP" in code.get("AccLanternHide.getGroup", "") and "AccLanternHide.isParallel" not in code and
          "Order.AFTER" in hd_ and "Class com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$CollectVisible" in hd_ and
          "SystemDependency.<init>" in hd_ and "AccLanternHide.DEPS" in code.get("AccLanternHide.getDependencies", "") and
          "AccLantern.T_EV" in code.get("AccLanternHide.getQuery", "") and
          all(x in code.get("AccLanternHide.tick", "") for x in ("EntityViewer.visible", "PlayerRef.getHiddenPlayersManager", "AccLantern.hideFrom",
                                                                 "Store.getEntityCountFor", "EntityTickingSystem.tick")),
          "Q20 the fix round's AccLanternHide: the find-visible group AFTER CollectVisible, sequential, on every EntityViewer; skips a world "
          "without helpers (getEntityCountFor, then super.tick) and hands each viewer's visible set to AccLantern.hideFrom")
    hf_ = code.get("AccLantern.hideFrom", "")
    hl_ = code.get("AccLantern.helper", "")
    check(all(x in hf_ for x in ("CommandBuffer.getArchetype", "Archetype.contains", "Iterator.remove", "HiddenPlayersManager.isPlayerHidden",
                                 "AccDefs.LAN_SHARE")) and "EntityViewer.queue" not in hf_ and
          "AccDefs.lanHKey" in hl_ and "AccDefs.lanKey(" not in hl_ and "EntityViewer.viewRadiusBlocks" in hl_ and
          all(("double %s" % c_) in hl_ for c_ in ("1.0E-6", "50.0", "0.1", "1.5", "-0.02")) and
          code.get("AccLantern.pickY", "").count("double 1.0E-6") == 2,   # (static final constants: javassist inlines them, like javac)
          "Q20 hideFrom only takes entries out of the visible set (never queues a packet); helper(): the white key, the view radius, the move "
          "threshold, the height margin")
    check(all(x in code.get("AccLanternSys.tick", "") for x in ("ArchetypeChunk.getReferenceTo", "ArchetypeChunk.getComponent", "PlayerRef.getUuid",
                                                               "AccLantern.step")) and
          all(x in code.get("AccLanternHelp.tick", "") for x in ("AccLantern.keep", "CommandBuffer.tryRemoveEntity", "RemoveReason.REMOVE")),
          "Q20 AccLanternSys reads the PlayerRef and calls AccLantern.step; AccLanternHelp asks AccLantern.keep and removes the rest")
    check(users("DynamicLight.<init>") == ["AccLantern.glow", "AccLantern.spawnS"] and users("CommandBuffer.addEntity") == ["AccLantern.spawnS"] and
          users("CommandBuffer.addComponent") == ["AccLantern.glow"] and users("CommandBuffer.tryRemoveComponent") == ["AccLantern.glow"] and
          users("CommandBuffer.tryRemoveEntity") == ["AccLantern.drop", "AccLantern.dropOne", "AccLanternHelp.tick"],
          "Q20 the light is added / removed only in AccLantern.glow, the helper spawned only in AccLantern.spawn, removed only in drop / AccLanternHelp: %r"
          % [users("DynamicLight.<init>"), users("CommandBuffer.addEntity"), users("CommandBuffer.tryRemoveEntity")])
    sp_ = code.get("AccLantern.spawnS", "")   # 0.5.5: spawn = spawnS(slot 0)
    check(all(x in sp_ for x in ("Store.getRegistry", "ComponentRegistry.newHolder", "getNonSerializedComponentType", "NonSerialized.get",
                                 "Holder.ensureComponent", "DespawnComponent.despawnInSeconds", "AccLanternMark.<init>", "AddReason.SPAWN")) and
          "EntityStore.takeNextNetworkId" in code.get("AccLantern.netId", ""),
          "Q20 AccLantern.spawn = the ambient-emitter entity (the store's own registry, NonSerialized, Intangible, NetworkId) + Despawn + our marker")
    check(not any("PersistentDynamicLight" in t_ or "EntityViewer.queue" in t_ for t_ in code.values()), "Q20 never a saved light, never a viewer-only light")
    st_ = code.get("SkyyAccessoriesPlugin.setup", "")
    check(st_.count("ComponentRegistryProxy.registerSystem") == 4 and st_.count("ComponentRegistryProxy.registerComponent") == 1 and
          "Class com.skyy.accessories.AccLanternMark" in st_ and "AccLantern.bind" in st_ and st_.index("AccLantern.bind") < st_.index("registerComponent")
          < st_.index("Class com.skyy.accessories.AccLanternSys") and "Class com.skyy.accessories.AccLanternHide" in st_ and
          "EntityTrackerSystems$EntityViewer.getComponentType" in code.get("AccLantern.bind", "") and "AccLantern.prune" in code.get("AccTick.run", "") and
          "AccLantern.clearAll" in code.get("SkyyAccessoriesPlugin.shutdown", "") and "AccStore.LPOKE" in code.get("AccStore.publish", "") and
          "AccStore.LPOKE" in code.get("AccLantern.step", ""),
          "Q20 setup binds the types (+ the EntityViewer), registers the marker once and 4 systems (AccEffects, AccLanternSys, AccLanternHelp, "
          "AccLanternHide); AccTick prunes, shutdown clears, AccStore.publish pokes, AccLantern.step reads the poke")
    Lan.T_PR = Lan.T_TC = Lan.T_DL = Lan.T_NID = Lan.T_INT = Lan.T_DES = Lan.T_DEATH = Lan.T_MARK = Lan.T_EV = None
    Lan.R_TIME = None
    Lan.clearAll()
    print("Q. the Lantern: model, torch, items, the real ECS world (equip / unequip / profile switch / logout / death / world change / restart / "
          "two players / foreign lights / unload / parked copies), config + the real kit, bytecode")


def run_tracker(P, Defs, Store, UUID, US, ll):
    """the fix round: Q21 - THE REACH LIGHT IS THE WEARER'S OWN, EXECUTED on the engine's own entity tracker: EntityStore.REGISTRY (the
    registry the tracker's system groups belong to) with the engine's NetworkSendableSpatialSystem, ClearEntityViewers, CollectVisible,
    ClearPreviouslyVisible, EnsureVisibleComponent, AddToVisible, RemoveEmptyVisibleComponent, DynamicLightTracker,
    DynamicLightSystems$EntityTrackerRemove, TransformSystems$EntityTrackerUpdate, SendPackets and DespawnSystem + the jar's AccLanternSys,
    AccLanternHelp, AccLanternHide; each player's EntityViewer writes to a recording IPacketReceiver, so the checks read what each client
    would get. The engine classes find their component types through EntityModule.get() / TimeModule.get(): two stand-ins
    (Unsafe.allocateInstance, the harness's types in their fields) are put in for this section and the old values put back after it."""
    from jpype import JClass, JArray, JImplements, JOverride
    import random
    Lan = JClass(P + ".AccLantern")
    for f_, v_ in (("LAN_HEIGHT", 128), ("LAN_EDGE", 255), ("LAN_LIGHTS", 1)):   # 0.5.5: the carried checks in the 0.5.4 light layout
        setattr(Defs, f_, v_)
    Defs.lanTable()
    Mark, MarkSup = JClass(P + ".AccLanternMark"), JClass(P + ".AccLanternMarkSup")
    LANS_ = ["Skyy_Talisman_Lantern_Common", "Skyy_Talisman_Lantern_Uncommon", "Skyy_Talisman_Lantern_Rare", "Skyy_Talisman_Lantern_Epic"]
    ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    ERS, AR = JClass("com.hypixel.hytale.component.EmptyResourceStorage"), JClass("com.hypixel.hytale.component.AddReason")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    DLC = JClass("com.hypixel.hytale.server.core.modules.entity.component.DynamicLight")
    NIDC = JClass("com.hypixel.hytale.server.core.modules.entity.tracker.NetworkId")
    INTC = JClass("com.hypixel.hytale.server.core.modules.entity.component.Intangible")
    DESC = JClass("com.hypixel.hytale.server.core.modules.entity.DespawnComponent")
    DTHC = JClass("com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent")
    PRF = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TRC = JClass("com.hypixel.hytale.server.core.modules.time.TimeResource")
    T_ = "com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems$"
    EVW, VSB = JClass(T_ + "EntityViewer"), JClass(T_ + "Visible")
    HRC = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    IAC = JClass("com.hypixel.hytale.server.core.modules.entity.component.Interactable")
    KDT = JClass("com.hypixel.hytale.component.spatial.KDTree")
    V3, Duration = JClass("org.joml.Vector3d"), JClass("java.time.Duration")
    EMc, TMc = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule"), JClass("com.hypixel.hytale.server.core.modules.time.TimeModule")
    ISY = JClass("com.hypixel.hytale.component.system.ISystem")

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def get(self):
            return self.f()

    @JImplements("java.util.function.Predicate")
    class Valid(object):
        @JOverride
        def test(self, r_):
            return bool(r_.isValid())

    @JImplements("com.hypixel.hytale.server.core.receiver.IPacketReceiver")
    class Rec(object):
        def __init__(self):
            self.p = []

        @JOverride
        def write(self, pk):
            self.p.append(pk)

        @JOverride
        def writeNoCache(self, pk):
            self.p.append(pk)

    @JImplements("java.util.function.BiConsumer")
    class Collect(object):
        def __init__(self):
            self.refs = []

        @JOverride
        def accept(self, chunk, cb):
            for i_ in range(int(chunk.size())):
                self.refs.append(chunk.getReferenceTo(i_))

    def fld(C_, name_):
        f_ = C_.class_.getDeclaredField(name_)
        f_.setAccessible(True)
        return f_

    REG = ES.REGISTRY
    T_TC = REG.registerComponent(TC, "Transform", TC.CODEC)
    T_DL = REG.registerComponent(DLC, Sup(lambda: DLC()))
    T_NID = REG.registerComponent(NIDC, Sup(lambda: NIDC(0)))
    T_INT = REG.registerComponent(INTC, "Intangible", INTC.CODEC)
    T_DES = REG.registerComponent(DESC, "Despawn", DESC.CODEC)
    T_DTH = REG.registerComponent(DTHC, Sup(lambda: None))
    T_PR = REG.registerComponent(PRF, Sup(lambda: None))
    T_EV = REG.registerComponent(EVW, Sup(lambda: None))
    T_VIS = REG.registerComponent(VSB, Sup(lambda: VSB()))
    T_HR = REG.registerComponent(HRC, Sup(lambda: None))
    T_IA = REG.registerComponent(IAC, Sup(lambda: None))
    T_MARK = REG.registerComponent(Mark, MarkSup())
    R_TIME = REG.registerResource(TRC, "Time", TRC.CODEC)
    R_SP = REG.registerSpatialResource(Sup(lambda: KDT(Valid())))
    em_f, tm_f = fld(EMc, "instance"), fld(TMc, "instance")
    em_old, tm_old = em_f.get(None), tm_f.get(None)
    em = US.allocateInstance(EMc.class_)
    for name_, v_ in (("transformComponentType", T_TC), ("networkIdComponentType", T_NID), ("dynamicLightComponentType", T_DL),
                      ("visibleComponentType", T_VIS), ("entityViewerComponentType", T_EV), ("headRotationComponentType", T_HR),
                      ("despawnComponentComponentType", T_DES), ("interactableComponentType", T_IA), ("intangibleComponentType", T_INT),
                      ("networkSendableSpatialResourceType", R_SP)):
        fld(EMc, name_).set(em, v_)
    tm = US.allocateInstance(TMc.class_)
    fld(TMc, "timeResourceType").set(tm, R_TIME)
    em_f.set(None, em)
    tm_f.set(None, tm)
    try:
        Lan.T_TC, Lan.T_DL, Lan.T_NID, Lan.T_INT, Lan.T_DES, Lan.T_DEATH, Lan.T_PR, Lan.T_EV = T_TC, T_DL, T_NID, T_INT, T_DES, T_DTH, T_PR, T_EV
        Lan.T_MARK, Lan.R_TIME = T_MARK, R_TIME
        Lan.clearAll()
        sysl = [JClass("com.hypixel.hytale.server.core.modules.entity.system.NetworkSendableSpatialSystem")(R_SP),
                JClass(T_ + "ClearEntityViewers")(T_EV), JClass(T_ + "CollectVisible")(T_EV), JClass(T_ + "ClearPreviouslyVisible")(T_VIS),
                JClass(T_ + "EnsureVisibleComponent")(T_EV, T_VIS), JClass(T_ + "AddToVisible")(T_EV, T_VIS),
                JClass(T_ + "RemoveEmptyVisibleComponent")(T_VIS),
                JClass("com.hypixel.hytale.server.core.modules.entity.system.EntitySystems$DynamicLightTracker")(T_VIS),
                JClass("com.hypixel.hytale.server.core.modules.entity.dynamiclight.DynamicLightSystems$EntityTrackerRemove")(T_VIS),
                JClass("com.hypixel.hytale.server.core.modules.entity.system.TransformSystems$EntityTrackerUpdate")(),
                JClass(T_ + "SendPackets")(T_EV), JClass("com.hypixel.hytale.server.core.modules.entity.DespawnSystem")(T_DES),
                JClass(P + ".AccLanternSys")(), JClass(P + ".AccLanternHelp")(), JClass(P + ".AccLanternHide")()]
        hide = sysl[-1]
        # the order: 20 shuffles through the engine's own ISystem.calculateOrder (its DependencyGraph)
        rnd = random.Random(541)
        ok_o = True
        for _t in range(20):
            lst = list(sysl)
            rnd.shuffle(lst)
            arr = JArray(ISY)(len(lst))
            for i_, s_ in enumerate(lst):
                arr[i_] = s_
            ISY.calculateOrder(REG, arr, len(lst))
            pos_ = dict((str(arr[i_].getClass().getSimpleName()), i_) for i_ in range(len(lst)))
            ok_o = ok_o and (pos_["ClearEntityViewers"] < pos_["CollectVisible"] < pos_["AccLanternHide"] < pos_["ClearPreviouslyVisible"] <
                             pos_["EnsureVisibleComponent"] < pos_["AddToVisible"] < pos_["RemoveEmptyVisibleComponent"] <
                             pos_["DynamicLightTracker"] < pos_["SendPackets"] and pos_["NetworkSendableSpatialSystem"] < pos_["CollectVisible"])
        check(ok_o and str(hide.getGroup()) == str(JClass(T_[:-1]).FIND_VISIBLE_ENTITIES_GROUP) and not bool(hide.isParallel(64, 64)) and
              hide.getQuery() == T_EV, "Q21 the jar's AccLanternHide: the find-visible group, sequential, every viewer; 20 shuffles through the "
              "engine's DependencyGraph: always after CollectVisible and before ClearPreviouslyVisible / EnsureVisibleComponent / AddToVisible "
              "(the visible set it edits is what the light, the moves and the entity go to)")
        for s_ in sysl:
            REG.registerSystem(s_)
        w1 = REG.addStore(ES(None), ERS.get())

        def player(u, name, x, y, z, radius):
            rec = Rec()
            h_ = REG.newHolder()
            tc = TC()
            tc.setPosition(V3(x, y, z))
            h_.addComponent(T_TC, tc)
            h_.addComponent(T_PR, PRF(None, u, name, "en-US", None, None))
            h_.addComponent(T_NID, NIDC(int(w1.getExternalData().takeNextNetworkId())))
            h_.addComponent(T_EV, EVW(radius, rec))
            return w1.addEntity(h_, AR.SPAWN), rec

        def tick(n=1):
            for _q in range(n):
                w1.tick(1.0 / 30.0)

        def helpers(owner):
            cl = Collect()
            w1.forEachChunk(T_MARK, cl)
            return [r_ for r_ in cl.refs if w1.getComponent(r_, T_MARK).owner is not None and w1.getComponent(r_, T_MARK).owner.equals(owner)]

        nid = lambda r_: int(w1.getComponent(r_, T_NID).getId())
        pos = lambda r_: (float(w1.getComponent(r_, T_TC).getPosition().x()), float(w1.getComponent(r_, T_TC).getPosition().y()),
                          float(w1.getComponent(r_, T_TC).getPosition().z()))
        gkey = lambda r_: None if w1.getComponent(r_, T_DL) is None else int(Defs.lanKeyOf(w1.getComponent(r_, T_DL).getColorLight()))
        cnt = lambda c_: int(getattr(Lan, c_).get())

        def got(rec, n_, since=0):
            """what this client got for network id n_: the component updates, the removed component types, how often the entity was removed"""
            ups, rcs, gone = [], [], 0
            for pk in rec.p[since:]:
                if pk.updates is not None:
                    for eu in pk.updates:
                        if int(eu.networkId) == n_:
                            if eu.updates is not None:
                                ups.extend(list(eu.updates))
                            if eu.removed is not None:
                                rcs.extend(str(x_) for x_ in eu.removed)
                if pk.removed is not None and n_ in [int(x_) for x_ in pk.removed]:
                    gone += 1
            return ups, rcs, gone
        names = lambda ups: [str(u_.getClass().getSimpleName()) for u_ in ups]
        lights = lambda ups: [int(Defs.lanKeyOf(u_.dynamicLight)) for u_ in ups if str(u_.getClass().getSimpleName()) == "DynamicLightUpdate"]
        HK208, K11 = int(Defs.lanHKey(208)), int(Defs.lanKey(11))
        a1, b1, c1 = UUID.randomUUID(), UUID.randomUUID(), UUID.randomUUID()
        ra, reca = player(a1, "Ava", 0.5, 64.0, 0.5, 640)
        rb, recb = player(b1, "Ben", 8.5, 64.0, 0.5, 640)
        tick(2)
        va, vb = w1.getComponent(ra, T_EV), w1.getComponent(rb, T_EV)
        check(bool(va.visible.contains(rb)) and bool(vb.visible.contains(ra)) and not helpers(a1) and got(recb, nid(ra))[0],
              "Q21 the real tracker runs: Ava and Ben see each other (CollectVisible -> AddToVisible -> SendPackets to each IPacketReceiver)")
        hid0 = cnt("HIDDEN")
        Store.equipK(a1, str(a1), LANS_[3])
        tick(3)
        hs_ = helpers(a1)
        h = hs_[0] if hs_ else None
        if h is None:
            check(False, "Q21 no helper spawned for Ava")
            return
        hn, an = nid(h), nid(ra)
        vis_h = w1.getComponent(h, T_VIS)
        check(len(hs_) == 1 and pos(h) == (0.5, 187.0, 0.5) and gkey(h) == HK208 and bool(va.visible.contains(h)) and
              not bool(vb.visible.contains(h)) and vis_h is not None and [k_ for k_ in vis_h.visibleTo.keySet()] == [ra] and cnt("HIDDEN") > hid0,
              "Q21 Ava wears Legendary: her helper (123 up, white 208) is in HER visible set only - AccLanternHide took it out of Ben's, so "
              "its Visible.visibleTo is Ava alone (taken out %d times)" % (cnt("HIDDEN") - hid0))
        ua_, ra_, ga_ = got(reca, hn)
        ub_, rb_, gb_ = got(recb, hn)
        check("DynamicLightUpdate" in names(ua_) and lights(ua_) == [HK208] and "TransformUpdate" in names(ua_) and not ub_ and not rb_ and gb_ == 0,
              "Q21 the packets: Ava's client got the helper (its transform + the white light %08x); Ben's client never got anything for it: "
              "%r / %r" % (HK208, names(ua_), names(ub_)))
        check(K11 in lights(got(recb, an)[0]) and K11 in lights(got(reca, an)[0]),
              "Q21 the glow on Ava (the torch light) reached BOTH clients - everyone sees her glow")
        # finding 3 on the wire: a 1-block step sends no helper move, a 3-block step one (the 123-up helper's threshold is 1.5 blocks)
        n0 = len(reca.p)
        w1.getComponent(ra, T_TC).setPosition(V3(1.5, 64.0, 0.5))
        tick(2)                                          # (AccLanternSys has no group: its move goes out with the next SendPackets)
        u1 = names(got(reca, hn, n0)[0])
        n1 = len(reca.p)
        w1.getComponent(ra, T_TC).setPosition(V3(3.5, 64.0, 0.5))
        tick(2)
        u2 = names(got(reca, hn, n1)[0])
        check("TransformUpdate" not in u1 and u2.count("TransformUpdate") == 1 and not got(recb, hn)[0],
              "Q21 Ava steps 1 block: no helper move on the wire; 3 blocks: one TransformUpdate, to Ava only: %r / %r" % (u1, u2))
        # lantern.shareReach: everyone gets it; a viewer who hid the wearer (the vanilla /hide) does not
        Defs.LAN_SHARE = True
        nb0 = len(recb.p)
        tick(2)
        ubs = got(recb, hn, nb0)[0]
        check(bool(vb.visible.contains(h)) and lights(ubs) == [HK208], "Q21 lantern.shareReach on: Ben's client gets the helper and its light too")
        hm = w1.getComponent(rb, T_PR).getHiddenPlayersManager()
        hidden_ = fld(JClass("com.hypixel.hytale.server.core.entity.entities.player.HiddenPlayersManager"), "hiddenPlayers").get(hm)
        hidden_.add(a1)                                  # = hidePlayer(a1) without its player-list packet (ServerPlayerListModule is not running here)
        nb1 = len(recb.p)
        tick()
        check(not bool(vb.visible.contains(h)) and got(recb, hn, nb1)[2] >= 1, "Q21 shared, but Ben hides Ava (HiddenPlayersManager, /hide): "
              "the helper is removed from Ben's client")
        check(bool(hm.isPlayerHidden(a1)), "Q21 (the harness hid Ava for Ben through the manager's own set)")
        hidden_.remove(a1)
        Defs.LAN_SHARE = False
        nb2 = len(recb.p)
        tick(2)
        check(not bool(vb.visible.contains(h)) and not got(recb, hn, nb2)[0], "Q21 lantern.shareReach off again: Ben never gets it back")
        # unequip: the glow's removal reaches Ben (DynamicLightSystems$EntityTrackerRemove), Ava's client drops the helper
        na3, nb3 = len(reca.p), len(recb.p)
        Store.unequipK(a1, str(a1), 0)
        tick(2)
        check("DynamicLight" in got(recb, an, nb3)[1] and "DynamicLight" in got(reca, an, na3)[1] and got(reca, hn, na3)[2] >= 1 and
              not helpers(a1) and not bool(h.isValid()), "Q21 Ava unequips: both clients are told her light is gone, her client drops the helper")
        # 0.5.5: THE RING on the real tracker - the default layout (height 64, edge 96, lights 7): Ava's Legendary = the light above + 5
        # around it; each reaches HER client only (AccLanternHide takes every marked entity of another wearer out), white 95
        for f_, v_ in (("LAN_HEIGHT", 64), ("LAN_EDGE", 96), ("LAN_LIGHTS", 7)):
            setattr(Defs, f_, v_)
        Defs.lanTable()
        Lan.SPAWNT.remove(a1)
        Lan.RSPAWNT.remove(a1)
        na4, nb4 = len(reca.p), len(recb.p)
        Store.equipK(a1, str(a1), LANS_[3])
        tick(3)
        hr_ = helpers(a1)
        sl_ = dict((int(w1.getComponent(r_, T_MARK).slot), r_) for r_ in hr_)
        K95 = int(Defs.lanHKey(95))
        nids_ = [nid(r_) for r_ in hr_]
        ax_, ay_, az_ = pos(ra)                           # where Ava stands now
        spot = lambda k_: (ax_, ay_ + 52.0, az_) if k_ == 0 else (ax_ + 27.5 * math.cos(2 * math.pi * (k_ - 1) / 5), ay_ + 52.0,
                                                                  az_ + 27.5 * math.sin(2 * math.pi * (k_ - 1) / 5))
        check(len(hr_) == 6 and sorted(sl_) == [0, 1, 2, 3, 4, 5] and all(gkey(r_) == K95 for r_ in hr_) and
              all(bool(va.visible.contains(r_)) and not bool(vb.visible.contains(r_)) for r_ in hr_) and
              all(lights(got(reca, n_, na4)[0]) == [K95] for n_ in nids_) and all(not got(recb, n_, nb4)[0] for n_ in nids_) and
              all(max(abs(a_ - b_) for a_, b_ in zip(pos(sl_[k_]), spot(k_))) < 1e-9 for k_ in sl_),
              "Q21 0.5.5 the ring on the real tracker: Ava's Legendary = 6 hidden lights (the one 52 up + 5 around at 27.5, slots 0-5), "
              "each in HER visible set only - her client got each one's white 95 light, Ben's client none of them %r" % ((
                  [(k_, pos(r_), gkey(r_), bool(va.visible.contains(r_)), bool(vb.visible.contains(r_))) for k_, r_ in sorted(sl_.items())],
                  [lights(got(reca, n_, na4)[0]) for n_ in nids_], [len(got(recb, n_, nb4)[0]) for n_ in nids_]),))
        na5 = len(reca.p)
        Store.unequipK(a1, str(a1), 0)
        tick(2)
        check(not helpers(a1) and all(got(reca, n_, na5)[2] >= 1 for n_ in nids_) and Lan.RING.get(a1) is None,
              "Q21 0.5.5 Ava unequips: all six leave her client at once, the ring state is gone")
        for f_, v_ in (("LAN_HEIGHT", 128), ("LAN_EDGE", 255), ("LAN_LIGHTS", 1)):   # back to the 0.5.4 layout for the rest of Q21
            setattr(Defs, f_, v_)
        Defs.lanTable()
        # the view radius (a nit): never farther up than the wearer's own view radius - 4 (CollectVisible only collects inside it)
        rc, recc = player(c1, "Cal", 600.5, 64.0, 600.5, 96)
        Store.equipK(c1, str(c1), LANS_[3])
        cl0 = cnt("CLAMPED")
        tick(3)
        hc = helpers(c1)
        lv92 = min(208, int(Defs.lanMaxLevel(92.0 - 3.0, float(Defs.lanCap(4)))))
        vc = w1.getComponent(rc, T_EV)
        hcn = nid(hc[0]) if hc else -1
        check(len(hc) == 1 and pos(hc[0]) == (600.5, 156.0, 600.5) and gkey(hc[0]) == int(Defs.lanHKey(lv92)) and bool(vc.visible.contains(hc[0]))
              and cnt("CLAMPED") > cl0 and lights(got(recc, hcn)[0]) == [int(Defs.lanHKey(lv92))] and ll(lv92, 89.0) <= ll(11, 0.3),
              "Q21 Cal plays with a 96-block view radius: his Legendary helper waits 92 up (not 123, which his client would never get) with its "
              "light lowered to %d (the cap holds), and his client gets it" % lv92)
        vc.viewRadiusBlocks = 640
        tick(2)
        check(pos(hc[0]) == (600.5, 187.0, 600.5) and gkey(hc[0]) == HK208, "Q21 Cal raises his view distance: 123 up, 208 at once")
        # the 5 s dead-man (review finding 6): the plugin stops - the jar's systems and the marker are unregistered - and the engine's own
        # DespawnSystem removes the helper 5 s after its last refresh; Cal's client drops it
        for cn_ in ("AccLanternSys", "AccLanternHelp", "AccLanternHide"):
            REG.unregisterSystem(JClass(P + "." + cn_).class_)
        REG.unregisterComponent(T_MARK)
        tr = w1.getResource(R_TIME)
        tr.add(Duration.ofSeconds(4))
        tick()
        alive4 = bool(hc[0].isValid())
        nc0 = len(recc.p)
        tr.add(Duration.ofSeconds(2))
        tick(2)
        check(alive4 and not bool(hc[0].isValid()) and got(recc, hcn, nc0)[2] >= 1, "Q21 the dead-man: with the jar's systems and the marker "
              "unregistered (a stopped plugin) the helper is still there 4 s later, gone at 6 s (the engine's DespawnSystem), and Cal's client "
              "drops it")
        print("Q21. the real entity tracker: the helper reached its wearer only (taken out of other viewers' sets %d times), lantern.shareReach "
              "and /hide, the glow and its removal reached everyone, the view-radius clamp, the dead-man through the engine's DespawnSystem"
              % (cnt("HIDDEN") - hid0))
    finally:
        em_f.set(None, em_old)
        tm_f.set(None, tm_old)
        Defs.LAN_SHARE = False


def Collect_all(w):
    """every entity Ref of a store (Store.forEachChunk with a Python BiConsumer)"""
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.BiConsumer")
    class All(object):
        def __init__(self):
            self.refs = []

        @JOverride
        def accept(self, chunk, cb):
            for i_ in range(int(chunk.size())):
                self.refs.append(chunk.getReferenceTo(i_))
    a = All()
    w.forEachChunk(a)
    return a.refs


def run_y054(jar):
    """0.5.4: Y - compare with the 0.5.3 jar (the SET pin): classes and assets."""
    import skyybuild as B
    import zipfile
    from jpype import JClass
    IP_, PS_, BOS_ = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")

    def csig(data):
        cp0 = JClass("javassist.ClassPool")(False)
        cp0.appendSystemPath()
        cp0.appendClassPath(B.SERVER_JAR)
        cc0 = cp0.makeClass(JClass("java.io.ByteArrayInputStream")(data))
        out = {}
        ms = [(str(mm.getName()) + str(mm.getSignature()), mm) for mm in cc0.getDeclaredMethods()]
        if cc0.getClassInitializer() is not None:
            ms.append(("<clinit>", cc0.getClassInitializer().toMethod("clinit_", cc0)))
        for nm, mm in ms:
            bos = BOS_()
            IP_(PS_(bos)).print_(mm)
            out["m " + nm] = re.sub(r"#\d+ = ", "", str(bos.toString()))
        for fd in cc0.getDeclaredFields():
            out["f " + str(fd.getName())] = str(fd.getSignature()) + " = " + str(fd.getConstantValue())
        return out

    def norm(code):
        lines = [re.sub(r"^\s*\d+:\s*", "", l.rstrip("\r")) for l in (code or "").split("\n") if l.strip()]
        lines = [re.sub(r"^ldc(_w)? ", "ldc ", l) for l in lines]
        return [re.sub(r"^((?:if\w*|goto\w*|jsr\w*)) -?\d+$", r"\1", l) for l in lines]

    za, zb = zipfile.ZipFile(JAR053), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    ca = dict((n, za.read(n)) for n in na if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in nb if n.endswith(".class"))
    same = sorted(n for n in ca if n in cb and ca[n] == cb[n])
    changed = sorted(n for n in ca if n in cb and ca[n] != cb[n])
    new_ = sorted(n for n in cb if n not in ca)
    gone = sorted(n for n in ca if n not in cb)
    short = lambda xs: ", ".join(x.split("/")[-1][:-6] for x in xs)
    check(short(gone) == "AccNightVision, AccNv" and short(new_) == "AccLantern, AccLanternHelp, AccLanternHide, AccLanternMark, AccLanternMarkSup, AccLanternSys",
          "Y gone = the Night Vision classes, new = the Lantern classes: %s / %s" % (short(gone), short(new_)))
    check(set(short(changed).split(", ")) <= {"AccAdmin", "AccCfg", "AccDefs", "AccStore", "AccTick", "CfgFile", "CfgFn", "CfgRows",
                                             "SkyyAccessoriesPlugin"}, "Y changed classes are the expected ones: " + short(changed))
    check(all(("com/skyy/accessories/%s.class" % c) in same for c in ("AccEffects", "AccGear", "MoveSync", "AccPage", "AccNotice", "AccGiveTask",
                                                                   "AccRestampTask", "WbTab", "WbRank", "WbAssetL", "CfgSaveTask", "CfgPub",
                                                                   "CfgHist", "CfgLog", "AccFn", "AccGiveFn")),
          "Y byte-identical: AccEffects, AccGear, MoveSync, the page, the notice, the give task / function, the restamp, the Workbench tab, the kit's "
          "save / publish / history / log")
    mdiff = {}
    for cn in changed:
        sn = cn.split("/")[-1][:-6]
        x1, x2 = csig(ca[cn]), csig(cb[cn])
        mdiff[sn] = sorted(("+" if k not in x1 else ("-" if k not in x2 else "~")) + k.split("(")[0] for k in set(x1) | set(x2)
                           if (norm(x1.get(k)) != norm(x2.get(k)) if k.startswith("m ") else x1.get(k) != x2.get(k)))
    d_ = mdiff.get("AccDefs", [])
    check(all(x in d_ for x in ("+m lanLight", "+m lanSolve", "+m lanTable", "+m lanKey", "+m lanHKey", "+f LAN_SHARE", "+m lanOurs", "+m isLantern", "+m lanBest", "+m lanRow",
                                "+f LINE_LANTERN", "+f LAN_IDS", "-f LINE_NIGHTVISION", "-m nvOnText", "~m isRetired", "~m pretty", "~m bonusRows",
                                "~m defsText", "~m linesText")) and "~m bestTiers" not in d_ and "~m tierOf" not in d_,
          "Y AccDefs: + the Lantern model / rules / texts, - the Night Vision light settings, ~ isRetired / pretty / rows / defs / lines; tierOf / bestTiers unchanged")
    check(all(x in mdiff.get("AccStore", []) for x in ("+f LPOKE", "-f NVPOKE", "~m publish")) and
          all(x in mdiff.get("AccCfg", []) for x in ("+f LAN_KEYS", "-f NV_KEYS", "~m load")) and mdiff.get("AccTick", []) == ["~m run"],
          "Y AccStore: the poke renamed, acc:tal leaves a retired one out; AccCfg: the Lantern keys; AccTick: prunes the Lantern")
    print("Y. members that differ: " + "; ".join("%s: %s" % (k2, ", ".join(v)) for k2, v in sorted(mdiff.items())))
    assets_a = dict((n, za.read(n)) for n in na if not n.endswith(".class"))
    assets_b = dict((n, zb.read(n)) for n in nb if not n.endswith(".class"))
    LJ = ["Server/Item/Items/Utility/%s.json" % i for i in LANS]
    check(sorted(assets_b) == sorted(list(assets_a) + LJ), "Y the 0.5.3 asset files + the 4 Lantern item JSONs")
    diff = sorted(n for n in assets_a if assets_a[n] != assets_b.get(n))
    NVJ = "Server/Item/Items/Utility/%s.json" % NVID
    check(diff == sorted([NVJ, "Server/Languages/en-US/server.lang", "manifest.json"]), "Y besides them only the Night Vision JSON, server.lang and the "
          "manifest differ: %r" % diff)
    j3, j4 = json.loads(assets_a[NVJ]), json.loads(assets_b[NVJ])
    j3x = dict(j3)
    del j3x["Categories"]
    j3x["Variant"] = True
    check(j4 == j3x, "Y the Night Vision JSON: exactly Categories -> Variant (out of the creative library)")
    la = assets_a["Server/Languages/en-US/server.lang"].decode("utf8").split("\n")
    lb = assets_b["Server/Languages/en-US/server.lang"].decode("utf8").split("\n")
    nvk = ["items.%s.name" % NVID, "server.items.%s.name" % NVID, "items.%s.description" % NVID, "server.items.%s.description" % NVID]
    chg = [i for i in range(len(la) - 1) if la[i] != lb[i]]
    check(len(lb) == len(la) + 16 and lb[-1] == "" and [la[i].split("=", 1)[0] for i in chg] == nvk and
          [lb[i].split("=", 1)[0] for i in chg] == nvk and [l.split("=", 1)[0].split(".")[-1] for l in lb[len(la) - 1:-1]] == ["name", "name", "description",
                                                                                                                       "description"] * 4,
          "Y server.lang: the 4 Night Vision lines changed in place, 16 Lantern lines at the end, nothing else")
    ma, mb = json.loads(assets_a["manifest.json"]), json.loads(assets_b["manifest.json"])
    check(sorted(k2 for k2 in set(ma) | set(mb) if ma.get(k2) != mb.get(k2)) == ["Description", "Name", "Version"] and mb["Version"] == "0.5.4" and
          mb["Name"] == "0.5.4 SkyyAccessories" and "Night Vision" not in mb["Description"] and "Lantern" in mb["Description"] and
          mb["Description"].replace(" the Lantern line (Normal to Legendary, each crafted from the rarity below) makes its wearer glow like a torch for "
                                    "everyone and lights farther with each rarity through a hidden light above them;",
                                    " the admin-given Night Vision accessory (its own line) gives its wearer alone a light that brightens caves and the night;")
          == ma["Description"], "Y the manifest: Name / Version + the Night Vision sentence replaced by the Lantern sentence")
    print("Y. compare with 0.5.3: classes identical %d, changed %d (%s), new %d, gone %d; assets: + 4 Lantern JSONs, Night Vision JSON, server.lang, "
          "manifest" % (len(same), len(changed), short(changed), len(new_), len(gone)))


def run_m55(P, Defs, Cfg, jpath):
    """0.5.5: U - THE ONE-TIME lantern.height UPDATE (AccCfg.m55Update / migrate055, setup()'s order: migrate051, migrate055, load(true))."""
    import skyybuild as B
    from jpype import JClass, JArray, JString
    MARK, MARK_ID = str(Cfg.M55_MARK), str(Cfg.M55_MARK_ID)
    check(str(Cfg.M55_KEY) == "lantern.height" and str(Cfg.M55_OLD) == "128" and str(Cfg.M55_NEW) == "64" and
          str(Cfg.M55_WHO) == "SkyyAccessories 0.5.5" and MARK.startswith("# " + MARK_ID) and "=" not in MARK and
          MARK in str(Cfg.DEFAULT_TEXT).split("\n") and "lantern.height=64" in str(Cfg.DEFAULT_TEXT).split("\n"),
          "U the update's data; the 0.5.5 default text carries lantern.height=64 and the marker")

    def upd(t):
        r = Cfg.m55Update(JString(t))
        if r is None:
            return None
        return str(r[0]), str(r[1]), [str(x) for x in r[2]], [str(x) for x in r[3]]
    u54 = JArray(JClass("java.net.URL"))(2)
    u54[0] = JClass("java.io.File")(JAR054).toURI().toURL()
    u54[1] = JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()
    t054 = str(JClass(P + ".AccCfg", loader=JClass("java.net.URLClassLoader")(u54, JClass("java.lang.ClassLoader").getPlatformClassLoader())).DEFAULT_TEXT)
    u53 = JArray(JClass("java.net.URL"))(2)
    u53[0] = JClass("java.io.File")(JAR053).toURI().toURL()
    u53[1] = u54[1]
    t053 = str(JClass(P + ".AccCfg", loader=JClass("java.net.URLClassLoader")(u53, JClass("java.lang.ClassLoader").getPlatformClassLoader())).DEFAULT_TEXT)
    lines = t054.split("\n")
    check("lantern.height=128" in lines and lines.count("lantern.height=128") == 1 and MARK_ID not in t054,
          "U the 0.5.4 default file (what a fresh 0.5.4 install wrote) holds lantern.height=128 and no marker")
    i_ = lines.index("lantern.height=128")
    exp = list(lines)
    exp[i_] = "lantern.height=64"
    exp.insert(i_, MARK)
    exp = "\n".join(exp)
    r = upd(t054)
    check(r is not None and r[0] == exp and r[1] == "lantern.height 128 -> 64" and r[2] == [] and r[3] == ["lantern.height", "128", "64"],
          "U1 the 0.5.4 default file: lantern.height 128 -> 64, the marker right above it, every other line byte for byte")
    check(upd(r[0]) is None and upd(str(Cfg.DEFAULT_TEXT)) is None, "U1 a file with the marker (an updated one, a fresh 0.5.5 one) is never updated")
    rc = upd(t054.replace("\n", "\r\n"))
    check(rc is not None and rc[0] == exp.replace("\n", "\r\n"), "U2 a CRLF file stays CRLF (the marker line too)")
    t_c = t054.replace("lantern.height=128", "lantern.height = 100")
    r_c = upd(t_c)
    check(r_c[0] == t_c.replace("lantern.height = 100", MARK + "\nlantern.height = 100") and r_c[1] == "" and r_c[3] == [] and
          r_c[2] == ["lantern.height=100 kept (custom) - the 0.5.5 default is 64"], "U3 a custom value is kept and noted (the marker added)")
    t_6 = t054.replace("lantern.height=128", "lantern.height=64")
    r_6 = upd(t_6)
    check(r_6[0] == t_6.replace("lantern.height=64", MARK + "\nlantern.height=64") and r_6[1] == "" and r_6[2] == [] and r_6[3] == [],
          "U3 already 64: only the marker, no note")
    t_s = t054.replace("lantern.height=128", "  lantern.height :  128  ")
    r_s = upd(t_s)
    check(r_s[0] == t_s.replace("  lantern.height :  128  ", MARK + "\n  lantern.height :  64") and r_s[1] == "lantern.height 128 -> 64",
          "U3 spaced: the key, the separator and the spaces before the value stay")
    t_m = t054.replace("lantern.height=128", "lantern.height=12\\\n8")
    r_m = upd(t_m)
    check(r_m[0] == t_m.replace("lantern.height=12\\\n8", MARK + "\nlantern.height=12\\\n8") and r_m[3] == [] and len(r_m[2]) == 1,
          "U3 a continued entry is kept (noted)")
    r_d = upd(t054 + "lantern.height=128\n")
    check(r_d[0] == exp + "lantern.height=64\n" and r_d[3] == ["lantern.height", "128", "64"], "U3 a duplicated 128 line: both become 64")
    r_d2 = upd(t054 + "lantern.height=90\n")
    check(r_d2[0] == t054.replace("lantern.height=128", MARK + "\nlantern.height=128") + "lantern.height=90\n" and r_d2[3] == [] and
          r_d2[2] == ["lantern.height=90 kept (custom) - the 0.5.5 default is 64"], "U3 the LAST entry decides (Properties keeps it): 90 -> nothing changes")
    r_t = upd(t054.replace("lantern.height=128", "#lantern.height=128\nlantern.height=128"))
    check(r_t[0] == exp.replace(MARK + "\nlantern.height=64", "#lantern.height=128\n" + MARK + "\nlantern.height=64"),
          "U3 a commented '#lantern.height=128' line is left alone")
    r_n = upd(t053)
    check(r_n[0] == t053 + MARK + "\n" and r_n[1] == "" and r_n[2] == [] and r_n[3] == [] and t053.endswith("\n"),
          "U4 a file with no lantern line (0.5.3's): only the marker, at the end - a later in-game 128 is never turned back")
    check(upd("slots=18")[0] == "slots=18\n" + MARK and upd("slots=18\r\n")[0] == "slots=18\r\n" + MARK + "\r\n" and upd("")[0] == MARK + "\n",
          "U4 no trailing newline / CRLF / empty: the file's own line ending")
    Pub, Fn = JClass(P + ".CfgPub"), JClass(P + ".CfgFn")

    def jobj(*xs):
        a = JArray(JClass("java.lang.Object"))(len(xs))
        for i, v in enumerate(xs):
            a[i] = JString(v) if isinstance(v, str) else v
        return a

    def histfiles(d_):
        hd = os.path.join(d_, "config-history")
        return sorted(f_ for f_ in os.listdir(hd) if f_ != "index.log") if os.path.isdir(hd) else []
    mods = os.path.join(SCRATCH, "m55-kit")
    d = os.path.join(mods, "Skyy_SkyyAccessories")
    os.makedirs(d)
    f = os.path.join(d, "config.properties")
    open(f, "wb").write(t054.encode("latin-1"))
    Cfg.FILE = jpath(f)
    res = str(Cfg.migrate055())
    new = open(f, "rb").read()
    hf = histfiles(d)
    log = open(os.path.join(d, "config-changes.log"), encoding="utf8").read().split("\n") if os.path.exists(os.path.join(d, "config-changes.log")) else []
    lg = [l_ for l_ in log if l_]
    check(new == exp.encode("latin-1") and "lantern.height 128 -> 64" in res and len(hf) == 1 and
          open(os.path.join(d, "config-history", hf[0]), "rb").read() == t054.encode("latin-1") if hf else False,
          "U5 migrate055 on a 0.5.4 file: written as m55Update says, the History copy = the old file byte for byte: " + res[:120])
    check(len(lg) == 1 and lg[0].split("\t")[1:] == ["SkyyAccessories 0.5.5", "-", "update", "lantern.height", "128", "64", "ok"],
          "U5 one config-changes.log line in the kit's format (status ok: Server Setup -> Changes offers Undo): %r" % lg)
    cs = str(Cfg.load(True))
    check(int(Defs.LAN_HEIGHT) == 64 and open(f, "rb").read() == new, "U5 the loader then runs at height 64 and leaves the file alone")
    check(str(Cfg.migrate055()) == "" and open(f, "rb").read() == new and len(histfiles(d)) == 1, "U5 the next start changes nothing")
    Pub.start(jpath(mods), None)
    rU = [str(x) for x in Fn().apply(jobj("set", "lantern.height", "128", None, "console", "yes", "console"))]
    Pub.flush()
    Pub.shutdown()
    after = open(f, "rb").read().decode("latin-1")
    check(rU[0] == "ok" and parse_props(after).get("lantern.height") == "128" and int(Defs.LAN_HEIGHT) == 128 and str(Cfg.migrate055()) == "" and
          open(f, "rb").read().decode("latin-1") == after, "U5 Undo through the real kit (set back to 128): it stays 128 at the next start (the marker)")
    # the live data (a scratch copy) and a fresh install
    lf = os.path.join(LIVE, "config.properties")
    if os.path.exists(lf):
        dl = os.path.join(SCRATCH, "m55-live", "Skyy_SkyyAccessories")
        shutil.copytree(LIVE, dl)
        fl = os.path.join(dl, "config.properties")
        old = open(fl, "rb").read()
        logn = len(open(os.path.join(dl, "config-changes.log"), "rb").read().split(b"\n")) if os.path.exists(os.path.join(dl, "config-changes.log")) else 0
        h0 = histfiles(dl)
        Cfg.FILE = jpath(fl)
        resl = str(Cfg.migrate055())
        newl = open(fl, "rb").read()
        exl = upd(old.decode("latin-1"))
        h1 = histfiles(dl)
        logn2 = len(open(os.path.join(dl, "config-changes.log"), "rb").read().split(b"\n")) if os.path.exists(os.path.join(dl, "config-changes.log")) else 0
        check((exl is None and newl == old and resl == "") or (exl is not None and newl == exl[0].encode("latin-1") and len(h1) == len(h0) + 1 and
              any(open(os.path.join(dl, "config-history", x), "rb").read() == old for x in h1) and logn2 == logn + (1 if exl[3] else 0)),
              "U6 Skyy's live file (a scratch copy): %s" % (resl[:140] or "already updated"))
        check(str(Cfg.migrate055()) == "" and open(fl, "rb").read() == newl, "U6 the live copy's next start changes nothing")
        print("U6. the live copy: %s" % (resl or "nothing to do"))
    else:
        print("note: no live config.properties - U6 skipped")
    df = os.path.join(SCRATCH, "m55-fresh")
    os.makedirs(df)
    ff = os.path.join(df, "config.properties")
    Cfg.FILE = jpath(ff)
    r0 = str(Cfg.migrate055())
    Cfg.load(True)
    ft = open(ff, "rb").read()
    check(r0 == "" and MARK.encode("latin-1") in ft and b"lantern.height=64" in ft and str(Cfg.migrate055()) == "" and open(ff, "rb").read() == ft and
          not histfiles(df), "U7 a fresh install: no file -> nothing; the default file carries height 64 + the marker -> never updated")
    print("U. the lantern.height update: 0.5.4 file 128 -> 64, CRLF, custom / spaced / continued / duplicated / commented, no line, the kit "
          "(History, log, loader, Undo), the live copy, a fresh install")


def run_y055(jar):
    """0.5.5: Y - compare with the 0.5.4 jar (the SET pin): classes and assets."""
    import zipfile
    za, zb = zipfile.ZipFile(JAR054), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    ca = dict((n, za.read(n)) for n in na if n.endswith(".class"))
    cb = dict((n, zb.read(n)) for n in nb if n.endswith(".class"))
    same = sorted(n for n in ca if n in cb and ca[n] == cb[n])
    changed = sorted(n for n in ca if n in cb and ca[n] != cb[n])
    new_ = sorted(n for n in cb if n not in ca)
    gone = sorted(n for n in ca if n not in cb)
    short = lambda xs: ", ".join(x.split("/")[-1][:-6] for x in xs)
    check(not new_ and not gone, "Y no class new or gone: %s / %s" % (short(new_), short(gone)))
    check(set(short(changed).split(", ")) <= {"AccCfg", "AccDefs", "AccLantern", "AccLanternMark", "AccLanternHelp", "SkyyAccessoriesPlugin",
                                             "CfgFile", "CfgFn", "CfgRows", "CfgPub"} and
          {"AccCfg", "AccDefs", "AccLantern", "AccLanternMark", "AccLanternHelp", "SkyyAccessoriesPlugin"} <= set(short(changed).split(", ")),
          "Y changed classes: the Lantern ones, the config and the plugin (+ the kit's version texts): " + short(changed))
    check(all(("com/skyy/accessories/%s.class" % c) in same for c in ("AccEffects", "AccGear", "MoveSync", "AccPage", "AccNotice", "AccStore",
                                                                   "AccTick", "AccLanternSys", "AccLanternHide", "AccLanternMarkSup", "WbTab",
                                                                   "WbRank", "AccFn", "AccGiveFn", "AccRestampTask", "CfgHist", "CfgLog")),
          "Y byte-identical: AccEffects, AccGear, MoveSync, the page, the notice, AccStore, AccTick, AccLanternSys, AccLanternHide, the "
          "Workbench tab, the give / restamp paths, the kit's History and log")
    assets_a = dict((n, za.read(n)) for n in na if not n.endswith(".class"))
    assets_b = dict((n, zb.read(n)) for n in nb if not n.endswith(".class"))
    diff = sorted(n for n in set(assets_a) | set(assets_b) if assets_a.get(n) != assets_b.get(n))
    ma, mb = json.loads(assets_a["manifest.json"]), json.loads(assets_b["manifest.json"])
    check(diff == ["manifest.json"] and sorted(k2 for k2 in set(ma) | set(mb) if ma.get(k2) != mb.get(k2)) == ["Name", "Version"] and
          mb["Version"] == "0.5.5", "Y every asset identical (items, recipes, server.lang, icons) but the manifest's Name / Version: %r" % diff)
    print("Y. compare with 0.5.4: classes identical %d, changed %d (%s); assets: only the manifest version" % (len(same), len(changed), short(changed)))



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
    for p in (JAR053, JAR054, SACKS_JAR):
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
    if OLDJARS:
        args += ["--oldjars", OLDJARS]
    r = subprocess.run(args, env=env)
    if not KEEP:
        shutil.rmtree(SCRATCH, ignore_errors=True)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
