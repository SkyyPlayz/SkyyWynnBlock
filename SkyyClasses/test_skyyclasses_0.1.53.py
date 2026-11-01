"""Harness for SkyyClasses 0.1.53 (lean round katana: the vanilla Katana is a Warrior weapon; tools/classes_0_1_53_patch.py). Build first:
    python tools/classes_0_1_53_patch.py && python SkyyClasses/build_skyyclasses_0.1.53.py
    python SkyyClasses/test_skyyclasses_0.1.53.py [--keep] [--expect-dump]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; no new class / system / command; line endings kept; the jar has the same file names as
                 0.1.52; the only non-class change = the manifest (server.lang + every item / effect JSON byte for byte)
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.1.52 -> 0.1.53 (EXPECT below: ClassDefs' static tables + the version strings)
  K     katana   EXECUTES the new rule in the 0.1.53 jar: ClassDefs.rule / ownerOf / nounOf / prefixesOf / WTEXT on every vanilla Weapon_Longsword_*
                 (Assets.zip, read only) + The Armory / SkyyArmory ids; the bridge lists class:weapons:<Class> exactly as setup() publishes them and
                 SkyyGear's / SkyyMerchants' longest-prefix reading of them (Katana -> Warrior, other longswords -> Spellblade);
                 ClassRules.allowed + AllowedFn.apply + blockText for a Warrior / Spellblade / classless player (profile:class:<uuid>)
  K0    katana0  the same calls on the 0.1.52 jar: there the Katana is still the Spellblade's (the change is real, not a harness artefact)
  X46 / W46 / W47 / X48 / ALT / SM / W50 / EL / BR / W  the 0.1.52 harness's EXEC + WIRE phases on the 0.1.53 jar (unchanged behaviour)
  LIVE  start twice on a scratch COPY of Skyy's live Skyy_SkyyClasses
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): a real Katana hit in game (the DamageLock reads the hand item id - the same ownerOf call exercised here);
SkyyArmory's Crescent Rush / sword guard ride every vanilla longsword incl. the Katana (SkyyArmory's own files, not this jar).
Scratch: tools/dev/scratch/katana/cls (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, json, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "katana", "cls")]
import harness_kit as HK
import skyybuild as B

_ORIG_COMPARE0 = HK.run_compare
_s = importlib.util.spec_from_file_location("test_skyyclasses_0_1_52", os.path.join(HERE, "test_skyyclasses_0.1.52.py"))
T52 = importlib.util.module_from_spec(_s)
_argv = list(sys.argv)
_s.loader.exec_module(T52)
sys.argv[:] = _argv
HK.run_compare = _ORIG_COMPARE0          # 0.1.52's compare drops server.lang; 0.1.53 changes no lang line (the static phase proves it byte for byte)
T51, T50, T48 = T52.T51, T52.T50, T52.T48

VERSION, OLD = "0.1.53", "0.1.52"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyClasses-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyClasses-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyclasses_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyclasses_%s.py" % OLD)
PATCH = os.path.join(TOOLS, "classes_0_1_53_patch.py")
PKG = "com.skyy.classes."
SCRATCH = os.path.abspath(HK.arg("--dir"))
T51.GEN = GEN          # the 0.1.51 wire phase reads the generated script: read THIS one
KATANA = "Weapon_Longsword_Katana"
WARRIOR, SPELLBLADE = 1, 7
EXPECT = {   # checked 2026-11-01 (--expect-dump, 0.1.52 -> 0.1.53): ClassDefs' tables (static init: R_PREFIX / R_OWNER / R_NOUN / WTEXT) + the version strings
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~m header'],
    'ClassDefs': ['~<clinit>'],
    'KitMigrate': ['~m runOnce'],
    'SkyyClassesPlugin': ['~m setup'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyClasses 0.1.53 - build script') and g.count('VERSION = "0.1.53"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem("), g.count("registerCommand("), g.count("makeClass(")), (o.count("registerSystem("), o.count("registerCommand("), o.count("makeClass(")),
         "S no new class / system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    na, nb = set(za.namelist()), set(zb.namelist())
    K.eq((sorted(nb - na), sorted(na - nb)), ([], []), "S the jar has exactly the 0.1.52 file names")
    K.eq(sorted(n for n in na & nb if not n.endswith(".class") and za.read(n) != zb.read(n)), ["manifest.json"],
         "S the only non-class change: the manifest (server.lang + every item / effect JSON byte for byte)")
    m = json.loads(zb.read("manifest.json").decode("utf-8-sig"))
    K.eq(m.get("Version"), VERSION, "S manifest version")
    # the generated script: exactly one Katana rule, Warrior's, and the Warrior weapon text
    K.eq(g.count('("Weapon_Shield_", "shields"), ("Weapon_Longsword_Katana", "katanas")],'), 1, "S one Katana rule row (in the Warrior's weapons)")
    K.eq(len(re.findall(r'"weapons": \[[^\n]*Weapon_Longsword_Katana', g)), 1, "S the Katana in exactly one class's weapons")
    K.check('"weapon_text": "Swords / Spears / Shields / Katana"' in g and '"weapon_text": "Swords / Spears / Shields",' not in g, "S Warrior weapon text")
    K.save()


def _katana_calls(K, jar, tag, want_owner, want_noun, want_wtext):
    """the rule calls on one jar (the JVM is this child's own)"""
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    UUID = JClass("java.util.UUID")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    D = JClass(PKG + "ClassDefs")
    R = JClass(PKG + "ClassRules")
    AF = JClass(PKG + "AllowedFn")
    names = [str(x) for x in D.NAMES]
    K.eq((names[WARRIOR], names[SPELLBLADE]), ("Warrior", "Spellblade"), "%s class slots" % tag)
    az = zipfile.ZipFile(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
    ls = sorted(os.path.basename(n)[:-5] for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json")
                and os.path.basename(n).startswith("Weapon_Longsword_"))
    K.check(KATANA in ls and len(ls) >= 19, "%s Assets.zip has the Katana among %d longswords" % (tag, len(ls)))
    # 1. ClassDefs on every vanilla longsword
    K.eq((int(D.ownerOf(KATANA)), str(D.nounOf(KATANA))), (want_owner, want_noun), "%s ownerOf / nounOf(Katana)" % tag)
    other = [(i, int(D.ownerOf(i)), str(D.nounOf(i))) for i in ls if i != KATANA]
    K.eq([x for x in other if x[1:] != (SPELLBLADE, "longswords")], [], "%s every other vanilla longsword stays Spellblade (%d)" % (tag, len(other)))
    for i, o in (("Longsword_Iron_Red", SPELLBLADE), ("Zweihander", SPELLBLADE), ("Weapon_Elemental_Flame", SPELLBLADE), ("Weapon_GreatShield_Iron", SPELLBLADE),
                 ("Weapon_Sword_Iron", WARRIOR), ("Weapon_Spear_Iron", WARRIOR), ("Weapon_Shield_Wood", WARRIOR), ("Weapon_Longsword_Katana_X", want_owner)):
        K.eq(int(D.ownerOf(i)), o, "%s ownerOf(%s)" % (tag, i))
    r = int(D.rule(KATANA))
    K.eq(str(D.R_PREFIX[r]), KATANA if want_owner == WARRIOR else "Weapon_Longsword_", "%s rule(Katana) = its prefix" % tag)
    K.eq(str(D.WTEXT[WARRIOR]), want_wtext, "%s WTEXT Warrior" % tag)
    # 2. the bridge exactly as setup() publishes it + the other mods' longest-prefix reading (SkyyGear GearView.classReq, SkyyMerchants ownerOf)
    for i in range(len(names)):
        br.put("class:weapons:" + names[i], D.prefixesOf(i))
    br.put("class:weapons:free", D.prefixesOf(D.FREE))
    br.put("class:weapons:unassigned", D.prefixesOf(D.UNASSIGNED))
    pw = str(br.get("class:weapons:Warrior")).split(",")
    ps = str(br.get("class:weapons:Spellblade")).split(",")
    K.eq(KATANA in pw, want_owner == WARRIOR, "%s class:weapons:Warrior lists the Katana: %s" % (tag, pw))
    K.check(KATANA not in ps and "Weapon_Longsword_" in ps, "%s class:weapons:Spellblade keeps Weapon_Longsword_ only: %s" % (tag, ps))

    def longest(iid):
        best, bl = None, 0
        for n in names + ["free", "unassigned"]:
            for p in str(br.get("class:weapons:" + n) or "").split(","):
                if p and iid.startswith(p) and len(p) > bl:
                    best, bl = n, len(p)
        return best
    K.eq(longest(KATANA), names[want_owner], "%s other mods' longest-prefix reading: Katana" % tag)
    K.eq(sorted(set(longest(i) for i in ls if i != KATANA)), ["Spellblade"], "%s other mods' reading: the other longswords" % tag)
    # 3. ClassRules.allowed / AllowedFn / blockText for a Warrior, a Spellblade and a classless player
    uw, us, un = UUID.fromString("00000000-0000-0000-0000-00000000aa01"), UUID.fromString("00000000-0000-0000-0000-00000000aa02"), UUID.fromString("00000000-0000-0000-0000-00000000aa03")
    br.put("profile:class:" + str(uw), "Warrior")
    br.put("profile:class:" + str(us), "Spellblade")
    W_ = want_owner == WARRIOR
    K.eq([bool(R.allowed(uw, KATANA)), bool(R.allowed(us, KATANA))], [W_, not W_], "%s allowed(Katana): Warrior, Spellblade" % tag)
    K.eq([bool(R.allowed(uw, "Weapon_Longsword_Iron")), bool(R.allowed(us, "Weapon_Longsword_Iron")), bool(R.allowed(uw, "Weapon_Sword_Iron"))],
         [False, True, True], "%s allowed: iron longsword (Warrior, Spellblade), iron sword (Warrior)" % tag)
    JObjA = JClass("java.lang.Object")[:]
    K.eq(bool(AF().apply(JObjA([uw, KATANA]))), W_, "%s class:fn:allowed {Warrior, Katana}" % tag)
    K.eq(bool(AF().apply(JObjA([us, KATANA]))), not W_, "%s class:fn:allowed {Spellblade, Katana}" % tag)
    bt = str(R.blockText(us if W_ else uw, KATANA, False))
    want_bt = ("Only Warriors can use katanas. You are a Spellblade - your weapons: Longswords / Zweihander / Great Shields." if W_ else
               "Only Spellblades can use longswords. You are a Warrior - your weapons: " + want_wtext + ".")
    K.eq(bt, want_bt, "%s blockText (the wrong class holding the Katana)" % tag)
    K.check(bool(R.allowed(un, KATANA)) is True, "%s classless player (requireClass off): the Katana works" % tag)
    K.notes.append("%s: Katana -> %s (%s); %d other longswords -> Spellblade; blockText %r" % (tag, names[int(D.ownerOf(KATANA))], str(D.nounOf(KATANA)), len(other), bt))


def run_katana(out, jar, scratch, _home):
    K = HK.Child(out)
    _katana_calls(K, jar, "K", WARRIOR, "katanas", "Swords / Spears / Shields / Katana")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_katana0(out, jar, scratch, _home):
    K = HK.Child(out)
    _katana_calls(K, OLD_JAR, "K0", SPELLBLADE, "longswords", "Swords / Spears / Shields")
    K.save()
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    HK.run(name="SkyyClasses", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("katana", run_katana), ("katana0", run_katana0),
                   ("exec46", T48.run_exec46), ("wire46", T48.run_wire46), ("wire47", T48.run_wire47), ("exec48", T48.run_exec),
                   ("alt", T50.run_alt), ("sm", T50.run_exec), ("wire50", T50.run_wire), ("elem", T51.run_elem), ("wire", T51.run_wire), ("live", T48.run_live)],
           script=__file__, live=(T48.LIVE_DIR, "Skyy_SkyyClasses"))
