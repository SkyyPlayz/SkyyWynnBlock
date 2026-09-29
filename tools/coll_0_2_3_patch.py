"""Derive SkyyCollections/build_skyycollections_0.2.3.py from 0.2.2 (0.2.2 is left untouched; line endings preserved).
Regenerate after editing this file: delete SkyyCollections/build_skyycollections_0.2.3.py, run python tools/coll_0_2_3_patch.py.
0.2.3 = the Magic Bag restructure, SkyyCollections half (research/Bag-Restructure-Spec.md sections 2, 6, 7, 8.2, 9, 10; built together
with SkyySacks 0.7.7 = the spec's "0.8.0", from the same spec). Everything 0.2.2 does stays.
  1. Bag unlock ladder in the default rewards.properties (spec 6.1): every bag type unlocks from ONE collection at tiers 1/3/5/7 =
     Normal / Unique / Rare / Legendary (item suffixes Small / Medium / Rare / Large). Mining = Iron (Skyy's lock; the three old
     Cobblestone III/V/VIII Mining Bag rows move there), Foraging = OakLog, Farming = Wheat, Combat = Bone, Smithing = HideLight (the
     four non-Mining picks are the spec defaults, [SKYY?]). Recipe ids Skyy_Sack_<Type>_<Suffix>_Recipe_Generated_0 = SkyySacks 0.7.7's
     item ids + the engine's generated recipe suffix. The commented Iron.3 / Iron.5 ore-line proposals are written merged with the bag
     token. Build asserts: four tokens per type at 1/3/5/7, one bag type per collection, the collection's first item has the bag's
     catOf prefix; the newest SkyySacks script's BAG_CATS must equal the five types.
  2. Names (6.2): CollUtil.prettyItem prints rarities ("Rare Mining Bag", "Mythic Omni Bag").
  3. coll:fn:where (6.3): apply(Object[]{UUID or null, recipeId}) -> "<CollId>|<Name>|<tier>|<threshold>|<count>" for the lowest tier
     of a visible collection that unlocks it, null otherwise / before validate() / on error. Published in setup(), removed in shutdown().
  4. sacks:freebags (6.4, written by SkyySacks): Boolean.TRUE adds " (free on this server)" to bag recipe names in reward texts.
  5. Coin-bypass (7): config bypass.bagMax (none|normal|unique|rare|legendary, default unique). CollUnlocks.compute skips a bag recipe
     whose rarity is above it on a tier reached only by buying; unlockText / the BOUGHT row / the Unlocked recipes view say so.
  6. Server Setup (8.2, kit 1.1): the choice row bypass.bagMax (Coin unlocks); a 'Magic Bags' category with one read-only row per bag
     type showing where its four rarities unlock (custom:CollKit, live from the rewards table); the rewards table help names the ladder.
  7. Migration (9): CollBagMigrate.run() in setup() BEFORE CollReg.loadAll and CfgPub.start (plain java.* text work): marker guard,
     archive to rewards-0.2.properties, untouched 0.2.2 bag lines removed, hand-edited bag lines kept (their type is admin-managed and
     gets no new rows), the 20 new tokens appended to an existing line of the same key or added under a section comment, the two
     proposed-ore comments merged, marker + atomic write, migration-bags.log + one INFO line. Deliberate choice where the spec is
     silent: an untouched 0.2.2 bag line of an ADMIN-MANAGED type is kept too (the admin's ladder for that type stays whole instead of
     losing its default rows). M6 (bought tiers whose bag moved away or now lies above bypass.bagMax, held only by the purchase) runs
     right after loadAll (CollBagMigrate.reportBought) so it can skip tiers the player has since gathered; it only logs.
     Players already past a tier get the unlock at once: coll:recipes is recomputed from the current counts on every publish (first
     sight, tier-up, purchase, reload, profile switch) - no per-player file changes.
  8. coll:epoch also bumps when the unlock LIST changes at the same size (the publish signature includes the list's hash).
Review fixes (2026-09-28):
  9. CollBypass.offer refuses ("Nothing more here can be bought with coins - gather it.") when no tier from the next one up to the coin
     wall holds a recipe a purchase can unlock (CollBypass.buyable: not a bag above bypass.bagMax; no bag at all while sacks:freebags is
     on, since every bag is known then). unlockText: "Unlocks A - B (coins and XP when gathered)." / "Tier IV has nothing to unlock -
     buying it opens tier V for buying." / "... - tier V is above the coin wall."; no free note in the Buy info.
 10. The Buy info label wraps inside its 540 x 46 box; card "Next:" lines drop the free note (the tier rows keep it).
 11. CollBagMigrate.run writes the new text's tmp first, then the archive (the bytes read, CREATE_NEW), then moves the tmp over; any
     failure deletes the tmp and this run's archive (CollIO.writeTextAtomic -> CollIO.moveReplace).
 12. One WARN at every start (CollBagMigrate.gaps) naming each bag type with rarities no visible collection tier unlocks ("(hand-edited)"
     on a type the migration left admin-managed): a gap blocks the rarities above it and the Mythic Omni Bag.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.2.py")
dst = os.path.join(ROOT, "SkyyCollections", "build_skyycollections_0.2.3.py")
assert not os.path.exists(dst), "refusing to overwrite " + dst
raw = open(src, encoding="utf8", newline="").read()
CRLF = "\r\n" in raw
s = raw.replace("\r\n", "\n")

def rep(old, new, count=1):
    global s
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)

# ---------------- docstring + version ----------------
rep('''"""SkyyCollections 0.2.2 - build script (derived from 0.2.1 by tools/coll_0_2_2_patch.py - edit the patch, not this file; 0.2.1 was
derived from 0.2 by tools/coll_0_2_1_patch.py; 0.2 was written fresh: the 0.1.5 per-profile code, the coll:recipes bridge contract
and the page command rules are carried over, everything else follows research/Collections-Spec.md).
''', '''"""SkyyCollections 0.2.3 - build script (derived from 0.2.2 by tools/coll_0_2_3_patch.py - edit the patch, not this file; 0.2.2 was
derived from 0.2.1 by tools/coll_0_2_2_patch.py; 0.2.1 from 0.2 by tools/coll_0_2_1_patch.py; 0.2 was written fresh: the 0.1.5
per-profile code, the coll:recipes bridge contract and the page command rules are carried over, everything else follows
research/Collections-Spec.md).

0.2.3: Magic Bag unlocks by rarity (research/Bag-Restructure-Spec.md 6-9), the SkyyCollections half of SkyySacks 0.7.7's restructure.
  - Default rewards.properties: each bag type unlocks from one collection at tiers 1/3/5/7 = Normal / Unique / Rare / Legendary
    (Mining = Iron Ore, Foraging = Oak Log, Farming = Wheat, Combat = Bone Fragments, Smithing = Light Hide). Cobblestone keeps its
    pickaxes and brick. Existing worlds: CollBagMigrate moves untouched 0.2.2 bag lines to the ladder once (archive
    rewards-0.2.properties, migration-bags.log); hand-edited bag lines are kept. Past tiers unlock at once (computed from counts).
  - Rarity names ("Rare Mining Bag", "Mythic Omni Bag"); " (free on this server)" when SkyySacks says bags are free (sacks:freebags).
  - Coin unlocks never unlock a bag above bypass.bagMax (default unique): Rare and Legendary bags must be gathered.
  - coll:fn:where tells SkyySacks' bag page where a recipe unlocks and how far the player is.
  - Server Setup: Coin unlocks -> "Best bag coins can unlock"; Magic Bags -> where each bag type unlocks (read only).
  - Review fixes: no Buy button where a purchase can no longer unlock anything before the coin wall; shorter, wrapping Buy info; the
    migration writes its tmp before archiving and cleans both up on failure; one start-up WARN names bag rarities no collection unlocks.
''')
rep('''Run:   python build_skyycollections_0.2.2.py          -> SkyyCollections/SkyyCollections-0.2.2.jar''',
    '''Run:   python build_skyycollections_0.2.3.py          -> SkyyCollections/SkyyCollections-0.2.3.jar''')
rep('''VERSION = "0.2.2"
''', '''VERSION = "0.2.3"
''')

# ---------------- 1. the default rewards.properties: bag ladder + build asserts ----------------
rep('''RW = [
    "# SkyyCollections 0.2 - tier rewards, ADDED to the default coins / skill XP of collections.properties",
    "# <CollectionId>.<tier number>=recipe:<RecipeId>,coins:<n>,xp:<Skill>:<n>",
    "# Recipe ids are <OutputItemId>_Recipe_Generated_<index>. Unknown ids and recipes on exclude.benches (config.properties) are",
    "# skipped and logged once. An unlocked recipe shows in /craft -> Collections and crafts there without its bench (materials",
    "# still needed). Every collection's tier I will also get its minion recipe once SkyyMinions exists.",
    "Wheat.1=" + REC("Tool_Sickle_Crude"), "Wheat.3=" + REC("Tool_Hoe_Copper"), "Wheat.4=" + REC("Tool_Sickle_Copper"),
    "Wheat.5=" + BAG("Farming", "Medium"), "Wheat.6=" + REC("Tool_Sickle_Iron"), "Wheat.7=" + REC("Tool_Hoe_Iron"), "Wheat.8=" + BAG("Farming", "Large"),
    "OakLog.1=" + REC("Tool_Hatchet_Copper"), "OakLog.3=" + BAG("Foraging", "Small"), "OakLog.5=" + BAG("Foraging", "Medium"),
    "OakLog.6=" + REC("Tool_Hatchet_Iron"), "OakLog.8=" + BAG("Foraging", "Large"),
    "Cobblestone.1=" + REC("Tool_Pickaxe_Copper"), "Cobblestone.3=" + BAG("Mining", "Small"), "Cobblestone.4=" + REC("Rock_Stone_Brick"),
    "Cobblestone.5=" + BAG("Mining", "Medium"), "Cobblestone.6=" + REC("Tool_Pickaxe_Iron"), "Cobblestone.8=" + BAG("Mining", "Large"),
    "Fiber.3=" + REC("Tool_Shears_Basic"),
    "Stick.3=" + REC("Weapon_Arrow_Crude"),
    "Bone.3=" + BAG("Combat", "Small"), "Bone.5=" + BAG("Combat", "Medium"), "Bone.8=" + BAG("Combat", "Large"),
    "Sandstone.4=" + REC("Rock_Sandstone_Brick"), "Shale.4=" + REC("Rock_Shale_Brick"), "Slate.4=" + REC("Rock_Slate_Brick"),
    "Basalt.4=" + REC("Rock_Basalt_Brick"), "Marble.4=" + REC("Rock_Marble_Brick"),
    "# Proposed ore line (research/Collections-Spec.md 4.3) - waiting for Skyy's OK. Remove the # of a line to enable it.",
]
PIECES = ["Head", "Hands", "Legs", "Chest"]
for metal, tools in (("Copper", []), ("Iron", []), ("Thorium", ["Tool_Pickaxe_Thorium", "Tool_Hatchet_Thorium"]),
                     ("Cobalt", ["Tool_Pickaxe_Cobalt", "Tool_Hatchet_Cobalt"]), ("Adamantite", ["Tool_Pickaxe_Adamantite", "Tool_Hatchet_Adamantite"]),
                     ("Mithril", ["Tool_Pickaxe_Mithril", "Tool_Hatchet_Mithril"])):
    if tools:
        RW.append("#%s.1=%s" % (metal, ",".join(REC(t) for t in tools)))
    for n, p in enumerate(PIECES):
        RW.append("#%s.%d=%s" % (metal, n + 2, REC("Armor_%s_%s" % (metal, p))))
    if metal == "Thorium":
        RW.append("#Thorium.6=" + REC("Tool_Hoe_Thorium"))
''', r'''# ---- 0.2.3: Magic Bag unlock ladder (research/Bag-Restructure-Spec.md 2.2, 2.3, 6.1). A bag grows from a collection whose items that
# same bag holds (SkyySacks catOf). Recipe ids = SkyySacks 0.7.7 item ids Skyy_Sack_<Type>_<Small|Medium|Rare|Large> + the engine's
# generated suffix _Recipe_Generated_0 (Small/Medium/Large verified in Skyy's 2026-09-25 server log; Rare is new in SkyySacks 0.7.7).
# Rarity = suffix: Small Normal, Medium Unique, Rare Rare, Large Legendary. The Mythic Omni Bag (Skyy_Sack_Omni) has no collection gate.
BAG_TYPES = ("Mining", "Foraging", "Farming", "Combat", "Smithing")     # = SkyySacks BAG_CATS (checked below)
BAG_COLL = {"Mining": "Iron", "Foraging": "OakLog", "Farming": "Wheat", "Combat": "Bone", "Smithing": "HideLight"}  # Mining = Skyy's lock
BAG_LADDER = (("Small", "Normal", 1), ("Medium", "Unique", 3), ("Rare", "Rare", 5), ("Large", "Legendary", 7))
BAG_PREFIX = {"Mining": "Ore_", "Foraging": "Wood_", "Farming": "Plant_", "Combat": "Ingredient_Bone", "Smithing": "Ingredient_Hide_"}
# the 11 bag lines of the 0.2.2 default file (CollBagMigrate removes them when untouched)
OLD_BAG_ROWS = [("Wheat.5", BAG("Farming", "Medium")), ("Wheat.8", BAG("Farming", "Large")),
                ("OakLog.3", BAG("Foraging", "Small")), ("OakLog.5", BAG("Foraging", "Medium")), ("OakLog.8", BAG("Foraging", "Large")),
                ("Cobblestone.3", BAG("Mining", "Small")), ("Cobblestone.5", BAG("Mining", "Medium")), ("Cobblestone.8", BAG("Mining", "Large")),
                ("Bone.3", BAG("Combat", "Small")), ("Bone.5", BAG("Combat", "Medium")), ("Bone.8", BAG("Combat", "Large"))]
NEW_BAG_ROWS = [("%s.%d" % (BAG_COLL[t], tier), BAG(t, sfx)) for t in BAG_TYPES for (sfx, _rar, tier) in BAG_LADDER]
# the non-bag tier rewards (unchanged from 0.2.2; Cobblestone keeps its pickaxes and brick)
BASE_RW = [("Wheat.1", REC("Tool_Sickle_Crude")), ("Wheat.3", REC("Tool_Hoe_Copper")), ("Wheat.4", REC("Tool_Sickle_Copper")),
           ("Wheat.6", REC("Tool_Sickle_Iron")), ("Wheat.7", REC("Tool_Hoe_Iron")),
           ("OakLog.1", REC("Tool_Hatchet_Copper")), ("OakLog.6", REC("Tool_Hatchet_Iron")),
           ("Cobblestone.1", REC("Tool_Pickaxe_Copper")), ("Cobblestone.4", REC("Rock_Stone_Brick")), ("Cobblestone.6", REC("Tool_Pickaxe_Iron")),
           ("Fiber.3", REC("Tool_Shears_Basic")), ("Stick.3", REC("Weapon_Arrow_Crude")),
           ("Sandstone.4", REC("Rock_Sandstone_Brick")), ("Shale.4", REC("Rock_Shale_Brick")), ("Slate.4", REC("Rock_Slate_Brick")),
           ("Basalt.4", REC("Rock_Basalt_Brick")), ("Marble.4", REC("Rock_Marble_Brick"))]
RW_ORDER = ["Wheat", "OakLog", "Cobblestone", "Iron", "Fiber", "Stick", "Bone", "HideLight", "Sandstone", "Shale", "Slate", "Basalt", "Marble"]
RW_ENTRIES = {}                      # one line per key (the kit's table rule): non-bag tokens first, then the bag token
for _k, _tok in BASE_RW + NEW_BAG_ROWS:
    RW_ENTRIES.setdefault(_k, []).append(_tok)
RW_MARK = "# bags: rarity ladder (0.2.3)"
RW_SECTION = "# Magic Bags (rarity ladder: Normal I, Unique III, Rare V, Legendary VII) - SkyyCollections 0.2.3"
RW_IRON_NOTE = ("# Iron.3 and Iron.5 below also carry the Mining bag: to enable one, REPLACE the live Iron.3 / Iron.5 line with it"
                " (one line per tier).")
RW = [
    "# SkyyCollections 0.2 - tier rewards, ADDED to the default coins / skill XP of collections.properties",
    "# <CollectionId>.<tier number>=recipe:<RecipeId>,coins:<n>,xp:<Skill>:<n>",
    "# Recipe ids are <OutputItemId>_Recipe_Generated_<index>. Unknown ids and recipes on exclude.benches (config.properties) are",
    "# skipped and logged once. An unlocked recipe shows in /craft -> Collections and crafts there without its bench (materials",
    "# still needed). Every collection's tier I will also get its minion recipe once SkyyMinions exists.",
    "# Magic Bags (SkyySacks): each bag type unlocks from ONE collection - Normal at tier 1, Unique at 3, Rare at 5, Legendary at 7.",
    "# Mining from Iron, Foraging from OakLog, Farming from Wheat, Combat from Bone, Smithing from HideLight. Keep one line per tier.",
    RW_MARK,
]
for _k in sorted(RW_ENTRIES, key=lambda k: (RW_ORDER.index(k.rsplit(".", 1)[0]), int(k.rsplit(".", 1)[1]))):
    RW.append(_k + "=" + ",".join(RW_ENTRIES[_k]))
RW.append("# Proposed ore line (research/Collections-Spec.md 4.3) - waiting for Skyy's OK. Remove the # of a line to enable it.")
PIECES = ["Head", "Hands", "Legs", "Chest"]
_BAG_AT = dict(NEW_BAG_ROWS)
ORE_MERGED = []                      # (0.2.2 comment line, 0.2.3 replacement lines) - CollBagMigrate step M4
for metal, tools in (("Copper", []), ("Iron", []), ("Thorium", ["Tool_Pickaxe_Thorium", "Tool_Hatchet_Thorium"]),
                     ("Cobalt", ["Tool_Pickaxe_Cobalt", "Tool_Hatchet_Cobalt"]), ("Adamantite", ["Tool_Pickaxe_Adamantite", "Tool_Hatchet_Adamantite"]),
                     ("Mithril", ["Tool_Pickaxe_Mithril", "Tool_Hatchet_Mithril"])):
    if tools:
        RW.append("#%s.1=%s" % (metal, ",".join(REC(t) for t in tools)))
    for n, p in enumerate(PIECES):
        _k = "%s.%d" % (metal, n + 2)
        _old = "#%s=%s" % (_k, REC("Armor_%s_%s" % (metal, p)))
        if _k in _BAG_AT:            # the commented proposal shares a key with a live bag line: written merged, bag token first
            _new = ([RW_IRON_NOTE] if not ORE_MERGED else []) + ["#%s=%s,%s" % (_k, _BAG_AT[_k], REC("Armor_%s_%s" % (metal, p)))]
            ORE_MERGED.append((_old, _new))
            RW.extend(_new)
        else:
            RW.append(_old)
    if metal == "Thorium":
        RW.append("#Thorium.6=" + REC("Tool_Hoe_Thorium"))
assert [o for o, _n in ORE_MERGED] == ["#Iron.3=" + REC("Armor_Iron_Hands"), "#Iron.5=" + REC("Armor_Iron_Chest")], ORE_MERGED
# build asserts (spec 6.1): four tokens per bag type at tiers 1/3/5/7 in rarity order, one bag type per collection, the collection's
# first item has the prefix of the bag's catOf rule, the collection is visible and has at least 7 tiers, every live key is unique
_bag_tiers = dict((t, []) for t in BAG_TYPES)
_bag_colls = {}
_keys = [l.split("=", 1)[0] for l in RW if l and not l.startswith("#")]
assert len(_keys) == len(set(k.lower() for k in _keys)), "rewards.properties default: a key has two lines"
for _l in RW:
    if not _l or _l.startswith("#"):
        continue
    _k, _v = _l.split("=", 1)
    for _tok in _v.split(","):
        if not _tok.startswith("recipe:Skyy_Sack_"):
            continue
        _m = re.match(r"^recipe:Skyy_Sack_([A-Za-z]+)_(Small|Medium|Rare|Large)_Recipe_Generated_0$", _tok)
        assert _m and _m.group(1) in BAG_TYPES, _tok
        _cid, _t = _k.rsplit(".", 1)
        _bag_tiers[_m.group(1)].append((int(_t), _m.group(2), _cid))
        _bag_colls.setdefault(_cid, set()).add(_m.group(1))
_regby = dict((r[0], r) for r in REG)
for _t in BAG_TYPES:
    assert sorted(_bag_tiers[_t]) == [(1, "Small", BAG_COLL[_t]), (3, "Medium", BAG_COLL[_t]), (5, "Rare", BAG_COLL[_t]),
                                      (7, "Large", BAG_COLL[_t])], (_t, _bag_tiers[_t])
    _r = _regby[BAG_COLL[_t]]
    assert _r[5][0].startswith(BAG_PREFIX[_t]), (_t, _r[5][0])
    assert "hidden" not in _r[6] and _r[1] != "Fishing" and len(CURVES[_r[2]]) >= 7, _t
assert all(len(v) == 1 for v in _bag_colls.values()), "a collection carries two bag types: %s" % _bag_colls
assert len(NEW_BAG_ROWS) == 20 and len(OLD_BAG_ROWS) == 11
# the newest SkyySacks build script (read as text, never imported) must have the same five bag types
def _ver(fn):
    return tuple(int(x) for x in fn[len("build_skyysacks_"):-3].split("."))
_sdir = os.path.join(HERE, "..", "SkyySacks")
_sacks = sorted([f for f in os.listdir(_sdir) if re.match(r"^build_skyysacks_\d+(\.\d+)*\.py$", f)], key=_ver) if os.path.isdir(_sdir) else []
if _sacks:
    _txt = open(os.path.join(_sdir, _sacks[-1]), encoding="utf8").read()
    _m = re.search(r"^BAG_CATS\s*=\s*\(([^)]*)\)", _txt, re.M)
    if not _m or tuple(re.findall(r'"([A-Za-z]+)"', _m.group(1))) != BAG_TYPES:
        raise SystemExit("SkyySacks %s: BAG_CATS is not %s - the bag recipe ids would not match" % (_sacks[-1], BAG_TYPES))
    print("bag ladder: 5 types x 4 rarities (tiers 1/3/5/7); SkyySacks cross-check: %s BAG_CATS match%s" % (
        _sacks[-1], "" if _ver(_sacks[-1]) >= (0, 7, 7) else " (older than 0.7.7: its server logs the Rare bag ids as unknown recipes)"))
else:
    print("bag ladder: 5 types x 4 rarities (tiers 1/3/5/7); note: no SkyySacks build script found for the cross-check")
''')
# the bypass.bagMax template line (new installs only; an existing config.properties falls back to the default 'unique')
rep('''    "bypass.walls=5,4,3,0",
''', '''    "bypass.walls=5,4,3,0",
    "# highest bag rarity a BOUGHT tier may unlock (none, normal, unique, rare, legendary)",
    "bypass.bagMax=unique",
''')

# ---------------- classes ----------------
rep('''ckit = K("CollKit")   # 0.2.2: admin config kit hooks + the shared reload
ALL = (util, cio, rd, reg, drp, mig, cdat, sto, rew, unl, cred, byp, plc, pend, gctx, btk, ptk, pltk, ktk, atk, rtk, bsy, usy, psy, plsy, ksy,
       tcmp, top, fnc, page, ckit, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)''',
    '''ckit = K("CollKit")   # 0.2.2: admin config kit hooks + the shared reload
bmig = K("CollBagMigrate")   # 0.2.3: rewards.properties bag lines -> the rarity ladder (once)
ALL = (util, cio, rd, reg, drp, mig, cdat, sto, bmig, rew, unl, cred, byp, plc, pend, gctx, btk, ptk, pltk, ktk, atk, rtk, bsy, usy, psy,
       plsy, ksy, tcmp, top, fnc, page, ckit, ulc, rlc, gvc, tpc, nmc, cmd, sav, pl)''')

# ---------------- fields ----------------
rep('''          "public static volatile int[] BYP_WALL = new int[] { 5, 4, 3, 0 };",
''', '''          "public static volatile int[] BYP_WALL = new int[] { 5, 4, 3, 0 };",
          "public static volatile int BYP_BAGMAX = 2;",
''')
rep('''F(top, "public static final java.util.HashMap CACHE = new java.util.HashMap();")
''', r'''F(top, "public static final java.util.HashMap CACHE = new java.util.HashMap();")
# 0.2.3 CollBagMigrate tables (generated from OLD_BAG_ROWS / NEW_BAG_ROWS / ORE_MERGED above)
def _jarr(xs):
    return "new String[] { " + ", ".join('"' + x.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"' for x in xs) + " }"
for f in ("public static volatile boolean RAN = false;",
          "public static volatile java.util.HashSet MANAGED = new java.util.HashSet();",
          "public static final String MARK = " + _jarr([RW_MARK])[15:-2] + ";",
          "public static final String SECTION = " + _jarr([RW_SECTION])[15:-2] + ";",
          "public static final String[] OLD_K = " + _jarr([k for k, _t in OLD_BAG_ROWS]) + ";",
          "public static final String[] OLD_T = " + _jarr([t for _k, t in OLD_BAG_ROWS]) + ";",
          "public static final String[] NEW_K = " + _jarr([k for k, _t in NEW_BAG_ROWS]) + ";",
          "public static final String[] NEW_T = " + _jarr([t for _k, t in NEW_BAG_ROWS]) + ";",
          "public static final String[] C_OLD = " + _jarr([o for o, _n in ORE_MERGED]) + ";",
          "public static final String[] C_NEW = " + _jarr(["\n".join(n) for _o, n in ORE_MERGED]) + ";"):
    F(bmig, f)
''')

# ---------------- 2. names: rarity words; bag helpers (CollUtil) ----------------
rep('''# display name of an item / recipe output id (no lang lookup): Tool_Sickle_Crude -> Crude Sickle, Skyy_Sack_Mining_Small -> Small Mining Bag
M(util, r"""
public static String prettyItem(String id) {
  if (id == null) return "?";
  String[] p = id.split("_");
  if (id.startsWith("Skyy_Sack_") && p.length >= 4) return p[3] + " " + p[2] + " Bag";''',
    '''# 0.2.3: Magic Bag rarity word of an item suffix (Bag-Restructure-Spec 3.1): Small Normal, Medium Unique, Rare Rare, Large Legendary
M(util, r"""
public static String rarityOf(String sfx) {
  if ("Small".equals(sfx)) return "Normal";
  if ("Medium".equals(sfx)) return "Unique";
  if ("Large".equals(sfx)) return "Legendary";
  return sfx;
}""")
# 0.2.3: bag rank of a recipe id (spec 7): Skyy_Sack_*_Small 1, _Medium 2, _Rare 3, _Large 4, Skyy_Sack_Omni 5, anything else 0 (never limited)
M(util, r"""
public static int bagRank(String rid) {
  if (rid == null) return 0;
  String id = rid.trim();
  int g = id.indexOf("_Recipe_Generated_");
  if (g > 0) id = id.substring(0, g);
  if (!id.startsWith("Skyy_Sack_")) return 0;
  if (id.equals("Skyy_Sack_Omni")) return 5;
  String[] p = id.split("_");
  if (p.length < 4) return 0;
  if (p[3].equals("Small")) return 1;
  if (p[3].equals("Medium")) return 2;
  if (p[3].equals("Rare")) return 3;
  if (p[3].equals("Large")) return 4;
  return 0;
}""")
M(util, r"""
public static boolean isBag(String rid) {
  return rid != null && rid.startsWith("Skyy_Sack_");
}""")
# 0.2.3 (spec 6.4): SkyySacks publishes sacks:freebags = Boolean.TRUE when every bag recipe is free (its switch, or no SkyyCollections)
M(util, r"""
public static boolean freeBags() {
  try { return Boolean.TRUE.equals(bridge().get("sacks:freebags")); } catch (Throwable t) { return false; }
}""")
# display name of an item / recipe output id (no lang lookup): Tool_Sickle_Crude -> Crude Sickle, Skyy_Sack_Mining_Small -> Normal Mining Bag
M(util, r"""
public static String prettyItem(String id) {
  if (id == null) return "?";
  String[] p = id.split("_");
  if (id.equals("Skyy_Sack_Omni")) return "Mythic Omni Bag";
  if (id.startsWith("Skyy_Sack_") && p.length >= 4) return rarityOf(p[3]) + " " + p[2] + " Bag";''')
rep('''M(util, r"""
public static String prettyRecipe(String rid) {
  if (rid == null) return "?";
  int g = rid.indexOf("_Recipe_Generated_");
  return prettyItem(g > 0 ? rid.substring(0, g) : rid);
}""")
''', '''M(util, r"""
public static String prettyRecipe(String rid) {
  if (rid == null) return "?";
  int g = rid.indexOf("_Recipe_Generated_");
  return prettyItem(g > 0 ? rid.substring(0, g) : rid);
}""")
# 0.2.3: a recipe reward as the reward texts show it ("Rare Mining Bag recipe", + " (free on this server)" for a free bag)
M(util, r"""
public static String recipeLabel(String rid) {
  String s = prettyRecipe(rid) + " recipe";
  if (isBag(rid) && freeBags()) s = s + " (free)";   // main session: short, the tier-row labels do not wrap
  return s;
}""")
''')

# ---------------- CollIO: replace a file with a written tmp (atomic move, retried) for the migration ----------------
# (review fix: the caller writes the tmp, archives the old file only after that, and deletes tmp + archive itself when this throws)
rep('''M(cio, r"""
public static synchronized void append(java.nio.file.Path f, String text) {''', '''M(cio, r"""
public static synchronized void moveReplace(java.nio.file.Path tmp, java.nio.file.Path f) throws java.io.IOException {
  java.io.IOException last = null;
  for (int i = 0; i < 5; i++) {
    try {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE });
      return;
    } catch (java.nio.file.AtomicMoveNotSupportedException e) {
      java.nio.file.Files.move(tmp, f, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING });
      return;
    } catch (java.nio.file.FileSystemException e) {
      last = e;
    }
    try { Thread.sleep(20L); } catch (InterruptedException ie) { }
  }
  throw last;
}""")
M(cio, r"""
public static synchronized void append(java.nio.file.Path f, String text) {''')

# ---------------- 5. config: bypass.bagMax ----------------
rep('''M(reg, r"""
public static String loadConfig() {''', '''# 0.2.3: bypass.bagMax words -> the highest bag rank a bought tier may unlock (-1 = not a known word)
M(reg, r"""
public static int bagMaxIndex(String w) {
  if (w == null) return -1;
  String[] n = new String[] { "none", "normal", "unique", "rare", "legendary" };
  for (int i = 0; i < n.length; i++) if (n[i].equals(w.trim().toLowerCase())) return i;
  return -1;
}""")
M(reg, r"""
public static String loadConfig() {''')
rep('''  if (felled) srcs.add("skills:felled"); else srcs.remove("skills:felled");
  ADD_SOURCES = srcs;
  return "migrate=" + MIGRATE + " auto=" + AUTO + " bypass=" + BYPASS + " felled=" + felled;''',
    '''  if (felled) srcs.add("skills:felled"); else srcs.remove("skills:felled");
  ADD_SOURCES = srcs;
  String bm = String.valueOf(p.getProperty("bypass.bagMax", "unique")).trim().toLowerCase();
  int bi = bagMaxIndex(bm);
  if (bi < 0) { @PKG@.CollUtil.warn("config.properties: bypass.bagMax=" + bm + " is not none, normal, unique, rare or legendary - using unique"); bi = 2; }
  BYP_BAGMAX = bi;
  return "migrate=" + MIGRATE + " auto=" + AUTO + " bypass=" + BYPASS + " bagMax=" + bi + " felled=" + felled;''')

# ---------------- reward texts: rarity names, free note, "(gather this tier)" on BOUGHT rows ----------------
rep('''M(reg, r"""
public static String rewardText(@PKG@.RegData R, int c, int t) {
  StringBuilder sb = new StringBuilder();
  String[] rs = recipesAt(c, t);
  for (int i = 0; i < rs.length; i++) { if (sb.length() > 0) sb.append(" - "); sb.append(@PKG@.CollUtil.prettyRecipe(rs[i])).append(" recipe"); }''',
    '''# 0.2.3: bought = a BOUGHT row of the collection page: a bag above bypass.bagMax says it must be gathered (spec 7)
M(reg, r"""
public static String rewardTextB(@PKG@.RegData R, int c, int t, boolean bought) {
  StringBuilder sb = new StringBuilder();
  String[] rs = recipesAt(c, t);
  boolean free = @PKG@.CollUtil.freeBags();
  for (int i = 0; i < rs.length; i++) {
    if (sb.length() > 0) sb.append(" - ");
    sb.append(@PKG@.CollUtil.recipeLabel(rs[i]));
    if (bought && !free && @PKG@.CollUtil.bagRank(rs[i]) > BYP_BAGMAX) sb.append(" (gather this tier)");
  }''')
rep('''    sb.append('+').append(@PKG@.CollUtil.fmt(((Long) a[1]).longValue())).append(' ').append((String) a[0]).append(" XP");
  }
  return sb.length() == 0 ? "-" : sb.toString();
}""")
''', '''    sb.append('+').append(@PKG@.CollUtil.fmt(((Long) a[1]).longValue())).append(' ').append((String) a[0]).append(" XP");
  }
  return sb.length() == 0 ? "-" : sb.toString();
}""")
M(reg, r"""
public static String rewardText(@PKG@.RegData R, int c, int t) {
  return rewardTextB(R, c, t, false);
}""")
''')
rep('''  for (int i = 0; i < rs.length; i++) out.add(@PKG@.CollUtil.prettyRecipe(rs[i]) + " recipe");''',
    '''  for (int i = 0; i < rs.length; i++) out.add(@PKG@.CollUtil.recipeLabel(rs[i]));''')
rep('''    for (int i = 0; i < ls.size(); i++) pr.sendMessage(@MSG@.raw("   " + (String) ls.get(i)).color(((String) ls.get(i)).endsWith(" recipe") ? "#c8f0a0" : "#e8d8a0"));''',
    '''    for (int i = 0; i < ls.size(); i++) pr.sendMessage(@MSG@.raw("   " + (String) ls.get(i)).color(((String) ls.get(i)).indexOf(" recipe") >= 0 ? "#c8f0a0" : "#e8d8a0"));''')

# ---------------- 7. CollBagMigrate (after CollStore: it uses CollIO, CollUtil, CollReg.tierOf and CollStore.sumMap) ----------------
rep('''# ================= CollRewards: coins + skill XP per tier, owed-and-retry (separate paid markers, never paid twice) =================
''', r'''# ================= 0.2.3 CollBagMigrate: rewards.properties bag lines -> the rarity ladder, once (Bag-Restructure-Spec 9) =================
# run() is plain java.* text work on the file (no assets), called in setup() BEFORE CollReg.loadAll and CfgPub.start, so the loaders and
# the config kit's first read already see the result. A bare JVM can run it on fixture files. Line rules = the mod's loader (trimmed
# line, '#' or '!' comment, key before the first '='), with \: and \= read as : and =.
M(bmig, r"""
public static String norm(String s) {
  return s.replace("\\:", ":").replace("\\=", "=");
}""")
M(bmig, r"""
public static String rkey(String k) {
  int dot = k.lastIndexOf('.');
  if (dot <= 0) return k.trim().toLowerCase();
  try { return k.substring(0, dot).trim().toLowerCase() + "." + Integer.parseInt(k.substring(dot + 1).trim()); } catch (Throwable t) { return k.trim().toLowerCase(); }
}""")
M(bmig, r"""
public static String[] entry(String line) {
  if (line == null) return null;
  String t = norm(line.trim());
  if (t.length() == 0 || t.startsWith("#") || t.startsWith("!")) return null;
  int eq = t.indexOf('=');
  if (eq <= 0) return null;
  return new String[] { t.substring(0, eq).trim(), t.substring(eq + 1).trim() };
}""")
# tokens of a value, "recipe: X" read as "recipe:X" (the loader trims the recipe id too)
M(bmig, r"""
public static String[] toks(String v) {
  String[] p = @PKG@.CollUtil.csv(v);
  for (int i = 0; i < p.length; i++) if (p[i].startsWith("recipe:")) p[i] = "recipe:" + p[i].substring(7).trim();
  return p;
}""")
# "Mining|Small" for a bag recipe token, "Omni|" for the Omni, null for anything else
M(bmig, r"""
public static String bagOf(String tok) {
  if (tok == null) return null;
  String t = tok.trim();
  if (!t.startsWith("recipe:")) return null;
  String id = t.substring(7).trim();
  int g = id.indexOf("_Recipe_Generated_");
  if (g > 0) id = id.substring(0, g);
  if (!id.startsWith("Skyy_Sack_")) return null;
  String[] p = id.split("_");
  if (p.length < 4) return (p.length == 3 ? p[2] : "?") + "|";
  return p[2] + "|" + p[3];
}""")
M(bmig, r"""
public static String typeOf(String tok) {
  String b = bagOf(tok);
  if (b == null) return null;
  return b.substring(0, b.indexOf('|')).toLowerCase();
}""")
M(bmig, r"""
public static int oldIndex(String k, String[] tk) {
  if (tk.length != 1) return -1;
  String rk = rkey(k);
  for (int j = 0; j < OLD_K.length; j++) if (rkey(OLD_K[j]).equals(rk) && tk[0].equals(OLD_T[j])) return j;
  return -1;
}""")
M(bmig, r"""
public static String rtrim(String s) {
  int e = s.length();
  while (e > 0 && (s.charAt(e - 1) == ' ' || s.charAt(e - 1) == '\t')) e--;
  return s.substring(0, e);
}""")
# M0 guard, M2 remove untouched 0.2.2 bag lines, M3 add the new tokens, M4 merge the two ore comments, M5 marker + write + log; M1 archive
# (review fix) happens inside the write: tmp written first, then the archive (the bytes read, CREATE_NEW - never a read-only copy), then the
# move; any failure deletes the tmp and this run's archive, so a file that cannot be written leaves nothing behind start after start.
M(bmig, r"""
public static String run(java.nio.file.Path base) {
  RAN = false;
  if (base == null) return "bags: no data folder";
  java.nio.file.Path f = base.resolve("rewards.properties");
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "bags: no rewards.properties yet (written with the rarity ladder)";
    byte[] raw = java.nio.file.Files.readAllBytes(f);
    String text = java.nio.charset.StandardCharsets.UTF_8.newDecoder().decode(java.nio.ByteBuffer.wrap(raw)).toString();
    String nl = text.indexOf("\r\n") >= 0 ? "\r\n" : "\n";
    java.util.ArrayList lines = new java.util.ArrayList(java.util.Arrays.asList(text.split("\r?\n", -1)));
    if (lines.size() > 0 && ((String) lines.get(lines.size() - 1)).length() == 0) lines.remove(lines.size() - 1);
    for (int i = 0; i < lines.size(); i++) if (((String) lines.get(i)).trim().equals(MARK)) return "bags: rewards already on the rarity ladder";
    StringBuilder log = new StringBuilder();
    java.util.HashSet managed = new java.util.HashSet();
    int n0 = lines.size();
    int[] old = new int[n0];
    int hand = 0;
    for (int i = 0; i < n0; i++) {
      old[i] = -1;
      String[] e = entry((String) lines.get(i));
      if (e == null) continue;
      String[] tk = toks(e[1]);
      int j = oldIndex(e[0], tk);
      if (j >= 0) { old[i] = j; continue; }
      boolean bag = false;
      for (int k = 0; k < tk.length; k++) {
        String ty = typeOf(tk[k]);
        if (ty == null) continue;
        bag = true;
        if (!ty.equals("omni") && !ty.equals("?")) managed.add(ty);
      }
      if (bag) { hand++; log.append("  kept hand-edited line ").append(i + 1).append(": ").append(((String) lines.get(i)).trim()).append('\n'); }
    }
    MANAGED = managed;
    boolean[] drop = new boolean[n0];
    int removed = 0;
    for (int i = 0; i < n0; i++) {
      if (old[i] < 0) continue;
      String ty = typeOf(OLD_T[old[i]]);
      if (managed.contains(ty)) { log.append("  kept untouched line ").append(i + 1).append(" (its bag type has hand-edited lines): ").append(((String) lines.get(i)).trim()).append('\n'); continue; }
      drop[i] = true;
      removed++;
      log.append("  removed line ").append(i + 1).append(": ").append(((String) lines.get(i)).trim()).append('\n');
    }
    for (int i = n0 - 1; i >= 0; i--) if (drop[i]) lines.remove(i);
    java.util.HashSet present = new java.util.HashSet();
    for (int i = 0; i < lines.size(); i++) {
      String[] e = entry((String) lines.get(i));
      if (e == null) continue;
      String[] tk = toks(e[1]);
      for (int k = 0; k < tk.length; k++) present.add(tk[k]);
    }
    int appended = 0; int added = 0;
    boolean section = false;
    java.util.HashSet told = new java.util.HashSet();
    for (int j = 0; j < NEW_K.length; j++) {
      String ty = typeOf(NEW_T[j]);
      if (managed.contains(ty)) { if (told.add(ty)) log.append("  ").append(ty).append(" bag lines are hand-edited - no new ").append(ty).append(" bag lines added\n"); continue; }
      if (present.contains(NEW_T[j])) { log.append("  already there: ").append(NEW_T[j]).append('\n'); continue; }
      int at = -1;
      String want = rkey(NEW_K[j]);
      for (int i = 0; i < lines.size() && at < 0; i++) {
        String[] e = entry((String) lines.get(i));
        if (e != null && rkey(e[0]).equals(want)) at = i;
      }
      if (at >= 0) {
        String ln = rtrim((String) lines.get(at));
        String[] e = entry(ln);
        ln = ln + (e[1].length() == 0 ? "" : ",") + NEW_T[j];
        lines.set(at, ln);
        appended++;
        log.append("  appended to line ").append(at + 1).append(": ").append(ln.trim()).append('\n');
      } else {
        if (!section) { lines.add(""); lines.add(SECTION); section = true; }
        lines.add(NEW_K[j] + "=" + NEW_T[j]);
        added++;
        log.append("  added: ").append(NEW_K[j]).append('=').append(NEW_T[j]).append('\n');
      }
      present.add(NEW_T[j]);
    }
    for (int m = 0; m < C_OLD.length; m++) {
      for (int i = 0; i < lines.size(); i++) {
        if (!((String) lines.get(i)).trim().equals(C_OLD[m])) continue;
        lines.remove(i);
        String[] rp = C_NEW[m].split("\n");
        for (int k = 0; k < rp.length; k++) lines.add(i + k, rp[k]);
        log.append("  proposed ore line merged with its bag token: ").append(rp[rp.length - 1]).append('\n');
        break;
      }
    }
    int top = 0;
    while (top < lines.size() && ((String) lines.get(top)).trim().startsWith("#")) top++;
    lines.add(top, MARK);
    StringBuilder out = new StringBuilder();
    for (int i = 0; i < lines.size(); i++) out.append((String) lines.get(i)).append(nl);
    java.nio.file.Path tmp = f.resolveSibling("rewards.properties.tmp");
    java.nio.file.Path arch = base.resolve("rewards-0.2.properties");
    if (java.nio.file.Files.exists(arch, new java.nio.file.LinkOption[0])) arch = base.resolve("rewards-0.2." + new java.text.SimpleDateFormat("yyyyMMdd-HHmmss").format(new java.util.Date()) + ".properties");
    boolean archived = false;
    try {
      java.nio.file.Files.write(tmp, out.toString().getBytes("UTF-8"), new java.nio.file.OpenOption[0]);
      java.nio.file.Files.write(arch, raw, new java.nio.file.OpenOption[] { java.nio.file.StandardOpenOption.CREATE_NEW, java.nio.file.StandardOpenOption.WRITE });
      archived = true;
      @PKG@.CollIO.moveReplace(tmp, f);
    } catch (Throwable we) {
      try { java.nio.file.Files.deleteIfExists(tmp); } catch (Throwable t2) { }
      if (archived) { try { java.nio.file.Files.deleteIfExists(arch); } catch (Throwable t3) { } }
      @PKG@.CollUtil.warn("could not move the bag rewards to the rarity ladder - rewards.properties is left as it was and this is retried at the next start: " + we);
      return "bags: migration failed";
    }
    RAN = true;
    String sum = removed + " removed, " + (appended + added) + " added (" + appended + " on existing lines), " + hand + " hand-edited line(s) kept";
    @PKG@.CollIO.append(base.resolve("migration-bags.log"), "# " + new java.util.Date() + " - SkyyCollections 0.2.3: bag rewards moved to the rarity ladder (" + sum + "); the old file is " + arch.getFileName() + "\n" + log);
    @PKG@.CollUtil.info("bag rewards moved to the rarity ladder: " + removed + " removed, " + (appended + added) + " added, " + hand + " hand-edited lines kept (see migration-bags.log)");
    return "bags: " + sum;
  } catch (Throwable t) {
    @PKG@.CollUtil.warn("could not move the bag rewards to the rarity ladder - rewards.properties is left as it was and this is retried at the next start: " + t);
    return "bags: migration failed";
  }
}""")
# why a bought old bag tier no longer gives its bag (null = the purchase still unlocks it); new places from the default ladder
M(bmig, r"""
public static String lostWhy(String id, long b, String oldTok) {
  String ty = typeOf(oldTok);
  String bg = bagOf(oldTok);
  if (MANAGED.contains(ty)) return "check it by hand (its bag lines are hand-edited)";
  for (int j = 0; j < NEW_K.length; j++) {
    if (!bg.equals(bagOf(NEW_T[j]))) continue;
    int dot = NEW_K[j].lastIndexOf('.');
    String nid = NEW_K[j].substring(0, dot);
    int nt = Integer.parseInt(NEW_K[j].substring(dot + 1));
    if (!nid.equalsIgnoreCase(id)) return "that tier has no bag now (the bag unlocks at " + nid + " " + @PKG@.CollUtil.roman(nt) + ")";
    if ((long) nt > b) return "the bag now unlocks at " + id + " " + @PKG@.CollUtil.roman(nt);
    if (@PKG@.CollUtil.bagRank(NEW_T[j].substring(7)) > @PKG@.CollReg.BYP_BAGMAX) return "the bag is above the coin limit now (bypass.bagMax) - it must be gathered";
    return null;
  }
  return "that tier has no bag now";
}""")
# M6 (after loadAll, only on the start that migrated): purchases of old bag tiers that lost their bag and are held only by the purchase
# (a tier gathered since is skipped). Logged for a manual refund; no counts file is written.
M(bmig, r"""
public static String reportBought(java.nio.file.Path base) {
  if (!RAN || base == null) return "";
  try {
    java.io.File[] fs = base.resolve("counts").toFile().listFiles();
    if (fs == null) return "";
    @PKG@.RegData R = @PKG@.CollReg.D;
    StringBuilder log = new StringBuilder();
    int n = 0;
    for (int i = 0; i < fs.length; i++) {
      String fn = fs[i].getName();
      if (!fn.endsWith(".properties")) continue;
      String key = fn.substring(0, fn.length() - 11);
      java.util.Properties p = null;
      try { p = @PKG@.CollIO.read(fs[i].toPath()); } catch (Throwable t) { continue; }
      for (int j = 0; j < OLD_K.length; j++) {
        int dot = OLD_K[j].lastIndexOf('.');
        String id = OLD_K[j].substring(0, dot);
        int t = Integer.parseInt(OLD_K[j].substring(dot + 1));
        long b = 0L;
        try { b = Long.parseLong(String.valueOf(p.getProperty("_bought." + id, "0")).trim()); } catch (Throwable e) { }
        if (b < (long) t) continue;
        if (R != null) {
          Object ci = R.byId.get(id.toLowerCase());
          if (ci instanceof Integer) {
            int c = ((Integer) ci).intValue();
            if (@PKG@.CollReg.tierOf(R, c, @PKG@.CollStore.sumMap(p, (String[]) R.items[c])) >= t) continue;
          }
        }
        String why = lostWhy(id, b, OLD_T[j]);
        if (why == null) continue;
        String bagId = OLD_T[j].substring(7, OLD_T[j].indexOf("_Recipe_Generated_"));
        String nm = p.getProperty("_name");
        String[] bp = bagId.split("_");
        log.append("  ").append(key).append(nm != null ? " (" + nm + ")" : "").append(" bought ").append(id).append(' ').append(@PKG@.CollUtil.roman(t)).append(" (").append(bp[3]).append(' ').append(bp[2]).append(" Bag, now the ").append(@PKG@.CollUtil.prettyItem(bagId)).append(") - ").append(why).append('\n');
        n++;
      }
    }
    if (n == 0) return "bags: no bought tier lost its bag";
    @PKG@.CollIO.append(base.resolve("migration-bags.log"), "# bought collection tiers whose bag moved away or must now be gathered (not refunded - refund by hand if you like):\n" + log);
    @PKG@.CollUtil.info(n + " bought collection tier(s) lost their bag - listed in migration-bags.log (no refunds were made)");
    return "bags: " + n + " bought tier(s) lost their bag (migration-bags.log)";
  } catch (Throwable t) {
    @PKG@.CollUtil.warn("could not list the bought tiers that lost their bag: " + t);
    return "";
  }
}""")
# review fix: bag rarities that no visible collection tier unlocks in the loaded rewards table, per type in ladder order
# ("Mining (hand-edited): Rare, Legendary; Combat: Normal"), "" when all 20 are there. Every bag recipe takes the rarity below it and the
# Mythic Omni Bag takes one Legendary bag of each type, so one gap blocks the rarities above it and the Omni. setup() logs one WARN with
# it at every start (an admin-managed type from the migration gets no new rows, so this is where a missing Rare shows outside the log).
M(bmig, r"""
public static String gaps() {
  @PKG@.RegData R = @PKG@.CollReg.D;
  java.util.HashMap rw = @PKG@.CollReg.REWARDS;
  if (R == null || rw == null) return "";
  java.util.HashSet have = new java.util.HashSet();
  for (int c = 0; c < R.n; c++) {
    if (R.hidden[c]) continue;
    int mx = @PKG@.CollReg.maxTier(R, c);
    for (int t = 1; t <= mx; t++) {
      String[] tk = (String[]) rw.get(R.id[c].toLowerCase() + "." + t);
      if (tk == null) continue;
      for (int i = 0; i < tk.length; i++) { String b = bagOf(tk[i]); if (b != null) have.add(b); }
    }
  }
  StringBuilder sb = new StringBuilder();
  String cur = null;
  for (int j = 0; j < NEW_T.length; j++) {
    String b = bagOf(NEW_T[j]);
    if (have.contains(b)) continue;
    int bar = b.indexOf('|');
    String ty = b.substring(0, bar);
    String rar = @PKG@.CollUtil.rarityOf(b.substring(bar + 1));
    if (ty.equals(cur)) { sb.append(", ").append(rar); continue; }
    if (sb.length() > 0) sb.append("; ");
    sb.append(ty).append(MANAGED.contains(ty.toLowerCase()) ? " (hand-edited)" : "").append(": ").append(rar);
    cur = ty;
  }
  return sb.toString();
}""")

# ================= CollRewards: coins + skill XP per tier, owed-and-retry (separate paid markers, never paid twice) =================
''')

# ---------------- 5. unlock list: bags above bypass.bagMax only by gathering; epoch signature includes the list ----------------
rep('''    for (int c = 0; c < R.n; c++) {
      if (R.hidden[c]) continue;
      int eff = @PKG@.CollStore.effTier(d, R, c);
      for (int t = 1; t <= eff; t++) {
        String[] rs = @PKG@.CollReg.recipesAt(c, t);
        for (int i = 0; i < rs.length; i++) out.add(rs[i]);
      }
    }''', '''    int bagMax = @PKG@.CollReg.BYP_BAGMAX;
    for (int c = 0; c < R.n; c++) {
      if (R.hidden[c]) continue;
      int ct = @PKG@.CollStore.countTier(d, R, c);
      int eff = @PKG@.CollStore.effTier(d, R, c);
      for (int t = 1; t <= eff; t++) {
        String[] rs = @PKG@.CollReg.recipesAt(c, t);
        for (int i = 0; i < rs.length; i++) {
          if (t > ct && @PKG@.CollUtil.bagRank(rs[i]) > bagMax) continue;
          out.add(rs[i]);
        }
      }
    }''')
rep('''      String sig = key + "|" + s[0] + "|" + s[3] + "|" + ids.size();''',
    '''      String sig = key + "|" + s[0] + "|" + s[3] + "|" + ids.size() + "|" + sb.toString().hashCode();''')

# ---------------- 5. coin-bypass text: a bag above bypass.bagMax must be gathered ----------------
rep('''M(byp, r"""
public static String unlockText(int c, int t) {
  String[] rs = @PKG@.CollReg.recipesAt(c, t);
  if (rs.length == 0) return "Tier " + @PKG@.CollUtil.roman(t) + " has no recipe - buying it only opens the next tier for buying.";
  StringBuilder sb = new StringBuilder("Unlocks ");
  for (int i = 0; i < rs.length; i++) { if (i > 0) sb.append(" - "); sb.append(@PKG@.CollUtil.prettyRecipe(rs[i])); }
  sb.append(". Its coins and XP come when you gather to it.");
  return sb.toString();
}""")''', '''M(byp, r"""
public static String unlockText(int c, int t) {
  @PKG@.RegData R = @PKG@.CollReg.D;
  String[] rs = @PKG@.CollReg.recipesAt(c, t);
  boolean free = @PKG@.CollUtil.freeBags();
  StringBuilder ok = new StringBuilder();
  StringBuilder no = new StringBuilder();
  for (int i = 0; i < rs.length; i++) {
    String nm = @PKG@.CollUtil.prettyRecipe(rs[i]);
    if (buyable(rs[i], free)) { if (ok.length() > 0) ok.append(" - "); ok.append(nm); }
    else if (!free) { if (no.length() > 0) no.append(" - "); no.append(nm); }
  }
  String gather = no.length() == 0 ? "" : no + " must be gathered";
  if (ok.length() > 0) return "Unlocks " + ok + " (coins and XP when gathered)" + (gather.length() > 0 ? ". " + gather : "") + ".";
  String r = "Tier " + @PKG@.CollUtil.roman(t) + (gather.length() > 0 ? ": " + gather : " has nothing to unlock");
  int mx = R == null ? t : @PKG@.CollReg.maxTier(R, c);
  int wall = R == null ? 0 : @PKG@.CollReg.BYP_WALL[R.curve[c]];
  if (t >= mx) return r + ".";
  if (t + 1 > wall) return r + " - tier " + @PKG@.CollUtil.roman(t + 1) + " is above the coin wall.";
  return r + " - buying it opens tier " + @PKG@.CollUtil.roman(t + 1) + " for buying.";
}""")''')
# review fix: the Buy button only where a purchase can still unlock something before the coin wall (see chainBuyable)
rep('''# Object[]{Integer next tier, Long price, String refusal or null}
M(byp, r"""''', '''# 0.2.3 review fix: can a purchase unlock this recipe? Not a bag above bypass.bagMax (it must be gathered), and no bag at all while
# SkyySacks says every bag is free (sacks:freebags: the bag is known anyway, so buying its tier adds nothing).
M(byp, r"""
public static boolean buyable(String rid, boolean free) {
  if (!@PKG@.CollUtil.isBag(rid)) return true;
  return !free && @PKG@.CollUtil.bagRank(rid) <= @PKG@.CollReg.BYP_BAGMAX;
}""")
# true when a tier in [from .. to] holds a recipe a purchase can unlock. offer() refuses otherwise: a bought tier only opens the next one
# for buying, so a chain that reaches the coin wall without one would take coins for nothing (OakLog IV/V, Iron / Bone / Light Hide IV).
M(byp, r"""
public static boolean chainBuyable(int c, int from, int to) {
  boolean free = @PKG@.CollUtil.freeBags();
  for (int t = from; t <= to; t++) {
    String[] rs = @PKG@.CollReg.recipesAt(c, t);
    for (int i = 0; i < rs.length; i++) if (buyable(rs[i], free)) return true;
  }
  return false;
}""")
# Object[]{Integer next tier, Long price, String refusal or null}
M(byp, r"""''')
rep('''    else if (next > wall) err = "Tier " + @PKG@.CollUtil.roman(next) + " must be gathered - coins unlock up to tier " + @PKG@.CollUtil.roman(wall) + " here.";
''', '''    else if (next > wall) err = "Tier " + @PKG@.CollUtil.roman(next) + " must be gathered - coins unlock up to tier " + @PKG@.CollUtil.roman(wall) + " here.";
    else if (!chainBuyable(c, next, wall < mx ? wall : mx)) err = "Nothing more here can be bought with coins - gather it.";
''')

# ---------------- 3. coll:fn:where ----------------
rep('''fnc.addInterface(pool.get("java.util.function.Function"))
F(fnc, "public String mode;")
C(fnc, "public CollFn(String mode) { this.mode = mode; }")
M(fnc, r"""
public Object apply(Object arg) {
  try {
    Object[] a = (Object[]) arg;''', '''fnc.addInterface(pool.get("java.util.function.Function"))
F(fnc, "public String mode;")
C(fnc, "public CollFn(String mode) { this.mode = mode; }")
# 0.2.3 coll:fn:where (Bag-Restructure-Spec 6.3): {UUID player or null, String recipeId} -> "<CollId>|<Name>|<tier>|<threshold>|<count>"
# for the LOWEST tier of a visible collection whose validated rewards list the recipe (ties: registry order); count = the player's
# real count on the active profile (0 without a player). null when no collection lists it, before validate() ran, or on any error.
M(fnc, r"""
public static Object where(Object[] a) {
  try {
    if (a == null || a.length < 2 || a[1] == null) return null;
    java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
    String rid = String.valueOf(a[1]).trim();
    @PKG@.RegData R = @PKG@.CollReg.D;
    if (R == null || !@PKG@.CollReg.VALIDATED || rid.length() == 0) return null;
    int bc = -1; int bt = 0;
    for (int c = 0; c < R.n; c++) {
      if (R.hidden[c]) continue;
      int mx = @PKG@.CollReg.maxTier(R, c);
      int lim = bt > 0 && bt - 1 < mx ? bt - 1 : mx;
      boolean hit = false;
      for (int t = 1; t <= lim && !hit; t++) {
        String[] rs = @PKG@.CollReg.recipesAt(c, t);
        for (int i = 0; i < rs.length && !hit; i++) if (rid.equals(rs[i])) { bc = c; bt = t; hit = true; }
      }
    }
    if (bc < 0) return null;
    long n = 0L;
    if (u != null) {
      @PKG@.CollData d = @PKG@.CollStore.data(u);
      if (d != null) n = @PKG@.CollStore.sum(d, R, bc);
    }
    return R.id[bc] + "|" + R.name[bc] + "|" + bt + "|" + @PKG@.CollReg.threshold(R, bc, bt) + "|" + n;
  } catch (Throwable t) { return null; }
}""")
M(fnc, r"""
public Object apply(Object arg) {
  try {
    if ("where".equals(this.mode)) return where((Object[]) arg);
    Object[] a = (Object[]) arg;''')

# ---------------- page (review fix): the Buy info wraps inside its 540 x 46 box (two 14 px lines fit) and its texts are short; card
# "Next:" lines drop the free note (it stays on the tier rows) so the 32-char clip keeps the bag name whole ----------------
rep('''    b.appendInline("#SkyyCBuyRow", lab("SkyyCBuyInfo", "Width: 540, Height: 46", "", 14, false, "#c8b070", false));''',
    '''    b.appendInline("#SkyyCBuyRow", "Label #SkyyCBuyInfo { Anchor: (Width: 540, Height: 46); Text: \\"\\"; Style: (FontSize: 14, TextColor: #c8b070, VerticalAlignment: Center, Wrap: true); }");''')
rep('''  java.util.ArrayList nx = ct >= mx ? null : @PKG@.CollReg.rewardLines(R, c, ct + 1);
  b.set("#SkyyCCdNext" + n + ".Text", nx == null ? "All tiers done" : (nx.isEmpty() ? "Next: tier " + @PKG@.CollUtil.roman(ct + 1) : "Next: " + @PKG@.CollUtil.clip((String) nx.get(0), 32)));''',
    '''  java.util.ArrayList nx = ct >= mx ? null : @PKG@.CollReg.rewardLines(R, c, ct + 1);
  String[] nr = ct >= mx ? new String[0] : @PKG@.CollReg.recipesAt(c, ct + 1);
  String n1 = nr.length > 0 ? @PKG@.CollUtil.prettyRecipe(nr[0]) + " recipe" : (nx == null || nx.isEmpty() ? "" : (String) nx.get(0));
  b.set("#SkyyCCdNext" + n + ".Text", nx == null ? "All tiers done" : (nx.isEmpty() ? "Next: tier " + @PKG@.CollUtil.roman(ct + 1) : "Next: " + @PKG@.CollUtil.clip(n1, 32)));''')
# ---------------- page: BOUGHT rows name gated bags; the Unlocked recipes view follows compute() ----------------
rep('''    b.set("#SkyyCRew" + t + ".Text", @PKG@.CollReg.rewardText(R, c, t) + (t > ct && t <= bt ? "   (coins and XP paid when reached)" : ""));''',
    '''    b.set("#SkyyCRew" + t + ".Text", @PKG@.CollReg.rewardTextB(R, c, t, t > ct && t <= bt) + (t > ct && t <= bt ? "  (paid when reached)" : ""));''')
rep('''      for (int i = 0; i < rs.length; i++) {
        if (!seen.add(rs[i])) continue;
        lines.add(@PKG@.CollUtil.prettyRecipe(rs[i]) + "    (" + R.name[c] + " " + @PKG@.CollUtil.roman(t) + (t > ct ? " - bought" : "") + ")");''',
    '''      for (int i = 0; i < rs.length; i++) {
        if (t > ct && @PKG@.CollUtil.bagRank(rs[i]) > @PKG@.CollReg.BYP_BAGMAX) continue;
        if (!seen.add(rs[i])) continue;
        lines.add(@PKG@.CollUtil.prettyRecipe(rs[i]) + "    (" + R.name[c] + " " + @PKG@.CollUtil.roman(t) + (t > ct ? " - bought" : "") + ")");''')

# ---------------- 6. Server Setup rows (kit 1.1) ----------------
rep('''KIT_CATS = [("curves", "Curves"), ("rewards", "Rewards"), ("bypass", "Coin unlocks"), ("rules", "Rules"), ("registry", "Registry")]''',
    '''KIT_CATS = [("curves", "Curves"), ("rewards", "Rewards"), ("bags", "Magic Bags"), ("bypass", "Coin unlocks"), ("rules", "Rules"),
            ("registry", "Registry")]   # 0.2.3: + Magic Bags''')
rep('''    ("bypass.walls", "Highest tier coins can buy", "bypass", "text", "5,4,3,0", "1", "200", "", "", "live,danger",
     "Per curve Bulk,Standard,Rare,Elite (0 = never). Higher tiers must be gathered.",
     "reload@config.properties:bypass.walls;check=CollKit.checkWalls"),
''', '''    ("bypass.walls", "Highest tier coins can buy", "bypass", "text", "5,4,3,0", "1", "200", "", "", "live,danger",
     "Per curve Bulk,Standard,Rare,Elite (0 = never). Higher tiers must be gathered.",
     "reload@config.properties:bypass.walls;check=CollKit.checkWalls"),
    # 0.2.3 (Bag-Restructure-Spec 7, 8.2)
    ("bypass.bagMax", "Best bag coins can unlock", "bypass", "choice", "unique", "", "", "none|None,normal|Normal,unique|Unique,rare|Rare,legendary|Legendary",
     "", "live", "Bag recipes above this rarity unlock only by gathering, never with a bought tier.",
     "reload@config.properties:bypass.bagMax"),
''')
rep('''    ("rewards", "Tier rewards (rewards.properties)", "registry", "table", "", "", "", "text;type;Rewards", "", "live,adv",
     "Entry Wheat.3 = recipe:<RecipeId>,coins:<n>,xp:<Skill>:<n> - added to that tier's coins and XP.",
     "reload@rewards.properties:;check=CollKit.checkReward"),
]''', '''    ("rewards", "Tier rewards (rewards.properties)", "registry", "table", "", "", "", "text;type;Rewards", "", "live,adv",
     "Wheat.3 = recipe:<id>,coins:<n>,xp:<Skill>:<n>. Bags: Iron, OakLog, Wheat, Bone, HideLight 1/3/5/7.",
     "reload@rewards.properties:;check=CollKit.checkReward"),
]
# 0.2.3: one read-only row per bag type = where its Normal / Unique / Rare / Legendary recipes unlock (live from the rewards table)
for _t in BAG_TYPES:
    KIT_ROWS.append(("bags." + _t, _t + " bag unlocks", "bags", "text", "", "", "", "", "", "ro",
                     "Collection tiers of the Normal / Unique / Rare / Legendary %s Bag - edit them in Tier rewards." % _t,
                     "custom:CollKit@config.properties"))''')
rep('''  return ask;
}""")

# ================= commands (HANDOFF command rules: Adventurer group on player commands, admin = requirePermission + no groups) =================
''', r'''  return ask;
}""")
# 0.2.3: the read-only Magic Bags rows (custom:, no file key). "Iron Ore I / III / V / VII" when one collection holds all four rarities,
# else "<collection> <tier>" per rarity ("none" = no collection unlocks it). Read from the loaded rewards table (the file as the mod reads it).
M(ckit, r"""
public static String bagLadder(String type) {
  @PKG@.RegData R = @PKG@.CollReg.D;
  java.util.HashMap rw = @PKG@.CollReg.REWARDS;
  if (R == null || rw == null) return "(collections are not loaded)";
  String[] sfx = new String[] { "Small", "Medium", "Rare", "Large" };
  String[] cn = new String[4];
  int[] tier = new int[4];
  for (int k = 0; k < 4; k++) {
    String want = "Skyy_Sack_" + type + "_" + sfx[k];
    for (int c = 0; c < R.n; c++) {
      if (R.hidden[c]) continue;
      int mx = @PKG@.CollReg.maxTier(R, c);
      boolean hit = false;
      for (int t = 1; t <= mx && !hit; t++) {
        if (tier[k] > 0 && t >= tier[k]) break;
        String[] tk = (String[]) rw.get(R.id[c].toLowerCase() + "." + t);
        if (tk == null) continue;
        for (int i = 0; i < tk.length && !hit; i++) {
          if (!tk[i].startsWith("recipe:")) continue;
          String rid = tk[i].substring(7).trim();
          int g = rid.indexOf("_Recipe_Generated_");
          if (g > 0 && rid.substring(0, g).equals(want)) { cn[k] = R.name[c]; tier[k] = t; hit = true; }
        }
      }
    }
  }
  boolean one = tier[0] > 0;
  for (int k = 1; k < 4 && one; k++) if (tier[k] <= 0 || !cn[k].equals(cn[0])) one = false;
  if (one) return cn[0] + " " + @PKG@.CollUtil.roman(tier[0]) + " / " + @PKG@.CollUtil.roman(tier[1]) + " / " + @PKG@.CollUtil.roman(tier[2]) + " / " + @PKG@.CollUtil.roman(tier[3]);
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < 4; k++) {
    if (k > 0) sb.append(", ");
    sb.append(tier[k] > 0 ? cn[k] + " " + @PKG@.CollUtil.roman(tier[k]) : "none");
  }
  return sb.toString();
}""")
M(ckit, r"""
public static String customGet(String key) {
  try {
    if (key != null && key.startsWith("bags.")) return bagLadder(key.substring(5));
  } catch (Throwable t) { @PKG@.CollUtil.warn("Magic Bags row failed: " + t); }
  return null;
}""")
M(ckit, r"""
public static Object[] customSet(String key, String value) {
  return new Object[] { "bad", null, "Read only - change the bag lines in Registry > Tier rewards (entries like Iron.3)." };
}""")

# ================= commands (HANDOFF command rules: Adventurer group on player commands, admin = requirePermission + no groups) =================
''')

# ---------------- setup(): migration before loadAll (and before CfgPub.start), M6 after; coll:fn:where ----------------
rep('''  @PKG@.PlacedStore.DIR = base.resolve("placed");
  String s = @PKG@.CollReg.loadAll();''', '''  @PKG@.PlacedStore.DIR = base.resolve("placed");
  String bm = @PKG@.CollBagMigrate.run(base);
  String s = @PKG@.CollReg.loadAll();
  String bb = @PKG@.CollBagMigrate.reportBought(base);
  String gp = @PKG@.CollBagMigrate.gaps();
  if (gp.length() > 0) @PKG@.CollUtil.warn("no collection tier unlocks these Magic Bags: " + gp + " - they, the rarities above them and the Mythic Omni Bag cannot be crafted unless bags are free (SkyySacks bags.freeRecipes). Add them in Server Setup > Collections > Registry > Tier rewards or rewards.properties, one line per tier (e.g. Iron.5=recipe:Skyy_Sack_Mining_Rare_Recipe_Generated_0).");''')
rep('''  b.put("coll:fn:add", new @PKG@.CollFn("add"));
  b.put("coll:list", @PKG@.CollReg.listString());''', '''  b.put("coll:fn:add", new @PKG@.CollFn("add"));
  b.put("coll:fn:where", new @PKG@.CollFn("where"));
  b.put("coll:list", @PKG@.CollReg.listString());''')
rep('''  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCollections] 0.2.2 ready - item collections, /collections, admin settings in SkyWynn Menu -> Server Setup (/modconfig); migration + recipe check run at start; " + s);''',
    '''  getLogger().at(java.util.logging.Level.INFO).log("[SkyyCollections] 0.2.3 ready - item collections, Magic Bag unlocks by rarity, /collections, admin settings in SkyWynn Menu -> Server Setup (/modconfig); migration + recipe check run at start; " + s + "; " + bm + (bb.length() > 0 ? "; " + bb : ""));''')
rep('''    b.remove("coll:fn:count"); b.remove("coll:fn:tier"); b.remove("coll:fn:add"); b.remove("coll:list");''',
    '''    b.remove("coll:fn:count"); b.remove("coll:fn:tier"); b.remove("coll:fn:add"); b.remove("coll:fn:where"); b.remove("coll:list");''')
rep('''B.assemble(jar, B.manifest("SkyyCollections", VERSION, "SkyWynn collections, Hypixel SkyBlock style: the ITEMS you gather (fiber, sticks, every log type, cobble, ores, crops, mob drops) count toward ~100 collections in Farming, Mining, Foraging and Combat. Tiers pay coins (SkyyCoins), gathering skill XP (SkyySkills) and recipe unlocks for the SkyySacks craft page; coin unlocks for early tiers; leaderboards. /collections. Per profile with SkyyProfiles (optional). Zero dependencies.", PKG + ".SkyyCollectionsPlugin"),''',
    '''B.assemble(jar, B.manifest("SkyyCollections", VERSION, "SkyWynn collections, Hypixel SkyBlock style: the ITEMS you gather (fiber, sticks, every log type, cobble, ores, crops, mob drops) count toward ~100 collections in Farming, Mining, Foraging and Combat. Tiers pay coins (SkyyCoins), gathering skill XP (SkyySkills) and recipe unlocks for the SkyySacks craft page, including the Magic Bag rarities (Mining bags from Iron Ore); coin unlocks for early tiers; leaderboards. /collections. Per profile with SkyyProfiles (optional). Zero dependencies.", PKG + ".SkyyCollectionsPlugin"),''')
rep('''kit.write(OUT)   # 0.2.2: deferred checks (CollKit hooks exist with the right signatures), then the 7 kit classes''',
    '''kit.write(OUT)   # 0.2.2: deferred checks (CollKit hooks exist with the right signatures), then the 7 kit classes (0.2.3: + customGet/customSet)''')

assert "0.2.2 ready" not in s and s.count('VERSION = "0.2.3"') == 1
out = s.replace("\n", "\r\n") if CRLF else s
open(dst, "w", encoding="utf8", newline="").write(out)
print("wrote", dst, "(CRLF)" if CRLF else "(LF)")
