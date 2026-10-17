"""Harness for SkyyAuctions 0.1.12 (TEXT ONLY: the retired bag item is named the Old Accessory Bag in every player / admin text;
tools/auctions_0_1_12_patch.py). Build first:
python tools/auctions_0_1_12_patch.py && python SkyyAuctions/build_skyyauctions_0.1.12.py

    python SkyyAuctions/test_skyyauctions_0.1.12.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--bz <SkyyBazaar jar>]

Phases (fresh child JVMs, -Xverify:all):
  A    verify   every class loads + initialises
  C    compare  0.1.11 -> 0.1.12: only the text-carrying members differ; non-class entries: manifest.json only
  V    THE RENAME, read from the class constant pools of both jars: every string constant that changed is EXACTLY a planned old -> new
       text (PAIRS) or the version - nothing else; every pair used; no class text still says "the Accessory Bag" / "+ Accessory Bag"
  HUB / RB / MK / D (live) the 0.1.11 harness's phases on this jar - unchanged behaviour
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, zipfile, struct, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_sp = importlib.util.spec_from_file_location("ah0111test", os.path.join(HERE, "test_skyyauctions_0.1.11.py"))
T11 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T11)
T10, TB, H = T11.T10, T11.TB, T11.H

VERSION = "0.1.12"
OLD_VERSION = "0.1.11"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-%s.jar" % OLD_VERSION)
BZ_JAR = T10.BZ_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "vcrename", "ah")))
EXPECT = {   # javassist inlines the static final texts (BAG_REASON, BAGS_NOTE, the blocked.txt lines) into every method that uses them
    "AhCfg": ["~m applyBuiltin", "~m load", "~m loadBlocked", "~m migrate", "~m setPaused"],
    "AhCmds": ["~m reload", "~m status"], "AhItem": ["~m blockedReason"], "AhPage": ["~m renderCreate"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAuctionsPlugin": ["~m setup"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
PAIRS = [("Magic Bags and the Accessory Bag open their owner's own storage", "Magic Bags and the Old Accessory Bag open their owner's own storage"),
         ("Magic Bags + Accessory Bag ", "Magic Bags + Old Accessory Bag "),
         ("and the Accessory Bag cannot be listed or bought", "and the Old Accessory Bag cannot be listed or bought"),
         ("and the Accessory Bag are blocked built in", "and the Old Accessory Bag are blocked built in")]
BAD = re.compile(r"(the|\+) Accessory Bag")


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


def text_diff(K, jar, old_jar, pairs, old_v, new_v, bad, keep=None):
    """every changed string constant = a planned pair or the version; every pair used; no BAD text left (KEEP excepted)"""
    za, zb = zipfile.ZipFile(old_jar), zipfile.ZipFile(jar)
    used, odd = set(), []
    names = sorted(n for n in zb.namelist() if n.endswith(".class"))
    K.eq(names, sorted(n for n in za.namelist() if n.endswith(".class")), "V the same classes")
    for n in names:
        sa, sb = set(cp_strings(za.read(n))), set(cp_strings(zb.read(n)))
        gone, new = sa - sb, sb - sa
        mapped = set()
        for s in gone:
            t = s
            for i, (o, w) in enumerate(pairs):
                if o in t:
                    used.add(i)
                    t = t.replace(o, w)
            mapped.add(t.replace(old_v, new_v))
        if mapped != new:
            odd.append("%s: -%s +%s" % (n.rsplit("/", 1)[-1], sorted(mapped - new)[:2], sorted(new - mapped)[:2]))
    K.check(not odd, "V every changed class text is a planned rename or the version (%d odd): %s" % (len(odd), odd[:4]))
    K.eq(sorted(set(range(len(pairs))) - used), [], "V every planned text pair was found in the old jar")
    hits = []
    for n in names:
        for s in cp_strings(zb.read(n)):
            for ln in s.split("\n"):
                if bad.search(ln) and not (keep and keep.search(ln)):
                    hits.append("%s: %s" % (n.rsplit("/", 1)[-1], ln[:120]))
    K.check(not hits, "V no class text still says the old name (%d): %s" % (len(hits), hits[:6]))
    return used


def run_rename(out, jar, scratch, _home):
    K = HK.Child(out)
    text_diff(K, jar, OLD_JAR, PAIRS, OLD_VERSION, VERSION, BAD)
    K.save()


if __name__ == "__main__":
    ph = [("rename", run_rename), ("hub", T10.run_hub), ("rb", T11.run_rb)]
    if os.path.isfile(BZ_JAR):
        ph.append(("mk", lambda out, jar, scratch, home: TB.run_mk(out, BZ_JAR, jar, scratch)))
    ph.append(("live", lambda out, jar, scratch, home: H.run_live(T10.S, out, jar, scratch, home)))
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=ph, script=__file__, live=(T10.LIVE, "Skyy_SkyyAuctions"))
