"""Harness for SkyySacks 0.8.16 (round small16: seeds / saplings Void switches, saplings -> Foraging, the vanilla pickup popup switch, the
feed card text; tools/sacks_0_8_16_patch.py). Build first:
    python tools/sacks_0_8_16_patch.py && python SkyySacks/build_skyysacks_0.8.16.py

    python SkyySacks/test_skyysacks_0.8.16.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.8.15 -> 0.8.16: exactly the planned members (+ PopupHide); non-class entries: manifest.json only
  NEW  the 0.8.15 harness's NEW phase on THIS jar (the kit 1.7 Void + /craft pages through SUI.assert_menu_page, the Void ops, the
       crafter, ADD FUEL, the Pocket tab) - the menu sweep pages still pass
  TG   EXECUTED on the 0.8.0 harness's Void stand-ins (real SimpleItemContainers, a stand-in Item store, a scratch pool folder):
       HOME   saplings are Foraging, seeds / Eternal seeds Farming, crops Farming
       FLAGS  SackPool.keepFlags reads the two /settings switches through a stand-in settings:fn:get (no SkyyMenu = both ON)
       ROUTE  PickGive.voidRoom (every auto-pickup: block / mob drops, harvests) and the sweep (2 s sweep + Deposit all): switches ON =
              seeds + saplings into the Void (0.8.15 behaviour); seeds OFF = seeds stay in the inventory, saplings still go in; saplings
              OFF likewise; both OFF; another player's switches never touch this player; the explicit Deposit (amount box) still stores;
              the sweep signature changes with a switch (so switching back ON re-sweeps)
       POPUP  PopupHide on the real GameplayConfig.DEFAULT: hide -> showItemPickupNotifications false, show -> true again, re-hide; the
              tick applies a changed switch at once; the Server Setup row + after= hook + config text exist
       FEED   the card text: the name alone (Void / inventory), "- Void full, rest in inventory", "- inventory full, on the ground"
  D    START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.10's run_live10 on this jar)
  AA   engine-access audit
Not testable without the game (UNVERIFIED): that the client shows no popup once the flag is off (the server stops SENDING it - bytecode),
the /settings rows in SkyyMenu's page, picking seeds up in game. Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK

_orig_compare = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_15", os.path.join(HERE, "test_skyysacks_0.8.15.py"))
T15 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T15)
HK.run_compare = _orig_compare      # 0.8.15's compare wrapper expects its own tab icon pair; this round changes only manifest.json
T0810, T089 = T15.T0810, T15.T089

VERSION = "0.8.16"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.15.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "small16", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],      # the config kit: version text + the new row
    "SackDefs": ["+f KEEPOUT", "+m keepKind", "+m intake", "~<clinit>", "~m homeOf"],
    "SackPool": ["+m keepFlags"],
    "SackCfg": ["+f HIDE_POPUP", "+m popupChanged", "~<clinit>", "~m pickKeys", "~m reload"],   # reload: the config.properties template text
    "CfgFile": ["~<clinit>"],   # the kit default texts (the config.properties template)
    "SweepTask": ["~m sigOf", "~m sweep"],
    "PickGive": ["~m text", "~m voidRoom"],
    "SackTick": ["~m run"],
    "SkyySacksPlugin": ["~m setup"],
}
ADDED = ["PopupHide"]


def run_tg(out, jar, scratch, home):
    """the 0.8.15 run_new pattern (the 0.8.0 stand-in slice), with this round's cases"""
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    src = open(T089.T080, encoding="utf8").read()
    a = src.index("    # ---------------- stand-ins (the 0.7.12+ harness pattern)\n")
    b = src.index("    # ---------------- D. categories\n", a)
    head = ("def run_void_fixture():\n    import jpype\n    import skyybuild as B\n"
            "    from jpype import JClass, JArray, JShort, JString, JInt, JLong, JImplements, JOverride\n"
            "    jp = JClass(\"javassist.ClassPool\")(True)\n    jp.appendClassPath(B.SERVER_JAR)\n    jp.appendClassPath(JAR)\n")
    body = head + src[a:b] + "    _VOID(locals())\n"
    ns = {"__file__": T089.T080, "__name__": "t080"}
    exec(compile(src[:src.index("def run():")], T089.T080, "exec"), ns)
    ns.update(JAR=jar, SCRATCH=os.path.join(scratch, "tg"), _VOID=lambda L: tg_cases(K, L, scratch, jar))
    exec(compile(body, T089.T080 + " (stand-in slice)", "exec"), ns)
    try:
        ns["run_void_fixture"]()
    finally:
        for f in ns["FAILS"]:
            K.check(False, "TG fixture: " + f)
        K.save()
        try:
            __import__("jpype").JClass(PKG + "SackPool").WRITER.shutdownNow()
        except Exception:
            pass


def tg_cases(K, L, scratch, jar):
    from jpype import JClass, JString, JImplements, JOverride, JLong
    Defs, Cfg, Pool = L["Defs"], L["Cfg"], L["Pool"]
    fresh, player, inv_counts, custom_item, drain, pc = (L[n] for n in ("fresh", "player", "inv_counts", "custom_item", "drain", "pc"))
    UUID, jfield, pref, bridge = (L[n] for n in ("UUID", "jfield", "pref", "bridge"))
    J = lambda n: JClass(PKG + n)
    Swp, PG, VS, PH = J("SweepTask"), J("PickGive"), J("VoidStore"), J("PopupHide")
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    pr_field = jfield(PLA.class_, "playerRef")

    # ============================================================== HOME
    SEED, ETER, SAPL, SAPL2, WHEAT = "Plant_Seeds_Wheat", "Plant_Seeds_Wheat_Eternal", "Plant_Sapling_Oak", "Plant_Sapling_Spruce_Frozen", "Plant_Crop_Wheat_Item"
    for i_ in (SEED, ETER, SAPL, SAPL2, WHEAT):
        custom_item(i_, 100)
    homes = dict((i_, str(Defs.homeOf(JString(i_)))) for i_ in (SEED, ETER, SAPL, SAPL2, WHEAT, "Plant_Seeds_Oak"))
    K.eq(homes, {SEED: "Farming", ETER: "Farming", SAPL: "Foraging", SAPL2: "Foraging", WHEAT: "Farming", "Plant_Seeds_Oak": "Farming"},
         "HOME: saplings -> Foraging (Skyy 'saplings in foraging'), seeds / Eternal seeds / seed bags + crops stay Farming")
    K.eq([int(Defs.keepKind(JString(i_))) for i_ in (SEED, ETER, SAPL, WHEAT, "Recipe_Plant_Seeds_Health1")], [1, 1, 2, 0, 0],
         "HOME: keepKind - seeds 1, saplings 2, everything else 0")

    # ============================================================== FLAGS (the /settings switches through settings:fn:get)
    SETS = {}

    @JImplements("java.util.function.Function")
    class SetGet(object):
        @JOverride
        def apply(self, o):
            u_, key_ = str(o[0]), str(o[1])
            v = SETS.get((u_, key_))
            return None if v is None else JClass("java.lang.Boolean").valueOf(v)
    U1, U2 = UUID.fromString("00000000-0000-0000-0000-00000000a001"), UUID.fromString("00000000-0000-0000-0000-00000000a002")
    bridge.remove("settings:fn:get")
    K.eq(int(Pool.keepFlags(U1)), 0, "FLAGS: no SkyyMenu (no settings:fn:get) = both switches ON (into the Void, the 0.8.15 behaviour)")
    bridge.put("settings:fn:get", SetGet())
    K.eq(int(Pool.keepFlags(U1)), 0, "FLAGS: a player who never touched the switches (no answer) = both ON")

    def setf(u_, seeds, saps):
        SETS[(str(u_), "sacks.seedsVoid")] = seeds
        SETS[(str(u_), "sacks.saplingsVoid")] = saps
        return int(Pool.keepFlags(u_))
    K.eq([setf(U1, True, True), setf(U1, False, True), setf(U1, True, False), setf(U1, False, False)], [0, 1, 2, 3],
         "FLAGS: seeds off = 1, saplings off = 2, both = 3, both on = 0")
    K.check(Defs.KEEPOUT.get(str(U1)) is not None and int(Defs.KEEPOUT.get(str(U1))) == 3 and Defs.KEEPOUT.get(str(U2)) is None,
            "FLAGS: KEEPOUT holds U1 = 3, nothing for U2")
    setf(U1, True, True)
    K.check(Defs.KEEPOUT.get(str(U1)) is None, "FLAGS: switching both back ON removes the entry")

    # ============================================================== ROUTE (auto-pickup gate + the sweep)
    def mkp(u_, storage):
        p_ = player(storage=storage)
        pr_field.set(p_, pref(u_))
        return p_
    k1 = str(U1)

    def room(u_, iid, q=10):
        return int(PG.voidRoom(u_, JString(k1), IS(iid, q)))

    def sweep_case(tag, seeds, saps):
        fresh(os.path.join(scratch, "tg", "pd-" + tag))
        setf(U1, seeds, saps)
        p_ = mkp(U1, [(SEED, 12), (SAPL, 5), (WHEAT, 20)])
        before = inv_counts(p_)
        moved = int(Swp.sweep(p_, JString(k1), None, True))     # Deposit all (allContainers) = the same gate as the 2 s sweep
        drain()
        after, pool = inv_counts(p_), pc(k1)
        kept = sorted(i_ for i_ in (SEED, SAPL, WHEAT) if after.get(i_, 0) == before[i_])
        stored = sorted(i_ for i_ in (SEED, SAPL, WHEAT) if pool.get(i_, 0) == before[i_] and after.get(i_, 0) == 0)
        total_ok = all(after.get(i_, 0) + pool.get(i_, 0) == before[i_] for i_ in before)
        return kept, stored, moved, total_ok

    fresh(os.path.join(scratch, "tg", "pd-room"))
    setf(U1, True, True)
    r_on = [room(U1, i_) for i_ in (SEED, SAPL, WHEAT)]
    K.check(all(r_ > 0 for r_ in r_on), "ROUTE: switches ON - auto-pickup puts seeds, saplings and crops into the Void (room %s)" % r_on)
    setf(U1, False, True)
    r_s = [room(U1, i_) for i_ in (SEED, ETER, SAPL, WHEAT)]
    K.check(r_s[0] == 0 and r_s[1] == 0 and r_s[2] > 0 and r_s[3] > 0, "ROUTE: seeds OFF - seeds + Eternal seeds stay in the inventory (room 0), saplings + crops still go in (%s)" % r_s)
    setf(U1, True, False)
    r_p = [room(U1, i_) for i_ in (SEED, SAPL, SAPL2, WHEAT)]
    K.check(r_p[0] > 0 and r_p[1] == 0 and r_p[2] == 0 and r_p[3] > 0, "ROUTE: saplings OFF - saplings stay out, seeds + crops go in (%s)" % r_p)
    setf(U2, False, False)
    setf(U1, True, True)
    K.check(room(U1, SEED) > 0 and room(U1, SAPL) > 0 and int(PG.voidRoom(U2, JString(str(U2)), IS(SEED, 5))) == 0,
            "ROUTE: one player's switches never touch another player (U2 off, U1 on)")
    setf(U2, True, True)

    res = {}
    for tag, sd, sa in (("on", True, True), ("seeds", False, True), ("saps", True, False), ("both", False, False)):
        res[tag] = sweep_case(tag, sd, sa)
    K.eq(res["on"][:2], ([], sorted([SAPL, SEED, WHEAT])), "ROUTE: sweep with both ON - everything into the Void (%s)" % (res["on"],))
    K.eq(res["seeds"][:2], ([SEED], sorted([SAPL, WHEAT])), "ROUTE: sweep with seeds OFF - the 12 seeds stay in the inventory (%s)" % (res["seeds"],))
    K.eq(res["saps"][:2], ([SAPL], sorted([SEED, WHEAT])), "ROUTE: sweep with saplings OFF - the 5 saplings stay (%s)" % (res["saps"],))
    K.eq(res["both"][:2], (sorted([SAPL, SEED]), [WHEAT]), "ROUTE: sweep with both OFF - only the wheat goes in (%s)" % (res["both"],))
    K.check(all(v[3] for v in res.values()), "ROUTE: every sweep: inventory + Void = what the player had (nothing lost or doubled)")
    # the explicit Deposit (amount box, one picked item) still stores seeds on purpose
    fresh(os.path.join(scratch, "tg", "pd-dep"))
    setf(U1, False, False)
    p_ = mkp(U1, [(SEED, 12)])
    got = int(VS.depositInv(p_, U1, JString(k1), JString(SEED), JLong(-1)))
    drain()
    K.check(got == 12 and inv_counts(p_).get(SEED, 0) == 0 and pc(k1).get(SEED, 0) == 12,
            "ROUTE: the Deposit button (picked item, amount box) still stores seeds with the switch off (%d)" % got)
    # the sweep signature follows the switches (switching back ON re-sweeps at once)
    s_off = str(Swp.sigOf(U1))
    setf(U1, True, True)
    SETS[(str(U1), "sacks.seedsVoid")] = True
    s_on = str(Swp.sigOf(U1))
    K.check(s_off != s_on, "ROUTE: SweepTask.sigOf changes with a switch (a switch flip wakes the sweep)")
    SETS.clear()
    Defs.KEEPOUT.clear()

    # ============================================================== POPUP (the real GameplayConfig.DEFAULT)
    # the real GameplayConfig class needs the game's asset stores in its static init (EntityEffect, ...): TEST ONLY its <clinit> is
    # replaced by "DEFAULT = new GameplayConfig()" (the real public constructor, the real field + getter PopupHide changes)
    GCN = "com.hypixel.hytale.server.core.asset.type.gameplay.GameplayConfig"
    jp = L["jp"]
    gc_ = jp.get(GCN)
    gc_.getClassInitializer().setBody("{ java.lang.reflect.Field f = sun.misc.Unsafe.class.getDeclaredField(\"theUnsafe\"); f.setAccessible(true);"
                                      " DEFAULT = (%s) ((sun.misc.Unsafe) f.get(null)).allocateInstance(%s.class); }" % (GCN, GCN))
    gc_.toClass(JClass("com.hypixel.hytale.server.core.asset.type.gameplay.DeathConfig$ItemsLossMode").class_)
    GCc = JClass(GCN)
    d = GCc.DEFAULT                                # a GameplayConfig object (its sub-configs need the asset stores - not loaded here)
    jfield(GCc.class_, "showItemPickupNotifications").setBoolean(d, True)   # the vanilla default (popups on)
    K.check(GCc.DEFAULT is not None and bool(GCc.DEFAULT.getShowItemPickupNotifications()), "POPUP: the stand-in DEFAULT starts with popups on")
    v0 = bool(d.getShowItemPickupNotifications())
    Cfg.HIDE_POPUP = True
    n1 = int(PH.apply())
    v1 = bool(d.getShowItemPickupNotifications())
    Cfg.HIDE_POPUP = False
    n2 = int(PH.apply())
    v2 = bool(d.getShowItemPickupNotifications())
    K.check(v0 and n1 >= 1 and not v1 and n2 >= 1 and v2,
            "POPUP: hide -> GameplayConfig.DEFAULT.getShowItemPickupNotifications() false (%d changed), show -> true again (%d) [%s]" % (n1, n2, str(PH.STATE)))
    Cfg.HIDE_POPUP = True
    PH.LAST = 0
    PH.tick()
    K.check(not bool(d.getShowItemPickupNotifications()) and int(PH.LAST) == 1, "POPUP: the 2 s tick applies a changed switch at once")
    K.eq(int(PH.apply()), 0, "POPUP: applying again changes nothing (already hidden)")
    Cfg.HIDE_POPUP = False
    Cfg.popupChanged(JString("pickup.hidePopup"))
    K.check(bool(d.getShowItemPickupNotifications()), "POPUP: the Server Setup after= hook (SackCfg.popupChanged) shows it again at once")
    Cfg.HIDE_POPUP = True
    bs = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    K.check('("pickup.hidePopup", "Hide the vanilla pickup popup", "pickup", "bool", "true"' in bs and "after=SackCfg.popupChanged" in bs
            and '"#pickup.hidePopup=true",' in bs and 'HIDE_POPUP = boolKey(p, "pickup.hidePopup", true);' in bs,
            "POPUP: the Server Setup row (live, default ON, after= hook), the config.properties line and the hand-edit reader exist")
    with zipfile.ZipFile(jar) as z:
        rows = z.read("com/skyy/sacks/CfgRows.class")
    K.check(b"pickup.hidePopup" in rows, "POPUP: the row is in the jar's CfgRows (Server Setup -> SkyyVoid and Crafting -> Auto-pickup)")
    K.check('regSetting("sacks.seedsVoid", "Seeds go into the Void", "sacks", true' in bs and 'regSetting("sacks.saplingsVoid", "Saplings go into the Void", "sacks", true' in bs,
            "FLAGS: setup registers the two /settings switches (tab sacks, default ON)")

    # ============================================================== FEED (the card text)
    def r_arr(v):
        a_ = JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.Long").TYPE, 3)
        for i_, x in enumerate(v):
            JClass("java.lang.reflect.Array").setLong(a_, i_, x)
        return a_
    t = lambda r_, q: str(PG.text(JString("Oak Log"), r_arr(r_), q))
    K.eq([t([12, 0, 0], 12), t([0, 12, 0], 12), t([5, 7, 0], 12), t([0, 4, 8], 12), t([12, 0, 3], 15)],
         ["Oak Log", "Oak Log", "Oak Log - Void full, rest in inventory", "Oak Log - inventory full, on the ground", "Oak Log - inventory full, on the ground"],
         "FEED: the card text = the name alone (like vanilla), a note only when the Void / inventory is full")
    drain()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("new", T15.run_new), ("tg", run_tg), ("live", T0810.run_live10)],
           __file__, live=(T15.BETA, "Skyy_SkyySacks"))
