"""skyyeggs - THE PET EGG TABLE (research/Pet-Eggs-Spec.md, round R1 = SkyyPets 0.4.0). ONE source of truth for every jar that knows
the pet eggs (the tools/skyyench.py idea):

    SkyyPets 0.4.0+          ships the 30 egg items (item JSON + recipe, the Skyy_Pet_Mythic quality, icons, world textures, lang),
                             the two-roll hatch (roll 1 = which pet, roll 2 = its rarity), the drop roll behind pets:fn:eggroll and the
                             Server Setup > Pets > Eggs / Egg drops rows whose DEFAULTS are below
    SkyyBazaar (R3)          a product per egg: Common / Uncommon = AUTO (a processed good from RECIPES), Rare / Epic = BAZAAR_BASE,
                             Legendary / Mythic never; its build loop check also reads RECIPES (recipe_inputs)
    SkyyMerchants (R3)       the Legendary rows MERCHANT_ROWS (>= MERCHANT_MIN_X x any Bazaar base of that egg)
    SkyyCollections (R4)     the reward tokens COLLECTION_EGGS

Skyy's words this follows (docs/answered/pets.md, word for word there):
  - 2026-10-15 "i want eggs. hatching with an animation where it rolls, and chooses what pet you get, then a second roll for the rarity
    ... there are mining eggs, farming eggs, combat eggs and so on. pets pets arnt tiered, but generally ordered from best to worst in each
    category. when hatching an egg, you have a high chance to ghet a bad pet, and a low chance to get a good one. same for rarity commons
    are common, legendry's are extremely rare."
  - popups: "eggs come in rarities from common to mythic. the better the egg the higher the chance of better pets. a legendary egg will
    always give an above average pet, and never below rare." / hatch rarities "Common to Mythic" / "Spinning reel, ~3 s each roll"
  - 2026-10-10 "Eggs trade, pets don't": an egg is a plain item (no metadata) - Bazaar / Auction House / merchants; a hatched pet is a
    bound record.

Rules kept here (the build scripts assert them; tools/test_skyyeggs.py is not needed - SkyyPets' harness executes every number):
  - Ids / MaxStack / recipes are BUILD-TIME (baked into item JSON); every weight / order / chance is a Server Setup DEFAULT.
  - Rare and up are never craftable; no egg combining (fusing is for pets); no reverse recipe.
  - Every rarity row sums to 10,000; Legendary / Mythic hatch rows never hold a Common / Uncommon weight ("never below rare").
  - Pure Python, no imports beyond the standard library (SkyyBazaar / SkyyMerchants / SkyyCollections import it too).
"""

EGGS_VERSION = "1"            # bump when an id, a recipe or the bridge format changes
PREFIX = "Skyy_PetEgg_"
CATEGORIES = ("Mining", "Farming", "Foraging", "Combat", "Exploration")      # Fishing later (spec 2.3 / R5): no Fishing pets yet
RARITIES = ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic")
MAX_STACK = 25                # = vanilla Food_Egg (Skyy: "use Hytale stack numbers")
MYTHIC_QUALITY = "Skyy_Pet_Mythic"
MYTHIC_COLOR = "#cc66cc"      # = skyyui RARITY["Mythic"] (the art's gem colour)
MYTHIC_VALUE = 6              # above vanilla Legendary (5), below SkyyAuctions' technical threshold (8)
QUALITY = {"Common": "Common", "Uncommon": "Uncommon", "Rare": "Rare", "Epic": "Epic", "Legendary": "Legendary", "Mythic": MYTHIC_QUALITY}
ICON_DIR = "Icons/ItemsGenerated"                # under Common/ (the art: art/pet-eggs/Common/Icons/ItemsGenerated/<id>.png)
TEXTURE_DIR = "Items/Pets"                       # under Common/: Skyy_PetEgg_<Rarity>_Texture.png (one per rarity)
# Skyy 2026-10-16 "can you make the held item texture look more round?": our OWN round model (tools/art/pet_egg_model.py, generated into
# the jar at build time) replaces the vanilla one-box egg; its anchor nodes match the vanilla egg's (VANILLA_EGG_MODEL, numbers checked)
EGG_MODEL = "Items/Pets/Skyy_PetEgg.blockymodel"
VANILLA_EGG_MODEL = "Items/Consumables/Food/Egg.blockymodel"
ART_DIR = "art/pet-eggs"

# ---------------------------------------------------------------------------------------------------------------- ids, names, flavor
def egg_id(cat, rar):
    assert cat in CATEGORIES and rar in RARITIES, (cat, rar)
    return PREFIX + cat + "_" + rar


IDS = [egg_id(c, r) for c in CATEGORIES for r in RARITIES]


def name(cat, rar):
    return "%s %s Egg" % (rar, cat)


def tier_tag(rar):
    """the standing tier-tag rule (research/Tier-Tags-Plan.md): the rarity + noun FIRST in the flavor text - "Rare Egg" (no T-number: the
    T1-T8 ladder is the metal ladder)"""
    return "%s Egg" % rar


def flavor(cat, rar):
    return "%s - Right-click to hatch a random %s pet. Better eggs give better pets." % (tier_tag(rar), cat)


def parse_id(item_id):
    """'Skyy_PetEgg_Mining_Rare' -> ('Mining', 'Rare'); None for anything else"""
    if not isinstance(item_id, str) or not item_id.startswith(PREFIX):
        return None
    p = item_id[len(PREFIX):].split("_")
    if len(p) != 2 or p[0] not in CATEGORIES or p[1] not in RARITIES:
        return None
    return p[0], p[1]


# ---------------------------------------------------------------------------------------------------------------- roll 1: which pet
# Default best -> worst order per category (SkyyPets 0.4.3 roster adds included; spec 2.2 = SkyyPets 0.3.1 Pet kinds, ordered by start rarity, summonable first, home zone,
# main stat, table order). Server Setup row pets.egg.order.<category> (comma list); a kind in no list is placed by its start rarity.
ORDER = {
    "Mining": ["CrystalGolem", "Goat", "Warthog", "Molerat", "Meerkat", "Mouse"],
    "Farming": ["Mosshorn", "Bison", "Rabbit", "Bunny", "Chicken", "Corgi", "Frog"],
    "Foraging": ["Bear", "Moose", "Turkey", "Owl", "Cat", "Squirrel"],
    "Exploration": ["Camel", "Horse", "Antelope", "Deer", "Gecko", "Rat"],
    "Combat": ["Ram", "Skrill", "VoidEye", "Hawk", "Mouflon", "VoidCrawler", "Wolf", "Tusker", "Skeleton", "SkeletonKnight", "VoidLarva",
               "Boar", "Fox", "Dog"],
}
# R = how many times likelier the pool's worst pet is than its best (row pets.egg.ratio.<rarity>); pool = all / the best half (min 1)
RATIO = {"Common": 16.0, "Uncommon": 8.0, "Rare": 4.0, "Epic": 2.0, "Legendary": 2.0, "Mythic": 0.5}
POOL = {"Common": "all", "Uncommon": "all", "Rare": "all", "Epic": "all", "Legendary": "half", "Mythic": "half"}


def pool_size(n, pool):
    if n <= 0:
        return 0
    return n if pool == "all" else max(1, n // 2)


def weights(n, ratio, pool):
    """weight per pet, BEST FIRST (rank 1 = best), for a category list of n kinds: the pool keeps the best pool_size(n) pets; inside it
    weight = R ^ (-x), x = 0 for the pool's worst, 1 for its best (x = position / (pool size - 1)); pets outside the pool = 0"""
    m = pool_size(n, pool)
    out = []
    for i in range(n):
        if i >= m:
            out.append(0.0)
            continue
        x = 1.0 if m == 1 else (m - 1 - i) / float(m - 1)
        out.append(ratio ** (-x))
    return out


def percents(n, rar):
    w = weights(n, RATIO[rar], POOL[rar])
    t = sum(w)
    return [100.0 * x / t for x in w]


# ---------------------------------------------------------------------------------------------------------------- roll 2: the rarity
# per 10,000, Common / Uncommon / Rare / Epic / Legendary / Mythic (row pets.egg.rarity.<eggRarity>, written C/U/R/E/L/M)
RARITY_W = {
    "Common": (7000, 2300, 600, 90, 9, 1),
    "Uncommon": (5000, 3500, 1200, 270, 27, 3),
    "Rare": (3000, 4000, 2300, 600, 90, 10),
    "Epic": (1000, 3500, 3800, 1400, 250, 50),
    "Legendary": (0, 0, 6500, 2800, 600, 100),
    "Mythic": (0, 0, 0, 6500, 2800, 700),
}
NEVER_BELOW_RARE = ("Legendary", "Mythic")       # Skyy: "a legendary egg will always give an above average pet, and never below rare"


def rarity_text(w):
    return "/".join(str(int(x)) for x in w)


# ---------------------------------------------------------------------------------------------------------------- drops (pets:fn:eggroll)
# 1 in N per natural action (rows pets.egg.drop.<source>); luck x (1 + min(Fortune, cap) x pct %); cap per profile per real hour
DROP_N = {"mining": 5000, "foraging": 5000, "farming": 5000, "combat": 2500, "exploration": 150, "fishing": 300}
DROP_SOURCES = ("mining", "foraging", "farming", "combat", "exploration", "fishing")
DROP_CAT = {"mining": "Mining", "foraging": "Foraging", "farming": "Farming", "combat": "Combat", "exploration": "Exploration",
            "fishing": None}
DROP_LOW = (7500, 2000, 450, 45, 5, 0)          # tier < HIGH_TIER (row pets.egg.drop.rarityLow), per 10,000
DROP_HIGH = (5500, 3000, 1200, 250, 45, 5)      # tier >= HIGH_TIER (row pets.egg.drop.rarityHigh)
HIGH_TIER = 4
FORTUNE_PCT = 25.0
FORTUNE_CAP = 2.0
CAP_PER_HOUR = 3

# ---------------------------------------------------------------------------------------------------------------- the hatch page
REEL_SECONDS = 3.0
REEL1_MS = (60, 60, 70, 80, 90, 110, 130, 160, 190, 230, 280, 340, 410, 500)       # 14 frames, 2.71 s (+ 0.4 s hold)
REEL2_MS = (70, 80, 90, 110, 130, 160, 200, 250, 310, 380, 460, 550)               # 12 frames, 2.79 s (+ 0.4 s hold)
HOLD_MS = 400

# ---------------------------------------------------------------------------------------------------------------- recipes (Common + Uncommon only)
# 1 Food_Egg + ...; Skyy_Ench_<Key> = SkyyCollections' Enchanted materials (tools/skyyench.py). BENCH = the spec 6.3 fallback: the
# Farmingbench's existing Farming category (an own Workbench tab "Pet Eggs" through the skyyench runtime tab protocol is UNVERIFIED for a
# second mod - a later round)
BENCH_ID = "Farmingbench"
BENCH_CATEGORY = "Farming"
BASE_EGG = "Food_Egg"
RECIPES = {
    ("Mining", "Common"): [("Skyy_Ench_Cobblestone", 12)],
    ("Mining", "Uncommon"): [("Skyy_Ench_Iron", 2)],
    ("Foraging", "Common"): [("Skyy_Ench_Oak", 4)],
    ("Foraging", "Uncommon"): [("Skyy_Ench_Maple", 6)],
    ("Farming", "Common"): [("Skyy_Ench_Wheat", 6)],
    ("Farming", "Uncommon"): [("Skyy_Ench_Wheat", 12), ("Skyy_Ench_Carrot", 12)],
    ("Combat", "Common"): [("Ingredient_Bone_Fragment", 128), ("Ingredient_Leather_Light", 16)],
    ("Combat", "Uncommon"): [("Skyy_Ench_Iron", 2), ("Ingredient_Bone_Fragment", 128)],
    ("Exploration", "Common"): [("Skyy_Ench_Oak", 2), ("Skyy_Ench_Cobblestone", 6)],
    ("Exploration", "Uncommon"): [("Skyy_Ench_Oak", 6), ("Skyy_Ench_Copper", 2)],
}
CRAFTABLE = ("Common", "Uncommon")


def recipe_inputs(cat, rar):
    """[(item id, qty)] including the vanilla egg, or None (not craftable)"""
    r = RECIPES.get((cat, rar))
    return None if r is None else [(BASE_EGG, 1)] + list(r)


def recipe_id(cat, rar):
    return egg_id(cat, rar) + "_Recipe_Generated_0"


# ---------------------------------------------------------------------------------------------------------------- economy (R3 / R4 read these)
BAZAAR = {"Common": "AUTO", "Uncommon": "AUTO", "Rare": 25000, "Epic": 100000}     # Legendary / Mythic: never on the Bazaar
MERCHANT_ROWS = [("pet." + egg_id(c, "Legendary"), egg_id(c, "Legendary"), 600000, 1, (3, 4, 5)) for c in CATEGORIES]   # (row, id, price, stock, zones)
MERCHANT_PER_VISIT = 1
MERCHANT_CHANCE = 25
MERCHANT_MIN_X = 4.0          # a merchant row for a Bazaar-listed egg must be >= 4 x its base (the Bazaar pays at most 4.0 x 0.9)
COLLECTION_EGGS = {"III": "Common", "V": "Uncommon", "last": "Rare", "last_flagship": "Epic"}
COLLECTION_FLAGSHIPS = ("Wheat", "OakLog", "Cobblestone", "BoneFragment")

# ---------------------------------------------------------------------------------------------------------------- DRAGON EGGS (SkyyPets 0.4.11)
# research/Dragon-Pet-Spec.md section 2 (+ docs/answered/pets.md 2026-10-18 DRAGON PET DESIGN: "hatches in the hatchery"). A dragon egg
# hatches ONE fixed dragon kind (no roll 1) at a rarity from DRAGON_RARITY_W (roll 2, never below Rare). Dragon eggs are NOT in IDS /
# ORDER / RECIPES / BAZAAR / MERCHANT_ROWS / COLLECTION_EGGS: never craftable, never fused, never from egg drops, never on the Bazaar
# (the Auction House may list them - they are plain items). Ids are BUILD-TIME; Server Setup > Pets > Dragons (pets.dragon.eggs) may drop
# or remap them. The two Nestkeeper eggs are Aures' own items (Dragon Nestkeeper, PACK.md): used BY ID at runtime only - their files are
# never copied; holding one in your hand still hatches Aures' wild dragon (their feature, kept).
# (egg item id, dragon kind, name, owner mod, admin word)
DRAGON_EGGS = [
    ("Dragon_Egg_Plain", "DragonPlain", "Plain Dragon Egg", "Nestkeeper", "plain"),
    ("Dragon_Egg_Tundra", "DragonTundra", "Tundra Dragon Egg", "Nestkeeper", "tundra"),
    ("Skyy_PetEgg_Dragon_Fire", "DragonFire", "Fire Dragon Egg", "SkyyPets", "fire"),
    ("Skyy_PetEgg_Dragon_Thunder", "DragonStorm", "Storm Dragon Egg", "SkyyPets", "thunder"),
    ("Skyy_PetEgg_Dragon_Air", "DragonSky", "Sky Dragon Egg", "SkyyPets", "air"),
]
DRAGON_EGG_IDS = [e[0] for e in DRAGON_EGGS]
DRAGON_RARITY_W = (0, 0, 6000, 3000, 900, 100)     # C/U/R/E/L/M per 10,000: never below Rare, Mythic 1 % (spec 2, question 7 default)
DRAGON_HATCH_SECONDS = 3600                        # 1 h (spec 2, question 7 default)


def _dragon_checks():
    assert len(DRAGON_EGG_IDS) == len(set(DRAGON_EGG_IDS)) == 5 and not set(DRAGON_EGG_IDS) & set(IDS)
    assert all(parse_id(i) is None for i in DRAGON_EGG_IDS), "a dragon egg id must never parse as a category egg"
    assert len(set(e[1] for e in DRAGON_EGGS)) == len(DRAGON_EGGS) and all(e[1].startswith("Dragon") for e in DRAGON_EGGS)
    assert all(len(e[2]) <= 40 and e[3] in ("Nestkeeper", "SkyyPets") and e[4].isalpha() for e in DRAGON_EGGS)
    assert sum(DRAGON_RARITY_W) == 10000 and DRAGON_RARITY_W[0] == 0 and DRAGON_RARITY_W[1] == 0


_dragon_checks()

# SECRET DRAGON EGGS (SkyyPets 0.4.19, research/cloud/Secret-Dragons-Spec.md = round D5b; docs/answered/pets.md 2026-10-23 SECRET DRAGON EGGS).
# A list of its own (NOT in DRAGON_EGGS: SkyyMobs' boss drop + older SkyyPets builds read DRAGON_EGGS as the elemental eggs). Same tuple shape.
# Plain names (no "Dragon" - Skyy: "no quest or explanation - players figure them out"); never craftable, never sold by us, one per profile
# per word (pets:fn:giveSecretEgg). ALL_DRAGON_EGGS = the order SkyyPets 0.4.19+ ships (its DRAGONS table follows it).
SECRET_EGGS = [
    ("Skyy_PetEgg_Dragon_Void", "DragonVoid", "Strange Void Egg", "SkyyPets", "void"),
    ("Skyy_PetEgg_Dragon_Blood", "DragonBlood", "Crimson Egg", "SkyyPets", "blood"),
    ("Skyy_PetEgg_Dragon_Light", "DragonLight", "Radiant Egg", "SkyyPets", "light"),
    ("Skyy_PetEgg_Dragon_Crystal", "DragonCrystal", "Crystal Egg", "SkyyPets", "crystal"),
]
SECRET_EGG_IDS = [e[0] for e in SECRET_EGGS]
SECRET_RATES = "void=30, blood=20"                # per 10,000 per qualifying event (pets:fn:secretRoll); a word not listed = always
ALL_DRAGON_EGGS = DRAGON_EGGS + SECRET_EGGS
ALL_DRAGON_EGG_IDS = [e[0] for e in ALL_DRAGON_EGGS]


def _secret_checks():
    assert len(ALL_DRAGON_EGG_IDS) == len(set(ALL_DRAGON_EGG_IDS)) == 9 and not set(ALL_DRAGON_EGG_IDS) & set(IDS)
    assert all(parse_id(i) is None for i in SECRET_EGG_IDS) and all(e[3] == "SkyyPets" for e in SECRET_EGGS)
    assert len(set(e[1] for e in ALL_DRAGON_EGGS)) == 9 and len(set(e[4] for e in ALL_DRAGON_EGGS)) == 9
    assert all(e[1].startswith("Dragon") and len(e[2]) <= 40 and "Dragon" not in e[2] and e[4].isalpha() for e in SECRET_EGGS)


_secret_checks()


# ---------------------------------------------------------------------------------------------------------------- self checks (import time)
def _checks():
    assert len(IDS) == 30 and len(set(IDS)) == 30
    for c in CATEGORIES:
        for r in RARITIES:
            assert parse_id(egg_id(c, r)) == (c, r)
            assert len(name(c, r)) <= 40 and flavor(c, r).startswith(tier_tag(r) + " - ")
    assert parse_id("Skyy_PetEgg_Fishing_Rare") is None and parse_id("Food_Egg") is None
    for r, w in RARITY_W.items():
        assert len(w) == 6 and sum(w) == 10000 and all(x >= 0 for x in w), r
    for r in NEVER_BELOW_RARE:
        assert RARITY_W[r][0] == 0 and RARITY_W[r][1] == 0, r
    assert sum(DROP_LOW) == 10000 and sum(DROP_HIGH) == 10000
    assert set(RARITY_W) == set(RARITIES) == set(RATIO) == set(POOL)
    assert all(POOL[r] in ("all", "half") and RATIO[r] > 0 for r in RARITIES)
    assert set(ORDER) == set(CATEGORIES) and all(len(set(v)) == len(v) for v in ORDER.values())
    # spec 3.1 tables (python, rows sum to 100): 4 pets Common 3.9 / 9.7 / 24.5 / 61.8, Legendary 33.3 / 66.7 / 0 / 0, Mythic 66.7 / 33.3
    p = percents(4, "Common")
    assert [round(x, 1) for x in p] == [3.9, 9.7, 24.5, 61.8], p
    assert [round(x, 1) for x in percents(4, "Legendary")] == [33.3, 66.7, 0.0, 0.0]
    assert [round(x, 1) for x in percents(4, "Mythic")] == [66.7, 33.3, 0.0, 0.0]
    assert [round(x, 1) for x in percents(14, "Common")][:2] == [1.3, 1.6] and round(percents(14, "Common")[13], 1) == 20.2
    assert [round(x, 1) for x in percents(5, "Epic")] == [13.7, 16.3, 19.4, 23.1, 27.5]
    for n in range(1, 21):          # the top-half rule: a Legendary / Mythic egg never gives a pet of the bottom half
        for r in NEVER_BELOW_RARE:
            w = weights(n, RATIO[r], POOL[r])
            assert all(x == 0 for x in w[max(1, n // 2):]) and all(x > 0 for x in w[:max(1, n // 2)]), (n, r)
    for (c, r) in RECIPES:
        assert c in CATEGORIES and r in CRAFTABLE
    assert set(RECIPES) == set((c, r) for c in CATEGORIES for r in CRAFTABLE)
    assert sum(REEL1_MS) == 2710 and sum(REEL2_MS) == 2790 and len(REEL1_MS) == 14 and len(REEL2_MS) == 12
    assert all(m[2] >= MERCHANT_MIN_X * BAZAAR.get("Legendary", 0) for m in MERCHANT_ROWS) and "Legendary" not in BAZAAR


_checks()
