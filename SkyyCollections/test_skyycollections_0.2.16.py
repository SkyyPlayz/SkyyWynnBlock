"""Harness for SkyyCollections 0.2.16 (SOUND PASS ROUND 2: tier up / late reward + the per-player sound switch;
tools/collections_0_2_16_patch.py). Build first:
    python tools/collections_0_2_16_patch.py && python SkyyCollections/build_skyycollections_0.2.16.py

    python SkyyCollections/test_skyycollections_0.2.16.py [--jar <SkyyCollections-0.2.16.jar>] [--dir <scratch>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py):
  A   verify   every class loads + initialises with -Xverify:all
  C   compare  0.2.15 -> 0.2.16: + CollSnd; CollCredit.announce / creditOne, CollRewards.giveTier, the plugin setup, the kit's rows /
               version texts only
  SND EXECUTED through the ENGINE's own send path (tools/soundpass_kit.py Stage): tools/soundpass_gen.unit (file, rows, the kit's check=
      hook, ids, gate, the per-player switch settings:sounds:<uuid>, missing id, offline, ok()); THE CALL SITE, REAL: CollCredit.creditShard
      (the credit path every gathered item takes) on a REAL registry + counts file with a stand-in online player: 300 Raw Chicken crosses
      tiers I..III = the COLLECTION UP chat line(s) AND ONE tier sting (UI 2D, that player only); a credit inside a tier = no sting; the
      player MUTED in /settings = the chat line, no sting; the "Collection tier-ups" setting off (settings:fn:get FALSE) = neither; the
      rankup route Off = neither; the late reward: CollSnd.reward plays, held (inside a tier-up's settle) = silent; static: giveTier's
      "in your inventory" line plays CollSnd.reward, creditOne holds around its settle (try / finally), only CollSnd.playTo calls SoundUtil;
      KIT end to end (cmdSetConsole edits, file lines)
  D   live     0.2.15's start-twice phase on a scratch COPY of the live Skyy_SkyyCollections, then the 0.2.16 data steps + CollSnd.load +
               the kit TWICE (fresh class loaders = restarts): the first adds only sounds.properties (+ kit files), the second nothing
  AA  audit    the engine-access audit
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

_spec = importlib.util.spec_from_file_location("tc0215", os.path.join(HERE, "test_skyycollections_0.2.15.py"))
T15 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T15)

VERSION = "0.2.16"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyCollections-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyCollections-0.2.15.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sound2", "coll")))
PKG = "com.skyy.collections."
LIVE_DIR = T15.LIVE_DIR
SOUNDS = [dict(key="tier", field="TIER", label="Collection tier up", id="SFX_Memories_Unlock_Local",
               help="A collection reached a new tier (with the COLLECTION UP line)."),
          dict(key="reward", field="REWARD", label="Late reward", id="SFX_Chest_Wooden_Open_Player",
               help="An owed item reward landed in the inventory later.")]
EXPECT = {"CfgFile": ["~<clinit>", "~m init"], "CfgFn": ["~m opExport"], "CfgRows": ["+f DL3", "~<clinit>", "~m defLines", "~m header"],
          "CollCredit": ["~m announce", "~m creditOne"], "CollRewards": ["~m giveTier"], "SkyyCollectionsPlugin": ["~m setup"]}
ADDED = ["CollSnd"]


def loader_for(jar):
    from jpype import JClass, JArray
    URL = JClass("java.net.URL")
    arr = JArray(URL)(1)
    arr[0] = JClass("java.io.File")(jar).toURI().toURL()
    return JClass("java.net.URLClassLoader")(arr, JClass("java.lang.ClassLoader").getSystemClassLoader())


def run_snd(out, jar, scratch, _home):
    from jpype import JClass, JLong, JImplements, JOverride
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    st = SK.Stage()
    ua = T15.OWNER
    pa = st.player("Alice", ua)
    pb = st.player("Bob", "0f0f0f0f-1111-2222-3333-555555555555")
    st.universe()
    P = lambda n: JClass(PKG + n)
    Snd, Rows, Fn, CP = P("CollSnd"), P("CfgRows"), P("CfgFn"), P("CfgPub")
    G.unit(K, st, Snd, Rows, Fn, pa, ua, "SkyyCollections", SOUNDS, os.path.join(scratch, "unit", "Skyy_SkyyCollections"))
    Reg, Store, Util, Cred = P("CollReg"), P("CollStore"), P("CollUtil"), P("CollCredit")
    Paths, UUID = JClass("java.nio.file.Paths"), JClass("java.util.UUID")
    base = os.path.join(scratch, "x", "Skyy_SkyyCollections")
    os.makedirs(base)
    Reg.BASE = Paths.get(base)
    Store.DIR = Paths.get(base).resolve("counts")
    Reg.loadAll()
    R = Reg.D
    ou = UUID.fromString(ua)
    key = str(Util.pkey(ou))
    br = G.bridge(st.J)

    def item(cid):
        return str(list(R.items[int(R.byId.get(cid.lower()))])[0])

    def fresh():
        Snd.LAST.clear()
        st.clear()
    # ---- THE CALL SITE, REAL: the credit path with an online player
    fresh()
    Cred.creditShard(pa, ou, key, item("RawChicken"), JLong(256))
    Cred.creditShard(pa, ou, key, item("RawChicken"), JLong(44))
    ch = [t for w, t in st.chats("Alice")]
    ups = [t for t in ch if "COLLECTION UP" in t.upper() or "Raw Chicken" in t]
    K.check(len(ups) >= 1, "SITE 300 Raw Chicken crossed tiers: the COLLECTION UP line(s) were sent: %s" % ch[:4])
    K.eq(st.sounds(), [("Alice", "SFX_Memories_Unlock_Local", "UI", "2d")], "SITE ... AND ONE tier sting to that player only (several tiers in one moment = one sting)")
    K.check(not st.chats("Bob") and not st.sounds("Bob"), "SITE Bob got nothing")
    fresh()
    Cred.creditShard(pa, ou, key, item("RawChicken"), JLong(1))
    K.check(st.sounds() == [], "SITE a credit inside a tier: no sting")
    # muted in /settings: the line, no sting
    fresh()
    br.put("settings:sounds:" + ua, JClass("java.lang.Boolean").FALSE)
    Cred.creditShard(pa, ou, key, item("Wheat"), JLong(256))
    ch = [t for w, t in st.chats("Alice")]
    K.check(len(ch) >= 1 and st.sounds() == [], "SITE the player MUTED every sound in /settings: the chat line(s), no sting: %s" % ch[:2])
    br.remove("settings:sounds:" + ua)

    @JImplements("java.util.function.Function")
    class Get(object):
        def __init__(self, ans):
            self.ans = ans

        @JOverride
        def apply(self, a):
            return JClass("java.lang.Boolean").FALSE if str(a[1]) == self.ans else JClass("java.lang.Boolean").TRUE
    # the "Collection tier-ups" setting off: neither line nor sting
    fresh()
    br.put("settings:fn:get", Get("coll.tierUp"))
    Cred.creditShard(pa, ou, key, item("Copper"), JLong(256))
    K.check(st.sounds() == [] and not any("COLLECTION UP" in t for w, t in st.chats("Alice")),
            "SITE 'Collection tier-ups' off in /settings: no tier line, no sting: %s %s" % (st.sounds(), st.chats("Alice")[:3]))
    br.remove("settings:fn:get")
    # the rankup route Off (SkyyHud msgroute): neither
    @JImplements("java.util.function.Function")
    class Route(object):
        @JOverride
        def apply(self, a):
            return "off" if str(a[1]) == "rankup" else "chat"
    fresh()
    br.put("msgroute:fn:get", Route())     # Bob: a player whose route was never asked (MsgRoute caches a route 2 s per player + kind)
    ob = UUID.fromString("0f0f0f0f-1111-2222-3333-555555555555")
    Cred.creditShard(pb, ob, str(Util.pkey(ob)), item("OakLog"), JLong(256))
    K.check(st.sounds() == [] and not any("COLLECTION UP" in t for w, t in st.chats("Bob")), "SITE the rankup route Off: no tier line, no sting: %s %s" % (st.sounds(), st.chats("Bob")[:3]))
    br.remove("msgroute:fn:get")
    # ---- the late reward sting + the hold
    fresh()
    K.check(bool(Snd.reward(pa)) and st.sounds() == [("Alice", "SFX_Chest_Wooden_Open_Player", "UI", "2d")], "SITE a late item reward: the reward sting")
    fresh()
    Snd.hold(ou, True)
    K.check(not bool(Snd.reward(pa)) and st.sounds() == [], "SITE a reward inside a tier-up moment (held): silent")
    Snd.hold(ou, False)
    K.check(bool(Snd.reward(pa)) and len(st.sounds()) == 1 and Snd.QUIET.isEmpty(), "SITE released: plays again; nothing left held")
    K.check(not bool(Snd.reward(None)), "SITE no player: nothing")
    # ---- static
    g = PW.calls(jar)
    su = "com.hypixel.hytale.server.core.universe.world.SoundUtil"
    K.eq(sorted(m for m, cs in g.items() if any(c.startswith(su + ".") for c in cs)), ["CollSnd.playTo"], "STATIC only CollSnd.playTo calls SoundUtil")
    K.check(PKG + "CollSnd.playTo" in g.get("CollCredit.announce", set()) and PKG + "CollSnd.reward" in g.get("CollRewards.giveTier", set())
            and PKG + "CollSnd.hold" in g.get("CollCredit.creditOne", set()) and PKG + "CollSnd.load" in g.get("SkyyCollectionsPlugin.setup", set()),
            "STATIC announce plays the tier sting, giveTier the reward sting, creditOne holds, setup loads the file")
    gen = open(os.path.join(HERE, "build_skyycollections_%s.py" % VERSION), encoding="utf8").read()
    a0 = gen.index("@PKG@.CollSnd.hold(u, true);")
    K.check(a0 < gen.index("try { paid = @PKG@.CollRewards.settle(d, R, c, u, key); } finally { @PKG@.CollSnd.hold(u, false); }", a0) < gen.index("if (tierOn) announce(pr, R, c, ot + 1, nt);", a0),
            "STATIC creditOne: hold -> settle -> release (finally) -> announce")
    K.check(gen.index("@PKG@.CollSnd.load(base);") < gen.index("@PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());"), "STATIC sounds.properties read before the kit starts")
    G.kit_set(K, st.J, Snd, CP, Fn, os.path.join(scratch, "kit", "mods"), "SkyyCollections", SOUNDS)
    K.save()


def run_live(out, jar, scratch, home):
    tmp = os.path.join(scratch, "live15.json")
    T15.run_live(tmp, jar, scratch, home)
    from jpype import JClass
    prev = json.load(open(tmp))
    K = HK.Child(out)
    K.ok, K.fails, K.notes = prev["ok"], list(prev["fails"]), list(prev["notes"])
    Paths = JClass("java.nio.file.Paths")
    mods = os.path.dirname(home)
    h0 = HK.tree_hash(home)
    snaps = []
    for start in (1, 2):
        L = loader_for(jar)
        P = lambda n: JClass(PKG + n, loader=L)
        b_ = Paths.get(home)
        P("CollReg").BASE = b_
        P("CollStore").DIR = b_.resolve("counts")
        P("CollReg").loadAll()
        Snd, CP = P("CollSnd"), P("CfgPub")
        t = str(Snd.load(b_))
        CP.start(Paths.get(mods), JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyCollections"))
        K.check(t == "sounds on (2 of 2)" and int(Snd.WARNS.get()) == 0, "DS%d: the live copy reads the sound defaults: %s" % (start, t))
        CP.shutdown()
        snaps.append(HK.tree_hash(home))
    G.live_twice(K, h0, snaps[0], snaps[1])
    K.check(open(os.path.join(home, "sounds.properties"), encoding="latin-1").read() == G.file_text("SkyyCollections", SOUNDS), "DS: sounds.properties = the default text")
    K.save()


if __name__ == "__main__":
    HK.run("SkyyCollections", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("snd", run_snd), ("live", run_live)], __file__, live=(LIVE_DIR, "Skyy_SkyyCollections"))
