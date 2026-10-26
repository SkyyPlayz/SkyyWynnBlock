"""Harness for SkyySacks 0.8.31 (auto-compact fix, round compfix - tools/sacks_0_8_31_patch.py).
Build first:
    python tools/sacks_0_8_31_patch.py && python SkyySacks/build_skyysacks_0.8.31.py

    python SkyySacks/test_skyysacks_0.8.31.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.30 -> 0.8.31 (only the classes the patch touches + the new SackBeat)
  0.8.30's phases re-run on the 0.8.31 jar: cmp30 (buy / compact / craft-opens / unpack / page / fixers), sweephook, rbw + rbr (the reader
        is the 0.8.30 jar now = the rollback), live + live2 (start twice on a live copy). (live30 is left out: it checked that nobody had
        bought the upgrade yet - Skyy has now.)
  CMP31 on the 0.8.9 Void stand-ins: the vanilla pair (Essence of Life -> Greater Essence of Life) locked below Life Essence I, compacted
        from I on, values conserved; crops compact; a recipe unlocked MID-SESSION compacts on the very next run (no relog) and changes the
        sweep signature (coll:recipes, and coll:<uuid> for a tier-up); the page names the unlocked items + the next unlock (coll:fn:where);
        a selected item says unlocked / locked; Turn on / Pay compact at once (runNow); the pd.compact.recheck clock; the SackBeat watchdog
  TICK  bytecode: the plugin schedules SackTick on SackPool.WRITER (not the shared scheduler); SackTick.run calls SackBeat.check +
        recheckDue; SweepTask.run still items -> VoidCompact.run -> sigOf
  LIVE31 on a scratch COPY of NewBetaTest's Skyy_SkyySacks (+ SkyyCollections, read for the unlocks): the player's p3 profile with its
        bought bags: Essence of Life -> Greater Essence of Life (Skyy's 4,955 + 73 -> 55 + 122 when the copy still holds those numbers),
        every unlocked crop compacts, every pair's value conserved, nothing locked moves
Exit code 1 on any failure.
"""
import os, sys, json, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyench as EN

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_30", os.path.join(HERE, "test_skyysacks_0.8.30.py"))
T30 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T30)
sys.argv = _argv
HK.run_compare = _RC
T089 = T30.T089

VERSION = "0.8.31"
OLD_VERSION = "0.8.30"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
T30.OLD_JAR = OLD_JAR          # the rollback reader (run_rbr) = 0.8.30 now
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "compfix", "h")))
PKG = "com.skyy.sacks."
BETA = T30.BETA
COLL_LIVE = os.path.join(os.path.dirname(BETA), "Skyy_SkyyCollections") if BETA else None
EXPECT = {"SkyySacksPlugin": ["~m setup", "~m shutdown"],
          "SackCfg": ["+f CMP_RECHECK", "~m pdKeys", "~m pdSig", "~m reload", "~<clinit>"],
          "CfgRows": ["~<clinit>", "~m header"], "CfgFile": ["~<clinit>"], "CfgFn": ["~m opExport"],
          "VoidCompact": ["+f VBASE", "+f VENCH", "+f VCOLL", "+f VTIER", "~<clinit>", "~m pairsIn", "~m run",
                          "+m vtier", "+m np", "+m baseAt", "+m enchAt", "+m unl", "+m pairOf", "+m pairsU", "+m roman", "+m nm", "+m why",
                          "+m whyText", "+m names", "+m stateOf", "+m runNow"],
          "SacksPage": ["~m compactBox", "~m render", "~m onEvent"],
          "SweepTask": ["~m sigOf"], "SackTick": ["~m run"],
          # RecipeCmp: its /craft tier sort table is re-baked from the committed tools/tier_tags.py (newer than the 0.8.30 build - sort only)
          "RecipeCmp": ["~<clinit>"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
LE, LEC = "Ingredient_Life_Essence", "Ingredient_Life_Essence_Concentrated"
WHEAT, CARROT, LETTUCE, PUMPKIN, TOMATO = ("Plant_Crop_Wheat_Item", "Plant_Crop_Carrot_Item", "Plant_Crop_Lettuce_Item",
                                           "Plant_Crop_Pumpkin_Item", "Plant_Crop_Tomato_Item")
EW, EC, EL, EP = "Skyy_Ench_Wheat", "Skyy_Ench_Carrot", "Skyy_Ench_Lettuce", "Skyy_Ench_Pumpkin"
RS = "_Recipe_Generated_0"


def coll_stub(jp, anchor):
    """a SkyyCollections stand-in: coll:fn:tier / where / count answer from one static map ("<kind>:<arg 1>" -> value)"""
    from jpype import JClass
    CtF, CtM, CtC = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    c = jp.makeClass(PKG + "SkyyTestColl31")
    c.addInterface(jp.get("java.util.function.Function"))
    c.addField(CtF.make("public static final java.util.HashMap R = new java.util.HashMap();", c))
    c.addField(CtF.make("public String kind;", c))
    c.addConstructor(CtC.make("public SkyyTestColl31(String k) { this.kind = k; }", c))
    c.addMethod(CtM.make("""public Object apply(Object o) {
  Object[] a = (Object[]) o;
  return R.get(kind + ":" + String.valueOf(a[1]));
}""", c))
    return JClass(c.toClass(anchor))


def cases31(K, L, scratch):
    from jpype import JClass, JString, JLong, JInt
    VS, Defs, Cfg, Pool, SPage = L["VS"], L["Defs"], L["Cfg"], L["Pool"], L["SPage"]
    fresh, write_pool, player, pc, custom_item, drain = (L[n] for n in ("fresh", "write_pool", "player", "pc", "custom_item", "drain"))
    UUID, us, jfield, pref, bridge = L["UUID"], L["us"], L["jfield"], L["pref"], L["bridge"]
    VC, Beat, Swp = JClass(PKG + "VoidCompact"), JClass(PKG + "SackBeat"), JClass(PKG + "SweepTask")
    for i_ in (LE, LEC, WHEAT, CARROT, LETTUCE, PUMPKIN, TOMATO, EW, EC, EL, EP):
        custom_item(i_, 100)
    drain()
    TC = T30.coins_fixture(L)
    CS = coll_stub(L["jp"], JClass(PKG + "SackBridge").class_)
    for kd in ("tier", "where", "count"):
        bridge.put(JString("coll:fn:" + kd), CS(JString(kd)))
    CATS = [str(c) for c in Defs.CATS]
    FA = CATS.index("Farming")
    base = os.path.join(scratch, "cmp31")
    U = UUID.fromString("00000000-0000-0000-0000-0000000c0831")
    k = str(U)

    def recipes(ids):
        bridge.put(JString("coll:recipes:" + k), JString(",".join(i + RS for i in ids)))

    def tier(n):
        CS.R.put(JString("tier:LifeEssence"), JInt(n))
        CS.R.put(JString("count:LifeEssence"), JLong(5435 if n > 0 else 0))

    def val(d, b, e):
        return d.get(b, 0) + 100 * d.get(e, 0)

    # ---- the pair table
    K.check([str(x) for x in VC.VBASE] == [LE] and [str(x) for x in VC.VENCH] == [LEC] and [str(x) for x in VC.VCOLL] == ["LifeEssence"]
            and int(VC.VTIER) == 1 and int(VC.np()) == 111 and len(VC.BASE) == 110 and int(VC.pairOf(JString(LE))) == 110
            and str(Defs.homeOf(JString(LE))) == "Farming" and str(Defs.homeOf(JString(LEC))) == "Farming",
            "VP the vanilla pair: Essence of Life -> Greater Essence of Life (both Farming), unlocked at Life Essence I; 110 Enchanted rows kept")
    K.eq(int(VC.pairsIn(FA, None)), 26, "VP the Farming bag: 25 Enchanted crops / meats + Essence of Life = 26 pairs")

    # ---- compaction (Skyy's Farming bag)
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {LE: 4955, LEC: 73, WHEAT: 537, EW: 3, CARROT: 1658, LETTUCE: 566, PUMPKIN: 250})
    s = VS.st(k)
    s.first = 1
    recipes([EW, EC, EL, "Skyy_Ench_Potato"])
    tier(0)
    TC.BAL = 100000
    r_ = str(VC.buy(U, k, FA))
    caps = VS.capsK(U, k)
    v0 = pc(k)
    made = int(VC.run(U, k, caps))
    a = pc(k)
    K.check(r_.startswith("+Farming now has Auto-compact") and made == 5 + 16 + 5 and a.get(WHEAT) == 37 and a.get(EW) == 8
            and a.get(CARROT) == 58 and a.get(EC) == 16 and a.get(LETTUCE) == 66 and a.get(EL) == 5
            and a.get(LE) == 4955 and a.get(LEC) == 73 and a.get(PUMPKIN) == 250,
            "CMP31 Farming bought, crops unlocked: Wheat 537 -> 5 (+37 loose), Carrot 1,658 -> 16 (+58), Lettuce 566 -> 5 (+66); Essence "
            "of Life stays (Life Essence below tier I), Pumpkin stays (locked): %s" % a)
    tier(9)
    made = int(VC.run(U, k, caps))
    a = pc(k)
    K.check(made == 49 and a.get(LE) == 55 and a.get(LEC) == 73 + 49,
            "CMP31 Life Essence I+: 4,955 Essence of Life -> 49 Greater Essence of Life + 55 loose (73 -> 122): %s" % a)
    K.check(all(val(a, b, e) == val(v0, b, e) for b, e in ((LE, LEC), (WHEAT, EW), (CARROT, EC), (LETTUCE, EL), (PUMPKIN, EP))),
            "CMP31 every value conserved (base + 100 x compacted)")
    # mid-session unlock: no relog, no restart - the very next run compacts it, and the sweep signature changed so the 2 s tick comes
    sig0 = str(Swp.sigOf(U))
    recipes([EW, EC, EL, "Skyy_Ench_Potato", EP])
    sig1 = str(Swp.sigOf(U))
    made = int(VC.run(U, k, caps))
    a = pc(k)
    K.check(sig0 != sig1 and made == 2 and a.get(PUMPKIN) == 50 and a.get(EP) == 2,
            "CMP31 Pumpkin unlocked MID-SESSION: the sweep signature changes and the next run makes 2 Enchanted Pumpkin (+50): %s" % a)
    bridge.put(JString("coll:" + k), JString("tiers=10,found=5,maxed=0,recipes=5,score=10"))
    sig2 = str(Swp.sigOf(U))
    bridge.put(JString("coll:" + k), JString("tiers=11,found=5,maxed=0,recipes=5,score=11"))
    Swp.EVENTS_OK = True   # the event system "registered" (else every player is due every tick)
    Swp.INVDIRTY.remove(U)
    Swp.LASTSWEEP.put(U, JLong(JClass("java.lang.System").nanoTime()))
    Swp.SIG.put(U, JString(sig2))
    K.check(sig2 != str(Swp.sigOf(U)) and bool(Swp.needs(U, JString(str(Swp.sigOf(U))))) and not bool(Swp.needs(U, JString(sig2))),
            "CMP31 a collection tier-up with no recipe change (coll:<uuid> summary) changes the signature -> the 2 s tick sweeps")
    Swp.SIG.remove(U)
    Swp.EVENTS_OK = False
    Pool.add(k, LE, JLong(45))
    K.eq(int(VC.run(U, k, caps)), 1, "CMP31 45 more Essence of Life (55 + 45 = 100) -> 1 more Greater Essence of Life at once")
    Cfg.CMP_ON = False
    Pool.add(k, LE, JLong(300))
    K.eq(int(VC.run(U, k, caps)), 0, "CMP31 Server Setup pd.compact.on=false: the vanilla pair stops too")
    Cfg.CMP_ON = True
    VC.toggle(U, k, FA)
    K.check(bool(VC.paused(k, FA)) and int(VC.run(U, k, caps)) == 0 and pc(k).get(LE) == 300, "CMP31 Farming paused: 300 Essence of Life stay loose")
    VC.toggle(U, k, FA)
    K.eq(int(VC.runNow(U, k)), 3, "CMP31 runNow (what a Turn on / Pay click calls): the 300 -> 3 at once")

    # ---- the page texts
    CS.R.put(JString("where:" + "Skyy_Ench_Tomato" + RS), JString("Tomato|Tomato|1|15|3"))
    CS.R.put(JString("where:" + "Skyy_Ench_Cauliflower" + RS), JString("Cauliflower|Cauliflower|1|15|0"))
    t2 = str(VC.names(U, FA, JClass(PKG + "KnowSync").collShared(U), 60))
    t2w = str(VC.names(U, FA, JClass(PKG + "KnowSync").collShared(U), 400))   # (stand-in items have no names: dname = the id)
    K.check(t2.startswith("On for 6 of 26: ") and all(x in t2w for x in ("Wheat", "Carrot", "Lettuce", "Potato", "Pumpkin", LE)) and " +" in t2
            and "Next: " in t2 and "Tomato I (3/15)" in t2,
            "PAGE31 the On line names the unlocked items and the closest locked one with its tier: %r" % t2)
    tier(0)
    t3 = str(VC.names(U, FA, JClass(PKG + "KnowSync").collShared(U), 60))
    K.check(t3.startswith("On for 5 of 26: "), "PAGE31 Essence of Life below tier I is not counted as unlocked: %r" % t3)
    tier(9)
    st_w, st_t, st_le = (str(VC.stateOf(U, k, JString(x))) for x in (WHEAT, TOMATO, LE))
    K.check(st_w == "Auto-compacts (unlocked)" and st_t == "Locked: Tomato I (3/15)" and st_le == "Auto-compacts (unlocked)"
            and str(VC.stateOf(U, k, JString("Ingredient_Bar_Iron"))) == "",
            "PAGE31 a selected item: Wheat %r, Tomato %r, Essence of Life %r; Iron (Smithing, not bought) says nothing" % (st_w, st_t, st_le))
    p3 = player(storage=[], cap=4)
    pg = us.allocateInstance(SPage.class_)
    jfield(SPage.class_, "playerRef").set(pg, pref(U))
    jfield(SPage.class_, "info").set(pg, JString(""))
    jfield(SPage.class_, "amount").set(pg, JString(""))
    UCBc = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEBc = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def text(b_):
        out_ = []
        for c_ in b_.getCommands():
            k_ = c_.getClass()
            while k_ is not None:
                for f_ in k_.getDeclaredFields():
                    if JClass("java.lang.reflect.Modifier").isStatic(f_.getModifiers()):
                        continue
                    f_.setAccessible(True)
                    v_ = f_.get(c_)
                    if v_ is not None:
                        out_.append(str(v_))
                k_ = k_.getSuperclass()
        return "\n".join(out_)

    def render(cat, sel=None):
        pg.cat = cat
        pg.sel = None if sel is None else JString(sel)
        b_, e_ = UCBc(), UEBc()
        pg.render(b_, e_, p3, k, U)
        return text(b_)
    t = render("Farming", TOMATO)
    K.check("Auto-compact: On" in t and "On for 6 of 26:" in t and "Locked: Tomato I (3/15)" in t,
            "PAGE31 the rendered Farming page: 'Auto-compact: On', 'On for 6 of 26: ...', the selected Tomato 'Locked: Tomato I (3/15)'")
    sk = Pool.settledKey(U)
    if sk is not None and str(sk) == k:
        pg.key = JString(k)
        VC.toggle(U, k, FA)
        Pool.add(k, WHEAT, JLong(263))   # 37 + 263 = 300
        pg.onEvent(None, None, p3, JString('{"a":"cmptog:%d","@Amt":""}' % FA))
        K.check(str(pg.info).startswith("+Auto-compact is on again") and "3 Enchanted made now" in str(pg.info) and pc(k).get(WHEAT) is None,
                "PAGE31 Turn on compacts at once (no sweep needed): %s" % pg.info)
    else:
        K.notes.append("PAGE31 the click test needs settledKey(U) == k here (got %s) - runNow was checked directly above" % sk)

    # ---- the safety re-read clock (pd.compact.recheck)
    Cfg.CMP_RECHECK = 180
    Beat.LASTRE = 0
    seq = [bool(Beat.recheckDue(JLong(t_))) for t_ in (1000, 1000 + 179999, 1000 + 180000, 1000 + 180001)]
    Cfg.CMP_RECHECK = 0
    off = bool(Beat.recheckDue(JLong(10 ** 9)))
    Cfg.CMP_RECHECK = 180
    K.check(seq == [False, False, True, False] and not off, "RECHECK every 180 s (first call arms the clock), 0 = off: %s / %s" % (seq, off))
    # ---- the watchdog
    Beat.QUEUED = True
    Beat.SENT = 1000
    Beat.STALLED = False
    n0 = int(Beat.STALLS.get())
    Beat.check(JLong(1000 + 29999))
    s1 = bool(Beat.STALLED)
    Beat.check(JLong(1000 + 30000))
    s2, n1 = bool(Beat.STALLED), int(Beat.STALLS.get())
    Beat.check(JLong(1000 + 90000))
    n2 = int(Beat.STALLS.get())
    Beat().run()
    K.check(not s1 and s2 and n1 == n0 + 1 and n2 == n1 and not bool(Beat.STALLED) and not bool(Beat.QUEUED),
            "WATCHDOG the shared scheduler not running our beat for 30 s = ONE stall warning (not repeated), cleared when it runs")
    drain()


def run_cmp31(out, jar, scratch, home):
    T089.void_cases = cases31
    T089.run_void(out, jar, scratch, home)


def run_tick(out, jar, scratch, _home):
    """bytecode: SackTick on SackPool.WRITER; SackTick.run -> SackBeat.check + recheckDue; the sweep order kept"""
    from jpype import JClass, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(JString(jar))
    Mn = JClass("javassist.bytecode.Mnemonic")

    def ops(m):
        seen = []
        ci = m.getMethodInfo().getCodeAttribute().iterator()
        cpool = m.getMethodInfo().getConstPool()
        while ci.hasNext():
            i = ci.next()
            op = str(Mn.OPCODE[ci.byteAt(i)])
            if op in ("getstatic", "putstatic"):
                idx = ci.u16bitAt(i + 1)
                seen.append(op + " " + str(cpool.getFieldrefClassName(idx)).split(".")[-1] + "." + str(cpool.getFieldrefName(idx)))
            elif op == "new":
                seen.append("new " + str(cpool.getClassInfo(ci.u16bitAt(i + 1))).split(".")[-1])
            elif op in ("invokestatic", "invokevirtual", "invokeinterface", "invokespecial"):
                idx = ci.u16bitAt(i + 1)
                if op == "invokeinterface":
                    seen.append(str(cpool.getInterfaceMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getInterfaceMethodrefName(idx)))
                else:
                    seen.append(str(cpool.getMethodrefClassName(idx)).split(".")[-1] + "." + str(cpool.getMethodrefName(idx)))
        return seen
    pl = cp.get(PKG + "SkyySacksPlugin")
    hit = None
    for m in pl.getDeclaredMethods():
        s = ops(m)
        for j in range(len(s) - 2):
            if s[j + 1] == "new SackTick":
                hit = (str(m.getName()), s[j])
    K.check(hit is not None and hit[1] == "getstatic SackPool.WRITER", "TICK SackTick is scheduled on SackPool.WRITER (our own thread): %s" % (hit,))
    shared = [str(m.getName()) for m in pl.getDeclaredMethods() if any(
        ops(m)[j] == "getstatic HytaleServer.SCHEDULED_EXECUTOR" and ops(m)[j + 1] == "new SackTick" for j in range(len(ops(m)) - 1))]
    K.check(not shared, "TICK no SackTick on HytaleServer.SCHEDULED_EXECUTOR any more (%s)" % shared)
    s = ops(cp.get(PKG + "SackTick").getDeclaredMethod("run"))
    K.check("SackBeat.check" in s and "SackBeat.recheckDue" in s and s.index("SackBeat.check") < s.index("SweepTask.needs"),
            "TICK SackTick.run: the watchdog + the re-check clock before the per-player loop")
    sb = ops(cp.get(PKG + "SackBeat").getDeclaredMethod("check"))
    K.check("getstatic HytaleServer.SCHEDULED_EXECUTOR" in sb and "new SackBeat" in sb, "TICK SackBeat.check puts the beat on the shared scheduler")
    s = ops(cp.get(PKG + "SweepTask").getDeclaredMethod("run"))
    a, b_, c = (s.index(x) if x in s else -1 for x in ("SweepTask.items", "VoidCompact.run", "SweepTask.sigOf"))
    K.check(0 <= a < b_ < c, "TICK SweepTask.run: items -> VoidCompact.run -> sigOf (unchanged)")
    K.save()


def _props(p):
    d = {}
    for ln in open(p, encoding="latin-1"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            a, b = ln.split("=", 1)
            d[a.strip()] = b.strip()
    return d


def live_unlocks(coll_dir, key):
    """the player's unlocks the way SkyyCollections 0.2.33 computes them (read-only scratch copy): Enchanted row r is unlocked when its
    collection's count reaches the ench.tier.<key> threshold (config line, else the row's tier); Life Essence = its collection tier"""
    C = _props(os.path.join(coll_dir, "collections.properties"))
    cnt = _props(os.path.join(coll_dir, "counts", key + ".properties"))
    cfg = _props(os.path.join(coll_dir, "config.properties"))
    curv = dict((k_[6:], [int(x) for x in v.split(",")]) for k_, v in C.items() if k_.startswith("curve."))

    def tier_of(cid):
        row = C.get("coll." + cid)
        if not row:
            return 0, 0
        p = row.split("|")
        n = sum(int(cnt.get(i, 0)) for i in p[4].split(",") if i)
        return sum(1 for x in curv[p[1]] if n >= x), n
    unl, rows = [], []
    for t in EN.TABLE + EN.TABLE_ALLOYS:
        if t[1] != "I":
            continue
        et = int(cfg.get("ench.tier." + t[0].lower(), t[4]))
        ti, n = tier_of(t[3])
        rows.append((t[5], t[3], t[2], ti, et, n))
        if ti >= et and not EN.TABLE_ALLOYS.count(t):
            unl.append(EN.PREFIX + t[0])
    le_t, le_n = tier_of("LifeEssence")
    return unl, le_t, le_n, rows


def run_live31(out, jar, scratch, home):
    from jpype import JClass, JString, JInt, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    VS, Pool, VC, Cfg = JClass(PKG + "VoidStore"), JClass(PKG + "SackPool"), JClass(PKG + "VoidCompact"), JClass(PKG + "SackCfg")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", bridge)
    cdir = os.path.join(scratch, "live31coll")
    shutil.copytree(COLL_LIVE, cdir)            # read-only source; the scratch copy is what we read
    key = "d8ddde89-98b2-4739-983e-a39773d582b6-p3"
    jp = JClass("javassist.ClassPool")(True)
    jp.appendClassPath(JString(jar))
    CS = coll_stub(jp, JClass(PKG + "SackBridge").class_)
    for kd in ("tier", "where", "count"):
        bridge.put(JString("coll:fn:" + kd), CS(JString(kd)))
    unl, le_t, le_n, rows = live_unlocks(cdir, key)
    CS.R.put(JString("tier:LifeEssence"), JInt(le_t))
    bridge.put(JString("coll:recipes:" + key[:36]), JString(",".join(e + RS for e in unl)))
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Cfg.MTIME = -1
    Cfg.reload()
    VS.DIR = Paths.get(os.path.join(home, "pd"))
    Pool.DIR = Paths.get(os.path.join(home, "pools"))
    if not os.path.isfile(os.path.join(home, "pd", key + ".properties")):
        K.notes.append("LIVE31 no %s profile in the live copy - skipped" % key)
        K.save()
        return
    u = JClass("java.util.UUID").fromString(JString(key[:36]))
    bought = [str(c) for i, c in enumerate(JClass(PKG + "SackDefs").CATS) if bool(VC.active(key, i))]
    b0 = dict((str(e.getKey()), int(e.getValue().longValue())) for e in Pool.pool(key).entrySet())
    made = int(VC.run(u, key, VS.capsK(u, key)))
    a = dict((str(e.getKey()), int(e.getValue().longValue())) for e in Pool.pool(key).entrySet())
    le0, lec0 = b0.get(LE, 0), b0.get(LEC, 0)
    farming = "Farming" in bought
    K.check(farming and le_t >= 1, "LIVE31 the live profile: Auto-compact on in %s; Life Essence collection tier %d (%d collected)" % (bought, le_t, le_n))
    K.check(a.get(LE, 0) == le0 % 100 and a.get(LEC, 0) == lec0 + le0 // 100,
            "LIVE31 Essence of Life %d + Greater %d -> %d loose + %d Greater (%d made)%s" % (
                le0, lec0, a.get(LE, 0), a.get(LEC, 0), le0 // 100,
                " = Skyy's 4,955 -> 49 + 55" if (le0, lec0) == (4955, 73) else ""))
    pairs = [(str(b), str(e)) for b, e in zip(VC.BASE, VC.ENCH)] + [(LE, LEC)]
    K.check(all(a.get(b, 0) + 100 * a.get(e, 0) == b0.get(b, 0) + 100 * b0.get(e, 0) for b, e in pairs)
            and all(a.get(x, 0) == b0.get(x, 0) for x in set(a) | set(b0) if x not in dict(pairs) and x not in dict((e, b) for b, e in pairs)),
            "LIVE31 every pair's value conserved and no other item changed (%d Enchanted / Greater made)" % made)
    Defs = JClass(PKG + "SackDefs")
    moved = sorted(b for b, e in pairs if a.get(b, 0) != b0.get(b, 0))
    bad = [b for b, e in pairs if a.get(b, 0) != b0.get(b, 0) and not (e in unl or e == LEC)]
    left = [b for b, e in pairs if (e in unl or e == LEC) and str(Defs.homeOf(JString(b))) in bought and a.get(b, 0) >= 100]
    K.check(not bad and not left, "LIVE31 only unlocked pairs moved (%s); no unlocked pair in a bought bag keeps 100+ loose (%s)" % (moved, left))
    fr = [r for r in rows if r[0] == "Farming"]
    K.notes.append("LIVE31 Farming unlocks (collection, tier now / needed, collected): " + "; ".join(
        "%s %s %d/%d (%d)" % ("UNLOCKED" if r[3] >= r[4] else "locked", r[1], r[3], r[4], r[5]) for r in fr)
        + "; Life Essence tier %d (needs %d)" % (le_t, int(VC.VTIER)))
    K.notes.append("LIVE31 Farming before -> after: " + ", ".join("%s %d->%d" % (b, b0.get(b, 0), a.get(b, 0)) for b in
                                                                 (LE, LEC, WHEAT, EW, CARROT, EC, LETTUCE, EL) if b0.get(b, 0) or a.get(b, 0)))
    K.save()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ["SackBeat"],
           [("cmp30", T30.run_cmp30), ("sweephook", T30.run_sweephook), ("rbw", T30.run_rbw), ("rbr", T30.run_rbr),
            ("cmp31", run_cmp31), ("tick", run_tick),
            ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10), ("live31", run_live31)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
