"""Harness for SkyyAuctions 0.1.13 (SORT ONLY: the Browse tier sort on the 15-step metal ladder, tools/tier_tags.py TT_VERSION 2;
tools/auctions_0_1_13_patch.py). Build first:
python tools/auctions_0_1_13_patch.py && python SkyyAuctions/build_skyyauctions_0.1.13.py

    python SkyyAuctions/test_skyyauctions_0.1.13.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--bz <SkyyBazaar jar>]

Phases (fresh child JVMs, -Xverify:all):
  A    verify   every class loads + initialises
  C    compare  0.1.12 -> 0.1.13: only AhItem (ttMap = the inlined TT_SPEC, lvTier = the bands) + the version texts differ; non-class: manifest.json
  TT   THE TABLE: AhItem.TT_SPEC of 0.1.13 = tools/tier_tags.py (TT_VERSION 2) ROWS exactly; 0.1.12's = the TT_VERSION 1 table (git 73014c2);
       every id moved by renumber() except exactly the 54 zone-metal / Bronze rows that now sit at their OWN step (named);
       AhItem.lvTier / sortTier (real class) = TT.tier_for_level for every level 0-119 (+ Onyxium ids T16, untiered 99)
  HUB / RB / MK / D (live) the 0.1.12 harness's phases on this jar - unchanged behaviour
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, zipfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

_sp = importlib.util.spec_from_file_location("ah0112test", os.path.join(HERE, "test_skyyauctions_0.1.12.py"))
T12 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T12)
T10, T11, TB, H = T12.T10, T12.T11, T12.TB, T12.H

VERSION = "0.1.13"
OLD_VERSION = "0.1.12"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-%s.jar" % OLD_VERSION)
BZ_JAR = T10.BZ_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "l1", "ah")))
EXPECT = {"AhItem": ["~m ttMap", "~m lvTier"],                               # the re-baked TT_SPEC (inlined into ttMap) + the 15-step bands
          "AhCmds": ["~m status"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the version text
          "SkyyAuctionsPlugin": ["~m setup"]}                               # the ready line
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
TT1_COMMIT = "73014c2"      # the last commit with tools/tier_tags.py TT_VERSION 1 (the table 0.1.12 was built on)


def tt_v1(scratch):
    d = os.path.join(scratch, "tt1")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "tier_tags_v1.py")
    open(p, "wb").write(subprocess.check_output(["git", "show", TT1_COMMIT + ":tools/tier_tags.py"], cwd=ROOT))
    sp = importlib.util.spec_from_file_location("tier_tags_v1", p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    assert m.TT_VERSION == "1", m.TT_VERSION
    return m


def spec_in(jar, cls):
    """the 'id:tier|id:tier|...' constant of a class"""
    hit = [s for s in T12.cp_strings(zipfile.ZipFile(jar).read(cls)) if re.fullmatch(r"(?:[A-Za-z0-9_]+:\d+\|)+[A-Za-z0-9_]+:\d+", s)]
    assert len(hit) == 1, (cls, len(hit))
    return dict((a, int(b)) for a, b in (x.split(":") for x in hit[0].split("|")))


def table_proof(K, new_spec, old_spec, T1, tag):
    """new = TT_VERSION 2 ROWS exactly; old = rows of the TT_VERSION 1 table (git 73014c2; an older jar may lack rows added later - named);
    every common row moved by renumber() except the rows that now sit at their OWN word's step (zone metals, mining armor, Bronze - named)"""
    K.eq(new_spec, dict((i, TT.tier(i)) for i in TT.ROWS), "%s the new jar's table = tools/tier_tags.py TT_VERSION 2 (%d rows)" % (tag, len(TT.ROWS)))
    K.eq(dict((i, t) for i, t in old_spec.items() if T1.tier(i) != t), {}, "%s the old jar's rows = TT_VERSION 1 (git %s)" % (tag, TT1_COMMIT))
    K.eq(sorted(set(old_spec) - set(new_spec)), [], "%s no row dropped" % tag)
    added = sorted(set(new_spec) - set(old_spec))
    K.check(all(i in T1.ROWS for i in added), "%s the rows the old jar lacks were added to the TT_VERSION 1 table after its build" % tag)
    own = sorted(i for i in old_spec if new_spec[i] != TT.renumber(old_spec[i]))
    OWN = set(i for i in TT.ROWS if i in TT.WG_IDS or i == "Ingredient_Bar_Bronze" or i.startswith("Armor_Mining_")
              or i in ("Skyy_Ench_Lead", "Skyy_Ench_Chromium", "Skyy_Ench_Slag", "Skyy_Ench_Titanium"))
    K.eq(own, sorted(OWN & set(old_spec)), "%s the rows NOT moved by renumber() = the zone metals / their Enchanted ingots / mining armor + Bronze" % tag)
    STEP = lambda w: TT.metal_tier("Bronze") if w == "Electrum" else TT.metal_tier(w)     # Electrum (Gold + Silver) sits at the Bronze step (spec 8)
    K.check(all(new_spec[i] == STEP(TT.word(i)) for i in OWN), "%s each of those sits at its OWN word's ladder step (%d rows; Electrum at Bronze's T3)" % (tag, len(OWN)))
    K.notes.append("%s %d rows (%d the old jar lacked: %s): %d renumbered as renumber(), %d at their own step (%s), %d unchanged" % (
        tag, len(new_spec), len(added), ", ".join(added[:4]) + (" ..." if len(added) > 4 else ""),
        sum(1 for i in old_spec if i not in own and new_spec[i] != old_spec[i]), len(own),
        ", ".join("%s %d->%d" % (i, old_spec[i], new_spec[i]) for i in own[:3]) + (" ..." if len(own) > 3 else ""),
        sum(1 for i in old_spec if new_spec[i] == old_spec[i])))


def run_tier(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    T1 = tt_v1(scratch)
    table_proof(K, spec_in(jar, "com/skyy/auctions/AhItem.class"), spec_in(OLD_JAR, "com/skyy/auctions/AhItem.class"), T1, "TT")
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    I = JClass(PKG + "AhItem")
    bad = [(l, x) for l in range(0, 120) for x in ("Weapon_Sword_Iron", "Armor_Onyxium_Chest", "Weapon_Sword_Lumen_SkyWynn", "Armor_Copper_Head")
           if int(I.lvTier(x, l)) != TT.tier_for_level(l, x)]
    K.eq(bad, [], "TT AhItem.lvTier = tools/tier_tags.py tier_for_level for every level 0-119")
    K.eq([int(I.sortTier(x, l)) for x, l in (("Ore_Thorium", -1), ("Ingredient_Bar_Lumen_SkyWynn", -1), ("Weapon_Sword_Iron", 16), ("Weapon_Sword_Iron", 50),
                                              ("Armor_Onyxium_Chest", 5), ("Skyy_No_Such_Thing", -1), ("Ore_Copper", 99))],
         [4, 15, 2, 15, 16, 99, 1], "TT AhItem.sortTier: table rows, level bands, Onyxium, untiered last")
    K.save()


if __name__ == "__main__":
    ph = [("tier", run_tier), ("hub", T10.run_hub), ("rb", T11.run_rb)]
    if os.path.isfile(BZ_JAR):
        ph.append(("mk", lambda out, jar, scratch, home: TB.run_mk(out, BZ_JAR, jar, scratch)))
    ph.append(("live", lambda out, jar, scratch, home: H.run_live(T10.S, out, jar, scratch, home)))
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=ph, script=__file__, live=(T10.LIVE, "Skyy_SkyyAuctions"))
