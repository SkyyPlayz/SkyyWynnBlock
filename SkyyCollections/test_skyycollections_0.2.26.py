"""Harness for SkyyCollections 0.2.26 (round L1: the tier tags + the recipe tier sort on the 15-step metal ladder, tools/tier_tags.py
TT_VERSION 2; tools/collections_0_2_26_patch.py). Build first:
    python tools/collections_0_2_26_patch.py && python SkyyCollections/build_skyycollections_0.2.26.py

    python SkyyCollections/test_skyycollections_0.2.26.py [--jar <SkyyCollections-0.2.26.jar>] [--dir <scratch>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.2.25 -> 0.2.26: only CollTier (the re-baked table, LADDER_N) + the version texts differ; non-class entries: manifest.json + server.lang
  L    lang     server.lang 0.2.25 -> 0.2.26: the same keys in the same order; the ONLY changed lines are the descriptions of the ids whose tag
                tools/tier_tags.py changed (TT_VERSION 1 of git 73014c2 -> TT_VERSION 2) - 130 of the 150 tagged ids, each line differing ONLY
                in its leading tag ("T2 Copper - " -> "T1 Copper - "; Bronze "T3 Iron" -> "T3 Bronze"; the Lettuce probe's "\\n" form too);
                names and every other line untouched; the 20 ids whose tag stays (T4 Thorium, T3 Bronze-tier crops ...) unchanged
  TT   table    CollTier of both jars (real classes, -Xverify:all): 0.2.26 TT_IDS / TT_TIER / METAL_W / METAL_T = TT_VERSION 2; 0.2.25's =
                TT_VERSION 1; every row moved by renumber() except the 54 rows at their OWN step (zone metals, their Enchanted ingots, mining
                armor, Bronze); the crop groups unchanged; tierKey / tierText on the new ladder
  X    exec     the 0.2.25 harness's exec phase on this jar (registry, rewards, merge) - unchanged behaviour
  AA   audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "ci"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("ah0113test", os.path.join(ROOT, "SkyyAuctions", "test_skyyauctions_0.1.13.py"))
AH13 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(AH13)       # its tt_v1 (TT_VERSION 1 from git 73014c2) + table_proof
sys.argv = _argv
_eq_orig = HK.Child.eq
_sp = importlib.util.spec_from_file_location("coll0225test", os.path.join(HERE, "test_skyycollections_0.2.25.py"))
T25 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T25)
sys.argv = _argv
HK.Child.eq = _eq_orig             # 0.2.25's compare-phase hook is replaced by this file's own below

VERSION = "0.2.26"
OLD_VERSION = "0.2.25"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "l1", "coll")))
PKG = "com.skyy.collections."
LANG = "Server/Languages/en-US/server.lang"
EXPECT = {"CollTier": ["~<clinit>", "~m tierText"],      # the re-baked tier table (TT_TIER) + LADDER_N 16 (a constant javassist inlines)
          "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the kit's version texts
          "SkyyCollectionsPlugin": ["~m setup"]}          # the ready line names 0.2.26
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []

if HK.arg("--phase") == "compare":
    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            return self.check(sorted(got) == sorted(["manifest.json", LANG]), "C: non-class entries changed = manifest.json + server.lang: %s" % sorted(got))
        return _eq_orig(self, got, want, what)
    HK.Child.eq = _eq


def lang_pairs(jar):
    return [tuple(l.split("=", 1)) for l in zipfile.ZipFile(jar).read(LANG).decode("utf-8").split("\n") if "=" in l]


def run_lang(out, jar, scratch, _home):
    K = HK.Child(out)
    T1 = AH13.tt_v1(scratch)
    a, b = lang_pairs(OLD_JAR), lang_pairs(jar)
    K.eq([k for k, v in b], [k for k, v in a], "L the same keys in the same order (%d)" % len(a))
    da, db = dict(a), dict(b)
    changed = sorted(k for k in db if da.get(k) != db[k])
    ids = sorted(set(k.split(".")[-2] for k in changed))
    mine = TT.ids_for("SkyyCollections")
    want_ids = sorted(i for i in mine if T1.tag_for(i) != TT.tag_for(i))
    K.eq(len(mine), 150, "L 150 tagged ids (tools/tier_tags.py, owner SkyyCollections)")
    K.eq(ids, want_ids, "L the changed lines belong to exactly the ids whose tag changed (%d of %d)" % (len(want_ids), len(mine)))
    K.check(len(want_ids) == 130, "L 130 ids change their tag (%d)" % len(want_ids))
    K.check(all(k.endswith(".description") for k in changed), "L only descriptions changed: %s" % [k for k in changed if not k.endswith(".description")][:3])
    bad = []
    for k in changed:
        i = k.split(".")[-2]
        o, n, to, tn = da[k], db[k], T1.tag_for(i), TT.tag_for(i)
        if not (o.startswith(to) and n.startswith(tn) and o[len(to):] == n[len(tn):] and (o[len(to):] == "" or o[len(to):].startswith(TT.SEP) or o[len(to):].startswith("\\n"))):
            bad.append((k, o[:40], n[:40]))
    K.eq(bad, [], "L each changed description differs ONLY in its leading tag (TT_VERSION 1 tag -> TT_VERSION 2 tag)")
    K.check(all(db["server.items.%s.description" % i].startswith(TT.tag_for(i)) for i in mine if "server.items.%s.description" % i in db),
            "L every tagged description starts with its TT_VERSION 2 tag")
    ex = [("Ingredient_Bar_Copper", "T2 Copper", "T1 Copper"), ("Ore_Iron", "T3 Iron", "T2 Iron"), ("Ingredient_Bar_Bronze", "T3 Iron", "T3 Bronze"),
          ("Skyy_Ench_Cobalt", "T5 Cobalt", "T7 Cobalt"), ("Skyy_Ench_Lead", "T4 Lead", "T5 Lead"), ("Ore_Onyxium", "T8 Onyxium", "T16 Onyxium")]
    K.eq([(i, da["server.items.%s.description" % i][:len(o)], db["server.items.%s.description" % i][:len(n)]) for i, o, n in ex], ex, "L sample tags old -> new")
    K.check(db["server.items.Ore_Thorium.description"] == da["server.items.Ore_Thorium.description"], "L Thorium keeps T4 (unchanged line)")
    K.notes.append("L %d lines changed (%d ids), %d tagged ids unchanged: %s" % (len(changed), len(ids), len(mine) - len(want_ids),
                                                                              ", ".join(i for i in mine if i not in want_ids)))
    K.save()


def run_tier(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    T1 = AH13.tt_v1(scratch)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    File = JClass("java.io.File")
    ld = JClass("java.net.URLClassLoader")([File(OLD_JAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()], None)
    Cn = JClass(PKG + "CollTier")
    Co = JClass("java.lang.Class").forName(PKG + "CollTier", True, ld)
    K.check(str(Co.getProtectionDomain().getCodeSource().getLocation()).endswith("SkyyCollections-%s.jar" % OLD_VERSION), "TT the 0.2.25 CollTier from its own jar")
    old = lambda f: [x for x in Co.getField(f).get(None)]
    new = lambda f: [x for x in getattr(Cn, f)]
    n_ids, o_ids = [str(x) for x in new("TT_IDS")], [str(x) for x in old("TT_IDS")]
    AH13.table_proof(K, dict(zip(n_ids, [int(x) for x in new("TT_TIER")])), dict(zip(o_ids, [int(x) for x in old("TT_TIER")])), T1, "TT")
    K.eq(list(zip([str(x) for x in new("METAL_W")], [int(x) for x in new("METAL_T")])), [tuple(t) for t in TT.TOOL_METALS], "TT METAL_W / METAL_T = TT.TOOL_METALS")
    K.eq(int(Cn.LADDER_N), 16, "TT LADDER_N = 16")
    _ng = dict(zip(n_ids, zip([str(x) for x in new("TT_GRP")], [int(x) for x in new("TT_RANK")])))
    K.eq([(i, _ng[i]) for i in o_ids], list(zip(o_ids, zip([str(x) for x in old("TT_GRP")], [int(x) for x in old("TT_RANK")]))), "TT the crop groups / ranks of the 0.2.25 rows unchanged")
    K.check(all(_ng[i] == ("", 9) for i in n_ids if i not in o_ids), "TT the rows 0.2.25 lacked (SkyyGear 0.3.21's mining armor) are no crop family")
    cases = [("Ore_Copper", "T1"), ("Tool_Pickaxe_Wood", "T1"), ("Ingredient_Bar_Thorium", "T4"), ("Ore_Lead_SkyWynn", "T5"), ("Weapon_Sword_Cobalt", "T7"),
             ("Ingredient_Bar_Lumen_SkyWynn", "T15"), ("Weapon_Sword_Onyxium", "T16"), ("Skyy_Acc_Test_T3", "T3"), ("Rock_Stone", "")]
    K.eq([str(Cn.tierText(i)) for i, w in cases], [w for i, w in cases], "TT CollTier.tierText on the new ladder")
    srt = ["Ore_Lead_SkyWynn", "Ore_Mithril", "Ore_Thorium", "Ingredient_Bar_Dusk_SkyWynn", "Ore_Copper", "Ore_Iron", "Ingredient_Bar_Bronze", "Rock_Stone"]
    K.eq(sorted(srt, key=lambda i: (int(Cn.tierKey(i)), i)), ["Rock_Stone", "Ore_Copper", "Ore_Iron", "Ingredient_Bar_Bronze", "Ore_Thorium", "Ore_Lead_SkyWynn",
                                                               "Ingredient_Bar_Dusk_SkyWynn", "Ore_Mithril"], "TT CollTier.tierKey sorts on the 15-step ladder")
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("lang", run_lang), ("tier", run_tier), ("exec", T25.run_exec)], __file__)
