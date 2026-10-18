"""Harness for SkyyWorldGen 0.7.4 (round L1: the zone metals' tier tags on the 15-step ladder, tools/tier_tags.py TT_VERSION 2;
tools/worldgen_0_7_4_patch.py). Build first:
    python tools/worldgen_0_7_4_patch.py && python SkyyWorldGen/build_skyyworldgen_0.7.4.py

    python SkyyWorldGen/test_skyyworldgen_0.7.4.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.7.3 -> 0.7.4: only the version texts differ (EXPECT); non-class entries: manifest.json + Server/Languages/en-US/server.lang
               (every item JSON, recipe, texture and icon byte-identical)
  V    version  the five changed classes differ only in their version string constants; the 3 instance templates only in the version
  L    lang     server.lang 0.7.3 -> 0.7.4: the same keys in the same order; the ONLY changed lines are the descriptions of the 16 zone
               metals whose tag moved (Electrum stays T3) - each one differs only in its leading "T<n>" (0.7.3 = the TT_VERSION 1 number of
               git 73014c2, 0.7.4 = tools/tier_tags.py TT_VERSION 2 = its own ladder step); names untouched
  AA   audit    the engine-access audit
The 0.7.3 harness (SkyyWorldGen/test_skyyworldgen_0.7.3.py) covers the generator; C proves its code is unchanged. Exit code 1 on any failure.
"""
import os, sys, re, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import tier_tags as TT

_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("ah0113test", os.path.join(ROOT, "SkyyAuctions", "test_skyyauctions_0.1.13.py"))
AH13 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(AH13)       # its tt_v1 (TT_VERSION 1 from git 73014c2)
sys.argv = _argv

VERSION = "0.7.4"
OLD_VERSION = "0.7.3"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyWorldGen-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyWorldGen-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "l1", "wg")))
PKG = "com.skyy.worldgen."
LANG = "Server/Languages/en-US/server.lang"
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
            return self.check(sorted(got) == sorted(["manifest.json", LANG] + BSON), "C: non-class entries changed = manifest.json + server.lang + the 3 instance templates (version only, phase V): %s" % sorted(got))
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq


def lang_lines(jar):
    t = zipfile.ZipFile(jar).read(LANG).decode("utf8")
    out = []
    for ln in t.splitlines():
        m = re.match(r"([A-Za-z0-9_.]+)\s*=\s?(.*)$", ln)
        if m:
            out.append((m.group(1), m.group(2)))
    return out


def run_lang(out, jar, scratch, _home):
    K = HK.Child(out)
    T1 = AH13.tt_v1(scratch)
    a, b = lang_lines(OLD_JAR), lang_lines(jar)
    K.eq([k for k, v in b], [k for k, v in a], "L the same keys in the same order (%d)" % len(a))
    da, db = dict(a), dict(b)
    changed = sorted(k for k in db if da.get(k) != db[k])
    ids = sorted(set(k.split(".")[-2] for k in changed))
    want_ids = sorted(i for i in TT.ids_for("SkyyWorldGen") if T1.tag_for(i) != TT.tag_for(i))
    K.eq(ids, want_ids, "L the changed lines belong to exactly the zone metals whose tag moved (%d of %d)" % (len(want_ids), len(TT.ids_for("SkyyWorldGen"))))
    K.eq(sorted(i for i in TT.ids_for("SkyyWorldGen") if i not in want_ids), ["Ingredient_Bar_Electrum_SkyWynn"], "L Electrum keeps its tag (T3)")
    K.check(all(k.endswith(".description") for k in changed), "L only descriptions changed (%d lines): %s" % (len(changed), [k for k in changed if not k.endswith(".description")][:3]))
    bad = []
    for k in changed:
        i = k.split(".")[-2]
        o, n = da[k], db[k]
        if not (o.startswith(T1.tag_for(i) + TT.SEP) and n.startswith(TT.tag_for(i) + TT.SEP) and o[len(T1.tag_for(i)):] == n[len(TT.tag_for(i)):]):
            bad.append((k, o[:40], n[:40]))
    K.eq(bad, [], "L each changed description differs ONLY in its leading tag (old TT_VERSION 1 tag -> TT_VERSION 2 tag)")
    K.eq(sorted(set(TT.tag_for(i) for i in want_ids)), sorted(["T5 Lead", "T6 Dusk", "T8 Chromium", "T9 Azurvane", "T11 Slag", "T12 Cinder", "T14 Titanium", "T15 Lumen"]),
         "L the new tags")
    K.check(all(db[k].startswith(TT.tag_for(k.split(".")[-2]) + TT.SEP) for k in db if k.endswith(".description") and k.split(".")[-2] in TT.ROWS),
            "L every zone metal description starts with its TT_VERSION 2 tag")
    K.notes.append("L %d lines changed (%d ids x the items. / server.items. twins), e.g. %s: '%s' -> '%s'" % (
        len(changed), len(ids), changed[0], da[changed[0]][:24], db[changed[0]][:24]))
    K.save()


def run_ver(out, jar, scratch, _home):
    """V: every changed class string constant and the 3 instance templates differ ONLY by the version 0.7.3 -> 0.7.4"""
    K = HK.Child(out)
    za, zb = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(jar)
    odd = []
    for cn in sorted(EXPECT):
        n = "com/skyy/worldgen/%s.class" % cn
        sa, sb = set(AH13.T12.cp_strings(za.read(n))), set(AH13.T12.cp_strings(zb.read(n)))
        V_ = lambda x: x.replace(OLD_VERSION, "@V@").replace(VERSION, "@V@")      # a version token either way (the file header names 0.7.4, "new in 0.7.3" stays)
        if set(V_(x) for x in sa - sb) != set(V_(x) for x in sb - sa) or not (sa - sb):
            odd.append((cn, sorted(sa - sb)[:2], sorted(sb - sa)[:2]))
    K.eq(odd, [], "V the changed classes differ only in the version text (string constants %s -> %s)" % (OLD_VERSION, VERSION))
    for n in BSON:
        a, b = za.read(n), zb.read(n)
        K.check(a != b and a.replace(OLD_VERSION.encode(), b"@V@") == b.replace(VERSION.encode(), b"@V@").replace(OLD_VERSION.encode(), b"@V@"), "V %s = 0.7.3's with only the version changed" % n.split("/")[2])
    K.save()


if __name__ == "__main__":
    HK.run("SkyyWorldGen", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("ver", run_ver), ("lang", run_lang)], __file__)
