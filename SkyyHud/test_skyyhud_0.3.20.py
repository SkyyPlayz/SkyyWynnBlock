"""SkyyHud 0.3.20 harness - THE NOTIFICATION FEED + SKILL XP FLASH + MESSAGE ROUTING round (tools/hud_0_3_20_patch.py). Built on
tools/harness_kit.py: each phase a fresh child JVM (the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in the scratch
folder). Every new code path is EXECUTED on the real jar classes (real HudMain.build / feedFill / feedTick, the real bridge Functions, the
real 250 ms step, the real config kit rows) - only the engine's player / world are stand-ins.

    python SkyyHud/test_skyyhud_0.3.20.py [--jar SkyyHud-0.3.20.jar] [--old SkyyHud-0.3.19.jar] [--dir <scratch>] [--keep]

  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.19 -> 0.3.20: the 11 new classes; exactly the listed classes / members differ; non-class entries: the manifest
  E    exec     E0 the ids + the new built-in spots (no two default boxes touch); E1 saved layouts never move + the feed's first free spot
                (feedPlace) for a file without a Feed line; E2 the bridge API (feed:fn:push / xpflash:fn:push argument checks, the 64 bound,
                widget off / feed off / no HUD = FALSE) + 8 Java threads pushing at once while the 250 ms step drains (nothing lost or
                counted twice); E3 merge / fade / caps on the real step (x1 -> x4 -> x9, the 0.3 s highlight, 100 % -> 60 % -> 25 % -> gone at
                4.0 / 4.3 / 4.7 / 5.0 s, the 3 s merge window, the 4-card / maxCards cap, kinds -> chips); E4 the real HUD markup + feedFill
                sets (fixed slots, only .Text / .Visible / .ItemId, nothing when nothing changed, Item icons Show / Hide, top / bottom
                stacking, sizes, Feed off); E5 the Skill XP flash (2 s batch, +79 formats, the tints / edge / gain sets per stage, the
                temporary row of a hidden skill = a shape re-send, a shown row = a wider box, Hide = no temporary row); E6 msgroute (server
                defaults, the player's switches through settings:fn:get, the widget / feed fallbacks, system / unknown = chat) + the settings
                registration (20 switches, defaults follow Server Setup, the node) + the Server Setup rows through the REAL config kit;
                E7 /skyyhud testfeed's Feed.test end to end (routing, the 2-card overflow, the delayed merges on SkyyHud's thread, the XP
                pushes); E8 the timer: FeedTick.run with nobody active does nothing, an active player gets ONE update per step and leaves
                ACTIVE when idle; E9 bytecode facts (the feed timer on HudThreads at 250 ms, never the engine scheduler; the push / route
                paths touch no engine class; the admin command's permission calls)
  FIX  review fixes: 1 cards pushed out before they were drawn / XP past the 16 cap become chat lines (flushOver), drawn ones do not;
       2 the 60 % / 25 % fade variants keep the chips + hairline; 3 unknown item ids become no icon (iconOk on the item asset map)
  X19  the 0.3.19 exec checks (HudThreads, WTime, hubWorld, the minimap bounds, the tick / attach paths, its bytecode facts) on THIS jar
  ST   live     START TWICE on a scratch COPY of the live Skyy_SkyyHud (HudCfg.load incl. the feed keys missing from the live file, the
                config kit, every saved layout): nothing written, the same layouts, every saved line exactly as saved, the feed's spot free
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): how the cards / tints look, .Visible / .ItemId sets and an ItemIcon inside a HUD document, the
fade feel at 250 ms steps, the real chat height (the feed's spot is the mockup's estimate).
Scratch: tools/dev/scratch/hudfeed/h20 (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, re, json, time, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PWK

VERSION, PREV = "0.3.20", "0.3.19"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(HK.arg("--old", os.path.join(HERE, "SkyyHud-%s.jar" % PREV)))
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hudfeed", "h20")))
PKG = "com.skyy.hud."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyHud")
OLD_IDS = ["Coords", "Zone", "Gclock", "Rclock", "Day", "Session", "Online", "Coins", "Party", "Guild", "Skills", "Combat", "Minimap", "Seasons",
           "Abilities"]
KINDS = ["pickup", "drop", "skillxp", "levelup", "coins", "collection", "rankup", "quest", "heal", "petxp"]
DEFS = {"pickup": "feed", "drop": "feed", "skillxp": "feed", "levelup": "chat", "coins": "feed", "collection": "feed", "rankup": "chat",
        "quest": "feed", "heal": "feed", "petxp": "feed"}

EXPECT = {}       # filled from the first compare run (section C); see the bottom of this file
ADDED = ["Feed", "FeedCard", "FeedCfg", "FeedPushFn", "FeedState", "FeedTestStep", "FeedTick", "FeedView", "HudTestFeedCmd", "MsgRouteFn", "XpFlashFn"]


def load_module(path, alias):
    spec = importlib.util.spec_from_file_location(alias, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def jv(v):
    try:
        x = json.loads(v)
    except Exception:
        return v
    if isinstance(x, dict) and list(x) == ["0"]:
        x = x["0"]
    return x


def run_exec(out, jar, scratch, home):
    hcls = os.path.join(scratch, "hcls20")
    os.makedirs(hcls, exist_ok=True)
    # the load / drain helpers are compiled BEFORE the JVM that uses them starts (their folder must be on its class path)
    import subprocess
    p_ = subprocess.run([sys.executable, os.path.abspath(__file__), "--mkload", hcls, "--jar", jar], env=dict(os.environ))
    if p_.returncode != 0:
        K0 = HK.Child(out)
        K0.check(False, "E2: the load helper classes were not compiled")
        K0.save()
        return
    import jpype
    from jpype import JClass, JImplements, JOverride, JArray, JObject, JLong, JInt
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST, hcls], verify=True)
    UUID, System, CHM = JClass("java.util.UUID"), JClass("java.lang.System"), JClass("java.util.concurrent.ConcurrentHashMap")
    Paths, Long, Integer, Double, Boolean, String = (JClass("java.nio.file.Paths"), JClass("java.lang.Long"), JClass("java.lang.Integer"),
                                                     JClass("java.lang.Double"), JClass("java.lang.Boolean"), JClass("java.lang.String"))
    PRef = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jf(c, n):
        k = c.class_ if hasattr(c, "class_") else c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)

    def setf(obj, cls, name, val):
        jf(cls, name).set(obj, val)
    # a bare JVM has no Item asset store (the editor's canvas handles): an empty one (the 0.3.12 - 0.3.18 harness pattern)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(B.SERVER_JAR)
    fake = jp.makeClass("com.hypixel.hytale.assetstore.SkyyTestFakeStore20", jp.get("com.hypixel.hytale.assetstore.AssetStore"))
    fake.addConstructor(JClass("javassist.CtNewConstructor").make(
        "public SkyyTestFakeStore20() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    store = U.allocateInstance(fake.toClass(AS.class_))
    amap = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")()
    jf(AS, "assetMap").set(store, amap)
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    jf(ItemC, "ASSET_STORE").set(None, store)
    # FIX 3: the items the tests draw are "loaded" (real Assets.zip ids); anything else is unknown to the server
    for id_ in ("Plant_Crop_Pumpkin_Item", "Wood_Oak_Trunk", "Ingredient_Crystal_White"):
        jf(amap.getClass(), "assetMap").get(amap).put(id_, U.allocateInstance(ItemC.class_))
    H = lambda n: JClass(PKG + n)
    WL, Wid, LS, HM, EP, SP, Cfg, Plugin = (H("WLayout"), H("Widgets"), H("LayoutStore"), H("HudMain"), H("EditorPage"), H("SettingsPage"),
                                           H("HudCfg"), H("SkyyHudPlugin"))
    Feed, FCfg, FV, HT = H("Feed"), H("FeedCfg"), H("FeedView"), H("HudThreads")
    plugin = U.allocateInstance(Plugin.class_)
    setf(plugin, Plugin, "huds", CHM())
    mBuild = HM.class_.getDeclaredMethod("build", UCB.class_)
    mBuild.setAccessible(True)
    bridge = CHM()
    System.getProperties().put("skyy.bridge", bridge)
    work = os.path.join(scratch, "e")
    os.makedirs(work, exist_ok=True)

    def uid(n):
        return UUID(0x320, n)

    def pref(n, name="Mia"):
        pr = U.allocateInstance(PRef.class_)
        setf(pr, PRef, "uuid", uid(n))
        setf(pr, PRef, "username", name)
        return pr

    def cmds(b):
        return [[str(c.type.name()), None if c.selector is None else str(c.selector), None if c.data is None else str(c.data),
                 None if c.text is None else str(c.text)] for c in b.getCommands()]

    def sets(cm):
        return dict((c[1], jv(c[2])) for c in cm if c[0] == "Set" and c[1])

    def grp(cm, base):
        g = [c[3] for c in cm if c[0] == "AppendInline" and c[3] and ("Group #%s " % base) in c[3]]
        return g[0] if len(g) == 1 else None

    def use_dir(name):
        d = os.path.join(work, name)
        os.makedirs(d, exist_ok=True)
        LS.DIR = Paths.get(os.path.join(d, "layouts"))
        LS.CACHE.clear()
        return d

    def hud(pr):
        h = HM(pr)
        b = UCB()
        mBuild.invoke(h, b)
        return h, cmds(b)

    def rebuild(h):
        b = UCB()
        mBuild.invoke(h, b)
        return cmds(b)

    def ffill(h):
        b = UCB()
        re_ = bool(h.feedFill(b, False))
        return re_, cmds(b)

    def arr(*xs):
        return JArray(JObject)(list(xs))
    cfgdir = os.path.join(work, "cfg")
    os.makedirs(cfgdir, exist_ok=True)
    Cfg.FILE = Paths.get(os.path.join(cfgdir, "config.properties"))
    Cfg.load()
    cfg_text = open(os.path.join(cfgdir, "config.properties"), encoding="latin-1").read()
    K.check(all(("msg.%s=%s" % (k_, d_)) in cfg_text for k_, d_ in DEFS.items()) and "feed.showSecs=4" in cfg_text and "feed.maxCards=4" in cfg_text,
            "E6: a NEW config.properties carries the feed keys and the 10 msg.<kind> defaults")
    # ================================================================================== E0 ids + the new built-in spots
    JIDS = [str(x) for x in Wid.IDS]
    K.check(JIDS == OLD_IDS + ["Feed"], "E0: Feed is APPENDED to Widgets.IDS (old files / codes keep their meaning): %s" % JIDS[-3:])
    use_dir("e0")
    me = pref(1)
    u = me.getUuid()
    m0 = LS.get(u)

    def at(m_, id_):
        l_ = m_.get(id_)
        return (bool(l_.en), str(l_.anchor), int(l_.dx), int(l_.dy), int(l_.scale))
    want = {"Party": (True, "tl", 8, 200, 100), "Guild": (True, "tl", 8, 324, 100), "Skills": (True, "tr", 8, 240, 100),
            "Abilities": (True, "br", 460, 21, 100), "Feed": (True, "bl", 8, 488, 100), "Coords": (True, "tl", 8, 8, 100),
            "Zone": (True, "tr", 8, 8, 100), "Gclock": (True, "bl", 8, 40, 100), "Coins": (True, "br", 8, 8, 100),
            "Combat": (True, "t", 0, 130, 100), "Minimap": (True, "tr", 8, 40, 100), "Online": (False, "tr", 8, 206, 100)}
    got0 = dict((k_, at(m0, k_)) for k_ in want)
    fl0 = m0.get("Feed")
    K.check(got0 == want and int(fl0.bw) == 280 and int(fl0.bh) == 140 and bool(fl0.opt),
            "E0: a new player's spots = the approved defaults (Party tl 8,200 / Guild tl 8,324 / Skills tr 8,240 / Abilities br 460,21 / Feed "
            "bl 8,488 280 x 140, Item icons Hide), the others unchanged: %s" % dict((k_, v_) for k_, v_ in got0.items() if v_ != want[k_]))

    def box(m_, id_):
        l_ = m_.get(id_)
        w_ = int(l_.bw) * int(l_.scale) // 100
        h_ = int(Wid.hMax(l_))
        p_ = Wid.screenPosWH(l_, w_, h_)
        return (int(p_[0]), int(p_[1]), w_, h_)

    def touch(a, b, g=0):
        return a[0] < b[0] + b[2] + g and b[0] < a[0] + a[2] + g and a[1] < b[1] + b[3] + g and b[1] < a[1] + a[3] + g
    shown = [k_ for k_ in JIDS if bool(m0.get(k_).en) and k_ not in ("Seasons",)]
    hits = [(a_, b_) for i_, a_ in enumerate(shown) for b_ in shown[i_ + 1:] if touch(box(m0, a_), box(m0, b_))]
    fb = box(m0, "Feed")
    K.check(not hits and fb == (8, 452, 280, 140) and not touch(fb, (8, 600, 560, 360)),
            "E0: no two default boxes touch (maximum boxes at 1080p: %s); the feed box %s sits 8 px above the estimated chat" % (hits, fb))
    # ================================================================================== E1 saved layouts never move + feedPlace
    d1 = use_dir("e1")
    lyd = os.path.join(d1, "layouts")
    os.makedirs(lyd, exist_ok=True)
    u_old, u_min, u_feed = uid(11), uid(12), uid(13)
    old_lines = {"Party": "1,tl,8,320,100,1", "Guild": "1,tl,8,444,100,1", "Skills": "1,tl,8,544,100,1", "Abilities": "1,tl,8,760,100,1"}
    files = {u_old: "".join("%s=%s\n" % kv for kv in old_lines.items()), u_min: "Coords=1,tl,8,8,100,1\n",
             u_feed: "Feed=1,tl,100,100,100,1\nGuild=1,tl,8,444,100,1\n"}
    for uu, txt in files.items():
        open(os.path.join(lyd, str(uu) + ".properties"), "w", encoding="latin-1").write(txt)
    snap = dict((f_, open(os.path.join(lyd, f_), "rb").read()) for f_ in os.listdir(lyd))
    mo = LS.get(u_old)
    kept = all(str(mo.get(k_).ser()) == v_ for k_, v_ in old_lines.items())
    fo = mo.get("Feed")
    fbo = box(mo, "Feed")
    others = [box(mo, k_) for k_ in JIDS if k_ not in ("Feed", "Seasons") and bool(mo.get(k_).en)]
    free = not any(touch(fbo, b_, 4) for b_ in others) and not touch(fbo, (8, 600, 560, 360), 4)
    K.check(kept and (str(fo.anchor), int(fo.dx), int(fo.dy)) != ("bl", 8, 488) and free and fbo[0] + fbo[2] <= 960 and 8 <= fbo[1],
            "E1: a 0.3.19 file with the OLD spots (Party 8,320 / Guild 8,444 / Skills 8,544 / Abilities 8,760): every saved line loads exactly "
            "(%s); the feed (no Feed line) left its default spot, which touched Guild / Skills, for a free one: %s %s,%s -> box %s"
            % (kept, fo.anchor, fo.dx, fo.dy, fbo))
    mm_ = LS.get(u_min)
    mf_ = LS.get(u_feed)
    K.check(at(mm_, "Feed") == (True, "bl", 8, 488, 100) and str(mf_.get("Feed").ser()) == "1,tl,100,100,100,1" and str(mf_.get("Guild").ser()) == "1,tl,8,444,100,1"
            and dict((f_, open(os.path.join(lyd, f_), "rb").read()) for f_ in os.listdir(lyd)) == snap,
            "E1: a file whose widgets leave the default free keeps the feed at bl 8,488; a SAVED Feed line is never moved (even over a Guild); "
            "LayoutStore.get wrote nothing")
    # ================================================================================== E2 the bridge API
    use_dir("e2")
    Feed.STATES.clear()
    Feed.ACTIVE.clear()
    Feed.PLUGIN = plugin
    Feed.publish()
    fpush, fxp, froute = bridge.get("feed:fn:push"), bridge.get("xpflash:fn:push"), bridge.get("msgroute:fn:get")
    h1 = HM(me)
    LS.get(u)
    plugin.huds.put(u, h1)
    T, F_ = True, False
    res = [bool(fpush.apply("x")), bool(fpush.apply(arr(u, "pickup", None))), bool(fpush.apply(arr(u, "Pick_up", None, "Pumpkin", Long(1)))),
           bool(fpush.apply(arr(u, "pickup", None, "   ", Long(1)))), bool(fpush.apply(arr(uid(99), "pickup", None, "Pumpkin", Long(1)))),
           bool(fpush.apply(arr(str(u), "pickup", "Bad Id!", "Pumpkin", Long(1))))]
    st = Feed.STATES.get(u)
    q1 = [list(st.q.peek())] if st is not None and st.q.peek() is not None else []
    K.check(res == [F_, F_, F_, F_, F_, T] and len(q1) == 1 and q1[0][2] is None,
            "E2: feed:fn:push refuses a non-array, too few elements, a bad kind, an empty text, a player without a HUD; takes a String uuid "
            "(a bad item id becomes null): %s" % res)
    LS.get(u).get("Feed").en = False
    off1 = bool(fpush.apply(arr(u, "pickup", None, "Pumpkin", Long(1))))
    LS.get(u).get("Feed").en = True
    FCfg.ENABLED = False
    off2 = bool(fpush.apply(arr(u, "pickup", None, "Pumpkin", Long(1))))
    FCfg.ENABLED = True
    st.q.clear()
    st.qn.set(0)
    d0 = int(Feed.DROPPED.get())
    burst = [bool(fpush.apply(arr(u, "pickup", None, "P%d" % i, None))) for i in range(70)]
    K.check(not off1 and not off2 and burst.count(True) == 64 and burst[64:] == [False] * 6 and int(Feed.DROPPED.get()) - d0 == 6
            and int(st.qn.get()) == 64 and Feed.ACTIVE.containsKey(u),
            "E2: FALSE while the player's Feed widget is off / the feed is off in Server Setup; 64 waiting pushes at most (6 more refused + "
            "counted), the player is ACTIVE")
    st.q.clear()
    st.qn.set(0)
    xr0 = bool(fxp.apply(arr(u, "Mining", Long(5))))      # review 2 fix: no SkyySkills = the Skills widget draws nothing -> FALSE

    @JImplements("java.util.function.Function")
    class Lvl0(object):
        @JOverride
        def apply(self, x):
            return Integer(1)
    bridge.put("skill:fn:level", Lvl0())                  # SkyySkills present for the push checks below (removed after FIX1)
    K.check(not xr0 and st.q.peek() is None, "E2 (review 2 fix): xpflash:fn:push answers FALSE without SkyySkills (nothing would be drawn)")
    xr = [bool(fxp.apply(arr(u, "Mining"))), bool(fxp.apply(arr(u, "Min<ing", Long(5)))), bool(fxp.apply(arr(u, "Mining", Double(0.2)))),
          bool(fxp.apply(arr(u, "Mining", Double(12.6))))]
    LS.get(u).get("Skills").en = False
    xr.append(bool(fxp.apply(arr(u, "Mining", Long(5)))))
    LS.get(u).get("Skills").en = True
    ev = list(st.q.peek()) if st.q.peek() is not None else []
    K.check(xr == [F_, F_, F_, T, F_] and len(ev) == 3 and str(ev[1]) == "Mining" and int(ev[2]) == 13,
            "E2: xpflash:fn:push refuses no amount / a bad skill name / less than 0.5 / the Skills widget off; 12.6 XP = 13: %s %s" % (xr, ev))
    st.q.clear()
    st.qn.set(0)
    # 8 Java threads push at once while the step drains on another thread: nothing lost, nothing counted twice
    FCfg.SHOW_SECS = 15.0
    FCfg.MERGE_SECS = 10.0
    st.cards.clear()
    PL, DR, Thr = JClass("skyyhud320.PushLoad"), JClass("skyyhud320.Drain"), JClass("java.lang.Thread")
    PL.OK.set(0)
    PL.NO.set(0)
    d0 = int(Feed.DROPPED.get())
    dr = DR(st)
    td = Thr(dr)
    td.start()
    ths = [Thr(PL(fpush, u, 2000)) for _i in range(8)]
    for t_ in ths:
        t_.start()
    for t_ in ths:
        t_.join(60000)
    time.sleep(0.2)
    dr.stop = True
    td.join(10000)
    Feed.step(st, System.currentTimeMillis())
    total = sum(int(c_.count) for c_ in st.cards)
    ok_, no_ = int(PL.OK.get()), int(PL.NO.get())
    K.check(ok_ + no_ == 16000 and total == ok_ and int(Feed.DROPPED.get()) - d0 == no_ and int(st.qn.get()) == 0 and st.q.isEmpty()
            and len(st.cards) == 1 and int(dr.steps) > 10,
            "E2: THREAD SAFETY: 8 Java threads x 2,000 pushes against a draining step thread (%d steps): accepted %d + refused %d = 16,000, the "
            "one merged card counts exactly the accepted %d, the refusals = DROPPED, queue empty" % (int(dr.steps), ok_, no_, total))
    FCfg.SHOW_SECS = 4.0
    FCfg.MERGE_SECS = 3.0
    st.cards.clear()
    # ================================================================================== E3 merge / fade / caps (the real step, fake time)
    t0 = 10_000_000_000

    def view():
        return Feed.viewOf(u)

    def vs(v_):
        return [(str(v_.name[i]), str(v_.cnt[i]), int(v_.stage[i]), bool(v_.hi[i]), int(v_.cls[i])) for i in range(int(v_.n))]

    def push(kind, text, cnt=None, icon=None):
        return bool(fpush.apply(arr(u, kind, icon, text, None if cnt is None else Long(cnt))))
    push("pickup", "Pumpkin", 1, "Plant_Crop_Pumpkin_Item")
    Feed.step(st, t0)
    a1 = vs(view())
    push("pickup", "Pumpkin", 3, "Plant_Crop_Pumpkin_Item")
    Feed.step(st, t0 + 800)
    a2 = vs(view())
    Feed.step(st, t0 + 1150)
    a3 = vs(view())
    push("pickup", "Pumpkin", 5, "Plant_Crop_Pumpkin_Item")
    Feed.step(st, t0 + 2100)
    a4 = vs(view())
    K.check(a1 == [("Pumpkin", "x1", 1, False, 0)] and a2 == [("Pumpkin", "x4", 1, True, 0)] and a3 == [("Pumpkin", "x4", 1, False, 0)]
            and a4 == [("Pumpkin", "x9", 1, True, 0)] and str(view().icon[0]) == "Plant_Crop_Pumpkin_Item",
            "E3: MERGE: Pumpkin x1 -> x4 (0.8 s, gold highlight for 0.3 s) -> x9 (2.1 s), one card: %s %s %s %s" % (a1, a2, a3, a4))
    t1 = t0 + 2100
    fade = []
    for dt in (4299, 4300, 4699, 4700, 4999, 5000):
        Feed.step(st, t1 + dt)
        v_ = view()
        fade.append(int(v_.stage[0]) if int(v_.n) else 0)
    K.check(fade == [1, 2, 2, 3, 3, 0] and len(st.cards) == 0,
            "E3: FADE: fully shown 4 s after the last change, 60 %% at +4.3 s, 25 %% at +4.7 s, gone at +5.0 s: %s" % fade)
    t2 = t1 + 10000
    push("pickup", "Oak Log", 1)
    Feed.step(st, t2)
    push("pickup", "oak log", 1)
    Feed.step(st, t2 + 2999)
    m3 = vs(view())
    push("pickup", "Oak Log", 1)
    Feed.step(st, t2 + 2999 + 3000)
    m4 = vs(view())
    K.check(m3 == [("oak log", "x2", 1, True, 0)] and len(m4) == 2 and m4[0][1] == "x1" and m4[1][1] == "x2",
            "E3: the merge window: within 3 s (same text, any case, no item id) = the same card; 3 s after its last change = a new card: %s / %s" % (m3, m4))
    st.cards.clear()
    t3 = t2 + 20000
    for i, (k_, tx_) in enumerate((("heal", "+8 HP  Priest heal"), ("coins", "+120 coins  Bank interest"), ("petxp", "Wolf  +35 Pet XP"),
                                    ("quest", "Chop logs  7/10"), ("drop", "Double drop!  Oak Log"), ("pickup", "Pumpkin"))):
        push(k_, tx_)
    Feed.step(st, t3)
    c6 = vs(view())
    K.check([x[0] for x in c6] == ["Pumpkin", "Double drop!  Oak Log", "Chop logs  7/10", "Wolf  +35 Pet XP"] and [x[4] for x in c6] == [0, 1, 0, 3]
            and all(x[1] == "" for x in c6) and len(st.cards) == 4,
            "E3: CAP: 6 cards in one step -> the 4 newest (newest first), the oldest pushed out at once; chips: drop gold, pet XP purple, "
            "quest / pickup blue; no count given = none shown: %s" % c6)
    ov6 = [str(x) for x in st.over]
    K.check(ov6 == ["+8 HP  Priest heal", "+120 coins  Bank interest"] and int(Feed.flushOver(st, None)) == 0 and st.over.isEmpty(),
            "FIX1: the 2 cards pushed out before any step drew them become chat lines (oldest first; flushOver sends them on SkyyHud's "
            "thread, then clears): %s" % ov6)
    push("drop", "Double drop!  Oak Log")
    push("heal", "+8 HP  Priest heal")
    FCfg.MAX_CARDS = 2
    Feed.step(st, t3 + 100)
    c2 = vs(view())
    FCfg.MAX_CARDS = 4
    K.check(len(c2) == 2 and c2[0][0] == "+8 HP  Priest heal" and c2[0][4] == 2 and c2[1] == ("Double drop!  Oak Log", "x2", 1, True, 1),
            "E3: Server Setup 'Most cards at once' 2 -> 2 cards; a repeat without a count shows x2; heal = the green chip: %s" % c2)
    K.check(st.over.isEmpty(), "FIX1: cards pushed out AFTER they were drawn do not go to chat (they were seen): %s" % [str(x) for x in st.over])
    # FIX 1: an XP batch past the 16 pending skills = a chat line, not silence
    st.cards.clear()
    st.batch.clear()
    st.flash.clear()
    for i in range(17):
        fxp.apply(arr(u, "Skill" + "ABCDEFGHIJKLMNOPQ"[i], Long(5 + i)))
    Feed.step(st, t3 + 15000)
    ovx = [str(x) for x in st.over]
    K.check(int(st.batch.size()) == 16 and ovx == ["+21 SkillQ XP"], "FIX1: a 17th pending skill's XP becomes a chat line: %s" % ovx)
    st.over.clear()
    st.batch.clear()
    bridge.remove("skill:fn:level")
    # FIX 3: an item id the server does not have is dropped (the card keeps its text, no ItemId is ever sent); known ids stay; cached
    push("drop", "Oak Log", 1, "Wood_Oak_Trunkk")
    push("drop", "Strange", 1, "Foo:Bar")
    push("pickup", "Oak Log", 1, "Wood_Oak_Trunk")
    Feed.step(st, t3 + 16000)
    v9 = view()
    ic9 = [(str(v9.name[i]), None if v9.icon[i] is None else str(v9.icon[i])) for i in range(int(v9.n))]
    K.check(ic9 == [("Oak Log", "Wood_Oak_Trunk"), ("Strange", None), ("Oak Log", None)] and Feed.ICONS.get("Wood_Oak_Trunkk") is not None
            and not bool(Feed.ICONS.get("Wood_Oak_Trunkk")) and bool(Feed.ICONS.get("Wood_Oak_Trunk")) and bool(Feed.iconOk("Plant_Crop_Pumpkin_Item"))
            and not bool(Feed.iconOk(None)),
            "FIX3: unknown item ids ('Wood_Oak_Trunkk', 'Foo:Bar') become no icon (text kept), the loaded 'Wood_Oak_Trunk' keeps its icon; "
            "results cached per id: %s" % ic9)
    st.cards.clear()
    long_t = "A" * 60 + "\u0007tail"
    push("quest", "Line\u0001one\ttwo")
    push("quest", long_t)
    Feed.step(st, t3 + 20000)
    c7 = vs(view())
    K.check(c7[1][0] == "Line one two" and len(c7[0][0]) == 48, "E3: control characters become spaces, a text is cut at 48 characters: %s" % [x[0] for x in c7])
    st.cards.clear()
    Feed.step(st, t3 + 40000)
    # ================================================================================== E4 the HUD markup + feedFill
    use_dir("e4")
    plugin.huds.clear()
    h, cm = hud(me)
    plugin.huds.put(u, h)
    mk = grp(cm, "SkyyWFeed") or ""
    ids_ = re.findall(r"#(SkyyWFeed\w*)", mk)
    K.check(mk.startswith("Group #SkyyWFeed { Anchor: (Bottom: 488, Left: 8, Width: 280, Height: 140); ") and all(
        ("Group #SkyyWFeed%d%s { Anchor: (Left: 0, Top: %d, Width: 280, Height: 32); Visible: false; " % (j, v, 108 - 36 * j)) in mk
        for j in range(4) for v in "FMLH") and mk.count("ItemIcon") == 0 and all(("#SkyyWFeed%dK%d " % (j, c)) in mk for j in range(4) for c in range(4))
            and "_" not in "".join(ids_) and len(ids_) == len(set(ids_)) and "Background: #0b1524(0.72); " in mk and "#E8A93B(0.30)" in mk
            and all(("#SkyyWFeed%d%sK%d " % (j, v, c)) in mk for j in range(4) for v in "ML" for c in range(4))
            and mk.count("#E8A93B(0.18)") == 16 and mk.count("#E8A93B(0.08)") == 16 and "#E8A93B(0.33)" in mk and "#d2b8ff(0.14)" in mk,
            "E4: the HUD carries the feed box at bl 8,488 (280 x 140), 4 fixed slots (newest at the bottom: Top 108 / 72 / 36 / 0), each F / M / "
            "L / H hidden, 4 chips per slot, no ItemIcon (Item icons Hide), unique ids without '_' (%d); FIX2: the 60 %% / 25 %% variants keep "
            "the 4 chips (0.33 / 0.14) and the hairline (0.18 / 0.08); markup %d chars" % (len(ids_), len(mk)))
    st = Feed.STATES.get(u)
    push("pickup", "Pumpkin", 1, "Plant_Crop_Pumpkin_Item")
    t4 = t3 + 60000
    Feed.step(st, t4)
    re_, c_ = ffill(h)
    s_ = sets(c_)
    K.check(not re_ and s_.get("#SkyyWFeed0FN.Text") == "Pumpkin" and s_.get("#SkyyWFeed0MN.Text") == "Pumpkin" and s_.get("#SkyyWFeed0FC.Text") == "x1"
            and s_.get("#SkyyWFeed0F.Visible") is True and s_.get("#SkyyWFeed0M.Visible") is False and s_.get("#SkyyWFeed0K0.Visible") is True
            and s_.get("#SkyyWFeed0MK0.Visible") is True and s_.get("#SkyyWFeed0LK0.Visible") is True and s_.get("#SkyyWFeed0LK1.Visible") is False
            and all(c[0] == "Set" for c in c_) and not any("#SkyyWFeed1" in (c[1] or "") for c in c_),
            "E4: a new card = only Sets on slot 0 (texts in F / M / L, count, chip, F visible) - no append, no re-send: %d sets" % len(c_))
    re_, c_ = ffill(h)
    K.check(not re_ and c_ == [], "E4: nothing changed -> feedFill sends nothing (%d)" % len(c_))
    push("pickup", "Pumpkin", 3, "Plant_Crop_Pumpkin_Item")
    Feed.step(st, t4 + 800)
    re_, c_ = ffill(h)
    s_ = sets(c_)
    K.check(s_.get("#SkyyWFeed0FC.Text") == "" and s_.get("#SkyyWFeed0HC.Text") == "x4" and s_.get("#SkyyWFeed0H.Visible") is True
            and "#SkyyWFeed0FN.Text" not in s_, "E4: a merge = the gold highlight (H shown, its count x4, the white count blanked), the text not re-sent: %s" % sorted(s_))
    Feed.step(st, t4 + 1200)
    s_ = sets(ffill(h)[1])
    Feed.step(st, t4 + 800 + 4400)
    s2_ = sets(ffill(h)[1])
    Feed.step(st, t4 + 800 + 4800)
    s3_ = sets(ffill(h)[1])
    Feed.step(st, t4 + 800 + 5000)
    s4_ = sets(ffill(h)[1])
    K.check(s_.get("#SkyyWFeed0H.Visible") is False and s_.get("#SkyyWFeed0FC.Text") == "x4"
            and s2_ == {"#SkyyWFeed0F.Visible": False, "#SkyyWFeed0M.Visible": True, "#SkyyWFeed0L.Visible": False, "#SkyyWFeed0H.Visible": False}
            and s3_.get("#SkyyWFeed0L.Visible") is True and s3_.get("#SkyyWFeed0M.Visible") is False and s4_.get("#SkyyWFeed0L.Visible") is False
            and all(k_.endswith(".Visible") for k_ in list(s2_) + list(s3_) + list(s4_)),
            "E4: the fade steps are .Visible sets only (60 %%: %s; 25 %%; gone)" % s2_)
    # a full build while a card shows = the same state in the new document
    push("coins", "+120 coins  Bank interest")
    Feed.step(st, t4 + 20000)
    cmb = rebuild(h)
    sb_ = sets(cmb)
    K.check(sb_.get("#SkyyWFeed0FN.Text") == "+120 coins  Bank interest" and sb_.get("#SkyyWFeed0F.Visible") is True and sb_.get("#SkyyWFeed0K1.Visible") is True
            and sb_.get("#SkyyWFeed0K0.Visible") is False and "#SkyyWFeed1F.Visible" not in sb_
            and sb_.get("#SkyyWFeed0MK1.Visible") is True and sb_.get("#SkyyWFeed0LK1.Visible") is True and sb_.get("#SkyyWFeed0MK0.Visible") is False,
            "E4: a full HUD build (any re-send) writes the shown card into the new document (gold chip for coins); empty slots stay as built")
    LS.get(u).get("Feed").opt = False
    cmi = rebuild(h)
    mki = grp(cmi, "SkyyWFeed") or ""
    push("pickup", "Pumpkin", 2, "Plant_Crop_Pumpkin_Item")
    Feed.step(st, t4 + 20100)
    si_ = sets(ffill(h)[1])
    K.check(mki.count("ItemIcon #SkyyWFeed") == 4 and 'ItemId: "Ingredient_Crystal_White"; Visible: false;' in mki
            and si_.get("#SkyyWFeed0I.ItemId") == "Plant_Crop_Pumpkin_Item" and si_.get("#SkyyWFeed0I.Visible") is True and si_.get("#SkyyWFeed1I.Visible") is False,
            "E4: Item icons Show -> an ItemIcon per slot; the card's item id is SET (.ItemId) and shown, a card without one hides it: %s"
            % dict((k_, v_) for k_, v_ in si_.items() if "I." in k_))
    LS.get(u).get("Feed").opt = True
    lf = LS.get(u).get("Feed")
    lf.anchor, lf.dx, lf.dy, lf.scale = "tl", 300, 50, 50
    mkt = grp(rebuild(h), "SkyyWFeed") or ""
    lf.anchor, lf.dx, lf.dy, lf.scale = "bl", 8, 488, 100
    lf.en = False
    cmo = rebuild(h)
    lf.en = True
    K.check(mkt.startswith("Group #SkyyWFeed { Anchor: (Top: 50, Left: 300, Width: 140, Height: 70); ") and "#SkyyWFeed0F { Anchor: (Left: 0, Top: 0, Width: 140, Height: 16)" in mkt
            and "#SkyyWFeed3F { Anchor: (Left: 0, Top: 54, Width: 140, Height: 16)" in mkt and grp(cmo, "SkyyWFeed") is None and not bool(h.feedOn),
            "E4: a top-anchored feed stacks downward (newest at the top), 50 %% = 140 x 70 with 16 px cards; Feed hidden = not in the HUD")
    ecm_b, ecm_e = UCB(), UEB()
    EP(me, plugin).build(None, ecm_b, ecm_e, None)
    ecm = cmds(ecm_b)
    pv = grp(ecm, "SkyyEPvFeed") or ""
    spb, spe = UCB(), UEB()
    SP(me, plugin, "Feed").build(None, spb, spe, None)
    spc = cmds(spb)
    sp_ev = [str(e.data) for e in spe.getEvents()]
    K.check("Width: 186, Height: 93" in pv and sets(ecm).get("#SkyyEPvFeedTxt.Text") == "Notification Feed"
            and any("Item icons" in (c[3] or "") for c in spc) and any('"optoff"' in d_ for d_ in sp_ev),
            "E4: the editor draws the feed as its 280 x 140 box at 2/3 ('Notification Feed'); its Settings page has the Item icons Show / Hide row")
    # ================================================================================== E5 the Skill XP flash
    use_dir("e5")
    plugin.huds.clear()
    Feed.STATES.clear()
    Feed.ACTIVE.clear()

    @JImplements("java.util.function.Function")
    class Lvl(object):
        @JOverride
        def apply(self, x):
            return Integer(1)
    bridge.put("skill:fn:level", Lvl())
    bridge.put("skill:" + str(u), "Mining:12,Foraging:3,Farming:5")
    bridge.put("skill:overall:" + str(u), Integer(7))
    h, cm = hud(me)
    plugin.huds.put(u, h)
    K.check(str(h.shape.get("Skills")) == "K1" and "SkyyWSkillsF0a" in (grp(cm, "SkyyWSkills") or "") and "SkyyWSkillsX0" in (grp(cm, "SkyyWSkills") or ""),
            "E5: no flash: the Skills widget (Overall Level only, no SkyyClasses) keeps shape K1; every row carries its hidden tints + gain label")
    K.check([str(Feed.fmtGain(JLong(x))) for x in (79, 999, 1240, 9999, 12400, 999949, 999950, 1234567)]
            == ["+79", "+999", "+1,240", "+9,999", "+12.4k", "+999.9k", "+1.0M", "+1.2M"], "E5: the gain formats +79 / +1,240 / +12.4k / +1.2M")
    t5 = t4 + 100000
    fxp.apply(arr(u, "Mining", Long(40)))
    st = Feed.STATES.get(u)
    Feed.step(st, t5)
    fxp.apply(arr(u, "Mining", Long(10)))
    Feed.step(st, t5 + 500)
    nb = int(view().fn.__len__())
    Feed.step(st, t5 + 1999)
    nb2 = int(view().fn.__len__())
    Feed.step(st, t5 + 2000)
    v5 = view()
    fl5 = [(str(v5.fn[i]), str(v5.fg[i]), int(v5.fst[i])) for i in range(len(v5.fn))]
    sl = LS.get(u).get("Skills")
    m5 = [None if x is None else str(x) for x in Wid.modelL("Skills", me, sl)]
    K.check(nb == 0 and nb2 == 0 and fl5 == [("Mining", "+50", 1)] and m5[0] == "K2+1" and m5[4] == "Mining" and m5[5] == "12" and m5[23] == "+50"
            and m5[32] == "1" and m5[22] is None,
            "E5: BATCH: 40 + 10 Mining XP within 2 s = ONE flash '+50' at 2 s; Mining's line is off -> a temporary row (shape K2+1, level 12): %s %s" % (fl5, m5[:6]))
    re_, c_ = ffill(h)
    K.check(re_, "E5: the temporary row = a Skills shape change -> feedFill asks for the 0.3.8 re-send")
    cm5 = rebuild(h)
    mk5 = grp(cm5, "SkyyWSkills") or ""
    s5 = sets(cm5)
    n1 = re.search(r"Label #SkyyWSkillsN1Txt \{[^}]*TextColor: (#[0-9a-f]{6})", mk5)
    x1 = re.search(r"Label #SkyyWSkillsX1Txt \{ Anchor: \(Left: (\d+), Top: (\d+), Width: (\d+)[^}]*TextColor: #39f493, HorizontalAlignment: End", mk5)
    wsk = int(re.search(r"Group #SkyyWSkills \{ Anchor: \([^)]*Width: (\d+)", mk5).group(1))
    K.check(n1 is not None and n1.group(1) == "#b7cedd" and x1 is not None and s5.get("#SkyyWSkillsX1Txt.Text") == "+50" and s5.get("#SkyyWSkillsF1a.Visible") is True
            and s5.get("#SkyyWSkillsE1.Visible") is True and "#SkyyWSkillsF0a.Visible" not in s5 and "Background: #E8A93B(0.30); Visible: false;" in mk5,
            "E5: re-built: the temporary Mining row in #b7cedd, its gain label (green, End) says +50, tint 30 %% + the gold edge shown (box %d wide)" % wsk)
    Feed.step(st, t5 + 2500)
    sa = sets(ffill(h)[1])
    Feed.step(st, t5 + 3750)
    sb2 = sets(ffill(h)[1])
    K.check(sa == {"#SkyyWSkillsF1a.Visible": False, "#SkyyWSkillsF1b.Visible": True, "#SkyyWSkillsE1.Visible": True}
            and sb2 == {"#SkyyWSkillsF1a.Visible": False, "#SkyyWSkillsF1b.Visible": False, "#SkyyWSkillsE1.Visible": False},
            "E5: the tint steps 30 %% -> 14 %% (0.5 s) -> none (1.75 s) are .Visible sets only; the +50 stays: %s / %s" % (sa, sb2))
    fxp.apply(arr(u, "Mining", Long(5)))
    Feed.step(st, t5 + 4000)
    Feed.step(st, t5 + 6000)
    v6 = view()
    s6 = sets(ffill(h)[1])
    K.check([(str(v6.fn[0]), str(v6.fg[0]), int(v6.fst[0]))] == [("Mining", "+55", 1)] and s6.get("#SkyyWSkillsX1Txt.Text") == "+55" and s6.get("#SkyyWSkillsF1a.Visible") is True,
            "E5: a new batch during the flash adds to it (+55) and restarts the 3 s (tint 30 %% again)")
    Feed.step(st, t5 + 9000)
    v7 = view()
    re7, c7_ = ffill(h)
    K.check(len(v7.fn) == 0 and re7 and str(Wid.modelL("Skills", me, sl)[0]) == "K1" and bool(Feed.idle(st)),
            "E5: 3 s after the last batch the flash ends: the temporary row leaves (shape K1 -> re-send), the player is idle")
    rebuild(h)
    sl.opt = False
    rH = fxp.apply(arr(u, "Mining", Long(7)))
    qH = int(st.qn.get())
    Feed.step(st, t5 + 20000)
    Feed.step(st, t5 + 22000)
    mh = str(Wid.modelL("Skills", me, sl)[0])
    K.check(not bool(rH) and qH == 0,
            "E5 (review 2 fix): 'XP of hidden skills Hide' + Mining's line off -> xpflash:fn:push answers FALSE (the sender sends chat), nothing queued: %s %d" % (rH, qH))
    # Feed.xpShows - executed for every branch (shown line / class line / temporary row / no room / no SkyySkills)
    xs = {}
    sl.lines = 3
    xs["off"] = bool(Feed.xpShows(u, "Mining"))
    sl.lines = 1 | 4
    xs["shown"] = bool(Feed.xpShows(u, " mining "))
    sl.lines = 3
    bridge.put("class:list", "Priest")
    bridge.put("class:skill:" + str(u), "Divinity")
    xs["cls"] = bool(Feed.xpShows(u, "Divinity"))
    xs["clsOther"] = bool(Feed.xpShows(u, "Mining"))
    sl.opt = True
    xs["tmp"] = bool(Feed.xpShows(u, "Zzzskill"))
    sl.lines = int(WL.LINES_ALL)
    xs["full"] = bool(Feed.xpShows(u, "Zzzskill"))
    xs["fullShown"] = bool(Feed.xpShows(u, "Exploration"))
    bridge.remove("class:list")
    bridge.remove("class:skill:" + str(u))
    sl.lines = 3
    bridge.remove("skill:fn:level")
    xs["noSkills"] = bool(Feed.xpShows(u, "Mining"))
    bridge.put("skill:fn:level", Lvl())
    K.check(xs == {"off": False, "shown": True, "cls": True, "clsOther": False, "tmp": True, "full": False, "fullShown": True, "noSkills": False},
            "E5 (review 2 fix): Feed.xpShows = a shown line (any case / spaces), the class line = the class skill, else a temporary row only with "
            "Show and a free row; all 10 rows shown -> no room; no SkyySkills -> nothing drawn: %s" % xs)
    Feed.step(st, t5 + 40000)
    sl.lines = 1 | 4                       # Overall Level + Mining shown
    cm8 = rebuild(h)
    w0 = int(re.search(r"Group #SkyyWSkills \{ Anchor: \([^)]*Width: (\d+)", grp(cm8, "SkyyWSkills")).group(1))
    fxp.apply(arr(u, "Mining", Long(1240)))
    Feed.step(st, t5 + 50000)
    Feed.step(st, t5 + 52000)
    re8, c8 = ffill(h)
    cm9 = rebuild(h)
    w1 = int(re.search(r"Group #SkyyWSkills \{ Anchor: \([^)]*Width: (\d+)", grp(cm9, "SkyyWSkills")).group(1))
    m9 = [None if x is None else str(x) for x in Wid.modelL("Skills", me, sl)]
    K.check(mh == "K1" and m9[0] == "K2" and m9[23] == "+1,240" and re8 and w1 > w0 and sets(cm9).get("#SkyyWSkillsX1Txt.Text") == "+1,240",
            "E5: 'XP of hidden skills Hide' = no temporary row (%s); a SHOWN Mining row flashes in place (shape K2), the box grows for the gain "
            "(%d -> %d px, re-send asked)" % (mh, w0, w1))
    sl.lines = 3
    spb, spe = UCB(), UEB()
    SP(me, plugin, "Skills").build(None, spb, spe, None)
    K.check(any("XP of hidden skills" in (c[3] or "") for c in cmds(spb)), "E5: the Skills Settings page has the 'XP of hidden skills Show / Hide' row")
    # ================================================================================== E6 msgroute + the settings registration + the kit rows
    Feed.STATES.clear()
    Feed.ACTIVE.clear()
    use_dir("e6")
    LS.get(u)
    plugin.huds.clear()
    plugin.huds.put(u, HM(me))
    r0 = dict((k_, str(froute.apply(arr(u, k_)))) for k_ in KINDS + ["system", "zzz", "Pick_up"])
    K.check(r0 == dict(list(DEFS.items()) + [("system", "chat"), ("zzz", "chat"), ("Pick_up", "chat")]),
            "E6: msgroute without SkyyMenu = the Server Setup defaults; system / unknown kinds = chat: %s" % r0)
    vals = {}

    @JImplements("java.util.function.Function")
    class Get(object):
        @JOverride
        def apply(self, x):
            v_ = vals.get(str(x[1]))
            return None if v_ is None else Boolean(v_)
    bridge.put("settings:fn:get", Get())
    vals.update({"msg.pickup": False, "msg.coins": True, "msg.coins.feed": False, "msg.levelup": True, "msg.levelup.feed": True, "msg.heal": True})
    r1 = dict((k_, str(froute.apply(arr(u, k_)))) for k_ in ("pickup", "coins", "levelup", "heal", "quest"))
    LS.get(u).get("Feed").en = False
    r2 = (str(froute.apply(arr(u, "levelup"))), str(froute.apply(arr(u, "skillxp"))))
    LS.get(u).get("Feed").en = True
    LS.get(u).get("Skills").en = False
    r3 = str(froute.apply(arr(u, "skillxp")))
    LS.get(u).get("Skills").en = True
    FCfg.ENABLED = False
    r4 = (str(froute.apply(arr(u, "heal"))), str(froute.apply(arr(u, "skillxp"))))
    FCfg.ENABLED = True
    calls_before = [0]

    @JImplements("java.util.function.Function")
    class GetCount(object):
        @JOverride
        def apply(self, x):
            calls_before[0] += 1
            return Boolean(True)
    bridge.put("settings:fn:get", GetCount())
    u_off = UUID.randomUUID()
    rOff = dict((k_, str(froute.apply(arr(u_off, k_)))) for k_ in ("pickup", "levelup", "skillxp"))
    FCfg.R_QUEST = "off"
    rOff["quest"] = str(froute.apply(arr(str(u_off), "quest")))
    FCfg.R_QUEST = "feed"
    rOn = str(froute.apply(arr(u, "pickup")))
    K.check(rOff == {"pickup": "chat", "levelup": "chat", "skillxp": "chat", "quest": "off"} and calls_before[0] == 2 and rOn == "feed",
            "E6 (review 2 fix): a player with NO HUD (offline) = the Server Setup default with feed -> chat, and settings:fn:get is NOT asked "
            "(no disk read on the caller's thread); a HUD player still asks it (2 calls): %s calls=%d" % (rOff, calls_before[0]))
    bridge.remove("settings:fn:get")
    FCfg.R_QUEST = "off"
    r5 = str(froute.apply(arr(str(u), "quest")))
    FCfg.R_QUEST = "feed"
    K.check(r1 == {"pickup": "off", "coins": "chat", "levelup": "feed", "heal": "feed", "quest": "feed"} and r2 == ("chat", "feed") and r3 == "chat"
            and r4 == ("chat", "feed") and r5 == "off" and str(froute.apply("bad")) == "chat",
            "E6: the player's switches win (off / chat / feed; no feed choice = the server's); Feed widget off -> chat (skillxp still the skill "
            "list); Skills widget off -> skillxp chat; the feed off in Server Setup -> chat; a server default 'off' -> off: %s %s %s %s %s" % (r1, r2, r3, r4, r5))
    regs = []

    @JImplements("java.util.function.Function")
    class Reg(object):
        @JOverride
        def apply(self, x):
            regs.append([None if y is None else (bool(y) if isinstance(y, (bool,)) or str(type(y)).find("Boolean") >= 0 else str(y)) for y in x])
            return Boolean(True)
    bridge.put("settings:fn:register", Reg())
    FCfg.registerAll()
    rk = dict((r_[1], r_) for r_ in regs)
    defs_ok = all(rk.get("msg." + k_) and rk["msg." + k_][4] == (d_ != "off") and rk["msg." + k_ + ".feed"][4] == (d_ == "feed") for k_, d_ in DEFS.items())
    K.check(len(regs) == 20 and defs_ok and all(r_[0] == "SkyyHud" and r_[3] == "messages" and r_[6] == "skyyhud.messages" and len(r_[2]) <= 48 and len(r_[5]) <= 100 for r_ in regs)
            and all(bridge.containsKey("settings:def:msg." + k_) and bridge.containsKey("settings:def:msg." + k_ + ".feed") for k_ in KINDS),
            "E6: 20 switches registered (msg.<kind> + msg.<kind>.feed, category messages, node skyyhud.messages, defaults = the Server Setup "
            "rows), settings:def:* written for load order: %s" % [r_[1] for r_ in regs[:4]])
    # the REAL config kit rows (Server Setup -> Feed / Messages)
    kmods = os.path.join(work, "k", "mods")
    os.makedirs(os.path.join(kmods, "Skyy_SkyyHud"))
    kf = os.path.join(kmods, "Skyy_SkyyHud", "config.properties")
    open(kf, "w", encoding="latin-1").write("# a 0.3.19 file\ndefaultLayout=\nmm.maxRadius=224\n")
    Cfg.FILE = Paths.get(kf)
    Cfg.load()
    loaded = (bool(FCfg.ENABLED), float(FCfg.SHOW_SECS), float(FCfg.MERGE_SECS), int(FCfg.MAX_CARDS), float(FCfg.XP_BATCH_SECS), float(FCfg.XP_FLASH_SECS),
              str(FCfg.R_PICKUP), str(FCfg.R_LEVELUP))
    Pub, Fn = H("CfgPub"), H("CfgFn")
    Pub.start(Paths.get(kmods), None)
    regs.clear()
    kres = []
    for key_, val_, ok_ in (("hud.feed.showSecs", "6", True), ("hud.feed.showSecs", "0.5", False), ("hud.feed.maxCards", "9", False),
                            ("hud.feed.maxCards", "3", True), ("hud.msg.levelup", "feed", True), ("hud.msg.levelup", "loud", False),
                            ("hud.msg.skillxp", "Skill list", True), ("hud.feed.enabled", "false", True)):
        try:
            r_ = Fn.set(key_, val_, None, "Console", "yes", "console")
            got = str(r_[0]) if r_ is not None else None
        except Exception as ex:
            got = "threw %s" % ex
        kres.append((key_, val_, got))
        K.check((got == "ok") == ok_, "E6: the kit %s %s = %s (%s)" % ("takes" if ok_ else "refuses", key_, val_, got))
    lv = [r_ for r_ in regs if r_[1] == "msg.levelup.feed"]
    K.check(float(FCfg.SHOW_SECS) == 6.0 and int(FCfg.MAX_CARDS) == 3 and str(FCfg.R_LEVELUP) == "feed" and str(FCfg.R_SKILLXP) == "feed"
            and not bool(FCfg.ENABLED) and lv and lv[-1][4] is True,
            "E6: the rows write the live fields (6 s, 3 cards, level-ups -> feed, the feed off) and a Messages change re-registers the "
            "players' defaults at once (msg.levelup.feed default now %s)" % (lv[-1][4] if lv else None))
    Pub.flush()
    ktext = open(kf, encoding="latin-1").read()
    K.check(loaded == (True, 4.0, 3.0, 4, 2.0, 3.0, "feed", "chat") and "feed.showSecs=6" in ktext and "msg.levelup=feed" in ktext
            and "mm.maxRadius=224" in ktext, "E6: a 0.3.19 config.properties (no feed keys) loads the defaults %s; the kit writes feed.showSecs=6 / "
            "msg.levelup=feed and keeps the old lines" % (loaded,))
    Cfg.FILE = Paths.get(os.path.join(cfgdir, "config.properties"))
    Cfg.load()
    bridge.remove("settings:fn:register")
    # ================================================================================== E7 /skyyhud testfeed (Feed.test)
    use_dir("e7")
    Feed.STATES.clear()
    Feed.ACTIVE.clear()
    plugin.huds.clear()
    h, cm = hud(me)
    plugin.huds.put(u, h)
    HT.EXEC = None
    HT.start()
    summ = str(Feed.test(me))
    st = Feed.STATES.get(u)
    Feed.step(st, System.currentTimeMillis())
    va = vs(view())
    time.sleep(2.6)
    Feed.step(st, System.currentTimeMillis())
    vb = vs(view())
    Feed.step(st, System.currentTimeMillis() + 2000)
    vx = view()
    HT.stop()
    ov7 = [str(x) for x in st.over]
    K.check(ov7 == ["+8 HP  Priest heal", "+120 coins  Bank interest"] and "come into chat instead" in summ,
            "FIX1: testfeed's 2 cards that never fit are chat lines (the summary says so): %s" % ov7)
    st.over.clear()
    K.check("feed 6, chat 0, off 0" in summ and "skill list 2" in summ and [x[0] for x in va] == ["Pumpkin", "Double drop!  Oak Log", "Chop logs  7/10", "Wolf  +35 Pet XP"]
            and vb[0][0] == "Pumpkin" and vb[0][1] == "x9" and sorted(str(x) for x in vx.fn) == ["Foraging", "Mining"]
            and sorted(str(x) for x in vx.fg) == ["+40", "+79"],
            "E7: /skyyhud testfeed: 6 cards routed to the feed (the 2 oldest pushed out), Pumpkin x1 -> x9 by the two delayed pushes on "
            "SkyyHud's thread, Skill XP Foraging (no class) +79 + Mining +40 flash after the batch: %s" % summ[:90])
    # ================================================================================== E8 the timer
    FT = H("FeedTick")
    Feed.STATES.clear()
    Feed.ACTIVE.clear()
    t8 = int(Feed.TICKS.get())
    FT(plugin).run()
    idle_ok = int(Feed.TICKS.get()) == t8
    ups = []

    @JImplements("java.util.function.Consumer")
    class Nop(object):
        @JOverride
        def accept(self, x):
            pass
    push("pickup", "Pumpkin", 1)
    act1 = Feed.ACTIVE.containsKey(u)
    FT(plugin).run()                          # feedTick -> update() needs a real player: caught inside, the step + view still happen
    v8 = view()
    st = Feed.STATES.get(u)
    for c_ in list(st.cards):
        c_.changed = c_.changed - 6000
    FT(plugin).run()
    K.check(idle_ok and act1 and int(v8.n) == 1 and not Feed.ACTIVE.containsKey(u) and int(Feed.TICKS.get()) == t8 + 2,
            "E8: FeedTick with nobody active does nothing; a push makes the player ACTIVE, the tick steps + shows it, and once the card is "
            "gone the player leaves ACTIVE")
    plugin.huds.clear()
    push_nohud = bool(fpush.apply(arr(u, "pickup", None, "Pumpkin", None)))
    Feed.ACTIVE.put(u, st)
    FT(plugin).run()
    K.check(not push_nohud and not Feed.ACTIVE.containsKey(u) and not Feed.STATES.containsKey(u),
            "E8: a player who left (no HUD) is refused and dropped from ACTIVE / STATES at the next tick")
    # ================================================================================== E9 bytecode facts
    G = PWK.calls(jar)
    chk = lambda m_, c_: c_ in G.get(m_, set())
    eng = lambda m_: sorted(c for c in G.get(m_, set()) if c.startswith("com.hypixel"))
    K.check(chk("SkyyHudPlugin.setup", "com.skyy.hud.FeedTick.<init>") and chk("SkyyHudPlugin.setup", "com.skyy.hud.HudThreads.start")
            and not any("SCHEDULED_EXECUTOR" in c for c in G.get("SkyyHudPlugin.setup", set())) and chk("FeedTick.run", "com.skyy.hud.Feed.tickAll")
            and chk("Feed.tickAll", "com.skyy.hud.HudMain.feedTick") and chk("SkyyHudPlugin.shutdown", "com.skyy.hud.HudThreads.stop")
            and chk("Feed.tickAll", "com.skyy.hud.Feed.flushOver") and chk("Feed.addCard", "com.skyy.hud.Feed.iconOk")
            and chk("Feed.addCard", "com.skyy.hud.Feed.overflow") and chk("Feed.addXp", "com.skyy.hud.Feed.overflow"),
            "E9: bytecode: the feed timer = FeedTick on HudThreads (SkyyHud's thread), never the engine scheduler; FeedTick -> Feed.tickAll -> "
            "HudMain.feedTick; shutdown stops the thread; FIX1 / FIX3 wiring: tickAll -> flushOver, addCard -> iconOk + overflow, addXp -> overflow")
    K.check(any(c.endswith("PlayerRef.sendMessage") for c in G.get("Feed.flushOver", set()))
            and all(c.endswith("Item.getAssetMap") or c.endswith("AssetMap.getAsset") for c in eng("Feed.iconOk")) and eng("Feed.iconOk")
            and not eng("Feed.overflow"),
            "FIX1 / FIX3: flushOver sends with PlayerRef.sendMessage; iconOk reads ONLY the item asset map (no world / store / entity): %s"
            % eng("Feed.iconOk"))
    K.check(all(not eng(m_) for m_ in ("Feed.push", "Feed.xpPush", "Feed.xpShows", "Feed.route", "Feed.offer", "Feed.widgetOn", "Feed.step", "Feed.addCard",
                                         "Feed.makeView", "FeedPushFn.apply", "XpFlashFn.apply", "MsgRouteFn.apply", "FeedCfg.register")),
            "E9: the bridge paths (push / xpPush / route / offer / widgetOn) and the step call NO engine class (no world, store or entity): %s"
            % dict((m_, eng(m_)) for m_ in ("Feed.push", "Feed.route", "Feed.step") if eng(m_)))
    K.check(any(c.endswith(".requirePermission") for c in G.get("HudTestFeedCmd.<init>", set()))
            and any(c.endswith(".setPermissionGroups") for c in G.get("HudTestFeedCmd.<init>", set()))
            and chk("HudCmd.<init>", "com.skyy.hud.HudTestFeedCmd.<init>"),
            "E9: /skyyhud testfeed: requirePermission + setPermissionGroups(new String[0]) under the Adventurer /skyyhud")
    # ================================================================================== E10 the saved layout file vs 0.3.19 (same widgets)
    URL, URLCL, File = JClass("java.net.URL"), JClass("java.net.URLClassLoader"), JClass("java.io.File")
    ua = JArray(URL)(2)                  # the 0.3.19 jar + its own copy of the server classes (the system loader holds the 0.3.20 jar)
    ua[0] = File(OLD_JAR).toURI().toURL()
    ua[1] = File(B.SERVER_JAR).toURI().toURL()
    old_ld = URLCL(ua, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    LSo = JClass(PKG + "LayoutStore", loader=old_ld)
    K.check(LSo.class_ != LS.class_, "E10: the 0.3.19 LayoutStore is its own class (its own loader)")
    d10 = os.path.join(work, "e10")
    LS.DIR = Paths.get(os.path.join(d10, "new"))
    LSo.DIR = Paths.get(os.path.join(d10, "old"))
    LS.CACHE.clear()
    HT.EXEC = None
    u10 = uid(77)
    for L_ in (LS, LSo):
        m_ = L_.get(u10)
        m_.get("Gclock").dx = 77
        m_.get("Coins").en = False
        L_.save(u10)

    def body(p_):
        return sorted(ln.strip() for ln in open(p_, encoding="latin-1") if ln.strip() and not ln.startswith("#"))
    bn, bo = body(os.path.join(d10, "new", str(u10) + ".properties")), body(os.path.join(d10, "old", str(u10) + ".properties"))
    want_add = sorted(["Feed=1,bl,8,488,100,1", "Party=1,tl,8,200,100,1", "Guild=1,tl,8,324,100,1", "Skills=1,tr,8,240,100,1", "Abilities=1,br,460,21,100,1"])
    K.check(sorted(set(bn) - set(bo)) == want_add and sorted(set(bo) - set(bn)) == sorted(["Party=1,tl,8,320,100,1", "Guild=1,tl,8,444,100,1",
            "Skills=1,tl,8,544,100,1", "Abilities=1,tl,8,760,100,1"]) and "Gclock=1,bl,77,40,100,1" in bn and "Coins=0,br,8,8,100,1" in bn,
            "E10: a NEW player's saved file vs 0.3.19's = the same lines but the Feed line and the 4 moved built-in spots (what the 0.3.19 "
            "harness X1 byte-compares against 0.3.18): +%s -%s" % (sorted(set(bn) - set(bo)), sorted(set(bo) - set(bn))))
    K.save()


def run_x19(out, jar, scratch, home):
    T19 = load_module(os.path.join(HERE, "test_skyyhud_0.3.19.py"), "hud0319h")
    T19.run_exec(out, jar, os.path.join(scratch, "x19"), home)
    # X1's last condition byte-compares a fresh player's saved file with 0.3.18's: it differs ONLY by the new Feed line + the 4 moved
    # built-in spots, which E10 checks exactly; the rest of X1 (the thread, the write count, no .tmp) is in its own message
    d = json.load(open(out))
    keep, eased = [], []
    for f in d["fails"]:
        if f.startswith("X1: HudThreads: no thread -> inline save") and "('SkyyHud-Tick', True)" in f and "(writes 1)" in f:
            eased.append(f[:60])
        else:
            keep.append(f)
    d["fails"] = keep
    d["ok"] += len(eased)
    d.setdefault("notes", []).append("X19: X1's byte compare with 0.3.18 differs by the Feed line + the moved defaults only (checked in E10): %d eased" % len(eased))
    json.dump(d, open(out, "w"), indent=1)


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    LS, Cfg, Pub, Wid, FCfg = P("LayoutStore"), P("HudCfg"), P("CfgPub"), P("Widgets"), P("FeedCfg")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    mods = os.path.dirname(home)
    lyd = os.path.join(home, "layouts")
    players = [f[:-11] for f in sorted(os.listdir(lyd)) if f.endswith(".properties")] if os.path.isdir(lyd) else []
    res = []
    for _n in range(2):
        b0 = HK.tree_hash(mods)
        LS.CACHE.clear()
        LS.DIR = Paths.get(lyd)
        Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
        Wid.HUBFILE = Paths.get(os.path.join(mods, "Skyy_SkyyIslands", "hub.properties"))
        Cfg.load()
        Pub.start(Paths.get(mods), None)
        r_ = {"feed": (bool(FCfg.ENABLED), float(FCfg.SHOW_SECS), int(FCfg.MAX_CARDS), str(FCfg.R_PICKUP), str(FCfg.R_LEVELUP))}
        for us in players:
            mp = LS.get(UUID.fromString(us))
            r_[us] = dict((str(w_), str(mp.get(w_).ser())) for w_ in Wid.IDS)
        Pub.flush()
        a0 = HK.tree_hash(mods)
        res.append((r_, sorted(k for k in set(b0) | set(a0) if b0.get(k) != a0.get(k))))
    K.check(res[0][1] == [] and res[1][1] == [] and res[0][0] == res[1][0],
            "ST: two starts on a COPY of the live Skyy_SkyyHud (%d layouts): nothing written, the same layouts: %s" % (len(players), [r[1] for r in res]))
    K.check(res[0][0]["feed"] == (True, 4.0, 4, "feed", "chat"), "ST: the live config.properties has no feed keys yet -> the defaults %s" % (res[0][0]["feed"],))
    bad = []
    for us in players:
        fl = {}
        for ln in open(os.path.join(lyd, us + ".properties"), encoding="latin-1"):
            if "=" in ln and not ln.startswith("#"):
                k_, v_ = ln.strip().split("=", 1)
                fl[k_] = v_
        r_ = res[0][0][us]
        if not all(r_[w_] == fl[w_] for w_ in r_ if w_ in fl):
            bad.append(us[:8])
        K.notes.append("ST: player %s...: feed at %s (saved Feed line: %s)" % (us[:8], r_["Feed"], "Feed" in fl))
    K.check(not bad, "ST: every saved line of every live layout loads exactly as saved (%d players): %s" % (len(players), bad))
    K.save()


def mkload(out_dir, jar):
    """Compile the two Java helpers of E2 (pure Java threads: the load is not serialised by Python's GIL)."""
    from jpype import JClass
    HK.jvm([B.JAVASSIST, B.SERVER_JAR, jar], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(jar)
    CF, CM, CC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    pl = cp.makeClass("skyyhud320.PushLoad")
    pl.addInterface(cp.get("java.lang.Runnable"))
    for f in ("public static java.util.concurrent.atomic.AtomicLong OK = new java.util.concurrent.atomic.AtomicLong();",
              "public static java.util.concurrent.atomic.AtomicLong NO = new java.util.concurrent.atomic.AtomicLong();",
              "public java.util.function.Function f;", "public Object u;", "public int n;"):
        pl.addField(CF.make(f, pl))
    pl.addConstructor(CC.make("public PushLoad(java.util.function.Function f, Object u, int n) { this.f = f; this.u = u; this.n = n; }", pl))
    pl.addMethod(CM.make("""public void run() {
  for (int i = 0; i < this.n; i++) {
    Object r = this.f.apply(new Object[] { this.u, "pickup", null, "Pumpkin", Long.valueOf(1L) });
    if (Boolean.TRUE.equals(r)) OK.incrementAndGet(); else NO.incrementAndGet();
  }
}""", pl))
    pl.writeFile(out_dir)
    dr = cp.makeClass("skyyhud320.Drain")
    dr.addInterface(cp.get("java.lang.Runnable"))
    for f in ("public volatile boolean stop;", "public com.skyy.hud.FeedState s;", "public volatile int steps;"):
        dr.addField(CF.make(f, dr))
    dr.addConstructor(CC.make("public Drain(com.skyy.hud.FeedState s) { this.s = s; this.stop = false; this.steps = 0; }", dr))
    dr.addMethod(CM.make("""public void run() {
  while (!this.stop) {
    com.skyy.hud.Feed.step(this.s, System.currentTimeMillis());
    this.steps = this.steps + 1;
    Thread.yield();
  }
}""", dr))
    dr.writeFile(out_dir)


# section C: exactly these classes / members differ (beyond the 11 added classes) - filled in from the first compare run
EXPECT.update({
    "Widgets": ["+f FCHIP", "+f FCHIPL", "+f FCHIPM", "+m feedChips", "+m feedFit", "+m feedHair", "+m feedLabel", "+m feedPlace", "+m feedSrc", "+m fitText", "+m skillsModelX",
                "~<clinit>", "~m def", "~m innerW", "~m label", "~m linePairs", "~m modelL", "~m skillsBody", "~m text", "~m viewW"],
    "LayoutStore": ["~m get"],
    "HudCfg": ["~m load", "~m writeDefaults"], "CfgFile": ["~<clinit>"],
    "HudMain": ["+f feedBold", "+f feedIcons", "+f feedOn", "+f feedSc", "+f flashSeen", "+m feedFill", "+m feedTick", "~m build"],
    "SkyyHudPlugin": ["+f feedTicker", "~m setup", "~m shutdown", "~m tickAll"],
    "HudCmd": ["~c "],
    "EditorPage": ["~m prepView"],
    "SettingsPage": ["~m build"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],
})

if __name__ == "__main__":
    if "--mkload" in sys.argv:
        mkload(HK.arg("--mkload"), JAR)
        sys.exit(0)
    HK.run("SkyyHud", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("exec", run_exec), ("x19", run_x19), ("live", run_live)],
           os.path.abspath(__file__), live=(LIVE_DIR, "Skyy_SkyyHud"))
