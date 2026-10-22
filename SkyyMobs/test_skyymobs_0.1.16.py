"""Harness for SkyyMobs 0.1.16 (packprep: the pack mods' bosses / mini bosses / mobs / helpers into our ranks - tools/mobs_0_1_16_patch.py).
Build first:
    python tools/mobs_0_1_16_patch.py && python SkyyMobs/build_skyymobs_0.1.16.py
    python SkyyMobs/test_skyymobs_0.1.16.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S  static   the patch re-runs to identical bytes (--out), line endings kept, no new class / command / system
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.15 -> 0.1.16 (EXPECT below)
  P  pack     the role ids of the defaults against the REAL pack archives (scratch copies of Skyy's Mods folder: Soulslike_Bosses-1_3_7.zip,
              DungeonBosses-0.1.2.jar, StructureV2-0.1.7.jar): every boss / mini / helper id is a role file there; every 100,000 HP role is a
              helper; no helper is a boss; every SLB boss role (not a template) is listed as a boss, mini boss or helper
  X  exec     EXECUTES MobCfg on the defaults: every pack boss = mob:fn:boss (isBoss) + rank 3 at its fixed level (factors: rank.boss.base
              over its own base); the minis rank 2 (Abyss adds at 78, the Ice Magus at its band: whyNot null, no fixed level); the pack mobs
              band-levelled; every helper refused FIRST ("pack mod boss helper"), even under Extra mobs that get levels; a file scale.role line
              beats the pack level; empty rows = 0.1.15 (no boss, no level); a live edit through packEdit (new boss, the health signature
              changes); packPairs on bad levels; vanilla bosses / fighters unchanged; the default file carries the four rows
  D  live     start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyMobs (the migrations + MobCfg.load + MobSpoils.loadV3): 0.1.16
              writes nothing of its own, start 2 changes nothing; the live file (no pack lines) runs with the defaults
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): a boss phase role swap (P1 -> P2 / Disguise -> Conductor) keeping the level; their own drop tables.
Scratch: tools/dev/scratch/packprep/mobs (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, subprocess, hashlib, zipfile, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.1.16"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "packprep", "mobs")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyymobs_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyymobs_0.1.15.py")
PATCH = os.path.join(ROOT, "tools", "mobs_0_1_16_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMobs-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMobs-0.1.15.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PACK_DIR = os.path.abspath(os.environ.get("SKYY_PACK_DIR") or os.path.join(ROOT, "tools", "dev", "scratch", "packprep", "pack"))   # env SKYY_PACK_DIR: another scratch copy          # scratch COPIES of the pack mods (read-only source: Skyy's Mods folder)
PKG = "com.skyy.mobs."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMobs")
ADDED = []
EXPECT = {
    "MobCfg": ["+f PACK_BOSSES", "+f PACK_FIXED", "+f PACK_MINIS", "+f PACK_MOBS", "+f PACK_NEVER", "+f P_PNEVER", "+f ROLES_FILE", "+f ROLE_SIG_FILE",
               "+m packEdit", "+m packMerge", "+m packNames", "+m packPairs", "~<clinit>", "~m apply", "~m bossText", "~m bosses", "~m derive",
               "~m load", "~m reloadAll", "~m roles", "~m useDefaults", "~m whyNot"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"],
    "SkyyMobsPlugin": ["~m setup"],          # the version in the ready line
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
U = "00000000-0000-0000-0000-000000000116"
BOSSES = {"SLB_Goblin_Ogre_Boss": 18, "SLB_Frenzied_Bramblekin": 20, "SLB_Nightlord": 38, "SLB_Gravedigger": 40, "SLB_Gravedigger_Beast": 40, "SLB_Bishop": 42,
          "SLB_Bishop_Aerial": 42, "SLB_Rubeus_Beast": 44, "SLB_Conductor_Disguise": 45, "SLB_Conductor": 45, "SLB_Abyss_Watcher_Main": 78,
          "SLB_Ancient_Calamity_P1": 98, "SLB_Ancient_Calamity_P2": 98, "Sv2_CompositeBoss_Dormant": 20, "Sv2_CompositeBoss_P1": 20,
          "Sv2_CompositeBoss_P2": 20, "Sv2_CompositeBoss_P3": 20, "Sv2_Astral": 58}
MINIS = {"SLB_Abyss_Watcher_Hostile": 78, "SLB_Abyss_Watcher_Support": 78, "Sv2_Magic": 0}
HELPERS = ["SLB_Ancient_Calamity_Entombed", "SLB_Ancient_Calamity_Fake_Death", "SLB_Ancient_Calamity_Flame_Emitter", "SLB_Ancient_Calamity_Static_Flame",
           "SLB_Ancient_Calamity_Preview", "SLB_Conductor_Dying", "SLB_Conductor_Transforming", "SLB_Rubeus_Human", "Beast_Abomination_Ally",
           "Beast_Crawler_Ally", "Human_Beast_Ally", "Werewolf_Ally", "Sv2_Magic_Decoy"]
MOBS = ["Sv2_Bandit_Minion", "Sv2_Bandit_Minion_Aggressive", "Sv2_Bandit_Minion_Defensive", "Sv2_Bandit_Minion_Mixed", "Sv2_Ship_Archer", "Sv2_Ship_Cutthroat",
        "Sv2_Ship_Grenadier", "Sv2_Ship_Raider", "Sv2_Ship_Spearman"]


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyMobs 0.1.16 - build script') and g.count('VERSION = "0.1.16"') == 1, "S header + VERSION")
    K.eq((g.count("registerSystem(") - o.count("registerSystem("), g.count("registerCommand(") - o.count("registerCommand("),
          g.count("makeClass(") - o.count("makeClass(")), (0, 0, 0), "S no new system, command or class")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


def run_pack(out, jar, scratch, home):
    K = HK.Child(out)
    roles, hp = {}, {}
    for f in ("Soulslike_Bosses-1_3_7.zip", "DungeonBosses-0.1.2.jar", "StructureV2-0.1.7.jar"):
        p = os.path.join(PACK_DIR, f)
        if not os.path.isfile(p):
            K.check(False, "P the scratch copy %s is missing (copy it from Skyy's Mods folder into %s)" % (f, PACK_DIR))
            continue
        z = zipfile.ZipFile(p)
        for n in z.namelist():
            if "/NPC/Roles/" in n and n.endswith(".json"):
                r = n.rsplit("/", 1)[1][:-5]
                roles[r] = f
                m = re.search(r'"MaxHealth"\s*:\s*([0-9.]+)', z.read(n).decode("utf-8", "replace"))
                if m:
                    hp[r] = float(m.group(1))
    for r in list(BOSSES) + list(MINIS) + HELPERS:
        K.check(r in roles, "P %s is a role of %s" % (r, roles.get(r, "NO pack mod")))
    big = sorted(r for r, h in hp.items() if h >= 100000 and r.startswith("SLB_"))
    K.check(all(r in HELPERS for r in big), "P every 100,000 HP SLB role is a helper: %s" % big)
    K.check(not set(HELPERS) & set(BOSSES) and not set(HELPERS) & set(MINIS), "P no helper is a boss / mini boss")
    slb = sorted(r for r, f in roles.items() if f.startswith("Soulslike") and r.startswith("SLB_") and "Template" not in r)
    left = [r for r in slb if r not in BOSSES and r not in MINIS and r not in HELPERS]
    K.eq(left, [], "P every Souls like Bosses boss role is a boss, a mini boss or a helper (%d roles)" % len(slb))
    sv2 = sorted(r for r, f in roles.items() if r.startswith("Sv2_") and "Template" not in r and not r.startswith("Component"))
    K.eq(sorted(r for r in sv2 if r not in BOSSES and r not in MINIS and r not in HELPERS and r not in MOBS), ["Sv2_Local_Trader"],
         "P every StructureV2 / DungeonBosses role is placed (the trader stays unlevelled: *Trader* guard)")
    K.save()


def run_exec(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    C = JClass(PKG + "MobCfg")
    uu = JClass("java.util.UUID").fromString(U)
    C.useDefaults()
    d = str(C.DEF_CFG)
    for k in ("rank.pack.bosses=", "rank.pack.minis=", "rank.pack.mobs=", "rank.pack.never="):
        K.check(("\n" + k) in d, "X the default file carries %s" % k)
    for r, lv in BOSSES.items():
        K.check(bool(C.isBoss(r)) and int(C.roleLevel(r)) == lv and int(C.rankOf(r, uu, False)) == 3 and C.whyNotRole("HOSTILE", r) is None,
                "X %s: boss (mob:fn:boss), fixed Lv %d, rank boss" % (r, lv))
    f = C.factors("SLB_Nightlord", uu, 2500.0, False)
    K.check(abs(float(f[0]) - 4500.0 / 2500.0) < 1e-9 and abs(float(f[1]) - float(C.RANK_BOSS_DMG)) < 1e-9 and int(f[2]) == 3,
            "X the Nightlord's 2500 base -> rank.boss.base 4500 (x%.2f Health, x%s damage)" % (float(f[0]), f[1]))
    for r, lv in MINIS.items():
        K.check(not bool(C.isBoss(r)) and int(C.rankOf(r, uu, False)) == 2 and int(C.roleLevel(r)) == lv and C.whyNot("HOSTILE", r) is None,
                "X %s: mini boss, %s" % (r, ("fixed Lv %d" % lv) if lv else "band level"))
    for r in MOBS:
        K.check(C.whyNot("HOSTILE", r) is None and not bool(C.isBoss(r)) and int(C.rankOf(r, uu, False)) == 0, "X %s gets a band level, no rank" % r)
    for r in HELPERS:
        w = C.whyNotRole("HOSTILE", r)
        K.check(w is not None and "pack mod boss helper" in str(w) and not bool(C.isBoss(r)) and int(C.roleLevel(r)) == 0, "X helper %s never levelled: %s" % (r, w))
    K.check(C.whyNot("HOSTILE", "Henchman") is not None and C.whyNot("HOSTILE", "Sv2_Local_Trader") is not None, "X Henchman (instances) + the trader stay unlevelled")
    K.check(bool(C.isBoss("Goblin_Duke")) and int(C.roleLevel("Dragon_Fire")) == 98 and C.whyNot("HOSTILE", "Trork_Warrior") is None and not bool(C.isBoss("Trork_Warrior")),
            "X the vanilla bosses / fighters unchanged")
    K.check("pack bosses" in str(C.bossText()), "X bossText: %s" % C.bossText())
    Props = JClass("java.util.Properties")

    def apply_(extra):
        c = C.props(C.DEF_CFG)
        for k, v in extra.items():
            c.setProperty(k, v)
        C.apply(c, C.props(C.DEF_BANDS))
    apply_({"scale.role.SLB_Nightlord": "50,1,1", "levels.roles": "SLB_Ancient_*"})
    K.eq(int(C.roleLevel("SLB_Nightlord")), 50, "X a file scale.role line beats the pack level")
    K.check(C.whyNotRole("HOSTILE", "SLB_Ancient_Calamity_Flame_Emitter") is not None and C.whyNot("HOSTILE", "SLB_Ancient_Calamity_P1") is None,
            "X a helper stays refused even when Extra mobs that get levels matches it")
    apply_({"rank.pack.bosses": "", "rank.pack.minis": "", "rank.pack.mobs": "", "rank.pack.never": ""})
    K.check(not any(bool(C.isBoss(r)) for r in BOSSES if r != "SLB_Goblin_Ogre_Boss") and all(int(C.roleLevel(r)) == 0 for r in BOSSES)
            and all(int(C.rankOf(r, uu, False)) != 2 for r in MINIS) and all(C.whyNot("HOSTILE", r) is not None for r in MOBS),
            "X empty rows = 0.1.15 (no pack boss / level; the Ogre still matches the old *_Boss* boss pattern)")
    C.useDefaults()
    sig0 = str(C.HP_SIG)
    C.PACK_BOSSES = "SLB_Test_Boss_X=33, Sv2_Test_Y"
    C.packEdit(None)
    K.check(int(C.roleLevel("SLB_Test_Boss_X")) == 33 and bool(C.isBoss("SLB_Test_Boss_X")) and bool(C.isBoss("Sv2_Test_Y")) and int(C.roleLevel("Sv2_Test_Y")) == 0
            and str(C.HP_SIG) != sig0 and not bool(C.isBoss("SLB_Nightlord")), "X a live Server Setup edit (packEdit): the new list in force at once, the health signature changes")
    pp = C.packPairs("A=0, B=abc, C=150, D=5, =7, E")
    K.eq(([str(x) for x in pp[0]], [int(x) for x in pp[1]]), (["A", "B", "C", "D", "E"], [0, 0, 0, 5, 0]), "X packPairs: a bad level = band level (WARN), an empty role skipped")
    K.eq(str(C.packNames(" X=4 ,Y ")), "X,Y", "X packNames")
    C.useDefaults()
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([jar, B.SERVER_JAR], verify=True)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    Cfg, S = JClass(PKG + "MobCfg"), JClass(PKG + "MobSpoils")
    P = JClass("java.nio.file.Paths")
    txt = open(os.path.join(home, "config.properties"), encoding="latin-1").read()

    def start():
        Cfg.DIR = P.get(home)
        Cfg.FILE = P.get(os.path.join(home, "config.properties"))
        Cfg.BANDS = P.get(os.path.join(home, "bands.properties"))
        o = [str(JClass(PKG + m).run(P.get(home))) for m in ("MobMig", "MobMig14", "MobMig11", "MobMig12", "MobMigP4")]
        Cfg.load()
        o.append(str(S.loadV3(P.get(home))))
        return o
    h0 = tree_hash(home)
    o1 = start()
    h1 = tree_hash(home)
    ch = sorted(k for k in set(h0) | set(h1) if h0.get(k) != h1.get(k))
    K.check(set(ch) <= {"trees.properties"}, "D start 1 on a scratch COPY of the live data: 0.1.16 writes nothing of its own (%s; %s)" % (ch, [x[:60] for x in o1 if x]))
    o2 = start()
    K.check(tree_hash(home) == h1 and all(x == "" for x in o2[:-1]), "D start 2 changes nothing")
    if "rank.pack." not in txt:
        K.check(bool(Cfg.isBoss("SLB_Nightlord")) and int(Cfg.roleLevel("Sv2_CompositeBoss_P1")) == 20, "D the live file (no pack lines) runs with the pack defaults")
    K.save()


HK.run("SkyyMobs", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("pack", run_pack), ("exec", run_exec), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyMobs"))
