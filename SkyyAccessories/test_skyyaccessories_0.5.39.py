"""Harness for SkyyAccessories 0.5.39 (acc:fn:charms vc:power / vc:pick - the Power tab of the inventory's Charms panel for SkyyMenu 0.3.77;
tools/accessories_0_5_39_patch.py, round oldmenu9). Build first:
    python tools/accessories_0_5_39_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.39.py
    python SkyyAccessories/test_skyyaccessories_0.5.39.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; 0.5.38's patch still regenerates 0.5.38; no new system / command / class; line endings
                 kept; the jar adds / removes no entry, the only changed non-class entry = manifest.json; acc:fn:charms still put + removed once
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.38 -> 0.5.39 (AccPage: + vcPower / vcPick, ~vc; AccBagFn ~vcApply; the version texts)
  VP    EXECUTED with the real AccPage.vc / AccPower on 0.5.37's World stand-in: vc:power = the Power tab's own numbers (AP of the bag,
                 multiplier, the Power that works now, the wait, on / off, the profile key, the Combat 15 level, every visible Power: id, name,
                 group, lock text, statText at your AP, picked); vc:pick = AccPower.pick with the switch wait: picked = '+' and the file
                 written; the same press again (an older drawing) = '=' + nothing written; with the new shown Power = '=already'; a locked
                 Power / the wait / Powers off / an unknown or display-name id / an empty arg / another profile's key / a busy profile = refused,
                 the file untouched; the apply path (not online = "off|" / "-"); vc:rows still answers
  VR    0.5.38's vc:rows / vc:craft checks again on this jar
  VC    0.5.37's vc:list / tier / take / put checks again on this jar
  OP036 0.5.36's Enchanted Craft-row checks again on this jar
  LIVE  start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyAccessories (start 2 changes nothing)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the real world thread call from SkyyMenu's page; the panel render.
Scratch: tools/dev/scratch/oldmenu9/acc (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "oldmenu9", "acc")]
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq
_chd0 = HK.Child


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T538 = _mod(os.path.join(HERE, "test_skyyaccessories_0.5.38.py"), "test_skyyaccessories_0_5_38")
T537, T536, T534, T22 = T538.T537, T538.T536, T538.T534, T538.T22
HK.run_compare = _cmp0
HK.Child = _chd0
HK.Child.eq = _eq00

VERSION, OLD = "0.5.39", "0.5.38"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyaccessories_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "accessories_0_5_39_patch.py")
PKG = "com.skyy.accessories."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T534.LIVE_DIR
EXPECT = {
    "AccPage": ["+m vcPick", "+m vcPower", "~m vc"],
    "AccBagFn": ["~m vcApply"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAccessoriesPlugin": ["~m setup"],          # the version texts
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
FC, SPD = T537.FC, T537.SPD


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAccessories 0.5.39 - build script') and g.count('VERSION = "0.5.39"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.eq((g.count('bridge().put("acc:fn:charms"'), g.count('bridge().remove("acc:fn:charms")')), (1, 1), "S acc:fn:charms still published once, removed once")
    K.check("AccPower.pick(u, k, q[0], System.currentTimeMillis(), true)" in g and 'if (!cur.equals(q[1])) return "=Your Power changed since you looked' in g,
            "S vc:pick = the page's own pick WITH the switch wait, guarded by the Power the panel showed")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(ROOT, "tools", "accessories_0_5_38_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), [], "S the jar adds / removes no entry")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def run_vp(out, jar, scratch, _home):
    K = HK.Child(out)
    T22.JAR = jar
    M = T22.m18()
    W = M.World(os.path.join(scratch, "vp"))
    C, D, A = W.Craft, W.Defs, W.Acc
    from jpype import JClass, JArray, JObject, JImplements, JOverride
    M.setup_recipes(W)
    Pw = W.J("AccPower")
    PG, BF = W.J("AccPage"), W.J("AccBagFn")
    OBJ = lambda xs: JArray(JClass("java.lang.Object"))(xs)
    pdir = os.path.join(scratch, "vp", "power")
    Pw.DIR = JClass("java.nio.file.Paths").get(pdir)
    Pw.WAIT = 0
    Pw.PICK.clear()
    LV = {"v": None}

    @JImplements("java.util.function.Function")
    class LvFn(object):
        @JOverride
        def apply(self, a):
            return None if LV["v"] is None else JObject(LV["v"], "java.lang.Integer")
    W.bridge.put("skill:fn:level", LvFn())
    inv = W.inv(fill=None, put=[])
    p, pr, U = W.player(inv, "Pow")
    k = str(U)
    A.putK(U, k, 0, SPD)

    def vc(op, kk, arg):
        return str(PG.vc(op, pr, None, None, p, U, kk, arg))

    def parse(r):
        ls = r.split("\n")
        return ls[0].split("|"), [l_.split("|") for l_ in ls[1:] if l_.startswith("p|")]

    def pfile():
        f_ = os.path.join(pdir, k + ".properties")
        return open(f_, encoding="latin-1").read() if os.path.exists(f_) else None

    def cur_id():
        i_ = int(Pw.effIndex(U, k))
        return str(Pw.PW_ID[i_]) if i_ >= 0 else ""

    cl = lambda t_: t_.replace("|", "/").replace("\n", " ").replace("\r", " ")   # AccPage.vcClean
    # P1 the read = the Power tab's own numbers (no SkyySkills level: the Combat 15 Powers say so)
    Pw.LV.clear()
    h, ps = parse(vc("vc:power", "", ""))
    ap = int(Pw.apOf(C.bagSnap(U, k)))
    m = Pw.mult(ap)
    K.check(h[0] == "ok" and h[1] == str(ap) and h[2] == str(Pw.multText(m)) and h[3] == cur_id() and h[4] == "0" and h[5] == "1" and h[6] == k
            and h[7] == str(Pw.UNLOCK) and h[8] == "0" and len(h) == 9 and ap > 0,
            "P1 header: ok | AP of the bag | x multiplier | the Power that works now | wait 0 | on | the profile key | Combat 15 | wait (%s)" % h)
    want = [i_ for i_ in range(len(Pw.PW_ID)) if bool(Pw.visible(i_))]
    ok = len(ps) == len(want)
    for j_, i_ in enumerate(want):
        r_ = ps[j_] if j_ < len(ps) else []
        lk_ = Pw.lockOf(U, i_)
        one_ = (len(r_) == 8 and r_[1] == str(i_) and r_[2] == str(Pw.PW_ID[i_]) and r_[3] == str(Pw.PW_NAME[i_]) and r_[4] == str(Pw.PW_GRP[i_])
                and r_[5] == ("" if lk_ is None else cl(str(lk_))) and r_[6] == cl(str(Pw.statText(i_, m))) and r_[7] == ("1" if str(Pw.PW_ID[i_]) == h[3] else "0"))
        if not one_:
            K.notes.append("P1 row %d mismatch: %s" % (i_, r_))
        ok = ok and one_
    K.check(ok and len(ps) >= 11, "P1 every visible Power = id, name, group, lock, statText at your AP, picked - in the tab's order (%d rows)" % len(ps))
    K.check(sum(1 for r_ in ps if r_[7] == "1") == 1 and any(r_[5].startswith("needs SkyySkills") for r_ in ps if r_[4] == "1"),
            "P1 exactly one row is yours; the Combat 15 Powers without a Combat level say they need SkyySkills")
    # P2 the lock with a Combat level
    LV["v"] = 14
    Pw.LV.clear()
    h, ps = parse(vc("vc:power", "", ""))
    gc_ = [r_ for r_ in ps if r_[2] == "GlassCannon"]
    K.check(gc_ and gc_[0][5] == "unlocks at Combat 15 (you are Combat 14)" and all(r_[5] == "" for r_ in ps if r_[4] == "0"),
            "P2 Combat 14: the Combat 15 Powers say when they unlock, the Combat ones are free (%s)" % (gc_[0][5] if gc_ else None))
    # P3 the pick (the shown Power guards it)
    shown_ = h[3]
    f0_ = pfile()
    r = vc("vc:pick", k, "Slayer|" + shown_)
    K.check(r.startswith("+Power is now Slayer") and cur_id() == "Slayer" and pfile() is not None and "power=Slayer" in pfile(),
            "P3 Pick Slayer (the panel showed %s) = '+Power is now Slayer', power/<key>.properties written (%s; file before: %s)" % (shown_, r, f0_ is not None))
    t1_ = pfile()
    r = vc("vc:pick", k, "Tank|" + shown_)
    K.check(r.startswith("=Your Power changed since you looked (it is Slayer now)") and cur_id() == "Slayer" and pfile() == t1_,
            "P3 a press from the older drawing (it showed %s) = '=', nothing written (%s)" % (shown_, r))
    h, ps = parse(vc("vc:power", "", ""))
    K.check(h[3] == "Slayer" and [r_[2] for r_ in ps if r_[7] == "1"] == ["Slayer"], "P3 the redraw shows Slayer as yours")
    r = vc("vc:pick", k, "Tank|" + h[3])
    K.check(r.startswith("+Power is now Tank") and cur_id() == "Tank", "P3 the same press again with the new drawing runs (%s)" % r)
    r = vc("vc:pick", k, "Tank|Tank")
    t2_ = pfile()
    K.check(r == "=Tank is already your Power" and pfile() == t2_, "P3 the Power you have = '=already', nothing written (%s)" % r)
    for arg_, want_, why_ in (("GlassCannon|Tank", "-Glass Cannon is locked - it unlocks at Combat 15", "a locked Power"),
                              ("Nope|Tank", "-There is no such Power here", "an unknown id"),
                              ("Glass Cannon|Tank", "-There is no such Power here", "a display name (only ids the read sent)"),
                              ("", "-Pick a Power first", "an empty arg"), ("Slayer", "-Pick a Power first", "no shown Power"),
                              ("Slayer|" + "x" * 50, "-Pick a Power first", "an overlong shown Power")):
        r = vc("vc:pick", k, arg_)
        K.check(r.startswith(want_) and cur_id() == "Tank" and pfile() == t2_, "P3 %s: refused, nothing written (%s)" % (why_, r))
    LV["v"] = 15
    Pw.LV.clear()
    r = vc("vc:pick", k, "GlassCannon|Tank")
    K.check(r.startswith("+Power is now Glass Cannon") and cur_id() == "GlassCannon", "P3 Combat 15: Glass Cannon can be picked (%s)" % r)
    # the switch wait (the page's own rule)
    Pw.WAIT = 600
    h, ps = parse(vc("vc:power", "", ""))
    t3_ = pfile()
    r = vc("vc:pick", k, "Tank|GlassCannon")
    K.check(r.startswith("-wait ") and r.endswith("before you switch your Power again") and cur_id() == "GlassCannon" and pfile() == t3_ and int(h[4]) > 0 and h[8] == "600",
            "P3 the switch wait: refused, nothing written; the read says how long (%s, wait left %s)" % (r, h[4]))
    Pw.WAIT = 0
    # P4 the profile key + the busy gate + Powers off
    r = vc("vc:pick", k + "x", "Tank|GlassCannon")
    K.check(r.startswith("-Your profile changed") and cur_id() == "GlassCannon" and pfile() == t3_, "P4 another profile's key: nothing written (%s)" % r)
    W.bridge.put("profile:busy:" + k, "1")
    K.check(vc("vc:power", "", "").startswith("off|your profile is still loading") and vc("vc:pick", k, "Tank|GlassCannon").startswith("-your profile is still loading")
            and pfile() == t3_, "P4 a busy profile: the read says so, Pick writes nothing")
    W.bridge.remove("profile:busy:" + k)
    Pw.ON = False
    h, ps = parse(vc("vc:power", "", ""))
    r = vc("vc:pick", k, "Tank|" + h[3])
    K.check(h[5] == "0" and r.startswith("-Accessory Powers are switched off") and pfile() == t3_, "P4 Powers off: the read says 0, Pick refused (%s)" % r)
    Pw.ON = True
    K.check(str(PG.vc("vc:power", pr, None, None, None, U, k, "")).startswith("off|Your player could not be read")
            and str(PG.vc("vc:pick", pr, None, None, None, U, k, "Tank|GlassCannon")).startswith("-Your player could not be read"), "P4 no player: off / -")
    # P5 the bridge apply + the older ops
    fn = BF()
    K.check(str(fn.apply(OBJ(["vc:power", U, "", ""]))).startswith("off|You are not online here") and str(fn.apply(OBJ(["vc:pick", U, k, "Tank|GlassCannon"]))).startswith("-You are not online"),
            "P5 apply: a player the Universe does not know = off / - (nothing written)")
    K.check(vc("vc:rows", "", "0").startswith("ok|0|") and vc("vc:list", "", "").startswith("ok|") and vc("vc:nope", k, "").startswith("-Void Charms does not know that"),
            "P5 vc:rows / vc:list still answer; an unknown op = 'does not know that' (what SkyyMenu 0.3.77 reads as 'needs 0.5.39')")
    K.notes.append("VP power rows: %d, AP %d" % (len(ps), ap))
    K.save()


def run_vr(out, jar, scratch, home):
    T538.run_vr(out, jar, scratch, home)


def run_vc(out, jar, scratch, home):
    T537.run_vc(out, jar, scratch, home)


def run_op036(out, jar, scratch, home):
    T536.run_op(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("vp", run_vp), ("vr", run_vr), ("vc", run_vc), ("op036", run_op036), ("live", T534.run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
