"""Harness for SkyyMenu 0.3.21 (the Messages tab; tools/menu_0_3_21_patch.py).
Build first: python tools/menu_0_3_21_patch.py && python SkyyMenu/build_skyymenu_0.3.21.py

    python SkyyMenu/test_skyymenu_0.3.21.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.3.20 -> 0.3.21: exactly MenuData (the tab tables, SET_ORDER_MSG, the narrow tab buttons), SetReg.rank, SettingsPage.build
              (+ the version texts) differ; no class added
  T  tabs     SkyyHud 0.3.22's 22 registrations (its exact Object[7] shape, category "messages", no node) through settings:fn:register:
              all 22 land on the Messages tab in SkyyHud's kind order (shown, then feed), none on General; General = 0.3.20's General
              without them (its own 12 rows: CONTROL 0.3.20 files the 22 under General = 34 rows); msg.private (SkyyEssentials,
              general) stays on General; an unknown category still goes to General; the Settings page itself (engine UICommandBuilder):
              9 visible tabs = 5 + 4 buttons of 206 px in the two rows (<= 1080 px), the Messages tab = 3 pages of 8 / 8 / 6 rows
              starting msg.pickup, msg.pickup.feed; General 2 pages; with 8 or fewer visible tabs (no SkyyHud) the page's commands are
              0.3.20's byte for byte (same tabs, same rows)
  N, X, D     every 0.3.20 check carried forward: test_skyymenu_0.3.20.py's run_name and the 0.3.19 run_exec / run_live it carries, run on
              the 0.3.21 jar exactly as they ran on 0.3.20
  AA engine-access audit
Scratch: tools/dev/scratch/msgtab/menu (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("test_skyymenu_0_3_20", os.path.join(HERE, "test_skyymenu_0.3.20.py"))
T20 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T20)
T19 = T20.T19

VERSION = "0.3.21"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.20.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "msgtab", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T19.LIVE_DIR
EXPECT = {
    "MenuData": ["+f SET_ORDER_MSG", "+f UI_STABN", "+f UI_STABSELN", "~<clinit>"],
    "SetReg": ["~m rank"],
    "SettingsPage": ["~m build"],
    "CfgRows": ["~m header"],                     # the version text
    "CfgFn": ["~m opExport"],                     # the version text
    "SkyyMenuPlugin": ["~m setup"],               # the ready line's version
}
ADDED = []
KINDS = ["pickup", "drop", "skillxp", "levelup", "coins", "collection", "rankup", "quest", "heal", "petxp", "ability"]
MSG_KEYS = [k for kd in KINDS for k in ("msg." + kd, "msg." + kd + ".feed")]
# the General rows of the live set (SET_KNOWN general, Settings-Spec 2.2 order) + who registers them
GENERAL = [("party.invites", "SkyyParty"), ("party.members", "SkyyParty"), ("party.chat", "SkyyParty"), ("guild.online", "SkyyGuilds"),
           ("guild.members", "SkyyGuilds"), ("guild.chat", "SkyyGuilds"), ("tpa.requests", "SkyyEssentials"), ("tpa.updates", "SkyyEssentials"),
           ("msg.private", "SkyyEssentials")]
OTHER = [("skills.xpGain", "skills"), ("coll.tierUp", "collections"), ("sacks.benchDone", "sacks"), ("classes.healGiven", "combat"),
         ("coins.payReceived", "coins"), ("profiles.loginStatus", "profiles"), ("cooking.grade", "cooking")]


def run_tabs(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject
    import skyyui as SUI
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    Sys = JClass("java.lang.System")
    BR = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", BR)
    L = {"new": T19.loader_for(jar), "old": T19.loader_for(OLD_JAR)}
    J = lambda k, n: JClass(PKG + n, loader=L[k])
    Bool, UUID = JClass("java.lang.Boolean"), JClass("java.util.UUID")
    MDn = J("new", "MenuData")
    cat_ids = [str(x) for x in MDn.SET_CAT_ID]
    K.eq(cat_ids[-2:], ["messages", "general"], "T: the Messages tab right before General (General stays last)")
    K.eq(len(cat_ids), 9, "T: 9 tabs")
    K.eq(str(MDn.SET_TAB[7]), "Messages", "T: the tab button text")
    MSG, GEN = cat_ids.index("messages"), cat_ids.index("general")
    OGEN = [str(x) for x in J("old", "MenuData").SET_CAT_ID].index("general")

    def jarr(*xs):
        a = JArray(JObject)(len(xs))
        for i, x in enumerate(xs):
            a[i] = x
        return a

    def hud_rows(k):
        """SkyyHud 0.3.22 HudCfg.register(i) for every kind: the exact Object[7] it builds (default: chat kinds ON / feed OFF)"""
        fn = J(k, "SetRegFn")()
        res = []
        for kd in KINDS:
            d = "chat" if kd in ("levelup", "rankup", "ability") else "feed"
            a = jarr("SkyyHud", "msg." + kd, "Label " + kd, "messages", Bool.valueOf(d != "off"),
                     "Off = never shown. On = shown in the feed or in chat (the next switch).", None)
            f = jarr("SkyyHud", "msg." + kd + ".feed", "Label " + kd + ": in the feed (off = chat)", "messages", Bool.valueOf(d == "feed"),
                     "On = a card in the feed above the chat. Off = a line in chat.", None)
            res.append(bool(fn.apply(a)))
            res.append(bool(fn.apply(f)))
        return res

    def others(k):
        SR = J(k, "SetReg")
        SR.registerOwn()
        for key, mod in GENERAL:
            SR.register(jarr(mod, key, "L " + key, "general", Bool.TRUE, "h"))
        for key, c in OTHER:
            SR.register(jarr("SkyyX", key, "L " + key, c, Bool.TRUE, "h"))

    for k in ("new", "old"):
        others(k)
    K.check(all(hud_rows("new")) and all(hud_rows("old")), "T: SkyyHud's 22 registrations are accepted (both jars)")
    SRn, SRo = J("new", "SetReg"), J("old", "SetReg")
    km = [str(x) for x in SRn.keysOf(MSG)]
    K.eq(km, MSG_KEYS, "T: the Messages tab = SkyyHud's 22 rows in its kind order (shown, then feed)")
    kg = [str(x) for x in SRn.keysOf(GEN)]
    K.check(not [x for x in kg if x in MSG_KEYS], "T: no message-route row on General: %s" % kg)
    K.eq(kg, [g for g, _m in GENERAL] + ["menu.tooltips", "menu.hotkey"], "T: General = its own rows (the 0.3.19 length)")
    K.check("msg.private" in kg, "T: msg.private (SkyyEssentials, general) stays on General")
    kgo = [str(x) for x in SRo.keysOf(OGEN)]
    K.eq([x for x in kgo if x not in MSG_KEYS], kg, "T: General without the 22 = 0.3.20's General without them")
    K.eq(sorted(x for x in kgo if x in MSG_KEYS), sorted(MSG_KEYS), "T CONTROL 0.3.20: the 22 rows were filed under General")
    K.eq(len(kgo), 33, "T CONTROL 0.3.20: General had 11 + 22 = 33 rows (5 pages)")
    # an unknown category still goes to the last tab (General) - the catch-all is unchanged
    SRn.register(jarr("SkyyX", "harness.unknownCat", "L", "nosuchtab", Bool.TRUE, "h"))
    K.check(str(SRn.info("harness.unknownCat")[3]) == "general", "T: an unknown category -> General")
    SRn.DEFS.remove("harness.unknownCat")
    # a SkyyHud row registered again (its after= hook re-registers all) keeps the tab
    hud_rows("new")
    K.eq([str(x) for x in SRn.keysOf(MSG)], MSG_KEYS, "T: re-registering keeps the Messages rows (idempotent)")

    # ---------------- the Settings page itself (engine UICommandBuilder / UIEventBuilder)
    Cls = JClass("java.lang.Class")
    fu = Cls.forName("sun.misc.Unsafe").getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def jf(c, name):
        while c is not None:
            try:
                f = c.getDeclaredField(name)
                f.setAccessible(True)
                return f
            except Exception:
                c = c.getSuperclass()
        raise KeyError(name)
    u = UUID.fromString("00000000-0000-4000-8000-000000000321")

    def pref():
        p = U.allocateInstance(PR.class_)
        jf(PR.class_, "uuid").set(p, u)
        return p

    def build(k, cat, page=0):
        pg = J(k, "SettingsPage")(pref(), cat)
        pg.pageNo = page
        b, ev = UCB(), UEB()
        pg.build(None, b, ev, None)
        res = []
        for c in list(b.getCommands()):
            g = lambda n: (lambda v: "" if v is None else str(v))(jf(c.getClass(), n).get(c))
            res.append((g("selector"), g("text"), g("data")))
        return pg, res

    def tabs(cmds):
        outl = []
        for sel, t, _d in cmds:
            m = re.search(r"#SkyyStgTab(\d+) \{ Anchor: \(Width: (\d+)", t)
            if sel.startswith("#SkyyStgTabs") and m:
                outl.append((sel, int(m.group(1)), int(m.group(2))))
        return outl

    def head(cmds):
        h = [d for s_, t, d in cmds if s_ == "#SkyyStgHead.Text"]
        return h[0] if h else ""

    def rows(cmds):
        return len([1 for s_, t, d in cmds if s_ == "#SkyyStgRows" and t.startswith("Group #SkyyStgRow")])

    pg, c = build("new", MSG)
    tb = tabs(c)
    r0 = [x for x in tb if x[0] == "#SkyyStgTabs0"]
    r1 = [x for x in tb if x[0] == "#SkyyStgTabs1"]
    K.eq((len(r0), len(r1)), (5, 4), "T page: 9 visible tabs = 5 + 4 per row")
    K.check(all(x[2] == 206 for x in tb), "T page: the 9 tab buttons are 206 px: %s" % tb)
    sp0 = len([1 for s_, t, d in c if s_ == "#SkyyStgTabs0" and "Width: 12," in t])
    K.check(5 * 206 + sp0 * 12 <= 1080 and sp0 == 4, "T page: the first row is %d px (<= 1080 inside the page)" % (5 * 206 + sp0 * 12))
    K.check(all(SUI.text_width(str(t), 18, bold=True) + 16 <= 206 for t in MDn.SET_TAB), "T page: every tab name fits 206 px")
    K.check([x[1] for x in tb] == list(range(9)), "T page: tab order Skills .. Cooking, Messages, General: %s" % [x[1] for x in tb])
    K.check("Messages (chat, feed or off)   -   22 settings   -   page 1 of 3" in head(c), "T page: Messages header %r" % head(c))
    K.eq(rows(c), 8, "T page: Messages page 1 = 8 rows")
    K.eq([str(x) for x in pg.rowKeys][:2], ["msg.pickup", "msg.pickup.feed"], "T page: the first two rows = Item pickups shown + feed")
    sel = [t for s_, t, d in c if s_.startswith("#SkyyStgTabs") and "#SkyyStgTab%d " % MSG in t]
    K.check(sel and "#e0b060" in sel[0], "T page: the Messages tab is drawn selected")
    _pg, c3 = build("new", MSG, 2)
    K.check(rows(c3) == 6 and "page 3 of 3" in head(c3), "T page: Messages page 3 = 6 rows (%r)" % head(c3))
    K.eq([str(x) for x in _pg.rowKeys if x is not None][-2:], ["msg.ability", "msg.ability.feed"], "T page: the last rows = Ability casts")
    _pg, cg = build("new", GEN)
    K.check("General (party, guild, teleports, menu)   -   11 settings   -   page 1 of 2" in head(cg), "T page: General header %r" % head(cg))
    _pg, cgo = build("old", OGEN)
    K.check("33 settings   -   page 1 of 5" in head(cgo), "T page CONTROL 0.3.20: General had 33 rows, 5 pages (%r)" % head(cgo))
    # no SkyyHud (8 visible tabs): the page = 0.3.20's, command for command
    for k_ in ("new", "old"):
        SR = J(k_, "SetReg")
        for key in MSG_KEYS:
            SR.DEFS.remove(key)
    for ci in range(8):
        _a, cn = build("new", ci if ci < 7 else GEN)
        _b, co = build("old", ci if ci < 7 else OGEN)
        # the one difference: General is tab 8 now (0.3.20: tab 7) - its button id #SkyyStgTab8 vs #SkyyStgTab7
        cn = [tuple(x.replace("#SkyyStgTab8 ", "#SkyyStgTab7 ") for x in r_) for r_ in cn]
        dif = [(a_, b_) for a_, b_ in zip(cn, co) if a_ != b_]
        K.check(cn == co, "T page: with 8 visible tabs (no SkyyHud) tab %d draws exactly what 0.3.20 draws (General's id aside): %s" % (ci, dif[:2]))
    _a, cn = build("new", GEN)
    K.check(len(tabs(cn)) == 8 and all(x[2] == 252 for x in tabs(cn)) and len([x for x in tabs(cn) if x[0] == "#SkyyStgTabs0"]) == 4,
            "T page: 8 visible tabs = 0.3.20's 4 + 4 buttons of 252 px")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("tabs", run_tabs), ("name", T20.run_name), ("exec", T19.run_exec), ("live", T19.run_live)], script=__file__,
           live=(LIVE_DIR, "Skyy_SkyyMenu"))
