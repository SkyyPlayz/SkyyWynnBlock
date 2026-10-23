"""Farming tree node icons (40) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py.
Skyy's Farming decision (2026-10-23): Quick Scythe becomes "+X% harvester swing speed on crops" -> drawn as a harvester with motion lines."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents

TREE = "Farming"


# ---------------------------------------------------------------- local parts
def pumpkin(ic, cx, cy, s=1.0):
    ic.add(capsule(cx, cy - 10 * s, cx + 3 * s, cy - 16 * s, 2 * s), "green", base=0.5, bevel=0, line=True)
    ic.add(ellipse(cx, cy, 16 * s, 12 * s), "honey", mode="sphere", base=0.6, line=True,
           pattern=lambda x, y: -0.14 if abs(((x - cx) / (16 * s)) * 3 % 1 - 0.5) > 0.42 else 0)


def bundle(ic, cx, by, s=1.0):
    for k, (bx, tx) in enumerate(((-3, -12), (0, 0), (3, 12), (-1.5, -6), (1.5, 6))):
        ic.add(capsule(cx + bx * s, by, cx + tx * s, by - 22 * s, 1.2 * s), "green", base=0.55, bevel=0)
        ic.add(rot_ellipse(cx + tx * s, by - 26 * s, 3.6 * s, 8 * s, tx * 2), "wheat", base=0.62, grad=0.6, bevel=1.0, line=True,
               pattern=lambda x, y: -0.1 if int(y) % 3 == 0 else 0)
    ic.add(rrect(cx - 6 * s, by - 12 * s, cx + 6 * s, by - 8 * s, 1.5 * s), "mahog", base=0.55, grad=0.4, line=True)


def rows(ic, by, n=3, s=1.0):
    ic.add(rect(2, by - 2, 50, by + 4), "soil", base=0.45, grad=0.4)
    for k in range(n):
        wheat(ic, 10 + k * 15, by, s, lean=(k - 1) * 2)


def cornucopia(ic, cx, cy, s=1.0):
    horn = poly([(cx + 18 * s, cy + 14 * s), (cx + 6 * s, cy + 12 * s), (cx - 8 * s, cy + 2 * s), (cx - 14 * s, cy - 10 * s), (cx - 4 * s, cy - 6 * s),
                 (cx + 8 * s, cy - 4 * s), (cx + 18 * s, cy - 8 * s)])
    ic.add(horn, "wheat", base=0.5, grad=0.6, line=True, pattern=lambda x, y: -0.12 if int((x - cx) / (4 * s)) % 2 else 0)
    ic.add(ellipse(cx + 18 * s, cy + 3 * s, 5 * s, 11 * s), "wood", base=0.3, bevel=0, line=True)


def bell(ic, cx, cy, s=1.0, pal="gold"):
    ic.add(union(inter(ellipse(cx, cy, 10 * s, 12 * s), rect(cx - 11 * s, cy - 13 * s, cx + 11 * s, cy + 4 * s)),
                 rect(cx - 12 * s, cy + 3 * s, cx + 12 * s, cy + 7 * s)), pal, base=0.6, grad=0.6, bevel=1.0, line=True)
    ic.add(circle(cx, cy + 9 * s, 2.6 * s), pal, mode="sphere", base=0.5, line=True)
    ic.add(ering(cx, cy - 13 * s, 3 * s, 3 * s, 1.5 * s, 1.5 * s), pal, base=0.5, bevel=0, line=True)


def shears(ic, cx, cy, s=1.0):
    for f in (-1, 1):
        ic.add(poly([(cx, cy), (cx + f * 3 * s, cy - 2 * s), (cx + f * 4 * s, cy - 24 * s)]), "steel", base=0.7, grad=0.5, bevel=0.6, line=True)
        ic.add(ering(cx + f * 6 * s, cy + 6 * s, 5 * s, 5 * s, 2.8 * s, 2.8 * s), "red", base=0.55, bevel=0, line=True)


def wool_ball(ic, cx, cy, r):
    ic.add(circle(cx, cy, r), "cream", mode="sphere", base=0.62, line=True,
           pattern=lambda x, y: -0.1 if int((x - cx) * 0.6 + (y - cy)) % 4 == 0 else 0)


def herb(ic, cx, by, s=1.0, pal="emerald"):
    ic.add(capsule(cx, by, cx, by - 18 * s, 1.2 * s), "green", base=0.5, bevel=0)
    for (y, a, f) in ((-6, -150, -1), (-10, -30, 1), (-15, -150, -1), (-19, -30, 1)):
        leaf(ic, cx + f * 6 * s, by + y * s, 0.7 * s, a, pal=pal)


def compost(ic, cx, by, s=1.0):
    ic.add(inter(ellipse(cx, by, 20 * s, 14 * s), rect(cx - 21 * s, by - 15 * s, cx + 21 * s, by)), "soil", base=0.5, grad=0.6, line=True,
           pattern=lambda x, y: 0.08 * math.sin(x * 1.7) * math.sin(y * 1.3))
    leaf(ic, cx - 6 * s, by - 10 * s, 0.6 * s, -20, pal="honey"); leaf(ic, cx + 7 * s, by - 7 * s, 0.6 * s, -150, pal="grass")


def watering_can(ic, cx, cy, s=1.0):
    ic.add(capsule(cx + 8 * s, cy + 2 * s, cx + 22 * s, cy - 10 * s, 1.8 * s), "teal", base=0.55, bevel=0, line=True)
    ic.add(rrect(cx - 12 * s, cy - 8 * s, cx + 10 * s, cy + 10 * s, 3 * s), "teal", mode="cyl", axis=(1, 0), base=0.55, line=True)
    ic.add(ering(cx - 1 * s, cy - 9 * s, 9 * s, 7 * s, 6.5 * s, 4.8 * s), "teal", base=0.5, bevel=0, line=True)


def glasshouse(ic, cx, by, s=1.0):
    ic.add(rect(cx - 16 * s, by - 14 * s, cx + 16 * s, by), "glass", base=0.5, grad=0.5, line=True,
           pattern=lambda x, y: -0.12 if int((x - cx) / (5.3 * s)) != (x - cx) / (5.3 * s) and abs(((x - cx) / (8 * s)) % 1) < 0.12 else 0)
    ic.add(poly([(cx - 18 * s, by - 14 * s), (cx + 18 * s, by - 14 * s), (cx, by - 26 * s)]), "glass", base=0.7, grad=0.5, line=True)
    for x in (-16, 0, 16):
        ic.add(rect(cx + x * s - 1 * s, by - 14 * s, cx + x * s + 1 * s, by), "steel", base=0.5, bevel=0)


# ---------------------------------------------------------------- Harvester
def green_eye():
    ic = Icon("GreenEye")
    wheat(ic, 22, 60, 1.3)
    eye(ic, 46, 16, 1.0, iris="emerald")
    spark(ic, 10, 22, "ability", 2); spark(ic, 34, 30, "ability", 2); spark(ic, 12, 40, "ability", 1)
    return ic


def bountiful_rows():
    ic = Icon("BountifulRows")
    rows(ic, 58, 3, 1.15)
    plus(ic, 53, 12, 1.1, "yield")
    return ic


def quick_scythe():
    ic = Icon("QuickScythe")
    arc(ic, 40, 44, 32, 200, 262, 3.0, "speed")
    arc(ic, 40, 44, 24, 206, 258, 2.6, "speed", base=0.55)
    lines(ic, [(4, 36, 12, 36), (6, 44, 13, 43)], "speed", 1.4)
    scythe(ic, 50, 60, 34, 12, 1.15)
    return ic


def sweep_harvest():
    ic = Icon("SweepHarvest")
    rows(ic, 60, 3, 1.0)
    arc(ic, 26, 60, 30, 200, 330, 3.2, "ability")
    scythe(ic, 58, 46, 46, 8, 0.85)
    return ic


def wide_sweep():
    ic = Icon("WideSweep")
    wheat(ic, 32, 48, 1.2)
    arrows_out(ic, 32, 34, 24, "ability", 0.85)
    return ic


def swift_sweep():
    ic = Icon("SwiftSweep")
    scythe(ic, 32, 60, 22, 12, 1.0)
    clock(ic, 49, 49, 10, "ability")
    return ic


def double_reap():
    ic = Icon("DoubleReap")
    bundle(ic, 20, 60, 0.85)
    bundle(ic, 40, 60, 0.85)
    plus(ic, 54, 12, 1.0, "yield")
    return ic


def auto_seed():
    ic = Icon("AutoSeed")
    wheat(ic, 22, 56, 1.3)
    for (x, y) in ((38, 40), (46, 48), (40, 54)):
        seed(ic, x, y, 1.0)
    plus(ic, 52, 14, 1.0, "yield")
    return ic


def fertile_soil():
    ic = Icon("FertileSoil")
    sapling(ic, 26, 56, 1.5)
    arrow(ic, 50, 22, 1.1, "speed")
    lines(ic, [(50, 32, 50, 46), (44, 36, 44, 44), (56, 36, 56, 44)], "speed", 1.4)
    return ic


def golden_harvest():
    ic = Icon("GoldenHarvest")
    ic.add(capsule(30, 60, 32, 36, 1.6), "green", base=0.55, bevel=0)
    ic.add(rot_ellipse(32, 26, 6.5, 15, 3), "gold", base=0.66, grad=0.6, bevel=1.0, line=True, pattern=lambda x, y: -0.12 if int(y) % 3 == 0 else 0)
    leaf(ic, 22, 46, 0.8, -150)
    spark(ic, 50, 12, "yield", 2); spark(ic, 12, 18, "yield", 1); spark(ic, 50, 40, "yield", 1)
    return ic


def bumper_crop():
    ic = Icon("BumperCrop")
    pumpkin(ic, 28, 40, 1.4)
    plus(ic, 53, 12, 1.05, "yield")
    return ic


def harvest_frenzy():
    ic = Icon("HarvestFrenzy")
    bundle(ic, 24, 60, 1.05)
    xp_orb(ic, 48, 20, 11)
    arrow(ic, 50, 48, 0.95, "xp")
    return ic


def scythe_tempering():
    ic = Icon("ScytheTempering")
    podium(ic, 4, 60)
    hoe(ic, 30, 34, 44, 12, 0.9, head="gold")
    plus(ic, 12, 14, 0.95, "yield")
    return ic


def cornucopia_icon():
    ic = Icon("Cornucopia")
    cornucopia(ic, 26, 34, 1.4)
    pumpkin(ic, 50, 42, 0.55)
    wheat(ic, 50, 30, 0.6, lean=6)
    ic.add(circle(44, 54, 4.5), "red", mode="sphere", base=0.6, line=True)
    ic.add(circle(55, 54, 4), "gold", mode="sphere", base=0.7, line=True)
    spark(ic, 10, 8, "yield", 2)
    return ic


# ---------------------------------------------------------------- Rancher
def animal_friend():
    ic = Icon("AnimalFriend")
    cow_head(ic, 28, 34, 1.4)
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def gentle_touch():
    ic = Icon("GentleTouch")
    sheep(ic, 24, 40, 1.0)
    ic.add(heart(44, 16, 0.75), "ruby", base=0.62, grad=0.6, bevel=0.8, line=True)
    plus(ic, 54, 50, 0.9, "yield")
    return ic


def animal_call():
    ic = Icon("AnimalCall")
    cow_head(ic, 22, 36, 1.2)
    for R, b in ((14, 0.85), (21, 0.68), (28, 0.52)):
        arc(ic, 30, 34, R, -45, 45, 2.6, "ability", base=b)
    return ic


def wide_call():
    ic = Icon("WideCall")
    bell(ic, 32, 30, 1.2)
    arrows_out(ic, 32, 32, 25, "ability", 0.8)
    return ic


def calm_presence():
    ic = Icon("CalmPresence")
    sheep(ic, 24, 32, 1.05)
    hourglass(ic, 50, 46, 1.0, "ability")
    return ic


def pet_farmer():
    ic = Icon("PetFarmer")
    paw(ic, 24, 38, 1.45, acc("pet"))
    wheat(ic, 50, 58, 0.95, lean=-3)
    plus(ic, 12, 10, 0.85, "pet")
    return ic


def quality_feed():
    ic = Icon("QualityFeed")
    bucket(ic, 28, 40, 1.4, fill="wheat", pal="wood")
    spark(ic, 50, 12, "yield", 2)
    plus(ic, 53, 50, 0.95, "yield")
    return ic


def twin_birth():
    ic = Icon("TwinBirth")
    egg(ic, 20, 38, 1.3)
    egg(ic, 38, 40, 1.3)
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def barn_aura():
    ic = Icon("BarnAura")
    cow_head(ic, 24, 40, 1.15)
    ring_item(ic, 46, 20, 1.05)
    plus(ic, 54, 52, 0.9, "yield")
    return ic


def shearing_master():
    ic = Icon("ShearingMaster")
    wool_ball(ic, 40, 42, 15)
    shears(ic, 18, 36, 1.1)
    plus(ic, 54, 12, 0.95, "yield")
    return ic


def golden_egg():
    ic = Icon("GoldenEgg")
    egg(ic, 30, 36, 2.0, pal="gold")
    spark(ic, 52, 12, "yield", 2); spark(ic, 12, 52, "yield", 1)
    return ic


def beast_whisperer():
    ic = Icon("BeastWhisperer")
    paw(ic, 26, 38, 1.45, acc("pet"))
    ic.add(heart(48, 16, 0.85), "ruby", base=0.62, grad=0.6, bevel=0.8, line=True)
    arrow(ic, 52, 48, 0.85, "pet")
    return ic


def prize_herd():
    ic = Icon("PrizeHerd")
    cow_head(ic, 26, 34, 1.3)
    ic.add(poly([(44, 44), (40, 60), (46, 56), (50, 61), (52, 44)]), "red", base=0.55, grad=0.5, line=True)
    ic.add(poly(star_pts(48, 40, 10, 6.5, 10)), "gold", base=0.62, grad=0.5, line=True)
    ic.add(circle(48, 40, 4.5), "red", base=0.65, bevel=0)
    spark(ic, 54, 8, "yield", 2)
    return ic


# ---------------------------------------------------------------- Alchemist's Garden
def herb_lore():
    ic = Icon("HerbLore")
    herb(ic, 26, 58, 1.6)
    plus(ic, 52, 12, 1.05, "yield")
    return ic


def pest_control():
    ic = Icon("PestControl")
    wheat(ic, 20, 58, 1.25)
    shield(ic, 44, 36, 1.2, pal=acc("yield"))
    return ic


def compost_boost():
    ic = Icon("CompostBoost")
    compost(ic, 30, 56, 1.25)
    sapling(ic, 30, 40, 0.75)
    burst(ic, 50, 16, 9, 4, 8, acc("ability"), base=0.85)
    spark(ic, 10, 16, "ability", 2)
    return ic


def rich_compost():
    ic = Icon("RichCompost")
    compost(ic, 26, 50, 1.15)
    hourglass(ic, 50, 22, 1.0, "ability")
    return ic


def quick_mix():
    ic = Icon("QuickMixFarming")
    compost(ic, 26, 46, 1.1)
    clock(ic, 49, 49, 10, "ability")
    return ic


def rare_seed():
    ic = Icon("RareSeed")
    seed(ic, 28, 36, 1.9, pal="amethyst")
    for a in range(0, 360, 60):
        lines(ic, [(28 + 13 * math.cos(math.radians(a)), 36 + 13 * math.sin(math.radians(a)), 28 + 19 * math.cos(math.radians(a)),
                    36 + 19 * math.sin(math.radians(a)))], "buff", 1.4)
    plus(ic, 53, 12, 1.0, "yield")
    spark(ic, 12, 14, "yield", 1)
    return ic


def watering():
    ic = Icon("WateringCan")
    watering_can(ic, 24, 28, 1.25)
    for (x, y) in ((48, 34), (54, 44), (46, 50)):
        drop(ic, x, y, 0.5)
    plus(ic, 14, 54, 0.85, "yield")
    return ic


def gear_resonance():
    ic = Icon("GearResonanceFarming")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 40, R, 200, 340, 2.6, "yield", base=b)
    helmet(ic, 32, 38, 1.0, pal="wheat")
    ic.add(rect(16, 36, 48, 39), "red", base=0.55, bevel=0)
    return ic


def hothouse():
    ic = Icon("Hothouse")
    glasshouse(ic, 26, 58, 1.2)
    sapling(ic, 26, 56, 0.6)
    arrow(ic, 52, 16, 1.0, "speed")
    lines(ic, [(52, 26, 52, 40)], "speed", 1.5)
    return ic


def seed_broker():
    ic = Icon("SeedBroker")
    for (x, y, a) in ((26, 32, -30), (36, 38, 20), (26, 44, 60)):
        seed(ic, x, y, 1.4, ang=a)
    turn_arrow(ic, 30, 38, 22, 200, 340, "yield")
    turn_arrow(ic, 30, 38, 22, 20, 160, "yield")
    return ic


def mutation():
    ic = Icon("Mutation")
    ic.add(capsule(30, 60, 32, 36, 1.6), "green", base=0.55, bevel=0)
    ic.add(inter(rot_ellipse(32, 26, 6.5, 15, 3), rect(0, 0, 32, 64)), "wheat", base=0.62, grad=0.6, bevel=1.0, line=True)
    ic.add(inter(rot_ellipse(32, 26, 6.5, 15, 3), rect(32, 0, 64, 64)), "amethyst", base=0.62, grad=0.6, bevel=1.0, line=True)
    spark(ic, 50, 16, "buff", 2)
    plus(ic, 52, 48, 0.95, "yield")
    return ic


def bundling():
    ic = Icon("Bundling")
    bundle(ic, 26, 60, 1.15)
    stack_badge(ic, 50, 44, 1.1, pal=acc("yield"))
    return ic


def eden_patch():
    ic = Icon("EdenPatch")
    ic.add(rect(6, 48, 58, 58), "soil", base=0.5, grad=0.4, line=True)
    for k, x in enumerate((14, 32, 50)):
        wheat(ic, x, 50, 0.9, lean=(k - 1) * 2)
    flower(ic, 23, 44, 0.45, petal="ruby"); flower(ic, 41, 44, 0.45, petal="amethyst")
    spark(ic, 10, 10, "yield", 2); spark(ic, 56, 12, "yield", 2); spark(ic, 32, 8, "yield", 1)
    return ic


ROWS = [
 ("Farming.b1.r1.free", "B1R1Free", "ability", green_eye, "a ripe wheat ear glowing blue, an eye watching it"),
 ("Farming.b1.r1a", "B1R1a", "yield", bountiful_rows, "three wheat plants in a soil row + a green plus"),
 ("Farming.b1.r1b", "B1R1b", "speed", quick_scythe, "a harvester's scythe mid-swing with teal motion arcs (Skyy: harvester swing speed on crops)"),
 ("Farming.b1.r2.free", "B1R2Free", "ability", sweep_harvest, "a scythe sweeping a blue arc over a wheat row (5x5 harvest)"),
 ("Farming.b1.r2a", "B1R2a", "ability", wide_sweep, "a wheat ear with four blue arrows pushing outward (bigger area)"),
 ("Farming.b1.r2b", "B1R2b", "ability", swift_sweep, "a scythe + a blue cooldown clock"),
 ("Farming.b1.r3a", "B1R3a", "yield", double_reap, "two tied wheat bundles + a green plus (double crops)"),
 ("Farming.b1.r3b", "B1R3b", "yield", auto_seed, "a wheat ear dropping seeds + a green plus"),
 ("Farming.b1.r3c", "B1R3c", "speed", fertile_soil, "a sprout in soil + a teal up arrow (faster growth)"),
 ("Farming.b1.r4a", "B1R4a", "yield", golden_harvest, "a golden wheat ear, green sparkles"),
 ("Farming.b1.r4b", "B1R4b", "yield", bumper_crop, "a big pumpkin + a green plus (Farming Fortune)"),
 ("Farming.b1.r5a", "B1R5a", "xp", harvest_frenzy, "a wheat bundle, a gold XP orb + a gold up arrow"),
 ("Farming.b1.r5b", "B1R5b", "yield", scythe_tempering, "a gold hoe on a copper / iron / gold podium + a green plus (per hoe tier)"),
 ("Farming.b1.r6", "B1R6", "yield", cornucopia_icon, "a horn of plenty spilling pumpkin, wheat and fruit (capstone)"),
 ("Farming.b2.r1a", "B2R1a", "yield", animal_friend, "a cow's head + a green plus (more animal products)"),
 ("Farming.b2.r1b", "B2R1b", "yield", gentle_touch, "a sheep with a pink heart + a green plus (breeding)"),
 ("Farming.b2.r2.free", "B2R2Free", "ability", animal_call, "a cow's head with blue call arcs"),
 ("Farming.b2.r2a", "B2R2a", "ability", wide_call, "a gold cow bell with four blue arrows pushing outward (more range)"),
 ("Farming.b2.r2b", "B2R2b", "ability", calm_presence, "a sheep + an hourglass (calm for longer)"),
 ("Farming.b2.r3a", "B2R3a", "pet", pet_farmer, "a tan paw beside a wheat ear + a tan plus"),
 ("Farming.b2.r3b", "B2R3b", "yield", quality_feed, "a wooden feed bucket of grain, sparkle + green plus"),
 ("Farming.b2.r3c", "B2R3c", "yield", twin_birth, "two eggs side by side + a green plus (twins)"),
 ("Farming.b2.r4a", "B2R4a", "yield", barn_aura, "a cow's head and a gold emerald ring + a green plus (per accessory)"),
 ("Farming.b2.r4b", "B2R4b", "yield", shearing_master, "red-handled shears by a ball of wool + a green plus"),
 ("Farming.b2.r5a", "B2R5a", "yield", golden_egg, "a big golden egg, green sparkles"),
 ("Farming.b2.r5b", "B2R5b", "pet", beast_whisperer, "a tan paw with a pink heart + a tan up arrow (pet happiness)"),
 ("Farming.b2.r6", "B2R6", "yield", prize_herd, "a cow's head wearing a gold prize rosette (capstone)"),
 ("Farming.b3.r1a", "B3R1a", "yield", herb_lore, "an emerald herb sprig + a green plus"),
 ("Farming.b3.r1b", "B3R1b", "yield", pest_control, "a wheat ear behind a green shield (less crop loss)"),
 ("Farming.b3.r2.free", "B3R2Free", "ability", compost_boost, "a compost heap with a sprout and a blue burst"),
 ("Farming.b3.r2a", "B3R2a", "ability", rich_compost, "a compost heap + an hourglass (longer)"),
 ("Farming.b3.r2b", "B3R2b", "ability", quick_mix, "a compost heap + a blue cooldown clock"),
 ("Farming.b3.r3a", "B3R3a", "yield", rare_seed, "a glowing purple seed + a green plus"),
 ("Farming.b3.r3b", "B3R3b", "yield", watering, "a teal watering can pouring drops + a green plus"),
 ("Farming.b3.r3c", "B3R3c", "yield", gear_resonance, "a straw hat with a red band and green resonance arcs (per armor piece)"),
 ("Farming.b3.r4a", "B3R4a", "speed", hothouse, "a little glasshouse with a sprout + a teal up arrow"),
 ("Farming.b3.r4b", "B3R4b", "yield", seed_broker, "three seeds inside two green circling arrows (seed refund)"),
 ("Farming.b3.r5a", "B3R5a", "yield", mutation, "a wheat ear half gold, half purple (mutated) + a green plus"),
 ("Farming.b3.r5b", "B3R5b", "yield", bundling, "a tied crop bundle + green stacked tiles (bigger bundles)"),
 ("Farming.b3.r6", "B3R6", "yield", eden_patch, "a lush glowing plot of wheat and flowers (capstone)"),
]
