"""Exploration tree node icons (18) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents

TREE = "Exploration"


def spyglass(ic, x0, y0, x1, y1, s=1.0):
    ux, uy = unit(x0, y0, x1, y1)
    L = math.hypot(x1 - x0, y1 - y0)
    for k, (t0, t1, r, pal) in enumerate(((0.0, 0.4, 3.2, "gold"), (0.38, 0.72, 4.2, "mahog"), (0.7, 1.0, 5.2, "gold"))):
        ic.add(capsule(x0 + ux * L * t0, y0 + uy * L * t0, x0 + ux * L * t1, y0 + uy * L * t1, r * s), pal, mode="cyl", axis=(ux, uy), base=0.58,
               line=True)
    ic.add(circle(x1, y1, 4.2 * s), "glass", base=0.75, bevel=0, line=True)


def tower(ic, cx, by, s=1.0):
    ic.add(rect(cx - 7 * s, by - 26 * s, cx + 7 * s, by), "stone", base=0.5, grad=0.6, line=True, pattern=hstripes(4 * s, 0.07))
    ic.add(union(rect(cx - 9 * s, by - 32 * s, cx + 9 * s, by - 25 * s),
                 *[rect(cx + x * s, by - 35 * s, cx + (x + 3.4) * s, by - 31 * s) for x in (-9, -3.5, 2, 5.6)]), "stone", base=0.65, grad=0.5,
           line=True)
    ic.add(rrect(cx - 2 * s, by - 20 * s, cx + 2 * s, by - 14 * s, 1.5 * s), "navy", base=0.15, bevel=0, cast=False)


def globe(ic, cx, cy, r):
    ic.add(circle(cx, cy, r), "water", mode="sphere", base=0.6, line=True)
    land = union(ellipse(cx - r * 0.35, cy - r * 0.3, r * 0.35, r * 0.28), ellipse(cx + r * 0.3, cy + r * 0.25, r * 0.4, r * 0.3),
                 ellipse(cx + r * 0.45, cy - r * 0.5, r * 0.2, r * 0.15))
    ic.add(inter(land, circle(cx, cy, r - 1)), "grass", base=0.6, grad=0.6, bevel=0.6, rim=False)


def glider(ic, cx, cy, s=1.0):
    ic.add(poly([(cx - 24 * s, cy + 4 * s), (cx, cy - 10 * s), (cx + 24 * s, cy + 4 * s), (cx + 12 * s, cy + 1 * s), (cx, cy + 3 * s),
                 (cx - 12 * s, cy + 1 * s)]), "red", base=0.6, grad=0.6, line=True, pattern=lambda x, y: -0.12 if int((x - cx) / (6 * s)) % 2 else 0)
    ic.add(capsule(cx, cy - 8 * s, cx, cy + 14 * s, 1.0 * s), "wood", base=0.5, bevel=0)
    ic.add(capsule(cx - 6 * s, cy + 14 * s, cx + 6 * s, cy + 14 * s, 1.3 * s), "wood", base=0.55, bevel=0, line=True)


def rain_cloud(ic, cx, cy, s=1.0):
    ic.add(union(circle(cx - 8 * s, cy, 7 * s), circle(cx, cy - 4 * s, 9 * s), circle(cx + 9 * s, cy, 7 * s), rect(cx - 8 * s, cy, cx + 9 * s, cy + 7 * s)),
           "stone", base=0.68, grad=0.5, line=True)
    for x in (-8, 0, 8):
        ic.add(capsule(cx + x * s, cy + 11 * s, cx + (x - 2) * s, cy + 16 * s, 1.0 * s), "water", base=0.7, bevel=0)


def map_sense():
    ic = Icon("MapSense")
    map_scroll(ic, 30, 36, 1.3)
    spark(ic, 20, 30, "ability", 2); spark(ic, 40, 42, "ability", 2)
    eye(ic, 48, 12, 0.8)
    return ic


def wanderer():
    ic = Icon("Wanderer")
    sack(ic, 26, 38, 1.2, pal="leather")
    coin(ic, 46, 46, 10)
    plus(ic, 52, 12, 1.0, "yield")
    return ic


def trail_mix():
    ic = Icon("TrailMix")
    ic.add(inter(ellipse(26, 40, 18, 14), rect(6, 40, 46, 56)), "wood", base=0.52, grad=0.6, line=True)
    ic.add(ellipse(26, 40, 18, 3.5), "wood", base=0.75, bevel=0, cast=False)
    for (x, y, p) in ((16, 37, "wood"), (24, 34, "honey"), (33, 36, "mahog"), (20, 40, "red"), (29, 40, "wheat"), (37, 40, "honey")):
        ic.add(circle(x, y, 3.6), p, mode="sphere", base=0.62, line=True)
    bolt(ic, 50, 20, 0.95)
    return ic


def scout_pulse():
    ic = Icon("ScoutPulse")
    tower(ic, 32, 58, 1.1)
    for R, b in ((26, 0.5), (19, 0.68)):
        arc(ic, 32, 30, R, 200, 340, 2.6, "ability", base=b)
        arc(ic, 32, 30, R, 20, 70, 2.6, "ability", base=b)
    return ic


def far_sight():
    ic = Icon("FarSight")
    spyglass(ic, 10, 54, 40, 24, 1.1)
    arrow(ic, 52, 12, 1.0, "ability", ang=-45)
    return ic


def quick_scout():
    ic = Icon("QuickScout")
    spyglass(ic, 8, 44, 36, 16, 1.0)
    clock(ic, 49, 49, 10, "ability")
    return ic


def cartographer():
    ic = Icon("Cartographer")
    map_scroll(ic, 26, 30, 1.1)
    coin(ic, 46, 46, 9)
    plus(ic, 14, 54, 0.85, "yield")
    return ic


def chest_finder():
    ic = Icon("ChestFinder")
    chest(ic, 28, 40, 1.25)
    spark(ic, 12, 14, "yield", 2); spark(ic, 44, 16, "yield", 1)
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def pet_scout():
    ic = Icon("PetScout")
    paw(ic, 24, 38, 1.4, acc("pet"))
    compass(ic, 48, 18, 10)
    plus(ic, 53, 52, 0.85, "pet")
    return ic


def worldwalker():
    ic = Icon("Worldwalker")
    globe(ic, 30, 30, 22)
    boot(ic, 46, 46, 0.75, line=True)
    spark(ic, 8, 8, "speed", 2); spark(ic, 56, 10, "yield", 1)
    return ic


def light_packer():
    ic = Icon("LightPacker")
    backpack(ic, 26, 36, 1.35)
    feather(ic, 48, 22, 0.8, -60)
    plus(ic, 53, 52, 0.9, "yield")
    return ic


def camp_craft():
    ic = Icon("CampCraft")
    campfire(ic, 28, 58, 1.4)
    ic.add(heart(50, 16, 0.7), acc("health"), base=0.62, grad=0.5, bevel=0.6, line=True)
    plus(ic, 52, 40, 0.8, "health")
    return ic


def waystone_recall():
    ic = Icon("WaystoneRecall")
    waystone(ic, 28, 58, 1.3)
    turn_arrow(ic, 28, 34, 24, -60, 200, "ability", 3.0)
    return ic


def faster_recall():
    ic = Icon("FasterRecall")
    waystone(ic, 24, 50, 1.1)
    clock(ic, 49, 49, 10, "ability")
    return ic


def safe_landing():
    ic = Icon("SafeLanding")
    glider(ic, 30, 24, 1.1)
    lines(ic, [(10, 42, 10, 54), (52, 42, 52, 54)], "health", 1.6)
    return ic


def accessory_compass():
    ic = Icon("AccessoryCompass")
    compass(ic, 26, 34, 15)
    ring_item(ic, 48, 18, 0.9)
    lines(ic, [(44, 40, 58, 40), (46, 48, 60, 48), (44, 56, 58, 56)], "speed", 1.5)
    return ic


def weatherproof():
    ic = Icon("Weatherproof")
    rain_cloud(ic, 24, 20, 1.3)
    shield(ic, 44, 44, 1.05, pal=acc("health"))
    return ic


def wind_at_your_back():
    ic = Icon("WindAtYourBack")
    cape(ic, 38, 34, 1.3, pal="red")
    lines(ic, [(2, 18, 18, 18), (4, 30, 20, 30), (2, 42, 18, 42)], "speed", 1.6)
    spark(ic, 56, 8, "speed", 2)
    return ic


ROWS = [
 ("Exploration.b1.r1.free", "B1R1Free", "ability", map_sense, "a map with blue glints on its points of interest, a small eye"),
 ("Exploration.b1.r1a", "B1R1a", "yield", wanderer, "a loot bag and a gold coin + a green plus (more coins)"),
 ("Exploration.b1.r1b", "B1R1b", "speed", trail_mix, "a bowl of trail mix + a Stamina lightning bolt"),
 ("Exploration.b1.r2.free", "B1R2Free", "ability", scout_pulse, "a stone watchtower sending out blue scout rings"),
 ("Exploration.b1.r2a", "B1R2a", "ability", far_sight, "a brass spyglass + a blue arrow (more range)"),
 ("Exploration.b1.r2b", "B1R2b", "ability", quick_scout, "a spyglass + a blue cooldown clock"),
 ("Exploration.b1.r3a", "B1R3a", "yield", cartographer, "a map and a gold coin + a green plus (second coin find)"),
 ("Exploration.b1.r3b", "B1R3b", "yield", chest_finder, "a gold-trimmed chest, green sparkles + plus (loot quality)"),
 ("Exploration.b1.r3c", "B1R3c", "pet", pet_scout, "a tan paw and a compass + a tan plus (discovery radius)"),
 ("Exploration.b1.r4", "B1R4", "speed", worldwalker, "a green and blue globe with a walking boot (capstone)"),
 ("Exploration.b2.r1a", "B2R1a", "yield", light_packer, "a leather backpack with a feather + a green plus (carry more)"),
 ("Exploration.b2.r1b", "B2R1b", "health", camp_craft, "a campfire and a red heart + plus (rest regen)"),
 ("Exploration.b2.r2.free", "B2R2Free", "ability", waystone_recall, "a glowing waystone inside a blue return arrow"),
 ("Exploration.b2.r2a", "B2R2a", "ability", faster_recall, "a waystone + a blue cooldown clock"),
 ("Exploration.b2.r2b", "B2R2b", "health", safe_landing, "a red glider, red fall lines (less fall damage)"),
 ("Exploration.b2.r3a", "B2R3a", "speed", accessory_compass, "a compass and a gold ring + teal speed lines (per accessory)"),
 ("Exploration.b2.r3b", "B2R3b", "health", weatherproof, "a rain cloud over a red shield (weather resistance)"),
 ("Exploration.b2.r4", "B2R4", "speed", wind_at_your_back, "a red cloak billowing in teal wind lines (capstone)"),
]
