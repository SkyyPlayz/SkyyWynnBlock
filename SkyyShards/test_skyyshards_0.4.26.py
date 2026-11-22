"""Harness for SkyyShards 0.4.26 (shard clicker 4: the Combat town defense - tools/shards_0_4_26_patch.py, on top of 0.4.25).
Build first:
    python tools/shards_0_4_26_patch.py && python SkyyShards/build_skyyshards_0.4.26.py
    python SkyyShards/test_skyyshards_0.4.26.py [--keep]

  S26  static   the patch re-runs to identical bytes; header / VERSION / ready line; no new registerSystem / registerCommand; line endings kept; the jar
                ships the older clicker pictures + the town pictures (our own, no vanilla file); the town tables = Assets.zip (MaxHealth order, the
                vanilla drop averages, Trork_Warrior in Zone 1)
  TF   fight    EXECUTED the weapon tiers; Town level / kinds / at once maths; the monster choice (deterministic, easiest kinds first, every kind in
                turn at Town level 15); the click cap; no weapon; a kill = EXACT loot (a seeded Random replayed in Python) into combat.i0.drops (saved),
                the class XP (25 % of health x 0.6 x the level factor, to the ACTIVE class skill), the respawn wait; the tier gate (3 up refused, no
                hit; 2 up = click.twoTierUp); Warrior strength x2; storage full; room for 1 (the rarest first); a refused save (nothing added, the
                monster stands again, no arrival); switched off; no class = no XP; click.fight.cageSkip; the memory is the town's own
  TU   upgrade  EXECUTED Warrior strength (Tree size's coins + Void Essence; nothing taken when short; a stale double click buys once; the highest
                level); the page rows ku0..ku5 (Town level / Warrior speed / Monster level bought with the level shown, a stale level refused,
                Spirit warriors -> the Totems tab, Town size waits for 5 / 5 / 5); a STALE TOWN (another zone in the slot / another profile) = no
                fight, no buy
  TZ   zones    EXECUTED the Combat zone locks (class 19 refused for Zone 2, 20 opens); the town map (locks, header, Open, Buy); an owned town in a
                locked zone stays open + playable
  TK   memkey   EXECUTED the fix: Foraging / Mining damage + XP fractions sit under <profile>|<kind>|<slot> / <uuid>|<profile>|<kind> (a tree and a
                node in the same slot number never share)
  TC   collect  EXECUTED the grid shows the click loot; a cell / Collect all pay it (the collection credit), no XP at Collect
  TP   page     the Combat footer has Shard clicker; kopen -> view 5 town; every size walks clean (the monster squares carry kt<spot>:<slot>, the
                monster pictures, the town island, no weather / decorations), the title, the rows, the element count, the packet; a kill on the page
                (status, pop, the slain picture); the map; the info line; switched off = no button; Foraging / Mining / Farming unchanged
  then 0.4.25's phases (farm25 .. page25), 0.4.24's, 0.4.23's and the older ones on THIS jar (their tree / node memory lines now expect
  <profile>|<kind>|<slot>), A verify, C compare, AA audit, live START TWICE on a scratch copy of the live data
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.26"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "fight1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.25.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.25.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_26_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

# the 0.4.25 harness (it loads 0.4.24 -> 0.4.23 -> ... older): its version moves to this one in memory; the lines that read the Foraging / Mining
# memory under <profile>|<slot> now read <profile>|<kind>|<slot> (0.4.26 fix)
EXTRA23 = [('d0_ = float(Ck.state(JString(OWNER + "|0"))[0][0])', 'd0_ = float(Ck.state(JString(OWNER + "|1|0"))[0][0])'),
           ('d1_ = float(Ck.state(JString(OWNER + "|0"))[0][0])', 'd1_ = float(Ck.state(JString(OWNER + "|1|0"))[0][0])')]
EXTRA24 = [('d1 = float(Ck.state(JString(OWNER + "|2"))[0][0])', 'd1 = float(Ck.state(JString(OWNER + "|0|2"))[0][0])'),
           ('Ck.accSet(JString(OWNER + "|0"), 0.75)', 'Ck.accSet(JString(OWNER + "|0|0"), 0.75)'),
           ('abs(float(Ck.accGet(JString(OWNER + "|0"))) - 0.75)', 'abs(float(Ck.accGet(JString(OWNER + "|0|0"))) - 0.75)')]
_T25 = open(os.path.join(HERE, "test_skyyshards_0.4.25.py"), encoding="utf8").read()
assert _T25.count('VERSION = "0.4.25"\n') == 1 and _T25.count("FIX24 = [(") == 1 and _T25.count("FIX23 = [(") == 1, "the 0.4.25 harness changed"
_T25 = _T25.replace('VERSION = "0.4.25"\n', 'VERSION = "%s"\n' % VERSION).replace("FIX24 = [(", "FIX24 = EXTRA24 + [(").replace("FIX23 = [(", "FIX23 = EXTRA23 + [(")
_argv = list(sys.argv)
T425 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_25", loader=None))
T425.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.25.py")
T425.__dict__["EXTRA23"] = EXTRA23
T425.__dict__["EXTRA24"] = EXTRA24
exec(compile(_T25, T425.__file__, "exec"), T425.__dict__)
sys.argv[:] = _argv
T424, T423, T422, T421 = T425.T424, T425.T423, T425.T422, T425.T421
T420, T419, T411, T410, T49, T416, T415, T413 = T425.T420, T425.T419, T425.T411, T425.T410, T425.T49, T425.T416, T425.T415, T425.T413
T425.JAR = T424.JAR = T423.JAR = T422.JAR = T421.JAR = T420.JAR = T419.JAR = T420.T418.JAR = T419.T417.JAR = JAR
T425.SCRATCH = T424.SCRATCH = T423.SCRATCH = T422.SCRATCH = T421.SCRATCH = T420.SCRATCH = T419.SCRATCH = T420.T418.SCRATCH = T416.SCRATCH = T415.SCRATCH = T419.T417.SCRATCH = SCRATCH
OWNER, MEMBER = T420.OWNER, T420.MEMBER
MI, FO, FK, CK = 0, 1, 2, 5
T0 = 1790000000000
BONE = "Ingredient_Bone_Fragment"
VOID = "Ingredient_Void_Essence"
CRUDE, IRON_SW, COBALT_SW = "Weapon_Sword_Crude", "Weapon_Sword_Iron", "Weapon_Sword_Cobalt"


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.26 - build script') and 'VERSION = "0.4.26"\n' in g, "S26 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S26 no new %r" % w)
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.26:" in g, "S26 the ready line names the round")
    K.check("if (kd == @PKG@.ShCombat.CK) {   // 0.4.22: the pool count -> its rolled drops" not in o or "isC" in o, "S26 (0.4.25's Combat Collect pays the .drops store)")
    K.check("ROLLBACK 0.4.26 -> 0.4.25 alone: no migration" in g and "its Combat Collect pays .drops (0.4.22)" in g, "S26 the rollback note")
    blk = g[g.index("# ---- 0.4.26 THE COMBAT TOWN (tools/shards_0_4_26_patch.py)"):g.index("# THE CLICK: Object[]{ status")]
    K.check("scheduleAtFixedRate" not in blk and "sendUpdate" not in blk, "S26 no periodic page update (HANDOFF section 2)")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S26 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S26 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S26 jar newer than the script, the script newer than the patch")
    with zipfile.ZipFile(jar) as z:
        names = z.namelist()
        clk = [n for n in names if n.startswith("Common/UI/Custom/SkyyShards/Map/Clk") and n.endswith("@2x.png")]
        t = [n for n in clk if re.search(r"/Clk(T(Mon\d+|Slain|Isl\d|Map\d)|UpT(Str|Lvl|Spd|Mob))@2x\.png$", n)]
        nmon = len([n for n in t if "/ClkTMon" in n])
        K.check(len(clk) == 66 + 43 + 34 + len(t) and len(t) == nmon + 1 + 3 + 5 + 4 and nmon >= 20 and all(z.read(n)[:8] == b"\x89PNG\r\n\x1a\n" for n in clk),
                "S26 66 + 43 + 34 + %d clicker pictures (%d monster looks)" % (len(t), nmon))
        import serverjar as _SJ
        az = zipfile.ZipFile(_SJ.assets_zip())
        van = set(az.getinfo(n).CRC for n in az.namelist() if n.lower().endswith(".png"))
        K.check(not any(z.getinfo(n).CRC in van for n in t), "S26 no town picture is a vanilla file (CRC)")
    K.save()


def _vanilla_hp():
    """role -> MaxHealth (Modify.MaxHealth / MaxHealth / the Reference's) from Assets.zip"""
    import serverjar as _SJ
    az = zipfile.ZipFile(_SJ.assets_zip())
    roles = dict((n.rsplit("/", 1)[1][:-5], n) for n in az.namelist() if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))

    def hp(r, d=0):
        j = json.loads(az.read(roles[r]).decode("utf-8-sig"))
        for v in ((j.get("Modify") or {}).get("MaxHealth"), j.get("MaxHealth")):
            if isinstance(v, (int, float)) and v > 0:
                return int(v)
        ref = j.get("Reference")
        return hp(ref, d + 1) if d < 4 and isinstance(ref, str) and ref in roles else 100
    return hp, roles


def _town(L, p, size=1, amt=0, ml=0, sp=0, stored=0, ns=None, extra=(), totems=1):
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        for k_ in list(p.stringPropertyNames()):
            if str(k_).startswith("combat."):
                p.remove(k_)
        for s, ty, sz in [(0, "skeleton", size)] + list(extra):
            p.setProperty("combat.i%d.type" % s, ty); p.setProperty("combat.i%d.size" % s, str(sz)); p.setProperty("combat.i%d.last" % s, str(T0))
            p.setProperty("combat.i%d.stored" % s, "0")
        p.setProperty("combat.i0.stored", str(stored)); p.setProperty("combat.i0.amt", str(amt)); p.setProperty("combat.i0.deco", str(ml))
        p.setProperty("combat.i0.irr", str(sp))
        if ns is not None:
            p.setProperty("combat.i0.nsize", str(ns))
        if totems:
            p.setProperty("combat.i0.totems", "soul_cage:1:::0:cb0001")
        p.setProperty("combat.auto", "1"); p.setProperty("combat.paused", "0"); p.setProperty("combat.storage", "5")
        p.setProperty("combat.placed", L["W_"] + "|1|2|3")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def _env(scratch, K, name, cls="Combat.Warrior", clv=30):
    from jpype import JClass, JString, JInt, JArray
    L, ou, W_, p, lv, got = T425._env(scratch, K, name)
    lv["class"] = clv
    T411.T48.add_items([(BONE, 100), (VOID, 64), (CRUDE, 1), (IRON_SW, 1), (COBALT_SW, 1), ("Weapon_Axe_Lead_SkyWynn", 1), ("Ingredient_Fabric_Scrap_Linen", 100),
                        ("Ingredient_Hide_Medium", 100), ("Ingredient_Life_Essence", 100),
                        ("Ingredient_Water_Essence", 100), ("Skyy_Ench_Bone", 64)])
    L["ShCombat"] = JClass(PKG + "ShCombat")
    Obj = JClass("java.lang.Object")
    st = {"cls": cls, "lv": clv, "xps": [], "refuse": False, "asked": 0}

    def run(a):
        if str(a[1]) == "class":
            if st["cls"] is None:
                return None
            return JArray(Obj)([JInt(st["lv"]), JInt(0), JInt(0), JInt(0), JInt(0), JString(st["cls"])])
        return JArray(Obj)([JInt(st["lv"])])
    L["br"].put("skill:fn:run", L["PyFn"](run))

    def xp_add(a):
        st["asked"] += 1
        if st["refuse"]:   # fixer: SkyySkills' default bridge.addxp.skills refuses class skills
            return L["Bool"].FALSE
        got["xp"] += int(a[2])
        st["xps"].append((str(a[1]), int(a[2])))
        return L["Bool"].TRUE
    L["fns"].put("skill:fn:addxp", L["PyFn"](xp_add))
    L["ShCombat"].LVL.clear()
    L["tst"] = st
    return L, ou, W_, p, lv, got


def _drops(p, slot=0):
    return T425._drops(p, slot, "combat")


def _loot(Ck, Cb, Cfg, gi, r):
    """a kill's loot replayed on a java.util.Random r: each "id:avg" = the whole part + one more at the rest's chance (rnd only when there is a
    rest); combat.cageSkip items out while click.fight.cageSkip is on -> [(id, q)] in T_DROP order"""
    out = []
    for part in str(Ck.T_DROP[gi]).split(","):
        i, v = part.rsplit(":", 1)
        v = float(v)
        if not v > 0 or (bool(Cfg.TF_SKIP) and bool(Cb.skip(i))):
            out.append((i, 0))
            continue
        w = int(math.floor(v + 1e-9))
        fr = v - w
        out.append((i, w + (1 if fr > 1e-9 and float(r.nextDouble()) < fr else 0)))
    return out


def run_fight(out, jar, scratch, _home):
    from jpype import JString, JDouble, JClass, JLong, JInt
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "tf")
    M, St, Core, Cfg, Ck, Isl, Cb = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShCombat"]
    _town(L, p)
    now = [T0]
    key = OWNER + "|5|0"

    def adv(ms):
        now[0] += ms
        Core.NOW_TEST = now[0]

    def ft(spot=0, hand=CRUDE, slot=0):
        r = Ck.chop(ou, JString(OWNER), CK, slot, spot, JString(hand) if hand else None)
        return str(r[0]), str(r[1])

    K.eq(int(Ck.TK), CK, "TF ShClk.TK = the Combat kind")
    # the tables = Assets.zip: each zone's kinds in MaxHealth order, Rat first in Zone 1, Trork_Warrior (Skyy's "trolls") in Zone 1, the drops
    hp, roles = _vanilla_hp()
    off = [int(x) for x in Ck.T_OFF]
    rows = [(str(Ck.T_ROLE[i]), int(Ck.T_HP[i]), int(Ck.T_RANK[i])) for i in range(len(Ck.T_ROLE))]
    K.check(len(off) == 6 and all(off[z + 1] - off[z] >= 8 for z in range(5)), "TF 5 zones of kinds: %s" % off)
    K.check(all(h == hp(r) for r, h, _ in rows), "TF every kind's health = Assets.zip's MaxHealth (Modify / its Reference)")
    K.check(all([h for _, h, _ in rows[off[z]:off[z + 1]]] == sorted(h for _, h, _ in rows[off[z]:off[z + 1]]) and [k_ for _, _, k_ in rows[off[z]:off[z + 1]]] == list(range(off[z + 1] - off[z]))
                for z in range(5)), "TF ... each zone in difficulty order (health), ranks 0..n-1")
    z1 = [r for r, _, _ in rows[off[0]:off[1]]]
    K.check(z1[0] == "Rat" and "Trork_Warrior" in z1 and z1.index("Wolf_Black") < z1.index("Bear_Grizzly") and z1[-1] in ("Skeleton_Burnt_Praetorian", "Golem_Firesteel", "Spider", "Void_Spectre"),
            "TF Zone 1: rats first, wolves before bears, Trork in, the big ones last: %s" % z1)
    sf = z1.index("Skeleton_Fighter") + off[0]
    dsf = dict((x.rsplit(":", 1)[0], float(x.rsplit(":", 1)[1])) for x in str(Ck.T_DROP[sf]).split(","))
    K.check(abs(dsf.get(BONE, 0) - 1.5) < 1e-9 and abs(dsf.get("Ingredient_Fabric_Scrap_Linen", 0) - 1.5) < 1e-9, "TF the Skeleton Fighter's loot = its vanilla DropList on average (1.5 Bone + 1.5 Linen): %s" % dsf)
    K.eq(str(Ck.T_NAME[off[0] + z1.index("Wolf_Black")]), "Black Wolf", "TF the names read well (Black Wolf)")
    # the weapon tiers
    K.eq([int(Ck.weapTier(JString(x))) if x else int(Ck.weapTier(None)) for x in (CRUDE, IRON_SW, "Weapon_Axe_Lead_SkyWynn", COBALT_SW, "Weapon_Bow_Weird", "Tool_Pickaxe_Copper", None)],
         [1, 2, 5, 7, 1, 0, 0], "TF the weapon tiers (tier_tags; the metal word; a tool / bare hands = 0)")
    # Town level, kinds, monsters at once
    K.eq([int(Ck.townLv(s, a)) for s, a in ((1, 0), (1, 5), (2, 0), (2, 3), (3, 5), (9, 9))], [0, 5, 5, 8, 15, 15], "TF Town level = (size - 1) x 5 + Mobs at once")
    n1 = off[1] - off[0]
    K.eq([int(Ck.kindsAt(0, t)) for t in (0, 7, 14, 15)], [max(1, -(-n1 * 1 // 16)), -(-n1 * 8 // 16), -(-n1 * 15 // 16), n1], "TF kinds open = ceil(n x (level + 1) / 16), all at 15 (n = %d)" % n1)
    K.eq([int(Ck.atOnce(s, a)) for s, a in ((1, 0), (1, 5), (2, 5), (3, 5))], [3, 8, 12, 18], "TF monsters at once = the world's Mobs at once (3 .. 18)")
    # fixer (fidelity critic 3): a maxed town = EVERY kind of its zone at once (Zones 1-3 have more kinds than the Large Mobs at once 18)
    zns = [off[z + 1] - off[z] for z in range(5)]
    K.eq([int(Ck.atOnceZ(z, 3, 5)) for z in range(5)], [max(18, n_) for n_ in zns], "FIX3 a maxed town's spots = max(Mobs at once 18, the zone's kinds %s)" % zns)
    K.check(max(zns) > 18, "FIX3 ... the case is real: a zone has %d kinds > 18 spots" % max(zns))
    K.eq([int(Ck.atOnceZ(0, s, a)) for s, a in ((1, 0), (1, 5), (2, 5), (3, 4))], [3, 8, 12, int(Ck.atOnce(3, 4))], "FIX3 ... below Town level 15 = the Mobs at once table")
    for z in range(5):
        m_ = int(Ck.atOnceZ(z, 3, 5))
        for n_ in (0, 1, 7):
            g_ = set(int(Ck.roleAt(z, 15, s_, JLong(n_), m_, JString(key))) for s_ in range(m_))
            K.check(g_ == set(range(off[z], off[z + 1])), "FIX3 ... Zone %d maxed, arrivals %d: all %d kinds stand at once on %d spots" % (z + 1, n_, zns[z], m_))
    # the monster choice: deterministic, among the open kinds; at Town level 15 every kind in turn
    k0 = int(Ck.kindsAt(0, 0))
    picks = [int(Ck.roleAt(0, 0, s, JLong(n), 3, JString(key))) for s in range(3) for n in range(30)]
    K.check(all(off[0] <= g < off[0] + k0 for g in picks) and picks == [int(Ck.roleAt(0, 0, s, JLong(n), 3, JString(key))) for s in range(3) for n in range(30)],
            "TF Town level 0: only the %d easiest kinds, the same answer twice" % k0)
    K.eq([int(Ck.roleAt(0, 15, s, JLong(n), 18, JString(key))) - off[0] for s, n in ((0, 0), (5, 0), (0, 1), (3, 2))], [0, 5, 0, 3],
         "TF Town level 15: spot i = kind i (every kind at once - fixer)")
    K.eq(int(Ck.roleAt(3, 15, 13, JLong(1), 18, JString(key))) - off[3], (13 + 18) % (off[4] - off[3]), "FIX3 ... a spot past the zone's kinds takes them in turn")
    # the click cap (a high HP: nothing slain)
    Cfg.TF_HP = 1000
    c0, cap0 = int(Ck.CHOPS.get()), int(Ck.CAPPED.get())
    for _ in range(20):
        ft(spot=1)
    K.eq((int(Ck.CHOPS.get()) - c0, int(Ck.CAPPED.get()) - cap0), (8, 12), "TF the click cap: 8 counted, 12 did nothing")
    K.eq(_drops(p), {}, "TF ... nothing slain yet")
    Cfg.TF_HP = 6
    Cfg.CK_CPS = 1000
    adv(1000)
    s, pp = ft(hand=None)
    K.check(s.startswith("-Hold a weapon"), "TF bare hands: %s" % s)
    s, pp = ft(hand="Tool_Pickaxe_Copper")
    K.check(s.startswith("-Hold a weapon"), "TF a pickaxe is not a weapon: %s" % s)
    # a kill: EXACTLY the replayed loot + the XP
    gi = int(Ck.roleAt(0, 0, 0, JLong(0), 3, JString(key)))
    hpm = float(Ck.monHp(gi))
    K.eq(round(hpm, 6), round(6 * (1 + 0.1 * int(Ck.T_RANK[gi])), 6), "TF the monster's clicks = 6 x (1 + 10 %% x rank %d)" % int(Ck.T_RANK[gi]))
    nclk = int(math.ceil(hpm - 1e-9))
    seed = 4711
    Ck.RND_TEST = JClass("java.util.Random")(JLong(seed))
    xs0 = len(L["tst"]["xps"])
    res = [ft() for _ in range(nclk)]
    Ck.RND_TEST = None
    lt = _loot(Ck, Cb, Cfg, gi, JClass("java.util.Random")(JLong(seed)))
    want = dict((i, q) for i, q in lt if q > 0)
    nm = str(Ck.T_NAME[gi])
    own = int(Cb.ownerLv(JString(OWNER)))
    lvl = (int(Cb.lvLoP(own, 0, 1, 0)) + int(Cb.lvHiP(own, 0, 1, 0))) // 2
    xpw = int(math.floor(float(Ck.killXp(gi, lvl)) * 25 / 100.0 + 1e-9))
    K.check(res[-2][0] == "" and res[-1][0].startswith("+Slew a %s (Lv %d)" % (nm, lvl)), "TF %d clicks slay the %s (Lv %d): %s" % (nclk, nm, lvl, res[-1]))
    K.eq(_drops(p), want, "TF ... EXACTLY the replayed loot into combat.i0.drops")
    disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="utf8").read().replace(chr(92) + ":", ":")
    K.check(not want or "combat.i0.drops=" in disk, "TF ... saved at once")
    K.eq(L["tst"]["xps"][xs0:], [("Combat.Warrior", xpw)] if xpw > 0 else [], "TF ... XP 25 %% of the world's (health %d x 0.6 x the Lv %d factor) = %d to the ACTIVE class skill" % (int(Ck.T_HP[gi]), lvl, xpw))
    K.eq(own, 30, "TF ... the monster level = the owner's class level (combat.levelWithPlayer)")
    K.eq(int(Ck.arrivals(JString(key), 0)), 1, "TF ... the next monster at that spot is another one (arrivals 1)")
    s, pp = ft()
    rs = int(Ck.townRespawnMs(1, 0))
    K.check(rs == 12000 and s == "=A new monster is on its way - 12 s.", "TF a slain monster's place fills after 40 %% of the world's 30 s: %s" % s)
    K.eq([int(Ck.townRespawnMs(1, 5)), int(Ck.townRespawnMs(3, 5))], [6000, 2400], "TF ... Warrior speed (Spawn speed) shortens it: 15 s -> 6 s, Large 6 s -> 2.4 s")
    Cfg.TF_RMIN = 5
    K.eq(int(Ck.townRespawnMs(3, 5)), 5000, "TF ... never below click.fight.minRespawnSec")
    Cfg.TF_RMIN = 2
    adv(12000)
    s, pp = ft()
    K.check(s == "" and pp.endswith(" / " + str(Cfg.dec(JDouble(float(Ck.monHp(int(Ck.roleAt(0, 0, 0, JLong(1), 3, JString(key))))))))), "TF ... after 12 s a new monster stands there: %r" % pp)
    # a spot the town does not have; an empty slot
    s, pp = ft(spot=3)
    K.check(s.startswith("=The page is up to date"), "TF spot 3 (3 at once): %s" % s)
    s, pp = ft(slot=5)
    K.check(s.startswith("-That island is not yours yet"), "TF an empty slot: %s" % s)
    # the tier gate: a Zone 2 town (monster tier 4): a T1 sword = 3 up = refused, no hit; a T2 sword = 2 up = click.twoTierUp a click
    _town(L, p, extra=[(1, "zone2", 1)])
    adv(20000)
    c1, g1 = int(Ck.CHOPS.get()), int(Ck.TGATED.get())
    s, pp = ft(slot=1)
    K.check(s.startswith("-Your Crude Sword (T1) is too weak for the Zone 2 town (T4 monsters)") or (s.startswith("-Your ") and "is too weak for the Zone 2 town (T4 monsters)" in s),
            "TF Zone 2 with a T1 weapon: refused: %s" % s)
    K.check(int(Ck.CHOPS.get()) == c1 and int(Ck.TGATED.get()) == g1 + 1, "TF ... no hit counted")
    s, pp = ft(slot=1, hand=IRON_SW)
    d = float(Ck.state(JString(OWNER + "|5|1"))[0][0])
    K.check(s == "" and abs(d - int(Cfg.CK_UP2) / 100.0) < 1e-9, "TF Zone 2 with a T2 sword (2 up): click.twoTierUp %d %% a click: %s" % (int(Cfg.CK_UP2), d))
    # Warrior strength 5 = +100 %: a T1 sword on Zone 1 hits 2
    _town(L, p, ns=5)
    Ck.TREES.clear(); Ck.TOWN.clear()
    adv(20000)
    s, pp = ft(spot=2)
    K.check(abs(float(Ck.state(JString(key))[0][2]) - 2.0) < 1e-9, "TF Warrior strength 5 (+100 %%): 2 a click: %r" % pp)
    # storage full: nothing happens; room for 1: the rarest first
    _town(L, p)
    Ck.TREES.clear(); Ck.TOWN.clear()
    St.LOCK.lock()
    try:
        lim = int(M.limOf(CK, p, 0))
        p.setProperty("combat.i0.stored", str(lim))
        p.setProperty("combat.i0.last", str(now[0]))
    finally:
        St.LOCK.unlock()
    c2 = int(Ck.CHOPS.get())
    s, pp = ft()
    K.check(s.startswith("-This town's storage is full") and int(Ck.CHOPS.get()) == c2, "TF storage full: nothing happens: %s" % s)
    # room for 1: a Large town at Town level 15 (every kind in turn: spot i = kind i) - the Skeleton Fighter's spot; a seed that drops 2+ items
    _town(L, p, size=3, amt=5)
    Ck.TREES.clear(); Ck.TOWN.clear()
    sfs = z1.index("Skeleton_Fighter")
    gi0 = int(Ck.roleAt(0, 15, sfs, JLong(0), 18, JString(key)))
    K.eq(str(Ck.T_ROLE[gi0]), "Skeleton_Fighter", "TF Town level 15: spot %d = the Skeleton Fighter" % sfs)
    sd = None
    for cand in range(1, 400):
        q_ = _loot(Ck, Cb, Cfg, gi0, JClass("java.util.Random")(JLong(cand)))
        if sum(q for _, q in q_) >= 2:
            sd, lt0 = cand, q_
            break
    if sd is None:
        K.check(False, "TF no seed gives 2+ items for %s" % Ck.T_ROLE[gi0])
    else:
        St.LOCK.lock()
        try:
            lim3 = int(M.limOf(CK, p, 0))
            p.setProperty("combat.i0.stored", str(lim3 - 1))
            p.setProperty("combat.i0.last", str(now[0]))
        finally:
            St.LOCK.unlock()
        Ck.RND_TEST = JClass("java.util.Random")(JLong(sd))
        for _ in range(int(math.ceil(float(Ck.monHp(gi0)) - 1e-9))):
            s, pp = ft(spot=sfs)
        Ck.RND_TEST = None
        first = [i for i, q in lt0 if q > 0][0]
        K.check(_drops(p) == {first: 1} and "did not fit" in s, "TF room for 1: the rarest (%s) first, the status says the rest did not fit: %s" % (first, s))
    # a refused save: nothing added, the monster stands again (one click), no arrival
    _town(L, p)
    Ck.TREES.clear(); Ck.TOWN.clear()
    adv(20000)
    gi0 = int(Ck.roleAt(0, 0, 0, JLong(0), 3, JString(key)))
    nc = int(math.ceil(float(Ck.monHp(gi0)) - 1e-9))
    for _ in range(nc - 1):
        ft()
    St.FAIL_TEST = True
    s, pp = ft()
    St.FAIL_TEST = False
    K.check(s.startswith("-The shard file could not be saved") and _drops(p) == {} and int(Ck.arrivals(JString(key), 0)) == 0, "TF a refused save adds nothing, no arrival: %s" % s)
    s, pp = ft()
    K.check(s.startswith("+Slew a ") and int(Ck.arrivals(JString(key), 0)) == 1, "TF ... the monster stood again: one click slays it: %s" % s)
    # no class chosen yet: no XP (the loot still comes)
    L["tst"]["cls"] = None
    Cb.LVL.clear()
    adv(20000)
    xs1 = len(L["tst"]["xps"])
    gi1 = int(Ck.roleAt(0, 0, 1, JLong(0), 3, JString(key)))
    for _ in range(int(math.ceil(float(Ck.monHp(gi1)) - 1e-9))):
        s, pp = ft(spot=1)
    K.check(s.startswith("+Slew a ") and "(no class chosen yet - no XP)" in s and len(L["tst"]["xps"]) == xs1, "TF no class: no XP: %s" % s)
    L["tst"]["cls"] = "Combat.Warrior"
    Cb.LVL.clear()
    # fixer (critics 1): SkyySkills refuses the class skill (its default bridge.addxp.skills): NOT banked as owed XP, the kill says so, not asked
    # again for 60 s; once SkyySkills takes it, it is paid at once
    def kill_at(sp_):
        g_ = int(Ck.roleAt(0, 0, sp_, Ck.arrivals(JString(key), sp_), 3, JString(key)))
        r_ = None
        for _ in range(int(math.ceil(float(Ck.monHp(g_)) - 1e-9))):
            r_ = ft(spot=sp_)
        return r_[0]
    Ck.NOXP.clear()
    L["tst"]["refuse"] = True
    adv(20000)
    xs2, a2, pr2 = len(L["tst"]["xps"]), L["tst"]["asked"], int(Ck.XPREF.get())
    s = kill_at(2)
    owk = [str(k_) for k_ in p.stringPropertyNames() if str(k_).startswith("owed.xp")]
    disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="utf8").read()
    K.check(s.startswith("+Slew a ") and "(no XP: SkyySkills does not take Warrior XP from shards" in s and "Combat.Warrior" in s and len(L["tst"]["xps"]) == xs2
            and L["tst"]["asked"] == a2 + 1 and int(Ck.XPREF.get()) == pr2 + 1, "FIX1 refused class XP: said, asked once: %s" % s)
    K.check(not owk and "owed.xp" not in disk, "FIX1 ... nothing banked as owed XP (memory %s, file %s)" % (owk, "owed.xp" in disk))
    K.check(not bool(Ck.classXpOk(ou, JString("Combat.Warrior"), JLong(now[0]))) and bool(Ck.classXpOk(ou, JString("Combat.Mage"), JLong(now[0]))),
            "FIX1 ... that player's Warrior XP is not asked for 60 s; another class still is")
    adv(20000)
    s = kill_at(2)
    K.check(s.startswith("+Slew a ") and "(no XP: " in s and L["tst"]["asked"] == a2 + 1, "FIX1 ... a kill 20 s later does not ask SkyySkills again: %s" % s)
    L["tst"]["refuse"] = False
    adv(61000)
    s = kill_at(2)
    K.check(s.startswith("+Slew a ") and " Warrior XP" in s and "(no XP" not in s and len(L["tst"]["xps"]) == xs2 + 1 and len(Ck.NOXP) == 0,
            "FIX1 ... after 60 s SkyySkills is asked again and pays at once: %s" % s)
    # click.fight.cageSkip: a kind whose loot has a Soul Cage-skipped item
    sk = [g for g in range(len(Ck.T_DROP)) if any(bool(Cb.skip(x.rsplit(":", 1)[0])) for x in str(Ck.T_DROP[g]).split(","))]
    K.check(len(sk) > 0, "TF some kinds drop Soul Cage-skipped items (Void Essence / ores / bars): %d" % len(sk))
    if sk:
        g = sk[0]
        Ck.RND_TEST = JClass("java.util.Random")(JLong(3))
        a = Ck.lootOf(g)
        Cfg.TF_SKIP = False
        b = Ck.lootOf(g)
        Cfg.TF_SKIP = True
        Ck.RND_TEST = None
        ia = [(str(x), int(y)) for x, y in zip(a[0], a[1])]
        ib = [(str(x), int(y)) for x, y in zip(b[0], b[1])]
        K.check(all(q == 0 for i, q in ia if bool(Cb.skip(i))) and any(q > 0 for i, q in ib if bool(Cb.skip(i))),
                "TF click.fight.cageSkip on: %s's skipped items give 0; off: they drop (%s)" % (Ck.T_ROLE[g], [x for x in ib if bool(Cb.skip(x[0]))]))
    # switched off
    Cfg.TF_ON = False
    s, pp = ft(spot=2)
    K.check(s.startswith("-The Combat town is switched off"), "TF click.fight.enabled false: %s" % s)
    Cfg.TF_ON = True
    # the memory is the town's own
    K.check(Ck.TREES.containsKey(JString(key)) and not Ck.TREES.containsKey(JString(OWNER + "|0")) and not Ck.TREES.containsKey(JString(OWNER + "|1|0")),
            "TF the town's damage sits under <profile>|5|<slot> only")
    Cfg.CK_CPS = 8
    K.save()


def run_memkey(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "tk")
    Core, Cfg, Ck = L["ShCore"], L["ShCfg"], L["ShClk"]
    T423._foraging(L, p)
    T424._mining(L, p)
    Ck.TREES.clear(); Ck.XPA.clear()
    Cfg.CK_CPS = 1000
    Core.NOW_TEST = T0 + 1000
    Ck.chop(ou, JString(OWNER), FO, 0, 0, JString("Tool_Hatchet_Copper"))
    Ck.chop(ou, JString(OWNER), MI, 0, 0, JString("Tool_Pickaxe_Copper"))
    keys = sorted(str(x) for x in Ck.TREES.keySet())
    K.eq(keys, sorted([OWNER + "|0|0", OWNER + "|1|0"]), "TK Foraging + Mining slot 0 keep their own damage: <profile>|<kind>|<slot>")
    K.check(float(Ck.state(JString(OWNER + "|1|0"))[0][0]) == 1.0 and float(Ck.state(JString(OWNER + "|0|0"))[0][0]) == 1.0, "TK ... one hit each, never added together")
    for _ in range(40):
        Ck.chop(ou, JString(OWNER), FO, 0, 0, JString("Tool_Hatchet_Copper"))
        Ck.chop(ou, JString(OWNER), MI, 0, 0, JString("Tool_Pickaxe_Copper"))
    xk = sorted(str(x) for x in Ck.XPA.keySet())
    K.check(all(x.endswith("|0") or x.endswith("|1") for x in xk) and len(xk) >= 1 and all(x.startswith(str(ou) + "|" + OWNER + "|") for x in xk),
            "TK the XP fractions: <uuid>|<profile>|<kind>: %s" % xk)
    Cfg.CK_CPS = 8
    K.save()


def run_upgrade(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "tu")
    M, St, Core, Cfg, Ck, Isl, Page, Cb = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"], L["ShCombat"]
    coins = L["coins"]
    _town(L, p)
    t0 = int(Isl.LAD0[CK])
    cv = float(Cfg.curve(int(Isl.band(int(Isl.TIER[t0])))))
    c1 = int(Ck.nodeCoins(1, cv))
    m1 = Ck.nodeMats(CK, t0, 1)
    EB = str(Isl.tok(CK, t0, JString("ench")))
    K.check(c1 > 0 and EB == "Skyy_Ench_Bone" and [str(x) for x in m1[0]] == [EB] and [int(x) for x in m1[1]] == [1], "TU Warrior strength 1 costs %d coins + 1 Enchanted Bone (= Tree size's rows)" % c1)
    K.check(all(str(Isl.tok(CK, t0 + z_, JString("ench"))) for z_ in range(5)), "TU ... every zone's town has an Enchanted item: %s" % [str(Isl.tok(CK, t0 + z_, JString("ench"))) for z_ in range(5)])
    cs = L["inv"](10)
    coins["bal"] = c1 - 1
    r = str(Ck.buyNode(ou, JString(OWNER), CK, 0, 0, cs))
    K.check(r.startswith("-You need"), "TU no Enchanted Bone: refused: %s" % r)
    cs[0].addItemStack(L["IS"](EB, 5))
    r = str(Ck.buyNode(ou, JString(OWNER), CK, 0, 0, cs))
    K.check(r.startswith("-You need %s coins" % "{:,}".format(c1)) and int(L["count"](cs, EB)) == 5, "TU not enough coins: nothing taken: %s" % r)
    coins["bal"] = 1000000
    r = str(Ck.buyNode(ou, JString(OWNER), CK, 0, 0, cs))
    K.check(r.startswith("+Warrior strength 1/10 in the Zone 1 town: your clicks hit +20 %"), "TU bought: %s" % r)
    K.check(str(p.getProperty("combat.i0.nsize")) == "1" and int(coins["bal"]) == 1000000 - c1 and int(L["count"](cs, EB)) == 4, "TU ... nsize 1, the coins + 1 Enchanted Bone taken")
    r = str(Ck.buyNode(ou, JString(OWNER), CK, 0, 0, cs))
    K.check(r.startswith("=The page is up to date now") and str(p.getProperty("combat.i0.nsize")) == "1", "TU a stale double click buys once: %s" % r)
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.nsize", "10")
    finally:
        St.LOCK.unlock()
    r = str(Ck.buyNode(ou, JString(OWNER), CK, 0, 10, cs))
    K.check(r.startswith("=Warrior strength is at its highest level"), "TU the highest level: %s" % r)
    Cfg.TF_ON = False
    r = str(Ck.buyNode(ou, JString(OWNER), CK, 0, 10, cs))
    K.check(r.startswith("-The Combat town is switched off"), "TU switched off: %s" % r)
    Cfg.TF_ON = True
    # the page rows: ku0..ku5 with the level shown
    _town(L, p)
    Page.TEST_INV = L["inv"](20)
    for it, q in ((BONE, 100), (VOID, 20), ("Ingredient_Life_Essence", 20), ("Ingredient_Water_Essence", 20), ("Skyy_Ench_Bone", 20)):
        Page.TEST_INV[0].addItemStack(L["IS"](it, q))
    Ck.HAND_TEST = CRUDE
    pg = Page(ou, W_)
    pg.kind = CK
    pg.view = 0
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    bd = T49._build(pg)
    K.eq(int(pg.view), 5, "TU kopen -> the town")
    K.check(all(('"ku%d:' % r_) in bd["datas"].get("#SkyyShKU%dX" % r_, "") for r_ in (0, 1, 2, 3, 5)), "TU the rows' buttons carry ku<row>:<level> (Town size waits)")
    K.check("First Town level, Warrior speed and Monster level 5/5 (0, 0, 0)" == str(pg.ckUpC[4]), "TU Town size waits for 5 / 5 / 5: %s" % pg.ckUpC[4])
    for row, prop in ((1, "combat.i0.amt"), (3, "combat.i0.irr"), (5, "combat.i0.deco")):
        pg.handleDataEvent(None, None, json.dumps({"a": "ku%d:0" % row}))
        K.check(str(p.getProperty(prop)) == "1" and str(pg.stText).startswith(("Mobs at once", "Spawn speed", "Mob level", "Bought")) or str(p.getProperty(prop)) == "1",
                "TU row %d bought its level (%s = %s): %s" % (row, prop, p.getProperty(prop), pg.stText))
        T49._build(pg)
        pg.handleDataEvent(None, None, json.dumps({"a": "ku%d:0" % row}))
        K.check(str(p.getProperty(prop)) == "1" and "up to date" in str(pg.stText), "TU ... a stale level (0) is refused: %s" % pg.stText)
    T49._build(pg)
    K.check(str(pg.ckUpL[1]) == "Lv 1 / 15" and int(pg.ckTn) == 4, "TU Town level 1 / 15: 4 at once now (%s, %d)" % (pg.ckUpL[1], int(pg.ckTn)))
    pg.handleDataEvent(None, None, json.dumps({"a": "ku0:0"}))
    K.check(str(p.getProperty("combat.i0.nsize")) == "1", "TU ku0 = Warrior strength: %s" % pg.stText)
    pg.handleDataEvent(None, None, json.dumps({"a": "ku2:1"}))
    K.check(int(pg.view) == 0 and int(pg.tab) == 3, "TU Spirit warriors -> the Totems tab")
    # a STALE TOWN: another zone in the shown slot / another profile = no fight, no buy
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    T49._build(pg)
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.type", "zone2")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    c0 = int(Ck.CHOPS.get())
    pg.handleDataEvent(None, None, json.dumps({"a": "kt0:0"}))
    K.check(int(Ck.CHOPS.get()) == c0 and "up to date" in str(pg.stText), "TU a stale town: the click does nothing: %s" % pg.stText)
    ns0 = str(p.getProperty("combat.i0.nsize"))
    pg.handleDataEvent(None, None, json.dumps({"a": "ku0:1"}))
    K.check(str(p.getProperty("combat.i0.nsize")) == ns0 and "up to date" in str(pg.stText), "TU ... and no buy: %s" % pg.stText)
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.type", "skeleton")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    T49._build(pg)
    pg.key = "someone-else"
    c0 = int(Ck.CHOPS.get())
    pg.handleDataEvent(None, None, json.dumps({"a": "kt0:0"}))
    K.check(int(Ck.CHOPS.get()) == c0, "TU a profile switch (another key on the page): the click does nothing: %s" % pg.stText)
    Ck.HAND_TEST = None
    K.save()


def run_zones(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "tz")
    M, St, Core, Cfg, Ck, Isl, Page, Cb = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"], L["ShCombat"]
    coins = L["coins"]
    _town(L, p)
    K.eq([int(Cb.need(i)) for i in range(5)], [0, 20, 40, 60, 80], "TZ Combat zones 1..5 open at class level 0 / 20 / 40 / 60 / 80")
    lv["class"] = 19
    cs = L["inv"](20)
    for it, q in ((BONE, 100), (VOID, 20)):
        cs[0].addItemStack(L["IS"](it, q))
    coins["bal"] = 100000000
    r = str(Core.buyIsland(ou, JString(OWNER), CK, 1, cs))
    K.check(r.startswith("-The Zone 2 island needs class level 20 (you: 19)"), "TZ class 19: Zone 2 waits: %s" % r)
    lv["class"] = 20
    r = str(Core.buyIsland(ou, JString(OWNER), CK, 1, cs))
    K.check("needs class level" not in r, "TZ class 20: the lock opens (the cost decides now): %s" % r)
    # an owned town in a locked zone stays open + playable
    _town(L, p, extra=[(2, "zone3", 1)])
    lv["class"] = 10
    Ck.HAND_TEST = COBALT_SW
    pg = Page(ou, W_)
    pg.kind = CK
    pg.view = 0
    pg.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    pg.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pg)
    r_ = T410.full(pg)
    K.check(not r_["miss"] and not r_["unbound"], "TZ the town map walks clean %s %s" % (r_["miss"][:2], r_["unbound"][:2]))
    K.check("ZONE 1 TOWN" in bd["mk"] and "ClkTMap0.png" in bd["mk"] and "ClkTMap4.png" in bd["mk"] and "ClkMap1.png" not in bd["mk"] and "#SkyyShKM1G" not in bd["mk"],
            "TZ ... five towns, one card a zone (cards 0 / 3 / 6 / 9 / 12)")
    K.check(not bool(pg.ckMLock[6]) and str(pg.ckMS[6]) == "Yours - Small" and int(pg.ckMB[6]) == 1, "TZ the owned Zone 3 town in a locked zone: open (%s)" % pg.ckMS[6])
    K.check(bool(pg.ckMLock[9]) and str(pg.ckMS[9]) == "Locked: class level 60" and "#SkyyShKM9Lk" in bd["mk"], "TZ Zone 4 not owned: locked + the lock picture")
    K.check(str(pg.ckZS[1]) == "Locked - class level 20 (you: 10)", "TZ the Zone 2 header: %s" % pg.ckZS[1])
    pg.handleDataEvent(None, None, json.dumps({"a": "km2"}))
    K.check(int(pg.ckMode) == 0 and int(pg.ckSlot) == 2, "TZ Open = that town (slot %s)" % pg.ckSlot)
    T49._build(pg)
    K.check(str(pg.ckChip) == "Zone 3 Town - Small" and str(pg.ckTexA[0]).find("ClkTMon") >= 0, "TZ ... the Zone 3 town shown: %s" % pg.ckChip)
    Cfg.CK_CPS = 1000
    for _ in range(80):
        pg.handleDataEvent(None, None, json.dumps({"a": "kt0:2"}))
        if str(pg.stText).startswith("Slew a"):
            break
    K.check(str(pg.stText).startswith("Slew a"), "TZ ... playable in the locked zone (nothing lost): %s" % pg.stText)
    lv["class"] = 30
    pg.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pg)
    K.check(int(pg.ckNext) == 1 and int(pg.ckMB[3]) == 2 and '"kb1"' in bd["datas"].get("#SkyyShKM3X", ""), "TZ class 30: Zone 2 can be bought from the map (card 3 -> kb1)")
    Cfg.CK_CPS = 8
    Ck.HAND_TEST = None
    K.save()


def run_collect(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "tc")
    M, St, Core, Cfg, Ck = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"]
    _town(L, p)
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.drops", BONE + ":25,Ingredient_Fabric_Scrap_Linen:7")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    g = dict((str(i), int(q)) for i, q in zip(*Core.gridOf(CK, p)))
    K.check(g.get(BONE) == 25 and g.get("Ingredient_Fabric_Scrap_Linen") == 7, "TC the grid shows the click loot: %s" % g)
    K.eq(int(M.usedOf(CK, p, 0)), 32, "TC ... it uses the town's storage")
    cs = L["inv"](5)
    got["coll"].clear(); got["xp"] = 0
    r = str(Core.collectKind(ou, JString(OWNER), CK, BONE, cs))
    K.check(r.startswith("+Collected 25"), "TC a cell click pays the Bone Fragments: %s" % r[:140])
    K.check(int(L["count"](cs, BONE)) == 25 and got["coll"].get(BONE, 0) == 25 and got["xp"] == 0, "TC ... 25 in the inventory, the collection +25, no XP at Collect")
    r = str(Core.collect(ou, JString(OWNER), CK, -1, cs))
    K.check(int(L["count"](cs, "Ingredient_Fabric_Scrap_Linen")) == 7 and p.getProperty("combat.i0.drops") is None, "TC Collect all pays the rest: %s" % r[:120])
    K.save()


def run_page(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "tp")
    M, St, Core, Cfg, Ck, Isl, Page = L["ShMath"], L["ShStore"], L["ShCore"], L["ShCfg"], L["ShClk"], L["ShIsl"], L["ShPage"]
    _town(L, p, stored=12)
    Page.TEST_INV = L["inv"](20)
    Ck.HAND_TEST = None
    pf = Page(ou, W_)
    pf.kind = CK
    pf.view = 0
    pf.handleDataEvent(None, None, json.dumps({"a": "tab0"}))
    bm = T49._build(pf)
    K.check("#SkyyShClk" in bm["mk"] and bm["datas"].get("#SkyyShClk", "").find('"kopen"') >= 0, "TP the Combat footer: Shard clicker -> kopen")
    pf.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    K.eq(int(pf.view), 5, "TP kopen -> the town (view 5)")
    for sz in (1, 2, 3):
        St.LOCK.lock()
        try:
            p.setProperty("combat.i0.size", str(sz)); p.setProperty("combat.i0.amt", "5"); p.setProperty("combat.i0.deco", "5"); p.setProperty("combat.i0.irr", "5")
            St.save(OWNER, p)
        finally:
            St.LOCK.unlock()
        bd = T49._build(pf)
        r_ = T410.full(pf)
        K.check(not r_["miss"] and not r_["unbound"], "TP size %d walks clean %s %s" % (sz, r_["miss"][:2], r_["unbound"][:2]))
        n = int(Ck.atOnceZ(0, sz, 5))   # fixer: a maxed Large town = every kind of Zone 1 (22)
        hits = [s_ for s_ in bd["datas"] if s_.startswith("#SkyyShKH")]
        K.eq(len(hits), n, "TP size %d: %d monster squares (Mobs at once)" % (sz, n))
        K.check(all(('"kt%s:0"' % s_[len("#SkyyShKH"):]) in bd["datas"][s_] for s_ in hits), "TP ... each names its spot + the island slot")
        K.check("ClkTMon" in bd["mk"] and "ClkTree1.png" not in bd["mk"] and "ClkTIsl%d.png" % sz in bd["mk"] and "#SkyyShKWx" not in bd["mk"] and "#SkyyShKD4" not in bd["mk"]
                and "#SkyyShKTo0" in bd["mk"], "TP ... the monsters, the town island, the spirit warriors (totems), no weather totem / decorations")
        K.check(bd["sets"].get("#SkyyShKTitle.Text") == "COMBAT SHARD" and "Warrior strength" in bd["mk"] and "Monster level" in bd["mk"] and "Tree size" not in bd["mk"],
                "TP ... the title + the town's row names")
        els = bd["mk"].count("{") - bd["mk"].count('"{')
        K.check(els < 1000, "TP ... %d elements (well under ~1,600)" % els)
        K.check(bd["size"] < 1000000, "TP ... the packet stays small (%d bytes)" % bd["size"])
    K.check(str(pf.ckInfo).startswith("Hold a weapon to fight"), "TP the info line without a weapon: %s" % pf.ckInfo)
    # a kill on the page: status, pop, the slain picture
    St.LOCK.lock()
    try:
        p.setProperty("combat.i0.size", "1"); p.setProperty("combat.i0.amt", "0"); p.setProperty("combat.i0.deco", "0"); p.setProperty("combat.i0.irr", "0")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    Ck.HAND_TEST = CRUDE
    T49._build(pf)
    Cfg.CK_CPS = 1000
    for i in range(40):
        pf.handleDataEvent(None, None, json.dumps({"a": "kt0:0"}))
        if str(pf.stText).startswith("Slew a"):
            break
    bd = T49._build(pf)
    K.check(str(pf.stText).startswith("Slew a ") and len(str(pf.ckPop)) > 0, "TP a monster is slain: %s / %s" % (pf.stText, pf.ckPop))
    K.check("#SkyyShKPop" in bd["mk"] and "ClkTSlain.png" in bd["mk"], "TP ... the gold pop + the slain monster while a new one comes")
    K.check(str(pf.ckInfo).startswith("Fighting with your ") and "(T1)" in str(pf.ckInfo), "TP the info line with a weapon: %s" % pf.ckInfo)
    pf.handleDataEvent(None, None, json.dumps({"a": "kmap"}))
    bd = T49._build(pf)
    r_ = T410.full(pf)
    K.check(not r_["miss"] and not r_["unbound"] and "ClkTMap0.png" in bd["mk"] and "ZONE 1 TOWN" in bd["mk"], "TP the town map walks clean")
    pf.handleDataEvent(None, None, json.dumps({"a": "kisl"}))
    pf.handleDataEvent(None, None, json.dumps({"a": "kback"}))
    K.check(int(pf.view) == 0 and int(pf.tab) == 1, "TP Shard menu -> the menu's Map tab")
    # switched off: no button, kopen refused; the other clickers untouched
    Cfg.TF_ON = False
    bm = T49._build(pf)
    pf.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
    K.check("#SkyyShClk" not in bm["mk"] and int(pf.view) == 0 and "switched off" in str(pf.stText), "TP the town off: no button, kopen refused")
    Cfg.TF_ON = True
    for kd_, setup, hand, title, pic in ((FO, T423._foraging, "Tool_Hatchet_Copper", "FORAGING SHARD", "ClkTree1.png"),
                                         (MI, T424._mining, "Tool_Pickaxe_Copper", "MINING SHARD", "ClkQNode0.png"),
                                         (FK, T425._farm, "Tool_Hoe_Crude", "FARMING SHARD", "ClkFCrop0.png")):
        po = Page(ou, W_)
        po.kind = kd_
        po.view = 0
        Ck.HAND_TEST = hand
        setup(L, p)
        po.handleDataEvent(None, None, json.dumps({"a": "kopen"}))
        bo = T49._build(po)
        K.check(int(po.view) == 5 and not bool(po.ckTown) and pic in bo["mk"] and "ClkTMon" not in bo["mk"] and bo["sets"].get("#SkyyShKTitle.Text") == title,
                "TP the %s clicker still shows its own page" % title)
    Cfg.CK_CPS = 8
    Ck.HAND_TEST = None
    K.save()


EXPECT = {   # 0.4.25 -> 0.4.26: the version texts (CfgFile / CfgFn / CfgRows / ShFill.markFixed / ShStore / the ready line) + the round
    'CfgFile': ['~<clinit>'],
    'CfgFn': ['~m opExport'],
    'CfgRows': ['~<clinit>', '~m header'],
    'CfgRows1': ['~<clinit>'],   # the kit's ROW HOLDERS (HOLDERS=2): the 10 click.fight.* rows
    'CfgRows2': ['~<clinit>'],
    'ShCfg': ['+f DEF_TF_ZT', '+f TF_HP', '+f TF_HPSTEP', '+f TF_NS_MAX', '+f TF_ON', '+f TF_RMIN', '+f TF_RSP', '+f TF_SKIP', '+f TF_STR', '+f TF_XPHP', '+f TF_ZT',
              '~<clinit>', '~m loadCfg'],
    'ShClk': ['+f LOOTED', '+f SLAIN', '+f TGATED', '+f TK', '+f TL_MAX', '+f TOWN', '+f T_DROP', '+f T_HP', '+f T_NAME', '+f T_OFF', '+f T_PIC', '+f T_RANK', '+f T_ROLE',
              '+f WEAP_ID', '+f WEAP_T', '+f NOXP', '+f XPREF', '+m atOnceZ', '+m classXpOk', '+m noXpWhy', '+m payClass',
              '+m arrivals', '+m arrive', '+m atOnce', '+m classSkill', '+m classWord', '+m fight', '+m killXp', '+m kindsAt', '+m lootOf',
              '+m mix', '+m monHp', '+m roleAt', '+m strPct', '+m townLv', '+m townRespawnMs', '+m townWord', '+m weapTier', '+m zN', '+m zoneTier', '~<clinit>',
              '~m buyNode', '~m chop', '~m mine'],   # chop / mine: the memory-key fix
    'ShFill': ['~m markFixed'],
    'ShPage': ['+f T_MON', '+f T_SLAIN', '+f ckTown', '+m fillTown', '+m townFresh', '~<clinit>', '~m act', '~m actClick', '~m build0', '~m buildClick', '~m buildFull',
               '~m fillClick', '~m fillFarm', '~m fillQuarry'],
    'ShStore': ['~m migrate', '~m migrate2', '~m save'],
    'SkyyShardsPlugin': ['~m setup'],
}


def _compare26(out, jar, old_jar, pkg, expect, added, removed=()):
    """the town's NEW pictures (Map/ClkT<Mon|Slain|Isl|Map>*, Map/ClkUpT*) are new only; every other non-class file identical; the kit's class compare
    runs on a copy of the new jar without the new pictures"""
    rx = re.compile(r"^Common/UI/Custom/SkyyShards/Map/Clk(T(Mon\d+|Slain|Isl\d|Map\d)|UpT(Str|Lvl|Spd|Mob))@2x\.png$")
    with zipfile.ZipFile(jar) as a, zipfile.ZipFile(old_jar) as b:
        na, nb = set(a.namelist()), set(b.namelist())
        new = sorted(n for n in na - nb if not n.endswith(".class"))
        assert all(rx.match(n) for n in new) and len(new) >= 30 and not any(rx.match(n) for n in nb), "C new non-class files: %s" % new[:8]
        gone = sorted(n for n in nb - na if not n.endswith(".class"))
        assert not gone, "C non-class files gone: %s" % gone[:8]
        chg = sorted(n for n in na & nb if not n.endswith(".class") and a.read(n) != b.read(n))
        assert chg == ["manifest.json"], "C changed non-class files: %s" % chg[:8]
    print("C. %d new non-class files (the town pictures); the older pictures + theme unchanged; manifest.json changed" % len(new))
    cp = os.path.join(SCRATCH, "compare-%s.jar" % VERSION)
    with zipfile.ZipFile(jar) as zi, zipfile.ZipFile(cp, "w", zipfile.ZIP_DEFLATED) as zo:
        for n in zi.namelist():
            if not rx.match(n):
                zo.writestr(n, zi.read(n))
    T419._compare(out, cp, old_jar, pkg, expect, added, removed)


def run_live(out, jar, scratch, home):
    T421.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run_compare = _compare26
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("fight26", run_fight), ("memkey26", run_memkey), ("upgrade26", run_upgrade), ("zones26", run_zones),
                   ("collect26", run_collect), ("page26", run_page),
                   ("farm25", T425.run_farm), ("upgrade25", T425.run_upgrade), ("zones25", T425.run_zones), ("collect25", T425.run_collect), ("page25", T425.run_page),
                   ("mine24", T424.run_mine), ("smithy24", T424.run_smithy), ("upgrade24", T424.run_upgrade), ("zones24", T424.run_zones),
                   ("collect24", T424.run_collect), ("fortune24", T424.run_fortune), ("page24", T424.run_page),
                   ("click23", T423.run_click), ("collect23", T423.run_collect), ("upgrade23", T423.run_upgrade), ("zones23", T423.run_zones),
                   ("page23", T423.run_page23),
                   ("combat22", T422.run_combat), ("farm22", T422.run_farm), ("page22", T422.run_page22),
                   ("geo", T421.run_geo), ("rebuild", T421.run_rebuild), ("level", T421.run_level), ("bags", T421.run_bags), ("page21", T421.run_page21),
                   ("comp", T420.run_comp), ("sell20", T420.run_sell), ("mig20", T420.run_mig20), ("ore", T420.run_ore), ("deb", T420.run_deb), ("page20", T420.run_page20), ("livecomp", T420.run_livecomp),
                   ("off", T419.run_off), ("mig", T419.run_mig), ("sell", T419.run_sell), ("page", T419.run_page),
                   ("open", T416._h(T416._g(T416.run_open), True)), ("bytecode", T423.run_bytecode23),
                   ("flows3", T416._h(T416._g(T413.run_flows3))), ("page49", T419.run_page49),
                   ("live", run_live)],
           script=__file__, live=(T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
