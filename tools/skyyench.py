"""skyyench - THE ENCHANTED MATERIALS TABLE (Gathering-Shards-Spec phase 1 = research/Gathering-Progression-Spec.md phase A + Skyy's
2026-10-06 updates). ONE source of truth for every jar that knows the Enchanted items:

    SkyyCollections 0.2.11+  ships the items (asset pack: item JSON + recipe, quality, icons, textures, the cube model), the Workbench tab
                             "Compressing" (runtime append, emit_tab), the unlock tiers (merged at validate like the Lantern rows), the
                             recipe knowledge sync and the coll:fn:add alias (credit = base x RATIO)
    SkyySacks 0.8.1+         SackDefs.homeOf: Skyy_Ench_<Key> -> the Void category of its base (sacks_home_java)
    SkyyBazaar 0.1.10+       a product per item, priced as a PROCESSED good from its recipe (100 x the input's raw value x (1 + premium))

Skyy's words this follows (docs/answered/bags.md + gear.md, word for word there):
  - 2026-10-05 "i want to use sky blocks enchanted iron and enchanted cobble. (basically compressed materials.)"
  - 2026-10-06 spec Q3 "Always 100" (100 base = 1 Enchanted), Q4 launch with 18 Enchanted items, no Enchanted Blocks yet
  - 2026-10-06 art review: "they should be enchanted ingots, not ore ... the only one that makes sense is rubble ... all kinda of rubble
    count towards rubble ... in the game the logs are blocks! just do an enchanted looking version of the same resource! a shiny coppy of
    the vanilla block." -> metals from INGOTS, stone = Cobblestone + Rubble (any rubble), one Enchanted log per key log
  - 2026-10-06 spec Q10 tweak "Enchanted premium" -> sold a bit ABOVE 100x base, capped below any loop (the processed-goods 22% rule)
  - 2026-10-11 UPGRADE COST "it costs a enchanted iron ingot to upgrade copper to iron" (phase 3 spends them; this phase makes them)

Rules kept here (the build scripts assert them):
  - RATIO 100 is a BUILD-TIME constant (a runtime ratio could not change the baked recipe and would mis-credit items players hold).
  - No reverse recipe, ever (no un-compress, no salvage output).
  - Crafting is never a collection credit (the base items counted when gathered); only a GIVER that creates an Enchanted item credits it,
    through SkyyCollections' coll:fn:add alias (base x RATIO, once, at creation).
  - Icons / textures are a "shiny copy of the vanilla resource", GENERATED at build time from Assets.zip (nothing vanilla is committed).
  - Pure Python, deterministic (same Assets.zip -> same bytes).
"""
import os, json, copy

ENCH_VERSION = "1"            # bump when the table or the runtime tab protocol changes
RATIO = 100                   # Skyy 2026-10-06 "Always 100"
STACK = 100                   # Skyy: "use Hytale stack numbers"
PREFIX = "Skyy_Ench_"
RECIPE_SUFFIX = "_Recipe_Generated_0"
QUALITY = "Skyy_Enchanted"    # own quality: the vanilla Epic texture set + drop glow, label "Enchanted"
QUALITY_LABEL = "Enchanted"
QUALITY_COLOR = "#c77dff"
QUALITY_VALUE = 4             # = vanilla Epic; below SkyyAuctions' technical threshold (8)
TAB_ID = "Workbench_SkyyCompressing"
TAB_NAME_KEY = "server.benchCategories.workbench.skyycompressing"
TAB_TEXT = "Compressing"
TAB_LANG = ["benchCategories.workbench.skyycompressing=" + TAB_TEXT, TAB_NAME_KEY + "=" + TAB_TEXT]
BENCH_ID = "Workbench"
ART_DIR = "SkyyCollections/Ench"          # Common/<...> for textures / the cube model; icons in Icons/ItemsGenerated/

# (Key, input kind I = item / R = resource type, input id, collection id, default unlock tier, Void category, display name, look)
# Unlock tiers = Gathering-Progression-Spec 3.2 grammar: tier III on the S / R / B curves, tier II on the E curve (Adamantite).
# look: ("ingot", metal) | ("cube", base block item) | ("rubble", base item) | ("crop", base crop item)
TABLE = [
    ("Cobblestone", "I", "Rock_Stone_Cobble",      "Cobblestone", 3, "Mining",   "Enchanted Cobblestone",      ("cube", "Rock_Stone_Cobble")),
    ("Rubble",      "R", "Rubble",                 "Rubble",      3, "Mining",   "Enchanted Rubble",           ("rubble", "Rubble_Stone")),
    ("Copper",      "I", "Ingredient_Bar_Copper",  "Copper",      3, "Mining",   "Enchanted Copper Ingot",     ("ingot", "Ingredient_Bar_Copper")),
    ("Iron",        "I", "Ingredient_Bar_Iron",    "Iron",        3, "Mining",   "Enchanted Iron Ingot",       ("ingot", "Ingredient_Bar_Iron")),
    ("Thorium",     "I", "Ingredient_Bar_Thorium", "Thorium",     3, "Mining",   "Enchanted Thorium Ingot",    ("ingot", "Ingredient_Bar_Thorium")),
    ("Cobalt",      "I", "Ingredient_Bar_Cobalt",  "Cobalt",      3, "Mining",   "Enchanted Cobalt Ingot",     ("ingot", "Ingredient_Bar_Cobalt")),
    ("Adamantite",  "I", "Ingredient_Bar_Adamantite", "Adamantite", 2, "Mining", "Enchanted Adamantite Ingot", ("ingot", "Ingredient_Bar_Adamantite")),
    ("Oak",         "I", "Wood_Oak_Trunk",         "OakLog",      3, "Foraging", "Enchanted Oak Log",          ("cube", "Wood_Oak_Trunk")),
    ("Maple",       "I", "Wood_Maple_Trunk",       "MapleLog",    3, "Foraging", "Enchanted Maple Log",        ("cube", "Wood_Maple_Trunk")),
    ("Gumboab",     "I", "Wood_Gumboab_Trunk",     "GumboabLog",  3, "Foraging", "Enchanted Gumboab Log",      ("cube", "Wood_Gumboab_Trunk")),
    ("Redwood",     "I", "Wood_Redwood_Trunk",     "RedwoodLog",  3, "Foraging", "Enchanted Redwood Log",      ("cube", "Wood_Redwood_Trunk")),
    ("Sallow",      "I", "Wood_Sallow_Trunk",      "SallowLog",   3, "Foraging", "Enchanted Sallow Log",       ("cube", "Wood_Sallow_Trunk")),
    ("Wheat",       "I", "Plant_Crop_Wheat_Item",  "Wheat",       3, "Farming",  "Enchanted Wheat",            ("crop", "Plant_Crop_Wheat_Item")),
    ("Carrot",      "I", "Plant_Crop_Carrot_Item", "Carrot",      3, "Farming",  "Enchanted Carrot",           ("crop", "Plant_Crop_Carrot_Item")),
    ("Cauliflower", "I", "Plant_Crop_Cauliflower_Item", "Cauliflower", 3, "Farming", "Enchanted Cauliflower",  ("crop", "Plant_Crop_Cauliflower_Item")),
    ("Pumpkin",     "I", "Plant_Crop_Pumpkin_Item", "Pumpkin",    3, "Farming",  "Enchanted Pumpkin",          ("crop", "Plant_Crop_Pumpkin_Item")),
    ("Tomato",      "I", "Plant_Crop_Tomato_Item", "Tomato",      3, "Farming",  "Enchanted Tomato",           ("crop", "Plant_Crop_Tomato_Item")),
    ("Cotton",      "I", "Plant_Crop_Cotton_Item", "Cotton",      3, "Farming",  "Enchanted Cotton",           ("crop", "Plant_Crop_Cotton_Item")),
    ("Potato",      "I", "Plant_Crop_Potato_Item", "Potato",      3, "Farming",  "Enchanted Potato",           ("crop", "Plant_Crop_Potato_Item")),
    # round tools01 (Skyy 2026-10-16 "make enchanted sticks too, and require them in the later tool upgrades."): same ratio + place as the
    # others (100 Sticks -> 1, Workbench Compressing tab, unlocked at Stick collection tier III); the stick is an item (no block) -> the
    # "ingot" look path (its own model + a shiny copy of its texture). Its Void category is Foraging (SkyySacks reads this table at build).
    ("Stick",       "I", "Ingredient_Stick",       "Stick",       3, "Foraging", "Enchanted Stick",            ("ingot", "Ingredient_Stick")),
]
KEYS = [t[0] for t in TABLE]
IDS = [PREFIX + k for k in KEYS]
RIDS = [i + RECIPE_SUFFIX for i in IDS]
CATS = ("Mining", "Foraging", "Farming")
assert len(TABLE) == 20 and len(set(KEYS)) == 20 and all(t[5] in CATS for t in TABLE)          # tools01: + the Enchanted Stick (was 19)
assert all(t[1] in ("I", "R") and 1 <= t[4] <= 3 for t in TABLE)
for _t in TABLE:
    assert all(c.isalnum() for c in _t[0]) and '"' not in _t[6] and "\\" not in _t[6] and "|" not in _t[6], _t


def row(key):
    for t in TABLE:
        if t[0] == key:
            return t
    return None


def cat_of(item_id):
    """the Python mirror of the Java SackDefs.enchCat (SkyySacks 0.8.1): the Void category of an Enchanted id, else None"""
    if not isinstance(item_id, str) or not item_id.startswith(PREFIX):
        return None
    t = row(item_id[len(PREFIX):])
    return t[5] if t else None


def tier_key(key):
    return "ench.tier." + key.lower()


def _jarr(vals):
    return "new String[] { " + ", ".join('"%s"' % v for v in vals) + " }"


def sacks_home_java():
    """the SackDefs method SkyySacks 0.8.1 compiles: enchCat(id) -> the category of a KNOWN Enchanted id, null otherwise (an unknown
    Skyy_Ench_ id is never stored: it belongs to no category)"""
    return ("public static String enchCat(String itemId) {\n"
            "  if (itemId == null || !itemId.startsWith(\"%s\")) return null;\n"
            "  String[] ids = %s;\n"
            "  String[] cats = %s;\n"
            "  for (int i = 0; i < ids.length; i++) if (ids[i].equals(itemId)) return cats[i];\n"
            "  return null;\n"
            "}") % (PREFIX, _jarr(IDS), _jarr([t[5] for t in TABLE]))


# ================================================================================================================ art (build time)
def _shine(img, outline):
    """the "shiny copy": brighter, a violet enchant tint, two diagonal glints; outline = a soft violet rim around the silhouette (icons)"""
    w, h = img.w, img.h
    out = img.copy()
    src = img
    for y in range(h):
        for x in range(w):
            r, g, b, a = src.get(x, y)
            if a == 0:
                continue
            m = (r + g + b) / 3.0
            r, g, b = m + (r - m) * 1.25, m + (g - m) * 1.25, m + (b - m) * 1.25      # a little more colour
            r, g, b = r * 1.08 + 6, g * 1.08 + 6, b * 1.08 + 6                        # a little brighter
            t = 0.07
            r, g, b = r * (1 - t) + 199 * t, g * (1 - t) + 125 * t, b * (1 - t) + 255 * t   # a hint of the enchant violet
            d = (x + (h - 1 - y)) / float(w + h)
            glint = 0.0
            for c0, half, k in ((0.40, 0.035, 0.50), (0.60, 0.018, 0.35)):
                e = abs(d - c0)
                if e < half:
                    glint = max(glint, k * (1.0 - e / half))
            r, g, b = r + (255 - r) * glint, g + (255 - g) * glint, b + (255 - b) * glint
            out.put(x, y, (_c8(r), _c8(g), _c8(b), a))
    if outline:
        for y in range(h):
            for x in range(w):
                if src.get(x, y)[3] >= 64:
                    continue
                near = 0
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and src.get(xx, yy)[3] >= 128:
                        near += 1
                if near:
                    out.put(x, y, (205, 130, 255, 110 + 30 * min(near, 3)))
    return out


def _c8(v):
    v = int(round(v))
    return 0 if v < 0 else (255 if v > 255 else v)


def _items(z):
    out = {}
    for n in z.namelist():
        if n.startswith("Server/Item/Items/") and n.endswith(".json"):
            try:
                out[n.rsplit("/", 1)[1][:-5]] = json.loads(z.read(n).decode("utf-8-sig"))
            except Exception:
                pass
    return out


def _inh(items, i, k):
    seen = set()
    x = items.get(i)
    while x is not None and i not in seen:
        seen.add(i)
        if k in x:
            return x[k]
        i = x.get("Parent")
        x = items.get(i) if i else None
    return None


def _cube_model(z, SA):
    """the Enchanted cube model: Assets.zip Blocks/Structures/Base_Shapes/Cube_Overlay.blockymodel (ONE 32-unit box) re-laid out at build
    time: the four sides read the texture's left 32x32, top + bottom its right 32x32, the box drawn at half a block (stretch 0.5)"""
    m = json.loads(SA._read(z, "Blocks/Structures/Base_Shapes/Cube_Overlay.blockymodel").decode("utf-8-sig"))
    assert len(m["nodes"]) == 1 and m["nodes"][0]["shape"]["type"] == "box", "Cube_Overlay changed"
    m = copy.deepcopy(m)
    sh = m["nodes"][0]["shape"]
    sh["settings"]["size"] = {"x": 32, "y": 32, "z": 32}
    sh["stretch"] = {"x": 0.5, "y": 0.5, "z": 0.5}
    m["nodes"][0]["position"] = {"x": 0, "y": 8, "z": 0}
    m["nodes"][0]["name"] = "SkyyEnchCube"
    lay = sh["textureLayout"]
    for f in ("front", "back", "left", "right", "top", "bottom"):
        assert f in lay, "Cube_Overlay textureLayout lost face " + f
        lay[f] = {"offset": {"x": 32 if f in ("top", "bottom") else 0, "y": 0}, "mirror": {"x": False, "y": False}, "angle": 0}
    return json.dumps(m, indent=2).encode("utf-8")


def build_assets(z, SA):
    """{jar path: bytes | str} for SkyyCollections (Server/... JSON as str, Common/... art as bytes) + the lang lines.
    z = Assets.zip (read-only), SA = tools/skyyart.py."""
    items = _items(z)
    files, lang = {}, []
    cube_rel = "Items/%s/EnchCube.blockymodel" % ART_DIR
    files["Common/" + cube_rel] = _cube_model(z, SA)
    for (key, kind, inp, coll, tier, cat, name, look) in TABLE:
        eid = PREFIX + key
        lk, base = look
        assert base in items, "Enchanted %s: base %s is not in Assets.zip" % (key, base)
        icon_src = _inh(items, base, "Icon")
        icon = SA.png_encode(_shine(SA.png_decode(SA._read(z, icon_src)), True))
        assert SA.png_size(icon) == (64, 64), (key, SA.png_size(icon))
        icon_rel = "Icons/ItemsGenerated/SkyyCollections_Ench_%s.png" % key
        files["Common/" + icon_rel] = icon
        tex_rel = "Items/%s/%s.png" % (ART_DIR, key)
        props = None
        if lk == "ingot":
            model = _inh(items, base, "Model")
            tex = SA.png_encode(_shine(SA.png_decode(SA._read(z, _inh(items, base, "Texture"))), False))
            props = _inh(items, base, "IconProperties")
            sound = _inh(items, base, "ItemSoundSetId")
        elif lk == "cube":
            bt = _inh(items, base, "BlockType")
            t0 = bt["Textures"][0]
            side, top = SA.png_decode(SA._read(z, t0["Sides"])), SA.png_decode(SA._read(z, t0["UpDown"]))
            assert (side.w, side.h, top.w, top.h) == (32, 32, 32, 32), (key, side.w, side.h, top.w, top.h)
            atlas = SA.Img(64, 32)
            for y in range(32):
                for x in range(32):
                    atlas.put(x, y, side.get(x, y))
                    atlas.put(32 + x, y, top.get(x, y))
            tex = SA.png_encode(_shine(atlas, False))
            model = cube_rel
            props = {"Scale": 1, "Translation": [0, -3], "Rotation": [22.5, 45, 22.5]}
            sound = _inh(items, base, "ItemSoundSetId")
        else:   # rubble / crop: the vanilla block's own CustomModel + a shiny copy of its first texture
            bt = _inh(items, base, "BlockType")
            model = bt["CustomModel"]
            tex = SA.png_encode(_shine(SA.png_decode(SA._read(z, bt["CustomModelTexture"][0]["Texture"])), False))
            props = _inh(items, base, "IconProperties") or {"Scale": 1, "Translation": [0, -3], "Rotation": [22.5, 45, 22.5]}
            sound = _inh(items, base, "ItemSoundSetId")
        files["Common/" + tex_rel] = tex
        node = {
            "TranslationProperties": {"Name": "server.items.%s.name" % eid, "Description": "server.items.%s.description" % eid},
            "Categories": ["Items"],
            "Quality": QUALITY,
            "Icon": icon_rel,
            "Model": model,
            "Texture": tex_rel,
            "IconProperties": props,
            "PlayerAnimationsId": "Item",
            "MaxStack": STACK,
            "Tags": {"Type": ["Ingredient"]},
            "DropOnDeath": True,
            "Recipe": {
                "Input": [{"ItemId": inp, "Quantity": RATIO}] if kind == "I" else [{"ResourceTypeId": inp, "Quantity": RATIO}],
                "BenchRequirement": [{"Type": "Crafting", "Id": BENCH_ID, "Categories": [TAB_ID]}],
                "OutputQuantity": 1,
                "TimeSeconds": 1,
                "KnowledgeRequired": True,
            },
        }
        if sound:
            node["ItemSoundSetId"] = sound
        files["Server/Item/Items/SkyyCollections/%s.json" % eid] = json.dumps(node, indent=2)
        # ench01fix: no promise of a use this phase lacks (the Anvil tier-up is phase 3) and no "already collected" claim (the ingots'
        # collections count ORE); crafting simply never adds collection credit
        desc = ("%d %s pressed into one. Crafting it adds nothing to your collections. Saved for tool and gear upgrades (coming soon). "
                "Workbench, Compressing tab - or /craft - once unlocked in /collections."
                % (RATIO, base_label(key)))
        lang += ["items.%s.name=%s" % (eid, name), "server.items.%s.name=%s" % (eid, name),
                 "items.%s.description=%s" % (eid, desc), "server.items.%s.description=%s" % (eid, desc)]
    files["Server/Item/Qualities/%s.json" % QUALITY] = json.dumps({
        "QualityValue": QUALITY_VALUE,
        "ItemTooltipTexture": "UI/ItemQualities/Tooltips/ItemTooltipEpic.png",
        "ItemTooltipArrowTexture": "UI/ItemQualities/Tooltips/ItemTooltipEpicArrow.png",
        "SlotTexture": "UI/ItemQualities/Slots/SlotEpic.png",
        "BlockSlotTexture": "UI/ItemQualities/Slots/SlotEpic.png",
        "SpecialSlotTexture": "UI/ItemQualities/Slots/SlotEpic.png",
        "TextColor": QUALITY_COLOR,
        "LocalizationKey": "server.general.qualities." + QUALITY,
        "VisibleQualityLabel": True,
        "RenderSpecialSlot": True,
        "ItemEntityConfig": {"ParticleSystemId": "Drop_Epic"}}, indent=2)
    lang += ["general.qualities.%s=%s" % (QUALITY, QUALITY_LABEL), "server.general.qualities.%s=%s" % (QUALITY, QUALITY_LABEL)]
    lang += TAB_LANG
    # the tab icon = the Enchanted Cobblestone icon (64 x 64 like the vanilla tab icons)
    ref = SA.png_size(SA._read(z, "Icons/CraftingCategories/Workbench/Processing.png"))
    tab = files["Common/Icons/ItemsGenerated/SkyyCollections_Ench_Cobblestone.png"]
    assert SA.png_size(tab) == ref, (SA.png_size(tab), ref)
    files["Common/" + tab_icon_path()] = tab
    return files, lang


BASE_LABEL = {"Cobblestone": "Cobblestone", "Rubble": "stone Rubble (any kind but Ice or Dawnstone)", "Copper": "Copper Ingots", "Iron": "Iron Ingots",
              "Thorium": "Thorium Ingots", "Cobalt": "Cobalt Ingots", "Adamantite": "Adamantite Ingots", "Oak": "Oak Logs",
              "Maple": "Maple Logs", "Gumboab": "Gumboab Logs", "Redwood": "Redwood Logs", "Sallow": "Sallow Logs", "Wheat": "Wheat",
              "Carrot": "Carrots", "Cauliflower": "Cauliflowers", "Pumpkin": "Pumpkins", "Tomato": "Tomatoes", "Cotton": "Cotton",
              "Potato": "Potatoes", "Stick": "Sticks"}
assert sorted(BASE_LABEL) == sorted(KEYS)
# ench01fix: the Rubble recipe takes ResourceTypeId "Rubble" = Rubble_Stone and every Rubble_* whose Parent is Rubble_Stone, EXCEPT
# Rubble_Ice(_Medium) (type Ice) and Rubble_Dawnstone(_Medium) (no parent, no type); the Rubble COLLECTION still counts all of them.
# One recipe can take only one resource type and vanilla items are never overridden, so the label says so (a known gap).


def base_label(key):
    return BASE_LABEL[key]


def tab_icon_path():
    return "Icons/CraftingCategories/SkyyCollections/Compressing.png"


def check_assets(files, z):
    """build checks: every TABLE item (20 since tools01), one quality, every Model / Texture / Icon / sound / particle / quality texture exists in Assets.zip or the
    jar, no vanilla path replaced, the recipe = RATIO x the base, KnowledgeRequired, the Compressing tab, no reverse recipe in the jar"""
    names = set(z.namelist())

    def exists(p):
        q = "Common/" + p
        return q in names or q in files or (q.endswith(".png") and q[:-4] + "@2x.png" in names)
    its = dict((p.rsplit("/", 1)[1][:-5], json.loads(t)) for p, t in files.items() if p.startswith("Server/Item/Items/"))
    assert sorted(its) == sorted(IDS), sorted(its)
    sounds = set(n.rsplit("/", 1)[1][:-5] for n in names if n.startswith("Server/Audio/ItemSounds/") and n.endswith(".json"))
    parts = set(n.rsplit("/", 1)[1][:-len(".particlesystem")] for n in names if n.endswith(".particlesystem"))
    vitems = set(n.rsplit("/", 1)[1][:-5] for n in names if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    for (key, kind, inp, coll, tier, cat, name, look) in TABLE:
        n = its[PREFIX + key]
        for k in ("Model", "Texture", "Icon"):
            assert exists(n[k]), (key, k, n[k])
        assert n["Quality"] == QUALITY and n["MaxStack"] == STACK and "BlockType" not in n and "Parent" not in n, key
        assert n.get("ItemSoundSetId") is None or n["ItemSoundSetId"] in sounds, (key, n.get("ItemSoundSetId"))
        r = n["Recipe"]
        assert r["KnowledgeRequired"] is True and r["OutputQuantity"] == 1 and len(r["Input"]) == 1, key
        i0 = r["Input"][0]
        assert i0["Quantity"] == RATIO and (i0.get("ItemId") == inp if kind == "I" else i0.get("ResourceTypeId") == inp), key
        assert kind == "R" or inp in vitems, (key, inp)
        assert r["BenchRequirement"] == [{"Type": "Crafting", "Id": BENCH_ID, "Categories": [TAB_ID]}], key
    q = json.loads(files["Server/Item/Qualities/%s.json" % QUALITY])
    for k in ("ItemTooltipTexture", "ItemTooltipArrowTexture", "SlotTexture", "BlockSlotTexture", "SpecialSlotTexture"):
        assert exists(q[k]), k
    assert q["ItemEntityConfig"]["ParticleSystemId"] in parts and q["QualityValue"] < 8
    clash = sorted(p for p in files if p in names)
    assert not clash, "an Enchanted asset would replace a vanilla file: %s" % clash
    # no recipe in this jar makes a base item from an Enchanted one (no un-compress) - every recipe here makes an Enchanted item
    for p, t in files.items():
        if p.startswith("Server/") and p.endswith(".json") and '"Recipe"' in t:
            assert p.rsplit("/", 1)[1][:-5].startswith(PREFIX), p
    return "%d Enchanted items (ratio %d, stack %d), quality %s, %d art files, Workbench tab '%s'" % (
        len(its), RATIO, STACK, QUALITY, sum(1 for p in files if p.startswith("Common/")), TAB_TEXT)


# ================================================================================================================ the Compressing tab
# Same engine facts as tools/skyywbtab.py (its probe() runs in the SkyyCollections build): the Workbench tabs are the ordered array
# CraftingBench.categories (protected), rebuilt into each window from getCategories(); a tab is APPENDED at runtime to every Workbench
# CraftingBench (copy-on-write) by its one owner (SkyyCollections), re-applied after an asset reload (LoadedAssetsEvent); the recipes
# land in it through their BenchRequirement Categories; the order inside the tab = a TreeSet in TABLE order (EnchRank).
CB = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.CraftingBench"
CBC = CB + "$BenchCategory"
BIC = CB + "$BenchItemCategory"
BEN = "com.hypixel.hytale.server.core.asset.type.blocktype.config.bench.Bench"
BT = "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType"
CRP = "com.hypixel.hytale.builtin.crafting.CraftingPlugin"
BRR = "com.hypixel.hytale.builtin.crafting.BenchRecipeRegistry"
CRR = "com.hypixel.hytale.server.core.asset.type.item.config.CraftingRecipe"
LAE = "com.hypixel.hytale.assetstore.event.LoadedAssetsEvent"
LOGT = "com.hypixel.hytale.logger.HytaleLogger"


def emit_tab(pool, CtField, CtNewMethod, CtNewConstructor, pkg, mod):
    """<pkg>.EnchRank (order), <pkg>.EnchTab (append + sort), <pkg>.EnchTabL (asset reloads). Returns the CtClass list."""
    tok = {"@PKG@": pkg, "@CB@": CB, "@CBC@": CBC, "@BIC@": BIC, "@BEN@": BEN, "@BT@": BT, "@CRP@": CRP, "@BRR@": BRR, "@LAE@": LAE,
           "@LOGT@": LOGT, "@MOD@": mod}

    def T(src):
        for k, v in tok.items():
            src = src.replace(k, v)
        assert "@" not in src, src[:200]
        return src
    rank = pool.makeClass(pkg + ".EnchRank")
    rank.addInterface(pool.get("java.util.Comparator"))
    tab = pool.makeClass(pkg + ".EnchTab")
    lis = pool.makeClass(pkg + ".EnchTabL")
    lis.addInterface(pool.get("java.util.function.Consumer"))

    def F(c, s):
        c.addField(CtField.make(T(s), c))

    def M(c, s):
        c.addMethod(CtNewMethod.make(T(s), c))
    F(rank, "public static final String[] ORDER = %s;" % _jarr(RIDS))
    rank.addConstructor(CtNewConstructor.make("public EnchRank() { }", rank))
    M(rank, """
public static int rank(String id) {
  if (id == null) return 9999;
  for (int i = 0; i < ORDER.length; i++) if (ORDER[i].equals(id)) return i;
  return 999;
}""")
    M(rank, """
public int compare(Object a, Object b) {
  String x = (String) a;
  String y = (String) b;
  int rx = rank(x);
  int ry = rank(y);
  if (rx != ry) return rx < ry ? -1 : 1;
  return x.compareTo(y);
}""")
    F(tab, "public static final String ID = \"%s\";" % TAB_ID)
    F(tab, "public static final String NAME = \"%s\";" % TAB_NAME_KEY)
    F(tab, "public static final String TEXT = \"%s\";" % TAB_TEXT)
    F(tab, "public static final String ICON = \"%s\";" % tab_icon_path())
    F(tab, "public static final String BENCH = \"%s\";" % BENCH_ID)
    F(tab, "public static final String PROTO = \"%s\";" % ENCH_VERSION)
    F(tab, "public static @LOGT@ LOG;")
    F(tab, "public static java.lang.reflect.Field CATS;")
    F(tab, "public static java.lang.reflect.Field REGS;")
    F(tab, "public static java.lang.reflect.Field CMAP;")
    F(tab, "public static volatile boolean CATS_BAD = false;")
    F(tab, "public static volatile boolean MAP_BAD = false;")
    F(tab, "public static volatile boolean WARN_SCAN = false;")
    F(tab, "public static volatile boolean WARN_SORT = false;")
    F(tab, "public static volatile String LAST = \"not started\";")
    M(tab, """
public static void info(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[@MOD@] " + m); } catch (Throwable t) { }
}""")
    M(tab, """
public static void warn(String m) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[@MOD@] " + m); } catch (Throwable t) { }
}""")
    M(tab, """
public static java.lang.reflect.Field catsField() {
  if (CATS != null) return CATS;
  if (CATS_BAD) return null;
  try {
    java.lang.reflect.Field f = @CB@.class.getDeclaredField("categories");
    f.setAccessible(true);
    CATS = f;
    return f;
  } catch (Throwable t) {
    CATS_BAD = true;
    warn("Compressing tab: the game changed (CraftingBench.categories: " + t + ") - the Enchanted recipes are not shown at the Workbench; /craft still makes them");
    return null;
  }
}""")
    M(tab, """
public static boolean mapFields() {
  if (REGS != null && CMAP != null) return true;
  if (MAP_BAD) return false;
  try {
    java.lang.reflect.Field a = @CRP@.class.getDeclaredField("registries");
    a.setAccessible(true);
    java.lang.reflect.Field b = @BRR@.class.getDeclaredField("categoryMap");
    b.setAccessible(true);
    REGS = a;
    CMAP = b;
    return true;
  } catch (Throwable t) {
    MAP_BAD = true;
    warn("Compressing tab: the game changed (recipe registry: " + t + ") - the tab lists its recipes in the engine's own order");
    return false;
  }
}""")
    M(tab, """
public static @CBC@ mine() {
  return new @CBC@(ID, NAME, ICON, (@BIC@[]) null);
}""")
    # 0 = already there (same name + icon), 1 = appended, 2 = an entry with our id replaced in place, -1 = failed. Copy-on-write.
    M(tab, """
public static int applyTo(@CB@ b) {
  java.lang.reflect.Field f = catsField();
  if (f == null || b == null) return -1;
  try {
    @CBC@[] cur = b.getCategories();
    int n = cur == null ? 0 : cur.length;
    for (int i = 0; i < n; i++) {
      if (cur[i] == null || !ID.equals(cur[i].getId())) continue;
      if (ICON.equals(cur[i].getIcon()) && NAME.equals(cur[i].getName())) return 0;
      @CBC@[] cp = new @CBC@[n];
      for (int j = 0; j < n; j++) cp[j] = cur[j];
      cp[i] = mine();
      f.set(b, cp);
      return 2;
    }
    @CBC@[] out = new @CBC@[n + 1];
    for (int k = 0; k < n; k++) out[k] = cur[k];
    out[n] = mine();
    f.set(b, out);
    return 1;
  } catch (Throwable t) { return -1; }
}""")
    M(tab, """
public static int locked(@CB@ b) {
  int r = -1;
  synchronized (b) { r = applyTo(b); }
  return r;
}""")
    M(tab, """
public static int scan(java.util.Collection c) {
  if (c == null) return 0;
  if (catsField() == null) return -1;
  java.util.IdentityHashMap seen = new java.util.IdentityHashMap();
  int ok = 0;
  int bad = 0;
  java.util.Iterator it = c.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @BT@)) continue;
    @BEN@ be = ((@BT@) o).getBench();
    if (!(be instanceof @CB@) || !BENCH.equals(be.getId())) continue;
    if (seen.put(be, be) != null) continue;
    if (locked((@CB@) be) < 0) bad++; else ok++;
  }
  if (bad > 0 && !WARN_SCAN) {
    WARN_SCAN = true;
    warn("Compressing tab: could not add the tab to " + bad + " Workbench definition(s) - the Enchanted recipes are not shown there; /craft still makes them");
  }
  return (bad > 0 && ok == 0) ? -1 : ok;
}""")
    M(tab, """
public static int scanAll() {
  try {
    return scan(@BT@.getAssetMap().getAssetMap().values());
  } catch (Throwable t) {
    if (!WARN_SCAN) { WARN_SCAN = true; warn("Compressing tab: could not read the block types (" + t + ")"); }
    return -1;
  }
}""")
    M(tab, """
public static String sort() {
  if (!mapFields()) return "the engine's order (registry unavailable)";
  try {
    java.util.Map regs = (java.util.Map) REGS.get(null);
    Object reg = regs == null ? null : regs.get(BENCH);
    if (reg == null) return "no Workbench recipes loaded yet";
    java.util.Map cm = (java.util.Map) CMAP.get(reg);
    Object cur = cm.get(ID);
    if (cur instanceof java.util.TreeSet && ((java.util.TreeSet) cur).comparator() instanceof @PKG@.EnchRank)
      return "table order, " + ((java.util.Set) cur).size() + " recipes";
    java.util.TreeSet ts = new java.util.TreeSet(new @PKG@.EnchRank());
    if (cur instanceof java.util.Collection) ts.addAll((java.util.Collection) cur);
    cm.put(ID, ts);
    if (cur instanceof java.util.Collection) ts.addAll((java.util.Collection) cur);
    return "table order, " + ts.size() + " recipes";
  } catch (Throwable t) {
    if (!WARN_SORT) { WARN_SORT = true; warn("Compressing tab: could not order the recipes (" + t + ") - they stay in the engine's own order"); }
    return "the engine's order";
  }
}""")
    M(tab, """
public static String start() {
  int n = scanAll();
  String s = sort();
  String line;
  if (n > 0) line = "Workbench tab '" + TEXT + "' on " + n + " Workbench definition(s); order: " + s + " (ench protocol " + PROTO + ")";
  else if (n == 0) line = "Workbench tab '" + TEXT + "': no Workbench block type found yet (the asset reload listener adds it later)";
  else line = "Workbench tab '" + TEXT + "' could not be added - see the warning above";
  LAST = line;
  if (n >= 0) info(line); else warn(line);
  return line;
}""")
    M(tab, """
public static void onLoaded(Object e) {
  try {
    @LAE@ ev = (@LAE@) e;
    if (ev.getAssetClass() == @BT@.class) {
      java.util.Map m = ev.getLoadedAssets();
      if (m != null) scan(m.values());
      scanAll();
    } else sort();
  } catch (Throwable t) { }
}""")
    lis.addConstructor(CtNewConstructor.make("public EnchTabL() { }", lis))
    M(lis, """
public void accept(Object e) {
  try { @PKG@.EnchTab.onLoaded(e); } catch (Throwable t) { }
}""")
    return [rank, tab, lis]


def setup_java(pkg):
    return ("  // 0.2.11 Workbench tab 'Compressing' (tools/skyyench.py): re-applied after an asset reload (new BlockType objects / recipe sets)\n"
            "  %s.EnchTab.LOG = getLogger();\n"
            "  try {\n"
            "    getEventRegistry().register(%s.class, %s.class, new %s.EnchTabL());\n"
            "    getEventRegistry().register(%s.class, %s.class, new %s.EnchTabL());\n"
            "  } catch (Throwable twb) { %s.EnchTab.warn(\"Compressing tab: no asset reload listener (\" + twb + \") - a live asset reload drops the tab until a restart\"); }\n"
            % (pkg, LAE, BT, pkg, LAE, CRR, pkg, pkg))
