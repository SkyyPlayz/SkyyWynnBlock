"""Harness for SkyyAccessories 0.5.14 (SOUND PASS ROUND 2: equipped / upgraded on the Accessory Bag page + the per-player sound switch;
tools/accessories_0_5_14_patch.py).
Build first: python tools/accessories_0_5_14_patch.py && python SkyyAccessories/build_skyyaccessories_0.5.14.py

    python SkyyAccessories/test_skyyaccessories_0.5.14.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.5.13 -> 0.5.14: + AccSnd; AccPage.handleDataEvent (the one call), the plugin setup, the kit's rows / version texts only
  SND EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py Stage): tools/soundpass_gen.unit (file, rows, the kit's check=
     hook, ids, gate, the per-player switch settings:sounds:<uuid>, missing id, offline, ok()); THE CALL SITE's call with REAL results:
     the REAL AccStore.equipK on a scratch bag (Workbench Accessory I into an empty bag = "" -> AccSnd.equipped = the equip sting;
     Workbench Accessory II = in place, returns the old id -> the upgrade sting; the same tier again = null (refused) -> silent); the
     player muted in /settings = silent; static: the page plays it right after equipK, after the refusal return, before the result text;
     only AccSnd.playTo calls SoundUtil; KIT end to end
  D  live     start twice on a scratch COPY of the live Skyy_SkyyAccessories with 0.5.14's setup order (migrations, AccCfg.load, notices,
              AccSnd.load, the kit): the first start adds only sounds.properties (+ kit files), the second changes nothing
  AA engine-access audit
NOT driven here: the click itself (AccPage.handleDataEvent needs a live UI page; 0.5.1's harness drove it, the click path is unchanged).
Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK
import soundpass_gen as G

VERSION = "0.5.14"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAccessories-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAccessories-0.5.13.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound2", "acc")))
PKG = "com.skyy.accessories."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyAccessories")
SOUNDS = [dict(key="equip", field="EQUIP", label="Accessory equipped", id="SFX_Drag_Items_Gems", help="An accessory went into a free bag slot."),
          dict(key="upgrade", field="UPGRADE", label="Accessory upgraded", id="SFX_Runebinders_Lattice_Unlock_Local",
               help="A better accessory of the same line replaced the old one in the bag.")]
EXPECT = {
    "AccPage": ["~m handleDataEvent"],
    "SkyyAccessoriesPlugin": ["~m setup"],
    "CfgFile": ["~<clinit>", "~m init"],
    "CfgRows": ["+f DL1", "~<clinit>", "~m defLines", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["AccSnd"]


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def run_snd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    st = SK.Stage()
    ua = "00000000-0000-4000-8000-0000000000ac"
    pa = st.player("Alice", ua)
    st.player("Bob", "00000000-0000-4000-8000-0000000000bc")
    st.universe()
    L = loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Snd, Rows, Fn, CP = J("AccSnd"), J("CfgRows"), J("CfgFn"), J("CfgPub")
    G.unit(K, st, Snd, Rows, Fn, pa, ua, "SkyyAccessories", SOUNDS, os.path.join(scratch, "unit", "Skyy_SkyyAccessories"))
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    Store = J("AccStore")
    Store.DIR = Paths.get(os.path.join(scratch, "bags"))
    u = UUID.fromString(ua)
    k = str(Store.pkey(u))
    br = G.bridge(st.J)

    def fresh():
        Snd.LAST.clear()
        st.clear()
    # ---- THE CALL SITE's call with REAL equipK results
    fresh()
    r1 = Store.equipK(u, k, "Skyy_Accessory_Workbench_T1")
    K.check(r1 is not None and str(r1) == "" and bool(Snd.equipped(u, r1)), "SITE equipK(Workbench Accessory I) into an empty bag = \"\" -> equipped: %r" % r1)
    K.eq(st.sounds(), [("Alice", "SFX_Drag_Items_Gems", "UI", "2d")], "SITE ... the equip sting, that player only")
    fresh()
    r2 = Store.equipK(u, k, "Skyy_Accessory_Workbench_T2")
    K.check(r2 is not None and str(r2) == "Skyy_Accessory_Workbench_T1" and bool(Snd.equipped(u, r2)), "SITE equipK(Workbench Accessory II) = in place, the old id back: %r" % r2)
    K.eq(st.sounds(), [("Alice", "SFX_Runebinders_Lattice_Unlock_Local", "UI", "2d")], "SITE ... the upgrade sting")
    fresh()
    r3 = Store.equipK(u, k, "Skyy_Accessory_Workbench_T2")
    K.check(r3 is None and not bool(Snd.equipped(u, r3)) and st.sounds() == [], "SITE the same tier again = refused (null) -> silent")
    fresh()
    br.put("settings:sounds:" + ua, JClass("java.lang.Boolean").FALSE)
    r4 = Store.equipK(u, k, "Skyy_Accessory_Workbench_T3")
    K.check(r4 is not None and not bool(Snd.equipped(u, r4)) and st.sounds() == [], "SITE the player MUTED in /settings: an upgrade, silent")
    br.remove("settings:sounds:" + ua)
    K.check(not bool(Snd.equipped(None, "")), "SITE no player: nothing")
    # ---- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["AccSnd.playTo"], "STATIC only AccSnd.playTo calls SoundUtil")
    K.check(PKG + "AccSnd.equipped" in g.get("AccPage.handleDataEvent", set()) and PKG + "AccSnd.load" in g.get("SkyyAccessoriesPlugin.setup", set()),
            "STATIC the bag page plays it; setup loads sounds.properties")
    gen = open(os.path.join(HERE, "build_skyyaccessories_%s.py" % VERSION), encoding="utf8").read()
    i0 = gen.index("String res = {PKG}.AccStore.equipK(u, k, put);")
    i1 = gen.index("if (res == null) {{", i0)
    i2 = gen.index("{PKG}.AccSnd.equipped(u, res);", i0)
    i3 = gen.index('this.info = "upgraded to "', i0)
    K.check(i0 < i1 < i2 < i3 and gen.count("AccSnd.equipped(") == 2, "STATIC equipK -> the refusal return -> the sting -> the result text (one call site)")
    K.check(gen.index("@PKG@.AccSnd.load(") < gen.index("@PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());"), "STATIC sounds.properties read before the kit starts")
    G.kit_set(K, st.J, Snd, CP, Fn, os.path.join(scratch, "kit", "mods"), "SkyyAccessories", SOUNDS)
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    snaps = []
    for start in (1, 2):
        L = loader_for(jar)
        J = lambda n: JClass(PKG + n, loader=L)
        J("AccStore").DIR = Paths.get(os.path.join(home, "bags"))
        J("AccCfg").FILE = Paths.get(os.path.join(home, "config.properties"))
        J("AccCfg").migrate051()
        J("AccCfg").migrate055()
        J("AccCfg").load(True)
        J("AccNotice").FILE = Paths.get(os.path.join(home, "notices.properties"))
        J("AccNotice").load()
        t = str(J("AccSnd").load(Paths.get(home)))
        J("CfgPub").start(Paths.get(mods), None)
        K.check(t == "sounds on (2 of 2)" and int(J("AccSnd").WARNS.get()) == 0, "DS%d: the live copy reads the sound defaults: %s" % (start, t))
        J("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
    G.live_twice(K, h0, snaps[0], snaps[1])
    K.check(open(os.path.join(home, "sounds.properties"), encoding="latin-1").read() == G.file_text("SkyyAccessories", SOUNDS), "DS: sounds.properties = the default text")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyAccessories", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("snd", run_snd), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyAccessories"))
