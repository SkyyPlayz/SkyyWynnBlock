"""Harness for SkyyPets 0.2.6 (SOUND PASS ROUND 1: the pet summon / dismiss sounds; tools/pets_0_2_6_patch.py).
Build first: python tools/pets_0_2_6_patch.py; python SkyyPets/build_skyypets_0.2.6.py

    python SkyyPets/test_skyypets_0.2.6.py [--dir <folder inside tools/dev/scratch/>] [--keep]

  A / C / AA  (tools/harness_kit.py, fresh child JVMs, -Xverify:all) verify, class compare 0.2.5 -> 0.2.6 (+ PetSnd; PetsCfg fields /
              load / seed, PetsPage.handleDataEvent, the kit + version texts only), engine-access audit
  SND         EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py: every Assets.zip sound id in the engine's SoundEvent store,
              a stand-in player on a REAL GamePacketHandler, a stand-in Universe): a real pet record (PetOps.create) -> the expression the
              /pets page runs, PetSnd.slotDone(u, PetOps.toSlot(...), true) = the slot change saved AND ONE PlaySoundEvent2D
              SFX_Deployable_Totem_Heal_Spawn (UI) to the owner; the same into the summon slot; takeOut = the dismiss sound; a refused
              change ("=" already there / "-" locked) = no sound; the switches (master / each sound / an EMPTY id stays empty after a
              reload - sv() would have put the default back) = silent; PetSnd itself (idx / err / check / pick / gate / a missing id = one
              WARN); Server Setup: the 5 rows (Sounds category, live, default ids), the kit's own check= hook; config.properties: a fresh
              file lists the 5 lines, a 0.2.5 file without them = the defaults; static: only PetSnd calls SoundUtil, the page's to1 / to2 /
              out clicks go through PetSnd.slotDone (3 calls)
  OLD         the WHOLE 0.2.5 harness (test_skyypets_0.2.5.py) run on the 0.2.6 jar with --old 0.2.5 (its core phase clicks to1 / to2 / out
              on the real page = the new call sites run; ECS, perm, bytecode, mobs, restarts, START TWICE on a scratch COPY of the live
              mods folder, the move twice, rollbacks, audit). Its checks that pin the 0.2.5 IDENTITY (the version / the 0.2.4 -> 0.2.5 class
              compare / the exact class list / a "SkyyPets 0.2.4 " text) are expected to differ and are listed in EXPECTED_OLD; every other
              failure fails this harness.
Exit code 1 on any failure.
"""
import os, sys, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK

VERSION = "0.2.6"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyPets-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyPets-0.2.5.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(TOOLS, "dev", "scratch", "sound1", "pets")))
PKG = "com.skyy.pets."
SUMMON, DISMISS = "SFX_Deployable_Totem_Heal_Spawn", "SFX_Deployable_Totem_Heal_Despawn"
EXPECT = {
    "PetsCfg": ["+f SND_ON", "+f SND_SUMMON", "+f SND_SUMMON_ID", "+f SND_DISMISS", "+f SND_DISMISS_ID", "~<clinit>", "~m applyScalars",
                "~m applyAll", "~m seed"],     # applyAll / seed: the DEFAULT_TEXT constant (5 new lines) they read
    "PetsPage": ["~m handleDataEvent"],
    "CfgFile": ["~<clinit>"],
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "SkyyPetsPlugin": ["~m setup"],
}
ADDED = ["PetSnd"]
# the 0.2.5 harness's checks that pin the 0.2.5 identity (prefix of the FAILED line) - each expected to fail on 0.2.6, with why
EXPECTED_OLD = [
    ("J: manifest Main / IncludesAssetPack TRUE (0.2: the two roles) / Version / Name", "the version is 0.2.6"),
    ("J/C: exactly the 47 expected classes: extra ['com.skyy.pets.PetSnd'] missing []", "+ PetSnd"),
    ("compare: C 0.2.5: the classes of 0.2.4 + PetOwnerFn only: +['PetSnd'] -[]", "its compare is 0.2.4 -> 0.2.5 (ours: phase C)"),
    ("compare: C 0.2.5: records, store, buffs, XP, ops, the tick, timers, commands, the views (LIVE upkeep), the world calls, F, the sweep, the loadout bridge, the page: byte-for-byte 0.2.4 (changed: ['PetsPage'])", "PetsPage.handleDataEvent = the 3 click sites"),
    ("compare: C 0.2.5: every change is one of the planned ones:", "0.2.6's planned changes (ours: phase C)"),
    ("compare: C 0.2.5: the plugin's setup + shutdown changed: ['~setup']", "the ready line names the sounds"),
    ("compare: C 0.2.5: PetsCfg.<clinit> differs from 0.2.4 only in its constants (strings / table sizes): [", "the 5 new fields (each named one must be SND_*: run_old checks)"),
    ("compare: C 0.2.5: shutdown = 0.2.4's + one more instanceof (PetOwnerFn) guarding the pets:fn:ownerOf remove (never another mod's entry): 4 vs 4", "0.2.5 vs 0.2.6: the same shutdown"),
    ("rollback 0.2.4: R 0.2.5: rollback - the 0.2.4 jar reads the live copy after 0.2.5", "the old jar is 0.2.5 here (its text says 0.2.5, not 0.2.4); unreadable 0 / duplicates 0 / 31 kinds are checked in the same line"),
    ("AA: engine-access audit: ", "48 classes (+ PetSnd); ours: phase AA (refused must stay [])"),
]


def run_snd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    st = SK.Stage()
    P = lambda n: JClass(PKG + n)
    Cfg, Store, Ops, Snd, Log, Rows, Fn = P("PetsCfg"), P("PetStore"), P("PetOps"), P("PetSnd"), P("PetsLog"), P("CfgRows"), P("CfgFn")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    Log.LINES = JClass("java.util.ArrayList")()
    u = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    pa = st.player("Alice", str(u))
    st.universe()
    mods = os.path.join(scratch, "snd-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    cf = os.path.join(mods, "Skyy_SkyyPets", "config.properties")
    txt = open(cf, encoding="latin-1").read()
    K.check("pets.sounds=true" in txt and "pets.sound.summon=true" in txt and ("pets.sound.summon.id=%s" % SUMMON) in txt and "pets.sound.dismiss=true" in txt
            and ("pets.sound.dismiss.id=%s" % DISMISS) in txt, "CFG a fresh config.properties lists the 5 sound lines")
    K.check(bool(Cfg.SND_ON) and bool(Cfg.SND_SUMMON) and str(Cfg.SND_SUMMON_ID) == SUMMON and str(Cfg.SND_DISMISS_ID) == DISMISS and SUMMON in st.ids and DISMISS in st.ids,
            "CFG defaults (both ids are in Assets.zip)")
    old = "\n".join(l for l in txt.splitlines() if not l.startswith("pets.sound")) + "\n"
    open(cf, "w", encoding="latin-1").write(old)
    Cfg.SND_SUMMON_ID = "x"
    Cfg.reloadAll()
    K.check(bool(Cfg.SND_ON) and str(Cfg.SND_SUMMON_ID) == SUMMON and str(Cfg.SND_DISMISS_ID) == DISMISS, "CFG a 0.2.5 file without the lines = the defaults")
    open(cf, "w", encoding="latin-1").write(old + "pets.sounds=false\npets.sound.summon.id=\npets.sound.dismiss.id=SFX_Coins_Land\n")
    Cfg.reloadAll()
    K.check(not bool(Cfg.SND_ON) and str(Cfg.SND_SUMMON_ID) == "" and str(Cfg.SND_DISMISS_ID) == "SFX_Coins_Land",
            "CFG an EMPTY id line stays empty after a reload (= that sound off; sv() would have put the default back); off / another id read")
    open(cf, "w", encoding="latin-1").write(txt)
    Cfg.reloadAll()
    rows = SK.kit_rows(Rows)
    SK.sound_rows(K, rows, "pets.sounds", [("pets.sound.summon", "pets.sound.summon.id", SUMMON), ("pets.sound.dismiss", "pets.sound.dismiss.id", DISMISS)])
    K.check(all(rows[k][2] == "sounds" for k in rows if k.startswith("pets.sound")), "ROW the Sounds category")
    for key in ("pets.sound.summon.id", "pets.sound.dismiss.id"):
        K.check("no sound event" in (SK.kit_check(Fn, Rows, key, SK.BAD_ID) or "") and SK.kit_check(Fn, Rows, key, "a-b") is not None
                and SK.kit_check(Fn, Rows, key, "") is None and SK.kit_check(Fn, Rows, key, "SFX_Coins_Land") is None, "CHECK %s: the kit's check= hook" % key)
    # ---------------- PetSnd itself
    K.check(int(Snd.idx(SUMMON)) == st.ids[SUMMON] and int(Snd.idx(SK.BAD_ID)) == -2147483648 and int(Snd.idx(" ")) == -2147483648, "PetSnd.idx")
    K.check(Snd.pick(True, True, SUMMON) == SUMMON and Snd.pick(False, True, SUMMON) is None and Snd.pick(True, False, SUMMON) is None and Snd.pick(True, True, "") is None, "PetSnd.pick")
    st.clear()
    K.check(bool(Snd.playTo(pa, SUMMON, "t")) and not bool(Snd.playTo(pa, SUMMON, "t")) and st.sounds() == [("Alice", SUMMON, "UI", "2d")], "PetSnd.playTo once; the gate holds a repeat")
    n0 = Log.LINES.size()
    K.check(not bool(Snd.play(u, SK.BAD_ID, "x")) and not bool(Snd.play(u, SK.BAD_ID, "x")) and len([x for x in list(Log.LINES)[n0:] if SK.BAD_ID in str(x)]) == 1,
            "PetSnd: a missing id plays nothing, one WARN")
    K.check(not bool(Snd.play(UUID(5, 5), SUMMON, "y")) and not bool(Snd.playTo(None, SUMMON, "y")), "PetSnd: an offline player / null = nothing")
    # ---------------- THE CALL SITE: the page's expression on a real pet record
    Store.ROOT = Paths.get(mods, "Skyy_SkyyPets")
    Store.DIR = Store.ROOT.resolve("pets")
    r = Store.get(str(Store.pkey(u)))
    pid = str(Ops.create(r, None, "Wolf", 3, 5, 0, "test", "t", True))
    K.check(not pid.startswith("-") and r.has(pid), "SITE a Wolf pet record (%s)" % pid)
    for k in (1, 2):
        if str(r.active(k)) == pid:
            r.set("active.%d" % k, "")
    Snd.LAST.clear()
    st.clear()
    a1 = str(Snd.slotDone(u, Ops.toSlot(u, pid, 1, "t"), True))
    K.check(a1.startswith("+") and str(r.active(1)) == pid and st.sounds() == [("Alice", SUMMON, "UI", "2d")], "SITE to1: saved + the summon sound: %s %s" % (a1, st.sounds()))
    st.clear()
    a1b = str(Snd.slotDone(u, Ops.toSlot(u, pid, 1, "t"), True))
    K.check(a1b.startswith("=") and st.sounds() == [], "SITE to1 again ('already there') = silent: %s" % a1b)
    Snd.LAST.clear()
    a2 = str(Snd.slotDone(u, Ops.toSlot(u, pid, 2, "t"), True))
    K.check(a2.startswith("-") and st.sounds() == [], "SITE to2 while the summon slot is locked = refused, silent: %s" % a2)
    r.set("slot2.unlocked", "true")
    a2 = str(Snd.slotDone(u, Ops.toSlot(u, pid, 2, "t"), True))
    K.check(a2.startswith("+") and str(r.active(2)) == pid and st.sounds() == [("Alice", SUMMON, "UI", "2d")], "SITE to2 (a Wolf may be summoned): saved + the summon sound: %s" % a2)
    st.clear()
    ao = str(Snd.slotDone(u, Ops.takeOut(u, pid, "t"), False))
    K.check(ao.startswith("+") and str(r.active(2)) == "" and st.sounds() == [("Alice", DISMISS, "UI", "2d")], "SITE out: saved + the dismiss sound: %s" % ao)
    st.clear()
    ao2 = str(Snd.slotDone(u, Ops.takeOut(u, pid, "t"), False))
    K.check(ao2.startswith("=") and st.sounds() == [], "SITE out again ('not in a slot') = silent")
    for what, f, v in (("master off", "SND_ON", False), ("summon off", "SND_SUMMON", False), ("empty summon id", "SND_SUMMON_ID", "")):
        old_v = getattr(Cfg, f)
        setattr(Cfg, f, v)
        Snd.LAST.clear()
        st.clear()
        ax = str(Snd.slotDone(u, Ops.toSlot(u, pid, 1, "t"), True))
        K.check(ax.startswith("+") and st.sounds() == [], "SITE %s: the change is saved, no sound" % what)
        Ops.takeOut(u, pid, "t")
        setattr(Cfg, f, old_v)
    K.check(Snd.slotDone(u, None, True) is None and str(Snd.slotDone(u, "-x", False)) == "-x", "SITE slotDone passes any answer through")
    # ---------------- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["PetSnd.playTo"], "STATIC only PetSnd.playTo calls SoundUtil")
    K.check(PKG + "PetSnd.slotDone" in g.get("PetsPage.handleDataEvent", set()) and PKG + "PetOps.toSlot" in g.get("PetsPage.handleDataEvent", set())
            and PKG + "PetOps.takeOut" in g.get("PetsPage.handleDataEvent", set()), "STATIC the page's slot clicks go through PetSnd.slotDone")
    pool = JClass("javassist.ClassPool")(True)
    pool.appendClassPath(jar)
    IP, PS, BOS = JClass("javassist.bytecode.InstructionPrinter"), JClass("java.io.PrintStream"), JClass("java.io.ByteArrayOutputStream")
    bos = BOS()
    for mm in pool.get(PKG + "PetsPage").getDeclaredMethods():
        if str(mm.getName()) == "handleDataEvent":
            IP(PS(bos)).print_(mm)
    K.eq(str(bos.toString()).count("PetSnd.slotDone"), 3, "STATIC exactly 3 slotDone calls (to1, to2, out)")
    K.save()


def run_old(K_label):
    """the whole 0.2.5 harness on the 0.2.6 jar; returns (ok count, unexpected failures, expected ones seen)"""
    sc = os.path.join(os.path.dirname(SCRATCH), "pets-old")
    env = dict(os.environ)
    p = subprocess.run([sys.executable, os.path.join(HERE, "test_skyypets_0.2.5.py"), "--jar", JAR, "--old", OLD_JAR, "--dir", sc],
                       env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = p.stdout.splitlines()
    oks = [l for l in lines if l.endswith("fail(s)") and " ok, " in l]
    failed = [l.strip()[len("FAILED: "):] for l in lines if l.strip().startswith("FAILED: ")]
    exp, bad = [], []
    import re
    for f in failed:
        hit = [e for e in EXPECTED_OLD if f.startswith(e[0])]
        if hit and "PetsCfg.<clinit>" in f and any(not x.startswith("SND_") for x in re.findall(r"PetsCfg\.(\w+)\(", f.split("constants", 1)[1])):
            hit = []           # a <clinit> change beyond the 5 sound fields is NOT expected
        (exp if hit else bad).append(f)
    return oks, bad, exp, p.returncode


if __name__ == "__main__":
    if "--phase" not in sys.argv and "--no-old" not in sys.argv:
        oks, bad, exp, rc = run_old("old")
        print("OLD. the 0.2.5 harness on the 0.2.6 jar: %s; %d expected identity checks differ, %d other failure(s)" % (oks[-1:] or "no summary", len(exp), len(bad)))
        for e in exp:
            print("  note (old): expected on 0.2.6: %s" % e[:200])
        HK.check(bool(oks), "OLD: the 0.2.5 harness ran to its summary")
        HK.check(not bad, "OLD: no failure outside the 0.2.5 identity checks: %s" % bad[:5])
        HK.check(len(exp) <= len(EXPECTED_OLD), "OLD: at most the listed identity checks differ (%d)" % len(exp))
    HK.run(name="SkyyPets", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("snd", run_snd)], script=__file__)
