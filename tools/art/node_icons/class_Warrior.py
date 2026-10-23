"""Warrior class tree node icons (37: 32 new + 5 reused ability icons) - DRAFT v1. Runner: tools/art/make_class_node_icons.py.
Class colour amber-gold #e0b060 (shield trim, banner, crest). Subjects echo the approved ability icons: Rallying Guard = the red banner,
Challenge = the tall red bulwark shield, Guardian's Oath = the great helm, Shield Shockwave = the round shield, Iron Chain = the hooked chain."""
from node_icons.class_kit import *

CLS = "Warrior"
G = C(CLS)


def rally(ic, x=14, top=8, s=1.0):
    banner(ic, x, top, s, cloth="cls_Berserker", trim=G, emblem=lambda ic_, cx, cy, ss: heater(ic_, cx, cy, ss, field="steel", trim=G))


def chal(ic, cx=28, cy=30, s=1.15):
    tower_shield(ic, cx, cy, s, field="cls_Berserker", trim=G)


def oath(ic, cx=28, cy=32, s=1.2):
    helm(ic, cx, cy, s, crest=G)


def wave_shield(ic, cx=28, cy=30, r=17, rings=True):
    if rings:
        shock_rings(ic, cx, cy, 0.9, "control")
    round_shield(ic, cx, cy, r, rim=G)


def ichain(ic, x0=8, y0=52, x1=38, y1=22, n=5, s=1.0):
    chain(ic, x0, y0, x1, y1, n, s)


ROWS = [
 # ---------------------------------------------------------------- Bulwark
 R("Warrior.b1.r1.free", "ability", Reuse(CLS, "RallyingGuard"), "REUSED ability icon Warrior/RallyingGuard.png"),
 R("Warrior.b1.r1a", "health", D("IronSkin", lambda ic: (heater(ic, 27, 30, 1.7, field="steel", trim=G),
                                                        sword(ic, 56, 6, 38, 22, 2.4), g_down(ic, 50, 50, 1.0, "health"))),
   "a steel heater shield turning a sword aside + a red down arrow (less melee damage taken)"),
 R("Warrior.b1.r1b", "health", D("LastStand", lambda ic: (g_heart(ic, 28, 28, 2.6, plus_=False), heater(ic, 28, 34, 0.75, field="steel", trim=G),
                                                         g_plus(ic, 50, 50, 1.0, "health"))),
   "a big red heart with the Warrior's shield on it + a red plus (+ max Health)"),
 R("Warrior.b1.r2.free", "ability", Reuse(CLS, "BulwarkStance"), "REUSED ability icon Warrior/BulwarkStance.png (= Challenge)"),
 R("Warrior.b1.r2a", "ability", D("ChallengeDuration", lambda ic: (chal(ic), g_hourglass(ic, 49, 48, 1.15))),
   "the red bulwark shield (Challenge) + a blue hourglass (lasts longer)"),
 R("Warrior.b1.r2b", "ward", D("ChallengeWard", lambda ic: (chal(ic), g_ward(ic, 49, 47, 1.15))),
   "the red bulwark shield (Challenge) + a white ward shield (shields you)"),
 R("Warrior.b1.r3a", "control", D("Knockback", lambda ic: (sword(ic, 8, 56, 34, 22, 2.8), g_mob(ic, 46, 24, 1.0), g_push(ic, 46, 48, 1.0, ang=-20))),
   "a sword striking a mob that is pushed away by a yellow knockback arrow"),
 R("Warrior.b1.r3b", "health", D("StoneGuard", lambda ic: (heater(ic, 28, 30, 1.7, field="stone", trim=G),
                                                          arrow_shaft(ic, 58, 8, 40, 22, 1.0), g_down(ic, 50, 50, 1.0, "health"))),
   "a stone-faced shield catching an arrow + a red down arrow (less ranged damage taken)"),
 R("Warrior.b1.r4a", "control", D("BlockSlow", lambda ic: (heater(ic, 27, 28, 1.7, field="steel", trim=G), g_snail(ic, 47, 50, 1.0))),
   "a raised shield + a yellow snail (blocked enemies slowed)"),
 R("Warrior.b1.r4b", "health", D("BlockLeech", lambda ic: (heater(ic, 27, 28, 1.7, field="steel", trim=G), g_leech(ic, 48, 48, 1.1))),
   "a raised shield + a blood drop into a heart (blocking heals)"),
 R("Warrior.b1.r5.free", "ability", Reuse(CLS, "Unbreakable"), "REUSED ability icon Warrior/Unbreakable.png (= Guardian's Oath)"),
 R("Warrior.b1.r5a", "ability", D("OathDuration", lambda ic: (oath(ic), g_hourglass(ic, 50, 48, 1.15))),
   "the great helm (Guardian's Oath) + a blue hourglass (lasts longer)"),
 R("Warrior.b1.r5b", "health", D("Anchor", lambda ic: (anchor(ic, 28, 32, 1.35), g_down(ic, 50, 50, 1.0, "health"))),
   "a steel anchor (stand still) + a red down arrow (less damage taken)"),
 R("Warrior.b1.r6", "ward", D("AegisEternal", lambda ic: (burst(ic, 30, 30, 30, 14, 12, G, base=0.62), chal(ic, 30, 28, 1.05),
                                                         g_party(ic, 50, 50, 0.85), g_ward(ic, 12, 52, 0.85))),
   "the bulwark shield on a gold burst, the party below + a white ward (capstone: Challenge holds, allies protected)"),
 # ---------------------------------------------------------------- Shockwave
 R("Warrior.b2.r1a", "ability", D("RallyRadius", lambda ic: (rally(ic, 20, 8, 0.9), g_expand(ic, 32, 34, 25, 0.75))),
   "the red rally banner with four blue arrows pushing outward (bigger radius)"),
 R("Warrior.b2.r1b", "ward", D("RallyPower", lambda ic: (rally(ic, 14, 6, 0.95), g_ward(ic, 49, 46, 1.1), g_plus(ic, 52, 22, 0.75, "ward"))),
   "the red rally banner + a white ward shield and plus (stronger ward)"),
 R("Warrior.b2.r2.free", "ability", Reuse(CLS, "ShieldShockwave"), "REUSED ability icon Warrior/ShieldShockwave.png"),
 R("Warrior.b2.r2a", "control", D("ShockKnockback", lambda ic: (wave_shield(ic, 26, 30), g_push(ic, 50, 50, 1.0, ang=-30))),
   "the round shield with yellow shock arcs + a knockback arrow"),
 R("Warrior.b2.r2b", "control", D("Concussion", lambda ic: (wave_shield(ic, 26, 32), g_stars(ic, 48, 16, 1.0))),
   "the round shield with shock arcs + three yellow stun stars"),
 R("Warrior.b2.r3a", "control", D("ShockSlow", lambda ic: (wave_shield(ic, 26, 30), g_snail(ic, 47, 51, 1.0))),
   "the round shield with shock arcs + a yellow snail (slows)"),
 R("Warrior.b2.r3b", "ability", D("ShockChain", lambda ic: (wave_shield(ic, 24, 28, 15), g_zap(ic, 46, 46, 1.2))),
   "the round shield + a blue bolt arcing between two enemies (chains)"),
 R("Warrior.b2.r4a", "control", D("ShockStun", lambda ic: (wave_shield(ic, 26, 32, 16), g_stars(ic, 48, 14, 0.85), g_hourglass(ic, 51, 50, 0.95, "control"))),
   "the round shield + stun stars + a yellow hourglass (longer stun)"),
 R("Warrior.b2.r4b", "damage", D("ShockPower", lambda ic: (wave_shield(ic, 26, 30), g_up(ic, 50, 50, 1.1, "damage"))),
   "the round shield with shock arcs + an orange up arrow (more damage)"),
 R("Warrior.b2.r5a", "ability", D("Fissure", lambda ic: (ground(ic, 46), round_shield(ic, 32, 30, 14, rim=G), g_expand(ic, 32, 30, 24, 0.72))),
   "the round shield slammed on cracked ground + four blue arrows (bigger radius)"),
 R("Warrior.b2.r5b", "damage", D("Tremor", lambda ic: (ground(ic, 48), g_mob(ic, 30, 30, 1.25),
                                                      [arcp(ic, 30, 54, R_, 230, 310, 2.4, acc("damage"), base=b_, line=True) for R_, b_ in ((18, 0.8), (26, 0.6))],
                                                      g_clock(ic, 51, 14, 0.8, "damage"))),
   "a mob on cracked ground with orange tremor waves + a ticking clock (damage over time)"),
 R("Warrior.b2.r6", "ability", D("Rumble", lambda ic: (shock_rings(ic, 28, 34, 1.0, "control", 2), round_shield(ic, 28, 34, 16, rim=G),
                                                      chal(ic, 50, 16, 0.5), g_repeat(ic, 50, 50, 1.2))),
   "the round shield sending shockwaves, the small Challenge shield + a repeat arrow (fires by itself while Challenge holds)"),
 # ---------------------------------------------------------------- Iron Chain
 R("Warrior.b3.r1a", "ward", D("RallyWard", lambda ic: (rally(ic, 10, 6, 0.8), g_party(ic, 38, 38, 1.1), g_ward(ic, 52, 52, 0.9))),
   "the rally banner over the party + a white ward (allies shielded too)"),
 R("Warrior.b3.r1b", "damage", D("ChainMark", lambda ic: (ichain(ic, 6, 54, 26, 34, 3), g_mob(ic, 40, 24, 1.3), g_up(ic, 50, 50, 1.0, "damage"))),
   "an iron chain hooked on a mob + an orange up arrow (taunted enemies take more damage)"),
 R("Warrior.b3.r2.free", "ability", Reuse(CLS, "IronChain"), "REUSED ability icon Warrior/IronChain.png"),
 R("Warrior.b3.r2a", "control", D("ChainPull", lambda ic: (ichain(ic, 10, 50, 34, 24, 4), g_pull(ic, 46, 50, 1.0, ang=200))),
   "the hooked iron chain + a yellow pull arrow (drags enemies closer)"),
 R("Warrior.b3.r3a", "ability", D("ChainBind", lambda ic: (ichain(ic, 6, 56, 28, 32, 4), g_mob(ic, 44, 18, 0.9), g_mob(ic, 50, 40, 0.9),
                                                          g_plus(ic, 26, 14, 0.8, "ability"))),
   "the iron chain binding two mobs + a blue plus (binds 1 more enemy)"),
 R("Warrior.b3.r3b", "health", D("ChainLeech", lambda ic: (ichain(ic, 8, 50, 34, 22, 4), g_leech(ic, 48, 48, 1.1))),
   "the iron chain + a blood drop into a heart (chain hits heal you)"),
 R("Warrior.b3.r4a", "control", D("ChainSlow", lambda ic: (ichain(ic, 8, 48, 34, 20, 4), g_snail(ic, 47, 51, 1.0))),
   "the iron chain + a yellow snail (chained enemies slower)"),
 R("Warrior.b3.r4b", "ward", D("PartyWard", lambda ic: (g_party(ic, 28, 30, 1.6), g_ward(ic, 50, 48, 1.1), g_plus(ic, 52, 16, 0.7, "ward"))),
   "the party + a white ward shield and plus (party wards stronger)"),
 R("Warrior.b3.r5a", "damage", D("HeavyLinks", lambda ic: (chain(ic, 8, 48, 36, 20, 4, 1.35, hook=False), g_up(ic, 50, 50, 1.1, "damage"))),
   "thick heavy chain links + an orange up arrow (more chain damage)"),
 R("Warrior.b3.r5b", "control", D("ChainStun", lambda ic: (ichain(ic, 6, 52, 30, 28, 4), g_stars(ic, 46, 16, 0.85), g_hourglass(ic, 51, 50, 0.95, "control"))),
   "the iron chain + stun stars + a yellow hourglass (longer stun)"),
 R("Warrior.b3.r6", "control", D("WardensGrip", lambda ic: ([chain(ic, 32, 32, x_, y_, 3, 0.7, hook=False) for x_, y_ in ((14, 14), (50, 14), (14, 50), (50, 50))],
                                                           [g_mob(ic, x_, y_, 0.62) for x_, y_ in ((10, 10), (54, 10), (10, 54), (54, 54))],
                                                           helm(ic, 32, 34, 0.7, crest=G))),
   "the great helm in the centre with chains yanking four mobs in from every side (capstone: pull all, root, ward)"),
]
