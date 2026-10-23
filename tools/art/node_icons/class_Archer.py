"""Archer class tree node icons (41: 36 new + 5 reused ability icons) - DRAFT v1. Runner: tools/art/make_class_node_icons.py.
Class colour leaf green #8fd67a (fletching). Subjects echo the approved ability icons: Pinning Shot = an arrow pinned in the ground,
Rapid Fire = three arrows in a row, Explosive Arrow = an arrow with a bomb head, Arrow Rain = arrows falling at a slant, Hunter's Net =
the round rope net with weights; a recurve bow for plain bow hits."""
from node_icons.class_kit import *

CLS = "Archer"
G = C(CLS)


def pin(ic, cx=28, cy=34, s=1.0):
    ic.add(ering(cx + 2 * s, cy + 12 * s, 14 * s, 4 * s, 10 * s, 2.4 * s), G, base=0.5, bevel=0, line=True)
    arrow_shaft(ic, cx - 12 * s, cy - 20 * s, cx + 2 * s, cy + 12 * s, 1.1 * s)


def rapid(ic, cx=28, cy=30, s=1.0):
    for k in range(3):
        d = (k - 1) * 9 * s
        arrow_shaft(ic, cx - 18 * s + d * 0.4, cy + 12 * s + d, cx + 14 * s + d * 0.4, cy - 10 * s + d, 0.95 * s)


def boom(ic, cx=28, cy=30, s=1.0):
    arrow_shaft(ic, cx - 18 * s, cy + 16 * s, cx + 4 * s, cy - 4 * s, 1.0 * s)
    bomb(ic, cx + 6 * s, cy - 6 * s, 7 * s)
    burst(ic, cx + 10 * s, cy - 18 * s, 5 * s, 2 * s, 6, "flame", base=0.85)


def rain(ic, cx=28, cy=30, s=1.0):
    for (dx, dy, k) in ((-12, -4, 0.85), (0, 2, 1.0), (12, -6, 0.85)):
        arrow_shaft(ic, cx + (dx - 6) * s, cy + (dy - 16) * s, cx + (dx + 4) * s, cy + (dy + 12) * s, k * s)


def hnet(ic, cx=28, cy=30, R=18):
    net(ic, cx, cy, R)


def bowshot(ic, cx=14, cy=32, s=1.2):
    bow(ic, cx, cy, s)
    arrow_shaft(ic, cx - 2 * s, cy, cx + 30 * s, cy, s)


ROWS = [
 # ---------------------------------------------------------------- Huntmaster
 R("Archer.b1.r1.free", "ability", Reuse(CLS, "PinningShot"), "REUSED ability icon Archer/PinningShot.png"),
 R("Archer.b1.r1a", "control", D("PinDuration", lambda ic: (pin(ic, 26, 30), g_hourglass(ic, 50, 48, 1.15, "control"))),
   "the pinning arrow in a root ring + a yellow hourglass (the root lasts longer)"),
 R("Archer.b1.r1b", "damage", D("HuntersMark", lambda ic: (pin(ic, 24, 32, 0.9), g_target(ic, 46, 22, 1.05), g_party(ic, 48, 50, 0.6))),
   "the pinning arrow, an orange target mark + the party (pinned targets take more from all allies)"),
 R("Archer.b1.r2.free", "ability", Reuse(CLS, "RapidFire"), "REUSED ability icon Archer/RapidFire.png"),
 R("Archer.b1.r2a", "ability", D("RapidPierce", lambda ic: (rapid(ic, 24, 24, 0.85), g_pierce(ic, 46, 50, 1.0))),
   "three Rapid Fire arrows + a blue arrow piercing two rings (pierces one more enemy)"),
 R("Archer.b1.r2b", "damage", D("SteadyDraw", lambda ic: (bowshot(ic, 10, 28, 1.15), g_up(ic, 50, 50, 1.0, "damage"))),
   "a drawn recurve bow + an orange up arrow (more bow damage)"),
 R("Archer.b1.r3a", "damage", D("EagleEye", lambda ic: (eye(ic, 24, 22, 1.4, iris="emerald"), arrow_shaft(ic, 6, 46, 54, 46, 1.0), g_up(ic, 52, 18, 0.8, "damage"))),
   "a sharp green eye over a long flying arrow + an orange up arrow (long shots deal more)"),
 R("Archer.b1.r3b", "control", D("PinBounce", lambda ic: (pin(ic, 20, 32, 0.85), g_fork(ic, 44, 30, 1.15, "control"))),
   "the pinning arrow + a yellow fork (bounces to root one more target)"),
 R("Archer.b1.r3c", "ability", D("Quickdraw", lambda ic: (rapid(ic, 24, 26, 0.85), g_clock(ic, 49, 48, 1.05))),
   "the Rapid Fire arrows + a cooldown clock (bow hits cut its cooldown)"),
 R("Archer.b1.r4a", "damage", D("RapidPower", lambda ic: (rapid(ic, 24, 26, 0.9), g_up(ic, 50, 50, 1.1, "damage"))),
   "the Rapid Fire arrows + an orange up arrow (more damage per arrow)"),
 R("Archer.b1.r4b", "damage", D("CalledShot", lambda ic: (g_target(ic, 28, 28, 1.9), arrow_shaft(ic, 4, 52, 26, 30, 1.0), g_plus(ic, 50, 52, 0.85, "damage"))),
   "an arrow flying into a big orange target mark + a plus (hits on Marked enemies deal more)"),
 R("Archer.b1.r5a", "speed", D("FleetRanger", lambda ic: (boot(ic, 32, 30, 1.4, pal=G, sole="leather", line=True), g_speed(ic, 4, 22, 1.0),
                                                         g_bolt(ic, 50, 50, 0.75, "stamina_y"))),
   "a green ranger boot with teal speed lines + a stamina bolt (move speed; kills give Stamina)"),
 R("Archer.b1.r5b", "damage", D("FocusFire", lambda ic: (g_target(ic, 30, 30, 1.6), [arrow_shaft(ic, x_, y_, 30 + (x_ - 30) * 0.3, 30 + (y_ - 30) * 0.3, 0.8)
                                                                                 for x_, y_ in ((4, 8), (4, 52), (56, 6))], g_plus(ic, 52, 52, 0.8, "damage"))),
   "three arrows converging on one orange target + a plus (stacking damage on the same target)"),
 R("Archer.b1.r6", "damage", D("DeadEye", lambda ic: (burst(ic, 32, 32, 28, 12, 10, G, base=0.5), g_target(ic, 32, 32, 1.5), rapid(ic, 30, 32, 0.6))),
   "Rapid Fire arrows into a target on a green burst (capstone: +50% to pinned enemies, keeps the Mark)"),
 # ---------------------------------------------------------------- Trapper
 R("Archer.b2.r1a", "control", D("BowSlow", lambda ic: (bowshot(ic, 10, 26, 1.1), g_snail(ic, 47, 51, 1.0))),
   "a drawn bow + a yellow snail (arrows slow)"),
 R("Archer.b2.r1b", "control", D("Tripwire", lambda ic: (ic.add(capsule(6, 40, 58, 40, 1.0), "cream", base=0.6, bevel=0),
                                                        [ic.add(capsule(x_, 34, x_, 50, 1.8), "wood", base=0.55, line=True) for x_ in (8, 56)],
                                                        boot(ic, 30, 22, 0.9, pal="leather", line=True), g_stars(ic, 46, 52, 0.75))),
   "a boot tripping a snare wire between two pegs + yellow root stars (a dodge leaves a snare)"),
 R("Archer.b2.r2.free", "ability", Reuse(CLS, "HuntersNet"), "REUSED ability icon Archer/HuntersNet.png"),
 R("Archer.b2.r2a", "ability", D("NetRadius", lambda ic: (hnet(ic, 32, 32, 15), g_expand(ic, 32, 32, 25, 0.72))),
   "the rope net with four blue arrows pushing outward (a bigger net)"),
 R("Archer.b2.r2b", "control", D("NetPull", lambda ic: (hnet(ic, 30, 30, 16), g_pull(ic, 50, 52, 0.85, "control", ang=200))),
   "the rope net + a yellow pull arrow (drags caught enemies to its centre)"),
 R("Archer.b2.r2c", "damage", D("BarbedMesh", lambda ic: (hnet(ic, 26, 28, 18), g_up(ic, 50, 50, 1.0, "damage"),
                                                         [ic.add(poly([(x_, y_ - 3), (x_ + 2, y_ + 2), (x_ - 2, y_ + 2)]), "steel", base=0.8, line=True)
                                                          for x_, y_ in ((18, 22), (30, 16), (34, 34), (20, 36))])),
   "the rope net with steel barbs + an orange up arrow (netted enemies take more)"),
 R("Archer.b2.r3a", "control", D("BowKnockback", lambda ic: (bowshot(ic, 8, 24, 1.05), g_push(ic, 48, 50, 1.0, ang=0))),
   "a drawn bow + a yellow knockback arrow (bow hits knock back)"),
 R("Archer.b2.r3b", "control", D("RootDuration", lambda ic: (hnet(ic, 26, 28, 17), g_hourglass(ic, 50, 48, 1.15, "control"))),
   "the rope net + a yellow hourglass (roots and snares last longer)"),
 R("Archer.b2.r4a", "control", D("NetLinger", lambda ic: (hnet(ic, 24, 26, 16), g_snail(ic, 47, 51, 1.0))),
   "the rope net + a yellow snail (netted enemies stay slower)"),
 R("Archer.b2.r4b", "health", D("Clinch", lambda ic: (hnet(ic, 26, 28, 18), g_mob(ic, 26, 28, 0.75), g_down(ic, 50, 50, 1.0, "health"))),
   "a mob caught in the net + a red down arrow (rooted enemies hit you for less)"),
 R("Archer.b2.r5a", "ability", D("Lockdown", lambda ic: (hnet(ic, 26, 28, 17), g_clock(ic, 49, 48, 1.05))),
   "the rope net + a cooldown clock (Hunter's Net comes back sooner)"),
 R("Archer.b2.r5b", "health", D("ThickHide", lambda ic: (shield(ic, 28, 28, 1.6, pal="leather"), hnet(ic, 46, 46, 9), g_down(ic, 14, 52, 0.85, "health"))),
   "a thick leather shield beside a small net + a red down arrow (less damage while an enemy is rooted)"),
 R("Archer.b2.r6", "control", D("SpidersDen", lambda ic: (hnet(ic, 22, 24, 13), hnet(ic, 42, 40, 13), g_stars(ic, 48, 14, 0.85))),
   "two nets (2 charges) + stun stars (capstone: netted twice = stunned)"),
 # ---------------------------------------------------------------- Stormvolley
 R("Archer.b3.r1a", "ability", D("BowSplit", lambda ic: (bowshot(ic, 6, 26, 1.0), g_fork(ic, 46, 48, 1.1))),
   "a drawn bow + a blue fork (bow hits splash to one more enemy)"),
 R("Archer.b3.r1b", "damage", D("VolleyTraining", lambda ic: (rain(ic, 20, 26, 0.7), bomb(ic, 44, 22, 6), hnet(ic, 44, 46, 8), g_up(ic, 18, 52, 0.8, "damage"))),
   "falling arrows, a bomb and a small net + an orange up arrow (all three volleys deal more)"),
 R("Archer.b3.r2.free", "ability", Reuse(CLS, "ArrowRain"), "REUSED ability icon Archer/ArrowRain.png"),
 R("Archer.b3.r2a", "ability", D("RainRadius", lambda ic: (rain(ic, 32, 32, 0.85), g_expand(ic, 32, 32, 26, 0.7))),
   "the falling Arrow Rain with four blue arrows pushing outward (a bigger rain)"),
 R("Archer.b3.r2b", "ability", D("RainDuration", lambda ic: (rain(ic, 26, 28), g_hourglass(ic, 50, 48, 1.15))),
   "the falling Arrow Rain + a blue hourglass (lasts longer)"),
 R("Archer.b3.r3a", "control", D("Pinfall", lambda ic: (rain(ic, 26, 26, 0.95), ic.add(ering(28, 52, 16, 4, 12, 2.4), G, base=0.5, bevel=0, line=True),
                                                       g_stars(ic, 50, 14, 0.75))),
   "the Arrow Rain landing in a root ring + yellow stars (a chance to pin)"),
 R("Archer.b3.r3b", "resource", D("DeepQuiver", lambda ic: (ic.add(rrect(14, 18, 32, 56, 4), "leather", base=0.55, grad=0.6, line=True),
                                                           [arrow_shaft(ic, 18 + k * 5, 26, 18 + k * 5 + 2, 6, 0.8) for k in range(3)],
                                                           g_bolt(ic, 46, 44, 1.0, "stamina_y"), g_plus(ic, 52, 16, 0.75, "resource"))),
   "a full leather quiver + a stamina bolt and plus (more Stamina, Arrow Rain costs less)"),
 R("Archer.b3.r3c", "damage", D("RainRicochet", lambda ic: (rain(ic, 24, 24, 0.85), g_fork(ic, 46, 48, 1.05, "damage"))),
   "the Arrow Rain + an orange fork (arrows bounce once)"),
 R("Archer.b3.r4a", "damage", D("RainPower", lambda ic: (rain(ic, 26, 28), g_up(ic, 50, 50, 1.1, "damage"))),
   "the Arrow Rain + an orange up arrow (more damage)"),
 R("Archer.b3.r4b", "control", D("RainPull", lambda ic: (rain(ic, 32, 26, 0.8), [arrow(ic, x_, 50, 0.7, "control", ang=a_) for x_, a_ in ((10, 0), (54, 180))])),
   "the Arrow Rain with yellow arrows pulling enemies to its centre"),
 R("Archer.b3.r5.free", "ability", Reuse(CLS, "ExplosiveArrow"), "REUSED ability icon Archer/ExplosiveArrow.png"),
 R("Archer.b3.r5a", "ability", D("BlastRadius", lambda ic: (boom(ic, 30, 34, 0.85), g_expand(ic, 32, 32, 26, 0.7))),
   "the Explosive Arrow with four blue arrows pushing outward (a bigger blast)"),
 R("Archer.b3.r5b", "control", D("BlastKnockback", lambda ic: (boom(ic, 24, 32, 0.95), g_push(ic, 50, 50, 1.0, ang=-20))),
   "the Explosive Arrow + a yellow knockback arrow (the blast knocks back and staggers)"),
 R("Archer.b3.r6", "damage", D("Firestorm", lambda ic: (burst(ic, 32, 34, 28, 12, 12, "flame", base=0.55), rain(ic, 32, 30, 0.8), bomb(ic, 46, 46, 6))),
   "the Arrow Rain inside a fire burst with a bomb (capstone: an Explosive Arrow detonates the whole rain)"),
]
