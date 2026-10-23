"""Priest class tree node icons (46: 41 new + 5 reused ability icons) - DRAFT v1. Runner: tools/art/make_class_node_icons.py.
Class colour holy gold #f2e6a0. Subjects echo the approved ability icons: Sacred Heal = the gold cross, Shield Bubble = a soul-cyan
bubble round a shield, Guardian Spirit = spread wings + a halo, Sanctuary = the gold arch shrine on a glowing floor ring, Martyr's Grace
= hearts linked by a gold bolt; a star-tipped wand for the wand bolts."""
from node_icons.class_kit import *

CLS = "Priest"
G = C(CLS)


def heal(ic, cx=26, cy=30, s=1.0):
    holy_cross(ic, cx, cy, s)


def bub(ic, cx=26, cy=30, s=1.0):
    bubble_shield(ic, cx, cy, s * 0.95)


def spirit(ic, cx=28, cy=30, s=1.0):
    wings_halo(ic, cx, cy, s)


def sanct(ic, cx=28, by=46, s=1.0):
    shrine(ic, cx, by, s)


def martyr(ic, cx=28, cy=30, s=1.0):
    ic.add(heart(cx - 8 * s, cy - 8 * s, 0.55 * s), "acc_health", base=0.6, grad=0.6, bevel=0.9, line=True)
    ic.add(heart(cx + 8 * s, cy + 8 * s, 0.75 * s), "acc_health", base=0.62, grad=0.6, bevel=0.9, line=True)
    lines(ic, [(cx - 4 * s, cy - 4 * s, cx + 1 * s, cy - 2 * s), (cx + 1 * s, cy - 2 * s, cx - 1 * s, cy + 2 * s), (cx - 1 * s, cy + 2 * s, cx + 4 * s, cy + 4 * s)],
          "xp", 1.4 * s)


ROWS = [
 # ---------------------------------------------------------------- Devotion
 R("Priest.b1.r1.free", "ability", Reuse(CLS, "SacredHeal"), "REUSED ability icon Priest/SacredHeal.png"),
 R("Priest.b1.r1a", "health", D("HealPower", lambda ic: (heal(ic), g_up(ic, 50, 50, 1.1, "health"))),
   "the gold Sacred Heal cross + a red up arrow (heals more)"),
 R("Priest.b1.r1b", "ability", D("HealReach", lambda ic: (heal(ic, 20, 26, 0.8), g_zap(ic, 40, 44, 1.1), g_ally(ic, 52, 34, 0.6, G))),
   "the heal cross arcing on to one more ally far away (a blue bolt to an ally)"),
 R("Priest.b1.r1c", "resource", D("HealEfficiency", lambda ic: (heal(ic), g_crystal(ic, 47, 46, 1.0), g_down(ic, 56, 26, 0.7, "resource"))),
   "the heal cross + a mana crystal with a violet down arrow (costs less Mana)"),
 R("Priest.b1.r2.free", "ability", Reuse(CLS, "MartyrsGrace"), "REUSED ability icon Priest/MartyrsGrace.png"),
 R("Priest.b1.r2a", "health", D("BloodCovenant", lambda ic: (martyr(ic, 26, 28), g_plus(ic, 50, 50, 1.0, "health"))),
   "Martyr's Grace hearts linked by a gold bolt + a red plus (heals more)"),
 R("Priest.b1.r2b", "ability", D("SwiftPrayer", lambda ic: (wand(ic, 12, 56, 34, 22), g_clock(ic, 48, 46, 1.1))),
   "a star-tipped wand + a cooldown clock (every Priest ability comes back sooner)"),
 R("Priest.b1.r3a", "health", D("HealEcho", lambda ic: (heal(ic, 24, 28), g_echo(ic, 50, 30, 1.1, "health"), g_repeat(ic, 48, 52, 0.75, "health"))),
   "the heal cross + red echo arcs and a repeat arrow (heals again 2s later)"),
 R("Priest.b1.r3b", "health", D("Renewal", lambda ic: (heal(ic), g_clock(ic, 49, 48, 1.0, "health"))),
   "the heal cross + a red clock (more healing over time)"),
 R("Priest.b1.r3c", "ability", D("LongReach", lambda ic: (heal(ic, 22, 30, 0.85), arrow(ic, 48, 30, 1.0, "ability", ang=0), g_ring(ic, 22, 30, 26, 2.0, "ability", 0.5))),
   "the heal cross in a wide blue range ring + an outward arrow (more heal range)"),
 R("Priest.b1.r4a", "ability", D("HealFollow", lambda ic: (heal(ic, 18, 22, 0.7), g_lowhp(ic, 44, 44, 1.0), g_homing(ic, 32, 30, 1.0))),
   "the heal cross homing on to a drained heart (centres on the most hurt ally)"),
 R("Priest.b1.r4b", "health", D("Triage", lambda ic: (g_lowhp(ic, 26, 28, 1.9), heal(ic, 48, 46, 0.55), g_plus(ic, 52, 16, 0.75, "health"))),
   "a nearly empty heart with a heal cross + a red plus (more for allies below 40%)"),
 R("Priest.b1.r4c", "resource", D("Clarity", lambda ic: (g_crystal(ic, 28, 30, 2.0), arc_arrow(ic, 28, 30, 21, 120, 400, 2.6, "resource"), g_plus(ic, 50, 52, 0.8, "resource"))),
   "a mana crystal in a violet refill arrow + a plus (Mana regen)"),
 R("Priest.b1.r5a", "ward", D("Overheal", lambda ic: (g_heart(ic, 26, 28, 2.0, plus_=False), heal(ic, 26, 26, 0.45), g_ward(ic, 50, 48, 1.05))),
   "a full heart with a small cross + a white ward (healing a full ally gives a ward)"),
 R("Priest.b1.r5b", "speed", D("Benediction", lambda ic: (g_ally(ic, 30, 32, 1.4, G), heal(ic, 46, 14, 0.4), g_speed(ic, 2, 26, 1.0), g_wing(ic, 46, 50, 0.9))),
   "a healed ally running with teal speed lines + a wing (healed allies move faster)"),
 R("Priest.b1.r6", "health", D("Miracle", lambda ic: (burst(ic, 32, 32, 30, 14, 12, "holy", base=0.55), heal(ic, 32, 30, 1.0), g_lowhp(ic, 50, 52, 0.75))),
   "the heal cross on a radiant gold burst + a drained heart (capstone: an ally below 20% is healed in full)"),
 # ---------------------------------------------------------------- Bulwark
 R("Priest.b2.r1a", "ward", D("Ward", lambda ic: (heater(ic, 26, 28, 1.6, field="rift", trim=G), g_plus(ic, 50, 50, 1.0, "ward"))),
   "a gold-trimmed soul shield + a white plus (shields absorb more)"),
 R("Priest.b2.r1b", "health", D("Steadfast", lambda ic: (bub(ic, 26, 28, 0.9), g_down(ic, 50, 50, 1.0, "health"))),
   "the Shield Bubble + a red down arrow (less damage while it is up)"),
 R("Priest.b2.r2.free", "ability", Reuse(CLS, "ShieldBubble"), "REUSED ability icon Priest/ShieldBubble.png"),
 R("Priest.b2.r2a", "ability", D("BubbleDuration", lambda ic: (bub(ic), g_hourglass(ic, 50, 48, 1.15))),
   "the Shield Bubble + a blue hourglass (lasts longer)"),
 R("Priest.b2.r2b", "ability", D("BubbleRadius", lambda ic: (bub(ic, 32, 32, 0.8), g_expand(ic, 32, 32, 26, 0.7))),
   "the Shield Bubble with four blue arrows pushing outward (covers more)"),
 R("Priest.b2.r2c", "control", D("Rebound", lambda ic: (bub(ic, 28, 32, 0.85), g_push(ic, 52, 14, 0.75, ang=-40), g_push(ic, 52, 52, 0.75, ang=40))),
   "the Shield Bubble breaking + yellow knockback arrows (pushes enemies back)"),
 R("Priest.b2.r3a", "resource", D("BubbleEfficiency", lambda ic: (bub(ic), g_crystal(ic, 47, 46, 1.0), g_down(ic, 56, 26, 0.7, "resource"))),
   "the Shield Bubble + a mana crystal with a violet down arrow (costs less Mana)"),
 R("Priest.b2.r3b", "health", D("AegisLink", lambda ic: (bubble(ic, 28, 30, 22), g_party(ic, 28, 32, 1.1), g_down(ic, 52, 52, 0.85, "health"))),
   "the party inside the bubble + a red down arrow (players inside take less damage)"),
 R("Priest.b2.r4a", "ward", D("BubbleReform", lambda ic: (bub(ic, 26, 28, 0.9), g_repeat(ic, 50, 50, 1.1, "ward"))),
   "the Shield Bubble + a white repeat arrow (reforms once after breaking)"),
 R("Priest.b2.r4b", "health", D("Bastion", lambda ic: (g_heart(ic, 28, 28, 2.4, plus_=False), heater(ic, 28, 32, 0.7, field="rift", trim=G), g_plus(ic, 50, 50, 1.0, "health"))),
   "a big red heart with the soul shield on it + a red plus (+ max Health)"),
 R("Priest.b2.r4c", "health", D("HoldTheLine", lambda ic: (g_party(ic, 26, 32, 1.3), arcp(ic, 26, 32, 22, 200, 340, 2.2, "rift", base=0.5, line=True), g_down(ic, 50, 50, 1.0, "health"))),
   "the party under a fading bubble arc + a red down arrow (less damage after it breaks)"),
 R("Priest.b2.r5.free", "ability", Reuse(CLS, "GuardianSpirit"), "REUSED ability icon Priest/GuardianSpirit.png"),
 R("Priest.b2.r5a", "health", D("SpiritSave", lambda ic: (spirit(ic, 28, 28, 0.9), g_ally(ic, 28, 48, 0.7, G), g_down(ic, 52, 52, 0.85, "health"))),
   "the Guardian Spirit wings over a saved ally + a red down arrow (the saved player takes less damage)"),
 R("Priest.b2.r5b", "ward", D("SpiritPower", lambda ic: (spirit(ic, 28, 30), g_up(ic, 52, 50, 1.0, "ward"))),
   "the Guardian Spirit wings and halo + a white up arrow (stronger protection)"),
 R("Priest.b2.r5c", "ability", D("SpiritReach", lambda ic: (spirit(ic, 24, 30, 0.85), arrow(ic, 52, 46, 0.95, "ability", ang=0))),
   "the Guardian Spirit + a blue outward arrow (reaches farther)"),
 R("Priest.b2.r6", "ward", D("UndyingVigil", lambda ic: (bubble(ic, 32, 34, 25), spirit(ic, 32, 32, 0.9), g_clock(ic, 52, 52, 0.7))),
   "the Guardian Spirit inside a Shield Bubble + a clock (capstone: a save raises a bubble; shorter wait)"),
 # ---------------------------------------------------------------- Hallowed Ground
 R("Priest.b3.r1a", "ability", D("ZoneRadius", lambda ic: (sanct(ic, 32, 46, 0.85), g_expand(ic, 32, 32, 26, 0.7))),
   "the Sanctuary shrine with four blue arrows pushing outward (bigger healing zones)"),
 R("Priest.b3.r1b", "damage", D("Smite", lambda ic: (wand(ic, 8, 56, 26, 30), beam(ic, 30, 26, 56, 10, 2.4, pal="holy"), g_up(ic, 50, 50, 1.0, "damage"))),
   "the star wand firing a gold bolt + an orange up arrow (wand bolts deal more, reach farther)"),
 R("Priest.b3.r2.free", "ability", Reuse(CLS, "Sanctuary"), "REUSED ability icon Priest/Sanctuary.png"),
 R("Priest.b3.r2a", "ability", D("SanctDuration", lambda ic: (sanct(ic, 26, 46), g_hourglass(ic, 51, 48, 1.1))),
   "the Sanctuary shrine + a blue hourglass (lasts longer)"),
 R("Priest.b3.r2b", "health", D("SanctPower", lambda ic: (sanct(ic, 26, 46), g_heart(ic, 50, 46, 1.2))),
   "the Sanctuary shrine + a red heart with a plus (heals more)"),
 R("Priest.b3.r3a", "health", D("Consecrate", lambda ic: (sanct(ic, 26, 50, 0.8), g_mob(ic, 44, 22, 1.0), g_down(ic, 50, 50, 0.9, "health"))),
   "a mob standing in the shrine's light + a red down arrow (enemies inside deal less)"),
 R("Priest.b3.r3b", "speed", D("Pilgrim", lambda ic: (sanct(ic, 32, 48, 0.8), g_speed(ic, 2, 22, 0.9), g_wing(ic, 48, 50, 0.9))),
   "the shrine with teal speed lines + a wing (allies in your zones move faster)"),
 R("Priest.b3.r3c", "ability", D("SanctFollow", lambda ic: (sanct(ic, 30, 46, 0.85), g_ally(ic, 50, 22, 0.8, G), arrow(ic, 50, 48, 0.8, "ability", ang=-30))),
   "the shrine moving after its Priest (a blue follow arrow)"),
 R("Priest.b3.r4a", "health", D("SanctChain", lambda ic: (sanct(ic, 32, 50, 0.95), heal(ic, 32, 24, 0.45), [g_ally(ic, x_, 44, 0.5, "cream") for x_ in (18, 46)],
                                                         g_zap(ic, 32, 8, 0.6, "health"))),
   "a heal cross inside the shrine spreading to everyone inside"),
 R("Priest.b3.r4b", "resource", D("SanctMana", lambda ic: (sanct(ic, 26, 48, 0.9), g_crystal(ic, 48, 46, 0.9), g_plus(ic, 52, 18, 0.75, "resource"))),
   "the shrine + a mana crystal and plus (allies inside refill Mana faster)"),
 R("Priest.b3.r4c", "ward", D("SanctWard", lambda ic: (sanct(ic, 26, 48, 0.9), g_ward(ic, 49, 46, 1.1))),
   "the shrine + a white ward shield (everyone inside keeps a ward when it ends)"),
 R("Priest.b3.r5a", "resource", D("SanctEfficiency", lambda ic: (sanct(ic, 26, 48, 0.9), g_crystal(ic, 47, 46, 1.0), g_down(ic, 56, 26, 0.7, "resource"))),
   "the shrine + a mana crystal with a violet down arrow (costs less Mana)"),
 R("Priest.b3.r5b", "damage", D("RadiantBeacon", lambda ic: (sanct(ic, 26, 48, 0.9), sword(ic, 40, 56, 56, 30, 2.0), g_up(ic, 52, 14, 0.8, "damage"))),
   "the shrine, a sword + an orange up arrow (allies inside deal more damage)"),
 R("Priest.b3.r6", "health", D("HolyLand", lambda ic: (ic.add(ering(22, 46, 17, 5, 13, 3), "holy", base=0.6, bevel=0, line=True),
                                                      ic.add(ering(42, 46, 17, 5, 13, 3), "holy", base=0.75, bevel=0, line=True),
                                                      sanct(ic, 22, 44, 0.6), sanct(ic, 42, 44, 0.6), g_heart(ic, 32, 18, 1.0))),
   "two Sanctuary shrines whose rings overlap + a heart (capstone: 2 charges; the overlap heals 150%)"),
]
