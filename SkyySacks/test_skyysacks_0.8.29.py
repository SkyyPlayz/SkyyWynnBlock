"""Harness for SkyySacks 0.8.29 (mob drops -> the Combat bag - tools/sacks_0_8_29_patch.py). Build first:
    python tools/sacks_0_8_29_patch.py && python SkyySacks/build_skyysacks_0.8.29.py

    python SkyySacks/test_skyysacks_0.8.29.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.28 -> 0.8.29: only SackDefs (~homeOf, ~<clinit> for the Combat 'holds' line), the plugin setup (version text), the
                 config kit version texts and RecipeCmp's tier table (tools/tier_tags.py re-bake, see EXPECT) differ; non-class files: manifest
  SRC   the 16 MOB029 ids: each is an item file in Assets.zip / its pack zip (read-only) AND is given by at least one NPC drop list
        (Server/Drops/NPCs/**) there; Skyy's four (Ingredient_Scraps, Goblin_Ear, Deco_Bone_Skulls, Ingredient_Spider_Silk) are in the list
  HOLD  (old jar, own child) homeOf for every Assets.zip item id + every pack NPC-drop id -> a file; then HOME (new jar): the answers differ
        for exactly the 16 ids (null -> Combat) - no id that had a bag moves; every MOB029 id's catOf / intake = Combat
  VOID  the 0.8.9 Void stand-ins on the real 0.8.29 classes: a player holding every MOB029 id + an old pool (bones Combat, hide Smithing,
        ore Mining, linen Combat): a Combat sweep takes every new id into the pool (inventory empty of them, conserved), the old stacks
        are untouched and keep their tabs (catTotal), then each old stack AND a new one withdraw back to the inventory (conserved)
  D     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.27's live phase) + 0.8.10's run_live10
  AA    engine-access audit
Exit code 1 on any failure.
"""
import os, sys, json, zipfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_argv = list(sys.argv)
_RC = HK.run_compare
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_27", os.path.join(HERE, "test_skyysacks_0.8.27.py"))
T0827 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0827)
sys.argv = _argv
HK.run_compare = _RC
T089 = T0827.T0810.T089

VERSION = "0.8.29"
OLD_VERSION = "0.8.28"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sack029", "h")))
PKG = "com.skyy.sacks."
GEN = os.path.join(HERE, "build_skyysacks_%s.py" % VERSION)
BETA = T0827.BETA
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")   # read-only (Python zipfile only)
MODS = os.path.join(B.USERDATA, "Mods")                                                              # read-only
PACKZ = {"souls": os.path.join(MODS, "Soulslike_Bosses-1_3_7.zip"), "dragon": os.path.join(MODS, "0.6.1_Aures_Dragon Nestkeeper_28_08_2026.zip")}
# RecipeCmp ~<clinit> = its /craft tier sort table re-baked from tools/tier_tags.py at build time (rows added after 0.8.28 was built:
# the 10-23 Legendary Dragon Egg commit, + any uncommitted rows in the working tree); built against the 0.8.28-era table it is identical
EXPECT = {"CfgFn": ["~m opExport"], "CfgRows": ["~m header"], "SkyySacksPlugin": ["~m setup"], "SackDefs": ["~m homeOf", "~<clinit>"],
          "RecipeCmp": ["~<clinit>"]}
if "--expect-dump" in sys.argv:
    EXPECT = {}
SKYY4 = ("Ingredient_Scraps", "Goblin_Ear", "Deco_Bone_Skulls", "Ingredient_Spider_Silk")


def mob029():
    """the MOB029 tuples, read from the generated script (Python literals)"""
    src = open(GEN, encoding="utf8").read()
    ns = {}
    a = src.index("MOB029_VANILLA = ")
    b = src.index("assert len(set(MOB029))", a)
    exec(src[a:b], ns)
    return list(ns["MOB029_VANILLA"]), list(ns["MOB029_PACK"])


def npc_drops(z):
    """item id -> NPC drop lists naming it (every ItemId under Server/Drops/NPCs/)"""
    out = {}

    def walk(o, f):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("ItemId", "Item") and isinstance(v, str):
                    out.setdefault(v, set()).add(f)
                walk(v, f)
        elif isinstance(o, list):
            for v in o:
                walk(v, f)
    for n in z.namelist():
        if n.startswith("Server/Drops/NPCs/") and n.endswith(".json"):
            try:
                walk(json.loads(z.read(n).decode("utf-8-sig")), n.rsplit("/", 1)[1][:-5])
            except Exception:
                pass
    return out


def item_ids(z):
    return set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def all_ids():
    """every vanilla item id + every pack NPC-drop id (the HOLD / HOME universe)"""
    ids = set(item_ids(zipfile.ZipFile(ASSETS)))
    for p in PACKZ.values():
        if os.path.isfile(p):
            z = zipfile.ZipFile(p)
            ids |= item_ids(z) | set(npc_drops(z))
    v, pk = mob029()
    return sorted(ids | set(v) | set(pk))


def run_src(out, jar, scratch, _home):
    K = HK.Child(out)
    v, pk = mob029()
    K.check(len(v) + len(pk) == 16 and all(i in v + pk for i in SKYY4), "SRC: 16 ids, Skyy's four (%s) among them" % ", ".join(SKYY4))
    az = zipfile.ZipFile(ASSETS)
    ai, ad = item_ids(az), npc_drops(az)
    for i in v:
        K.check(i in ai and i in ad, "SRC: vanilla %s is an Assets.zip item and an NPC drop (%s)" % (i, ", ".join(sorted(ad.get(i, ()))[:3])))
    pz = dict((k, zipfile.ZipFile(p)) for k, p in PACKZ.items() if os.path.isfile(p))
    K.check(len(pz) == 2, "SRC: both pack zips found (read-only): %s" % sorted(pz))
    for i in pk:
        hit = [(k, sorted(npc_drops(z).get(i, ()))[:2]) for k, z in pz.items() if i in item_ids(z) and i in npc_drops(z)]
        K.check(len(hit) == 1, "SRC: pack %s is an item + NPC drop of %s" % (i, hit))
    K.save()


def homes(jar, ids):
    from jpype import JClass, JString
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    D = JClass(PKG + "SackDefs")
    return dict((i, None if D.homeOf(JString(i)) is None else str(D.homeOf(JString(i)))) for i in ids)


def run_hold(out, jar, scratch, _home):
    K = HK.Child(out)
    ids = all_ids()
    h = homes(OLD_JAR, ids)
    json.dump(h, open(os.path.join(scratch, "home_old.json"), "w"), indent=0, sort_keys=True)
    K.check(len(h) > 3000, "HOLD: 0.8.28 homeOf for %d ids saved" % len(h))
    K.save()


def run_home(out, jar, scratch, _home):
    from jpype import JClass, JString
    K = HK.Child(out)
    old = json.load(open(os.path.join(scratch, "home_old.json")))
    new = homes(jar, sorted(old))
    v, pk = mob029()
    diff = dict((i, (old[i], new[i])) for i in old if old[i] != new[i])
    K.eq(sorted(diff), sorted(v + pk), "HOME: exactly the 16 MOB029 ids changed home (of %d ids)" % len(old))
    K.check(all(d == (None, "Combat") for d in diff.values()), "HOME: each of them null -> Combat (no bagged id moved): %s" % diff)
    D = JClass(PKG + "SackDefs")
    U = JClass("java.util.UUID").fromString("00000000-0000-0000-0000-0000000a0829")
    K.check(all(str(D.catOf(JString(i))) == "Combat" and str(D.intake(U, JString(i))) == "Combat" for i in v + pk),
            "HOME: catOf / intake (new pickups) = Combat for every MOB029 id")
    K.check("other mob drops" in str(D.HOLDS[4]), "HOME: the Combat holds line: %s" % D.HOLDS[4])
    K.eq([new.get(i) for i in ("Ingredient_Bone_Fragment", "Ingredient_Hide_Light", "Ore_Copper", "Ingredient_Fabric_Scrap_Linen",
                               "Food_Wildmeat_Raw", "Weapon_Sword_Bone", "Coffer_Key", "Deco_Trash", "Deco_Bone_Skulls_Wall")],
         ["Combat", "Smithing", "Mining", "Combat", "Farming", None, None, None, None], "HOME: spot checks (old homes kept, equipment / key / "
         "other skull decor not bagged)")
    K.save()


def cases29(K, L, scratch):
    from jpype import JString
    VS, Defs, Pool, SPage, Swp = L["VS"], L["Defs"], L["Pool"], L["SPage"], L["Swp"]
    fresh, write_pool, player, coll, pc, inv_counts, total, custom_item, drain = (L[n] for n in (
        "fresh", "write_pool", "player", "coll", "pc", "inv_counts", "total", "custom_item", "drain"))
    UUID = L["UUID"]
    base = os.path.join(scratch, "void29")
    v, pk = mob029()
    new = v + pk
    OLD = {"Ingredient_Bone_Fragment": 300, "Ingredient_Hide_Light": 120, "Ore_Copper": 80, "Ingredient_Fabric_Scrap_Linen": 50}
    for i_ in new + list(OLD):
        custom_item(i_, 100)
    drain()
    fresh(base)
    U = UUID.fromString("00000000-0000-0000-0000-0000000a0829")
    k = str(U)
    write_pool(os.path.join(base, "pools"), k, OLD)
    s = VS.st(k)
    s.first = 1
    coll(U, {"Combat": int(VS.totalFor(10, 4)), "Smithing": int(VS.totalFor(5, 5)), "Mining": int(VS.totalFor(5, 0))})
    before = dict((c, int(Pool.catTotal(k, c))) for c in ("Combat", "Smithing", "Mining"))
    K.eq(before, {"Combat": 350, "Smithing": 120, "Mining": 80}, "VOID: the old pool's tabs (bones + linen Combat, hide Smithing, ore Mining)")
    held = [(i_, 3 + n % 5) for n, i_ in enumerate(new)]
    p = player(storage=held[:16])
    b0 = total(inv_counts(p), pc(k))
    Swp.sweep(p, k, "Combat", True, None, VS.capsK(U, k), None)
    drain()
    after, inv = pc(k), inv_counts(p)
    miss = [i_ for i_, q in held if after.get(i_) != q or inv.get(i_)]
    K.check(not miss and total(inv, after) == b0, "VOID: a Combat sweep takes every MOB029 id (%d stacks) into the Void, conserved: missed %s"
            % (len(held), miss))
    K.check(all(after.get(i_) == q for i_, q in OLD.items()), "VOID: the old stacks are untouched: %s" % dict((i_, after.get(i_)) for i_ in OLD))
    K.eq(dict((c, int(Pool.catTotal(k, c))) for c in ("Smithing", "Mining")), {"Smithing": 120, "Mining": 80},
         "VOID: Smithing / Mining tabs unchanged")
    K.eq(int(Pool.catTotal(k, "Combat")), 350 + sum(q for _i, q in held), "VOID: Combat tab = old 350 + the new drops")
    b1 = total(inv_counts(p), pc(k))
    got = dict((i_, int(SPage.withdrawN(p, k, i_, q))) for i_, q in list(OLD.items()) + [("Ingredient_Scraps", 2), ("Goblin_Ear", 1)])
    drain()
    after, inv = pc(k), inv_counts(p)
    K.check(got == dict(list(OLD.items()) + [("Ingredient_Scraps", 2), ("Goblin_Ear", 1)]) and total(inv, after) == b1
            and all(i_ not in after for i_ in OLD) and inv.get("Ingredient_Hide_Light") == 120,
            "VOID: every old stored stack (Combat / Smithing / Mining) and two new ones withdraw in full, conserved: %s" % got)
    Pool.WRITER.shutdownNow()


def run_void29(out, jar, scratch, home):
    T089.void_cases = cases29
    T089.run_void(out, jar, scratch, home)


if __name__ == "__main__":
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, [],
           [("src", run_src), ("hold", run_hold), ("home", run_home), ("void29", run_void29),
            ("live", T0827.run_live27), ("live2", T0827.T0810.run_live10)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
