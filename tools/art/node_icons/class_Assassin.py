"""Assassin class tree node icons (41: 36 new + 5 reused ability icons) - DRAFT v1. Runner: tools/art/make_class_node_icons.py.
Class colour lilac #b58cff. Subjects echo the approved ability icons: Cloak + First Strike = the beak hood with a face mask (Skyy's
Assassin's-Creed hood), Vanishing Act = a smoke cloud, Shadow Clone = a dark hooded silhouette, God Killer = a crown pierced by a dagger,
Toxin = a green poison flask / cloud; kunai for the thrown hits."""
from node_icons.class_kit import *

CLS = "Assassin"
G = C(CLS)


def cloak(ic, cx=28, cy=30, s=1.05):
    hood(ic, cx, cy, s)


def vanish(ic, cx=28, cy=30, s=1.1):
    cloud(ic, cx, cy, s, pal="smoke", base=0.55)


def godkill(ic, cx=28, cy=34, s=1.0):
    crown(ic, cx, cy, s)
    dagger(ic, cx - 10 * s, cy + 18 * s, cx + 12 * s, cy - 20 * s, 2.4 * s)


def toxin(ic, cx=28, cy=30, s=1.0):
    flask(ic, cx, cy, s * 1.15)


def tcloud(ic, cx=28, cy=30, s=1.0):
    cloud(ic, cx, cy, s * 1.15, pal="poison", base=0.55)


ROWS = [
 # ---------------------------------------------------------------- Shadowstep
 R("Assassin.b1.r1.free", "ability", Reuse(CLS, "CloakFirstStrike"), "REUSED ability icon Assassin/CloakFirstStrike.png"),
 R("Assassin.b1.r1a", "ability", D("CloakDuration", lambda ic: (cloak(ic), g_hourglass(ic, 50, 48, 1.15))),
   "the masked hood (Cloak) + a blue hourglass (lasts longer)"),
 R("Assassin.b1.r1b", "damage", D("Ambush", lambda ic: (cloak(ic, 24, 28, 0.9), dagger(ic, 30, 54, 54, 26, 2.4), g_up(ic, 52, 52, 0.8, "damage"))),
   "the masked hood with a dagger striking + an orange up arrow (stronger First Strike)"),
 R("Assassin.b1.r2.free", "ability", Reuse(CLS, "VanishingAct"), "REUSED ability icon Assassin/VanishingAct.png"),
 R("Assassin.b1.r2a", "ability", D("CloakCooldown", lambda ic: (cloak(ic, 26, 28, 0.95), g_clock(ic, 49, 48, 1.05))),
   "the masked hood + a cooldown clock (Cloak and Vanishing Act come back sooner)"),
 R("Assassin.b1.r2b", "speed", D("Fleetfoot", lambda ic: (boot(ic, 32, 30, 1.45, pal="shadow", sole="dark", line=True), g_speed(ic, 4, 22, 1.0), g_wing(ic, 46, 50, 0.9))),
   "a dark shadow boot with speed lines + a teal wing (move speed, double while Cloaked)"),
 R("Assassin.b1.r3a", "resource", D("CloakEfficiency", lambda ic: (cloak(ic, 26, 28, 0.95), g_bolt(ic, 48, 46, 0.85, "stamina_y"), g_down(ic, 56, 22, 0.7, "resource"))),
   "the masked hood + a stamina bolt with a violet down arrow (costs less Stamina)"),
 R("Assassin.b1.r3b", "damage", D("Backstab", lambda ic: (g_ally(ic, 28, 30, 1.5, "rock"), dagger(ic, 54, 54, 34, 30, 2.4), g_up(ic, 14, 52, 0.85, "damage"))),
   "a dagger driven into a figure's back + an orange up arrow (hits from behind deal more)"),
 R("Assassin.b1.r4a", "ability", D("VanishEcho", lambda ic: (vanish(ic, 24, 24, 0.95), cloud(ic, 46, 46, 0.6, pal="smoke", base=0.4), g_plus(ic, 14, 52, 0.8, "ability"))),
   "a smoke cloud leaving a second, smaller cloud behind + a blue plus"),
 R("Assassin.b1.r4b", "control", D("SmokeVeil", lambda ic: (cloak(ic, 24, 28, 0.9), cloud(ic, 30, 50, 0.7, pal="smoke"), g_stars(ic, 48, 16, 0.85))),
   "the hood bursting out of smoke + stun stars (breaking Cloak stuns nearby)"),
 R("Assassin.b1.r4c", "resource", D("Nightrunner", lambda ic: (g_bolt(ic, 26, 30, 1.7, "stamina_y"), ic.add(ering(26, 30, 20, 20, 17, 17), G, base=0.5, bevel=0, line=True),
                                                             g_plus(ic, 50, 52, 0.85, "resource"))),
   "a stamina bolt in a lilac night ring + a violet plus (Stamina regen)"),
 R("Assassin.b1.r5a", "damage", D("PhantomEdge", lambda ic: (vanish(ic, 26, 20, 0.85), dagger(ic, 14, 56, 40, 30, 2.6), g_up(ic, 50, 50, 1.0, "damage"))),
   "a dagger lunging out of the Vanishing Act smoke + an orange up arrow (first hit after it deals more)"),
 R("Assassin.b1.r5b", "ability", D("KillCloak", lambda ic: (g_skull(ic, 20, 24, 1.3), cloak(ic, 40, 40, 0.75), g_plus(ic, 50, 14, 0.75, "ability"))),
   "a skull (a kill) + the hood re-cloaking (a kill while Cloaked cloaks you again)"),
 R("Assassin.b1.r6", "ability", D("GhostProtocol", lambda ic: (burst(ic, 30, 30, 28, 12, 10, G, base=0.5), cloak(ic, 30, 30, 0.95), g_skull(ic, 50, 50, 0.85),
                                                              g_repeat(ic, 12, 50, 0.8))),
   "the masked hood on a lilac burst, a skull + a repeat arrow (capstone: a First Strike kill cloaks you again)"),
 # ---------------------------------------------------------------- Executioner
 R("Assassin.b2.r1a", "damage", D("WeaponPower", lambda ic: (dagger(ic, 10, 54, 42, 16, 3.0), g_up(ic, 50, 50, 1.1, "damage"))),
   "a long dagger + an orange up arrow (more weapon damage)"),
 R("Assassin.b2.r1b", "damage", D("KunaiMark", lambda ic: (kunai(ic, 8, 50, 30, 30, 1.0), g_target(ic, 42, 24, 1.15), g_plus(ic, 50, 52, 0.8, "damage"))),
   "a kunai flying at an orange target mark + a plus (the marked target takes more)"),
 R("Assassin.b2.r2.free", "ability", Reuse(CLS, "ShadowClone"), "REUSED ability icon Assassin/ShadowClone.png (the free passive)"),
 R("Assassin.b2.r2a", "ability", D("CloneSplit", lambda ic: (clone(ic, 20, 30, 0.95, base=0.35), clone(ic, 36, 32, 1.0), g_plus(ic, 50, 52, 0.85, "ability"))),
   "two shadow clones side by side + a blue plus (one more clone)"),
 R("Assassin.b2.r2b", "ability", D("CloneDuration", lambda ic: (clone(ic, 26, 30, 1.15), g_hourglass(ic, 50, 48, 1.15))),
   "a shadow clone + a blue hourglass (clones last longer)"),
 R("Assassin.b2.r3a", "ability", D("KunaiChain", lambda ic: (kunai(ic, 6, 40, 28, 22, 1.0), g_zap(ic, 44, 44, 1.1))),
   "a kunai + a blue bolt bouncing between two enemies (bounces to one more)"),
 R("Assassin.b2.r3b", "damage", D("MirrorStrike", lambda ic: (clone(ic, 22, 32, 1.05), dagger(ic, 30, 54, 54, 26, 2.2), g_echo(ic, 50, 18, 0.85, "damage"))),
   "a shadow clone striking again with a dagger + orange echo arcs (ability hits repeat from the clone)"),
 R("Assassin.b2.r3c", "damage", D("Bloodthirst", lambda ic: (godkill(ic, 26, 32, 0.85), g_drop(ic, 46, 40, 0.9), g_up(ic, 52, 16, 0.8, "damage"))),
   "the God Killer crown and dagger, a blood drop + an orange up arrow (big hits give a damage buff)"),
 R("Assassin.b2.r4a", "control", D("ClonePull", lambda ic: (clone(ic, 16, 32, 0.9), g_mob(ic, 46, 30, 0.9), g_pull(ic, 32, 52, 0.85, "control", ang=180))),
   "a mob pulled toward a shadow clone by a yellow pull arrow"),
 R("Assassin.b2.r4b", "damage", D("Lethality", lambda ic: (dagger(ic, 10, 54, 40, 18, 2.8), g_skull(ic, 48, 46, 1.05), spark(ic, 44, 14, "damage", 2))),
   "a dagger + a skull and an orange spark (a chance for a Lethal hit)"),
 R("Assassin.b2.r5.free", "ability", Reuse(CLS, "GodKiller"), "REUSED ability icon Assassin/GodKiller.png"),
 R("Assassin.b2.r5a", "ability", D("GodKillerCooldown", lambda ic: (godkill(ic, 26, 32, 0.95), g_clock(ic, 50, 48, 1.0))),
   "the God Killer crown and dagger + a cooldown clock (comes back sooner)"),
 R("Assassin.b2.r5b", "damage", D("BountySense", lambda ic: (crown(ic, 30, 24, 0.75), g_mob(ic, 30, 40, 1.3, pal="cls_Berserker"), g_up(ic, 52, 50, 0.85, "damage"))),
   "a crowned big mob (an elite / boss) + an orange up arrow (more damage to them)"),
 R("Assassin.b2.r6", "damage", D("Deicide", lambda ic: (burst(ic, 30, 32, 28, 12, 10, "gold", base=0.5), godkill(ic, 30, 34, 0.95), g_lowhp(ic, 50, 50, 0.75))),
   "the God Killer crown and dagger on a gold burst + a drained heart (capstone: more damage the lower the target's Health)"),
 # ---------------------------------------------------------------- Venomcraft
 R("Assassin.b3.r1a", "ability", D("Lingering", lambda ic: (tcloud(ic, 26, 28), g_hourglass(ic, 50, 48, 1.15))),
   "a green Toxin cloud + a blue hourglass (the cloud lasts longer)"),
 R("Assassin.b3.r1b", "health", D("CoatedKunai", lambda ic: (kunai(ic, 8, 52, 38, 22, 1.15, blade="poison"), g_down(ic, 50, 50, 1.0, "health"))),
   "a poison-green kunai + a red down arrow (hit enemies deal less damage to you)"),
 R("Assassin.b3.r2.free", "ability", Reuse(CLS, "Toxin"), "REUSED ability icon Assassin/Toxin.png"),
 R("Assassin.b3.r2a", "damage", D("ToxinPower", lambda ic: (toxin(ic), g_up(ic, 50, 50, 1.1, "damage"))),
   "the green Toxin flask + an orange up arrow (ticks deal more)"),
 R("Assassin.b3.r2b", "ability", D("ToxinRadius", lambda ic: (tcloud(ic, 32, 32, 0.85), g_expand(ic, 32, 32, 26, 0.7))),
   "the Toxin cloud with four blue arrows pushing outward (bigger cloud)"),
 R("Assassin.b3.r3a", "control", D("ToxinSlow", lambda ic: (tcloud(ic, 26, 26), g_snail(ic, 47, 51, 1.0))),
   "the Toxin cloud + a yellow snail (Toxin slows)"),
 R("Assassin.b3.r3b", "damage", D("Exploit", lambda ic: (g_mob(ic, 26, 28, 1.3), g_drop(ic, 12, 12, 0.6, "poison"), g_snail(ic, 26, 52, 0.55), g_crack(ic, 44, 12, 0.5),
                                                        g_up(ic, 50, 50, 1.0, "damage"))),
   "a mob carrying three debuff marks (poison, slow, crack) + an orange up arrow (more damage per debuff)"),
 R("Assassin.b3.r4a", "ability", D("ToxinEcho", lambda ic: (tcloud(ic, 24, 28, 0.9), g_echo(ic, 50, 28, 1.1), g_repeat(ic, 48, 52, 0.75))),
   "the Toxin cloud + echo arcs and a repeat arrow (pulses again)"),
 R("Assassin.b3.r4b", "health", D("Neurotoxin", lambda ic: (g_mob(ic, 26, 28, 1.3, pal="poison"), g_down(ic, 50, 50, 1.0, "health"))),
   "a poisoned green mob + a red down arrow (poisoned enemies deal less damage)"),
 R("Assassin.b3.r4c", "resource", D("PoisonStamina", lambda ic: (g_skull(ic, 22, 24, 1.3, pal="poison"), g_bolt(ic, 44, 44, 1.1, "stamina_y"), g_plus(ic, 54, 18, 0.75, "resource"))),
   "a green poison skull + a stamina bolt and plus (more Stamina; poisoned kills give some back)"),
 R("Assassin.b3.r5a", "resource", D("ToxinEfficiency", lambda ic: (toxin(ic, 26, 28, 0.95), g_crystal(ic, 47, 46, 1.0), g_down(ic, 56, 26, 0.7, "resource"))),
   "the Toxin flask + a mana crystal with a violet down arrow (costs less Mana)"),
 R("Assassin.b3.r5b", "ability", D("Contagion", lambda ic: (g_skull(ic, 22, 24, 1.3, pal="poison"), g_fork(ic, 40, 40, 1.1), g_drop(ic, 54, 52, 0.7, "poison"))),
   "a poisoned skull forking its poison on to the next enemy (a green drop)"),
 R("Assassin.b3.r6", "damage", D("BlackLotus", lambda ic: (burst(ic, 32, 32, 28, 12, 10, "poison", base=0.5),
                                                          [ic.add(rot_ellipse(32 + 9 * math.cos(math.radians(a_)), 32 + 9 * math.sin(math.radians(a_)), 10, 4.5, a_), "shadow",
                                                                  base=0.55, grad=0.5, bevel=0.8, line=True) for a_ in range(-90, 270, 60)],
                                                          ic.add(circle(32, 32, 5), "poison", mode="sphere", base=0.8, line=True))),
   "a black lotus flower with a poison-green heart on a green burst (capstone: every 3rd tick detonates)"),
]
