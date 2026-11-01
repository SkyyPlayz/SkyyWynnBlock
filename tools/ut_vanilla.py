"""ut_vanilla - THE table of the Untiered (UT) weapons made from UNUSED vanilla weapons (research/Vanilla-Gear-Audit.md sections 4, 6, 8.3; round gl1 =
SkyyGear 0.3.53). Pure Python, no game files read at import. One source for: SkyyGear's build patch (tools/gear_0_3_53_patch.py: the ut / utfx /
utpow rows, the copies, the bag-pool removal of the used looks), tools/tier_tags.py (family "ut": the zone's alloy tag first in the flavour text)
and the harness. Same row shape and rules as tools/ut28.py (bands = ut28.ZONE_BAND, tag = ut28.ZONE_ALLOY, ut28.check's grammar).

Where answers go: Skyy's words on names / numbers -> docs/answered/gear.md; build steps -> RESUME.md queue. Every NAME is UNVERIFIED (zone lore,
Skyy may rename - change NAME here, nothing else).

Skyy (docs/answered/gear.md 2026-10-30 VANILLA GEAR AUDIT): Q "UT / Mythic picks from unused vanilla weapons: Ancient Bronze Daggers + Sword = Z1 UT
(Assassin / Warrior), Doomed = Z2 UT family, Saurian = Z4, Scythe_Void = Berserker Mythic, Silversteel = Warrior UT Z3-4, Katana = Warrior Z2 drop.
OK?" -> "Yes, all of them (Recommended)".
Decisions taken here (builder defaults, UNVERIFIED until Skyy sees them):
  - looks: every copy = the vanilla model by path + the orange Untiered placeholder recolour of its own texture (SkyyGear 0.3.47's pipeline).
    Three looks are already worn by a 0.3.47 UT (Daggers_Bronze_Ancient = Deepcave Shadow Z5, Shortbow_Doomed = Bonewhistle Z5, Sword_Silversteel
    = Raptorfang Z5): the new copy gets the DARKER map (LO 0.2, the Fossil Seer rule) so the two stay apart. Spear_Adamantite_Saurian already IS
    the Z4 Saurian Warrior UT (Magma Lance, 0.3.47) - not doubled.
  - Doomed = one UT weapon per class (audit section 4): Berserker battleaxe, Warrior sword, Assassin fang daggers, Archer shortbow, Mage staff.
    The Mage staff is a SkyyArmory row (like every ut28 staff / wand / book: SkyySkills ships its own Weapon_Staff_Doomed file with the class
    Mana cost, so a SkyyGear copy of the vanilla JSON would cast at the wrong cost) - its rows join now and stay unusable (GearUt.ok: the item
    must exist) until SkyyArmory builds Weapon_Staff_UT_Doomcaller.
  - Saurian longsword = the Spellblade (longswords are the Spellblade's weapon, docs/answered/classes.md 2026-10-08 Arcblade).
  - Scythe_Void = Mythic through gear.mythicItems (MYTHIC below) - the 0.2.16 developer-bow rule (Mythic is bosses only; no source but
    /gear give until the boss round). Katana stays a normal Zone 2 bag drop (level.material Katana = Thorium's band).
  - SIGNATURES: no new engine work (sig3 / sig5 rounds). Each row names the signature it should get later (SIG_LATER); nothing of it is shown
    in game (gear.md 2026-10-03 "hide it instead of leaving a note in the text").
"""
import ut28 as _UT28

ZONE_BAND = _UT28.ZONE_BAND
ZONE_ALLOY = _UT28.ZONE_ALLOY
LO_SHARED = 0.2          # the darker recolour of a look a 0.3.47 UT already wears

# (row, id, name, kind word, class, zone, owner, base id, model (vanilla look), body, fixed, trade-off, recolour lo, signature later)
WEAPONS = [
    (1, "Weapon_Daggers_UT_BarrowFangs", "Barrow Fangs", "daggers", "Assassin", 1, "gear", "Weapon_Daggers_Bronze_Ancient",
     "Weapon_Daggers_Bronze_Ancient", "cc cd", "tgtfull+40 tgtlow-20",
     "Opening cuts: 40% more damage to enemies at high Health. 20% less to enemies at low Health.", LO_SHARED,
     "sig3: an opener dash that marks the target"),
    (2, "Weapon_Sword_UT_GrovewardenRelic", "Grovewarden's Relic", "sword", "Warrior", 1, "gear", "Weapon_Sword_Bronze_Ancient",
     "Weapon_Sword_Bronze_Ancient", "str cd", "boss+25 dmg-10",
     "Ancient grove blade: 25% more damage to bosses and mini bosses. 10% less damage.", 0.0,
     "sig3: a guard-break thrust"),
    (3, "Weapon_Battleaxe_UT_DuneReaver", "Dune Reaver", "battleaxe", "Berserker", 2, "gear", "Weapon_Battleaxe_Doomed",
     "Weapon_Battleaxe_Doomed", "str lsteal", "lowhp+40 taken+6",
     "Doomed edge: 40% more damage while under half Health. You take 6% more damage while held.", 0.0,
     "sig5: a cursed whirl"),
    (4, "Weapon_Sword_UT_DoomedOath", "Doomed Oath", "sword", "Warrior", 2, "gear", "Weapon_Sword_Doomed",
     "Weapon_Sword_Doomed", "str cd", "tgtlow+35 dmg-10",
     "Cursed finisher: 35% more damage to enemies at low Health. 10% less damage.", 0.0,
     "sig5: an execute strike"),
    (5, "Weapon_Daggers_UT_Dunefang", "Dunefang", "daggers", "Assassin", 2, "gear", "Weapon_Daggers_Fang_Doomed",
     "Weapon_Daggers_Fang_Doomed", "cc cd", "back+40 lsteal+2 front-25",
     "Backstabs deal 40% more damage and +2% Life Steal. Hits from the front deal 25% less.", 0.0,
     "sig5: a draining backstab"),
    (6, "Weapon_Shortbow_UT_Dreadstring", "Dreadstring", "bow", "Archer", 2, "gear", "Weapon_Shortbow_Doomed",
     "Weapon_Shortbow_Doomed", "str cc", "dmg+15 range+18",
     "Hits 15% harder - but arrows past 18 blocks deal nothing.", LO_SHARED,
     "sig5: a cursed volley"),
    (7, "Weapon_Staff_UT_Doomcaller", "Doomcaller", "staff", "Mage", 2, "armory", "Weapon_Staff_Thorium",
     "Weapon_Staff_Doomed", "mp cc", "dmg+20 hp-8",
     "Hits 20% harder. 8% less max Health while held.", 0.0,
     "sig5: a doom bolt (SkyyArmory builds the copy)"),
    (8, "Weapon_Sword_UT_Silverbrand", "Everfrost Silverbrand", "sword", "Warrior", 3, "gear", "Weapon_Sword_Silversteel",
     "Weapon_Sword_Silversteel", "str cd", "front+25 back-20",
     "Duelist's blade: hits from the front deal 25% more damage. Backstabs deal 20% less.", LO_SHARED,
     "sig3: a riposte"),
    (9, "Weapon_Daggers_UT_SaurianTalons", "Saurian Talons", "daggers", "Assassin", 4, "gear", "Weapon_Daggers_Adamantite_Saurian",
     "Weapon_Daggers_Adamantite_Saurian", "cc cd", "tgtlow+40 tgtfull-20 fFire+3",
     "Caldera hunter: +3% Fire Damage. 40% more damage to enemies at low Health and 20% less at high Health.", 0.0,
     "sig5: a pouncing rend"),
    (10, "Weapon_Longsword_UT_SaurianSpine", "Saurian Spine", "longsword", "Spellblade", 4, "gear", "Weapon_Longsword_Adamantite_Saurian",
     "Weapon_Longsword_Adamantite_Saurian", "str cc", "boss+25 dmg-15 fEarth+3",
     "Geyser-split blade: +3% Earth Damage and 25% more damage to bosses and mini bosses. 15% less damage.", 0.0,
     "sig5: an earth-splitting arc"),
]

# Mythic (boss gear) by gear.mythicItems - the vanilla id itself, never in random bags (GearUtFx.mythicId)
MYTHIC = [("Weapon_Battleaxe_Scythe_Void", "Berserker", "sig5: a void reap (Mythic signature)")]

# already a UT look since SkyyGear 0.3.47 (the existing row covers the pick): the vanilla id -> the UT copy that wears it
COVERED = {"Weapon_Spear_Adamantite_Saurian": "Weapon_Spear_UT_MagmaLance (Z4 Warrior, Saurian)"}


def rows():
    """every id: (id, name, kind word, zone, owner, base id, model id, body, fixed, trade-off, row) - the tools/ut28.py rows() shape"""
    return [(w[1], w[2], w[3], w[5], w[6], w[7], w[8], w[9], w[10], w[11], w[0]) for w in WEAPONS]


IDS = [r[0] for r in rows()]
GEAR_IDS = [r[0] for r in rows() if r[4] == "gear"]
ARMORY_IDS = [r[0] for r in rows() if r[4] == "armory"]
# the vanilla looks now worn by a SkyyGear UT copy: out of the random bags. An "armory" row's look stays IN the bags until SkyyArmory ships
# that copy (gl1fix: else Z2 Mage bags lose the Doomed staff while Doomcaller cannot drop either) - move the row's look here in that round.
LOOKS = sorted(set(w[8] for w in WEAPONS if w[6] == "gear"))
ARMORY_LOOKS = sorted(set(w[8] for w in WEAPONS if w[6] == "armory") - set(LOOKS))          # waiting for SkyyArmory: still in the bags
LO = dict((w[1], w[12]) for w in WEAPONS)
CLASS = dict((w[1], w[4]) for w in WEAPONS)
SIG_LATER = dict([(w[1], w[13]) for w in WEAPONS] + [(m[0], m[2]) for m in MYTHIC])


def band(item_id):
    for r in rows():
        if r[0] == item_id:
            return ZONE_BAND[r[3]]
    return None


def check():
    """[] = fine, else the problems (the build and the harness assert it): tools/ut28.py's rules + this table's own"""
    bad = []
    rs = rows()
    if len(rs) != 10 or len(set(IDS)) != 10 or len(GEAR_IDS) != 9 or len(ARMORY_IDS) != 1:
        bad.append("counts %d / %d / %d / %d" % (len(rs), len(set(IDS)), len(GEAR_IDS), len(ARMORY_IDS)))
    if set(IDS) & set(_UT28.IDS):
        bad.append("an id is already a ut28 id")
    if [w[0] for w in WEAPONS] != list(range(1, len(WEAPONS) + 1)):
        bad.append("rows are not 1-%d" % len(WEAPONS))
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
        if own == "gear" and base != model:
            bad.append("a SkyyGear copy is its look's JSON: " + i)
        up = down = 0
        for w in fixed.split():
            if w.startswith("swing="):
                (up, down) = (up + 1, down) if w in ("swing=fast", "swing=superfast") else (up, down + 1)
                continue
            j = max(w.rfind("+"), w.rfind("-"))
            k, n = w[:j], float(w[j:])
            neg = (n > 0) if k in _UT28.DOWN_IF_POS else (n < 0)
            down += 1 if neg else 0
            up += 0 if neg else 1
        if not up or not down:
            bad.append("%s needs one upside and one downside (%s)" % (i, fixed))
        if any(w.startswith(("tgtlow", "tgtfull")) for w in fixed.split()) and ("half Health" in note or "full Health" in note):
            bad.append("trade-off text names a Server Setup threshold " + i)
        fam = i.split("_UT_")[0]
        if not base.startswith(fam + "_") or not model.startswith(fam + "_"):
            bad.append("%s: the base %s / look %s is not of the family %s" % (i, base, model, fam))
    for w in WEAPONS:
        if w[12] not in (0.0, LO_SHARED) or not w[13]:
            bad.append("recolour / signature placeholder " + w[1])
    used28 = set(r[6] for r in _UT28.rows())
    for w in WEAPONS:
        if (w[8] in used28) != (w[12] == LO_SHARED):
            bad.append("%s: a look a 0.3.47 UT wears gets the darker map (and only those)" % w[1])
    if set(COVERED) & set(LOOKS) or not set(COVERED) <= used28:
        bad.append("COVERED")
    return bad


assert not check(), check()
