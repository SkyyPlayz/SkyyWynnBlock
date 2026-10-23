"""Spellblade class tree node icons (38: 33 new + 5 reused ability icons) - DRAFT v1. Runner: tools/art/make_class_node_icons.py.
Class colour teal #6fd0d8. Subjects echo the approved ability icons: Arcane Breach = a teal crescent round a violet orb, Rift Cleave =
the teal crescent slash, Shattering Arc = the arc with flying shards, Sunder = a split armour plate, Elemental Imbue = a sword wrapped in a
fire + frost ribbon, Momentum = teal chevrons."""
from node_icons.class_kit import *

CLS = "Spellblade"
G = C(CLS)


def breach(ic, cx=28, cy=30, s=1.0):
    crescent(ic, cx, cy, 20 * s, G, ang=20, thick=0.5)
    ic.add(circle(cx + 3 * s, cy, 8 * s), "arcane", mode="sphere", base=0.75, line=True)


def rift(ic, cx=28, cy=30, s=1.0):
    crescent(ic, cx, cy, 22 * s, "rift", ang=-30, thick=0.36, base=0.72)
    ic.add(poly([(cx - 6 * s, cy + 20 * s), (cx - 2 * s, cy + 8 * s), (cx + 1 * s, cy + 20 * s)]), G, base=0.9, line=True)


def sarc(ic, cx=28, cy=30, s=1.0):
    arcp(ic, cx + 10 * s, cy + 10 * s, 24 * s, 180, 270, 5 * s, G, base=0.72, line=True, cast=True)
    for (dx, dy, r) in ((8, -10, 3.6), (14, -2, 3.0), (2, -16, 2.6)):
        ic.add(poly([(cx + dx * s, cy + (dy - r) * s), (cx + (dx + r) * s, cy + dy * s), (cx + dx * s, cy + (dy + r * 1.4) * s), (cx + (dx - r * 0.8) * s, cy + dy * s)]),
               "ice", base=0.8, line=True)


def sunder(ic, cx=28, cy=30, s=1.0):
    for sg, dx in ((-1, -2.5), (1, 2.5)):
        half_ = poly([(cx + dx * s, cy - 16 * s), (cx + (dx + 13 * sg) * s, cy - 12 * s), (cx + (dx + 12 * sg) * s, cy + 6 * s), (cx + dx * s, cy + 17 * s),
                      (cx + (dx + 3 * sg) * s, cy + 4 * s), (cx + (dx - 2 * sg) * s, cy - 3 * s)])
        ic.add(half_, "steel", base=0.6, grad=0.6, bevel=1.0, line=True)
    ic.add(poly([(cx - 1.5 * s, cy - 16 * s), (cx + 1.5 * s, cy - 16 * s), (cx + 2 * s, cy - 3 * s), (cx - 1 * s, cy + 4 * s), (cx + 1 * s, cy + 17 * s),
                 (cx - 2 * s, cy + 4 * s), (cx - 3 * s, cy - 3 * s)]), G, base=0.85, bevel=0, cast=False)


def imbue(ic, x0=10, y0=54, x1=42, y1=14):
    sword(ic, x0, y0, x1, y1, 3.0)
    for k in range(5):
        t = 0.3 + k * 0.14
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        ic.add(rot_ellipse(x, y, 7, 2.2, 45 if k % 2 else -20), "flame" if k % 2 else "ice", base=0.75, bevel=0.5, line=True)


def momentum(ic, cx, cy, s=1.0, cat=None):
    pal = acc(cat) if cat else G
    for k in range(3):
        x = cx + (k - 1) * 7 * s
        ic.add(poly([(x - 3 * s, cy - 8 * s), (x + 2 * s, cy - 8 * s), (x + 7 * s, cy), (x + 2 * s, cy + 8 * s), (x - 3 * s, cy + 8 * s), (x + 2 * s, cy)]), pal,
               base=0.6 + 0.12 * k, grad=0.4, bevel=0.7, line=True)


ROWS = [
 # ---------------------------------------------------------------- Rift Cleave
 R("Spellblade.b1.r1.free", "ability", Reuse(CLS, "ArcaneBreach"), "REUSED ability icon Spellblade/ArcaneBreach.png"),
 R("Spellblade.b1.r1a", "damage", D("BreachPower", lambda ic: (breach(ic), g_up(ic, 50, 50, 1.1, "damage"))),
   "the Arcane Breach crescent and orb + an orange up arrow (more spell damage)"),
 R("Spellblade.b1.r1b", "ability", D("BreachRadius", lambda ic: (breach(ic, 30, 32, 0.85), g_expand(ic, 32, 32, 26, 0.7))),
   "the Arcane Breach crescent with four blue arrows pushing outward (bigger blast)"),
 R("Spellblade.b1.r2.free", "ability", Reuse(CLS, "RiftCleave"), "REUSED ability icon Spellblade/RiftCleave.png"),
 R("Spellblade.b1.r2a", "ability", D("RiftWidth", lambda ic: (rift(ic, 30, 30, 0.9), arrow(ic, 8, 30, 0.75, "ability", ang=180), arrow(ic, 56, 30, 0.75, "ability", ang=0))),
   "the teal rift crescent with blue arrows out to both sides (a wider arc)"),
 R("Spellblade.b1.r2b", "ability", D("RiftChain", lambda ic: (rift(ic, 26, 28), g_zap(ic, 46, 48, 1.15))),
   "the rift crescent + a blue bolt between two enemies (arcs to one more)"),
 R("Spellblade.b1.r3a", "control", D("RiftSlow", lambda ic: (rift(ic, 26, 28), g_snail(ic, 47, 51, 1.0))),
   "the rift crescent + a yellow snail (rift hits slow)"),
 R("Spellblade.b1.r3b", "damage", D("RiftPower", lambda ic: (rift(ic, 26, 28), g_up(ic, 50, 50, 1.1, "damage"))),
   "the rift crescent + an orange up arrow (more rift damage)"),
 R("Spellblade.b1.r4a", "control", D("RiftSlowTime", lambda ic: (rift(ic, 26, 28), g_snail(ic, 46, 16, 0.75), g_hourglass(ic, 51, 50, 0.95, "control"))),
   "the rift crescent, a small snail + a yellow hourglass (the slow lasts longer)"),
 R("Spellblade.b1.r4b", "resource", D("RiftEfficiency", lambda ic: (rift(ic, 26, 28), g_crystal(ic, 47, 46, 1.0), g_down(ic, 56, 26, 0.7, "resource"))),
   "the rift crescent + a mana crystal with a violet down arrow (costs less Mana)"),
 R("Spellblade.b1.r5a", "control", D("RiftPush", lambda ic: (rift(ic, 24, 30), g_push(ic, 50, 48, 1.0, ang=-20))),
   "the rift crescent + a yellow knockback arrow (rifts push enemies)"),
 R("Spellblade.b1.r5b", "resource", D("Riptide", lambda ic: (rift(ic, 26, 26, 0.95), momentum(ic, 44, 50, 0.85), g_plus(ic, 54, 16, 0.75, "resource"))),
   "the rift crescent + teal Momentum chevrons and a plus (+ Momentum per cast)"),
 R("Spellblade.b1.r6", "ability", D("Riftmaw", lambda ic: (crescent(ic, 38, 34, 20, "rift", ang=-30, thick=0.36, base=0.5), rift(ic, 26, 26, 0.9),
                                                          momentum(ic, 46, 52, 0.7))),
   "two rift crescents, one right behind the other + Momentum chevrons (capstone: a second rift every cast)"),
 # ---------------------------------------------------------------- Sunder
 R("Spellblade.b2.r1a", "damage", D("BreachVuln", lambda ic: (breach(ic, 24, 28, 0.9), g_crack(ic, 48, 46, 1.1))),
   "the Arcane Breach crescent + a cracked armour plate (enemies take more from everything)"),
 R("Spellblade.b2.r1b", "ability", D("BreachVulnTime", lambda ic: (breach(ic, 24, 26, 0.9), g_crack(ic, 48, 20, 0.7), g_hourglass(ic, 50, 49, 1.0))),
   "the Breach crescent, a small cracked plate + a blue hourglass (vulnerability lasts longer)"),
 R("Spellblade.b2.r2.free", "ability", Reuse(CLS, "ShatteringArc"), "REUSED ability icon Spellblade/ShatteringArc.png"),
 R("Spellblade.b2.r2a", "damage", D("ArcVuln", lambda ic: (sarc(ic, 24, 26), g_crack(ic, 48, 46, 1.1))),
   "the Shattering Arc with its shards + a cracked armour plate (more vulnerability)"),
 R("Spellblade.b2.r2b", "ability", D("ArcDuration", lambda ic: (sarc(ic, 24, 26), g_hourglass(ic, 50, 48, 1.15))),
   "the Shattering Arc + a blue hourglass (its debuff lasts longer)"),
 R("Spellblade.b2.r3a", "health", D("Weaken", lambda ic: (g_mob(ic, 26, 26, 1.4), sword(ic, 40, 40, 54, 54, 2.2), g_down(ic, 18, 50, 0.9, "health"))),
   "a debuffed mob with a dulled blade + a red down arrow (Breached / Weakened enemies hit you for less)"),
 R("Spellblade.b2.r3b", "health", D("DebuffLeech", lambda ic: (g_crack(ic, 26, 28, 1.5), g_leech(ic, 49, 49, 1.1))),
   "a cracked armour plate (a debuffed enemy) + a leech drop (hitting it heals you)"),
 R("Spellblade.b2.r4a", "ability", D("SpreadDebuff", lambda ic: (g_skull(ic, 22, 26, 1.4), g_crack(ic, 46, 44, 0.85), g_fork(ic, 36, 20, 0.9))),
   "a skull (a death) forking its cracked-plate debuff on to the next enemy"),
 R("Spellblade.b2.r4b", "ability", D("DebuffDuration", lambda ic: (sunder(ic, 22, 30, 0.85), sarc(ic, 34, 14, 0.5), g_hourglass(ic, 50, 48, 1.15))),
   "the split plate (Sunder), a small arc + a blue hourglass (all three debuffs last longer)"),
 R("Spellblade.b2.r5.free", "ability", Reuse(CLS, "Sunder"), "REUSED ability icon Spellblade/Sunder.png"),
 R("Spellblade.b2.r5a", "damage", D("SunderShred", lambda ic: (sunder(ic, 26, 30, 1.05), g_down(ic, 50, 50, 1.0, "damage"))),
   "the split armour plate (Sunder) + an orange down arrow (shreds enemy defence)"),
 R("Spellblade.b2.r5b", "ability", D("SunderDuration", lambda ic: (sunder(ic, 26, 30, 1.05), g_hourglass(ic, 50, 48, 1.15))),
   "the split armour plate + a blue hourglass (Sunder lasts longer)"),
 R("Spellblade.b2.r6", "damage", D("Fracture", lambda ic: (burst(ic, 30, 30, 28, 12, 10, G, base=0.5), sunder(ic, 30, 30, 0.95), g_clock(ic, 50, 50, 0.85))),
   "the split plate on a teal shatter burst + a cooldown clock (capstone: half cooldown, Arc hits Sundered harder)"),
 # ---------------------------------------------------------------- Imbue
 R("Spellblade.b3.r1a", "resource", D("MomentumChance", lambda ic: (sword(ic, 8, 56, 34, 22, 2.8), momentum(ic, 46, 30, 1.0), g_plus(ic, 50, 52, 0.8, "resource"))),
   "a sword hit + teal Momentum chevrons and a plus (hits grant Momentum)"),
 R("Spellblade.b3.r1b", "damage", D("ElementPower", lambda ic: (imbue(ic), g_up(ic, 50, 50, 1.1, "damage"))),
   "the fire + frost wrapped sword + an orange up arrow (more elemental damage)"),
 R("Spellblade.b3.r2.free", "ability", Reuse(CLS, "ElementalImbue"), "REUSED ability icon Spellblade/ElementalImbue.png"),
 R("Spellblade.b3.r2a", "ability", D("ImbueDuration", lambda ic: (imbue(ic), g_hourglass(ic, 50, 48, 1.15))),
   "the imbued sword + a blue hourglass (Imbue lasts longer)"),
 R("Spellblade.b3.r2b", "damage", D("ImbuePower", lambda ic: (imbue(ic, 8, 52, 38, 16), g_plus(ic, 50, 50, 1.0, "damage"), burst(ic, 52, 22, 6, 2.5, 5, "flame", base=0.85, line=True))),
   "the imbued sword, a fire spark + an orange plus (Imbue adds elemental damage)"),
 R("Spellblade.b3.r3a", "resource", D("MomentumRefund", lambda ic: (momentum(ic, 26, 26, 1.2), g_crystal(ic, 46, 46, 1.0), g_repeat(ic, 22, 50, 0.85, "resource"))),
   "Momentum chevrons + a mana crystal with a refund arrow (spending Momentum refunds Mana)"),
 R("Spellblade.b3.r3b", "ability", D("ArcReach", lambda ic: (sarc(ic, 22, 30), arrow(ic, 50, 22, 0.95, "ability", ang=-45), arrow(ic, 50, 48, 0.8, "ability", ang=0))),
   "the Shattering Arc + blue arrows pushing its reach further"),
 R("Spellblade.b3.r4a", "control", D("ImbueSlow", lambda ic: (imbue(ic), g_snail(ic, 47, 51, 1.0))),
   "the imbued sword + a yellow snail (imbued hits slow)"),
 R("Spellblade.b3.r4b", "health", D("ImbueLeech", lambda ic: (imbue(ic), g_leech(ic, 49, 49, 1.1))),
   "the imbued sword + a leech drop (imbued hits heal you)"),
 R("Spellblade.b3.r5a", "damage", D("ArcEcho", lambda ic: (sarc(ic, 22, 26), g_echo(ic, 48, 46, 1.1))),
   "the Shattering Arc + two echo arcs (its hits strike again)"),
 R("Spellblade.b3.r5b", "damage", D("MomentumPower", lambda ic: (momentum(ic, 28, 28, 1.3), sword(ic, 30, 56, 56, 34, 2.2), g_up(ic, 14, 52, 0.85, "damage"))),
   "Momentum chevrons driving a sword + an orange up arrow (Momentum-spent hits deal more)"),
 R("Spellblade.b3.r6", "ability", D("ArcCascade", lambda ic: (g_ring(ic, 32, 32, 28, 2.6, "ability", 0.5), g_ring(ic, 32, 32, 21, 2.2, "ability", 0.7),
                                                             momentum(ic, 32, 32, 1.35))),
   "full Momentum chevrons releasing a blue nova ring (capstone: at 20 Momentum the next ability is free + a nova)"),
]
