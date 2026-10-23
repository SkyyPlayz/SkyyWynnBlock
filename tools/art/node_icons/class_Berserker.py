"""Berserker class tree node icons (38: 33 new + 5 reused ability icons) - DRAFT v1. Runner: tools/art/make_class_node_icons.py.
Class colour blood red #d9443f. Subjects echo the approved ability icons: Enrage = the horned bull skull, Blood Frenzy = three red claw
slashes, Warlord's Banner = the dark war banner with crossed axes, Whirlwind = the double axe in spin arcs, Earthsplitter = an axe in cracked ground."""
from node_icons.class_kit import *

CLS = "Berserker"
G = C(CLS)


def enrage(ic, cx=28, cy=32, s=1.15):
    bull_skull(ic, cx, cy, s)


def frenzy(ic, cx=28, cy=30, s=1.0):
    claws(ic, cx, cy, s)


def wbanner(ic, x=14, top=7, s=1.0):
    banner(ic, x, top, s, cloth="shadow", trim=G, emblem=crossed_axes_emblem)


def whirlwind(ic, cx=28, cy=30, s=1.0):
    whirl(ic, cx, cy, 21 * s, G, w=3.0 * s)
    axe(ic, cx - 9 * s, cy + 14 * s, cx + 5 * s, cy - 8 * s, 0.85 * s, double=True)


def splitter(ic, s=1.0):
    ground(ic, 46)
    axe(ic, 46, 8, 30, 40, 1.0)


ROWS = [
 # ---------------------------------------------------------------- Bloodlust
 R("Berserker.b1.r1.free", "ability", Reuse(CLS, "Enrage"), "REUSED ability icon Berserker/Enrage.png"),
 R("Berserker.b1.r1a", "health", D("EnrageLeech", lambda ic: (enrage(ic), g_leech(ic, 49, 49, 1.1))),
   "the Enrage bull skull + a blood drop into a heart (heal from damage dealt)"),
 R("Berserker.b1.r1b", "damage", D("Adrenaline", lambda ic: (axe(ic, 10, 56, 32, 22, 1.2), g_lowhp(ic, 49, 46, 1.05), g_up(ic, 50, 16, 0.85, "damage"))),
   "an axe, a half-drained heart (below 60% Health) + an orange up arrow (more damage)"),
 R("Berserker.b1.r2.free", "ability", Reuse(CLS, "BloodFrenzy"), "REUSED ability icon Berserker/BloodFrenzy.png"),
 R("Berserker.b1.r2a", "ability", D("FrenzyDuration", lambda ic: (frenzy(ic), g_hourglass(ic, 50, 48, 1.15))),
   "the three Blood Frenzy claw slashes + a blue hourglass (lasts longer)"),
 R("Berserker.b1.r2b", "health", D("FrenzyLeech", lambda ic: (frenzy(ic, 26, 30), g_leech(ic, 49, 49, 1.1), g_plus(ic, 52, 16, 0.75, "health"))),
   "the claw slashes + a blood drop into a heart and plus (more Frenzy leech)"),
 R("Berserker.b1.r3a", "damage", D("Echo", lambda ic: (axe(ic, 8, 56, 28, 24, 1.15), g_echo(ic, 46, 30, 1.2), g_plus(ic, 50, 52, 0.85, "damage"))),
   "an axe swing with two echo arcs + an orange plus (every 5th hit repeats)"),
 R("Berserker.b1.r3b", "health", D("Thirst", lambda ic: (g_skull(ic, 26, 28, 2.0), g_heart(ic, 48, 48, 1.3))),
   "a skull (a kill) + a red heart with a plus (kills heal you)"),
 R("Berserker.b1.r4a", "damage", D("EnragePower", lambda ic: (enrage(ic), g_up(ic, 50, 50, 1.1, "damage"))),
   "the Enrage bull skull + an orange up arrow (more melee damage while Enraged)"),
 R("Berserker.b1.r4b", "speed", D("FrenzyHaste", lambda ic: (frenzy(ic, 32, 28), g_speed(ic, 4, 40, 1.0), g_wing(ic, 46, 50, 1.0))),
   "the claw slashes with teal speed lines + a teal wing (faster during Frenzy)"),
 R("Berserker.b1.r5a", "health", D("RedMist", lambda ic: (cloud(ic, 30, 24, 1.3, pal="blood", base=0.5), g_lowhp(ic, 22, 48, 0.9), g_leech(ic, 49, 48, 1.0))),
   "a red mist cloud over a nearly empty heart + a leech drop (stronger leech at low Health)"),
 R("Berserker.b1.r5b", "ability", D("FrenzyRefresh", lambda ic: (frenzy(ic, 24, 28, 0.95), g_skull(ic, 50, 16, 0.9), g_repeat(ic, 49, 49, 1.15))),
   "the claw slashes, a skull (a kill) + a blue refresh arrow (kills refresh Frenzy)"),
 R("Berserker.b1.r6", "ward", D("CrimsonEternal", lambda ic: (burst(ic, 30, 30, 30, 14, 12, G, base=0.55), frenzy(ic, 30, 30, 1.0), g_ward(ic, 50, 49, 1.0),
                                                             g_drop(ic, 12, 50, 0.9))),
   "the claw slashes on a blood-red burst + a white ward and a blood drop (capstone: stacks never fade, overheal becomes a ward)"),
 # ---------------------------------------------------------------- Warlord's Banner
 R("Berserker.b2.r1a", "damage", D("RallyCry", lambda ic: (enrage(ic, 26, 26, 1.0), g_party(ic, 46, 48, 0.9), g_up(ic, 18, 52, 0.8, "damage"))),
   "the Enrage skull above the party + an orange up arrow (allies deal more damage)"),
 R("Berserker.b2.r1b", "ability", D("EnrageRadius", lambda ic: (enrage(ic, 32, 33, 0.95), g_expand(ic, 32, 32, 25, 0.72))),
   "the Enrage skull with four blue arrows pushing outward (bigger ally radius)"),
 R("Berserker.b2.r2.free", "ability", Reuse(CLS, "WarlordsBanner"), "REUSED ability icon Berserker/WarlordsBanner.png"),
 R("Berserker.b2.r2a", "ability", D("BannerDuration", lambda ic: (wbanner(ic), g_hourglass(ic, 50, 48, 1.15))),
   "the dark war banner + a blue hourglass (lasts longer)"),
 R("Berserker.b2.r2b", "damage", D("BannerPower", lambda ic: (wbanner(ic), g_up(ic, 50, 50, 1.1, "damage"))),
   "the dark war banner + an orange up arrow (banner gives more damage)"),
 R("Berserker.b2.r3a", "speed", D("BannerHaste", lambda ic: (wbanner(ic, 18), g_speed(ic, 2, 26, 1.0), g_wing(ic, 46, 50, 1.0))),
   "the war banner with teal speed lines + a teal wing (move speed inside)"),
 R("Berserker.b2.r3b", "ward", D("BannerWard", lambda ic: (wbanner(ic), g_ward(ic, 49, 47, 1.15))),
   "the war banner + a white ward shield (shields allies)"),
 R("Berserker.b2.r4a", "ability", D("BannerRadius", lambda ic: (wbanner(ic, 20, 9, 0.85), g_expand(ic, 32, 34, 25, 0.72))),
   "the war banner with four blue arrows pushing outward (bigger radius)"),
 R("Berserker.b2.r4b", "ability", D("BannerEcho", lambda ic: (wbanner(ic, 12), g_ring(ic, 26, 32, 25, 2.4), g_repeat(ic, 49, 49, 1.15))),
   "the war banner in a blue pulse ring + a repeat arrow (re-pulses its buff)"),
 R("Berserker.b2.r5a", "health", D("BloodPrice", lambda ic: (wbanner(ic, 10, 5, 0.85), g_party(ic, 40, 40, 0.9), g_leech(ic, 52, 22, 0.9))),
   "the war banner over the party + a leech drop (allies leech)"),
 R("Berserker.b2.r5b", "damage", D("BannerFury", lambda ic: (wbanner(ic), g_up(ic, 46, 50, 0.95, "damage"), g_up(ic, 56, 44, 0.7, "damage"))),
   "the war banner + two orange up arrows (a bigger damage buff)"),
 R("Berserker.b2.r6", "ability", D("WarlordsDomain", lambda ic: (g_ring(ic, 32, 34, 28, 2.4, "ability", 0.5), wbanner(ic, 18, 6, 0.85),
                                                               g_ally(ic, 18, 48, 1.0, G), g_speed(ic, 2, 44, 0.7))),
   "the war banner marching behind its Berserker inside a blue domain ring (capstone: the banner follows you)"),
 # ---------------------------------------------------------------- Warpath
 R("Berserker.b3.r1a", "damage", D("Cleave", lambda ic: (axe(ic, 8, 56, 28, 26, 1.1), g_mob(ic, 44, 18, 0.9), g_mob(ic, 50, 42, 0.9),
                                                        arcp(ic, 30, 30, 18, -60, 40, 2.6, acc("damage"), line=True))),
   "an axe with an orange cleave arc through two mobs (hits splash to another enemy)"),
 R("Berserker.b3.r1b", "damage", D("MeleePower", lambda ic: (axe(ic, 12, 54, 32, 22, 1.25, double=True), g_up(ic, 50, 50, 1.1, "damage"))),
   "a double axe + an orange up arrow (more melee damage)"),
 R("Berserker.b3.r2.free", "ability", Reuse(CLS, "Whirlwind"), "REUSED ability icon Berserker/Whirlwind.png"),
 R("Berserker.b3.r2a", "ability", D("WhirlRadius", lambda ic: (whirlwind(ic, 32, 32, 0.9), g_expand(ic, 32, 32, 27, 0.68))),
   "the spinning double axe with four blue arrows pushing outward (bigger radius)"),
 R("Berserker.b3.r2b", "ability", D("WhirlSplit", lambda ic: (whirlwind(ic, 26, 28, 0.95), g_fork(ic, 48, 48, 1.1))),
   "the spinning double axe + a blue fork (each pulse hits one more enemy)"),
 R("Berserker.b3.r3a", "damage", D("WhirlHaste", lambda ic: (whirlwind(ic, 26, 28, 1.0), arcp(ic, 26, 28, 27, 300, 390, 2.6, acc("damage"), line=True),
                                                            g_up(ic, 50, 50, 1.0, "damage"))),
   "the spinning double axe with an extra orange spin arc + an up arrow (spins harder: more damage)"),
 R("Berserker.b3.r3b", "control", D("WhirlSlow", lambda ic: (whirlwind(ic, 26, 28, 1.0), g_snail(ic, 47, 51, 1.0))),
   "the spinning double axe + a yellow snail (hits slow)"),
 R("Berserker.b3.r4a", "damage", D("Bleed", lambda ic: (whirlwind(ic, 26, 26, 0.95), g_drop(ic, 44, 46, 1.0), g_drop(ic, 54, 54, 0.7),
                                                       g_clock(ic, 16, 52, 0.75, "damage"))),
   "the spinning axe dripping blood + a ticking clock (enemies bleed over time)"),
 R("Berserker.b3.r4b", "ability", D("WhirlDuration", lambda ic: (whirlwind(ic, 26, 28, 1.0), g_hourglass(ic, 50, 48, 1.15))),
   "the spinning double axe + a blue hourglass (spins longer)"),
 R("Berserker.b3.r5.free", "ability", Reuse(CLS, "Earthsplitter"), "REUSED ability icon Berserker/Earthsplitter.png"),
 R("Berserker.b3.r5a", "control", D("SplitterLaunch", lambda ic: (splitter(ic), g_mob(ic, 14, 18, 0.85), arrow(ic, 14, 34, 0.8, "control", ang=-90))),
   "the axe split into cracked ground launching a mob upward (yellow up arrow)"),
 R("Berserker.b3.r5b", "health", D("SplitterLeech", lambda ic: (splitter(ic), g_leech(ic, 16, 22, 1.05))),
   "the axe in cracked ground + a blood drop into a heart (hits heal you)"),
 R("Berserker.b3.r6", "ability", D("EndlessFury", lambda ic: (whirl(ic, 30, 30, 26, G, w=3.2, n=4), whirlwind(ic, 30, 30, 0.85), g_speed(ic, 2, 50, 0.8),
                                                           g_repeat(ic, 52, 52, 0.85))),
   "a double ring of spin arcs round the axe, speed lines + a toggle arrow (capstone: Whirlwind becomes a moving toggle)"),
]
