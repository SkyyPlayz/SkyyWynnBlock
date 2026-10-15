"""Harness for SkyyMerchants 0.1.5 (HUBS H3b: the Market > Merchants tab = the new rumours hub page; tools/merchants_0_1_5_patch.py).
Build first: python tools/merchants_0_1_5_patch.py && python SkyyMerchants/build_skyymerchants_0.1.5.py

    python SkyyMerchants/test_skyymerchants_0.1.5.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.1.4 -> 0.1.5 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyMerchants, AA engine-access audit), plus here:
  VIS   MerchHubVis = MerchCfg.ON: the merchants switched off -> no Merchants tab (HubBar.tabs / open answers hidden)
  PAGE  MerchRumPage for a world WITH zones: one line per zone of that world = MerchCore.rumoursText (the /merchants chat lines) - every
        zone line set, in order, the heading and the hint; a world without zones: the one "No traveling merchants roam this world." line
  CLICK the Merchants tab itself redraws (fresh rumours); Refresh (a non-hub click) redraws
Exit code 1 on any failure.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.5"
PKG = "com.skyy.merchants."


def prep(E, J, home):
    from jpype import JClass
    J("MerchLog").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyMerchants")
    mods = os.path.dirname(home) if os.path.basename(home) == "Skyy_SkyyMerchants" else os.path.join(home, "mods")
    os.makedirs(os.path.join(mods, "Skyy_SkyyMerchants"), exist_ok=True)
    J("MerchCfg").load(E.Paths.get(mods))
    J("MerchReg").DIR = E.Paths.get(os.path.join(mods, "Skyy_SkyyMerchants", "merchants"))


def vis_cases(K, E, J, vis, u):
    from jpype import JClass
    FALSE = JClass("java.lang.Boolean").FALSE
    J("MerchCfg").ON = False
    K.check(vis.apply(u) == FALSE and len(list(J("HubBar").tabs("market", u))) == 0, "VIS: merchants switched off -> no Merchants tab")
    K.eq(str(J("HubBar").open(None, u, "market", "merchants")), "hidden", "VIS: switched off -> HubBar.open answers hidden")
    J("MerchCfg").ON = True


def chk_refresh(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "MerchRumPage" and len(E.sent(P)) > f0,
            "CLICK: Refresh (not a hub click) redraws the rumours page")


def extra_hub(K, W, J):
    from jpype import JClass
    E = W.E
    Z = J("MerchCfg").ZONES
    K.check(len(Z) > 0, "PAGE: the default config has zones (%d)" % len(Z))
    if len(Z) == 0:
        return
    wn = str(Z[0].world)
    pg = J("MerchRumPage")(W.P.pr, wn)
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    pg.build(W.P.ref, b, ev, W.P.st)
    cm = H.cmds_of(b)
    sets = []
    for ty, s, t, d in cm:
        if ty == "Set":
            v = json.loads(d)
            sets.append((s, str(v.get("0", v)) if isinstance(v, dict) else str(v)))
    want = str(J("MerchCore").rumoursText(wn, JClass("java.lang.System").currentTimeMillis())).split("\n")
    got = [v for s, v in sets if s.startswith("#SkyyMcRL")]
    K.check(len(got) == len(want) and [g.split(":")[0] for g in got] == [w.split(":")[0] for w in want] and len(got) >= 1,
            "PAGE: a zone world shows one line per zone = /merchants (%d lines: %s)" % (len(got), [g[:30] for g in got]))
    K.check(all(any(s == "#SkyyMcRL%d.Text" % i for s, v in sets) for i in range(len(got))), "PAGE: the zone lines are #SkyyMcRL0..%d" % (len(got) - 1))
    K.check(any(s == "#SkyyMcRHint.Text" and "press F" in v for s, v in sets), "PAGE: the hint line")
    pg2 = J("MerchRumPage")(W.P.pr, "no_such_world")
    b2 = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    pg2.build(W.P.ref, b2, JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")(), W.P.st)
    s2 = [json.loads(d) for ty, s, t, d in H.cmds_of(b2) if ty == "Set" and s == "#SkyyMcRL0.Text"]
    K.check(len(s2) == 1 and "No traveling merchants roam this world" in str(s2[0]), "PAGE: a world without zones: the one no-merchants line")
    gen = open(os.path.join(HERE, "build_skyymerchants_%s.py" % VERSION), encoding="utf8").read()
    K.check('if (r.equals("self")) { rebuild(); return; }' in gen, "CLICK: the Merchants tab itself redraws (fresh rumours)")


S = H.Spec(name="SkyyMerchants", version=VERSION, pkg=PKG, hub="market", tab="merchants", mod="SkyyMerchants", open_cls="MerchHubOpen",
           vis_cls="MerchHubVis", page_cls="MerchRumPage", prefix="SkyyMcRF", idp="SkyyMc", plugin_cls="SkyyMerchantsPlugin",
           register_call="MerchHubOpen.register", register=lambda J: J("MerchHubOpen").register(), prep=prep, vis_cases=vis_cases,
           self_redraw=True, clicks=[('{"a":"refresh"}', chk_refresh)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION))),
           old_jar=os.path.join(HERE, "SkyyMerchants-0.1.4.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3bcd", "merchants"))), script=__file__,
           added=["HubBar", "MerchRumPage", "MerchHubVis", "MerchHubOpen"],
           expect={"SkyyMerchantsPlugin": ["~m setup", "~m shutdown"], "CfgFn": ["~m opExport"],
                   # MerchCfg.seed / applyAll + CfgRows <clinit>: the config.properties header names the version ("# SkyyMerchants 0.1.5 - ...")
                   "CfgRows": ["~<clinit>", "~m header"], "MerchCfg": ["~m applyAll", "~m seed"]})

if __name__ == "__main__":
    H.run(S)
