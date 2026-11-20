"""Harness for SkyySacks 0.8.39 (round inv6 - tools/sacks_0_8_39_patch.py: the pocket panel's Upgrades link + Auto-compact toggle for SkyyMenu
0.3.55's inventory). Build first:
    python tools/sacks_0_8_39_patch.py && python SkyySacks/build_skyysacks_0.8.39.py

    python SkyySacks/test_skyysacks_0.8.39.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A / C   verify (-Xverify:all) + compare 0.8.38 -> 0.8.39 (SackBridge.pocketAct / openPocket, SackFn.apply and the version lines only)
  P39     EXECUTED on the 0.8.0 Void stand-ins (the REAL SackPool / VoidStore / VoidCompact / SackBridge / SackFn): every 0.8.38 P38 case
          first (regression), then
          STATE   sacks:fn:pocket cmpst: "=b" not bought, "=1" bought + on, "=0" paused, "=-" a bag with no Enchanted form (Fishing),
                  "=x" Server Setup pd.compact.on OFF; unknown pocket refused; no player on this thread = null
          TOGGLE  cmp on a bag not bought = "-Buy Auto-compact ... first" (nothing written, NO coin taken - buying stays on the Void page);
                  bought: Pause (comp.off written, "=Auto-compact paused"), Turn on ("+Auto-compact is on again", runNow); every item
                  counted (loose + 100 x Enchanted) the same before and after; another profile's token = "-Your profile changed",
                  nothing toggled; the right token toggles; FIX: no token or pd.compact.on OFF = refused
          OPEN    sacks:fn:openPocket: not a UUID / too few arguments / an unknown pocket / no player on this thread = FALSE
  F37 / S36 / BC36 / ALL35   the 0.8.37, 0.8.36 and 0.8.35 cases on THIS jar (regression)
  D       start twice on a scratch COPY of NewBetaTest's Skyy_SkyySacks: no migration, no byte changed
Exit code 1 on any failure.
"""
import os, sys, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_38", os.path.join(HERE, "test_skyysacks_0.8.38.py"))
T38 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T38)
sys.argv = _argv
HK.run_compare = _RC
T37 = T38.T37
T36, T35, T089, T30, BETA = T37.T36, T37.T35, T37.T089, T37.T30, T37.BETA

VERSION = "0.8.39"
OLD_VERSION = "0.8.38"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
T30.OLD_JAR = OLD_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "inv6", "sacks")))
PKG = "com.skyy.sacks."
EXPECT = {"SkyySacksPlugin": ["~m setup"], "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],
          "SackBridge": ["~m pocketAct", "+m openPocket"], "SackFn": ["~m apply"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
LEAD, IRON_E, IRON_B = T36.LEAD, T36.IRON_E, T36.IRON_B
ORE = "Ore_Copper"


def cases39(K, L, scratch):
    T38.cases38(K, L, scratch)   # every 0.8.38 pocket case on this jar first
    from jpype import JClass, JString, JArray
    VS, Defs, Pool = L["VS"], L["Defs"], L["Pool"]
    fresh, write_pool, player, drain, coll, custom_item = (L[n] for n in ("fresh", "write_pool", "player", "drain", "coll", "custom_item"))
    UUID, TPlayers, Bridge = L["UUID"], L["TPlayers"], L["Bridge"]
    Fn = JClass(PKG + "SackFn")
    Cfg = JClass(PKG + "SackCfg")
    Obj = JClass("java.lang.Object")
    cats = [str(c) for c in Defs.CATS]
    base = os.path.join(scratch, "p39")
    pools = os.path.join(base, "pools")
    U = UUID.fromString("00000000-0000-0000-0000-0000000f0839")
    k = str(U)
    for i_ in (LEAD, IRON_E, IRON_B, ORE):
        custom_item(i_, 100)

    def call(mode, *a):
        return Fn(mode).apply(JArray(Obj)([JString(x) if isinstance(x, str) else x for x in a]))

    def rd(i):
        return int(Pool.get(JString(k), JString(i)))

    def st(cat, tok=None):
        r = call(21, U, "cmpst", cat, "", tok) if tok is not None else call(21, U, "cmpst", cat, "")
        return None if r is None else str(r)

    def tog(cat, tok=None):
        r = call(21, U, "cmp", cat, "", tok) if tok is not None else call(21, U, "cmp", cat, "")
        drain()
        return None if r is None else str(r)

    def extra(key):
        v = VS.st(JString(k)).extra.getProperty(key)
        return None if v is None else str(v)
    drain()
    fresh(base)
    write_pool(pools, k, {IRON_B: 300, IRON_E: 2, LEAD: 5, ORE: 40})
    VS.st(k).first = 1
    coll(U, dict((c_, 0) for c_ in cats))
    total = lambda: rd(IRON_B) + 100 * rd(IRON_E)
    t0 = total()
    try:
        Bridge.PLAYERS = None
        K.check(call(21, U, "cmpst", "Smithing", "") is None and call(21, U, "cmp", "Smithing", "") is None, "P39 no player on this world thread -> null (nothing read, nothing toggled)")
        Bridge.PLAYERS = TPlayers()
        TPlayers.P = player(storage=[])
        K.eq(st("Smithing"), "=b", "P39 STATE a bag with Enchanted forms, not bought = '=b'")
        K.eq(st("Fishing"), "=-", "P39 STATE Fishing (no Enchanted form) = '=-'")
        K.check(str(st("Nope")).startswith("-No such pocket"), "P39 STATE an unknown pocket refused")
        r = tog("Smithing", k)
        K.check(str(r).startswith("-Buy Auto-compact for Smithing first") and extra("comp.Smithing") is None and extra("comp.off.Smithing") is None,
                "P39 TOGGLE not bought: refused, nothing written, no coin path (%s)" % r)
        VS.st(JString(k)).extra.setProperty("comp.Smithing", "1")   # bought (the Void page's Buy -> Pay wrote it)
        K.eq(st("Smithing"), "=1", "P39 STATE bought + on = '=1'")
        r = tog("Smithing", "someone-else#2")
        K.check(str(r).startswith("-Your profile changed") and extra("comp.off.Smithing") is None and st("Smithing") == "=1",
                "P39 TOGGLE another profile's token: refused, nothing toggled (%s)" % r)
        r = tog("Smithing", k)
        K.check(str(r).startswith("=Auto-compact paused for Smithing") and extra("comp.off.Smithing") == "1" and st("Smithing") == "=0" and total() == t0,
                "P39 TOGGLE Pause (the list's own token): comp.off written, '=0', every item counted (%s)" % r)
        r = tog("Smithing", k)
        K.check(str(r).startswith("+Auto-compact is on again for Smithing") and extra("comp.off.Smithing") is None and st("Smithing") == "=1" and total() == t0,
                "P39 TOGGLE Turn on: '+...', runNow ran, every Iron counted once (loose + 100 x Enchanted = %d) (%s)" % (total(), r))
        Cfg.CMP_ON = False
        K.eq(st("Smithing"), "=x", "P39 STATE Server Setup pd.compact.on OFF = '=x'")
        r = tog("Smithing", k)
        K.check(str(r).startswith("-Auto-compact is switched off") and extra("comp.off.Smithing") is None and total() == t0,
                "P39 FIX TOGGLE with Server Setup pd.compact.on OFF: refused like cmpst, nothing written (%s)" % r)
        Cfg.CMP_ON = True
        r = tog("Smithing")
        K.check(str(r).startswith("-Your profile changed") and extra("comp.off.Smithing") is None and st("Smithing", k) == "=1",
                "P39 FIX TOGGLE without a profile token: refused, nothing toggled (%s)" % r)
        # ---- OPEN
        K.check(not bool(call(22, U, "Nope")) and not bool(call(22, U)) and not bool(Fn(22).apply(U)) and not bool(call(22, "x", "Mining")),
                "P39 OPEN unknown pocket / too few arguments / not an array / not a UUID = FALSE")
        Bridge.PLAYERS = None
        K.check(not bool(call(22, U, "Mining")), "P39 OPEN no player on this world thread = FALSE")
    finally:
        Bridge.PLAYERS = None
        Cfg.CMP_ON = True


def run_p39(out, jar, scratch, home):
    T089.void_cases = cases39
    T089.run_void(out, jar, scratch, home)


def run_static(out, jar, scratch, home):
    import subprocess, zipfile
    K = HK.Child(out)
    gen = os.path.join(HERE, "build_skyysacks_%s.py" % VERSION)
    cp = os.path.join(scratch, "regen.py")
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sacks_0_8_39_patch.py"), "--out", cp], capture_output=True, text=True)
    K.check(p.returncode == 0 and open(cp, "rb").read() == open(gen, "rb").read(), "S the patch re-generates the script byte for byte: %s" % p.stderr[-300:])
    g = open(gen, encoding="utf8").read()
    for key in ("sacks:fn:pocketList", "sacks:fn:pocket", "sacks:fn:openTannery", "sacks:fn:openPocket"):
        K.check(g.count('sbr0.put("%s"' % key) == 1, "S setup publishes %s once" % key)
    zn, zo = zipfile.ZipFile(jar), zipfile.ZipFile(OLD_JAR)
    K.check("this.mode == 18 || this.mode == 20 || this.mode == 21) ? null" in g, "S FIX the pocket modes 20 / 21 answer null (not Long 0) when they fail")
    K.eq(sorted(set(zn.namelist()) ^ set(zo.namelist())), [], "S no jar entry added or removed")
    K.eq(sorted(n for n in zn.namelist() if not n.endswith(".class") and zn.read(n) != zo.read(n)), ["manifest.json"], "S changed non-class entries = manifest.json")
    K.save()


if __name__ == "__main__":
    os.makedirs(SCRATCH, exist_ok=True)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("static", run_static), ("p39", run_p39), ("f37", T37.run_f37), ("s36", T36.run_s36), ("all35", T35.run_all35), ("bc36", T36.run_bc36),
            ("live", T30.T0827.run_live27), ("live2", T30.T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
