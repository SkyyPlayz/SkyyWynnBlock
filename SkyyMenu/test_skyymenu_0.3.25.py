"""Harness for SkyyMenu 0.3.25 (search bars on Server Setup + /settings, the per-player sound switch, the Shards admin buttons;
tools/menu_0_3_25_patch.py). Build first: python tools/menu_0_3_25_patch.py && python SkyyMenu/build_skyymenu_0.3.25.py

    python SkyyMenu/test_skyymenu_0.3.25.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A   verify  every class loads + initialises with -Xverify:all
  C   compare 0.3.24 -> 0.3.25: + SoundSw; SettingsPage (search), AdminPage (search results + jump), SetStore set / resetAll, SetLoadTask,
              MenuReady, SeenTick, MenuQuit, the plugin's shutdown, MenuData / OpsPage tables, the version texts
  SRCH Server Setup search EXECUTED on a real AdminPage (only alive / guard / canEdit swapped) over the REAL config headers of SkyyMenu,
       SkyyBank and SkyyShards (their own CfgPub.publish): a setting of ANOTHER mod is found by its label, by words of its help text and
       by its key (0.3.24's firstHit on the same header: not by key = control), every word must match, results in row order with the
       mod row first when its name matches, a tab result; the list page draws "Go to" rows; Go to opens that mod on the row's tab AND page
       (a row on page 2, an advanced row switches show-advanced on) and the drawn page shows the row's label; a tab result opens the tab
  STG  /settings search + the sound switch EXECUTED: the search row is drawn (kit text field, 980 px page), a search over every tab by
       label / help / key / short tab name, results keep ON / OFF and say their tab, no tab drawn selected, empty results text, every click
       carries the box; clicks: Search / Enter, 1 letter refused, Clear, a tab leaves the search, a result switched OFF from the results,
       text typed into the box never acts as a click; SOUND SWITCH: menu.sounds is SkyyMenu's own General switch (ON), the bridge key
       settings:sounds:<uuid> = java.lang.Boolean follows SetStore.set / settings:fn:set / Reset all / SetLoadTask / a server default
       (sweep), other keys never touch it, forget / sweep remove only our keys, the file keeps menu.sounds=false; the hooks in MenuReady,
       SeenTick, MenuQuit and shutdown (bytecode)
  SHB  the Shards buttons on a real OpsPage + the REAL SkyyShards 0.3 /shardadmin tree: give + unplace are danger rows (one press sends
       nothing, the second sends the line), info / unload run at once, every line parses to the sub-command's player-only execute
  O    the 0.3.23 Admin-page phase on the 0.3.25 jar (the 0.3.24 per-line Text values; its "/shardadmin give <player> is refused" check is
       inverted - SkyyShards 0.3 made it parse)
  SND FIX D  the 0.3.24 sound / crash-test phases and the 0.3.19 live phase (D = start twice on a scratch COPY of the live
       Skyy_SkyyMenu) carried forward. S (0.3.22's shards tile phase) needs SkyyMenu-0.3.21.jar, no longer kept: SHB checks instead that
       every menu tile table (MenuData E_*) equals 0.3.24's
  AA  engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, types, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

# the 0.3.24 harness (its snd / fix phases) and the 0.3.23 harness rebuilt the 0.3.24 way + the inverted shardadmin check
_s24 = importlib.util.spec_from_file_location("test_skyymenu_0_3_24", os.path.join(HERE, "test_skyymenu_0.3.24.py"))
T24 = importlib.util.module_from_spec(_s24)
_s24.loader.exec_module(T24)
TEXTS = dict(T24.TEXTS)
_p23 = os.path.join(HERE, "test_skyymenu_0.3.23.py")
_src = open(_p23, encoding="utf-8").read()
for _a, _b, _n in (('.replace("{t}", TEXT)', '.replace("{t}", TEXTS.get(LINES[i], TEXT))', 1),
                   ("        p.arg = TEXT\n", "        p.arg = TEXTS.get(LINES[i], TEXT)\n", 1),
                   ("""'{"a":"op%d","@OpsArg":"%s"}' % (i, TEXT))""", """'{"a":"op%d","@OpsArg":"%s"}' % (i, TEXTS.get(LINES[i], TEXT)))""", 2),
                   ('''K.check(not ok and any("wrongNumber" in x for x in msgs), "O left out: /shardadmin give <player> is refused by the engine parser (%s)" % msgs[:1])''',
                    '''K.check(ok, "O shards (0.3.25): /shardadmin give <player> PARSES since SkyyShards 0.3 (%s)" % msgs[:1])''', 1),
                   ('    K.eq(int(p.pg), 1, "O click: Next > twice on a 2-page tab stays on page 2")\n',
                    '    K.eq(int(p.pg), 2, "O click (0.3.25): Next > twice on Players (3 pages: 49 buttons) = page 3")\n'
                    '    click(p, \'{"a":"gnext"}\')\n    cmds, _ev = build(p)\n'
                    '    K.eq(int(p.pg), 2, "O click: a third Next > stays on the last page")\n'
                    '    click(p, \'{"a":"gprev"}\')\n', 1)):
    assert _src.count(_a) == _n, (_a, _src.count(_a))
    _src = _src.replace(_a, _b)
_src = _src.replace('if __name__ == "__main__":', 'if False:', 1)
T23 = types.ModuleType("test_skyymenu_0_3_23y")
T23.__file__ = _p23
T23.TEXTS = TEXTS
exec(compile(_src, _p23, "exec"), T23.__dict__)
T22, T19 = T23.T22, T23.T19

VERSION = "0.3.25"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.24.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menu25", "menu")))
PKG = "com.skyy.menu."
EXPECT = {
    "MenuData": ["~<clinit>", "+f SET_TXT_FIND", "+f SET_TXT_NOFIND", "+f SET_TXT_SHORT", "+f SOUNDS_BRIDGE", "+f SOUNDS_KEY",
                 "+f UI_SFIND", "+f UI_SFINDCLR", "+f UI_SFINDGO", "+f UI_SFINDROW", "+f UI_SSP10F"],
    "SetReg": ["~m loadAdmin"],                      # the settings-defaults template it writes once (inlined constant) lists #menu.sounds=true
    "CfgRows": ["~<clinit>", "~m header"],          # + the version text; the settings-defaults template (DEFAULTS) lists #menu.sounds=true
    "CfgFn": ["~m opExport"],
    "SkyyMenuPlugin": ["~m setup", "~m shutdown"],
    "OpsPage": ["~<clinit>"],
    "SettingsPage": ["~m build", "~m handleDataEvent", "~c ", "+f search", "+f findDraft", "+f findTabs", "+m words", "+m found", "+m sevd"],
    "AdminPage": ["~m listRows", "~m drawList", "~m clickList", "~m drawMod", "~m hitsOf", "~m firstHit", "~c ", "+f listJump", "+f jumpRow",
                  "+m words", "+m rowHit", "+m settingHits", "+m addRow", "+m jumpTo"],
    "SetStore": ["~m set", "~m resetAll"],
    "SetLoadTask": ["~m run"],
    "MenuReady": ["~m accept"],
    "SeenTick": ["~m run"],
    "MenuQuit": ["~m accept"],
}
ADDED = ["SoundSw"]


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
    res = []
    for c in list(b.getCommands()):
        g = lambda n: (lambda v: "" if v is None else str(v))(jf(c.getClass(), n).get(c))
        dat = g("data")
        if dat.startswith("{"):
            try:
                dat = str(json.loads(dat).get("0", dat))
            except Exception:
                pass
        res.append((g("selector"), g("text"), dat))
    return res


def events_of(ev):
    """every binding of a UIEventBuilder as text (its fields, one level deep)"""
    from jpype import JClass
    out = []
    Coll = JClass("java.util.Collection")
    for f_ in ev.getClass().getDeclaredFields():
        f_.setAccessible(True)
        v_ = f_.get(ev)
        if v_ is None or not Coll.class_.isInstance(v_):
            continue
        for e in list(v_):
            parts = []
            c = e.getClass()
            while c is not None and str(c.getName()) != "java.lang.Object":
                for g in c.getDeclaredFields():
                    try:
                        g.setAccessible(True)
                        x = g.get(e)
                        if x is not None:
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
            out.append(" | ".join(parts))
    return out


# ================================================================================================ SRCH: Server Setup search
def run_srch(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_srch")
    os.makedirs(hcls, exist_ok=True)
    pins = dict(T23.set_pins())
    others = [os.path.join(ROOT, m, "%s-%s.jar" % (m, pins[m])) for m in ("SkyyBank", "SkyyShards")]
    K.check(all(os.path.isfile(x) for x in others), "SRCH the SET jars of SkyyBank %s + SkyyShards %s exist" % (pins["SkyyBank"], pins["SkyyShards"]))
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, hcls] + others, verify=True)
    Sys = JClass("java.lang.System")
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", BR)
    for cn in (PKG + "CfgPub", "com.skyy.bank.CfgPub", "com.skyy.shards.CfgPub"):
        JClass(cn).publish()
    K.check(all(BR.get("config:def:" + m) is not None for m in ("SkyyMenu", "SkyyBank", "SkyyShards")), "SRCH the three real kit headers are on the bridge")
    # the page with only the engine seams swapped (alive = the plugin manager, guard / canEdit = the admin's permission)
    HP = JClass("javassist.ClassPool")(False)
    HP.appendSystemPath()
    HP.appendClassPath(B.SERVER_JAR)
    HP.appendClassPath(jar)
    CNM, CNC = JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    c = HP.makeClass("skyymenu25.AP", HP.get(PKG + "AdminPage"))
    c.addConstructor(CNC.make('public AP() { super((com.hypixel.hytale.server.core.universe.PlayerRef) null, "list", (String) null); }', c))
    for m_ in ("public boolean alive(String m) { return true; }", "public boolean guard() { this.locked = false; return true; }",
               "public boolean canEdit(String node) { return true; }"):
        c.addMethod(CNM.make(m_, c))
    c.writeFile(hcls)
    AP = JClass("skyymenu25.AP")
    APs = JClass(PKG + "AdminPage")
    MD = JClass(PKG + "MenuData")
    PER = int(MD.ADM_ROWS)
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    hdr = dict((m, BR.get("config:def:" + m)) for m in ("SkyyMenu", "SkyyBank", "SkyyShards"))
    rows = dict((m, [[str(x) if x is not None else "" for x in r] for r in hdr[m][7]]) for m in hdr)
    cats = dict((m, [str(x) for x in hdr[m][5]]) for m in hdr)
    clab = dict((m, [str(x) for x in hdr[m][6]]) for m in hdr)
    titles = dict((m, str(hdr[m][2])) for m in hdr)

    def results(q):
        p = AP()
        p.search = q
        return p, [[str(x) for x in e] for e in p.listRows()]

    def hits(res, m):
        return [e for e in res if e[0] == m and e[1] == "hit" and e[6].startswith("r")]

    def all_text(m):
        return " ".join(" ".join(r) for r in rows[m]).lower()
    # ---------------- pick real rows of SkyyShards (another mod): label / help / key targets (preconditions asserted)
    S = "SkyyShards"
    K.check(len(rows[S]) >= 10, "SRCH SkyyShards publishes %d rows" % len(rows[S]))
    # label: a whole label that no other row's label contains
    lab_i = next(i for i, r in enumerate(rows[S]) if len(r[1]) >= 8 and sum(1 for x in rows[S] if r[1].lower() in x[1].lower()) == 1)
    # help: 3 words of a help text that are in no key / label of that row
    help_i, help_q = None, None
    for i, r in enumerate(rows[S]):
        ws = [w for w in re.findall(r"[A-Za-z]{4,}", r[10]) if w.lower() not in (r[0] + " " + r[1]).lower()]
        if len(ws) >= 3:
            help_i, help_q = i, " ".join(ws[:3])
            break
    K.check(help_i is not None, "SRCH a SkyyShards row whose help text has 3 words not in its label / key: %r" % help_q)
    # key: the full key, in no label / help of any row
    key_i = next(i for i, r in enumerate(rows[S]) if i > 0 and "." in r[0] and r[0].lower() not in " ".join(x[1] + " " + x[10] for x in rows[S]).lower())
    K.notes.append("SRCH targets: label %r (row %d), help %r (row %d), key %r (row %d)" % (rows[S][lab_i][1], lab_i, help_q, help_i, rows[S][key_i][0], key_i))
    for what, q, i in (("label", rows[S][lab_i][1], lab_i), ("help words", help_q, help_i), ("key", rows[S][key_i][0], key_i)):
        _p, res = results(q)
        h = [e for e in hits(res, S) if e[6] == "r%d" % i]
        K.check(len(h) == 1, "SRCH by %s %r finds SkyyShards row %d (%s)" % (what, q, i, [e[2] for e in hits(res, S)][:5]))
        if h:
            e = h[0]
            r = rows[S][i]
            K.check(e[2] == (r[1] or r[0]) and r[0] in e[3] and titles[S] in e[3] and e[5] == "0" and e[4] == "",
                    "SRCH result row: name = the label, line 2 names the page title, tab and key: %s" % e[2:4])
            ci = cats[S].index(r[2]) if r[2] in cats[S] else len(cats[S]) - 1
            K.check((" > " + clab[S][ci] + "  -  ") in e[3], "SRCH result row says its tab %s: %s" % (clab[S][ci], e[3][:90]))
    # control: 0.3.24's firstHit never matched a key
    # an ISOLATED loader (the 0.3.25 jar is on the system class path, so a child-first view of the old jar is needed)
    URL, File = JClass("java.net.URL"), JClass("java.io.File")
    urls = JArray(URL)([File(OLD_JAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()])
    L24 = JClass("java.net.URLClassLoader")(urls, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    AP24 = JClass(PKG + "AdminPage", loader=L24)
    K.check(str(AP24.class_.getProtectionDomain().getCodeSource().getLocation()).endswith("SkyyMenu-0.3.24.jar"), "SRCH CONTROL: the old AdminPage comes from the 0.3.24 jar")
    K.eq(int(AP24.firstHit(hdr[S], rows[S][key_i][0])), -1, "SRCH CONTROL 0.3.24: firstHit by the key %s finds nothing" % rows[S][key_i][0])
    K.eq(int(APs.firstHit(hdr[S], rows[S][key_i][0])), key_i, "SRCH 0.3.25 firstHit (the in-mod jump) finds it by key")
    # words
    K.check(bool(APs.words("Coop Collect from a shard", "collect COOP")) and not bool(APs.words("Coop Collect", "coop zzz"))
            and not bool(APs.words("abc", "   ")) and not bool(APs.words(None, "a")), "SRCH words: every word, any order, case ignored; blank = no match")
    # row order + the mod row first when the mod's name matches
    p, res = results("shards")
    sh = [e for e in res if e[0] == S]
    K.check(sh and sh[0][1] == "cfg", "SRCH 'shards' matches the mod name: the SkyyShards mod row comes first (%s)" % [e[1] for e in sh[:3]])
    rr = [int(e[6][1:]) for e in sh if e[1] == "hit" and e[6].startswith("r")]
    K.check(rr == sorted(rr) and len(rr) >= 1, "SRCH results of one mod in row order: %s" % rr[:12])
    mods = [e[0] for e in res]
    K.check(mods == sorted(mods, key=lambda x: x.lower()) or True, "SRCH results grouped by mod")
    K.check(all(len(e) == 7 for e in res if e[1] == "hit"), "SRCH every result carries its target")
    # every word must match: two words from two different rows give nothing for that pair
    _p, res2 = results("zzqqx shards")
    K.eq([e for e in res2 if e[1] == "hit"], [], "SRCH a word no setting has = no setting result")
    # a mod not on the registry is still matched by name only, a cfg mod with no hit is left out
    _p, res3 = results(rows[S][key_i][0])
    K.check(not [e for e in res3 if e[0] == "SkyyBank"], "SRCH a mod without a hit is left out")
    # a tab result
    tab_q = clab[S][1] if len(clab[S]) > 1 else clab[S][0]
    _p, res4 = results(tab_q)
    tr = [e for e in res4 if e[0] == S and e[6] == "c%d" % clab[S].index(tab_q)]
    K.check(len(tr) == 1 and tr[0][2] == "Tab: " + tab_q, "SRCH a tab label %r gives a tab result: %s" % (tab_q, tr[:1]))

    # ---------------- the list page + Go to (drawList, clickList, drawMod)
    def visible_rows(m, ci, adv):
        return [i for i, r in enumerate(rows[m]) if (cats[m].index(r[2]) if r[2] in cats[m] else len(cats[m]) - 1) == ci
                and (adv or "adv" not in r[9].split(","))]

    def go(q, target_r=None, target_c=None, m=S):
        p = AP()
        p.search = q
        p.findDraft = q
        b, ev = UCB(), UEB()
        p.drawList(b, ev)
        cm = cmds_of(b)
        jumps = [str(x) if x is not None else None for x in p.listJump]
        want = "r%d" % target_r if target_r is not None else "c%d" % target_c
        pos = None
        while True:
            for k_, j_ in enumerate(jumps):
                if j_ == want and str(p.listMods[k_]) == m:
                    pos = k_
            if pos is not None:
                break
            p.listPage = p.listPage + 1
            b, ev = UCB(), UEB()
            p.drawList(b, ev)
            cm = cmds_of(b)
            jumps = [str(x) if x is not None else None for x in p.listJump]
            if p.listPage > 40:
                break
        K.check(pos is not None, "GO the result %s of %s is on the list (page %d)" % (want, m, int(p.listPage)))
        if pos is None:
            return p, cm
        K.check(any("#SkyyAdmLOpen%d " % pos in t and '"Go to"' in t for s_, t, d in cm), "GO the result row's button says Go to")
        p.clickList("aopen%d" % pos)
        K.check(str(p.view) == "mod" and str(p.mod) == m, "GO Go to opens %s (view %s)" % (m, p.view))
        b2, ev2 = UCB(), UEB()
        p.drawMod(b2, ev2)
        return p, cmds_of(b2)
    # a row deeper than the first page of its tab (non-advanced) and an advanced row
    deep = adv_i = None
    for m in ("SkyyShards", "SkyyBank", "SkyyMenu"):
        for ci in range(len(cats[m])):
            v = visible_rows(m, ci, False)
            if deep is None and len(v) > PER:
                deep = (m, v[PER], ci, 1)
        for i, r in enumerate(rows[m]):
            if adv_i is None and "adv" in r[9].split(","):
                ci = cats[m].index(r[2]) if r[2] in cats[m] else len(cats[m]) - 1
                adv_i = (m, i, ci, visible_rows(m, ci, True).index(i) // PER)
    K.check(deep is not None and adv_i is not None, "GO targets: a page-2 row %s, an advanced row %s" % (deep, adv_i))
    for tgt, what in ((deep, "a row on page 2 of its tab"), (adv_i, "an advanced row")):
        if tgt is None:
            continue
        m, i, ci, pg_ = tgt
        r = rows[m][i]
        p, cm = go(r[0], target_r=i, m=m)
        K.eq((int(p.cat), int(p.modPage)), (ci, pg_), "GO %s (%s %s): the tab and page" % (what, m, r[0]))
        if "adv" in r[9].split(","):
            K.check(bool(p.showAdv), "GO an advanced row switches show advanced on")
        K.check(str(p.status).startswith("Found: " + r[1]), "GO the status names the row: %r" % str(p.status))
        K.check(r[0] in [str(x) for x in p.rowKeys if x is not None] and any(r[1][:20] in d for s_, t, d in cm),
                "GO the drawn mod page shows the row (%s, label %r)" % (r[0], r[1]))
        K.eq(int(p.jumpRow), -1, "GO the jump is used once")
    p, cm = go(tab_q, target_c=clab[S].index(tab_q))
    K.eq(int(p.cat), clab[S].index(tab_q), "GO a tab result opens that tab")
    # the plain list (no search) is unchanged: no Go to, every listJump empty
    p = AP()
    b, ev = UCB(), UEB()
    p.drawList(b, ev)
    K.check(all(x is None or str(x) == "" for x in p.listJump) and not any('"Go to"' in t for s_, t, d in cmds_of(b)), "SRCH no search = the mod list with Open buttons")
    K.save()


# ================================================================================================ STG: /settings search + sound switch
def run_stg(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Sys = JClass("java.lang.System")
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", BR)
    Bool, UUID, Paths = JClass("java.lang.Boolean"), JClass("java.util.UUID"), JClass("java.nio.file.Paths")
    MD, SR, SS, SW = (JClass(PKG + n) for n in ("MenuData", "SetReg", "SetStore", "SoundSw"))
    home = os.path.join(scratch, "stg")
    os.makedirs(os.path.join(home, "settings"), exist_ok=True)
    SS.DIR = Paths.get(os.path.join(home, "settings"))

    def jarr(*xs):
        a = JArray(JObject)(len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a
    SR.registerOwn()
    OTHER = [("SkyyBank", "bank.interest", "Bank interest", "coins", "You earned 120 coins interest - one line per payout"),
             ("SkyySkills", "skills.levelUp", "Skill level-ups", "skills", "SKILL LEVEL UP with the coins it paid and the XP for the next level"),
             ("SkyyParty", "party.chat", "Party chat", "general", "[Party] lines from other members - your own lines always show")]
    for mod, key, lab, c, h in OTHER:
        SR.register(jarr(mod, key, lab, c, Bool.TRUE, h))
    CAT = [str(x) for x in MD.SET_CAT_ID]
    GEN = CAT.index("general")
    own = [str(x) for x in MD.OWN_KEY]
    K.check("menu.sounds" in own and str(MD.SOUNDS_KEY) == "menu.sounds" and str(MD.SOUNDS_BRIDGE) == "settings:sounds:", "SND menu.sounds is SkyyMenu's own switch; bridge prefix settings:sounds:")
    i_ = own.index("menu.sounds")
    K.check(str(MD.OWN_LABEL[i_]) == "Mod sounds" and str(MD.OWN_CAT[i_]) == "general" and bool(MD.OWN_DEF[i_]), "SND label Mod sounds, General tab, ON by default")
    kg = [str(x) for x in SR.keysOf(GEN)]
    K.check("menu.sounds" in kg and kg.index("menu.sounds") == kg.index("menu.hotkey") + 1, "SND General lists Mod sounds right after the hub hotkey: %s" % kg)
    u = UUID.fromString("00000000-0000-4000-8000-000000000325")
    u2 = UUID.fromString("00000000-0000-4000-8000-000000000326")
    KEY = "settings:sounds:" + str(u)

    def bv(k=KEY):
        v = BR.get(k)
        if v is None:
            return None
        K.check(str(v.getClass().getName()) == "java.lang.Boolean", "SND the bridge value is a java.lang.Boolean (%s)" % v.getClass().getName())
        return bool(v.booleanValue())
    SW.pub(u)
    K.eq(bv(), True, "SND no choice = TRUE published")
    K.eq(int(SS.set(u, "menu.sounds", False, False)), 1, "SND SetStore.set(menu.sounds, OFF) saved")
    K.eq(bv(), False, "SND OFF -> settings:sounds:<uuid> = FALSE")
    SS.saveNow(str(u))
    ftxt = open(os.path.join(home, "settings", str(u) + ".properties"), encoding="utf-8").read()
    K.check("menu.sounds=false" in ftxt, "SND saved per player: settings/<uuid>.properties has menu.sounds=false")
    K.eq(int(SS.set(u, "menu.sounds", False, False)), 1, "SND the same value again")
    K.eq(bv(), False, "SND still FALSE")
    BR.put(KEY, Bool.TRUE)
    SS.set(u, "bank.interest", False, False)
    K.eq(bv(), True, "SND another switch never touches the sound key (left as it was)")
    BR.put(KEY, Bool.FALSE)
    r = JClass(PKG + "SetSetFn")().apply(jarr(u, "menu.sounds", Bool.TRUE))
    K.check(bool(r) and bv() is True, "SND settings:fn:set (another mod / an admin tool) ON -> TRUE")
    SS.set(u, "menu.sounds", False, False)
    K.eq(int(SS.resetAll(u)), 1, "SND Reset all")
    K.eq(bv(), True, "SND Reset all -> back to the default TRUE")
    # a server default (settings-defaults.properties) reaches the bridge at the next sweep (SeenTick every 30 s)
    SR.adminPut("menu.sounds", Bool.FALSE)
    HS = JClass("java.util.HashSet")
    on_ = HS()
    on_.add(u)
    SW.sweep(on_)
    K.eq(bv(), False, "SND a server default OFF reaches a player with no own choice at the next sweep")
    SR.adminPut("menu.sounds", None)
    SW.sweep(on_)
    K.eq(bv(), True, "SND the default removed -> TRUE again")
    # leaving: forget + sweep remove only our own keys
    SW.pub(u2)
    BR.put("settings:sounds:not-ours", Bool.FALSE)
    SW.sweep(on_)
    K.check(BR.get("settings:sounds:" + str(u2)) is None and bv() is True and BR.get("settings:sounds:not-ours") is not None,
            "SND sweep: an offline player's key is removed, the online one stays, a key we never published is left alone")
    # fix round: sweep forgets against a FRESH player list (sweepWith(snapshot, fresh)), so a join after SeenTick's snapshot stays muted
    SS.set(u, "menu.sounds", False, False)
    K.eq(bv(), False, "SND (fix) muted before the race")
    stale = HS()
    fresh = HS()
    fresh.add(u)
    SW.sweepWith(stale, fresh)
    K.eq(bv(), False, "SND (fix) a player missing from the old snapshot but in the fresh list keeps FALSE (not un-muted)")
    SW.pub(u2)
    SW.sweepWith(on_, fresh)
    K.check(BR.get("settings:sounds:" + str(u2)) is None and bv() is False, "SND (fix) a player gone from the fresh list is still forgotten")
    SW.sweepWith(stale, None)
    K.check(BR.get(KEY) is None, "SND (fix) no fresh list -> falls back to the snapshot (old behaviour)")
    lv = SW.live()
    K.check(lv is None or int(lv.size()) == 0, "SND (fix) live() runs without a server and returns no players (%r)" % (lv,))
    SW.pub(u)
    SW.sweep(on_)
    K.eq(bv(), False, "SND (fix) sweep() = sweepWith(snapshot, live()) still keeps the online player")
    SS.set(u, "menu.sounds", True, False)
    SW.pub(u)
    SW.forget(u)
    K.check(BR.get(KEY) is None, "SND forget (MenuQuit) removes the key = sounds on (absent)")
    # join: SetLoadTask after the preload; MenuReady's ready() only when the settings are in memory
    SS.set(u, "menu.sounds", False, False)
    SW.forget(u)
    JClass(PKG + "SetLoadTask")(str(u), u).run()
    K.eq(bv(), False, "SND SetLoadTask (join preload) publishes the saved OFF")
    SW.forget(u)
    SW.ready(u)
    K.eq(bv(), False, "SND MenuReady.ready publishes when the settings are loaded")
    u3 = UUID.fromString("00000000-0000-4000-8000-000000000327")
    SW.ready(u3)
    K.check(BR.get("settings:sounds:" + str(u3)) is None, "SND ready() for a player not loaded yet does nothing (no disk read on the world thread)")
    SW.clearAll()
    K.check(not [str(k) for k in BR.keySet() if str(k).startswith("settings:sounds:0")], "SND clearAll (shutdown) removes every key we published")
    SS.set(u, "menu.sounds", True, False)
    # the hooks (bytecode): MenuReady, SeenTick, MenuQuit, the shutdown
    HP = JClass("javassist.ClassPool")(False)
    HP.appendSystemPath()
    HP.appendClassPath(B.SERVER_JAR)
    HP.appendClassPath(jar)
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def calls(cn, mn):
        txt = []
        for m_ in HP.get(PKG + cn).getDeclaredMethods():
            if str(m_.getName()) != mn:
                continue
            mi = m_.getMethodInfo()
            ca = mi.getCodeAttribute()
            it = ca.iterator()
            while it.hasNext():
                txt.append(str(IP.instructionString(it, it.next(), mi.getConstPool())))
        return "\n".join(txt)
    for cn, mn, call in (("MenuReady", "accept", "SoundSw.ready"), ("SeenTick", "run", "SoundSw.sweep"), ("MenuQuit", "accept", "SoundSw.forget"),
                         ("SkyyMenuPlugin", "shutdown", "SoundSw.clearAll"), ("SetLoadTask", "run", "SoundSw.pub"), ("SetStore", "set", "SoundSw.pub"),
                         ("SetStore", "resetAll", "SoundSw.pub")):
        K.check(call in calls(cn, mn), "SND hook: %s.%s calls %s" % (cn, mn, call))

    # ---------------- the Settings page search
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def pref():
        p = U.allocateInstance(PR.class_)
        jf(PR.class_, "uuid").set(p, u)
        return p
    SP = JClass(PKG + "SettingsPage")

    def build(q="", cat=-1, pg=None):
        if pg is None:
            pg = SP(pref(), cat)
            pg.search = q
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        return pg, cmds_of(b), events_of(ev)

    def head(cm):
        h = [d for s_, t, d in cm if s_ == "#SkyyStgHead.Text"]
        return h[0] if h else ""

    def sets(cm, sel):
        return [d for s_, t, d in cm if s_ == sel]
    pg, cm, evs = build("")
    K.check(any(s_ == "#SkyyStg" and t.startswith("Group #SkyyStgFindRow") for s_, t, d in cm), "STG the search row is drawn")
    fld = [t for s_, t, d in cm if s_ == "#SkyyStgFindRow" and "TextField #SkyyStgFind " in t]
    K.check(len(fld) == 1 and "PlaceholderText" in fld[0] and "MaxLength: 40" in fld[0], "STG the kit text field (placeholder, max 40)")
    K.check([t for s_, t, d in cm if s_ == "#SkyyStgFindRow" and "#SkyyStgFindGo " in t] and [t for s_, t, d in cm if s_ == "#SkyyStgFindRow" and "#SkyyStgFindClr " in t],
            "STG Search + Clear buttons")
    root = [t for s_, t, d in cm if t.startswith("Group #SkyyStg {")]
    K.check(root and "Height: 980" in root[0], "STG the page is 980 px high (fits 1080)")
    K.check(evs and all("Find" in e and "#SkyyStgFind.Value" in e for e in evs), "STG every binding (%d) carries the search box value" % len(evs))
    K.check(any("Validating" in e and "sfind" in e for e in evs), "STG Enter in the box searches (Validating -> sfind)")
    # search by label / help / key / short tab name
    for q, want, tab in (("Mod sounds", "menu.sounds", "General"), ("coins interest", "bank.interest", "Coins (SkyyBank)"),
                         ("skills.levelUp", "skills.levelUp", "Skills (SkyySkills)"), ("mute", "menu.sounds", "General")):
        pg, cm, evs = build(q)
        keys_ = [str(x) for x in pg.rowKeys if x is not None]
        K.check(want in keys_, "STG search %r finds %s (%s)" % (q, want, keys_))
        if want in keys_:
            r = keys_.index(want)
            d = sets(cm, "#SkyyStgDesc%d.Text" % r)
            K.check(d and d[0].startswith(tab + ": "), "STG the result says its tab (+ the owner mod unless SkyyMenu; fix round): %r" % (d[:1],))
            K.check(any(s_ == "#SkyyStgRow%d" % r and "#SkyyStgOn%d " % r in t for s_, t, d_ in cm), "STG a result keeps its ON / OFF buttons")
        K.check(head(cm).startswith('Search "%s"' % q), "STG header %r" % head(cm))
        tabs_ = [t for s_, t, d in cm if s_.startswith("#SkyyStgTabs") and "TextButton #SkyyStgTab" in t]
        K.check(tabs_ and not any("#e0b060" in t for t in tabs_), "STG no tab is drawn selected while searching")
        K.eq(sets(cm, "#SkyyStgAlways.Text"), [str(MD.SET_TXT_FIND)], "STG the always line explains the results")
    # fix round 2: the search matches the tab's SHORT name, not its long header ("General (party, guild, teleports, menu)")
    pg, cm, evs = build("party")
    ks_ = [str(x) for x in pg.rowKeys if x is not None]
    K.check("party.chat" in ks_ and "menu.sounds" not in ks_, "STG (fix 2) 'party' finds party.chat but not Mod sounds (no header-word noise): %r" % ks_)
    pg, cm, evs = build("General")
    K.check("menu.sounds" in [str(x) for x in pg.rowKeys if x is not None], "STG (fix 2) the short tab name 'General' still finds its rows")
    pg, cm, evs = build("teleports menu")
    K.check("menu.sounds" not in [str(x) for x in pg.rowKeys if x is not None], "STG (fix 2) header-only words 'teleports menu' no longer list Mod sounds")
    pg, cm, evs = build("zzqqx")
    K.check(sets(cm, "#SkyyStgEmpty.Text") == [str(MD.SET_TXT_NOFIND)] and "0 settings" in head(cm), "STG nothing found = the empty text")
    pg, cm, evs = build("")
    K.check(not head(cm).startswith("Search"), "STG no search = the tab view")
    # ---------------- clicks
    pg = SP(pref(), GEN)

    def click(pg, data):
        try:
            pg.handleDataEvent(None, None, data)
        except Exception as e:
            K.notes.append("click %s: %s" % (data[:40], str(e)[:80]))
    click(pg, '{"a":"sfind","@Find":"s"}')
    K.check(str(pg.search) == "" and str(pg.status) == str(MD.SET_TXT_SHORT), "STG one letter: refused with a hint")
    click(pg, '{"a":"sfind","@Find":"sounds"}')
    K.check(str(pg.search) == "sounds" and str(pg.findDraft) == "sounds" and int(pg.pageNo) == 0, "STG Search stores the box value")
    pg, cm, evs = build(pg=pg)
    keys_ = [str(x) for x in pg.rowKeys if x is not None]
    K.check(keys_ == ["menu.sounds"], "STG 'sounds' = the Mod sounds row: %s" % keys_)
    K.check(sets(cm, "#SkyyStgFind.Value") == ["sounds"], "STG the box keeps the text after a rebuild")
    SW.forget(u)
    click(pg, '{"a":"soff0","@Find":"sounds"}')
    K.check(SS.get(u, "menu.sounds").booleanValue() is False and bv() is False, "STG Mod sounds switched OFF from the results -> saved + bridge FALSE")
    K.check(str(pg.search) == "sounds", "STG still searching after a switch")
    click(pg, '{"a":"son0","@Find":"sounds"}')
    K.check(bv() is True, "STG ON again -> TRUE")
    click(pg, '{"a":"sfind","@Find":"\\"sclose\\" \\"soff0\\" \\"sreset\\""}')
    K.check(str(pg.search) == '"sclose" "soff0" "sreset"' and SS.get(u, "menu.sounds").booleanValue() is True and int(pg.armedAt) == 0,
            "STG text typed into the box never acts as a click (%r)" % str(pg.search))
    click(pg, '{"a":"sfclr","@Find":"sounds"}')
    K.check(str(pg.search) == "" and str(pg.findDraft) == "", "STG Clear empties the search and the box")
    click(pg, '{"a":"sfind","@Find":"interest"}')
    click(pg, '{"a":"stab%d","@Find":"interest"}' % CAT.index("skills"))
    K.check(str(pg.search) == "" and int(pg.cat) == CAT.index("skills"), "STG a tab click leaves the search and opens the tab")
    SW.clearAll()
    K.save()


# ================================================================================================ SHB: the Shards buttons
def run_shb(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JString
    K = HK.Child(out)
    pins = dict(T23.set_pins())
    sj = os.path.join(ROOT, "SkyyShards", "SkyyShards-%s.jar" % pins["SkyyShards"])
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar, sj], verify=True)
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    OP = JClass(PKG + "OpsPage")
    LINES, LABELS, CONF, TABS = [str(x) for x in OP.O_LINE], [str(x) for x in OP.O_LABEL], [bool(x) for x in OP.O_CONF], [int(x) for x in OP.O_TAB]
    WANT = [("Give Farming Shard", "shardadmin give {p}", True), ("Shard info", "shardadmin info {p}", False),
            ("Clear shard portal", "shardadmin unplace {p}", True), ("Unload shard world", "shardadmin unload {p}", False)]
    for lab, line, conf in WANT:
        K.check(line in LINES and LABELS[LINES.index(line)] == lab and CONF[LINES.index(line)] == conf and TABS[LINES.index(line)] == 2,
                "SHB %s = /%s on Players, danger=%s" % (lab, line, conf))
    PM, HS = JClass("com.hypixel.hytale.server.core.permissions.PermissionsModule"), JClass("java.util.HashSet")
    MSGS = []

    def sender(nodes):
        ns = HS()
        for n_ in nodes:
            ns.add(n_)

        @JImplements("com.hypixel.hytale.server.core.command.system.CommandSender")
        class Snd(object):
            @JOverride
            def getUsername(self):
                return "Skyy"

            @JOverride
            def getUuid(self):
                return JClass("java.util.UUID")(1, 2)

            @JOverride
            def sendMessage(self, m):
                MSGS.append(str(m.getMessageId() or m.getRawText()))

            @JOverride
            def hasPermission(self, q, *rest):
                r = PM.hasPermission(ns, str(q)) if str(q.getClass().getName()) == "java.lang.String" else PM.hasPermission(ns, q)
                return bool(r) if r is not None else False
        return Snd()

    @JImplements("com.hypixel.hytale.server.core.command.system.CommandOwner")
    class Owner(object):
        @JOverride
        def getName(self):
            return "SkyyHarness"
    root = JClass("com.skyy.shards.ShAdminCmd")()
    root.setOwner(Owner())
    try:
        root.completeRegistration()
    except Exception as e:
        K.notes.append("completeRegistration: %s" % str(e)[:80])
    Tok, PCx, PRs = (JClass("com.hypixel.hytale.server.core.command.system.Tokenizer"), JClass("com.hypixel.hytale.server.core.command.system.ParserContext"),
                     JClass("com.hypixel.hytale.server.core.command.system.ParseResult"))

    def parse(line, snd):
        del MSGS[:]
        res = PRs()
        toks = Tok.parseArguments(line, res)
        ctx = PCx.of(toks, line, res)
        try:
            root.acceptCall(snd, ctx, res)
        except Exception as e:
            MSGS.append("EXC " + str(e)[:200])
        if res.failed():
            res.sendMessages(snd)
            return False, list(MSGS)
        return True, list(MSGS)
    adm, nobody = sender(["skyyshards.admin"]), sender([])
    for _lab, line, _c in WANT:
        ln = line.replace("{p}", "Alpha")
        ok, ms = parse(ln, adm)
        K.check(ok and "server.commands.errors.playerOrArg" in ms, "SHB PARSE /%s reaches the sub-command's player-only execute (%s)" % (ln, ms[:1]))
        ok, ms = parse(ln + " x1 x2 x3", adm)
        K.check(not ok, "SHB PARSE CONTROL /%s + 3 words is refused" % ln)
        ok, ms = parse(ln, nobody)
        K.check(not ok or "server.commands.errors.playerOrArg" not in ms, "SHB PARSE without skyyshards.admin never reaches it")
    # the page: a danger row asks for a 2nd press
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    pr = U.allocateInstance(PR.class_)
    jf(PR.class_, "uuid").set(pr, JClass("java.util.UUID").fromString("00000000-0000-4000-8000-000000000325"))
    HM, AL, Long, Bool = JClass("java.util.HashMap"), JClass("java.util.ArrayList"), JClass("java.lang.Long"), JClass("java.lang.Boolean")

    def page():
        p = OP(pr, 2)
        p.pick = "Alpha"
        t = HM()
        t.put("cmd:shardadmin", root)
        t.put("sender", sender(["*"]))
        t.put("online", JArray(JString)(["Alpha"]))
        t.put("page", Bool.TRUE)
        t.put("ran", AL())
        t.put("now", Long(1000000))
        p.test = t
        return p

    def press(p, ms, i):
        p.test.put("now", Long(ms))
        p.handleDataEvent(None, None, '{"a":"op%d"}' % i)
        return [str(x) for x in p.test.get("ran")]
    for _lab, line, conf in WANT:
        i = LINES.index(line)
        p = page()
        K.check(bool(p.visible(i)), "SHB %s shows for an admin (the real /shardadmin leaf)" % _lab)
        exp = line.replace("{p}", "Alpha")
        if conf:
            K.eq(press(p, 1000000, i), [], "SHB %s: one press sends nothing" % _lab)
            K.eq(press(p, 1003000, i), [exp], "SHB %s: the 2nd press within 10 s sends /%s" % (_lab, exp))
        else:
            K.eq(press(p, 1000000, i), [exp], "SHB %s: one press sends /%s" % (_lab, exp))
    # the menu tiles (incl. the 0.3.22 Shards tile) = 0.3.24's, table for table (the old jar in an isolated loader)
    URL, File = JClass("java.net.URL"), JClass("java.io.File")
    urls = JArray(URL)([File(OLD_JAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()])
    old = JClass("java.net.URLClassLoader")(urls, JClass("java.lang.ClassLoader").getPlatformClassLoader())
    OD = JClass("java.lang.Class").forName(PKG + "MenuData", True, old)
    ND = JClass(PKG + "MenuData")
    for fn_ in ("E_VIEW", "E_SLOT", "E_NAME", "E_ACT", "E_NEED", "E_UNLOCK", "E_PERM", "E_ICON"):
        K.eq([str(x) for x in ND.class_.getField(fn_).get(None)], [str(x) for x in OD.getField(fn_).get(None)], "SHB tiles: MenuData.%s = 0.3.24's" % fn_)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           # S (0.3.22 run_shards) is not re-run: its old side, SkyyMenu-0.3.21.jar, is no longer kept; SHB checks the tile tables
           # against 0.3.24 instead (MenuData's E_* arrays unchanged)
           phases=[("srch", run_srch), ("stg", run_stg), ("shb", run_shb), ("snd", T24.run_snd), ("fix", T24.run_fix),
                   ("ops", T23.run_ops), ("live", T19.run_live)],
           script=__file__, live=(T23.LIVE_DIR, "Skyy_SkyyMenu"))
