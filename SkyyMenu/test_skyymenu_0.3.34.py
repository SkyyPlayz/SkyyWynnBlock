"""Harness for SkyyMenu 0.3.34 (round smithhub: saved shortcuts of merged-away tabs open where their page went; the Storage / Crafting
blurbs; stand-ins follow the kit's merge data; tools/menu_0_3_34_patch.py). Build first:
    python tools/menu_0_3_34_patch.py && python SkyyMenu/build_skyymenu_0.3.34.py

    python SkyyMenu/test_skyymenu_0.3.34.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py - the 0.3.33 harness's way: -Xverify:all over the SkyyMenu 0.3.19 engine stand-ins):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.33 -> 0.3.34: exactly the listed members differ; non-class entries: manifest.json only
  M    EXECUTED:
       REG    no stand-in for smithing:identify (part of the Anvil) or market:auctions (part of Market); the reforge stand-in is labelled Anvil
       BANK   'tab:storage:bank' with the Bank tab hidden (merged into the Vault) and a Vault tab: looks "ok" (never locked), says the Vault;
              a click opens the VAULT tab (its Function ran, the Bank's did not); with the Bank tab standing on its own it is the Bank again
       AH     'tab:market:auctions' with the Auctions tab hidden and /ah on the server: looks "ok" with "Command: /ah"; a click runs /ah as
              the player; without /ah = the 0.3.33 look (no redirect); a visible Auctions tab = itself
       TEXT   the Storage + Crafting blurbs
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (NewBetaTest): the registry, Home built both times; nothing written
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, time, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import skyyui as SUI

_s29 = importlib.util.spec_from_file_location("test_skyymenu_0_3_29", os.path.join(HERE, "test_skyymenu_0.3.29.py"))
T29 = importlib.util.module_from_spec(_s29)
_s29.loader.exec_module(T29)
T19 = T29.T19
build_page, jf, DECL_RE, WH_RE = T29.build_page, T29.jf, T29.DECL_RE, T29.WH_RE

VERSION = "0.3.34"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.33.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "smithhub", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyMenu")
SKYY = "d8ddde89-98b2-4739-983e-a39773d582b6"
ADDED = []
EXPECT = {
    "MenuData": ["+f REDIR_FROM", "+f REDIR_NAME", "+f REDIR_TO", "+f REDIR_WHY", "~<clinit>"],
    "MenuPage": ["+m redirName", "+m redirect", "~m look", "~m shortcut"],
    "SkyyMenuPlugin": ["~m setup"],
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "OpsPage": ["~<clinit>"],
}


def run_m(out, jar, scratch, _home):
    from jpype import JClass, JArray, JImplements, JOverride, JObject
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hcls_m")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    home = os.path.join(scratch, "home_m")
    os.makedirs(os.path.join(home, "layouts"), exist_ok=True)
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    JV("SetReg").registerOwn()
    JV("MenuIO").begin()
    HB, MH, MD = JV("HubBar"), JV("MenuHub"), JV("MenuData")
    br = JV("MenuUtil").bridge()
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())
    TRUE, FALSE = JClass("java.lang.Boolean").TRUE, JClass("java.lang.Boolean").FALSE
    S, Int = JClass("java.lang.String"), JClass("java.lang.Integer")

    @JImplements("java.util.function.Function")
    class Stub(object):
        def __init__(self, ans):
            self.calls, self.ans = [], ans

        @JOverride
        def apply(self, x):
            self.calls.append(str(x))
            return self.ans

    def mkp(uid, name):
        P = E.player(uid, name=name)
        byU.put(uid, P.pr)
        E.UniH.PL.add(P.pr)
        E.PLAYERS.add(P.pr)
        return P
    P = mkp(E.PLAIN, "SkyyPlain")
    u = P.pr.getUuid()
    for n_ in ("smithing", "reforge", "upgrade", "identify", "bazaar", "vault", "bank"):
        E.CM.cmds.put(n_, E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    # ================================================================ REG
    n = int(MH.register())
    K.check(n >= 7, "REG: Menu's own tabs put (%d)" % n)
    K.check(br.get("hub:tab:smithing:identify") is None and br.get("hub:tab:market:auctions") is None,
            "REG: no stand-in for Identify (part of the Anvil) or the Auction House (part of Market)")
    rf = br.get("hub:tab:smithing:reforge")
    K.check(rf is not None and str(rf[0]) == "SkyyMenu" and str(rf[1]) == "Anvil", "REG: the reforge stand-in is labelled Anvil (%s)" % (None if rf is None else str(rf[1])))
    K.check(list(MD.REDIR_FROM) == ["tab:storage:bank", "tab:market:auctions"] and list(MD.REDIR_TO) == ["tab:storage:vault", "cmd:ah"], "REG: the redirect table")
    hm = JV("MenuPage")(P.pr, "main")
    P.pm.openCustomPage(P.ref, P.st, hm)
    E.pump(P)
    # ================================================================ BANK
    vf, bf = Stub(TRUE), Stub(TRUE)
    vault = JArray(JObject)([S("SkyyVault"), S("Vault"), Int.valueOf(30), S("vault"), vf, None])
    bank_h = JArray(JObject)([S("SkyyBank"), S("Bank"), Int.valueOf(40), S("bank"), bf, Stub(FALSE)])
    br.put("hub:tab:storage:vault", vault)
    br.put("hub:tab:storage:bank", bank_h)
    lk = hm.look("tab:storage:bank", False)
    K.check(lk is not None and str(lk[5]) == "ok" and str(lk[1]) == "Bank" and "Vault" in str(lk[2]) and str(lk[4]) == "sc:tab:storage:bank",
            "BANK: the saved Bank shortcut (its tab merged away) looks ok, says the Vault: %s" % (None if lk is None else [str(x) for x in lk]))
    del vf.calls[:]
    del bf.calls[:]
    hm.shortcut(P.ref, P.st, "tab:storage:bank")
    E.pump(P)
    K.check(vf.calls == [str(u)] and bf.calls == [], "BANK: a click opens the VAULT tab (vault %s, bank %s)" % (vf.calls, bf.calls))
    bank_v = JArray(JObject)([S("SkyyBank"), S("Bank"), Int.valueOf(40), S("bank"), bf, None])
    br.put("hub:tab:storage:bank", bank_v)
    K.check(JV("MenuPage").redirect("tab:storage:bank", u) is None, "BANK: a Bank tab standing on its own = no redirect")
    hm = JV("MenuPage")(P.pr, "main")
    P.pm.openCustomPage(P.ref, P.st, hm)
    E.pump(P)
    del vf.calls[:]
    del bf.calls[:]
    hm.shortcut(P.ref, P.st, "tab:storage:bank")
    E.pump(P)
    K.check(bf.calls == [str(u)] and vf.calls == [], "BANK: ... and its click opens the Bank (bank %s, vault %s)" % (bf.calls, vf.calls))
    br.remove("hub:tab:storage:bank")
    K.eq(str(JV("MenuPage").redirect("tab:storage:bank", u)), "tab:storage:vault", "BANK: no Bank tab at all -> the Vault")
    # ================================================================ AH
    af = Stub(TRUE)
    ah_h = JArray(JObject)([S("SkyyAuctions"), S("Auctions"), Int.valueOf(20), S("ah"), af, Stub(FALSE)])
    br.put("hub:tab:market:auctions", ah_h)
    K.check(JV("MenuPage").redirect("tab:market:auctions", u) is None, "AH: without /ah on the server = no redirect (0.3.33's look)")
    E.CM.cmds.put("ah", E.U.allocateInstance(JClass("skyymenu19.Cmd").class_))
    hm = JV("MenuPage")(P.pr, "main")
    P.pm.openCustomPage(P.ref, P.st, hm)
    E.pump(P)
    lk = hm.look("tab:market:auctions", False)
    K.check(lk is not None and str(lk[5]) == "ok" and str(lk[1]) == "Auction House" and "Command: /ah" in str(lk[2]),
            "AH: the saved Auctions shortcut (hidden: part of Market) looks ok with Command: /ah: %s" % (None if lk is None else [str(x) for x in lk]))
    E.CM.lines.clear()
    hm.shortcut(P.ref, P.st, "tab:market:auctions")
    E.pump(P)
    K.check([str(x) for x in E.CM.lines] == ["ah"] and af.calls == [], "AH: a click runs /ah as the player (%s)" % list(E.CM.lines))
    br.put("hub:tab:market:auctions", JArray(JObject)([S("SkyyAuctions"), S("Auctions"), Int.valueOf(20), S("ah"), af, None]))
    K.check(JV("MenuPage").redirect("tab:market:auctions", u) is None, "AH: a visible Auctions tab = itself")
    # ================================================================ TEXT
    bl = dict(zip(list(MD.HUB_ID), [str(x) for x in MD.HUB_BLURB]))
    K.check(bl.get("storage") == "Storage hub: the Void, Requip and your Vault (the Bank's coins are in it)." and "the Anvil" in bl.get("smithing", "")
            and "Upgrade (your tools)" in bl.get("smithing", ""), "TEXT: the Storage / Crafting blurbs: %s" % [bl.get("storage"), bl.get("smithing")])
    for k_ in ("storage:vault", "market:auctions"):
        br.remove("hub:tab:" + k_)
    MH.clearAll()
    JV("MenuIO").stop(2000)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    hcls = os.path.join(scratch, "hclasses_live")
    os.makedirs(hcls, exist_ok=True)
    os.chdir(scratch)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, hcls, jar], verify=True)
    E = T19.engine(scratch, hcls)
    JV = lambda n: JClass(PKG + n)
    Paths = E.Paths
    JV("PageGuard").STOP = False
    JV("PageGuard").EXEC = None
    ML = JV("MenuLayout")
    ML.DIR = Paths.get(os.path.join(home, "layouts"))
    ML.DEF_FILE = Paths.get(os.path.join(home, "layout-default.properties"))
    JV("SetStore").DIR = Paths.get(os.path.join(home, "settings"))
    JV("Given").DIR = Paths.get(os.path.join(home, "given-profile"))
    JV("Given").LEGACY = Paths.get(os.path.join(home, "given"))
    JV("SetReg").ADMIN_FILE = Paths.get(os.path.join(home, "settings-defaults.properties"))
    Cfg = JV("MenuCfg")
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    UniC = JClass("com.hypixel.hytale.server.core.universe.Universe")
    byU = jf(UniC.class_, "playersByUuid").get(UniC.get())
    snaps = [T19.snap(home)]
    res = []
    for n_ in range(2):
        ML.OWN.clear()
        ML.MIGRATED.clear()
        JV("MenuIO").begin()
        Cfg.init()
        Cfg.load()
        ML.loadDefault()
        JV("SetReg").loadAdmin(True)
        JV("SetReg").registerOwn()
        JV("SetReg").drain()
        P = E.player(E.UUID.fromString(SKYY))
        byU.put(P.pr.getUuid(), P.pr)
        n = int(JV("MenuHub").register())
        JV("SetLoadTask").preload(P.pr)
        ML.preload(P.pr.getUuid())
        hm = JV("MenuPage")(P.pr, "main")
        P.pm.openCustomPage(P.ref, P.st, hm)
        E.pump(P)
        c, _e = build_page(hm, P)
        ok = len(c) > 10
        time.sleep(0.8)
        ML.flushAll()
        JV("SetStore").flushAll()
        JV("MenuIO").stop(2000)
        JV("MenuHub").clearAll()
        snaps.append(T19.snap(home))
        res.append([n >= 7, ok])
    K.eq(res, [[True, True], [True, True]], "D: two starts on a COPY of the live Skyy_SkyyMenu: registry + Home built")
    a, b1, b2 = snaps
    K.check(a == b1 == b2, "D: neither start wrote a file (changed: %s)" % sorted(set(k for k in set(a) | set(b2) if a.get(k) != b2.get(k))))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("m", run_m), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
