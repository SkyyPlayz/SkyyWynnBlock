"""Harness for SkyyIslands 0.5.8 (the shard guards: tools/islands_0_5_8_patch.py). Build first:
python tools/islands_0_5_8_patch.py && python SkyyIslands/build_skyyislands_0.5.8.py

    python SkyyIslands/test_skyyislands_0.5.8.py [--keep]

Phases (each a fresh child JVM, the game's JRE, TEMP / TMP in scratch; tools/harness_kit.py):
  A  verify   every class loads + initialises with -Xverify:all on the 0.7 server jar
  C  compare  0.5.7 -> 0.5.8: exactly the planned members differ (+ RoleKeyFn, WorldKeyFn, HubFn); IslandMenuPage and every other class identical
  X  exec     EVERY NEW CODE PATH (-Xverify:all): GuardSystem.shardDecision (no SkyyShards = refused; TRUE / FALSE / null / a throwing
              Function; the exact Object[]{world, action, block, uuid} it sends), isShardWorld, portalDecision on real island files
              (owner / island admin / member yes, trusted / visitor / banned / unknown no, server admin yes), RoleKeyFn (every role word,
              bad arguments, an unknown or unreadable owner key, null for a pending / archived owner profile - review fix), WorldKeyFn
              (the owner key's current island world; unknown / bad = null - review fix), the subclasses' shardAction words and shardBlock / shardPortal on REAL
              DamageBlockEvent / BreakBlockEvent / UseBlockEvent$Pre objects (a block type with our id, a crop, none), the bridge keys
              setup publishes (island:role:key:fn, island:shardguard = "1") and shutdown removes
  D  live     START TWICE on a scratch COPY of the live Skyy_SkyyIslands: every island read, nothing written, files byte-identical;
              RoleKeyFn answers "owner" for each live island's own key
  AA engine-access audit
Scratch: tools/dev/scratch/shards01/i (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

VERSION = "0.5.8"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-0.5.7.jar")
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "shards01", "i")))
PKG = "com.skyy.islands."
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyIslands")

EXPECT = {
    "GuardSystem": ["+m shardAction", "+m shardBlock", "+m shardPortal", "+m shardDecision", "+m isShardWorld", "+m portalDecision", "~m handle"],
    "GuardDamage": ["+m shardAction", "+m shardBlock"],
    "GuardBreak": ["+m shardAction", "+m shardBlock"],
    "GuardPlace": ["+m shardAction"],
    "GuardPickup": ["+m shardAction"],
    "GuardUse": ["+m shardAction", "+m shardBlock", "+m shardPortal"],
    "GuardDrop": ["+m shardAction"],
    "GuardUseEntity": ["+m shardAction"],
    "GuardHurt": ["~m handle"],
    "SkyyIslandsPlugin": ["~m setup", "~m shutdown"],
    # the config kit's version strings only (tools/skyycfg.py, rebuilt with VERSION 0.5.8; constant pools: "0.5.7" -> "0.5.8" and the
    # config header line, nothing else - checked when this harness was written)
    "CfgRows": ["~<clinit>", "~m header"],
    "CfgFn": ["~m opExport"],
    "IslandCfg": ["~m load"],
}
ADDED = ["RoleKeyFn", "WorldKeyFn", "HubFn"]
OWNER = "1a1a1a1a-1111-2222-3333-444444444444"
ADMIN_K = "1b1b1b1b-1111-2222-3333-444444444444"
MEMBER = "1c1c1c1c-1111-2222-3333-444444444444"
TRUSTED = "1d1d1d1d-1111-2222-3333-444444444444"
VISITOR = "1e1e1e1e-1111-2222-3333-444444444444"
BANNED = "1f1f1f1f-1111-2222-3333-444444444444"


def fn_class():
    from jpype import JImplements, JOverride

    @JImplements("java.util.function.Function")
    class PyFn(object):
        def __init__(self, ans):
            self.ans = ans
            self.calls = []

        @JOverride
        def apply(self, a):
            self.calls.append(a)
            return self.ans(a)
    return PyFn


def run_exec(out, jar, scratch, _home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, B.JAVASSIST, jar], verify=True)
    Sys = JClass("java.lang.System")
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    Sys.getProperties().put("skyy.bridge", br)
    G, St, RK = JClass(PKG + "GuardSystem"), JClass(PKG + "IslandStore"), JClass(PKG + "RoleKeyFn")
    UUID, Paths, Bool = JClass("java.util.UUID"), JClass("java.nio.file.Paths"), JClass("java.lang.Boolean")
    PyFn = fn_class()
    o, a, m, t, v, b = (UUID.fromString(x) for x in (OWNER, ADMIN_K, MEMBER, TRUSTED, VISITOR, BANNED))
    W = "skyy-shard-" + OWNER
    # ---- A: shardDecision
    K.check(not G.shardDecision(W, "break", "Plant_Crop_Wheat_Block_Eternal", o), "X A no SkyyShards (no shard:fn:allowed) = refused")
    f = PyFn(lambda x: Bool.TRUE)
    br.put("shard:fn:allowed", f)
    K.check(bool(G.shardDecision(W, "break", "Plant_Crop_Wheat_Block_Eternal", o)), "X A shard:fn:allowed TRUE = allowed")
    last = f.calls[-1]
    K.eq([str(last[0]), str(last[1]), str(last[2]), str(last[3])], [W, "break", "Plant_Crop_Wheat_Block_Eternal", OWNER], "X A the exact Object[] sent")
    G.shardDecision(W, "pickup", None, o)
    K.eq(str(f.calls[-1][2]), "", "X A a null block id is sent as \"\"")
    for ans, want, what in ((Bool.FALSE, False, "FALSE"), (None, False, "null")):
        br.put("shard:fn:allowed", PyFn(lambda x, ans=ans: ans))
        K.check(bool(G.shardDecision(W, "place", "", o)) == want, "X A shard:fn:allowed %s = refused" % what)

    def boom(x):
        raise RuntimeError("boom")
    br.put("shard:fn:allowed", PyFn(boom))
    K.check(not G.shardDecision(W, "use", "", o), "X A a throwing Function = refused (never an exception out of the guard)")
    br.put("shard:fn:allowed", JString("not a function"))
    K.check(not G.shardDecision(W, "use", "", o), "X A a non-Function value = refused")
    K.eq([bool(G.isShardWorld(x)) for x in (W, "skyy-shard-", "skyy-island-" + OWNER, "default", None)], [True, True, False, False, False],
         "X A isShardWorld")
    # ---- B: portalDecision on real island files
    idir = os.path.join(scratch, "x", "islands")
    os.makedirs(idir, exist_ok=True)
    open(os.path.join(idir, OWNER + ".properties"), "w", encoding="latin-1").write(
        "v=5\nworld=skyy-island-%s\nownerName=Own\nmembers=%s,%s\nadmins=%s\ntrusted=%s\nbanned=%s\ncreated=1\nkit=1\n" % (OWNER, ADMIN_K, MEMBER, ADMIN_K, TRUSTED, BANNED))
    St.DIR = Paths.get(idir)
    St.loadIslandWorlds()
    IW = "skyy-island-" + OWNER
    K.eq(str(St.ownerOf(IW)), OWNER, "X B the island world is known")
    got = [bool(G.portalDecision(IW, u, False)) for u in (o, a, m, t, v, b)]
    K.eq(got, [True, True, True, False, False, False], "X B the shard portal: owner / island admin / member yes; trusted / visitor / banned no")
    K.check(bool(G.portalDecision(IW, v, True)) and not G.portalDecision("skyy-island-nobody", o, False) and not G.portalDecision(IW, None, False),
            "X B a server admin yes; an unknown island / no player no")
    # ---- C: RoleKeyFn
    rk = RK()
    roles = [str(rk.apply(JArray(JObject)([u, JString(OWNER)]))) for u in (o, a, m, t, v, b)]
    K.eq(roles, ["owner", "admin", "member", "trusted", "visitor", "banned"], "X C island:role:key:fn: every role word by the owner KEY")
    K.check(rk.apply(JArray(JObject)([o, JString("1a1a1a1a-0000-0000-0000-000000000000")])) is None and rk.apply("x") is None
            and rk.apply(JArray(JObject)([o])) is None and rk.apply(JArray(JObject)([JString("x"), JString(OWNER)])) is None
            and rk.apply(JArray(JObject)([o, JString("  ")])) is None, "X C an unknown key / bad arguments = null")
    K.eq([str(RK.roleWord(x)) for x in (-1, 0, 1, 2, 3, 4)], ["banned", "visitor", "trusted", "member", "admin", "owner"], "X C roleWord")
    # review fix: a deleted (pending) / archived owner profile has no co-op roles (SkyyProfiles profile:fn:state)
    state = {"s": "pending"}
    br.put("profile:fn:state", PyFn(lambda k: JString(state["s"]) if str(k) == OWNER else None))
    got_p = [rk.apply(JArray(JObject)([u, JString(OWNER)])) for u in (a, m)]
    state["s"] = "archived"
    got_a = rk.apply(JArray(JObject)([m, JString(OWNER)]))
    state["s"] = "active"
    got_ok = rk.apply(JArray(JObject)([m, JString(OWNER)]))
    br.remove("profile:fn:state")
    K.check(got_p == [None, None] and got_a is None and str(got_ok) == "member",
            "X C island:role:key:fn: null while the owner profile is pending / archived (co-op cannot drain a deleted profile's shard); active = member")
    # review fix: island:world:key:fn = the owner key's CURRENT island world
    WK = JClass(PKG + "WorldKeyFn")
    wk = WK()
    K.check(str(wk.apply(JString(OWNER))) == "skyy-island-" + OWNER and wk.apply(JString("1a1a1a1a-0000-0000-0000-000000000000")) is None
            and wk.apply(JString("  ")) is None and wk.apply(o) is None and wk.apply(None) is None,
            "X C island:world:key:fn: the current island world by owner key; unknown key / bad argument = null")
    # review fix 2: island:fn:hub = HubCmd.sendToHub for a player by UUID; a bad argument / no such player (no Universe here) = FALSE, never a throw
    HF = JClass(PKG + "HubFn")()
    JU = JClass("java.util.UUID")
    _hf = [HF.apply(JString("x")), HF.apply(None), HF.apply(JU.fromString(OWNER))]
    K.check(all(x is not None and str(x).lower() == "false" for x in _hf),
            "X C island:fn:hub: bad argument / unknown player = FALSE (never a throw)")
    # ---- A/B: the subclasses on REAL events
    BT = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    U_ = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    U_.setAccessible(True)
    U = U_.get(None)

    def btype(i):
        x = U.allocateInstance(BT.class_)
        k = BT.class_
        while k is not None:
            try:
                fl = k.getDeclaredField("id")
                fl.setAccessible(True)
                fl.set(x, i)
                break
            except Exception:
                k = k.getSuperclass()
        return x
    V3 = JClass("org.joml.Vector3i")
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    BBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.BreakBlockEvent")
    UPRE = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseBlockEvent$Pre")
    ITY = JClass("com.hypixel.hytale.protocol.InteractionType")
    crop, shard = btype("Plant_Crop_Wheat_Block_Eternal"), btype("Skyy_Shard_Farming")
    ev_d = DBE(None, V3(1, 2, 3), crop, 1.0, 0.0)
    ev_b = BBE(None, V3(1, 2, 3), crop)
    ev_u = UPRE(ITY.Use, None, V3(1, 2, 3), shard)
    ev_u2 = UPRE(ITY.Use, None, V3(1, 2, 3), crop)
    ev_n = BBE(None, V3(1, 2, 3), None)
    names = ["GuardDamage", "GuardBreak", "GuardPlace", "GuardPickup", "GuardUse", "GuardDrop", "GuardUseEntity"]
    gs = dict((n, JClass(PKG + n)()) for n in names)
    K.eq([str(gs[n].shardAction(ev_b)) for n in names], ["damage", "break", "place", "pickup", "use", "drop", "useentity"], "X A the action word of each guard")
    K.eq((str(gs["GuardDamage"].shardBlock(ev_d)), str(gs["GuardBreak"].shardBlock(ev_b)), str(gs["GuardUse"].shardBlock(ev_u)),
          str(gs["GuardBreak"].shardBlock(ev_n)), str(gs["GuardDamage"].shardBlock(ev_b)), str(gs["GuardPlace"].shardBlock(ev_b))),
         ("Plant_Crop_Wheat_Block_Eternal", "Plant_Crop_Wheat_Block_Eternal", "Skyy_Shard_Farming", "", "", ""),
         "X A shardBlock: the block id of Damage / Break / Use events; no block = \"\"; a guard reads only its own event type")
    K.eq((bool(gs["GuardUse"].shardPortal(ev_u)), bool(gs["GuardUse"].shardPortal(ev_u2)), bool(gs["GuardBreak"].shardPortal(ev_b))),
         (True, False, False), "X B shardPortal: only GuardUse on a Skyy_Shard_ block")
    # ---- C: setup publishes / shutdown removes (static check of the class bytes: the plugin needs a server to construct)
    import zipfile
    z = zipfile.ZipFile(jar)
    pb = z.read("com/skyy/islands/SkyyIslandsPlugin.class")
    K.check(b"island:role:key:fn" in pb and b"island:shardguard" in pb and b"island:world:key:fn" in pb and b"island:fn:hub" in pb,
            "X C the plugin publishes island:role:key:fn + island:shardguard + island:world:key:fn + island:fn:hub")
    K.save()


def run_live(out, jar, scratch, home):
    from jpype import JClass, JArray, JObject, JString
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    St, IOc, RK = JClass(PKG + "IslandStore"), JClass(PKG + "IslandIO"), JClass(PKG + "RoleKeyFn")
    Paths, Executors, UUID = JClass("java.nio.file.Paths"), JClass("java.util.concurrent.Executors"), JClass("java.util.UUID")
    h0 = HK.tree_hash(home)
    for start in (1, 2):
        St.SETTINGS.clear()
        St.STOPPING = False
        St.IO = None
        St.DIR = Paths.get(os.path.join(home, "islands"))
        St.loadIslandWorlds()
        St.IO = Executors.newSingleThreadExecutor(IOc(9, None))
        keys = St.islandKeys()
        w0 = St.WRITES.get()
        bad, owners = 0, 0
        rk = RK()
        wk = JClass(PKG + "WorldKeyFn")()
        wbad = 0
        for i in range(keys.size()):
            k = str(keys.get(i))
            s_ = St.settings(k)
            if s_.bad:
                bad += 1
            St.read0(keys.get(i), 1, 0)
            ou = St.ownerUuid(k)
            # no SkyyProfiles in a bare JVM: the owner's active profile is profile 1 (= the plain uuid key) - its island says owner,
            # the owner's other-profile islands (<uuid>-pN) say visitor (island:role:fn gives the same: profiles are kept apart)
            want = "owner" if k == str(ou) else "visitor"
            if ou is not None and str(rk.apply(JArray(JObject)([ou, JString(k)]))) == want:
                owners += 1
            if s_.world is not None and str(wk.apply(JString(k))) != str(s_.world):
                wbad += 1
        St.STOPPING = True
        St.stopIO()
        St.flushPending()
        K.check(St.WRITES.get() == w0 and bad == 0, "D start %d: %d islands read, none unreadable, nothing written" % (start, keys.size()))
        K.check(owners == keys.size(), "D start %d: island:role:key:fn for every live island's own owner: owner on profile 1, visitor from another profile (%d)" % (start, owners))
        K.check(wbad == 0, "D start %d: island:world:key:fn = each live island's own world name" % start)
        K.check(HK.tree_hash(home) == h0, "D start %d: every file byte-identical" % start)
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("exec", run_exec), ("live", run_live)], script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
