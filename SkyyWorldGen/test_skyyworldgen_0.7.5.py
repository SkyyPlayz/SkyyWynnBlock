"""Harness for SkyyWorldGen 0.7.5 (round wg75: alloy output = input, tools/worldgen_0_7_5_patch.py). Build first:
    python tools/worldgen_0_7_5_patch.py && python SkyyWorldGen/build_skyyworldgen_0.7.5.py

    python SkyyWorldGen/test_skyyworldgen_0.7.5.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.7.4 -> 0.7.5: only the version texts differ (EXPECT); non-class entries: manifest.json, server.lang, the 6 alloy recipes
               and the 3 instance templates (every item JSON, texture and icon byte-identical)
  V    version  the changed classes differ only in their version string constants; the 3 instance templates only in the version
  R    recipes  the per-alloy in / out table 0.7.4 -> 0.7.5: each Alloy_<Name>.json differs ONLY in PrimaryOutput / Output Quantity 1 -> 2
               (= the sum of its input quantities); inputs, bench SkyyAlloy and TimeSeconds identical
  AS   assets   every JSON entry parses; every recipe input / output id is a vanilla item (Assets.zip, read-only) or an item of this jar;
               every own item's Texture / Icon is in the jar; assets plain ASCII
  L    lang     server.lang 0.7.4 -> 0.7.5: the same keys in the same order; the ONLY changed lines are the 5 own alloy descriptions, each
               = the 0.7.4 text with " (1 + 1 makes 2)" after "Alloy of A + B" (so the tier tag stays first, byte for byte)
  G    gate     the Furnace Charm gate is unchanged: the 6 alloy recipes keep bench id "SkyyAlloy" and their output ids, and SkyySacks
               (SET pin) ProcBench still names "SkyyAlloy" + those 6 ids (its ALLOY_TIER reads the output id, not the quantity)
  AA   audit    the engine-access audit
No tools/tier_tags.py import (another builder may be editing it): the tags are proved against the 0.7.4 jar's own text.
Exit code 1 on any failure.
"""
import os, sys, re, json, struct, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

VERSION = "0.7.5"
OLD_VERSION = "0.7.4"
SACKS = os.path.join(ROOT, "SkyySacks", "SkyySacks-0.8.23.jar")      # the tools/deploy_set.py SET pin (Furnace Charm gate)
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyWorldGen-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wg75", "wg")))
PKG = "com.skyy.worldgen."
LANG = "Server/Languages/en-US/server.lang"
RDIR = "Server/Item/Recipes/SkyWynn/"
ALLOYS = {  # recipe word -> (output id, input A, input B, seconds, Furnace Charm tier in SkyySacks ProcBench.ALLOY_TIER)
    "Bronze": ("Ingredient_Bar_Bronze", "Ingredient_Bar_Copper", "Ingredient_Bar_Iron", 24, 1),
    "Dusk": ("Ingredient_Bar_Dusk_SkyWynn", "Ingredient_Bar_Thorium", "Ingredient_Bar_Lead_SkyWynn", 36, 2),
    "Azurvane": ("Ingredient_Bar_Azurvane_SkyWynn", "Ingredient_Bar_Cobalt", "Ingredient_Bar_Chromium_SkyWynn", 36, 3),
    "Cinder": ("Ingredient_Bar_Cinder_SkyWynn", "Ingredient_Bar_Adamantite", "Ingredient_Bar_Slag_SkyWynn", 40, 4),
    "Lumen": ("Ingredient_Bar_Lumen_SkyWynn", "Ingredient_Bar_Mithril", "Ingredient_Bar_Titanium_SkyWynn", 60, 5),
    "Electrum": ("Ingredient_Bar_Electrum_SkyWynn", "Ingredient_Bar_Gold", "Ingredient_Bar_Silver", 14, 1),
}
RECIPES = [RDIR + "Alloy_%s.json" % w for w in sorted(ALLOYS)]
ENCH_IN = {"Bronze": ("Copper", "Iron"), "Dusk": ("Thorium", "Lead"), "Azurvane": ("Cobalt", "Chromium"), "Cinder": ("Adamantite", "Slag"),
           "Lumen": ("Mithril", "Titanium"), "Electrum": ("Gold", "Silver")}


def coll_jar():
    """the SkyyCollections jar the build read: --coll <repo-relative jar> or the tools/deploy_set.py SET pin"""
    c = HK.arg("--coll") or os.environ.get("WG75_COLL")      # the env carries it into the phase children
    if c:
        return os.path.normpath(os.path.join(ROOT, c))
    import ast
    t = ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf8").read())
    st = [dict(ast.literal_eval(n.value)) for n in t.body if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "SET" for x in n.targets)][0]
    return os.path.join(ROOT, "SkyyCollections", "SkyyCollections-%s.jar" % st["SkyyCollections"])


def ench_recipes(jar):
    return sorted(n for n in zipfile.ZipFile(jar).namelist() if n.startswith(RDIR + "Alloy_Ench_"))
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~<clinit>", "~m header"], "SkyyWorldGenPlugin": ["~m setup"],
          "WgCfg": ["~m load", "~m reloadAll"], "WgStore": ["~m markCreated"]}      # only the version text (proved in phase V)
BSON = ["Server/Instances/SkyWynn_Proof2/instance.bson", "Server/Instances/SkyWynn_Zones/instance.bson", "Server/Instances/SkyWynn_Zones2/instance.bson"]
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []

if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            w = sorted(["manifest.json", LANG] + BSON + RECIPES + ench_recipes(JAR))
            return self.check(sorted(got) == w, "C: non-class entries changed = manifest.json + server.lang + the 6 alloy recipes + the 3 instance templates (+ %d new Enchanted alloy recipes): %s" % (len(ench_recipes(JAR)), sorted(got)))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def cp_strings(b):
    n = struct.unpack(">H", b[8:10])[0]
    i, k, out = 10, 1, []
    while k < n:
        t = b[i]
        if t == 1:
            L = struct.unpack(">H", b[i + 1:i + 3])[0]
            out.append(b[i + 3:i + 3 + L].decode("utf8", "replace"))
            i += 3 + L
        elif t in (3, 4):
            i += 5
        elif t in (5, 6):
            i += 9
            k += 1
        elif t in (7, 8, 16, 19, 20):
            i += 3
        elif t in (9, 10, 11, 12, 17, 18):
            i += 5
        elif t == 15:
            i += 4
        else:
            raise ValueError("constant tag %d" % t)
        k += 1
    return out


def jread(z, n):
    return json.loads(z.read(n).decode("utf-8-sig"))


def lang_lines(jar):
    t = zipfile.ZipFile(jar).read(LANG).decode("utf8")
    out = []
    for ln in t.splitlines():
        m = re.match(r"([A-Za-z0-9_.]+)\s*=\s?(.*)$", ln)
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def run_ver(out, jar, scratch, _home):
    """V: every changed class string constant and the 3 instance templates differ ONLY by the version 0.7.4 -> 0.7.5"""
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    odd = []
    for cn in sorted(EXPECT):
        n = "com/skyy/worldgen/%s.class" % cn
        sa, sb = set(cp_strings(za.read(n))), set(cp_strings(zb.read(n)))
        V_ = lambda x: x.replace(OLD_VERSION, "@V@").replace(VERSION, "@V@")
        if set(V_(x) for x in sa - sb) != set(V_(x) for x in sb - sa) or not (sa - sb):
            odd.append((cn, sorted(sa - sb)[:2], sorted(sb - sa)[:2]))
    K.eq(odd, [], "V the changed classes differ only in the version text (string constants %s -> %s)" % (OLD_VERSION, VERSION))
    for n in BSON:
        a, b = za.read(n), zb.read(n)
        K.check(a != b and a.replace(OLD_VERSION.encode(), b"@V@") == b.replace(VERSION.encode(), b"@V@").replace(OLD_VERSION.encode(), b"@V@"),
                "V %s = 0.7.4's with only the version changed" % n.split("/")[2])
    K.save()


def run_recipes(out, jar, scratch, _home):
    """R: the per-alloy in / out table"""
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    K.eq(sorted(n for n in zb.namelist() if n.startswith(RDIR) and not n.startswith(RDIR + "Alloy_Ench_")), sorted(RECIPES), "R the jar's plain recipe files = the 6 alloys")
    K.eq(sorted(n for n in za.namelist() if n.startswith(RDIR)), sorted(RECIPES), "R 0.7.4 had the same 6")
    rows = []
    for w in sorted(ALLOYS, key=lambda x: (ALLOYS[x][4], x)):
        oid, a, b, sec, tier = ALLOYS[w]
        n = RDIR + "Alloy_%s.json" % w
        o, r = jread(za, n), jread(zb, n)
        qin = sum(x["Quantity"] for x in r["Input"])
        K.eq([(x["ItemId"], x["Quantity"]) for x in r["Input"]], [(a, 1), (b, 1)], "R %s inputs 1 %s + 1 %s" % (w, a, b))
        K.eq(r["Input"], o["Input"], "R %s inputs identical to 0.7.4" % w)
        K.eq(r["PrimaryOutput"], {"ItemId": oid, "Quantity": qin}, "R %s PrimaryOutput = %d %s (bars out = bars in)" % (w, qin, oid))
        K.eq(r["Output"], [{"ItemId": oid, "Quantity": qin}], "R %s Output = %d %s" % (w, qin, oid))
        K.eq(o["PrimaryOutput"], {"ItemId": oid, "Quantity": 1}, "R %s was 1 bar in 0.7.4" % w)
        K.eq(r["BenchRequirement"], [{"Type": "Processing", "Id": "SkyyAlloy"}], "R %s bench SkyyAlloy" % w)
        K.eq(r["BenchRequirement"], o["BenchRequirement"], "R %s bench identical to 0.7.4" % w)
        K.eq(r["TimeSeconds"], sec, "R %s time %d s" % (w, sec))
        K.eq(r["TimeSeconds"], o["TimeSeconds"], "R %s time identical to 0.7.4" % w)
        o2, r2 = dict(o), dict(r)
        for d in (o2, r2):
            d.pop("PrimaryOutput"); d.pop("Output")
        K.eq(r2, o2, "R %s nothing else in the recipe changed (keys %s)" % (w, sorted(r)))
        rows.append("%-9s 1 %s + 1 %s, %d s, Charm T%d: 0.7.4 -> %d, 0.7.5 -> %d" % (
            w, a.replace("Ingredient_Bar_", "").replace("_SkyWynn", ""), b.replace("Ingredient_Bar_", "").replace("_SkyWynn", ""), sec, tier, o["PrimaryOutput"]["Quantity"], r["PrimaryOutput"]["Quantity"]))
    print("R. per-alloy in / out:")
    for x in rows:
        print("   " + x)
    K.notes.extend(rows)
    K.save()


def run_assets(out, jar, scratch, _home):
    """AS: the jar's assets are valid and every id they name exists"""
    K = HK.Child(out)
    import serverjar as SJ           # the CACHED Assets.zip copy (read-only; never the installed file)
    zb = zipfile.ZipFile(jar)
    names = zb.namelist()
    with zipfile.ZipFile(SJ.assets_zip()) as az:
        van = set(n.rsplit("/", 1)[1][:-5] for n in az.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        vcommon = set(n for n in az.namelist() if n.startswith("Common/"))
    own = set(n.rsplit("/", 1)[1][:-5] for n in names if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    coll = set(n.rsplit("/", 1)[1][:-5] for n in zipfile.ZipFile(coll_jar()).namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    bad_json = []
    for n in names:
        if n.endswith(".json"):
            try:
                jread(zb, n)
            except ValueError as e:
                bad_json.append((n, str(e)[:60]))
    K.eq(bad_json, [], "AS every JSON entry parses (%d)" % len([n for n in names if n.endswith(".json")]))
    miss = []
    for n in RECIPES + ench_recipes(jar):
        r = jread(zb, n)
        for x in r["Input"] + r["Output"] + [r["PrimaryOutput"]]:
            if x["ItemId"] not in van and x["ItemId"] not in own and not (x["ItemId"].startswith("Skyy_Ench_") and x["ItemId"] in coll):
                miss.append((n, x["ItemId"]))
            if not (isinstance(x["Quantity"], int) and x["Quantity"] > 0):
                miss.append((n, "quantity %r" % x["Quantity"]))
    K.eq(miss, [], "AS every alloy input / output is a vanilla, own or SkyyCollections Enchanted item with a positive quantity")
    K.check(not (own & van), "AS no own item id clashes with vanilla: %s" % sorted(own & van))
    tex = []
    for i in sorted(own):
        d = jread(zb, [n for n in names if n.endswith("/%s.json" % i) and n.startswith("Server/Item/Items/")][0])
        for p in ([d.get("Icon")] + ([d["Texture"]] if "Texture" in d else []) +
                  [t["Texture"] for t in (d.get("BlockType") or {}).get("CustomModelTexture", [])]):
            if p and ("Common/" + p) not in names and ("Common/" + p) not in vcommon:
                tex.append((i, p))
    K.eq(tex, [], "AS every own item's Icon / Texture / ore texture is in the jar or in vanilla Assets.zip (Onyxium uses vanilla's)")
    nonascii = [n for n in names if (n.endswith(".json") or n.endswith(".lang")) and any(c > 126 for c in zb.read(n))]
    K.eq(nonascii, [], "AS assets are plain ASCII")
    K.save()


def run_lang(out, jar, scratch, _home):
    K = HK.Child(out)
    a, b = lang_lines(OLD_JAR), lang_lines(jar)
    K.eq([k for k, v in b], [k for k, v in a], "L the same keys in the same order (%d)" % len(a))
    da, db = dict(a), dict(b)
    changed = sorted(k for k in db if da.get(k) != db[k])
    want = sorted("%s%s.description" % (p, ALLOYS[w][0]) for w in ALLOYS if w != "Bronze" for p in ("items.", "server.items."))
    K.eq(changed, want, "L the changed lines = the 5 own alloy descriptions (x the items. / server.items. twins)")
    bad = []
    for k in changed:
        o, n = da[k], db[k]
        m = re.match(r"^(.*Alloy of \w+ \+ \w+)(, smelted .*)$", o)
        if not m or n != m.group(1) + " (1 + 1 makes 2)" + m.group(2):
            bad.append((k, o[:60], n[:60]))
    K.eq(bad, [], "L each changed description = the 0.7.4 text with ' (1 + 1 makes 2)' inserted (tier tag unchanged, first)")
    K.check(all(re.match(r"^T\d+ \w+ - ", db[k]) for k in changed), "L every changed description still starts with its tier tag 'T<n> <Metal> - '")
    K.notes.append("L e.g. %s: '%s'" % (changed[0], db[changed[0]]))
    K.save()


def run_gate(out, jar, scratch, _home):
    """G: the Furnace Charm gate (SkyySacks ProcBench) sees the same bench id and output ids as 0.7.4"""
    K = HK.Child(out)
    zb = zipfile.ZipFile(jar)
    K.check(os.path.isfile(SACKS), "G the SkyySacks SET jar is here: %s" % SACKS)
    zs = zipfile.ZipFile(SACKS)
    pb = [n for n in zs.namelist() if n.endswith("/ProcBench.class")]
    K.eq(len(pb), 1, "G SkyySacks has one ProcBench class")
    s = set(cp_strings(zs.read(pb[0])))
    K.check("SkyyAlloy" in s, "G SkyySacks ProcBench names the bench SkyyAlloy")
    for w in sorted(ALLOYS):
        oid = ALLOYS[w][0]
        r = jread(zb, RDIR + "Alloy_%s.json" % w)
        K.check(r["BenchRequirement"][0]["Id"] == "SkyyAlloy" and r["PrimaryOutput"]["ItemId"] == oid and oid in s,
                "G %s: bench SkyyAlloy, output %s listed in SkyySacks ALLOY_IDS (Furnace Charm T%d)" % (w, oid, ALLOYS[w][4]))
    K.check(not any("RequiredTierLevel" in json.dumps(jread(zb, n)) for n in RECIPES), "G no plain alloy recipe carries its own RequiredTierLevel (the tier comes from SkyySacks' ladder, as 0.7.4)")
    K.check(not any(("Skyy_Ench_" + w) in s for w in ALLOYS), "G SkyySacks' ALLOY_IDS ladder has no Enchanted alloy id (so the Enchanted rows must carry RequiredTierLevel)")
    K.save()


def run_ench(out, jar, scratch, _home):
    """E: the Enchanted alloy smelts (Skyy 2026-10-18): one per Enchanted alloy item the SkyyCollections jar has, each 1 + 1 -> 2"""
    K = HK.Child(out)
    cj = coll_jar()
    K.check(os.path.isfile(cj), "E the SkyyCollections jar is here: %s" % cj)
    cids = set(n.rsplit("/", 1)[1][:-5] for n in zipfile.ZipFile(cj).namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    zb = zipfile.ZipFile(jar)
    want = sorted(RDIR + "Alloy_Ench_%s.json" % w for w in ALLOYS if "Skyy_Ench_" + w in cids)
    K.eq(ench_recipes(jar), want, "E the shipped Enchanted alloy recipes = the Enchanted alloys %s has (%d of 6)" % (os.path.basename(cj), len(want)))
    rows = []
    for w in sorted(ALLOYS, key=lambda x: (ALLOYS[x][4], x)):
        oid, a, b, sec, tier = ALLOYS[w]
        ea, eb, eo = "Skyy_Ench_" + ENCH_IN[w][0], "Skyy_Ench_" + ENCH_IN[w][1], "Skyy_Ench_" + w
        K.check(ea in cids and eb in cids, "E %s: the Enchanted inputs %s + %s exist in %s" % (w, ea, eb, os.path.basename(cj)))
        n = RDIR + "Alloy_Ench_%s.json" % w
        if n not in zb.namelist():
            rows.append("%-9s 1 %s + 1 %s -> 2 %s: NOT SHIPPED (SkyyCollections has no %s)" % (w, ea, eb, eo, eo))
            continue
        r = jread(zb, n)
        K.eq(r, {"Input": [{"ItemId": ea, "Quantity": 1}, {"ItemId": eb, "Quantity": 1}], "PrimaryOutput": {"ItemId": eo, "Quantity": 2},
                 "Output": [{"ItemId": eo, "Quantity": 2}], "BenchRequirement": [{"Type": "Processing", "Id": "SkyyAlloy", "RequiredTierLevel": tier}],
                 "TimeSeconds": sec}, "E %s: 1 %s + 1 %s -> 2 %s, SkyyAlloy, Furnace Charm T%d (RequiredTierLevel), %d s = the plain alloy's" % (w, ea, eb, eo, tier, sec))
        rows.append("%-9s 1 %s + 1 %s -> 2 %s, %d s, Charm T%d: shipped" % (w, ea, eb, eo, sec, tier))
    print("E. Enchanted alloys:")
    for x in rows:
        print("   " + x)
    K.notes.extend(rows)
    K.save()


if __name__ == "__main__":
    if HK.arg("--coll") and "--phase" not in sys.argv:
        os.environ["WG75_COLL"] = HK.arg("--coll")
    HK.run("SkyyWorldGen", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("ver", run_ver), ("recipes", run_recipes), ("assets", run_assets), ("lang", run_lang), ("gate", run_gate), ("ench", run_ench)], __file__)
