"""Harness for SkyyPets 0.3.0 (THE PET SYSTEM: starter choice, rarity = a small multiplier, fusing 4 -> 1, pet levels to 50 + pet rebirth,
the two one-time updates; tools/pets_0_3_0_patch.py).
Build first: python tools/pets_0_3_0_patch.py; python SkyyPets/build_skyypets_0.3.0.py

    python SkyyPets/test_skyypets_0.3.0.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--no-old]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.2.7 -> 0.3.0 (exactly the planned members;
              + PetStarterJob, PetsCfgMig), engine-access audit
  SYS         EXECUTED in the hub stage (tools/hub_tab_kit.py: the REAL PageManager, Universe, component stores, -Xverify:all):
              CFG    the new Server Setup rows (categories, defaults, the starter check hook), PetMath.cap / implied / maxCap
              STA    THE STARTER CHOICE: first sight = starter=choose (saved, one chat line, no pet); offer() timing (delay, once, only with
                     no page open: PetStarterJob opens /pets once, starter.shown); the starter view (page_check, 4 rows, Later); Choose
                     twice (the first press only asks; another row moves the question); the pick = one Common Lv 1 pet in the pet slot,
                     one save; a second pick / a forged click = "already"; busy / pets off / a switched-off kind refused; Later; an
                     existing profile (starter=<ms>) gets nothing; choice off = the 0.2.7 Rabbit
              BUF    rarity x1 ... x1.5, the Common Lv 20 Rabbit = 2 Farming Fortune (0.2.7: 0.6), + 5 % per pet rebirth
              XP     need(2) = 120 (x2), the cap 50 stops XP (xp 0), pet rebirth XP +10 % each, the max-level chat line
              REB    the gates (below the cap, all rebirths, combat, busy, pets off), ask -> rebirth (Lv 1, cap 60, ledger col 11), a
                     doubled / stale press refused, keep mode, R5 = Lv 100 max, a failed save puts everything back
              FUS    4 Rabbits -> 1 (the weakest 3 unslotted are used, the opened slotted base keeps id + slot), best-of-4 level +
                     rebirths, refusals (too few, slotted fodder, top rarity, off, kind off, stale rarity), the page: ask / fuse / a third
                     press only asks again; a failed save = nothing changed (+ fuse-abort); a 300-step NO-DUPE fuzz (every op re-read from
                     disk: ids, rarities, the index, no id twice); fuse recovery after a cut-off (abort / done / mixed, second start quiet);
                     /petadmin restore refuses a fused-away pet unless force
              FIX    the critic fixes, each executed: Fuse / Rebirth wait for the level update (a Lv 75 pet is never reset); the
                     update waits on an unreadable config; the Undo line names only the added lines; fuse / rebirth / the update hold
                     the record monitor (a thread holding it blocks them); the starter job skips a player in another world and gives up
                     after 5 failed opens; the scaled Fortune caps (Legendary R5 Lv 100 = 17.5, off = 10); the Fuse question names R
              FIX2   the second critics' fixes: the level update is state-based (a marked record with pets levelled past their max
                     after a rollback is updated again, Undo names lines to delete + lines to change back; no free rebirth when no
                     count holds the level); the Fuse question pins its fodder (a new weaker pet between the presses = asked again;
                     a stale key at the engine = nothing fused); every new status line / detail value fits (worst-case names, R5,
                     10-pet fuse); the empty list after Later points back to the choice
              MIG    the one-time level update (implied rebirths, level + XP kept, History copy byte-equal, marker, ledger, change-log
                     Undo line, chat; nothing to do = marker only; a failed History copy = nothing changes) + a 400-pet FUZZ
              CMIG   the one-time config update on real + synthetic files (only old-default lines, number-equal; hand edits kept + noted;
                     CRLF / spaces kept; continuation lines kept; no file; config-history copy byte-equal; config-changes.log lines;
                     marker; a second run changes nothing; a blocked config-history = nothing rewritten, no marker)
              ADM    /petadmin give Lv 75 = 3 pet rebirths, Lv 101 refused, list line, take + restore keep the rebirths (11th column),
                     an old 10-column line = the implied count
              PAGE   the detail view (13 rows, Fuse / Rebirth bound only when possible) + the starter view through page_check
  HUB         the 0.2.7 hub phase (Pets tab registry, visible, open, page in the hub shell, bar clicks) on the 0.3.0 jar (detail row 12 = the id)
  SND         the 0.2.6 sound phase on the 0.3.0 jar
  LIVE        START TWICE on a scratch COPY of the live Skyy_SkyyPets folder: start 1 = the config update (only old-default lines, History
              copy, marker) + every record's level update (marker only unless a pet is above Lv 50); start 2 + a second tick write NOTHING
  OLD         the WHOLE 0.2.5 harness (test_skyypets_0.2.5.py) on the 0.3.0 jar with --old 0.2.7 in COMPAT mode: every fresh config it seeds
              holds the 0.2.x NUMBERS (rarity 0.3 ... 1.25, curve 60 / 0.04, max level 100, no pet rebirths, the fixed Rabbit starter) -
              so its ~4,000 checks prove the 0.2.7 machinery is unchanged under those numbers. Checks that pin the 0.2.5 identity / the
              0.2.7 layout are expected to differ (EXPECTED_OLD, each with its reason); any other failure fails.
Exit code 1 on any failure.
"""
import os, sys, subprocess, importlib.util, random, shutil, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

VERSION = "0.3.0"
PKG = "com.skyy.pets."


# ======================================================================================================== COMPAT child (the OLD run)
def compat_child():
    """python test_skyypets_0.3.0.py --compat-child <script> <args...>: run <script> as __main__ with (1) every child it starts wrapped the
    same way and (2) PetsCfg.load seeding a missing config.properties with the 0.2.x numbers (+ the 0.3.0 update marker)"""
    i = sys.argv.index("--compat-child")
    script = os.path.abspath(sys.argv[i + 1])
    rest = sys.argv[i + 2:]
    me = os.path.abspath(__file__)
    _run = subprocess.run

    def run(cmd, *a, **k):
        if isinstance(cmd, (list, tuple)) and len(cmd) >= 2 and os.path.basename(str(cmd[1])).startswith("test_skyypets_0.2.5"):
            cmd = [cmd[0], me, "--compat-child", str(cmd[1])] + list(cmd[2:])
        return _run(cmd, *a, **k)
    subprocess.run = run
    import jpype
    _jc = jpype.JClass

    class CfgProxy(object):
        def __init__(self, real):
            object.__setattr__(self, "_real", real)

        def __getattr__(self, n):
            return getattr(object.__getattribute__(self, "_real"), n)

        def __setattr__(self, n, v):
            setattr(object.__getattribute__(self, "_real"), n, v)

        def load(self, path):
            real = object.__getattribute__(self, "_real")
            home = os.path.join(str(path.toString()), "Skyy_SkyyPets")
            cf = os.path.join(home, "config.properties")
            if not os.path.exists(cf):
                os.makedirs(os.path.join(home, "migrations"), exist_ok=True)
                open(cf, "w", encoding="latin-1", newline="").write(compat_text(str(real.DEFAULT_TEXT)))
                open(os.path.join(home, "migrations", "pets-030.done"), "w").write("compat\n")
            return real.load(path)

    def JClass(name, *a, **k):
        c = _jc(name, *a, **k)
        return CfgProxy(c) if str(name) == PKG + "PetsCfg" else c
    jpype.JClass = JClass
    # fixer 2: since 2026-10-15 the WORLD line of tools/deploy_set.py carries a comment, which the 0.2.5 harness's parse keeps (-> no
    # live world, every live phase empty); the compat run reads that one line without its comment (read-only, this process + its children)
    import builtins, io
    _open = builtins.open
    ds = os.path.normcase(os.path.abspath(os.path.join(TOOLS, "deploy_set.py")))

    def open_(f, *a, **k):
        mode = a[0] if a else k.get("mode", "r")
        if isinstance(f, str) and "b" not in mode and "w" not in mode and "a" not in mode and os.path.normcase(os.path.abspath(f)) == ds:
            with _open(f, *a, **k) as h:
                txt = h.read()
            return io.StringIO(chr(10).join((l.split("#")[0].rstrip() if l.startswith("WORLD = ") else l) for l in txt.split(chr(10))))
        return _open(f, *a, **k)
    builtins.open = open_
    sys.argv = [script] + rest
    import runpy
    runpy.run_path(script, run_name="__main__")


COMPAT = [("pets.rarity.common", "1", "0.3"), ("pets.rarity.uncommon", "1.1", "0.45"), ("pets.rarity.rare", "1.2", "0.6"),
          ("pets.rarity.epic", "1.3", "0.8"), ("pets.rarity.legendary", "1.4", "1"), ("pets.rarity.mythic", "1.5", "1.25"),
          ("pets.curve.linear", "120", "60"), ("pets.curve.cubic", "0.08", "0.04"), ("pets.level.cap", "50", "100"),
          ("pets.rebirth.max", "5", "0"), ("pets.starter.choose", "true", "false"), ("pets.cap.scale", "true", "false")]


def compat_text(txt):
    for k, new, old in COMPAT:
        a = "\n%s=%s\n" % (k, new)
        assert txt.count(a) == 1, k
        txt = txt.replace(a, "\n%s=%s\n" % (k, old))
    return txt


if "--compat-child" in sys.argv:
    compat_child()
    sys.exit(0)

import perfworld_kit as PW
import hub_tab_kit as HT

JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.2.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "pets03b", "test")))


def deploy_world():
    try:
        for l in open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8"):
            if l.startswith("WORLD = "):
                v = l.split("=", 1)[1].strip()
                return v[1:v.index('"', 1)] if v.startswith('"') else v.split("#")[0].strip()     # fixer 2: the line may carry a comment
    except Exception:
        pass
    return "HUD mod"


LIVE = os.path.join(B.USERDATA, "Saves", deploy_world(), "mods", "Skyy_SkyyPets")
# class compare 0.2.7 -> 0.3.0: exactly these members differ (+ added classes)
EXPECT = {
    "PetsCfg": ["~<clinit>", "~m applyAll", "~m seed", "~m applyScalars", "+m checkStarterKind", "+m fuseMax",
                "+f STARTER_CHOOSE", "+f STARTER_MINING", "+f STARTER_FARMING", "+f STARTER_FORAGING", "+f STARTER_COMBAT", "+f STARTER_DELAY",
                "+f LVL_CAP", "+f REB_LEVELS", "+f REB_MAX", "+f REB_RESET", "+f REB_STAT", "+f REB_XP", "+f FUSE_ON", "+f FUSE_COUNT",
                "+f FUSE_MAX_S", "+f COMBAT_S", "+f CAP_SCALE"],
    "PetMath": ["+m cap", "+m maxCap", "+m implied"],
    "PetRec": ["+m rebirthOf", "+m capOf", "~m addXp", "+m fuseApply", "+m fuseUndo", "+m rebirth", "+m unrebirth"],
    "PetStore": ["+m ledgerR", "+m rebOf", "~m ledger", "+m lnum", "+m fuseRecover"],
    "PetBuff": ["~m addPet", "~m compute", "+m petMult", "+m capMult"],
    "PetXp": ["~m give"],
    "PetOps": ["+m createR", "~m create", "~m starter", "~m admin", "~m line", "+f START_TYPES", "+f OFFER", "+f STARTS", "+f FUSES",
               "+f REBIRTHS", "+f LVLMIG", "+f MIG3", "~<clinit>", "+m starterKind", "+m starterPending", "+m perkWords", "+m pickAsk",
               "+m chooseLocked", "+m chooseStarter", "+m offer", "+m gate", "+m agoMs", "+m combatMs", "+m score", "+m sameOthers",
               "+m fodder", "+m kindName", "+m fuseWhy", "+m fuseReady", "+m fuseInfo", "+m levels", "+m fuseAsk", "+m fuseLocked", "+m fuse",
               "+m rebWhy", "+m rebReady", "+m rebInfo", "+m rebAsk", "+m rebirthLocked", "+m rebirth", "+m changeLog", "+m migrateLocked",
               "+m migrateLevels", "+f FAILS", "+m starterOpenFailed", "+m migWait", "+m fuseSync", "+m rebSync", "+m migSync",
               "+m needsLevelFix", "+m fdKey", "+m fodderKey", "+m lvList"],     # fixer 2
    "PetViews": ["~m want"],
    "PetsPage": ["~m build", "~m handleDataEvent", "~m xpText", "~c ", "+f confirm", "+f later"],
    "PetTick": ["~m second", "~m leave"],
    "PetTickSys": ["~m tick"],
    "PetAdminArg4Cmd": ["~c "],     # the usage text (restore ... force) / the arg help
    "PetAdminArg5Cmd": ["~c "],
    "SkyyPetsPlugin": ["~m setup"],
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFile": ["~<clinit>"],      # the kit's template constants (the config.properties default text)
}
ADDED = ["PetStarterJob", "PetsCfgMig"]
_eq0 = HK.Child.eq
_s7 = importlib.util.spec_from_file_location("test_skyypets_0_2_7", os.path.join(HERE, "test_skyypets_0.2.7.py"))
T27 = importlib.util.module_from_spec(_s7)
_s7.loader.exec_module(T27)
HK.Child.eq = _eq0     # the 0.2.7 harness allows the 59 kit files as CHANGED (0.2.6 -> 0.2.7); 0.2.7 -> 0.3.0 ships them unchanged
T27.PKG = PKG
FAIL_TEXT = T27.FAIL_TEXT

# the 0.2.5 harness's checks (COMPAT run) that pin the 0.2.5 identity / the 0.2.7 layout - expected on 0.3.0, each with why
EXPECTED_OLD = [(p, "0.2.7: " + w) for p, w in T27.EXPECTED_OLD if not p.startswith("J/C: exactly") and not p.startswith("compare: C 0.2.5: the classes")
                and not p.startswith("rollback 0.2.4")] + [
    ("J/C: exactly the 47 expected classes: extra ['com.skyy.pets.HubBar', 'com.skyy.pets.PetSnd', 'com.skyy.pets.PetStarterJob', 'com.skyy.pets.PetsCfgMig', 'com.skyy.pets.PetsHubOpen']",
     "+ PetSnd (0.2.6) + HubBar + PetsHubOpen (0.2.7) + PetStarterJob + PetsCfgMig (0.3.0; ours: phase C)"),
    ("compare: C 0.2.5: the classes of 0.2.4 + PetOwnerFn only: +['PetStarterJob', 'PetsCfgMig']", "its compare is 0.2.4 -> 0.2.5 (ours: phase C)"),
    ("rollback 0.2.4: R 0.2.5: rollback - the 0.2.4 jar reads the live copy after 0.2.5", "the old jar is 0.2.7 here (its text says 0.2.7)"),
    ("core: X: details with slot 2 filled: slot 2 Open + 4 buttons + close", "0.3.0: the detail view has 6 buttons now (Fuse / Rebirth bound only when possible)"),
    ("core: X 0.2.2: details of a Mouse (pet only): the Summon slot button is NOT bound (+ slot 1 Open + close): 8",
     "0.3.0: that profile holds 8 Common Mice, so the new Fuse button is bound too (+1; ours: FUS / PAGE)"),
    ("rollback 0.2.2: the child wrote no result", "SkyyPets-0.2.2.jar is no longer in the repo (tidied); the 0.2.7 rollback is phase R of that run"),
    ("compare: C 0.2.5: records, store, buffs, XP, ops, the tick", "0.3.0 changes the records, store, buffs, XP, ops, tick, page (ours: phase C)"),
    ("compare: C 0.2.5: PetsCfg.<clinit> differs from 0.2.4 only in its constants", "0.3.0: the new Server Setup fields"),
    ("compare: C 0.2.5: shutdown = 0.2.4's", "0.2.7: shutdown + PetsHubOpen.unregister"),
    ("bytecode: B 0.2.2: the tick runs starter -> the one-time move -> buffs", "0.3.0: + the one-time level update between the move and the buffs"),
    ("mobs: M: SkyyMobs-0.1.5.jar (the SET pin) not found", "that 0.2.5 phase pins a SkyyMobs jar that is no longer in the repo (environment, not 0.3.0)"),
    ("ecs: OC 0.2.5: SkyyMobs 0.1.8 / SkyySacks 0.8.4 classes could not load: Class com.skyy.sacks.PickBook is not found",
     "SkyySacks-0.8.4.jar is no longer in the repo (tidied; fixer 2 run) - environment, not 0.3.0"),
] + [("live %s: D %s: 0.2 on 0.1's config: built-in looks" % (l_, s_), "the live world is NewBetaTest since 2026-10-15: its config was written by 0.2.7 "
      "(every line there), not the 0.1-era file this 0.2.5 check pins - the 0.2.7 jar fails it the same way on that copy (fixer 2 run)")
     for l_, s_ in (("start1", "start1"), ("start2", "start2"), ("mig1", "mig1"), ("mig2", "mig2"), ("loadout", "lo"))] + [
    ("live %s: D %s 0.2.2: the live config has no role / summon lines" % (l_, s_), "NewBetaTest's 0.2.7 config HAS the role / summon lines - "
     "the 0.2.7 jar fails it the same way on that copy (fixer 2 run)")
    for l_, s_ in (("start1", "start1"), ("start2", "start2"), ("mig1", "mig1"), ("mig2", "mig2"), ("loadout", "lo"))] + [
    ("D lo 0.2.3: after set + set back that file holds exactly the same lines", "on the NewBetaTest copy the 0.2.7 jar fails it the same way "
     "(that world's pet files, not 0.3.0; fixer 2 run)"),
    ("D 0.2.2 move 1: only the moved profiles' files + the ledger changed", "0.3.0: the first tick also writes the levels.030 marker into every record with pets"),
    ("bytecode: B 0.2.2: toSlot checks the role; slot2Pet gates buffs, XP and the summon creature: ['PetBuff.capMult', 'PetBuff.compute', 'PetViews.want', 'PetXp.give']",
     "0.3.0 fixer: PetBuff.capMult (the scaled Fortune / swing caps) reads the summon-slot pet through the same slot2Pet gate"),
]


# ======================================================================================================== helpers
def mk_record(Store, key):
    return Store.get(key)


def ledger_lines(mods):
    p = os.path.join(mods, "Skyy_SkyyPets", "ledger.log")
    return open(p, encoding="utf-8").read().splitlines() if os.path.exists(p) else []


def props(path):
    out = {}
    if not os.path.exists(path):
        return out
    for l in open(path, encoding="latin-1").read().splitlines():
        if not l or l.startswith("#") or "=" not in l:
            continue
        k, v = l.split("=", 1)
        out[k] = v
    return out


# ======================================================================================================== SYS (the pet system)
def run_sys(out, jar, scratch, _home):
    from jpype import JClass, JProxy
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Log, Page, Math_, Buff, Xp, Tick, Job, Mig, Rows, Fn, Kind = (P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsLog"),
        P_("PetsPage"), P_("PetMath"), P_("PetBuff"), P_("PetXp"), P_("PetTick"), P_("PetStarterJob"), P_("PetsCfgMig"), P_("CfgRows"), P_("CfgFn"), P_("PetKind"))
    Paths, UUID, Bool = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.lang.Boolean")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.join(scratch, "sys-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    pdir = os.path.join(mods, "Skyy_SkyyPets", "pets")
    K.eq(str(P_("PetsHubOpen").register()), "character:pets", "the Pets hub tab is registered (the page checks need the selected tab)")
    import soundpass_kit as SK
    # ---------------------------------------------------------------- CFG
    rows = SK.kit_rows(Rows)
    want = {"pets.starter.choose": ("starter", "bool", "true"), "pets.starter.mining": ("starter", "text", "Mouse"),
            "pets.starter.farming": ("starter", "text", "Rabbit"), "pets.starter.foraging": ("starter", "text", "Squirrel"),
            "pets.starter.combat": ("starter", "text", "Dog"), "pets.starter.delay": ("starter", "int", "5"), "pets.starter": ("starter", "text", "Rabbit"),
            "pets.level.cap": ("rebirth", "int", "50"), "pets.rebirth.levels": ("rebirth", "int", "10"), "pets.rebirth.max": ("rebirth", "int", "5"),
            "pets.rebirth.reset": ("rebirth", "choice", "one"), "pets.rebirth.statPercent": ("rebirth", "dec", "5"), "pets.rebirth.xpPercent": ("rebirth", "dec", "10"),
            "pets.fuse.enabled": ("fuse", "bool", "true"), "pets.fuse.count": ("fuse", "int", "4"), "pets.fuse.maxRarity": ("fuse", "choice", "legendary"),
            "pets.combatSeconds": ("fuse", "int", "10"), "pets.rarity.common": ("rarity", "dec", "1"), "pets.rarity.uncommon": ("rarity", "dec", "1.1"),
            "pets.rarity.rare": ("rarity", "dec", "1.2"), "pets.rarity.epic": ("rarity", "dec", "1.3"), "pets.rarity.legendary": ("rarity", "dec", "1.4"),
            "pets.rarity.mythic": ("rarity", "dec", "1.5"), "pets.curve.linear": ("xp", "dec", "120"), "pets.curve.cubic": ("xp", "dec", "0.08"),
            "pets.cap.scale": ("rarity", "bool", "true")}
    bad = [k for k, (c, t, d) in want.items() if k not in rows or rows[k][2] != c or rows[k][3] != t or rows[k][4] != d]
    K.check(not bad, "CFG the 0.3.0 Server Setup rows (category / type / default): %s" % [(k, rows.get(k, [None] * 5)[2:5]) for k in bad])
    K.check(all("live" in rows[k][9] for k in want), "CFG every new row is live (no restart)")
    K.check(abs(float(Cfg.F1) - 1.0) < 1e-9 and abs(float(Cfg.F6) - 1.5) < 1e-9 and abs(float(Cfg.CURVE_LIN) - 120) < 1e-9 and abs(float(Cfg.CURVE_CUB) - 0.08) < 1e-9
            and int(Cfg.LVL_CAP) == 50 and int(Cfg.REB_MAX) == 5 and str(Cfg.REB_RESET) == "one" and int(Cfg.FUSE_COUNT) == 4 and int(Cfg.fuseMax()) == 5
            and bool(Cfg.STARTER_CHOOSE) and int(Cfg.COMBAT_S) == 10 and bool(Cfg.CAP_SCALE), "CFG the fields read their defaults from a fresh config")
    K.check(SK.kit_check(Fn, Rows, "pets.starter.mining", "Wolf") is None and "no pet kind" in (SK.kit_check(Fn, Rows, "pets.starter.mining", "Nope") or "")
            and SK.kit_check(Fn, Rows, "pets.starter.mining", "none") is not None, "CFG the starter kind rows: a real kind passes, an unknown one / none is refused")
    K.check([int(Math_.cap(r)) for r in range(0, 8)] == [50, 60, 70, 80, 90, 100, 100, 100] and int(Math_.maxCap()) == 100 and int(Math_.cap(-3)) == 50,
            "CFG PetMath.cap: 50 + 10 per pet rebirth, at most 5 (= 100)")
    K.check([int(Math_.implied(l)) for l in (1, 50, 51, 60, 61, 70, 71, 99, 100)] == [0, 0, 1, 1, 2, 2, 3, 5, 5], "CFG PetMath.implied (the update / give)")
    Cfg.REB_MAX = 3
    K.check(int(Math_.maxCap()) == 80 and int(Math_.implied(95)) == 3 and int(Math_.cap(5)) == 80, "CFG pets.rebirth.max 3 = max level 80")
    Cfg.REB_MAX = 5
    Cfg.LVL_CAP, Cfg.REB_LEVELS = 95, 10
    K.check(int(Math_.cap(1)) == 100 and int(Math_.maxCap()) == 100, "CFG never above 100")
    Cfg.LVL_CAP = 50
    Cfg.FUSE_MAX_S = "nonsense"
    Cfg.applyScalars(Cfg.props(str(Cfg.DEFAULT_TEXT).replace("pets.fuse.maxRarity=legendary", "pets.fuse.maxRarity=bogus").replace("pets.rebirth.reset=one", "pets.rebirth.reset=zz")))
    K.check(str(Cfg.FUSE_MAX_S) == "legendary" and str(Cfg.REB_RESET) == "one", "CFG a hand-typed bad choice falls back (legendary / one)")
    Cfg.reloadAll()
    # ---------------------------------------------------------------- STA: the starter choice
    P1 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000301"), "Starter1")
    u1 = P1.pr.getUuid()
    k1 = str(Store.pkey(u1))
    Store.KEYOF.put(u1, k1)
    r1 = Store.get(k1)
    led0 = len(ledger_lines(mods))
    K.check(bool(Ops.starter(u1, r1)) and str(r1.get("starter")) == "choose" and int(r1.count()) == 0, "STA first sight: starter=choose, no pet given")
    pf1 = props(os.path.join(pdir, k1 + ".properties"))
    K.check(pf1.get("starter") == "choose", "STA ... saved at once")
    K.check(any("starter choice offered" in l for l in ledger_lines(mods)[led0:]), "STA ... one ledger line")
    K.check(not bool(Ops.starter(u1, r1)), "STA ... never twice")
    K.check(bool(Ops.starterPending(r1)) and not bool(Ops.starterPending(None)), "STA starterPending")
    # offer(): the delay, then a job; PetStarterJob opens the page once, only when no other page is open
    ran = []
    api = JProxy(PKG + "PetWorldApi", dict={"execute": lambda w, r: (ran.append(r), True)[1]})
    P_("PetWorld").API = api
    W = E.W1
    try:
        Cfg.STARTER_DELAY = 0
        Ops.OFFER.clear()
        K.check(not bool(Ops.offer(u1, None)), "STA offer: no world = nothing")
        K.check(not bool(Ops.offer(u1, W)) and Ops.OFFER.containsKey(u1), "STA offer: the first second only starts the delay")
        K.check(bool(Ops.offer(u1, W)) and len(ran) == 1, "STA offer: after the delay one job is queued")
        K.check(not bool(Ops.offer(u1, W)) and len(ran) == 1, "STA offer: then it waits 3 s before trying again")
    finally:
        P_("PetWorld").API = None
    E.pump(P1)
    K.check(E.pg(P1) is None, "STA no page open yet")
    Pw = P_("PetWorld")
    WP = P_("PetsEng").worldObj(P1.st)
    K.check(WP is not None and E.same(WP, E.W1), "FIX (the player's world W1, the one the tick passes to offer)")
    # the stage's worlds hold no entity store of their own: the world -> store step answers as the engine does (W1 = the player's store)
    Pw.API = JProxy(PKG + "PetWorldApi", dict={"store": lambda w_: P1.st if E.same(w_, E.W1) else None})
    m0 = int(Job.MOVED)
    Job(u1, E.W2).run()
    Job(u1, None).run()
    E.pump(P1)
    K.check(int(Job.MOVED) == m0 + 2 and E.pg(P1) is None and r1.get("starter.shown") is None,
            "FIX B1 a job queued on another world / with no world skips the player (MOVED +%d), nothing opens" % (int(Job.MOVED) - m0))
    other = Page(P1.pr)
    P1.pm.openCustomPage(P1.ref, P1.st, other)
    E.pump(P1)
    w0 = int(Job.WAITED)
    Job(u1, WP).run()
    K.check(int(Job.WAITED) == w0 + 1 and r1.get("starter.shown") is None, "STA the job waits while another page is open (nothing marked)")
    other.handleDataEvent(P1.ref, P1.st, '{"a":"close"}')
    E.pump(P1)
    o0 = int(Job.OPENED)
    Job(u1, WP).run()
    E.pump(P1)
    pg = E.pg(P1)
    K.check(int(Job.OPENED) == o0 + 1 and pg is not None and str(pg.getClass().getName()) == PKG + "PetsPage" and r1.get("starter.shown") is not None,
            "STA no other page: the job opens /pets once and marks starter.shown (opened %d, page %s)" % (int(Job.OPENED) - o0, pg))
    Job(u1, WP).run()
    K.check(int(Job.OPENED) == o0 + 1, "STA ... never a second time")
    Pw.API = None
    Ops.OFFER.clear()
    K.check(not bool(Ops.offer(u1, W)) and not Ops.OFFER.containsKey(u1), "STA offer: shown = nothing more queued")
    PG = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000309"), "GiveUp")
    ug = PG.pr.getUuid()
    rg = Store.get(str(Store.pkey(ug)))
    Ops.starter(ug, rg)
    nw = len([l for l in list(Log.LINES) if "gave up opening the starter" in str(l)])
    gv = [bool(Ops.starterOpenFailed(ug, rg)) for _ in range(5)]
    nw2 = len([l for l in list(Log.LINES) if "gave up opening the starter" in str(l)])
    K.check(gv == [False] * 4 + [True] and str(rg.get("starter.shown")).startswith("gave up") and nw2 == nw + 1 and bool(Ops.starterPending(rg)),
            "FIX B2 4 failed opens = retried, the 5th gives up (starter.shown, ONE warning), the choice stays pending: %s" % gv)
    Tick.leave(ug)
    K.check(not Ops.FAILS.containsKey(ug), "FIX B2 ... leaving forgets the count")
    # the starter view
    built = HT.build(pg, P1)
    w, h, sets, evs = HT.page_check(K, E, P1, built, "SkyyPt", "character", "pets", "Pets", "STA starter view")
    sel = [s for s, _t in evs]
    K.check(int(pg.view) == 2 and all(("#SkyyPtC%dAct" % i) in sel for i in range(4)) and "#SkyyPtLater" in sel, "STA the starter view: 4 Choose rows + Later bound: %s" % sel)
    K.check("Choose your first pet" in str(sets.get("#SkyyPtLowH.Text")) and "Mouse - Mining pet" in str(sets) and "Rabbit - Farming pet" in str(sets)
            and "Squirrel - Foraging pet" in str(sets) and "Dog - Combat pet" in str(sets) and "Up to +5 Farming Fortune at Lv 50" in str(sets),
            "STA the rows name the 4 kinds + what they give")
    import skyyui as SUI_

    def wpx(t):     # the one-line status (16 px bold, centred, no wrap) - the mark (+ - =) is not shown
        t = str(t)
        return SUI_.text_width(t[1:] if t[:1] in "+-=" else t, 16, bold=True)

    def vpx(t):     # a detail row value (propValue, one line)
        return SUI_.text_width(str(t), SUI_.fs(13), bold=False)
    STATUS_MAX, VALUE_MAX = 900, 660     # the body is 926 px; a value column is 906 - 220 - 8 = 678 px
    stv = str(sets.get("#SkyyPtStatus.Text"))
    try:
        _j = json.loads(stv)
        stv = str(list(_j.values())[0] if isinstance(_j, dict) else _j)
    except ValueError:
        stv = stv.strip('"')
    K.check(stv.startswith("Pick the pet") and wpx(stv) <= STATUS_MAX, "FIX2 the starter view's status fits one line (%d px): %s" % (wpx(stv), stv))

    def click(P, page, a, i=None, tok=True):
        d = '{"a":"%s"' % a + (',"i":"%s"' % i if i is not None else "") + (',"t":"%s"' % page.tok if tok else "") + "}"
        page.handleDataEvent(P.ref, P.st, d)
        E.pump(P)
        return str(page.info)
    a1 = click(P1, pg, "pick", 0)
    K.check(a1.startswith("=") and "Mouse" in a1 and int(r1.count()) == 0 and str(pg.confirm) == "pick|0", "STA the first Choose only asks: %s" % a1)
    a2 = click(P1, pg, "pick", 1)
    K.check(a2.startswith("=") and "Rabbit" in a2 and int(r1.count()) == 0 and str(pg.confirm) == "pick|1", "STA another row moves the question (still no pet)")
    click(P1, pg, "prev")
    K.check(str(pg.confirm) == "", "STA any other click cancels the question")
    click(P1, pg, "pick", 1)
    a3 = click(P1, pg, "pick", 1)
    ids1 = list(r1.ids())
    K.check(a3.startswith("+") and len(ids1) == 1 and str(r1.kindOf(ids1[0])) == "Rabbit" and int(r1.rarityOf(ids1[0])) == 1 and int(r1.levelOf(ids1[0])) == 1
            and str(r1.active(1)) == ids1[0] and not bool(Ops.starterPending(r1)), "STA the second Choose: one Common Lv 1 Rabbit in the pet slot: %s" % a3)
    pf1 = props(os.path.join(pdir, k1 + ".properties"))
    K.check(pf1.get("starter", "").isdigit() and pf1.get("active.1") == ids1[0] and pf1.get("pet.%s.src" % ids1[0]) == "starter farming", "STA ... one save holds the pet + starter=<ms>")
    K.check(int(pg.view) == 0, "STA ... the page shows the pet list")
    a4 = str(Ops.chooseStarter(u1, 0, "t"))
    pg.confirm = "pick|0"
    a5 = click(P1, pg, "pick", 0)
    K.check(a4.startswith("=") and a5.startswith("=") and int(r1.count()) == 1, "STA a second pick / a forged click = 'already', never a second pet")
    # refusals + Later + an existing profile + choice off
    P2 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000302"), "Starter2")
    u2 = P2.pr.getUuid()
    r2 = Store.get(str(Store.pkey(u2)))
    Ops.starter(u2, r2)
    E.bridge.put("profile:busy:" + str(u2), Bool.TRUE)
    K.check(str(Ops.chooseStarter(u2, 0, "t")).startswith("-Your profile is still switching") and int(r2.count()) == 0, "STA busy = refused")
    E.bridge.remove("profile:busy:" + str(u2))
    Cfg.ON = False
    K.check(str(Ops.chooseStarter(u2, 0, "t")).startswith("-Pets are switched off") and int(r2.count()) == 0, "STA pets off = refused")
    Cfg.ON = True
    Cfg.KINDS_OFF = "Mouse"
    pg2 = Page(P2.pr)
    _c, ev2 = HT.build(pg2, P2)
    K.check("#SkyyPtC0Act" not in [s for s, _t in ev2] and "#SkyyPtC1Act" in [s for s, _t in ev2], "STA a switched-off starter kind: its row is not bound")
    K.check("not available" in str(Ops.chooseStarter(u2, 0, "t")) and int(r2.count()) == 0 and bool(Ops.starterPending(r2)), "STA ... and picking it is refused")
    K.check(str(Ops.chooseStarter(u2, 7, "t")).startswith("-There is no such"), "STA an index out of range is refused")
    Cfg.KINDS_OFF = "-"
    P2.pm.openCustomPage(P2.ref, P2.st, pg2)
    E.pump(P2)
    HT.build(pg2, P2)
    click(P2, pg2, "later", tok=False)
    _c, ev3 = HT.build(pg2, P2)
    K.check(bool(pg2.later) and int(pg2.view) == 0 and "#SkyyPtPgPrev" in [s for s, _t in ev3] and "#SkyyPtC0Act" not in [s for s, _t in ev3],
            "STA Later = the pet list on this page (the choice stays open: %s)" % bool(Ops.starterPending(r2)))
    K.check(any("open /pets again to choose your first pet" in str(x) for x in _c) and not any("eggs" in str(x) for x in _c),
            "FIX2 the empty list after Later says how to get back to the choice (no eggs claim)")
    P3 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000303"), "Old3")
    r3 = Store.get(str(Store.pkey(P3.pr.getUuid())))
    r3.set("starter", "12345")
    K.check(not bool(Ops.starter(P3.pr.getUuid(), r3)) and int(r3.count()) == 0 and not bool(Ops.starterPending(r3)), "STA an existing profile (starter=<ms>) gets nothing")
    Cfg.STARTER_CHOOSE = False
    P4 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000304"), "Fixed4")
    r4 = Store.get(str(Store.pkey(P4.pr.getUuid())))
    K.check(bool(Ops.starter(P4.pr.getUuid(), r4)) and int(r4.count()) == 1 and str(r4.kindOf(r4.ids()[0])) == "Rabbit", "STA choice off = the 0.2.7 Rabbit")
    Cfg.STARTER_CHOOSE = True
    Cfg.STARTER = "none"
    P5 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000305"), "None5")
    r5 = Store.get(str(Store.pkey(P5.pr.getUuid())))
    K.check(not bool(Ops.starter(P5.pr.getUuid(), r5)) and r5.get("starter") is None, "STA Starter pet none = no starter at all")
    Cfg.STARTER = "Rabbit"
    # the per-second tick drives it (PetTick.second: starter -> roles -> level update)
    P6 = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000306"), "Tick6")
    u6 = P6.pr.getUuid()
    Tick.second(u6, "w", None)
    r6 = Store.get(str(Store.pkey(u6)))
    K.check(str(r6.get("starter")) == "choose" and int(r6.count()) == 0, "STA the tick offers the choice on first sight")
    # ---------------------------------------------------------------- BUF
    rid = ids1[0]
    r1.set("pet.%s.level" % rid, "20")
    t = list(Buff.compute(r1, "w"))
    ff = t[list(Kind.STAT_KEYS).index("fortune.farming")]
    K.check(abs(ff - 2.0) < 1e-9, "BUF the Common Lv 20 Rabbit = +2 Farming Fortune (0.2.7: 0.6): %s" % ff)
    r1.set("pet.%s.rarity" % rid, "3")
    ff3 = list(Buff.compute(r1, "w"))[list(Kind.STAT_KEYS).index("fortune.farming")]
    r1.set("pet.%s.rebirth" % rid, "2")
    ff3r = list(Buff.compute(r1, "w"))[list(Kind.STAT_KEYS).index("fortune.farming")]
    K.check(abs(ff3 - 2.4) < 1e-9 and abs(ff3r - 2.64) < 1e-9, "BUF Rare = x1.2 (2.4), + 2 pet rebirths = +10 %% (2.64): %s %s" % (ff3, ff3r))
    FF = list(Kind.STAT_KEYS).index("fortune.farming")
    r1.set("pet.%s.level" % rid, "100"); r1.set("pet.%s.rarity" % rid, "1"); r1.set("pet.%s.rebirth" % rid, None)
    c100 = list(Buff.compute(r1, "w"))[FF]
    r1.set("pet.%s.rarity" % rid, "5")
    l100 = list(Buff.compute(r1, "w"))[FF]
    r1.set("pet.%s.rebirth" % rid, "5")
    l5 = list(Buff.compute(r1, "w"))[FF]
    cmv = float(Buff.capMult(r1))
    Cfg.CAP_SCALE = False
    l5off = list(Buff.compute(r1, "w"))[FF]
    Cfg.CAP_SCALE = True
    K.check(abs(c100 - 10) < 1e-9 and abs(l100 - 14) < 1e-9 and abs(l5 - 17.5) < 1e-9 and abs(cmv - 1.75) < 1e-9 and abs(l5off - 10) < 1e-9,
            "FIX C1 caps scale: Common Lv 100 = 10, Legendary = 14, Legendary R5 = 17.5 (cap x%s); pets.cap.scale off = the fixed 10: %s %s %s %s" % (cmv, c100, l100, l5, l5off))
    Cfg.F1 = 0.3
    r1.set("pet.%s.rarity" % rid, "1"); r1.set("pet.%s.rebirth" % rid, None)
    K.check(abs(float(Buff.capMult(r1)) - 1.0) < 1e-9 and abs(float(Buff.capMult(None)) - 1.0) < 1e-9, "FIX C1 ... never below the row value (a 0.3 factor keeps the cap at 10)")
    Cfg.F1 = 1.0
    r1.set("pet.%s.rarity" % rid, "1")
    r1.set("pet.%s.rebirth" % rid, None)
    r1.set("pet.%s.level" % rid, "1")
    # ---------------------------------------------------------------- XP
    K.check(int(Math_.need(2)) == 120, "XP need(2) = 120 (0.2.7: 60)")
    tot50 = int(Math_.total(50))
    K.check(tot50 == 267380, "XP Lv 1 -> 50 = 267,380 XP (0.2.7: 133,330): %d" % tot50)
    r1.addXp(rid, 1.0e9)
    K.check(int(r1.levelOf(rid)) == 50 and int(r1.xpOf(rid)) == 0, "XP the max level 50 stops XP (xp 0)")
    K.check(int(r1.addXp(rid, 1.0e6)) == 0 and int(r1.levelOf(rid)) == 50, "XP no more levels at the cap")
    # rebirth XP bonus through PetXp.give (the pet's own skill, 100 %)
    r1.set("pet.%s.level" % rid, "1"); r1.set("pet.%s.xp" % rid, "0")
    Store.REC.put(k1, r1)
    Xp.give(u1, "Farming", 50)
    x0 = int(r1.xpOf(rid))
    r1.set("pet.%s.xp" % rid, "0"); r1.set("pet.%s.rebirth" % rid, "2")
    Xp.give(u1, "Farming", 50)
    x2 = int(r1.xpOf(rid))
    K.check(x0 == 50 and x2 == 60, "XP 2 pet rebirths = +20 %% XP (%d -> %d)" % (x0, x2))
    r1.set("pet.%s.rebirth" % rid, None); r1.set("pet.%s.level" % rid, "49"); r1.set("pet.%s.xp" % rid, "0")
    Xp.give(u1, "Farming", 10 ** 7)
    K.check(int(r1.levelOf(rid)) == 50, "XP Lv 49 -> 50 by XP")
    # ---------------------------------------------------------------- REB
    r1.set("pet.%s.level" % rid, "49")
    K.check("can be reborn at Lv 50" in str(Ops.rebWhy(r1, rid)) and not bool(Ops.rebReady(r1, rid)), "REB below the cap: not yet")
    r1.set("pet.%s.level" % rid, "50")
    K.check(Ops.rebWhy(r1, rid) is None and bool(Ops.rebReady(r1, rid)) and "ready to rebirth" in str(Ops.rebInfo(r1, rid)), "REB at the cap: ready")
    K.check(str(Ops.gate(u1, 5000)) == "-You are in combat - wait 5 s." and Ops.gate(u1, 20000) is None and Ops.gate(u1, -1) is None, "REB the combat gate (10 s)")
    K.check(str(Ops.rebirth(u1, rid, 0, "t", 3000)).startswith("-You are in combat") and int(r1.rebirthOf(rid)) == 0, "REB in combat = refused")
    ask = str(Ops.rebAsk(u1, rid, -1))
    K.check(ask.startswith("=") and "max Lv 60" in ask and "back to Lv 1" in ask and int(r1.rebirthOf(rid)) == 0, "REB the ask changes nothing: %s" % ask)
    led0 = len(ledger_lines(mods))
    res = str(Ops.rebirth(u1, rid, 0, "t", -1))
    K.check(res.startswith("+") and int(r1.rebirthOf(rid)) == 1 and int(r1.levelOf(rid)) == 1 and int(r1.xpOf(rid)) == 0 and int(r1.capOf(rid)) == 60,
            "REB rebirth 1: Lv 1, max 60: %s" % res)
    pf = props(os.path.join(pdir, k1 + ".properties"))
    K.check(pf.get("pet.%s.rebirth" % rid) == "1" and pf.get("pet.%s.level" % rid) == "1", "REB saved at once")
    nl = [l for l in ledger_lines(mods)[led0:] if "\trebirth 1\t" in l]
    K.check(len(nl) == 1 and nl[0].split("\t")[10] == "1", "REB one ledger line, column 11 = 1")
    K.check(str(Ops.rebirth(u1, rid, 0, "t", -1)).startswith("=That pet was reborn already") and int(r1.rebirthOf(rid)) == 1, "REB a doubled press (old count) = refused")
    K.check(str(Ops.rebirth(u1, rid, 1, "t", -1)).startswith("-") and int(r1.rebirthOf(rid)) == 1, "REB again below the new cap = refused")
    Cfg.REB_RESET = "keep"
    r1.set("pet.%s.level" % rid, "60")
    res = str(Ops.rebirth(u1, rid, 1, "t", -1))
    K.check(res.startswith("+") and int(r1.levelOf(rid)) == 60 and int(r1.capOf(rid)) == 70 and "Back to Lv 1" not in res, "REB keep mode: Lv 60 kept, max 70")
    Cfg.REB_RESET = "one"
    # a reborn pet keeps its adult look (Chicken: the baby Chick below Lv 30 - but not once reborn)
    ch = str(Ops.createR(r1, None, "Chicken", 1, 3, 0, 0, "t", "t", True))
    Vw = P_("PetViews")
    w0_ = Vw.want(u1, r1, k1, 1, "w", False)
    r1.set("active.1", ch)
    w1_ = str(Vw.want(u1, r1, k1, 1, "w", False))
    r1.set("pet.%s.rebirth" % ch, "1")
    w2_ = str(Vw.want(u1, r1, k1, 1, "w", False))
    K.check("|Chick|" in w1_ and "|Chicken|" in w2_, "REB a reborn Lv 3 Chicken shows the adult Chicken, not the Chick: %s / %s" % (w1_, w2_))
    r1.set("active.1", rid)
    r1.remove(ch)
    Store.INDEX.remove(ch)
    r1.set("pet.%s.rebirth" % rid, "5"); r1.set("pet.%s.level" % rid, "100")
    K.check("has all 5" in str(Ops.rebWhy(r1, rid)) and "all done" in str(Ops.rebInfo(r1, rid)), "REB R5 Lv 100 = all done")
    # a failed save puts everything back
    r1.set("pet.%s.rebirth" % rid, "0"); r1.set("pet.%s.level" % rid, "50"); r1.set("pet.%s.xp" % rid, "0")
    Store.save(r1)
    blk = os.path.join(scratch, "blocked-dir")
    open(blk, "w").write("x")
    d0 = Store.DIR
    Store.DIR = Paths.get(blk)
    res = str(Ops.rebirth(u1, rid, 0, "t", -1))
    Store.DIR = d0
    K.check(res.startswith("-Your pets could not be saved") and int(r1.rebirthOf(rid)) == 0 and int(r1.levelOf(rid)) == 50, "REB a failed save = nothing changed")
    E.bridge.put("profile:busy:" + str(u1), Bool.TRUE)
    K.check(str(Ops.rebirth(u1, rid, 0, "t", -1)).startswith("-Your profile is still switching"), "REB busy = refused")
    E.bridge.remove("profile:busy:" + str(u1))
    # ---------------------------------------------------------------- FUS
    PF = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000310"), "Fuser")
    uf = PF.pr.getUuid()
    kf = str(Store.pkey(uf))
    rf = Store.get(kf)
    rf.set("starter", "1")

    def give(kind, rar, lvl, reb=0):
        pid = str(Ops.createR(rf, None, kind, rar, lvl, 0, reb, "test", "t", True))
        assert not pid.startswith("-"), pid
        return pid
    A = give("Rabbit", 1, 10)
    Bp = give("Rabbit", 1, 30)
    C = give("Rabbit", 1, 5)
    D = give("Rabbit", 1, 2)
    K.check(str(rf.active(1)) == A, "FUS the base A is in the pet slot")
    Ef = give("Rabbit", 1, 1)
    W1 = give("Wolf", 1, 7)
    fd = [str(x) for x in Ops.fodder(rf, A)]
    K.check(sorted(fd) == sorted([Ef, D, C]), "FUS the fodder = the 3 weakest unslotted Rabbits of that rarity (not B Lv 30, not the Wolf): %s" % fd)
    K.check(str(Ops.fuseInfo(rf, A)).startswith("ready: 4 Common -> 1 Uncommon"), "FUS the detail row says ready")
    ask = str(Ops.fuseAsk(uf, A, -1))
    K.check(ask.startswith("=") and "Fuse 4 Common Rabbit (Lv 10, 1, 2, 5) into 1 Uncommon Lv 10?" in ask and int(rf.count()) == 6, "FUS the ask changes nothing: %s" % ask)
    led0 = len(ledger_lines(mods))
    res = str(Ops.fuse(uf, A, 1, None, "t", -1))
    K.check(res.startswith("+") and int(rf.count()) == 3 and rf.has(A) and rf.has(Bp) and rf.has(W1) and not rf.has(C) and not rf.has(D) and not rf.has(Ef)
            and int(rf.rarityOf(A)) == 2 and int(rf.levelOf(A)) == 10 and str(rf.active(1)) == A, "FUS 4 -> 1: A Uncommon Lv 10 (kept its id + slot), B kept: %s" % res)
    K.check(not Store.INDEX.containsKey(C) and not Store.INDEX.containsKey(D) and not Store.INDEX.containsKey(Ef) and Store.INDEX.get(A) == kf, "FUS the index forgot the fodder")
    pf = props(os.path.join(pdir, kf + ".properties"))
    K.check(pf.get("pet.%s.rarity" % A) == "2" and ("pet.%s.kind" % C) not in pf and ("pet.%s.kind" % Bp) in pf, "FUS one save holds the result")
    ll = ledger_lines(mods)[led0:]
    rs = [l.split("\t")[8].split(" ")[0] for l in ll]
    K.check(rs == ["fuse-intent", "fuse-take", "fuse-take", "fuse-take", "fuse-up", "fuse-done"], "FUS ledger: intent, take x3, up, done: %s" % rs)
    K.check(str(Ops.fuse(uf, A, 1, None, "t", -1)).startswith("=That pet is Uncommon now"), "FUS a stale / doubled press (old rarity) = nothing fused again")
    # best of 4: the result takes the best pet's level + rebirths
    X = give("Rabbit", 2, 40, 1)
    Y = give("Rabbit", 2, 3)
    Z = give("Rabbit", 2, 2)
    askx = str(Ops.fuseAsk(uf, A, -1))
    K.check("(Lv 10, 2, 3, 40 R1) into 1 Rare Lv 40 R1?" in askx and "most-grown" in str(Ops.fuseInfo(rf, A)),
            "FIX A4 the Fuse question names the result's rebirths; the rule is on the Fusing row (fixer 2: one line): %s" % askx)
    res = str(Ops.fuse(uf, A, 2, None, "t", -1))
    K.check(res.startswith("+") and int(rf.rarityOf(A)) == 3 and int(rf.levelOf(A)) == 40 and int(rf.rebirthOf(A)) == 1 and not rf.has(X),
            "FUS the result = the best of the 4 (X: 1 pet rebirth, Lv 40): %s" % res)
    # refusals
    K.check("You need 4" in str(Ops.fuseWhy(rf, A)), "FUS too few = refused")
    S1 = give("Wolf", 1, 1); S2 = give("Wolf", 1, 1)
    rf.set("active.2", "")
    S3 = give("Wolf", 1, 1)
    rf.set("slot2.unlocked", "true")
    K.check(str(Ops.toSlot(uf, S3, 2, "t")).startswith("+"), "FUS (a Wolf in the summon slot)")
    K.check("You need 4" in str(Ops.fuseWhy(rf, W1)), "FUS a slotted pet is never fodder (W1 + S1 + S2 unslotted, S3 summoned = 3)")
    Ops.toSlot(uf, W1, 2, "t")
    K.check(Ops.fuseWhy(rf, W1) is None, "FUS the base itself may be slotted")
    Cfg.FUSE_ON = False
    K.check("switched off" in str(Ops.fuse(uf, W1, 1, None, "t", -1)) and int(rf.rarityOf(W1)) == 1, "FUS fusing off = refused")
    Cfg.FUSE_ON = True
    Cfg.KINDS_OFF = "Wolf"
    K.check("switched off" in str(Ops.fuseWhy(rf, W1)), "FUS a switched-off kind = refused")
    Cfg.KINDS_OFF = "-"
    rf.set("pet.%s.rarity" % A, "5")
    K.check("fusing stops at Legendary" in str(Ops.fuseWhy(rf, A)), "FUS at Legendary = stops")
    rf.set("pet.%s.rarity" % A, "3")
    K.check(str(Ops.fuse(uf, W1, 1, None, "t", 3000)).startswith("-You are in combat"), "FUS in combat = refused")
    import threading, time, jpype
    held, done_ = threading.Event(), threading.Event()

    def holder():
        with jpype.synchronized(rf):
            held.set()
            time.sleep(0.6)
        done_.set()
    for nm_, fn_ in (("fuse", lambda: Ops.fuse(uf, A, 3, None, "t", -1)), ("rebirth", lambda: Ops.rebirth(uf, A, 1, "t", -1)),
                     ("level update", lambda: Ops.migSync(uf, rf))):
        held.clear(); done_.clear()
        th = threading.Thread(target=holder)
        th.start()
        held.wait(5)
        t0_ = time.time()
        fn_()
        dt_ = time.time() - t0_
        th.join()
        K.check(dt_ >= 0.35, "FIX B3 %s waits while another thread holds the record (%.2f s)" % (nm_, dt_))
    # a failed save = nothing changed (+ fuse-abort)
    before = sorted(str(x) for x in rf.ids())
    led0 = len(ledger_lines(mods))
    Store.DIR = Paths.get(blk)
    res = str(Ops.fuse(uf, W1, 1, None, "t", -1))
    Store.DIR = d0
    K.check(res.startswith("-Your pets could not be saved") and sorted(str(x) for x in rf.ids()) == before and int(rf.rarityOf(W1)) == 1
            and Store.INDEX.containsKey(S1) and str(rf.active(2)) == W1, "FUS a failed save: all 4 pets back, rarity unchanged")
    K.check([l.split("\t")[8].split(" ")[0] for l in ledger_lines(mods)[led0:]] == ["fuse-intent", "fuse-abort"], "FUS ... ledger intent + abort")
    # the page: ask, fuse, a third press only asks again
    rf.set("pet.%s.level" % W1, "50")
    pgf = Page(PF.pr)
    PF.pm.openCustomPage(PF.ref, PF.st, pgf)
    E.pump(PF)
    HT.build(pgf, PF)
    pgf.sel, pgf.view = W1, 1
    built = HT.build(pgf, PF)
    w, h, sets, evs = HT.page_check(K, E, PF, built, "SkyyPt", "character", "pets", "Pets", "PAGE detail (can fuse + rebirth)")
    sel = [s for s, _t in evs]
    K.check("#SkyyPtB5" in sel and "#SkyyPtB6" in sel and W1 in str(sets.get("#SkyyPtD12V.Text")) and "ready" in str(sets.get("#SkyyPtD5V.Text"))
            and "ready to rebirth" in str(sets.get("#SkyyPtD4V.Text")) and "bonus x1" in str(sets.get("#SkyyPtD1V.Text")) and "50 / 50" in str(sets.get("#SkyyPtD2V.Text")),
            "PAGE detail: 13 rows (rebirths, fusing, bonus x1, 50 / 50) + Fuse and Rebirth bound")
    q1 = click(PF, pgf, "fuse")
    K.check(q1.startswith("=") and int(rf.rarityOf(W1)) == 1, "PAGE Fuse press 1 asks: %s" % q1)
    q2 = click(PF, pgf, "fuse")
    K.check(q2.startswith("+") and int(rf.rarityOf(W1)) == 2 and not rf.has(S1) and not rf.has(S2), "PAGE Fuse press 2 fuses (summoned S3 kept: %s)" % rf.has(S3))
    q3 = click(PF, pgf, "fuse")
    K.check(not q3.startswith("+") and int(rf.rarityOf(W1)) == 2, "PAGE a third press never fuses again: %s" % q3)
    _c, evn = HT.build(pgf, PF)
    K.check("#SkyyPtB5" not in [s for s, _t in evn], "PAGE ... Fuse is not bound any more (not enough Uncommon Wolves)")
    q4 = click(PF, pgf, "reb")
    q5 = click(PF, pgf, "reb")
    K.check(q4.startswith("=") and q5.startswith("+") and int(rf.rebirthOf(W1)) == 1 and int(rf.levelOf(W1)) == 1, "PAGE Rebirth: press 1 asks, press 2 rebirths")
    pgf.handleDataEvent(PF.ref, PF.st, '{"a":"fuse","t":"stale"}')
    K.check("page changed" in str(pgf.info), "PAGE a stale token is refused")
    # FIX2 the Fuse question pins the pets it would use up: a new, weaker pet between the two presses = asked again, nothing fused
    PK_ = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000321"), "Pin")
    uk = PK_.pr.getUuid()
    rk = Store.get(str(Store.pkey(uk)))
    rk.set("starter", "1")

    def givek(kind, lvl, rar=1, reb=0):
        pid = str(Ops.createR(rk, None, kind, rar, lvl, 0, reb, "test", "t", True))
        assert not pid.startswith("-"), pid
        return pid
    KA, KB, KC, KD = givek("Rabbit", 20), givek("Rabbit", 5), givek("Rabbit", 6), givek("Rabbit", 7)
    pgk = Page(PK_.pr)
    PK_.pm.openCustomPage(PK_.ref, PK_.st, pgk)
    E.pump(PK_)
    HT.build(pgk, PK_)
    pgk.sel, pgk.view = KA, 1
    HT.build(pgk, PK_)
    k1_ = click(PK_, pgk, "fuse")
    KN = givek("Rabbit", 1)
    k2_ = click(PK_, pgk, "fuse")
    K.check(k1_.startswith("=") and "(Lv 20, 5, 6, 7)" in k1_ and k2_.startswith("=") and "(Lv 20, 1, 5, 6)" in k2_ and int(rk.count()) == 5 and int(rk.rarityOf(KA)) == 1,
            "FIX2 a weaker pet arrived between the presses: asked again (naming the new set), nothing fused: %s / %s" % (k1_, k2_))
    k3_ = click(PK_, pgk, "fuse")
    K.check(k3_.startswith("+") and rk.has(KD) and not rk.has(KN) and not rk.has(KB) and int(rk.rarityOf(KA)) == 2,
            "FIX2 ... the next press fuses exactly the set the new question named (KD Lv 7 kept): %s" % k3_)
    M1, M2, M3, M4 = givek("Mouse", 3), givek("Mouse", 2), givek("Mouse", 4), givek("Mouse", 9)
    stale = str(Ops.fuse(uk, M1, 1, "%s,%s,%s" % (M2, M3, "zzzzzzzz"), "t", -1))
    K.check(stale.startswith("=Your pets changed") and rk.has(M2) and int(rk.rarityOf(M1)) == 1, "FIX2 the engine step: other fodder than the question named = nothing fused: %s" % stale)
    fk_ = str(Ops.fodderKey(rk, M1))
    K.check(fk_ == ",".join(sorted([M2, M3, M4])) and str(Ops.fuse(uk, M1, 1, fk_, "t", -1)).startswith("+") and int(rk.rarityOf(M1)) == 2,
            "FIX2 ... the named fodder = fused (key %s)" % fk_)
    # FIX2 every new status line fits one line, every new detail value fits its column (the longest built-in name: Skeleton Archer)
    sk = [givek("Skeleton", 100, 4, 5) for _ in range(4)]
    lg = givek("Skeleton", 90, 5, 4)
    one_ = givek("Skeleton", 10, 5)
    Cfg.FUSE_MAX_S = "mythic"
    texts = [str(Ops.fuseAsk(uk, sk[0], -1)), str(Ops.rebAsk(uk, lg, -1)), str(Ops.fuseWhy(rk, one_))]
    vals = [str(Ops.rebInfo(rk, lg)), str(Ops.fuseInfo(rk, sk[0])), str(Ops.fuseInfo(rk, one_)), str(Ops.fuseInfo(rk, lg))]
    texts.append(str(Ops.fuse(uk, sk[0], 4, str(Ops.fodderKey(rk, sk[0])), "t", -1)))
    texts.append(str(Ops.rebirth(uk, lg, 4, "t", -1)))
    vals += [str(Ops.rebInfo(rk, lg)), str(Ops.rebInfo(rk, sk[0]))]
    Cfg.FUSE_COUNT = 10
    tens = [givek("Mouse", 1 + i) for i in range(10)]
    texts.append(str(Ops.fuseAsk(uk, tens[0], -1)))
    Cfg.FUSE_COUNT = 4
    Cfg.REB_RESET = "keep"
    vals.append(str(Ops.rebInfo(rk, tens[0])))
    rk.set("pet.%s.level" % tens[9], "50")
    vals.append(str(Ops.rebInfo(rk, tens[9])))
    texts.append(str(Ops.rebAsk(uk, tens[9], -1)))
    Cfg.REB_RESET = "one"
    Cfg.FUSE_MAX_S = "legendary"
    Cfg.KINDS_OFF = "Squirrel"
    texts += [str(Ops.pickAsk(i)) for i in range(4)] + [str(Ops.gate(uk, 1)), "-Your pets are being updated to the new pet levels - try again in a moment."]
    Cfg.KINDS_OFF = "-"
    wide = [(int(wpx(t)), t) for t in texts if wpx(t) > STATUS_MAX]
    widev = [(int(vpx(t)), t) for t in vals if vpx(t) > VALUE_MAX]
    K.check(len(texts) == 13 and all(t[:1] in "+-=" for t in texts) and not wide, "FIX2 the new status lines fit one line (%d px max, longest %d px): %s" % (STATUS_MAX, max(int(wpx(t)) for t in texts), wide or texts[:2]))
    K.check(not widev, "FIX2 the new detail values fit their column (%d px max, longest %d px): %s" % (VALUE_MAX, max(int(vpx(t)) for t in vals), widev or vals[:2]))
    K.check(texts[3].startswith("+Fused 4 Epic Skeleton Archer") and texts[4].startswith("+Legendary Skeleton Archer reborn (5 / 5)") and "best 10" in texts[5],
            "FIX2 (the worst cases really ran: a fuse, a 5th rebirth, a 10-pet question): %s | %s | %s" % (texts[3], texts[4], texts[5]))
    # the NO-DUPE fuzz: random fuses / rebirths / XP / slot moves / failed saves; after every step the file on disk = memory and the index
    rnd = random.Random(30)
    PZ = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000320"), "Fuzz")
    uz = PZ.pr.getUuid()
    kz = str(Store.pkey(uz))
    rz = Store.get(kz)
    rz.set("starter", "1")
    rz.set("slot2.unlocked", "true")
    kinds = ["Rabbit", "Mouse", "Wolf"]
    for _ in range(40):
        Ops.createR(rz, None, rnd.choice(kinds), rnd.choice([1, 1, 1, 2]), rnd.randint(1, 50), 0, 0, "fz", "t", True)
    created, fused, fails, ops_ = int(rz.count()), 0, 0, 0
    probs = []
    for step in range(300):
        ids = [str(x) for x in rz.ids()]
        if not ids:
            break
        op = rnd.random()
        fail = rnd.random() < 0.12
        if fail:
            Store.DIR = Paths.get(blk)
        try:
            pid = rnd.choice(ids)
            if op < 0.45:
                n0 = int(rz.count())
                res = str(Ops.fuse(uz, pid, int(rz.rarityOf(pid)), None, "fz", -1))
                if res.startswith("+"):
                    fused += 1
                    if int(rz.count()) != n0 - 3:
                        probs.append("fuse count %d -> %d" % (n0, int(rz.count())))
            elif op < 0.6:
                rz.set("pet.%s.level" % pid, str(int(rz.capOf(pid))))
                Ops.rebirth(uz, pid, int(rz.rebirthOf(pid)), "fz", -1)
            elif op < 0.75:
                rz.addXp(pid, rnd.random() * 5e5)
            elif op < 0.9:
                Ops.toSlot(uz, pid, rnd.choice([1, 2]), "fz")
            else:
                Ops.createR(rz, None, rnd.choice(kinds), 1, 1, 0, 0, "fz", "t", True)
                created += 1
            ops_ += 1
        finally:
            Store.DIR = d0
        if fail:
            fails += 1
            Store.save(rz)
        mem = sorted((str(x), int(rz.rarityOf(x)), int(rz.levelOf(x)), int(rz.rebirthOf(x))) for x in rz.ids())
        if not Store.save(rz) and rz.isDirty():
            probs.append("save failed at step %d" % step)
        disk = props(os.path.join(pdir, kz + ".properties"))
        dids = sorted(k[4:-5] for k in disk if k.startswith("pet.") and k.endswith(".kind"))
        if dids != [m[0] for m in mem]:
            probs.append("step %d: disk ids != memory" % step)
        dd = sorted((i_, int(disk.get("pet.%s.rarity" % i_, "1")), int(disk.get("pet.%s.level" % i_, "1")), int(disk.get("pet.%s.rebirth" % i_, "0"))) for i_ in dids)
        if dd != mem:
            probs.append("step %d: disk rows != memory" % step)
        idx = sorted(str(k) for k in Store.INDEX.keySet() if str(Store.INDEX.get(k)) == kz)
        if idx != [m[0] for m in mem]:
            probs.append("step %d: index != file (%d / %d)" % (step, len(idx), len(mem)))
        if any(int(rz.levelOf(x)) > int(rz.capOf(x)) for x in rz.ids()):
            probs.append("step %d: a level above its cap" % step)
    K.check(not probs, "FUS NO-DUPE fuzz: 300 steps (%d ops, %d fuses, %d failed saves, %d pets made): disk = memory = index, never 4 pets AND the result: %s"
            % (ops_, fused, fails, created, probs[:5]))
    K.check(fused >= 3 and fails >= 10, "FUS ... the fuzz really fused (%d) and really failed saves (%d)" % (fused, fails))
    Store.REC.remove(kz)
    rz2 = Store.get(kz)
    K.check(sorted(str(x) for x in rz2.ids()) == sorted(str(x) for x in rz.ids()), "FUS ... a fresh read of the file = the record")
    # fuse recovery after a cut-off: three intents with no done (fodder all there / all gone / mixed)
    rec_mods = os.path.join(scratch, "rec-mods")
    rroot = os.path.join(rec_mods, "Skyy_SkyyPets")
    os.makedirs(os.path.join(rroot, "pets"), exist_ok=True)
    r0, d00 = Store.ROOT, Store.DIR
    Store.ROOT = Paths.get(rroot)
    Store.DIR = Store.ROOT.resolve("pets")
    open(os.path.join(rroot, "pets", "kk.properties"), "w", encoding="latin-1").write(
        "v=1\nseq=1\npet.aaaaaaaa.kind=Rabbit\npet.aaaaaaaa.rarity=1\npet.bbbbbbbb.kind=Rabbit\npet.bbbbbbbb.rarity=1\npet.cccccccc.kind=Rabbit\npet.cccccccc.rarity=1\n"
        "pet.dddddddd.kind=Rabbit\npet.dddddddd.rarity=2\npet.eeeeeeee.kind=Rabbit\npet.eeeeeeee.rarity=1\n")
    L = lambda base, fid, fod: "1\t%s\tRabbit\t1\t5\t0\tkk\tkk\tfuse-intent %s fodder=%s 1->2 best=%s\tt\t0" % (base, fid, fod, base)
    open(os.path.join(rroot, "ledger.log"), "w", encoding="utf-8").write(
        L("aaaaaaaa", "f1", "bbbbbbbb,cccccccc,eeeeeeee") + "\n" + L("dddddddd", "f2", "x1111111,x2222222,x3333333") + "\n"
        + L("aaaaaaaa", "f3", "bbbbbbbb,x4444444,x5555555") + "\n" + L("aaaaaaaa", "f4", "q,r,s") + "\n"
        + "2\taaaaaaaa\tRabbit\t1\t5\t0\tkk\tkk\tfuse-done f4\tt\t0\n")
    Store.scanAll()
    fr1 = [int(x) for x in Store.fuseRecover()]
    ll = open(os.path.join(rroot, "ledger.log"), encoding="utf-8").read().splitlines()
    K.check(fr1 == [3, 1, 1, 1] and any("fuse-abort f1 " in l for l in ll) and any("fuse-done f2 " in l for l in ll) and not any("f3 (" in l for l in ll),
            "FUS recovery: f1 fodder all there = abort, f2 all gone = done, f3 mixed = a warning only, f4 closed = skipped: %s" % fr1)
    fr2 = [int(x) for x in Store.fuseRecover()]
    K.check(fr2 == [1, 0, 0, 1] and len(open(os.path.join(rroot, "ledger.log"), encoding="utf-8").read().splitlines()) == len(ll), "FUS recovery: a second start writes nothing more: %s" % fr2)
    Store.ROOT, Store.DIR = r0, d00
    Store.scanAll()
    # restore guard: a fused-away pet (newest line fuse-take) needs force
    res = str(Ops.admin("t", "restore", "Fuser", C, None, None))
    K.check(res.startswith("-") and "used up in a fuse" in res and not rf.has(C), "ADM restore of a fused-away pet = refused: %s" % res[:90])
    rf = Store.get(kf)
    res = str(Ops.admin("t", "restore", "Fuser", C, "force", None))
    K.check(res.startswith("+") and Store.get(kf).has(C), "ADM ... with force it comes back")
    # ---------------------------------------------------------------- ADM
    res = str(Ops.admin("t", "give", "Fuser", "Fox", "Rare", "75"))
    rf = Store.get(kf)
    nid = [str(x) for x in rf.ids() if str(rf.kindOf(x)) == "Fox"][0]
    K.check(res.startswith("+") and int(rf.rebirthOf(nid)) == 3 and int(rf.levelOf(nid)) == 75 and "3 pet rebirths" in res, "ADM give Lv 75 = 3 pet rebirths: %s" % res)
    K.check(str(Ops.admin("t", "give", "Fuser", "Fox", "Rare", "101")) == "-Level is 1-100.", "ADM give Lv 101 refused")
    K.check("Lv 75 / 80 R3" in str(Ops.line(rf, nid)), "ADM list line: Lv 75 / 80 R3")
    Ops.admin("t", "take", "Fuser", nid, None, None)
    take = [l for l in ledger_lines(mods) if l.split("\t")[1] == nid][-1]
    K.check(take.split("\t")[8] == "take" and take.split("\t")[10] == "3", "ADM take writes the rebirths (column 11 = 3)")
    res = str(Ops.admin("t", "restore", "Fuser", nid, None, None))
    rf = Store.get(kf)
    K.check(res.startswith("+") and int(rf.rebirthOf(nid)) == 3 and int(rf.levelOf(nid)) == 75, "ADM restore keeps the 3 pet rebirths")
    Ops.admin("t", "take", "Fuser", nid, None, None)
    with open(os.path.join(mods, "Skyy_SkyyPets", "ledger.log"), "a", encoding="utf-8") as f_:
        f_.write("9\t%s\tFox\t3\t65\t0\t%s\t\ttake\tt\n" % (nid, kf))
    res = str(Ops.admin("t", "restore", "Fuser", nid, None, None))
    rf = Store.get(kf)
    K.check(res.startswith("+") and int(rf.rebirthOf(nid)) == 2 and int(rf.levelOf(nid)) == 65, "ADM an old 10-column line = the implied rebirths (Lv 65 -> 2)")
    # ---------------------------------------------------------------- MIG: the one-time level update
    PM = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000330"), "Mig")
    um = PM.pr.getUuid()
    km = str(Store.pkey(um))
    open(os.path.join(pdir, km + ".properties"), "w", encoding="latin-1").write(
        "v=1\nseq=3\nstarter=1\nactive.1=m0000001\n" + "".join("pet.%s.kind=Fox\npet.%s.rarity=2\npet.%s.level=%d\npet.%s.xp=%d\n" % (i_, i_, i_, l_, i_, x_) for i_, l_, x_ in
        (("m0000001", 30, 77), ("m0000002", 55, 5), ("m0000003", 60, 0), ("m0000004", 61, 9), ("m0000005", 100, 0))) + "pet.m0000006.kind=Fox\npet.m0000006.level=68\npet.m0000006.rebirth=2\n")
    Store.scanAll()
    rm = Store.get(km)
    before = open(os.path.join(pdir, km + ".properties"), "rb").read()
    Store.KEYOF.put(um, km)
    w1 = str(Ops.rebWhy(rm, "m0000005")); w2 = str(Ops.fuseWhy(rm, "m0000005")); w3 = str(Ops.rebirth(um, "m0000005", 0, "t", -1))
    K.check(bool(Ops.migWait(rm)) and all("being updated" in x for x in (w1, w2, w3)) and int(rm.levelOf("m0000005")) == 100 and int(rm.rebirthOf("m0000005")) == 0,
            "FIX A1 before the level update: Rebirth / Fuse of a Lv 100 R0 pet wait (no reset to Lv 1): %s / %s / %s" % (w1, w2, w3))
    fo, ev_ = Cfg.FILE_OK, Cfg.EVER_FILE
    Cfg.FILE_OK, Cfg.EVER_FILE = False, True
    resu = str(Ops.migrateLevels(um, rm))
    Cfg.FILE_OK, Cfg.EVER_FILE = fo, ev_
    K.check(resu.startswith("-the config file could not be read") and rm.get("levels.030") is None and int(rm.rebirthOf("m0000002")) == 0
            and open(os.path.join(pdir, km + ".properties"), "rb").read() == before, "FIX A3 an unreadable config = the level update waits (nothing written, no marker): %s" % resu)
    led0 = len(ledger_lines(mods))
    res = str(Ops.migrateLevels(um, rm))
    reb = dict((i_, int(rm.rebirthOf(i_))) for i_ in ("m0000001", "m0000002", "m0000003", "m0000004", "m0000005", "m0000006"))
    lv = dict((i_, int(rm.levelOf(i_))) for i_ in reb)
    K.check(res == "+4" and reb == {"m0000001": 0, "m0000002": 1, "m0000003": 1, "m0000004": 2, "m0000005": 5, "m0000006": 2}, "MIG implied rebirths (55->1, 60->1, 61->2, 100->5; Lv 30 and the R2 pet untouched): %s %s" % (res, reb))
    K.check(lv == {"m0000001": 30, "m0000002": 55, "m0000003": 60, "m0000004": 61, "m0000005": 100, "m0000006": 68} and int(rm.xpOf("m0000002")) == 5 and int(rm.xpOf("m0000004")) == 9,
            "MIG every level + XP kept")
    hist = [f_ for f_ in os.listdir(os.path.join(mods, "Skyy_SkyyPets", "history")) if f_.startswith(km + ".") and "before-0.3.0" in f_]
    K.check(len(hist) == 1 and open(os.path.join(mods, "Skyy_SkyyPets", "history", hist[0]), "rb").read() == before, "MIG one History copy, byte-equal to the file before")
    pf = props(os.path.join(pdir, km + ".properties"))
    K.check(pf.get("levels.030", "").isdigit() and pf.get("pet.m0000005.rebirth") == "5", "MIG saved with the marker")
    ml = [l for l in ledger_lines(mods)[led0:] if "0.3.0 level update" in l]
    K.check(len(ml) == 4, "MIG one ledger line per changed pet")
    cl = open(os.path.join(mods, "Skyy_SkyyPets", "level-update-changes.log"), encoding="utf-8").read()
    K.check(km in cl and "Undo:" in cl and hist[0] in cl, "MIG the change-log line names the History copy + the Undo")
    ul_ = cl[cl.find("delete only these lines: "):cl.find(" and the levels.030 line")]
    K.check(cl.find("delete only these lines: ") >= 0 and sorted(ul_[len("delete only these lines: "):].split(", ")) == ["pet.m0000002.rebirth=1", "pet.m0000003.rebirth=1",
            "pet.m0000004.rebirth=2", "pet.m0000005.rebirth=5"] and "WHOLE file" in cl and "m0000001" not in ul_ and "m0000006" not in ul_, "FIX A2 the Undo names only the added lines; the History copy is flagged as the whole file")
    K.check(not bool(Ops.migWait(rm)) and "can be reborn at Lv 70" in str(Ops.rebWhy(rm, "m0000004")),
            "FIX A1 after the update the gate opens (Lv 61 R2: next at Lv 70): %s" % Ops.rebWhy(rm, "m0000004"))
    K.check(str(Ops.migrateLevels(um, rm)) == "", "MIG a second run = nothing")
    # nothing to change -> marker only, no History copy
    PN = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000331"), "Mig2")
    rn = Store.get(str(Store.pkey(PN.pr.getUuid())))
    rn.set("starter", "1")
    Ops.createR(rn, None, "Fox", 1, 40, 0, 0, "t", "t", True)
    h0 = len(os.listdir(os.path.join(mods, "Skyy_SkyyPets", "history")))
    K.check(str(Ops.migrateLevels(PN.pr.getUuid(), rn)) == "=" and rn.get("levels.030") is not None and len(os.listdir(os.path.join(mods, "Skyy_SkyyPets", "history"))) == h0,
            "MIG nothing to change = the marker only (no History copy)")
    # a failed History copy = nothing changes
    PB = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000332"), "Mig3")
    kb = str(Store.pkey(PB.pr.getUuid()))
    open(os.path.join(pdir, kb + ".properties"), "w", encoding="latin-1").write("v=1\nseq=1\nstarter=1\npet.b0000001.kind=Fox\npet.b0000001.level=80\n")
    Store.scanAll()
    rb = Store.get(kb)
    hdir = os.path.join(mods, "Skyy_SkyyPets", "history")
    shutil.move(hdir, hdir + ".off")
    open(hdir, "w").write("x")
    res = str(Ops.migrateLevels(PB.pr.getUuid(), rb))
    os.remove(hdir)
    shutil.move(hdir + ".off", hdir)
    K.check(res.startswith("-") and int(rb.rebirthOf("b0000001")) == 0 and rb.get("levels.030") is None, "MIG a failed History copy = nothing changed (tried again later)")
    K.check(str(Ops.migrateLevels(PB.pr.getUuid(), rb)) == "+1" and int(rb.rebirthOf("b0000001")) == 3, "MIG ... next second it works (Lv 80 -> 3)")
    # FIX2 STATE-based: 0.3.0 -> 0.2.7 -> 0.3.0 (0.2.7 keeps the levels.030 line; its pets level to 100 with no cap) - pets above their
    # max level are updated again whatever the marker says; pets within their max untouched; never a free rebirth no count justifies
    PR_ = E.mkp(UUID.fromString("00000000-0000-0000-0000-000000000333"), "Rollback")
    ur = PR_.pr.getUuid()
    kr = str(Store.pkey(ur))
    open(os.path.join(pdir, kr + ".properties"), "w", encoding="latin-1").write(
        "v=1\nseq=1\nstarter=1\nlevels.030=1700000000000\npet.r0000001.kind=Fox\npet.r0000001.level=100\npet.r0000001.xp=7\n"
        "pet.r0000002.kind=Fox\npet.r0000002.level=85\npet.r0000002.rebirth=2\npet.r0000003.kind=Fox\npet.r0000003.level=68\npet.r0000003.rebirth=2\n"
        "pet.r0000004.kind=Fox\npet.r0000004.level=40\n")
    Store.scanAll()
    rr_ = Store.get(kr)
    Store.KEYOF.put(ur, kr)
    w1 = str(Ops.rebWhy(rr_, "r0000001"))
    w2 = str(Ops.rebirth(ur, "r0000001", 0, "t", -1))
    K.check(bool(Ops.migWait(rr_)) and "being updated" in w1 and "being updated" in w2 and int(rr_.levelOf("r0000001")) == 100 and int(rr_.rebirthOf("r0000001")) == 0,
            "FIX2 the marker is already there (rollback + re-deploy) and a Lv 100 R0 pet: Rebirth waits, no reset to Lv 1: %s / %s" % (w1, w2))
    res = str(Ops.migrateLevels(ur, rr_))
    got = dict((i_, (int(rr_.levelOf(i_)), int(rr_.rebirthOf(i_)))) for i_ in ("r0000001", "r0000002", "r0000003", "r0000004"))
    K.check(res == "+2" and got == {"r0000001": (100, 5), "r0000002": (85, 4), "r0000003": (68, 2), "r0000004": (40, 0)} and int(rr_.xpOf("r0000001")) == 7
            and str(rr_.get("levels.030")) == "1700000000000",
            "FIX2 ... the update runs again: Lv 100 R0 -> R5, Lv 85 R2 -> R4 (levels + XP kept), pets within their max untouched, the old marker kept: %s %s" % (res, got))
    pf = props(os.path.join(pdir, kr + ".properties"))
    K.check(pf.get("pet.r0000001.rebirth") == "5" and pf.get("pet.r0000002.rebirth") == "4", "FIX2 ... saved")
    cl2 = open(os.path.join(mods, "Skyy_SkyyPets", "level-update-changes.log"), encoding="utf-8").read().splitlines()[-1]
    K.check(kr in cl2 and "again" in cl2 and "delete only these lines: pet.r0000001.rebirth=5; change only these lines: pet.r0000002.rebirth=4 back to 2 (" in cl2
            and "levels.030" not in cl2, "FIX2 ... its Undo deletes the added line and changes the raised one back (no marker to delete): %s" % cl2[cl2.find("Undo"):][:220])
    K.check(not bool(Ops.migWait(rr_)) and str(Ops.migrateLevels(ur, rr_)) == "" and Ops.rebWhy(rr_, "r0000001") is not None, "FIX2 ... then quiet")
    Cfg.REB_LEVELS = 0
    rr_.set("pet.r0000004.level", "60")
    K.check(not bool(Ops.needsLevelFix(rr_, "r0000004")) and not bool(Ops.migWait(rr_)) and str(Ops.migrateLevels(ur, rr_)) == "" and int(rr_.rebirthOf("r0000004")) == 0,
            "FIX2 no free rebirths when no count could hold the level (max level gain 0, Lv 60 R0)")
    Cfg.REB_LEVELS = 10
    rr_.set("pet.r0000004.level", "40")
    Store.save(rr_)
    # FUZZ: 400 random pets in 20 files
    rnd = random.Random(7)
    probs = []
    for fi in range(20):
        key = "fz%02d" % fi
        lines_ = ["v=1", "seq=1", "starter=1"]
        want_ = {}
        for pi in range(20):
            pid = "z%02d%05d" % (fi, pi)
            lvl, xp_ = rnd.randint(1, 100), rnd.randint(0, 9999)
            pre = rnd.random() < 0.15
            lines_ += ["pet.%s.kind=Rabbit" % pid, "pet.%s.level=%d" % (pid, lvl), "pet.%s.xp=%d" % (pid, xp_)]
            if pre:
                lines_.append("pet.%s.rebirth=4" % pid)
            want_[pid] = (lvl, xp_, (5 if lvl > 90 else 4) if pre else (0 if lvl <= 50 else -(-(lvl - 50) // 10)))     # fixer 2: R4 above Lv 90 -> R5
        open(os.path.join(pdir, key + ".properties"), "w", encoding="latin-1").write("\n".join(lines_) + "\n")
        Store.REC.remove(key)
        rr = Store.get(key)
        Ops.migrateLevels(UUID(0, fi + 900), rr)
        Store.REC.remove(key)
        rr = Store.get(key)
        for pid, (lvl, xp_, rb_) in want_.items():
            got = (int(rr.levelOf(pid)), int(rr.xpOf(pid)), int(rr.rebirthOf(pid)))
            if got != (lvl, xp_, rb_):
                probs.append("%s %s want %s" % (pid, got, (lvl, xp_, rb_)))
            if rb_ not in (4, 5) and lvl > 50 and not (int(Math_.cap(rb_)) >= lvl > int(Math_.cap(rb_ - 1))):
                probs.append("%s not minimal" % pid)
    K.check(not probs, "MIG FUZZ 400 pets: level + XP kept, the fewest rebirths that hold the level, pre-set rebirths kept unless below the level (read back from disk): %s" % probs[:4])
    # ---------------------------------------------------------------- CMIG: the one-time config update
    D7 = compat_text(str(Cfg.DEFAULT_TEXT)).replace("pets.level.cap=100", "pets.level.cap=50").replace("pets.rebirth.max=0", "pets.rebirth.max=5").replace("pets.starter.choose=false", "pets.starter.choose=true")
    # a 0.2.7 file has no 0.3.0 lines at all
    old_lines = [l for l in D7.split("\n") if not l.split("=")[0] in [r_ for r_ in want if r_ not in ("pets.starter",) and not r_.startswith("pets.rarity") and not r_.startswith("pets.curve")]]
    D7 = "\n".join(old_lines)

    def cm(name, text, crlf=False):
        home = os.path.join(scratch, "cmig", name, "Skyy_SkyyPets")
        os.makedirs(home, exist_ok=True)
        data = text.replace("\n", "\r\n") if crlf else text
        if text is not None:
            open(os.path.join(home, "config.properties"), "wb").write(data.encode("latin-1"))
        return home
    hm = cm("default", D7)
    oldb = open(os.path.join(hm, "config.properties"), "rb").read()
    msg = str(Mig.run(Paths.get(hm)))
    newb = open(os.path.join(hm, "config.properties"), "rb").read()
    ol, nl_ = oldb.decode("latin-1").split("\n"), newb.decode("latin-1").split("\n")
    diff = [(a, b) for a, b in zip(ol, nl_) if a != b]
    K.check(len(ol) == len(nl_) and sorted(diff) == sorted([("%s=%s" % (k, o), "%s=%s" % (k, n)) for k, n, o in COMPAT[:8]]), "CMIG a 0.2.7 default file: exactly the 8 old-default lines changed: %s" % diff)
    hst = [f_ for f_ in os.listdir(os.path.join(hm, "config-history")) if f_.endswith(".bak")]
    K.check(len(hst) == 1 and open(os.path.join(hm, "config-history", hst[0]), "rb").read() == oldb, "CMIG config-history holds the old bytes first")
    chl = open(os.path.join(hm, "config-changes.log"), encoding="utf-8").read().splitlines()
    K.check(len(chl) == 8 and all("\tSkyWynn update 0.3.0\t-\tupdate\t" in l and l.endswith("\tok") for l in chl), "CMIG 8 config-changes.log lines (Server Setup -> Changes -> Undo)")
    K.check(os.path.exists(os.path.join(hm, "migrations", "pets-030.done")) and "pets.rarity.common 0.3 -> 1" in msg, "CMIG the marker + the log message")
    K.check(str(Mig.run(Paths.get(hm))) == "" and open(os.path.join(hm, "config.properties"), "rb").read() == newb, "CMIG a second start changes nothing")
    Cfg.load(Paths.get(os.path.dirname(hm)))
    K.check(abs(float(Cfg.F1) - 1.0) < 1e-9 and abs(float(Cfg.F6) - 1.5) < 1e-9 and abs(float(Cfg.CURVE_LIN) - 120.0) < 1e-9 and int(Cfg.LVL_CAP) == 50, "CMIG the updated file loads the new numbers")
    Cfg.load(Paths.get(mods))
    hm = cm("hand", D7.replace("pets.rarity.common=0.3", "pets.rarity.common=0.5").replace("pets.curve.linear=60", "pets.curve.linear = 60.0  ")
            .replace("pets.rarity.epic=0.8", "pets.rarity.epic=0.8\\\n  0"), crlf=True)
    oldb = open(os.path.join(hm, "config.properties"), "rb").read()
    msg = str(Mig.run(Paths.get(hm)))
    newt = open(os.path.join(hm, "config.properties"), "rb").read().decode("latin-1")
    K.check("pets.rarity.common=0.5\r\n" in newt and "pets.curve.linear = 120  \r\n" in newt and "pets.rarity.epic=0.8\\\r\n  0\r\n" in newt
            and "pets.rarity.rare=1.2\r\n" in newt and newt.count("\r\n") == oldb.decode("latin-1").count("\r\n") and "\n" not in newt.replace("\r\n", ""),
            "CMIG hand-edited common 0.5 + the continued epic line kept, '= 60.0  ' -> '= 120  ' (spaces kept), CRLF kept everywhere")
    K.check("kept hand-edited pets.rarity.common=0.5" in msg, "CMIG ... a hand edit is kept and noted")
    hm = cm("none", None)
    K.check("the 0.3.0 defaults apply" in str(Mig.run(Paths.get(hm))) and os.path.exists(os.path.join(hm, "migrations", "pets-030.done")), "CMIG no config file = the marker only")
    hm = cm("new", str(Cfg.DEFAULT_TEXT))
    oldb = open(os.path.join(hm, "config.properties"), "rb").read()
    K.check("nothing to change" in str(Mig.run(Paths.get(hm))) and open(os.path.join(hm, "config.properties"), "rb").read() == oldb, "CMIG a 0.3.0 file = nothing to change")
    hm = cm("blocked", D7)
    open(os.path.join(hm, "config-history"), "w").write("x")
    oldb = open(os.path.join(hm, "config.properties"), "rb").read()
    K.check(str(Mig.run(Paths.get(hm))) == "" and open(os.path.join(hm, "config.properties"), "rb").read() == oldb and not os.path.exists(os.path.join(hm, "migrations", "pets-030.done")),
            "CMIG config-history cannot be written = nothing rewritten, no marker (tried again next start)")
    rr = Mig.mgUpdate("a=1\npets.rarity.common=0.30\npets.rarity.common=0.45\n")
    K.check(int(rr[1]) == 0 and "kept hand-edited pets.rarity.common=0.45" in str(list(rr[2])), "CMIG the LAST entry decides (what Properties keeps)")
    K.check(not bool(Mig.sameAfter(b"pets.rarity.common=0.3\nx=1\n", b"pets.rarity.common=1\nx=2\n")) and bool(Mig.sameAfter(b"pets.rarity.common=0.3\n", b"pets.rarity.common=1\n")),
            "CMIG sameAfter: another key changing = refused")
    K.save()


# ======================================================================================================== HUB (the 0.2.7 phase, detail row 12)
def run_hub(out, jar, scratch, home):
    src = open(os.path.join(HERE, "test_skyypets_0.2.7.py"), encoding="utf-8").read()
    a = src.index("def run_hub(")
    b = src.index("\ndef run_snd(")
    body = src[a:b]
    assert body.count('"#SkyyPtD10V.Text"') == 1 and body.count("the 11 detail rows + Back") == 1
    body = body.replace('"#SkyyPtD10V.Text"', '"#SkyyPtD12V.Text"').replace("the 11 detail rows + Back", "the 13 detail rows (0.3.0) + Back")
    g = dict(T27.__dict__)
    g["PKG"] = PKG
    exec(compile(body, "run_hub(0.3.0)", "exec"), g)
    g["run_hub"](out, jar, scratch, home)


def run_snd(out, jar, scratch, home):
    T26 = T27.T26
    src = open(os.path.join(HERE, "test_skyypets_0.2.6.py"), encoding="utf-8").read()
    a = src.index("def run_snd(")
    b = src.index(chr(10) * 3, a)
    body = src[a:b]
    old = 'K.eq(str(bos.toString()).count("PetSnd.slotDone"), 3, "STATIC exactly 3 slotDone calls (to1, to2, out)")'
    assert body.count(old) == 1
    body = body.replace(old, 'K.eq(str(bos.toString()).count("PetSnd.slotDone"), 5, "STATIC exactly 5 slotDone calls (to1, to2, out + 0.3.0: Choose, Fuse / Rebirth)")')
    # fixer 2: since the 2026-10-15 server jar the FIRST SoundUtil call takes ~1 s in this stage (class init under -Xverify:all), longer
    # than the 500 ms gate, so "the gate holds a repeat" failed on the 0.2.7 jar too - one warm-up sound (another gate key) first
    gate_chk = '    K.check(bool(Snd.playTo(pa, SUMMON, "t")) and not bool(Snd.playTo(pa, SUMMON, "t"))'
    assert body.count(gate_chk) == 1
    body = body.replace(gate_chk, '    Snd.playTo(pa, SUMMON, "warm-up")\n    st.clear()\n' + gate_chk)
    g = dict(T26.__dict__)
    g["PKG"] = PKG
    exec(compile(body, "run_snd(0.3.0)", "exec"), g)
    g["run_snd"](out, jar, scratch, home)


# ======================================================================================================== LIVE: start twice on a copy
def tree(d):
    out = {}
    for r_, _ds, fs in os.walk(d):
        for f_ in fs:
            p = os.path.join(r_, f_)
            out[os.path.relpath(p, d)] = open(p, "rb").read()
    return out


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Mig, Log = P_("PetsCfg"), P_("PetStore"), P_("PetOps"), P_("PetsCfgMig"), P_("PetsLog")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    t0 = tree(home)
    oldcfg = props(os.path.join(home, "config.properties"))

    def start():
        Mig.run(Paths.get(home))
        Cfg.load(Paths.get(mods))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        sc = [int(x) for x in Store.scanAll()]
        fr = [int(x) for x in Store.fuseRecover()]
        return sc, fr
    sc1, fr1 = start()
    t1 = tree(home)
    ch = sorted(k for k in t1 if t0.get(k) != t1[k])
    newcfg = props(os.path.join(home, "config.properties"))
    exp = set(k for k, n, o in COMPAT[:8] if oldcfg.get(k) is not None and abs(float(oldcfg[k]) - float(o)) < 1e-9)
    chk = set(k for k in newcfg if newcfg.get(k) != oldcfg.get(k))
    K.check(chk == exp, "LIVE start 1: config.properties changed exactly the old-default lines %s (got %s)" % (sorted(exp), sorted(chk)))
    K.check(all(k == "config.properties" or k.startswith("config-history") or k == "config-changes.log" or k.startswith("migrations") for k in ch),
            "LIVE start 1 writes only the config update (+ its history / log / marker): %s" % ch)
    K.check(sc1[2] == 0 and sc1[3] == 0 and fr1[0] == 0, "LIVE the pet files read (files, pets, unreadable, dup %s), no cut-off fuse" % sc1)
    sc2, fr2 = start()
    t2 = tree(home)
    K.check(t2 == t1 and sc2 == sc1, "LIVE start 2 writes NOTHING")
    # the first tick of every record: the level update (marker only unless a pet is above Lv 50) + no starter for an existing profile
    keys = sorted(f_[:-11] for f_ in os.listdir(os.path.join(home, "pets")) if f_.endswith(".properties"))
    res = {}
    for k in keys:
        r = Store.get(k)
        res[k] = (str(Ops.migrateLevels(UUID(1, 1), r)), str(Ops.starterPending(r)), r.get("starter") is not None)
        Store.save(r)
    over = sum(1 for k in keys for i_ in Store.get(k).ids() if int(Store.get(k).levelOf(i_)) > 50 and int(Store.get(k).rebirthOf(i_)) == 0)
    K.check(over == 0 and all(v[1] == "False" for v in res.values()), "LIVE every record updated, no pet left above its max, no existing profile asked to choose: %s" % res)
    t3 = tree(home)
    for k in keys:
        Store.REC.remove(k)
    for k in keys:
        Ops.migrateLevels(UUID(1, 1), Store.get(k))
        Store.flushDirty()
    K.check(tree(home) == t3, "LIVE a second tick of every record writes nothing")
    K.save()


# ======================================================================================================== OLD (compat)
def run_old():
    sc = os.path.join(os.path.dirname(SCRATCH), "pets-old")
    p = subprocess.run([sys.executable, os.path.abspath(__file__), "--compat-child", os.path.join(HERE, "test_skyypets_0.2.5.py"), "--jar", JAR, "--old", OLD_JAR, "--dir", sc],
                       env=dict(os.environ), capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = p.stdout.splitlines()
    open(os.path.join(os.path.dirname(SCRATCH), "pets-old.log"), "w", encoding="utf-8").write(p.stdout + "\n" + p.stderr)
    oks = [l for l in lines if l.endswith("fail(s)") and " ok, " in l]
    failed = [l.strip()[len("FAILED: "):] for l in lines if l.strip().startswith("FAILED: ")]
    exp, bad = [], []
    for f in failed:
        (exp if [e for e in EXPECTED_OLD if f.startswith(e[0])] else bad).append(f)
    return oks, bad, exp, p.returncode


if __name__ == "__main__":
    if "--phase" not in sys.argv and "--no-old" not in sys.argv:
        oks, bad, exp, rc = run_old()
        print("OLD. the 0.2.5 harness on the 0.3.0 jar (compat numbers): %s; %d expected identity checks differ, %d other failure(s)" % (oks[-1:] or "no summary", len(exp), len(bad)))
        for e in exp:
            print("  note (old): expected on 0.3.0: %s" % e[:200])
        for b_ in bad:
            print("  OLD unexpected: %s" % b_[:400])
        HK.check(bool(oks), "OLD: the 0.2.5 harness ran to its summary")
        HK.check(not bad, "OLD: no failure outside the listed identity checks: %s" % bad[:5])
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("sys", run_sys), ("hub", run_hub), ("snd", run_snd), ("live", run_live)], script=__file__,
           live=(LIVE, "Skyy_SkyyPets"))
