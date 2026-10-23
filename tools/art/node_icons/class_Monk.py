"""Monk class tree node icons (38: 33 new + 5 reused ability icons) - DRAFT v1. Runner: tools/art/make_class_node_icons.py.
Class colour saffron #f08a30 (wraps). Subjects echo the approved ability icons: Flowing Form = the saffron + teal swirl, Palm Strike = the
open wrapped palm, Cyclone Kick = the wrapped foot (Skyy: wrapped, not a bare foot), Hundred Fists = the wrapped fist, Still Water = a
drop over ripples. Combo = saffron pips."""
from node_icons.class_kit import *

CLS = "Monk"
G = C(CLS)


def flow(ic, cx=28, cy=30, s=1.0):
    swirl_form(ic, cx, cy, s)


def fists(ic, cx=28, cy=30, s=1.0):
    fist(ic, cx + 6 * s, cy - 6 * s, 0.75 * s)
    fist(ic, cx - 2 * s, cy + 4 * s, 0.95 * s)


def combo(ic, cx, cy, n=3, s=1.0):
    for k in range(n):
        ic.add(circle(cx + (k - (n - 1) / 2.0) * 6.5 * s, cy, 2.8 * s), G, mode="sphere", base=0.75, line=True)


def afterimage(ic, cx, cy, s=1.0, base=0.35):
    g_ally(ic, cx, cy, s, pal="rift")


ROWS = [
 # ---------------------------------------------------------------- Flow
 R("Monk.b1.r1.free", "ability", Reuse(CLS, "FlowingForm"), "REUSED ability icon Monk/FlowingForm.png"),
 R("Monk.b1.r1a", "speed", D("Haste", lambda ic: (boot(ic, 32, 30, 1.45, pal="linen", sole="leather", line=True), g_speed(ic, 4, 22, 1.0), g_plus(ic, 50, 52, 0.85, "speed"))),
   "a wrapped monk shoe with teal speed lines + a teal plus (move speed)"),
 R("Monk.b1.r1b", "resource", D("SecondWind", lambda ic: (g_bolt(ic, 26, 30, 1.7, "stamina_y"), arc_arrow(ic, 26, 30, 20, 120, 400, 2.6, "resource"),
                                                         g_plus(ic, 50, 52, 0.85, "resource"))),
   "a yellow stamina bolt in a violet refill arrow + a plus (Stamina regen)"),
 R("Monk.b1.r2.free", "ability", Reuse(CLS, "HundredFists"), "REUSED ability icon Monk/HundredFists.png"),
 R("Monk.b1.r2a", "damage", D("FistsPower", lambda ic: (fists(ic), g_up(ic, 50, 50, 1.1, "damage"))),
   "two wrapped fists (Hundred Fists) + an orange up arrow (more damage while it runs)"),
 R("Monk.b1.r2b", "resource", D("FistsEfficiency", lambda ic: (fists(ic), g_bolt(ic, 48, 46, 0.85, "stamina_y"), g_down(ic, 56, 22, 0.7, "resource"))),
   "two wrapped fists + a stamina bolt with a violet down arrow (costs less Stamina)"),
 R("Monk.b1.r3a", "damage", D("FistsEcho", lambda ic: (fists(ic, 24, 30), g_echo(ic, 50, 30, 1.15), combo(ic, 46, 54, 4, 0.75))),
   "two wrapped fists + echo arcs and four combo pips (every 4th hit repeats)"),
 R("Monk.b1.r3b", "ability", D("FormDuration", lambda ic: (flow(ic), g_hourglass(ic, 50, 48, 1.15))),
   "the Flowing Form swirl + a blue hourglass (lasts longer)"),
 R("Monk.b1.r4a", "damage", D("FullSpeedPower", lambda ic: (fist(ic, 32, 28, 1.1), g_speed(ic, 2, 20, 1.0), g_up(ic, 50, 50, 1.0, "damage"))),
   "a fist flying forward with speed lines + an orange up arrow (more damage at full speed)"),
 R("Monk.b1.r4b", "ability", D("FormRadius", lambda ic: (flow(ic, 32, 32, 0.85), g_expand(ic, 32, 32, 26, 0.7))),
   "the Flowing Form swirl with four blue arrows pushing outward (bigger afterimage pulse)"),
 R("Monk.b1.r5a", "control", D("Slipstream", lambda ic: (afterimage(ic, 16, 30, 1.0), afterimage(ic, 30, 30, 1.2), g_speed(ic, 2, 50, 0.7), g_stars(ic, 48, 46, 0.9))),
   "a dodge roll leaving teal afterimages + stun stars (dodging stuns enemies it passes)"),
 R("Monk.b1.r5b", "speed", D("FormSpeed", lambda ic: (flow(ic, 32, 28), g_wing(ic, 46, 50, 1.0), g_speed(ic, 4, 46, 0.8))),
   "the Flowing Form swirl + a teal wing and speed lines (more speed in Flowing Form)"),
 R("Monk.b1.r6", "damage", D("Untouchable", lambda ic: (flow(ic, 32, 32, 1.05), [afterimage(ic, 32 + 22 * math.cos(math.radians(a_)), 32 + 22 * math.sin(math.radians(a_)), 0.6)
                                                                             for a_ in (-90, 30, 150)])),
   "the Flowing Form swirl ringed by three teal afterimages striking around you (capstone)"),
 # ---------------------------------------------------------------- Fist
 R("Monk.b2.r1a", "damage", D("PalmPower", lambda ic: (palm(ic, 26, 34, 1.0), g_up(ic, 50, 50, 1.1, "damage"))),
   "the open wrapped palm (Palm Strike) + an orange up arrow (more damage)"),
 R("Monk.b2.r1b", "damage", D("FinisherEcho", lambda ic: (palm(ic, 24, 34, 0.95), g_echo(ic, 50, 26, 1.1), combo(ic, 46, 54, 3, 0.75))),
   "the open palm + echo arcs and combo pips (combo finishers echo)"),
 R("Monk.b2.r2.free", "ability", Reuse(CLS, "PalmStrike"), "REUSED ability icon Monk/PalmStrike.png"),
 R("Monk.b2.r2a", "control", D("PalmLaunch", lambda ic: (palm(ic, 24, 36, 0.95), g_mob(ic, 48, 16, 0.8), arrow(ic, 48, 32, 0.8, "control", ang=-90))),
   "the open palm launching a mob upward (yellow up arrow)"),
 R("Monk.b2.r2b", "damage", D("PalmForce", lambda ic: (burst(ic, 28, 30, 24, 10, 8, "acc_damage", base=0.55), palm(ic, 28, 34, 0.9), g_plus(ic, 52, 52, 0.85, "damage"))),
   "the open palm on an orange impact burst + a plus (more Palm Strike damage)"),
 R("Monk.b2.r3a", "ability", D("PalmRicochet", lambda ic: (palm(ic, 22, 36, 0.9), g_fork(ic, 46, 30, 1.2))),
   "the open palm + a blue fork bouncing to another enemy"),
 R("Monk.b2.r3b", "control", D("PalmSlow", lambda ic: (palm(ic, 24, 34, 1.0), g_snail(ic, 47, 51, 1.0))),
   "the open palm + a yellow snail (slows)"),
 R("Monk.b2.r4a", "control", D("PalmStun", lambda ic: (palm(ic, 24, 36, 0.95), g_stars(ic, 46, 14, 0.85), g_hourglass(ic, 51, 50, 0.95, "control"))),
   "the open palm + stun stars + a yellow hourglass (longer stun)"),
 R("Monk.b2.r4b", "damage", D("ComboPower", lambda ic: (fist(ic, 28, 26, 1.05), combo(ic, 26, 48, 4, 1.0), g_up(ic, 52, 50, 0.9, "damage"))),
   "a fist over a row of saffron combo pips + an orange up arrow (each combo step hits harder)"),
 R("Monk.b2.r5.free", "ability", Reuse(CLS, "CycloneKick"), "REUSED ability icon Monk/CycloneKick.png"),
 R("Monk.b2.r5a", "resource", D("ComboStamina", lambda ic: (combo(ic, 30, 18, 5, 1.0), g_bolt(ic, 28, 40, 1.15, "stamina_y"), g_plus(ic, 50, 50, 0.85, "resource"))),
   "five combo pips above a stamina bolt + a violet plus (every 5th stack gives Stamina back)"),
 R("Monk.b2.r5b", "ability", D("Flurry", lambda ic: (combo(ic, 30, 22, 5, 1.1), combo(ic, 30, 34, 2, 1.1), g_plus(ic, 50, 50, 1.0, "ability"))),
   "a full row of combo pips with two more + a blue plus (higher combo cap)"),
 R("Monk.b2.r6", "damage", D("ThousandPalms", lambda ic: (burst(ic, 32, 32, 30, 14, 12, G, base=0.55), palm(ic, 22, 36, 0.7), palm(ic, 42, 36, 0.7), palm(ic, 32, 28, 0.8))),
   "three open palms striking at once on a saffron burst (capstone: Palm Strike with almost no cooldown)"),
 # ---------------------------------------------------------------- Still Water
 R("Monk.b3.r1a", "ward", D("FlowWard", lambda ic: (flow(ic, 26, 28, 0.9), g_ward(ic, 49, 47, 1.15))),
   "the Flowing Form swirl + a white ward shield (a ward when it ends)"),
 R("Monk.b3.r1b", "control", D("StanceSlow", lambda ic: (still_water(ic, 26, 26, 0.9), g_snail(ic, 47, 51, 1.0))),
   "the Still Water drop + a yellow snail (enemies you hit are slower)"),
 R("Monk.b3.r2.free", "ability", Reuse(CLS, "StillWater"), "REUSED ability icon Monk/StillWater.png"),
 R("Monk.b3.r2a", "ability", D("CounterWindow", lambda ic: (still_water(ic, 26, 26, 0.95), g_hourglass(ic, 50, 48, 1.15))),
   "the Still Water drop + a blue hourglass (a longer counter window)"),
 R("Monk.b3.r2b", "ward", D("CounterWard", lambda ic: (still_water(ic, 26, 26, 0.95), g_ward(ic, 49, 47, 1.15))),
   "the Still Water drop + a white ward shield (counters ward you)"),
 R("Monk.b3.r3a", "resource", D("StillEfficiency", lambda ic: (still_water(ic, 26, 26, 0.95), g_crystal(ic, 47, 46, 1.0), g_down(ic, 56, 26, 0.7, "resource"))),
   "the Still Water drop + a mana crystal with a violet down arrow (costs less Mana)"),
 R("Monk.b3.r3b", "damage", D("DeflectBack", lambda ic: (palm(ic, 18, 38, 0.8), arrow_shaft(ic, 30, 30, 52, 14, 1.0), arc_arrow(ic, 34, 24, 12, 160, 300, 2.2, "damage"))),
   "an open palm turning an arrow back at its shooter (an orange return arc)"),
 R("Monk.b3.r4a", "control", D("CounterPush", lambda ic: (still_water(ic, 24, 26, 0.9), g_push(ic, 50, 50, 1.0, ang=-20))),
   "the Still Water drop + a yellow knockback arrow (counters knock back)"),
 R("Monk.b3.r4b", "control", D("CounterStun", lambda ic: (still_water(ic, 24, 28, 0.9), g_stars(ic, 46, 14, 0.85), g_hourglass(ic, 51, 50, 0.95, "control"))),
   "the Still Water drop + stun stars + a yellow hourglass (longer counter stun)"),
 R("Monk.b3.r5a", "damage", D("CounterWave", lambda ic: (still_water(ic, 30, 24, 0.85), [arcp(ic, 30, 40, R_, 20, 160, 2.4, acc("damage"), base=b_, line=True)
                                                                                   for R_, b_ in ((20, 0.8), (27, 0.6))])),
   "the Still Water drop sending orange shockwave arcs out (counters emit a shockwave)"),
 R("Monk.b3.r5b", "damage", D("CounterPower", lambda ic: (still_water(ic, 26, 26, 0.95), g_up(ic, 50, 50, 1.1, "damage"))),
   "the Still Water drop + an orange up arrow (more counter damage)"),
 R("Monk.b3.r6", "ability", D("NoMind", lambda ic: (g_ring(ic, 32, 32, 27, 2.4, "ability", 0.5), still_water(ic, 32, 30, 0.95), g_clock(ic, 50, 50, 0.8))),
   "the Still Water drop in a calm blue ring + a cooldown clock (capstone: a counter resets your cooldowns)"),
]
