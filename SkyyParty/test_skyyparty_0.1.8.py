"""Harness for SkyyParty 0.1.8 (HUBS H3c: the Social > Party tab; tools/party_0_1_8_patch.py). Build first:
python tools/party_0_1_8_patch.py && python SkyyParty/build_skyyparty_0.1.8.py

    python SkyyParty/test_skyyparty_0.1.8.py [--dir <folder inside tools/dev/scratch/>] [--keep]

The phases are tools/hub_tab_harness.py's (A verify, C compare 0.1.7 -> 0.1.8 + the kit bytes, HUB executed: REG / PAGE / CLICK / DROP,
D live: two opens on a scratch COPY of the live Skyy_SkyyParty, AA engine-access audit), plus here:
  PAGE  no #SkyyPTitle and no title b.set any more (the hub title bar); a player IN a party (2 members) gets the member list in the hub
        shell too
  CLICK Refresh (a non-hub click) still answers on the page
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.8"
PKG = "com.skyy.party."


def prep(E, J, home):
    from jpype import JClass
    J("PartyStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyParty")


def chk_refresh(K, E, J, P, before, after, f0):
    K.check(after is not None and str(after.getClass().getSimpleName()) == "PartyPage" and len(E.sent(P)) > f0,
            "CLICK: Refresh (not a hub click) still answers on the party page")


def extra_hub(K, W, J):
    from jpype import JClass
    E = W.E
    PS = J("PartyStore")
    PS.join(W.O.pr.getUuid(), W.P.pr.getUuid())
    lo = PS.listOf(W.O.pr.getUuid())
    K.check(lo is not None and int(lo.size()) == 2, "PAGE: a party of the two harness players (the op leads)")
    J("PartyHubOpen").register()
    pg = J("PartyPage")(W.O.pr)
    W.O.pm.openCustomPage(W.O.ref, W.O.st, pg)
    E.pump(W.O)
    b = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")()
    ev = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")()
    pg.build(W.O.ref, b, ev, W.O.st)
    cm = H.cmds_of(b)
    K.check(not [c for c in cm if c[1] and "SkyyPTitle" in c[1]] and not [c for c in cm if c[2] and "#SkyyPTitle " in c[2]],
            "PAGE: no #SkyyPTitle element and no #SkyyPTitle b.set (the hub title bar replaced the 0.1.7 title)")
    K.check(cm[0][2].startswith("Group #SkyyPF ") and any(c[2] and "#SkyyPFHubTabs " in c[2] for c in cm), "PAGE: the leader's page is the hub shell too")
    K.check(any(c[2] and "#SkyyPRow1 " in c[2] for c in cm) and any(c[2] and "#SkyyPKick1 " in c[2] for c in cm),
            "PAGE: the leader's member list (2 rows, Kick on the member's row) in the hub shell")
    want = "Party 2 / %d players.  " % int(PS.MAX)
    K.check(any(c[1] and "SkyyPInfo" in c[1] and c[3] and want in str(c[3]) for c in cm),
            "PAGE: review fix - the info line leads with the party size + cap the 0.1.7 title showed (%r)" % want)
    J("HubBar").removeAll()


S = H.Spec(name="SkyyParty", version=VERSION, pkg=PKG, hub="social", tab="party", mod="SkyyParty", open_cls="PartyHubOpen", vis_cls=None,
           page_cls="PartyPage", prefix="SkyyPF", idp="SkyyP", plugin_cls="SkyyPartyPlugin", register_call="PartyHubOpen.register",
           register=lambda J: J("PartyHubOpen").register(), prep=prep, clicks=[('{"a":"refresh"}', chk_refresh)], extra_hub=extra_hub,
           jar=os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyParty-%s.jar" % VERSION))), old_jar=os.path.join(HERE, "SkyyParty-0.1.7.jar"),
           scratch=os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hubsH3bcd", "party"))), script=__file__,
           added=["HubBar", "PartyHubOpen"],
           expect={"PartyPage": ["+m hubAck", "+m hubClick", "~m build", "~m handleDataEvent"], "SkyyPartyPlugin": ["~m setup", "~m shutdown"],
                   "CfgFn": ["~m opExport"],
                   # CfgRows: the version text + the config kit's lock-free bridge read (tools/skyycfg.py since SkyyMenu 0.3.19; 0.1.7 was
                   # built with the older kit - a rebuild picks the current kit up, no behaviour change for the party)
                   "CfgRows": ["+f BRIDGE", "+m bridge0", "~m bridge", "~m header"]})

if __name__ == "__main__":
    H.run(S)
