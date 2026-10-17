"""Harness for SkyyAccessories 0.5.24 (TEXT ONLY: Void Charms everywhere players / admins read it; tools/accessories_0_5_24_patch.py).
Build first: python tools/accessories_0_5_24_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.24.py

    python SkyyAccessories/test_skyyaccessories_0.5.24.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.23 -> 0.5.24: only the text-carrying methods / constants change; non-class: manifest only
  0.5.22's phases on the new jar (test_skyyaccessories_0.5.22.py loaded with RENAMED: its two expected craft lines say "Void Charms"
  instead of "bag" - every other check unchanged): assets, power, retire, rows, page, live; 0.5.23's client-model phase (G)
  V    THE RENAME: the kit publishes the Server Setup title "Void Charms" (CfgRows / CfgData TITLE, config:def row) with the same MOD,
       NODE, category keys and row keys as 0.5.23 (no key / id / file changed); every row label / help / category, the three new-file
       headers, the chat / page texts (class constant pools) name no "Accessory Bag", no "the bag" / "bag page" / "bag slot" and no
       "Server Setup -> Accessories"; the lang file is byte-identical to 0.5.23 (item names unchanged)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, zipfile, struct, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_STRICT_COMPARE = HK.run_compare
# the 0.5.22 harness with its two craft-line expectations renamed (each must occur: a missing one = the old harness changed)
RENAMED = [('"upgraded to Unique Brawler Accessory in your bag - your Normal Brawler Accessory was used for it"',
            '"upgraded to Unique Brawler Accessory in your Void Charms - your Normal Brawler Accessory was used for it"'),
           ('"crafted Workbench I - it went straight into your bag"', '"crafted Workbench I - it went straight into your Void Charms"')]
_src22 = open(os.path.join(HERE, "test_skyyaccessories_0.5.22.py"), encoding="utf8").read()
for _o, _n in RENAMED:
    assert _src22.count(_o) == 1, "the 0.5.22 harness changed: %s" % _o
    _src22 = _src22.replace(_o, _n)
T22 = type(sys)("acc_h522r")
T22.__file__ = os.path.join(HERE, "test_skyyaccessories_0.5.22.py")
exec(compile(_src22, T22.__file__, "exec"), T22.__dict__)
_sp = importlib.util.spec_from_file_location("acc_h523", os.path.join(HERE, "test_skyyaccessories_0.5.23.py"))
T23 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T23)
HK.run_compare = _STRICT_COMPARE          # 0.5.24 changes no asset: the non-class entries may differ in manifest.json only

VERSION = "0.5.24"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.23.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "acc0524", "acc")))
PKG = T22.PKG
EXPECT = {
    "AccCfg": ["~m load", "~m writeDefaults"],                       # the reload summary, CONFIG_TEXT (new-file header + craft comments)
    "AccCraft": ["~m autoOne", "~m autoRun", "~m craft", "~m why"],   # the craft / upgrade / refusal lines
    "AccDefs": ["~m bonusText", "~m retiredWhy"],                     # the empty Bonuses line, the retired Night Vision line
    "AccPage": ["~m handleDataEvent"],                                # the profile-switch line
    "AccPower": ["~m load"], "AccSnd": ["~m load"],                   # the new-file headers
    "CfgRows": ["~<clinit>", "~m header"],                            # TITLE, row labels / helps, the version text
    "CfgFn": ["~m opExport"], "SkyyAccessoriesPlugin": ["~m setup"],  # the version text, the ready log line
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
BAD = [re.compile(p, re.I) for p in (r"accessory bag", r"\bthe bag\b", r"\bbag page\b", r"\bbag slot", r"\byour bag\b", r"\bthis bag\b",
                                     r"\bor bag\b", r"server setup -> accessories", r"\baccessory (slots|equipped|upgraded)\b")]
# texts that keep the old word on purpose (they name the retired ITEM, or are server-log / save-file / migration lines nobody reads in game)
KEEP_RE = re.compile(r"Old Accessory Bag|old Accessory Bag item|the old bag item|^# Accessory bag slots every player can fill, 1-9|"
                     r"^# Accessory bag slots every player can fill, 1-60|ITEM LOST|bag craft|inventory and bag full|the bag slot changed|"
                     r"-> bag|into the bag, |^bag \(upgraded|SkyyAccessories bag|bag file|save bag|starter bag|bag item|live in bags/|"
                     r"Accessories & Bags|^# Line switches: false = the line stays in the bag")


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


def run_rename(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)   # each jar in its own loader (the system loader has neither)
    Ln = T22.loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=Ln)
    R = J("CfgRows")
    K.eq(str(R.TITLE), "Void Charms", "V the Server Setup title is Void Charms")
    K.eq((str(R.MOD), str(R.NODE)), ("SkyyAccessories", "skyyaccessories.admin"), "V the same MOD and admin node")
    z_new, z_old = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    # rows / categories: keys unchanged (the 0.5.23 jar in its own class loader), texts renamed
    Ro = JClass(PKG + "CfgRows", loader=T22.loader_for(OLD_JAR))
    arr = lambda c, f: [str(x) for x in getattr(c, f)]
    for f_ in ("KEYS", "CATS", "TYPES", "DEFS", "MINS", "MAXS", "FLAGS", "CAT_IDS", "FILES", "BCLS", "BNAME", "BFK"):
        K.eq(arr(R, f_), arr(Ro, f_), "V CfgRows.%s unchanged (%d)" % (f_, len(arr(R, f_))))
    K.eq((str(Ro.TITLE), str(Ro.NODE)), ("Accessories", str(R.NODE)), "V (0.5.23 was titled Accessories)")
    K.check(z_new.read("Server/Languages/en-US/server.lang") == z_old.read("Server/Languages/en-US/server.lang"), "V the lang file is unchanged (item names)")
    nonclass = lambda z: sorted(n for n in z.namelist() if not n.endswith(".class") and n != "manifest.json")
    K.check(nonclass(z_new) == nonclass(z_old) and all(z_new.read(n) == z_old.read(n) for n in nonclass(z_new)),
            "V every asset is byte-identical to 0.5.23 (ids, items, recipes)")
    K.check(sorted(n for n in z_new.namelist() if n.endswith(".class")) == sorted(n for n in z_old.namelist() if n.endswith(".class")),
            "V the same classes")
    hits = []
    for n in z_new.namelist():
        if not n.endswith(".class"):
            continue
        for s in cp_strings(z_new.read(n)):
            for ln in s.split("\n"):
                if any(p.search(ln) for p in BAD) and not KEEP_RE.search(ln):
                    hits.append("%s: %s" % (n.rsplit("/", 1)[-1], ln[:120]))
    K.check(not hits, "V no class text still says Accessory Bag / the bag / bag page / bag slot / Server Setup -> Accessories (%d): %s" % (len(hits), hits[:6]))
    # the published texts, live: the kit's config:def answer and the rows
    labels, helps, cats = arr(R, "LABELS"), arr(R, "HELPS"), arr(R, "CAT_LABELS")
    K.check(labels and helps and cats == ["Void Charms", "Accessory Power", "Boosters", "Lantern", "Sounds"], "V categories %s" % cats)
    for want in ("Charm slots", "Craft in Void Charms", "Charm equipped sound", "Charm upgraded sound id", "Accessory Power on"):
        K.check(want in labels, "V row label %r" % want)
    bad_rows = [t for t in labels + helps + cats if any(p.search(t) for p in BAD)]
    K.check(not bad_rows, "V no row label / help / category says the old name: %s" % bad_rows[:4])
    for f_, cls_ in (("DEFAULT_TEXT", "AccSnd"),):
        t = str(getattr(J(cls_), f_))
        K.check("Server Setup -> Void Charms -> Sounds" in t and "# Charm equipped: A charm went into a free Void Charms slot." in t,
                "V %s.%s: the new sounds file header" % (cls_, f_))
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[], removed=[],
           phases=[("assets", T22.run_assets), ("power", T22.run_power), ("retire", T22.run_retire), ("rows", T22.run_rows),
                   ("page", T22.run_page), ("client", T23.run_client), ("rename", run_rename), ("live", T22.run_live)],
           script=__file__, live=(T22.LIVE_DIR, "Skyy_SkyyAccessories"))
