"""Harness for SkyyPets 0.4.14 (THE PET TOOLTIP: research/Pet-Tooltip-Layout.md + the D4 dragon icons; tools/pets_0_4_14_patch.py). Build first:
    python tools/pets_0_4_14_patch.py && python SkyyPets/build_skyypets_0.4.14.py
    python SkyyPets/test_skyypets_0.4.14.py [--keep] [--expect-dump]

  S     static   the patch re-runs to identical bytes; no new class / system / command; line endings kept; the jar: no new entry, the only
                 changed non-class entries = manifest.json + the 8 dragon icons, byte for byte = art/dragons (manifest sha256); no Void icon,
                 no file for Aures' Dragon_Egg_Plain / Dragon_Egg_Tundra; the old footer #ffff55 gone from the classes
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.13 -> 0.4.14, engine-access audit
  T     EXECUTED PetsPage.tip() on real records: a BONUS pet (Rat), a BONUS class pet (Boar: "Class", never "Combat"), a FIGHTER (Wolf), a MOUNT
                 (Horse), FIGHTER + MOUNT (Ram), a dragon below / at the ride level (riding on / off), a reborn dragon, an unknown + a switched-off
                 kind, summon mode (cannot = grey), the slot line; per tip: the type line + its colours, the section order, one stat per line, the
                 footer #ffcc00 then the dim Owned line last, only <color is="#rrggbb"> spans (no other markup), every colour from the set,
                 every line <= 45 visible characters; the Hatchery fuse grid's type line; the internal skill id stays "Combat"
  R/M/F/DG/VW/ST/EL410  0.4.13's / 0.4.12's / 0.4.11's / 0.4.10's phases EXECUTED on this jar (their old tooltip-text checks moved to the
                 new layout or to PetDragon.card, which is unchanged)
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyPets (0.4.11's live phase): nothing written
NOT COVERED (UNVERIFIED in game): several <color> spans on one line in an ItemGridSlot description, double spaces kept, the wrap width, the
tooltip height of a dragon card at high GUI scale, the new icons' look in the inventory / Pets page.
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, hashlib, importlib.util, subprocess, inspect

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "pets0414fix", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_s413 = importlib.util.spec_from_file_location("test_skyypets_0_4_13", os.path.join(HERE, "test_skyypets_0.4.13.py"))
T413 = importlib.util.module_from_spec(_s413)
_s413.loader.exec_module(T413)
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T412, T411, T410, T44, T41 = T413.T412, T413.T411, T413.T410, T413.T44, T413.T41

VERSION = "0.4.14"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.13.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.13.py")
PATCH = os.path.join(TOOLS, "pets_0_4_14_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
for _m in (T413, T412, T411, T410, T44):
    _m.PKG = PKG
for _m in (T413, T412, T411):
    _m.JAR, _m.OLD_JAR = JAR, OLD_JAR
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "PetsCfg": ["~m applyAll", "~m seed"], "PetsMigP5": ["~m mgLog", "~m run"],   # the VERSION text
    "PetHatchery": ["~m eggCell", "~m petCell"],          # eggCell: the footer #ffcc00 (TIP_FOOT1)
    "PetOps": ["+m tcol", "+m tmount", "+m tskill", "+m typeLine"],
    "PetsPage": ["+m atArr", "+m buffArr", "+m ecol", "+m progress", "+m sec", "+m statLines", "+m summonPart", "+m tc", "~m build", "~m tip"],          # build: the Class filter button
    "SkyyPetsPlugin": ["~m setup"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
ART = os.path.join(ROOT, "art", "dragons")
ICONS = (["Common/Icons/ItemsGenerated/Skyy_PetIcon_Dragon%s.png" % k for k in ("Plain", "Tundra", "Fire", "Storm", "Sky")]
         + ["Common/Icons/ItemsGenerated/Skyy_PetEgg_Dragon_%s.png" % e for e in ("Fire", "Thunder", "Air")])
C_FIGHT, C_MOUNT, C_BONUS, C_SOFT, C_DIM, C_SEC = "#e8554a", "#4fc3d9", "#b7cedd", "#d6e4ee", "#7f93a6", "#9aacbc"
C_GOLD, C_GREEN, C_RED, C_OK, C_FOOT, C_GREY = "#e8c25a", "#7ee08a", "#ff7a7a", "#39f493", "#ffcc00", "#797b7c"
ELEMS = ["#5dbb4a", "#ffd84d", "#4fa8ff", "#ff6a3d", "#c8f5ee"]
RAR = ["#c9d2dd", "#3e9049", "#2770b7", "#8b339e", "#bb8a2c", "#CC66CC"]
ALLOWED = set(x.lower() for x in [C_FIGHT, C_MOUNT, C_BONUS, C_SOFT, C_DIM, C_SEC, C_GOLD, C_GREEN, C_RED, C_OK, C_FOOT, C_GREY] + ELEMS)
ORDER = ["BUFFS NOW", "FIGHTING (SUMMON SLOT)", "RIDING", "AT LV", "SUMMON SLOT", "PROGRESS", "ABILITIES"]
SPAN = re.compile(r'<color is="(#[0-9a-fA-F]{6})">([^<]*)</color>')


def _eq(self, got, want, what):
    """the C compare: the non-class entries that changed = manifest.json + the 8 dragon icons"""
    if what == "C: non-class entries changed" and want == ["manifest.json"]:
        return self.check(sorted(got) == sorted(["manifest.json"] + ICONS), "C: non-class entries changed = manifest.json + the 8 dragon icons: %s" % sorted(got))
    return _eq00(self, got, want, what)


HK.Child.eq = _eq


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.14 - build script') and g.count('VERSION = "0.4.14"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem(") and g.count("= cls(") == o.count("= cls("),
            "S no new class, system or command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    z, oz = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(z.namelist()) ^ set(oz.namelist())), [], "S no entry added or removed")
    ch = sorted(n for n in set(z.namelist()) & set(oz.namelist()) if not n.endswith(".class") and not n.endswith("/") and z.read(n) != oz.read(n))
    K.eq(ch, sorted(["manifest.json"] + ICONS), "S the changed non-class entries = manifest.json + the 8 dragon icons")
    man = json.load(open(os.path.join(ART, "manifest.json"), encoding="utf8"))
    sha = dict((f["path"], f["sha256"]) for f in man["files"] if "sha256" in f)
    K.check(all(hashlib.sha256(z.read(p)).hexdigest() == sha[p] == hashlib.sha256(open(os.path.join(ART, *p.split("/")), "rb").read()).hexdigest() for p in ICONS),
            "S the 8 icons = art/dragons byte for byte (manifest sha256)")
    names = z.namelist()
    K.check(not [n for n in names if "Void" in n and "Dragon" in n] and not [n for n in names if "Dragon_Egg_Plain" in n or "Dragon_Egg_Tundra" in n],
            "S no Void dragon icon, no file for Aures' Dragon_Egg_Plain / Dragon_Egg_Tundra")
    for n in ("PetsPage", "PetHatchery", "PetOps"):
        b = z.read("com/skyy/pets/%s.class" % n)
        K.check(b"#ffff55" not in b, "S %s: the old footer #ffff55 is gone" % n)
    K.check(b"#ffcc00" in z.read("com/skyy/pets/PetsPage.class") and b"#ffcc00" in z.read("com/skyy/pets/PetHatchery.class"), "S the footer #ffcc00 in PetsPage + PetHatchery")
    pc = z.read("com/skyy/pets/PetsPage.class")
    K.check(b'Text: "Combat"' not in pc and pc.count(b'Text: "Class"') >= 1 and b'Text: "Combat"' in oz.read("com/skyy/pets/PetsPage.class"),
            "S the area filter button says Class, not Combat (Skyy: since when did we also have combat?)")
    K.check("Colour-coded pet tooltips." in json.dumps(json.loads(z.read("manifest.json"))), "S the manifest text")
    K.save()


# ======================================================================================================== T: the tooltip, EXECUTED
def _lines(tip):
    return tip.split("\n")


def _vis(line):
    return SPAN.sub(lambda m: m.group(2), line)


def _shape(K, tip, what, longok=False):
    """markup + colours + line length + footer order for one tooltip"""
    ls = _lines(tip)
    bad = [l for l in ls if "<" in SPAN.sub("", l) or ">" in SPAN.sub("", l).replace("->", "")]
    K.check(not bad and "<b>" not in tip and "<i>" not in tip, "T %s: only <color is=#rrggbb> spans, nothing else: %s" % (what, bad[:3]))
    cols = set(m.group(1).lower() for m in SPAN.finditer(tip)) - set(c.lower() for c in RAR)
    K.check(cols <= ALLOWED, "T %s: every colour from the one code: %s" % (what, sorted(cols - ALLOWED)))
    lng = [_vis(l) for l in ls if len(_vis(l)) > 45]
    K.check(longok or not lng, "T %s: every line <= 45 characters: %s" % (what, lng))
    K.check(ls[-1].startswith('<color is="%s">Owned ' % C_DIM) and " - id " in ls[-1], "T %s: the dim Owned line at the very bottom: %r" % (what, ls[-1]))
    foot = [l for l in ls if l.startswith('<color is="%s">' % C_FOOT) or l.startswith('<color is="%s">Click' % C_GREY) or l.startswith('<color is="%s">Cannot' % C_GREY)
            or l.startswith('<color is="%s">The summon' % C_GREY)]
    K.check(len(foot) == 1 and ls.index(foot[0]) >= len(ls) - 3, "T %s: one click hint, last before the minor lines: %s" % (what, foot))
    K.check("\n\n\n" not in tip and not ls[0].startswith("\n"), "T %s: one blank line between sections" % what)
    return ls


def _secs(tip):
    hs = []
    for l in _lines(tip):
        m = SPAN.fullmatch(l)
        if m and m.group(1).lower() == C_SEC:
            hs.append(m.group(2))
    return hs


def _order_ok(hs):
    idx = []
    for h in hs:
        k = [i for i, o in enumerate(ORDER) if h.startswith(o)]
        if not k:
            return False
        idx.append(k[0] if not h.startswith("SUMMON SLOT") else ORDER.index("SUMMON SLOT"))
    return idx == sorted(idx)


def run_t(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "t")
    K, JClass = W["K"], W["JClass"]
    P_ = lambda n: JClass(PKG + n)
    Cfg, Ops, Page, Kind, Hy, Rd = P_("PetsCfg"), P_("PetOps"), P_("PetsPage"), P_("PetKind"), P_("PetHatchery"), P_("PetRide")
    u, k, r = T44._mk(W, 9501)
    r.set("slot2.unlocked", "true")
    mk = lambda kd, ra, lv, reb=0: str(Ops.createR(r, None, kd, ra, lv, 0, reb, "test", "harness", False))
    tl = lambda t: _lines(t)[0]
    col = lambda c, t: '<color is="%s">%s</color>' % (c, t)
    # ---- BONUS (Rat, Exploration)
    rat = mk("Rat", 1, 1)
    t = str(Page.tip(r, rat, 0))
    _shape(K, t, "Rat")
    K.eq(tl(t), col(C_BONUS, "BONUS") + col(C_DIM, " - ") + col(C_SOFT, "Exploration"), "T Rat: the type line BONUS - Exploration")
    K.check(_lines(t)[1].startswith(col(RAR[0], "Common Rat") + "  " + col(C_GOLD, "Lv 1") + "  " + '<color is="%s">rarity bonus x' % C_DIM), "T Rat: name (rarity colour) + Lv (gold) + rarity bonus (dim): %r" % _lines(t)[1])
    hs = _secs(t)
    K.eq(hs, ["BUFFS NOW", "AT LV 50 (MAX FOR NOW)", "SUMMON SLOT", "PROGRESS", "ABILITIES"], "T Rat: the sections in order (no FIGHTING / RIDING)")
    K.check(col(C_DIM, "Not for summoning (Fighters and Mounts only)") in t and col(C_DIM, "None yet") in t, "T Rat: not for summoning + Abilities none yet")
    K.check(col(C_FOOT, "Click: put it in your pet slot") in t or col(C_FOOT, "Click: take it out of your pet slot") in t, "T Rat: the click hint in #ffcc00: %s" % _lines(t)[-2])
    stat = [l for l in _lines(t) if l.startswith('<color is="%s">+' % C_GREEN)]
    K.check(len(stat) >= 4 and all(re.fullmatch(r'<color is="%s">\+[0-9.]+</color> <color is="%s">[^<]+</color>' % (C_GREEN, C_SOFT), l) for l in stat),
            "T Rat: one '+value Stat' per line (value green, name soft white): %s" % stat[:2])
    K.check(col(C_SOFT, "Levels from Exploration") in t and (col(C_SOFT, "Level ") + col(C_GOLD, "1 / 50")) in t, "T Rat: PROGRESS levels + the skill")
    t1 = str(Page.tip(r, rat, 1))
    K.check(col(C_GREY, "Cannot be summoned (pet slot only) - only Mounts and Fighters") in t1 and tl(t1) == tl(t), "T Rat in summon mode: the hint grey, layout unchanged")
    # ---- BONUS class pet (Boar: skill id Combat -> "Class")
    boar = mk("Boar", 2, 10)
    t = str(Page.tip(r, boar, 0))
    _shape(K, t, "Boar")
    K.eq(tl(t), col(C_BONUS, "BONUS") + col(C_DIM, " - ") + col(C_SOFT, "Class"), "T Boar: BONUS - Class (Skyy: class IS the combat skill)")
    K.check("Combat" not in t and col(C_SOFT, "Levels from Class") in t, "T Boar: the word Combat never shows; Levels from Class")
    K.check(str(Cfg.kind("Boar").skill) == "Combat" and bool(Kind.skillMatch("Combat", "Combat.Warrior")), "T the internal skill id stays Combat (pet XP + saved data unchanged)")
    # ---- FIGHTER (Wolf)
    wolf = mk("Wolf", 3, 24)
    t = str(Page.tip(r, wolf, 0))
    _shape(K, t, "Wolf")
    K.eq(tl(t), col(C_FIGHT, "FIGHTER") + col(C_DIM, " - ") + col(C_SOFT, "Class"), "T Wolf: FIGHTER - Class in red")
    hs = _secs(t)
    K.eq(hs, ["BUFFS NOW (PET SLOT)", "FIGHTING (SUMMON SLOT)", "AT LV 50 (MAX FOR NOW)", "PROGRESS", "ABILITIES"], "T Wolf: the sections in order")
    K.check((col(C_SOFT, "Buffs at ") + col(C_GREEN, "%d%%" % int(Cfg.SLOT2_PCT)) + col(C_SOFT, " in the summon slot")) in t and col(C_DIM, "Only dragons attack for now") in t,
            "T Wolf: summon buffs at the row's % + honest 'only dragons attack' (no made-up bite number)")
    K.check("Bites for" not in t and _order_ok(hs), "T Wolf: no dragon bite line")
    # ---- MOUNT (Horse)
    horse = mk("Horse", 2, 5)
    t = str(Page.tip(r, horse, 0))
    _shape(K, t, "Horse")
    K.eq(tl(t), col(C_MOUNT, "MOUNT") + col(C_DIM, " - ") + col(C_SOFT, "Exploration"), "T Horse: MOUNT - Exploration in cyan")
    K.eq(_secs(t), ["BUFFS NOW (PET SLOT)", "RIDING", "AT LV 50 (MAX FOR NOW)", "SUMMON SLOT", "PROGRESS", "ABILITIES"], "T Horse: the sections in order")
    K.check(col(C_SOFT, "F on it in the summon slot") in t and col(C_DIM, "Ground only") in t and "in the summon slot" in t, "T Horse: riding lines + its summon buffs")
    Cfg.MOUNT_RIDE = False
    K.check(col(C_DIM, "Riding is off on this server.") in str(Page.tip(r, horse, 0)), "T Horse: Ride mount pets off -> the RIDING line says so")
    Cfg.reloadAll()
    # ---- FIGHTER + MOUNT (Ram)
    ram = mk("Ram", 4, 30)
    t = str(Page.tip(r, ram, 0))
    _shape(K, t, "Ram")
    K.eq(tl(t), col(C_FIGHT, "FIGHTER") + col(C_DIM, " + ") + col(C_MOUNT, "MOUNT"), "T Ram: FIGHTER + MOUNT (red + dim + cyan)")
    K.eq(_secs(t), ["BUFFS NOW (PET SLOT)", "FIGHTING (SUMMON SLOT)", "RIDING", "AT LV 50 (MAX FOR NOW)", "PROGRESS", "ABILITIES"], "T Ram: both sections, in order")
    # ---- the slot line
    r.set("active.1", wolf)
    t = str(Page.tip(r, wolf, 0))
    ls = _lines(t)
    K.check(col(C_SOFT, "In your pet slot (full buffs)") in ls and ls.index(col(C_SOFT, "In your pet slot (full buffs)")) == len(ls) - 3
            and col(C_FOOT, "Click: take it out of your pet slot") == ls[-2], "T a slotted pet: the slot line right above the click hint")
    r.set("active.1", "")
    # ---- unknown + switched off
    r.set("pet.%s.kind" % boar, "NoSuchKind")
    t = str(Page.tip(r, boar, 0))
    _shape(K, t, "unknown", longok=True)          # an unknown kind's made-up name may be long
    K.check(tl(t) == col(C_RED, "UNKNOWN") and col(C_RED, "Unknown pet kind - gives nothing") == _lines(t)[2] and "BUFFS NOW" not in t, "T unknown kind: UNKNOWN + the reason at the top, no buffs")
    r.set("pet.%s.kind" % boar, "Boar")
    Cfg.KINDS_OFF = "Wolf"
    t = str(Page.tip(r, wolf, 0))
    _shape(K, t, "off")
    K.check(tl(t) == col(C_RED, "OFF") and col(C_RED, "Switched off by the server - gives nothing") == _lines(t)[2] and "FIGHTING" not in t, "T switched-off kind: OFF + the reason, no sections")
    Cfg.reloadAll()
    # ---- dragons: below / at the ride level, riding off, reborn
    u2, k2, r2 = T44._mk(W, 9502)
    dg = str(Ops.createR(r2, None, "DragonFire", 3, 5, 0, 0, "test", "harness", False))
    K.check(not dg.startswith("-"), "T (a Fire Dragon Lv 5: %s)" % dg)
    t = str(Page.tip(r2, dg, 0))
    _shape(K, t, "dragon Lv 5")
    rl = int(Rd.rideLevel())
    K.eq(tl(t), col(C_FIGHT, "FIGHTER") + col(C_DIM, " - ") + col(C_SOFT, "Class"), "T dragon below Lv %d: FIGHTER - Class" % rl)
    K.check(col("#ff6a3d", "Fire") + col(C_DIM, " - its damage counts with Fire weapons") == _lines(t)[2], "T dragon: the element line in Fire orange: %r" % _lines(t)[2])
    K.check(_lines(t)[3].startswith('<color is="%s">Smalling, size x' % C_SOFT) and _lines(t)[3].endswith(col(C_DIM, " - Biteling at Lv %d" % int(P_("PetDragon").stageLv()[1]))), "T dragon: the stage line: %r" % _lines(t)[3])
    K.eq(_secs(t), ["BUFFS NOW (PET SLOT)", "FIGHTING (SUMMON SLOT)", "RIDING", "AT LV 50 (MAX FOR NOW)", "PROGRESS", "ABILITIES"], "T dragon: the sections in order")
    K.check((col(C_SOFT, "Ride it from Lv ") + col(C_GOLD, str(rl)) + "  " + col(C_RED, "locked")) in t and "Jump to" not in t, "T dragon below the ride level: locked (red)")
    K.check(col(C_SOFT, "Bites for ") in t and col(C_SOFT, "Health ") in t and col(C_DIM, "Shows only in the summon slot") in t and "Fights when" not in t, "T dragon: the fight lines")
    K.check(col(C_DIM, "One dragon per profile.") == _lines(t)[-2] and col(C_DIM, "No fusing (one dragon per profile)") in t, "T dragon: the minor block + no fusing")
    r2.set("pet.%s.level" % dg, str(rl + 2))
    t = str(Page.tip(r2, dg, 0))
    _shape(K, t, "dragon ridable")
    K.eq(tl(t), col(C_FIGHT, "FIGHTER") + col(C_DIM, " + ") + col(C_MOUNT, "MOUNT"), "T dragon at Lv %d: FIGHTER + MOUNT" % (rl + 2))
    K.check((col(C_SOFT, "Ride it from Lv ") + col(C_GOLD, str(rl)) + "  " + col(C_OK, "unlocked")) in t and col(C_SOFT, "Jump to take off and fly") in t
            and col(C_SOFT, "Fights when you are not riding it") in t, "T dragon: unlocked (green), fly line, fights when not ridden")
    Cfg.DRAGON_RIDE_MODE = "glide"
    K.check(col(C_SOFT, "Jump to glide") in str(Page.tip(r2, dg, 0)), "T dragon: glide mode line")
    Cfg.DRAGON_RIDE = False
    t = str(Page.tip(r2, dg, 0))
    K.check(tl(t) == col(C_FIGHT, "FIGHTER") + col(C_DIM, " - ") + col(C_SOFT, "Class") and col(C_DIM, "Riding is off on this server.") in t, "T dragon riding off: FIGHTER only + the line")
    Cfg.reloadAll()
    r2.set("pet.%s.level" % dg, "3")
    r2.set("pet.%s.rebirth" % dg, "1")
    K.eq(tl(str(Page.tip(r2, dg, 0))), col(C_FIGHT, "FIGHTER") + col(C_DIM, " + ") + col(C_MOUNT, "MOUNT"), "T a reborn dragon counts as Lv 100 (PetRide.levelOf): FIGHTER + MOUNT")
    # ---- the Hatchery fuse grid: the same type line on top (petCell needs the engine's item store: the source line + the bytecode reference)
    gsrc = open(GEN, encoding="utf8").read()
    K.check('g.setDescription(@PKG@.PetOps.typeLine(r.kindOf(id), @PKG@.PetRide.levelOf(r, id)) + "\\n" + "You own "' in gsrc
            and b"typeLine" in zipfile.ZipFile(jar).read("com/skyy/pets/PetHatchery.class"), "T the Hatchery fuse grid: the type line on top")
    K.check(str(Ops.typeLine("Horse", 1)) == col(C_MOUNT, "MOUNT") + col(C_DIM, " - ") + col(C_SOFT, "Exploration") and str(Ops.tskill("Combat.Warrior")) == "Class"
            and str(Ops.tskill("Mining")) == "Mining" and str(Ops.tskill(None)) == "-", "T typeLine / tskill direct")
    K.save()


# ======================================================================================================== reused phases, their tooltip checks moved
def _swap(fn, mod, pairs, allow_many=()):
    src = inspect.getsource(fn)
    for a, b in pairs:
        n = src.count(a)
        assert n == 1 or (a in allow_many and n >= 1), (fn.__name__, a, n)
        src = src.replace(a, b)
    ns = dict(mod.__dict__)
    exec(compile(src, mod.__file__, "exec"), ns)
    return ns[fn.__name__]


def run_r(out, jar, scratch, home):
    f = _swap(T413.run_r, T413, [('''"Ride it: F on it in the summon slot - jump to take off and fly." in tip and CARD_OLD not in tip''',
                                  ''''<color is="#d6e4ee">Jump to take off and fly</color>' in tip and tip.split(chr(10))[0].endswith('<color is="#4fc3d9">MOUNT</color>') and CARD_OLD not in tip''')])
    f(out, jar, scratch, home)


def run_f(out, jar, scratch, home):
    f = _swap(T412.run_f, T412, [('''"Fights next to you in the summon slot: bites for 2.3 %" in tip and "Riding and flying come in a later version." in tip and "Fighting, riding" not in tip''',
                                  ''''<color is="#d6e4ee">Bites for </color><color is="#7ee08a">2.3 %</color>' in tip and '<color is="#d6e4ee">Jump to take off and fly</color>' in tip and "Fighting, riding" not in tip''')])
    f(out, jar, scratch, home)


def run_dg(out, jar, scratch, home):
    f = _swap(T411.run_dg, T411, [("Page.tip(r, pid, 0)", "Dg.card(r, pid)"),
                                  ('''and "Fighting, riding and flying come in a later version." in tip and "Element: Earth</color>" in tip''',
                                   '''and "Ride it from Lv 10 (F on it in the summon slot)." in tip and "Fights next to you in the summon slot: bites for 0.1 %" in tip and '<color is="#5dbb4a">Earth</color>' in str(Page.tip(r, pid, 0))''')],
              allow_many=("Page.tip(r, pid, 0)",))
    f(out, jar, scratch, home)


def run_st(out, jar, scratch, home):
    f = _swap(T411.run_st, T411, [('''"Dragon: Weakling" in desc(cell)''', ''''<color is="#d6e4ee">Weakling, size x' in desc(cell) and "FIGHTER" in desc(cell)''')])
    f(out, jar, scratch, home)


def run_el(out, jar, scratch, home):
    f = _swap(T410.run_el, T410, [('''\'<color is="#c8f5ee">Element: Air</color> - its damage counts with Air weapons\' in tip or \'<color is="#ff6a3d">Element: Fire</color> - its damage counts with Fire weapons\' in tip''',
                                   '''\'<color is="#c8f5ee">Air</color><color is="#7f93a6"> - its damage counts with Air weapons</color>\' in tip or \'<color is="#ff6a3d">Fire</color><color is="#7f93a6"> - its damage counts with Fire weapons</color>\' in tip''')])
    f(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("t", run_t), ("r", run_r), ("m", T412.run_m), ("f", run_f), ("dg", run_dg), ("vw", T411.run_vw), ("st", run_st),
                   ("el410", run_el), ("live", T411.run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
