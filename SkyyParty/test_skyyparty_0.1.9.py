"""Harness for SkyyParty 0.1.9 (the SkyyCore pilot; tools/party_0_1_9_patch.py). Build first: python SkyyCore/build_skyycore_1.0.0.py,
python tools/party_0_1_9_patch.py && python SkyyParty/build_skyyparty_0.1.9.py

    python SkyyParty/test_skyyparty_0.1.9.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Every child JVM gets the SkyyCore jar on its class path (SKYY_HARNESS_CP). The OLD jar is the LIVE 0.1.8 (the SET pin).
  A        every class loads + initialises with -Xverify:all (Core on the class path)
  C        class compare 0.1.8 -> 0.1.9: removed = the 7 private kit classes + HubBar, added = CfgData, changed = exactly the members that
           now call SkyyCore (EXPECT); non-class entries: manifest.json + the 59 kit files (gone)
  KITBYTES no kit art / asset in the jar; manifest = stable SkyyParty, no asset pack, Dependencies Skyy:SkyyCore >=1.0.0 <2.0.0
  HUB      tools/hub_tab_harness.py on SkyyCore's HubBar (owner SkyyParty): REG / PAGE / CLICK / DROP + Refresh + a party of two in
           the hub shell (the 0.1.8 harness's extra checks)
  D        two opens of the page on a scratch COPY of the live Skyy_SkyyParty (nothing written)
  KIT      Server Setup parity: 0.1.8's own kit vs 0.1.9's kit copy in SkyyCore on a COPY of the live Skyy_SkyyParty (header, every
           get, status, versions, export, log, console sets, cmdSetConsole / cmdGet, the files afterwards) - SkyyBank's harness helper
  PAGE     page parity: the REAL PartyPage through each jar's hub bar - a player alone, a party of two (leader + member views), Refresh;
           and /partyadmin's status / set / reload answers (PartyAdmin, through the kit handle in 0.1.9): 0.1.8 = 0.1.9 (digits masked)
  AA       engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_harness as H

VERSION = "0.1.9"
PKG = "com.skyy.party."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyParty-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyParty-0.1.8.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "core10", "party")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyParty")
_s = importlib.util.spec_from_file_location("tb0114", os.path.join(ROOT, "SkyyBank", "test_skyybank_0.1.14.py"))
TB = importlib.util.module_from_spec(_s)
_s.loader.exec_module(TB)          # SkyyBank 0.1.14's harness: kit_parity / page_dump / page_compare (sets SKYY_HARNESS_CP = Core)
KITN = TB.KITN

EXPECT = {      # the class compare 0.1.8 -> 0.1.9: exactly the members that now call SkyyCore
    "PartyAdmin": ["~m cur", "~m reload", "~m set"],                   # CfgFn.cmdGet / op / cmdSet -> CfgData.kit()
    "PartyHubOpen": ["~m register"],                                   # HubBar.put -> SkyyCore's HubBar
    "PartyPage": ["~m build", "~m hubClick"],                          # HubBar.build / handle -> SkyyCore's HubBar
    "PartyStore": ["~m bridge"],                                       # Core.bridge (the same map, lock-free after the first call)
    "SkyyPartyPlugin": ["~m setup", "~m shutdown"],                    # register, kit start / shutdown, HubBar.removeAll(owner)
}


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
    K.check(cm[0][2].startswith("Group #SkyyPF ") and any(c[2] and "#SkyyPFHubTabs " in c[2] for c in cm), "PAGE: the leader's page is the hub shell")
    K.check(any(c[2] and "#SkyyPRow1 " in c[2] for c in cm) and any(c[2] and "#SkyyPKick1 " in c[2] for c in cm),
            "PAGE: the leader's member list (2 rows, Kick on the member's row) in the hub shell")
    want = "Party 2 / %d players.  " % int(PS.MAX)
    K.check(any(c[1] and "SkyyPInfo" in c[1] and c[3] and want in str(c[3]) for c in cm), "PAGE: the info line leads with the party size + cap")
    data = __import__("zipfile").ZipFile(JAR).read("com/skyy/party/SkyyPartyPlugin.class")
    K.check(b"SkyyCore " in data, "PAGE: the ready line names the SkyyCore version")
    JClass("com.skyy.core.ui.HubBar").removeAll("SkyyParty")


def run_kit(out, jar, scratch, _home):
    K = HK.Child(out)

    def prep_fn(J, home):
        from jpype import JClass
        J("PartyStore").loadConfig(JClass("java.nio.file.Paths").get(home))
    TB.kit_parity(K, "SkyyParty", PKG, OLD_JAR, jar, ("0.1.8", VERSION), scratch, LIVE_DIR,
                  sets=[("maxSize", "6"), ("inviteSeconds", "90"), ("privacy.staffBypass", "false"), ("maxSize", "99"), ("nope", "1")],
                  cmd_sets=[("maxSize", "4"), ("inviteSeconds", "default")], prep_fn=prep_fn)
    K.save()


def party_scenario(K, W, E, J, HB, home):
    from jpype import JClass
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.join(home, "mods")
    os.makedirs(os.path.join(mods, "Skyy_SkyyParty"), exist_ok=True)
    J("PartyStore").loadConfig(Paths.get(os.path.join(mods, "Skyy_SkyyParty")))
    try:
        J("CfgData").kit().start(Paths.get(mods), None)          # 0.1.9: the kit copy in SkyyCore
        K.notes.append("PAGE: Server Setup kit started through SkyyCore")
    except Exception:
        J("CfgPub").start(Paths.get(mods), None)                 # 0.1.8: its own kit
    J("PartyHubOpen").register()
    dumps = []

    def page(nm, X):
        r = str(HB.open(X.pr, X.pr.getUuid(), "social", "party"))
        E.pump(X)
        pg = X.pm.getCustomPage()
        K.check(r == "bridge" and pg is not None, "PAGE %s opened through the hub bar (%s)" % (nm, r))
        b, ev = UCB(), UEB()
        pg.build(X.ref, b, ev, X.st)
        dumps.append((nm, H.cmds_of(b), H.events_of(ev)))
        n0 = len(E.sent(X))
        X.pm.handleLegacyCustomPageEvent(X.ref, X.st, E.CPE(E.CPT.Data, '{"a":"refresh"}'))
        E.pump(X)
        dumps.append((nm + " refresh", [[k] for k in E.kinds(X, n0)], [[E.strs_of(X, n0)]]))
    page("alone", W.P)
    J("PartyStore").join(W.O.pr.getUuid(), W.P.pr.getUuid())
    page("leader of two", W.O)
    page("member of two", W.P)
    A = J("PartyAdmin")
    dumps.append(("partyadmin", [[str(A.status())], [str(A.set(W.O.pr, "maxSize", "7"))], [str(A.status())],
                                 [str(A.set(W.O.pr, "maxSize", "default"))], [str(A.reload(W.O.pr))], [str(A.status())]], []))
    return dumps


S = H.Spec(name="SkyyParty", version=VERSION, pkg=PKG, hub="social", tab="party", mod="SkyyParty", open_cls="PartyHubOpen", vis_cls=None,
           page_cls="PartyPage", prefix="SkyyPF", idp="SkyyP", plugin_cls="SkyyPartyPlugin", register_call="PartyHubOpen.register",
           register=lambda J: J("PartyHubOpen").register(), prep=prep, clicks=[('{"a":"refresh"}', chk_refresh)], extra_hub=extra_hub,
           jar=JAR, old_jar=OLD_JAR, scratch=SCRATCH, script=__file__,
           hub_class="com.skyy.core.ui.HubBar", hub_owner="SkyyParty", kit_in_jar=False,
           added=["CfgData"], removed=list(KITN) + ["HubBar"], expect=EXPECT,
           extra_phases=[("kit", run_kit),
                         ("pageold", lambda out, jar, scratch, home: TB.page_dump(out, S, OLD_JAR, scratch, "old", False, party_scenario)),
                         ("pagenew", lambda out, jar, scratch, home: TB.page_dump(out, S, jar, scratch, "new", True, party_scenario)),
                         ("pagecmp", lambda out, jar, scratch, home: TB.page_compare(out, scratch, "old", "new"))])

if __name__ == "__main__":
    H.run(S)
