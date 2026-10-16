"""Self-test of the skyyui kit 1.5 HUB contract + SKY WINDOW theme (research/Hubs-Spec.md 2 + 7, tools/HUBS-CONTRACT.md).

    python tools/test_skyyui_hubs.py [--dir <scratch folder>] [--no-java] [--keep]

Phase 1  the art + theme: verify() (Assets.zip, read-only) and sky_verify() (every kit PNG = the sha256 / size the kit pins, the art
         manifest agrees), both themes have the same roles, every sky role is a SkyyKit path inside Common/UI/Custom, every vanilla
         role a texture verify() proves, theme_button_style("vanilla") == button_style(); check_sky_paths refuses "../SkyyKit/..."
         (the client disconnects), "@2x" paths and unknown elements; check_jar_kit passes a jar built with kit_texture_files() and
         refuses a changed byte or a SkyyKit file outside the custom root.
Phase 2  the self-test page: a Character hub page (hub_shell 1200 x 900, sky) with the tab bar preview + a body: check_page (markup
         rules, parents, no duplicate id), assert_proven (proven properties only), check_sky_paths (every texture under
         Common/UI/Custom and shipped), the bar fits 8 tabs x 110 px at 1080p (page <= 1600 x 980), every hub fits its contract tabs,
         the 960 Skills page fits with the vanilla padding, every contract label fits its tab (16 px, or shrunk to 12), the java_hub_build
         line, assert_hub_page.
Phase 3  (a JVM; skipped with --no-java) installs class HubBar (sky + vanilla) with javassist against the cached HytaleServer.jar
         (tools/serverjar.py), loads it with -Xverify (URLClassLoader) and EXECUTES it: put() / the registry value types, build()
         into a REAL UICommandBuilder / UIEventBuilder = byte for byte hub_bar_preview(), the bound events (tabs, < Menu, close X),
         hub:last, handle() routing, open() through the bridge Function and through the command fallback (reached: "nocmd" - no
         CommandManager in a test JVM; the in-game fallback is proven by probe h1), hidden / missing / failed, the overflow rule,
         removeAll() removing only this jar's own arrays.
Phase 4  KIT 1.6 (the hub row, tab icons, default tab; research/Unified-Menu-Plan.md U1): backward compatibility against the COMMITTED
         kit (git HEAD:tools/skyyui.py loaded as a second module: hub_bar_java(), every 1.5 hub_shell, hub_bar_preview, java_hub_build
         byte-identical, KIT_VERSION still "1.5"); row shells (Home + a hub) keep the 1.5 page sizes (the row sits in the 38 px title
         bar: assert_hub_page unchanged), pass check_page / assert_proven / check_sky_paths, row 1 fits every page width the menu uses;
         the tab icon hook path is refused unless tab_icons=True; then (JVM) HubBar(row=True) compiled (sky + vanilla) and EXECUTED:
         def4 / defTab, putIcon / iconOf, hubs() order, buildRow == hub_row_preview and build2 == hub_bar_preview2 byte for byte (with
         and without icons, no-def fallback title), the row / tab / X bindings, pickTab (default -> last -> first), goHub / route outcomes.
Scratch: tools/dev/scratch/skyyui-hubs-test (deleted unless --keep). Prints "N ok, 0 fail"; exit 1 on a failure.
"""
import os, sys, shutil, zipfile, hashlib, json, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import skyyui as UI


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


SCRATCH = os.path.abspath(arg("--dir", os.path.join(HERE, "dev", "scratch", "skyyui-hubs-test")))
KEEP = "--keep" in sys.argv
NOJAVA = "--no-java" in sys.argv
P = "SkyyHt"
OKS = [0]
FAILS = []


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)


def raises(fn, exc, what, contains=None):
    try:
        fn()
    except exc as e:
        check(contains is None or contains in str(e), "%s (message: %s)" % (what, e))
        return
    except Exception as e:      # noqa
        FAILS.append("%s: raised %s instead of %s: %s" % (what, type(e).__name__, exc.__name__, e))
        return
    FAILS.append("%s: did not raise" % what)


# ================================================================= phase 1: the art + the theme table
def phase_art():
    UI.verify(quiet=True)
    files = UI.sky_verify()
    check(len(files) == len(UI.SKY_FILES) == 59, "sky_verify: 59 kit files (%d)" % len(files))
    check(all(p.startswith("Common/UI/Custom/SkyyKit/") for p in files), "every kit file ships under Common/UI/Custom/SkyyKit/")
    check(UI.KIT_VERSION == "1.5" and UI.kit_id().startswith("skyyui 1.5 "), "kit version 1.5 (%s)" % UI.kit_id())
    for p, data in files.items():
        check(hashlib.sha256(data).hexdigest() == UI.SKY_FILE[p[len(UI.SKY_JAR_DIR):]][3], "pinned sha256 of %s" % p)
    # the art directory with one changed byte fails the build
    bad = os.path.join(SCRATCH, "art-bad")
    shutil.copytree(UI.SKY_ART_DIR, bad, ignore=shutil.ignore_patterns("sheet.png"))
    f = os.path.join(bad, "Common", "UI", "Custom", "SkyyKit", "Tab@2x.png")
    d = bytearray(open(f, "rb").read())
    d[-20] ^= 1
    open(f, "wb").write(bytes(d))
    raises(lambda: UI.sky_verify(art_dir=bad), UI.SkyArtError, "sky_verify refuses a changed kit PNG", "Tab@2x.png changed")
    for t in UI.THEMES:
        check(sorted(UI.THEME[t]) == list(UI.THEME_ROLES), "theme %s has every role" % t)
    for role in UI.THEME_ROLES:
        sv = UI.theme_bg(role, "sky")
        el = UI.THEME_ELEMENT[role]
        check(('"SkyyKit/%s.png"' % el) in sv and "../" not in sv and "@2x" not in sv, "sky role %s = SkyyKit/%s.png" % (role, el))
        check(UI.check_sky_paths([sv]) == [el], "sky role %s passes check_sky_paths" % role)
        vv = UI.theme_bg(role, "vanilla")
        check(UI.check_sky_paths([vv]) == [], "vanilla role %s names a verified vanilla texture / colour" % role)
    for kind in UI.BUTTONS:
        for size in UI.BUTTON_SIZES:
            for dis in (False, True):
                check(UI.theme_button_style(kind, size, disabled=dis, theme="vanilla") == UI.button_style(kind, size, disabled=dis),
                      "theme_button_style vanilla == button_style (%s %s %s)" % (kind, size, dis))
                s = UI.theme_button_style(kind, size, disabled=dis, theme="sky")
                check(UI.check_sky_paths([s]) and "Common/Buttons" not in s, "sky %s %s button uses only kit art" % (kind, size))
    check(UI.theme_button_style("tertiary", "small", selected=True, theme="sky").count("Tertiary_Active") == 2,
          "sky selected tertiary = Tertiary_Active (Default + Hovered)")
    check(UI.theme_scrollbar_style(theme="vanilla") == UI.scrollbar_style(), "theme_scrollbar_style vanilla == scrollbar_style")
    check(UI.theme_row_style("normal", "vanilla") == UI.row_style("normal"), "theme_row_style vanilla == row_style")
    for s in (UI.theme_scrollbar_style(theme="sky"), UI.theme_row_style("selected", "sky"), UI.theme_separator(P + "Sep", theme="sky")):
        UI.check_sky_paths([s])
        check("SkyyKit/" in s, "sky helper uses the kit art: %s" % s[:60])
    # the path rules
    raises(lambda: UI.check_sky_paths(['Group { Background: (TexturePath: "../SkyyKit/Frame.png", Border: 32); }']), ValueError,
           "a SkyyKit path outside the custom root is refused (k1b disconnect)", "outside")
    raises(lambda: UI.check_sky_paths(['Group { Background: "SkyyKit/Frame@2x.png"; }']), ValueError, "an @2x markup path is refused")
    raises(lambda: UI.check_sky_paths(['Group { Background: "SkyyKit/Nope.png"; }']), ValueError, "an unknown kit element is refused")
    raises(lambda: UI.check_sky_paths(['Group { Background: "SkyyKit/Sub/Frame.png"; }']), ValueError, "a kit sub-folder is refused")
    raises(lambda: UI.check_sky_paths(['Group { Background: "../Common/ContainerPatch.png"; }']), ValueError,
           "any path leaving Common/UI/Custom is refused on a hub page")
    raises(lambda: UI.check_sky_paths(['Group { Background: "Common/NotAKitTexture.png"; }']), ValueError,
           "an unverified vanilla path is refused")
    # jars: the identical full set passes; a changed byte or a file outside the custom root fails
    good = os.path.join(SCRATCH, "good.jar")
    with zipfile.ZipFile(good, "w") as z:
        for p, data in UI.kit_texture_files().items():
            z.writestr(p, data)
    check(UI.check_jar_kit(good, need=("Tab", "Frame_Character")) == 59, "check_jar_kit: the full kit set in a jar")
    for name, mutate in (("changed", lambda z, p, d: z.writestr(p, d[:-1] + bytes([d[-1] ^ 1]))),
                         ("outside", lambda z, p, d: z.writestr(p.replace("Custom/SkyyKit/", "SkyyKit/"), d))):
        j = os.path.join(SCRATCH, name + ".jar")
        with zipfile.ZipFile(j, "w") as z:
            for p, data in UI.kit_texture_files().items():
                (mutate if p.endswith("Tab@2x.png") else (lambda zz, pp, dd: zz.writestr(pp, dd)))(z, p, data)
        raises(lambda: UI.check_jar_kit(j), ValueError, "check_jar_kit refuses a jar with a %s kit file" % name)
    sub = UI.kit_texture_files([UI.hub_close(P, "sky"), 'Group { Background: "SkyyKit/HubIcon_World.png"; }'])
    check(sorted(sub) == sorted(UI.SKY_JAR_DIR + n for n in ("Close@2x.png", "Close_Hovered@2x.png", "HubIcon_World@2x.png",
                                                            "HubIcon_World.png")), "kit_texture_files(markups) = only what they name")


# ================================================================= phase 2: the self-test page
CHAR_TABS = UI.hub_tabs("character")


def self_test_page():
    sh = UI.hub_shell(P, 1200, 900, "character")
    tabs = [(t, l, o) for t, o, _m, l, _c in CHAR_TABS]
    bar = UI.hub_bar_preview(P, tabs, "skills", sh.tabs_w)
    body = UI.Appends()
    body.append((sh.body, UI.label(P + "Info", "Hub self test - Character", "panelTitle", h=30)))
    body.append((sh.body, UI.theme_separator(P + "Sep", theme="sky")))
    body.append((sh.body, "Group #%sRow { Anchor: (Height: 44, Top: 8); LayoutMode: Left; }" % P))
    body.append((P + "Row", 'TextButton #%sOk { Anchor: (Width: 200, Height: 44); Padding: (Horizontal: 24); Text: "Primary"; %s }'
                 % (P, UI.theme_button_style("primary", theme="sky"))))
    body.append((P + "Row", "Group { Anchor: (Width: 16); }"))
    body.append((P + "Row", 'TextButton #%sNo { Anchor: (Width: 200, Height: 44); Padding: (Horizontal: 24); Text: "Secondary"; %s }'
                 % (P, UI.theme_button_style("secondary", theme="sky"))))
    body.append((sh.body, "Group #%sList { Anchor: (Height: 300, Top: 8); LayoutMode: TopScrolling; ScrollbarStyle: %s; Background: %s; "
                          "Padding: (Full: 8); }" % (P, UI.theme_scrollbar_style(theme="sky"), UI.theme_bg("inset", "sky"))))
    for i in range(6):
        body.append((P + "List", 'TextButton #%sR%d { Anchor: (Height: 36, Bottom: 4); Text: "Row %d"; %s }' % (
            P, i, i + 1, UI.theme_row_style("selected" if i == 0 else "normal", "sky"))))
    page = UI.Appends(list(sh.appends) + list(bar) + list(body))
    return sh, bar, page


def phase_page():
    sh, bar, page = self_test_page()
    UI.check_page(page, P)
    check(True, "self-test page: check_page (markup rules, every parent exists, no duplicate id)")
    toks = UI.assert_proven(page, what="hub self-test page")
    check("element TextButton" in toks and "Left" in toks, "self-test page: proven properties only (%d tokens)" % len(toks))
    els = UI.check_sky_paths(page)
    check({"Header", "HeaderOrnament", "Frame_Character", "Tab", "Tab_Selected", "Close", "Tertiary", "ScrollTrack"} <= set(els),
          "self-test page uses the sky kit (%d elements)" % len(els))
    ship = UI.kit_texture_files(page)
    check(all(UI.SKY_JAR_DIR + e + "@2x.png" in ship for e in els), "every kit texture the page names is shipped")
    check(all(p.startswith(UI.CUSTOM) for p in ship), "every shipped texture is under Common/UI/Custom")
    allpaths = [m.group(0) for mk in UI._flat_markups(page) for m in UI._SKY_PATH_RE.finditer(UI.render(mk))]
    check(allpaths and not any(p.startswith('"../') for p in allpaths), "no texture path leaves Common/UI/Custom (%d paths)" % len(allpaths))
    # the bar: 8 tabs x >= 110 at 1080p
    tabs = [mk for _p, mk in bar if mk.startswith("TextButton")]
    check(len(tabs) == 8, "Character shows its 8 contract tabs (%d)" % len(tabs))
    tw = UI.hub_tab_width(sh.tabs_w, 8)
    check(tw >= 110 and 8 * tw + 7 * UI.HUB_TAB_GAP <= sh.tabs_w, "8 tabs of %d px fit the %d px strip (>= 110)" % (tw, sh.tabs_w))
    check(sh.w <= UI.MAX_PAGE_W and sh.h <= UI.MAX_PAGE_H, "the hub page fits a 1080p screen (%d x %d <= 1600 x 980)" % (sh.w, sh.h))
    check(sum(1 for mk in tabs if "Tab_Selected" in mk) == 1 and "Tab_Selected" in tabs[1], "only the active tab (Skills) is selected")
    check(UI.used_height(UI.Appends([(sh.body, mk) for _p, mk in page if _p == sh.body]), sh.body) <= sh.h - UI.TITLE_H - 2 * sh.pad,
          "the self-test body fits under the bar")
    # every hub at the target page (1200, sky) and at 1080p's 8 x 110 minimum
    for hub in UI.HUBS:
        n = len(UI.hub_tabs(hub))
        check(UI.assert_hub_fits(hub, 1200 - 2 * UI.THEME_PAD["sky"], "sky") >= 110, "hub %s (%d tabs) fits a 1200 sky page" % (hub, n))
        check(UI.HUB_DEFS[hub][1] and UI.HUB_FRAME[hub] in UI.SKY_EL, "hub %s has a command and a frame mood" % hub)
    check(UI.hub_tab_width(915, 8) == 110 and UI.hub_max_tabs(915) == 8 and UI.hub_max_tabs(914) == 7, "8 x 110 + 35 = 915 exactly")
    check(UI.assert_hub_fits("character", 960 - 2 * UI.CONTENT_PAD, "sky") >= 110, "the 960 Skills page fits 8 tabs (vanilla padding 17)")
    raises(lambda: UI.assert_hub_fits("character", 960 - 2 * UI.THEME_PAD["sky"], "sky"), ValueError,
           "a 960 page with the sky padding 24 is too narrow for 8 tabs (documented: 963+)")
    check(UI.assert_hub_fits("character", 963 - 48, "sky") == 110, "a 963 sky page fits 8 tabs")
    raises(lambda: UI.assert_hub_fits("character", 1200 - 34, "vanilla"), ValueError, "8 vanilla tabs (160 min) do not fit 1200")
    check(UI.assert_hub_page(960, 880, hub="character") == (960, 894), "assert_hub_page: +52 bar - 38 title = +14")
    raises(lambda: UI.assert_hub_page(1240, 980), ValueError, "assert_hub_page: a 980 page cannot take the bar without a trim")
    # labels: 16 px bold fits the tab, or shrinks to 12 (ShrinkTextToFit) - never past it
    for hub in UI.HUBS:
        rows = UI.hub_tabs(hub)
        for w_ in (1200 - 48, max(UI.THEME_TAB_MIN["sky"] * len(rows) + 5 * (len(rows) - 1), 300)):
            t_ = UI.hub_tab_width(w_, len(rows))
            room = t_ - 2 * UI.HUB_TAB_PAD
            for _t, _o, _m, lab, _c in rows:
                check(UI.hub_clean(lab) == lab, "label %r is plain proven text" % lab)
                if UI.text_width(lab, 16, bold=True) > room:
                    check(UI.text_width(lab, 12, bold=True) <= room, "label %r fits a %d px tab even at 12 px" % (lab, t_))
                else:
                    check(True, "label fits")
    check(UI.text_width(UI.HUB_MENU_TEXT, 14, bold=True, upper=True) <= UI.HUB_MENU_W - 16, "< Menu fits its button")
    j = UI.java_hub_build(sh, "skills", cls="@PKG@.HubBar")
    check(j == '@PKG@.HubBar.build(b, ev, "SkyyHt", "character", "skills", %d, this.playerRef.getUuid(), 3);' % sh.tabs_w,
          "java_hub_build line: %s" % j)
    raises(lambda: UI.java_hub_build(sh, "back"), ValueError, "a reserved word is never a tab id")
    raises(lambda: UI.hub_tab_key("character", "Skills"), ValueError, "tab ids are lowercase")
    check(UI.hub_tab_key("storage", "bank") == "hub:tab:storage:bank" and UI.hub_def_key("world") == "hub:def:world",
          "registry keys")
    # the vanilla-theme shell is a valid page too (pages that keep the old look)
    vs = UI.hub_shell(P + "V", 1100, 860, "settings", theme="vanilla")
    UI.check_page(vs.appends, P + "V")
    check(UI.check_sky_paths(vs.appends) == [], "vanilla hub shell: vanilla textures only")
    return sh


# ================================================================= phase 3: HubBar compiled + executed against HytaleServer.jar
def phase_java(sh):
    try:
        import jpype
        import jpype.imports  # noqa
        import skyybuild as B
        import serverjar
    except ImportError as e:
        print("java phase skipped: %s" % e)
        return
    os.environ["TEMP"] = os.environ["TMP"] = SCRATCH
    sj = serverjar.server_jar()
    out = os.path.join(SCRATCH, "classes")
    os.makedirs(out, exist_ok=True)
    jpype.startJVM(B._jvm(), "-XX:-UsePerfData", "-Xverify:all", "-Djava.io.tmpdir=" + SCRATCH,
                   "--add-opens=java.base/java.lang=ALL-UNNAMED", "--enable-native-access=ALL-UNNAMED",
                   classpath=[B.JAVASSIST, sj], convertStrings=True)
    Jc = jpype.JClass
    pool = Jc("javassist.ClassPool")(False)
    pool.appendSystemPath()
    pool.appendClassPath(sj)
    CtField, CtNewMethod = Jc("javassist.CtField"), Jc("javassist.CtNewMethod")
    for cn, th in (("skyyhubtest.HubBar", "sky"), ("skyyhubtest.HubBarV", "vanilla")):
        try:
            UI.install_hub_bar(pool, cn, CtField, CtNewMethod, theme=th).writeFile(out)
            check(True, "HubBar (%s) compiles with javassist against HytaleServer.jar" % th)
        except Exception as e:      # noqa
            FAILS.append("HubBar (%s) does not compile: %s" % (th, e))
            return
    loader = Jc("java.net.URLClassLoader")(jpype.JArray(Jc("java.net.URL"))([Jc("java.io.File")(out).toURI().toURL()]),
                                          Jc("java.lang.ClassLoader").getSystemClassLoader())
    H = Jc("skyyhubtest.HubBar", loader=loader)
    HV = Jc("skyyhubtest.HubBarV", loader=loader)
    TRUE, FALSE = Jc("java.lang.Boolean").TRUE, Jc("java.lang.Boolean").FALSE
    UUID = Jc("java.util.UUID")
    CHM = Jc("java.util.concurrent.ConcurrentHashMap")
    Jc("java.lang.System").getProperties().remove("skyy.bridge")
    seen = []

    @jpype.JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @jpype.JOverride
        def apply(self, x):
            return self.f(x)

    def opener(tab):
        def f(u):
            seen.append((tab, None if u is None else str(u)))
            return TRUE
        return Fn(f)

    def boom(u):
        raise RuntimeError("open failed on purpose")

    m = H.map()
    u = UUID.randomUUID()
    last = CHM()
    m.put("hub:last:" + str(u), last)
    for t, o, mod, lab, cmd in CHAR_TABS:
        op = opener(t)
        vis = None
        if t == "trees":
            op = None                   # no open Function: the command fallback
        elif t == "class":
            op = Fn(boom)               # open throws: the command fallback
        elif t == "pets":
            vis = Fn(lambda x: FALSE)   # hidden for this player
        elif t == "collections":
            vis = Fn(lambda x: TRUE)
        arr = H.put("character", t, mod, lab, o, cmd, op, vis)
        check(arr is not None and len(arr) == 6, "put(character, %s)" % t)
    e = m.get("hub:tab:character:skills")
    check(isinstance(e[0], str) and isinstance(e[1], str) and Jc("java.lang.Integer").class_.isInstance(e[2])
          and isinstance(e[3], str) and Jc("java.util.function.Function").class_.isInstance(e[4]) and e[5] is None, "a registry value is Object[]{String, String, Integer, String, Function, null} (java.lang / java.util)")
    check(H.put("character", "Bad", "M", "x", 5, None, None, None) is None, "put refuses an id with capitals")
    check(H.put("character", "back", "M", "x", 5, None, None, None) is None, "put refuses a reserved id")
    check(H.put("character", "odd", "M", "x", 5, None, "not a function", None) is None, "put refuses an open that is no Function")
    check(getattr(H, "def_")("character", "Character", "character", "") is not None
          and m.get("hub:def:character")[1] == "character", "def(hub) puts hub:def:<hub> = {title, command, icon}")
    # build() into the REAL builders = hub_bar_preview byte for byte
    ucb = Jc("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ueb = Jc("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    n = H.build(ucb, ueb, P, "character", "skills", sh.tabs_w, u, 3)
    vis_tabs = [(t, l, o) for t, o, _m, l, _c in CHAR_TABS if t != "pets"]
    want = UI.hub_bar_preview(P, vis_tabs, "skills", sh.tabs_w)
    got = [(str(c.selector), str(c.text if c.text is not None else c.data)) for c in ucb.getCommands()]
    check(n == 7 and len(got) == len(want), "build drew the 7 visible tabs (%d, %d commands)" % (n, len(got)))
    for (gs, gm), (wp, wm) in zip(got, want):
        check(gs == "#" + wp and gm == UI.render(wm), "build() == hub_bar_preview(): %s" % gm[:70])
        UI.check_markup(gm, prefix=P)
        UI.check_sky_paths([gm])
    evs = [(str(x.selector), str(x.data)) for x in ueb.getEvents()]
    check(evs[0][0] == "#%sHubMenu" % P and "hub:back" in evs[0][1], "the < Menu button is bound to hub:back (%s)" % (evs[0],))
    check(evs[1][0] == "#%sHubClose" % P and "hub:close" in evs[1][1], "the close X is bound to hub:close")
    ids = [t for t, _l, _o in sorted(vis_tabs, key=lambda r: r[2])]
    for k, t in enumerate(ids):
        check(evs[2 + k][0] == "#%sHubT%d" % (P, k) and ('hub:%s' % t) in evs[2 + k][1], "tab %d is bound to hub:%s" % (k, t))
    check(str(last.get("character")) == "skills", "build() remembered hub:last character -> skills")
    ucb2 = Jc("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ueb2 = Jc("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    H.build(ucb2, ueb2, P, "character", "skills", sh.tabs_w, u, 0)
    check(not any("HubMenu" in str(x.selector) or "HubClose" in str(x.selector) for x in ueb2.getEvents()),
          "parts 0: no binding on bar buttons the page does not have")
    # handle() routing and open() outcomes
    js = lambda a: '{"a":"%s"}' % a
    check(H.handle(None, js("refresh"), "character", "skills") is None, "handle: a page click is not a hub click (null)")
    check(str(H.handle(None, js("hub:close"), "character", "skills")) == "close", "handle: the X -> close")
    check(str(H.handle(None, js("hub:back"), "character", "skills")) == "close", "handle: < Menu without SkyyMenu -> close")
    m.put("config:def:SkyyMenu", "x")
    check(str(H.handle(None, js("hub:back"), "character", "skills")) == "close", "handle: < Menu with no player to run /skymenu -> close")
    m.remove("config:def:SkyyMenu")
    check(str(H.handle(None, js("hub:skills"), "character", "skills")) == "self", "handle: the active tab -> self")
    check(str(H.handle(None, js("hub:Nope"), "character", "skills")) == "failed", "handle: a bad tab id -> failed")
    del seen[:]
    check(str(H.handle(None, js("hub:stats"), "character", "skills")) == "bridge" and seen == [("stats", None)],
          "handle: another tab -> its bridge Function (%s)" % seen)
    del seen[:]
    check(str(H.open(None, u, "character", "accessories")) == "bridge" and seen == [("accessories", str(u))],
          "open: the bridge Function gets the player's UUID")
    check(str(H.open(None, u, "character", "trees")) == "nocmd", "open: no open Function -> the command fallback is reached")
    check(str(H.open(None, u, "character", "class")) == "nocmd", "open: a throwing open Function -> the command fallback")
    check(str(H.open(None, u, "character", "pets")) == "hidden", "open: a hidden tab is not opened")
    check(str(H.open(None, u, "character", "nothere")) == "missing", "open: no entry (mod not loaded) -> missing")
    H.put("character", "nocmd", "M", "No command", 95, None, None, None)
    check(str(H.open(None, u, "character", "nocmd")) == "failed", "open: no Function and no command -> failed")
    check(int(H.run(None, "skymenu")) == 1, "run: no player -> 1 (nothing runs)")
    # overflow: more tabs than fit -> the first that fit, the active tab kept last
    for i in range(12):
        H.put("market", "t%d" % i, "M", "Tab %d" % i, 10 + i, "x", opener("t%d" % i), None)
    ucb3 = Jc("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    n3 = H.build(ucb3, Jc("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")(), P, "market", "t11", 600, None, 0)
    want3 = UI.hub_bar_preview(P, [("t%d" % i, "Tab %d" % i, 10 + i) for i in range(12)], "t11", 600)
    got3 = [str(c.text if c.text is not None else c.data) for c in ucb3.getCommands()]
    check(n3 == UI.hub_max_tabs(600) == 5 and got3 == [UI.render(mk) for _p, mk in want3] and "Tab 11" in got3[-1],
          "overflow: 5 of 12 tabs at 600 px, the active t11 kept last")
    for w_ in (300, 599, 600, 914, 915, 926, 1152, 1600):
        for n_ in (1, 3, 8):
            check(int(H.tabWidth(w_, n_)) == UI.hub_tab_width(w_, n_), "tabWidth(%d, %d)" % (w_, n_))
        check(int(H.maxTabs(w_)) == UI.hub_max_tabs(w_, "sky") and int(HV.maxTabs(w_)) == UI.hub_max_tabs(w_, "vanilla"),
              "maxTabs(%d)" % w_)
    odd = "Caf" + chr(233) + ", Shop!"
    check(str(H.clean(odd)) == UI.hub_clean(odd) == "Caf Shop" and str(H.jsonStr(js("hub:x"), "a")) == "hub:x",
          "clean / jsonStr match the kit")
    # the vanilla class draws vanilla tabs
    ucb4 = Jc("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    HV.build(ucb4, Jc("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")(), P, "market", "t0", 900, None, 0)
    v4 = [str(c.text if c.text is not None else c.data) for c in ucb4.getCommands()]
    check(v4 and all("SkyyKit" not in s for s in v4) and "Common/Buttons/Primary.png" in v4[0], "the vanilla HubBar draws vanilla tabs")
    # removeAll: only this jar's own arrays go
    foreign = jpype.JArray(Jc("java.lang.Object"))(6)
    m.put("hub:tab:character:stats", foreign)
    ours = len(CHAR_TABS) + 1 + 12 + 1                 # 8 character + nocmd + 12 market + hub:def:character
    removed = int(H.removeAll())
    check(removed == ours - 1, "removeAll removed %d of our %d keys (the replaced one stays)" % (removed, ours))
    check(m.get("hub:tab:character:stats") is not None and m.get("hub:tab:character:skills") is None
          and m.get("hub:def:character") is None and not any(str(k).startswith("hub:tab:market:") for k in m.keySet()),
          "removeAll left the foreign array and nothing of ours")
    check(m.get("hub:last:" + str(u)) is not None, "removeAll never touches hub:last (SkyyMenu's)")

    # ---------------------------------------------------------------- kit 1.6: HubBar(row=True) executed
    for cn, th in (("skyyhubtest.HubRow", "sky"), ("skyyhubtest.HubRowV", "vanilla")):
        try:
            UI.install_hub_bar(pool, cn, CtField, CtNewMethod, theme=th, row=True).writeFile(out)
            check(True, "HubBar row=True (%s) compiles with javassist against HytaleServer.jar" % th)
        except Exception as e:      # noqa
            FAILS.append("HubBar row=True (%s) does not compile: %s" % (th, e))
            return
    loader2 = Jc("java.net.URLClassLoader")(jpype.JArray(Jc("java.net.URL"))([Jc("java.io.File")(out).toURI().toURL()]),
                                           Jc("java.lang.ClassLoader").getSystemClassLoader())
    R = Jc("skyyhubtest.HubRow", loader=loader2)
    RV = Jc("skyyhubtest.HubRowV", loader=loader2)
    UCB = lambda: Jc("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    UEB = lambda: Jc("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    cmds = lambda b_: [(str(c.selector), str(c.text if c.text is not None else c.data)) for c in b_.getCommands()]
    evsel = lambda e_: [(str(x.selector), str(x.data)) for x in e_.getEvents()]
    m2 = R.map()
    for k in list(m2.keySet()):
        if str(k).startswith("hub:"):
            m2.remove(k)
    rw = 1218
    # no hub:def at all (no SkyyMenu): the bar shows the hub title
    b0 = UCB()
    check(int(R.buildRow(b0, UEB(), P, "world", rw, None)) == 0
          and cmds(b0) == [("#" + p_, UI.render(mk)) for p_, mk in UI.hub_row_preview(P, [], "world", rw)],
          "buildRow without any hub:def = the hub's title label")
    # SkyyMenu's defs (Home + 7, Character with its default tab)
    for i, t in zip(UI.HUB_ROW_IDS, UI.HUB_ROW_TITLES):
        d = R.def4(i, t, "skymenu" if i == "home" else UI.HUB_DEFS[i][1], "Skyy_Menu_Icon_%s" % t, "skills" if i == "character" else None)
        check(d is not None and len(d) == 4, "def4(%s) = {title, command, icon, default tab}" % i)
    check(str(R.defTab("character")) == "skills" and R.defTab("world") is None and R.defTab("nothere") is None, "defTab reads element 3")
    check(R.def4("character", "C", "c", "x", "Bad Tab")[3] is None, "def4 drops a bad default tab id")
    R.def4("character", "Character", "character", "Skyy_Menu_Icon_Character", "skills")
    check([str(x[0]) for x in R.hubs()] == list(UI.HUB_ROW_IDS), "hubs(): Home first, then the hubs in contract order")
    for hub, w_ in (("home", 1218), ("world", 754), ("character", 1064)):
        b1, e1 = UCB(), UEB()
        n1 = int(R.buildRow(b1, e1, P, hub, w_, None))
        want = UI.hub_row_preview(P, ROW_DEFS, hub, w_)
        got = cmds(b1)
        check(n1 == 8 and got == [("#" + p_, UI.render(mk)) for p_, mk in want],
              "buildRow(%s, %d) == hub_row_preview byte for byte (%d)" % (hub, w_, len(got)))
        for _s, mk in got:
            UI.check_markup(mk, prefix=P)
        ev1 = evsel(e1)
        check([s_ for s_, _d in ev1] == ["#%sHubR%d" % (P, k) for k in range(8)]
              and all(("hub:h:" + i) in d_ for (s_, d_), i in zip(ev1, UI.HUB_ROW_IDS)), "row bindings a = hub:h:<id> (%s)" % hub)
    bv = UCB()
    RV.buildRow(bv, UEB(), P, "home", 1218, None)
    check(cmds(bv) == [("#" + p_, UI.render(mk)) for p_, mk in UI.hub_row_preview(P, ROW_DEFS, "home", 1218, "vanilla")]
          and not any("SkyyKit" in mk for _s, mk in cmds(bv)), "the vanilla row = its preview, vanilla textures")
    # build2: row + X + the tab strip with icons
    u2 = UUID.randomUUID()
    last2 = CHM()
    m2.put("hub:last:" + str(u2), last2)
    for t, o, mod, lab, cmd in CHAR_TABS:
        if t in ("pets", "skills"):
            R.putIcon("character", t, mod, lab, o, cmd, opener(t), None, "character_" + t)
        elif t == "trees":
            check(len(R.putIcon("character", t, mod, lab, o, cmd, opener(t), None, "bad name")) == 6,
                  "putIcon with a bad icon name = the plain 6-element tab")
        else:
            R.put("character", t, mod, lab, o, cmd, opener(t), None)
    e_ = m2.get("hub:tab:character:pets")
    check(len(e_) == 7 and str(e_[6]) == "character_pets" and str(R.iconOf(e_)) == "character_pets"
          and R.iconOf(m2.get("hub:tab:character:stats")) is None, "putIcon stores element 6, iconOf reads it")
    b2, e2 = UCB(), UEB()
    n2 = int(R.build2(b2, e2, P, "character", "pets", 1066, u2, 6, 1064))
    tabs8 = [(t, l, o) for t, o, _m, l, _c in CHAR_TABS]
    want2 = list(UI.hub_row_preview(P, ROW_DEFS, "character", 1064)) + list(UI.hub_bar_preview2(
        P, tabs8, "pets", 1066, icons={"pets": "character_pets", "skills": "character_skills"}))
    got2 = cmds(b2)
    check(n2 == 8 and got2 == [("#" + p_, UI.render(mk)) for p_, mk in want2],
          "build2 == row + hub_bar_preview2 byte for byte (%d commands)" % len(got2))
    try:
        UI.check_sky_paths([mk for _s, mk in got2], tab_icons=True)
        check(True, "build2 output: every path a kit element or the tab icon hook")
    except Exception as ex:     # noqa
        FAILS.append("build2 paths: %s" % ex)
    ev2 = evsel(e2)
    check(ev2[0][0] == "#%sHubClose" % P and not any("HubMenu" in s_ for s_, _d in ev2) and len(ev2) == 1 + 8 + 8,
          "build2 parts 6: the X + 8 row + 8 tab bindings, no < Menu (%d)" % len(ev2))
    check(str(last2.get("character")) == "pets", "build2 remembers hub:last")
    b3 = UCB()
    check(int(R.build2(b3, UEB(), P, "home", None, 0, u2, 6, 1218)) == 0
          and all(s_ == "#%sHubRow" % P or s_.startswith("#%sHubR" % P) for s_, _m in cmds(b3)), "build2 on home: row 1 only, no tab strip")
    # pickTab: default -> last -> first (Skyy 2026-10-15 "id do skills as the default one": the default tab beats the remembered one)
    check(str(R.pickTab("character", u2)) == "skills", "pickTab: the default tab (Skills) beats the last tab (Pets)")
    R.def4("character", "Character", "character", "x", None)
    check(str(R.pickTab("character", u2)) == "pets", "pickTab: no default -> the last tab while shown")
    last2.put("character", "gone")
    check(str(R.pickTab("character", u2)) == "stats", "pickTab: no default + a stale last tab -> the first shown tab")
    R.def4("character", "Character", "character", "x", "skills")
    check(str(R.pickTab("character", u2)) == "skills", "pickTab: the default tab while the last one is gone")
    check(R.pickTab("market", u2) is None, "pickTab: a hub with no tab -> null")
    # goHub / route
    js = lambda a: '{"a":"%s"}' % a
    del seen[:]
    check(str(R.goHub(None, "character")) == "bridge" and seen == [("skills", None)],
          "goHub(character) opens its default tab through the Function (%s)" % seen)
    check(str(R.goHub(None, "market")) == "nocmd", "goHub(a hub with no tab) runs its hub:def command (no CommandManager here: nocmd)")
    m2.remove("hub:def:storage")
    check(str(R.goHub(None, "storage")) == "missing", "goHub: no tab and no def -> missing")
    check(str(R.goHub(None, "home")) == "close", "goHub(home) with no player to run /skymenu -> close")
    check(str(R.goHub(None, "Bad")) == "failed", "goHub: a bad hub id -> failed")
    check(str(R.route(None, js("hub:h:character"), "character", "pets")) == "self", "route: the page's own hub -> self")
    del seen[:]
    check(str(R.route(None, js("hub:h:character"), "world", "teleport")) == "bridge" and seen == [("skills", None)],
          "route: another hub -> goHub")
    check(str(R.route(None, js("hub:close"), "character", "pets")) == "close" and str(R.route(None, js("hub:pets"), "character", "pets")) == "self"
          and R.route(None, js("refresh"), "character", "pets") is None, "route falls through to handle() for the X / tabs / page clicks")
    n_rm = int(R.removeAll())
    check(n_rm >= 15 and not any(str(k).startswith("hub:tab:character:") or str(k).startswith("hub:def:") for k in m2.keySet()),
          "removeAll removes the row class's defs + tabs (%d keys)" % n_rm)


# ================================================================= phase 4: kit 1.6 (the hub row) - python side
def committed_kit():
    """the committed tools/skyyui.py (git HEAD) as a second module, or None when git / the file is not available"""
    try:
        src = subprocess.run(["git", "show", "HEAD:tools/skyyui.py"], cwd=os.path.dirname(HERE), capture_output=True, check=True).stdout
    except Exception as e:      # noqa
        print("phase 4: git not available - the committed-kit compare is skipped (%s)" % e)
        return None
    f = os.path.join(SCRATCH, "skyyui_head.py")
    open(f, "wb").write(src)
    spec = importlib.util.spec_from_file_location("skyyui_head", f)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, HERE)
    spec.loader.exec_module(m)
    m.SKY_ART_DIR, m.KIT_DIR = UI.SKY_ART_DIR, UI.KIT_DIR     # the art folder of the repo, not of the scratch copy
    m.verify(quiet=True)
    return m


ROW_DEFS = [(i, t, "Skyy_Menu_Icon_%s" % t) for i, t in zip(UI.HUB_ROW_IDS, UI.HUB_ROW_TITLES)]


def phase_row():
    check(UI.KIT_VERSION == "1.5" and UI.KIT_HUB_VERSION == "1.6", "kit 1.6 is additive: KIT_VERSION stays 1.5 (41 builders assert it)")
    old = committed_kit()
    if old is not None and not hasattr(old, "KIT_HUB_VERSION"):
        check(old.hub_bar_java() == UI.hub_bar_java() and old.hub_bar_java("vanilla") == UI.hub_bar_java("vanilla"),
              "COMPAT: hub_bar_java() (sky + vanilla) == the committed kit 1.5 source")
        check(UI.hub_bar_java(row=True)[:len(UI.hub_bar_java())] == UI.hub_bar_java(), "COMPAT: row=True only APPENDS members")
        check(old.hub_bar_java_core() == UI.hub_bar_java_core(), "COMPAT: SkyyCore's shared HubBar source unchanged")
        for hub in UI.HUBS:
            for th in ("sky", "vanilla"):
                for menu in (True, False):
                    a = old.hub_shell(P, 1400, 900, hub, theme=th, menu=menu)
                    b = UI.hub_shell(P, 1400, 900, hub, theme=th, menu=menu)
                    check(list(a.appends) == list(b.appends) and (a.inner_h, a.tabs_w, a.parts) == (b.inner_h, b.tabs_w, b.parts),
                          "COMPAT: hub_shell(%s, %s, menu=%s) byte-identical" % (hub, th, menu))
            tabs = [(t, l, o) for t, o, _m, l, _c in UI.hub_tabs(hub)]
            check(list(old.hub_bar_preview(P, tabs, tabs[0][0], 1152)) == list(UI.hub_bar_preview(P, tabs, tabs[0][0], 1152)),
                  "COMPAT: hub_bar_preview(%s) byte-identical" % hub)
            check(list(UI.hub_bar_preview2(P, tabs, tabs[0][0], 1152)) == list(UI.hub_bar_preview(P, tabs, tabs[0][0], 1152)),
                  "hub_bar_preview2 without icons == the kit 1.5 strip (%s)" % hub)
        sh5 = old.hub_shell(P, 1200, 900, "character")
        check(old.java_hub_build(sh5, "skills") == UI.java_hub_build(UI.hub_shell(P, 1200, 900, "character"), "skills"),
              "COMPAT: java_hub_build on a 1.5 shell unchanged")
        check(old.check_sky_paths(sh5.appends) == UI.check_sky_paths(sh5.appends), "COMPAT: check_sky_paths unchanged by default")
    elif old is not None:
        print("phase 4: the committed kit is already 1.6 - the 1.5 byte compare is skipped")
    # the row shells: Home (no tabs) and a hub (tabs) at the menu's page sizes
    for hub, w, h in (("home", 1268, 616), ("world", 804, 704), ("social", 804, 980), ("settings", 1128, 980), ("character", 1114, 966)):
        sh = UI.hub_shell(P + "R", w, h, hub, row=True)
        UI.check_page(sh.appends, P + "R")
        UI.assert_proven(sh.appends, what="row shell " + hub)
        els = UI.check_sky_paths(sh.appends)
        check(sh.row and sh.row_w == w - 50 and sh.parts == UI.HUB_PART_ROW | UI.HUB_PART_CLOSE and sh.title is None,
              "row shell %s %d x %d: row %d px, parts row + close, no title label" % (hub, w, h, sh.row_w))
        bar = [mk for p_, mk in sh.appends if p_ == sh.bar]
        check(len(bar) == 1 and bar[0].startswith("Group #%sRHubRow { Anchor: (Left: 10, Top: -3, Width: %d, Height: 30); LayoutMode: Left; }" % (P, w - 50)),
              "row shell %s: #HubRow sits IN the 38 px title bar (%s)" % (hub, bar[:1]))
        check("HeaderOrnament" not in els and "Header" in els and "Close" in els and "HubMenu" not in str(list(sh.appends)),
              "row shell %s: Header bar + the close X, no < Menu, no crest (the row takes the bar)" % hub)
        if hub == "home":
            check(sh.tabs is None and sh.tabs_w == 0 and sh.inner_h == h - UI.TITLE_H - 48 and "Frame" in els,
                  "row shell home: no tab strip, the plain sky Frame")
            check(UI.java_hub_build(sh, None, cls="X") == 'X.build2(b, ev, "SkyyHtR", "home", null, 0, this.playerRef.getUuid(), 6, %d);' % (w - 50),
                  "java_hub_build on the Home shell = build2 with no tab")
            raises(lambda: UI.java_hub_build2(sh, "stats"), ValueError, "Home has no tabs")
        else:
            five = UI.hub_shell(P + "R", w, h, hub)
            check((sh.w, sh.h, sh.inner_w, sh.inner_h, sh.tabs_w) == (five.w, five.h, five.inner_w, five.inner_h, five.tabs_w),
                  "row shell %s: the same page / body / strip size as the kit 1.5 shell (the page does not grow)" % hub)
            check(UI.assert_hub_page(w, h - UI.HUB_BAR_H, old_title_h=0, hub=hub, pad=24) == (w, h), "assert_hub_page(%s) unchanged" % hub)
            check(UI.java_hub_build(sh, "x" if hub != "world" else "teleport", cls="X").startswith('X.build2(b, ev, "SkyyHtR", "%s", ' % hub),
                  "java_hub_build on a row shell = build2")
        bw, icon = UI.assert_hub_row_fits(sh.row_w)
        check(bw >= 88 and icon, "row 1 at %d px: 8 buttons of %d px with icons" % (w, bw))
        pv = UI.hub_row_preview(P + "R", ROW_DEFS, hub, sh.row_w)
        page = UI.Appends(list(sh.appends) + list(pv))
        UI.check_page(page, P + "R")
        UI.assert_proven(page, what="row preview")
        check({"Primary", "Tertiary"} <= set(UI.check_sky_paths(pv)), "row %s: Tertiary buttons + the active one Primary" % hub)
        btn = [mk for _p, mk in pv if mk.startswith("Button")]
        check(len(btn) == 8 and sum(1 for mk in btn if "SkyyKit/Primary.png" in mk) == 1, "row %s: 8 buttons, one Primary" % hub)
    raises(lambda: UI.hub_shell(P, 1200, 900, "home"), ValueError, "home without row=True is refused (no kit 1.5 home)")
    raises(lambda: UI.assert_hub_row_fits(500), ValueError, "row 1 refuses a page too narrow for 8 buttons")
    check(UI.assert_hub_row_fits(704)[1] is False, "a narrow row drops the icons (labels only)")
    # tab icon hook paths
    check(UI.hub_tab_icon_paths("character", "pets") == ("SkyyHubTabs/character_pets.png", "SkyyHubTabs/character_pets_on.png",
          "Common/UI/Custom/SkyyHubTabs/character_pets@2x.png", "Common/UI/Custom/SkyyHubTabs/character_pets_on@2x.png"), "tab icon paths")
    check(UI.hub_tab_icon_ok("world_teleport") and not UI.hub_tab_icon_ok("world_close") and not UI.hub_tab_icon_ok("World_x")
          and not UI.hub_tab_icon_ok("a_b_c"), "tab icon names: <hub>_<tab> only")
    tabs = [(t, l, o) for t, o, _m, l, _c in UI.hub_tabs("character")]
    iv = UI.hub_bar_preview2(P + "I", tabs, "pets", 1066, icons={"pets": "character_pets", "skills": "character_skills", "trees": "bad name"})
    raises(lambda: UI.check_sky_paths(iv), ValueError, "an icon path is refused by default (no art ships in kit 1.6)")
    check(set(UI.check_sky_paths(iv, tab_icons=True)) >= {"Tab", "Tab_Selected"}, "tab_icons=True accepts the hook paths")
    raises(lambda: UI.check_sky_paths(['Group { Background: "SkyyHubTabs/Nope.png"; }'], tab_icons=True), ValueError,
           "a malformed hook path is refused even with tab_icons=True")
    raises(lambda: UI.check_sky_paths(['Group { Background: "../SkyyHubTabs/world_x.png"; }'], tab_icons=True), ValueError,
           "a hook path outside Common/UI/Custom is refused")
    sh = UI.hub_shell(P + "I", 1114, 966, "character", row=True)
    UI.check_page(UI.Appends(list(sh.appends) + list(iv)), P + "I")
    UI.assert_proven(iv, what="icon tabs")
    ib = [mk for p_, mk in iv if mk.startswith("Button")]
    check(len(ib) == 2 and "Tab_Selected" in [mk for mk in ib if "HubT4" in mk][0], "icon tabs: Skills + Pets are Buttons, Pets selected")
    check(any('"SkyyHubTabs/character_pets_on.png"' in mk for _p, mk in iv) and any('"SkyyHubTabs/character_skills.png"' in mk for _p, mk in iv),
          "the active tab uses the _on icon, the others the plain one")
    check(sum(1 for _p, mk in iv if mk.startswith("TextButton")) == 6, "the other 6 tabs (a bad icon name too) stay kit 1.5 TextButtons")


def main():
    base = os.path.join(HERE, "dev", "scratch") + os.sep
    if not (SCRATCH + os.sep).lower().startswith(base.lower()) or SCRATCH.rstrip(os.sep).lower() == base.rstrip(os.sep).lower():
        raise SystemExit("--dir must be a folder inside tools/dev/scratch/ (it is emptied and deleted): " + SCRATCH)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH, exist_ok=True)
    try:
        phase_art()
        sh = phase_page()
        phase_row()
        if NOJAVA:
            print("java phase skipped (--no-java)")
        else:
            phase_java(sh)
    finally:
        if not KEEP:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    for f in FAILS:
        print("  FAIL:", f)
    print("%d ok, %d fail (%s)" % (OKS[0], len(FAILS), UI.kit_id()))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
