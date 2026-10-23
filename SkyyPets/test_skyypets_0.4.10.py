"""Harness for SkyyPets 0.4.10 (elem1: one element per pet kind -> element damage % + element Defence on pets:stats; tools/pets_0_4_10_patch.py).
Build first:
    python tools/pets_0_4_10_patch.py && python SkyyPets/build_skyypets_0.4.10.py
    python SkyyPets/test_skyypets_0.4.10.py [--keep]

  S     static   the patch re-runs to identical bytes; no new class / system / command; line endings kept
  A/C/AA          (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.9 -> 0.4.10, engine-access audit
  EL    EXECUTED on real pet records: PetBuff.compute2 + publish -> pets:stats:<uuid> carries fFire / dFire for a Fox (Fire) at rarity x level /
                 100 x slot strength (1 % / 15 at Lv 100 Common, the summon slot at its percent), a pet with no element none; the pets.element
                 parser (aliases, none, bad entries skipped + the check= hook), a live edit (a new element at once), pets.elemDmg / elemDef 0
                 = no line; the card text "Element: Fire - its damage counts with a Fire weapon"; SkyyGear's own reader (GearStats.parsePets
                 rules: sum per key, floored) gives the key SkyyGear 0.3.39 gates
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyPets: nothing written by 0.4.10, every pet file reads, the element rows at their defaults
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "elem1", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_s44 = importlib.util.spec_from_file_location("test_skyypets_0_4_4", os.path.join(HERE, "test_skyypets_0.4.4.py"))
T44 = importlib.util.module_from_spec(_s44)
_s44.loader.exec_module(T44)
T41 = T44.T41
HK.run_compare = _cmp0

VERSION = "0.4.10"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.9.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.9.py")
PATCH = os.path.join(TOOLS, "pets_0_4_10_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T44.PKG = PKG
EXPECT = {
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "PetBuff": ["~m addPet", "~m compute", "~m compute2", "~m petText"], "PetKind": ["~<clinit>"], "PetTick": ["~<clinit>"],          # compute / petText: the inlined stat count N (19 -> 29)
    "PetsMigP5": ["~m mgLog", "~m run"], "SkyyPetsPlugin": ["~m setup"],          # the version text
    "PetsCfg": ["+f ELEMS", "+f ELEM_DEF", "+f ELEM_DMG", "+f ELEM_MAP", "+f ELEM_NAMES", "+f ELEM_TXT", "+m checkElem", "+m elemOf", "+m elemParse",
                "+m elemWord", "~<clinit>", "~m applyAll", "~m applyScalars", "~m seed"],          # applyAll / seed: the fresh file text
    "PetsPage": ["~m buffsAt", "~m tip"],          # buffsAt: the inlined N
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.10 - build script') and g.count('VERSION = "0.4.10"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "= cls("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def _pet(r, pid, kind, rar, lvl, slot=None):
    for kk, vv in (("kind", kind), ("rarity", str(rar)), ("level", str(lvl))):
        r.set("pet.%s.%s" % (pid, kk), vv)
    if slot:
        r.set("active.%d" % slot, pid)


def run_el(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "el")
    K, JClass = W["K"], W["JClass"]
    P_ = lambda n: JClass(PKG + n)
    Buff, Cfg, Kind = P_("PetBuff"), P_("PetsCfg"), P_("PetKind")
    BR = W["BR"]
    keys = [str(x) for x in Kind.STAT_KEYS]
    K.check(all(k in keys for k in ("fEarth", "fThunder", "fWater", "fFire", "fAir", "dEarth", "dThunder", "dWater", "dFire", "dAir")), "EL the ten element keys are pet stats")
    K.check(all(str(Kind.STAT_HOW[keys.index(k)]) == "gear" for k in ("fFire", "dFire")), "EL delivered on pets:stats (gear)")

    def stats(u_, r_):
        t = list(Buff.compute2(u_, r_, "w"))
        return dict((keys[i], float(t[i])) for i in range(len(t)) if abs(float(t[i])) > 1e-9)
    u, k, r = T44._mk(W, 9301)
    _pet(r, "f1", "Fox", 1, 100, slot=1)
    s = stats(u, r)
    K.check(abs(s.get("fFire", 0) - 1.0) < 1e-9 and abs(s.get("dFire", 0) - 15.0) < 1e-9 and not any(k_ in s for k_ in ("fWater", "dWater", "fEarth")),
            "EL a Common Lv 100 Fox (Fire) = +1 %% Fire damage, +15 Fire Defence, nothing else elemental: %s" % dict((a, b) for a, b in s.items() if a[0] in "fd" and a[1].isupper()))
    _pet(r, "f1", "Fox", 3, 50, slot=1)
    fac = float(Cfg.factor(3))
    s = stats(u, r)
    K.check(abs(s.get("fFire", 0) - 1.0 * fac * 0.5) < 1e-9 and abs(s.get("dFire", 0) - 15.0 * fac * 0.5) < 1e-9, "EL rarity x level / 100: Rare Lv 50 = 1 x %.2f x 0.5" % fac)
    Buff.publish(u, Buff.compute2(u, r, "w"))
    m = BR.get("pets:stats:" + str(u))
    K.check(m is not None and abs(float(m.get("fFire")) - 1.0 * fac * 0.5) < 1e-9 and abs(float(m.get("dFire")) - 15.0 * fac * 0.5) < 1e-9,
            "EL pets:stats:<uuid> carries fFire / dFire (SkyyGear reads them)")
    u2, k2, r2 = T44._mk(W, 9302)
    _pet(r2, "c1", "Chicken", 1, 100, slot=1)
    s2 = stats(u2, r2)
    K.check(not any(k_[0] in "fd" and k_[1:] in ("Earth", "Thunder", "Water", "Fire", "Air") for k_ in s2), "EL a pet with no element (Chicken) gives none")
    K.eq([str(Cfg.elemOf(x)) if Cfg.elemOf(x) is not None else None for x in ("Wolf", "skrill", "VoidEye", "Rabbit", "Nope", None)],
         ["Air", "Thunder", "Thunder", None, None, None], "EL pets.element defaults (any case; none / unknown kind = no element)")
    Cfg.ELEMS = "Chicken=Lightning, Fox=wind, Rabbit=none, Wolf=Ice, Bad, =Fire"
    K.eq([str(Cfg.elemOf(x)) if Cfg.elemOf(x) is not None else None for x in ("Chicken", "Fox", "Rabbit", "Wolf")], ["Thunder", "Air", None, None],
         "EL a live edit: aliases Lightning / Wind, none, bad entries skipped")
    s2 = stats(u2, r2)
    K.check(abs(s2.get("fThunder", 0) - 1.0) < 1e-9 and abs(s2.get("dThunder", 0) - 15.0) < 1e-9, "EL ... the Chicken now gives Thunder at once")
    K.check(Cfg.checkElem("pets.element", "Wolf=Ice") is not None and Cfg.checkElem("pets.element", "Wolf") is not None
            and Cfg.checkElem("pets.element", "Wolf=Air, Fox=none") is None and Cfg.checkElem("pets.element", None) is None, "EL the check= hook")
    Cfg.ELEM_DMG, Cfg.ELEM_DEF = 0.0, 0.0
    s2 = stats(u2, r2)
    K.check("fThunder" not in s2 and "dThunder" not in s2, "EL pets.elemDmg / elemDef 0 = no element lines")
    Cfg.ELEM_DMG, Cfg.ELEM_DEF = 1.0, 15.0
    # the summon slot at its percent (a summonable kind: Camel = Fire)
    Cfg.ELEMS = str(Cfg.ELEMS) + ", Camel=Fire"
    u3, k3, r3 = T44._mk(W, 9303)
    _pet(r3, "c2", "Camel", 2, 100, slot=2)
    r3.set("unlocked", "1")
    Cfg.SLOT2_MODE = "always"
    s3 = stats(u3, r3)
    K.check(abs(s3.get("fFire", 0) - 1.0 * float(Cfg.factor(2)) * float(Cfg.SLOT2_PCT) / 100.0) < 1e-9, "EL the summon slot at %d %%: %s" % (int(Cfg.SLOT2_PCT), s3.get("fFire")))
    tip = str(P_("PetsPage").tip(r, "f1", 0))
    K.check('<color is="#c8f5ee">Element: Air</color> - its damage counts with Air weapons' in tip or '<color is="#ff6a3d">Element: Fire</color> - its damage counts with Fire weapons' in tip,
            "EL the card's hover text names the element in its colour (elem1fix, Style Guide 15): %s" % [l for l in tip.split("\n") if "Element" in l])
    K.check("% Air Damage (Air weapon)" in tip or "% Fire Damage (Fire weapon)" in tip, "EL Buffs now lists the element damage line")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Mig, Mig2, MgP5, Log = P_("PetsCfg"), P_("PetStore"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("PetsMigP5"), P_("PetsLog")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    t0 = T41.tree(home)

    def start():
        Mig.run(Paths.get(home))
        Mig2.run(Paths.get(home))
        r = str(MgP5.run(Paths.get(home)))
        Cfg.load(Paths.get(mods))
        v = str(Cfg.loadV3(Paths.get(home)))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return r, v, [int(x) for x in Store.scanAll()]
    r1, v1, sc1 = start()
    t1 = T41.tree(home)
    K.check(r1 == "" or "Balance P5 power (SkyyPets 0.4.8)" in r1, "LIVE start 1: only 0.4.8's own P5 update may run (%s)" % ("ran" if r1 else "already done"))
    K.check(sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k) and not k.startswith(("config-history", "migrations", "config.properties", "config-changes"))) == []
            or r1 != "", "LIVE 0.4.10 writes nothing of its own")
    K.check(sc1[2] == 0 and sc1[3] == 0, "LIVE every pet file reads (%s)" % sc1)
    txt = open(os.path.join(home, "config.properties"), encoding="latin-1").read() if os.path.isfile(os.path.join(home, "config.properties")) else ""
    if "pets.element" not in txt:
        K.check(str(Cfg.elemOf("Fox")) == "Fire" and abs(float(Cfg.ELEM_DMG) - 1.0) < 1e-9 and abs(float(Cfg.ELEM_DEF) - 15.0) < 1e-9, "LIVE the element rows at their defaults")
    r2, v2, sc2 = start()
    K.check(r2 == "" and T41.tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("static", run_static), ("el", run_el), ("live", run_live)],
           script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
