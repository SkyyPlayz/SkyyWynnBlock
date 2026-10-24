"""Harness for SkyyZones 0.2.2 (round zones022: whole-world regrow by world-name prefix - SkyyShards' shard worlds; tools/zones_0_2_2_patch.py).
Build first:  python tools/zones_0_2_2_patch.py && python SkyyZones/build_skyyzones_0.2.2.py
    python SkyyZones/test_skyyzones_0.2.2.py [--keep]
Phases (fresh child JVMs, tools/harness_kit.py; scratch tools/dev/scratch/zones022/zh):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.2.1 -> 0.2.2: no class added / removed; only the members this round touches differ
  F2  fakes    the 0.2.0 harness's engine stand-ins (Store / ArchetypeChunk / World / PlayerRef subclasses) into scratch/fake2
  X   exec     the REAL ZGuard / ZRegen / ZPass / ZTicker / ZCfg on stand-in worlds with the REAL engine events (BreakBlockEvent ...):
               a copper ore broken by hand in a skyy-shard-* world -> allowed once (vanilla drop), D line FIRST, Rock_Stone placeholder,
               the waiting spot refuses break / dig / place (no 2nd drop: the placeholder can't be mined), a contested 2nd break in the same
               tick refused, back after 4 s (id + rotation), mineable again; a non-ore block (stone, trunk), place + use in the shard
               untouched; an island world (even with a prefix that would match it) + an unlisted world untouched; the prefix row off;
               regen off; builder mode; a mob break; a region in a shard world decides first; a region edit elsewhere does NOT force a
               shard entry back (the re-index fix); a restart mid-timer keeps it waiting with its stone placeholder; an old regen.properties
               (no new lines) reads the defaults and is not rewritten; the 3 kit check hooks; /zones status line
  D   live     start twice on a scratch COPY of the live mods folder (the plugin's file start + the kit): only kit / SkyyZones files
  AA  audit    engine-access audit
"""
import os, sys, hashlib, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import skyybuild as B

VERSION, OLD = "0.2.2", "0.2.1"
PKG = "com.skyy.zones."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyZones-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyZones-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "zones022", "zh")))
LIVE = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods")
EXPECT = {"ZCfg": ["~m loadRegen", "+m joinList", "+m prefixes", "+m ptypes", "+m prefixWorld", "+m prefixListed", "+m prefixType", "+m prefixPh",
                   "+m checkPrefix", "+m checkPTypes", "+m checkPPh", "+f PREFIX", "+f PTYPES", "+f PPH", "+f PXSRC", "+f PXARR", "+f PTSRC",
                   "+f PTARR", "+f PXBROKE", "~<clinit>"],
          "ZRules": ["+m regrowType"], "ZRw": ["~m snapshot"], "ZPass": ["~m pass"], "ZRegen": ["~m broke", "+m broke", "~m status"], "ZGuard": ["~m regrow", "~m handle"],
          "SkyyZonesPlugin": ["~m setup"], "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header", "~<clinit>"], "ZStore": ["~m parseAll"], "ZFn": ["~m publish", "~m unpublish"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
SHARD = "skyy-shard-d8ddde89-98b2-4739-983e-a39773d582b6-p3"     # Skyy's real shard world name (50 characters)
ISLAND = "skyy-island-d8ddde89-98b2-4739-983e-a39773d582b6-p3"
PLAIN = "skywynn_server"


def t20():
    spec = importlib.util.spec_from_file_location("zones_t20", os.path.join(HERE, "test_skyyzones_0.2.0.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_fakes(out, jar, scratch, _home):
    T = t20()
    os.makedirs(os.path.join(scratch, "fake2"), exist_ok=True)
    T.run_mkfake(os.path.join(scratch, "fake2"))
    K = HK.Child(out)
    K.check(os.path.isdir(os.path.join(scratch, "fake2")), "F2: the stand-ins are written")
    K.save()


def run_exec(out, jar, scratch, _home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, os.path.join(scratch, "fake2")], verify=True)
    T = t20()
    T.SCRATCH = scratch
    E = T.engine(K)
    try:
        xrun(K, E, T, scratch)
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:500])
    K.save()


def xrun(K, E, T, scratch):
    from jpype import JClass, JArray, JString, JInt, JLong, JFloat, JImplements, JOverride
    U, jfield, BT = E["U"], E["jfield"], E["BT"]
    FAKE = T.FAKE
    P = lambda n: JClass(PKG + n)
    Cfg, Sto, Eng, Msg, Bld, Plug, Rgn, Pass, Tkr, Dep, Cmds = (P(n) for n in (
        "ZCfg", "ZStore", "ZEng", "ZMsg", "ZBuild", "SkyyZonesPlugin", "ZRegen", "ZPass", "ZTicker", "ZDep", "ZCmds"))
    AL, HM, IHM, UUID, Paths, Bool = (JClass("java.util.ArrayList"), JClass("java.util.HashMap"), JClass("java.util.IdentityHashMap"),
                                      JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Boolean"))
    MS, MB, MCH, FW, FP = (JClass(FAKE + "." + n) for n in ("MapStore", "MapBuffer", "MapChunk", "FakeWorld", "FakePr"))
    WLD = JClass("com.hypixel.hytale.server.core.universe.world.World")
    EST = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    TC = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    V3D, V3I = JClass("org.joml.Vector3d"), JClass("org.joml.Vector3i")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    REF = JClass("com.hypixel.hytale.component.Ref")
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    ICTX = JClass("com.hypixel.hytale.server.core.entity.InteractionContext")
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    PLBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.PlaceBlockEvent")
    UBP = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre")
    btm = BT.getAssetMap()

    def bt(n):
        return btm.getAsset(JInt(int(btm.getIndex(n))))
    lines = AL()
    Cfg.LINES = lines

    def logged():
        r = [str(x) for x in lines]
        lines.clear()
        return r

    @JImplements(PKG + "ZApi")
    class Api(object):
        def __init__(self):
            self.notes, self.wb, self.state, self.occ, self.writes, self.loads, self.tasks, self.worlds, self.lat = [], {}, {}, set(), [], [], [], {}, []

        @JOverride
        def notify(self, pr, text):
            self.notes.append((str(pr.getUsername()), str(text)))

        @JOverride
        def title(self, pr, t, sub):
            pass

        @JOverride
        def particle(self, id_, x, y, z, to, st):
            pass

        @JOverride
        def target(self, r, st):
            return None

        @JOverride
        def selection(self, r, st, pr):
            return None

        @JOverride
        def give(self, r, st, id_):
            return 0

        @JOverride
        def blockAt(self, w, x, y, z):
            return self.wb.get((str(w.getName()), int(x), int(y), int(z)), "Rock_Stone")

        @JOverride
        def stateAt(self, w, x, y, z):
            return JArray(JInt)(self.state.get((str(w.getName()), int(x), int(y), int(z)), [0, 0]))

        @JOverride
        def put(self, w, x, y, z, id_, rot):
            k = (str(w.getName()), int(x), int(y), int(z))
            self.writes.append(k + (str(id_), int(rot)))
            self.wb[k] = str(id_)
            return True

        @JOverride
        def occupied(self, w, x, y, z):
            return (str(w.getName()), int(x), int(y), int(z)) in self.occ

        @JOverride
        def load(self, w, x, y, z, after):
            self.loads.append(after)

        @JOverride
        def world(self, name):
            return self.worlds.get(str(name))

        @JOverride
        def exec(self, w, r):
            self.tasks.append(r)
            return True

        @JOverride
        def later(self, r, ms):
            self.lat.append(r)

        @JOverride
        def scan(self, w, box, ids, stats):
            return AL()
    api = Api()
    Eng.API = api
    perms = {}

    @JImplements("java.util.function.Function")
    class PermFn(object):
        @JOverride
        def apply(self, o):
            return Bool.valueOf(bool(perms.get((str(o[0]), str(o[1])), False)))
    Cfg.PERM_TEST = PermFn()

    # ---------------------------------------------------------------- C: config + files
    home = os.path.join(scratch, "x", "Skyy_SkyyZones")
    os.makedirs(os.path.dirname(home), exist_ok=True)
    r = str(Plug.paths(Paths.get(home)))
    rtxt = open(os.path.join(home, "regen.properties"), encoding="utf8").read()
    K.check("regen.worldPrefix=skyy-shard-\n" in rtxt and "regen.prefixTypes=copper,iron,gold,silver,thorium,cobalt,adamantite,mithril,onyxium,gem\n" in rtxt
            and "regen.prefixPlaceholder=Rock_Stone\n" in rtxt and rtxt == str(Cfg.REGEN_TEXT), "C: a new regen.properties has the 3 prefix lines (%s)" % r[:120])
    K.check((str(Cfg.PREFIX), str(Cfg.PTYPES), str(Cfg.PPH)) == ("skyy-shard-", "copper,iron,gold,silver,thorium,cobalt,adamantite,mithril,onyxium,gem", "Rock_Stone"),
            "C: the defaults are read")
    # Skyy's file = written by 0.2.0 / 0.2.1 (no prefix lines): the defaults apply, the file is NOT rewritten
    old = "".join(l + "\n" for l in rtxt.split("\n") if l and not l.startswith("regen.worldPrefix") and not l.startswith("regen.prefix")
                  and "regen.worldPrefix" not in l and "Island worlds (" not in l and "a broken block of those types" not in l)
    rf = os.path.join(home, "regen.properties")
    open(rf, "wb").write(old.replace("\n", "\r\n").encode("utf8"))
    b0 = open(rf, "rb").read()
    Cfg.PREFIX, Cfg.PTYPES, Cfg.PPH = "x", "y", "z"
    Cfg.loadRegen(False)
    K.check(open(rf, "rb").read() == b0 and str(Cfg.PREFIX) == "skyy-shard-" and str(Cfg.PTYPES).startswith("copper,") and str(Cfg.PPH) == "Rock_Stone",
            "C: an old regen.properties (no prefix lines, CRLF) reads the defaults and stays byte-identical")
    open(rf, "a", encoding="utf8").write("regen.worldPrefix=\n")
    Cfg.loadRegen(False)
    K.check(str(Cfg.PREFIX) == "" and len(Cfg.prefixes()) == 0 and not bool(Cfg.prefixWorld(SHARD)), "C: regen.worldPrefix= (empty) = off")
    open(rf, "wb").write(b0)
    Cfg.loadRegen(False)
    # prefixWorld
    K.check(bool(Cfg.prefixWorld(SHARD)) and bool(Cfg.prefixWorld(SHARD.upper())) and not bool(Cfg.prefixWorld(ISLAND)) and not bool(Cfg.prefixWorld(PLAIN))
            and not bool(Cfg.prefixWorld("skyy-shard")) and not bool(Cfg.prefixWorld(None)), "C: prefixWorld - shard yes (any case), island / plain / None no")
    Cfg.PREFIX = "skyy-"
    K.check(bool(Cfg.prefixWorld(SHARD)) and not bool(Cfg.prefixWorld(ISLAND)), "C: even a hand-edited prefix 'skyy-' never matches an island world")
    Cfg.PREFIX = "skyy-shard-"
    K.check(str(Cfg.prefixType(SHARD, "Ore_Copper_Stone")) == "copper" and str(Cfg.prefixType(SHARD, "*Ore_Iron_Shale")) == "iron"
            and Cfg.prefixType(SHARD, "Rock_Stone") is None and Cfg.prefixType(SHARD, "Wood_Oak_Trunk") is None and Cfg.prefixType(ISLAND, "Ore_Copper_Stone") is None,
            "C: prefixType - ores yes; stone, trunks, island worlds no")
    # kit check hooks
    ck = lambda f, v: (None if f(JString("k"), v) is None else str(f(JString("k"), v)))
    K.check(ck(Cfg.checkPrefix, "skyy-shard-") is None and ck(Cfg.checkPrefix, "") is None and ck(Cfg.checkPrefix, "skyy-shard-, mine_") is None
            and "island" in ck(Cfg.checkPrefix, "skyy-island-") and "island" in ck(Cfg.checkPrefix, "skyy-") and "island" in ck(Cfg.checkPrefix, "skyy-island-abc")
            and ck(Cfg.checkPrefix, "abc") is not None and ck(Cfg.checkPrefix, "a b c d e f g h i") is not None and ck(Cfg.checkPrefix, "bad/name") is not None,
            "C: checkPrefix - refuses island-matching starts, too short / bad names, more than 8")
    K.check(ck(Cfg.checkPTypes, "copper,iron") is None and ck(Cfg.checkPTypes, "") is None and "later" in ck(Cfg.checkPTypes, "copper,logs")
            and "later" in ck(Cfg.checkPTypes, "crops") and "No resource type" in ck(Cfg.checkPTypes, "copper,nope") and "placeholder" in ck(Cfg.checkPTypes, "stone"),
            "C: checkPTypes - logs / crops / unknown / a type listing the placeholder refused")
    K.check(ck(Cfg.checkPPh, "Rock_Stone") is None and ck(Cfg.checkPPh, "none") is None and "copper" in ck(Cfg.checkPPh, "Ore_Copper_Stone")
            and ck(Cfg.checkPPh, "No_Such_Block_X") is not None and ck(Cfg.checkPPh, "a b") is not None, "C: checkPPh - a prefix-type block / unknown / bad id refused")
    logged()

    # ---------------------------------------------------------------- worlds / players / events
    def mkworld(name):
        w = U.allocateInstance(FW.class_)
        jfield(WLD, "name").set(w, name)
        es = U.allocateInstance(EST.class_)
        jfield(EST, "world").set(es, w)
        st = U.allocateInstance(MS.class_)
        st.comps = IHM()
        st.ext = es
        return w, st
    wS, stS = mkworld(SHARD)
    wI, stI = mkworld(ISLAND)
    wP, stP = mkworld(PLAIN)
    api.worlds = {SHARD: wS, ISLAND: wI, PLAIN: wP}
    cb = U.allocateInstance(MB.class_)
    nref = [0]

    def mkref(st):
        nref[0] += 1
        r_ = REF(st, JInt(nref[0]))
        st.comps.put(r_, IHM())
        return r_

    def mkplayer(st, name, n, builder=False):
        r_ = mkref(st)
        pr_ = U.allocateInstance(FP.class_)
        jfield(PRc, "uuid").set(pr_, UUID.fromString("00000000-0000-4000-8000-%012x" % (0xc000 + n)))
        jfield(PRc, "username").set(pr_, name)
        pr_.msgs = AL()
        st.comps.get(r_).put(PRc.getComponentType(), pr_)
        st.comps.get(r_).put(TC.getComponentType(), TC(V3D(0.5, 101.0, 0.5), R3(0.0, 0.0, 0.0)))
        perms[(str(pr_.getUuid()), "skyyzones.build")] = builder
        ch = U.allocateInstance(MCH.class_)
        ch.ref = r_
        return {"ch": ch, "st": st, "pr": pr_, "u": pr_.getUuid(), "ref": r_}
    Skyy = mkplayer(stS, "Skyy", 1)
    Coop = mkplayer(stS, "Coop", 2)
    Bd = mkplayer(stS, "Builder", 3, builder=True)
    IslP = mkplayer(stI, "Skyy", 4)
    PlP = mkplayer(stP, "Skyy", 5)
    mob = U.allocateInstance(MCH.class_)
    mob.ref = mkref(stS)
    gB, gD, gP, gU = (P(n)() for n in ("ZGuardBreak", "ZGuardDamage", "ZGuardPlace", "ZGuardUse"))

    def item(i):
        if i is None:
            return None
        try:
            return IS(i, 1)
        except Exception:
            s_ = U.allocateInstance(IS.class_)
            for fn_, v_ in (("itemId", i), ("quantity", JInt(1))):
                f_ = IS.class_.getDeclaredField(fn_)
                f_.setAccessible(True)
                f_.set(s_, v_)
            return s_

    def fire(p, kind, x, y, z, block="Ore_Copper_Stone", st=None):
        ch_, st_ = (p["ch"], p["st"]) if isinstance(p, dict) else (p, st)
        if kind == "break":
            g_, e_ = gB, BBE(item("Tool_Pickaxe_Iron"), V3I(x, y, z), bt(block))
        elif kind == "dig":
            g_, e_ = gD, DBE(item("Tool_Pickaxe_Iron"), V3I(x, y, z), bt(block), JFloat(1.0), JFloat(0.5))
        elif kind == "place":
            g_, e_ = gP, PLBE(item("Rock_Stone"), V3I(x, y, z), None)
        else:
            g_, e_ = gU, UBP(ITY.Use, U.allocateInstance(ICTX.class_), V3I(x, y, z), bt(block))
        Msg.LAST.clear()
        g_.handle(0, ch_, st_, cb, e_)
        return bool(e_.isCancelled())

    def mine(p, wn, x, y, z, block="Ore_Copper_Stone", st=None):
        api.wb[(wn, x, y, z)] = block
        c_ = fire(p, "break", x, y, z, block=block, st=st)
        if not c_:
            api.wb[(wn, x, y, z)] = "Empty"   # the engine removes it after the uncancelled event
        return c_

    def drain():
        n = 0
        while api.tasks:
            api.tasks.pop(0).run()
            n += 1
        return n

    def tick(at):
        Dep.CLOCK = JLong(at)
        P("ZTicker")().run()
        return drain()

    def waiting(wn, x, y, z):
        return bool(Rgn.depleted(wn, x, y, z))
    rdir = os.path.join(home, "regen")

    def jl(wn):
        f = os.path.join(rdir, wn + ".journal")
        return open(f, encoding="utf8").read().splitlines() if os.path.isfile(f) else []

    def notes():
        r_ = list(api.notes)
        del api.notes[:]
        return r_
    Cfg.REGEN_ON = True
    Cfg.JITTER = 0.0
    Cfg.SPEED = 1.0
    T0 = 1800000000000
    Dep.CLOCK = JLong(T0)
    K.check(Sto.INDEX is not None and not bool(Sto.INDEX.has(SHARD)) and not bool(Cfg.protectedWorld(SHARD)), "X: the shard world has no region and is not a protected world")

    # ---- THE BREAK: an ore by hand in the shard -> allowed once, D line first, Rock_Stone placeholder
    api.state[(SHARD, 5, 101, 5)] = [3, 0]
    b0_ = int(Rgn.BROKE.get())
    c_ = mine(Skyy, SHARD, 5, 101, 5)
    j_ = jl(SHARD)
    K.check(not c_ and waiting(SHARD, 5, 101, 5) and j_ == ["D 5 101 5 Ore_Copper_Stone copper %d 3 Rock_Stone" % (T0 + 4000)] and len(api.tasks) == 1
            and int(Rgn.BROKE.get()) == b0_ + 1 and int(Cfg.PXBROKE.get()) == 1 and not notes(),
            "X: a copper ore broken by hand in %s is ALLOWED (one vanilla drop / XP / collection), its D line (copper, +4 s, rotation 3, placeholder Rock_Stone) journaled first: %s" % (SHARD[:20], j_))
    K.check(drain() == 1 and api.wb[(SHARD, 5, 101, 5)] == "Rock_Stone" and api.writes[-1] == (SHARD, 5, 101, 5, "Rock_Stone", 0),
            "X: the pass turns the spot into STONE (Rock_Stone) - Skyy: 'it turns to stone'")
    # ---- dupes: the placeholder / the spot while it regrows
    nj_ = len(jl(SHARD))
    K.check(fire(Skyy, "break", 5, 101, 5, block="Rock_Stone") and fire(Coop, "break", 5, 101, 5, block="Rock_Stone") and fire(Coop, "dig", 5, 101, 5, block="Rock_Stone")
            and fire(Skyy, "place", 5, 101, 5) and len(jl(SHARD)) == nj_ and notes()[0] == ("Skyy", "Growing back - wait a moment."),
            "X: DUPE - the stone placeholder cannot be broken / dug / built on by the owner or co-op while it regrows (cancelled = no drop), nothing journaled")
    K.check(fire(mob, "break", 5, 101, 5, block="Rock_Stone", st=stS), "X: ... nor by a mob")
    api.wb[(SHARD, 6, 101, 5)] = "Ore_Copper_Stone"
    c1_ = fire(Skyy, "break", 6, 101, 5)
    c2_ = fire(Coop, "break", 6, 101, 5)
    api.wb[(SHARD, 6, 101, 5)] = "Empty"
    K.check(not c1_ and c2_ and sum(1 for l in jl(SHARD) if l.startswith("D 6 101 5 ")) == 1, "X: DUPE - two players break one ore in one tick: the 2nd is refused (one drop roll)")
    drain()
    notes()
    # ---- a region edit in another world must NOT force a shard entry back (the re-index check asks regrowType)
    Sto.create("townx", PLAIN, "full", JArray(JInt)([100, 60, 100, 110, 80, 110]), "Skyy")
    tick(T0 + 1000)
    K.check(waiting(SHARD, 5, 101, 5) and not bool(Rgn.at(SHARD, 5, 101, 5).force) and api.wb[(SHARD, 5, 101, 5)] == "Rock_Stone",
            "X: a region edit (new index) leaves the waiting shard ore waiting (not forced back early)")
    tick(T0 + 3999)
    K.check(waiting(SHARD, 5, 101, 5) and api.wb[(SHARD, 5, 101, 5)] == "Rock_Stone", "X: before 4 s nothing comes back")
    tick(T0 + 4000)
    K.check(not waiting(SHARD, 5, 101, 5) and api.wb[(SHARD, 5, 101, 5)] == "Ore_Copper_Stone" and (SHARD, 5, 101, 5, "Ore_Copper_Stone", 3) in api.writes
            and not waiting(SHARD, 6, 101, 5) and api.wb[(SHARD, 6, 101, 5)] == "Ore_Copper_Stone", "X: after copper's 4 s the ORE grows back (id + rotation 3)")
    K.check(not fire(Skyy, "dig", 5, 101, 5) and not mine(Skyy, SHARD, 5, 101, 5) and waiting(SHARD, 5, 101, 5), "X: ... and can be mined again (a new regrow)")
    drain()
    # ---- everything else in the shard: untouched by SkyyZones
    nw_ = len(api.writes)
    K.check(not mine(Skyy, SHARD, 9, 100, 9, block="Rock_Stone") and not waiting(SHARD, 9, 100, 9) and not mine(Skyy, SHARD, 9, 102, 9, block="Wood_Oak_Trunk")
            and not waiting(SHARD, 9, 102, 9) and not mine(Skyy, SHARD, 9, 103, 9, block="Plant_Crop_Carrot_Block") and not waiting(SHARD, 9, 103, 9),
            "X: a NON-ore block (stone floor, trunk, crop) in the shard - not cancelled by us, no regrow (SkyyShards / SkyyIslands decide as today)")
    K.check(not fire(Skyy, "place", 9, 104, 9) and not fire(Skyy, "use", 9, 100, 9, block="Bench_Workbench") and not fire(Skyy, "dig", 9, 105, 9, block="Ore_Iron_Stone")
            and drain() == 0 and len(api.writes) == nw_ and not notes(), "X: place / use / dig in the shard - untouched, no block write")
    # ---- island + a plain world: unaffected
    K.check(not mine(IslP, ISLAND, 5, 101, 5) and not waiting(ISLAND, 5, 101, 5) and not jl(ISLAND) and not mine(PlP, PLAIN, 5, 101, 5)
            and not waiting(PLAIN, 5, 101, 5) and not jl(PLAIN) and drain() == 0, "X: an ore broken on the player's ISLAND world / an unlisted world - vanilla, no regrow, no regen file")
    Cfg.PREFIX = "skyy-"
    K.check(not mine(IslP, ISLAND, 6, 101, 5) and not waiting(ISLAND, 6, 101, 5), "X: ... even with a hand-set prefix 'skyy-' the island is never a regrow area")
    Cfg.PREFIX = "skyy-shard-"
    # ---- the prefix row off / regen off / zones off / builder mode
    Cfg.PREFIX = ""
    K.check(not mine(Skyy, SHARD, 7, 101, 5) and not waiting(SHARD, 7, 101, 5), "X: regen.worldPrefix empty (off) - a shard ore breaks like vanilla")
    Cfg.PREFIX = "skyy-shard-"
    Cfg.PTYPES = "iron"
    K.check(not mine(Skyy, SHARD, 7, 101, 6) and not waiting(SHARD, 7, 101, 6) and not mine(Skyy, SHARD, 7, 101, 7, block="Ore_Iron_Stone") and waiting(SHARD, 7, 101, 7),
            "X: regen.prefixTypes iron only - copper breaks like vanilla, iron regrows")
    Cfg.PTYPES = "copper,iron,gold,silver,thorium,cobalt,adamantite,mithril,onyxium,gem"
    drain()
    Cfg.REGEN_ON = False
    K.check(not mine(Skyy, SHARD, 8, 101, 5) and not waiting(SHARD, 8, 101, 5), "X: regen.enabled off - vanilla")
    Cfg.REGEN_ON = True
    Cfg.ON = False
    K.check(not mine(Skyy, SHARD, 8, 101, 6) and not waiting(SHARD, 8, 101, 6), "X: zones.on off - vanilla")
    Cfg.ON = True
    Bld.set(Bd["u"], "Builder", True)
    K.check(not mine(Bd, SHARD, 8, 101, 7) and not waiting(SHARD, 8, 101, 7), "X: builder mode - breaks start no regrow")
    Bld.set(Bd["u"], "Builder", False)
    api.wb[(SHARD, 8, 101, 8)] = "Ore_Copper_Stone"
    K.check(not fire(mob, "break", 8, 101, 8, st=stS) and waiting(SHARD, 8, 101, 8), "X: a mob break of a shard ore regrows too (as in regions)")
    api.wb[(SHARD, 8, 101, 8)] = "Empty"
    drain()
    # ---- a placeholder that is a prefix-type block -> the type's own (Rock_Bedrock)
    Cfg.PPH = "Ore_Iron_Stone"
    mine(Skyy, SHARD, 10, 101, 5)
    drain()
    K.check(api.wb[(SHARD, 10, 101, 5)] == "Rock_Bedrock" and any("regen.prefixPlaceholder Ore_Iron_Stone" in l for l in logged()),
            "X: a hand-edited placeholder that is itself an ore -> Rock_Bedrock (the type's own; warned once)")
    Cfg.PPH = "Rock_Stone"
    # ---- a region inside a shard world decides first
    Sto.create("shardfull", SHARD, "full", JArray(JInt)([20, 90, 20, 30, 110, 30]), "Skyy")
    api.wb[(SHARD, 25, 101, 25)] = "Ore_Copper_Stone"
    K.check(fire(Skyy, "break", 25, 101, 25) and not waiting(SHARD, 25, 101, 25), "X: a FULL region in a shard world still refuses the ore (regions decide first)")
    Sto.create("shardsky", SHARD, "skyblock", JArray(JInt)([40, 90, 40, 50, 110, 50]), "Skyy")
    Sto.set("shardsky", "types", "copper", "Skyy")
    c_ = mine(Skyy, SHARD, 45, 101, 45)
    drain()
    K.check(not c_ and waiting(SHARD, 45, 101, 45) and api.wb[(SHARD, 45, 101, 45)] == "Rock_Bedrock", "X: a SKYBLOCK region there uses its own placeholder (Rock_Bedrock)")
    c_ = mine(Skyy, SHARD, 60, 101, 60)
    drain()
    K.check(not c_ and waiting(SHARD, 60, 101, 60) and api.wb[(SHARD, 60, 101, 60)] == "Rock_Stone", "X: ... outside the regions the prefix rule (stone) still applies")
    tick(T0 + 4100)
    K.check(not bool(Rgn.at(SHARD, 60, 101, 60).force), "X: ... and the region edits did not force the prefix entry back")
    # ---- restart mid-timer
    before_ = sorted((int(d.x), int(d.y), int(d.z), str(d.ph), str(d.type), int(d.due)) for d in Rgn.rw(SHARD, False).dep.values())
    Rgn.shutdown()
    r_ = str(Rgn.start(Paths.get(rdir)))
    after_ = sorted((int(d.x), int(d.y), int(d.z), str(d.ph), str(d.type), int(d.due)) for d in Rgn.rw(SHARD, False).dep.values())
    K.check(before_ == after_ and any(e[:5] == (60, 101, 60, "Rock_Stone", "copper") for e in after_),
            "X: RESTART mid-timer - the shard's waiting ores come back from regen/ with their stone placeholder + times (%s): %s | %s" % (r_[:100], before_, after_))
    K.check(fire(Coop, "break", 60, 101, 60, block="Rock_Stone"), "X: ... still protected after the restart")
    tick(T0 + 60000)
    K.check(not waiting(SHARD, 60, 101, 60) and api.wb[(SHARD, 60, 101, 60)] == "Ore_Copper_Stone", "X: ... and grows back")
    # ---- /zones status
    st_ = [str(s) for s in Rgn.status()]
    K.check(any(s.startswith("Whole-world regrow in worlds starting skyy-shard-: copper, iron") and "placeholder Rock_Stone" in s for s in st_), "X: /zones status names the rule: %s" % [s for s in st_ if "Whole" in s])
    Cfg.PREFIX = ""
    K.check(any(s == "Whole-world regrow (regen.worldPrefix): off" for s in (str(x) for x in Rgn.status())), "X: ... and says off")
    Cfg.PREFIX = "skyy-shard-"
    Rgn.shutdown()
    Eng.API = None


def snap(d):
    out = {}
    for base, _dirs, fs in os.walk(d):
        for f in fs:
            p_ = os.path.join(base, f)
            out[os.path.relpath(p_, d).replace(os.sep, "/")] = hashlib.sha1(open(p_, "rb").read()).hexdigest()
    return out


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Plug, CPub, Sto = (JClass(PKG + n) for n in ("SkyyZonesPlugin", "CfgPub", "ZStore"))
    Paths = JClass("java.nio.file.Paths")
    Sto.SYNC = True
    before = snap(home)

    def start():
        r = str(Plug.paths(Paths.get(os.path.join(home, "Skyy_SkyyZones"))))
        CPub.start(Paths.get(home), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyZones"))
        CPub.flush()
        CPub.shutdown()
        return r
    r1 = start()
    s1 = snap(home)
    r2 = start()
    s2 = snap(home)
    ch = sorted(f for f in before if s1.get(f) != before[f] and not f.startswith("Skyy_SkyyZones/"))
    K.check(not ch, "D start 1: every file outside Skyy_SkyyZones byte-identical (%s)" % ch[:5])
    K.check(s1 == s2, "D start 2 changes nothing (%s)" % sorted(f for f in set(s1) | set(s2) if s1.get(f) != s2.get(f)))
    rp = [f for f in before if f.endswith("Skyy_SkyyZones/regen.properties")]
    K.check(all(s1.get(f) == before[f] for f in rp), "D Skyy's existing regen.properties is not rewritten (%d found)" % len(rp))
    K.notes.append("D: %s | %s" % (r1[:200], r2[:200]))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyZones", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [], [("fakes", run_fakes), ("exec", run_exec), ("live", run_live)], __file__,
           live=(LIVE, "mods"))
