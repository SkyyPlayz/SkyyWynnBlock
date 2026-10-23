"""Fishing tree node icons (17) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents

TREE = "Fishing"


def tentacle(ic, pts, s=1.0, pal="amethyst"):
    n = len(pts)
    for k in range(n - 1):
        r = (3.6 - 2.6 * k / (n - 1)) * s
        ic.add(capsule(pts[k][0], pts[k][1], pts[k + 1][0], pts[k + 1][1], r), pal, base=0.55, grad=0.5, bevel=0.6, line=True)


def tug_sense():
    ic = Icon("TugSense")
    water(ic, 4, 40, 60, 58)
    bobber(ic, 30, 36, 1.6)
    for (x0, y0, x1, y1) in ((12, 12, 17, 18), (50, 12, 45, 18), (31, 3, 31, 10)):
        lines(ic, [(x0, y0, x1, y1)], "ability", 1.7)
    return ic


def sharp_hook():
    ic = Icon("SharpHook")
    hook(ic, 34, 32, 1.9)
    lines(ic, [(4, 26, 16, 26), (6, 36, 18, 36), (8, 46, 20, 46)], "speed", 1.5)
    spark(ic, 22, 50, "speed", 1)
    return ic


def fish_fortune():
    ic = Icon("FishFortune")
    fish(ic, 26, 22, 1.0)
    fish(ic, 26, 44, 1.0, pal="teal")
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def chum_cast():
    ic = Icon("ChumCast")
    bucket(ic, 22, 40, 1.2, fill="ruby", pal="wood")
    fish(ic, 50, 18, 0.5, flip=True); fish(ic, 52, 40, 0.5, flip=True)
    for R, b in ((10, 0.85), (16, 0.65)):
        arc(ic, 38, 30, R, -50, 50, 2.4, "ability", base=b)
    return ic


def rich_chum():
    ic = Icon("RichChum")
    fish(ic, 28, 34, 1.4, pal="gold")
    spark(ic, 12, 14, "yield", 2)
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def long_chum():
    ic = Icon("LongChum")
    bucket(ic, 24, 34, 1.25, fill="ruby", pal="wood")
    hourglass(ic, 50, 46, 1.0, "ability")
    return ic


def rod_tempering():
    ic = Icon("RodTempering")
    rod(ic, 10, 58, 48, 10, 1.2)
    ic.add(circle(48, 10, 4), "flame", mode="sphere", base=0.8, line=True)
    lines(ic, [(30, 50, 44, 50), (36, 58, 52, 58), (40, 42, 54, 42)], "speed", 1.5)
    return ic


def pet_angler():
    ic = Icon("PetAngler")
    paw(ic, 24, 38, 1.4, acc("pet"))
    fish(ic, 46, 16, 0.6, flip=True)
    xp_orb(ic, 51, 49, 8)
    return ic


def legend_of_the_deep():
    ic = Icon("LegendOfTheDeep")
    water(ic, 2, 46, 62, 60)
    fish(ic, 30, 32, 1.6, pal="abyss")
    ic.add(poly([(16, 18), (18, 10), (22, 15), (26, 8), (30, 15), (34, 10), (36, 18)]), "gold", base=0.65, grad=0.5, line=True)
    spark(ic, 54, 10, "yield", 2); spark(ic, 8, 40, "yield", 1)
    return ic


def sea_legs():
    ic = Icon("SeaLegs")
    boot(ic, 34, 30, 1.3, line=True)
    waves(ic, 32, 54, 52, "speed", 1.6, 3.0, 3)
    lines(ic, [(2, 20, 12, 20), (4, 28, 14, 28)], "speed", 1.5)
    return ic


def waterproof():
    ic = Icon("Waterproof")
    bubbles(ic, 26, 34, 2.3)
    plus(ic, 52, 50, 1.0, "health")
    return ic


def tide_call():
    ic = Icon("TideCall")
    water(ic, 2, 44, 62, 58)
    boat(ic, 32, 40, 0.9)
    for R, b in ((20, 0.65), (27, 0.5)):
        arc(ic, 32, 42, R, 200, 340, 2.6, "ability", base=b)
    return ic


def calm_waters():
    ic = Icon("CalmWaters")
    boat(ic, 34, 38, 1.0)
    waves(ic, 34, 52, 48, "ability", 1.4, 2.0, 3)
    lines(ic, [(2, 26, 12, 26), (4, 34, 12, 34)], "speed", 1.5)
    return ic


def hook_line():
    ic = Icon("HookLine")
    coil(ic, 26, 34, 1.4, pal="cream")
    hook(ic, 24, 32, 0.6)
    shield(ic, 48, 44, 1.0, pal=acc("tool"))
    return ic


def salvage_hook():
    ic = Icon("SalvageHook")
    ic.add(capsule(30, 2, 30, 22, 0.8), "cream", base=0.7, bevel=0)
    hook(ic, 25, 26, 1.25)
    chest(ic, 28, 46, 0.9)
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def gear_resonance():
    ic = Icon("GearResonanceFishing")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 38, R, 200, 340, 2.6, "yield", base=b)
    ic.add(circle(32, 36, 17), "copper", mode="sphere", base=0.58, line=True)
    ic.add(circle(32, 34, 8.5), "glass", base=0.6, grad=0.5, line=True)
    for a in (0, 90, 180, 270):
        ic.add(circle(32 + 12.5 * math.cos(math.radians(a)), 34 + 12.5 * math.sin(math.radians(a)), 1.4), "gold", base=0.8, bevel=0)
    return ic


def krakens_favor():
    ic = Icon("KrakensFavor")
    tentacle(ic, [(6, 60), (8, 44), (14, 30), (22, 22), (28, 24)], 1.2)
    tentacle(ic, [(58, 60), (56, 46), (52, 36), (46, 30)], 1.0)
    chest(ic, 34, 46, 1.0)
    spark(ic, 50, 12, "yield", 2); spark(ic, 34, 14, "yield", 1)
    return ic


ROWS = [
 ("Fishing.b1.r1.free", "B1R1Free", "ability", tug_sense, "a red bobber in the water with blue alert marks (bite indicator)"),
 ("Fishing.b1.r1a", "B1R1a", "speed", sharp_hook, "a steel fish hook with teal speed lines (faster bites)"),
 ("Fishing.b1.r1b", "B1R1b", "yield", fish_fortune, "two fish + a green plus (double catch)"),
 ("Fishing.b1.r2.free", "B1R2Free", "ability", chum_cast, "a bucket of red chum with fish swimming in, blue lure arcs"),
 ("Fishing.b1.r2a", "B1R2a", "yield", rich_chum, "a golden fish, green sparkle + plus (rare fish)"),
 ("Fishing.b1.r2b", "B1R2b", "ability", long_chum, "a bucket of chum + an hourglass (longer)"),
 ("Fishing.b1.r3a", "B1R3a", "speed", rod_tempering, "a fishing rod with a glowing hot tip and teal speed lines"),
 ("Fishing.b1.r3b", "B1R3b", "pet", pet_angler, "a tan paw, a fish and a gold XP orb (XP per pet tier)"),
 ("Fishing.b1.r4", "B1R4", "yield", legend_of_the_deep, "a huge dark deep-sea fish wearing a gold crown (capstone)"),
 ("Fishing.b2.r1a", "B2R1a", "speed", sea_legs, "a boot over teal waves with speed lines (swim speed)"),
 ("Fishing.b2.r1b", "B2R1b", "health", waterproof, "air bubbles + a red plus (more breath)"),
 ("Fishing.b2.r2.free", "B2R2Free", "ability", tide_call, "a boat on calm water inside blue calming arcs"),
 ("Fishing.b2.r2a", "B2R2a", "speed", calm_waters, "a boat on blue ripples with teal speed lines (boat speed)"),
 ("Fishing.b2.r2b", "B2R2b", "tool", hook_line, "a coil of fishing line with a hook + a soft-white shield (line strength)"),
 ("Fishing.b2.r3a", "B2R3a", "yield", salvage_hook, "a hook lifting a sunken chest + a green plus"),
 ("Fishing.b2.r3b", "B2R3b", "yield", gear_resonance, "a copper diving helmet with a porthole, green resonance arcs (per armor piece)"),
 ("Fishing.b2.r4", "B2R4", "yield", krakens_favor, "kraken tentacles curling round a sunken chest (capstone)"),
]
