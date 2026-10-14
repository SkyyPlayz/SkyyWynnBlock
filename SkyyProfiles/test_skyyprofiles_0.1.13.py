"""Harness for SkyyProfiles 0.1.13 (a profile switch waits while a rebirth runs; tools/profiles_0_1_13_patch.py).
Build first: python tools/profiles_0_1_13_patch.py && python SkyyProfiles/build_skyyprofiles_0.1.13.py

    python SkyyProfiles/test_skyyprofiles_0.1.13.py --dir <empty folder inside tools/dev/scratch/> [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.1.12 -> 0.1.13: ProfSwitch (+ rebirthBlock, switchTo, createAndSwitch) and the version texts; no class added
  RB EXECUTED: rebirthBlock (no SkyyRebirth, busy false / true, a throwing function, a non-Boolean answer); switchTo + createAndSwitch on
     PlayerRef stand-ins: refused with the rebirth text while rebirth:fn:busy says the player's profile is busy - NOTHING saved (the
     players file byte-equal, no profile created, no switch marker, BUSY / profile:busy never taken) - and past the check once it is not
     busy (the switch then fails later only because there is no world here); the REAL SkyyRebirth 0.2 rebirth:fn:busy (RbFn mode 4 on
     its own BUSY map, the UUID -> the active pkey via profile:fn:key) refuses the switch the same way
  X, D        test_skyyprofiles_0.1.12.py's exec + live phases on the 0.1.13 jar (everything 0.1.12 did still holds)
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, importlib.util, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK


def tmod(fn, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T12 = tmod("test_skyyprofiles_0.1.12.py", "tp0112")

VERSION = "0.1.13"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyProfiles-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyProfiles-0.1.12.jar")
RB_JAR = os.path.join(ROOT, "SkyyRebirth", "SkyyRebirth-0.2.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "rebirth3", "profiles")))
PKG = "com.skyy.profiles."
LIVE_DIR = T12.LIVE_DIR
EXPECT = {
    "ProfSwitch": ["+m rebirthBlock", "~m switchTo", "~m createAndSwitch"],
    "SkyyProfilesPlugin": ["~m setup"],                 # the ready line
    "ProfCfg": ["~m capMigrate"],                       # version text
    "ProfDel": ["~m archiveLocked"],                    # archive.version = the version text
    "CfgRows": ["~m header"], "CfgFn": ["~m opExport"],  # the config kit's version text
}
ADDED = []


def run_rb(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR], verify=True)
    UUID, Bool = JClass("java.util.UUID"), JClass("java.lang.Boolean")
    bridge = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", bridge)
    J = T12.Jar(jar, os.path.join(scratch, "rb"))
    try:
        J.Cfg.BRIDGE = None
    except Exception:
        pass
    S, Sw = J.Store, J.Sw

    @JImplements("java.util.function.Function")
    class Fn(object):
        def __init__(self, f):
            self.f = f

        @JOverride
        def apply(self, o):
            return self.f(o)
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    us = uf.get(None)
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    Mod = JClass("java.lang.reflect.Modifier")
    uuid_fs = [f_ for f_ in PRc.class_.getDeclaredFields() if f_.getType() == UUID.class_ and not Mod.isStatic(f_.getModifiers())]
    for f_ in uuid_fs:
        f_.setAccessible(True)

    def pref(u):
        r_ = us.allocateInstance(PRc.class_)
        for f_ in uuid_fs:
            f_.set(r_, u)
        return r_
    u = UUID(0x0B0A000000000000, 0x7713)
    K.check(Sw.rebirthBlock(u) is None, "RB no SkyyRebirth: no block")
    st = {"v": Bool.FALSE}
    bridge.put("rebirth:fn:busy", Fn(lambda o: st["v"]))
    K.check(Sw.rebirthBlock(u) is None, "RB not busy: no block")
    st["v"] = Bool.TRUE
    K.eq(str(Sw.rebirthBlock(u)), "A rebirth is finishing on this profile - switch profiles again in a few seconds.", "RB busy: the block text")
    st["v"] = "yes"
    K.check(Sw.rebirthBlock(u) is None, "RB a non-Boolean answer: no block")

    def boom(o):
        raise RuntimeError("x")
    bridge.put("rebirth:fn:busy", Fn(boom))
    K.check(Sw.rebirthBlock(u) is None, "RB a throwing function: no block (no exception)")
    # switchTo / createAndSwitch with two profiles
    S.create(u, "1", "Apple", "Mage", True)
    S.create(u, "2", "Banana", "Archer", False)
    f = J.file(u)
    h0 = hashlib.sha1(open(f, "rb").read()).hexdigest()
    bridge.put("rebirth:fn:busy", Fn(lambda o: Bool.TRUE))

    def run(fn):
        try:
            return str(fn())
        except Exception as e:
            return "EXC " + str(e)[:120]
    r1 = run(lambda: Sw.switchTo(None, None, pref(u), None, "2"))
    r2 = run(lambda: Sw.createAndSwitch(None, None, pref(u), None, "Priest", "Cherry"))
    K.check(r1.startswith("A rebirth is finishing") and r2.startswith("A rebirth is finishing"), "RB busy: switchTo + createAndSwitch refused: %s / %s" % (r1, r2))
    K.check(hashlib.sha1(open(f, "rb").read()).hexdigest() == h0 and int(S.count(S.load(u))) == 2 and not S.BUSY.containsKey(u)
            and bridge.get("profile:busy:" + str(u)) is None and not os.path.exists(os.path.join(J.home, "switching", str(u) + ".properties")),
            "RB refused = nothing saved: the players file byte-equal, no profile created, no BUSY / profile:busy, no switch marker")
    bridge.put("rebirth:fn:busy", Fn(lambda o: Bool.FALSE))
    r3 = run(lambda: Sw.switchTo(None, None, pref(u), None, "2"))
    K.check(not r3.startswith("A rebirth is finishing"), "RB not busy: switchTo gets past the rebirth check (%s)" % r3[:80])
    # fix round 2: a rebirth that starts between the first check and the claim - the second check (after profile:busy is set) refuses
    seen = []

    def late(o):
        seen.append(bridge.get("profile:busy:" + str(u)) is not None)
        return Bool.TRUE if len(seen) >= 2 else Bool.FALSE
    bridge.put("rebirth:fn:busy", Fn(late))
    h1 = hashlib.sha1(open(f, "rb").read()).hexdigest()
    r6 = run(lambda: Sw.switchTo(None, None, pref(u), None, "2"))
    K.check(r6.startswith("A rebirth is finishing") and seen == [False, True] and not S.BUSY.containsKey(u)
            and bridge.get("profile:busy:" + str(u)) is None and hashlib.sha1(open(f, "rb").read()).hexdigest() == h1
            and not os.path.exists(os.path.join(J.home, "switching", str(u) + ".properties")),
            "FIX2 RB a rebirth starting in the window: re-checked AFTER profile:busy is claimed -> refused, BUSY + profile:busy released, nothing saved (%s, %s)" % (r6[:60], seen))
    # the REAL SkyyRebirth 0.2 rebirth:fn:busy
    rl = T12.loader_for(RB_JAR)
    RbFn, RbStore, RbCfg = (JClass("com.skyy.rebirth.RbFn", loader=rl), JClass("com.skyy.rebirth.RbStore", loader=rl), JClass("com.skyy.rebirth.RbCfg", loader=rl))
    RbCfg.BRIDGE = None
    bridge.put("rebirth:fn:busy", RbFn(4))
    bridge.put("profile:fn:key", Fn(lambda o: str(o) + "-p2" if str(o) == str(u) else str(o)))
    RbStore.BUSY.put(str(u) + "-p2", "tx1760000000001-a1b2c3")
    r4 = run(lambda: Sw.switchTo(None, None, pref(u), None, "2"))
    K.check(r4.startswith("A rebirth is finishing"), "RB with the REAL SkyyRebirth 0.2 rebirth:fn:busy (the active pkey -p2 busy): refused (%s)" % r4[:80])
    RbStore.BUSY.clear()
    r5 = run(lambda: Sw.switchTo(None, None, pref(u), None, "2"))
    K.check(not r5.startswith("A rebirth is finishing"), "RB the REAL function, nothing busy: past the check")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyProfiles", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("rb", run_rb), ("exec", T12.run_exec), ("live", T12.run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyProfiles"))
