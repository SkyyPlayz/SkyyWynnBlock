"""Derive SkyyBazaar/build_skyybazaar_0.1.4.py from the LIVE 0.1.3 (build_skyybazaar_0.1.3.py = the tools/deploy_set.py SET pin;
0.1.3 and every older script stay untouched).
Run:  python tools/bazaar_0_1_4_patch.py   then   python SkyyBazaar/build_skyybazaar_0.1.4.py   (never --deploy: coordinated deploy)
SkyyBazaar uses patch scripts (0.1.1 .. 0.1.3 came from tools/bazaar_0_1_1_patch.py .. tools/bazaar_0_1_3_patch.py): edit THIS file,
never the generated build script.

0.1.4 = PROGRESSION PRICES (Skyy 2026-10-04, LOCKED in docs/answered/economy.md: "right now i can easily buy a stack of mithril like
its nothing ... id probbly 2x each material. so copper stays. iron gets 2x. thorium gets 4x ect", "same fore the more rare woods. we
are building a progresson tree", "and the crops in the vanilla expansion path ... especially for the eternal seeds", hides "just double
the price of all of them"; cloth + gems: the open question's default, x2 per tier step). What the patch changes:
  - PRICE_014 below: the new DEFAULT base price of every product whose default moves (the generated PRODUCTS rows get it; every other
    row, every name, every tab and every AUTO row is unchanged). Ingots, leathers and cloth bolts stay AUTO and follow their raw inputs.
  - crops / seeds / eternal seeds follow the VANILLA farming path: the build reads the Farmingbench RequiredTierLevel of every seed
    recipe in Assets.zip, checks it against VANILLA_SEED_TIER and checks every crop / seed / eternal seed price against the tier
    ladder (a price under its ladder value only where the no-money-loop cap requires it, each cap written down with its reason).
  - the money-loop checks (0.1.2's check_assets + 0.1.3's loop_check at every premium 0-22 + the admin price guard) run on the new
    table, plus a 0.1.4 check over the vanilla recipes UNIONED with every SET jar's own item / recipe assets (SkyySacks bags, SkyyGear
    staffs / wands, SkyyAccessories benches + accessories, SkyyCooking cooked food ...), and the build prints the tightest margins.
  - saved state: products.properties gets a ONE-TIME update (Catalog.migrate14, marker migrated.0.1.4 in pricing.properties): a product
    line whose price is still EXACTLY its 0.1.3 default gets the 0.1.4 default (price text only; id, category, name, spacing, line
    ending and every other line stay byte for byte); a hand-set price (/bazaaradmin price or a hand edit) is kept and logged. A
    byte-verified copy of the file goes to Skyy_SkyyBazaar/config-history/ first; one trades.log line per changed price with its undo
    command; runs once; market.properties (demand) is never touched.
"""
import os
import re
import ast
import math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.3.py")
dst = os.path.join(ROOT, "SkyyBazaar", "build_skyybazaar_0.1.4.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert "@@" not in s, "0.1.3 already holds a @@ token"
REG0 = s.count("registerCommand(")


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d != %d: %s" % (n, count, old[:120])
    s = s.replace(old, new)


def block(a, b):
    """the text from anchor a (included) to anchor b (excluded) of the CURRENT source"""
    assert s.count(a) == 1 and s.count(b) == 1, (a[:60], b[:60])
    return s[s.index(a):s.index(b)]


# ------------------------------------------------------------------------------------------------ blocks that must stay byte-identical
# the whole trade core, the page, the admin commands and the tick: 0.1.4 changes prices, the product checks and the one-time update only
KEEP = [block("# ================= Coins (SkyyCoins bridge; copied from SkyyBank) =================", "# ================= Catalog"),
        block("# ================= Market (factors, pricing, decay, persistence, trade log queue) =================",
              "# ================= Inv (count-verified inventory moves; world thread only) ================="),
        block("# ================= Inv (count-verified inventory moves; world thread only) =================", "# ================= plugin ="),
        block("# ================= BzUtil =================", "# ================= Coins (SkyyCoins bridge; copied from SkyyBank) ================="),
        block("def check_assets(products, spread):", "# ================= 0.1.3 build-time pipeline"),
        block("def asset_model(js, data, drops, recfiles):", "def bag_items(js, data, drops, M, lang):"),
        block("def processed_table(M, products):", "def loop_check(M, prices, spread):"),
        block("def edge_table(M, products, charcoal):", "EDGES = edge_table(MODEL, set(ids), CHARCOAL)")]

# ================================================================================================================ the 0.1.4 price table
# (id, 0.1.3 default, 0.1.4 default) per family, from the LOCKED lines. The 0.1.3 value is asserted against the 0.1.3 PRODUCTS row.
METALS = [  # ore x2 per tier step of the tool ladder (Copper x1 ... Onyxium x64); Silver, Gold, Prisma: not in the ladder, unchanged
    ("Ore_Iron", 8, 16), ("Ore_Thorium", 12, 48), ("Ore_Cobalt", 18, 144), ("Ore_Adamantite", 30, 480), ("Ore_Mithril", 45, 1440),
    ("Ore_Onyxium", 58, 3712)]
_W2 = ("Apple", "Banyan", "Bottletree", "Camphor", "Fig_Blue", "Gumboab", "Maple", "Palo", "Poisoned", "Sallow", "Spiral", "Windwillow",
       "Wisteria_Wild")
WOODS = ([("Wood_%s_Trunk" % w, 4, 8) for w in _W2] + [("Wood_Amber_Trunk", 5, 20), ("Wood_Redwood_Trunk", 5, 20),
         ("Wood_Azure_Trunk", 6, 48), ("Wood_Petrified_Trunk", 6, 48)] + [("Wood_%s_Trunk" % w, 8, 128) for w in ("Crystal", "Fire", "Ice", "Stormbark")])
HIDES = [("Ingredient_Hide_%s" % h, a, 2 * a) for h, a in (("Soft", 4), ("Light", 6), ("Medium", 12), ("Heavy", 18), ("Scaled", 24),
                                                          ("Storm", 30), ("Dark", 36), ("Prismic", 45))]
CLOTH = [  # scraps x2 per tier step of today's prices (4 | 8 | 10 | 12 | 16 | 20); the bolts are AUTO (woven from 1 Cotton / Wool Scraps)
    ("Ingredient_Fabric_Scrap_Silk", 8, 16), ("Ingredient_Fabric_Scrap_Shadoweave", 10, 40), ("Ingredient_Fabric_Scrap_Cindercloth", 12, 96),
    ("Ingredient_Fabric_Scrap_Stormsilk", 16, 256), ("Ingredient_Fabric_Scrap_Prismaloom", 20, 640)]
GEMS = [("Rock_Gem_Diamond", 60, 120), ("Rock_Gem_Voidstone", 60, 120)]   # gems x2 per tier step (40 | 60): the 40s stay
# the vanilla farming path (Farmingbench RequiredTierLevel of the normal seed recipe, 1 when none; the eternal seed recipe is one tier
# higher) -> 4 price tiers, two vanilla tiers each (Skyy: "what and carrots are the cheapest"); x2 per tier step of today's prices
VANILLA_SEED_TIER = {"Lettuce": 1, "Wheat": 1, "Carrot": 2, "Corn": 2, "Cauliflower": 3, "Turnip": 3, "Aubergine": 4, "Pumpkin": 4,
                     "Chilli": 5, "Tomato": 5, "Cotton": 6, "Rice": 6, "Onion": 7, "Potato": 7}
PRICE_TIER = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4}
CROP_PRICE, SEED_PRICE, ETERNAL_PRICE = {1: 2, 2: 6, 3: 16, 4: 40}, {1: 1, 2: 2, 3: 4, 4: 8}, {1: 50, 2: 200, 3: 800, 4: 3200}
# no-money-loop caps (Essence of Life 0.5; a buy -> craft -> sell must not pay at the 10 % spread: price x 0.9 <= recipe cost x 1.1;
# the eternal caps keep ~4 % under that bound: Chilli / Tomato 627, Onion / Potato 2,512)
SEED_CAP = {"Chilli": 3.5, "Tomato": 3.5, "Onion": 6, "Potato": 6}         # 6 / 10 Essence of Life -> 1 seed: caps 3.67 / 6.11
ETERNAL_CAP = {"Lettuce": 37, "Wheat": 37, "Chilli": 600, "Tomato": 600, "Onion": 2400, "Potato": 2400}   # recipe cost x 1.1 / 0.9
_crop_name = {"Onion": "Onion", "Potato": "Potato"}
CROPS = []
for _c, _vt in sorted(VANILLA_SEED_TIER.items()):
    _t = PRICE_TIER[_vt]
    CROPS.append(("Plant_Crop_%s_Item" % _c, None, CROP_PRICE[_t]))
    CROPS.append(("Plant_Seeds_%s" % _c, None, SEED_CAP.get(_c, SEED_PRICE[_t])))
    CROPS.append(("Plant_Seeds_%s_Eternal" % _c, None, ETERNAL_CAP.get(_c, ETERNAL_PRICE[_t])))
# Bronze Ingot (fixed, Bazaar-only): keeps closing the Ancient Steel craft -> salvage chain at the new Iron Ore / Medium Hide prices
OTHER = [("Ingredient_Bar_Bronze", 21, 40)]
# SAPLINGS (Skyy 2026-10-05 LOCKED: seeds + saplings "Raise with their tier"): a sapling climbs x2 per tier step like its log (today's
# sapling price = its log's, so x2 per tier and "same sapling:log ratio" are the same ladder), capped where the vanilla Farmingbench
# recipe (N Essence of Life -> 1 sapling; Apple: 1 Greater Essence + 4 Apples) would let buy -> craft -> sell pay. ONE cap rule for
# seeds and saplings: floor to 0.5 of 0.6 x the Essence of Life count (the bound is 0.611 x N = N x 0.5 x 1.1 / 0.9, so ~2 % margin).
# SAPLING_ESSENCE = the Essence of Life count of each sapling's recipe in Assets.zip, own or inherited through Parent (checked by the
# build); None = a recipe with other inputs (Apple: Greater Essence + Apples)
SAPLING_TIER = {"Bamboo": 1, "Ash": 1, "Aspen": 1, "Beech": 1, "Birch": 1, "Cedar": 1, "Dry": 1, "Jungle": 1, "Oak": 1, "Palm": 1,
                "Spruce": 1, "Spruce_Frozen": 1, "Apple": 2, "Banyan": 2, "Bottletree": 2, "Camphor": 2, "Fig_Blue": 2, "Gumboab": 2,
                "Maple": 2, "Palo": 2, "Poisoned": 2, "Sallow": 2, "Spiral": 2, "Windwillow": 2, "Wisteria_Wild": 2, "Amber": 3,
                "Redwood": 3, "Azure": 4, "Petrified": 4, "Crystal": 5, "Fire": 5, "Ice": 5, "Stormbark": 5}
SAPLING_ESSENCE = {"Bamboo": 15, "Ash": 15, "Aspen": 5, "Beech": 5, "Birch": 10, "Cedar": 25, "Dry": 30, "Jungle": 15, "Oak": 15,
                   "Palm": 35, "Spruce": 15, "Spruce_Frozen": 15, "Apple": None, "Banyan": 15, "Bottletree": 30, "Camphor": 10,
                   "Fig_Blue": 20, "Gumboab": 10, "Maple": 20, "Palo": 15, "Poisoned": 15, "Sallow": 15, "Spiral": 20, "Windwillow": 15,
                   "Wisteria_Wild": 25, "Amber": 15, "Redwood": 20, "Azure": 20, "Petrified": 30, "Crystal": 15, "Fire": 30, "Ice": 15,
                   "Stormbark": 15}


def ess_cap(n):
    return None if n is None else math.floor(0.6 * n * 2 + 1e-9) / 2.0


for _c, _n in (("Chilli", 6), ("Tomato", 6), ("Onion", 10), ("Potato", 10)):
    assert SEED_CAP[_c] == ess_cap(_n), (_c, SEED_CAP[_c], ess_cap(_n))      # the seed caps follow the same rule
FAMILIES = [("metals (ore; ingots AUTO)", METALS), ("woods (logs; planks unchanged)", WOODS), ("hides (leathers AUTO)", HIDES),
            ("cloth scraps (bolts AUTO)", CLOTH), ("gems", GEMS), ("crops / seeds / eternal seeds (vanilla farming path)", CROPS),
            ("other", OTHER)]

# ------------------------------------------------------------------------------------------------ apply it to the PRODUCTS rows
_pa = s.index("PRODUCTS = [  # (item id, base price or AUTO, official en-US name)")
_pb = s.index("\n]\n", _pa) + 3
_ptxt = s[_pa:_pb]
OLD013 = {}
for _m in re.finditer(r'^    \("(\w+)", ([0-9.]+|AUTO), "', _ptxt, re.M):
    OLD013[_m.group(1)] = None if _m.group(2) == "AUTO" else ast.literal_eval(_m.group(2))
SAPLINGS, SAPLING_CAPPED = [], {}
for _s, _t in SAPLING_TIER.items():
    _i = "Plant_Sapling_%s" % _s
    _want = OLD013[_i] * 2 ** (_t - 1)
    _cap = ess_cap(SAPLING_ESSENCE[_s])
    _new = _want if _cap is None or _want <= _cap else _cap
    if _new != _want:
        SAPLING_CAPPED[_i] = (_want, _cap)
    assert _new >= OLD013[_i], _i                                       # never below today's price
    SAPLINGS.append((_i, OLD013[_i], int(_new) if float(_new).is_integer() else _new))
FAMILIES.insert(-1, ("saplings (x2 per log tier, Essence of Life caps)", SAPLINGS))
PRICE_014 = {}
CHANGED = {}
for _fam, _rows in FAMILIES:
    for _id, _old, _new in _rows:
        assert _id in OLD013 and OLD013[_id] is not None, "not a fixed 0.1.3 product: %s" % _id
        assert _old is None or abs(OLD013[_id] - _old) < 1e-9, "%s: 0.1.3 price is %s, the table says %s" % (_id, OLD013[_id], _old)
        assert _id not in PRICE_014, "two families price %s" % _id
        PRICE_014[_id] = _new
        if abs(OLD013[_id] - _new) > 1e-9:
            CHANGED[_id] = (OLD013[_id], _new)


def _num(v):
    return ("%g" % v) if isinstance(v, float) else str(v)


_new_ptxt = _ptxt
for _id, (_o, _n) in CHANGED.items():
    _pat = re.compile(r'^(    \("%s", )([0-9.]+)(, ")' % re.escape(_id), re.M)
    assert len(_pat.findall(_new_ptxt)) == 1, _id
    _new_ptxt = _pat.sub(lambda m: m.group(1) + _num(_n) + m.group(3), _new_ptxt)
s = s[:_pa] + _new_ptxt + s[_pb:]
_changed_lines = ",\n".join('    "%s": (%s, %s)' % (i, _num(o), _num(n)) for i, (o, n) in sorted(CHANGED.items()))

# ================================================================================================================ docstring
rep('"""SkyyBazaar 0.1.3 - build script (javassist via jpype).', '"""SkyyBazaar 0.1.4 - build script (javassist via jpype).')
rep('''Run:   python build_skyybazaar_0.1.3.py            -> SkyyBazaar/SkyyBazaar-0.1.3.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.3 is GENERATED from build_skyybazaar_0.1.2.py by tools/bazaar_0_1_3_patch.py - edit the patch, not this file; 0.1.2 came
       from 0.1.1 by tools/bazaar_0_1_2_patch.py, 0.1.1 from 0.1 by tools/bazaar_0_1_1_patch.py; every older script is kept as it was)
''', '''Run:   python build_skyybazaar_0.1.4.py            -> SkyyBazaar/SkyyBazaar-0.1.4.jar   (build only; deploys go through
       tools/deploy_set.py --yes, never --deploy)
       (0.1.4 is GENERATED from build_skyybazaar_0.1.3.py by tools/bazaar_0_1_4_patch.py - edit the patch, not this file; 0.1.3 came
       from 0.1.2 by tools/bazaar_0_1_3_patch.py, 0.1.2 from 0.1.1, 0.1.1 from 0.1; every older script is kept as it was)

0.1.4 (2026-10-05) - PROGRESSION PRICES (Skyy 2026-10-04, LOCKED in docs/answered/economy.md: "id probbly 2x each material. so copper
stays. iron gets 2x. thorium gets 4x ect" / "same fore the more rare woods. we are building a progresson tree" / "the crops in the
vanilla expansion path ... especially for the eternal seeds" / hides "just double the price of all of them"; cloth + gems: the open
question's default, x2 per tier step). Only DEFAULT prices change: the trade core, the page, the commands, the tick, the tabs and every
name are 0.1.3's (asserted byte-identical by tools/bazaar_0_1_4_patch.py).
 - PRICE_014 (the table below PRODUCTS): ores x2 per tier step of the tool ladder (Copper 5, Iron 16, Thorium 48, Cobalt 144,
   Adamantite 480, Mithril 1,440, Onyxium 3,712; ingots stay AUTO = ore + fuel x (1 + premium); Silver, Gold, Prisma unchanged); logs x2
   per tier step (T1 3 / Bamboo, Burnt 2 stay; T2 8; T3 Amber, Redwood 20; T4 Azure, Petrified 48; T5 Crystalwood, Fire, Frostwood,
   Stormbark 128; planks unchanged); hides x2 flat (Soft 8 ... Prismatic 90; leathers AUTO); cloth scraps x2 per tier step
   (Wool / Linen / Cotton 4, Silk 16, Shadoweave 40, Cindercloth 96, Stormsilk 256, Prismaloom 640; bolts AUTO from 1 Cotton / Wool
   Scraps - the vanilla Loombench weaves EVERY bolt but Wool from 1 Cotton, so a bolt can never cost more than ~1.22 x Cotton);
   Diamond / Voidstone 60 -> 120 (the 40 gems stay). Bronze Ingot 21 -> 40 (Bazaar-only: from 38.5 the latent buy Bronze + log +
   Light Leather -> Ancient Steel armor -> salvage -> smelt / tan -> sell chain stays closed at every premium 0-22 with the new Iron
   Ore / hide prices; at 21 it paid x1.25).
 - CROPS on the VANILLA farming path: the build reads the Farmingbench RequiredTierLevel of each normal seed recipe (Assets.zip) and
   stops when it differs from VANILLA_SEED_TIER: Lettuce, Wheat 1 | Carrot, Corn 2 | Cauliflower, Turnip 3 | Aubergine, Pumpkin 4 |
   Chilli, Tomato 5 | Cotton, Rice 6 | Onion, Potato 7 (eternal seeds one tier higher). Two vanilla tiers = one price tier: crops
   2 / 6 / 16 / 40, normal seeds 1 / 2 / 4 / 8, eternal seeds 50 / 200 / 800 / 3,200 - each held under its no-loop cap where the
   vanilla recipe needs it (Essence of Life 0.5: seed <= essence x 0.5 x 1.1 / 0.9; eternal <= its recipe cost x 1.1 / 0.9):
   Chilli / Tomato seeds 3.5, Onion / Potato seeds 6, Lettuce / Wheat eternal 37, Chilli / Tomato eternal 600, Onion / Potato eternal
   2,400. NOTE: the vanilla path is NOT today's price order (Potato / Onion are the LAST vanilla tier but were 2 / 3 coins).
 - SAPLINGS (Skyy 2026-10-05 LOCKED: seeds + saplings "Raise with their tier"): x2 per tier step of their log (today a sapling costs
   what its log costs, so this is also the same sapling:log ratio), capped where the vanilla Farmingbench recipe (N Essence of Life -> 1;
   SAPLING_ESSENCE, checked against Assets.zip) would let buy -> craft -> sell pay. ONE cap rule for seeds and saplings: floor to 0.5 of
   0.6 x N (the loop bound is 0.611 x N). Crystal / Poisoned inherit Oak's 15-essence recipe; Apple's needs Greater Essence + Apples: uncapped.
 - MONEY LOOPS: everything 0.1.3 checks (check_assets at premium 0 / 15 / 20 / 22, loop_check at every premium 0..22 - fuel, charcoal,
   co-products, liquidation - and the admin price guard) on the new table, PLUS (0.1.4) the same loop_check over the vanilla recipes
   UNIONED with the item / recipe assets of every tools/deploy_set.py SET jar (their recipes added, their items' resource types added -
   never removing a vanilla recipe, so the union is at least as strict); the build prints the tightest recipe margins.
 - SAVED STATE: products.properties gets a ONE-TIME update at the first 0.1.4 start (Catalog.migrate14, after 0.1.3's migrate; marker
   migrated.0.1.4 appended to pricing.properties, whose other bytes stay): a product line whose price is still EXACTLY its 0.1.3
   default (numerically: "16" = "16.0") gets its 0.1.4 default - the price text only; id, category, name, spacing, every other line and
   each line ending stay byte for byte. A price that is not the 0.1.3 default (set live with /bazaaradmin price, or a hand edit) is
   KEPT and logged. Before the file is written a byte copy goes to Skyy_SkyyBazaar/config-history/Skyy_SkyyBazaar~products.properties.
   <yyyyMMdd-HHmmss-SSS>.bak and is read back and compared (a mismatch changes nothing; the next start retries). trades.log gets one
   MIGRATE-0.1.4 summary line + one line per changed price with its undo command (/bazaaradmin price <id> <old>) + one per kept
   price; one server INFO line. A failed step writes no marker and retries at the next start (idempotent: a moved line no longer holds
   its 0.1.3 default). market.properties (demand factors, counters) is never touched; processed goods stay auto / fixed as they were.
   0.1.3's own update (kept for a server coming from 0.1.2, or one whose migrated.0.1.3 marker was lost) now also counts a 0.1.3 seed
   line (SEED013) as a default, so a re-run moves it to its 0.1.4 line instead of taking a bar at its 0.1.3 auto price for a hand
   price and making it FIXED.
   Undo all: put the config-history copy back as products.properties and remove the migrated.0.1.4 line (or roll back to 0.1.3).
''')
rep('VERSION = "0.1.3"', 'VERSION = "0.1.4"')

# ================================================================================================================ the table + checks
rep('''# 0.1.2's product table, VERBATIM (renamed): the one-time update tells a 0.1.2 default line from a hand-edited one with it''',
    '''# 0.1.4: every product whose DEFAULT price moved: id -> (0.1.3 default, 0.1.4 default). The one-time update (Catalog.migrate14) moves a
# line still holding the 0.1.3 value; the build checks the PRODUCTS rows against it (tools/bazaar_0_1_4_patch.py holds the families)
PRICE_014 = {
%s,
}
# the vanilla farming path (Farmingbench RequiredTierLevel of the normal seed recipe; checked against Assets.zip below) -> price tier
VANILLA_SEED_TIER = %r
PRICE_TIER = %r
CROP_PRICE, SEED_PRICE, ETERNAL_PRICE = %r, %r, %r
SEED_CAP = %r
ETERNAL_CAP = %r
SAPLING_TIER = %r
SAPLING_ESSENCE = %r

# 0.1.2's product table, VERBATIM (renamed): the one-time update tells a 0.1.2 default line from a hand-edited one with it''' % (
        _changed_lines, VANILLA_SEED_TIER, PRICE_TIER, CROP_PRICE, SEED_PRICE, ETERNAL_PRICE, SEED_CAP, ETERNAL_CAP, SAPLING_TIER,
        SAPLING_ESSENCE))

rep('''# every 0.1.2 product stays, with its 0.1.2 raw price (the one-time update rewrites a 0.1.2 default line to its 0.1.3 line)''',
    '''# every 0.1.2 product stays, with its 0.1.2 raw price unless 0.1.4 moved its default (PRICE_014; the one-time updates rewrite a
# 0.1.2 / 0.1.3 default line to its current line)''')
rep('''    if p not in PROC and abs(float(_new[p][1]) - b) > 1e-9:''', '''    if p not in PROC and p not in PRICE_014 and abs(float(_new[p][1]) - b) > 1e-9:''')

# after the 0.1.2 checks: the 0.1.4 table checks + the vanilla farming path
rep('''FUELS, CHARCOAL = fuel_list(MODEL, set(ids))
FIXED_BASE = dict((p[0], float(p[1])) for p in PRODUCTS if p[1] is not AUTO)
''', '''# ---- 0.1.4: the PRODUCTS rows carry the 0.1.4 defaults, and the crops follow the vanilla farming path
for _i, (_o, _n) in PRICE_014.items():
    assert _i in _new and _new[_i][1] is not AUTO and abs(float(_new[_i][1]) - _n) < 1e-9, "PRICE_014 %s: row %s" % (_i, _new.get(_i))
    assert abs(_o - _n) > 1e-9 and _i not in PROC, _i


def farming_path(data):
    """{crop: Farmingbench RequiredTierLevel of its normal seed recipe} from the item assets (1 when the recipe names no tier)"""
    out = {}
    for c in VANILLA_SEED_TIER:
        for sid, extra in (("Plant_Seeds_%s" % c, 0), ("Plant_Seeds_%s_Eternal" % c, 1)):
            r = (data.get(sid) or {}).get("Recipe") or {}
            br = r.get("BenchRequirement") or []
            br = [br] if isinstance(br, dict) else br
            t = [int(b.get("RequiredTierLevel") or 1) for b in br if isinstance(b, dict) and b.get("Id") == "Farmingbench"]
            if len(t) != 1:
                raise SystemExit("0.1.4 farming path: %s has no single Farmingbench recipe (%s) - Assets.zip changed?" % (sid, br))
            if extra == 0:
                out[c] = t[0]
            elif t[0] != out[c] + 1:
                raise SystemExit("0.1.4 farming path: %s is Farmingbench tier %d, not its seed's %d + 1" % (sid, t[0], out[c]))
    return out


def sapling_essence(data):
    """{sapling: Essence of Life count of its Recipe, own or inherited (None: another input)} from the item assets"""
    out = {}
    for sname in SAPLING_TIER:
        k, r, seen = "Plant_Sapling_%s" % sname, None, set()
        while k in data and k not in seen and r is None:          # a recipe inherited through Parent counts (Crystal, Poisoned: Oak's)
            seen.add(k)
            r = (data.get(k) or {}).get("Recipe")
            k = (data.get(k) or {}).get("Parent")
        ins = (r or {}).get("Input") or []
        e = [int(i.get("Quantity", 1) or 1) for i in ins if isinstance(i, dict) and i.get("ItemId") == "Ingredient_Life_Essence"]
        out[sname] = e[0] if (len(ins) == 1 and len(e) == 1) else None
    return out


_se = sapling_essence(DATA)
if _se != SAPLING_ESSENCE:
    raise SystemExit("0.1.4: the vanilla sapling recipes changed - %s, the table says %s" % (_se, SAPLING_ESSENCE))
for _s, _t in SAPLING_TIER.items():
    _i = "Plant_Sapling_%s" % _s
    _cap = None if _se[_s] is None else math.floor(0.6 * _se[_s] * 2 + 1e-9) / 2.0
    _old = PRICE_014[_i][0] if _i in PRICE_014 else float(_new[_i][1])
    _want = _old * 2 ** (_t - 1)
    assert float(_new[_i][1]) == (_want if _cap is None or _want <= _cap else _cap), (_i, _new[_i], _want, _cap)
_fp = farming_path(DATA)
if _fp != VANILLA_SEED_TIER:
    raise SystemExit("0.1.4: the vanilla farming path changed - Farmingbench seed tiers %s, the table says %s" % (_fp, VANILLA_SEED_TIER))
for _c, _vt in VANILLA_SEED_TIER.items():
    _t = PRICE_TIER[_vt]
    for _i, _want, _cap in (("Plant_Crop_%s_Item" % _c, CROP_PRICE[_t], None), ("Plant_Seeds_%s" % _c, SEED_PRICE[_t], SEED_CAP.get(_c)),
                            ("Plant_Seeds_%s_Eternal" % _c, ETERNAL_PRICE[_t], ETERNAL_CAP.get(_c))):
        _have = float(_new[_i][1])
        assert _have == (_want if _cap is None else _cap) and (_cap is None or _cap < _want), (_i, _have, _want, _cap)
print("0.1.4 farming path (Farmingbench seed tiers, Assets.zip): " + ", ".join("%s %d" % (c, t) for c, t in sorted(_fp.items(), key=lambda x: (x[1], x[0]))))
FUELS, CHARCOAL = fuel_list(MODEL, set(ids))
FIXED_BASE = dict((p[0], float(p[1])) for p in PRODUCTS if p[1] is not AUTO)
''')

# ---- loop_check: an optional margins list (the tightest recipes for the build output); behaviour unchanged without it
rep('''def loop_check(M, prices, spread):''', '''def loop_check(M, prices, spread, margins=None):''')
rep('''        v = worth(outs)
        if v > tot + 1e-9:
            loops.append((v / tot if tot > 0 else INF, name, ins, outs, fuel_s))
    return loops, costable, len(recipes), passes''', '''        v = worth(outs)
        if v > tot + 1e-9:
            loops.append((v / tot if tot > 0 else INF, name, ins, outs, fuel_s))
        if margins is not None and tot > 0 and v > 0:
            margins.append((v / tot, name, ins, outs, fuel_s))
    return loops, costable, len(recipes), passes''')

# ---- 0.1.4: the SET jars' recipes on top of the vanilla ones + the tightest margins
rep('''print("loop check: no money loop at any premium %d-%d%%" % (PREMIUM_MIN, PREMIUM_MAX))
''', '''print("loop check: no money loop at any premium %d-%d%%" % (PREMIUM_MIN, PREMIUM_MAX))


def set_jars():
    """[(mod, version, jar path)] of the tools/deploy_set.py SET (read as a literal, never imported); SkyyBazaar itself is skipped"""
    t = ast.parse(open(os.path.join(HERE, "..", "tools", "deploy_set.py"), encoding="utf8").read())
    for n in t.body:
        if isinstance(n, ast.Assign) and any(getattr(x, "id", "") == "SET" for x in n.targets):
            out = []
            for mod, ver in ast.literal_eval(n.value):
                if mod == "SkyyBazaar":
                    continue
                jp = os.path.normpath(os.path.join(HERE, "..", mod, "%s-%s.jar" % (mod, ver)))
                if not os.path.exists(jp):
                    raise SystemExit("0.1.4 SET recipe scan: %s %s is not built (%s)" % (mod, ver, jp))
                out.append((mod, ver, jp))
            return out
    raise SystemExit("tools/deploy_set.py has no SET")


def set_model(M, data):
    """MODEL + every SET jar's Server/Item/Items (their Recipe, through Parent into vanilla too) and Server/Item/Recipes, and the jar
    items' resource types - added, never replacing a vanilla recipe or membership (the union can only make the check stricter)"""
    recipes = list(M["recipes"])
    rt_items = collections.defaultdict(list)
    for k, v in M["rt_items"].items():
        rt_items[k] = list(v)
    per_mod = []
    for mod, ver, jp in set_jars():
        z = zipfile.ZipFile(jp)
        items, recs = {}, []
        for n in z.namelist():
            if n.endswith(".json") and n.startswith("Server/Item/Items/"):
                try:
                    items[n.rsplit("/", 1)[1][:-5]] = json.loads(z.read(n).decode("utf-8-sig"))
                except Exception:
                    raise SystemExit("0.1.4 SET recipe scan: %s %s is not JSON" % (mod, n))
            elif n.endswith(".json") and n.startswith("Server/Item/Recipes/"):
                try:
                    recs.append((n, json.loads(z.read(n).decode("utf-8-sig"))))
                except Exception:
                    raise SystemExit("0.1.4 SET recipe scan: %s %s is not JSON" % (mod, n))
        before = len(recipes)
        jm = None
        if items:
            merged = dict(data)
            merged.update(items)
            jm = asset_model(None, merged, None, [])
        for r in (jm["recipes"] if jm else []):
            if r[0] in items:
                recipes.append(("%s:%s" % (mod, r[0]), r[1], r[2], r[3], r[4]))
        for n, d in recs:
            outs = [(o["ItemId"], o.get("Quantity", 1) or 1) for o in (d.get("Output") or ([d["PrimaryOutput"]] if d.get("PrimaryOutput") else []))
                    if isinstance(o, dict) and o.get("ItemId")]
            ins = []
            for i in d.get("Input") or []:
                if isinstance(i, dict) and i.get("ItemId"):
                    ins.append(("I", i["ItemId"], i.get("Quantity", 1) or 1))
                elif isinstance(i, dict) and i.get("ResourceTypeId"):
                    ins.append(("R", i["ResourceTypeId"], i.get("Quantity", 1) or 1))
            br = d.get("BenchRequirement") or []
            br = [br] if isinstance(br, dict) else br
            if ins and outs:
                recipes.append(("%s:%s" % (mod, n), ins, outs, [(b.get("Type"), b.get("Id")) for b in br if isinstance(b, dict)], d.get("TimeSeconds")))
        for k in (items if jm else ()):
            for r in jm["rtypes"](k):
                if k not in rt_items[r]:
                    rt_items[r].append(k)
        per_mod.append((mod, len(items), len(recipes) - before))
    return {"inh": M["inh"], "rtypes": M["rtypes"], "rt_items": rt_items, "recipes": recipes, "benches": M["benches"],
            "fuels": M["fuels"]}, per_mod


SET_MODEL, SET_SCAN = set_model(MODEL, DATA)
_extra = [(m, i, r) for m, i, r in SET_SCAN if i or r]
for _prem in range(PREMIUM_MIN, PREMIUM_MAX + 1):
    _loops = loop_check(SET_MODEL, all_prices(_prem / 100.0), SPREAD)[0]
    if _loops:
        for ratio, name, ins, outs, fuel_s in sorted(_loops, reverse=True)[:30]:
            print("MONEY LOOP (SET jars) x%.3f  %s  in=%s -> out=%s fuel=%.1fs" % (ratio, name, ins, outs, fuel_s))
        raise SystemExit("%d money loops through the SET jars' recipes at premium %d%%" % (len(_loops), _prem))
print("0.1.4 SET recipe scan: %d jars, items / recipes added: %s; %d recipes in all - no money loop at any premium %d-%d%%"
      % (len(SET_SCAN), ", ".join("%s %d/%d" % e for e in _extra), len(SET_MODEL["recipes"]), PREMIUM_MIN, PREMIUM_MAX))
def tight(prem, n=10):
    """the n recipes closest to paying at this premium (liquidated outputs / cheapest inputs, 1.0 = a loop), processing recipes of the
    AUTO goods (and fuel burns) left out - those sit at (1 + premium) x 0.9 / 1.1 by construction"""
    got = []
    loop_check(SET_MODEL, all_prices(prem / 100.0), SPREAD, got)
    bound = (1 + prem / 100.0) * (1 - SPREAD) / (1 + SPREAD)
    seen, top, at = set(), [], set()
    for r, nm, ins, outs, fs in sorted(got, key=lambda x: -x[0]):
        if nm in seen or all(o in PROC for o, q in outs):
            continue
        seen.add(nm)
        if r >= bound - 1e-6:
            at.add(nm)          # liquidated through a processing step (burn to charcoal, smelt, tan, weave): the premium bound
            continue
        top.append((r, nm))
        if len(top) >= n:
            break
    return top, len(at)


MARGINS = dict((p, tight(p)) for p in (PREMIUM_DEF, PREMIUM_MAX))
for _p, (_top, _at) in sorted(MARGINS.items()):
    print("tightest recipes at premium %d%% (outputs liquidated / inputs at their cheapest; 1.0 = a loop; %d recipes sit at the processing "
          "bound %.4f): %s" % (_p, _at, (1 + _p / 100.0) * (1 - SPREAD) / (1 + SPREAD),
                               "; ".join("%s %.4f" % (n.replace("Server/Item/Recipes/", "").replace(".json", ""), r) for r, n in _top)))
''')

# ================================================================================================================ Java: the one-time update
rep('''cat_.addField(CtField.make('public static volatile String MIGRATED = "";', cat_))''',
    '''cat_.addField(CtField.make('public static volatile String MIGRATED = "";', cat_))
# 0.1.4: the one-time progression price update (migrate14): ids, 0.1.3 defaults, 0.1.4 defaults (seed spelling) + its marker
_m14 = sorted(PRICE_014)
cat_.addField(CtField.make("public static final String[] M14_ID = %s;" % jarr(_m14), cat_))
cat_.addField(CtField.make("public static final double[] M14_OLD = new double[] { %s };" % ", ".join(repr(float(PRICE_014[i][0])) for i in _m14), cat_))
cat_.addField(CtField.make("public static final double[] M14_NEW = new double[] { %s };" % ", ".join(repr(float(PRICE_014[i][1])) for i in _m14), cat_))
cat_.addField(CtField.make("public static final String[] M14_TXT = %s;" % jarr(["%g" % PRICE_014[i][1] for i in _m14]), cat_))
cat_.addField(CtField.make("public static final String[] M14_OTXT = %s;" % jarr(["%g" % PRICE_014[i][0] for i in _m14]), cat_))
cat_.addField(CtField.make('public static volatile String MIGRATED14 = "";', cat_))
cat_.addField(CtField.make("public static final java.util.ArrayList M14_LOG = new java.util.ArrayList();", cat_))
assert all(float(t) == PRICE_014[i][1] for i, t in zip(_m14, ["%g" % PRICE_014[i][1] for i in _m14]))''')
rep('''  if (stamp != null && stamp.length() > 0) {
    sb.append("# the one-time update to 0.1.3 is done (remove this line only to run it again)\\n");
    sb.append("migrated.0.1.3=").append(stamp).append('\\n');
  }''', '''  if (stamp != null && stamp.length() > 0) {
    sb.append("# the one-time update to 0.1.3 is done (remove this line only to run it again)\\n");
    sb.append("migrated.0.1.3=").append(stamp).append('\\n');
  }
  if (MIGRATED14 != null && MIGRATED14.length() > 0) {
    sb.append("# the one-time 0.1.4 progression price update is done (remove this line only to run it again)\\n");
    sb.append("migrated.0.1.4=").append(MIGRATED14).append('\\n');
  }''')
rep('''  String mg = pp.getProperty("migrated.0.1.3");
  if (mg != null && mg.trim().length() > 0) MIGRATED = mg.trim();
}"""), cat_))''', '''  String mg = pp.getProperty("migrated.0.1.3");
  if (mg != null && mg.trim().length() > 0) MIGRATED = mg.trim();
  String mg14 = pp.getProperty("migrated.0.1.4");
  if (mg14 != null && mg14.trim().length() > 0) MIGRATED14 = mg14.trim();
}"""), cat_))''')

MIG14 = r'''
# ---- 0.1.4: THE ONE-TIME PROGRESSION PRICE UPDATE (PROJECT-RULES one-time migrations). Runs after migrate() (0.1.3; it must have marked
# migrated.0.1.3) while pricing.properties has no migrated.0.1.4. A product line (first one of its id that load() would read; peek =
# parse's rules) whose price is EXACTLY its 0.1.3 default (M14_OLD, numerically) gets M14_TXT in place of the price text only; a price
# that is not the 0.1.3 default is kept and logged; everything else (other lines, comments, spacing, each line ending, a missing final
# newline) stays byte for byte. Before products.properties is written its bytes go to config-history/ (read back + compared - a
# mismatch throws, nothing changes). products.properties first, the marker last (appended to pricing.properties, its bytes kept), so a
# failed step changes nothing it cannot redo. The trades.log lines wait in M14_LOG (setup writes them after Market.load).
cat_.addMethod(CtNewMethod.make(jt(r"""
public static int m14(String id) {
  if (id == null) return -1;
  for (int i = 0; i < M14_ID.length; i++) if (M14_ID[i].equals(id)) return i;
  return -1;
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static String withPrice(String body, String np) {
  int eq = body.indexOf('=');
  if (eq < 0) return null;
  int c1 = body.indexOf(',', eq + 1);
  if (c1 < 0) return null;
  int c2 = body.indexOf(',', c1 + 1);
  int end = c2 < 0 ? body.length() : c2;
  String tok = body.substring(c1 + 1, end);
  int a = 0;
  while (a < tok.length() && Character.isWhitespace(tok.charAt(a))) a++;
  int b = tok.length();
  while (b > a && Character.isWhitespace(tok.charAt(b - 1))) b--;
  return body.substring(0, c1 + 1) + tok.substring(0, a) + np + tok.substring(b) + body.substring(end);
}"""), cat_))
cat_.addMethod(CtNewMethod.make(jt(r"""
public static synchronized String migrate14() {
  init();
  M14_LOG.clear();
  try {
    if (PFILE == null || FILE == null || !java.nio.file.Files.exists(PFILE, new java.nio.file.LinkOption[0])) return null;
    byte[] praw = java.nio.file.Files.readAllBytes(PFILE);
    java.util.Properties pp = new java.util.Properties();
    pp.load(new java.io.ByteArrayInputStream(praw));
    String m13 = pp.getProperty("migrated.0.1.3");
    if (m13 == null || m13.trim().length() == 0) return null;
    String done = pp.getProperty("migrated.0.1.4");
    if (done != null && done.trim().length() > 0) { MIGRATED14 = done.trim(); return null; }
    int rewrote = 0;
    int already = 0;
    java.util.ArrayList kept = new java.util.ArrayList();
    java.util.ArrayList lines = new java.util.ArrayList();
    StringBuilder ex = new StringBuilder();
    String backup = "";
    if (java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      byte[] raw = java.nio.file.Files.readAllBytes(FILE);
      String txt = new String(raw, java.nio.charset.StandardCharsets.UTF_8);
      if (!java.util.Arrays.equals(txt.getBytes(java.nio.charset.StandardCharsets.UTF_8), raw)) throw new java.io.IOException("products.properties is not plain UTF-8 - left as it is");
      String[] ls = txt.split("\n", -1);
      StringBuilder sb = new StringBuilder(txt.length() + 64);
      java.util.HashSet have = new java.util.HashSet();
      for (int i = 0; i < ls.length; i++) {
        String ln = ls[i];
        boolean cr = ln.endsWith("\r");
        String body = cr ? ln.substring(0, ln.length() - 1) : ln;
        String out = body;
        @PKG@.Product p = peek(body);
        if (p != null && !have.contains(p.id)) {
          have.add(p.id);
          int k = m14(p.id);
          if (k >= 0) {
            if (Math.abs(p.base - M14_OLD[k]) < 1.0E-9) {
              String nb = withPrice(body, M14_TXT[k]);
              @PKG@.Product q = peek(nb);
              if (nb != null && q != null && q.id.equals(p.id) && q.cat.equals(p.cat) && q.name.equals(p.name) && Math.abs(q.base - M14_NEW[k]) < 1.0E-9) {
                out = nb;
                rewrote++;
                lines.add("MIGRATE-0.1.4 PRICE " + p.id + " " + M14_OTXT[k] + " -> " + M14_TXT[k] + " (undo: /bazaaradmin price " + p.id + " " + M14_OTXT[k] + ")");
                if (rewrote <= 4) { if (ex.length() > 0) ex.append(", "); ex.append(p.name).append(' ').append(M14_OTXT[k]).append(" -> ").append(M14_TXT[k]); }
              } else {
                kept.add(p.id);
                lines.add("MIGRATE-0.1.4 KEPT " + p.id + " " + @PKG@.BzUtil.num(p.base) + " (the line could not be rewritten safely; the 0.1.4 default is " + M14_TXT[k] + ")");
              }
            } else if (Math.abs(p.base - M14_NEW[k]) < 1.0E-9) {
              already++;
            } else {
              kept.add(p.id + " " + @PKG@.BzUtil.num(p.base));
              lines.add("MIGRATE-0.1.4 KEPT " + p.id + " " + @PKG@.BzUtil.num(p.base) + " (your price; the 0.1.3 default was " + M14_OTXT[k] + ", the 0.1.4 default is " + M14_TXT[k] + ")");
            }
          }
        }
        sb.append(out);
        if (i < ls.length - 1) sb.append(cr ? "\r\n" : "\n");
        else if (cr) sb.append('\r');
      }
      if (rewrote > 0) {
        java.nio.file.Path hd = FILE.toAbsolutePath().getParent().resolve("config-history");
        java.nio.file.Files.createDirectories(hd, new java.nio.file.attribute.FileAttribute[0]);
        java.time.format.DateTimeFormatter fm = java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd-HHmmss-SSS");
        java.time.LocalDateTime t0 = java.time.LocalDateTime.now();
        java.nio.file.Path bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0) + ".bak");
        int g = 0;
        while (java.nio.file.Files.exists(bak, new java.nio.file.LinkOption[0]) && g < 1000) {
          g++;
          bak = hd.resolve("Skyy_SkyyBazaar~products.properties." + fm.format(t0.plusNanos(1000000L * g)) + ".bak");
        }
        atomicWrite(bak, raw);
        byte[] back = java.nio.file.Files.readAllBytes(bak);
        if (!java.util.Arrays.equals(back, raw)) throw new java.io.IOException("the history copy " + bak + " does not match products.properties - nothing changed");
        backup = "config-history/" + bak.getFileName().toString();
        atomicWrite(FILE, sb.toString().getBytes(java.nio.charset.StandardCharsets.UTF_8));
      }
    }
    String stamp = java.time.Instant.now().toString();
    String ptxt = new String(praw, "ISO-8859-1");
    String pnl = ptxt.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    StringBuilder pb = new StringBuilder(ptxt);
    if (ptxt.length() > 0 && !ptxt.endsWith("\n")) pb.append(pnl);
    pb.append("# the one-time 0.1.4 progression price update is done (remove this line only to run it again)").append(pnl);
    pb.append("migrated.0.1.4=").append(stamp).append(pnl);
    atomicWrite(PFILE, pb.toString().getBytes("ISO-8859-1"));
    MIGRATED14 = stamp;
    String head = "MIGRATE-0.1.4 rewrote " + rewrote + " kept " + kept.size() + " already " + already + (backup.length() > 0 ? " backup " + backup : "");
    M14_LOG.add(head);
    M14_LOG.addAll(lines);
    String msg = "one-time 0.1.4 progression price update (Skyy 2026-10-04: x2 per tier step): " + rewrote + " default prices updated"
               + (ex.length() > 0 ? " (" + ex + (rewrote > 4 ? ", ..." : "") + ")" : "")
               + (kept.isEmpty() ? "" : ", your own prices kept for " + kept)
               + (already > 0 ? ", " + already + " already at the 0.1.4 price" : "")
               + (backup.length() > 0 ? "; the old file is " + backup + ", every change + its undo command is in trades.log" : "");
    @PKG@.BzUtil.info(msg);
    return head;
  } catch (Throwable t) {
    M14_LOG.clear();
    @PKG@.BzUtil.warn("the one-time 0.1.4 price update of products.properties failed (" + t + ") - nothing was marked done; it runs again at the next start");
    return null;
  }
}"""), cat_))
'''
rep('''# the raw-input value of a processed good: inputs (qty x the cheapest listed product of each input) + fuel (seconds x the cheapest''',
    MIG14.lstrip("\n") + '''# the raw-input value of a processed good: inputs (qty x the cheapest listed product of each input) + fuel (seconds x the cheapest''')
rep('''  String mig = @PKG@.Catalog.migrate();
  int n = @PKG@.Catalog.load();''', '''  String mig = @PKG@.Catalog.migrate();
  String mig14 = @PKG@.Catalog.migrate14();
  int n = @PKG@.Catalog.load();''')
rep('''  if (mig != null) @PKG@.Market.log(mig);''', '''  if (mig != null) @PKG@.Market.log(mig);
  if (mig14 != null) { for (int i = 0; i < @PKG@.Catalog.M14_LOG.size(); i++) @PKG@.Market.log((String) @PKG@.Catalog.M14_LOG.get(i)); }
  @PKG@.Catalog.M14_LOG.clear();''')

# ---- isDefault also knows the 0.1.3 seed lines: 0.1.3's update re-run (its marker lost) must not take a 0.1.3 default line - e.g. a
#      bar at its 0.1.3 auto price - for a hand edit and make it FIXED; it moves such a line to its 0.1.4 seed line instead
rep('''OLD_SEED_LINES = ["%s=%s,%s,%s" % (p, c, ("%g" % b), n) for p, c, b, n in PRODUCTS_012]
''', '''OLD_SEED_LINES = ["%s=%s,%s,%s" % (p, c, ("%g" % b), n) for p, c, b, n in PRODUCTS_012]
# 0.1.4: the 0.1.3 seed lines (0.1.3 fixed prices = PRICE_014's old values, its auto prices at the default premium from them)
_fb013 = dict(FIXED_BASE)
_fb013.update((_i, float(_o)) for _i, (_o, _n) in PRICE_014.items())
_auto013 = auto_prices(_fb013, PROC, FUELS, CHARCOAL, PREMIUM_DEF / 100.0)
SEED013_LINES = ["%s=%s,%s,%s" % (pid, BAG_OF[pid], "%g" % (_auto013[pid] if base is AUTO else _fb013[pid]), name) for pid, base, name in PRODUCTS]
assert sum(1 for a, b in zip(SEED013_LINES, SEED_LINES) if a != b) >= len(PRICE_014)
''')
rep('''cat_.addField(CtField.make("public static final String[] OLD_SEED = %s;" % jarr(OLD_SEED_LINES), cat_))''',
    '''cat_.addField(CtField.make("public static final String[] OLD_SEED = %s;" % jarr(OLD_SEED_LINES), cat_))
cat_.addField(CtField.make("public static final String[] SEED013 = %s;" % jarr(SEED013_LINES), cat_))''')
rep('''  if (sameLine(p, peek(seedLine(p.id)))) return true;
  for (int i = 0; i < OLD_SEED.length; i++) {''', '''  if (sameLine(p, peek(seedLine(p.id)))) return true;
  for (int i = 0; i < SEED013.length; i++) {
    @PKG@.Product q0 = peek(SEED013[i]);
    if (q0 != null && q0.id.equals(p.id) && sameLine(p, q0)) return true;
  }
  for (int i = 0; i < OLD_SEED.length; i++) {''')

# ================================================================================================================ checks on the result
for kb in KEEP:
    assert kb in s, "a block that must stay 0.1.3's changed: %s" % kb[:90]
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert "@@" not in s
assert s.count('VERSION = "0.1.4"') == 1
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst, len(s.split(LF)), "lines; %d default prices change:" % len(CHANGED))
for _fam, _rows in FAMILIES:
    print("  %-52s %s" % (_fam, ", ".join("%s %s->%s" % (i.replace("Ingredient_", "").replace("Plant_", "").replace("_Trunk", "").replace("_Item", ""),
                                                         _num(CHANGED[i][0]), _num(CHANGED[i][1])) for i, _o, _n in _rows if i in CHANGED)))
