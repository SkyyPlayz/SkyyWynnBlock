"""Harness for SkyyRanks 0.1.2 (MENU PATTERN sweep S4: the ranks editor on the kit 1.7 hub_page of the Settings hub; tools/ranks_0_1_2_patch.py).
Build first:
    python tools/ranks_0_1_2_patch.py && python SkyyRanks/build_skyyranks_0.1.2.py

    python SkyyRanks/test_skyyranks_0.1.2.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.1.1 -> 0.1.2: exactly the listed members differ (RankUI, RankPage; + HubBar); the non-class entries: manifest.json + the
                kit's 59 Sky Window files (the jar is an asset pack now)
  O    old      the 0.1.1 page (old jar) driven through the SAME clicks as N: every view's bound actions recorded
  N    EXECUTED (new jar, a fake permission engine behind RankPerm.FAKE, a scratch data folder):
       PAGES    every view BUILT by the real RankPage.build - Ranks, a rank's Settings / Grants / Grants search / Members / Members online,
                Players, a player, Confirm, the locked page: check_page (markup rules, parents, no duplicate id), kit paths only, every
                b.set / binding names an element that exists, SUI.assert_menu_page (1600 x 980, row 1 + row 2, ONE sub row, no back /
                < Menu text, no pager, the content fits); the title bar says Settings; row 2 shows Server Setup selected
       ACTIONS  each view binds the 0.1.1 view's actions minus exactly prev / next / setup / close and the selected tab (drawn, not
                bound), plus only the top rows (hub:*) and Show more
       CLICKS   create a rank, grant + remove a node, search, the sub-tabs, Confirm -> Cancel, hub:setup / hub:close / hub:h:settings
                handled before the access guard
       LISTS    230 online players: ONE list of the first 200 + Show more, a click draws all 230; few rows grow (4 ranks: 95 px rows,
                230 players: 66 px)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

VERSION = "0.1.2"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyRanks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyRanks-0.1.1.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menuS4", "ranks", "h")))
PKG = "com.skyy.ranks."
ADDED = ["HubBar"]
EXPECT = {}      # filled below
OLD_ACTIONS = os.path.join(SCRATCH, "old_actions.json")


# ---------------------------------------------------------------------------------------------------------------- C (kit art allowed)
_orig_compare = HK.run_compare


def run_compare_kit(out, jar, old_jar, pkg, expect, added, removed=()):
    """harness_kit.run_compare, whose last check wants only manifest.json among the non-class entries: 0.1.2 also adds the kit's 59 Sky
    Window files (Common/UI/Custom/SkyyKit/) - the class compare runs unchanged, the entry check is redone here with the kit files allowed"""
    _orig_compare(out, jar, old_jar, pkg, expect, added, removed)
    d = json.load(open(out))
    want = "C: non-class entries changed"
    kit = sorted(SUI.kit_texture_files().keys()) if isinstance(SUI.kit_texture_files(), dict) else sorted(SUI.kit_texture_files())
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    ea = [n for n in za.namelist() if not n.endswith(".class")]
    eb = [n for n in zb.namelist() if not n.endswith(".class")]
    ed = sorted(n for n in set(ea) | set(eb) if n not in ea or n not in eb or za.read(n) != zb.read(n))
    fails = [f for f in d["fails"] if not f.startswith(want)]
    ok = ed == sorted(["manifest.json"] + kit)
    if not ok:
        fails.append("%s (kit art allowed): got %s" % (want, ed[:6]))
    else:
        d["ok"] += 1
    man = json.loads(zb.read("manifest.json"))
    if man.get("IncludesAssetPack") is not True:
        fails.append("C: the manifest is an asset pack (IncludesAssetPack true)")
    d["fails"] = fails
    d["notes"].append("C: non-class entries = manifest.json + %d kit files" % len(kit))
    json.dump(d, open(out, "w"), indent=1)


HK.run_compare = run_compare_kit


# ---------------------------------------------------------------------------------------------------------------- the page reader
def jf(c, name):
    while c is not None:
        try:
            f = c.getDeclaredField(name)
            f.setAccessible(True)
            return f
        except Exception:
            c = c.getSuperclass()
    raise KeyError(name)


def cmds_of(b):
    out = []
    for c in list(b.getCommands()):
        g = lambda n: (lambda v: None if v is None else str(v))(jf(c.getClass(), n).get(c))
        out.append((g("type"), g("selector"), g("text"), g("data")))
    return out


def events_of(ev):
    """(selector, action) of every binding: the EventData's "a" value (found in the binding's fields, whatever their names)"""
    from jpype import JClass
    out = []
    Coll = JClass("java.util.Collection")
    for f_ in ev.getClass().getDeclaredFields():
        f_.setAccessible(True)
        v_ = f_.get(ev)
        if v_ is None or not Coll.class_.isInstance(v_):
            continue
        for e in list(v_):
            sel, parts = None, []
            c = e.getClass()
            while c is not None and str(c.getName()) != "java.lang.Object":
                for g in c.getDeclaredFields():
                    try:
                        g.setAccessible(True)
                        x = g.get(e)
                        if x is None:
                            continue
                        if str(g.getName()) == "selector":
                            sel = str(x)
                        parts.append(str(x))
                        for h in x.getClass().getDeclaredFields():
                            try:
                                h.setAccessible(True)
                                y = h.get(x)
                                if y is not None:
                                    parts.append(str(y))
                            except Exception:
                                pass
                    except Exception:
                        pass
                c = c.getSuperclass()
            txt = " | ".join(parts)
            m = re.search(r'"a"\s*:\s*"([^"]*)"', txt) or re.search(r"\ba=([^,}\s|]+)", txt)
            out.append((sel, m.group(1) if m else None, txt))
    return out


DECL_RE = re.compile(r"\b([A-Za-z]+) #([A-Za-z0-9]+) \{")


def build_page(page):
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    page.build(None, b, ev, None)
    return cmds_of(b), events_of(ev)


def unq(d):
    if d is None:
        return ""
    d = str(d)
    try:
        v = json.loads(d)
    except Exception:
        return d
    if isinstance(v, dict) and len(v) == 1:
        v = list(v.values())[0]
    return v if isinstance(v, str) else d


# ---------------------------------------------------------------------------------------------------------------- the fake engine + page
def setup(scratch, jar, label, n_online=3):
    import jpype
    from jpype import JClass, JImplements, JOverride
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    JV = lambda n: JClass(PKG + n)
    Paths, HashSet, TreeSet, ArrayList = JClass("java.nio.file.Paths"), JClass("java.util.HashSet"), JClass("java.util.TreeSet"), JClass("java.util.ArrayList")
    UUID, Bool, JStr = JClass("java.util.UUID"), JClass("java.lang.Boolean"), JClass("java.lang.String")
    ME = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    state = {"has": True}
    nodes = ["skyyessentials.fly", "skyyessentials.home", "skyymenu.modconfig", "skyyparty.bypass", "skyyranks.admin", "skyyskills.boost"]

    groups, members = {}, {}          # the fake provider: group -> nodes, user -> groups (enough for RankOps' read-back checks)

    def jset(xs):
        h = HashSet()
        for x in xs:
            h.add(x)
        return h

    @JImplements("java.util.function.Function")
    class Fake(object):
        @JOverride
        def apply(self, arr):
            op, a, b = str(arr[0]), arr[1], arr[2]
            if op == "has":
                return Bool.TRUE if state["has"] else Bool.FALSE
            if op == "ready":
                return Bool.TRUE
            if op == "groupsOf":
                g = set(members.get(str(a), set())) | {"hytale:Adventurer"}
                if str(a) == str(ME):
                    g.add("hytale:Admin")
                return jset(sorted(g))
            if op == "addToGroup":
                members.setdefault(str(a), set()).add(str(b))
                return None
            if op == "removeFromGroup":
                members.setdefault(str(a), set()).discard(str(b))
                return None
            if op == "groupNodes":
                return jset(sorted(groups.get(str(a), set())))
            if op == "addGroupNodes":
                groups.setdefault(str(a), set()).update(str(x) for x in b)
                return None
            if op == "removeGroupNodes":
                groups.setdefault(str(a), set()).difference_update(str(x) for x in b)
                return None
            if op == "allGroups":
                return jset(sorted(groups))
            if op == "userNodes":
                return HashSet()
            if op == "registered":
                t = TreeSet()
                for n_ in nodes:
                    t.add(n_)
                return t
            return None
    fake = Fake()
    home = os.path.join(scratch, "home_" + label)
    os.makedirs(home, exist_ok=True)
    Cfg, Store, Perm, Eng = JV("RankCfg"), JV("RankStore"), JV("RankPerm"), JV("RankEngine")
    Perm.FAKE = fake
    Cfg.INLINE = True
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    online = ArrayList()
    for i in range(n_online):
        online.add(JClass("java.lang.String[]")([JStr("00000000-0000-0000-0000-%012d" % (100 + i)), JStr("Player%03d" % i)]))
    Cfg.TEST_ONLINE = online
    Cfg.loadCfg(True)
    Store.load(Paths.get(home))
    Eng.STARTED = True
    br = Cfg.bridge()
    # the Settings hub's Server Setup tab as SkyyMenu puts it (mod, label, order, command, open Function, hide Function)
    from jpype import JArray, JObject
    br.put("hub:tab:settings:setup", JArray(JObject)([JStr("SkyyMenu"), JStr("Server Setup"), JClass("java.lang.Integer")(40), JStr("modconfig"), None, None]))
    for h_ in SUI.HUB_ROW_IDS:        # row 1 as SkyyMenu publishes it: hub:def:<hub> = { title, command, icon item }
        br.put("hub:def:" + h_, JArray(JObject)([JStr("Home" if h_ == "home" else SUI.hub_title_now(h_)), JStr("skymenu"), JStr("Skyy_Menu")]))
    br.put("hub:tab:settings:mods", JArray(JObject)([JStr("SkyyMenu"), JStr("Mods"), JClass("java.lang.Integer")(30), JStr("mods"), None, None]))
    return JV, ME, state, online, JStr


def flow(page, click, built):
    """the SAME clicks on the old and the new page: every view in order -> {view: (cmds, events)}"""
    out = {}
    out["ranks"] = built("ranks")
    click("edit:2")
    out["rank-settings"] = built("rank-settings")
    click("tab3")
    out["rank-grants"] = built("rank-grants")
    click("search", ',"@F0":"skyy"')
    out["grants-search"] = built("grants-search")
    click("tab4")
    out["rank-members"] = built("rank-members")
    click("online")
    out["members-online"] = built("members-online")
    click("tab1")
    out["players"] = built("players")
    click("popen:0")
    out["player"] = built("player")
    click("tab0")
    out["ranks-again"] = built("ranks-again")      # (row clicks use the row keys of the last build)
    click("edit:3")
    click("tab3")
    click("grant", ',"@F0":"skyyessentials.home"')
    out["confirm"] = built("confirm")
    click("no")
    out["after-cancel"] = built("after-cancel")
    return out


def run_old(out, _jar, scratch, _home):
    K = HK.Child(out)
    JV, ME, state, online, JStr = setup(scratch, OLD_JAR, "old")
    pg = JV("RankPage")(ME, "SkyyOp", "ranks", None)

    def click(a, extra=""):
        pg.handleDataEvent(None, None, '{"a":"%s"%s}' % (a, extra))

    def built(v):
        c, e = build_page(pg)
        return sorted(set(a for _s, a, _t in e if a))
    acts = flow(pg, click, built)
    state["has"] = False
    acts["locked"] = built("locked")
    K.check(len(acts["ranks"]) > 5 and "yes" in acts["confirm"] and "no" in acts["confirm"], "O: the 0.1.1 page ran the flow (%d actions on Ranks, Confirm reached)" % len(acts["ranks"]))
    json.dump(acts, open(OLD_ACTIONS, "w"), indent=1)
    K.save()


def run_new(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    JV, ME, state, online, JStr = setup(scratch, jar, "new")
    pg = JV("RankPage")(ME, "SkyyOp", "ranks", None)
    Store = JV("RankStore")

    def click(a, extra=""):
        pg.handleDataEvent(None, None, '{"a":"%s"%s}' % (a, extra))

    views = {}

    def built(v):
        c, e = build_page(pg)
        apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in c if t is not None and ty and "Append" in ty])
        sets = [(s, unq(d)) for ty, s, t, d in c if ty == "Set"]
        try:
            SUI.check_page(apps, "Skyy")
            K.check(True, "%s: check_page" % v)
        except Exception as ex:
            K.check(False, "%s: check_page: %s" % (v, ex))
        try:
            SUI.check_sky_paths(apps, tab_icons=True)
            allp = [m.group(0) for mk in apps.markups() for m in SUI._SKY_PATH_RE.finditer(SUI.render(mk))]
            K.check(not [p for p in allp if p.startswith('"../')], "%s: no texture path leaves Common/UI/Custom" % v)
        except Exception as ex:
            K.check(False, "%s: sky paths: %s" % (v, ex))
        ids = set()
        for _p, mk in apps:
            ids |= set(x.group(2) for x in DECL_RE.finditer(SUI.render(mk)))
        bad = [s for s, _d in sets if s.lstrip("#").split(".")[0] not in ids] + [s for s, _a, _t in e if s and s.lstrip("#") not in ids]
        K.check(not bad, "%s: every b.set / binding names an element that exists (%d sets, %d bindings): %s" % (v, len(sets), len(e), bad[:4]))
        try:
            info = SUI.assert_menu_page(apps, hub="settings", what="SkyyRanks " + v, sets=sets)
            K.check(info["rows"] == 2 and info["subs"] == 1, "%s: assert_menu_page (1600 x 980, rows 1 + 2, one sub row, no back / pager)" % v)
        except Exception as ex:
            K.check(False, "%s: assert_menu_page: %s" % (v, ex))
        title = [t for ty, s, t, d in c if t and "#SkyyRkTitle" in t]
        K.check(len(title) == 1 and 'Text: "Settings"' in title[0] and not any("SkyyRkTitle" in str(s) for s, _d in sets),
                "%s: the title bar says Settings (the hub)" % v)
        k = [t for ty, s, t, d in c if t and t.startswith("Button #SkyyRkBigT")]
        K.check(len(k) == 2, "%s: row 2 = the Settings tabs in the bridge (%d)" % (v, len(k)))
        # the content group's direct children fit its 676 px (assert_menu_page with a shell does it on previews; here by hand)
        kids = SUI.Appends([(p, mk) for p, mk in apps if p == "SkyyRkBody"])
        used = SUI.used_height(kids, "SkyyRkBody")
        K.check(used <= 676, "%s: the content is %d px of 676" % (v, used))
        acts = sorted(set(a for _s, a, _t in e if a))
        K.check(all(a for _s, a, _t in e), "%s: every binding sends an action" % v)
        views[v] = (c, e, apps, sets)
        return acts
    acts = flow(pg, click, built)
    state["has"] = False
    acts["locked"] = built("locked")
    state["has"] = True
    # ---- ACTIONS: the same handler actions as 0.1.1
    old = json.load(open(OLD_ACTIONS)) if os.path.isfile(OLD_ACTIONS) else None
    K.check(old is not None, "ACTIONS: the 0.1.1 run left its actions")
    gone_ok = {"prev", "next", "setup", "close"}
    sel = {"ranks": "tab0", "rank-settings": "tab2", "rank-grants": "tab3", "grants-search": "tab3", "rank-members": "tab4",
           "members-online": "tab4", "players": "tab1", "after-cancel": "tab3", "ranks-again": "tab0"}
    for v in sorted(acts):
        if old is None or v not in old:
            continue
        o, n = set(old[v]), set(acts[v])
        lost = sorted(o - n - gone_ok - ({sel[v]} if v in sel else set()))
        extra = sorted(a for a in n - o if not a.startswith("hub:") and a != "more")
        K.check(not lost and not extra, "ACTIONS %s: 0.1.1's actions kept (lost %s, new %s; %d -> %d)" % (v, lost, extra, len(o), len(n)))
        K.check(not (n & gone_ok), "ACTIONS %s: no prev / next / setup / close bound any more" % v)
        K.check("hub:close" in n and len([a for a in n if a.startswith("hub:h:")]) == len(SUI.HUB_ROW_IDS) and "hub:setup" in n,
                "ACTIONS %s: row 1 (%d hubs), row 2 and the X bound: %s" % (v, len(SUI.HUB_ROW_IDS), sorted(a for a in n if a.startswith("hub:"))))
    # ---- the views' own rules
    c, e, apps, sets = views["ranks"]
    subs = [t for ty, s, t, d in c if s == "#SkyyRkSub" and t and t.startswith("TextButton")]
    K.check(len(subs) == 2 and "Primary" in subs[0] and "Secondary" in subs[1], "SUB: Ranks view = [RANKS (active, Primary)][PLAYERS]")
    rows = [t for ty, s, t, d in c if s == "#SkyyRkRows" and t and t.startswith("Group #SkyyRkRow")]
    K.check(len(rows) == 4 and all("Height: 95)" in r for r in rows), "GROW: 4 ranks -> 4 rows of 95 px (rule 7): %s" % [re.search(r"Height: (\d+)", r).group(1) for r in rows])
    c, e, apps, sets = views["rank-settings"]
    subs = [t for ty, s, t, d in c if s == "#SkyyRkSub" and t and t.startswith("TextButton")]
    K.check(len(subs) == 5 and "Primary" in subs[2] and sum("Primary" in x for x in subs) == 1, "SUB: a rank = [RANKS][PLAYERS] [SETTINGS (active)][GRANTS][MEMBERS]")
    K.check(any(t and "#SkyyRkRows" in t and "Height: 616" in t for ty, s, t, d in c), "SETTINGS: the taller list (no add row)")
    c, e, apps, sets = views["player"]
    subs = [t for ty, s, t, d in c if s == "#SkyyRkSub" and t and t.startswith("TextButton")]
    K.check(len(subs) == 3 and "Primary" in subs[2], "SUB: a player = [RANKS][PLAYERS] [PLAYER (active)]")
    c, e, apps, sets = views["confirm"]
    K.check(any(t and "#SkyyRkYes" in t for ty, s, t, d in c) and any(t and "#SkyyRkNo" in t for ty, s, t, d in c), "CONFIRM: an in-page view (Confirm / Cancel) under rows 1 + 2")
    c, e, apps, sets = views["locked"]
    K.check(any("no access" in str(d) for s, d in sets) and not any(a == "refresh" for _s, a, _t in e), "LOCKED: the no-access line, no Refresh")
    ups = [t for ty, s, t, d in views["ranks"][0] if t and "#SkyyRkFoot" == s]
    K.check(len(ups) >= 3 and any("#SkyyRkStatus" in t for t in ups) and any("#SkyyRkRefresh" in t for t in ups), "FOOT: the result line + Refresh in the footer")
    # ---- CLICKS
    click("tab0")
    click("create", ',"@F0":"vip","@F1":"VIP"')
    K.check(Store.find("vip") is not None and str(pg.view) == "rank" and str(pg.rankId) == "vip", "CLICK: create vip from the add row opens it (%s)" % pg.status)
    click("tab3")
    click("grant", ',"@F0":"skyyessentials.fly"')
    K.check(Store.find("vip").grants.contains("skyyessentials.fly"), "CLICK: grant skyyessentials.fly to vip (%s)" % pg.status)
    build_page(pg)                                 # the row keys of the Grants view
    click("ungrant:0")
    K.check(not Store.find("vip").grants.contains("skyyessentials.fly"), "CLICK: Remove the grant (%s)" % pg.status)
    click("tab2")
    K.check(int(pg.sub) == 0, "CLICK: Settings sub-tab")
    click("hub:h:settings")
    K.check(str(pg.view) == "rank", "HUB: row 1 Settings = this page (self)")
    state["has"] = False
    click("hub:close")
    K.check(not str(pg.status).startswith("-You have no access"), "HUB: the X is handled before the access guard (%s)" % pg.status)
    click("hub:setup")
    K.check(not str(pg.status).startswith("-You have no access"), "HUB: Server Setup (row 2) is handled before the access guard")
    state["has"] = True
    # ---- LISTS: 230 online players -> 200 rows + Show more, then all 230; normal 66 px rows
    for i in range(3, 230):
        online.add(JClass("java.lang.String[]")([JStr("00000000-0000-0000-0000-%012d" % (100 + i)), JStr("Player%03d" % i)]))
    click("tab1")
    c, e = build_page(pg)
    rows = [t for ty, s, t, d in c if s == "#SkyyRkRows" and t and t.startswith("Group #SkyyRkRow")]
    K.check(len(rows) == 200 and all("Height: 66)" in r for r in rows), "LISTS: 230 players -> the first 200 rows at 66 px (%d)" % len(rows))
    K.check(any(a == "more" for _s, a, _t in e) and any("first 200 shown" in str(d) for ty, s, t, d in c if ty == "Set"), "LISTS: Show more + the head says so")
    click("more")
    c, e = build_page(pg)
    rows = [t for ty, s, t, d in c if s == "#SkyyRkRows" and t and t.startswith("Group #SkyyRkRow")]
    K.check(len(rows) == 230 and not any(a == "more" for _s, a, _t in e), "LISTS: Show more draws all 230 (%d)" % len(rows))
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in c if t is not None and ty and "Append" in ty])
    try:
        SUI.check_page(apps, "Skyy")
        SUI.assert_menu_page(apps, hub="settings", what="230 players", sets=[(s, unq(d)) for ty, s, t, d in c if ty == "Set"])
        K.check(True, "LISTS: the 230-row page passes the page rules")
    except Exception as ex:
        K.check(False, "LISTS: the 230-row page: %s" % ex)
    K.notes.append("N: views %s" % ", ".join("%s %d actions" % (v, len(a)) for v, a in sorted(acts.items())))
    K.save()


EXPECT.update({
    # the version string (the ready line, rank:version; the config kit's header / export name the mod version)
    "CfgFn": ["~m opExport"],
    "SkyyRanksPlugin": ["~m setup"],
    # + the config kit's drift since 0.1.1 was built (a scratch rebuild of the 0.1.1 script shows +f BRIDGE, +m bridge0, ~m bridge too)
    "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header"],
    "RankPage": ["+f cap", "+f rowH", "+m grow", "+m hubClick", "+m more", "+m tab", "-m tab", "~m act", "~m addRow", "~m build",
                 "~m buildConfirm", "~m buildFoot", "~m buildGrants", "~m buildMembers", "~m buildPlayer", "~m buildPlayers", "~m buildRanks",
                 "~m buildSettings", "~m buildStatus", "~m buildTabs", "~m clearDrafts", "~m clickNav", "~m empty", "~m field",
                 "~m handleDataEvent", "~m init", "~m pageText", "~m pre", "~m rowStart", "~m setPages", "~m setRow", "~m sp", "~m texts"],
    "RankUI": ["+f CAP", "+f HS", "+f HSX", "+f LISTX_IN", "+f LIST_IN", "+f MORE", "+f MOREROW", "+f MORESP", "+f ROWSX", "-f BAR",
               "-f BODY", "-f CLOSE", "-f DECOB", "-f DECOT", "-f FLEAD", "-f FOOT", "-f GAPDEL", "-f NEXT", "-f PREV", "-f ROOT", "-f SEP",
               "-f SETUP", "-f SP12", "-f TAB", "-f TABS", "-f TABSEL", "-f TITLE", "~<clinit>"],
})

if __name__ == "__main__":
    HK.run(name="SkyyRanks", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("old", run_old), ("new", run_new)], script=__file__)
