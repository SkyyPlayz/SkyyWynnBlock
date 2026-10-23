"""Mining tree node icons (44) - APPROVED by Skyy 2026-10-23 ("i love it!"). Loaded by tools/art/make_tree_node_icons.py.
Drawn with the painter in make_tree_node_icons.py (imported read-only). Do not change a picture without Skyy's OK."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents

TREE = "Mining"


def m_prospectors_eye():
    ic = Icon("ProspectorsEye")
    stone_wall(ic, 6, 30, 58, 58)
    for (x, y, r) in ((17, 44, 3.6), (40, 50, 3.0), (49, 38, 2.4)):
        ic.add(circle(x, y, r), "ore", mode="sphere", base=0.72, line=True)
    eye(ic, 32, 20, 2.2)
    lines(ic, [(10, 8, 15, 12), (54, 8, 49, 12), (32, 1.5, 32, 5)], "ability", 1.4)
    spark(ic, 17, 44, "ability", 2); spark(ic, 49, 37, "ability", 1)
    return ic


def m_quick_swing():
    ic = Icon("QuickSwing")
    arc(ic, 42, 46, 34, 205, 262, 3.0, "speed")
    arc(ic, 42, 46, 26, 210, 258, 2.6, "speed", base=0.55)
    lines(ic, [(4, 34, 12, 34), (6, 42, 13, 41)], "speed", 1.4)
    pick(ic, 52, 56, 34, 22, arm=17)
    return ic


def m_rich_seams():
    ic = Icon("RichSeams")
    ore_chunk(ic, 28, 38, 1.55, line=True)
    plus(ic, 50, 14, 1.25, "yield")
    spark(ic, 14, 16, "yield", 2); spark(ic, 52, 34, "yield", 1)
    return ic


def m_vein_burst():
    ic = Icon("VeinBurst")
    burst(ic, 32, 33, 29, 10, 8, acc("ability"), rot=-67.5, base=0.62)
    burst(ic, 32, 33, 17, 7, 8, acc("ability"), base=0.9)
    ore_cube(ic, 8, 8, 13); ore_cube(ic, 42, 6, 12); ore_cube(ic, 9, 42, 11); ore_cube(ic, 41, 41, 13)
    return ic


def m_wide_burst():
    ic = Icon("WideBurst")
    ic.add(ering(32, 32, 24, 24, 20.5, 20.5), acc("ability"), base=0.6, bevel=0, line=True)
    ore_cube(ic, 22, 23, 15)
    for a in (-45, 45, 135, 225):
        r = 22.5
        arrow(ic, 32 + r * math.cos(math.radians(a)), 32 + r * math.sin(math.radians(a)), 0.9, "ability", ang=a)
    return ic


def m_burst_recovery():
    ic = Icon("BurstReach")
    burst(ic, 24, 38, 22, 8, 8, acc("ability"), rot=-67.5, base=0.62)
    burst(ic, 24, 38, 12, 5, 8, acc("ability"), base=0.92)
    ore_cube(ic, 36, 10, 17)
    plus(ic, 52, 47, 1.05, "ability")
    return ic


def m_chain_fortune():
    ic = Icon("ChainFortune")
    for (x, y, rot) in ((14, 46, -40), (25, 36, 50), (36, 26, -40)):
        ic.add(diff(rot_ellipse(x, y, 9.5, 5.6, rot), rot_ellipse(x, y, 6.2, 2.5, rot)), "steel", base=0.6, grad=0.5, bevel=0.9, line=True)
    ic.add(circle(46, 20, 12), acc("xp"), mode="sphere", base=0.62, line=True)
    ic.add(poly(star_pts(46, 20.5, 7, 3, 4)), acc("xp"), base=0.95, bevel=0, cast=False)
    arrow(ic, 50, 47, 1.05, "xp")
    return ic


def m_gem_eye():
    ic = Icon("GemEye")
    gem(ic, 36, 30, 1.8, "ruby", line=True)
    eye(ic, 17, 50, 1.1, iris="emerald")
    spark(ic, 55, 10, "yield", 2); spark(ic, 12, 22, "yield", 1)
    plus(ic, 54, 49, 0.9, "yield")
    return ic


def m_smelters_touch():
    ic = Icon("SmeltersTouch")
    flame(ic, 32, 42, 1.65)
    ingot(ic, 32, 25, 1.45, "steel")
    spark(ic, 53, 10, "yield", 2); spark(ic, 11, 13, "yield", 1)
    return ic


def m_steady_pick():
    ic = Icon("SteadyPick")
    pick(ic, 28, 48, 32, 15, arm=17)
    wave = [(4, 53), (16, 53), (20, 46), (25, 60), (30, 50), (34, 53), (60, 53)]
    for k in range(len(wave) - 1):
        lines(ic, [(wave[k][0], wave[k][1], wave[k + 1][0], wave[k + 1][1])], "speed", 1.6)
    return ic


def m_motherlode():
    ic = Icon("Motherlode")
    burst(ic, 32, 38, 30, 12, 12, "gold", rot=-90, base=0.62)
    gem(ic, 16, 36, 1.05, "emerald", line=True)
    gem(ic, 48, 36, 1.05, "ruby", line=True)
    gem(ic, 32, 30, 1.35, "diamond", line=True)
    spark(ic, 8, 10, "yield", 2); spark(ic, 56, 12, "yield", 2); spark(ic, 32, 58, "yield", 1)
    return ic


def m_vein_sense():
    ic = Icon("VeinSense")
    for R, b in ((27, 0.55), (21, 0.72)):
        arc(ic, 32, 30, R, 150, 210, 2.8, "ability", base=b)
        arc(ic, 32, 30, R, -30, 30, 2.8, "ability", base=b)
    eye(ic, 32, 30, 1.4)
    ore_cube(ic, 25, 45, 12)
    return ic


def m_seismic_pulse():
    ic = Icon("SeismicPulse")
    ic.add(rect(3, 44, 61, 58), "stone", base=0.48, grad=0.5, pattern=hstripes(4, 0.06))
    ic.add(poly([(30, 44), (35, 44), (33, 49), (37, 53), (31, 58), (32, 52), (28, 49)]), "navy", base=0.15, bevel=0, cast=False, rim=False)
    for R, b in ((26, 0.5), (18, 0.65), (10, 0.85)):
        arc(ic, 32, 44, R, 195, 345, 2.8, "ability", base=b)
    burst(ic, 12, 14, 7, 3, 5, "gold", base=0.8, line=True)
    burst(ic, 52, 12, 6, 2.6, 5, "gold", base=0.8, line=True)
    return ic


def m_overclock():
    ic = Icon("Overclock")
    ic.add(gear(30, 34, 24, 18, 10, hole=0, tooth=0.5), "steel", base=0.55, grad=0.6, bevel=1.0, line=True)
    ic.add(circle(30, 34, 11.5), "steel", base=0.32, bevel=0, cast=False)
    arrow(ic, 30, 34, 1.35, "xp")
    spark(ic, 56, 8, "xp", 2); spark(ic, 57, 26, "xp", 1)
    return ic


def m_bottomless_pockets():
    ic = Icon("BottomlessPockets")
    sack(ic, 30, 38, 1.5)
    ore_chunk(ic, 22, 12, 0.6)
    ore_chunk(ic, 40, 9, 0.5)
    plus(ic, 53, 50, 1.0, "yield")
    return ic


def m_heart_of_the_mountain():
    ic = Icon("HeartOfTheMountain")
    ic.add(mountain_shape(32, 60, 1.05), "stone", base=0.5, grad=0.6, pattern=hstripes(5, 0.07, 2), line=True)
    ic.add(poly([(33, 28.5), (28, 34), (37.5, 34)]), "cream", base=0.85, bevel=0)                         # snow cap
    ic.add(circle(32, 46, 10.5), acc("ability"), mode="sphere", base=0.45, rim=False, bevel=0)               # glow
    ic.add(heart(32, 46, 0.72), "ore", base=0.7, grad=0.6, bevel=0.8, line=True)
    spark(ic, 10, 14, "ability", 2); spark(ic, 55, 18, "ability", 1)
    return ic


def m_tool_mastery():
    ic = Icon("ToolMastery")
    for k, (pal, x, h) in enumerate((("copper", 4, 10), ("steel", 22, 17), ("gold", 40, 24))):
        ic.add(rect(x, 60 - h, x + 18, 60), pal, base=0.5 + 0.05 * k, grad=0.5, line=True)
        ic.add(rect(x, 60 - h, x + 18, 60 - h + 2.5), pal, base=0.85, bevel=0)
    pick(ic, 36, 32, 46, 13, arm=11, hr=2.7, r=2.0, head="gold")
    lines(ic, [(4, 22, 18, 22), (8, 30, 22, 30), (6, 14, 16, 14)], "speed", 1.5)
    return ic


def m_durable_grip():
    ic = Icon("DurableGrip")
    ic.add(capsule(10, 56, 44, 14, 5.0), "wood", mode="cyl", axis=(0.63, -0.78), base=0.58)
    for t in (0.28, 0.42, 0.56, 0.7):
        x, y = 10 + (44 - 10) * t, 56 + (14 - 56) * t
        ic.add(rot_ellipse(x, y, 6.6, 2.4, 50), "leather", base=0.62, grad=0.4, bevel=0.6, line=True)
    shield(ic, 47, 42, 1.0, pal=acc("tool"))
    ic.add(capsule(43, 39, 46, 43, 1.1), "steel", base=0.3, bevel=0, cast=False)
    ic.add(capsule(46, 43, 52, 35, 1.1), "steel", base=0.3, bevel=0, cast=False)
    return ic


def m_stoneskin():
    ic = Icon("Stoneskin")
    ic.add(rect(6, 52, 58, 60), "stone", base=0.45, grad=0.4)
    boot(ic, 28, 41, 1.45, pal="stone", sole="stone", line=True)
    for (x, y) in ((22, 26), (30, 32), (23, 38)):
        ic.add(rect(x - 3, y - 2.5, x + 3, y + 2.5), "stone", base=0.75, bevel=0.6)
    lines(ic, [(48, 6, 48, 18), (55, 10, 55, 22), (41, 3, 41, 12)], "health", 1.6)
    lines(ic, [(6, 50, 12, 46), (58, 50, 52, 46)], "health", 1.3)
    return ic


def m_rockhide():
    ic = Icon("Rockhide")
    h = heart(32, 31, 2.25)
    ic.add(h, acc("health"), base=0.58, grad=0.6, bevel=1.1, line=True)
    ic.add(inter(h, Shape(lambda x, y: x + y * 0.4 > 44 and int((x * 0.7 + y) // 9) % 2 == 0, h.bb)), "stone", base=0.6, grad=0.5, bevel=0.7)
    ic.add(inter(h, Shape(lambda x, y: x + y * 0.4 > 44 and int((x * 0.7 + y) // 9) % 2 == 1, h.bb)), "stone", base=0.45, grad=0.5, bevel=0.7)
    spark(ic, 16, 18, "health", 1)
    return ic


def m_echo_step():
    ic = Icon("EchoStep")
    for k, dx in enumerate((-22, -11)):
        ic.add(boot_shape(40 + dx, 38, 1.3), acc("speed"), base=0.3 + 0.25 * k, bevel=0, cast=False, line=True)
    boot(ic, 40, 38, 1.3, line=True)
    lines(ic, [(2, 50, 10, 50)], "speed", 1.4)
    return ic


def m_gear_resonance():
    ic = Icon("GearResonance")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 38, R, 200, 340, 2.6, "speed", base=b)
    dome = union(inter(ellipse(32, 40, 19, 19), rect(0, 0, 64, 40)), rect(13, 38, 51, 43))
    ic.add(dome, "copper", base=0.58, grad=0.6, bevel=1.0, line=True)
    ic.add(rect(9, 42, 55, 47), "copper", base=0.42, grad=0.4, line=True)                                   # brim
    ic.add(rrect(26, 27, 38, 37, 2.5), "steel", base=0.5, line=True)
    ic.add(circle(32, 32, 4), "lamp", mode="sphere", base=0.85)
    lines(ic, [(32, 50, 32, 60), (22, 50, 18, 58), (42, 50, 46, 58)], "speed", 1.4)
    return ic


def m_quick_repair():
    ic = Icon("QuickRepair")
    pick(ic, 12, 56, 26, 38, arm=13, hr=3.0, r=2.2)
    hammer(ic, 54, 50, 40, 22, 1.0)
    burst(ic, 31, 30, 8, 3, 4, acc("tool"), base=0.85, line=True)
    arc(ic, 32, 32, 27, 200, 300, 2.6, "tool")
    arrow(ic, 50.5, 9.5, 0.65, "tool", ang=-15)
    return ic


def m_emergency_pick():
    ic = Icon("EmergencyPick")
    pick(ic, 40, 58, 30, 22, arm=17)
    ic.add(poly([(20, 18), (24, 22), (21, 24), (25, 28), (23, 29), (19, 25), (22, 23)]), "navy", base=0.2, bevel=0, cast=False, rim=False)
    lines(ic, [(4, 40, 16, 40), (6, 48, 18, 48), (8, 56, 20, 56)], "speed", 1.5)
    ic.add(circle(52, 14, 9), acc("health"), mode="sphere", base=0.6, line=True)
    ic.add(rrect(50.4, 7.5, 53.6, 16.5, 1.2), "cream", base=0.85, bevel=0, cast=False)
    ic.add(circle(52, 19.5, 1.7), "cream", base=0.85, bevel=0, cast=False)
    return ic


def m_trinket_seams():
    ic = Icon("TrinketSeams")
    ore_chunk(ic, 24, 42, 1.25, line=True)
    ring_item(ic, 44, 22, 1.25)
    plus(ic, 53, 50, 0.95, "yield")
    spark(ic, 9, 12, "yield", 1)
    return ic


def m_hardened_edge():
    ic = Icon("HardenedEdge")
    ic.add(capsule(6, 58, 26, 34, 2.6), "wood", mode="cyl", axis=(0.64, -0.77), base=0.58)
    blade = poly([(18, 30), (30, 26), (46, 18), (60, 6), (50, 24), (36, 36), (26, 42)])
    ic.add(blade, "steel", base=0.62, grad=0.6, bevel=1.1, line=True)
    ic.add(poly([(46, 18), (60, 6), (55, 15), (44, 22)]), "steel", base=0.98, bevel=0, cast=False)
    for R, b in ((22, 0.62), (16, 0.8)):
        arc(ic, 44, 38, R, 20, 110, 2.6, "damage", base=b)
    spark(ic, 58, 5, "damage", 2)
    return ic


def m_tool_tempering():
    ic = Icon("ToolTempering")
    for (x, y, r) in ((14, 14, 6), (22, 9, 5), (9, 7, 4)):
        ic.add(circle(x, y, r), "cloud", mode="sphere", base=0.7)
    pick(ic, 18, 56, 36, 30, arm=17, head="flame")
    arrow(ic, 50, 46, 1.0, "tool")
    return ic


def m_lucky_strike():
    ic = Icon("LuckyStrike")
    pick(ic, 52, 58, 40, 24, arm=14, hr=2.8, r=2.1)
    for (dx, dy) in ((-6, -6), (6, -6), (-6, 6), (6, 6)):
        ic.add(circle(22 + dx, 30 + dy, 7), "green", mode="sphere", base=0.6, line=True)
    ic.add(capsule(22, 32, 16, 52, 1.6), "green", base=0.45, bevel=0)
    ic.add(circle(22, 30, 2.6), "green", base=0.85, bevel=0, cast=False)
    spark(ic, 56, 8, "tool", 2)
    arc(ic, 40, 24, 19, -70, 20, 2.4, "tool")
    return ic


def m_blast_hammer():
    ic = Icon("BlastHammer")
    burst(ic, 40, 22, 22, 9, 8, acc("ability"), rot=-67.5, base=0.62)
    hammer(ic, 10, 58, 36, 26, 1.35)
    ore_cube(ic, 46, 44, 11); ore_cube(ic, 4, 4, 9)
    return ic


def m_masterwork_pick():
    ic = Icon("MasterworkPick")
    pick(ic, 12, 58, 36, 26, arm=20, bend=6, hr=3.8, r=2.8, head="gold")
    gem(ic, 36, 26, 0.5, "diamond", line=True)
    burst(ic, 52, 46, 9, 3.4, 4, "gold", base=0.9, line=True)
    spark(ic, 10, 10, "tool", 2); spark(ic, 56, 6, "tool", 1)
    return ic


def m_cave_sense():
    ic = Icon("CaveSense")
    bat(ic, 32, 18, 1.55)
    sack(ic, 32, 44, 0.95, pal="leather")
    coin(ic, 47, 52, 6)
    plus(ic, 13, 49, 0.95, "yield")
    return ic


def m_lantern_lore():
    ic = Icon("LanternLore")
    for a in range(0, 360, 45):
        x0, y0 = 32 + 17 * math.cos(math.radians(a)), 35 + 17 * math.sin(math.radians(a))
        x1, y1 = 32 + 27 * math.cos(math.radians(a)), 35 + 27 * math.sin(math.radians(a))
        lines(ic, [(x0, y0, x1, y1)], "ability", 1.7)
    ic.add(ering(32, 10, 5, 5, 2.8, 2.8), "steel", base=0.55, bevel=0, line=True)
    ic.add(rrect(22, 14, 42, 19, 1.5), "steel", base=0.6, grad=0.5, line=True)
    ic.add(rect(24, 19, 40, 46), "lamp", mode="cyl", axis=(0, 1), base=0.75)
    flame(ic, 32, 34, 0.7)
    for x in (24, 32, 40):
        ic.add(rect(x - 1.2, 19, x + 1.2, 46), "steel", base=0.45, bevel=0)
    ic.add(rrect(21, 45, 43, 50, 1.5), "steel", base=0.5, grad=0.5, line=True)
    return ic


def m_depth_charge():
    ic = Icon("DepthCharge")
    burst(ic, 46, 12, 11, 4.5, 8, "flame", base=0.75)
    charge_sticks(ic, 28, 38, 1.4)
    spark(ic, 47, 12, "ability", 2)
    return ic


def m_bigger_bang():
    ic = Icon("BiggerBang")
    burst(ic, 32, 32, 21, 10, 10, "flame", base=0.6, line=True)
    burst(ic, 32, 32, 12, 6, 10, "flame", base=0.92, rot=-72)
    for a in (-45, 45, 135, 225):
        r = 24
        arrow(ic, 32 + r * math.cos(math.radians(a)), 32 + r * math.sin(math.radians(a)), 0.82, "ability", ang=a)
    return ic


def m_safe_fuse():
    ic = Icon("SafeFuse")
    charge_sticks(ic, 22, 30, 1.05)
    burst(ic, 27, 12, 5, 2, 6, "flame", base=0.85)
    sh = shield(ic, 42, 40, 1.35)
    ic.add(heart(42, 37, 0.62), acc("health"), base=0.62, grad=0.5, bevel=0.6)
    return ic


def m_pet_digger():
    ic = Icon("PetDigger")
    pick(ic, 54, 58, 44, 22, arm=12, hr=2.8, r=2.0)
    paw(ic, 24, 36, 1.55, acc("pet"))
    ore_chunk(ic, 48, 52, 0.42)
    plus(ic, 12, 10, 0.85, "pet")
    return ic


def m_deep_bounty():
    ic = Icon("DeepBounty")
    ore_chunk(ic, 24, 26, 1.25, line=True)
    coin(ic, 43, 44, 13)
    spark(ic, 56, 16, "yield", 2); spark(ic, 10, 52, "yield", 1)
    return ic


def m_cave_stalker():
    ic = Icon("CaveStalker")
    stone_wall(ic, 6, 28, 58, 60)
    bat(ic, 32, 45, 1.45, pal=acc("ability"), base=0.6)
    eye(ic, 32, 15, 1.7)
    return ic


def m_miners_fortune():
    ic = Icon("MinersFortune")
    ore_chunk(ic, 26, 46, 1.1, line=True)
    gem(ic, 33, 21, 1.15, "emerald", line=True)
    plus(ic, 53, 13, 1.05, "yield")
    lines(ic, [(33, 39, 33, 44), (24, 36, 21, 40), (42, 36, 45, 40)], "yield", 1.2)
    return ic


def m_geode_cracker():
    ic = Icon("GeodeCracker")
    ic.add(circle(30, 36, 23), "stone", mode="sphere", base=0.55, line=True)
    inside = ellipse(30, 36, 16, 16)
    ic.add(inside, "amethyst", base=0.22, bevel=0, cast=False)
    for (x, y, a) in ((22, 30, -30), (30, 26, 0), (38, 31, 30), (25, 41, -60), (36, 42, 60), (30, 36, 0)):
        ic.add(inter(rot_ellipse(x, y, 3.0, 6.5, a), inside), "amethyst", base=0.75, grad=0.6, bevel=0.6)
    ic.add(poly([(30, 13), (34, 20), (29, 24), (33, 30), (27, 25), (31, 20)]), "navy", base=0.15, bevel=0, cast=False, rim=False)
    plus(ic, 54, 12, 1.0, "yield")
    return ic


def m_dust_sweep():
    ic = Icon("DustSweep")
    mag = diff(union(circle(20, 22, 15), rect(5, 22, 35, 42)), union(circle(20, 22, 6.5), rect(13.5, 22, 26.5, 43)))
    ic.add(mag, "red", base=0.58, grad=0.6, bevel=1.0, line=True)
    ic.add(rect(5, 34, 13.5, 43), "steel", base=0.7, grad=0.4, line=True)
    ic.add(rect(26.5, 34, 35, 43), "steel", base=0.7, grad=0.4, line=True)
    lines(ic, [(10, 47, 13, 54), (31, 47, 36, 53), (40, 36, 48, 38)], "yield", 1.4)
    ore_chunk(ic, 50, 52, 0.42); ore_chunk(ic, 22, 57, 0.32); ore_chunk(ic, 54, 28, 0.36)
    return ic


def m_pet_synergy():
    ic = Icon("PetSynergy")
    burst(ic, 32, 32, 30, 15, 8, "gold", rot=-67.5, base=0.62)
    paw(ic, 32, 35, 1.45, acc("pet"))
    spark(ic, 52, 10, "pet", 2); spark(ic, 10, 50, "pet", 1)
    arrow(ic, 52, 50, 0.9, "pet")
    return ic


def m_abyss_walker():
    ic = Icon("AbyssWalker")
    ic.add(ellipse(32, 54, 28, 8), "abyss", base=0.4, grad=0.6, bevel=0)
    ic.add(ellipse(32, 54, 18, 4.2), "abyss", base=0.12, bevel=0, cast=False)
    boot(ic, 34, 32, 1.45, line=True)
    lines(ic, [(2, 22, 14, 22), (4, 30, 16, 30), (6, 38, 18, 38)], "speed", 1.5)
    return ic


def m_core_tap():
    ic = Icon("CoreTap")
    ic.add(circle(32, 34, 21), "abyss", mode="sphere", base=0.45, line=True)
    ic.add(circle(32, 34, 13), acc("ability"), mode="sphere", base=0.75, line=True)
    ic.add(circle(28, 30, 4), acc("ability"), base=1.0, bevel=0, cast=False, rim=False)
    gem(ic, 9, 14, 0.5, "ruby", line=True); gem(ic, 55, 12, 0.5, "emerald", line=True); gem(ic, 55, 54, 0.45, "diamond", line=True)
    spark(ic, 9, 52, "ability", 2)
    return ic


# (node key "<Tree>.b<branch>.<id | r<row>.free>", file stem, category, draw fn, what the icon shows)
ROWS = [
 ("Mining.b1.r1.free", "B1R1Free", "ability", m_prospectors_eye, "a wide-open eye over a stone wall whose blue ore glints through"),
 ("Mining.b1.r1a", "B1R1a", "speed", m_quick_swing, "an iron pickaxe mid-swing with teal swoosh arcs + speed lines"),
 ("Mining.b1.r1b", "B1R1b", "yield", m_rich_seams, "a big ore chunk with blue ore spots + a green plus and sparkles (Mining Fortune)"),
 ("Mining.b1.r2.free", "B1R2Free", "ability", m_vein_burst, "four ore cubes flying apart from a blue 8-point burst"),
 ("Mining.b1.r2a", "B1R2a", "ability", m_wide_burst, "an ore cube in a blue ring with four arrows pushing outward (bigger vein)"),
 ("Mining.b1.r2b", "B1R2b", "ability", m_burst_recovery, "a blue burst + one more ore cube with a blue plus (Burst breaks 1 more ore)"),
 ("Mining.b1.r2c", "B1R2c", "xp", m_chain_fortune, "three steel chain links into a gold XP orb + a gold up arrow"),
 ("Mining.b1.r3a", "B1R3a", "yield", m_gem_eye, "a big cut ruby, a small green-eyed eye + a green plus (gem chance)"),
 ("Mining.b1.r3b", "B1R3b", "yield", m_smelters_touch, "an iron bar on a flame (auto-smelt), green sparkles"),
 ("Mining.b1.r3c", "B1R3c", "speed", m_steady_pick, "an upright pickaxe over a steady teal rhythm line"),
 ("Mining.b1.r4a", "B1R4a", "yield", m_motherlode, "three gems (emerald, diamond, ruby) bursting from a gold jackpot star (x3)"),
 ("Mining.b1.r4b", "B1R4b", "ability", m_vein_sense, "an eye with blue range arcs either side, an ore cube below (more range)"),
 ("Mining.b1.r5a", "B1R5a", "ability", m_seismic_pulse, "cracked ground sending blue shock arcs up, two gold stun stars"),
 ("Mining.b1.r5b", "B1R5b", "xp", m_overclock, "a steel cog with a gold up arrow in its hub, gold sparks (more XP)"),
 ("Mining.b1.r5c", "B1R5c", "yield", m_bottomless_pockets, "a gold-tied leather sack with ore chunks spilling on top + a green plus"),
 ("Mining.b1.r6", "B1R6", "ability", m_heart_of_the_mountain, "a snow-capped stone mountain with a glowing blue crystal heart (capstone)"),
 ("Mining.b2.r1a", "B2R1a", "speed", m_tool_mastery, "a gold pick on a copper / iron / gold podium (tool tiers) + speed lines"),
 ("Mining.b2.r1b", "B2R1b", "tool", m_durable_grip, "a leather-wrapped pick handle with a soft-white shield + tick (less wear)"),
 ("Mining.b2.r2.free", "B2R2Free", "health", m_stoneskin, "a stone-plated boot landing on stone, red fall lines (less fall damage)"),
 ("Mining.b2.r2a", "B2R2a", "health", m_rockhide, "a red heart half covered in stone plates (+ max Health)"),
 ("Mining.b2.r2b", "B2R2b", "speed", m_echo_step, "a leather boot with two teal after-images behind it (move speed)"),
 ("Mining.b2.r3a", "B2R3a", "speed", m_gear_resonance, "a copper miner's helmet with its lamp, teal resonance arcs (per armor piece)"),
 ("Mining.b2.r3b", "B2R3b", "tool", m_quick_repair, "a hammer striking a pickaxe head, white repair spark + a turn arrow"),
 ("Mining.b2.r3c", "B2R3c", "speed", m_emergency_pick, "a cracked pickaxe with a red warning badge (!) and teal speed lines"),
 ("Mining.b2.r4a", "B2R4a", "yield", m_trinket_seams, "a gold emerald ring over an ore chunk + a green plus (per accessory)"),
 ("Mining.b2.r4b", "B2R4b", "damage", m_hardened_edge, "a sharpened pick point with a white edge glint, orange slash arcs"),
 ("Mining.b2.r5a", "B2R5a", "tool", m_tool_tempering, "a glowing hot pickaxe head with steam puffs + a white up arrow (tool tier)"),
 ("Mining.b2.r5b", "B2R5b", "tool", m_lucky_strike, "a four-leaf clover beside a pickaxe, white refund arc + spark"),
 ("Mining.b2.r5c", "B2R5c", "ability", m_blast_hammer, "a heavy sledgehammer before a blue burst, ore cubes flying"),
 ("Mining.b2.r6", "B2R6", "tool", m_masterwork_pick, "an ornate gold pickaxe with a diamond set in its head (capstone)"),
 ("Mining.b3.r1a", "B3R1a", "yield", m_cave_sense, "a cave bat over a loot sack and a coin + a green plus (cave-mob loot)"),
 ("Mining.b3.r1b", "B3R1b", "ability", m_lantern_lore, "a miner's lantern with a flame inside and blue light rays all round"),
 ("Mining.b3.r2.free", "B3R2Free", "ability", m_depth_charge, "a bundle of three red charge sticks with a lit fuse spark"),
 ("Mining.b3.r2a", "B3R2a", "ability", m_bigger_bang, "a fiery explosion with four blue arrows pushing outward (bigger radius)"),
 ("Mining.b3.r2b", "B3R2b", "health", m_safe_fuse, "charge sticks behind a steel shield with a red heart (no self-damage)"),
 ("Mining.b3.r3a", "B3R3a", "pet", m_pet_digger, "a big tan paw print beside a pickaxe and an ore chunk + a tan plus"),
 ("Mining.b3.r3b", "B3R3b", "yield", m_deep_bounty, "an ore chunk with a big gold coin in front, green sparkles (ore pays coins)"),
 ("Mining.b3.r3c", "B3R3c", "ability", m_cave_stalker, "an eye above a stone wall with a glowing blue bat seen through it"),
 ("Mining.b3.r4a", "B3R4a", "yield", m_miners_fortune, "an emerald popping out of an ore chunk + a green plus (gem chance)"),
 ("Mining.b3.r4b", "B3R4b", "yield", m_geode_cracker, "a cracked stone geode full of purple crystals + a green plus"),
 ("Mining.b3.r4c", "B3R4c", "yield", m_dust_sweep, "a red magnet pulling ore bits in along green pull lines (pickup radius)"),
 ("Mining.b3.r5a", "B3R5a", "pet", m_pet_synergy, "a tan paw on a tan star burst + a tan up arrow (pet abilities stronger)"),
 ("Mining.b3.r5b", "B3R5b", "speed", m_abyss_walker, "a boot striding over a dark violet abyss, teal speed lines"),
 ("Mining.b3.r6", "B3R6", "ability", m_core_tap, "a glowing blue deep core in a dark shell, three gems flung out (capstone)"),
]
