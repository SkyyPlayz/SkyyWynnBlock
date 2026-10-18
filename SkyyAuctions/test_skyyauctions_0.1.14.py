"""Harness for SkyyAuctions 0.1.14 (the TT_VERSION 3 level bands + tier table in the Browse sort, and the forced player save (R8) fixed:
the engine's shallow holder instead of Store.copyEntity; tools/auctions_0_1_14_patch.py). Build first:
python tools/auctions_0_1_14_patch.py && python SkyyAuctions/build_skyyauctions_0.1.14.py

    python SkyyAuctions/test_skyyauctions_0.1.14.py [--dir <folder inside tools/dev/scratch/>] [--keep] [--bz <SkyyBazaar jar>]

Phases (fresh child JVMs, -Xverify:all):
  A    verify   every class loads + initialises
  C    compare  0.1.13 -> 0.1.14: AhItem (re-baked TT_SPEC + bands), AhStore (shallowHolder, forceSave, SAVE_FAILS / SAVES) + the version texts
  TT   THE TABLE: AhItem.TT_SPEC of 0.1.14 = tools/tier_tags.py (TT_VERSION 3) ROWS exactly; 0.1.13's = TT_VERSION 2 (git a50a14af); every
       row whose tier moved is a gathering-ladder id (logs, crops, seeds, their Enchanted items) - no metal / ore / tool / weapon / armor row
       moved; the 6 Enchanted alloys + the Mushroom spores / Eternal spores are in; AhItem.lvTier / sortTier (real class) = TT.tier_for_level
       for every level 0-150 (+ Onyxium ids T16, untiered 99)
  STATIC the root cause in the engine bytecode: Store.copyEntity -> ArchetypeChunk.copyEntity clones every component -> Entity.clone() =
       EntityModule.getCodec(getClass()).encode(...); EntityModule.setup registers Player with registerComponent (never registerEntity, so
       codecMap has no Player); Player has no clone override; the engine's own save = PlayerSavingSystems.createShallowHolder (no clone).
       0.1.13 forceSave = Store.copyEntity + SAVE_BROKEN on the first throw; 0.1.14 = AhStore.shallowHolder (getArchetype / getComponent /
       EntityStore.REGISTRY.newHolder, no clone); afterTrade still saves AFTER the trade's own work (the R1 / R4 order)
  SAVE EXECUTED on a real engine Store (ComponentRegistry + addStore + addEntity, the Player component, World / WorldConfig / EntityStore
       allocated with only the fields the guard reads; EntityModule.codecMap without Player = the live server):
       REPRO 0.1.13: store.copyEntity(ref) throws the NPE of the logs ("... because "codec" is null"); AhStore.forceSave never reaches
             Player.saveConfig and sets SAVE_BROKEN on the first call (every later trade: markNeedsSave only)
       FIX   0.1.14: every forceSave reaches Player.saveConfig(world, holder, true) with a holder whose Player component IS the live one
             (nothing cloned); a world that does not save players / is save-locked is skipped; a throwing saveConfig counts SAVE_FAILS, only
             5 in a row set SAVE_BROKEN, a success resets the count; forceSave never touches a record, the claims or the inventory
  HUB / RB / MK / D (live) the 0.1.12 harness's phases on this jar - unchanged behaviour
  AA   engine-access audit
Exit code 1 on any failure.
"""
import os, sys, re, zipfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK
import tier_tags as TT

_cmp0 = HK.run_compare
_sp = importlib.util.spec_from_file_location("ah0113test", os.path.join(HERE, "test_skyyauctions_0.1.13.py"))
T13 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T13)
HK.run_compare = _cmp0
T10, T11, TB, H, T12 = T13.T10, T13.T11, T13.TB, T13.H, T13.T12

VERSION = "0.1.14"
OLD_VERSION = "0.1.13"
PKG = "com.skyy.auctions."
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyyAuctions-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyyAuctions-%s.jar" % OLD_VERSION)
BZ_JAR = T10.BZ_JAR
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "mobauc", "ah")))
EXPECT = {"AhItem": ["~m ttMap", "~m lvTier"],                                          # the re-baked TT_SPEC (inlined into ttMap) + the bands
          "AhStore": ["+f SAVES", "+f SAVE_FAILS", "+m shallowHolder", "~<clinit>", "~m forceSave"],   # R8: the shallow holder
          "AhCmds": ["~m status"], "CfgFn": ["~m opExport"], "CfgRows": ["~m header"],   # the version text
          "SkyyAuctionsPlugin": ["~m setup"]}                                          # the ready line
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = []
TT2_COMMIT = "a50a14af"     # the last commit with tools/tier_tags.py TT_VERSION 2 (the table 0.1.13 was built on)
EE = "com.hypixel.hytale.server.core.asset.type.entityeffect.config.EntityEffect"
GATHER_PREFIXES = ("Wood_", "Plant_Crop_", "Plant_Seeds_", "Plant_Spores_", "Skyy_Ench_")
NEW_ROWS = {"Skyy_Ench_Bronze": 3, "Skyy_Ench_Electrum": 3, "Skyy_Ench_Dusk": 6, "Skyy_Ench_Azurvane": 9, "Skyy_Ench_Cinder": 12,
            "Skyy_Ench_Lumen": 15, "Plant_Seeds_Mushroom": 15, "Plant_Spores_Mushroom_Eternal": 15, "Skyy_Ench_Mushroom": 15}


def tt_v2(scratch):
    d = os.path.join(scratch, "tt2")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "tier_tags_v2.py")
    open(p, "wb").write(subprocess.check_output(["git", "show", TT2_COMMIT + ":tools/tier_tags.py"], cwd=ROOT))
    sp = importlib.util.spec_from_file_location("tier_tags_v2", p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    assert m.TT_VERSION == "2", m.TT_VERSION
    return m


def run_tier(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    V2 = tt_v2(scratch)
    new, old = T13.spec_in(jar, "com/skyy/auctions/AhItem.class"), T13.spec_in(OLD_JAR, "com/skyy/auctions/AhItem.class")
    K.eq(new, dict((i, TT.tier(i)) for i in TT.ROWS), "TT the new jar's table = tools/tier_tags.py TT_VERSION 3 (%d rows)" % len(TT.ROWS))
    K.eq(dict((i, t) for i, t in old.items() if V2.tier(i) != t), {}, "TT the old jar's table = TT_VERSION 2 (git %s)" % TT2_COMMIT)
    K.eq(sorted(set(old) - set(new)), [], "TT no row dropped")
    moved = sorted(i for i in old if new[i] != old[i])
    K.eq([i for i in moved if not i.startswith(GATHER_PREFIXES)], [], "TT every moved row is a gathering-ladder id (logs / crops / seeds / their Enchanted)")
    K.eq([i for i in moved if i.startswith("Skyy_Ench_") and i[len("Skyy_Ench_"):] in TT.LADDER], [], "TT no Enchanted METAL row moved")
    K.eq(dict((i, new.get(i)) for i in NEW_ROWS), NEW_ROWS, "TT the 6 Enchanted alloys + the Mushroom spores / Eternal spores / Enchanted Mushroom")
    K.check(new.get("Wood_Maple_Trunk") == 3 and new.get("Wood_Gumboab_Trunk") == 6 and new.get("Plant_Crop_Turnip_Item") == 6,
            "TT spec 8 hovers: Maple log T3, Gumboab log T6, Turnip T6")
    added = sorted(set(new) - set(old))
    K.notes.append("TT %d rows; %d moved (%s ...); %d new (%s ...)" % (len(new), len(moved), ", ".join("%s %d->%d" % (i, old[i], new[i]) for i in moved[:4]),
                                                                     len(added), ", ".join(added[:5])))
    HK.jvm([B.SERVER_JAR, jar], verify=True)
    I = JClass(PKG + "AhItem")
    bad = [(l, x) for l in range(0, 151) for x in ("Weapon_Sword_Iron", "Armor_Onyxium_Chest", "Weapon_Sword_Lumen_SkyWynn", "Armor_Copper_Head")
           if int(I.lvTier(x, l)) != TT.tier_for_level(l, x)]
    K.eq(bad, [], "TT AhItem.lvTier = tools/tier_tags.py tier_for_level for every level 0-150")
    K.eq([int(I.lvTier("Weapon_Sword_Iron", l)) for l in (0, 7, 8, 14, 15, 19, 20, 27, 28, 35, 40, 48, 55, 60, 68, 75, 80, 88, 94, 95, 150)],
         [1, 1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 14, 15, 15], "TT the band starts (spec 1: Iron 8, Bronze 15, Thorium 20 ... Lumen 95)")
    K.eq([int(I.sortTier(x, l)) for x, l in (("Ore_Thorium", -1), ("Ingredient_Bar_Lumen_SkyWynn", -1), ("Weapon_Sword_Iron", 16), ("Weapon_Sword_Iron", 50),
                                              ("Armor_Onyxium_Chest", 5), ("Skyy_No_Such_Thing", -1), ("Ore_Copper", 99), ("Skyy_Ench_Bronze", -1),
                                              ("Plant_Spores_Mushroom_Eternal", -1))],
         [4, 15, 3, 8, 16, 99, 1, 3, 15], "TT AhItem.sortTier: table rows, level bands, Onyxium, untiered last, the new rows")
    K.save()


def _code_of(pool, IP, cn, mn):
    out_ = []
    for m_ in pool.get(cn).getDeclaredMethods():
        if str(m_.getName()) != mn:
            continue
        ca_ = m_.getMethodInfo().getCodeAttribute()
        if ca_ is None:
            continue
        it_, cpl_ = ca_.iterator(), m_.getMethodInfo().getConstPool()
        while it_.hasNext():
            out_.append(str(IP.instructionString(it_, it_.next(), cpl_)))
    return "\n".join(out_)


def run_static(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.JAVASSIST], verify=False)
    CPc = JClass("javassist.ClassPool")
    IP = JClass("javassist.bytecode.InstructionPrinter")

    def pool_of(*cp):
        p_ = CPc(False)
        p_.appendSystemPath()
        for c in cp:
            p_.appendClassPath(c)
        return p_
    pe = pool_of(B.SERVER_JAR)
    code = lambda p_, cn, mn: _code_of(p_, IP, cn, mn)
    K.check("clone" not in [str(m.getName()) for m in pe.get("com.hypixel.hytale.server.core.entity.entities.Player").getDeclaredMethods()],
            "STATIC the engine's Player does not override clone() (Entity.clone is used)")
    ec = code(pe, "com.hypixel.hytale.server.core.entity.Entity", "clone")
    K.check("EntityModule.getCodec" in ec and "DirectDecodeCodec.encode" in ec, "STATIC Entity.clone() = EntityModule.getCodec(getClass()).encode(...)")
    K.check("codecMap" in code(pe, "com.hypixel.hytale.server.core.modules.entity.EntityModule", "getCodec"), "STATIC EntityModule.getCodec reads codecMap")
    su = code(pe, "com.hypixel.hytale.server.core.modules.entity.EntityModule", "setup").splitlines()
    ix = [i for i, l in enumerate(su) if "entities.Player.CODEC" in l]
    K.check(len(ix) == 1 and "ComponentRegistryProxy.registerComponent" in su[ix[0] + 1],
            "STATIC EntityModule.setup registers Player with registerComponent (never registerEntity): codecMap has no Player")
    K.check("Component.clone" in code(pe, "com.hypixel.hytale.component.ArchetypeChunk", "copyEntity"),
            "STATIC Store.copyEntity -> ArchetypeChunk.copyEntity clones every component (the Player too)")
    sh = code(pe, "com.hypixel.hytale.server.core.modules.entity.player.PlayerSavingSystems", "createShallowHolder")
    K.check("ArchetypeChunk.getComponent" in sh and "ComponentRegistry.newHolder" in sh and "clone" not in sh,
            "STATIC the engine's own player save uses a shallow holder (getComponent + newHolder, no clone)")
    po, pn = pool_of(B.SERVER_JAR, OLD_JAR), pool_of(B.SERVER_JAR, jar)
    fo, fn = code(po, PKG + "AhStore", "forceSave"), code(pn, PKG + "AhStore", "forceSave")
    K.check("Store.copyEntity" in fo and "AhStore.SAVE_BROKEN" in fo, "STATIC 0.1.13 forceSave = Store.copyEntity (always the NPE) + SAVE_BROKEN on the first throw")
    sw = code(pn, PKG + "AhStore", "shallowHolder")
    K.check("copyEntity" not in fn and "AhStore.shallowHolder" in fn and "Store.getArchetype" in sw and "ComponentRegistry.newHolder" in sw
            and "clone" not in sw and "Store.getComponent" in sw and "EntityStore.REGISTRY" in sw,
            "STATIC 0.1.14 forceSave = AhStore.shallowHolder (Store.getArchetype + getComponent + EntityStore.REGISTRY.newHolder, nothing cloned)")
    K.check("AhStore.SAVE_FAILS" in fn and "markNeedsSave" in fn and fn.index("markNeedsSave") < fn.index("AhStore.shallowHolder") < fn.index("Player.saveConfig"),
            "STATIC 0.1.14 forceSave: markNeedsSave first, then the holder, then saveConfig; failures counted in a row")
    puts = [l for l in fn.splitlines() if "putstatic" in l or "putfield" in l]
    K.check(all("SAVE_BROKEN" in l for l in puts), "STATIC 0.1.14 forceSave writes no field but SAVE_BROKEN (no record / claim / inventory state): %s" % puts)
    at = code(pn, PKG + "AhStore", "afterTrade")
    _nocp = lambda t: re.sub(r"#\d+", "#", t)
    K.eq(_nocp(at), _nocp(code(po, PKG + "AhStore", "afterTrade")), "STATIC afterTrade unchanged (the save still runs after the trade's own work - R1 / R4)")
    K.save()


def _engine(jar):
    """a REAL engine Store with one Player entity (the class registered as a plain component, EntityModule.codecMap without it = the live
    server); World / WorldConfig / EntityStore allocated with only the fields forceSave's guard reads. Returns a dict of handles."""
    from jpype import JClass, JArray, JString, JImplements, JOverride
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    JClass("com.hypixel.hytale.server.core.Options").parse(JArray(JString)(["--universe", os.path.join(HK.arg("--dir"), "universe")]))
    uf = JClass("sun.misc.Unsafe").class_.getDeclaredField("theUnsafe")
    uf.setAccessible(True)
    U = uf.get(None)

    def fld(c, n):
        k = c
        while k is not None:
            try:
                f = k.getDeclaredField(n)
                f.setAccessible(True)
                return f
            except Exception:
                k = k.getSuperclass()
        raise KeyError(n)
    PLA = JClass("com.hypixel.hytale.server.core.entity.entities.Player")
    ES = JClass("com.hypixel.hytale.server.core.universe.world.storage.EntityStore")
    EM = JClass("com.hypixel.hytale.server.core.modules.entity.EntityModule")
    em = U.allocateInstance(EM.class_)
    fld(EM.class_, "codecMap").set(em, JClass("java.util.HashMap")())
    fld(EM.class_, "classMap").set(em, JClass("java.util.HashMap")())
    fld(EM.class_, "state").set(em, JClass("com.hypixel.hytale.server.core.plugin.PluginState").valueOf("ENABLED"))
    fld(EM.class_, "instance").set(None, em)
    cp = JClass("javassist.ClassPool")(True)
    cp.appendClassPath(B.SERVER_JAR)
    CtM, CtF, CtC = JClass("javassist.CtNewMethod"), JClass("javassist.CtField"), JClass("javassist.CtNewConstructor")
    # a Player whose saveConfig records its holder instead of writing a file (THROW > 0: it throws that many times)
    sub = cp.makeClass("com.hypixel.hytale.server.core.entity.entities.SkyyAhTestPlayer", cp.get(PLA.class_.getName()))
    for d in ("public static volatile Object LAST = null;", "public static volatile int CALLS = 0;", "public static volatile int THROW = 0;",
              "public static volatile Object WORLD = null;", "public static volatile boolean FORCE = false;"):
        sub.addField(CtF.make(d, sub))
    sub.addMethod(CtM.make("public java.util.concurrent.CompletableFuture saveConfig(com.hypixel.hytale.server.core.universe.world.World w, "
                           "com.hypixel.hytale.component.Holder h, boolean f) { CALLS++; if (THROW > 0) { THROW--; throw new IllegalStateException(\"test save failure\"); } "
                           "LAST = h; WORLD = w; FORCE = f; return java.util.concurrent.CompletableFuture.completedFuture(null); }", sub))
    SubC = sub.toClass(PLA.class_)
    AS = JClass("com.hypixel.hytale.assetstore.AssetStore")
    fake = cp.makeClass("com.hypixel.hytale.assetstore.SkyyAhTestFakeStore", cp.get(AS.class_.getName()))
    fake.addConstructor(CtC.make("public SkyyAhTestFakeStore() { super((com.hypixel.hytale.assetstore.AssetStore$Builder) null); }", fake))
    FakeCls = fake.toClass(AS.class_)
    Ld = PLA.class_.getClassLoader()

    @JImplements("java.util.function.IntFunction")
    class Arr(object):
        @JOverride
        def apply(self, n):
            return JClass("java.lang.reflect.Array").newInstance(JClass("java.lang.Class").forName(EE, False, Ld), n)
    st = U.allocateInstance(FakeCls)       # EntityEffect's store (WorldConfig -> GameplayConfig's class init reads it)
    fld(AS.class_, "assetMap").set(st, JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")(Arr()))
    fld(JClass("java.lang.Class").forName(EE, False, Ld), "STORE").set(None, st)

    @JImplements("java.util.function.Supplier")
    class Sup(object):
        @JOverride
        def get(self):
            return U.allocateInstance(SubC)
    R = JClass("com.hypixel.hytale.component.ComponentRegistry")()
    pt = R.registerComponent(SubC, Sup())
    W = JClass("com.hypixel.hytale.server.core.universe.world.World")
    w = U.allocateInstance(W.class_)
    locks = JClass("java.util.concurrent.atomic.AtomicInteger")(0)
    fld(W.class_, "savingLocks").set(w, locks)
    WC = JClass("com.hypixel.hytale.server.core.universe.world.WorldConfig")
    wc = U.allocateInstance(WC.class_)
    fld(WC.class_, "isSavingPlayers").setBoolean(wc, True)
    fld(W.class_, "worldConfig").set(w, wc)
    es = U.allocateInstance(ES.class_)
    fld(ES.class_, "world").set(es, w)
    store = R.addStore(es, JClass("com.hypixel.hytale.component.EmptyResourceStorage")())
    h = R.newHolder()
    pl = U.allocateInstance(SubC)
    h.addComponent(pt, pl)
    ref = store.addEntity(h, JClass("com.hypixel.hytale.component.AddReason").SPAWN)
    return {"store": store, "ref": ref, "pl": pl, "pt": pt, "w": w, "wc": wc, "locks": locks, "fld": fld,
            "SP": JClass("com.hypixel.hytale.server.core.entity.entities.SkyyAhTestPlayer"), "WC": WC}


def run_save_old(out, _jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E = _engine(OLD_JAR)
    store, ref, pl, SP = E["store"], E["ref"], E["pl"], E["SP"]
    msg = ""
    try:
        store.copyEntity(ref)
    except Exception as e:
        msg = str(e)
    K.check("NullPointerException" in msg and 'because "codec" is null' in msg and "DirectDecodeCodec.encode" in msg,
            "REPRO 0.1.13: Store.copyEntity(player ref) throws the NPE of the server logs: %s" % msg[:200])
    S, C = JClass(PKG + "AhStore"), JClass(PKG + "AhCfg")
    C.FORCE_SAVE = True
    S.SAVE_BROKEN = False
    for _i in range(3):
        S.forceSave(pl, ref, store)
    K.check(bool(S.SAVE_BROKEN) and int(SP.CALLS) == 0, "REPRO 0.1.13: forceSave never reaches Player.saveConfig and is SAVE_BROKEN after the first call (calls %d)" % int(SP.CALLS))
    K.notes.append("REPRO 0.1.13 copyEntity: %s" % msg[:160])
    K.save()


def run_save_new(out, jar, scratch, _home):
    from jpype import JClass
    K = HK.Child(out)
    E = _engine(jar)
    store, ref, pl, SP, w, locks, wc, fld = E["store"], E["ref"], E["pl"], E["SP"], E["w"], E["locks"], E["wc"], E["fld"]
    S, C = JClass(PKG + "AhStore"), JClass(PKG + "AhCfg")
    C.FORCE_SAVE = True
    S.SAVE_BROKEN = False
    live0, dirty0 = int(S.LIVE.size()), int(S.DIRTY.size())
    hh = S.shallowHolder(store, ref)
    comps = [c for c in hh.getComponents() if c is not None] if hasattr(hh, "getComponents") else []
    K.check(hh is not None, "FIX shallowHolder builds a holder on a real engine Store")
    K.check(any(c.equals(pl) and c is not None and JClass("java.lang.System").identityHashCode(c) == JClass("java.lang.System").identityHashCode(pl) for c in comps) or not comps,
            "FIX the holder's Player component IS the live one (nothing cloned)")
    for i in range(3):
        S.forceSave(pl, ref, store)
    K.check(int(SP.CALLS) == 3 and SP.LAST is not None and bool(SP.FORCE) and SP.WORLD.equals(w) and not bool(S.SAVE_BROKEN) and int(S.SAVES.get()) == 3,
            "FIX every forceSave reaches Player.saveConfig(world, holder, true) (3 of 3; SAVES %d)" % int(S.SAVES.get()))
    pc = None
    try:
        pc = SP.LAST.getComponent(E["pt"])
    except Exception:
        pc = None
    K.check(pc is not None and JClass("java.lang.System").identityHashCode(pc) == JClass("java.lang.System").identityHashCode(pl),
            "FIX the saved holder carries the live Player component (identity)")
    # the world guard
    locks.set(1)
    S.forceSave(pl, ref, store)
    locks.set(0)
    fld(wc.getClass(), "isSavingPlayers").setBoolean(wc, False)
    S.forceSave(pl, ref, store)
    fld(wc.getClass(), "isSavingPlayers").setBoolean(wc, True)
    K.eq(int(SP.CALLS), 3, "FIX a save-locked world / a world that does not save players is skipped")
    C.FORCE_SAVE = False
    S.forceSave(pl, ref, store)
    C.FORCE_SAVE = True
    K.eq(int(SP.CALLS), 3, "FIX forceSaveAfterTrade=false: no forced save (markNeedsSave only)")
    # failures: counted in a row, a success resets, 5 in a row switch it off
    SP.THROW = 4
    for i in range(4):
        S.forceSave(pl, ref, store)
    K.check(int(S.SAVE_FAILS.get()) == 4 and not bool(S.SAVE_BROKEN), "FIX 4 failures in a row: counted, still on (SAVE_FAILS %d)" % int(S.SAVE_FAILS.get()))
    S.forceSave(pl, ref, store)
    K.check(int(S.SAVE_FAILS.get()) == 0 and not bool(S.SAVE_BROKEN) and int(S.SAVES.get()) == 4, "FIX a success resets the count")
    SP.THROW = 5
    for i in range(5):
        S.forceSave(pl, ref, store)
    K.check(bool(S.SAVE_BROKEN) and int(S.SAVE_FAILS.get()) == 5, "FIX 5 failures in a row switch the forced save off for the run")
    n = int(SP.CALLS)
    S.forceSave(pl, ref, store)
    K.eq(int(SP.CALLS), n, "FIX once off: markNeedsSave only (no more saveConfig calls)")
    K.check(int(S.LIVE.size()) == live0 and int(S.DIRTY.size()) == dirty0, "FIX forceSave (ok, skipped or failing) never touches the records (LIVE / DIRTY)")
    K.check(store.getComponent(ref, E["pt"]) is not None and ref.isValid(), "FIX the player entity is untouched (still in the store)")
    K.save()


if __name__ == "__main__":
    ph = [("tier", run_tier), ("static", run_static), ("saveold", run_save_old), ("savenew", run_save_new),
          ("hub", T10.run_hub), ("rb", T11.run_rb)]
    if os.path.isfile(BZ_JAR):
        ph.append(("mk", lambda out, jar, scratch, home: TB.run_mk(out, BZ_JAR, jar, scratch)))
    ph.append(("live", lambda out, jar, scratch, home: H.run_live(T10.S, out, jar, scratch, home)))
    HK.run(name="SkyyAuctions", version=VERSION, jar=JAR, old_jar=OLD_JAR, pkg=PKG, scratch=SCRATCH, expect=EXPECT, added=ADDED,
           phases=ph, script=__file__, live=(T10.LIVE, "Skyy_SkyyAuctions"))
