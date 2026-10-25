"""Harness for SkyyShards 0.4.11 (THE COMBAT SHARD: one island per zone - starter archipelago round R5, research/Starter-Archipelago-Spec.md
section 10; tools/shards_0_4_11_patch.py, on top of the 0.4.10 hotfix).
Build first:
    python tools/shards_0_4_11_patch.py && python SkyyShards/build_skyyshards_0.4.11.py
    python SkyyShards/test_skyyshards_0.4.11.py [--keep]

  S    static   the patch re-runs to identical bytes; no new registerSystem / registerCommand; ShCombat + ShFight written; the ready line
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.4.10 -> 0.4.11: exactly the planned members differ (EXPECT); the map files: only the Combat map's differ
  410  every 0.4.10 harness phase on the 0.4.11 jar (and through it 0.4.9 / 0.4.8 / 0.4.7 / 0.4.6), incl. PHASE O (the in-order selector
       walk over every page variant) and F (the click flows on a simulated client) - checks 0.4.11 changes on purpose kept as notes
  Z    zones    the ladder (Zone 1 = the old key, Zones 2-5), tname, the sub names, every spec 10 table value (cap / levels / respawn at
                every size + level, the zone offsets), the pools per zone x size x part (night void mobs on Small, the cavern mobs only
                at Large), the drop split (sums, determinism, fallback), the class gate, the materials
  G    land     EXECUTED ShGeo + ShFill on a block map for every zone x size x slot: the floor of the zone, the rise / forest / corner /
                torches, NOTHING standing on a bridge's walkway, the cavern + stair only at Large (in chunk section 2), the stair WALKED
                from the island floor down to the cavern floor, the spawn spots standable, grow Small -> Medium -> Large in place
  N    night    EXECUTED ShFight.night on simulated players: the night packet when a player is in the Combat region, again after 3 s (not
                before), the real time back on leaving the region, a player gone from the world forgotten without a packet, the switch off
  W    spawn    EXECUTED ShFight.tickWorld on a simulated world (the painted block map + a fake entity store): fill one a second to the cap,
                levels inside the range (+ the zone offset), never within combat.minDist of a player and only on a standable spot, a dead
                mob's place back after exactly the respawn time, the cap / level / speed sub-upgrades, AFK (no move in combat.afkSec =
                no spawns, a step = spawns again), the hourly lid, nobody on the island 30 s = removed, the leash, Large upper vs cavern
                pools, leftovers adopted (pool roles only) + the excess removed, visitors never spawn mobs, spawning off / a paused
                shard / an island gone = removed, an unknown role skipped
  B    buy      EXECUTED purchases on the 0.4.6 fixture: Zone 2 refused below class level 20 (text), bought at 25 (coins + 64 Medium Hide
                taken, Small, its own slot), Zone 3 before Zone 2 refused, the 3 combat subs (combat.mat.* items), Grow's text with the
                combat names; COLLECT gives the pool's drops (the sum = what was stored, a full inventory keeps the rest, no XP)
  K    config   a fresh file holds every combat row; hand edits + junk (a bad range = the default + WARN); the Server Setup rows
  GT   gate     shard:fn:allowed("hurt") = yes in a shard world, unanswered elsewhere
  O2   order    the Combat Map tab: every zone x size x level x view x class level, built on the real UICommandBuilder and walked in order
  D    live     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyyShards: nothing runs again, every real shard's menu clicked through
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import balance_model as BM

VERSION = "0.4.11"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "r5combat2fix2", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.10.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.10.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_11_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
_spec = importlib.util.spec_from_file_location("test_skyyshards_0_4_10", os.path.join(HERE, "test_skyyshards_0.4.10.py"))
T410 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T410)
sys.argv[:] = _argv
T410.JAR = JAR
T49 = T410.T49
T49.JAR = JAR
T48 = T49.T48
T48.JAR = JAR
T47, T46 = T48.T47, T48.T46
T46.JAR = JAR
T47.JAR = JAR
T42 = T46.T42
OWNER, MEMBER, VISITOR = T46.OWNER, T46.MEMBER, T46.VISITOR
KINDS = ["Mining", "Foraging", "Farming", "Ranching", "Orchard", "Combat"]
KK = [k.lower() for k in KINDS]
MKD, FOK, FK, RK, OK_, CK = 0, 1, 2, 3, 4, 5
Y = 100
CAP = [[3, 4, 5, 6, 7, 8], [8, 9, 10, 10, 11, 12], [12, 13, 14, 16, 17, 18]]
LVL = [[(1, 3), (2, 4), (2, 5), (3, 6), (4, 7), (5, 8)], [(5, 8), (6, 9), (7, 10), (8, 11), (9, 12), (10, 13)], [(10, 13), (11, 14), (12, 16), (13, 17), (15, 19), (16, 20)]]
RSP = [[30, 27, 24, 21, 18, 15], [15, 14, 13, 12, 11, 10], [10, 9, 8, 8, 7, 6]]
OFF = [0, 20, 40, 60, 80]
ZDROP = ["Ingredient_Bone_Fragment", "Ingredient_Hide_Medium", "Ingredient_Ice_Essence", "Ingredient_Fabric_Scrap_Cindercloth", "Ingredient_Fire_Essence"]
VOID = ("Larva_Void", "Crawler_Void", "Eye_Void")
CAVE1 = ("Goblin_Scrapper", "Goblin_Lobber", "Goblin_Miner", "Goblin_Burner", "Rat", "Spider_Cave", "Toad_Rhino_Magma", "Golem_Firesteel", "Skeleton_Soldier")
SUP = T49._superseded


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.11 - build script') and g.count('VERSION = "0.4.11"\n') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check("[admc, gfn, dfn, smap, pl, cmb, fight, nightf]" in g and 'cmb = mk("ShCombat")' in g and 'fight = mk("ShFight"' in g and 'nightf = mk("ShNightF"' in g, "S ShCombat + ShFight + ShNightF written out")
    K.check("@PAD@.registerOutbound((@PPF@) new @PKG@.ShNightF())" in g and "@PAD@.deregisterOutbound(nf)" in g, "S the night filter is registered at setup and removed at shutdown")
    K.check("0.4.11: THE COMBAT SHARD (one island per zone" in g and "0.4.10: the shard menu opens again" in g, "S the ready line names the round (and keeps the hotfix's)")
    K.check("this.kShown = kShownSig(this.kZ)" in g and "if (this.kst != null) kSets(b); else stSets(b);" in g, "S the 0.4.10 hotfix is kept (kShown + status sets after base2)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    K.save()


# ---------------------------------------------------------------------------------------------------------- the 0.4.10 phases, 0.4.11 changes as notes
# Combat has 5 islands now (Zone 1 at T2 cost numbers, the zone names): the older phases that counted one Combat island or priced the old T1
# skeleton island, and the old map-file byte compare, describe behaviour 0.4.11 replaces on purpose.
SUP411 = ()


def _sup(fn, extra=()):
    return lambda out, jar, scratch, home: SUP(SUP411 + tuple(extra), lambda: fn(out, jar, scratch, home))


# ---------------------------------------------------------------------------------------------------------- the fixture
def _L(scratch, K):
    L = T49._setup(scratch, K)
    from jpype import JClass
    for n in ("ShCombat", "ShFight", "ShGeo", "ShFill", "ShGate", "ShIsl", "ShMath"):
        L[n] = JClass(PKG + n)
    T48.add_items([(i, 100) for i in ZDROP + ["Ingredient_Void_Essence", "Ingredient_Life_Essence", "Ingredient_Water_Essence", "Ingredient_Fabric_Scrap_Linen"]])
    Cb = L["ShCombat"]
    ids = set()
    for i in range(len(Cb.DROP_IDS)):
        for x in str(Cb.DROP_IDS[i]).split(","):
            if x:
                ids.add(x.rsplit(":", 1)[0])
    T48.add_items([(i, 100) for i in sorted(ids)])
    return L


_KN = [0]


def _key():
    """a fresh profile key (a valid pkey: uuid + -p1)"""
    _KN[0] += 1
    return "0b0b0b0b-1111-2222-3333-%012d-p1" % _KN[0]


def _prof(L, key, slots, auto=False):
    """a profile with combat islands: slots = [(slot, ladder index, size, (amt, deco, irr))]"""
    St, Mth = L["ShStore"], L["ShMath"]
    p = St.get(key)
    assert p is not None, key
    St.LOCK.lock()
    try:
        for s, zi, sz, lv in slots:
            p.setProperty("combat.i%d.type" % s, "skeleton" if zi == 0 else "zone%d" % (zi + 1))
            p.setProperty("combat.i%d.size" % s, str(sz))
            p.setProperty("combat.i%d.last" % s, "1790000000000")
            p.setProperty("combat.i%d.stored" % s, "0")
            p.setProperty("combat.i%d.totems" % s, "soul_cage:1")
            for f_, v_ in zip(("amt", "deco", "irr"), lv):
                p.setProperty("combat.i%d.%s" % (s, f_), str(v_))
        if auto:
            p.setProperty("combat.auto", "1")
        St.save(key, p)
    finally:
        St.LOCK.unlock()
    return p


def _paint(L, p, kd=CK):
    """the region's wanted cells painted onto a fresh block map (ShFill.TEST_BLOCKS) - returns the map (dict-like Java HashMap)"""
    from jpype import JClass
    Geo, Fill = L["ShGeo"], L["ShFill"]
    m = JClass("java.util.HashMap")()
    Fill.TEST_BLOCKS = m
    want = Geo.region(p, kd)
    Fill.paintY(None, want, None, None)
    return m, want


def _ctr(L, slot):
    Geo = L["ShGeo"]
    return int(Geo.ox(CK)) + int(Geo.SX[slot]), int(Geo.OZ) + int(Geo.SZ[slot])


# ---------------------------------------------------------------------------------------------------------- Z: the zone tables (pure)
def run_zones(out, jar, scratch, _home):
    K = HK.Child(out)
    L = _L(os.path.join(scratch, "z"), K)
    Isl, Cb, Cfg = L["ShIsl"], L["ShCombat"], L["ShCfg"]
    l0, n = int(Isl.LAD0[CK]), int(Isl.LADN[CK])
    K.eq(n, 5, "Z the Combat ladder has 5 zones")
    K.eq([str(Isl.KEY[l0 + i]) for i in range(n)], ["skeleton", "zone2", "zone3", "zone4", "zone5"], "Z Zone 1 keeps the old key (every owned Combat island is Zone 1)")
    K.eq([str(Isl.tname(l0 + i)) for i in range(n)], ["Zone %d" % (i + 1) for i in range(5)], "Z tname = Zone N (no tier tag)")
    K.eq([int(Isl.TIER[l0 + i]) for i in range(n)], [2, 5, 8, 11, 14], "Z cost tiers = P7_MID_T (spec 13.2)")
    K.eq([str(Isl.PROD[l0 + i]) for i in range(n)], ZDROP, "Z the zones' common drops")
    K.eq(str(Isl.tname(int(Isl.LAD0[FK]) + 1)), "T2 Lettuce", "Z other shards keep the tier tag")
    K.eq([str(Isl.subName(CK, w)) for w in range(3)], ["Mobs at once", "Mob level", "Spawn speed"], "Z the combat sub names (spec 10)")
    K.eq([str(Isl.subName(FK, w)) for w in range(3)], ["Crop Amount", "Decorations", "Irrigation"], "Z Farming's sub names unchanged")
    bad = []
    for s in range(3):
        for l in range(6):
            if int(Cb.cap(s + 1, l)) != CAP[s][l]:
                bad.append(("cap", s, l, int(Cb.cap(s + 1, l))))
            if int(Cb.respawnSec(s + 1, l)) != RSP[s][l]:
                bad.append(("rsp", s, l))
            for z in range(5):
                if (int(Cb.lvLo(z, s + 1, l)), int(Cb.lvHi(z, s + 1, l))) != (LVL[s][l][0] + OFF[z], LVL[s][l][1] + OFF[z]):
                    bad.append(("lvl", z, s, l))
            want_low = CAP[s][l] // 2 if s == 2 else 0
            if int(Cb.lowerCap(s + 1, l)) != want_low:
                bad.append(("low", s, l))
    K.eq(bad, [], "Z every spec 10 value: mobs at once 3..8 / 8..12 / 12..18 (Large half below), Lv 1-3 .. 16-20 + 0/20/40/60/80, respawn 30..15 / 15..10 / 10..6")
    K.eq([int(Cb.need(i)) for i in range(5)], [0, 20, 40, 60, 80], "Z class level per zone (Zone 1 = with the shard)")
    r1 = [str(x) for x in Cb.roles(0, 1, 0)]
    K.check(all(v in r1 for v in VOID) and "Skeleton_Fighter" in r1 and "Wolf_Black" in r1 and "Bear_Grizzly" not in r1, "Z Zone 1 Small: skeletons, wolves + the night void mobs: %s" % r1)
    r2 = [str(x) for x in Cb.roles(0, 2, 0)]
    K.check(all(v in r2 for v in r1) and all(v in r2 for v in ("Bear_Grizzly", "Spider", "Skeleton_Burnt_Praetorian")) and len(r2) == len(r1) + 3, "Z Medium adds grizzly, spider, praetorian (keeps Small's)")
    r3 = [str(x) for x in Cb.roles(0, 3, 0)]
    K.check(all(v in r3 for v in r2) and all(v in r3 for v in ("Snake_Marsh", "Fen_Stalker", "Skeleton_Mage")), "Z Large upper adds the swamp / mage mobs")
    lw = [str(x) for x in Cb.roles(0, 3, 1)]
    K.eq(sorted(lw), sorted(CAVE1), "Z the Large cavern = goblins, rats, cave spiders, magma toads, Golem_Firesteel, mineshaft skeletons")
    K.check(len(list(Cb.roles(0, 2, 1))) == 0 and len(list(Cb.roles(0, 1, 1))) == 0, "Z no cavern below Large")
    K.check(all(len(list(Cb.roles(z, 3, 0))) >= 8 and len(list(Cb.roles(z, 3, 1))) >= 4 for z in range(5)), "Z every zone has upper + cavern pools at Large")
    K.check("Hyena" in [str(x) for x in Cb.roles(1, 1, 0)] and "Skeleton_Frost_Fighter" in [str(x) for x in Cb.roles(2, 2, 0)], "Z Zones 2 / 3 use their own vanilla mobs")
    # the drop split
    fails = []
    for z in range(5):
        for s in (1, 2, 3):
            for nn in (0, 1, 2, 7, 13, 100, 999, 12345):
                r = Cb.split(z, s, nn, ZDROP[z])
                ids, q = [str(x) for x in r[0]], [int(x) for x in r[1]]
                r2_ = Cb.split(z, s, nn, ZDROP[z])
                if sum(q) != nn or min(q + [0]) < 0 or len(ids) != len(q) or [int(x) for x in r2_[1]] != q:
                    fails.append((z, s, nn, ids, q))
    K.eq(fails, [], "Z the Soul Cage split: always adds up to what was made, never negative, the same every time")
    r = Cb.split(0, 1, 100, "Ingredient_Bone_Fragment")
    ids = [str(x) for x in r[0]]
    K.check("Ingredient_Bone_Fragment" in ids and len(ids) >= 2, "Z Zone 1 Small drops = its pool's vanilla drops: %s" % list(zip(ids, [int(x) for x in r[1]])))
    qd = dict(zip(ids, [int(x) for x in r[1]]))
    per = {}
    for r_ in [str(x) for x in Cb.allRoles(0, 1)]:
        for e_ in str(Cb.dropsOf(r_)).split(","):
            if e_:
                i_, q_ = e_.rsplit(":", 1)
                if not bool(Cb.skip(i_)):
                    per[i_] = per.get(i_, 0.0) + float(q_) * float(Cb.wt(0, r_))
    tw = sum(per.values())
    K.check(qd.get("Ingredient_Bone_Fragment", 0) == qd.get("Ingredient_Fabric_Scrap_Linen", -1) and all(abs(qd.get(i_, 0) - 100 * q_ / tw) < 1.0 for i_, q_ in per.items()),
            "Z the mix = a fight of the pool at the vanilla spawn odds (each role's drops a kill x its odds; combat.cageSkip left out): %s" % qd)
    # fix (critic r5combat2 2nd round): spawn odds, cageSkip, the weighted pick, the throughput lid factor
    K.check(float(Cb.wt(0, "Skeleton_Burnt_Praetorian")) < 0.25 * float(Cb.wt(0, "Skeleton_Fighter")) and float(Cb.wt(0, "Rat")) > 5 * float(Cb.wt(0, "Golem_Firesteel"))
            and float(Cb.wt(0, "No_Such_Role")) == 1.0, "Z vanilla spawn odds: Praetorian %.3f vs Skeleton_Fighter %.3f, Rat %.3f vs Golem_Firesteel %.3f, unknown = 1"
            % (float(Cb.wt(0, "Skeleton_Burnt_Praetorian")), float(Cb.wt(0, "Skeleton_Fighter")), float(Cb.wt(0, "Rat")), float(Cb.wt(0, "Golem_Firesteel"))))
    SKIPPED = ("Ore_", "Ingredient_Bar_", "Ingredient_Crystal_", "Rock_")
    bad_sk = sorted(set(i for z in range(5) for s_ in (1, 2, 3) for i in [str(x) for x in Cb.split(z, s_, 100000, ZDROP[z])[0]]
                        if i.startswith(SKIPPED) or i in ("Ingredient_Void_Essence", "Ingredient_Voidheart")))
    K.eq(bad_sk, [], "Z combat.cageSkip: no Void Essence / Voidheart / ingots / ores / crystals / stone from any Soul Cage (they come from fighting)")
    sk0 = Cfg.CB_SKIP
    Cfg.CB_SKIP = Cfg.skipOf("")
    try:
        K.check("Ingredient_Void_Essence" in [str(x) for x in Cb.split(0, 1, 1000, ZDROP[0])[0]], "Z combat.cageSkip empty: the night void mobs' Void Essence is in the mix again")
    finally:
        Cfg.CB_SKIP = sk0
    K.eq([str(x) for x in Cfg.skipOf(" Ore_* ,,Ingredient_Bone_Fragment, Ore_*")], ["Ore_*", "Ingredient_Bone_Fragment"], "Z combat.cageSkip text -> trimmed ids, no blanks / repeats")
    from jpype import JClass
    AL = JClass("java.util.ArrayList")
    ok_ = AL()
    for r_ in ("Skeleton_Fighter", "Skeleton_Burnt_Praetorian", "No_Such_Role"):
        ok_.add(r_)
    cnt = {}
    for k_ in range(10000):
        v_ = str(Cb.wpick(0, ok_, (k_ + 0.5) / 10000.0))
        cnt[v_] = cnt.get(v_, 0) + 1
    wsum = float(Cb.wt(0, "Skeleton_Fighter")) + float(Cb.wt(0, "Skeleton_Burnt_Praetorian")) + 1.0
    K.check(all(abs(cnt.get(r_, 0) / 10000.0 - float(Cb.wt(0, r_)) / wsum) < 0.002 for r_ in ("Skeleton_Fighter", "Skeleton_Burnt_Praetorian", "No_Such_Role"))
            and Cb.wpick(0, AL(), 0.5) is None, "Z the spawner picks by the spawn odds: %s" % cnt)
    K.check(abs(float(Cb.lidX(1, 0, 0)) - 1.0) < 1e-12 and abs(float(Cb.lidX(3, 5, 5)) - 30.0) < 1e-9 and abs(float(Cb.lidX(1, 5, 5)) - 16.0 / 3.0) < 1e-9
            and abs(float(Cb.lidX(2, 0, 0)) - 16.0 / 3.0) < 1e-9, "Z the spawn lid factor = mobs at once / respawn vs Small level 0 (1 / 5.33 / 30)")
    K.eq(str(Cb.dropsOf("Skeleton_Fighter")), "Ingredient_Bone_Fragment:1.5,Ingredient_Fabric_Scrap_Linen:1.5", "Z a role's drops a kill (the sword scrap = gear, left out)")
    K.check(not any(i.startswith(("Armor_", "Weapon_", "Tool_")) for z in range(5) for i in [str(x) for x in Cb.split(z, 3, 1000, "x")[0]]), "Z no gear in the drops")
    Cfg.CB_POOL[0] = "Wolf_Black"
    try:
        r = Cb.split(0, 1, 50, "Ingredient_Bone_Fragment")
        K.eq(([str(x) for x in r[0]], [int(x) for x in r[1]]), (["Ingredient_Bone_Fragment"], [50]), "Z a pool without known drops gives the zone's common drop")
    finally:
        Cfg.CB_POOL[0] = Cfg.DEF_CB_POOL[0]
    K.check(str(Cb.subMat(CK, 0)).startswith("raw:16|") and "Void_Essence" in str(Cb.subMat(CK, 0)) and "Life_Essence" in str(Cb.subMat(CK, 1))
            and "Water_Essence" in str(Cb.subMat(CK, 2)) and str(Cb.subMat(FK, 1)) == str(Cfg.MAT_DECO), "Z combat subs cost combat.mat.* (the others isl.mat.*)")
    K.eq(str(Cb.nextTxt(0, 1, 0, 0)), "3 -> 4 mobs at once", "Z next text: mobs at once")
    K.eq(str(Cb.nextTxt(1, 2, 1, 2)), "Lv 27-30 -> 28-31", "Z next text: mob level (Zone 2 offset)")
    K.eq(str(Cb.nextTxt(0, 3, 2, 4)), "every 7 s -> 6 s", "Z next text: spawn speed")
    K.eq(str(Cb.nowTxt(0, 3, 5, 5, 5)), "18 at once (9 below) - Lv 16-20 - every 6 s", "Z now text at a maxed Large")
    K.save()


# ---------------------------------------------------------------------------------------------------------- BAL: the Soul Cage's pace vs fighting a zone
def _kill_items(roles):
    """expected vanilla drop items a kill (gear left out) of each role, from Assets.zip's drop lists (Multiple = each child at Weight %,
    Choice = by weight, Single = the quantity's middle) -> the pool's mean"""
    import serverjar as SJ, zipfile
    z = zipfile.ZipFile(SJ.assets_zip())
    R = dict((n.rsplit("/", 1)[1][:-5], n) for n in z.namelist() if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
    D = dict((n.rsplit("/", 1)[1][:-5], n) for n in z.namelist() if n.startswith("Server/Drops/") and n.endswith(".json"))

    def ev(c):
        t = c.get("Type")
        if t == "Single":
            it = c.get("Item", {})
            i = it.get("ItemId") or ""
            return 0.0 if i.startswith(("Armor_", "Weapon_", "Tool_")) or not i else (it.get("QuantityMin", 1) + it.get("QuantityMax", 1)) / 2.0
        chs = c.get("Containers", [])
        if t == "Multiple":
            return sum(min(1.0, ch.get("Weight", 100) / 100.0) * ev(ch) for ch in chs)
        if t == "Choice":
            tw = float(sum(ch.get("Weight", 1) for ch in chs) or 1)
            return sum(ch.get("Weight", 1) / tw * ev(ch) for ch in chs)
        return 0.0
    tot = 0.0
    for r in roles:
        for d in re.findall(r'"DropList"\s*:\s*"([^"]+)"', z.read(R[r]).decode("utf-8-sig")):
            if d in D:
                tot += ev(json.loads(z.read(D[d]).decode("utf-8-sig")).get("Container", {}))
    return tot / max(1, len(roles))


def _c(x):
    return "{:,.0f}".format(x)


def _prices(scratch):
    """the live Bazaar prices (read-only: copied into scratch first); {} when there is none"""
    import shutil
    src = os.path.join(os.environ.get("APPDATA", ""), "Hytale", "UserData", "Saves", "NewBetaTest", "mods", "Skyy_SkyyBazaar", "products.properties")
    if not os.path.isfile(src):
        return {}
    os.makedirs(scratch, exist_ok=True)
    dst = os.path.join(scratch, "bazaar-products.properties")
    shutil.copyfile(src, dst)
    pr = {}
    for ln in open(dst, encoding="utf-8", errors="replace"):
        if "=" in ln and not ln.lstrip().startswith("#"):
            k_, v_ = ln.split("=", 1)
            a_ = v_.split(",")
            try:
                pr[k_.strip()] = float(a_[1])
            except (IndexError, ValueError):
                pass
    return pr


def _kill_value(Cb, z, roles, PR):
    """a kill of zone z at the vanilla spawn odds (the jar's own tables): (drop items, coins) - every drop (fighting keeps them all)"""
    w = items = coins = 0.0
    for r in roles:
        wr = float(Cb.wt(z, r))
        w += wr
        for e_ in str(Cb.dropsOf(r)).split(","):
            if e_:
                i_, q_ = e_.rsplit(":", 1)
                items += wr * float(q_)
                coins += wr * float(q_) * PR.get(i_, 0.0)
    return (items / w, coins / w) if w else (0.0, 0.0)


def _cage_value(Cb, z, size, PR):
    """coins an item of a zone-z Soul Cage's mix at `size`"""
    r = Cb.split(z, size, 100000, "x")
    return sum(int(q) * PR.get(str(i), 0.0) for i, q in zip(r[0], r[1])) / 100000.0


def run_balance(out, jar, scratch, _home):
    K = HK.Child(out)
    L = _L(os.path.join(scratch, "bal"), K)
    Tot, Isl, Cb, Cfg, St = L["ShTotem"], L["ShIsl"], L["ShCombat"], L["ShCfg"], L["ShStore"]
    t0 = 1790000000000

    def wr(kd, tier, size, typ="soul_cage"):
        return float(Tot.workerRate(kd, Tot.parse("%s:%d" % (typ, tier)), size, t0))
    K.check(abs(wr(FK, 1, 1, "harvest_spirit") - 1.125) < 1e-9 and abs(wr(FK, 5, 3, "harvest_spirit") - 25.975) < 0.01, "BAL Farming's worker speeds unchanged (1.125 / 25.975 a minute)")
    cage = [wr(CK, t, 3) for t in range(1, 6)]
    K.check(all(abs(cage[t - 1] - wr(CK, t, 1)) < 1e-12 and abs(cage[t - 1] - wr(CK, t, 2)) < 1e-12 for t in range(1, 6)),
            "BAL a Soul Cage's speed does not grow with the island's area (Small = Medium = Large)")
    # fix (critic: Skyy "new islands stay the same"): a new Zone 1 Small with one Soul Cage I = 1.125 / min = 67.5 / h = the 0.4.10 rate
    # (0.4.10's reach there = 1.0: the Farming worker's Small-island reach at tier I, the same formula); each tier = its worker speed
    rates = [float(x) for x in Cfg.RATES]
    K.check(all(abs(cage[t] - rates[t]) < 1e-9 for t in range(5)), "BAL each Soul Cage tier = its tier's worker speed %s" % ["%.4f" % x for x in cage])
    K.check(abs(cage[0] - 1.125) < 1e-9 and abs(wr(FK, 1, 1, "harvest_spirit") - 1.125) < 1e-9, "BAL a Soul Cage I = 1.125 / min (67.5 / h), as in 0.4.10")
    # 0.4.11 retune (Skyy popup COMBAT SHARD PACE "About 1-1.5x"): combat.cageGrowth (a power above one Soul Cage I) + combat.cagePct per zone
    from jpype import JArray as _JA, JInt as _JI
    r0 = rates[0]
    K.eq([int(x) for x in Cfg.CB_CAGE] + [int(Cfg.CB_GROW)], [100, 68, 39, 82, 68, 54], "BAL the retuned defaults: combat.cagePct 100,68,39,82,68, combat.cageGrowth 54")
    K.check(abs(float(Cfg.cbOut(r0, 0)) - r0) < 1e-12 and abs(float(Cfg.cbOut(0.5 * r0, 0)) - 0.5 * r0) < 1e-12 and abs(float(Cfg.cbOut(0.1, 0)) - 0.1) < 1e-12,
            "BAL cbOut: one Soul Cage I (and the manual phase below it) unchanged in Zone 1")
    K.check(abs(float(Cfg.cbOut(4 * r0, 0)) - r0 * 4 ** 0.54) < 1e-9 and abs(float(Cfg.cbOut(4 * r0, 2)) - 0.39 * r0 * 4 ** 0.54) < 1e-9
            and abs(float(Cfg.cbOut(4 * r0, 9)) - 0.68 * r0 * 4 ** 0.54) < 1e-9, "BAL cbOut: r0 x (r / r0) ^ 0.54 x the zone's cagePct (a zone past the list = its last)")
    _xs = [r0 * (0.2 + 0.37 * k_) for k_ in range(200)]
    K.check(all(float(Cfg.cbOut(_xs[k_], z_)) < float(Cfg.cbOut(_xs[k_ + 1], z_)) for z_ in range(5) for k_ in range(199)), "BAL cbOut always grows with the raw rate (every cage / upgrade / grow still adds)")
    _cg, _cc = int(Cfg.CB_GROW), [int(x) for x in Cfg.CB_CAGE]
    try:
        Cfg.CB_GROW = 100
        Cfg.CB_CAGE = _JA(_JI)([100, 100, 100, 100, 100])
        K.check(all(abs(float(Cfg.cbOut(x_, z_)) - x_) < 1e-9 for x_ in (0.3, 1.125, 7.0, 99.0) for z_ in range(5)), "BAL cageGrowth 100 + cagePct 100 = the raw rate (off)")
        Cfg.CB_CAGE = _JA(_JI)([50, 50, 50, 50, 50])
        K.check(abs(float(Cfg.cbOut(7.0, 3)) - 3.5) < 1e-9, "BAL combat.cagePct 50 halves the island")
    finally:
        Cfg.CB_GROW = _cg
        Cfg.CB_CAGE = _JA(_JI)(_cc)
    p = St.get(_key())
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.type", "skeleton")
        for f_ in ("amt", "deco", "irr"):
            p.setProperty("combat.i0.%s" % f_, "5")
    finally:
        St.LOCK.unlock()
    mx = float(Isl.mult(CK, p, 0, 3))
    K.check(abs(mx - 1.45 ** 3 * 1.4) < 1e-6, "BAL a maxed Large = x%.3f (the 0.4.9 +3 %% a level x the spawn factor 1.4: Mobs at once 18 / Spawn speed 6 s)" % mx)
    # fix (critic r5combat2 2nd round, spec 10): Mobs at once x Spawn speed drive the Soul Cage; a new island x1; combat.spawnBonus 0 = the +3 % alone
    K.check(abs(float(Cfg.cbSpawnX(1, 0, 0)) - 1.0) < 1e-12 and abs(float(Cfg.cbSpawnX(3, 5, 5)) - 1.4) < 1e-9
            and abs(float(Cfg.cbSpawnX(1, 5, 5)) - 1.4 ** (math.log(16.0 / 3.0) / math.log(30.0))) < 1e-9 and abs(float(Cfg.cbSpawnX(1, 5, 0)) - 1.4 ** (math.log(8.0 / 3.0) / math.log(30.0))) < 1e-9,
            "BAL the spawn factor: new x1, Small Mobs at once 5 x%.3f, + Spawn speed 5 x%.3f, maxed Large x1.4" % (float(Cfg.cbSpawnX(1, 5, 0)), float(Cfg.cbSpawnX(1, 5, 5))))
    K.check(all(float(Cfg.cbSpawnX(s_, a_, i_)) <= float(Cfg.cbSpawnX(s_, min(5, a_ + 1), i_)) + 1e-12 and float(Cfg.cbSpawnX(s_, a_, i_)) <= float(Cfg.cbSpawnX(s_, a_, min(5, i_ + 1))) + 1e-12
                for s_ in (1, 2, 3) for a_ in range(6) for i_ in range(6)), "BAL the spawn factor never drops with a level bought")
    Cfg.CB_SPB = 0
    try:
        K.check(abs(float(Isl.mult(CK, p, 0, 3)) - 1.45 ** 3) < 1e-6, "BAL combat.spawnBonus 0: the +3 % a level alone")
    finally:
        Cfg.CB_SPB = 40
    PR = _prices(scratch)
    rows = []
    RAT = []

    def irate(z, size, tier, n, lv, tc):
        """the REAL island rate (ShTotem.islandRate, Automated) in items / hour: zone z, n Soul Cages of `tier`, every sub at lv, compressor tc"""
        St.LOCK.lock()
        try:
            p.setProperty("combat.i0.type", "skeleton" if z == 0 else "zone%d" % (z + 1))
            p.setProperty("combat.i0.size", str(size))
            p.setProperty("combat.i0.totems", ",".join(["soul_cage:%d" % tier] * n))
            for f_ in ("amt", "deco", "irr"):
                p.setProperty("combat.i0.%s" % f_, str(lv))
            p.setProperty("combat.auto", "1")
            p.setProperty("combat.compressor", str(tc))
        finally:
            St.LOCK.unlock()
        return float(Tot.islandRate(CK, p, 0, size, t0)) * 60.0
    tc3 = float(Cfg.TC_MULT[3])
    K.check(abs(irate(0, 1, 1, 1, 0, 0) - 67.5) < 1e-9, "BAL Skyy 'new islands stay the same': a new Zone 1 Small island (one Soul Cage I, Automated) = 67.5 / h, exactly 0.4.10")
    for z in range(5):
        roles = list(dict.fromkeys([str(x) for x in Cb.allRoles(z, 3)]))
        ipk, cpk = _kill_value(Cb, z, roles, PR)              # a kill of the zone (vanilla spawn odds, every drop - fighting keeps them all)
        fight, fightC = BM.KILLS_H * ipk, BM.KILLS_H * cpk     # an hour of fighting that zone yourself (150 kills)
        cs_, cl_ = _cage_value(Cb, z, 1, PR), _cage_value(Cb, z, 3, PR)   # coins an item of the cage's mix (Small / Large)
        new = irate(z, 1, 1, 1, 0, 0)                          # a new Small island, one Soul Cage I (manual phase: x 0.5)
        maxed = irate(z, 3, z + 1, 5, 5, 0)                    # a maxed Large, 5 Soul Cages of the zone's tier, no Time Compressor
        maxtc = irate(z, 3, z + 1, 5, 5, 3)                    # ... + Time Compressor III (the FULLY maxed island)
        best = irate(z, 3, 5, 5, 5, 3)                         # ... with 5 Soul Cage V
        raw = 5 * cage[z] * 60.0 * mx                          # before the retune (combat.cageGrowth 100, cagePct 100)
        K.check(abs(maxtc / maxed - tc3) < 1e-9, "BAL Zone %d: the Time Compressor III is not squeezed on a combat island (x%g, as its menu says)" % (z + 1, tc3))
        f_ = 1.0 / fightC if fightC else 0.0
        RAT.append((maxtc * cl_ * f_, best * cl_ * f_, new * cs_, maxed * cl_ * f_, new * cs_ * f_))
        rows.append("Zone %d: fighting %d drops / h = %s coins | new Small cage I %.1f / h = %s coins (%.3fx) | maxed Large 5 x cage %s: %.0f / h = %s coins (%.2fx), + Time Compressor III %.0f / h = %s coins (%.2fx) | 5 x cage V + TC III %.2fx | before the retune %.2fx (TC III %.2fx)"
                    % (z + 1, fight, _c(fightC), new, _c(new * cs_), RAT[-1][4], ["I", "II", "III", "IV", "V"][z], maxed, _c(maxed * cl_), RAT[-1][3],
                       maxtc, _c(maxtc * cl_), RAT[-1][0], RAT[-1][1], raw * cl_ * f_, raw * cl_ * f_ * tc3))
    bone = PR.get("Ingredient_Bone_Fragment", 0.0)
    rows.append("0.4.10 (Bone Fragments only): a new island = %.0f / h = %s coins; 0.4.11 Zone 1 new Small = %s coins (%.2fx); manual kills on an island: ordinary kill XP + drops, at most the player's own kill speed (no walking: ~2-2.5x the open world's 150 an hour); the spawn lid 300 an hour at Small level 0 x the island's mobs at once / respawn (x30 at a maxed Large)"
                % (cage[0] * 60.0, _c(cage[0] * 60.0 * bone), _c(RAT[0][2]), RAT[0][2] / (cage[0] * 60.0 * bone) if bone else 0.0))
    for r_ in rows:
        print("BAL " + r_)
        K.notes.append(r_)
    if PR:
        K.check(0.7 <= RAT[0][2] / (cage[0] * 60.0 * bone) <= 1.5, "BAL Skyy 'new islands stay the same': a new Zone 1 Small island's Soul Cage I sells for %.2fx its 0.4.10 Bone Fragments" % (RAT[0][2] / (cage[0] * 60.0 * bone)))
        for z_, r_ in enumerate(RAT):   # 0.4.11 retune: Skyy 2026-10-24 popup COMBAT SHARD PACE "About 1-1.5x (Recommended)"
            K.check(1.0 <= r_[0] <= 1.5, "BAL Skyy 'About 1-1.5x': Zone %d fully maxed (Large, 5 Soul Cages of its tier, Time Compressor III) = %.2fx the coins of fighting it" % (z_ + 1, r_[0]))
            K.check(0.5 <= r_[3] <= 0.75, "BAL Zone %d maxed without the Time Compressor = %.2fx (half: the compressor is part of the target)" % (z_ + 1, r_[3]))
            K.check(r_[4] < 0.25, "BAL Zone %d: a new island stays far below fighting (%.3fx)" % (z_ + 1, r_[4]))
    else:
        K.notes.append("BAL no Bazaar price file (live products.properties) - coin checks skipped")
    K.check(int(Cfg.CB_MAXH) == 2 * BM.KILLS_H, "BAL the spawner's lid at Small level 0 = 2 x the model's open-world kills an hour (%d)" % int(Cfg.CB_MAXH))
    K.save()


# ---------------------------------------------------------------------------------------------------------- G: the land
SOLIDLESS = ("Furniture_Crude_Torch", "Plant_Reeds_Marsh", "Plant_Cactus_1", "Plant_Fern_Forest", "Plant_Bramble_Dead_Lavathorn", "Plant_Reeds_Lava")


def _id(m, x, y, z):
    o = m.get("%d,%d,%d" % (x, y, z))
    return "" if o is None else str(o)


def _solid(i):
    return i != "" and i not in SOLIDLESS and "Leaves" not in i and "Crystal" not in i


def _stand(m, x, y, z):
    """feet at y: a solid floor below, 2 free cells (torches / plants / crystals do not block)"""
    a, b = _id(m, x, y, z), _id(m, x, y + 1, z)
    return _solid(_id(m, x, y - 1, z)) and not _solid(a) and not _solid(b) and "Fence" not in a and "Fence" not in b


def _walk(m, start, goal_y, box):
    """BFS over standable feet cells (4 neighbours, up 1 / down up to 3): can a player get from start to any cell at feet height goal_y?"""
    from collections import deque
    seen = {start}
    dq = deque([start])
    x0, x1, z0, z1 = box
    while dq:
        x, y, z = dq.popleft()
        if y == goal_y:
            return True
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, nz = x + dx, z + dz
            if not (x0 <= nx <= x1 and z0 <= nz <= z1):
                continue
            for dy in (0, 1, -1, -2, -3):
                ny = y + dy
                if dy == 1 and _solid(_id(m, x, y + 2, z)):
                    continue
                if (nx, ny, nz) in seen or not _stand(m, nx, ny, nz):
                    continue
                if dy < 0 and any(_solid(_id(m, nx, yy, nz)) for yy in range(ny + 2, y + 2)):
                    continue
                seen.add((nx, ny, nz))
                dq.append((nx, ny, nz))
                break
    return False


def run_land(out, jar, scratch, _home):
    K = HK.Child(out)
    L = _L(os.path.join(scratch, "g"), K)
    Geo, Fill, St = L["ShGeo"], L["ShFill"], L["ShStore"]
    pal = ["Soil_Grass", "Soil_Sand", "Soil_Grass_Cold", "Soil_Ash", "Rock_Magma_Cooled"]
    walk_ok, walk_bad, gap_bad, spot_stats, floors, lows, feats = 0, [], [], [], [], [], []
    for z in range(5):
        for slot in range(5):
            for sz in (1, 2, 3):
                key = _key()
                p = _prof(L, key, [(slot, z, sz, (0, 0, 0))])
                m, want = _paint(L, p)
                cx, cz = _ctr(L, slot)
                h = [6, 10, 14][sz - 1]
                floors.append(_id(m, cx + 3, Y, cz - 4) == pal[z] or _id(m, cx - 4, Y, cz + 3) == pal[z])
                low = sum(1 for i in range(want.size()) if int(want.get(i)[1]) < 96)
                lows.append((z, slot, sz, low))
                # nothing that stands (blocks a walk) on a walkway cell of this island
                for dx in range(-h, h + 1):
                    for dz in range(-h, h + 1):
                        if not bool(Geo.gap(slot, dx, dz)):
                            continue
                        for y in (Y + 1, Y + 2):
                            i = _id(m, cx + dx, y, cz + dz)
                            if _solid(i) or "Fence" in i:
                                gap_bad.append((z, slot, sz, dx, dz, y, i))
                # the rise / forest only from Medium on
                tall = sum(1 for dx in range(-h, h + 1) for dz in range(-h, h + 1) if _solid(_id(m, cx + dx, Y + 1, cz + dz)))
                feats.append((sz, tall))
                # the spawn spots: standable after the paint
                for part in (0, 1):
                    sp = [int(x) for x in Geo.cspots(slot, sz, part)]
                    fy = Y + 1 if part == 0 else int(Geo.CAVE_FY) + 1
                    pts = [(sp[2 * i], sp[2 * i + 1]) for i in range(len(sp) // 2)]
                    ok = sum(1 for dx, dz in pts if _stand(m, cx + dx, fy, cz + dz))
                    spot_stats.append((z, slot, sz, part, len(pts), ok))
                if sz == 3:
                    sq = int(Geo.quads(slot)[0])
                    sx, szc = cx + 9 * int(Geo.QX[sq]), cz + 9 * int(Geo.QZ[sq])
                    # start on the island floor next to the fence's way in (ring 2, positions 0 / 1 / 15 = the corner (-2,-2))
                    start = (sx - 3, Y + 1, szc - 3)
                    if not _stand(m, *start):
                        start = (sx - 2, Y + 1, szc - 3)
                    box = (cx - h, cx + h, cz - h, cz + h)
                    if _stand(m, *start) and _walk(m, start, int(Geo.CAVE_FY) + 1, box):
                        walk_ok += 1
                    else:
                        walk_bad.append((z, slot, start, _stand(m, *start)))
    Fill.TEST_BLOCKS = None
    K.check(all(floors), "G every zone's floor block (grass / sand / cold grass / ash / cooled magma): %d of %d" % (sum(floors), len(floors)))
    K.check(all((low > 0) == (sz == 3) for _z, _s, sz, low in lows), "G the cavern (cells under y 96, chunk section 2) only at Large: %s" % [l for l in lows if (l[3] > 0) != (l[2] == 3)][:4])
    K.eq(gap_bad[:5], [], "G nothing that blocks a walk stands on a bridge's walkway (trees, rise, torches, fence)")
    small = [t for s, t in feats if s == 1]
    med = [t for s, t in feats if s == 2]
    K.check(max(small) <= 2 and min(med) >= 12, "G Small = a flat arena (only the totem); Medium + the rise and trees (%d .. %d / %d .. %d)" % (min(small), max(small), min(med), max(med)))
    K.check(walk_ok == 25 and not walk_bad, "G the spiral stair is WALKED from the island floor to the cavern floor on every zone x slot (%d ok): %s" % (walk_ok, walk_bad[:3]))
    up = [s for s in spot_stats if s[3] == 0]
    lo = [s for s in spot_stats if s[3] == 1 and s[2] == 3]
    K.check(all(s[5] >= 0.7 * s[4] and s[4] > 0 for s in up), "G upper spawn spots standable (>= 70 %%, trees / rise / torches take the rest): worst %s" % (min(up, key=lambda s: s[5] / max(1.0, s[4])),))
    K.check(all(s[5] >= 0.95 * s[4] and s[4] > 300 for s in lo), "G cavern spawn spots standable (>= 95 %%): worst %s" % (min(lo, key=lambda s: s[5] / max(1.0, s[4])),))
    K.check(all(s[4] == 0 for s in spot_stats if s[3] == 1 and s[2] < 3), "G no cavern spots below Large")
    # grow in place: Small -> Medium -> Large on ONE map = the fresh Large (the stair / cavern / features), the spots still standable
    from jpype import JClass
    key = _key()
    p = _prof(L, key, [(1, 0, 1, (5, 5, 5))])
    m = JClass("java.util.HashMap")()
    Fill.TEST_BLOCKS = m
    for sz in (1, 2, 3):
        St.LOCK.lock()
        try:
            p.setProperty("combat.i1.size", str(sz))
        finally:
            St.LOCK.unlock()
        Fill.paintY(None, Geo.region(p, CK), None, None)
    m2, _w = _paint(L, p)
    Fill.TEST_BLOCKS = None
    cx, cz = _ctr(L, 1)
    diff = [(k_, str(m.get(k_)), str(m2.get(k_))) for k_ in [str(x) for x in m2.keySet()] if str(m.get(k_)) != str(m2.get(k_))]
    extra = [(k_, str(m.get(k_))) for k_ in [str(x) for x in m.keySet()] if m2.get(k_) is None]
    K.check(not diff and all(v in SOLIDLESS for _k, v in extra), "G grown in place = a fresh Large (only small-size torches may stay): %d different, extra %s" % (len(diff), extra[:4]))
    sq = int(Geo.quads(1)[0])
    sx, szc = cx + 9 * int(Geo.QX[sq]), cz + 9 * int(Geo.QZ[sq])
    K.check(_walk(m, (sx - 3, Y + 1, szc - 3), int(Geo.CAVE_FY) + 1, (cx - 14, cx + 14, cz - 14, cz + 14)) or _walk(m, (sx - 2, Y + 1, szc - 3), int(Geo.CAVE_FY) + 1, (cx - 14, cx + 14, cz - 14, cz + 14)),
            "G the grown island's stair is walkable too")
    K.check(int(Geo.CAVE_FY) > int(Y - 20) and int(Geo.CAVE_FY) >> 5 == 2, "G the cavern floor (y %d) is above the void rescue line and in section 2" % int(Geo.CAVE_FY))
    K.save()


# ---------------------------------------------------------------------------------------------------------- the simulated world (N, W)
class World(object):
    """a fake entity store for ShFight.TEST: mobs by uuid {role, pos, alive}; logs every op"""

    def __init__(self, L, blocks):
        self.L, self.blocks = L, blocks
        self.mobs, self.log, self.n, self.spawns, self.levels, self.nights, self.restores, self.removed = {}, [], 0, [], {}, [], [], []
        self.roles_ok = None
        self.extra_near = []
        self.restore_held = []

    def fn(self, a):
        from jpype import JArray, JDouble, JObject, JString, JClass
        op = str(a[0])
        Bool = self.L["Bool"]
        if op == "role":
            r = str(a[1])
            return Bool.valueOf(self.roles_ok is None or r in self.roles_ok)
        if op == "spawn":
            self.n += 1
            u = "00000000-0000-0000-0000-%012d" % self.n
            pos = [float(a[2]), float(a[3]), float(a[4])]
            self.mobs[u] = dict(role=str(a[1]), pos=pos, alive=True)
            self.spawns.append((u, str(a[1]), pos))
            return JString(u)
        if op == "info":
            mb = self.mobs.get(str(a[1]))
            if mb is None or not mb["alive"]:
                return None
            return JArray(JDouble)(mb["pos"])
        if op == "remove":
            mb = self.mobs.get(str(a[1]))
            if mb is None or not mb["alive"]:
                return Bool.FALSE
            mb["alive"] = False
            self.removed.append(str(a[1]))
            return Bool.TRUE
        if op == "near":
            x, y, z, r = float(a[1]), float(a[2]), float(a[3]), float(a[4])
            l = JClass("java.util.ArrayList")()
            for u, mb in self.mobs.items():
                if mb["alive"] and (mb["pos"][0] - x) ** 2 + (mb["pos"][2] - z) ** 2 <= r * r:
                    l.add(JArray(JObject)([JString(u), JString(mb["role"]), JArray(JDouble)(mb["pos"])]))
            return l
        if op == "level":
            self.levels[str(a[1])] = int(a[2])
            return Bool.TRUE
        if op == "night":
            self.nights.append(str(a[1]))
            return Bool.TRUE
        if op == "restore":
            self.restores.append(str(a[1]))
            self.restore_held.append(self.L["ShFight"].NIGHT.get(a[1]) is not None)   # fix: the hold must be gone before the real time is sent
            return Bool.TRUE
        return None

    def alive(self, role_set=None):
        return [u for u, mb in self.mobs.items() if mb["alive"] and (role_set is None or mb["role"] in role_set)]


def _players(L, ps):
    """ps = [(uuid str, (x, y, z), member)] -> the Java list ShFight.tickWorld takes"""
    from jpype import JArray, JObject, JDouble, JClass
    l = JClass("java.util.ArrayList")()
    for u, q, mem in ps:
        l.add(JArray(JObject)([L["UUID"].fromString(u), JArray(JDouble)([float(q[0]), float(q[1]), float(q[2])]), L["Bool"].valueOf(bool(mem)), None]))
    return l


def run_night(out, jar, scratch, _home):
    K = HK.Child(out)
    L = _L(os.path.join(scratch, "n"), K)
    Fi, Cfg, Geo = L["ShFight"], L["ShCfg"], L["ShGeo"]
    wd = World(L, None)
    Fi.TEST = L["PyFn"](wd.fn)
    cx, cz = _ctr(L, 0)
    farm = (int(Geo.ox(FK)) + 0.5, Y + 1, 3.5)
    t0 = 1790000000000
    A, Bp = OWNER, MEMBER
    UU = L["UUID"]
    ua = UU.fromString(A)
    wid, wid2 = UU.fromString("77777777-0000-0000-0000-000000000001"), UU.fromString("77777777-0000-0000-0000-000000000002")
    Fi.TEST_WID = wid
    Fi.NIGHT.clear()
    n1 = int(Fi.night(None, "w1", _players(L, [(A, (cx + 2, Y + 1, cz + 2), True), (Bp, farm, True)]), t0))
    K.check(n1 == 1 and wd.nights == [A], "N a player in the Combat region gets the night (the farm one does not): %s" % wd.nights)
    Fi.night(None, "w1", _players(L, [(A, (cx + 3, Y + 1, cz + 2), True)]), t0 + 999)
    K.check(wd.nights == [A], "N not again before 1 s")
    Fi.night(None, "w1", _players(L, [(A, (cx + 3, Y + 1, cz + 2), True)]), t0 + 1000)
    K.check(wd.nights == [A, A], "N again every second (fix: the vanilla TimePacketSystem's 1 s broadcast rate)")
    # fix (critic r5combat2): ShNightF drops the world's own time packets for a held player - same world, our night < 3.5 s old, never ours
    hb = UU.fromString(Bp)
    K.check(bool(Fi.holds(ua, wid, t0 + 1000)) and bool(Fi.holds(ua, wid, t0 + 4499)) and not bool(Fi.holds(ua, wid, t0 + 4500)),
            "N the hold: the world's time packet is dropped while our night is under 3.5 s old")
    K.check(not bool(Fi.holds(ua, wid2, t0 + 1100)) and not bool(Fi.holds(hb, wid, t0 + 1100)) and not bool(Fi.holds(ua, None, t0 + 1100)) and not bool(Fi.holds(None, wid, t0 + 1100)),
            "N ... only in that world (another world's time passes), never for a player not held (the farm one)")
    Fi.OWN.set(L["Bool"].TRUE)
    try:
        own = bool(Fi.holds(ua, wid, t0 + 1100))
    finally:
        Fi.OWN.remove()
    K.check(not own, "N ... our own night packets always pass (the OWN mark on the sending thread)")
    from jpype import JClass
    NF = JClass(PKG + "ShNightF")
    K.check(not bool(NF().test(None, None)) and NF.class_.getInterfaces()[0].getName() == "com.hypixel.hytale.server.core.io.adapter.PlayerPacketFilter",
            "N ShNightF is the outbound PlayerPacketFilter (a null player / packet passes, never throws)")
    Fi.night(None, "w1", _players(L, [(A, farm, True)]), t0 + 4000)
    K.check(wd.restores == [A] and Fi.NIGHT.get(ua) is None and wd.restore_held == [False] and not bool(Fi.holds(ua, wid, t0 + 4001)),
            "N into another region of the same world = the hold released FIRST, then the real time back (%s)" % wd.restore_held)
    Fi.night(None, "w1", _players(L, [(A, (cx, Y + 1, cz), True)]), t0 + 5000)
    Fi.night(None, "w1", _players(L, []), t0 + 6000)
    K.check(wd.restores == [A] and Fi.NIGHT.get(L["UUID"].fromString(A)) is None, "N gone from the world = forgotten, no packet (the next world sends its own time)")
    Fi.night(None, "w1", _players(L, [(A, (cx, Y + 1, cz), True)]), t0 + 7000)
    Cfg.CB_NIGHT = False
    Fi.night(None, "w1", _players(L, [(A, (cx, Y + 1, cz), True)]), t0 + 8000)
    Cfg.CB_NIGHT = True
    K.check(wd.restores == [A, A] and wd.restore_held == [False, False], "N the switch off = the real time back at once (hold released first)")
    Fi.night(None, "w1", _players(L, [(A, (cx, Y + 1, cz), True)]), t0 + 9000)
    K.check(Fi.NIGHT.get(ua) is not None, "N back in the Combat region: held again")
    Fi.flushAll(None, "0b0b-nobody")
    K.check(Fi.NIGHT.get(ua) is not None, "N a flush of another world keeps this world's holds")
    Fi.night(None, "test", _players(L, [(A, (cx, Y + 1, cz), True)]), t0 + 10000)
    Fi.flushAll(None, "0b0b-nobody")
    K.check(Fi.NIGHT.get(ua) is None, "N the world's last player left (flushAll): its night holds go (fix: no leftover entries)")
    Fi.TEST_WID = None
    from jpype import JClass
    Inst = JClass("java.time.Instant")
    for ms in (0, 3600000 * 5, 3600000 * 23 + 59999, 86400000 * 400 + 1):
        mid = int(Fi.midnight(Inst.ofEpochMilli(t0 + ms)).toEpochMilli())
        K.check(mid > t0 + ms and mid - (t0 + ms) <= 86400000 and mid % 86400000 == 0, "N the next midnight (game time %d): %d" % (ms, mid))
    Fi.TEST = None
    K.save()


def _wsetup(L, key, slots, scratch_tag):
    """profile + painted blocks + simulated world"""
    p = _prof(L, key, slots)
    L["_k"] = key
    m, _w = _paint(L, p)
    wd = World(L, m)
    Fi = L["ShFight"]
    Fi.TEST = L["PyFn"](wd.fn)
    Fi.SEED = 12345
    for mp in (Fi.MOBS, Fi.DUE, Fi.EMPTY, Fi.SCAN, Fi.MOVED, Fi.BUCKET, Fi.NIGHT):
        mp.clear()
    return p, m, wd


def run_spawn(out, jar, scratch, _home):
    K = HK.Child(out)
    L = _L(os.path.join(scratch, "w"), K)
    Fi, Cfg, Geo, Fill, St, Cb = L["ShFight"], L["ShCfg"], L["ShGeo"], L["ShFill"], L["ShStore"], L["ShCombat"]
    p, m, wd = _wsetup(L, _key(), [(0, 0, 1, (0, 0, 0))], "a")
    cx, cz = _ctr(L, 0)
    t = [1790000000000]
    pos = [cx + 3.5, Y + 1.0, cz + 2.5]

    def tick(ps=None, dt=1000, who=None):
        t[0] += dt
        pl = _players(L, ps if ps is not None else [(OWNER, tuple(pos), True)])
        return int(Fi.tickWorld(None, L["_k"], St.get(L["_k"]), pl, t[0]))

    def step():
        pos[0] = cx + 3.5 if pos[0] != cx + 3.5 else cx - 2.5   # a real move (> 1.5 blocks)

    def settle(n=45):
        for _i in range(n):
            step()
            tick()
    n = [tick() for _ in range(6)]
    K.eq(n, [1, 1, 1, 0, 0, 0], "W Zone 1 Small: one mob a second up to Mobs at once = 3")
    al = wd.alive()
    K.eq(len(al), 3, "W 3 alive")
    K.check(all(1 <= wd.levels[u] <= 3 for u in al), "W levels inside Lv 1-3: %s" % [wd.levels[u] for u in al])
    pool = [str(x) for x in Cb.roles(0, 1, 0)]
    K.check(all(wd.mobs[u]["role"] in pool for u in al), "W roles from the Zone 1 Small pool")

    def far_ok():
        return all(math.dist(sp, pos) >= 6.0 - 1e-9 for _u, _r, sp in wd.spawns[-1:])
    K.check(all(_stand(m, int(math.floor(sp[0])), int(sp[1]), int(math.floor(sp[2]))) for _u, _r, sp in wd.spawns), "W every spawn on a standable spot of our floor")
    # a death: its place comes back after exactly 30 s
    wd.mobs[al[0]]["alive"] = False
    tick()                                       # the death is seen: its place is due 30 s from now
    seq = [tick(dt=1000) for _ in range(29)]
    K.check(sum(seq) == 0, "W not before the respawn time (30 s at Spawn speed 0)")
    step()
    r30 = tick(dt=1000)
    K.check(r30 == 1 and len(wd.alive()) == 3, "W the dead mob's place spawns again after 30 s (%d)" % r30)
    # the spawns never closer than 6 to any player: a player standing in the middle of the floor + a second (co-op) player elsewhere
    ok_far = True
    for _i in range(40):
        u0 = wd.alive()[0]
        wd.mobs[u0]["alive"] = False
        step()
        before = len(wd.spawns)
        tick(ps=[(OWNER, tuple(pos), True), (MEMBER, (cx - 4.5, Y + 1.0, cz - 4.5), True)], dt=31000)
        for _u, _r, sp in wd.spawns[before:]:
            if math.dist(sp, pos) < 6.0 or math.dist(sp, (cx - 4.5, Y + 1.0, cz - 4.5)) < 6.0:
                ok_far = False
    K.check(ok_far, "W 40 respawns: never within combat.minDist (6) of a player")
    # Mobs at once 5 -> 8 at once
    settle()
    K.eq(len(wd.alive()), 3, "W settled at 3 alive")
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.amt", "5")
    finally:
        St.LOCK.unlock()
    step()
    n = sum(tick() for _ in range(8))
    K.check(n == 5 and len(wd.alive()) == 8, "W Mobs at once 5 = 8 alive (%d new, %d alive)" % (n, len(wd.alive())))
    # Mob level 5 = Lv 5-8; Spawn speed 5 = 15 s
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.deco", "5")
        p.setProperty("combat.i0.irr", "5")
    finally:
        St.LOCK.unlock()
    u0 = wd.alive()[0]
    wd.mobs[u0]["alive"] = False
    tick()
    seq = [tick() for _ in range(14)]
    step()
    r15 = tick()
    newest = wd.spawns[-1][0]
    K.check(sum(seq) == 0 and r15 == 1, "W Spawn speed 5 = back after 15 s")
    K.check(5 <= wd.levels[newest] <= 8, "W Mob level 5 = Lv 5-8 (%d)" % wd.levels[newest])
    # AFK: no move for 300 s = no new mobs; one step = spawns again
    settle()
    u0 = wd.alive()[0]
    wd.mobs[u0]["alive"] = False
    afk0 = int(Fi.AFK.get())
    got = [tick(dt=20000) for _ in range(16)]   # 320 s without moving
    K.check(sum(got) == 1 and got[0] == 0 and got[1] == 1 and int(Fi.AFK.get()) > afk0, "W AFK: the place came back once (moved within 300 s), then nothing without a move (%s)" % got)
    u0 = wd.alive()[0]
    wd.mobs[u0]["alive"] = False
    a = [tick(dt=20000) for _ in range(3)]
    K.check(sum(a) == 0, "W AFK: still nothing while standing still")
    step()
    K.check(tick() == 1, "W one step = spawns again")
    # the leash: a mob carried off the island is removed (and its place comes back)
    u0 = wd.alive()[0]
    wd.mobs[u0]["pos"] = [cx + 30.0, Y + 1.0, cz]
    tick()
    K.check(u0 in wd.removed and u0 not in wd.alive(), "W a mob 30 blocks off its island is removed (no drops)")
    u1 = wd.alive()[0]
    wd.mobs[u1]["pos"] = [cx, Y - 40.0, cz]
    tick()
    K.check(u1 in wd.removed, "W a mob falling under the island is removed")
    # a visitor alone never spawns mobs; the owner leaves: after 30 s everything is removed
    n_vis = sum(tick(ps=[(VISITOR, tuple(pos), False)], dt=1000) for _ in range(5))
    K.check(n_vis == 0, "W a visitor alone: no spawns")
    al0 = list(wd.alive())
    tick(ps=[], dt=20000)
    K.check(all(u in wd.alive() for u in al0), "W nobody there 20 s: the mobs still stand (30 s grace)")
    tick(ps=[], dt=11000)
    K.check(not wd.alive(), "W nobody there 30 s: every mob removed (%d)" % len(wd.alive()))
    # the hourly lid: 10 an hour -> the bucket (18) runs dry, then about one every 6 minutes
    Cfg.CB_MAXH = 10
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.irr", "5")
    finally:
        St.LOCK.unlock()
    Fi.BUCKET.clear()
    tot = 0
    for _i in range(60):
        for u in wd.alive():
            wd.mobs[u]["alive"] = False
        step()
        tot += tick(dt=16000)
    lid = tot
    Cfg.CB_MAXH = 300
    lx = float(Cb.lidX(1, int(str(p.getProperty("combat.i0.amt") or "0")), 5))
    K.check(lx > 1.5 and 18 + int(16.0 * 10 * lx / 60.0) - 1 <= lid <= 18 + int(16.0 * 10 * lx / 60.0) + 3,
            "W combat.maxPerHour 10 x the island's lid factor %.2f (Spawn speed 5): 16 min of instant kills spawn the 18-mob burst + ~%d more (%d)" % (lx, int(16.0 * 10 * lx / 60.0), lid))
    # Large: the cavern mobs only below, the upper ones only above, the split cap
    p, m, wd = _wsetup(L, _key(), [(0, 0, 3, (5, 0, 5))], "b")
    cx, cz = _ctr(L, 0)
    t[0] += 1000
    up = [str(x) for x in Cb.roles(0, 3, 0)]
    low = [str(x) for x in Cb.roles(0, 3, 1)]
    pos[:] = [cx + 4.5, Y + 1.0, cz + 6.5]
    for _i in range(20):
        step()
        tick()
    K.check(len(wd.alive()) == 9 and all(wd.mobs[u]["role"] in up for u in wd.alive()), "W Large, a player on top: 9 (of 18) upper mobs, upper roles only (%d)" % len(wd.alive()))
    sq = int(Geo.quads(0)[0])
    pos[:] = [cx - 6.5 * int(Geo.QX[sq]), int(Geo.CAVE_FY) + 1.0, cz + 0.5]
    for _i in range(30):
        pos[0] += 2.0 if _i % 2 == 0 else -2.0
        tick()
    cav = [u for u in wd.alive() if wd.mobs[u]["pos"][1] < Y - 2]
    K.check(len(cav) == 9 and all(wd.mobs[u]["role"] in low for u in cav), "W Large, a player in the cavern: 9 cavern mobs, cavern roles only (%d)" % len(cav))
    K.check(all(10 <= wd.levels[u] <= 13 for u in cav), "W Large at Mob level 0 = Lv 10-13: %s" % sorted(set(wd.levels[u] for u in cav)))
    K.check(all(_stand(m, int(math.floor(wd.mobs[u]["pos"][0])), int(wd.mobs[u]["pos"][1]), int(math.floor(wd.mobs[u]["pos"][2]))) for u in cav), "W cavern spawns on the cavern floor")
    up_alive = [u for u in wd.alive() if wd.mobs[u]["pos"][1] >= Y]
    K.check(len(up_alive) == 9, "W the upper mobs stay while the cavern is visited... until 30 s without anyone on top")
    tick(dt=31000)
    K.check(not [u for u in wd.alive() if wd.mobs[u]["pos"][1] >= Y] and len([u for u in wd.alive() if wd.mobs[u]["pos"][1] < Y - 2]) == 9, "W ... then the upper ones go, the cavern ones stay")
    # leftovers after a restart: pool roles in the box are counted (cap kept), other roles ignored, the excess removed
    p, m, wd = _wsetup(L, _key(), [(0, 0, 1, (0, 0, 0))], "c")
    cx, cz = _ctr(L, 0)
    for i, role in enumerate(("Skeleton_Fighter", "Wolf_Black", "Skeleton_Fighter", "Skeleton_Fighter", "Kweebec_Seedling")):
        wd.mobs["11111111-0000-0000-0000-00000000000%d" % i] = dict(role=role, pos=[cx - 3.5 + i, Y + 1.0, cz - 3.5], alive=True)
    pos[:] = [cx + 4.5, Y + 1.0, cz + 4.5]
    tick()
    left = [u for u in wd.alive() if u.startswith("11111111")]
    K.check(int(Fi.ADOPTED.get()) >= 3 and len(left) == 4 and "11111111-0000-0000-0000-000000000004" in left and not wd.spawns,
            "W 4 leftover pool mobs + a non-pool NPC: the cap (3) adopted, the 4th pool mob removed, the other NPC untouched, nothing new spawned (%s)" % left)
    # spawning off / a paused shard / the island gone: removed
    Cfg.CB_SPAWN = False
    tick()
    Cfg.CB_SPAWN = True
    K.check(not [u for u in wd.alive() if wd.mobs[u]["role"] != "Kweebec_Seedling"], "W Combat islands spawn mobs OFF: every tracked mob removed")
    for _i in range(4):
        step()
        tick()
    K.check(len(wd.alive()) == 4, "W ... ON again: back to 3 (+ the other NPC)")
    St.LOCK.lock()
    try:
        p.setProperty("combat.paused", "1")
    finally:
        St.LOCK.unlock()
    tick()
    K.check(len(wd.alive()) == 1, "W a picked-up (paused) shard: removed")
    St.LOCK.lock()
    try:
        p.remove("combat.paused")
    finally:
        St.LOCK.unlock()
    for _i in range(4):
        step()
        tick()
    St.LOCK.lock()
    try:
        p.remove("combat.i0.type")
    finally:
        St.LOCK.unlock()
    tick()
    K.check(len(wd.alive()) == 1, "W an island that is gone: its mobs removed")
    # Zone 3 levels + an unknown role skipped
    p, m, wd = _wsetup(L, _key(), [(2, 2, 2, (2, 3, 0))], "d")
    cx, cz = _ctr(L, 2)
    pos[:] = [cx + 4.5, Y + 1.0, cz + 4.5]
    wd.roles_ok = set(str(x) for x in Cb.roles(2, 2, 0)) - {"Wolf_White"}
    for _i in range(12):
        step()
        tick()
    al = wd.alive()
    K.check(len(al) == 10 and all(48 <= wd.levels[u] <= 51 for u in al), "W Zone 3 Medium, Mob level 3: Lv 48-51 (8-11 + 40): %s" % sorted(set(wd.levels[u] for u in al)))
    K.check(not any(wd.mobs[u]["role"] == "Wolf_White" for u in al), "W a role the server does not know is skipped")
    K.check(bool(Fi.has(L["_k"])) and not bool(Fi.has(_key())), "W has(): this profile still has tracked combat mobs (another does not)")
    pre = L["_k"] + "|"
    K.check(bool(Fi.tracked(pre, al[0])) and not bool(Fi.tracked(_key() + "|", al[0])), "W tracked(): only this profile's own lists are read (fix: other worlds' lists belong to their threads)")
    K.check(any(str(k_).startswith(pre) for k_ in Fi.SCAN.keySet()), "W the leftover scan times exist while the island is visited")
    nfl = int(Fi.flushAll(None, L["_k"]))
    K.check(not any(str(k_).startswith(pre) for k_ in Fi.SCAN.keySet()), "W flushAll also drops the profile's scan times (fix: no leftover entries)")
    K.check(nfl == 10 and not wd.alive() and not bool(Fi.has(L["_k"])), "W the world's last player left (ShTick -> flushAll): all %d removed at once, never left in the chunks" % nfl)
    Fi.TEST = None
    Fill.TEST_BLOCKS = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- B: buy / subs / grow / collect
def run_buy(out, jar, scratch, _home):
    K = HK.Child(out)
    L = _L(os.path.join(scratch, "b"), K)
    from jpype import JInt
    St, Isl, Mth, Core, Door, Cfg, Cb = (L[n] for n in ("ShStore", "ShIsl", "ShMath", "ShCore", "ShDoor", "ShCfg", "ShCombat"))
    inv, count, UUID, coins, PyFn = (L[n] for n in ("inv", "count", "UUID", "coins", "PyFn"))
    ou = UUID.fromString(OWNER)
    W = "skyy-island-" + OWNER
    Core.NOW_TEST = 1790000000000
    lv = {"class": 10}
    Isl.LEVEL_TEST = PyFn(lambda a: JInt(lv.get(str(a[2]), 99)))
    Door.door(ou, OWNER, "combat", W, 5, 6, 7)
    p = St.get(OWNER)
    K.check(bool(Mth.hasIsland(CK, p, 0)) and str(p.getProperty("combat.i0.type")) == "skeleton", "B the Combat door gives Zone 1 (the old skeleton key)")
    cs = inv(27, 27, 9)
    coins["bal"] = 10000000
    T48._fill(L, cs, [("Ingredient_Hide_Medium", 200), ("Ingredient_Ice_Essence", 100), ("Ingredient_Bone_Fragment", 900), ("Ingredient_Void_Essence", 60),
                      ("Ingredient_Life_Essence", 60), ("Ingredient_Water_Essence", 60)])
    r = str(Core.buyIsland(ou, OWNER, CK, 1, cs))
    K.check(r.startswith("-") and "class level 20" in r and "you: 10" in r, "B Zone 2 below class level 20: refused (%s)" % r)
    K.eq(count(cs, "Ingredient_Hide_Medium"), 200, "B ... nothing taken")
    lv["class"] = -1
    r = str(Core.buyIsland(ou, OWNER, CK, 1, cs))
    K.check(r.startswith("-") and "no class levels" in r and count(cs, "Ingredient_Hide_Medium") == 200, "B no skills mod (class level -1): Zone 2 stays locked (fix: never open): %s" % r)
    lv["class"] = 10
    r = str(Core.buyIsland(ou, OWNER, CK, 2, cs))
    K.check(r.startswith("-") and ("Zone 2" in r or "class level" in r), "B Zone 3 before Zone 2: refused (%s)" % r)
    lv["class"] = 25
    b0 = coins["bal"]
    r = str(Core.buyIsland(ou, OWNER, CK, 1, cs))
    want_c = int(Isl.coins(float(Cfg.BUY_H), float(Cfg.curve(int(Isl.band(5))))))
    K.check(r.startswith("+") and "Zone 2" in r, "B Zone 2 bought at class level 25: %s" % r)
    K.eq((b0 - coins["bal"], count(cs, "Ingredient_Hide_Medium")), (want_c, 136), "B ... coins (0.5 h at the T5 band) + 64 Medium Hide taken")
    s2 = int(Isl.slotOf(CK, p, int(Isl.LAD0[CK]) + 1))
    K.check(s2 == 1 and str(p.getProperty("combat.i1.size")) == "1", "B ... a Small Zone 2 island in the next slot")
    r = str(Core.buyIsland(ou, OWNER, CK, 2, cs))
    K.check(r.startswith("-") and "40" in r, "B Zone 3 at class level 25: refused (needs 40): %s" % r)
    # the 3 combat subs on Zone 1 (combat.mat.*: Bone Fragments + Void / Life / Water Essence, x the level)
    v0, l0, w0, b0_ = (count(cs, i) for i in ("Ingredient_Void_Essence", "Ingredient_Life_Essence", "Ingredient_Water_Essence", "Ingredient_Bone_Fragment"))
    rs = [str(Core.buySub(ou, OWNER, CK, 0, w, cs)) for w in range(3)]
    K.check(all(x.startswith("+") for x in rs) and "Mobs at once 1/5" in rs[0] and "Mob level 1/5" in rs[1] and "Spawn speed 1/5" in rs[2], "B the 3 combat subs bought: %s" % rs)
    K.eq((v0 - count(cs, "Ingredient_Void_Essence"), l0 - count(cs, "Ingredient_Life_Essence"), b0_ - count(cs, "Ingredient_Bone_Fragment")),
         (0, 0, 16 + 16 + 8), "B ... Small level 1 = 16 / 16 / 8 Bone Fragments (no essence at Small)")
    St.LOCK.lock()
    try:
        for f_ in ("amt", "deco"):
            p.setProperty("combat.i0.%s" % f_, "5")
    finally:
        St.LOCK.unlock()
    r = str(Core.grow(ou, OWNER, CK, 0, cs))
    K.check(r.startswith("-") and "Mobs at once 5/5" in r and "Mob level 5/5" in r and "Spawn speed 1/5" in r, "B Grow names the combat subs: %s" % r)
    # COLLECT: the stored count = the pool's drops
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.stored", "500")
        p.setProperty("combat.i0.last", str(1790000000000))
        p.setProperty("combat.i1.stored", "0")
    finally:
        St.LOCK.unlock()
    cs2 = inv(27, 27, 27, 27)
    want = Cb.split(0, 1, 500, "Ingredient_Bone_Fragment")
    wid, wq = [str(x) for x in want[0]], [int(x) for x in want[1]]
    r = str(Core.collect(ou, OWNER, CK, 0, cs2))
    got = [count(cs2, i) for i in wid]
    K.check(r.startswith("+Collected") and got == wq and sum(got) == 500, "B Collect gives the Zone 1 Small pool's drops, 500 in all: %s / %s" % (list(zip(wid, got)), r[:160]))
    K.check(" XP" not in r, "B ... still no XP at Collect (Skyy G9: drops only)")
    K.eq(int(Mth.stored(CK, p, 0)), 0, "B ... the island is empty")
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.stored", "5000")
    finally:
        St.LOCK.unlock()
    cs3 = inv(len(wid))
    r = str(Core.collect(ou, OWNER, CK, 0, cs3))
    tot = sum(count(cs3, i) for i in wid)
    K.check(r.startswith("+") and 0 < tot < 5000 and int(Mth.stored(CK, p, 0)) == 5000 - tot, "B a small inventory (one slot a kind): what did not fit stays (%d given, %d stay): %s" % (tot, int(Mth.stored(CK, p, 0)), r[:200]))
    w3 = Cb.split(0, 1, tot, "Ingredient_Bone_Fragment")
    K.check([count(cs3, str(i)) for i in w3[0]] == [int(x) for x in w3[1]], "B ... and what was given is EXACTLY the mix of that count (fix: a full inventory never picks the drops)")
    # the critic's case: every drop's stack full but one empty slot, collected again and again - always the exact mix, never the rare one alone
    bad_mix, tot_all, st0 = [], 0, 3000
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.stored", str(st0))
    finally:
        St.LOCK.unlock()
    for rep_ in range(6):
        cs5 = inv(len(wid) + 1)
        T48._fill(L, cs5, [(i_, 100) for i_ in wid[:-1]])
        before = [count(cs5, i_) for i_ in wid]
        Core.collect(ou, OWNER, CK, 0, cs5)
        gv = [count(cs5, i_) - b_ for i_, b_ in zip(wid, before)]
        g = sum(gv)
        tot_all += g
        want_ = [int(x) for x in Cb.split(0, 1, g, "Ingredient_Bone_Fragment")[1]]
        if gv != want_:
            bad_mix.append((rep_, gv, want_))
    r = str(Core.collect(ou, OWNER, CK, 0, inv(1)))
    K.check(r.startswith("-Not enough room") and "every kind of drop" in r, "B one free slot for %d kinds of drops: nothing, and the message says why: %s" % (len(wid), r))
    K.check(not bad_mix and int(Mth.stored(CK, p, 0)) == st0 - tot_all, "B 6 Collects with only one free slot: each gives exactly the mix of what it gives, the rest stays stored (%d given; %s)" % (tot_all, bad_mix[:1]))
    St.LOCK.lock()
    try:
        p.setProperty("combat.i1.stored", "300")
    finally:
        St.LOCK.unlock()
    cs4 = inv(27, 27, 27)
    w2 = Cb.split(1, 1, 300, "Ingredient_Hide_Medium")
    r = str(Core.collect(ou, OWNER, CK, 1, cs4))
    K.check(r.startswith("+") and [count(cs4, str(i)) for i in w2[0]] == [int(x) for x in w2[1]], "B Zone 2's Collect = Zone 2's pool drops: %s" % r[:140])
    # fix (critic r5combat2 2nd round): the 0.4.8 map migration never renames a 0.4.6 / 0.4.7 profile's extra Skeleton islands to Zones 2-5
    k6 = _key()
    p6 = _prof(L, k6, [(0, 0, 1, (0, 0, 0)), (2, 0, 1, (0, 0, 0)), (3, 0, 2, (0, 0, 0))])
    St.LOCK.lock()
    try:
        p6.remove("map.done")
        for s_ in (0, 2, 3):
            p6.remove("combat.i%d.amt" % s_)
    finally:
        St.LOCK.unlock()
    St.migrate2(k6, p6)
    K.check(str(p6.getProperty("map.done")) == "1" and [str(p6.getProperty("combat.i%d.type" % s_)) for s_ in (0, 2, 3)] == ["skeleton"] * 3
            and str(p6.getProperty("combat.i2.amt")) == "5", "B the 0.4.8 map migration of a 0.4.6 profile: its 3 Combat islands stay Zone 1 (no free Zones 2-5), Amount 5 as before: %s"
            % [str(p6.getProperty("combat.i%d.type" % s_)) for s_ in (0, 2, 3)])
    Isl.LEVEL_TEST = None
    K.save()


# ---------------------------------------------------------------------------------------------------------- K: config
def run_config(out, jar, scratch, _home):
    from jpype import JClass
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    K = HK.Child(out)
    home = os.path.join(scratch, "k", "mods", "Skyy_SkyyShards")
    os.makedirs(home)
    Cfg, path = T42.kit_home(home)
    Cfg.loadCfg(True)
    lines = open(os.path.join(home, "config.properties"), "rb").read().replace(b"\r\n", b"\n").decode("latin-1").split("\n")
    want = ["combat.nightHold=true", "combat.spawn=true", "combat.zoneLevel.2=20", "combat.zoneLevel.5=80", "combat.cap.small=3,4,5,6,7,8",
            "combat.cap.large=12,13,14,16,17,18", "combat.level.small=1-3,2-4,2-5,3-6,4-7,5-8", "combat.level.large=10-13,11-14,12-16,13-17,15-19,16-20",
            "combat.respawn.small=30,27,24,21,18,15", "combat.respawn.large=10,9,8,8,7,6", "combat.levelOffset=0,20,40,60,80", "combat.maxPerHour=300",
            "combat.afkSec=300", "combat.minDist=6", "combat.cagePct=100,68,39,82,68", "combat.cageGrowth=54"] + ["combat.pool.%d.%s=" % (z, pt) for z in range(1, 6) for pt in ("small", "medium", "large", "lower")]
    K.eq([w for w in want if not any(l.startswith(w) for l in lines)], [], "K a fresh file holds every combat row")
    open(os.path.join(home, "config.properties"), "a", encoding="latin-1").write(
        "\ncombat.cap.small=2,3\ncombat.level.medium=junk\ncombat.respawn.large=4\ncombat.zoneLevel.3=0\ncombat.levelOffset=0,5\ncombat.pool.1.small=Rat\ncombat.nightHold=false\n"
        "combat.level.small=4-2,7\ncombat.cagePct=100,50\ncombat.cageGrowth=300\n")
    Cfg.loadCfg(False)
    K.check([int(x) for x in Cfg.CB_CAGE] == [100, 50, 50, 50, 50] and int(Cfg.CB_GROW) == 100, "K combat.cagePct: a short list repeats; combat.cageGrowth above 100 = 100")
    K.check([int(x) for x in Cfg.CB_CAP][:6] == [2, 3, 3, 3, 3, 3] and [int(x) for x in Cfg.CB_LO][6:12] == [5, 6, 7, 8, 9, 10]
            and [int(x) for x in Cfg.CB_RSP][12:] == [4] * 6 and int(Cfg.CB_ZLV[1]) == 0 and [int(x) for x in Cfg.CB_OFF] == [0, 5, 5, 5, 5]
            and str(Cfg.CB_POOL[0]) == "Rat" and not bool(Cfg.CB_NIGHT), "K hand edits: short lists repeat, a junk range = the default (+ WARN), 0 = any class level")
    K.check([int(x) for x in Cfg.CB_LO][:6] == [4, 7, 7, 7, 7, 7] and [int(x) for x in Cfg.CB_HI][:6] == [4, 7, 7, 7, 7, 7], "K a range lo > hi = lo; a single number = lo-lo")
    rows = dict((str(r[0]), [str(x) for x in list(r)]) for r in JClass(PKG + "CfgRows").header()[7])
    K.check(all(("combat.pool.%d.%s" % (z, pt)) in rows for z in range(1, 6) for pt in ("small", "medium", "large", "lower"))
            and all(x in rows for x in ("combat.nightHold", "combat.spawn", "combat.zoneLevel.2", "combat.cap.medium", "combat.level.large", "combat.respawn.small",
                                        "combat.levelOffset", "combat.maxPerHour", "combat.cagePct", "combat.cageGrowth", "combat.afkSec", "combat.minDist", "combat.mat.cap", "combat.mat.speed")),
            "K the Server Setup rows exist (%d combat rows)" % sum(1 for k in rows if k.startswith("combat.")))
    K.save()


# ---------------------------------------------------------------------------------------------------------- GT: the gate
def run_gate(out, jar, scratch, _home):
    K = HK.Child(out)
    L = _L(os.path.join(scratch, "gt"), K)
    G, Cb, Fi, Geo = L["ShGate"], L["ShCombat"], L["ShFight"], L["ShGeo"]
    from jpype import JArray, JObject, JString
    W1 = "skyy-shard-" + OWNER
    u = L["UUID"].fromString(MEMBER)
    from jpype import JClass
    now = int(JClass("java.lang.System").currentTimeMillis())
    Cb.HERE.clear()
    gi = G()
    ask = lambda w_, who: gi.apply(JArray(JObject)([JString(w_), JString("hurt"), JString(""), who]))
    a0 = ask(W1, u)
    K.check(a0 is not None and not bool(a0), "GT hurt: a player the combat tick has not seen in the Combat region = no (fix: every other NPC in a shard world stays safe)")
    wd = World(L, None)
    Fi.TEST = L["PyFn"](wd.fn)
    cx, cz = _ctr(L, 0)
    try:
        Fi.tickWorld(None, OWNER, None, _players(L, [(MEMBER, (cx + 2, Y + 1, cz + 2), True), (VISITOR, (int(Geo.ox(FK)) + 0.5, Y + 1, 3.5), True)]), now)
    finally:
        Fi.TEST = None
    a1 = G.allowed("test", "hurt", "", u)
    a2 = G.allowed(W1, "hurt", "", u)
    v = L["UUID"].fromString(VISITOR)
    K.check(not bool(Cb.mayHurt(W1, u, now)) and bool(Cb.mayHurt("test", u, now)) and bool(Cb.mayHurt("test", u, now + 3000)) and not bool(Cb.mayHurt("test", u, now + 3001))
            and not bool(Cb.mayHurt("test", v, now)), "GT the tick marks a player in the Combat region (that world only, 3 s); the one on the farm is not marked")
    K.check(a1 is None and a2 is not None and not bool(a2), "GT ... and the gate asks it: another world's mark never counts")
    Cb.mark(u, W1, now)
    a3 = ask(W1, u)
    a4 = ask(W1, None)
    K.check(a3 is not None and bool(a3) and a4 is not None and not bool(a4), "GT hurt = yes for a player in the Combat region (the bridge's 4th value), no without a player")
    b = G.allowed("skyy-island-" + OWNER, "hurt", "")
    c = G.allowed("skyy-shard-" + OWNER, "break", "Rock_Stone")
    K.check(b is None and c is not None and not bool(c), "GT unanswered outside shard worlds; breaking stone still no")
    Cb.HERE.clear()
    K.save()


# ---------------------------------------------------------------------------------------------------------- O2: the Combat Map tab, walked in order
def run_order2(out, jar, scratch, _home):
    K = HK.Child(out)
    L, ou, W, p, lvd = T410._world(os.path.join(scratch, "o2"), K)
    from jpype import JInt
    Page, Isl, St, Door = L["ShPage"], L["ShIsl"], L["ShStore"], L["ShDoor"]
    lv = {"class": 30}
    Isl.LEVEL_TEST = L["PyFn"](lambda a: JInt(lv.get(str(a[2]), 9)))
    Door.door(ou, OWNER, "combat", W, 5, 6, 7)
    bad, n, txts = [], 0, set()
    for zi in range(5):
        for sz in (1, 2, 3):
            for sub in (0, 3, 5):
                St.LOCK.lock()
                try:
                    for z2 in range(5):
                        s_ = z2
                        if z2 <= zi:
                            p.setProperty("combat.i%d.type" % s_, "skeleton" if z2 == 0 else "zone%d" % (z2 + 1))
                            p.setProperty("combat.i%d.size" % s_, str(sz))
                            p.setProperty("combat.i%d.last" % s_, "1790000000000")
                            for f_ in ("amt", "deco", "irr"):
                                p.setProperty("combat.i%d.%s" % (s_, f_), str(sub))
                        else:
                            p.remove("combat.i%d.type" % s_)
                finally:
                    St.LOCK.unlock()
                for cl in (5, 30, 99):
                    lv["class"] = cl
                    for sel in range(5):
                        for zoom in (0, 2):
                            pg = Page(ou, W)
                            pg.kind = CK
                            pg.view = 0
                            pg.tab = 1
                            pg.zoom = zoom
                            pg.act("mn%d" % sel, None, None)
                            r = T410.full(pg)
                            n += 1
                            if r["miss"] or r["unbound"]:
                                bad.append(("zone %d size %d sub %d class %d sel %d zoom %d" % (zi + 1, sz, sub, cl, sel, zoom), r["miss"][:2], r["unbound"][:2]))
                            for t_ in [str(x) for x in pg.mTx]:
                                if t_:
                                    txts.add(t_)
    K.check(not bad, "O2 the Combat Map tab: %d builds walked in order, every selector there when its command runs: %s" % (n, bad[:2]))
    K.check(any(t_.startswith("Next: 3 -> 4 mobs at once") for t_ in txts) and any(t_.startswith("Next: Lv ") for t_ in txts) and any(t_.startswith("Next: every ") for t_ in txts),
            "O2 the combat sub texts show on the island view")
    K.check(any("Needs class level 40" in t_ for t_ in txts) and any("kinds of mobs" in t_ for t_ in txts), "O2 the buy view's class gate + the pool line")
    K.check(any(t_ == "Zone 3 Island" for t_ in txts), "O2 the island name = Zone N")
    Isl.LEVEL_TEST = None
    Page.TEST_INV = None
    K.save()


def run_players48(out, jar, scratch, home):
    """the map migration's collect.log line names the RUNNING version: 0.4.11 now"""
    SUP(("P one collect.log line with the Undo",), lambda: T48.run_players(out, jar, os.path.join(scratch, "p48"), home))
    d_ = json.load(open(out))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = d_["ok"], d_["fails"], d_["notes"]
    log = os.path.join(scratch, "p48", "p", "x", "collect.log")
    if not os.path.isfile(log):
        log = os.path.join(scratch, "p48", "x", "collect.log")
    txt = open(log, encoding="utf8").read() if os.path.isfile(log) else ""
    K.check("map migration (SkyyShards 0.4.11) 0a0a0a0a-1111-2222-3333-000000000001" in txt and "Undo:" in txt,
            "P the map migration's collect.log line (running version 0.4.11) with the Undo")
    K.save()


# ---------------------------------------------------------------------------------------------------------- D: live
def run_live411(out, jar, scratch, home):
    T410.run_live410(out, jar, scratch, home)


EXPECT = {   # 0.4.10 -> 0.4.11, checked by hand 2026-10-24: the version texts (CfgFile / CfgFn / CfgRows, ShStore log lines, the ready line) + the round
    "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
    "ShCfg": ["+f CB_AFK", "+f CB_CAGE", "+f CB_CAP", "+f CB_DIST", "+f CB_HI", "+f CB_LO", "+f CB_MAT", "+f CB_MAXH", "+f CB_NIGHT", "+f CB_OFF",
              "+f CB_POOL", "+f CB_RSP", "+f CB_SPAWN", "+f CB_ZLV", "+f DEF_CB_CAP", "+f DEF_CB_MAT", "+f DEF_CB_OFF", "+f DEF_CB_POOL", "+m rangesOf", "+f CB_SKIP", "+f CB_SPB", "+f DEF_CB_SKIP", "+m cbSpawnX", "+m skipOf", "+f DEF_CB_CAGE", "+f CB_GROW", "+m cbOut",
              "~<clinit>", "~m loadCfg", "~m writeDefaults"],
    "ShCore": ["~m buyIsland0", "~m buySub0", "~m collect0", "~m grow0"],
    "ShFill": ["~m paintAsync"], "ShGate": ["+m allowed", "~m allowed", "~m apply"],   # + allowed(world, action, block, who): the attacker
    "ShGeo": ["+f CAVE_FY", "+f CAVE_R", "+f CAVE_TY", "+f CCAVE", "+f CCORN", "+f CCRYS", "+f CFENCE", "+f CFLOOR", "+f CLAVA", "+f CLEAF", "+f CPLANT",
              "+f CRIM", "+f CRISE", "+f CSPOT", "+f CTOP", "+f CTORCH", "+f CTRUNK", "+f QX", "+f QZ", "+f TRL", "+f TRM", "+m cavern", "+m combat",
              "+m cspots", "+m ctree", "+m inQ", "+m isLava", "+m nearShaft", "+m qGap", "+m quads", "+m stair", "~<clinit>", "~m island"],
    "ShIsl": ["~<clinit>", "~m mult", "~m rank", "~m subName", "~m tname"],   # mult: x the combat spawn factor   # rank: the ladder count TN (a constant) is 5 bigger
    "ShMap": ["~<clinit>"],                                         # the Combat map: 5 discs
    "ShPage": ["+f cLv", "~m fill", "~m fillMap"],
    "ShStore": ["~m migrate", "~m migrate2", "~m save"], "ShTick": ["~m run"], "ShTotem": ["~m islandRate", "~m workerRate"], "SkyyShardsPlugin": ["~m setup", "~m shutdown"]}
_ORIG_COMPARE = T49._ORIG_COMPARE


def _compare(out, jar, old_jar, pkg, expect, added, removed=()):
    """the map files: every one byte-identical except the Combat map's (5 islands now); the classes as EXPECT"""
    import zipfile as _zf
    cps = []
    for j, tag in ((jar, VERSION), (old_jar, "old")):
        cp = os.path.join(SCRATCH, "compare-%s.jar" % tag)
        with _zf.ZipFile(j) as zi, _zf.ZipFile(cp, "w", _zf.ZIP_DEFLATED) as zo:
            for n_ in zi.namelist():
                if not T49.MAP_ENTRY.match(n_):
                    zo.writestr(n_, zi.read(n_))
        cps.append(cp)
    with _zf.ZipFile(jar) as a, _zf.ZipFile(old_jar) as b:
        ma = dict((n_, a.read(n_)) for n_ in a.namelist() if T49.MAP_ENTRY.match(n_))
        mb = dict((n_, b.read(n_)) for n_ in b.namelist() if T49.MAP_ENTRY.match(n_))
    ch = sorted(n_ for n_ in set(ma) | set(mb) if ma.get(n_) != mb.get(n_))
    combat = all(("Combat" in n_) or re.search(r"/K5Z\dK\.txt$", n_) for n_ in ch)
    assert combat and ch, "C the map files differ outside the Combat map: %s" % [n_ for n_ in ch if "Combat" not in n_][:5]
    print("C. map files: %d of %d differ, all the Combat map's (%s ...)" % (len(ch), len(ma), ch[:3]))
    _ORIG_COMPARE(out, cps[0], cps[1], pkg, expect, added, removed)


HK.run_compare = _compare
SUPC = ()


def _p(fn, sup=()):
    return lambda out, jar, scratch, home: SUP(tuple(sup), lambda: fn(out, jar, os.path.join(scratch, "p410"), home))


if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShCombat", "ShFight", "ShNightF"],
           phases=[("static", run_static),
                   ("exec48", _p(T49.run_exec48)), ("exec47", _p(T49.run_exec47)), ("exec46", _p(T49.run_exec46)), ("centre47", _p(T49.run_centre47)),
                   ("config48", _p(T49.run_config48)), ("mig48", _p(T410.run_mig48)), ("players48", _p(run_players48)), ("geo48", _p(T49.run_geo48)),
                   ("config49", _p(T49.run_config)), ("mig49", _p(T49.run_mig)), ("exec49", _p(T49.run_exec)), ("page49", _p(T49.run_page)),
                   ("width", _p(T49.run_width)), ("order", _p(T410.run_order)), ("flows", _p(T410.run_flows)),
                   ("zones", run_zones), ("balance", run_balance), ("land", run_land), ("night", run_night), ("spawn", run_spawn), ("buy", run_buy), ("config", run_config),
                   ("gate", run_gate), ("order2", run_order2), ("live", run_live411)],
           script=__file__, live=(T46.LIVE_SH, "mods/Skyy_SkyyShards"))
