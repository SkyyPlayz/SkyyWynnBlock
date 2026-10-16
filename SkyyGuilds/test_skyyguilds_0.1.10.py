"""Harness for SkyyGuilds 0.1.10 (GUILD NAMES: spaces, punctuation and symbols; tools/guilds_0_1_10_patch.py) = the 0.1.9 harness
(HUBS H3c: the Social > Guild tab) carried forward, compare 0.1.9 -> 0.1.10, plus NAMES (executed on the real GuildStore, after PAGE):
  NAMES  Skyy's symbols (and | < > quote backslash ` ~ [ ] { } : ; ') make guilds; the name is kept exactly (norm only trims and joins
         spaces); findGuild finds it; refused: 2 / 25 characters, no letter, an accented letter, an emoji, the same name in other
         case; clean() echoes symbols, drops non-ASCII, max 32; the names round-trip through the guild files (Properties + loadAll)
Build first:
python tools/guilds_0_1_10_patch.py && python SkyyGuilds/build_skyyguilds_0.1.10.py

    python SkyyGuilds/test_skyyguilds_0.1.10.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.1.8 -> 0.1.9 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyGuilds as its own guild member, AA engine-access audit), plus here:
  PAGE  the views in the hub shell: not in a guild (the REG / PAGE / CLICK phases), a guild made for the op (1414 x 968, every
        page_check; the guild name [TAG] leads #SkyyGSub; no #SkyyGTitle), the full bank log (1414 x 968, at most 13 lines a page, the
        name leads #SkyyGLogSub; no #SkyyGLogTitle; check_page + the body fits); the script has 6 members / 13 log lines a page and the
        newest 2 log lines (the 1080p fit)
  CLICK Refresh (a non-hub click) still works; the page id is the one the patch pins (GUILD_PAGE_CHECKED)
Exit code 1 on any failure.
"""
import os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.10"
PKG = "com.skyy.guilds."


def prep(E, J, home):
    from jpype import JClass
    GS = J("GuildStore")
    GS.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyGuilds")
    GS.DIR = E.Paths.get(home)
    GS.GDIR = E.Paths.get(os.path.join(home, "guilds"))
    J("GCfg").FILE = E.Paths.get(os.path.join(home, "config.properties"))
    J("GCfg").load()
    GS.loadAll()


def live_player(home):
    p = os.path.join(home, "players.properties")
    if not os.path.isfile(p):
        return None
    for ln in open(p, encoding="latin-1"):
        m = re.match(r"([0-9a-f-]{36})=[^|]*\|([^|]*)\|", ln.strip())
        if m:
            return m.group(1), m.group(2)
    return None


def chk_refresh(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "GuildPage" and len(E.sent(P)) > f0,
            "CLICK: Refresh (not a hub click) still answers on the guild page")


def sets_of(cm):
    import json
    out = {}
    for ty, s, t, d in cm:
        if ty == "Set":
            try:
                v = json.loads(d)
                out[s] = str(v.get("0", v)) if isinstance(v, dict) else str(v)
            except Exception:
                out[s] = str(d)
    return out


def build(J, X, pg):
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    pg.build(X.ref, b, ev, X.st)
    return H.cmds_of(b), H.events_of(ev)


def extra_hub(K, W, J):
    import zipfile
    from jpype import JClass
    import skyyui as SUI
    E = W.E
    GS = J("GuildStore")
    O = W.O
    u = O.pr.getUuid()
    r = str(GS.create(u, "SkyyOp", "Harness Guild"))
    K.check(GS.snapshot(u) is not None, "PAGE: a guild made for the op (%s)" % r)
    J("GuildHubOpen").register()
    E.br.put("hub:last:" + str(u), JClass("java.util.concurrent.ConcurrentHashMap")())
    rr = str(J("HubBar").open(O.pr, u, "social", "guild"))
    E.pump(O)
    pg = O.pm.getCustomPage()
    K.check(rr == "bridge" and pg is not None and str(pg.getClass().getSimpleName()) == "GuildPage", "PAGE: the guild view opens through the tab (%s)" % rr)

    cm, evs = H.page_check(K, E, S, O, pg, J("HubBar"), "PAGE guild view")
    st = sets_of(cm)
    sub = st.get("#SkyyGSub.Text", "")
    K.check(sub.startswith("Harness Guild") and "Guild level" in sub, "PAGE guild view: the guild name leads #SkyyGSub (%s)" % sub[:60])
    K.check(not [c for c in cm if (c[1] and "SkyyGTitle" in c[1]) or (c[2] and "#SkyyGTitle " in c[2])], "PAGE guild view: no #SkyyGTitle")
    root = cm[0][2]
    K.check("Width: 1414, Height: 968" in root, "PAGE guild view: 1414 x 968 (%s)" % root[:60])
    pg.view = 1
    cm2, _e2 = build(J, O, pg)
    st2 = sets_of(cm2)
    ls = st2.get("#SkyyGLogSub.Text", "")
    K.check(ls.startswith("Harness Guild") and "guild bank log" in ls and "Guild bank:" in ls, "PAGE log view: the name leads #SkyyGLogSub (%s)" % ls[:60])
    K.check(not [c for c in cm2 if (c[1] and "SkyyGLogTitle" in c[1]) or (c[2] and "#SkyyGLogTitle " in c[2])], "PAGE log view: no #SkyyGLogTitle")
    K.check("Width: 1414, Height: 968" in cm2[0][2] and cm2[0][2].startswith("Group #SkyyGuildF "), "PAGE log view: the same 1414 x 968 hub shell")
    rows = [c for c in cm2 if c[2] and re.search(r"#SkyyGLRow\d+ ", c[2])]
    K.check(len(rows) <= 13, "PAGE log view: at most 13 log lines a page (%d)" % len(rows))
    apps = SUI.Appends([(None if s is None else s.lstrip("#"), t) for ty, s, t, d in cm2 if t is not None and ty and "Append" in ty])
    try:
        SUI.check_page(apps, "SkyyG")
        K.check(SUI.used_height(apps, "SkyyGuild") <= 968 - 38 - 48, "PAGE log view: the body fits under the strip")
    except Exception as e:
        K.check(False, "PAGE log view: check_page: %s" % e)
    pg.view = 0
    gen = open(os.path.join(HERE, "build_skyyguilds_%s.py" % VERSION), encoding="utf8").read()
    K.check("  int per = 6;" in gen and "  int per = 13;" in gen and "shown < 2" in gen, "PAGE: 6 members / 13 log lines a page, the newest 2 log lines")
    m = re.search(r'GUILD_PAGE_CHECKED = "([0-9a-f]{12})"', gen)
    data = zipfile.ZipFile(S.jar).read("com/skyy/guilds/SkyyGuildsPlugin.class")
    K.check(m is not None and ("page " + m.group(1)).encode() in data, "PAGE: the built page id = GUILD_PAGE_CHECKED %s (the ready line)" % (m and m.group(1)))
    J("HubBar").removeAll()
    names(K, J, GS, O)


def names(K, J, GS, O):
    """0.1.10 NAMES (Skyy 2026-10-16: "allow spaces punctuation and symbols like !@#$%^&*()_+-= ,.? / and so on")"""
    import glob
    from jpype import JClass
    UUID = JClass("java.util.UUID")
    ok, bad = [], []
    good = ["Skyy's !@#$%^&*()_+-=", "  A ,.?   /  B  ", "Pipe|<b>" + chr(92) + chr(34) + "`~[]{}:;x"]
    want = [" ".join(n.split()) for n in good]
    for i, nm in enumerate(good):
        u = UUID.fromString("00000000-0000-0000-0000-00000000a1%02d" % i)
        r = str(GS.create(u, "N%d" % i, nm))
        g = GS.findGuild(want[i])
        ok.append([r[:1], None if g is None else str(g.name)])
    K.check([o[0] for o in ok] == ["+"] * 3 and [o[1] for o in ok] == want,
            "NAMES: symbol names make guilds, kept exactly (trim + one space), findGuild finds them: %s" % ok)
    u9 = UUID.fromString("00000000-0000-0000-0000-00000000a199")
    for nm in ("ab", "x" * 25, "!!! 123 ???", "Caf" + chr(0xE9) + " Club", "Fire " + chr(0x1F525) + " Guild", "SKYY'S !@#$%^&*()_+-="):
        bad.append(str(GS.create(u9, "N9", nm))[:90])
    K.check(all(b.startswith("-") for b in bad) and "3 to 24" in bad[0] and "3 to 24" in bad[1] and "at least one letter" in bad[2]
            and "no emoji" in bad[3] and "no emoji" in bad[4] and "already exists" in bad[5],
            "NAMES: refused - 2 / 25 characters, no letter, an accented letter, an emoji, the same name in other case: %s" % bad)
    cl = [str(GS.clean(x)) for x in ("a!@#$%^&*()_+-= ,.?/b", "caf" + chr(0xE9), "y" * 40)]
    K.check(cl == ["a!@#$%^&*()_+-= ,.?/b", "caf", "y" * 32], "NAMES: clean() echoes symbols, drops non-ASCII, max 32: %s" % cl)
    fs = sorted(glob.glob(os.path.join(str(GS.GDIR.toString()), "*.properties")))
    GS.loadAll()
    back = [None if GS.findGuild(w) is None else str(GS.findGuild(w).name) for w in want]
    K.check(len(fs) >= 3 and back == want, "NAMES: the names round-trip through the guild files (Properties store -> loadAll): %d files %s" % (len(fs), back))


S = H.Spec(name="SkyyGuilds", version=VERSION, pkg=PKG, hub="social", tab="guild", mod="SkyyGuilds", open_cls="GuildHubOpen", vis_cls=None,
           page_cls="GuildPage", prefix="SkyyGuildF", idp="SkyyG", plugin_cls="SkyyGuildsPlugin", register_call="GuildHubOpen.register",
           register=lambda J: J("GuildHubOpen").register(), prep=prep, live_player=live_player,
           clicks=[('{"a":"refresh"}', chk_refresh)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyGuilds-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyGuilds-0.1.9.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "small01", "guilds"))), script=__file__,
           added=[],
           expect={"GuildStore": ["+m printable", "~m clean", "~m nameError"],   # 0.1.10: the name rule + the echo
                   "GuildPage": ["~m buildNone"], "GCreateCmd": ["~c "],          # the rule line / command description
                   "SkyyGuildsPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "GCfg": ["~m load"]})
H.KIT_FILES = []   # 0.1.9 -> 0.1.10: the 59 kit files are already in 0.1.9 (byte-equal), so only manifest.json changes

if __name__ == "__main__":
    H.run(S)
