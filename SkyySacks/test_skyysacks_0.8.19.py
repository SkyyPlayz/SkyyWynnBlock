"""Harness for SkyySacks 0.8.19 (TEXT ONLY: the charm bag is called Void Charms in every player / admin text; tools/sacks_0_8_19_patch.py).
Build first:
    python tools/sacks_0_8_19_patch.py && python SkyySacks/build_skyysacks_0.8.19.py

    python SkyySacks/test_skyysacks_0.8.19.py [--keep] [--dir <folder inside tools/dev/scratch/>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.8.18 -> 0.8.19: only the text-carrying methods change; non-class entries: manifest.json only
  V    THE RENAME, read from the class constant pools of both jars: every string constant that changed is EXACTLY a planned old -> new
       text (PAIRS) or the version - nothing else; every pair was used; no class text still names the "Accessory Bag" / "accessory bag"
  SUP / TG / KEYS / D (live) the 0.8.18 harness's phases on this jar - unchanged behaviour
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, zipfile, struct, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_orig_compare = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_18", os.path.join(HERE, "test_skyysacks_0.8.18.py"))
T18 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T18)
sys.argv = _argv
HK.run_compare = _orig_compare

VERSION = "0.8.19"
OLD_VERSION = "0.8.18"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "vcrename", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the version text
    "AccLink": ["~m benchPre", "~m pull"], "AccSettle": ["~m run"],   # the bench line + the two bench WARN lines
    "CraftPage": ["~m buildProc", "~m craftOne", "~m renderPage"],      # the /craft texts
    "SackBridge": ["~m craftWhy"],                                      # "needs its bench accessory in your Void Charms"
    "SkyySacksPlugin": ["~m setup"],   # the ready line
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
# the text fragments as they sit in the constant pools (javassist keeps each literal of a + chain as its own constant)
PAIRS = [("out of your Accessory Bag.", "out of your Void Charms."),
         (" accessory in your accessory bag to queue more.", " accessory in your Void Charms to queue more."),
         ("the Void and your Accessory Bag - sorted by tier.", "the Void and your Void Charms - sorted by tier."),
         ("equip the Campfire accessory in your accessory bag to cook here", "equip the Campfire accessory in your Void Charms to cook here"),
         ("your Accessory Bag changed - nothing was used", "your Void Charms changed - nothing was used"),
         (" from your Accessory Bag)", " from your Void Charms)"),
         ("needs its bench accessory in your accessory bag", "needs its bench accessory in your Void Charms"),
         (" could not go back into the Accessory Bag of ", " could not go back into the Void Charms of "),
         ("back into the Accessory Bag failed: ", "back into Void Charms failed: "),
         ("benches + /craft use the Accessory Bag (", "benches + /craft use Void Charms (")]
BAD = re.compile(r"accessory bag", re.I)


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
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("rename", run_rename), ("sup", T18.run_sup), ("tg", T18.T16.run_tg), ("keys", T18.T17.run_keys), ("live", T18.T0810.run_live10)],
           __file__, live=(T18.T16.T15.BETA, "Skyy_SkyySacks"))
