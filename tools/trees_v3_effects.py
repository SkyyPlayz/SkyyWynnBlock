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
BALANCE P5 (2026-10-21, research/Balance-P5-Power-Spec.md 4.2.2 / 7.1; SkyyAccessories 0.5.30, SkyyGear 0.3.35, SkyyTrees 0.4.5): Accessory
Plates is now % of max Health (effect "hpp", a fraction: +0.5 % a rank a counting accessory, 7.5 % at rank 3 x 5 - the Void Charms Health
line became % too); Masterwork Pick's Fortune +5 / +10 (was 7.5 / 15); SkyyTrees' own Rich Seams (Mining.MFortune, +2.5 a rank, 7.5 at
rank 3) counts in TREE_FORT_MAX (TREE_OWN_FORT) -> the Mining tree's whole Fortune = 7.5 + 15 + 7.5 + 10 = 40.0 (was 67.5). The pet rows
keep their x1.5 ceiling (PET_FACTOR_MAX) although SkyyPets 0.4.8's Mythic rarity is x1.75: a Fabled / Mythic pet reaches the row ceiling.
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
    ("Combat", 2, "r4a", "SkyyAccessories", "hpp", 0.005, "acc", 5),               # Accessory Plates: +0.5 % max Health per accessory (Balance P5 4.2.2: was +2 FLAT; ceiling 7.5 %)
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
    ("Mining", 2, "r6", "SkyyGear", "dd.mining", 0.05, "pick", 2),                  # ... and +5 Mining Fortune, x2 = 10 (Balance P5 7.1: was 7.5 / 15 - the Mining tree budget with Rich Seams counted)
    ("Exploration", 2, "r3a", "SkyyAccessories", "spd", 0.5, "acc", 5),            # Accessory Compass: +0.5% move Speed per counting accessory per rank (tree text 2: R3C)
    ("Acrobatics", 2, "r3a", "SkyyAccessories", "stam", 0.2, "acc", 5),             # Accessory Sprint: +0.2 max Stamina (2% of the base 10) per counting accessory per rank
    # ---------------- Balance P8b (2026-10-22, research/Balance-P8-Rebirth-Spec.md 4.2; SkyyTrees 0.4.6, SkyyClasses 0.1.45, SkyyMobs 0.1.15):
    # the essential trees row by row. A row's FREE perk is the id "r<row>.free" (key Skill.<Tree>.b<n>.r<row>.free, rank 1 while the row is
    # open). SkyyTrees' OWN rows: vein / feller = whole ore / logs, spd = whole % move speed, the rest fractions - see the P8b notes below.
    ("Mining", 1, "r2b", "SkyyTrees", "vein", 1.0, None, 0),                        # Burst Recovery -> Burst Reach: +1 Vein Burst ore a rank
    ("Mining", 2, "r5c", "SkyyTrees", "vein", 2.0, None, 0),                        # Blast Hammer: +2 Vein Burst ore a rank
    ("Mining", 2, "r2a", "SkyyTrees", "hpp", 0.02, None, 0),                        # Rockhide: +2 % max Health a rank
    ("Mining", 2, "r2b", "SkyyTrees", "spd", 2.0, None, 0),                         # Echo Step: +2 % move speed a rank
    ("Mining", 2, "r2.free", "SkyyTrees", "fall", 0.10, None, 0),                   # Stoneskin (row 2 free perk): -10 % fall damage
    ("Mining", 3, "r3b", "SkyyTrees", "coins.mining", 0.02, None, 0),               # Deep Bounty: 2 % a rank an ore also pays coins (Mining level)
    ("Mining", 3, "r4a", "SkyyTrees", "gem.mining", 0.0006, None, 0),               # Miner's Fortune: +0.06 % a rank gem chance per block (Gem Eye's step)
    ("Mining", 3, "r5b", "SkyyTrees", "spd", 2.0, None, 0),                         # Abyss Walker: +2 % move speed a rank (Mining move 4 + 6 = 10)
    ("Mining", 2, "r4b", "SkyyClasses", "dmg", 1.5, None, 0),                       # Hardened Edge: +1.5 % damage a rank (SkyyClasses UpFx, inside dmgCap)
    ("Foraging", 1, "r2b", "SkyyTrees", "feller", 1.0, None, 0),                    # Quick Fell -> Timber reach: +1 Tree Feller log a rank
    ("Foraging", 1, "r4a", "SkyyTrees", "extra.foraging", 0.008, None, 0),          # Rare Grain: +0.8 % a rank a log drops once more (= 0.8 Fortune)
    ("Foraging", 1, "r5b", "SkyyTrees", "xp.foraging", 0.015, None, 0),             # Forest Fortune: +1.5 % Foraging XP a rank
    ("Foraging", 3, "r1a", "SkyyTrees", "spd", 2.0, None, 0),                       # Light Foot: +2 % move speed a rank
    ("Foraging", 3, "r3b", "SkyyTrees", "hpp", 0.02, None, 0),                      # Sturdy Hide: +2 % max Health a rank
    ("Foraging", 3, "r3c", "SkyyTrees", "fall", 0.05, None, 0),                     # Wind Walker: -5 % fall damage a rank
    ("Combat", 1, "r1.free", "SkyyClasses", "dmg", 3.0, None, 0),                   # Combat Focus (row 1 free perk): +3 % damage (no streak system: flat)
    ("Combat", 1, "r3a", "SkyyClasses", "dmgLow", 4.0, None, 0),                    # Finisher: +4 % a rank vs enemies below 30 % Health
    ("Combat", 1, "r3b", "SkyyTrees", "spd", 1.0, None, 0),                         # Momentum: +1 % move speed a rank
    ("Combat", 1, "r5a", "SkyyClasses", "dmgBoss", 3.0, None, 0),                   # Trophy Hunter: +3 % a rank vs bosses + mini bosses
    ("Combat", 2, "r1a", "SkyyTrees", "hpp", 0.005, None, 0),                       # Toughness: +0.5 % max Health a rank (Combat Health budget 10 with Plates 7.5)
    ("Combat", 2, "r1b", "SkyyClasses", "kbRes", 3.0, None, 0),                     # Iron Will: +3 % knockback resistance a rank
    ("Combat", 2, "r3a", "SkyyClasses", "drAll", 2.0, None, 0),                     # Thick Skin: +2 % damage reduction a rank (inside drCap)
    ("Combat", 3, "r1a", "SkyyMobs", "drop", 2.0, None, 0),                         # Scavenger: +2 % a rank a kill drops 1 more item of its loot
    ("Combat", 3, "r1b", "SkyyMobs", "coins", 3.0, None, 0),                        # Coin Purse: 3 % a rank a kill pays coins = the mob's level
    ("Combat", 3, "r3b", "SkyyMobs", "rare", 1.0, None, 0),                         # Rare Drop: +1 % a rank 1 more of the kill's rarest loot
    ("Combat", 3, "r4a", "SkyyMobs", "bossRoll", 3.0, None, 0),                     # Boss Hunter: +3 % a rank a boss / mini boss drops its loot again
    ("Combat", 3, "r5a", "SkyyMobs", "dbl", 2.0, None, 0),                          # Lucky Kill: 2 % a rank a kill drops its whole loot twice
    # ---------------- Balance P8c (2026-10-22, research/Balance-P8-Rebirth-Spec.md 4.4; SkyyPets 0.4.9, SkyySkills 0.4.60, SkyyTrees 0.4.7):
    # the Beastmastery tree (points = the Beastmastery skill level). SkyyPets applies every row: petxp.<kind> = more XP for that kind of pet
    # (combat / mining / green = Farming and Foraging pets / all), petsyn.<kind> = that kind of pet's stats + x % (the Mining tree's Pet
    # Synergy rule; rare = pets of Rare rarity or better; all = every pet). Budgets per pet kind (check()): pet XP <= TREE_XP_MAX 30 %, pet stats
    # <= 15 %. P8c fixer: docs/answered/skills.md 2026-10-16 BEASTMASTERY GLOBAL NODE (Skyy: "actually, do add the +% global power at the
    # bottom") = the bottom capstone Kinship of the Wild's "all equipped pets gain +x % all stats" part, live as petsyn.all +3 % (its extra pet
    # slot stays coming soon); Gentle Giant 2.5 -> 1 % a rank so every kind stays at 15 % (4 + 6 + 2 + 3).
    ("Beastmastery", 1, "r1a", "SkyyPets", "petxp.combat", 0.006, None, 0),         # Whistle Training: +0.6 % Combat pet XP a rank (was +2 flat)
    ("Beastmastery", 1, "r1b", "SkyyPets", "petxp.combat", 0.03, None, 0),          # Fang Familiar: +3 % Combat pet XP a rank
    ("Beastmastery", 1, "r3a", "SkyyPets", "petsyn.combat", 0.01, None, 0),         # Battle Bond: +1 % all stats from Combat pets a rank
    ("Beastmastery", 1, "r4b", "SkyyPets", "petxp.combat", 0.04, None, 0),          # Fang Tempering: +4 % Combat pet XP a rank
    ("Beastmastery", 1, "r5a", "SkyyPets", "petsyn.combat", 0.02, None, 0),         # Predator's Gift: +2 % all stats from Combat pets a rank
    ("Beastmastery", 1, "r5b", "SkyyPets", "petxp.all", 0.02, None, 0),             # Rapid Learner: +2 % XP for every pet a rank
    ("Beastmastery", 2, "r1a", "SkyyPets", "petxp.mining", 0.024, None, 0),         # Digger's Calling: +2.4 % Mining pet XP a rank (was 3: budget)
    ("Beastmastery", 2, "r3a", "SkyyPets", "petsyn.mining", 0.01, None, 0),         # Stone Bond: +1 % all stats from Mining pets a rank
    ("Beastmastery", 2, "r4b", "SkyyPets", "petxp.mining", 0.04, None, 0),          # Deep Tempering: +4 % Mining pet XP a rank
    ("Beastmastery", 2, "r5a", "SkyyPets", "petsyn.mining", 0.02, None, 0),         # Earthen Gift: +2 % all stats from Mining pets a rank
    ("Beastmastery", 3, "r1a", "SkyyPets", "petxp.green", 0.024, None, 0),          # Green Companion: +2.4 % Farming / Foraging pet XP a rank
    ("Beastmastery", 3, "r3a", "SkyyPets", "petsyn.farming", 0.01, None, 0),        # Verdant Bond: +1 % all stats from Farming pets a rank
    ("Beastmastery", 3, "r3b", "SkyyPets", "petsyn.foraging", 0.01, None, 0),       # Wild Bond: +1 % all stats from Foraging pets a rank
    ("Beastmastery", 3, "r4b", "SkyyPets", "petxp.green", 0.04, None, 0),           # Roots Tempering: +4 % Farming / Foraging pet XP a rank
    ("Beastmastery", 3, "r5a", "SkyyPets", "petsyn.green", 0.02, None, 0),          # Nature's Gift: +2 % all stats from Farming and Foraging pets
    ("Beastmastery", 3, "r5b", "SkyyPets", "petsyn.rare", 0.01, None, 0),           # Gentle Giant: +1 % all stats of Rare or better pets a rank (fixer: was 2.5, room for Kinship)
    ("Beastmastery", 3, "r6", "SkyyPets", "petsyn.all", 0.03, None, 0),             # Kinship of the Wild (capstone): +3 % all stats of every pet - Skyy's "+% global power at the bottom"
    # P8c fixer 2: docs/answered/pets.md 2026-10-16 (LOCKED, Skyy: "the hatchery has limited slots (upgradable in beast masters skill tree")
    # -> Gentle Hand (was "+3% pet happiness/rank" - no happiness system) = +1 Hatchery slot a rank, 3 ranks (SkyyPets PetHatchery.extra:
    # pets.hatch.slots 2 + this + pets:hatch:slots:<uuid>, at most 10 extra / 12 slots)
    ("Beastmastery", 3, "r1b", "SkyyPets", "hatch", 1.0, None, 0),                  # Gentle Hand: +1 Hatchery slot a rank
    # ---------------- Balance P8d (2026-10-22, research/Balance-P8-Rebirth-Spec.md 4.5; SkyyTrees 0.4.8): the useful + light trees. Only
    # SkyyTrees' OWN TreeSk rows (no applier mod rebuilt); the 0.3 node aliases are in tools/trees_v3_data.py P8D_OLD. New own effects:
    # stam = flat max Stamina (skyytree_stamina), dodge.acrobatics = SkyySkills' dodge push (skill:bonus, fraction; SkyySkills clamps the
    # tree part at acro.treeDodgeMax 0.25). See P8D NUMBERS below.
    ("Farming", 1, "r1b", "SkyyTrees", "spd", 1.0, None, 0),                        # Quick Scythe: +1 % move speed a rank (crops break in one hit)
    ("Farming", 1, "r4b", "SkyyTrees", "dd.farming", 0.009, None, 0),               # Bumper Crop: +0.9 Farming Fortune a rank (Farming tree 37.2 -> 39.9)
    ("Cooking", 1, "r4a", "SkyyTrees", "hpp", 0.01, None, 0),                       # Comfort Food: +1 % max Health a rank (always on)
    ("Alchemy", 3, "r1a", "SkyyTrees", "hpp", 0.01, None, 0),                       # Resist Tonic: +1 % max Health a rank
    ("Smithing", 1, "r1a", "SkyyTrees", "xp.smithing", 0.02, None, 0),              # Steady Strikes: +2 % Smithing XP a rank (was the dead Smithing.SQuick alias)
    ("Acrobatics", 1, "r3b", "SkyyTrees", "dodge.acrobatics", 0.02, None, 0),       # Combat Flip: +2 % dodge push a rank
    ("Acrobatics", 1, "r3c", "SkyyTrees", "spd", 1.0, None, 0),                     # Gear Resonance: +1 % move speed a rank
    ("Acrobatics", 2, "r1a", "SkyyTrees", "spd", 1.0, None, 0),                     # Adrenaline: +1 % move speed a rank (at any Health)
    ("Acrobatics", 2, "r2b", "SkyyTrees", "fall", 0.02, None, 0),                   # Steady Land: -2 % fall damage a rank
    ("Acrobatics", 2, "r3b", "SkyyTrees", "dodge.acrobatics", 0.02, None, 0),       # Evade Master: +2 % dodge push a rank
    ("Acrobatics", 2, "r3c", "SkyyTrees", "fall", 0.03, None, 0),                   # Fearless: -3 % fall damage a rank (at any Health)
    ("Exploration", 1, "r1b", "SkyyTrees", "stam", 0.3, None, 0),                   # Trail Mix: +0.3 max Stamina a rank (3 % of the base 10)
    ("Exploration", 2, "r2b", "SkyyTrees", "fall", 0.05, None, 0),                  # Safe Landing: -5 % fall damage a rank
    # ---------------- Balance P7b (2026-10-22, SkyyExploration 0.3.3 + SkyyTrees 0.4.9): Skyy's popup "Keep the no-boost rule (Recommended)"
    # (docs/answered/skills.md 2026-10-22): Wanderer + Cartographer get NON-XP effects - Loot Bag / supply drop COINS only (SkyyExploration's
    # LgCore.loot). lg.coins = + x % of every Loot Bag / supply drop coin roll; lg.coin2 = x chance a claim holds one more coin roll. Never XP,
    # never more bags (a bag pays Exploration XP). Size (tools/balance_model.py --econ): luggage ~10 % of an exploring hour's coins (spec 2.3),
    # x1.2 x 1.15 at max = +3.8 % of that hour - inside the "other 6 %" budget's slack.
    ("Exploration", 1, "r1a", "SkyyExploration", "lg.coins", 0.04, None, 0),        # Wanderer: +4 % Loot Bag + supply drop coins a rank (20 % at 5)
    ("Exploration", 1, "r3a", "SkyyExploration", "lg.coin2", 0.05, None, 0),        # Cartographer: +5 % a rank a claim holds a second coin find (15 % at 3)
    # ---------------- 0.6.0 COMBAT INTO CLASS (research/Combat-Into-Class-Spec.md 3.2; SkyyTrees 0.6.0 + SkyyClasses 0.1.47 + SkyySkills
    # 0.4.64): the Combat tree's four never-wired nodes, now in every class's Weaponcraft branch (keys unchanged; trees_v3_data C060_COMBAT).
    # Reprisal + Edge of the Legend add to damage INSIDE SkyyClasses' class-tree damage cap; Second Wind / Rally are healing (no max Health).
    ("Combat", 2, "r3b", "SkyyClasses", "thorns", 3.0, None, 0),                    # Reprisal: 3 % of the melee damage taken dealt back a rank
    ("Combat", 2, "r3c", "SkyyClasses", "lowHeal", 5.0, None, 0),                   # Second Wind: once a fight, below 20 % Health heal 5 % of max a rank
    ("Combat", 1, "r6", "SkyyClasses", "dmgLow", 10.0, None, 0),                    # Edge of the Legend (capstone): +10 % vs enemies below 30 % Health
    ("Combat", 2, "r4b", "SkyySkills", "hpregen", 3.0, None, 0),                    # Rally: +3 % out-of-combat Health regen a rank (SkyySkills HpRegen)
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

# BALANCE P8b NUMBERS (builder 2026-10-22, the spec's section 4.2 table; Skyy "just go with the recommended on all of them"):
#   every number is the spec's except these, each held by a budget the spec itself sets (4.1, proved by check()) or by this round's mods:
#   Toughness   spec "+2 % max Health/rank" x 5 = 10 % + Accessory Plates' 7.5 % = 17.5 % from the Combat tree > the 10 % Health budget ->
#               +0.5 % a rank (2.5 % at rank 5; Combat tree Health = 10.0).
#   Miner's Fortune spec "+1 % gem drop chance/rank" = 50 x Gem Eye's own step (3 MGems levels x 0.02 % = 0.06 % a rank; the live Gem Eye
#               text said "+2 %", fixed in trees_v3_data.py) -> Gem Eye's step, +0.06 % a rank per block (Mining gems x2 with both maxed).
#   Rare Drop   the gear-bag rarity roll is SkyyGear's (not in this round) -> SkyyMobs' own roll: 1 more of the kill's rarest drop-list item.
#   Hardened Edge / Combat Focus  the spec's "SkyyGear dmg" -> SkyyClasses UpFx (SkyyGear is not in this round; UpFx keeps them inside
#               the class-tree damage cap dmgCap 40 together with the Combat fight rows).
#   SkyyMobs' loot rows never make gear: an extra roll skips every Weapon_ / Armor_ / Tool_ / Skyy_ item, so SkyyGear's UT meter (kills
#   of elites / mini bosses / dungeons) and Mythic roll (boss kills) see exactly the kills they saw before (SkyyMobs harness: 10,000 kills).
# BUDGETS (spec 4.1, check()): Fortune incl. extra-drop chance (1 % = 1 Fortune) <= TREE_FORT_MAX 40, XP <= TREE_XP_MAX 30 %, move speed
#   <= TREE_MOVE_MAX 10 %, max Health <= TREE_HP_MAX 10 % (TREE_HP_BY: Combat 13.75 %, wc15) - each per skill tree, every applier's rows + SkyyTrees' own rows + the 0.3 XP node
#   aliases (P8B_OLD_PER: the 0.3 node's per a level; SkyyTrees 0.4.6 asserts its defaults). Heartwood (Foraging b1 r1b, the 0.3 FFortune
#   alias, +6 double-log %) is NOT in the Fortune budget (P5 counted only Rich Seams; the spec's 37.5 -> 39.9 leaves it out) - P9 decides.

# BALANCE P8d NUMBERS (builder 2026-10-22, spec 4.5; Skyy "just go with the recommended on all of them"): every live row is a 4.1 kind,
#   inside the 4.1 budgets (check()): Farming Fortune 37.2 -> 39.9 (Bumper Crop 2.7 fills the gap; Bountiful Rows / Double Reap / the potion
#   crop rows are 0.3 node aliases, outside the budget as in P5 / P8b - P9 decides), XP Farming 25 / Cooking 23 / Alchemy 25 / Smithing 9 -> 17
#   (Fishing XP stays 0: every Fishing XP is a skill:fn:addxp grant), move Farming 3 / Acrobatics 6 / Exploration 7.5, max Health Cooking 3 /
#   Alchemy 3; the Acrobatics dodge rows 12 % of SkyySkills' 25 % tree-dodge clamp.
#   Kept coming soon (no system yet, Q4 / Q5): every active and its modifier rows (Sweep Harvest, Animal Call, Compost Boost, Flash Fry, Banquet,
#   Splash Mix, Mutagen Flask, Chum Cast, Quench, Field Repair, Roll, Scout Pulse, Waystone Recall), crop growth / golden / mutated crops,
#   animal products and breeding, pet happiness / feeding, food buff timers / healing, potion strength / duration / drink rows (no brew code
#   in the SET - the 4 dead Alchemy aliases of P8D_DROP too), stack / sack / carry rows, durability rows, the accessory / armor-tag rows of
#   mods outside this round, daily / hourly capstones, the Fishing rework rows (A:187 Q4: Sea Legs, Waterproof, Calm Waters, Pet Angler,
#   Rich Chum, Hook Line) and the Exploration XP rows Wanderer / Cartographer (Exploration XP takes no booster or tree bonus - Skyy's
#   locked answer, docs/plans/SkyyExploration-Plan.md Answers Q3 "No XP boosters for Exploration XP" + docs/handoff/design-locks.md:140;
#   the P8 spec 4.5 "-> SkyyExploration XP" conflicts with that locked answer, so these two stay coming soon).

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


def is_free(uid):
    """P8b: "r<row>.free" = the row's free perk (rank 1 while the row is open)"""
    return uid.endswith(".free")


def up(tree, branch, uid):
    """the trees_v3_data upgrade dict of a row (KeyError / AssertionError when the table changed); P8b: a free perk -> {name, max 1, hook}"""
    t = V3D.tree(tree)
    assert t["kind"] == "skill", tree
    if is_free(uid):
        for r in t["branches"][branch - 1]["rows"]:
            if "r%d.free" % r["r"] == uid and r["free"] is not None:
                return {"id": uid, "name": r["free"]["name"], "max": 1, "hook": r["free"]["hook"], "text": r["free"]["text"]}
        raise KeyError(key(tree, branch, uid))
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
# Balance P5 (research/Balance-P5-Power-Spec.md 7.1): SkyyTrees' OWN Fortune node counts in the same budget - (tree, branch, id, effect,
# per rank in effect units; the rank max comes from trees_v3_data). Rich Seams = the 0.3 node Mining.MFortune (SkyyTrees' trees.properties
# nodes.Mining[MFortune.per], 0.025 = +2.5 a rank since SkyyTrees 0.4.5; was 0.1 = +10, outside the budget): 3 ranks = 7.5.
TREE_OWN_FORT = [("Mining", 1, "r1b", "dd.mining", 0.025)]
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
    """a flat-points effect (no %): max Health, max Stamina (R3c); P8b: Vein Burst ore, Tree Feller logs"""
    return eff in ("hp", "stam", "vein", "feller", "hatch")   # P8c fixer 2: + Hatchery slots (P8d: SkyyTrees' own stam rows too)


def unit(eff):
    """display unit: fractions (Fortune / XP / Breaking Power / synergy / chances) show x100 as %, SkyyGear stats are whole % already"""
    return 100.0 if (eff[:3] in ("dd.", "xp.", "bp.") or eff.startswith(("petsyn.", "petxp.", "gem.", "coins.", "extra.", "dodge.", "lg.")) or eff in ("class.xp", "cook.ingr", "hpp", "fall", "hatchspd")) else 1.0   # P7b: + lg.


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


_EW = {"thorns": "Thorns", "lowHeal": "Heal", "hpregen": "Regen", "hp": "Health", "hpp": "Health", "dd": "Fortune", "xp": "XP", "bp": "Power", "dmg": "Damage", "cc": "Crit", "cd": "Crit Dmg", "petsyn": "Boost", "class": "XP", "cook": "Chance",
       "spd": "Speed", "stam": "Stamina",
       # P8b
       "vein": "Ore", "feller": "Logs", "fall": "Fall", "gem": "Gems", "coins": "Coins", "extra": "Extra", "dmgLow": "Damage", "dmgBoss": "Damage",
       "drAll": "Guard", "kbRes": "Steady", "drop": "Drop", "rare": "Rare", "bossRoll": "Boss", "dbl": "Double",
       # P8c
       "petxp": "Pet XP", "hatch": "Slots", "hatchspd": "Hatch time cut",   # hatchspd: r062_apply (Warm Nest); fixer: "Hatch" alone did not say it is a time cut
       # P8d
       "dodge": "Dodge",
       # P7b (SkyyExploration)
       "lg": "Coins"}


def _scale_words(e):
    sc = e[6]
    if sc is None:
        return "(row perk)" if is_free(e[2]) else "a rank"
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
                                                                     "cook.ingr": "double ingredient chance", "hp": "max Health", "hpp": "max Health",
                                                                     "spd": "move Speed", "stam": "max Stamina",
                                                                     # P8b
                                                                     "vein": "Vein Burst ore", "feller": "Tree Feller logs",
                                                                     "fall": "less fall damage", "gem.mining": "gem chance a block",
                                                                     "coins.mining": "chance an ore pays coins",
                                                                     "extra.foraging": "chance a log drops again", "dmgLow": "damage vs low Health",
                                                                     "dmgBoss": "damage vs bosses", "drAll": "damage reduction",
                                                                     "kbRes": "knockback resistance", "drop": "chance of 1 more loot item",
                                                                     "coins": "chance a kill pays coins", "rare": "chance of 1 more rarest item",
                                                                     "bossRoll": "chance a boss drops loot again", "dbl": "chance of double loot",
                                                                     # P8c (the Beastmastery tree, SkyyPets)
                                                                     "petxp.combat": "Combat pet XP", "petxp.mining": "Mining pet XP",
                                                                     "petxp.green": "Farming and Foraging pet XP", "petxp.all": "XP for every pet",
                                                                     "petsyn.combat": "Combat pet stats", "petsyn.farming": "Farming pet stats",
                                                                     "petsyn.foraging": "Foraging pet stats", "petsyn.green": "Farming and Foraging pet stats",
                                                                     "petsyn.rare": "stats of Rare or better pets", "petsyn.all": "stats of every pet",
                                                                     "hatch": "Hatchery slot",
                                                                     "hatchspd": "shorter egg hatch time",   # 0.6.2 / 0.4.17 (r062_apply: Warm Nest)
                                                                     # 0.6.0 (Combat into Class: Reprisal, Second Wind, Rally)
                                                                     "thorns": "melee damage dealt back", "lowHeal": "max Health healed once a fight below 20 %",
                                                                     "hpregen": "out-of-combat Health regen",
                                                                     # P8d (SkyyTrees' own Acrobatics rows)
                                                                     "dodge.acrobatics": "dodge push",
                                                                     # P7b (SkyyExploration's Loot Bag / supply drop coins)
                                                                     "lg.coins": "Loot Bag + supply drop coins",
                                                                     "lg.coin2": "chance of a second coin find"}[eff]
    return "+%s%s %s %s" % (_n(e[5] * unit(eff)), "" if flat(eff) else " %", what, _scale_words(e))


WHERE = {"SkyyPets": "Pets -> Skill trees", "SkyyGear": "Gear -> Stats", "SkyyAccessories": "Void Charms -> Skill trees",
         "SkyyTrees": "Trees -> Skill trees", "SkyyClasses": "Classes -> Abilities", "SkyyMobs": "Mobs -> Skill trees",
         "SkyyExploration": "Exploration -> Skill trees"}   # Server Setup place (P8b: + 3; P7b: + SkyyExploration)
FILE_OF = {"SkyyTrees": "tree-effects.properties"}   # P8b: SkyyTrees' own trees.properties is its main file - its rows live beside it


def fname(applier):
    """P8b: the file of an applier's rows (Skyy_<Mod>/<file>)"""
    return FILE_OF.get(applier, "trees.properties")


def cfg_text(applier, where=None):
    where = where or WHERE[applier]
    """Skyy_<Mod>/trees.properties (plain ASCII): <ckey>.per = one rank's value, <ckey>.max = the ceiling, both in % (display units)"""
    L = ["# %s - Skill Trees 3 rows (tools/trees_v3_effects.py). Change them in game: SkyWynn Menu -> Server Setup ->" % applier,
         "# %s (Advanced), or edit here and press Reload there. The ranks come from SkyyTrees (/tree). Numbers are in %%:" % where,
         "# <row>.per = what one rank gives (x the tool tier / armor pieces / accessories / pet rarity bonus the row names),",
         "# <row>.max = the most that row ever adds. 0 = the row gives nothing." + (_flat_note(applier) if [e for e in rows(applier) if flat(e[4])] else "")]
    for e in rows(applier):
        _nm = up(e[0], e[1], e[2])["name"]
        L.append(("# %s: %s" % (_nm, describe(e))) if _nm.startswith(e[0] + " ") else ("# %s %s: %s" % (e[0], _nm, describe(e))))   # fixer: never "Combat Combat Focus"
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
    return " %s rows are in points, not %%." % " / ".join({"hp": "Health", "stam": "Stamina", "vein": "Vein Burst ore", "feller": "Tree Feller log", "hatch": "Hatchery slot"}[f] for f in fl)


def _flat_word(eff):
    return {"hp": "Health", "stam": "Stamina", "vein": "ore", "feller": "logs", "hatch": "slots"}[eff]


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
    m.append((r"""
public static String loadV3(java.nio.file.Path dir) {
  if (dir == null) return "@FN@: no folder (built-in numbers)";
  try {
    java.nio.file.Path f = dir.resolve("@FN@");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(dir, new java.nio.file.attribute.FileAttribute[0]);
      java.nio.file.Path tmp = dir.resolve("@FN@.tmp");
      java.nio.file.Files.write(tmp, V3_TEXT.getBytes("ISO-8859-1"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
    }
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(f, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
""" + sets + r"""    return "@FN@ read";
  } catch (Throwable t) {
    @WARN@("could not read @FN@ (the Skill Trees 3 rows keep their numbers): " + t);
    return "@FN@ could not be read";
  }
}""").replace("@WARN@", warn).replace("@FN@", fname(applier)))
    return m


def cfg_text_field(applier, where=None):
    import json
    return "public static final String V3_TEXT = %s;" % json.dumps(cfg_text(applier, where))


TREE_ROW_MODS = ("SkyyTrees", "SkyyClasses", "SkyyMobs")   # P8b fixer: the appliers whose Server Setup rows are pure skill-tree rows


def cfg_rows(applier, cls, file, cat):
    """the Server Setup rows (config kit tuples), two a row: per rank + the ceiling, bound to <cls>.V3P<i> / V3X<i> in <file>"""
    out = []
    for i, e in enumerate(rows(applier)):
        nm = up(e[0], e[1], e[2])["name"]
        ew = _EW[e[4].split(".")[0]]
        lab = "%s %s %s" % (e[0], nm, ew)
        if len(lab) > 33 or (applier in TREE_ROW_MODS and nm.startswith(e[0] + " ")):   # P8b fixer: never "Combat Combat Focus"
            lab = "%s %s" % (nm, ew)
        assert len(lab) <= 33, lab
        h1 = describe(e) + "."
        if len(h1) > 100:
            h1 = h1[:97] + "..."
        h2 = "Most %s %s ever adds (in %s), whatever the rank, gear or pet." % (e[0], nm, _flat_word(e[4]) if flat(e[4]) else "%")
        if applier in TREE_ROW_MODS:   # P8b fixer: the tree rows' own words (the Gear / Pets / Accessories rows keep theirs, byte for byte)
            h2 = ("Most %s gives (a flat %s perk, in %s)." % (nm, e[0], _flat_word(e[4]) if flat(e[4]) else "%")) if is_free(e[2]) else                  ("Most %s %s gives at its top rank (in %s)." % (e[0], nm, _flat_word(e[4]) if flat(e[4]) else "%"))
        assert len(h2) <= 100, h2
        per_word = " (perk)" if is_free(e[2]) else " a rank"   # P8b fixer: a free perk is flat (rank 1), not per rank
        out.append(("%s.per" % ckey(e), lab + per_word, cat, "dec", _n(e[5] * unit(e[4])), "0", str(PER_HI), "", "" if flat(e[4]) else "%", "live,adv", h1,
                    "field:%s.V3P%d@%s:%s.per" % (cls, i, file, ckey(e))))
        out.append(("%s.max" % ckey(e), lab + " most", cat, "dec", _n(vmax(e) * unit(e[4])), "0", str(MAX_HI), "", "" if flat(e[4]) else "%", "live,adv", h2,
                    "field:%s.V3X%d@%s:%s.max" % (cls, i, file, ckey(e))))
    for r in out:
        assert len(r[1]) <= 40 and len(r[10]) <= 100, r
    return out


def own_fort(sk):
    """Balance P5: the Fortune SkyyTrees' own nodes of one skill add at max rank (TREE_OWN_FORT, effect units)"""
    return sum(per * maxrank(t, b, uid) for t, b, uid, eff, per in TREE_OWN_FORT if eff == "dd." + sk)


def tree_fort(sk):
    """Balance P5: the whole tree Fortune of one skill at max (own nodes + every applier row's ceiling, effect units); P8b: + the extra-drop
    chance rows (extra.<skill>: 1 % a log drops again = 1 Fortune, spec 4.1)"""
    return own_fort(sk) + sum(vmax(e) for e in EFFECTS if e[4] in ("dd." + sk, "extra." + sk))


# ---------------------------------------------------------------------------------------------------- P8b BUDGETS (spec 4.1)
TREE_XP_MAX = 0.30      # the most XP % all rows of one skill tree add (fraction)
TREE_MOVE_MAX = 10.0    # the most move speed % one tree adds (whole %)
TREE_HP_MAX = 0.10      # the most max Health % one tree adds (fraction)
TREE_HP_BY = {"Combat": 0.1375}   # per-tree lifts of TREE_HP_MAX. Combat = Weaponcraft: Toughness 2.5 + Accessory Plates 11.25 (wc15 x1.5,
                                  # SkyyAccessories 0.5.33) - Skyy 2026-10-27 popup answer "Raise cap to 13.75%"; every other tree stays 10 %


def tree_hp_max(tree):
    """the max Health budget of one tree (fraction): TREE_HP_BY or TREE_HP_MAX"""
    return TREE_HP_BY.get(tree, TREE_HP_MAX)
P8B_OLD_PER = {"Mining.MWisdom": ("xp", 0.01), "Foraging.FWisdom": ("xp", 0.01), "Farming.AWisdom": ("xp", 0.01), "Cooking.CWisdom": ("xp", 0.01),
               "Alchemy.PWisdom": ("xp", 0.01), "Smithing.SWisdom": ("xp", 0.01), "Fishing.NWisdom": ("xp", 0.01)}   # the 0.3 XP nodes' per a level
SKILL_OF = {"Combat": "combat"}   # a tree's XP key (class.xp = the Combat tree's XP too)


def _sk(tree):
    return SKILL_OF.get(tree, tree.lower())


def own_xp(tree):
    """P8b: the XP fraction the 0.3 node aliases of one skill tree add at max rank"""
    t = V3D.tree(tree)
    s = 0.0
    for b in t["branches"]:
        for r in b["rows"]:
            for u in r["ups"]:
                h = u["hook"]
                if h and h[0] == "old" and h[1] in P8B_OLD_PER and P8B_OLD_PER[h[1]][0] == "xp":
                    s += u["max"] * h[2] * P8B_OLD_PER[h[1]][1]
    return s


def tree_xp(tree):
    """P8b: the whole XP % of one skill tree at max (fraction): applier + own rows (xp.<skill>, class.xp for Combat) + the node aliases"""
    sk = _sk(tree)
    return own_xp(tree) + sum(vmax(e) for e in EFFECTS if e[0] == tree and (e[4] == "xp." + sk or (tree == "Combat" and e[4] == "class.xp")))


def tree_move(tree):
    """P8b: the whole move speed % of one tree at max (whole %)"""
    return sum(vmax(e) for e in EFFECTS if e[0] == tree and e[4] == "spd")


def tree_hp(tree):
    """P8b: the whole max Health % of one tree at max (fraction; hpp rows)"""
    return sum(vmax(e) for e in EFFECTS if e[0] == tree and e[4] == "hpp")


# ---------------------------------------------------------------------------------------------------- P8c PET BUDGETS (spec 4.4)
TREE_PETSTAT_MAX = 0.15   # the most "+x % all stats from <kind> pets" the Beastmastery tree adds to one pet kind (the pets' 15 % power share)
PET_KINDS = ("combat", "mining", "farming", "foraging", "exploration")   # SkyyPets' pet skills (PetKind.skill, lower case)
PET_XP_KINDS = ("combat", "mining", "green", "all")                      # petxp.<k>: green = Farming + Foraging pets, all = every pet
PET_SYN_KINDS = ("combat", "mining", "farming", "foraging", "green", "rare", "all")   # petsyn.<k>: rare = Rare or better pets of any kind; all = every pet (fixer)
TREE_DODGE_MAX = 0.25     # P8d: SkyySkills acro.treeDodgeMax default - the most tree dodge push it applies (fraction)
P8D_TREES = V3D.P8D_TREES   # P8d: the seven useful + light trees of round P8d
HATCH_CUT_MAX = 0.25      # r062 (SkyyPets 0.4.17): the most the Beastmastery tree cuts egg hatch time by default (Warm Nest 4 x 5 % = 20 %)
HATCH_EXTRA_MAX = 10      # P8c fixer 2: SkyyPets PetHatchery.extra clamps the extra Hatchery slots to 10 (pets.hatch.slots 2 + 10 = MAX_SLOTS 12)


def _pet_match(k, pk):
    """P8c: does a petxp / petsyn suffix k apply to a pet of skill pk (lower case)? (rare = any kind - the rarity decides at run time)"""
    return k == pk or k in ("all", "rare") or (k == "green" and pk in ("farming", "foraging"))


def pet_xp(pk):
    """P8c: the most pet XP % (fraction) the Beastmastery tree gives one pet kind"""
    return sum(vmax(e) for e in EFFECTS if e[0] == "Beastmastery" and e[4].startswith("petxp.") and _pet_match(e[4][6:], pk))


def pet_stat(pk):
    """P8c: the most pet stat % (fraction) the Beastmastery tree gives one pet kind (a Rare+ pet: Gentle Giant included)"""
    return sum(vmax(e) for e in EFFECTS if e[0] == "Beastmastery" and e[4].startswith("petsyn.") and _pet_match(e[4][7:], pk))


def check():
    V3D.check()
    for t, b, uid, eff, per in TREE_OWN_FORT:
        assert up(t, b, uid)["hook"] == ("old", "Mining.MFortune", 1) and eff == "dd.mining" and per > 0, (t, b, uid)
    seen = set()
    for e in EFFECTS:
        tree, b, uid, mod, eff, per, scale, cap = e
        u = up(tree, b, uid)
        assert u["hook"] is None, ("R3b wires only coming-soon upgrades", e)
        assert mod in ("SkyyGear", "SkyyPets", "SkyyAccessories", "SkyySkills", "SkyyCooking", "SkyyFishing", "SkyyTrees", "SkyyClasses", "SkyyMobs", "SkyyExploration"), e   # P7b: + SkyyExploration
        assert not is_free(uid) or (scale is None and maxrank(tree, b, uid) == 1), ("P8b: a free perk row is flat, rank 1", e)
        assert (tree, b, uid, eff) not in seen, ("one row per effect", e)
        seen.add((tree, b, uid, eff))
        assert per > 0 and (scale is None) == (cap == 0), e
        assert scale is None or scale in ("tool", "acc", "weapon", "pick") or scale.startswith("armor:") or scale.startswith("pet:"), e
        assert scale not in ("weapon", "pick") or mod == "SkyyGear", ("R3c: only SkyyGear knows the held weapon / pick scales", e)
        assert len(set(m for (t2, b2, i2, m, _e, _p, _s, _c) in EFFECTS if (t2, b2, i2) == (tree, b, uid))) == 1, ("one applier per upgrade", e)
        assert "," not in key(tree, b, uid)
    # P8c: the Beastmastery tree is SkyyPets' (the Beastmastery skill exists since SkyySkills 0.4.60): pet XP / pet stat rows only, each
    # pet kind's budgets held (spec 4.4: pet XP <= TREE_XP_MAX per kind, pet stats <= TREE_PETSTAT_MAX per kind)
    assert all(e[3] == "SkyyPets" and (e[4].startswith(("petxp.", "petsyn.")) or e[4] in ("hatch", "hatchspd")) and e[6] is None for e in EFFECTS if e[0] == "Beastmastery"), "P8c: Beastmastery = SkyyPets pet rows (r062: + hatchspd)"
    # r062 (SkyyPets 0.4.17): the hatch time cut rows - Beastmastery only, inside the budget (SkyyPets clamps the live sum at 90 % too)
    assert all(e[0] == "Beastmastery" and e[3] == "SkyyPets" and e[6] is None for e in EFFECTS if e[4] == "hatchspd"), "r062: hatchspd rows"
    assert sum(vmax(e) for e in EFFECTS if e[4] == "hatchspd") <= HATCH_CUT_MAX + 1e-9, "r062: hatch time cut over its budget"
    # P8c fixer 2: the Hatchery slot row(s) - Beastmastery only, whole slots, inside the extra-slot clamp
    assert all(e[0] == "Beastmastery" and e[5] == int(e[5]) for e in EFFECTS if e[4] == "hatch"), "P8c: hatch rows"
    assert sum(vmax(e) for e in EFFECTS if e[4] == "hatch") <= HATCH_EXTRA_MAX, "P8c: Hatchery slots over the clamp"
    assert not [e for e in EFFECTS if e[4].startswith("petxp.") and (e[0] != "Beastmastery" or e[4][6:] not in PET_XP_KINDS)], "P8c: petxp.<kind> rows"
    assert not [e for e in EFFECTS if e[4].startswith("petsyn.") and e[4][7:] not in PET_SYN_KINDS], "P8c: petsyn.<kind> rows"
    for pk in PET_KINDS:
        assert pet_xp(pk) <= TREE_XP_MAX + 1e-9, ("Beastmastery pet XP budget", pk, pet_xp(pk))
        assert pet_stat(pk) <= TREE_PETSTAT_MAX + 1e-9, ("Beastmastery pet stat budget", pk, pet_stat(pk))
    assert not [e for e in EFFECTS if e[0] == "Exploration" and e[4].startswith("xp.")], "Exploration never gets XP bonuses (Skyy, SkyySkills rule)"
    # the ceilings: every VMAX names a row; the tree Fortune rows of one skill add at most TREE_FORT_MAX together; no non-pet Fortune row over
    # ROW_FORT_MAX; a pet row never above its x1.5 value
    names = set((e[0], e[1], e[2], e[4]) for e in EFFECTS)
    assert all(k in names for k in VMAX), [k for k in VMAX if k not in names]
    for sk in set(e[4].split(".", 1)[1] for e in EFFECTS if e[4].startswith(("dd.", "extra."))):
        tot = tree_fort(sk)
        assert tot <= TREE_FORT_MAX + 1e-9, ("tree Fortune budget", sk, tot)
    # P8b: the XP / move / Health budgets of every skill tree (spec 4.1)
    for t in V3D.TREES:
        if t["kind"] != "skill":
            continue
        assert tree_xp(t["name"]) <= TREE_XP_MAX + 1e-9, ("tree XP budget", t["name"], tree_xp(t["name"]))
        assert tree_move(t["name"]) <= TREE_MOVE_MAX + 1e-9, ("tree move budget", t["name"], tree_move(t["name"]))
        assert tree_hp(t["name"]) <= tree_hp_max(t["name"]) + 1e-9, ("tree Health budget", t["name"], tree_hp(t["name"]))
    assert not [e for e in EFFECTS if e[4] in ("vein", "feller", "fall", "gem.mining", "coins.mining", "extra.foraging") and e[3] != "SkyyTrees"], "P8b: SkyyTrees' own effects"
    # P8d: the dodge rows are SkyyTrees' own Acrobatics rows, inside SkyySkills' tree-dodge clamp; every SkyyTrees own effect is one TreeSk
    # applies (xp. / dd. / dodge. through skill:bonus, spd / fall through the movement source, hpp / stam as stat modifiers, the gather rolls)
    assert not [e for e in EFFECTS if e[4].startswith("dodge.") and (e[3] != "SkyyTrees" or e[4] != "dodge.acrobatics")], "P8d: dodge rows"
    assert sum(vmax(e) for e in EFFECTS if e[4] == "dodge.acrobatics") <= TREE_DODGE_MAX + 1e-9, "P8d: tree dodge over SkyySkills' clamp"
    _own = ("spd", "fall", "hpp", "stam", "vein", "feller", "gem.mining", "coins.mining", "extra.foraging", "dodge.acrobatics")
    assert not [e for e in EFFECTS if e[3] == "SkyyTrees" and not (e[4] in _own or e[4].startswith(("xp.", "dd.")))], "P8d: an own effect TreeSk does not apply"
    assert not [e for e in EFFECTS if e[4] in ("dmgLow", "dmgBoss", "drAll", "kbRes") and e[3] != "SkyyClasses"], "P8b: SkyyClasses' fight rows"
    assert not [e for e in EFFECTS if e[4] in ("thorns", "lowHeal") and e[3] != "SkyyClasses"], "0.6.0: Reprisal / Second Wind are SkyyClasses'"
    assert [(e[0], e[2]) for e in EFFECTS if e[4] == "hpregen"] == [("Combat", "r4b")] and all(e[3] == "SkyySkills" for e in EFFECTS if e[4] == "hpregen"), "0.6.0: Rally"
    assert not [e for e in EFFECTS if e[4] in ("drop", "coins", "rare", "bossRoll", "dbl") and e[3] != "SkyyMobs"], "P8b: SkyyMobs' loot rows"
    # P7b: SkyyExploration applies only its two coin rows (the Exploration tree, never XP: Skyy's no-boost rule)
    assert [(e[0], e[4]) for e in EFFECTS if e[3] == "SkyyExploration"] == [("Exploration", "lg.coins"), ("Exploration", "lg.coin2")], "P7b: SkyyExploration's rows"
    assert not [e for e in EFFECTS if e[4].startswith("lg.") and (e[3] != "SkyyExploration" or e[6] is not None)], "P7b: lg. rows"
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

# ---------------------------------------------------------------------------------------------------- r062 (SkyyTrees 0.6.2 + SkyyPets 0.4.17)
# r062_apply() - ONLY those two builds call it (opt-in like trees_v3_data.v4_apply; every other build reads the table above unchanged):
#  1. BEASTMASTERY HATCHING (docs/answered/pets.md 2026-10-23, Skyy: "(in the beast master tree, have upgrades that speed up hatching and give
#     more hatchery slots too.)"): Warm Nest (Wild Roots r2c) "hatchspd" = a fraction cut off every Hatchery egg's wait (5 % a rank, 4 ranks =
#     20 %; HATCH_CUT_MAX 25 %) and Burrow Nursery (Deep Burrow r4c) "hatch" = +1 Hatchery slot a rank (2 ranks; SkyyPets sums every "hatch"
#     row: Gentle Hand 3 + 2 = 5 extra, inside HATCH_EXTRA_MAX 10). Recommended defaults - research/balance/targets.md has no hatch target; a
#     Common egg 120 s -> 96 s, a Mythic 2 h -> 1 h 36 m at 20 %; the slot pair keeps the 12-slot ceiling out of reach of the tree alone.
#     APPENDED at the end: every older SkyyPets row keeps its index (V3P<i> / V3X<i> fields, trees.properties keys unchanged).
#  2. WEAPONCRAFT x1.5, PETS PART (docs/answered/classes.md 2026-10-23 CLASS TREE REBUILD BUILT: "Weaponcraft (old Combat) per-rank numbers to
#     be raised ~x1.5"): Pet Fang (Combat b3 r3a, every class tree's Weaponcraft row 3) damage 1 -> 1.5 % a rank (x1.5; ceiling 7.5 -> 11.25
#     at rank 5 with a x1.5 Mythic pet); class XP 2 -> 2.6 % a rank (x1.3: the Combat / class tree's XP budget TREE_XP_MAX 30 % with Battle
#     Insight's 10 % = 19.5 + 10 = 29.5 %; x1.5 = 32.5 % would break it). SkyyPets 0.4.17 moves trees.properties lines still on the old
#     defaults once (PetsMigW15).
R062_APPLIED = []
R062_ROWS = [("Beastmastery", 3, "r2c", "SkyyPets", "hatchspd", 0.05, None, 0),   # Warm Nest: -5 % egg hatch time a rank
             ("Beastmastery", 2, "r4c", "SkyyPets", "hatch", 1.0, None, 0)]       # Burrow Nursery: +1 Hatchery slot a rank
R062_FANG = {("Combat", 3, "r3a", "xp.combat"): (0.02, 0.026), ("Combat", 3, "r3a", "dmg"): (1, 1.5)}   # (old per rank, new per rank)


def r062_apply():
    """SkyyTrees 0.6.2 / SkyyPets 0.4.17 (once): the two Beastmastery hatching rows + Pet Fang's raised numbers. Returns True."""
    if R062_APPLIED:
        return True
    V3D.r062_apply()
    seen = set()
    for i, e in enumerate(EFFECTS):
        k = (e[0], e[1], e[2], e[4])
        if k in R062_FANG:
            assert e[3] == "SkyyPets" and e[5] == R062_FANG[k][0], ("r062: the Pet Fang row moved", e)
            EFFECTS[i] = tuple(e[:5]) + (R062_FANG[k][1],) + tuple(e[6:])
            seen.add(k)
    assert seen == set(R062_FANG), seen
    assert not [e for e in EFFECTS if (e[0], e[1], e[2]) in set(r[:3] for r in R062_ROWS)]
    EFFECTS.extend(R062_ROWS)
    R062_APPLIED.append(1)
    check()
    return True

if __name__ == "__main__":
    for m in ("SkyyGear", "SkyyPets", "SkyyAccessories", "SkyySkills", "SkyyCooking", "SkyyFishing", "SkyyTrees", "SkyyClasses", "SkyyMobs", "SkyyExploration"):
        print(m, reads_csv(m))
    for _t in ("Mining", "Foraging", "Combat") + P8D_TREES:
        print("%s: Fortune %.1f, XP %.1f %%, move %.1f %%, Health %.1f %%" % (_t, 100 * tree_fort(_t.lower()), 100 * tree_xp(_t), tree_move(_t), 100 * tree_hp(_t)))
    print("Beastmastery (P8c): " + "; ".join("%s pets XP %.1f %%, stats %.1f %%" % (_k, 100 * pet_xp(_k), 100 * pet_stat(_k)) for _k in PET_KINDS))
