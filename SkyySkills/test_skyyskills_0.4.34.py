"""SkyySkills 0.4.34 - harness for CHAT OVERFLOW -> FEED (tools/skills_0_4_34_patch.py, the shared tools/skyyroute.py MsgRoute).
Build first: python tools/skills_0_4_34_patch.py && python SkyySkills/build_skyyskills_0.4.34.py

    python SkyySkills/test_skyyskills_0.4.34.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.33 -> 0.4.34: exactly the planned members differ; MsgRoute added
  R   route    EXECUTED with a stand-in SkyyHud on the skyy.bridge map (msgroute:fn:get / feed:fn:push / xpflash:fn:push as Functions):
               MsgRoute: no SkyyHud = chat (no ask), the 2 s cache (one ask), TTL 0 asks again, an odd / throwing answer = chat, feed /
               flash answers, forget, pretty;
               SkillMsg.routed for EVERY route: chat = the 0.4.33 jar's take() text word for word (same state, its own loader), feed = one
               xpflash per skill with the HUD names (class skill via class:skill:<uuid>), a refused flash stays in the chat line, off =
               nothing, the staged Acrobatics counter flashes too, an old SkyyHud (no msgroute) = the chat line; PEND / STAGE emptied and
               LAST stamped on every route;
               PartyXp.routed: chat = 0.4.33's "[Party] ..." line word for word, feed / partial / off;
               Perks.ddRoute / ddFeed / ddFeedList, Brew.potRoute, Fell.sumFeed: feed cards (kind, icon id, text, count), refused = chat,
               off = handled with no card, chat = not handled;
               SESSION: a 12-minute session shaped like the 2026-10-11 log (75 skill-XP lines, 4 double drops, 1 tree summary) run
               through the real routed() / ddRoute / sumFeed with no SkyyHud (= 0.4.33) and with the server defaults (Feed) ->
               tools/dev/scratch/msgroute/session/skills.json (the Collections harness adds every mod up)
  X   exec     test_skyyskills_0.4.32.py's exec phase on the 0.4.34 jar (every 0.4.32 lag-fix path still holds)
  D   live     test_skyyskills_0.4.32.py's live phase on the 0.4.34 jar: START TWICE on a scratch COPY of the live Skyy_SkyySkills
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.4.34"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.33.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "msgroute", "sk")))
SESSION = os.environ.get("SKYYROUTE_SESSION") or os.path.join(ROOT, "tools", "dev", "scratch", "msgroute", "session")
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")

EXPECT = {
    # version texts only (inlined strings): the pack name "Skyy:0.4.34 SkyySkills", the xp.properties header, the config kit's export header
    "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"],
    "SkillCfg": ["~m load"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "SkyySkillsPlugin": ["~m setup"],
    "SkillMsg": ["+m line", "+m routed", "+m takeArr", "~m send", "~m take"],
    "PartyXp": ["+m routed", "+m takeRaw", "+m text", "~m send", "~m take"],
    "Perks": ["+m ddFeed", "+m ddFeedList", "+m ddRoute", "~m doubled"],
    "Brew": ["+m potRoute", "~m extraPotion"],
    "Fell": ["+m sumFeed", "~m end"],
}
ADDED = ["MsgRoute"]


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T32 = tmod("test_skyyskills_0.4.32.py", "t0432")
if not os.path.isfile(T32.OLD_JAR) and os.environ.get("SKYY_OLD_JAR_DIR"):   # tools/tidy_local.py archives 0.4.31: an extracted copy
    T32.OLD_JAR = os.path.join(os.environ["SKYY_OLD_JAR_DIR"], os.path.basename(T32.OLD_JAR))


# ====================================================================================================== R: every route, executed
def run_route(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    MR, SM, PX, PK, BR_, FE, Defs, Sto, SCl = (P("MsgRoute"), P("SkillMsg"), P("PartyXp"), P("Perks"), P("Brew"), P("Fell"), P("SkillDefs"),
                                               P("SkillStore"), P("SkillClass"))
    Sys, UUID, Bool, Long = JClass("java.lang.System"), JClass("java.util.UUID"), JClass("java.lang.Boolean"), JClass("java.lang.Long")
    Cfg = P("SkillCfg")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    pd = os.path.join(scratch, "r", "players")
    os.makedirs(pd)
    Sto.DIR = T32.path(pd)
    bridge = Sto.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    S = {"route": {}, "feed_ok": True, "flash_ok": True, "flash_no": set(), "asks": 0, "cards": [], "flashes": [], "throw": False}

    def f_route(o):
        S["asks"] += 1
        if S["throw"]:
            raise RuntimeError("boom")
        return S["route"].get(str(o[1]), "chat")

    def f_feed(o):
        S["cards"].append((str(o[1]), None if o[2] is None else str(o[2]), str(o[3]), None if o[4] is None else int(o[4])))
        return Bool.TRUE if S["feed_ok"] else Bool.FALSE

    def f_flash(o):
        S["flashes"].append((str(o[1]), int(o[2])))
        return Bool.FALSE if (not S["flash_ok"] or str(o[1]) in S["flash_no"]) else Bool.TRUE

    FR, FF, FX = Fn(f_route), Fn(f_feed), Fn(f_flash)

    def hud(on=True, route=None):
        for k in ("msgroute:fn:get", "feed:fn:push", "xpflash:fn:push"):
            bridge.remove(k)
        if on:
            bridge.put("msgroute:fn:get", FR)
            bridge.put("feed:fn:push", FF)
            bridge.put("xpflash:fn:push", FX)
        S["route"] = dict(route or {})
        S["cards"], S["flashes"], S["asks"], S["feed_ok"], S["flash_ok"], S["flash_no"], S["throw"] = [], [], 0, True, True, set(), False
        MR.CACHE.clear()
        MR.GATE.clear()

    u = UUID.fromString("00000000-0000-4000-8000-000000000434")
    us = str(u)
    MINING, ACRO = int(Defs.indexOf("mining")), int(Defs.indexOf("acrobatics"))
    DIV = int(Defs.indexOf("divinity"))
    K.check(MINING >= 0 and ACRO >= 0 and DIV >= 0, "R setup: skill slots %d / %d / %d" % (MINING, ACRO, DIV))
    bridge.put("class:skill:" + us, "Divinity")
    bridge.put("class:" + us, "Priest")
    NAMES = dict((i, str(SCl.skillName(u, i))) for i in range(int(Defs.N)))

    # ---- MsgRoute itself
    hud(False)
    K.eq(str(MR.route(u, "skillxp")), "chat", "R MsgRoute: no SkyyHud -> chat")
    K.check(not MR.feed(u, "drop", None, "x", 1) and not MR.flash(u, "Mining", 5), "R MsgRoute: no SkyyHud -> feed / flash refused")
    hud(True, {"skillxp": "feed", "drop": "off"})
    a0 = int(MR.ASKS.get())
    r1, r2 = str(MR.route(u, "skillxp")), str(MR.route(u, "skillxp"))
    K.check(r1 == "feed" and r2 == "feed" and S["asks"] == 1 and int(MR.ASKS.get()) == a0 + 1, "R MsgRoute: cached - two routes, one ask")
    K.eq(str(MR.route(u, "drop")), "off", "R MsgRoute: off")
    S["route"]["skillxp"] = "chat"
    K.eq(str(MR.route(u, "skillxp")), "feed", "R MsgRoute: inside the 2 s cache a changed choice is not asked yet")
    MR.CACHE.clear()
    MR.TTL = 0
    a1 = S["asks"]
    r3, r4 = str(MR.route(u, "skillxp")), str(MR.route(u, "skillxp"))
    K.check(r3 == "chat" and r4 == "chat" and S["asks"] == a1 + 2, "R MsgRoute: TTL 0 asks every time (the player's new choice)")
    MR.TTL = 2000
    hud(True, {"skillxp": "weird"})
    K.eq(str(MR.route(u, "skillxp")), "chat", "R MsgRoute: an unknown answer = chat")
    hud(True, {"skillxp": "feed"})
    S["throw"] = True
    K.eq(str(MR.route(u, "skillxp")), "chat", "R MsgRoute: a throwing SkyyHud = chat")
    hud(True, {"skillxp": "feed"})
    MR.route(u, "skillxp")
    K.check(MR.CACHE.size() == 1, "R MsgRoute: one cache entry")
    MR.forget(u)
    K.check(MR.CACHE.size() == 0, "R MsgRoute: forget(u) drops the player's entries")
    K.check(MR.feed(u, "drop", "Wood_Oak_Trunk", "t", 3) and S["cards"] == [("drop", "Wood_Oak_Trunk", "t", 3)], "R MsgRoute: feed passes kind / icon / text / count")
    K.check(MR.feed(u, "pickup", None, "t2", 0) and S["cards"][-1] == ("pickup", None, "t2", None), "R MsgRoute: count 0 -> null (no x1)")
    S["feed_ok"] = False
    K.check(not MR.feed(u, "drop", None, "t", 1), "R MsgRoute: a refused card -> false")
    K.eq(str(MR.pretty("Plant_Crop_Pumpkin_Item")), "Plant Crop Pumpkin", "R MsgRoute: pretty")

    # ---- SkillMsg.routed vs the 0.4.33 jar
    Lo = T32.loader_for(OLD_JAR, isolated=True)
    OSto, OSM = JClass(PKG + "SkillStore", loader=Lo), JClass(PKG + "SkillMsg", loader=Lo)
    OSto.DIR = JClass("java.nio.file.Paths", loader=Lo).get(pd, JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.String").class_, 0))
    OUUID = JClass("java.util.UUID", loader=Lo)

    def pend(M, uid, vals, n):
        arr = JArray(JLong)(n)
        for i, v in vals.items():
            arr[i] = v
        M.PEND.put(uid, arr)

    N = int(Defs.N)
    hud(True, {"skillxp": "chat"})
    pend(SM, u, {MINING: 40, DIV: 79}, N)
    pend(OSM, u, {MINING: 40, DIV: 79}, N)
    new_line, old_line = SM.routed(u), OSM.take(u)
    K.check(new_line is not None and str(new_line) == str(old_line) and "+40 Mining XP (" in str(new_line),
            "R SkillMsg chat = 0.4.33's line word for word: %s" % new_line)
    K.check(SM.PEND.get(u) is None and SM.LAST.get(u) is not None, "R SkillMsg chat: PEND emptied, LAST stamped")
    hud(False)
    pend(SM, u, {MINING: 7}, N)
    K.check(SM.routed(u) is not None and S["flashes"] == [], "R SkillMsg: an old SkyyHud (no msgroute) = the chat line")
    hud(True, {"skillxp": "feed"})
    pend(SM, u, {MINING: 40, DIV: 79}, N)
    r = SM.routed(u)
    K.check(r is None and sorted(S["flashes"]) == sorted([(NAMES[MINING], 40), ("Divinity", 79)]) and SM.PEND.get(u) is None,
            "R SkillMsg feed: one flash per skill (class skill as SkyyClasses names it), no chat line: %s" % S["flashes"])
    hud(True, {"skillxp": "feed"})
    S["flash_no"] = {NAMES[MINING]}
    pend(SM, u, {MINING: 40, DIV: 79}, N)
    r = SM.routed(u)
    K.check(r is not None and str(r).startswith("+40 Mining XP (") and "Divinity" not in str(r) and len(S["flashes"]) == 2,
            "R SkillMsg feed, Mining refused: only Mining stays in chat: %s" % r)
    hud(True, {"skillxp": "off"})
    pend(SM, u, {MINING: 40}, N)
    o0 = int(MR.OFF.get())
    K.check(SM.routed(u) is None and S["flashes"] == [] and SM.PEND.get(u) is None and int(MR.OFF.get()) == o0 + 1, "R SkillMsg off: nothing, PEND emptied")
    hud(True, {"skillxp": "feed"})
    SM.stage(u, ACRO, 70)
    K.check(SM.routed(u) is None and S["flashes"] == [(NAMES[ACRO], 70)] and SM.STAGE.get(u) is None, "R SkillMsg feed: the staged Acrobatics counter flashes: %s" % S["flashes"])
    K.check(SM.routed(u) is None, "R SkillMsg: nothing pending -> null")

    # ---- PartyXp
    OPX = JClass(PKG + "PartyXp", loader=Lo)
    hud(True, {"skillxp": "chat"})
    PX.add(u, DIV, 6, "Skyy")
    OPX.add(OUUID.fromString(us), DIV, 6, "Skyy")
    a, b = PX.routed(u), OPX.take(OUUID.fromString(us))
    K.check(a is not None and str(a) == str(b) and str(a).startswith("[Party] +6 ") and str(a).endswith("from Skyy's kill"),
            "R PartyXp chat = 0.4.33's line word for word: %s" % a)
    hud(True, {"skillxp": "feed"})
    PX.add(u, DIV, 6, "Skyy")
    PX.add(u, DIV, 4, "Skyy")
    K.check(PX.routed(u) is None and S["flashes"] == [("Divinity", 10)], "R PartyXp feed: one flash (6 + 4): %s" % S["flashes"])
    hud(True, {"skillxp": "feed"})
    S["flash_ok"] = False
    PX.add(u, DIV, 6, "Skyy")
    PX.add(u, DIV, 6, "Skyy")
    r = PX.routed(u)
    K.check(r is not None and "+12 Divinity XP" in str(r) and str(r).endswith("from 2 kills by Skyy"), "R PartyXp feed refused: the [Party] line keeps the source: %s" % r)
    hud(True, {"skillxp": "off"})
    PX.add(u, DIV, 6, "Skyy")
    K.check(PX.routed(u) is None and PX.PEND.get(u) is None and S["flashes"] == [], "R PartyXp off: nothing")

    # ---- double drop / extra potion / tree felled
    SArr, LArr = JArray(JString), JArray(JLong)
    hud(True, {"drop": "feed"})
    K.check(PK.ddFeed(u, SArr(["Wood_Oak_Trunk", None, "Ore_Copper", "A", "B"]), LArr([2, 5, 1, 1, 1]), "Double drop: ")
            and S["cards"] == [("drop", "Wood_Oak_Trunk", "Double drop: Wood Oak Trunk, +3 more", 2)],
            "R FIX ddFeed: ONE card per proc (the item with the most extra, null skipped, +N more): %s" % S["cards"])
    K.check(PK.ddFeed(u, SArr(["Wood_Oak_Trunk"]), LArr([2]), "Double drop: ") and len(S["cards"]) == 2, "R FIX gate: the same item again passes (SkyyHud merges it)")
    K.check(PK.ddFeed(u, SArr(["Wood_Birch_Trunk"]), LArr([1]), "Double drop: ") and len(S["cards"]) == 2,
            "R FIX gate: a NEW item within 1 s is folded away (handled, no card, no chat line)")
    ge = MR.GATE.get("drop|" + us)
    ge[1] = Long.valueOf(int(ge[1]) - 1500)
    K.check(PK.ddFeed(u, SArr(["Wood_Birch_Trunk"]), LArr([1]), "Double drop: ") and len(S["cards"]) == 3 and S["cards"][-1][1] == "Wood_Birch_Trunk",
            "R FIX gate: a new item after 1 s gets its card")
    # FIX 1 burst: a felled tree / sickle = 40 procs over 6 item types in the same instant -> at most ONE new card key (SkyyHud stacks 4)
    hud(True, {"drop": "feed"})
    kinds = ["Wood_Oak_Trunk", "Plant_Leaves_Oak", "Plant_Sapling_Oak", "Plant_Fruit_Apple", "Ingredient_Stick", "Rock_Stone"]
    hb = all(PK.ddFeed(u, SArr([kinds[i % 6]]), LArr([1]), "Double drop: ") for i in range(40))
    K.check(hb and len(set(c[1] for c in S["cards"])) == 1, "R FIX burst: 40 procs over 6 items -> %d card key(s), all handled (never chat)" % len(set(c[1] for c in S["cards"])))
    # FIX 2: a refused card = the chat line, and no other card of that proc was shown (one card per proc - never cards + the line)
    hud(True, {"drop": "feed"})
    S["feed_ok"] = False
    K.check(not PK.ddFeed(u, SArr(["Wood_Oak_Trunk", "Ore_Copper"]), LArr([2, 1]), "Double drop: ") and len(S["cards"]) == 1,
            "R FIX ddFeed refused -> the chat line, after exactly one (refused) card: %s" % S["cards"])
    K.check(not PK.ddFeed(u, SArr([]), LArr([]), "Double drop: "), "R Perks.ddFeed: nothing to show -> the chat line")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    AL = JClass("java.util.ArrayList")
    drops = AL()
    # a bare JVM has no item assets, so new ItemStack(id, q) throws; a stand-in stack = the class allocated without its constructor with
    # the two fields ddFeedList reads (itemId, quantity) - the REAL getItemId / getQuantity / isEmpty run on it
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def stack(iid, q):
        st = U.allocateInstance(IS.class_)
        for f in IS.class_.getDeclaredFields():
            if str(f.getName()) == "itemId":
                f.setAccessible(True)
                f.set(st, iid)
            elif str(f.getName()) == "quantity":
                f.setAccessible(True)
                f.setInt(st, q)
        return st
    try:
        s1 = stack("Wood_Oak_Trunk", 2)
        mk = str(s1.getItemId()) == "Wood_Oak_Trunk" and int(s1.getQuantity()) == 2 and not s1.isEmpty()
        drops.add(s1)
    except Exception as e:
        mk = False
        K.notes.append("stand-in ItemStack failed: %s" % e)
    K.check(mk, "R setup: a stand-in ItemStack (Wood_Oak_Trunk x2) reads back through the real getters")
    hud(True, {"drop": "feed"})
    if mk:
        K.check(PK.ddRoute(u, drops) and S["cards"] == [("drop", "Wood_Oak_Trunk", "Double drop: Wood Oak Trunk", 2)], "R Perks.ddRoute feed: the ItemStack list -> one card: %s" % S["cards"])
    K.check(not PK.ddFeedList(u, AL(), "Double drop: ") and not PK.ddFeedList(u, None, "x"), "R Perks.ddFeedList: empty / null -> chat line")
    hud(True, {"drop": "off"})
    K.check(PK.ddRoute(u, drops) and S["cards"] == [], "R Perks.ddRoute off: handled, no card")
    hud(True, {"drop": "chat"})
    K.check(not PK.ddRoute(u, drops), "R Perks.ddRoute chat: the chat line")
    hud(True, {"drop": "feed"})
    K.check(BR_.potRoute(u, "Potion_Health_Small", 3) and S["cards"] == [("drop", "Potion_Health_Small", "Extra potion: Potion Health Small", 3)],
            "R Brew.potRoute feed: %s" % S["cards"])
    K.check(BR_.potRoute(u, "Potion_Mana_Small", 1) and len(S["cards"]) == 1, "R FIX Brew.potRoute: a NEW item within 1 s is folded away (handled)")
    hud(True, {"drop": "feed"})
    S["feed_ok"] = False
    K.check(not BR_.potRoute(u, "Potion_Health_Small", 3), "R Brew.potRoute refused -> chat")
    hud(True, {"drop": "off"})
    K.check(BR_.potRoute(u, "x", 1) and S["cards"] == [], "R Brew.potRoute off: handled")
    hud(True, {"drop": "chat"})
    K.check(not BR_.potRoute(u, "x", 1), "R Brew.potRoute chat: the chat line")
    hud(True, {"pickup": "feed"})
    K.check(FE.sumFeed(u, 207, 36) and S["cards"] == [("pickup", None, "Tree felled: 207 logs, 36 leaves", None)], "R Fell.sumFeed feed: %s" % S["cards"])
    hud(True, {"pickup": "feed"})
    K.check(FE.sumFeed(u, 1, 0) and S["cards"][-1][2] == "Tree felled: 1 log", "R Fell.sumFeed: 1 log, no leaves")
    S["feed_ok"] = False
    K.check(not FE.sumFeed(u, 3, 1), "R Fell.sumFeed refused -> chat")
    hud(True, {"pickup": "off"})
    K.check(FE.sumFeed(u, 3, 1) and S["cards"] == [], "R Fell.sumFeed off: handled")
    hud(True, {"pickup": "chat"})
    K.check(not FE.sumFeed(u, 3, 1), "R Fell.sumFeed chat: the chat line")

    # ---- SESSION (the 2026-10-11 shape): 75 XP lines, 4 double drops, 1 tree summary over 12 minutes
    def session(defaults):
        hud(defaults is not None, defaults)
        MR.TTL = 2000
        lines, cards, flashes = 0, 0, 0
        sk = [MINING, DIV, ACRO, int(Defs.indexOf("farming")), int(Defs.indexOf("foraging"))]
        for i in range(75):
            pend(SM, u, {sk[i % len(sk)]: 10 + i}, N)
            if SM.routed(u) is not None:
                lines += 1
            if i % 12 == 0:
                MR.CACHE.clear()   # time passes (the 2 s cache)
        for i in range(4):
            if not PK.ddRoute(u, drops):
                lines += 1
        if not FE.sumFeed(u, 207, 36):
            lines += 1
        return lines, len(S["cards"]), len(S["flashes"])
    before = session(None)
    after = session({"skillxp": "feed", "drop": "feed", "pickup": "feed"})
    K.check(before[0] == 80 and after[0] == 0 and after[2] == 75, "R SESSION skills: 80 chat lines without SkyyHud (= 0.4.33), %d with the Feed defaults (%d flashes, %d cards)"
            % (after[0], after[2], after[1]))
    os.makedirs(SESSION, exist_ok=True)
    json.dump({"mod": "SkyySkills " + VERSION, "before": before[0], "after": after[0], "flashes": after[2], "cards": after[1],
               "what": "75 skill XP lines + 4 double drops + 1 tree felled summary"}, open(os.path.join(SESSION, "skills.json"), "w"), indent=1)
    K.notes.append("SESSION skills: before %d chat lines, after %d (%d XP flashes, %d feed cards); MsgRoute %s" % (before[0], after[0], after[2], after[1], MR.stats()))
    K.save()


def run_exec(out, jar, scratch, home):
    T32.SCRATCH = scratch
    return T32.run_exec(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    return T32.run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("route", run_route), ("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
