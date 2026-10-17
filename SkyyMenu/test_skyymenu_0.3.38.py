"""Harness for SkyyMenu 0.3.38 (the Void Charms rename, the Supplies tab icon, Teleport Arrange: dotted warp names + Prev / Next;
tools/menu_0_3_38_patch.py). Build first:
    python tools/menu_0_3_38_patch.py && python SkyyMenu/build_skyymenu_0.3.38.py

    python SkyyMenu/test_skyymenu_0.3.38.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py - the 0.3.37 harness's way: -Xverify:all over the SkyyMenu 0.3.19 engine stand-ins):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.37 -> 0.3.38: exactly the listed members differ; the non-class entries = manifest, server.lang (+ the Supplies item
                name), the new icon item Skyy_Menu_Icon_Supplies (JSON + PNG)
  T    the 0.3.37 harness's Teleport phase on this jar (sources, clicks, Arrange, degrade, art) - unchanged behaviour
  T38  EXECUTED on the same stand-ins (the 0.3.37 phase with these checks added before its DEGRADE part):
       DOTS    MenuLayout.okWarp takes '.', up to 64 characters, still refuses a space; okKey("warp:mine.deep", tp)
       PAGES   with 17+ warps Arrange has more than one page; its foot row shows Next > (and < Prev on page 2), the row fits; Next / Prev
               page through the auto tiles while Arrange stays open; the pager words also pass the kit 1.7 rules (H.kit17_rules)
       ARRANGE a dotted warp (mine.deep) found on its page is pinned by a click (the grid / layout hold warp:mine.deep, picked up); a warp
               whose name breaks the rule ("bad name") says it can't be arranged and nothing is saved
  ICON / TEXT  (in T38): TAB_KEY / TAB_ICON map storage:supplies -> Skyy_Menu_Icon_Supplies; its JSON + PNG = art/accessory-bag-icon
               (manifest sha256), hidden (Variant, no Categories); the Mods data says "Void Charms" (setup title), "Craft tab of Void
               Charms", no "Accessories and Bags"
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, json, hashlib, zipfile, inspect, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_s37 = importlib.util.spec_from_file_location("test_skyymenu_0_3_37", os.path.join(HERE, "test_skyymenu_0.3.37.py"))
T37 = importlib.util.module_from_spec(_s37)
_s37.loader.exec_module(T37)
T35 = T37.T35

VERSION = "0.3.38"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.37.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "vcrename", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T35.LIVE_DIR
ADDED = []
EXPECT = {      # the class compare 0.3.37 -> 0.3.38
    'CfgFn': ['~m opExport'], 'CfgRows': ['~m header'],   # the config kit's version text
    'MenuData': ['~<clinit>'],                            # TAB_KEY / TAB_ICON (+ Supplies), the Mods texts, the version
    'MenuLayout': ['~m okWarp'],                          # '.' + 64 characters
    'MenuPage': ['~m dashEditClick', '~m foot'],          # the can't-be-arranged line; Arrange's Prev / Next
    'OpsPage': ['~<clinit>'],                             # the live SET versions the Admin page lists (Accessories 0.5.24 deployed since)
    'SkyyMenuPlugin': ['~m setup'],                       # the ready line
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
SART = os.path.join(ROOT, "art", "accessory-bag-icon")

T38 = r'''
    # ================= 0.3.38: DOTS + PAGES + the Supplies icon + the Mods texts
    K.check(bool(ML.okWarp("mine.deep")) and bool(ML.okWarp("x" * 64)) and not bool(ML.okWarp("x" * 65)) and not bool(ML.okWarp("bad name"))
            and bool(ML.okKey("warp:mine.deep", True)) and not bool(ML.okKey("warp:bad name", True)), "DOTS: okWarp takes '.', 64 characters, no space")
    for n_ in ["mine.deep", "bad name"] + ["w%02d" % i_ for i_ in range(14)]:
        mkwarp(n_)
    pg6 = openp(P, MP(P.pr, "tp"))
    built(P, pg6, "Teleport (many warps)")
    foot(P, pg6, "hedit")
    c6, _e6, _a6 = built(P, pg6, "Teleport (Arrange, page 1 of several)")
    K.check(bool(pg6.editing) and int(pg6.pages) > 1 and int(pg6.pageNo) == 0, "PAGES: Arrange has %d pages" % int(pg6.pages))
    txt6 = " ".join((t or "") for ty, s, t, d in c6)
    K.check("SkyyMTpFnext" in txt6 and "SkyyMTpFprev" not in txt6 and "SkyyMTpFedone" in txt6, "PAGES: Arrange page 1 shows Next > (no < Prev) beside Done")
    seen = {}
    bad_slot = None
    for pn_ in range(int(pg6.pages)):
        aa_ = list(pg6.autoAt)
        for s_ in auto:
            if aa_[s_] is not None:
                seen[str(aa_[s_])] = (pn_, s_)
        if pn_ < int(pg6.pages) - 1:
            foot(P, pg6, "next")
            c7, _e7, _a7 = built(P, pg6, "Teleport (Arrange, page %d)" % (pn_ + 2))
            K.check(bool(pg6.editing) and int(pg6.pageNo) == pn_ + 1 and "SkyyMTpFprev" in " ".join((t or "") for ty, s, t, d in c7),
                    "PAGES: Next > turns Arrange to page %d (< Prev shown, still arranging)" % (pn_ + 2))
    K.check("warp:mine.deep" in seen and "warp:bad name" in seen and "warp:w13" in seen, "PAGES: every auto tile is reachable in Arrange: %d tiles" % len(seen))
    while int(pg6.pageNo) > 0:
        foot(P, pg6, "prev")
    K.check(int(pg6.pageNo) == 0 and bool(pg6.editing), "PAGES: < Prev goes back to page 1")
    pn_, s_ = seen["warp:bad name"]
    for _i in range(pn_):
        foot(P, pg6, "next")
    slot(P, pg6, s_)
    gb = [None if x is None else str(x) for x in ML.grid(u, 1)]
    K.check("warp:bad name" not in gb and int(pg6.editSel) == -1 and "can't be arranged" in str(pg6.status), "ARRANGE: a warp name the layout can't save is not picked up: %r" % str(pg6.status))
    while int(pg6.pageNo) > 0:
        foot(P, pg6, "prev")
    pn_, s_ = seen["warp:mine.deep"]
    for _i in range(pn_):
        foot(P, pg6, "next")
    K.eq(str(list(pg6.autoAt)[s_]), "warp:mine.deep", "ARRANGE: mine.deep sits where the page walk found it")
    slot(P, pg6, s_)
    gd = [None if x is None else str(x) for x in ML.grid(u, 1)]
    K.check(gd[s_] == "warp:mine.deep" and int(pg6.editSel) == s_ and "Picked up" in str(pg6.status), "ARRANGE: a dotted warp is pinned + picked up (0.3.37 dropped it): %r" % str(pg6.status))
    foot(P, pg6, "edone")
    JV("MenuIO").stop(2000)
    lay6 = ""
    for root_, _d, fs_ in os.walk(os.path.join(home, "layouts")):
        for f_ in fs_:
            lay6 += open(os.path.join(root_, f_), encoding="utf8", errors="replace").read()
    K.check("warp:mine.deep" in lay6 and "bad name" not in lay6, "ARRANGE: the layout file holds warp:mine.deep (and no bad name)")
    JV("MenuIO").begin()
    pg7 = openp(P, MP(P.pr, "tp"))
    built(P, pg7, "Teleport (dotted warp pinned)")
    K.eq(acts(pg7).get(s_), "warp:mine.deep", "ARRANGE: a new page shows mine.deep where it was pinned (click = warp:mine.deep)")
    # the Supplies tab icon + the Mods texts
    tk = [str(x) for x in MD.TAB_KEY]
    ti = [str(x) for x in MD.TAB_ICON]
    K.check("storage:supplies" in tk and ti[tk.index("storage:supplies")] == "Skyy_Menu_Icon_Supplies" and ti.count("Skyy_Menu_Icon_Supplies") == 1,
            "ICON: TAB_ICON storage:supplies = Skyy_Menu_Icon_Supplies (one page per icon)")
    K.check("storage_supplies" not in [str(x) for x in MD.TAB_ART], "ICON: no tab picture pair for Supplies (label only, as before)")
    z6 = zipfile.ZipFile(jar)
    sj = json.loads(z6.read("Server/Item/Items/Utility/Skyy_Menu_Icon_Supplies.json").decode("utf8"))
    sm = json.load(open(os.path.join(SART, "manifest.json"), encoding="utf8"))
    K.check(sj["Icon"] == "Icons/ItemsGenerated/Skyy_Menu_Icon_Supplies.png" and sj.get("Variant") is True and "Categories" not in sj and "Recipe" not in sj
            and hashlib.sha256(z6.read("Common/Icons/ItemsGenerated/Skyy_Menu_Icon_Supplies.png")).hexdigest() == sm["files"][0]["sha256"],
            "ICON: the Supplies icon item = the approved satchel (art/accessory-bag-icon sha256), hidden, no recipe")
    lang6 = z6.read("Server/Languages/en-US/server.lang").decode("utf8")
    K.check("items.Skyy_Menu_Icon_Supplies.name=Supplies" in lang6, "ICON: the item's name line")
    blob = b"".join(z6.read(n) for n in z6.namelist() if n.endswith(".class"))
    K.check(b"Craft tab of Void Charms" in blob and b"charm slots, booster lines, notices, Lantern" in blob and b"Accessories and Bags" not in blob
            and b"that work in the bag" not in blob, "TEXT: the SkyyAccessories Mods entry says Void Charms (setup blurb + description)")
    # ---------------- DEGRADE'''
_src = inspect.getsource(T37.run_t)
_anc = "\n    # ---------------- DEGRADE"
assert _src.count(_anc) == 1, "the 0.3.37 harness changed (DEGRADE anchor)"
_src = _src.replace("def run_t(out, jar, scratch, _home):", "def run_t38(out, jar, scratch, _home):").replace(_anc, T38, 1)
_src = _src.replace('hcls = os.path.join(scratch, "hcls_t")', 'hcls = os.path.join(scratch, "hcls_t38")').replace(
    'home = os.path.join(scratch, "home_t")', 'home = os.path.join(scratch, "home_t38")')
T37.__dict__["SART"] = SART
exec(compile(_src, T37.__file__, "exec"), T37.__dict__)


def nonclass_want():
    return sorted(["manifest.json", "Server/Languages/en-US/server.lang", "Server/Item/Items/Utility/Skyy_Menu_Icon_Supplies.json",
                   "Common/Icons/ItemsGenerated/Skyy_Menu_Icon_Supplies.png"])


if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        _eq0 = HK.Child.eq

        def _eq(self, got, want, what):
            if what == "C: non-class entries changed" and want == ["manifest.json"]:
                return _eq0(self, sorted(got), nonclass_want(), "C: non-class entries changed = manifest, server.lang, the Supplies icon item")
            return _eq0(self, got, want, what)
        HK.Child.eq = _eq
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("t", T37.run_t), ("t38", T37.run_t38), ("live", T35.run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
