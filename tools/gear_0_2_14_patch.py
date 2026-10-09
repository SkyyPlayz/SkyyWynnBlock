"""Derive SkyyGear/build_skyygear_0.2.14.py from the LIVE 0.2.13 (build_skyygear_0.2.13.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_13_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_14_patch.py      then      python SkyyGear/build_skyygear_0.2.14.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.14.py

0.2.14 = UNTIERED, MYTHIC AND SET - phase G1 of research/cloud/Untiered-Mythic-Spec.md (sections 1.5-1.6, 2.1-2.2, 3, 5.3, 6.1 items 1-3 + 5 +
the bag parts of 6 + 7; Skyy's answers docs/answered/gear.md 2026-10-08 / 2026-10-09, newest wins). Skyy's words: "untiered orange, mythic
for boss gear. a Set is any armor set that gives a special buff IF you have the entire set on"; "UT weapons and armor are only mob drops and
chest loot (bosses can drop them too.)" + "but you cant craft them." + "they can come from quests, but not shops."; 2026-10-09 popup:
"Mythic -> Bosses only (Recommended); UT drops -> Orange mystery bag; level-up caps -> Mythic +2, UT +3, rest +6 (Recommended); trading ->
Direct trade OK (Recommended)"; the market wall (docs/answered/economy.md 2026-10-08): Mythic + UT + Sets never bought or sold on the Bazaar /
Auctions / merchants, direct player trade allowed.
  1. UNTIERED = the 8th rarity: id "untiered", name "Untiered", ORANGE #FFAA00 (the 8th quality asset Skyy_Gear_Untiered: the vanilla
     Legendary (gold) tooltip frame + slot, the Drop_Legendary glow, QualityValue 7 - NOT 8: vanilla Technical is 8 and SkyyAuctions /
     SkyyAccessories treat a QualityValue of 8 or more as a technical item - lang line), a RARITIES row, so gear:tiers (the Auction
     House rarity filter), the Identify / Reforge pages and /gear see it. An item is Untiered ONLY when its id is in the new Untiered table
     (Server Setup -> Gear -> Rarity -> "Untiered items": ut.<item id>=<min level>,<max level>,<trade-off line>, hold the item to add it; the
     id must be gear with a bag type and NO recipe may make it - Skyy "but you cant craft them.": a row whose id a recipe makes (the build-time
     craftable pool ids + the live CraftingRecipe store) is IGNORED with one WARN and refused in Server Setup; GearRoll.craftable is false for a
     table id - fix round, critic 1). The table ships EMPTY (the first batch is phase G2). Rules: GearRoll.newDoc makes every document of a
     table id Untiered (level kept inside the row's range) and nothing else ever Untiered; a plain (undocumented) table id is stamped
     Untiered by the first inventory scan (the legacy stamp, a lazy heal - documented items keep their document); table ids never sit in
     the normal bag pool (GearPool) and are never crafted (no recipe; craft odds 0). Untiered rows of the rarity / odds / cost / xp tables:
     0 modifiers (fixed stats; the stat lines come with G2), odds 0,0,0 (forced: it never rolls), identify 1,500 + 100 / level, level up
     1,500 + 300 / level (spec 2.2), reforge REFUSED ("fixed stats" - Level up still works), xp 0. Tooltip: the normal base lines, then ONE
     orange line = the row's trade-off text ("Untiered - fixed stats" when the row has none), the "UNTIERED SWORD" footer.
     /gear rarity untiered and /gear give --rarity untiered only for table ids (a table id is always Untiered: other rarities refused).
  2. THE ORANGE MYSTERY BAG (Skyy 2026-10-09 "UT drops -> Orange mystery bag"): the 8th bag Skyy_Unid_Bag_Untiered ("Untiered Mystery Bag",
     the 0.2.11 placeholder look recoloured orange, Quirk's art later - the same one-line BAG_ART swap). Same document (SkyyUnid v2: mys =
     the bag type, r = untiered, lo / hi, at "-"), the same Identify page / /identify / Identify all / re-identify / write safety as every
     bag; identify picks a level of lo..hi that an Untiered row of that type covers, then one of those rows (uniform), and writes an
     identified Untiered document. EMPTY TABLE (today): no orange bag can be made (/gear box untiered and gear:fn:box answer "nothing fits"),
     and a bag that exists while no row fits (a row removed later) is REFUSED before any coin moves: "No Untiered sword is set up for
     Lv 10-14 on this server yet - keep the bag, it can be identified once one is added." Re-identify of an item from an orange bag stays
     inside the Untiered rows of its type. Made by /gear box untiered [level] [type] and gear:fn:box (a 6th element "untiered"); the drop
     sources (mob drops, chests, bosses, quests) come with G2 / B1 - but a single undocumented Untiered-table item that drops already becomes
     an orange bag of its type (GearUnid.fromItem: mob drops + fresh chests; gear:fn:box with that stack - Unclaimed Luggage).
  3. MYTHIC OFF THE RANDOM LADDER (Skyy 2026-10-09 "Bosses only"): its odds are 0 everywhere (ODDS_DEF mythic 0,0,0; the loader forces the
     Mythic and Untiered weights to 0 whatever the file says - one WARN for a hand-edited weight, Server Setup refuses one), the Smithing
     step-up stops at Fabled (LADDER = Normal..Fabled; craftRarity steps r < 4 only), craft.maxRarity choices end at Fabled (a file value
     "mythic" counts as fabled + one WARN). Existing Mythic items and Mythic bags stay as they are (nothing rewrites a document).
     ONE-TIME UPDATE migrate0214 (PROJECT-RULES 4): odds.mythic=0,0.5,0.6 (exactly the old default, one physical line) -> 0,0,0 (value text
     only, key / separator / line ending kept; one config-changes.log row "odds[mythic]" 0|0.5|0.6 -> 0|0|0 with status "done" - fix round 2:
     NO Undo button, because 0.2.14 refuses any Mythic odds above 0 (Skyy "Mythic -> Bosses only"), so an Undo could only fail; the way back
     is the verified History copy "before the 0.2.14 rarity update", used with a rollback to 0.2.13); a hand-edited odds.mythic is KEPT + noted (and ignored by the loader). History copy verified first, atomic write, ISO-8859-1
     bytes, run-once marker, every other byte and line ending kept.
  4. LEVEL-UP CAPS PER RARITY (Skyy 2026-10-09 "Mythic +2, UT +3, rest +6"): the table levelUp.cap.<rarity> (Normal..Fabled 6, Mythic 2, Set
     6, Untiered 3) replaces reforge.levelCap (its kit row is gone; Server Setup -> Gear -> Costs -> "Level ups at most by rarity").
     migrate0214 adds the table (+ the untiered rows of rarity / odds / cost.reforge / cost.levelUp / cost.identify / xp.reforge / xp.craft
     and the two empty table comments) as ONE block at the end of the file - only the keys the file lacks (java.util.Properties asks). The
     old reforge.levelCap line is left as it is (bytes kept) and no longer read; a HAND-EDITED value N (not 6) is carried: the six +6
     rarities start at N, Untiered at min(N, 3), Mythic at min(N, 2) - one note. Without the block (an update that could not keep its
     History copy) the loader reads reforge.levelCap the same way. Cost row cost.levelUp.untiered = 1,500 + 300 per level.
  5. SETS (Skyy 2026-10-08 "a Set is any armor set that gives a special buff IF you have the entire set on"): the table set.<set id>=<name>,
     <pieces 1-4>,<full-set bonus> (Server Setup -> Gear -> Rarity -> "Armor sets"; EMPTY - gathering sets come later). Bonus = space-separated
     "<key>+<n>": hp (max Health) or a LIVE armor stat key (str mp cc cd chg lsteal hpr hprp def spd stam); anything else is refused in Server
     Setup / skipped with one WARN by the loader. Membership = the "set" field of the piece's gear document (written by gear:fn:grant or
     /gear set <id>); the rarity label stays separate (a Set piece is green "Set", a Mythic piece of a set stays purple - spec 3).
     FULL-SET CHECK on the armor pass: GearSet.counts = the worn ACTIVE pieces (identified, level met) per set id; a set is complete when the
     count reaches its pieces; complete sets add their stat bonus to GearStats.totals (every reader: combat, regen, Speed, /gear) and their
     hp to GearArmor.lockSums (the existing Health lock plumbing: up at once, down in the 1 s tick) - only while part.stats is on. Mixed sets
     never count for each other; swapping a piece out drops the bonus on the next pass. Tooltip of a set piece: "Set: <name> (x/4)" (x =
     the owner's worn active pieces, refreshed by the inventory scan; neutral text "(4 pieces)") + "Full set (all 4): <bonus>" grey, or
     "Full set bonus: <bonus>" in the set colour while complete; an unknown set id = one grey line. /gear lists your complete sets.
  6. THE MARKET WALL (economy.md 2026-10-08 "Mythic + UT + Sets"): SkyyGear publishes market:veto["SkyyGear"] (the Auction House's existing
     veto contract: Function(ItemStack) -> null or a reason) = GearWall: a Mythic / Untiered / Set rarity document, a document with a set
     field, an Untiered-table id (plain or not), or a Mythic / Untiered / Set mystery bag -> "Mythic, Untiered and Set gear never goes on the
     market - trade it directly with another player." SkyyAuctions 0.1.3 already asks every veto when listing AND when buying (AhItem.tradeable
     / the buy path) - NO SkyyAuctions change. SkyyMerchants 0.1 already refuses whatever gear:fn:rarity answers mythic / untiered / set for a
     plain id - SkyyGear now answers "untiered" for a plain table id (the legacy stamp) - NO SkyyMerchants change. SkyyBazaar: see its own
     0.1.7 patch. Direct player trade is untouched. Bridge gear:fn:tradeable: ItemStack or Object[] { id, metadata } -> Boolean (false =
     walled), null for bad input.
  7. BRIDGE gear:fn:grant (quests / bosses / chests later): Object[] { String id, Number level (< 1 = the band start), String rarity (null /
     "" = Untiered for a table id, Set when a set is given, else the Chest odds - never Mythic / Untiered by chance), String set (armor only),
     String pool (stored as "pool" for the B1 boss pools), UUID player | null, String src (default "grant") } -> an identified ItemStack, or
     null (not gear, unknown rarity, an Untiered mismatch, a set on a non-armor or an Untiered item). Level kept inside the item's band (an
     Untiered item: its row's range). One gear.log GRANT line.
SAVED DATA PER STACK: new OPTIONAL document fields "set" and "pool" (absent = none), the rarity id "untiered", the bag id
Skyy_Unid_Bag_Untiered; nothing existing is rewritten except the legacy stamp of a PLAIN Untiered-table id (a lazy heal at the first scan).
The 8th quality asset can move the stored Skyy_Gear_* quality indices; GearQual's existing heal rewrites every stack whose index moved at its
owner's join scan (engine review 4). ROLLBACK FLOORS (for tools/deploy_set.py, reported, not edited here): rolling back to 0.2.13 is safe for
documents (0.2.13 reads "untiered" as Normal, ignores set / pool, keeps the stored fields; its own reforge.levelCap line is still in the file)
BUT an orange bag (Skyy_Unid_Bag_Untiered) and the Skyy_Gear_Untiered quality do not exist there - identify / clear every orange bag first
(none can exist while the Untiered table is empty); 0.2.13 also lets Mythic roll again only if odds.mythic is hand-set back (the update wrote 0).
ROLLBACK ALSO LIFTS THE MARKET WALL (fix round, critic 2): 0.2.13 publishes no market:veto, so the existing Mythic items (and any Set / Untiered
gear) become listable on the Auction House again, and 0.2.13 reads an Untiered item as Normal and would let it be reforged (random modifiers
that survive a roll-forward) - identify / clear Untiered items too before rolling back.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.13.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.14.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.13"' in s and s.startswith('"""SkyyGear 0.2.13 - build script'), "build_skyygear_0.2.13.py is not the live 0.2.13"
assert "untiered" not in s.lower(), "0.2.13 already has the 0.2.14 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.13 - build script (javassist via jpype). GENERATED by tools/gear_0_2_13_patch.py from the LIVE 0.2.12 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.13.py -> SkyyGear/SkyyGear-0.2.13.jar (never --deploy).

0.2.13 = ''', '''"""SkyyGear 0.2.14 - build script (javassist via jpype). GENERATED by tools/gear_0_2_14_patch.py from the LIVE 0.2.13 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.14.py -> SkyyGear/SkyyGear-0.2.14.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.14 = "):].strip() + '''

0.2.13 (the base, everything below is still true unless 0.2.14 above says otherwise):
0.2.13 = ''')
rep('VERSION = "0.2.13"', 'VERSION = "0.2.14"')

# ================================================================================================================ 1. the rarity tables
rep('''    ("set", "Set", "#55FF55", "#55FF55", "Uncommon", "Uncommon", "Drop_Uncommon"),
]''', '''    ("set", "Set", "#55FF55", "#55FF55", "Uncommon", "Uncommon", "Drop_Uncommon"),
    # 0.2.14 (Skyy LOCKED 2026-10-08 "untiered orange"): ROTMG's UT orange on the vanilla Legendary (gold) frame, slot and drop glow
    ("untiered", "Untiered", "#FFAA00", "#FFAA00", "Legendary", "Legendary", "Drop_Legendary"),
]''')
rep('''assert R_IDS == ["normal", "unique", "rare", "legendary", "fabled", "mythic", "set"]
LADDER = R_IDS[:6]          # stepping order for Smithing (never to Set)''',
    '''assert R_IDS == ["normal", "unique", "rare", "legendary", "fabled", "mythic", "set", "untiered"]
R7 = R_IDS[:7]              # 0.2.14: the seven rarities of 0.2.13 - every older block of the default file keeps exactly these rows
# 0.2.14 (Skyy 2026-10-09 "Mythic -> Bosses only"): the Smithing step-up order ends at Fabled (never to Mythic, Set or Untiered)
LADDER = R_IDS[:5]''')
rep('''              "fabled": (5, 50, 110), "mythic": (6, 60, 130), "set": (3, 45, 95)}''',
    '''              "fabled": (5, 50, 110), "mythic": (6, 60, 130), "set": (3, 45, 95), "untiered": (0, 0, 0)}''')
rep('''            "mythic": (0, 0.5, 0.6), "set": (0, 0, 0)}''',
    '''            "mythic": (0, 0, 0), "set": (0, 0, 0), "untiered": (0, 0, 0)}
# 0.2.14: Mythic left the random odds (boss-only); the 0.2.13 default line migrate0214 rewrites (only while it still holds exactly this)
ODDS_MYTHIC_OLD = (0, 0.5, 0.6)''')
rep('''              "mythic": (10000, 0), "set": (2500, 0)}
COST_I_DEF''', '''              "mythic": (10000, 0), "set": (2500, 0), "untiered": (5000, 0)}
COST_I_DEF''')
rep('''              "mythic": (2500, 150), "set": (500, 40)}
XP_R_DEF = {"normal": 5, "unique": 10, "rare": 20, "legendary": 40, "fabled": 80, "mythic": 160, "set": 40}''',
    '''              "mythic": (2500, 150), "set": (500, 40), "untiered": (1500, 100)}
XP_R_DEF = {"normal": 5, "unique": 10, "rare": 20, "legendary": 40, "fabled": 80, "mythic": 160, "set": 40, "untiered": 0}''')
rep('''XP_C_DEF = {"normal": 500, "unique": 1000, "rare": 2000, "legendary": 4000, "fabled": 8000, "mythic": 16000, "set": 4000}''',
    '''XP_C_DEF = {"normal": 500, "unique": 1000, "rare": 2000, "legendary": 4000, "fabled": 8000, "mythic": 16000, "set": 4000, "untiered": 0}''')
rep('''              "mythic": (4000, 800), "set": (1000, 200)}''',
    '''              "mythic": (4000, 800), "set": (1000, 200), "untiered": (1500, 300)}
# 0.2.14 (Skyy 2026-10-09 "Mythic +2, UT +3, rest +6"): the most level ups over the made / found level, per rarity (levelUp.cap.<id>)
LVCAP_DEF = {"normal": 6, "unique": 6, "rare": 6, "legendary": 6, "fabled": 6, "mythic": 2, "set": 6, "untiered": 3}
assert sorted(LVCAP_DEF) == sorted(R_IDS) and LVCAP_DEF["mythic"] == 2 and LVCAP_DEF["untiered"] == 3''')
rep('LU_TBLL = ["cost.levelUp.%s=%d,%d" % ((_r,) + COST_L_DEF[_r]) for _r in R_IDS]', 'LU_TBLL = ["cost.levelUp.%s=%d,%d" % ((_r,) + COST_L_DEF[_r]) for _r in R7]')
rep('XC_TBLL = ["xp.craft.%s=%d" % (_r, XP_C_DEF[_r]) for _r in R_IDS]', 'XC_TBLL = ["xp.craft.%s=%d" % (_r, XP_C_DEF[_r]) for _r in R7]')
rep('LU_ROWK = ["reforge.levelUp", "reforge.levelCap"]', 'LU_ROWK = ["reforge.levelUp"]          # 0.2.14: reforge.levelCap -> the levelUp.cap table')
rep('''            "mythic": ("#4a2a6a", "#9a56c8", "#e6b8ff"), "set": ("#1f5a2a", "#4cae5a", "#b8ffbf")}''',
    '''            "mythic": ("#4a2a6a", "#9a56c8", "#e6b8ff"), "set": ("#1f5a2a", "#4cae5a", "#b8ffbf"),
            "untiered": ("#7a4300", "#e08a00", "#ffd27a")}     # 0.2.14: the orange bag''')

# the quality value: 8+ is vanilla's Technical / Tool / Developer band (SkyyAuctions AhItem.technical refuses those) - Untiered stays at 7
rep('''        "QualityValue": _i + 1,''', '''        "QualityValue": min(_i + 1, 7),      # 0.2.14: never 8+ (vanilla Technical; SkyyAuctions calls 8+ technical)''')
rep('''    EXTRA["Server/Item/Qualities/%s.json" % QUAL_IDS[_i]] = json.dumps(_q, indent=2)''', '''    assert _q["QualityValue"] < 8, "a quality at 8 or more is 'technical' for SkyyAuctions"
    EXTRA["Server/Item/Qualities/%s.json" % QUAL_IDS[_i]] = json.dumps(_q, indent=2)''')

# ================================================================================================================ 2. config rows
rep('_rch = ",".join("%s|%s" % (r[0], r[1]) for r in RARITIES[:6])', '_rch = ",".join("%s|%s" % (r[0], r[1]) for r in RARITIES[:5])     # 0.2.14: ends at Fabled')
rep('''     "reload@%s:rarity.;check=GearCfg.checkRarity" % CFG_FILE),''', '''     "reload@%s:rarity.;check=GearCfg.checkRarity" % CFG_FILE),
    # 0.2.14 the Untiered items + the armor sets (both empty by default; G2 / quests fill them)
    ("ut", "Untiered items", "rarity", "table", "", "1", "100", "int|int|text;held;Min level|Max level|Trade-off", "", "live,danger",
     "Items that are always Untiered (orange bags, quests): level range + one trade-off line, no commas.",
     "reload@%s:ut.;entry=item;check=GearUt.checkUt" % CFG_FILE),
    ("set", "Armor sets", "rarity", "table", "", "1", "4", "text|int|text;type;Name|Pieces|Full-set bonus", "", "live,danger",
     "All pieces worn = the bonus, e.g. hp+100 def+10 (hp or an armor stat key). No commas.",
     "reload@%s:set.;check=GearSet.checkSet" % CFG_FILE),''')
rep('''     "reload@%s:odds.;check=GearCfg.checkRarityKey" % CFG_FILE),''', '''     "reload@%s:odds.;check=GearCfg.checkOdds" % CFG_FILE),''')
rep('''    ("reforge.levelCap", "Level ups at most", "costs", "int", str(LVLUP_CAP_DEF), "0", "50", "", "", "live,danger",
     "An item rises at most this many levels over the level it was made or found at (Skyy: 6).",
     "field:GearCfg.LVLUP_CAP"),''', '''    # 0.2.14: per rarity (Skyy 2026-10-09 "Mythic +2, UT +3, rest +6"), replaces reforge.levelCap
    ("levelUp.cap", "Level ups at most by rarity", "costs", "table", "", "0", "50", "int;none;Levels", "", "live,danger",
     "Most level ups over the made / found level (Skyy: Mythic 2, Untiered 3, the rest 6).",
     "reload@%s:levelUp.cap.;check=GearCfg.checkRarityKey" % CFG_FILE),''')
rep('''"steal.maxPerSec", "reforge.levelUp", "reforge.levelCap", "cost.levelUp",''', '''"steal.maxPerSec", "reforge.levelUp", "levelUp.cap", "cost.levelUp",''')
rep('''           "tool.fortune.matBonus", "tool.fortune.cap"}''', '''           "tool.fortune.matBonus", "tool.fortune.cap",
           # 0.2.14: the Untiered items (what bags / grants make) and the armor sets (combat stats) - confirm in Server Setup
           "ut", "set"}''')
# the default file: every older block keeps its seven rows (R7); the 0.2.14 block goes to the end (GU_LINES, the exact lines migrate0214 adds)
for _k in ('''    for r in R_IDS:
        L.append("rarity.%s=%d,%d,%d" % ((r,) + RARITY_DEF[r]))''', '''    for r in R_IDS:
        L.append("odds.%s=%s" % (r, ",".join(_dn(x) for x in ODDS_DEF[r])))''', '''    for r in R_IDS:
        L.append("cost.reforge.%s=%d,%d" % ((r,) + COST_R_DEF[r]))''', '''    for r in R_IDS:
        L.append("cost.identify.%s=%d,%d" % ((r,) + COST_I_DEF[r]))''', '''    for r in R_IDS:
        L.append("xp.reforge.%s=%d" % (r, XP_R_DEF[r]))'''):
    rep(_k, _k.replace("for r in R_IDS:", "for r in R7:"))
rep('''    L += ["", TL_HEAD]         # 0.2.12: the tool rows at the very end of a fresh file (no one-time update adds them)
    for k in TL_ROWK:
        scal(k)
    return "\\n".join(L) + "\\n"''', '''    L += ["", TL_HEAD]         # 0.2.12: the tool rows at the very end of a fresh file (no one-time update adds them)
    for k in TL_ROWK:
        scal(k)
    L += [""] + GU_LINES       # 0.2.14: the Untiered / Mythic / Set block (migrate0214 adds exactly these lines to an older file)
    return "\\n".join(L) + "\\n"''')
rep('''def default_text():''', '''# 0.2.14: the block at the end of a fresh file = what migrate0214 adds to an older one (marker, the levelUp.cap table, the untiered rows of the
# seven rarity tables, the two empty table comments). Plain ASCII, every line unique in the file.
GU_MARK_ID = "SkyyGear 0.2.14 rarity update"
GU_WHO = "SkyyGear 0.2.14"
GU_HEAD = "# ---- Untiered, Mythic and Set (SkyyGear 0.2.14) ----"
GU_MARK = ("# %s (Skyy 2026-10-09): Mythic only from bosses (odds 0), level ups capped per rarity (Mythic +2, Untiered +3, the rest +6), "
           "the Untiered items and the armor sets" % GU_MARK_ID)
LC_TBLC = "# ---- levelUp.cap.<id>=<most level ups over the level it was made / found at> (replaces reforge.levelCap, which is no longer read) ----"
LC_TBLL = ["levelUp.cap.%s=%d" % (_r, LVCAP_DEF[_r]) for _r in R_IDS]
UTR_C = "# ---- the untiered rows of the rarity, odds, cost and xp tables (Untiered: fixed stats, never rolled, never crafted, never reforged) ----"
UTR_K = ["rarity.untiered", "odds.untiered", "cost.reforge.untiered", "cost.levelUp.untiered", "cost.identify.untiered", "xp.reforge.untiered",
         "xp.craft.untiered"]
UTR_V = ["%d,%d,%d" % RARITY_DEF["untiered"], ",".join(_dn(x) for x in ODDS_DEF["untiered"]), "%d,%d" % COST_R_DEF["untiered"],
         "%d,%d" % COST_L_DEF["untiered"], "%d,%d" % COST_I_DEF["untiered"], "%d" % XP_R_DEF["untiered"], "%d" % XP_C_DEF["untiered"]]
UTR_L = ["%s=%s" % (_k, _v) for _k, _v in zip(UTR_K, UTR_V)]
SET_TBLC = "# ---- set.<set id>=<name>,<pieces 1-4>,<full-set bonus: hp+100 def+10 ...> (Armor sets: the bonus needs every piece worn) ----"
UT_TBLC = "# ---- ut.<item id>=<min level>,<max level>,<trade-off line> (Untiered items: always Untiered, from orange bags and quests) ----"
GU_LINES = [GU_HEAD, GU_MARK, LC_TBLC] + LC_TBLL + [UTR_C] + UTR_L + [SET_TBLC, UT_TBLC]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in GU_LINES) and all("=" not in _x for _x in (GU_HEAD, GU_MARK, UTR_C))
assert len(set(GU_LINES)) == len(GU_LINES)


def default_text():''')
rep('''assert LU_ROWL == ["reforge.levelUp=true", "reforge.levelCap=%d" % LVLUP_CAP_DEF]''', '''assert LU_ROWL == ["reforge.levelUp=true"]''')
rep('''for _r in R_IDS:
    assert _dp.get("xp.craft." + _r) == str(XP_C_DEF[_r]), _r
''', '''for _r in R_IDS:
    assert _dp.get("xp.craft." + _r) == str(XP_C_DEF[_r]), _r
# 0.2.14: the block once, at the very end (after a blank line), every line unique; the untiered rows + the levelUp.cap table read back
assert _DL[-len(GU_LINES) - 2:] == [""] + GU_LINES + [""], _DL[-len(GU_LINES) - 3:]
assert all(_DL.count(_x) == 1 for _x in GU_LINES) and DEFAULT_TEXT.count(GU_MARK_ID) == 1 and "reforge.levelCap" not in _dp
for _r in R_IDS:
    assert _dp.get("levelUp.cap." + _r) == str(LVCAP_DEF[_r]) and _dp.get("rarity." + _r) == "%d,%d,%d" % RARITY_DEF[_r], _r
    assert _dp.get("odds." + _r) == ",".join(_dn(x) for x in ODDS_DEF[_r]) and _dp.get("cost.levelUp." + _r) == "%d,%d" % COST_L_DEF[_r], _r
assert _dp.get("odds.mythic") == "0,0,0" and _dp.get("craft.maxRarity") == "fabled"
''')

# ================================================================================================================ 3. Java: tables + config
rep('''F(gdf, "public static final int NR = %d;" % NR)''', '''F(gdf, "public static final int NR = %d;" % NR)
# 0.2.14: the fixed (never random) rarities
F(gdf, "public static final int R_MY = %d;" % R_IDS.index("mythic"))
F(gdf, "public static final int R_SET = %d;" % R_IDS.index("set"))
F(gdf, "public static final int R_UT = %d;" % R_IDS.index("untiered"))''')
rep('''gcm  = mk("GearCmd", APC)''', '''gcm  = mk("GearCmd", APC)
# 0.2.14 Untiered / Mythic / Set (tools/gear_0_2_14_patch.py)
gut   = mk("GearUt")            # the Untiered table: rows, bag picks, checks
gset  = mk("GearSet")           # the armor sets: table, the full-set check, tooltip block
gwall = mk("GearWall")          # market:veto - the market wall (Mythic, Untiered, Set)
G1_CLASSES = [gut, gset, gwall]''')
rep('''        ("loot", "GearLootCmd", "Loot round counters, the bag pool and the odds", False)]''',
    '''        ("loot", "GearLootCmd", "Loot round counters, the bag pool and the odds", False),
        # 0.2.14 the armor sets
        ("set", "GearSetCmd", "Put the held armor in a set: /gear set <set id|clear>", True)]''')
rep('''F(gcf, "public static volatile int[] MIG = %s;" % jints([MIG_DEF[r] for r in MIG_IDS]))''',
    '''F(gcf, "public static volatile int[] MIG = %s;" % jints([MIG_DEF[r] for r in MIG_IDS]))
# 0.2.14: level-up caps per rarity, the Untiered table { String[] ids, int[] lo, int[] hi, String[] trade-off } and the armor sets
# { String[] ids, String[] names, int[] pieces, int[] bonus (NS + 1 per set: the stats, then hp), String[] bonus text } - each swapped whole
F(gcf, "public static volatile int[] LV_CAP = %s;" % jints([LVCAP_DEF[r] for r in R_IDS]))
F(gcf, "public static final int[] DLV_CAP = %s;" % jints([LVCAP_DEF[r] for r in R_IDS]))
F(gcf, "public static volatile Object[] UTAB = new Object[] { new String[0], new int[0], new int[0], new String[0] };")
F(gcf, "public static volatile Object[] STAB = new Object[] { new String[0], new String[0], new int[0], new int[0], new String[0] };")
F(gcf, "public static final String GU_MARK = %s;" % jstr(GU_MARK))
F(gcf, "public static final String GU_MARK_ID = %s;" % jstr(GU_MARK_ID))
F(gcf, "public static final String GU_WHO = %s;" % jstr(GU_WHO))
F(gcf, "public static final String GU_HEAD = %s;" % jstr(GU_HEAD))
F(gcf, "public static final String LC_TBLC = %s;" % jstr(LC_TBLC))
F(gcf, "public static final String UTR_C = %s;" % jstr(UTR_C))
F(gcf, "public static final String SET_TBLC = %s;" % jstr(SET_TBLC))
F(gcf, "public static final String UT_TBLC = %s;" % jstr(UT_TBLC))
F(gcf, "public static final String[] UTR_K = %s;" % jarr(UTR_K))
F(gcf, "public static final String[] UTR_V = %s;" % jarr(UTR_V))
F(gcf, "public static final String ODDS_MY_OLD = %s;" % jstr(",".join(_dn(x) for x in ODDS_MYTHIC_OLD)))
F(gcf, "public static final String ODDS_MY_NEW = %s;" % jstr(",".join(_dn(x) for x in ODDS_DEF["mythic"])))''')

# fix round (critic 1): GearUt.recipeOuts reads the live CraftingRecipe store - probe its API at build time
rep('''for c, m in ((CREPRE, "getCraftedRecipe"), (CREPRE, "isCancelled"), (CREPRE, "setCancelled"), (UNI, "getPlayer"), (CRR, "getPrimaryOutput")):''',
    '''for c, m in ((CREPRE, "getCraftedRecipe"), (CREPRE, "isCancelled"), (CREPRE, "setCancelled"), (UNI, "getPlayer"), (CRR, "getPrimaryOutput"),
             (CRR, "getAssetMap"), (CRR, "getOutputs")):''')

# GearUt part 1 (only GearCfg): the table lookups every early reader needs (GearData.legacy, GearRoll.newDoc, GearView, GearPool)
rep('''# ================================================================= Gear: settings registry helpers (research/Settings-Spec.md 1.3)''',
    '''# ================================================================= 0.2.14 GearUt (1/3): the Untiered table lookups (GearCfg.UTAB, swapped whole)
M(gut, r"""
public static int idx(Object[] t, String id) {
  if (id == null || t == null) return -1;
  String[] ids = (String[]) t[0];
  for (int i = 0; i < ids.length; i++) if (ids[i].equals(id)) return i;
  return -1;
}""")
# fix round (critic 1, Skyy "but you cant craft them."): an id that ANY recipe makes is never Untiered - its table row is ignored (one WARN),
# Server Setup refuses it (checkUt), GearRoll.craftable says no. Recipe outputs = the build-time craftable pool ids (vanilla + SkyyGear's magic
# recipes, GearPool.P_DROP false) + the LIVE CraftingRecipe store (other mods' recipes; cached, rebuilt when the store's size changes)
F(gut, "public static final String[] CRAFTED = new String[] { %s };" % ", ".join('"%s"' % _p[0] for _p in sorted(LOOT_POOL) if not _p[3]))
F(gut, "public static volatile java.util.HashSet RCP = null;")
F(gut, "public static volatile int RCP_N = -1;")
M(gut, r"""
public static java.util.HashSet recipeOuts() {
  java.util.Map m = null;
  try { m = @CRR@.getAssetMap().getAssetMap(); } catch (Throwable t) { m = null; }
  if (m == null) return new java.util.HashSet();
  int n = m.size();
  java.util.HashSet s = RCP;
  if (s != null && RCP_N == n) return s;
  s = new java.util.HashSet();
  try {
    java.util.Iterator it = new java.util.ArrayList(m.values()).iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @CRR@)) continue;
      @CRR@ rc = (@CRR@) o;
      @MQ@ po = rc.getPrimaryOutput();
      if (po != null && po.getItemId() != null) s.add(po.getItemId());
      @MQ@[] os = rc.getOutputs();
      if (os == null) continue;
      for (int i = 0; i < os.length; i++) if (os[i] != null && os[i].getItemId() != null) s.add(os[i].getItemId());
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("utrcp", "could not read the crafting recipes (only vanilla recipes count for the Untiered table): " + t); }
  RCP = s;
  RCP_N = n;
  return s;
}""")
M(gut, r"""
public static boolean crafted(String id) {
  if (id == null) return false;
  for (int i = 0; i < CRAFTED.length; i++) if (CRAFTED[i].equals(id)) return true;
  return recipeOuts().contains(id);
}""")
# the row of id, -1 = none (or a craftable id: ignored with one WARN)
M(gut, r"""
public static int idx(String id) {
  int i = idx(@PKG@.GearCfg.UTAB, id);
  if (i < 0 || !crafted(id)) return i;
  @PKG@.Gear.warnOnce("utcraft:" + id, "config.properties: ut." + id + " is ignored - a recipe makes that item and Untiered gear can never be crafted (pick an item no recipe makes)");
  return -1;
}""")
M(gut, "public static boolean has(String id) { return idx(id) >= 0; }")
M(gut, r"""
public static String note(String id) {
  Object[] t = @PKG@.GearCfg.UTAB;
  int i = idx(id);
  if (i < 0) return null;
  String n = ((String[]) t[3])[i];
  if (n == null || n.trim().length() == 0) return null;
  return n.trim();
}""")
# the row's level range { lo, hi } (null = not in the table)
M(gut, r"""
public static int[] band(String id) {
  Object[] t = @PKG@.GearCfg.UTAB;
  int i = idx(id);
  if (i < 0) return null;
  return new int[] { ((int[]) t[1])[i], ((int[]) t[2])[i] };
}""")
M(gut, r"""
public static int clampLv(String id, int L) {
  int[] b = band(id);
  if (b == null) return L;
  if (L < b[0]) return b[0];
  if (L > b[1]) return b[1];
  return L;
}""")
M(gut, "public static int size() { return ((String[]) @PKG@.GearCfg.UTAB[0]).length; }")
# /gear give --rarity and /gear rarity: only Untiered-table items are Untiered, and they always are (null = fine)
M(gut, r"""
public static String rarityWhy(String id, int r) {
  boolean ut = has(id);
  if (r == @PKG@.GearDefs.R_UT && !ut) return id + " is not in the Untiered table (Server Setup -> Gear -> Rarity -> Untiered items) - it cannot be Untiered";
  if (r != @PKG@.GearDefs.R_UT && r >= 0 && ut) return id + " is in the Untiered table - it is always Untiered";
  return null;
}""")

# ================================================================= Gear: settings registry helpers (research/Settings-Spec.md 1.3)''')

# GearCfg: parsers + checks + caps + the loader's 0.2.14 part
rep('''# every value read from the file (or the built-in defaults when there is no file: bare-JVM tests); clamps like the kit rows''',
    '''# ---- 0.2.14: a set bonus key = hp (max Health, index NS) or a LIVE stat that armor can carry; -1 = not allowed
M(gcf, r"""
public static int bonusStat(String k) {
  if (k == null) return -1;
  if (k.equals("hp")) return @PKG@.GearDefs.NS;
  int si = @PKG@.GearDefs.sIndex(k);
  if (si < 0 || @PKG@.GearDefs.S_LIVE[si] == 0 || @PKG@.GearDefs.S_SLOT[si].indexOf('a') < 0) return -1;
  return si;
}""")
# "hp+100 def+10" -> int[NS + 1] (stats, then hp; each 1..100000, summed and capped); bad tokens appended to bad (never null)
M(gcf, r"""
public static int[] parseBonus(String s, StringBuilder bad) {
  int ns = @PKG@.GearDefs.NS;
  int[] out = new int[ns + 1];
  if (s == null) return out;
  String t = s.trim();
  if (t.length() == 0) return out;
  String[] ps = t.split("\\\\s+");
  for (int i = 0; i < ps.length; i++) {
    String p = ps[i].trim();
    if (p.length() == 0) continue;
    int c = p.indexOf('+');
    long v = -1L;
    int si = -1;
    if (c > 0 && c < p.length() - 1) {
      si = bonusStat(p.substring(0, c));
      try { v = Long.parseLong(p.substring(c + 1).replace("_", "")); } catch (Throwable x) { v = -1L; }
    }
    if (si < 0 || v < 1L || v > 100000L) { if (bad != null) { if (bad.length() > 0) bad.append(' '); bad.append(p); } continue; }
    long sum = (long) out[si] + v;
    if (sum > 100000L) sum = 100000L;
    out[si] = (int) sum;
  }
  return out;
}""")
# ut.<id>=<lo>,<hi>[,<trade-off>] -> UTAB (key order; bad lines skipped with one WARN each; the id is checked where it is used - GearUt.ok)
M(gcf, r"""
public static Object[] readUt(java.util.Properties p) {
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList lo = new java.util.ArrayList();
  java.util.ArrayList hi = new java.util.ArrayList();
  java.util.ArrayList no = new java.util.ArrayList();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith("ut.") || k.length() <= 3) continue;
    String id = k.substring(3).trim();
    String v = p.getProperty(k);
    String[] cs = v == null ? new String[0] : v.replace('|', ',').split(",", 3);
    int a = -1;
    int b = -1;
    if (cs.length >= 2) {
      try { a = Integer.parseInt(cs[0].trim()); b = Integer.parseInt(cs[1].trim()); } catch (Throwable x) { a = -1; b = -1; }
    }
    if (id.length() == 0 || a < 0 || b < 0) { @PKG@.Gear.warnOnce("utrow:" + k + "=" + v, "config.properties: " + k + "=" + v + " is not <min level>,<max level>[,<trade-off line>] - ignored"); continue; }
    if (a < 1) a = 1;
    if (a > 100) a = 100;
    if (b > 100) b = 100;
    if (b < a) b = a;
    ids.add(id);
    lo.add(Integer.valueOf(a));
    hi.add(Integer.valueOf(b));
    no.add(cs.length > 2 ? cs[2].trim() : "");
  }
  int n = ids.size();
  String[] ia = new String[n];
  int[] la = new int[n];
  int[] ha = new int[n];
  String[] na = new String[n];
  for (int i = 0; i < n; i++) {
    ia[i] = (String) ids.get(i);
    la[i] = ((Integer) lo.get(i)).intValue();
    ha[i] = ((Integer) hi.get(i)).intValue();
    na[i] = (String) no.get(i);
  }
  return new Object[] { ia, la, ha, na };
}""")
# set.<id>=<name>,<pieces>,<bonus> -> STAB (key order; bad lines skipped / bad bonus words dropped with one WARN each)
M(gcf, r"""
public static Object[] readSets(java.util.Properties p) {
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList nm = new java.util.ArrayList();
  java.util.ArrayList pc = new java.util.ArrayList();
  java.util.ArrayList bo = new java.util.ArrayList();
  java.util.ArrayList tx = new java.util.ArrayList();
  java.util.Iterator it = new java.util.TreeSet(p.stringPropertyNames()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (!k.startsWith("set.") || k.length() <= 4) continue;
    String id = k.substring(4).trim();
    String v = p.getProperty(k);
    String[] cs = v == null ? new String[0] : v.replace('|', ',').split(",", 3);
    int n = -1;
    if (cs.length >= 2) { try { n = Integer.parseInt(cs[1].trim()); } catch (Throwable x) { n = -1; } }
    String name = cs.length > 0 ? cs[0].trim() : "";
    if (id.length() == 0 || name.length() == 0 || n < 1) { @PKG@.Gear.warnOnce("setrow:" + k + "=" + v, "config.properties: " + k + "=" + v + " is not <name>,<pieces 1-4>,<bonus> - ignored"); continue; }
    if (n > 4) n = 4;
    String bt = cs.length > 2 ? cs[2].trim() : "";
    StringBuilder bad = new StringBuilder();
    int[] b = parseBonus(bt, bad);
    if (bad.length() > 0) @PKG@.Gear.warnOnce("setbonus:" + k + "=" + v, "config.properties: " + k + " - these bonus words are skipped (use hp+N or a live armor stat key + N): " + bad);
    ids.add(id);
    nm.add(name);
    pc.add(Integer.valueOf(n));
    bo.add(b);
    tx.add(bt);
  }
  int c = ids.size();
  int w = @PKG@.GearDefs.NS + 1;
  String[] ia = new String[c];
  String[] na = new String[c];
  int[] pa = new int[c];
  int[] ba = new int[c * w];
  String[] ta = new String[c];
  for (int i = 0; i < c; i++) {
    ia[i] = (String) ids.get(i);
    na[i] = (String) nm.get(i);
    pa[i] = ((Integer) pc.get(i)).intValue();
    int[] b = (int[]) bo.get(i);
    for (int k2 = 0; k2 < w; k2++) ba[i * w + k2] = b[k2];
    ta[i] = (String) tx.get(i);
  }
  return new Object[] { ia, na, pa, ba, ta };
}""")
M(gcf, r"""
public static int lvCap(int r) {
  int[] a = LV_CAP;
  int i = r < 0 || r >= @PKG@.GearDefs.NR ? 0 : r;
  return a != null && i < a.length ? a[i] : 6;
}""")
# "+6 (Mythic +2, Untiered +3)" when the five random rarities and Set share one cap, else every rarity
M(gcf, r"""
public static String capText() {
  int[] a = LV_CAP;
  int nr = @PKG@.GearDefs.NR;
  boolean same = true;
  for (int i = 1; i < nr; i++) if (i != @PKG@.GearDefs.R_MY && i != @PKG@.GearDefs.R_UT && a[i] != a[0]) same = false;
  if (same) return "+" + a[0] + " (Mythic +" + a[@PKG@.GearDefs.R_MY] + ", Untiered +" + a[@PKG@.GearDefs.R_UT] + ")";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < nr; i++) { if (i > 0) sb.append(", "); sb.append(@PKG@.GearDefs.R_NAME[i]).append(" +").append(a[i]); }
  return sb.toString();
}""")
M(gcf, r"""
public static String g1Text() {
  return "Mythic boss-only (no random odds, no Smithing step-up), level ups " + capText() + ", Untiered table " + @PKG@.GearUt.size() + " item(s), armor sets " + ((String[]) STAB[0]).length + ", market wall on (market:veto)";
}""")

# every value read from the file (or the built-in defaults when there is no file: bare-JVM tests); clamps like the kit rows''')
rep('''  CRAFT_MAX = @PKG@.GearDefs.R_ID[rchoice(ptext(p, "craft.maxRarity", "fabled"), 5, 4)];''',
    '''  // 0.2.14: crafting never reaches Mythic any more (the choices end at Fabled; a file value mythic counts as fabled)
  String cmx = ptext(p, "craft.maxRarity", "fabled");
  if (@PKG@.GearDefs.rIndex(cmx) > 4) @PKG@.Gear.warnOnce("craftmax:" + cmx, "config.properties: craft.maxRarity=" + cmx + " counts as fabled - crafting never makes Mythic, Set or Untiered gear (Skyy 2026-10-09)");
  CRAFT_MAX = @PKG@.GearDefs.R_ID[rchoice(cmx, 4, 4)];''')
rep('''  R_MODS = rm; R_LO = rl; R_HI = rh;''', '''  // 0.2.14: Mythic is boss-only and Untiered never rolls (Skyy 2026-10-09) - their weights are 0 whatever the file says (one WARN)
  for (int i = 0; i < nr; i++) {
    if (i != @PKG@.GearDefs.R_MY && i != @PKG@.GearDefs.R_UT) continue;
    if (oc[i] > 0.0 || om[i] > 0.0 || ox[i] > 0.0) @PKG@.Gear.warnOnce("oddsfix:" + i + ":" + oc[i] + ":" + om[i] + ":" + ox[i], "config.properties: odds." + @PKG@.GearDefs.R_ID[i] + " is ignored - " + (i == @PKG@.GearDefs.R_MY ? "Mythic gear only comes from bosses" : "Untiered gear only comes from its orange bags and quests") + " (Skyy 2026-10-09); it counts as 0,0,0");
    oc[i] = 0.0; om[i] = 0.0; ox[i] = 0.0;
  }
  // 0.2.14: levelUp.cap.<rarity>; a missing line takes the old reforge.levelCap (Untiered / Mythic never above their own default), else the default
  double[] olc = cells(p.getProperty("reforge.levelCap"), 1);
  int[] lc = new int[nr];
  for (int i = 0; i < nr; i++) {
    double[] c = cells(p.getProperty("levelUp.cap." + @PKG@.GearDefs.R_ID[i]), 1);
    if (c != null) lc[i] = (int) clampd(c[0], 0.0, 50.0);
    else if (olc != null) {
      int ov = (int) clampd(olc[0], 0.0, 50.0);
      lc[i] = (i == @PKG@.GearDefs.R_MY || i == @PKG@.GearDefs.R_UT) && ov > DLV_CAP[i] ? DLV_CAP[i] : ov;
    } else lc[i] = DLV_CAP[i];
  }
  Object[] utab = readUt(p);
  Object[] stab = readSets(p);
  LV_CAP = lc; UTAB = utab; STAB = stab;
  R_MODS = rm; R_LO = rl; R_HI = rh;''')
rep('''M(gcf, "public static int craftMax() { return rchoice(CRAFT_MAX, 5, 4); }")''', '''M(gcf, "public static int craftMax() { return rchoice(CRAFT_MAX, 4, 4); }")''')
rep('''  if (r < 0 || !@PKG@.GearDefs.R_ID[r].equals(e)) return "Unknown rarity " + e + " - use normal, unique, rare, legendary, fabled, mythic or set (lower case).";
  return null;
}""")''', '''  if (r < 0 || !@PKG@.GearDefs.R_ID[r].equals(e)) return "Unknown rarity " + e + " - use normal, unique, rare, legendary, fabled, mythic, set or untiered (lower case).";
  return null;
}""")
# 0.2.14: the odds rows - Mythic (boss-only) and Untiered (orange bags) keep 0,0,0
M(gcf, r"""
public static String checkOdds(String key, String value) {
  String bad = checkRarityKey(key, value);
  if (bad != null || value == null) return bad;
  int r = @PKG@.GearDefs.rIndex(entryOf(key));
  if (r != @PKG@.GearDefs.R_MY && r != @PKG@.GearDefs.R_UT) return null;
  double[] c = cells(value, 3);
  if (c != null && (c[0] > 0.0 || c[1] > 0.0 || c[2] > 0.0)) return r == @PKG@.GearDefs.R_MY ? "Mythic gear only comes from bosses (Skyy 2026-10-09) - its odds stay 0,0,0." : "Untiered gear only comes from its orange bags and quests - its odds stay 0,0,0.";
  return null;
}""")''')

# ================================================================================================================ 4. the one-time update
rep('''# 0.2.1 ready line part: the base stats in force (live values)''', '''# ---- 0.2.14 ONE-TIME UPDATE migrate0214 (PROJECT-RULES section 4; tools/gear_0_2_14_patch.py item 3 + 4). Pure text step: null = the marker
# is already in a comment line (a fresh 0.2.14 file carries it). Else { new text, "odds.mythic 0,0.5,0.6 -> 0,0,0" ("" = no value changed),
# String[] notes, String[] log rows (key, old, new), "levelUp.cap.normal, ..." (what was added) }. odds.mythic: every ONE-LINE entry holding
# exactly the 0.2.13 default is rewritten when the LAST entry (the one Properties keeps) holds it (value text only: key, separator, CR kept).
# The block (blank line + head + marker + the levelUp.cap table comment and every missing levelUp.cap line + the untiered table comment and
# every missing untiered line + the two table comments) goes to the END of the file (chEnd: the end-of-file continuation trap). The six +6
# rarities carry a hand-edited reforge.levelCap N (Untiered / Mythic at most their default); keys already there are kept + noted.
M(gcf, r"""
public static Object[] guUpdate(String text) {
  String[] raw = text.split("\\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(GU_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  java.util.ArrayList oddsAt = new java.util.ArrayList();
  int lastOdds = -1;
  boolean lastOne = false;
  int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    String key = @PKG@.CfgFile.key(s);
    if (key != null && key.equals("odds.mythic")) {
      lastOdds = k;
      lastOne = e == k;
      if (e == k && @PKG@.CfgFile.value(l, k).trim().equals(ODDS_MY_OLD)) oddsAt.add(Integer.valueOf(k));
    }
    k = e + 1;
  }
  StringBuilder chg = new StringBuilder();
  java.util.ArrayList notes = new java.util.ArrayList();
  java.util.ArrayList rows = new java.util.ArrayList();
  String ov = pp.getProperty("odds.mythic");
  boolean rewrite = ov != null && ov.trim().equals(ODDS_MY_OLD) && lastOne && oddsAt.contains(Integer.valueOf(lastOdds));
  if (rewrite) {
    chg.append("odds.mythic ").append(ODDS_MY_OLD).append(" -> ").append(ODDS_MY_NEW);
    rows.add("odds[mythic]");
    rows.add(ODDS_MY_OLD.replace(',', '|'));
    rows.add(ODDS_MY_NEW.replace(',', '|'));
  } else if (ov != null) {
    notes.add("odds.mythic=" + @PKG@.CfgRows.oneLine(ov.trim()) + " kept (not the 0.2.13 default " + ODDS_MY_OLD + ") - the loader counts it as 0,0,0: Mythic gear only comes from bosses now");
  }
  int carry = -1;
  String oc = pp.getProperty("reforge.levelCap");
  if (oc != null) {
    double[] c = cells(oc, 1);
    if (c != null && (int) clampd(c[0], 0.0, 50.0) != DLV_CAP[0]) {
      carry = (int) clampd(c[0], 0.0, 50.0);
      notes.add("reforge.levelCap=" + carry + " kept (custom) - it is no longer read; the levelUp.cap rows of normal, unique, rare, legendary, fabled and set start at " + carry + ", untiered at " + (carry < DLV_CAP[@PKG@.GearDefs.R_UT] ? carry : DLV_CAP[@PKG@.GearDefs.R_UT]) + ", mythic at " + (carry < DLV_CAP[@PKG@.GearDefs.R_MY] ? carry : DLV_CAP[@PKG@.GearDefs.R_MY]));
    } else if (c == null) {
      notes.add("reforge.levelCap=" + @PKG@.CfgRows.oneLine(oc) + " kept - it is not a number (and no longer read); the levelUp.cap rows start at their defaults");
    }
  }
  StringBuilder added = new StringBuilder();
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add("");
  blk.add(GU_HEAD);
  blk.add(GU_MARK);
  boolean tc = false;
  for (int i = 0; i < @PKG@.GearDefs.NR; i++) {
    String lk = "levelUp.cap." + @PKG@.GearDefs.R_ID[i];
    if (pp.getProperty(lk) != null) { notes.add(lk + " is already in the file - kept"); continue; }
    int v = DLV_CAP[i];
    if (carry >= 0) v = (i == @PKG@.GearDefs.R_MY || i == @PKG@.GearDefs.R_UT) && carry > DLV_CAP[i] ? DLV_CAP[i] : carry;
    if (!tc) { blk.add(LC_TBLC); tc = true; }
    blk.add(lk + "=" + v);
    if (added.length() > 0) added.append(", ");
    added.append(lk);
  }
  tc = false;
  for (int i = 0; i < UTR_K.length; i++) {
    if (pp.getProperty(UTR_K[i]) != null) { notes.add(UTR_K[i] + " is already in the file - kept"); continue; }
    if (!tc) { blk.add(UTR_C); tc = true; }
    blk.add(UTR_K[i] + "=" + UTR_V[i]);
    if (added.length() > 0) added.append(", ");
    added.append(UTR_K[i]);
  }
  blk.add(SET_TBLC);
  blk.add(UT_TBLC);
  String crDef = text.indexOf("\\r\\n") >= 0 ? "\\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    if (rewrite && oddsAt.contains(Integer.valueOf(i))) {
      String s2 = (String) l.get(i);
      out.add(s2.substring(0, @PKG@.CfgFile.valStart(s2)) + ODDS_MY_NEW + (raw[i].endsWith("\\r") ? "\\r" : ""));
    } else out.add(raw[i]);
  }
  chPut(out, chEnd(l, tail, raw), blk, crDef);
  StringBuilder sb = new StringBuilder(text.length() + 2048);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), chg.toString(), (String[]) notes.toArray(new String[0]), (String[]) rows.toArray(new String[0]), added.toString() };
}""")
# one config-changes.log line in the kit's table-row format. Status "done" (fix round 2, critic 1): SkyyMenu offers Undo only on "ok" rows, and an
# Undo of odds[mythic] back to 0|0.5|0.6 is always refused by checkOdds (Mythic is boss-only) - the row records the change without a dead button
M(gcf, r"""
public static String guLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\\t" + GU_WHO + "\\t-\\tupdate\\t" + @PKG@.CfgRows.oneLine(k) + "\\t" + o + "\\t" + n + "\\tdone";
}""")
# setup(), right after migrate025 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes),
# the change-log row, one INFO line (+ one per note), gear.log; "" = nothing done (no file, marker already there, or a failure - WARN, file
# untouched, the next start tries again; the loader then forces the Mythic odds to 0 and reads the caps / tables on their defaults anyway)
M(gcf, r"""
public static synchronized String migrate0214() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = guUpdate(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), GU_WHO, "before the 0.2.14 rarity update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated to the 0.2.14 rarity rules: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is - Mythic odds count as 0 anyway, the level up caps run on their defaults; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(guLog(rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] notes = (String[]) r[2];
    String add = (String) r[4];
    String msg = chg.length() > 0
      ? "config.properties updated to the 0.2.14 rarity rules: " + chg + " (Mythic gear only comes from bosses now; the old file is kept in config-history)"
      : "config.properties: odds.mythic did not hold the 0.2.13 default - no value changed (0.2.14 marker added)";
    if (add.length() > 0) msg = msg + "; new settings: " + add;
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.2.14 rarity rules: " + (chg.length() > 0 ? chg : "no value changed") + (add.length() > 0 ? "; added " + add : "") + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not update config.properties to the 0.2.14 rarity rules (the file is used as it is): " + t);
    return "";
  }
}""")
# 0.2.1 ready line part: the base stats in force (live values)''')

# ================================================================================================================ 5. documents + rolls
rep('''M(gdt, "public static @BD@ legacy(String id) { return base(kindFor(id), 0, true, \\"legacy\\"); }")''',
    '''# 0.2.14: an Untiered-table id is stamped Untiered (UTs are defined by their id - the lazy heal of a plain UT item at its first scan)
M(gdt, "public static @BD@ legacy(String id) { return base(kindFor(id), @PKG@.GearUt.has(id) ? @PKG@.GearDefs.R_UT : 0, true, \\"legacy\\"); }")''')
rep('''  if (c > 0.0 && r < max && r < 5 && RNG.nextDouble() * 100.0 < c) r = r + 1;''',
    '''  // 0.2.14: the step-up ladder ends at Fabled (Mythic is boss-only)
  if (c > 0.0 && r < max && r < 4 && RNG.nextDouble() * 100.0 < c) r = r + 1;''')
rep('''public static @BD@ newDoc(String id, int r, boolean ident, String src, int lvl) {
  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), r, ident, src);''', '''public static @BD@ newDoc(String id, int r, boolean ident, String src, int lvl) {
  // 0.2.14: an Untiered-table id is always Untiered (its level inside the row's range); nothing else is ever Untiered
  if (@PKG@.GearUt.has(id)) { r = @PKG@.GearDefs.R_UT; if (lvl >= 0) lvl = @PKG@.GearUt.clampLv(id, lvl); }
  else if (r == @PKG@.GearDefs.R_UT) r = 0;
  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), r, ident, src);''')
rep('''    try { v = @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && !excluded(id, ex); } catch (Throwable x) { v = false; }''',
    '''    try { v = @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && !excluded(id, ex) && !@PKG@.GearUt.has(id); } catch (Throwable x) { v = false; }''')

# fix round (critic 1): an Untiered-table id never gets a crafted document (belt and braces: GearUt.idx already ignores a row whose id a recipe
# makes, so a table id has no recipe - this keeps the /craft bridge (gear:fn mode 8) and the bench craft systems from ever minting one)
rep('''public static boolean craftable(String id) {
  if (id == null) return false;
  if (@PKG@.GearData.isGear(id)) return true;''', '''public static boolean craftable(String id) {
  if (id == null || @PKG@.GearUt.has(id)) return false;
  if (@PKG@.GearData.isGear(id)) return true;''')
# GearUt part 2 (after GearPool): the orange-bag picks + the kit check
rep('''# ---------------------------------------------------------------- GearUnid (the mystery bags)''', '''# ---------------------------------------------------------------- 0.2.14 GearUt (2/3): the orange-bag picks (rows of one bag type, -1 = any)
# a usable row: the item exists, is gear, has a bag type and no recipe makes it
M(gut, r"""
public static boolean ok(Object[] t, int i) {
  try {
    String id = ((String[]) t[0])[i];
    return @PKG@.Gear.item(id) != null && @PKG@.GearData.isGear(id) && @PKG@.GearPool.typeOfId(id) >= 0 && !crafted(id);
  } catch (Throwable x) { return false; }
}""")
M(gut, r"""
public static boolean match(Object[] t, int i, int ty, int L) {
  if (!ok(t, i)) return false;
  if (ty >= 0 && @PKG@.GearPool.typeOfId(((String[]) t[0])[i]) != ty) return false;
  return L < 0 || (((int[]) t[1])[i] <= L && L <= ((int[]) t[2])[i]);
}""")
M(gut, r"""
public static int count() {
  Object[] t = @PKG@.GearCfg.UTAB;
  int n = 0;
  for (int i = 0; i < ((String[]) t[0]).length; i++) if (ok(t, i)) n++;
  return n;
}""")
M(gut, r"""
public static boolean[] levels(int ty) {
  boolean[] out = new boolean[102];
  Object[] t = @PKG@.GearCfg.UTAB;
  int[] lo = (int[]) t[1];
  int[] hi = (int[]) t[2];
  for (int i = 0; i < lo.length; i++) {
    if (!match(t, i, ty, -1)) continue;
    for (int L = lo[i]; L <= hi[i] && L <= 101; L++) if (L >= 0) out[L] = true;
  }
  return out;
}""")
M(gut, r"""
public static int levelCount(int ty, int lo, int hi) {
  boolean[] lv = levels(ty);
  int n = 0;
  for (int L = lo; L <= hi; L++) if (L >= 1 && L <= 101 && lv[L]) n++;
  return n;
}""")
M(gut, r"""
public static int pickLevel(int ty, int lo, int hi) {
  boolean[] lv = levels(ty);
  int n = 0;
  for (int L = lo; L <= hi; L++) if (L >= 1 && L <= 101 && lv[L]) n++;
  if (n == 0) return -1;
  int k = @PKG@.GearRoll.RNG.nextInt(n);
  for (int L = lo; L <= hi; L++) {
    if (L < 1 || L > 101 || !lv[L]) continue;
    if (k == 0) return L;
    k--;
  }
  return -1;
}""")
M(gut, r"""
public static String pickItem(int ty, int L) {
  Object[] t = @PKG@.GearCfg.UTAB;
  String[] ids = (String[]) t[0];
  int n = 0;
  for (int i = 0; i < ids.length; i++) if (match(t, i, ty, L)) n++;
  if (n == 0) return null;
  int k = @PKG@.GearRoll.RNG.nextInt(n);
  for (int i = 0; i < ids.length; i++) {
    if (!match(t, i, ty, L)) continue;
    if (k == 0) return ids[i];
    k--;
  }
  return null;
}""")
# a random bag type among the usable rows covering L (L < 0 = any level); -1 = none
M(gut, r"""
public static int pickType(int L) {
  Object[] t = @PKG@.GearCfg.UTAB;
  String[] ids = (String[]) t[0];
  int[] tys = new int[ids.length];
  int n = 0;
  for (int i = 0; i < ids.length; i++) {
    if (!match(t, i, -1, L)) continue;
    int ty = @PKG@.GearPool.typeOfId(ids[i]);
    boolean seen = false;
    for (int j = 0; j < n; j++) if (tys[j] == ty) seen = true;
    if (!seen) { tys[n] = ty; n++; }
  }
  if (n == 0) return -1;
  return tys[@PKG@.GearRoll.RNG.nextInt(n)];
}""")
# { lo, hi, centre }: the nearest covered level to L, +-half around it, ends trimmed inward to covered levels (GearPool.range's rule)
M(gut, r"""
public static int[] range(int ty, int L, int half) {
  if (L < 1) L = 1;
  if (L > 100) L = 100;
  if (half < 0) half = 0;
  boolean[] lv = levels(ty);
  int best = -1;
  for (int d = 0; d <= 100 && best < 0; d++) {
    if (L - d >= 1 && lv[L - d]) best = L - d;
    else if (L + d <= 100 && lv[L + d]) best = L + d;
  }
  if (best < 0) return null;
  int lo = best - half;
  int hi = best + half;
  if (lo < 1) lo = 1;
  if (hi > 100) hi = 100;
  while (lo < best && !lv[lo]) lo++;
  while (hi > best && !lv[hi]) hi--;
  return new int[] { lo, hi, best };
}""")
# why an orange bag cannot be opened now (null = it can): no usable Untiered row of its type covers its range
M(gut, r"""
public static String why(int ty, int lo, int hi) {
  if (levelCount(ty, lo, hi) > 0) return null;
  String tn = ty >= 0 && ty < @PKG@.GearPool.T_NAME.length ? @PKG@.GearPool.T_NAME[ty].toLowerCase() : "item";
  return "No Untiered " + tn + " is set up for " + (lo == hi ? "Lv " + lo : "Lv " + lo + "-" + hi) + " on this server yet - keep the bag, it can be identified once one is added.";
}""")
# Server Setup check of a ut row: the held item must be gear with a bag type; <min>,<max>[,<trade-off>] 1-100, no commas in the text
M(gut, r"""
public static String checkUt(String key, String value) {
  String e = @PKG@.GearCfg.entryOf(key);
  if (e != null) {
    if (!@PKG@.GearData.isGear(e)) return e + " is not gear - only weapons and armor can be Untiered.";
    if (@PKG@.GearPool.typeOfId(e) < 0) return e + " has no mystery-bag type (sword, bow, staff, chestplate ...) - it cannot be Untiered yet.";
    if (crafted(e)) return e + " can be crafted (a recipe makes it) - Untiered gear is never craftable, pick an item no recipe makes.";
  }
  if (value == null) return null;
  String[] cs = value.replace('|', ',').split(",", -1);
  if (cs.length < 2 || cs.length > 3) return "Write <min level>,<max level>,<trade-off line> (no commas in the line).";
  int a = -1;
  int b = -1;
  try { a = Integer.parseInt(cs[0].trim()); b = Integer.parseInt(cs[1].trim()); } catch (Throwable x) { return "The levels must be whole numbers 1-100."; }
  if (a < 1 || a > 100 || b < 1 || b > 100) return "The levels must be 1-100.";
  if (b < a) return "Max level must be at least Min level.";
  return null;
}""")
M(gut, r"""
public static String statusText() {
  return "Untiered table " + count() + " / " + size() + " usable item(s)";
}""")

# ---------------------------------------------------------------- GearUnid (the mystery bags)''')

# GearUnid: the Untiered branch of why / rerollWhy / pick + the bag texts
rep('''  if (@PKG@.GearPool.levelCount(ty, at(d), lo(d), hi(d)) == 0) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(d), hi(d)) + " any more - an admin can help.";
  return null;''', '''  if (rar(d) == @PKG@.GearDefs.R_UT) return @PKG@.GearUt.why(ty, lo(d), hi(d));       // 0.2.14: the orange bag reads the Untiered table
  if (@PKG@.GearPool.levelCount(ty, at(d), lo(d), hi(d)) == 0) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(d), hi(d)) + " any more - an admin can help.";
  return null;''')
rep('''  if (@PKG@.GearPool.levelCount(ty, at(b), lo(b), hi(b)) == 0) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(b), hi(b)) + " any more.";''',
    '''  if (rar(b) == @PKG@.GearDefs.R_UT) return @PKG@.GearUt.why(ty, lo(b), hi(b));       // 0.2.14
  if (@PKG@.GearPool.levelCount(ty, at(b), lo(b), hi(b)) == 0) return "No " + typeName(ty).toLowerCase() + " exists in " + rangeText(lo(b), hi(b)) + " any more.";''')
rep('''  if (ty < 0) return null;
  int L = @PKG@.GearPool.pickLevel(ty, at, lo, hi);
  if (L < 0) return null;
  String id = @PKG@.GearPool.pickItem(ty, at, L);''', '''  if (ty < 0) return null;
  // 0.2.14: an orange bag picks among the Untiered rows of its type (newDoc makes the document Untiered)
  boolean ut = r == @PKG@.GearDefs.R_UT;
  int L = ut ? @PKG@.GearUt.pickLevel(ty, lo, hi) : @PKG@.GearPool.pickLevel(ty, at, lo, hi);
  if (L < 0) return null;
  String id = ut ? @PKG@.GearUt.pickItem(ty, L) : @PKG@.GearPool.pickItem(ty, at, L);''')
rep('''M(gunid, "public static String title(@BD@ d) { return \\"Unidentified \\" + typeName(type(d)); }")''',
    '''M(gunid, "public static String title(@BD@ d) { return \\"Unidentified \\" + (rar(d) == @PKG@.GearDefs.R_UT ? \\"Untiered \\" : \\"\\") + typeName(type(d)); }")''')
rep('''  txt.add("Unidentified - which " + typeName(ty).toLowerCase() + " it is, its exact level and its modifiers are decided when you identify it."); col.add(@PKG@.GearDefs.C_GRAY);''',
    '''  if (r == @PKG@.GearDefs.R_UT) { txt.add("Unidentified - which Untiered " + typeName(ty).toLowerCase() + " it is and its exact level are decided when you identify it. Untiered gear has fixed stats and one trade-off."); col.add(@PKG@.GearDefs.C_GRAY); }
  else { txt.add("Unidentified - which " + typeName(ty).toLowerCase() + " it is, its exact level and its modifiers are decided when you identify it."); col.add(@PKG@.GearDefs.C_GRAY); }''')

# GearUt part 3 (after GearUnid.make): a new orange bag
rep('''# ---------------------------------------------------------------- GearLoot (extra mob roll, chest level + extra bag, counters)''',
    '''# ---------------------------------------------------------------- 0.2.14 GearUt (3/3): a new orange bag at level L (type ty, -1 = any type a row
# covers near L); null = no usable Untiered row (the table is empty today)
M(gut, r"""
public static @IS@ bag(int L, int ty, String src, String ls, int tier) {
  int[] rg = range(ty, L, @PKG@.GearCfg.RANGE_HALF);
  if (rg == null) return null;
  int t = ty >= 0 ? ty : pickType(rg[2]);
  if (t < 0) return null;
  if (ty < 0) rg = range(t, rg[2], @PKG@.GearCfg.RANGE_HALF);
  if (rg == null) return null;
  return @PKG@.GearUnid.make(t, 0, @PKG@.GearDefs.R_UT, rg[0], rg[1], src, ls, tier);
}""")

# ---------------------------------------------------------------- GearLoot (extra mob roll, chest level + extra bag, counters)''')
rep('''    int shift = tier >= 4 ? 21 : (tier >= 3 ? 11 : 0);
    if (a[0] instanceof @IS@) {''', '''    int shift = tier >= 4 ? 21 : (tier >= 3 ? 11 : 0);
    // 0.2.14: a 6th element "untiered" = an orange bag (a type key or null; never from an ItemStack)
    String rq = a.length > 5 && a[5] instanceof String ? ((String) a[5]).trim() : "";
    if (rq.length() > 0 && @PKG@.GearDefs.rIndex(rq) == @PKG@.GearDefs.R_UT) {
      if (a[0] instanceof @IS@) return null;
      int tu = a[0] instanceof String ? @PKG@.GearPool.typeIdx((String) a[0]) : -1;
      if (a[0] instanceof String && tu < 0) return null;
      return @PKG@.GearUt.bag(L, tu, src, "bridge", tier);
    }
    if (a[0] instanceof @IS@) {''')

# ================================================================================================================ 6. sets
# GearSet part (a): before GearView (lookups, the tooltip block, the Server Setup check)
rep('''# ================================================================= GearView (spec 6): tooltip, plain lines, sigs''', '''# ================================================================= 0.2.14 GearSet (1/2): the armor sets table (GearCfg.STAB, swapped whole), the
# tooltip block, the Server Setup check. WORN: profile key (Gear.pkey, PROFILES-CONTRACT rule 2) -> Object[] { the STAB it was counted with,
# int[] worn active pieces per set }
F(gset, "public static final java.util.concurrent.ConcurrentHashMap WORN = new java.util.concurrent.ConcurrentHashMap();")
M(gset, r"""
public static int idx(Object[] t, String sid) {
  if (sid == null || t == null) return -1;
  String[] ids = (String[]) t[0];
  String s = sid.trim();
  for (int i = 0; i < ids.length; i++) if (ids[i].equalsIgnoreCase(s)) return i;
  return -1;
}""")
M(gset, "public static int idx(String sid) { return idx(@PKG@.GearCfg.STAB, sid); }")
# the set id a gear document carries (null = none)
M(gset, r"""
public static String of(@BD@ d) {
  String s = @PKG@.GearData.str(d, "set", null);
  if (s == null) return null;
  s = s.trim();
  return s.length() == 0 ? null : s;
}""")
M(gset, "public static String name(Object[] t, int i) { return ((String[]) t[1])[i]; }")
M(gset, "public static int pieces(Object[] t, int i) { return ((int[]) t[2])[i]; }")
M(gset, r"""
public static String bonusText(Object[] t, int i) {
  int ns = @PKG@.GearDefs.NS;
  int[] b = (int[]) t[3];
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k <= ns; k++) {
    int v = b[i * (ns + 1) + k];
    if (v == 0) continue;
    if (sb.length() > 0) sb.append(", ");
    if (k == ns) sb.append("+").append(v).append(" Health");
    else sb.append("+").append(v).append("%".equals(@PKG@.GearDefs.S_UNIT[k]) ? "% " : " ").append(@PKG@.GearDefs.S_LABEL[k]);
  }
  return sb.length() > 0 ? sb.toString() : "no bonus set up";
}""")
M(gset, r"""
public static int worn(java.util.UUID u, Object[] t, int i) {
  if (u == null) return -1;
  Object[] w = (Object[]) WORN.get(@PKG@.Gear.pkey(u));
  Object w0 = w == null ? null : w[0];
  Object tt = t;
  if (w == null || w0 != tt) return -1;
  int[] c = (int[]) w[1];
  return i >= 0 && i < c.length ? c[i] : -1;
}""")
# the tooltip block of a set piece: "Set: <name> (x/4)" + the bonus line (set colour while complete, grey otherwise); a Mythic piece in purple
M(gset, r"""
public static void tipLines(java.util.UUID owner, @BD@ d, int r, java.util.ArrayList txt, java.util.ArrayList col) {
  String sid = of(d);
  if (sid == null) return;
  Object[] t = @PKG@.GearCfg.STAB;
  int i = idx(t, sid);
  String hex = @PKG@.GearDefs.R_HEX[r == @PKG@.GearDefs.R_MY ? @PKG@.GearDefs.R_MY : @PKG@.GearDefs.R_SET];
  if (i < 0) { txt.add("Set: " + sid + " (not set up on this server)"); col.add(@PKG@.GearDefs.C_GRAY); return; }
  int n = pieces(t, i);
  int w = worn(owner, t, i);
  txt.add("Set: " + name(t, i) + (w >= 0 ? " (" + (w > n ? n : w) + "/" + n + ")" : " (" + n + " pieces)"));
  col.add(hex);
  boolean on = w >= n;
  txt.add((on ? "Full set bonus: " : "Full set (all " + n + "): ") + bonusText(t, i));
  col.add(on ? hex : @PKG@.GearDefs.C_GRAY);
}""")
# Server Setup check of a set row: id 1-40 of a-z 0-9 _ -; <name>,<pieces 1-4>,<bonus words>; no commas in the name / bonus
M(gset, r"""
public static String checkSet(String key, String value) {
  String e = @PKG@.GearCfg.entryOf(key);
  if (e != null) {
    if (e.length() < 1 || e.length() > 40) return "A set id is 1-40 letters (e.g. cobalt_quest).";
    for (int i = 0; i < e.length(); i++) {
      char c = e.charAt(i);
      if (!((c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_' || c == '-')) return "A set id uses a-z, 0-9, _ and - only (e.g. cobalt_quest).";
    }
  }
  if (value == null) return null;
  String[] cs = value.replace('|', ',').split(",", -1);
  if (cs.length != 3) return "Write <name>,<pieces>,<bonus> - e.g. Cobalt Guard,4,hp+100 (no commas inside).";
  if (cs[0].trim().length() == 0) return "Give the set a name.";
  int n = -1;
  try { n = Integer.parseInt(cs[1].trim()); } catch (Throwable x) { n = -1; }
  if (n < 1 || n > 4) return "Pieces must be 1-4 (Head, Chest, Hands, Legs).";
  StringBuilder bad = new StringBuilder();
  @PKG@.GearCfg.parseBonus(cs[2], bad);
  if (bad.length() > 0) return "Unknown bonus words: " + bad + " - use hp+N or a live armor stat key + N (str mp cc cd chg lsteal hpr hprp def spd stam).";
  return null;
}""")

# ================================================================= GearView (spec 6): tooltip, plain lines, sigs''')
# GearSet part (b): the full-set check (needs GearStats.active / sat), before GearStats.totals
rep('''# design review 2: THE totals (spec 4.3 T): the weapon's modifiers''', '''# ---- 0.2.14 GearSet (2/2): THE FULL-SET CHECK on the armor pass. counts = per set of the table, the worn ACTIVE pieces (identified, level met)
# carrying its id (Head / Chest / Hands / Legs: one each, so mixed sets never help each other); complete = count >= its pieces. note() keeps
# the counts for the tooltip (the inventory scan + every totals pass); addTo adds the complete sets' stats to the totals, hp() their Health
M(gset, r"""
public static int[] counts(Object[] t, java.util.UUID u, @IC@ armor) {
  int[] c = new int[((String[]) t[0]).length];
  if (armor == null || c.length == 0) return c;
  for (int k = 0; k < armor.getCapacity(); k++) {
    @IS@ s = armor.getItemStack((short) k);
    if (s == null || s.isEmpty() || @PKG@.GearData.slotOf(s.getItemId()) != 2) continue;
    @BD@ d = @PKG@.GearData.effective(s.getItemId(), s.getMetadata());
    String sid = of(d);
    if (sid == null) continue;
    int i = idx(t, sid);
    if (i < 0 || !@PKG@.GearStats.active(u, s.getItemId(), d)) continue;
    c[i] = c[i] + 1;
  }
  return c;
}""")
M(gset, r"""
public static int[] note(java.util.UUID u, @IC@ armor) {
  Object[] t = @PKG@.GearCfg.STAB;
  int[] c = counts(t, u, armor);
  if (u != null) WORN.put(@PKG@.Gear.pkey(u), new Object[] { t, c });
  return c;
}""")
M(gset, r"""
public static void addTo(int[] tot, java.util.UUID u, @IC@ armor) {
  Object[] t = @PKG@.GearCfg.STAB;
  int[] c = counts(t, u, armor);
  if (c.length == 0) return;
  if (u != null) WORN.put(@PKG@.Gear.pkey(u), new Object[] { t, c });
  int ns = @PKG@.GearDefs.NS;
  int[] b = (int[]) t[3];
  int[] pc = (int[]) t[2];
  for (int i = 0; i < c.length; i++) {
    if (pc[i] <= 0 || c[i] < pc[i]) continue;
    for (int k = 0; k < ns && k < tot.length; k++) tot[k] = @PKG@.GearStats.sat((long) tot[k] + (long) b[i * (ns + 1) + k]);
  }
}""")
M(gset, r"""
public static float hp(java.util.UUID u, @IC@ armor) {
  Object[] t = @PKG@.GearCfg.STAB;
  int[] c = counts(t, u, armor);
  int ns = @PKG@.GearDefs.NS;
  int[] b = (int[]) t[3];
  int[] pc = (int[]) t[2];
  float h = 0.0f;
  for (int i = 0; i < c.length; i++) if (pc[i] > 0 && c[i] >= pc[i]) h = h + (float) b[i * (ns + 1) + ns];
  return h;
}""")
M(gset, r"""
public static String activeText(java.util.UUID u, @IC@ armor) {
  Object[] t = @PKG@.GearCfg.STAB;
  int[] c = counts(t, u, armor);
  int[] pc = (int[]) t[2];
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < c.length; i++) {
    if (pc[i] <= 0 || c[i] < pc[i]) continue;
    if (sb.length() > 0) sb.append("; ");
    sb.append(name(t, i)).append(": ").append(bonusText(t, i));
  }
  return sb.length() > 0 ? sb.toString() : "none";
}""")
M(gset, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  String k0 = u.toString();
  java.util.Iterator it = new java.util.ArrayList(WORN.keySet()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.equals(k0) || k.startsWith(k0 + "-p")) WORN.remove(k);
  }
}""")
# design review 2: THE totals (spec 4.3 T): the weapon's modifiers''')
rep('''      if (active(u, s.getItemId(), d)) addMods(t, d, true);
    }
  }
  if (withExtra) {''', '''      if (active(u, s.getItemId(), d)) addMods(t, d, true);
    }
    @PKG@.GearSet.addTo(t, u, armor);      // 0.2.14: complete armor sets
  }
  if (withExtra) {''')
rep('''    out.put(hk, Float.valueOf((prev instanceof Float ? ((Float) prev).floatValue() : 0.0f) + dh));
  }
  return out;
}""")''', '''    out.put(hk, Float.valueOf((prev instanceof Float ? ((Float) prev).floatValue() : 0.0f) + dh));
  }
  // 0.2.14: a complete armor set's hp bonus through the same Health lock (signed: the modifier ADDS -want); only while part.stats is on
  if (@PKG@.GearCfg.PART_STATS) {
    float sh = @PKG@.GearSet.hp(u, armor);
    if (sh > 0.0f) {
      Integer hk2 = Integer.valueOf(@DST@.getHealth());
      Object p2 = out.get(hk2);
      out.put(hk2, Float.valueOf((p2 instanceof Float ? ((Float) p2).floatValue() : 0.0f) - sh));
    }
  }
  return out;
}""")''')
rep('''  boolean loot = @PKG@.GearChestOpen.looting(u);
  for (int k = 0; k < SCAN.length; k++) {''', '''  boolean loot = @PKG@.GearChestOpen.looting(u);
  try { @PKG@.GearSet.note(u, inv.getArmor()); } catch (Throwable tsn) { }     // 0.2.14: the set tooltip's worn count, before any re-render
  for (int k = 0; k < SCAN.length; k++) {''')
rep('''  REGEN.remove(u); LEECH.remove(u); MANA.remove(u); WARNED.remove(u); MOVE.remove(u); LOCKED.remove(u); BLOCKED.remove(u); PRIMED.remove(u);''',
    '''  REGEN.remove(u); LEECH.remove(u); MANA.remove(u); WARNED.remove(u); MOVE.remove(u); LOCKED.remove(u); BLOCKED.remove(u); PRIMED.remove(u);
  @PKG@.GearSet.forget(u);''')

# ================================================================================================================ 7. tooltip, forge, caps
rep('''  statLines(id, d, txt, col);
  if (slot == 3) @PKG@.GearTool.lines(owner, id, d, txt, col);   // 0.2.12: tool power + Fortune by level''', '''  statLines(id, d, txt, col);
  if (slot == 3) @PKG@.GearTool.lines(owner, id, d, txt, col);   // 0.2.12: tool power + Fortune by level
  // 0.2.14: an Untiered item's one orange trade-off line (its table row), then a set piece's block
  if (r == @PKG@.GearDefs.R_UT) { String un = @PKG@.GearUt.note(id); add(txt, col, un != null ? un : "Untiered - fixed stats.", hex); }
  @PKG@.GearSet.tipLines(owner, d, r, txt, col);''')
rep('''  if (why == null) why = @PKG@.GearStamp.stackWhy(it, give, "a reforge");''', '''  if (why == null) why = @PKG@.GearStamp.stackWhy(it, give, "a reforge");
  // 0.2.14: Untiered gear has fixed stats (spec 1.6) - no reforge (Level up still works)
  if (why == null && d != null && @PKG@.GearData.rarity(d) == @PKG@.GearDefs.R_UT) why = "Untiered items have fixed stats - they cannot be reforged (Level up still works).";''')
rep('''  int capUp = org + @PKG@.GearCfg.LVLUP_CAP;''', '''  int lc = @PKG@.GearCfg.lvCap(d == null ? 0 : @PKG@.GearData.rarity(d));     // 0.2.14: per rarity
  int capUp = org + lc;''')
rep('''(cur - org) + " over Lv " + org + " (made / found) - the most is +" + @PKG@.GearCfg.LVLUP_CAP + ".");''',
    '''(cur - org) + " over Lv " + org + " (made / found) - the most is +" + lc + " for " + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(d)] + " gear.");''')
rep('''", cap +" + @PKG@.GearCfg.LVLUP_CAP + ") cost "''', '''", cap +" + @PKG@.GearCfg.lvCap(r) + ") cost "''')
rep('''"Level up: +1 level for coins, at most +" + @PKG@.GearCfg.LVLUP_CAP + " over the level it was made or found at."''',
    '''"Level up: +1 level for coins, at most " + @PKG@.GearCfg.capText() + " over its made / found level."''')
rep('''"on (at most +" + @PKG@.GearCfg.LVLUP_CAP + " levels)"''', '''"on (at most " + @PKG@.GearCfg.capText() + " levels)"''')
# the Reforge page's empty-anvil cost list: Untiered is never reforged (fixed stats)
rep('''      long per = @PKG@.GearCfg.CR_PER[r];
      b.set("#SkyyGCost" + r + ".Text", @PKG@.GearDefs.R_NAME[r] + ": " + @PKG@.Gear.fmt(@PKG@.GearCfg.CR_BASE[r]) + " coins" + (per > 0L ? " + " + @PKG@.Gear.fmt(per) + " per item level" : ""));''',
    '''      long per = @PKG@.GearCfg.CR_PER[r];
      if (r == @PKG@.GearDefs.R_UT) { b.set("#SkyyGCost" + r + ".Text", @PKG@.GearDefs.R_NAME[r] + ": fixed stats - never reforged (Level up still works)"); continue; }
      b.set("#SkyyGCost" + r + ".Text", @PKG@.GearDefs.R_NAME[r] + ": " + @PKG@.Gear.fmt(@PKG@.GearCfg.CR_BASE[r]) + " coins" + (per > 0L ? " + " + @PKG@.Gear.fmt(per) + " per item level" : ""));''')

# ================================================================================================================ 8. the market wall + bridges
rep('''# ================================================================= GearForge: the reforge core (spec 5.4 + write safety 1.7)''',
    '''# ================================================================= 0.2.14 GearWall: THE MARKET WALL (economy.md 2026-10-08 "Mythic + UT + Sets"). market:veto
# ["SkyyGear"] = this Function(ItemStack) -> null (may go on a market) or the reason (SkyyAuctions asks it when listing and buying, SkyyBazaar
# 0.1.7 before every trade). Walled: a Mythic / Untiered / Set rarity document, a document with a set field, an Untiered-table id (documented
# or not), a Mythic / Untiered / Set mystery bag. Direct player trade is never asked. Never throws (a failure answers a refusal).
gwall.addInterface(pool.get("java.util.function.Function"))
F(gwall, 'public static final String REASON = "Mythic, Untiered and Set gear never goes on the market - trade it directly with another player.";')
# fix round 2 (critic 3): gear (or a bag) whose document cannot be read (damaged, or written by a NEWER SkyyGear after a rollback) is refused -
# it may be Mythic / Untiered / Set, so the wall fails closed
F(gwall, 'public static final String UNREAD = "The gear data of this item cannot be read by this SkyyGear version - it cannot go on the market (trade it directly, or ask an admin).";')
C(gwall, "public GearWall() { }")
M(gwall, r"""
public static boolean fixed(int r) { return r == @PKG@.GearDefs.R_MY || r == @PKG@.GearDefs.R_UT || r == @PKG@.GearDefs.R_SET; }""")
M(gwall, r"""
public static String why(String id, @BD@ md) {
  if (id == null) return null;
  if (@PKG@.GearUnid.isBox(id)) {
    @BV@ v = md == null ? null : md.get(@PKG@.GearUnid.KEY);
    @BD@ bd = v != null && v.isDocument() ? v.asDocument() : null;
    if (v != null && bd == null) return UNREAD;
    return bd != null && fixed(@PKG@.GearUnid.rar(bd)) ? REASON : null;
  }
  if (@PKG@.GearUt.has(id)) {
    if (@PKG@.GearData.isGear(id)) return REASON;
    @PKG@.Gear.warnOnce("utnotgear:" + id, "config.properties: ut." + id + " is ignored - that item is not gear (only weapons and armor can be Untiered)");
  }
  if (!@PKG@.GearData.gearish(id, md)) return null;
  @BD@ d = @PKG@.GearData.effective(id, md);
  if (d == null) return UNREAD;
  if (fixed(@PKG@.GearData.rarity(d)) || @PKG@.GearSet.of(d) != null) return REASON;
  return null;
}""")
M(gwall, r"""
public Object apply(Object o) {
  try {
    if (!(o instanceof @IS@)) return null;
    @IS@ s = (@IS@) o;
    if (s.isEmpty()) return null;
    return why(s.getItemId(), s.getMetadata());
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("wall", "the market wall check failed (counted as a refusal): " + t);
    return "could not check this item";
  }
}""")

# ================================================================= GearForge: the reforge core (spec 5.4 + write safety 1.7)''')
rep('''M(gfn, r"""
public Object apply(Object o) {
  try {
    int m = this.mode;
    if (m == 10) return curve(o);''', '''# 0.2.14 gear:fn:grant (quests / bosses / chests): Object[] { String id, Number level, String rarity, String set, String pool, UUID player,
# String src } -> an identified ItemStack or null (see the 0.2.14 header item 7). Never throws, never touches ECS.
M(gfn, r"""
public static Object grant(Object o) {
  try {
    if (!(o instanceof Object[])) return null;
    Object[] a = (Object[]) o;
    if (a.length < 1 || !(a[0] instanceof String)) return null;
    String id = (String) a[0];
    int lv = a.length > 1 && a[1] instanceof Number ? ((Number) a[1]).intValue() : -1;
    String rq = a.length > 2 && a[2] instanceof String ? ((String) a[2]).trim() : "";
    String sid = a.length > 3 && a[3] instanceof String ? ((String) a[3]).trim() : "";
    String pl = a.length > 4 && a[4] instanceof String ? ((String) a[4]).trim() : "";
    java.util.UUID u = a.length > 5 && a[5] instanceof java.util.UUID ? (java.util.UUID) a[5] : null;
    String src = a.length > 6 && a[6] instanceof String && ((String) a[6]).trim().length() > 0 ? ((String) a[6]).trim() : "grant";
    if (!@PKG@.GearData.isGear(id) || @PKG@.Gear.item(id) == null) return null;
    boolean ut = @PKG@.GearUt.has(id);
    int r;
    if (rq.length() == 0) r = ut ? @PKG@.GearDefs.R_UT : (sid.length() > 0 ? @PKG@.GearDefs.R_SET : @PKG@.GearRoll.pickRarity(2));
    else {
      r = @PKG@.GearDefs.rIndex(rq);
      if (r < 0) return null;
    }
    if (ut != (r == @PKG@.GearDefs.R_UT)) {
      @PKG@.Gear.warnOnce("grantut:" + id + ":" + r, "gear:fn:grant refused " + id + " as " + @PKG@.GearDefs.R_ID[r] + " - only Untiered-table items are Untiered, and they always are");
      return null;
    }
    if (sid.length() > 0) {
      if (ut || @PKG@.GearData.slotOf(id) != 2) return null;
      if (@PKG@.GearSet.idx(sid) < 0) @PKG@.Gear.warnOnce("grantset:" + sid, "gear:fn:grant: the set " + sid + " is not in the Armor sets table yet - the piece carries it and counts once the set is added");
      if (r != @PKG@.GearDefs.R_MY) r = @PKG@.GearDefs.R_SET;
    }
    if (lv < 1) lv = @PKG@.GearLevel.level(id, null);
    int[] b = ut ? @PKG@.GearUt.band(id) : @PKG@.GearLevel.band(id);
    if (b != null) {
      if (lv < b[0]) lv = b[0];
      if (lv > b[1]) lv = b[1];
    }
    if (lv < 0) lv = 0;
    @BD@ d = @PKG@.GearRoll.newDoc(id, r, true, src, lv);
    if (sid.length() > 0) d.put("set", new org.bson.BsonString(sid));
    if (pl.length() > 0) d.put("pool", new org.bson.BsonString(pl));
    @IS@ s = @PKG@.GearData.put(new @IS@(id, 1), d, u);
    @PKG@.GearLog.line("GRANT " + src + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)] + " lv" + @PKG@.GearLevel.level(id, d) + (sid.length() > 0 ? " set " + sid : "") + (pl.length() > 0 ? " pool " + pl : "") + " [" + @PKG@.GearView.modSummary(d) + "]");
    return s;
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("grant", "gear:fn:grant failed: " + t);
    return null;
  }
}""")
# 0.2.14 gear:fn:tradeable: an ItemStack or Object[] { id, metadata } -> Boolean (false = behind the market wall), null = bad input
M(gfn, r"""
public static Object tradeable(Object o) {
  Object[] xs = x(o);
  if (xs == null) return null;
  return Boolean.valueOf(@PKG@.GearWall.why((String) xs[0], (@BD@) xs[1]) == null);
}""")
M(gfn, r"""
public Object apply(Object o) {
  try {
    int m = this.mode;
    if (m == 12) return grant(o);          // 0.2.14
    if (m == 13) return tradeable(o);      // 0.2.14
    if (m == 10) return curve(o);''')
rep('''    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid", "curve", "speed")))''',
    '''    ("describe", "rollsLine", "rarity", "level", "identified", "sig", "gate", "stats", "roll", "unid", "curve", "speed", "grant", "tradeable")))''')
rep('''  @PKG@.GearCfg.migrate025();
  @PKG@.GearCfg.load();''', '''  @PKG@.GearCfg.migrate025();
  @PKG@.GearCfg.migrate0214();
  @PKG@.GearCfg.load();''')
rep('''  br.put("gear:tiers", @PKG@.GearDefs.TIERS);''', '''  br.put("gear:tiers", @PKG@.GearDefs.TIERS);
  // 0.2.14 THE MARKET WALL: Mythic, Untiered and Set gear never goes on the Auction House / Bazaar (market:veto, the AH's own contract)
  try {
    br.putIfAbsent("market:veto", new java.util.concurrent.ConcurrentHashMap());
    Object mv = br.get("market:veto");
    if (mv instanceof java.util.Map) ((java.util.Map) mv).put("SkyyGear", new @PKG@.GearWall());
    else @PKG@.Gear.warn("market:veto is not a map - the market wall is OFF (the Auction House could list Mythic / Untiered / Set gear)");
  } catch (Throwable tmv) { @PKG@.Gear.warn("market:veto could not be published - the market wall is OFF: " + tmv); }''')
rep('''  try { @PKG@.Gear.bridge().remove("gear:fn:box"); } catch (Throwable t4) { }''', '''  try { @PKG@.Gear.bridge().remove("gear:fn:box"); } catch (Throwable t4) { }
  try { Object mv = @PKG@.Gear.bridge().get("market:veto"); if (mv instanceof java.util.Map) ((java.util.Map) mv).remove("SkyyGear"); } catch (Throwable t6) { }''')
rep('''| relevel | box | loot, node skyygear.admin)''', '''| relevel | box | loot | set, node skyygear.admin)''')
rep('''"; Life Steal at most " + @PKG@.GearCfg.STEAL_MAX + "% of max Health per second; gear:fn:curve, gear:fn:speed;''',
    '''"; Life Steal at most " + @PKG@.GearCfg.STEAL_MAX + "% of max Health per second; " + @PKG@.GearCfg.g1Text() + " (" + @PKG@.GearUt.statusText() + "); gear:fn:curve, gear:fn:speed, gear:fn:grant, gear:fn:tradeable;''')

# ================================================================================================================ 9. admin commands
rep('''  this.rarityArg = withOptionalArg("rarity", "normal, unique, rare, legendary, fabled, mythic or set", @ATY@.STRING);''',
    '''  this.rarityArg = withOptionalArg("rarity", "normal, unique, rare, legendary, fabled, mythic, set or untiered", @ATY@.STRING);''')
rep('''    if (r < 0) { msg(pr, "unknown rarity '" + rar + "' - normal, unique, rare, legendary, fabled, mythic, set"); return; }
  } else r = @PKG@.GearRoll.pickRarity(0);''', '''    if (r < 0) { msg(pr, "unknown rarity '" + rar + "' - normal, unique, rare, legendary, fabled, mythic, set, untiered"); return; }
    String uw = @PKG@.GearUt.rarityWhy(id, r);          // 0.2.14
    if (uw != null) { msg(pr, uw); return; }
  } else r = @PKG@.GearRoll.pickRarity(0);''')
rep('''      if (r < 0) { msg(pr, "usage: /gear rarity <normal|unique|rare|legendary|fabled|mythic|set>"); return; }''',
    '''      if (r < 0) { msg(pr, "usage: /gear rarity <normal|unique|rare|legendary|fabled|mythic|set|untiered>"); return; }
      String uw = @PKG@.GearUt.rarityWhy(id, r);        // 0.2.14
      if (uw != null) { msg(pr, uw); return; }''')
rep('''    } else if (action.equals("unid")) {
      nd.put("id", new org.bson.BsonBoolean(false));''', '''    } else if (action.equals("set")) {
      // 0.2.14: /gear set <set id|clear> - an armor piece joins a set (green Set label unless it is Mythic); clear leaves the rarity as it is
      String sw = @PKG@.GearSet.join(nd, id, rest);
      if (sw != null) { msg(pr, sw); return; }
    } else if (action.equals("unid")) {
      nd.put("id", new org.bson.BsonBoolean(false));''')
rep('''M(gset, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  String k0 = u.toString();
  java.util.Iterator it = new java.util.ArrayList(WORN.keySet()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.equals(k0) || k.startsWith(k0 + "-p")) WORN.remove(k);
  }
}""")''', '''M(gset, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  String k0 = u.toString();
  java.util.Iterator it = new java.util.ArrayList(WORN.keySet()).iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.equals(k0) || k.startsWith(k0 + "-p")) WORN.remove(k);
  }
}""")
M(gset, r"""
public static String list() {
  String[] ids = (String[]) @PKG@.GearCfg.STAB[0];
  if (ids.length == 0) return "none yet";
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ids.length; i++) { if (i > 0) sb.append(", "); sb.append(ids[i]); }
  return sb.toString();
}""")
# /gear set <set id|clear> on a document clone nd of armor id: the piece joins the set (green Set label unless it is Mythic); clear removes the
# field and leaves the rarity; null = done, else why not (nd untouched)
M(gset, r"""
public static String join(@BD@ nd, String id, String arg) {
  String a = arg == null ? "" : arg.trim();
  if (a.length() == 0) return "usage: /gear set <set id|clear> - sets: " + list();
  if (@PKG@.GearData.slotOf(id) != 2) return "only armor pieces can be in a set";
  if (a.equalsIgnoreCase("clear")) { nd.remove("set"); return null; }
  Object[] t = @PKG@.GearCfg.STAB;
  int si = idx(t, a);
  if (si < 0) return "no set '" + a + "' - add it in Server Setup -> Gear -> Rarity -> Armor sets first (sets: " + list() + ")";
  if (@PKG@.GearData.rarity(nd) == @PKG@.GearDefs.R_UT) return "Untiered items cannot be in a set";
  nd.put("set", new org.bson.BsonString(((String[]) t[0])[si]));
  if (@PKG@.GearData.rarity(nd) != @PKG@.GearDefs.R_MY) nd.put("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[@PKG@.GearDefs.R_SET]));
  return null;
}""")''')
rep('''  if (tk.length == 0) { msg(pr, "usage: /gear box <normal|unique|rare|legendary|fabled|mythic|set|random> [level 1-" + @PKG@.GearCfg.LOOT_TOP + "] [type: sword, bow, chestplate ...]"); return; }
  int r = tk[0].equalsIgnoreCase("random") ? @PKG@.GearUnid.rarity(1, 0) : @PKG@.GearDefs.rIndex(tk[0]);
  if (r < 0) { msg(pr, "unknown rarity '" + tk[0] + "' - normal, unique, rare, legendary, fabled, mythic, set or random"); return; }''',
    '''  if (tk.length == 0) { msg(pr, "usage: /gear box <normal|unique|rare|legendary|fabled|mythic|set|untiered|random> [level 1-" + @PKG@.GearCfg.LOOT_TOP + "] [type: sword, bow, chestplate ...]"); return; }
  int r = tk[0].equalsIgnoreCase("random") ? @PKG@.GearUnid.rarity(1, 0) : @PKG@.GearDefs.rIndex(tk[0]);
  if (r < 0) { msg(pr, "unknown rarity '" + tk[0] + "' - normal, unique, rare, legendary, fabled, mythic, set, untiered or random"); return; }''')
rep('''  @IS@ s = null;
  for (int k = 0; k < 8 && s == null; k++) {
    s = @PKG@.GearUnid.roll(L, ty, "admin", "admin", 0, null, 1, 0);''', '''  // 0.2.14: an orange bag comes from the Untiered table (none while it is empty)
  if (r == @PKG@.GearDefs.R_UT) {
    @IS@ ub = @PKG@.GearUt.bag(L, ty, "admin", "admin", 0);
    if (ub == null) { msg(pr, "no Untiered " + (ty >= 0 ? @PKG@.GearPool.T_NAME[ty].toLowerCase() : "item") + " fits around level " + L + " - " + @PKG@.GearUt.statusText() + " (Server Setup -> Gear -> Rarity -> Untiered items)"); return; }
    boolean uin = give(inv, ub);
    @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " box " + @PKG@.GearUnid.logText(ub) + (uin ? "" : " (inventory full)"));
    msg(pr, (uin ? "gave " : "NOT given (inventory full): ") + @PKG@.GearUnid.titleOf(ub) + " - Untiered, " + @PKG@.GearUnid.rangeText(@PKG@.GearUnid.lo(@PKG@.GearUnid.doc(ub)), @PKG@.GearUnid.hi(@PKG@.GearUnid.doc(ub))));
    return;
  }
  @IS@ s = null;
  for (int k = 0; k < 8 && s == null; k++) {
    s = @PKG@.GearUnid.roll(L, ty, "admin", "admin", 0, null, 1, 0);''')
rep('''    msg(pr, "Your active totals (held weapon + worn armor you meet the level for): " + totalsText(t));''',
    '''    msg(pr, "Your active totals (held weapon + worn armor you meet the level for): " + totalsText(t));
    msg(pr, "Complete armor sets: " + @PKG@.GearSet.activeText(u, inv.getArmor()));      // 0.2.14''')
rep('''C(subc["loot"], r"""
public GearLootCmd() {''', '''C(subc["set"], r"""
public GearSetCmd() {
  super("set", "Put the held armor in a set: /gear set <set id|clear>");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
C(subc["loot"], r"""
public GearLootCmd() {''')
rep('''  addSubCommand(new @PKG@.GearLootCmd());''', '''  addSubCommand(new @PKG@.GearLootCmd());
  addSubCommand(new @PKG@.GearSetCmd());''')
rep('''SIG_CLASSES + LOOT_CLASSES + TOOL_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''',
    '''SIG_CLASSES + LOOT_CLASSES + TOOL_CLASSES + G1_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')
rep('''print("classes written: %d + %d config kit classes; %d config rows; %d stats; %d quality assets" % (len(ALL), len(kit.classes), len(CFG_ROWS), NS, NR))''',
    '''print("classes written: %d + %d config kit classes; %d config rows; %d stats; %d quality assets" % (len(ALL), len(kit.classes), len(CFG_ROWS), NS, NR))
print("0.2.14: Untiered / Mythic / Set - %s + /gear set; rarities %s; ladder %s; level-up caps %s; Mythic odds %s (was %s); %d bags; gear:fn:grant, "
      "gear:fn:tradeable, market:veto; migrate0214 block %d lines" % (", ".join(str(c.getName()).rsplit(".", 1)[1] for c in G1_CLASSES), ",".join(R_IDS),
                                                                    ",".join(LADDER), LVCAP_DEF, ODDS_DEF["mythic"], ODDS_MYTHIC_OLD, len(BAG_IDS), len(GU_LINES)))''')

# ================================================================================================================ 10. Untiered drops -> orange bags
# a single undocumented Untiered-table item that drops (mob drop / fresh chest) becomes an ORANGE bag of its type (Skyy 2026-10-09 "UT drops ->
# Orange mystery bag"), its range around the drop level inside the Untiered rows of that type; null = none fits (it stays itself)
rep('''  int[] rg = @PKG@.GearPool.range(ty, at, lv, @PKG@.GearCfg.RANGE_HALF);
  if (rg == null && at > 0) { at = 0; rg = @PKG@.GearPool.range(ty, 0, lv, @PKG@.GearCfg.RANGE_HALF); }
  if (rg == null) return null;
  return make(ty, at, rarity(col, col == 1 ? lv : 0), rg[0], rg[1], col == 1 ? "drop" : "chest", src, 0);''',
    '''  if (@PKG@.GearUt.has(id)) {
    int[] ru = @PKG@.GearUt.range(ty, lv, @PKG@.GearCfg.RANGE_HALF);
    return ru == null ? null : make(ty, 0, @PKG@.GearDefs.R_UT, ru[0], ru[1], col == 1 ? "drop" : "chest", src, 0);
  }
  int[] rg = @PKG@.GearPool.range(ty, at, lv, @PKG@.GearCfg.RANGE_HALF);
  if (rg == null && at > 0) { at = 0; rg = @PKG@.GearPool.range(ty, 0, lv, @PKG@.GearCfg.RANGE_HALF); }
  if (rg == null) return null;
  return make(ty, at, rarity(col, col == 1 ? lv : 0), rg[0], rg[1], col == 1 ? "drop" : "chest", src, 0);''')
rep('''      int ty0 = @PKG@.GearPool.typeOfId(s.getItemId());
      if (ty0 < 0) return null;''', '''      int ty0 = @PKG@.GearPool.typeOfId(s.getItemId());
      if (ty0 < 0) return null;
      if (@PKG@.GearUt.has(s.getItemId())) return @PKG@.GearUt.bag(L, ty0, src, "bridge", tier);      // 0.2.14: an Untiered item = an orange bag''')

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", DST)
