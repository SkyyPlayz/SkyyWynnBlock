"""Harness for SkyyShards 0.4.33 (Shard Link - tools/shards_0_4_33_patch.py, on top of 0.4.32; the pocket half is SkyySacks 0.8.42).
Build first:
    python tools/shards_0_4_33_patch.py && python SkyyShards/build_skyyshards_0.4.33.py
    python SkyyShards/test_skyyshards_0.4.33.py [--keep] [--only label,label] [--dir <scratch>]

  S33   static  the patch re-runs to identical bytes; header / VERSION / ready line / rollback note; no new registerSystem / registerCommand; line
                endings kept; ShLink is the only new class
  L33   link    EXECUTED with a stand-in SkyySacks (sacks:fn:link: state / room / put / done / ack, its own pocket + markers) for all SIX shards on
                seeded production (stock, Auto-Compactor Enchanted, bonus finds, legacy, clicked drops with bars + an alloy, the town's roll):
                the link = Collect all into an inventory, item for item, collection credit for credit, XP for XP; the shard empty afterwards
  F33   full    the pocket full mid-batch: what fits moves (credited), the rest stays exactly where it was (stock count, drops), a later
                Collect all pays the rest - link + Collect = one Collect (items, credit, XP); an item no pocket takes stays
  R33   restart a crash after the shard's journal save (SkyySacks never got the put) -> everything back, no credit; SkyySacks wrote it but the
                answer was lost -> credited once; SkyySacks unreachable -> the journal waits on disk, a "restart" (the shard file re-read) +
                SkyySacks back -> settled once; never twice (a second resolve does nothing)
  G33   gates   a co-op member / another player, a profile switch (pkey), a busy profile, no link on, a locked shard, a shard in use (BUSY) move
                nothing; the page throttle; Collect all runs the link first; the tick (tickOne) moves every shard; the page line "Linked to pocket";
                many small transfers pay exactly the XP of one Collect (the kept fraction)
  X33   fixes   (link1 critics) an id with ; or = never taken; a full pocket puts the shard back key by key; the Moon Blade cache warmed
                before the settle; no SkyySacks = no page line; a lost ack kept in <kind>.linkack and asked again (restart, no link on)
  then 0.4.32's phases (minus static / livemig32) on THIS jar, A verify, C compare, AA audit, live33 = 0.4.32's start-twice on a scratch copy of
                the live data (the new keys appear only after a transfer: no migration)
Exit code 1 on any failure.
"""
import os, sys, importlib.util, subprocess, json, re, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.4.33"
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "link1", "h")]
if "--jar" not in sys.argv:
    sys.argv += ["--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)]
JAR = os.path.abspath(HK.arg("--jar"))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.4.32.jar")
GEN = os.path.join(HERE, "build_skyyshards_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyshards_0.4.32.py")
PATCH = os.path.join(ROOT, "tools", "shards_0_4_33_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.shards."

_T32 = open(os.path.join(HERE, "test_skyyshards_0.4.32.py"), encoding="utf8").read()
assert _T32.count('VERSION = "0.4.32"\n') == 1, "the 0.4.32 harness changed"
_T32 = _T32.replace('VERSION = "0.4.32"\n', 'VERSION = "%s"\n' % VERSION)
_argv = list(sys.argv)
T432 = importlib.util.module_from_spec(importlib.util.spec_from_loader("test_skyyshards_0_4_32", loader=None))
T432.__dict__["__file__"] = os.path.join(HERE, "test_skyyshards_0.4.32.py")
exec(compile(_T32, T432.__file__, "exec"), T432.__dict__)
sys.argv[:] = _argv
T431, T428, T427, T426, T425, T424, T423 = T432.T431, T432.T428, T432.T427, T432.T426, T432.T425, T432.T424, T432.T423
for _m in (T432, T431, T428):
    _m.JAR = JAR
    _m.SCRATCH = SCRATCH
OWNER = T428.OWNER
T0 = T428.T0
MI, FO, FK, RA, OR, CK = 0, 1, 2, 3, 4, 5
KN = ["mining", "foraging", "farming", "ranching", "orchard", "combat"]


def run_static(out, jar, scratch, _home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyShards 0.4.33 - build script') and 'VERSION = "0.4.33"\n' in g, "S33 header + VERSION")
    for w in ("registerSystem(", "registerCommand("):
        K.check(g.count(w) == o.count(w), "S33 no new %r" % w)
    K.check(g.count('mk("') == o.count('mk("') + 1 and 'lnk = mk("ShLink")' in g, "S33 one new class: ShLink")
    K.check("[SkyyShards] @VERSION@ ready (@KITID@) - 0.4.33: Shard Link" in g, "S33 the ready line names the round")
    K.check("ROLLBACK 0.4.33 -> 0.4.32 alone" in g and "SAVED DATA: new keys <kind>.linkpend" in g, "S33 the rollback + saved-data notes")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "b.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S33 the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S33 line endings kept")
    K.check(os.path.getmtime(GEN) >= os.path.getmtime(PATCH) and os.path.getmtime(jar) >= os.path.getmtime(GEN), "S33 jar newer than the script, the script newer than the patch")
    z = zipfile.ZipFile(jar)
    zo = zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(z.namelist()) - set(zo.namelist())), ["com/skyy/shards/ShLink.class"], "S33 the only new jar entry is ShLink.class")
    K.eq(sorted(set(zo.namelist()) - set(z.namelist())), [], "S33 no jar entry removed")
    K.save()


# ---------------------------------------------------------------------------------------------------- the stand-in SkyySacks
ENCH_MINING = ("Copper", "Iron", "Cobblestone", "Thorium", "Cobalt", "Bronze", "Lead", "Silver", "Gold")


def cat_of(i):
    """SkyySacks catOf, the rows this harness needs (Plant_Seeds_* = no pocket: it must stay in the shard)"""
    if i.startswith("Plant_Seeds_"):
        return None
    if i.startswith("Skyy_Ench_"):
        n = i[len("Skyy_Ench_"):]
        if n in ENCH_MINING:
            return "Mining"
        if n in ("Oak", "Beech", "Maple", "Birch", "TreeSap", "Stick", "Fiber"):
            return "Foraging"
        if n in ("Bone", "Linen", "Venom", "Chitin", "Feathers"):
            return "Combat"
        return "Farming"
    if i.startswith(("Ore_", "Rock_", "Rubble_", "Soil_")):
        return "Mining"
    if i.startswith(("Ingredient_Bar_", "Ingredient_Hide_", "Ingredient_Leather_")):
        return "Smithing"
    if i.startswith(("Wood_", "Plant_Sapling_")) or i in ("Ingredient_Stick", "Ingredient_Fibre", "Ingredient_Tree_Sap"):
        return "Foraging"
    if i.startswith(("Plant_", "Food_")) or i.startswith("Ingredient_Life_Essence"):
        return "Farming"
    if i.startswith("Ingredient_"):
        return "Combat"
    return None


class Sacks(object):
    """sacks:fn:link as SkyySacks 0.8.42 answers it (the contract its own harness checks on the real classes)"""

    def __init__(self, key, room=10 ** 9):
        self.key = key
        self.active = {"Mining", "Foraging", "Farming", "Combat", "Smithing"}
        self.room = dict((c, room) for c in self.active)
        self.pool = {}
        self.marks = {}
        self.mode = None      # "down" = put never happens (null), "lost" = put happens but the answer is lost, "dead" = done answers null too
        self.calls = []
        self.under_lock = 0

    def __call__(self, a):
        from jpype import JClass
        if bool(JClass(PKG + "ShStore").LOCK.isHeldByCurrentThread()):
            self.under_lock += 1
        op = str(a[0])
        self.calls.append(op)
        if op == "state":
            return ",".join(sorted(self.active))
        if op == "room":
            if str(a[2]) != self.key or not self.active:
                return ""
            ids = [x for x in str(a[3]).split(",") if x]
            ia = ",".join("%s=%s" % (i, cat_of(i)) for i in ids if cat_of(i) in self.active)
            return ",".join("%s:%d" % (c, self.room[c]) for c in sorted(self.active)) + "|" + ia
        if op == "put":
            tok = str(a[3])
            if self.mode in ("down", "dead"):
                return None
            if tok in self.marks:
                return self.marks[tok]
            if str(a[2]) != self.key:
                return ""
            acc = []
            for x in str(a[4]).split(","):
                i, q = x.rsplit(":", 1)
                c = cat_of(i)
                g = 0 if c not in self.active else min(int(q), self.room[c])
                if g:
                    self.room[c] -= g
                    self.pool[i] = self.pool.get(i, 0) + g
                acc.append("%s:%d" % (i, g))
            self.marks[tok] = ",".join(acc)
            if self.mode == "lost":
                return None
            return self.marks[tok]
        if op == "done":
            if self.mode == "dead":
                return None
            return self.marks.get(str(a[2]), "")
        if op == "ack":
            if self.mode == "noack":
                return None
            return JClass("java.lang.Boolean")(self.marks.pop(str(a[2]), None) is not None)
        return None


def _env(scratch, K, name):
    from jpype import JClass
    L, ou, W_, p, lv, got = T431._env(scratch, K, name)
    for k_ in ("Ranching", "Orchard", "Mining", "Foraging", "Farming"):
        lv[k_] = 100
    L["ShLink"] = JClass(PKG + "ShLink")
    L["ShLink"].PAGE_MS = 0
    return L, ou, W_, p, lv, got


def _props(p):
    return dict((str(k), str(p.getProperty(k))) for k in p.stringPropertyNames())


def _restore(L, p, snap):
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        p.clear()
        for k_, v_ in snap.items():
            p.setProperty(k_, v_)
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    L["ShCore"].AL_PAR.clear()
    L["ShCore"].MEM_OWED.clear()
    L["ShLink"].LINE.clear()
    L["ShLink"].LAST.clear()


SEED_DROPS = {MI: "Ore_Copper:7,Ingredient_Bar_Iron:5,Ingredient_Bar_Bronze:3", FO: "Wood_Oak_Trunk:9,Plant_Sapling_Oak:4",
              FK: "Plant_Crop_Wheat_Item:11,Plant_Seeds_Wheat:6", RA: "Food_Chicken_Raw:5,Ingredient_Feathers_Light:3", OR: "Plant_Fruit_Apple:8"}


def _seed(L, p, kd, stored=345, cmp=1, ench=3, legacy=True):
    """one island of the zone-1 type of shard kd with known stock: stored (Auto-Compactor I on: 3 Enchanted + 45), bonus finds, legacy stock,
    clicked drops (Mining: an ore, bars, an alloy; Farming: seeds no pocket takes); Combat: a town pool count (rolled by the transfer / Collect)"""
    Isl = L["ShIsl"]
    key = str(Isl.KEY[int(Isl.LAD0[kd])])
    T432._set_one(L, p, kd, key, 2)
    St = L["ShStore"]
    St.LOCK.lock()
    try:
        b = "%s.i0." % KN[kd]
        p.setProperty(b + "last", str(T0))
        p.setProperty(b + "stored", str(stored if kd != CK else 600))
        if kd == CK:
            p.remove(b + "rolled")
            p.remove(b + "drops")
        else:
            p.setProperty(b + "drops", SEED_DROPS[kd])
            p.setProperty(KN[kd] + ".compactor", str(cmp))
            if str(L["ShKind"].BONUS[kd]):
                p.setProperty(b + "ench", str(ench))
            if legacy:
                t = int(Isl.ty(kd, p, 0))
                lid = str(Isl.ENCH[t]) or str(Isl.PROD[t])
                p.setProperty(b + "legacy", "%s:%d" % (lid, 2))
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()


def _shard_left(L, p, kd):
    M = L["ShMath"]
    out = {"stored": int(M.stored(kd, p, 0)), "ench": int(M.ench(kd, p, 0)), "legacy": str(p.getProperty("%s.i0.legacy" % KN[kd]) or ""),
           "drops": str(p.getProperty("%s.i0.drops" % KN[kd]) or "")}
    return out


def _inv_items(L, cs, ids):
    return dict((i, int(L["count"](cs, i))) for i in ids if int(L["count"](cs, i)))


ALL_IDS = None


def _ids(L):
    global ALL_IDS
    if ALL_IDS is None:
        Isl = L["ShIsl"]
        s = set()
        for t in range(int(Isl.TN)):
            for a in (Isl.PROD, Isl.ENCH, Isl.SMELT, Isl.SMELTE, Isl.SEED):
                if str(a[t]):
                    s.add(str(a[t]))
        for v in SEED_DROPS.values():
            s |= set(x.rsplit(":", 1)[0] for x in v.split(","))
        for b in L["ShKind"].BONUS:
            if str(b):
                s.add(str(b))
        Cb = L["ShCombat"]
        try:
            for r in Cb.DROP_ITEM:
                if str(r):
                    s.add(str(r))
        except Exception:
            pass
        ALL_IDS = sorted(s)
    return ALL_IDS


def _collect(L, ou, kd, got):
    """the baseline: Collect all into an empty inventory (no SkyySacks link)"""
    from jpype import JString
    L["ShLink"].FN_TEST = None
    c0, x0 = dict(got["coll"]), got["xp"]
    cs = L["inv"](27, 27, 27, 9)
    r = str(L["ShCore"].collect(ou, JString(OWNER), kd, -1, cs))
    ids = _ids(L)
    # the town's drops: whatever ids the inventory got
    items = {}
    for c in cs:
        for s_ in range(int(c.getCapacity())):
            it = c.getItemStack(s_)
            if it is not None and not it.isEmpty():
                items[str(it.getItemId())] = items.get(str(it.getItemId()), 0) + int(it.getQuantity())
    coll = dict((k_, v_ - c0.get(k_, 0)) for k_, v_ in got["coll"].items() if v_ - c0.get(k_, 0))
    return r, items, coll, got["xp"] - x0


def _link(L, ou, kd, got, sk):
    from jpype import JString
    L["ShLink"].FN_TEST = L["PyFn"](sk)
    c0, x0, p0 = dict(got["coll"]), got["xp"], dict(sk.pool)
    n = int(L["ShLink"].run(ou, JString(OWNER), kd))
    pool = dict((k_, v_ - p0.get(k_, 0)) for k_, v_ in sk.pool.items() if v_ - p0.get(k_, 0))
    coll = dict((k_, v_ - c0.get(k_, 0)) for k_, v_ in got["coll"].items() if v_ - c0.get(k_, 0))
    return n, pool, coll, got["xp"] - x0


def _addd(a, b):
    o = dict(a)
    for k_, v_ in b.items():
        o[k_] = o.get(k_, 0) + v_
    return dict((k_, v_) for k_, v_ in o.items() if v_)


# ---------------------------------------------------------------------------------------------------- L33 / F33: link = Collect, all six shards
def run_link(out, jar, scratch, _home):
    from jpype import JString
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "l33")
    Lk, M = L["ShLink"], L["ShMath"]
    for kd in (FO, MI, FK, RA, OR, CK):
        for variant in ("cmp", "plain"):
            _seed(L, p, kd, cmp=1 if variant == "cmp" else 0)
            snap = _props(p)
            r, inv, coll_c, xp_c = _collect(L, ou, kd, got)
            K.check(r.startswith("+Collected"), "L33 %s/%s the baseline Collect all ran: %s" % (KN[kd], variant, r[:160]))
            left_c = _shard_left(L, p, kd)
            _restore(L, p, snap)
            sk = Sacks(OWNER)
            n, pool, coll_l, xp_l = _link(L, ou, kd, got, sk)
            left_l = _shard_left(L, p, kd)
            stay = dict((i, q) for i, q in inv.items() if cat_of(i) is None)
            moved = dict((i, q) for i, q in inv.items() if cat_of(i) is not None)
            K.eq(pool, moved, "L33 %s/%s the pocket got exactly what Collect all gives (items no pocket takes stay: %s)" % (KN[kd], variant, stay))
            K.eq(n, sum(moved.values()), "L33 %s/%s run() = the items moved" % (KN[kd], variant))
            K.notes.append("L33 %s/%s: Collect gave %d items %s; the link moved %d, credit %s, XP %d" % (KN[kd], variant, sum(inv.values()), sorted(inv.items())[:6], n, sorted(coll_l.items())[:4], xp_l))
            if not stay:
                K.eq(coll_l, coll_c, "L33 %s/%s collection credit = Collect's" % (KN[kd], variant))
                K.eq(xp_l, xp_c, "L33 %s/%s XP = Collect's (%d)" % (KN[kd], variant, xp_c))
                K.eq(left_l, left_c, "L33 %s/%s the shard is left as Collect leaves it" % (KN[kd], variant))
            else:
                # Farming seeds: no pocket takes them - they stay in the drops; Collect all then pays them: link + Collect = Collect
                r2, inv2, coll2, xp2 = _collect(L, ou, kd, got)
                K.eq(inv2, stay, "L33 %s/%s ... the items no pocket takes stayed and a Collect all gives just them: %s" % (KN[kd], variant, r2[:80]))
                K.eq(_addd(coll_l, coll2), coll_c, "L33 %s/%s ... link + Collect credit = Collect's" % (KN[kd], variant))
                K.eq(xp_l + xp2, xp_c, "L33 %s/%s ... link + Collect XP = Collect's" % (KN[kd], variant))
            K.check(str(p.getProperty("%s.linkpend" % KN[kd]) or "") == "" and not sk.marks, "L33 %s/%s no journal line left, every marker acked" % (KN[kd], variant))
            K.check(sk.under_lock == 0, "L33 %s/%s SkyySacks never called under the shard lock" % (KN[kd], variant))
            K.check(any(str(x).find("LINK done") >= 0 for x in [open(os.path.join(os.path.dirname(str(L["ShStore"].DIR)), "collect.log"), encoding="utf8").read()]),
                    "L33 %s/%s collect.log has the LINK lines" % (KN[kd], variant))
            # F33: the pocket full mid-batch (room 17 a pocket): what fits moves, the rest stays; Collect all then = the rest
            _restore(L, p, snap)
            sk2 = Sacks(OWNER, room=17)
            n2, pool2, coll2l, xp2l = _link(L, ou, kd, got, sk2)
            K.check(0 < n2 <= 17 * 5 and all(v_ <= 17 for v_ in pool2.values()), "F33 %s/%s a full pocket takes only its room: %d moved %s" % (KN[kd], variant, n2, pool2))
            K.check("it is full" in str(Lk.line(JString(OWNER), kd) or ""), "F33 %s/%s the page line says the pocket is full: %s" % (KN[kd], variant, Lk.line(JString(OWNER), kd)))
            r3, inv3, coll3, xp3 = _collect(L, ou, kd, got)
            K.eq(_addd(pool2, inv3), inv, "F33 %s/%s what did not fit stayed exactly: link + Collect all = Collect all (items)" % (KN[kd], variant))
            K.eq(_addd(coll2l, coll3), coll_c, "F33 %s/%s ... credit, never twice, never lost" % (KN[kd], variant))
            K.check(abs((xp2l + xp3) - xp_c) <= 1, "F33 %s/%s ... XP (%d + %d vs %d; a Collect of a part rounds down once)" % (KN[kd], variant, xp2l, xp3, xp_c))
            _restore(L, p, snap)
            if kd == CK:
                break   # the town has no compactor: one variant
    K.save()


# ---------------------------------------------------------------------------------------------------- R33: restarts mid-transfer
def run_restart(out, jar, scratch, _home):
    from jpype import JString, JClass
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "r33")
    Lk, St = L["ShLink"], L["ShStore"]
    for kd in (MI, FK, CK):
        _seed(L, p, kd)
        snap = _props(p)
        r, inv, coll_c, xp_c = _collect(L, ou, kd, got)
        _restore(L, p, snap)
        moved = dict((i, q) for i, q in inv.items() if cat_of(i) is not None)
        # 1. SkyySacks never got the put (crash before its save): done = "never happened" -> all back, no credit
        sk = Sacks(OWNER)
        sk.mode = "down"
        c0, x0 = dict(got["coll"]), got["xp"]
        n = int(_link(L, ou, kd, got, sk)[0])
        K.check(n == 0 and not sk.pool and got["coll"] == c0 and got["xp"] == x0, "R33 %s put never happened: nothing moved, no credit" % KN[kd])
        K.check(str(p.getProperty("%s.linkpend" % KN[kd]) or "") == "", "R33 %s ... the journal line resolved (done = never happened)" % KN[kd])
        r_, inv_, coll_, xp_ = _collect(L, ou, kd, got)
        K.eq((inv_, coll_, xp_), (inv, coll_c, xp_c), "R33 %s ... everything was back: Collect all = the baseline" % KN[kd])
        _restore(L, p, snap)
        # 2. written but the answer lost -> credited once (from done)
        sk = Sacks(OWNER)
        sk.mode = "lost"
        n, pool, coll_l, xp_l = _link(L, ou, kd, got, sk)
        K.eq(pool, moved, "R33 %s answer lost: the pocket has the items" % KN[kd])
        if not [i for i in inv if cat_of(i) is None]:
            K.eq((coll_l, xp_l), (coll_c, xp_c), "R33 %s ... credited once, from done" % KN[kd])
        K.check(str(p.getProperty("%s.linkpend" % KN[kd]) or "") == "" and not sk.marks, "R33 %s ... resolved + acked" % KN[kd])
        _restore(L, p, snap)
        # 3. SkyySacks dead (no put, no done): the journal waits ON DISK; a restart (file re-read) + SkyySacks back -> settled once
        sk = Sacks(OWNER)
        sk.mode = "lost"            # the put is written, then everything stops answering
        Lk.FN_TEST = L["PyFn"](sk)
        tk = str(Lk.tok(kd))
        room = JClass("java.util.HashMap")()
        idc = JClass("java.util.HashMap")()
        for c_ in sk.active:
            room.put(c_, JClass("java.lang.Long")(10 ** 9))
        for i in _ids(L) + list(inv):
            if cat_of(i):
                idc.put(i, cat_of(i))
        from jpype import JArray, JBoolean
        full = JArray(JBoolean)(1)
        line = str(Lk.take(ou, JString(OWNER), kd, p, room, idc, JString(tk), full))
        disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="latin-1").read()
        K.check(line.startswith(tk + "|") and ("%s.linkpend=" % KN[kd]) in disk, "R33 %s the shard's take + journal line are on disk before SkyySacks is asked" % KN[kd])
        items = {}
        for e in line.split("|", 1)[1].split(";"):
            f = e.split(",")
            items[f[2]] = items.get(f[2], 0) + int(f[3])
        sk.mode = None
        sk(["put", ou, OWNER, tk, ",".join("%s:%d" % x for x in items.items())])
        sk.mode = "dead"
        c0, x0 = dict(got["coll"]), got["xp"]
        K.eq(int(Lk.run(ou, JString(OWNER), kd)), 0, "R33 %s SkyySacks dead: nothing settled (cannot tell)" % KN[kd])
        K.check(str(p.getProperty("%s.linkpend" % KN[kd]) or "") == line and got["coll"] == c0, "R33 %s ... the journal waits, no credit" % KN[kd])
        St.CACHE.remove(JString(OWNER))   # the restart: the shard file is read again from disk
        p2 = St.get(JString(OWNER))
        K.check(str(p2.getProperty("%s.linkpend" % KN[kd]) or "") == line, "R33 %s ... after the restart the journal line is read back from disk" % KN[kd])
        sk.mode = None
        n = int(Lk.run(ou, JString(OWNER), kd))
        coll_l = dict((k_, v_ - c0.get(k_, 0)) for k_, v_ in got["coll"].items() if v_ - c0.get(k_, 0))
        K.check(n >= sum(items.values()) and str(p2.getProperty("%s.linkpend" % KN[kd]) or "") == "", "R33 %s ... SkyySacks back: settled (%d moved)" % (KN[kd], n))
        if not [i for i in inv if cat_of(i) is None]:
            K.eq((coll_l, got["xp"] - x0), (coll_c, xp_c), "R33 %s ... credited exactly once" % KN[kd])
        c1, x1 = dict(got["coll"]), got["xp"]
        K.eq(int(Lk.resolve(ou, JString(OWNER), kd, p2, None)), -1, "R33 %s ... a second resolve finds nothing" % KN[kd])
        K.check(got["coll"] == c1 and got["xp"] == x1, "R33 %s ... and pays nothing twice" % KN[kd])
        _restore(L, St.get(JString(OWNER)), snap)
        p = St.get(JString(OWNER))
    K.save()


# ---------------------------------------------------------------------------------------------------- G33: gates, page, tick, XP fraction
def run_gates(out, jar, scratch, _home):
    from jpype import JString, JClass
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "g33")
    Lk, St, Cfg, Core, Page = L["ShLink"], L["ShStore"], L["ShCfg"], L["ShCore"], L["ShPage"]
    UUID = JClass("java.util.UUID")
    _seed(L, p, MI)
    snap = _props(p)
    sk = Sacks(OWNER)
    Lk.FN_TEST = L["PyFn"](sk)
    other = UUID.fromString("00000000-0000-0000-0000-00000000c0b1")
    kt = Cfg.KEY_TEST
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER) if str(u) == str(ou) else JString(str(u)))   # every player on their own profile
    K.eq(int(Lk.run(other, JString(OWNER), MI)), 0, "G33 another player (co-op member / visitor) moves nothing")
    K.check(not sk.pool and "put" not in sk.calls, "G33 ... SkyySacks never asked to put")
    Cfg.KEY_TEST = L["PyFn"](lambda u: JString(OWNER + "-p2"))
    K.eq(int(Lk.run(ou, JString(OWNER), MI)), 0, "G33 the owner on another profile (a profile switch) moves nothing from this one")
    Cfg.KEY_TEST = kt
    Lk.BUSY.put(JString(OWNER + "|0"), JClass("java.lang.Boolean").TRUE)
    K.eq(int(Lk.run(ou, JString(OWNER), MI)), 0, "G33 a transfer of the same shard already running: nothing")
    Lk.BUSY.clear()
    sk.active = set()
    K.eq(int(Lk.run(ou, JString(OWNER), MI)), 0, "G33 no link on (room = ''): nothing")
    K.check(Lk.line(JString(OWNER), MI) is None, "G33 ... no page line")
    K.eq(_shard_left(L, p, MI)["stored"], 345, "G33 ... the stock untouched")
    sk.active = {"Mining", "Smithing"}
    sk.key = OWNER + "-other"
    K.eq(int(Lk.run(ou, JString(OWNER), MI)), 0, "G33 SkyySacks says another profile is active: nothing")
    sk.key = OWNER
    lv["Mining"] = 0
    lk = str(L["ShIsl"].lockMsg(ou, MI) or "")
    if lk:
        K.eq(int(Lk.run(ou, JString(OWNER), MI)), 0, "G33 a locked shard (level) moves nothing: %s" % lk[:60])
    lv["Mining"] = 100
    # Collect all runs the link first
    Lk.LAST.clear()
    cs = L["inv"](27, 27, 9)
    r = str(Core.collect(ou, JString(OWNER), MI, -1, cs))
    K.check(sk.pool.get("Ore_Copper", 0) > 0 and int(L["count"](cs, "Ore_Copper")) == 0, "G33 Collect all: the link first (Ore_Copper went to the pocket) then the rest: %s / %s" % (sk.pool, r[:100]))
    _restore(L, p, snap)
    # the page: the line + the throttle
    sk = Sacks(OWNER)
    Lk.FN_TEST = L["PyFn"](sk)
    Lk.PAGE_MS = 60000
    pg = T427._page(L, ou, W_, MI)
    T432.T49._build(pg)
    K.check("Linked to pocket (Mining, Smithing)" in str(pg.sgHint), "G33 the clicker page line: %s" % pg.sgHint)
    K.check(sum(sk.pool.values()) > 0, "G33 ... opening the page moved the stock")
    nput = sk.calls.count("put")
    _seed(L, p, MI)
    T432.T49._build(T427._page(L, ou, W_, MI))
    K.eq(sk.calls.count("put"), nput, "G33 ... a redraw within PAGE_MS does not move again (the tick does)")
    Lk.PAGE_MS = 0
    # the tick: every shard of the owner
    _restore(L, p, snap)
    _seed(L, p, FO)
    sk = Sacks(OWNER)
    Lk.FN_TEST = L["PyFn"](sk)
    m = int(Lk.tickOne(ou))
    K.check(m > 0 and sk.pool.get("Ore_Copper", 0) > 0 and sk.pool.get("Wood_Oak_Trunk", 0) > 0, "G33 tickOne moves every owned shard (Mining + Foraging): %d %s" % (m, sk.pool))
    # the XP fraction: 12 small transfers of 7 = one transfer of 84 (Mining XP x XP_PCT rounds per batch)
    Cfg.XP_PCT = 33
    _restore(L, p, snap)
    big = None
    for chunks in ((84,), (7,) * 12):
        _restore(L, p, snap)
        St.LOCK.lock()
        try:
            p.setProperty("mining.i0.drops", "")
            p.remove("mining.i0.drops")
            p.remove("mining.i0.legacy")
            p.setProperty("mining.compactor", "0")
        finally:
            St.LOCK.unlock()
        x0 = got["xp"]
        for c_ in chunks:
            St.LOCK.lock()
            try:
                p.setProperty("mining.i0.stored", str(c_))
                St.save(OWNER, p)
            finally:
                St.LOCK.unlock()
            _link(L, ou, MI, got, Sacks(OWNER))
        if big is None:
            big = got["xp"] - x0
        else:
            K.eq(got["xp"] - x0, big, "G33 12 small transfers pay the XP of one (the fraction is kept in mining.linkxpf): %d" % big)
    Cfg.XP_PCT = 20
    _restore(L, p, snap)
    K.save()


# ---------------------------------------------------------------------------------------------------- X33: the link1 critics' fixes
def run_fix(out, jar, scratch, _home):
    from jpype import JString, JClass, JArray, JBoolean
    K = HK.Child(out)
    L, ou, W_, p, lv, got = _env(scratch, K, "x33")
    Lk, St, M = L["ShLink"], L["ShStore"], L["ShMath"]
    g = open(GEN, encoding="utf8").read()
    # 1. an id with a journal / bridge separator: never asked about, never taken; it waits in the shard for Collect all
    _seed(L, p, MI)
    St.LOCK.lock()
    try:
        p.setProperty("mining.i0.drops", SEED_DROPS[MI] + ",Ore_Odd;X=1:4")
        St.save(OWNER, p)
    finally:
        St.LOCK.unlock()
    K.eq(int(M.held(MI, p, 0).get(JString("Ore_Odd;X=1")) or 0), 4, "X33 (the odd id is a held drop)")
    K.check("Ore_Odd" not in str(Lk.cands(MI, p)), "X33 an id with ; or = is never asked about (cands)")
    sk = Sacks(OWNER)
    Lk.FN_TEST = L["PyFn"](sk)
    room, idc = JClass("java.util.HashMap")(), JClass("java.util.HashMap")()
    for c_ in sk.active:
        room.put(c_, JClass("java.lang.Long")(10 ** 9))
    for i in _ids(L) + ["Ore_Odd;X=1"]:
        if cat_of(i):
            idc.put(i, cat_of(i))
    tk = str(Lk.tok(MI))
    line = str(Lk.take(ou, JString(OWNER), MI, p, room, idc, JString(tk), JArray(JBoolean)(1)))
    K.check(line.startswith(tk + "|") and "Ore_Odd" not in line, "X33 ... even when the room answer maps it: never taken")
    items = {}
    for e in line.split("|", 1)[1].split(";"):
        f = e.split(",")
        items[f[2]] = items.get(f[2], 0) + int(f[3])
    acc = sk(["put", ou, OWNER, tk, ",".join("%s:%d" % x for x in items.items())])
    K.check(int(Lk.resolve(ou, JString(OWNER), MI, p, JString(acc))) > 0 and str(p.getProperty("mining.linkpend") or "") == "",
            "X33 ... the journal settles (nothing stuck)")
    K.eq(int(M.held(MI, p, 0).get(JString("Ore_Odd;X=1")) or 0), 4, "X33 ... the odd drop is still in the shard (Collect all pays it)")
    # 2. nothing to move (a full pocket): the shard is put back key by key, the same Properties object, every key as before
    _seed(L, p, MI)
    K.check('restore(p, old); return "";' in g and 'p.clear(); p.putAll(old); return "";' not in g, "X33 the no-move path restores key by key (no clear())")
    before = _props(p)
    sk0 = Sacks(OWNER, room=0)
    Lk.FN_TEST = L["PyFn"](sk0)
    K.eq(int(Lk.run(ou, JString(OWNER), MI)), 0, "X33 a full pocket: nothing moves")
    K.check(St.get(JString(OWNER)) is p or St.get(JString(OWNER)).equals(p), "X33 ... the same shard object")
    K.eq(_props(p), before, "X33 ... every key exactly as before (the settle + the roll undone)")
    # 3. the Moon Blade cache is warmed (outside the lock) before take() settles
    Tot = JClass(PKG + "ShTotem")
    Tot.MOON_CACHE.clear()
    calls = []

    def moon(o):
        calls.append(str(o))
        return JClass("java.lang.Double")(2.0)
    Tot.MOON_TEST = L["PyFn"](moon)
    _seed(L, p, FK)
    sk = Sacks(OWNER)
    Lk.FN_TEST = L["PyFn"](sk)
    Lk.run(ou, JString(OWNER), FK)
    K.check(OWNER in calls and Tot.MOON_CACHE.containsKey(JString(OWNER)), "X33 the Moon Blade bridge asked (cache warm) before the transfer settles: %s" % calls[:3])
    Tot.MOON_TEST = None
    Tot.MOON_CACHE.clear()
    # 4. no SkyySacks any more: the page line goes
    Lk.LINE.put(JString(OWNER + "|0"), JString("Linked to pocket (Mining): new items go straight there."))
    Lk.FN_TEST = None
    if L["ShCfg"].fn(JString("sacks:fn:link")) is None:
        K.eq(int(Lk.run(ou, JString(OWNER), MI)), 0, "X33 no sacks:fn:link: nothing")
        K.check(Lk.line(JString(OWNER), MI) is None, "X33 ... and no 'Linked to pocket' line")
    # 5. an ack SkyySacks did not answer is kept (on disk) and asked again - also after a restart, also with no link on
    _seed(L, p, MI)
    sk = Sacks(OWNER)
    sk.mode = "noack"
    Lk.FN_TEST = L["PyFn"](sk)
    n = int(Lk.run(ou, JString(OWNER), MI))
    ak = str(p.getProperty("mining.linkack") or "")
    disk = open(os.path.join(str(St.DIR), OWNER + ".properties"), encoding="latin-1").read()
    K.check(n > 0 and str(p.getProperty("mining.linkpend") or "") == "" and len(sk.marks) == 1 and ak == list(sk.marks)[0] and ("mining.linkack=" + ak) in disk,
            "X33 the ack is lost: moved %d, settled, the token kept in mining.linkack (on disk)" % n)
    St.CACHE.remove(JString(OWNER))   # the restart
    p = St.get(JString(OWNER))
    sk.mode = None
    sk.active = set()                 # and no link on any more
    Lk.tickOne(ou)
    K.check(not sk.marks and str(p.getProperty("mining.linkack") or "") == "", "X33 ... after a restart, with no link on: the tick acks it again (marker gone, the line gone)")
    sk.active = {"Mining", "Smithing", "Foraging", "Farming", "Combat"}
    _seed(L, p, MI)
    n = int(Lk.run(ou, JString(OWNER), MI))
    K.check(n > 0 and not sk.marks and str(p.getProperty("mining.linkack") or "") == "", "X33 an answered ack leaves no line, no marker")
    K.eq(str(Lk.addTok(JString(",".join("t%d" % i for i in range(25))), JString("tz"))).split(",")[-1], "tz", "X33 the ack list keeps the newest")
    K.eq(len(str(Lk.addTok(JString(",".join("t%d" % i for i in range(25))), JString("tz"))).split(",")), 20, "X33 ... at most 20")
    K.save()


def run_live(out, jar, scratch, home):
    T432.T431.run_live(out, jar, scratch, home)


EXPECT = {   # 0.4.32 -> 0.4.33: Collect all runs the link first, the page runs it + shows the line, the tick; the rest = the @VERSION@ string
    'SkyyShardsPlugin': ['~m setup'], 'ShCore': ['~m collect0'], 'ShPage': ['~m build0', '~m ckPost'], 'ShTick': ['~m runIn'],
    'CfgFn': ['~m opExport'], 'CfgRows': ['~m header'], 'ShFill': ['~m markFixed'],
    'ShStore': ['~m migrate', '~m migrate2', '~m migrate3', '~m migrate4', '~m migrate5', '~m migrate6', '~m save'],
}

PHASES = [("static", run_static), ("link33", run_link), ("restart33", run_restart), ("gates33", run_gates), ("fix33", run_fix)] + \
         [x for x in T432.PHASES if x[0] not in ("static", "livemig32")] + [("livemig33", T431.run_live)]


if __name__ == "__main__":
    ph = PHASES
    if "--only" in sys.argv and "--phase" not in sys.argv:
        want = set(HK.arg("--only").split(","))
        ph = [x for x in PHASES if x[0] in want]
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=["ShLink"],
           phases=ph, script=__file__, live=(T431.T416.T46.LIVE_SH, "mods/Skyy_SkyyShards"))
