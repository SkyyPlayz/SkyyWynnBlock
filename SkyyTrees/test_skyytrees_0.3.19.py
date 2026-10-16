"""SkyyTrees 0.3.19 - harness for round hubchar (Trees + Abilities = one tab: SkyyClasses 0.1.33's Class tab is a MERGED tab of the Trees
tab, kit skyyui HUB_MERGED; tools/trees_0_3_19_patch.py). Build first:
    python tools/trees_0_3_19_patch.py && python SkyyTrees/build_skyytrees_0.3.19.py
    python SkyyTrees/test_skyytrees_0.3.19.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Every JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch (tools/harness_kit.py).
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.18 -> 0.3.19: HubBar + the kit's MERGED TABS methods; TreePage.hubSel / handleDataEvent; the version texts; non-class
                entries: manifest.json only
  CT   EXECUTED (tools/hub_tab_kit.py engine stand-ins, the REAL PageManager, -Xverify:all), with a stand-in of SkyyClasses' Class tab:
       MERGED  the Class tab as SkyyClasses 0.1.33 puts it (8 elements, a hide Function answering FALSE, host "trees"): the strip has no
               Class tab; tree:fn:classPage (= /class) opens the class tree in Class tab mode with TREES selected (page_check 1600 x 980);
               the selected Trees tab = "self" (result line cleared, Respec disarmed, the class tree stays); the page's own tree tabs
               still switch trees (a skill tree, the class tree again - Trees selected on both); other tabs / < Menu / X as the contract
       OLD     the Class tab as SkyyClasses 0.1.32 puts it (6 elements, always visible): Class selected in Class tab mode and the Trees
               tab switches to the last skill tree, exactly as 0.3.18 (the 0.3.16 rule)
  ST1/ST2 start twice on a scratch COPY of the live Skyy_SkyyTrees folder (TreeCfg.load + the tab / classPage registration): nothing written
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import hub_tab_kit as HT
import deploy_set as DS

VERSION = "0.3.19"
PKG = "com.skyy.trees."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyTrees-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyTrees-0.3.18.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hubchar", "tr")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyyTrees")
ADDED = []
SUBM = ["+m hostOf", "+m hostShown", "+m hostTab", "+m openSub", "+m putSub", "+m selOf", "+m subIcon", "+m subTabs"]
EXPECT = {"HubBar": SUBM, "TreePage": ["~m hubSel", "~m handleDataEvent"], "SkyyTreesPlugin": ["~m setup"],
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "TreeCfg": ["~m load"]}       # + the version texts
FAIL_TEXT = "That tab could not open right now - try again."


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_ct(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Sto, Cfg, Defs, HO, CH, Page, HB = J("TreeStore"), J("TreeCfg"), J("TreeDefs"), J("TreesHubOpen"), J("TreeClassHub"), J("TreePage"), J("HubBar")
    Sto.DIR = E.Paths.get(scratch, "ct-mods", "Skyy_SkyyTrees", "players")
    os.makedirs(os.path.join(scratch, "ct-mods", "Skyy_SkyyTrees", "players"), exist_ok=True)
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001b9"), "TreeMerge")
    u = P.pr.getUuid()
    us = str(u)
    Int = JClass("java.lang.Integer")
    S = JClass("java.lang.String")
    NT = int(Defs.NT)
    CH.register()
    HO.register()

    @JImplements("java.util.function.Function")
    class Stub:
        def __init__(self, ans):
            self.calls, self.ans = [], ans

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            return self.ans
    copen, hide = Stub(E.TRUE), Stub(E.FALSE)
    merged = JArray(JObject)([S("SkyyClasses"), S("Class"), Int.valueOf(40), S("class"), copen, hide, S("character_class"), S("trees")])
    old = JArray(JObject)([S("SkyyClasses"), S("Class"), Int.valueOf(40), S("class"), copen, None])
    E.bridge.put("class:" + us, "Mage")
    Cfg.CLASS_ON = True
    fn = CH()

    def open_chub():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "TreePage") else None

    def click(p_, a):
        p_.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % a)
        E.pump(P)
        return E.pg(P)
    g = PW.calls(jar)
    K.check(PKG + "HubBar.selOf" in g.get("TreePage.hubSel", set()), "REG: hubSel() asks HubBar.selOf (bytecode)")
    # ---------------------------------------------------------------- MERGED (SkyyClasses 0.1.33)
    E.bridge.put("hub:tab:character:class", merged)
    K.check([str(x) for x in HT.hub_tabs(E, "character", u)] == ["trees"], "MERGED: the Character strip has no Class tab (%s)" % HT.hub_tabs(E, "character", u))
    Page.LASTTREE.put(u, Int.valueOf(2))
    pg = open_chub()
    K.check(pg is not None and int(pg.tree) == NT and bool(pg.chub), "MERGED: /class (tree:fn:classPage) = the class tree in Class tab mode")
    K.eq(str(pg.hubSel()), "trees", "MERGED: hubSel() = trees (Class is part of the Trees tab)")
    w, h, sets, evs = HT.page_check(K, E, P, HT.build(pg, P), "SkyyTrF", "character", "trees", "Trees", "MERGED class tree (Trees selected)", idp="SkyyTr")
    K.eq((w, h), (1600, 980), "MERGED class tree: 1600 x 980 as 0.3.18")
    K.check(any(s_ == "#SkyyTrTab%d" % NT for s_, _t in evs), "MERGED: the page's own class tree tab (abilities + loadout) is bound")
    pg.msg = "x"
    pg.armT = 2
    cur = click(pg, "hub:trees")
    K.check(E.same(cur, pg) and int(pg.tree) == NT and str(pg.msg) == "" and int(pg.armT) == -1 and int(Page.LASTTREE.get(u)) == 2,
            "MERGED: the selected Trees tab = self (the class tree stays, result line cleared, Respec disarmed)")
    cur = click(pg, "trtab0")
    K.check(E.same(cur, pg) and int(pg.tree) == 0 and str(pg.hubSel()) == "trees", "MERGED: the own Mining tab switches in place, Trees selected")
    HT.page_check(K, E, P, HT.build(pg, P), "SkyyTrF", "character", "trees", "Trees", "MERGED Mining", idp="SkyyTr")
    cur = click(pg, "trtab%d" % NT)
    K.check(E.same(cur, pg) and int(pg.tree) == NT and str(pg.hubSel()) == "trees", "MERGED: the own class tab again, Trees selected")
    fakes = HT.Fakes(E, "character")

    def open_armed():
        p_ = open_chub()
        p_.msg = "x"
        p_.armT = 2
        return p_
    HT.clicks(K, E, P, open_armed, "character", "trees", "CLICK merged class mode", fakes,
              self_check=lambda p_: str(p_.msg) == "" and int(p_.armT) == -1 and int(p_.tree) == NT, fail_text=FAIL_TEXT)
    fakes.remove()
    # ---------------------------------------------------------------- OLD (SkyyClasses 0.1.32: a Class tab of its own)
    E.bridge.put("hub:tab:character:class", old)
    K.check([str(x) for x in HT.hub_tabs(E, "character", u)] == ["trees", "class"], "OLD: Trees + Class tabs (0.1.32)")
    pg = open_chub()
    K.eq(str(pg.hubSel()), "class", "OLD: hubSel() = class in Class tab mode (as 0.3.18)")
    HT.page_check(K, E, P, HT.build(pg, P), "SkyyTrF", "character", "class", "Class", "OLD class tree (Class selected)", idp="SkyyTr")
    Page.LASTTREE.put(u, Int.valueOf(2))
    cur = click(pg, "hub:trees")
    K.check(E.same(cur, pg) and int(pg.tree) == 2 and not bool(pg.chub) and str(pg.hubSel()) == "trees", "OLD: the Trees tab switches to the last skill tree (the 0.3.16 rule)")
    E.bridge.remove("hub:tab:character:class")
    E.bridge.remove("class:" + us)
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, HO, CH = JClass(PKG + "TreeCfg"), JClass(PKG + "TreesHubOpen"), JClass(PKG + "TreeClassHub")
    Paths = JClass("java.nio.file.Paths")
    base = os.path.join(scratch, "st", "mods", "Skyy_SkyyTrees")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    f = [x for x in Cfg.class_.getDeclaredFields() if str(x.getName()) == "FILE"]
    if f:
        Cfg.FILE = Paths.get(os.path.join(base, "trees.properties"))
    lo = None
    try:
        lo = str(Cfg.load())
    except Exception as e:
        lo = "load: %s" % e
    r1, r2 = str(HO.register()), str(CH.register())
    HO.unregister()
    CH.unregister()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    K.check(bool(f) and not ch, "ST start %s on a scratch COPY of the live data (%d files): nothing written %s (load %s; tab %s, classPage %s)"
            % (step, len(before), ch, (lo or "")[:60], r1, r2))
    if step == "2":
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyyTrees folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyyTrees", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("ct", run_ct), ("st1", run_st1), ("st2", run_st2)], script=__file__)
