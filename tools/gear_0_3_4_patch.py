"""Derive SkyyGear/build_skyygear_0.3.4.py from the LIVE 0.3.3 (build_skyygear_0.3.3.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_3_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_3_4_patch.py      then      python SkyyGear/build_skyygear_0.3.4.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.4.py

0.3.4 = GATHERING PHASE 4 (research/Gathering-Shards-Spec.md 5.5, 6, 6.2) + THE HOE TILL AREA (RESUME 'Next': "hoe till area by tier").
Skyy's words this round follows (docs/answered/gear.md, word for word):
  2026-10-12 RARITY SIGILS: "and to upgrade the rarity of an item. gems? stones? or runes? (we will make it work on any and all gear that has a
   rarity. and skip tiers. so if you have a common pickaxe, and a legendary upgrade rune, you can just upgrade it to legendary in the /smithing
   menu" + popup "Sigils (Recommended)".
  2026-10-13 G3 "No Mythic Sigil; AH yes, Bazaar never (Recommended)"; docs/log 2026-10-13 ART REVIEW: "Sigils (ship 5: Unique..Mythic; drop
   the Normal one, nothing is below the lowest rarity)" (the later art go-ahead; the Mythic Sigil stays a boss-only drop - question 1).
  2026-10-12 GATHERING ARMOR LEVELS: popup "Yes, like the tools (Recommended)": "level = skill level, capped by tier, tier up on the Upgrade tab
   with Enchanted materials, keep rarity + rolls".
  2026-10-13 G5 "Yes, as proposed (Recommended)" = spec 4.3 "Hoe tier also sets the till area (1 / 3x3 / 3x3 / 5x5 / 5x5 / 7x7 / 7x7 / 9x9 for
   T0-T7, hoe.area)".
  2026-10-14 "Run everything you can in parallel. I want everything on your list done by 5 pm when i get off work."
Built on the LIVE 0.3.3 (the 0.3.0 - 0.3.3 lifelong / gate / lost-tool code is untouched apart from the listed hooks).

1. SIGILS (GearSigil): five items Skyy_Sigil_Unique / _Rare / _Legendary / _Fabled / _Mythic (the approved art: research/cloud/icons-1013,
   64 px icons, our own drawings; the held model = the vanilla Rune Shard model by path with a rarity-tinted copy of the rune texture,
   generated at build time, nothing vanilla committed). On the Anvil tab of /smithing an item with a rarity shows a SIGIL STRIP while you carry
   a Sigil: "<Rarity> Sigil (x2): Unique -> LEGENDARY"; Apply arms, a second click within 10 s spends ONE Sigil and sets the item's rarity to
   the Sigil's (skips tiers; upward only). Its lines stay; the new rarity's extra slots are EMPTY until the next Reforge (Reforge already
   rolls the rarity's full line count - GearRoll.reforge). "Other" picks another Sigil you carry. Works on any identified item with a rarity:
   weapons, armor, tools (a lifelong tool stays lifelong; a /pickaxe replacement with a Sigil counts as "invested" - never thrown away).
   REFUSED: Set / Untiered / Mythic items, quest / boss Set pieces, unidentified items, stacks, a Sigil at or below the item's rarity,
   part.sigils off. WRITE SAFETY = the 0.2.22 Upgrade core's pattern: fingerprint re-check, SIGIL-BEGIN flushed to gear.log, (a) one Sigil
   leaves its slot (storage first; checked), (b) the item's own slot gets the new document (checked); a failure puts both back; counts
   checked after (Sigils -1, item unchanged). MARKET (G3): GearWall (market:veto) refuses a Sigil only when the caller is the Bazaar
   (com.skyy.bazaar) - the Auction House may list / sell them. NPC SHOPS (fixer): com.skyy.merchants is in NOSELL for the day SkyyMerchants
   asks market:veto, but SkyyMerchants 0.1.3 never asks it (its own why(): Skyy_Sack_ / NEVER / mythic-untiered-set) - today a Sigil stays out
   of NPC shops only because no default stock lists one; the Merchants round should add Skyy_Sigil_* to its NEVER default (or ask the veto).
   Row part.sigils (default on).
2. GATHERING ARMOR THAT LEVELS (GearArmLv): the 28 Mining armor pieces (the vanilla metal sets, 0.2.15) follow your Mining level like the
   lifelong tools: level = your Mining level kept inside the piece's tier band (so a piece is never above you once you reach its tier, and a
   higher tier stays inactive until you do); the stamp scan rewrites "[Lv N]" (GearTool.held notices a Mining level-up once a second and
   queues the scan); Reforge "Level up" is refused on them (their level follows the skill). TIER UP on the Anvil (the Upgrade card): new rows
   garmor.ladders = Copper > Iron > Thorium > Cobalt > Adamantite per slot, costs spec 6.1 (Iron / Thorium: Head 1, Chest 2, Legs 2, Hands 1
   Enchanted; Cobalt / Adamantite: 1 / 1 / 1 / 1 - the spec's Hands 0 is made 1, no free step - question 3); needs the Mining level the new
   tier starts at; KEEPS rarity (Set stays Set, its set field moves to the new tier's Mining Set; an old rolled piece keeps rarity + lines).
   Mithril / Onyxium steps wait for their Enchanted items (tools/skyyench.py has none). Foraging / Farming / Fishing armor do not exist yet
   (art pending) - GearArmLv is written per gate skill so they plug in by id later. Rows garmor.levels (on) + garmor.ladders.
3. THE HOE TILLS AN AREA BY TIER (GearTill + GearTillSys): spec 4.3 + G5: your LIFELONG hoe tills a square around the block you till - side
   1 / 3 / 3 / 5 / 5 / 7 / 7 / 9 for Crude .. Onyxium (row hoe.area; vanilla hoes end at Thorium = 5x5). SERVER SIDE, VERIFIED bytecode
   2026-10-14: vanilla Hoe_Till = ChangeBlockInteraction (BlockOperations.setBlock, NO event) then ModifyInventory (held item durability -1 ->
   ItemContainer.setItemStackForSlot -> InventoryChangeEvent). GearTillSys listens to that change on the hotbar / tools section: the same
   lifelong hoe one durability lower + the block you look at (TargetUtil.getTargetBlock) is freshly tilled soil = a till; it then tills the
   tillable blocks (the Hoe_Till Changes map, read from Assets.zip at build time) on the same layer with air above, in loaded sections only
   (BlockOperations.setBlock - the engine's own call). A block hit in the last 300 ms (left click with the hoe = DamageBlockEvent) is no till.
   PROTECTION: island worlds ask SkyyIslands' island:perm:fn "build" (TRUE = till, FALSE = only the vanilla block); any other world (hub, zone
   worlds) = only the vanilla block unless hoe.areaElsewhere is on (default OFF - question 4). No extra durability (question 5). Creative
   (no durability change) = the vanilla single block. Rows hoe.areaOn (on), hoe.area, hoe.areaElsewhere (off).
FIXER 2: (a) the MYTHIC SIGIL is refused on the Anvil by default - LOCKED 2026-10-08 popup batch 2 "Mythic boss-only (out of random drops +
Smithing step-up)"; row sigil.mythicUse (off) lets an owner allow it (question 11); (b) the extra tilled blocks use the vanilla till's exact
setBlock arguments (the block's rotation index, filler 0, SetBlockSettings.PERFORM_BLOCK_UPDATE = 256, verified bytecode 2026-10-14);
(c) the Sigil strip text is short (no "Reforge it after" tail, no "Sigil:" prefix, label 330 px, min font 12).
SAVED DATA: an item a Sigil touched carries r = the new rarity + sgN (Sigils used) (+ tr 1 on tools); a /pickaxe exact copy carries lrpS
(the Sigil count it was copied with); mining pieces get their lvl rewritten (as the lifelong tools do). Nothing else. New rows absent = their
default (no one-time update; a fresh file gets a 0.3.4 block right after the lifelong block).
ROLLBACK: 0.3.4 -> 0.3.3 is safe: Sigil items become unknown items (keep them in a chest), rarity changes made by Sigils stay (plain documents
0.3.3 reads); mining pieces keep their last written level; tiered-up mining pieces are ordinary pieces of the new tier.
"""
import os
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.3.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.4.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.3"' in s and "GENERATED by tools/gear_0_3_3_patch.py" in s and "0.3.4" not in s[:400], "not the generated 0.3.3 script"
assert "GearSigil" not in s and "GearTill" not in s and "GearArmLv" not in s
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.3":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.3" % _set.get("SkyyGear"))

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.3 - build script (javassist via jpype). GENERATED by tools/gear_0_3_3_patch.py from the LIVE 0.3.2 (itself GENERATED by
tools/gear_0_3_2_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.3.py -> SkyyGear/SkyyGear-0.3.3.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.3.py
''', '''"""SkyyGear 0.3.4 - build script (javassist via jpype). GENERATED by tools/gear_0_3_4_patch.py from the LIVE 0.3.3 (itself GENERATED by
tools/gear_0_3_3_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.4.py -> SkyyGear/SkyyGear-0.3.4.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.4.py

0.3.4 = SIGILS + GATHERING ARMOR THAT LEVELS + THE HOE TILL AREA (Gathering-Shards-Spec phase 4; notes: tools/gear_0_3_4_patch.py): five
Sigils (Unique .. Mythic) raise an item's rarity on the Anvil (skip tiers, upward only, new slots empty until a Reforge; never on the Bazaar,
the Auction House may sell them); the Mining armor pieces level with your Mining level (capped by tier) and tier up on the Anvil
with Enchanted materials keeping their rarity; your lifelong hoe tills a 1 / 3 / 3 / 5 / 5 / 7 / 7 / 9 square by tier (island worlds where
you may build; elsewhere only with hoe.areaElsewhere).

--- 0.3.3 notes ---
''')
rep('VERSION = "0.3.3"\n', 'VERSION = "0.3.4"\n')

# ================================================================================================================ build-time tables
# the armor tier-up ladders (spec 6.1 per piece: Iron / Thorium 1 / 2 / 2 / 1, Cobalt / Adamantite 1 / 1 / 1 / 0 -> hands 1: no free step)
after('''for _i in re.findall(r"(Tool_[A-Za-z]+_[A-Za-z]+)", LL_LADDER_DEF) + ["Ingredient_Bar_Copper"]:
    assert _i in AZ_ITEMS, "lifelong.ladders names %s - not in Assets.zip" % _i
''', '''# 0.3.4 GATHERING ARMOR THAT LEVELS (Skyy 2026-10-12 "Yes, like the tools"): the Mining armor pieces tier up on the Anvil with the Enchanted
# ingot of the NEW tier (research/Gathering-Shards-Spec.md 5.5 / 6.1: Head 1 / Chest 2 / Legs 2 / Hands 1 for Iron + Thorium, 1 / 1 / 1 / 0 for
# Cobalt + Adamantite - the 0 is made 1, no free step). Mithril / Onyxium wait for their Enchanted items (none in tools/skyyench.py yet).
GA_SLOT_N = {"Head": (1, 1), "Chest": (2, 1), "Legs": (2, 1), "Hands": (1, 1)}          # (Iron / Thorium, Cobalt / Adamantite)
GA_STEPS = [("Iron", 0), ("Thorium", 0), ("Cobalt", 1), ("Adamantite", 1)]
GA_LADDER_ROWS = []
for _sl in ("Head", "Chest", "Legs", "Hands"):
    _row = "Armor_Copper_%s" % _sl
    for _t, _c in GA_STEPS:
        _row += ">Armor_%s_%s(%s)" % (_t, _sl, _lle(_t, GA_SLOT_N[_sl][_c]))
    GA_LADDER_ROWS.append(_row)
GA_LADDER_DEF = ",".join(GA_LADDER_ROWS)
assert len(GA_LADDER_DEF) < 2000 and all(32 <= ord(_c) < 127 for _c in GA_LADDER_DEF) and "Mithril" not in GA_LADDER_DEF
for _i in re.findall(r"(Armor_[A-Za-z]+_[A-Za-z]+)", GA_LADDER_DEF):
    assert _i in AZ_ITEMS, "garmor.ladders names %s - not in Assets.zip" % _i
assert not (set(re.findall(r"([A-Z][A-Za-z]+_[A-Za-z_]+?)(?=[>(,]|$)", GA_LADDER_DEF)) & set(re.findall(r"(Tool_[A-Za-z]+_[A-Za-z]+)", LL_LADDER_DEF)))
# 0.3.4 THE HOE TILL AREA (spec 4.3 + G5 "Yes, as proposed"): the side of the tilled square per hoe tier Crude .. Onyxium
HOE_AREA_DEF = "1,3,3,5,5,7,7,9"
assert [int(_x) for _x in HOE_AREA_DEF.split(",")] == [1, 3, 3, 5, 5, 7, 7, 9]
''')

# ================================================================================================================ rows
after('''     "Logs need a hatchet and ore a pickaxe; bare hands and other items are refused.", "field:GearCfg.GATE_BARE"),
''', '''    # 0.3.4 SIGILS + GATHERING ARMOR LEVELS + THE HOE TILL AREA (research/Gathering-Shards-Spec.md phase 4; Skyy 2026-10-12 / 2026-10-13)
    ("part.sigils", "Rarity Sigils", "smithing", "bool", "true", "", "", "", "", "live,part,danger",
     "A Sigil raises an item's rarity on the Anvil (skips tiers, upward only). Off = Sigils do nothing.", "field:GearCfg.SIG_ON"),
    # fixer 2: LOCKED 2026-10-08 (popup batch 2) "Mythic boss-only (out of random drops + Smithing step-up)" - the Mythic Sigil is refused on
    # the Anvil unless the server owner turns this on (round question 11)
    ("sigil.mythicUse", "Mythic Sigil works on the Anvil", "smithing", "bool", "false", "", "", "", "", "live,danger",
     "Off = Mythic stays boss-only: a Mythic Sigil cannot make an item Mythic on the Anvil.", "field:GearCfg.SIG_MY"),
    ("garmor.levels", "Gathering armor levels with you", "garmor", "bool", "true", "", "", "", "", "live,part,danger",
     "Mining armor matches your Mining level (capped by tier) and tiers up on the Anvil. Off = fixed.", "field:GearCfg.GARM_LV"),
    ("garmor.ladders", "Gathering armor tier-up costs", "garmor", "text", GA_LADDER_DEF, "0", "2000", "", "", "live,danger",
     "Armor tiers on the Anvil, like upgrade.ladders: A>B(Id*2), ladders joined by commas.",
     "field:GearCfg.GARM_LADDERS;check=GearUp.checkLadders"),
    ("hoe.areaOn", "Hoe tills an area", "lifelong", "bool", "true", "", "", "", "", "live",
     "Your lifelong hoe tills a square by its tier (hoe.area) where you may build.", "field:GearCfg.HOE_ON"),
    ("hoe.area", "Till square per hoe tier", "lifelong", "text", HOE_AREA_DEF, "1", "40", "", "", "live",
     "Side of the square, Crude to Onyxium: 8 odd numbers 1-9, joined by commas.", "field:GearCfg.HOE_AREA;check=GearTill.checkArea"),
    ("hoe.areaElsewhere", "Area tilling outside islands", "lifelong", "bool", "false", "", "", "", "", "live,danger",
     "Off = the extra blocks are tilled only on island worlds where you may build.", "field:GearCfg.HOE_ELSE"),
''')
rep('''           "lifelong.resetCoins", "gate.on", "gate.nextFactor", "gate.bareHands", "lifelong.reclaimTier", "gate.crudeFactor",
           "gate.twoUpFactor"}''', '''           "lifelong.resetCoins", "gate.on", "gate.nextFactor", "gate.bareHands", "lifelong.reclaimTier", "gate.crudeFactor",
           "gate.twoUpFactor",
           # 0.3.4: Sigils (rarity = economy), gathering armor levels + tier-up costs, area tilling outside islands (protection)
           "part.sigils", "garmor.levels", "garmor.ladders", "hoe.areaElsewhere", "sigil.mythicUse"}''')
after('''assert all(32 <= ord(_c) < 127 for _c in LL_HEAD) and "=" not in LL_HEAD
''', '''G34_HEAD = "# ---- sigils, gathering armor levels, the hoe till area (SkyyGear 0.3.4) ----"
G34_ROWK = ["part.sigils", "sigil.mythicUse", "garmor.levels", "garmor.ladders", "hoe.areaOn", "hoe.area", "hoe.areaElsewhere"]
assert all(32 <= ord(_c) < 127 for _c in G34_HEAD) and "=" not in G34_HEAD
''')
rep('''    for k in LL_ROWK:
        scal(k)
    L += [""] + GU_LINES''', '''    for k in LL_ROWK:
        scal(k)
    L += ["", G34_HEAD]         # 0.3.4: the new rows (no one-time update adds them; absent = the default)
    for k in G34_ROWK:
        scal(k)
    L += [""] + GU_LINES''')
rep('''              ("GATE_TWO", "double", "0.1")]          # 0.3.1''', '''              ("GATE_TWO", "double", "0.1"),          # 0.3.1
              # 0.3.4 sigils, gathering armor levels, the hoe till area
              ("SIG_ON", "boolean", "true"), ("SIG_MY", "boolean", "false"), ("GARM_LV", "boolean", "true"), ("GARM_LADDERS", "String", jstr(GA_LADDER_DEF)),
              ("HOE_ON", "boolean", "true"), ("HOE_AREA", "String", jstr(HOE_AREA_DEF)), ("HOE_ELSE", "boolean", "false")]''')
after('''  GATE_BARE = pbool(p, "gate.bareHands", true);
''', '''  // 0.3.4 sigils, gathering armor levels, the hoe till area (ladders / area checked where they are used - a bad part = one WARN, the default)
  SIG_ON = pbool(p, "part.sigils", true);
  SIG_MY = pbool(p, "sigil.mythicUse", false);          // fixer 2: Mythic is boss-only unless the owner allows the Mythic Sigil
  GARM_LV = pbool(p, "garmor.levels", true);
  GARM_LADDERS = ptext(p, "garmor.ladders", "@GALADDEF@").trim();
  HOE_ON = pbool(p, "hoe.areaOn", true);
  HOE_AREA = ptext(p, "hoe.area", "@HOEAREADEF@").trim();
  HOE_ELSE = pbool(p, "hoe.areaElsewhere", false);
''')
rep('''.replace("@IDTOOLDEF@", ID_TOOL_DEF).replace("@LLLADDEF@", LL_LADDER_DEF))''',
    '''.replace("@IDTOOLDEF@", ID_TOOL_DEF).replace("@LLLADDEF@", LL_LADDER_DEF)
   .replace("@GALADDEF@", GA_LADDER_DEF).replace("@HOEAREADEF@", HOE_AREA_DEF))''')

# ================================================================================================================ the Sigil items (assets)
SIGIL_ITEMS_PY = '''
# ================================================================= 0.3.4 THE SIGILS (Skyy 2026-10-12 "Sigils"; docs/log 2026-10-13 ART REVIEW "ship 5: Unique..Mythic"):
# the icons are the approved art (research/cloud/icons-1013/icons, our own 64 px drawings); the held model is the vanilla Rune Shard model BY
# PATH with a rarity-tinted copy of its texture made here (nothing vanilla committed)
SIG_RIDS = ["unique", "rare", "legendary", "fabled", "mythic"]
SIG_IDS = ["Skyy_Sigil_" + R_NAMES[R_IDS.index(_r)] for _r in SIG_RIDS]
SIG_RANK = [R_IDS.index(_r) for _r in SIG_RIDS]
assert SIG_RANK == [1, 2, 3, 4, 5] and SIG_IDS[0] == "Skyy_Sigil_Unique" and SIG_IDS[-1] == "Skyy_Sigil_Mythic"
_SIG_SRC = "Server/Item/Items/Ingredient/Goblin/Ingredient_Rune_Shard.json"
_sj = json.loads(AZ.read(_SIG_SRC).decode("utf-8-sig"))
SIG_MODEL = _sj["Model"]
SIG_TEX_SRC = _sj["Texture"]
for _p in (SIG_MODEL, SIG_TEX_SRC):
    assert ("Common/" + _p) in AZ_NAMES, "the Sigil held-model source is gone from Assets.zip: " + _p
SIG_ART = os.path.join(os.path.dirname(HERE), "research", "cloud", "icons-1013", "icons")
SIG_FILES = {}
SIG_ITEMS = {}
_stex = AZ.read("Common/" + SIG_TEX_SRC)
for _k, _sid in enumerate(SIG_IDS):
    _nm = R_NAMES[SIG_RANK[_k]]
    _png = open(os.path.join(SIG_ART, _sid + ".png"), "rb").read()
    _w, _h = SA.png_size(_png)
    assert (_w, _h) == (64, 64), "the approved Sigil icon %s is %dx%d, not 64x64" % (_sid, _w, _h)
    SIG_FILES["Common/Icons/ItemsGenerated/%s.png" % _sid] = _png
    SIG_FILES["Common/Items/SkyyGear/Sigil/Sigil_%s.png" % _nm] = SA.recolor(_stex, _ramp(BAG_RAMP[SIG_RIDS[_k]]), rank=0.35)
    SIG_ITEMS["Server/Item/Items/SkyyGear/%s.json" % _sid] = json.dumps({
        "TranslationProperties": {"Name": "server.items.%s.name" % _sid, "Description": "server.items.%s.description" % _sid},
        "Quality": QUAL_IDS[SIG_RANK[_k]], "MaxStack": 16,
        "Icon": "Icons/ItemsGenerated/%s.png" % _sid, "IconProperties": _sj["IconProperties"],
        "Model": SIG_MODEL, "Texture": "Items/SkyyGear/Sigil/Sigil_%s.png" % _nm, "Scale": _sj.get("Scale", 0.8),
        "PlayerAnimationsId": "Item", "ItemSoundSetId": _sj.get("ItemSoundSetId", "ISS_Items_Gems"), "Tags": {"Type": ["Sigil"]}}, indent=2)
    assert _sid not in AZ_ITEMS, _sid
for _k, _v in SIG_FILES.items():
    assert _k not in AZ_NAMES, "a Sigil file would shadow a vanilla file: " + _k
SIG_LANG = []
for _k, _sid in enumerate(SIG_IDS):
    _nm = R_NAMES[SIG_RANK[_k]]
    SIG_LANG.append("items.%s.name = %s Sigil" % (_sid, _nm))
    if _nm == "Mythic":          # fixer 2: Mythic is boss-only (sigil.mythicUse off by default)
        SIG_LANG.append("items.%s.description = A boss treasure. Mythic gear comes from bosses - this Sigil works on the Anvil only where the server allows it. Never sold on the Bazaar." % _sid)
    else:
        SIG_LANG.append("items.%s.description = Raises an item to %s on the Anvil (/smithing) - skips tiers, upward only. Reforge it after to fill the new slots. Never sold on the Bazaar." % (_sid, _nm))
EXTRA.update(SIG_FILES)
EXTRA.update(SIG_ITEMS)
EXTRA["Server/Languages/en-US/server.lang"] = EXTRA["Server/Languages/en-US/server.lang"] + "\\n".join(SIG_LANG) + "\\n"
print("0.3.4 sigils: %d items (%s), approved icons + tinted rune texture, %d files" % (len(SIG_IDS), ", ".join(SIG_IDS), len(SIG_FILES)))
'''
after('''print("0.2.11 mystery bags: %d items (%s art), %d files" % (len(BAG_IDS), BAG_ART, len(BAG_FILES)))
''', SIGIL_ITEMS_PY)

# ================================================================================================================ GearArmLv (early: before GearTool)
after('''M(gll, "public static String newUid() { return java.util.UUID.randomUUID().toString().replace(\\"-\\", \\"\\").substring(0, 16); }")
''', '''# ---- 0.3.4 GATHERING ARMOR THAT LEVELS (GearArmLv, early part: GearTool.held calls watch once a second). Level = the gate skill (Mining for the
# 28 metal pieces) kept inside the piece's tier band: never above you once you reach its tier, inactive below its tier's start
garl = mk("GearArmLv")
G34_CLASSES = [garl]
F(garl, "public static final java.util.concurrent.ConcurrentHashMap LV = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Integer (Mining level seen)
F(garl, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Long (last sync)
F(garl, "public static final java.util.concurrent.ConcurrentHashMap FORCE = new java.util.concurrent.ConcurrentHashMap();")   # fixer: UUID -> TRUE (a level-up: the next sync skips the 400 ms throttle)
F(garl, "public static final long[] N = new long[4];")          # 0 syncs, 1 levels written, 2 write fails, 3 level-ups noticed
# the gate skill of a gathering armor piece (null = not one): today only the Mining metal pieces (Foraging / Farming / Fishing sets plug in here)
M(garl, r"""
public static String skillOf(String id) {
  if (!@PKG@.GearCfg.GARM_LV || id == null) return null;
  return @PKG@.GearMine.isPiece(id) ? "Mining" : null;
}""")
# THE LEVEL RULE (Skyy 2026-10-12 "Yes, like the tools"): the skill level kept inside the band; -1 = not a piece / skill unknown (no SkyySkills)
M(garl, r"""
public static int levelFor(java.util.UUID u, String id) {
  String sk = skillOf(id);
  if (sk == null || u == null) return -1;
  int h = @PKG@.GearGate.have(u, sk);
  if (h == -2) return -1;
  if (h < 0) h = 0;
  int f = @PKG@.GearLevel.floor(h);
  int[] b = @PKG@.GearLevel.band(id);
  int lv = f < b[0] ? b[0] : (f > b[1] ? b[1] : f);
  return lv < 1 ? 1 : lv;
}""")
# once a second (GearTool.held): a Mining level-up since the last look queues the stamp scan (its sync rewrites "[Lv N]")
M(garl, r"""
public static void watch(java.util.UUID u) {
  try {
    if (!@PKG@.GearCfg.GARM_LV || u == null) return;
    int h = @PKG@.GearGate.have(u, "Mining");
    Object o = LV.get(u);
    if (o instanceof Integer && ((Integer) o).intValue() == h) return;
    LV.put(u, Integer.valueOf(h));
    if (o != null) { N[3] = N[3] + 1L; FORCE.put(u, Boolean.TRUE); @PKG@.GearLL.RESYNC.put(u, Boolean.TRUE); }          // fixer: FORCE first
  } catch (Throwable t) { }
}""")
M(garl, "public static void forget(java.util.UUID u) { if (u != null) { LV.remove(u); LAST.remove(u); FORCE.remove(u); } }")
# a piece whose level follows the skill (an identified document); Reforge Level up refuses it
M(garl, r"""
public static boolean synced(String id, @BD@ d) {
  return skillOf(id) != null && d != null && @PKG@.GearData.identified(d);
}""")
# a tier-up needs the gate skill level the new tier starts at (its band start); null = fine
M(garl, r"""
public static String tierWhy(java.util.UUID u, String to) {
  String sk = skillOf(to);
  if (sk == null || u == null) return null;
  int h = @PKG@.GearGate.have(u, sk);
  if (h == -2) return null;
  int need = @PKG@.GearLevel.band(to)[0];
  if (h >= need) return null;
  return @PKG@.Gear.itemName(to) + " needs " + sk + " " + need + " (you: " + (h < 0 ? 0 : h) + ").";
}""")
''')
rep('''  @PKG@.GearLL.lvlWatch(u, s);          // 0.3.0 fix round: a lifelong tool's stale [Lv N] after a skill level-up (GearHandSys queues the sweep)
''', '''  @PKG@.GearLL.lvlWatch(u, s);          // 0.3.0 fix round: a lifelong tool's stale [Lv N] after a skill level-up (GearHandSys queues the sweep)
  @PKG@.GearArmLv.watch(u);          // 0.3.4: a Mining level-up -> the stamp scan re-levels the worn / carried mining armor
''')
# the Anvil ladders = upgrade.ladders + lifelong.ladders + (0.3.4) garmor.ladders
rep('''M(gll, r"""
public static String ladders() {
  String a = @PKG@.GearCfg.UP_LADDERS == null ? "" : @PKG@.GearCfg.UP_LADDERS;
  String b = @PKG@.GearCfg.LL_LADDERS == null ? "" : @PKG@.GearCfg.LL_LADDERS;
  if (!@PKG@.GearCfg.LL_ON || b.trim().length() == 0) return a;
  if (a.trim().length() == 0) return b;
  return a + "," + b;
}""")''', '''M(gll, r"""
public static String ladders() {
  String a = @PKG@.GearCfg.UP_LADDERS == null ? "" : @PKG@.GearCfg.UP_LADDERS;
  String b = @PKG@.GearCfg.LL_LADDERS == null ? "" : @PKG@.GearCfg.LL_LADDERS;
  String c = @PKG@.GearCfg.GARM_LADDERS == null || !@PKG@.GearCfg.GARM_LV ? "" : @PKG@.GearCfg.GARM_LADDERS;          // 0.3.4: gathering armor
  String r = a;
  if (@PKG@.GearCfg.LL_ON && b.trim().length() > 0) r = r.trim().length() == 0 ? b : r + "," + b;
  if (c.trim().length() > 0) r = r.trim().length() == 0 ? c : r + "," + c;
  return r;
}""")''')
# a /pickaxe replacement a Sigil was used on is invested (never thrown away when the original turns up)
rep('''  return t > @PKG@.GearData.num(d, "lrpT", t) || @PKG@.GearData.num(d, "rfN", 0) > @PKG@.GearData.num(d, "lrpF", 0);''',
    '''  // 0.3.4: a Sigil used AFTER the copy (sgN over lrpS) invests it too
  return t > @PKG@.GearData.num(d, "lrpT", t) || @PKG@.GearData.num(d, "rfN", 0) > @PKG@.GearData.num(d, "lrpF", 0)
    || @PKG@.GearData.num(d, "sgN", 0) > @PKG@.GearData.num(d, "lrpS", 0);''')
rep('''    nd.put("lrpF", new org.bson.BsonInt32(@PKG@.GearData.num(src, "rfN", 0)));
''', '''    nd.put("lrpF", new org.bson.BsonInt32(@PKG@.GearData.num(src, "rfN", 0)));
    nd.put("lrpS", new org.bson.BsonInt32(@PKG@.GearData.num(src, "sgN", 0)));          // 0.3.4: only a LATER Sigil invests the copy
''')

# ================================================================================================================ GearSigil + GearArmLv (before GearWall)
before('''# ================================================================= 0.2.14 GearWall: THE MARKET WALL''', '''# ================================================================= 0.3.4 GearSigil (1/2): the ids, the market rule (GearWall asks it) - the Anvil core is
# after GearUp (2/2). G3 "No Mythic Sigil; AH yes, Bazaar never": the Auction House may list / sell a Sigil, the Bazaar never
# (fixer: com.skyy.merchants is listed for when SkyyMerchants asks market:veto - 0.1.3 does not, see the header)
gsig = mk("GearSigil")
G34_CLASSES.append(gsig)
F(gsig, "public static final String[] IDS = %s;" % jarr(SIG_IDS))
F(gsig, "public static final int[] RANK = %s;" % jints(SIG_RANK))
F(gsig, 'public static final String[] NOSELL = new String[] { "com.skyy.bazaar.", "com.skyy.merchants." };')
F(gsig, 'public static final String MARKET = "Sigils are never sold on the Bazaar - list it on the Auction House or trade it directly.";')
F(gsig, 'public static final String MYOFF = "Mythic is boss-only - a Mythic Sigil cannot be used on this server.";')          # fixer 2 (sigil.mythicUse off)
F(gsig, "public static volatile int CRASH_AT = 0;")          # harness only: 1 = throw right after the Sigil left (a crash)
F(gsig, "public static final long[] N = new long[4];")          # 0 applied, 1 refused, 2 failed (put back), 3 market refusals
# the rarity a Sigil id sets (1 Unique .. 5 Mythic), 0 = not a Sigil
M(gsig, r"""
public static int rank(String id) {
  if (id == null || !id.startsWith("Skyy_Sigil_")) return 0;
  for (int i = 0; i < IDS.length; i++) if (IDS[i].equals(id)) return RANK[i];
  return 0;
}""")
M(gsig, r"""
public static String idOf(int r) {
  for (int i = 0; i < RANK.length; i++) if (RANK[i] == r) return IDS[i];
  return null;
}""")
# GearWall: a Sigil asked about by the Bazaar (or a future SkyyMerchants that asks; the caller's classes on this thread's stack) = refused; anyone else (the Auction House) = allowed
M(gsig, r"""
public static String marketWhy() {
  StackTraceElement[] st = new Throwable().getStackTrace();
  for (int i = 0; i < st.length; i++) {
    String c = st[i].getClassName();
    if (c == null) continue;
    for (int k = 0; k < NOSELL.length; k++) if (c.startsWith(NOSELL[k])) { N[3] = N[3] + 1L; return MARKET; }
  }
  return null;
}""")
# 0.3.4 GearArmLv (2/2, read side): a mining piece's level follows the skill (Reforge Level up refuses it); a piece may climb garmor.ladders
# keeping its rarity: Set (with a GATHERING set field or none) or a plain rarity (an old rolled piece) - never Mythic / Untiered / a quest set
M(garl, r"""
public static boolean ladderOk(String id, @BD@ d) {
  if (skillOf(id) == null || d == null) return false;
  int r = @PKG@.GearData.rarity(d);
  if (r != @PKG@.GearDefs.R_SET && r > 4) return false;
  String sid = @PKG@.GearSet.of(d);
  return sid == null || @PKG@.GearUtFx.gathering(sid);
}""")
''')
# GearWall: a Sigil is no gear - the market rule above, before the gear checks
rep('''  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.llStack(id, md)) return "Lifelong tools stay with their owner - they never go on the market.";
''', '''  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.llStack(id, md)) return "Lifelong tools stay with their owner - they never go on the market.";
  if (@PKG@.GearSigil.rank(id) > 0) return @PKG@.GearSigil.marketWhy();          // 0.3.4: AH yes, Bazaar never (G3)
''')
# Reforge Level up: a mining piece follows the skill
rep('''  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.isLL(d)) return lvOut(8, cur, cur, org, "a lifelong tool follows your skill level.");     // 0.3.0
''', '''  if (@PKG@.GearCfg.LL_ON && @PKG@.GearLL.isLL(d)) return lvOut(8, cur, cur, org, "a lifelong tool follows your skill level.");     // 0.3.0
  if (@PKG@.GearArmLv.synced(id, d)) return lvOut(8, cur, cur, org, "gathering armor follows your " + @PKG@.GearArmLv.skillOf(id) + " level.");     // 0.3.4
''')

# ================================================================================================================ GearTill (early) + the hit mark
before('''# 0.2.12: GearToolHitSys = the DamageBlockEvent hook SkyyTrees' TreeDmgSys''', '''# 0.3.4 GearTill (1/2, early): the last block hit per player (GearToolHitSys) - a hoe's durability drop within 300 ms of a block hit is a
# left-click swing, never a till. The till itself (GearTill 2/2 + GearTillSys) is near the plugin.
gtill = mk("GearTill")
G34_CLASSES.append(gtill)
F(gtill, "public static final java.util.concurrent.ConcurrentHashMap HIT = new java.util.concurrent.ConcurrentHashMap();")   # UUID -> Long
M(gtill, "public static void hitMark(java.util.UUID u) { if (u != null) HIT.put(u, Long.valueOf(System.currentTimeMillis())); }")
M(gtill, "public static void forget(java.util.UUID u) { if (u != null) HIT.remove(u); }")
''')
rep('''    if (pr == null) return;
    float d0 = e.getDamage();
    // 0.3.3: a crop two or more tiers above''', '''    if (pr == null) return;
    @PKG@.GearTill.hitMark(pr.getUuid());          // 0.3.4: a block hit is no till (the hoe's durability drop that follows)
    float d0 = e.getDamage();
    // 0.3.3: a crop two or more tiers above''')

# ================================================================================================================ GearArmLv.sync + the stamp task
before('''M(gspt, r"""
public void run() {
  java.util.UUID u = null;''', '''# 0.3.4 GearArmLv.sync (the stamp task, after the lifelong sweep; at most every 400 ms per player): every identified mining piece in the
# inventory sections (armor included) whose level is not the rule's gets it written (GearData.put: name + tooltip follow; our own write -
# GearStamp.selfNote). Unstamped / unidentified pieces are left to the stamp scan / Identify. Never throws.
M(garl, r"""
public static int sync(@PR@ pr, @INV@ inv, boolean force) {
  int n = 0;
  try {
    if (!@PKG@.GearCfg.GARM_LV || pr == null || inv == null) return 0;
    java.util.UUID u = pr.getUuid();
    if (@PKG@.Gear.busy(u)) return 0;
    boolean fz = FORCE.remove(u) != null;          // fixer: a level-up the watch saw is never eaten by the throttle (its RESYNC is already used up)
    long now = System.currentTimeMillis();
    Object l = LAST.get(u);
    if (!force && !fz && l instanceof Long && now >= ((Long) l).longValue() && now - ((Long) l).longValue() < 400L) return 0;
    LAST.put(u, Long.valueOf(now));
    N[0] = N[0] + 1L;
    for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
      @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
      if (c == null) continue;
      for (int i = 0; i < c.getCapacity(); i++) {
        @IS@ x = c.getItemStack((short) i);
        if (x == null || x.isEmpty() || skillOf(x.getItemId()) == null || x.getQuantity() != 1) continue;
        @BD@ d = null;
        try { d = @PKG@.GearData.gearDoc(x.getMetadata()); } catch (Throwable td) { d = null; }
        if (!synced(x.getItemId(), d)) continue;
        int lv = levelFor(u, x.getItemId());
        if (lv < 1 || @PKG@.GearData.num(d, "lvl", -1) == lv) continue;
        @BD@ nd = d.clone();
        nd.put("lvl", new org.bson.BsonInt32(lv));
        nd.remove("lvU");
        Object tx = null;
        try { tx = c.setItemStackForSlot((short) i, @PKG@.GearData.put(x, nd, u)); } catch (Throwable tw) { tx = null; }
        @IS@ back = c.getItemStack((short) i);
        boolean ok = tx != null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) && back != null && x.getItemId().equals(back.getItemId());
        if (!ok) { N[2] = N[2] + 1L; continue; }
        @PKG@.GearStamp.selfNote(u, tx);
        N[1] = N[1] + 1L;
        n++;
      }
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("armlv", "the gathering armor level sync failed: " + t); }
  return n;
}""")
M(garl, r"""
public static String statusText() {
  return "gathering armor " + (@PKG@.GearCfg.GARM_LV ? "levels with the skill (Mining pieces: Mining level kept inside the tier band; Anvil tier-up " + (@PKG@.GearCfg.GARM_LADDERS == null || @PKG@.GearCfg.GARM_LADDERS.trim().length() == 0 ? "off" : "on") + ")" : "OFF (garmor.levels)");
}""")
''')
rep('''    @PKG@.GearLL.sweepHook(this.pr, @PKG@.GearStamp.invOf(this.pr));          // 0.3.0: lifelong levels / copies (throttled inside)
''', '''    @PKG@.GearLL.sweepHook(this.pr, @PKG@.GearStamp.invOf(this.pr));          // 0.3.0: lifelong levels / copies (throttled inside)
    @PKG@.GearArmLv.sync(this.pr, @PKG@.GearStamp.invOf(this.pr), false);          // 0.3.4: gathering armor levels (throttled inside)
''')

# ================================================================================================================ GearUp: armor tier-up
rep('''    if (@PKG@.GearData.rarity(d) > 4 || @PKG@.GearSet.of(d) != null) return new Object[] { special(id), to, null };
  }''', '''    // 0.3.4: a gathering armor piece climbs garmor.ladders keeping its Set rarity (a gathering set field) - quest / boss sets never
    if ((@PKG@.GearData.rarity(d) > 4 || @PKG@.GearSet.of(d) != null) && !@PKG@.GearArmLv.ladderOk(id, d)) return new Object[] { special(id), to, null };
  }
  // 0.3.4: a gathering armor tier-up needs the skill level the new tier starts at (Mining 15 for Iron ...)
  String aw = @PKG@.GearArmLv.tierWhy(u, to);
  if (aw != null && @PKG@.GearArmLv.skillOf(id) != null) return new Object[] { aw, to, null };''')
rep('''  if (u != null && @PKG@.GearLL.isLL(nd)) {
    int ll = @PKG@.GearLL.levelFor(u, to);
    if (ll >= 1) { nd.put("lvl", new org.bson.BsonInt32(ll)); info[3] = ll; }
  }
  return nd;''', '''  if (u != null && @PKG@.GearLL.isLL(nd)) {
    int ll = @PKG@.GearLL.levelFor(u, to);
    if (ll >= 1) { nd.put("lvl", new org.bson.BsonInt32(ll)); info[3] = ll; }
  }
  // 0.3.4: a gathering armor piece moves to the new tier's Mining Set (a gathering set field only) and takes the level rule
  if (@PKG@.GearArmLv.skillOf(to) != null) {
    String os = @PKG@.GearSet.of(nd);
    String ns = @PKG@.GearMine.setFor(to);
    if (os != null && ns != null && @PKG@.GearUtFx.gathering(os)) nd.put("set", new org.bson.BsonString(ns));
    int al = @PKG@.GearArmLv.levelFor(u, to);
    if (al >= 1) { nd.put("lvl", new org.bson.BsonInt32(al)); info[3] = al; }
  }
  return nd;''')

# ================================================================================================================ GearSigil (2/2): the Anvil core
before('''# ================================================================= GearUnid.reView: a bag's name follows the switch''', '''# ================================================================= 0.3.4 GearSigil (2/2): the Anvil core (the 0.2.22 Upgrade write pattern)
# why an item cannot take Sigil rarity R (null = it can); d = its document (GearForge.docOf)
M(gsig, r"""
public static String why(@IS@ it, @BD@ d, int R) {
  if (!@PKG@.GearCfg.SIG_ON) return "Sigils are switched off on this server.";
  if (it == null || it.isEmpty()) return "Pick an item first.";
  String id = it.getItemId();
  if (!@PKG@.GearData.forgeable(id)) return @PKG@.Gear.itemName(id) + " has no rarity - Sigils work on weapons, armor and gathering tools.";
  if (it.getQuantity() != 1) return "That item is a stack of " + it.getQuantity() + " - split it first.";
  if (@PKG@.GearUt.has(id) || @PKG@.GearUtFx.mythicId(id)) return @PKG@.Gear.itemName(id) + " is a special item - its rarity never changes.";
  int st = @PKG@.GearData.state(it.getMetadata());
  if (st == 3 || st == 4 || d == null) return "The gear data on that item cannot be read here - an admin can check it with /gear read.";
  if (!@PKG@.GearData.identified(d)) return "Identify it first" + @PKG@.GearCfg.idHow() + ".";
  int r = @PKG@.GearData.rarity(d);
  if (r == @PKG@.GearDefs.R_SET || @PKG@.GearSet.of(d) != null) {
    String gsk = @PKG@.GearArmLv.skillOf(id);          // fixer: gathering armor says what it does instead (round question 8)
    if (gsk != null) return "Set rarity stays - gathering armor levels with your " + gsk + " and tiers up on the Anvil instead.";          // fixer 2: short enough for the strip
    return "Set pieces keep their Set rarity - a Sigil cannot change them.";
  }
  if (r == @PKG@.GearDefs.R_UT) return "Untiered items have fixed stats - a Sigil cannot change them.";
  if (r >= @PKG@.GearDefs.R_MY) return "It is already Mythic - nothing is above it.";
  if (R <= r) return "A " + @PKG@.GearDefs.R_NAME[R] + " Sigil only raises items below " + @PKG@.GearDefs.R_NAME[R] + " - this one is " + @PKG@.GearDefs.R_NAME[r] + ".";
  if (R >= @PKG@.GearDefs.R_MY && !@PKG@.GearCfg.SIG_MY) return MYOFF;          // fixer 2: LOCKED "Mythic boss-only (... + Smithing step-up)"
  return null;
}""")
# the new document: rarity R, lines kept (the new slots stay empty until a Reforge), sgN + 1; a tool shows its rarity from now on (tr 1)
M(gsig, r"""
public static @BD@ docFor(String id, @BD@ d, int R) {
  @BD@ nd = d.clone();
  nd.put("r", new org.bson.BsonString(@PKG@.GearDefs.R_ID[R]));
  if (@PKG@.GearData.toolRolls(id)) nd.put("tr", new org.bson.BsonInt32(1));
  nd.put("sgN", new org.bson.BsonInt32(@PKG@.GearData.num(d, "sgN", 0) + 1));
  return nd;
}""")
# how many of each Sigil the player carries (inventory, backpack, hotbar - the Upgrade materials' sections); index = rank
M(gsig, r"""
public static int[] carried(@INV@ inv) {
  int[] n = new int[7];
  if (inv == null) return n;
  for (int i = 0; i < IDS.length; i++) n[RANK[i]] = @PKG@.GearUp.have(inv, IDS[i]);
  return n;
}""")
# the Sigils that would raise this rarity, lowest first (ranks); empty = none carried above it. fixer 2: the Mythic Sigil only with sigil.mythicUse
M(gsig, r"""
public static int[] choices(int[] have, int r) {
  int top = @PKG@.GearCfg.SIG_MY ? 5 : 4;
  int k = 0;
  for (int i = r + 1; i <= top; i++) if (have[i] > 0) k++;
  int[] out = new int[k];
  k = 0;
  for (int i = r + 1; i <= top; i++) if (have[i] > 0) out[k++] = i;
  return out;
}""")
M(gsig, r"""
public static Object[] res(int code, String msg) { return new Object[] { Integer.valueOf(code), msg, null, null }; }""")
# THE WRITE. Object[] { Integer code (1 done, 0 refused - nothing moved, -1 failed - see the message), String message, IS the new item, BD its
# document }. (a) ONE Sigil leaves its slot (storage first, never the item's own slot), (b) the item's own slot gets the new document; any
# failure puts both back; SIGIL-BEGIN is on disk before anything moves; the counts are checked after.
M(gsig, r"""
public static Object[] apply(@INV@ inv, int s, int slot, String id, String fp, int R, java.util.UUID u, String who) {
  @IC@ ic = @PKG@.GearStamp.section(inv, s);
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (ic == null || !@PKG@.GearForge.same(it, id, fp)) return res(0, "The item moved or changed - pick it again.");
  @BD@ d = @PKG@.GearForge.docOf(id, it.getMetadata());
  String why = why(it, d, R);
  if (why != null) { N[1] = N[1] + 1L; return res(0, why); }
  String sid = idOf(R);
  if (sid == null || @PKG@.Gear.item(sid) == null) return res(0, "There is no " + @PKG@.GearDefs.R_NAME[R] + " Sigil on this server.");
  @IC@[] secs = @PKG@.GearUp.matSecs(inv);
  java.util.ArrayList plan = new java.util.ArrayList();
  for (int j = 0; j < secs.length && plan.isEmpty(); j++) {
    @IC@ mc = secs[j];
    if (mc == null) continue;
    for (int i = 0; i < mc.getCapacity() && plan.isEmpty(); i++) {
      if (mc == ic && i == slot) continue;
      @IS@ x = mc.getItemStack((short) i);
      if (!@PKG@.GearUp.usable(x, sid)) continue;
      plan.add(new Object[] { mc, Integer.valueOf(i), x, x.getQuantity() > 1 ? x.withQuantity(x.getQuantity() - 1) : null });
    }
  }
  if (plan.isEmpty()) { N[1] = N[1] + 1L; return res(0, "You need a " + @PKG@.GearDefs.R_NAME[R] + " Sigil in your inventory, backpack or hotbar."); }
  @BD@ nd = null;
  @IS@ ns = null;
  try { nd = docFor(id, d, R); ns = @PKG@.GearData.put(it, nd, u); } catch (Throwable t0) { nd = null; ns = null; @PKG@.Gear.warn("sigil: the document could not be made for " + who + ": " + t0); }
  if (nd == null || ns == null || ns.isEmpty() || !id.equals(ns.getItemId())) return res(0, "The new item could not be made - nothing was used.");
  Object[] e = (Object[]) plan.get(0);
  @IC@ mc = (@IC@) e[0];
  int sl = ((Integer) e[1]).intValue();
  @IS@ rest = (@IS@) e[3];
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int bs = @PKG@.GearStamp.countId(all, sid);
  int bi = @PKG@.GearStamp.countId(all, id);
  int r0 = @PKG@.GearData.rarity(d);
  @PKG@.GearLog.line("SIGIL-BEGIN " + who + " " + u + " " + id + " @" + @PKG@.GearForge.where(s, slot) + " " + @PKG@.GearMerge.json(it) + " -> " + @PKG@.GearDefs.R_ID[R] + " " + nd.toJson() + " sigil " + sid + " @" + @PKG@.GearUp.where(secs, mc, sl));
  try { @PKG@.GearLog.flush(); } catch (Throwable xf) { }          // SIGIL-BEGIN is ON DISK before anything moves
  // (a) the Sigil leaves
  Object tx = null;
  Throwable ex = null;
  try { tx = rest == null ? mc.removeItemStackFromSlot((short) sl) : mc.setItemStackForSlot((short) sl, rest); } catch (Throwable x) { ex = x; }
  @IS@ now = mc.getItemStack((short) sl);
  boolean ok = ex == null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded())
    && (rest == null ? (now == null || now.isEmpty()) : (now != null && !now.isEmpty() && sid.equals(now.getItemId()) && now.getQuantity() == rest.getQuantity()));
  if (!ok) {
    String rb = @PKG@.GearUp.restore(plan, 1, secs);
    N[2] = N[2] + 1L;
    if (rb.length() > 0) {
      @PKG@.Gear.warn("SIGIL: the Sigil of " + who + " (" + u + ") could not be put back - it is in gear.log (SIGIL-RESTORE-FAILED)");
      @PKG@.GearLog.line("SIGIL-RESTORE-FAILED " + who + " " + u + " not back: " + rb);
      return res(-1, "Something went wrong and the Sigil could not be put back - an admin can find it in the server log.");
    }
    @PKG@.GearLog.line("SIGIL-FAILED " + who + " " + u + " (the Sigil was not taken: " + (ex != null ? String.valueOf(ex) : "the inventory refused it") + ") - RESTORED, nothing used");
    return res(-1, "The inventory refused the change - nothing was used.");
  }
  if (CRASH_AT == 1) throw new IllegalStateException("harness: a crash right after the Sigil left");
  // (b) the item's own slot gets the new document
  Object t2 = null;
  Throwable e2 = null;
  try { t2 = ic.setItemStackForSlot((short) slot, ns); } catch (Throwable x2) { e2 = x2; }
  @IS@ now2 = ic.getItemStack((short) slot);
  @BD@ d2 = null;
  try { d2 = now2 == null || now2.isEmpty() ? null : @PKG@.GearData.gearDoc(now2.getMetadata()); } catch (Throwable td) { d2 = null; }
  boolean put = e2 == null && !(t2 instanceof @TXN@ && !((@TXN@) t2).succeeded()) && now2 != null && id.equals(now2.getItemId()) && d2 != null && @PKG@.GearData.rarity(d2) == R;
  if (!put) {
    String why2 = e2 != null ? String.valueOf(e2) : "the inventory refused it";
    boolean kept = @PKG@.GearForge.same(now2, id, fp);
    if (!kept) {
      try { ic.setItemStackForSlot((short) slot, it); } catch (Throwable xr) { }
      kept = @PKG@.GearForge.same(ic.getItemStack((short) slot), id, fp);
    }
    String rb2 = @PKG@.GearUp.restore(plan, 1, secs);
    N[2] = N[2] + 1L;
    if (!kept || rb2.length() > 0) {
      @PKG@.Gear.warn("SIGIL FAILED for " + who + " (" + u + "): " + why2 + (kept ? "" : " - the item could not be put back") + (rb2.length() > 0 ? " - the Sigil is not back: " + rb2 : "") + "; everything is in gear.log");
      @PKG@.GearLog.line("SIGIL-RESTORE-FAILED " + who + " " + u + " " + id + " " + @PKG@.GearMerge.json(it) + " (item back " + kept + ") sigil not back: [" + rb2 + "]: " + why2);
      return res(-1, "Something went wrong - an admin can find your item and Sigil in the server log.");
    }
    @PKG@.GearLog.line("SIGIL-FAILED " + who + " " + u + " (the item was not written: " + why2 + ") - RESTORED, nothing used");
    return res(-1, "The inventory refused the new item - nothing was used.");
  }
  @PKG@.GearStamp.selfNote(u, t2);
  int as = @PKG@.GearStamp.countId(all, sid);
  int ai = @PKG@.GearStamp.countId(all, id);
  if (as != bs - 1 || ai != bi) {
    @PKG@.Gear.warn("SIGIL COUNT MISMATCH for " + who + ": " + sid + " " + bs + "->" + as + " " + id + " " + bi + "->" + ai);
    @PKG@.GearLog.line("SIGIL-COUNT " + who + " " + u + " " + sid + " " + bs + "->" + as + " " + id + " " + bi + "->" + ai);
  }
  N[0] = N[0] + 1L;
  @PKG@.GearLog.line("SIGIL " + who + " " + u + " " + id + " " + @PKG@.GearDefs.R_ID[r0] + " -> " + @PKG@.GearDefs.R_ID[R] + " [" + @PKG@.GearView.modSummary(nd) + "] sgN " + @PKG@.GearData.num(nd, "sgN", 0) + " @" + @PKG@.GearForge.where(s, slot));
  return new Object[] { Integer.valueOf(1), "Done!", ns, nd };
}""")
M(gsig, r"""
public static String statusText() {
  return "sigils " + (@PKG@.GearCfg.SIG_ON ? "on (Anvil tab: " + IDS.length + " Sigils Unique .. Mythic, skip tiers, upward only; the Mythic Sigil " + (@PKG@.GearCfg.SIG_MY ? "allowed" : "refused (boss-only, sigil.mythicUse)") + "; never on the Bazaar; applied " + N[0] + ", refused " + N[1] + ", failed " + N[2] + ", market refusals " + N[3] + ")" : "OFF (part.sigils)");
}""")
''')

# ================================================================================================================ the Anvil: the Sigil strip
rep('''           "public int anTierV;", "public boolean anTierOk;", "public long anIdAt;"):''',
    '''           "public int anTierV;", "public boolean anTierOk;", "public long anIdAt;",
           # 0.3.4: the Sigil strip - the chosen Sigil (rank, 0 = the lowest that fits), the armed click (10 s, this exact item)
           "public int anSig;", "public long anSgArm;", "public String anSgFp;"):''')
after('''assert 92 + 1 + 328 + 1 + 8 + ANV_CARD_H == 656 and 92 + 1 + 278 + 50 + 1 + 8 + ANV_CARD_H == 656
''', '''# 0.3.4: the Sigil strip (50) takes its height from the lines column, also with the re-identify strip (lines 228: at most 8 lines)
assert 92 + 1 + 278 + 50 + 1 + 8 + ANV_CARD_H == 656 and 92 + 1 + 228 + 50 + 50 + 1 + 8 + ANV_CARD_H == 656 and 28 + 8 * 24 <= 228 - 6
assert 330 + 8 + 60 + 14 + 150 == 562, "the Sigil strip"          # fixer 2: a wider label (long reasons stay readable)
''')
before('''# the right column (562 x 656)
M(rpg, r"""
public void anPanel(''', '''# 0.3.4 the SIGIL strip (562 x 50, only while the player carries a Sigil): the chosen Sigil + what it does, Other (when several fit), Apply
# (arms) -> Confirm sigil (10 s, this exact item). Returns nothing; the clicks are "sg" / "sgn"
M(rpg, r"""
public int anSigPick(int[] ch) {
  if (ch.length == 0) return 0;
  for (int i = 0; i < ch.length; i++) if (ch[i] == this.anSig) return ch[i];
  return ch[0];
}""")
M(rpg, r"""
public void anSigil(@UCB@ b, @UEB@ ev, @IS@ sel, @BD@ d, int[] have) {
  int r = d == null ? 0 : @PKG@.GearData.rarity(d);
  int[] ch = @PKG@.GearSigil.choices(have, r);
  int R = anSigPick(ch);
  String why = R > 0 ? @PKG@.GearSigil.why(sel, d, R) : @PKG@.GearSigil.why(sel, d, 5);
  String txt;
  String col = @PKG@.GearDefs.C_LABEL;
  if (R == 0 && @PKG@.GearSigil.MYOFF.equals(why)) why = null;          // fixer 2: the Mythic refusal only when the player carries ONLY Mythic Sigils
  if (why == null && R == 0) why = have[5] > 0 && !@PKG@.GearCfg.SIG_MY && r < @PKG@.GearDefs.R_MY ? @PKG@.GearSigil.MYOFF : "Your Sigils are not above " + @PKG@.GearDefs.R_NAME[r] + ".";
  if (why != null) txt = why;          // fixer 2: no prefix and no tail - the strip stays readable (2 lines at 330 px)
  else {
    txt = @PKG@.GearDefs.R_NAME[R] + " Sigil (x" + have[R] + "): " + @PKG@.GearDefs.R_NAME[r] + " -> " + @PKG@.GearDefs.R_NAME[R].toUpperCase();
    col = rarHex(R);
  }
  boolean armed = why == null && this.anSgArm > 0L && System.currentTimeMillis() - this.anSgArm <= 10000L && this.anSgFp != null && this.anSgFp.equals(this.selFp);
  b.appendInline("#SkyyGAnvil", "Group #SkyyGSg { Anchor: (Height: 50); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyGSg", "Label #SkyyGSgTxt { Anchor: (Width: 330, Height: 44); Text: \\"\\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + col + ", VerticalAlignment: Center, Wrap: true, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12); }");
  b.set("#SkyyGSgTxt.Text", txt);
  b.appendInline("#SkyyGSg", "Group { Anchor: (Width: 8); }");
  if (why == null && ch.length > 1) {
    b.appendInline("#SkyyGSg", "TextButton #SkyyGBtnSgN { Anchor: (Width: 60, Height: 44); Text: \\"Other\\"; " + @PKG@.GearUi.btn(1) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnSgN", @EVD@.of("a", "sgn"));
  } else b.appendInline("#SkyyGSg", "Group { Anchor: (Width: 60); }");
  b.appendInline("#SkyyGSg", "Group { Anchor: (Width: 14); }");
  String bt = why != null ? "Cannot apply" : (armed ? "Confirm sigil" : "Apply sigil");
  b.appendInline("#SkyyGSg", "TextButton #SkyyGBtnSg { Anchor: (Width: 150, Height: 44); Text: \\"" + bt + "\\"; " + @PKG@.GearUi.btn(why != null ? 3 : (armed ? 2 : 0)) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnSg", @EVD@.of("a", "sg"));
}""")

''')
rep('''  boolean rr = !un && (this.selSec == 0 || this.selSec == 1 || this.selSec == 2) && @PKG@.GearUnid.rerollable(sel);
  anLines(b, sel, d, rr ? 278 : 328);
  if (rr) anReid(b, ev, u, sel, have);''', '''  boolean rr = !un && (this.selSec == 0 || this.selSec == 1 || this.selSec == 2) && @PKG@.GearUnid.rerollable(sel);
  // 0.3.4: the Sigil strip while the player carries any Sigil (an identified item that is no mystery bag)
  int[] sgh = null;
  if (!un && !@PKG@.GearUnid.isBox(sel.getItemId()) && @PKG@.GearCfg.SIG_ON) sgh = @PKG@.GearSigil.carried(inv);
  boolean sg = false;
  for (int k = 1; sgh != null && k < sgh.length; k++) if (sgh[k] > 0) sg = true;
  anLines(b, sel, d, 328 - (rr ? 50 : 0) - (sg ? 50 : 0));
  if (rr) anReid(b, ev, u, sel, have);
  if (sg) anSigil(b, ev, sel, d, sgh);''')
rep('''  if (a.equals("id")) { anId(inv); rebuild(); return true; }
  if (a.equals("rr")) { anReroll(inv); rebuild(); return true; }''', '''  if (a.equals("id")) { anId(inv); rebuild(); return true; }
  if (a.equals("sg") || a.equals("sgn")) { anSigDo(inv, a.equals("sgn")); rebuild(); return true; }          // 0.3.4 the Sigil strip
  if (a.equals("rr")) { anReroll(inv); rebuild(); return true; }''')
before('''# the Anvil's clicks; true = handled.''', '''# the clicks: Other = the next Sigil that fits; Apply = arm (10 s, this exact item), then GearSigil.apply (the item stays on the anvil)
M(rpg, r"""
public void anSigDo(@INV@ inv, boolean other) {
  if (this.selSec < 0) { this.info = "-Pick an item first."; return; }
  @IS@ it = @PKG@.GearStamp.at(inv, this.selSec, this.selSlot);
  if (!@PKG@.GearForge.same(it, this.selId, this.selFp)) { anClear(); this.info = "-The item on the anvil moved or changed - pick it again."; return; }
  @BD@ d = @PKG@.GearForge.docOf(this.selId, it.getMetadata());
  int r = d == null ? 0 : @PKG@.GearData.rarity(d);
  int[] ch = @PKG@.GearSigil.choices(@PKG@.GearSigil.carried(inv), r);
  int R = anSigPick(ch);
  if (other) {
    if (ch.length > 1) {
      int k = 0;
      for (int i = 0; i < ch.length; i++) if (ch[i] == R) k = i;
      this.anSig = ch[(k + 1) % ch.length];
      this.anSgArm = 0L;
      this.info = "=" + @PKG@.GearDefs.R_NAME[this.anSig] + " Sigil picked.";
    }
    return;
  }
  if (!anGuard("changed")) return;
  if (R == 0) { this.info = "-You carry no Sigil above " + @PKG@.GearDefs.R_NAME[r] + "."; return; }
  String why = @PKG@.GearSigil.why(it, d, R);
  if (why != null) { this.info = "-" + why; return; }
  long now = System.currentTimeMillis();
  if (this.anSgArm <= 0L || now - this.anSgArm > 10000L || this.anSgFp == null || !this.anSgFp.equals(this.selFp)) {
    this.anSgArm = now;
    this.anSgFp = this.selFp;
    this.info = "=Click Confirm sigil to spend one " + @PKG@.GearDefs.R_NAME[R] + " Sigil - it becomes " + @PKG@.GearDefs.R_NAME[R] + " (no way back).";
    return;
  }
  this.anSgArm = 0L;
  Object[] res = @PKG@.GearSigil.apply(inv, this.selSec, this.selSlot, this.selId, this.selFp, R, this.playerRef.getUuid(), this.playerRef.getUsername());
  int code = ((Integer) res[0]).intValue();
  if (code == 1 && res[2] instanceof @IS@) {
    @IS@ back = @PKG@.GearStamp.at(inv, this.selSec, this.selSlot);
    this.selFp = @PKG@.GearForge.fp(back != null && !back.isEmpty() ? back : (@IS@) res[2]);
    this.fresh = false; this.before = null; this.after = null; this.upMade = null; this.upMadeId = null; this.anRev = null;
    @BD@ nd = (@BD@) res[3];
    int lines = @PKG@.GearData.mods(nd).size();
    int slots = @PKG@.GearCfg.R_MODS[@PKG@.GearCfg.ri(R)];
    this.info = "+Your " + @PKG@.Gear.itemName(this.selId) + " is " + @PKG@.GearDefs.R_NAME[R] + " now" + (slots > lines ? " - " + (slots - lines) + " empty slot" + (slots - lines == 1 ? "" : "s") + ": Reforge it to fill them." : ".");
    return;
  }
  String msg = (String) res[1];
  if (msg != null && msg.startsWith("The item moved")) anClear();
  this.info = "-" + msg;
}""")
''')
# a new pick clears the chosen Sigil + the armed click
rep('''  this.anRev = null; this.anArm = 0L; this.anArmFp = null; this.anIdAt = 0L;          // fix round 2: a deliberate pick''',
    '''  this.anRev = null; this.anArm = 0L; this.anArmFp = null; this.anIdAt = 0L;          // fix round 2: a deliberate pick
  this.anSig = 0; this.anSgArm = 0L; this.anSgFp = null;          // 0.3.4''')

# ================================================================================================================ GearTill (2/2) + GearTillSys
TILL_PY = '''
# ================================================================= 0.3.4 THE HOE TILL AREA (GearTill 2/2 + GearTillSys; tools/gear_0_3_4_patch.py item 3). VERIFIED bytecode
# 2026-10-14: Hoe_Till = ChangeBlockInteraction.interactWithBlock (BlockOperations.setBlock, no event) -> ModifyInventory (held durability -1 via
# ItemContainer.setItemStackForSlot -> InventoryChangeEvent with a SlotTransaction). The Changes map is read from Assets.zip here.
_hti = json.loads(AZ.read("Server/Item/Interactions/Weapons/Hoe/Attacks/Till/Hoe_Till.json").decode("utf-8-sig"))
assert _hti.get("Type") == "ChangeBlock" and _hti.get("Next", {}).get("AdjustHeldItemDurability") == -1, "vanilla Hoe_Till changed shape: %s" % _hti.get("Type")
TILL_FROM = sorted(_hti["Changes"])
TILL_TO = sorted(set(_hti["Changes"].values()))
assert TILL_TO == ["Soil_Dirt_Tilled"] and len(TILL_FROM) >= 10 and "Soil_Grass" in TILL_FROM and "Soil_Dirt" in TILL_FROM
_hr = json.loads(AZ.read("Server/Item/Items/Tool/Hoe/Tool_Hoe_Crude.json").decode("utf-8-sig"))
assert _hr["Interactions"]["Secondary"] == "Hoe_Till", "the Crude hoe's Secondary is not Hoe_Till any more"
TI = {"TGU": "com.hypixel.hytale.server.core.util.TargetUtil",
      "BOPS": "com.hypixel.hytale.server.core.universe.world.chunk.BlockOperations",
      "SLTX": "com.hypixel.hytale.server.core.inventory.transaction.SlotTransaction",
      "TOOLC": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Tool",
      "HOTC": "com.hypixel.hytale.server.core.inventory.InventoryComponent$Hotbar",
      "BSECT": "com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection",
      "CHST": "com.hypixel.hytale.server.core.universe.world.storage.ChunkStore",
      "BTYP": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
      "SBS": "com.hypixel.hytale.server.core.universe.world.SetBlockSettings",
      "V3I": "org.joml.Vector3i"}
for _k in TI:
    assert _k not in T, "0.3.4 token clashes: " + _k
T.update(TI)
for _c, _m in ((TI["TGU"], "getTargetBlock"), (TI["BOPS"], "setBlock"), (TI["SLTX"], "getSlotBefore"), (TI["SLTX"], "getSlotAfter"),
               (TI["TOOLC"], "getComponentType"), (TI["HOTC"], "getComponentType"), (TI["BSECT"], "get"), (TI["BSECT"], "getComponentType"),
               (TI["CHST"], "getChunkSectionReferenceAtBlock"), (TI["CHST"], "getStore"), (TI["BTYP"], "getAssetMap"), (TI["V3I"], "x"),
               (TI["BSECT"], "getRotationIndex"),
               (ICE, "getTransaction"), (ICE, "getComponentType"), (EST, "getWorld"), (IS, "getDurability")):
    B.probe(pool, _c, _m)
_tgs = [str(_m.getSignature()) for _m in pool.get(TI["TGU"]).getDeclaredMethods() if str(_m.getName()) == "getTargetBlock"]
assert "(Lcom/hypixel/hytale/component/Ref;DLcom/hypixel/hytale/component/ComponentAccessor;)Lorg/joml/Vector3i;" in _tgs, _tgs
_sbs = [str(_m.getSignature()) for _m in pool.get(TI["BOPS"]).getDeclaredMethods() if str(_m.getName()) == "setBlock"]
assert "(Lcom/hypixel/hytale/server/core/universe/world/storage/ChunkStore;Lcom/hypixel/hytale/component/Ref;IIIILcom/hypixel/hytale/server/core/asset/type/blocktype/config/BlockType;III)Z" in _sbs, _sbs
# fixer 2 (VERIFIED bytecode 2026-10-14): vanilla ChangeBlockInteraction.interactWithBlock calls setBlock(cs, ref, x, y, z, newId, type,
# BlockSection.getRotationIndex(x, y, z), 0, 256) - 256 = SetBlockSettings.PERFORM_BLOCK_UPDATE; the extra blocks use the same arguments
assert int(pool.get(TI["SBS"]).getField("PERFORM_BLOCK_UPDATE").getConstantValue()) == 256, "SetBlockSettings.PERFORM_BLOCK_UPDATE is not 256 any more"
F(gtill, "public static final String[] FROM = %s;" % jarr(TILL_FROM))
F(gtill, 'public static final String TO = "%s";' % TILL_TO[0])
F(gtill, "public static volatile int[] IDX = null;")          # FROM's block indexes (resolved once the block map is loaded)
F(gtill, "public static volatile int TOI = -1;")
F(gtill, "public static volatile int EMPTY = -1;")
F(gtill, "public static volatile String AREA_SRC = null;")
F(gtill, "public static volatile int[] AREA = new int[] { 1, 3, 3, 5, 5, 7, 7, 9 };")
F(gtill, "public static volatile java.util.function.Function PERM = null;")          # HARNESS SEAM ONLY: island:perm:fn stand-in
F(gtill, "public static volatile java.util.function.Function TARGET = null;")          # HARNESS SEAM ONLY: Ref -> Vector3i (TargetUtil)
F(gtill, "public static volatile java.util.function.Function BLK = null;")          # HARNESS SEAM ONLY: Object[] { x, y, z } -> Integer block id
F(gtill, "public static volatile java.util.function.Function SETB = null;")          # HARNESS SEAM ONLY: Object[] { x, y, z, id, rotation, settings } -> Boolean (BlockOperations)
F(gtill, "public static final int SETF = 256;")          # fixer 2: SetBlockSettings.PERFORM_BLOCK_UPDATE, as the vanilla till (asserted at build time)
F(gtill, "public static volatile String LASTWHY = \\"\\";")
F(gtill, "public static final long[] N = new long[6];")          # 0 tills seen, 1 extra blocks tilled, 2 refused (protection), 3 skipped (a hit), 4 not a till, 5 write fails
# hoe.area: 8 odd numbers 1-9 (Crude .. Onyxium); null = fine (Server Setup check=)
M(gtill, r"""
public static int[] parseArea(String v) {
  if (v == null) return null;
  String[] p = v.split(",");
  if (p.length != 8) return null;
  int[] a = new int[8];
  for (int i = 0; i < 8; i++) {
    try { a[i] = Integer.parseInt(p[i].trim()); } catch (Throwable t) { return null; }
    if (a[i] < 1 || a[i] > 9 || a[i] % 2 == 0) return null;
  }
  return a;
}""")
M(gtill, r"""
public static String checkArea(String key, String value) {
  return parseArea(value) == null ? "Till square per hoe tier: 8 odd numbers from 1 to 9 (Crude, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium), joined by commas." : null;
}""")
M(gtill, r"""
public static int side(int tier) {
  String v = @PKG@.GearCfg.HOE_AREA;
  if (v != null && !v.equals(AREA_SRC)) {
    int[] a = parseArea(v);
    if (a == null) @PKG@.Gear.warnOnce("hoearea:" + v.hashCode(), "config.properties: hoe.area '" + v + "' is not 8 odd numbers 1-9 - the default 1,3,3,5,5,7,7,9 applies");
    AREA = a == null ? new int[] { 1, 3, 3, 5, 5, 7, 7, 9 } : a;
    AREA_SRC = v;
  }
  int[] a2 = AREA;
  if (tier < 0) tier = 0;
  if (tier >= a2.length) tier = a2.length - 1;
  return a2[tier];
}""")
M(gtill, r"""
public static boolean resolve() {
  if (IDX != null && TOI >= 0) return true;
  try {
    int[] ix = new int[FROM.length];
    for (int i = 0; i < FROM.length; i++) ix[i] = @BTYP@.getAssetMap().getIndex(FROM[i]);
    int t = @BTYP@.getAssetMap().getIndex(TO);
    int e = @BTYP@.getAssetMap().getIndex("Empty");
    if (t == Integer.MIN_VALUE || t < 0) return false;
    EMPTY = e == Integer.MIN_VALUE ? 0 : e;
    IDX = ix;
    TOI = t;
    return true;
  } catch (Throwable x) { return false; }
}""")
M(gtill, r"""
public static boolean tillable(int id) {
  int[] ix = IDX;
  if (ix == null || id < 0) return false;
  for (int i = 0; i < ix.length; i++) if (ix[i] == id) return true;
  return false;
}""")
# block id at world x, y, z (-1 = the section is not loaded - never loads anything)
M(gtill, r"""
public static int blockAt(@CHST@ cs, int x, int y, int z) {
  if (y < 0 || y >= 320) return -1;
  java.util.function.Function sb = BLK;
  if (sb != null) { Object o = sb.apply(new Object[] { Integer.valueOf(x), Integer.valueOf(y), Integer.valueOf(z) }); return o instanceof Integer ? ((Integer) o).intValue() : -1; }
  @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
  if (r == null || !r.isValid()) return -1;
  @BSECT@ bs = (@BSECT@) cs.getStore().getComponent(r, @BSECT@.getComponentType());
  return bs == null ? -1 : bs.get(x, y, z);
}""")
# fixer 2: the rotation index of the block at x, y, z (0 = unknown / the BLK seam), as the vanilla till passes it to setBlock
M(gtill, r"""
public static int rotAt(@CHST@ cs, int x, int y, int z) {
  if (BLK != null || cs == null) return 0;
  try {
    @REF@ r = cs.getChunkSectionReferenceAtBlock(x, y, z);
    if (r == null || !r.isValid()) return 0;
    @BSECT@ bs = (@BSECT@) cs.getStore().getComponent(r, @BSECT@.getComponentType());
    return bs == null ? 0 : bs.getRotationIndex(x, y, z);
  } catch (Throwable t) { return 0; }
}""")
# the protection answer for this player in this world: 1 = till, 0 = refused (only the vanilla block). Island worlds: SkyyIslands'
# island:perm:fn "build" (TRUE / FALSE); any other world (null = not an island): hoe.areaElsewhere
M(gtill, r"""
public static int allowed(java.util.UUID u, String world) {
  java.util.function.Function f = PERM != null ? PERM : @PKG@.Gear.fn("island:perm:fn");
  Object r = null;
  if (f != null && u != null && world != null) {
    try { r = f.apply(new Object[] { u, world, "build" }); } catch (Throwable t) { r = Boolean.FALSE; }
  }
  if (r instanceof Boolean) return ((Boolean) r).booleanValue() ? 1 : 0;
  return @PKG@.GearCfg.HOE_ELSE ? 1 : 0;
}""")
# the extra blocks around a freshly tilled (cx, cy, cz): side x side on the same layer, tillable + air above, loaded sections only; returns
# how many were tilled
M(gtill, r"""
public static int area(@WLD@ w, int cx, int cy, int cz, int side) {
  if (w == null || side <= 1 || !resolve()) return 0;
  @CHST@ cs = w.getChunkStore();
  @BTYP@ to = null;
  int h = side / 2;
  int n = 0;
  for (int dx = -h; dx <= h; dx++) {
    for (int dz = -h; dz <= h; dz++) {
      if (dx == 0 && dz == 0) continue;
      int x = cx + dx;
      int z = cz + dz;
      int id = blockAt(cs, x, cy, z);
      if (!tillable(id)) continue;
      int up = blockAt(cs, x, cy + 1, z);
      if (up != EMPTY && up != 0) continue;
      boolean ok = false;
      int rot = rotAt(cs, x, cy, z);          // fixer 2: the vanilla till's arguments (rotation, filler 0, PERFORM_BLOCK_UPDATE)
      java.util.function.Function sw = SETB;
      if (sw != null) ok = Boolean.TRUE.equals(sw.apply(new Object[] { Integer.valueOf(x), Integer.valueOf(cy), Integer.valueOf(z), Integer.valueOf(TOI), Integer.valueOf(rot), Integer.valueOf(SETF) }));
      else {
        if (to == null) to = (@BTYP@) @BTYP@.getAssetMap().getAsset(TOI);
        if (to == null || cs == null) return n;
        @REF@ r = cs.getChunkSectionReferenceAtBlock(x, cy, z);
        if (r == null || !r.isValid()) continue;
        try { ok = @BOPS@.setBlock(cs, r, x, cy, z, TOI, to, rot, 0, SETF); } catch (Throwable t) { ok = false; }
      }
      if (ok) n++; else N[5] = N[5] + 1L;
    }
  }
  return n;
}""")
# THE TILL (GearTillSys, world thread): the held hoe of the event's slot lost exactly durability 1, same id + same lifelong uid, it is YOUR
# lifelong hoe, no block hit in the last 300 ms, the block you look at is tilled soil -> the area. Returns the extra blocks (-1 = not a till)
M(gtill, r"""
public static int onChange(@PR@ pr, @REF@ ref, @CB@ cb, @WLD@ w, @IS@ before, @IS@ after) {
  if (!@PKG@.GearCfg.HOE_ON || pr == null || before == null || after == null || before.isEmpty() || after.isEmpty()) return -1;
  String id = after.getItemId();
  if (@PKG@.GearLL.kOf(id) != 2 || !id.equals(before.getItemId())) return -1;
  double dd = before.getDurability() - after.getDurability();
  if (dd < 0.5 || dd > 1.5) return -1;
  java.util.UUID u = pr.getUuid();
  @BD@ d = null;
  try { d = @PKG@.GearData.gearDoc(after.getMetadata()); } catch (Throwable t0) { d = null; }
  if (!@PKG@.GearLL.mine(u, d)) { LASTWHY = "not your lifelong hoe"; return -1; }
  @BD@ d0 = null;
  try { d0 = @PKG@.GearData.gearDoc(before.getMetadata()); } catch (Throwable t1) { d0 = null; }
  if (d0 == null || !@PKG@.GearLL.uid(d0).equals(@PKG@.GearLL.uid(d))) { LASTWHY = "another stack"; return -1; }
  Object hm = HIT.get(u);
  long now = System.currentTimeMillis();
  if (hm instanceof Long && now >= ((Long) hm).longValue() && now - ((Long) hm).longValue() < 300L) { N[3] = N[3] + 1L; LASTWHY = "a block hit"; return -1; }
  int side = side(@PKG@.GearLL.tier(id));
  if (side <= 1) { LASTWHY = "tier " + @PKG@.GearLL.tier(id) + " tills one block"; return 0; }
  if (w == null || !resolve()) { LASTWHY = "no world / block map"; return -1; }
  @V3I@ tb = null;
  try { tb = TARGET != null ? (@V3I@) TARGET.apply(ref) : @TGU@.getTargetBlock(ref, 8.0, cb); } catch (Throwable t2) { tb = null; }
  if (tb == null) { N[4] = N[4] + 1L; LASTWHY = "no target block"; return -1; }
  int x = tb.x();
  int y = tb.y();
  int z = tb.z();
  if (blockAt(w.getChunkStore(), x, y, z) != TOI) { N[4] = N[4] + 1L; LASTWHY = "the target is no tilled soil"; return -1; }
  N[0] = N[0] + 1L;
  if (allowed(u, w.getName()) != 1) { N[2] = N[2] + 1L; LASTWHY = "protected (" + w.getName() + ")"; return 0; }
  int n = area(w, x, y, z, side);
  N[1] = N[1] + (long) n;
  LASTWHY = "tilled " + n + " around " + x + "," + y + "," + z + " (" + side + "x" + side + ")";
  return n;
}""")
M(gtill, r"""
public static String statusText() {
  return "hoe till area " + (@PKG@.GearCfg.HOE_ON ? "on (lifelong hoe, side by tier " + @PKG@.GearCfg.HOE_AREA + ", " + (@PKG@.GearCfg.HOE_ELSE ? "any world" : "island worlds where you may build") + "; tills " + N[0] + ", extra blocks " + N[1] + ", protected " + N[2] + ")" : "OFF (hoe.areaOn)");
}""")
gtis = mk("GearTillSys", EES)
G34_CLASSES.append(gtis)
event_system(gtis, "GearTillSys", ICE, PLAYER_Q, r"""
    if (!@PKG@.GearCfg.HOE_ON || !(ev instanceof @ICE@)) return;
    @ICE@ e = (@ICE@) ev;
    if (e.getComponentType() != @HOTC@.getComponentType() && e.getComponentType() != @TOOLC@.getComponentType()) return;
    Object tx = e.getTransaction();
    if (!(tx instanceof @SLTX@)) return;
    @SLTX@ s = (@SLTX@) tx;
    @PR@ pr = (@PR@) chunk.getComponent(idx, @PR@.getComponentType());
    if (pr == null) return;
    @WLD@ w = null;
    try { w = ((@EST@) st.getExternalData()).getWorld(); } catch (Throwable tw) { w = null; }
    @PKG@.GearTill.onChange(pr, chunk.getReferenceTo(idx), buf, w, s.getSlotBefore(), s.getSlotAfter());""")
print("0.3.4 hoe till area: %d tillable blocks -> %s, sides %s by tier (GearTillSys on InventoryChangeEvent)" % (len(TILL_FROM), TILL_TO[0], HOE_AREA_DEF))
'''
before('''# ================================================================= plugin (spec Appendix A setup() order)''', TILL_PY)
rep('''                                                        # 0.3.0 lifelong tools: the Drop key on a lifelong tool
                                                        "GearLLDropSys")))''', '''                                                        # 0.3.0 lifelong tools: the Drop key on a lifelong tool
                                                        "GearLLDropSys",
                                                        # 0.3.4 the hoe till area (the hoe's durability change after a till)
                                                        "GearTillSys")))''')
rep('''@PKG@.GearLL.statusText() + "; gear:fn:curve''', '''@PKG@.GearLL.statusText() + "; " + @PKG@.GearSigil.statusText() + "; " + @PKG@.GearArmLv.statusText() + "; " + @PKG@.GearTill.statusText() + "; gear:fn:curve''')
rep('''+ ANVIL_CLASSES + LIFE_CLASSES
assert len(set(''', '''+ ANVIL_CLASSES + LIFE_CLASSES + G34_CLASSES
assert len(set(''')
rep('''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS)), "SkyyGear 0.2.16 ships the 8 mystery bags + the 16 Untiered copies"''',
    '''    assert sorted(n for n in _names if n.startswith("Server/Item/Items/")) == sorted(list(BAG_ITEMS) + list(UT_ITEMS) + list(SIG_ITEMS)), "SkyyGear 0.3.4 ships the 8 mystery bags + the 16 Untiered copies + the 5 Sigils"
    for _k, _v in list(SIG_ITEMS.items()) + list(SIG_FILES.items()):          # 0.3.4
        assert _jz.read(_k) == (_v.encode("utf-8") if isinstance(_v, str) else _v), "Sigil file missing from the jar: " + _k''')
rep('''a crop two tiers above your hoe is refused; no tool no logs or ore); Server Setup -> Gear.''',
    '''a crop two tiers above your hoe is refused; no tool no logs or ore); SIGILS (Unique .. Mythic) raise an item's rarity on the Anvil, skipping tiers (never sold on the Bazaar; Mythic stays boss-only unless the server allows the Mythic Sigil); Mining armor levels with your Mining level and tiers up on the Anvil keeping its rarity; your lifelong hoe tills a bigger square the higher its tier; Server Setup -> Gear.''')
# the join / leave forget
rep('''    @PKG@.GearLL.forget(u);     // 0.3.0: the slow popup / sweep / chat-line clocks''',
    '''    @PKG@.GearLL.forget(u);     // 0.3.0: the slow popup / sweep / chat-line clocks
    @PKG@.GearArmLv.forget(u);     // 0.3.4
    @PKG@.GearTill.forget(u);     // 0.3.4''')

# ================================================================================================================ checks on the result
assert s.count("GearSigil.apply(") == 1 and s.count("GearArmLv.sync(") == 1 and s.count("GearTill.onChange(") == 1 and s.count("GearTill.hitMark(") == 1
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.3 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.3 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
