"""Harness for SkyyMenu 0.3.27 (the Shards tile goes - round shards04; tools/menu_0_3_27_patch.py).
Build first: python tools/menu_0_3_27_patch.py && python SkyyMenu/build_skyymenu_0.3.27.py

    python SkyyMenu/test_skyymenu_0.3.27.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.3.26 -> 0.3.27: only MenuData (the tile tables) + the version texts; non-class: manifest (+ server.lang only if it moved)
  TILE  MenuData read in a JVM (0.3.26 = the control): no main-view entry "Shards", no entry needs / calls shard:fn:open, slot 11 empty;
        every other main tile keeps its slot / icon / action / rule; the Island Menu tile's text says where shard menus open; no class of
        the 0.3.27 jar names shard:fn:open (0.3.26's does); the icon item Skyy_Menu_Icon_Shards still ships (hidden); the Admin page's four
        Shards buttons (OpsPage) are still there
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.3.27"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.26.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards04", "menu")))
PKG = "com.skyy.menu."
EXPECT = {
    "MenuData": ["~<clinit>"],
    "CfgFn": ["~m opExport"],          # the version texts
    "CfgRows": ["~m header"],
    "SkyyMenuPlugin": ["~m setup"],
    "OpsPage": ["~<clinit>"],          # the mod versions the Admin page lists, read from the newest build scripts at BUILD time (as in 0.3.26)
}
if HK.arg("--phase") == "compare":
    _eq0 = HK.Child.eq

    def _eq(self, got, want, what):
        if what == "C: non-class entries changed" and want == ["manifest.json"]:
            got = sorted(got)
            ok_ = got in (["manifest.json"], ["Server/Languages/en-US/server.lang", "manifest.json"])
            return self.check(ok_, "C: non-class entries changed = manifest (+ server.lang): %s" % got)
        return _eq0(self, got, want, what)
    HK.Child.eq = _eq
ADDED = []


def run_tile(out, jar, scratch, _home):
    from jpype import JClass, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    URL, File = JClass("java.net.URL"), JClass("java.io.File")
    old = JClass("java.net.URLClassLoader")(JArray(URL)([File(OLD_JAR).toURI().toURL(), File(B.SERVER_JAR).toURI().toURL()]),
                                            JClass("java.lang.ClassLoader").getPlatformClassLoader())
    OD = JClass("java.lang.Class").forName(PKG + "MenuData", True, old)
    ND = JClass(PKG + "MenuData").class_

    def arr(C, n):
        return [str(x) for x in C.getField(n).get(None)]

    def tiles(C):
        v, sl, nm, ic, act, need, body = (arr(C, "E_VIEW"), [int(x) for x in C.getField("E_SLOT").get(None)], arr(C, "E_NAME"), arr(C, "E_ICON"),
                                          arr(C, "E_ACT"), arr(C, "E_NEED"), arr(C, "E_BODY"))
        return [dict(view=v[i], slot=sl[i], name=nm[i], icon=ic[i], act=act[i], need=need[i], body=body[i]) for i in range(len(v))]
    nt, ot = tiles(ND), tiles(OD)
    nmain = dict((t["slot"], t) for t in nt if t["view"] == "main")
    omain = dict((t["slot"], t) for t in ot if t["view"] == "main")
    K.check(11 in omain and "Shards" in omain[11]["name"] and omain[11]["need"] == "shard:fn:open", "TILE control: 0.3.26 had the Shards tile at main 11 (need shard:fn:open)")
    K.check(11 not in nmain and not [t for t in nt if "Shards" == t["name"].strip()], "TILE 0.3.27: no Shards tile, slot 11 empty")
    K.check(not [t for t in nt if "shard:fn:open" in t["act"] or t["need"] == "shard:fn:open"], "TILE 0.3.27: no entry needs or calls shard:fn:open")
    K.eq(sorted(s for s in omain if s != 11), sorted(nmain), "TILE every other main tile keeps its slot")
    for s, t in nmain.items():
        o = omain[s]
        same = dict(t)
        same.pop("body")
        so = dict(o)
        so.pop("body")
        K.check(same == so, "TILE main %d %s keeps its icon / action / rule" % (s, t["name"]))
        if "Island Menu" in t["name"]:
            K.check("Shards: right-click one on your island to open its menu." in t["body"] and "Shards:" not in o["body"],
                    "TILE the Island Menu text says where shard menus open (new in 0.3.27)")
        else:
            K.check(t["body"] == o["body"], "TILE main %d %s text unchanged" % (s, t["name"]))
    K.eq(len(nt), len(ot) - 1, "TILE exactly one entry less (the Shards tile)")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.check(not [n for n in zn.namelist() if n.endswith(".class") and b"shard:fn:open" in zn.read(n)], "TILE no 0.3.27 class names shard:fn:open")
    K.check([n for n in zo.namelist() if n.endswith(".class") and b"shard:fn:open" in zo.read(n)] != [], "TILE control: 0.3.26 named it")
    K.check("Server/Item/Items/Utility/Skyy_Menu_Icon_Shards.json" in zn.namelist(), "TILE the Skyy_Menu_Icon_Shards icon item still ships (hidden)")
    ops = [n for n in zn.namelist() if n.endswith("OpsPage.class")]
    blob = b"".join(zn.read(n) for n in zn.namelist() if n.endswith(".class"))
    K.check(all(x in blob for x in (b"shardadmin give {p}", b"shardadmin info {p}", b"shardadmin unplace {p}", b"shardadmin unload {p}")) and ops,
            "TILE the Admin page's four Shards buttons are still there")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("tile", run_tile)], script=__file__)
