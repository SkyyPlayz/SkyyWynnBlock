"""Harness for SkyyGear 0.3.60 (round skl2: gear:fn:shop = the Anvil's own code for SkyyMenu 0.3.68's skill page workshop -
tools/gear_0_3_60_patch.py header).
Build first (the build needs Quirk's private art; in a worktree: SKYWYNN_PRIVATE_ART=<path to SkyWynn-PRIVATE-art>):
    python tools/gear_0_3_60_patch.py && python SkyyGear/build_skyygear_0.3.60.py
    python SkyyGear/test_skyygear_0.3.60.py [--keep] [--expect-dump]

Phases (fresh child processes / JVMs, tools/harness_kit.py; the 0.3.59 jar is the compare base):
  S  static    the patch re-runs to identical bytes; ONE new class (GearShopFn), no system / command; no jar entry removed, the only new entry =
               GearShopFn.class; the only changed non-class entry = manifest.json (no lang / item / art change); the bridge key is put + removed
  A  verify    every class loads + initialises with -Xverify:all
  C  compare   0.3.59 -> 0.3.60 (EXPECT below)
  E  engine    the 0.2.11 harness's bare server boot (vanilla pack + THIS jar), REAL Inventory objects, Python stand-ins of SkyyCoins / SkyySkills /
               the profile keys - every new path EXECUTED:
               TWIN  for a tool and an armour piece of each skill page (Mining pickaxe, Foraging hatchet, Farming hoe, Fishing / Combat pieces,
                     Combat sword): workshop act forge / lvl / up / sg on inventory A == the Anvil's own core (GearForge.reforge / levelUp, GearUp.upgrade,
                     GearSigil.apply) on the identical inventory B: same answer code, coins taken, item id, rarity, level, line count, materials /
                     Sigils used
               READ  the read answer = the Anvil's card numbers (costReforge / costLevelUp / lvlInfo / GearUp.preview + cost / GearSigil choices),
                     the key = the fingerprint, an empty place = x, every field without '|' / line breaks
               SAFE  a stale token, profile:busy, a double click (400 ms), the item moved / changed (a stale page after a paid action = refused,
                     nothing paid twice), not enough coins (nothing taken), an unidentified item, a Sigil that does not fit, Apply = arm then Confirm
                     (10 s, this item + this Sigil), a bad op; apply() off the world thread / junk arguments = null; the counters
  E59 / E58 / E57 / E56 / E55 / E54  the earlier harnesses' engine phases against THIS jar (every earlier check still passes)
  D  live      start twice on a scratch COPY of Skyy's live Skyy_SkyyGear (the 0.3.58 live phase): no one-time update, the second start changes nothing
  AA engine-access audit
NOT COVERED (UNVERIFIED in game): the real Universe player lookup + Store.isInThread inside apply() (the harness has no world; the core it calls
is executed with a REAL inventory); SkyyMenu's page drawing it (SkyyMenu/test_skyymenu_0.3.68.py).
Scratch: tools/dev/scratch/skl2/gear (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, re, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION = "0.3.60"
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "skl2", "gear")]
import skyybuild as B
import harness_kit as HK

GEN = os.path.join(HERE, "build_skyygear_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyygear_0.3.59.py")
PATCH = os.path.join(ROOT, "tools", "gear_0_3_60_patch.py")
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyGear-0.3.59.jar")
SCRATCH = os.path.abspath(HK.arg("--dir"))
PKG = "com.skyy.gear."
T59 = {"__file__": os.path.join(HERE, "test_skyygear_0.3.59.py"), "__name__": "t59"}
_s = open(T59["__file__"], encoding="utf8").read()
exec(compile(_s[:_s.rindex(chr(10) + 'HK.run_compare = T54["run_compare54"]')], T59["__file__"], "exec"), T59)
T58, T57, T56, T55, T54 = T59["T58"], T59["T57"], T59["T56"], T59["T55"], T59["T54"]
for _t in (T54, T55, T56, T57, T58, T59):
    _t["SCRATCH"] = SCRATCH
ADDED = ["GearShopFn"]
EXPECT = None if "--expect-dump" in sys.argv else {
    'CfgRows': ['~m header'], 'CfgRows2': ['~<clinit>'], 'CfgFn': ['~m opExport'], 'GearCfg': ['~m defaultsText'],          # the version texts
    'SkyyGearPlugin': ['~m setup', '~m shutdown'],          # gear:fn:shop put / removed
    'GearBye': ['~m accept'],          # fix round: the player left = gear:fn:shop 'bye' (its per-player maps)
}
U = "00000000-0000-0000-0000-000000000360"
UB = "00000000-0000-0000-0000-000000000361"          # the twin (the Anvil's own core) runs as another player: its own purse


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyGear 0.3.60 - build script') and g.count('VERSION = "0.3.60"') == 1, "S header + VERSION")
    K.eq([g.count(w) - o.count(w) for w in ("registerSystem(", "registerCommand(", 'mk("')], [0, 0, 1], "S one new class (GearShopFn), no system / command")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, "build.py")
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-runs to identical bytes: %s" % p.stderr[-300:])
    K.check((b"\r\n" in open(GEN_OLD, "rb").read()) == (b"\r\n" in open(GEN, "rb").read()), "S line endings kept")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.eq(sorted(set(zn.namelist()) - set(zo.namelist())), ["com/skyy/gear/GearShopFn.class"], "S the only new jar entry = GearShopFn.class")
    K.eq(sorted(set(zo.namelist()) - set(zn.namelist())), [], "S no jar entry removed")
    K.eq(sorted(n for n in zn.namelist() if not n.endswith(".class") and n in zo.namelist() and zn.read(n) != zo.read(n)), ["manifest.json"],
         "S the only changed non-class entry = manifest.json (no lang / item / quality / art change)")
    K.check('br.put("gear:fn:shop", new @PKG@.GearShopFn());' in g and 'bq.remove("gear:fn:shop");' in g, "S gear:fn:shop put in setup, removed at shutdown")
    sh = g[g.index('gshop = mk("GearShopFn")'):g.index('_fns = "\\n".join(')]
    for call in ("@PKG@.GearForge.reforge(", "@PKG@.GearForge.levelUp(", "@PKG@.GearUp.upgrade(", "@PKG@.GearSigil.apply(", "@PKG@.GearForge.lvlInfo(",
                 "@PKG@.GearUp.preview(", "@PKG@.GearUp.shortOfU(", "@PKG@.GearSigil.choices(", "@PKG@.GearSigil.why(", "@PKG@.GearCfg.costReforge(",
                 "@PKG@.GearCfg.costLevelUp(", "@PKG@.ReforgePage.anLvShort(", "@PKG@.ReforgePage.upWhyNot(", "@PKG@.GearReq.levelRow(", "@PKG@.GearReq.collRow("):
        K.check(call in sh, "S GearShopFn calls the Anvil's own %s" % call)
    K.check("isInThread()" in sh and "if (!onThread(u)) { N[3] = N[3] + 1L; return null; }" in sh, "S apply() reads / acts on the player's world thread only")
    K.check(not re.search(r"\b(?:costReforge|costLevelUp)\s*=", sh) and "new java.util.Random" not in sh and "SecureRandom" not in sh,
            "S no number of its own: every cost / roll is the Anvil's")
    K.save()


def run_engine(out, jar, scratch, home):
    from jpype import JClass, JInt, JString, JImplements, JOverride, JObject, JArray, JLong, JShort, JByte
    K = HK.Child(out)
    h211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
    t = open(h211, encoding="utf-8").read()
    t = t[:t.index("def run_engine(out):")]
    esc = os.path.join(scratch, "eng60")
    os.makedirs(esc, exist_ok=True)
    argv0 = sys.argv
    sys.argv = [h211, "--jar", jar, "--dir", esc]
    H = {"__name__": "skyygear_h211_lib", "__file__": h211, "__builtins__": __builtins__}
    exec(compile(t, h211 + " (engine boot, library)", "exec"), H)
    sys.argv = argv0
    H.update({"JAR": jar, "SCRATCH": esc, "VERSION": VERSION})
    H["_jvm"]([B.SERVER_JAR, B.JAVASSIST, jar], verify=True, big=True)

    class KC(object):
        def __init__(self, k):
            self.k = k
            self.notes = k.notes

        def check(self, c, w):
            return self.k.check(c, "E boot: " + w)
    E = H["engine_boot"](KC(K))
    us = E["us"]
    P = lambda n: JClass(PKG + n)
    Cfg, Data, Roll, Defs, Forge, Up, Sig, Shop, Lvl, Gear = (P("GearCfg"), P("GearData"), P("GearRoll"), P("GearDefs"), P("GearForge"), P("GearUp"),
                                                             P("GearSigil"), P("GearShopFn"), P("GearLevel"), P("Gear"))
    Props = JClass("java.util.Properties")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    BS = JClass("org.bson.BsonString")
    UUID = JClass("java.util.UUID")
    Paths = JClass("java.nio.file.Paths")
    OA = JArray(JObject)
    u, ub = UUID.fromString(U), UUID.fromString(UB)
    sysp = JClass("java.lang.System").getProperties()
    br = sysp.get("skyy.bridge")
    if br is None:
        br = JClass("java.util.concurrent.ConcurrentHashMap")()
        sysp.put("skyy.bridge", br)
    data = os.path.join(scratch, "data60")
    os.makedirs(data, exist_ok=True)
    Cfg.DIR = Paths.get(data)
    fresh = str(Cfg.defaultsText())

    def apply(**kv):
        p = Props()
        p.load(JClass("java.io.StringReader")(fresh))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    BASE = {"part__gate": "false"}
    apply(**BASE)

    @JImplements("java.util.function.Function")
    class PyFn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, a):
            return self.f(a)
    PURSE = {U: 100000, UB: 100000}
    TAKEN = []

    def c_get(a):
        return JObject(JLong(PURSE.get(str(a), -1)), "java.lang.Long")

    def c_take(a):
        k_, n_ = str(a[0]), int(a[1])
        if PURSE.get(k_, 0) < n_:
            return JObject(False, "java.lang.Boolean")
        PURSE[k_] -= n_
        TAKEN.append((k_, n_))
        return JObject(True, "java.lang.Boolean")

    def c_add(a):
        PURSE[str(a[0])] = PURSE.get(str(a[0]), 0) + int(a[1])
        return JObject(JLong(PURSE[str(a[0])]), "java.lang.Long")
    br.put("coins:fn:get", PyFn(c_get))
    br.put("coins:fn:take", PyFn(c_take))
    br.put("coins:fn:add", PyFn(c_add))
    br.put("skill:fn:level", PyFn(lambda a: JObject(JInt(60), "java.lang.Integer")))
    for k_ in (u, ub):
        br.put("class:skill:" + str(k_), "Swordsmanship")
        br.put("profile:epoch:" + str(k_), "ep1")
    br.put("coll:fn:tierup", PyFn(lambda a: JString("1|X|X|9|1|1")))

    def fld(cls, name):
        k = cls.class_ if hasattr(cls, "class_") else cls
        while k is not None:
            try:
                f = k.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(name)
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    SECS = (("hotbar", "Hotbar", 9), ("storage", "Storage", 36), ("backpack", "Backpack", 9), ("armor", "Armor", 4), ("utility", "Utility", 4), ("tools", "Tool", 4))
    SECN = {"hotbar": 0, "storage": 1, "backpack": 2, "armor": 3}

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        fld(Cc, "inventory").set(o_, cont)
        return o_

    def mkinv():
        inv_ = INV()
        cs_ = {}
        for f_, kind, n_ in SECS:
            cs_[f_] = SIC(JShort(n_))
            try:
                fld(INV, f_).set(inv_, comp(kind, cs_[f_]))
            except Exception:
                fld(INV, f_).set(inv_, cs_[f_])
        return inv_, cs_

    def doc(iid, r, lv=20, src="admin", ident=True):
        d_ = Roll.newDoc(JString(iid), JInt(r), ident, JString(src), JInt(lv))
        d_.put("r", BS(Defs.R_ID[r]))
        return d_

    def gstack(iid, r, lv=20, ident=True, uu=None):
        return Data.put(IS(JString(iid), JInt(1)), doc(iid, r, lv, "admin", ident), uu or u)

    def counts(cs_):
        n = {}
        for f_, _k, _n in SECS:
            c_ = cs_[f_]
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is not None and not s_.isEmpty():
                    n[str(s_.getItemId())] = n.get(str(s_.getItemId()), 0) + int(s_.getQuantity())
        return n

    def state(cs_, sec, sl):
        s_ = cs_[sec].getItemStack(JShort(sl))
        if s_ is None or s_.isEmpty():
            return None
        d_ = Forge.docOf(s_.getItemId(), s_.getMetadata())
        return (str(s_.getItemId()), None if d_ is None else int(Data.rarity(d_)), int(Lvl.level(s_.getItemId(), d_)), None if d_ is None else int(Data.mods(d_).size()))

    def keyOf(cs_, sec, sl):
        return str(Shop.key(cs_[sec].getItemStack(JShort(sl))))

    def parse(ans):
        rows = [r_.split("|") for r_ in str(ans).split("\n")]
        return rows[0], rows[1:]
    RID = [str(x) for x in Defs.R_ID]
    R = dict((n_, RID.index(n_)) for n_ in RID)
    exists = lambda iid: Gear.item(JString(iid)) is not None
    SIG_IDS = [str(x) for x in Sig.IDS]
    SIG_RANK = [int(x) for x in Sig.RANK]
    sigil = dict((SIG_RANK[i_], SIG_IDS[i_]) for i_ in range(len(SIG_IDS)))
    K.notes.append("Sigil ids by rank: %s" % sigil)

    def pick(*ids):          # armour / weapons: a forgeable one
        for i_ in ids:
            if exists(i_) and bool(Data.forgeable(JString(i_))):
                return i_
        return None

    def tool(*ids):          # tools: whatever the boot has (a plain tool the Anvil refuses is a fair twin too)
        for i_ in ids:
            if exists(i_):
                return i_
        return None
    # the skill pages' tools + armour (what SkyyMenu 0.3.68 sends: the tool slot + the armour slots)
    CASES = [("Mining tool", tool("Tool_Pickaxe_Iron", "Tool_Pickaxe_Lead_SkyWynn", "Tool_Pickaxe_Bronze_SkyWynn"), "hotbar", 0),
             ("Mining armour", pick("Armor_Iron_Head", "Armor_Copper_Head"), "armor", 0),
             ("Foraging tool", tool("Tool_Hatchet_Iron", "Tool_Hatchet_Lead_SkyWynn", "Tool_Hatchet_Bronze_SkyWynn"), "hotbar", 1),
             ("Foraging armour", pick("Armor_Iron_Chest", "Armor_Copper_Chest"), "armor", 1),
             ("Farming tool", pick("Tool_Hoe_Iron", "Tool_Hoe_Copper", "Tool_Hoe_Crude", "Tool_Sickle_Iron"), "storage", 4),
             ("Farming armour", pick("Armor_Iron_Hands", "Armor_Copper_Hands"), "armor", 2),
             ("Fishing armour", pick("Armor_Iron_Legs", "Armor_Copper_Legs"), "armor", 3),
             ("Combat tool", pick("Weapon_Sword_Iron", "Weapon_Sword_Copper"), "hotbar", 2),
             ("Combat armour", pick("Armor_Thorium_Chest", "Armor_Iron_Chest"), "backpack", 3)]
    K.notes.append("cases: %s" % [(c_[0], c_[1]) for c_ in CASES])
    miss_ = [c_[0] for c_ in CASES if not c_[1]]
    K.check(not [m_ for m_ in miss_ if m_ not in ("Mining tool", "Foraging tool")], "E every skill page's armour / weapon / hoe stand-in exists in this boot: %s" % miss_)
    if miss_:          # the bare boot's asset validation drops the pickaxes / hatchets (their stat assets are missing here) - UNVERIFIED on those two ids
        K.notes.append("UNVERIFIED in this boot (no item asset): %s - the hoe is the tool case (the same GearForge / GearUp / GearSigil code)" % miss_)
    K.notes.append("forgeable: %s" % [(c_[1], bool(Data.forgeable(JString(c_[1])))) for c_ in CASES if c_[1]])
    CASES = [c_ for c_ in CASES if c_[1]]

    def twin(iid, sec, sl, r=0, lv=20, extra=()):
        a_, ca = mkinv()
        b_, cb = mkinv()
        ca[sec].setItemStackForSlot(JShort(sl), gstack(iid, r, lv, uu=u))
        cb[sec].setItemStackForSlot(JShort(sl), gstack(iid, r, lv, uu=ub))
        for s2, k2, x2, q2 in extra:
            ca[s2].setItemStackForSlot(JShort(k2), IS(JString(x2), JInt(q2)))
            cb[s2].setItemStackForSlot(JShort(k2), IS(JString(x2), JInt(q2)))
        return a_, ca, b_, cb

    def act(inv_, op, at, iid, key, Rr=0, tok="ep1"):
        Shop.LAST.clear()
        return str(Shop.act(inv_, u, JString("Tester"), JString(tok), JString(op), JString(at), JString(iid), JString(key), JInt(Rr)))

    # ================================================================================== READ
    rb = []
    for name, iid, sec, sl in CASES:
        a_, ca, _b, _cb = twin(iid, sec, sl, R["rare"], 20)
        at = "%d:%d" % (SECN[sec], sl)
        ans = str(Shop.read(a_, u, JString(at + ";-;9:9;" + at)))
        h_, rows = parse(ans)
        if h_[:2] != ["ok", "ep1"] or int(h_[2]) != PURSE[U] or len(h_) != 7:
            rb.append((name, "head", h_))
        if any("\r" in r_ for r_ in ans.split("\n")):
            rb.append((name, "a line break inside a field"))
        i_ = [r_ for r_ in rows if r_[0] == "i" and r_[1] == "0"]
        x_ = sorted(r_[1] for r_ in rows if r_[0] == "x")
        if x_ != ["1", "2"] or len([r_ for r_ in rows if r_[0] == "i"]) != 2:
            rb.append((name, "the empty / bad places = x, the item twice", x_))
        if not i_ or len(i_[0]) != 15 or i_[0][4] != iid or i_[0][5] != keyOf(ca, sec, sl) or i_[0][5] != str(Forge.fp(ca[sec].getItemStack(JShort(sl)))).replace("|", "/") \
                or int(i_[0][7]) != R["rare"] or i_[0][2] != str(SECN[sec]) or i_[0][3] != str(sl):
            rb.append((name, "i line", i_))
            continue
        st_ = ca[sec].getItemStack(JShort(sl))
        d_ = Forge.docOf(st_.getItemId(), st_.getMetadata())
        lv_ = int(Lvl.level(JString(iid), d_))
        f_ = [r_ for r_ in rows if r_[0] == "f" and r_[1] == "0"][0]
        if int(f_[3]) != int(Cfg.costReforge(JInt(R["rare"]), JInt(lv_))) or f_[2] != "0" or f_[5] != "Reforge":
            rb.append((name, "f = the Anvil's reforge cost", f_, int(Cfg.costReforge(JInt(R["rare"]), JInt(lv_)))))
        li_ = Forge.lvlInfo(u, JString(iid), d_)
        l_ = [r_ for r_ in rows if r_[0] == "l" and r_[1] == "0"][0]
        if int(l_[3]) != int(Cfg.costLevelUp(JInt(R["rare"]), JInt(int(li_[2])))) or (int(li_[0]) == 0) != (l_[2] in ("0", "1")):
            rb.append((name, "l = the Anvil's level-up row", l_, list(li_)))
        u_ = [r_ for r_ in rows if r_[0] == "u" and r_[1] == "0"][0]
        pv = Up.preview(st_, u) if Up.next(JString(iid)) is not None else None
        why_ = None if pv is None else (pv[0] if pv[0] is not None else Up.shortOfU(a_, u, pv[6]))
        if pv is not None and ((why_ is None) != (u_[2] == "0")):
            rb.append((name, "u = GearUp.preview + shortOfU's verdict", u_, str(why_)))
        mats = [r_ for r_ in rows if r_[0] == "m" and r_[1] == "0"]
        if pv is not None and pv[6] is not None and [m_[2] for m_ in mats] != [str(x) for x in pv[6][0]]:
            rb.append((name, "m = the cost's materials in order", mats))
        if not [r_ for r_ in rows if r_[0] == "w" and r_[1] == "0"] or not [r_ for r_ in rows if r_[0] == "s" and r_[1] == "0"]:
            rb.append((name, "w + s lines"))
        K.notes.append("READ %s: %s" % (name, " / ".join("|".join(r_) for r_ in rows if r_[1] == "0")[:600]))
    K.check(not rb, "READ the answer = the Anvil's card numbers for every skill page's tool + armour (head, i / f / l / u / m / w / s, x for empty): %s" % rb[:3])

    # ================================================================================== TWIN: the workshop act == the Anvil's own core
    tb = []
    for name, iid, sec, sl in CASES:
        at = "%d:%d" % (SECN[sec], sl)
        # REFORGE
        a_, ca, b_, cb = twin(iid, sec, sl, R["rare"], 20)
        PURSE[U] = PURSE[UB] = 100000
        ra = act(a_, "forge", at, iid, keyOf(ca, sec, sl))
        sB = cb[sec].getItemStack(JShort(sl))
        rbx = Forge.reforge(cb[sec], JInt(sl), JString(iid), Forge.fp(sB), ub, JString("Tester"), False, P("GearStamp").giveOf(b_), P("GearStamp").allOf(b_))
        if (ra.startswith("+")) != (int(rbx[0]) == 1) or PURSE[U] != PURSE[UB] or state(ca, sec, sl)[:3] != state(cb, sec, sl)[:3] or state(ca, sec, sl)[3] != state(cb, sec, sl)[3] \
                or counts(ca) != counts(cb):
            tb.append((name, "forge", ra, int(rbx[0]), str(rbx[1]), PURSE[U], PURSE[UB], state(ca, sec, sl), state(cb, sec, sl)))
        K.notes.append("TWIN %s forge: %s | coins %d" % (name, ra, 100000 - PURSE[U]))
        # LEVEL UP
        a_, ca, b_, cb = twin(iid, sec, sl, R["rare"], 20)
        PURSE[U] = PURSE[UB] = 100000
        ra = act(a_, "lvl", at, iid, keyOf(ca, sec, sl))
        sB = cb[sec].getItemStack(JShort(sl))
        rbx = Forge.levelUp(cb[sec], JInt(sl), JString(iid), Forge.fp(sB), ub, JString("Tester"), P("GearStamp").giveOf(b_), P("GearStamp").allOf(b_))
        if (ra.startswith("+")) != (int(rbx[0]) == 1) or PURSE[U] != PURSE[UB] or state(ca, sec, sl) != state(cb, sec, sl) or counts(ca) != counts(cb):
            tb.append((name, "lvl", ra, int(rbx[0]), str(rbx[1]), state(ca, sec, sl), state(cb, sec, sl)))
        if not ra.startswith("+"):
            K.notes.append("TWIN %s lvl refused on both: %s" % (name, ra))
        # UPGRADE (the materials of the next tier in the bag of both)
        nx = Up.next(JString(iid))
        extra = []
        if nx is not None:
            c_ = Up.cost(JString(iid), nx)
            if c_ is not None:
                for j_ in range(len(c_[0])):
                    extra.append(("storage", 10 + j_, str(c_[0][j_]), int(c_[1][j_])))
        a_, ca, b_, cb = twin(iid, sec, sl, R["rare"], 20, extra)
        PURSE[U] = PURSE[UB] = 100000
        ra = act(a_, "up", at, iid, keyOf(ca, sec, sl))
        sB = cb[sec].getItemStack(JShort(sl))
        rbx = Up.upgrade(b_, JInt(SECN[sec]), JInt(sl), JString(iid), Forge.fp(sB), ub, JString("Tester"))
        if (ra.startswith("+")) != (int(rbx[0]) == 1) or PURSE[U] != PURSE[UB] or state(ca, sec, sl) != state(cb, sec, sl) or counts(ca) != counts(cb):
            tb.append((name, "up", ra, int(rbx[0]), str(rbx[1]), state(ca, sec, sl), state(cb, sec, sl)))
        K.notes.append("TWIN %s up (%s -> %s): %s" % (name, iid, nx, ra))
        # SIGIL: arm, then confirm (the twin: GearSigil.apply once)
        a_, ca, b_, cb = twin(iid, sec, sl, R["normal"], 20, [("storage", 20, sigil[R["legendary"]], 2)])
        k0 = keyOf(ca, sec, sl)
        r1 = act(a_, "sg", at, iid, k0, R["legendary"])
        r2 = act(a_, "sg", at, iid, k0, R["legendary"])
        sB = cb[sec].getItemStack(JShort(sl))
        rbx = Sig.apply(b_, JInt(SECN[sec]), JInt(sl), JString(iid), Forge.fp(sB), JInt(R["legendary"]), ub, JString("Tester"))
        if not r1.startswith("=Click Confirm sigil") or (r2.startswith("+")) != (int(rbx[0]) == 1) or state(ca, sec, sl) != state(cb, sec, sl) or counts(ca) != counts(cb):
            tb.append((name, "sg", r1, r2, int(rbx[0]), str(rbx[1]), state(ca, sec, sl), state(cb, sec, sl)))
        K.notes.append("TWIN %s sg: %s / %s" % (name, r1[:60], r2))
    K.check(not tb, "TWIN workshop forge / lvl / up / sg == the Anvil's own core on an identical inventory (code, coins, item, rarity, level, lines, materials / Sigils): %s" % tb[:2])
    # at least one of each action really went through (else the twin proves only refusals)
    ok_ = {}
    for name, iid, sec, sl in [c_ for c_ in CASES if c_[0] in ("Combat tool", "Mining armour", "Farming tool")]:
        at = "%d:%d" % (SECN[sec], sl)
        for op in ("forge", "lvl", "sg"):
            a_, ca, b_, cb = twin(iid, sec, sl, R["normal"], 10, [("storage", 20, sigil[R["rare"]], 1)])
            PURSE[U] = 100000
            k0 = keyOf(ca, sec, sl)
            r_ = act(a_, op, at, iid, k0, R["rare"])
            if op == "sg":
                r_ = act(a_, op, at, iid, k0, R["rare"])
            ok_.setdefault(op, []).append(r_[:70])
    K.check(all(any(x_.startswith("+") for x_ in ok_[op]) for op in ("forge", "lvl", "sg")), "TWIN a reforge, a level up and a Sigil really went through: %s" % ok_)

    # ================================================================================== SAFE
    sb = []
    name, iid, sec, sl = CASES[0]
    at = "%d:%d" % (SECN[sec], sl)
    a_, ca, _b, _cb = twin(iid, sec, sl, R["rare"], 20)
    PURSE[U] = 100000
    k0 = keyOf(ca, sec, sl)
    s0 = state(ca, sec, sl)
    r_ = act(a_, "forge", at, iid, k0, tok="ep0")
    if not r_.startswith("=Your profile changed") or PURSE[U] != 100000 or keyOf(ca, sec, sl) != k0:
        sb.append(("stale token", r_))
    br.put("profile:busy:" + U, True)
    r_ = act(a_, "forge", at, iid, k0)
    br.remove("profile:busy:" + U)
    if not r_.startswith("-Your profile is still loading") or PURSE[U] != 100000:
        sb.append(("busy", r_))
    r_ = act(a_, "forge", at, iid, k0 + "x")
    if not r_.startswith("-That item moved") or PURSE[U] != 100000:
        sb.append(("wrong key", r_))
    r_ = act(a_, "forge", "%d:%d" % (SECN[sec], sl + 1), iid, k0)
    if not r_.startswith("-That item moved") or PURSE[U] != 100000:
        sb.append(("wrong place", r_))
    r_ = act(a_, "lvl", at, "Weapon_Nope", k0)
    if not r_.startswith("-That item moved"):
        sb.append(("wrong id", r_))
    r1 = act(a_, "forge", at, iid, k0)
    paid = 100000 - PURSE[U]
    Shop.LAST.clear()
    r2 = str(Shop.act(a_, u, JString("Tester"), JString("ep1"), JString("forge"), JString(at), JString(iid), JString(k0), JInt(0)))
    r3 = str(Shop.act(a_, u, JString("Tester"), JString("ep1"), JString("forge"), JString(at), JString(iid), JString(keyOf(ca, sec, sl)), JInt(0)))
    if not r1.startswith("+Reforged!") or paid <= 0 or not r2.startswith("-That item moved") or r3 != "=One moment." or 100000 - PURSE[U] != paid:
        sb.append(("a stale page after a paid reforge = moved; a second click within 400 ms = One moment; paid ONCE", r1, r2, r3, paid, 100000 - PURSE[U]))
    PURSE[U] = 5
    k1 = keyOf(ca, sec, sl)
    s1 = state(ca, sec, sl)
    r_ = act(a_, "forge", at, iid, k1)
    if not r_.startswith("-Not enough coins") or PURSE[U] != 5 or state(ca, sec, sl) != s1 or keyOf(ca, sec, sl) != k1:
        sb.append(("not enough coins: nothing taken, nothing changed", r_))
    h_, rows = parse(Shop.read(a_, u, JString(at)))
    f_ = [x_ for x_ in rows if x_[0] == "f"][0]
    if f_[2] != "1" or "need" not in f_[4] or f_[5] != "Not enough coins":
        sb.append(("read says the coins are short", f_))
    PURSE[U] = 100000
    # unidentified
    a2, c2, _b, _cb = mkinv()[0], None, None, None
    a2, c2 = mkinv()
    SWU = "Weapon_Sword_Iron"
    c2["hotbar"].setItemStackForSlot(JShort(0), Data.put(IS(JString(SWU), JInt(1)), Roll.newDoc(JString(SWU), JInt(R["rare"]), False, JString("craft"), JInt(10)), u))
    r_ = act(a2, "forge", "0:0", SWU, keyOf(c2, "hotbar", 0))
    if not r_.startswith("-Identify it first") or PURSE[U] != 100000:
        sb.append(("unidentified", r_))
    h_, rows = parse(Shop.read(a2, u, JString("0:0")))
    if [x_ for x_ in rows if x_[0] == "i"][0][12] != "1" or [x_ for x_ in rows if x_[0] == "f"][0][5] != "Identify it first":
        sb.append(("read: unidentified", rows[:3]))
    # Sigils: no Sigil carried, one below the rarity, arm on another item does not confirm this one, a Sigil you do not carry
    a3, c3 = mkinv()
    c3["hotbar"].setItemStackForSlot(JShort(0), gstack(iid, R["legendary"], 20))
    c3["hotbar"].setItemStackForSlot(JShort(1), gstack(iid, R["normal"], 20))
    c3["storage"].setItemStackForSlot(JShort(0), IS(JString(sigil[R["rare"]]), JInt(1)))
    h_, rows = parse(Shop.read(a3, u, JString("0:0;0:1")))
    s0_ = [x_ for x_ in rows if x_[0] == "s" and x_[1] == "0"][0]
    s1_ = [x_ for x_ in rows if x_[0] == "s" and x_[1] == "1"][0]
    c1_ = [x_ for x_ in rows if x_[0] == "c" and x_[1] == "1"]
    if s0_[2] != "2" or s1_[2] != "0" or len(c1_) != 1 or c1_[0][2] != str(R["rare"]) or c1_[0][7] != "0":
        sb.append(("read Sigil: none above Legendary / Rare fits a Normal", s0_, s1_, c1_))
    r_ = act(a3, "sg", "0:0", iid, keyOf(c3, "hotbar", 0), R["rare"])
    if not r_.startswith("-You carry no Sigil above") and not r_.startswith("-"):
        sb.append(("a Sigil below the rarity", r_))
    r_ = act(a3, "sg", "0:1", iid, keyOf(c3, "hotbar", 1), R["fabled"])
    if not r_.startswith("-You do not carry a"):
        sb.append(("a Sigil not carried", r_))
    ra1 = act(a3, "sg", "0:1", iid, keyOf(c3, "hotbar", 1), R["rare"])
    h_, rows = parse(Shop.read(a3, u, JString("0:0;0:1")))
    armed_ = [x_ for x_ in rows if x_[0] == "c" and x_[1] == "1"][0][7]
    ro = act(a3, "lvl", "0:0", iid, keyOf(c3, "hotbar", 0))
    ra2 = act(a3, "sg", "0:1", iid, keyOf(c3, "hotbar", 1), R["rare"])
    if not ra1.startswith("=Click Confirm sigil") or armed_ != "1" or not ra2.startswith("=Click Confirm sigil") or counts(c3).get(sigil[R["rare"]]) != 1:
        sb.append(("arm; another action in between disarms (the next click arms again, nothing spent)", ra1, armed_, ro, ra2))
    ra3 = act(a3, "sg", "0:1", iid, keyOf(c3, "hotbar", 1), R["rare"])
    if not ra3.startswith("+Your ") or counts(c3).get(sigil[R["rare"]]) is not None or state(c3, "hotbar", 1)[1] != R["rare"]:
        sb.append(("confirm = the Sigil used, the item Rare", ra3, counts(c3)))
    ra4 = act(a3, "sg", "0:1", iid, keyOf(c3, "hotbar", 1), R["rare"])
    if not ra4.startswith("-"):
        sb.append(("a third click = refused (no Sigil left)", ra4))
    # an old arm runs out after 10 s
    a4, c4 = mkinv()
    c4["hotbar"].setItemStackForSlot(JShort(0), gstack(iid, R["normal"], 20))
    c4["storage"].setItemStackForSlot(JShort(0), IS(JString(sigil[R["rare"]]), JInt(1)))
    k4 = keyOf(c4, "hotbar", 0)
    act(a4, "sg", "0:0", iid, k4, R["rare"])
    Shop.ARM.put(u, JString("%s|%d|%d" % (k4, R["rare"], int(JClass("java.lang.System").currentTimeMillis()) - 11000)))
    r_ = act(a4, "sg", "0:0", iid, k4, R["rare"])
    if not r_.startswith("=Click Confirm sigil") or counts(c4).get(sigil[R["rare"]]) != 1:
        sb.append(("an arm older than 10 s arms again", r_))
    r_ = act(a4, "nope", "0:0", iid, k4)
    if not r_.startswith("-Unknown workshop action"):
        sb.append(("bad op", r_))
    r_ = str(Shop.act(None, u, JString("T"), JString("ep1"), JString("forge"), JString("0:0"), JString(iid), JString(k4), JInt(0)))
    if not r_.startswith("-You are not in a world"):
        sb.append(("no inventory", r_))
    # apply(): junk = null, no such player (off the world thread) = null, counters
    fn = Shop()
    n3 = int(Shop.N[3])
    junk = [fn.apply(None), fn.apply(JString("x")), fn.apply(OA([])), fn.apply(OA([u])), fn.apply(OA([JString("u"), JString("read"), JString("0:0")])),
            fn.apply(OA([u, JString("nope"), JString("0:0")]))]
    off = [fn.apply(OA([u, JString("read"), JString("0:0")])), fn.apply(OA([u, JString("act"), JString("ep1"), JString("forge"), JString("0:0"), JString(iid), JString(k4), JInt(0)]))]
    if [x_ for x_ in junk + off if x_ is not None] or int(Shop.N[3]) != n3 + 2:
        sb.append(("apply: junk / not on the world thread = null", [str(x_) for x_ in junk + off], int(Shop.N[3]) - n3))
    K.check(not sb, "SAFE stale token, busy, moved / wrong place / id, a stale page after a paid action, double click, coins short, unidentified, Sigil arm / confirm / "
                    "disarm / timeout / not carried, bad op, apply() guards - nothing paid twice: %s" % sb[:3])
    K.notes.append("counters N = %s" % [int(x) for x in Shop.N])
    K.check(int(Shop.N[1]) > 0 and int(Shop.N[2]) > 0 and int(Shop.N[4]) > 0 and int(Shop.N[5]) > 0 and int(Shop.N[6]) > 0 and int(Shop.N[8]) > 0,
            "SAFE the counters count done / refused / stale / double / moved / armed")
    # ================================================================================== FIX ROUND (critics of round skl2)
    # 1. the Anvil's "just upgraded" guard (ReforgePage.upDo upMade): a second / late Upgrade on the redrawn page (new key, > 400 ms) is refused
    #    for 3 s (it would take the NEXT tier's materials unasked); any other act or 3 s later = allowed again
    ug = []
    upc = [c_ for c_ in CASES if c_[0] in ("Mining armour", "Foraging armour", "Fishing armour", "Farming armour", "Combat tool") and Up.next(JString(c_[1])) is not None]
    done_ = False
    for name, iid, sec, sl in upc:
        nx = Up.next(JString(iid))
        c_ = Up.cost(JString(iid), nx)
        nn = Up.next(nx)
        c2_ = Up.cost(nx, nn) if nn is not None else None
        extra = []
        for cc_ in (c_, c2_):
            if cc_ is None:
                continue
            for j_ in range(len(cc_[0])):
                extra.append(("storage", 10 + len(extra), str(cc_[0][j_]), int(cc_[1][j_]) * 2))
        a5, c5, _b, _cb = twin(iid, sec, sl, R["rare"], 20, extra)
        PURSE[U] = 100000
        Shop.UPM.clear()
        r1 = act(a5, "up", "%d:%d" % (SECN[sec], sl), iid, keyOf(c5, sec, sl))
        if not r1.startswith("+Upgraded"):
            K.notes.append("UPGUARD %s: the first upgrade refused (%s) - next case" % (name, r1[:80]))
            continue
        done_ = True
        at = "%d:%d" % (SECN[sec], sl)
        iid2, k2 = state(c5, sec, sl)[0], keyOf(c5, sec, sl)
        s2, n2, p2 = state(c5, sec, sl), counts(c5), PURSE[U]
        r2 = act(a5, "up", at, iid2, k2)
        if not r2.startswith("-Already upgraded") or state(c5, sec, sl) != s2 or counts(c5) != n2 or PURSE[U] != p2 or keyOf(c5, sec, sl) != k2:
            ug.append(("a second Upgrade on the redrawn page within 3 s = refused, nothing taken", name, r1, r2))
        # 3 s later (the stamp aged) = the guard lets it through (the Anvil's own verdict decides)
        Shop.UPM.put(u, JString("%s|%d" % (k2, int(JClass("java.lang.System").currentTimeMillis()) - 3500)))
        r3 = act(a5, "up", at, iid2, k2)
        if r3.startswith("-Already upgraded"):
            ug.append(("3 s later the guard is gone", name, r3))
        K.notes.append("UPGUARD %s: %s / %s / %s" % (name, r1[:60], r2[:60], r3[:70]))
        # any other act clears it
        a6, c6, _b, _cb = twin(iid, sec, sl, R["rare"], 20, extra)
        Shop.UPM.clear()
        act(a6, "up", at, iid, keyOf(c6, sec, sl))
        iid6, k6 = state(c6, sec, sl)[0], keyOf(c6, sec, sl)
        ro = act(a6, "lvl", at, iid6, k6)
        if Shop.UPM.get(u) is not None:
            ug.append(("another act clears the guard", name, ro))
        # a profile switch clears it too
        Shop.UPM.put(u, JString("%s|%d" % (k6, int(JClass("java.lang.System").currentTimeMillis()))))
        act(a6, "forge", at, iid6, k6, tok="ep0")
        if Shop.UPM.get(u) is not None:
            ug.append(("a stale token clears the guard", name))
        break
    if not done_:
        ug.append(("no case upgraded - the guard is unproven", [c_[0] for c_ in upc]))
    K.check(not ug, "FIX1 UPGUARD the item an Upgrade just made is not upgraded again by a late / second click within 3 s (nothing taken); 3 s later, "
                    "another act or a profile switch = allowed again: %s" % ug[:2])
    # 3. the player left (GearBye -> gear:fn:shop "bye") = LAST / ARM / UPM forgotten; off the world thread is fine for it
    Shop.LAST.put(u, JObject(JLong(1), "java.lang.Long"))
    Shop.ARM.put(u, JString("k|2|1"))
    Shop.UPM.put(u, JString("k|1"))
    rb_ = fn.apply(OA([u, JString("bye"), JString("")]))
    K.check(rb_ is None and Shop.LAST.get(u) is None and Shop.ARM.get(u) is None and Shop.UPM.get(u) is None,
            "FIX3 BYE gear:fn:shop 'bye' (the player left) forgets the per-player maps")
    gb = open(GEN, encoding="utf8", newline="").read()
    gbye = gb[gb.index('gbye = mk("GearBye")'):gb.index("# ================================================================= GearUi")]
    K.check('Object shop = @PKG@.Gear.bridge().get("gear:fn:shop");' in gbye and '.apply(new Object[] { u, "bye", "" });' in gbye,
            "FIX3 BYE GearBye (PlayerDisconnectEvent) calls gear:fn:shop 'bye' through the bridge (GearShopFn is made later)")
    # 2. a failure inside an act never claims "nothing changed" (the Anvil's core may have run); the warn names the op + item
    gs = gb[gb.index('gshop = mk("GearShopFn")'):gb.index('_fns = "\\n".join(')]
    K.check("Something went wrong - nothing changed" not in gs and "-Something went wrong - check your coins and the item before trying again." in gs
            and 'what = " " + (String) a[3] + " on " + (String) a[5] + " at " + (String) a[4];' in gs and '"gear:fn:shop " + op + what + " failed: "' in gs,
            "FIX2 CATCH a failed act says to check coins + item (never 'nothing changed'); the warn line names the op, item id and place")
    # a field with '|' / a line break is cleaned
    K.eq(str(Shop.clean(JString("a|b\nc\rd"))), "a/b c d", "READ clean(): '|' -> '/', line breaks -> spaces")
    K.save()


HK.run_compare = T54["run_compare54"]
HK.run("SkyyGear", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
       [("static", run_static), ("engine", run_engine), ("engine59", T59["run_engine"]), ("engine58", T58["run_engine"]), ("engine57", T57["run_engine"]),
        ("engine56", T56["run_engine"]), ("engine55", T55["run_engine"]), ("engine54", T54["run_engine"]), ("live", T58["run_live"])],
       __file__, live=(T58["LIVE_DIR"], "Skyy_SkyyGear"))
