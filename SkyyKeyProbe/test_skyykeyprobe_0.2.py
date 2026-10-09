"""Harness for SkyyKeyProbe 0.2 (copied from the 0.1 harness; every 0.1 check kept). Build first:
    python SkyyKeyProbe/build_skyykeyprobe_0.2.py

    python SkyyKeyProbe/test_skyykeyprobe_0.2.py [--keep]

NEW 0.2 (the /keyprobe sprint probe) - executed, not just loaded:
  S  (child, in X) the reflection field list against the REAL protocol MovementStates / MovementSettings classes; dir / relDeg / r1 /
     velText / wishText / skipComp / cut / dump (real MouseInteraction packet, arrays, enums) / pktLine (MouseInteraction,
     SyncInteractionChains); the diff printer on synthetic MovementStates; KpSprint: the chat cap (10 / s chat, 40 / s log, rest
     dropped, '+N in the log only'), movement (baseline, sprinting / wish / velocity changes, empty packets), packet (Pong counted
     only), sample (baseline line, server + sent states, velocity, settings, stamina DRAINS / steady, component changed / added /
     removed / muted after 40), summary; THROUGH THE REAL PacketAdapters filter: /keyprobe sprint on (KpCmds.run + the
     KProbeSprintCmd execute()), ClientMovement + MouseInteraction + Pong packets -> world-thread chat lines; the server sampler
     (KpCore.tickAll -> KpSample on a stand-in World with real MovementStatesComponent / Velocity / HeadRotation / MovementManager /
     EntityStatMap components and a real Archetype): baseline, changes, busy skip + 2 s stale reset, player left = stopped, no world,
     no entity, error path; the daemon Timer (KpTick) start / stop; off = summary; plugin shutdown clears the sprint state + timer
  F  FIX ROUND (critic findings), each executed: the component VALUE summary (KpLogic.allFields / vtext / compSum / fname / fval) on
     REAL engine components - Velocity / PlayerInput keep the same identity hashCode after an in-place change while compSum sees it
     (the 0.2 blind spot); the per-FIELD mute; every line past the chat cap is logged (100 / s); the 20 ms sampler is faster than
     the engine's TickingThread.TPS tick; at most 3 probes at once; a probe stops itself after 5 min (summary delivered) and the Timer
     stops when the last probe ends inside tickAll; the TAP + HOLD steps text
  P  KProbeSprintCmd: permission group hytale:Adventurer, NOT the admin node, a sub-command of /keyprobe (getSubCommands)
  B  engine facts: AbstractCommand.acceptCall0 dispatches sub-commands BEFORE its own hasPermission; hasPermission stops at a command
     that sets its own groups
  D  the sprint paths run for every copied live player too (still writes nothing)

  J  the jar: manifest (Main, IncludesAssetPack true, version), exactly the 15 classes, exactly 2 items + 30 roots + 1 lang file, no .ui
  N  NO OVERRIDE: every asset path / id is new - not in Assets.zip, not in any installed mod (read-only scan of UserData/Mods); the
     Key Tester carries ONLY the vanilla stick's look (no recipe, no resource types, no fuel), the helmet no stats / recipe / durability
  R  the roots as built: the 8 key types = RequireNewClick + HudInputBindingEntry + ONE Charging (AllowIndefiniteHold false, keys 0 /
     0.3 / 2) with three SendMessage (Target Owner) branches; SwapTo / SwapFrom / GameModeSwap / Death = one SendMessage; Held /
     HeldOffhand / Wielding / Equipped = one Simple; NO Parallel anywhere; every mapped type a real InteractionType; lang lines; binds
  A  (child) every class loads + verifies (game JRE, -Xverify:all, -XX:-UsePerfData)
  V  (child) THE ENGINE ASSET VALIDATORS on all 32 assets and every inline step in them: the store's decode (no unknown key), the codec's
     FULL validate pass, AssetValidationResults.logOrThrowValidatorExceptions, the contained assets - NEGATIVE CONTROL: a one-entry
     Parallel fails the same function with the engine's own message; then every asset into the real stores from our pack and
     RootInteraction.build() of all 30 roots: 0 "Missing interaction", each graph = Charging + 3 SendMessage | SendMessage | Simple
  X  (child) EVERY code path executed on real engine objects: real SyncInteractionChains / SyncInteractionChain / InteractionSyncData /
     ClientMovement / MovementStates packets through the REAL PacketAdapters filter (the engine's PlayerPacketWatcher lambda, a
     GamePacketHandler carrying the PlayerRef) -> KpWatch -> KpCore -> KpState -> KpSay on a stand-in World's execute; tap / hold /
     no-end / failed / charge / Helmet / worn armor / other item / all on; the 0.3 s cap + hidden count + the 20-in-10-s mute; stale
     chains; the 32-chain cap; movement edges + double-tap crouch + moves off; hand check (tester / helmet / other / no ref); every
     subcommand through KpCmds.run and the three commands' execute(); give storage-first + no room + no inventory; report / binds /
     reset / off; packet errors logged 3 times at most; start() twice = one filter; plugin shutdown deregisters + clears
  P  (child) permissions: node skyykeyprobe.admin, empty permission groups on the root + both variants, getPermissionGroupsRecursive gives
     the node to no group; alias /kprobe
  B  (child) setup()'s calls in order (LOG, registerCommand(KProbeCmd), KpCore.start) + the engine facts the probe stands on, read from
     HytaleServer.jar bytecode (watcher lambda returns false; inbound filters run before the handler; root resolution by item map)
  D  START TWICE ON A SCRATCH COPY OF LIVE DATA: the live player files (read-only) copied to scratch; two fresh child JVMs each start the
     probe, run every watched-player path for each copied player's real uuid / name, and the probe writes NOTHING: every scratch file
     byte-identical, no new file, no state carried into the second start
  AA (child) the ENGINE-ACCESS AUDIT: every class / field / method reference of the jar looked up with MethodHandles.privateLookupIn the
     referencing class - 0 refused; the control (a protected call) refused
Not testable without the game: which inputs the CLIENT really sends (the whole point of the probe), whether HudInputBindingEntry shows
on an item, the real default keys. Scratch: tools/dev/scratch/keyprobe01/test (deleted at the end unless --keep). Exit 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.2"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyKeyProbe-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "kprobe02", "test")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyykeytest"
PKG = "com.skyy.keyprobe."
CLASSES = sorted(PKG + c for c in ["KpLog", "KpLogic", "KpState", "KpSay", "KpCore", "KpWatch", "KpCmds", "KProbeArg2Cmd", "KProbeArgCmd",
                                   "KProbeCmd", "SkyyKeyProbePlugin", "KpSprint", "KpSample", "KpTick", "KProbeSprintCmd"])
NODE = "skyykeyprobe.admin"
TESTER, HELMET = "SkyyKeyProbe_Tester", "SkyyKeyProbe_Helmet"
KEYS = ["Primary", "Secondary", "Ability1", "Ability2", "Ability3", "Use", "Pick", "Dodge"]
LOUD = ["SwapTo", "SwapFrom", "GameModeSwap", "Death"]
QUIET = ["Held", "HeldOffhand", "Wielding", "Equipped"]
TYPES = KEYS + LOUD + QUIET
PACK = "Skyy:0.2 SkyyKeyProbe"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


def deploy_world():
    try:
        for l in open(os.path.join(TOOLS, "deploy_set.py"), encoding="utf-8"):
            if l.startswith("WORLD = "):
                return l.split("=", 1)[1].strip().strip('"')
    except Exception:
        pass
    return "HUD mod"


LIVE = os.path.abspath(arg("--live", os.path.join(B.USERDATA, "Saves", deploy_world(), "universe", "players")))


def walk(o, fn):
    fn(o)
    if isinstance(o, dict):
        for v in o.values():
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


# ====================================================================================================== parent: J N R
def part_static():
    jz, az = zipfile.ZipFile(JAR), zipfile.ZipFile(ASSETS)
    man = json.loads(jz.read("manifest.json"))
    check(man["Main"] == PKG + "SkyyKeyProbePlugin" and man.get("IncludesAssetPack") is True and man["Version"] == VERSION
          and man["Name"] == "%s SkyyKeyProbe" % VERSION and man["Group"] == "Skyy", "J. manifest %s" % man)
    cls = sorted(n[:-6].replace("/", ".") for n in jz.namelist() if n.endswith(".class"))
    check(cls == CLASSES, "J. classes %s" % cls)
    other = sorted(n for n in jz.namelist() if not n.endswith(".class") and n != "manifest.json")
    items = sorted(n for n in other if n.startswith("Server/Item/Items/"))
    roots = sorted(n for n in other if n.startswith("Server/Item/RootInteractions/"))
    check(items == ["Server/Item/Items/SkyyKeyProbe/%s.json" % HELMET, "Server/Item/Items/SkyyKeyProbe/%s.json" % TESTER], "J. items %s" % items)
    want_roots = sorted(["Server/Item/RootInteractions/SkyyKeyProbe/SkyyKeyProbe_Tester_%s.json" % t for t in TYPES] +
                        ["Server/Item/RootInteractions/SkyyKeyProbe/SkyyKeyProbe_Helmet_%s.json" % t for t in TYPES if t not in ("Primary", "Secondary")])
    check(roots == want_roots, "J. the 30 roots: %s" % sorted(set(roots) ^ set(want_roots)))
    check(sorted(set(other) - set(items) - set(roots)) == ["Server/Languages/en-US/server.lang"], "J. nothing else in the jar: %s" % other)
    check(not any(n.lower().endswith(".ui") for n in jz.namelist()), "J. no .ui file")
    _bs = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_skyykeyprobe_%s.py" % VERSION), encoding="utf-8").read()
    check("'server ran ...' lines (SendMessage steps) are NOT capped by us" in _bs and "trash both probe items" in _bs,
          "J. (fix keyprobe01fix C2-1 / C1-1) the build doc states the uncapped engine lines + the trash reminder")
    # ---------------- N
    azn = set(az.namelist())
    az_ids = set(n.rsplit("/", 1)[1][:-5] for n in azn if n.startswith("Server/") and n.endswith(".json"))
    for n in items + roots:
        check(n not in azn, "N. %s is a new path" % n)
        i = n.rsplit("/", 1)[1][:-5]
        check(i not in az_ids and i.startswith("SkyyKeyProbe_"), "N. id %s is new (no vanilla asset of that name)" % i)
    ids = [n.rsplit("/", 1)[1][:-5] for n in items + roots]
    mods = os.path.join(B.USERDATA, "Mods")
    seen, scanned = {}, 0
    for f in sorted(os.listdir(mods)) if os.path.isdir(mods) else []:
        p = os.path.join(mods, f)
        if not (f.endswith(".jar") or f.endswith(".zip")) or f.startswith("SkyyKeyProbe") or not os.path.isfile(p):
            continue
        try:
            with zipfile.ZipFile(p) as mz:
                names = mz.namelist()
        except Exception:
            continue
        scanned += 1
        for n in names:
            if n.endswith(".json") and n.rsplit("/", 1)[-1][:-5] in ids:
                seen.setdefault(n.rsplit("/", 1)[-1][:-5], []).append(f)
            if "/SkyyKeyProbe/" in n or n.startswith("com/skyy/keyprobe/"):
                seen.setdefault(n, []).append(f)
    check(not seen and scanned > 0, "N. no installed mod (%d scanned) defines a probe id / path: %s" % (scanned, seen))
    van = dict((n.rsplit("/", 1)[1][:-5], n) for n in azn if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    t = json.loads(jz.read(items[1]))
    h = json.loads(jz.read(items[0]))
    stick = json.loads(az.read(van["Ingredient_Stick"]).decode("utf-8-sig"))
    check(sorted(t) == sorted(["TranslationProperties", "MaxStack", "Icon", "IconProperties", "Model", "Texture", "PlayerAnimationsId",
                                "ItemSoundSetId", "Interactions"]) and t["MaxStack"] == 1,
          "N. the Key Tester has only look + name + MaxStack 1 + Interactions (no recipe / resource types / fuel / parent): %s" % sorted(t))
    for k in ("Icon", "IconProperties", "Model", "Texture", "PlayerAnimationsId", "ItemSoundSetId"):
        check(t[k] == stick[k], "N. Key Tester %s = the vanilla stick's" % k)
    check("Recipe" not in h and "Parent" not in h and "MaxDurability" not in h and h["Armor"] == {"ArmorSlot": "Head", "BaseDamageResistance": 0},
          "N. the helmet: ArmorSlot Head, no stats, no recipe / parent / durability: %s" % h.get("Armor"))
    # ---------------- R
    lang = {}
    for l in jz.read("Server/Languages/en-US/server.lang").decode("utf-8").splitlines():
        if "=" in l:
            k, v = l.split("=", 1)
            lang[k] = v
    for i in (TESTER, HELMET):
        for pre in ("", "server."):
            check(("%sitems.%s.name" % (pre, i)) in lang and ("%sitems.%s.description" % (pre, i)) in lang, "R. lang name + description of %s" % i)
    check(lang.get("items.%s.name" % TESTER) == "Key Tester" and lang.get("items.%s.name" % HELMET) == "Key Tester Helmet", "R. item names")
    for k in KEYS:
        check(lang.get("hud.inputBinding.SkyyKeyProbe_%s" % k) == "Key probe: %s" % k, "R. HUD binding line for %s" % k)
    check(sorted(t["Interactions"]) == sorted(TYPES) and all(t["Interactions"][x] == "SkyyKeyProbe_Tester_%s" % x for x in TYPES),
          "R. the Key Tester maps all 16 types to its own roots")
    check(sorted(h["Interactions"]) == sorted(TYPES) and h["Interactions"]["Primary"] == {"Interactions": [{"Type": "EquipItem"}]}
          and h["Interactions"]["Secondary"] == {"Interactions": [{"Type": "EquipItem"}]}
          and all(h["Interactions"][x] == "SkyyKeyProbe_Helmet_%s" % x for x in TYPES if x not in ("Primary", "Secondary")),
          "R. the helmet: click-to-wear (vanilla EquipItem) + 14 roots")
    par = []
    for n in items + roots:
        walk(json.loads(jz.read(n)), lambda o: par.append(n) if isinstance(o, dict) and o.get("Type") == "Parallel" else None)
    check(not par, "R. no Parallel step anywhere (the 2026-10-08 one-entry Parallel lesson): %s" % par)
    for n in roots:
        d = json.loads(jz.read(n))
        rid = n.rsplit("/", 1)[1][:-5]
        src, typ = rid.split("_")[1], rid.split("_")[2]
        label = "Key Tester" if src == "Tester" else "Key Tester Helmet (in hand or worn)"
        if typ in KEYS:
            st = d["Interactions"]
            ok = (d.get("RequireNewClick") is True and d.get("HudInputBindingEntry") == "server.hud.inputBinding.SkyyKeyProbe_%s" % typ
                  and len(st) == 1 and st[0]["Type"] == "Charging" and st[0]["AllowIndefiniteHold"] is False and st[0]["DisplayProgress"] is False
                  and sorted(st[0]["Next"]) == ["0", "0.3", "2"]
                  and all(v["Type"] == "SendMessage" and v["Target"] == "Owner" and v["Message"].startswith("[KeyProbe] server ran %s on the %s: " % (typ, label))
                          for v in st[0]["Next"].values()))
        elif typ in LOUD:
            ok = d == {"Interactions": [{"Type": "SendMessage", "Target": "Owner", "Message": "[KeyProbe] server ran %s on the %s" % (typ, label)}]}
        else:
            ok = d == {"Interactions": [{"Type": "Simple"}]}
        check(ok, "R. root %s has the specced shape: %s" % (rid, json.dumps(d)[:300]))
    print("J/N/R. jar: %d classes, 2 items, %d roots; %d installed mods scanned, no clash; no Parallel" % (len(cls), len(roots), scanned))


# ====================================================================================================== children
def _jvm(cp, verify=True):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED", "-Djava.io.tmpdir=" + tmp]
    jpype.startJVM(jvm, *opts, classpath=list(cp), convertStrings=True)


class Child(object):
    def __init__(self, out):
        self.out, self.ok, self.fails, self.notes = out, 0, [], []

    def check(self, cond, what):
        if cond:
            self.ok += 1
        else:
            self.fails.append(what)
            print("FAIL", what)

    def save(self, **extra):
        d = {"ok": self.ok, "fails": self.fails, "notes": self.notes}
        d.update(extra)
        json.dump(d, open(self.out, "w"), indent=1)


def run_mkfake(out_dir):
    """child F: stand-ins (subclasses of engine classes, always created with Unsafe.allocateInstance - no constructor runs)"""
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG
    ms = cp.makeClass(P + ".MapStore")
    ms.setSuperclass(cp.get("com.hypixel.hytale.component.Store"))
    for decl in ("java.util.Map comps", "com.hypixel.hytale.component.Archetype arch"):
        ms.addField(CtField.make("public %s;" % decl, ms))
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))
    ms.addMethod(CtNewMethod.make("""public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (this.comps == null || r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""", ms))
    ms.addMethod(CtNewMethod.make("public com.hypixel.hytale.component.Archetype getArchetype(com.hypixel.hytale.component.Ref r) { return this.arch; }", ms))
    ms.addMethod(CtNewMethod.make("public boolean isProcessing() { return false; }", ms))
    ms.addMethod(CtNewMethod.make("""public void putComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) {
  java.util.Map m = (java.util.Map) this.comps.get(r);
  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }
  m.put(t, c);
}""", ms))
    ms.writeFile(out_dir)
    fh = cp.makeClass(P + ".FakeHotbar")
    fh.setSuperclass(cp.get("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar"))
    fh.addField(CtField.make("public com.hypixel.hytale.server.core.inventory.ItemStack item;", fh))
    fh.addConstructor(CtNewConstructor.make("public FakeHotbar() { super(); }", fh))
    fh.addMethod(CtNewMethod.make("public com.hypixel.hytale.server.core.inventory.ItemStack getActiveItem() { return this.item; }", fh))
    fh.writeFile(out_dir)
    fw = cp.makeClass(P + ".FakeWorld")
    fw.setSuperclass(cp.get("com.hypixel.hytale.server.core.universe.world.World"))
    fw.addField(CtField.make("public java.util.List tasks;", fw))
    fw.addConstructor(CtNewConstructor.make("public FakeWorld() { super(null, null, null); }", fw))
    fw.addMethod(CtNewMethod.make("public void execute(java.lang.Runnable r) { if (this.tasks == null) this.tasks = new java.util.ArrayList(); this.tasks.add(r); }", fw))
    fw.writeFile(out_dir)
    lk = cp.makeClass(P + ".LookupIn")
    lk.addMethod(CtNewMethod.make(
        "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
        "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}", lk))
    lk.writeFile(out_dir)
    ba = cp.makeClass(P + ".BadAccess")
    ba.addMethod(CtNewMethod.make(
        "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
        "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}", ba))
    ba.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


def base_engine(K):
    """Options + allocated HytaleServer / Universe (worldsByUuid), the logger capture, AssetRegistryLoader.init, the interaction stores and
    every interaction Type codec exactly as InteractionModule.setup registers them (read from its bytecode) - the SkyyArmory 0.1.11 harness"""
    from jpype import JClass, JArray, JString, JImplements, JOverride
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jfield(c, n):
        f = c.class_.getDeclaredField(n)
        f.setAccessible(True)
        return f
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jfield(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jfield(HS, "instance").set(None, hs)
    CHM, COLL = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Collections")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap, wbu = CHM(), CHM(), CHM()
    for n, v in (("playersByUuid", pbu), ("players", COLL.unmodifiableCollection(pbu.values())), ("worlds", wmap), ("worldsByUuid", wbu),
                 ("unmodifiableWorlds", COLL.unmodifiableMap(wmap))):
        jfield(UNI, n).set(uni, v)
    jfield(UNI, "instance").set(None, uni)
    HLB = JClass("com.hypixel.hytale.logger.backend.HytaleLoggerBackend")
    CAPLOG = JClass("java.util.concurrent.CopyOnWriteArrayList")()
    HLB.subscribe(CAPLOG)

    def records():
        out = []
        for r in list(CAPLOG):
            try:
                msg = str(r.getMessage())
                ps = r.getParameters()
                if ps is not None and len(ps) > 0:
                    try:
                        msg = str(JClass("java.lang.String").format(msg, ps))
                    except Exception:
                        msg = msg + " " + " ".join(str(p) for p in ps)
                out.append((str(r.getLevel()), msg))
            except Exception:
                pass
        return out
    JClass("com.hypixel.hytale.server.core.asset.AssetRegistryLoader").init()
    AR = JClass("com.hypixel.hytale.assetstore.AssetRegistry")
    HAS = JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore")
    ILT = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    DAMc = JClass("com.hypixel.hytale.assetstore.map.DefaultAssetMap")
    ARR = JClass("java.lang.reflect.Array")

    @JImplements("java.util.function.Function")
    class GetId:
        @JOverride
        def apply(self, o): return o.getId()

    @JImplements("java.util.function.IntFunction")
    class ArrOf:
        def __init__(self, c): self.c = c

        @JOverride
        def apply(self, n): return ARR.newInstance(self.c.class_, n)

    @JImplements("java.util.function.Function")
    class NoRep:
        @JOverride
        def apply(self, k): return None

    @JImplements("java.util.function.Predicate")
    class IsUnknown:
        @JOverride
        def test(self, o): return bool(o.isUnknown())
    PI = "com.hypixel.hytale.server.core.modules.interaction.interaction.config."
    INTc, ROOTc = JClass(PI + "Interaction"), JClass(PI + "RootInteraction")
    UIc = JClass("com.hypixel.hytale.server.core.modules.interaction.interaction.UnarmedInteractions")

    def reg_ilt(c, path, codec, unknown=False):
        if AR.getAssetStore(c.class_) is not None:
            return
        b_ = HAS.builder(c.class_, ILT(ArrOf(c))).setPath(path).setCodec(codec).setKeyFunction(GetId()).setReplaceOnRemove(NoRep())
        if unknown:
            b_ = b_.setIsUnknown(IsUnknown())
        AR.register(b_.build())
    reg_ilt(INTc, "Item/Interactions", INTc.CODEC, True)
    reg_ilt(ROOTc, "Item/RootInteractions", ROOTc.CODEC)
    if AR.getAssetStore(UIc.class_) is None:
        AR.register(HAS.builder(UIc.class_, DAMc()).setPath("Item/Unarmed/Interactions").setCodec(UIc.CODEC).setKeyFunction(GetId()).build())
    CPj = JClass("javassist.ClassPool")(True)
    CPj.appendClassPath(B.SERVER_JAR)
    CPool = JClass("javassist.bytecode.ConstPool")
    imc = CPj.get("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    ms_ = [x for x in imc.getDeclaredMethods() if str(x.getName()) == "setup"][0]
    cp_, it_ = ms_.getMethodInfo().getConstPool(), ms_.getMethodInfo().getCodeAttribute().iterator()
    last_s, last_c, regs = None, None, []
    while it_.hasNext():
        p_ = it_.next()
        op_ = it_.byteAt(p_)
        if op_ in (0x12, 0x13):
            idx = it_.byteAt(p_ + 1) if op_ == 0x12 else it_.u16bitAt(p_ + 1)
            if cp_.getTag(idx) == CPool.CONST_String:
                last_s = str(cp_.getStringInfo(idx))
            elif cp_.getTag(idx) == CPool.CONST_Class:
                last_c = str(cp_.getClassInfo(idx))
        elif op_ == 0xb6:
            idx = it_.u16bitAt(p_ + 1)
            if str(cp_.getMethodrefClassName(idx)).endswith("AssetCodecMapCodec") and str(cp_.getMethodrefName(idx)) == "register":
                regs.append((last_s, last_c))
    for nm_, cl_ in regs:
        C_ = JClass(cl_)
        try:
            INTc.CODEC.register(nm_, C_.class_, jfield(C_, "CODEC").get(None))
        except Exception as e:
            K.notes.append("codec %s: %s" % (nm_, str(e)[:80]))
    K.check(("Charging", PI + "client.ChargingInteraction") in regs and ("SendMessage", PI + "none.simple.SendMessageInteraction") in regs
            and len(regs) > 60, "E: the interaction Type codecs registered from InteractionModule.setup's bytecode (%d)" % len(regs))
    names = dict(regs)
    K.check(all(k in names for k in ("Charging", "SendMessage", "Simple", "EquipItem")), "E: Charging / SendMessage / Simple / EquipItem are engine types: %s"
            % [k for k in ("Charging", "SendMessage", "Simple", "EquipItem") if k not in names])
    return {"U": U, "jfield": jfield, "AR": AR, "uni": uni, "wbu": wbu, "records": records, "INTc": INTc, "ROOTc": ROOTc, "PI": PI}


def sprint_part(K, E, L):
    """S: the 0.2 sprint probe on real engine objects (called from run_engine with its locals)"""
    import math
    from jpype import JClass, JArray, JObject, JInt, JFloat, JLong, JString, JBoolean, JDouble
    U, jfield, records = E["U"], E["jfield"], E["records"]
    Logic, Core, Cmds, Log = L["Logic"], L["Core"], L["Cmds"], L["Log"]
    Spr, Smp, Tick = JClass(PKG + "KpSprint"), JClass(PKG + "KpSample"), JClass(PKG + "KpTick")
    PA, PW, st, comps, tt, world, f1, HA = L["PA"], L["PW"], L["st"], L["comps"], L["tt"], L["world"], L["f1"], L["HA"]
    said, run_tasks, tick, chain, IT = L["said"], L["run_tasks"], L["tick"], L["chain"], L["IT"]
    MVS, CMV, SICS, SIC, MOD, CT = L["MVS"], L["CMV"], L["SICS"], L["SIC"], L["MOD"], L["CT"]
    SB = JClass("java.lang.StringBuilder")
    MSETc = JClass("com.hypixel.hytale.protocol.MovementSettings")
    # ---- the reflection field list against the REAL classes
    want = sorted(str(f.getName()) for f in MVS.class_.getDeclaredFields() if MOD.isPublic(f.getModifiers()) and not MOD.isStatic(f.getModifiers()))
    got = sorted(str(f.getName()) for f in Logic.mvFields())
    K.check(got == want and len(got) >= 24 and all(x in got for x in ("sprinting", "running", "walking", "idle", "horizontalIdle", "extraJumpsUsed")),
            "S: KpLogic.mvFields() = every public field of the real protocol MovementStates (%d): %s" % (len(got), got))
    K.check(Logic.mvFields() is not None and Logic.MVF is not None and len(Logic.MVF) == len(got), "S: the field list is cached")
    nm = str(Logic.names(Logic.mvFields()))
    K.check(all(x in nm for x in want) and str(Logic.names(None)) == "", "S: names() lists them all: %s" % nm)
    wset = sorted(str(f.getName()) for f in MSETc.class_.getDeclaredFields() if MOD.isPublic(f.getModifiers()) and not MOD.isStatic(f.getModifiers()))
    gset = sorted(str(f.getName()) for f in Logic.setFields())
    K.check(gset == wset and "forwardSprintSpeedMultiplier" in gset and "strafeRunSpeedMultiplier" in gset and "backwardRunSpeedMultiplier" in gset,
            "S: KpLogic.setFields() = every public field of the real MovementSettings (%d)" % len(gset))
    K.check(len(Logic.fieldsOf(None)) == 0, "S: fieldsOf(null) = empty")
    # ---- direction words, numbers, text
    D = lambda x, z, y=0.0, h=True: str(Logic.dir(JDouble(x), JDouble(z), JFloat(y), h))
    K.check([D(0, -5), D(0, 5), D(-5, 0), D(5, 0), D(0.05, 0), D(0, 5, 180.0), D(0, 5, math.pi), D(-3, -3), D(3, 3), D(3, -3), D(-3, 3), D(0, -5, 0, False)]
            == ["forward", "back", "left", "right", "still", "forward", "forward", "forward-left", "back-right", "forward-right", "back-left", "moving"],
            "S: dir() - 8 ways against the look yaw (radians; > 7 = degrees), still, no yaw yet")
    K.check([int(Logic.relDeg(JDouble(-5), JDouble(0), JFloat(0))), int(Logic.relDeg(JDouble(5), JDouble(0), JFloat(0))),
             int(Logic.relDeg(JDouble(0), JDouble(-5), JFloat(0))), int(Logic.relDeg(JDouble(0), JDouble(5), JFloat(0)))] == [90, -90, 0, 180],
            "S: relDeg - 0 forward, +90 left, -90 right, 180 back")
    K.check([str(Logic.r1(JDouble(v))) for v in (0.04, -0.06, 12.34, -2.5, 0.0)] == ["0.0", "-0.1", "12.3", "-2.5", "0.0"], "S: r1")
    K.check(str(Logic.velText(JDouble(-5), JDouble(0), JFloat(0), True)) == "left 5.0 b/s (90 deg) [x -5.0 z 0.0]"
            and str(Logic.velText(JDouble(0), JDouble(0), JFloat(0), True)) == "still 0.0 b/s [x 0.0 z 0.0]"
            and str(Logic.velText(JDouble(0), JDouble(-4), JFloat(0), False)) == "moving 4.0 b/s [x 0.0 z -4.0]", "S: velText")
    K.check(str(Logic.velKey(JDouble(-5), JDouble(0), JFloat(0), True)) == "left@5" and str(Logic.wishKey(JDouble(0), JDouble(0), JDouble(-1))) == "0.0,0.0,-1.0"
            and str(Logic.wishText(JDouble(0), JDouble(0), JDouble(-1), JFloat(0), True)) == "(0.0,0.0,-1.0) forward len 1.0", "S: velKey / wishKey / wishText")
    K.check(bool(Logic.skipComp("MovementStatesComponent")) and bool(Logic.skipComp("TransformComponent")) and not bool(Logic.skipComp("PlayerInput"))
            and not bool(Logic.skipComp("Velocity")) and not bool(Logic.skipComp("MovementManager")), "S: skipComp (fix round: Velocity / MovementManager diffed too)")
    K.check(str(Logic.cut("abcdef", 3)) == "abc..." and str(Logic.cut(None, 3)) == "null" and str(Logic.cut("ab", 3)) == "ab", "S: cut")
    sb = SB()
    Logic.add(sb, "a")
    Logic.add(sb, "")
    Logic.add(sb, None)
    Logic.add(sb, "b")
    K.check(str(sb) == "a, b", "S: add")
    MI = JClass("com.hypixel.hytale.protocol.packets.player.MouseInteraction")
    MBE = JClass("com.hypixel.hytale.protocol.MouseButtonEvent")
    mi = MI()
    mi.activeSlot = 3
    mi.itemInHandId = "Weapon_Sword_Iron"
    mi.mouseButton = MBE()
    dm = str(Logic.dump(mi, 2))
    K.check(dm.startswith("MouseInteraction{") and "activeSlot=3" in dm and "itemInHandId='Weapon_Sword_Iron'" in dm and "mouseButton=MouseButtonEvent{" in dm
            and "PACKET_ID" not in dm, "S: dump of a real MouseInteraction (public fields, 2 levels, no statics): %s" % dm)
    K.check(str(Logic.dump(JArray(JInt)([1, 2, 3, 4, 5]), 1)) == "[1 2 3 +2]" and str(Logic.dump(None, 1)) == "null" and str(Logic.dump(IT.Dodge, 1)) == "Dodge"
            and str(Logic.dump(mi, 0)) == "MouseInteraction" and str(Logic.dump(JArray(JInt)([1]), 0)) == "[..]", "S: dump arrays / null / enum / depth 0")
    pl = str(Logic.pktLine(mi))
    K.check(pl.startswith("[KeyProbe] sprint packet MouseInteraction MouseInteraction{") and len(pl) <= 280 and Logic.pktLine(None) is None, "S: pktLine: %s" % pl)
    sp_ = SICS()
    sp_.updates = JArray(SIC)([chain("Ability1", 1, True, "NotFinished"), None])
    K.check(str(Logic.pktLine(sp_)) == "[KeyProbe] sprint packet SyncInteractionChains: Ability1 start NotFinished item SkyyKeyProbe_Tester;",
            "S: pktLine of SyncInteractionChains: %s" % Logic.pktLine(sp_))
    # ---- the diff printer on synthetic MovementStates
    fs = Logic.mvFields()
    prev = JArray(JObject)(len(fs))
    m1 = MVS()
    m1.onGround = True
    K.check(int(Logic.diff(fs, prev, m1, "", SB())) == 0, "S: diff - the first look only sets the baseline")
    m2 = MVS()
    m2.onGround, m2.sprinting, m2.running, m2.extraJumpsUsed = True, True, True, 1
    b2 = SB()
    n2 = int(Logic.diff(fs, prev, m2, "x.", b2))
    K.check(n2 == 3 and "x.sprinting false->true" in str(b2) and "x.running false->true" in str(b2) and "x.extraJumpsUsed 0->1" in str(b2),
            "S: diff prints only the changed fields: %s" % b2)
    K.check(int(Logic.diff(fs, prev, m2, "", SB())) == 0 and int(Logic.diff(None, prev, m2, "", SB())) == 0 and int(Logic.diff(fs, prev, None, "", SB())) == 0,
            "S: diff - no change / no fields / no object")
    # ---- KpSprint: the chat cap
    s = Spr(PA["pr"], PA["uuid"], "Skyy")
    got = [s.chatLine("l%d" % i, JLong(1000 + i)) for i in range(12)]
    K.check(sum(1 for x in got if x is not None) == 10 and got[10] is None and got[11] is None and int(s.logged) == 2,
            "S: the first 10 lines of a second go to chat, the next to the log only")
    K.check(any("(chat cap) to Skyy: l10" in m for lv, m in records()), "S: a capped line is in the server log")
    nx = str(s.chatLine("next", JLong(2100)))
    K.check(nx == "next (+2 more lines in the server log only)", "S: the next chat line says how many went to the log only: %s" % nx)
    for i in range(45):
        s.chatLine("m%d" % i, JLong(3500 + i))
    K.check(int(s.shown) == 21 and int(s.logged) == 37 and int(s.dropped) == 0, "F: 45 lines in a second: 10 chat, 35 log only, none dropped (%d / %d / %d)"
            % (int(s.shown), int(s.logged), int(s.dropped)))
    K.check(all(any(("(chat cap) to Skyy: m%d" % i) == m[len("[SkyyKeyProbe] "):] or m.endswith("(chat cap) to Skyy: m%d" % i) for lv, m in records()) for i in range(10, 45)),
            "F: EVERY line past the chat cap is in the server log (m10..m44)")
    for i in range(120):
        s.chatLine("q%d" % i, JLong(5000 + i))
    K.check(int(s.shown) == 31 and int(s.logged) == 127 and int(s.dropped) == 20, "F: beyond 100 a second lines are only counted (%d / %d / %d)"
            % (int(s.shown), int(s.logged), int(s.dropped)))
    K.check(s.chatLine(None, JLong(9000)) is None and str(s.chatLine("back", JLong(500))).startswith("back"), "S: chatLine(null); a clock going back resets the window")
    # ---- movement()
    POS, V3, DIR = JClass("com.hypixel.hytale.protocol.Position"), JClass("com.hypixel.hytale.protocol.Vector3d"), JClass("com.hypixel.hytale.protocol.Direction")

    def cm(ms=None, wish=None, vel=None, yaw=None):
        c_ = CMV()
        c_.movementStates = ms
        if wish is not None:
            c_.wishMovement = POS(JDouble(wish[0]), JDouble(wish[1]), JDouble(wish[2]))
        if vel is not None:
            c_.velocity = V3(JDouble(vel[0]), JDouble(vel[1]), JDouble(vel[2]))
        if yaw is not None:
            c_.lookOrientation = DIR(JFloat(yaw), JFloat(0), JFloat(0))
        return c_

    def ms(**kw):
        m_ = MVS()
        m_.onGround = True
        for k_, v_ in kw.items():
            setattr(m_, k_, v_)
        return m_
    s2 = Spr(PA["pr"], PA["uuid"], "Skyy")
    K.check(s2.movement(cm(ms(), (0, 0, 0), (0, 0, 0), 0.0)) is None, "S: movement - the first packet is the baseline")
    K.check(str(s2.movement(cm(ms(sprinting=True)))) == "[KeyProbe] sprint client: sprinting false->true", "S: movement - sprinting edge")
    K.check(str(s2.movement(cm(None, (-1, 0, 0)))) == "[KeyProbe] sprint client: wish (-1.0,0.0,0.0) left len 1.0", "S: movement - wish change")
    K.check(str(s2.movement(cm(None, None, (-5, 0, 0)))) == "[KeyProbe] sprint client: velocity left 5.0 b/s (90 deg) [x -5.0 z 0.0]", "S: movement - velocity change")
    K.check(s2.movement(cm(None, None, (-5.2, 0, 0.1))) is None, "S: movement - the same direction + rounded speed prints nothing")
    l3 = str(s2.movement(cm(ms(sprinting=False, crouching=True), (0, 0, 1), (0, 0, 4), 0.0)))
    K.check("sprinting true->false" in l3 and "crouching false->true" in l3 and "wish (0.0,0.0,1.0) back len 1.0" in l3 and "velocity back 4.0 b/s (180 deg)" in l3,
            "S: movement - several changes in one line: %s" % l3)
    K.check(s2.movement(cm()) is None and s2.movement(None) is None and int(s2.moves) == 8, "S: movement - empty / null packets")
    # ---- packet()
    PONG = JClass("com.hypixel.hytale.protocol.packets.connection.Pong")
    K.check(s2.packet(PONG()) is None and s2.packet(None) is None and str(s2.packet(mi)).startswith("[KeyProbe] sprint packet MouseInteraction"),
            "S: packet - Pong only counted, others printed")
    K.check(int(s2.pkts.get("Pong")) == 1 and int(s2.pkts.get("MouseInteraction")) == 1 and int(s2.pkts.get("ClientMovement")) == 8, "S: packet counts")
    # ---- sample()
    s3 = Spr(PA["pr"], PA["uuid"], "Skyy")
    JS, JI = JArray(JString), JArray(JInt)

    def SU(*rows):
        return JArray(JObject)([JS(r) for r in rows])
    set1 = MSETc()
    set1.forwardSprintSpeedMultiplier = JFloat(1.5)
    b0 = str(s3.sample(ms(), ms(), JDouble(0), JDouble(0), True, JFloat(0), True, set1, JFloat(10), True, JS(["A#1", "B#2"]), SU(["f=1", "g=a"], ["h=0"]), 2))
    K.check(b0 == "[KeyProbe] sprint: baseline taken (2 components, stamina 10.00). Now, 2 s apart: TAP sprint while holding W, A, D, S, then standing still; then HOLD sprint 2 s while holding A, D, S.",
            "S: sample - the baseline line: %s" % b0)
    K.check(s3.sample(ms(), ms(), JDouble(0), JDouble(0), True, JFloat(0), True, set1, JFloat(10), True, JS(["A#1", "B#2"]), SU(["f=1", "g=a"], ["h=0"]), 2) is None,
            "S: sample - nothing changed = no line")
    set2 = MSETc()
    set2.forwardSprintSpeedMultiplier = JFloat(1.65)
    l4 = str(s3.sample(ms(sprinting=True), ms(running=True), JDouble(5), JDouble(0), True, JFloat(0), True, set2, JFloat(9.5), True,
                       JS(["A#1", "C#3", "B#2"]), SU(["f=7", "g=a"], ["k=3"], ["h=0"]), 3))
    K.check(l4.startswith("[KeyProbe] sprint server: sprinting false->true") and "sent.running false->true" in l4 and "velocity right 5.0 b/s (-90 deg)" in l4
            and "settings.forwardSprintSpeedMultiplier 1.5->1.65" in l4 and "stamina DRAINS at 9.50" in l4 and "component A#1 changed: f 1->7" in l4 and "g a" not in l4
            and "component added C#3" in l4 and "B#2" not in l4, "S: sample - server states, sent copy, velocity, settings, stamina, components: %s" % l4)
    l5 = s3.sample(ms(sprinting=True), ms(running=True), JDouble(5), JDouble(0), True, JFloat(0), True, set2, JFloat(9.0), True, JS(["A#1", "C#3"]), SU(["f=7", "g=a"], ["k=3"]), 2)
    K.check(str(l5) == "[KeyProbe] sprint server: component removed B#2", "S: sample - stamina still draining = no line; a removed component: %s" % l5)
    l6 = str(s3.sample(None, None, JDouble(0), JDouble(0), False, JFloat(0), False, None, JFloat(9.0), True, None, None, 0))
    K.check(l6 == "[KeyProbe] sprint server: stamina steady at 9.00", "S: sample - stamina steady; missing parts skipped: %s" % l6)
    K.check(str(s3.sample(None, None, JDouble(0), JDouble(0), False, JFloat(0), False, None, JFloat(9.5), True, None, None, 0)) == "[KeyProbe] sprint server: stamina regens at 9.50",
            "S: sample - stamina regens")
    mute = []
    for i in range(SP_MUTE_N + 2):
        mute.append(s3.sample(None, None, JDouble(0), JDouble(0), False, JFloat(0), False, None, JFloat(0), False, JS(["A#1", "C#3"]),
                              SU(["f=%d" % (100 + i), "g=a"], ["k=3"]), 2))
    K.check(str(mute[0]) == "[KeyProbe] sprint server: component A#1 changed: f 7->100"
            and all(str(x).startswith("[KeyProbe] sprint server: component A#1 changed: f ") for x in mute[:SP_MUTE_N - 1])
            and str(mute[SP_MUTE_N - 1]) == "[KeyProbe] sprint server: component field A#1.f changes all the time - muted" and mute[-1] is None
            and s3.muted.contains("A#1.f"), "F: sample - a FIELD changing more than %d times is muted with one line: %s" % (SP_MUTE_N, mute[SP_MUTE_N - 1]))
    lg_ = str(s3.sample(None, None, JDouble(0), JDouble(0), False, JFloat(0), False, None, JFloat(0), False, JS(["A#1", "C#3"]), SU(["f=1", "g=b"], ["k=3"]), 2))
    K.check(lg_ == "[KeyProbe] sprint server: component A#1 changed: g a->b", "F: per-field mute - the muted field is silent, the other field of the same component still prints: %s" % lg_)
    lm_ = str(s3.sample(None, None, JDouble(0), JDouble(0), False, JFloat(0), False, None, JFloat(0), False, JS(["A#1", "C#3"]),
                        SU(["f=2", "g=c"], ["k=4", "a=1", "b=1", "c=1", "d=1"]), 2))
    K.check("component C#3 changed: k 3->4; a null->1; b null->1; c null->1 +1 more" in lm_ and "component A#1 changed: g b->c" in lm_,
            "F: a changed component prints at most 4 fields + the rest counted; a new field shows old as null: %s" % lm_)
    sm = [str(x) for x in s3.summary()]
    K.check(sm[0].startswith("[KeyProbe] Sprint probe OFF for Skyy: 0 movement packets, %d server samples" % int(s3.samples)) and sm[1] == "  Packets you sent: none"
            and sm[2] == "  Component fields muted (changed all the time): A#1.f", "S: summary: %s" % sm)
    sm2 = [str(x) for x in s2.summary()]
    K.check(sm2[1] == "  Packets you sent: ClientMovement 8, MouseInteraction 1, Pong 1" and len(sm2) == 2, "S: summary packet counts: %s" % sm2)
    # ---- FIX ROUND: the component VALUE summary on REAL engine components (the 0.2 hashCode blind spot)
    VELc0 = JClass("com.hypixel.hytale.server.core.modules.physics.component.Velocity")
    PIc0 = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput")
    SMS0 = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$SetMovementStates")
    OBJ = JClass("java.lang.Object")
    K.check(VELc0.class_.getMethod("hashCode").getDeclaringClass() == OBJ.class_ and PIc0.class_.getMethod("hashCode").getDeclaringClass() == OBJ.class_,
            "F: engine fact - Velocity and PlayerInput do NOT override hashCode (identity hash)")
    v0 = VELc0()
    h0, c0_ = int(v0.hashCode()), [str(x) for x in Logic.compSum(v0)]
    v0.set(JDouble(-5), JDouble(0), JDouble(1.234))
    h1, c1_ = int(v0.hashCode()), [str(x) for x in Logic.compSum(v0)]
    K.check(h0 == h1 and c0_ != c1_ and any(x.startswith("velocity={") and "x=-5.00" in x and "z=1.23" in x for x in c1_),
            "F: Velocity.set() in place - hashCode unchanged (old diff blind), compSum changed: %s" % c1_)
    p0 = PIc0()
    ph0, pc0_ = int(p0.hashCode()), [str(x) for x in Logic.compSum(p0)]
    p0.queue(U.allocateInstance(SMS0.class_))
    ph1, pc1_ = int(p0.hashCode()), [str(x) for x in Logic.compSum(p0)]
    K.check(ph0 == ph1 and "inputUpdateQueue=size=0" in pc0_ and "inputUpdateQueue=size=1 [SetMovementStates]" in pc1_ and "mountId=0" in pc1_,
            "F: PlayerInput.queue() in place - hashCode unchanged, compSum shows the queue size + element type: %s" % pc1_)
    K.check(len(Logic.compSum(None)) == 0 and len(Logic.allFields(None)) == 0 and bool(Logic.allFields(VELc0.class_).equals(Logic.allFields(VELc0.class_))),
            "F: compSum(null) / allFields(null) empty; allFields cached per class (the same array twice)")
    K.check(Logic.CF.containsKey(VELc0.class_) and Logic.CF.containsKey(PIc0.class_), "F: the field cache holds the classes summarised")
    UUIDc = JClass("java.util.UUID")
    uu = UUIDc(JLong(1), JLong(2))
    HM = JClass("java.util.HashMap")()
    HM.put("a", "b")
    AL = JClass("java.util.ArrayList")()
    for x_ in ("a", "b", "c", "d"):
        AL.add(x_)
    vt = [str(Logic.vtext(x_, 1)) for x_ in (None, JDouble(1.005), JFloat(-0.004), JInt(7), True, IT.Dodge, "abc", AL, HM, JArray(JInt)([1, 2, 3, 4, 5]), uu)]
    K.check(vt == ["null", "1.00", "0.00", "7", "true", "Dodge", "'abc'", "size=4 [String String String ...]", "size=1", "len=5[1 2 3 4 ...]", str(uu)],
            "F: vtext - null / float 2 decimals / int / bool / enum / string / collection / map / array / java object: %s" % vt)
    nest = str(Logic.vtext(mi, 1))
    deep = str(Logic.vtext(mi, 2))
    K.check(nest.startswith("{") and "activeSlot=3" in nest and "mouseButton={" not in nest and "mouseButton=MouseButtonEvent@" in nest
            and deep.startswith("MouseInteraction@"), "F: vtext - an object = its fields one level deep, deeper = type@identity: %s" % nest[:200])
    longc = [str(x) for x in Logic.compSum(mi)]
    K.check(all(len(x) <= len(Logic.fname(x)) + 1 + 100 for x in longc), "F: compSum - every field text at most 100 chars (long ones = 70 + hash)")
    K.check(str(Logic.fname("abc=1=2")) == "abc" and str(Logic.fval("abc=1=2")) == "1=2" and str(Logic.fname(None)) == "?" and str(Logic.fval(None)) == "null"
            and str(Logic.fval("x")) == "", "F: fname / fval")
    # ---- THROUGH THE ENGINE: /keyprobe sprint on, the real filter, the world thread
    Core.STATES.remove(PA["uuid"])          # the 0.1 watcher off for PA: only sprint lines below
    Core.AUTO_TIMER = False
    said()
    Cmds.run(PA["ref"], st, PA["pr"], "sprint", None)
    on = said()
    K.check(len(on) == 2 and on[0].startswith("[KeyProbe] Sprint probe ON") and "then HOLD sprint 2 s while holding A, D, S" in on[0]
            and "stops by itself after 5 min" in on[0] and ("(%d fields: " % len(want)) in on[1] and "sprinting" in on[1]
            and Core.SPRINT.containsKey(PA["uuid"]) and Core.TIMER is None, "S: /keyprobe sprint ON lists the reflected fields: %s" % on)
    SP = Core.SPRINT.get(PA["uuid"])
    tick(1000)
    K.check(not bool(f1.test(HA, cm(ms(), (0, 0, 0), (0, 0, 0), 0.0))) and run_tasks() == 0, "S: the first movement packet through the REAL filter = baseline, never blocks")
    tick(100)
    f1.test(HA, cm(ms(sprinting=True)))
    K.check(run_tasks() == 1 and said() == ["[KeyProbe] sprint client: sprinting false->true"], "S: a sprint edge through the real filter -> chat on the world thread")
    tick(100)
    K.check(not bool(f1.test(HA, mi)) and run_tasks() == 1 and said()[0].startswith("[KeyProbe] sprint packet MouseInteraction"), "S: a MouseInteraction packet -> its line")
    tick(100)
    K.check(not bool(f1.test(HA, PONG())) and run_tasks() == 0, "S: Pong -> counted only")
    K.check(any("to Skyy: [KeyProbe] sprint client: sprinting false->true" in m for lv, m in records()), "S: every chat line is in the server log ([SkyyKeyProbe] to <name>: [KeyProbe] ...)")
    # ---- the server sampler: real components on the stand-in store
    EM, EMc = L["EM"], L["em"]
    MSCc = JClass("com.hypixel.hytale.server.core.entity.movement.MovementStatesComponent")
    VELc = JClass("com.hypixel.hytale.server.core.modules.physics.component.Velocity")
    HRTc = JClass("com.hypixel.hytale.server.core.modules.entity.component.HeadRotation")
    MMGc = JClass("com.hypixel.hytale.server.core.entity.entities.player.movement.MovementManager")
    ESMc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatMap")
    ESVc = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatValue")
    ESMOD = JClass("com.hypixel.hytale.server.core.modules.entitystats.EntityStatsModule")
    DSTc = JClass("com.hypixel.hytale.server.core.modules.entitystats.asset.DefaultEntityStatTypes")
    PIc = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput")
    esmod = U.allocateInstance(ESMOD.class_)
    ct_esm = U.allocateInstance(CT.class_)
    jfield(CT, "index").set(ct_esm, JInt(90))
    jfield(ESMOD, "entityStatMapComponentType").set(esmod, ct_esm)
    jfield(ESMOD, "instance").set(None, esmod)
    jfield(DSTc, "STAMINA").set(None, JInt(2))
    ct_pi = U.allocateInstance(CT.class_)
    jfield(CT, "index").set(ct_pi, JInt(91))
    cts = {"msc": MSCc.getComponentType(), "vel": VELc.getComponentType(), "hrt": HRTc.getComponentType(), "mmg": MMGc.getComponentType(),
           "esm": ESMc.getComponentType(), "pi": ct_pi}
    K.check(all(v is not None for v in cts.values()), "S: the component types resolve (EntityModule / EntityStatsModule stand-ins): %s" % cts)
    tcls = {"msc": MSCc, "vel": VELc, "hrt": HRTc, "mmg": MMGc, "esm": ESMc, "pi": PIc}
    for k_, c_ in cts.items():
        jfield(CT, "tClass").set(c_, tcls[k_].class_)
    for k_, c_ in tt.items():
        jfield(CT, "tClass").set(c_, c_.getTypeClass() or JClass("java.lang.Object").class_)
    msc = MSCc()
    msc.setMovementStates(ms())
    msc.setSentMovementStates(ms())
    vel = VELc()
    vel.set(JDouble(0), JDouble(0), JDouble(0))
    hrt = HRTc()
    hrt.getRotation().setYaw(JFloat(0))
    mmg = U.allocateInstance(MMGc.class_)
    mset = MSETc()
    mset.forwardSprintSpeedMultiplier = JFloat(1.5)
    jfield(MMGc, "settings").set(mmg, mset)
    esm = U.allocateInstance(ESMc.class_)
    esv = U.allocateInstance(ESVc.class_)
    jfield(ESVc, "value").set(esv, JFloat(10))
    jfield(ESMc, "values").set(esm, JArray(ESVc)([None, None, esv]))
    K.check(abs(float(esm.get(int(DSTc.getStamina())).get()) - 10.0) < 1e-6, "S: the stand-in stamina reads through EntityStatMap.get(DefaultEntityStatTypes.getStamina())")
    pc = comps.get(PA["ref"])
    pin = PIc()
    for k_, v_ in (("msc", msc), ("vel", vel), ("hrt", hrt), ("mmg", mmg), ("esm", esm), ("pi", pin)):
        pc.put(cts[k_], v_)
    allct = list(tt.values()) + list(cts.values())
    arr = [None] * (max(int(c_.getIndex()) for c_ in allct) + 1)
    for c_ in allct:
        arr[int(c_.getIndex())] = c_
    ARCH = JClass("com.hypixel.hytale.component.Archetype")
    arch2 = U.allocateInstance(ARCH.class_)
    jfield(ARCH, "componentTypes").set(arch2, JArray(CT)(arr))
    old_arch = st.arch
    st.arch = arch2
    K.check(int(arch2.length()) == len(arr) and arch2.get(int(ct_pi.getIndex())) == ct_pi, "S: the stand-in Archetype answers length() / get(i)")
    pbu = jfield(JClass("com.hypixel.hytale.server.core.universe.Universe"), "playersByUuid").get(E["uni"])
    pbu.put(PA["uuid"], PA["pr"])
    K.check(JClass("com.hypixel.hytale.server.core.universe.Universe").get().getPlayer(PA["uuid"]) is not None, "S: Universe.getPlayer finds the stand-in player")
    said()
    Core.tickAll()
    K.check(world.tasks is not None and world.tasks.size() == 1 and bool(SP.busy), "S: tickAll hands ONE KpSample to the player's world (busy set)")
    Core.tickAll()
    K.check(world.tasks.size() == 1, "S: a second tick while the sample is pending adds nothing")
    K.check(run_tasks() == 1, "S: the sample runs on the world thread")
    bl = said()
    K.check(len(bl) == 1 and bl[0].startswith("[KeyProbe] sprint: baseline taken (6 components, stamina 10.00)") and not bool(SP.busy),
            "S: the first sample = the baseline line (6 components: storage, hotbar, backpack, PlayerInput, Velocity, MovementManager): %s" % bl)
    tick(100)
    msc.getMovementStates().sprinting = True
    msc.getSentMovementStates().sprinting = True
    vel.set(JDouble(-5), JDouble(0), JDouble(0))
    jfield(ESVc, "value").set(esv, JFloat(9.5))
    mset.forwardSprintSpeedMultiplier = JFloat(1.65)
    SMSc = JClass("com.hypixel.hytale.server.core.modules.entity.player.PlayerInput$SetMovementStates")
    pin.queue(U.allocateInstance(SMSc.class_))          # an IN-PLACE change: same PlayerInput object, same identity hashCode
    Core.tickAll()
    run_tasks()
    l7 = said()
    K.check(len(l7) == 1 and l7[0].startswith("[KeyProbe] sprint server: sprinting false->true, sent.sprinting false->true, velocity left 5.0 b/s (90 deg)")
            and "settings.forwardSprintSpeedMultiplier 1.5->1.65" in l7[0] and "stamina DRAINS at 9.50" in l7[0] and "component PlayerInput#91 changed: inputUpdateQueue size=0->size=1 [SetMovementStates]" in l7[0]
            and "component Velocity#" in l7[0]
            and "TransformComponent" not in l7[0] and "HeadRotation" not in l7[0], "S: a sample after changes = one server line: %s" % l7)
    tick(100)
    Core.tickAll()
    run_tasks()
    K.check(said() == ["[KeyProbe] sprint server: stamina steady at 9.50"], "S: the stamina trend change (drains -> steady) prints once")
    tick(100)
    Core.tickAll()
    run_tasks()
    K.check(said() == [], "S: a quiet sample prints nothing")
    # busy: a sample that never ran is retried after 2 s
    SP.busy = True
    SP.busyAt = JLong(int(Core.now()))
    Core.tickAll()
    K.check(world.tasks.size() == 0, "S: a pending sample younger than 2 s is not doubled")
    tick(2500)
    Core.tickAll()
    K.check(world.tasks.size() == 1, "S: ... and retried after 2 s (a world that never ran it does not stop the probe)")
    run_tasks()
    said()
    # no entity / no sp / error path
    Smp(None).run()
    jfield(L["PRc"], "entity").set(PA["pr"], None)
    Smp(SP).run()
    K.check(said() == [], "S: a sample without an entity (relog / world switch) does nothing")
    jfield(L["PRc"], "entity").set(PA["pr"], PA["ref"])
    e0 = int(Smp.ERRORS.get())
    good_n = SP.compN
    SP.compN = None
    pc.put(ct_pi, PIc())
    Smp(SP).run()
    SP.compN = good_n
    K.check(int(Smp.ERRORS.get()) == e0 + 1 and any("sprint sample failed" in m for lv, m in records()), "S: a failing sample is caught and logged (3 times at most)")
    # no world: the sampler skips
    Cmds.sprint(PW["pr"])
    said()
    pbu.put(PW["uuid"], PW["pr"])
    Core.tickAll()
    K.check(world.tasks.size() == 0 or all(not bool(t_.sp.pr.equals(PW["pr"])) for t_ in [world.tasks.get(i) for i in range(int(world.tasks.size()))]),
            "S: a player without a world gets no sample")
    run_tasks()
    said()
    # the player left the server = stopped
    pbu.remove(PW["uuid"])
    Core.tickAll()
    K.check(not Core.SPRINT.containsKey(PW["uuid"]) and any("NoWorld left the server - sprint probe off" in m for lv, m in records()), "S: a player who left is dropped")
    run_tasks()
    said()
    # errors in tickAll are caught
    Core.SPRINT.put(JClass("java.util.UUID").randomUUID(), JString("not a sprint state"))
    t0 = int(Core.ERRORS.get())
    Core.tickAll()
    K.check(int(Core.ERRORS.get()) == t0 + 1, "S: a broken entry in tickAll is caught")
    for k_ in [k for k in Core.SPRINT.keySet() if not k.equals(PA["uuid"])]:
        Core.SPRINT.remove(k_)
    run_tasks()
    said()
    # KpTick.run = tickAll
    Tick().run()
    K.check(world.tasks.size() == 1, "S: KpTick.run() calls KpCore.tickAll (one sample queued)")
    run_tasks()
    said()
    # ---- FIX ROUND: the sample period beats the world tick; at most 3 probes; auto stop after 5 min; the Timer stops in tickAll
    TTc = JClass("com.hypixel.hytale.server.core.util.thread.TickingThread")
    tf_ = TTc.class_.getDeclaredField("TPS")
    tf_.setAccessible(True)
    tps = int(tf_.get(None))
    K.check(int(Core.TICK_MS) == 20 and int(Core.TICK_MS) < 1000 // tps, "F: the 20 ms sampler is faster than one world tick (TickingThread.TPS = %d -> %d ms)" % (tps, 1000 // tps))
    K.check(int(Core.MAX_N) == 3 and int(Core.MAX_MS) == 300000, "F: MAX_N 3 / MAX_MS 5 min")
    fakes = []
    for i in range(2):
        fu = JClass("java.util.UUID").randomUUID()
        fakes.append(fu)
        Core.SPRINT.put(fu, Spr(None, fu, "Fake%d" % i))
    said()
    Cmds.sprint(PW["pr"])
    cap_ = said()
    K.check(len(cap_) == 1 and cap_[0].startswith("[KeyProbe] 3 players are already running the sprint probe") and not Core.SPRINT.containsKey(PW["uuid"])
            and int(Core.SPRINT.size()) == 3, "F: a 4th player is refused while 3 probes run: %s" % cap_)
    for fu in fakes:
        Core.SPRINT.remove(fu)
    K.check(int(SP.started) > 0, "F: sprint ON stamps the start time (%d)" % int(SP.started))
    st0 = SP.started
    SP.busy = False
    tick(300001)
    Core.tickAll()
    run_tasks()
    au = said()
    K.check(not Core.SPRINT.containsKey(PA["uuid"]) and len(au) >= 2 and au[0] == "[KeyProbe] Sprint probe stopped by itself after 5 minutes (/keyprobe sprint starts it again)."
            and au[1].startswith("[KeyProbe] Sprint probe OFF for Skyy:"), "F: a probe older than 5 min stops itself and the summary is delivered: %s" % au[:2])
    Core.SPRINT.put(PA["uuid"], SP)          # back on for the checks below (same state)
    SP.started = JLong(int(Core.now()))
    Core.AUTO_TIMER = True
    Core.ensureTimer()
    K.check(Core.TIMER is not None, "F: (timer on)")
    Core.SPRINT.remove(PA["uuid"])
    Core.tickAll()
    K.check(Core.TIMER is None, "F: tickAll stops the Timer once no probe is left (left / auto-stopped players)")
    Core.AUTO_TIMER = False
    Core.SPRINT.put(PA["uuid"], SP)
    said()
    # off through the command = summary + timer stop
    Cmds.run(PA["ref"], st, PA["pr"], "sprint", None)
    off = said()
    K.check(off[0].startswith("[KeyProbe] Sprint probe OFF for Skyy: 2 movement packets,") and off[1].startswith("  Packets you sent: ClientMovement 2, MouseInteraction 1, Pong 1")
            and Core.SPRINT.isEmpty() and Core.TIMER is None, "S: /keyprobe sprint again = OFF + summary: %s" % off)
    # the real daemon Timer: on / off
    Core.AUTO_TIMER = True
    Cmds.sprint(PA["pr"])
    tm = Core.TIMER
    K.check(tm is not None, "S: sprint on starts the daemon Timer")
    Core.ensureTimer()
    K.check(Core.TIMER == tm, "S: ensureTimer twice = one Timer")
    Cmds.sprint(PA["pr"])
    K.check(Core.TIMER is None and Core.SPRINT.isEmpty(), "S: the last sprint off stops the Timer")
    run_tasks()
    said()
    Core.AUTO_TIMER = False
    # the any-player sub-command's execute()
    CTXc = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    WLD, STc, REF, PRc = JClass("com.hypixel.hytale.server.core.universe.world.World"), JClass("com.hypixel.hytale.component.Store"), L["REF"], L["PRc"]
    sc = JClass(PKG + "KProbeSprintCmd")()
    m_ = sc.getClass().getDeclaredMethod("execute", CTXc.class_, STc.class_, REF.class_, PRc.class_, WLD.class_)
    m_.setAccessible(True)
    m_.invoke(sc, JArray(JObject)([None, st, PA["ref"], PA["pr"], None]))
    K.check(said()[0].startswith("[KeyProbe] Sprint probe ON") and Core.SPRINT.containsKey(PA["uuid"]), "S: KProbeSprintCmd.execute toggles ON")
    m_.invoke(sc, JArray(JObject)([None, st, PA["ref"], PA["pr"], None]))
    K.check(said()[0].startswith("[KeyProbe] Sprint probe OFF") and Core.SPRINT.isEmpty(), "S: ... and OFF")
    # the 0.1 watcher and the sprint probe together: both see the same packet
    Cmds.run(PA["ref"], st, PA["pr"], "on", None)
    Cmds.sprint(PA["pr"])
    said()
    tick(1000)
    L["send"](HA, chain("Ability2", 77, True, "Finished"))
    run_tasks()
    both = said()
    K.check(any(x.startswith("[KeyProbe] sprint packet SyncInteractionChains: Ability2 start Finished") for x in both)
            and any(x.startswith("[KeyProbe] Ability2 fired") for x in both), "S: with /keyprobe on + sprint, one packet feeds both: %s" % both)
    Cmds.sprint(PA["pr"])
    Core.STATES.remove(PA["uuid"])
    said()
    st.arch = old_arch
    print("S. sprint probe: reflection list (%d fields), diff printer, cap, packets, server sampler, timer, commands executed" % len(want))


SP_MUTE_N = 40


def run_engine(out):
    """child: A + V + X"""
    from jpype import JClass, JArray, JObject, JInt, JFloat, JLong, JString, JBoolean, JShort
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR, B.JAVASSIST])
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    for n in CLASSES:
        try:
            Cls.forName(n, True, loader)
            K.ok += 1
        except Exception as e:
            K.fails.append("A: load %s: %s" % (n, e))
            print("LOAD FAIL", n, e)
    print("A. loaded + verified + initialised %d classes (-Xverify:all)" % len(CLASSES))
    if K.fails:
        K.save()
        return
    E = base_engine(K)
    U, jfield, AR, records, INTc, ROOTc = E["U"], E["jfield"], E["AR"], E["records"], E["INTc"], E["ROOTc"]
    jz, az = zipfile.ZipFile(JAR), zipfile.ZipFile(ASSETS)
    Log = JClass(PKG + "KpLog")
    Log.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyKeyProbe")

    # ================= V. THE ENGINE ASSET VALIDATORS (SkyyArmory 0.1.11 R14a function) on all 32 assets + every inline step
    AEI, ADT = JClass("com.hypixel.hytale.assetstore.AssetExtraInfo"), JClass("com.hypixel.hytale.assetstore.AssetExtraInfo$Data")
    RJR, Paths, ArrayList = JClass("com.hypixel.hytale.codec.util.RawJsonReader"), JClass("java.nio.file.Paths"), JClass("java.util.ArrayList")
    ITMc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    HLOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyyKeyProbeHarness")
    AZN, JN = set(az.namelist()), set(jz.namelist())
    KNOWN = set(os.path.basename(n).rsplit(".", 1)[0] for n in AZN | JN) | set(n[len("Common/"):] for n in AZN | JN if n.startswith("Common/"))
    ENV, WARN = [], []

    def dec(c, key, text):
        st = AR.getAssetStore(c.class_)
        ei = AEI(Paths.get(key + ".json"), ADT(c.class_, key, None))
        try:
            o = st.getCodec().decodeJsonAsset(RJR.fromJsonString(text), ei)
        except Exception as e:
            return None, "exception " + str(e)[:300], None
        prob = []
        vr = ei.getValidationResults()
        if vr is not None and vr.hasFailed():
            prob.append("validation failed %s" % [str(x) for x in (vr.getResults() or [])][:3])
        uk = [str(x) for x in ei.getUnknownKeys()]
        if uk:
            prob.append("unknown keys %s" % uk)
        return o, "; ".join(prob), ei

    def env(txt):
        fl = re.findall(r"FAIL: ([^\n]*)", txt)
        return bool(fl) and all(re.search(r"'([^']+)'", f) and re.search(r"'([^']+)'", f).group(1) in KNOWN
                                and ("doesn't exist" in f or "does not exist" in f) for f in fl)

    def validate(c, key, text, depth=0):
        n0 = len(records())
        o, w, ei = dec(c, key, text)
        if o is None:
            return None, w
        prob = [w] if w else []
        msgs = []
        try:
            AR.getAssetStore(c.class_).getCodec().validate(o, ei)
        except Exception as e:
            msgs.append("validate threw %s" % str(e)[:600])
        vr = ei.getValidationResults()
        try:
            if vr is not None:
                vr.logOrThrowValidatorExceptions(HLOG)
        except Exception as e:
            msgs.append("logOrThrowValidatorExceptions: %s" % str(e))
        try:
            ei.getData().loadContainedAssets(False)
        except Exception as e:
            msgs.append("contained assets: %s" % str(e)[:600])
        msgs += [m for lv, m in records()[n0:] if "Failed to validate" in m or "Array size" in m or "FAIL:" in m]
        for m in msgs:
            if "FAIL:" not in m and "Array size" not in m and "threw" not in m and "contained assets:" not in m:
                WARN.append("%s: %s" % (key, m[:200]))
                continue
            (ENV if env(m) else prob).append("%s: %s" % (key, m[:400]))
        if depth == 0 and c in (INTc, ROOTc):
            kids = []

            def kid(x, top):
                if isinstance(x, dict):
                    if isinstance(x.get("Type"), str) and not top:
                        kids.append(x)
                    for v in x.values():
                        kid(v, False)
                elif isinstance(x, list):
                    for v in x:
                        kid(v, False)
            kid(json.loads(text), True)
            for n_, k_ in enumerate(kids):
                ko, kw = validate(INTc, "%s_Inline%d" % (key, n_), json.dumps(k_), 1)
                if ko is None or kw:
                    prob.append("inline %d %s: %s" % (n_, k_.get("Type"), kw))
        return o, "; ".join(prob)
    neg_o, neg_w = validate(INTc, "SkyyKeyProbeHarness_OneParallel", json.dumps(
        {"Type": "Simple", "Next": {"Type": "Parallel", "Interactions": [{"Interactions": [{"Type": "Simple"}]}]}}))
    pos_o, pos_w = validate(INTc, "SkyyKeyProbeHarness_TwoParallel", json.dumps(
        {"Type": "Simple", "Next": {"Type": "Parallel", "Interactions": [{"Interactions": [{"Type": "Simple"}]}, {"Interactions": [{"Type": "Simple"}]}]}}))
    K.check(bool(neg_w) and "Array size is invalid" in neg_w and pos_o is not None and not pos_w,
            "V NEGATIVE CONTROL: the validator function refuses a one-entry Parallel with the engine's own message and passes 2 entries: %r | %r"
            % (str(neg_w)[:300], str(pos_w)[:200]))
    neg2_o, neg2_w = validate(ROOTc, "SkyyKeyProbeHarness_BadKey", json.dumps({"Interactions": [{"Type": "Simple"}], "NoSuchKey": 1}))
    K.check(bool(neg2_w) and "unknown keys" in neg2_w, "V NEGATIVE CONTROL: an unknown key is caught: %r" % str(neg2_w)[:200])
    roots = sorted(n for n in JN if n.startswith("Server/Item/RootInteractions/"))
    items = sorted(n for n in JN if n.startswith("Server/Item/Items/"))
    bad, objs = [], {"root": [], "item": []}
    for n in roots:
        o, w = validate(ROOTc, n.rsplit("/", 1)[1][:-5], jz.read(n).decode("utf-8"))
        if o is None or w:
            bad.append("root %s: %s" % (n, w))
        else:
            objs["root"].append(o)
    K.check(not bad and len(objs["root"]) == 30, "V: the ENGINE ASSET VALIDATORS pass on all 30 roots and every inline step (decode, full validate, "
            "logOrThrowValidatorExceptions, contained assets; no unknown key): %s" % bad[:4])

    def load(c, objs_):
        l_ = ArrayList()
        for o in objs_:
            l_.add(o)
        r_ = AR.getAssetStore(c.class_).loadAssets(PACK, l_)
        return not r_.hasFailed()
    K.check(bool(load(ROOTc, objs["root"])), "V: the 30 roots load into the real RootInteraction store from our pack")
    for n in items:
        o, w = validate(ITMc, n.rsplit("/", 1)[1][:-5], jz.read(n).decode("utf-8"))
        if o is None or w:
            bad.append("item %s: %s" % (n, w))
        else:
            objs["item"].append(o)
    K.check(not bad and len(objs["item"]) == 2, "V: the ENGINE ASSET VALIDATORS pass on both items: %s" % bad[:4])
    K.check(bool(load(ITMc, objs["item"])), "V: both items load into the real Item store from our pack")
    tester, helmet = ITMc.getAssetMap().getAsset(TESTER), ITMc.getAssetMap().getAsset(HELMET)
    K.check(tester is not None and helmet is not None and str(ITMc.getAssetMap().getAssetPack(TESTER)) == PACK, "V: the items sit in the store from our pack")
    IT = JClass("com.hypixel.hytale.protocol.InteractionType")
    if tester is not None and helmet is not None:
        ti, hi = tester.getInteractions(), helmet.getInteractions()
        K.check(ti.size() == 16 and all(str(ti.get(IT.valueOf(t))) == "SkyyKeyProbe_Tester_%s" % t for t in TYPES),
                "V: the decoded Key Tester answers getInteractions().get(type) = its root for all 16 types (what InteractionContext.getRootInteractionId reads)")
        K.check(hi.size() == 16 and all(str(hi.get(IT.valueOf(t))) == "SkyyKeyProbe_Helmet_%s" % t for t in TYPES if t not in ("Primary", "Secondary"))
                and hi.get(IT.Primary) is not None and hi.get(IT.Secondary) is not None,
                "V: the decoded helmet maps 14 types to its roots + Primary / Secondary to the inline EquipItem roots")
        K.check(helmet.getArmor() is not None and str(helmet.getArmor().getArmorSlot()) == "Head", "V: the helmet is Head armor")
        K.check(int(tester.getMaxStack()) == 1 and int(helmet.getMaxStack()) == 1, "V: both items MaxStack 1")
    # RootInteraction.build() of all 30 roots: no missing interaction, the specced operation classes
    RMAP = ROOTc.getAssetMap()
    n_miss0 = len([m for lv, m in records() if "Missing interaction" in m])
    cbad, rows = [], 0
    for n in roots:
        rid = n.rsplit("/", 1)[1][:-5]
        typ = rid.split("_")[2]
        r_ = RMAP.getAsset(rid)
        if r_ is None:
            cbad.append("%s not in store" % rid)
            continue
        try:
            r_.build()
        except Exception as e:
            cbad.append("build %s: %s" % (rid, str(e)[:200]))
            continue
        ops = []
        for i in range(int(r_.getOperationMax())):
            inner = r_.getOperation(i).getInnerOperation()
            if inner is not None and INTc.class_.isInstance(inner):
                ops.append(str(inner.getClass().getSimpleName()))
        want = (["ChargingInteraction"] + ["SendMessageInteraction"] * 3) if typ in KEYS else (["SendMessageInteraction"] if typ in LOUD else ["SimpleInteraction"])
        if sorted(ops) != sorted(want):
            cbad.append("%s ops %s (want %s)" % (rid, ops, want))
        rows += 1
    n_miss1 = len([m for lv, m in records() if "Missing interaction" in m])
    K.check(not cbad and rows == 30 and n_miss1 == n_miss0,
            "V: RootInteraction.build() of all 30 roots on the real stores - 0 missing interactions; keys = Charging + 3 SendMessage, swaps / death = "
            "SendMessage, held / worn = Simple: %s" % cbad[:4])
    rk = RMAP.getAsset("SkyyKeyProbe_Tester_Ability2")
    if rk is not None:
        K.check(bool(jfield(ROOTc, "requireNewClick").get(rk)) if "requireNewClick" in [str(f.getName()) for f in ROOTc.class_.getDeclaredFields()] else True,
                "V: the key roots decode RequireNewClick true")
    print("V. engine validators: 32 assets pass (+ inline steps); NOTE %d test-bed lines (vanilla names not loaded in the bare JVM) %s; %d WARNING-only"
          % (len(ENV), sorted(set(x.split(":")[0] for x in ENV))[:6], len(WARN)))
    K.notes.append("V test-bed lines: %s" % [x[:1200] for x in ENV[:4]])

    # ================= X. every code path
    Logic, State, Core, Say, Watch, Cmds = (JClass(PKG + "KpLogic"), JClass(PKG + "KpState"), JClass(PKG + "KpCore"), JClass(PKG + "KpSay"),
                                            JClass(PKG + "KpWatch"), JClass(PKG + "KpCmds"))
    SINK = JClass("java.util.ArrayList")()
    Log.SINK = SINK

    def said():
        out_ = [str(x) for x in SINK]
        SINK.clear()
        return out_
    # ---- KpLogic
    K.check(str(Logic.yn(True)) == "y" and str(Logic.yn(False)) == "n", "X: yn")
    K.check(str(Logic.typeName(int(IT.Ability2.ordinal()))) == "Ability2" and str(Logic.typeName(99)) == "Type#99" and str(Logic.typeName(-1)) == "Type#-1",
            "X: typeName (valid / out of range)")
    K.check(int(Logic.typeIndex("Dodge")) == int(IT.Dodge.ordinal()) and int(Logic.typeIndex("Nope")) == -1 and int(Logic.typeIndex(None)) == -1, "X: typeIndex")
    K.check([int(Logic.srcOf(TESTER, "Ability1", -1)), int(Logic.srcOf(HELMET, "Use", 0)), int(Logic.srcOf("Weapon_Sword_Iron", "Primary", 0)),
             int(Logic.srcOf(None, "Primary", -1)), int(Logic.srcOf("Weapon_Sword_Iron", "Equipped", 0)), int(Logic.srcOf(TESTER, "Equipped", 0)),
             int(Logic.srcOf(None, "Equipped", -1))] == [0, 1, 2, 2, 3, 3, 2], "X: srcOf - tester / helmet in hand / other / bare hand / worn armor")
    K.check([str(Logic.f2(JFloat(0.42))), str(Logic.f2(JFloat(1.0))), str(Logic.f2(JFloat(0.05))), str(Logic.f2(JFloat(-0.5))), str(Logic.f2(JFloat(12.345)))]
            == ["0.42", "1.00", "0.05", "-0.50", "12.35"], "X: f2")
    l1 = str(Logic.chainLine("Ability2", JLong(120), True, False, False, JFloat(0.0), 0, TESTER, -1, "Finished", 0))
    K.check(l1 == "[KeyProbe] Ability2 fired (hold 120 ms tap, crouching y, sprinting n, in air n)", "X: the spec line: %s" % l1)
    l2 = str(Logic.chainLine("Dodge", JLong(-1), False, True, True, JFloat(0.42), 3, "Weapon_Sword_Iron", 0, "Failed", 2))
    K.check(l2 == "[KeyProbe] Dodge fired (hold ? - no end seen within 5 s, crouching n, sprinting y, in air y) client charge 0.42 s - WORN armor, slot 0 [ended: Failed] (+2 more hidden)",
            "X: chainLine no end / charge / worn / ended / hidden: %s" % l2)
    l3 = str(Logic.chainLine("Use", JLong(450), False, False, False, JFloat(0.0), 2, "", -1, "", 0))
    l4 = str(Logic.chainLine("Use", JLong(300), False, False, False, JFloat(0.0), 1, HELMET, -1, None, 0))
    K.check(l3.endswith("(hold 450 ms hold, crouching n, sprinting n, in air n) - other item: empty hand") and l4.endswith("(hold 300 ms hold, crouching n, sprinting n, in air n) - Helmet in hand"),
            "X: chainLine hold / other empty hand / helmet: %s | %s" % (l3, l4))
    K.check("muted now" in str(Logic.muteLine("Held")) and str(Logic.moveLine(0, JLong(0), 0)) == "[KeyProbe] move: crouch ON"
            and str(Logic.moveLine(11, JLong(210), 3)) == "[KeyProbe] move: DOUBLE-TAP crouch (210 ms between the two presses) (+3 more hidden)"
            and str(Logic.moveLine(42, JLong(0), 0)) == "[KeyProbe] move: edge 42", "X: muteLine / moveLine")
    K.check(len(Logic.BINDS) >= 12 and "Ability1" in str(Logic.BINDS[3]) and "UNVERIFIED" in str(Logic.BINDS[3]) and "Dodge" in " ".join(str(x) for x in Logic.BINDS),
            "X: the build-time bind lines: %s" % [str(x)[:80] for x in Logic.BINDS][:4])
    # ---- KpState: gate / start / finish / move / report / reset
    UUID = JClass("java.util.UUID")
    s = State(UUID.fromString("00000000-0000-0000-0000-00000000a001"), "Tester1")
    A1, A2, HELD = int(IT.Ability1.ordinal()), int(IT.Ability2.ordinal()), int(IT.Held.ordinal())
    K.check([int(s.gate(A1, JLong(1000))), int(s.gate(A1, JLong(1100))), int(s.gate(A1, JLong(1200))), int(s.gate(A1, JLong(1400)))] == [0, -1, -1, 2]
            and int(s.gate(-1, JLong(1))) == -1 and int(s.gate(40, JLong(1))) == -1, "X: the 0.3 s cap counts hidden lines and reports them on the next line")
    codes = [int(s.gate(HELD, JLong(5000 + 400 * i))) for i in range(22)]
    K.check(codes[:20] == [0] * 20 and codes[20] == -2 and codes[21] == -1 and bool(s.muted[HELD]), "X: more than 20 in 10 s mutes the type once: %s" % codes)
    s2 = State(UUID.fromString("00000000-0000-0000-0000-00000000a002"), None)
    K.check(str(s2.name) == "?", "X: a state without a name")
    s2.crouch, s2.sprint, s2.air = True, False, True
    K.check(s2.start(A2, 7, 0, TESTER, -1, JLong(10000)).size() == 0 and int(s2.fired[A2]) == 1 and int(s2.srcN[A2 * 4]) == 1, "X: start counts the type + source")
    l = s2.finish(7, "Finished", False, JFloat(0.0), JLong(10120))
    K.check(str(l) == "[KeyProbe] Ability2 fired (hold 120 ms tap, crouching y, sprinting n, in air y)" and int(s2.taps[A2]) == 1 and int(s2.longest[A2]) == 120,
            "X: finish = the tap line with the crouch / air state at the PRESS: %s" % l)
    K.check(s2.finish(7, "Finished", False, JFloat(0.0), JLong(10200)) is None, "X: a chain id that is not pending ends nothing")
    s2.start(A2, 8, 1, HELMET, -1, JLong(11000))
    l = str(s2.finish(8, "Failed", False, JFloat(1.5), JLong(11800)))
    K.check(l.startswith("[KeyProbe] Ability2 fired (hold 800 ms hold") and "client charge 1.50 s - Helmet in hand [ended: Failed]" in l and int(s2.holds[A2]) == 1,
            "X: hold + charge + helmet + failed end: %s" % l)
    s2.start(A1, 9, 2, "Weapon_Sword_Iron", -1, JLong(12000))
    stale = s2.start(A1, 10, 0, TESTER, -1, JLong(18000))
    K.check(stale.size() == 1 and "no end seen within 5 s" in str(stale.get(0)) and "other item: Weapon_Sword_Iron" in str(stale.get(0)),
            "X: a chain without an end prints 'no end seen' when the next one starts after 5 s: %s" % [str(x) for x in stale])
    s2.finish(10, "Finished", False, JFloat(0.0), JLong(18100))
    s2.finish(99, "Finished", False, JFloat(0.0), JLong(18100))
    s2.start(A1, 11, 0, TESTER, -1, JLong(18200))
    hid = s2.finish(11, "Finished", False, JFloat(0.0), JLong(18210))
    K.check(hid is None and int(s2.hidden[A1]) == 2, "X: Ability1 lines within 0.3 s of the last shown one are hidden (counted: %d)" % int(s2.hidden[A1]))
    for i in range(32):
        s2.start(A1, 100 + i, 0, TESTER, -1, JLong(19000))
    K.check(s2.pend.size() == 32, "X: up to 32 pending chains are kept")
    s2.start(A1, 200, 0, TESTER, -1, JLong(19001))
    K.check(s2.pend.size() == 1 and s2.pend.containsKey(JClass("java.lang.Integer").valueOf(200)), "X: the 33rd pending chain clears the stuck ones (bounded memory)")
    s2.start(A1, 200, 0, TESTER, -1, JLong(19002))
    K.check(s2.pend.size() == 1, "X: the same chain id again replaces its entry")
    # muted type: finish answers the mute line once, then nothing
    s3 = State(UUID.fromString("00000000-0000-0000-0000-00000000a003"), "M")
    lines3 = []
    for i in range(23):
        s3.start(HELD, 300 + i, 0, TESTER, -1, JLong(30000 + 350 * i))
        r3 = s3.finish(300 + i, "Finished", False, JFloat(0.0), JLong(30000 + 350 * i))
        lines3.append(None if r3 is None else str(r3))
    K.check(sum(1 for x in lines3 if x and "fired" in x) == 20 and sum(1 for x in lines3 if x and "muted now" in x) == 1 and lines3[-1] is None
            and int(s3.fired[HELD]) == 23, "X: a type firing nonstop: 20 lines, one mute line, then silence; all 23 counted")
    # moves
    JB = JArray(JBoolean)
    s4 = State(UUID.fromString("00000000-0000-0000-0000-00000000a004"), "Mover")

    def mv(st, now, crouch=False, sprint=False, jump=False, roll=False, slide=False, mantle=False, glide=False, fly=False, ground=True):
        return [str(x) for x in st.move(JB([crouch, sprint, jump, roll, slide, mantle, glide, fly, ground]), JLong(now))]
    K.check(mv(s4, 1000) == [] and bool(s4.haveMv), "X: the first movement packet only sets the baseline")
    K.check(mv(s4, 1100, crouch=True) == [] and int(s4.edges[0]) == 1, "X: moves off = edges counted, no line")
    s4.moves = True
    mv(s4, 1200)
    K.check(mv(s4, 1700, crouch=True) == ["[KeyProbe] move: crouch ON"], "X: crouch ON line")
    K.check(mv(s4, 1800) == ["[KeyProbe] move: crouch off"], "X: crouch off line")
    out_d = mv(s4, 1950, crouch=True)
    K.check(out_d == ["[KeyProbe] move: DOUBLE-TAP crouch (250 ms between the two presses)"] and int(s4.edges[11]) == 1,
            "X: two crouch presses within 0.4 s = DOUBLE-TAP (the second crouch ON line is inside the 0.3 s cap): %s" % out_d)
    mv(s4, 2400)
    K.check(mv(s4, 3000, crouch=True) == ["[KeyProbe] move: crouch ON (+1 more hidden)"], "X: after a double-tap the next press starts a new pair; hidden count shown")
    got = mv(s4, 3500, sprint=True, jump=True, roll=True, slide=True, mantle=True, glide=True, fly=True, ground=False)
    K.check(got == ["[KeyProbe] move: crouch off", "[KeyProbe] move: sprint ON", "[KeyProbe] move: jump", "[KeyProbe] move: roll", "[KeyProbe] move: slide",
                    "[KeyProbe] move: mantle (ledge climb)", "[KeyProbe] move: glide", "[KeyProbe] move: fly ON"] and bool(s4.air),
            "X: every ON edge in one packet, air state from onGround: %s" % got)
    K.check(mv(s4, 4000, ground=True) == ["[KeyProbe] move: sprint off", "[KeyProbe] move: land"] and not bool(s4.air), "X: sprint off + land")
    K.check(s4.move(None, JLong(5000)).size() == 0 and s4.move(JB([True]), JLong(5000)).size() == 0, "X: a bad flag array is ignored")
    # report + reset
    s2.other()
    s2.start(int(IT.Pickup.ordinal()), 500, 2, "x", -1, JLong(40000))
    rep = [str(x) for x in s2.report()]
    K.check(rep[0].startswith("[KeyProbe] Report for ?") and any(x.startswith("  Ability2: 2x (1 tap, 1 hold, longest 800 ms; Key Tester 1, Helmet in hand 1") for x in rep)
            and any("Never fired: Primary, Secondary, Ability3, Use, Pick, Dodge, SwapTo" in x for x in rep)
            and any("Pickup: 1x (a type the probe items do not map)" in x for x in rep) and any("Chains from other items: 1 (not shown" in x for x in rep)
            and any(x.startswith("  Moves seen: crouch 0, sprint 0") for x in rep) and "Death and GameModeSwap" in rep[-1], "X: report: %s" % rep)
    rep3 = [str(x) for x in s3.report()]
    K.check(any("Held: 23x" in x and "[muted]" in x for x in rep3), "X: report marks a muted type")
    rep0 = [str(x) for x in State(UUID.randomUUID(), "E").report()]
    K.check(any("Nothing fired yet" in x for x in rep0) and any("Never fired: Primary" in x for x in rep0), "X: an empty report")
    s3.reset()
    K.check(int(s3.fired[HELD]) == 0 and not bool(s3.muted[HELD]) and s3.pend.size() == 0 and int(s3.chains) == 0, "X: reset zeroes + unmutes")
    s4.all = True
    rep4 = [str(x) for x in s4.report()]
    K.check(any("(shown: all on)" in x for x in rep4) and any("crouch 4" in x and "double-tap crouch 1" in x and "land 1" in x for x in rep4), "X: report moves + all on: %s" % rep4)

    # ---- world stand-ins: PlayerRef, a FakeWorld in Universe.worldsByUuid, a MapStore with the hand / inventory components
    PRc = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    REF = JClass("com.hypixel.hytale.component.Ref")
    MS, FH, FW = JClass(FAKE_PKG + ".MapStore"), JClass(FAKE_PKG + ".FakeHotbar"), JClass(FAKE_PKG + ".FakeWorld")
    IHM, IS = JClass("java.util.IdentityHashMap"), JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    CT, EM = JClass("com.hypixel.hytale.component.ComponentType"), JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    INVC = JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent")
    HOT, STO, BKP = (JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar"), JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Storage"),
                     JClass("com.hypixel.hytale.server.core.inventory.InventoryComponent$Backpack"))
    MOD = JClass("java.lang.reflect.Modifier")
    em = U.allocateInstance(EM.class_)
    nidx = [0]
    for f in EM.class_.getDeclaredFields():
        if not MOD.isStatic(f.getModifiers()) and f.getType() == CT.class_:
            v = U.allocateInstance(CT.class_)
            nidx[0] += 1
            jfield(CT, "index").set(v, JInt(nidx[0]))
            f.setAccessible(True)
            f.set(em, v)
    jfield(EM, "instance").set(None, em)
    tt = {"storage": STO.getComponentType(), "hotbar": HOT.getComponentType(), "backpack": BKP.getComponentType()}
    K.check(all(v is not None for v in tt.values()), "X: the inventory component types resolve through the allocated EntityModule: %s" % tt)
    ARCH = JClass("com.hypixel.hytale.component.Archetype")
    arch = U.allocateInstance(ARCH.class_)
    arr = [None] * (max(int(t.getIndex()) for t in tt.values()) + 1)
    for t_ in tt.values():
        arr[int(t_.getIndex())] = t_
    jfield(ARCH, "componentTypes").set(arch, JArray(CT)(arr))
    jfield(INVC, "STORAGE_HOTBAR_BACKPACK").set(None, JArray(CT)([tt["storage"], tt["hotbar"], tt["backpack"]]))
    comps = IHM()
    st = U.allocateInstance(MS.class_)
    st.comps, st.arch = comps, arch
    world = U.allocateInstance(FW.class_)
    wuid = UUID.fromString("00000000-0000-0000-0000-0000000000w1".replace("w", "f"))
    E["wbu"].put(wuid, world)
    nref = [0]

    def mkplayer(name, n, hand=None, storage=36, hot=9, world_uuid=wuid, with_ref=True):
        pr_ = U.allocateInstance(PRc.class_)
        jfield(PRc, "uuid").set(pr_, UUID.fromString("00000000-0000-0000-0000-%012x" % (0xc000 + n)))
        jfield(PRc, "username").set(pr_, name)
        jfield(PRc, "worldUuid").set(pr_, world_uuid)
        r_ = None
        if with_ref:
            nref[0] += 1
            r_ = REF(st, JInt(nref[0]))
            comps.put(r_, IHM())
            hb = U.allocateInstance(FH.class_)
            jfield(INVC, "inventory").set(hb, HOT(JShort(hot)).getInventory())
            hb.item = None if hand is None else IS(hand, 1)
            comps.get(r_).put(tt["hotbar"], hb)
            comps.get(r_).put(tt["storage"], STO(JShort(storage)))
            comps.get(r_).put(tt["backpack"], BKP(JShort(0)))
            jfield(PRc, "entity").set(pr_, r_)
        return {"pr": pr_, "ref": r_, "uuid": pr_.getUuid()}
    PA = mkplayer("Skyy", 1, hand=TESTER)
    PB = mkplayer("Other", 2, hand="Weapon_Sword_Iron")
    PN = mkplayer("Nobody", 3, with_ref=False)
    PW = mkplayer("NoWorld", 4, hand=TESTER, world_uuid=None)
    K.check(str(Say.handId(PA["pr"])) == TESTER and str(Say.handId(PB["pr"])) == "Weapon_Sword_Iron" and Say.handId(PN["pr"]) is None
            and Say.handId(None) is None, "X: handId reads the item in hand through the engine's InventoryComponent.getItemInHand (tester / other / no ref)")

    def run_tasks():
        n_ = 0
        ts = world.tasks
        while ts is not None and ts.size() > 0:
            batch = [ts.get(i) for i in range(int(ts.size()))]
            ts.clear()
            for t_ in batch:
                t_.run()
                n_ += 1
        return n_
    # ---- the REAL engine filter: KpCore.start() registers through PacketAdapters.registerInbound(PlayerPacketWatcher)
    PAD = JClass("com.hypixel.hytale.server.core.io.adapter.PacketAdapters")
    inb = jfield(PAD, "inboundHandlers").get(None)
    n_in0 = inb.size()
    Core.start()
    Core.start()
    f1 = Core.FILTER
    K.check(f1 is not None and inb.size() == n_in0 + 1 and inb.contains(f1), "X: start() twice registers ONE inbound filter (start stops the old one first)")
    GPH = JClass("com.hypixel.hytale.server.core.io.handlers.game.GamePacketHandler")

    def handler(p):
        h_ = U.allocateInstance(GPH.class_)
        jfield(GPH, "playerRef").set(h_, p["pr"])
        return h_
    HA, HB, HW = handler(PA), handler(PB), handler(PW)
    SICS = JClass("com.hypixel.hytale.protocol.packets.interaction.SyncInteractionChains")
    SIC = JClass("com.hypixel.hytale.protocol.packets.interaction.SyncInteractionChain")
    ISD = JClass("com.hypixel.hytale.protocol.InteractionSyncData")
    ISTA = JClass("com.hypixel.hytale.protocol.InteractionState")
    CMV = JClass("com.hypixel.hytale.protocol.packets.player.ClientMovement")
    MVS = JClass("com.hypixel.hytale.protocol.MovementStates")
    FCI = JClass("com.hypixel.hytale.protocol.ForkedChainId")
    clock = [100000]

    def tick(ms):
        clock[0] += ms
        Core.CLOCK = JLong(clock[0])

    def chain(typ, cid, initial, state, hand=TESTER, slot=-1, charge=None, forked=False):
        u = SIC()
        u.interactionType = None if typ is None else IT.valueOf(typ)
        u.chainId = cid
        u.initial = initial
        u.state = None if state is None else ISTA.valueOf(state)
        u.itemInHandId = hand
        u.equipSlot = slot
        if charge is not None:
            d_ = ISD()
            d_.chargeValue = JFloat(charge)
            u.interactionData = JArray(ISD)([None, d_])
        if forked:
            u.forkedId = FCI()
        return u

    def send(h_, *updates):
        p_ = SICS()
        p_.updates = JArray(SIC)(list(updates))
        r_ = f1.test(h_, p_)
        return bool(r_)

    def movep(h_, **kw):
        m_ = MVS()
        m_.onGround = True
        for k_, v_ in kw.items():
            setattr(m_, k_, v_)
        c_ = CMV()
        c_.movementStates = m_
        return bool(f1.test(h_, c_))
    tick(0)
    K.check(not send(HA, chain("Ability1", 1, True, "NotFinished")) and run_tasks() == 0 and said() == [] and Core.STATES.isEmpty(),
            "X: nobody watched = the filter returns false (never blocks) and nothing happens")
    # watch PA through the command path
    Cmds.run(PA["ref"], st, PA["pr"], "on", None)
    K.check(said() == ["[KeyProbe] Watching you (probe items only). /keyprobe off stops."] and Core.state(PA["uuid"]) is not None, "X: /keyprobe on")
    SA = Core.state(PA["uuid"])
    K.check(not movep(HA) and not movep(HA, crouching=True, sprinting=True) and run_tasks() == 0, "X: movement with moves off: no lines, the filter never blocks")
    tick(1000)
    K.check(not send(HA, chain("Ability1", 2, True, "NotFinished")) and run_tasks() == 0 and int(SA.fired[A1]) == 1, "X: an Ability1 press is counted at once")
    tick(450)
    send(HA, chain("Ability1", 2, False, "Finished", charge=0.4))
    K.check(run_tasks() == 1 and said() == ["[KeyProbe] Ability1 fired (hold 450 ms hold, crouching y, sprinting y, in air n) client charge 0.40 s"],
            "X: the release packet -> the line on the world thread with the crouch / sprint state at the press + the client charge")
    tick(1000)
    send(HA, chain("Primary", 3, True, "Finished"))
    K.check(run_tasks() == 1 and said() == ["[KeyProbe] Primary fired (hold 0 ms tap, crouching y, sprinting y, in air n)"], "X: a chain that starts + ends in one update")
    tick(1000)
    send(HA, chain("Ability3", 4, True, "NotFinished", forked=True), None, chain(None, 5, True, "NotFinished"))
    K.check(run_tasks() == 0 and int(SA.chains) == 2, "X: forked / empty / typeless updates are skipped")
    tick(1000)
    send(HA, chain("Primary", 6, True, "NotFinished", hand="Weapon_Sword_Iron"))
    tick(100)
    send(HA, chain("Primary", 6, False, "Finished", hand="Weapon_Sword_Iron"))
    K.check(run_tasks() == 0 and int(SA.others) == 1, "X: another item's chain is counted as 'other' and not shown (all off)")
    Cmds.run(PA["ref"], st, PA["pr"], "all", "on")
    said()
    tick(1000)
    send(HA, chain("Primary", 7, True, "NotFinished", hand=None))
    tick(50)
    send(HA, chain("Primary", 7, False, "ItemChanged", hand=None))
    K.check(run_tasks() == 1 and said() == ["[KeyProbe] Primary fired (hold 50 ms tap, crouching y, sprinting y, in air n) - other item: empty hand [ended: ItemChanged]"],
            "X: all on: a bare-hand chain reports, with its end state")
    Cmds.run(PA["ref"], st, PA["pr"], "all", "off")
    said()
    tick(1000)
    send(HA, chain("Equipped", 8, True, "Finished", hand=TESTER, slot=0))
    K.check(run_tasks() == 1 and said() == ["[KeyProbe] Equipped fired (hold 0 ms tap, crouching y, sprinting y, in air n) - WORN armor, slot 0"],
            "X: an Equipped chain of a worn piece reports as worn armor (even with the tester in hand)")
    send(HA, chain("Use", 9, True, "Finished", hand=HELMET))
    K.check(run_tasks() == 1 and said()[0].endswith("- Helmet in hand"), "X: the helmet held in hand")
    # movement lines: only while a probe item is in hand
    Cmds.run(PA["ref"], st, PA["pr"], "moves", "on")
    said()
    tick(1000)
    movep(HA)
    tick(100)
    movep(HA, jumping=True, onGround=False)
    _n = run_tasks()
    _s = said()
    K.check(_n == 2 and _s == ["[KeyProbe] move: crouch off", "[KeyProbe] move: sprint off", "[KeyProbe] move: jump"], "X: movement lines while holding the tester: %s %s" % (_n, _s))
    comps.get(PA["ref"]).get(tt["hotbar"]).item = IS(HELMET, 1)
    tick(500)
    movep(HA, crouching=True)
    K.check(run_tasks() == 1 and said() == ["[KeyProbe] move: crouch ON", "[KeyProbe] move: land"], "X: ... and while holding the helmet")
    comps.get(PA["ref"]).get(tt["hotbar"]).item = IS("Weapon_Sword_Iron", 1) if ITMc.getAssetMap().getAsset("Weapon_Sword_Iron") is not None else None
    tick(500)
    movep(HA)
    K.check(run_tasks() == 1 and said() == [], "X: no movement line with another item in hand (the world-thread hand check drops it)")
    jfield(PRc, "entity").set(PA["pr"], None)
    tick(500)
    movep(HA, crouching=True)
    K.check(run_tasks() == 1 and said() == [], "X: no movement line when the player has no entity (relog / world switch)")
    jfield(PRc, "entity").set(PA["pr"], PA["ref"])
    comps.get(PA["ref"]).get(tt["hotbar"]).item = IS(TESTER, 1)
    # no world: lines go to the log only
    Cmds.run(PW["ref"], st, PW["pr"], "on", None)
    said()
    und0 = int(Core.UNDELIVERED.get())
    send(HW, chain("Dodge", 1, True, "Finished"))
    K.check(int(Core.UNDELIVERED.get()) == und0 + 1 and run_tasks() == 0 and said() == [], "X: no world to deliver to = the line goes to the log only")
    # errors: a broken state entry is caught, logged at most 3 times
    Core.STATES.put(PB["uuid"], JString("not a state"))
    e0 = int(Core.ERRORS.get())
    for i in range(5):
        send(HB, chain("Primary", 50 + i, True, "Finished"))
    n_warn = len([m for lv, m in records() if "packet read failed" in m])
    K.check(int(Core.ERRORS.get()) == e0 + 5 and n_warn == 3, "X: packet errors are caught (filter never throws) and logged 3 times at most (%d)" % n_warn)
    Core.STATES.remove(PB["uuid"])
    K.check(not bool(f1.test(HA, JClass("com.hypixel.hytale.protocol.packets.interaction.CancelInteractionChain")()))
            if _has("com.hypixel.hytale.protocol.packets.interaction.CancelInteractionChain") else True, "X: other packet types pass untouched")
    send(HA, *[])
    p0 = SICS()
    K.check(not bool(f1.test(HA, p0)) and not bool(f1.test(HA, CMV())), "X: a packet with no updates / no movement states is ignored")
    Watch().accept(JObject(JString("x")), JObject(JString("y")))
    Watch().accept(None, None)
    Core.packet(None, None)
    K.check(True, "X: KpWatch bridge accept(Object, Object) ignores non-player arguments")
    # KpSay direct: an empty list / an exception in delivery
    Say(PA["pr"], None, False).run()
    Say(PA["pr"], JClass("java.util.ArrayList")(), True).run()
    bad_l = JClass("java.util.ArrayList")()
    bad_l.add(JInt(5))
    w0 = len([m for lv, m in records() if "chat delivery failed" in m])
    Say(PA["pr"], bad_l, False).run()
    K.check(len([m for lv, m in records() if "chat delivery failed" in m]) == w0 + 1, "X: KpSay logs a delivery failure instead of throwing")
    # ---- commands (KpCmds) - every word
    Cmds.run(PA["ref"], st, PA["pr"], "report", None)
    rep = said()
    K.check(rep[0].startswith("[KeyProbe] Report for Skyy") and any(x.startswith("  Ability1: 1x (0 tap, 1 hold, longest 450 ms") for x in rep)
            and any("Chains from other items: 2 (not shown" in x for x in rep), "X: /keyprobe report: %s" % rep)
    Cmds.run(PA["ref"], st, PA["pr"], "binds", None)
    b_ = said()
    K.check(len(b_) == len(Logic.BINDS) and b_[0].startswith("[KeyProbe] Binds") and b_[1].startswith("  "), "X: /keyprobe binds")
    Cmds.run(PA["ref"], st, PA["pr"], "moves", "maybe")
    Cmds.run(PA["ref"], st, PA["pr"], "moves", None)
    K.check(said() == ["[KeyProbe] Usage: /keyprobe moves on|off"] * 2, "X: moves with a bad / no value -> usage")
    Cmds.run(PA["ref"], st, PA["pr"], "MOVES", " Off ")
    K.check(said()[0].startswith("[KeyProbe] Movement lines off") and not bool(SA.moves), "X: moves off (case / spaces)")
    Cmds.run(PA["ref"], st, PA["pr"], "reset", None)
    K.check(said() == ["[KeyProbe] Counts zeroed, every type unmuted."] and int(SA.chains) == 0, "X: /keyprobe reset")
    Cmds.run(PA["ref"], st, PA["pr"], "nonsense", None)
    Cmds.run(PA["ref"], st, PA["pr"], None, None)
    K.check(len(said()) == 10, "X: an unknown / empty word -> the 5 help lines (0.2: + /keyprobe sprint)")
    Cmds.run(PA["ref"], st, PA["pr"], "off", None)
    K.check(said() == ["[KeyProbe] Stopped watching you; your counts are gone.", "[KeyProbe] Before this probe is removed from the server: take the Key Tester Helmet off and trash both probe items (Key Tester + Key Tester Helmet)."] and Core.state(PA["uuid"]) is None, "X: /keyprobe off forgets you + reminds to trash both probe items (fix keyprobe01fix C1-1)")
    Cmds.run(PA["ref"], st, PA["pr"], "on", None)
    Cmds.run(PA["ref"], st, PA["pr"], "stop", None)
    K.check(said()[-2:] == ["[KeyProbe] Stopped watching you; your counts are gone.", "[KeyProbe] Before this probe is removed from the server: take the Key Tester Helmet off and trash both probe items (Key Tester + Key Tester Helmet)."] and Core.state(PA["uuid"]) is None, "X: /keyprobe stop = off (with the trash reminder)")
    Cmds.report(PA["pr"])
    K.check(said() == ["[KeyProbe] Not watching you - /keyprobe on (or /keyprobe give) first."], "X: report when not watched")
    # give: storage first, nothing dropped
    Cmds.run(PA["ref"], st, PA["pr"], "give", None)
    g_ = said()
    stor = comps.get(PA["ref"]).get(tt["storage"]).getInventory()
    ids_ = [str(stor.getItemStack(JShort(i)).getItemId()) for i in range(int(stor.getCapacity())) if stor.getItemStack(JShort(i)) is not None]
    K.check(g_ == ["[KeyProbe] Given: Key Tester + Key Tester Helmet. Watching you now: hold the Key Tester and press every key, then /keyprobe report."]
            and ids_ == [TESTER, HELMET] and Core.state(PA["uuid"]) is not None, "X: /keyprobe give puts both items into STORAGE first + watches: %s %s" % (g_, ids_))
    PF = mkplayer("Full", 5, hand=None, storage=0, hot=0)
    Cmds.run(PF["ref"], st, PF["pr"], "give", None)
    K.check(said() == ["[KeyProbe] Given: nothing. No room for SkyyKeyProbe_Tester, SkyyKeyProbe_Helmet - nothing was dropped. Watching you now: hold the Key Tester and press every key, then /keyprobe report."],
            "X: give with no room: nothing dropped, said so")
    PX = mkplayer("NoInv", 6, with_ref=False)
    r_x = REF(st, JInt(999))
    comps.put(r_x, IHM())
    st_noarch = U.allocateInstance(MS.class_)
    st_noarch.comps = comps
    Cmds.give(PX["pr"], st_noarch, r_x)
    K.check(said() == ["[KeyProbe] Could not open your inventory - nothing given (watching you anyway)."], "X: give without an inventory")
    Core.FILTER = None
    Cmds.report(PA["pr"])
    K.check(said()[-1].startswith("[KeyProbe] WARNING: the packet watcher is not registered"), "X: report warns when the watcher is missing")
    Core.FILTER = f1
    # ---- the three commands' execute() with a real CommandContext
    CTXc = JClass("com.hypixel.hytale.server.core.command.system.CommandContext")
    WLD, STc = JClass("com.hypixel.hytale.server.core.universe.world.World"), JClass("com.hypixel.hytale.component.Store")
    cmd, cmd1, cmd2 = JClass(PKG + "KProbeCmd")(), JClass(PKG + "KProbeArgCmd")(), JClass(PKG + "KProbeArg2Cmd")()

    def execute(c, ctx):
        m_ = c.getClass().getDeclaredMethod("execute", CTXc.class_, STc.class_, REF.class_, PRc.class_, WLD.class_)
        m_.setAccessible(True)
        m_.invoke(c, JArray(JObject)([ctx, st, PA["ref"], PA["pr"], None]))
    execute(cmd, None)
    _h = said()
    K.check(len(_h) == 5 and "/keyprobe sprint - (any player)" in _h[-1], "X: /keyprobe -> the help lines: %s" % _h)
    ctx = U.allocateInstance(CTXc.class_)
    av = JClass("java.util.HashMap")()
    av.put(cmd1.whatArg, "binds")
    jfield(CTXc, "argValues").set(ctx, av)
    execute(cmd1, ctx)
    K.check(len(said()) == len(Logic.BINDS), "X: /keyprobe binds through KProbeArgCmd.execute + CommandContext.get")
    av2 = JClass("java.util.HashMap")()
    av2.put(cmd2.whatArg, "moves")
    av2.put(cmd2.valArg, "on")
    ctx2 = U.allocateInstance(CTXc.class_)
    jfield(CTXc, "argValues").set(ctx2, av2)
    execute(cmd2, ctx2)
    K.check(said()[0].startswith("[KeyProbe] Movement lines ON") and bool(Core.state(PA["uuid"]).moves), "X: /keyprobe moves on through KProbeArg2Cmd.execute")
    execute(cmd1, None)
    execute(cmd2, None)
    K.check(said() == ["[KeyProbe] Usage: /keyprobe <give, on, off, report, binds, reset>", "[KeyProbe] Usage: /keyprobe moves on|off | all on|off"],
            "X: both variants without a context -> usage")
    # ================= S. the 0.2 sprint probe - every new code path executed
    sprint_part(K, E, locals())
    # sprint left ON with the real daemon timer running, so the shutdown below must stop both
    Core.AUTO_TIMER = True
    Cmds.sprint(PA["pr"])
    said()
    K.check(Core.TIMER is not None and Core.SPRINT.containsKey(PA["uuid"]), "S: sprint on with AUTO_TIMER = a real daemon Timer")
    # ---- plugin shutdown: deregisters the filter + clears the state
    PLc = JClass(PKG + "SkyyKeyProbePlugin")
    plg = U.allocateInstance(PLc.class_)
    try:
        sd = PLc.class_.getDeclaredMethod("shutdown")
        sd.setAccessible(True)
        sd.invoke(plg, JArray(JObject)([]))
    except Exception as e:
        K.notes.append("plugin shutdown: super.shutdown() on an allocated plugin: %s" % str(e)[:120])
    K.check(Core.FILTER is None and not inb.contains(f1) and inb.size() == n_in0 and Core.STATES.isEmpty(),
            "X: plugin shutdown deregisters the inbound filter and forgets every watched player")
    K.check(Core.SPRINT.isEmpty() and Core.TIMER is None, "S: plugin shutdown cancels the sprint Timer and forgets every sprint-probed player")
    world.tasks = None
    Core.stop()
    K.check(Core.FILTER is None, "X: stop() twice is harmless")
    Log.SINK = None
    Core.CLOCK = JLong(0)
    K.check(int(Core.now()) > 1000000000000, "X: CLOCK 0 = real time")
    print("X. every probe path executed")
    K.save()


def _has(cn):
    try:
        from jpype import JClass
        JClass(cn)
        return True
    except Exception:
        return False


def run_perm(out):
    """child P: permissions with the engine's own AbstractCommand code"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("KProbeCmd", "KProbeArgCmd", "KProbeArg2Cmd"):
        try:
            c = JClass(PKG + cn)()
        except Exception as e:
            K.check(False, "P. construct %s: %s" % (cn, e))
            continue
        perm = c.getPermission()
        groups = fld.get(c)
        K.check(perm is not None and NODE in str(perm.getId() if hasattr(perm, "getId") else perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty (%s)" % (cn, groups))
        if cn == "KProbeCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak, "P. getPermissionGroupsRecursive gives %s to no group (leak: %s)" % (NODE, leak))
            K.check("kprobe" in [str(a) for a in c.getAliases()] and str(c.getName()) == "keyprobe", "P. /keyprobe + alias /kprobe")
            subs = c.getSubCommands()
            K.check(subs is not None and subs.containsKey("sprint") and str(subs.get("sprint").getClass().getSimpleName()) == "KProbeSprintCmd",
                    "P. /keyprobe sprint is a SUB-command (dispatched before the parent's permission check): %s" % subs)
            sprec = [str(k) for k in rec.keySet()]
            K.check(not leak, "P. the admin node stays in no group with the any-player sub-command added (%s)" % sprec)
    sc = JClass(PKG + "KProbeSprintCmd")()
    g = fld.get(sc)
    perm = sc.getPermission()
    K.check(g is not None and [str(x) for x in g] == ["hytale:Adventurer"], "P. /keyprobe sprint: permission group hytale:Adventurer (every player): %s" % g)
    K.check(perm is None or NODE not in str(perm), "P. /keyprobe sprint does NOT require the admin node (%s)" % perm)
    K.check(str(sc.getName()) == "sprint", "P. the sub-command is named sprint")
    K.save()


def bytecode_calls(cp, cls, meth):
    from jpype import JClass
    cc = cp.get(cls)
    mi = [m for m in cc.getClassFile2().getMethods() if str(m.getName()) == meth][0]
    cpool, it = mi.getConstPool(), mi.getCodeAttribute().iterator()
    calls = []
    while it.hasNext():
        p = it.next()
        op = it.byteAt(p)
        if op in (0xb6, 0xb7, 0xb8, 0xb9):
            i = it.u16bitAt(p + 1)
            if cpool.getTag(i) == JClass("javassist.bytecode.ConstPool").CONST_InterfaceMethodref:
                calls.append(str(cpool.getInterfaceMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getInterfaceMethodrefName(i)))
            else:
                calls.append(str(cpool.getMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getMethodrefName(i)))
        elif op == 0xbb:
            calls.append("new " + str(cpool.getClassInfo(it.u16bitAt(p + 1))).rsplit(".", 1)[-1])
        elif op in (0xb2, 0xb3):
            calls.append(("get " if op == 0xb2 else "put ") + str(cpool.getFieldrefClassName(it.u16bitAt(p + 1))).rsplit(".", 1)[-1] + "."
                         + str(cpool.getFieldrefName(it.u16bitAt(p + 1))))
    return calls


def run_bytecode(out):
    """child B: setup()'s calls in order + the engine facts the probe stands on (HytaleServer.jar bytecode)"""
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    calls = bytecode_calls(cp, PKG + "SkyyKeyProbePlugin", "setup")
    want = ["put KpLog.LOG", "PluginBase.getCommandRegistry", "new KProbeCmd", "CommandRegistry.registerCommand", "KpCore.start"]
    pos, ok = 0, True
    for w in want:
        if w not in calls[pos:]:
            ok = False
            break
        pos = calls.index(w, pos) + 1
    K.check(ok and not any("registerSystem" in c for c in calls), "B: setup() = LOG, registerCommand(new KProbeCmd), KpCore.start - no ECS system: %s" % calls)
    K.check("KpCore.stop" in bytecode_calls(cp, PKG + "SkyyKeyProbePlugin", "shutdown"), "B: shutdown() calls KpCore.stop")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def code(cls, meth, sig=None):
        for mm in cp.get(cls).getDeclaredMethods():
            if str(mm.getName()) == meth and (sig is None or sig in str(mm.getSignature())):
                mi = mm.getMethodInfo()
                it = mi.getCodeAttribute().iterator()
                cpool, o = mi.getConstPool(), []
                while it.hasNext():
                    p = it.next()
                    o.append(str(IP.instructionString(it, p, cpool)))
                return "\n".join(o)
        return ""

    def in_order(txt, needles):
        i = 0
        for nd in needles:
            j = txt.find(nd, i)
            if j < 0:
                return nd
            i = j + len(nd)
        return None
    PADc = "com.hypixel.hytale.server.core.io.adapter.PacketAdapters"
    facts = [
        ("the PlayerPacketWatcher wrapper hands the GamePacketHandler's PlayerRef to accept() and returns false (never blocks)",
         PADc, "lambda$registerInbound$2", None, ["GamePacketHandler", "getPlayerRef", "PlayerPacketWatcher.accept", "iconst_0", "ireturn"]),
        ("inbound filters run on the network thread BEFORE the packet handler",
         "com.hypixel.hytale.server.core.io.netty.PlayerChannelHandler", "channelRead", None, ["PacketAdapters.__handleInbound", "PacketHandler.handle"]),
        ("syncStart resolves the item by equipSlot then asks the context for the type's root id",
         "com.hypixel.hytale.server.core.entity.InteractionManager", "syncStart", None,
         ["SyncInteractionChain.equipSlot", "InteractionContext.forInteraction", "InteractionContext.getRootInteractionId", "Missing root interaction"]),
        ("getRootInteractionId = the entity's Interactions override, else the item's Interactions map",
         "com.hypixel.hytale.server.core.entity.InteractionContext", "getRootInteractionId", None,
         ["Interactions.getInteractionId", "originalItemType", "Item.getInteractions", "Map.get"]),
        ("Equipped chains use the ARMOR container slot", "com.hypixel.hytale.server.core.entity.InteractionContext", "forInteraction",
         "ILcom/hypixel/hytale/component/ComponentAccessor", ["InventoryComponent$Armor.getComponentType", "tableswitch", "InventoryComponent$Armor.getInventory"]),
        ("SendMessage Target Owner sends to the owning player's PlayerRef",
         "com.hypixel.hytale.server.core.modules.interaction.interaction.config.none.simple.SendMessageInteraction", "firstRun", None,
         ["getOwningEntity", "PlayerRef.getComponentType", "buildMessage", "PlayerRef.sendMessage"]),
        ("Death chains are server-run", "com.hypixel.hytale.server.core.modules.entity.damage.DeathSystems$RunDeathInteractions", "onComponentAdded", None,
         ["InteractionType.Death"]),
        ("0.2: acceptCall0 dispatches sub-commands BEFORE its own permission check (an admin parent does not block /keyprobe sprint)",
         "com.hypixel.hytale.server.core.command.system.AbstractCommand", "acceptCall0", None,
         ["checkForExecutingSubcommands", "ObjectBooleanPair.rightBoolean", "AbstractCommand.hasPermission"]),
        ("0.2: checkForExecutingSubcommands looks the first token up in the sub-commands and runs that one's acceptCall0",
         "com.hypixel.hytale.server.core.command.system.AbstractCommand", "checkForExecutingSubcommands", None,
         ["AbstractCommand.subCommands", "AbstractCommand.getSubCommand", "AbstractCommand.acceptCall0"]),
        ("0.2: hasPermission - a command with its own permission groups does not ask its parent",
         "com.hypixel.hytale.server.core.command.system.AbstractCommand", "hasPermission", None,
         ["AbstractCommand.permission", "CommandSender.hasPermission", "AbstractCommand.parentCommand", "AbstractCommand.permissionGroups",
          "AbstractCommand.parentCommand", "AbstractCommand.hasPermission"]),
    ]
    for what, cls, meth, sig, needles in facts:
        miss = in_order(code(cls, meth, sig), needles)
        K.check(miss is None, "B: engine fact - %s (missing %r)" % (what, miss))
    K.save()


def run_live(step, out):
    """child D: one 'server start' on the scratch copy of the live player files"""
    from jpype import JClass, JArray, JBoolean, JLong, JInt, JFloat
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    home = os.path.join(SCRATCH, "live")

    def snap():
        d_ = {}
        for r_, _, fs in os.walk(home):
            for f_ in fs:
                p_ = os.path.join(r_, f_)
                d_[os.path.relpath(p_, home)] = hashlib.sha256(open(p_, "rb").read()).hexdigest()
        return d_
    before = snap()
    Core, State, Log = JClass(PKG + "KpCore"), JClass(PKG + "KpState"), JClass(PKG + "KpLog")
    Spr, MVS, CMV = JClass(PKG + "KpSprint"), JClass("com.hypixel.hytale.protocol.MovementStates"), JClass("com.hypixel.hytale.protocol.packets.player.ClientMovement")
    from jpype import JDouble
    IT = JClass("com.hypixel.hytale.protocol.InteractionType")
    K.check(Core.STATES.isEmpty() and Core.FILTER is None and int(Core.CLOCK) == 0 and Core.SPRINT.isEmpty() and Core.TIMER is None,
            "D %s: the probe starts with no state (nothing carried over, no sprint probe, no timer)" % step)
    Core.start()
    K.check(Core.FILTER is not None, "D %s: the watcher registers" % step)
    SINK = JClass("java.util.ArrayList")()
    Log.SINK = SINK
    UUID = JClass("java.util.UUID")
    used = 0
    for f in sorted(before):
        if not f.endswith(".json"):
            continue
        try:
            d = json.load(open(os.path.join(home, f), encoding="utf-8"))
        except Exception as e:
            K.check(False, "D %s %s: unreadable copy: %s" % (step, f, e))
            continue
        uid = os.path.basename(f)[:-5]
        try:
            u = UUID.fromString(uid)
        except Exception:
            continue
        name = (d.get("Components", {}).get("Nameplate", {}) or {}).get("Text") or d.get("Components", {}).get("DisplayName", {}).get("DisplayName", {}).get("RawText") or uid[:8]
        s = State(u, str(name))
        Core.STATES.put(u, s)
        s.move(JArray(JBoolean)([False] * 8 + [True]), JLong(1000))
        s.start(int(IT.Ability2.ordinal()), 1, 0, TESTER, -1, JLong(2000))
        line = s.finish(1, "Finished", False, JFloat(0.0), JLong(2100))
        rep = [str(x) for x in s.report()]
        K.check(str(line).startswith("[KeyProbe] Ability2 fired (hold 100 ms tap") and rep[0].startswith("[KeyProbe] Report for "),
                "D %s %s: a watched player with this live uuid / name runs the key + report paths" % (step, f))
        # 0.2: the sprint paths for this live player (no PlayerRef needed for the pure state)
        sp = Spr(None, u, str(name))
        Core.SPRINT.put(u, sp)
        m0, m1 = MVS(), MVS()
        m1.sprinting = True
        c0, c1 = CMV(), CMV()
        c0.movementStates, c1.movementStates = m0, m1
        sp.movement(c0)
        l1 = sp.movement(c1)
        b0 = sp.sample(m0, m0, JDouble(0), JDouble(0), True, JFloat(0), True, None, JFloat(10), True, None, None, 0)
        l2 = sp.sample(m1, m0, JDouble(0), JDouble(0), True, JFloat(0), True, None, JFloat(9), True, None, None, 0)
        sm = [str(x) for x in sp.summary()]
        K.check(str(l1) == "[KeyProbe] sprint client: sprinting false->true" and str(b0).startswith("[KeyProbe] sprint: baseline taken")
                and str(l2) == "[KeyProbe] sprint server: sprinting false->true, stamina DRAINS at 9.00" and sm[0].startswith("[KeyProbe] Sprint probe OFF for "),
                "D %s %s: the sprint probe paths run for this live player: %s %s" % (step, f, l1, l2))
        used += 1
    Core.stop()
    K.check(Core.STATES.isEmpty() and Core.FILTER is None and Core.SPRINT.isEmpty(), "D %s: stop forgets everyone (key + sprint probes)" % step)
    after = snap()
    K.check(before == after, "D %s: the probe wrote NOTHING - every scratch file byte-identical, no new file (%d files)" % (step, len(after)))
    K.notes.append("D %s: %d live player copies used" % (step, used))
    K.save(files=len(after), used=used)


def run_audit(out):
    """child AA: the engine-access audit (the SkyyMonkProbe harness part AA)"""
    from jpype import JClass
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=False)
    Cls, loader = JClass("java.lang.Class"), JClass("java.lang.ClassLoader").getSystemClassLoader()
    CP = JClass("javassist.ClassPool")(False)
    CP.appendSystemPath()
    for p_ in (B.SERVER_JAR, JAR, FAKE_DIR):
        CP.appendClassPath(p_)
    LIN, MTc, CPool, JMod_ = (JClass(FAKE_PKG + ".LookupIn"), JClass("java.lang.invoke.MethodType"), JClass("javassist.bytecode.ConstPool"),
                              JClass("java.lang.reflect.Modifier"))
    XOPS = {0xb2: "getstatic", 0xb3: "putstatic", 0xb4: "getfield", 0xb5: "putfield", 0xb6: "invokevirtual", 0xb7: "invokespecial",
            0xb8: "invokestatic", 0xb9: "invokeinterface", 0xba: "invokedynamic", 0xbb: "new", 0xbd: "anewarray", 0xc0: "checkcast",
            0xc1: "instanceof", 0xc5: "multianewarray", 0x12: "ldc", 0x13: "ldc_w"}

    def jvm_class(name):
        return Cls.forName(name.replace("/", "."), False, loader)
    cs_ = set()

    def lookup_audit(cn):
        D = jvm_class(cn)
        lk = LIN.lookupIn(D)
        cc = CP.get(cn)
        sup = str(cc.getSuperclass().getName()) if cc.getSuperclass() is not None else None
        refused, n = [], 0
        for mi in cc.getClassFile2().getMethods():
            ca = mi.getCodeAttribute()
            if ca is None:
                continue
            cp, it_ = mi.getConstPool(), ca.iterator()
            in_ctor = str(mi.getName()) == "<init>"
            while it_.hasNext():
                p_ = it_.next()
                op = it_.byteAt(p_)
                if op not in XOPS:
                    continue
                where = "%s.%s @%d %s" % (cn.rsplit(".", 1)[-1], mi.getName(), p_, XOPS[op])
                if op == 0xba:
                    refused.append(where + ": invokedynamic")
                    continue
                idx = it_.byteAt(p_ + 1) if op == 0x12 else it_.u16bitAt(p_ + 1)
                tag = cp.getTag(idx)
                if op in (0x12, 0x13) and tag != CPool.CONST_Class:
                    continue
                n += 1
                C_ = None
                try:
                    if op in (0x12, 0x13, 0xbb, 0xbd, 0xc0, 0xc1, 0xc5):
                        lk.accessClass(jvm_class(str(cp.getClassInfo(idx))))
                    elif op in (0xb2, 0xb3, 0xb4, 0xb5):
                        C_ = jvm_class(str(cp.getFieldrefClassName(idx)))
                        ft = MTc.fromMethodDescriptorString("(" + str(cp.getFieldrefType(idx)) + ")V", loader).parameterType(0)
                        if op in (0xb2, 0xb3):
                            lk.findStaticGetter(C_, str(cp.getFieldrefName(idx)), ft)
                        else:
                            lk.findGetter(C_, str(cp.getFieldrefName(idx)), ft)
                    else:
                        if tag == CPool.CONST_InterfaceMethodref:
                            cname, name, desc = (str(cp.getInterfaceMethodrefClassName(idx)), str(cp.getInterfaceMethodrefName(idx)),
                                                 str(cp.getInterfaceMethodrefType(idx)))
                        else:
                            cname, name, desc = (str(cp.getMethodrefClassName(idx)), str(cp.getMethodrefName(idx)), str(cp.getMethodrefType(idx)))
                        C_ = jvm_class(cname)
                        mt = MTc.fromMethodDescriptorString(desc, loader)
                        if name == "<init>" and in_ctor and cname in (sup, cn):
                            md = int(C_.getDeclaredConstructor(mt.parameterArray()).getModifiers())
                            if not (JMod_.isPublic(md) or JMod_.isProtected(md) or cname == cn
                                    or (not JMod_.isPrivate(md) and str(C_.getPackageName()) == str(D.getPackageName()))):
                                raise ValueError("constructor %s %s%s is not accessible from %s" % (JMod_.toString(md), cname, desc, cn))
                        elif name == "<init>":
                            lk.findConstructor(C_, mt)
                        elif op == 0xb8:
                            lk.findStatic(C_, name, mt)
                        elif op == 0xb7:
                            lk.findSpecial(C_, name, mt, D)
                        else:
                            lk.findVirtual(C_, name, mt)
                except Exception as ex_:
                    ok_ = False
                    if "caller-sensitive" in str(ex_) and op in (0xb6, 0xb8, 0xb9) and C_ is not None:
                        try:
                            mm_ = C_.getMethod(name, mt.parameterArray())
                            ok_ = JMod_.isPublic(int(C_.getModifiers())) and JMod_.isPublic(int(mm_.getModifiers()))
                            if ok_:
                                cs_.add("%s.%s" % (str(C_.getName()), name))
                        except Exception:
                            ok_ = False
                    if not ok_:
                        refused.append("%s: %s" % (where, ex_))
        return refused, n
    names = [n_[:-6].replace("/", ".") for n_ in zipfile.ZipFile(JAR).namelist() if n_.endswith(".class")]
    res = {"classes": len(names), "refs": 0, "refused": [], "per": {}}
    for cn in names:
        try:
            r_, k_ = lookup_audit(cn)
        except Exception as ex_:
            r_, k_ = ["%s: could not audit: %s" % (cn, ex_)], 0
        res["refused"] += r_
        res["refs"] += k_
        res["per"][cn.rsplit(".", 1)[-1]] = k_
    res["control"] = lookup_audit(FAKE_PKG + ".BadAccess")[0]
    res["caller_sensitive"] = sorted(cs_)
    json.dump(res, open(out, "w"), indent=1)


# ====================================================================================================== parent driver
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--live", LIVE], env=env)


def take(path, label):
    if not os.path.isfile(path):
        check(False, "%s: the child wrote no result" % label)
        return None
    d = json.load(open(path))
    OKS[0] += d["ok"]
    for f in d["fails"]:
        FAILS.append("%s: %s" % (label, f))
    for n in d.get("notes", []):
        print("  note (%s): %s" % (label, n))
    return d


def main():
    for flag, fn in (("--mkfake", lambda: run_mkfake(arg("--mkfake"))), ("--engine", lambda: run_engine(arg("--out"))),
                     ("--live-step", lambda: run_live(arg("--live-step"), arg("--out"))), ("--perm", lambda: run_perm(arg("--out"))),
                     ("--bytecode", lambda: run_bytecode(arg("--out"))), ("--audit", lambda: run_audit(arg("--out")))):
        if flag in sys.argv:
            fn()
            return
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "tmp"), exist_ok=True)
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    try:
        part_static()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0 and os.path.isfile(os.path.join(FAKE_DIR, FAKE_PKG, "FakeWorld.class")), "F: the stand-ins were generated")
        out = os.path.join(SCRATCH, "engine.json")
        child(env, "--engine", "x", "--out", out)
        take(out, "engine")
        home = os.path.join(SCRATCH, "live")
        os.makedirs(home, exist_ok=True)
        n = 0
        if os.path.isdir(LIVE):
            for f in sorted(os.listdir(LIVE)):
                if f.endswith(".json") and os.path.isfile(os.path.join(LIVE, f)):
                    shutil.copyfile(os.path.join(LIVE, f), os.path.join(home, f))      # read-only source; the copy is scratch
                    n += 1
        print("D. %d live player files copied (read-only source %s)" % (n, LIVE))
        check(n > 0, "D: live player files found to copy (%s)" % LIVE)
        used = []
        for step in ("start1", "start2"):
            out = os.path.join(SCRATCH, "live-%s.json" % step)
            child(env, "--live-step", step, "--out", out)
            r = take(out, "live " + step)
            used.append((r or {}).get("used", 0))
        check(used[0] > 0 and used[0] == used[1], "D: both starts used the same %s live player copies" % used)
        for label, flag in (("perm", "--perm"), ("bytecode", "--bytecode")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            child(env, flag, "--out", out)
            take(out, label)
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 300 and a["classes"] == len(CLASSES),
                  "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
            check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: control refused: %s" % a["control"])
            print("AA. engine-access audit: %d references in %d classes, %d refused, control refused; caller-sensitive: %s"
                  % (a["refs"], a["classes"], len(a["refused"]), a["caller_sensitive"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("%d ok, %d fail(s)" % (OKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAILED:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
