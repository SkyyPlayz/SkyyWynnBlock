"""SkyySkills 0.4.45 - harness for round hubchar (Stats + Skills = one tab: SkyyMenu 0.3.33's Stats tab is a MERGED tab of the Skills tab,
kit skyyui HUB_MERGED; /skills gets the sub-tabs YOUR STATS | SKILLS; tools/skills_0_4_45_patch.py).
Build first: python tools/skills_0_4_45_patch.py && python SkyySkills/build_skyyskills_0.4.45.py

    python SkyySkills/test_skyyskills_0.4.45.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (each a fresh child JVM: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in scratch; tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.4.44 -> 0.4.45: HubBar + the kit's MERGED TABS methods; SkillsPage build + handleDataEvent; the version texts; non-class
               entries: manifest.json only
  HUB EXECUTED (tools/hub_tab_kit.py: the SkyyMenu 0.3.19 harness's engine stand-ins, the REAL PageManager, -Xverify:all), with a stand-in
      of SkyyMenu's Stats tab:
      MERGED  the Stats tab as SkyyMenu 0.3.33 puts it (8 elements, a hide Function FALSE, host "skills"): no Stats tab in the strip;
              /skills built into a REAL builder = a hub page (page_check, Skills selected, 974 x 980); the sub-tab row FIRST in the body:
              YOUR STATS (bound to hub:stats) + SKILLS (active, hub:skills) + the hint beside them; the scrolling list 743 high with the
              12 rows; no hint line under the list. YOUR STATS -> the Stats tab's open Function (openSub: although its hide Function says
              FALSE); SKILLS -> the list in place (from the Top 10 view too)
      OLD     the Stats tab as SkyyMenu 0.3.32 puts it (a tab of its own): YOUR STATS still opens it
      NONE    no Stats tab (SkyyMenu not loaded): YOUR STATS is a blank of its width (no binding); a stray hub:stats click = one chat line
      PAGES   a skill's Stats page, the Top 10 view and the Overall page: unchanged hub pages (Skills selected)
  ST1/ST2 start twice on a scratch COPY of the live Skyy_SkyySkills folder (setup's one-time updates in order + SkillCfg.load + the tab):
      nothing written; the live folder is only read
  AA  engine-access audit
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

VERSION = "0.4.45"
PKG = "com.skyy.skills."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySkills-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySkills-0.4.44.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "hubchar", "sk")))
LIVE = os.path.join(B.HYTALE, "UserData", "Saves", DS.WORLD, "mods", "Skyy_SkyySkills")
ADDED = []
SUBM = ["+m hostOf", "+m hostShown", "+m hostTab", "+m openSub", "+m putSub", "+m selOf", "+m subIcon", "+m subTabs"]
EXPECT = {"HubBar": SUBM, "SkillsPage": ["~m build", "~m handleDataEvent"],
          # version texts (each checked by the compare: only the version constant differs)
          "SkillCfg": ["~m load"], "ManaGuard": ["~m armReport2", "~m intReport", "~m packReport"], "CfgRows": ["~<clinit>", "~m header"],
          "CfgFn": ["~m opExport"], "SkyySkillsPlugin": ["~m setup"]}
MIGS = ("ManaMig", "HealMig", "DocMig", "ClassManaMig", "SkillLvMig", "KillXpMig", "AcroMig", "PerkMig", "PollMig", "RbCoinMig", "Pd44Mig")


def tree_hash(root):
    o = {}
    for d, _x, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            o[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return o


def run_hub(out, jar, scratch, _home):
    from jpype import JClass, JArray, JLong, JImplements, JOverride, JObject
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    E.HB = PKG + "HubBar"
    J = lambda n: JClass(PKG + n)
    Cfg, Sto, Defs, HO, HB = J("SkillCfg"), J("SkillStore"), J("SkillDefs"), J("SkillsHubOpen"), J("HubBar")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    P = E.mkp(E.UUID.fromString("00000000-0000-0000-0000-0000000001a5"), "SkillMerge")
    u = P.pr.getUuid()
    N = int(Defs.N)
    dd = [0] * (2 * N)
    for sl in (0, 1, 2, 4):
        dd[sl] = 4000
    Sto.DATA.put(str(u), JArray(JLong)(dd))
    S, Int = JClass("java.lang.String"), JClass("java.lang.Integer")
    HO.register()

    @JImplements("java.util.function.Function")
    class Stub:
        def __init__(self, ans):
            self.calls, self.ans = [], ans

        @JOverride
        def apply(self, o):
            self.calls.append(str(o))
            return self.ans
    sopen, hide = Stub(E.TRUE), Stub(E.FALSE)
    merged = JArray(JObject)([S("SkyyMenu"), S("Stats"), Int.valueOf(10), S("stats"), sopen, hide, S("character_stats"), S("skills")])
    old = JArray(JObject)([S("SkyyMenu"), S("Stats"), Int.valueOf(10), S("stats"), sopen, None, S("character_stats")])
    fn = HO()

    def open_page():
        r = fn.apply(u)
        E.pump(P)
        pg = E.pg(P)
        return pg if (r == E.TRUE and pg is not None and str(pg.getClass().getName()) == PKG + "SkillsPage") else None

    def click(p_, word):
        p_.handleDataEvent(P.ref, P.st, '{"a":"%s"}' % word)
        E.pump(P)
        return E.pg(P)
    g = PW.calls(jar)
    K.check(PKG + "HubBar.openSub" in g.get("SkillsPage.handleDataEvent", set()), "REG: the list's YOUR STATS goes through HubBar.openSub (bytecode)")
    # ---------------------------------------------------------------- MERGED (SkyyMenu 0.3.33)
    E.bridge.put("hub:tab:character:stats", merged)
    K.check([str(x) for x in HT.hub_tabs(E, "character", u)] == ["skills"], "MERGED: the Character strip has no Stats tab (%s)" % HT.hub_tabs(E, "character", u))
    pg = open_page()
    built = HT.build(pg, P)
    w, h, sets, evs = HT.page_check(K, E, P, built, "SkyySkF", "character", "skills", "Skills", "MERGED /skills", idp="SkyySk")
    K.eq((w, h), (974, 980), "MERGED /skills: 974 x 980 as 0.4.44")
    apps = [(s_, t) for ty, s_, t, d in built[0] if t]
    body = [t for s_, t in apps if s_ == "#SkyySkills"]
    K.check(len(body) >= 4 and body[0].startswith("Group #SkyySkillsHubTabs") is False and any(t.startswith("Group #SkyySkSubRow ") for t in body[:3]),
            "MERGED /skills: the sub-tab row sits right under the strip (%s)" % [t[:30] for t in body[:4]])
    sub = [t for s_, t in apps if s_ == "#SkyySkSubRow"]
    K.check(len(sub) == 3 and "#SkyySkSubMe " in sub[0] and "YOUR STATS" in sub[0].upper() and "#SkyySkSubSk " in sub[1] and "Primary" in sub[1]
            and "#SkyySkHint " in sub[2], "MERGED /skills: YOUR STATS | SKILLS (active) | the hint (%s)" % [t[:60] for t in sub])
    K.check(any(s_ == "#SkyySkSubMe" and "hub:stats" in t for s_, t in evs) and any(s_ == "#SkyySkSubSk" and "hub:skills" in t for s_, t in evs),
            "MERGED /skills: YOUR STATS = hub:stats, SKILLS = hub:skills")
    ls = [t for s_, t in apps if "#SkyySkList " in t]
    K.check(len(ls) == 1 and "TopScrolling" in ls[0] and "Height: 743" in ls[0], "MERGED /skills: the scrolling list 743 high (%s)" % (ls[0][:120] if ls else None))
    rows = [t for s_, t in apps if s_ == "#SkyySkList" and t.startswith("Group #SkyySkRow")]
    K.check(len(rows) == 12, "MERGED /skills: the 12 skill rows (%d)" % len(rows))
    K.check(not [t for s_, t in apps if s_ == "#SkyySkills" and "#SkyySkHint " in t], "MERGED /skills: no hint line under the list any more")
    del sopen.calls[:]
    del hide.calls[:]
    cur = click(pg, "hub:stats")
    K.check(sopen.calls == [str(u)] and not hide.calls and not list(E.CM.lines), "MERGED: YOUR STATS opens the Stats tab through its Function, hide never asked (%s)" % sopen.calls)
    pg = open_page()
    pg.view = 0
    cur = click(pg, "hub:skills")
    K.check(E.same(cur, pg) and int(pg.view) == -1, "MERGED: SKILLS (the selected tab) = the list in place, from the Top 10 view too")
    # the sub-pages stay as 0.4.44 (Skills selected)
    pg = open_page()
    st = click(pg, "skstat0")
    if st is not None:
        HT.page_check(K, E, P, HT.build(st, P), "SkyyStF", "character", "skills", "Skills", "PAGES a skill's Stats page", idp="SkyyS")
    pg = open_page()
    ov = click(pg, "skstatov")
    if ov is not None:
        HT.page_check(K, E, P, HT.build(ov, P), "SkyyOvPage", "character", "skills", "Skills", "PAGES Overall", idp="SkyyOv")
    pg = open_page()
    pg.view = 0
    HT.page_check(K, E, P, HT.build(pg, P), "SkyySkF", "character", "skills", "Skills", "PAGES Top 10", idp="SkyySk")
    K.check(not [t for ty, s_, t, d in HT.build(pg, P)[0] if t and "#SkyySkSubRow " in t], "PAGES Top 10: no sub-tab row (its own Back)")
    # ---------------------------------------------------------------- OLD (SkyyMenu 0.3.32)
    E.bridge.put("hub:tab:character:stats", old)
    K.check([str(x) for x in HT.hub_tabs(E, "character", u)] == ["stats", "skills"], "OLD: Stats + Skills tabs (0.3.32)")
    del sopen.calls[:]
    pg = open_page()
    click(pg, "hub:stats")
    K.check(sopen.calls == [str(u)], "OLD: YOUR STATS opens SkyyMenu 0.3.32's Stats tab too")
    # ---------------------------------------------------------------- NONE
    E.bridge.remove("hub:tab:character:stats")
    pg = open_page()
    built = HT.build(pg, P)
    sub = [t for ty, s_, t, d in built[0] if t and s_ == "#SkyySkSubRow"]
    K.check(sub and sub[0].startswith("Group #SkyySkSubMe ") and not any(s_ == "#SkyySkSubMe" for s_, t in built[1]),
            "NONE: no Stats tab -> YOUR STATS is a blank of its width, not bound (%s)" % (sub[0][:60] if sub else None))
    HT.page_check(K, E, P, built, "SkyySkF", "character", "skills", "Skills", "NONE /skills", idp="SkyySk")
    n0 = len(E.sent(P))
    cur = click(pg, "hub:stats")
    K.check(E.same(cur, pg) and "Your Stats page could not open" in E.strs_of(P, n0), "NONE: a stray hub:stats = one chat line, the page stays")
    K.save()


def run_st(out, jar, scratch, step):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    J = lambda n: JClass(PKG + n)
    Cfg, HO = J("SkillCfg"), J("SkillsHubOpen")
    Cfg.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySkills")
    Paths = JClass("java.nio.file.Paths")
    base = os.path.join(scratch, "st", "mods", "Skyy_SkyySkills")
    if step == "1":
        shutil.rmtree(os.path.join(scratch, "st"), ignore_errors=True)
        shutil.copytree(LIVE, base)
        json.dump(tree_hash(LIVE), open(os.path.join(scratch, "st-live.json"), "w"))
    before = tree_hash(base)
    J("SkillStore").DIR = Paths.get(os.path.join(base, "players"))
    J("PlacedStore").DIR = Paths.get(os.path.join(base, "placed"))
    Cfg.FILE = Paths.get(os.path.join(base, "xp.properties"))
    ran = []
    for m in MIGS:
        J(m).run()
        ran.append(m)
    rules = str(Cfg.load())
    reg = str(HO.register())
    HO.unregister()
    after = tree_hash(base)
    ch = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    K.check(not ch and reg == "character:skills" and len(ran) == len(MIGS),
            "ST start %s on a scratch COPY of the live data (%d files; %d one-time updates + load + the tab): nothing written %s" % (step, len(before), len(ran), ch))
    if step == "2":
        K.check(tree_hash(LIVE) == json.load(open(os.path.join(scratch, "st-live.json"))), "ST: the live Skyy_SkyySkills folder was only read")
    K.save()
    sys.stdout.flush()
    os._exit(0)


def run_st1(out, jar, scratch, _home):
    run_st(out, jar, scratch, "1")


def run_st2(out, jar, scratch, _home):
    run_st(out, jar, scratch, "2")


if __name__ == "__main__":
    HK.run(name="SkyySkills", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("hub", run_hub), ("st1", run_st1), ("st2", run_st2)], script=__file__)
