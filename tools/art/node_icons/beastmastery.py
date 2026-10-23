"""Beastmastery tree node icons (40) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents
from node_icons.combat import slashes
from node_icons.cooking import crown

TREE = "Beastmastery"

PAW = acc("pet")


def war_horn(ic, cx, cy, s=1.0):
    ic.add(poly([(cx - 16 * s, cy + 6 * s), (cx - 12 * s, cy - 2 * s), (cx, cy - 6 * s), (cx + 14 * s, cy - 12 * s), (cx + 16 * s, cy - 2 * s),
                 (cx + 2 * s, cy + 4 * s), (cx - 10 * s, cy + 10 * s)]), "bone", base=0.6, grad=0.6, bevel=1.0, line=True)
    ic.add(ellipse(cx + 15 * s, cy - 7 * s, 3 * s, 6 * s), "bone", base=0.3, bevel=0, line=True)
    for x in (-6, 4):
        ic.add(rot_ellipse(cx + x * s, cy + (1 - x * 0.35) * s, 1.6 * s, 6 * s, -25), "gold", base=0.65, bevel=0)


def mound(ic, cx, by, s=1.0):
    ic.add(inter(ellipse(cx, by, 22 * s, 14 * s), rect(cx - 23 * s, by - 15 * s, cx + 23 * s, by)), "soil", base=0.5, grad=0.6, line=True,
           pattern=lambda x, y: 0.07 * math.sin(x * 1.5) * math.sin(y * 1.2))


def nest(ic, cx, cy, s=1.0):
    egg(ic, cx, cy - 4 * s, 1.0 * s, pal="cream")
    ic.add(inter(ellipse(cx, cy, 16 * s, 9 * s), rect(cx - 17 * s, cy - 2 * s, cx + 17 * s, cy + 10 * s)), "wood", base=0.5, grad=0.5, line=True,
           pattern=lambda x, y: -0.12 if int((x - cx) * 0.6 + (y - cy) * 1.4) % 3 == 0 else 0)


def roots(ic, cx, cy, s=1.0):
    for (x1, y1) in ((-16, 14), (-6, 18), (6, 18), (16, 12)):
        ic.add(capsule(cx, cy - 6 * s, cx + x1 * s, cy + y1 * s, 2.2 * s), "wood", base=0.5, grad=0.4, bevel=0, line=True)
    ic.add(rect(cx - 4 * s, cy - 16 * s, cx + 4 * s, cy - 4 * s), "wood", mode="cyl", axis=(0, 1), base=0.55, line=True)


# ---------------------------------------------------------------- Bonded Fangs
def bond_of_beasts():
    ic = Icon("BondOfBeasts")
    paw(ic, 24, 38, 1.45, PAW)
    sword(ic, 60, 4, 44, 24, 0.6)
    xp_orb(ic, 52, 48, 8)
    return ic


def whistle_training():
    ic = Icon("WhistleTraining")
    whistle(ic, 28, 30, 1.4)
    for R, b in ((10, 0.8), (16, 0.62)):
        arc(ic, 16, 26, R, 190, 250, 2.2, "pet", base=b)
    xp_orb(ic, 50, 50, 8)
    return ic


def fang_familiar():
    ic = Icon("FangFamiliar")
    fang(ic, 26, 30, 1.8, ang=10)
    paw(ic, 48, 20, 0.55, PAW)
    xp_orb(ic, 50, 50, 8)
    return ic


def rally_cry():
    ic = Icon("RallyCry")
    war_horn(ic, 24, 36, 1.2)
    for R, b in ((10, 0.85), (16, 0.68), (22, 0.52)):
        arc(ic, 42, 28, R, -60, 30, 2.6, "ability", base=b)
    return ic


def long_rally():
    ic = Icon("LongRally")
    war_horn(ic, 26, 28, 1.1)
    hourglass(ic, 50, 46, 1.0, "ability")
    return ic


def pack_speed():
    ic = Icon("PackSpeed")
    paw(ic, 34, 36, 1.45, PAW)
    lines(ic, [(2, 24, 14, 24), (4, 34, 16, 34), (6, 44, 18, 44)], "speed", 1.5)
    return ic


def battle_bond():
    ic = Icon("BattleBond")
    paw(ic, 24, 40, 1.35, PAW)
    sword(ic, 58, 6, 40, 30, 0.7)
    plus(ic, 52, 50, 0.9, "pet")
    return ic


def pack_instinct():
    ic = Icon("PackInstinct")
    paw(ic, 18, 24, 0.75, PAW); paw(ic, 40, 22, 0.75, PAW); paw(ic, 28, 46, 0.85, PAW)
    plus(ic, 53, 50, 0.95, "damage")
    return ic


def guard_dog():
    ic = Icon("GuardDog")
    shield(ic, 34, 32, 1.7, pal=acc("health"))
    paw(ic, 34, 30, 0.7, PAW)
    return ic


def alphas_mark():
    ic = Icon("AlphasMark")
    paw(ic, 26, 40, 1.4, PAW)
    burst(ic, 48, 16, 10, 4, 4, acc("damage"), base=0.75, line=True)
    return ic


def fang_tempering():
    ic = Icon("FangTempering")
    fang(ic, 26, 30, 1.7, pal="flame", ang=10)
    xp_orb(ic, 50, 48, 9)
    return ic


def predators_gift():
    ic = Icon("PredatorsGift")
    slashes(ic, 26, 32, "pet", 3, 1.25)
    arrow(ic, 52, 46, 1.0, "pet")
    return ic


def rapid_learner():
    ic = Icon("RapidLearner")
    xp_orb(ic, 30, 34, 15)
    paw(ic, 50, 14, 0.5, PAW)
    lines(ic, [(46, 34, 60, 34), (44, 42, 58, 42), (46, 50, 60, 50)], "pet", 1.5)
    return ic


def apex_bond():
    ic = Icon("ApexBond")
    paw(ic, 32, 40, 1.5, PAW)
    crown(ic, 32, 12, 1.1)
    ic.add(heart(52, 52, 0.55), acc("health"), base=0.62, grad=0.5, bevel=0.6, line=True)
    return ic


# ---------------------------------------------------------------- Deep Burrow
def diggers_calling():
    ic = Icon("DiggersCalling")
    paw(ic, 24, 38, 1.35, PAW)
    pick(ic, 58, 34, 50, 12, arm=9, hr=2.4, r=1.7)
    xp_orb(ic, 52, 50, 8)
    return ic


def cave_nose():
    ic = Icon("CaveNose")
    ore_chunk(ic, 42, 42, 0.9)
    for k in range(3):
        waves(ic, 16, 14 + k * 9, 24, "ability", 1.3, 2.0, 2)
    return ic


def pet_dig():
    ic = Icon("PetDig")
    mound(ic, 32, 60, 1.25)
    ore_cube(ic, 8, 22, 10); ore_cube(ic, 44, 18, 11)
    paw(ic, 30, 30, 0.75, PAW)
    burst(ic, 30, 8, 6, 2.5, 8, acc("ability"), base=0.85)
    return ic


def deeper_dig():
    ic = Icon("DeeperDig")
    mound(ic, 26, 58, 1.05)
    ore_cube(ic, 18, 28, 13)
    plus(ic, 52, 16, 1.0, "ability")
    return ic


def quick_dig():
    ic = Icon("QuickDig")
    mound(ic, 26, 46, 1.0)
    paw(ic, 26, 24, 0.6, PAW)
    clock(ic, 49, 49, 10, "ability")
    return ic


def stone_bond():
    ic = Icon("StoneBond")
    paw(ic, 28, 36, 1.5, "stone")
    plus(ic, 52, 50, 0.95, "pet")
    return ic


def ore_sniffer():
    ic = Icon("OreSniffer")
    ore_chunk(ic, 24, 40, 1.15, line=True)
    paw(ic, 48, 16, 0.55, PAW)
    plus(ic, 53, 50, 0.95, "yield")
    return ic


def glimmering_coat():
    ic = Icon("GlimmeringCoat")
    for a in range(0, 360, 45):
        x0, y0 = 32 + 18 * math.cos(math.radians(a)), 34 + 18 * math.sin(math.radians(a))
        x1, y1 = 32 + 27 * math.cos(math.radians(a)), 34 + 27 * math.sin(math.radians(a))
        lines(ic, [(x0, y0, x1, y1)], "ability", 1.7)
    paw(ic, 32, 36, 1.2, "lamp")
    return ic


def gem_hound():
    ic = Icon("GemHound")
    gem(ic, 30, 30, 1.3, "emerald", line=True)
    paw(ic, 14, 50, 0.5, PAW)
    plus(ic, 53, 50, 0.95, "yield")
    return ic


def deep_tempering():
    ic = Icon("DeepTempering")
    ore_chunk(ic, 26, 38, 1.15, ore="flame", line=True)
    xp_orb(ic, 50, 16, 9)
    return ic


def earthen_gift():
    ic = Icon("EarthenGift")
    ic.add(mountain_shape(30, 60, 0.85), "stone", base=0.5, grad=0.6, pattern=hstripes(5, 0.07, 2), line=True)
    paw(ic, 30, 46, 0.6, PAW)
    arrow(ic, 52, 16, 1.0, "pet")
    return ic


def burrow_rush():
    ic = Icon("BurrowRush")
    pick(ic, 44, 58, 36, 22, arm=15)
    paw(ic, 16, 46, 0.55, PAW)
    lines(ic, [(4, 14, 16, 14), (6, 22, 18, 22), (4, 30, 14, 30)], "speed", 1.5)
    return ic


def heart_of_stone():
    ic = Icon("HeartOfStone")
    ic.add(heart(32, 30, 2.0), "stone", base=0.55, grad=0.6, bevel=1.1, line=True, pattern=hstripes(5, 0.06))
    gem(ic, 32, 30, 0.6, "ruby", line=True)
    paw(ic, 52, 52, 0.45, PAW)
    spark(ic, 8, 10, "pet", 2)
    return ic


# ---------------------------------------------------------------- Wild Roots
def green_companion():
    ic = Icon("GreenCompanion")
    paw(ic, 24, 40, 1.35, PAW)
    leaf(ic, 48, 20, 1.0, -40)
    xp_orb(ic, 52, 50, 8)
    return ic


def gentle_hand():
    ic = Icon("GentleHand")
    nest(ic, 28, 40, 1.4)
    plus(ic, 53, 14, 1.0, "pet")
    return ic


def pet_harvest():
    ic = Icon("PetHarvest")
    wheat(ic, 14, 54, 1.0, lean=-2)
    log(ic, 44, 50, 0.7)
    paw(ic, 32, 28, 0.85, PAW)
    burst(ic, 50, 12, 7, 3, 8, acc("ability"), base=0.85)
    return ic


def wide_harvest():
    ic = Icon("WideHarvest")
    paw(ic, 32, 34, 0.9, PAW)
    arrows_out(ic, 32, 32, 24, "ability", 0.8)
    return ic


def quick_harvest():
    ic = Icon("QuickHarvest")
    wheat(ic, 20, 56, 1.2)
    paw(ic, 34, 22, 0.5, PAW)
    clock(ic, 49, 49, 10, "ability")
    return ic


def verdant_bond():
    ic = Icon("VerdantBond")
    paw(ic, 24, 40, 1.35, PAW)
    wheat(ic, 48, 34, 0.75, lean=2)
    plus(ic, 52, 52, 0.85, "pet")
    return ic


def wild_bond():
    ic = Icon("WildBond")
    paw(ic, 24, 40, 1.35, PAW)
    tree(ic, 48, 34, 0.55)
    plus(ic, 52, 52, 0.85, "pet")
    return ic


def pet_picnic():
    ic = Icon("PetPicnic")
    ic.add(poly([(4, 50), (36, 44), (56, 54), (24, 60)]), "red", base=0.6, grad=0.5, line=True,
           pattern=lambda x, y: -0.16 if (int(x / 5) + int(y / 5)) % 2 else 0)
    drumstick(ic, 22, 36, 0.7)
    bone(ic, 34, 40, 48, 32, 0.8)
    xp_orb(ic, 50, 14, 8)
    return ic


def fertile_trail():
    ic = Icon("FertileTrail")
    for (x, y) in ((12, 54), (26, 44), (16, 30)):
        paw(ic, x, y, 0.4, "soil")
    sapling(ic, 40, 40, 0.8)
    plus(ic, 53, 50, 0.95, "yield")
    return ic


def roots_tempering():
    ic = Icon("RootsTempering")
    roots(ic, 26, 40, 1.2)
    xp_orb(ic, 50, 16, 9)
    return ic


def natures_gift():
    ic = Icon("NaturesGift")
    flower(ic, 22, 22, 1.0, petal="ruby")
    paw(ic, 30, 44, 0.85, PAW)
    arrow(ic, 52, 46, 1.0, "pet")
    return ic


def gentle_giant():
    ic = Icon("GentleGiant")
    paw(ic, 28, 38, 1.7, PAW)
    gem(ic, 50, 14, 0.45, "diamond", line=True)
    plus(ic, 53, 52, 0.85, "pet")
    return ic


def kinship_of_the_wild():
    ic = Icon("KinshipOfTheWild")
    ic.add(heart(32, 34, 1.0), acc("health"), base=0.62, grad=0.5, bevel=0.8, line=True)
    for a in (-90, 30, 150):
        paw(ic, 32 + 19 * math.cos(math.radians(a)), 33 + 19 * math.sin(math.radians(a)), 0.5, PAW)
    spark(ic, 8, 10, "pet", 2); spark(ic, 56, 56, "pet", 1)
    return ic


ROWS = [
 ("Beastmastery.b1.r1.free", "B1R1Free", "pet", bond_of_beasts, "a tan paw, a small sword and a gold XP orb (pet XP per kill)"),
 ("Beastmastery.b1.r1a", "B1R1a", "pet", whistle_training, "a steel training whistle with tan call arcs + a gold XP orb"),
 ("Beastmastery.b1.r1b", "B1R1b", "pet", fang_familiar, "a big fang and a tan paw + a gold XP orb"),
 ("Beastmastery.b1.r2.free", "B1R2Free", "ability", rally_cry, "a bone war horn blowing blue call arcs"),
 ("Beastmastery.b1.r2a", "B1R2a", "ability", long_rally, "a war horn + an hourglass (longer)"),
 ("Beastmastery.b1.r2b", "B1R2b", "speed", pack_speed, "a tan paw with teal speed lines (pet attack speed)"),
 ("Beastmastery.b1.r3a", "B1R3a", "pet", battle_bond, "a tan paw and a sword + a tan plus (Combat pet stats)"),
 ("Beastmastery.b1.r3b", "B1R3b", "damage", pack_instinct, "three tan paws + an orange plus (damage per pet)"),
 ("Beastmastery.b1.r3c", "B1R3c", "health", guard_dog, "a tan paw on a red shield (pet takes some damage)"),
 ("Beastmastery.b1.r4a", "B1R4a", "damage", alphas_mark, "a tan paw and an orange crit star (pet crits)"),
 ("Beastmastery.b1.r4b", "B1R4b", "pet", fang_tempering, "a glowing hot fang + a gold XP orb"),
 ("Beastmastery.b1.r5a", "B1R5a", "pet", predators_gift, "three tan claw slashes + a tan up arrow (all Combat pet stats)"),
 ("Beastmastery.b1.r5b", "B1R5b", "pet", rapid_learner, "a big gold XP orb with a tan paw and tan speed lines (all-pet XP)"),
 ("Beastmastery.b1.r6", "B1R6", "pet", apex_bond, "a crowned tan paw with a red heart (capstone)"),
 ("Beastmastery.b2.r1a", "B2R1a", "pet", diggers_calling, "a tan paw and a pickaxe + a gold XP orb (Mining pet XP)"),
 ("Beastmastery.b2.r1b", "B2R1b", "ability", cave_nose, "blue scent trails drifting to an ore chunk (ore detection)"),
 ("Beastmastery.b2.r2.free", "B2R2Free", "ability", pet_dig, "a tan paw digging a soil mound, ore cubes flying, blue burst"),
 ("Beastmastery.b2.r2a", "B2R2a", "ability", deeper_dig, "an ore cube on a dug mound + a blue plus (one more ore)"),
 ("Beastmastery.b2.r2b", "B2R2b", "ability", quick_dig, "a paw over a dug mound + a blue cooldown clock"),
 ("Beastmastery.b2.r3a", "B2R3a", "pet", stone_bond, "a stone-grey paw + a tan plus (Mining pet stats)"),
 ("Beastmastery.b2.r3b", "B2R3b", "yield", ore_sniffer, "an ore chunk and a tan paw + a green plus (ore yield)"),
 ("Beastmastery.b2.r3c", "B2R3c", "ability", glimmering_coat, "a glowing golden paw with blue light rays (lights caves)"),
 ("Beastmastery.b2.r4a", "B2R4a", "yield", gem_hound, "a cut emerald and a small paw + a green plus (gem chance)"),
 ("Beastmastery.b2.r4b", "B2R4b", "pet", deep_tempering, "an ore chunk with glowing hot ore + a gold XP orb"),
 ("Beastmastery.b2.r5a", "B2R5a", "pet", earthen_gift, "a tan paw on a stone mountain + a tan up arrow"),
 ("Beastmastery.b2.r5b", "B2R5b", "speed", burrow_rush, "a pickaxe and a tan paw with teal speed lines (mining speed)"),
 ("Beastmastery.b2.r6", "B2R6", "pet", heart_of_stone, "a stone heart set with a ruby, a tan paw (capstone)"),
 ("Beastmastery.b3.r1a", "B3R1a", "pet", green_companion, "a tan paw and a leaf + a gold XP orb (Farming / Foraging pet XP)"),
 ("Beastmastery.b3.r1b", "B3R1b", "pet", gentle_hand, "an egg in a twig nest + a tan plus (one more Hatchery slot)"),
 ("Beastmastery.b3.r2.free", "B3R2Free", "ability", pet_harvest, "a tan paw between a wheat ear and a log, blue burst"),
 ("Beastmastery.b3.r2a", "B3R2a", "ability", wide_harvest, "a tan paw with four blue arrows pushing outward (bigger radius)"),
 ("Beastmastery.b3.r2b", "B3R2b", "ability", quick_harvest, "a wheat ear and a paw + a blue cooldown clock"),
 ("Beastmastery.b3.r3a", "B3R3a", "pet", verdant_bond, "a tan paw and a wheat ear + a tan plus (Farming pet stats)"),
 ("Beastmastery.b3.r3b", "B3R3b", "pet", wild_bond, "a tan paw and a small tree + a tan plus (Foraging pet stats)"),
 ("Beastmastery.b3.r3c", "B3R3c", "pet", pet_picnic, "a checked picnic cloth with a drumstick and a bone + a gold XP orb"),
 ("Beastmastery.b3.r4a", "B3R4a", "yield", fertile_trail, "a trail of paw prints to a sprout + a green plus"),
 ("Beastmastery.b3.r4b", "B3R4b", "pet", roots_tempering, "a tangle of roots + a gold XP orb"),
 ("Beastmastery.b3.r5a", "B3R5a", "pet", natures_gift, "a red flower and a tan paw + a tan up arrow"),
 ("Beastmastery.b3.r5b", "B3R5b", "pet", gentle_giant, "a big tan paw with a diamond + a tan plus (Rare or better pets)"),
 ("Beastmastery.b3.r6", "B3R6", "pet", kinship_of_the_wild, "three tan paws circling a red heart (capstone)"),
]
