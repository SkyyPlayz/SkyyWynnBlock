"""SkyySkills 0.4.42 - harness for the FORTUNE INDICATOR (tools/skills_0_4_42_patch.py: the grouped "Fortune!" line of message kind
"fortune", the soft sound, the sparkle at the block; the drop maths untouched).
Build first: python tools/skills_0_4_42_patch.py && python SkyySkills/build_skyyskills_0.4.42.py
             (+ the jars the inherited phases read: SkyySkills-0.4.41.jar / 0.4.40.jar, SkyyTrees/SkyyTrees-0.3.11.jar,
             SkyyRebirth/SkyyRebirth-0.3.3.jar - read only)

    python SkyySkills/test_skyyskills_0.4.42.py [--dir <empty folder inside tools/dev/scratch/>] [--keep] [--no-old]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.41 -> 0.4.42: + Fortune, FortTask; Perks.doubled (the message part only - rolls / extras / fortune / breakDouble /
               harvestDouble / give are IDENTICAL = the drop maths did not change), BreakTask / HarvestTask.run + FellCredit.one (the
               block position), SkSnd (the Fortune sound + sparkle switch), Acro.retainOnline, the plugin's setup / shutdown, the config
               rows + default file, version texts; non-class entries: manifest.json only
  FORT EXECUTED (tools/hub_tab_kit.py engine stand-ins: real PlayerRefs known to Universe.getPlayer, their packets recorded):
      TEXT   the card text / chat line with the item names players see (Fortune.name = SkyySacks' Item translation -> I18nModule en-US
             resolver; the prettified id only without a translation)
      GROUP  hits within 1.5 s merge (one group, biggest item first), a group is due 1.5 s after its last hit or 4 s after its first,
             a new group after it was taken
      ROUTE  deliver(): feed (one card kind fortune, icon, "Fortune! <item>", count = its extra), a refused card = the chat line, the
             player's msg.fortune.feed off = chat, msg.fortune off / perk.doubleDropMessage off = nothing, no SkyyHud + feed = SILENT
      HIT    Fortune.hit on a real PlayerRef: the group opens once (one sound try per group: the Fortune sound id; the per-player
             settings:sounds mute), the sparkle packet (SpawnParticleSystem Block_Break_Treasure) reaches ONLY that player, at most one per
             250 ms, never from a stale / missing block position, nothing at all when the player hides the line; step() sends the group
             (feed card / the chat packet to that player), an offline player's group is dropped
      WIRE   bytecode: doubled -> Fortune.hit (no ddRoute any more); BreakTask / FellCredit / HarvestTask set Fortune.at before their
             breakDouble / harvestDouble; Sickle.award still goes through doubled; Fortune.spark -> ParticleUtil; Acro.retainOnline ->
             Fortune.retain; setup registers msg.fortune + msg.fortune.feed in "messages"; the fresh default file lists the 0.4.42 block
      CFG    SkSnd.read: sound.fortune / sound.fortune.id / fortune.sparkle (defaults when missing)
  0.4.41's phases on the 0.4.42 jar (its HUB phase + every inherited 0.4.40-and-older phase it runs) - the checks pinning 0.4.41's
      version text / the old double-drop line are expected to differ (EXPECTED42 below, each with its reason).
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT

VERSION = "0.4.42"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.41.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "skills0442", "sk")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySkills")
os.environ.setdefault("SKYYROUTE_SESSION", os.path.join(SCRATCH, "routesession"))
EXPECT = {
    "Perks": ["~m doubled"],                                   # the message part -> Fortune.hit
    "BreakTask": ["~m run"], "HarvestTask": ["~m run"], "FellCredit": ["~m one"],   # Fortune.at (the sparkle's block)
    "SkSnd": ["+f FORT", "+f FORT_ID", "+f SPARKLE", "+m fortune", "~<clinit>", "~m read", "~m text"],
    "Acro": ["~m retainOnline"],                               # Fortune.retain
    "SkyySkillsPlugin": ["~m setup", "~m shutdown"],           # the two settings, the ready line; shutdown clears the groups
    # the default file (0.4.42 block, header version), the kit's rows (3 new + 2 texts), version texts
    "SkillCfg": ["~m load"], "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"], "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"],
}
ADDED = ["Fortune", "FortTask"]
SND, FX = "SFX_Crops_Grow_Stage_Complete", "Block_Break_Treasure"


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_EQ0 = HK.Child.eq
T41 = tmod("test_skyyskills_0.4.41.py", "t0441")
HK.Child.eq = _EQ0   # 0.4.41's harness widens the compare to its 59 new kit files (--phase compare); 0.4.41 -> 0.4.42 changes manifest.json only


def run_fort(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString, JLong
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    J = lambda n: JClass(PKG + n)
    F, FT, MR, SS, PC, Cfg, Sto = J("Fortune"), J("FortTask"), J("MsgRoute"), J("SkSnd"), J("PerkCfg"), J("SkillCfg"), J("SkillStore")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    Bool, UUID, AL = JClass("java.lang.Boolean"), JClass("java.util.UUID"), JClass("java.util.ArrayList")
    SArr = lambda xs: JArray(JString)(list(xs))
    LArr = lambda xs: JArray(JLong)(list(xs))
    F.MANUAL = True
    br = E.bridge
    K.check(E.same(MR.br(), br) and E.same(Sto.bridge(), br), "setup: Fortune / MsgRoute / SkillStore share ONE bridge map")

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    S = {"set": {}, "cards": [], "feed_ok": True}

    def f_get(o):
        v = S["set"].get(str(o[1]))
        return None if v is None else (Bool.TRUE if v else Bool.FALSE)

    def f_feed(o):
        S["cards"].append((str(o[1]), None if o[2] is None else str(o[2]), str(o[3]), None if o[4] is None else int(o[4])))
        return Bool.TRUE if S["feed_ok"] else Bool.FALSE
    FG, FF = Fn(f_get), Fn(f_feed)

    def env(hud=True, settings=True, sets=None, feed_ok=True):
        for k in ("settings:fn:get", "feed:fn:push"):
            br.remove(k)
        if settings:
            br.put("settings:fn:get", FG)
        if hud:
            br.put("feed:fn:push", FF)
        S["set"], S["cards"], S["feed_ok"] = dict(sets or {}), [], feed_ok
        F.GRP.clear()
        F.POS.clear()
        F.SPK.clear()
        MR.CACHE.clear()
        MR.GATE.clear()
        PC.DD_MSG = True

    # stand-in ItemStacks (a bare JVM has no item assets; the 0.4.34 harness recipe: allocated, itemId + quantity set, the REAL getters)
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
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

    def drops(*pairs):
        l = AL()
        for iid, q in pairs:
            l.add(stack(iid, q))
        return l
    d0 = drops(("Wood_Oak_Trunk", 1))
    K.check(str(d0.get(0).getItemId()) == "Wood_Oak_Trunk" and int(d0.get(0).getQuantity()) == 1, "setup: a stand-in ItemStack reads back")

    # ---------------------------------------------------------------- TEXT (item names: Item translation -> I18nModule en-US; this bare JVM has
    # no item assets / translations, so name() falls back to the prettified id - a seeded NAMES cache stands in for the translated names)
    F.NAMES.clear()
    K.eq(str(F.name("Skyy_Nope_Item")), "Skyy Nope", "TEXT name(): an item without a translation = the prettified id")
    K.check(str(F.NAMES.get("Skyy_Nope_Item")) == "Skyy Nope", "TEXT name(): cached")
    F.NAMES.put("Wood_Oak_Trunk", "Oak Log")
    F.NAMES.put("Ingredient_Stick", "Stick")
    K.eq(str(F.cardText(SArr(["Wood_Oak_Trunk", "Ingredient_Stick"]))), "Fortune! Oak Log, +1 more", "TEXT card uses the name players see (Oak Log)")
    K.eq(str(F.chatLine(SArr(["Wood_Oak_Trunk", "Ingredient_Stick"]), LArr([5, 1]))), "Fortune! +5 Oak Log, +1 Stick", "TEXT chat line uses the names players see")
    F.NAMES.clear()
    g0 = PW.calls(jar)
    K.check("com.hypixel.hytale.server.core.asset.type.item.config.Item.getTranslationKey" in g0.get("Fortune.name", set())
            and "com.hypixel.hytale.server.core.modules.i18n.I18nModule.getMessage" in g0.get("Fortune.name", set())
            and PKG + "Fortune.name" in g0.get("Fortune.cardText", set()) and PKG + "Fortune.name" in g0.get("Fortune.chatLine", set()),
            "TEXT name() = SkyySacks' resolver (Item.getTranslationKey -> I18nModule.getMessage), used by the card and the chat line")
    import serverjar   # the cached Assets.zip copy (never the installed file)
    with zipfile.ZipFile(serverjar.assets_zip()) as za:
        lang = za.read("Server/Languages/en-US/server.lang").decode("utf8", "replace")
    K.check("items.Wood_Oak_Trunk.name = Oak Log" in lang and "items.Ore_Copper.name = Copper Ore" in lang,
            "TEXT the game's en-US names the resolver returns in game: Wood_Oak_Trunk = Oak Log, Ore_Copper = Copper Ore")
    K.eq(str(F.cardText(SArr(["Wood_Oak_Trunk"]))), "Fortune! Wood Oak Trunk", "TEXT card, one item")
    K.eq(str(F.cardText(SArr(["Wood_Oak_Trunk", "Ingredient_Stick"]))), "Fortune! Wood Oak Trunk, +1 more", "TEXT card, two items")
    K.eq(str(F.chatLine(SArr(["Wood_Oak_Trunk", "Ingredient_Stick"]), LArr([5, 1]))), "Fortune! +5 Wood Oak Trunk, +1 Ingredient Stick", "TEXT chat line")
    K.eq(str(F.chatLine(SArr(["A", "B", "C", "D", "E"]), LArr([5, 4, 3, 2, 1]))), "Fortune! +5 A, +4 B, +3 C, +2 more", "TEXT chat line: 3 items + more")
    K.eq(str(F.chatLine(SArr(["Plant_Crop_Pumpkin_Item"]), LArr([2]))), "Fortune! +2 Plant Crop Pumpkin", "TEXT chat line: the _Item tail goes")

    # ---------------------------------------------------------------- GROUP
    env()
    u = UUID.fromString("00000000-0000-4000-8000-000000000442")
    t0 = 1000000
    K.eq(int(F.hitU(u, d0, t0)), 1, "GROUP the first proc opens a group")
    K.eq(int(F.hitU(u, drops(("Wood_Oak_Trunk", 1)), t0 + 500)), 0, "GROUP a proc 0.5 s later joins it")
    K.eq(int(F.hitU(u, drops(("Ingredient_Stick", 1), ("Wood_Oak_Trunk", 2)), t0 + 900)), 0, "GROUP two items 0.9 s later join it")
    K.eq(int(F.hitU(u, AL(), t0 + 950)), -1, "GROUP an empty list adds nothing")
    K.eq(int(F.hitU(u, drops(("Wood_Oak_Trunk", 0)), t0 + 950)), -1, "GROUP a 0-quantity stack adds nothing")
    K.eq(int(F.due(u, t0 + 1000)), 1400, "GROUP due 1.5 s after the LAST hit (1400 ms left)")
    K.eq(int(F.due(u, t0 + 2400)), 0, "GROUP due now")
    tk = F.take(u)
    K.check(tk is not None and [str(x) for x in tk[0]] == ["Wood_Oak_Trunk", "Ingredient_Stick"] and [int(x) for x in tk[1]] == [4, 1],
            "GROUP take: 4 Wood Oak Trunk + 1 stick, biggest first (%s)" % str(None if tk is None else ([str(x) for x in tk[0]], [int(x) for x in tk[1]])))
    K.check(F.take(u) is None and int(F.due(u, t0)) == -1, "GROUP taken = gone")
    for k in range(6):   # a proc every second (fast mining): the group is due 4 s after its first hit at the latest
        F.hitU(u, d0, t0 + 1000 * k)
    K.eq(int(F.due(u, t0 + 4000)), 0, "GROUP non-stop procs: due at MAX_AGE (4 s after the first) - a line every ~4 s, never none")
    F.take(u)
    K.eq(int(F.hitU(u, d0, t0 + 6000)), 1, "GROUP after a take the next proc opens a NEW group (= one sound per group)")
    F.GRP.clear()

    # ---------------------------------------------------------------- ROUTE (deliver, pr null = no chat packet)
    ids, qs = SArr(["Wood_Oak_Trunk", "Ingredient_Stick"]), LArr([4, 1])
    said = AL()
    MR.SAID = said
    env()
    K.eq(str(F.deliver(u, None, ids, qs)), "feed", "ROUTE default (no SkyyMenu answer): feed")
    K.check(S["cards"] == [("fortune", "Wood_Oak_Trunk", "Fortune! Wood Oak Trunk, +1 more", 4)] and said.size() == 0,
            "ROUTE feed: ONE card kind fortune, the item's icon, its extra as the count, no chat line: %s" % S["cards"])
    env(feed_ok=False)
    K.check(str(F.deliver(u, None, ids, qs)) == "chat" and len(S["cards"]) == 1 and said.size() == 1 and str(said.get(0)) == "Fortune! +4 Wood Oak Trunk, +1 Ingredient Stick",
            "ROUTE SkyyHud refused the card (Feed widget off) -> the chat line: %s" % (list(said),))
    said.clear()
    env(sets={"msg.fortune.feed": False})
    K.check(str(F.deliver(u, None, ids, qs)) == "chat" and S["cards"] == [] and said.size() == 1, "ROUTE the player's feed switch off -> chat, no card")
    said.clear()
    env(sets={"msg.fortune": False})
    K.check(str(F.deliver(u, None, ids, qs)) == "off" and S["cards"] == [] and said.size() == 0, "ROUTE the player's show switch off -> nothing")
    env()
    PC.DD_MSG = False
    K.check(str(F.deliver(u, None, ids, qs)) == "off" and S["cards"] == [] and said.size() == 0, "ROUTE perk.doubleDropMessage false -> nothing")
    env(hud=False)
    K.check(str(F.deliver(u, None, ids, qs)) == "none" and said.size() == 0, "ROUTE no SkyyHud + feed wanted -> SILENT (no chat line)")
    env(hud=False, sets={"msg.fortune.feed": False})
    K.check(str(F.deliver(u, None, ids, qs)) == "chat" and said.size() == 1, "ROUTE no SkyyHud + the player chose chat -> the chat line")
    said.clear()
    env(hud=False, settings=False)
    K.check(str(F.deliver(u, None, ids, qs)) == "none" and said.size() == 0, "ROUTE no SkyyHud, no SkyyMenu -> silent")
    MR.SAID = None

    # ---------------------------------------------------------------- HIT on real PlayerRefs (packets recorded)
    P = E.mkp(UUID.fromString("00000000-0000-4000-8000-0000000004a1"), "FortA")
    Q = E.mkp(UUID.fromString("00000000-0000-4000-8000-0000000004a2"), "FortB")
    pu = P.pr.getUuid()

    def particles(X, frm=0):
        return [i for i, k in enumerate(E.kinds(X)) if k == "SpawnParticleSystem" and i >= frm]
    env()
    SS.WARNED.clear()
    p0, q0 = len(E.sent(P)), len(E.sent(Q))
    F.at(pu, 10, 64, -3)
    F.hit(P.pr, drops(("Ore_Copper", 2)))
    K.check(F.GRP.containsKey(pu) and int(F.GROUPS.get()) >= 1, "HIT a proc opens the player's group")
    K.check(SS.WARNED.containsKey(SND), "HIT the group's sound is the Fortune sound %s (tried; this bare JVM has no SoundEvent map)" % SND)
    pp = particles(P, p0)
    K.check(len(pp) == 1 and FX in E.strs_of(P, pp[0]) and len(particles(Q, q0)) == 0,
            "HIT the sparkle (SpawnParticleSystem %s) reaches ONLY that player (P %d, Q %d)" % (FX, len(pp), len(particles(Q, q0))))
    sp = E.sent(P)[pp[0]] if pp else None
    if sp is not None:
        txt = []
        for fld in sp.getClass().getDeclaredFields():
            fld.setAccessible(True)
            txt.append("%s=%s" % (fld.getName(), fld.get(sp)))
        K.notes.append("HIT the sparkle packet: " + ", ".join(txt))
        pos = [f for f in sp.getClass().getDeclaredFields() if str(f.getName()) == "position"]
        if pos:
            pos[0].setAccessible(True)
            pv = pos[0].get(sp)
            K.check(abs(float(pv.x) - 10.5) < 1e-6 and abs(float(pv.y) - 64.5) < 1e-6 and abs(float(pv.z) + 2.5) < 1e-6, "HIT the sparkle sits on the block centre (10.5, 64.5, -2.5): %s" % pv)
        sc = [f for f in sp.getClass().getDeclaredFields() if str(f.getName()) == "scale"]
        if sc:
            sc[0].setAccessible(True)
            K.check(abs(float(sc[0].get(sp)) - 0.6) < 1e-6, "HIT the sparkle is drawn at 0.6 scale")
    w0 = SS.WARNED.size()
    p1 = len(E.sent(P))
    F.at(pu, 11, 64, -3)
    F.hit(P.pr, drops(("Ore_Copper", 1)))
    K.check(len(particles(P, p1)) == 0 and SS.WARNED.size() == w0 and int(F.GRP.get(pu)[1][1]) > 0,
            "HIT a second proc right after: joins the group, no second sound try, no sparkle within 250 ms")
    F.SPK.clear()
    p2 = len(E.sent(P))
    F.at(pu, 12, 64, -3)
    F.hit(P.pr, drops(("Ore_Copper", 1)))
    K.eq(len(particles(P, p2)), 1, "HIT after the 250 ms gap the next proc sparkles again")
    F.SPK.clear()
    p3 = len(E.sent(P))
    F.POS.put(pu, JArray(JClass("double"))([1.0, 2.0, 3.0, 1.0]))   # set long ago
    F.hit(P.pr, drops(("Ore_Copper", 1)))
    F.hit(P.pr, drops(("Ore_Copper", 1)))   # no position at all (a sickle swing)
    K.check(len(particles(P, p3)) == 0 and F.POS.isEmpty(), "HIT a stale (> 100 ms) or missing block position: no sparkle, the position is used once")
    # step: the group goes to the feed, then it is gone
    S["cards"] = []
    g = F.GRP.get(pu)
    first = int(g[1][0])
    K.check(int(F.step(pu, first + 100)) > 0, "HIT step before the group is due -> the wait left")
    K.check(int(F.step(pu, first + 10000)) == -1 and S["cards"] == [("fortune", "Ore_Copper", "Fortune! Ore Copper", 6)] and not F.GRP.containsKey(pu),
            "HIT step when due: ONE card 'Fortune! Ore Copper' x6 (the 5 procs: 2 + 1 + 1 + 1 + 1), the group is gone: %s" % S["cards"])
    # the chat path through step: the line is a packet to THAT player
    env(sets={"msg.fortune.feed": False})
    F.hit(P.pr, drops(("Wood_Oak_Trunk", 3)))
    c0, cq = len(E.sent(P)), len(E.sent(Q))
    F.step(pu, int(F.GRP.get(pu)[1][0]) + 10000)
    K.check("Fortune! +3 Wood Oak Trunk" in E.strs_of(P, c0) and "Fortune!" not in E.strs_of(Q, cq), "HIT chat: 'Fortune! +3 Wood Oak Trunk' goes to that player only")
    # the player's mute + hidden line
    env()
    SS.WARNED.clear()
    m0 = int(SS.MUTED.get())
    br.put("settings:sounds:" + str(pu), Bool.FALSE)
    F.hit(P.pr, drops(("Ore_Copper", 1)))
    K.check(int(SS.MUTED.get()) == m0 + 1 and not SS.WARNED.containsKey(SND), "HIT settings:sounds:<uuid> FALSE (the player's sound switch) mutes the Fortune sound")
    br.remove("settings:sounds:" + str(pu))
    env(sets={"msg.fortune": False})
    SS.WARNED.clear()
    p4 = len(E.sent(P))
    F.at(pu, 1, 2, 3)
    F.hit(P.pr, drops(("Ore_Copper", 1)))
    K.check(not F.GRP.containsKey(pu) and len(particles(P, p4)) == 0 and not SS.WARNED.containsKey(SND), "HIT the player hid the line: no group, no sound, no sparkle")
    env(sets={"skills.doubleDrop": False})
    F.hit(P.pr, drops(("Ore_Copper", 1)))
    K.check(not F.GRP.containsKey(pu), "HIT the old skills.doubleDrop switch still hides it")
    env()
    SS.SPARKLE = False
    F.at(pu, 1, 2, 3)
    p5 = len(E.sent(P))
    F.hit(P.pr, drops(("Ore_Copper", 1)))
    K.check(F.GRP.containsKey(pu) and len(particles(P, p5)) == 0, "HIT fortune.sparkle false: the line + sound stay, no sparkle")
    SS.SPARKLE = True
    # a player who left before the group was due: dropped, nothing sent
    ghost = UUID.fromString("00000000-0000-4000-8000-0000000004ff")
    F.hitU(ghost, d0, 5)
    S["cards"] = []
    K.check(int(F.step(ghost, 100000)) == -1 and not F.GRP.containsKey(ghost) and S["cards"] == [], "HIT an offline player's group is dropped")
    FT(ghost).run()   # nothing open: no reschedule, no exception
    online = JClass("java.util.HashSet")()
    F.hitU(ghost, d0, 5)
    F.retain(online)
    K.check(F.GRP.isEmpty() and F.POS.isEmpty() and F.SPK.isEmpty(), "HIT retain(online) drops the groups of players who left")
    K.notes.append("Fortune " + str(F.stats()))

    # ---------------------------------------------------------------- WIRE (bytecode)
    g = PW.calls(jar)
    has = lambda m, c: PKG + c in g.get(m, set())
    K.check(has("Perks.doubled", "Fortune.hit") and not has("Perks.doubled", "Perks.ddRoute") and has("Perks.doubled", "Perks.give"),
            "WIRE Perks.doubled: give() as before, then Fortune.hit (the old ddRoute / chat line gone)")
    for m, c in (("BreakTask.run", "Perks.breakDouble"), ("FellCredit.one", "Perks.breakDouble"), ("HarvestTask.run", "Perks.harvestDouble")):
        K.check(has(m, "Fortune.at") and has(m, c), "WIRE %s sets Fortune.at (the block) and still calls %s" % (m, c))
    K.check(has("Sickle.award", "Perks.doubled") and has("Perks.breakDouble", "Perks.doubled") and has("Perks.harvestDouble", "Perks.doubled"),
            "WIRE every gathering path (breaks, felled trees, F-harvests, sickle swings) reaches doubled -> the indicator")
    K.check(has("Fortune.hit", "SkSnd.fortune") and has("Fortune.hit", "Fortune.spark") and has("Fortune.hit", "Fortune.sched"),
            "WIRE Fortune.hit: the sound, the sparkle, the task")
    K.check("com.hypixel.hytale.server.core.universe.world.ParticleUtil.spawnParticleEffect" in g.get("Fortune.spark", set()), "WIRE Fortune.spark -> ParticleUtil")
    K.check(has("FortTask.run", "Fortune.step") and has("Fortune.step", "Fortune.deliver") and has("Acro.retainOnline", "Fortune.retain"),
            "WIRE FortTask -> step -> deliver; Acro.retainOnline -> Fortune.retain")
    z = zipfile.ZipFile(jar)
    plug = z.read("com/skyy/skills/SkyySkillsPlugin.class")
    K.check(b"msg.fortune.feed" in plug and b"msg.fortune" in plug and b"Fortune drops: in the feed (off = chat)" in plug and b"messages" in plug,
            "WIRE setup registers msg.fortune + msg.fortune.feed in the Messages tab")
    cfgc = b"".join(z.read(n) for n in z.namelist() if n.startswith("com/skyy/skills/SkillCfg") and n.endswith(".class"))
    K.check(b"sound.fortune.id=" + SND.encode() in cfgc and b"fortune.sparkle=true" in cfgc, "WIRE the fresh xp.properties lists the 0.4.42 block")
    # ---------------------------------------------------------------- CFG
    Props = JClass("java.util.Properties")
    p = Props()
    SS.read(p)
    K.check(bool(SS.FORT) and str(SS.FORT_ID) == SND and bool(SS.SPARKLE), "CFG missing keys = the defaults (sound on, %s, sparkle on)" % SND)
    p.setProperty("sound.fortune", "false")
    p.setProperty("sound.fortune.id", "SFX_Coins_Land")
    p.setProperty("fortune.sparkle", "false")
    SS.read(p)
    K.check(not bool(SS.FORT) and str(SS.FORT_ID) == "SFX_Coins_Land" and not bool(SS.SPARKLE), "CFG the three keys are read")
    K.check(SS.pick(True, False, "SFX_Coins_Land") is None, "CFG sound.fortune false = no Fortune sound")
    SS.read(Props())
    K.check("Fortune " + SND in str(SS.text()), "CFG the ready line names the Fortune sound: %s" % SS.text())
    SS.LAST.clear()
    K.check(bool(SS.gate("u|fortune", 1000)) and not bool(SS.gate("u|fortune", 1400)) and bool(SS.gate("u|level", 1400)) and bool(SS.gate("u|fortune", 1500)),
            "CFG the sound gate with fixed times: one Fortune sound per 0.5 s per player, other sounds keep their own slot")
    SS.LAST.clear()
    K.save()


# 0.4.41's phases on this jar: the checks pinning the older row count - with why
T41.EXPECTED41.extend([
    ("G sound: a second level-up sting within 0.5 s is skipped", "timing only: in a cold -Xverify:all JVM the FIRST PlaySoundEvent2D took ~690 ms "
     "(measured 2026-10-15), longer than the 0.5 s gate itself; SkSnd.gate is unchanged (C: identical) and FORT CFG checks it with fixed times"),
    ("G sound: Overall level up first = the skill sting skipped", "the same cold-JVM timing (the stamp of the line above); FORT CFG checks the gate"),
    ("G ROWS: the Sounds category, 249 rows (241 + 8)", "0.4.42: 252 rows (+ sound.fortune, sound.fortune.id, fortune.sparkle - the build asserts them, FORT CFG reads them)"),
])
# the inherited G38 / START TWICE (live) phases load SkyySkills-0.4.37.jar as their control; tools/tidy_local.py archived it
# (backups/archive/old-jars-*.tar.xz, read only): the parent extracts that one jar next to the scratch folder (SKYY_OLD_JAR_DIR, inherited by
# the child phases) and removes it at the end
OLD37 = "SkyySkills-0.4.37.jar"
OLD_DIR = SCRATCH + "-old"


def _old37():
    if os.path.isfile(os.path.join(HERE, OLD37)):
        return
    d = os.environ.get("SKYY_OLD_JAR_DIR")
    if not d and "--phase" not in sys.argv:
        import tarfile
        arch = os.path.join(ROOT, "backups", "archive")
        for a in sorted(os.listdir(arch) if os.path.isdir(arch) else [], reverse=True):
            if not (a.startswith("old-jars-") and a.endswith(".tar.xz")):
                continue
            with tarfile.open(os.path.join(arch, a), "r:xz") as t:
                m = [x for x in t.getmembers() if x.isfile() and x.name == "SkyySkills/" + OLD37]
                if m:
                    os.makedirs(OLD_DIR, exist_ok=True)
                    open(os.path.join(OLD_DIR, OLD37), "wb").write(t.extractfile(m[0]).read())
                    d = OLD_DIR
                    os.environ["SKYY_OLD_JAR_DIR"] = d
                    break
    if d and os.path.isfile(os.path.join(d, OLD37)):
        T41.T38.OLD_JAR = os.path.join(d, OLD37)


_old37()

if __name__ == "__main__":
    phases = [("fort", run_fort)]
    if "--no-old" not in sys.argv:
        phases += [("hub", T41.run_hub)] + [(k, T41.wrap41(f)) for k, f in T41.OLD_PHASES]
    try:
        HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
               phases=phases, script=__file__, live=(LIVE_DIR, "Skyy_SkyySkills"))
    finally:
        if "--phase" not in sys.argv and os.path.isdir(OLD_DIR):
            import shutil
            shutil.rmtree(OLD_DIR, ignore_errors=True)
