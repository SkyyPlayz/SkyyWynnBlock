"""Harness for SkyyArmory 0.1.31 (THE WOOD WAND HOLD LEAP; tools/armory_0_1_31_patch.py). Build first:
    python tools/armory_0_1_31_patch.py && python SkyyArmory/build_skyyarmory_0.1.31.py

    python SkyyArmory/test_skyyarmory_0.1.31.py [--keep]

Phases (fresh child JVMs, tools/harness_kit.py: the game's JRE, -Xverify:all, -XX:-UsePerfData, TEMP / TMP in the scratch folder):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.1.30 -> 0.1.31: exactly the Wood wand pieces (ArmoryDefs WOOD_TRAV + woodSpawn, ArmoryTrav WOODS + woodCode + woodHit, the
               two system hooks, the info words, the start line) + the version texts differ
  X   exec     ArmoryDefs.woodSpawn truth table (Wood / Rotten / Tribal in a player's hand = 2000; the leap's re-launch = 2000; an NPC, a
               vanilla staff, a metal wand, no item, another id = -1); the vanilla orb id still has no pidCode + no damage tune;
               ArmoryTrav.woodHit on a real TravWorld (record code 2000 = 2000, another code / no record / no world / another id = -1);
               ArmoryTrav.woodCode: the re-launch (TravWorld.pend 2000) = 2000 without asking the caster, no caster = -1 (no throw);
               the start line + the info words name the Wood wand's hold
  D   live     START TWICE on a scratch COPY of the live NewBetaTest Skyy_SkyyArmory: nothing rewritten
  AA  audit    the engine-access audit
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION, OLD = "0.1.31", "0.1.30"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyArmory-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyArmory-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "wandfix", "armory")))
PKG = "com.skyy.armory."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyArmory")
EXPECT = {"ArmoryDefs": ["~<clinit>", "+f WOOD_TRAV", "+m woodSpawn"],
          "ArmoryTrav": ["~<clinit>", "+f WOODS", "+m woodCode", "+m woodHit"],
          "ArmoryTravSys": ["~m onEntityAdded"], "ArmoryHitSys": ["~m handle"],
          "ArmoryCheck": ["~m packCheck", "~m packOf"], "ArmoryInfoFn": ["~m apply"],          # the info words (armory:fn:info)
          # the version text "0.1.31" (ldc strings in the loader / export / Server Setup header / ready line) + the start line's words
          "ArmoryCfg": ["~m load", "~m reloadAll", "~m useDefaults", "~m leapText"], "CfgFn": ["~m opExport"],
          "CfgRows": ["~<clinit>", "~m header"], "SkyyArmoryPlugin": ["~m setup", "~m start"]}


def run_exec(out, jar, scratch, home):
    from jpype import JClass, JObject
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Defs = JClass(PKG + "ArmoryDefs")
    AT = JClass(PKG + "ArmoryTrav")
    TW = JClass(PKG + "TravWorld")
    TS = JClass(PKG + "TravShot")
    Cfg = JClass(PKG + "ArmoryCfg")
    Cfg.useDefaults()
    VAN = str(Defs.W_ORB[0])
    K.eq(VAN, "Skeleton_Mage_Corruption_Orb", "X: W_ORB[0] is the shared vanilla orb (the Wood wand hold's)")
    K.check(bool(Defs.WOOD_TRAV), "X: WOOD_TRAV on")
    K.eq(int(Defs.pidCode(VAN)), -1, "X: the vanilla orb still has no pidCode (NPCs / staffs untouched by every other path)")
    K.eq(float(Defs.tuneFactor2(VAN, True, Cfg.TUNE_W, Cfg.TUNE_S, Cfg.QUICK_DAMAGE, Cfg.STAFF_BONUS)), 1.0, "X: no damage tune on the vanilla orb (as 0.1.30)")

    def ws(pid, pend, pl, held):
        return int(Defs.woodSpawn(pid, pend, pl, held))
    for w_ in ("Weapon_Wand_Wood", "Weapon_Wand_Wood_Rotten", "Weapon_Wand_Tribal"):
        K.eq(ws(VAN, -1, True, w_), 2000, "X: a player holding %s -> the hold orb is the Wood wand's charged orb (2000)" % w_)
        K.eq(ws(VAN, -1, False, w_), -1, "X: an NPC 'holding' %s -> never" % w_)
    for h_ in ("Weapon_Wand_Copper", "Weapon_Wand_Onyxium", "Weapon_Staff_Wood", "Weapon_Staff_Crystal_Red", "Weapon_Sword_Iron", None, ""):
        K.eq(ws(VAN, -1, True, h_), -1, "X: a player holding %r firing the vanilla orb -> -1 (a vanilla staff's orb stays plain)" % (h_,))
    K.eq(ws(VAN, 2000, False, None), 2000, "X: the leap's own re-launched orb (TravWorld.pend code 2000) -> 2000 (no hand check)")
    K.eq(ws(VAN, 2003, True, "Weapon_Staff_Wood"), -1, "X: another pend code is not the Wood re-launch")
    for p_ in ("SkyyArmory_Orb_Copper", "Skeleton_Mage_Corruption_Orb_X", None):
        K.eq(ws(p_, 2000, True, "Weapon_Wand_Wood"), -1, "X: another projectile id %r -> -1" % (p_,))

    # real objects: a Store (never constructed - allocateInstance), Refs, a TravWorld
    Unsafe = JClass("sun.misc.Unsafe")
    fu = Unsafe.class_.getDeclaredField("theUnsafe")
    fu.setAccessible(True)
    U = fu.get(None)
    STc = JClass("com.hypixel.hytale.component.Store")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    st = JObject(U.allocateInstance(STc.class_), STc)
    r1, r2, r3 = REFc(st, 7101), REFc(st, 7102), REFc(st, 7103)
    tw = TW.get(st)
    tw.orbs.put(r1, TS(0.0, 0.0, 0.0, 0.0, 2000, None, VAN))
    tw.orbs.put(r2, TS(0.0, 0.0, 0.0, 0.0, 2003, None, VAN))
    K.eq(int(AT.woodHit(st, r1, VAN)), 2000, "X: woodHit: the orb's record has code 2000 -> burst + signature charge (2000)")
    K.eq(int(AT.woodHit(st, r2, VAN)), -1, "X: woodHit: another record code -> -1")
    K.eq(int(AT.woodHit(st, r3, VAN)), -1, "X: woodHit: no record (an NPC's / a staff's orb) -> -1")
    K.eq(int(AT.woodHit(st, r1, "SkyyArmory_Orb_Copper")), -1, "X: woodHit: another id -> -1 (pidCode handles our own)")
    K.eq(int(AT.woodHit(None, r1, VAN)), -1, "X: woodHit: no world -> -1")
    K.eq(int(AT.woodHit(st, None, VAN)), -1, "X: woodHit: no projectile -> -1")
    # woodCode: the leap's re-launch is known from TravWorld.pend alone (the caster is never asked)
    tw.pend.put(r3, TS(0.0, 0.0, 0.0, 0.0, 2000, None, VAN))
    w0 = int(AT.WOODS)
    K.eq(int(AT.woodCode(r3, None, VAN, st, None)), 2000, "X: woodCode: the re-launched orb in TravWorld.pend (2000) -> 2000, counted")
    K.eq(int(AT.WOODS) - w0, 1, "X: WOODS counts it")
    tw.pend.remove(r3)
    m_ = [m for m in AT.class_.getDeclaredMethods() if str(m.getName()) == "woodCode"][0]          # the patch's @LPC@ = woodCode's 2nd parameter
    lpc_name = str(m_.getParameterTypes()[1].getName())
    LPC = JClass(lpc_name)
    pc = JObject(U.allocateInstance(LPC.class_), LPC)
    K.eq(int(AT.woodCode(r3, pc, VAN, st, None)), -1, "X: woodCode: no caster (creator null) -> -1, no throw")
    K.eq(int(AT.woodCode(r3, pc, "SkyyArmory_Orb_Iron", st, None)), -1, "X: woodCode: another id -> -1 at once")
    K.eq(int(AT.WOODS) - w0, 1, "X: refused ones are not counted")
    lt = str(Cfg.leapText())
    K.check("every wand - the Wood / Rotten / Tribal wands too" in lt and lt.startswith("wand hold (every wand"), "X: the start line names the Wood wand hold: " + lt[:90])
    K.eq(str(JClass(PKG + "TravMath").travWords(False, True, True, "blink", 16, 6.0, 9.0, 2.5))[:20], "Hold - hop back + bu", "X: the traversal words the Wood row now gets")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg = JClass(PKG + "ArmoryCfg")
    Paths = JClass("java.nio.file.Paths")
    Cfg.DIR = Paths.get(home)
    Cfg.FILE = Paths.get(home).resolve("config.properties")
    f = os.path.join(home, "config.properties")
    before = open(f, "rb").read() if os.path.isfile(f) else None
    snaps = []
    for start in (1, 2):
        for m in ("migrate012", "migrate013", "migrate014", "migrate016", "migrate017", "migrate018", "migrate021"):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(f, "rb").read() if os.path.isfile(f) else None)
    K.check(snaps[0] == snaps[1], "D: the 2nd start changes nothing")
    K.check(before is None or snaps[0] == before, "D: the live copy's config.properties is not rewritten by 0.1.31")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyArmory", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=[],
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyArmory"))
