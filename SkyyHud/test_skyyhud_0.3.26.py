"""Harness for SkyyHud 0.3.26 (HUBS H3c: the Settings > HUD tab = the new HUD launcher hub page; tools/hud_0_3_26_patch.py). Build first:
python tools/hud_0_3_26_patch.py && python SkyyHud/build_skyyhud_0.3.26.py

    python SkyyHud/test_skyyhud_0.3.26.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.3.25 -> 0.3.26 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyHud, AA engine-access audit), plus here:
  REG   the open Function answers FALSE while the plugin is not registered (PLUGIN null: the bar then runs /skyyhud = the editor)
  PAGE  the launcher: heading, the two lines, "Open the HUD editor" + "Widgets list" bound to hudedit / hudwidgets, the chat hint
  CLICK Widgets list opens the 0.3.25 WidgetsPage; Open the HUD editor opens the 0.3.25 EditorPage (the HUD attached first when it is not
        yet - here it is: the editor opens straight away), both on the player's world thread, replacing the launcher
Exit code 1 on any failure.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.3.26"
PKG = "com.skyy.hud."
PL = {}


def prep(E, J, home):
    from jpype import JClass
    J("LayoutStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyHud")
    J("LayoutStore").DIR = E.Paths.get(os.path.join(home, "layouts"))
    J("HudCfg").LOG = J("LayoutStore").LOG
    J("HudCfg").FILE = E.Paths.get(os.path.join(home, "config.properties"))
    pl = E.U.allocateInstance(J("SkyyHudPlugin").class_)
    H.jf(J("SkyyHudPlugin").class_, "huds").set(pl, JClass("java.util.concurrent.ConcurrentHashMap")())
    PL["pl"] = pl


def register(J):
    return J("HudHubOpen").register(PL["pl"])


def chk_widgets(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "WidgetsPage", "CLICK: Widgets list opens the 0.3.25 widgets page (%s)"
            % (None if after is None else after.getClass().getSimpleName()))


def chk_editor(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "EditorPage", "CLICK: Open the HUD editor opens the 0.3.25 editor (%s; %s)"
            % (None if after is None else after.getClass().getSimpleName(), E.strs_of(P, f0)[-120:]))


def after_open(K, E, J, P, pg):
    from jpype import JClass
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    pg.build(P.ref, b, ev, P.st)
    cm = H.cmds_of(b)
    evs = H.events_of(ev)
    K.check(any(c[2] and "#SkyyHudHEdit " in c[2] and "Open the HUD editor" in c[2] for c in cm)
            and any(s == "#SkyyHudHEdit" and "hudedit" in t for s, t in evs) and any(s == "#SkyyHudHWid" and "hudwidgets" in t for s, t in evs),
            "PAGE: Open the HUD editor / Widgets list, bound to hudedit / hudwidgets")
    sets = dict((s, d) for ty, s, t, d in cm if ty == "Set")
    K.check("#SkyyHudHL1.Text" in sets and "#SkyyHudHL2.Text" in sets and "/skyyhud" in sets.get("#SkyyHudHHint.Text", ""),
            "PAGE: the two lines and the chat hint")
    # the HUD of the harness player counts as attached: Open the HUD editor goes straight to the editor
    PL["pl"].huds.put(P.pr.getUuid(), JClass("java.lang.Object")())


def extra_hub(K, W, J):
    from jpype import JClass
    E = W.E
    J("HudHubOpen").unregister()
    K.check(J("HudHubOpen").PLUGIN is None and J("HudHubOpen")().apply(W.P.pr.getUuid()) == JClass("java.lang.Boolean").FALSE,
            "REG: unregister clears PLUGIN; the open Function then answers FALSE (the bar runs /skyyhud)")


S = H.Spec(name="SkyyHud", version=VERSION, pkg=PKG, hub="settings", tab="hud", mod="SkyyHud", open_cls="HudHubOpen", vis_cls=None,
           page_cls="HudHubPage", prefix="SkyyHudHF", idp="SkyyHud", plugin_cls="SkyyHudPlugin", register_call="HudHubOpen.register",
           drop_call="HudHubOpen.unregister", register=register, prep=prep, after_open=after_open,
           clicks=[('{"a":"hudwidgets"}', chk_widgets), ('{"a":"hudedit"}', chk_editor)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyHud-0.3.25.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3bcd", "hud"))), script=__file__,
           added=["HubBar", "HudHubPage", "HudHubOpen"],
           expect={"SkyyHudPlugin": ["~m setup", "~m shutdown"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]})

if __name__ == "__main__":
    H.run(S)
