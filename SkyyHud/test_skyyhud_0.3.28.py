"""Harness for SkyyHud 0.3.28 (HUD widget Background OFF by default, except the Quest Tracker; tools/hud_0_3_28_patch.py). Build first:
python tools/hud_0_3_28_patch.py && python SkyyHud/build_skyyhud_0.3.28.py

    python SkyyHud/test_skyyhud_0.3.28.py [--jar SkyyHud-0.3.28.jar] [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; the engine stand-ins of tools/hub_tab_kit.stage):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.27 -> 0.3.28: Widgets + def0 / bgDef, ~def; the version texts only; non-class entries: the manifest
  R27  the 0.3.27 phase re-run unchanged on the new jar (first-join picture rebuild + hud:assets:ready)
  R28  EXECUTED (the jar's own Widgets / WLayout / LayoutStore code):
       DEF      Widgets.def(id) for EVERY widget id: Background OFF, Quest ON; every other field = def0(id) (the 0.3.27 layout); an
                unknown id OFF; bgDef(id) agrees
       NEW      a player with no layout file: LayoutStore.get gives each widget its default Background (Quest ON, the rest OFF), and
                the drawn widget markup has no Background (Quest has it)
       SAVED    a player file holding Coords Background ON and Quest Background OFF (and no Zone line): both kept; Zone (missing) takes
                the new default OFF; the file's bytes are never rewritten by reading it
       OLD      a pre-0.3.6 five-field line still reads Background ON (WLayout's constructor unchanged)
       RESET    LayoutStore.reset (= /skyyhud reset): every widget back to Background OFF, Quest ON, saved as such ("...,0" / "...,1")
       ADMIN    a server default layout code (Server Setup -> HUD) holding Coords Background ON: start / reset keep it ON; widgets the
                code leaves out follow the new default
       IMPORT   an export code's own Background values are kept
  AA   audit    the engine-access audit
Not testable without the game (UNVERIFIED): how a background-less widget reads over bright terrain.
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK
import hub_tab_kit as HT

VERSION = "0.3.28"
PKG = "com.skyy.hud."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyHud-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyHud-0.3.27.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "hud0328", "h")))
ADDED = []
EXPECT = {
    "Widgets": ["+m bgDef", "+m def0", "~m def"],
    # the version string (the kit's header / export, the ready line)
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"], "SkyyHudPlugin": ["~m setup"],
}
BG_ON = ["Quest"]


def t27():
    spec = importlib.util.spec_from_file_location("hud0327h", os.path.join(HERE, "test_skyyhud_0.3.27.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run_r27(out, jar, scratch, home):
    t27().run_r27(out, jar, scratch, home)


def run_r28(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E = HT.stage(scratch, jar)
    H = lambda n: JClass(PKG + n)
    W, WL, LS, HC = H("Widgets"), H("WLayout"), H("LayoutStore"), H("HudCfg")
    UUID = JClass("java.util.UUID")
    ids = [str(i) for i in W.IDS]
    K.check(len(ids) >= 17 and "Quest" in ids and "Abilities" in ids and "Feed" in ids, "DEF: the widget ids (%d): %s" % (len(ids), ids))

    def want(i):
        return i in BG_ON

    def fields(l):
        return (bool(l.en), str(l.anchor), int(l.dx), int(l.dy), int(l.scale), str(l.col), bool(l.bold), bool(l.ital), bool(l.glow),
                str(l.gcol), int(l.bw), int(l.bh), bool(l.opt), int(l.lines), int(l.ldef), str(l.ocol), str(l.mm), bool(l.fixed))
    # ---------------------------------------------------------------- DEF: the built-in layout of every widget
    d = getattr(W, "def_", None) or getattr(W, "def")       # JPype renames the Python keyword "def" to def_
    bad = [i for i in ids if bool(d(i).bg) != want(i)]
    K.check(bad == [], "DEF: Widgets.def(id).bg is OFF for every widget except Quest (ON) - wrong: %s" % bad)
    K.check([i for i in ids if bool(W.bgDef(i)) != want(i)] == [], "DEF: bgDef agrees for every widget")
    K.check(all(bool(W.def0(i).bg) for i in ids), "DEF: def0 = the 0.3.27 layout (Background ON) for every widget")
    K.check([i for i in ids if fields(d(i)) != fields(W.def0(i))] == [], "DEF: every other field of def(id) = def0(id)")
    K.check(not bool(d("NoSuchWidget").bg) and not bool(W.bgDef("quest")), "DEF: an unknown id (and a wrong-case id) is OFF")
    for i in ids:
        K.check(bool(W.start(i).bg) == want(i), "DEF: Widgets.start(%s) (no server default) Background %s" % (i, "ON" if want(i) else "OFF"))
    # ---------------------------------------------------------------- NEW: no layout file
    hdir = os.path.join(scratch, "hudhome")
    ldir = os.path.join(hdir, "layouts")
    os.makedirs(ldir, exist_ok=True)
    LS.DIR = E.Paths.get(ldir)
    LS.CACHE.clear()
    HC.FILE = E.Paths.get(os.path.join(hdir, "config.properties"))
    HC.load()
    HC.DEFAULT_LAYOUT = ""
    u1 = UUID.fromString("00000000-0000-0000-0000-00000000a281")
    m1 = LS.get(u1)
    K.check([i for i in ids if bool(m1.get(i).bg) != want(i)] == [], "NEW: a player with no file: Quest ON, every other widget OFF")
    K.check(not os.path.exists(os.path.join(ldir, str(u1) + ".properties")), "NEW: reading writes no file")
    src = str(W.widgetSrcW("Coords", m1.get("Coords"), 180))
    K.check("Background:" not in src and "#SkyyWCoords" in src, "NEW: the Coords widget markup has no Background")
    qsrc = str(W.widgetSrcW("Quest", m1.get("Quest"), 180))
    K.check("Background: #0b1524(0.72)" in qsrc, "NEW: the Quest widget markup keeps its Background")
    # ---------------------------------------------------------------- SAVED: explicit values kept, a missing line takes the new default
    u2 = UUID.fromString("00000000-0000-0000-0000-00000000a282")
    f2 = os.path.join(ldir, str(u2) + ".properties")
    body = b"#SkyyHud layout\r\nCoords=1,tl,8,8,100,1\r\nQuest=1,tl,8,42,100,0\r\nGclock=1,bl,8,40,100,0\r\n"
    open(f2, "wb").write(body)
    m2 = LS.get(u2)
    K.check(bool(m2.get("Coords").bg), "SAVED: a saved Coords Background ON stays ON")
    K.check(not bool(m2.get("Quest").bg), "SAVED: a saved Quest Background OFF stays OFF")
    K.check(not bool(m2.get("Gclock").bg), "SAVED: a saved OFF stays OFF")
    K.check(not bool(m2.get("Zone").bg) and not bool(m2.get("Abilities").bg), "SAVED: widgets missing from the file take the new default (OFF)")
    K.check(open(f2, "rb").read() == body, "SAVED: reading never rewrites the player's file")
    # ---------------------------------------------------------------- OLD: a five-field line (before 0.3.6)
    o = WL.parse("1,tl,8,8,100", d("Coords"))
    K.check(o is not None and bool(o.bg), "OLD: a five-field line still reads Background ON")
    K.check(not bool(WL.parse("1,tl,8,8,100,0", d("Quest")).bg) and bool(WL.parse("1,tl,8,8,100,1", d("Coords")).bg), "OLD: field 6 always wins over the default")
    # ---------------------------------------------------------------- RESET: /skyyhud reset
    LS.reset(u2)
    m2 = LS.get(u2)
    K.check([i for i in ids if bool(m2.get(i).bg) != want(i)] == [], "RESET: every widget back to the default (Quest ON, the rest OFF)")
    import io
    p = {}
    for ln in io.open(f2, encoding="latin-1").read().splitlines():
        if "=" in ln and not ln.startswith("#"):
            k, v = ln.split("=", 1)
            p[k] = v.split(",")
    K.check(sorted(p) == sorted(ids), "RESET: the file holds every widget (%d lines)" % len(p))
    K.check([i for i in ids if p.get(i, ["", "", "", "", "", "?"])[5] != ("1" if want(i) else "0")] == [],
            "RESET: saved as Background 0 for every widget, 1 for Quest")
    LS.CACHE.clear()
    K.check([i for i in ids if bool(LS.get(u2).get(i).bg) != want(i)] == [], "RESET: read back from the file the same")
    # ---------------------------------------------------------------- ADMIN: the server default layout code is an explicit choice
    HC.DEFAULT_LAYOUT = "Coords=1:tl:8:8:100:1;Quest=1:tl:8:42:100:0"
    K.check(bool(HC.hasDefault()), "ADMIN: a server default layout is set")
    K.check(bool(W.start("Coords").bg) and not bool(W.start("Quest").bg), "ADMIN: start() keeps the code's own Background values")
    K.check(not bool(W.start("Zone").bg), "ADMIN: a widget the code leaves out follows the new default (OFF)")
    u3 = UUID.fromString("00000000-0000-0000-0000-00000000a283")
    LS.reset(u3)
    m3 = LS.get(u3)
    K.check(bool(m3.get("Coords").bg) and not bool(m3.get("Quest").bg) and not bool(m3.get("Skills").bg), "ADMIN: /skyyhud reset gives the server default's values")
    HC.DEFAULT_LAYOUT = ""
    # ---------------------------------------------------------------- IMPORT: an export code keeps its values
    u4 = UUID.fromString("00000000-0000-0000-0000-00000000a284")
    n = int(LS.importCode(u4, "Coords=1:tl:8:8:100:1;Quest=1:tl:8:42:100:0"))
    m4 = LS.get(u4)
    K.check(n == 2 and bool(m4.get("Coords").bg) and not bool(m4.get("Quest").bg) and not bool(m4.get("Zone").bg),
            "IMPORT: the code's Background values are kept, the rest default (%d imported)" % n)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyHud", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("r27", run_r27), ("r28", run_r28)], script=__file__)
