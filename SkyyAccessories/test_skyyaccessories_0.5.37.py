"""Harness for SkyyAccessories 0.5.37 (acc:fn:charms - the Charms panel bridge for SkyyMenu 0.3.54; tools/accessories_0_5_37_patch.py). Build first:
    python tools/accessories_0_5_37_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.37.py
    python SkyyAccessories/test_skyyaccessories_0.5.37.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  S     static   the patch re-runs to identical bytes; 0.5.36's patch still regenerates 0.5.36; no new system / command / class; line endings
                 kept; the jar: no entry added / removed, the only changed non-class entry = manifest.json; acc:fn:charms put + removed once
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.5.36 -> 0.5.37 (AccPage + AccBagFn + the version texts)
  VC    EXECUTED with the real AccPage.vc / AccCraft step / row / craft / AccStore on real engine containers (the 0.5.18 World stand-in +
                 0.5.36's stand-in SkyySacks): vc:list (header, charms, a second copy marked, totals, the picked charm + its costs in the
                 '(need N more)' style), TIER UP (the in-place upgrade; a stale recipe id, a double click, not the best copy, not enough
                 materials = nothing used), TAKE OUT (back to the inventory; again = refused; a full inventory = it stays in its slot),
                 PUT IN (Equip rules: a second same charm refused, not a charm, not carried), a PROFILE switch (another key = nothing moves),
                 the profile busy gate, the bridge apply (a player not online, bad args, acc:fn:bag's own 'list' op unchanged)
  OP036 0.5.36's Enchanted Craft-row checks again on this jar
  LIVE  start twice on a scratch COPY of Skyy's live NewBetaTest Skyy_SkyyAccessories (start 2 changes nothing)
  AA    engine-access audit
NOT COVERED (UNVERIFIED in game): the real world thread call from SkyyMenu's page (Store.isInThread on a live world); the panel render.
Scratch: tools/dev/scratch/inv5/acc (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, subprocess, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(ROOT, "tools", "dev", "scratch", "inv5", "acc")]
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


T536 = _mod(os.path.join(HERE, "test_skyyaccessories_0.5.36.py"), "test_skyyaccessories_0_5_36")
T534, T22 = T536.T534, T536.T22
HK.run_compare = _cmp0
HK.Child = _chd0
HK.Child.eq = _eq00

VERSION, OLD = "0.5.37", "0.5.36"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-%s.jar" % OLD)
GEN = os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyyaccessories_%s.py" % OLD)
PATCH = os.path.join(ROOT, "tools", "accessories_0_5_37_patch.py")
PKG = "com.skyy.accessories."
SCRATCH = os.path.abspath(HK.arg("--dir"))
LIVE_DIR = T534.LIVE_DIR
EXPECT = {
    "AccPage": ["+m vc", "+m vcClean", "+m vcInt", "+m vcList", "+m vcPut", "+m vcSel", "+m vcTake", "+m vcTier"],
    "AccBagFn": ["+m vcApply", "~m apply"],
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyyAccessoriesPlugin": ["~m setup", "~m shutdown"],          # the version texts + the key
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
FC, THOR, LEAD = T536.FC, T536.THOR, T536.LEAD
SPD = "Skyy_Talisman_Speed_Common"


def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyAccessories 0.5.37 - build script') and g.count('VERSION = "0.5.37"') == 1, "S header + VERSION")
    K.check("MERGE 3 and UPGRADE BAG (approved art) are NOT built" in g, "S the not-built parts are written in the script notes")
    for w in ("registerSystem(", "registerCommand(", "makeClass("):
        K.check(g.count(w) == o.count(w), "S no new %s" % w)
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.eq((g.count('bridge().put("acc:fn:charms"'), g.count('bridge().remove("acc:fn:charms")')), (1, 1), "S acc:fn:charms published once, removed once at shutdown")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    for patch, ref in ((PATCH, GEN), (os.path.join(ROOT, "tools", "accessories_0_5_36_patch.py"), GEN_OLD)):
        cp = os.path.join(d, os.path.basename(ref))
        p = subprocess.run([sys.executable, patch, "--out", cp], capture_output=True, text=True)
        K.check(p.returncode == 0 and open(cp, "rb").read() == open(ref, "rb").read(), "S %s re-generates its script byte for byte: %s" % (os.path.basename(patch), p.stderr[-300:]))
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn ^ on), [], "S the jar adds / removes no entry")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


def run_vc(out, jar, scratch, _home):
    K = HK.Child(out)
    T22.JAR = jar
    M = T22.m18()
    W = M.World(os.path.join(scratch, "vc"))
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

    def parse(r):
        ls = r.split("\n")
        out_ = {"h": ls[0].split("|"), "c": {}, "t": [], "s": None, "n": []}
        for l_ in ls[1:]:
            f_ = l_.split("|")
            if f_[0] == "c":
                out_["c"][int(f_[1])] = f_
            elif f_[0] == "t":
                out_["t"].append(f_)
            elif f_[0] == "s":
                out_["s"] = f_
            elif f_[0] == "n":
                out_["n"].append(f_)
        return out_

    def state():
        return dict((a, b) for a, b in V["n"].items() if b), dict((a, b) for a, b in V["owe"].items() if b)

    def rid(t):
        return FC[t - 1] + "_Recipe_SkyyCharm"

    # V1 the list: three charms (a second copy of Furnace Charm I), the totals, the picked charm + its costs
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64)], {LEAD: 90}, "Skyy", tier=1)
    A.putK(U, k, 3, FC[0])
    A.putK(U, k, 5, SPD)
    L = parse(vc("vc:list", pr, p, U, "", ""))
    K.check(L["h"][0] == "ok" and L["h"][1] == "3" and int(L["h"][2]) >= 1 and int(L["h"][3]) == 60 and L["h"][5] == k,
            "V1 header: ok | 3 used | cap | bag length 60 | AP | the profile key (%s)" % L["h"])
    K.check(sorted(L["c"]) == [0, 3, 5] and L["c"][0][2] == FC[0] and L["c"][5][2] == SPD and L["c"][0][4] == str(D.pretty(FC[0])),
            "V1 one c line per charm with its slot, id, name (%s)" % sorted(L["c"]))
    K.check(int(L["c"][0][3]) >= 0 and int(L["c"][3][3]) < 0, "V1 the second copy of Furnace Charm I is marked not counting (AP %s / %s)" % (L["c"][0][3], L["c"][3][3]))
    K.check([t_[1] for t_ in L["t"]] == [x_ for x_ in [str(y_) for y_ in D.bonusRows(A.slotsK(U, k))][0::2] if x_] and any(t_[1] == "Furnace Charm" for t_ in L["t"]),
            "V1 the totals = AccDefs.bonusRows (ALL CHARMS TOGETHER): %s" % [t_[1] for t_ in L["t"]])
    K.check(L["s"] is None, "V1 nothing picked = no detail")
    L = parse(vc("vc:list", pr, p, U, "", "0|" + FC[0]))
    s_ = L["s"] or []
    K.check(len(s_) == 10 and s_[3] == "u" and s_[4] == rid(2) and s_[5].endswith("CAN UPGRADE") and s_[8] == str(C.accName(FC[1])),
            "V1 the picked Furnace Charm I: mode u, the next step's recipe id, CAN UPGRADE, next = Furnace Charm II (%s)" % s_)
    K.check(L["n"] and L["n"][0][2].startswith("this ") and all(n_[1] == "1" for n_ in L["n"]) and len(L["n"]) >= 3,
            "V1 the costs: the charm itself, then each material, all met (%s)" % L["n"])
    K.check(parse(vc("vc:list", pr, p, U, "", "0|Wrong_Id"))["s"] is None and parse(vc("vc:list", pr, p, U, "", "77|" + FC[0]))["s"] is None,
            "V1 a pick that does not match the slot = no detail")
    # V2 TIER UP with a stale recipe id: nothing used
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    r = vc("vc:tier", pr, p, U, k, "0|%s|%s" % (FC[0], "Some_Old_Recipe"))
    K.check(r.startswith("-That charm changed") and W.slots(inv) == s0 and state() == st0 and W.bag(U) == b0, "V2 a stale recipe id: refused, nothing used (%s)" % r)
    # V3 TIER UP: the Craft tab's in-place upgrade
    r = vc("vc:tier", pr, p, U, k, "0|%s|%s" % (FC[0], rid(2)))
    K.check(r.startswith("+upgraded to Furnace Charm II") and W.bag(U)[0] == FC[1] and W.count(inv, THOR) == 0 and state() == ({LEAD: 26}, {}),
            "V3 TIER UP = the in-place upgrade: slot 0 holds II, the Thorium + 64 Lead paid, the Void settled (%s)" % r)
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    r = vc("vc:tier", pr, p, U, k, "0|%s|%s" % (FC[0], rid(2)))
    K.check(r.startswith("-That charm moved") and W.slots(inv) == s0 and state() == st0 and W.bag(U) == b0, "V3 the same click again (double click): refused, nothing used (%s)" % r)
    # V4 not the best copy
    L = parse(vc("vc:list", pr, p, U, "", "3|" + FC[0]))
    K.check(L["s"] is not None and L["s"][3] == "x" and "Not counting" in L["s"][5], "V4 the lower copy: mode x, 'Not counting' (%s)" % (L["s"],))
    r = vc("vc:tier", pr, p, U, k, "3|%s|%s" % (FC[0], rid(2)))
    K.check(r.startswith("-Only your best") and W.bag(U) == b0 and state() == st0, "V4 tier up on the lower copy: refused, nothing used (%s)" % r)
    # V5 not enough materials
    inv, p, pr, U, k = fresh([], {LEAD: 3}, "Short", tier=1)
    L = parse(vc("vc:list", pr, p, U, "", "0|" + FC[0]))
    K.check(L["s"][3] == "u" and L["s"][5].endswith("NEEDS MATERIALS") and any(n_[1] == "0" and "more)" in n_[2] for n_ in L["n"]),
            "V5 the detail says NEEDS MATERIALS and '(need N more)' (%s)" % L["n"])
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    r = vc("vc:tier", pr, p, U, k, "0|%s|%s" % (FC[0], L["s"][4]))
    K.check(r.startswith("-not enough materials") and W.slots(inv) == s0 and state() == st0 and W.bag(U) == b0, "V5 refused, nothing used (%s)" % r)
    # V6 TAKE OUT
    inv, p, pr, U, k = fresh([], {}, "Take", tier=1)
    A.putK(U, k, 3, SPD)
    r = vc("vc:take", pr, p, U, k, "3|" + SPD)
    K.check(r.startswith("+Took out") and W.count(inv, SPD) == 1 and W.bag(U)[3] is None, "V6 TAKE OUT: in the inventory, the slot empty (%s)" % r)
    r = vc("vc:take", pr, p, U, k, "3|" + SPD)
    K.check(r.startswith("-That charm moved") and W.count(inv, SPD) == 1, "V6 again (double click): refused, no second item (%s)" % r)
    r = vc("vc:take", pr, p, U, k, "0|" + SPD)
    K.check(r.startswith("-That charm moved") and W.bag(U)[0] == FC[0], "V6 a slot that holds another charm: refused (%s)" % r)
    inv, p, pr, U, k = fresh([], {}, "Full", tier=1, fill="Junk_One")
    s0, b0 = W.slots(inv), W.bag(U)
    r = vc("vc:take", pr, p, U, k, "0|" + FC[0])
    K.check(r.startswith("-Your inventory is full") and W.slots(inv) == s0 and W.bag(U) == b0, "V6 a full inventory: the charm stays in its slot, nothing lost (%s)" % r)
    # V7 PUT IN (a charm dragged from the bag)
    inv, p, pr, U, k = fresh([("s", 0, SPD, 1), ("s", 1, SPD, 1), ("s", 2, "Junk_One", 1)], {}, "Put")
    r = vc("vc:put", pr, p, U, k, SPD)
    K.check(r.startswith("+Put") and SPD in W.bag(U) and W.count(inv, SPD) == 1, "V7 PUT IN: in Void Charms, one left in the inventory (%s)" % r)
    r = vc("vc:put", pr, p, U, k, SPD)
    K.check(r.startswith("-Void Charms is full, or the same or a better") and W.count(inv, SPD) == 1 and W.bag(U).count(SPD) == 1, "V7 the same charm again: refused, kept (%s)" % r)
    K.check(vc("vc:put", pr, p, U, k, "Junk_One").startswith("-Only charms") and W.count(inv, "Junk_One") == 1, "V7 not a charm: refused")
    K.check(vc("vc:put", pr, p, U, k, "Skyy_Talisman_Vitality_Common").startswith("-Could not find"), "V7 a charm you do not carry: refused")
    # V8 the profile key + the busy gate
    inv, p, pr, U, k = fresh([("s", 0, THOR, 64)], {LEAD: 90}, "Prof", tier=1)
    s0, st0, b0 = W.slots(inv), state(), W.bag(U)
    for op_, arg_ in (("vc:take", "0|" + FC[0]), ("vc:tier", "0|%s|%s" % (FC[0], rid(2))), ("vc:put", SPD)):
        r = vc(op_, pr, p, U, "another-profile", arg_)
        K.check(r.startswith("-Your profile changed") and W.slots(inv) == s0 and state() == st0 and W.bag(U) == b0, "V8 %s with another profile's key: nothing moves (%s)" % (op_, r))
    W.bridge.put("profile:busy:" + str(U), "1")
    K.check(vc("vc:list", pr, p, U, "", "").startswith("off|your profile is still loading") and vc("vc:take", pr, p, U, k, "0|" + FC[0]).startswith("-your profile is still loading")
            and W.bag(U) == b0, "V8 a busy profile: the list says so, an action moves nothing")
    W.bridge.remove("profile:busy:" + str(U))
    K.check(vc("vc:nope", pr, p, U, k, "").startswith("-Void Charms does not know") and str(PG.vc("vc:list", pr, None, None, None, U, k, "")).startswith("off|Your player could not be read"),
            "V8 an unknown op / no player: refused")
    # V9 the bridge apply
    fn = BF()
    K.check(str(fn.apply(OBJ(["vc:list", U, "", ""]))).startswith("off|You are not online here") and str(fn.apply(OBJ(["vc:take", U, k, "0|x"]))).startswith("-You are not online"),
            "V9 apply: a player the Universe does not know = off / - (nothing moves)")
    K.check(fn.apply("x") is None and fn.apply(OBJ(["vc:list"])) is None, "V9 apply: bad arguments = null")
    K.eq(str(fn.apply(OBJ(["list", U, k]))), str(A.listK(U, k)), "V9 apply: acc:fn:bag's own 'list' op unchanged")
    K.check(fn.apply(OBJ(["list", U, "another"])) is None, "V9 apply: acc:fn:bag's key check unchanged")
    K.save()


def run_op036(out, jar, scratch, home):
    T536.run_op(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("static", run_static), ("vc", run_vc), ("op036", run_op036), ("live", T534.run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
