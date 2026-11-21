"""Harness for SkyyPets 0.4.28 (pets:fn:tab + pets:fn:tabact for SkyyMenu 0.3.58's one-screen Pets tab; tools/pets_0_4_28_patch.py). Build first:
    python tools/pets_0_4_28_patch.py && python SkyyPets/build_skyypets_0.4.28.py
    python SkyyPets/test_skyypets_0.4.28.py [--keep] [--expect-dump] [--dir <folder inside tools/dev/scratch/>]

  S     static   the patch re-runs to identical bytes; ONE class added (PetTabFn), no system / command / setting; the jar adds only PetTabFn.class,
                 changed non-class entries = manifest.json; both keys published
  A/C/AA         (tools/harness_kit.py, -Xverify:all) verify, class compare 0.4.27 -> 0.4.28, engine-access audit
  TAB   EXECUTED on 0.4.4's stand-in world (real PetStore / PetOps / PetHatchery / PetEgg + the fake inventory and Void):
                 READ    the header (profile token = the profile key, counts, pages, Hatchery slots), the area labels, the two slots, the page of pets
                         rarest first with the approved tooltip and THIS screen's footer, filters (role / area), pages, the selected pet's plain
                         lines (tags, buffs, where, progress, at max, fusing group), eggs held (inventory + Void), the 10 craft rows (Common = craft,
                         Uncommon = upgrade of its Common egg), Hatchery lines; null when Pets is off / a profile switch runs / no player
                 ACT     slot (never a toggle: already there = '='), out, a Bonus pet refused from the mount slot, fuse + rebirth two-press (another
                         op cancels), craft (Common; double click = ONE egg; a full inventory = everything back), upgrade (the Common egg taken
                         once), place (the egg taken once, a free slot), take (two presses, the egg back once), hatch (wrong hid refused; ready ->
                         one pet, the slot free), a wrong / old profile token refused (nothing moves), the 350 ms same-op guard, unknown op
                 APPLY   non-UUID / no player = null; the TEST_INV seam; mode 1 needs { UUID, token, op, arg }
                 FIX     (round tab2fix) a two-press ask older than 15 s asks again (never fuses / takes); the screen's first read (arg 7 = 1)
                         clears a pending ask, a later read keeps it; Take out on a ready egg = "press Hatch" (nothing moves); the craft cost
                         line = "Name have/need" (have capped at need, no "(need N)", an upgrade's own egg left out)
  the 0.4.27 phases (SUMMON / PETSLOT / EGGS / IDLE / AGG / REAL / MIG / ECS / PT / live / live2) run again on this jar.
Exit code 1 on any failure.
"""
import os, sys, zipfile, importlib.util, subprocess, inspect, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
if "--dir" not in sys.argv:
    sys.argv += ["--dir", os.path.join(TOOLS, "dev", "scratch", "tab2", "pets")]
import skyybuild as B
import harness_kit as HK

_cmp0 = HK.run_compare
_eq00 = HK.Child.eq


def _mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    a = list(sys.argv)
    s.loader.exec_module(m)
    sys.argv[:] = a
    return m


T427 = _mod(os.path.join(HERE, "test_skyypets_0.4.27.py"), "test_skyypets_0_4_27")
HK.run_compare = _cmp0
HK.Child.eq = _eq00
T425, T424, T423, T417, T44, T41 = T427.T425, T427.T424, T427.T423, T427.T417, T427.T44, T427.T41

VERSION = "0.4.28"
PKG = "com.skyy.pets."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.4.27.jar")
GEN = os.path.join(HERE, "build_skyypets_%s.py" % VERSION)
GEN_OLD = os.path.join(HERE, "build_skyypets_0.4.27.py")
PATCH = os.path.join(TOOLS, "pets_0_4_28_patch.py")
SCRATCH = os.path.abspath(HK.arg("--dir"))
T427.JAR = T425.JAR = T424.JAR = T423.JAR = JAR
ADDED = ["PetTabFn"]
EXPECT = {   # 0.4.28 changes only the version text baked into the config kit + migration lines, and the setup (the two keys)
    'CfgFn': ['~m opExport'], 'CfgRows': ['~<clinit>', '~m header'], 'PetsCfg': ['~m applyAll', '~m seed'], 'PetsMigDrg': ['~m run'],
    'PetsMigP5': ['~m mgLog', '~m run'], 'PetsMigS2': ['~m run'], 'PetsMigW15': ['~m run'], 'SkyyPetsPlugin': ['~m setup'],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
# the 0.4.27 MIG phase names its version in the Changes line it expects: the same phase with this version
_t425 = open(T425.__file__, encoding="utf8").read()          # (T427 already re-compiled run_mig, so getsource would point at the wrong lines)
_src = _t425[_t425.index("def run_mig("):_t425.index("\ndef ", _t425.index("def run_mig(")) + 1]
for _old in (r"\tSkyyPets 0.4.25\t", r"\tSkyyPets 0.4.27\t"):
    if _src.count(_old) == 1:
        exec(compile(_src.replace(_old, r"\tSkyyPets 0.4.28\t"), T425.__file__, "exec"), T425.__dict__)
        break
else:
    raise AssertionError("0.4.25's MIG phase changed")


# ======================================================================================================== S: static
def run_static(out, jar, scratch, home):
    K = HK.Child(out)
    g = open(GEN, encoding="utf8", newline="").read()
    o = open(GEN_OLD, encoding="utf8", newline="").read()
    K.check(g.startswith('"""SkyyPets 0.4.28 - build script') and g.count('VERSION = "0.4.28"') == 1, "S header + VERSION")
    K.check(g.count("registerCommand(") == o.count("registerCommand(") and g.count("registerSystem(") == o.count("registerSystem("), "S no system or command added")
    K.eq(g.count("= cls(") - o.count("= cls("), 1, "S one class added (PetTabFn)")
    K.check(("\r\n" in g) == ("\r\n" in o), "S line endings kept")
    K.check(g.count("CfgRow(") == o.count("CfgRow(") if "CfgRow(" in o else True, "S no setting added")
    d = os.path.join(scratch, "static")
    os.makedirs(d, exist_ok=True)
    cp = os.path.join(d, os.path.basename(GEN))
    p = subprocess.run([sys.executable, PATCH, "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(GEN, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    K.check('bridge().put("pets:fn:tab", new @PKG@.PetTabFn(0));' in g and 'bridge().put("pets:fn:tabact", new @PKG@.PetTabFn(1));' in g
            and 'bridge().put("pets:fn:ride", new @PKG@.PetRideFn());' in g, "S pets:fn:tab + pets:fn:tabact published (pets:fn:ride stays)")
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    nn, on = set(zn.namelist()), set(zo.namelist())
    K.eq(sorted(nn - on), ["com/skyy/pets/PetTabFn.class"], "S the jar adds only PetTabFn.class")
    K.eq(sorted(on - nn), [], "S the jar removes nothing")
    K.eq(sorted(n for n in nn & on if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json (no item / recipe / lang file changed)")
    K.save()


# ======================================================================================================== TAB: the two keys, executed
def run_tab(out, jar, scratch, _home):
    W = T424._world(out, jar, scratch, "tab")
    K, JClass, JProxy = W["K"], W["JClass"], W["JProxy"]
    Hy, Egg, V, Ops, Store, Cfg = W["PetHatchery"], W["PetEgg"], W["V"], W["PetOps"], W["PetStore"], W["PetsCfg"]
    TF = JClass(PKG + "PetTabFn")
    Inv, pi = T41.Inv, T41.proxy_inv
    T427._tells(W)
    EC, EU = "Skyy_PetEgg_Mining_Common", "Skyy_PetEgg_Mining_Uncommon"
    NL = chr(31)
    u, k, r = T44._mk(W, 951)
    wolves = [str(Ops.createR(r, None, "Wolf", 3, 10 + i, 0, 0, "test", "harness", False)) for i in range(4)]
    rab = str(Ops.createR(r, None, "Rabbit", 1, 5, 0, 0, "test", "harness", False))
    Store.save(r)
    inv = Inv({"Food_Egg": 3, "Skyy_Ench_Cobblestone": 24})

    def rd(sel="", role=0, area=0, page=0, per=42, esel="", iv=None):
        s_ = TF.read(u, sel, role, area, page, per, esel, pi(iv if iv is not None else inv))
        return None if s_ is None else str(s_)

    def lines(s_, pre):
        return [l_.split("|") for l_ in s_.split("\n") if l_.startswith(pre + "|")]

    def act(op, arg, iv=None, tok=None, clear=True):
        if clear:
            TF.LAST.clear()
            Hy.CLICK.clear()
            Egg.HATCHING.clear()
        return str(TF.act(u, k if tok is None else tok, op, arg, "harness", pi(iv if iv is not None else inv), None, None, None))
    def settle():
        """the player save after an egg move (the 0.4.4 DUPE phase's way): the open debts / credits done, the file saved, one tick"""
        for kk in list(r.keysWith("eggdebt.")) + list(r.keysWith("eggcredit.")):
            Egg.DONE.put(str(kk).split(".", 1)[1], W["Long"](W["now"]()))
        inv.psave()
        T44._tick(W, u, r, inv)
    # READ
    s = rd()
    K.check(s is not None and s.startswith("ok|%s|5|" % k), "TAB READ the header: ok, the profile token = the profile key, 5 pets: %s" % (s or "")[:80])
    hd = s.split("\n")[0].split("|")
    K.eq(len(hd), 15, "TAB READ the header has 15 fields (SkyyMenu 0.3.58 reads 15)")
    K.eq([x[2] for x in lines(s, "a")], ["All", "Combat", "Farming", "Mining", "Foraging", "Fishing", "Exploration", "Cooking"], "TAB READ the area labels")
    ps = lines(s, "p")
    K.check(len(ps) == 5 and [x[1] for x in ps][:4] == sorted(wolves, key=lambda w_: -int(r.levelOf(w_))) and ps[4][1] == rab,
            "TAB READ the page: rarest first (the 4 Rare Wolves, the most grown first), then the Common Rabbit: %s" % [x[1] for x in ps])
    tip0 = "|".join(ps[0][7:])
    K.check("Click: select it" in tip0 and "Click: put it in your pet slot" not in tip0 and NL in tip0 and "\n" not in tip0 and "BUFFS NOW" in tip0,
            "TAB READ each pet carries the approved sectioned tooltip with this screen's footer (newlines as char 31)")
    d = lines(s, "d")
    K.check(len(d) == 1 and d[0][1] == (str(r.active(1)) or ps[0][1]) and "FIGHTER" in d[0][9] and len(lines(s, "b")) >= 1 and len(lines(s, "w")) == 3 and len(lines(s, "g")) == 2 and len(lines(s, "t")) == 1,
            "TAB READ the selected pet (default = the first shown): tags, buffs, where x3, progress x2, at max: %s" % (d[:1],))
    f = lines(s, "f")
    K.check(len(f) == 1 and f[0][1] == "4" and len(lines(s, "fo")) == 4 and len(lines(s, "fr")) == 1, "TAB READ fusing: 4 of the same Rare Wolf, the group icons, the result: %s" % f)
    cs = lines(s, "c")
    K.check(len(cs) == 10 and [x[6] for x in cs].count("0") == 5 and all(x[8] == x[2].replace("_Uncommon", "_Common") for x in cs if x[6] == "1"),
            "TAB READ the craft rows: 5 Common crafts + 5 Uncommon upgrades, each upgrade names its Common egg")
    _cc, _cu = [x for x in cs if x[2] == EC][0], [x for x in cs if x[2] == EU][0]
    _pp = [q_.rsplit(" ", 1)[1].split("/") for q_ in _cc[7].split(" + ")]
    K.check(_cc[5] == "1" and _cu[5] == "0" and "(need" not in _cc[7] + _cu[7] and _pp and all(int(h_) <= int(n_) for h_, n_ in _pp)
            and _cc[7].split(" + ")[0].endswith(" 1/1") and _cu[7] == "Enchanted Iron Ingot 0/2",
            "TAB FIX can-craft + the short cost line 'Name have/need' (have capped at need): %s | %s" % (_cc[7], _cu[7]))
    K.check(len(lines(s, "h")) == int(hd[10]) and all(x[2] == "empty" for x in lines(s, "h")), "TAB READ the Hatchery lines (all empty)")
    K.check(len(lines(rd(role=1), "p")) == 1 and len(lines(rd(role=2), "p")) == 4 and len(lines(rd(per=2, page=1), "p")) == 2 and rd(per=2, page=9).split("\n")[0].split("|")[7] == "2",
            "TAB READ filters (Bonus = the Rabbit, Fighter = the Wolves) and pages (2 a page, a page past the end = the last)")
    s2 = rd(sel=rab)
    K.check(lines(s2, "d")[0][1] == rab and "BONUS" in lines(s2, "d")[0][9], "TAB READ a selected id = its detail")
    # APPLY
    F0, F1 = TF(0), TF(1)
    K.check(F0.apply("x") is None and F0.apply(JClass("java.lang.Object[]")([u])) is None and F1.apply(JClass("java.lang.Object[]")([u, k, "out", "1"])) is None,
            "TAB APPLY a non-UUID / no player on this thread = null")
    TF.TEST_INV = JProxy("java.util.function.Function", dict={"apply": lambda uu: pi(inv)})
    a0 = F0.apply(JClass("java.lang.Object[]")([u, "", JClass("java.lang.Integer")(0), JClass("java.lang.Integer")(0), JClass("java.lang.Integer")(0),
                                                JClass("java.lang.Integer")(42), ""]))
    K.check(a0 is not None and str(a0).startswith("ok|"), "TAB APPLY mode 0 with a player (the TEST_INV seam) = the lines")
    _I = JClass("java.lang.Integer")
    TF.CONF.put(u, "fuse|x|1|y" + chr(30) + str(int(time.time() * 1000)))
    F0.apply(JClass("java.lang.Object[]")([u, "", _I(0), _I(0), _I(0), _I(42), "", _I(0)]))
    _kept = TF.CONF.get(u) is not None
    F0.apply(JClass("java.lang.Object[]")([u, "", _I(0), _I(0), _I(0), _I(42), "", _I(1)]))
    K.check(_kept and TF.CONF.get(u) is None, "TAB FIX a later read keeps a pending two-press ask; the screen's FIRST read (arg 7 = 1) clears it")
    TF.LAST.clear()
    a1 = F1.apply(JClass("java.lang.Object[]")([u, k, "out", "1"]))
    K.check(a1 is not None and (str(a1) == "-That slot is empty." or str(a1).endswith("left your pet slot.")) and str(r.active(1)) == "", "TAB APPLY mode 1 = act (%s)" % a1)
    K.check(F1.apply(JClass("java.lang.Object[]")([u, k])) is None, "TAB APPLY mode 1 without op = null")
    TF.TEST_INV = None
    # ACT: slots
    m = act("slot", wolves[0] + "|1", tok="old-profile")
    K.check(m.startswith("=Your profile changed") and str(r.active(1)) == "", "TAB SAFE a wrong profile token: refused, nothing moves (%s)" % m)
    m = act("slot", wolves[0] + "|1")
    K.check(m.startswith("+") and str(r.active(1)) == wolves[0], "TAB ACT slot <id>|1 = into the pet slot (%s)" % m)
    m = act("slot", wolves[0] + "|1", clear=False)
    K.eq(m, "=One moment.", "TAB SAFE the same op again within 350 ms = '=One moment.' (a double click never runs twice)")
    m = act("slot", wolves[0] + "|1")
    K.check(m.startswith("=That pet is already in your pet slot") and str(r.active(1)) == wolves[0], "TAB ACT slot on the same slot = '=' (never a toggle)")
    m = act("slot", rab + "|2")
    K.check(m.startswith("-") and str(r.active(2)) == "", "TAB ACT a Bonus pet into the mount slot = refused (%s)" % m)
    m = act("out", "1")
    K.check(m.startswith("+") and str(r.active(1)) == "", "TAB ACT out 1 = the pet slot empty (%s)" % m)
    K.check(act("out", "3").startswith("-There is no such slot") and act("nope", "").startswith("-Unknown"), "TAB ACT a bad slot / an unknown op = '-'")
    # fuse: two presses, another op cancels
    n0 = int(r.count())
    m1 = act("fuse", wolves[0])
    m2 = act("out", "2")
    m3 = act("fuse", wolves[0])
    K.check(m1.startswith("=") and m3.startswith("=") and int(r.count()) == n0, "TAB ACT fuse: the first press asks; another op in between cancels (asks again): %s" % m1[:80])
    m4 = act("fuse", wolves[0])
    K.check(m4.startswith("+") and int(r.count()) == n0 - 3, "TAB ACT fuse twice = 4 Rare Wolves -> 1 Epic (%s)" % m4[:80])
    K.check(act("reb", rab).startswith("-") or act("reb", rab).startswith("="), "TAB ACT rebirth below max level = refused / asks (SkyyPets' rule)")
    # craft: double click, full inventory
    m = act("craft", EC)
    K.check(m.startswith("+Crafted a Common Mining Egg") and inv.count(EC) == 1 and inv.count("Food_Egg") == 2, "TAB ACT craft a Common egg (the craft door): %s" % m)
    m2 = act("craft", EC, clear=False)
    K.check(m2 == "=One moment." and inv.count(EC) == 1, "TAB SAFE a double-clicked craft = ONE egg")
    invF = Inv({"Food_Egg": 1, "Skyy_Ench_Cobblestone": 12}, refuse={EC})
    m = act("craft", EC, iv=invF)
    K.check(m.startswith("-No room") and invF.live == {"Food_Egg": 1, "Skyy_Ench_Cobblestone": 12} and invF.count(EC) == 0, "TAB SAFE a full inventory: everything back (%s)" % m)
    K.check(act("craft", "Rock_Stone").startswith("-That egg cannot be crafted"), "TAB ACT craft of a non-egg = refused")
    invU = Inv({EC: 1, "Skyy_Ench_Iron": 2})
    m = act("craft", EU, iv=invU)
    K.check(m.startswith("+Upgraded") and invU.count(EC) == 0 and invU.count(EU) == 1 and invU.count("Skyy_Ench_Iron") == 0, "TAB ACT the upgrade = the Common egg + materials taken once: %s" % m)
    # the Hatchery: place / take (two presses) / hatch
    m = act("place", EC)
    K.check(m.startswith("+") and inv.count(EC) == 0 and int(Hy.used(r)) == 1, "TAB ACT place = the egg taken once into a free slot: %s" % m)
    h = lines(rd(), "h")
    hl = [x for x in h if x[2] in ("wait", "ready")]
    K.check(len(hl) == 1 and hl[0][3] == EC and hl[0][8] != "", "TAB READ the placed egg's line (state, egg, hid): %s" % hl)
    n_, hid = hl[0][1], hl[0][8]
    m1 = act("take", n_ + "|" + hid)
    K.check(m1.startswith("=Take the") and inv.count(EC) == 0 and int(Hy.used(r)) == 1, "TAB ACT take: the first press asks")
    settle()
    _c = str(TF.CONF.get(u))
    TF.CONF.put(u, _c.rsplit(chr(30), 1)[0] + chr(30) + str(int(time.time() * 1000) - 16000))
    mx = act("take", n_ + "|" + hid)
    K.check(mx.startswith("=Take the") and inv.count(EC) == 0 and int(Hy.used(r)) == 1 and int(TF.CONF_MS) == 15000,
            "TAB FIX an ask older than 15 s never confirms: the press asks again, the egg stays in its slot (%s)" % mx[:60])
    m2 = act("take", n_ + "|" + hid)
    K.check(m2.startswith("+") and inv.count(EC) == 1 and int(Hy.used(r)) == 0, "TAB ACT take twice = the egg back once, the slot free: %s" % m2)
    settle()
    m = act("place", EC)
    settle()
    h = [x for x in lines(rd(), "h") if x[2] in ("wait", "ready")][0]
    K.check(act("hatch", h[1] + "|nothid").startswith("=That slot changed") and act("hatch", h[1] + "|" + h[8]).startswith("-Still hatching"),
            "TAB ACT hatch: a wrong hid = refused; not ready = refused")
    Hy.CLOCK_OFF = 3 * 3600 * 1000
    TF.CONF.put(u, "take|%s|%s" % (h[1], h[8]) + chr(30) + str(int(time.time() * 1000)))
    mr = act("take", h[1] + "|" + h[8])
    K.check(mr.startswith("=It is ready now") and TF.CONF.get(u) is None and int(Hy.used(r)) == 1 and inv.count(EC) == 0,
            "TAB FIX Take out on an egg that became ready (even with a pending ask) = 'press Hatch', nothing moves, the ask cleared (%s)" % mr)
    np0 = int(r.count())
    m = act("hatch", h[1] + "|" + h[8])
    Hy.CLOCK_OFF = 0
    K.check(m.startswith("+") and int(r.count()) == np0 + 1 and int(Hy.used(r)) == 0 and inv.count(EC) == 0, "TAB ACT hatch (no reel page here = the reveal) = one pet, the slot free: %s" % m[:80])
    # profile switch / busy / off
    W["keys"][str(u)] = "otherprofile"
    m = act("craft", EC)
    K.check(m.startswith("=Your profile changed") and inv.count(EC) == 0, "TAB SAFE a profile switch between the read and the click: refused, nothing moves")
    W["keys"].pop(str(u), None)
    W["BR"].put("profile:busy:" + str(u), W["Bool"].TRUE)
    K.check(rd() is None and act("craft", EC).startswith("=Your profile is switching"), "TAB SAFE while a profile switch runs: read = null, act refused")
    W["BR"].remove("profile:busy:" + str(u))
    Cfg.ON = False
    K.check(rd() is None and act("craft", EC).startswith("-Pets are switched off"), "TAB Pets off: read = null, act refused")
    Cfg.ON = True
    K.notes.append("TAB counters: reads %d acts %d stale %d guard %d" % (int(TF.READS.get()), int(TF.ACTS.get()), int(TF.STALE.get()), int(TF.GUARD.get())))
    K.save()


if __name__ == "__main__":
    P_ = T427._phase
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[P_("static", run_static), P_("tab", run_tab), P_("summon", T427.run_summon), P_("petslot", T427.run_petslot), P_("eggs", T427.run_eggs),
                   P_("idle", T427._petslot(T425.run_idle)), P_("agg", T427._petslot(T425.run_agg)), P_("real", T425.run_real), P_("mig", T425.run_mig),
                   P_("ecs", T424.run_ecs), P_("pt", T425._old(T423.run_pt)),
                   P_("live", T417.run_live), P_("live2", T425.run_live2)],
           script=__file__, live=(T423.T422.T421.T41.LIVE, "Skyy_SkyyPets"))
