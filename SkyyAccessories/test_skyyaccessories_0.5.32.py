"""Harness for SkyyAccessories 0.5.32 (elem1: the five single-element charm lines + Prism - tools/accessories_0_5_32_patch.py). Build first:
    python tools/accessories_0_5_32_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.32.py
    python SkyyAccessories/test_skyyaccessories_0.5.32.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; no new system / command; line endings kept
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.31 -> 0.5.32 (EXPECT below); non-class files: the 36 new item files + server.lang + manifest.json only
  EL    EXECUTED on the real AccDefs / AccGear / AccCfg: the 16 lines (the old 10 at their indexes), the element BOOST ladders, statParts
        ("+4% Fire damage, +13 Fire Defence"; Prism "+3% every element"), bestTiers on the new ids, gear:extra (textOf2) carries
        fFire / dFire / rElem next to the old keys (SkyyGear 0.3.39 reads them), line switches, combatToGear off = nothing, boostIn / checkBoost
        on an element entry, isBoosterId / tierOf / rarityOf for T1..T6, the item files (quality, recipe chain, no Normal recipe = drop only),
        the tooltips (lang: the stat line first, the weapon rule)
  MIG   0.5.30's migrateP5 text step still moves exactly the 14 old entries (the new ones are never touched)
  LIVE  START TWICE on a scratch COPY of the live Skyy_SkyyAccessories: the loader adds only the new element keys (boost.<Element>.*, the
        line switches - its usual pure addition), no other value changes, start 2 changes nothing
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the charms' vanilla crystal looks in the Void Charms grid, the drop-up Craft rows (AccCraft) for the new
lines with one in the bag (the same code path as Strength / Crit).
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B
import skyyonce_harness as OH

_argv = list(sys.argv)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "elem1", "acc")]
_sp = importlib.util.spec_from_file_location("test_skyyaccessories_0_5_30", os.path.join(HERE, "test_skyyaccessories_0.5.30.py"))
T530 = importlib.util.module_from_spec(_sp)
_orig_compare = HK.run_compare
_sp.loader.exec_module(T530)
HK.run_compare = _orig_compare
SCRATCH = os.path.abspath(HK.arg("--dir"))
sys.argv = _argv

VERSION, OLD = "0.5.32", "0.5.31"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyaccessories_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "accessories_0_5_32_patch.py")
PKG = T530.PKG
ELINES = ["Earth", "Thunder", "Water", "Fire", "Air", "Prism"]
NEW_IDS = ["Skyy_Talisman_%s_T%d" % (f, t) for f in ELINES for t in range(1, 7)]
HK.run_compare = OH.compare_allowing(lambda n: n == "Server/Languages/en-US/server.lang" or any(n == "Server/Item/Items/Utility/%s.json" % i for i in NEW_IDS))
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"], "SkyyAccessoriesPlugin": ["~m setup"],
          "AccDefs": ["+f LINE_AIR", "+f LINE_EARTH", "+f LINE_FIRE", "+f LINE_PRISM", "+f LINE_THUNDER", "+f LINE_WATER", "~<clinit>", "~m bonusRows", "~m lineOn", "~m statParts"],
          "AccGear": ["~m pageRows"], "AccPower": ["~<clinit>"],          # bonusRows / pageRows: the inlined BONUS_MAX 12 -> 18; AccPower: the GEAR_KEYS / E_GEAR tables it copies
          "AccCfg": ["~<clinit>", "~m load", "~m writeDefaults"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAccessories 0.5.32 - build script') and g.count('VERSION = "0.5.32"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_el(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    D, Cfg, Gear = JClass(PKG + "AccDefs"), JClass(PKG + "AccCfg"), JClass(PKG + "AccGear")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    S = lambda *ids: JArray(JString)([JString(i) for i in ids])
    fam = [str(x) for x in D.FAMILIES]
    K.eq(fam, ["Vitality", "Endurance", "Intelligence", "Regeneration", "Speed", "Strength", "MagicPower", "Defense", "Crit", "Feather"] + ELINES,
         "EL 16 lines, the old 10 at their indexes")
    ek = [str(x) for x in D.E_KEYS]
    bo = [float(x) for x in D.BOOST]
    lad = lambda k: [round(bo[ek.index(k) * 7 + t], 4) for t in range(1, 7)]
    K.check(all(lad(n + ".dmgPct") == [1, 1, 2, 2, 3, 3] and lad(n + ".defence") == [3, 5, 7, 9, 11, 13] for n in ELINES[:5]) and lad("Prism.allPct") == [1, 1, 1, 2, 2, 2],
            "EL the ladders: weak -> powerful (Skyy) - damage 1..3 %, Defence 3..13, Prism 1..2 % (elem1fix: fitted to the P5 split)")
    K.eq(str(D.LINE_NAME[int(D.lineOf("Prism"))]), "Elemental", "EL elem1fix: players see <Rarity> Elemental Accessory + the tooltip Elemental Power (admin word Prism)")
    K.eq(ek[:14], ["Health.pct", "Stamina.flat", "Stamina.regenPct", "Mana.pct", "Mana.floor", "Regeneration.pct", "Speed.pct", "Strength.flat",
                   "MagicPower.flat", "Defense.flat", "Crit.chancePct", "Crit.damagePct", "Feather.fallPct", "Feather.jumpPct"], "EL the 14 old entries keep their indexes")
    lf, lp = int(D.lineOf("Fire")), int(D.lineOf("Prism"))
    K.eq([str(x) for x in D.statParts(lf, 6)], ["+3% Fire damage, +13 Fire Defence"], "EL statParts Mythic Fire")
    K.eq([str(x) for x in D.statParts(lf, 1)], ["+1% Fire damage, +3 Fire Defence"], "EL statParts Normal Fire")
    K.eq([str(x) for x in D.statParts(lp, 6)], ["+2% every element"], "EL statParts Mythic Prism")
    best = [int(x) for x in D.bestTiers(S("Skyy_Talisman_Fire_T6", "Skyy_Talisman_Fire_T2", "Skyy_Talisman_Water_T3", "Skyy_Talisman_Prism_T4", "Skyy_Talisman_Crit_T6"))]
    K.check(best[lf] == 6 and best[int(D.lineOf("Water"))] == 3 and best[lp] == 4, "EL bestTiers on the element ids: %s" % best)
    txt = str(Gear.textOf2(JArray(JClass("int"))(best), None))
    K.eq(dict(x.split(":") for x in txt.split(",")), {"cc": "8", "cd": "16", "fFire": "3", "dFire": "13", "fWater": "2", "dWater": "7", "rElem": "2"},
         "EL gear:extra carries the element keys SkyyGear 0.3.39 reads (%s)" % txt)
    K.check(all(int(D.tierOf("Skyy_Talisman_%s_T%d" % (f, t))) == t and int(D.rarityOf("Skyy_Talisman_%s_T%d" % (f, t))) == t and bool(D.isBoosterId("Skyy_Talisman_%s_T%d" % (f, t)))
                for f in ELINES for t in range(1, 7)), "EL tierOf / rarityOf / isBoosterId on the 36 new ids")
    K.eq(str(D.DISPLAY[int(D.rarityOf("Skyy_Talisman_Thunder_T5"))]), "Fabled", "EL T5 = Fabled")
    e_f = ek.index("Fire.dmgPct")
    K.eq([float(x) for x in Cfg.boostIn("2,3,4,5,6,7", e_f)], [2, 3, 4, 5, 6, 7], "EL boostIn on an element entry")
    K.check(Cfg.checkBoost("boost[Fire.dmgPct]", "1,2,3,4,5,6") is None and Cfg.checkBoost("boost[Fire.dmgPct]", "1,2,3") is not None, "EL checkBoost on an element entry")
    K.check(bool(D.lineOn(lf)) and "Skyy_Talisman_Fire_T6" in str(D.defsText()), "EL line switch on + acc:defs lists the new ids")
    D.COMBAT_TO_GEAR = False
    K.eq(str(Gear.textOf2(JArray(JClass("int"))(best), None)), "", "EL combatToGear off = the element lines send nothing")
    D.COMBAT_TO_GEAR = True
    # the item files + texts
    z = zipfile.ZipFile(jar)
    lang = z.read("Server/Languages/en-US/server.lang").decode("utf-8")
    for f in ELINES:
        for t in range(1, 7):
            iid = "Skyy_Talisman_%s_T%d" % (f, t)
            n = json.loads(z.read("Server/Item/Items/Utility/%s.json" % iid))
            ok = n["Quality"] == "Skyy_Acc_" + ["", "Normal", "Unique", "Rare", "Legendary", "Fabled", "Mythic"][t]
            ok = ok and (("Recipe" not in n) if t == 1 else (n["Recipe"]["Input"][0]["ItemId"] == "Skyy_Talisman_%s_T%d" % (f, t - 1)))
            K.check(ok, "EL %s: quality + %s" % (iid, "no recipe (drop only)" if t == 1 else "the upgrade chain"))
    nm = [l for l in lang.split("\n") if l.startswith("items.Skyy_Talisman_Fire_T6.")]
    K.check(any("=Mythic Fire Accessory" in l for l in nm) and any("+3% Fire damage" in l and "+13 Fire Defence" in l and "added to every hit you land" in l and "weapon deals" not in l for l in nm),
            "EL the Mythic Fire name + tooltip (stat line first; elem1fix: no weapon rule - charms count with any weapon): %s" % [l[:160] for l in nm])
    import skyyelem as ELX
    for f in ELX.NAMES:          # elem1fix2: each element charm's values in its element colour (Style Guide 15)
        d = [l for l in lang.split("\n") if l.startswith("items.Skyy_Talisman_%s_T3.description=" % f)]
        K.check(len(d) == 1 and d[0].count('<color is="%s">' % ELX.COLORS[f]) == 2 and "#7ee08a" not in d[0].split("while in your Void Charms.")[0],
                "EL elem1fix2: %s charm damage + Defence values in %s" % (f, ELX.COLORS[f]))
    K.check(any(l.startswith("items.Skyy_Talisman_Prism_T1.description=") and "every element" in l and "Elemental Power" in l for l in lang.split("\n")), "EL the Prism tooltip (elem1fix: names Elemental Power)")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Paths = JClass("java.nio.file.Paths")
    J = lambda n: JClass(PKG + n)
    fc, fp = os.path.join(home, "config.properties"), os.path.join(home, "power.properties")
    c0 = open(fc, "rb").read() if os.path.isfile(fc) else b""

    def start():
        J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
        J("AccCfg").FILE = Paths.get(fc)
        for m in ("migrate051", "migrate055", "migrate0518"):
            getattr(J("AccCfg"), m)()
        a = str(J("AccCfg").migrateP5(J("AccCfg").FILE, False))
        J("AccCfg").load(True)
        J("AccPower").FILE = Paths.get(fp)
        J("AccPower").DIR = Paths.get(os.path.join(home, "power"))
        b = str(J("AccCfg").migrateP5(J("AccPower").FILE, True))
        J("AccPower").load()
        return a, b
    a1, b1 = start()
    c1 = open(fc, "rb").read()
    po, pn = T530._props(c0), T530._props(c1)
    ch = sorted(k for k in set(po) | set(pn) if po.get(k) != pn.get(k))
    p5 = [k for k in ch if k.startswith("boost.") and k.split(".")[1] not in ELINES and k != "boost.Health.pct"]
    newk = [k for k in ch if k.split(".")[1] in ELINES or k in ("line." + f for f in ELINES)]
    other = [k for k in ch if k not in p5 and k not in newk and k != "boost.Health.pct"]
    K.notes.append("LIVE start 1: P5 update %r; keys changed %d (new element keys %d, 0.5.30's own P5 moves %d)" % (a1[:80], len(ch), len(newk), len(p5)))
    K.check(not other, "LIVE start 1: only the new element keys (and 0.5.30's own P5 update if it had not run) change: %s" % other[:6])
    K.check(all(k in pn for k in ["boost.%s.dmgPct" % f for f in ELINES[:5]] + ["boost.Prism.allPct"]) or not newk, "LIVE the element rows are read / added at their defaults")
    D = J("AccDefs")
    ek = [str(x) for x in D.E_KEYS]
    K.check(abs(float(D.BOOST[ek.index("Fire.dmgPct") * 7 + 6]) - 3.0) < 1e-6, "LIVE the loader reads the element ladders (elem1fix: Mythic 3 %)")
    h1 = T530.tree_hash(home)
    a2, b2 = start()
    K.check(a2 == "" and b2 == "" and T530.tree_hash(home) == h1, "LIVE start 2 changes nothing")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("el", run_el), ("mig", T530.run_mig), ("live", run_live)],
           script=__file__, live=(T530.LIVE_DIR, "Skyy_SkyyAccessories"))
