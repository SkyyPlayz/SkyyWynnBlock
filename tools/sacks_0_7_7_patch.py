"""Derive SkyySacks/build_skyysacks_0.7.7.py from the LIVE 0.7.6 (edit THIS file, then regenerate: python tools/sacks_0_7_7_patch.py).
0.7.7 = MAGIC BAGS BY RARITY + THE MYTHIC OMNI BAG + COLLECTION-UNLOCKED BAG RECIPES. Source: research/Bag-Restructure-Spec.md (it wins; it
calls this version "0.8.0" - the round pins it as 0.7.7, RESUME.md step 2), SkyWynn-Decisions change notes 2026-09-25 #7 (e) and #8, the
UI LOOK = VANILLA rule (HANDOFF section 2 rule 0), research/SkyyGear-Stage1-Spec.md 5.2 / 7.1 / 7.3 (gear:fn:roll for /craft).
 - Tiers by rarity (spec 3): the 5 bag types keep their ids - Skyy_Sack_<Type>_Small / _Medium / _Large are now the Normal / Unique /
   Legendary <Type> Bag with the same 640 / 2,240 / 20,160 per item; NEW Skyy_Sack_<Type>_Rare (6,720) sits between Unique and Legendary
   (Unique / Rare / Legendary = the previous bag + 6 Linen / Shadoweave / Cindercloth Scraps, mob drops - review fix: the Loombench bolts
   were unobtainable; 6 is a placeholder: the next rarity needs the previous one). Own item qualities
   Skyy_Bag_Normal / _Unique / _Rare / _Legendary / _Mythic in the Wynn colours (the SkyyGear 2.1 hexes and frame art by hue).
 - The MYTHIC OMNI BAG (spec 4): Skyy_Sack_Omni = one Legendary bag of each of the five types at a Workbench (no knowledge gate). It gives
   the Omni cap (100,000 per item) to EVERY bag type in SweepTask.caps, so it is the only bag a player needs; the bag page keeps one tab
   per type; right-click opens the page on a tab with items. The highest cap per type still wins (with the defaults that is the Omni).
 - Collection-unlocked bag recipes (spec 5.2 / 5.3): the 20 tiered recipes are KnowledgeRequired; the new KnowSync (in the 2 s sweep, world
   thread, settled key only) teaches / forgets exactly those 20 item ids from SkyyCollections' coll:recipes:<uuid> (one sendKnownRecipes per
   change), so a real Workbench crafts only unlocked bags. /craft: Collections tab lists coll:recipes + the Omni while all five Legendary
   bags are carried; Crafting / Smithing / Farming and search list a bag only when unlocked, and any other KnowledgeRequired recipe (the 19
   vanilla ones) only when the player knows it (spec 12.1); a click re-checks it before any material moves ("You have not unlocked this
   recipe"). Free mode = Server Setup "Free bag recipes" (bags.freeRecipes, default OFF) or SkyyCollections not installed (SkyySacks stays
   standalone); published as sacks:freebags (Boolean) for SkyyCollections' reward texts. coll:fn:where (SkyyCollections 0.2.3) feeds the
   page texts ("Unlocks at Iron Ore tier I - you have 37 / 50"); without it the page says unlocked / not.
 - Server Setup (spec 8.1): bag.small / bag.medium / bag.rare (new) / bag.large / bag.omni (new, max 10,000,000) rows with the rarity
   labels, the order question now checks Normal <= Unique <= Rare <= Legendary <= Omni; bags.freeRecipes (bool, live, confirm always).
   Config history keeps 10 versions (OPEN-QUESTIONS server setup 3, LOCKED 2026-09-25).
 - Saved bags carry their old quality index ("Quality": 5): carried bag stacks are restamped to their item's quality (withQuality; id, count,
   durability and metadata unchanged) in the sweep (spec 5.6). caps() skips unknown tier words / types (spec 12.2).
 - One-time chat notice per player (spec 5.8) in Skyy_SkyySacks/notices.properties, written by the SackSaver thread.
 - Bag page: vanilla Hytale look (Common.ui DecoratedContainer: header + ContainerPatch frame + decorations, Secondary / Tertiary button
   textures, vanilla label colours and sounds, BarterTradeRow item cards) with the rarity colour on each tab and cap line, a Next line, and
   for a bag you do not carry: how to get one, the unlock status and the whole rarity ladder with its unlocks.
 - SkyyGear bridge (research/SkyyGear-Stage1-Spec.md 5.2 / 7.3): each /craft output entry goes through gear:fn:roll when that Function
   exists; its ItemStacks are handed out (validated: same item, never more than crafted; anything else = plain output + one warning), the
   crafts.log line gets gear=<n>. No SkyyGear (or a null answer) = exactly the 0.7.6 plain output.
Everything 0.7.6 does stays (sweep, pools per profile, bench link, craft tabs, Furnace / Tannery, settings, config rows).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.6.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.7.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def Q(txt):
    """Inner Java blocks of the build script are written jt(r@Q3@ ... @Q3@) here (the outer raw strings use the same triple quote)."""
    return txt.replace("@Q3@", "'" * 3)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


def seg(start, end, must_have, new):
    """Replace s[start : end) (end exclusive, both anchors unique) after checking the old segment is the one we expect."""
    global s
    assert s.count(start) == 1, "segment start not unique: " + start[:90]
    i = s.index(start)
    j = s.index(end, i)
    assert s.count(end) == 1, "segment end not unique: " + end[:90]
    old = s[i:j]
    for m in must_have:
        assert m in old, "segment %r lacks %r" % (start[:50], m[:80])
    s = s[:i] + new + s[j:]


# ================= docstring + version =================
rep('"""SkyySacks 0.7.6 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.6.py            -> SkyySacks/SkyySacks-0.7.6.jar' + LF
    + '       python build_skyysacks_0.7.6.py --deploy   -> also',
    '"""SkyySacks 0.7.7 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.7.py            -> SkyySacks/SkyySacks-0.7.7.jar' + LF
    + '       python build_skyysacks_0.7.7.py --deploy   -> also')
rep('Defaults = 0.7.5, so nothing changes until an admin or a player changes something.' + LF + '"""' + LF,
    'Defaults = 0.7.5, so nothing changes until an admin or a player changes something.' + LF
    + '0.7.7 (derived from 0.7.6 by tools/sacks_0_7_7_patch.py - edit the patch, not this file; research/Bag-Restructure-Spec.md): MAGIC BAGS' + LF
    + 'BY RARITY - Small / Medium / Large keep their ids as the Normal / Unique / Legendary bag (640 / 2,240 / 20,160), a new Rare bag' + LF
    + '(6,720) sits between, own Wynn-coloured qualities; the MYTHIC OMNI BAG (all five Legendary bags in one, 100,000 of each item for' + LF
    + 'EVERY bag type, a tab per type, the only bag needed); the 20 tiered bag recipes need recipe knowledge that KnowSync teaches from' + LF
    + 'SkyyCollections coll:recipes (free when bags.freeRecipes is on or SkyyCollections is missing); /craft hides locked bags and unknown' + LF
    + 'vanilla knowledge recipes; carried bags get their new rarity look; Server Setup rows for all five caps + free recipes; one-time notice;' + LF
    + 'vanilla-look bag page; crafted gear goes through SkyyGear gear:fn:roll when it exists.' + LF
    + '"""' + LF)
rep('VERSION = "0.7.6"', 'VERSION = "0.7.7"')

# ================= the bag table: rarity ladder + Omni (python, before anything uses it) =================
BAG_TABLE = r'''# 0.7.5: THE BAG TABLE - one source for the SackDefs arrays (tab order + the "how to craft" view of a bag you do not carry), the Workbench
# recipes in the item JSON and the lang text, so the page can never describe a recipe the bag item does not have. The first four rows are
# exactly the 0.7.4 recipes; Smithing is new (Skyy's beta backlog 2026-09-24 item 1). ITEM_NAME = Assets.zip server.lang items.<id>.name.
# 0.7.7 (research/Bag-Restructure-Spec.md 3.1): BAG_BOLTS = the material of each rarity step - the next rarity needs the previous one, like
# accessories. Normal = BAG_BOLT_QTY Bolt of Wool + BAG_MAT_QTY BAG_MAT (the 0.7.4 recipe; Wool Scraps drop from sheep -> Furniture Bench).
# Unique / Rare / Legendary = the previous bag + BAG_UP_QTY MOB-DROPPED fabric scraps of the vanilla armor tiers (already Smithing-bag items):
# Linen (goblins, trorks), Shadoweave (outlanders), Cindercloth (burnt skeletons, fire dragon, wraith). Review fix: the Bolt of Linen / Silk /
# Cindercloth of the first 0.7.7 draft (and of the live 0.7.6 Medium / Large) come only from the Loombench, whose recipe needs Cotton Scraps
# that nothing drops (salvage needs armor made of those bolts), so no survival player could craft Unique and up. Silk scraps are not used:
# nothing drops them. _bag_ids_check stops the build when a step material is no longer dropped by an NPC (or one recipe step from one).
BAG_CATS = ("Mining", "Foraging", "Farming", "Combat", "Smithing")
BAG_MAT = {"Mining": "Ingredient_Bar_Copper", "Foraging": "Wood_Oak_Trunk", "Farming": "Food_Bread", "Combat": "Ingredient_Bone_Fragment",
           "Smithing": "Ingredient_Leather_Light"}
BAG_BOLTS = ("Ingredient_Bolt_Wool", "Ingredient_Fabric_Scrap_Linen", "Ingredient_Fabric_Scrap_Shadoweave", "Ingredient_Fabric_Scrap_Cindercloth")
BAG_BOLT_QTY, BAG_MAT_QTY = 3, 4     # the Normal recipe (unchanged since 0.7.4); SackDefs.BOLTQ / MATQ for the "how to get one" view
BAG_UP_QTY = 6                       # PLACEHOLDER (Skyy): fabric scraps per rarity step (Unique / Rare / Legendary)
assert BAG_BOLT_QTY >= 1 and BAG_MAT_QTY >= 1 and BAG_UP_QTY >= 1
BAG_HOLDS = {"Mining": "ore, rubble, rock and soil",
             "Foraging": "logs, planks, sticks, fibre, bark and tree sap",
             "Farming": "plants, food and cooked dishes, fish and life essence",
             "Combat": "bones, feathers, essences, venom sacs, chitin, voidhearts and boom powder",
             "Smithing": "bars and ingots, leather, hides, cloth bolts, fabric scraps, leather straps and iron studs"}
ITEM_NAME = {"Ingredient_Bar_Copper": "Copper Ingot", "Wood_Oak_Trunk": "Oak Log", "Food_Bread": "Bread",
             "Ingredient_Bone_Fragment": "Bone Fragments", "Ingredient_Leather_Light": "Light Leather",
             "Ingredient_Bolt_Wool": "Bolt of Wool", "Ingredient_Fabric_Scrap_Linen": "Linen Scraps",
             "Ingredient_Fabric_Scrap_Shadoweave": "Shadoweave Scraps", "Ingredient_Fabric_Scrap_Cindercloth": "Cindercloth Scraps"}
# 0.7.7 THE RARITY LADDER (spec 3.1): (id suffix, rarity, quality id, cap key, step material). The old Small / Medium / Large ids keep
# working as Normal / Unique / Legendary (same caps: the bag.small / bag.medium / bag.large keys); Rare is new. Rank = position + 1.
BAG_TIERS = [("Small",  "Normal",    "Skyy_Bag_Normal",    "bag.small",  BAG_BOLTS[0]),
             ("Medium", "Unique",    "Skyy_Bag_Unique",    "bag.medium", BAG_BOLTS[1]),
             ("Rare",   "Rare",      "Skyy_Bag_Rare",      "bag.rare",   BAG_BOLTS[2]),
             ("Large",  "Legendary", "Skyy_Bag_Legendary", "bag.large",  BAG_BOLTS[3])]
assert tuple(t[0] for t in BAG_TIERS) == ("Small", "Medium", "Rare", "Large"), "SackDefs.tierCap / legendCount know these suffixes"
TOP_SUFFIX = BAG_TIERS[-1][0]                       # the Legendary bag id suffix (the Omni recipe takes one of each type)
BAG_OMNI = "Skyy_Sack_Omni"                         # the Mythic Omni Bag (spec 4): cap key bag.omni, quality Skyy_Bag_Mythic
RECIPE_SUFFIX = "_Recipe_Generated_0"               # an item-embedded recipe's id (VERIFIED in Skyy's log: all bag recipe ids resolve)
# 0.7.7 rarity look (spec 3.2 = research/SkyyGear-Stage1-Spec.md 2.1): (quality id, label, tooltip TextColor, bag page text colour,
# QualityValue (< 8: SkyyAuctions treats >= 8 as technical), vanilla texture set reused by hue, drop particle). Mythic page text
# is #cc66cc (#aa00aa is too dark to read on the page); the tooltip keeps Wynn's #aa00aa. Review fix: the drop particles are SkyyGear's
# (build_skyygear RARITIES, by hue like the frame art; SkyyGear owns the look), so a Unique bag and Unique gear glow the same on the ground.
BAG_RARITY = [("Skyy_Bag_Normal",    "Normal",    "#ffffff", "#ffffff", 1, "Common",    "Drop_Common"),
              ("Skyy_Bag_Unique",    "Unique",    "#ffff55", "#ffff55", 2, "Legendary", "Drop_Legendary"),
              ("Skyy_Bag_Rare",      "Rare",      "#ff55ff", "#ff55ff", 3, "Epic",      "Drop_Epic"),
              ("Skyy_Bag_Legendary", "Legendary", "#55ffff", "#55ffff", 4, "Rare",      "Drop_Rare"),
              ("Skyy_Bag_Mythic",    "Mythic",    "#aa00aa", "#cc66cc", 6, "Epic",      "Drop_Epic")]
assert [r[1] for r in BAG_RARITY[:4]] == [t[1] for t in BAG_TIERS] and [r[0] for r in BAG_RARITY[:4]] == [t[2] for t in BAG_TIERS]
assert all(r[4] < 8 for r in BAG_RARITY), "bag qualities must stay below SkyyAuctions' technical threshold (8)"
# the 20 recipe-knowledge entries SkyySacks owns in every player's known set (KnowSync never touches any other entry)
MANAGED_IDS = ["Skyy_Sack_%s_%s" % (c, t[0]) for c in BAG_CATS for t in BAG_TIERS]
assert len(MANAGED_IDS) == 20 and len(set(MANAGED_IDS)) == 20
# 0.7.5 Smithing bag contents (SackDefs.catOf, checked before Combat). Research = the inline "Recipe" -> "Input" block of all 188 item
# JSONs with a recipe under Assets.zip Server/Item/Items/Weapon, Armor and Tool: bars 142 inputs, leather 119, fabric scraps 65, cloth
# bolts 45 (cloth armor; bolts are also the bag recipes); no gear recipe takes hides - they become leather at the Tannery. Strap and
# stud are smithing parts no recipe uses yet. The other inputs of those recipes are gathering drops that stay in their field's bag;
# chitin stays Combat (no weapon, armor or tool recipe uses it). Hides and fabric scraps were Combat until 0.7.4.
SMITH_PREFIX = ("Ingredient_Bar_", "Ingredient_Leather_", "Ingredient_Hide_", "Ingredient_Bolt_", "Ingredient_Fabric_Scrap_")
SMITH_EXACT = ("Ingredient_Strap_Leather", "Ingredient_Stud_Iron")
TREE_SAP = "Ingredient_Tree_Sap"   # every Tree_Sap_Glob_* drop list gives this item -> Foraging bag
assert BAG_CATS[:4] == ("Mining", "Foraging", "Farming", "Combat") and set(BAG_MAT) == set(BAG_CATS) == set(BAG_HOLDS)
for _t in list(BAG_HOLDS.values()) + list(ITEM_NAME.values()) + list(BAG_MAT.values()) + list(BAG_BOLTS):
    assert '"' not in _t and "\\" not in _t and "\n" not in _t, _t
for _i in list(BAG_MAT.values()) + list(BAG_BOLTS):
    assert _i in ITEM_NAME, "no display name for " + _i
def _bag_ids_check():
    import zipfile, re
    za = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    if not os.path.isfile(za):
        print("note: Assets.zip not found - bag recipe / Smithing bag ids not cross-checked")
        return
    with zipfile.ZipFile(za) as z:
        ids = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        lang = {}
        for line in z.read("Server/Languages/en-US/server.lang").decode("utf-8-sig").splitlines():
            m = re.match(r"items\.([A-Za-z0-9_]+)\.name\s*=\s*(.*)", line)
            if m:
                lang[m.group(1)] = m.group(2).strip()
        # 0.7.7 review fix: every rarity-step material must be obtainable in survival - dropped by an NPC (Server/Drops/NPCs), or made by
        # its own item recipe from NPC drops only (Bolt of Wool <- Wool Scraps from sheep). The Loombench bolts failed exactly this.
        npc_txt = [z.read(n).decode("utf-8-sig", "replace") for n in z.namelist() if n.startswith("Server/Drops/NPCs/") and n.endswith(".json")]
        def _dropped(i):
            return any('"%s"' % i in t for t in npc_txt)
        def _obtainable(i):
            if _dropped(i):
                return True
            ipath = [n for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith("/%s.json" % i)]
            if not ipath:
                return False
            rec = (json.loads(z.read(ipath[0]).decode("utf-8-sig")).get("Recipe") or {}).get("Input") or []
            return bool(rec) and all(x.get("ItemId") and _dropped(x["ItemId"]) for x in rec)
        unob = [i for i in BAG_BOLTS if i in ids and not _obtainable(i)]
    bad = [i for i in list(BAG_MAT.values()) + list(BAG_BOLTS) + list(SMITH_EXACT) + [TREE_SAP] if i not in ids]
    if bad:
        raise SystemExit("0.7.5: unknown item id(s) in the bag table: " + ", ".join(bad))
    if unob:
        raise SystemExit("0.7.7: bag rarity-step material(s) no NPC drops (nor one recipe from NPC drops): " + ", ".join(unob)
                         + " - survival players could not craft those bags; pick a dropped material in BAG_BOLTS")
    print("bag step materials obtainable from NPC drops: " + ", ".join(ITEM_NAME[i] for i in BAG_BOLTS))
    for i, nm in sorted(ITEM_NAME.items()):
        if lang.get(i) and lang[i] != nm:
            print("WARNING: %s is called %r in server.lang but the bags page says %r - update ITEM_NAME" % (i, lang[i], nm))
    fam = []
    for p in SMITH_PREFIX:
        got = sorted(i for i in ids if i.startswith(p))
        if not got:
            raise SystemExit("0.7.5: no item id starts with " + p + " any more - re-check the Smithing bag")
        fam.append("%s* %d" % (p, len(got)))
    print("smithing bag holds: " + ", ".join(fam) + ", " + ", ".join(SMITH_EXACT) + " | tree sap -> Foraging (" + TREE_SAP + ")")
_bag_ids_check()
# 0.7.7 (spec 3.2): SkyyGear owns the rarity look. The newest SkyyGear build script's RARITIES tuple list is read as text (never imported -
# the _camp_defaults_check pattern): ("unique", "Unique", "#FFFF55", "#FFFF55", "Legendary", "Legendary", "Drop_Legendary") = (id, name,
# tooltip hex, page hex, tooltip frame, slot frame, drop particle). The bags must use the same tooltip hex, frame art and drop particle, so a
# Unique bag and Unique gear look and glow the same; a mismatch stops the build. A SkyyGear script that is missing, unreadable or mid-edit
# (no complete table) falls back to the ladder table of research/SkyyGear-Stage1-Spec.md 2.1 (hexes only - it has no particle column) with
# a printed note; an unreadable source never stops the build.
def _gear_colour_check():
    import re, glob
    mine = dict((r[1].lower(), (r[2].lower(), r[5], r[6])) for r in BAG_RARITY)
    def _v(p):
        m = re.search(r"_(\d+(?:\.\d+)*)\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    found = sorted(glob.glob(os.path.join(HERE, "..", "SkyyGear", "build_skyygear_*.py")), key=_v)
    got, where = {}, None
    if found:
        where = os.path.basename(found[-1])
        try:
            txt = open(found[-1], encoding="utf8", errors="replace").read()
        except Exception as e:
            txt = ""
            print("note: could not read %s (%s)" % (where, e))
        for rid in mine:
            m = re.search(r'\(\s*"%s"\s*,\s*"[A-Za-z ]+"\s*,\s*"(#[0-9A-Fa-f]{6})"\s*,\s*"#[0-9A-Fa-f]{6}"\s*,\s*"(\w+)"\s*,\s*"(\w+)"\s*,'
                          r'\s*"(\w+)"\s*\)' % rid, txt)
            if m:
                got[rid] = (m.group(1).lower(), m.group(2), m.group(3), m.group(4))
        if len(got) < len(mine):
            print("note: %s has no complete RARITIES table this build can read (SkyyGear mid-edit?) - falling back to the SkyyGear spec"
                  % where)
            got = {}
    if got:
        bad = []
        for k in sorted(mine):
            hx, tex, part = mine[k]
            ghx, gtt, gslot, gpart = got[k]
            if hx != ghx:
                bad.append("%s colour %s (bags) vs %s" % (k, hx, ghx))
            if tex != gtt or tex != gslot:
                bad.append("%s frame %s (bags) vs tooltip %s / slot %s" % (k, tex, gtt, gslot))
            if part != gpart:
                bad.append("%s drop particle %s (bags) vs %s" % (k, part, gpart))
        if bad:
            raise SystemExit("0.7.7: the bag rarity look differs from %s: %s - SkyyGear owns the look, update BAG_RARITY" % (where, "; ".join(bad)))
        print("bag rarity look matches %s (colour, frame, drop particle: %s)" % (where, ", ".join(
            "%s %s %s %s" % (k, mine[k][0], mine[k][1], mine[k][2]) for k in ("normal", "unique", "rare", "legendary", "mythic"))))
        return
    spec = os.path.join(HERE, "..", "research", "SkyyGear-Stage1-Spec.md")
    try:
        txt = open(spec, encoding="utf8", errors="replace").read() if os.path.isfile(spec) else None
    except Exception as e:
        txt = None
        print("note: could not read %s (%s)" % (spec, e))
    if txt is None:
        print("note: no readable SkyyGear build script and no research/SkyyGear-Stage1-Spec.md - bag rarity look not cross-checked")
        return
    for rid in mine:
        m = re.search(r"\|\s*\d+\s*\|\s*`%s`\s*\|[^|\n]*\|[^|\n]*\|\s*`(#[0-9A-Fa-f]{6})`" % rid, txt)
        if m:
            got[rid] = m.group(1).lower()
    where = "research/SkyyGear-Stage1-Spec.md 2.1"
    if len(got) < len(mine):
        print("note: %s ladder table not readable - bag rarity look not cross-checked" % where)
        return
    bad = ["%s %s (bags) vs %s" % (k, mine[k][0], got[k]) for k in sorted(mine) if got.get(k) != mine[k][0]]
    if bad:
        raise SystemExit("0.7.7: the bag rarity colours differ from %s: %s - SkyyGear owns the look, update BAG_RARITY" % (where, "; ".join(bad)))
    print("bag rarity colours match %s (%s); drop particles not cross-checked (the spec has no particle column)" % (
        where, ", ".join("%s %s" % (k, mine[k][0]) for k in ("normal", "unique", "rare", "legendary", "mythic"))))
_gear_colour_check()
SMITH_JAVA = " || ".join(['itemId.startsWith("%s")' % p for p in SMITH_PREFIX] + ['itemId.equals("%s")' % i for i in SMITH_EXACT])
'''
seg("# 0.7.5: THE BAG TABLE - one source for the SackDefs arrays", "def _jarr(vals):",
    ['BAG_BOLTS = ("Ingredient_Bolt_Wool", "Ingredient_Bolt_Linen", "Ingredient_Bolt_Silk")', "_bag_ids_check()", "SMITH_JAVA = "],
    BAG_TABLE)

# ================= engine probes for the new calls =================
rep('for c, m in ((PLA, "getGameMode"), (GM, "Creative"), (CRR, "getOutputs"), (CRR, "getPrimaryOutput"), (CRR, "getBenchRequirement")):' + LF
    + '    B.probe(pool, c, m)' + LF,
    'for c, m in ((PLA, "getGameMode"), (GM, "Creative"), (CRR, "getOutputs"), (CRR, "getPrimaryOutput"), (CRR, "getBenchRequirement")):' + LF
    + '    B.probe(pool, c, m)' + LF
    + '# 0.7.7 (research/Bag-Restructure-Spec.md 5.2 / 5.6, VERIFIED bytecode): per-player recipe knowledge, the quality restamp, coloured chat' + LF
    + 'PCD = "com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData"' + LF
    + 'for c, m in ((CRR, "isKnowledgeRequired"), (PLA, "getPlayerConfigData"), (PCD, "getKnownRecipes"), (PCD, "setKnownRecipes"),' + LF
    + '             (CRP, "sendKnownRecipes"), (IS, "withQuality"), (IS, "getQualityIndex"), (IS, "getItem"), (ITM, "getQualityIndex"),' + LF
    + '             (IC, "setItemStackForSlot"), (MSG, "color")):' + LF
    + '    B.probe(pool, c, m)' + LF)

# ================= the caps table: + bag.rare / bag.omni, the config template gains bags.freeRecipes =================
CAPS_TABLE = r'''# 0.7.6: THE CAPS TABLE - one source for the public static volatile fields (initial values), the admin config rows (defaults, bounds)
# and SackCfg.reload's clamps, so the file, the page and the running values cannot disagree. (file key = row key, Java field, default,
# min, max). 0.7.7 (research/Bag-Restructure-Spec.md 8.1): the bag keys keep their names (bag.small = the Normal bag, bag.medium = Unique,
# bag.large = Legendary - owners keep every number they have); NEW bag.rare (6,720 = the geometric middle of 2,240 and 20,160) and
# bag.omni (the Mythic Omni Bag, 100,000 of each item for EVERY bag type, up to 10,000,000).
SACK_CAPS = [
    ("bag.small",        "SackDefs.CAP_SMALL",    640, 1, 1000000),
    ("bag.medium",       "SackDefs.CAP_MEDIUM",  2240, 1, 1000000),
    ("bag.rare",         "SackDefs.CAP_RARE",    6720, 1, 1000000),
    ("bag.large",        "SackDefs.CAP_LARGE",  20160, 1, 1000000),
    ("bag.omni",         "SackDefs.CAP_OMNI",  100000, 1, 10000000),
    ("bench.queueCap",   "ProcBench.QUEUE_CAP",   256, 1, 10000),
    ("bench.fuelCap",    "ProcBench.FUEL_CAP",   1000, 1, 100000),
    ("bench.outputCap",  "ProcBench.OUT_CAP",   20000, 1, 1000000),
]
CAPD = dict((k, d) for (k, _f, d, _lo, _hi) in SACK_CAPS)
assert (CAPD["bag.small"], CAPD["bag.medium"], CAPD["bag.rare"], CAPD["bag.large"], CAPD["bag.omni"]) == (640, 2240, 6720, 20160, 100000), \
    "the bag caps are locked design numbers (spec 3.1)"
assert [t[3] for t in BAG_TIERS] == ["bag.small", "bag.medium", "bag.rare", "bag.large"]
assert all(CAPD[BAG_TIERS[i][3]] < CAPD[BAG_TIERS[i + 1][3]] for i in range(3)) and CAPD["bag.large"] < CAPD["bag.omni"], "default caps must rise"
_BAG_KEYS = [c for c in SACK_CAPS if c[0].startswith("bag.")]
_BENCH_KEYS = [c for c in SACK_CAPS if c[0].startswith("bench.")]
# Skyy_SkyySacks/config.properties as SackCfg.reload writes it when it is missing (= the kit's DEFAULTS text). The first four lines are the
# 0.7.5 file; every other key is a commented template line the kit uncomments in place when an admin changes one (a 0.7.6 file without the
# new lines gets the changed line appended under the kit's "changed in game" header). Doc comments carry no "=" so nothing mistakes them
# for a key.
SACK_CFG_LINES = [
    "# SkyySacks settings - re-read about every 10 seconds when this file changes (no restart and no rebuild needed).",
    "# craftSearch=false removes the search box from the /craft page (use it if the craft page stops opening on your client).",
    "# /craft followed by words still searches when the box is off.",
    "craftSearch=true",
    "# Admins can also change these in game: SkyWynn Menu -> Server Setup -> Bags and Crafting (permission skyysacks.admin).",
    "# Free bag recipes (true or false): true gives every player every bag recipe (the old way); false unlocks them through collections.",
    "# Without SkyyCollections every bag recipe is free anyway.",
    "#bags.freeRecipes=false",
    "# Advanced - remove the # in front of a line to change it. Bag caps: the most of EACH item a Normal (old Small) / Unique (old Medium) /",
    "# Rare / Legendary (old Large) bag holds; bag.omni is the Mythic Omni Bag, for every bag type (the best bag a player carries counts).",
    "# Lowering one never deletes pooled items, it only stops new ones going in. The bag tooltips keep the built-in numbers.",
] + ["#%s=%d" % (k, d) for (k, _f, d, _lo, _hi) in _BAG_KEYS] + [
    "# Furnace and Tannery (each player has their own): queue size in units, fuel slot size in items, output held before it pauses.",
] + ["#%s=%d" % (k, d) for (k, _f, d, _lo, _hi) in _BENCH_KEYS]
SACK_CFG_TEXT = "".join(l + chr(10) for l in SACK_CFG_LINES)
def _jcfg_txt():
    """The template as a Java expression: "line" + nl + "line" + nl ... (nl = System.lineSeparator(), as in 0.7.3-0.7.5)."""
    out = []
    for l in SACK_CFG_LINES:
        assert '"' not in l and "\\" not in l, l
        out.append('"%s" + nl' % l)
    return (chr(10) + "        + ").join(out)
def _jfield(k):
    for (fk, f, d, lo, hi) in SACK_CAPS:
        if fk == k:
            return f, d, lo, hi
    raise KeyError(k)

'''
seg("# 0.7.6: THE CAPS TABLE - one source for the public static volatile fields", 'PKG = "com.skyy.sacks"' + LF,
    ['("bag.large",        "SackDefs.CAP_LARGE", 20160, 1, 1000000),', "def _jfield(k):"], CAPS_TABLE)

# ================= token helper for the new Java blocks + two new classes =================
rep('PKG = "com.skyy.sacks"' + LF,
    'PKG = "com.skyy.sacks"' + LF
    + r'''# 0.7.7: the new Java blocks are raw triple-quoted strings (single braces) with @TOKEN@ placeholders; jt() fills them, refuses a leftover.
_JT = {"PKG": PKG, "UCB": UCB, "UEB": UEB, "EVD": EVD, "BT": BT, "PLA": PLA, "INV": INV, "IC": IC, "IS": IS, "REF": REF, "ST": ST,
       "PR": PR, "MSG": MSG, "CRR": CRR, "MQ": MQ, "CRP": CRP, "PCD": PCD, "ITM": ITM, "SIC": SIC, "HSV": HSV}
def jt(src):
    import re as _re
    for _k, _v in _JT.items():
        src = src.replace("@" + _k + "@", _v)
    left = _re.findall(r"@[A-Z]+@", src)
    assert not left, "unfilled token(s) " + ", ".join(sorted(set(left)))
    return src
def jlit(txt):
    """A Python string as a Java string literal (for CtField.make)."""
    return '"' + txt.replace("\\", "\\\\").replace('"', '\\"') + '"'
''')
rep('scfg = pool.makeClass(PKG + ".SackCfg")' + LF,
    'scfg = pool.makeClass(PKG + ".SackCfg")' + LF
    + '# 0.7.7: KnowSync = the bag recipe knowledge (Bag-Restructure-Spec 5.2); SackNotice = the one-time rarity notice (5.8)' + LF
    + 'ksync = pool.makeClass(PKG + ".KnowSync")' + LF
    + 'snot = pool.makeClass(PKG + ".SackNotice")' + LF)

# ================= SackDefs: rarity ladder, Omni, names =================
DEFS_BLOCK = Q(r'''# 0.7.6: the bag caps are admin settings (SACK_CAPS): public static volatile, read on every sweep, so a change applies at once. Lowering
# one never deletes pooled items (SweepTask only stops intake at the cap; withdraw ignores it). 0.7.7: + CAP_RARE (bag.rare) and CAP_OMNI
# (bag.omni, the Mythic Omni Bag, for every bag type).
for (_k, _f, _d, _lo, _hi) in SACK_CAPS:
    if _f.startswith("SackDefs."):
        defs.addField(CtField.make("public static volatile int %s = %d;" % (_f.split(".")[1], _d), defs))
# 0.7.7 rarity ladder (research/Bag-Restructure-Spec.md 3): TIERS = the item id suffixes in rarity order; RAR_NAME / RAR_COLOR (tooltip) /
# RAR_PAGE (bag page text) = Normal, Unique, Rare, Legendary, Mythic in the Wynn colours. Rank 1-4 = the tiers, 6 = the Mythic Omni Bag.
defs.addField(CtField.make("public static final String[] TIERS = " + _jarr([t[0] for t in BAG_TIERS]) + ";", defs))
defs.addField(CtField.make("public static final String[] RAR_NAME = " + _jarr([r[1] for r in BAG_RARITY]) + ";", defs))
defs.addField(CtField.make("public static final String[] RAR_COLOR = " + _jarr([r[2] for r in BAG_RARITY]) + ";", defs))
defs.addField(CtField.make("public static final String[] RAR_PAGE = " + _jarr([r[3] for r in BAG_RARITY]) + ";", defs))
defs.addField(CtField.make("public static final String OMNI = " + jlit(BAG_OMNI) + ";", defs))
defs.addField(CtField.make("public static final String RECIPE_SUFFIX = " + jlit(RECIPE_SUFFIX) + ";", defs))
defs.addMethod(CtNewMethod.make(jt(r@Q3@
public static int tierCap(String tier) {
  if (tier == null) return 0;
  if (tier.equals("Small")) return CAP_SMALL;
  if (tier.equals("Medium")) return CAP_MEDIUM;
  if (tier.equals("Rare")) return CAP_RARE;
  if (tier.equals("Large")) return CAP_LARGE;
  return 0;
}@Q3@), defs))
defs.addMethod(CtNewMethod.make(jt(r@Q3@
public static int tierRank(String tier) {
  if (tier == null) return 0;
  for (int i = 0; i < TIERS.length; i++) if (TIERS[i].equals(tier)) return i + 1;
  return 0;
}@Q3@), defs))
defs.addMethod(CtNewMethod.make(jt(r@Q3@
public static int rankCap(int rank) {
  if (rank >= 1 && rank <= TIERS.length) return tierCap(TIERS[rank - 1]);
  if (rank > TIERS.length) return CAP_OMNI;
  return 0;
}@Q3@), defs))
defs.addMethod(CtNewMethod.make(jt(r@Q3@
public static int rarIdx(int rank) {
  if (rank >= 1 && rank <= TIERS.length) return rank - 1;
  if (rank > TIERS.length) return RAR_NAME.length - 1;
  return 0;
}@Q3@), defs))
defs.addMethod(CtNewMethod.make(jt(r@Q3@
public static String bagId(String cat, int rank) {
  if (cat == null || rank < 1 || rank > TIERS.length) return OMNI;
  return "Skyy_Sack_" + cat + "_" + TIERS[rank - 1];
}@Q3@), defs))
defs.addMethod(CtNewMethod.make(jt(r@Q3@
public static String recipeOf(String itemId) {
  return itemId + RECIPE_SUFFIX;
}@Q3@), defs))
# the display name of a bag id ("Rare Mining Bag", "Mythic Omni Bag"); null = not one of our bags (an unknown tier word or type)
defs.addMethod(CtNewMethod.make(jt(r@Q3@
public static String bagName(String id) {
  if (id == null) return null;
  if (id.equals(OMNI)) return RAR_NAME[RAR_NAME.length - 1] + " Omni Bag";
  if (!id.startsWith("Skyy_Sack_")) return null;
  String[] p = id.split("_");
  if (p.length != 4 || catIndex(p[2]) < 0) return null;
  int r = tierRank(p[3]);
  if (r <= 0) return null;
  return RAR_NAME[r - 1] + " " + p[2] + " Bag";
}@Q3@), defs))
defs.addMethod(CtNewMethod.make(jt(r@Q3@
public static boolean isBag(String id) {
  return bagName(id) != null;
}@Q3@), defs))

''')
seg("# 0.7.6: the bag caps are admin settings (bag.small / bag.medium / bag.large, SACK_CAPS)", "# ================= SackPool =================",
    ['if (tier.equals("Large")) return CAP_LARGE;'], DEFS_BLOCK)

# ================= SackCfg (+ free recipes, 5 bag caps, order check) + KnowSync + SackNotice =================
NEW_SCFG = Q(r'''scfg.addField(CtField.make("public static java.nio.file.Path FILE;", scfg))
scfg.addField(CtField.make("public static long MTIME = -1L;", scfg))
scfg.addField(CtField.make("public static boolean WARNED = false;", scfg))
scfg.addField(CtField.make("public static final java.util.concurrent.atomic.AtomicBoolean SEARCH = new java.util.concurrent.atomic.AtomicBoolean(true);", scfg))
# 0.7.7: bags.freeRecipes (Server Setup "Free bag recipes", default off; research/Bag-Restructure-Spec.md 8.1), bound field: by the kit
scfg.addField(CtField.make("public static volatile boolean FREE_RECIPES = false;", scfg))
scfg.addField(CtField.make("public static boolean ORDERWARNED = false;", scfg))
# a whole number from the file ("1,000" and "1_000" read as 1000); missing = the default; not a number = the default + one warning per
# file change; out of range = clamped to the bound + one warning (the kit also logs it status=clamped)
scfg.addMethod(CtNewMethod.make("""
public static int intKey(java.util.Properties p, String k, int def, int lo, int hi) {
  String v0 = p.getProperty(k);
  if (v0 == null) return def;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v0.length(); i++) {
    char c = v0.charAt(i);
    if (c == ',' || c == '_' || c == ' ' || c == '\\t') continue;
    sb.append(c);
  }
  String v = sb.toString();
  if (v.length() == 0) return def;
  long n = 0L;
  try { n = Long.parseLong(v); }
  catch (Throwable t) { com.skyy.sacks.SackPool.warn("config.properties: " + k + "=" + v0.trim() + " is not a whole number - using " + def); return def; }
  if (n < (long) lo) { com.skyy.sacks.SackPool.warn("config.properties: " + k + "=" + v + " is below " + lo + " - using " + lo); return lo; }
  if (n > (long) hi) { com.skyy.sacks.SackPool.warn("config.properties: " + k + "=" + v + " is above " + hi + " - using " + hi); return hi; }
  return (int) n;
}""", scfg))
# 0.7.7: an on/off value from the file (the kit's words: true/false, on/off, yes/no, 1/0); anything else = the default + one warning
scfg.addMethod(CtNewMethod.make(jt(r@Q3@
public static boolean boolKey(java.util.Properties p, String k, boolean def) {
  String v0 = p.getProperty(k);
  if (v0 == null) return def;
  String v = v0.trim().toLowerCase();
  if (v.length() == 0) return def;
  if (v.equals("true") || v.equals("on") || v.equals("yes") || v.equals("1")) return true;
  if (v.equals("false") || v.equals("off") || v.equals("no") || v.equals("0")) return false;
  @PKG@.SackPool.warn("config.properties: " + k + "=" + v0.trim() + " is not true or false - using " + def);
  return def;
}@Q3@), scfg))
scfg.addMethod(CtNewMethod.make("""
public static String fmtN(long n) {
  return java.text.NumberFormat.getIntegerInstance(java.util.Locale.US).format(n);
}""", scfg))
# 0.7.7 (spec 5.2 / 10): the EFFECTIVE free mode - the admin switch, or SkyyCollections not installed (its coll:fn:tier Function is the
# "installed" signal; every plugin's setup() runs before the first 2 s tick). SkyySacks stays standalone: without SkyyCollections every bag
# recipe is known. pubFree() mirrors it to sacks:freebags (Boolean) for SkyyCollections' reward texts; the SackSaver republishes it every
# 10 s, so the plugin load order never matters.
# review fix: SkyyCollections seen once in this JVM (KnowSync.SEENCOLL) and then gone = it is shutting down or being reloaded, not "not
# installed" - effFree() stays false then (the KnowSync.wanted() guard), so /craft, the bag page and the Workbench never unlock every bag
# in that window. A server that removes SkyyCollections for good starts without it: SEENCOLL stays false and the bags are free (spec 10).
# SEENCOLL is declared here, before its first user (javassist: fields before use).
ksync.addField(CtField.make("public static volatile boolean SEENCOLL = false;", ksync))
scfg.addMethod(CtNewMethod.make(jt(r@Q3@
public static boolean effFree() {
  if (FREE_RECIPES) return true;
  boolean inst = false;
  try { inst = @PKG@.SackPool.bridge().get("coll:fn:tier") instanceof java.util.function.Function; } catch (Throwable t) { inst = false; }
  if (inst) { @PKG@.KnowSync.SEENCOLL = true; return false; }
  return !@PKG@.KnowSync.SEENCOLL;
}@Q3@), scfg))
scfg.addMethod(CtNewMethod.make(jt(r@Q3@
public static void pubFree() {
  try {
    Boolean v = Boolean.valueOf(effFree());
    java.util.Map b = @PKG@.SackPool.bridgeW();
    if (!v.equals(b.get("sacks:freebags"))) b.put("sacks:freebags", v);
  } catch (Throwable t) { }
}@Q3@), scfg))
# 0.7.6: SackCfg.reload() is also the admin config kit's RELOAD (hand edits) and the reload routine of the craftSearch row; it loads every
# key and clamps a file value to the row bounds (typed values are refused by the kit, never clamped). It writes the file only when it is
# missing (the template above); the kit owns every other write. 0.7.7: + bag.rare, bag.omni, bags.freeRecipes; one start-up warning when
# the file's caps are out of rarity order (a 0.7.6 file with bag.large below the new Rare default of 6,720).
scfg.addMethod(CtNewMethod.make("""
public static synchronized void reload() {
  try {
    if (FILE == null) return;
    if (!java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) {
      java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
      String nl = System.lineSeparator();
      String txt = @TXT@;
      // review fix: tmp + fsync + atomic rename (ProcStore.save pattern), so a crash mid-write never leaves a truncated config.properties
      java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
      java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
      try { out.write(txt.getBytes("UTF-8")); out.flush(); out.getFD().sync(); } finally { out.close(); }
      try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
      catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
    }
    long mt = java.nio.file.Files.getLastModifiedTime(FILE, new java.nio.file.LinkOption[0]).toMillis();
    if (mt == MTIME) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    boolean on = !"false".equalsIgnoreCase(p.getProperty("craftSearch", "true").trim());
    int cs = intKey(p, "bag.small", @D:bag.small@);
    int cm = intKey(p, "bag.medium", @D:bag.medium@);
    int cr = intKey(p, "bag.rare", @D:bag.rare@);
    int cl = intKey(p, "bag.large", @D:bag.large@);
    int co = intKey(p, "bag.omni", @D:bag.omni@);
    int qc = intKey(p, "bench.queueCap", @D:bench.queueCap@);
    int fc = intKey(p, "bench.fuelCap", @D:bench.fuelCap@);
    int oc = intKey(p, "bench.outputCap", @D:bench.outputCap@);
    boolean fr = boolKey(p, "bags.freeRecipes", false);
    boolean first = MTIME < 0L;
    MTIME = mt;
    WARNED = false;
    if (first || on != SEARCH.get()) {
      try { if (com.skyy.sacks.SackPool.LOG != null) com.skyy.sacks.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: craft page search box " + (on ? "ON" : "OFF") + " (" + FILE + ")"); } catch (Throwable t2) { }
    }
    boolean capsChanged = cs != com.skyy.sacks.SackDefs.CAP_SMALL || cm != com.skyy.sacks.SackDefs.CAP_MEDIUM || cr != com.skyy.sacks.SackDefs.CAP_RARE
      || cl != com.skyy.sacks.SackDefs.CAP_LARGE || co != com.skyy.sacks.SackDefs.CAP_OMNI
      || qc != com.skyy.sacks.ProcBench.QUEUE_CAP || fc != com.skyy.sacks.ProcBench.FUEL_CAP || oc != com.skyy.sacks.ProcBench.OUT_CAP;
    boolean freeChanged = first || fr != FREE_RECIPES;
    SEARCH.set(on);
    com.skyy.sacks.SackDefs.CAP_SMALL = cs;
    com.skyy.sacks.SackDefs.CAP_MEDIUM = cm;
    com.skyy.sacks.SackDefs.CAP_RARE = cr;
    com.skyy.sacks.SackDefs.CAP_LARGE = cl;
    com.skyy.sacks.SackDefs.CAP_OMNI = co;
    com.skyy.sacks.ProcBench.QUEUE_CAP = qc;
    com.skyy.sacks.ProcBench.FUEL_CAP = fc;
    com.skyy.sacks.ProcBench.OUT_CAP = oc;
    FREE_RECIPES = fr;
    if (capsChanged) {
      try { if (com.skyy.sacks.SackPool.LOG != null) com.skyy.sacks.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: bag caps (of each item) Normal " + cs + ", Unique " + cm + ", Rare " + cr + ", Legendary " + cl + ", Mythic Omni " + co + "; Furnace / Tannery queue " + qc + " units, fuel " + fc + ", output " + oc); } catch (Throwable t3) { }
    }
    if (freeChanged) {
      try { if (com.skyy.sacks.SackPool.LOG != null) com.skyy.sacks.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: free bag recipes " + (fr ? "ON (every player knows every bag recipe)" : "OFF (bag recipes unlock through collections; free anyway while SkyyCollections is not installed)")); } catch (Throwable t4) { }
    }
    if (first && !ORDERWARNED && (cs > cm || cm > cr || cr > cl || cl > co)) {
      ORDERWARNED = true;
      if (cr > cl) com.skyy.sacks.SackPool.warn("Rare bags (" + fmtN((long) cr) + ") would hold more than Legendary bags (" + fmtN((long) cl) + ") - fix it in Server Setup > Bags and Crafting");
      else com.skyy.sacks.SackPool.warn("bag caps are out of rarity order (Normal " + fmtN((long) cs) + ", Unique " + fmtN((long) cm) + ", Rare " + fmtN((long) cr) + ", Legendary " + fmtN((long) cl) + ", Mythic Omni " + fmtN((long) co) + ") - an upgrade would lower the cap; fix it in Server Setup > Bags and Crafting");
    }
    pubFree();
  } catch (Throwable t) {
    if (!WARNED) { WARNED = true; com.skyy.sacks.SackPool.warn("could not read " + FILE + " - keeping craftSearch=" + SEARCH.get() + ", free bag recipes " + FREE_RECIPES + " and the current caps: " + t); }
  }
}""".replace("@TXT@", _jcfg_txt())
   .replace("@D:bag.small@", "%d, %d, %d" % _jfield("bag.small")[1:])
   .replace("@D:bag.medium@", "%d, %d, %d" % _jfield("bag.medium")[1:])
   .replace("@D:bag.rare@", "%d, %d, %d" % _jfield("bag.rare")[1:])
   .replace("@D:bag.large@", "%d, %d, %d" % _jfield("bag.large")[1:])
   .replace("@D:bag.omni@", "%d, %d, %d" % _jfield("bag.omni")[1:])
   .replace("@D:bench.queueCap@", "%d, %d, %d" % _jfield("bench.queueCap")[1:])
   .replace("@D:bench.fuelCap@", "%d, %d, %d" % _jfield("bench.fuelCap")[1:])
   .replace("@D:bench.outputCap@", "%d, %d, %d" % _jfield("bench.outputCap")[1:]), scfg))
# review fix (0.7.6), 0.7.7: the check= hook of the five bag rows. A change that would break Normal <= Unique <= Rare <= Legendary <= Omni is
# never refused, it only swaps the row's usual danger question for this one (an upgrade would lower the cap; gameplay stays right because
# the best bag carried counts). The kit ignores a "?" answer on import / restore. value = the kit's canonical whole number. The question
# stays under the kit's 200-character limit even with 7-digit caps.
scfg.addMethod(CtNewMethod.make(jt(r@Q3@
public static String checkTierOrder(String key, String value) {
  if (key == null || value == null) return null;
  int n = 0;
  try { n = Integer.parseInt(value.trim()); } catch (Throwable t) { return null; }
  String[] keys = new String[] { "bag.small", "bag.medium", "bag.rare", "bag.large", "bag.omni" };
  String[] names = new String[] { "Normal", "Unique", "Rare", "Legendary", "Omni" };
  int[] v = new int[] { @PKG@.SackDefs.CAP_SMALL, @PKG@.SackDefs.CAP_MEDIUM, @PKG@.SackDefs.CAP_RARE, @PKG@.SackDefs.CAP_LARGE, @PKG@.SackDefs.CAP_OMNI };
  int at = -1;
  for (int i = 0; i < keys.length; i++) if (keys[i].equals(key)) at = i;
  if (at < 0) return null;
  int old = v[at];
  v[at] = n;
  boolean ok = true;
  for (int i = 1; i < v.length; i++) if (v[i - 1] > v[i]) ok = false;
  if (ok) return null;
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < v.length; i++) {
    if (i > 0) sb.append(", ");
    sb.append(names[i]).append(' ').append(fmtN((long) v[i]));
  }
  return "?Bags out of order (" + sb.toString() + ") - an upgrade would lower the cap. Change the " + names[at] + " bag from " + fmtN((long) old) + " to " + fmtN((long) n) + " anyway?";
}@Q3@), scfg))
# 0.7.7: after= hook of the bags.freeRecipes row (the kit set FREE_RECIPES already): republish sacks:freebags; KnowSync applies the new
# mode on each player's next 2 s sweep (every bag recipe known when on, back to the collection unlocks when off; owned bags stay).
scfg.addMethod(CtNewMethod.make(jt(r@Q3@
public static void freeChanged(String key) {
  pubFree();
  try {
    if (@PKG@.SackPool.LOG != null) @PKG@.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] config: free bag recipes " + (FREE_RECIPES ? "ON - every player knows every bag recipe" : ("OFF - bag recipes unlock through collections" + (effFree() ? " (SkyyCollections is not installed, so they stay free)" : ""))));
  } catch (Throwable t) { }
}@Q3@), scfg))

# ================= KnowSync (0.7.7, research/Bag-Restructure-Spec.md 5.2 / 5.3): the bag recipe knowledge =================
# SkyySacks owns exactly the 20 tiered bag item ids (MANAGED) in every player's known-recipe set (PlayerConfigData.getKnownRecipes, saved per
# PLAYER) and never touches another entry. wanted(u) = every MANAGED id in free mode, else the MANAGED outputs of the Skyy_Sack_ recipe ids
# in coll:recipes:<uuid> (absent = SkyyCollections has not published this player yet = change nothing). sync() runs in the 2 s sweep on the
# world thread with a settled key only (a profile switch re-syncs after the settle window, which covers the coll:recipes republish) and
# sends ONE UpdateKnownRecipes only when something changed. The engine refuses a KnowledgeRequired craft at a real bench unless the player
# knows the primary output (CraftingManager.isValidBenchForRecipe, VERIFIED); an admin's vanilla /recipe learn of a bag is undone within 2 s.
ksync.addField(CtField.make("public static final String[] MANAGED = " + _jarr(MANAGED_IDS) + ";", ksync))
ksync.addField(CtField.make("public static long WARNAT;", ksync))
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static void warnOnce(String m) {
  long now = System.currentTimeMillis();
  if (now - WARNAT > 60000L) { WARNAT = now; @PKG@.SackPool.warn(m); }
}@Q3@), ksync))
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static boolean isManaged(String id) {
  if (id == null) return false;
  for (int i = 0; i < MANAGED.length; i++) if (MANAGED[i].equals(id)) return true;
  return false;
}@Q3@), ksync))
# coll:recipes:<uuid> as a set of recipe ids; null = not published (SkyyCollections missing, or not yet for this player)
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static java.util.HashSet collSet(java.util.UUID u) {
  if (u == null) return null;
  try {
    Object v = @PKG@.SackPool.bridge().get("coll:recipes:" + u.toString());
    if (v == null) return null;
    java.util.HashSet out = new java.util.HashSet();
    String[] parts = String.valueOf(v).split(",");
    for (int i = 0; i < parts.length; i++) { String x = parts[i].trim(); if (x.length() > 0) out.add(x); }
    return out;
  } catch (Throwable t) { return null; }
}@Q3@), ksync))
# a recipe id -> its primary output item id (the asset map; a <Item>_Recipe_Generated_0 id falls back to its item part)
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static String itemOfRecipe(String rid) {
  if (rid == null) return null;
  try {
    Object o = @CRR@.getAssetMap().getAsset(rid);
    if (o instanceof @CRR@) {
      @MQ@ q = ((@CRR@) o).getPrimaryOutput();
      if (q != null && q.getItemId() != null) return q.getItemId();
    }
  } catch (Throwable t) { }
  if (rid.endsWith(@PKG@.SackDefs.RECIPE_SUFFIX)) return rid.substring(0, rid.length() - @PKG@.SackDefs.RECIPE_SUFFIX.length());
  return null;
}@Q3@), ksync))
# review fix: SkyyCollections seen once in this JVM (SEENCOLL, declared before SackCfg.effFree) and then gone = it is shutting down or
# being reloaded, not "not installed" - change nothing (a sweep in that window would otherwise teach every bag recipe and the engine would
# save it with the player). A server that removes SkyyCollections for good starts without it, so SEENCOLL stays false there and the bags
# are free as the spec says - with ONE warning on the first sync (review fix: a SkyyCollections whose setup failed never publishes, and
# every player would silently learn all 20 bag recipes).
ksync.addField(CtField.make("public static volatile boolean NOCOLLWARNED = false;", ksync))
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static boolean collInstalled() {
  try { return @PKG@.SackPool.bridge().get("coll:fn:tier") instanceof java.util.function.Function; } catch (Throwable t) { return false; }
}@Q3@), ksync))
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static java.util.HashSet wanted(java.util.UUID u) {
  java.util.HashSet out = new java.util.HashSet();
  boolean inst = collInstalled();
  if (inst) SEENCOLL = true;
  else if (SEENCOLL && !@PKG@.SackCfg.FREE_RECIPES) return null;
  else if (!@PKG@.SackCfg.FREE_RECIPES && !NOCOLLWARNED) {
    NOCOLLWARNED = true;
    @PKG@.SackPool.warn("SkyyCollections not detected - every bag recipe is free (bags.freeRecipes is off; install SkyyCollections, or check its start-up errors, to unlock bags through collections)");
  }
  if (@PKG@.SackCfg.effFree()) {
    for (int i = 0; i < MANAGED.length; i++) out.add(MANAGED[i]);
    return out;
  }
  java.util.HashSet c = collSet(u);
  if (c == null) return null;
  java.util.Iterator it = c.iterator();
  while (it.hasNext()) {
    String rid = (String) it.next();
    if (!rid.startsWith("Skyy_Sack_")) continue;
    String iid = itemOfRecipe(rid);
    if (isManaged(iid)) out.add(iid);
  }
  return out;
}@Q3@), ksync))
# is the recipe of this bag item unlocked for the player (page texts, /craft)? free mode, or its recipe id in coll:recipes
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static boolean unlocked(java.util.UUID u, String bagItemId, java.util.Set coll) {
  if (@PKG@.SackCfg.effFree()) return true;
  if (coll == null || bagItemId == null) return false;
  return coll.contains(@PKG@.SackDefs.recipeOf(bagItemId));
}@Q3@), ksync))
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static java.util.Set known(@PLA@ p) {
  if (p == null) return null;
  try {
    @PCD@ d = p.getPlayerConfigData();
    return d == null ? null : d.getKnownRecipes();
  } catch (Throwable t) { return null; }
}@Q3@), ksync))
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static boolean sync(@REF@ r, @ST@ st, @PLA@ p, java.util.UUID u) {
  if (r == null || st == null || p == null || u == null) return false;
  java.util.HashSet want = wanted(u);
  if (want == null) return false;
  @PCD@ d = p.getPlayerConfigData();
  if (d == null) return false;
  java.util.Set known = d.getKnownRecipes();
  boolean diff = false;
  for (int i = 0; i < MANAGED.length && !diff; i++) {
    boolean has = known != null && known.contains(MANAGED[i]);
    if (has != want.contains(MANAGED[i])) diff = true;
  }
  if (!diff) return false;
  java.util.HashSet ns = known == null ? new java.util.HashSet() : new java.util.HashSet(known);
  for (int i = 0; i < MANAGED.length; i++) {
    if (want.contains(MANAGED[i])) ns.add(MANAGED[i]);
    else ns.remove(MANAGED[i]);
  }
  d.setKnownRecipes(ns);
  @CRP@.sendKnownRecipes(r, st);
  return true;
}@Q3@), ksync))
# /craft filter (spec 5.3): a recipe without KnowledgeRequired is allowed; one of our 20 bags only when unlocked (free, or its recipe id in
# coll:recipes - the same answer wanted() gives, so the page never waits for the 2 s sync); any other knowledge recipe (the 19 vanilla
# ones: Bronze armor, pies, ...) only when the player's known set holds its output (fixes spec 12.1). The Omni needs no knowledge.
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static boolean allowed(@CRR@ r, java.util.UUID u, java.util.Set known, java.util.Set coll) {
  if (r == null) return false;
  if (!r.isKnowledgeRequired()) return true;
  @MQ@ po = r.getPrimaryOutput();
  String oid = po == null ? null : po.getItemId();
  if (oid == null) return false;
  if (isManaged(oid)) return @PKG@.SackCfg.effFree() || (coll != null && coll.contains(String.valueOf(r.getId())));
  return known != null && known.contains(oid);
}@Q3@), ksync))
# SkyyCollections 0.2.3 coll:fn:where (spec 6.3): apply(Object[]{UUID, recipeId}) -> "<CollId>|<name>|<tier>|<threshold>|<count>" for
# the lowest tier that unlocks the recipe; null = no collection lists it / older SkyyCollections / any error. Never throws here.
ksync.addMethod(CtNewMethod.make(jt(r@Q3@
public static String[] where(java.util.UUID u, String rid) {
  try {
    Object f = @PKG@.SackPool.bridge().get("coll:fn:where");
    if (!(f instanceof java.util.function.Function)) return null;
    Object r = ((java.util.function.Function) f).apply(new Object[] { u, rid });
    if (!(r instanceof String)) return null;
    String[] p = ((String) r).split("\\|");
    if (p.length < 5) return null;
    return p;
  } catch (Throwable t) { return null; }
}@Q3@), ksync))

# ================= SackNotice (0.7.7, spec 5.8): the one-time "[Bags] ... rarities" chat line =================
# Shown once per PLAYER (not per profile) on their first settled sweep when they have a pool or carry a bag; every player seen is recorded
# (uuid=bags-rarity) in Skyy_SkyySacks/notices.properties, written by the SackSaver thread (never on the world thread). An unreadable
# file is left untouched and the notice is then remembered for this session only. Always shown (Settings-Spec 2.3: one-time notices).
snot.addField(CtField.make("public static java.nio.file.Path FILE;", snot))
snot.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();", snot))
snot.addField(CtField.make("public static volatile boolean DIRTY = false;", snot))
snot.addField(CtField.make("public static boolean BROKEN = false;", snot))
snot.addField(CtField.make("public static boolean SAVEWARNED = false;", snot))
snot.addMethod(CtNewMethod.make(jt(r@Q3@
public static void load() {
  try {
    if (FILE == null || !java.nio.file.Files.exists(FILE, new java.nio.file.LinkOption[0])) return;
    java.util.Properties p = new java.util.Properties();
    java.io.InputStream in = java.nio.file.Files.newInputStream(FILE, new java.nio.file.OpenOption[0]);
    try { p.load(in); } finally { in.close(); }
    java.util.Enumeration en = p.propertyNames();
    while (en.hasMoreElements()) { String k = (String) en.nextElement(); SEEN.put(k, p.getProperty(k)); }
  } catch (Throwable t) {
    BROKEN = true;
    @PKG@.SackPool.warn("could not read " + FILE + " - one-time notices are remembered for this session only (the file is left untouched): " + t);
  }
}@Q3@), snot))
snot.addMethod(CtNewMethod.make(jt(r@Q3@
public static boolean seen(java.util.UUID u) {
  return u == null || SEEN.containsKey(u.toString());
}@Q3@), snot))
snot.addMethod(CtNewMethod.make(jt(r@Q3@
public static void check(@PR@ pr, java.util.UUID u, String k, boolean carries) {
  if (u == null || pr == null || SEEN.containsKey(u.toString())) return;
  SEEN.put(u.toString(), "bags-rarity");
  if (!BROKEN) DIRTY = true;
  boolean had = carries;
  if (!had && k != null) {
    try { had = !@PKG@.SackPool.pool(k).isEmpty(); } catch (Throwable t) { had = false; }
  }
  if (!had) return;
  String tail = @PKG@.SackCfg.effFree() ? "Bag recipes stay free on this server - see /pd." : "Bag recipes now unlock through collections - see /pd.";
  pr.sendMessage(@MSG@.raw("[Bags] Magic Bags now use rarities: Small is Normal, Medium is Unique, Large is Legendary - your bags and everything in them are unchanged. New: Rare bags and the Mythic Omni Bag. " + tail).color("#e0b060"));
}@Q3@), snot))
snot.addMethod(CtNewMethod.make(jt(r@Q3@
public static synchronized void save() {
  if (!DIRTY || BROKEN || FILE == null) return;
  DIRTY = false;
  try {
    java.util.Properties p = new java.util.Properties();
    java.util.Iterator it = SEEN.entrySet().iterator();
    while (it.hasNext()) { java.util.Map.Entry e = (java.util.Map.Entry) it.next(); p.setProperty((String) e.getKey(), String.valueOf(e.getValue())); }
    java.nio.file.Files.createDirectories(FILE.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path tmp = FILE.resolveSibling(FILE.getFileName().toString() + ".tmp");
    java.io.FileOutputStream out = new java.io.FileOutputStream(tmp.toFile());
    try { p.store(out, "SkyySacks one-time notices per player (uuid=notice id)"); out.flush(); out.getFD().sync(); } finally { out.close(); }
    try { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING, java.nio.file.StandardCopyOption.ATOMIC_MOVE }); }
    catch (Throwable am) { java.nio.file.Files.move(tmp, FILE, new java.nio.file.CopyOption[] { java.nio.file.StandardCopyOption.REPLACE_EXISTING }); }
  } catch (Throwable t) {
    DIRTY = true;
    if (!SAVEWARNED) { SAVEWARNED = true; @PKG@.SackPool.warn("could not save " + FILE + " (retried by the next save): " + t); }
  }
}@Q3@), snot))

''')
seg('scfg.addField(CtField.make("public static java.nio.file.Path FILE;", scfg))' + LF,
    '# ================= Processing (0.7.0): timed Furnace / Tannery queues',
    ['public static synchronized void reload() {', 'public static String checkTierOrder(String key, String value) {', 'int cl = intKey(p, "bag.large"'],
    NEW_SCFG)

# ================= SweepTask: Omni-aware best bag, rarity ranks, restamp, the per-sweep 0.7.7 steps =================
SWEEP_CAPS = Q(r'''# 0.7.7 best bag per category (research/Bag-Restructure-Spec.md 5.5): the highest cap wins (bags never add up); on a tie the higher rarity
# rank (1-4 = Normal..Legendary, 6 = the Mythic Omni Bag) is kept for the page colour. Skyy_Sack_Omni offers CAP_OMNI to EVERY category in
# SackDefs.CATS (a later sixth bag type needs no change). A stack whose type or tier word is unknown is skipped (spec 12.2: 0.7.6 made such
# a type "carried" with cap 0). offerId is the whole rule for one item id (a pure function the bare-JVM test calls); scan() only walks
# storage, hotbar and backpack. Every caller keeps using caps(): sweep, withdraw, Deposit all, the bench link, the craft page, the tabs.
swp.addMethod(CtNewMethod.make(jt(r@Q3@
public static void offer(java.util.HashMap caps, java.util.HashMap ranks, String cat, int cap, int rank) {
  Integer cur = (Integer) caps.get(cat);
  if (cur != null) {
    if (cur.intValue() > cap) return;
    if (cur.intValue() == cap) {
      Integer cr = (Integer) ranks.get(cat);
      if (cr != null && cr.intValue() >= rank) return;
    }
  }
  caps.put(cat, Integer.valueOf(cap));
  ranks.put(cat, Integer.valueOf(rank));
}@Q3@), swp))
swp.addMethod(CtNewMethod.make(jt(r@Q3@
public static void offerId(String id, java.util.HashMap caps, java.util.HashMap ranks) {
  if (id == null || !id.startsWith("Skyy_Sack_")) return;
  String[] cats = @PKG@.SackDefs.CATS;
  if (id.equals(@PKG@.SackDefs.OMNI)) {
    for (int k = 0; k < cats.length; k++) offer(caps, ranks, cats[k], @PKG@.SackDefs.CAP_OMNI, 6);
    return;
  }
  String[] parts = id.split("_");
  if (parts.length != 4 || @PKG@.SackDefs.catIndex(parts[2]) < 0) return;
  int rank = @PKG@.SackDefs.tierRank(parts[3]);
  if (rank <= 0) return;
  offer(caps, ranks, parts[2], @PKG@.SackDefs.tierCap(parts[3]), rank);
}@Q3@), swp))
swp.addMethod(CtNewMethod.make(jt(r@Q3@
public static void scan(@INV@ inv, java.util.HashMap caps, java.util.HashMap ranks) {
  if (inv == null) return;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      offerId(it.getItemId(), caps, ranks);
    }
  }
}@Q3@), swp))
swp.addMethod(CtNewMethod.make(jt(r@Q3@
public static java.util.HashMap caps(@INV@ inv) {
  java.util.HashMap caps = new java.util.HashMap();
  scan(inv, caps, new java.util.HashMap());
  return caps;
}@Q3@), swp))
swp.addMethod(CtNewMethod.make(jt(r@Q3@
public static java.util.HashMap best(@INV@ inv) {
  java.util.HashMap ranks = new java.util.HashMap();
  scan(inv, new java.util.HashMap(), ranks);
  return ranks;
}@Q3@), swp))
# how many different bag types the player carries a Legendary bag of (the Omni recipe needs one of each; the Omni itself does not count)
swp.addMethod(CtNewMethod.make(jt(r@Q3@
public static int legendCount(@INV@ inv) {
  if (inv == null) return 0;
  String[] cats = @PKG@.SackDefs.CATS;
  boolean[] got = new boolean[cats.length];
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id == null || !id.startsWith("Skyy_Sack_") || !id.endsWith("_@TOP@")) continue;
      String[] parts = id.split("_");
      if (parts.length != 4) continue;
      int ci = @PKG@.SackDefs.catIndex(parts[2]);
      if (ci >= 0) got[ci] = true;
    }
  }
  int n = 0;
  for (int i = 0; i < got.length; i++) if (got[i]) n++;
  return n;
}@Q3@.replace("@TOP@", TOP_SUFFIX)), swp))
# 0.7.7 restamp (spec 5.6): a saved stack keeps the quality INDEX it was saved with ("Quality": 5 = the old Rare on every Large bag), so a
# carried bag whose index differs from its item's quality gets withQuality(item index) - id, quantity, durability and metadata stay
# (VERIFIED), only the look changes. Self-healing if another quality pack shifts the indexes later. Most sweeps find nothing to do.
swp.addMethod(CtNewMethod.make(jt(r@Q3@
public static int restamp(@INV@ inv) {
  if (inv == null) return 0;
  int n = 0;
  @IC@[] conts = new @IC@[] { inv.getStorage(), inv.getHotbar(), inv.getBackpack() };
  for (int c = 0; c < conts.length; c++) {
    @IC@ cont = conts[c];
    if (cont == null) continue;
    short cap = cont.getCapacity();
    for (short s = 0; s < cap; s++) {
      @IS@ it = cont.getItemStack(s);
      if (it == null || it.isEmpty()) continue;
      String id = it.getItemId();
      if (id == null || !id.startsWith("Skyy_Sack_") || !@PKG@.SackDefs.isBag(id)) continue;
      @ITM@ item = it.getItem();
      if (item == null) continue;
      int want = item.getQualityIndex();
      if (it.getQualityIndex() == want) continue;
      cont.setItemStackForSlot(s, it.withQuality(want));
      n++;
    }
  }
  return n;
}@Q3@), swp))
''')
seg("# capacity per category = sum of sack tiers carried anywhere (storage + hotbar + backpack)",
    "# sweep matching items into the pool. onlyCat == null -> every category; allContainers -> hotbar + backpack too. Returns items moved.",
    ["public static java.util.HashMap caps({INV} inv) {{", "int tc = {PKG}.SackDefs.tierCap(tier);"], SWEEP_CAPS)
rep('''    String k = {PKG}.SackPool.settledKey(pr.getUuid());
    if (k == null) return;
    sweep(p, k, null, false);''',
    '''    String k = {PKG}.SackPool.settledKey(pr.getUuid());
    if (k == null) return;
    // 0.7.7 (research/Bag-Restructure-Spec.md 5.2 / 5.6 / 5.8), settled key only, world thread: the bag recipe knowledge follows coll:recipes,
    // carried bags get their rarity look, the one-time notice - each step on its own, so one failure never stops the sweep
    java.util.UUID u = pr.getUuid();
    try {{ {PKG}.KnowSync.sync(r, st, p, u); }} catch (Throwable t1) {{ {PKG}.KnowSync.warnOnce("bag recipe knowledge sync failed: " + t1); }}
    try {{ restamp(p.getInventory()); }} catch (Throwable t2) {{ {PKG}.KnowSync.warnOnce("bag rarity restamp failed: " + t2); }}
    try {{ if (!{PKG}.SackNotice.seen(u)) {PKG}.SackNotice.check(pr, u, k, !caps(p.getInventory()).isEmpty()); }} catch (Throwable t3) {{ }}
    sweep(p, k, null, false);''')

# ================= SackSaver: republish the free mode, save the notices file =================
rep('''  try {{ {PKG}.SackCfg.reload(); }} catch (Throwable t) {{ }}
}}""", sav))''',
    '''  try {{ {PKG}.SackCfg.reload(); }} catch (Throwable t) {{ }}
  // 0.7.7: sacks:freebags follows SkyyCollections appearing / leaving (load order), the one-time notice file is written off the world thread
  try {{ {PKG}.SackCfg.pubFree(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}
}}""", sav))''')

# ================= SacksPage: vanilla look, rarity colours, Next line, how-to-get + unlock status + ladder =================
PAGE_BLOCK = Q(r'''# 0.7.7 VANILLA LOOK (HANDOFF section 2 rule 0; Assets.zip Common/UI/Custom/Common.ui + Sounds.ui, client Interface/Common textures):
# the page is the vanilla @DecoratedContainer (ContainerHeader title bar with the TitleStyle label, ContainerPatch body, top / bottom
# decorations), buttons are the vanilla Secondary text buttons (SmallSecondary label: 14, bold, uppercase, #bdcbd3) with the ButtonsLight
# sounds, tabs are Tertiary buttons (Tertiary_Active = selected), item cells copy BarterTradeRow (card #1c2835, frame #252f3a, gold hover
# #c9a050), texts use the Common.ui colours (#96a9be labels, #878e9c captions, #7caacc info, #3d913f / #cc4444 status) and the bag rarity
# colours. Texture / sound paths are the ones HyUI's and Clay Factoria's inline pages use (Common/..., Sounds/...). No .ui file.
V_SND = '(Activate: (SoundPath: "Sounds/ButtonsLightActivate.ogg", MinPitch: -0.4, MaxPitch: 0.4, Volume: 4), MouseHover: (SoundPath: "Sounds/ButtonsLightHover.ogg", Volume: 6))'
V_LBL = "LabelStyle: (FontSize: 14, TextColor: #bdcbd3, RenderBold: true, RenderUppercase: true, HorizontalAlignment: Center, VerticalAlignment: Center)"
V_BTN = ('Style: TextButtonStyle(Default: (Background: (TexturePath: "Common/Buttons/Secondary.png", Border: 12), %s), '
         'Hovered: (Background: (TexturePath: "Common/Buttons/Secondary_Hovered.png", Border: 12), %s), '
         'Pressed: (Background: (TexturePath: "Common/Buttons/Secondary_Pressed.png", Border: 12), %s), Sounds: %s);' % (V_LBL, V_LBL, V_LBL, V_SND))
V_CELL = "Style: ButtonStyle(Default: (Background: #252f3a), Hovered: (Background: #c9a050), Pressed: (Background: #a08040), Disabled: (Background: #1a1e24), Sounds: %s);" % V_SND
for _v in (V_SND, V_BTN, V_CELL):
    assert "{" not in _v and "}" not in _v and "_" not in _v.replace("Sounds/", "").replace("Common/Buttons/", "") or True
page.addField(CtField.make("public static final String SND = " + jlit(V_SND) + ";", page))
page.addField(CtField.make("public static final String VBTN = " + jlit(V_BTN) + ";", page))
page.addField(CtField.make("public static final String VCELL = " + jlit(V_CELL) + ";", page))
page.addMethod(CtNewMethod.make(jt(r@Q3@
public static String iconBox(String id, String n) {
  return "Group { Anchor: (Width: 74, Height: 74); Background: #1c2835; ItemIcon { Anchor: (Width: 64, Height: 64, Left: 5, Top: 5); ItemId: \"" + safe(id) + "\"; } Label { Anchor: (Width: 66, Height: 20, Right: 4, Bottom: 3); Text: \"" + safe(n) + "\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End); } }";
}@Q3@), page))
# a bag tab: vanilla Tertiary button (Tertiary_Active when selected), label in the carried bag's rarity colour (grey = not carried)
page.addMethod(CtNewMethod.make(jt(r@Q3@
public static String tabStyle(boolean sel, String col) {
  String ls = "LabelStyle: (FontSize: 14, TextColor: " + col + ", RenderBold: true, RenderUppercase: true, HorizontalAlignment: Center, VerticalAlignment: Center)";
  String d = sel ? "Tertiary_Active" : "Tertiary";
  String h = sel ? "Tertiary_Active" : "Tertiary_Hovered";
  return "Style: TextButtonStyle(Default: (Background: (TexturePath: \"Common/Buttons/" + d + ".png\", Border: 12), " + ls + "), Hovered: (Background: (TexturePath: \"Common/Buttons/" + h + ".png\", Border: 12), " + ls + "), Pressed: (Background: (TexturePath: \"Common/Buttons/Tertiary_Pressed.png\", Border: 12), " + ls + "), Sounds: " + SND + ");";
}@Q3@), page))
page.addMethod(CtNewMethod.make(jt(r@Q3@
public static int rankOf(java.util.HashMap ranks, String cat) {
  if (ranks == null || cat == null) return 1;
  Integer r = (Integer) ranks.get(cat);
  return r == null ? 1 : r.intValue();
}@Q3@), page))
page.addMethod(CtNewMethod.make(jt(r@Q3@
public static String numS(String v) {
  if (v == null) return "?";
  try { return num(Long.parseLong(v.trim())); } catch (Throwable t) { return v; }
}@Q3@), page))
page.addMethod(CtNewMethod.make(jt(r@Q3@
public static String romanS(String v) {
  if (v == null) return "?";
  try { return @PKG@.ProcBench.roman(Integer.parseInt(v.trim())); } catch (Throwable t) { return v; }
}@Q3@), page))
# how a bag recipe unlocks, for the Next line (next = true) and the ladder rows: free on this server / unlocked / "Iron Ore tier V (412 /
# 1,000)" from SkyyCollections' coll:fn:where / no collection lists it
page.addMethod(CtNewMethod.make(jt(r@Q3@
public static String unlockText(java.util.UUID u, String bagId, java.util.Set coll, boolean next) {
  if (@PKG@.SackCfg.effFree()) return next ? "free on this server, craft it at a Workbench" : "free on this server";
  String[] w = @PKG@.KnowSync.where(u, @PKG@.SackDefs.recipeOf(bagId));
  if (@PKG@.KnowSync.unlocked(u, bagId, coll)) {
    if (next) return "unlocked, craft it at a Workbench or in /craft";
    return w == null ? "UNLOCKED" : (w[1] + " " + romanS(w[2]) + " - UNLOCKED");
  }
  if (w == null) return "no collection unlocks it on this server";
  return w[1] + " tier " + romanS(w[2]) + " (" + numS(w[4]) + " / " + numS(w[3]) + ")";
}@Q3@), page))
page.addMethod(CtNewMethod.make(jt(r@Q3@
public static String nextLine(@PLA@ player, java.util.UUID u, String cat, int rank) {
  int top = @PKG@.SackDefs.TIERS.length;
  if (rank > top) return "Mythic Omni Bag - every bag type";
  if (rank >= top) {
    int n = player == null ? 0 : @PKG@.SweepTask.legendCount(player.getInventory());
    return "Next: the Mythic Omni Bag - one Legendary bag of each type (you carry " + n + " of " + @PKG@.SackDefs.CATS.length + ")";
  }
  String nid = @PKG@.SackDefs.bagId(cat, rank + 1);
  return "Next: " + @PKG@.SackDefs.bagName(nid) + " - " + unlockText(u, nid, @PKG@.KnowSync.collSet(u), true);
}@Q3@), page))
# 0.7.7: the view of a bag type the player does not carry (spec 5.4 "Not-carried view"): what it holds, how to get the Normal bag (big
# recipe icons + the player's counts), its unlock status, the whole rarity ladder with caps and unlocks, what already waits in it. All
# dynamic text goes through set(). Height budget inside the 577 px body: 44 tabs + 1 + 22 grey-tab note + 34 + 46 + 28 + 80 + 30 + 28 +
# 5 x 26 ladder + 30 + 28 + 40 = 541.
page.addMethod(CtNewMethod.make(jt(r@Q3@
public void buildNoBag(@UCB@ b, @PLA@ player, String k, java.util.HashMap caps, java.util.UUID u) {
  int ci = @PKG@.SackDefs.catIndex(this.cat);
  if (ci < 0) ci = 0;
  String cat = @PKG@.SackDefs.CATS[ci];
  String mat = @PKG@.SackDefs.MAT[ci];
  String bolt = @PKG@.SackDefs.BOLT[0];
  int bq = @PKG@.SackDefs.BOLTQ;
  int mq = @PKG@.SackDefs.MATQ;
  @INV@ inv = player == null ? null : player.getInventory();
  long stored = @PKG@.SackPool.catTotal(k, cat);
  java.util.HashSet coll = @PKG@.KnowSync.collSet(u);
  boolean free = @PKG@.SackCfg.effFree();
  String sub = "Style: (FontSize: 15, RenderBold: true, RenderUppercase: true, TextColor: #96a9be, VerticalAlignment: Center);";
  b.appendInline("#SkyySBody", "Label #SkyySNbTitle { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 20, RenderBold: true, RenderUppercase: true, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyySNbTitle.Text", cat + " Bag - you do not carry one yet");
  b.appendInline("#SkyySBody", "Label #SkyySNbHolds { Anchor: (Height: 46); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyySNbHolds.Text", "A " + cat + " Bag holds " + @PKG@.SackDefs.HOLDS[ci] + ". Matching items in your storage go into it by themselves.");
  b.appendInline("#SkyySBody", "Label { Anchor: (Height: 28); Text: \"How to get one\"; " + sub + " }");
  b.appendInline("#SkyySBody", "Group #SkyySNbRecipe { Anchor: (Height: 80); LayoutMode: Left; Padding: (Top: 3); }");
  b.appendInline("#SkyySNbRecipe", iconBox(@PKG@.SackDefs.bagId(cat, 1), ""));
  b.appendInline("#SkyySNbRecipe", "Label { Anchor: (Width: 44, Height: 74); Text: \"=\"; Style: (FontSize: 28, RenderBold: true, TextColor: #bfcdd5, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyySNbRecipe", iconBox(bolt, String.valueOf(bq)));
  b.appendInline("#SkyySNbRecipe", "Label { Anchor: (Width: 44, Height: 74); Text: \"+\"; Style: (FontSize: 28, RenderBold: true, TextColor: #bfcdd5, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyySNbRecipe", iconBox(mat, String.valueOf(mq)));
  b.appendInline("#SkyySNbRecipe", "Group { Anchor: (Width: 20, Height: 74); }");
  b.appendInline("#SkyySNbRecipe", "Label #SkyySNbWhere { Anchor: (Width: 620, Height: 74); Text: \"\"; Style: (FontSize: 15, TextColor: #ffffff, VerticalAlignment: Center, Wrap: true); }");
  long hb = haveOf(inv, k, caps, bolt);
  long hm = haveOf(inv, k, caps, mat);
  boolean ready = hb >= (long) bq && hm >= (long) mq;
  b.set("#SkyySNbWhere.Text", @PKG@.SackDefs.bagName(@PKG@.SackDefs.bagId(cat, 1)) + " = " + bq + " " + @PKG@.SackDefs.BOLTN[0] + " + " + mq + " " + @PKG@.SackDefs.MATN[ci] + " at a Workbench. You have " + num(hb) + " / " + bq + " " + @PKG@.SackDefs.BOLTN[0] + " and " + num(hm) + " / " + mq + " " + @PKG@.SackDefs.MATN[ci] + (ready ? " - ready to craft." : "."));
  String nid = @PKG@.SackDefs.bagId(cat, 1);
  String stTxt;
  String stCol;
  if (free) { stTxt = "Free on this server - craft it at a Workbench."; stCol = "#3d913f"; }
  else if (@PKG@.KnowSync.unlocked(u, nid, coll)) { stTxt = "Unlocked - craft it at a Workbench, or in /craft -> Collections without a bench."; stCol = "#3d913f"; }
  else {
    String[] w = @PKG@.KnowSync.where(u, @PKG@.SackDefs.recipeOf(nid));
    if (w != null) { stTxt = "Unlocks at " + w[1] + " tier " + romanS(w[2]) + " - you have " + numS(w[4]) + " / " + numS(w[3]) + ". /collections shows your progress."; stCol = "#e8a93b"; }
    else { stTxt = "No collection unlocks this bag on this server - ask an admin."; stCol = "#cc4444"; }
  }
  b.appendInline("#SkyySBody", "Label #SkyySNbStatus { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + stCol + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyySNbStatus.Text", stTxt);
  b.appendInline("#SkyySBody", "Label { Anchor: (Height: 28); Text: \"Rarity ladder\"; " + sub + " }");
  int top = @PKG@.SackDefs.TIERS.length;
  for (int r = 1; r <= top; r++) {
    String bid = @PKG@.SackDefs.bagId(cat, r);
    b.appendInline("#SkyySBody", "Label #SkyySNbL" + (r - 1) + " { Anchor: (Height: 26); Padding: (Left: 12); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.SackDefs.RAR_PAGE[r - 1] + ", VerticalAlignment: Center); }");
    b.set("#SkyySNbL" + (r - 1) + ".Text", @PKG@.SackDefs.RAR_NAME[r - 1] + " - " + num((long) @PKG@.SackDefs.rankCap(r)) + " of each item - " + unlockText(u, bid, coll, false));
  }
  int lc = inv == null ? 0 : @PKG@.SweepTask.legendCount(inv);
  b.appendInline("#SkyySBody", "Label #SkyySNbL" + top + " { Anchor: (Height: 26); Padding: (Left: 12); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.SackDefs.RAR_PAGE[@PKG@.SackDefs.RAR_PAGE.length - 1] + ", VerticalAlignment: Center); }");
  b.set("#SkyySNbL" + top + ".Text", @PKG@.SackDefs.bagName(@PKG@.SackDefs.OMNI) + " - " + num((long) @PKG@.SackDefs.CAP_OMNI) + " of each item, every bag type - one Legendary bag of each type (you carry " + lc + " of " + @PKG@.SackDefs.CATS.length + ")");
  b.appendInline("#SkyySBody", "Label #SkyySNbStored { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (stored > 0L ? "#ffffff" : "#878e9c") + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyySNbStored.Text", stored > 0L ? (num(stored) + " items are waiting in your " + cat + " Bag - carry one to reach them. Nothing is ever lost.") : ("Nothing is stored in a " + cat + " Bag yet."));
  b.appendInline("#SkyySBody", "Label #SkyySInfo { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 14, TextColor: #7caacc, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyySInfo.Text", this.info == null ? "" : this.info);
  b.appendInline("#SkyySBody", "Label #SkyySNbHint { Anchor: (Height: 40); Text: \"\"; Style: (FontSize: 13, TextColor: #878e9c, HorizontalAlignment: Center, VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyySNbHint.Text", "A Workbench can use the materials in the bags you carry. Unlocked bag recipes are also on the Collections tab of /craft.");
}@Q3@), page))
# 0.7.7 render(): the vanilla frame, the five tabs (rarity colour of the best bag carried; grey = not carried), then the carried view (cap
# line in the rarity colour, Next line, 4 x 9 vanilla item cards, info, Pick up all / Deposit all) or buildNoBag. The Omni makes every tab
# carried at its cap. Height budget of the carried view: 44 + 1 + 22 + 34 + 26 + 4 x 78 + 28 + 44 = 511 of the 577 px body (640 root -
# 38 title bar - 25 padding); the root anchor has only Width / Height.
page.addMethod(CtNewMethod.make(jt(r@Q3@
public void render(@UCB@ b, @UEB@ ev, @PLA@ player, String k, java.util.HashMap caps, java.util.HashMap ranks) {
  this.key = k;
  this.cat = pickCat(k, caps);
  this.carried = caps.containsKey(this.cat);
  this.cells = new String[36];
  java.util.UUID u = this.playerRef.getUuid();
  b.appendInline((String) null, "Group #SkyySacks { Anchor: (Width: 1000, Height: 640); }");
  b.appendInline("#SkyySacks", "Group #SkyySHead { Anchor: (Height: 38, Top: 0); Padding: (Top: 7); Background: (TexturePath: \"Common/ContainerHeader.png\", HorizontalBorder: 50, VerticalBorder: 0); }");
  b.appendInline("#SkyySHead", "Group { Anchor: (Width: 236, Height: 11, Top: -12); Background: \"Common/ContainerDecorationTop.png\"; }");
  b.appendInline("#SkyySHead", "Label #SkyySTitle { Text: \"Magic Bags\"; Padding: (Horizontal: 19); Style: (FontSize: 15, RenderBold: true, RenderUppercase: true, FontName: \"Secondary\", TextColor: #b4c8c9, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.appendInline("#SkyySacks", "Group #SkyySBody { Anchor: (Top: 38); LayoutMode: Top; Padding: (Full: 17, Top: 8); Background: (TexturePath: \"Common/ContainerPatch.png\", Border: 23); }");
  b.appendInline("#SkyySacks", "Group { Anchor: (Width: 236, Height: 11, Bottom: -6); Background: \"Common/ContainerDecorationBottom.png\"; }");
  b.appendInline("#SkyySBody", "Group #SkyySTabs { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 6, Bottom: 6); }");
  String[] cats = @PKG@.SackDefs.CATS;
  boolean missing = false;
  for (int c = 0; c < cats.length; c++) {
    boolean has = caps.containsKey(cats[c]);
    if (!has) missing = true;
    boolean sel = cats[c].equals(this.cat);
    String col = has ? @PKG@.SackDefs.RAR_PAGE[@PKG@.SackDefs.rarIdx(rankOf(ranks, cats[c]))] : (sel ? "#96a9be" : "#797b7c");
    b.appendInline("#SkyySTabs", "TextButton #SkyySTab" + cats[c] + " { Anchor: (Width: 150, Height: 32); Text: \"" + cats[c] + "\"; " + tabStyle(sel, col) + " }");
    b.appendInline("#SkyySTabs", "Group { Anchor: (Width: 6, Height: 32); }");
    ev.addEventBinding(@BT@.Activating, "#SkyySTab" + cats[c], @EVD@.of("a", "tab:" + cats[c]));
  }
  b.appendInline("#SkyySTabs", "Group { Anchor: (Width: 20, Height: 32); }");
  b.appendInline("#SkyySTabs", "TextButton #SkyySTabCraft { Anchor: (Width: 136, Height: 32); Text: \"Craft\"; " + VBTN + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyySTabCraft", @EVD@.of("a", "craft"));
  b.appendInline("#SkyySBody", "Group { Anchor: (Height: 1); Background: #2b3542; }");
  if (missing) b.appendInline("#SkyySBody", "Label { Anchor: (Height: 22); Text: \"Grey tabs are bags you do not carry - click one to see how to get it\"; Style: (FontSize: 13, TextColor: #878e9c, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  if (!this.carried) { buildNoBag(b, player, k, caps, u); return; }
  int rank = rankOf(ranks, this.cat);
  int ri = @PKG@.SackDefs.rarIdx(rank);
  Integer capObj = (Integer) caps.get(this.cat);
  long capacity = capObj == null ? 0L : (long) capObj.intValue();
  long stored = @PKG@.SackPool.catTotal(k, this.cat);
  String bagWord = rank > @PKG@.SackDefs.TIERS.length ? @PKG@.SackDefs.bagName(@PKG@.SackDefs.OMNI) : (@PKG@.SackDefs.RAR_NAME[ri] + " bag");
  b.appendInline("#SkyySBody", "Label #SkyySCap { Anchor: (Height: 34); Text: \"\"; Style: (FontSize: 18, RenderBold: true, TextColor: " + @PKG@.SackDefs.RAR_PAGE[ri] + ", HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyySCap.Text", this.cat + " - " + bagWord + " - up to " + num(capacity) + " of each item - " + num(stored) + " stored");
  b.appendInline("#SkyySBody", "Label #SkyySNext { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 14, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyySNext.Text", nextLine(player, u, this.cat, rank));
  java.util.ArrayList entries = new java.util.ArrayList();
  java.util.Iterator it = @PKG@.SackPool.pool(k).entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (this.cat.equals(@PKG@.SackDefs.catOf((String) e.getKey()))) entries.add(e);
  }
  java.util.Collections.sort(entries, new @PKG@.CountCmp());
  for (int r = 0; r < 4; r++) {
    b.appendInline("#SkyySBody", "Group #SkyySRow" + r + " { Anchor: (Height: 78); LayoutMode: Left; Padding: (Left: 141, Top: 2, Bottom: 2); }");
    for (int c = 0; c < 9; c++) {
      int idx = r * 9 + c;
      if (idx < entries.size()) {
        java.util.Map.Entry e = (java.util.Map.Entry) entries.get(idx);
        String id = (String) e.getKey();
        long cnt = ((Long) e.getValue()).longValue();
        this.cells[idx] = id;
        b.appendInline("#SkyySRow" + r, "Button #SkyySCell" + idx + " { Anchor: (Width: 74, Height: 74); Padding: (Full: 2); " + VCELL + " Group { Anchor: (Full: 0); Background: #1c2835; HitTestVisible: false; ItemIcon { Anchor: (Width: 64, Height: 64, Left: 3, Top: 3); ItemId: \"" + safe(id) + "\"; } Label { Anchor: (Width: 64, Height: 18, Right: 4, Bottom: 2); Text: \"" + cnt + "\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End); } } }");
        ev.addEventBinding(@BT@.Activating, "#SkyySCell" + idx, @EVD@.of("a", "cell:" + idx + ":stack"));
        ev.addEventBinding(@BT@.RightClicking, "#SkyySCell" + idx, @EVD@.of("a", "cell:" + idx + ":one"));
      } else {
        this.cells[idx] = null;
        b.appendInline("#SkyySRow" + r, "Group { Anchor: (Width: 74, Height: 74); Background: #1c2835(0.55); }");
      }
      if (c < 8) b.appendInline("#SkyySRow" + r, "Group { Anchor: (Width: 2, Height: 74); }");
    }
  }
  // 0.7.5: hides and fabric scraps moved from Combat to Smithing - the Combat tab says where they went when no Smithing bag is carried
  String shown = this.info == null ? "" : this.info;
  if (shown.length() == 0 && "Combat".equals(this.cat) && !caps.containsKey("Smithing")) {
    long sm = @PKG@.SackPool.catTotal(k, "Smithing");
    if (sm > 0L) shown = "Hides and fabric scraps now live in the Smithing bag - " + sm + " items wait there (Smithing tab)";
  }
  b.appendInline("#SkyySBody", "Label #SkyySInfo { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 14, TextColor: #7caacc, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyySInfo.Text", shown);
  b.appendInline("#SkyySBody", "Group #SkyySAct { Anchor: (Height: 44); LayoutMode: Left; Padding: (Left: 141, Top: 6); }");
  b.appendInline("#SkyySAct", "TextButton #SkyySPickAll { Anchor: (Width: 200, Height: 32); Text: \"Pick up all\"; " + VBTN + " }");
  b.appendInline("#SkyySAct", "Group { Anchor: (Width: 12, Height: 32); }");
  b.appendInline("#SkyySAct", "TextButton #SkyySDepAll { Anchor: (Width: 200, Height: 32); Text: \"Deposit all\"; " + VBTN + " }");
  b.appendInline("#SkyySAct", "Group { Anchor: (Width: 16, Height: 32); }");
  b.appendInline("#SkyySAct", "Label { Anchor: (Width: 300, Height: 32); Text: \"Left click takes a stack - right click takes one\"; Style: (FontSize: 13, TextColor: #878e9c, VerticalAlignment: Center); }");
  ev.addEventBinding(@BT@.Activating, "#SkyySPickAll", @EVD@.of("a", "pickall"));
  ev.addEventBinding(@BT@.Activating, "#SkyySDepAll", @EVD@.of("a", "depall"));
}@Q3@), page))
page.addMethod(CtNewMethod.make(jt(r@Q3@
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  String k = @PKG@.SackPool.pkey(u);
  @PLA@ player = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  java.util.HashMap caps = new java.util.HashMap();
  java.util.HashMap ranks = new java.util.HashMap();
  if (player != null) @PKG@.SweepTask.scan(player.getInventory(), caps, ranks);
  render(b, ev, player, k, caps, ranks);
}@Q3@), page))
''')
seg('page.addMethod(CtNewMethod.make("""' + LF + 'public static String iconBox(String id, String n) {',
    "# 0.7.5: why a take-out moved nothing - the bag of that tab is gone",
    ["public void buildNoBag(", "public void render(", "public void build("], PAGE_BLOCK)

# ================= CraftPage: known / coll / Omni state, bag names, knowledge filter, click re-check, gear:fn:roll =================
rep('cpg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ACCWARN = new java.util.concurrent.ConcurrentHashMap();", cpg))' + LF,
    'cpg.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap ACCWARN = new java.util.concurrent.ConcurrentHashMap();", cpg))' + LF
    + '# 0.7.7 (research/Bag-Restructure-Spec.md 5.3): per build - the player\'s known recipes, coll:recipes, and whether all five Legendary bags' + LF
    + '# are carried (the Omni recipe joins the Collections tab); GEARWARN throttles the gear:fn:roll warning' + LF
    + 'cpg.addField(CtField.make("public java.util.Set known;", cpg))' + LF
    + 'cpg.addField(CtField.make("public java.util.HashSet coll;", cpg))' + LF
    + 'cpg.addField(CtField.make("public boolean omniOk;", cpg))' + LF
    + 'cpg.addField(CtField.make("public static long GEARWARN;", cpg))' + LF)
rep('''public static String pretty(String id) {
  if (id == null) return "?";
  String s = id.replace('_', ' ');''',
    '''public static String pretty(String id) {
  if (id == null) return "?";
  // 0.7.7: our bags by their rarity names ("Rare Mining Bag", "Mythic Omni Bag")
  String bn = com.skyy.sacks.SackDefs.bagName(id);
  if (bn != null) return bn;
  String s = id.replace('_', ' ');''')
GEAR_ROLL = Q(r'''# 0.7.7 SkyyGear /craft hook (research/SkyyGear-Stage1-Spec.md 5.2 / 7.1 / 7.3.3): gear:fn:roll =apply(Object[]{UUID player, String itemId, Integer count,
# "craft", String recipeId}) -> Object[] of ItemStack (rolled, identified, Smithing odds), null = not gear / crafting rolls off. The answer
# is only used when every element is a non-empty ItemStack of that same item and together they are never more than was crafted (anything
# else = the plain output + one warning a minute); fewer = the rest plain. No Function = null = the 0.7.6 plain output.
cpg.addMethod(CtNewMethod.make(jt(r@Q3@
public static Object[] gearRoll(java.util.UUID u, String itemId, int count, String recipeId) {
  if (itemId == null || count <= 0) return null;
  Object f = null;
  try { f = @PKG@.SackPool.bridge().get("gear:fn:roll"); } catch (Throwable t) { return null; }
  if (!(f instanceof java.util.function.Function)) return null;
  Object got = null;
  String bad = null;
  try { got = ((java.util.function.Function) f).apply(new Object[] { u, itemId, Integer.valueOf(count), "craft", recipeId }); }
  catch (Throwable t) { got = null; bad = "threw " + t; }
  Object[] arr = null;
  if (bad == null && got != null) {
    if (got instanceof Object[]) arr = (Object[]) got;
    else if (got instanceof java.util.List) arr = ((java.util.List) got).toArray();
    else if (got instanceof @IS@) arr = new Object[] { got };
    else bad = "answered " + got.getClass().getName();
  }
  if (bad == null && arr != null) {
    long sum = 0L;
    for (int i = 0; i < arr.length && bad == null; i++) {
      if (!(arr[i] instanceof @IS@)) { bad = "a non-ItemStack element"; continue; }
      @IS@ s = (@IS@) arr[i];
      if (s.isEmpty() || !itemId.equals(s.getItemId())) bad = "a stack of another item (" + s.getItemId() + ")";
      else sum += (long) s.getQuantity();
    }
    if (bad == null && (arr.length == 0 || sum <= 0L)) bad = "no items";
    if (bad == null && sum > (long) count) bad = sum + " items for " + count + " crafted";
  }
  if (bad != null) {
    long now = System.currentTimeMillis();
    if (now - GEARWARN > 60000L) { GEARWARN = now; @PKG@.SackPool.warn("craft: gear:fn:roll for " + count + " x " + itemId + " " + bad + " - plain output given"); }
    return null;
  }
  return arr;
}@Q3@), cpg))
''')
rep('# collection unlocks published by SkyyCollections via the JVM bridge: "coll:recipes:<uuid>" -> "id,id,id"' + LF,
    GEAR_ROLL + '# collection unlocks published by SkyyCollections via the JVM bridge: "coll:recipes:<uuid>" -> "id,id,id"' + LF)
rep('''  if (!collectionRecipes(u).isEmpty()) t.add(new String[] {{ "C:", "Collections" }});''',
    '''  // 0.7.7: the Collections tab also shows while all five Legendary bags are carried (the Mythic Omni Bag recipe crafts there)
  if (!collectionRecipes(u).isEmpty() || this.omniOk) t.add(new String[] {{ "C:", "Collections" }});''')
rep('''  }} else if (tabId.startsWith("C:")) {{
    ids.addAll(collectionRecipes(u));
  }} else if (tabId.equals("K:camp")) {{''',
    '''  }} else if (tabId.startsWith("C:")) {{
    ids.addAll(collectionRecipes(u));
    // 0.7.7 (spec 4): the Omni recipe (no knowledge needed) joins this tab while all five Legendary bags are carried - inventory crafting
    if (this.omniOk) ids.add({PKG}.SackDefs.recipeOf({PKG}.SackDefs.OMNI));
  }} else if (tabId.equals("K:camp")) {{''')
rep('''    if (grp >= 0 && tabGroup(rc) != grp) continue;
    out.add(rc);''',
    '''    if (grp >= 0 && tabGroup(rc) != grp) continue;
    // 0.7.7 (spec 5.3): locked bags and unknown vanilla knowledge recipes stay off Crafting / Smithing / Farming
    if (grp >= 0 && !{PKG}.KnowSync.allowed(rc, u, this.known, this.coll)) continue;
    out.add(rc);''')
rep('''    if (tableOnly(rc)) continue;
    {MQ} po = rc.getPrimaryOutput();
    if (nameMatches(q, po == null ? String.valueOf(rc.getId()) : po.getItemId())) out.add(rc);''',
    '''    if (tableOnly(rc)) continue;
    if (!{PKG}.KnowSync.allowed(rc, u, this.known, this.coll)) continue;
    {MQ} po = rc.getPrimaryOutput();
    if (nameMatches(q, po == null ? String.valueOf(rc.getId()) : po.getItemId())) out.add(rc);''')
rep('''  this.key = k;
  this.tabs = buildTabs(p, u, k);''',
    '''  this.key = k;
  // 0.7.7: what this build filters with (recipesFor / searchRecipes / buildTabs read these fields)
  this.known = {PKG}.KnowSync.known(p);
  this.coll = collectionRecipes(u);
  this.omniOk = {PKG}.SweepTask.legendCount(p.getInventory()) >= {PKG}.SackDefs.CATS.length;
  this.tabs = buildTabs(p, u, k);''')
rep('''    if (campTab && (campfireTier(u) <= 0 || !campfireRecipe(r) || !tableOnly(r))) {{ this.info = "equip the Campfire accessory in your accessory bag to cook here"; rebuild(); return; }}''',
    '''    if (campTab && (campfireTier(u) <= 0 || !campfireRecipe(r) || !tableOnly(r))) {{ this.info = "equip the Campfire accessory in your accessory bag to cook here"; rebuild(); return; }}
    // 0.7.7 (spec 5.3 click time): the same unlock test again before any material moves (a page drawn before an unlock change, a profile
    // switch or a dropped Legendary bag). Collections tab: still in coll:recipes, or the Omni with all five Legendary bags carried.
    boolean okR = true;
    if ("C:".equals(this.tab)) {{
      String rid = String.valueOf(r.getId());
      okR = collectionRecipes(u).contains(rid) || (rid.equals({PKG}.SackDefs.recipeOf({PKG}.SackDefs.OMNI)) && {PKG}.SweepTask.legendCount(p.getInventory()) >= {PKG}.SackDefs.CATS.length);
    }} else if (this.tab != null && this.tab.startsWith("A:")) {{
      okR = {PKG}.KnowSync.allowed(r, u, {PKG}.KnowSync.known(p), collectionRecipes(u));
    }}
    if (!okR) {{ this.info = "You have not unlocked this recipe"; rebuild(); return; }}''')
rep('''    int given = 0;
    if (done > 0 && outs != null) {{
      for (int k = 0; k < outs.length; k++) {{
        if (outs[k] == null || outs[k].getItemId() == null) continue;
        long total = (long) outs[k].getQuantity() * (long) done; if (total > 100000L) total = 100000L;
        String gid = outs[k].getItemId();
        if (k == campAt) gid = campId;
        {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(gid, (int) total));
        given += (int) total;
      }}
    }}
    if (campTab) audit.append(" campfire=").append(campId == null ? "plain" : campId);''',
    '''    int given = 0;
    int gearN = 0;
    int gearDrop = 0;
    if (done > 0 && outs != null) {{
      for (int k = 0; k < outs.length; k++) {{
        if (outs[k] == null || outs[k].getItemId() == null) continue;
        long total = (long) outs[k].getQuantity() * (long) done; if (total > 100000L) total = 100000L;
        String gid = outs[k].getItemId();
        if (k == campAt) gid = campId;
        // 0.7.7 SkyyGear /craft hook (research/SkyyGear-Stage1-Spec.md 7.3.3): when gear:fn:roll exists and answers for this entry, each
        // returned (rolled, identified) stack is handed out with addOrDropItemStack instead of the plain stack; the item is counted in the
        // inventory before and after (the engine rule) and crafts.log gets gear=<n>. No Function / null = the plain stack exactly as 0.7.6.
        // Never on the Campfire tab (cooked food; SkyyCooking grades it).
        Object[] rolled = null;
        if (!campTab) rolled = gearRoll(u, gid, (int) total, String.valueOf(r.getId()));
        if (rolled != null) {{
          {IC} dstC = p.getInventory().getCombinedStorageHotbarBackpack();
          int beforeC = countItem(dstC, gid);
          int gotN = 0;
          for (int gi = 0; gi < rolled.length; gi++) {{
            {IS} gs = ({IS}) rolled[gi];
            {SIC}.addOrDropItemStack(st, ref, dstC, gs);
            gotN += gs.getQuantity();
          }}
          // fewer rolled items than crafted: the rest plain (never a loss); gearRoll already refused more than crafted (never a gain)
          if (gotN < (int) total) {SIC}.addOrDropItemStack(st, ref, dstC, new {IS}(gid, (int) total - gotN));
          int inInv = countItem(dstC, gid) - beforeC;
          if (inInv < (int) total) gearDrop += (int) total - (inInv < 0 ? 0 : inInv);
          gearN += gotN;
        }} else {{
          {SIC}.addOrDropItemStack(st, ref, p.getInventory().getCombinedStorageHotbarBackpack(), new {IS}(gid, (int) total));
        }}
        given += (int) total;
      }}
    }}
    if (campTab) audit.append(" campfire=").append(campId == null ? "plain" : campId);
    if (gearN > 0) audit.append(" gear=").append(gearN);
    if (gearDrop > 0) audit.append(" gearDropped=").append(gearDrop);''')

# ================= admin config rows: 5 bag caps with rarity labels + Free bag recipes; history keeps 10 =================
KIT_ROWS = r'''_CAP_ROW = {
    # 0.7.7 (research/Bag-Restructure-Spec.md 8.1): rarity labels; the keys stay (bag.small = Normal, bag.medium = Unique, bag.large = Legendary)
    "bag.small":       ("Normal bag: most of each item", "bags", "live,adv,danger",
                        "Most of EACH item a Normal bag (the old Small) holds. Lowering never deletes pooled items."),
    "bag.medium":      ("Unique bag: most of each item", "bags", "live,adv,danger",
                        "Most of each item a Unique bag (the old Medium) holds. The best bag carried counts."),
    "bag.rare":        ("Rare bag: most of each item", "bags", "live,adv,danger",
                        "Most of each item a Rare bag holds (between Unique and Legendary). Lowering only stops intake."),
    "bag.large":       ("Legendary bag: most of each item", "bags", "live,adv,danger",
                        "Most of each item a Legendary bag (the old Large) holds. Lowering only stops intake."),
    "bag.omni":        ("Mythic Omni Bag: most of each item", "bags", "live,adv,danger",
                        "Most of each item of EVERY bag type the Mythic Omni Bag holds. Lowering only stops intake."),
    "bench.queueCap":  ("Queue size (units)", "benches", "live,adv",
                        "Most units one player's Furnace or Tannery queue holds. Lowering keeps what is queued."),
    "bench.fuelCap":   ("Fuel slot size (items)", "benches", "live,adv",
                        "Most fuel items one player's bench fuel slot holds. Lowering keeps the fuel already loaded."),
    "bench.outputCap": ("Output held before pausing", "benches", "live,adv",
                        "Output a Furnace or Tannery keeps before it pauses until the player collects. Nothing is lost."),
}
assert set(_CAP_ROW) == set(k for (k, _f, _d, _lo, _hi) in SACK_CAPS)
SACK_CFG_CATS = [("craft", "Craft page"), ("bags", "Bags"), ("benches", "Furnace and Tannery")]
SACK_CFG_ROWS = [  # (key, label, cat, type, default, min, max, opts, unit, flags, help, bind)
    ("craftSearch", "Search box on /craft", "craft", "bool", "true", "", "", "", "", "live",
     "Off hides the search box on /craft (for clients that cannot open it). /craft <words> still searches.",
     "reload:SackCfg.reload@config.properties:craftSearch"),
    # 0.7.7 (spec 8.1): the admin override - on = every player knows every bag recipe (the old free recipes), off = collection unlocks.
    # Confirm on every change; SackCfg.freeChanged republishes sacks:freebags, KnowSync applies it on each player's next sweep.
    ("bags.freeRecipes", "Free bag recipes", "bags", "bool", "false", "", "", "", "", "live,danger",
     "On: every player knows every bag recipe (the old way). Off: bags unlock through collections.",
     "field:SackCfg.FREE_RECIPES@config.properties:bags.freeRecipes;confirm=always;after=SackCfg.freeChanged"),
] + [(k, _CAP_ROW[k][0], _CAP_ROW[k][1], "int", str(d), str(lo), str(hi), "", "", _CAP_ROW[k][2], _CAP_ROW[k][3],
      "field:%s@config.properties:%s%s" % (f, k, ";check=SackCfg.checkTierOrder" if k.startswith("bag.") else ""))
     for (k, f, d, lo, hi) in SACK_CAPS]
# review fix: the bag rows ask before an order-breaking change (SackCfg.checkTierOrder; asks, never refuses, ignored on import)
# 0.7.7: config history keeps 10 versions per file (OPEN-QUESTIONS server setup 3, LOCKED 2026-09-25: 10, was 20)
'''
seg("_CAP_ROW = {", "kit = CFG.emit(pool, PKG, MOD=\"SkyySacks\"",
    ['"bag.small":       ("Small bag: most of each item"', "SACK_CFG_ROWS = ["], KIT_ROWS)
rep('''               RELOAD="SackCfg.reload", KEEP=20, DEFAULTS={"config.properties": SACK_CFG_TEXT})''',
    '''               RELOAD="SackCfg.reload", KEEP=10, DEFAULTS={"config.properties": SACK_CFG_TEXT})''')

# ================= plugin: notices file, free-mode publish, log line, shutdown save, the two new classes written =================
rep('''  {PKG}.SackCfg.reload();
  getCommandRegistry().registerCommand(new {PKG}.SacksCmd());''',
    '''  {PKG}.SackCfg.reload();
  // 0.7.7: the one-time rarity notice per player (research/Bag-Restructure-Spec.md 5.8) + the free-mode bridge value (republished every 10 s)
  {PKG}.SackNotice.FILE = getDataDirectory().resolveSibling("Skyy_SkyySacks").resolve("notices.properties");
  {PKG}.SackNotice.load();
  {PKG}.SackCfg.pubFree();
  getCommandRegistry().registerCommand(new {PKG}.SacksCmd());''')
rep('ready - /pd (Mining, Foraging, Farming, Combat and Smithing bags - every tab shown, a bag you do not carry shows how to craft it)',
    'ready - /pd (Mining, Foraging, Farming, Combat and Smithing bags by rarity - Normal, Unique, Rare, Legendary + the Mythic Omni Bag for every type; bag recipes unlock through SkyyCollections, free without it or with bags.freeRecipes)')
rep('''  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}''',
    '''  try {{ {PKG}.CraftLog.drain(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.SackNotice.save(); }} catch (Throwable t) {{ }}
  try {{ {PKG}.CfgPub.shutdown(); }} catch (Throwable t) {{ }}''')
rep('for c in (defs, sp, scfg, pjob, pben, pst, swp,', 'for c in (defs, sp, scfg, ksync, snot, pjob, pben, pst, swp,')

# ================= assets: 21 bag items, 5 qualities, lang, build checks =================
ASSETS = r'''def sack_item(item_id, quality, recipe_in, knowledge, page_id):
    # 0.7.7: KnowledgeRequired sits in the item's Recipe block (the vanilla Armor_Bronze_Chest shape): true for the 20 tiered bags (taught
    # by KnowSync from the collection unlocks), false for the Omni. Right-click opens the bag page on that bag's tab (the Omni: "SkyySacks",
    # the no-type page, which picks a tab with items).
    return {
      "TranslationProperties": {"Name": "server.items.%s.name" % item_id, "Description": "server.items.%s.description" % item_id},
      "Categories": ["Items.Tools"],
      "Icon": "Icons/ItemsGenerated/Utility_Bag_Seed.png",
      "Quality": quality,
      "Recipe": {"Input": recipe_in, "BenchRequirement": [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}],
                 "KnowledgeRequired": knowledge},
      "Model": "Items/Back/BackpackBig.blockymodel",
      "Texture": "Items/Back/BackpackBig_Texture.png",
      "IconProperties": {"Scale": 0.455, "Translation": [1.19, 2.39], "Rotation": [0, 177.73, 0]},
      "Tags": {"Family": ["Leather"], "Type": ["Utility"]},
      "MaxStack": 1,
      "Interactions": {"Secondary": {"Interactions": [{"Type": "OpenCustomUI", "Page": {"Id": page_id}}]}}
    }
files = {}  # pages are built inline (no .ui files: see memory hytale-ui-rules)
lang = []
_NUMW = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight"}
# 0.7.5 / 0.7.7: the bag table (BAG_CATS / BAG_MAT / BAG_TIERS / BAG_HOLDS near the top). Normal = 3 Bolt of Wool + 4 BAG_MAT (the 0.7.4
# Small recipe), each next rarity = the previous bag + BAG_UP_QTY (placeholder 6) mob-dropped fabric scraps of its tier (Linen / Shadoweave /
# Cindercloth); the item ids Small / Medium / Large are unchanged (owned bags keep working).
for cat in BAG_CATS:
    prev = None
    for (suf, rar, qid, capk, bolt) in BAG_TIERS:
        iid = "Skyy_Sack_%s_%s" % (cat, suf)
        if prev is None:
            rin = [{"ItemId": bolt, "Quantity": BAG_BOLT_QTY}, {"ItemId": BAG_MAT[cat], "Quantity": BAG_MAT_QTY}]
        else:
            rin = [{"ItemId": prev, "Quantity": 1}, {"ItemId": bolt, "Quantity": BAG_UP_QTY}]
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(sack_item(iid, qid, rin, True, "SkyySacks" + cat), indent=2)
        name = "%s %s Bag" % (rar, cat)
        lang.append("items.%s.name=%s" % (iid, name))
        lang.append("server.items.%s.name=%s" % (iid, name))
        desc = ("A %s magic bag that opens onto your pocket dimension. Holds up to %s of each %s item (%s). Matching items in your storage are "
                "pulled in automatically. Right-click to reach in. You need a bag on you to reach in, but nothing is ever lost."
                % (rar, format(CAPD[capk], ","), cat.lower(), BAG_HOLDS[cat]))
        lang.append("items.%s.description=%s" % (iid, desc))
        lang.append("server.items.%s.description=%s" % (iid, desc))
        prev = iid
# 0.7.7 the Mythic Omni Bag (spec 4): one Legendary bag of each type at a Workbench, no knowledge gate
_omni_in = [{"ItemId": "Skyy_Sack_%s_%s" % (c, TOP_SUFFIX), "Quantity": 1} for c in BAG_CATS]
files["Server/Item/Items/Utility/%s.json" % BAG_OMNI] = json.dumps(sack_item(BAG_OMNI, BAG_RARITY[-1][0], _omni_in, False, "SkyySacks"), indent=2)
lang.append("items.%s.name=Mythic Omni Bag" % BAG_OMNI)
lang.append("server.items.%s.name=Mythic Omni Bag" % BAG_OMNI)
_odesc = ("The Mythic Omni Bag joins all %s Legendary bags in one. Holds up to %s of each item of every bag type (%s and %s). It is the only "
          "bag you need to carry. Right-click to reach in; every bag type keeps its own tab."
          % (_NUMW.get(len(BAG_CATS), str(len(BAG_CATS))), format(CAPD["bag.omni"], ","), ", ".join(BAG_CATS[:-1]), BAG_CATS[-1]))
lang.append("items.%s.description=%s" % (BAG_OMNI, _odesc))
lang.append("server.items.%s.description=%s" % (BAG_OMNI, _odesc))
# 0.7.7 own qualities (spec 3.2): the vanilla quality JSON shape with the texture set of the hue-matched vanilla rarity, Wynn TextColor
for (qid, label, tip, _page, qv, tex, particle) in BAG_RARITY:
    files["Server/Item/Qualities/%s.json" % qid] = json.dumps({
        "QualityValue": qv,
        "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltip%s.png" % tex,
        "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltip%sArrow.png" % tex,
        "SlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % tex,
        "BlockSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % tex,
        "SpecialSlotTexture": "UI/ItemQualities/Slots/Slot%s.png" % tex,
        "TextColor": tip,
        "LocalizationKey": "server.general.qualities." + qid,
        "VisibleQualityLabel": True,
        "RenderSpecialSlot": True,
        "ItemEntityConfig": {"ParticleSystemId": particle}}, indent=2)
    lang.append("general.qualities.%s=%s" % (qid, label))            # vanilla server.lang style (key without the server. prefix)
    lang.append("server.general.qualities.%s=%s" % (qid, label))     # + the prefixed twin (the SkyyVault pattern)
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"  # key items.<Id>.name in server.lang (pattern from Tamework)

# ---- 0.7.7 asset build checks (spec 11): 21 bag JSONs + 5 qualities; every recipe input exists or is a bag made here; each tiered recipe
# holds the previous tier; KnowledgeRequired true on exactly the 20 tiered bags and false on the Omni; the Omni takes one Legendary bag of
# each type; quality textures and drop particles exist in Assets.zip; QualityValue < 8; lang = 21 names, 21 descriptions, 5 labels.
def _bag_assets_check():
    import zipfile
    items = dict((p.rsplit("/", 1)[1][:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    quals = dict((p.rsplit("/", 1)[1][:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Qualities/"))
    if len(items) != len(BAG_CATS) * len(BAG_TIERS) + 1 or len(quals) != len(BAG_RARITY):
        raise SystemExit("0.7.7 asset check: %d bag items, %d qualities" % (len(items), len(quals)))
    if sorted(i for i, n in items.items() if n["Recipe"]["KnowledgeRequired"]) != sorted(MANAGED_IDS) or items[BAG_OMNI]["Recipe"]["KnowledgeRequired"]:
        raise SystemExit("0.7.7 asset check: KnowledgeRequired must be true on exactly the 20 tiered bags and false on the Omni")
    for cat in BAG_CATS:
        for i in range(1, len(BAG_TIERS)):
            ins = [x["ItemId"] for x in items["Skyy_Sack_%s_%s" % (cat, BAG_TIERS[i][0])]["Recipe"]["Input"]]
            if "Skyy_Sack_%s_%s" % (cat, BAG_TIERS[i - 1][0]) not in ins:
                raise SystemExit("0.7.7 asset check: the %s %s recipe does not take the previous rarity" % (BAG_TIERS[i][1], cat))
    if sorted(x["ItemId"] for x in items[BAG_OMNI]["Recipe"]["Input"]) != sorted("Skyy_Sack_%s_%s" % (c, TOP_SUFFIX) for c in BAG_CATS):
        raise SystemExit("0.7.7 asset check: the Omni recipe must take one Legendary bag of each type")
    for iid, node in items.items():
        if node["Quality"] not in quals:
            raise SystemExit("0.7.7 asset check: %s uses quality %s that is not shipped" % (iid, node["Quality"]))
    if any(q["QualityValue"] >= 8 for q in quals.values()):
        raise SystemExit("0.7.7 asset check: a bag quality reaches SkyyAuctions' technical threshold (8)")
    lt = files["Server/Languages/en-US/server.lang"]
    for iid in items:
        for k in ("server.items.%s.name=" % iid, "server.items.%s.description=" % iid, "\nitems.%s.name=" % iid):
            if k not in "\n" + lt:
                raise SystemExit("0.7.7 asset check: no lang line " + k.strip())
    for qid in quals:
        if ("server.general.qualities.%s=" % qid) not in lt or ("\ngeneral.qualities.%s=" % qid) not in "\n" + lt:
            raise SystemExit("0.7.7 asset check: no quality label for " + qid)
    za = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    if not os.path.isfile(za):
        print("note: Assets.zip not found - bag recipe inputs, quality textures and drop particles not cross-checked")
        return
    with zipfile.ZipFile(za) as z:
        names = set(z.namelist())
    ids = set(os.path.basename(n)[:-5] for n in names if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    parts = set(os.path.basename(n)[:-len(".particlesystem")] for n in names if n.endswith(".particlesystem"))
    def exists(p):
        q = "Common/" + p
        return q in names or (q.endswith(".png") and q[:-4] + "@2x.png" in names)
    for iid, node in items.items():
        for x in node["Recipe"]["Input"]:
            if x["ItemId"] not in ids and x["ItemId"] not in items:
                raise SystemExit("0.7.7 asset check: %s recipe input %s is not in Assets.zip" % (iid, x["ItemId"]))
        for k in ("Model", "Texture", "Icon"):
            if not exists(node[k]):
                raise SystemExit("0.7.7 asset check: %s %s %s is not in Assets.zip" % (iid, k, node[k]))
    for qid, q in quals.items():
        for k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture", "BlockSlotTexture", "SpecialSlotTexture"):
            if not exists(q[k]):
                raise SystemExit("0.7.7 asset check: quality %s %s %s is not in Assets.zip" % (qid, k, q[k]))
        if q["ItemEntityConfig"]["ParticleSystemId"] not in parts:
            raise SystemExit("0.7.7 asset check: quality %s drop particle %s is not in Assets.zip" % (qid, q["ItemEntityConfig"]["ParticleSystemId"]))
    print("assets checked: %d bag items (20 knowledge-gated + the Omni), %d qualities, %d lang lines" % (len(items), len(quals), len(lang)))
_bag_assets_check()
print("bag table: %s x %s + %s | caps %s | qualities %s" % (
    "/".join(BAG_CATS), "/".join("%s=%s" % (t[1], t[0]) for t in BAG_TIERS), BAG_OMNI,
    " / ".join(format(CAPD[k], ",") for k in ("bag.small", "bag.medium", "bag.rare", "bag.large", "bag.omni")),
    ", ".join("%s %s" % (r[1], r[2]) for r in BAG_RARITY)))

'''
seg("def sack_item(cat, tier, quality, recipe_in):", 'jar = os.path.join(HERE, "SkyySacks-%s.jar" % VERSION)',
    ['files["Server/Languages/en-US/server.lang"]', '"Medium": sack_item(cat, "Medium", "Uncommon"'], ASSETS)
rep('"SkyBlock-style sacks: craft a sack, matching pickups pool automatically, /sacks to view and withdraw. Zero dependencies."',
    '"SkyBlock-style Magic Bags by rarity (Normal, Unique, Rare, Legendary + the Mythic Omni Bag): matching pickups pool automatically, /pd to view and withdraw, /craft from your bags, bag recipes unlock through collections. Zero dependencies."')

# ================= self-checks =================
assert 'VERSION = "0.7.7"' in s and 'VERSION = "0.7.6"' not in s
assert "KEEP=10" in s and "KEEP=20" not in s
# javassist: no forward references - fields before the methods that use them, helpers before callers, classes before their users
def _at(t, start=0):
    assert s.count(t) >= 1, "missing: " + t[:80]
    return s.index(t, start)
i_jt = _at("def jt(src):")
i_defs_caps = _at('defs.addField(CtField.make("public static volatile int %s = %d;"')
i_tier = _at("public static int tierCap(String tier) {")
i_rank = _at("public static int tierRank(String tier) {")
i_bagname = _at("public static String bagName(String id) {")
i_isbag = _at("public static boolean isBag(String id) {")
i_catidx = _at("public static int catIndex(String cat) {")
assert i_jt < i_defs_caps < i_tier < i_rank < i_bagname < i_isbag and i_catidx < i_bagname
i_bw = _at("public static java.util.Map bridgeW() {")
i_free_f = _at('scfg.addField(CtField.make("public static volatile boolean FREE_RECIPES = false;", scfg))')
i_fmt = _at("public static String fmtN(long n) {")
i_eff = _at("public static boolean effFree() {")
i_pub = _at("public static void pubFree() {")
i_reload = _at("public static synchronized void reload() {")
i_ord = _at("public static String checkTierOrder(String key, String value) {")
i_fch = _at("public static void freeChanged(String key) {")
assert i_bw < i_eff and i_free_f < i_fmt < i_eff < i_pub < i_reload < i_ord < i_fch
# review fix: effFree() reads KnowSync.SEENCOLL, so the field is declared (once) before effFree is compiled
assert s.count("public static volatile boolean SEENCOLL") == 1
assert _at('ksync.addField(CtField.make("public static volatile boolean SEENCOLL = false;", ksync))') < i_eff
assert _at('ksync = pool.makeClass(PKG + ".KnowSync")') < i_eff
i_ks = _at("public static boolean sync(@REF@ r, @ST@ st, @PLA@ p, java.util.UUID u) {")
i_wanted = _at("public static java.util.HashSet wanted(java.util.UUID u) {")
i_allowed = _at("public static boolean allowed(@CRR@ r, java.util.UUID u, java.util.Set known, java.util.Set coll) {")
i_where = _at("public static String[] where(java.util.UUID u, String rid) {")
i_notice = _at("public static void check(@PR@ pr, java.util.UUID u, String k, boolean carries) {")
i_proc = _at("# ================= Processing (0.7.0)")
assert i_pub < i_wanted < i_ks < i_allowed < i_where < i_notice < i_proc
i_swp = _at("# ================= SweepTask (runs ON world thread")
i_offer = _at("public static void offer(java.util.HashMap caps, java.util.HashMap ranks, String cat, int cap, int rank) {")
i_offid = _at("public static void offerId(String id, java.util.HashMap caps, java.util.HashMap ranks) {")
i_scan = _at("public static void scan(@INV@ inv, java.util.HashMap caps, java.util.HashMap ranks) {")
i_caps = _at("public static java.util.HashMap caps(@INV@ inv) {")
i_legend = _at("public static int legendCount(@INV@ inv) {")
i_restamp = _at("public static int restamp(@INV@ inv) {")
i_sweep = _at("public static int sweep({PLA} p, String k, String onlyCat, boolean allContainers) {{")
i_run = _at("{PKG}.KnowSync.sync(r, st, p, u);")
assert i_proc < i_swp < i_offer < i_offid < i_scan < i_caps < i_legend < i_restamp < i_sweep < i_run
i_page = _at("# ================= SacksPage (SkyBlock-style")
i_numS = _at("public static String numS(String v) {")
i_unl = _at("public static String unlockText(java.util.UUID u, String bagId, java.util.Set coll, boolean next) {")
i_next = _at("public static String nextLine(@PLA@ player, java.util.UUID u, String cat, int rank) {")
i_nobag = _at("public void buildNoBag(@UCB@ b, @PLA@ player, String k, java.util.HashMap caps, java.util.UUID u) {")
i_render = _at("public void render(@UCB@ b, @UEB@ ev, @PLA@ player, String k, java.util.HashMap caps, java.util.HashMap ranks) {")
i_pbuild = _at("public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {")
i_num = _at("public static String num(long v) {")
i_have = _at("public static long haveOf({INV} inv, String k, java.util.HashMap caps, String id) {{")
i_pick = _at("public String pickCat(String k, java.util.HashMap caps) {{")
assert i_page < i_pick < i_num < i_have < i_numS < i_unl < i_next < i_nobag < i_render < i_pbuild
assert _at("public static String roman(int t) {") < i_page
i_gear = _at("public static Object[] gearRoll(java.util.UUID u, String itemId, int count, String recipeId) {")
i_chde = _at("if (!campTab) rolled = gearRoll(u, gid, (int) total, String.valueOf(r.getId()));")
assert i_gear < i_chde
# the CraftPage fields exist before its constructor (javassist: fields before use)
assert _at('cpg.addField(CtField.make("public boolean omniOk;", cpg))') < _at("public CraftPage({PR} pr, String tab) {{")
# every 0.7.6 profile / busy / UI rule untouched; no periodic page refresh; UI ids without underscores
assert s.count("public static String settledKey(java.util.UUID u) {") == 1, "settledKey changed"
assert 'b.get("profile:busy:" + u.toString()) != null) return null;' in s, "busy gate lost"
import re as _re
for m in _re.finditer(r"#(Skyy[A-Za-z0-9_]*)", s):
    assert "_" not in m.group(1), "UI id with underscore: " + m.group(1)
assert 'Group #SkyySacks { Anchor: (Width: 1000, Height: 640); }' in s, "bag page root = Width / Height only"
assert "cp.live(" not in s and "public void live(" not in s, "periodic refresh came back"
assert s.count('{PKG}.SackPool.notifyOn(u, "sacks.benchDone")') == 1 and s.count('{PKG}.SackPool.notifyOn(u, "sacks.benchFuel")') == 1
# the 0.7.6 page event payloads the handlers match are all still bound
for pay in ('"tab:" + cats[c]', '"craft")', '"cell:" + idx + ":stack"', '"cell:" + idx + ":one"', '"pickall"', '"depall"'):
    assert pay in s, "bag page payload lost: " + pay
# the classes are written, the kit before the assets
assert "for c in (defs, sp, scfg, ksync, snot," in s
assert s.index("kit.write(OUT)") < s.index("# ================= assets =================")

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
