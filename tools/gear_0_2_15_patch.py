"""Derive SkyyGear/build_skyygear_0.2.15.py from the LIVE 0.2.14 (build_skyygear_0.2.14.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_14_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_15_patch.py      then      python SkyyGear/build_skyygear_0.2.15.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.15.py

0.2.15 = MINING ARMOR - the vanilla metal armor sets Copper..Onyxium are the green Mining Sets (research/cloud/Mining-Armor-Spec.md sections 2-7;
Skyy's answers docs/answered/gear.md 2026-10-08 / 2026-10-09, newest wins). Skyy's words: "lets still make the farming and gathering armor, but
use vanilla for mining, and armory for combat gear. that makes things easy!"; "yes, gathering armor uses the set label, the full set gives a little
bonus gathering fortune (mining foraging ect.) and the higher tiers can give a little more like mining /chopping speed, movement speed, ect.";
"We we are making the vanilla armor the mining gear so I'd do that first"; 2026-10-09 popup: "Mining gate -> Yes, Mining level; mining stats ->
Yes, tool in hand; old metal armor -> Leave as is; quest set base -> An Armory set after 0.7" (spec defaults kept: Mining Power now, full Health /
resistance now, helmet light by tier, metal armor out of random combat loot).
  1. THE 28 PIECES (Armor_<Copper|Iron|Thorium|Cobalt|Adamantite|Mithril|Onyxium>_<Head|Chest|Hands|Legs>, build-checked against Assets.zip:
     ArmorSlot, ISS_Armor_Heavy) are MINING ARMOR while garmor.miningOn (default on). Matched by EXACT id in code (GearMine.IDS) - no kind.prefix
     rows (a prefix row would also catch The Armory's Armor_Iron_<Slot>_<Colour> recolours) and no saved-data rewrite: the documents keep kind
     combat, so the armor box stays hidden and the Health / resistance lock stays enforced exactly as in 0.2.14; only the GATE changes, at read
     time: GearGate.check / GearView.gateLine use the gate skill Mining for these ids (old pieces too - Skyy "Mining level"), so a piece under your
     Mining level is inactive (no Health, no resistance, no mining lines, does not count for its set), and its tooltip says "Requires Mining N".
     Health / resistance = the level curve x garmor.miningShare (100 % = 0.2.14 exactly; Skyy may lower it after The Armory's Heavy sets).
  2. NEW PIECES: every new document of the 28 ids (crafts, native mob / chest drops, /gear give, gear:fn:grant) = rarity Set (green), identified,
     0 modifiers, level inside the material band, set field "mining_<tier>" (GearMine.doc via GearRoll.newDoc). Crafts are made at your MINING
     level (craftSkill / craftLabel = Mining), clamped into the band (Cobalt by Mining 12 = Lv 25 and inactive until Mining 25). A native mob /
     chest drop is an identified Set piece at the mob / chest level clamped into the band (GearTag.unid); never a mystery bag (GearUnid.fromItem,
     spread and gear:fn:box with the stack refuse them) and never in the bag pool (GearPool.table: bags, the unidentified roll, chest extras); the
     Heavy bag pool keeps Bronze / Steel / Heavy Leather. The Reforge modifier roll refuses a Set mining piece ("fixed mining lines"); Level up
     still works (Set cost). Craft Smithing XP of a Set mining piece = the Normal row (a Set row would pay 8x a Normal craft for plain metal armor).
     OLD PIECES (made before 0.2.15) are untouched (Skyy "Leave as is"): rarity, level and rolled combat modifiers stay and still count; they get
     the Mining gate, the mining lines and count for their tier's set BY ID (no document change). A piece whose document carries another set
     field (a quest / boss set) belongs only to that set.
  3. MINING LINES per piece (Server Setup -> Gear -> Gathering armor -> "Mining armor by tier": garmor.mining.<tier>=<Fortune Head Chest Legs Hands>,
     <Wisdom % Head Chest Legs Hands>,<lamp 0-4>; the spec 2.3 numbers) + THE SEVEN MINING SETS in the 0.2.14 Armor sets table (set.mining_<tier>=
     <Tier> Mining Set,4,<bonus>; bonus words mfort / mwis / mpow (decimals) and spd; spec 2.4 numbers: full sets 1.5 / 2.3 / 3.8 / 6.0 / 8.3 /
     11.3 / 15.0 Fortune). Everything counts ONLY while a pickaxe or shovel is held (Skyy "tool in hand"); 1-3 pieces or mixed tiers = no bonus.
     The Mining Sets' own stats (spd) never enter the always-on totals (GearSet.addTo / hp skip them); other sets may carry mining words too.
  4. DELIVERY: GearMine.note (the 1 s armor pass + every armor change) keeps per player { Fortune (capped armor.fortune.cap 15), Wisdom % (capped
     armor.wisdom.cap 10), Mining Power %, Speed points, lamp }. Fortune + Wisdom ride the EXISTING skill:bonus "gear" source of the held tool
     (dd.mining = (tool Fortune + armor Fortune) / 100, xp.mining = Wisdom / 100, the tool's only.mining filter: pickaxe rock / ore, shovel soil) -
     posted even when the tool's own part is 0 (an under-level tool); hatchet / sword / empty hand = no armor part (no SkyySkills change). Mining
     Power: GearToolHitSys factor x (1 + mpow / 100) on the tool's own block types only. Speed: the existing armor movement source (flat layer,
     x speed.per / 100), only while a pickaxe / shovel is held (re-read every armor pass: gone <= 1 s after a swap).
  5. HELMET LAMP: gear:lamp:<uuid> = Integer 1-4 (the worn ACTIVE metal helmet's lamp: Normal / Unique / Rare / Legendary = Lantern reach 6 / 12 /
     24 / 48) on the skyy.bridge map, removed when none, under-level, on profile:busy and on leave. No reader yet (SkyyAccessories 0.5.10); the
     tooltip "Lamp:" line only shows when acc:lamp = "on" (published by that reader). No fake glow.
  6. TOOLTIP: per piece "Mining Fortune +x", "Mining Wisdom +y%", "Mining lines work with a pickaxe or shovel in hand"; the green Set block for
     every mining piece (old ones by id): "Set: Cobalt Mining Set (3/4)" + "Full set (all 4): Mining Fortune +4, Mining Power +8% (pickaxe or
     shovel in hand)". /gear prints the mining armor line.
  7. PETS (queued, research/cloud/Pet-Core-Spec.md + SkyyPets 0.1): pets:stats:<uuid> (Map String -> Number, replaced whole; keys str cc cd def mp
     dmg like gear:extra, fractions summed per key then floored, unknown keys such as swing.* skipped) is read into the same totals path as
     gear:extra (combat, regen, /gear "From other mods"). gear:extra itself is untouched (SkyyAccessories owns it; the separate pets key is the
     merge-safe door - Pet-Core-Spec G4).
SAVED DATA: new documents of the 28 ids carry r "set" + set "mining_<tier>" (fields 0.2.14 already reads); nothing existing is rewritten.
CONFIG (PROJECT-RULES 4): ONE-TIME UPDATE migrate0215 = pure ADDITION (no value is rewritten, so no change-log row): the block (heading, marker,
garmor.miningOn / garmor.miningShare / armor.fortune.cap / armor.wisdom.cap with their help lines, the 7 garmor.mining rows, the 7 set.mining_* rows)
at the END of the file, only the keys the file lacks (keys already there kept + noted); verified History copy first, atomic write, ISO-8859-1
bytes, run-once marker, every other byte and line ending kept. A fresh file carries exactly that block.
ROLLBACK FLOORS (for tools/deploy_set.py, reported, not edited here): rolling back to 0.2.14 is safe for documents (0.2.14 reads r "set" and the
set field; new mining pieces show as green Set pieces with Class-gated combat Health and no mining lines). BUT the 7 set.mining_* rows stay in
config.properties and 0.2.14 reads them as plain sets: their mfort / mwis / mpow words are skipped with one WARN and the Adamantite / Mithril /
Onyxium spd+5 / +8 / +10 becomes an ALWAYS-ON full-set Speed bonus - before a rollback EDIT (never delete) those three rows: take out only their
spd+N word. Deleted set.mining_* lines never come back by themselves (migrate0215 is run-once); 0.2.15 then says so at every start (one INFO
line with the default lines to paste back - fix round). 0.2.14 also puts the 28 ids back into the bag pool. Rolling forward again re-reads
everything (no data change); put spd+5 / +8 / +10 back in Server Setup -> Gear -> Rarity -> Armor sets.
FIX ROUND (critics): an old Heavy mystery bag whose Heavy range lost its metal pieces opens / re-identifies with any armor of its slot
(GearUnid.fit: same range any armor, else the nearest levels); GearMine.note skips a player who left (GearTool.GONE); /gear posts no lamp while profile:busy; the gmMissing INFO line;
the garmor.mining column headings spelled out.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.14.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.15.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.14"' in s and s.startswith('"""SkyyGear 0.2.14 - build script'), "build_skyygear_0.2.14.py is not the live 0.2.14"
assert "GearMine" not in s and "garmor" not in s, "0.2.14 already has the 0.2.15 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.14 - build script (javassist via jpype). GENERATED by tools/gear_0_2_14_patch.py from the LIVE 0.2.13 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.14.py -> SkyyGear/SkyyGear-0.2.14.jar (never --deploy).

0.2.14 = ''', '''"""SkyyGear 0.2.15 - build script (javassist via jpype). GENERATED by tools/gear_0_2_15_patch.py from the LIVE 0.2.14 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.15.py -> SkyyGear/SkyyGear-0.2.15.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.15 = "):].strip() + '''

0.2.14 (the base, everything below is still true unless 0.2.15 above says otherwise):
0.2.14 = ''')
rep('VERSION = "0.2.14"', 'VERSION = "0.2.15"')

# ================================================================================================================ 1. the 28 pieces (build checks)
rep(r'''LOOT_TNAME = [_TNAME.get(_k, _k.split("_", 1)[1]) for _k in LOOT_TYPES]''', r'''LOOT_TNAME = [_TNAME.get(_k, _k.split("_", 1)[1]) for _k in LOOT_TYPES]

# ================================================================= 0.2.15 MINING ARMOR (tools/gear_0_2_15_patch.py): the 28 vanilla metal pieces
MINE_TIERS = ["Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
MINE_SLOTS = ["Head", "Chest", "Hands", "Legs"]          # the engine's ItemArmorSlot order (no Feet slot)
MINE_IDS = ["Armor_%s_%s" % (_t, _s) for _t in MINE_TIERS for _s in MINE_SLOTS]
_LP_IDS = set(_p[0] for _p in LOOT_POOL)
for _k, _i in enumerate(MINE_IDS):
    _a = az_get(_i, "Armor")
    assert isinstance(_a, dict) and _a.get("ArmorSlot") == MINE_SLOTS[_k % 4], "mining armor %s: ArmorSlot %s" % (_i, _a)
    assert az_get(_i, "ItemSoundSetId") == "ISS_Armor_Heavy", "mining armor %s is not ISS_Armor_Heavy" % _i
    assert _i in _LP_IDS, "mining armor %s is not in the 0.2.14 bag pool (nothing to take out)" % _i
for _s in MINE_SLOTS:          # the Heavy bags keep Bronze / Steel / Heavy Leather pieces in every slot
    assert [_p[0] for _p in LOOT_POOL if _p[1] == "Armor_" + _s and _p[2] == 1 and _p[0] not in MINE_IDS], "no Heavy %s left without the mining pieces" % _s
# spec 2.3 (Fortune / Wisdom % per piece in the ROW order Head, Chest, Legs, Hands; helmet lamp 0-4) + 2.4 (the full-set bonus words)
MINE_ROWS = [("copper", "0.1 0.2 0.1 0.1", "0 0 0 0", 1, "mfort+1"),
             ("iron", "0.2 0.3 0.2 0.1", "0 0 0 0", 2, "mfort+1.5"),
             ("thorium", "0.3 0.5 0.3 0.2", "0 0 0 0", 2, "mfort+2.5 mpow+5"),
             ("cobalt", "0.5 0.7 0.5 0.3", "0.5 0.7 0.5 0.3", 3, "mfort+4 mpow+8"),
             ("adamantite", "0.7 1.0 0.7 0.4", "1.0 1.4 1.0 0.6", 3, "mfort+5.5 mpow+10 spd+5"),
             ("mithril", "1.0 1.3 0.9 0.6", "1.5 2.1 1.5 0.9", 4, "mfort+7.5 mpow+12 spd+8"),
             ("onyxium", "1.3 1.8 1.2 0.7", "2.0 2.8 2.0 1.2", 4, "mfort+10 mpow+15 spd+10")]
assert [_r[0] for _r in MINE_ROWS] == [_t.lower() for _t in MINE_TIERS]
MINE_FCAP, MINE_WCAP = 15.0, 10.0


def _mine_words(txt):
    _o = {}
    for _w in txt.split():
        _k, _v = _w.split("+")
        _o[_k] = _o.get(_k, 0.0) + float(_v)
    return _o


def _slot_order(cell):        # row order Head Chest Legs Hands -> engine slot order Head Chest Hands Legs
    _v = [float(_x) for _x in cell.split()]
    return [_v[0], _v[1], _v[3], _v[2]]


MINE_F = [_x for _r in MINE_ROWS for _x in _slot_order(_r[1])]
MINE_W = [_x for _r in MINE_ROWS for _x in _slot_order(_r[2])]
MINE_L = [_r[3] for _r in MINE_ROWS]
_full = [round(sum(_slot_order(_r[1])) + _mine_words(_r[4])["mfort"], 2) for _r in MINE_ROWS]
assert _full == [1.5, 2.3, 3.8, 6.0, 8.3, 11.3, 15.0] and max(_full) <= MINE_FCAP, "spec 4 full-set Fortune: %s" % _full
assert all(round(sum(_slot_order(_r[2])), 2) <= MINE_WCAP for _r in MINE_ROWS) and [round(sum(_slot_order(_r[2])), 2) for _r in MINE_ROWS][3:] == [2.0, 4.0, 6.0, 8.0]
assert all(set(_mine_words(_r[4])) <= {"mfort", "mwis", "mpow", "spd"} for _r in MINE_ROWS) and MINE_L == [1, 2, 2, 3, 3, 4, 4]
print("0.2.15 mining armor: %d pieces (%s); full-set Fortune %s (cap %g)" % (len(MINE_IDS), ", ".join(MINE_TIERS), _full, MINE_FCAP))''')

# take the 28 ids out of the bag pool at RUN time (garmor.miningOn off = 0.2.14's pool again)
rep(r'''    try { v = @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && !excluded(id, ex) && !@PKG@.GearUt.has(id); } catch (Throwable x) { v = false; }''',
    r'''    try { v = @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && !excluded(id, ex) && !@PKG@.GearUt.has(id) && !@PKG@.GearMine.isPiece(id); } catch (Throwable x) { v = false; }''')

# ================================================================================================================ 2. config rows
rep(r'''            ("costs", "Costs"), ("drops", "Drops + craft"), ("loot", "Loot"), ("tools", "Tools"), ("combat", "Combat"), ("migrate", "Migration")]''',
    r'''            ("costs", "Costs"), ("drops", "Drops + craft"), ("loot", "Loot"), ("tools", "Tools"), ("combat", "Combat"), ("migrate", "Migration"),
            ("garmor", "Gathering armor")]       # 0.2.15''')
rep(r'''     "Old SkyyRolls items move over no better than this (never Mythic/Set)." + PH, "field:GearCfg.MIGRATE_MAX"),''',
    r'''     "Old SkyyRolls items move over no better than this (never Mythic/Set)." + PH, "field:GearCfg.MIGRATE_MAX"),
    # 0.2.15 mining armor (Skyy 2026-10-09: the vanilla metal sets are the mining gear)
    ("garmor.miningOn", "Mining armor (vanilla metal sets)", "garmor", "bool", "true", "", "", "", "", "live,part,danger",
     "Copper..Onyxium armor = green Mining Sets: Mining gate, mining lines with a pickaxe or shovel.", "field:GearCfg.GM_ON"),
    ("garmor.mining", "Mining armor by tier", "garmor", "table", "", "0", "4", "text|text|int;none;Fortune Head Chest Legs Hands|Wisdom % Head Chest Legs Hands|Lamp 0-4",
     "", "live,danger", "Fortune and Wisdom % per piece (Head Chest Legs Hands) + helmet lamp 0-4 (0 = none).",
     "reload@%s:garmor.mining.;check=GearMine.checkRow" % CFG_FILE),
    ("garmor.miningShare", "Mining armor Health / resistance", "garmor", "int", "100", "0", "100", "", "%", "live,danger",
     "Share of the normal armor Health and resistance the metal pieces give (100 = full).", "field:GearCfg.GM_SHARE"),
    ("armor.fortune.cap", "Most Fortune from armor", "garmor", "dec", "15", "0", "100", "", "", "live,danger",
     "Mining Fortune from worn armor (pieces + full set) stops here (Onyxium full set = 15).", "field:GearCfg.GM_FCAP"),
    ("armor.wisdom.cap", "Most Wisdom % from armor", "garmor", "dec", "10", "0", "100", "", "%", "live,danger",
     "Mining Wisdom % from worn armor stops here.", "field:GearCfg.GM_WCAP"),''')
rep(r'''           # 0.2.14: the Untiered items (what bags / grants make) and the armor sets (combat stats) - confirm in Server Setup
           "ut", "set"}''', r'''           # 0.2.14: the Untiered items (what bags / grants make) and the armor sets (combat stats) - confirm in Server Setup
           "ut", "set",
           # 0.2.15: the mining armor switch, its per-tier lines, its Health share and the armor Fortune / Wisdom caps (economy)
           "garmor.miningOn", "garmor.mining", "garmor.miningShare", "armor.fortune.cap", "armor.wisdom.cap"}''')
rep(r'''              ("TOOL_FMAT", "double", repr(TOOL_FMAT_DEF)), ("TOOL_FCAP", "double", repr(TOOL_FCAP_DEF))]''',
    r'''              ("TOOL_FMAT", "double", repr(TOOL_FMAT_DEF)), ("TOOL_FCAP", "double", repr(TOOL_FCAP_DEF)),
              # 0.2.15 mining armor
              ("GM_ON", "boolean", "true"), ("GM_SHARE", "int", "100"), ("GM_FCAP", "double", repr(MINE_FCAP)), ("GM_WCAP", "double", repr(MINE_WCAP))]''')

# the fresh file's 0.2.15 block (= exactly what migrate0215 adds to an older file): heading, marker, then GROUPS (a comment + its key lines)
rep(r'''def default_text():''', r'''# 0.2.15: the mining armor block at the very end of a fresh file (migrate0215 appends the missing keys of it, group by group, to an older one)
GM_MARK_ID = "SkyyGear 0.2.15 mining armor"
GM_WHO = "SkyyGear 0.2.15"
GM_HEAD = "# ---- Mining armor: the vanilla metal sets Copper..Onyxium (SkyyGear 0.2.15) ----"
GM_MARK = ("# %s (Skyy 2026-10-09): the vanilla metal armor is the mining gear - Mining level gate, mining lines and the full-set bonus "
           "only with a pickaxe or shovel in hand" % GM_MARK_ID)
_gmr = dict((_r[0], _r) for _r in CFG_ROWS)
GM_SCAL = ["garmor.miningOn", "garmor.miningShare", "armor.fortune.cap", "armor.wisdom.cap"]
GM_TBLC = "# ---- garmor.mining.<tier>=<Fortune Head Chest Legs Hands>,<Wisdom % Head Chest Legs Hands>,<lamp 0 none, 1 Normal, 2 Unique, 3 Rare, 4 Legendary> ----"
GM_SETC = "# ---- the seven Mining Sets (Armor sets): all 4 pieces worn = the bonus (mfort Fortune, mwis Wisdom %, mpow Mining Power %, spd Speed), pickaxe or shovel in hand ----"
GM_GROUPS = [("# %s: %s" % (_gmr[_k][1], _gmr[_k][10]), ["%s=%s" % (_k, _gmr[_k][4])]) for _k in GM_SCAL]
GM_GROUPS.append((GM_TBLC, ["garmor.mining.%s=%s,%s,%d" % (_r[0], _r[1], _r[2], _r[3]) for _r in MINE_ROWS]))
GM_GROUPS.append((GM_SETC, ["set.mining_%s=%s Mining Set,4,%s" % (_r[0], _r[0].capitalize(), _r[4]) for _r in MINE_ROWS]))
GM_LINES = [GM_HEAD, GM_MARK] + [_x for _c, _ls in GM_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in GM_LINES) and all("=" not in _x for _x in (GM_HEAD, GM_MARK))
assert len(set(GM_LINES)) == len(GM_LINES)


def default_text():''')
rep(r'''    L += [""] + GU_LINES       # 0.2.14: the Untiered / Mythic / Set block (migrate0214 adds exactly these lines to an older file)
    return "\n".join(L) + "\n"''', r'''    L += [""] + GU_LINES       # 0.2.14: the Untiered / Mythic / Set block (migrate0214 adds exactly these lines to an older file)
    L += [""] + GM_LINES       # 0.2.15: the mining armor block (migrate0215 adds the missing lines of it to an older file)
    return "\n".join(L) + "\n"''')
rep(r'''assert _DL[-len(GU_LINES) - 2:] == [""] + GU_LINES + [""], _DL[-len(GU_LINES) - 3:]''',
    r'''assert _DL[-len(GU_LINES) - len(GM_LINES) - 3:-len(GM_LINES) - 1] == [""] + GU_LINES + [""], _DL[-len(GU_LINES) - len(GM_LINES) - 3:]
# 0.2.15: the mining armor block once, at the very end, every line unique; the rows read back
assert _DL[-len(GM_LINES) - 1:] == GM_LINES + [""] and all(_DL.count(_x) == 1 for _x in GM_LINES) and DEFAULT_TEXT.count(GM_MARK_ID) == 1
for _r in MINE_ROWS:
    assert _dp.get("garmor.mining." + _r[0]) == "%s,%s,%d" % _r[1:4] and _dp.get("set.mining_" + _r[0]) == "%s Mining Set,4,%s" % (_r[0].capitalize(), _r[4])''')

# ================================================================================================================ 3. Java: the class, fields, tables
rep(r'''G1_CLASSES = [gut, gset, gwall]''', r'''G1_CLASSES = [gut, gset, gwall]
# 0.2.15 mining armor (tools/gear_0_2_15_patch.py)
gmine = mk("GearMine")          # the 28 metal pieces: lines, the Mining Sets' delivery, lamp, Server Setup checks
GM_CLASSES = [gmine]''')
rep(r'''F(gcf, "public static volatile Object[] STAB = new Object[] { new String[0], new String[0], new int[0], new int[0], new String[0] };")''',
    r'''F(gcf, "public static volatile Object[] STAB = new Object[] { new String[0], new String[0], new int[0], new int[0], new String[0] };")
# 0.2.15: the mining armor table { double[28] Fortune, double[28] Wisdom % (slot order Head Chest Hands Legs per tier), int[7] lamp } - swapped whole
_jd = lambda xs: "new double[] { %s }" % ", ".join(repr(float(x)) for x in xs)
F(gcf, "public static final double[] DGM_F = %s;" % _jd(MINE_F))
F(gcf, "public static final double[] DGM_W = %s;" % _jd(MINE_W))
F(gcf, "public static final int[] DGM_L = %s;" % jints(MINE_L))
F(gcf, "public static volatile Object[] GM_TAB = new Object[] { %s, %s, %s };" % (_jd(MINE_F), _jd(MINE_W), "new int[] { %s }" % ", ".join(str(x) for x in MINE_L)))
F(gcf, "public static final String GM_MARK = %s;" % jstr(GM_MARK))
F(gcf, "public static final String GM_MARK_ID = %s;" % jstr(GM_MARK_ID))
F(gcf, "public static final String GM_WHO = %s;" % jstr(GM_WHO))
F(gcf, "public static final String GM_HEAD = %s;" % jstr(GM_HEAD))
F(gcf, "public static final String[] GM_GC = %s;" % jarr([_c for _c, _ls in GM_GROUPS]))
F(gcf, "public static final int[] GM_GS = %s;" % jints([len(_ls) for _c, _ls in GM_GROUPS]))
F(gcf, "public static final String[] GM_GL = %s;" % jarr([_x for _c, _ls in GM_GROUPS for _x in _ls]))
F(gcf, "public static final String[] GM_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in GM_GROUPS for _x in _ls]))''')

# GearMine part 1 (only GearCfg fields + Gear helpers): ids, tables, words, the row parser, the cache readers
rep(r'''# ================================================================= Gear: settings registry helpers (research/Settings-Spec.md 1.3)''',
    r'''# ================================================================= 0.2.15 GearMine (1/4): the 28 metal pieces, the per-tier table (GearCfg.GM_TAB), the
# Mining Set bonus words, the per-player cache ARM: UUID -> double[] { Fortune, Wisdom %, Mining Power %, Speed points, lamp 0-4 } (GearMine.note)
F(gmine, "public static final String[] IDS = %s;" % jarr(MINE_IDS))
F(gmine, "public static final String[] TIER = %s;" % jarr([_t.lower() for _t in MINE_TIERS]))
F(gmine, "public static final String[] TNAME = %s;" % jarr(MINE_TIERS))
F(gmine, "public static final String[] SET_IDS = %s;" % jarr(["mining_" + _t.lower() for _t in MINE_TIERS]))
F(gmine, 'public static final String[] WORDS = new String[] { "mfort", "mwis", "mpow" };')
F(gmine, 'public static final String[] WLABEL = new String[] { "Mining Fortune", "Mining Wisdom", "Mining Power" };')
F(gmine, 'public static final String[] WUNIT = new String[] { "", "%", "%" };')
F(gmine, 'public static final String[] LAMP_NAME = new String[] { "", "Normal", "Unique", "Rare", "Legendary" };')
F(gmine, "public static final int[] LAMP_REACH = new int[] { 0, 6, 12, 24, 48 };")
F(gmine, "public static final int I_SPD = %d;" % S_KEYS.index("spd"))
F(gmine, "public static final java.util.concurrent.ConcurrentHashMap ARM = new java.util.concurrent.ConcurrentHashMap();")
F(gmine, "public static final java.util.concurrent.ConcurrentHashMap LAMP = new java.util.concurrent.ConcurrentHashMap();")
M(gmine, r"""
public static int index(String id) {
  if (id == null) return -1;
  for (int i = 0; i < IDS.length; i++) if (IDS[i].equals(id)) return i;
  return -1;
}""")
M(gmine, "public static boolean isPiece(String id) { return @PKG@.GearCfg.GM_ON && index(id) >= 0; }")
M(gmine, r"""
public static int tier(String id) {
  int i = index(id);
  return i < 0 ? -1 : i / 4;
}""")
# the set a piece counts for BY ID (old pieces have no set field): null = not a mining piece / mining armor off
M(gmine, r"""
public static String setFor(String id) {
  if (!@PKG@.GearCfg.GM_ON) return null;
  int i = index(id);
  return i < 0 ? null : SET_IDS[i / 4];
}""")
M(gmine, r"""
public static int setTier(String sid) {
  if (sid == null) return -1;
  String s = sid.trim();
  for (int i = 0; i < SET_IDS.length; i++) if (SET_IDS[i].equalsIgnoreCase(s)) return i;
  return -1;
}""")
M(gmine, r"""
public static double fortune(int i) {
  double[] f = (double[]) @PKG@.GearCfg.GM_TAB[0];
  return i >= 0 && i < f.length ? f[i] : 0.0;
}""")
M(gmine, r"""
public static double wisdom(int i) {
  double[] w = (double[]) @PKG@.GearCfg.GM_TAB[1];
  return i >= 0 && i < w.length ? w[i] : 0.0;
}""")
M(gmine, r"""
public static int lamp(int t) {
  int[] l = (int[]) @PKG@.GearCfg.GM_TAB[2];
  return t >= 0 && t < l.length ? l[t] : 0;
}""")
M(gmine, r"""
public static int word(String k) {
  if (k == null) return -1;
  String t = k.trim();
  for (int i = 0; i < WORDS.length; i++) if (WORDS[i].equalsIgnoreCase(t)) return i;
  return -1;
}""")
# a bonus word's number (decimals allowed): 0 < v <= 1000, else -1
M(gmine, r"""
public static double wordVal(String v) {
  if (v == null) return -1.0;
  double x = -1.0;
  try { x = Double.parseDouble(v.trim().replace("_", "")); } catch (Throwable t) { return -1.0; }
  if (Double.isNaN(x) || Double.isInfinite(x) || !(x > 0.0) || x > 1000.0) return -1.0;
  return x;
}""")
# "mfort+4 mpow+8 spd+5" -> { mfort, mwis, mpow } (other words ignored here)
M(gmine, r"""
public static double[] words(String text) {
  double[] o = new double[3];
  if (text == null) return o;
  String[] ps = text.trim().split("\\s+");
  for (int i = 0; i < ps.length; i++) {
    String p = ps[i].trim();
    int c = p.indexOf('+');
    if (c <= 0) continue;
    int w = word(p.substring(0, c));
    if (w < 0) continue;
    double v = wordVal(p.substring(c + 1));
    if (v < 0.0) continue;
    o[w] = o[w] + v;
  }
  return o;
}""")
M(gmine, r"""
public static String num(double v) {
  double r = (double) Math.round(v * 100.0) / 100.0;
  long l = Math.round(r);
  if (Math.abs(r - (double) l) < 0.000001) return String.valueOf(l);
  return String.valueOf(r);
}""")
M(gmine, r"""
public static String wordsText(String text) {
  double[] w = words(text);
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < w.length; i++) {
    if (!(w[i] > 0.0)) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(WLABEL[i]).append(" +").append(num(w[i])).append(WUNIT[i]);
  }
  return sb.toString();
}""")
# "0.1 0.2 0.1 0.1" -> double[4] (row order), each 0-100; null = bad
M(gmine, r"""
public static double[] four(String cell) {
  if (cell == null) return null;
  String[] ps = cell.trim().split("\\s+");
  if (ps.length != 4) return null;
  double[] o = new double[4];
  for (int i = 0; i < 4; i++) {
    try { o[i] = Double.parseDouble(ps[i].trim()); } catch (Throwable x) { return null; }
    if (Double.isNaN(o[i]) || o[i] < 0.0 || o[i] > 100.0) return null;
  }
  return o;
}""")
# a garmor.mining row <Fortune Head Chest Legs Hands>,<Wisdom % Head Chest Legs Hands>,<lamp 0-4> -> { double[4] Fortune, double[4] Wisdom (both in
# the engine slot order Head Chest Hands Legs), Integer lamp }; null = bad
M(gmine, r"""
public static Object[] parseRow(String v) {
  if (v == null) return null;
  String[] cs = v.replace('|', ',').split(",", -1);
  if (cs.length != 3) return null;
  double[] f = four(cs[0]);
  double[] w = four(cs[1]);
  int l = -1;
  try { l = Integer.parseInt(cs[2].trim()); } catch (Throwable x) { l = -1; }
  if (f == null || w == null || l < 0 || l > 4) return null;
  return new Object[] { new double[] { f[0], f[1], f[3], f[2] }, new double[] { w[0], w[1], w[3], w[2] }, Integer.valueOf(l) };
}""")
# Server Setup / file check of a Mining Set's bonus: mfort mwis mpow spd only (they all need a pickaxe or shovel in hand); null = fine
M(gmine, r"""
public static String setWhy(String sid, String bonus) {
  if (setTier(sid) < 0 || bonus == null) return null;
  String[] ps = bonus.trim().split("\\s+");
  for (int i = 0; i < ps.length; i++) {
    String p = ps[i].trim();
    if (p.length() == 0) continue;
    int c = p.indexOf('+');
    String k = c > 0 ? p.substring(0, c).trim() : p;
    if (word(k) < 0 && !k.equals("spd")) return "A Mining Set's bonus uses mfort (Fortune), mwis (Wisdom %), mpow (Mining Power %) and spd (Speed) only - they work with a pickaxe or shovel in hand.";
  }
  return null;
}""")
# the worn mining armor of a player (null = none noted / mining armor off); the CALLER checks the pickaxe / shovel
M(gmine, r"""
public static double[] bonus(java.util.UUID u) {
  if (u == null || !@PKG@.GearCfg.GM_ON) return null;
  return (double[]) ARM.get(u);
}""")

# ================================================================= Gear: settings registry helpers (research/Settings-Spec.md 1.3)''')

# GearCfg: the set bonus words, the table reader, the scalars
rep(r'''    int c = p.indexOf('+');
    long v = -1L;
    int si = -1;''', r'''    int c = p.indexOf('+');
    // 0.2.15: the mining words (mfort / mwis / mpow, decimals) are kept in the row text for GearMine, never stats here
    if (c > 0 && @PKG@.GearMine.word(p.substring(0, c)) >= 0) {
      if (@PKG@.GearMine.wordVal(p.substring(c + 1)) < 0.0 && bad != null) { if (bad.length() > 0) bad.append(' '); bad.append(p); }
      continue;
    }
    long v = -1L;
    int si = -1;''')
rep(r'''# every value read from the file (or the built-in defaults when there is no file: bare-JVM tests); clamps like the kit rows''',
    r'''# ---- 0.2.15: garmor.mining.<tier> rows -> GM_TAB (a missing row = its built-in default; a bad row = the default + one WARN)
M(gcf, r"""
public static Object[] readMine(java.util.Properties p) {
  int n = DGM_F.length;
  double[] f = new double[n];
  double[] w = new double[n];
  int[] l = new int[DGM_L.length];
  for (int i = 0; i < n; i++) { f[i] = DGM_F[i]; w[i] = DGM_W[i]; }
  for (int i = 0; i < l.length; i++) l[i] = DGM_L[i];
  for (int t = 0; t < @PKG@.GearMine.TIER.length; t++) {
    String k = "garmor.mining." + @PKG@.GearMine.TIER[t];
    String v = p.getProperty(k);
    if (v == null) continue;
    Object[] r = @PKG@.GearMine.parseRow(v);
    if (r == null) { @PKG@.Gear.warnOnce("gmrow:" + k + "=" + v, "config.properties: " + k + "=" + v + " is not <Fortune x4>,<Wisdom x4>,<lamp 0-4> - its default is used"); continue; }
    double[] rf = (double[]) r[0];
    double[] rw = (double[]) r[1];
    for (int s = 0; s < 4; s++) { f[t * 4 + s] = rf[s]; w[t * 4 + s] = rw[s]; }
    l[t] = ((Integer) r[2]).intValue();
  }
  return new Object[] { f, w, l };
}""")

# every value read from the file (or the built-in defaults when there is no file: bare-JVM tests); clamps like the kit rows''')
rep(r'''  TOOL_FCAP = pdec(p, "tool.fortune.cap", TOOL_FCAP_DEFV, 0.0, 1000.0);''', r'''  TOOL_FCAP = pdec(p, "tool.fortune.cap", TOOL_FCAP_DEFV, 0.0, 1000.0);
  // 0.2.15 mining armor
  GM_ON = pbool(p, "garmor.miningOn", true);
  GM_SHARE = (int) plong(p, "garmor.miningShare", 100L, 0L, 100L);
  GM_FCAP = pdec(p, "armor.fortune.cap", 15.0, 0.0, 100.0);
  GM_WCAP = pdec(p, "armor.wisdom.cap", 10.0, 0.0, 100.0);''')
rep(r'''  LV_CAP = lc; UTAB = utab; STAB = stab;''', r'''  Object[] gmt = readMine(p);         // 0.2.15
  LV_CAP = lc; UTAB = utab; STAB = stab; GM_TAB = gmt;''')

# ================================================================================================================ 4. the one-time update
rep(r'''# 0.2.1 ready line part: the base stats in force (live values)''', r'''# ---- 0.2.15 ONE-TIME UPDATE migrate0215 (PROJECT-RULES section 4): a pure ADDITION. Pure text step: null = the marker is already in a comment
# line (a fresh 0.2.15 file carries it). Else { new text, String[] notes (keys already there - kept), "garmor.miningOn, ..." (what was added) }.
# The block (blank line + heading + marker, then per group its comment + every MISSING key line) goes to the END of the file (chEnd: the
# end-of-file continuation trap); which keys exist is asked of java.util.Properties itself. No value anywhere is changed.
M(gcf, r"""
public static Object[] gmUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(GM_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    k = e + 1;
  }
  java.util.ArrayList notes = new java.util.ArrayList();
  StringBuilder added = new StringBuilder();
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add("");
  blk.add(GM_HEAD);
  blk.add(GM_MARK);
  int at = 0;
  for (int g = 0; g < GM_GC.length; g++) {
    boolean first = true;
    for (int j = 0; j < GM_GS[g]; j++) {
      int x = at + j;
      if (pp.getProperty(GM_GK[x]) != null) { notes.add(GM_GK[x] + " is already in the file - kept"); continue; }
      if (first) { blk.add(GM_GC[g]); first = false; }
      blk.add(GM_GL[x]);
      if (added.length() > 0) added.append(", ");
      added.append(GM_GK[x]);
    }
    at = at + GM_GS[g];
  }
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) out.add(raw[i]);
  chPut(out, chEnd(l, tail, raw), blk, crDef);
  StringBuilder sb = new StringBuilder(text.length() + 4096);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), (String[]) notes.toArray(new String[0]), added.toString() };
}""")
# fix round: the set.mining_* keys of the block a file lacks ("" = none), and their default lines ("; "-joined)
M(gcf, r"""
public static String gmMissing(String text) {
  java.util.Properties pp = new java.util.Properties();
  try { if (text != null) pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < GM_GK.length; i++) {
    if (!GM_GK[i].startsWith("set.mining_") || pp.getProperty(GM_GK[i]) != null) continue;
    if (sb.length() > 0) sb.append(", ");
    sb.append(GM_GK[i]);
  }
  return sb.toString();
}""")
M(gcf, r"""
public static String gmDefaults(String text) {
  java.util.Properties pp = new java.util.Properties();
  try { if (text != null) pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < GM_GK.length; i++) {
    if (!GM_GK[i].startsWith("set.mining_") || pp.getProperty(GM_GK[i]) != null) continue;
    if (sb.length() > 0) sb.append("; ");
    sb.append(GM_GL[i]);
  }
  return sb.toString();
}""")
# setup(), right after migrate0214 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one INFO
# line (+ one per note), gear.log; "" = nothing done (no file, marker already there, or a failure - WARN, file untouched, the next start tries again;
# the loader then runs on the built-in mining rows, and the Mining Sets stay off until their set rows are in the file)
M(gcf, r"""
public static synchronized String migrate0215() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    String otext = new String(old, "ISO-8859-1");
    Object[] r = gmUpdate(otext);
    if (r == null) {
      // fix round (safety critic LOW 2): the update is run-once, so a Mining Set row removed later (e.g. around a rollback) never comes back
      // by itself - say so at every start, with the default line to paste back (nothing is written)
      String miss = gmMissing(otext);
      if (miss.length() > 0) @PKG@.Gear.info("config.properties has no " + miss + " - those Mining Sets give no full-set bonus. Add them back in Server Setup -> Gear -> Rarity -> Armor sets (defaults: " + gmDefaults(otext) + ")");
      return "";
    }
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), GM_WHO, "before the 0.2.15 mining armor update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated with the 0.2.15 mining armor settings: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the built-in mining rows are used, the Mining Sets stay off; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] notes = (String[]) r[1];
    String add = (String) r[2];
    String msg = "config.properties: the 0.2.15 mining armor settings were added at the end (" + (add.length() > 0 ? add : "only the marker - every key was there") + "); no value changed; the old file is kept in config-history";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.2.15 mining armor: added " + (add.length() > 0 ? add : "the marker only") + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not add the 0.2.15 mining armor settings to config.properties (the file is used as it is): " + t);
    return "";
  }
}""")
# 0.2.1 ready line part: the base stats in force (live values)''')
rep(r'''  @PKG@.GearCfg.migrate0214();
  @PKG@.GearCfg.load();''', r'''  @PKG@.GearCfg.migrate0214();
  @PKG@.GearCfg.migrate0215();
  @PKG@.GearCfg.load();''')

# ================================================================================================================ 5. gate, crafts, documents
rep(r'''public static Object[] check(java.util.UUID u, String id, @BD@ d, int need) {
  String kind = @PKG@.GearData.kind(d);
  String gate = @PKG@.GearData.gate(d);
  boolean enforced = @PKG@.GearDefs.enforcedKind(kind);''', r'''public static Object[] check(java.util.UUID u, String id, @BD@ d, int need) {
  String kind = @PKG@.GearData.kind(d);
  String gate = @PKG@.GearData.gate(d);
  boolean enforced = @PKG@.GearDefs.enforcedKind(kind);
  // 0.2.15 (Skyy "Mining gate -> Yes, Mining level"): the 28 metal pieces - old documents too - need your MINING level (read time, no rewrite)
  if (@PKG@.GearMine.isPiece(id)) { gate = "Mining"; enforced = true; }''')
rep(r'''public static Object[] gateLine(java.util.UUID owner, String id, @BD@ d, int need) {
  String kind = @PKG@.GearData.kind(d);
  String gate = @PKG@.GearData.gate(d);
  String lv = "Lv " + need;
  if (!@PKG@.GearDefs.enforcedKind(kind)) {''', r'''public static Object[] gateLine(java.util.UUID owner, String id, @BD@ d, int need) {
  String kind = @PKG@.GearData.kind(d);
  String gate = @PKG@.GearData.gate(d);
  String lv = "Lv " + need;
  boolean mine = @PKG@.GearMine.isPiece(id);       // 0.2.15: a mining piece is enforced with the Mining gate
  if (mine) gate = "Mining";
  if (!mine && !@PKG@.GearDefs.enforcedKind(kind)) {''')

# GearMine part 1c (needs GearData.base + GearLevel): the document of a NEW mining piece
rep(r'''# ================================================================= GearRoll (spec 2.3, 5.3, 5.4): SecureRandom, never seeded''',
    r'''# ================================================================= 0.2.15 GearMine (2/4): the document of a NEW mining piece - rarity Set, identified,
# no modifiers, level kept inside the material band (lvl < 0 = no stamp: part.levels off), set field mining_<tier>
M(gmine, r"""
public static @BD@ doc(String id, String src, int lvl) {
  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), @PKG@.GearDefs.R_SET, true, src);
  if (lvl >= 0) {
    int[] b = @PKG@.GearLevel.band(id);
    int L = lvl;
    if (L < b[0]) L = b[0];
    if (L > b[1]) L = b[1];
    d.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.clamp(L)));
  }
  String sid = setFor(id);
  if (sid != null) d.put("set", new org.bson.BsonString(sid));
  return d;
}""")

# ================================================================= GearRoll (spec 2.3, 5.3, 5.4): SecureRandom, never seeded''')
rep(r'''public static @BD@ newDoc(String id, int r, boolean ident, String src, int lvl) {
  // 0.2.14: an Untiered-table id is always Untiered (its level inside the row's range); nothing else is ever Untiered''',
    r'''public static @BD@ newDoc(String id, int r, boolean ident, String src, int lvl) {
  // 0.2.15: a NEW piece of the 28 metal ids is always an identified green Mining Set piece (no modifiers, fixed mining lines)
  if (@PKG@.GearMine.isPiece(id)) return @PKG@.GearMine.doc(id, src, lvl);
  // 0.2.14: an Untiered-table id is always Untiered (its level inside the row's range); nothing else is ever Untiered''')
rep(r'''public static String craftSkill(String id, java.util.UUID u) {
  String w = weaponSkill(id);
  if (w != null) return w;''', r'''public static String craftSkill(String id, java.util.UUID u) {
  if (@PKG@.GearMine.isPiece(id)) return "Mining";      // 0.2.15: metal armor is made at your Mining level
  String w = weaponSkill(id);
  if (w != null) return w;''')
rep(r'''public static String craftLabel(String id, java.util.UUID u) {
  String w = weaponSkill(id);''', r'''public static String craftLabel(String id, java.util.UUID u) {
  if (@PKG@.GearMine.isPiece(id)) return "Mining";      // 0.2.15
  String w = weaponSkill(id);''')
rep(r'''  if (id == null || !@PKG@.GearData.isGear(id)) return 0L;
  double v = (double) @PKG@.GearCfg.xpCraft(r) * xpTier(xpStart(id));''', r'''  if (id == null || !@PKG@.GearData.isGear(id)) return 0L;
  // 0.2.15: a Set mining piece pays the Normal row (every craft is Set now - the Set row would pay 8x for plain metal armor)
  if (r == @PKG@.GearDefs.R_SET && @PKG@.GearMine.isPiece(id)) r = 0;
  double v = (double) @PKG@.GearCfg.xpCraft(r) * xpTier(xpStart(id));''')
rep(r'''  double h = bh[si] * curveH(lv) * bonus(st);      // 0.2.5: the Armor Health curve H (base.hpCurve)
  double r = br[si] / 100.0 * curveR(lv);
  return new float[] { (float) h, (float) r };''', r'''  double h = bh[si] * curveH(lv) * bonus(st);      // 0.2.5: the Armor Health curve H (base.hpCurve)
  double r = br[si] / 100.0 * curveR(lv);
  // 0.2.15: a mining piece gives garmor.miningShare % of it (100 = 0.2.14 exactly - no multiplication at all)
  if (@PKG@.GearCfg.GM_SHARE != 100 && @PKG@.GearMine.isPiece(id)) {
    double sh = (double) @PKG@.GearCfg.GM_SHARE / 100.0;
    h = h * sh;
    r = r * sh;
  }
  return new float[] { (float) h, (float) r };''')

# ================================================================================================================ 6. drops: never a bag, an identified Set piece
rep(r'''public static @IS@ fromItem(@IS@ s, int col, int L, String ls) {
  if (s == null || s.isEmpty() || s.getQuantity() != 1 || !@PKG@.GearCfg.UNID_BAGS) return null;
  String id = s.getItemId();''', r'''public static @IS@ fromItem(@IS@ s, int col, int L, String ls) {
  if (s == null || s.isEmpty() || s.getQuantity() != 1 || !@PKG@.GearCfg.UNID_BAGS) return null;
  String id = s.getItemId();
  if (@PKG@.GearMine.isPiece(id)) return null;        // 0.2.15: gathering armor never drops unidentified''')
# fix round (safety critic MEDIUM 1): a bag made by 0.2.11-0.2.14 stores its armor type + level range; with the 28 metal ids out of the pool the
# levels 28-29 and 38-44 have NO armor of any type any more (Heavy Hands / Legs Lv 14 none either - harness X1 notes). Opening / re-identifying
# such a bag (and its 'why' pre-check) uses GearUnid.fit: its own type + range when it still has a candidate; else any armor of the slot in
# the same range; else the NEAREST levels with a candidate of its own type (then any type), +-half its width - the same nearest-level rule a
# NEW bag gets at creation (GearPool.range in GearUnid.roll / fromItem). A bag that still has a candidate is unchanged.
rep(r'''# why a bag cannot be opened now (null = it can): unreadable, newer schema, unknown type, no candidate in its range''',
    r'''# 0.2.15 fix round: { armor type, lo, hi } a STORED bag picks with (see above); null = no candidate of that slot at any level
M(gunid, r"""
public static int[] fit(int ty, int at, int lo, int hi) {
  if (@PKG@.GearPool.levelCount(ty, at, lo, hi) > 0) return new int[] { at, lo, hi };
  if (at > 0 && @PKG@.GearPool.levelCount(ty, 0, lo, hi) > 0) return new int[] { 0, lo, hi };
  int c = (lo + hi) / 2;
  int half = (hi - lo) / 2;
  int a = at;
  int[] rg = @PKG@.GearPool.range(ty, at, c, half);
  if (rg == null && at > 0) { a = 0; rg = @PKG@.GearPool.range(ty, 0, c, half); }
  if (rg == null) return null;
  return new int[] { a, rg[0], rg[1] };
}""")
# why a bag cannot be opened now (null = it can): unreadable, newer schema, unknown type, no candidate in its range''')
rep(r'''  if (@PKG@.GearPool.levelCount(ty, at(d), lo(d), hi(d)) == 0) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(d), hi(d)) + " any more - an admin can help.";''',
    r'''  if (fit(ty, at(d), lo(d), hi(d)) == null) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(d), hi(d)) + " any more - an admin can help.";''')
rep(r'''  boolean ut = r == @PKG@.GearDefs.R_UT;
  int L = ut ? @PKG@.GearUt.pickLevel(ty, lo, hi) : @PKG@.GearPool.pickLevel(ty, at, lo, hi);''', r'''  boolean ut = r == @PKG@.GearDefs.R_UT;
  if (!ut) {         // 0.2.15 fix round: an old bag whose range lost its metal pieces (GearUnid.fit)
    int[] f = fit(ty, at, lo, hi);
    if (f == null) return null;
    at = f[0];
    lo = f[1];
    hi = f[2];
  }
  int L = ut ? @PKG@.GearUt.pickLevel(ty, lo, hi) : @PKG@.GearPool.pickLevel(ty, at, lo, hi);''')
rep(r'''  if (@PKG@.GearPool.levelCount(ty, at(b), lo(b), hi(b)) == 0) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(b), hi(b)) + " any more.";''',
    r'''  if (fit(ty, at(b), lo(b), hi(b)) == null) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(b), hi(b)) + " any more.";''')
rep(r'''  if (@PKG@.GearPool.typeOfId(s0.getItemId()) < 0) return 0;
  int q = s0.getQuantity();''', r'''  if (@PKG@.GearPool.typeOfId(s0.getItemId()) < 0) return 0;
  if (@PKG@.GearMine.isPiece(s0.getItemId())) return 0;      // 0.2.15
  int q = s0.getQuantity();''')
rep(r'''      if (@PKG@.GearUt.has(s.getItemId())) return @PKG@.GearUt.bag(L, ty0, src, "bridge", tier);      // 0.2.14: an Untiered item = an orange bag''',
    r'''      if (@PKG@.GearUt.has(s.getItemId())) return @PKG@.GearUt.bag(L, ty0, src, "bridge", tier);      // 0.2.14: an Untiered item = an orange bag
      if (@PKG@.GearMine.isPiece(s.getItemId())) return null;      // 0.2.15: a mining piece is never a bag''')
rep(r'''  if (col != 1 && col != 2) return s;
  if (@PKG@.GearCfg.UNID_BAGS && s.getQuantity() == 1) {''', r'''  if (col != 1 && col != 2) return s;
  // 0.2.15 (spec 5): a native drop of a metal piece = an identified green Mining Set piece at the mob / chest level, kept in its band
  if (@PKG@.GearMine.isPiece(id)) {
    int[] mb = @PKG@.GearLevel.band(id);
    int ml = lvl >= 1 ? lvl : mb[0];
    return @PKG@.GearData.put(s, @PKG@.GearRoll.newDoc(id, @PKG@.GearDefs.R_SET, true, col == 1 ? "drop" : "chest", @PKG@.GearCfg.PART_LEVELS ? ml : -1), null);
  }
  if (@PKG@.GearCfg.UNID_BAGS && s.getQuantity() == 1) {''')
rep(r'''  if (why == null && d != null && @PKG@.GearData.rarity(d) == @PKG@.GearDefs.R_UT) why = "Untiered items have fixed stats - they cannot be reforged (Level up still works).";''',
    r'''  if (why == null && d != null && @PKG@.GearData.rarity(d) == @PKG@.GearDefs.R_UT) why = "Untiered items have fixed stats - they cannot be reforged (Level up still works).";
  // 0.2.15: a Set mining piece has fixed mining lines (no random modifiers); old metal pieces with rolled modifiers still reforge
  if (why == null && d != null && @PKG@.GearData.rarity(d) == @PKG@.GearDefs.R_SET && @PKG@.GearMine.isPiece(id)) why = "Mining Set pieces have fixed mining lines - they cannot be reforged (Level up still works).";''')

# ================================================================================================================ 7. tools: Fortune / Wisdom / Mining Power
rep(r'''M(gtool, r"""
public static void post(java.util.UUID u, int row, double fo, String only) {
  if (u == null) return;
  try {
    java.util.Map b = @PKG@.Gear.bridge();
    String key = "skill:bonus:" + u.toString();
    Object o = b.get(key);
    if (row < 0 || row > 2 || !(fo > 0.0) || @PKG@.Gear.busy(u)) {
      if (o instanceof java.util.Map && ((java.util.Map) o).remove(SRC) != null) N[4] = N[4] + 1L;
      return;
    }
    java.util.HashMap m = new java.util.HashMap();
    m.put("dd." + ROWKEY[row], Double.valueOf(fo / 100.0));''', r'''# 0.2.15: + Wisdom (xp.<skill> = Wisdom % / 100, the worn mining armor's) in the same "gear" source; wis 0 = exactly 0.2.14's post
M(gtool, r"""
public static void postX(java.util.UUID u, int row, double fo, String only, double wis) {
  if (u == null) return;
  try {
    java.util.Map b = @PKG@.Gear.bridge();
    String key = "skill:bonus:" + u.toString();
    Object o = b.get(key);
    if (row < 0 || row > 2 || (!(fo > 0.0) && !(wis > 0.0)) || @PKG@.Gear.busy(u)) {
      if (o instanceof java.util.Map && ((java.util.Map) o).remove(SRC) != null) N[4] = N[4] + 1L;
      return;
    }
    java.util.HashMap m = new java.util.HashMap();
    if (fo > 0.0) m.put("dd." + ROWKEY[row], Double.valueOf(fo / 100.0));
    if (wis > 0.0) m.put("xp." + ROWKEY[row], Double.valueOf(wis / 100.0));''')
rep(r'''  } catch (Throwable t) { @PKG@.Gear.warnOnce("toolpost", "tool Fortune bridge post failed: " + t); }
}""")''', r'''  } catch (Throwable t) { @PKG@.Gear.warnOnce("toolpost", "tool Fortune bridge post failed: " + t); }
}""")
M(gtool, "public static void post(java.util.UUID u, int row, double fo, String only) { postX(u, row, fo, only, 0.0); }")''')
rep(r'''  double[] st = stats(u, s);
  LAST.put(u, new Object[] { s, Long.valueOf(now), st });
  if (st == null || st[3] == 0.0) post(u, -1, 0.0, null);
  else post(u, (int) st[1], st[5], ONLY[(int) st[0]]);
  return st;''', r'''  double[] st = stats(u, s);
  LAST.put(u, new Object[] { s, Long.valueOf(now), st });
  // 0.2.15: a pickaxe / shovel also carries the worn mining armor's Fortune + Wisdom (GearMine: pieces + complete Mining Sets, capped) - posted
  // even when the tool's own part is 0 (an under-level tool); any other hand = no armor part
  double[] ma = null;
  if (st != null && (st[0] == 1.0 || st[0] == 2.0)) ma = @PKG@.GearMine.bonus(u);
  double af = ma == null ? 0.0 : ma[0];
  double aw = ma == null ? 0.0 : ma[1];
  double tf = st != null && st[3] != 0.0 ? st[5] : 0.0;
  if (st == null || (!(tf > 0.0) && !(af > 0.0) && !(aw > 0.0))) post(u, -1, 0.0, null);
  else postX(u, (int) st[1], tf + af, ONLY[(int) st[0]], aw);
  return st;''')
rep(r'''    double[] st = held(u, s);
    if (st == null) { N[1] = N[1] + 1L; return dmg; }
    if (st[3] == 0.0) { N[2] = N[2] + 1L; return dmg; }
    if (!(st[4] > 1.0) || !(dmg > 0.0f) || !onType((int) st[0], bt)) { N[1] = N[1] + 1L; return dmg; }
    N[0] = N[0] + 1L;
    return (float) ((double) dmg * st[4]);''', r'''    double[] st = held(u, s);
    if (st == null) { N[1] = N[1] + 1L; return dmg; }
    int f = (int) st[0];
    boolean on = onType(f, bt);
    // 0.2.15: the worn Mining Sets' Mining Power % on the tool's own block types (pickaxe rock / ore, shovel soil), also with an under-level tool
    double af = 1.0;
    if (on && (f == 1 || f == 2)) {
      double[] ma = @PKG@.GearMine.bonus(u);
      if (ma != null && ma[2] > 0.0) af = 1.0 + ma[2] / 100.0;
    }
    if (st[3] == 0.0 && !(af > 1.0)) { N[2] = N[2] + 1L; return dmg; }
    double tf = st[3] != 0.0 && st[4] > 1.0 && on ? st[4] : 1.0;
    if (!(tf * af > 1.0) || !(dmg > 0.0f)) { N[1] = N[1] + 1L; return dmg; }
    N[0] = N[0] + 1L;
    return (float) ((double) dmg * tf * af);''')

# ================================================================================================================ 8. sets: membership by id, the bonus words
rep(r'''M(gset, "public static String name(Object[] t, int i) { return ((String[]) t[1])[i]; }")''', r'''# 0.2.15: the set a piece counts for - its document's set field, else (a metal piece without one: old pieces) its Mining Set by id
M(gset, r"""
public static String sidOf(String id, @BD@ d) {
  String s = of(d);
  if (s != null) return s;
  return @PKG@.GearMine.setFor(id);
}""")
M(gset, "public static String name(Object[] t, int i) { return ((String[]) t[1])[i]; }")''')
rep(r'''public static String bonusText(Object[] t, int i) {
  int ns = @PKG@.GearDefs.NS;
  int[] b = (int[]) t[3];
  StringBuilder sb = new StringBuilder();''', r'''public static String bonusText(Object[] t, int i) {
  int ns = @PKG@.GearDefs.NS;
  int[] b = (int[]) t[3];
  // 0.2.15: the mining words first (Mining Fortune +4, Mining Power +8%), then the stats; mining parts / a Mining Set name the tool they need
  String mw = @PKG@.GearMine.wordsText(((String[]) t[4])[i]);
  boolean tool = mw.length() > 0 || @PKG@.GearMine.setTier(((String[]) t[0])[i]) >= 0;
  StringBuilder sb = new StringBuilder(mw);''')
rep(r'''    else sb.append("+").append(v).append("%".equals(@PKG@.GearDefs.S_UNIT[k]) ? "% " : " ").append(@PKG@.GearDefs.S_LABEL[k]);
  }
  return sb.length() > 0 ? sb.toString() : "no bonus set up";''', r'''    else sb.append("+").append(v).append("%".equals(@PKG@.GearDefs.S_UNIT[k]) ? "% " : " ").append(@PKG@.GearDefs.S_LABEL[k]);
  }
  if (sb.length() > 0 && tool) sb.append(" (pickaxe or shovel in hand)");
  return sb.length() > 0 ? sb.toString() : "no bonus set up";''')
rep(r'''public static void tipLines(java.util.UUID owner, @BD@ d, int r, java.util.ArrayList txt, java.util.ArrayList col) {
  String sid = of(d);''', r'''public static void tipLines(java.util.UUID owner, String id, @BD@ d, int r, java.util.ArrayList txt, java.util.ArrayList col) {
  String sid = sidOf(id, d);       // 0.2.15: a metal piece without a set field shows its Mining Set''')
rep(r'''  txt.add((on ? "Full set bonus: " : "Full set (all " + n + "): ") + bonusText(t, i));
  col.add(on ? hex : @PKG@.GearDefs.C_GRAY);
}""")''', r'''  txt.add((on ? "Full set bonus: " : "Full set (all " + n + "): ") + bonusText(t, i));
  col.add(on ? hex : @PKG@.GearDefs.C_GRAY);
}""")
M(gset, "public static void tipLines(java.util.UUID owner, @BD@ d, int r, java.util.ArrayList txt, java.util.ArrayList col) { tipLines(owner, null, d, r, txt, col); }")''')
rep(r'''  if (bad.length() > 0) return "Unknown bonus words: " + bad + " - use hp+N or a live armor stat key + N (str mp cc cd chg lsteal hpr hprp def spd stam).";
  return null;''', r'''  if (bad.length() > 0) return "Unknown bonus words: " + bad + " - use hp+N or a live armor stat key + N (str mp cc cd chg lsteal hpr hprp def spd stam), or the mining words mfort mwis mpow (decimals ok).";
  return @PKG@.GearMine.setWhy(e, cs[2]);       // 0.2.15: a Mining Set takes mfort mwis mpow spd only''')
rep(r'''    @BD@ d = @PKG@.GearData.effective(s.getItemId(), s.getMetadata());
    String sid = of(d);
    if (sid == null) continue;''', r'''    @BD@ d = @PKG@.GearData.effective(s.getItemId(), s.getMetadata());
    String sid = sidOf(s.getItemId(), d);        // 0.2.15: old metal pieces count for their Mining Set by id
    if (sid == null) continue;''')
rep(r'''  for (int i = 0; i < c.length; i++) {
    if (pc[i] <= 0 || c[i] < pc[i]) continue;
    for (int k = 0; k < ns && k < tot.length; k++) tot[k] = @PKG@.GearStats.sat((long) tot[k] + (long) b[i * (ns + 1) + k]);
  }''', r'''  String[] ids = (String[]) t[0];
  for (int i = 0; i < c.length; i++) {
    if (pc[i] <= 0 || c[i] < pc[i]) continue;
    if (@PKG@.GearMine.setTier(ids[i]) >= 0) continue;      // 0.2.15: a Mining Set's stats need a pickaxe / shovel (GearMine delivers them)
    for (int k = 0; k < ns && k < tot.length; k++) tot[k] = @PKG@.GearStats.sat((long) tot[k] + (long) b[i * (ns + 1) + k]);
  }''')
rep(r'''  float h = 0.0f;
  for (int i = 0; i < c.length; i++) if (pc[i] > 0 && c[i] >= pc[i]) h = h + (float) b[i * (ns + 1) + ns];
  return h;''', r'''  float h = 0.0f;
  String[] ids = (String[]) t[0];
  for (int i = 0; i < c.length; i++) if (pc[i] > 0 && c[i] >= pc[i] && @PKG@.GearMine.setTier(ids[i]) < 0) h = h + (float) b[i * (ns + 1) + ns];
  return h;''')

# GearMine part 3 (before GearView): the tooltip lines of a piece
rep(r'''# ================================================================= GearView (spec 6): tooltip, plain lines, sigs''', r'''# ================================================================= 0.2.15 GearMine (3/4): a metal piece's tooltip lines (under the stat lines)
M(gmine, r"""
public static void lines(java.util.UUID owner, String id, @BD@ d, java.util.ArrayList txt, java.util.ArrayList col) {
  int i = index(id);
  if (i < 0 || !@PKG@.GearCfg.GM_ON) return;
  double f = fortune(i);
  double w = wisdom(i);
  if (f > 0.0) { txt.add("Mining Fortune +" + num(f)); col.add(null); }
  if (w > 0.0) { txt.add("Mining Wisdom +" + num(w) + "%"); col.add(null); }
  if (i % 4 == 0) {
    int lp = lamp(i / 4);
    if (lp > 0 && "on".equals(@PKG@.Gear.bget("acc:lamp"))) { txt.add("Lamp: " + LAMP_NAME[lp] + " light (" + LAMP_REACH[lp] + " blocks)"); col.add(null); }
  }
  if (f > 0.0 || w > 0.0) { txt.add("Mining lines work with a pickaxe or shovel in hand"); col.add(@PKG@.GearDefs.C_GRAY); }
}""")

# ================================================================= GearView (spec 6): tooltip, plain lines, sigs''')
rep(r'''  if (slot == 3) @PKG@.GearTool.lines(owner, id, d, txt, col);   // 0.2.12: tool power + Fortune by level
  // 0.2.14: an Untiered item's one orange trade-off line (its table row), then a set piece's block
  if (r == @PKG@.GearDefs.R_UT) { String un = @PKG@.GearUt.note(id); add(txt, col, un != null ? un : "Untiered - fixed stats.", hex); }
  @PKG@.GearSet.tipLines(owner, d, r, txt, col);''', r'''  if (slot == 3) @PKG@.GearTool.lines(owner, id, d, txt, col);   // 0.2.12: tool power + Fortune by level
  if (slot == 2) @PKG@.GearMine.lines(owner, id, d, txt, col);   // 0.2.15: a metal piece's mining lines
  // 0.2.14: an Untiered item's one orange trade-off line (its table row), then a set piece's block
  if (r == @PKG@.GearDefs.R_UT) { String un = @PKG@.GearUt.note(id); add(txt, col, un != null ? un : "Untiered - fixed stats.", hex); }
  @PKG@.GearSet.tipLines(owner, id, d, r, txt, col);''')

# ================================================================================================================ 9. pets:stats + GearMine part 4
rep(r'''M(gst, r"""
public static int[] extra(java.util.UUID u) {
  Object o = u == null ? null : @PKG@.Gear.bget("gear:extra:" + u);''', r'''M(gst, r"""
public static int[] gearExtra(java.util.UUID u) {
  Object o = u == null ? null : @PKG@.Gear.bget("gear:extra:" + u);''')
rep(r'''# ---- 0.2.14 GearSet (2/2): THE FULL-SET CHECK on the armor pass.''', r'''# ---- 0.2.15 PETS (SkyyPets 0.1, research/cloud/Pet-Core-Spec.md): pets:stats:<uuid> = Map String -> Number, replaced whole by SkyyPets (the
# ACTIVE profile; removed when empty / on leave). Keys = SkyyGear stat keys (str cc cd def mp dmg ...); fractions are SUMMED per key, then
# floored; unknown keys (swing.mining ...) skipped; each total within +-1,000,000. Parsed once per map object (identity) per player. It joins
# gear:extra (SkyyAccessories' string, untouched) in extra(): combat, regen, /gear "From other mods".
F(gst, "public static final java.util.concurrent.ConcurrentHashMap PCACHE = new java.util.concurrent.ConcurrentHashMap();")
M(gst, r"""
public static int[] parsePets(java.util.Map m) {
  int[] t = new int[@PKG@.GearDefs.NS];
  double[] acc = new double[t.length];
  try {
    java.util.Iterator it = new java.util.ArrayList(m.entrySet()).iterator();
    while (it.hasNext()) {
      java.util.Map.Entry e = (java.util.Map.Entry) it.next();
      if (!(e.getKey() instanceof String) || !(e.getValue() instanceof Number)) continue;
      int si = @PKG@.GearDefs.sIndex(((String) e.getKey()).trim());
      if (si < 0) continue;
      double v = ((Number) e.getValue()).doubleValue();
      if (Double.isNaN(v) || Double.isInfinite(v)) continue;
      acc[si] = acc[si] + v;
    }
  } catch (Throwable x) { @PKG@.Gear.warnOnce("pets", "pets:stats could not be read (counted as none): " + x); }
  for (int i = 0; i < t.length; i++) {
    double v = Math.floor(acc[i] + 0.000000001);
    if (v > 1000000.0) v = 1000000.0;
    if (v < -1000000.0) v = -1000000.0;
    t[i] = (int) v;
  }
  return t;
}""")
M(gst, r"""
public static int[] pets(java.util.UUID u) {
  if (u == null) return null;
  Object o = @PKG@.Gear.bget("pets:stats:" + u);
  if (!(o instanceof java.util.Map)) { PCACHE.remove(u); return null; }
  Object[] e = (Object[]) PCACHE.get(u);
  if (e != null && e[0] == o) return (int[]) e[1];
  int[] t = parsePets((java.util.Map) o);
  PCACHE.put(u, new Object[] { o, t });
  return t;
}""")
M(gst, r"""
public static int[] extra(java.util.UUID u) {
  int[] g = gearExtra(u);
  int[] p = pets(u);
  if (p == null) return g;
  if (g == null) return p;
  int[] t = new int[g.length];
  for (int i = 0; i < t.length && i < p.length; i++) t[i] = sat((long) g[i] + (long) p[i]);
  return t;
}""")
# ---- 0.2.14 GearSet (2/2): THE FULL-SET CHECK on the armor pass.''')

rep(r'''# ================================================================= GearNotice: players/<pkey>.properties noticeShown (spec 8.2)''',
    r'''# ================================================================= 0.2.15 GearMine (4/4): THE DELIVERY. compute = the worn ACTIVE metal pieces' lines (gate = Mining)
# + every complete set's mining words (+ a Mining Set's spd), capped; note (the armor pass: 1 s + every armor change) keeps it in ARM and posts
# the helmet lamp; GearTool reads ARM for Fortune / Wisdom / Mining Power with a pickaxe / shovel, the armor pass for Speed
M(gmine, "public static double r2(double v) { return (double) Math.round(v * 100.0) / 100.0; }")
M(gmine, r"""
public static double[] compute(java.util.UUID u, @IC@ armor) {
  double[] o = new double[5];
  if (!@PKG@.GearCfg.GM_ON || armor == null) return o;
  int lp = 0;
  for (int k = 0; k < armor.getCapacity(); k++) {
    @IS@ s = armor.getItemStack((short) k);
    if (s == null || s.isEmpty()) continue;
    String id = s.getItemId();
    int i = index(id);
    if (i < 0) continue;
    @BD@ d = @PKG@.GearData.effective(id, s.getMetadata());
    if (!@PKG@.GearStats.active(u, id, d)) continue;
    o[0] = o[0] + fortune(i);
    o[1] = o[1] + wisdom(i);
    if (i % 4 == 0) { int l = lamp(i / 4); if (l > lp) lp = l; }
  }
  Object[] t = @PKG@.GearCfg.STAB;
  int[] c = @PKG@.GearSet.counts(t, u, armor);
  String[] ids = (String[]) t[0];
  int[] pc = (int[]) t[2];
  int[] b = (int[]) t[3];
  String[] tx = (String[]) t[4];
  int w = @PKG@.GearDefs.NS + 1;
  for (int i = 0; i < c.length; i++) {
    if (pc[i] <= 0 || c[i] < pc[i]) continue;
    double[] ws = words(tx[i]);
    o[0] = o[0] + ws[0];
    o[1] = o[1] + ws[1];
    o[2] = o[2] + ws[2];
    if (setTier(ids[i]) >= 0) o[3] = o[3] + (double) b[i * w + I_SPD];
  }
  double fc = @PKG@.GearCfg.GM_FCAP;
  double wc = @PKG@.GearCfg.GM_WCAP;
  o[0] = r2(o[0] > fc ? fc : o[0]);
  o[1] = r2(o[1] > wc ? wc : o[1]);
  o[2] = r2(o[2]);
  o[4] = (double) lp;
  return o;
}""")
M(gmine, r"""
public static void postLamp(java.util.UUID u, int lv) {
  if (u == null) return;
  try {
    java.util.Map br = @PKG@.Gear.bridge();
    String k = "gear:lamp:" + u.toString();
    if (lv <= 0) {
      LAMP.remove(u);
      if (br.get(k) != null) br.remove(k);
      return;
    }
    Integer v = Integer.valueOf(lv);
    if (!v.equals(br.get(k))) br.put(k, v);
    LAMP.put(u, v);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("gmlamp", "gear:lamp bridge post failed: " + t); }
}""")
# leave / profile:busy: no mining lines, no lamp until the next armor pass
M(gmine, r"""
public static void clear(java.util.UUID u) {
  if (u == null) return;
  ARM.remove(u);
  postLamp(u, 0);
}""")
# fix round (engine critic LOW 1): a player who left (GearTool.GONE, set by PlayerDisconnectEvent, cleared on PlayerReady) gets no cache and
# no lamp key from a late world-thread pass - the same guard GearTool.held has
M(gmine, r"""
public static double[] note(java.util.UUID u, @IC@ armor) {
  if (u == null) return null;
  if (@PKG@.GearTool.GONE.containsKey(u)) { clear(u); return null; }
  double[] o = compute(u, armor);
  ARM.put(u, o);
  postLamp(u, (int) o[4]);
  return o;
}""")
# the held stack the tool code saw last (GearHandSys every tick): a pickaxe (1) or a shovel (2)
M(gmine, r"""
public static boolean toolHeld(java.util.UUID u) {
  if (u == null) return false;
  Object[] e = (Object[]) @PKG@.GearTool.LAST.get(u);
  if (e == null || !(e[2] instanceof double[])) return false;
  double[] st = (double[]) e[2];
  return st[0] == 1.0 || st[0] == 2.0;
}""")
# the Mining Sets' Speed for the armor pass (flat layer like armor Speed: points x speed.per / 100), only with a pickaxe / shovel in hand
M(gmine, r"""
public static float moveSpeed(java.util.UUID u, double[] a) {
  if (a == null || a[3] == 0.0 || !@PKG@.GearCfg.PART_STATS || !toolHeld(u)) return 0.0f;
  return (float) (a[3] * @PKG@.GearCfg.SPEED_PER / 100.0);
}""")
# Server Setup check of a garmor.mining row (the seven tiers always stay)
M(gmine, r"""
public static String checkRow(String key, String value) {
  String e = @PKG@.GearCfg.entryOf(key);
  if (e != null) {
    boolean ok = false;
    for (int i = 0; i < TIER.length; i++) if (TIER[i].equals(e)) ok = true;
    if (!ok) return "The mining armor tiers are copper, iron, thorium, cobalt, adamantite, mithril and onyxium.";
  }
  if (value == null) return "The seven tiers always stay - write 0 0 0 0,0 0 0 0,0 to give a tier nothing.";
  if (parseRow(value) == null) return "Write <Fortune Head Chest Legs Hands>,<Wisdom % Head Chest Legs Hands>,<lamp 0-4> - e.g. 0.5 0.7 0.5 0.3,0 0 0 0,3 (numbers 0-100).";
  return null;
}""")
M(gmine, r"""
public static String statusText() {
  if (!@PKG@.GearCfg.GM_ON) return "mining armor OFF (garmor.miningOn)";
  return "mining armor on: " + IDS.length + " metal pieces (Copper..Onyxium) are green Mining Set pieces gated by Mining, mining lines + the full-set bonus with a pickaxe or shovel in hand (armor Fortune up to " + num(@PKG@.GearCfg.GM_FCAP) + ", Wisdom up to " + num(@PKG@.GearCfg.GM_WCAP) + "%), Health / resistance " + @PKG@.GearCfg.GM_SHARE + "%, gear:lamp:<uuid>; pets:stats:<uuid> read with gear:extra";
}""")
M(gmine, r"""
public static String meText(java.util.UUID u, @IC@ armor) {
  if (!@PKG@.GearCfg.GM_ON) return "off on this server";
  if (@PKG@.Gear.busy(u)) return "paused while your profile switches";      // fix round (engine critic LOW 2): no lamp post mid-swap
  double[] a = note(u, armor);
  if (a == null || (a[0] == 0.0 && a[1] == 0.0 && a[2] == 0.0 && a[3] == 0.0)) return "none worn (or under your Mining level)";
  return "Mining Fortune +" + num(a[0]) + ", Mining Wisdom +" + num(a[1]) + "%, Mining Power +" + num(a[2]) + "%, Speed +" + num(a[3]) + (toolHeld(u) ? " - active (pickaxe / shovel in hand)" : " - hold a pickaxe or shovel");
}""")

# ================================================================= GearNotice: players/<pkey>.properties noticeShown (spec 8.2)''')

# ================================================================================================================ 10. the armor pass, cleanup, /gear, ready line
rep(r'''  if (busy) return;
  warnLines(pr, u, armor);
  float sp = 0.0f;
  if (@PKG@.GearCfg.PART_STATS && armor != null) {
    int[] t = @PKG@.GearStats.totals(u, null, armor, null, true);
    sp = (float) ((double) t[@PKG@.GearHit.I_SPD] * @PKG@.GearCfg.SPEED_PER / 100.0);
  }''', r'''  if (busy) { @PKG@.GearMine.clear(u); return; }      // 0.2.15: no mining lines / lamp while the profile swaps
  warnLines(pr, u, armor);
  double[] mine = @PKG@.GearMine.note(u, armor);        // 0.2.15: the worn mining armor (+ the helmet lamp)
  float sp = 0.0f;
  if (@PKG@.GearCfg.PART_STATS && armor != null) {
    int[] t = @PKG@.GearStats.totals(u, null, armor, null, true);
    sp = (float) ((double) t[@PKG@.GearHit.I_SPD] * @PKG@.GearCfg.SPEED_PER / 100.0);
  }
  sp = sp + @PKG@.GearMine.moveSpeed(u, mine);          // 0.2.15: a Mining Set's Speed, only with a pickaxe / shovel in hand''')
rep(r'''  @PKG@.GearSet.forget(u);
  try { @PKG@.GearMove.post(u, "@MOVESRC@", "flat", 0.0f, 0.0f, 0.0f); } catch (Throwable t) { }''', r'''  @PKG@.GearSet.forget(u);
  @PKG@.GearMine.clear(u);                    // 0.2.15: the lamp key + the mining cache
  @PKG@.GearStats.PCACHE.remove(u);           // 0.2.15: the parsed pets:stats
  try { @PKG@.GearMove.post(u, "@MOVESRC@", "flat", 0.0f, 0.0f, 0.0f); } catch (Throwable t) { }''')
rep(r'''    int[] x = @PKG@.GearStats.extra(u);
    if (x != null) msg(pr, "From other mods (gear:extra): " + totalsText(x));''', r'''    msg(pr, "Mining armor: " + @PKG@.GearMine.meText(u, inv.getArmor()));        // 0.2.15
    int[] x = @PKG@.GearStats.extra(u);
    if (x != null) msg(pr, "From other mods (gear:extra + pets:stats): " + totalsText(x));''')
rep(r'''(" + @PKG@.GearUt.statusText() + "); gear:fn:curve, gear:fn:speed, gear:fn:grant, gear:fn:tradeable;''',
    r'''(" + @PKG@.GearUt.statusText() + "); " + @PKG@.GearMine.statusText() + "; gear:fn:curve, gear:fn:speed, gear:fn:grant, gear:fn:tradeable;''')
rep(r'''SIG_CLASSES + LOOT_CLASSES + TOOL_CLASSES + G1_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''', r'''SIG_CLASSES + LOOT_CLASSES + TOOL_CLASSES + G1_CLASSES + GM_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')
rep(r'''                                                                    ",".join(LADDER), LVCAP_DEF, ODDS_DEF["mythic"], ODDS_MYTHIC_OLD, len(BAG_IDS), len(GU_LINES)))''',
    r'''                                                                    ",".join(LADDER), LVCAP_DEF, ODDS_DEF["mythic"], ODDS_MYTHIC_OLD, len(BAG_IDS), len(GU_LINES)))
print("0.2.15: mining armor - GearMine; %d pieces out of the bag pool; rows garmor.miningOn / garmor.mining (7) / garmor.miningShare / armor.fortune.cap / "
      "armor.wisdom.cap + the 7 set.mining_* rows; migrate0215 block %d lines; pets:stats read" % (len(MINE_IDS), len(GM_LINES)))''')

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", DST)
