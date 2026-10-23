"""Cooking tree node icons (40) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents
from node_icons.farming import pumpkin

TREE = "Cooking"


# ---------------------------------------------------------------- local parts
def bowl(ic, cx, cy, s=1.0, soup="honey"):
    ic.add(inter(ellipse(cx, cy, 16 * s, 13 * s), rect(cx - 17 * s, cy, cx + 17 * s, cy + 14 * s)), "wood", base=0.52, grad=0.6, line=True)
    ic.add(ellipse(cx, cy, 16 * s, 4 * s), "wood", base=0.72, grad=0.4, line=True)
    ic.add(ellipse(cx, cy, 13 * s, 2.8 * s), soup, base=0.7, grad=0.5, bevel=0, cast=False)


def steam(ic, cx, cy, s=1.0):
    for k, dx in enumerate((-6, 0, 6)):
        pts = [(cx + dx * s + 2 * s * math.sin(t * 1.6 + k), cy - t * 3.2 * s) for t in range(5)]
        for i in range(len(pts) - 1):
            ic.add(capsule(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], 1.2 * s), "cloud", base=0.75, bevel=0, cast=False)


def spoon(ic, x0, y0, x1, y1, s=1.0):
    ic.add(capsule(x0, y0, x1, y1, 1.6 * s), "wood", base=0.6, bevel=0, line=True)
    ic.add(ellipse(x1, y1, 4.5 * s, 6 * s), "wood", base=0.7, grad=0.5, line=True)


def chef_hat(ic, cx, cy, s=1.0):
    ic.add(union(circle(cx - 8 * s, cy - 6 * s, 7 * s), circle(cx, cy - 10 * s, 8.5 * s), circle(cx + 8 * s, cy - 6 * s, 7 * s),
                 rect(cx - 10 * s, cy - 6 * s, cx + 10 * s, cy + 4 * s)), "cream", base=0.72, grad=0.5, bevel=1.0, line=True)
    ic.add(rect(cx - 11 * s, cy + 2 * s, cx + 11 * s, cy + 9 * s), "cream", base=0.55, grad=0.4, line=True,
           pattern=lambda x, y: -0.1 if int((x - cx) / (3 * s)) % 2 else 0)


def cloche(ic, cx, cy, s=1.0):
    plate(ic, cx, cy + 6 * s, 1.2 * s)
    ic.add(inter(ellipse(cx, cy + 4 * s, 17 * s, 16 * s), rect(cx - 18 * s, cy - 14 * s, cx + 18 * s, cy + 4 * s)), "steel", mode="sphere",
           base=0.62, sphere=(cx, cy + 4 * s, 17 * s, 16 * s), line=True)
    ic.add(circle(cx, cy - 13 * s, 2.6 * s), "steel", mode="sphere", base=0.7, line=True)


def cleaver(ic, cx, cy, s=1.0):
    ic.add(capsule(cx + 8 * s, cy + 6 * s, cx + 18 * s, cy + 16 * s, 2.0 * s), "wood", base=0.55, bevel=0, line=True)
    ic.add(poly([(cx - 14 * s, cy - 10 * s), (cx + 2 * s, cy - 14 * s), (cx + 12 * s, cy + 4 * s), (cx - 4 * s, cy + 8 * s)]), "steel", base=0.62,
           grad=0.6, bevel=1.0, line=True)
    ic.add(circle(cx - 6 * s, cy - 7 * s, 1.6 * s), "navy", base=0.15, bevel=0, cast=False)


def shaker(ic, cx, cy, s=1.0):
    ic.add(rrect(cx - 5 * s, cy - 6 * s, cx + 5 * s, cy + 10 * s, 2 * s), "glass", base=0.6, grad=0.5, line=True)
    ic.add(inter(ellipse(cx, cy - 6 * s, 5 * s, 5 * s), rect(cx - 6 * s, cy - 12 * s, cx + 6 * s, cy - 6 * s)), "steel", base=0.65, line=True)
    for (x, y) in ((-3, -15), (1, -18), (4, -14)):
        ic.add(circle(cx + x * s, cy + y * s, 0.9 * s), "cream", base=0.85, bevel=0)


def crown(ic, cx, cy, s=1.0):
    ic.add(poly([(cx - 12 * s, cy + 5 * s), (cx - 13 * s, cy - 6 * s), (cx - 6 * s, cy), (cx, cy - 9 * s), (cx + 6 * s, cy), (cx + 13 * s, cy - 6 * s),
                 (cx + 12 * s, cy + 5 * s)]), "gold", base=0.62, grad=0.5, bevel=0.8, line=True)
    ic.add(circle(cx, cy + 1 * s, 2 * s), "ruby", base=0.7, bevel=0)


# ---------------------------------------------------------------- Line Cook
def taste_test():
    ic = Icon("TasteTest")
    bowl(ic, 26, 40, 1.2)
    spoon(ic, 48, 56, 38, 30, 1.1)
    eye(ic, 46, 14, 0.85)
    spark(ic, 14, 24, "buff", 2)
    return ic


def seasoned():
    ic = Icon("Seasoned")
    drumstick(ic, 24, 40, 1.3)
    shaker(ic, 46, 26, 1.0)
    plus(ic, 14, 12, 0.95, "buff")
    return ic


def long_simmer():
    ic = Icon("LongSimmer")
    cauldron(ic, 28, 40, 1.1, liquid="honey")
    steam(ic, 28, 24, 1.0)
    arrow(ic, 53, 16, 1.0, "yield")
    return ic


def flash_fry():
    ic = Icon("FlashFry")
    flame(ic, 26, 50, 0.9)
    pan(ic, 26, 36, 1.0, food="cream")
    ic.add(circle(26, 35, 2.2), "honey", base=0.8, bevel=0, cast=False)
    burst(ic, 52, 14, 9, 4, 8, acc("ability"), base=0.85)
    return ic


def hot_pan():
    ic = Icon("HotPan")
    pan(ic, 22, 28, 0.95, food="mahog")
    clock(ic, 49, 49, 10, "ability")
    return ic


def double_skillet():
    ic = Icon("DoubleSkillet")
    pan(ic, 20, 22, 0.8, food="cream")
    pan(ic, 22, 44, 0.8, food="mahog")
    plus(ic, 53, 50, 0.95, "ability")
    return ic


def hearty_meals():
    ic = Icon("HeartyMeals")
    drumstick(ic, 24, 38, 1.35)
    ic.add(heart(48, 16, 0.75), acc("health"), base=0.62, grad=0.5, bevel=0.6, line=True)
    plus(ic, 52, 50, 0.85, "health")
    return ic


def spice_rack():
    ic = Icon("SpiceRack")
    jar(ic, 18, 38, 1.0, fill="red")
    jar(ic, 38, 40, 1.0, fill="honey")
    arrow(ic, 52, 14, 0.95, "yield")
    return ic


def leftovers():
    ic = Icon("Leftovers")
    plate(ic, 30, 44, 1.3)
    ic.add(inter(rot_ellipse(30, 38, 12, 6.5, -10), rect(0, 0, 32, 64)), "wood", base=0.62, grad=0.6, bevel=1.0, line=True)
    turn_arrow(ic, 32, 34, 26, 200, 320, "yield")
    return ic


def comfort_food():
    ic = Icon("ComfortFood")
    bowl(ic, 26, 40, 1.25, soup="red")
    steam(ic, 26, 30, 0.9)
    ic.add(heart(50, 16, 0.75), acc("health"), base=0.62, grad=0.5, bevel=0.6, line=True)
    return ic


def chefs_pride():
    ic = Icon("ChefsPride")
    chef_hat(ic, 24, 34, 1.3)
    ring_item(ic, 48, 22, 0.9)
    hourglass(ic, 50, 50, 0.7, "buff")
    return ic


def feast_mode():
    ic = Icon("FeastMode")
    cake(ic, 26, 40, 1.2)
    xp_orb(ic, 48, 16, 10)
    return ic


def gourmet_touch():
    ic = Icon("GourmetTouch")
    plate(ic, 28, 46, 1.3)
    drumstick(ic, 28, 34, 0.85)
    spark(ic, 12, 14, "yield", 2); spark(ic, 44, 20, "yield", 1)
    plus(ic, 53, 12, 0.95, "yield")
    return ic


def signature_dish():
    ic = Icon("SignatureDish")
    cloche(ic, 30, 38, 1.2)
    burst(ic, 50, 12, 9, 3.6, 4, "gold", base=0.9, line=True)
    spark(ic, 8, 12, "buff", 2)
    return ic


# ---------------------------------------------------------------- Pantry
def foragers_larder():
    ic = Icon("ForagersLarder")
    sack(ic, 26, 40, 1.25, pal="wheat")
    pumpkin(ic, 26, 22, 0.45)
    berries(ic, 40, 22, 0.55)
    plus(ic, 53, 50, 0.95, "yield")
    return ic


def fresh_catch():
    ic = Icon("FreshCatch")
    plate(ic, 28, 46, 1.3)
    fish(ic, 26, 38, 0.9)
    arrow(ic, 53, 14, 1.0, "yield")
    return ic


def pantry_pouch():
    ic = Icon("PantryPouch")
    backpack(ic, 24, 36, 1.25, pal="wheat")
    bread(ic, 24, 14, 0.5)
    stack_badge(ic, 50, 46, 1.1, pal=acc("yield"))
    return ic


def deep_pantry():
    ic = Icon("DeepPantry")
    ic.add(rect(4, 10, 44, 58), "wood", base=0.4, grad=0.5, line=True)
    for y in (24, 42):
        ic.add(rect(6, y, 42, y + 3), "wood", base=0.7, bevel=0)
    jar(ic, 14, 16, 0.5, fill="red"); jar(ic, 26, 16, 0.5, fill="honey"); jar(ic, 14, 34, 0.5, fill="green"); bread(ic, 30, 38, 0.45)
    stack_badge(ic, 52, 46, 1.0, pal=acc("yield"))
    return ic


def preserves():
    ic = Icon("Preserves")
    jar(ic, 26, 36, 1.5, fill="ruby")
    hourglass(ic, 51, 46, 0.95, "tool")
    return ic


def thrifty_cook():
    ic = Icon("ThriftyCook")
    bread(ic, 30, 36, 1.1)
    turn_arrow(ic, 30, 34, 24, 200, 330, "yield")
    turn_arrow(ic, 30, 34, 24, 20, 150, "yield")
    return ic


def pet_sous_chef():
    ic = Icon("PetSousChef")
    paw(ic, 26, 42, 1.3, acc("pet"))
    chef_hat(ic, 46, 18, 0.7)
    xp_orb(ic, 52, 50, 7)
    return ic


def spice_trader():
    ic = Icon("SpiceTrader")
    jar(ic, 24, 36, 1.35, fill="honey")
    coin(ic, 46, 48, 8)
    plus(ic, 52, 12, 0.95, "yield")
    return ic


def cauldron_master():
    ic = Icon("CauldronMaster")
    cauldron(ic, 28, 38, 1.35, liquid="honey")
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def master_butcher():
    ic = Icon("MasterButcher")
    cleaver(ic, 22, 22, 1.0)
    drumstick(ic, 34, 40, 0.9)
    plus(ic, 53, 12, 0.95, "yield")
    return ic


def seasonal_harvest():
    ic = Icon("SeasonalHarvest")
    pumpkin(ic, 26, 40, 1.15)
    leaf(ic, 44, 20, 1.0, -40, pal="honey")
    plus(ic, 53, 50, 0.9, "buff")
    return ic


def bulk_prep():
    ic = Icon("BulkPrep")
    for k in range(3):
        plate(ic, 26, 50 - k * 7, 1.0)
    bread(ic, 26, 26, 0.6)
    stack_badge(ic, 52, 20, 1.0, pal=acc("yield"))
    return ic


def bottomless_larder():
    ic = Icon("BottomlessLarder")
    chest(ic, 30, 46, 1.25)
    bread(ic, 22, 30, 0.55); drumstick(ic, 38, 28, 0.55); pumpkin(ic, 30, 24, 0.35)
    spark(ic, 8, 10, "yield", 2); spark(ic, 56, 12, "yield", 2)
    return ic


# ---------------------------------------------------------------- Festival
def big_batch():
    ic = Icon("BigBatch")
    bowl(ic, 22, 30, 0.85, soup="red")
    bowl(ic, 30, 46, 0.85, soup="honey")
    plus(ic, 53, 14, 1.0, "yield")
    return ic


def plate_presentation():
    ic = Icon("PlatePresentation")
    plate(ic, 30, 44, 1.35)
    drumstick(ic, 28, 32, 0.75)
    leaf(ic, 44, 36, 0.6, -20)
    plus(ic, 53, 12, 0.95, "buff")
    return ic


def banquet():
    ic = Icon("Banquet")
    table(ic, 30, 44, 1.2)
    cake(ic, 22, 30, 0.45); drumstick(ic, 36, 28, 0.55); bottle(ic, 44, 30, 0.45)
    burst(ic, 52, 10, 8, 3.4, 8, acc("ability"), base=0.85)
    return ic


def long_feast():
    ic = Icon("LongFeast")
    table(ic, 26, 34, 1.0)
    cake(ic, 22, 22, 0.4)
    hourglass(ic, 51, 46, 0.95, "ability")
    return ic


def wide_table():
    ic = Icon("WideTable")
    table(ic, 32, 34, 0.9)
    arrows_out(ic, 32, 34, 25, "ability", 0.8)
    return ic


def sweet_tooth():
    ic = Icon("SweetTooth")
    cake(ic, 28, 38, 1.4)
    plus(ic, 53, 12, 0.95, "buff")
    return ic


def pet_tasting():
    ic = Icon("PetTasting")
    paw(ic, 24, 42, 1.3, acc("pet"))
    drumstick(ic, 44, 18, 0.6)
    xp_orb(ic, 52, 50, 7)
    return ic


def gear_resonance():
    ic = Icon("GearResonanceCooking")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 40, R, 200, 340, 2.6, "buff", base=b)
    chef_hat(ic, 32, 40, 1.15)
    return ic


def hospitality():
    ic = Icon("Hospitality")
    table(ic, 26, 44, 1.0)
    ic.add(heart(26, 26, 0.8), acc("health"), base=0.62, grad=0.5, bevel=0.6, line=True)
    plus(ic, 52, 16, 0.9, "health")
    return ic


def rare_vintage():
    ic = Icon("RareVintage")
    bottle(ic, 26, 38, 1.3)
    spark(ic, 44, 22, "yield", 2)
    plus(ic, 52, 50, 0.95, "yield")
    return ic


def chefs_kiss():
    ic = Icon("ChefsKiss")
    plate(ic, 26, 48, 1.2)
    drumstick(ic, 26, 38, 0.7)
    arrow(ic, 46, 22, 0.9, "yield")
    arrow(ic, 56, 22, 0.9, "yield")
    return ic


def lasting_impression():
    ic = Icon("LastingImpression")
    table(ic, 24, 30, 0.9)
    hourglass(ic, 50, 46, 1.0, "buff")
    return ic


def royal_feast():
    ic = Icon("RoyalFeast")
    plate(ic, 30, 48, 1.4)
    drumstick(ic, 28, 34, 1.0)
    crown(ic, 46, 14, 1.0)
    spark(ic, 8, 12, "buff", 2)
    return ic


ROWS = [
 ("Cooking.b1.r1.free", "B1R1Free", "ability", taste_test, "a bowl of soup with a tasting spoon, an eye and a purple sparkle (see buff values)"),
 ("Cooking.b1.r1a", "B1R1a", "buff", seasoned, "a roast drumstick and a salt shaker + a purple plus (food buff strength)"),
 ("Cooking.b1.r1b", "B1R1b", "yield", long_simmer, "a simmering pot with steam + a green up arrow (Grade higher)"),
 ("Cooking.b1.r2.free", "B1R2Free", "ability", flash_fry, "an egg frying in a pan on a flame, a blue burst (instant cook)"),
 ("Cooking.b1.r2a", "B1R2a", "ability", hot_pan, "a frying pan + a blue cooldown clock"),
 ("Cooking.b1.r2b", "B1R2b", "ability", double_skillet, "two frying pans + a blue plus (one more item)"),
 ("Cooking.b1.r3a", "B1R3a", "health", hearty_meals, "a roast drumstick and a red heart + plus (more healing)"),
 ("Cooking.b1.r3b", "B1R3b", "yield", spice_rack, "two spice jars + a green up arrow (Grade higher)"),
 ("Cooking.b1.r3c", "B1R3c", "yield", leftovers, "half a loaf on a plate with a green turn arrow (food not used up)"),
 ("Cooking.b1.r4a", "B1R4a", "health", comfort_food, "a steaming bowl of red soup and a red heart (+ max Health)"),
 ("Cooking.b1.r4b", "B1R4b", "buff", chefs_pride, "a chef's hat, a gold ring and a purple-sand hourglass (per accessory)"),
 ("Cooking.b1.r5a", "B1R5a", "xp", feast_mode, "a cake with a cherry + a gold XP orb"),
 ("Cooking.b1.r5b", "B1R5b", "yield", gourmet_touch, "a drumstick served on a plate, green sparkles + plus (rarer food)"),
 ("Cooking.b1.r6", "B1R6", "buff", signature_dish, "a silver cloche on a plate with a gold star (capstone)"),
 ("Cooking.b2.r1a", "B2R1a", "yield", foragers_larder, "a grain sack topped with a pumpkin and berries + a green plus"),
 ("Cooking.b2.r1b", "B2R1b", "yield", fresh_catch, "a fish on a plate + a green up arrow (Grade higher)"),
 ("Cooking.b2.r2.free", "B2R2Free", "yield", pantry_pouch, "a food pack with a loaf + green stacked slots (food slots)"),
 ("Cooking.b2.r2a", "B2R2a", "yield", deep_pantry, "a pantry shelf of jars and bread + green stacked slots"),
 ("Cooking.b2.r2b", "B2R2b", "tool", preserves, "a jar of red preserves + a soft-white hourglass (shelf life)"),
 ("Cooking.b2.r3a", "B2R3a", "yield", thrifty_cook, "a loaf inside two green circling arrows (ingredient saved)"),
 ("Cooking.b2.r3b", "B2R3b", "pet", pet_sous_chef, "a tan paw wearing a little chef's hat + a gold XP orb"),
 ("Cooking.b2.r3c", "B2R3c", "yield", spice_trader, "a spice jar and a coin + a green plus (more spice)"),
 ("Cooking.b2.r4a", "B2R4a", "yield", cauldron_master, "a big cooking pot of stew + a green plus (bigger batches)"),
 ("Cooking.b2.r4b", "B2R4b", "yield", master_butcher, "a cleaver and a drumstick + a green plus (more meat)"),
 ("Cooking.b2.r5a", "B2R5a", "buff", seasonal_harvest, "a pumpkin with an autumn leaf + a purple plus (in-season buff)"),
 ("Cooking.b2.r5b", "B2R5b", "yield", bulk_prep, "a stack of plates under a loaf + green stacked slots (batch slot)"),
 ("Cooking.b2.r6", "B2R6", "yield", bottomless_larder, "a chest overflowing with bread, meat and a pumpkin (capstone)"),
 ("Cooking.b3.r1a", "B3R1a", "yield", big_batch, "two bowls of soup + a green plus (one more serving)"),
 ("Cooking.b3.r1b", "B3R1b", "buff", plate_presentation, "a garnished dish on a plate + a purple plus (shared-meal buff)"),
 ("Cooking.b3.r2.free", "B3R2Free", "ability", banquet, "a red-clothed table laid with cake, meat and wine, blue burst"),
 ("Cooking.b3.r2a", "B3R2a", "ability", long_feast, "a banquet table + an hourglass (longer)"),
 ("Cooking.b3.r2b", "B3R2b", "ability", wide_table, "a banquet table with four blue arrows pushing outward (bigger radius)"),
 ("Cooking.b3.r3a", "B3R3a", "buff", sweet_tooth, "a cream cake with a cherry + a purple plus (dessert buff)"),
 ("Cooking.b3.r3b", "B3R3b", "pet", pet_tasting, "a tan paw, a drumstick and a gold XP orb (pet XP from food)"),
 ("Cooking.b3.r3c", "B3R3c", "buff", gear_resonance, "a chef's hat with purple resonance arcs (per armor piece)"),
 ("Cooking.b3.r4a", "B3R4a", "health", hospitality, "a banquet table under a red heart + plus (regen for allies)"),
 ("Cooking.b3.r4b", "B3R4b", "yield", rare_vintage, "a ruby wine bottle, green sparkle + plus (rare drink)"),
 ("Cooking.b3.r5a", "B3R5a", "yield", chefs_kiss, "a dish on a plate + two green up arrows (+2 Grades)"),
 ("Cooking.b3.r5b", "B3R5b", "buff", lasting_impression, "a banquet table + a purple-sand hourglass (buff lasts after leaving)"),
 ("Cooking.b3.r6", "B3R6", "buff", royal_feast, "a roast on a platter under a gold crown (capstone)"),
]
