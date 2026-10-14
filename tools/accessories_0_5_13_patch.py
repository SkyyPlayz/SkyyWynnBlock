"""Derive SkyyAccessories/build_skyyaccessories_0.5.13.py from the GENERATED 0.5.12 script (build_skyyaccessories_0.5.12.py = the
tools/deploy_set.py SET pin, written by tools/accessories_0_5_12_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.12 script
stays untouched - never re-run accessories_0_5_12_patch.py on top of this).
Run:  python tools/accessories_0_5_13_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.13.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.13.py

0.5.13 = THE WORKBENCH TAB ORDER (Skyy 2026-10-13, screenshot of Workbench > Accessories & Bags, docs/answered/gear.md: "since the tutorial
asks you to craft this, id move it to the top. sort them by tier, and per tier,m sort them by easiest to craft.")
  - Workbench Accessory I (Skyy_Accessory_Workbench_T1 - the SkyyQuests tutorial's first craft) is the FIRST entry of the tab.
  - Then every other recipe of the tab by TIER = its rarity (Normal 1, Unique 2, Rare 3, Legendary 4 - the item's own Quality; bench
    accessories I / II / III / IV+ are exactly those rarities; no exceptions: the Accessory Bag wears the Unique colour, so it sorts as
    tier 2 = the cheapest Unique (fixer 2026-10-13: a Unique-coloured item inside the Normal block read as a sorting mistake; it is
    still pocket-craftable through Fieldcraft, unchanged), and inside a tier by EASIEST TO CRAFT = the lowest COST:
      cost(item) = sum over its recipe inputs of quantity x cost(input), divided by the recipe's OutputQuantity;
      an input that is one of OUR items, a vanilla bench (Bench_*), the vanilla lantern / crude torch / crude candle or Concentrated Life
      Essence is expanded through its own recipe (our generated JSON, Assets.zip read-only) - so an upgrade always costs more than the
      accessory it consumes, and Arcane Bench Accessory I pays for its Arcane Bench (Thorium, Void Essence);
      every other input is a RAW material with a material tier MAT_TIER (1 = first-zone basics ... 6 = the rarest) and costs
      3 ** (tier - 1) (each material tier counts as three times harder to get than the one below; 2 ** let 5 Cobalt Ingots beat 20 Iron);
      ties: the English display name, then the id.
    The build FAILS on a raw material MAT_TIER does not list (a new recipe input needs a deliberate tier).
  - The Omni Accessory stays LAST (the old rule "legendaries and omnis at the bottom"; its cost is the highest anyway - asserted).
  - HOW: the server sends the tab's recipes in the iteration order of the registry set SkyyAccessories (the tab OWNER) installs:
    java.util.TreeSet(WbRank) (tools/skyywbtab.py: CraftingWindow builds windowData "craftableRecipes" by iterating that set). WbRank.rank
    is the only thing that changes: this build keeps the shared kit's emitted WbRank and, once the item JSONs exist, replaces its rank(String)
    with the new order (ORDER / TIER tables baked from the generated recipes) and keeps the kit's pattern rule as rankOld(String) for ids
    the table does not list (a future accessory / bench / an old id: + 500000 so it sorts AFTER the listed ones of its tier, the Omni
    Accessory 9000000 and unknown ids 8000000 stay where they were). tools/skyywbtab.py (shared with SkyySacks) is NOT edited; with
    SkyySacks running too the result is the same (the owner always installs its own TreeSet(WbRank) - unchanged WbTab code).
    The protocol has no sort field (protocol CraftingRecipe: id, inputs, outputs, primaryOutput, benchRequirement, knowledgeRequired,
    timeSeconds, requiredMemoriesLevel). Whether the client keeps the order the server sends is still UNVERIFIED (native client).
  - The tab NAME stays "Accessories & Bags": SkyySacks 0.8.0 removed the bag recipes, but the Accessory Bag still lists in the tab, and the
    name text is one lang key that BOTH mods ship from tools/skyywbtab.py (changing it here only would make two mods send different text
    for the same key) - a rename is a shared-kit + SkyySacks change for Skyy to decide.
Config, saves, bridge keys, items, recipes, assets, lang: unchanged. Classes changed: WbRank (rank replaced, rankOld added, ORDER / TIER
fields). Everything else = 0.5.12 (version constants only; the config kit classes follow whatever tools/skyycfg.py is in the tree).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, "SkyyAccessories")
src = os.path.join(HERE, "build_skyyaccessories_0.5.12.py")
dst = os.path.join(HERE, "build_skyyaccessories_0.5.13.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.12"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.12"\n' in s and "hideKnown" in s and "_wbtab_order" not in s, "the source must be the generated 0.5.12 script"
REG0, SYS0 = s.count("registerCommand("), s.count("registerSystem(")

# ---------------------------------------------------------------------------------------------------------------- header
rep('''"""SkyyAccessories 0.5.12 - build script (derived from the generated build_skyyaccessories_0.5.11.py by tools/accessories_0_5_12_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.12.py            -> SkyyAccessories/SkyyAccessories-0.5.12.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.12.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.12.py             (bare JVM -Xverify:all: class compare 0.5.11 -> 0.5.12, hideKnown = hideFrom on
       random sets, the real entity tracker run on BOTH jars with the same results, start twice on a live copy)
''', '''"""SkyyAccessories 0.5.13 - build script (derived from the generated build_skyyaccessories_0.5.12.py by tools/accessories_0_5_13_patch.py -
edit the patch, not this file)
Run:   python build_skyyaccessories_0.5.13.py            -> SkyyAccessories/SkyyAccessories-0.5.13.jar   (deploys go through tools/deploy_set.py --yes)
       python build_skyyaccessories_0.5.13.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)
Test:  python test_skyyaccessories_0.5.13.py             (bare JVM -Xverify:all: class compare 0.5.12 -> 0.5.13 = WbRank only, the new
       order on a real CraftingWindow with and without SkyySacks, the 0.5.12 Lantern tracker checks on the new jar, start twice on a live copy)
0.5.13: THE WORKBENCH TAB ORDER (Skyy 2026-10-13: "since the tutorial asks you to craft this, id move it to the top. sort them by tier, and
     per tier,m sort them by easiest to craft."; full notes in tools/accessories_0_5_13_patch.py): Workbench Accessory I first, then
     tier by tier (Normal, Unique, Rare, Legendary = the item's rarity, the Accessory Bag included = Unique), inside a tier the cheapest
     recipe first (inputs expanded to raw materials, each raw material worth 3 ** (material tier - 1)), the Omni Accessory last. Only
     WbRank.rank changes (the order the server sends); items, recipes, saves unchanged.
''')
rep('VERSION = "0.5.12"\n', 'VERSION = "0.5.13"\n')

# ---------------------------------------------------------------------------------------------------------------- _wbtab_checks: the old order
# print / the old Lantern rank asserts describe the shared kit's order, which this build no longer ships -> the new order check below
rep('''        rq = json.loads(files["Server/Item/Items/Utility/%s.json" % i])["Recipe"]["BenchRequirement"]
        assert rq == WB_REQ, "0.5.4: %s must sit in the Workbench tab only: %r" % (i, rq)
        rk = WB.rank_py(i + WB.RECIPE_SUFFIX + "0")
        last_line = WB.rank_py("Skyy_Talisman_Speed_%s" % ID_WORD[t] + WB.RECIPE_SUFFIX + "0")
        first_bench = min(WB.rank_py("Skyy_Accessory_%s_T%d" % (b, n) + WB.RECIPE_SUFFIX + "0") for b in WB.BENCHES
                          for n in range(1, WB.BENCH_TIERS[b] + 1) if min(n, 4) == t)
        assert t * 1000000 <= rk < (t + 1) * 1000000 and last_line < rk < first_bench, (i, rk, last_line, first_bench)
    print("Workbench tab: the 4 Lantern recipes rank into their rarity tiers (after that tier's crafted stat lines, before its bench "
          "accessories) through tools/skyywbtab.py's pattern rule - the shared kit is unchanged")
''', '''        rq = json.loads(files["Server/Item/Items/Utility/%s.json" % i])["Recipe"]["BenchRequirement"]
        assert rq == WB_REQ, "0.5.4: %s must sit in the Workbench tab only: %r" % (i, rq)
    print("Workbench tab: the 4 Lantern recipes sit in the tab only (0.5.13: their place comes from _wbtab_order)")
''')
rep('''    WB.order_print(names, ("Skyy_Accessory_", "Skyy_Talisman_"))
    print("Workbench tab: %d recipes of this mod in '%s' (Accessory Bag also in pocket crafting), none in a vanilla tab; tab protocol %s"
          % (len(got), WB.TAB_TEXT, WB.WB_VERSION))


_wbtab_checks()
''', '''    print("Workbench tab: %d recipes of this mod in '%s' (Accessory Bag also in pocket crafting), none in a vanilla tab; tab protocol %s"
          % (len(got), WB.TAB_TEXT, WB.WB_VERSION))


_wbtab_checks()


# ================= 0.5.13: THE WORKBENCH TAB ORDER (Skyy 2026-10-13: "since the tutorial asks you to craft this, id move it to the top. sort them
# by tier, and per tier,m sort them by easiest to craft."; full notes in tools/accessories_0_5_13_patch.py). Workbench Accessory I first; then
# by tier (= the item's rarity Quality, no exceptions), inside a tier by cost (raw materials, 3 ** (material tier - 1) each),
# ties by English name then id; the Omni Accessory last (not listed: the kit's rankOld keeps it at 9000000).
from fractions import Fraction as _Frac
ORD_FIRST = "Skyy_Accessory_Workbench_T1"
ORD_LAST = OMNI
ORD_BASE = 3                     # cost of one raw material = ORD_BASE ** (material tier - 1)
ORD_SHIFT = 500000               # a pattern-ranked id (kit rule, t * 1000000 + < 400000) moves after the listed ids of its tier
# vanilla inputs that are themselves crafted from the tab's point of view: expanded through their Assets.zip recipe
ORD_EXPAND = ("Bench_", "Deco_Lantern", "Furniture_Crude_Torch", "Furniture_Crude_Candle", "Ingredient_Life_Essence_Concentrated")
# RAW material tiers (where a player first finds it: 1 = first-zone basics, 2 = Iron / medium hides / second-zone wood and crops,
# 3 = Thorium, Silver, Gold, gems, heavy hides, silk, 4 = Cobalt, Fire / Ice, 5 = Shadoweave, Cindercloth, Void / Lightning,
# 6 = Voidheart and the last crops / wood of the Farming Bench ladder). A missing input stops the build.
MAT_TIER = {}
for _t, _ids in ((1, "res:Wood_Trunk res:Rock res:Rubble res:Wood_Softwood_Trunk res:Salvage_Wood Ingredient_Stick Ingredient_Fibre "
                     "Ingredient_Tree_Sap Ingredient_Bar_Copper Ingredient_Leather_Light Ingredient_Hide_Light Ingredient_Fabric_Scrap_Linen "
                     "Ingredient_Fabric_Scrap_Cotton Ingredient_Feathers_Light Ingredient_Bone_Fragment Ingredient_Life_Essence "
                     "Plant_Crop_Wheat_Item Plant_Crop_Lettuce_Item Ingredient_Crystal_Red Ingredient_Crystal_Yellow Ingredient_Crystal_Blue "
                     "Ingredient_Crystal_Green Ingredient_Crystal_Cyan"),
                 (2, "Ingredient_Bar_Iron Ingredient_Leather_Medium Ingredient_Hide_Medium Ingredient_Feathers_Blue Ingredient_Sac_Venom "
                     "Wood_Azure_Trunk res:Wood_Lightwood_Trunk Plant_Crop_Carrot_Item Plant_Crop_Corn_Item"),
                 (3, "Ingredient_Bar_Thorium Ingredient_Bar_Silver Ingredient_Bar_Gold Ingredient_Leather_Heavy Ingredient_Hide_Heavy "
                     "Ingredient_Fabric_Scrap_Silk Rock_Gem_Topaz Rock_Gem_Ruby Rock_Gem_Emerald Rock_Gem_Sapphire Rock_Gem_Zephyr "
                     "Ingredient_Chitin_Sturdy Plant_Crop_Cauliflower_Item Plant_Crop_Turnip_Item res:Wood_Hardwood_Trunk"),
                 (4, "Ingredient_Bar_Cobalt Ingredient_Fire_Essence Ingredient_Ice_Essence Plant_Crop_Aubergine_Item Plant_Crop_Pumpkin_Item "
                     "res:Wood_Drywood_Trunk"),
                 (5, "Ingredient_Fabric_Scrap_Shadoweave Ingredient_Bolt_Cindercloth Ingredient_Void_Essence Ingredient_Lightning_Essence "
                     "Plant_Crop_Tomato_Item Plant_Crop_Chilli_Item res:Wood_Darkwood_Trunk"),
                 (6, "Ingredient_Voidheart Plant_Crop_Cotton_Item Plant_Crop_Rice_Item Wood_Redwood_Trunk")):
    for _i in _ids.split():
        assert _i not in MAT_TIER, _i
        MAT_TIER[_i] = _t


def _ord_items():
    """our generated item JSONs by id (every recipe of the tab and every input that is one of our items)"""
    out = {}
    for p, t in files.items():
        if p.startswith("Server/Item/Items/") and p.endswith(".json"):
            out[os.path.basename(p)[:-5]] = json.loads(t)
    return out


def _ord_key(x):
    return x.get("ItemId") if x.get("ItemId") else "res:" + x["ResourceTypeId"]


def _ord_cost(iid, own, memo, path=()):
    """(cost as an exact Fraction, highest raw material tier) of ONE iid"""
    if iid in memo:
        return memo[iid]
    assert iid not in path, "0.5.13: recipe loop %s" % (path + (iid,),)
    if iid in MAT_TIER:
        out = (_Frac(ORD_BASE) ** (MAT_TIER[iid] - 1), MAT_TIER[iid])
    elif iid in own or iid.startswith(ORD_EXPAND):
        if iid in own:
            node = own[iid]
        else:
            need_item(iid)
            node = json.loads(_ASSETS.read(_ITEMS[iid]).decode("utf-8-sig"))
        r = node.get("Recipe")
        assert r and r.get("Input"), "0.5.13: %s has no recipe to expand" % iid
        oq = r.get("OutputQuantity") or 1
        c, top = _Frac(0), 0
        for x in r["Input"]:
            cc, tt = _ord_cost(_ord_key(x), own, memo, path + (iid,))
            c += cc * int(x.get("Quantity", 1))
            top = max(top, tt)
        out = (c / int(oq), top)
    else:
        raise SystemExit("0.5.13 Workbench tab order: the recipe input %s (via %s) has no material tier - add it to MAT_TIER" % (iid, " > ".join(path)))
    memo[iid] = out
    return out


def ord_rank_py(rid):
    """the Python mirror of the 0.5.13 WbRank.rank (the harness compares both on every id it sees)"""
    if rid is None:
        return 9900000
    b = WB.base_py(rid)
    if b in ORD_POS:
        i = ORD_POS[b]
        return ORD_TIER[i] * 1000000 + 1000 + i
    r = WB.rank_py(rid)
    return r + ORD_SHIFT if 1000000 <= r < 5000000 else r


def _wbtab_order():
    global ORDER, ORD_TIER, ORD_POS, ORD_COST, ORD_NAMES
    own = _ord_items()
    tab = sorted(i for i, n in own.items() if n.get("Recipe") and any(WB.TAB_ID in (q.get("Categories") or []) for q in
                                                                       n["Recipe"].get("BenchRequirement") or []))
    assert len(tab) == 51 and ORD_FIRST in tab and ORD_LAST in tab and BAG in tab, (len(tab), tab[:3])
    lmap = dict(l.split("=", 1) for l in lang if "=" in l)
    ORD_NAMES = dict((i, lmap["server.items.%s.name" % i]) for i in tab)
    memo = {}
    rows = []
    for i in tab:
        q = own[i]["Quality"]
        t = QUAL_IDS.index(q)
        assert 1 <= t <= 4, (i, q)
        c, top = _ord_cost(i, own, memo)
        rows.append((t, c, ORD_NAMES[i], i, top))
    ORD_COST = dict((r[3], r[1]) for r in rows)
    body = sorted(r for r in rows if r[3] not in (ORD_FIRST, ORD_LAST))
    first = [r for r in rows if r[3] == ORD_FIRST][0]
    assert first[0] == 1, first
    ORDER = [ORD_FIRST] + [r[3] for r in body]
    ORD_TIER = [0] + [r[0] for r in body]
    ORD_POS = dict((i, k) for k, i in enumerate(ORDER))
    # the rules, asserted
    assert ORDER[0] == ORD_FIRST and ORD_LAST not in ORDER and sorted(ORDER + [ORD_LAST]) == tab
    assert all(ORD_TIER[k] <= ORD_TIER[k + 1] for k in range(len(ORDER) - 1)), "tiers ascending"
    assert all(body[k][:3] <= body[k + 1][:3] for k in range(len(body) - 1)), "inside a tier: cost, then name ascending"
    assert ORD_COST[ORD_LAST] > max(ORD_COST[i] for i in ORDER), "the Omni Accessory is also the most expensive recipe"
    for i in tab:   # an upgrade never lists before what it consumes
        for x in own[i]["Recipe"]["Input"]:
            k = _ord_key(x)
            if k in ORD_POS and i in ORD_POS:
                assert ORD_POS[k] < ORD_POS[i], "0.5.13: %s lists before its input %s" % (i, k)
    rids = [i + WB.RECIPE_SUFFIX + "0" for i in tab]
    want = [i + WB.RECIPE_SUFFIX + "0" for i in ORDER + [ORD_LAST]]
    assert sorted(rids, key=lambda r: (ord_rank_py(r), r)) == want, "the mirror sorts the tab exactly as ORDER + Omni"
    assert ord_rank_py("Skyy_Talisman_Crit_Epic_Recipe_Generated_0") > ord_rank_py("Skyy_Accessory_Farmingbench_T7_Recipe_Generated_0") and \\
        ord_rank_py("Skyy_Talisman_Crit_Epic_Recipe_Generated_0") < ord_rank_py(OMNI) and \\
        ord_rank_py("Skyy_Talisman_Crit_Uncommon") < ord_rank_py("Skyy_Talisman_Vitality_Rare"), "a future line sorts after its tier, before the next"
    # ---- WbRank: the kit's rank(String) becomes rankOld(String); rank(String) = the table first (written again over the 0.5.2 class file)
    wr = WB_CLASSES[0]
    assert str(wr.getName()) == PKG + ".WbRank"
    wr.defrost()
    m0 = wr.getDeclaredMethod("rank")
    wr.addMethod(CtNewMethod.copy(m0, "rankOld", wr, None))
    wr.removeMethod(m0)
    wr.addField(CtField.make("public static final String[] ORDER = new String[] { %s };" % jstrs(ORDER), wr))
    wr.addField(CtField.make("public static final int[] TIER = new int[] { %s };" % ", ".join(str(t) for t in ORD_TIER), wr))
    wr.addMethod(CtNewMethod.make("""
public static long rank(String id) {
  if (id == null) return 9900000L;
  int i = idx(ORDER, base(id));
  if (i >= 0) return TIER[i] * 1000000L + 1000L + i;
  long r = rankOld(id);
  if (r >= 1000000L && r < 5000000L) return r + %dL;
  return r;
}""" % ORD_SHIFT, wr))
    wr.writeFile(OUT)
    print("Workbench tab order (0.5.13, %d recipes; tier = rarity, cost = raw materials x %d ** (material tier - 1), * = pinned):" % (len(tab), ORD_BASE))
    rowp = []
    for k, i in enumerate(ORDER + [ORD_LAST], 1):
        t = ORD_TIER[k - 1] if k <= len(ORDER) else 4
        c = ORD_COST[i]
        rowp.append("%2d %s%s T%d %s" % (k, "*" if i in (ORD_FIRST, ORD_LAST) else " ", ORD_NAMES[i], max(t, 1),
                                          ("%d" % c) if c.denominator == 1 else ("%.1f" % float(c))))
    for k in range(0, len(rowp), 3):
        print("   " + " | ".join(rowp[k:k + 3]))


_wbtab_order()
''')

# ---------------------------------------------------------------------------------------------------------------- guards
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0, "no new command or ECS system"
assert s.index("_wbtab_order()\n") > s.index("for c in WB_CLASSES:"), "the WbRank change runs after the classes are written once"
assert s.index("_wbtab_order()\n") < s.index("_aitems = []"), "the access audit sees the new WbRank"
_gone = sorted(ln for ln in set(OLD.split(LF)) - set(s.split(LF)))
_ALLOWED = {
    '"""SkyyAccessories 0.5.12 - build script (derived from the generated build_skyyaccessories_0.5.11.py by tools/accessories_0_5_12_patch.py -',
    "Run:   python build_skyyaccessories_0.5.12.py            -> SkyyAccessories/SkyyAccessories-0.5.12.jar   (deploys go through tools/deploy_set.py --yes)",
    "       python build_skyyaccessories_0.5.12.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world (never used)",
    "Test:  python test_skyyaccessories_0.5.12.py             (bare JVM -Xverify:all: class compare 0.5.11 -> 0.5.12, hideKnown = hideFrom on",
    "       random sets, the real entity tracker run on BOTH jars with the same results, start twice on a live copy)",
    'VERSION = "0.5.12"',
    '        rk = WB.rank_py(i + WB.RECIPE_SUFFIX + "0")',
    '        last_line = WB.rank_py("Skyy_Talisman_Speed_%s" % ID_WORD[t] + WB.RECIPE_SUFFIX + "0")',
    '        first_bench = min(WB.rank_py("Skyy_Accessory_%s_T%d" % (b, n) + WB.RECIPE_SUFFIX + "0") for b in WB.BENCHES',
    "                          for n in range(1, WB.BENCH_TIERS[b] + 1) if min(n, 4) == t)",
    "        assert t * 1000000 <= rk < (t + 1) * 1000000 and last_line < rk < first_bench, (i, rk, last_line, first_bench)",
    '    print("Workbench tab: the 4 Lantern recipes rank into their rarity tiers (after that tier\'s crafted stat lines, before its bench "',
    '          "accessories) through tools/skyywbtab.py\'s pattern rule - the shared kit is unchanged")',
    '    WB.order_print(names, ("Skyy_Accessory_", "Skyy_Talisman_"))',
}
_bad = [ln for ln in _gone if ln not in _ALLOWED]
assert not _bad, "0.5.12 lines lost by accident: %s" % _bad[:5]
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, "(%d lines; 0.5.12 had %d)" % (s.count(LF), OLD.count(LF)))
