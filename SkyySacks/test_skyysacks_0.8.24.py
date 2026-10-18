"""Harness for SkyySacks 0.8.24 (every Void category gets the same starting space pd.base + fair upgrade costs on the 15-step tiers;
tools/sacks_0_8_24_patch.py). Build first:
    python tools/sacks_0_8_24_patch.py && python SkyySacks/build_skyysacks_0.8.24.py      (tools/tier_tags.py TT_VERSION 3)

    python SkyySacks/test_skyysacks_0.8.24.py [--dir <folder inside tools/dev/scratch/>] [--keep]

Phases (fresh child processes, tools/harness_kit.py):
  A     verify   every class loads + initialises with -Xverify:all
  C     compare  0.8.23 -> 0.8.24: exactly the planned members (EXPECT) + the new class SackMig0824
  CAP   (the 0.8.0 harness's Void stand-ins, through 0.8.9's run_void) space per category x level x rarity: all six categories at the same
        level and rarity get the SAME space = (1500 + level x 150) x the multiplier (capsK through the real level / collection path,
        Lv 1 .. 250, Normal .. Legendary, Omni x5); pd.base 0 = the 0.8.23 numbers exactly; "+225 space" per Unique level unchanged;
        Skyy's six live categories old -> new
  COST  the cost table (the 18 SackCfg defaults = the table below), the v3 tree tiers (Oak-tier = Oak + Birch, Beech-tier = Beech / Ash /
        Aspen / Apple, Maple-tier = Maple + Azure ...), a Foraging Rare upgrade paid with Ash (Beech-tier) + Birch (Oak-tier) + Azure
        (Maple-tier) from the Void and the inventory, refused one log short (the "Maple-tier logs" name), conserved
  ALLOY (Collections 0.2.28 hand-off) CraftPage.alloyOk on real CraftingRecipe objects: a plain SkyyAlloy row is never knowledge-locked;
        Alloy_Ench_* stays locked (with or without Collections' run-time KnowledgeRequired flag) until the known set holds its output;
        procQueue refuses it ("your collections unlock this smelt", nothing taken); HOME: the 6 Enchanted alloys -> Mining, old homes kept
  WORST (SkyyArmory 0.1.38 Soul Cage hand-off, Skyy "Use the worst one") mixed-rarity rolled Soul Orbs (stand-in items with a resource
        type): rank = plain / named -1, then rarity x 100000 + level; takeWorst takes plain, then Unique 40, then Rare 5 (not Rare 12 / Mythic),
        leaves item-id inputs to the engine, a short take puts every stack back (same objects), no rolled match = the engine's order;
        PAY: 0.8.23's plain copy counted 0 orbs, plainCopyFor counts the rolled ones (not a named stack), the payment takes the worst real
        orb + exactly 2 copper and records it for an exact refund, metaTouchedM allows only that slot, slotRestore puts it back as itself
  OVER  an existing category OVER its space keeps every item (the sweep takes in no more of it, nothing deleted); a category that was full
        at 0.8.23's space takes new items again under 0.8.24's
  MIG   the real SackMig089 then SackMig0824 (what setup runs) on a scratch mods folder: the NewBetaTest file (CRLF, commented defaults,
        0.8.9 marker already there): exactly the 15 commented cost lines refreshed, the 0.8.24 marker appended (CRLF), Properties
        identical, History = old bytes; a pre-0.8.9 file: 0.8.8 -> 0.8.9 -> 0.8.24 in one start; a synthetic LF file: live old defaults
        moved (spaces in the text too), a hand edit + a doubled line kept and named, one change-log line per moved value, SackCfg.reload
        reads them, start 2 changes nothing; Undo through the kit sticks; a fresh start writes both markers + pd.base; History blocked =
        untouched
  D     START TWICE on a scratch COPY of NewBetaTest's Skyy_SkyySacks (0.8.10's run_live10 on this jar)
  LIVE2 the same live copy: every profile's pd file + pool -> per category the 0.8.23 space vs the 0.8.24 space (never smaller), what is
        stored (kept), the pd files byte-identical after reading
  AA    engine-access audit
Not testable without the game (UNVERIFIED): the page in game, real gathering rates (the hours in the patch docstring are assumptions),
Zone 2 Lead veins in Skyy's already-generated world. Exit code 1 on any failure.
"""
import os, sys, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyybuild as B
import harness_kit as HK

_orig_compare = HK.run_compare
_argv = list(sys.argv)
_sp = importlib.util.spec_from_file_location("test_skyysacks_0_8_10", os.path.join(HERE, "test_skyysacks_0.8.10.py"))
T0810 = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(T0810)
T089 = T0810.T089
sys.argv = _argv
HK.run_compare = _orig_compare

VERSION = "0.8.24"
OLD_VERSION = "0.8.23"
JAR = os.path.abspath(HK.arg("--jar", os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)))
OLD_JAR = os.path.join(HERE, "SkyySacks-%s.jar" % OLD_VERSION)
SCRATCH = os.path.abspath(HK.arg("--dir", os.path.join(ROOT, "tools", "dev", "scratch", "sacks24", "h")))
PKG = "com.skyy.sacks."
BETA = os.path.join(B.USERDATA, "Saves", "NewBetaTest", "mods", "Skyy_SkyySacks")
EXPECT = {
    "SackCfg": ["+f PD_BASE", "~m pdKeys", "~m pdSig", "~m reload", "~<clinit>"],
    "VoidStore": ["~m capOf"],
    "SackDefs": ["~<clinit>", "~m enchCat"],   # LOGT_* = the 15 v3 tree tiers; enchCat + the 6 Enchanted alloys (Mining)
    "CraftPage": ["+m alloyOk", "~m procQueue", "~m buildProc",   # the alloy rows respect recipe knowledge
                  "+m gearRank", "+m wear", "+m worstSlots", "+m takeWorst", "~m craftOne"],   # worst first (Soul Cage)
    "SackBridge": ["+m gearFor", "+m plainCopyFor", "+m applyCopyM", "+m metaTouchedM", "~m plainCopy", "~m applyCopy",
                   "~m craftHave", "~m craftPay", "~m craftRefund"],
    "RecipeCmp": ["~<clinit>"],         # the /craft sort table re-baked from tier_tags TT_VERSION 3
    "SkyySacksPlugin": ["~m setup"],    # + SackMig0824.run, the ready line
    "CfgFn": ["~m opExport"], "CfgRows": ["~m header", "~<clinit>"], "CfgFile": ["~<clinit>"],
}
if "--expect-dump" in sys.argv:
    EXPECT = {}
ADDED = ["SackMig0824"]
CATS = ["Mining", "Foraging", "Farming", "Fishing", "Combat", "Smithing"]
MULT = [1.0, 1.5, 2.0, 3.0, 5.0]
RAR = ["Normal", "Unique", "Rare", "Legendary", "Omni"]
BASE, PER = 1500, 150
# THE COST TABLE (0.8.24 defaults; the patch docstring explains every number)
COST = {
    ("Mining", 1): "Rock_Stone_Cobble:400,Ore_Copper:250,Ore_Iron:100",
    ("Mining", 2): "Rock_Stone_Cobble:1000,Ore_Copper:600,Ore_Iron:500",
    ("Mining", 3): "Rock_Stone_Cobble:2000,Ore_Copper:750,Ore_Iron:750,Ore_Thorium:500,Ore_Lead_SkyWynn:300",
    ("Foraging", 1): "Wood_Oak_Trunk:400,Wood_Beech_Trunk:200,Ingredient_Fibre:250,Ingredient_Tree_Sap:100",
    ("Foraging", 2): "Wood_Oak_Trunk:1000,Wood_Beech_Trunk:1000,Wood_Maple_Trunk:500,Ingredient_Tree_Sap:250",
    ("Foraging", 3): "Wood_Beech_Trunk:2000,Wood_Maple_Trunk:1500,Wood_Dry_Trunk:1000,Wood_Bottletree_Trunk:750,Wood_Gumboab_Trunk:500,Ingredient_Tree_Sap:500",
    ("Farming", 1): "Plant_Crop_Wheat_Item:400,Plant_Crop_Lettuce_Item:200,Ingredient_Life_Essence:100",
    ("Farming", 2): "Plant_Crop_Wheat_Item:750,Plant_Crop_Lettuce_Item:500,Plant_Crop_Carrot_Item:500,Ingredient_Life_Essence:250",
    ("Farming", 3): "Plant_Crop_Wheat_Item:1500,Plant_Crop_Carrot_Item:1000,Plant_Crop_Corn_Item:750,Plant_Crop_Cauliflower_Item:500,Plant_Crop_Turnip_Item:500,Ingredient_Life_Essence:500",
    ("Fishing", 1): "Food_Fish_Raw:100",
    ("Fishing", 2): "Food_Fish_Raw:500,Fish_Bluegill_Item:50",
    ("Fishing", 3): "Food_Fish_Raw:1500,Fish_Catfish_Item:150,Fish_Minnow_Item:150",
    ("Combat", 1): "Ingredient_Bone_Fragment:200,Ingredient_Fabric_Scrap_Linen:50",
    ("Combat", 2): "Ingredient_Bone_Fragment:750,Ingredient_Fabric_Scrap_Linen:200,Ingredient_Sac_Venom:50,Ingredient_Chitin_Sturdy:50",
    ("Combat", 3): "Ingredient_Bone_Fragment:1500,Ingredient_Fabric_Scrap_Linen:400,Ingredient_Sac_Venom:150,Ingredient_Chitin_Sturdy:150,Ingredient_Fabric_Scrap_Shadoweave:100,Ingredient_Void_Essence:100",
    ("Smithing", 1): "Ingredient_Leather_Light:60,Ingredient_Bar_Copper:150",
    ("Smithing", 2): "Ingredient_Leather_Light:100,Ingredient_Leather_Medium:60,Ingredient_Bar_Copper:200,Ingredient_Bar_Iron:150,Ingredient_Bar_Bronze:100",
    ("Smithing", 3): "Ingredient_Leather_Medium:150,Ingredient_Leather_Heavy:100,Ingredient_Bar_Iron:300,Ingredient_Bar_Thorium:200,Ingredient_Bar_Lead_SkyWynn:150,Ingredient_Bar_Dusk_SkyWynn:100",
}
# 0.8.23's defaults (SackMig0824's old values; Fishing unchanged)
OLD = {
    ("Mining", 1): "Rock_Stone_Cobble:500,Ore_Copper:250,Ore_Iron:100",
    ("Mining", 2): "Rock_Stone_Cobble:2000,Ore_Copper:1000,Ore_Iron:1000,Ore_Thorium:250",
    ("Mining", 3): "Rock_Stone_Cobble:5000,Ore_Iron:2500,Ore_Thorium:1000,Ore_Cobalt:500,Ore_Adamantite:100",
    ("Foraging", 1): "Wood_Oak_Trunk:500,Ingredient_Fibre:500,Ingredient_Tree_Sap:100",
    ("Foraging", 2): "Wood_Oak_Trunk:2000,Wood_Maple_Trunk:1000,Wood_Gumboab_Trunk:500,Ingredient_Tree_Sap:250",
    ("Foraging", 3): "Wood_Oak_Trunk:5000,Wood_Maple_Trunk:2000,Wood_Gumboab_Trunk:1000,Wood_Redwood_Trunk:1000,Wood_Sallow_Trunk:500,Ingredient_Tree_Sap:500",
    ("Farming", 1): "Plant_Crop_Wheat_Item:500,Plant_Crop_Lettuce_Item:250,Ingredient_Life_Essence:100",
    ("Farming", 2): "Plant_Crop_Wheat_Item:2000,Plant_Crop_Carrot_Item:1000,Plant_Crop_Cauliflower_Item:500,Ingredient_Life_Essence:250",
    ("Farming", 3): "Plant_Crop_Wheat_Item:5000,Plant_Crop_Carrot_Item:2000,Plant_Crop_Pumpkin_Item:1000,Plant_Crop_Tomato_Item:1000,Plant_Crop_Cotton_Item:500,Ingredient_Life_Essence:500",
    ("Combat", 1): "Ingredient_Bone_Fragment:250,Ingredient_Fabric_Scrap_Linen:100",
    ("Combat", 2): "Ingredient_Bone_Fragment:1000,Ingredient_Fabric_Scrap_Linen:500,Ingredient_Sac_Venom:100,Ingredient_Chitin_Sturdy:100,Ingredient_Fabric_Scrap_Shadoweave:100",
    ("Combat", 3): "Ingredient_Bone_Fragment:2500,Ingredient_Fabric_Scrap_Linen:1000,Ingredient_Sac_Venom:250,Ingredient_Chitin_Sturdy:250,Ingredient_Void_Essence:100,Ingredient_Voidheart:10",
    ("Smithing", 1): "Ingredient_Leather_Light:200,Ingredient_Bar_Copper:100",
    ("Smithing", 2): "Ingredient_Leather_Light:750,Ingredient_Leather_Medium:500,Ingredient_Bar_Copper:250,Ingredient_Bar_Iron:100",
    ("Smithing", 3): "Ingredient_Leather_Light:2000,Ingredient_Leather_Medium:1000,Ingredient_Leather_Heavy:250,Ingredient_Bar_Iron:250,Ingredient_Bar_Thorium:100",
}
MIGKEYS = [("pd.cost.%s.%s" % (c, RAR[r]), OLD[(c, r)], COST[(c, r)]) for c in CATS for r in (1, 2, 3) if (c, r) in OLD]
assert len(MIGKEYS) == 15
MK = "skyysacks-0.8.24-void"
MK089 = "skyysacks-0.8.9-void"


def cap_py(lv, rank, base=BASE):
    import math
    return int(math.floor((base + lv * PER) * MULT[rank] + 1e-6))


# ======================================================================================================== CAP / COST / OVER (stand-ins)
def cases24(K, L, scratch):
    from jpype import JClass, JString
    VS, Defs, Cfg, Pool, Swp = L["VS"], L["Defs"], L["Cfg"], L["Pool"], L["Swp"]
    fresh, write_pool, player, coll, pc, inv_counts, total, custom_item, drain = (L[n] for n in (
        "fresh", "write_pool", "player", "coll", "pc", "inv_counts", "total", "custom_item", "drain"))
    UUID, IS = L["UUID"], L["IS"]
    base = os.path.join(scratch, "void24")
    K.eq([str(c) for c in Defs.CATS], CATS, "CAP the six categories")
    K.check(int(Cfg.PD_BASE) == BASE and int(Cfg.PD_PER_LEVEL) == PER, "CAP defaults: pd.base 1500, pd.perLevel 150")
    # capOf: the one formula - every level x rarity
    bad = [(lv, r) for lv in range(1, 251) for r in range(5) if int(VS.capOf(lv, r)) != cap_py(lv, r)]
    K.check(not bad, "CAP capOf = (1500 + level x 150) x the multiplier for Lv 1..250 x Normal..Omni: %s" % bad[:4])
    K.eq([int(VS.capOf(lv + 1, 1)) - int(VS.capOf(lv, 1)) for lv in (4, 23, 100)], [225, 225, 225], "CAP '+225 space' per Unique level unchanged")
    Cfg.PD_BASE = 0
    K.check(all(int(VS.capOf(lv, r)) == cap_py(lv, r, 0) for lv in range(1, 251) for r in range(5)), "CAP pd.base 0 = the 0.8.23 rule exactly")
    Cfg.PD_BASE = -5
    K.eq(int(VS.capOf(4, 1)), cap_py(4, 1, 0), "CAP a negative base (hand edit past the row's floor) counts as 0")
    Cfg.PD_BASE = BASE
    # all six categories through the REAL level path (collection totals -> level -> capsK) at the same level + rarity: the same space
    drain()
    fresh(base)
    U = UUID.fromString("00000000-0000-0000-0000-0000000a0824")
    k = str(U)
    write_pool(os.path.join(base, "pools"), k, {})
    s = VS.st(k)
    s.first = 1
    rows = []
    for lv in (1, 4, 7, 10, 23, 25, 50):
        coll(U, dict((c, int(VS.totalFor(lv, ci))) for ci, c in enumerate(CATS)))
        for r in range(4):
            for ci in range(6):
                s.rar[ci] = r
                s.best[ci] = 1
            caps = VS.capsK(U, k)
            got = [int(caps.get(c)) for c in CATS]
            if got != [cap_py(lv, 4 if r == 3 else r)] * 6:   # all six Legendary = Omni (pd.omniAuto) -> x5
                rows.append((lv, RAR[r], got))
    K.check(not rows, "CAP all six categories at the same level + rarity (through coll:fn:catTotal -> level -> capsK) hold the same space (all six Legendary = Omni x5): %s" % rows[:3])
    # Skyy's six live categories (NewBetaTest p3: best levels + rarities)
    live = {"Mining": (7, 0), "Foraging": (23, 1), "Farming": (4, 1), "Fishing": (3, 0), "Combat": (4, 0), "Smithing": (5, 0)}
    old = dict((c, cap_py(lv, r, 0)) for c, (lv, r) in live.items())
    new = dict((c, int(VS.capOf(lv, r))) for c, (lv, r) in live.items())
    K.eq([old["Foraging"], old["Farming"]], [5175, 900], "CAP Skyy's screenshots under 0.8.23: Foraging Lv 23 Unique 5,175, Farming Lv 4 Unique 900")
    K.eq(new, {"Mining": 2550, "Foraging": 7425, "Farming": 3150, "Fishing": 1950, "Combat": 2100, "Smithing": 2250},
         "CAP Skyy's six categories under 0.8.24 (old %s)" % old)
    for c in CATS:
        s.rar[CATS.index(c)] = 0
    # ---- COST: the defaults + the v3 tree tiers
    for (c, r), v in COST.items():
        K.eq(str(getattr(Cfg, "PD_COST_%s_%s" % (c.upper(), RAR[r].upper()))), v, "COST default %s -> %s" % (c, RAR[r]))
    mem = lambda i: sorted(str(x) for x in Defs.members(JString(i)))
    K.eq([mem("Wood_Oak_Trunk"), mem("Wood_Beech_Trunk"), mem("Wood_Maple_Trunk"), mem("Wood_Gumboab_Trunk")],
         [["Wood_Birch_Trunk", "Wood_Oak_Trunk"], ["Wood_Apple_Trunk", "Wood_Ash_Trunk", "Wood_Aspen_Trunk", "Wood_Beech_Trunk"],
          ["Wood_Azure_Trunk", "Wood_Maple_Trunk"], ["Wood_Gumboab_Trunk", "Wood_Palo_Trunk"]],
         "COST a log line counts its v3 tree tier (Oak-tier = Oak + Birch; Ash is Beech-tier now)")
    K.eq([str(Defs.unitName(JString(i))) for i in ("Wood_Oak_Trunk", "Wood_Ash_Trunk", "Wood_Azure_Trunk", "Wood_Crystal_Trunk")],
         ["Oak-tier logs", "Beech-tier logs", "Maple-tier logs", "Crystal-tier logs"], "COST the tier names")
    K.eq(len(list(Defs.LOGT_IDS)), 34, "COST all 34 vanilla trunks are in a tier")
    # a Foraging Rare upgrade (from Unique): Oak-tier 1000 + Beech-tier 1000 + Maple-tier 500 + Tree Sap 250
    ids = ["Wood_Oak_Trunk", "Wood_Birch_Trunk", "Wood_Ash_Trunk", "Wood_Beech_Trunk", "Wood_Maple_Trunk", "Wood_Azure_Trunk", "Ingredient_Tree_Sap"]
    for i_ in ids:
        custom_item(i_, 100)
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {"Wood_Oak_Trunk": 860, "Wood_Ash_Trunk": 1851, "Wood_Maple_Trunk": 14, "Wood_Azure_Trunk": 32,
                                                 "Ingredient_Tree_Sap": 647})
    s = VS.st(k)
    s.first = 1
    s.rar[1] = 1
    p = player(storage=[("Wood_Birch_Trunk", 100), ("Wood_Birch_Trunk", 40), ("Wood_Maple_Trunk", 100), ("Wood_Maple_Trunk", 100)])
    b0 = total(inv_counts(p), pc(k))
    r_ = str(VS.upgrade(p, U, k, 1, 1))
    K.check(r_.endswith("(246 / 500)") and "Maple" in r_ and int(s.rar[1]) == 1 and total(inv_counts(p), pc(k)) == b0,
            "COST Skyy's Foraging (860 Oak + 1,851 Ash + 46 Maple-tier in the Void, 140 Birch + 200 Maple held): refused at Maple-tier "
            "246 / 500, nothing taken: %s" % r_)
    p.getInventory().getHotbar().addItemStack(IS("Wood_Azure_Trunk", 100))
    p.getInventory().getHotbar().addItemStack(IS("Wood_Azure_Trunk", 100))
    p.getInventory().getHotbar().addItemStack(IS("Wood_Maple_Trunk", 60))
    b1 = total(inv_counts(p), pc(k))
    r_ = str(VS.upgrade(p, U, k, 1, 1))
    drain()
    after = total(inv_counts(p), pc(k))
    taken = dict((i_, b1.get(i_, 0) - after.get(i_, 0)) for i_ in set(b1) | set(after))
    K.check(r_.startswith("+Foraging is now Rare") and int(s.rar[1]) == 2
            and taken.get("Wood_Oak_Trunk", 0) + taken.get("Wood_Birch_Trunk", 0) == 1000
            and taken.get("Wood_Ash_Trunk", 0) == 1000 and taken.get("Wood_Maple_Trunk", 0) + taken.get("Wood_Azure_Trunk", 0) == 500
            and taken.get("Ingredient_Tree_Sap", 0) == 250 and sum(taken.values()) == 2750 and all(v >= 0 for v in taken.values()),
            "COST Foraging Rare paid exactly: 1,000 Oak-tier (Oak / Birch), 1,000 Beech-tier (Ash), 500 Maple-tier (Maple / Azure), 250 sap: %s / %s"
            % (r_, dict((a, b) for a, b in taken.items() if b)))
    K.eq(int(VS.capOf(23, 2)), 9900, "COST Foraging Lv 23 Rare holds (1500 + 3450) x 2 = 9,900")
    # ---- OVER: an existing category over its space keeps everything; a full-at-0.8.23 category takes items again
    for i_ in ("Ingredient_Life_Essence", "Plant_Crop_Wheat_Item", "Ingredient_Bone_Fragment"):
        custom_item(i_, 100)
    drain()
    fresh(base)
    write_pool(os.path.join(base, "pools"), k, {"Ingredient_Life_Essence": 539, "Plant_Crop_Wheat_Item": 361, "Ingredient_Bone_Fragment": 5000})
    s = VS.st(k)
    s.first = 1
    s.rar[2] = 1          # Farming Unique
    coll(U, {"Farming": int(VS.totalFor(4, 2)), "Combat": int(VS.totalFor(4, 4))})
    caps = VS.capsK(U, k)
    K.eq([int(caps.get("Farming")), int(caps.get("Combat"))], [3150, 2100], "OVER Farming Lv 4 Unique 3,150 (was 900), Combat Lv 4 Normal 2,100")
    p = player(storage=[("Plant_Crop_Wheat_Item", 100), ("Ingredient_Bone_Fragment", 50)])
    b0 = total(inv_counts(p), pc(k))
    Swp.sweep(p, k, "Farming", True, None, caps, None)
    Swp.sweep(p, k, "Combat", True, None, VS.capsK(U, k), None)
    drain()
    after = pc(k)
    K.check(total(inv_counts(p), after) == b0 and after.get("Plant_Crop_Wheat_Item") == 461 and after.get("Ingredient_Bone_Fragment") == 5000
            and inv_counts(p).get("Ingredient_Bone_Fragment") == 50 and after.get("Ingredient_Life_Essence") == 539,
            "OVER Farming (900 stored, full at 0.8.23's 900) takes the 100 wheat now; Combat over its space (5,000 / 2,100) keeps every bone, "
            "the 50 held bones stay in the inventory; conserved: %s" % after)
    Cfg.PD_BASE = 0
    K.eq(int(VS.capsK(U, k).get("Farming")), 900, "OVER rollback view (pd.base 0): Farming back to 900 - the 1,000 stored stay (nothing deleted)")
    K.eq(pc(k).get("Plant_Crop_Wheat_Item"), 461, "OVER the stored wheat is untouched by a lower space")
    Cfg.PD_BASE = BASE
    worst_cases(K, L)
    Pool.WRITER.shutdownNow()


def worst_cases(K, L):
    """WORST FIRST (Skyy popup "Use the worst one"): mixed-rarity rolled Soul Orbs taken by a resource-type input"""
    from jpype import JClass, JString, JArray, JInt, JFloat, JShort
    custom_item, jfield = L["custom_item"], L["jfield"]
    IS = L["IS"]
    CP, SB = JClass(PKG + "CraftPage"), JClass(PKG + "SackBridge")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    IRT = JClass("com.hypixel.hytale.protocol.ItemResourceType")
    CRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    SIC = JClass("com.hypixel.hytale.server.core.inventory.container.SimpleItemContainer")
    CIC = JClass("com.hypixel.hytale.server.core.inventory.container.CombinedItemContainer")
    IC = JClass("com.hypixel.hytale.server.core.inventory.container.ItemContainer")
    BD, BS, BI = JClass("org.bson.BsonDocument"), JClass("org.bson.BsonString"), JClass("org.bson.BsonInt32")
    ItemC = JClass("com.hypixel.hytale.server.core.asset.type.item.config.Item")
    RT = "SkyyArmory_Any_SoulOrb"
    ORB, ORB2, BAR = "Skyy_Test_SoulOrb", "Skyy_Test_SoulOrb_Iron", "Ingredient_Bar_Copper"
    for i_ in (ORB, ORB2):
        it_ = custom_item(i_, 1)
        jfield(ItemC.class_, "resourceTypes").set(it_, JArray(IRT)([IRT(JString(RT), JInt(1))]))
    custom_item(BAR, 100)
    K.eq([int(CP.rtUnits(JString(ORB), JString(RT))), int(CP.rtUnits(JString(BAR), JString(RT)))], [1, 0],
         "WORST the stand-in orbs carry the resource type (the engine's getMatchingResourceType)")

    def orb(r, lv, iid=ORB):
        s = IS(JString(iid), JInt(1))
        if r is None:
            return s
        d = BD()
        d.put(JString("r"), BS(JString(r)))
        d.put(JString("lvl"), BI(JInt(lv)))
        return s.withMetadata(JString("SkyyGear"), d)

    def named(iid=ORB):
        d = BD()
        d.put(JString("name"), BS(JString("Bob")))
        return IS(JString(iid), JInt(1)).withMetadata(JString("Custom"), d)

    def cont(stacks):
        c = SIC(JShort(8))
        for i, s in enumerate(stacks):
            if s is not None:
                c.setItemStackForSlot(JShort(i), s)
        return c

    def desc(c):
        out = []
        for i in range(int(c.getCapacity())):
            s = c.getItemStack(JShort(i))
            if s is None or s.isEmpty():
                out.append(None)
                continue
            w = int(CP.wear(s))
            out.append("%s:%d" % (str(s.getItemId())[-4:], w))
        return out

    def res(q):
        return MQ(None, JString(RT), None, JInt(q), None)
    K.eq([int(CP.wear(orb(None, 0))), int(CP.wear(orb("unique", 40))), int(CP.wear(orb("rare", 5))), int(CP.wear(orb("mythic", 30))),
          int(CP.wear(orb("set", 1))), int(CP.wear(orb("Legendary", 7))), int(CP.wear(named()))],
         [-1, 100040, 200005, 700030, 300001, 400007, -1], "WORST ranks: plain / named = -1 (lowest), then rarity x 100000 + level")
    mixed = [orb("mythic", 30), orb("rare", 12), orb(None, 0), orb("rare", 5), orb("unique", 40), IS(JString(BAR), JInt(5))]
    c = cont(mixed)
    K.eq([int(x) for x in CP.worstSlots(c, res(1))], [2, 4, 3, 1, 0], "WORST order: plain, Unique 40, Rare 5, Rare 12, Mythic 30 (copper is no orb)")
    JAL = JClass("java.util.ArrayList")

    def J(xs=()):
        a = JAL()
        for x in xs:
            a.add(x)
        return a
    gs = lambda c_, i: c_.getItemStack(JShort(i))
    l = J()
    l.add(MQ(JString(BAR), None, None, JInt(2), None))
    l.add(res(2))
    keep = [gs(c, i) for i in range(8)]
    rest = CP.takeWorst(c, l)
    K.check(rest is not None and rest.size() == 1 and str(rest.get(0).getItemId()) == BAR and desc(c)[2] is None and desc(c)[4] is None
            and gs(c, 0) == keep[0] and gs(c, 1) == keep[1] and gs(c, 3) == keep[3] and int(gs(c, 5).getQuantity()) == 5,
            "WORST 2 orbs: the plain one and the Unique go, Mythic / both Rares untouched (same objects); copper left for the engine: %s" % desc(c))
    rest = CP.takeWorst(c, J([res(1)]))
    K.check(rest is not None and rest.size() == 0 and desc(c)[3] is None and gs(c, 1) == keep[1] and gs(c, 0) == keep[0],
            "WORST the next one is the Rare Lv 5 (not the Lv 12, not the Mythic): %s" % desc(c))
    before = [gs(c, i) for i in range(8)]
    K.check(CP.takeWorst(c, J([res(3)])) is None and [gs(c, i) for i in range(8)] == before,
            "WORST 3 asked, 2 left: refused and every stack back as it was (same objects) - nothing taken")
    c2 = cont([IS(JString(ORB), JInt(1)), IS(JString(ORB), JInt(1))])
    rest = CP.takeWorst(c2, J([res(1)]))
    K.check(CP.worstSlots(c2, res(1)) is None and rest.size() == 1 and desc(c2)[:2] == ["lOrb:-1", "lOrb:-1"],
            "WORST no rolled orb at all: the input goes to the engine unchanged (its own order, as before)")
    c3 = cont([orb("legendary", 9, ORB2), orb("normal", 50), orb("normal", 3, ORB2)])
    rest = CP.takeWorst(c3, J([res(1)]))
    K.check(rest.size() == 0 and desc(c3)[2] is None and desc(c3)[0] is not None and desc(c3)[1] is not None,
            "WORST two orb kinds of one type: Normal Lv 3 before Normal Lv 50 before Legendary: %s" % desc(c3))
    # ---- sacks:fn:craftHave / craftPay pieces: the copy holds the rolled orbs a resource input matches; worst first; exact refund record
    po = MQ(JString("Skyy_Test_SoulCage"), None, None, JInt(1), None)
    rec = CRc(JArray(MQ)([res(1), MQ(JString(BAR), None, None, JInt(2), None)]), po, JArray(MQ)([po]), JInt(1), JArray(BR)(0), JFloat(0.0), False, JInt(0))
    jfield(CRc.class_, "id").set(rec, JString("Skyy_Test_Cage"))
    hot = cont([orb("rare", 20), named(), orb("unique", 3), IS(JString(BAR), JInt(4))])
    back = cont([orb("mythic", 50)])
    cs = JArray(IC)([back, hot])
    snap = SB.slotSnap(cs)
    old = SB.plainCopy(cs)
    K.eq(int(old[0].countRemovableMaterial(res(1))), 0, "PAY 0.8.23's plain copy: the rolled orbs are skipped (0 / 1 - the bug)")
    pcp = SB.plainCopyFor(cs, rec)
    cp = pcp[0]
    K.eq(int(cp.countRemovableMaterial(res(1))), 3, "PAY plainCopyFor: the 3 rolled orbs count for the resource input (craftHave shows 1 / 1); the named one stays out")
    K.check(bool(SB.gearFor(rec, orb("rare", 1))) and not bool(SB.gearFor(rec, named())) and not bool(SB.gearFor(None, orb("rare", 1))),
            "PAY gearFor: a rolled orb yes, a named (non-gear) stack no, no recipe no")
    view = CIC(JArray(IC)([cp]))
    ins = J([res(1), MQ(JString(BAR), None, None, JInt(2), None)])
    rest = CP.takeWorst(view, ins)
    view.removeMaterials(rest)
    mo = J()
    r_ = SB.applyCopyM(pcp, cs, mo)
    K.check(r_ is None and mo.size() == 1 and str(mo.get(0).getItemId()) == ORB and int(CP.wear(mo.get(0))) == 100003
            and (gs(hot, 2) is None or gs(hot, 2).isEmpty()),
            "PAY the worst orb (Unique Lv 3) leaves the REAL hotbar; it is recorded for an exact refund: %s / %s" % (r_, [str(x) for x in mo]))
    K.check(gs(hot, 0) == snap.get(1)[0] and gs(back, 0) == snap.get(0)[0] and gs(hot, 1) == snap.get(1)[1]
            and int(gs(hot, 3).getQuantity()) == 2,
            "PAY exactly one orb + 2 copper taken: the Rare 20, the Mythic 50 and the named orb are untouched")
    K.check(not bool(SB.metaTouchedM(cs, snap, pcp)) and bool(SB.metaTouched(cs, snap)),
            "PAY metaTouchedM allows the paid rolled slot (the old metaTouched would refuse the whole payment)")
    SB.slotRestore(cs, snap)
    K.check(gs(hot, 2) == snap.get(1)[2] and int(gs(hot, 3).getQuantity()) == 4, "PAY a refused payment's slotRestore puts the orb back as itself")


def run_void24(out, jar, scratch, home):
    T089.void_cases = cases24
    T089.run_void(out, jar, scratch, home)


# ======================================================================================================== MIG
def run_mig(out, jar, scratch, home):
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    from jpype import JClass, JString
    Paths = JClass("java.nio.file.Paths")
    Pool, Cfg, M89, Mig = JClass(PKG + "SackPool"), JClass(PKG + "SackCfg"), JClass(PKG + "SackMig089"), JClass(PKG + "SackMig0824")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    base = os.path.join(scratch, "mig")
    shutil.rmtree(base, ignore_errors=True)
    nfile = [0]

    def world(text_bytes):
        nfile[0] += 1
        d = os.path.join(base, "w%d" % nfile[0], "mods", "Skyy_SkyySacks")
        os.makedirs(d)
        f = os.path.join(d, "config.properties")
        if text_bytes is not None:
            open(f, "wb").write(text_bytes)
        return d, f

    def start(f):
        """what setup() runs: SackMig089 then SackMig0824"""
        a = str(M89.run(Paths.get(f)))
        b = str(Mig.run(Paths.get(f)))
        return a, b

    def props(b):
        P_ = JClass("java.util.Properties")()
        P_.load(JClass("java.io.ByteArrayInputStream")(b))
        return dict((str(k), str(P_.getProperty(k))) for k in P_.stringPropertyNames())

    def hist(d):
        hd = os.path.join(d, "config-history")
        return sorted(os.path.join(hd, n) for n in os.listdir(hd) if "config.properties." in n and n.endswith(".bak")) if os.path.isdir(hd) else []

    def chlog(d):
        f = os.path.join(d, "config-changes.log")
        return [l.split("\t") for l in open(f, encoding="utf8").read().splitlines()] if os.path.isfile(f) else []

    def reload_cfg(f):
        Cfg.FILE = Paths.get(f)
        Cfg.MTIME = -1
        Cfg.reload()

    # ---- the NewBetaTest file (CRLF, commented defaults, the 0.8.9 marker already there)
    bcfg = os.path.join(BETA, "config.properties")
    if os.path.isfile(bcfg):
        b0 = open(bcfg, "rb").read()
        d, f = world(b0)
        r89, r = start(f)
        b1 = open(f, "rb").read()
        l0, l1 = b0.split(b"\r\n"), b1.split(b"\r\n")
        diff = [(a, c) for a, c in zip(l0[:-1], l1) if a != c]
        want = [(("#%s=%s" % (k_, o)).encode(), ("#%s=%s" % (k_, n)).encode()) for k_, o, n in MIGKEYS]
        K.check(r89 == "" and sorted(diff) == sorted(want), "MIG beta: 0.8.9 does nothing (marker); exactly the 15 commented cost lines get the "
                "0.8.24 default: %d / %s" % (len(diff), [x[1][:40] for x in diff][:3]))
        K.check(len(l1) == len(l0) + 1 and l1[-2].startswith(b"# ---------- SkyySacks 0.8.24 (marker " + MK.encode()) and l1[-1] == b""
                and b1.count(b"\n") == b1.count(b"\r\n"), "MIG beta: the 0.8.24 marker line appended with the file's CRLF ending")
        K.check(props(b0) == props(b1), "MIG beta: the Properties are identical (only comments changed)")
        h = hist(d)
        K.check(len(h) == 1 and open(h[0], "rb").read() == b0, "MIG beta: config-history holds the old bytes")
        K.check(chlog(d) == [] and "no setting line held the old default" in r and "15 commented default line(s) refreshed" in r,
                "MIG beta: no change-log line; INFO: %s" % r[:200])
        K.check(start(f) == ("", "") and open(f, "rb").read() == b1 and len(hist(d)) == 1, "MIG beta: start 2 changes nothing (markers)")
    else:
        K.notes.append("MIG: no NewBetaTest config.properties - the beta case skipped")
    # ---- a pre-0.8.9 file (live 0.8.8 Smithing default, commented 0.8.8 Combat default, live Mining default): 0.8.8 -> 0.8.9 -> 0.8.24
    s88 = T089.OLDNUM["PD_COST_SMITHING_UNIQUE"]
    c88 = T089.OLDNUM["PD_COST_COMBAT_UNIQUE"]
    txt = "pd.perLevel=100\npd.cost.Smithing.Unique=%s\n#pd.cost.Combat.Unique=%s\npd.cost.Mining.Rare=%s\n" % (s88, c88, OLD[("Mining", 2)])
    d, f = world(txt.encode())
    r89, r = start(f)
    t1 = open(f, "rb").read().decode("latin-1")
    K.check(t1.startswith("pd.perLevel=150\npd.cost.Smithing.Unique=%s\n#pd.cost.Combat.Unique=%s\npd.cost.Mining.Rare=%s\n"
                          % (COST[("Smithing", 1)], COST[("Combat", 1)], COST[("Mining", 2)]))
            and MK089 in t1 and MK in t1 and t1.index(MK089) < t1.index(MK),
            "MIG pre-0.8.9: one start moves 0.8.8 -> 0.8.9 -> 0.8.24 (perLevel 150, Smithing / Mining live, Combat commented), both markers: %r" % t1[:300])
    cl = chlog(d)
    K.check(sorted((x[1], x[4]) for x in cl) == sorted([("SkyySacks 0.8.9", "pd.perLevel"), ("SkyySacks 0.8.9", "pd.cost.Smithing.Unique"),
                                                         ("SkyySacks 0.8.24", "pd.cost.Smithing.Unique"), ("SkyySacks 0.8.24", "pd.cost.Mining.Rare")]),
            "MIG pre-0.8.9: one change-log line per moved value per step: %s" % [(x[1], x[4]) for x in cl])
    K.check(len(hist(d)) == 2, "MIG pre-0.8.9: a History copy before each step (%d)" % len(hist(d)))
    # ---- synthetic: LF file, one CRLF line, no final newline; live old defaults, a hand edit, a doubled line
    k_fu, o_fu, n_fu = [m for m in MIGKEYS if m[0] == "pd.cost.Foraging.Unique"][0]
    k_fr, o_fr, n_fr = [m for m in MIGKEYS if m[0] == "pd.cost.Foraging.Rare"][0]
    k_mu, o_mu, n_mu = [m for m in MIGKEYS if m[0] == "pd.cost.Mining.Unique"][0]
    k_cr, o_cr, n_cr = [m for m in MIGKEYS if m[0] == "pd.cost.Combat.Rare"][0]
    k_fl, o_fl, n_fl = [m for m in MIGKEYS if m[0] == "pd.cost.Farming.Legendary"][0]
    spaced = o_fu.replace(",", " , ").replace(":", ": ")
    txt = ("# " + MK089 + "\ncraftSearch=true\n%s = %s\r\n%s=%s\n%s=Wood_Oak_Trunk:5\n#%s=%s\n%s=%s\n%s=%s\npd.cost.Fishing.Unique=Food_Fish_Raw:100"
           % (k_fu, spaced, k_mu, o_mu, k_fr, k_fl, o_fl, k_cr, o_cr, k_cr, o_cr))
    b0 = txt.encode("latin-1")
    d, f = world(b0)
    r89, r = start(f)
    t1 = open(f, "rb").read().decode("latin-1")
    want = ("# " + MK089 + "\ncraftSearch=true\n%s = %s\r\n%s=%s\n%s=Wood_Oak_Trunk:5\n#%s=%s\n%s=%s\n%s=%s\npd.cost.Fishing.Unique=Food_Fish_Raw:100\n"
            % (k_fu, n_fu, k_mu, n_mu, k_fr, k_fl, n_fl, k_cr, o_cr, k_cr, o_cr))
    K.check(r89 == "" and t1.startswith(want) and t1[len(want):].startswith("# ---------- SkyySacks 0.8.24") and t1.endswith("\n") and t1.count("\r\n") == 1,
            "MIG syn: the spaced Foraging.Unique (its CRLF kept) and Mining.Unique moved, the commented Farming.Legendary refreshed, the "
            "hand-edited Foraging.Rare and the DOUBLED Combat.Rare kept, Fishing untouched, final newline added, marker appended: %r" % t1[:300])
    K.check(open(hist(d)[0], "rb").read() == b0 and len(hist(d)) == 1, "MIG syn: the History copy = the old bytes")
    cl = chlog(d)
    K.check(sorted((x[4], x[5], x[6]) for x in cl) == sorted([(k_fu, spaced.strip(), n_fu), (k_mu, o_mu, n_mu)])
            and all(x[1] == "SkyySacks 0.8.24" and x[3] == "update" and x[7] == "ok" for x in cl),
            "MIG syn: one change-log line per moved value: %s" % [x[4:7] for x in cl])
    K.check("%s=Wood_Oak_Trunk:5 kept - an admin changed it" % k_fr in r and k_cr + "=" in r and "doubled" in r,
            "MIG syn: the INFO names the kept hand edit and the doubled line: %s" % r.replace("\n", " | ")[:300])
    reload_cfg(f)
    K.check(str(Cfg.PD_COST_FORAGING_UNIQUE) == n_fu and str(Cfg.PD_COST_MINING_UNIQUE) == n_mu and str(Cfg.PD_COST_FORAGING_RARE) == "Wood_Oak_Trunk:5"
            and str(Cfg.PD_COST_FARMING_LEGENDARY) == n_fl and int(Cfg.PD_BASE) == BASE,
            "MIG syn: SackCfg.reload reads the moved values, the hand edit, the defaults (pd.base 1500 with no line)")
    K.check(start(f) == ("", "") and open(f, "rb").read().decode("latin-1") == t1, "MIG syn: start 2 changes nothing (markers)")
    # ---- Undo through the kit (Server Setup -> Changes -> Undo = a console set of the old value), then start 3
    CP, Fn = JClass(PKG + "CfgPub"), JClass(PKG + "CfgFn")
    CP.start(Paths.get(os.path.dirname(d)), Pool.LOG)
    ru = str(Fn.cmdSetConsole(JString(k_mu), JString(o_mu)))
    rb = str(Fn.cmdSetConsole(JString("pd.base"), JString("0")))
    CP.shutdown()
    t2 = open(f, "rb").read().decode("latin-1")
    K.check(str(Cfg.PD_COST_MINING_UNIQUE) == o_mu and ("%s=%s" % (k_mu, o_mu)) in t2 and int(Cfg.PD_BASE) == 0 and "pd.base=0" in t2,
            "MIG undo: the kit sets the old Mining cost back and pd.base 0 (fields + file lines): %s | %s" % (ru, rb))
    K.check(start(f) == ("", "") and open(f, "rb").read().decode("latin-1") == t2, "MIG undo: start 3 keeps the undone values (markers)")
    # ---- a fresh start: no file -> SackCfg.reload writes the 0.8.24 default (both markers, pd.base, the new costs)
    d, f = world(None)
    K.check(start(f) == ("", "") and not os.path.exists(f), "MIG fresh: no file -> nothing done")
    reload_cfg(f)
    t3 = open(f, "rb").read()
    K.check(MK.encode() in t3 and MK089.encode() in t3 and b"#pd.base=1500" in t3 and all(("#%s=%s" % (k_, n)).encode() in t3 for k_, o, n in MIGKEYS)
            and int(Cfg.PD_BASE) == BASE, "MIG fresh: the default file carries both markers, #pd.base=1500 and the 15 new costs")
    K.check(start(f) == ("", "") and open(f, "rb").read() == t3 and hist(d) == [], "MIG fresh: the updates find the markers - nothing written")
    # ---- History cannot be written: untouched; the next start updates it
    d, f = world(("# %s\n%s=%s\n" % (MK089, k_mu, o_mu)).encode())
    open(os.path.join(d, "config-history"), "wb").write(b"not a folder")
    b0 = open(f, "rb").read()
    K.check(start(f) == ("", "") and open(f, "rb").read() == b0, "MIG nohist: config-history cannot be made -> the file is untouched")
    os.remove(os.path.join(d, "config-history"))
    K.check(start(f)[1] != "" and ("%s=%s" % (k_mu, n_mu)).encode() in open(f, "rb").read(), "MIG nohist: the next start updates it")
    K.save()


# ======================================================================================================== ALLOY (Collections 0.2.28 hand-off)
def run_alloy24(out, jar, scratch, home):
    """the Furnace tab's SkyyAlloy rows respect recipe knowledge (CraftPage.alloyOk -> KnowSync.allowedOut); procQueue refuses a locked
    Enchanted smelt; the 6 Enchanted alloys home in Mining"""
    from jpype import JClass, JString, JArray, JInt, JFloat
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    CRc = JClass("com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe")
    MQ = JClass("com.hypixel.hytale.server.core.inventory.MaterialQuantity")
    BR = JClass("com.hypixel.hytale.protocol.BenchRequirement")
    CP, Defs, Pool, PS = JClass(PKG + "CraftPage"), JClass(PKG + "SackDefs"), JClass(PKG + "SackPool"), JClass(PKG + "ProcStore")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    HS = JClass("java.util.HashSet")
    Paths = JClass("java.nio.file.Paths")
    d = os.path.join(scratch, "alloy", "processing")
    os.makedirs(d, exist_ok=True)
    PS.DIR = Paths.get(d)

    def field(name):
        f = CRc.class_.getDeclaredField(name)
        f.setAccessible(True)
        return f

    def recipe(rid, out_, ins, bench, kr):
        brs = JArray(BR)(0)
        if bench:
            b_ = BR()
            b_.id = JString(bench)
            b_.requiredTierLevel = 1
            brs = JArray(BR)([b_])
        mi = JArray(MQ)([MQ(JString(i), None, None, JInt(1), None) for i in ins])
        po = MQ(JString(out_), None, None, JInt(2), None)
        r = CRc(mi, po, JArray(MQ)([po]), JInt(2), brs, JFloat(24.0), bool(kr), JInt(0))
        field("id").set(r, JString(rid))
        return r

    def known(*ids):
        s = HS()
        for i in ids:
            s.add(JString(i))
        return s
    plain = recipe("Alloy_Bronze", "Ingredient_Bar_Bronze", ["Ingredient_Bar_Copper", "Ingredient_Bar_Iron"], "SkyyAlloy", False)
    ench = recipe("Alloy_Ench_Bronze", "Skyy_Ench_Bronze", ["Skyy_Ench_Copper", "Skyy_Ench_Iron"], "SkyyAlloy", False)       # as the file ships
    enchk = recipe("Alloy_Ench_Dusk", "Skyy_Ench_Dusk", ["Skyy_Ench_Thorium", "Skyy_Ench_Lead"], "SkyyAlloy", True)          # Collections' flag set
    other = recipe("Skyy_Test_NotAlloy", "Ingredient_Bar_Iron", ["Ore_Iron"], "Furnace", True)
    K.check(bool(CP.alloyOk(plain, known(), HS())) and bool(CP.alloyOk(plain, None, None)),
            "ALLOY a plain alloy row (no knowledge) is not locked by knowledge (the Furnace Charm gate alone, unchanged)")
    K.check(not bool(CP.alloyOk(ench, known(), HS())) and not bool(CP.alloyOk(ench, None, None)),
            "ALLOY Alloy_Ench_Bronze (file without KnowledgeRequired, i.e. no SkyyCollections flag) stays LOCKED for a player who does not know it")
    K.check(bool(CP.alloyOk(ench, known("Skyy_Ench_Bronze"), HS())), "ALLOY ... unlocked once the known set holds Skyy_Ench_Bronze (Collections granted it)")
    K.check(not bool(CP.alloyOk(enchk, known("Skyy_Ench_Bronze"), HS())) and bool(CP.alloyOk(enchk, known("Skyy_Ench_Dusk"), HS())),
            "ALLOY a KnowledgeRequired Enchanted Dusk smelt: locked with only Bronze known, open with Dusk known")
    K.check(bool(CP.alloyOk(other, known(), HS())), "ALLOY a non-alloy Furnace recipe is not this rule's business (true)")
    # procQueue refuses the locked Enchanted smelt before anything is taken (p = null: no known set)
    k = "00000000-0000-0000-0000-0000000a2400"
    r_ = str(CP.procQueue(None, None, None, JString(k), JString("Furnace"), 1, ench, 1))
    K.check("collections unlock this smelt" in r_ and "nothing was taken" in r_, "ALLOY procQueue refuses a locked Enchanted smelt: %s" % r_)
    r2 = str(CP.procQueue(None, None, None, JString(k), JString("Furnace"), 1, plain, 1))
    K.check("Furnace Charm T1 unlocks this" in r2, "ALLOY a plain alloy still meets the Furnace Charm gate first (no charm here): %s" % r2)
    # the 6 Enchanted alloys -> Smithing; the old homes unchanged
    al = ["Skyy_Ench_" + w for w in ("Bronze", "Dusk", "Azurvane", "Cinder", "Lumen", "Electrum")]
    K.eq([None if Defs.homeOf(JString(i)) is None else str(Defs.homeOf(JString(i))) for i in al], ["Mining"] * 6,
         "HOME the 6 Enchanted alloys go to Mining (TABLE_ALLOYS, like the other Enchanted metals)")
    K.eq([str(Defs.homeOf(JString(i))) for i in ("Skyy_Ench_Copper", "Skyy_Ench_Oak", "Skyy_Ench_Charcoal")], ["Mining", "Foraging", "Smithing"],
         "HOME the older Enchanted rows keep their homes")
    K.check(Defs.homeOf(JString("Skyy_Ench_NoSuchThing")) is None, "HOME an unknown Enchanted id still has no home")
    K.save()


# ======================================================================================================== LIVE2
def run_live_caps(out, jar, scratch, home):
    """the live copy: every profile's Void (pd/<key>.properties) + pool -> per category 0.8.23 space vs 0.8.24 space, stored kept"""
    from jpype import JClass
    K = HK.Child(out)
    HK.jvm([B.SERVER_JAR, jar, B.JAVASSIST], verify=True)
    Pool, Cfg, VS = JClass(PKG + "SackPool"), JClass(PKG + "SackCfg"), JClass(PKG + "VoidStore")
    Paths = JClass("java.nio.file.Paths")
    Pool.LOG = JClass("com.hypixel.hytale.logger.HytaleLogger").get("SkyySacks")
    Pool.DIR = Paths.get(os.path.join(home, "pools"))
    Cfg.FILE = Paths.get(os.path.join(home, "config.properties"))
    Cfg.MTIME = -1
    Cfg.reload()
    pdd = os.path.join(home, "pd")
    keys = sorted(f[:-11] for f in os.listdir(pdd) if f.endswith(".properties")) if os.path.isdir(pdd) else []
    K.check(len(keys) > 0, "LIVE2 the live copy has Void files (%d)" % len(keys))
    raw0 = dict((k_, open(os.path.join(pdd, k_ + ".properties"), "rb").read()) for k_ in keys)
    bad, lines = [], []
    for k_ in keys:
        pr = {}
        for l in raw0[k_].decode("latin-1").splitlines():
            if "=" in l and not l.startswith("#"):
                a, b = l.split("=", 1)
                pr[a.strip()] = b.strip()
        cells = []
        for c in CATS:
            lv, r = max(1, int(pr.get("best." + c, "1"))), int(pr.get("rar." + c, "0"))
            if pr.get("omni") == "true":
                r = 4
            o, n = cap_py(lv, r, 0), int(VS.capOf(lv, r))
            stored = int(Pool.catTotal(k_, c))
            if n < o or n != cap_py(lv, r):
                bad.append((k_, c, o, n))
            cells.append("%s Lv%d %s %d->%d (stored %d%s)" % (c, lv, RAR[r], o, n, stored, ", OVER" if stored > n else ""))
        lines.append(k_[-12:] + ": " + "; ".join(cells))
    K.check(not bad, "LIVE2 every live category's space grows (never smaller) and = (1500 + best level x 150) x rarity: %s" % bad[:3])
    for l in lines:
        K.notes.append("LIVE2 " + l)
        print("LIVE2", l)
    K.check(all(open(os.path.join(pdd, k_ + ".properties"), "rb").read() == raw0[k_] for k_ in keys), "LIVE2 the pd files are untouched (read only)")
    K.save()


if __name__ == "__main__":
    print("kit:", T089.KIT_NOTE)
    HK.run("SkyySacks", VERSION, JAR, OLD_JAR, PKG, SCRATCH, EXPECT, ADDED,
           [("void", run_void24), ("alloy", run_alloy24), ("mig", run_mig), ("live", T0810.run_live10), ("live2", run_live_caps)],
           __file__, live=(BETA, "Skyy_SkyySacks"))
