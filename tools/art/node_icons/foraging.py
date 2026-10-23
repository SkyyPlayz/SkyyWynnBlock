"""Foraging tree node icons (42) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py.
Drawn with the painter in make_tree_node_icons.py (imported read-only)."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents

TREE = "Foraging"


# ---------------------------------------------------------------- Woodcutter
def timber_sense():
    ic = Icon("TimberSense")
    tree(ic, 24, 60, 1.3)
    turn_arrow(ic, 24, 40, 30, -80, -10, "ability")
    for k in range(3):
        ic.add(circle(52, 40 + k * 7, 2.6), acc("ability"), base=0.75, bevel=0, line=True)
    return ic


def sharp_axe():
    ic = Icon("SharpAxe")
    arc(ic, 42, 46, 34, 205, 262, 3.0, "speed")
    arc(ic, 42, 46, 26, 210, 258, 2.6, "speed", base=0.55)
    lines(ic, [(4, 34, 12, 34), (6, 42, 13, 41)], "speed", 1.4)
    axe(ic, 50, 58, 34, 20, 1.25)
    return ic


def heartwood():
    ic = Icon("Heartwood")
    log(ic, 28, 46, 1.25)
    log(ic, 26, 26, 1.25)
    plus(ic, 53, 12, 1.1, "yield")
    spark(ic, 8, 10, "yield", 1)
    return ic


def timber():
    ic = Icon("Timber")
    tree(ic, 22, 60, 1.25)
    burst(ic, 26, 47, 12, 5, 8, acc("ability"), base=0.9)
    axe(ic, 58, 56, 38, 40, 1.15)
    return ic


def clean_cut():
    ic = Icon("CleanCut")
    sapling(ic, 26, 56, 1.55)
    plus(ic, 52, 14, 1.1, "yield")
    axe(ic, 58, 60, 48, 40, 0.75)
    return ic


def quick_fell():
    ic = Icon("QuickFell")
    burst(ic, 24, 40, 22, 8, 8, acc("ability"), rot=-67.5, base=0.62)
    burst(ic, 24, 40, 12, 5, 8, acc("ability"), base=0.92)
    log(ic, 44, 16, 0.95)
    plus(ic, 52, 48, 1.05, "ability")
    return ic


def giant_reach():
    ic = Icon("GiantReach")
    ic.add(rect(19, 26, 27, 60), "wood", mode="cyl", axis=(0, 1), base=0.5)
    tree(ic, 23, 34, 1.2)
    arrow(ic, 50, 20, 1.2, "ability")
    lines(ic, [(50, 30, 50, 56)], "ability", 1.6)
    ic.add(rect(43, 55, 57, 58), acc("ability"), base=0.7, bevel=0)
    return ic


def bark_collector():
    ic = Icon("BarkCollector")
    log(ic, 26, 40, 1.35)
    for (x, y, a) in ((14, 18, -20), (28, 14, 15)):
        ic.add(rot_ellipse(x, y, 7, 3, a), "wood", base=0.35, grad=0.5, bevel=0.6, line=True, pattern=hstripes(1.5, 0.08))
    drop(ic, 46, 20, 0.9, "honey")
    plus(ic, 53, 52, 0.95, "yield")
    return ic


def steady_rhythm():
    ic = Icon("SteadyRhythm")
    axe(ic, 26, 48, 32, 14, 1.15)
    wave = [(4, 53), (16, 53), (20, 46), (25, 60), (30, 50), (34, 53), (60, 53)]
    for k in range(len(wave) - 1):
        lines(ic, [(wave[k][0], wave[k][1], wave[k + 1][0], wave[k + 1][1])], "speed", 1.6)
    return ic


def replanter():
    ic = Icon("Replanter")
    sapling(ic, 32, 50, 1.45)
    turn_arrow(ic, 32, 36, 25, 200, 330, "yield")
    turn_arrow(ic, 32, 36, 25, 20, 150, "yield")
    return ic


def rare_grain():
    ic = Icon("RareGrain")
    ic.add(circle(30, 36, 22), "wood", mode="sphere", base=0.5, line=True)
    ic.add(circle(30, 36, 18), "cream", base=0.6, grad=0.4, bevel=0, cast=False,
           pattern=lambda x, y: -0.14 if int(math.hypot(x - 30, y - 36) / 3.2) % 2 else 0)
    spark(ic, 24, 30, "yield", 2)
    plus(ic, 53, 12, 1.05, "yield")
    return ic


def splinter_shield():
    ic = Icon("SplinterShield")
    shield(ic, 28, 34, 1.9, pal="wood")
    ic.add(rect(26, 16, 30, 52), "steel", base=0.55, bevel=0)
    for (x0, y0, x1, y1) in ((48, 10, 56, 6), (50, 20, 60, 20), (46, 30, 55, 34)):
        ic.add(capsule(x0, y0, x1, y1, 1.6), "cream", base=0.65, bevel=0, line=True)
    spark(ic, 10, 10, "health", 1)
    return ic


def lumber_surge():
    ic = Icon("LumberSurge")
    log(ic, 26, 44, 1.3)
    xp_orb(ic, 44, 18, 11)
    arrow(ic, 14, 16, 0.95, "xp")
    return ic


def forest_fortune():
    ic = Icon("ForestFortune")
    tree(ic, 24, 60, 1.3)
    xp_orb(ic, 48, 46, 11)
    spark(ic, 54, 10, "xp", 2)
    return ic


def echo_fell():
    ic = Icon("EchoFell")
    axe(ic, 22, 50, 30, 22, 1.0)
    turn_arrow(ic, 32, 32, 26, 160, 400, "ability", 3.2)
    return ic


def world_tree():
    ic = Icon("WorldTreesBlessing")
    ic.add(circle(32, 26, 24), "gold", mode="sphere", base=0.4, rim=False, bevel=0)
    ic.add(rect(27, 34, 37, 60), "wood", mode="cyl", axis=(0, 1), base=0.5)
    ic.add(union(circle(32, 20, 16), circle(18, 30, 11), circle(46, 30, 11)), "emerald", base=0.55, grad=0.6, bevel=1.0, line=True)
    ic.add(poly([(20, 60), (27, 52), (37, 52), (44, 60)]), "wood", base=0.4, grad=0.4)
    spark(ic, 8, 8, "ability", 2); spark(ic, 57, 9, "ability", 2); spark(ic, 53, 52, "yield", 1)
    return ic


# ---------------------------------------------------------------- Wildkeeper
def green_thumb():
    ic = Icon("GreenThumb")
    berries(ic, 26, 34, 1.5)
    plus(ic, 52, 14, 1.1, "yield")
    return ic


def foragers_pouch():
    ic = Icon("ForagersPouch")
    sack(ic, 26, 36, 1.35, pal="leather")
    leaf(ic, 18, 14, 0.8, -150)
    stack_badge(ic, 50, 46, 1.1, pal=acc("yield"))
    return ic


def pollen_puffs(ic, cx, cy, s=1.0):
    for (x, y, r) in ((-10, 0, 6), (0, -5, 7), (10, 0, 6), (-4, 4, 5), (5, 5, 5)):
        ic.add(circle(cx + x * s, cy + y * s, r * s), "wheat", mode="sphere", base=0.75, line=True)


def pollen_cloud():
    ic = Icon("PollenCloud")
    pollen_puffs(ic, 32, 18, 1.4)
    sapling(ic, 32, 58, 1.2)
    for (x, y) in ((14, 36), (48, 34), (24, 42)):
        ic.add(circle(x, y, 1.8), acc("ability"), base=0.8, bevel=0)
    return ic


def wide_bloom():
    ic = Icon("WideBloom")
    flower(ic, 32, 32, 1.4, petal="ruby")
    arrows_out(ic, 32, 32, 24, "ability", 0.85)
    return ic


def lingering_spores():
    ic = Icon("LingeringSpores")
    pollen_puffs(ic, 26, 26, 1.4)
    hourglass(ic, 50, 46, 1.0, "ability")
    return ic


def mushroom_hunter():
    ic = Icon("MushroomHunter")
    mushroom(ic, 26, 58, 1.8)
    plus(ic, 52, 14, 1.1, "yield")
    return ic


def small_paw(ic, cx, cy, s, pal="soil"):
    paw(ic, cx, cy, s, pal)


def beast_trails():
    ic = Icon("BeastTrails")
    for k, (x, y) in enumerate(((12, 54), (24, 44), (16, 32), (30, 22))):
        small_paw(ic, x, y, 0.42, "leather")
    eye(ic, 46, 40, 1.1)
    arc(ic, 46, 40, 16, -40, 40, 2.4, "ability")
    return ic


def wild_taste():
    ic = Icon("WildTaste")
    berries(ic, 24, 30, 1.35)
    hourglass(ic, 50, 46, 1.0, "buff")
    return ic


def pet_companion():
    ic = Icon("PetCompanion")
    paw(ic, 26, 36, 1.5, acc("pet"))
    leaf(ic, 50, 18, 1.1, -40)
    plus(ic, 52, 50, 0.9, "pet")
    return ic


def camouflage():
    ic = Icon("Camouflage")
    bush(ic, 30, 36, 1.45)
    for x in (24, 36):
        ic.add(circle(x, 34, 2.6), "cream", base=0.8, bevel=0, line=True)
        ic.add(circle(x, 34, 1.2), "navy", base=0.1, bevel=0, cast=False)
    arrow(ic, 53, 14, 0.9, "health", ang=90)
    return ic


def seasonal_bounty():
    ic = Icon("SeasonalBounty")
    leaf(ic, 22, 24, 1.6, -45, pal="honey")
    leaf(ic, 32, 40, 1.6, -135, pal="grass")
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def fey_bargain():
    ic = Icon("FeyBargain")
    wing(ic, 22, 30, 1.0, flip=True, pal="amethyst")
    wing(ic, 42, 30, 1.0, pal="amethyst")
    ic.add(circle(32, 32, 7), acc("buff"), mode="sphere", base=0.8, line=True)
    spark(ic, 10, 10, "yield", 2); spark(ic, 54, 54, "yield", 1)
    plus(ic, 52, 12, 0.9, "yield")
    return ic


def heart_of_the_grove():
    ic = Icon("HeartOfTheGrove")
    for (x, y, a) in ((12, 16, -130), (52, 16, -50), (10, 46, 150), (54, 46, 30)):
        leaf(ic, x, y, 1.0, a)
    ic.add(heart(32, 32, 1.75), "emerald", base=0.62, grad=0.6, bevel=1.1, line=True)
    paw(ic, 32, 32, 0.55, acc("pet"))
    spark(ic, 32, 6, "pet", 2)
    return ic


# ---------------------------------------------------------------- Trailblazer
def light_foot():
    ic = Icon("LightFoot")
    boot(ic, 36, 36, 1.4, pal="leather", line=True)
    leaf(ic, 52, 14, 0.8, -30)
    lines(ic, [(2, 24, 14, 24), (4, 32, 16, 32), (6, 40, 18, 40)], "speed", 1.5)
    return ic


def tool_tier_bonus():
    ic = Icon("ToolTierBonus")
    podium(ic, 4, 60)
    axe(ic, 34, 32, 46, 12, 0.85, head="gold")
    lines(ic, [(4, 22, 18, 22), (8, 30, 22, 30), (6, 14, 16, 14)], "speed", 1.5)
    return ic


def vine(ic, pts, pal="green"):
    for k in range(len(pts) - 1):
        ic.add(capsule(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1], 2.0), pal, base=0.55, grad=0.4, bevel=0, line=True)


def grapple_vine():
    ic = Icon("GrappleVine")
    tree(ic, 48, 40, 0.75)
    vine(ic, [(8, 58), (16, 48), (26, 40), (36, 30), (42, 24)])
    leaf(ic, 18, 46, 0.6, -60); leaf(ic, 32, 34, 0.6, 120)
    arrow(ic, 18, 22, 0.95, "ability", ang=-45)
    return ic


def long_vine():
    ic = Icon("LongVine")
    coil(ic, 22, 40, 1.3)
    vine(ic, [(34, 40), (44, 36), (50, 30)])
    arrow(ic, 52, 20, 1.0, "ability", ang=-45)
    return ic


def vine_recovery():
    ic = Icon("VineRecovery")
    coil(ic, 26, 30, 1.4)
    clock(ic, 49, 49, 10, "ability")
    return ic


def gear_resonance():
    ic = Icon("GearResonanceForaging")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 40, R, 200, 340, 2.6, "yield", base=b)
    helmet(ic, 32, 38, 1.0, pal="wood")
    leaf(ic, 24, 26, 0.7, -140); leaf(ic, 40, 26, 0.7, -40)
    return ic


def sturdy_hide():
    ic = Icon("SturdyHide")
    h = heart(32, 31, 2.25)
    ic.add(h, acc("health"), base=0.58, grad=0.6, bevel=1.1, line=True)
    ic.add(inter(h, Shape(lambda x, y: x + y * 0.4 > 44 and int((x * 0.7 + y) // 9) % 2 == 0, h.bb)), "wood", base=0.62, grad=0.5, bevel=0.7)
    ic.add(inter(h, Shape(lambda x, y: x + y * 0.4 > 44 and int((x * 0.7 + y) // 9) % 2 == 1, h.bb)), "wood", base=0.45, grad=0.5, bevel=0.7)
    return ic


def wind_walker():
    ic = Icon("WindWalker")
    feather(ic, 28, 34, 1.6, -50)
    lines(ic, [(50, 6, 50, 20), (57, 12, 57, 26), (43, 4, 43, 13)], "health", 1.6)
    waves(ic, 30, 58, 40, "speed", 1.3, 2.0, 2)
    return ic


def accessory_boughs():
    ic = Icon("AccessoryBoughs")
    leaf(ic, 22, 42, 1.6, -135)
    ring_item(ic, 42, 24, 1.25)
    plus(ic, 53, 52, 0.95, "yield")
    return ic


def hawk_eye():
    ic = Icon("HawkEye")
    feather(ic, 20, 46, 1.0, -40, pal="wood")
    eye(ic, 34, 28, 1.6, iris="honey")
    for R, b in ((26, 0.55), (21, 0.72)):
        arc(ic, 34, 28, R, -30, 30, 2.6, "ability", base=b)
    return ic


def hardwood_axe():
    ic = Icon("HardwoodAxe")
    axe(ic, 14, 58, 34, 20, 1.3, handle="mahog")
    shield(ic, 48, 44, 1.0, pal=acc("tool"))
    return ic


def vine_swing():
    ic = Icon("VineSwing")
    vine(ic, [(10, 4), (14, 16), (20, 26), (28, 34)])
    sword(ic, 56, 12, 30, 48, 1.0)
    for R, b in ((22, 0.62), (16, 0.8)):
        arc(ic, 40, 44, R, 20, 110, 2.6, "damage", base=b)
    return ic


def pathfinders_mantle():
    ic = Icon("PathfindersMantle")
    cape(ic, 32, 34, 1.45, pal="green")
    leaf(ic, 24, 30, 0.7, -60, pal="emerald"); leaf(ic, 40, 40, 0.7, 120, pal="emerald")
    spark(ic, 8, 10, "ability", 2); spark(ic, 56, 10, "ability", 1)
    return ic


ROWS = [
 ("Foraging.b1.r1.free", "B1R1Free", "ability", timber_sense, "a tree with a blue fall arrow and three log-count pips"),
 ("Foraging.b1.r1a", "B1R1a", "speed", sharp_axe, "an axe mid-swing with teal swoosh arcs + speed lines"),
 ("Foraging.b1.r1b", "B1R1b", "yield", heartwood, "two stacked logs + a green plus (double logs)"),
 ("Foraging.b1.r2.free", "B1R2Free", "ability", timber, "an axe striking a tree trunk with a blue burst (fell the whole tree)"),
 ("Foraging.b1.r2a", "B1R2a", "yield", clean_cut, "a sapling + a green plus, a small axe (more saplings)"),
 ("Foraging.b1.r2b", "B1R2b", "ability", quick_fell, "a blue burst + one more log with a blue plus (Tree Feller breaks 1 more)"),
 ("Foraging.b1.r2c", "B1R2c", "ability", giant_reach, "a very tall tree beside a blue up arrow (bigger trees)"),
 ("Foraging.b1.r3a", "B1R3a", "yield", bark_collector, "a log with bark strips and an amber resin drop + a green plus"),
 ("Foraging.b1.r3b", "B1R3b", "speed", steady_rhythm, "an upright axe over a steady teal rhythm line"),
 ("Foraging.b1.r3c", "B1R3c", "yield", replanter, "a sapling inside two green circling arrows (auto-replant)"),
 ("Foraging.b1.r4a", "B1R4a", "yield", rare_grain, "a log's end grain with its rings, a green sparkle + plus"),
 ("Foraging.b1.r4b", "B1R4b", "health", splinter_shield, "a wooden shield shedding splinters (block chance)"),
 ("Foraging.b1.r5a", "B1R5a", "xp", lumber_surge, "a log, a gold XP orb + a gold up arrow"),
 ("Foraging.b1.r5b", "B1R5b", "xp", forest_fortune, "a tree with a gold XP orb at its foot"),
 ("Foraging.b1.r5c", "B1R5c", "ability", echo_fell, "an axe inside a blue circling arrow (Timber! resets)"),
 ("Foraging.b1.r6", "B1R6", "ability", world_tree, "a great emerald tree glowing gold, sparkles (capstone)"),
 ("Foraging.b2.r1a", "B2R1a", "yield", green_thumb, "a cluster of red berries + a green plus"),
 ("Foraging.b2.r1b", "B2R1b", "yield", foragers_pouch, "a leather pouch with a leaf and green stacked slots"),
 ("Foraging.b2.r2.free", "B2R2Free", "ability", pollen_cloud, "a golden pollen cloud over a sapling, blue motes"),
 ("Foraging.b2.r2a", "B2R2a", "ability", wide_bloom, "a red flower with four blue arrows pushing outward (bigger radius)"),
 ("Foraging.b2.r2b", "B2R2b", "ability", lingering_spores, "a pollen cloud + an hourglass (longer)"),
 ("Foraging.b2.r3a", "B2R3a", "yield", mushroom_hunter, "a big red spotted mushroom + a green plus"),
 ("Foraging.b2.r3b", "B2R3b", "ability", beast_trails, "a trail of paw prints and an eye with a blue sense arc"),
 ("Foraging.b2.r3c", "B2R3c", "buff", wild_taste, "berries + a purple-sand hourglass (food effect lasts longer)"),
 ("Foraging.b2.r4a", "B2R4a", "pet", pet_companion, "a tan paw with a leaf + a tan plus"),
 ("Foraging.b2.r4b", "B2R4b", "health", camouflage, "two eyes peeking out of a bush, a red down arrow (less aggro range)"),
 ("Foraging.b2.r5a", "B2R5a", "yield", seasonal_bounty, "an autumn leaf and a green leaf + a green plus"),
 ("Foraging.b2.r5b", "B2R5b", "yield", fey_bargain, "a glowing fey with purple wings, green sparkles + plus"),
 ("Foraging.b2.r6", "B2R6", "pet", heart_of_the_grove, "an emerald heart with a tan paw, framed by leaves (capstone)"),
 ("Foraging.b3.r1a", "B3R1a", "speed", light_foot, "a boot with a leaf and teal speed lines"),
 ("Foraging.b3.r1b", "B3R1b", "speed", tool_tier_bonus, "a gold axe on a copper / iron / gold podium + speed lines"),
 ("Foraging.b3.r2.free", "B3R2Free", "ability", grapple_vine, "a vine reaching up to a tree with a blue travel arrow"),
 ("Foraging.b3.r2a", "B3R2a", "ability", long_vine, "a coiled vine reaching out to a blue arrow (more range)"),
 ("Foraging.b3.r2b", "B3R2b", "ability", vine_recovery, "a coiled vine + a blue cooldown clock"),
 ("Foraging.b3.r3a", "B3R3a", "yield", gear_resonance, "a bark helmet with leaves and green resonance arcs (per armor piece)"),
 ("Foraging.b3.r3b", "B3R3b", "health", sturdy_hide, "a red heart half covered in bark plates (+ max Health)"),
 ("Foraging.b3.r3c", "B3R3c", "health", wind_walker, "a feather drifting down, red fall lines, a teal breeze"),
 ("Foraging.b3.r4a", "B3R4a", "yield", accessory_boughs, "a gold emerald ring over a leaf + a green plus (per accessory)"),
 ("Foraging.b3.r4b", "B3R4b", "ability", hawk_eye, "an amber hawk eye with a feather and blue range arcs"),
 ("Foraging.b3.r5a", "B3R5a", "tool", hardwood_axe, "an axe on a dark hardwood handle + a soft-white shield"),
 ("Foraging.b3.r5b", "B3R5b", "damage", vine_swing, "a sword swung from a vine, orange slash arcs"),
 ("Foraging.b3.r6", "B3R6", "ability", pathfinders_mantle, "a green trail cloak with a gold clasp and leaves (capstone)"),
]
