"""Combat tree node icons (42) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents

TREE = "Combat"


def skull(ic, cx, cy, s=1.0, horns=True):
    if horns:
        ic.add(crescent(cx - 14 * s, cy - 2 * s, 10 * s, 180, 300, 4 * s), "bone", base=0.65, grad=0.5, line=True)
        ic.add(crescent(cx + 14 * s, cy - 2 * s, 10 * s, 240, 360, 4 * s), "bone", base=0.65, grad=0.5, line=True)
    ic.add(union(circle(cx, cy - 2 * s, 11 * s), rrect(cx - 7 * s, cy + 4 * s, cx + 7 * s, cy + 13 * s, 2 * s)), "bone", base=0.66, grad=0.6, bevel=1.0, line=True)
    for x in (-4.5, 4.5):
        ic.add(ellipse(cx + x * s, cy - 1 * s, 3 * s, 3.4 * s), "navy", base=0.12, bevel=0, cast=False)
    for x in (-3, 0, 3):
        ic.add(rect(cx + x * s - 0.7 * s, cy + 8 * s, cx + x * s + 0.7 * s, cy + 13 * s), "navy", base=0.15, bevel=0, cast=False)


def chestplate(ic, cx, cy, s=1.0, pal="steel"):
    ic.add(poly([(cx - 16 * s, cy - 12 * s), (cx - 6 * s, cy - 14 * s), (cx, cy - 10 * s), (cx + 6 * s, cy - 14 * s), (cx + 16 * s, cy - 12 * s),
                 (cx + 14 * s, cy + 2 * s), (cx + 10 * s, cy + 14 * s), (cx - 10 * s, cy + 14 * s), (cx - 14 * s, cy + 2 * s)]), pal, base=0.58,
           grad=0.6, bevel=1.0, line=True, pattern=lambda x, y: -0.1 if abs(x - cx) < 0.8 * s else 0)


def banner(ic, cx, cy, s=1.0, pal="red"):
    ic.add(capsule(cx - 10 * s, cy - 18 * s, cx - 10 * s, cy + 20 * s, 1.6 * s), "wood", base=0.55, bevel=0, line=True)
    ic.add(poly([(cx - 9 * s, cy - 16 * s), (cx + 12 * s, cy - 16 * s), (cx + 12 * s, cy + 6 * s), (cx + 1.5 * s, cy), (cx - 9 * s, cy + 6 * s)]), pal,
           base=0.58, grad=0.6, line=True)
    ic.add(circle(cx - 10 * s, cy - 19 * s, 2.4 * s), "gold", mode="sphere", base=0.7)


def purse(ic, cx, cy, s=1.0):
    sack(ic, cx, cy, s, pal="mahog")
    ic.add(poly(star_pts(cx, cy + 5 * s, 5 * s, 2 * s, 4)), "gold", base=0.85, bevel=0, cast=False)


def whetstone(ic, cx, cy, s=1.0):
    ic.add(rrect(cx - 16 * s, cy - 4 * s, cx + 16 * s, cy + 4 * s, 2 * s), "stone", base=0.5, grad=0.6, line=True)
    ic.add(rect(cx - 16 * s, cy - 4 * s, cx + 16 * s, cy - 2 * s), "stone", base=0.8, bevel=0)


def slashes(ic, cx, cy, cat="damage", n=3, s=1.0):
    for k in range(n):
        o = (k - (n - 1) / 2.0) * 7 * s
        lines(ic, [(cx - 10 * s + o, cy - 12 * s, cx + 6 * s + o, cy + 12 * s)], cat, 1.6 * s)


# ---------------------------------------------------------------- Duelist
def combat_focus():
    ic = Icon("CombatFocus")
    target(ic, 30, 34, 17, "damage")
    sword(ic, 56, 8, 22, 46, 1.0)
    return ic


def hone_edge():
    ic = Icon("HoneEdge")
    whetstone(ic, 30, 52, 1.2)
    sword(ic, 54, 10, 14, 44, 1.0)
    spark(ic, 50, 14, "damage", 2)
    plus(ic, 14, 12, 0.9, "damage")
    return ic


def weak_spot():
    ic = Icon("WeakSpot")
    target(ic, 30, 34, 19, "damage")
    burst(ic, 30, 34, 9, 3.5, 4, "gold", base=0.9, line=True)
    return ic


def flurry():
    ic = Icon("Flurry")
    sword(ic, 54, 10, 20, 50, 1.0)
    for k in range(4):
        arc(ic, 30, 30, 10 + k * 6, 300, 380, 2.4, "ability", base=0.85 - 0.08 * k)
    return ic


def extra_strike():
    ic = Icon("ExtraStrike")
    sword(ic, 46, 8, 14, 46, 1.0)
    slashes(ic, 34, 36, "ability", 2, 0.8)
    plus(ic, 52, 50, 1.0, "ability")
    return ic


def flurry_recovery():
    ic = Icon("FlurryRecovery")
    sword(ic, 40, 6, 10, 40, 0.9)
    clock(ic, 49, 49, 10, "ability")
    return ic


def rending():
    ic = Icon("Rending")
    sword(ic, 54, 8, 20, 46, 1.0)
    for (x, y) in ((22, 20), (14, 30), (46, 46)):
        drop(ic, x, y, 0.6, "red")
    return ic


def finisher():
    ic = Icon("Finisher")
    h = heart(24, 40, 1.15)
    ic.add(inter(h, rect(0, 0, 24, 64)), "ruby", base=0.6, grad=0.6, bevel=0.8, line=True)
    ic.add(inter(h, rect(24, 0, 64, 64)), "stone", base=0.35, bevel=0, line=True)
    sword(ic, 58, 6, 34, 34, 0.9)
    plus(ic, 12, 10, 0.85, "damage")
    return ic


def momentum():
    ic = Icon("Momentum")
    boot(ic, 32, 36, 1.35, line=True)
    lines(ic, [(2, 24, 14, 24), (4, 32, 16, 32), (6, 40, 18, 40)], "speed", 1.5)
    sword(ic, 60, 6, 46, 22, 0.55)
    return ic


def parry_reflex():
    ic = Icon("ParryReflex")
    shield(ic, 26, 34, 1.5)
    burst(ic, 44, 18, 8, 3, 4, "gold", base=0.9, line=True)
    turn_arrow(ic, 32, 34, 27, 280, 400, "ability")
    return ic


def crit_mastery():
    ic = Icon("CritMastery")
    burst(ic, 28, 36, 22, 8, 4, acc("damage"), base=0.65, line=True)
    burst(ic, 28, 36, 10, 4, 4, "gold", base=0.95, rot=-45)
    arrow(ic, 52, 14, 1.0, "damage")
    return ic


def gear_resonance():
    ic = Icon("GearResonanceCombat")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 40, R, 200, 340, 2.6, "damage", base=b)
    helmet(ic, 32, 38, 1.0, pal="steel")
    ic.add(rect(20, 32, 44, 35), "navy", base=0.15, bevel=0, cast=False)
    ic.add(rect(30.5, 20, 33.5, 40), "steel", base=0.8, bevel=0)
    return ic


def trophy_hunter():
    ic = Icon("TrophyHunter")
    skull(ic, 28, 34, 1.2)
    target(ic, 50, 50, 9, "damage")
    return ic


def weapon_tempering():
    ic = Icon("WeaponTempering")
    podium(ic, 4, 60)
    sword(ic, 48, 8, 34, 32, 0.8, pal="gold")
    plus(ic, 12, 14, 0.9, "damage")
    return ic


def bloodlust():
    ic = Icon("Bloodlust")
    drop(ic, 24, 32, 2.0, "red")
    hourglass(ic, 50, 46, 1.0, "damage")
    return ic


def edge_of_the_legend():
    ic = Icon("EdgeOfTheLegend")
    burst(ic, 32, 32, 28, 12, 8, acc("damage"), rot=-67.5, base=0.5)
    sword(ic, 54, 8, 12, 52, 1.2, pal="gold")
    spark(ic, 10, 10, "damage", 2)
    return ic


# ---------------------------------------------------------------- Bulwark
def toughness():
    ic = Icon("Toughness")
    ic.add(heart(28, 32, 2.0), acc("health"), base=0.58, grad=0.6, bevel=1.1, line=True)
    ic.add(inter(heart(28, 32, 2.0), rect(0, 28, 64, 33)), "steel", base=0.65, bevel=0)
    plus(ic, 52, 50, 0.95, "health")
    return ic


def iron_will():
    ic = Icon("IronWill")
    ic.add(rect(4, 54, 60, 60), "stone", base=0.45, grad=0.4)
    boot(ic, 24, 42, 1.3, pal="steel", sole="steel", line=True)
    for k in range(2):
        arrow(ic, 52, 22 + k * 14, 0.8, "health", ang=180)
    return ic


def shield_wall():
    ic = Icon("ShieldWall")
    burst(ic, 32, 32, 29, 13, 8, acc("ability"), rot=-67.5, base=0.6)
    shield(ic, 32, 30, 1.9)
    ic.add(rect(30, 14, 34, 50), "gold", base=0.6, bevel=0)
    return ic


def longer_wall():
    ic = Icon("LongerWall")
    shield(ic, 26, 30, 1.5)
    hourglass(ic, 50, 46, 1.0, "ability")
    return ic


def quick_draw():
    ic = Icon("QuickDraw")
    shield(ic, 26, 28, 1.5)
    clock(ic, 49, 49, 10, "ability")
    return ic


def thick_skin():
    ic = Icon("ThickSkin")
    chestplate(ic, 28, 34, 1.4)
    plus(ic, 52, 14, 1.0, "health")
    return ic


def reprisal():
    ic = Icon("Reprisal")
    sh = shield(ic, 28, 32, 1.6)
    for (x, y, a) in ((28, 10, -90), (8, 20, 200), (48, 20, -20), (12, 40, 160), (44, 40, 20)):
        ic.add(poly([(x + 4 * math.cos(math.radians(a + 90)), y + 4 * math.sin(math.radians(a + 90))),
                     (x - 4 * math.cos(math.radians(a + 90)), y - 4 * math.sin(math.radians(a + 90))),
                     (x + 7 * math.cos(math.radians(a)), y + 7 * math.sin(math.radians(a)))]), "steel", base=0.8, bevel=0, line=True)
    for R, b in ((16, 0.75), (22, 0.6)):
        arc(ic, 40, 48, R, 0, 90, 2.4, "damage", base=b)
    return ic


def second_wind():
    ic = Icon("SecondWind")
    ic.add(heart(30, 32, 1.6), acc("health"), base=0.58, grad=0.6, bevel=1.0, line=True)
    turn_arrow(ic, 30, 32, 26, 120, 400, "health")
    return ic


def accessory_plates():
    ic = Icon("AccessoryPlates")
    chestplate(ic, 24, 38, 1.1)
    ring_item(ic, 48, 20, 0.95)
    plus(ic, 53, 52, 0.9, "health")
    return ic


def rally():
    ic = Icon("Rally")
    banner(ic, 26, 34, 1.3)
    ic.add(heart(50, 46, 0.65), acc("health"), base=0.62, grad=0.5, bevel=0.6, line=True)
    plus(ic, 52, 16, 0.85, "health")
    return ic


def bastion():
    ic = Icon("Bastion")
    ic.add(rect(10, 22, 40, 60), "stone", base=0.5, grad=0.6, line=True, pattern=hstripes(5, 0.07))
    ic.add(union(*[rect(x, 14, x + 6, 23) for x in (10, 22, 34)]), "stone", base=0.62, grad=0.5, line=True)
    shield(ic, 46, 42, 1.0, pal=acc("health"))
    return ic


def ward_pulse():
    ic = Icon("WardPulse")
    shield(ic, 20, 32, 1.3)
    for R, b in ((14, 0.85), (21, 0.68), (28, 0.52)):
        arc(ic, 26, 32, R, -45, 45, 2.6, "ability", base=b)
    arrow(ic, 56, 52, 0.75, "ability", ang=0)
    return ic


def unbreakable():
    ic = Icon("Unbreakable")
    ic.add(circle(32, 32, 26), "gold", mode="sphere", base=0.38, rim=False, bevel=0)
    shield(ic, 32, 30, 1.8)
    ic.add(poly([(30, 12), (35, 22), (29, 28), (35, 36), (30, 48), (33, 36), (27, 28), (32, 22)]), "gold", base=0.85, bevel=0, cast=False, rim=False)
    return ic


# ---------------------------------------------------------------- Spoils
def scavenger():
    ic = Icon("Scavenger")
    sack(ic, 26, 40, 1.2, pal="leather")
    bone(ic, 38, 14, 54, 24, 0.9)
    plus(ic, 53, 50, 0.95, "yield")
    return ic


def coin_purse():
    ic = Icon("CoinPurse")
    purse(ic, 26, 38, 1.3)
    coin(ic, 48, 48, 9)
    sword(ic, 58, 4, 44, 20, 0.55)
    return ic


def mark_the_prey():
    ic = Icon("MarkThePrey")
    skull(ic, 32, 32, 0.95, horns=False)
    target(ic, 32, 32, 22, "ability")
    return ic


def wide_mark():
    ic = Icon("WideMark")
    target(ic, 22, 26, 13, "ability")
    target(ic, 42, 42, 10, "ability")
    plus(ic, 52, 12, 0.9, "ability")
    return ic


def lingering_mark():
    ic = Icon("LingeringMark")
    target(ic, 26, 28, 17, "ability")
    hourglass(ic, 51, 46, 0.95, "ability")
    return ic


def pet_fang():
    ic = Icon("PetFang")
    paw(ic, 24, 40, 1.35, acc("pet"))
    fang(ic, 48, 20, 1.0, ang=20)
    plus(ic, 52, 52, 0.85, "pet")
    return ic


def rare_drop():
    ic = Icon("RareDrop")
    gem(ic, 28, 34, 1.5, "amethyst", line=True)
    spark(ic, 10, 14, "yield", 2)
    plus(ic, 52, 14, 1.0, "yield")
    return ic


def salvage():
    ic = Icon("Salvage")
    sword(ic, 40, 14, 12, 50, 0.9)
    ic.add(poly([(40, 14), (46, 8), (50, 12), (44, 18)]), "steel", base=0.7, bevel=0, line=True)
    for (x, y) in ((50, 30), (54, 40)):
        ic.add(rect(x - 3, y - 2, x + 3, y + 2), "steel", base=0.7, bevel=0, line=True)
    plus(ic, 52, 52, 0.9, "yield")
    return ic


def boss_hunter():
    ic = Icon("BossHunter")
    skull(ic, 24, 26, 0.95)
    chest(ic, 38, 48, 0.75)
    plus(ic, 54, 12, 0.95, "yield")
    return ic


def treasure_sense():
    ic = Icon("TreasureSense")
    ic.add(rect(24, 2, 36, 44), acc("ability"), base=0.62, grad=0.3, bevel=0, cast=False, line=True,
           pattern=lambda x, y: 0.2 if abs(x - 30) < 2 else 0)
    chest(ic, 30, 48, 1.05)
    return ic


def lucky_kill():
    ic = Icon("LuckyKill")
    clover(ic, 20, 26, 1.2)
    coin(ic, 40, 44, 9); coin(ic, 50, 34, 8)
    plus(ic, 52, 10, 0.85, "yield")
    return ic


def combat_insight():
    ic = Icon("CombatInsight")
    sword(ic, 44, 8, 12, 48, 1.0)
    xp_orb(ic, 46, 44, 11)
    return ic


def master_looter():
    ic = Icon("MasterLooter")
    chest(ic, 30, 46, 1.25)
    gem(ic, 22, 26, 0.5, "ruby", line=True); gem(ic, 38, 24, 0.55, "emerald", line=True); coin(ic, 30, 30, 4.5)
    spark(ic, 8, 10, "yield", 2); spark(ic, 56, 12, "yield", 2)
    return ic


ROWS = [
 ("Combat.b1.r1.free", "B1R1Free", "damage", combat_focus, "a sword before an orange target (+ damage)"),
 ("Combat.b1.r1a", "B1R1a", "damage", hone_edge, "a sword over a whetstone, orange glint + plus"),
 ("Combat.b1.r1b", "B1R1b", "damage", weak_spot, "an orange target with a gold crit star in the bullseye"),
 ("Combat.b1.r2.free", "B1R2Free", "ability", flurry, "a sword with four blue strike arcs (rapid strikes)"),
 ("Combat.b1.r2a", "B1R2a", "ability", extra_strike, "a sword, two blue slashes + a blue plus (one more strike)"),
 ("Combat.b1.r2b", "B1R2b", "ability", flurry_recovery, "a sword + a blue cooldown clock"),
 ("Combat.b1.r2c", "B1R2c", "damage", rending, "a sword shedding red bleed drops"),
 ("Combat.b1.r3a", "B1R3a", "damage", finisher, "a sword striking a half-empty heart + an orange plus (low-Health foes)"),
 ("Combat.b1.r3b", "B1R3b", "speed", momentum, "a running boot with teal speed lines and a small sword"),
 ("Combat.b1.r3c", "B1R3c", "ability", parry_reflex, "a shield with a gold parry spark and a blue turn arrow (free Flurry)"),
 ("Combat.b1.r4a", "B1R4a", "damage", crit_mastery, "a big orange crit star with a gold core + an orange up arrow"),
 ("Combat.b1.r4b", "B1R4b", "damage", gear_resonance, "a steel knight's helm with orange resonance arcs (per armor piece)"),
 ("Combat.b1.r5a", "B1R5a", "damage", trophy_hunter, "a horned boss skull + an orange target"),
 ("Combat.b1.r5b", "B1R5b", "damage", weapon_tempering, "a gold sword on a copper / iron / gold podium + an orange plus"),
 ("Combat.b1.r5c", "B1R5c", "damage", bloodlust, "a red blood drop + an orange-sand hourglass (focus lasts longer)"),
 ("Combat.b1.r6", "B1R6", "damage", edge_of_the_legend, "a golden sword on an orange burst (capstone)"),
 ("Combat.b2.r1a", "B2R1a", "health", toughness, "a red heart banded with steel + a red plus"),
 ("Combat.b2.r1b", "B2R1b", "health", iron_will, "an iron boot planted on stone, red push arrows bouncing off"),
 ("Combat.b2.r2.free", "B2R2Free", "ability", shield_wall, "a big steel shield on a blue burst"),
 ("Combat.b2.r2a", "B2R2a", "ability", longer_wall, "a shield + an hourglass (longer)"),
 ("Combat.b2.r2b", "B2R2b", "ability", quick_draw, "a shield + a blue cooldown clock"),
 ("Combat.b2.r3a", "B2R3a", "health", thick_skin, "a steel breastplate + a red plus (damage reduction)"),
 ("Combat.b2.r3b", "B2R3b", "damage", reprisal, "a spiked shield with orange strike arcs (thorns)"),
 ("Combat.b2.r3c", "B2R3c", "health", second_wind, "a red heart inside a red circling arrow (heal at low Health)"),
 ("Combat.b2.r4a", "B2R4a", "health", accessory_plates, "a breastplate and a gold ring + a red plus (per accessory)"),
 ("Combat.b2.r4b", "B2R4b", "health", rally, "a red war banner and a red heart + plus (regen out of combat)"),
 ("Combat.b2.r5a", "B2R5a", "health", bastion, "a stone tower beside a red shield"),
 ("Combat.b2.r5b", "B2R5b", "ability", ward_pulse, "a shield sending out blue push arcs"),
 ("Combat.b2.r6", "B2R6", "health", unbreakable, "a cracked shield held together by glowing gold (capstone)"),
 ("Combat.b3.r1a", "B3R1a", "yield", scavenger, "a loot sack and a bone + a green plus (one more drop)"),
 ("Combat.b3.r1b", "B3R1b", "yield", coin_purse, "a coin purse, a coin and a small sword (kills pay coins)"),
 ("Combat.b3.r2.free", "B3R2Free", "ability", mark_the_prey, "a skull inside a blue crosshair mark"),
 ("Combat.b3.r2a", "B3R2a", "ability", wide_mark, "two blue crosshair marks + a blue plus (more targets)"),
 ("Combat.b3.r2b", "B3R2b", "ability", lingering_mark, "a blue crosshair mark + an hourglass (longer)"),
 ("Combat.b3.r3a", "B3R3a", "pet", pet_fang, "a tan paw and a fang + a tan plus"),
 ("Combat.b3.r3b", "B3R3b", "yield", rare_drop, "a cut amethyst, green sparkle + plus (rarest loot once more)"),
 ("Combat.b3.r3c", "B3R3c", "yield", salvage, "a broken sword and scrap + a green plus"),
 ("Combat.b3.r4a", "B3R4a", "yield", boss_hunter, "a horned boss skull over a chest + a green plus"),
 ("Combat.b3.r4b", "B3R4b", "ability", treasure_sense, "a chest under a blue loot beam"),
 ("Combat.b3.r5a", "B3R5a", "yield", lucky_kill, "a four-leaf clover and two coins + a green plus (loot twice)"),
 ("Combat.b3.r5b", "B3R5b", "xp", combat_insight, "a sword + a gold XP orb"),
 ("Combat.b3.r6", "B3R6", "yield", master_looter, "a chest heaped with gems and coins (capstone)"),
]
