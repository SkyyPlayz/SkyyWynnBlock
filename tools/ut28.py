"""ut28 - THE table of the first 28 Untiered (UT) items of Zones 1-5 (12 armor sets = 48 ids + 16 weapons; research/cloud/UT-28-Build-Sheet.md,
round ut28, SkyyGear 0.3.47). Pure Python, no game files read at import. One source for: SkyyGear's build patch (tools/gear_0_3_47_patch.py: the
ut / utfx / utpow rows, its 55 copies), tools/tier_tags.py (family "ut": the tag first in the flavour text), the harness and the later SkyyArmory
round (its 9 copies: owner "armory" rows below - their ids join SkyyGear's Untiered table now and stay unusable (GearUt.ok: the item must exist)
until SkyyArmory builds them).

Where answers go: Skyy's words on names / numbers -> docs/answered/gear.md; build steps -> RESUME.md queue. Names are zone lore (Skyy 2026-10-23
popup "Zone lore names"); every name is UNVERIFIED (Skyy may rename - change NAME / PIECES here, nothing else).

Decisions taken here (sheet "Questions for Skyy" defaults + the 0.3.47 build):
  - bands = the LIVE zone-end bands (docs/answered/gear.md 2026-10-22 "Move to zone end"): Z1 12-20, Z2 32-40, Z3 52-60, Z4 72-80, Z5 92-100
    (the sheet's 35-43 ... 95-103 were the pre-move alloy bands); the tier TAG = the zone's alloy (T3 Bronze, T6 Dusk, T9 Azurvane, T12 Cinder,
    T15 Lumen - gear.md 285 "UT = the zone's alloy").
  - grammar (sheet 1 + Q2 default): rows 18 Magma Lance / 19 Stormvent drop "pierce+1" (no reader for spear thrusts or crossbow bolts - pierce
    is SkyyArmory's staff / wand quick shot only; add it back when that engine exists); everything else as the sheet's utfx column.
  - looks (Skyy 2026-10-24 "vanilla first" + "since you made new bronze daggers, you can use these ones for a UT or a mythic."): every SkyyGear
    copy wears a VANILLA model (MODEL column) with the orange Untiered placeholder recolour of that model's own texture (built at build time,
    nothing vanilla committed). Weapon_Daggers_Bronze_Ancient -> row 24 Deepcave Shadow (UT, Assassin daggers; no Mythic slot on this sheet).
  - trade-off texts never name a number Server Setup can change (fix round ut28fix): tgtlow / tgtfull say "low / high Health"
    (utline.lowTarget / fullTarget), the aura says "nearby" (utline.auraReach); the exact values are in the tooltip's trick lines.
"""

ZONE_BAND = {1: (12, 20), 2: (32, 40), 3: (52, 60), 4: (72, 80), 5: (92, 100)}          # = SkyyGear UT_END (migrate39)
ZONE_ALLOY = {1: "Bronze", 2: "Dusk", 3: "Azurvane", 4: "Cinder", 5: "Lumen"}
SLOTS = ("Head", "Chest", "Hands", "Legs")
SMALL = ("Head", "Hands")          # S line = Head / Hands, M line = Chest / Legs (the Filing Cabinet pattern)

# ---- the 12 armor sets: (row, set word, set name, kind, zone, vanilla base set, (Head, Chest, Hands, Legs) piece words, body,
#      fixed S, fixed M, trade-off S, trade-off M)
ARMOR = [
    (1, "OasisWarden", "Oasis Warden's", "cloth", 2, "Armor_Cloth_Silk", ("Hood", "Robe", "Cuffs", "Skirt"), "mp def",
     "hp+4 def+2 mregen-8", "hp+6 def+3 mregen-12",
     "Oasis warden: +4% max Health and +2 Defense but 8% slower Mana regen per piece.",
     "Oasis warden: +6% max Health and +3 Defense but 12% slower Mana regen per piece."),
    (2, "ScarakStalker", "Scarak Stalker's", "light", 2, "Armor_Leather_Soft", ("Cap", "Vest", "Gloves", "Pants"), "cc cd",
     "back+8 cc+1 front-6", "back+12 cc+2 front-8",
     "Scarak stalker: backstabs +8% damage and +1% Crit Chance but hits from the front -6% per piece.",
     "Scarak stalker: backstabs +12% damage and +2% Crit Chance but hits from the front -8% per piece."),
    (3, "RedDuneSentinel", "Red Dune Sentinel", "heavy", 2, "Armor_Steel", ("Helm", "Plate", "Gauntlets", "Greaves"), "def mp",
     "mp+2 mregen+6 hp-3", "mp+3 mregen+10 hp-4 taken+2",
     "Red dune sentinel: +2 Magical Power and 6% faster Mana regen but 3% less max Health per piece.",
     "Red dune sentinel: +3 Magical Power and 10% faster Mana regen but 4% less max Health and 2% more damage taken."),
    (4, "EverfrostWanderer", "Everfrost Wanderer's", "cloth", 3, "Armor_Cloth_Linen", ("Hood", "Shroud", "Wraps", "Hem"), "mp",
     "spd+1 mp+2 hp-4", "spd+2 mp+3 hp-6",
     "Everfrost wanderer: +1 Speed and +2 Magical Power but 4% less max Health per piece.",
     "Everfrost wanderer: +2 Speed and +3 Magical Power but 6% less max Health per piece."),
    (5, "YetiHunter", "Yeti Hunter's", "light", 3, "Armor_Leather_Light", ("Cap", "Vest", "Gloves", "Chaps"), "cc cd",
     "lsteal+1 cc+1 hprp-4 taken+2", "lsteal+2 cc+1 hprp-6 taken+3",
     "Yeti hunter: +1% Life Steal and +1% Crit Chance but 4% less Health Regen and 2% more damage taken.",
     "Yeti hunter: +2% Life Steal and +1% Crit Chance but 6% less Health Regen and 3% more damage taken."),
    (6, "GlacierBulwark", "Glacier Bulwark", "heavy", 3, "Armor_Cobalt", ("Helm", "Plate", "Gauntlets", "Greaves"), "def",
     "taken-3 spd-1", "taken-5 spd-2 stam-1",
     "Glacier bulwark: take 3% less damage per piece but you move slower (-1 Speed).",
     "Glacier bulwark: take 5% less damage per piece but you move slower (-2 Speed and -1 Stamina Regen)."),
    (7, "GhostGroveMystic", "Ghost Grove Mystic's", "cloth", 4, "Armor_Cloth_Cindercloth", ("Hood", "Robe", "Cuffs", "Skirt"), "mp stam",
     "dmg+5 mregen-10", "dmg+5 mregen-10",
     "Ghost grove mystic: +5% damage per piece but 10% slower Mana regen per piece.",
     "Ghost grove mystic: +5% damage per piece but 10% slower Mana regen per piece."),
    (8, "GeyserRunner", "Geyser Runner's", "light", 4, "Armor_Leather_Heavy", ("Hat", "Duster", "Gloves", "Boots"), "cc",
     "spd+2 stam+1 dmg-1", "spd+3 stam+1 dmg-2 hp-2",
     "Geyser runner: +2 Speed and +1 Stamina Regen but 1% less damage per piece.",
     "Geyser runner: +3 Speed and +1 Stamina Regen but 2% less damage and 2% less max Health per piece."),
    (9, "CalderaGuard", "Caldera Guard", "heavy", 4, "Armor_Adamantite", ("Helm", "Plate", "Gauntlets", "Greaves"), "def",
     "def+3 hprp+4 spd-1 lowtaken+6", "def+5 hprp+6 spd-1 lowtaken+10",
     "Caldera guard: +3 Defense and +4% Health Regen but -1 Speed and 6% more damage taken under half Health.",
     "Caldera guard: +5 Defense and +6% Health Regen but -1 Speed and 10% more damage taken under half Health."),
    (10, "FossilSeer", "Fossil Seer's", "cloth", 5, "Armor_Cloth_Silk", ("Cowl", "Mantle", "Sleeves", "Train"), "mp",
     "lowhp+6 mp+2 hp-4", "lowhp+10 mp+3 hp-6",
     "Fossil seer: +6% damage under half Health and +2 Magical Power but 4% less max Health per piece.",
     "Fossil seer: +10% damage under half Health and +3 Magical Power but 6% less max Health per piece."),
    (11, "Raptorhide", "Raptorhide", "light", 5, "Armor_Leather_Raven", ("Hood", "Coat", "Gloves", "Boots"), "cc cd",          # body + Crit Damage: "cc" alone left the Gloves under Fabled at the 600 % cap (the 0.3.36 Courier fix)
     "spd+2 stam+1 taken+2 hp-2", "spd+3 stam+2 taken+3 hp-3",
     "Raptorhide: +2 Speed and +1 Stamina Regen but 2% more damage taken and 2% less max Health per piece.",
     "Raptorhide: +3 Speed and +2 Stamina Regen but 3% more damage taken and 3% less max Health per piece."),
    (12, "LavaBastion", "Lava Lake Bastion", "heavy", 5, "Armor_Prisma", ("Helm", "Plate", "Gauntlets", "Greaves"), "def",
     "hp+5 def+2 taken-1 mregen-8 spd-1", "hp+7 def+4 taken-2 mregen-12 spd-1",
     "Lava bastion: +5% max Health +2 Defense and 1% less damage taken but 8% slower Mana regen and -1 Speed.",
     "Lava bastion: +7% max Health +4 Defense and 2% less damage taken but 12% slower Mana regen and -1 Speed."),
]

# ---- the 16 weapons: (row, id, name, kind word, class, zone, owner, base id (the copy's JSON / Armory's own item), model (vanilla look source),
#      body, fixed, trade-off)
WEAPONS = [
    (13, "Weapon_Longsword_UT_AzureArc", "The Azure Arc", "longsword", "Spellblade", 1, "gear", "Weapon_Longsword_Katana", "Weapon_Longsword_Katana",
     "str cc", "fAir+4 swing=slow", "Azure forest blade: +4% Air Damage. Swings at the slow tier (Momentum builds slower)."),
    (14, "Weapon_Spellbook_UT_SandscriptCodex", "The Sandscript Codex", "spellbook", "Mage", 2, "armory", "Weapon_Spellbook_Thorium",
     "Weapon_Spellbook_Grimoire_Purple", "mp cc", "mcost-25 dmg-20", "Spells cost 25% less Mana. 20% less damage."),
    (15, "Weapon_Fist_UT_SteppeWind", "Steppe Wind Wraps", "fist weapon", "Monk", 2, "armory", "Weapon_Fist_Wraps_Silk", "Weapon_Fist_Wraps_Silk",
     "str cc", "swing=fast dmg-8", "Swings one tier faster. 8% less damage."),
    (16, "Weapon_Kunai_UT_ScarakStinger", "Scarak Stinger", "kunai", "Assassin", 2, "armory", "Weapon_Kunai_Thorium", "Weapon_Kunai",
     "cc cd", "poison+12 dmg-20", "Every hit poisons (12% of the hit over the Poison time). 20% less damage."),
    (17, "Weapon_Wand_UT_HotspringBlessing", "Hotspring Blessing", "wand", "Priest", 3, "armory", "Weapon_Wand_Cobalt", "Weapon_Wand_Root",
     "mp hpr", "aura+50 dmg-25", "Your heal orb also heals nearby party members at 50%. 25% less damage."),
    (18, "Weapon_Spear_UT_MagmaLance", "Magma Lance", "spear", "Warrior", 4, "gear", "Weapon_Spear_Adamantite_Saurian",
     "Weapon_Spear_Adamantite_Saurian", "str cc", "dmg-25 fFire+3", "Magma-forged tip: +3% Fire Damage. 25% less damage."),
    (19, "Weapon_Crossbow_UT_Stormvent", "Stormvent", "crossbow", "Archer", 4, "gear", "Weapon_Crossbow_Ancient_Steel", "Weapon_Crossbow_Ancient_Steel",
     "str cc", "range+20 dmg-20 fThunder+3", "Steam-vent bolts: +3% Thunder Damage. Bolts past 20 blocks deal nothing. 20% less damage."),
    (20, "Weapon_Spellbook_UT_AshfallGrimoire", "Ashfall Grimoire", "spellbook", "Mage", 4, "armory", "Weapon_Spellbook_Adamantite",
     "Weapon_Spellbook_Demon", "mp cc", "dmg+20 mcost+30 fFire+3", "Hits 20% harder with +3% Fire Damage. Spells cost 30% more Mana."),
    (21, "Weapon_Fist_UT_EmberrootWraps", "Emberroot Wraps", "fist weapon", "Monk", 4, "armory", "Weapon_Fist_Wraps_Cindercloth",
     "Weapon_Fist_Wraps_Cindercloth", "str cc", "lsteal+4 dmg-20", "+4% Life Steal on every hit. 20% less damage."),
    (22, "Weapon_Sword_UT_Raptorfang", "Raptorfang", "sword", "Warrior", 5, "gear", "Weapon_Sword_Silversteel", "Weapon_Sword_Silversteel",
     "str cd", "tgtlow+50 tgtfull-25", "50% more damage to enemies at low Health. 25% less to enemies at high Health."),
    (23, "Weapon_Shortbow_UT_Bonewhistle", "Bonewhistle", "bow", "Archer", 5, "gear", "Weapon_Shortbow_Doomed", "Weapon_Shortbow_Doomed",
     "str cc", "tgtfull+60 tgtlow-15", "60% more damage to enemies at high Health. 15% less to enemies at low Health."),
    (24, "Weapon_Daggers_UT_DeepcaveShadow", "Deepcave Shadow", "daggers", "Assassin", 5, "gear", "Weapon_Daggers_Bronze_Ancient",
     "Weapon_Daggers_Bronze_Ancient", "cc cd", "back+80 front-50", "Backstabs deal 80% more damage. Hits from the front deal 50% less."),
    (25, "Weapon_Axe_UT_PrimalCleaver", "Primal Cleaver", "axe", "Berserker", 5, "gear", "Weapon_Axe_Bone", "Weapon_Axe_Bone",
     "str lsteal", "lowhp+50 lsteal+3 hp-12", "50% more damage under half Health and +3% Life Steal. 12% less max Health while held."),
    (26, "Weapon_Staff_UT_Stormfossil", "The Stormfossil", "staff", "Mage", 5, "armory", "Weapon_Staff_Mithril", "Weapon_Staff_Crystal_Purple",
     "mp cc", "pierce+1 taken+8 fThunder+3", "Quick shots pierce every enemy in a line with +3% Thunder Damage. You take 8% more damage while held."),
    (27, "Weapon_Wand_UT_Cavewind", "Cavewind", "wand", "Priest", 5, "armory", "Weapon_Wand_Mithril", "Weapon_Wand_Stoneskin",
     "mp cc", "dmg+25 heal-100 fAir+3", "Hits 25% harder with +3% Air Damage. Your heal orb heals nothing."),
    (28, "Weapon_Bo_UT_CrushingTail", "Crushing Tail", "bo staff", "Monk", 5, "armory", "Weapon_Bo_Mithril", "Weapon_Bo_Mithril",
     "str cc", "kb+150 boss-30 fAir+3", "Knocks enemies back 2.5x as far with +3% Air Damage. 30% less damage to bosses and mini bosses."),
]

# the new trick words (sheet section 4); SkyyGear reads tgtlow / tgtfull / boss / lowtaken, SkyyArmory reads mcost / aura through gear:fn:utfx
NEW_TRICKS = ("tgtlow", "tgtfull", "boss", "lowtaken", "mcost", "aura")
# downside sign per trick: +1 = a positive value is the DOWNSIDE (more damage taken, dearer spells), -1 = a negative value is
DOWN_IF_POS = ("taken", "lowtaken", "mcost", "range")


def armor_rows():
    """[(row, id, name, kind, zone, base id, body, fixed, trade-off, set word, slot)] - 48 rows, Head / Chest / Hands / Legs per set"""
    out = []
    for r in ARMOR:
        for k, sl in enumerate(SLOTS):
            small = sl in SMALL
            out.append((r[0], "Armor_UT_%s_%s" % (r[1], sl), "%s %s" % (r[2], r[6][k]), r[3], r[4], "%s_%s" % (r[5], sl), r[7],
                        r[8] if small else r[9], r[10] if small else r[11], r[1], sl))
    return out


def rows():
    """every id: (id, name, kind word, zone, owner, base id, model id, body, fixed, trade-off, row) - armor first, then weapons, sheet order"""
    out = []
    for a in armor_rows():
        out.append((a[1], a[2], "%s armor" % a[3], a[4], "gear", a[5], a[5], a[6], a[7], a[8], a[0]))
    for w in WEAPONS:
        out.append((w[1], w[2], w[3], w[5], w[6], w[7], w[8], w[9], w[10], w[11], w[0]))
    return out


IDS = [r[0] for r in rows()]
GEAR_IDS = [r[0] for r in rows() if r[4] == "gear"]
ARMORY_IDS = [r[0] for r in rows() if r[4] == "armory"]


def band(item_id):
    for r in rows():
        if r[0] == item_id:
            return ZONE_BAND[r[3]]
    return None


def check():
    """[] = fine, else the problems (the build and the harness assert it)"""
    bad = []
    rs = rows()
    if len(rs) != 64 or len(set(IDS)) != 64 or len(GEAR_IDS) != 55 or len(ARMORY_IDS) != 9:
        bad.append("counts %d / %d / %d / %d" % (len(rs), len(set(IDS)), len(GEAR_IDS), len(ARMORY_IDS)))
    if sorted(set(r[10] for r in rs)) != list(range(1, 29)):
        bad.append("rows are not 1-28")
    for r in rs:
        i, nm, kind, z, own, base, model, body, fixed, note = r[:10]
        if "_UT_" not in i or not i.isascii() or "=" in i or "," in i:
            bad.append("id " + i)
        if not body.split() or not fixed.split():
            bad.append("lines " + i)
        if not (len(note) <= 110 and note.isascii() and "," not in note and "=" not in note and note == note.strip()):
            bad.append("trade-off text " + i)
        if not (nm.isascii() and "," not in nm and "=" not in nm and 0 < len(nm) <= 40):
            bad.append("name " + i)
        if z not in ZONE_BAND or own not in ("gear", "armory"):
            bad.append("zone / owner " + i)
        up = down = 0
        for w in fixed.split():
            if w.startswith("swing="):
                (up, down) = (up + 1, down) if w == "swing=fast" or w == "swing=superfast" else (up, down + 1)
                continue
            j = max(w.rfind("+"), w.rfind("-"))
            k, n = w[:j], float(w[j:])
            neg = (n > 0) if k in DOWN_IF_POS else (n < 0)
            if k == "heal" and n <= -100:
                neg = True
            down += 1 if neg else 0
            up += 0 if neg else 1
        if not up or not down:
            bad.append("%s needs one upside and one downside (%s)" % (i, fixed))
    for w in WEAPONS:
        fam = w[1].split("_UT_")[0]
        if not w[7].startswith(fam + "_"):
            bad.append("%s: the base %s is not of the family %s" % (w[1], w[7], fam))
    for r in rs:          # fix round ut28fix: no editable threshold in a trade-off text (the trick lines show the live values)
        if any(w.startswith(("tgtlow", "tgtfull")) for w in r[8].split()) and ("half Health" in r[9] or "full Health" in r[9]):
            bad.append("trade-off text names a Server Setup threshold " + r[0])
        if any(w.startswith("aura") for w in r[8].split()) and "blocks" in r[9]:
            bad.append("trade-off text names the aura reach " + r[0])
    return bad


assert not check(), check()
