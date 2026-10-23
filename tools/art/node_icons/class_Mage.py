"""Mage class tree node icons (44: 39 new + 5 reused ability icons) - DRAFT v1. Runner: tools/art/make_class_node_icons.py.
Class colour sky blue #7fb0e0. Subjects echo the approved ability icons: Meteor = a burning rock with a fire tail, Starfall = pale
falling stars, Arcane Beam = a violet beam, Mana Barrier = the glassy blue dome, Frost Nova = the six-armed ice crystal; a mana crystal
for Mana itself and an orb staff for plain spells."""
from node_icons.class_kit import *

CLS = "Mage"
G = C(CLS)


def met(ic, cx=26, cy=34, s=1.25):
    meteor(ic, cx, cy, s)


def stars(ic, cx=28, cy=30, s=1.0):
    falling_star(ic, cx - 8 * s, cy + 8 * s, 8 * s)
    falling_star(ic, cx + 8 * s, cy - 6 * s, 6 * s)


def abeam(ic, x0=8, y0=52, x1=46, y1=14, w=4.5):
    beam(ic, x0, y0, x1, y1, w)
    ic.add(circle(x0, y0, w + 2), "arcane", mode="sphere", base=0.8, line=True)


def barrier(ic, cx=28, by=42, R=19):
    dome(ic, cx, by, R)


def nova(ic, cx=28, cy=30, R=19):
    snowflake(ic, cx, cy, R)


def staff(ic):
    orb_staff(ic, 12, 56, 34, 22, orb="arcane", r=6)


ROWS = [
 # ---------------------------------------------------------------- Cosmos
 R("Mage.b1.r1.free", "ability", Reuse(CLS, "Meteor"), "REUSED ability icon Mage/Meteor.png"),
 R("Mage.b1.r1a", "ability", D("MeteorRadius", lambda ic: (met(ic, 30, 34, 1.0), g_expand(ic, 32, 32, 26, 0.7))),
   "the burning Meteor with four blue arrows pushing outward (a bigger impact)"),
 R("Mage.b1.r1b", "damage", D("MeteorPower", lambda ic: (met(ic), g_up(ic, 50, 50, 1.1, "damage"))),
   "the burning Meteor + an orange up arrow (more damage)"),
 R("Mage.b1.r2.free", "ability", Reuse(CLS, "Starfall"), "REUSED ability icon Mage/Starfall.png"),
 R("Mage.b1.r2a", "ability", D("MoreStars", lambda ic: (stars(ic, 26, 30), falling_star(ic, 46, 46, 5), g_plus(ic, 52, 22, 0.8, "ability"))),
   "three falling stars + a blue plus (more stars)"),
 R("Mage.b1.r2b", "ability", D("StarFollow", lambda ic: (falling_star(ic, 18, 32, 8), g_homing(ic, 42, 40, 1.4))),
   "a falling star + a blue homing arrow into a target (stars seek the nearest enemy)"),
 R("Mage.b1.r2c", "damage", D("AstralFocus", lambda ic: (staff(ic), falling_star(ic, 42, 18, 5), g_up(ic, 50, 50, 1.0, "damage"))),
   "an orb staff with a star + an orange up arrow (more spell damage)"),
 R("Mage.b1.r3a", "damage", D("Crater", lambda ic: (ground(ic, 46, crack=False), ic.add(ellipse(30, 47, 18, 4.5), "flame", base=0.75, bevel=0),
                                                   flame(ic, 22, 40, 0.65), flame(ic, 36, 40, 0.8), g_clock(ic, 50, 16, 0.85, "damage"))),
   "a burning crater with flames + a ticking clock (Meteor leaves fire that burns over time)"),
 R("Mage.b1.r3b", "damage", D("MeteorEcho", lambda ic: (meteor(ic, 40, 20, 0.7), met(ic, 22, 40, 0.95), g_echo(ic, 52, 46, 0.9, "damage"))),
   "two Meteors, a smaller one following + orange echo arcs (a second Meteor lands)"),
 R("Mage.b1.r3c", "ability", D("SwiftCasting", lambda ic: (staff(ic), g_clock(ic, 48, 46, 1.1))),
   "an orb staff + a cooldown clock (every Mage ability comes back sooner)"),
 R("Mage.b1.r4a", "control", D("MeteorKnockback", lambda ic: (met(ic, 30, 30, 1.0), g_push(ic, 50, 52, 0.9, ang=20), g_push(ic, 12, 52, 0.9, ang=160))),
   "the Meteor with yellow knockback arrows flinging enemies outward"),
 R("Mage.b1.r4b", "ability", D("ShootingStar", lambda ic: (falling_star(ic, 20, 40, 7), meteor(ic, 40, 22, 0.75), g_clock(ic, 50, 50, 0.8))),
   "a star hitting, a small Meteor + a cooldown clock (Starfall hits cut Meteor's cooldown)"),
 R("Mage.b1.r5a", "damage", D("CriticalMass", lambda ic: (g_mob(ic, 30, 30, 1.2), meteor(ic, 12, 14, 0.5), snowflake(ic, 50, 14, 7), g_up(ic, 50, 50, 1.0, "damage"))),
   "a mob hit by two different spells (fire + frost) + an orange up arrow"),
 R("Mage.b1.r5b", "speed", D("CometTail", lambda ic: (met(ic, 30, 30, 1.0), g_speed(ic, 2, 48, 0.9), g_wing(ic, 46, 50, 0.95))),
   "the Meteor with teal speed lines + a wing (casting it gives move speed)"),
 R("Mage.b1.r6", "damage", D("Cataclysm", lambda ic: (burst(ic, 32, 34, 30, 13, 12, "flame", base=0.5), met(ic, 30, 36, 1.0), falling_star(ic, 50, 16, 5),
                                                     falling_star(ic, 14, 14, 4))),
   "a giant Meteor on a fire burst with stars falling round it (capstone: double radius + 3 stars)"),
 # ---------------------------------------------------------------- Arcanist
 R("Mage.b2.r1a", "resource", D("ManaWell", lambda ic: (g_crystal(ic, 28, 30, 2.4), g_plus(ic, 50, 50, 1.0, "resource"))),
   "a big blue mana crystal + a violet plus (more max Mana)"),
 R("Mage.b2.r1b", "damage", D("Overflow", lambda ic: (g_crystal(ic, 26, 34, 2.0), [lines(ic, [(x_, 10, x_, 16)], "resource", 1.4) for x_ in (16, 26, 36)],
                                                     g_up(ic, 50, 50, 1.0, "damage"))),
   "an overflowing mana crystal + an orange up arrow (full Mana: the next spell hits harder)"),
 R("Mage.b2.r2.free", "ability", Reuse(CLS, "ArcaneBeam"), "REUSED ability icon Mage/ArcaneBeam.png"),
 R("Mage.b2.r2a", "ability", D("BeamPierce", lambda ic: (abeam(ic, 8, 30, 54, 30, 3.6), [g_mob(ic, x_, 30, 0.55) for x_ in (30, 46)], g_plus(ic, 50, 52, 0.8, "ability"))),
   "the violet beam passing through two mobs + a blue plus (pierces one more)"),
 R("Mage.b2.r2b", "ability", D("BeamDuration", lambda ic: (abeam(ic), g_hourglass(ic, 50, 48, 1.15))),
   "the Arcane Beam + a blue hourglass (channels longer)"),
 R("Mage.b2.r3a", "damage", D("BeamRamp", lambda ic: (abeam(ic, 8, 46, 40, 14, 3.5), [g_up(ic, 38 + k * 7, 56 - k * 6, 0.55 + 0.12 * k, "damage") for k in range(3)])),
   "the Arcane Beam + three growing orange up arrows (damage ramps while channelling)"),
 R("Mage.b2.r3b", "control", D("BeamSlow", lambda ic: (abeam(ic), g_snail(ic, 47, 51, 1.0))),
   "the Arcane Beam + a yellow snail (the beam slows)"),
 R("Mage.b2.r3c", "resource", D("Attunement", lambda ic: (g_crystal(ic, 28, 30, 2.0), arc_arrow(ic, 28, 30, 21, 120, 400, 2.6, "resource"), g_plus(ic, 50, 52, 0.8, "resource"))),
   "a mana crystal in a violet refill arrow + a plus (Mana regen)"),
 R("Mage.b2.r4a", "ability", D("BeamFork", lambda ic: (abeam(ic, 8, 50, 30, 30, 3.6), g_fork(ic, 42, 26, 1.2))),
   "the Arcane Beam splitting into a blue fork (hits fork to one more enemy)"),
 R("Mage.b2.r4b", "ability", D("FocusingLens", lambda ic: (ic.add(ering(28, 28, 14, 14, 10, 10), "gold", mode="torus", torus=(28, 28, 14, 14, 10, 10), bevel=0, line=True),
                                                          ic.add(circle(28, 28, 10), "glass", base=0.75, bevel=0.6), ic.add(capsule(38, 38, 52, 52, 3), "wood", base=0.55, line=True),
                                                          arrow(ic, 50, 14, 0.85, "ability", ang=-45))),
   "a gold magnifying lens + a blue arrow outward (more spell range)"),
 R("Mage.b2.r4c", "resource", D("Feedback", lambda ic: (abeam(ic, 8, 52, 30, 30, 3.4), g_skull(ic, 38, 22, 1.0), g_crystal(ic, 48, 48, 0.9), g_plus(ic, 56, 30, 0.6, "resource"))),
   "the beam killing (a skull) + a mana crystal and plus (a beam kill refunds Mana)"),
 R("Mage.b2.r5a", "damage", D("BeamEcho", lambda ic: (abeam(ic), g_echo(ic, 50, 44, 1.1, "damage"))),
   "the Arcane Beam + orange echo arcs (its hits strike again)"),
 R("Mage.b2.r5b", "speed", D("ArcaneHaste", lambda ic: (abeam(ic, 16, 50, 52, 14, 3.6), boot(ic, 16, 46, 0.7, pal="arcane", line=True), g_speed(ic, 2, 26, 0.8))),
   "a boot moving while the beam fires + teal speed lines (speed while channelling)"),
 R("Mage.b2.r6", "damage", D("PrismOverload", lambda ic: (ic.add(poly([(20, 44), (32, 14), (44, 44)]), "glass", base=0.7, grad=0.6, bevel=1.0, line=True),
                                                         beam(ic, 2, 40, 24, 32, 2.6), [beam(ic, 40, 32, x_, y_, 2.0, pal=p_) for x_, y_, p_ in ((62, 18, "flame"), (62, 32, "arcane"), (62, 46, "ice"))])),
   "a glass prism splitting the beam into three (capstone: the beam lasts twice as long and keeps gaining damage)"),
 # ---------------------------------------------------------------- Spellward
 R("Mage.b3.r1a", "resource", D("BlinkStep", lambda ic: (g_ally(ic, 16, 34, 1.0, "arcane"), g_ally(ic, 44, 34, 1.2, G), arcp(ic, 30, 34, 14, 200, 340, 2.2, acc("resource"), line=True),
                                                        g_crystal(ic, 50, 14, 0.6))),
   "a figure blinking from one spot to another along a violet arc + a mana crystal (dodge blinks, costs Mana)"),
 R("Mage.b3.r1b", "health", D("ArcaneSkin", lambda ic: (ic.add(ering(28, 30, 18, 18, 14.5, 14.5), "arcane", base=0.6, bevel=0, line=True), g_ally(ic, 28, 32, 1.2, G),
                                                       g_down(ic, 50, 50, 1.0, "health"))),
   "a figure in a violet magic skin ring + a red down arrow (less magic / projectile damage)"),
 R("Mage.b3.r2.free", "ability", Reuse(CLS, "ManaBarrier"), "REUSED ability icon Mage/ManaBarrier.png"),
 R("Mage.b3.r2a", "ward", D("BarrierWard", lambda ic: (barrier(ic), g_ward(ic, 50, 48, 1.1))),
   "the blue Mana Barrier dome + a white ward shield (absorbs more)"),
 R("Mage.b3.r2b", "ability", D("BarrierDuration", lambda ic: (barrier(ic), g_hourglass(ic, 50, 48, 1.15))),
   "the Mana Barrier dome + a blue hourglass (lasts longer)"),
 R("Mage.b3.r3a", "ward", D("Conduit", lambda ic: (barrier(ic, 28, 40, 18), g_crystal(ic, 28, 34, 0.8), g_up(ic, 50, 50, 1.0, "ward"))),
   "the dome with a mana crystal inside + a white up arrow (soaks more per Mana)"),
 R("Mage.b3.r3b", "control", D("BarrierBlast", lambda ic: (barrier(ic, 30, 44, 16), [arrow(ic, 30 + 22 * math.cos(math.radians(a_)), 40 + 22 * math.sin(math.radians(a_)), 0.7,
                                                                                         "control", ang=a_) for a_ in (-160, -90, -20)])),
   "the dome breaking with yellow arrows blasting enemies away"),
 R("Mage.b3.r3c", "resource", D("ManaTide", lambda ic: (barrier(ic, 26, 40, 17), g_crystal(ic, 48, 46, 0.9), arc_arrow(ic, 48, 46, 11, 130, 400, 2.0, "resource"))),
   "the dome + a mana crystal in a refill arrow (Mana regen while it stands)"),
 R("Mage.b3.r4a", "control", D("BarrierSlow", lambda ic: (barrier(ic, 26, 40, 17), g_snail(ic, 47, 51, 1.0))),
   "the dome + a yellow snail (enemies that hit it are slowed)"),
 R("Mage.b3.r4b", "health", D("LastWard", lambda ic: (g_skull(ic, 26, 28, 1.6), ic.add(capsule(12, 46, 42, 12, 2.4), "acc_health", base=0.75, line=True), g_ward(ic, 50, 48, 1.0))),
   "a skull crossed out + a white ward (a killing blow is cancelled once a minute)"),
 R("Mage.b3.r4c", "ability", D("ClearMind", lambda ic: (barrier(ic, 26, 40, 17), g_clock(ic, 49, 48, 1.05))),
   "the dome + a cooldown clock (Mana Barrier comes back sooner)"),
 R("Mage.b3.r5.free", "ability", Reuse(CLS, "FrostNova"), "REUSED ability icon Mage/FrostNova.png"),
 R("Mage.b3.r5a", "ability", D("NovaRadius", lambda ic: (nova(ic, 32, 32, 16), g_expand(ic, 32, 32, 26, 0.7))),
   "the Frost Nova crystal with four blue arrows pushing outward (bigger)"),
 R("Mage.b3.r5b", "control", D("NovaDuration", lambda ic: (nova(ic, 26, 28, 18), g_hourglass(ic, 50, 48, 1.15, "control"))),
   "the Frost Nova crystal + a yellow hourglass (the freeze lasts longer)"),
 R("Mage.b3.r6", "ability", D("GlacialAegis", lambda ic: (barrier(ic, 32, 46, 22), nova(ic, 32, 30, 13), g_repeat(ic, 52, 14, 0.8))),
   "a Frost Nova bursting from the Mana Barrier dome + a trigger arrow (capstone: the Nova fires when the barrier breaks)"),
]
