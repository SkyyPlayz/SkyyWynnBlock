"""Harness for SkyyAccessories 0.5.38 (acc:fn:charms vc:rows / vc:craft - the Charms panel as rows for SkyyMenu 0.3.60;
tools/accessories_0_5_38_patch.py). Build first:
    python tools/accessories_0_5_38_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.38.py
    python SkyyAccessories/test_skyyaccessories_0.5.38.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; 0.5.37's patch still regenerates 0.5.37; no new system / command / class; line endings
                 kept; the jar adds / removes no entry, the only changed non-class entry = manifest.json; acc:fn:charms still put + removed once
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.37 -> 0.5.38 (AccPage: + vcRows / vcCraft, ~vc; AccBagFn ~vcApply; the version texts)
  VR    EXECUTED with the real AccPage.vc / AccCraft rowsFor / lineRow / craft on real engine containers (0.5.37's World stand-in): vc:rows
                 = the Craft tab's rows of each sub tab (same ids / order / status / cost as AccCraft.lineRow, the row's recipe id = ridOf, can =
                 CAN CRAFT / CAN UPGRADE, mode c / u / m, a bad sub = Benches); vc:craft = the Craft tab's button: an UPGRADE in place (materials
                 paid), the SAME click again (double click) = nothing used, a stale / unknown recipe id = nothing used, not enough materials =
                 nothing used, another profile's key = nothing moves, a busy profile = nothing moves; the apply path (not online = "off|" /
                 "-"); acc:fn:bag's own ops unchanged
  VC    0.5.37's vc:list / tier / take / put checks again on this jar
  OP036 0.5.36's Enchanted Craft-row checks again on this jar
  LIVE  start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyAccessories (start 2 changes nothing)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the real world thread call from SkyyMenu's page; the panel render.
Scratch: tools/dev/scratch/menufix1/acc (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "menufix1", "acc")]
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


T537 = _mod(os.path.join(HERE, "test_skyyaccessories_0.5.37.py"), "test_skyyaccessories_0_5_37")
T536, T534, T22 = T537.T536, T537.T534, T537.T22
HK.run_compare = _cmp0
HK.Child = _chd0
HK.Child.eq = _eq00

VERSION, OLD = "0.5.38", "0.5.37"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyaccessories_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "accessories_0_5_38_patch.py")
PKG = "com.skyy.accessories."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T534.LIVE_DIR
EXPECT = {
    "AccPage": ["+m vcCraft", "+m vcRows", "~m vc"],
    "AccBagFn": ["~m vcApply"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAccessoriesPlugin": ["~m setup"],          # the version texts
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
FC, THOR, LEAD, SPD = T537.FC, T537.THOR, T537.LEAD, T537.SPD


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAccessories 0.5.38 - build script') and g.count('VERSION = "0.5.38"') == 1, "S header + VERSION")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.eq((g.count('bridge().put("acc:fn:charms"'), g.count('bridge().remove("acc:fn:charms")')), (1, 1), "S acc:fn:charms still published once, removed once")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(ROOT, "tools", "accessories_0_5_37_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), [], "S the jar adds / removes no entry")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def run_vr(out, jar, scratch, _home):
    K = HK.Child(out)
    T22.JAR = jar
    M = T22.m18()
    W = M.World(os.path.join(scratch, "vr"))
    C, D, A = W.Craft, W.Defs, W.Acc
    from jpype import JClass, JArray
    M.setup_recipes(W)
    for iid in FC:
        W.item(iid, 1, 900)
    for m_ in (THOR, LEAD):
        W.item(m_, 100, 0)
    W.item("Junk_One", 1, 0)
    V = T536.sacks(W, C)
    PG, BF = W.J("AccPage"), W.J("AccBagFn")
    OBJ = lambda xs: JArray(JClass("java.lang.Object"))(xs)

    def fresh(put=(), void=None, name="P", tier=0, fill=None):
        for k_ in ("n", "owe", "opn"):
            V[k_].clear()
        V["paused"].clear()
        V["fail"].clear()
        V["noopen"] = False
        del V["calls"][:]
        V["n"].update(void or {})
        inv = W.inv(fill=fill, put=put)
        p, pr, U = W.player(inv, name)
        k = str(U)
        if tier:
            A.putK(U, k, 0, FC[tier - 1])
        return inv, p, pr, U, k

    def vc(op, pr, p, U, k, arg):
        return str(PG.vc(op, pr, None, None, p, U, k, arg))

    def rows(r):
        ls = r.split("\n")
        return ls[0].split("|"), [l_.split("|") for l_ in ls[1:] if l_.startswith("r|")], [l_ for l_ in ls[1:] if l_.startswith("x|")]

    def state():
        return dict((a, b) for a, b in V["n"].items() if b), dict((a, b) for a, b in V["owe"].items() if b)

    def rid(t):
        return FC[t - 1] + "_Recipe_SkyyCharm"

    # R1 the rows of every sub tab = AccCraft.rowsFor + lineRow (the Craft tab's own rows)
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64)], {LEAD: 90}, "Skyy", tier=1)
    names = [str(x_) for x_ in C.SUB_NAMES]
    K.eq(names, ["Benches", "Combat", "Gathering"], "R1 the sub tabs (AccCraft.SUB_NAMES)")
    tot = 0
    for sub in range(3):
        h, rs, xs = rows(vc("vc:rows", pr, p, U, "", str(sub)))
        want = list(C.rowsFor(U, k, p, sub))
        K.check(h[0] == "ok" and h[1] == str(sub) and h[2] == str(len(want)) and h[3] == k and h[4] == ",".join(names) and not xs,
                "R1 %s header: ok | sub | %d rows | the profile key | the tab names (%s)" % (names[sub], len(want), h))
        ok = len(rs) == len(want)
        for i_, e_ in enumerate(want):
            ri = [str(x_) for x_ in C.lineRow(U, k, p, e_)]
            r_ = rs[i_] if i_ < len(rs) else []
            rd = C.ridOf(e_)
            can = ri[2].endswith("CAN CRAFT") or ri[2].endswith("CAN UPGRADE")
            cl = lambda t_: t_.replace("|", "/").replace("\n", " ").replace("\r", " ")   # AccPage.vcClean
            one_ = len(r_) == 12 and r_[1] == str(i_) and r_[2] == cl(ri[0]) and r_[3] == cl(ri[1]) and r_[4] == cl(ri[2]) and r_[6] == cl(ri[4]) \
                and r_[7] == ("1" if can else "0") and r_[8] == ri[6] and r_[9] == ("" if rd is None else cl(str(rd))) and r_[10] == cl(ri[7])
            if not one_:
                K.notes.append("R1 %s row %d mismatch: %s vs %s" % (names[sub], i_, r_, ri))
            ok = ok and one_
        K.check(ok, "R1 %s: every row = lineRow (id, name, status, cost, can, mode, recipe id) in the Craft tab's order (%d rows)" % (names[sub], len(rs)))
        tot += len(rs)
    K.check(tot > 0, "R1 there are rows to draw (%d)" % tot)
    h, rs, _x = rows(vc("vc:rows", pr, p, U, "", "9"))
    K.check(h[1] == "0", "R1 an unknown sub = Benches (%s)" % h[1])
    # R2 the Furnace Charm line (Benches) - tier I in the bag = an UPGRADE row to II that can be made
    fr = None
    for sub in range(3):
        for r_ in rows(vc("vc:rows", pr, p, U, "", str(sub)))[1]:
            if r_[9] == rid(2):
                fr = r_
    K.check(fr is not None and fr[8] == "u" and fr[7] == "1" and fr[4].endswith("CAN UPGRADE"), "R2 the Furnace Charm row: Upgrade to II, can make now (%s)" % (fr,))
    # R3 vc:craft = the Craft tab's button (the in-place upgrade)
    r = vc("vc:craft", pr, p, U, k, rid(2))
    K.check(r.startswith("+upgraded to Furnace Charm II") and W.bag(U)[0] == FC[1] and W.count(inv, THOR) == 0 and state() == ({LEAD: 26}, {}),
            "R3 CRAFT on the row = the in-place upgrade: II in slot 0, the Thorium + 64 Lead paid (%s)" % r)
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    r = vc("vc:craft", pr, p, U, k, rid(2))
    K.check(r.startswith("-") and W.slots(inv) == s0 and state() == st0 and W.bag(U) == b0, "R3 the same click again (double click / an old row): refused, nothing used (%s)" % r)
    for bad in ("Some_Old_Recipe", "", "x" * 200):
        r = vc("vc:craft", pr, p, U, k, bad)
        K.check(r.startswith("-") and W.slots(inv) == s0 and state() == st0 and W.bag(U) == b0, "R3 a stale / empty / overlong recipe id %r: refused, nothing used (%s)" % (bad[:20], r))
    # R4 not enough materials
    inv, p, pr, U, k = fresh([], {LEAD: 3}, "Short", tier=1)
    fr = [r_ for sub in range(3) for r_ in rows(vc("vc:rows", pr, p, U, "", str(sub)))[1] if r_[9] == rid(2)]
    K.check(len(fr) == 1 and fr[0][7] == "0" and fr[0][4].endswith("NEEDS MATERIALS"), "R4 the row says NEEDS MATERIALS, can = 0 (%s)" % fr)
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    r = vc("vc:craft", pr, p, U, k, rid(2))
    K.check(r.startswith("-not enough materials") and W.slots(inv) == s0 and state() == st0 and W.bag(U) == b0, "R4 CRAFT without the materials: refused, nothing used (%s)" % r)
    # R5 the profile key + the busy gate
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64)], {LEAD: 90}, "Prof", tier=1)
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    r = vc("vc:craft", pr, p, U, k + "x", rid(2))
    K.check(r.startswith("-Your profile changed") and W.slots(inv) == s0 and state() == st0 and W.bag(U) == b0, "R5 another profile's key: nothing moves (%s)" % r)
    W.bridge.put("profile:busy:" + str(U), "1")
    K.check(vc("vc:rows", pr, p, U, "", "0").startswith("off|your profile is still loading") and vc("vc:craft", pr, p, U, k, rid(2)).startswith("-your profile is still loading")
            and W.bag(U) == b0 and state() == st0, "R5 a busy profile: the rows say so, CRAFT moves nothing")
    W.bridge.remove("profile:busy:" + str(U))
    K.check(str(PG.vc("vc:rows", pr, None, None, None, U, k, "0")).startswith("off|Your player could not be read"), "R5 no player: off")
    # R6 the bridge apply
    fn = BF()
    K.check(str(fn.apply(OBJ(["vc:rows", U, "", "0"]))).startswith("off|You are not online here") and str(fn.apply(OBJ(["vc:craft", U, k, rid(2)]))).startswith("-You are not online"),
            "R6 apply: a player the Universe does not know = off / - (nothing moves)")
    K.eq(str(fn.apply(OBJ(["list", U, k]))), str(A.listK(U, k)), "R6 apply: acc:fn:bag's own 'list' op unchanged")
    K.save()


def run_vc(out, jar, scratch, home):
    T537.run_vc(out, jar, scratch, home)


def run_op036(out, jar, scratch, home):
    T536.run_op(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("vr", run_vr), ("vc", run_vc), ("op036", run_op036), ("live", T534.run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
