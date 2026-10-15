"""Harness for SkyySacks 0.8.5 (SOUND PASS ROUND 2: Void full / Void upgrade + the per-player sound switch; tools/sacks_0_8_5_patch.py).
Build first: python tools/sacks_0_8_5_patch.py && python SkyySacks/build_skyysacks_0.8.5.py

    python SkyySacks/test_skyysacks_0.8.5.py [--keep] [--dir <scratch>]

Phases (fresh child JVMs, tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all
  C  compare  0.8.4 -> 0.8.5: + SackSnd; PickGive.tell (Void full), SacksPage.onEvent (the Void page: the upgrade sting replaces the craft click),
              the plugin setup, the kit's rows / version texts only
  SND EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py Stage): tools/soundpass_gen.unit (file, rows, the kit's check=
     hook, ids, gate, the per-player switch settings:sounds:<uuid>, missing id, offline, ok()); THE CALL SITE, REAL: PickGive.tell (what
     every auto-pickup delivery calls) with a stand-in online player: a delivery that left items at the feet (r[2] > 0) = the chat
     warning + the Void full sting + the usual pickup click; a second one within 30 s = the pickup click only; Void and inventory not
     full = the pickup click only; the player muted in /settings = no sting (the vanilla pickup click is not ours and stays); the Void
     full row off = no sting; the upgrade: SackSnd.ok(u, the Upgrade result, 1) - "+..." plays, "-..." / "=..." silent; static: the
     page's Upgrade plays SackSnd.ok and NO LONGER the craft click, only SackSnd.playTo + PickGive.tell (the old pickup click) call
     SoundUtil (0.8.4 control: the page did); KIT end to end
  D  live     0.8.4's live checks on a scratch COPY of the live Skyy_SkyySacks (every pool loads with 0.8.4 and 0.8.5 alike, twice; the live
              config.properties loads twice byte-identical), then SackCfg.reload + SackSnd.load + the kit TWICE: the first start adds
              only sounds.properties (+ kit files), the second nothing
  AA engine-access audit
Exit code 1 on any failure.
"""
import os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK
import soundpass_gen as G

VERSION = "0.8.5"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-0.8.4.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound2", "sacks")))
PKG = "com.skyy.sacks."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyySacks")
SOUNDS = [dict(key="full", field="FULL", label="Void full", id="SFX_Generic_Crafting_Failed",
               help="Auto-pickup: Void and inventory full, drops land at your feet. Once per 30 s."),
          dict(key="upgrade", field="UPGRADE", label="Void upgrade", id="SFX_Workbench_Upgrade_Complete_Default",
               help="The Void page's Upgrade went through (replaces the old craft click there).")]
EXPECT = {
    "PickGive": ["~m tell"],
    "SacksPage": ["~m onEvent"],
    "SkyySacksPlugin": ["~m setup"],
    "CfgFile": ["~<clinit>", "~m init"],
    "CfgRows": ["+f DL1", "~<clinit>", "~m defLines", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["SackSnd"]


def loader_for(j):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(j).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def run_snd(out, jar, scratch, _home):
    from jpype import JClass, JArray, JLong
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    st = SK.Stage()
    ua = "00000000-0000-4000-8000-0000000005ac"
    pa = st.player("Alice", ua)
    st.player("Bob", "00000000-0000-4000-8000-0000000005bc")
    st.universe()
    L = loader_for(jar)
    J = lambda n: JClass(PKG + n, loader=L)
    Snd, Rows, Fn, CP = J("SackSnd"), J("CfgRows"), J("CfgFn"), J("CfgPub")
    G.unit(K, st, Snd, Rows, Fn, pa, ua, "SkyySacks", SOUNDS, os.path.join(scratch, "unit", "Skyy_SkyySacks"))
    UUID = JClass("java.util.UUID")
    u = UUID.fromString(ua)
    Give = J("PickGive")
    br = G.bridge(st.J)
    PICK = "SFX_Player_Pickup_Item"

    def r(void, inv, feet):
        return JArray(JLong)([void, inv, feet])

    def fresh():
        Snd.LAST.clear()
        Snd.FULLAT.clear()
        Give.FULL.clear()
        Give.SND.clear()
        st.clear()

    def mine():
        return [x for x in st.sounds() if x[1] != PICK]
    # ---- THE CALL SITE, REAL: PickGive.tell
    fresh()
    Give.tell(u, pa, "Ore_Copper", 64, r(0, 0, 64))
    ch = [t for w, t in st.chats("Alice")]
    K.check(any("Void and inventory are full" in t for t in ch), "SITE a delivery that left 64 at the feet: the chat warning: %s" % ch)
    K.eq(mine(), [("Alice", "SFX_Generic_Crafting_Failed", "UI", "2d")], "SITE ... AND ONE Void full sting (UI 2D, that player only)")
    K.check(any(x[1] == PICK for x in st.sounds()), "SITE ... the usual pickup click still plays")
    Snd.LAST.clear()
    Give.SND.clear()
    st.clear()
    Give.tell(u, pa, "Ore_Copper", 64, r(0, 0, 64))
    K.check(mine() == [], "SITE a second full delivery within 30 s: no second sting (the 30 s window)")
    Snd.FULLAT.put(u, JClass("java.lang.Long")(int(JClass("java.lang.System").currentTimeMillis()) - 31000))
    Snd.LAST.clear()
    st.clear()
    Give.tell(u, pa, "Ore_Copper", 64, r(0, 0, 64))
    K.check(len(mine()) == 1, "SITE 31 s later: the sting again")
    fresh()
    Give.tell(u, pa, "Ore_Copper", 64, r(40, 24, 0))
    K.check(mine() == [] and any(x[1] == PICK for x in st.sounds()), "SITE Void + inventory took it all: the pickup click only, no sting")
    fresh()
    br.put("settings:sounds:" + ua, JClass("java.lang.Boolean").FALSE)
    Give.tell(u, pa, "Ore_Copper", 64, r(0, 0, 64))
    K.check(mine() == [] and int(Snd.MUTED.get()) >= 1, "SITE the player MUTED in /settings: no Void full sting")
    br.remove("settings:sounds:" + ua)
    fresh()
    Snd.S_FULL = False
    Give.tell(u, pa, "Ore_Copper", 64, r(0, 0, 64))
    K.check(mine() == [], "SITE the Void full row off: no sting")
    Snd.S_FULL = True
    fresh()
    K.check(not bool(Snd.full(None, 0)), "SITE full(): no player = nothing")
    # ---- the upgrade: SackSnd.ok(u, the Upgrade result, 1)
    fresh()
    K.check(bool(Snd.ok(u, "+Mining is now Rare (x2)", 1)) and mine() == [("Alice", "SFX_Workbench_Upgrade_Complete_Default", "UI", "2d")],
            "SITE the Upgrade went through ('+'): the upgrade sting")
    fresh()
    K.check(not bool(Snd.ok(u, "-Not enough Ingredient_Bar_Iron", 1)) and not bool(Snd.ok(u, "=Already upgraded", 1)) and mine() == [],
            "SITE a refused / already-done Upgrade: silent")
    # ---- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    g0 = PW.calls(OLD_JAR)
    K.eq(sorted(m for m, cs in g0.items() if any(c.startswith(su + ".") for c in cs)), ["PickGive.tell", "PocketCraftWindow.handleAction", "SacksPage.onEvent"],
         "STATIC (control) 0.8.4: the Void page (SacksPage.onEvent) played the craft click itself")
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["PickGive.tell", "PocketCraftWindow.handleAction", "SackSnd.playTo"],
         "STATIC 0.8.5 SoundUtil: SackSnd.playTo + the old pickup click (PickGive.tell) + the pocket craft click only - the Void page no longer")
    K.check(PKG + "SackSnd.ok" in g.get("SacksPage.onEvent", set()) and PKG + "SackSnd.full" in g.get("PickGive.tell", set())
            and PKG + "SackSnd.load" in g.get("SkyySacksPlugin.setup", set()), "STATIC the Upgrade + PickGive.tell play; setup loads the file")
    gen = open(os.path.join(HERE, "build_skyysacks_%s.py" % VERSION), encoding="utf8").read()
    vp = gen[gen.index('if (a.startsWith("upgok:")) {'):]
    vp = vp[:vp.index("return;\n    }")]
    K.check("SFX_Player_Craft_Item_Inventory" not in vp and vp.index("@PKG@.VoidStore.upgrade(player, u, k, uci, from)") < vp.index("@PKG@.SackSnd.ok(u, this.info, 1);"),
            "STATIC the Upgrade: the sting after VoidStore.upgrade, the craft click gone")
    K.check(gen.index("{PKG}.SackSnd.load(") < gen.index("{PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());"), "STATIC sounds.properties read before the kit starts")
    G.kit_set(K, st.J, Snd, CP, Fn, os.path.join(scratch, "kit", "mods"), "SkyySacks", SOUNDS)
    K.save()


def sha(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest()


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST], verify=True)
    before = HK.tree_hash(home)
    pools = os.path.join(home, "pools")
    keys = sorted(f[:-11] for f in os.listdir(pools) if f.endswith(".properties")) if os.path.isdir(pools) else []
    P = JClass("java.nio.file.Paths")
    seen = None
    for start in (1, 2):
        for j in (OLD_JAR, jar):
            SP = JClass(PKG + "SackPool", loader=loader_for(j))
            SP.DIR = P.get(pools)
            got = {}
            for k in keys:
                got[k] = dict((str(e.getKey()), int(e.getValue().longValue())) for e in SP.pool(k).entrySet())
            if seen is None:
                seen = got
            K.check(got == seen, "D start %d %s: every pool loads the same items" % (start, os.path.basename(j)))
    JClass("java.lang.System").getProperties().put("skyy.bridge", JClass("java.util.concurrent.ConcurrentHashMap")())
    cfgf = os.path.join(home, "config.properties")
    if os.path.isfile(cfgf):
        h0 = sha(cfgf)
        Cfg = JClass(PKG + "SackCfg", loader=loader_for(jar))
        Cfg.FILE = P.get(cfgf)
        for _ in (1, 2):
            Cfg.MTIME = -1
            Cfg.reload()
        K.eq(sha(cfgf), h0, "D live config.properties byte-identical after two loads")
    K.eq(HK.tree_hash(home), before, "D the live copy's bytes are unchanged by the data starts")
    K.notes.append("D: %d profile pools" % len(keys))
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    snaps = []
    for start in (1, 2):
        L = loader_for(jar)
        Jn = lambda n: JClass(PKG + n, loader=L)
        if os.path.isfile(cfgf):
            Jn("SackCfg").FILE = P.get(cfgf)
            Jn("SackCfg").reload()
        t = str(Jn("SackSnd").load(P.get(home)))
        Jn("CfgPub").start(P.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks"))
        K.check(t == "sounds on (2 of 2)" and int(Jn("SackSnd").WARNS.get()) == 0, "DS%d: the live copy reads the sound defaults: %s" % (start, t))
        Jn("CfgPub").shutdown()
        snaps.append(HK.tree_hash(home))
    G.live_twice(K, h0, snaps[0], snaps[1])
    K.check(open(os.path.join(home, "sounds.properties"), encoding="latin-1").read() == G.file_text("SkyySacks", SOUNDS), "DS: sounds.properties = the default text")
    K.save()


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED, [("snd", run_snd), ("live", run_live)], __file__,
           live=(LIVE_DIR, "Skyy_SkyySacks"))
