"""Harness for SkyyMenu 0.3.39 (the Storage > Supplies tab picture pair + MODS_VERSIONS = the live SET; tools/menu_0_3_39_patch.py).
Build first:
    python tools/menu_0_3_39_patch.py && python SkyyMenu/build_skyymenu_0.3.39.py

    python SkyyMenu/test_skyymenu_0.3.39.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py - the 0.3.38 harness's way: -Xverify:all over the SkyyMenu 0.3.19 engine stand-ins):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3.38 -> 0.3.39: exactly the listed members differ; the non-class entries = manifest + the two Supplies tab pictures
               (Common/UI/Custom/SkyyHubTabs/storage_supplies(_on)@2x.png)
  T    the 0.3.37 harness's Teleport phase on this jar - unchanged behaviour
  T39  the 0.3.38 T38 phase (dots, Arrange pages, the Supplies icon item, the Void Charms texts) with its "no Supplies picture" check
       turned round:
       ART     TAB_ART holds storage_supplies; the jar's two SkyyHubTabs files = art/hub-tab-icons storage_supplies(_on).png (manifest
               sha256 + bytes); TAB_ART = every TAB_KEY (no exemption left)
       VERS    MOD_VER (the Mods list's offline versions) = tools/deploy_set.py SET for every listed mod (SkyyAccessories no longer 0.5.22)
  D    live     two starts on a scratch COPY of the live Skyy_SkyyMenu (the 0.3.35 harness's phase)
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import harness_kit as HK

_s38 = importlib.util.spec_from_file_location("test_skyymenu_0_3_38", os.path.join(HERE, "test_skyymenu_0.3.38.py"))
T38M = importlib.util.module_from_spec(_s38)
_s38.loader.exec_module(T38M)
T37 = T38M.T37
T35 = T38M.T35

VERSION = "0.3.39"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyMenu-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.38.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "m339", "menu")))
PKG = "com.skyy.menu."
LIVE_DIR = T35.LIVE_DIR
ADDED = []
EXPECT = {      # the class compare 0.3.38 -> 0.3.39
    'CfgFn': ['~m opExport'], 'CfgRows': ['~m header'],   # the config kit's version text
    'MenuData': ['~<clinit>'],                            # TAB_ART (+ storage_supplies), MOD_VER (the live SET), the version
    'OpsPage': ['~<clinit>'],                             # the live SET versions the Admin page lists (SET moved on since 0.3.38)
    'SkyyMenuPlugin': ['~m setup'],                       # the ready line
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
TART = os.path.join(ROOT, "art", "hub-tab-icons")
DEPLOY_SET = os.path.join(ROOT, "tools", "deploy_set.py")

_old_chk = '''    K.check("storage_supplies" not in [str(x) for x in MD.TAB_ART], "ICON: no tab picture pair for Supplies (label only, as before)")'''
_new_chk = '''    ta_ = [str(x) for x in MD.TAB_ART]
    K.check("storage_supplies" in ta_ and sorted(ta_) == sorted(k_.replace(":", "_") for k_ in tk), "ART: TAB_ART holds storage_supplies and = every TAB_KEY (no exemption)")
    tm_ = json.load(open(os.path.join(TART, "manifest.json"), encoding="utf8"))
    tf_ = dict((f_["path"], f_) for f_ in tm_["files"])
    zt_ = zipfile.ZipFile(jar)
    for s_, f_ in (("", "storage_supplies.png"), ("_on", "storage_supplies_on.png")):
        d_ = zt_.read("Common/UI/Custom/SkyyHubTabs/storage_supplies%s@2x.png" % s_)
        K.check(hashlib.sha256(d_).hexdigest() == tf_[f_]["sha256"] and len(d_) == tf_[f_]["bytes"]
                and d_ == open(os.path.join(TART, f_), "rb").read(), "ART: SkyyHubTabs/storage_supplies%s@2x.png = art/hub-tab-icons/%s" % (s_, f_))
    import ast as ast_
    set_ = None
    for n_ in ast_.parse(open(DEPLOY_SET, encoding="utf-8").read()).body:
        if isinstance(n_, ast_.Assign) and any(getattr(t_, "id", None) == "SET" for t_ in n_.targets):
            set_ = dict(ast_.literal_eval(n_.value))
    mn_ = [str(x) for x in MD.MOD_NAME] if hasattr(MD, "MOD_NAME") else None
    mv_ = [str(x) for x in MD.MOD_VER]
    if mn_ is not None:
        bad_ = [(m_, v_, set_.get(m_)) for m_, v_ in zip(mn_, mv_) if m_ != "SkyyMenu" and m_ in set_ and set_[m_] != v_]
        K.check(set_ is not None and not bad_ and "0.5.22" not in [v_ for m_, v_ in zip(mn_, mv_) if m_ == "SkyyAccessories"],
                "VERS: MOD_VER = the live SET for every listed mod %s" % (bad_ or ""))
    else:
        K.check(set_ is not None and set_["SkyyAccessories"] in mv_ and "0.5.22" not in mv_, "VERS: MOD_VER has SkyyAccessories %s, no 0.5.22" % set_["SkyyAccessories"])'''
_src = T38M._src
assert _src.count(_old_chk) == 1, "the 0.3.38 harness changed (Supplies art check)"
_src = _src.replace(_old_chk, _new_chk, 1).replace("def run_t38(out, jar, scratch, _home):", "def run_t39(out, jar, scratch, _home):")
_src = _src.replace('hcls = os.path.join(scratch, "hcls_t38")', 'hcls = os.path.join(scratch, "hcls_t39")').replace(
    'home = os.path.join(scratch, "home_t38")', 'home = os.path.join(scratch, "home_t39")')
T37.__dict__["TART"] = TART
T37.__dict__["DEPLOY_SET"] = DEPLOY_SET
exec(compile(_src, T37.__file__, "exec"), T37.__dict__)


def nonclass_want():
    return sorted(["manifest.json", "Common/UI/Custom/SkyyHubTabs/storage_supplies@2x.png", "Common/UI/Custom/SkyyHubTabs/storage_supplies_on@2x.png"])


if __name__ == "__main__":
    if HK.arg("--phase") == "compare":
        _eq0 = HK.Child.eq

        def _eq(self, got, want, what):
            if what == "C: non-class entries changed" and want == ["manifest.json"]:
                return _eq0(self, sorted(got), nonclass_want(), "C: non-class entries changed = manifest + the two Supplies tab pictures")
            return _eq0(self, got, want, what)
        HK.Child.eq = _eq
    HK.run(name="SkyyMenu", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("t", T37.run_t), ("t39", T37.run_t39), ("live", T35.run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyMenu"))
