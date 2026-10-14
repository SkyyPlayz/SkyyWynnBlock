"""Harness for SkyyCollections 0.2.12 (CHAT OVERFLOW -> FEED + COLLECTION LEVEL-UP RECIPES; tools/collections_0_2_12_patch.py, the shared
tools/skyyroute.py MsgRoute). Also adds up the SESSION measurement of all three sender mods (SkyySkills 0.4.34 + SkyyClasses 0.1.20
harnesses write their part first).
Build first: python tools/collections_0_2_12_patch.py && python SkyyCollections/build_skyycollections_0.2.12.py

    python SkyyCollections/test_skyycollections_0.2.12.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises
  C   compare  0.2.11 -> 0.2.12: exactly the listed members differ; MsgRoute / CollMsg / CollNew added; non-class entries: manifest only
  J   test_skyycollections_0.2.11.py's asset-pack phase on the 0.2.12 jar (the Enchanted pack is byte-identical)
  X   test_skyycollections_0.2.11.py's exec phase on the 0.2.12 jar (every 0.2.11 path still holds)
  R   route    EXECUTED (registry from the default files in scratch, recipes from rewards.properties, a stand-in SkyyHud on the bridge):
               CollMsg.craftQ == CollCraft.query on EVERY tier of the registry (the /craft words 0.2.8's CRAFT button runs); rankParts /
               text / message for a recipe tier (craft on: "/craft <words>", off: "/collections <name>"), a tier without recipes (no
               command), the rewards (coins + skill XP = 0.2.11's rewardLines numbers), rarityHex fallback + hex(Color) + Mythic swap;
               cardText, icon, progText (next tier / max); progress for every route (feed card with the item icon + count; chat / off /
               refused / no SkyyHud = nothing, never a chat line); announce for every route (off: nothing; feed: a rankup card; feed
               refused + chat: the one line recorded through MsgRoute.SAID before the stub player's send);
               CollNew: mark (only tiers with recipes, not bought ones, from..to), isNew, seen; creditOne(offline) across a tier marks NEW
               on the profile's data and makes it dirty; the counts file written by save() carries "_new.<id>" and 0.2.11's fromProps
               reads it back (rollback safe);
               CollPage (a stand-in PlayerRef): buildDetail shows "NEW" in the marked tier's state cell, then the markers are gone (seen);
               unlockedRows puts "NEW  " before a marked recipe;
               SESSION: the 2026-10-11 rank-ups (Raw Wildmeat II, Essence of Life III, Bone Fragments I) old line count (1 + 0.2.11's
               reward lines + its recipe line) vs 0.2.12 (one line); then ALL MODS: the 116-line session -> lines per minute before / after
  D   test_skyycollections_0.2.11.py's live phase on the 0.2.12 jar: START TWICE on a scratch COPY of the live Skyy_SkyyCollections
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.2.12"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.11.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "msgroute", "co")))
SESSION = os.environ.get("SKYYROUTE_SESSION") or os.path.join(ROOT, "tools", "dev", "scratch", "msgroute", "session")
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyCollections")
LOG_LINES, LOG_MINUTES = 116, 12.0          # the 2026-10-11 session (docs/answered/ui.md CHAT OVERFLOW measurement)
EXPECT = {
    "CollCredit": ["~m announce", "~m creditOne"],
    "CollPage": ["~m buildDetail", "~m unlockedRows"],
    "SkyyCollectionsPlugin": ["~m setup"],   # version texts (ready line, pack name, page id)
    "CfgFn": ["~m opExport"],
    "CfgRows": ["~m header"],
}
ADDED = ["CollMsg", "CollNew", "MsgRoute"]


T11 = None


def _t11():
    """test_skyycollections_0.2.11.py's functions WITHOUT its last two statements (it runs HK.run at import - no __main__ guard)"""
    global T11
    if T11 is None:
        fp = os.path.join(HERE, "test_skyycollections_0.2.11.py")
        src = open(fp, encoding="utf8").read()
        cut = src.index(chr(10) + "HK.run_compare = _compare" + chr(10))
        mod = types.ModuleType("t0211")
        mod.__file__ = fp
        exec(compile(src[:cut], fp, "exec"), mod.__dict__)
        T11 = mod
    T11.VERSION = VERSION
    return T11


def run_route(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    P = lambda n: JClass(PKG + n)
    MR, Msg, New, Reg, Store, Util, Craft, Cred, Unl, Page, Data = (P("MsgRoute"), P("CollMsg"), P("CollNew"), P("CollReg"), P("CollStore"),
                                                                   P("CollUtil"), P("CollCraft"), P("CollCredit"), P("CollUnlocks"),
                                                                   P("CollPage"), P("CollData"))
    Paths, HashMap, HashSet, UUID, Bool, Long = (JClass("java.nio.file.Paths"), JClass("java.util.HashMap"), JClass("java.util.HashSet"),
                                                 JClass("java.util.UUID"), JClass("java.lang.Boolean"), JClass("java.lang.Long"))
    bridge = Util.bridge()

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)

    S = {"route": {}, "ok": True, "cards": []}

    def f_route(o):
        return S["route"].get(str(o[1]), "chat")

    def f_feed(o):
        S["cards"].append((str(o[1]), None if o[2] is None else str(o[2]), str(o[3]), None if o[4] is None else int(o[4])))
        return Bool.TRUE if S["ok"] else Bool.FALSE
    FR, FF = Fn(f_route), Fn(f_feed)

    def hud(on=True, route=None):
        for k in ("msgroute:fn:get", "feed:fn:push"):
            bridge.remove(k)
        if on:
            bridge.put("msgroute:fn:get", FR)
            bridge.put("feed:fn:push", FF)
        S["route"], S["ok"], S["cards"] = dict(route or {}), True, []
        MR.CACHE.clear()
        MR.GATE.clear()
        Msg.PEND.clear()

    # ---- registry in scratch; recipes from rewards.properties (a bare JVM has no recipe assets - the 0.2.8 harness's way)
    wbase = os.path.join(scratch, "r", "Skyy_SkyyCollections")
    os.makedirs(wbase)
    Reg.BASE = Paths.get(wbase)
    Store.DIR = Paths.get(wbase).resolve("counts")
    Reg.loadAll()
    R = Reg.D
    rec = HashMap()
    for c in range(R.n):
        for t in range(1, int(Reg.maxTier(R, c)) + 1):
            toks = Reg.REWARDS.get(str(R.id[c]).lower() + "." + str(t))
            if toks is None:
                continue
            ids = [str(x)[7:].strip() for x in toks if str(x).startswith("recipe:")]
            if ids:
                rec.put("%d.%d" % (c, t), JArray(JString)(ids))
    Reg.RECIPES = rec
    Reg.VALIDATED = True
    VIS = [c for c in range(R.n) if not R.hidden[c]]
    K.check(len(VIS) > 50 and rec.size() > 20, "R setup: %d visible collections, %d recipe tiers" % (len(VIS), rec.size()))

    # ---- craftQ == CollCraft.query on every tier
    bad, n_t = [], 0
    for c in range(R.n):
        for t in range(1, int(Reg.maxTier(R, c)) + 1):
            rs = Reg.recipesAt(c, t)
            if len(rs) == 0:
                continue
            n_t += 1
            hs = HashSet()
            for x in rs:
                hs.add(x)
            a, b = Msg.craftQ(rs), Craft.query(rs, hs)
            if (None if a is None else str(a)) != (None if b is None else str(b)):
                bad.append((str(R.id[c]), t, a, b))
    K.check(not bad and n_t > 20, "R craftQ = CollCraft.query on all %d recipe tiers (the /craft words 0.2.8's CRAFT button runs): %s" % (n_t, bad[:3]))

    # ---- rankParts / text / message
    rc = [(c, t) for c in VIS for t in range(1, int(Reg.maxTier(R, c)) + 1) if len(Reg.recipesAt(c, t)) > 0]
    c1, t1 = rc[0]
    ps = Msg.rankParts(R, c1, t1, True)
    tx = str(Msg.text(ps))
    rl = [str(x) for x in Reg.rewardLines(R, c1, t1)]
    names = [str(Util.prettyRecipe(r)) for r in Reg.recipesAt(c1, t1)]
    K.check(tx.startswith("COLLECTION UP  %s %s  New: " % (R.name[c1], Util.roman(t1))) and all(n in tx for n in names)
            and tx.endswith("  /craft " + str(Msg.craftQ(Reg.recipesAt(c1, t1)))), "R rankParts (craft on): %s" % tx)
    nums = [x for x in rl if not x.endswith(" recipe") and " recipe (" not in x]
    K.check(all(x in tx for x in nums), "R rankParts: the coins / skill XP = 0.2.11's reward lines %s" % nums)
    K.check(str(ps.get(0)[1]) == "#ffc800" and all(str(p[1]) == "#c8f0a0" for p in ps if str(p[0]) in names), "R rankParts colours: header gold, recipe names = rarity (bare JVM fallback green)")
    tx2 = str(Msg.text(Msg.rankParts(R, c1, t1, False)))
    K.check(tx2.endswith("  /collections " + str(R.name[c1]).replace(" ", "").lower()), "R rankParts (no /craft): ends with /collections <name>: %s" % tx2)
    K.eq(int(Reg.find(str(R.name[c1]).replace(" ", "").lower())), c1, "R the /collections word finds that collection")
    nr = [(c, t) for c in VIS for t in range(1, int(Reg.maxTier(R, c)) + 1) if len(Reg.recipesAt(c, t)) == 0]
    c0, t0 = nr[0]
    tx0 = str(Msg.text(Msg.rankParts(R, c0, t0, True)))
    K.check("New:" not in tx0 and "/craft" not in tx0 and "/collections" not in tx0, "R rankParts without recipes: no list, no command: %s" % tx0)
    m = Msg.message(ps)
    K.check(str(m.getRawText()) == str(ps.get(0)[0]) and m.getChildren().size() == ps.size() - 1, "R message: root + %d coloured children" % (ps.size() - 1))
    K.eq(str(Msg.rarityHex("No_Such_Item_Recipe_Generated_0")), "#c8f0a0", "R rarityHex: an unknown item = 0.2.11's recipe green")
    K.eq(str(Msg.outId("Food_Bread_Recipe_Generated_2")), "Food_Bread", "R outId")
    Col = JClass("com.hypixel.hytale.protocol.Color")
    try:
        col = Col()
        col.red, col.green, col.blue = -86, 0, -86   # bytes: 0xAA 0x00 0xAA
        K.eq(str(Msg.hex(col)).upper(), "#AA00AA", "R hex(Color) reads unsigned bytes")
    except Exception as e:
        K.notes.append("Color stand-in: %s" % e)
    K.eq(str(Msg.cardText(R, c1, t1)), "%s %s - %s%s" % (R.name[c1], Util.roman(t1), Util.clip(names[0], 28), ", +%d" % (len(names) - 1) if len(names) > 1 else ""),
         "R FIX cardText names the first recipe (+N for the rest)")
    cm = [(c, t) for c, t in rc if len(Reg.recipesAt(c, t)) > 1]
    if cm:
        cx, tx_ = cm[0]
        nx = [str(Util.prettyRecipe(r)) for r in Reg.recipesAt(cx, tx_)]
        K.check(str(Msg.cardText(R, cx, tx_)).endswith(", +%d" % (len(nx) - 1)) and str(Util.clip(nx[0], 28)) in str(Msg.cardText(R, cx, tx_)),
                "R FIX cardText with %d recipes: %s" % (len(nx), Msg.cardText(R, cx, tx_)))
    else:
        K.notes.append("no tier with 2+ recipes in the registry")
    K.eq(str(Msg.cardText(R, c0, t0)), "%s %s" % (R.name[c0], Util.roman(t0)), "R cardText without recipes")
    R.iconOk[c1] = True
    K.eq(str(Msg.icon(R, c1)), str(R.icon[c1]), "R icon: the collection icon when it is an item")
    R.iconOk[c1] = False
    K.check(Msg.icon(R, c1) is None, "R icon: none when it is no item")
    mx1 = int(Reg.maxTier(R, c1))
    K.eq(str(Msg.progText(R, c1, 340, 0)), "%s 340 / %s" % (R.name[c1], Util.fmt(Reg.threshold(R, c1, 1))), "R progText: to the next tier")
    K.eq(str(Msg.progText(R, c1, 99999999, mx1)), "%s %s (max)" % (R.name[c1], Util.fmt(99999999)), "R progText: max")

    # ---- progress, every route
    u = UUID.fromString("00000000-0000-4000-8000-000000000212")
    item = str(R.items[c1][0])
    hud(True, {"collection": "feed"})
    K.check(Msg.progress(u, R, c1, item, 9, 340, 0) and S["cards"] == [("collection", item, str(Msg.progText(R, c1, 340, 0)), 9)], "R progress feed: one card (item icon, count 9): %s" % S["cards"])
    # REVIEW FIX: the gate (SkyyHud would send a card pushed out of its 4-card stack before it was drawn as a chat line)
    K.check(not Msg.progress(u, R, c1, item, 4, 344, 0) and len(S["cards"]) == 1, "R FIX progress: the same item within 300 ms waits (no card)")
    ge = MR.GATE.get("collection|" + str(u))

    def age(i, ms):
        ge[i] = Long.valueOf(int(ge[i]) - ms)
    age(2, 400)
    K.check(Msg.progress(u, R, c1, item, 1, 345, 0) and S["cards"][-1] == ("collection", item, str(Msg.progText(R, c1, 345, 0)), 5),
            "R FIX progress: after 300 ms the next card carries the waited amount (1 + 4 = x5): %s" % S["cards"][-1:])
    age(2, 400)
    K.check(not Msg.progress(u, R, c1, "Other_Item", 2, 10, 0) and len(S["cards"]) == 2, "R FIX progress: a NEW item within 1 s waits")
    age(1, 1100)
    age(2, 400)
    K.check(Msg.progress(u, R, c1, "Other_Item", 3, 13, 0) and S["cards"][-1][1:] == ("Other_Item", str(Msg.progText(R, c1, 13, 0)), 5),
            "R FIX progress: after 1 s the new item gets its card with its waited amount (3 + 2 = x5): %s" % S["cards"][-1:])
    # burst: a sickle over 6 crops / a felled tree, 60 gathers in the same instant -> ONE card, no amount lost (the rest waits in PEND)
    hud(True, {"collection": "feed"})
    crops = ["Plant_Crop_Wheat_Item", "Plant_Crop_Carrot_Item", "Plant_Crop_Potato_Item", "Plant_Crop_Pumpkin_Item", "Plant_Crop_Corn_Item", "Plant_Crop_Onion_Item"]
    for i in range(60):
        Msg.progress(u, R, c1, crops[i % 6], 1 + (i % 3), 100 + i, 0)
    pend_ = sum(int(Msg.PEND.get(k)[0]) for k in Msg.PEND.keySet())
    tot_ = sum(1 + (i % 3) for i in range(60))
    K.check(len(S["cards"]) == 1 and S["cards"][0][3] + pend_ == tot_, "R FIX burst: 60 gathers over 6 crops in one instant -> %d card(s) (SkyyHud stacks 4, overflow = chat), %d of %d waiting"
            % (len(S["cards"]), pend_, tot_))
    for rt in ("chat", "off"):
        hud(True, {"collection": rt})
        K.check(not Msg.progress(u, R, c1, item, 9, 340, 0) and S["cards"] == [], "R progress %s: nothing (no chat line ever)" % rt)
    hud(True, {"collection": "feed"})
    S["ok"] = False
    K.check(not Msg.progress(u, R, c1, item, 9, 340, 0), "R progress refused: nothing")
    hud(False)
    K.check(not Msg.progress(u, R, c1, item, 9, 340, 0), "R progress without SkyyHud: nothing")

    # ---- announce, every route (a stand-in PlayerRef: the uuid only; its sendMessage cannot work in a bare JVM)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)

    def pref(uid):
        p = U.allocateInstance(PR.class_)
        f = PR.class_.getDeclaredField("uuid")
        f.setAccessible(True)
        f.set(p, uid)
        return p
    pr = pref(u)
    said = JClass("java.util.ArrayList")()
    MR.SAID = said
    hud(True, {"rankup": "off"})
    Cred.announce(pr, R, c1, t1, t1)
    K.check(said.size() == 0 and S["cards"] == [], "R announce off: nothing")
    hud(True, {"rankup": "feed"})
    R.iconOk[c1] = True
    Cred.announce(pr, R, c1, t1, t1)
    K.check(said.size() == 0 and S["cards"] == [("rankup", str(R.icon[c1]), str(Msg.cardText(R, c1, t1)), None)], "R announce feed: a rankup card: %s" % S["cards"])
    for label, route, ok in (("feed refused", "feed", False), ("chat", "chat", True)):
        hud(True, {"rankup": route})
        S["ok"] = ok
        said.clear()
        try:
            Cred.announce(pr, R, c1, t1, t1)
        except Exception:
            pass   # the stand-in player cannot send; the line is recorded before the send
        K.check(said.size() == 1 and str(said.get(0)) == str(Msg.text(Msg.rankParts(R, c1, t1, bool(Msg.craftOn())))), "R announce %s: ONE chat line: %s" % (label, said))
    MR.SAID = None

    # ---- CollNew + the credit path (offline) + save / 0.2.11 read-back
    key = str(u)
    d = Store.dataK(key)
    hs_ = [c for c in VIS if len(Reg.recipesAt(c, 1)) > 0 and len(Reg.recipesAt(c, 2)) == 0]
    cc = hs_[0] if hs_ else c1
    K.eq(int(New.mark(d, key, R, cc, 1, 2)), 1 << 1, "R mark: only tier I (tier II has no recipe) -> bit 1")
    K.check(New.isNew(d, R, cc, 1) and not New.isNew(d, R, cc, 2) and Store.DIRTY.containsKey(key), "R isNew + the profile is dirty")
    K.check(New.seen(d, key, R, cc) and not New.isNew(d, R, cc, 1) and not New.seen(d, key, R, cc), "R seen clears once")
    d.meta.put("_bought." + str(R.id[cc]), Long.valueOf(1))
    K.eq(int(New.mark(d, key, R, cc, 1, 1)), 0, "R mark: a tier bought with coins is not NEW")
    d.meta.remove("_bought." + str(R.id[cc]))
    K.check(not New.isNew(None, R, cc, 1) and not New.isNew(d, R, cc, 0) and not New.isNew(d, R, cc, 63), "R isNew: bad input = false")
    first = str(R.items[cc][0])
    Store.DIRTY.clear()
    Cred.creditOne(None, u, key, first, int(Reg.threshold(R, cc, 1)), True)
    K.check(New.isNew(d, R, cc, 1) and Store.DIRTY.containsKey(key), "R creditOne (offline) across tier I: NEW marked on the profile, dirty")
    K.check(bool(Store.save(key)), "R save() the counts file")
    txt = open(os.path.join(wbase, "counts", key + ".properties"), encoding="latin-1").read()
    K.check(("_new.%s=2" % R.id[cc]) in txt, "R the counts file carries _new.%s=2" % R.id[cc])
    L = _t11().loader_for(OLD_JAR)
    OStore = JClass(PKG + "CollStore", loader=L)
    Props = JClass("java.util.Properties")
    pp = Props()
    pp.setProperty("_new.%s" % R.id[cc], "2")
    pp.setProperty(first, "5")
    od = OStore.fromProps(pp)
    K.check(int(od.meta.get("_new.%s" % R.id[cc])) == 2 and int(od.items.get(first)) == 5, "R rollback: 0.2.11 reads _new.* as a meta number (kept on its save)")

    # ---- the page (a stand-in PlayerRef with the profile's uuid)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    pg = Page(pref(u))
    pg.view, pg.coll, pg.cat = 2, cc, int(R.cat[cc])
    b, ev = UCB(), UEB()
    pg.build(None, b, ev, None)
    st = None
    for cmd in b.getCommands():
        if cmd.selector is not None and str(cmd.selector) == "#SkyyCTr1S.Text":
            st = str(cmd.data)
    K.check(st is not None and "NEW" in st, "R buildDetail: tier I's state cell says NEW: %s" % st)
    K.check(not New.isNew(d, R, cc, 1), "R buildDetail: the markers are cleared after the page was drawn (shown once)")
    b, ev = UCB(), UEB()
    pg.build(None, b, ev, None)
    st2 = [str(c_.data) for c_ in b.getCommands() if c_.selector is not None and str(c_.selector) == "#SkyyCTr1S.Text"]
    K.check(st2 and "NEW" not in st2[0] and "DONE" in st2[0], "R buildDetail again: DONE (%s)" % st2)
    New.mark(d, key, R, cc, 1, 1)
    rows = Page.unlockedRows(d, R)
    mine = [str(r[1]) for r in rows if int(r[4]) == cc]
    K.check(mine and all(x.startswith("NEW  ") for x in mine), "R unlockedRows: NEW before the marked recipes: %s" % mine)
    New.seen(d, key, R, cc)
    mine = [str(r[1]) for r in Page.unlockedRows(d, R) if int(r[4]) == cc]
    K.check(mine and not any(x.startswith("NEW") for x in mine), "R unlockedRows: plain after seen")

    # ---- the page id: the jar's ready line = COLL_PAGE_CHECKED in the build script (this harness ran the page code above)
    import re, zipfile
    plug = zipfile.ZipFile(jar).read("com/skyy/collections/SkyyCollectionsPlugin.class").decode("latin1")
    chk = re.search(r'COLL_PAGE_CHECKED = "([0-9a-f]{12})"', open(os.path.join(HERE, "build_skyycollections_%s.py" % VERSION), encoding="utf8").read())
    K.check(chk is not None and ("page " + chk.group(1)) in plug, "R the jar's page id = COLL_PAGE_CHECKED (%s)" % (chk and chk.group(1)))

    # ---- SESSION: the 2026-10-11 rank-ups + every mod added up
    def find(word):
        for c in VIS:
            if word.lower() in str(R.name[c]).lower():
                return c
        return None
    ups = [(w, t) for w, t in (("Wildmeat", 2), ("Essence", 3), ("Bone", 1))]
    old_lines, new_lines, found = 0, 0, []
    for w, t in ups:
        c = find(w)
        if c is None:
            K.notes.append("SESSION: no collection named like %s" % w)
            continue
        found.append("%s %s" % (R.name[c], Util.roman(t)))
        old_lines += 1 + Reg.rewardLines(R, c, t).size() + (1 if len(Reg.recipesAt(c, t)) > 0 else 0)
        new_lines += 1
    K.check(len(found) == 3, "R SESSION: the log's three rank-ups found: %s" % found)
    coll = {"mod": "SkyyCollections " + VERSION, "before": old_lines, "after": new_lines, "what": "rank-ups %s (rank-up route default = Chat: one line each)" % found}
    os.makedirs(SESSION, exist_ok=True)
    json.dump(coll, open(os.path.join(SESSION, "collections.json"), "w"), indent=1)
    parts = {"collections": coll}
    for nm in ("skills", "classes"):
        fp = os.path.join(SESSION, nm + ".json")
        if os.path.isfile(fp):
            parts[nm] = json.load(open(fp))
    K.check(set(parts) == {"skills", "classes", "collections"}, "R SESSION: all three mods measured (run the SkyySkills 0.4.34 + SkyyClasses 0.1.20 harnesses first): %s" % sorted(parts))
    moved_before = sum(p["before"] for p in parts.values())
    kept = LOG_LINES - moved_before
    after = kept + sum(p["after"] for p in parts.values())
    tot = {"session_lines": LOG_LINES, "minutes": LOG_MINUTES, "moved_before": moved_before, "kept": kept, "before": LOG_LINES, "after": after,
           "per_minute_before": round(LOG_LINES / LOG_MINUTES, 1), "per_minute_after": round(after / LOG_MINUTES, 1), "parts": parts}
    json.dump(tot, open(os.path.join(SESSION, "total.json"), "w"), indent=1)
    K.check(kept >= 0 and after < LOG_LINES, "R SESSION total: %d chat lines (%.1f / min) -> %d (%.1f / min); %d kept as they were (level-ups, server, quests...)"
            % (LOG_LINES, LOG_LINES / LOG_MINUTES, after, after / LOG_MINUTES, kept))
    K.notes.append("SESSION total: %s" % json.dumps({k: v for k, v in tot.items() if k != "parts"}))
    K.save()


def run_jar(out, jar, scratch, home):
    return _t11().run_jar(out, jar, scratch, home)


def run_exec(out, jar, scratch, home):
    return _t11().run_exec(out, jar, scratch, home)


def run_live(out, jar, scratch, home):
    return _t11().run_live(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("jar", run_jar), ("exec", run_exec), ("route", run_route), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
