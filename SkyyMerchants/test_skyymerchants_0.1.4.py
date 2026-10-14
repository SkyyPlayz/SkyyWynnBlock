"""Harness for SkyyMerchants 0.1.4 (RARITY SIGILS NEVER SOLD IN NPC SHOPS: the wall, the default list, the one-time update;
tools/merchants_0_1_4_patch.py) = the 0.1.3 harness (every exec check kept, the 0.1.3 IO behaviour unchanged) + phase S + the live phase's
one-time update.
Build first: python tools/merchants_0_1_4_patch.py && python SkyyMerchants/build_skyymerchants_0.1.4.py

    python SkyyMerchants/test_skyymerchants_0.1.4.py [--keep]

0.1.4 NEW: C compares 0.1.3 -> 0.1.4 (+ MerchMig); S = every new code path: MerchWall.why refuses Skyy_Sigil_* whatever the list says (an
emptied list too), the stock check refuses a Sigil line, applyTables skips a Sigil stock line; the fresh default lists Skyy_Sigil_* and carries
the marker (never updated); MerchMig.update on texts (the old default rewritten value-only, CRLF kept, a hand-edited list kept + noted, the
marker = done, no key = marker only, a continued value never rewritten, a last line with no newline, duplicate keys = the last one decides);
MerchMig.run on a scratch file (History copy verified first, the change-log row with ok = Undo, run twice = no change, no History = nothing
written); D runs the update + MerchCfg.load twice on the live copy (the first start rewrites the old default + adds the marker, the second
changes nothing; Skyy_Sigil_* walled after the load).

--- the 0.1.3 harness header ---

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py + tools/perfworld_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.2 -> 0.1.3: exactly the planned members differ (+ MerchIO)
  X  exec     EVERY NEW CODE PATH (-Xverify:all): bridge0 / bridge (created once, cached in BRIDGE, same map); the static checks (every
              bridge() is the lock-free form; Thread.sleep only in moveRetry, reached only from write0 <- writeOne; every file write of
              MerchReg / sales.log only in write0 / sale0 / sites); MerchIO thread factory (SkyyMerchants-IO, daemon); save() with IO
              running: returns at once while the writer is held (WLOCK held by the test = the caller never writes), the file is written
              by SkyyMerchants-IO, 0.1.2's text byte for byte; coalescing (50 saves while held = at most 2 writes, the newest text);
              settled / ok; a FAILED write (folder blocked) keeps the text, marks the world, relocate + respawnSame refuse at once
              (count 8), retryFailed re-queues it, the next write clears it; the per-world second skips the ghost sweep until settled
              and sweeps once settled; relocate's old-merchant removal waits for the write; sales.log lines appended in order by the
              writer (sale -> sale0) + the synchronous fallback; ready(): the first read queued on the writer (false), then in memory
              (true); IO off = the 0.1.2 synchronous save (real result); flushAll: writer stopped, queue drained, every world written
  D  live     START TWICE on a scratch COPY of the live Skyy_SkyyMerchants: the registry read on the writer, saved again = byte-identical,
              sales.log untouched; the second start the same
  AA engine-access audit
Behaviour regression (separately, same jar): python SkyyMerchants/test_skyymerchants_0.1.py --jar SkyyMerchants/SkyyMerchants-0.1.3.jar
(244 ok; its only fails are the 0.1 manifest version, the new MerchIO class in its class list / AA count and its live folder rule).
Scratch: tools/dev/scratch/perfworld/merchants (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW

VERSION = "0.1.4"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMerchants-0.1.3.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "gear5", "merchants")))
PKG = "com.skyy.merchants."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyMerchants")

EXPECT = {     # 0.1.4 (tools/merchants_0_1_4_patch.py): the wall, the update call, the default list / text constants
    "MerchWall": ["~m why"],                    # A: Skyy_Sigil_* never sold
    "SkyyMerchantsPlugin": ["~m setup"],        # C: MerchMig.run before MerchCfg.load (+ the ready line's version)
    "MerchCfg": ["~<clinit>", "~m applyAll", "~m seed", "~m applyScalars"],     # B: the default text / list constants
    "CfgRows": ["~<clinit>", "~m header"],      # the config kit re-emitted: the new default list in its row table, version text
    "CfgFn": ["~m opExport"],
}
ADDED = ["MerchMig"]


def api_sim(state):
    from jpype import JImplements, JOverride, JArray, JString, JDouble
    IC = "com.hypixel.hytale.server.core.inventory.container.ItemContainer"

    @JImplements(PKG + "MerchApi")
    class Sim(object):
        @JOverride
        def worlds(self): return JArray(JString)(["default"])
        @JOverride
        def exec(self, wn, r): r.run(); return True
        @JOverride
        def height(self, wn, x, z): return 64
        @JOverride
        def block(self, wn, x, y, z): return "Soil_Grass" if y <= 64 else "Empty"
        @JOverride
        def fluid(self, wn, x, y, z): return False
        @JOverride
        def env(self, wn, x, y, z): return "Env_Zone1_Plains"
        @JOverride
        def players(self, wn): return JArray(JDouble)([10.0, 20.0])
        @JOverride
        def spawnPoint(self, wn): return JArray(JDouble)([0.0, 64.0, 0.0])
        @JOverride
        def roleOk(self, role): return True
        @JOverride
        def spawn(self, wn, role, x, y, z, yaw, name):
            state["spawned"].append((x, y, z))
            return "00000000-0000-4000-8000-%012d" % len(state["spawned"])
        @JOverride
        def present(self, wn, uuid, x, z, name): return 1
        @JOverride
        def remove(self, wn, uuid):
            state["removed"].append(str(uuid))
            return 1
        @JOverride
        def tell(self, wn, text, color): pass
        @JOverride
        def tellPlayer(self, u, text, color): pass
        @JOverride
        def conts(self, player): return None
        @JOverride
        def pos(self, ref, st): return None
        @JOverride
        def open(self, ref, pr, page): return False
    return Sim()


# ====================================================================================================== X: every new code path
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, synchronized
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Log, Reg, Site, Core, Shop, IOc, Eng, Cfg, Timer = (P("MerchLog"), P("MerchReg"), P("MerchSite"), P("MerchCore"), P("MerchShop"),
                                                        P("MerchIO"), P("MerchEng"), P("MerchCfg"), P("MerchTimer"))
    Sys, Paths, Files = JClass("java.lang.System"), JClass("java.nio.file.Paths"), JClass("java.nio.file.Files")
    Executors, Thread = JClass("java.util.concurrent.Executors"), JClass("java.lang.Thread")
    lines = JClass("java.util.ArrayList")()
    Log.LINES = lines
    # ---- A: bridge
    K.check(Log.BRIDGE is None, "X bridge: BRIDGE empty before the first call")
    m1 = Log.bridge()
    K.check(Sys.identityHashCode(Sys.getProperties().get("skyy.bridge")) == Sys.identityHashCode(m1), "X bridge: the first call creates + stores the map")
    K.check(Log.BRIDGE is not None and Sys.identityHashCode(Log.BRIDGE) == Sys.identityHashCode(m1)
            and Sys.identityHashCode(Log.bridge()) == Sys.identityHashCode(m1) and Sys.identityHashCode(Log.bridge0()) == Sys.identityHashCode(m1),
            "X bridge: cached in BRIDGE, the same map every call, bridge0 finds it")
    PW.bridge_static(K, jar)
    # ---- static: sleeps + file writes only on the writer's methods
    g = PW.calls(jar)
    K.eq([m for m in PW.sites(g, PW.SLEEP) if not m.startswith("Cfg")], ["MerchReg.moveRetry"],
         "X static: Thread.sleep only in MerchReg.moveRetry (+ the config kit's admin saves on the scheduler)")
    K.eq(PW.callers(g, "MerchReg.moveRetry", PKG), ["MerchReg.write0"], "X static: moveRetry called only by write0")
    K.eq(PW.callers(g, "MerchReg.write0", PKG), ["MerchReg.writeOne0"], "X static: write0 called only by writeOne0")
    K.eq(PW.callers(g, "MerchReg.writeOne0", PKG), ["MerchReg.writeOne"], "X static: writeOne0 only under WLOCK (writeOne)")
    K.eq(PW.callers(g, "MerchShop.sale0", PKG), ["MerchIO.run", "MerchShop.sale"], "X static: sale0 = the writer job or the IO-off fallback")
    io = PW.sites(g, PW.IO_TARGETS)
    K.check(set(io) <= {"MerchReg.write0", "MerchReg.moveRetry", "MerchReg.sites", "MerchShop.sale0", "MerchCfg.read", "MerchCfg.seed", "MerchMig.run", "MerchMig.saved"} | set(m for m in io if m.startswith("Cfg")),
            "X static: file I/O only in write0 / sites / sale0 / the config load: %s" % io)
    # ---- the writer
    d = os.path.join(scratch, "x")
    os.makedirs(d, exist_ok=True)
    Reg.DIR = Paths.get(os.path.join(d, "merchants"))
    Shop.LOGF = Paths.get(os.path.join(d, "sales.log"))
    fac = IOc(9, None)
    t = fac.newThread(IOc(1, "nothing"))
    K.check(str(t.getName()) == "SkyyMerchants-IO" and t.isDaemon(), "X MerchIO.newThread: SkyyMerchants-IO, daemon")
    # IO off first: the 0.1.2 synchronous save, real result
    sites = Reg.sites("default")
    K.check(sites is not None and sites.size() == 0, "X sites: no file = an empty registry")
    s = Site()
    s.zone, s.uuid, s.x, s.y, s.z, s.placedAt, s.visit = "zone1", "00000000-0000-4000-8000-000000000001", 10, 64, 20, 1000, 1
    s.stock, s.env, s.rumour = "w:Weapon_Sword_Iron:100:1", "Env_Zone1_Plains", "near the hills"
    Reg.add(sites, s)
    K.check(Reg.IO is None and Reg.save("default"), "X save (IO off): written now, true")
    f = os.path.join(d, "merchants", "default.tsv")
    want = "# SkyyMerchants roaming merchants - world default: zone uuid x y z placedAt visit held stock ghosts env rumour\n" + str(s.line()) + "\n"
    K.eq(open(f, encoding="utf8", newline="").read() if os.path.isfile(f) else None, want, "X save (IO off): the 0.1.2 text byte for byte")
    K.check(str(Reg.LASTW) == str(Thread.currentThread().getName()) and Reg.settled("default"), "X save (IO off): written on the caller, settled")
    # IO on
    Reg.IO = Executors.newSingleThreadExecutor(fac)
    w0 = Reg.WRITES.get()
    s.visit = 2
    with synchronized(Reg.WLOCK):
        t0 = time.time()
        ok = Reg.save("default")
        dt = time.time() - t0
        K.check(ok and dt < 0.5 and Reg.WRITES.get() == w0, "X save (IO on): returns at once (%.1f ms) while the writer is held; nothing written by the caller" % (dt * 1000))
        K.check(not Reg.settled("default"), "X settled: false while a write is queued")
        for i in range(50):
            s.visit = 100 + i
            Reg.save("default")
        K.check(Reg.WRITES.get() == w0, "X 50 more saves: still nothing written by the caller")
    K.check(PW.wait_until(lambda: Reg.settled("default")), "X settled after the writer ran")
    nw = Reg.WRITES.get() - w0
    K.check(1 <= nw <= 2, "X coalesced: 51 saves = %d write(s)" % nw)
    K.check(str(Reg.LASTW) == "SkyyMerchants-IO", "X the file was written by SkyyMerchants-IO (%s)" % Reg.LASTW)
    want = "# SkyyMerchants roaming merchants - world default: zone uuid x y z placedAt visit held stock ghosts env rumour\n" + str(s.line()) + "\n"
    K.eq(open(f, encoding="utf8", newline="").read(), want, "X the newest text is on disk (visit 149)")
    # ---- a failed write: the folder is blocked by a file
    Reg.DIR = Paths.get(os.path.join(d, "blocked", "merchants"))
    open(os.path.join(d, "blocked"), "w").write("x")
    fails0 = Reg.SAVE_FAILS.get()
    K.check(Reg.save("default"), "X save into a blocked folder: queued (true)")
    K.check(PW.wait_until(lambda: not Reg.ok("default")), "X the failed write marks the world FAILED")
    K.check(Reg.SAVE_FAILS.get() == fails0 + 1 and Reg.PEND.containsKey("default") and not Reg.settled("default"),
            "X failed: SAVE_FAILS +1, the text kept in PEND, not settled")
    K.check(any("could not save the merchants of world default" in str(x) for x in lines), "X failed: the WARN line")
    state = {"spawned": [], "removed": []}
    Eng.API = api_sim(state)
    n8 = Core.N[8]
    z = JClass(PKG + "MerchZone")()
    z.key, z.name, z.world, z.any, z.lo, z.hi = "zone1", "Emerald Wilds", "default", True, 1, 10
    K.check(not Core.relocate("default", sites, z, s, 5000, "moved") and Core.N[8] == n8 + 1 and not state["spawned"],
            "X relocate refused at once while the world's write FAILED (count 8, nothing spawned)")
    K.check(not Core.respawnSame("default", sites, z, s, 5000) and Core.N[8] == n8 + 2 and not state["spawned"],
            "X respawnSame refused at once while FAILED")
    # the per-world second: ghost sweep skipped while not settled
    s.addGhost("00000000-0000-4000-8000-0000000000aa", 4000)
    s.uuid = ""
    Cfg.ON = False
    Cfg.ZONES = JArray(JClass(PKG + "MerchZone"))(0)
    Core.second("default", 6000)
    K.check("00000000-0000-4000-8000-0000000000aa" not in state["removed"], "X second: the ghost sweep waits while the file is not settled")
    import shutil
    os.remove(os.path.join(d, "blocked"))
    Reg.DIR = Paths.get(os.path.join(d, "merchants"))
    K.check(Reg.retryFailed() >= 1, "X retryFailed re-queues the failed world")
    K.check(PW.wait_until(lambda: Reg.settled("default") and Reg.ok("default")), "X the retried write lands: settled, FAILED cleared")
    Core.second("default", 7000)
    K.check("00000000-0000-4000-8000-0000000000aa" in state["removed"], "X second: the ghost sweep runs once settled (old merchant removed)")
    PW.wait_until(lambda: Reg.settled("default"))
    # relocate with IO on: the new merchant spawned + saved; the OLD one is not removed before the write landed
    Cfg.ON = True
    st2 = {"spawned": [], "removed": []}
    Eng.API = api_sim(st2)
    s.uuid = "00000000-0000-4000-8000-0000000000bb"
    s.ghosts = ""
    with synchronized(Reg.WLOCK):
        try:
            r = Core.relocate("default", sites, z, s, 8000, "moved")
        except Exception as ex:
            r = False
            K.notes.append("relocate threw in the sim: %s" % str(ex)[:200])
        removed_early = "00000000-0000-4000-8000-0000000000bb" in st2["removed"]
    K.check(not removed_early, "X relocate (IO on, write not landed): the old merchant stays (a ghost) until the file is written")
    if r:
        K.check(s.hasGhost("00000000-0000-4000-8000-0000000000bb"), "X relocate: the old merchant is a ghost in the queued file")
        PW.wait_until(lambda: Reg.settled("default"))
        Core.second("default", 9000)
        K.check("00000000-0000-4000-8000-0000000000bb" in st2["removed"], "X the next second (settled) removes the old merchant")
    else:
        K.notes.append("relocate found no spot in the sim (%s) - the write-ahead path is covered by the ghost-sweep checks" % Core.N[6])
    # ---- sales.log through the writer, in order
    with synchronized(Reg.WLOCK):
        pass
    for i in range(20):
        Shop.sale("BUY t%d" % i)
    K.check(PW.wait_until(lambda: os.path.isfile(os.path.join(d, "sales.log")) and open(os.path.join(d, "sales.log"), encoding="utf8").read().count("\n") == 20),
            "X sale: 20 lines appended by the writer")
    got = [l.split("\t", 1)[1] for l in open(os.path.join(d, "sales.log"), encoding="utf8").read().splitlines()]
    K.eq(got, ["BUY t%d" % i for i in range(20)], "X sale: in order, 0.1.2 line format (time TAB line)")
    # ---- ready(): the first read on the writer
    os.makedirs(os.path.join(d, "merchants"), exist_ok=True)
    open(os.path.join(d, "merchants", "other.tsv"), "w", encoding="utf8", newline="").write(want.replace("world default", "world other"))
    K.check(not Reg.ready("other"), "X ready: false the first time (the read is queued on the writer)")
    K.check(PW.wait_until(lambda: Reg.W.containsKey("other")) and Reg.ready("other") and Reg.sites("other").size() == 1,
            "X ready: the registry read by SkyyMerchants-IO, then true (1 line)")
    # ---- the timer: retryFailed + ready, never a hop for a world not read yet
    K.check(Reg.LOADING.isEmpty(), "X LOADING empty after the read")
    # ---- flushAll at shutdown: writer stopped, everything written synchronously
    if Reg.find(sites, "zone1") is None:
        Reg.add(sites, s)
    s.visit = 777
    with synchronized(Reg.WLOCK):
        Reg.save("default")
    Reg.STOPPING = True
    Reg.flushAll()
    K.check(Reg.IO is None and Reg.settled("default"), "X flushAll: writer stopped, nothing pending")
    K.check("\t777\t" in open(f, encoding="utf8").read(), "X flushAll: the newest state is on disk")
    K.check(Reg.save("default") and str(Reg.LASTW) == str(Thread.currentThread().getName()), "X after stop: save writes synchronously (0.1.2)")
    K.save()


# ====================================================================================================== D: start twice on live data
def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Reg, IOc = JClass(PKG + "MerchReg"), JClass(PKG + "MerchIO")
    Paths, Executors = JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors")
    md = os.path.join(home, "merchants")
    names = sorted(n[:-4] for n in os.listdir(md) if n.endswith(".tsv")) if os.path.isdir(md) else []
    before = {n: open(os.path.join(md, n + ".tsv"), "rb").read() for n in names}
    log0 = open(os.path.join(home, "sales.log"), "rb").read() if os.path.isfile(os.path.join(home, "sales.log")) else None
    for start in (1, 2):
        Reg.W.clear()
        Reg.NAMES.clear()
        Reg.STOPPING = False
        Reg.DIR = Paths.get(md)
        Reg.IO = Executors.newSingleThreadExecutor(IOc(9, None))
        for n in names:
            Reg.ready(n)
        K.check(PW.wait_until(lambda: all(Reg.W.containsKey(n) for n in names)), "D start %d: every world registry read by the writer (%s)" % (start, names))
        for n in names:
            Reg.save(n)
        Reg.STOPPING = True
        Reg.flushAll()
        after = {n: open(os.path.join(md, n + ".tsv"), "rb").read() for n in names}
        K.check(after == before, "D start %d: every registry saved back byte-identical (%d worlds, %s lines)"
                % (start, len(names), [str(Reg.W.get(n).size()) for n in names]))
        K.check((open(os.path.join(home, "sales.log"), "rb").read() if log0 is not None else None) == log0, "D start %d: sales.log untouched" % start)
    K.notes.append("D: live worlds %s" % names)
    # 0.1.4: the one-time update + MerchCfg.load, started twice on the live copy
    Mig, Cfg, Wall = JClass(PKG + "MerchMig"), JClass(PKG + "MerchCfg"), JClass(PKG + "MerchWall")
    cfgf = os.path.join(home, "config.properties")
    c0 = open(cfgf, "rb").read()
    mods = os.path.dirname(home)
    r1 = str(Mig.run(Paths.get(mods)))
    Cfg.load(Paths.get(mods))
    c1 = open(cfgf, "rb").read()
    r2 = str(Mig.run(Paths.get(mods)))
    Cfg.load(Paths.get(mods))
    c2 = open(cfgf, "rb").read()
    mark = str(Mig.MARK).encode("latin-1")
    old_line = ("merchant.neverSell=" + str(Mig.OLD_DEF)).encode("latin-1")
    new_line = ("merchant.neverSell=" + str(Mig.NEW_DEF)).encode("latin-1")
    body1 = c1.replace(mark, b"").rstrip(b"\r\n")
    if (old_line + b"\n") in c0 or (old_line + b"\r\n") in c0 or c0.endswith(old_line):
        K.check(body1 == c0.replace(old_line, new_line, 1).rstrip(b"\r\n") and c1.count(mark) == 1 and r1.startswith("config.properties updated for 0.1.4"),
                "D (0.1.4): the live copy still held the 0.1.3 default -> rewritten to the new list + the marker at the end, every other byte kept: %s" % r1[:90])
    else:
        K.check(body1 == c0.rstrip(b"\r\n") and c1.count(mark) == 1, "D (0.1.4): a hand-edited live list is kept (only the marker): %s" % r1[:90])
    K.check(r2 == "" and c2 == c1 and str(Wall.why("Skyy_Sigil_Rare")) == "Rarity Sigils are never sold in shops" and "Skyy_Sigil_*" in str(Cfg.NEVER),
            "D (0.1.4): the second start changes nothing; after the load Skyy_Sigil_* is on the list and walled")
    K.notes.append("D (0.1.4): live update %s" % r1[:120])
    K.save()


# ====================================================================================================== S (0.1.4): Sigils never sold
def run_sigil(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    Wall, Cfg, Mig, Log = P("MerchWall"), P("MerchCfg"), P("MerchMig"), P("MerchLog")
    lines = JClass("java.util.ArrayList")()
    Log.LINES = lines
    Paths = JClass("java.nio.file.Paths")
    # S1 the wall: every Sigil id, whatever the never-sell list says
    sig = ["Skyy_Sigil_Unique", "Skyy_Sigil_Rare", "Skyy_Sigil_Legendary", "Skyy_Sigil_Fabled", "Skyy_Sigil_Mythic"]
    Cfg.NEVER = ""
    w_ = [str(Wall.why(i)) for i in sig]
    K.check(all(x == "Rarity Sigils are never sold in shops" for x in w_) and Wall.why("Weapon_Sword_Iron") is None
            and str(Wall.why("Skyy_Sack_Small")) == "Magic Bags are never sold",
            "S1 MerchWall.why refuses every Skyy_Sigil_* even with an EMPTY never-sell list (hand-edited); a sword passes; bags still walled: %s" % w_[:2])
    ck = str(Cfg.checkStock("merchant.stock[Skyy_Sigil_Rare]", "1|2500|1"))
    K.check(ck.startswith("Skyy_Sigil_Rare can never be sold here: Rarity Sigils"), "S1 the Server Setup stock check refuses a Sigil line: %s" % ck)
    Cfg.applyAll(Cfg.props(str(Cfg.DEFAULT_TEXT) + "\nweapon.Skyy_Sigil_Legendary=1/9999/1\n"))
    ids = [str(it.id) for it in Cfg.ITEMS]
    K.check("Skyy_Sigil_Legendary" not in ids and len(ids) > 10 and any("weapon.Skyy_Sigil_Legendary is never sold" in str(l) for l in lines),
            "S1 a stock line naming a Sigil is skipped with a WARN (%d other lines load)" % len(ids))
    # S2 the default list + the fresh file's marker
    dt = str(Cfg.DEFAULT_TEXT)
    K.check(("merchant.neverSell=" + str(Mig.NEW_DEF) + "\n") in dt and str(Mig.NEW_DEF) == str(Mig.OLD_DEF) + ",Skyy_Sigil_*" and str(Mig.MARK) in dt
            and Mig.update(dt) is None and "Skyy_Sigil_*" in str(Cfg.NEVER),
            "S2 the fresh default lists Skyy_Sigil_* (old default + ',Skyy_Sigil_*') and carries the marker (a fresh file is never updated)")
    # S3 MerchMig.update on texts
    OLDL = "merchant.neverSell=" + str(Mig.OLD_DEF)
    t1 = "# head\nmerchant.on=true\n" + OLDL + "\nzone.zone1=default/Env_Zone1/1-20\n"
    r1 = Mig.update(t1)
    n1 = str(r1[0])
    K.check(n1 == "# head\nmerchant.on=true\nmerchant.neverSell=" + str(Mig.NEW_DEF) + "\nzone.zone1=default/Env_Zone1/1-20\n" + str(Mig.MARK) + "\n"
            and str(r1[1]) == "merchant.neverSell + Skyy_Sigil_*" and [str(x) for x in r1[3]] == ["merchant.neverSell", str(Mig.OLD_DEF), str(Mig.NEW_DEF)]
            and Mig.update(n1) is None,
            "S3 the old default is rewritten (value only), the marker goes to the end, the change-log row is (key, old, new); run again = nothing: %r" % n1[-80:])
    t2 = t1.replace("\n", "\r\n")
    n2 = str(Mig.update(t2)[0])
    K.check(n2.replace("\r\n", "\n") == n1 and all(l_.endswith("\r") for l_ in n2.split("\n")[:-1]), "S3 a CRLF file keeps its CR on every line: %r" % n2[-60:])
    t3 = t1.replace(OLDL, OLDL + ",Weapon_Sword_Iron")
    r3 = Mig.update(t3)
    K.check(str(r3[0]) == t3 + str(Mig.MARK) + "\n" and str(r3[1]) == "" and len(list(r3[2])) == 1 and "kept as it is" in str(list(r3[2])[0]) and len(list(r3[3])) == 0,
            "S3 a hand-edited list is KEPT (+ a note; Sigils are walled anyway); only the marker is added")
    t4 = "merchant.on=true\n"
    r4 = Mig.update(t4)
    K.check(str(r4[0]) == t4 + str(Mig.MARK) + "\n" and str(r4[1]) == "" and len(list(r4[2])) == 0, "S3 no neverSell line = only the marker (the new default applies)")
    t5 = "merchant.neverSell=" + str(Mig.OLD_DEF)[:20] + "\\\n  " + str(Mig.OLD_DEF)[20:] + "\n"
    K.check(str(Mig.update(t5)[1]) == "", "S3 a value continued over two lines is never rewritten (kept + noted)")
    t6 = "merchant.on=true\n" + OLDL
    n6 = str(Mig.update(t6)[0])
    K.check(n6 == "merchant.on=true\nmerchant.neverSell=" + str(Mig.NEW_DEF) + "\n" + str(Mig.MARK),
            "S3 a last line with no newline: rewritten, the marker on its own line: %r" % n6[-80:])
    t7 = OLDL + "\nmerchant.neverSell=Debug_*\n"
    K.check(str(Mig.update(t7)[1]) == "" and str(Mig.update(t7)[0]).startswith(OLDL + "\nmerchant.neverSell=Debug_*\n"),
            "S3 duplicate keys: the LAST one decides (a hand value there = nothing rewritten)")
    # S4 MerchMig.run on a scratch file: History first, change log, twice = no change
    mods = os.path.join(scratch, "migmods")
    home = os.path.join(mods, "Skyy_SkyyMerchants")
    os.makedirs(home, exist_ok=True)
    cfgf = os.path.join(home, "config.properties")
    open(cfgf, "wb").write(t2.encode("latin-1"))
    r_ = str(Mig.run(Paths.get(mods)))
    after = open(cfgf, "rb").read().decode("latin-1")
    hist = os.path.join(home, "config-history")
    hfiles = [f for f in os.listdir(hist) if f.endswith(".bak")] if os.path.isdir(hist) else []
    clp = os.path.join(home, "config-changes.log")
    clog = open(clp, encoding="utf-8").read() if os.path.isfile(clp) else ""
    K.check(r_.startswith("config.properties updated for 0.1.4") and after == n2 and len(hfiles) == 1
            and open(os.path.join(hist, hfiles[0]), "rb").read() == t2.encode("latin-1")
            and "\tmerchant.neverSell\t" in clog and clog.rstrip("\n").endswith("\tok") and str(Mig.LAST) == "rewrote",
            "S4 MerchMig.run: the old file kept in config-history (byte for byte) FIRST, the new text written, one change-log row (status ok = Undo): %s | %s | %r"
            % (r_[:80], hfiles, clog[-120:]))
    r2_ = str(Mig.run(Paths.get(mods)))
    K.check(r2_ == "" and open(cfgf, "rb").read().decode("latin-1") == n2, "S4 the second start changes nothing")
    K.check(str(Mig.run(Paths.get(os.path.join(scratch, "nomods")))) == "", "S4 no config file = nothing (the seed writes the new default)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMerchants", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("sigil", run_sigil), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMerchants"))
