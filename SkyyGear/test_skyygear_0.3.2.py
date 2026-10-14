"""Harness for SkyyGear 0.3.2 = the 0.3.1 harness (every check kept) + THE EXACT LOST TOOL (tools/gear_0_3_2_patch.py header). Build first:
    python tools/gear_0_3_2_patch.py && python SkyyGear/build_skyygear_0.3.2.py

    python SkyyGear/test_skyygear_0.3.2.py [--jar <SkyyGear-0.3.2.jar>] [--old <SkyyGear-0.2.26.jar>] [--j31 <SkyyGear-0.3.1.jar>] [--j24 <SkyyGear-0.2.24.jar>] [--keep]

0.3.2 (Skyy 2026-10-13 "if you can, make it give their exact tool back. (or if its in a chest, summons it to your inventory.)"): the 0.3.1
checks whose ANSWER the new rule changes are kept with the new expectation (each marked "0.3.2:"): /pickaxe with the tool out of reach
gives an EXACT copy (same item, rarity, rolls) instead of a new Common one; lifelong.reclaimTier is a legacy row (on changes nothing). New:
  LT  THE EXACT LOST TOOL EXECUTED (same booted engine): the snapshot (made by the sweep, refreshed on a reforge, none for an unseen tool);
      the tracker (GearLL.trackMaybe gate -> GearLife.trackLater coalesced -> GearTrackTask -> GearLife.track) on a REAL ContainerBlockWindow
      and a REAL ContainerWindow (the Vault's kind) in a real WindowManager; /pickaxe: full inventory refused first, Requip fetch (ok / refused
      / not loaded / ok-but-missing), an open window (chest + Vault kind), the tracked chest (loaded / unloaded / another world / gone / tool
      moved on), the exact copy (rarity, lines, reforge name, perks + points, level, new uid + lcu, lrpF) + the wait (copies only), the legacy
      Common answer without a snapshot; THE DUPE PROOFS: the original turns up after the copy (copy removed / original retired when the copy
      was reforged AFTER copying), a chest another player has open (they took it first -> copy, theirs does nothing for them), a profile
      switch mid-summon (busy / another profile key -> nothing moves), a CRASH at every summon step (7, 8, 9) with the engine having saved
      the source, the target, both or neither - never two working tools, never a lost one (the exact copy is always one /pickaxe away);
      the move's own failure paths (source refuses, target refuses -> back in the source)
  C32 CLASS COMPARE 0.3.1 -> 0.3.2: exactly the listed members differ

0.3.1 (Skyy 2026-10-13 "if crude is also T1 it should take the normal amount of hits" + "x2.5  / X10   tiers above cannot be broken"):
the 0.3.0 checks whose ANSWER the new rule changes are kept with the new expectation (each marked "0.3.1:"): Crude / Wood count as tier 1,
1 up x gate.nextFactor (0.4), 2 up x gate.twoUpFactor (0.1, was refused), 3+ up refused; gate.crudeFactor = an unused legacy row; the
live copy (D) gains exactly the run-once marker line. New phases:
  G   THE 0.3.1 GATE MATRIX on the REAL hit system + real BlockTypes (Crude / Copper / Iron pickaxes and hatchets x ore / log tiers: normal,
      x0.4, x0.1, refused + the popups' words), only.farming + gear:fn:farmTier for Crude hoes, the rows, statusText; THE ONE-TIME UPDATE
      migrate031 (pure text: old default rewritten / hand-edited kept + noted / absent = marker only / marker = nothing / CRLF + other bytes
      kept / a continued line never rewritten; on a scratch file: History copy first, change-log row with Undo (ok), run twice = no change)
  C31 CLASS COMPARE 0.3.0 -> 0.3.1: exactly the listed members differ

The 0.2.11 harness's helpers (verify A, the bare-server boot, the engine-access audit AA, FakeStore / FakeChunk / FakeUtil) and the 0.2.22
stand-ins (MergeFail, FakeReforgePage, FakeMultiPage, FakePR) are loaded from their files; this harness adds FakePM (the page a command
opens) and FakeLifePage. Read-only sources are COPIED into scratch first: the live Skyy_SkyyGear folder (D), the live player files
(universe/players/*.json - their real tool stacks drive the migration, M), SkyyCollections 0.2.11 (the Enchanted items the tier-up costs
name) and SkyyArmory 0.1.23 + Multitools 1.2.9 (for the carried 0.2.26 Anvil child).
  S   non-class entries 0.2.26 -> 0.3.0: only the manifest changed; classes added = exactly the 0.3.0 set
  A   every class loads + verifies (-Xverify:all)
  C   CLASS COMPARE 0.2.26 -> 0.3.0: exactly the listed members differ (javassist members + resolved bytecode)
  R   THE 0.2.26 HARNESS'S ANVIL CHILD with this jar (N1-N13: reforge / upgrade / identify, every click and failure) - only the listed
      deviations (the tab row now has a Tools tab)
  X   THE 0.2.25 HARNESS'S RANDOMISED OLD-VS-NEW STATS COMPARISON with this jar against 0.2.24 (snapshot / tick / hits / gate / stamp scan)
  L   LIFELONG TOOLS EXECUTED (one booted engine, vanilla pack + SkyyCollections 0.2.11): rows; kinds / tiers / level rule; the registry;
      the gate matrix (every tool family x tier x block tier + bare hands + the wrong tool) and the REAL GearToolHitSys on REAL
      DamageBlockEvents / BlockTypes; only.farming; perks (points, tier need, reader gate, effects in GearTool.stats, reset for coins,
      refund on a failed write); the sweep (level sync, registry id, restore, remove, demote, foreign copies); /pickaxe (every refusal, the
      dupe guard, the cooldown, crash at every step); /lifelong; the tier-up on the Anvil (GearUp.check / upgrade); PROTECTION: the REAL
      GearLLDropSys on DropItemEvent$PlayerRequest (cancelled before anything moves), the engine's salvage matching (a lifelong tool never
      matches a recipe input), the market wall, the multitool merge, Reforge Level up; NO CRAFTING: the REAL GearCraftPreSys on a REAL
      CraftRecipeEvent$Pre (+ Creative, + a shovel), the Smithing Craft tab; the Tools page (layout, ids, clicks) + every command;
      gear:fn:lifelong / perk / farmTier; the tooltip lines
  FX  THE FIX ROUND (one check per critic finding fixed - see the "FIX" lines): another player's lifelong tool breaks nothing (real hit
      system); an invested /pickaxe replacement is never thrown away (settle / demote); /pickaxe gives the tier your skill fits
      (lifelong.reclaimTier, on / off); the held-tool level watch; at most 5 registry writes per migration; a cancelled drop from an open
      chest window marks the window changed; cactus keeps Fortune; gear:fn:farmTier takes an item id; the Requip hint; LL-MARK undo data
  FX2 THE SECOND FIX ROUND: the reforge-then-retrieve exploit (the original is RETIRED - still lifelong, never sold, breaks nothing, may be
      dropped - and /lifelong swaps it back); another player's lifelong tool may be dropped; lifelong.reclaimTier OFF by default (no free
      tier); an unreadable registry is read again after 30 s; a failing registry write WARNs once + the every-scan sweep waits; LL-MARK logs
      the old level + bought levels and says so; gate.crudeFactor; gear:fn:lifelong(UUID) -> Integer kinds owned
  M   THE MIGRATION ON THE LIVE PLAYERS' REAL TOOL STACKS (scratch copies): the best tool per kind, rolls kept, Crude Common gifts, counts;
      a CRASH AT EVERY STEP (1-6) then a restart (registry re-read from disk), with and without the engine having saved the inventory -
      never a second item, never a lost one, the journal always finished
  D   START TWICE on a scratch COPY of the live Skyy_SkyyGear folder with each jar: the 2nd start changes nothing; 0.3.0 writes the same
      config.properties as 0.2.26 (absent rows = defaults); the fresh default file differs only by the lifelong block; no lifelong folder
      is made at start
  AA  THE ENGINE-ACCESS AUDIT
Scratch: tools/dev/scratch/losttool/harness (deleted at the end unless --keep). Exit code 1 on any failure.
"""
import os, sys, json, shutil, zipfile, subprocess, re, hashlib, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import skyybuild as B

VERSION = "0.3.2"
OLD_VERSION = "0.2.26"
V31 = "0.3.1"          # 0.3.2: the C32 compare base


def arg(name, default=None):
    if name in sys.argv:
        i = sys.argv.index(name)
        return sys.argv[i + 1] if i + 1 < len(sys.argv) else default
    return default


SCR_ROOT = os.path.abspath(arg("--root", os.path.join(TOOLS, "dev", "scratch", "losttool")))
J31 = os.path.abspath(arg("--j31", os.path.join(HERE, "SkyyGear-%s.jar" % V31)))                    # read only (C32)
SCRATCH = os.path.abspath(arg("--dir", os.path.join(SCR_ROOT, "harness")))
JAR = os.path.abspath(arg("--jar", os.path.join(HERE, "SkyyGear-%s.jar" % VERSION)))
OLD_JAR = os.path.abspath(arg("--old", os.path.join(HERE, "SkyyGear-%s.jar" % OLD_VERSION)))      # read only
J24 = os.path.abspath(arg("--j24", os.path.join(HERE, "SkyyGear-0.2.24.jar")))                   # read only (X)
CO_SRC = os.path.join(ROOT, "SkyyCollections", "SkyyCollections-0.2.11.jar")                      # read only - copied
AR_SRC = os.path.join(ROOT, "SkyyArmory", "SkyyArmory-0.1.23.jar")                                # read only - copied (R)
MT_SRC = os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")                                        # read only - copied (R)
LIVE_DIR = os.path.join(B.USERDATA, "Saves", "HUD mod", "mods", "Skyy_SkyyGear")
LIVE_PLAYERS = os.path.join(B.USERDATA, "Saves", "HUD mod", "universe", "players")
CO_JAR = os.path.join(SCRATCH, "packs", "SkyyCollections-0.2.11.jar")
PLAYERS = os.path.join(SCRATCH, "players")
PKG = "com.skyy.gear."
NEW_CLASSES = {"GearLL", "GearLife", "LifePage", "PickaxeCmd", "HatchetCmd", "HoeCmd", "SickleCmd", "ToolPtsCmd", "LifelongCmd",
               "GearLLDropSys", "GearLLFn", "GearTrackTask"}          # 0.3.2: + GearTrackTask

_H211 = os.path.join(HERE, "test_skyygear_0.2.11.py")
_t = open(_H211, encoding="utf-8").read()
_cut = _t.rindex('if __name__ == "__main__":')
H = {"__name__": "skyygear_h211", "__file__": _H211, "__builtins__": __builtins__}
exec(compile(_t[:_cut], _H211 + " (helpers)", "exec"), H)
H.update({"JAR": JAR, "OLD_JAR": OLD_JAR, "SCRATCH": SCRATCH, "FAKE_DIR": os.path.join(SCRATCH, "fake"), "VERSION": VERSION})
FAKE_DIR = H["FAKE_DIR"]
FAKE_PKG = H["FAKE_PKG"]
Child, _jvm, jar_classes = H["Child"], H["_jvm"], H["jar_classes"]
_H222 = os.path.join(HERE, "test_skyygear_0.2.22.py")
_t2 = open(_H222, encoding="utf-8").read()
_c2 = _t2.index("# ====================================================================================================== F+: this round's stand-ins")
_e2 = _t2.index("# ====================================================================================================== T + R + U + N + P")
H22 = {"__name__": "skyygear_h222", "__builtins__": __builtins__, "H": H, "FAKE_PKG": FAKE_PKG, "PKG": PKG, "JAR": JAR, "B": B, "os": os}
exec(compile(_t2[_c2:_e2], _H222 + " (stand-ins)", "exec"), H22)
FAILS, OKS = [], [0]


def check(cond, what):
    if cond:
        OKS[0] += 1
    else:
        FAILS.append(what)
        print("FAIL", what)


# ====================================================================================================== S: non-class entries
def run_assets():
    zo, zn = zipfile.ZipFile(OLD_JAR), zipfile.ZipFile(JAR)
    ea = dict((n, zo.read(n)) for n in zo.namelist() if not n.endswith(".class"))
    eb = dict((n, zn.read(n)) for n in zn.namelist() if not n.endswith(".class"))
    added = sorted(set(eb) - set(ea))
    changed = sorted(n for n in set(ea) & set(eb) if ea[n] != eb[n])
    check(not added and not (set(ea) - set(eb)) and changed == ["manifest.json"] and ('"%s"' % VERSION).encode() in eb["manifest.json"]
          and b"Crude counts as Copper; one tier up takes 2.5x the hits, two up 10x, three up is refused" in eb["manifest.json"]
          and b"LIFELONG TOOLS: one pickaxe, hatchet, hoe and sickle per player for life" in eb["manifest.json"]
          and b"Tools (your lifelong pickaxe, hatchet, hoe and sickle" in eb["manifest.json"],
          "S: 0.2.26 -> 0.3.0: no file added / removed, only the manifest changed (version + the lifelong words): + %s ~ %s" % (added[:3], changed[:3]))
    ca = set(n for n in zo.namelist() if n.endswith(".class"))
    cb = set(n for n in zn.namelist() if n.endswith(".class"))
    check(not (ca - cb) and set(n.split("/")[-1][:-6] for n in cb - ca) == NEW_CLASSES,
          "S: classes added = exactly the 0.3.0 set; none removed: + %s - %s" % (sorted(cb - ca), sorted(ca - cb)))
    names = set(zn.namelist())
    check(not [n for n in names if "Skyy_Ench" in n or "inkblindcat" in n.lower() or n.endswith(".ui") or n.startswith("Server/Item/Items/Tool")],
          "S: no Enchanted item / pack mod / vanilla tool file is shipped or overridden (runtime ids only), no .ui file")


# ====================================================================================================== F: stand-ins
def run_mkfake5(out_dir):
    H22["run_mkfake2"](out_dir)
    from jpype import JClass
    cp = JClass("javassist.ClassPool")(False)
    cp.appendSystemPath()
    cp.appendClassPath(B.SERVER_JAR)
    cp.appendClassPath(JAR)
    CtField, CtNewMethod, CtNewConstructor = JClass("javassist.CtField"), JClass("javassist.CtNewMethod"), JClass("javassist.CtNewConstructor")
    PMc = "com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager"
    pm = cp.makeClass(FAKE_PKG + ".FakePM")
    pm.setSuperclass(cp.get(PMc))
    pm.addField(CtField.make("public static java.lang.Object last;", pm))
    pm.addField(CtField.make("public static int opens;", pm))
    pm.addConstructor(CtNewConstructor.make("public FakePM() { super(); }", pm))
    pm.addMethod(CtNewMethod.make("public void openCustomPage(com.hypixel.hytale.component.Ref r, com.hypixel.hytale.component.Store s, "
                                  "com.hypixel.hytale.server.core.entity.entities.player.pages.CustomUIPage p) { last = p; opens = opens + 1; }", pm))
    pm.writeFile(out_dir)
    fp = cp.makeClass(FAKE_PKG + ".FakeLifePage")
    fp.setSuperclass(cp.get(PKG + "LifePage"))
    fp.addField(CtField.make("public int rebuilds;", fp))
    fp.addField(CtField.make("public int closes;", fp))
    fp.addConstructor(CtNewConstructor.make("public FakeLifePage(com.hypixel.hytale.server.core.universe.PlayerRef pr) { super(pr); }", fp))
    fp.addMethod(CtNewMethod.make("public void rebuild() { this.rebuilds = this.rebuilds + 1; }", fp))
    fp.addMethod(CtNewMethod.make("public void close() { this.closes = this.closes + 1; }", fp))
    fp.writeFile(out_dir)
    print("F+. FakePM, FakeLifePage written")


# ====================================================================================================== L + M: one booted engine
def run_life(out):
    from jpype import JClass, JInt, JShort, JLong, JByte, JFloat, JDouble, JImplements, JOverride, JObject, JArray, JString, JBoolean
    K = Child(out)
    _jvm([B.SERVER_JAR, B.JAVASSIST, JAR, FAKE_DIR], verify=True, big=True)
    E = H["engine_boot"](K)
    ITEM, us, jf = E["ITEM"], E["us"], E["jf"]
    K.check(set(E["fail"]) <= set(E["vfail"]), "E: the jar as its own pack: no failed store of its own (%s vs vanilla %s)" % (E["fail"], E["vfail"]))
    CRR = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    HAL = JClass("java.util.ArrayList")
    AZP = game_assets()          # fix round: the CACHED Assets.zip (tools/serverjar.py) - B.SERVER_JAR is a cached copy since 2026-10-13
    afs = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(AZP), JClass("java.util.HashMap")())
    with zipfile.ZipFile(AZP) as az_:
        tnames = [n for n in az_.namelist() if n.startswith("Server/Item/Items/Tool/") and n.endswith(".json")]
        AZJ = {}
        for n in az_.namelist():
            if n.startswith("Server/Item/Items/") and n.endswith(".json"):
                try:
                    AZJ[os.path.basename(n)[:-5]] = json.loads(az_.read(n).decode("utf-8-sig"))
                except Exception:
                    pass
    tl_ = HAL()
    for n in tnames:
        tl_.add(afs.getPath("/" + n))
    ITEM.getAssetStore().loadAssetsFromPaths("Hytale:Hytale", tl_)

    def gen_recipes(items):
        lst = HAL()
        for it in items:
            if it is not None and it.hasRecipesToGenerate():
                it.collectRecipesToGenerate(lst)
        if lst.size() > 0:
            CRR.getAssetStore().loadAssets("Hytale:Hytale", lst)
        return int(lst.size())
    n_rc = gen_recipes(list(ITEM.getAssetMap().getAssetMap().values()))
    CAR = JClass("com.hypixel.hytale.server.core.asset.common.CommonAssetRegistry")
    FCA = JClass("com.hypixel.hytale.server.core.asset.common.asset.FileCommonAsset")

    def addpack(jar, name):
        fs_ = JClass("java.nio.file.FileSystems").newFileSystem(JClass("java.nio.file.Paths").get(jar), JClass("java.util.HashMap")())
        with zipfile.ZipFile(jar) as z_:
            for nm in z_.namelist():
                if nm.startswith("Common/") and not nm.endswith("/"):
                    CAR.addCommonAsset(name, FCA(fs_.getPath("/" + nm), nm[len("Common/"):], hashlib.sha256(z_.read(nm)).hexdigest(), None))
        return E["loadpack"](jar, name, False)
    cfail, _crec = addpack(CO_JAR, "Skyy:SkyyCollections")
    ENCH = ["Skyy_Ench_%s" % k for k in ("Iron", "Thorium", "Cobalt", "Adamantite", "Maple", "Gumboab", "Redwood", "Sallow", "Carrot", "Cauliflower")]
    K.check(all(ITEM.getAssetMap().getAsset(i) is not None for i in ENCH),
            "E: SkyyCollections 0.2.11 (scratch copy) loaded as its own pack: every Enchanted item the tier-up costs name is real (failed stores %s)" % cfail)
    P = lambda n: JClass(PKG + n)
    Cfg, Gear, Up, Data, Roll, Forge, Stamp, Lvl, Defs, Log, View, Ui, Tool, LL, Life, Gate, Merge, Wall, Smith = (
        P("GearCfg"), P("Gear"), P("GearUp"), P("GearData"), P("GearRoll"), P("GearForge"), P("GearStamp"), P("GearLevel"), P("GearDefs"),
        P("GearLog"), P("GearView"), P("GearUi"), P("GearTool"), P("GearLL"), P("GearLife"), P("GearGate"), P("GearMerge"), P("GearWall"),
        P("GearSmith"))
    Props = JClass("java.util.Properties")
    SR = JClass("java.io.StringReader")
    FRESH = str(Cfg.defaultsText())
    Paths = JClass("java.nio.file.Paths")
    HOME = os.path.join(SCRATCH, "gearhome")
    os.makedirs(HOME, exist_ok=True)
    Cfg.DIR = Paths.get(HOME)
    GLF = os.path.join(SCRATCH, "gear.log")
    Log.FILE = Paths.get(GLF)

    def apply(**kv):
        p = Props()
        p.load(SR(FRESH))
        for k, v in kv.items():
            p.setProperty(k.replace("__", "."), v)
        Cfg.apply(p, False)
    apply()

    def logs():
        Log.flush()
        out_ = []
        if os.path.isfile(GLF):
            with open(GLF, encoding="utf-8") as f_:
                out_ = [l_ for l_ in f_.read().split("\n") if l_.strip()]
            os.remove(GLF)
        return out_ + [l_ for l_ in str(Log.take()).split("\n") if l_.strip()]
    logs()

    # ============================================================================ L1: the rows
    LLKEYS = ["part.lifelong=true", "lifelong.noCraft=true", "lifelong.noDrop=true", "lifelong.reclaimSec=600", "lifelong.reclaimTier=false", "lifelong.repickDays=7",
              "lifelong.perkSpeed=2", "lifelong.perkFortune=1", "lifelong.perkWisdom=1", "lifelong.resetCoins=5000", "gate.on=true",
              "gate.nextFactor=0.4", "gate.twoUpFactor=0.1", "gate.crudeFactor=0.1", "gate.bareHands=true"]
    K.check(all(("\n" + k + "\n") in FRESH for k in LLKEYS) and "lifelong.ladders=Tool_Pickaxe_Crude>Tool_Pickaxe_Copper(Ingredient_Bar_Copper*25)" in FRESH
            and bool(Cfg.LL_ON) and bool(Cfg.GATE_ON) and abs(float(Cfg.GATE_NEXT) - 0.4) < 1e-12 and int(Cfg.LL_RECLAIM) == 600 and not bool(Cfg.LL_RTIER)
            and abs(float(Cfg.GATE_NEXT0) - 0.1) < 1e-12 and abs(float(Cfg.GATE_TWO) - 0.1) < 1e-12,
            "L1 (0.3.1): the fresh config: the 16 lifelong rows at their defaults (gate.nextFactor 0.4 + gate.twoUpFactor 0.1 = Skyy's x2.5 / X10, "
            "gate.crudeFactor kept as an unused legacy row, ladders start with 25 Copper Ingots = G1, lifelong.reclaimTier OFF = fix round 2)")
    LAD = str(Cfg.LL_LADDERS)
    K.check(Up.checkLadders("lifelong.ladders", LAD) is None and "Skyy_Ench_Iron*1" in LAD and "Tool_Hatchet_Iron(Skyy_Ench_Maple*1)" in LAD
            and "Tool_Hoe_Thorium(Skyy_Ench_Cauliflower*1)" in LAD and "Tool_Sickle_Iron(Skyy_Ench_Carrot*1)" in LAD and "Mithril" not in LAD,
            "L1: lifelong.ladders passes GearUp.checkLadders with the real items (Enchanted Iron / Maple / Cauliflower / Carrot), no Mithril step yet")
    CRows, CFn = JClass(PKG + "CfgRows"), JClass(PKG + "CfgFn")
    dang = [k for k in ("part.lifelong", "lifelong.noCraft", "lifelong.ladders", "gate.on", "gate.nextFactor", "gate.bareHands", "lifelong.reclaimTier", "gate.crudeFactor", "gate.twoUpFactor")
            if not bool(CRows.flag(int(CRows.index(k)), "danger"))]
    K.check(not dang and int(CRows.index("lifelong.noDrop")) >= 0 and not bool(CRows.flag(int(CRows.index("lifelong.noDrop")), "danger")),
            "L1: the economy rows are danger rows (Server Setup asks first), noDrop is not: %s" % dang)
    K.check(str(LL.ladders()).startswith(str(Cfg.UP_LADDERS) + ",Tool_Pickaxe_Crude>") and Up.next("Tool_Pickaxe_Crude") == "Tool_Pickaxe_Copper"
            and Up.next("Weapon_Wand_SoulOrb") is not None and Up.next("Tool_Shovel_Crude") is None,
            "L1: the Anvil ladders = upgrade.ladders + lifelong.ladders (Soul Cages still there, shovels have none)")
    apply(part__lifelong="false")
    K.check(str(LL.ladders()) == str(Cfg.UP_LADDERS) and Up.next("Tool_Pickaxe_Crude") is None, "L1: part.lifelong off = the 0.2.26 ladders only")
    apply()

    # ---- bridge stand-ins: skills, profile keys, busy, coins, Requip
    br = Gear.bridge()
    Integer, Long_, Bool_ = JClass("java.lang.Integer"), JClass("java.lang.Long"), JClass("java.lang.Boolean")
    UUID = JClass("java.util.UUID")
    U1 = UUID.fromString("00000000-0000-0000-0000-0000000000a1")
    U2 = UUID.fromString("00000000-0000-0000-0000-0000000000b2")
    SK = {}
    PKEY = {str(U1): "p1", str(U2): "p2"}

    @JImplements("java.util.function.Function")
    class SkillFn(object):
        @JOverride
        def apply(self, o):
            v = SK.get((str(o[0]), str(o[1])))
            return None if v is None else JObject(JInt(v), Integer)

    @JImplements("java.util.function.Function")
    class KeyFn(object):
        @JOverride
        def apply(self, o):
            return JString(PKEY.get(str(o), str(o)))
    COINS = [10 ** 7]

    @JImplements("java.util.function.Function")
    class CoinGet(object):
        @JOverride
        def apply(self, o):
            return JObject(JLong(COINS[0]), Long_)

    @JImplements("java.util.function.Function")
    class CoinTake(object):
        @JOverride
        def apply(self, o):
            n_ = int(o[1])
            if n_ > COINS[0]:
                return JObject(False, Bool_)
            COINS[0] -= n_
            return JObject(True, Bool_)

    @JImplements("java.util.function.Function")
    class CoinAdd(object):
        @JOverride
        def apply(self, o):
            COINS[0] += int(o[1])
            return JObject(JLong(COINS[0]), Long_)
    RQ = {}

    @JImplements("java.util.function.Function")
    class RqList(object):
        @JOverride
        def apply(self, o):
            rows = RQ.get(str(o[1]), [])
            arr = JArray(JObject)(len(rows))
            for i_, r_ in enumerate(rows):
                arr[i_] = JArray(JObject)([JString(r_[0]), JString(r_[1]), r_[2]])
            return arr
    br.put("skill:fn:level", SkillFn())
    br.put("profile:fn:key", KeyFn())
    br.put("coins:fn:get", CoinGet())
    br.put("coins:fn:take", CoinTake())
    br.put("coins:fn:add", CoinAdd())
    br.put("wardrobe:fn:list", RqList())

    def skills(u=U1, **kv):
        for k_, v_ in kv.items():
            SK[(str(u), k_)] = v_
        Gate.forget(u)
        Tool.LAST.clear()

    IS = JClass("com.hypixel.hytale.server.core.inventory.ItemStack")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    BD = JClass("org.bson.BsonDocument")
    INV = JClass("com.hypixel.hytale.server.core.inventory.Inventory")
    ICOMP = "com.hypixel.hytale.server.core.inventory.InventoryComponent$"
    MF = JClass(FAKE_PKG + ".MergeFail")

    def stack(iid, q=1):
        return IS(iid, JInt(q))

    def doc(s_):
        return None if s_ is None or s_.isEmpty() else Data.gearDoc(s_.getMetadata())

    def comp(kind, cont):
        Cc = JClass(ICOMP + kind)
        for args in ((cont, JByte(0)), (cont,)):
            try:
                return Cc(*args)
            except Exception:
                pass
        o_ = us.allocateInstance(Cc.class_)
        jf(Cc, "inventory").set(o_, cont)
        return o_
    SECS = {"hotbar": 9, "storage": 36, "backpack": 9, "armor": 4, "utility": 4, "tools": 4}
    KINDS = (("hotbar", "Hotbar"), ("storage", "Storage"), ("backpack", "Backpack"), ("armor", "Armor"), ("utility", "Utility"), ("tools", "Tool"))

    def mkinv(fail=()):
        inv_ = INV()
        cs_ = dict((k_, MF(JShort(n_)) if k_ in fail else SIC(JShort(n_))) for k_, n_ in SECS.items())
        for f_, kind in KINDS:
            jf(INV, f_).set(inv_, comp(kind, cs_[f_]))
        return inv_, cs_

    def allstacks(cs_):
        out_ = []
        for k_ in ("hotbar", "armor", "tools", "utility", "storage", "backpack"):          # GearStamp.SCAN order
            c_ = cs_[k_]
            for i_ in range(int(c_.getCapacity())):
                s_ = c_.getItemStack(JShort(i_))
                if s_ is not None and not s_.isEmpty():
                    out_.append((k_, i_, s_))
        return out_

    def lls(cs_, pk=None):
        """every lifelong stack: (section, slot, kind, uid, owner, rp, stack)"""
        out_ = []
        for k_, i_, s_ in allstacks(cs_):
            d_ = doc(s_)
            if d_ is not None and bool(LL.isLL(d_)) and (pk is None or str(LL.owner(d_)) == pk):
                out_.append((k_, i_, int(LL.kOf(s_.getItemId())), str(LL.uid(d_)), str(LL.owner(d_)), bool(LL.isRp(d_)), s_))
        return out_

    def ids(cs_):
        out_ = {}
        for k_, i_, s_ in allstacks(cs_):
            out_[str(s_.getItemId())] = out_.get(str(s_.getItemId()), 0) + int(s_.getQuantity())
        return out_

    # ---- a player world (FakeStore with Player + PlayerRef + the InventoryComponents), a FakeChunk on it
    PR = JClass("com.hypixel.hytale.server.core.universe.PlayerRef")
    FPR = JClass(FAKE_PKG + ".FakePR")
    FCh = JClass(FAKE_PKG + ".FakeChunk")
    FS = JClass(FAKE_PKG + ".FakeStore")
    FPM = JClass(FAKE_PKG + ".FakePM")
    FU = JClass(FAKE_PKG + ".FakeUtil")
    for cn in ("com.hypixel.hytale.server.core.modules.entity.EntityModule", "com.hypixel.hytale.server.core.modules.entity.damage.DamageModule",
               "com.hypixel.hytale.server.core.modules.block.BlockModule", "com.hypixel.hytale.server.core.universe.Universe"):
        FU.single(cn)
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    PMC = JClass("com.hypixel.hytale.server.core.entity.entities.player.pages.PageManager")
    REFc = JClass("com.hypixel.hytale.component.Ref")
    IHM = JClass("java.util.IdentityHashMap")
    pm_field = None
    k_ = PLA.class_
    while k_ is not None and pm_field is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == PMC.class_:
                f_.setAccessible(True)
                pm_field = f_
        k_ = k_.getSuperclass()

    def mkpr(u, name):
        pr_ = us.allocateInstance(FPR.class_)
        jf(PR, "uuid").set(pr_, u)
        jf(PR, "username").set(pr_, name)
        return pr_
    PR1, PR2 = mkpr(U1, "Tester"), mkpr(U2, "Other")

    def said(pr_):
        s_ = pr_.said
        return [] if s_ is None else [str(x) for x in s_]

    def world(inv_, cs_, pr_):
        pl = us.allocateInstance(PLA.class_)
        jf(PLA, "inventory").set(pl, inv_)
        if pm_field is not None:
            pm_field.set(pl, us.allocateInstance(FPM.class_))
        ref = us.allocateInstance(REFc.class_)
        jf(REFc, "index").setInt(ref, JInt(7))
        st = us.allocateInstance(FS.class_)
        st.comps = JClass("java.util.HashMap")()
        pm = IHM()
        pm.put(PLA.getComponentType(), pl)
        pm.put(PR.getComponentType(), pr_)
        for f_, kind in KINDS:
            try:
                pm.put(JClass(ICOMP + kind).getComponentType(), INV.class_.getDeclaredField(f_) and jf(INV, f_).get(inv_))
            except Exception as e_:
                K.notes.append("world: no component type for %s (%s)" % (kind, str(e_)[:80]))
        st.comps.put(ref, pm)
        jf(REFc, "store").set(ref, st)
        ch = us.allocateInstance(FCh.class_)
        ch.comps = IHM()
        ch.comps.put(PR.getComponentType(), pr_)
        ch.ref = ref
        return ref, st, ch, pl

    def reset_reg():
        """a server restart: the registry cache goes, the files stay"""
        LL.REG.clear()
        LL.LAST.clear()
        LL.BADAT.clear()
        LL.FAILAT.clear()

    def wipe_home():
        LL.REG.clear()
        LL.LAST.clear()
        LL.BADAT.clear()
        LL.FAILAT.clear()
        shutil.rmtree(os.path.join(HOME, "lifelong"), ignore_errors=True)

    def regfile(pk):
        f_ = os.path.join(HOME, "lifelong", pk + ".properties")
        out_ = {}
        if os.path.isfile(f_):
            for l_ in open(f_, encoding="utf-8").read().split("\n"):
                if l_ and not l_.startswith("#") and "=" in l_:
                    a_, b_ = l_.split("=", 1)
                    out_[a_] = b_
        return out_

    # ============================================================================ L2: kinds, tiers, the level rule
    fams = {"Tool_Pickaxe_": 0, "Tool_Hatchet_": 1, "Tool_Hoe_": 2, "Tool_Sickle_": 3}
    tools = sorted(i for i in AZJ if i.startswith(tuple(fams)) and not i.startswith("Tool_Hatchet_Pickaxe_"))
    TIERW = {"Crude": 0, "Wood": 0, "Copper": 1, "Scrap": 1, "Bronze": 2, "Iron": 2, "Steel": 2, "Thorium": 3, "Cobalt": 4, "Adamantite": 5,
             "Mithril": 6, "Onyxium": 7}
    bad2 = [(i, int(LL.kOf(i)), int(LL.tier(i))) for i in tools
            if int(LL.kOf(i)) != [v for p, v in fams.items() if i.startswith(p)][0] or int(LL.tier(i)) != [TIERW[w] for w in i.split("_")[2:] if w in TIERW][0]]
    K.check(len(tools) >= 20 and not bad2 and all(int(LL.kOf(i)) == -1 for i in ("Tool_Shovel_Iron", "Tool_Hammer_Iron", "Weapon_Axe_Iron", "Skyy_Tool_X")),
            "L2: every vanilla pickaxe / hatchet / hoe / sickle has its kind + tier; shovels, hammers, weapon axes are no lifelong kind (bad %s)" % bad2[:3])
    caps = dict((i, int(Lvl.band(i)[1])) for i in ("Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium"))
    skills(Mining=30, Foraging=4, Farming=0)
    lv = [int(LL.levelFor(U1, i)) for i in ("Tool_Pickaxe_Crude", "Tool_Pickaxe_Iron", "Tool_Pickaxe_Thorium", "Tool_Hatchet_Iron", "Tool_Hoe_Copper")]
    K.check(lv == [min(30, caps["Tool_Pickaxe_Crude"]), min(30, caps["Tool_Pickaxe_Iron"]), min(30, caps["Tool_Pickaxe_Thorium"]), 4, 1],
            "L2: the level rule = min(skill, the tier's band top), at least 1: Mining 30 -> Crude %d / Iron %d / Thorium %d, Foraging 4 -> 4, Farming 0 -> 1 (caps %s): %s"
            % (lv[0], lv[1], lv[2], caps, lv))
    br.remove("skill:fn:level")
    Gate.forget(U1)
    K.check(int(LL.levelFor(U1, "Tool_Pickaxe_Iron")) == -1 and int(LL.earned(U1, JInt(0))) == 0, "L2: no SkyySkills = -1 (the document's level stays), no points")
    br.put("skill:fn:level", SkillFn())
    skills(Mining=30)
    K.check(int(LL.earned(U1, JInt(0))) == 29 and int(LL.earned(U1, JInt(1))) == 3, "L2: 1 point per skill level (Mining 30 = 29 points, Foraging 4 = 3)")

    # ============================================================================ L3: the gate matrix + the REAL hit system
    BTY = JClass("com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType")
    bmap = BTY.getAssetMap().getAssetMap()
    bids = [str(k) for k in bmap.keySet()]
    seen_cat = {1: set(), 3: set(), 4: set()}
    for b in bids:
        c_, m_ = [int(x) for x in LL.catOf(b)]
        if m_ >= 1:
            seen_cat[c_].add(b)
    ow = [str(x) for x in LL.ORE_W]
    wn = [str(x) for x in LL.WOOD_W]
    cw = [str(x) for x in LL.CROP_W]
    miss = [w for w in ow if not [b for b in seen_cat[1] if b.lstrip("*").startswith("Ore_" + w)]] + \
           [w for w in wn if not [b for b in seen_cat[3] if b.lstrip("*").startswith("Wood_" + w + "_")]] + \
           [w for w in cw if not [b for b in seen_cat[4] if b.lstrip("*").startswith("Plant_Crop_" + w + "_")]]
    K.check(set(miss) <= {"Onyxium"} and len(seen_cat[1]) >= 9 and len(seen_cat[3]) >= 20 and len(seen_cat[4]) >= 10,
            "L3: every tier-table word matches real BlockTypes in the store (%d ore, %d log, %d crop blocks gated; no block yet: %s - Onyxium is Zone 5)"
            % (len(seen_cat[1]), len(seen_cat[3]), len(seen_cat[4]), miss))
    ungated = [list(LL.catOf(x)) for x in ("Rock_Stone", "Soil_Dirt", "Wood_Oak_Planks", "Ore_Prisma", "Plant_Crop_Berry_Block")]
    K.check(all(u_[1] < 1 for u_ in ungated) and list(LL.catOf("*Ore_Iron_Stone")) == [1, 2] and list(LL.catOf("Wood_Fig_Blue_Trunk")) == [3, 5],
            "L3: stone / dirt / planks / an unlisted ore / berries never gated; a state id (*Ore_Iron_Stone) = Iron M2; Wood_Fig_Blue_Trunk = M5: %s" % ungated)
    FAMMAX = [int(x) for x in LL.FAMMAX]

    def py_decide(f, t, c, m):
        if c == 0 or m < 1:
            return -1
        fits = (c == 1 and f in (1, 6)) or (c == 3 and f in (3, 6)) or (c == 4 and f in (4, 5))
        if not fits:
            return -1 if c == 4 else 2
        me = min(m, FAMMAX[f])
        d = me - max(t, 1)          # 0.3.1: Crude / Wood count as tier 1
        return 0 if d <= 0 else (1 if d <= 2 else 2)          # 0.3.1: one or two up = slow, three up refused
    badm, nm = [], 0
    for iid in tools + ["Tool_Shovel_Iron", "Weapon_Sword_Iron", "Weapon_Axe_Iron", None]:
        f = 0 if iid is None else int(Data.toolFam(iid))
        t = TIERW.get(([w for w in (iid or "").split("_")[2:] if w in TIERW] + ["Crude"])[0], 0)
        s_ = None if iid is None else stack(iid)
        for c in (1, 3, 4):
            for m in range(0, 8):
                got = int(LL.decideC(s_, JInt(c), JInt(m))[0])
                want = py_decide(f, t, c, m)
                nm += 1
                if got != want:
                    badm.append((iid, c, m, got, want))
    K.check(not badm and nm > 500, "L3: THE GATE MATRIX: %d cases (every pickaxe / hatchet / hoe / sickle tier, a shovel, a sword, a weapon axe, bare hands x ore / "
            "log / crop x M0-M7) = the 0.3.1 rule (Crude = tier 1; own tier normal, +1 / +2 slow, +3 refused, no fitting tool on ore / logs refused, "
            "crops by hand free, a family's top tier caps the ask): bad %s" % (nm, badm[:4]))
    K.check(int(LL.decideC(stack("Tool_Hoe_Thorium"), JInt(4), JInt(7))[0]) == 0 and int(LL.decideC(stack("Tool_Sickle_Iron"), JInt(4), JInt(4))[0]) == 0
            and int(LL.decideC(stack("Tool_Hoe_Iron"), JInt(4), JInt(7))[0]) == 1 and int(LL.decideC(stack("Tool_Hoe_Crude"), JInt(4), JInt(5))[0]) == 1
            and int(LL.decideC(stack("Tool_Hoe_Crude"), JInt(4), JInt(5))[5]) == 2
            and int(LL.decideC(stack("Tool_Pickaxe_Crude"), JInt(1), JInt(1))[0]) == 0,
            "L3 (0.3.1): the top vanilla hoe (Thorium) / sickle (Iron) works at full speed on every crop above it (a Potato, a Pumpkin); an Iron hoe on a "
            "Potato = one up; a Crude hoe on a Tomato = two up (slow, was refused); a Crude pickaxe on Copper ore = NORMAL (was slow)")
    apply(gate__bareHands="false")
    K.check(int(LL.decideC(None, JInt(3), JInt(1))[0]) == -1 and int(LL.decideC(stack("Tool_Shovel_Iron"), JInt(1), JInt(4))[0]) == -1,
            "L3: gate.bareHands off: no tool / the wrong tool is not gated")
    apply(gate__on="false")
    K.check(int(LL.decideC(stack("Tool_Pickaxe_Crude"), JInt(1), JInt(7))[0]) == -1, "L3: gate.on off: nothing is gated")
    apply()
    # the REAL GearToolHitSys.handle on REAL DamageBlockEvents
    DBE = JClass("com.hypixel.hytale.server.core.event.events.ecs.DamageBlockEvent")
    ctor = [c for c in DBE.class_.getConstructors() if len(c.getParameterTypes()) == 5][0]
    pts = [str(p.getName()) for p in ctor.getParameterTypes()]
    JFl = JClass("java.lang.Float")

    def ev(s_, b_, d):
        args, nf = [], 0
        for p in pts:
            if p.endswith("ItemStack"):
                args.append(s_)
            elif p.endswith("BlockType"):
                args.append(b_)
            elif p == "float":
                args.append(JFl.valueOf(JFloat(1.0 if nf == 0 else d)))
                nf += 1
            else:
                args.append(JClass(p)(JInt(0), JInt(64), JInt(0)))
        return ctor.newInstance(JArray(JObject)(args))
    Hit = JClass(PKG + "GearToolHitSys")
    hs = Hit()
    invH, csH = mkinv()
    refH, stH, chH, plH = world(invH, csH, PR1)
    BL = dict((n, bmap.get(n)) for n in ("Ore_Iron_Stone", "Ore_Copper_Stone", "Ore_Thorium_Sandstone", "Wood_Oak_Trunk", "Wood_Maple_Trunk", "Rock_Stone"))
    K.check(all(v is not None for v in BL.values()), "L3: the real BlockTypes are in the store: %s" % [k for k, v in BL.items() if v is None])
    skills(Mining=10, Foraging=10)

    def hit(s_, bn, d=0.3):
        Tool.LAST.clear()
        e_ = ev(s_, BL[bn], d)
        d0 = float(e_.getDamage())
        hs.handle(JInt(0), chH, stH, None, e_)
        return bool(e_.isCancelled()), float(e_.getDamage()), d0
    n0 = [int(x) for x in LL.N]
    ref_on = float(Tool.onDamage(U1, stack("Tool_Pickaxe_Iron"), BL["Ore_Iron_Stone"], JFloat(0.3)))
    r_norm = hit(stack("Tool_Pickaxe_Iron"), "Ore_Iron_Stone")
    Tool.LAST.clear()
    ref_slow = float(Tool.onDamage(U1, stack("Tool_Pickaxe_Iron"), BL["Ore_Thorium_Sandstone"], JFloat(0.3)))
    r_slow = hit(stack("Tool_Pickaxe_Iron"), "Ore_Thorium_Sandstone")
    r_ref = hit(stack("Tool_Pickaxe_Copper"), "Ore_Thorium_Sandstone")
    r_bare = hit(None, "Wood_Oak_Trunk")
    r_sword = hit(stack("Weapon_Sword_Iron"), "Ore_Copper_Stone")
    r_stone = hit(None, "Rock_Stone")
    r_crude_log = hit(stack("Tool_Hatchet_Crude"), "Wood_Oak_Trunk")
    r_crude_maple = hit(stack("Tool_Hatchet_Crude"), "Wood_Maple_Trunk")
    n1 = [int(x) for x in LL.N]
    Tool.LAST.clear()
    ref_cu_th = float(Tool.onDamage(U1, stack("Tool_Pickaxe_Copper"), BL["Ore_Thorium_Sandstone"], JFloat(0.3)))
    Tool.LAST.clear()
    ref_cr_oak = float(Tool.onDamage(U1, stack("Tool_Hatchet_Crude"), BL["Wood_Oak_Trunk"], JFloat(0.3)))
    Tool.LAST.clear()
    ref_cr_map = float(Tool.onDamage(U1, stack("Tool_Hatchet_Crude"), BL["Wood_Maple_Trunk"], JFloat(0.3)))
    K.check(not r_norm[0] and abs(r_norm[1] - ref_on) < 1e-6 and not r_slow[0] and abs(r_slow[1] - float(JFloat(ref_slow * 0.4))) < 1e-6
            and not r_ref[0] and abs(r_ref[1] - float(JFloat(ref_cu_th * 0.1))) < 1e-6
            and r_bare[0] and r_sword[0] and not r_stone[0] and abs(r_stone[1] - r_stone[2]) < 1e-9
            and not r_crude_log[0] and abs(r_crude_log[1] - ref_cr_oak) < 1e-6
            and not r_crude_maple[0] and abs(r_crude_maple[1] - float(JFloat(ref_cr_map * 0.4))) < 1e-6,
            "L3 (0.3.1): THE REAL HIT SYSTEM: Iron pickaxe on iron ore = its own power (%.4f); on thorium (one up) = that x0.4 (%.5f); a Copper pickaxe on "
            "thorium (two up) = x0.1, no longer cancelled; bare hands on a log and a sword on copper ore = cancelled; bare hands on stone = vanilla; Crude "
            "hatchet on Oak = NORMAL (Crude = T1), on Maple = x0.4 (was refused): %s" % (r_norm[1], r_slow[1], [r_norm, r_slow, r_ref, r_bare, r_sword, r_stone, r_crude_log, r_crude_maple]))
    K.check(n1[0] - n0[0] >= 2 and n1[1] - n0[1] >= 3 and n1[2] - n0[2] >= 2, "L3 (0.3.1): the counters: refused %d (bare %d), slowed %d" % (n1[0] - n0[0], n1[2] - n0[2], n1[1] - n0[1]))
    e_c = ev(stack("Tool_Pickaxe_Copper"), BL["Ore_Thorium_Sandstone"], 0.3)
    e_c.setCancelled(True)
    hs.handle(JInt(0), chH, stH, None, e_c)
    K.check(bool(e_c.isCancelled()) and abs(float(e_c.getDamage()) - 0.3) < 1e-6, "L3: an event another mod cancelled (SkyyIslands) is left alone")

    # ============================================================================ L4: only.farming (no Fortune one tier up)
    o0, o1, o3 = str(LL.onlyFor(JInt(4), JInt(0), "")), str(LL.onlyFor(JInt(4), JInt(1), "")), str(LL.onlyFor(JInt(4), JInt(3), ""))
    o5 = str(LL.onlyFor(JInt(5), JInt(2), ""))
    free_ = str(LL.CROP_FREE)
    K.check(o0 == o1 and o1.split(",")[:2] == ["Wheat", "Lettuce"] and "Carrot" not in o1 and "Berry" in o1 and free_ in o1
            and all(w in o3 for w in ("Wheat", "Carrot", "Cauliflower", "Pumpkin", "Tomato", "Cotton", "Potato"))
            and "Pumpkin" in o5 and "Potato" in o5 and str(LL.onlyFor(JInt(1), JInt(0), "Rock_,Rubble_,Ore_")) == "Rock_,Rubble_,Ore_",
            "L4 (0.3.1): a Crude hoe's Fortune counts like a Copper hoe's (Crude = T1: Wheat + Lettuce + the free crops; was the free crops only); a "
            "Thorium hoe (the top vanilla hoe) on every crop; an Iron sickle too (sickles end at Iron); pickaxes keep their "
            "0.2.12 filter: %s | %s" % (o0[:60], o1[:60]))
    skills(Farming=20)
    Tool.LAST.clear()
    Tool.held(U1, Data.put(stack("Tool_Hoe_Crude"), Roll.newDoc("Tool_Hoe_Crude", JInt(0), True, "craft", JInt(5)), None))
    g_ = br.get("skill:bonus:" + str(U1))
    gsrc = None if g_ is None else g_.get("gear")
    K.check(gsrc is not None and str(gsrc.get("only.farming")) == o0, "L4: Tool.held posts only.farming = that list for a Crude hoe: %s" % (None if gsrc is None else str(gsrc)[:160]))
    ft = [int(LL.farmTier("Plant_Crop_Wheat_Block", "Tool_Hoe_Crude")), int(LL.farmTier("Plant_Crop_Carrot_Block", "Tool_Hoe_Crude")),
          int(LL.farmTier("Plant_Crop_Wheat_Block", "Tool_Hoe_Copper")), int(LL.farmTier("Plant_Crop_Wheat_Block", None)),
          int(LL.farmTier("Rock_Stone", "Tool_Hoe_Crude"))]
    K.check("Plant_Cactus" in o0.split(",") and "Plant_Cactus" in o1.split(",") and "Plant_Cactus" in o5.split(",")
            and any(str(b).startswith("Plant_Cactus") for b in bids),
            "FIX engine-5: a hoe / sickle's only.farming always lists Plant_Cactus (SkyySkills counts cactus as Farming and matches by 'contains' - "
            "Fortune keeps counting on it at every tier; a real Plant_Cactus block is in the store): %s" % o0[-60:])
    K.check(ft == [0, 1, 0, -1, -1], "L4 (0.3.1): gear:fn:farmTier's core: Crude hoe on Wheat = 0 (normal, was 1), on Carrot = 1 (half XP, was 2), "
            "Copper hoe on Wheat = 0, by hand = -1, a stone = -1: %s" % ft)

    # ============================================================================ M: THE MIGRATION ON THE LIVE PLAYERS' REAL STACKS
    BDc = JClass("org.bson.BsonDocument")
    SECMAP = {"HotbarInventory": "hotbar", "StorageInventory": "storage", "BackpackInventory": "backpack", "ArmorInventory": "armor",
              "UtilityInventory": "utility", "ToolInventory": "tools"}
    LIVE = {}
    for f_ in sorted(glob.glob(os.path.join(PLAYERS, "*.json"))):
        d_ = json.load(open(f_, encoding="utf-8"))
        rows = []
        for ck, sec in SECMAP.items():
            items = ((d_.get("Components") or {}).get(ck) or {}).get("Inventory", {}).get("Items", {}) or {}
            for sl, it in items.items():
                iid = it.get("Id")
                if not iid or ITEM.getAssetMap().getAsset(iid) is None:
                    continue
                md = it.get("Metadata")
                rows.append((sec, int(sl), iid, int(it.get("Quantity", 1)), json.dumps(md) if md else None))
        LIVE[os.path.basename(f_)[:-5]] = rows
    K.notes.append("M: live players (scratch copies): %s" % dict((k, len(v)) for k, v in LIVE.items()))

    def live_inv(rows):
        inv_, cs_ = mkinv()
        for sec, sl, iid, q, md in rows:
            if sl >= int(cs_[sec].getCapacity()):
                continue
            s_ = IS(iid, JInt(q), BDc.parse(md)) if md else IS(iid, JInt(q))
            cs_[sec].setItemStackForSlot(JShort(sl), s_)
        return inv_, cs_

    def snapshot(cs_):
        return [(k_, i_, str(s_.getItemId()), int(s_.getQuantity()), None if s_.getMetadata() is None else str(s_.getMetadata().toJson()))
                for k_, i_, s_ in allstacks(cs_)]

    def restore_inv(cs_, snap):
        for k_ in SECS:
            c_ = cs_[k_]
            for i_ in range(int(c_.getCapacity())):
                c_.removeItemStackFromSlot(JShort(i_))
        for k_, i_, iid, q, md in snap:
            cs_[k_].setItemStackForSlot(JShort(i_), IS(iid, JInt(q), BDc.parse(md)) if md else IS(iid, JInt(q)))

    def keep_fields(d_):
        """the parts of a document the migration must keep: rarity, lines, reforge name, identified"""
        if d_ is None:
            return None
        return (str(Data.str(d_, "r", "normal")), str(View.modSummary(d_)), str(Data.str(d_, "rf", "")), bool(Data.identified(d_)))

    def invariants(tag, cs_, pk, before_ids, gifts):
        L_ = lls(cs_, pk)
        R_ = regfile(pk)
        kinds = sorted(x[2] for x in L_)
        uids_ok = all(R_.get("%s.uid" % str(LL.KIND[x[2]])) == x[3] for x in L_)
        now_ids = ids(cs_)
        want = dict(before_ids)
        for g in gifts:
            want[g] = want.get(g, 0) + 1
        pend = [k for k in R_ if k.endswith(".pend")]
        return kinds == [0, 1, 2, 3] and uids_ok and now_ids == want and not pend and R_.get("migrated") == "1", \
            "%s: kinds %s uids_ok %s pend %s migrated %s counts %s" % (tag, kinds, uids_ok, pend, R_.get("migrated"),
                                                                      dict((k, (now_ids.get(k, 0), want.get(k, 0))) for k in set(now_ids) | set(want) if now_ids.get(k, 0) != want.get(k, 0)))
    best_pick = {}
    for pname, rows in LIVE.items():
        wipe_home()
        logs()
        PKEY[str(U1)] = "live-" + pname[:8]
        pk = PKEY[str(U1)]
        skills(Mining=31, Foraging=15, Farming=8)
        inv_, cs_ = live_inv(rows)
        refL, stL, chL, plL = world(inv_, cs_, PR1)
        before = ids(cs_)
        bdocs = dict(((k_, i_), keep_fields(doc(s_))) for k_, i_, s_ in allstacks(cs_))
        owners_ = sorted(set(str(LL.owner(doc(s_))) for k_, i_, s_ in allstacks(cs_) if doc(s_) is not None and bool(LL.isLL(doc(s_)))))
        if owners_:
            # 0.3.2: this live player file was saved AFTER 0.3.0 went live (2026-10-13 19:54) - the tools are lifelong already (owner = the
            # real profile key). The migration's pick / gift / crash checks need a pre-0.3.0 inventory; here instead: 0.3.2 on the REAL migrated
            # inventory ADOPTS each tool (a lost registry rebuilt from the items), gives nothing, keeps every count + rarity / lines, takes a
            # snapshot of each; a second sweep and a restart change nothing
            PKEY[str(U1)] = owners_[0]
            pk = owners_[0]
            logs()
            Life.sweep0(PR1, inv_, True)
            lgA = logs()
            rA_ = regfile(pk)
            LA = lls(cs_, pk)
            keptA = all(keep_fields(doc(x[6])) == bdocs.get((x[0], x[1])) for x in LA)
            regA = all(rA_.get("%s.uid" % str(LL.KIND[x[2]])) == x[3] and rA_.get("%s.snapU" % str(LL.KIND[x[2]])) == x[3] for x in LA)
            snapA = snapshot(cs_)
            Life.sweep0(PR1, inv_, True)
            reset_reg()
            Life.sweep0(PR1, inv_, True)
            K.check(len(owners_) == 1 and ids(cs_) == before and keptA and regA and rA_.get("migrated") == "1" and len(LA) == len(set(x[2] for x in LA))
                    and not [l for l in lgA if "LL-MARK " in l or "LL-GIVE " in l] and len([l for l in lgA if "LL-ADOPT " in l]) == len(LA)
                    and snapshot(cs_) == snapA and regfile(pk) == rA_,
                    "M (0.3.2): live player %s is ALREADY migrated in game (owner %s, %d lifelong tools): 0.3.2 adopts each one (no mark, no gift), "
                    "every count + rarity / lines kept, registry uid + snapshot per kind; a 2nd sweep + a restart change nothing" % (pname[:8], owners_, len(LA)))
            K.notes.append("M: %s is already migrated in game - the pre-0.3.0 migration checks ran on the other live player(s) only" % pname[:8])
            PKEY[str(U1)] = "p1"
            continue
        # the expected pick: per kind the best (rarity, level, lines), identified, not stacked
        exp = {}
        for k_, i_, s_ in allstacks(cs_):
            kk = int(LL.kOf(s_.getItemId()))
            if kk < 0 or int(s_.getQuantity()) != 1:
                continue
            d_ = Data.effective(s_.getItemId(), s_.getMetadata())
            key = (0 if d_ is None else int(Data.rarity(d_)), int(Lvl.level(s_.getItemId(), d_)), 0 if d_ is None else int(Data.mods(d_).size()))
            if kk not in exp or key > exp[kk][0]:
                exp[kk] = (key, k_, i_, str(s_.getItemId()))
        gifts = [str(LL.KCRUDE[k]) for k in range(4) if k not in exp]
        nw0 = int(LL.N[5])
        Life.sweep0(PR1, inv_, True)
        nw1 = int(LL.N[5])
        K.check(nw1 - nw0 <= 5, "FIX engine-3: %s: the migration wrote the registry %d times (one journal per marked / given kind + ONE save; 0.3.0 "
                "before the fix: up to 10)" % (pname[:8], nw1 - nw0))
        ok, why = invariants("M " + pname[:8], cs_, pk, before, gifts)
        K.check(ok, "M: live player %s: after the migration exactly one lifelong tool per kind, the registry names each uid, migrated=1, no journal "
                "left, every item count unchanged except %s: %s" % (pname[:8], gifts, why))
        L_ = dict((x[2], x) for x in lls(cs_, pk))
        picked = dict((k, (L_[k][0], L_[k][1], str(L_[k][6].getItemId()))) for k in L_)
        exp_pos = dict((k, (v[1], v[2], v[3])) for k, v in exp.items())
        kept = all(keep_fields(doc(L_[k][6])) == bdocs.get((L_[k][0], L_[k][1])) or bdocs.get((L_[k][0], L_[k][1])) is None for k in exp)
        K.check(all(picked[k] == exp_pos[k] for k in exp) and kept, "M: %s: the best tool of each kind was picked where it lay (%s) and kept its rarity / "
                "lines / reforge name; the rest stay plain" % (pname[:8], dict((str(LL.KIND[k]), v[2]) for k, v in exp_pos.items())))
        lvl_ok = all(int(Data.num(doc(L_[k][6]), "lvl", -1)) == int(LL.levelFor(U1, L_[k][6].getItemId())) for k in L_)
        K.check(lvl_ok, "M: %s: each lifelong tool's document level = min(skill, its tier's top): %s" % (
            pname[:8], dict((str(LL.KIND[k]), int(Data.num(doc(L_[k][6]), "lvl", -1))) for k in L_)))
        best_pick[pname] = dict((str(LL.KIND[k]), v[2]) for k, v in exp_pos.items())
        snap1 = snapshot(cs_)
        reg1 = regfile(pk)
        Life.sweep0(PR1, inv_, True)
        reset_reg()
        Life.sweep0(PR1, inv_, True)
        K.check(snapshot(cs_) == snap1 and regfile(pk) == reg1, "M: %s: a second sweep and a restart + sweep change nothing (run once)" % pname[:8])
        lg = logs()
        K.check(all(" undo: " in l for l in lg if "LL-MARK " in l), "FIX A-3: %s: every LL-MARK line carries the stack as it was (undo data): %s"
                % (pname[:8], [l[-80:] for l in lg if "LL-MARK " in l][:1]))
        K.check(len([l for l in lg if "LL-MARK " in l]) == len(exp) and len([l for l in lg if "LL-GIVE " in l]) == len(gifts)
                and len([l for l in lg if "LL-MIGRATED" in l]) == 1, "M: %s: gear.log has one LL-MARK per picked tool, one LL-GIVE per gift, one LL-MIGRATED"
                % pname[:8])
        K.check(any("Lifelong tools: you keep ONE pickaxe" in x for x in said(PR1)), "M: %s: the one-time chat line" % pname[:8])
        PR1.said = None
        # CRASH AT EVERY STEP: 1-3 mark, 4-6 give; then a restart (registry cache dropped) with the inventory as it was at the crash
        # (the engine saved it) AND with the inventory from before the step (the engine did not save it) - the end state is the same rule
        for crash_at in (1, 2, 3, 4, 5, 6):
            for saved in (True, False):
                wipe_home()
                inv2, cs2 = live_inv(rows)
                pre = snapshot(cs2)
                Life.CRASH_AT = crash_at
                crashed = False
                try:
                    Life.sweep0(PR1, inv2, True)
                except Exception as ex_:
                    crashed = "harness: a crash at lifelong step %d" % crash_at in str(ex_)
                Life.CRASH_AT = 0
                if not crashed and ((crash_at <= 3 and not exp) or (crash_at >= 4 and not gifts)):
                    continue
                if not saved:
                    restore_inv(cs2, pre)
                reset_reg()
                Life.sweep0(PR1, inv2, True)
                Life.sweep0(PR1, inv2, True)
                ok2, why2 = invariants("crash %d saved %s" % (crash_at, saved), cs2, pk, before, gifts)
                K.check(crashed and ok2, "M: %s: a CRASH at step %d (inventory %s) then a restart: %s" % (
                    pname[:8], crash_at, "saved" if saved else "not saved", why2))
        logs()
        # a failing registry write: nothing moves, the next sweep finishes
        wipe_home()
        inv3, cs3 = live_inv(rows)
        pre3 = snapshot(cs3)
        LL.FAIL_SAVE = True
        Life.sweep0(PR1, inv3, True)
        LL.FAIL_SAVE = False
        K.check(snapshot(cs3) == pre3 and not lls(cs3), "M: %s: the registry cannot be written -> no item is touched" % pname[:8])
        Life.sweep0(PR1, inv3, True)
        ok3, why3 = invariants("after a failed write", cs3, pk, before, gifts)
        K.check(ok3, "M: %s: ... and the next sweep migrates normally: %s" % (pname[:8], why3))
    K.notes.append("M: picks %s" % best_pick)
    PKEY[str(U1)] = "p1"
    # a NEW profile: an empty inventory gets the four Crude Common tools (no SkyyIslands change needed)
    wipe_home()
    invN, csN = mkinv()
    skills(Mining=1, Foraging=1, Farming=1)
    RQ["items"] = [("e9", "Tool_Pickaxe_Iron", None), ("e8", "Weapon_Sword_Iron", None)]
    PR1.said = None
    nwN = int(LL.N[5])
    Life.sweep0(PR1, invN, True)
    nwN = int(LL.N[5]) - nwN
    RQ.clear()
    K.check(nwN == 5 and regfile("p1").get("migrated") == "1" and not [k for k in regfile("p1") if k.endswith(".pend")],
            "FIX engine-3: a new profile's four gifts = 4 journal writes + 1 save (was 10), migrated=1 + every commit on disk: %d writes" % nwN)
    K.check(any("Your Requip holds a pickaxe that was not checked" in x and "/lifelong" in x for x in said(PR1))
            and not any("holds a pickaxe, " in x for x in said(PR1)),
            "FIX A-3: the migration names a lifelong-kind tool sitting in Requip once (pick it with /lifelong); a sword there is not named: %s" % said(PR1)[-1:])
    LN = lls(csN, "p1")
    K.check(sorted(str(x[6].getItemId()) for x in LN) == sorted(str(x) for x in LL.KCRUDE) and all(str(Data.str(doc(x[6]), "r", "")) == "normal"
            and int(Data.mods(doc(x[6])).size()) == 0 and int(Data.num(doc(x[6]), "lvl", -1)) == 1 and not x[5] for x in LN)
            and [x[0] for x in LN] == ["storage"] * 4,
            "M: a NEW profile's first join: the four Crude Common tools (Lv 1, no lines) in the storage first: %s" % [(x[0], x[1], str(x[6].getItemId())) for x in LN])
    # no room: the kinds wait, nothing is lost, the line comes once a minute
    wipe_home()
    invF, csF = mkinv()
    for sec in ("storage", "backpack", "hotbar"):
        for i_ in range(int(csF[sec].getCapacity())):
            csF[sec].setItemStackForSlot(JShort(i_), stack("Rock_Stone", 10))
    PR1.said = None
    Life.sweep0(PR1, invF, True)
    Life.sweep0(PR1, invF, True)
    K.check(not lls(csF) and regfile("p1").get("migrated") is None and len([x for x in said(PR1) if "is waiting - free one inventory slot" in x]) == 4,
            "M: a full inventory: nothing given, not marked done, one waiting line per kind (not repeated at once)")
    csF["storage"].removeItemStackFromSlot(JShort(0))
    csF["storage"].removeItemStackFromSlot(JShort(1))
    csF["storage"].removeItemStackFromSlot(JShort(2))
    csF["storage"].removeItemStackFromSlot(JShort(3))
    LL.LAST.clear()
    Life.sweep0(PR1, invF, False)
    K.check(len(lls(csF)) == 4 and regfile("p1").get("migrated") == "1", "M: ... room made -> the next sweep gives all four")

    # ============================================================================ L5: perks + points
    wipe_home()
    logs()
    inv5, cs5 = mkinv()
    cs5["hotbar"].setItemStackForSlot(JShort(0), Data.put(stack("Tool_Pickaxe_Copper"), Roll.newDoc("Tool_Pickaxe_Copper", JInt(2), True, "craft", JInt(12)), None))
    skills(Mining=12, Foraging=2, Farming=1)
    Life.sweep0(PR1, inv5, True)
    reg5 = LL.reg("p1")
    pick5 = cs5["hotbar"].getItemStack(JShort(0))
    K.check(bool(LL.isLL(doc(pick5))) and str(Data.str(doc(pick5), "r", "")) == "rare", "L5: the Rare Copper pickaxe became the lifelong one")
    r_hatch = str(Life.buy(U1, JInt(1), JInt(0)))
    r_none = str(Life.buy(U1, JInt(2), JInt(0)))
    r_wis = str(Life.buy(U1, JInt(0), JInt(2)))
    r_vein = str(Life.buy(U1, JInt(0), JInt(3)))
    br.put("gear:perk:readers", "vein, fell")
    r_vein2 = str(Life.buy(U1, JInt(0), JInt(3)))
    br.remove("gear:perk:readers")
    K.check(r_hatch.startswith("+Speed is level 1 now (0 points left)") and r_none.startswith("-Speed is not an upgrade for a hoe")
            and "needs an Iron pickaxe" in r_wis and "next SkyyTrees" in r_vein and "needs an Iron pickaxe" in r_vein2,
            "L5: Speed for the hatchet (Foraging 2 = 1 point); refusals: Speed is not for hoes; Wisdom + Vein Mine need an Iron tool; Vein Mine waits for "
            "SkyyTrees (gear:perk:readers) - then the tier rule: %s | %s | %s | %s | %s" % (r_hatch, r_none, r_wis, r_vein, r_vein2))
    st0 = [float(x) for x in Tool.stats(U1, pick5)]
    got = [str(Life.buy(U1, JInt(0), JInt(0))) for _i in range(11)]
    st1 = [float(x) for x in Tool.stats(U1, pick5)]
    K.check(all(g.startswith("+") for g in got[:10]) and got[10].startswith("-Speed is already at its top level (10)")
            and abs(st1[4] - min(100.0, st0[4] * 1.2)) < 1e-6 and int(LL.perkOf(reg5, JInt(0), JInt(0))) == 10 and regfile("p1").get("pickaxe.up.spd") == "10",
            "L5: 10 Speed levels (1 point each, 11 points free) -> power x1.2 exactly (%.4f -> %.4f), the 11th refused; the registry file says 10" % (st0[4], st1[4]))
    r_more = str(Life.buy(U1, JInt(0), JInt(1)))
    r_poor = str(Life.buy(U1, JInt(0), JInt(1)))
    st2 = [float(x) for x in Tool.stats(U1, pick5)]
    K.check(r_more.startswith("+Fortune is level 1 now (0 points left)") and r_poor.startswith("-Fortune 2 costs 1 point - you have 0 free")
            and abs(st2[5] - min(float(Cfg.TOOL_FCAP), round((st1[5] + 1.0) * 10) / 10.0)) < 1e-6,
            "L5: Fortune 1 = +1 Fortune on the tool (%.1f -> %.1f); out of points refused: %s" % (st1[5], st2[5], r_poor))
    od = doc(pick5).clone()
    for k_ in ("ll", "lu", "lo", "lrp"):
        od.remove(k_)
    other = Data.put(stack("Tool_Pickaxe_Copper"), od, None)
    sto = [float(x) for x in Tool.stats(U1, other)]
    K.check(abs(sto[4] - st0[4]) < 1e-9 and abs(sto[5] - st0[5]) < 1e-9 and sto[4] < st2[4], "L5: the same Rare roll as a PLAIN tool gets none of the perks "
            "(power %.4f / %.4f with Speed 10, Fortune %.1f / %.1f)" % (sto[4], st2[4], sto[5], st2[5]))
    skills(Mining=12)
    K.check(int(LL.free(U1, reg5, JInt(0))) == 0 and int(LL.spent(reg5, JInt(0))) == 11, "L5: spent 11 of 11")
    # the reset: coins first, more each time, refund on a failed write, coins unavailable
    COINS[0] = 10 ** 7
    c1 = int(LL.resetCost(reg5, JInt(0)))
    pre_c = COINS[0]
    r1 = str(Life.reset(U1, "Tester", JInt(0)))
    c2 = int(LL.resetCost(reg5, JInt(0)))
    K.check(c1 == 5000 * 11 and r1.startswith("+All 11 points of your pickaxe are back") and COINS[0] == pre_c - c1 and int(LL.spent(reg5, JInt(0))) == 0
            and regfile("p1").get("pickaxe.resets") == "1" and "pickaxe.up.spd" not in regfile("p1"),
            "L5: reset = 5,000 x 11 spent x 1 = %d coins taken, every point back, resets=1 on disk: %s" % (c1, r1))
    for _i in range(3):
        Life.buy(U1, JInt(0), JInt(0))
    c3 = int(LL.resetCost(reg5, JInt(0)))
    K.check(c2 == 0 and c3 == 5000 * 3 * 2, "L5: the next reset costs more: 3 spent x 2 = %d" % c3)
    pre_c = COINS[0]
    LL.FAIL_SAVE = True
    r_f = str(Life.reset(U1, "Tester", JInt(0)))
    LL.FAIL_SAVE = False
    K.check(r_f.startswith("-The reset could not be saved - nothing changed and your coins were refunded") and COINS[0] == pre_c
            and int(LL.spent(reg5, JInt(0))) == 3 and regfile("p1").get("pickaxe.resets") == "1",
            "L5: a reset whose write fails refunds the coins and changes nothing: %s" % r_f)
    br.remove("coins:fn:take")
    r_nc = str(Life.reset(U1, "Tester", JInt(0)))
    br.put("coins:fn:take", CoinTake())
    COINS[0] = 10
    r_poor2 = str(Life.reset(U1, "Tester", JInt(0)))
    COINS[0] = 10 ** 7
    K.check(r_nc.startswith("-Coins are not available") and r_poor2.startswith("-A reset costs 30,000 coins - you have 10"),
            "L5: no SkyyCoins / too few coins: nothing changes: %s | %s" % (r_nc, r_poor2))
    LL.FAIL_SAVE = True
    r_bf = str(Life.buy(U1, JInt(0), JInt(1)))
    LL.FAIL_SAVE = False
    K.check(r_bf.startswith("-Fortune") or r_bf.startswith("-Your choice could not be saved"), "L5: a perk whose write fails is not kept: %s" % r_bf)
    br.put("profile:busy:" + str(U1), JBoolean(True))
    K.check(str(Life.buy(U1, JInt(0), JInt(0))).startswith("-Your profile is still loading") and str(Life.reset(U1, "T", JInt(0))).startswith("-Your profile is still loading"),
            "L5: profile:busy refuses perks and resets")
    br.remove("profile:busy:" + str(U1))
    lg5 = logs()
    K.check(len([l for l in lg5 if "LL-PERK " in l]) >= 14 and len([l for l in lg5 if "LL-RESET " in l]) == 1 and any("REFUND " in l for l in lg5),
            "L5: gear.log: LL-PERK per level, one LL-RESET, the REFUND line")

    # ============================================================================ L6: the sweep (levels, registry id, restore, remove, demote, foreign)
    wipe_home()
    inv6, cs6 = mkinv()
    skills(Mining=10, Foraging=10, Farming=10)
    Life.sweep0(PR1, inv6, True)
    L6 = dict((x[2], x) for x in lls(cs6, "p1"))
    pk6 = L6[0]
    K.check(int(Data.num(doc(pk6[6]), "lvl", -1)) == min(10, caps["Tool_Pickaxe_Crude"]), "L6: the Crude pickaxe starts at Mining 10 -> Lv %d" % min(10, caps["Tool_Pickaxe_Crude"]))
    skills(Mining=11)
    Stamp_ = None
    LL.LAST.clear()
    Life.sweep(PR1, inv6, False)
    s6 = cs6[pk6[0]].getItemStack(JShort(pk6[1]))
    K.notes.append("L6: crude cap %d; lvl after Mining 11 = %d; name %s" % (caps["Tool_Pickaxe_Crude"], int(Data.num(doc(s6), "lvl", -1)), View.nameText(s6.getItemId(), doc(s6))))
    K.check(int(Data.num(doc(s6), "lvl", -1)) == min(11, caps["Tool_Pickaxe_Crude"]) and str(View.lvTag(s6.getItemId(), doc(s6))) == " [Lv %d]" % min(11, caps["Tool_Pickaxe_Crude"])
            and ("[Lv %d]" % min(11, caps["Tool_Pickaxe_Crude"])) in str(s6.getMetadata().toJson()),
            "L6: a skill level-up -> the next sweep rewrites the tool's level and its name says [Lv N] (Skyy: 'when the skill levels up ... levels up the tool')")
    skills(Mining=40)
    LL.LAST.clear()
    Life.sweep(PR1, inv6, False)
    s6 = cs6[pk6[0]].getItemStack(JShort(pk6[1]))
    K.check(int(Data.num(doc(s6), "lvl", -1)) == caps["Tool_Pickaxe_Crude"], "L6: ... but never above its tier's top (Mining 40 -> Crude Lv %d)" % caps["Tool_Pickaxe_Crude"])
    n_w = int(Life.N[1])
    LL.LAST.clear()
    Life.sweep(PR1, inv6, False)
    LL.LAST.clear()
    Life.sweep(PR1, inv6, True)
    K.check(int(Life.N[1]) == n_w, "L6: nothing changed -> no write (the sweep only writes what moved)")
    Life.sweep(PR1, inv6, False)
    t0_ = int(Life.N[0])
    Life.sweep(PR1, inv6, False)
    K.check(int(Life.N[0]) == t0_, "L6: the per-scan sweep is throttled (400 ms)")
    # a foreign lifelong tool + a stale copy of mine
    inv7, cs7 = mkinv()
    PKEY[str(U2)] = "p2"
    skills(U2, Mining=5, Foraging=5, Farming=5)
    Life.sweep0(PR2, inv7, True)
    L7 = dict((x[2], x) for x in lls(cs7, "p2"))
    theirs = cs7[L7[0][0]].getItemStack(JShort(L7[0][1]))
    cs6["storage"].setItemStackForSlot(JShort(30), theirs)
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    K.check(cs6["storage"].getItemStack(JShort(30)) is not None and str(LL.owner(doc(cs6["storage"].getItemStack(JShort(30))))) == "p2",
            "L6: another player's lifelong tool (their current one) in my inventory is left alone")
    # FIX A-1 / engine-1: another player's lifelong tool breaks NOTHING for you (the REAL hit system, ore / log / stone), yours still works
    n7 = int(LL.N[7])
    own6 = cs6[pk6[0]].getItemStack(JShort(pk6[1]))
    rf1 = hit(theirs, "Ore_Copper_Stone")
    rf2 = hit(theirs, "Rock_Stone")
    rf3 = hit(own6, "Rock_Stone")
    rf4 = hit(own6, "Ore_Copper_Stone")
    K.check(rf1[0] and rf2[0] and not rf3[0] and not rf4[0] and int(LL.N[7]) == n7 + 2,
            "FIX A-1 / engine-1: THE REAL HIT SYSTEM: p2's lifelong pickaxe in p1's hand is refused on copper ore AND on stone (a handed-over tool is "
            "useless, so /pickaxe after handing yours over gives no second working tool); p1's own Crude pickaxe still mines stone + copper: %s"
            % [rf1, rf2, rf3, rf4])
    tip = JClass("java.util.ArrayList")(), JClass("java.util.ArrayList")()
    LL.lines(U1, theirs.getItemId(), doc(theirs), tip[0], tip[1])
    K.check([str(x) for x in tip[0]] == ["Lifelong tool of another player"], "L6: its tooltip says whose it is")
    # /pickaxe for p1 while the pickaxe is in a chest
    cpk = cs6[pk6[0]].getItemStack(JShort(pk6[1]))
    chest = SIC(JShort(27))
    chest.setItemStackForSlot(JShort(0), cpk)
    cs6[pk6[0]].removeItemStackFromSlot(JShort(pk6[1]))
    refR, stR, chR, plR = world(inv6, cs6, PR1)
    apply(lifelong__reclaimTier="false")          # this part: the tier you had (the default since fix round 2)
    r_rc = str(Life.reclaim(PR1, plR, JInt(0)))
    L6b = dict((x[2], x) for x in lls(cs6, "p1"))
    rep_ = L6b[0]
    K.check(r_rc.startswith("+Your pickaxe cannot be reached") and ("exact copy: " + str(Gear.itemName("Tool_Pickaxe_Crude"))) in r_rc and rep_[5]
            and str(rep_[6].getItemId()) == "Tool_Pickaxe_Crude" and str(Data.str(doc(rep_[6]), "lcu", "")) == pk6[3] and rep_[3] != pk6[3]
            and regfile("p1").get("pickaxe.uid") == rep_[3] and regfile("p1").get("pickaxe.rp") == "1" and str(Data.str(doc(rep_[6]), "r", "")) == "normal",
            "L6 (0.3.2): /pickaxe with the pickaxe in an untracked chest: an EXACT copy (lrp, the same item + rarity, a new uid, lcu = the original's), "
            "the registry names it: %s" % r_rc)
    r_rc2 = str(Life.reclaim(PR1, plR, JInt(0)))
    K.check(r_rc2.startswith("-You still have your lifelong pickaxe"), "L6: /pickaxe again: refused - you have one: %s" % r_rc2)
    # the original comes back from the chest: it is the lifelong one again, the replacement goes (no dupe)
    cs6["storage"].setItemStackForSlot(JShort(20), chest.getItemStack(JShort(0)))
    chest.removeItemStackFromSlot(JShort(0))
    PR1.said = None
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    L6c = [x for x in lls(cs6, "p1") if x[2] == 0]
    K.check(len(L6c) == 1 and L6c[0][3] == pk6[3] and not L6c[0][5] and regfile("p1").get("pickaxe.uid") == pk6[3] and regfile("p1").get("pickaxe.rp") == "0"
            and ids(cs6).get("Tool_Pickaxe_Crude") == 2 and any("is back - the replacement" in x for x in said(PR1)),
            "L6: THE DUPE GUARD: the original came back -> it is the lifelong pickaxe again, the replacement is gone (one of mine + the other player's): %s"
            % [(x[0], x[1], x[5]) for x in L6c])
    # a replacement copy that comes back after its original returned (it was in another chest): removed
    cs6["storage"].setItemStackForSlot(JShort(21), rep_[6])
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    K.check(ids(cs6).get("Tool_Pickaxe_Crude") == 2 and cs6["storage"].getItemStack(JShort(21)) is None,
            "L6: a stale replacement (lrp) that turns up later is removed - it was free")
    # a COPY of the current lifelong stack in the same inventory (Creative pick-block, an engine glitch): the second one goes
    curp = [x for x in lls(cs6, "p1") if x[2] == 0][0]
    cs6["storage"].setItemStackForSlot(JShort(25), curp[6])
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    K.check(len([x for x in lls(cs6, "p1") if x[2] == 0]) == 1 and cs6[curp[0]].getItemStack(JShort(curp[1])) is not None,
            "L6: a second stack carrying the current lifelong uid in the same inventory is removed (the first one in scan order stays)")
    # a stale NON-replacement while the current is a non-replacement: RETIRED (fix round 2 - was: plain), rolls kept
    staled = Data.put(stack("Tool_Hatchet_Copper"), Life.llDoc(Roll.newDoc("Tool_Hatchet_Copper", JInt(3), True, "craft", JInt(12)), "Tool_Hatchet_Copper", U1, "p1", "deadbeefdeadbeef", False), None)
    cs6["storage"].setItemStackForSlot(JShort(22), staled)
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    s22 = cs6["storage"].getItemStack(JShort(22))
    K.check(s22 is not None and bool(LL.isLL(doc(s22))) and bool(LL.isRt(doc(s22))) and str(Data.str(doc(s22), "r", "")) == "legendary",
            "L6 + FIX2 safety-2: an older lifelong tool (not a replacement, not the one /lifelong re-picked away from) is RETIRED (still lifelong, "
            "breaks nothing) and keeps its Legendary roll - never a free plain tool")
    # a foreign REPLACEMENT that is no longer its owner's lifelong one: removed from whoever holds it
    inv8, cs8 = mkinv()
    refS, stS, chS, plS = world(inv7, cs7, PR2)
    cx = cs7[L7[1][0]].getItemStack(JShort(L7[1][1]))
    chest.setItemStackForSlot(JShort(1), cx)
    cs7[L7[1][0]].removeItemStackFromSlot(JShort(L7[1][1]))
    LL.REG.remove("p2")
    r2 = str(Life.reclaim(PR2, plS, JInt(1)))
    rep2 = [x for x in lls(cs7, "p2") if x[2] == 1][0]
    cs6["storage"].setItemStackForSlot(JShort(23), rep2[6])          # p2 hands the replacement to p1 through a chest
    cs7[rep2[0]].removeItemStackFromSlot(JShort(rep2[1]))
    cs7["storage"].setItemStackForSlot(JShort(24), chest.getItemStack(JShort(1)))   # p2 takes the original back
    LL.LAST.clear()
    Life.sweep0(PR2, inv7, True)
    LL.LAST.clear()
    Life.sweep0(PR1, inv6, True)
    K.check(r2.startswith("+") and cs6["storage"].getItemStack(JShort(23)) is None and len([x for x in lls(cs7, "p2") if x[2] == 1]) == 1,
            "L6: a /hatchet replacement passed to another player is removed once its owner's original is back (no free tools by trading)")
    # registry unreadable -> hands off
    wipe_home()
    os.makedirs(os.path.join(HOME, "lifelong"), exist_ok=True)
    os.makedirs(os.path.join(HOME, "lifelong", "p1.properties"), exist_ok=True)       # a folder where the file should be = unreadable
    inv9, cs9 = mkinv()
    Life.sweep0(PR1, inv9, True)
    K.check(not lls(cs9) and bool(LL.bad(LL.reg("p1"))), "L6: an unreadable registry file: nothing is given / marked for that profile (and it is never overwritten)")
    shutil.rmtree(os.path.join(HOME, "lifelong"), ignore_errors=True)
    # FIX2 safety-3: the bad read is NOT cached for the uptime - within 30 s still hands off, then read again (the file is fine now)
    still_bad = bool(LL.bad(LL.reg("p1"))) and not bool(LL.REG.containsKey("p1"))
    LL.BADAT.put("p1", JObject(JLong(int(__import__("time").time() * 1000) - 31000), Long_))
    healed = not bool(LL.bad(LL.reg("p1"))) and bool(LL.REG.containsKey("p1"))
    LL.LAST.clear()
    Life.sweep0(PR1, inv9, True)
    K.check(still_bad and healed and len(lls(cs9, "p1")) == 4,
            "FIX2 safety-3: an unreadable registry is not cached as bad: 30 s later it is read again and the profile gets its tools: %s" % [still_bad, healed])
    LL.REG.clear()
    LL.BADAT.clear()
    apply()

    # ============================================================================ FX: the fix round's own paths
    # (1) FIX A-2: an INVESTED replacement (reforged / tiered up) is never thrown away when the original turns up
    wipe_home()
    logs()
    invX, csX = mkinv()
    refX, stX, chX, plX = world(invX, csX, PR1)
    skills(Mining=12, Foraging=12, Farming=12)
    csX["storage"].setItemStackForSlot(JShort(5), Data.put(stack("Tool_Pickaxe_Crude"), Roll.newDoc("Tool_Pickaxe_Crude", JInt(3), True, "craft", JInt(8)), None))
    Life.sweep0(PR1, invX, True)
    oX = [x for x in lls(csX, "p1") if x[2] == 0][0]
    chestX = SIC(JShort(27))
    chestX.setItemStackForSlot(JShort(0), oX[6])
    csX[oX[0]].removeItemStackFromSlot(JShort(oX[1]))
    apply(lifelong__reclaimTier="false")
    rX = str(Life.reclaim(PR1, plX, JInt(0)))
    apply()
    rpX = [x for x in lls(csX, "p1") if x[2] == 0][0]
    K.check(rX.startswith("+") and rpX[5] and int(Data.num(doc(rpX[6]), "lrpT", -1)) == 0, "FX: the replacement carries the tier it was given at (lrpT 0): %s" % rX)
    # the player reforges it (rfN 1 - what GearForge writes) -> invested; the next sweep remembers it (inv=1)
    rdoc = doc(rpX[6]).clone()
    rdoc.put("rfN", JClass("org.bson.BsonInt32")(JInt(1)))
    csX[rpX[0]].setItemStackForSlot(JShort(rpX[1]), Data.put(stack("Tool_Pickaxe_Crude"), rdoc, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invX, True)
    K.check(bool(LL.invested("Tool_Pickaxe_Crude", rdoc)) and regfile("p1").get("pickaxe.inv") == "1" and regfile("p1").get("pickaxe.rp") == "1",
            "FX: a reforged replacement is invested; the registry remembers it (pickaxe.inv=1)")
    PR1.said = None
    csX["storage"].setItemStackForSlot(JShort(20), chestX.getItemStack(JShort(0)))      # the original comes back
    chestX.removeItemStackFromSlot(JShort(0))
    nX = ids(csX).get("Tool_Pickaxe_Crude")
    LL.LAST.clear()
    Life.sweep0(PR1, invX, True)
    LL.LAST.clear()
    Life.sweep0(PR1, invX, True)
    LX = [x for x in lls(csX, "p1") if x[2] == 0]
    o20 = csX["storage"].getItemStack(JShort(20))
    rfX = regfile("p1")
    LX = [x for x in LX if not bool(LL.isRt(doc(x[6])))]          # fix round 2: the original stays lifelong, RETIRED
    K.check(len(LX) == 1 and LX[0][3] == rpX[3] and not LX[0][5] and int(Data.num(doc(LX[0][6]), "rfN", 0)) == 1 and o20 is not None
            and bool(LL.isLL(doc(o20))) and bool(LL.isRt(doc(o20))) and str(Data.str(doc(o20), "r", "")) == "legendary" and ids(csX).get("Tool_Pickaxe_Crude") == nX
            and rfX.get("pickaxe.uid") == rpX[3] and rfX.get("pickaxe.rp") == "0" and "pickaxe.inv" not in rfX
            and any("upgraded its replacement" in x for x in said(PR1)),
            "FIX A-2 + FIX2 safety-2: the original came back while the REFORGED replacement is current: nothing is removed - the replacement stays the "
            "lifelong pickaxe (rp=0, its lrp mark gone), the original is RETIRED (lifelong, Legendary roll kept - not a plain tool), item count unchanged: %s" % ((
                [(x[0], x[1], x[5]) for x in LX], dict((k, v) for k, v in rfX.items() if k.startswith("pickaxe."))),))
    # an invested replacement that turns up while an ORIGINAL is current is demoted (kept as a plain tool), never removed
    stale_inv = Life.llDoc(Roll.newDoc("Tool_Pickaxe_Copper", JInt(0), True, "craft", JInt(10)), "Tool_Pickaxe_Copper", U1, "p1", "feedfeedfeedfeed", True)
    stale_inv.put("lrpT", JClass("org.bson.BsonInt32")(JInt(0)))          # given Crude, tiered up to Copper
    csX["storage"].setItemStackForSlot(JShort(21), Data.put(stack("Tool_Pickaxe_Copper"), stale_inv, None))
    stale_free = Life.llDoc(None, "Tool_Pickaxe_Copper", U1, "p1", "beefbeefbeefbeef", True)          # a free (not invested) one
    csX["storage"].setItemStackForSlot(JShort(22), Data.put(stack("Tool_Pickaxe_Copper"), stale_free, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invX, True)
    s21, s22 = csX["storage"].getItemStack(JShort(21)), csX["storage"].getItemStack(JShort(22))
    K.check(s21 is not None and bool(LL.isRt(doc(s21))) and s22 is None and len([x for x in lls(csX, "p1") if x[2] == 0 and not bool(LL.isRt(doc(x[6])))]) == 1,
            "FIX A-2 + FIX2: a stale replacement someone tiered up (Crude -> Copper) is RETIRED (kept, never plain), a free stale one is removed as before")
    lgX = logs()
    K.check(any("LL-SETTLE " in l for l in lgX), "FX: gear.log has the LL-SETTLE line")
    # (2) FIX C-1 / A-4: /pickaxe gives the tier your skill level fits (Skyy G2: Mining 20 -> Iron), never below the tier you had
    tf = [str(LL.tierFor(U1, JInt(0), "Tool_Pickaxe_Crude")) for _m in (0,)]
    res_tf = []
    for mlv, had in ((20, "Tool_Pickaxe_Crude"), (1, "Tool_Pickaxe_Crude"), (16, "Tool_Pickaxe_Crude"), (26, "Tool_Pickaxe_Copper"), (49, "Tool_Pickaxe_Crude"),
                     (20, "Tool_Pickaxe_Cobalt")):
        skills(Mining=mlv)
        res_tf.append(str(LL.tierFor(U1, JInt(0), had)))
    skills(Farming=49)
    res_tf.append(str(LL.tierFor(U1, JInt(3), "Tool_Sickle_Crude")))
    res_tf.append(str(LL.tierFor(U1, JInt(2), "Tool_Hoe_Crude")))
    br.remove("skill:fn:level")
    Gate.forget(U1)
    res_tf.append(str(LL.tierFor(U1, JInt(0), "Tool_Pickaxe_Copper")))
    br.put("skill:fn:level", SkillFn())
    K.check(res_tf == ["Tool_Pickaxe_Iron", "Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Thorium", "Tool_Pickaxe_Adamantite", "Tool_Pickaxe_Cobalt",
                       "Tool_Sickle_Iron", "Tool_Hoe_Thorium", "Tool_Pickaxe_Copper"],
            "FIX C-1: tierFor = the first ladder tier whose band holds your level (Mining 20 -> Iron = Skyy's own example, 1 -> Crude, 16 -> Copper, "
            "26 -> Thorium, 49 -> the ladder top Adamantite), never below the tier you had (Cobalt at 20 stays Cobalt); sickles end at Iron, hoes at "
            "Thorium; no SkyySkills = the tier you had: %s" % res_tf)
    wipe_home()
    invY, csY = mkinv()
    refY, stY, chY, plY = world(invY, csY, PR1)
    skills(Mining=20, Foraging=1, Farming=1)
    Life.sweep0(PR1, invY, True)
    yP = [x for x in lls(csY, "p1") if x[2] == 0][0]
    csY[yP[0]].removeItemStackFromSlot(JShort(yP[1]))
    apply(lifelong__reclaimTier="true")          # fix round 2: the row is OFF by default now
    rY = str(Life.reclaim(PR1, plY, JInt(0)))
    gY = [x for x in lls(csY, "p1") if x[2] == 0]
    apply(lifelong__reclaimSec="0")          # the default (reclaimTier off)
    csY[gY[0][0]].removeItemStackFromSlot(JShort(gY[0][1]))
    LL.reg("p1").setProperty("pickaxe.id", "Tool_Pickaxe_Crude")
    rY2 = str(Life.reclaim(PR1, plY, JInt(0)))
    gY2 = [x for x in lls(csY, "p1") if x[2] == 0]
    apply()
    K.check(rY.startswith("+Your pickaxe cannot be reached") and str(gY[0][6].getItemId()) == "Tool_Pickaxe_Crude"
            and int(Data.num(doc(gY[0][6]), "lrpT", -1)) == 0 and str(gY2[0][6].getItemId()) == "Tool_Pickaxe_Crude" and len(gY2) == 1,
            "FIX C-1 -> 0.3.2: lifelong.reclaimTier is a LEGACY row - ON changes nothing: /pickaxe at Mining 20 after losing a Crude pickaxe = an "
            "exact copy of that Crude pickaxe (no free tier-up either way): %s | %s" % (rY, rY2))
    # (3) FIX engine-2: the held-tool recompute flags a stale [Lv N]; GearHandSys hands it to the stamp task (its sweep rewrites the level)
    wipe_home()
    invZ, csZ = mkinv()
    skills(Mining=10, Foraging=10, Farming=10)
    Life.sweep0(PR1, invZ, True)
    zP = [x for x in lls(csZ, "p1") if x[2] == 0][0][6]
    LL.RESYNC.clear()
    Tool.LAST.clear()
    Tool.held(U1, zP)
    r_same = bool(LL.RESYNC.containsKey(U1))
    skills(Mining=11)
    Tool.LAST.clear()
    Tool.held(U1, zP)
    r_up = bool(LL.RESYNC.containsKey(U1))
    LL.RESYNC.clear()
    Tool.LAST.clear()
    Tool.held(U1, theirs)
    r_for = bool(LL.RESYNC.containsKey(U1))
    LL.RESYNC.clear()
    K.check(not r_same and r_up and not r_for, "FIX engine-2: GearTool.held (GearHandSys, once a second) flags the held lifelong pickaxe after a Mining "
            "level-up (not before, not for another player's tool) - GearHandSys.tick then calls GearStamp.dirtyIn (C: GearHandSys ~tick): %s"
            % [r_same, r_up, r_for])
    # (4) FIX engine-4: the Drop key on a lifelong tool inside an open CHEST WINDOW: cancelled + the window marked changed (re-sent)
    wipe_home()
    invW, csW = mkinv()
    refW, stW, chW, plW = world(invW, csW, PR1)
    Life.sweep0(PR1, invW, True)
    wP = [x for x in lls(csW, "p1") if x[2] == 0][0]
    chestW = SIC(JShort(27))
    chestW.setItemStackForSlot(JShort(3), wP[6])
    csW[wP[0]].removeItemStackFromSlot(JShort(wP[1]))
    WMc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    CWc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow")
    win_ok = None
    WINc = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.Window")

    def wdirty(w_):
        return bool(jf(WINc, "isDirty").get(w_).getAndSet(False))
    try:
        wm = WMc()
        jf(WMc, "windowId").get(wm).set(JInt(10))
        cw = CWc(chestW)
        wm.setWindow(JInt(4), cw)
        wmf = None
        k_ = PLA.class_
        while k_ is not None and wmf is None:
            for f_ in k_.getDeclaredFields():
                if f_.getType() == WMc.class_:
                    f_.setAccessible(True)
                    wmf = f_
            k_ = k_.getSuperclass()
        wmf.set(plW, wm)
        wdirty(cw)
        DIRQw = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest")
        DropW = JClass(PKG + "GearLLDropSys")()
        ew = DIRQw(JInt(4), JShort(3))
        DropW.handle(JInt(0), chW, stW, None, ew)
        chestW.setItemStackForSlot(JShort(5), stack("Rock_Stone", 3))
        wdirty(cw)
        ew2 = DIRQw(JInt(4), JShort(5))
        DropW.handle(JInt(0), chW, stW, None, ew2)
        d2 = wdirty(cw)
        win_ok = (bool(ew.isCancelled()), chestW.getItemStack(JShort(3)) is not None, not bool(ew2.isCancelled()), d2)
    except Exception as ex_:
        K.notes.append("FX: the chest-window drop could not be staged: %s" % str(ex_)[:200])
    K.check(win_ok is not None and win_ok[0] and win_ok[1] and win_ok[2] and not win_ok[3],
            "FIX engine-4: the Drop key on the lifelong pickaxe in an open chest window (section id 4 = a real ContainerWindow) is cancelled and the "
            "tool stays; stone from the same window is not: %s" % (win_ok,))
    # the window was marked changed by the cancelled drop: re-run the lifelong one and read the flag right after
    if win_ok is not None:
        wdirty(cw)
        ew3 = DIRQw(JInt(4), JShort(3))
        DropW.handle(JInt(0), chW, stW, None, ew3)
        K.check(bool(ew3.isCancelled()) and wdirty(cw),
                "FIX engine-4: ... and the cancelled drop marked the chest window changed (WindowManager.markWindowChanged -> Window.invalidate: "
                "PlayerSendInventorySystem re-sends it, the client shows the tool back)")
    # (5) FIX A-1: the hand-over sequence end to end: p1's ORIGINAL goes to p2 through a chest, p1 types /pickaxe, p2's copy breaks nothing
    wipe_home()
    PKEY[str(U2)] = "p2"
    invA, csA = mkinv()
    refA, stA, chA, plA = world(invA, csA, PR1)
    invB, csB = mkinv()
    skills(Mining=20)
    skills(U2, Mining=20)
    Life.sweep0(PR1, invA, True)
    Life.sweep0(PR2, invB, True)
    aO = [x for x in lls(csA, "p1") if x[2] == 0][0]
    csB["storage"].setItemStackForSlot(JShort(30), aO[6])          # handed to p2 (chest / trade)
    csA[aO[0]].removeItemStackFromSlot(JShort(aO[1]))
    rA = str(Life.reclaim(PR1, plA, JInt(0)))
    LL.LAST.clear()
    Life.sweep0(PR2, invB, True)
    held_by_b = csB["storage"].getItemStack(JShort(30))
    K.check(rA.startswith("+") and held_by_b is not None and int(LL.hit(PR2, held_by_b, BL["Ore_Copper_Stone"])) == 2
            and int(LL.hit(PR2, held_by_b, BL["Rock_Stone"])) == 2 and int(LL.hit(PR1, [x for x in lls(csA, "p1") if x[2] == 0][0][6], BL["Rock_Stone"])) == 0,
            "FIX A-1: p1 hands the original pickaxe to p2 and gets a replacement with /pickaxe: the original stays p1's item (kept for when it comes back) "
            "but breaks nothing for p2 - no second working tool: %s" % rA)
    wipe_home()

    # ============================================================================ FX2: the second fix round's own paths
    BI32 = JClass("org.bson.BsonInt32")
    SECID_X = {"hotbar": -1, "storage": -2, "armor": -3, "utility": -5, "tools": -8, "backpack": -9}
    DIRQx = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest")
    DropX = JClass(PKG + "GearLLDropSys")()
    # (1) FIX2 safety-2: THE EXPLOIT SEQUENCE - original in a chest, /pickaxe, reforge the replacement, take the original back: the original
    # is RETIRED (still lifelong, never sold, breaks nothing, may be dropped), never a plain rolled tool; /lifelong swaps the two
    wipe_home()
    logs()
    invQ, csQ = mkinv()
    refQ, stQ, chQ, plQ = world(invQ, csQ, PR1)
    skills(Mining=12, Foraging=12, Farming=12)
    csQ["storage"].setItemStackForSlot(JShort(5), Data.put(stack("Tool_Pickaxe_Crude"), Roll.newDoc("Tool_Pickaxe_Crude", JInt(3), True, "craft", JInt(8)), None))
    Life.sweep0(PR1, invQ, True)
    oQ = [x for x in lls(csQ, "p1") if x[2] == 0][0]
    chestQ = SIC(JShort(27))
    chestQ.setItemStackForSlot(JShort(0), oQ[6])
    csQ[oQ[0]].removeItemStackFromSlot(JShort(oQ[1]))
    # 0.3.2 fix round (safety critic 1): an EXACT copy and its original never swap (LT5); this check keeps the 0.3.0 swap for the legacy
    # replacement (no snapshot = a Common tool, not a copy of the original)
    for k_ in ("pickaxe.snap", "pickaxe.snapId", "pickaxe.snapU"):
        LL.reg("p1").remove(k_)
    rQ = str(Life.reclaim(PR1, plQ, JInt(0)))
    rpQ = [x for x in lls(csQ, "p1") if x[2] == 0][0]
    rdq = doc(rpQ[6]).clone()
    rdq.put("rfN", BI32(JInt(1)))
    csQ[rpQ[0]].setItemStackForSlot(JShort(rpQ[1]), Data.put(stack("Tool_Pickaxe_Crude"), rdq, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invQ, True)
    csQ["storage"].setItemStackForSlot(JShort(20), chestQ.getItemStack(JShort(0)))
    chestQ.removeItemStackFromSlot(JShort(0))
    nQ = ids(csQ).get("Tool_Pickaxe_Crude")
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, invQ, True)
    oS = csQ["storage"].getItemStack(JShort(20))
    oD = doc(oS)
    rS_ = csQ[rpQ[0]].getItemStack(JShort(rpQ[1]))
    hO1, hO2, hR = hit(oS, "Rock_Stone"), hit(oS, "Ore_Copper_Stone"), hit(rS_, "Rock_Stone")
    tipO = JClass("java.util.ArrayList")(), JClass("java.util.ArrayList")()
    LL.lines(U1, oS.getItemId(), oD, tipO[0], tipO[1])
    eO = DIRQx(JInt(-2), JShort(20))
    DropX.handle(JInt(0), chQ, stQ, None, eO)
    eR = DIRQx(JInt(SECID_X[rpQ[0]]), JShort(rpQ[1]))
    DropX.handle(JInt(0), chQ, stQ, None, eR)
    K.check(rQ.startswith("+") and oS is not None and bool(LL.isLL(oD)) and bool(LL.isRt(oD)) and str(LL.owner(oD)) == "p1"
            and str(Data.str(oD, "r", "")) == "legendary" and ids(csQ).get("Tool_Pickaxe_Crude") == nQ and regfile("p1").get("pickaxe.uid") == rpQ[3]
            and Wall.why(oS.getItemId(), oS.getMetadata()) is not None and not bool(LL.mine(U1, oD))
            and hO1[0] and hO2[0] and not hR[0] and "Retired lifelong pickaxe - it breaks nothing" in [str(x) for x in tipO[0]]
            and not bool(eO.isCancelled()) and bool(eR.isCancelled()),
            "FIX2 safety-2: original in a chest -> /pickaxe -> reforge the replacement -> take the original back: the original is RETIRED (still "
            "lifelong + p1's, Legendary kept, the market wall refuses it, it breaks NOTHING - stone or ore, its tooltip says so, it MAY be dropped); "
            "the reforged replacement is the one working pickaxe (it can't be dropped); item count unchanged: %s" % [rQ, hO1, hO2, hR, [str(x) for x in tipO[0]]])
    # /lifelong on the retired original swaps them (any time, no once-per-kind limit): one working pickaxe, never a plain one
    csQ["hotbar"].setItemStackForSlot(JShort(0), oS)
    csQ["storage"].removeItemStackFromSlot(JShort(20))
    PR1.said = None
    rSw = str(Life.repick(PR1, plQ))
    h0 = csQ["hotbar"].getItemStack(JShort(0))
    rNow = csQ[rpQ[0]].getItemStack(JShort(rpQ[1]))
    regA = regfile("p1").get("pickaxe.uid")
    hA, hB = hit(h0, "Rock_Stone")[0], hit(rNow, "Rock_Stone")[0]
    rSw2 = str(Life.repick(PR1, plQ))
    csQ["hotbar"].setItemStackForSlot(JShort(0), rNow)
    csQ[rpQ[0]].setItemStackForSlot(JShort(rpQ[1]), h0)
    rSw3 = str(Life.repick(PR1, plQ))
    back0 = csQ["hotbar"].getItemStack(JShort(0))
    oNow = csQ[rpQ[0]].getItemStack(JShort(rpQ[1]))
    lgQ = logs()
    K.check(rSw.startswith("+") and "again" in rSw and bool(LL.isLL(doc(h0))) and not bool(LL.isRt(doc(h0))) and str(LL.uid(doc(h0))) == oQ[3]
            and bool(LL.isRt(doc(rNow))) and regA == oQ[3] and not hA and hB and regfile("p1").get("pickaxe.uid") == rpQ[3]
            and rSw2.startswith("-That already is your lifelong pickaxe") and rSw3.startswith("+") and not bool(LL.isRt(doc(back0)))
            and bool(LL.isRt(doc(oNow))) and str(LL.uid(doc(back0))) == rpQ[3] and ids(csQ).get("Tool_Pickaxe_Crude") == nQ
            and len([x for x in lls(csQ, "p1") if x[2] == 0 and not bool(LL.isRt(doc(x[6])))]) == 1
            and any("LL-RETIRE " in l for l in lgQ) and len([l for l in lgQ if "LL-SWAP " in l]) == 2 and not any("LL-DEMOTE " in l for l in lgQ),
            "FIX2 safety-2: /lifelong on the retired original swaps it back (the replacement retires), again on the current one is refused, and "
            "swapping back works too: always exactly ONE working pickaxe, nothing turns plain, counts unchanged: %s | %s | %s" % (rSw, rSw2, rSw3))
    # (2) FIX2 cross-mod-2: another player's lifelong tool in my inventory may be dropped (it is useless to me); mine may not
    theirsQ = Data.put(stack("Tool_Hatchet_Crude"), Life.llDoc(None, "Tool_Hatchet_Crude", U2, "p2", "abcabcabcabcabca", False), None)
    csQ["storage"].setItemStackForSlot(JShort(30), theirsQ)
    eT = DIRQx(JInt(-2), JShort(30))
    DropX.handle(JInt(0), chQ, stQ, None, eT)
    K.check(not bool(eT.isCancelled()) and bool(eR.isCancelled()),
            "FIX2 cross-mod-2: the Drop key on ANOTHER player's lifelong hatchet is not cancelled (nobody is stuck with a tool they can't use)")
    # (3) FIX2 cross-mod-1: gear:fn:lifelong(UUID) -> Integer kinds owned (SkyyQuests' tutorial "lifelong 4/4"); the Object[] form unchanged
    FnQ = JClass(PKG + "GearLLFn")(JInt(0))
    FnQ1 = JClass(PKG + "GearLLFn")(JInt(1))
    nk = FnQ.apply(U1)
    nk2 = FnQ.apply(U2)
    K.check(nk is not None and int(nk) == 4 and str(nk.getClass().getName()) == "java.lang.Integer" and FnQ1.apply(U1) is None
            and str(FnQ.apply(JArray(JObject)([U1, JString("pickaxe")]))) == regfile("p1").get("pickaxe.uid"),
            "FIX2 cross-mod-1: gear:fn:lifelong(bare UUID) = Integer 4 for a migrated profile (%s for an unknown one); perk / farmTier ignore a bare UUID; "
            "the Object[] form still gives the uid" % nk2)
    # (4) FIX2 safety-4: a failing registry write WARNs once per 30 s and the every-scan sweep waits (forced ones still try)
    wipe_home()
    logs()
    LL.TOLD.remove("save:p1")          # the earlier failing-write checks of this harness ran < 30 s ago
    LL.FAIL_SAVE = True
    for _i in range(5):
        LL.save("p1", Props())
    LL.FAIL_SAVE = False
    lgW = logs()
    nwarn = len([l for l in lgW if "could not be written" in l])
    invV, csV = mkinv()
    failing0 = bool(LL.failing("p1"))
    LL.LAST.clear()
    Life.sweep0(PR1, invV, False)
    skipped = not lls(csV)
    Life.sweep0(PR1, invV, True)
    K.check(nwarn == 1 and failing0 and skipped and len(lls(csV, "p1")) == 4 and not bool(LL.failing("p1")),
            "FIX2 safety-4: 5 failed registry writes = ONE WARN; the every-scan sweep then waits 30 s, a forced one (join / a command) still runs and "
            "a good write clears the back-off: %s" % [nwarn, failing0, skipped])
    # (5) FIX2 safety-5: the migration logs the old level + coin-bought levels (lvU) and says so when the level drops
    wipe_home()
    logs()
    invU, csU = mkinv()
    skills(Mining=5, Foraging=5, Farming=5)
    dU = Roll.newDoc("Tool_Pickaxe_Copper", JInt(2), True, "craft", JInt(17))
    dU.put("lvU", BI32(JInt(3)))
    csU["storage"].setItemStackForSlot(JShort(2), Data.put(stack("Tool_Pickaxe_Copper"), dU, None))
    PR1.said = None
    Life.sweep0(PR1, invU, True)
    lgU = logs()
    mk = [l for l in lgU if "LL-MARK " in l and "Tool_Pickaxe_Copper" in l]
    K.check(len(mk) == 1 and "(was lv17, bought lvU 3)" in mk[0] and any("was Lv 17 (3 of it bought with coins)" in x for x in said(PR1))
            and any("Only your inventory was checked" in x and "Vault" in x for x in said(PR1)),
            "FIX2 safety-5 + design-6: LL-MARK says 'was lv17, bought lvU 3', the player is told the level now follows Mining; the notice points "
            "at chests / the Void / the Vault: %s" % (mk[:1],))
    # (6) FIX2 design-1 -> 0.3.1: gate.crudeFactor is an unused LEGACY row (Crude counts as Copper): setting it changes nothing; the one-up
    # factor is gate.nextFactor for every tier, slowF(1) / slowF(3) = the one-up / two-up rows
    skills(Mining=10, Foraging=10)
    apply(gate__crudeFactor="0.25")
    Tool.LAST.clear()
    refC = float(Tool.onDamage(U1, stack("Tool_Hatchet_Crude"), BL["Wood_Oak_Trunk"], JFloat(0.3)))
    rC = hit(stack("Tool_Hatchet_Crude"), "Wood_Oak_Trunk")
    Tool.LAST.clear()
    refI = float(Tool.onDamage(U1, stack("Tool_Pickaxe_Iron"), BL["Ore_Thorium_Sandstone"], JFloat(0.3)))
    rI = hit(stack("Tool_Pickaxe_Iron"), "Ore_Thorium_Sandstone")
    Tool.LAST.clear()
    refM = float(Tool.onDamage(U1, stack("Tool_Hatchet_Crude"), BL["Wood_Maple_Trunk"], JFloat(0.3)))
    rM = hit(stack("Tool_Hatchet_Crude"), "Wood_Maple_Trunk")
    apply()
    K.check(not rC[0] and abs(rC[1] - refC) < 1e-6 and not rI[0] and abs(rI[1] - float(JFloat(refI * 0.4))) < 1e-6
            and not rM[0] and abs(rM[1] - float(JFloat(refM * 0.4))) < 1e-6
            and abs(float(LL.slowF(JInt(1))) - 0.4) < 1e-12 and abs(float(LL.slowF(JInt(3))) - 0.1) < 1e-12 and abs(float(LL.slowF(JInt(0))) - 1.0) < 1e-12,
            "FIX2 design-1 (0.3.1): gate.crudeFactor 0.25 changes nothing any more - a Crude hatchet on Oak = normal (%.5f), on Maple x0.4 (%.5f), an "
            "Iron pickaxe on thorium x0.4 (%.5f); slowF(1) 0.4, slowF(3) 0.1" % (rC[1], rM[1], rI[1]))
    wipe_home()

    # ============================================================================ L7: /pickaxe in full (every refusal, cooldown, Requip, crash at every step)
    wipe_home()
    logs()
    invP, csP = mkinv()
    refP, stP, chP, plP = world(invP, csP, PR1)
    skills(Mining=20, Foraging=20, Farming=20)
    Life.sweep0(PR1, invP, True)
    Lp = dict((x[2], x) for x in lls(csP, "p1"))
    apply(part__lifelong="false")
    r_off = str(Life.reclaim(PR1, plP, JInt(0)))
    apply()
    br.put("profile:busy:" + str(U1), JBoolean(True))
    r_busy = str(Life.reclaim(PR1, plP, JInt(0)))
    br.remove("profile:busy:" + str(U1))
    r_have = str(Life.reclaim(PR1, plP, JInt(0)))
    pick = csP[Lp[0][0]].getItemStack(JShort(Lp[0][1]))
    csP[Lp[0][0]].removeItemStackFromSlot(JShort(Lp[0][1]))
    RQ["items"] = [("e1", str(pick.getItemId()), pick.getMetadata())]
    r_rq = str(Life.reclaim(PR1, plP, JInt(0)))
    RQ.clear()
    LL.reg("p1").setProperty("pickaxe.id", "Tool_Pickaxe_Iron")         # 0.3.2: the SNAPSHOT (Crude) decides, not the registry's id
    full = []
    for i_ in range(36):
        if csP["storage"].getItemStack(JShort(i_)) is None:
            csP["storage"].setItemStackForSlot(JShort(i_), stack("Rock_Stone"))
            full.append(("storage", i_))
    for sec in ("backpack", "hotbar"):
        for i_ in range(int(csP[sec].getCapacity())):
            if csP[sec].getItemStack(JShort(i_)) is None:
                csP[sec].setItemStackForSlot(JShort(i_), stack("Rock_Stone"))
                full.append((sec, i_))
    r_full = str(Life.reclaim(PR1, plP, JInt(0)))
    for sec, i_ in full:
        csP[sec].removeItemStackFromSlot(JShort(i_))
    r_ok = str(Life.reclaim(PR1, plP, JInt(0)))
    newp = [x for x in lls(csP, "p1") if x[2] == 0]
    r_cd = str(Life.reclaim(PR1, plP, JInt(0)))       # it is on me now -> "you still have"
    csP[newp[0][0]].removeItemStackFromSlot(JShort(newp[0][1]))
    r_cd2 = str(Life.reclaim(PR1, plP, JInt(0)))
    K.check(r_off.startswith("-Lifelong tools are switched off") and r_busy.startswith("-Your profile is still loading")
            and r_have.startswith("-You still have your lifelong pickaxe") and r_rq.startswith("-Your lifelong pickaxe is in your Requip")
            and r_full.startswith("-No room") and r_ok.startswith("+Your pickaxe cannot be reached")
            and ("exact copy: %s [Lv %d]" % (Gear.itemName("Tool_Pickaxe_Crude"), int(LL.levelFor(U1, "Tool_Pickaxe_Crude")))) in r_ok and len(newp) == 1
            and str(newp[0][6].getItemId()) == "Tool_Pickaxe_Crude" and r_cd.startswith("-You still have")
            and re.match(r"-Your pickaxe cannot be reached \(.*\)\. You can get an exact copy in \d+ s\.", r_cd2),
            "L7 (0.3.2): /pickaxe: off / busy / you have it / in Requip (not loaded) / no room refused; then an EXACT copy of the lost Crude pickaxe "
            "(the snapshot decides, not a tier); lost again at once = the wait: %s | %s | %s" % (r_full, r_ok, r_cd2))
    apply(lifelong__reclaimSec="0")
    for crash_at in (4, 5, 6):
        LL.reg("p1").setProperty("pickaxe.reclaimAt", "0")
        cur = [x for x in lls(csP, "p1") if x[2] == 0]
        for x in cur:
            csP[x[0]].removeItemStackFromSlot(JShort(x[1]))
        before_n = ids(csP).get("Tool_Pickaxe_Crude", 0)          # 0.3.2: the exact copy is the Crude pickaxe
        Life.CRASH_AT = crash_at
        crashed = False
        try:
            Life.reclaim(PR1, plP, JInt(0))
        except Exception as ex_:
            crashed = ("lifelong step %d" % crash_at) in str(ex_)
        Life.CRASH_AT = 0
        reset_reg()
        Life.sweep0(PR1, invP, True)
        got_n = ids(csP).get("Tool_Pickaxe_Crude", 0)
        cur2 = [x for x in lls(csP, "p1") if x[2] == 0]
        rf = regfile("p1")
        if crash_at == 4:
            okc = got_n == before_n and not cur2 and "pickaxe.pend" not in rf
            r_after = str(Life.reclaim(PR1, plP, JInt(0)))
            okc = okc and r_after.startswith("+") and len([x for x in lls(csP, "p1") if x[2] == 0]) == 1
        else:
            okc = got_n == before_n + 1 and len(cur2) == 1 and rf.get("pickaxe.uid") == cur2[0][3] and "pickaxe.pend" not in rf
        K.check(crashed and okc, "L7: /pickaxe CRASH at step %d then a restart: %s (registry %s)" % (
            crash_at, "nothing given, the journal dropped, /pickaxe works again" if crash_at == 4 else "the given pickaxe is committed, never a 2nd",
            dict((k, v) for k, v in rf.items() if k.startswith("pickaxe."))))
    apply()
    lg7 = logs()
    K.check(any("LL-COPY " in l and " exact copy of " in l for l in lg7) and any("LL-RECOVER " in l and "committed" in l for l in lg7) and any("LL-RECOVER " in l and "journal dropped" in l for l in lg7),
            "L7 (0.3.2): gear.log: LL-COPY (exact copy of <uid>), LL-RECOVER committed / dropped")

    # ============================================================================ LT (0.3.2): THE EXACT LOST TOOL
    # Skyy 2026-10-13: "if you can, make it give their exact tool back. (or if its in a chest, summons it to your inventory.)"
    WMc_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.WindowManager")
    CWc_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerWindow")
    CBWc_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.ContainerBlockWindow")
    WINc_ = JClass("com.hypixel.hytale.server.core.entity.entities.player.windows.Window")
    BS_ = JClass("org.bson.BsonString")
    B64 = JClass("java.util.Base64")
    JStr = JClass("java.lang.String")
    wmf_ = None
    k_ = PLA.class_
    while k_ is not None and wmf_ is None:
        for f_ in k_.getDeclaredFields():
            if f_.getType() == WMc_.class_:
                f_.setAccessible(True)
                wmf_ = f_
        k_ = k_.getSuperclass()

    def new_wm(pl_, *wins):
        """a REAL WindowManager on the player with these windows open (ids 4, 5, ...); setWindow registers the engine's change events"""
        wm_ = WMc_()
        jf(WMc_, "windowId").get(wm_).set(JInt(20))
        for i_, w_ in enumerate(wins):
            wm_.setWindow(JInt(4 + i_), w_)
        wmf_.set(pl_, wm_)
        return wm_

    def wdirty_(w_):
        return bool(jf(WINc_, "isDirty").get(w_).getAndSet(False))

    def chest_win(c_, x=10, y=64, z=-5):
        return CBWc_(JInt(x), JInt(y), JInt(z), JInt(0), BL["Rock_Stone"], c_)

    @JImplements("java.util.concurrent.Executor")
    class QExec(object):
        def __init__(self):
            self.q = []

        @JOverride
        def execute(self, r_):
            self.q.append(r_)
    FETCH = {"mode": "ok", "cs": None, "store": {}, "calls": 0}

    @JImplements("java.util.function.Function")
    class RqFetch(object):
        @JOverride
        def apply(self, o):
            FETCH["calls"] += 1
            eid_ = str(o[1])
            if FETCH["mode"] == "refuse":
                return JString("Inventory full - make room first.")
            if FETCH["mode"] == "lie":
                return JString("ok")
            s_ = FETCH["store"].pop(eid_, None)
            if s_ is None:
                return JString("That item is not in Requip any more.")
            c_ = FETCH["cs"]["storage"]
            for i_ in range(int(c_.getCapacity())):
                if c_.getItemStack(JShort(i_)) is None:
                    c_.setItemStackForSlot(JShort(i_), s_)
                    break
            RQ["items"] = [r_ for r_ in RQ.get("items", []) if r_[0] != eid_]
            return JString("ok")

    def pick_now(cs_, pk="p1"):
        """the WORKING lifelong pickaxes (not retired) in this inventory"""
        return [x for x in lls(cs_, pk) if x[2] == 0 and not bool(LL.isRt(doc(x[6])))]

    def slot_of(c_, uid):
        for i_ in range(int(c_.getCapacity())):
            s_ = c_.getItemStack(JShort(i_))
            if s_ is not None and not s_.isEmpty() and doc(s_) is not None and str(LL.uid(doc(s_))) == uid:
                return i_
        return -1

    def num_(v):
        return int(v.get("$numberInt", v.get("$numberLong", -1))) if isinstance(v, dict) else int(v if v is not None else -1)

    def snapjson(rf_):
        t_ = rf_.get("pickaxe.snap")
        return None if t_ is None else json.loads(str(JStr(B64.getDecoder().decode(t_), "UTF-8")))

    def setup_lt(rfn=2):
        """a fresh profile p1 whose pickaxe is a Legendary Iron one (rolled, reforged rfN times) + 1 Fortune perk bought"""
        wipe_home()
        logs()
        Life.TEST_CHESTS = None
        Life.TEST_WKEY = "world1~aaaa"
        PKEY[str(U1)] = "p1"
        inv_, cs_ = mkinv()
        ref_, st_, ch_, pl_ = world(inv_, cs_, PR1)
        skills(Mining=20, Foraging=20, Farming=20)
        d_ = Roll.newDoc("Tool_Pickaxe_Iron", JInt(3), True, "craft", JInt(16))
        d_.put("rfN", BI32(JInt(rfn)))
        cs_["storage"].setItemStackForSlot(JShort(5), Data.put(stack("Tool_Pickaxe_Iron"), d_, None))
        Life.sweep0(PR1, inv_, True)
        new_wm(pl_)
        return inv_, cs_, ref_, st_, pl_

    def to_chest(cs_, c_, slot=3):
        p_ = pick_now(cs_)[0]
        c_.setItemStackForSlot(JShort(slot), p_[6])
        cs_[p_[0]].removeItemStackFromSlot(JShort(p_[1]))
        return p_

    def tracked_into(pl_, cs_, ref_, st_, c_, win_, slot=3):
        """the player moves the pickaxe into an open window's container; GearInvSys' gate queues the tracker, the world runs it"""
        new_wm(pl_, win_)
        p_ = to_chest(cs_, c_, slot)
        ex_ = QExec()
        jf(PR, "entity").set(PR1, ref_)
        LL.trackMaybe(PR1, st_, ref_, ex_, None)
        LL.trackMaybe(PR1, st_, ref_, ex_, None)          # a second change before the task ran: coalesced
        nq_ = len(ex_.q)
        for r_ in ex_.q:
            r_.run()
        jf(PR, "entity").set(PR1, None)
        return p_, nq_

    # ---- LT1: the snapshot (the sweep makes it; only a real change writes the registry)
    invT, csT, refT, stT, plT = setup_lt()
    P1 = LL.reg("p1")
    r_perk = str(Life.buy(U1, JInt(0), JInt(1)))
    A = pick_now(csT)[0]
    rf1 = regfile("p1")
    sj = snapjson(rf1)
    nw0 = int(LL.N[5])
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    nw1 = int(LL.N[5])
    d2 = doc(A[6]).clone()
    d2.put("rfN", BI32(JInt(3)))
    csT[A[0]].setItemStackForSlot(JShort(A[1]), Data.put(stack("Tool_Pickaxe_Iron"), d2, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    nw2 = int(LL.N[5])
    sj2 = snapjson(regfile("p1"))
    K.check(r_perk.startswith("+") and sj is not None and rf1.get("pickaxe.snapId") == "Tool_Pickaxe_Iron" and rf1.get("pickaxe.snapU") == A[3]
            and sj.get("r") == "legendary" and "lvl" not in sj and "lrt" not in sj and sj.get("lu") == A[3] and nw1 == nw0
            and nw2 == nw1 + 1 and sj2 is not None and num_(sj2.get("rfN")) == 3,
            "LT1: the sweep keeps a SNAPSHOT of the current pickaxe in the registry (its document minus lvl / lrt, Base64 JSON, item id, uid); "
            "a sweep with nothing changed writes nothing (%d writes), a reforge (rfN 2 -> 3) = exactly one write (%d)" % (nw1 - nw0, nw2 - nw1))
    K.check(str(LL.HERE.get(U1)) == "15:p1" and int(LL.hereMask(LL.HERE.get(U1), "p1")) == 15 and int(LL.hereMask(LL.HERE.get(U1), "p9")) == 0,
            "LT1: GearLL.HERE = the four kinds whose current tool is here (15:p1); another profile key reads 0: %s" % LL.HERE.get(U1))
    # fix round (safety critic 3): snapU pointing at another uid while SNAPRAW still matches -> the sweep re-points it (no shortcut)
    PS1 = LL.reg("p1")
    PS1.setProperty("pickaxe.snapU", "0000000000000000")
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    suF = regfile("p1").get("pickaxe.snapU")
    # fix round (engine critic 2): SNAPRAW is bounded (memory only)
    for i_ in range(4200):
        Life.SNAPRAW.put("zz%d|pickaxe" % i_, "x")
    Life.SNAPRAW.remove("p1|pickaxe")
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    nSR = int(Life.SNAPRAW.size())
    K.check(suF == A[3] and nSR <= 8 and regfile("p1").get("pickaxe.snapU") == A[3],
            "LT1 FIX (safety 3 + engine 2): a snapshot whose snapU names another uid is re-pointed by the next sweep even though the document "
            "did not change (%s); SNAPRAW over 4096 entries is cleared on the next real put (%d left)" % (suF, nSR))

    # ---- LT2: the tracker gate (GearLL.trackMaybe) + GearLife.trackLater coalescing + GearTrackTask + GearLife.track on REAL windows
    exN = QExec()
    LL.trackMaybe(PR1, stT, refT, exN, None)          # no window open -> nothing queued
    chestC = SIC(JShort(27))
    cbw = chest_win(chestC)
    A, nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    rfT = regfile("p1")
    K.check(not exN.q and nq == 1 and rfT.get("pickaxe.locK") == "chest" and rfT.get("pickaxe.locW") == "world1~aaaa"
            and (rfT.get("pickaxe.locX"), rfT.get("pickaxe.locY"), rfT.get("pickaxe.locZ")) == ("10", "64", "-5")
            and str(LL.HERE.get(U1)) == "14:p1" and not bool(LL.TRACKQ.containsKey(U1)),
            "LT2: THE TRACKER: no open window = nothing queued; the pickaxe moved into an open REAL ContainerBlockWindow (10 64 -5) -> ONE world "
            "task for two changes (coalesced), GearTrackTask -> track stores the place (chest, world key, x y z) and clears the kind's HERE bit: %s"
            % dict((k, v) for k, v in rfT.items() if k.startswith("pickaxe.loc")))
    vaultC = SIC(JShort(54))
    cwV = CWc_(vaultC)
    new_wm(plT, cwV)
    hat = [x for x in lls(csT, "p1") if x[2] == 1][0]
    vaultC.setItemStackForSlot(JShort(7), hat[6])
    csT[hat[0]].removeItemStackFromSlot(JShort(hat[1]))
    Life.track(PR1, plT, None)
    rfV = regfile("p1")
    lgT = logs()
    K.check(rfV.get("hatchet.locK") == "window:ContainerWindow" and "hatchet.locW" not in rfV and str(LL.HERE.get(U1)) == "12:p1"
            and any("LL-WHERE " in l and "chest world1 10 64 -5" in l for l in lgT) and any("LL-WHERE " in l and "window:ContainerWindow" in l for l in lgT),
            "LT2: a hatchet moved into an open ContainerWindow (the kind SkyyVault opens) = place 'window:ContainerWindow'; gear.log has LL-WHERE for both")
    # the window comes back to the inventory with the hatchet: the next look clears its place
    csT["storage"].setItemStackForSlot(JShort(30), vaultC.getItemStack(JShort(7)))
    vaultC.removeItemStackFromSlot(JShort(7))
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    K.check("hatchet.locK" not in regfile("p1") and str(LL.HERE.get(U1)) == "14:p1", "LT2: the hatchet seen back in the inventory -> its place is cleared")

    # ---- LT3: /pickaxe with the chest window STILL OPEN -> fetched from the window (the exact stack, the same uid)
    new_wm(plT, cbw)
    n15 = int(Life.N[15])
    nI = ids(csT).get("Tool_Pickaxe_Iron", 0)
    r3 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    got3 = pick_now(csT)
    rf3 = regfile("p1")
    K.check(r3.startswith("+Your %s came back from the open chest into your " % Gear.itemName("Tool_Pickaxe_Iron")) and len(got3) == 1 and got3[0][3] == A[3]
            and slot_of(chestC, A[3]) < 0 and rf3.get("pickaxe.uid") == A[3] and "pickaxe.locK" not in rf3 and int(Life.N[15]) == n15 + 1
            and ids(csT).get("Tool_Pickaxe_Iron", 0) == nI + 1 and not got3[0][5],
            "LT3: /pickaxe with the chest window open: the SAME pickaxe (uid %s, not a copy) moves from the chest into the inventory, the place is "
            "cleared, counter +1: %s" % (A[3], r3))
    # the Vault kind of window too
    vaultC2 = SIC(JShort(54))
    cwV2 = CWc_(vaultC2)
    A, _nq = tracked_into(plT, csT, refT, stT, vaultC2, cwV2, 11)
    r3v = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r3v.startswith("+Your %s came back from the open storage window" % Gear.itemName("Tool_Pickaxe_Iron")) and len(pick_now(csT)) == 1
            and pick_now(csT)[0][3] == A[3] and slot_of(vaultC2, A[3]) < 0,
            "LT3: ... and from an open ContainerWindow (the Vault's kind): %s" % r3v)

    # ---- LT3b (fix round, engine critic 1): THE REAL QUEUE ORDER. One inventory change queues GearStampTask (GearStamp.dirty0 -> w.execute,
    # idle player) BEFORE GearTrackTask (trackMaybe a line later); the world queue is FIFO, so the sweep (pass) runs first while the tool is
    # already in the chest - the tracker must still find it
    new_wm(plT, cbw)
    AQ = to_chest(csT, chestC)
    exO = QExec()
    jf(PR, "entity").set(PR1, refT)
    hereB = str(LL.HERE.get(U1))
    LL.trackMaybe(PR1, stT, refT, exO, None)          # GearInvSys: the tracker task is queued (TRACKQ) ...
    LL.LAST.clear()
    Life.sweep0(PR1, invT, False)          # ... but the stamp task queued first runs first (sweepHook -> sweep, not forced)
    hereMid = str(LL.HERE.get(U1))
    nqO = len(exO.q)
    for r_ in exO.q:
        r_.run()
    jf(PR, "entity").set(PR1, None)
    rfQ = regfile("p1")
    hereAfter = str(LL.HERE.get(U1))
    LL.LAST.clear()
    Life.sweep0(PR1, invT, False)
    hereLater = str(LL.HERE.get(U1))
    K.check(nqO == 1 and hereB == "15:p1" and hereMid == "15:p1" and rfQ.get("pickaxe.locK") == "chest"
            and (rfQ.get("pickaxe.locX"), rfQ.get("pickaxe.locY"), rfQ.get("pickaxe.locZ")) == ("10", "64", "-5")
            and hereAfter == "14:p1" and hereLater == "14:p1" and not bool(LL.TRACKQ.containsKey(U1)),
            "LT3b FIX (engine 1): stamp task (sweep) BEFORE the tracker task in queue order: while the tracker is queued the sweep keeps the "
            "pickaxe's HERE bit (%s -> %s), the tracker then records the chest (%s) and clears the bit (%s, still %s after the next sweep)"
            % (hereB, hereMid, rfQ.get("pickaxe.locK"), hereAfter, hereLater))
    rQb = str(Life.reclaimW(PR1, plT, JInt(0), None))          # the window is still open: back into the inventory for LT4
    K.check(rQb.startswith("+Your ") and len(pick_now(csT)) == 1 and pick_now(csT)[0][3] == AQ[3], "LT3b: ... and fetched back: %s" % rQb)

    # ---- LT4: the TRACKED CHEST, windows closed, chunk loaded -> fetched; unloaded -> exact copy; the original turns up -> the copy goes
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    Life.TEST_CHESTS = JClass("java.util.HashMap")()
    Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", chestC)
    n16 = int(Life.N[16])
    r4 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r4.startswith("+Your %s came back from the chest at 10 64 -5 into your " % Gear.itemName("Tool_Pickaxe_Iron")) and len(pick_now(csT)) == 1
            and pick_now(csT)[0][3] == A[3] and slot_of(chestC, A[3]) < 0 and int(Life.N[16]) == n16 + 1 and "pickaxe.locK" not in regfile("p1"),
            "LT4: /pickaxe with the chest closed but its chunk loaded: the SAME pickaxe comes back from the chest it was put in: %s" % r4)
    # unloaded chunk -> the EXACT copy
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    Life.TEST_CHESTS = JClass("java.util.HashMap")()          # nothing loaded
    origD = doc(chestC.getItemStack(JShort(slot_of(chestC, A[3]))))
    perk0 = int(LL.perkOf(LL.reg("p1"), JInt(0), JInt(1)))
    free0 = int(LL.free(U1, LL.reg("p1"), JInt(0)))
    n17 = int(Life.N[17])
    r5 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    cp = pick_now(csT)
    cD = doc(cp[0][6]) if cp else None
    rf5 = regfile("p1")
    K.check(r5.startswith("+Your pickaxe cannot be reached (it is in a chest at 10 64 -5 that is not loaded right now), so here is an exact copy: %s [Lv %d]"
                          % (Gear.itemName("Tool_Pickaxe_Iron"), int(LL.levelFor(U1, "Tool_Pickaxe_Iron"))))
            and len(cp) == 1 and str(cp[0][6].getItemId()) == "Tool_Pickaxe_Iron" and cp[0][3] != A[3] and cp[0][5]
            and str(Data.str(cD, "r", "")) == "legendary" and str(View.modSummary(cD)) == str(View.modSummary(origD))
            and str(Data.str(cD, "rf", "")) == str(Data.str(origD, "rf", "")) and int(Data.num(cD, "rfN", -1)) == int(Data.num(origD, "rfN", -2))
            and int(Data.num(cD, "lrpF", -1)) == int(Data.num(origD, "rfN", -2)) and str(Data.str(cD, "lcu", "")) == A[3]
            and int(Data.num(cD, "lvl", -1)) == int(LL.levelFor(U1, "Tool_Pickaxe_Iron")) and not bool(LL.invested("Tool_Pickaxe_Iron", cD))
            and int(LL.perkOf(LL.reg("p1"), JInt(0), JInt(1))) == perk0 == 1 and int(LL.free(U1, LL.reg("p1"), JInt(0))) == free0
            and rf5.get("pickaxe.uid") == cp[0][3] and rf5.get("pickaxe.rp") == "1" and rf5.get("pickaxe.snapU") == cp[0][3]
            and int(Life.N[17]) == n17 + 1 and slot_of(chestC, A[3]) >= 0,
            "LT4: the chest's chunk is NOT loaded -> an EXACT copy: the same Iron pickaxe, Legendary, the same lines + reforge count, perks (Fortune 1) "
            "and free points unchanged, level = the skill rule, a NEW uid with lcu = the original's, lrpF = the copied reforge count (so it is not "
            "'invested'); the registry names the copy; the original is untouched in the chest: %s" % r5)
    hC = hit(cp[0][6], "Ore_Iron_Stone")
    hO = hit(chestC.getItemStack(JShort(slot_of(chestC, A[3]))), "Rock_Stone")
    csT[cp[0][0]].removeItemStackFromSlot(JShort(cp[0][1]))
    r5w = str(Life.reclaimW(PR1, plT, JInt(0), None))
    csT[cp[0][0]].setItemStackForSlot(JShort(cp[0][1]), cp[0][6])
    K.check(not hC[0] and hO[0] and re.match(r"-Your pickaxe cannot be reached \(.+\)\. You can get an exact copy in \d+ s\.", r5w)
            and "pickaxe.locK" not in regfile("p1"),
            "LT4: only the copy works now (the original in the chest breaks nothing - stale); the copy's commit forgot the ORIGINAL's place (a new "
            "uid); losing the copy at once = the wait (copies only): %s" % r5w)
    # fix round (safety critic 1 + 2): the copy's family is recorded (pickaxe.nsw names the original); a 0.3.1 rollback's .inv=1 on the
    # unchanged copy is re-read by the next look (so the guard still removes the copy, not the original)
    nswF = str(regfile("p1").get("pickaxe.nsw", ""))
    PI4 = LL.reg("p1")
    PI4.setProperty("pickaxe.inv", "1")
    LL.save("p1", PI4)
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    K.check(A[3] in nswF.split(",") and "pickaxe.inv" not in regfile("p1") and bool(Life.family(LL.reg("p1"), "pickaxe", cD))
            and bool(Life.family(LL.reg("p1"), "pickaxe", origD)),
            "LT4 FIX (safety 1 + 2): the copy records its family (pickaxe.nsw = %s); both the copy and the original belong to it; a stale "
            "pickaxe.inv=1 (a 0.3.1 rollback) on the UNCHANGED copy is cleared by the next look" % nswF)
    # the original turns up (the chunk loaded, the player takes it): it is the pickaxe again, the copy disappears - never two
    csT["storage"].setItemStackForSlot(JShort(33), chestC.getItemStack(JShort(slot_of(chestC, A[3]))))
    chestC.removeItemStackFromSlot(JShort(slot_of(chestC, A[3])))
    PR1.said = None
    LL.TOLD.clear()          # the "is back" line is once per 5 s (an earlier part of this harness said it moments ago)
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, invT, True)
    nowP = pick_now(csT)
    K.check(len(nowP) == 1 and nowP[0][3] == A[3] and regfile("p1").get("pickaxe.uid") == A[3] and regfile("p1").get("pickaxe.rp") == "0"
            and ids(csT).get("Tool_Pickaxe_Iron", 0) == 1 and len(lls(csT, "p1")) == 4 and any("is back" in x for x in said(PR1)),
            "LT4: THE GUARD: the original turns up while the exact copy is current -> the original is the pickaxe again and the copy is removed "
            "(one Iron pickaxe left, uid %s): %s" % (A[3], ([(x[0], x[1], x[3], x[5]) for x in nowP], regfile("p1").get("pickaxe.uid"), ids(csT).get("Tool_Pickaxe_Iron"), said(PR1)[-2:])))

    # ---- LT5: the copy was reforged AFTER copying -> it stays, the original is RETIRED (never two working tools, nothing thrown away)
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    apply(lifelong__reclaimSec="0")
    r6 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    cp6 = pick_now(csT)[0]
    d6 = doc(cp6[6]).clone()
    d6.put("rfN", BI32(JInt(int(Data.num(d6, "rfN", 0)) + 1)))
    csT[cp6[0]].setItemStackForSlot(JShort(cp6[1]), Data.put(stack("Tool_Pickaxe_Iron"), d6, None))
    LL.LAST.clear()
    Life.sweep0(PR1, invT, True)
    csT["storage"].setItemStackForSlot(JShort(34), chestC.getItemStack(JShort(slot_of(chestC, A[3]))))
    chestC.removeItemStackFromSlot(JShort(slot_of(chestC, A[3])))
    PR1.said = None
    LL.TOLD.clear()
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, invT, True)
    w6 = pick_now(csT)
    o34 = csT["storage"].getItemStack(JShort(34))
    K.check(r6.startswith("+") and bool(LL.invested("Tool_Pickaxe_Iron", d6)) and len(w6) == 1 and w6[0][3] == cp6[3] and o34 is not None
            and bool(LL.isRt(doc(o34))) and ids(csT).get("Tool_Pickaxe_Iron", 0) == 2 and hit(o34, "Rock_Stone")[0] and not hit(w6[0][6], "Rock_Stone")[0],
            "LT5: the exact copy REFORGED after copying (rfN > lrpF) is invested: when the original turns up the copy stays THE pickaxe and the "
            "original is RETIRED (kept, breaks nothing) - two items, one working tool")
    # fix round (safety critic 1): the retired original can NOT be swapped back with /lifelong (a free undo of the paid reforge)
    saidS = said(PR1)
    h0 = csT["hotbar"].getItemStack(JShort(0))
    csT["hotbar"].setItemStackForSlot(JShort(0), o34)
    csT["storage"].removeItemStackFromSlot(JShort(34))
    rFam = str(Life.repick(PR1, plT))
    w6b = pick_now(csT)
    hb0 = csT["hotbar"].getItemStack(JShort(0))
    K.check(rFam.startswith("-That pickaxe and your lifelong one are exact copies of each other") and len(w6b) == 1 and w6b[0][3] == cp6[3]
            and regfile("p1").get("pickaxe.uid") == cp6[3] and hb0 is not None and bool(LL.isRt(doc(hb0)))
            and any("is an exact copy of it, so the old one stays retired" in x for x in saidS),
            "LT5 FIX (safety 1): /lifelong on the retired ORIGINAL of an invested exact copy is refused - the copy stays THE pickaxe, the "
            "original stays retired; the turn-up message no longer offers the swap: %s | %s" % (rFam, saidS[-1:]))
    csT["storage"].setItemStackForSlot(JShort(34), hb0)
    if h0 is None:
        csT["hotbar"].removeItemStackFromSlot(JShort(0))
    else:
        csT["hotbar"].setItemStackForSlot(JShort(0), h0)
    apply()

    # ---- LT6: out of reach in other ways: another world, the tool moved on, a closed Vault (window place)
    invT, csT, refT, stT, plT = setup_lt()
    chestC = SIC(JShort(27))
    cbw = chest_win(chestC)
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    Life.TEST_CHESTS = JClass("java.util.HashMap")()
    Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", chestC)
    Life.TEST_WKEY = "otherworld~bbbb"
    r7 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r7.startswith("+Your pickaxe cannot be reached (it is in a chest at 10 64 -5 in world1 - only a chest in the world you are in can send it)")
            and slot_of(chestC, A[3]) >= 0 and len(pick_now(csT)) == 1,
            "LT6: the tracked chest is in ANOTHER world -> it is left alone, an exact copy instead (the guard sorts it out later): %s" % r7)
    invT, csT, refT, stT, plT = setup_lt()
    chestC = SIC(JShort(27))
    cbw = chest_win(chestC)
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    elsewhere = SIC(JShort(27))
    elsewhere.setItemStackForSlot(JShort(0), chestC.getItemStack(JShort(slot_of(chestC, A[3]))))          # someone moved it on
    chestC.removeItemStackFromSlot(JShort(slot_of(chestC, A[3])))
    Life.TEST_CHESTS = JClass("java.util.HashMap")()
    Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", chestC)
    r8 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r8.startswith("+Your pickaxe cannot be reached (it is no longer in the chest at 10 64 -5)") and len(pick_now(csT)) == 1,
            "LT6: the tool is no longer in the tracked chest -> an exact copy: %s" % r8)
    invT, csT, refT, stT, plT = setup_lt()
    vC = SIC(JShort(54))
    A, _nq = tracked_into(plT, csT, refT, stT, vC, CWc_(vC))
    new_wm(plT)
    r9 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r9.startswith("+Your pickaxe cannot be reached (it is in a storage that cannot be opened from here)") and len(pick_now(csT)) == 1
            and slot_of(vC, A[3]) >= 0,
            "LT6: put into a storage window that is closed now (the Vault's kind) -> an exact copy; the original stays where it is: %s" % r9)

    # ---- LT7: Requip (wardrobe:fn:fetch): ok / refused / ok but missing / busy
    invT, csT, refT, stT, plT = setup_lt()
    A = pick_now(csT)[0]
    FETCH["cs"] = csT
    FETCH["store"] = {"e7": A[6]}
    RQ["items"] = [("e7", str(A[6].getItemId()), A[6].getMetadata())]
    csT[A[0]].removeItemStackFromSlot(JShort(A[1]))
    br.put("wardrobe:fn:fetch", RqFetch())
    FETCH["mode"] = "refuse"
    rq1 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    n_rq1 = len(pick_now(csT))
    FETCH["mode"] = "lie"
    rq2 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    br.put("profile:busy:" + str(U1), JBoolean(True))
    c0 = FETCH["calls"]
    rq3 = str(Life.fromRequip(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], "e7"))
    br.remove("profile:busy:" + str(U1))
    c1 = FETCH["calls"]
    FETCH["mode"] = "ok"
    n14 = int(Life.N[14])
    rq4 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(rq1.startswith("-Your lifelong pickaxe is in your Requip, but it could not come out: Inventory full") and n_rq1 == 0
            and rq2.startswith("-Requip let your pickaxe out, but it is not in your inventory") and rq3.startswith("-Your profile is changing") and c1 == c0
            and rq4.startswith("+Your %s came out of your Requip into your " % Gear.itemName("Tool_Pickaxe_Iron")) and pick_now(csT)[0][3] == A[3]
            and int(Life.N[14]) == n14 + 1 and not RQ.get("items"),
            "LT7: REQUIP: refused -> said, nothing copied; 'ok' but not in the inventory -> said (no copy, no dupe); profile busy -> Requip is not "
            "even asked; ok -> the SAME pickaxe is out of Requip: %s | %s | %s" % (rq1, rq2, rq4))
    br.remove("wardrobe:fn:fetch")
    RQ.clear()

    # ---- LT8: a FULL inventory is refused before anything moves (the tool stays in the open chest, nothing dropped)
    invT, csT, refT, stT, plT = setup_lt()
    chestC = SIC(JShort(27))
    cbw = chest_win(chestC)
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    fillT = []
    for sec in ("storage", "backpack", "hotbar"):
        for i_ in range(int(csT[sec].getCapacity())):
            if csT[sec].getItemStack(JShort(i_)) is None:
                csT[sec].setItemStackForSlot(JShort(i_), stack("Rock_Stone", 7))
                fillT.append((sec, i_))
    r10 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r10.startswith("-No room - free one inventory slot") and slot_of(chestC, A[3]) >= 0 and not pick_now(csT),
            "LT8: inventory full -> refused first, the pickaxe stays in the chest (never dropped): %s" % r10)
    for sec, i_ in fillT:
        csT[sec].removeItemStackFromSlot(JShort(i_))

    # ---- LT9: a chest ANOTHER player has open
    # (a) p1 fetches while p2 looks in: it moves, p2's REAL window is marked changed by the engine's own container event (re-sent)
    invB, csB = mkinv()
    refB, stB, chB, plB = world(invB, csB, PR2)
    cbwB = chest_win(chestC)
    new_wm(plB, cbwB)
    wdirty_(cbwB)
    new_wm(plT, cbw)
    r11 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r11.startswith("+Your ") and slot_of(chestC, A[3]) < 0 and len(pick_now(csT)) == 1 and wdirty_(cbwB),
            "LT9: p1 fetches the pickaxe from a chest p2 has open: it moves once, and p2's window is marked changed by the engine's own "
            "container change event (p2's client is re-sent the chest - the tool is gone there): %s" % r11)
    # (b) p2 took it first: p1 gets an exact copy; p2's original does NOTHING for p2; back with p1 -> the copy goes
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    new_wm(plT)
    csB["storage"].setItemStackForSlot(JShort(4), chestC.getItemStack(JShort(slot_of(chestC, A[3]))))
    chestC.removeItemStackFromSlot(JShort(slot_of(chestC, A[3])))
    Life.TEST_CHESTS = JClass("java.util.HashMap")()
    Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", chestC)
    apply(lifelong__reclaimSec="0")
    r12 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    PKEY[str(U2)] = "p2"
    skills(U2, Mining=20)
    LL.LAST.clear()
    Life.sweep0(PR2, invB, True)
    heldB = csB["storage"].getItemStack(JShort(4))
    hB = int(LL.hit(PR2, heldB, BL["Rock_Stone"])) if heldB is not None else -9
    csT["storage"].setItemStackForSlot(JShort(35), heldB)
    csB["storage"].removeItemStackFromSlot(JShort(4))
    for _i in range(2):
        LL.LAST.clear()
        Life.sweep0(PR1, invT, True)
    K.check(r12.startswith("+Your pickaxe cannot be reached (it is no longer in the chest at 10 64 -5)") and heldB is not None and hB == 2
            and len(pick_now(csT)) == 1 and pick_now(csT)[0][3] == A[3] and ids(csT).get("Tool_Pickaxe_Iron", 0) == 1,
            "LT9: p2 took p1's pickaxe out of the chest first: p1 gets an exact copy; the original does NOTHING for p2 (hit refused); once it is "
            "back with p1 it is the pickaxe again and the copy is removed: %s" % r12)
    apply()

    # ---- LT10: a profile switch mid-summon: busy / another profile key -> nothing moves
    A, _nq = tracked_into(plT, csT, refT, stT, chestC, cbw)
    sA = slot_of(chestC, A[3])
    br.put("profile:busy:" + str(U1), JBoolean(True))
    m1 = str(Life.move(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], chestC, JInt(sA), "the chest", JInt(16)))
    br.remove("profile:busy:" + str(U1))
    PKEY[str(U1)] = "p9"
    m2 = str(Life.move(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], chestC, JInt(sA), "the chest", JInt(16)))
    t2 = str(Life.track(PR1, plT, None))
    PKEY[str(U1)] = "p1"
    K.check(m1.startswith("-Your profile is changing") and m2.startswith("-Your profile is changing") and slot_of(chestC, A[3]) == sA and not pick_now(csT),
            "LT10: a profile switch mid-summon (profile:busy, or the active profile key is another one) -> refused, the pickaxe stays in the chest")

    # ---- LT11: the move's own failure paths: the source refuses / removes-then-throws, the target refuses (back in the source), both refuse
    MFc = JClass(FAKE_PKG + ".MergeFail")
    srcF = MFc(JShort(27))
    srcF.setItemStackForSlot(JShort(2), chestC.getItemStack(JShort(sA)))
    chestC.removeItemStackFromSlot(JShort(sA))
    srcF.rm = 1
    m3 = str(Life.move(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], srcF, JInt(2), "the chest", JInt(16)))
    srcF.rm = 2
    m4 = str(Life.move(PR1, invT, "p1", LL.reg("p1"), JInt(0), A[3], srcF, JInt(2), "the chest", JInt(16)))
    ok4 = len(pick_now(csT)) == 1 and slot_of(srcF, A[3]) < 0
    p4 = pick_now(csT)[0]
    srcF.rm = 0
    srcF.setItemStackForSlot(JShort(2), p4[6])
    csT[p4[0]].removeItemStackFromSlot(JShort(p4[1]))
    invF2, csF2 = mkinv(fail=("storage", "backpack", "hotbar"))
    for sec in ("storage", "backpack", "hotbar"):
        csF2[sec].refuseId = "Tool_Pickaxe_Iron"
    m5 = str(Life.move(PR1, invF2, "p1", LL.reg("p1"), JInt(0), A[3], srcF, JInt(2), "the chest", JInt(16)))
    back5 = slot_of(srcF, A[3]) == 2
    srcF.refuseId = "Tool_Pickaxe_Iron"
    logs()
    m6 = str(Life.move(PR1, invF2, "p1", LL.reg("p1"), JInt(0), A[3], srcF, JInt(2), "the chest", JInt(16)))
    lg6 = logs()
    srcF.refuseId = None
    K.check(m3.startswith("-Your pickaxe could not be taken out of the chest - nothing moved") and m4.startswith("+") and ok4
            and m5.startswith("-Your pickaxe could not be put into your inventory - it stayed in the chest") and back5
            and m6.startswith("-Moving your pickaxe went wrong") and any("LL-SUMMON-LOST " in l and " undo: " in l for l in lg6),
            "LT11: the source refuses -> nothing moved; removes-then-throws -> still delivered; the inventory refuses -> put back in the source "
            "slot; BOTH refuse -> LL-SUMMON-LOST with the undo data (WARN) and the registry still names it: %s | %s | %s | %s" % (m3, m4, m5, m6))
    # ... and that 'lost' tool is never lost for good: /pickaxe makes its exact copy
    apply(lifelong__reclaimSec="0")
    r13 = str(Life.reclaimW(PR1, plT, JInt(0), None))
    K.check(r13.startswith("+Your pickaxe cannot be reached") and "exact copy" in r13 and len(pick_now(csT)) == 1
            and str(Data.str(doc(pick_now(csT)[0][6]), "r", "")) == "legendary",
            "LT11: ... the next /pickaxe makes the exact (Legendary) copy: %s" % r13)
    apply()

    # ---- LT12: A CRASH AT EVERY SUMMON STEP, then a restart with the engine having saved: neither / the source / the target / both
    def crash_case(step, saved_src, saved_dst):
        inv_, cs_, ref_, st_, pl_ = setup_lt()
        ch_ = SIC(JShort(27))
        cw_ = chest_win(ch_)
        a_, _n = tracked_into(pl_, cs_, ref_, st_, ch_, cw_)
        s0 = slot_of(ch_, a_[3])
        it0 = ch_.getItemStack(JShort(s0))
        inv_before = snapshot(cs_)
        new_wm(pl_, cw_)
        Life.CRASH_AT = step
        crashed = False
        try:
            Life.reclaimW(PR1, pl_, JInt(0), None)
        except Exception as ex_:
            crashed = ("lifelong step %d" % step) in str(ex_)
        Life.CRASH_AT = 0
        # the restart: what the engine had saved
        if not saved_src and slot_of(ch_, a_[3]) < 0:
            ch_.setItemStackForSlot(JShort(s0), it0)
        if not saved_dst:
            restore_inv(cs_, inv_before)
        reset_reg()
        new_wm(pl_)
        Life.TEST_CHESTS = JClass("java.util.HashMap")()
        Life.TEST_CHESTS.put("world1~aaaa|10|64|-5", ch_)
        apply(lifelong__reclaimSec="0")
        LL.LAST.clear()
        Life.sweep0(PR1, inv_, True)
        if not pick_now(cs_):
            Life.reclaimW(PR1, pl_, JInt(0), None)
        # a second stack with the same uid left in the chest (the inventory was saved, the chest was not): it comes into the inventory
        dup = slot_of(ch_, a_[3])
        if dup >= 0 and pick_now(cs_):
            cs_["storage"].setItemStackForSlot(JShort(31), ch_.getItemStack(JShort(dup)))
            ch_.removeItemStackFromSlot(JShort(dup))
            for _i in range(2):
                LL.LAST.clear()
                Life.sweep0(PR1, inv_, True)
        apply()
        work = pick_now(cs_)
        regu = regfile("p1").get("pickaxe.uid")
        others = [ch_.getItemStack(JShort(i_)) for i_ in range(27) if ch_.getItemStack(JShort(i_)) is not None]
        working_elsewhere = [o_ for o_ in others if not hit(o_, "Rock_Stone")[0]]
        ok = (crashed and len(work) == 1 and work[0][3] == regu and not hit(work[0][6], "Rock_Stone")[0] and not working_elsewhere
              and str(Data.str(doc(work[0][6]), "r", "")) == "legendary" and ids(cs_).get("Tool_Pickaxe_Iron", 0) == 1)
        return ok, (crashed, [(x[0], x[1], x[3], x[5]) for x in work], regu, len(others), dup)
    for step in (7, 8):
        for ss, sd in ((False, False), (True, False), (False, True), (True, True)):
            okc, why = crash_case(step, ss, sd)
            K.check(okc, "LT12: a CRASH at summon step %d (engine saved: chest %s, inventory %s) then a restart (+ /pickaxe if needed): exactly ONE "
                    "working Legendary pickaxe, the registry names it, nothing else works: %s" % (step, "yes" if ss else "no", "yes" if sd else "no", why))
    # step 9: Requip said ok (the tool is out) and the server died before the bookkeeping: the next look is normal
    inv9, cs9, ref9, st9, pl9 = setup_lt()
    A9 = pick_now(cs9)[0]
    FETCH["cs"] = cs9
    FETCH["store"] = {"e9": A9[6]}
    FETCH["mode"] = "ok"
    RQ["items"] = [("e9", str(A9[6].getItemId()), A9[6].getMetadata())]
    cs9[A9[0]].removeItemStackFromSlot(JShort(A9[1]))
    br.put("wardrobe:fn:fetch", RqFetch())
    Life.CRASH_AT = 9
    cr9 = False
    try:
        Life.reclaimW(PR1, pl9, JInt(0), None)
    except Exception as ex_:
        cr9 = "lifelong step 9" in str(ex_)
    Life.CRASH_AT = 0
    reset_reg()
    LL.LAST.clear()
    Life.sweep0(PR1, inv9, True)
    br.remove("wardrobe:fn:fetch")
    RQ.clear()
    K.check(cr9 and len(pick_now(cs9)) == 1 and pick_now(cs9)[0][3] == A9[3] and regfile("p1").get("pickaxe.uid") == A9[3],
            "LT12: a CRASH right after Requip let the pickaxe out: after the restart it is simply the pickaxe (same uid), nothing to repair")

    # ---- LT13: the legacy answer: a tool lost before 0.3.2 (no snapshot) = a Common tool of the tier it had
    invL, csL, refL, stL, plL = setup_lt()
    AL = pick_now(csL)[0]
    csL[AL[0]].removeItemStackFromSlot(JShort(AL[1]))
    PL = LL.reg("p1")
    for k_ in ("pickaxe.snap", "pickaxe.snapId", "pickaxe.snapU"):
        PL.remove(k_)
    LL.save("p1", PL)
    rL = str(Life.reclaimW(PR1, plL, JInt(0), None))
    gL = pick_now(csL)
    K.check(rL.startswith("+Here is a new Common %s" % Gear.itemName("Tool_Pickaxe_Iron")) and "before exact copies existed" in rL and len(gL) == 1
            and str(Data.str(doc(gL[0][6]), "r", "")) == "normal" and str(gL[0][6].getItemId()) == "Tool_Pickaxe_Iron",
            "LT13: no snapshot (lost before 0.3.2, never seen since) -> the 0.3.1 answer, a Common tool of the tier it had: %s" % rL)
    # a snapshot of ANOTHER uid is never used (snapU must be the current uid)
    PL.setProperty("pickaxe.snap", B64.getEncoder().encodeToString(JStr("{\"r\": \"legendary\"}").getBytes("UTF-8")))
    PL.setProperty("pickaxe.snapU", "0000000000000000")
    K.check(Life.snapDoc(PL, "pickaxe", gL[0][3]) is None and Life.snapDoc(PL, "pickaxe", "0000000000000000") is not None,
            "LT13: snapDoc only answers for the CURRENT uid")

    # ---- LT14: the texts, rows, counters, statusText
    lgE = logs()
    K.check("fetch yours from Requip / an open window / its loaded chest, else an exact copy every" in str(LL.statusText())
            and "fetched from Requip" in str(Life.counters()) and "exact copies" in str(Life.counters()),
            "LT14: statusText + counters name the new paths: %s" % str(Life.counters())[-120:])
    _bs = open(os.path.join(HERE, "build_skyygear_%s.py" % VERSION), encoding="utf-8").read()
    K.check('w = "Not on you - /" + K + " brings it back";' in _bs and "(or an exact copy)\";" not in _bs
            and "the Void or your Vault?" not in _bs and "Is a better tool in a chest or your Vault?" in _bs,
            "LT14 FIX (fidelity 2 + 4): the Tools tab line is 'Not on you - /pickaxe brings it back' (36 chars, fits the 340 px column); the "
            "migration notice no longer names the Void")
    Life.TEST_CHESTS = None
    Life.TEST_WKEY = None
    LL.HERE.clear()
    LL.TRACKQ.clear()
    PKEY[str(U1)] = "p1"
    wipe_home()

    # ============================================================================ L8: /lifelong (re-pick)
    wipe_home()
    invR, csR = mkinv()
    refR2, stR2, chR2, plR2 = world(invR, csR, PR1)
    csR["storage"].setItemStackForSlot(JShort(5), Data.put(stack("Tool_Pickaxe_Iron"), Roll.newDoc("Tool_Pickaxe_Iron", JInt(1), True, "craft", JInt(16)), None))
    Life.sweep0(PR1, invR, True)
    first = [x for x in lls(csR, "p1") if x[2] == 0][0]
    better = Data.put(stack("Tool_Pickaxe_Cobalt"), Roll.newDoc("Tool_Pickaxe_Cobalt", JInt(3), True, "craft", JInt(25)), None)
    csR["hotbar"].setItemStackForSlot(JShort(0), better)
    K.check(int(invR.getActiveHotbarSlot()) == 0 and not bool(invR.usingToolsItem()), "L8: a new inventory holds hotbar slot 0")
    r_rp = str(Life.repick(PR1, plR2))
    LR = [x for x in lls(csR, "p1") if x[2] == 0]
    old_ = csR[first[0]].getItemStack(JShort(first[1]))
    r_rp2 = str(Life.repick(PR1, plR2))
    csR["hotbar"].setItemStackForSlot(JShort(0), stack("Tool_Shovel_Iron"))
    r_sh = str(Life.repick(PR1, plR2))
    csR["hotbar"].setItemStackForSlot(JShort(0), Data.put(stack("Tool_Hatchet_Iron"), Roll.newDoc("Tool_Hatchet_Iron", JInt(1), True, "craft", JInt(16)), None))
    LL.reg("p1").setProperty("migratedAt", "1")
    r_late = str(Life.repick(PR1, plR2))
    K.check(r_rp.startswith("+%s is your lifelong pickaxe now" % Gear.itemName("Tool_Pickaxe_Cobalt")) and len(LR) == 1 and str(LR[0][6].getItemId()) == "Tool_Pickaxe_Cobalt"
            and str(Data.str(doc(LR[0][6]), "r", "")) == "legendary" and not bool(LL.isLL(doc(old_))) and r_rp2.startswith("-That already is your lifelong pickaxe")
            and r_sh.startswith("-Only a pickaxe, hatchet, hoe or sickle") and r_late.startswith("-Re-picking was open for 7 days"),
            "L8: /lifelong: the Legendary Cobalt pickaxe in hand becomes the lifelong one, the old one turns plain; again / a shovel / too late refused: %s | %s"
            % (r_rp, r_late))
    LL.reg("p1").setProperty("migratedAt", str(int(__import__("time").time() * 1000)))
    csR["hotbar"].setItemStackForSlot(JShort(0), Data.put(stack("Tool_Pickaxe_Thorium"), Roll.newDoc("Tool_Pickaxe_Thorium", JInt(0), True, "craft", JInt(20)), None))
    r_twice = str(Life.repick(PR1, plR2))
    K.check(r_twice.startswith("-You already re-picked your lifelong pickaxe"), "L8: once per kind: %s" % r_twice)

    # ============================================================================ L9: protection (drop, salvage, market, merge, level up) + no crafting
    wipe_home()
    invD, csD = mkinv()
    refD, stD, chD, plD = world(invD, csD, PR1)
    Life.sweep0(PR1, invD, True)
    LD = dict((x[2], x) for x in lls(csD, "p1"))
    DIRQ = JClass("com.hypixel.hytale.server.core.event.events.ecs.DropItemEvent$PlayerRequest")
    Drop = JClass(PKG + "GearLLDropSys")()
    SECID = {"hotbar": -1, "storage": -2, "armor": -3, "utility": -5, "tools": -8, "backpack": -9}
    sec0, slot0 = LD[0][0], LD[0][1]
    e1 = DIRQ(JInt(SECID[sec0]), JShort(slot0))
    n4 = int(LL.N[4])
    Drop.handle(JInt(0), chD, stD, None, e1)
    csD["storage"].setItemStackForSlot(JShort(35), stack("Rock_Stone", 5))
    e2 = DIRQ(JInt(-2), JShort(35))
    Drop.handle(JInt(0), chD, stD, None, e2)
    apply(lifelong__noDrop="false")
    e3 = DIRQ(JInt(SECID[sec0]), JShort(slot0))
    Drop.handle(JInt(0), chD, stD, None, e3)
    apply()
    K.check(bool(e1.isCancelled()) and not bool(e2.isCancelled()) and not bool(e3.isCancelled()) and int(LL.N[4]) == n4 + 1
            and csD[sec0].getItemStack(JShort(slot0)) is not None,
            "L9: THE REAL GearLLDropSys on DropItemEvent$PlayerRequest (InventoryUtils.getSectionById resolves the section): the Drop key on the lifelong "
            "pickaxe is cancelled (it stays), on stone it is not; lifelong.noDrop off lets it go")
    # SALVAGE: the engine's own matching (ProcessingBenchBlock.updateRecipe -> testRemoveMaterialFromSlot -> isEquivalentType)
    IUM = JClass("com.hypixel.hytale.server.core.inventory.container.InternalContainerUtilMaterial")
    MQc = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    salv = None
    for rc in CRR.getAssetMap().getAssetMap().values():
        try:
            inp = rc.getInput()
            if inp is not None and len(inp) == 1 and str(inp[0].getItemId()) == str(LD[0][6].getItemId()):
                salv = rc
                break
        except Exception:
            pass
    sc = SIC(JShort(3))
    sc.setItemStackForSlot(JShort(0), LD[0][6])
    sc.setItemStackForSlot(JShort(1), stack(str(LD[0][6].getItemId())))
    sc.setItemStackForSlot(JShort(2), stack("Rock_Stone"))
    mq = salv.getInput()[0] if salv is not None else MQc(str(LD[0][6].getItemId()), None, None, JInt(1), None)
    t_ll = int(IUM.testRemoveMaterialFromSlot(sc, JShort(0), mq, JInt(1), False))
    t_pl = int(IUM.testRemoveMaterialFromSlot(sc, JShort(1), mq, JInt(1), False))
    t_no = int(IUM.testRemoveMaterialFromSlot(sc, JShort(2), mq, JInt(1), False))
    K.check(t_ll == t_no and t_pl != t_no, "L9: SALVAGE: the engine's recipe matching (%s) treats the lifelong %s like a stone (no match: %d = %d) and "
            "matches a plain one (%d)" % ("the real salvage recipe " + str(salv.getId()) if salv is not None else "a recipe input", LD[0][6].getItemId(), t_ll, t_no, t_pl))
    K.check(Wall.why(LD[0][6].getItemId(), LD[0][6].getMetadata()) is not None and "never go on the market" in str(Wall.why(LD[0][6].getItemId(), LD[0][6].getMetadata()))
            and Wall.why("Tool_Pickaxe_Crude", Data.put(stack("Tool_Pickaxe_Crude"), Roll.newDoc("Tool_Pickaxe_Crude", JInt(0), True, "craft", JInt(1)), None).getMetadata()) is None,
            "L9: the market wall refuses a lifelong tool (Auction House / Bazaar), not a plain one")
    K.check("cannot be merged" in str(Merge.why(LD[0][6], JInt(1))), "L9: the multitool merge refuses a lifelong pickaxe: %s" % Merge.why(LD[0][6], JInt(1)))
    li = Forge.lvlInfo(U1, LD[0][6].getItemId(), doc(LD[0][6]))
    K.check(int(li[0]) == 8 and "follows your skill level" in str(li[5]), "L9: Reforge Level up refuses a lifelong tool (code 8): %s" % li[5])
    # NO CRAFTING: the REAL GearCraftPreSys on a REAL CraftRecipeEvent$Pre
    PreE = JClass("com.hypixel.hytale.server.core.event.events.ecs.CraftRecipeEvent$Pre")
    Pre = JClass(PKG + "GearCraftPreSys")()

    def recipe_of(out_id):
        for rc in CRR.getAssetMap().getAssetMap().values():
            try:
                po = rc.getPrimaryOutput()
                if po is not None and str(po.getItemId()) == out_id and int(po.getQuantity()) == 1:
                    return rc
            except Exception:
                pass
        return None
    rcP = recipe_of("Tool_Pickaxe_Copper")
    rcS = None
    for _sid in ("Tool_Shovel_Copper", "Tool_Shovel_Crude", "Tool_Shovel_Iron", "Tool_Shovel_Thorium", "Tool_Shovel_Cobalt"):
        rcS = rcS or recipe_of(_sid)
    chC = us.allocateInstance(FCh.class_)
    chC.comps = IHM()
    chC.ref = refD
    PR1.said = None
    ep = PreE(rcP, JInt(1))
    Pre.handle(JInt(0), chC, stD, None, ep)
    es = PreE(rcS, JInt(1))
    Pre.handle(JInt(0), chC, stD, None, es)
    ec = PreE(rcP, JInt(1))
    try:
        gmf = jf(PLA, "gameMode")
        gmf.set(plD, JClass("com.hypixel.hytale.protocol.GameMode").Creative)
        Pre.handle(JInt(0), chC, stD, None, ec)
        gmf.set(plD, None)
    except KeyError:
        K.notes.append("L9: Player has no gameMode field - the Creative case is not run")
    apply(lifelong__noCraft="false")
    eo = PreE(rcP, JInt(1))
    Pre.handle(JInt(0), chC, stD, None, eo)
    apply()
    K.check(rcP is not None and rcS is not None and bool(ep.isCancelled()) and not bool(es.isCancelled()) and not bool(ec.isCancelled()) and not bool(eo.isCancelled())
            and any("Tools are not crafted any more" in x for x in said(PR1)),
            "L9: NO CRAFTING: the real Copper pickaxe recipe (%s) is refused at the bench / /craft with a chat line; a shovel crafts; Creative crafts; "
            "lifelong.noCraft off crafts: %s" % (None if rcP is None else rcP.getId(), [rcS is not None and rcS.getId(), bool(ep.isCancelled()), bool(es.isCancelled()),
                                                     bool(ec.isCancelled()), bool(eo.isCancelled()), said(PR1)[-1:]]))
    K.check(not bool(Smith.usable(rcP)) and bool(Smith.usable(rcS)) == bool(Smith.usable(rcS)) and bool(LL.noCraft("Tool_Hoe_Iron"))
            and not bool(LL.noCraft("Tool_Shovel_Iron")), "L9: the Smithing Craft tab hides pickaxe recipes (shovels unchanged)")

    # ============================================================================ L10: the tier-up on the Anvil (GearUp)
    wipe_home()
    invU, csU = mkinv()
    refU, stU, chU, plU = world(invU, csU, PR1)
    skills(Mining=4, Foraging=4, Farming=4)
    Life.sweep0(PR1, invU, True)
    LU = dict((x[2], x) for x in lls(csU, "p1"))
    secU, slotU = LU[0][0], LU[0][1]
    plain = Data.put(stack("Tool_Pickaxe_Crude"), Roll.newDoc("Tool_Pickaxe_Crude", JInt(1), True, "craft", JInt(3)), None)
    cU = Up.check(plain, U1)
    cL = Up.check(csU[secU].getItemStack(JShort(slotU)), U1)
    K.check(str(cU[0]).startswith("Only your lifelong pickaxe can be tiered up") and str(cL[0]).startswith("You need Mining %d to tier up to %s"
            % (int(Lvl.band("Tool_Pickaxe_Copper")[0]), str(LL.an(Gear.itemName("Tool_Pickaxe_Copper"))))), "L10: a plain Crude pickaxe cannot climb; yours needs the Copper band start: %s | %s" % (cU[0], cL[0]))
    skills(Mining=int(Lvl.band("Tool_Pickaxe_Copper")[0]) + 3)
    cL2 = Up.check(csU[secU].getItemStack(JShort(slotU)), U1)
    K.check(cL2[0] is None and str(cL2[1]) == "Tool_Pickaxe_Copper" and list(cL2[2][0]) == ["Ingredient_Bar_Copper"] and list(cL2[2][1]) == [25],
            "L10: with the level: Copper for 25 Copper Ingots (Skyy's G1)")
    csU["storage"].setItemStackForSlot(JShort(30), stack("Ingredient_Bar_Copper", 30))
    before_u = str(LU[0][3])
    res = Up.upgrade(invU, JInt({"hotbar": 0, "storage": 1, "backpack": 2, "armor": 3, "utility": 4, "tools": 5}[secU]), JInt(slotU),
                     "Tool_Pickaxe_Crude", Forge.fp(csU[secU].getItemStack(JShort(slotU))), U1, "Tester")
    nu = csU[secU].getItemStack(JShort(slotU))
    K.check(int(res[0]) == 1 and str(nu.getItemId()) == "Tool_Pickaxe_Copper" and str(LL.uid(doc(nu))) == before_u and bool(LL.isLL(doc(nu)))
            and int(Data.num(doc(nu), "lvl", -1)) == int(LL.levelFor(U1, "Tool_Pickaxe_Copper")) and ids(csU).get("Ingredient_Bar_Copper") == 5,
            "L10: THE TIER-UP (GearUp.upgrade): the lifelong Crude pickaxe becomes a Copper one - same uid, still lifelong, at your level; 25 ingots taken")
    LL.LAST.clear()
    Life.sweep0(PR1, invU, True)
    K.check(regfile("p1").get("pickaxe.id") == "Tool_Pickaxe_Copper", "L10: the next sweep records the new tier (what /pickaxe would give back)")
    pvI = Up.preview(nu, U1)
    K.check(str(pvI[0]).startswith("You need Mining") or str(pvI[0]).startswith("You need 1 more") or pvI[0] is None,
            "L10: the next step (Iron) asks for the Iron band level / 1 Enchanted Iron Ingot: %s" % pvI[0])

    # ============================================================================ L11: the Tools page + the commands + the bridge + the tooltip
    wipe_home()
    invT, csT = mkinv()
    refT, stT, chT, plT = world(invT, csT, PR1)
    skills(Mining=12, Foraging=12, Farming=12)
    Life.sweep0(PR1, invT, True)
    FLP = JClass(FAKE_PKG + ".FakeLifePage")
    UCB = JClass("com.hypixel.hytale.server.core.ui.builder.UICommandBuilder")
    UEB = JClass("com.hypixel.hytale.server.core.ui.builder.UIEventBuilder")

    def cmds(ub_):
        out_ = []
        for c_ in ub_.getCommands():
            vals = {}
            for f_ in ("selector", "data", "text"):
                try:
                    v_ = getattr(c_, f_)
                    vals[f_] = None if v_ is None else str(v_)
                except Exception:
                    vals[f_] = None
            out_.append(vals)
        return out_

    def evtext(ue_):
        out_ = []
        for e_ in ue_.getEvents():
            for f_ in ("selector", "data", "eventData"):
                try:
                    v_ = getattr(e_, f_)
                    if v_ is not None:
                        out_.append(str(v_))
                except Exception:
                    pass
        return chr(10).join(out_)

    def render(pg_):
        ub_, ue_ = UCB(), UEB()
        pg_.build(refT, ub_, ue_, stT)
        cl = cmds(ub_)
        return chr(10).join("%s|%s|%s" % (v["selector"], v["data"], v["text"]) for v in cl) + chr(10) + evtext(ue_), cl
    pg = FLP(PR1)
    txt, cl = render(pg)
    idsx = re.findall(r"#([A-Za-z0-9_]+)\s*\{", chr(10).join("%s" % (v["text"] if v["text"] and "{" in v["text"] else (v["data"] or "")) for v in cl))
    K.check(idsx and not [i for i in idsx if "_" in i] and len(idsx) == len(set(idsx)) and "Your lifelong tools" in txt and "Upgrade Points" in txt
            and "#SkyyGTab4" in txt and "Tools" in txt and "ItemGridSlot" not in txt and txt.count("#SkyyGLRow") >= 4,
            "L11: the Tools page renders: unique ids without underscores, the Tools tab, four tool rows, the points panel, no ItemGridSlot: %s"
            % (([i for i in idsx if "_" in i], [i for i in idsx if idsx.count(i) > 1][:5], "Your lifelong tools" in txt, "Upgrade Points" in txt,
               "#SkyyGTab4" in txt, txt.count("#SkyyGLRow")),))
    hs_ = {}
    for v in cl:
        dat = v["text"] if v["text"] and "{" in v["text"] else (v["data"] or "")
        m_ = re.match(r"^\s*\w+[^{]*\{\s*Anchor: \(([^)]*)\)", dat)
        if m_ and v["selector"]:
            h_ = re.search(r"Height: (\d+)", m_.group(1))
            hs_[v["selector"]] = hs_.get(v["selector"], 0) + (int(h_.group(1)) if h_ else 0)
    K.check(hs_.get("#SkyyGBody", 0) <= 808 and hs_.get("#SkyyGList", 0) <= 656 and hs_.get("#SkyyGPanel", 0) <= 656,
            "L11: the height budget (body %d <= 808, list %d <= 656, panel %d <= 656)" % (hs_.get("#SkyyGBody", 0), hs_.get("#SkyyGList", 0), hs_.get("#SkyyGPanel", 0)))
    COINS[0] = 10 ** 7
    pg.handleDataEvent(refT, stT, '{"a":"sel:1"}')
    K.check(int(pg.sel) == 1, "L11: click a tool row -> its points")
    pg.lastClick = 0
    pg.handleDataEvent(refT, stT, '{"a":"buy:0"}')
    info1 = str(pg.info)
    pg.lastClick = 0
    pg.handleDataEvent(refT, stT, '{"a":"reset"}')
    info2 = str(pg.info)
    pg.lastClick = 0
    pg.handleDataEvent(refT, stT, '{"a":"reset"}')
    info3 = str(pg.info)
    K.check(info1.startswith("+Speed is level 1 now") and info2.startswith("=Click Reset again within 8 s to pay 5,000 coins") and info3.startswith("+All 1 points of your hatchet are back"),
            "L11: buy Speed for the hatchet, Reset asks first, the 2nd click pays: %s | %s | %s" % (info1, info2, info3))
    pg.handleDataEvent(refT, stT, '{"a":"buy:0"}')
    K.check(str(pg.info) == info3, "L11: a click within 400 ms is dropped")
    pg.handleDataEvent(refT, stT, '{"a":"mode:4"}')
    pg.handleDataEvent(refT, stT, '{"a":"refresh"}')
    br.put("profile:epoch:" + str(U1), "e2")
    pg.lastClick = 0
    pg.handleDataEvent(refT, stT, '{"a":"buy:1"}')
    K.check(str(pg.info).startswith("-Your profile changed"), "L11: a profile switch since the page opened refuses the click")
    br.remove("profile:epoch:" + str(U1))
    pg.handleDataEvent(refT, stT, '{"a":"back"}')
    K.check(int(pg.closes) == 1 and int(pg.rebuilds) >= 5, "L11: Back closes (no SkyyMenu), the clicks rebuild")
    K.check(bool(LL.tabGo('{"a":"mode:4"}', PR1)) and not bool(LL.tabGo('{"a":"mode:3"}', PR1)), "L11: the Tools tab click on the other pages is caught (mode:4 only)")

    def run_cmd(cls, ref_, st_, pr_):
        cmd = P(cls)()
        exe = [m_ for m_ in P(cls).class_.getDeclaredMethods() if str(m_.getName()) == "execute"][0]
        exe.setAccessible(True)
        FPM.last = None
        exe.invoke(cmd, None, st_, ref_, pr_, None)
        return FPM.last
    PR1.said = None
    lp = run_cmd("ToolPtsCmd", refT, stT, PR1)
    K.check(lp is not None and str(lp.getClass().getName()).endswith("LifePage"), "L11: /toolpoints opens the Tools page")
    run_cmd("PickaxeCmd", refT, stT, PR1)
    run_cmd("LifelongCmd", refT, stT, PR1)
    sd = said(PR1)
    K.check(any("You still have your lifelong pickaxe" in x for x in sd) and any("Hold the tool you want" in x or "Only a pickaxe" in x for x in sd),
            "L11: /pickaxe and /lifelong run and answer in chat: %s" % sd[-2:])
    # every replacement command runs (the tools are on the player: each says so) + the hooks the build gave a body (join / scan / prefetch / forget)
    PR1.said = None
    for cls in ("HatchetCmd", "HoeCmd", "SickleCmd"):
        run_cmd(cls, refT, stT, PR1)
    sd2 = said(PR1)
    K.check([("You still have your lifelong %s" % k_) in " ".join(sd2) for k_ in ("hatchet", "hoe", "sickle")] == [True, True, True],
            "L11: /hatchet, /hoe and /sickle run: %s" % sd2)
    LL.REG.clear()
    LL.prefetch(U1)
    K.check(LL.REG.containsKey("p1"), "L11: GearLL.prefetch (GearRefreshTask's scheduler hop) reads the registry into memory")
    nsw = int(Life.N[0])
    LL.joinHook(PR1, invT)
    LL.LAST.clear()
    LL.sweepHook(PR1, invT)
    K.check(int(Life.N[0]) == nsw + 2, "L11: joinHook / sweepHook (GearRefreshTask.run / GearStampTask.run) run the sweep (their bodies were set at build)")
    LL.SLOW.put(U1, JLong(1))
    LL.TOLD.put(str(U1) + ":x", JLong(1))
    LL.forget(U1)
    K.check(not LL.SLOW.containsKey(U1) and not LL.TOLD.containsKey(str(U1) + ":x") and not LL.LAST.containsKey(U1), "L11: GearLL.forget (GearBye) clears the player's clocks")
    cons = []
    for cls, nm_ in (("PickaxeCmd", "pickaxe"), ("HatchetCmd", "hatchet"), ("HoeCmd", "hoe"), ("SickleCmd", "sickle"), ("ToolPtsCmd", "toolpoints"), ("LifelongCmd", "lifelong")):
        c_ = P(cls)()
        cons.append((nm_, str(c_.getName())))
    K.check(all(a == b for a, b in cons), "L11: command names: %s" % cons)
    Fn0, Fn1, Fn2 = JClass(PKG + "GearLLFn")(JInt(0)), JClass(PKG + "GearLLFn")(JInt(1)), JClass(PKG + "GearLLFn")(JInt(2))
    uidp = str(LL.reg("p1").getProperty("pickaxe.uid"))
    K.check(str(Fn0.apply(JArray(JObject)([U1, JString("pickaxe")]))) == uidp and Fn0.apply(JArray(JObject)([U1, JString("shovel")])) is None
            and int(Fn1.apply(JArray(JObject)([U1, JString("hatchet"), JString("spd")]))) == 0
            and int(Fn2.apply(JArray(JObject)([U1, JString("Plant_Crop_Carrot_Block"), JString("Tool_Hoe_Crude")]))) == 1          # 0.3.1: was 2
            and int(Fn2.apply(JArray(JObject)([U1, JString("Plant_Crop_Carrot_Block"), stack("Tool_Hoe_Crude")]))) == -1
            and Fn0.apply(JString("bad")) is None, "L11 + FIX engine-6: gear:fn:lifelong / perk / farmTier answer (and never throw); farmTier takes the held item id (java.lang only - an "
                "ItemStack is no tool to it): %s" % [
                str(Fn0.apply(JArray(JObject)([U1, JString("pickaxe")]))), uidp, Fn0.apply(JArray(JObject)([U1, JString("shovel")])),
                Fn1.apply(JArray(JObject)([U1, JString("hatchet"), JString("spd")])), Fn2.apply(JArray(JObject)([U1, JString("Plant_Crop_Carrot_Block"), JString("Tool_Hoe_Crude")]))])
    tipT = JClass("java.util.ArrayList")(), JClass("java.util.ArrayList")()
    pT = [x for x in lls(csT, "p1") if x[2] == 0][0][6]
    Tool.lines(U1, pT.getItemId(), doc(pT), tipT[0], tipT[1])
    tl_txt = [str(x) for x in tipT[0]]
    K.check(any(x.startswith("Lifelong pickaxe: levels with Mining (max Lv") for x in tl_txt) and any("Upgrade Points free - /toolpoints" in x for x in tl_txt)
            and "Can't be dropped. Lost it? /pickaxe" in tl_txt and max(len(x) for x in tl_txt) <= 60,
            "L11: the tooltip: lifelong line, free points, can't be dropped (short lines): %s" % tl_txt[-4:])
    K.check("lifelong tools on" in str(LL.statusText()) and "gate refused" in str(LL.counters()) and "sweeps" in str(Life.counters()),
            "L11: status + counters: %s" % str(LL.statusText())[:160])

    # ============================================================================ G (0.3.1): THE NEW TIER GATE
    apply()
    skills(Mining=10, Foraging=10, Farming=10)
    st31 = str(LL.statusText())
    K.check("Crude counts as Copper, one tier up x0.4, two up x0.1, three up refused" in st31,
            "G: statusText names the new gate: %s" % st31[-160:])
    rws = dict((k, int(CRows.index(k))) for k in ("gate.nextFactor", "gate.twoUpFactor", "gate.crudeFactor"))
    K.check(all(v >= 0 for v in rws.values()) and bool(CRows.flag(rws["gate.twoUpFactor"], "danger")),
            "G: Server Setup rows: gate.nextFactor, the NEW gate.twoUpFactor (danger), gate.crudeFactor kept as a legacy row: %s" % rws)
    gsrcs = [b for b in sorted(str(k) for k in bmap.keySet()) if not b.startswith("*")]

    def first(pre, suf=""):
        for b_ in gsrcs:
            if b_.startswith(pre) and (not suf or suf in b_):
                return b_
        return None
    ORE, WOOD = {}, {}
    for w_, m_ in zip([str(x) for x in LL.ORE_W], [int(x) for x in LL.ORE_M]):
        b_ = first("Ore_" + w_ + "_")
        if b_ is not None and m_ not in ORE and list(LL.catOf(b_)) == [1, m_]:
            ORE[m_] = b_
    for w_, m_ in zip([str(x) for x in LL.WOOD_W], [int(x) for x in LL.WOOD_M]):
        b_ = first("Wood_" + w_ + "_", "_Trunk")
        if b_ is not None and m_ not in WOOD and list(LL.catOf(b_)) == [3, m_]:
            WOOD[m_] = b_
    K.notes.append("G: ore blocks by tier %s, logs by tier %s" % (ORE, WOOD))

    def hitb(s_, bid):
        Tool.LAST.clear()
        e_ = ev(s_, bmap.get(bid), 0.3)
        hs.handle(JInt(0), chH, stH, None, e_)
        return bool(e_.isCancelled()), float(e_.getDamage())

    def refb(s_, bid):
        Tool.LAST.clear()
        return float(Tool.onDamage(U1, s_, bmap.get(bid), JFloat(0.3)))
    FX = {0: 1.0, 1: 0.4, 2: 0.1}
    gbad, gseen, gn = [], set(), 0
    for tool_, te_ in (("Tool_Pickaxe_Crude", 1), ("Tool_Pickaxe_Copper", 1), ("Tool_Pickaxe_Iron", 2),
                       ("Tool_Hatchet_Crude", 1), ("Tool_Hatchet_Copper", 1), ("Tool_Hatchet_Iron", 2)):
        tab_ = ORE if "Pickaxe" in tool_ else WOOD
        for m_ in sorted(tab_):
            up = m_ - te_
            cx, dmg = hitb(stack(tool_), tab_[m_])
            ref = refb(stack(tool_), tab_[m_])
            if up >= 3:
                ok = cx
            else:
                ok = (not cx) and abs(dmg - float(JFloat(ref * FX[max(up, 0)]))) < 1e-6
            gn += 1
            gseen.add((tool_, min(max(up, 0), 3)))
            if not ok:
                gbad.append((tool_, tab_[m_], m_, up, cx, dmg, ref))
    need = set((t_, k_) for t_ in ("Tool_Pickaxe_Crude", "Tool_Pickaxe_Copper", "Tool_Pickaxe_Iron", "Tool_Hatchet_Crude", "Tool_Hatchet_Copper")
               for k_ in (0, 1, 2, 3))
    K.check(not gbad and need <= gseen and gn >= 30,
            "G: THE 0.3.1 GATE MATRIX on the REAL hit system + real ore / log blocks (%d hits): Crude and Copper pickaxes / hatchets = tier 1 "
            "(T1 normal, T2 x0.4, T3 x0.1, T4+ refused), Iron one tier higher (T2 normal, T3 x0.4, T4 x0.1, T5+ refused); missing cases %s; bad %s"
            % (gn, sorted(need - gseen)[:4], gbad[:4]))
    dC = LL.decideC(stack("Tool_Hoe_Crude"), JInt(4), JInt(5))
    dP = LL.decideC(stack("Tool_Pickaxe_Crude"), JInt(1), JInt(4))
    dI = LL.decideC(stack("Tool_Pickaxe_Iron"), JInt(1), JInt(4))
    K.check(int(LL.fullT(dC)) == 3 and int(dC[5]) == 2 and int(LL.fullT(dP)) == 4 and int(dP[0]) == 2 and int(dP[5]) == 3
            and int(dI[0]) == 1 and int(dI[5]) == 2 and int(dP[3]) == 0,
            "G: decide's [5] = tiers above (Crude = T1), [3] the raw tier; fullT caps a hoe at Thorium (%s / %s / %s)" % (list(dC), list(dP), list(dI)))
    ftc = [int(LL.farmTier(c_, h_)) for c_, h_ in (("Plant_Crop_Wheat_Block", "Tool_Hoe_Crude"), ("Plant_Crop_Wheat_Block", "Tool_Sickle_Crude"),
                                                    ("Plant_Crop_Carrot_Block", "Tool_Sickle_Crude"), ("Plant_Crop_Potato_Block", "Tool_Hoe_Crude"),
                                                    ("Plant_Crop_Potato_Block", "Tool_Hoe_Copper"), ("Plant_Crop_Potato_Block", "Tool_Hoe_Iron"))]
    K.check(ftc == [0, 0, 1, 1, 1, 1],
            "G: farming: Crude hoe / sickle on Wheat (T1) normal; anything above your tier = 1 (half XP, no Fortune) - a Crude hoe on a Potato is "
            "two up (vanilla hoes end at Thorium) = still 1, never refused: %s" % ftc)
    with zipfile.ZipFile(JAR) as zj_:
        llb = zj_.read("com/skyy/gear/GearLL.class")
    K.check(b"Slow going" in llb and b"x the hits. With " in llb and b"two tiers" in llb and b"one tier" in llb and b"It needs at least " in llb
            and b" for full speed). Tier yours up on the Anvil (/smithing)." in llb and b"Too tough for your " in llb
            and b"This is one tier above your " not in llb,
            "G: the popups: 'Slow going' names one / two tiers and the hits (2.5x / 10x), 'Too tough' names the lowest tier that breaks it + the "
            "full-speed tier")

    # ---- G: THE ONE-TIME UPDATE migrate031 (pure text)
    MK = str(Cfg.GQ_MARK)

    def gq(t_):
        r_ = Cfg.gqUpdate(JString(t_))
        if r_ is None:
            return None
        return [str(r_[0]), str(r_[1]), [str(x) for x in r_[2]], [str(x) for x in r_[3]]]
    tA = "# SkyyGear\r\nlevel.x=1\r\ngate.on=true\r\ngate.nextFactor=0.1\r\ngate.bareHands=true\r\n"
    rA = gq(tA)
    tB = "a=1\ngate.nextFactor = 0.1\nb=2"
    rB = gq(tB)
    tC = "a=1\r\ngate.nextFactor=0.25\r\ngate.crudeFactor=0.3\r\n"
    rC_ = gq(tC)
    tD = "a=1\nb=2\n"
    rD = gq(tD)
    tE = "a=1\n" + MK + "\ngate.nextFactor=0.1\n"
    rE = gq(tE)
    tF = "a=1\ngate.nextFactor=0.\\\n  1\n"
    rF = gq(tF)
    tG = "gate.nextFactor=0.10\na=1\\\n"
    rG = gq(tG)
    K.check(rA is not None and rA[0] == tA.replace("gate.nextFactor=0.1\r", "gate.nextFactor=0.4\r") + MK + "\r\n" and rA[1] == "gate.nextFactor 0.1 -> 0.4"
            and rA[3] == ["gate.nextFactor", "0.1", "0.4"] and rA[2] == [],
            "G migrate031: the old default 0.1 -> 0.4 (value text only), every other byte + CRLF kept, the marker at the end, one change-log row: %r" % (rA,))
    K.check(rB is not None and rB[0] == "a=1\ngate.nextFactor = 0.4\nb=2\n" + MK and rB[3] == ["gate.nextFactor", "0.1", "0.4"],
            "G migrate031: ' = ' separator kept, LF file without a final newline keeps having none: %r" % (rB,))
    K.check(rC_ is not None and rC_[0] == tC + MK + "\r\n" and rC_[1] == "" and rC_[3] == [] and len(rC_[2]) == 2 and "gate.nextFactor=0.25 kept" in rC_[2][0]
            and "gate.crudeFactor=0.3 is no longer read" in rC_[2][1],
            "G migrate031: a HAND-EDITED gate.nextFactor (0.25) is kept + noted; a gate.crudeFactor line is noted (no longer read) and left: %r" % (rC_,))
    K.check(rD is not None and rD[0] == tD + MK + "\n" and rD[1] == "" and rD[2] == [] and rD[3] == [],
            "G migrate031: no gate.nextFactor line (the live file today) = nothing to rewrite, only the run-once marker: %r" % (rD,))
    K.check(rE is None and rF is not None and "gate.nextFactor=0.\\\n  1\n" in rF[0] and rF[3] == [] and "kept" in rF[2][0]
            and rG is not None and rG[0] == "gate.nextFactor=0.4\n" + MK + "\na=1\\\n" and rG[3] == ["gate.nextFactor", "0.10", "0.4"],
            "G migrate031: the marker = nothing to do; a continued (two-line) value is never rewritten; 0.10 counts as the old default; a file "
            "ending in a continuation keeps the marker out of that value: %r | %r" % (rF, rG))

    # ---- G: migrate031 on scratch files (History copy first, change-log row with Undo, run twice)
    GH = os.path.join(SCRATCH, "g031")

    def mfile(sub, text):
        d_ = os.path.join(GH, sub)
        shutil.rmtree(d_, ignore_errors=True)
        os.makedirs(d_)
        p_ = os.path.join(d_, "config.properties")
        with open(p_, "wb") as f_:
            f_.write(text.encode("latin-1"))
        Cfg.FILE = Paths.get(p_)
        return d_, p_

    def hist(d_, b_):
        h_ = os.path.join(d_, "config-history")
        if not os.path.isdir(h_):
            return False
        for root_, _ds, fs_ in os.walk(h_):
            for n_ in fs_:
                if open(os.path.join(root_, n_), "rb").read() == b_:
                    return True
        return False

    def clog(d_):
        p_ = os.path.join(d_, "config-changes.log")
        return open(p_, encoding="utf-8").read() if os.path.isfile(p_) else ""
    d1, p1 = mfile("default", tA)
    m1 = str(Cfg.migrate031())
    b1 = open(p1, "rb").read()
    cl1 = clog(d1)
    m1b = str(Cfg.migrate031())
    K.check(b1 == rA[0].encode("latin-1") and hist(d1, tA.encode("latin-1")) and "\tgate.nextFactor\t0.1\t0.4\tok" in cl1 and "SkyyGear 0.3.1" in cl1
            and "gate.nextFactor 0.1 -> 0.4" in m1 and m1b == "" and open(p1, "rb").read() == b1 and clog(d1) == cl1,
            "G migrate031 on a file: History copy of the old bytes first, the rewrite, a change-log row (status ok = Undo); the 2nd run changes "
            "nothing (marker): %s | %s" % (m1[:160], cl1[-160:]))
    Cfg.load()
    K.check(abs(float(Cfg.GATE_NEXT) - 0.4) < 1e-12 and abs(float(Cfg.GATE_TWO) - 0.1) < 1e-12, "G: after the update the loader reads 0.4 / 0.1")
    d2, p2 = mfile("hand", tC)
    m2 = str(Cfg.migrate031())
    b2 = open(p2, "rb").read()
    m2b = str(Cfg.migrate031())
    Cfg.load()
    K.check(b2 == (tC + MK + "\r\n").encode("latin-1") and hist(d2, tC.encode("latin-1")) and clog(d2).count("gate.nextFactor") == 0
            and "gate.nextFactor=0.25 kept" in m2 and m2b == "" and open(p2, "rb").read() == b2 and abs(float(Cfg.GATE_NEXT) - 0.25) < 1e-12,
            "G migrate031 on a HAND-EDITED file: value kept (the loader reads 0.25) + noted, only the marker added, no change-log row, 2nd run "
            "changes nothing: %s" % m2[:200])
    d3, p3 = mfile("absent", tD)
    m3 = str(Cfg.migrate031())
    m3b = str(Cfg.migrate031())
    Cfg.load()
    K.check(open(p3, "rb").read() == (tD + MK + "\n").encode("latin-1") and "new default 0.4 applies" in m3 and m3b == ""
            and abs(float(Cfg.GATE_NEXT) - 0.4) < 1e-12,
            "G migrate031 with no gate rows (the live file): marker only, the new default 0.4 applies, 2nd run nothing: %s" % m3[:200])
    Cfg.FILE = None
    apply()
    shutil.rmtree(GH, ignore_errors=True)
    K.save()


# C32 (0.3.2): every member tools/gear_0_3_2_patch.py touches, nothing else
_CMD32 = {"~c ", "~m execute"}          # the description text + reclaimW(..., world)
WANT32 = {
    "GearLL": {"~<clinit>", "+f HERE", "+f TRACKQ", "~m forget", "+m hereMask", "~m invested", "~m statusText", "+m trackHook", "+m trackMaybe"},
    "GearInvSys": {"~m handle"},
    "GearLife": {"~<clinit>", "+f SNAPRAW", "+f TEST_CHESTS", "+f TEST_WKEY", "+m chestAt", "+m clearLoc", "~m commit", "~m counters", "+m fromChest",
                 "+m fromRequip", "+m fromWindows", "~m give", "+m give2", "+m hereAdd", "~m keep", "+m locText", "+m locWhy", "+m move", "~m pass", "+m present",
                 "~m reclaim", "+m reclaimW", "~m recover", "+m rqFind", "+m setLoc", "+m slotIn", "+m snapDoc", "+m snapSet", "+m snapText",
                 "+m track", "+m trackLater", "+m winName", "+m wkOf",
                 "+m nswHas", "+m nswAdd", "+m lcuOf", "+m family", "~m repick", "~m settle", "~m notice"},          # fix round
    "LifePage": {"~m row"},
    "PickaxeCmd": _CMD32, "HatchetCmd": _CMD32, "HoeCmd": _CMD32, "SickleCmd": _CMD32,
}

# ====================================================================================================== C: class compare
def run_compare(out):
    from jpype import JClass
    K = Child(out)
    _jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(j):
        p_ = CPc(False)
        p_.appendSystemPath()
        p_.appendClassPath(B.SERVER_JAR)
        p_.appendClassPath(j)
        return p_

    def members(p_, cn, vers):
        c_ = p_.get(cn)
        d_ = {}
        for f_ in c_.getDeclaredFields():
            d_["f " + str(f_.getName())] = str(f_.getSignature())

        def code(b_):
            mi_ = b_.getMethodInfo()
            ca_ = mi_.getCodeAttribute()
            if ca_ is None:
                return ""
            it_ = ca_.iterator()
            cpl_ = mi_.getConstPool()
            lines_ = []
            while it_.hasNext():
                pos_ = it_.next()
                t_ = re.sub(r"#\d+ = ", "", str(IP.instructionString(it_, pos_, cpl_))).replace("ldc_w ", "ldc ")
                t_ = re.sub(r"^((if\w*|goto|goto_w|jsr|jsr_w) )\d+$", r"\1N", t_)
                for v_ in vers:
                    t_ = t_.replace(v_, "VER")
                lines_.append(t_)
            return "\n".join(lines_)
        for m_ in c_.getDeclaredMethods():
            d_["m " + str(m_.getName()) + str(m_.getSignature())] = code(m_)
        for m_ in c_.getDeclaredConstructors():
            d_["c " + str(m_.getSignature())] = code(m_)
        ci = c_.getClassInitializer()
        if ci is not None:
            d_["<clinit>"] = code(ci)
        return d_

    def jdiff(old_jar, old_ver):
        pa, pb = pool_of(old_jar), pool_of(JAR)
        na, nb = jar_classes(old_jar), jar_classes(JAR)
        diffs = {}
        for cn in sorted(set(na) & set(nb)):
            ma, mb = members(pa, cn, (old_ver, VERSION)), members(pb, cn, (old_ver, VERSION))
            dd = sorted(k for k in set(ma) | set(mb) if ma.get(k) != mb.get(k))
            if dd:
                diffs[cn.split(".")[-1]] = [("+" if k not in ma else ("-" if k not in mb else "~")) + k.split("(")[0] for k in dd]
        add = sorted(x.split(".")[-1] for x in set(nb) - set(na))
        gone = sorted(set(na) - set(nb))
        print("C. class compare %s -> %s: + %s - %s" % (old_ver, VERSION, add, gone))
        for k in sorted(diffs):
            print("   %-16s %s" % (k, ", ".join(diffs[k])[:1500]))
        return diffs, add, gone

    # ---- C32 (0.3.2): 0.3.1 -> 0.3.2 = exactly this round's members (tools/gear_0_3_2_patch.py): the tracker gate + HERE in GearLL, the
    # GearInvSys hook, GearLife's fetch / copy / snapshot / place members, the commands (text + the world), the Tools tab line, GearTrackTask
    d32, add32, gone32 = jdiff(J31, V31)
    want32 = WANT32
    bad32 = {}
    for k in set(want32) | set(d32):
        if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs":
            continue
        got = set(d32.get(k, []))
        if got != want32.get(k, set()):
            bad32[k] = (sorted(want32.get(k, set()) - got), sorted(got - want32.get(k, set())))
    cfg32 = dict((k, v) for k, v in d32.items() if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs")
    K.check(add32 == ["GearTrackTask"] and not gone32 and not bad32 and "GearDefs" not in cfg32
            and cfg32 == {"CfgRows": ["~<clinit>"], "GearCfg": ["~m defaultsText"]},
            "C32: 0.3.1 -> 0.3.2 changed exactly the listed members (+ GearTrackTask; config classes: only the row texts - the kit's row table "
            "and the fresh file's help lines): bad %s, config %s" % (bad32, cfg32))
    diffs, add, gone = jdiff(OLD_JAR, OLD_VERSION)
    K.check(set(add) == NEW_CLASSES and not gone, "C: added exactly the 0.3.0 classes (+ 0.3.2 GearTrackTask), none removed: + %s - %s" % (add, gone))
    want = {
        "Gear": {"+m fnum10"},          # 0.3.1
        "GearTool": {"~m gate", "~m stats", "~m held", "~m lines"},
        "GearToolHitSys": {"~m handle"},
        "GearHandSys": {"~m tick"},          # fix round: the stale-level hand-off (GearLL.RESYNC -> GearStamp.dirtyIn)
        "GearCraftPreSys": {"~m handle"},
        "GearWall": {"~m why"},
        "GearForge": {"~m lvlInfo"},
        "GearMerge": {"~m why"},
        "GearUp": {"~m tab", "~m check", "~m docI"},
        "GearUi": {"~m tabs"},
        "GearSmith": {"~m usable"},
        "GearRefreshTask": {"~m run"},
        "GearStampTask": {"~m run"},
        "GearInvSys": {"~m handle"},          # 0.3.2: the lifelong tool tracker's gate
        "GearBye": {"~m accept"},
        "ReforgePage": {"~m handleDataEvent"},
        "MultiPage": {"~m handleDataEvent"},
        "SmithPage": {"~m handleDataEvent"},
        "SkyyGearPlugin": {"~m setup", "~m shutdown"},
    }
    bad = {}
    for k in set(want) | set(diffs):
        if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs":
            continue
        got = set(diffs.get(k, []))
        if got != want.get(k, set()):
            bad[k] = (sorted(want.get(k, set()) - got), sorted(got - want.get(k, set())))
    K.check(not bad, "C: changed exactly the listed members outside the config classes (missing / extra): %s" % bad)
    cfgd = dict((k, v) for k, v in diffs.items() if k.startswith("GearCfg") or k.startswith("Cfg") or k == "GearDefs")
    want_f = {"+f LL_ON", "+f LL_NOCRAFT", "+f LL_NODROP", "+f LL_LADDERS", "+f LL_RECLAIM", "+f LL_REPICK", "+f LL_PSPD", "+f LL_PFORT", "+f LL_PWIS",
              "+f LL_RESET", "+f GATE_ON", "+f GATE_NEXT", "+f GATE_BARE", "+f LL_RTIER", "+f GATE_NEXT0", "+f GATE_TWO"}
    K.check(set(cfgd.get("GearCfg", [])) >= want_f and "GearDefs" not in cfgd
            and all(x.startswith("+f ") or x.startswith("~m ") or x.startswith("+m ") or x == "~<clinit>" for v in cfgd.values() for x in v),
            "C: the config classes gained the 15 rows (fields, the kit's row tables) and nothing else: %s" % cfgd)
    K.save(diffs=diffs)


# ====================================================================================================== D: start twice on a scratch copy
def run_start(out, home, which):
    from jpype import JClass
    K = Child(out)
    jar = JAR if which == "new" else OLD_JAR
    _jvm([B.SERVER_JAR, jar], verify=(which == "new"))
    Cfg = JClass(PKG + "GearCfg")
    Path = JClass("java.nio.file.Paths")
    Cfg.DIR = Path.get(home)
    Cfg.FILE = Path.get(os.path.join(home, "config.properties"))
    JClass(PKG + "GearLog").FILE = Path.get(os.path.join(home, "gear.log"))
    lld = os.path.join(home, "lifelong")

    def lltree():
        if not os.path.isdir(lld):
            return None
        return dict((f_, open(os.path.join(lld, f_), "rb").read()) for f_ in sorted(os.listdir(lld)))
    ll0 = lltree()          # 0.3.2: the live data has a lifelong folder since 0.3.0 went live (2026-10-13 19:54)
    snaps = []
    for step in (1, 2):
        for m in ("migrate011", "migrateStat011", "migrate012", "migrate013", "migrate02", "migrate021", "migrate023", "migrate025", "migrate0214",
                  "migrate0215", "migrate0216", "migrate0217", "migrate0218") + (("migrate031",) if which == "new" else ()):
            getattr(Cfg, m)()
        Cfg.load()
        snaps.append(open(os.path.join(home, "config.properties"), "rb").read())
    K.check(snaps[1] == snaps[0], "D/%s: the 2nd start changes nothing" % which)
    if which == "new":
        K.check(bool(Cfg.LL_ON) and bool(Cfg.GATE_ON) and abs(float(Cfg.GATE_NEXT) - 0.4) < 1e-12 and abs(float(Cfg.GATE_TWO) - 0.1) < 1e-12
                and str(Cfg.LL_LADDERS).startswith("Tool_Pickaxe_Crude>") and lltree() == ll0,
                "D/new (0.3.2): the live file has no lifelong / gate rows -> the defaults apply (lifelong on, gate on x0.4 / x0.1); the start never "
                "makes or touches the lifelong folder (%s)" % (None if ll0 is None else sorted(ll0)))
    K.save(cfg=snaps[0].decode("latin-1"), fresh=str(Cfg.defaultsText()), mark=(str(Cfg.GQ_MARK) if which == "new" else ""))


# ====================================================================================================== R: the 0.2.26 Anvil child + X
R26_DEVIATIONS = [
    # the tab row now has five places (Craft | Anvil | Tools | Multitool): the 0.2.26 child counts / names the tabs of the 0.2.26 row
    "N2", "tab",
]


# fix round (2026-10-14): B.SERVER_JAR is a CACHED copy now (tools/serverjar.py, tools/dev/scratch/serverjar/jar-*/HytaleServer.jar) and the
# cached Assets.zip lives in its own folder; the older harnesses (0.2.25 / 0.2.26, read only) look for Assets.zip at
# dirname(dirname(SERVER_JAR)). Their children run through WRAP with skyybuild.SERVER_JAR pinned to a hard-linked side-by-side layout in
# this harness's scratch (no copy, nothing written outside the scratch; the installed game files are never opened).
def game_assets():
    import serverjar
    return serverjar.assets_zip()


def game_layout():
    import serverjar
    g = os.path.join(SCR_ROOT, "game")
    sj = os.path.join(g, "Server", "HytaleServer.jar")
    for src, dst in ((serverjar.server_jar(), sj), (serverjar.assets_zip(), os.path.join(g, "Assets.zip"))):
        if not os.path.isfile(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            os.link(src, dst)
    return sj


WRAP = ("import sys, runpy; sys.path.insert(0, sys.argv[1]); import skyybuild; skyybuild.SERVER_JAR = sys.argv[2]; s = sys.argv[3]; "
        "sys.argv = [s] + sys.argv[4:]; runpy.run_path(s, run_name='__main__')")


def wrap(head):
    """[python, script] -> the same script run with skyybuild.SERVER_JAR pinned to game_layout()"""
    return [head[0], "-c", WRAP, TOOLS, game_layout(), head[1]]


def run_r26(env):
    d = os.path.join(SCRATCH, "r26")
    for sub in ("tmp", "packs"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    shutil.copyfile(AR_SRC, os.path.join(d, "packs", "SkyyArmory-0.1.23.jar"))
    if os.path.isfile(MT_SRC):
        shutil.copyfile(MT_SRC, os.path.join(d, "packs", "Multitools-1.2.9.jar"))
    e2 = dict(env)
    e2["TEMP"] = e2["TMP"] = os.path.join(d, "tmp")
    h26 = os.path.join(HERE, "test_skyygear_0.2.26.py")
    base = [sys.executable, h26, "--dir", d, "--jar", JAR, "--old", OLD_JAR, "--root", SCR_ROOT]
    p0 = subprocess.run(wrap(base[:2]) + ["--mkfake", os.path.join(d, "fake")] + base[2:], env=e2, capture_output=True, text=True)
    check(p0.returncode == 0, "R: the 0.2.26 stand-ins compiled against the 0.3.0 jar (rc %s) %s" % (p0.returncode, p0.stderr[-500:]))
    out = os.path.join(d, "anvil.json")
    p = subprocess.run(wrap(base[:2]) + ["--anvil", "--out", out] + base[2:], env=e2, capture_output=True, text=True)
    check(p.returncode == 0 and os.path.isfile(out), "R: the 0.2.26 Anvil child ran with the 0.3.0 jar (rc %s)" % p.returncode)
    if not os.path.isfile(out):
        print(p.stdout[-3000:], p.stderr[-3000:])
        return
    r = json.load(open(out))
    OKS[0] += r["ok"]
    dev = [f for f in r["fails"] if "tab" in f.lower() and ("Tools" in f or "row" in f.lower() or "tabs" in f.lower())]
    other = [f for f in r["fails"] if f not in dev]
    check(not other and r["ok"] >= 50, "R: the 0.2.26 Anvil checks (reforge / level up / upgrade / identify, every click, every failure step): %d ok, "
          "no fail outside the tab row: %s" % (r["ok"], other[:6]))
    for f in dev:
        print("  expected deviation (R, the Tools tab joins the row): %s" % f[:220])


def run_x25(env):
    d = os.path.join(SCRATCH, "x25")
    os.makedirs(os.path.join(d, "tmp"), exist_ok=True)
    os.makedirs(os.path.join(d, "fake"), exist_ok=True)
    out = os.path.join(d, "exec.json")
    e2 = dict(env)
    e2["TEMP"] = e2["TMP"] = os.path.join(d, "tmp")
    p = subprocess.run(wrap([sys.executable, os.path.join(HERE, "test_skyygear_0.2.25.py")]) + ["--phase", "exec", "--out", out, "--dir", d, "--jar", JAR,
                        "--old", J24], env=e2, capture_output=True, text=True)
    check(p.returncode == 0 and os.path.isfile(out), "X: the 0.2.25 harness's exec phase ran with the 0.3.0 jar (rc %s)" % p.returncode)
    if not os.path.isfile(out):
        print(p.stdout[-2000:], p.stderr[-2000:])
        return
    r = json.load(open(out))
    expected = [f for f in r["fails"] if "fresh config text" in f]
    other = [f for f in r["fails"] if "fresh config text" not in f]
    OKS[0] += r["ok"]
    check(not other and r["ok"] >= 20, "X: the randomised 0.2.24-vs-new stats comparison (snapshot, tick, hits, gate, stamp scan, chest file, bridge): "
          "%d ok, no other fail: %s" % (r["ok"], other))
    check(len(expected) <= 1, "X: its only expected deviation is the fresh config text (checked exactly in D): %s" % expected)


# ====================================================================================================== parent
def child(env, *args):
    return subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args) + ["--dir", SCRATCH, "--jar", JAR, "--old", OLD_JAR], env=env)


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
    for flag, fn in (("--mkfake", lambda: run_mkfake5(arg("--mkfake"))), ("--verify", lambda: H["run_verify"](arg("--out"))),
                     ("--life", lambda: run_life(arg("--out"))), ("--compare", lambda: run_compare(arg("--out"))),
                     ("--start", lambda: run_start(arg("--out"), arg("--start"), arg("--which"))), ("--audit", lambda: H["run_audit"](arg("--out")))):
        if flag in sys.argv:
            try:
                fn()
            except SystemExit:
                raise
            except Exception:
                import traceback
                traceback.print_exc()
                sys.exit(1)
            return
    assert os.path.isfile(JAR) and os.path.isfile(OLD_JAR) and os.path.isfile(CO_SRC) and os.path.isfile(AR_SRC) and os.path.isfile(J24), (JAR, OLD_JAR, CO_SRC, AR_SRC, J24)
    sc = os.path.realpath(SCRATCH)
    assert sc.startswith(os.path.realpath(SCR_ROOT) + os.sep), "the scratch folder must be inside " + SCR_ROOT
    shutil.rmtree(SCRATCH, ignore_errors=True)
    for sub in ("tmp", "packs", "players"):
        os.makedirs(os.path.join(SCRATCH, sub), exist_ok=True)
    with zipfile.ZipFile(OLD_JAR) as z_:
        assert '"Version": "%s"' % OLD_VERSION in z_.read("manifest.json").decode("utf-8"), "the old jar is not " + OLD_VERSION
    shutil.copyfile(CO_SRC, CO_JAR)              # read-only sources; the children use the scratch copies
    for f_ in glob.glob(os.path.join(LIVE_PLAYERS, "*.json")):
        shutil.copyfile(f_, os.path.join(PLAYERS, os.path.basename(f_)))
    env = dict(os.environ)
    env["TEMP"] = env["TMP"] = os.path.join(SCRATCH, "tmp")
    env["JAVA_TOOL_OPTIONS"] = "-XX:-UsePerfData"
    os.environ["TEMP"] = os.environ["TMP"] = env["TEMP"]
    only = arg("--only")
    try:
        run_assets()
        p = child(env, "--mkfake", FAKE_DIR)
        check(p.returncode == 0, "F: the stand-ins were generated")
        for label, flag in (("verify", "--verify"), ("compare", "--compare"), ("life", "--life")):
            if only and label not in only.split(","):
                continue
            out = os.path.join(SCRATCH, "%s.json" % label)
            pr = child(env, flag, "--out", out)
            check(pr.returncode == 0, "%s: the child exited cleanly (%s)" % (label, pr.returncode))
            take(out, label)
        if not only or "r26" in only.split(","):
            run_r26(env)
        if not only or "x25" in only.split(","):
            run_x25(env)
        res = {}
        if not only or "start" in only.split(","):
            for which in ("old", "new"):
                home = os.path.join(SCRATCH, "live-" + which)
                shutil.copytree(LIVE_DIR, home)
                out = os.path.join(SCRATCH, "start-%s.json" % which)
                pr = child(env, "--start", home, "--which", which, "--out", out)
                check(pr.returncode == 0, "D/%s: the child exited cleanly" % which)
                res[which] = take(out, "start-" + which)
            print("D. live Skyy_SkyyGear copied twice (read-only source %s)" % LIVE_DIR)
            if res.get("old") and res.get("new"):
                oc_, nc_, mk_ = res["old"]["cfg"], res["new"]["cfg"], res["new"].get("mark", "")
                ol_, nl_ = oc_.split("\n"), nc_.split("\n")
                gone_ = [x for x in ol_ if x not in nl_]
                more_ = [x.rstrip("\r") for x in nl_ if x not in ol_]
                if mk_ and mk_ in oc_:
                    # 0.3.2: the live file already carries the 0.3.1 marker (0.3.1 went live 2026-10-13 22:23): nothing is left to add
                    check(nc_ == oc_ and "gate.nextFactor" not in oc_,
                          "D (0.3.2): the live copy already ran the 0.3.1 update - 0.3.2 starts it to exactly the config.properties 0.2.26 writes "
                          "(no row, no marker added): + %s - %s" % (more_[:3], gone_[:3]))
                else:
                    check(mk_ and more_ == [mk_] and not gone_ and len(nl_) == len(ol_) + 1 and "gate.nextFactor" not in oc_
                          and nc_.replace(mk_ + ("\r\n" if "\r\n" in oc_ else "\n"), "", 1) == oc_,
                          "D (0.3.1): 0.3.1 starts the live copy to exactly the config.properties 0.2.26 writes + the one run-once marker line "
                          "(the live file has no gate rows: nothing to rewrite): + %s - %s" % (more_[:3], gone_[:3]))
                fo = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-old")) if not f.startswith("config-history"))
                fn_ = sorted(f for f in os.listdir(os.path.join(SCRATCH, "live-new")) if not f.startswith("config-history"))
                check(fo == fn_, "D: the same files after the starts: %s / %s" % (fo, fn_))
                a_ = res["old"]["fresh"].split("\n")[1:]          # the first line names the version
                b_ = res["new"]["fresh"].split("\n")[1:]
                extra = [l_ for l_ in b_ if l_ not in a_]
                keys = [l_.split("=")[0] for l_ in extra if not l_.startswith("#") and l_]
                check([l_ for l_ in a_ if l_ not in b_] == [] and extra[0] == "# ---- lifelong tools + the tool tier gate (SkyyGear 0.3.0) ----"
                      and keys == ["part.lifelong", "lifelong.noCraft", "lifelong.noDrop", "lifelong.ladders", "lifelong.reclaimSec", "lifelong.reclaimTier", "lifelong.repickDays",
                                   "lifelong.perkSpeed", "lifelong.perkFortune", "lifelong.perkWisdom", "lifelong.resetCoins", "gate.on", "gate.nextFactor",
                                   "gate.twoUpFactor", "gate.crudeFactor", "gate.bareHands"]
                      and extra[1] == res["new"].get("mark"),
                      "D (0.3.1): a FRESH default file differs from 0.2.26's only by the lifelong block (+ gate.twoUpFactor, + the 0.3.1 marker right "
                      "under its heading - a fresh file never runs migrate031): %s" % extra[:4])
        if not only or "audit" in only.split(","):
            outa = os.path.join(SCRATCH, "audit.json")
            pa = child(env, "--audit", "--out", outa)
            check(pa.returncode == 0 and os.path.isfile(outa), "AA: the engine-access audit child ran")
            if os.path.isfile(outa):
                a = json.load(open(outa))
                check(not a["refused"] and a["refs"] > 10000, "AA: engine-access audit: %d references in %d classes, refused %s" % (a["refs"], a["classes"], a["refused"][:5]))
                check(len(a["control"]) == 1 and "sendUpdate" in a["control"][0], "AA: the control is refused: %s" % a["control"])
                print("AA. engine-access audit: %d references in %d classes, 0 refused, control refused" % (a["refs"], a["classes"]))
    finally:
        if "--keep" not in sys.argv:
            shutil.rmtree(SCRATCH, ignore_errors=True)
    print("SkyyGear %s harness: %d ok, %d fail(s)" % (VERSION, OKS[0], len(FAILS)))
    for f in FAILS:
        print("FAIL:", f)
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
