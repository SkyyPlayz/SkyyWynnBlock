"""Harness for SkyyCollections 0.2.27 (round c227: the zone-metal tool tier-up gates - tierup:<kind>:<Metal> for SkyyGear 0.3.23+'s nine new
ladder metals, the Server Setup reward check, CollRw27Mig; tools/collections_0_2_27_patch.py). Build first:
    python tools/collections_0_2_27_patch.py && python SkyyCollections/build_skyycollections_0.2.27.py

    python SkyyCollections/test_skyycollections_0.2.27.py [--jar <SkyyCollections-0.2.27.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.26 -> 0.2.27: exactly the listed members differ (+ the new class CollRw27Mig); non-class entries: manifest.json only
  X    exec     the default rewards: 0.2.26's table + ONLY the 36 tierup tokens (each on its gate tier, nothing else changed); coll:fn:tierup
                answers each of the 36 "<kind>:<Metal>" with its gate ("0|Lead|Lead Ore|4|250|0" ...) and "1|..." once the counts reach it;
                the old tokens answer as in 0.2.26 (pickaxe:Iron), an unknown one stays null; coll:fn:tierups lists them for a profile; the
                page cell text says "Lead Pickaxe tier-up"; the Server Setup check takes tierup:pickaxe:Lead / Lumen, still refuses a bad word
  T    migr     CollRw27Mig on the 0.2.26 default (from the 0.2.26 jar) -> exactly the 0.2.27 table; on the LIVE rewards.properties text (read
                only) after the older updates; CRLF; no final newline; a hand-edited gate line kept + logged; a removed one stays removed; a 2nd
                run and the fresh 0.2.27 default = nothing
  D    live     the setup order on a scratch COPY of the live Skyy_SkyyCollections, started twice: CollRw27Mig once (History copy byte for byte,
                one Undo row per entry, migration-tierup27.log), the 2nd start changes nothing, the live registry gates the 36 tokens
  M    pages    the 0.2.23 page phase on this jar (assert_menu_page on every view)
  AA   audit    the engine-access audit
Scratch: tools/dev/scratch/c227/coll (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, re, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

VERSION = "0.2.27"
OLD_VERSION = "0.2.26"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "c227", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyCollections")
METALS = ["Bronze", "Lead", "Dusk", "Chromium", "Azurvane", "Slag", "Cinder", "Titanium", "Lumen"]
KINDS = ["pickaxe", "hatchet", "harvester", "can"]
# the gate table the patch header promises (written out by hand - the build computes it from the rules)
GATE = {"pickaxe": {"Bronze": ("Iron", 5), "Lead": ("Lead", 4), "Dusk": ("Lead", 5), "Chromium": ("Chromium", 4), "Azurvane": ("Chromium", 5),
                    "Slag": ("Slag", 3), "Cinder": ("Slag", 4), "Titanium": ("Titanium", 3), "Lumen": ("Titanium", 4)},
        "hatchet": {"Bronze": ("GumboabLog", 4), "Lead": ("RedwoodLog", 4), "Dusk": ("RedwoodLog", 4), "Chromium": ("SallowLog", 4),
                    "Azurvane": ("SallowLog", 4), "Slag": ("SallowLog", 5), "Cinder": ("SallowLog", 5), "Titanium": ("SallowLog", 6), "Lumen": ("SallowLog", 6)}}
_CROP = {"Bronze": "Cauliflower", "Lead": "Pumpkin", "Dusk": "Pumpkin", "Chromium": "Tomato", "Azurvane": "Tomato", "Slag": "Cotton", "Cinder": "Cotton",
         "Titanium": "Potato", "Lumen": "Potato"}
GATE["harvester"] = dict((m, (_CROP[m], 4)) for m in METALS)
GATE["can"] = dict((m, (_CROP[m], 4)) for m in METALS)
TOKS = dict(("%s:%s" % (k, m), GATE[k][m]) for k in KINDS for m in METALS)
EXPECT = {"CollReg": ["~m rewardsText"],                            # the default rewards.properties (+ the 36 tokens, the marker)
          "CollKit": ["~m rewardToken"],                            # the reward check takes the zone metal words
          "CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"],   # the kit's version texts + the rewards.properties default text
          "CollTier": ["~<clinit>"],                                # tools/tier_tags.py rows added since 0.2.26 was built (SkyyGear 0.3.23 tools,
                                                                    # SkyyArmory 0.1.33 / 0.1.34 weapons): the recipe list's tier sort table
          "SkyyCollectionsPlugin": ["~m setup"]}                    # CollRw27Mig + the ready line
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["CollRw27Mig"]


def _mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    _a = list(sys.argv)
    spec.loader.exec_module(m)
    sys.argv[:] = _a
    return m


def T21():
    return _mod("t21", os.path.join(HERE, "test_skyycollections_0.2.21.py"))


def T23():
    return _mod("t23", os.path.join(HERE, "test_skyycollections_0.2.23.py"))


def P(n):
    from jpype import JClass
    return JClass(PKG + n)


def old_cls(n):
    from jpype import JClass, JArray
    U_ = JClass("java.net.URL")
    srv = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(B.SERVER_JAR).toURI().toURL()]), JClass("java.lang.ClassLoader").getPlatformClassLoader())
    L = JClass("java.net.URLClassLoader")(JArray(U_)([JClass("java.io.File")(OLD_JAR).toURI().toURL()]), srv)
    return JClass(PKG + n, loader=L)


def table(t_):
    from jpype import JArray, JString
    return dict((str(k), [str(x) for x in v]) for k, v in P("CollCobMig").table(JArray(JString)([l_.rstrip("\r") for l_ in t_.split("\n")])).items())


# ------------------------------------------------------------------------------------------------------------------- X: exec
def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Store, Util, Fn, Kit = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollFn"), P("CollKit")
    base = t21.fresh(scratch, "x")
    R = Reg.D
    ids = [str(R.id[c]) for c in range(R.n)]
    BY = dict((i, c) for c, i in enumerate(ids))
    # the default table: 0.2.26's + only the 36 tokens
    new, old = table(str(Reg.rewardsText())), table(str(old_cls("CollReg").rewardsText()))
    K.eq(sorted(new), sorted(old), "X the default rewards: the same %d keys as 0.2.26" % len(old))
    diff = dict((k, [x for x in new[k] if x not in old[k]]) for k in new if new[k] != old[k])
    K.check(all([x for x in new[k] if x in old[k]] == old[k] for k in diff), "X every changed line keeps all its 0.2.26 tokens in their order")
    got = {}
    for k, add in diff.items():
        for x in add:
            got[x] = k
    want = dict(("tierup:" + t, "%s.%d" % (c.lower(), n)) for t, (c, n) in TOKS.items())
    K.eq(sorted(got.items()), sorted(want.items()), "X the ONLY additions are the 36 tierup tokens, each on its gate tier (%d lines)" % len(diff))
    # coll:fn:tierup for each of the 36: gate + progress
    fn = Fn("tierup")
    O = JClass("java.lang.Object")
    ans = lambda who, tok: fn.apply(JArray(O)([who, JString(tok)]))
    bad = []
    for t, (c, n) in TOKS.items():
        r = ans(None, t)
        th = int(Reg.threshold(R, BY[c], n))
        w = "0|%s|%s|%d|%d|0" % (c, str(R.name[BY[c]]), n, th)
        if r is None or str(r) != w:
            bad.append((t, None if r is None else str(r), w))
    K.eq(bad, [], "X coll:fn:tierup {null, <kind>:<Metal>} = the gate for all 36 (pickaxe:Lead -> %s)" % ans(None, "pickaxe:Lead"))
    K.check(str(ans(None, "pickaxe:Iron")).startswith("0|Iron|") and str(ans(None, "hatchet:Adamantite")).startswith("0|SallowLog|")
            and ans(None, "pickaxe:Onyxium") is None and ans(None, "shovel:Lead") is None and ans(None, "PICKAXE:Lead") is not None,
            "X old tokens unchanged (pickaxe:Iron, hatchet:Adamantite); pickaxe:Onyxium / shovel:Lead still null; the kind in any case")
    # a profile: Lead at its tier IV threshold, Chromium one under -> pickaxe:Lead 1, pickaxe:Dusk 0, pickaxe:Chromium 0
    UUID = JClass("java.util.UUID")
    u = UUID.fromString("00000000-0000-0000-0000-0000000c2270")
    key = str(Util.pkey(u))
    lead4 = int(Reg.threshold(R, BY["Lead"], 4))
    chr4 = int(Reg.threshold(R, BY["Chromium"], 4))
    t21.counts(base, key, [("Ore_Lead_SkyWynn", lead4), ("Ore_Chromium_SkyWynn", chr4 - 1)])
    r1, r2, r3 = str(ans(u, "pickaxe:Lead")), str(ans(u, "pickaxe:Dusk")), str(ans(JString(key), "pickaxe:Chromium"))
    K.check(r1 == "1|Lead|%s|4|%d|%d" % (R.name[BY["Lead"]], lead4, lead4) and r2.startswith("0|Lead|") and r2.split("|")[3] == "5" and r3.startswith("0|Chromium|")
            and r3.endswith("|%d" % (chr4 - 1)), "X progress: Lead IV reached -> pickaxe:Lead 1, pickaxe:Dusk 0 (Lead V), pickaxe:Chromium 0 (%s / %s / %s)" % (r1, r2, r3))
    tl = str(Fn("tierups").apply(u))
    K.check("pickaxe:Lead" in tl.split(",") and "pickaxe:Dusk" not in tl.split(",") and "pickaxe:Chromium" not in tl.split(","),
            "X coll:fn:tierups lists pickaxe:Lead (not Dusk / Chromium): %s" % tl)
    # the page texts
    cell = str(Reg.rewardTextP(R, BY["Lead"], 4, False))
    cell2 = str(Reg.rewardTextP(R, BY["Iron"], 5, False))
    cell3 = str(Reg.rewardTextP(R, BY["Pumpkin"], 4, False))
    K.check("Lead Pickaxe tier-up" in cell and "Bronze Pickaxe tier-up" in cell2 and "Mining Armor tier-up" in cell2
            and "Lead Harvester tier-up" in cell3 and "Dusk Watering Can tier-up" in cell3 and "Cobalt Harvester tier-up" in cell3,
            "X page cells: Lead IV '%s' / Iron V '%s' / Pumpkin IV '%s'" % (cell[:90], cell2[:120], cell3[:160]))
    # the Server Setup reward check
    ck = lambda v: Kit.rewardToken(JString(v))
    K.check(ck("tierup:pickaxe:Lead") is None and ck("tierup:can:Lumen") is None and ck("tierup:hatchet:Iron") is None
            and ck("tierup:pickaxe:Gold") is not None and "Lumen" in str(ck("tierup:pickaxe:Gold")),
            "X Server Setup: tierup:pickaxe:Lead / can:Lumen / hatchet:Iron accepted, tierup:pickaxe:Gold refused (%s)" % str(ck("tierup:pickaxe:Gold"))[:80])
    K.notes.append("X gate table: " + "; ".join("%s %s" % (k, ", ".join("%s=%s %d" % (m, GATE[k][m][0], GATE[k][m][1]) for m in METALS)) for k in KINDS))
    K.save()


# ------------------------------------------------------------------------------------------------------------------- T: migr
def run_migr(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    t21 = T21()
    Reg, Rw = P("CollReg"), P("CollRw27Mig")
    OLDER = [P(n) for n in ("CollToolMig", "CollRw21Mig", "CollRw24Mig", "CollRw25Mig")]
    t21.fresh(scratch, "t")
    OLDDEF = str(old_cls("CollReg").rewardsText())          # the 0.2.26 default
    DEF = str(Reg.rewardsText())

    def upd(t_):
        r_ = Rw.update(t_)
        return None if r_ is None else (str(r_[0]), [str(x) for x in r_[1]], str(r_[2]), int(r_[3]), int(r_[4]), bool(r_[5]), int(r_[6]))
    nk = len(Rw.K)
    K.check(nk == len(set((c, n) for c, n in TOKS.values())) and all(str(o) != "" for o in Rw.OLDV), "T CollRw27Mig: %d gate tier entries, each an existing 0.2.26 line" % nk)
    K.check(Rw.update(DEF) is None and all(M_.update(DEF) is None for M_ in OLDER), "T a fresh 0.2.27 rewards.properties: every update = nothing (markers)")
    u0 = upd(OLDDEF)
    K.check(u0 is not None and u0[5] and u0[3] == nk and u0[4] == 0 and table(u0[0]) == table(DEF) and upd(u0[0]) is None,
            "T the 0.2.26 default -> the loader reads exactly the 0.2.27 default (%d entries updated); a 2nd run = nothing" % nk)
    K.check(len(u0[1]) == 3 * nk and all(u0[1][i + 1] != "(none)" and "tierup:" in u0[1][i + 2] for i in range(0, len(u0[1]), 3)),
            "T one Undo row per entry (old line -> line + tierup tokens)")
    ol, nl = OLDDEF.split("\n"), u0[0].split("\n")
    K.check(len(nl) == len(ol) + 1 and sum(1 for a in ol if a not in nl) == nk, "T only the %d gate lines changed + the marker line" % nk)
    # the LIVE text (read only): the older updates first, like setup
    live = open(os.path.join(LIVE_DIR, "rewards.properties"), "rb").read().decode("latin-1")
    t_ = live
    for M_ in OLDER:
        r_ = M_.update(t_)
        t_ = t_ if r_ is None else str(r_[0])
    u1 = upd(t_)
    K.check(u1 is not None and u1[5] and upd(u1[0]) is None, "T the LIVE file: %d entries updated, %d kept by hand; the loader reads the old table + those; a 2nd run = nothing" % (u1[3], u1[4]))
    tl = table(u1[0])
    K.check(all(("tierup:" + t) in tl.get("%s.%d" % (c.lower(), n), []) for t, (c, n) in TOKS.items()) if u1[4] == 0 else True,
            "T the LIVE file: every gate line holds its tokens")
    mk = str(Rw.MARK5)
    K.check(u1[0].count(mk) == 1, "T the marker once")
    crlf = t_.replace("\r\n", "\n").replace("\n", "\r\n")
    uc = upd(crlf)
    K.check(uc[5] and uc[0].count("\r\n") == uc[0].count("\n") and uc[3] == u1[3], "T CRLF kept on every line")
    une = upd(t_.rstrip("\n").rstrip("\r"))
    K.check(une[5] and not une[0].endswith("\n") and une[3] == u1[3], "T no final newline stays none")
    lk = [l_ for l_ in t_.split("\n") if l_.lower().startswith("lead.4=")]
    own = t_.replace(lk[0], "Lead.4=coins:7", 1) if lk else t_
    uo = upd(own)
    K.check(bool(lk) and uo[5] and uo[3] == u1[3] - 1 and uo[4] == 1 and table(uo[0])["lead.4"] == ["coins:7"] and "kept hand-edited line" in uo[2],
            "T a hand-edited Lead.4 line: kept + logged, the other entries updated")
    gone = "\n".join(l_ for l_ in t_.split("\n") if not l_.lower().startswith("lead.4="))
    ug = upd(gone)
    K.check(ug[5] and ug[3] == u1[3] - 1 and "lead.4" not in table(ug[0]) and "an admin removed it" in ug[2], "T a removed Lead.4 line stays removed (logged)")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- D: live
def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Reg, Store = P("CollReg"), P("CollStore")
    b_ = JClass("java.nio.file.Paths").get(home)
    rw0 = open(os.path.join(home, "rewards.properties"), "rb").read()
    msgs, hs = [], []
    for start in (1, 2):
        Reg.BASE = b_
        Store.DIR = b_.resolve("counts")
        P("CollBagMigrate").run(b_)
        P("CollBypassMig").run(b_)
        P("CollCoinMig").run(b_)
        Reg.loadAll()
        for m in ("CollCobMig", "CollSigMig", "CollShardMig", "CollToolMig", "CollRw21Mig", "CollRw24Mig", "CollRw25Mig"):
            P(m).run(b_)
        msgs.append(str(P("CollRw27Mig").run(b_)))
        hs.append(HK.tree_hash(home))
    K.check(msgs[0].startswith("zone-metal tool tier-ups added") and msgs[1] == "" and hs[0] == hs[1],
            "D the 1st start adds the tier-ups once (%s), the 2nd changes nothing" % msgs[0][:140])
    fn = P("CollFn")("tierup")
    O = JClass("java.lang.Object")
    miss = [t for t in TOKS if fn.apply(JArray(O)([None, JString(t)])) is None]
    K.eq(miss, [], "D the live registry gates all 36 tokens")
    chg = open(os.path.join(home, "config-changes.log"), encoding="latin-1").read()
    rows = [l_ for l_ in chg.split("\n") if "SkyyCollections 0.2.27" in l_]
    K.check(len(rows) == len(P("CollRw27Mig").K) and all("\trewards[" in l_ for l_ in rows), "D %d Undo rows (rewards[<entry>])" % len(rows))
    hist = os.path.join(home, "config-history")
    K.check(os.path.isdir(hist) and any(open(os.path.join(hist, f), "rb").read() == rw0 for f in os.listdir(hist) if f.startswith("Skyy_SkyyCollections~rewards.properties")),
            "D config-history holds the old rewards.properties byte for byte")
    K.check(os.path.isfile(os.path.join(home, "migration-tierup27.log")), "D migration-tierup27.log written")
    K.save()


# ------------------------------------------------------------------------------------------------------------------- M: pages
def run_pages(out, jar, scratch, home):
    """the 0.2.23 page phase as it is; its one version check (the ready line names 0.2.23) asks for 0.2.27 instead"""
    ck0 = HK.Child.check
    plug = zipfile.ZipFile(jar).read("com/skyy/collections/SkyyCollectionsPlugin.class")

    def ck(self, cond, what):
        if what == "PAGE the ready line names 0.2.23":
            return ck0(self, re.search(rb"\[SkyyCollections\] 0\.2\.27 ready", plug) is not None, "PAGE the ready line names 0.2.27")
        return ck0(self, cond, what)
    eq0 = HK.Child.eq
    TAGS = ["", "Armor_Copper_Chest", "Armor_Copper_Head", "Ingredient_Bar_Iron", "Tool_Pickaxe_Mithril"]

    def eq(self, got, want, what):
        if what == "LIST the tier tags" and want == ["", "T2", "T2", "T3", "T7"]:          # the 0.2.23 numbers; TT_VERSION 2 (0.2.26) renumbered them
            w2 = [""] + [str(P("CollTier").tierText(i)) for i in TAGS[1:]]          # this jar's own tag of each row's output
            eq0(self, w2, ["", "T1", "T1", "T2", "T13"], "LIST the rows' tags on the TT_VERSION 2 ladder (Copper T1, Iron T2, Mithril T13)")
            return eq0(self, got, w2, "LIST the tier tags (TT_VERSION 2 ladder)")
        return eq0(self, got, want, what)
    HK.Child.check = ck
    HK.Child.eq = eq
    T23().run_pages(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("exec", run_exec), ("migr", run_migr), ("pages", run_pages), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
