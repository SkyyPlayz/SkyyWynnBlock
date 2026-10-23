"""Alchemy tree node icons (40) - DRAFT v1, same style as the approved Mining icons. Loaded by tools/art/make_tree_node_icons.py."""
from make_tree_node_icons import *          # the painter: Icon, shapes, part helpers, accents
from node_icons.farming import glasshouse, herb

TREE = "Alchemy"


def splash(ic, cx, cy, s=1.0, pal="red"):
    for a in range(0, 360, 45):
        x, y = cx + 14 * s * math.cos(math.radians(a)), cy + 14 * s * math.sin(math.radians(a))
        drop(ic, x, y, 0.45 * s, pal)
    ic.add(circle(cx, cy, 7 * s), pal, mode="sphere", base=0.6, line=True)


def gas_cloud(ic, cx, cy, s=1.0, pal="poison"):
    ic.add(union(circle(cx - 9 * s, cy + 1 * s, 7 * s), circle(cx, cy - 4 * s, 9 * s), circle(cx + 9 * s, cy + 1 * s, 7 * s),
                 rect(cx - 9 * s, cy, cx + 9 * s, cy + 7 * s)), pal, base=0.62, grad=0.5, line=True)


def belt(ic, cx, cy, s=1.0):
    ic.add(rect(cx - 26 * s, cy + 6 * s, cx + 26 * s, cy + 12 * s), "leather", base=0.5, grad=0.4, line=True)
    for k, liq in enumerate(("red", "blue", "green")):
        vial(ic, cx + (k - 1) * 14 * s, cy, 0.7 * s, liquid=liq)
    ic.add(rrect(cx - 4 * s, cy + 5 * s, cx + 4 * s, cy + 13 * s, 1 * s), "gold", base=0.65, bevel=0, line=True)


# ---------------------------------------------------------------- Brewer
def steady_hand():
    ic = Icon("SteadyHand")
    flask(ic, 30, 38, 1.5, liquid="red")
    lines(ic, [(48, 22, 60, 22), (50, 30, 62, 30), (48, 38, 60, 38)], "speed", 1.5)
    return ic


def potent_brew():
    ic = Icon("PotentBrew")
    flask(ic, 28, 38, 1.55, liquid="ruby")
    plus(ic, 52, 14, 1.05, "buff")
    return ic


def extended_vial():
    ic = Icon("ExtendedVial")
    vial(ic, 24, 34, 1.5, liquid="blue")
    hourglass(ic, 50, 46, 1.0, "buff")
    return ic


def splash_mix():
    ic = Icon("SplashMix")
    flask(ic, 22, 40, 1.0, liquid="red")
    splash(ic, 44, 22, 1.0, pal="red")
    spark(ic, 10, 10, "ability", 2)
    return ic


def wide_splash():
    ic = Icon("WideSplash")
    splash(ic, 32, 32, 1.0, pal="red")
    arrows_out(ic, 32, 32, 25, "ability", 0.8)
    return ic


def quick_mix():
    ic = Icon("QuickMixAlchemy")
    flask(ic, 26, 34, 1.3, liquid="green")
    clock(ic, 49, 49, 10, "ability")
    return ic


def double_dose():
    ic = Icon("DoubleDose")
    flask(ic, 18, 40, 1.0, liquid="red")
    flask(ic, 38, 40, 1.0, liquid="red")
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def clean_distill():
    ic = Icon("CleanDistill")
    ic.add(capsule(10, 8, 30, 14, 2.0), "glass", base=0.6, bevel=0, line=True)
    drop(ic, 31, 22, 0.55, "blue")
    flask(ic, 30, 44, 1.05, liquid="blue")
    turn_arrow(ic, 32, 40, 24, -60, 40, "yield")
    return ic


def stable_brew():
    ic = Icon("StableBrew")
    flask(ic, 26, 36, 1.35, liquid="ruby")
    shield(ic, 49, 44, 0.95, pal=acc("tool"))
    return ic


def tier_up():
    ic = Icon("TierUp")
    flask(ic, 26, 38, 1.35, liquid="amethyst")
    arrow(ic, 50, 22, 1.2, "yield")
    lines(ic, [(50, 32, 50, 50)], "yield", 1.6)
    return ic


def alembic_resonance():
    ic = Icon("AlembicResonance")
    flask(ic, 24, 40, 1.15, liquid="ruby")
    ring_item(ic, 46, 22, 1.0)
    plus(ic, 53, 52, 0.9, "buff")
    return ic


def master_distiller():
    ic = Icon("MasterDistiller")
    cauldron(ic, 26, 40, 1.2, liquid="green")
    xp_orb(ic, 49, 16, 10)
    return ic


def catalyst():
    ic = Icon("Catalyst")
    gem(ic, 30, 14, 0.7, "diamond", line=True)
    drop(ic, 30, 30, 0.45, "diamond")
    flask(ic, 30, 46, 1.0, liquid="amethyst")
    spark(ic, 50, 30, "buff", 2); spark(ic, 12, 40, "buff", 1)
    return ic


def philosophers_draught():
    ic = Icon("PhilosophersDraught")
    burst(ic, 32, 36, 28, 13, 12, "gold", base=0.55)
    flask(ic, 32, 38, 1.4, liquid="gold")
    spark(ic, 52, 8, "buff", 2)
    return ic


# ---------------------------------------------------------------- Herbalist
def herb_eye():
    ic = Icon("HerbEye")
    herb(ic, 22, 60, 1.45, pal="ruby")
    eye(ic, 44, 16, 0.85, iris="emerald")
    plus(ic, 52, 48, 0.95, "yield")
    return ic


def mortar_and_pestle():
    ic = Icon("MortarAndPestle")
    mortar(ic, 28, 40, 1.3)
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def quick_gather():
    ic = Icon("QuickGather")
    herb(ic, 18, 58, 1.2)
    herb(ic, 36, 58, 1.2, pal="grass")
    plus(ic, 53, 12, 1.0, "yield")
    return ic


def trained_hands():
    ic = Icon("TrainedHands")
    gauntlet(ic, 22, 40, 1.15, pal="leather")
    herb(ic, 44, 44, 0.9)
    plus(ic, 53, 12, 0.95, "yield")
    return ic


def careful_cut():
    ic = Icon("CarefulCut")
    herb(ic, 24, 60, 1.4, pal="amethyst")
    ic.add(crescent(50, 30, 12, 170, 280, 4), "steel", base=0.7, grad=0.5, bevel=0.8, line=True)
    ic.add(capsule(46, 40, 54, 52, 1.8), "wood", base=0.55, bevel=0, line=True)
    plus(ic, 52, 10, 0.85, "yield")
    return ic


def pet_herbalist():
    ic = Icon("PetHerbalist")
    paw(ic, 24, 40, 1.4, acc("pet"))
    herb(ic, 50, 30, 0.8)
    plus(ic, 12, 10, 0.85, "pet")
    return ic


def rare_drops():
    ic = Icon("RareDrops")
    mushroom(ic, 26, 56, 1.6, cap="amethyst")
    spark(ic, 44, 30, "yield", 1)
    plus(ic, 52, 14, 1.0, "yield")
    return ic


def dried_herbs():
    ic = Icon("DriedHerbs")
    ic.add(capsule(6, 8, 40, 8, 1.4), "wood", base=0.55, bevel=0, line=True)
    for k, x in enumerate((14, 24, 34)):
        ic.add(capsule(x, 8, x, 16, 0.9), "cream", base=0.7, bevel=0)
        for (y, a, f) in ((20, 60, -1), (26, 120, 1), (32, 60, -1)):
            leaf(ic, x + f * 3, y, 0.55, a, pal="honey")
    hourglass(ic, 51, 46, 0.95, "tool")
    return ic


def alchemy_set_resonance():
    ic = Icon("AlchemySetResonance")
    for R, b in ((29, 0.5), (24, 0.68)):
        arc(ic, 32, 40, R, 200, 340, 2.6, "speed", base=b)
    helmet(ic, 32, 38, 1.0, pal="leather")
    for x in (24, 40):
        ic.add(circle(x, 34, 5), "glass", base=0.65, grad=0.5, line=True)
    return ic


def sensitive_nose():
    ic = Icon("SensitiveNose")
    herb(ic, 44, 60, 1.2, pal="amethyst")
    for k in range(3):
        waves(ic, 18, 20 + k * 10, 24, "ability", 1.3, 2.0, 2)
    return ic


def wild_mix():
    ic = Icon("WildMix")
    leaf(ic, 20, 22, 0.9, -40); mushroom(ic, 44, 30, 0.7, cap="amethyst"); berries(ic, 30, 44, 0.7)
    turn_arrow(ic, 32, 32, 27, 200, 320, "yield")
    turn_arrow(ic, 32, 32, 27, 20, 140, "yield")
    return ic


def greenhouse():
    ic = Icon("Greenhouse")
    glasshouse(ic, 26, 58, 1.2)
    herb(ic, 26, 56, 0.6)
    arrow(ic, 52, 16, 1.0, "speed")
    lines(ic, [(52, 26, 52, 40)], "speed", 1.5)
    return ic


def heart_of_the_wild_garden():
    ic = Icon("HeartOfTheWildGarden")
    ic.add(heart(32, 32, 1.75), "emerald", base=0.6, grad=0.6, bevel=1.1, line=True)
    flower(ic, 24, 26, 0.5, petal="ruby"); flower(ic, 40, 30, 0.5, petal="amethyst"); flower(ic, 32, 40, 0.45, petal="cream")
    spark(ic, 8, 10, "yield", 2); spark(ic, 56, 10, "yield", 1)
    return ic


# ---------------------------------------------------------------- Mutagen
def resist_tonic():
    ic = Icon("ResistTonic")
    flask(ic, 26, 38, 1.4, liquid="red")
    ic.add(heart(50, 16, 0.7), acc("health"), base=0.62, grad=0.5, bevel=0.6, line=True)
    return ic


def sip_quick():
    ic = Icon("SipQuick")
    vial(ic, 26, 34, 1.5, liquid="red")
    lines(ic, [(42, 20, 56, 20), (44, 30, 58, 30), (42, 40, 56, 40)], "speed", 1.5)
    return ic


def mutagen_flask():
    ic = Icon("MutagenFlask")
    burst(ic, 32, 34, 28, 13, 10, acc("damage"), base=0.55)
    flask(ic, 32, 38, 1.3, liquid="poison")
    return ic


def stable_flask():
    ic = Icon("StableFlask")
    flask(ic, 24, 38, 1.3, liquid="poison")
    shield(ic, 48, 42, 1.0, pal=acc("health"))
    return ic


def quick_chill():
    ic = Icon("QuickChill")
    flask(ic, 24, 36, 1.3, liquid="diamond")
    for (x, y) in ((10, 12), (40, 10)):
        ic.add(poly(star_pts(x, y, 5, 1.6, 6)), "diamond", base=0.85, bevel=0, line=True)
    clock(ic, 49, 49, 10, "ability")
    return ic


def antidote():
    ic = Icon("Antidote")
    vial(ic, 22, 34, 1.4, liquid="emerald")
    shield(ic, 46, 40, 1.05, pal=acc("health"))
    ic.add(capsule(42, 38, 46, 42, 1.1), "cream", base=0.8, bevel=0, cast=False)
    ic.add(capsule(46, 42, 52, 34, 1.1), "cream", base=0.8, bevel=0, cast=False)
    return ic


def volatile_vial():
    ic = Icon("VolatileVial")
    burst(ic, 40, 22, 18, 7, 9, acc("damage"), base=0.7, line=True)
    flask(ic, 24, 42, 1.1, liquid="red")
    return ic


def poison_master():
    ic = Icon("PoisonMaster")
    drop(ic, 28, 34, 2.0, "poison")
    for (x, y, r) in ((14, 52, 3), (44, 54, 2.4)):
        ic.add(circle(x, y, r), "poison", mode="sphere", base=0.6, line=True)
    plus(ic, 52, 14, 1.0, "damage")
    return ic


def potion_belt():
    ic = Icon("PotionBelt")
    belt(ic, 30, 30, 1.0)
    plus(ic, 52, 52, 1.0, "yield")
    return ic


def overdose():
    ic = Icon("Overdose")
    flask(ic, 24, 38, 1.3, liquid="ruby")
    h = heart(48, 18, 0.8)
    ic.add(inter(h, rect(0, 0, 48, 64)), acc("health"), base=0.62, grad=0.5, bevel=0.6, line=True)
    ic.add(inter(h, rect(48, 0, 64, 64)), "stone", base=0.35, bevel=0, line=True)
    plus(ic, 52, 50, 0.85, "buff")
    return ic


def transmute():
    ic = Icon("Transmute")
    flask(ic, 18, 42, 0.8, liquid="stone")
    flask(ic, 46, 26, 0.8, liquid="ruby")
    turn_arrow(ic, 32, 34, 18, 130, 300, "yield")
    return ic


def lingering_cloud():
    ic = Icon("LingeringCloud")
    gas_cloud(ic, 26, 26, 1.3)
    hourglass(ic, 51, 46, 0.95, "ability")
    return ic


def elixir_of_becoming():
    ic = Icon("ElixirOfBecoming")
    ic.add(ering(32, 36, 26, 26, 22, 22), "gold", mode="torus", torus=(32, 36, 26, 26, 22, 22), bevel=0, line=True)
    flask(ic, 32, 40, 1.35, liquid="amethyst")
    for (x, y, p) in ((10, 14, "ruby"), (54, 14, "emerald"), (54, 58, "diamond")):
        ic.add(circle(x, y, 3), p, mode="sphere", base=0.7, line=True)
    return ic


ROWS = [
 ("Alchemy.b1.r1.free", "B1R1Free", "speed", steady_hand, "a red potion flask with teal speed lines (brews faster)"),
 ("Alchemy.b1.r1a", "B1R1a", "buff", potent_brew, "a ruby potion flask + a purple plus (stronger effects)"),
 ("Alchemy.b1.r1b", "B1R1b", "buff", extended_vial, "a tall blue vial + a purple-sand hourglass (longer effects)"),
 ("Alchemy.b1.r2.free", "B1R2Free", "ability", splash_mix, "a flask and a red potion splash"),
 ("Alchemy.b1.r2a", "B1R2a", "ability", wide_splash, "a red splash with four blue arrows pushing outward (bigger radius)"),
 ("Alchemy.b1.r2b", "B1R2b", "ability", quick_mix, "a green potion flask + a blue cooldown clock"),
 ("Alchemy.b1.r3a", "B1R3a", "yield", double_dose, "two red potion flasks + a green plus (two charges)"),
 ("Alchemy.b1.r3b", "B1R3b", "yield", clean_distill, "a glass tube dripping into a blue flask, a green turn arrow (fewer ingredients)"),
 ("Alchemy.b1.r3c", "B1R3c", "tool", stable_brew, "a ruby flask + a soft-white shield (does not expire early)"),
 ("Alchemy.b1.r4a", "B1R4a", "yield", tier_up, "a purple flask + a tall green up arrow (higher tier)"),
 ("Alchemy.b1.r4b", "B1R4b", "buff", alembic_resonance, "a ruby flask and a gold ring + a purple plus (per accessory)"),
 ("Alchemy.b1.r5a", "B1R5a", "xp", master_distiller, "a bubbling green cauldron + a gold XP orb"),
 ("Alchemy.b1.r5b", "B1R5b", "buff", catalyst, "a diamond dripping into a purple flask, purple sparkles"),
 ("Alchemy.b1.r6", "B1R6", "buff", philosophers_draught, "a golden potion flask on a gold star burst (capstone)"),
 ("Alchemy.b2.r1a", "B2R1a", "yield", herb_eye, "a red herb sprig and a green-eyed eye + a green plus"),
 ("Alchemy.b2.r1b", "B2R1b", "yield", mortar_and_pestle, "a stone mortar and pestle with green paste + a green plus"),
 ("Alchemy.b2.r2.free", "B2R2Free", "yield", quick_gather, "two herb sprigs + a green plus (double yield)"),
 ("Alchemy.b2.r2a", "B2R2a", "yield", trained_hands, "a leather glove beside a herb + a green plus"),
 ("Alchemy.b2.r2b", "B2R2b", "yield", careful_cut, "a purple herb and a curved herb knife + a green plus (rare herbs)"),
 ("Alchemy.b2.r3a", "B2R3a", "pet", pet_herbalist, "a tan paw beside a herb + a tan plus"),
 ("Alchemy.b2.r3b", "B2R3b", "yield", rare_drops, "a purple mushroom + a green plus (rare ingredients)"),
 ("Alchemy.b2.r3c", "B2R3c", "tool", dried_herbs, "herbs hung up to dry + a soft-white hourglass (shelf life)"),
 ("Alchemy.b2.r4a", "B2R4a", "speed", alchemy_set_resonance, "a leather cap with brewing goggles, teal resonance arcs (per armor piece)"),
 ("Alchemy.b2.r4b", "B2R4b", "ability", sensitive_nose, "blue scent trails drifting to a purple herb"),
 ("Alchemy.b2.r5a", "B2R5a", "yield", wild_mix, "a leaf, a mushroom and berries inside green circling arrows (free ingredient)"),
 ("Alchemy.b2.r5b", "B2R5b", "speed", greenhouse, "a little glasshouse with a herb + a teal up arrow (regrow speed)"),
 ("Alchemy.b2.r6", "B2R6", "yield", heart_of_the_wild_garden, "an emerald heart blooming with flowers (capstone)"),
 ("Alchemy.b3.r1a", "B3R1a", "health", resist_tonic, "a red tonic flask and a red heart (+ max Health)"),
 ("Alchemy.b3.r1b", "B3R1b", "speed", sip_quick, "a red vial with teal speed lines (drink faster)"),
 ("Alchemy.b3.r2.free", "B3R2Free", "damage", mutagen_flask, "a bubbling green mutagen flask on an orange burst (+ damage)"),
 ("Alchemy.b3.r2a", "B3R2a", "health", stable_flask, "a mutagen flask + a red shield (smaller defense penalty)"),
 ("Alchemy.b3.r2b", "B3R2b", "ability", quick_chill, "an icy flask with snowflakes + a blue cooldown clock"),
 ("Alchemy.b3.r3a", "B3R3a", "health", antidote, "a green antidote vial + a red shield with a tick (debuff resistance)"),
 ("Alchemy.b3.r3b", "B3R3b", "damage", volatile_vial, "a red flask under an orange explosion (thrown potion damage)"),
 ("Alchemy.b3.r3c", "B3R3c", "damage", poison_master, "a big lime poison drop + an orange plus"),
 ("Alchemy.b3.r4a", "B3R4a", "yield", potion_belt, "a leather belt holding three vials + a green plus (one more quickslot)"),
 ("Alchemy.b3.r4b", "B3R4b", "buff", overdose, "a ruby flask and a half-empty heart + a purple plus (stronger at low Health)"),
 ("Alchemy.b3.r5a", "B3R5a", "yield", transmute, "a grey failed brew turning into a ruby potion on a green arrow"),
 ("Alchemy.b3.r5b", "B3R5b", "ability", lingering_cloud, "a lime poison cloud + an hourglass (longer zone)"),
 ("Alchemy.b3.r6", "B3R6", "buff", elixir_of_becoming, "a purple elixir in a gold ring with three coloured motes (capstone)"),
]
