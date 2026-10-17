"""Harness for SkyyIslands 0.5.19 (NAMED ISLAND HOMES: /island sethome [name] | /island <home> | delhome <name> | homes, the homes/<profile
key>.properties files, Server Setup homes.max, island:fn:homes / island:fn:gohome; tools/islands_0_5_19_patch.py).
Build first: python tools/islands_0_5_19_patch.py && python SkyyIslands/build_skyyislands_0.5.19.py

    python SkyyIslands/test_skyyislands_0.5.19.py [--jar <jar>] [--dir <empty folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child JVMs, tools/harness_kit.py; tools/hub_tab_kit.stage = the engine stand-ins, -Xverify:all):
  A    verify   every class loads + initialises with -Xverify:all
  C    compare  0.5.18 -> 0.5.19: exactly the expected members differ (IslandCmd go -> goAt + go / goHome / the constructor, IslandCfg
                homes.max, the config rows / header, the bridge puts in setup), the 8 new classes; non-class entries: manifest.json
  TREE the REAL /island command tree (IslandCmd constructed): sethome (+ its <name> variant), delhome <name>, homes, the /island <home>
       variant; every player node + variant carries hytale:Adventurer, reload none; required-arg counts; IslandHomes.ROOT set; every
       sub-command name AND alias of the tree (+ main, help) is refused as a home name, case-insensitively
  HOMES the logic on scratch island files (owner O, co-op member M, another owner V, a player N without an island):
       sethome refused off the ground (MovementStates: mid-air, flying, swimming, gliding, falling), allowed on the ground;
       set main / named (TransformComponent read by setHere), go-target = the saved spot, case-insensitive names, list, delete, the
       limit (default 6, full list refused, an old name moves when full, homes.max lowered = nothing deleted, 0 = off), bad names,
       sub-command words, another player's island + a non-island world refused, the co-op member's homes live on the co-op island,
       a profile switch (profile:fn:key) = another homes file, /island reset (a new world) = the homes go void (refused, removed, the main
       home falls back to the spawn with a note), leaving the co-op = void, an unreadable homes file (refused; the main home never blocks
       /island), the file format (atomic: no .tmp left), the bridge Functions (HomesFn, GoHomeFn offline / bad input) never throw
  D    live: a scratch COPY of the live Skyy_SkyyIslands: HomesFn / listText for every island owner, no file of the copy changed
  AA   engine-access audit
Not testable without the game (UNVERIFIED): the actual teleports (teleportPlayerToLoadingInstance's spawn override, the same-island
Teleport hop), the command parser picking /island <home> after the sub-command words, chat colours.
Exit code 1 on any failure.
"""
import os, sys, re, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import hub_tab_kit as HT

VERSION = "0.5.19"
OLD = "0.5.18"
PKG = "com.skyy.islands."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyIslands-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyIslands-%s.jar" % OLD)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "homes", "harness")))
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyyIslands")
ADDED = ["IslandHomes", "HomesFn", "GoHomeFn", "IslandSetHomeNameCmd", "IslandSetHomeCmd", "IslandDelHomeCmd", "IslandHomesCmd",
         "IslandGoHomeNameCmd"]
EXPECT = {"IslandCmd": ["+m goAt", "~m go", "~m goHome", "~c "],
          "IslandCfg": ["+f HOMES_MAX", "~<clinit>", "~m load"],
          "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"], "CfgFile": ["~<clinit>"],
          "SkyyIslandsPlugin": ["~m setup"]}
OWN = "00000000-0000-0000-0000-0000000019a1"
MEM = "00000000-0000-0000-0000-0000000019a2"
VIS = "00000000-0000-0000-0000-0000000019a3"
NOI = "00000000-0000-0000-0000-0000000019a4"
WORDS_EXTRA = ["main", "help"]


def prep(J, Paths, home):
    from jpype import JClass
    J("IslandStore").LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyIslands")
    b = Paths.get(home)
    J("IslandStore").DIR = b.resolve("islands")
    J("IslandCfg").FILE = b.resolve("config.properties")
    J("IslandCfg").load("Cow,Sheep,Pig,Chicken")
    J("IslandStore").HUB_FILE = b.resolve("hub.properties")
    J("IslandStore").loadHub()
    J("IslandStore").loadIslandWorlds()
    J("IslandStore").STOPPING = False


def setup(scratch, jar, home):
    from jpype import JClass
    os.makedirs(os.path.join(home, "islands"), exist_ok=True)
    E = HT.stage(scratch, jar)
    J = lambda n: JClass(PKG + n)
    prep(J, E.Paths, home)
    return E, J


def tree(icmd):
    """{path: (groups, required count, is variant)} of the real command tree"""
    from jpype import JClass
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fg = HT.jf(AC.class_, "permissionGroups")
    fr = HT.jf(AC.class_, "requiredArguments")
    out = {}

    def groups(c):
        g = fg.get(c)
        return None if g is None else [str(x) for x in g]

    def walk(c, path):
        out[path] = (groups(c), int(fr.get(c).size()), bool(c.isVariant()))
        for v in c.getVariantCommands():
            out[path + " <%d args>" % int(fr.get(v).size())] = (groups(v), int(fr.get(v).size()), bool(v.isVariant()))
        subs = c.getSubCommands()
        for k in sorted(str(x) for x in subs.keySet()):
            walk(subs.get(k), path + " " + k)
    walk(icmd, "/island")
    return out


def run_tree(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    home = os.path.join(scratch, "tree", "Skyy_SkyyIslands")
    E, J = setup(os.path.join(scratch, "tree"), jar, home)
    IH = J("IslandHomes")
    K.check(IH.ROOT is None, "TREE: IslandHomes.ROOT is empty before /island is made")
    ic = J("IslandCmd")()
    K.check(IH.ROOT is not None and E.same(IH.ROOT, ic), "TREE: the IslandCmd constructor sets IslandHomes.ROOT")
    t = tree(ic)
    for p in sorted(t):
        K.notes.append("tree %-34s groups=%s required=%d%s" % (p, t[p][0], t[p][1], " (variant)" if t[p][2] else ""))
    ADV = ["hytale:Adventurer"]
    want = {"/island": (ADV, 0, False), "/island <1 args>": (ADV, 1, True), "/island sethome": (ADV, 0, False),
            "/island sethome <1 args>": (ADV, 1, True), "/island delhome": (ADV, 1, False), "/island homes": (ADV, 0, False)}
    for p, w in sorted(want.items()):
        K.eq(t.get(p), w, "TREE: %s (groups, required args, variant)" % p)
    K.eq(t.get("/island reload"), ([], 0, False), "TREE: /island reload stays admin-only (no groups)")
    bad = [p for p, v in t.items() if p != "/island reload" and v[0] != ADV]
    K.check(not bad, "TREE: every player node / variant carries hytale:Adventurer: %s" % bad)
    K.eq(len([p for p in t if p.count(" ") == 1 and "<" not in p]), 25, "TREE: 25 sub-commands under /island (0.5.18's 22 incl. reload + sethome, delhome, homes)")
    # every name + alias of the real tree is refused (the runtime check AND the build-time list)
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    al = HT.jf(AC.class_, "subCommandsAliases").get(ic)
    words = sorted(set([str(k) for k in ic.getSubCommands().keySet()] + [str(k) for k in al.keySet()]))
    K.check(len(words) == 32 and "banlist" in words and "go" in words and "sethome" in words, "TREE: %d words (names + aliases): %s" % (len(words), words))
    K.eq(sorted(set(str(w) for w in IH.WORDS)), sorted(set(words + WORDS_EXTRA)), "TREE: IslandHomes.WORDS = every name + alias of the tree + main, help")
    notref = [w for w in words + WORDS_EXTRA if IH.bad(w) is None or IH.bad(w.upper()) is None]
    K.check(not notref, "TREE: every command word (any case) is refused as a home name: %s" % notref)
    K.check("command word" in str(IH.bad("Menu")), "TREE: the refusal names it a command word: %s" % IH.bad("Menu"))
    # the runtime check alone (a word the build-time list does not have): ROOT's getSubCommand
    K.check(bool(IH.reserved("settings")) and not bool(IH.reserved("farm")), "TREE: reserved(settings) yes, reserved(farm) no")
    K.save(tree={p: list(v) for p, v in t.items()})


def run_homes(out, jar, scratch, _home):
    from jpype import JClass, JImplements, JOverride, JArray, JObject
    K = HK.Child(out)
    base = os.path.join(scratch, "homes")
    home = os.path.join(base, "Skyy_SkyyIslands")
    os.makedirs(os.path.join(home, "islands"), exist_ok=True)
    with open(os.path.join(home, "islands", OWN + ".properties"), "w", encoding="latin-1", newline="\n") as f:
        f.write("v=5\nworld=skyy-island-harness\nownerName=Owner\nmembers=%s\nname.%s=Mem\n" % (MEM, MEM))
    with open(os.path.join(home, "islands", VIS + ".properties"), "w", encoding="latin-1", newline="\n") as f:
        f.write("v=5\nworld=skyy-island-vee\nownerName=Vee\n")
    E, J = setup(base, jar, home)
    IH, IS, CFG = J("IslandHomes"), J("IslandStore"), J("IslandCfg")
    J("IslandCmd")()                                   # IslandHomes.ROOT (the sub-command words)
    UU = E.UUID.fromString
    O, M, V, N = UU(OWN), UU(MEM), UU(VIS), UU(NOI)
    K.eq((str(IS.homeKey(O)), str(IS.homeKey(M)), str(IS.homeKey(V))), (OWN, OWN, VIS), "HOMES: home islands: O own, M = O's co-op, V own")
    K.eq(int(CFG.HOMES_MAX), 6, "HOMES: homes.max default 6 (Skyy: max of like 6)")
    W = "skyy-island-harness"
    hdir = os.path.join(home, "homes")
    hf = lambda k: os.path.join(hdir, k + ".properties")
    st = lambda r: str(r)

    def tgt(u, n):
        r = IH.target(u, n)
        if isinstance(r, str) or str(r.getClass().getName()) == "java.lang.String":
            return str(r)
        a = list(r)
        pos = None if a[1] is None else [float(x) for x in a[1]]
        rot = None if a[2] is None else [float(x) for x in a[2]]
        return (str(a[0]), pos, rot, None if a[3] is None else str(a[3]))

    # ---- setHere through the real TransformComponent + a world named like the island
    TCc = JClass("com.hypixel.hytale.server.core.modules.entity.component.TransformComponent")
    V3 = JClass("org.joml.Vector3d")
    R3 = JClass("com.hypixel.hytale.math.vector.Rotation3f")
    P = E.mkp(O, "Owner")
    P.st.row(P.ref).put(TCc.getComponentType(), TCc(V3(10.5, 130.0, -4.25), R3(0.0, 1.5, 0.0)))
    WRL = JClass("com.hypixel.hytale.server.core.universe.world.World")
    wi = E.U.allocateInstance(E.HW.class_)
    HT.jf(WRL.class_, "name").set(wi, W)
    MSCc, MST = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent"), JClass("com.hypixel.hytale.protocol.MovementStates")
    msc = MSCc()
    ms = MST()
    msc.setMovementStates(ms)
    P.st.row(P.ref).put(MSCc.getComponentType(), msc)
    for fl in ("air", "flying", "swimming", "gliding", "falling"):
        ms.onGround = fl != "air"
        ms.flying, ms.swimming, ms.gliding, ms.falling = fl == "flying", fl == "swimming", fl == "gliding", fl == "falling"
        r = st(IH.setHere(P.st, P.ref, P.pr, wi, "x"))
        K.eq(r, "-Stand on solid ground to set a home.", "HOMES 0: sethome while %s = refused" % ("in mid-air (not on ground)" if fl == "air" else fl))
    K.check(not os.path.exists(hf(OWN)), "HOMES 0: nothing saved while off the ground")
    ms.onGround, ms.flying, ms.swimming, ms.gliding, ms.falling = True, False, False, False, False
    ms.inFluid = True
    r = st(IH.setHere(P.st, P.ref, P.pr, wi, None))
    K.check(r.startswith("+Main home set here"), "HOMES 1: /island sethome on the own island, on the ground (shallow water ok): %s" % r)
    ms.inFluid = False
    K.eq(tgt(O, None), (OWN, [10.5, 130.0, -4.25], [0.0, 1.5, 0.0], None), "HOMES 1: /island lands on the main home (position + rotation)")
    K.eq(tgt(O, ""), tgt(O, "main"), "HOMES 1: /island main = the main home")
    r = st(IH.setHere(P.st, P.ref, P.pr, wi, "Farm"))
    K.check(r.startswith("+Home 'Farm' set here (1 / 6)"), "HOMES 2: /island sethome Farm: %s" % r)
    K.eq(tgt(O, "farm")[1], [10.5, 130.0, -4.25], "HOMES 2: /island farm (any case) finds Farm")
    r = st(IH.setAt(O, "FARM", W, 1.0, 100.0, 2.0, 0.0, 0.0, 0.0))
    K.check(r.startswith("+Home 'FARM' moved here (1 / 6)"), "HOMES 2: setting the same name again moves it (count stays): %s" % r)
    K.eq(tgt(O, "Farm")[1], [1.0, 100.0, 2.0], "HOMES 2: the moved spot")
    K.eq([str(x) for x in IH.names(O)], ["FARM"], "HOMES 2: the last spelling is shown")
    r = st(IH.setAt(O, None, W, 3.0, 101.0, 4.0, 0.0, 0.0, 0.0))
    K.check(r.startswith("+Main home moved here"), "HOMES 2: /island sethome again moves the main home: %s" % r)
    txt = open(hf(OWN), encoding="latin-1").read()
    K.check(("main=%s|%s|3.0|101.0|4.0|0.0|0.0|0.0|main" % (OWN, W)) in txt and ("home.farm=%s|%s|1.0|100.0|2.0|0.0|0.0|0.0|FARM" % (OWN, W)) in txt
            and txt.startswith("# SkyyIslands island homes of ONE profile"), "HOMES 2: the file format: %s" % txt.splitlines()[2:])
    K.check(not [f for f in os.listdir(hdir) if f.endswith(".tmp")], "HOMES 2: atomic writes leave no .tmp")

    # ---- the limit
    for i in range(5):
        K.check(st(IH.setAt(O, "spot%d" % i, W, i, 100.0, i, 0.0, 0.0, 0.0)).startswith("+Home"), "HOMES 3: home %d of 6" % (i + 2))
    r = st(IH.setAt(O, "seventh", W, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0))
    K.check(r.startswith("-You already have 6 / 6 named homes"), "HOMES 3: the 7th is refused: %s" % r)
    K.check(st(IH.setAt(O, "spot0", W, 9.0, 100.0, 9.0, 0.0, 0.0, 0.0)).startswith("+Home 'spot0' moved"), "HOMES 3: a full list still moves an old name")
    K.check(st(IH.setAt(O, None, W, 3.0, 101.0, 4.0, 0.0, 0.0, 0.0)).startswith("+Main home"), "HOMES 3: the main home does not count")
    CFG.HOMES_MAX = 2
    K.eq(len(IH.names(O)), 6, "HOMES 3: homes.max lowered to 2 deletes nothing")
    lt = st(IH.listText(O))
    K.check(lt.startswith("=Your island homes (6 / 2): FARM, spot0, spot1, spot2, spot3, spot4 - /island <name> goes there. Main home: set"),
            "HOMES 3: /island homes: %s" % lt)
    K.check(st(IH.setAt(O, "new", W, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0)).startswith("-You already have 6 / 2"), "HOMES 3: over the lowered limit - no new one")
    CFG.HOMES_MAX = 0
    K.check("switched off" in st(IH.setAt(O, "new", W, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0)), "HOMES 3: homes.max 0 = named homes off")
    K.check(st(IH.setAt(O, None, W, 3.0, 101.0, 4.0, 0.0, 0.0, 0.0)).startswith("+Main home"), "HOMES 3: homes.max 0 keeps the main home")
    CFG.HOMES_MAX = 6

    # ---- delete
    DEL = getattr(IH, "del_", None) or getattr(IH, "del")
    r = st(DEL(O, "SPOT4"))
    K.check(r.startswith("+Home 'spot4' deleted (5 / 6)"), "HOMES 4: /island delhome SPOT4: %s" % r)
    K.check(st(DEL(O, "spot4")).startswith("-No home named 'spot4'"), "HOMES 4: again = no such home")
    K.check(st(IH.target(O, "spot4")).startswith("-No home named 'spot4'"), "HOMES 4: /island spot4 after delete = refused")
    K.check(st(DEL(O, "")).startswith("-Usage"), "HOMES 4: /island delhome without a name = usage")

    # ---- bad names
    for nm in ("", "  ", "a b", "x" * 17, "héllo", "farm!", "a.b", "a|b"):
        r = IH.bad(nm)
        K.check(r is not None and str(r).startswith("-"), "HOMES 5: bad name %r refused: %s" % (nm, r))
    K.check(IH.bad("x" * 16) is None and IH.bad("Big_Farm-2") is None, "HOMES 5: 16 chars / letters digits - _ are fine")
    K.check(st(IH.setAt(O, "visit", W, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0)).startswith("-'visit' is an /island command word"), "HOMES 5: a sub-command word is refused")
    K.check(st(IH.setAt(O, "BanList", W, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0)).startswith("-'BanList' is an /island command word"), "HOMES 5: an alias (any case) is refused")

    # ---- whose island
    r = st(IH.setAt(O, "x", "skyy-island-vee", 0.0, 100.0, 0.0, 0.0, 0.0, 0.0))
    K.check(r.startswith("-Homes can only be set on your own island"), "HOMES 6: on another player's island = refused: %s" % r)
    r = st(IH.setAt(V, "x", W, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0))
    K.check(r.startswith("-Homes can only be set on your own island"), "HOMES 6: V standing on O's island = refused: %s" % r)
    r = st(IH.setAt(O, "x", "default", 0.0, 100.0, 0.0, 0.0, 0.0, 0.0))
    K.check(r.startswith("-Stand on your island"), "HOMES 6: in the hub world = refused: %s" % r)
    r = st(IH.setAt(N, "x", "default", 0.0, 100.0, 0.0, 0.0, 0.0, 0.0))
    K.check(r.startswith("-You have no island yet"), "HOMES 6: no island = refused: %s" % r)
    K.check(not os.path.exists(hf(VIS)) and not os.path.exists(hf(NOI)), "HOMES 6: refused players got no homes file")
    r = st(IH.setAt(M, "base", W, 5.0, 120.0, 5.0, 0.0, 0.0, 0.0))
    K.check(r.startswith("+Home 'base' set here (1 / 6)"), "HOMES 6: the co-op member sets a home on the co-op island: %s" % r)
    K.eq(tgt(M, "base")[:2], (OWN, [5.0, 120.0, 5.0]), "HOMES 6: the member's home goes to the co-op island (owner key)")
    K.eq(tgt(M, "farm"), "-No home named 'farm'. /island homes lists yours (/island visit <player> visits a player).",
         "HOMES 6: homes are per player profile (the owner's are not the member's)")
    K.eq(tgt(V, "base"), "-No home named 'base'. /island homes lists yours (/island visit <player> visits a player).", "HOMES 6: V has none")
    K.eq(tgt(V, None), (VIS, None, None, None), "HOMES 6: no main home = the island spawn (null spot)")

    # ---- profile switch
    keys = {OWN: OWN}

    @JImplements("java.util.function.Function")
    class KeyFn:
        @JOverride
        def apply(self, u):
            return keys.get(str(u), str(u))
    E.bridge.put("profile:fn:key", KeyFn())
    keys[OWN] = OWN + "-p2"
    K.eq(len(IH.names(O)), 0, "HOMES 7: on profile 2 the owner has no homes (another file)")
    K.check(st(IH.setAt(O, "farm", W, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0)).startswith("-You have no island yet"),
            "HOMES 7: profile 2 has no island yet - no home on profile 1's island")
    K.eq(tgt(O, None), (OWN + "-p2", None, None, None), "HOMES 7: /island on profile 2 = its own island's spawn")
    keys[OWN] = OWN
    K.eq(len(IH.names(O)), 5, "HOMES 7: back on profile 1 the 5 homes are there")
    E.bridge.remove("profile:fn:key")

    # ---- reset = a new world: every home of that island goes void
    K.check(int(IS.setWorldName(OWN, W + "-r1")) >= 0 and str(IS.settings(OWN).world) == W + "-r1", "HOMES 8: the island got a new world (reset)")
    lt = st(IH.listText(O))
    K.check("FARM (void: your island was reset since)" in lt and "Main home: void (your island was reset since)" in lt, "HOMES 8: /island homes marks them void: %s" % lt)
    K.eq(len(IH.names(O)), 0, "HOMES 8: the bridge lists no void home")
    r = tgt(O, "farm")
    K.eq(r, "-Home 'FARM' is gone: your island was reset since. Set it again with /island sethome FARM.", "HOMES 8: /island farm after a reset")
    K.check("home.farm=" not in open(hf(OWN), encoding="latin-1").read(), "HOMES 8: the void home was removed from the file")
    r = tgt(O, None)
    K.check(r[0] == OWN and r[1] is None and r[3] is not None and r[3].startswith("=Your main home was cleared (your island was reset since)"),
            "HOMES 8: /island after a reset = a note, then the spawn: %s" % (r,))
    K.check("main=" not in open(hf(OWN), encoding="latin-1").read(), "HOMES 8: the void main home was removed")
    K.check(st(IH.setAt(O, "farm", W + "-r1", 7.0, 100.0, 7.0, 0.0, 0.0, 0.0)).startswith("+Home 'farm' set here"), "HOMES 8: a new home on the new world works")
    # the member's home on the reset island is void too (the co-op island changed world)
    K.check(st(IH.target(M, "base")).startswith("-Home 'base' is gone: your island was reset since"), "HOMES 8: the member's home is void after the reset")

    # ---- leaving the co-op: the member's home island is their own now - spots on the co-op island are void
    K.check(st(IH.setAt(M, "base2", W + "-r1", 1.0, 100.0, 1.0, 0.0, 0.0, 0.0)).startswith("+Home 'base2'"), "HOMES 9: the member saves another")
    K.check(bool(IS.setProps(OWN, JArray(JClass("java.lang.String"))(["members"]), JArray(JClass("java.lang.String"))([""]))), "HOMES 9: the member leaves (members cleared)")
    IS.MEMBER_OF.remove(MEM)
    K.eq(str(IS.homeKey(M)), MEM, "HOMES 9: the member's home island is their own now")
    r = st(IH.target(M, "base2"))
    K.check(r.startswith("-Home 'base2' is gone: you no longer live on that island"), "HOMES 9: the co-op spot is void: %s" % r)

    # ---- an unreadable homes file
    os.makedirs(hf(VIS))
    r = st(IH.setAt(V, "x", "skyy-island-vee", 0.0, 100.0, 0.0, 0.0, 0.0, 0.0))
    K.check(r.startswith("-Your homes file can't be read"), "HOMES 10: unreadable file - set refused: %s" % r)
    K.eq(tgt(V, None), (VIS, None, None, None), "HOMES 10: unreadable file - /island still goes (the spawn)")
    K.check(st(IH.target(V, "x")).startswith("-Your homes file can't be read"), "HOMES 10: unreadable file - /island <name> refused")
    K.eq(len(IH.names(V)), 0, "HOMES 10: unreadable file - the bridge answers an empty list")
    os.rmdir(hf(VIS))

    # ---- the bridge Functions
    hm = J("HomesFn")()
    K.eq([str(x) for x in hm.apply(O)], ["farm"], "HOMES 11: island:fn:homes(UUID) = the usable named homes")
    K.eq(len(hm.apply("nope")), 0, "HOMES 11: island:fn:homes(not a UUID) = empty, no throw")
    gh = J("GoHomeFn")()
    K.check(str(gh.apply(JArray(JObject)([N, "farm"]))).startswith("-That player is not online"), "HOMES 11: island:fn:gohome offline = refused")
    K.check(str(gh.apply("x")).startswith("-island:fn:gohome takes"), "HOMES 11: island:fn:gohome bad input = refused")
    K.check(not [f for f in os.listdir(hdir) if f.endswith(".tmp")], "HOMES 11: no .tmp file left")
    K.notes.append("files: %s" % sorted(os.listdir(hdir)))
    K.save()


def run_live(out, jar, scratch, home):
    K = HK.Child(out)
    h0 = HK.tree_hash(home)
    E, J = setup(os.path.join(scratch, "livehomes"), jar, home)
    J("IslandCmd")()
    d = os.path.join(home, "islands")
    owners = [f[:-11] for f in sorted(os.listdir(d)) if f.endswith(".properties") and len(f) >= 36 + 11] if os.path.isdir(d) else []
    K.check(bool(owners), "D: the live copy has island owners (%d)" % len(owners))
    hm = J("HomesFn")()
    for k in owners:
        u = E.UUID.fromString(k[:36])
        n = len(hm.apply(u))
        lt = str(J("IslandHomes").listText(u))
        K.check(n == 0 and lt.startswith("=Your island homes (0 / 6): none yet"), "D: %s: no homes yet, /island homes: %s" % (k[:8], lt[:60]))
        t = J("IslandHomes").target(u, None)
        K.check(t is not None and len(t) == 4 and t[1] is None, "D: %s: /island = the island spawn as 0.5.18" % k[:8])
    K.check(HK.tree_hash(home) == h0, "D: no file of the copy changed (reads write nothing)")
    K.save()


if __name__ == "__main__":
    HK.run(name="SkyyIslands", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=[("tree", run_tree), ("homes", run_homes), ("live", run_live)],
           script=__file__, live=(LIVE_DIR, "Skyy_SkyyIslands"))
