"""SkyWynn Skill Trees 3 round R3b - THE ONE TABLE of the skill-tree upgrades that a mod OTHER than SkyyTrees applies (2026-10-20).
Owner: Skyy (they/them). Spec: research/Skill-Trees-3-Spec.md section 4 + 7 (R3); the trees themselves: tools/trees_v3_data.py (R0).

Skyy (2026-10-18, docs/answered/skills.md): "i want all the skill trees to follow the same general pattern. drop the dust" + the four power
sources rule (PROJECT-RULES 4: "your weapon is only part of it. your gear is important, but accessory's and pets are essential too!").

Build scripts IMPORT this file: tools/<mod>_<ver>_patch.py of SkyyGear 0.3.32, SkyyPets 0.4.5, SkyyAccessories 0.5.28, SkyySkills 0.4.56,
SkyyFishing 0.1.11, SkyyCooking 0.1.14 generate their Java from the rows they own; SkyyTrees (the next build after 0.4.0) flips every
upgrade named here from "(coming soon)" to live with the hook ("v3", <applier>) - see THE CONTRACT below. Edit numbers HERE, then rebuild
the applier (and SkyyTrees for the page text).

THE CONTRACT (SkyyTrees <-> the appliers, java.lang types only, through the skyy.bridge map):
  saved key   "Skill.<Tree>.b<branch>.<id>" (= SkyyTrees' saved key of the upgrade, players/<pkey>.properties v=3)
  rank read   tree:fn:level.apply(new Object[] { UUID player, "Skill.<Tree>.b<n>.<id>" }) -> Integer = the rank the player owns (0 when the
              upgrade is not live, unknown, or SkyyTrees is older than the v3 hook build - SkyyTrees 0.4.0 answers 0 for every "Skill." key,
              so every applier below is a no-op until SkyyTrees flips the hooks)
  live        the upgrade is buyable only while tree:reads:<applier> (a comma String) lists its saved key - each applier puts its list at
              setup and removes exactly its own value at shutdown (bridge.remove(key, value)), the 0.3 READER CONTRACT
  aliases     READ_OLD below: 0.3 node aliases ("old" hooks of trees_v3_data.py) an applier newly reads through tree:fn:bonus - live today
              (SkyyTrees 0.4.0 already knows those readers: READ_BY)

Row = (tree, branch number, upgrade id, applier mod, effect, per rank, scale, scale cap):
  effect  a skill:bonus key (fractions: dd.<skill> Fortune / 100, xp.<skill> XP / 100, bp.<skill> Breaking Power / 100) or a SkyyGear stat
          key (dmg / cc / cd: whole %), or a named effect the applier documents (class.xp, petsyn.mining, cook.ingr)
  scale   None = per rank flat; "tool" = x the held tool's material tier (SkyyGear tool tier 0 Crude / Wood .. 7 Onyxium / Titanium / Lumen);
          "armor:<fam>" = x the worn ACTIVE armor pieces of that family (mining / foraging / farming / combat), at most `cap`;
          "acc" = x the accessories that count in Void Charms (best of each line, the Omni = 1), at most `cap`;
          "pet:<Skill>" = x the RARITY BONUS of the best equipped pet of that skill (pet slot + the open summon slot): SkyyPets' own
          pets.rarity.<r> multiplier (x1 Common .. x1.5 Mythic by default) - Skyy 2026-10-15 "pets arnt tiered, but generally ordered" and
          "a pet's rarity is a small modifier" (docs/answered/pets.md), so a Mythic pet is worth x1.5, never x6; the cap column of a pet row
          is the highest rarity index (6) only
  value = min(per x rank x scale, the row's ceiling) (scale 1 when None)

First-pass numbers (Skyy 2026-10-20 "if you have any doubt, do research to get good data to base your default on"): the per-rank numbers are
the trees' own texts (trees_v3_data.py, spec section 4); the CAPS are new (the spec gives none): 4 armor pieces (the spec's "max 4 pieces"),
5 accessories (the per-slot rows would otherwise grow with all 60 Void Charms slots).
CEILINGS (fixer 2026-10-20, critics: the tree Fortune rows of three mods had no combined limit): every row has a ceiling = the most it ever
adds (vmax below; Server Setup "Most" row). Fortune is uncapped by design (Skyy 2026-10-18 "there isnt a cap on any of the fortunes"; the
"cant get over 100% till you reach T4" line is about the TOOL's own +3 a level), so the limit is a BUDGET, from Skyy's own numbers:
fully maxed gathering armor ~ +60 Fortune (docs/answered/gear.md 2026-10-16) = the armor's 30 % of the power split (35/30/20/15, A:190
Q15) -> ~200 end-game Fortune a skill; the skill tree's share is held to the pets' 15 % of it plus a little = TREE_FORT_MAX 40 a skill.
Each non-pet Fortune row stops at 15 (= the pets' own whole Fortune cap pets.fortune.cap 10 x the x1.5 Mythic bonus) and each pet row at
its x1.5 value (7.5), so Mining <= 22.5, Foraging / Farming <= 37.5 (check() proves the sum per skill). research/balance/targets.md has no
tree target yet - the balance pass P5 tunes it; a server owner can change every per-rank number and ceiling in Server Setup (cfg_rows).
FIXER 2 (2026-10-20, critic: "the top ranks of five upgrades are worth nothing"): with the trees' own +2 a rank the ceiling was reached at
rank 1-2 (4 pieces / 5 accessories / a T4+ tool), so the last ranks bought nothing. The per-rank numbers are now ceiling / (max rank x the
top count): Trinket Seams + Accessory Boughs 1 a rank a counting accessory, Scythe Tempering 0.7 a rank a hoe tier, Farming Gear Resonance
1.25 and Foraging Gear Resonance 0.75 a rank a piece - every rank adds at the top count, and check() proves no default ceiling cuts the
max rank (natural <= ceiling). The ceilings stay (they bound a server owner's own per-rank change).
Combat Accessory Plates (fixer 2, four power sources: Combat had no accessory row): +2 FLAT max Health per counting accessory per rank
(the spec's "+2% max health" read against the base 100 Health - SkyyAccessories' Health is flat since 0.5, the Vitality booster too),
at most 5 accessories = +30 at rank 3 (a Lv 1 Copper armor set gives +25, a Lv 40 set ~+269: docs/answered/gear.md 2026-10-03/04);
added to the Power's own Health (skyyacc_health), no reader needed.
"""
import trees_v3_data as V3D

# (tree, branch, id, applier, effect, per rank, scale, cap)
EFFECTS = [
    # ---------------- Mining (essential): tool tier, gear, accessory, pet rows + Pet Synergy
    ("Mining", 2, "r1a", "SkyyGear", "bp.mining", 0.02, "tool", 7),                # Tool Mastery: +2% mining speed per tool tier, per rank
    ("Mining", 2, "r3a", "SkyyGear", "bp.mining", 0.01, "armor:mining", 4),        # Gear Resonance: +1% mining speed per mining piece
    ("Mining", 2, "r4a", "SkyyAccessories", "dd.mining", 0.01, "acc", 5),         # Trinket Seams: +1 Mining Fortune per accessory (fixer 2: was 2, max rank = the 15 ceiling)
    ("Mining", 3, "r3a", "SkyyPets", "xp.mining", 0.02, "pet:Mining", 6),          # Pet Digger: +2% Mining XP ...
    ("Mining", 3, "r3a", "SkyyPets", "dd.mining", 0.01, "pet:Mining", 6),          # ... and +1% ore yield, x the Mining pet's rarity bonus
    ("Mining", 3, "r5a", "SkyyPets", "petsyn.mining", 0.04, None, 0),              # Pet Synergy: Mining pets' effects +4% per rank
    # ---------------- Foraging (essential)
    ("Foraging", 3, "r1b", "SkyyGear", "bp.foraging", 0.02, "tool", 7),            # Tool Tier Bonus: +2% chopping speed per axe tier
    ("Foraging", 3, "r3a", "SkyyGear", "dd.foraging", 0.0075, "armor:foraging", 4),  # Gear Resonance: +0.75 Foraging Fortune per forest piece (fixer 2: was 1)
    ("Foraging", 3, "r4a", "SkyyAccessories", "dd.foraging", 0.01, "acc", 5),     # Accessory Boughs: +1 Foraging Fortune per accessory (fixer 2: was 2)
    ("Foraging", 2, "r4a", "SkyyPets", "xp.foraging", 0.02, "pet:Foraging", 6),    # Pet Companion: +2% Foraging XP ...
    ("Foraging", 2, "r4a", "SkyyPets", "dd.foraging", 0.01, "pet:Foraging", 6),    # ... and +1% yield x the Foraging pet's rarity bonus
    # ---------------- Combat (essential; points = the class level)
    ("Combat", 1, "r1a", "SkyyGear", "dmg", 2, None, 0),                           # Hone Edge: +2% weapon damage per rank
    ("Combat", 1, "r1b", "SkyyGear", "cc", 2, None, 0),                            # Weak Spot: +2% crit chance per rank
    ("Combat", 1, "r4a", "SkyyGear", "cd", 3, None, 0),                            # Crit Mastery: +3% crit damage per rank
    ("Combat", 1, "r4b", "SkyyGear", "dmg", 2, "armor:combat", 4),                 # Gear Resonance: +2% damage per combat armor piece
    ("Combat", 2, "r4a", "SkyyAccessories", "hp", 2, "acc", 5),                    # Accessory Plates: +2 max Health per accessory (fixer 2; flat = 2% of the base 100)
    ("Combat", 3, "r3a", "SkyyPets", "xp.combat", 0.02, "pet:Combat", 6),          # Pet Fang: +2% combat (class) XP ...
    ("Combat", 3, "r3a", "SkyyPets", "dmg", 1, "pet:Combat", 6),                   # ... and +1% damage x the Combat pet's rarity bonus
    ("Combat", 3, "r5b", "SkyySkills", "class.xp", 0.02, None, 0),                 # Combat Insight: +2% combat (class) XP per rank
    # ---------------- Farming (useful)
    ("Farming", 1, "r5b", "SkyyGear", "dd.farming", 0.007, "tool", 7),             # Scythe Tempering: +0.7 Farming Fortune per hoe tier (fixer 2: was 2)
    ("Farming", 3, "r3c", "SkyyGear", "dd.farming", 0.0125, "armor:farming", 4),   # Gear Resonance: +1.25 Farming Fortune per farming piece (fixer 2: was 2)
    ("Farming", 2, "r3a", "SkyyPets", "xp.farming", 0.02, "pet:Farming", 6),       # Pet Farmer: +2% Farming XP ...
    ("Farming", 2, "r3a", "SkyyPets", "dd.farming", 0.01, "pet:Farming", 6),       # ... and +1% yield x the Farming pet's rarity bonus
    # ---------------- Cooking (useful)
    ("Cooking", 2, "r1a", "SkyyCooking", "cook.ingr", 0.03, None, 0),              # Forager's Larder: +3% ingredient yield (Prep Cook's double output)
    ("Cooking", 2, "r3b", "SkyyPets", "xp.cooking", 0.02, "pet:Farming", 6),       # Pet Sous-Chef: +2% Cooking XP x the Farming pet's rarity bonus
    # ---------------- Alchemy (useful)
    ("Alchemy", 2, "r3a", "SkyyPets", "xp.alchemy", 0.02, "pet:Foraging", 6),      # Pet Herbalist: +2% Alchemy XP x the Foraging pet's rarity bonus
    # ---------------- Fishing (light, rework pending): Pet Angler stays coming soon - every Fishing XP is a skill:fn:addxp GRANT, and putting
    # Fishing into SkyySkills' bridge.bonus.addxpSkills would also boost SkyyCollections / SkyyQuests / SkyyShards Fishing rewards
    # ---------------- Smithing (light)
    ("Smithing", 2, "r3b", "SkyyPets", "xp.smithing", 0.02, "pet:Mining", 6),      # Pet Hammer: +2% Smithing XP x the Mining pet's rarity bonus
    # ---------------- R3c (2026-10-20, SkyyGear 0.3.33 / SkyyAccessories 0.5.29): the gear / weapon / accessory rows R3b left coming soon
    # (appended at the end: the R3b rows keep their indexes = their V3P<i> / V3X<i> fields). See R3C below for every number's reason.
    ("Combat", 1, "r5b", "SkyyGear", "dmg", 1, "weapon", 5),                       # Weapon Tempering: +1% damage per weapon tier above Iron (at most 5), per rank (tree text 2: R3C)
    ("Mining", 2, "r6", "SkyyGear", "bp.mining", 0.25, "pick", 2),                  # Masterwork Pick (capstone): +25% Breaking Power on a held pick, x2 on your own lifelong one
    ("Mining", 2, "r6", "SkyyGear", "dd.mining", 0.075, "pick", 2),                 # ... and +7.5 Mining Fortune, x2 = 15 (the row ceiling; tree text 10: R3C)
    ("Exploration", 2, "r3a", "SkyyAccessories", "spd", 0.5, "acc", 5),            # Accessory Compass: +0.5% move Speed per counting accessory per rank (tree text 2: R3C)
    ("Acrobatics", 2, "r3a", "SkyyAccessories", "stam", 0.2, "acc", 5),             # Accessory Sprint: +0.2 max Stamina (2% of the base 10) per counting accessory per rank
]

# R3c FIRST-PASS NUMBERS (builder 2026-10-20; Skyy "if you have any doubt, do research to get good data to base your default on" + the four power
# sources rule; every number is a Server Setup row - Gear -> Stats / Void Charms -> Skill trees, Advanced):
#   Weapon Tempering  tree text "+2% damage per weapon tier above Iron, per rank": 2 x 4 ranks x 5 steps (Thorium .. Onyxium / Titanium / Lumen)
#                     = +40% Damage, more than every other Combat row together (Hone Edge 10, Combat Gear Resonance 24, the Combat pet 7.5) and
#                     above a weapon's own Damage roll (30 at 100%); fixer 2's rule (per = ceiling / (max rank x top count)) with a 20 ceiling
#                     (between Hone Edge and Gear Resonance) -> 1 a step a rank: +20% at rank 4 with an Onyxium-tier weapon, +4% with Thorium.
#                     Steps = SkyyGear's internal tool / weapon tier of the id's metal word - 2 (Iron / Steel = 2): Bronze / Thorium 1, Cobalt /
#                     Lead / Dusk 2, Adamantite / Chromium / Azurvane 3, Mithril / Slag / Cinder 4, Onyxium / Titanium / Lumen 5.
#   Masterwork Pick   tree text "+25% speed and +10% ore yield, doubled while held tool is the highest tier in your inventory": speed = Breaking
#                     Power (the R3b reading of "mining speed"), kept at +25 / +50; "ore yield" = Mining Fortune (Pet Digger's reading) at
#                     +7.5 / +15 so the row stays inside ROW_FORT_MAX and Mining's tree Fortune budget (15 + 7.5 + 15 = 37.5 <= 40); "highest
#                     tier in your inventory" = your own working lifelong pickaxe / multitool (Skyy 2026-10-16: normal tools are gone, the
#                     lifelong one is the one that tiers up), any other pick x1.
#   Accessory Compass tree text "+2% move speed per filled accessory slot/rank" = 2 x 3 x 5 = +30% Speed, three times the Legendary Speed Accessory
#                     (+10%); held to 7.5 (3/4 of that accessory: the accessories' 20% share) -> 0.5 a rank an accessory; added to the
#                     Accessory Power's Speed (AccPower.tick c[7] -> the accessories.talismans movement source).
#   Accessory Sprint  "+2% stamina" read against the vanilla base 10 Stamina (Server/Entity/Stats/Stamina.json, research/Exploration-Build-Spec.md;
#                     the Plates rule: % of the base -> flat points): 0.2 a rank an accessory, +3 at rank 3 x 5 (the Legendary Stamina Accessory
#                     gives +12); added to the skyyacc_stamina modifier.
#   "filled accessory slot" = an accessory that COUNTS in Void Charms (AccV3.count: best of each line, the Omni 1), at most 5 - the R3b rows' rule.

# 0.3 node aliases an applier newly READS (live with SkyyTrees 0.4.0: those nodes already name the applier in its READ_BY)
# (old node key, applier, the v3 upgrade(s) that feed it, what the applier does with tree:fn:bonus)
READ_OLD = [
    ("Alchemy.PWisdom", "SkyySkills", "Alchemy b1 r5a Master Distiller", "xp.alchemy from SkyyTrees' own skill:bonus source (Alchemy in bridge.bonus.xpSkills)"),
    ("Fishing.NBite", "SkyyFishing", "Fishing b1 r1a Sharp Hook", "+Fishing Speed % (fraction x 100)"),
    ("Fishing.NFortune", "SkyyFishing", "Fishing b1 r1b Fish Fortune", "+double catch %"),
    ("Fishing.NTreasure", "SkyyFishing", "Fishing b2 r3a Salvage Hook", "+Treasure Chance %"),
]

# the 0.3 node ids SkyyTrees 0.4.0 no longer feeds (no v3 upgrade aliases them) that a NON-SkyyTrees mod read - each reader moves or drops it
DEAD_READERS = {
    "SkyyCooking": {"CGrill": "dropped", "CPrep": "dropped", "CBaker": "dropped", "CMaster": "dropped",
                    "CIngr": "moved to Skill.Cooking.b2.r1a Forager's Larder (cook.ingr)", "CFed": "never read (a comment)"},
    "SkyyExploration": {"EScav": "dropped (Scavenger has no v3 upgrade)"},
}


def key(tree, branch, uid):
    return "Skill.%s.b%d.%s" % (tree, branch, uid)


def up(tree, branch, uid):
    """the trees_v3_data upgrade dict of a row (KeyError / AssertionError when the table changed)"""
    t = V3D.tree(tree)
    assert t["kind"] == "skill", tree
    for r in t["branches"][branch - 1]["rows"]:
        for u in r["ups"]:
            if u["id"] == uid:
                return u
    raise KeyError(key(tree, branch, uid))


def rows(applier):
    """the EFFECTS rows one applier owns"""
    return [e for e in EFFECTS if e[3] == applier]


def keys(applier):
    """the saved keys one applier lists in tree:reads:<applier> (sorted, unique)"""
    return sorted(set(key(e[0], e[1], e[2]) for e in EFFECTS if e[3] == applier))


def reads_csv(applier):
    """tree:reads:<applier>: the v3 keys + the 0.3 aliases it reads"""
    return ",".join(keys(applier) + sorted(o for o, a, _u, _w in READ_OLD if a == applier))


def maxrank(tree, branch, uid):
    return up(tree, branch, uid)["max"]


# ---------------------------------------------------------------------------------------------------- CEILINGS (fixer 2026-10-20, see the header)
TREE_FORT_MAX = 0.40     # the most all tree Fortune rows of ONE skill add together (40 Fortune), proved by check()
PET_FACTOR_MAX = 1.5     # SkyyPets pets.rarity.mythic default (x1 Common .. x1.5 Mythic) - a pet row's natural top
ROW_FORT_MAX = 0.15      # a non-pet Fortune row stops at 15 (pets.fortune.cap 10 x 1.5)
VMAX = {  # (tree, branch, id, effect) -> ceiling in effect units; rows not named stop at their natural top (natural())
    ("Mining", 2, "r4a", "dd.mining"): ROW_FORT_MAX,          # Trinket Seams (natural 30)
    ("Foraging", 3, "r3a", "dd.foraging"): ROW_FORT_MAX,      # Gear Resonance (natural 20)
    ("Foraging", 3, "r4a", "dd.foraging"): ROW_FORT_MAX,      # Accessory Boughs (natural 30)
    ("Farming", 1, "r5b", "dd.farming"): ROW_FORT_MAX,        # Scythe Tempering (natural 42)
    ("Farming", 3, "r3c", "dd.farming"): ROW_FORT_MAX,        # Gear Resonance (natural 24)
}


def flat(eff):
    """a flat-points effect (no %): max Health, max Stamina (R3c)"""
    return eff in ("hp", "stam")


def unit(eff):
    """display unit: fractions (Fortune / XP / Breaking Power / synergy / chances) show x100 as %, SkyyGear stats are whole % already"""
    return 100.0 if (eff[:3] in ("dd.", "xp.", "bp.") or eff.startswith("petsyn.") or eff in ("class.xp", "cook.ingr")) else 1.0


def natural(e):
    """the most a row can add at max rank with the top scale (pet rows: the default Mythic bonus)"""
    tree, b, uid, _m, _eff, per, scale, cap = e
    sm = 1.0 if scale is None else (PET_FACTOR_MAX if scale.startswith("pet:") else float(cap))
    return per * maxrank(tree, b, uid) * sm


def vmax(e):
    """the row's ceiling (effect units)"""
    return min(VMAX.get((e[0], e[1], e[2], e[4]), natural(e)), natural(e))


def _n(v):
    s = "%.6f" % round(float(v), 6)
    s = s.rstrip("0").rstrip(".")
    return s if s else "0"


def ckey(e):
    """the Server Setup / trees.properties key stem of a row (unique per row)"""
    return "tree.%s.b%d.%s.%s" % (e[0], e[1], e[2], e[4].split(".")[0])


_EW = {"hp": "Health", "dd": "Fortune", "xp": "XP", "bp": "Power", "dmg": "Damage", "cc": "Crit", "cd": "Crit Dmg", "petsyn": "Boost", "class": "XP", "cook": "Chance",
       "spd": "Speed", "stam": "Stamina"}


def _scale_words(e):
    sc = e[6]
    if sc is None:
        return "a rank"
    if sc == "tool":
        return "a rank x the held tool's tier (at most %d)" % e[7]
    if sc == "acc":
        return "a rank x each counting accessory (at most %d)" % e[7]
    if sc.startswith("armor:"):
        return "a rank x each worn %s piece (at most %d)" % (sc[6:], e[7])
    if sc == "weapon":
        # fixer 2 (critic: the tier tags count 13 steps above Iron, SkyyGear's metal tier 5): name the steps the row really uses
        return "a rank x weapon metal steps over Iron (Bronze/Thorium 1, Cobalt 2 .. Onyxium %d)" % e[7]
    if sc == "pick":
        return "a rank on a held pick, x2 on your own lifelong one"
    return "a rank x the %s pet's rarity bonus" % sc[4:]


def describe(e):
    """one plain line: '+2 % Mining Fortune a rank x ...' (ASCII)"""
    eff = e[4]
    what = {"dd": "%s Fortune", "xp": "%s XP", "bp": "%s Breaking Power"}.get(eff.split(".")[0])
    what = (what % eff.split(".", 1)[1].capitalize()) if what else {"dmg": "Damage", "cc": "Crit Chance", "cd": "Crit Damage",
                                                                     "petsyn.mining": "Mining pet stats", "class.xp": "class XP",
                                                                     "cook.ingr": "double ingredient chance", "hp": "max Health",
                                                                     "spd": "move Speed", "stam": "max Stamina"}[eff]
    return "+%s%s %s %s" % (_n(e[5] * unit(eff)), "" if flat(eff) else " %", what, _scale_words(e))


WHERE = {"SkyyPets": "Pets -> Skill trees", "SkyyGear": "Gear -> Stats", "SkyyAccessories": "Void Charms -> Skill trees"}   # Server Setup place


def cfg_text(applier, where=None):
    where = where or WHERE[applier]
    """Skyy_<Mod>/trees.properties (plain ASCII): <ckey>.per = one rank's value, <ckey>.max = the ceiling, both in % (display units)"""
    L = ["# %s - Skill Trees 3 rows (tools/trees_v3_effects.py). Change them in game: SkyWynn Menu -> Server Setup ->" % applier,
         "# %s (Advanced), or edit here and press Reload there. The ranks come from SkyyTrees (/tree). Numbers are in %%:" % where,
         "# <row>.per = what one rank gives (x the tool tier / armor pieces / accessories / pet rarity bonus the row names),",
         "# <row>.max = the most that row ever adds. 0 = the row gives nothing." + (_flat_note(applier) if [e for e in rows(applier) if flat(e[4])] else "")]
    for e in rows(applier):
        L.append("# %s %s: %s" % (e[0], up(e[0], e[1], e[2])["name"], describe(e)))
        L.append("%s.per=%s" % (ckey(e), _n(e[5] * unit(e[4]))))
        L.append("%s.max=%s" % (ckey(e), _n(vmax(e) * unit(e[4]))))
    t = "\n".join(L) + "\n"
    assert all(32 <= ord(c) < 127 for c in t.replace("\n", "")) and "\\" not in t, "trees.properties text must be plain ASCII"
    return t


def _flat_note(applier):
    """the trees.properties note on flat rows (R3c: unchanged words while Health is the only flat effect of an applier)"""
    fl = sorted(set(e[4] for e in rows(applier) if flat(e[4])))
    if fl == ["hp"]:
        return " Health rows are in Health points, not %."
    return " %s rows are in points, not %%." % " / ".join({"hp": "Health", "stam": "Stamina"}[f] for f in fl)


def _flat_word(eff):
    return {"hp": "Health", "stam": "Stamina"}[eff]


PER_HI, MAX_HI = 100, 1000     # the Server Setup bounds (display units)


def cfg_fields(applier):
    """Java fields of the class that holds the rows' live numbers (bound by the config kit: public static volatile, display units)"""
    out = []
    for i, e in enumerate(rows(applier)):
        out.append("public static volatile double V3P%d = %s;" % (i, repr(float(_n(e[5] * unit(e[4]))))))
        out.append("public static volatile double V3X%d = %s;" % (i, repr(float(_n(vmax(e) * unit(e[4]))))))
    return out


def cfg_methods(applier, warn):
    """Java methods (in order): v3num, v3per(i) / v3most(i) (EFFECT units: display / unit), loadV3(dir) (seeds trees.properties when
    missing, then reads it; a missing / bad / out-of-range line keeps the built-in number). warn = a 'Pkg.Cls.warn' call target."""
    R = rows(applier)
    m = [r"""
public static double v3num(java.util.Properties p, String k, double def, double hi) {
  String s = p == null ? null : p.getProperty(k);
  if (s == null) return def;
  try {
    double v = Double.parseDouble(s.trim());
    if (Double.isNaN(v) || Double.isInfinite(v) || v < 0.0 || v > hi) return def;
    return v;
  } catch (Throwable t) { return def; }
}"""]
    m.append("\npublic static double v3per(int i) {\n" + "".join("  if (i == %d) return V3P%d / %s;\n" % (i, i, repr(unit(e[4]))) for i, e in enumerate(R)) + "  return 0.0;\n}")
    m.append("\npublic static double v3most(int i) {\n" + "".join("  if (i == %d) return V3X%d / %s;\n" % (i, i, repr(unit(e[4]))) for i, e in enumerate(R)) + "  return 0.0;\n}")
    sets = "".join('    V3P%d = v3num(p, "%s.per", %s, %d.0);\n    V3X%d = v3num(p, "%s.max", %s, %d.0);\n'
                   % (i, ckey(e), repr(float(_n(e[5] * unit(e[4])))), PER_HI, i, ckey(e), repr(float(_n(vmax(e) * unit(e[4])))), MAX_HI)
                   for i, e in enumerate(R))
    m.append(r"""
public static String loadV3(java.nio.file.Path dir) {
  if (dir == null) return "trees.properties: no folder (built-in numbers)";
  try {
    java.nio.file.Path f = dir.resolve("trees.properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = dir.resolve("trees.properties.tmp");
      java.nio.file.Files.write(tmp, V3_TEXT.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
""" + sets + r"""    return "trees.properties read";
  } catch (Throwable t) {
    @WARN@("could not read trees.properties (the Skill Trees 3 rows keep their numbers): " + t);
    return "trees.properties could not be read";
  }
}""".replace("@WARN@", warn))
    return m


def cfg_text_field(applier, where=None):
    import json
    return "public static final String V3_TEXT = %s;" % json.dumps(cfg_text(applier, where))


def cfg_rows(applier, cls, file, cat):
    """the Server Setup rows (config kit tuples), two a row: per rank + the ceiling, bound to <cls>.V3P<i> / V3X<i> in <file>"""
    out = []
    for i, e in enumerate(rows(applier)):
        nm = up(e[0], e[1], e[2])["name"]
        ew = _EW[e[4].split(".")[0]]
        lab = "%s %s %s" % (e[0], nm, ew)
        if len(lab) > 33:
            lab = "%s %s" % (nm, ew)
        assert len(lab) <= 33, lab
        h1 = describe(e) + "."
        if len(h1) > 100:
            h1 = h1[:97] + "..."
        h2 = "Most %s %s ever adds (in %s), whatever the rank, gear or pet." % (e[0], nm, _flat_word(e[4]) if flat(e[4]) else "%")
        assert len(h2) <= 100, h2
        out.append(("%s.per" % ckey(e), lab + " a rank", cat, "dec", _n(e[5] * unit(e[4])), "0", str(PER_HI), "", "" if flat(e[4]) else "%", "live,adv", h1,
                    "field:%s.V3P%d@%s:%s.per" % (cls, i, file, ckey(e))))
        out.append(("%s.max" % ckey(e), lab + " most", cat, "dec", _n(vmax(e) * unit(e[4])), "0", str(MAX_HI), "", "" if flat(e[4]) else "%", "live,adv", h2,
                    "field:%s.V3X%d@%s:%s.max" % (cls, i, file, ckey(e))))
    for r in out:
        assert len(r[1]) <= 40 and len(r[10]) <= 100, r
    return out


def check():
    V3D.check()
    seen = set()
    for e in EFFECTS:
        tree, b, uid, mod, eff, per, scale, cap = e
        u = up(tree, b, uid)
        assert u["hook"] is None, ("R3b wires only coming-soon upgrades", e)
        assert mod in ("SkyyGear", "SkyyPets", "SkyyAccessories", "SkyySkills", "SkyyCooking", "SkyyFishing"), e
        assert (tree, b, uid, eff) not in seen, ("one row per effect", e)
        seen.add((tree, b, uid, eff))
        assert per > 0 and (scale is None) == (cap == 0), e
        assert scale is None or scale in ("tool", "acc", "weapon", "pick") or scale.startswith("armor:") or scale.startswith("pet:"), e
        assert scale not in ("weapon", "pick") or mod == "SkyyGear", ("R3c: only SkyyGear knows the held weapon / pick scales", e)
        assert len(set(m for (t2, b2, i2, m, _e, _p, _s, _c) in EFFECTS if (t2, b2, i2) == (tree, b, uid))) == 1, ("one applier per upgrade", e)
        assert "," not in key(tree, b, uid)
    assert not [e for e in EFFECTS if e[0] == "Beastmastery"], "Beastmastery stays coming soon (no skill yet)"
    assert not [e for e in EFFECTS if e[0] == "Exploration" and e[4].startswith("xp.")], "Exploration never gets XP bonuses (Skyy, SkyySkills rule)"
    # the ceilings: every VMAX names a row; the tree Fortune rows of one skill add at most TREE_FORT_MAX together; no non-pet Fortune row over
    # ROW_FORT_MAX; a pet row never above its x1.5 value
    names = set((e[0], e[1], e[2], e[4]) for e in EFFECTS)
    assert all(k in names for k in VMAX), [k for k in VMAX if k not in names]
    for sk in set(e[4][3:] for e in EFFECTS if e[4].startswith("dd.")):
        tot = sum(vmax(e) for e in EFFECTS if e[4] == "dd." + sk)
        assert tot <= TREE_FORT_MAX + 1e-9, ("tree Fortune budget", sk, tot)
    for e in EFFECTS:
        assert 0 < vmax(e) <= natural(e) + 1e-12, e
        # fixer 2: no default ceiling cuts a row below its max rank at the top count (every rank bought adds something)
        assert natural(e) <= VMAX.get((e[0], e[1], e[2], e[4]), natural(e)) + 1e-9, ("the ceiling makes the top ranks worthless", e, natural(e))
        if e[4].startswith("dd.") and not (e[6] or "").startswith("pet:"):
            assert vmax(e) <= ROW_FORT_MAX + 1e-12, e
    keys_ = [ckey(e) for e in EFFECTS]
    assert len(set(keys_)) == len(keys_), "ckey must be unique"
    return True


check()

if __name__ == "__main__":
    for m in ("SkyyGear", "SkyyPets", "SkyyAccessories", "SkyySkills", "SkyyCooking", "SkyyFishing"):
        print(m, reads_csv(m))
