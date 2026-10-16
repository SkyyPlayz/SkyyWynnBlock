"""Harness for SkyyCollections 0.2.19 (STONE CONVERSIONS: our own cobble <-> rubble recipes in pocket crafting + the Workbench Survival
tab; tools/collections_0_2_19_patch.py). Build first:
    python tools/collections_0_2_19_patch.py && python SkyyCollections/build_skyycollections_0.2.19.py

    python SkyyCollections/test_skyycollections_0.2.19.py [--jar <SkyyCollections-0.2.19.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.18 -> 0.2.19: SkyyCollectionsPlugin.setup (version + ready line) + the config kit's version texts (CfgFn.opExport,
                CfgRows.header) only; non-class entries: manifest.json + the 32 new recipe files (nothing else changed or removed)
  ST   stone    recomputed HERE from Assets.zip and the SkyyBazaar SET pin, independently of the build: the 16 stones (every
                Rock_<S>_Cobble[_Mossy] with a Rubble_<S>[_Mossy] that its blocks hand out; Dawnstone's blocks drop Stone Rubble = out),
                each 1 cobble -> 1 rubble (= every vanilla Salvage_Rock_<S>_Cobble ratio) and n rubble -> 1 cobble (2; Cooled Magma 3),
                same stone in and out, item ids only (never the Rubble resource type), Fieldcraft "Tools" + Workbench "Workbench_Survival"
                (the Campfire's two benches), KnowledgeRequired false, TimeSeconds 0, no other key; no Bazaar profit at the 10 % spread and
                no round-trip gain; recipe ids / paths new to Assets.zip; no vanilla item JSON in the jar; server.lang byte-identical to
                0.2.18 (no lang key); no enabled pack mod already converting a pair; SkyySacks' SET pin reads the Fieldcraft recipes for
                /craft; the ready line = 0.2.19 + "32 stone conversion recipes"
  D    live     0.2.17's live phase (= 0.2.16's start twice on a scratch COPY of the live Skyy_SkyyCollections): nothing new written
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, ast, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import harness_kit as HK

_spec = importlib.util.spec_from_file_location("tc0218", os.path.join(HERE, "test_skyycollections_0.2.18.py"))
T18 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T18)

VERSION = "0.2.19"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.18.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "coll0219", "harness")))
PKG = "com.skyy.collections."
LIVE_DIR = T18.LIVE_DIR
EXPECT = {"SkyyCollectionsPlugin": ["~m setup"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"]}   # + the config kit's VERSION texts
ADDED = []
LANG = "Server/Languages/en-US/server.lang"
RDIR = "Server/Item/Recipes/SkyyCollections/"
STONES = ["Aqua", "Basalt", "Calcite", "Chalk", "Lime", "Magma_Cooled", "Marble", "Quartzite", "Sandstone", "Sandstone_Red",
          "Sandstone_White", "Shale", "Slate", "Stone", "Stone_Mossy", "Volcanic"]
REV_N = {"Magma_Cooled": 3}            # rubble per cobble; every other stone 2
BENCH = [{"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["Tools"]}, {"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Survival"]}]


def cob_of(k):
    return "Rock_Stone_Cobble_Mossy" if k == "Stone_Mossy" else "Rock_%s_Cobble" % k


def want_recipes():
    out = {}
    for k in STONES:
        out["SkyyCollections_Stone_Cobble_To_Rubble_" + k] = (cob_of(k), 1, "Rubble_" + k, 1)
        out["SkyyCollections_Stone_Rubble_To_Cobble_" + k] = ("Rubble_" + k, REV_N.get(k, 2), cob_of(k), 1)
    return out


RIDS = sorted(want_recipes())

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            exp = sorted(["manifest.json"] + [RDIR + r + ".json" for r in RIDS])
            return self.check(sorted(got) == exp, "C: non-class entries changed = manifest.json + the %d stone recipe files (extra %s, missing %s)" % (
                len(RIDS), sorted(set(got) - set(exp)), sorted(set(exp) - set(got))))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def bazaar_prices():
    import deploy_set as DS
    p = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_%s.py" % dict(DS.SET)["SkyyBazaar"])
    prices = {}
    for node in ast.parse(open(p, encoding="utf8").read()).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "PRODUCTS" for t in node.targets):
            lst = node.value.left if isinstance(node.value, ast.BinOp) else node.value
            for e in lst.elts:
                if isinstance(e, ast.Tuple) and isinstance(e.elts[0], ast.Constant):
                    prices[e.elts[0].value] = e.elts[1].value if isinstance(e.elts[1], ast.Constant) else None
    return os.path.basename(p), prices


def run_stone(out, jar, scratch, _home):
    import serverjar
    import deploy_set as DS
    K = HK.Child(out)
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    W = want_recipes()
    # ---- the jar's recipe files
    files = sorted(n for n in zn.namelist() if n.startswith("Server/Item/Recipes/"))
    K.eq(files, sorted(RDIR + r + ".json" for r in W), "ST: the jar's recipe files = the 32 stone recipes, nothing else under Server/Item/Recipes/")
    bad = []
    for rid, (i, qi, o, qo) in sorted(W.items()):
        d = json.loads(zn.read(RDIR + rid + ".json").decode("utf-8"))
        exp = {"Input": [{"ItemId": i, "Quantity": qi}], "PrimaryOutput": {"ItemId": o, "Quantity": qo}, "Output": [{"ItemId": o, "Quantity": qo}],
               "BenchRequirement": BENCH, "TimeSeconds": 0, "KnowledgeRequired": False}
        if d != exp:
            bad.append("%s: %s" % (rid, json.dumps(d)[:160]))
    K.check(not bad, "ST: every recipe = 1 cobble -> 1 rubble / n rubble -> 1 cobble, same stone, item ids, Fieldcraft Tools + Workbench Survival, "
                     "no knowledge, instant (%d bad: %s)" % (len(bad), bad[:3]))
    K.check(not any("ResourceTypeId" in zn.read(f).decode("utf-8") for f in files), "ST: no recipe takes a resource type (Any Rubble)")
    # ---- Assets.zip facts, read again here
    with zipfile.ZipFile(serverjar.assets_zip()) as z:
        names = z.namelist()
        ip = dict((os.path.basename(n)[:-5], n) for n in names if n.startswith("Server/Item/Items/") and n.endswith(".json"))

        def js(n):
            return json.loads(z.read(n).decode("utf-8-sig"))
        pairs = []
        for i in sorted(ip):
            m = re.match(r"^Rock_([A-Za-z_]+?)_Cobble(_Mossy)?$", i)
            if m and ("Rubble_" + m.group(1) + (m.group(2) or "")) in ip:
                pairs.append(m.group(1) + (m.group(2) or ""))
        K.eq(sorted(pairs), sorted(STONES + ["Dawnstone"]), "ST: Assets.zip cobble / rubble pairs = the 16 stones + Dawnstone")
        g = (js(ip["Rubble_Dawnstone"]).get("BlockType") or {}).get("Gathering") or {}
        dl = [n for n in names if n.startswith("Server/Drops/") and n.endswith("/Rubble_Flint.json")]
        K.check(all((g.get(t) or {}).get("DropList") == "Rubble_Flint" for t in ("Soft", "Harvest")) and len(dl) == 1
                and "Rubble_Dawnstone" not in z.read(dl[0]).decode("utf-8-sig") and '"Rubble_Stone"' in z.read(dl[0]).decode("utf-8-sig"),
                "ST: Dawnstone rubble blocks drop Stone Rubble (DropList Rubble_Flint) - nobody holds Rubble_Dawnstone, so no Dawnstone recipe")
        K.check(not any("Dawnstone" in r for r in W), "ST: no Dawnstone recipe")
        mids = []
        for k in STONES:
            for v in ("", "_Medium"):
                i = "Rubble_" + k + v
                if i not in ip:
                    continue
                gg = (js(ip[i]).get("BlockType") or {}).get("Gathering") or {}
                for t in ("Soft", "Harvest"):
                    e = gg.get(t) or {}
                    if e.get("ItemId"):
                        ok = e["ItemId"] == "Rubble_" + k
                    else:
                        dn = [n for n in names if n.startswith("Server/Drops/") and n.endswith("/%s.json" % e.get("DropList"))]
                        ok = len(dn) == 1 and set(re.findall(r'"ItemId"\s*:\s*"([^"]+)"', z.read(dn[0]).decode("utf-8-sig"))) == set(["Rubble_" + k])
                    if not ok:
                        mids.append("%s %s" % (i, t))
        K.check(not mids, "ST: breaking / F-picking each stone's small and _Medium rubble gives the small Rubble_<Stone> (%s)" % mids)
        K.check("Server/Item/Category/Fieldcraft/Tools.json" in names, "ST: pocket crafting's category Fieldcraft/Tools exists")
        camp = js(ip["Bench_Campfire"])["Recipe"]["BenchRequirement"]
        K.check(sorted((b["Id"], b.get("Categories")) for b in camp) == sorted((b["Id"], b["Categories"]) for b in BENCH),
                "ST: the benches = the Campfire recipe's own (Fieldcraft Tools + Workbench Survival)")
        cats = [c.get("Id") for c in js(ip["Bench_WorkBench"])["BlockType"]["Bench"]["Categories"]]
        K.check("Workbench_Survival" in cats, "ST: the Workbench has the Survival tab (%s)" % cats)
        # vanilla salvage = our forward ratio; no vanilla rubble -> cobble recipe
        sal = {}
        for n in names:
            m = re.match(r"^Server/Item/Recipes/.*/Salvage_(Rock_[A-Za-z_]+?_Cobble(?:_Mossy)?)\.json$", n)
            if m and m.group(1) in [cob_of(k) for k in STONES]:
                d = js(n)
                sal[m.group(1)] = (d["Input"][0]["Quantity"], d["PrimaryOutput"]["ItemId"], d["PrimaryOutput"]["Quantity"])
        K.eq(len(sal), 13, "ST: vanilla Salvagebench converts 13 of the 16 cobbles")
        K.check(all(qi == 1 and qo == 1 and o == "Rubble_" + [k for k in STONES if cob_of(k) == c][0] for c, (qi, o, qo) in sal.items()),
                "ST: every vanilla Salvage_Rock_<S>_Cobble is 1 cobble -> 1 same-stone rubble = our forward ratio (%s)" % sorted(sal.items())[:2])
        rev = []
        cobs = set(cob_of(k) for k in STONES)
        for n in names:
            if n.startswith("Server/Item/") and n.endswith(".json") and ("Rubble" in z.read(n).decode("utf-8-sig")):
                try:
                    d = js(n)
                except Exception:
                    continue
                b = os.path.basename(n)[:-5]
                if n.startswith("Server/Item/Items/") and b in cobs and isinstance(d.get("Recipe"), dict):
                    rev.append(b)
                if n.startswith("Server/Item/Recipes/") and ((d.get("PrimaryOutput") or {}).get("ItemId") in cobs):
                    rev.append(b)
        K.check(not rev, "ST: no vanilla recipe makes one of these cobbles from rubble (%s)" % rev)
        # new ids / paths
        vr = set(os.path.basename(n)[:-5] for n in names if n.startswith("Server/Item/Recipes/") and n.endswith(".json"))
        vr |= set(i + "_Recipe_Generated_0" for i in ip)
        K.check(not set(W) & vr and not set(files) & set(names), "ST: recipe ids and paths are new to Assets.zip")
    items = [n for n in zn.namelist() if n.startswith("Server/Item/Items/")]
    K.check(all(os.path.basename(n).startswith("Skyy_Ench_") for n in items), "ST: no vanilla item JSON in the jar (Server/Item/Items/ = our %d Skyy_Ench_ files)" % len(items))
    # ---- economy: no Bazaar profit at the default 10 % spread, no round-trip gain
    bzf, pr = bazaar_prices()
    eco = []
    for rid, (i, qi, o, qo) in sorted(W.items()):
        pi, po = pr.get(i), pr.get(o)
        if not (isinstance(pi, (int, float)) and isinstance(po, (int, float))):
            eco.append("%s: unpriced (%s, %s)" % (rid, pi, po))
        elif not (qo * po * 0.9 < qi * pi * 1.1):
            eco.append("%s: buy %.2f -> sell %.2f" % (rid, qi * pi * 1.1, qo * po * 0.9))
    K.check(not eco, "ST: no recipe pays on the Bazaar (%s base prices, buy x1.1 / sell x0.9): %s" % (bzf, eco or "ok"))
    K.check(all(1.0 / REV_N.get(k, 2) <= 1 for k in STONES), "ST: a round trip never gains (1 cobble -> 1 rubble -> 1/2 or 1/3 cobble)")
    K.notes.append("ST: Bazaar %s: cobble %s, rubble %s, Cooled Magma Cobble %s" % (bzf, pr.get("Rock_Stone_Cobble"), pr.get("Rubble_Stone"), pr.get("Rock_Magma_Cooled_Cobble")))
    # ---- lang untouched, ready line
    K.check(zn.read(LANG) == zo.read(LANG), "ST: server.lang byte-identical to 0.2.18 (no lang key added)")
    plug = zn.read("com/skyy/collections/SkyyCollectionsPlugin.class")
    K.check(b"0.2.19 ready" in plug and b"32 stone conversion recipes" in plug and b"0.2.18 ready" not in plug, "ST: the ready line = 0.2.19 + 32 stone conversion recipes")
    # ---- SkyySacks /craft: its SET pin reads the Fieldcraft bench recipes (its Crafting tab), no SkyySacks change needed
    ss = os.path.join(ROOT, "SkyySacks", "build_skyysacks_%s.py" % dict(DS.SET)["SkyySacks"])
    st = open(ss, encoding="utf8").read()
    K.check('getBenchRecipes(@BTP@.Crafting, "Fieldcraft")' in st and "Crafting = Fieldcraft" in st,
            "ST: SkyySacks %s's /craft Crafting tab reads the Fieldcraft recipes" % dict(DS.SET)["SkyySacks"])
    # ---- enabled pack mods (read-only): none converts one of these pairs already (no duplicate recipes in the pack)
    import skyybuild as B
    want = set(DS.PACK_THIRD_PARTY) - set(DS.PACK_DISABLED)
    dup, seen = [], 0
    pairs = dict((cob_of(k), "Rubble_" + k) for k in STONES)
    rubs = set(pairs.values())
    if os.path.isdir(B.MODS_DIR):
        for nm in sorted(os.listdir(B.MODS_DIR)):
            p = os.path.join(B.MODS_DIR, nm)
            if not nm.lower().endswith((".jar", ".zip")):
                continue
            try:
                zz = zipfile.ZipFile(p)
                man = json.loads(zz.read("manifest.json").decode("utf-8-sig"))
            except Exception:
                continue
            if "%s:%s" % (man.get("Group", ""), man.get("Name", "")) not in want:
                continue
            seen += 1
            for e in zz.namelist():
                if not (e.startswith("Server/Item/") and e.endswith(".json")):
                    continue
                t = zz.read(e).decode("utf-8-sig", "replace")
                if "Rubble_" in t and "_Cobble" in t:
                    hit = [r for r in rubs if r in t] and [c for c in pairs if c in t]
                    if hit:
                        dup.append("%s %s" % (nm, e))
    K.check(not dup, "ST: no enabled pack mod already converts cobble <-> rubble (%d of %d found): %s" % (seen, len(want), dup[:4]))
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("stone", run_stone), ("live", T18.T17.run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
