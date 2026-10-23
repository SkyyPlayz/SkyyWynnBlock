"""Smithing tree node icons (19) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents

TREE = "Smithing"


def hot_blade(ic, x0, y0, x1, y1, s=1.0):
    sword(ic, x0, y0, x1, y1, s, pal="flame")


def kit(ic, cx, cy, s=1.0):
    ic.add(rrect(cx - 16 * s, cy - 8 * s, cx + 16 * s, cy + 12 * s, 2.5 * s), "red", base=0.55, grad=0.6, line=True)
    ic.add(ering(cx, cy - 9 * s, 7 * s, 5 * s, 4.5 * s, 3 * s), "steel", base=0.55, bevel=0, line=True)
    ic.add(rect(cx - 16 * s, cy - 1 * s, cx + 16 * s, cy + 2 * s), "steel", base=0.6, bevel=0)
    ic.add(rrect(cx - 3 * s, cy - 2 * s, cx + 3 * s, cy + 4 * s, 1 * s), "gold", base=0.7, bevel=0, line=True)


def broken_cog(ic, cx, cy, r):
    ic.add(diff(gear(cx, cy, r, r * 0.75, 9, hole=r * 0.3), poly([(cx, cy), (cx + r * 1.2, cy - r * 0.5), (cx + r * 1.2, cy + r * 0.3)])),
           "steel", base=0.55, grad=0.6, bevel=1.0, line=True)


def hammer_time():
    ic = Icon("HammerTime")
    hammer(ic, 40, 58, 28, 22, 1.4)
    lines(ic, [(44, 12, 56, 12), (46, 20, 58, 20), (48, 28, 60, 28)], "speed", 1.5)
    arc(ic, 40, 58, 40, 230, 270, 2.6, "speed")
    return ic


def steady_strikes():
    ic = Icon("SteadyStrikes")
    anvil(ic, 28, 44, 0.95)
    hammer(ic, 22, 28, 12, 10, 0.85)
    xp_orb(ic, 48, 16, 10)
    return ic


def thrift():
    ic = Icon("Thrift")
    ingot(ic, 30, 38, 1.35, "steel")
    turn_arrow(ic, 30, 34, 24, 200, 330, "yield")
    turn_arrow(ic, 30, 34, 24, 20, 150, "yield")
    return ic


def quench():
    ic = Icon("Quench")
    bucket(ic, 32, 46, 1.2, fill="water", pal="wood")
    hot_blade(ic, 44, 30, 20, 4, 0.9)
    for (x, y, r) in ((46, 22, 5), (52, 14, 4), (14, 26, 4)):
        ic.add(circle(x, y, r), "cloud", mode="sphere", base=0.7)
    spark(ic, 8, 10, "ability", 2)
    return ic


def quick_quench():
    ic = Icon("QuickQuench")
    bucket(ic, 24, 32, 1.2, fill="water", pal="wood")
    for (x, y, r) in ((20, 8, 4.5), (28, 10, 3.5)):
        ic.add(circle(x, y, r), "cloud", mode="sphere", base=0.7)
    clock(ic, 49, 49, 10, "ability")
    return ic


def perfect_quench():
    ic = Icon("PerfectQuench")
    hot_blade(ic, 46, 10, 18, 52, 1.05)
    burst(ic, 18, 16, 9, 3.6, 4, "gold", base=0.9, line=True)
    plus(ic, 52, 50, 0.95, "yield")
    return ic


def gear_resonance():
    ic = Icon("GearResonanceSmithing")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 38, R, 200, 340, 2.6, "yield", base=b)
    helmet(ic, 32, 38, 1.0, pal="steel")
    ic.add(rect(28, 22, 36, 44), "steel", base=0.75, bevel=0)
    return ic


def tool_lore():
    ic = Icon("ToolLore")
    pick(ic, 12, 56, 30, 26, arm=15)
    shield(ic, 48, 44, 1.0, pal=acc("tool"))
    return ic


def masterwork():
    ic = Icon("Masterwork")
    anvil(ic, 30, 44, 1.0)
    arrow(ic, 32, 14, 1.25, "yield")
    spark(ic, 52, 12, "yield", 2)
    return ic


def legendary_forge():
    ic = Icon("LegendaryForge")
    anvil(ic, 32, 46, 1.05)
    ingot(ic, 32, 30, 0.9, "gold")
    burst(ic, 32, 18, 10, 4, 8, "gold", base=0.85)
    spark(ic, 8, 10, "yield", 2); spark(ic, 56, 10, "yield", 1)
    return ic


def quick_repair():
    ic = Icon("QuickRepairSmithing")
    hammer(ic, 36, 52, 26, 24, 1.15)
    turn_arrow(ic, 30, 34, 24, 200, 330, "speed")
    lines(ic, [(46, 44, 58, 44), (48, 52, 60, 52)], "speed", 1.5)
    return ic


def salvager():
    ic = Icon("Salvager")
    broken_cog(ic, 26, 36, 18)
    for (x, y) in ((48, 30), (52, 40), (44, 44)):
        ic.add(rect(x - 2.5, y - 2, x + 2.5, y + 2), "steel", base=0.7, bevel=0, line=True)
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def field_repair():
    ic = Icon("FieldRepair")
    kit(ic, 28, 42, 1.2)
    hammer(ic, 54, 30, 42, 10, 0.75)
    burst(ic, 16, 14, 8, 3.4, 8, acc("ability"), base=0.85)
    return ic


def better_repair():
    ic = Icon("BetterRepair")
    kit(ic, 26, 34, 1.2)
    plus(ic, 50, 50, 1.1, "tool")
    return ic


def quick_kit():
    ic = Icon("QuickKit")
    kit(ic, 26, 30, 1.15)
    clock(ic, 49, 49, 10, "ability")
    return ic


def accessory_anvil():
    ic = Icon("AccessoryAnvil")
    anvil(ic, 26, 46, 0.85)
    ring_item(ic, 44, 18, 1.1)
    plus(ic, 14, 14, 0.9, "buff")
    return ic


def pet_hammer():
    ic = Icon("PetHammer")
    paw(ic, 24, 38, 1.45, acc("pet"))
    hammer(ic, 58, 58, 48, 34, 0.75)
    xp_orb(ic, 50, 12, 7)
    return ic


def reinforce():
    ic = Icon("Reinforce")
    shield(ic, 28, 32, 1.8)
    for (x, y) in ((18, 20), (38, 20), (28, 44)):
        ic.add(circle(x, y, 2.0), "gold", mode="sphere", base=0.75)
    plus(ic, 52, 50, 1.0, "tool")
    return ic


def eternal_edge():
    ic = Icon("EternalEdge")
    ic.add(ering(32, 32, 26, 26, 22, 22), "gold", mode="torus", torus=(32, 32, 26, 26, 22, 22), bevel=0, line=True)
    sword(ic, 48, 12, 16, 52, 1.1)
    spark(ic, 10, 10, "tool", 2); spark(ic, 54, 54, "tool", 1)
    return ic


ROWS = [
 ("Smithing.b1.r1.free", "B1R1Free", "speed", hammer_time, "a smith's hammer mid-swing with teal motion lines (faster crafts)"),
 ("Smithing.b1.r1a", "B1R1a", "xp", steady_strikes, "a hammer over an anvil + a gold XP orb"),
 ("Smithing.b1.r1b", "B1R1b", "yield", thrift, "an iron bar inside two green circling arrows (materials saved)"),
 ("Smithing.b1.r2.free", "B1R2Free", "ability", quench, "a glowing hot blade plunged into a water bucket, steam puffs"),
 ("Smithing.b1.r2a", "B1R2a", "ability", quick_quench, "a steaming quench bucket + a blue cooldown clock"),
 ("Smithing.b1.r2b", "B1R2b", "yield", perfect_quench, "a glowing hot blade with a gold star + a green plus (bonus stat)"),
 ("Smithing.b1.r3a", "B1R3a", "yield", gear_resonance, "a steel smith's helm with green resonance arcs (per armor piece)"),
 ("Smithing.b1.r3b", "B1R3b", "tool", tool_lore, "a pickaxe + a soft-white shield (more durable tools)"),
 ("Smithing.b1.r3c", "B1R3c", "yield", masterwork, "an anvil with a big green up arrow (+1 upgrade)"),
 ("Smithing.b1.r4", "B1R4", "yield", legendary_forge, "a gold bar glowing on an anvil, gold burst (capstone)"),
 ("Smithing.b2.r1a", "B2R1a", "speed", quick_repair, "a hammer with a teal turning arrow and speed lines (repair speed)"),
 ("Smithing.b2.r1b", "B2R1b", "yield", salvager, "a broken cog and scrap pieces + a green plus"),
 ("Smithing.b2.r2.free", "B2R2Free", "ability", field_repair, "a red repair kit with a hammer, blue burst"),
 ("Smithing.b2.r2a", "B2R2a", "tool", better_repair, "a repair kit + a soft-white plus"),
 ("Smithing.b2.r2b", "B2R2b", "ability", quick_kit, "a repair kit + a blue cooldown clock"),
 ("Smithing.b2.r3a", "B2R3a", "buff", accessory_anvil, "an anvil and a gold emerald ring + a purple plus (enchant strength)"),
 ("Smithing.b2.r3b", "B2R3b", "pet", pet_hammer, "a tan paw, a hammer and a gold XP orb (XP per pet tier)"),
 ("Smithing.b2.r3c", "B2R3c", "tool", reinforce, "a riveted steel shield + a soft-white plus"),
 ("Smithing.b2.r4", "B2R4", "tool", eternal_edge, "a sword inside an endless gold ring (unbreakable, capstone)"),
]
