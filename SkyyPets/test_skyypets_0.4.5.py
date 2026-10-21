"""Harness for SkyyPets 0.4.5 (Skill Trees 3 R3b: the pet rows of the skill trees; tools/pets_0_4_5_patch.py, tools/trees_v3_effects.py).
Build first: python tools/pets_0_4_5_patch.py; python SkyyPets/build_skyypets_0.4.5.py

    python SkyyPets/test_skyypets_0.4.5.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.4.4 -> 0.4.5 (exactly the planned members +
              the new PetV3), engine-access audit
  V3          EXECUTED: a fake SkyyTrees tree:fn:level answers the ranks; PetTick.second (the real per-second path: compute2 -> publish) on a
              scratch record with real pets - rank 0 = exactly 0.4.4's bridge entries (nothing added); rank N = per x N x the pet's RARITY
              BONUS (PetsCfg.factor, x1 .. x1.5; fixer 2026-10-20), never above the row's ceiling, in
              the "pets" skill:bonus source (xp.mining / dd.mining / xp.smithing ...) and pets:stats dmg; a pet of another skill / an off kind
              / pets OFF / a no-buff world = nothing; the summon slot pet counts by its tier; Mining Pet Synergy = the Mining pet's own stats
              x (1 + 4 % x rank) under the caps; ranks are clamped to the upgrade's max; a bad answer (string, exception) = 0;
              tree:reads:SkyyPets = the 9 keys, removed at shutdown only while it is ours
  CFG         (fixer) the Server Setup numbers: PetsCfg.V3P<i> / V3X<i> change the live value; loadV3 seeds trees.properties (= the table's
              cfg_text) and reads hand edits (a bad / out-of-range line keeps the built-in number)
  LIVE        0.4.1's LIVE phase (start twice on a scratch COPY of the live Skyy_SkyyPets folder: nothing written)
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import trees_v3_effects as V3E

_cmp0 = HK.run_compare
_s44 = importlib.util.spec_from_file_location("test_skyypets_0_4_4", os.path.join(HERE, "test_skyypets_0.4.4.py"))
T44 = importlib.util.module_from_spec(_s44)
_s44.loader.exec_module(T44)
T41 = T44.T41
HK.run_compare = _cmp0

VERSION = "0.4.5"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.4.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "st3r3b", "pets")))
EXPECT = {
    "PetBuff": sorted(["+m compute2", "~m intact", "~m publish", "~m clear"]),
    "PetTick": ["~m second"],
    "SkyyPetsPlugin": ["~m setup", "~m shutdown"],
    # only the version text "0.4.4" -> "0.4.5" (the config.properties header + the Server Setup header)
    # fixer: + trees.properties (the Skill Trees 3 pet rows' numbers, Server Setup -> Pets -> Skill trees): the fields, the loader, the kit's
    # second file (CfgFile init / CfgRows defLines + DL1 = the kit's own per-file tables)
    "PetsCfg": sorted(["~m applyAll", "~m seed", "~m reloadAll", "+m v3num", "+m v3per", "+m v3most", "+m loadV3", "~<clinit>", "+f V3_TEXT"]
                      + ["+f V3P%d" % _i for _i in range(12)] + ["+f V3X%d" % _i for _i in range(12)]),
    "CfgFn": ["~m opExport"], "CfgRows": sorted(["~<clinit>", "~m header", "+f DL1", "~m defLines"]), "CfgFile": sorted(["~<clinit>", "~m init"]),
}
ADDED = ["PetV3"]


def run_v3(out, jar, scratch, _home):
    W = T44._world(out, jar, scratch, "v3")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    P_ = lambda n: JClass(PKG + n)
    Buff, V3, Cfg, Kind, Tick, Store = P_("PetBuff"), P_("PetV3"), P_("PetsCfg"), P_("PetKind"), P_("PetTick"), P_("PetStore")
    BR = W["BR"]
    Int = JClass("java.lang.Integer")
    RANK = {}

    def fake(a):
        k = str(a[1])
        v = RANK.get(k, 0)
        if v == "boom":
            raise RuntimeError("boom")
        if isinstance(v, str):
            return JClass("java.lang.String")(v)
        return Int(v)
    BR.put("tree:fn:level", JProxy("java.util.function.Function", dict={"apply": fake}))
    # the table made it into the jar
    rows = V3E.rows("SkyyPets")
    K.check([str(x) for x in V3.KEYS] == [V3E.key(e[0], e[1], e[2]) for e in rows] and [str(x) for x in V3.EFF] == [e[4] for e in rows]
            and [float(x) for x in V3.PER] == [float(e[5]) for e in rows], "TBL PetV3 holds the trees_v3_effects rows of SkyyPets (%d)" % len(rows))
    K.check(str(V3.READS) == V3E.reads_csv("SkyyPets") and len(str(V3.READS).split(",")) == 8, "TBL tree:reads:SkyyPets = the 8 keys: %s" % V3.READS)

    u, k, r = T44._mk(W, 701)
    # a Rare (tier 3) Lv 100 Goat (Mining) in the pet slot
    for kk, vv in (("kind", "Goat"), ("rarity", "3"), ("level", "100")):
        r.set("pet.g1.%s" % kk, vv)
    r.set("active.1", "g1")
    us = str(u)

    def bon():
        m = BR.get("skill:bonus:" + us)
        s = m.get("pets") if m is not None else None
        return dict((str(a), float(b)) for a, b in s.entrySet()) if s is not None else {}

    def pst():
        m = BR.get("pets:stats:" + us)
        return dict((str(a), float(b)) for a, b in m.entrySet()) if m is not None else {}
    Tick.second(u, "w", None)
    b0, p0 = bon(), pst()
    t0 = list(Buff.compute(r, "w"))
    K.check(set(b0) == {"dd.mining"} and abs(b0["dd.mining"] - t0[list(Kind.STAT_KEYS).index("fortune.mining")] / 100.0) < 1e-9 and "swing.mining" in p0,
            "R0 rank 0 everywhere = exactly the 0.4.4 entries (the Goat's own Fortune + swing): %s %s" % (b0, p0))
    # Pet Digger rank 2 (fixer: x the RARITY BONUS, Rare = x1.2 by default): + 2 % x 2 x 1.2 = 4.8 % Mining XP, + 1 % x 2 x 1.2 = 2.4 % Fortune
    f3, f5, f6 = float(Cfg.factor(3)), float(Cfg.factor(5)), float(Cfg.factor(6))
    K.check(abs(f3 - 1.2) < 1e-9 and abs(f5 - 1.4) < 1e-9 and abs(f6 - 1.5) < 1e-9, "RAR the default rarity bonuses Rare x1.2, Legendary x1.4, Mythic x1.5")
    kd = V3E.key("Mining", 3, "r3a")
    RANK[kd] = 2
    Tick.second(u, "w", None)
    b1 = bon()
    K.check(abs(b1.get("xp.mining", 0) - 0.02 * 2 * f3) < 1e-9 and abs(b1.get("dd.mining", 0) - (b0["dd.mining"] + 0.01 * 2 * f3)) < 1e-9,
            "DIG Pet Digger rank 2 with a Rare Mining pet: +4.8 %% Mining XP, +2.4 %% Fortune added to the pet's own: %s" % b1)
    RANK[kd] = 9
    Tick.second(u, "w", None)
    K.check(abs(bon().get("xp.mining", 0) - 0.02 * 5 * f3) < 1e-9 and int(V3.MAX[list(V3.KEYS).index(kd)]) == 5, "DIG a rank above max (9) is clamped to Pet Digger's max 5 (+12 %%): %s" % bon())
    # fixer: a Mythic pet at rank 5 = the x1.5 top: +15 % XP, +7.5 Fortune (0.4.5 first build: +60 % / +30)
    r.set("pet.g1.rarity", "6")
    Tick.second(u, "w", None)
    b6 = bon()
    t6 = list(Buff.compute(r, "w"))[list(Kind.STAT_KEYS).index("fortune.mining")] / 100.0
    K.check(abs(b6.get("xp.mining", 0) - 0.15) < 1e-9 and abs(b6.get("dd.mining", 0) - (t6 + 0.075)) < 1e-9,
            "MYTH Mythic Mining pet, Pet Digger rank 5: +15 %% XP, +7.5 Fortune (the pet's own stays under its cap): %s" % b6)
    # fixer: Server Setup numbers - a lower ceiling / a new per-rank number change the live value at once (PetsCfg fields = the kit binding)
    ix = [i for i, e in enumerate(rows) if V3E.key(e[0], e[1], e[2]) == kd and e[4] == "xp.mining"][0]
    idd = [i for i, e in enumerate(rows) if V3E.key(e[0], e[1], e[2]) == kd and e[4] == "dd.mining"][0]
    K.check(abs(float(getattr(Cfg, "V3X%d" % ix)) - 15.0) < 1e-9 and abs(float(getattr(Cfg, "V3X%d" % idd)) - 7.5) < 1e-9
            and abs(float(getattr(Cfg, "V3P%d" % ix)) - 2.0) < 1e-9, "CFG the built-in numbers: XP 2 %% a rank, at most 15 %%; Fortune at most 7.5")
    setattr(Cfg, "V3X%d" % ix, 5.0)
    Tick.second(u, "w", None)
    K.check(abs(bon().get("xp.mining", 0) - 0.05) < 1e-9, "CFG the XP ceiling set to 5 %% caps Pet Digger's XP at 5 %%: %s" % bon())
    setattr(Cfg, "V3X%d" % ix, 15.0)
    setattr(Cfg, "V3P%d" % ix, 1.0)
    Tick.second(u, "w", None)
    K.check(abs(bon().get("xp.mining", 0) - 0.01 * 5 * f6) < 1e-9, "CFG per rank set to 1 %%: 1 x 5 x 1.5 = 7.5 %%: %s" % bon())
    setattr(Cfg, "V3P%d" % ix, 0.0)
    Tick.second(u, "w", None)
    K.check("xp.mining" not in bon(), "CFG per rank 0 = the row gives nothing: %s" % bon())
    setattr(Cfg, "V3P%d" % ix, 2.0)
    r.set("pet.g1.rarity", "3")
    RANK[kd] = "x"
    Tick.second(u, "w", None)
    K.check("xp.mining" not in bon(), "DIG a non-number answer = rank 0")
    RANK[kd] = "boom"
    Tick.second(u, "w", None)
    K.check("xp.mining" not in bon(), "DIG an answer that throws = rank 0 (the tick goes on)")
    RANK[kd] = 1
    # Smithing Pet Hammer reads the Mining pet too; Foraging rows see nothing (no Foraging pet)
    RANK[V3E.key("Smithing", 2, "r3b")] = 3
    RANK[V3E.key("Foraging", 2, "r4a")] = 3
    Tick.second(u, "w", None)
    b2 = bon()
    K.check(abs(b2.get("xp.smithing", 0) - 0.02 * 3 * f3) < 1e-9 and "xp.foraging" not in b2 and abs(b2.get("xp.mining", 0) - 0.02 * f3) < 1e-9,
            "HAM Pet Hammer rank 3 x Rare Mining pet = +7.2 %% Smithing XP; the Foraging row needs a Foraging pet = nothing: %s" % b2)
    # an off kind gives nothing
    Cfg.KINDS_OFF = "Goat"
    Tick.second(u, "w", None)
    K.check("xp.mining" not in bon() and "xp.smithing" not in bon(), "OFF a switched-off pet kind = no tree rows: %s" % bon())
    Cfg.KINDS_OFF = "-"
    # a Combat pet in the open summon slot: Pet Fang -> xp.combat + pets:stats dmg
    for kk, vv in (("kind", "Wolf"), ("rarity", "5"), ("level", "50")):
        r.set("pet.w1.%s" % kk, vv)
    r.set("active.2", "w1")
    r.set("slot2.unlocked", "true")
    kf = V3E.key("Combat", 3, "r3a")
    RANK[kf] = 2
    Tick.second(u, "w", None)
    b3, p3 = bon(), pst()
    sk = str(Cfg.kind("Wolf").skill)
    if sk == "Combat" and bool(Cfg.summonable("Wolf")):
        K.check(abs(b3.get("xp.combat", 0) - 0.02 * 2 * f5) < 1e-9 and abs(p3.get("dmg", 0) - (p0.get("dmg", 0) + 2 * f5)) < 1e-9,
                "FANG a Legendary (x1.4) Combat pet in the summon slot, Pet Fang rank 2: +5.6 %% combat XP (xp.combat), +2.8 Damage %% (pets:stats dmg): %s %s" % (b3, p3))
    else:
        K.check(False, "FANG the Wolf is no summonable Combat pet any more (%s) - pick another kind for this check" % sk)
    # Mining Pet Synergy: the Goat's own stats x (1 + 4 % x 3)
    RANK.clear()
    r.set("pet.g1.level", "30")          # under the Fortune / swing caps
    Tick.second(u, "w", None)
    base = list(Buff.compute2(u, r, "w"))
    RANK[V3E.key("Mining", 3, "r5a")] = 3
    syn = list(Buff.compute2(u, r, "w"))
    FM, SM = list(Kind.STAT_KEYS).index("fortune.mining"), list(Kind.STAT_KEYS).index("swing.mining")
    want_f = min(base[FM] * 1.12, float(Cfg.FORT_CAP) * float(Buff.capMult(r)))
    K.check(abs(syn[FM] - want_f) < 1e-6 and syn[SM] > base[SM] and abs(syn[list(Kind.STAT_KEYS).index("dmg")] - base[list(Kind.STAT_KEYS).index("dmg")]) < 1e-9,
            "SYN Mining Pet Synergy rank 3: the Goat's Fortune %.3f -> %.3f (x1.12 under the cap), swing up, the Combat pet unchanged" % (base[FM], syn[FM]))
    Tick.second(u, "w", None)
    K.check(abs(bon().get("dd.mining", 0) - syn[FM] / 100.0) < 1e-9, "SYN ... and published as dd.mining: %s" % bon())
    # pets OFF / a no-buff world: no extras, the source goes
    RANK[kd] = 3
    Cfg.ON = False
    Tick.second(u, "w", None)
    K.check(not bon() and not pst() and V3.LASTX.get(u) is None, "OFFALL pets OFF = no pets source, no extras")
    Cfg.ON = True
    Cfg.NOBUFF = "nobuffworld"
    Tick.second(u, "nobuffworld", None)
    K.check("xp.mining" not in bon() and V3.LASTX.get(u) is None, "NOBUFF a no-buff world = no tree rows: %s" % bon())
    Cfg.NOBUFF = ""
    Tick.second(u, "w", None)
    K.check(abs(bon().get("xp.mining", 0) - 0.06 * f3) < 1e-9, "BACK the next normal second publishes them again")
    # another mod replaced the skill:bonus map: the next second re-fills (intact sees the extras)
    BR.put("skill:bonus:" + us, JClass("java.util.concurrent.ConcurrentHashMap")())
    Tick.second(u, "w", None)
    K.check(abs(bon().get("xp.mining", 0) - 0.06 * f3) < 1e-9, "INTACT a replaced skill:bonus map is re-filled with the tree rows")
    # leave: everything goes
    Buff.clear(u)
    K.check(not bon() and V3.LASTX.get(u) is None, "LEAVE PetBuff.clear drops the extras too")
    # the reader list
    V3.reads(True)
    K.check(str(BR.get("tree:reads:SkyyPets")) == str(V3.READS), "READS published")
    BR.put("tree:reads:SkyyPets", "someone-else")
    V3.reads(False)
    K.check(str(BR.get("tree:reads:SkyyPets")) == "someone-else", "READS shutdown removes only our own value")
    BR.put("tree:reads:SkyyPets", V3.READS)
    V3.reads(False)
    K.check(BR.get("tree:reads:SkyyPets") is None, "READS ... and does remove ours")
    # no SkyyTrees at all
    BR.remove("tree:fn:level")
    K.check(int(V3.rank(u, kd, 3)) == 0, "NOTREES no tree:fn:level = rank 0")
    # fixer: trees.properties - seeded with the table's text when missing, hand edits read, bad lines keep the built-in number
    Paths = JClass("java.nio.file.Paths")
    td = os.path.join(scratch, "v3cfg")
    os.makedirs(td, exist_ok=True)
    tf = os.path.join(td, "trees.properties")
    if os.path.exists(tf):
        os.remove(tf)
    res = str(Cfg.loadV3(Paths.get(td)))
    K.check(os.path.exists(tf) and open(tf, encoding="latin-1", newline="").read() == V3E.cfg_text("SkyyPets") and res == "trees.properties read",
            "LOAD a missing trees.properties is written with the table's defaults (%s)" % res)
    t = open(tf, encoding="latin-1", newline="").read()
    ck = V3E.ckey(rows[ix])
    t = t.replace("%s.per=2\n" % ck, "%s.per=3\n" % ck).replace("%s.max=15\n" % ck, "%s.max=-4\n" % ck)
    open(tf, "w", encoding="latin-1", newline="").write(t)
    Cfg.loadV3(Paths.get(td))
    K.check(abs(float(getattr(Cfg, "V3P%d" % ix)) - 3.0) < 1e-9 and abs(float(getattr(Cfg, "V3X%d" % ix)) - 15.0) < 1e-9,
            "LOAD a hand edit (per 3) is read; a bad line (max -4) keeps the built-in 15")
    K.check(abs(float(Cfg.v3per(ix)) - 0.03) < 1e-12 and abs(float(Cfg.v3most(ix)) - 0.15) < 1e-12 and float(Cfg.v3per(99)) == 0.0,
            "LOAD v3per / v3most answer in effect units (fractions)")
    setattr(Cfg, "V3P%d" % ix, 2.0)
    K.save()


def run_live(out, jar, scratch, home):
    # 0.4.1's LIVE phase, except: start 1 writes exactly ONE new file, trees.properties (fixer: the Skill Trees 3 numbers, = the table's text);
    # start 2 writes nothing
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P_ = lambda n: JClass(PKG + n)
    Cfg, Store, Mig, Mig2, Log, Egg, Hy = P_("PetsCfg"), P_("PetStore"), P_("PetsCfgMig"), P_("PetsCfgMig2"), P_("PetsLog"), P_("PetEgg"), P_("PetHatchery")
    Paths = JClass("java.nio.file.Paths")
    Log.LINES = JClass("java.util.ArrayList")()
    mods = os.path.dirname(home)
    t0 = T41.tree(home)

    def start():
        Mig.run(Paths.get(home))
        Mig2.run(Paths.get(home))
        Cfg.load(Paths.get(mods))
        Store.ROOT = Paths.get(home)
        Store.DIR = Store.ROOT.resolve("pets")
        return ([int(x) for x in Store.scanAll()], [int(x) for x in Store.fuseRecover()], [int(x) for x in Egg.recover()], [int(x) for x in Hy.recover()])
    sc1, fr1, hr1, hq1 = start()
    t1 = T41.tree(home)
    ch = sorted(k for k in set(t0) | set(t1) if t0.get(k) != t1.get(k))
    tp = os.path.join(home, "trees.properties")
    K.check(ch == ["trees.properties"] and open(tp, encoding="latin-1", newline="").read() == V3E.cfg_text("SkyyPets"),
            "LIVE start 1 writes only the new trees.properties (the table's defaults; no config migration): %s" % ch)
    K.check(sc1[2] == 0 and sc1[3] == 0 and fr1[0] == 0 and hr1[0] == 0 and hq1[0] == 0, "LIVE every pet file read %s, no cut-off fuse / hatch / egg move" % sc1)
    K.check(abs(float(Cfg.v3most(0)) - V3E.vmax(V3E.rows("SkyyPets")[0])) < 1e-12, "LIVE the Skill Trees 3 numbers are the built-in ones")
    sc2, fr2, hr2, hq2 = start()
    K.check(T41.tree(home) == t1 and sc2 == sc1, "LIVE start 2 writes NOTHING")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("v3", run_v3), ("live", run_live)], script=__file__, live=(T41.LIVE, "Skyy_SkyyPets"))
