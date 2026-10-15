"""Harness for SkyyShards 0.3.1 (SOUND PASS ROUND 2: collect / totem placed / island grown + the per-player sound switch;
SkyyShards/build_skyyshards_0.3.1.py, hand-written from 0.3).

    python SkyyShards/test_skyyshards_0.3.1.py [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.3 -> 0.3.1: + ShSnd; ShCore: collect / grow / placeTotem became wrappers (+ collect0 / grow0 / placeTotem0 = the 0.3
                bodies, compared instruction for instruction below), the plugin setup, the kit's rows / version texts only
  SND  EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py Stage): tools/soundpass_gen.unit (file, rows, the kit's check=
       hook, ids, gate, the per-player switch settings:sounds:<uuid>, missing id, offline, ok()); THE WRAPPERS, REAL, with a stand-in
       online player: Collect / Grow / Place on a profile without a shard = refused ("-") = silent; the sting per wrapper through ShSnd.ok
       with the result each wrapper hands it ("+Collected ..." -> collect sting, "+Placed ..." -> totem sting, "+The ... grew" -> grow
       sting; muted = silent); static: each wrapper = body + ShSnd.ok(u, r, <its sound>) and nothing else, the bodies are byte-for-byte
       the 0.3 methods (renamed), only ShSnd.playTo calls SoundUtil; KIT end to end
  X    0.3's exec phase (every 0.3 path incl. X8 Collect, X10 Grow, X16 / X17 Place on the REAL code) on the 0.3.1 jar - the wrappers run
       on every call there (no Universe in that JVM, so the stings find no player: the results must be exactly 0.3's)
  P, CMP 0.3's parse / 0.2-compare phases on the 0.3.1 jar (CMP: the extra new class ShSnd is a note, nothing else)
  D    start twice on a scratch COPY of the live mods folder: start 1 writes only config.properties + sounds.properties into the new
       Skyy_SkyyShards folder (the live data has none yet), start 2 nothing; the copied Skyy_SkyyIslands stays byte-identical
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import perfworld_kit as PW
import soundpass_kit as SK
import soundpass_gen as G

VERSION = "0.3.1"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyShards-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyShards-0.3.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound2", "shards")))
PKG = "com.skyy.shards."
_argv = list(sys.argv)
sys.argv = [sys.argv[0]]       # the 0.3 module reads --jar / --dir at import: keep it on its own defaults
_spec = importlib.util.spec_from_file_location("ts03", os.path.join(HERE, "test_skyyshards_0.3.py"))
T3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T3)
sys.argv = _argv
LIVE_DIR = T3.LIVE_DIR
SOUNDS = [dict(key="collect", field="COLLECT", label="Shard collect", id="SFX_Crystal_Hit", help="Collect took items out of a shard island."),
          dict(key="totem", field="TOTEM", label="Totem placed", id="SFX_Deployable_Totem_Heal_Spawn", help="A totem was placed on a shard island pad."),
          dict(key="grow", field="GROW", label="Island grown", id="SFX_Workbench_Upgrade_Complete_Default", help="A shard island grew to Medium or Large.")]
EXPECT = {
    "ShCore": ["+m collect0", "+m grow0", "+m placeTotem0", "~m collect", "~m grow", "~m placeTotem"],
    "SkyyShardsPlugin": ["~m setup"],
    "ShStore": ["~m save"],                       # the version in the shard file's comment line ("SkyyShards 0.3.1 - one profile's shards")
    "CfgFile": ["~<clinit>", "~m init"],
    "CfgRows": ["+f DL1", "~<clinit>", "~m defLines", "~m header"],
    "CfgFn": ["~m opExport"],
}
ADDED = ["ShSnd"]


def run_snd(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    st = SK.Stage()
    ua = T3.OWNER
    pa = st.player("Alice", ua)
    st.player("Bob", T3.VISITOR)
    st.universe()
    P = lambda n: JClass(PKG + n)
    Snd, Rows, Fn, CP = P("ShSnd"), P("CfgRows"), P("CfgFn"), P("CfgPub")
    G.unit(K, st, Snd, Rows, Fn, pa, ua, "SkyyShards", SOUNDS, os.path.join(scratch, "unit", "Skyy_SkyyShards"))
    Cfg, St, Core = P("ShCfg"), P("ShStore"), P("ShCore")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    base = os.path.join(scratch, "snd-x")       # not "x": the 0.3 exec phase owns scratch/x
    os.makedirs(base, exist_ok=True)
    Cfg.DIR = Paths.get(base)
    Cfg.FILE = Paths.get(os.path.join(base, "config.properties"))
    Cfg.loadCfg(True)
    St.DIR = Paths.get(os.path.join(base, "shards"))
    Cfg.ON = True
    u = UUID.fromString(ua)
    br = G.bridge(st.J)

    def fresh():
        Snd.LAST.clear()
        st.clear()
    # ---- the wrappers, REAL: a profile without a shard = refused = silent
    fresh()
    rc, rg, rp = str(Core.collect(u, ua, -1, None)), str(Core.grow(u, ua, 0, None)), str(Core.placeTotem(u, ua, 0, 0, 0, None))
    K.check(rc[:1] in "-=" and rg[:1] in "-=" and rp[:1] in "-=" and st.sounds() == [], "SITE Collect / Grow / Place refused (no shard): silent: %s | %s | %s" % (rc, rg, rp))
    rc2 = str(Core.collect(u, ua, 2, -1, None))
    K.check(rc2[:1] in "-=" and st.sounds() == [], "SITE the 5-argument Collect (another kind) refused: silent: %s" % rc2)
    # ---- the sting each wrapper hands its result to: ShSnd.ok(u, r, 0 | 1 | 2)
    for w, res, sid in ((0, "+Collected 64 Wheat.", "SFX_Crystal_Hit"), (1, "+Placed Harvest Spirit Totem I on island 1 (pad 1 of 2).", "SFX_Deployable_Totem_Heal_Spawn"),
                        (2, "+The Wheat island grew to Medium.", "SFX_Workbench_Upgrade_Complete_Default")):
        fresh()
        K.check(bool(Snd.ok(u, res, w)) and st.sounds() == [("Alice", sid, "UI", "2d")], "SITE %s -> %s to that player only" % (res[:30], sid))
    fresh()
    br.put("settings:sounds:" + ua, JClass("java.lang.Boolean").FALSE)
    K.check(not bool(Snd.ok(u, "+Collected 64 Wheat.", 0)) and st.sounds() == [], "SITE muted in /settings: silent")
    br.remove("settings:sounds:" + ua)
    # ---- static: the wrappers and the renamed bodies
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["ShSnd.playTo"], "STATIC only ShSnd.playTo calls SoundUtil")
    for m, body, w in (("collect", "collect0", 0), ("grow", "grow0", 2), ("placeTotem", "placeTotem0", 1)):
        K.check(g.get("ShCore." + m, set()) >= {PKG + "ShCore." + body, PKG + "ShSnd.ok"}, "STATIC ShCore.%s = %s + ShSnd.ok" % (m, body))
    gen = open(os.path.join(HERE, "build_skyyshards_%s.py" % VERSION), encoding="utf8").read()
    for m, body, w in (("collect", "collect0", 0), ("grow", "grow0", 2), ("placeTotem", "placeTotem0", 1)):
        K.check(("String r = %s(" % body) in gen and ("@PKG@.ShSnd.ok(u, r, %d); return r; }" % w) in gen, "STATIC the %s wrapper hands its result to sound %d" % (m, w))
    old = open(os.path.join(HERE, "build_skyyshards_0.3.py"), encoding="utf8").read()

    def body_of(src, head):
        i = src.index(head)
        return src[i:src.index('}""")', i)]
    for m in ("collect", "grow", "placeTotem"):
        o = body_of(old, "public static String %s(java.util.UUID u, String k, int kd," % m)
        n = body_of(gen, "public static String %s0(java.util.UUID u, String k, int kd," % m)
        n = n.split("\n", 1)
        o = o.split("\n", 1)
        K.check(n[1] == o[1] and n[0].startswith(o[0].replace(m + "(", m + "0(")), "STATIC %s0 = the 0.3 %s body, only renamed" % (m, m))
    K.check(gen.index("@PKG@.ShSnd.load(dir);") < gen.index("@PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());"), "STATIC sounds.properties read before the kit starts")
    G.kit_set(K, st.J, Snd, CP, Fn, os.path.join(scratch, "kit", "mods"), "SkyyShards", SOUNDS)
    K.save()


def run_exec(out, jar, scratch, home):
    return T3.run_exec(out, jar, scratch, home)


def run_parse(out, jar, scratch, home):
    return T3.run_parse(out, jar, scratch, home)


def run_cmp02(out, jar, scratch, home):
    """0.3's 0.2 -> 0.3 compare on the 0.3.1 jar: its "new classes" list now also has ShSnd (0.3.1's) - exactly that one difference
    becomes a note; anything else stays a failure"""
    T3.run_cmp02(out, jar, scratch, home)
    d = json.load(open(out))
    keep, moved = [], []
    for f in d["fails"]:
        if f.startswith("C02: the new classes") and "'ShSnd'" in f and f.split("got ")[1].replace(", 'ShSnd'", "").split(", want ")[0] == f.split("want ")[1]:
            moved.append(f)
        else:
            keep.append(f)
    d["fails"] = keep
    d["notes"] = d.get("notes", []) + ["C02: + ShSnd is 0.3.1's own class (the only extra): %s" % m[:80] for m in moved]
    json.dump(d, open(out, "w"), indent=1)


def run_live(out, jar, scratch, home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    Cfg, Snd, CP = JClass(PKG + "ShCfg"), JClass(PKG + "ShSnd"), JClass(PKG + "CfgPub")
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    isl = os.path.join(mods, "Skyy_SkyyIslands")
    h0 = HK.tree_hash(isl) if os.path.isdir(isl) else None
    sh = os.path.join(mods, "Skyy_SkyyShards")
    had = os.path.isdir(sh)
    K.notes.append("D the live data %s Skyy_SkyyShards folder" % ("HAS a" if had else "has no"))
    snaps = []
    before = HK.tree_hash(sh) if had else {}
    for start in (1, 2):
        Cfg.DIR = Paths.get(sh)
        Cfg.FILE = Paths.get(os.path.join(sh, "config.properties"))
        Cfg.loadCfg(True)
        t = str(Snd.load(Paths.get(sh)))
        CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyShards"))
        K.check(t == "sounds on (3 of 3)" and int(Snd.WARNS.get()) == 0, "DS%d: the sound defaults: %s" % (start, t))
        CP.shutdown()
        snaps.append(HK.tree_hash(sh))
    G.live_twice(K, before, snaps[0], snaps[1], also=("config.properties",) if not had else ())
    if h0 is not None:
        K.check(HK.tree_hash(isl) == h0, "D the copied Skyy_SkyyIslands is byte-identical")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyShards", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("snd", run_snd), ("exec", run_exec), ("parse", run_parse), ("cmp02", run_cmp02), ("live", run_live)], script=__file__,
           live=(os.path.join(LIVE_DIR, "Skyy_SkyyIslands"), "mods/Skyy_SkyyIslands"))
