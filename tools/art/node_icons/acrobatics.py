"""Acrobatics tree node icons (19) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents

TREE = "Acrobatics"


def cat_face(ic, cx, cy, s=1.0, pal="honey"):
    ic.add(union(circle(cx, cy, 13 * s), poly([(cx - 12 * s, cy - 4 * s), (cx - 11 * s, cy - 17 * s), (cx - 3 * s, cy - 11 * s)]),
                 poly([(cx + 12 * s, cy - 4 * s), (cx + 11 * s, cy - 17 * s), (cx + 3 * s, cy - 11 * s)])), pal, base=0.6, grad=0.6, bevel=1.0, line=True)
    for x in (-5, 5):
        ic.add(ellipse(cx + x * s, cy - 1 * s, 2.4 * s, 3.2 * s), "emerald", base=0.7, bevel=0, cast=False)
        ic.add(ellipse(cx + x * s, cy - 1 * s, 0.8 * s, 2.4 * s), "navy", base=0.1, bevel=0, cast=False)
    ic.add(poly([(cx - 2 * s, cy + 4 * s), (cx + 2 * s, cy + 4 * s), (cx, cy + 6 * s)]), "ruby", base=0.6, bevel=0, cast=False)


def roll():
    ic = Icon("Roll")
    boot(ic, 29, 36, 1.3, line=True)
    turn_arrow(ic, 32, 32, 25, 150, 400, "ability", 3.2)
    return ic


def quick_roll():
    ic = Icon("QuickRoll")
    turn_arrow(ic, 26, 28, 18, 150, 400, "ability", 3.0)
    clock(ic, 49, 49, 10, "ability")
    return ic


def long_leap():
    ic = Icon("LongLeap")
    arc(ic, 32, 60, 24, 190, 300, 2.4, "speed", base=0.5)
    boot(ic, 40, 26, 1.1, line=True)
    arrow(ic, 14, 22, 1.3, "speed")
    lines(ic, [(14, 32, 14, 50)], "speed", 1.6)
    return ic


def wall_grip():
    ic = Icon("WallGrip")
    stone_wall(ic, 4, 2, 24, 62)
    gauntlet(ic, 36, 30, 1.3, pal="leather")
    lines(ic, [(52, 44, 52, 54), (44, 50, 44, 58)], "ability", 1.4)
    return ic


def strong_grip():
    ic = Icon("StrongGrip")
    gauntlet(ic, 26, 30, 1.4, pal="leather")
    hourglass(ic, 50, 46, 1.0, "ability")
    return ic


def chain_jump():
    ic = Icon("ChainJump")
    wing(ic, 22, 34, 0.9, flip=True)
    wing(ic, 42, 34, 0.9)
    boot(ic, 32, 34, 0.9, line=True)
    arrow(ic, 32, 8, 1.0, "speed")
    return ic


def light_feet():
    ic = Icon("LightFeet")
    feather(ic, 22, 20, 1.0, -30)
    boot(ic, 30, 40, 1.35, line=True)
    lines(ic, [(54, 6, 54, 18), (60, 12, 60, 24)], "health", 1.6)
    return ic


def combat_flip():
    ic = Icon("CombatFlip")
    turn_arrow(ic, 30, 34, 20, 120, 380, "speed", 3.0)
    boot(ic, 30, 34, 0.75, line=True)
    arrow(ic, 54, 50, 0.9, "speed", ang=0)
    return ic


def gear_resonance():
    ic = Icon("GearResonanceAcrobatics")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 38, R, 200, 340, 2.6, "speed", base=b)
    helmet(ic, 32, 38, 1.0, pal="leather")
    feather(ic, 44, 20, 0.6, -60)
    return ic


def phantom_step():
    ic = Icon("PhantomStep")
    ic.add(boot_shape(18, 36, 1.35), acc("buff"), base=0.5, bevel=0, cast=False, line=True)
    boot(ic, 36, 38, 1.35, line=True)
    burst(ic, 52, 12, 8, 3.2, 4, "gold", base=0.9, line=True)
    spark(ic, 10, 54, "ability", 2)
    return ic


def adrenaline():
    ic = Icon("Adrenaline")
    ic.add(heart(26, 30, 1.5), "ruby", base=0.6, grad=0.6, bevel=1.0, line=True)
    bolt(ic, 27, 30, 0.75)
    lines(ic, [(46, 24, 60, 24), (48, 32, 62, 32), (46, 40, 60, 40)], "speed", 1.5)
    return ic


def close_call():
    ic = Icon("CloseCall")
    sword(ic, 54, 10, 22, 50, 1.0)
    turn_arrow(ic, 26, 26, 16, 100, 250, "speed", 2.6)
    for R, b in ((20, 0.62), (14, 0.8)):
        arc(ic, 40, 44, R, 20, 110, 2.6, "damage", base=b)
    return ic


def parkour_rush():
    ic = Icon("ParkourRush")
    for k in range(3):
        ic.add(rect(4 + k * 18, 56 - k * 10, 20 + k * 18, 62), "stone", base=0.5 + 0.05 * k, grad=0.5, line=True)
    boot(ic, 44, 18, 0.8, line=True)
    for k in range(3):
        arc(ic, 12 + k * 18, 46 - k * 10, 8, 200, 340, 2.0, "speed")
    return ic


def rush_time():
    ic = Icon("RushTime")
    boot(ic, 24, 30, 1.35, line=True)
    lines(ic, [(2, 20, 10, 20), (2, 28, 10, 28)], "speed", 1.4)
    hourglass(ic, 50, 46, 1.0, "speed")
    return ic


def steady_land():
    ic = Icon("SteadyLand")
    ic.add(rect(4, 52, 60, 60), "stone", base=0.45, grad=0.4)
    boot(ic, 28, 37, 1.45, line=True)
    for (x, y, r) in ((12, 50, 4), (50, 50, 4)):
        ic.add(circle(x, y, r), "cloud", mode="sphere", base=0.6)
    arrow(ic, 52, 16, 0.95, "health", ang=90)
    return ic


def accessory_sprint():
    ic = Icon("AccessorySprint")
    bolt(ic, 24, 34, 1.5)
    ring_item(ic, 46, 22, 1.0)
    plus(ic, 53, 52, 0.9, "speed")
    return ic


def evade_master():
    ic = Icon("EvadeMaster")
    boot(ic, 20, 34, 1.4, line=True)
    arrow(ic, 50, 24, 1.0, "speed", ang=0)
    arrow(ic, 50, 42, 1.0, "speed", ang=0)
    return ic


def fearless():
    ic = Icon("Fearless")
    ic.add(poly([(2, 30), (26, 30), (30, 34), (28, 62), (2, 62)]), "stone", base=0.5, grad=0.6, line=True, pattern=hstripes(5, 0.07))
    boot(ic, 42, 24, 1.15, line=True)
    lines(ic, [(40, 42, 40, 54), (48, 44, 48, 58)], "health", 1.6)
    return ic


def cats_nine_lives():
    ic = Icon("CatsNineLives")
    cat_face(ic, 28, 34, 1.4)
    ic.add(heart(52, 14, 0.62), acc("health"), base=0.65, grad=0.5, bevel=0.6, line=True)
    spark(ic, 52, 52, "health", 2)
    return ic


ROWS = [
 ("Acrobatics.b1.r1.free", "B1R1Free", "ability", roll, "a boot inside a blue rolling arrow (dodge roll)"),
 ("Acrobatics.b1.r1a", "B1R1a", "ability", quick_roll, "a blue roll arrow + a blue cooldown clock"),
 ("Acrobatics.b1.r1b", "B1R1b", "speed", long_leap, "a boot leaping on a teal arc beside a teal up arrow (jump height)"),
 ("Acrobatics.b1.r2.free", "B1R2Free", "ability", wall_grip, "a leather glove gripping a stone wall, blue slide marks"),
 ("Acrobatics.b1.r2a", "B1R2a", "ability", strong_grip, "a gripping glove + an hourglass (longer wall slide)"),
 ("Acrobatics.b1.r2b", "B1R2b", "speed", chain_jump, "a winged boot with a teal up arrow (mid-air jump)"),
 ("Acrobatics.b1.r3a", "B1R3a", "health", light_feet, "a feather above a boot, red fall lines (less fall damage)"),
 ("Acrobatics.b1.r3b", "B1R3b", "speed", combat_flip, "a boot inside a teal flip arrow + a push arrow (dodge push)"),
 ("Acrobatics.b1.r3c", "B1R3c", "speed", gear_resonance, "a feathered leather cap with teal resonance arcs"),
 ("Acrobatics.b1.r4", "B1R4", "ability", phantom_step, "a boot leaving a purple phantom copy, gold star (capstone)"),
 ("Acrobatics.b2.r1a", "B2R1a", "speed", adrenaline, "a red heart with a lightning bolt and teal speed lines"),
 ("Acrobatics.b2.r1b", "B2R1b", "damage", close_call, "a sword after a teal dodge arrow, orange slash arcs"),
 ("Acrobatics.b2.r2.free", "B2R2Free", "speed", parkour_rush, "a boot bounding up three stone steps on teal arcs"),
 ("Acrobatics.b2.r2a", "B2R2a", "speed", rush_time, "a running boot + a teal-sand hourglass (longer rush)"),
 ("Acrobatics.b2.r2b", "B2R2b", "health", steady_land, "a boot landing softly in dust puffs, a red down arrow"),
 ("Acrobatics.b2.r3a", "B2R3a", "speed", accessory_sprint, "a Stamina lightning bolt and a gold ring + a teal plus (per accessory)"),
 ("Acrobatics.b2.r3b", "B2R3b", "speed", evade_master, "a boot with two teal push arrows"),
 ("Acrobatics.b2.r3c", "B2R3c", "health", fearless, "a boot stepping off a cliff edge, red fall lines"),
 ("Acrobatics.b2.r4", "B2R4", "health", cats_nine_lives, "a green-eyed cat's face with a red heart (capstone)"),
]
