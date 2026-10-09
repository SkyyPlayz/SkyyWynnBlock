"""Harness for SkyyMerchants 0.1 (NEW mod: roaming merchants). Build first: python SkyyMerchants/build_skyymerchants_0.1.py

    python SkyyMerchants/test_skyymerchants_0.1.py [--jar <SkyyMerchants-0.1.jar>] [--dir <scratch>] [--live <world mods folder>] [--keep]

Parent (plain Python, read only): J the jar (manifest, exactly the expected classes, NO asset / lang / .ui file, no installed mod shares the
package); K Assets.zip facts (role Temple_Klops static + invulnerable + shop-less, the zone env ids, every vanilla default id, the hint key,
the 6 developer bows + boss specials on the never-sell list, no default on it).
Children (fresh JVMs, the game's JRE, -XX:-UsePerfData, TEMP / TMP / java.io.tmpdir in scratch):
  F  stand-ins compiled with javassist (MapStore / MapBuffer / MapChunk ECS parts, FakePr, TestPage = MerchPage with rebuild / close
     recorded, LookupIn / BadAccess for the audit)
  A  every class loads + verifies (-Xverify:all)
  V  THE ENGINE ASSET VALIDATORS (SkyyGear 0.2.11 harness engine_boot): the vanilla pack store by store, then THE JAR as its own pack - no
     failed store / SEVERE / WARNING about it (it ships no asset at all)
  X  EVERY NEW CODE PATH on a stand-in world (MerchEng.API) + the REAL item store + REAL SimpleItemContainers: config load / tables / every
     check= hook, the kit ops (console set, tset good + walled + bad, RELOAD), zones / items / sites / ghosts, the registry (save, reload,
     unreadable never overwritten, bad lines -> .bad copy, save refused), spot rules every branch, rumours (8 directions, distance bands,
     places, placeholders), the per-world second (appear only in loaded area + in its zone, rumour, move + restock + old removed, old one
     unloaded -> ghost -> removed when it loads, missing 15 s -> back at the same spot with the same stock, no player / no spot -> waits,
     part off -> all leave, on -> back, zone removed -> line dropped, spawn refused, save refused -> the new one removed again, role
     fallback), admin requests (remove / held / spawn / spawn while out / move / other world queued), the add-hook verdicts, THE BUY
     (success, too poor, full inventory, out of stock, Mythic / UT / never-sell walled, moved on, too far, busy profile, no coin bank, take
     refused / threw, give failed -> refund, refund failed), the shop page (build every tab + empty, tab, stale, arm, buy, close), commands,
     MerchCore.use / MerchOpen, the timer + world task
  E  THE ECS HANDLERS on stand-in stores (allocated component types): MerchUseSys (ours -> cancelled + page, ghost -> line, other NPC
     untouched, cancelled event ignored, broken logged once), MerchAddSys (ghost / orphan -> CommandBuffer.tryRemoveEntity, current /
     unrelated kept), the REAL MerchEng.prepare / uuidOf / roleOf / plateOf / worldOf
  R  RESTART x3 (fresh JVMs, the stand-in world saved between them): R1 fresh start (2 merchants appear, 1 per zone); R2 restart, the engine
     kept them (re-attached by UUID, a crash orphan removed, no new spawn); R3 restart, the engine lost them (nothing for 15 s, then back
     at the SAME spots, the late-loading old one removed); R4 restart again (kept, ghosts empty) - never 2 merchants of one zone
  D  START TWICE on a scratch COPY of the live world mods folder: only Skyy_SkyyMerchants/config.properties appears (every other file
     byte-identical); start 2 changes nothing
  P  /merchantadmin + both usage variants: skyymerchants.admin, empty permission groups, no group leak; /merchants = hytale:Adventurer
  B  BYTECODE: setup() order; spawnNPC = vanilla SpawnNpcEffect's descriptor; the engine facts (RoleBuilderSystem *UseNPC, UseEntityInteraction
     fires UseEntityEvent$Pre and honours its cancel, EntityMakeInteractableCommand = ensureComponent(Interactable))
  C  CLASS COMPARE: new mod - no older SkyyMerchants exists; the class list is the expected list (J)
  AA THE ENGINE-ACCESS AUDIT (MethodHandles.privateLookupIn every referencing class)
Scratch: tools/dev/scratch/merch01/test (deleted unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, hashlib, time, importlib.util, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.1"


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyMerchants-%s.jar" % VERSION)))
SCRATCH = os.path.abspath(arg("--dir", os.path.join(TOOLS, "dev", "scratch", "merch01", "test")))
FAKE_DIR = os.path.join(SCRATCH, "fake")
FAKE_PKG = "skyymerchtest"
PKG = "com.skyy.merchants."
NODE = "skyymerchants.admin"
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
OURS = ["MerchAddSys", "MerchAdminArg2Cmd", "MerchAdminArgCmd", "MerchAdminCmd", "MerchantsCmd", "MerchApi", "MerchCfg", "MerchCmds",
        "MerchCoins", "MerchCore", "MerchEng", "MerchItem", "MerchLog", "MerchOpen", "MerchPage", "MerchReg", "MerchRumour", "MerchShop",
        "MerchSite", "MerchSpot", "MerchTimer", "MerchUseSys", "MerchWall", "MerchWorldTask", "MerchZone", "SkyyMerchantsPlugin"]
KITC = ["CfgFile", "CfgFn", "CfgHist", "CfgLog", "CfgPub", "CfgRows", "CfgSaveTask"]
CLASSES = sorted(PKG + c for c in OURS + KITC)
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


LIVE = os.path.abspath(arg("--live", os.path.join(B.USERDATA, "Saves", deploy_world(), "mods")))


# ====================================================================================================== parent: J K
def part_static():
    z = zipfile.ZipFile(JAR)
    names = z.namelist()
    man = json.loads(z.read("manifest.json"))
    check(man.get("Main") == PKG + "SkyyMerchantsPlugin" and man.get("IncludesAssetPack") is False and man.get("Version") == VERSION
          and man.get("Name") == "%s SkyyMerchants" % VERSION, "J: manifest Main / IncludesAssetPack false / Version / Name: %r" % man)
    cls = sorted(n[:-6].replace("/", ".") for n in names if n.endswith(".class"))
    check(cls == CLASSES, "J/C: exactly the %d expected classes: extra %s missing %s" % (len(CLASSES), sorted(set(cls) - set(CLASSES)), sorted(set(CLASSES) - set(cls))))
    other = [n for n in names if not n.endswith(".class") and n != "manifest.json" and not n.endswith("/")]
    check(not other, "J: no asset / lang / .ui file ships (nothing for the asset validators): %s" % other)
    clash = []
    if os.path.isdir(B.MODS_DIR):
        for f in os.listdir(B.MODS_DIR):
            p = os.path.join(B.MODS_DIR, f)
            if not (f.endswith(".jar") or f.endswith(".zip")) or f.startswith("SkyyMerchants"):
                continue
            try:
                with zipfile.ZipFile(p) as mz:
                    if any(n.startswith("com/skyy/merchants/") for n in mz.namelist()):
                        clash.append(f)
            except Exception:
                pass
    check(not clash, "J: no installed mod ships com.skyy.merchants classes: %s" % clash)
    az = zipfile.ZipFile(ASSETS)
    an = set(az.namelist())
    roles = dict((n.rsplit("/", 1)[1][:-5], n) for n in an if n.startswith("Server/NPC/Roles/") and n.endswith(".json"))
    r = json.loads(az.read(roles["Temple_Klops"]).decode("utf-8-sig"))
    t = json.loads(az.read(roles["Template_Temple"]).decode("utf-8-sig"))
    check(r.get("Reference") == "Template_Temple" and r["Modify"].get("MotionStatic") is True and r["Modify"].get("Appearance") == "Klops_Merchant"
          and t.get("Invulnerable") is True and "InteractionInstruction" not in json.dumps(r) + json.dumps(t),
          "K: Temple_Klops = Variant of Template_Temple, MotionStatic, Klops_Merchant look, Invulnerable, no barter shop")
    envs = set(n.rsplit("/", 1)[1][:-5] for n in an if "/Environments/" in n and n.endswith(".json"))
    check(all(("Env_Zone%d" % i) in envs for i in (1, 2, 3, 4)) and "Env_Zone1_Plains" in envs and "Env_Zone2_Savanna" in envs, "K: the 4 zone env ids exist")
    check("interactionHints.trade" in az.read("Server/Languages/en-US/server.lang").decode("utf-8"), "K: the vanilla hint key")
    items = set(n.rsplit("/", 1)[1][:-5] for n in an if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    src = open(os.path.join(HERE, "build_skyymerchants_0.1.py"), encoding="utf-8").read()
    import re
    van = re.findall(r'\("([A-Za-z_]+)", "[\d,]+", \d+, \d+, "vanilla"\)', src)
    check(len(van) == 14 and all(v in items for v in van), "K: every vanilla default weapon is in Assets.zip (%d)" % len(van))
    for bow in ("Weapon_Shortbow_Combat", "Weapon_Shortbow_Bomb", "Weapon_Shortbow_Pull", "Weapon_Shortbow_Ricochet", "Weapon_Shortbow_Vampire",
                "Weapon_Shortbow_Test_Zoom"):
        check(bow in items and bow in src.split("NEVER = (")[1].split(")")[0], "K: developer bow %s exists and is on the never-sell list" % bow)
    nev = src.split("NEVER = (")[1].split(")")[0]
    wsec = src.split("WEAPONS = [")[1].split("\n]")[0]
    for sp in ("FireWhip", "ScorpianFlail", "Antique_Shield", "AntiqueShield*"):
        check(sp in nev and ('"%s"' % sp) not in wsec, "K: FIX Armory special %s is on the never-sell list and not stocked" % sp)
    arm1 = re.findall(r'\("([A-Za-z_]+)", "1", \d+, \d+, "TheArmoryMod"\)', src)
    check(len(arm1) == 6 and "Sword_Iron_Green" in arm1 and "Weapon_Battleaxe_Iron_Blue" in arm1 and "Weapon_Shield_Iron_Red_Pat" in arm1,
          "K: FIX zone 1 keeps 6 Armory recolours (+2 vanilla bows): %s" % arm1)
    # FIX2: every zone has a Mage / Priest / Monk row from SkyyArmory, verified against the SkyyArmory jar in Mods (read only)
    sa = re.findall(r'\("([A-Za-z_]+)", "([\d,]+)", \d+, \d+, "SkyyArmory"\)', src)
    saj = os.path.join(B.MODS_DIR, "SkyyArmory.jar")
    sa_ids = set()
    if os.path.exists(saj):
        with zipfile.ZipFile(saj) as z_:
            sa_ids = set(n.rsplit("/", 1)[1][:-5] for n in z_.namelist() if "/Item/Items/" in n and n.endswith(".json"))
    check(len(sa) == 13 and (not sa_ids or all(i in sa_ids for i, _ in sa)), "K: FIX2 13 SkyyArmory rows, all real SkyyArmory items: %s" % sa)
    for zn in "1234":
        fam = set(i.split("_")[1] for i, z in sa if zn in z.split(","))
        check({"Wand", "Spellbook", "Bo"} <= fam, "K: FIX2 zone %s sells a wand (Priest), a spellbook (Mage) and a Bo (Monk): %s" % (zn, fam))
    mi = re.findall(r'\("([A-Za-z_]*Mithril)", "([\d,]+)"', src)
    check(len(mi) == 3 and all(z == "3,4" for _, z in mi), "K: FIX2 Mithril (band 40-49) is sold in zones 3 and 4, not only zone 4: %s" % mi)


# ====================================================================================================== children
def _jvm(cp, verify=True, big=False):
    import jpype
    tmp = os.path.join(SCRATCH, "tmp")
    os.makedirs(tmp, exist_ok=True)
    jvm = os.path.join(B.HYTALE, "install", "release", "package", "jre", "latest", "bin", "server", "jvm.dll")
    if not os.path.exists(jvm):
        jvm = B._jvm()
    opts = (["-Xverify:all"] if verify else []) + (["-Xmx6g"] if big else []) + ["-XX:-UsePerfData", "--enable-native-access=ALL-UNNAMED",
                                                                                 "-Djava.io.tmpdir=" + tmp]
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
    from jpype import JClass
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    P = FAKE_PKG

    def mk(name, sup=None, ifaces=()):
        c = cp.makeClass(P + "." + name)
        if sup:
            c.setSuperclass(cp.get(sup))
        for i in ifaces:
            c.addInterface(cp.get(i))
        return c

    def F(c, s):
        c.addField(CtField.make(s, c))

    def M(c, s):
        c.addMethod(CtNewMethod.make(s, c))
    CR = "com.hypixel.hytale.component."
    ms = mk("MapStore", CR + "Store")
    for d in ("java.util.Map comps", "java.util.List removed", "java.util.List ensured", "com.hypixel.hytale.component.Component ensureVal",
              "java.lang.Object ext"):
        F(ms, "public %s;" % d)
    ms.addConstructor(CtNewConstructor.make("public MapStore() { super(null, 0, null, null); }", ms))
    M(ms, """public com.hypixel.hytale.component.Component getComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  if (r == null) return null;
  java.util.Map m = (java.util.Map) this.comps.get(r);
  return m == null ? null : (com.hypixel.hytale.component.Component) m.get(t);
}""")
    M(ms, """public void putComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t, com.hypixel.hytale.component.Component c) {
  java.util.Map m = (java.util.Map) this.comps.get(r);
  if (m == null) { m = new java.util.IdentityHashMap(); this.comps.put(r, m); }
  m.put(t, c);
}""")
    M(ms, """public void ensureComponent(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.ComponentType t) {
  this.ensured.add(t);
  if (getComponent(r, t) == null) putComponent(r, t, this.ensureVal);
}""")
    M(ms, """public com.hypixel.hytale.component.Holder removeEntity(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.RemoveReason why) {
  this.removed.add(r); this.comps.remove(r); return null;
}""")
    M(ms, "public java.lang.Object getExternalData() { return this.ext; }")
    ms.writeFile(out_dir)
    mb = mk("MapBuffer", CR + "CommandBuffer")
    F(mb, "public java.util.List removed;")
    mb.addConstructor(CtNewConstructor.make("public MapBuffer() { super(null); this.removed = new java.util.ArrayList(); }", mb))
    M(mb, "public void tryRemoveEntity(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.RemoveReason why) { this.removed.add(r); }")
    mb.writeFile(out_dir)
    mc = mk("MapChunk", CR + "ArchetypeChunk")
    F(mc, "public com.hypixel.hytale.component.Ref ref;")
    F(mc, "public boolean boom;")
    mc.addConstructor(CtNewConstructor.make("public MapChunk() { super(null, null); }", mc))
    M(mc, "public com.hypixel.hytale.component.Ref getReferenceTo(int i) { if (this.boom) throw new IllegalStateException(\"boom\"); return this.ref; }")
    mc.writeFile(out_dir)
    fp = mk("FakePr", "com.hypixel.hytale.server.core.universe.PlayerRef")
    F(fp, "public boolean admin;")
    F(fp, "public java.util.List msgs;")
    fp.addConstructor(CtNewConstructor.make("public FakePr() { super((com.hypixel.hytale.component.Holder) null, (java.util.UUID) null, (String) null, (String) null, (com.hypixel.hytale.server.core.io.PacketHandler) null, (com.hypixel.hytale.server.core.modules.entity.player.ChunkTracker) null); }", fp))
    M(fp, "public boolean hasPermission(java.lang.String n) { return this.admin && \"%s\".equals(n); }" % NODE)
    M(fp, "public void sendMessage(com.hypixel.hytale.server.core.Message m) { if (this.msgs == null) this.msgs = new java.util.ArrayList(); this.msgs.add(m == null ? \"null\" : m.getRawText()); }")
    fp.writeFile(out_dir)
    tp = mk("TestPage", PKG + "MerchPage")
    F(tp, "public int rebuilds;")
    F(tp, "public int closes;")
    tp.addConstructor(CtNewConstructor.make("public TestPage(com.hypixel.hytale.server.core.universe.PlayerRef pr, String wn, String zone, String npc) { super(pr, wn, zone, npc); }", tp))
    M(tp, "public void rebuild() { this.rebuilds = this.rebuilds + 1; }")
    M(tp, "public void close() { this.closes = this.closes + 1; }")
    tp.writeFile(out_dir)
    lk = mk("LookupIn")
    M(lk, "public static java.lang.invoke.MethodHandles$Lookup lookupIn(java.lang.Class c) throws java.lang.Exception {\n"
          "  return java.lang.invoke.MethodHandles.privateLookupIn(c, java.lang.invoke.MethodHandles.lookup());\n}")
    lk.writeFile(out_dir)
    ba = mk("BadAccess")
    M(ba, "public static void send(com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) {\n"
          "  p.sendUpdate(new com.hypixel.hytale.server.core.ui.builder.UICommandBuilder());\n}")
    ba.writeFile(out_dir)
    print("F. stand-ins written to", out_dir)


# ====================================================================================================== the stand-in world
def default_state():
    return {"players": {"default": [[-100.0, 0.0], [100.0, 0.0]]}, "spawn": {"default": [10.0, -10.0]}, "radius": 400.0,
            "unloaded": [], "ents": {}, "cols": {}, "roles": ["Temple_Klops", "Temple_Kweebec_Static"], "spawn_null": False,
            "exec_fail": False, "pos": [0.0, 65.0, 0.0], "env_override": None}


def make_sim(state):
    """MerchEng.API: a flat world (top Soil_Grass at y 64), Env_Zone1_Plains west of x 0, Env_Zone2_Savanna east; chunks within `radius`
    of a player are loaded (minus `unloaded`); entities = state['ents']"""
    from jpype import JImplements, JOverride, JArray, JString, JDouble, JClass
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    S = state
    log = {"spawned": [], "removed": [], "tells": [], "ptells": [], "opened": [], "execs": 0, "prepared": 0}
    conts = {}

    def loaded(wn, x, z):
        if [int(x) // 32, int(z) // 32] in S["unloaded"]:
            return False
        for px, pz in S["players"].get(wn, []):
            if (px - x) ** 2 + (pz - z) ** 2 <= S["radius"] ** 2:
                return True
        return False

    def col(x, z):
        return S["cols"].get("%d,%d" % (x, z), {})

    @JImplements(PKG + "MerchApi")
    class Sim:
        @JOverride
        def worlds(self):
            return JArray(JString)([w for w, ps in S["players"].items() if ps])

        @JOverride
        def exec(self, wn, r):
            log["execs"] += 1
            if S["exec_fail"]:
                return False
            r.run()
            return True

        @JOverride
        def height(self, wn, x, z):
            if not loaded(wn, x, z):
                return -1
            return int(col(x, z).get("h", 64))

        @JOverride
        def block(self, wn, x, y, z):
            if not loaded(wn, x, z):
                return None
            c = col(x, z)
            h = int(c.get("h", 64))
            if y == h:
                return c.get("top", "Soil_Grass")
            if y == h + 1:
                return c.get("a1", "Empty")
            if y == h + 2:
                return c.get("a2", "Empty")
            return "Rock_Stone" if y < h else "Empty"

        @JOverride
        def fluid(self, wn, x, y, z):
            return bool(col(x, z).get("fluid", False)) if loaded(wn, x, z) else True

        @JOverride
        def env(self, wn, x, y, z):
            if not loaded(wn, x, z):
                return None
            c = col(x, z)
            if "env" in c:
                return c["env"]
            if S["env_override"]:
                return S["env_override"]
            return "Env_Zone1_Plains" if x < 0 else "Env_Zone2_Savanna"

        @JOverride
        def players(self, wn):
            return JArray(JDouble)([v for p in S["players"].get(wn, []) for v in p])

        @JOverride
        def spawnPoint(self, wn):
            return JArray(JDouble)(S["spawn"].get(wn, [0.0, 0.0]))

        @JOverride
        def roleOk(self, role):
            return str(role) in S["roles"]

        @JOverride
        def spawn(self, wn, role, x, y, z, yaw, name):
            if S["spawn_null"]:
                return None
            u = "%08x-0000-4000-8000-%012x" % (random.getrandbits(32), random.getrandbits(48))
            S["ents"][u] = {"w": str(wn), "role": str(role), "name": str(name), "x": float(x), "y": float(y), "z": float(z)}
            log["spawned"].append(u)
            return u

        @JOverride
        def present(self, wn, uuid, x, z, name):
            e = S["ents"].get(str(uuid))
            if e is not None and loaded(wn, e["x"], e["z"]):
                if e["name"] != str(name):
                    e["name"] = str(name)
                    log["prepared"] += 1
                return 1
            return 0 if loaded(wn, x, z) else -1

        @JOverride
        def remove(self, wn, uuid):
            e = S["ents"].get(str(uuid))
            if e is not None and loaded(wn, e["x"], e["z"]):
                del S["ents"][str(uuid)]
                log["removed"].append(str(uuid))
                return 1
            return 0

        @JOverride
        def tell(self, wn, text, color):
            log["tells"].append((str(wn), str(text), str(color)))

        @JOverride
        def tellPlayer(self, u, text, color):
            log["ptells"].append((str(u), str(text), str(color)))

        @JOverride
        def conts(self, player):
            return JArray(IC)(conts.get(str(player), []))

        @JOverride
        def pos(self, ref, st):
            return JArray(JDouble)(S["pos"]) if S["pos"] is not None else None

        @JOverride
        def open(self, ref, pr, page):
            log["opened"].append(page)
            return True
    return Sim(), log, conts, loaded


def bridge_setup():
    from jpype import JImplements, JOverride, JClass, JLong, JBoolean, JObject, JArray, JInt
    br = JClass("java.util.concurrent.ConcurrentHashMap")()
    JClass("java.lang.System").getProperties().put("skyy.bridge", br)
    st = {"purse": {}, "take": "ok", "add": "ok", "rarity": {}, "level": True}

    @JImplements("java.util.function.Function")
    class Get:
        @JOverride
        def apply(self, u):
            return JLong(st["purse"].get(str(u), 0))

    @JImplements("java.util.function.Function")
    class Take:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            if st["take"] == "throw":
                raise RuntimeError("test: take threw")
            if st["take"] == "refuse" or st["purse"].get(u, 0) < n:
                return JBoolean(False)
            st["purse"][u] = st["purse"].get(u, 0) - n
            return JBoolean(True)

    @JImplements("java.util.function.Function")
    class Add:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            if st["add"] == "refuse":
                return None
            st["purse"][u] = st["purse"].get(u, 0) + n
            return JLong(st["purse"][u])

    @JImplements("java.util.function.Function")
    class Rarity:
        @JOverride
        def apply(self, a):
            return st["rarity"].get(str(a[0]), "normal")

    @JImplements("java.util.function.Function")
    class LevelAt:
        @JOverride
        def apply(self, a):
            if not st["level"]:
                return None
            x = int(a[1])
            Integer = JClass("java.lang.Integer")
            lo, hi = (5, 9) if x < 0 else (22, 24)
            return JArray(JObject)([Integer.valueOf(lo), Integer.valueOf(hi), "biome", "test"])
    fns = {"coins:fn:get": Get(), "coins:fn:take": Take(), "coins:fn:add": Add(), "gear:fn:rarity": Rarity(), "mob:fn:levelAt": LevelAt()}
    for k, v in fns.items():
        br.put(k, v)
    return br, st, fns


def ents_of(state, zone_side):
    return [u for u, e in state["ents"].items() if e["name"] == "Traveling Merchant" and ((e["x"] < 0) == (zone_side == 1))]


# ====================================================================================================== X (+ A, V)
def gear_harness():
    sp = importlib.util.spec_from_file_location("skyygear_h211", os.path.join(ROOT, "SkyyGear", "test_skyygear_0.2.11.py"))
    G = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(G)
    G.SCRATCH, G.JAR, G.ASSETS, G.VERSION = SCRATCH, JAR, ASSETS, VERSION
    return G


def jall(o):
    return [str(x) for x in o] if o is not None else []


def run_core(out):
    from jpype import JClass, JArray, JString, JLong, JInt, JObject, JDouble
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    bad = []
    for cn in CLASSES:
        try:
            JClass("java.lang.Class").forName(cn, True, JClass("java.lang.ClassLoader").getSystemClassLoader())
        except Exception as e:
            bad.append("%s: %s" % (cn, str(e)[:160]))
    K.check(not bad, "A: every class loads and verifies under -Xverify:all: %s" % bad)
    G = gear_harness()
    E = G.engine_boot(K)
    ours = [r for r in E["rec"] if r[0] in ("SEVERE", "WARNING") and ("SkyyMerchants" in r[1] or "merchants" in r[1].lower())]
    K.check(not ours and set(E["fail"]) <= set(E["vfail"]), "V: the jar as its own pack: no failed store / SEVERE / WARNING about it %s %s" % (ours[:3], E["fail"]))
    try:
        xrun(K, E)
    except Exception as e:
        import traceback
        traceback.print_exc()
        K.check(False, "X: run crashed: %s" % str(e)[:400])
    K.save()


def xrun(K, E):
    from jpype import JClass, JArray, JString, JLong, JInt, JObject, JDouble, JFloat
    us, jf = E["us"], E["jf"]
    P = lambda n: JClass(PKG + n)
    Cfg, Zone, Item, Site, Reg, Spot, Rum, Shop, Core, Eng, Log, Wall, Coins, Cmds, Timer, WTask, Open = (
        P("MerchCfg"), P("MerchZone"), P("MerchItem"), P("MerchSite"), P("MerchReg"), P("MerchSpot"), P("MerchRumour"), P("MerchShop"),
        P("MerchCore"), P("MerchEng"), P("MerchLog"), P("MerchWall"), P("MerchCoins"), P("MerchCmds"), P("MerchTimer"), P("MerchWorldTask"), P("MerchOpen"))
    Paths, UUID, AL, Files = JClass("java.nio.file.Paths"), JClass("java.util.UUID"), JClass("java.util.ArrayList"), JClass("java.nio.file.Files")
    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    lines = AL()
    Log.LINES = lines
    br, bst, fns = bridge_setup()
    # ---------------------------------------------------------------- the stand-in world first (check hooks call roleOk)
    state = default_state()
    sim, slog, conts, loaded = make_sim(state)
    K.check(Eng.roleOk("Temple_Klops") is True, "X: with no API the real roleOk answers (no NPCPlugin = allowed)")
    Eng.API = sim
    # ---------------------------------------------------------------- config: seed, read, tables, hooks
    mods = os.path.join(SCRATCH, "x-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    cf = os.path.join(mods, "Skyy_SkyyMerchants", "config.properties")
    K.check(os.path.isfile(cf) and "zone.zone1=default/Env_Zone1/1-20" in open(cf, encoding="latin-1").read(), "X: the default config.properties is seeded")
    zs = [str(z.key) for z in Cfg.ZONES]
    K.check(zs == ["zone1", "zone2", "zone3", "zone4"] and int(Cfg.MOVE_S) == 1200 and bool(Cfg.ON) and str(Cfg.ROLE) == "Temple_Klops"
            and len(Cfg.ITEMS) == 44, "X: 4 zones, move 1200 s, part on, role Temple_Klops, 44 stock lines: %s %d" % (zs, len(Cfg.ITEMS)))
    z1 = Cfg.zone("zone1")
    K.check(str(z1.name) == "Zone 1" and str(z1.region) == "Emerald Wilds" and int(z1.lo) == 1 and int(z1.hi) == 20 and str(z1.band()) == "Lv 1-20",
            "X: zone1 = Zone 1, Emerald Wilds, Lv 1-20")
    K.check(z1.envOk("Env_Zone1_Plains") and z1.envOk("Env_Zone1") and not z1.envOk("Env_Zone2_Savanna") and not z1.envOk(None),
            "X: zone1 env filter (prefix Env_Zone1; unknown env refused)")
    zx = Zone.parse("zx", "default|*,!Env_Zone1_Caves|0", "|")
    K.check(zx.envOk(None) and zx.envOk("Env_Zone3_Tundra") and not zx.envOk("Env_Zone1_Caves_Plains") and zx.levelOk(99) and str(zx.band()) == "any level",
            "X: * / ! filters and no level band")
    K.check(z1.levelOk(1) and z1.levelOk(19) and not z1.levelOk(20) and not z1.levelOk(0) and Zone.parse("zy", "w|a|7", "|").levelOk(7),
            "X: level band lo <= L < hi (one-level band = that level)")
    K.check(all(Zone.parse("z", v, "|") is None for v in ("w|a", "|a|1-2", "w||1-2", "w|a|5-2", "w|a|x", "w|!a|0")), "X: bad zone lines refused")
    it = Item.parse("Weapon_Sword_Frost", "1,zone2|7500|1", "|", 0)
    K.check(it is not None and it.inZone(z1) and it.inZone(Cfg.zone("zone2")) and not it.inZone(Cfg.zone("zone3")) and Item.parse("x", "*|1|1", "|", 0).inZone(z1),
            "X: item zones by number / key / *")
    K.check(all(Item.parse("x", v, "|", 0) is None for v in ("1|2", "1|-1|1", "1|2|2000", "a b|1|1", "|1|1", "1|x|1")), "X: bad stock lines refused")
    for k, v, ok in (("merchant.role", "Temple_Klops", True), ("merchant.role", "No_Such_Role", False), ("rumour.text", "hi {where}", True),
                     ("rumour.text", "no hint", False), ("merchant.ringMin", "1000", False), ("merchant.ringMin", "40", True),
                     ("merchant.ringMax", "20", False), ("merchant.ringMax", "300", True), ("merchant.neverSell", "a, *", False),
                     ("merchant.neverSell", "A_*,B", True)):
        fn = {"merchant.role": Cfg.checkRole, "rumour.text": Cfg.checkRumour, "merchant.ringMin": Cfg.checkRing, "merchant.ringMax": Cfg.checkRing,
              "merchant.neverSell": Cfg.checkNever}[k]
        r = fn(k, v)
        K.check((r is None) == ok, "X: check %s=%s -> %s" % (k, v, r))
    K.check(Cfg.checkZone("merchant.zones[zone9]", "default|Env_Zone3|30-45") is None and Cfg.checkZone("merchant.zones[z]", "w|a/b|0") is not None
            and Cfg.checkZone("merchant.zones[z]", "bad") is not None and Cfg.checkZone("x", None) is None, "X: checkZone")
    K.check(Cfg.checkStock("merchant.weapons[Weapon_Sword_Frost]", "2|7500|1") is None
            and "never" in str(Cfg.checkStock("merchant.weapons[Weapon_Shortbow_Vampire]", "1|1|1"))
            and "Magic Bags" in str(Cfg.checkStock("merchant.weapons[Skyy_Sack_Small]", "1|1|1"))
            and Cfg.checkStock("merchant.weapons[Weapon_Sword_Iron]", "1|1") is not None and Cfg.checkStock("merchant.weapons[a]", "1/2|1|1") is not None
            and Cfg.checkStock("k", None) is None, "X: checkStock (walled ids, bad shape, slash)")
    bst["rarity"]["Weapon_Sword_Onyxium"] = "mythic"
    bst["rarity"]["Weapon_Mace_Mithril"] = "untiered"
    K.check("Mythic" in str(Wall.why("Weapon_Sword_Onyxium")) and "Untiered" in str(Wall.why("Weapon_Mace_Mithril")) and Wall.why("Weapon_Sword_Frost") is None
            and Wall.why(None) is not None and Wall.listed("Debug_Stick", "Debug_*") and not Wall.listed("X", "*,") and str(Cfg.entryOf("plain")) == "plain",
            "X: the wall: gear:fn:rarity mythic / untiered, never list, prefixes")
    del bst["rarity"]["Weapon_Mace_Mithril"]
    # ---------------------------------------------------------------- the kit (console path) + RELOAD
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    P("CfgPub").start(Paths.get(mods), HL.get("SkyyMerchHarness"))
    CfgFn = P("CfgFn")
    m = str(CfgFn.cmdSetConsole("merchant.moveSeconds", "600"))
    K.check(int(Cfg.MOVE_S) == 600 and "600" in m, "X: kit console set merchant.moveSeconds 600 applies at once: %s" % m)
    m2 = str(CfgFn.cmdSetConsole("merchant.moveSeconds", "5"))
    K.check(int(Cfg.MOVE_S) == 600, "X: kit refuses 5 s (min 60): %s" % m2)
    fnk = br.get("config:fn:SkyyMerchants")
    K.check(fnk is not None and br.get("config:def:SkyyMerchants") is not None, "X: the kit published config:def / config:fn:SkyyMerchants")
    loads0 = int(Cfg.LOADS)
    r = fnk.apply(JArray(JObject)(["tset", "merchant.weapons", "Weapon_Shortbow_Vampire", "1|100|1", None, "console", "yes", "console"]))
    K.check(r is not None and str(r[0]) == "bad", "X: kit tset of a developer bow is refused (bad): %s" % (jall(r),))
    r = fnk.apply(JArray(JObject)(["add", "merchant.zones", "zone5", "default|Env_Zone2|20-30", None, "console", "yes", "console"]))
    K.check(r is not None and str(r[0]) in ("ok",), "X: kit tset of a new zone line: %s" % (jall(r),))
    for _ in range(60):
        if int(Cfg.LOADS) > loads0 and Cfg.zone("zone5") is not None:
            break
        time.sleep(0.1)
    K.check(Cfg.zone("zone5") is not None and "zone.zone5=default/Env_Zone2/20-30" in open(cf, encoding="latin-1").read(),
            "X: the table line is written with sep / and RELOAD made zone5 live")
    r = fnk.apply(JArray(JObject)(["remove", "merchant.zones", "zone5", None, "console", "yes", "console"]))
    for _ in range(60):
        if Cfg.zone("zone5") is None:
            break
        time.sleep(0.1)
    K.check(Cfg.zone("zone5") is None, "X: kit remove of zone5 reloads it away")
    m3 = str(CfgFn.cmdSetConsole("merchant.moveSeconds", "1200"))
    P("CfgPub").flush()
    # ---------------------------------------------------------------- site / ghosts
    s = Site()
    s.zone, s.uuid, s.x, s.y, s.z, s.stock, s.env, s.rumour = "zone1", str(UUID.randomUUID()), -50, 65, 7, "0:A:1:2", "Env_Zone1_Plains", "tab\there"
    s2 = Site.parse(s.line())
    K.check(s2 is not None and str(s2.uuid) == str(s.uuid) and int(s2.x) == -50 and str(s2.rumour) == "tab here", "X: site line round trip (tabs cleaned)")
    K.check(Site.parse("zone1\tnot-a-uuid\t1\t2\t3\t0\t0\t0\t\t\t\t") is None and Site.parse("# c") is None and Site.parse("a\tb") is None, "X: bad site lines")
    for i in range(20):
        s.addGhost("g%d" % i, 1000 + i)
    g = jall(s.ghostList())
    K.check(len(g) == 16 and g[-1] == "g19" and not s.hasGhost("g0"), "X: ghosts capped at 16 (oldest dropped): %d" % len(g))
    K.check(s.dropGhost("g19") and not s.hasGhost("g19") and not s.dropGhost("nope"), "X: dropGhost")
    s.addGhost("old", 0)
    K.check(s.expireGhosts(10 ** 12, 1000) and not s.hasGhost("old") and len(s.ghostList()) == 0, "X: ghosts expire")
    # ---------------------------------------------------------------- registry
    regdir = os.path.join(mods, "Skyy_SkyyMerchants", "merchants")
    Reg.DIR = Paths.get(regdir)
    l = Reg.sites("w1")
    K.check(l is not None and l.size() == 0 and not Reg.known("w9"), "X: a world without a file = empty list")
    K.check(Reg.NOFILE.containsKey("w9") and not Reg.known("w9"), "X: FIX known() caches 'no registry file' (no disk stat per NPC add)")
    Reg.NOFILE.put("w1", True)
    Reg.add(l, s2)
    K.check(Reg.save("w1") and os.path.isfile(os.path.join(regdir, "w1.tsv")), "X: registry saved atomically")
    K.check(not Reg.NOFILE.containsKey("w1"), "X: FIX save() clears the cached 'no file' of its world")
    Reg.W.clear()
    l2 = Reg.sites("w1")
    K.check(l2.size() == 1 and str(Reg.find(l2, "zone1").uuid) == str(s.uuid) and Reg.known("w1"), "X: registry read back")
    with open(os.path.join(regdir, "w2.tsv"), "w", encoding="utf-8") as f_:
        f_.write("# x\n" + s2.line() + "\nbroken line\n")
    l3 = Reg.sites("w2")
    bads = [f for f in os.listdir(regdir) if f.startswith("w2-") and f.endswith(".tsv.bad")]
    K.check(l3.size() == 1 and len(bads) == 1, "X: an unreadable line is skipped after the whole file was copied to .bad: %s" % bads)
    os.makedirs(os.path.join(regdir, "w3.tsv"))
    K.check(Reg.sites("w3") is None and os.path.isdir(os.path.join(regdir, "w3.tsv")), "X: an unreadable registry pauses that world and is never overwritten")
    K.check(str(Reg.wf("a b/c")) == "a_b_c" and str(Reg.wf(None)) == "_", "X: world file names sanitised")
    # ---------------------------------------------------------------- spot rules
    pl = JArray(JDouble)([-100.0, 0.0])
    def colr(x, z, zone="zone1"):
        return int(Spot.column("default", Cfg.zone(zone), x, z, pl))
    K.check(colr(-100, 10) < 0 and "near a player" in str(Spot.LAST_WHY), "X: spot: near a player")
    K.check(colr(-1000, 0) < 0 and "not loaded" in str(Spot.LAST_WHY), "X: spot: not loaded")
    state["cols"]["-150,0"] = {"top": "Rock_Stone_Brick_Stairs"}
    K.check(colr(-150, 0) < 0 and "natural" in str(Spot.LAST_WHY), "X: spot: built block")
    state["cols"]["-151,0"] = {"a1": "Plant_Flower_Red"}
    K.check(colr(-151, 0) < 0 and "room" in str(Spot.LAST_WHY), "X: spot: a flower above (never replaces a garden)")
    state["cols"]["-152,0"] = {"fluid": True}
    K.check(colr(-152, 0) < 0 and "water" in str(Spot.LAST_WHY), "X: spot: water")
    state["cols"]["-153,0"] = {"h": 0}
    K.check(colr(-153, 0) < 0 and "no ground" in str(Spot.LAST_WHY), "X: spot: no ground")
    K.check(colr(50, 0) < 0 and "outside the zone" in str(Spot.LAST_WHY), "X: spot: zone2 env for a zone1 merchant")
    state["cols"]["-154,0"] = {"env": "Env_Zone1_Plains"}
    bst_level = bst["level"]
    K.check(colr(-154, 0) == 65 and str(Spot.LAST_ENV) == "Env_Zone1_Plains", "X: spot: a valid zone1 column = y 65")
    state["cols"]["60,0"] = {}
    K.check(int(Spot.column("default", Cfg.zone("zone1"), -155, 0, pl)) == 65, "X: spot: zone1 level 5 inside 1-20")
    zl = Zone.parse("zl", "default|*|30-45", "|")
    K.check(int(Spot.column("default", zl, -156, 0, pl)) < 0 and "level" in str(Spot.LAST_WHY), "X: spot: SkyyMobs level outside the band")
    bst["level"] = False
    K.check(int(Spot.column("default", zl, -156, 0, pl)) == 65, "X: spot: no SkyyMobs answer = the Area alone decides")
    bst["level"] = bst_level
    K.check(Spot.ground("Soil_Grass") and not Spot.ground("Soil_Dirt_Tilled") and not Spot.ground("Rock_Stone_Cobble") and not Spot.ground(None)
            and Spot.soft("Plant_Grass_Short") and Spot.soft("Plant_Fern") and not Spot.soft("Plant_Bush") and not Spot.soft(None), "X: ground / soft")
    K.check(int(Core.SPOT_TRIES) == 16, "X: FIX2 a spot search tries 16 columns (was 6: a zone next to where players stand failed ~1 in 60 searches)")
    K.check(Spot.find("nowhere", z1, 6) is None and "no player" in str(Spot.LAST_WHY), "X: find: no player in the world")
    p_ = Spot.find("default", z1, 50)
    K.check(p_ is not None and int(p_[0]) < 0, "X: find: a zone1 spot west of x 0: %s" % (list(p_) if p_ is not None else None))
    # ---------------------------------------------------------------- rumours
    dirs = [(0, -100, "north"), (100, -100, "north-east"), (100, 0, "east"), (100, 100, "south-east"), (0, 100, "south"), (-100, 100, "south-west"),
            (-100, 0, "west"), (-100, -100, "north-west")]
    K.check(all(str(Rum.dir(dx, dz)) == d for dx, dz, d in dirs), "X: 8-way compass (north = -Z)")
    K.check([str(Rum.where(x, 0)) for x in (10, 300, 800, 2000, 5000)] == ["close to spawn", "a short walk east of spawn", "a fair way east of spawn",
                                                                           "far to the east of spawn", "very far to the east of spawn"], "X: distance bands")
    K.check([str(Rum.place(e)) for e in ("Env_Zone1_Plains", "Env_Zone1", "Env_Zone2_Mage_Towers", "Env_Zone9_Odd_Place", None, "Foo")]
            == ["plains", "wilds", "mage towers", "odd place", "wilds", "wilds"], "X: place names")
    t = str(Rum.text("{place}|{where}|{dir}|{dist}|{zone}|{region}|{name}", z1, "Env_Zone1_Azure", -800.0, -800.0, "N"))
    K.check(t == "azure forest|a fair way north-west of spawn|north-west|a fair way|Zone 1|Emerald Wilds|N", "X: every placeholder: %s" % t)
    K.check("[0-9]" not in t and not any(c.isdigit() for c in str(Rum.text(Cfg.RUMOUR, z1, "Env_Zone1_Plains", -800.0, 300.0, "N")).replace("Zone 1", "")),
            "X: the default rumour has no coordinates")
    # ---------------------------------------------------------------- THE SECOND (fresh registry)
    Reg.W.clear()
    Reg.NAMES.clear()
    shutil.rmtree(regdir, ignore_errors=True)
    Core.KNOWN.clear()
    Core.GHOSTS.clear()
    now = 10 ** 12
    n0 = list(Core.N)
    Core.second("default", now)
    sites = Reg.sites("default")
    a1, a2 = Reg.find(sites, "zone1"), Reg.find(sites, "zone2")
    K.check(a1 is not None and a2 is not None and len(str(a1.uuid)) > 0 and len(str(a2.uuid)) > 0 and Reg.find(sites, "zone3") is None,
            "X: first second: zone1 + zone2 merchants appear, zone3 / zone4 (no area loaded) wait")
    K.check(state["ents"][str(a1.uuid)]["x"] < 0 and state["ents"][str(a2.uuid)]["x"] >= 0 and str(a1.env).startswith("Env_Zone1") and str(a2.env).startswith("Env_Zone2"),
            "X: merchants only in their zone (zone1 west / Env_Zone1, zone2 east / Env_Zone2)")
    K.check(all(48 <= min(((e["x"] - px) ** 2 + (e["z"] - pz) ** 2) ** 0.5 for px, pz in state["players"]["default"]) <= 200 for e in state["ents"].values()),
            "X: spots 48-192 blocks from a player")
    K.check(len(slog["tells"]) == 2 and all("traveling merchant" in t_[1] and t_[2] == "#E8A93B" for t_ in slog["tells"]), "X: one rumour per merchant, gold: %s" % slog["tells"])
    K.check(str(Core.KNOWN.get(str(a1.uuid))) == "default\tzone1" and os.path.isfile(os.path.join(regdir, "default.tsv")), "X: indexed + saved")
    st1 = str(a1.stock)
    offers1 = [x.split(":") for x in st1.split(",") if x]
    K.check(1 <= len(offers1) <= 4 and all(o[0] == "0" and o[1] in ("Weapon_Shortbow_Frost", "Weapon_Shortbow_Flame") for o in offers1),
            "X: zone1 restock = only the ids this server knows (the Armory is not loaded here): %s" % st1)
    st2 = str(a2.stock)
    K.check("Weapon_Sword_Frost" in st2 or "Weapon_Axe_Bone" in st2 or len(st2) > 0, "X: zone2 stock: %s" % st2)
    u1 = str(a1.uuid)
    Core.second("default", now + 1000)
    K.check(str(a1.uuid) == u1 and len(state["ents"]) == 2, "X: next second: nothing changes")
    rename = str(CfgFn.cmdSetConsole("merchant.name", "Wandering Klops"))
    Core.second("default", now + 2000)
    K.check(state["ents"][u1]["name"] == "Wandering Klops", "X: a renamed merchant gets the new name within a second (present re-applies it)")
    CfgFn.cmdSetConsole("merchant.name", "Traveling Merchant")
    Core.second("default", now + 3000)
    # move (20 min)
    t_move = now + 1200 * 1000 + 5000
    v1 = int(a1.visit)
    Core.second("default", t_move)
    K.check(str(a1.uuid) != u1 and u1 not in state["ents"] and u1 in slog["removed"] and int(a1.visit) == v1 + 1 and len(str(a1.ghosts)) == 0,
            "X: after 1200 s the merchant MOVES: new one, old removed, no ghost, visit +1")
    K.check(len(slog["tells"]) >= 4, "X: a rumour per move")
    K.check(len([e for e in state["ents"].values()]) == 2, "X: still exactly 2 merchants")
    # move while the old one's chunk is NOT loaded -> ghost, removed when it loads
    u2 = str(a1.uuid)
    e2 = state["ents"][u2]
    state["unloaded"].append([int(e2["x"]) // 32, int(e2["z"]) // 32])
    Core.request("zone1", "move", None)
    Core.second("default", t_move + 1000)
    K.check(str(a1.uuid) != u2 and a1.hasGhost(u2) and u2 in state["ents"] and str(Core.GHOSTS.get(u2)) == "default",
            "X: the old one is in an unloaded chunk -> kept as a ghost")
    K.check(int(Core.onAdded("default", u2, "Temple_Klops", "Traveling Merchant")) == 1 and not a1.hasGhost(u2), "X: the ghost loads -> the add hook says remove it")
    del state["ents"][u2]
    state["unloaded"] = []
    # missing in a loaded area -> 15 s -> back at the same spot, same stock
    u3, sx, sy, sz, sst, svis = str(a1.uuid), int(a1.x), int(a1.y), int(a1.z), str(a1.stock), int(a1.visit)
    del state["ents"][u3]
    tm = t_move + 2000
    Core.second("default", tm)
    Core.second("default", tm + 10000)
    K.check(str(a1.uuid) == u3, "X: missing for under 15 s: nothing yet")
    Core.second("default", tm + 16000)
    K.check(str(a1.uuid) != u3 and (int(a1.x), int(a1.y), int(a1.z)) == (sx, sy, sz) and str(a1.stock) == sst and int(a1.visit) == svis and a1.hasGhost(u3),
            "X: missing 15 s in a loaded area -> back at the SAME spot with the same stock (old uuid a ghost)")
    # zone with no valid spot waits; no player = nothing
    nsp = int(Core.N[6])
    state["players"]["default"] = []
    Core.second("default", tm + 17000)
    K.check(len(state["ents"]) == 2, "X: no player in the world: nothing moves")
    state["players"]["default"] = [[-100.0, 0.0], [100.0, 0.0]]
    # part off -> all leave, lines kept; on -> back
    CfgFn.cmdSetConsole("part.merchants", "false")
    K.check(not bool(Cfg.ON), "X: part off")
    Core.second("default", tm + 18000)
    K.check(len(state["ents"]) == 0 and Reg.find(sites, "zone1") is not None and len(str(a1.uuid)) == 0, "X: part OFF: every merchant leaves, lines kept")
    CfgFn.cmdSetConsole("part.merchants", "true")
    Core.second("default", tm + 19000)
    K.check(len(state["ents"]) == 2, "X: part ON: they come back")
    # zone removed from the config -> its merchant leaves and the line goes
    r = fnk.apply(JArray(JObject)(["remove", "merchant.zones", "zone2", None, "console", "yes", "console"]))
    for _ in range(60):
        if Cfg.zone("zone2") is None:
            break
        time.sleep(0.1)
    Core.second("default", tm + 20000)
    K.check(Cfg.zone("zone2") is None and Reg.find(sites, "zone2") is None and len(state["ents"]) == 1, "X: zone2 removed -> merchant gone, line dropped")
    r = fnk.apply(JArray(JObject)(["add", "merchant.zones", "zone2", "default|Env_Zone2|20-30", None, "console", "yes", "console"]))
    for _ in range(60):
        if Cfg.zone("zone2") is not None:
            break
        time.sleep(0.1)
    Core.second("default", tm + 21000)
    K.check(len(state["ents"]) == 2, "X: zone2 back -> merchant back")
    # spawn refused / role fallback / save refused
    a1 = Reg.find(sites, "zone1")
    state["spawn_null"] = True
    n7 = int(Core.N[7])
    Core.request("zone1", "move", None)
    Core.second("default", tm + 22000)
    K.check(int(Core.N[7]) == n7 + 1 and len(state["ents"]) == 2, "X: spawn refused -> nothing changes (retried)")
    state["spawn_null"] = False
    CfgFn.cmdSetConsole("merchant.role", "Temple_Klops")
    Cfg.ROLE = "Gone_Role"
    Core.request("zone1", "move", None)
    Core.second("default", tm + 23000)
    K.check(state["ents"][str(a1.uuid)]["role"] == "Temple_Klops", "X: a role that does not exist -> the default role")
    Cfg.ROLE = "Temple_Klops"
    good_dir = Reg.DIR
    blocker = os.path.join(SCRATCH, "x-blocker")
    open(blocker, "w").write("x")
    Reg.DIR = Paths.get(blocker).resolve("sub")
    n8, ents_before, ua = int(Core.N[8]), dict(state["ents"]), str(a1.uuid)
    Core.request("zone1", "move", None)
    Core.second("default", tm + 24000)
    K.check(int(Core.N[8]) == n8 + 1 and str(a1.uuid) == ua and set(state["ents"]) == set(ents_before), "X: save refused -> the new merchant removed again, nothing changed")
    Reg.DIR = good_dir
    # admin requests (replies to the requester)
    adm = UUID.randomUUID()
    Core.request("zone1", "remove", adm)
    Core.second("default", tm + 25000)
    K.check(len(str(a1.uuid)) == 0 and bool(a1.held) and len(state["ents"]) == 1 and "stays away" in slog["ptells"][-1][1], "X: remove -> gone + held, the admin is told")
    Core.second("default", tm + 3000000)
    K.check(len(state["ents"]) == 1, "X: held: does not come back by itself")
    Core.request("zone1", "spawn", adm)
    Core.second("default", tm + 3001000)
    K.check(len(state["ents"]) == 2 and not bool(a1.held) and "appeared" in slog["ptells"][-1][1], "X: spawn -> back, the admin is told: %s" % slog["ptells"][-1][1])
    Core.request("zone1", "spawn", adm)
    Core.second("default", tm + 3002000)
    K.check("already out" in slog["ptells"][-1][1], "X: spawn while out -> 'already out'")
    state["env_override"] = "Env_Zone9_Nowhere"
    Core.request("zone1", "move", adm)
    Core.second("default", tm + 3003000)
    K.check("No spot" in slog["ptells"][-1][1] and len(state["ents"]) == 2, "X: move with no valid spot -> told, the merchant stays")
    state["env_override"] = None
    # add-hook verdicts
    cur = str(a1.uuid)
    K.check(int(Core.onAdded("default", cur, "Temple_Klops", "Traveling Merchant")) == 0, "X: add hook: the current merchant is kept")
    K.check(int(Core.onAdded("default", "orphan-1", "Temple_Klops", "Traveling Merchant")) == 1, "X: add hook: our role + our name, no line = orphan removed")
    K.check(int(Core.onAdded("default", "vanilla-1", "Temple_Klops", None)) == 0 and int(Core.onAdded("default", "x", "Kweebec_Merchant", "Traveling Merchant")) == 0,
            "X: add hook: a vanilla temple Klops / another role is kept")
    os.makedirs(os.path.join(regdir, "w3.tsv"), exist_ok=True)
    Reg.W.remove("w3")
    K.check(int(Core.onAdded("w3", "x", "Temple_Klops", "Traveling Merchant")) == 0 and int(Core.onAdded(None, "x", "a", "b")) == 0,
            "X: add hook: an unreadable registry never removes anything")
    # ---------------------------------------------------------------- commands
    FP = JClass(FAKE_PKG + ".FakePr")
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    def fakepr(name):
        p = us.allocateInstance(FP.class_)
        for f in PR.class_.getDeclaredFields():
            tn = str(f.getType().getName())
            if tn == "java.util.UUID":
                f.setAccessible(True); f.set(p, UUID.randomUUID())
            elif tn == "java.lang.String" and str(f.getName()).lower().startswith("user"):
                f.setAccessible(True); f.set(p, JString(name))
        return p
    apr = fakepr("Admin")
    K.check(str(apr.getUsername()) == "Admin" and apr.getUuid() is not None, "X: FakePr has a name + uuid")
    res = {v: str(Cmds.admin(apr, "default", v, z)) for v, z in (("help", None), ("list", None), ("fly", None), ("move", None), ("move", "zoneX"))}
    K.check(res["help"].startswith("=/merchantadmin") and "zone1 (Zone 1" in res["list"] and "since start" in res["list"] and res["fly"].startswith("-Unknown"),
            "X: admin help / list / unknown: %s" % dict((k, v[:80]) for k, v in res.items()))
    K.check("Which zone" in str(Cmds.admin(apr, "default", "move", "")) and "No zone zoneX" in str(Cmds.admin(apr, "default", "move", "zoneX")), "X: admin bad zone")
    out_ = str(Cmds.admin(apr, "default", "move", "zone1"))
    K.check(out_ == "", "X: admin move in the same world runs at once (reply comes as a line)")
    out2 = str(Cmds.admin(apr, "elsewhere", "move", "zone1"))
    K.check(out2.startswith("=Queued") and Core.REQ.containsKey("zone1"), "X: admin move from another world is queued")
    Core.REQ.clear()
    CfgFn.cmdSetConsole("part.merchants", "false")
    K.check("switched off" in str(Cmds.admin(apr, "default", "spawn", "zone1")), "X: admin spawn while part off is refused")
    CfgFn.cmdSetConsole("part.merchants", "true")
    Core.second("default", tm + 3004000)
    Cmds.reply(apr, "+ok\nline2")
    Cmds.reply(apr, "")
    K.check(len(apr.msgs) >= 2 and str(apr.msgs[-2]).startswith("[Merchants] ok"), "X: reply splits lines: %s" % jall(apr.msgs)[-2:])
    rt = str(Core.rumoursText("default", tm + 3004000))
    K.check("Zone 1:" in rt and "traveling merchant" in rt and "moves on in about" in rt and "Zone 3: no word" in rt, "X: /merchants text: %s" % rt[:200])
    K.check("No traveling merchants" in str(Core.rumoursText("nowhere", 0)), "X: /merchants in a world without zones")
    W_ = JClass("com.hypixel.hytale.server.core.universe.world.World")
    wobj = us.allocateInstance(W_.class_)
    jf(W_, "name").set(wobj, JString("default"))
    for cn, args_ in (("MerchantsCmd", None), ("MerchAdminCmd", None), ("MerchAdminArgCmd", None), ("MerchAdminArg2Cmd", None)):
        c = JClass(PKG + cn)()
        mth = [mm for mm in c.getClass().getDeclaredMethods() if str(mm.getName()) == "execute"][0]
        mth.setAccessible(True)
        n_ = len(apr.msgs)
        mth.invoke(c, None, None, None, apr, wobj)
        K.check(len(apr.msgs) > n_, "X: %s.execute answers in chat" % cn)
    # ---------------------------------------------------------------- the buy (REAL containers)
    a1 = Reg.find(sites, "zone1")
    buyer = UUID.randomUUID()
    inv = SIC(4)
    conts["inv"] = [inv]
    a1.stock = "0:Weapon_Sword_Frost:7500:1,0:Weapon_Sword_Onyxium:45000:1,0:Weapon_Shortbow_Vampire:10:1,0:No_Such_Item:5:1,1:Weapon_Axe_Bone:6000:0"
    ex = state["ents"][str(a1.uuid)]
    state["pos"] = [ex["x"], ex["y"], ex["z"]]
    pos = JArray(JDouble)(state["pos"])
    npc = str(a1.uuid)
    def buy(id_, cat=0, who=buyer, player="inv", p=pos, n=None):
        return str(Shop.buy(who, "Tester", JString(player), p, "default", "zone1", n or npc, cat, id_))
    Shop.LOGF = Paths.get(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"))
    bst["purse"][str(buyer)] = 1000
    r_ = buy("Weapon_Sword_Frost")
    K.check(r_.startswith("-You need 7,500 coins - you have 1,000") and bst["purse"][str(buyer)] == 1000 and int(Shop.countIn(inv, "Weapon_Sword_Frost")) == 0,
            "X: buy too poor: refused, nothing moves: %s" % r_)
    bst["purse"][str(buyer)] = 100000
    full = SIC(1)
    full.addItemStack(IS("Weapon_Sword_Iron", 1))
    conts["full"] = [full]
    r_ = buy("Weapon_Sword_Frost", player="full")
    K.check(r_.startswith("-Your inventory is full") and bst["purse"][str(buyer)] == 100000, "X: buy with a full inventory: refused before paying: %s" % r_)
    r_ = buy("Weapon_Sword_Onyxium")
    K.check("Mythic" in r_ and bst["purse"][str(buyer)] == 100000, "X: Mythic (SkyyGear says) never sold: %s" % r_)
    r_ = buy("Weapon_Shortbow_Vampire")
    K.check("never-sell" in r_, "X: a developer bow is never sold: %s" % r_)
    K.check("does not know" in buy("No_Such_Item"), "X: an unknown id is refused")
    K.check("Sold out" in buy("Weapon_Axe_Bone", cat=1), "X: an offer with 0 left = sold out")
    of_ = Shop.offers(a1, 0)
    ids_ = [str(x) for x in of_[0]]
    K.check(ids_ == ["Weapon_Sword_Frost"] and "No_Such_Item" in str(a1.stock) and "Weapon_Sword_Onyxium" in str(a1.stock),
            "X: FIX2 the page hides unknown / Mythic / never-sell rows of the saved stock (saved line kept): %s" % ids_)
    K.check("does not sell" in buy("Weapon_Sword_Iron"), "X: an id not on offer")
    K.check("moved on" in buy("Weapon_Sword_Frost", n="00000000-0000-4000-8000-000000000000"), "X: the page's merchant moved on")
    K.check("Walk back" in buy("Weapon_Sword_Frost", p=JArray(JDouble)([ex["x"] + 50, 65.0, ex["z"]])), "X: too far away")
    K.check("Walk back" in str(Shop.buy(buyer, "Tester", JString("inv"), None, "default", "zone1", npc, 0, "Weapon_Sword_Frost"))
            and bst["purse"][str(buyer)] == 100000, "X: FIX no position = refused (was: range check skipped)")
    K.check("Walk back" in buy("Weapon_Sword_Frost", p=JArray(JDouble)([ex["x"], float(a1.y) + 40.0, ex["z"]])), "X: FIX far above the merchant = refused (height counts)")
    br.put("profile:busy:" + str(buyer), True)
    K.check("profile" in buy("Weapon_Sword_Frost"), "X: profile busy")
    br.remove("profile:busy:" + str(buyer))
    tk = br.remove("coins:fn:take")
    K.check("coin bank (SkyyCoins) is not running" in buy("Weapon_Sword_Frost"), "X: no coin bank")
    br.put("coins:fn:take", tk)
    bst["take"] = "refuse"
    K.check("Not enough coins" in buy("Weapon_Sword_Frost") and "1" in str(a1.stock.split(",")[0]), "X: take refused -> stock back, nothing given")
    bst["take"] = "throw"
    K.check("coin bank failed" in buy("Weapon_Sword_Frost"), "X: take threw -> TAKE-ERROR logged, nothing given")
    bst["take"] = "ok"
    bst_before = bst["purse"][str(buyer)]
    Shop.LOGF = Paths.get(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"))
    st_ = SIC(1)
    st_.addItemStack(IS("Weapon_Sword_Frost", 1))
    conts["lie"] = [st_]
    r_ = buy("Weapon_Sword_Frost", player="lie")
    K.check(r_.startswith("-Your inventory is full"), "X: Weapon stacks are 1 high: an occupied slot is no room: %s" % r_)
    good = buy("Weapon_Sword_Frost")
    K.check(good.startswith("+Bought Frost Sword for 7,500 coins") and bst["purse"][str(buyer)] == bst_before - 7500 and int(Shop.countIn(inv, "Weapon_Sword_Frost")) == 1
            and "0:Weapon_Sword_Frost:7500:0" in str(a1.stock), "X: BUY SUCCESS: coins taken, the item in storage, stock 1 -> 0: %s" % good)
    K.check("Sold out" in buy("Weapon_Sword_Frost") and int(Shop.countIn(inv, "Weapon_Sword_Frost")) == 1, "X: out of stock after the buy")
    salelog = open(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"), encoding="utf-8").read()
    K.check("BUY Tester" in salelog and "TAKE-ERROR" in salelog, "X: sales.log BUY + TAKE-ERROR lines")
    reg_txt = open(os.path.join(regdir, "default.tsv"), encoding="utf-8").read()
    K.check("Weapon_Sword_Frost:7500:0" in reg_txt, "X: the stock change is saved")
    a1.stock = "0:Weapon_Sword_Frost:7500:1"
    inv2 = SIC(4)
    conts["inv2"] = [inv2]
    okdir = Reg.DIR
    badf = os.path.join(mods, "Skyy_SkyyMerchants", "notadir")
    open(badf, "w").close()
    Reg.DIR = Paths.get(badf)
    p0 = bst["purse"][str(buyer)]
    r_ = buy("Weapon_Sword_Frost", player="inv2")
    Reg.DIR = okdir
    os.remove(badf)
    K.check(r_.startswith("+Bought") and int(Shop.countIn(inv2, "Weapon_Sword_Frost")) == 1 and bst["purse"][str(buyer)] == p0 - 7500
            and "SAVE-FAILED Tester" in open(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"), encoding="utf-8").read(),
            "X: FIX a sale whose registry save fails is logged SAVE-FAILED in sales.log: %s" % r_)
    K.check(bool(Reg.save("default")), "X: the registry saves again once the folder is back")
    # give fails -> refund ; refund fails -> REFUND-FAILED (the take function empties the container list between room() and give())
    a1.stock = "0:Weapon_Sword_Frost:7500:2"
    K.check(int(Shop.give(JString("nothing"), "Weapon_Sword_Frost")) == 0, "X: give() with no container gives 0")
    conts["once"] = [SIC(1)]
    from jpype import JImplements, JOverride, JBoolean
    @JImplements("java.util.function.Function")
    class TakeAndFill:
        @JOverride
        def apply(self, a):
            u, n = str(a[0]), int(a[1])
            bst["purse"][u] = bst["purse"].get(u, 0) - n
            conts["once"] = []
            return JBoolean(True)
    br.put("coins:fn:take", TakeAndFill())
    pv = bst["purse"][str(buyer)]
    r_ = buy("Weapon_Sword_Frost", player="once")
    K.check(r_.startswith("-The item could not be given - your 7,500 coins were refunded") and bst["purse"][str(buyer)] == pv and "0:Weapon_Sword_Frost:7500:2" in str(a1.stock),
            "X: the item could not be given -> coins refunded + stock back: %s" % r_)
    conts["once"] = [SIC(1)]
    bst["add"] = "refuse"
    r_ = buy("Weapon_Sword_Frost", player="once")
    K.check("refund" in r_ and "FAILED" in r_ and "REFUND-FAILED" in open(os.path.join(mods, "Skyy_SkyyMerchants", "sales.log"), encoding="utf-8").read(),
            "X: refund refused -> REFUND-FAILED logged + told: %s" % r_)
    bst["add"] = "ok"
    br.put("coins:fn:take", fns["coins:fn:take"])
    CfgFn.cmdSetConsole("part.merchants", "false")
    K.check("away" in buy("Weapon_Sword_Frost"), "X: part off -> no buying")
    CfgFn.cmdSetConsole("part.merchants", "true")
    Core.second("default", tm + 3005000)
    # stock helpers
    K.check(str(Shop.label("Weapon_Sword_Iron")) == "Sword Iron" and str(Shop.name("Weapon_Sword_Frost")) == "Frost Sword" and len(str(Shop.name("Sword_Iron_Green"))) > 0,
            "X: names: build-time / label fallback")
    K.check(int(Shop.adjust(None, 0, "x", -1)) == -1 and int(Shop.adjust(a1, 0, "nope", -1)) == -1, "X: adjust on nothing")
    K.check(Shop.room(JString("inv"), "Food_Bread") and Shop.room(JString("inv"), "Weapon_Sword_Frost"), "X: room() with free slots")
    # ---------------------------------------------------------------- the page
    a1 = Reg.find(sites, "zone1")
    a1.stock = "0:Weapon_Sword_Frost:7500:1,0:Weapon_Axe_Bone:6000:0"
    pp = fakepr("Shopper")
    bst["purse"][str(pp.getUuid())] = 50000
    TP = JClass(FAKE_PKG + ".TestPage")
    page = TP(pp, "default", "zone1", str(a1.uuid))
    UCB, UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder"), JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")
    def build(pg):
        b_, e_ = UCB(), UEB()
        pg.build(None, b_, e_, None)
        return b_, e_
    b_, e_ = build(page)
    nev = len(e_.getEvents())
    K.check(nev == 5 and len(b_.getCommands()) > 10, "X: page tab 0: 4 base bindings + 1 Buy (sold-out row has none): %d events, %d commands" % (nev, len(b_.getCommands())))
    K.check("Zone 1 merchant - Lv 1-20 - moves on in" in str(page.hintText(int(time.time() * 1000))) or "moved on" in str(page.hintText(0)), "X: page hint")
    page.handleDataEvent(None, None, '{"a":"tab","i":"1"}')
    b_, e_ = build(page)
    K.check(int(page.tab) == 1 and page.rebuilds == 1 and len(e_.getEvents()) == 4, "X: tab Mounts: empty (only the 4 base bindings)")
    page.handleDataEvent(None, None, '{"a":"tab","i":"2"}')
    build(page)
    page.handleDataEvent(None, None, '{"a":"tab","i":"0"}')
    build(page)
    page.handleDataEvent(None, None, '{"a":"buy","i":"0","t":"stale"}')
    K.check(str(page.info).startswith("=The page changed"), "X: stale token")
    build(page)
    tok = str(page.tok)
    state["pos"] = [state["ents"][str(a1.uuid)]["x"], 65.0, state["ents"][str(a1.uuid)]["z"]]
    conts["None"] = [SIC(2)]
    page.handleDataEvent(None, None, '{"a":"buy","i":"0","t":"%s"}' % tok)
    K.check(str(page.info).startswith("=Buy Frost Sword for 7,500 coins? Click BUY again"), "X: first Buy click arms: %s" % page.info)
    build(page)
    page.handleDataEvent(None, None, '{"a":"buy","i":"0","t":"%s"}' % str(page.tok))
    K.check(str(page.info).startswith("+Bought Frost Sword"), "X: second click buys: %s" % page.info)
    build(page)
    page.handleDataEvent(None, None, '{"a":"buy","i":"9","t":"%s"}' % str(page.tok))
    K.check("gone" in str(page.info), "X: a row that is gone")
    page.handleDataEvent(None, None, '{"a":"close"}')
    K.check(page.closes == 1, "X: Close")
    page2 = TP(pp, "default", "zone1", "00000000-0000-4000-8000-000000000000")
    b2, e2 = build(page2)
    K.check(len(e2.getEvents()) == 4 and "moved on" in str(page2.hintText(0)), "X: a page of a merchant that moved on shows nothing for sale")
    K.check(str(JClass(PKG + "MerchPage").jsonStr('{"a":"x\\"y"}', "a")) == 'x"y' and int(JClass(PKG + "MerchPage").toInt("x")) == -1, "X: jsonStr / toInt")
    # ---------------------------------------------------------------- use + open + timer
    n9 = int(Core.N[9])
    K.check(Core.use("default", str(a1.uuid), None, pp) and len(slog["opened"]) == 1 and int(Core.N[9]) == n9 + 1, "X: use on our merchant -> the page opens next tick")
    Core.GHOSTS.put("ghost-x", "default")
    K.check(Core.use("default", "ghost-x", None, pp) and "packing up" in str(pp.msgs[-1]), "X: use on an old one -> a line")
    K.check(not Core.use("default", "someone-else", None, pp) and not Core.use("default", None, None, pp), "X: use on another NPC -> not ours")
    state["exec_fail"] = True
    K.check(Core.use("default", str(a1.uuid), None, pp) and len(slog["opened"]) == 2, "X: no world execute -> opened directly")
    state["exec_fail"] = False
    CfgFn.cmdSetConsole("part.merchants", "false")
    Open(None, pp, "default", "zone1", str(a1.uuid)).run()
    K.check("away" in str(pp.msgs[-1]), "X: MerchOpen while part off -> a line")
    CfgFn.cmdSetConsole("part.merchants", "true")
    ex0 = slog["execs"]
    Timer().run()
    K.check(slog["execs"] > ex0 and not WTask.PENDING.containsKey("default"), "X: the timer runs the world task (pending cleared)")
    state["exec_fail"] = True
    Timer().run()
    K.check(not WTask.PENDING.containsKey("default"), "X: a refused execute clears pending")
    state["exec_fail"] = False
    WTask.PENDING.put("default", True)
    ex1 = slog["execs"]
    Timer().run()
    K.check(slog["execs"] == ex1, "X: a world whose task is still pending is not queued twice")
    WTask.PENDING.clear()
    lt = str(Core.listText("default", tm + 3006000))
    K.check("zone3" in lt and "not out yet" in lt and "since start" in lt, "X: /merchantadmin list text: %s" % lt[:300])
    Core.flush()
    K.check(not any("WARN" in str(x) and "failed" in str(x) and "the merchant second" in str(x) for x in lines), "X: no failed second in the log")
    K.notes.append("X log tail: " + " | ".join(str(x) for x in list(lines)[-6:]))
    P("CfgPub").shutdown()


# ====================================================================================================== E: the ECS handlers
def run_ecs(out):
    from jpype import JClass, JArray, JString, JInt, JObject
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    Unsafe = JClass("sun.misc.Unsafe")
    uf = Unsafe.class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def jf(c, n):
        k = c.class_
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(SCRATCH, "e-universe")]))
    HS = JClass("com.hypixel.hytale.server.core.HytaleServer")
    hs = U.allocateInstance(HS.class_)
    jf(HS, "eventBus").set(hs, JClass("com.hypixel.hytale.event.EventBus")(False))
    jf(HS, "instance").set(None, hs)
    CHM, COLL = JClass("java.util.concurrent.ConcurrentHashMap"), JClass("java.util.Collections")
    UNI = JClass("com.hypixel.hytale.server.core.universe.Universe")
    uni = U.allocateInstance(UNI.class_)
    pbu, wmap = CHM(), CHM()
    for n, v in (("playersByUuid", pbu), ("players", COLL.unmodifiableCollection(pbu.values())), ("worlds", wmap), ("worldsByUuid", CHM()),
                 ("unmodifiableWorlds", COLL.unmodifiableMap(wmap))):
        jf(UNI, n).set(uni, v)
    jf(UNI, "instance").set(None, uni)
    CT = JClass("com.hypixel.hytale.component.ComponentType")
    MOD = JClass("java.lang.reflect.Modifier")
    n_ = [0]

    def newct():
        v = U.allocateInstance(CT.class_)
        n_[0] += 1
        jf(CT, "index").set(v, JInt(n_[0]))
        return v

    def fill(cls, inst):
        for f in cls.class_.getDeclaredFields():
            if MOD.isStatic(f.getModifiers()):
                continue
            if f.getType() == CT.class_:
                f.setAccessible(True)
                f.set(inst, newct())
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EM.class_)
    fill(EM, em)
    jf(EM, "instance").set(None, em)
    c2t = JClass("java.util.HashMap")()
    NPCc = JClass("com.hypixel.hytale.server.npc.entities.NPCEntity")
    c2t.put(NPCc.class_, newct())
    jf(EM, "classToComponentType").set(em, c2t)
    IM = JClass("com.hypixel.hytale.server.core.modules.interaction.InteractionModule")
    im = U.allocateInstance(IM.class_)
    fill(IM, im)
    jf(IM, "instance").set(None, im)
    jf(UNI, "playerRefComponentType").set(uni, newct())
    P = lambda n: JClass(PKG + n)
    Cfg, Reg, Core, Eng, Use, Add, Site, Log = (P("MerchCfg"), P("MerchReg"), P("MerchCore"), P("MerchEng"), P("MerchUseSys"), P("MerchAddSys"),
                                                P("MerchSite"), P("MerchLog"))
    UUC, NPL, DNC, PDN, ITB, ITS, ITY, PRc = (JClass("com.hypixel.hytale.server.core.entity.UUIDComponent"),
                                              JClass("com.hypixel.hytale.server.core.entity.nameplate.Nameplate"),
                                              JClass("com.hypixel.hytale.server.core.modules.entity.component.DisplayNameComponent"),
                                              JClass("com.hypixel.hytale.server.core.modules.entity.component.PersistentDisplayName"),
                                              JClass("com.hypixel.hytale.server.core.modules.entity.component.Interactable"),
                                              JClass("com.hypixel.hytale.server.core.modules.interaction.Interactions"),
                                              JClass("com.hypixel.hytale.protocol.InteractionType"),
                                              JClass("com.hypixel.hytale.server.core.universe.PlayerRef"))
    for c in (UUC, NPL, DNC, PDN, ITB, ITS, NPCc, PRc):
        K.check(c.getComponentType() is not None, "E: %s.getComponentType resolves" % c.class_.getSimpleName())
    MS, MB, MC, FP = (JClass(FAKE_PKG + ".MapStore"), JClass(FAKE_PKG + ".MapBuffer"), JClass(FAKE_PKG + ".MapChunk"), JClass(FAKE_PKG + ".FakePr"))
    Ref, UUID, Paths = JClass("com.hypixel.hytale.component.Ref"), JClass("java.util.UUID"), JClass("java.nio.file.Paths")
    st = U.allocateInstance(MS.class_)
    st.comps, st.removed, st.ensured = JClass("java.util.HashMap")(), JClass("java.util.ArrayList")(), JClass("java.util.ArrayList")()
    st.ensureVal = U.allocateInstance(ITB.class_)
    W = JClass("com.hypixel.hytale.server.core.universe.world.World")
    w = U.allocateInstance(W.class_)
    jf(W, "name").set(w, JString("default"))
    ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    es = U.allocateInstance(ES.class_)
    for f in ES.class_.getDeclaredFields():
        if f.getType() == W.class_:
            f.setAccessible(True)
            f.set(es, w)
    st.ext = es
    K.check(str(Eng.worldOf(st)) == "default", "E: the REAL MerchEng.worldOf reads the store's world")
    # the registry: zone1 merchant U1 with ghost G1
    mods = os.path.join(SCRATCH, "e-mods")
    os.makedirs(mods, exist_ok=True)
    Cfg.load(Paths.get(mods))
    Reg.DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMerchants", "merchants"))
    sites = Reg.sites("default")
    s = Site()
    u1, g1 = str(UUID.randomUUID()), str(UUID.randomUUID())
    s.zone, s.uuid, s.x, s.y, s.z = "zone1", u1, -50, 65, 5
    s.addGhost(g1, 10 ** 13)
    Reg.add(sites, s)
    Reg.save("default")
    Core.reindex("default", sites)
    sim, slog, conts, loaded = make_sim(default_state())
    Eng.API = sim

    def npc(uuid_s, role, plate):
        r = Ref(st, 100 + len(st.comps))
        st.putComponent(r, UUC.getComponentType(), UUC(UUID.fromString(uuid_s)))
        n = U.allocateInstance(NPCc.class_)
        jf(NPCc, "roleName").set(n, JString(role))
        st.putComponent(r, NPCc.getComponentType(), n)
        if plate is not None:
            st.putComponent(r, NPL.getComponentType(), NPL(plate))
        return r
    r1 = npc(u1, "Temple_Klops", "Traveling Merchant")
    rg = npc(g1, "Temple_Klops", "Traveling Merchant")
    ro = npc(str(UUID.randomUUID()), "Temple_Klops", "Traveling Merchant")
    rv = npc(str(UUID.randomUUID()), "Temple_Klops", None)
    K.check(str(Eng.uuidOf(st, r1)) == u1 and str(Eng.roleOf(st, r1)) == "Temple_Klops" and str(Eng.plateOf(st, r1)) == "Traveling Merchant"
            and Eng.plateOf(st, rv) is None, "E: the REAL uuidOf / roleOf / plateOf on a stand-in store")
    n_set = int(Eng.prepare(st, rv, "Traveling Merchant"))
    its = st.getComponent(rv, ITS.getComponentType())
    K.check(n_set >= 4 and str(st.getComponent(rv, NPL.getComponentType()).getText()) == "Traveling Merchant" and st.getComponent(rv, DNC.getComponentType()) is not None
            and st.getComponent(rv, PDN.getComponentType()) is not None and st.getComponent(rv, ITB.getComponentType()) is not None
            and str(its.getInteractionId(ITY.Use)) == "*UseNPC" and str(its.getInteractionHint()) == "server.interactionHints.trade",
            "E: the REAL MerchEng.prepare: name (3 components), Interactable, Use = *UseNPC, the trade hint (%d set)" % n_set)
    K.check(int(Eng.prepare(st, rv, "Traveling Merchant")) == 0, "E: prepare twice changes nothing")
    nof = jf(ITS, "isNetworkOutdated")
    nof.setBoolean(its, False)
    Eng.prepare(st, rv, "Traveling Merchant")
    K.check(not nof.getBoolean(its), "E: FIX prepare() leaves an unchanged trade hint alone (Interactions not marked network-outdated every second)")
    its.setInteractionHint("x")
    K.check(int(Eng.prepare(st, rv, "Traveling Merchant")) == 1 and str(its.getInteractionHint()) == "server.interactionHints.trade",
            "E: FIX prepare() restores a changed hint")
    jf(NPCc, "roleName").set(st.getComponent(rv, NPCc.getComponentType()), JString("Temple_Klops"))
    st.comps.get(rv).remove(NPL.getComponentType())
    st.comps.get(rv).remove(DNC.getComponentType())
    def mb0():
        b_ = U.allocateInstance(MB.class_)
        b_.removed = JClass("java.util.ArrayList")()
        return b_
    add = Add()
    K.check(add.getQuery() is not None, "E: MerchAddSys query = NPCEntity")
    AR = JClass("com.hypixel.hytale.component.AddReason")
    for ref_, want, what in ((r1, False, "the current merchant kept"), (rg, True, "the ghost removed"), (ro, True, "an orphan (our role + name) removed"),
                             (rv, False, "a nameless temple Klops kept")):
        cb = U.allocateInstance(MB.class_)
        cb.removed = JClass("java.util.ArrayList")()
        add.onEntityAdded(ref_, AR.LOAD, st, cb)
        K.check((cb.removed.size() == 1) == want, "E: MerchAddSys: %s" % what)
    K.check(not s.hasGhost(g1), "E: the removed ghost left the line")
    cbn = mb0()
    add.onEntityAdded(r1, AR.LOAD, None, cbn)
    K.check(cbn.removed.size() == 0 and not Add.FAILED_ONCE, "E: an add with no store / world is ignored (never removes)")
    # the use system
    use = Use()
    pr = U.allocateInstance(FP.class_)
    for f in PRc.class_.getDeclaredFields():
        if str(f.getType().getName()) == "java.util.UUID":
            f.setAccessible(True)
            f.set(pr, UUID.randomUUID())
    rp = Ref(st, 900)
    st.putComponent(rp, PRc.getComponentType(), pr)
    ch = U.allocateInstance(MC.class_)
    ch.ref = rp
    UEP = JClass("com.hypixel.hytale.server.core.event.events.ecs.UseEntityEvent$Pre")
    e = UEP(ITY.Use, None, r1)
    use.handle(0, ch, st, mb0(), e)
    K.check(e.isCancelled() and len(slog["opened"]) == 1, "E: MerchUseSys: F on our merchant -> vanilla use cancelled, the page opens next tick")
    Core.GHOSTS.put(str(Eng.uuidOf(st, ro)), "default")
    e2 = UEP(ITY.Use, None, ro)
    use.handle(0, ch, st, mb0(), e2)
    K.check(e2.isCancelled() and pr.msgs is not None and "packing up" in str(pr.msgs[-1]), "E: F on an old one (ghost) -> cancelled + a line")
    e3 = UEP(ITY.Use, None, rv)
    use.handle(0, ch, st, mb0(), e3)
    K.check(not e3.isCancelled() and len(slog["opened"]) == 1, "E: F on another NPC: untouched")
    e4 = UEP(ITY.Use, None, r1)
    e4.setCancelled(True)
    use.handle(0, ch, st, mb0(), e4)
    K.check(len(slog["opened"]) == 1, "E: an already cancelled use is left alone")
    ch.boom = True
    use.handle(0, ch, st, mb0(), UEP(ITY.Use, None, r1))
    K.check(Use.FAILED_ONCE, "E: a broken use is logged once")
    K.save()


# ====================================================================================================== R: restarts
def run_restart(step, out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR, FAKE_DIR])
    sp = os.path.join(SCRATCH, "r-state.json")
    state = json.load(open(sp)) if os.path.isfile(sp) else default_state()
    P = lambda n: JClass(PKG + n)
    Cfg, Reg, Core, Eng, Log = P("MerchCfg"), P("MerchReg"), P("MerchCore"), P("MerchEng"), P("MerchLog")
    Paths = JClass("java.nio.file.Paths")
    br, bst, fns = bridge_setup()
    mods = os.path.join(SCRATCH, "r-mods")
    Cfg.load(Paths.get(mods))
    Reg.DIR = Paths.get(os.path.join(mods, "Skyy_SkyyMerchants", "merchants"))
    sim, slog, conts, loaded = make_sim(state)
    Eng.API = sim
    t0 = 2 * 10 ** 12 + {"R1": 0, "R2": 60000, "R3": 120000, "R4": 180000}[step]

    def per_zone():
        return len(ents_of(state, 1)), len(ents_of(state, 2))

    def reg_uuids():
        txt = open(os.path.join(mods, "Skyy_SkyyMerchants", "merchants", "default.tsv"), encoding="utf-8").read()
        return dict((l.split("\t")[0], l.split("\t")) for l in txt.splitlines() if l and not l.startswith("#"))
    if step == "R1":
        for k in range(3):
            Core.second("default", t0 + k * 1000)
        K.check(per_zone() == (1, 1) and int(Core.N[0]) == 2, "R1: a fresh start: one merchant per zone (%s)" % (per_zone(),))
    elif step == "R2":
        before = reg_uuids()
        orphan = "11111111-0000-4000-8000-000000000001"
        state["ents"][orphan] = {"w": "default", "role": "Temple_Klops", "name": "Traveling Merchant", "x": -120.0, "y": 65.0, "z": 0.0}
        for u in list(state["ents"]):     # the chunks load: the RefSystem sees every NPC
            e = state["ents"][u]
            if int(Core.onAdded("default", u, e["role"], e["name"])) == 1:
                del state["ents"][u]
        K.check(orphan not in state["ents"], "R2: a crash orphan (our role + name, no line) is removed when it loads")
        for k in range(25):
            Core.second("default", t0 + k * 1000)
        after = reg_uuids()
        K.check(per_zone() == (1, 1) and int(Core.N[0]) == 0 and int(Core.N[2]) == 0 and before["zone1"][1] == after["zone1"][1] and before["zone2"][1] == after["zone2"][1],
                "R2: restart, the engine kept them: re-attached by UUID, nothing spawned, still 1 per zone")
    elif step == "R3":
        before = reg_uuids()
        lost = dict(state["ents"])
        state["ents"] = {}                  # the engine did not save the NPCs
        Core.second("default", t0)
        Core.second("default", t0 + 10000)
        K.check(per_zone() == (0, 0), "R3: the engine lost them: nothing for 15 s (they may still be loading)")
        Core.second("default", t0 + 16000)
        after = reg_uuids()
        same = all(before[z][2:5] == after[z][2:5] for z in ("zone1", "zone2"))
        K.check(per_zone() == (1, 1) and same and int(Core.N[2]) == 2 and before["zone1"][1] != after["zone1"][1],
                "R3: back at the SAME spots after 15 s (new UUIDs, the old ones ghosts)")
        for u, e in lost.items():            # an old one loads late after all
            state["ents"][u] = e
            if int(Core.onAdded("default", u, e["role"], e["name"])) == 1:
                del state["ents"][u]
        K.check(per_zone() == (1, 1), "R3: the late old ones are removed when they load - never 2 of one zone")
        Core.second("default", t0 + 17000)
        K.check(all(len(reg_uuids()[z][9]) == 0 for z in ("zone1", "zone2")), "R3: the ghosts are gone from the lines")
    else:
        before = reg_uuids()
        for u in list(state["ents"]):
            e = state["ents"][u]
            Core.onAdded("default", u, e["role"], e["name"])
        for k in range(20):
            Core.second("default", t0 + k * 1000)
        after = reg_uuids()
        K.check(per_zone() == (1, 1) and int(Core.N[0]) + int(Core.N[1]) + int(Core.N[2]) == 0 and before["zone1"][1] == after["zone1"][1],
                "R4: restart again: kept, nothing new, 1 per zone")
    json.dump(state, open(sp, "w"), indent=1)
    K.save()


# ====================================================================================================== D: start twice on live data
def run_live(step, out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    home = os.path.join(SCRATCH, "live")
    P = lambda n: JClass(PKG + n)
    Paths = JClass("java.nio.file.Paths")
    HL = JClass("com.hypixel.hytale.logger.HytaleLogger")
    # setup()'s order: config load, registry folder, the kit
    P("MerchCfg").load(Paths.get(home))
    P("MerchReg").DIR = Paths.get(home).resolve("Skyy_SkyyMerchants").resolve("merchants")
    P("CfgPub").start(Paths.get(home), HL.get("SkyyMerchLive"))
    K.check(len(P("MerchCfg").ZONES) == 4 and int(P("MerchCfg").MOVE_S) == 1200, "D %s: config read (4 zones, 1200 s)" % step)
    K.check(P("MerchReg").sites("default") is not None, "D %s: the registry of world default reads (none yet)" % step)
    P("CfgPub").shutdown()
    P("MerchReg").flushAll()
    K.save()


def tree_hash(root):
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


# ====================================================================================================== P / B / AA
def run_perm(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.SERVER_JAR, JAR])
    AC = JClass("com.hypixel.hytale.server.core.command.system.AbstractCommand")
    fld = AC.class_.getDeclaredField("permissionGroups")
    fld.setAccessible(True)
    for cn in ("MerchAdminCmd", "MerchAdminArgCmd", "MerchAdminArg2Cmd"):
        c = JClass(PKG + cn)()
        perm = c.getPermission()
        groups = fld.get(c)
        K.check(perm is not None and NODE in str(perm), "P. %s requires %s (%s)" % (cn, NODE, perm))
        K.check(groups is not None and len(groups) == 0, "P. %s permission groups empty" % cn)
        if cn == "MerchAdminCmd":
            rec = c.getPermissionGroupsRecursive()
            leak = [str(k) for k in rec.keySet() if rec.get(k) is not None and any(NODE in str(x) for x in rec.get(k))]
            K.check(not leak and str(c.getName()) == "merchantadmin", "P. /merchantadmin gives %s to no group (leak %s)" % (NODE, leak))
    m = JClass(PKG + "MerchantsCmd")()
    K.check(list(fld.get(m)) == ["hytale:Adventurer"] and str(m.getName()) == "merchants" and "rumours" in [str(a) for a in m.getAliases()],
            "P. /merchants (alias /rumours) = hytale:Adventurer")
    K.save()


def bytecode_calls(cp, cls, meth, sig=None):
    from jpype import JClass
    cc = cp.get(cls)
    ms = [m for m in cc.getClassFile2().getMethods() if str(m.getName()) == meth and (sig is None or sig in str(m.getDescriptor()))]
    calls = []
    for mi in ms:
        cpool, it = mi.getConstPool(), mi.getCodeAttribute().iterator()
        while it.hasNext():
            p = it.next()
            op = it.byteAt(p)
            if op in (0xb6, 0xb7, 0xb8, 0xb9):
                i = it.u16bitAt(p + 1)
                if cpool.getTag(i) == JClass("javassist.bytecode.ConstPool").CONST_InterfaceMethodref:
                    calls.append(str(cpool.getInterfaceMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getInterfaceMethodrefName(i)) + str(cpool.getInterfaceMethodrefType(i)))
                else:
                    calls.append(str(cpool.getMethodrefClassName(i)).rsplit(".", 1)[-1] + "." + str(cpool.getMethodrefName(i)) + str(cpool.getMethodrefType(i)))
            elif op == 0xbb:
                calls.append("new " + str(cpool.getClassInfo(it.u16bitAt(p + 1))).rsplit(".", 1)[-1])
            elif op in (0x12, 0x13):
                i = it.byteAt(p + 1) if op == 0x12 else it.u16bitAt(p + 1)
                if cpool.getTag(i) == JClass("javassist.bytecode.ConstPool").CONST_String:
                    calls.append("ldc " + str(cpool.getStringInfo(i)))
    return calls


def run_bytecode(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    full = lambda cls, m, sig=None: bytecode_calls(cp, cls, m, sig)
    calls = [c.split("(")[0] for c in full(PKG + "SkyyMerchantsPlugin", "setup")]
    want = ["MerchCfg.load", "CfgPub.start", "new MerchantsCmd", "CommandRegistry.registerCommand", "new MerchAdminCmd", "CommandRegistry.registerCommand",
            "new MerchUseSys", "ComponentRegistryProxy.registerSystem", "new MerchAddSys", "ComponentRegistryProxy.registerSystem", "new MerchTimer",
            "ScheduledExecutorService.scheduleWithFixedDelay"]
    pos, ok = 0, True
    for x in want:
        try:
            pos = calls.index(x, pos) + 1
        except ValueError:
            ok = False
            break
    K.check(ok and calls.count("ComponentRegistryProxy.registerSystem") == 2, "B: setup() = config, kit, 2 commands, 2 systems (once each), the 1 s timer: %s" % calls)
    van = [c for c in full("com.hypixel.hytale.builtin.triggervolumes.effect.builtin.SpawnNpcEffect", "execute") if "spawnNPC" in c]
    ours = [c for c in full(PKG + "MerchEng", "spawn") if "spawnNPC" in c]
    K.check(ours and ours == van, "B: MerchEng.spawn = vanilla SpawnNpcEffect's NPCPlugin.spawnNPC: %s vs %s" % (ours, van))
    rm = full(PKG + "MerchEng", "remove")
    K.check(any(c.startswith("EntityStore.getRefFromUUID") for c in rm) and any(c.startswith("Store.removeEntity") for c in rm), "B: remove = getRefFromUUID + Store.removeEntity(REMOVE)")
    rbs = full("com.hypixel.hytale.server.npc.systems.RoleBuilderSystem", "onEntityAdd")
    K.check("ldc *UseNPC" in rbs, "B: engine fact: RoleBuilderSystem gives every NPC Use = *UseNPC")
    uei = full("com.hypixel.hytale.server.core.modules.interaction.interaction.config.client.UseEntityInteraction", "firstRun")
    K.check("new UseEntityEvent$Pre" in uei and any(c.startswith("UseEntityEvent$Pre.isCancelled") for c in uei), "B: engine fact: UseEntityInteraction fires UseEntityEvent$Pre and honours its cancel")
    emi = full("com.hypixel.hytale.server.core.command.commands.world.entity.EntityMakeInteractableCommand", "execute")
    pre = full(PKG + "MerchEng", "prepare")
    K.check(any(c.startswith("Store.ensureComponent") for c in emi) and any(c.startswith("Store.ensureComponent") for c in pre), "B: prepare = Store.ensureComponent(Interactable) like the vanilla command")
    tk = full(PKG + "MerchAddSys", "onEntityAdded")
    K.check(any(c.startswith("CommandBuffer.tryRemoveEntity") for c in tk), "B: the add hook removes through the CommandBuffer (never during the store's processing)")
    us_ = full(PKG + "MerchCore", "use")
    K.check(any(c.startswith("MerchEng.exec") for c in us_) and not any("openCustomPage" in c for c in full(PKG + "MerchUseSys", "handle")),
            "B: the use system never opens a page itself (World.execute -> MerchOpen)")
    K.save()


def run_audit(out):
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
    for flag, fn in (("--mkfake", lambda: run_mkfake(arg("--mkfake"))), ("--core", lambda: run_core(arg("--out"))),
                     ("--ecs", lambda: run_ecs(arg("--out"))), ("--restart", lambda: run_restart(arg("--restart"), arg("--out"))),
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
        check(p.returncode == 0 and os.path.isfile(os.path.join(FAKE_DIR, FAKE_PKG, "MapStore.class")), "F: the stand-ins were generated")
        for label, flag in (("core", "--core"), ("ecs", "--ecs"), ("perm", "--perm"), ("bytecode", "--bytecode")):
            out = os.path.join(SCRATCH, "%s.json" % label)
            child(env, flag, "--out", out)
            take(out, label)
        for step in ("R1", "R2", "R3", "R4"):
            out = os.path.join(SCRATCH, "restart-%s.json" % step)
            child(env, "--restart", step, "--out", out)
            take(out, "restart " + step)
        home = os.path.join(SCRATCH, "live")
        if os.path.isdir(LIVE):
            shutil.copytree(LIVE, home)
        else:
            os.makedirs(home)
        h0 = tree_hash(home)
        check(len(h0) > 0 and not os.path.exists(os.path.join(home, "Skyy_SkyyMerchants")), "D: live mod data copied (%d files), no merchants folder yet" % len(h0))
        out = os.path.join(SCRATCH, "live-1.json")
        child(env, "--live-step", "start1", "--out", out)
        take(out, "live start1")
        h1 = tree_hash(home)
        new = sorted(set(h1) - set(h0))
        changed = sorted(k for k in h0 if h1.get(k) != h0[k])
        check(new == [os.path.join("Skyy_SkyyMerchants", "config.properties")] and not changed,
              "D: start 1 writes only Skyy_SkyyMerchants/config.properties, every other file byte-identical (new %s changed %s)" % (new, changed))
        out = os.path.join(SCRATCH, "live-2.json")
        child(env, "--live-step", "start2", "--out", out)
        take(out, "live start2")
        h2 = tree_hash(home)
        check(h2 == h1, "D: start 2 changes nothing (%s)" % sorted(k for k in set(h1) | set(h2) if h1.get(k) != h2.get(k)))
        outa = os.path.join(SCRATCH, "audit.json")
        pa = child(env, "--audit", "--out", outa)
        check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
        if os.path.isfile(outa):
            a = json.load(open(outa))
            check(not a["refused"] and a["refs"] > 400 and a["classes"] == len(CLASSES),
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
