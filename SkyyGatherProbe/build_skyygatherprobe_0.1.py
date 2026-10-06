"""SkyyGatherProbe 0.1 - build script (javassist via jpype). A THROWAWAY dev / test pack: phase P0 of research/Gathering-Progression-Spec.md
(section 6 P0 row, F4 / F7 / F9 / F12 / F20, "Still unknowable"). Modelled on SkyyUiProbe: op-only commands, pinned for ONE test session,
then removed from the SET again. Nothing here is a feature; it only answers engine questions before phase A depends on them.
Run:   python SkyyGatherProbe/build_skyygatherprobe_0.1.py   -> SkyyGatherProbe/SkyyGatherProbe-0.1.jar + SkyyGatherProbe/SkyyGatherProbeB-0.1.jar
       (no --deploy on purpose: tools/deploy_set.py installs the set once Skyy says deploy)
Check: python SkyyGatherProbe/test_skyygatherprobe_0.1.py   (bare JVM, -Xverify:all, asset + id-collision checks, pure-logic tests)

TWO JARS (both needed for P3; both go in the set for the test session and come out together):
  SkyyGatherProbe-0.1.jar   (plugin + asset pack): the /gprobe command, every probe item / block / recipe, the recoloured P5 icon.
  SkyyGatherProbeB-0.1.jar  (tiny plugin + asset pack): ONLY a second copy of the probe's own item Skyy_GProbe_P3_Twin (MaxStack 13 and the
                            name "...from jar B" instead of 7 / "...from jar A") - P3 "two jars override the same item: who wins" is asked
                            on a probe-only id, never on a vanilla or pack-mod id. Its plugin only publishes skyy.bridge "gprobe:b" = its
                            version so /gprobe p3 can say whether B loaded at all.
NO VANILLA / PACK-MOD ID IS OVERRIDDEN: every asset file is new (Skyy_GProbe_* ids); the harness checks Assets.zip and every installed mod
in UserData/Mods (read-only) for a clash. The probe pickaxe and the two gate blocks are COPIES of vanilla jsons under new ids.

SKYY'S ANSWERS THAT SHAPED THE PROBES (docs/answered/bags.md, 2026-10-06): Enchanted ratio ALWAYS 100 -> P1 is a 100-input recipe (ore,
which stacks to 25 = 4 stacks; and logs split bag + inventory); hard pickaxe gates on Iron / Thorium / Cobalt ARE wanted -> P6 is required.

THE PROBES (one op-only command or recipe each; every chat line is also written to the server log as "[SkyyGatherProbe] ..."):
  P1  recipes "Probe P1: 100 Iron Ore" (Workbench, Crafting tab) = 100 Ore_Iron -> 1 Skyy_GProbe_P1_Ore, and "Probe P1: 100 Oak Logs" =
      100 Wood_Oak_Trunk -> 1 Skyy_GProbe_P1_Log. /gprobe p1 prints the counts in inventory and in bags (SkyySacks sacks:fn:count).
  P2  recipe "Probe P2: Knowledge" (Workbench, Crafting tab, KnowledgeRequired true) = 1 Rock_Stone_Cobble -> Skyy_GProbe_P2_Know.
      /gprobe learn | forget [seconds] = CraftingPlugin.learnRecipe / forgetRecipe (which send UpdateKnownRecipes), now or after a delay
      so an open Workbench can be watched. /gprobe p2 = known or not.
  P3  Skyy_GProbe_P3_Twin is defined in BOTH jars. /gprobe p3 reads the server's asset (MaxStack 7 = jar A won, 13 = jar B won) and
      says whether jar B's plugin loaded; the item's name in the client shows which language line won.
  P4  recipe "Probe P4: 20 Hardwood Logs" = ResourceTypeId Wood_Hardwood_Trunk x 20 (Oak / Ash / Fir / Apple) -> Skyy_GProbe_P4_Res;
      filled from the SkyySacks bag mirror with the logs in a Foraging bag only. /gprobe p4 prints inventory / bag log counts.
  P5  Skyy_GProbe_P5_Icon: Iron Ore look with a PURPLE icon made at build time by tools/skyyart.py recolor_icon from the vanilla Ore_Iron
      icon (shipped as Common/Icons/ItemsGenerated/Skyy_GProbe_P5_Icon.png). Also craftable: 1 Rock_Stone_Cobble at the Workbench.
  P6  two probe ore BLOCKS that look like Iron ore in stone (copies of Ore_Iron_Stone, same drops: Iron Ore + Cobblestone):
        Skyy_GProbe_P6_Ore   GatherType OreIron, Quality 3  -> every vanilla pickaxe is refused (all carry Quality 0 on OreIron);
                             the probe pickaxe Skyy_GProbe_P6_Pick (a copy of the Iron pickaxe, OreIron spec Quality 3) mines it
        Skyy_GProbe_P6_Rock  GatherType Rocks,   Quality 3  -> vanilla Rocks qualities: Crude / Wood / Scrap 1, Copper 2, Iron 3,
                             Thorium / Cobalt 4, Adamantite 5, Mithril / Onyxium 6 -> Crude + Copper refused, Iron and up mine it
      /gprobe p6 prints, for the item in your hand, the engine's verdict on both probe blocks + vanilla Iron / Adamantite ore.
  trees  /gprobe trees [radius] counts trees per species in the LOADED chunks around you (spec 2.2 key-log scarcity check).
  kit    /gprobe kit gives the test materials (storage first): 100 Iron Ore, 140 Oak Logs, 4 Cobblestone, P3 twin, P5 item, 4 + 4 P6
         blocks, the probe pickaxe, a Copper and an Iron pickaxe. Items that do not fit are reported (never dropped).

DESK READ (HytaleServer.jar bytecode, 2026-10-06; BlockHarvestUtils.getSpecPowerDamageBlock(Item held, BlockType block, ItemTool tool)
and its only caller damageSingleBlock):
  - no Gathering / no Breaking / no GatherType on the block -> no spec; a held WEAPON or builder tool -> no spec.
  - q = Breaking.Quality (int, absent = 0). With a tool: the FIRST spec in Tool.Specs whose GatherType equals the block's -> if
    spec.Quality < q: no spec (refused), else that spec. No matching spec -> no spec. Without a tool (bare hand / plain item): the
    ItemToolSpec asset named like the GatherType (Server/Item/Unarmed/Gathering/<GatherType>.json, e.g. OreIron Power 0.001, no Quality)
    with the same Quality test.
  - damageSingleBlock: power = spec ? spec.Power : 0. power != 0 -> Breaking path (damage = power x the hit's multiplier ->
    DamageBlockEvent (cancellable) -> block health -> destroyed = performBlockBreak + the Breaking drops). power == 0 and the block is
    not Soft -> held item present and not a weapon: the GameplayConfig "UnbreakableBlock" particle + sound and the tool's
    IncorrectMaterial sound, then RETURN false: no DamageBlockEvent, no damage, no break, no drops, no durability loss. Bare hand /
    weapon: return false silently.
  So Quality is a hard gate ONLY when the tool spec of the SAME GatherType carries a Quality >= the block's. Vanilla pickaxes have NO
  Quality on OreCopper / OreIron / OreThorium / OreCobalt specs (only Rocks 1-6 and OreAdamantite 4 on Thorium and up): a Quality on
  Iron / Thorium / Cobalt ore therefore needs the pickaxe jsons overridden too (SkyyGear, F20) - or the ore re-typed to GatherType Rocks
  (vanilla's Rocks ladder already gates, but the ore then mines at stone speed and Thorium / Cobalt pickaxes share Rocks Quality 4).
  Only Ore_Adamantite_Magma carries a Quality in Assets.zip today (4); no Mithril ore block has one.
"""
import sys, os, json, zipfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import skyybuild as B
import skyyart as SA

if "--deploy" in sys.argv:
    raise SystemExit("SkyyGatherProbe: --deploy is not supported here - deploys go through tools/deploy_set.py")

VERSION = "0.1"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
NODE = "skyygatherprobe.admin"

# ================= the probe ids (all new; the harness proves no clash with Assets.zip or installed mods) =================
P1_ORE, P1_LOG = "Skyy_GProbe_P1_Ore", "Skyy_GProbe_P1_Log"
P2_KNOW = "Skyy_GProbe_P2_Know"
P3_TWIN = "Skyy_GProbe_P3_Twin"
P4_RES = "Skyy_GProbe_P4_Res"
P5_ICON = "Skyy_GProbe_P5_Icon"
P6_ORE, P6_ROCK, P6_PICK = "Skyy_GProbe_P6_Ore", "Skyy_GProbe_P6_Rock", "Skyy_GProbe_P6_Pick"
P6_Q = 3                          # the gate Quality on both probe blocks (and on the probe pickaxe's OreIron spec)
P3_STACK_A, P3_STACK_B = 7, 13    # the server-side marker of who won P3
RATIO = 100                       # Skyy 2026-10-06: Enchanted ratio always 100
P4_TYPE, P4_QTY = "Wood_Hardwood_Trunk", 20
BENCH = [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}]   # a vanilla Workbench tab (no tab override)
KIT = [("Ore_Iron", 100), ("Wood_Oak_Trunk", 140), ("Rock_Stone_Cobble", 4), (P3_TWIN, 1), (P5_ICON, 1), (P6_ORE, 4), (P6_ROCK, 4),
       (P6_PICK, 1), ("Tool_Pickaxe_Copper", 1), ("Tool_Pickaxe_Iron", 1)]
KEY_LOGS = ["Oak", "Maple", "Gumboab", "Redwood", "Sallow"]          # spec 2.2 key logs (+ the swap candidates the count may pick)

az = zipfile.ZipFile(ASSETS)
AZ_NAMES = set(az.namelist())
ITEM_PATH = dict((n.rsplit("/", 1)[1][:-5], n) for n in AZ_NAMES if n.startswith("Server/Item/Items/") and n.endswith(".json"))


def vanilla(item_id):
    if item_id not in ITEM_PATH:
        raise SystemExit("vanilla item %s not in Assets.zip" % item_id)
    return json.loads(az.read(ITEM_PATH[item_id]))


for _i, _q in KIT:
    if not _i.startswith("Skyy_GProbe_") and _i not in ITEM_PATH:
        raise SystemExit("kit item %s not in Assets.zip" % _i)
if "Server/Item/ResourceTypes/%s.json" % P4_TYPE not in AZ_NAMES:
    raise SystemExit("resource type %s not in Assets.zip" % P4_TYPE)
if not any(r.get("Id") == P4_TYPE for r in vanilla("Wood_Oak_Trunk").get("ResourceTypes", [])):
    raise SystemExit("Wood_Oak_Trunk no longer carries %s - pick another P4 type" % P4_TYPE)

files, lang = {}, []


def name_lines(iid, name, desc):
    for pre in ("", "server."):
        lang.append("%sitems.%s.name=%s" % (pre, iid, name))
        lang.append("%sitems.%s.description=%s" % (pre, iid, desc))


def look_of(src_id):
    """the visual fields of a vanilla item (icon, model, texture, icon view, animation / sound set) - never its recipe / block / tool."""
    v = vanilla(src_id)
    out = {}
    for k in ("Icon", "Model", "Texture", "IconProperties", "PlayerAnimationsId", "ItemSoundSetId", "Categories"):
        if k in v:
            out[k] = v[k]
    for k in ("Icon", "Model", "Texture"):
        if k in out and ("Common/" + out[k]) not in AZ_NAMES:
            raise SystemExit("%s of %s (%s) not in Assets.zip" % (k, src_id, out[k]))
    return out


def probe_item(iid, look, name, desc, recipe_in=None, knowledge=False, max_stack=None):
    d = {"TranslationProperties": {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid}}
    d.update(look_of(look))
    if recipe_in is not None:
        d["Recipe"] = {"Input": recipe_in, "BenchRequirement": BENCH, "TimeSeconds": 1, "KnowledgeRequired": knowledge}
    if max_stack is not None:
        d["MaxStack"] = max_stack
    files["Server/Item/Items/SkyyGatherProbe/%s.json" % iid] = json.dumps(d, indent=2)
    name_lines(iid, name, desc)
    return d


probe_item(P1_ORE, "Ingredient_Bar_Iron", "Probe P1: 100 Iron Ore",
           "Gather probe P1: crafted from 100 Iron Ore (4 stacks of 25) at the Workbench. Throwaway test item.", [{"ItemId": "Ore_Iron", "Quantity": RATIO}])
probe_item(P1_LOG, "Ingredient_Bar_Copper", "Probe P1: 100 Oak Logs",
           "Gather probe P1: crafted from 100 Oak Logs, part in a bag and part in the inventory. Throwaway test item.",
           [{"ItemId": "Wood_Oak_Trunk", "Quantity": RATIO}])
probe_item(P2_KNOW, "Ingredient_Bar_Gold", "Probe P2: Knowledge",
           "Gather probe P2: a recipe you must know (KnowledgeRequired). /gprobe learn or /gprobe forget. Throwaway test item.",
           [{"ItemId": "Rock_Stone_Cobble", "Quantity": 1}], knowledge=True)
probe_item(P3_TWIN, "Ingredient_Bar_Silver", "Probe P3 Twin - from jar A",
           "Gather probe P3: this item is defined in two jars. This text and a stack of 7 = jar A won. Throwaway test item.",
           max_stack=P3_STACK_A)
probe_item(P4_RES, "Ingredient_Stick", "Probe P4: 20 Hardwood Logs",
           "Gather probe P4: needs 20 logs of the Hardwood Trunk type (Oak, Ash, Fir, Apple) - test it with the logs in a bag. Throwaway test item.",
           [{"ResourceTypeId": P4_TYPE, "Quantity": P4_QTY}])
p5 = probe_item(P5_ICON, "Ore_Iron", "Probe P5: Purple Icon",
                "Gather probe P5: the Iron Ore look with a purple icon recoloured at build time. Purple icon = recoloured icons draw. Throwaway test item.",
                [{"ItemId": "Rock_Stone_Cobble", "Quantity": 1}])
# ---- P5: the recoloured icon (skyyart recolor_icon on the vanilla Ore_Iron icon; a fixed purple gradient, dark -> light, 0..255)
SA.verify()
_icon_src = az.read("Common/" + vanilla("Ore_Iron")["Icon"])
PURPLE = ((34, 10, 52), (70, 26, 110), (112, 52, 170), (160, 96, 222), (214, 170, 255), (246, 228, 255))
_icon = SA.recolor_icon(_icon_src, PURPLE)
if _icon == _icon_src:
    raise SystemExit("P5: the recoloured icon equals the vanilla icon")
p5["Icon"] = "Icons/ItemsGenerated/%s.png" % P5_ICON
files["Server/Item/Items/SkyyGatherProbe/%s.json" % P5_ICON] = json.dumps(p5, indent=2)
files["Common/" + p5["Icon"]] = _icon

# ---- P6: the two gate blocks (copies of Ore_Iron_Stone: look + drops kept, Breaking GatherType / Quality set) and the probe pickaxe
def gate_block(iid, gather, name, desc):
    d = json.loads(json.dumps(vanilla("Ore_Iron_Stone")))
    if "Parent" in d or "Recipe" in d:
        raise SystemExit("Ore_Iron_Stone changed shape (Parent / Recipe) - re-check the P6 copy")
    d["TranslationProperties"] = {"Name": "server.items.%s.name" % iid, "Description": "server.items.%s.description" % iid}
    br = d["BlockType"]["Gathering"]["Breaking"]
    if br.get("GatherType") != "OreIron" or "Quality" in br:
        raise SystemExit("Ore_Iron_Stone Breaking changed (GatherType %r, Quality %r)" % (br.get("GatherType"), br.get("Quality")))
    br["GatherType"] = gather
    br["Quality"] = P6_Q
    files["Server/Item/Items/SkyyGatherProbe/%s.json" % iid] = json.dumps(d, indent=2)
    name_lines(iid, name, desc)


gate_block(P6_ORE, "OreIron", "Probe P6: Gated Iron Ore (OreIron Q%d)" % P6_Q,
           "Gather probe P6: Iron ore with Quality %d on its OreIron breaking. Vanilla pickaxes should be refused; the Probe Gate Pickaxe should mine it." % P6_Q)
gate_block(P6_ROCK, "Rocks", "Probe P6: Gated Iron Ore (Rocks Q%d)" % P6_Q,
           "Gather probe P6: Iron ore re-typed to Rocks with Quality %d. Crude and Copper pickaxes should be refused; Iron and better should mine it." % P6_Q)
_crude, _iron = vanilla("Tool_Pickaxe_Crude"), vanilla("Tool_Pickaxe_Iron")
if _iron.get("Parent") != "Tool_Pickaxe_Crude" or "Parent" in _crude:
    raise SystemExit("pickaxe inheritance changed - re-check the P6 pickaxe flattening")
pick = dict(_crude)
pick.update(_iron)                 # the Iron pickaxe as the engine builds it: Crude's fields + Iron's own (Iron defines its whole Tool block)
for k in ("Parent", "Recipe"):
    pick.pop(k, None)
pick["TranslationProperties"] = {"Name": "server.items.%s.name" % P6_PICK, "Description": "server.items.%s.description" % P6_PICK}
pick["Tool"] = json.loads(json.dumps(_iron["Tool"]))
_ore_specs = [s for s in pick["Tool"]["Specs"] if s.get("GatherType") == "OreIron"]
if len(_ore_specs) != 1 or "Quality" in _ore_specs[0]:
    raise SystemExit("Tool_Pickaxe_Iron OreIron spec changed: %r" % _ore_specs)
_ore_specs[0]["Quality"] = P6_Q
files["Server/Item/Items/SkyyGatherProbe/%s.json" % P6_PICK] = json.dumps(pick, indent=2)
name_lines(P6_PICK, "Probe Gate Pickaxe (OreIron Q%d)" % P6_Q,
           "Gather probe P6: an Iron pickaxe whose OreIron spec carries Quality %d, so it may mine the gated probe ore. Throwaway test item." % P6_Q)
files["Server/Languages/en-US/server.lang"] = "\n".join(lang) + "\n"

# jar B: only the P3 twin (+ its lang lines)
FILES_B = {}
_twin_b = json.loads(files["Server/Item/Items/SkyyGatherProbe/%s.json" % P3_TWIN])
_twin_b["MaxStack"] = P3_STACK_B
FILES_B["Server/Item/Items/SkyyGatherProbeB/%s.json" % P3_TWIN] = json.dumps(_twin_b, indent=2)
_lang_b = []
for pre in ("", "server."):
    _lang_b.append("%sitems.%s.name=Probe P3 Twin - from jar B" % (pre, P3_TWIN))
    _lang_b.append("%sitems.%s.description=Gather probe P3: this item is defined in two jars. This text and a stack of 13 = jar B won. Throwaway test item." % (pre, P3_TWIN))
FILES_B["Server/Languages/en-US/server.lang"] = "\n".join(_lang_b) + "\n"

# ---- asset build checks: ids new, recipe numbers as specced, gate qualities set
_ids = sorted(p.rsplit("/", 1)[1][:-5] for p in files if p.startswith("Server/Item/Items/"))
assert _ids == sorted([P1_ORE, P1_LOG, P2_KNOW, P3_TWIN, P4_RES, P5_ICON, P6_ORE, P6_ROCK, P6_PICK]), _ids
for _i in _ids + [P3_TWIN]:
    if _i in ITEM_PATH or not _i.startswith("Skyy_GProbe_"):
        raise SystemExit("probe id %s would override a vanilla id" % _i)
for _p in list(files) + list(FILES_B):
    if _p in AZ_NAMES and not _p.endswith("server.lang"):
        raise SystemExit("asset path %s exists in Assets.zip (override)" % _p)
print("assets: %d items, %d lang lines, P5 icon %d bytes, jar B: %d files" % (len(_ids), len(lang), len(_icon), len(FILES_B)))

# ================= Java =================
J = B.start()
pool, CtField, CtNewMethod, CtNewConstructor = J["pool"], J["CtField"], J["CtNewMethod"], J["CtNewConstructor"]
OUT = B.class_out(HERE)
OUT_B = B.class_out(HERE, "build_classes_b")
PKG = "com.skyy.gatherprobe"
PKG_B = "com.skyy.gatherprobeb"
T = {
    "PKG": PKG, "VERSION": VERSION, "NODE": NODE,
    "JP": "com.hypixel.hytale.server.core.plugin.JavaPlugin",
    "JPI": "com.hypixel.hytale.server.core.plugin.JavaPluginInit",
    "PR": "com.hypixel.hytale.server.core.universe.PlayerRef",
    "REF": "com.hypixel.hytale.component.Ref",
    "ST": "com.hypixel.hytale.component.Store",
    "WLD": "com.hypixel.hytale.server.core.universe.world.World",
    "WCH": "com.hypixel.hytale.server.core.universe.world.chunk.WorldChunk",
    "CHU": "com.hypixel.hytale.math.util.ChunkUtil",
    "APC": "com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand",
    "AC": "com.hypixel.hytale.server.core.command.system.AbstractCommand",
    "CTX": "com.hypixel.hytale.server.core.command.system.CommandContext",
    "ATY": "com.hypixel.hytale.server.core.command.system.arguments.types.ArgTypes",
    "RA": "com.hypixel.hytale.server.core.command.system.arguments.system.RequiredArg",
    "MSG": "com.hypixel.hytale.server.core.Message",
    "LOG": "com.hypixel.hytale.logger.HytaleLogger",
    "PLA": "com.hypixel.hytale.server.core.entity.entities.Player",
    "PCD": "com.hypixel.hytale.server.core.entity.entities.player.data.PlayerConfigData",
    "INV": "com.hypixel.hytale.server.core.inventory.Inventory",
    "IC": "com.hypixel.hytale.server.core.inventory.container.ItemContainer",
    "IS": "com.hypixel.hytale.server.core.inventory.ItemStack",
    "IST": "com.hypixel.hytale.server.core.inventory.transaction.ItemStackTransaction",
    "ITM": "com.hypixel.hytale.server.core.asset.type.item.config.Item",
    "ITL": "com.hypixel.hytale.server.core.asset.type.item.config.ItemTool",
    "ITS": "com.hypixel.hytale.server.core.asset.type.item.config.ItemToolSpec",
    "BTY": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType",
    "BGA": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockGathering",
    "BBD": "com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockBreakingDropType",
    "CRP": "com.hypixel.hytale.builtin.crafting.CraftingPlugin",
    "TRC": "com.hypixel.hytale.server.core.modules.entity.component.TransformComponent",
    "V3D": "org.joml.Vector3d",
    "HSV": "com.hypixel.hytale.server.core.HytaleServer",
}
PB = "com.hypixel.hytale.server.core.plugin.PluginBase"
for c, m in ((T["AC"], "requirePermission"), (T["AC"], "setPermissionGroups"), (T["AC"], "addAliases"), (T["AC"], "addUsageVariant"),
             (T["AC"], "withRequiredArg"), (T["CTX"], "get"), (T["ATY"], "STRING"), (T["PR"], "getUsername"), (T["PR"], "sendMessage"),
             (T["PR"], "getUuid"), (T["PR"], "getReference"), (T["MSG"], "raw"), (T["PLA"], "getComponentType"), (T["PLA"], "getInventory"),
             (T["PLA"], "getPlayerConfigData"), (T["PCD"], "getKnownRecipes"), (T["INV"], "getStorage"), (T["INV"], "getHotbar"),
             (T["INV"], "getBackpack"), (T["INV"], "getCombinedStorageFirst"), (T["INV"], "getItemInHand"), (T["IC"], "addItemStack"),
             (T["IC"], "getCapacity"), (T["IC"], "getItemStack"), (T["IS"], "getItemId"), (T["IS"], "getQuantity"), (T["IS"], "isEmpty"),
             (T["IS"], "getItem"), (T["IST"], "succeeded"), (T["IST"], "getRemainder"), (T["ITM"], "getAssetMap"), (T["ITM"], "getTool"),
             (T["ITM"], "getWeapon"), (T["ITM"], "getMaxStack"), (T["ITM"], "getId"), (T["ITL"], "getSpecs"), (T["ITS"], "getGatherType"),
             (T["ITS"], "getQuality"), (T["ITS"], "getPower"), (T["ITS"], "getAssetMap"), (T["BTY"], "getAssetMap"), (T["BTY"], "getGathering"),
             (T["BTY"], "getId"), (T["BGA"], "getBreaking"), (T["BGA"], "isSoft"), (T["BBD"], "getGatherType"), (T["BBD"], "getQuality"),
             (T["CRP"], "learnRecipe"), (T["CRP"], "forgetRecipe"), (T["TRC"], "getComponentType"), (T["TRC"], "getPosition"),
             (T["WLD"], "getChunkIfLoaded"), (T["WLD"], "execute"), (T["WCH"], "getBlock"), (T["WCH"], "getHeight"),
             (T["CHU"], "indexChunk"), (T["HSV"], "SCHEDULED_EXECUTOR"), ("com.hypixel.hytale.component.Ref", "getStore"),
             ("com.hypixel.hytale.component.Ref", "isValid"), (PB, "getCommandRegistry"), (PB, "getLogger"), (PB, "shutdown")):
    B.probe(pool, c, m)

import re
TOKEN = re.compile(r"@([A-Z0-9]{2,7})@")


def jv(src):
    def rep(mm):
        k = mm.group(1)
        if k not in T:
            raise SystemExit("unknown token @%s@ in:\n%s" % (k, src[:300]))
        return T[k]
    return TOKEN.sub(rep, src)


def M(cls, src):
    try:
        cls.addMethod(CtNewMethod.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("compile failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:2500]))


def F(cls, src):
    try:
        cls.addField(CtField.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("field failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:600]))


def C(cls, src):
    try:
        cls.addConstructor(CtNewConstructor.make(jv(src), cls))
    except Exception as e:
        raise SystemExit("constructor failed in %s:\n%s\n---\n%s" % (cls.getName(), e, jv(src)[:1500]))


def mk(name, sup=None, pkg=PKG):
    return pool.makeClass(pkg + "." + name, pool.get(sup)) if sup else pool.makeClass(pkg + "." + name)


def jl(s):
    return json.dumps(s)          # a Java string literal (ASCII text only here)


def jarr(xs):
    return "new String[] { %s }" % ", ".join(jl(x) for x in xs)


# ---- GpLog: the server log + chat (every chat line is logged too, so the log alone carries the results)
log = mk("GpLog")
F(log, "public static @LOG@ LOG;")
M(log, r"""
public static void info(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.INFO).log("[SkyyGatherProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void warn(String msg) {
  try { if (LOG != null) LOG.at(java.util.logging.Level.WARNING).log("[SkyyGatherProbe] " + msg); } catch (Throwable t) { }
}""")
M(log, r"""
public static void tell(@PR@ pr, String s) {
  info((pr == null ? "" : "to " + pr.getUsername() + ": ") + s);
  try { if (pr != null) pr.sendMessage(@MSG@.raw("[GatherProbe] " + s)); } catch (Throwable t) { }
}""")

# ---- GpLogic: pure functions (no engine objects) - the harness calls them directly
lg = mk("GpLogic")
F(lg, "public static final String[] KEYLOGS = %s;" % jarr(KEY_LOGS))
# a natural tree trunk block id "Wood_<Species>_Trunk" (the player-made _Full / _Half / _Stairs pieces and branches / roots are not)
M(lg, r"""
public static boolean isTrunk(String id) {
  return id != null && id.length() > 11 && id.startsWith("Wood_") && id.endsWith("_Trunk");
}""")
M(lg, r"""
public static String species(String id) {
  if (!isTrunk(id)) return null;
  return id.substring(5, id.length() - 6);
}""")
# a trunk block is a tree BASE when the block under it is ground: not the same trunk, not air / empty, not leaves, not another wood
# piece except roots (branches and leaning trunk pieces sit on air, leaves or wood)
M(lg, r"""
public static boolean isBase(String self, String below) {
  if (!isTrunk(self)) return false;
  if (below == null || below.length() == 0) return false;
  if (below.equals(self)) return false;
  if (below.equals("Empty") || below.equals("Unknown")) return false;
  if (below.indexOf("Leaves") >= 0) return false;
  if (below.startsWith("Wood_") && !below.endsWith("_Roots")) return false;
  return true;
}""")
# the engine's getSpecPowerDamageBlock rule on plain data: the FIRST spec of the block's GatherType decides; quality < block quality =
# refused; no spec of that type = no power. Answer: "ALLOWED ..." / "REFUSED ..." / "NO SPEC ..."
M(lg, r"""
public static String verdict(String[] gts, int[] qs, float[] pws, String blockGt, int blockQ) {
  if (blockGt == null) return "NO GATHER TYPE (block has no Breaking gather type)";
  if (gts != null) {
    for (int i = 0; i < gts.length; i++) {
      if (gts[i] != null && gts[i].equals(blockGt)) {
        if (qs[i] < blockQ) return "REFUSED (your " + blockGt + " quality " + qs[i] + " < block quality " + blockQ + ")";
        return "ALLOWED (power " + pws[i] + ", your " + blockGt + " quality " + qs[i] + " >= block quality " + blockQ + ")";
      }
    }
  }
  return "NO SPEC (your tool has no " + blockGt + " power: 0 damage)";
}""")
M(lg, r"""
public static String plural(int n, String one, String many) { return n + " " + (n == 1 ? one : many); }""")

# ---- GpTrees: the tree count (world thread; loaded chunks only)
tr = mk("GpTrees")
M(tr, r"""
public static String nameOf(java.util.HashMap cache, int id) {
  Integer k = Integer.valueOf(id);
  Object o = cache.get(k);
  if (o != null) return (String) o;
  String n = "";
  try {
    Object a = @BTY@.getAssetMap().getAsset(id);
    if (a instanceof @BTY@) n = String.valueOf(((@BTY@) a).getId());
  } catch (Throwable t) { n = ""; }
  cache.put(k, n);
  return n;
}""")
M(tr, r"""
public static int blockAt(@WLD@ w, @WCH@ c, int x, int y, int z) {
  if (y < 0 || y >= 320) return 0;
  if (c != null && (x >> 5) == c.getX() && (z >> 5) == c.getZ()) return c.getBlock(x, y, z);
  @WCH@ o = w.getChunkIfLoaded(@CHU@.indexChunk(x >> 5, z >> 5));
  return o == null ? 0 : o.getBlock(x, y, z);
}""")
M(tr, r"""
public static boolean baseAt(@WLD@ w, @WCH@ c, java.util.HashMap cache, int x, int y, int z, String self) {
  if (!self.equals(nameOf(cache, blockAt(w, c, x, y, z)))) return false;
  return @PKG@.GpLogic.isBase(self, nameOf(cache, blockAt(w, c, x, y - 1, z)));
}""")
M(tr, r"""
public static void bump(java.util.TreeMap m, String k) {
  int[] v = (int[]) m.get(k);
  if (v == null) { v = new int[1]; m.put(k, v); }
  v[0]++;
}""")
M(tr, r"""
public static int get(java.util.TreeMap m, String k) {
  int[] v = (int[]) m.get(k);
  return v == null ? 0 : v[0];
}""")
# scan every loaded chunk column within the square radius r around (px, pz): from the heightmap top down 120 blocks (all trunks of a
# surface tree; cave trees deeper than that are missed). One tree = one base cluster (a 2x2 trunk counts once).
M(tr, r"""
public static java.util.ArrayList scan(@WLD@ w, int px, int pz, int r) {
  long t0 = System.currentTimeMillis();
  java.util.HashMap cache = new java.util.HashMap();
  java.util.TreeMap trees = new java.util.TreeMap();
  java.util.TreeMap trunks = new java.util.TreeMap();
  int loaded = 0, missing = 0, cols = 0;
  int cx0 = (px - r) >> 5, cx1 = (px + r) >> 5, cz0 = (pz - r) >> 5, cz1 = (pz + r) >> 5;
  for (int cx = cx0; cx <= cx1; cx++) {
    for (int cz = cz0; cz <= cz1; cz++) {
      @WCH@ c = w.getChunkIfLoaded(@CHU@.indexChunk(cx, cz));
      if (c == null) { missing++; continue; }
      loaded++;
      for (int lx = 0; lx < 32; lx++) {
        int x = (cx << 5) + lx;
        if (x < px - r || x > px + r) continue;
        for (int lz = 0; lz < 32; lz++) {
          int z = (cz << 5) + lz;
          if (z < pz - r || z > pz + r) continue;
          cols++;
          int top = c.getHeight(x, z);
          if (top <= 0 || top > 319) top = 319;
          int bot = top - 120;
          if (bot < 1) bot = 1;
          String below = nameOf(cache, c.getBlock(x, bot - 1, z));
          for (int y = bot; y <= top; y++) {
            String n = nameOf(cache, c.getBlock(x, y, z));
            if (@PKG@.GpLogic.isTrunk(n)) {
              String sp = @PKG@.GpLogic.species(n);
              bump(trunks, sp);
              if (@PKG@.GpLogic.isBase(n, below)) {
                boolean dup = baseAt(w, c, cache, x - 1, y, z, n) || baseAt(w, c, cache, x, y, z - 1, n)
                    || baseAt(w, c, cache, x - 1, y, z - 1, n) || baseAt(w, c, cache, x + 1, y, z - 1, n);
                if (!dup) bump(trees, sp);
              }
            }
            below = n;
          }
        }
      }
    }
  }
  java.util.ArrayList out = new java.util.ArrayList();
  out.add("Trees within " + r + " blocks of (" + px + ", " + pz + "): " + loaded + " chunks scanned, " + missing
      + " not loaded (skipped), " + cols + " columns, " + (System.currentTimeMillis() - t0) + " ms. Format: trees / trunk blocks.");
  // species sorted by tree count, highest first
  java.util.ArrayList keys = new java.util.ArrayList(trunks.keySet());
  int total = 0;
  for (int i = 0; i < keys.size(); i++) total += get(trees, (String) keys.get(i));
  while (keys.size() > 0) {
    int best = 0;
    for (int i = 1; i < keys.size(); i++) if (get(trees, (String) keys.get(i)) > get(trees, (String) keys.get(best))) best = i;
    String k = (String) keys.remove(best);
    out.add("  " + k + ": " + get(trees, k) + " / " + get(trunks, k));
  }
  StringBuilder kl = new StringBuilder("Key logs (spec 2.2): ");
  for (int i = 0; i < @PKG@.GpLogic.KEYLOGS.length; i++) {
    String k = @PKG@.GpLogic.KEYLOGS[i];
    kl.append(i == 0 ? "" : ", ").append(k).append(" ").append(get(trees, k));
  }
  out.add(kl.toString() + ". Total trees: " + total + ".");
  if (trunks.size() == 0) out.add("No natural trunk blocks found - stand in the middle of the island and try a bigger radius.");
  return out;
}""")

# ---- GpTask: a delayed learn / forget (scheduler thread -> the player's world thread)
task = mk("GpTask")
task.addInterface(pool.get("java.lang.Runnable"))
F(task, "public @WLD@ world;")
F(task, "public @PR@ pr;")
F(task, "public boolean learn;")
F(task, "public boolean onWorld;")
C(task, r"""
public GpTask(@WLD@ w, @PR@ pr, boolean learn) {
  this.world = w;
  this.pr = pr;
  this.learn = learn;
  this.onWorld = false;
}""")

# ---- GpCmds: what each probe does
cmds = mk("GpCmds")
F(cmds, "public static final String P1ORE = %s;" % jl(P1_ORE))
F(cmds, "public static final String P1LOG = %s;" % jl(P1_LOG))
F(cmds, "public static final String P2 = %s;" % jl(P2_KNOW))
F(cmds, "public static final String P3 = %s;" % jl(P3_TWIN))
F(cmds, "public static final String P6ORE = %s;" % jl(P6_ORE))
F(cmds, "public static final String P6ROCK = %s;" % jl(P6_ROCK))
F(cmds, "public static final String[] KIT = %s;" % jarr([i for i, q in KIT]))
F(cmds, "public static final int[] KITQ = new int[] { %s };" % ", ".join(str(q) for i, q in KIT))
M(cmds, r"""
public static void tell(@PR@ pr, String s) { @PKG@.GpLog.tell(pr, s); }""")
M(cmds, r"""
public static java.util.Map bridge() {
  Object b = System.getProperties().get("skyy.bridge");
  if (b instanceof java.util.Map) return (java.util.Map) b;
  return java.util.Collections.EMPTY_MAP;
}""")
M(cmds, r"""
public static @PLA@ player(@ST@ store, @REF@ ref) {
  try { return (@PLA@) store.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { return null; }
}""")
M(cmds, r"""
public static int countIn(@IC@ cont, String id) {
  if (cont == null || id == null) return 0;
  int n = 0;
  short cap = cont.getCapacity();
  for (short s = 0; s < cap; s++) {
    @IS@ it = cont.getItemStack(s);
    if (it == null || it.isEmpty()) continue;
    if (id.equals(it.getItemId())) n += it.getQuantity();
  }
  return n;
}""")
M(cmds, r"""
public static int countInv(@PLA@ p, String id) {
  if (p == null) return 0;
  @INV@ inv = p.getInventory();
  if (inv == null) return 0;
  return countIn(inv.getStorage(), id) + countIn(inv.getHotbar(), id) + countIn(inv.getBackpack(), id);
}""")
# SkyySacks 0.7.13 sacks:fn:count {UUID, itemId} -> Long (takeable from the bags you carry now; -1 = paused); -2 here = no SkyySacks
M(cmds, r"""
public static long countBag(@PR@ pr, String id) {
  try {
    Object f = bridge().get("sacks:fn:count");
    if (!(f instanceof java.util.function.Function)) return -2L;
    Object r = ((java.util.function.Function) f).apply(new Object[] { pr.getUuid(), id });
    if (r instanceof Long) return ((Long) r).longValue();
    return -2L;
  } catch (Throwable t) { return -2L; }
}""")
M(cmds, r"""
public static String bagText(long n) {
  if (n == -2L) return "? (SkyySacks bridge not found)";
  if (n == -1L) return "? (bags paused - profile switch settling)";
  return String.valueOf(n);
}""")
M(cmds, r"""
public static void counts(@PR@ pr, @PLA@ p, String label, String id, int need) {
  int inv = countInv(p, id);
  long bag = countBag(pr, id);
  long sum = inv + (bag > 0L ? bag : 0L);
  tell(pr, label + ": inventory " + inv + ", bags you carry " + bagText(bag) + " (together " + sum + ", the recipe needs " + need + ").");
}""")
M(cmds, r"""
public static void help(@PR@ pr) {
  tell(pr, "Gather probes (op only). Do them in order, then send Skyy's notes + the server log:");
  tell(pr, "/gprobe kit - the test items (empty your inventory first; carry NO bags while you take it)");
  tell(pr, "/gprobe p1 - 100 Iron Ore and 100 Oak Logs recipes (Workbench, Crafting tab): counts in inventory and bags");
  tell(pr, "/gprobe p2 - is the Knowledge probe recipe known? /gprobe learn or forget [seconds] (a delay lets you watch an open Workbench)");
  tell(pr, "/gprobe p3 - which jar won the twin item (server side)");
  tell(pr, "/gprobe p4 - the 20 Hardwood Logs (resource type) recipe filled from a bag: log counts");
  tell(pr, "/gprobe p5 - the purple icon item");
  tell(pr, "/gprobe p6 - what the item in your hand does to the gated probe ores (hold the pickaxe, then type it)");
  tell(pr, "/gprobe trees [radius] - trees per species around you (default 96, max 384; loaded chunks only)");
}""")
M(cmds, r"""
public static void kit(@PR@ pr, @PLA@ p) {
  if (p == null || p.getInventory() == null) { tell(pr, "No inventory found."); return; }
  @IC@ dst = p.getInventory().getCombinedStorageFirst();
  StringBuilder got = new StringBuilder();
  StringBuilder lost = new StringBuilder();
  for (int i = 0; i < KIT.length; i++) {
    int added = 0;
    try {
      @IST@ tx = dst.addItemStack(new @IS@(KIT[i], KITQ[i]));
      @IS@ rem = tx == null ? null : tx.getRemainder();
      added = (tx == null || !tx.succeeded()) ? 0 : KITQ[i] - (rem == null || rem.isEmpty() ? 0 : rem.getQuantity());
    } catch (Throwable t) { @PKG@.GpLog.warn("kit: " + KIT[i] + " failed: " + t); added = 0; }
    got.append(got.length() == 0 ? "" : ", ").append(added).append(" ").append(KIT[i]);
    if (added < KITQ[i]) lost.append(lost.length() == 0 ? "" : ", ").append(KITQ[i] - added).append(" ").append(KIT[i]);
  }
  tell(pr, "Kit given: " + got.toString() + ".");
  if (lost.length() > 0) tell(pr, "Did NOT fit (nothing was dropped - free some space and run /gprobe kit again): " + lost.toString() + ".");
}""")
M(cmds, r"""
public static void p1(@PR@ pr, @PLA@ p) {
  tell(pr, "P1 (ratio 100): Workbench > Crafting tab > 'Probe P1: 100 Iron Ore' and 'Probe P1: 100 Oak Logs'.");
  counts(pr, p, "Iron Ore", "Ore_Iron", 100);
  counts(pr, p, "Oak Logs", "Wood_Oak_Trunk", 100);
  tell(pr, "Made so far: P1 ore items " + countInv(p, P1ORE) + ", P1 log items " + countInv(p, P1LOG) + ".");
}""")
M(cmds, r"""
public static boolean knows(@PLA@ p, String id) {
  try {
    @PCD@ d = p.getPlayerConfigData();
    java.util.Set k = d == null ? null : d.getKnownRecipes();
    return k != null && k.contains(id);
  } catch (Throwable t) { return false; }
}""")
M(cmds, r"""
public static void p2(@PR@ pr, @PLA@ p) {
  if (p == null) { tell(pr, "No player found."); return; }
  tell(pr, "P2: 'Probe P2: Knowledge' (Workbench, Crafting tab, KnowledgeRequired) is " + (knows(p, P2) ? "KNOWN" : "NOT known") + " for you.");
  tell(pr, "Look at the Crafting tab now: is the recipe hidden, greyed out, or craftable? /gprobe learn 10 = learn it in 10 s (open the Workbench and watch).");
}""")
M(cmds, r"""
public static void doLearn(@PR@ pr, @REF@ ref, @ST@ store, boolean learn) {
  boolean ch = false;
  try {
    if (learn) ch = @CRP@.learnRecipe(ref, P2, store);
    else ch = @CRP@.forgetRecipe(ref, P2, store);
  } catch (Throwable t) { tell(pr, "P2: " + (learn ? "learn" : "forget") + " failed: " + t); return; }
  @PLA@ p = player(store, ref);
  tell(pr, "P2: " + (learn ? "learned" : "forgot") + " the Knowledge recipe (" + (ch ? "changed" : "no change") + "; now "
      + (p != null && knows(p, P2) ? "KNOWN" : "NOT known") + "). An UpdateKnownRecipes packet was sent - did an open Workbench change by itself?");
}""")
M(cmds, r"""
public static void learnLater(@PR@ pr, @WLD@ w, boolean learn, int secs) {
  try {
    @HSV@.SCHEDULED_EXECUTOR.schedule(new @PKG@.GpTask(w, pr, learn), (long) secs * 1000L, java.util.concurrent.TimeUnit.MILLISECONDS);
    tell(pr, "P2: will " + (learn ? "LEARN" : "FORGET") + " the Knowledge recipe in " + secs + " s - open the Workbench Crafting tab now and watch it.");
  } catch (Throwable t) { tell(pr, "P2: could not schedule: " + t); }
}""")
M(cmds, r"""
public static void p3(@PR@ pr) {
  int ms = -1;
  try {
    Object o = @ITM@.getAssetMap().getAsset(P3);
    if (o instanceof @ITM@) ms = ((@ITM@) o).getMaxStack();
  } catch (Throwable t) { ms = -1; }
  Object b = bridge().get("gprobe:b");
  String who = ms == @P3A@ ? "jar A (SkyyGatherProbe) won" : (ms == @P3B@ ? "jar B (SkyyGatherProbeB) won" : "neither (unexpected)");
  tell(pr, "P3: server asset " + P3 + " has MaxStack " + ms + " -> " + who + ". Jar B plugin " + (b == null ? "NOT loaded" : "loaded (" + b + ")") + ".");
  tell(pr, "Now hover the 'Probe P3 Twin' item: the name says 'from jar A' or 'from jar B' (the client's language line), and how many stack in one slot (7 or 13).");
}""".replace("@P3A@", str(P3_STACK_A)).replace("@P3B@", str(P3_STACK_B)))
M(cmds, r"""
public static void p4(@PR@ pr, @PLA@ p) {
  tell(pr, "P4: 'Probe P4: 20 Hardwood Logs' needs 20 logs of the resource type Wood_Hardwood_Trunk (Oak / Ash / Fir / Apple).");
  counts(pr, p, "Oak Logs", "Wood_Oak_Trunk", 20);
  tell(pr, "Test it with ALL oak logs in a Foraging bag (none in the inventory): can you craft it at the Workbench?");
}""")
M(cmds, r"""
public static void p5(@PR@ pr, @PLA@ p) {
  tell(pr, "P5: you have " + countInv(p, "@P5@") + " 'Probe P5: Purple Icon'. Its inventory icon should be a PURPLE iron ore. Grey / white / missing = recoloured icons do not draw. It is also in the Workbench Crafting tab (1 Cobblestone).");
}""".replace("@P5@", P5_ICON))
M(cmds, r"""
public static String blockLine(String id, String[] gts, int[] qs, float[] pws) {
  try {
    Object o = @BTY@.getAssetMap().getAsset(id);
    if (!(o instanceof @BTY@)) return id + ": block type not loaded";
    @BTY@ bt = (@BTY@) o;
    @BGA@ g = bt.getGathering();
    @BBD@ br = g == null ? null : g.getBreaking();
    if (br == null) return id + ": no Breaking";
    return id + " (" + br.getGatherType() + " quality " + br.getQuality() + "): " + @PKG@.GpLogic.verdict(gts, qs, pws, br.getGatherType(), br.getQuality());
  } catch (Throwable t) { return id + ": " + t; }
}""")
M(cmds, r"""
public static void p6(@PR@ pr, @PLA@ p) {
  if (p == null || p.getInventory() == null) { tell(pr, "No inventory found."); return; }
  @IS@ held = p.getInventory().getItemInHand();
  @ITM@ it = (held == null || held.isEmpty()) ? null : held.getItem();
  String hid = it == null ? "bare hand" : it.getId();
  String[] gts = new String[0];
  int[] qs = new int[0];
  float[] pws = new float[0];
  String note = "";
  if (it != null && it.getWeapon() != null) note = " (a WEAPON: the engine gives weapons no gather spec at all)";
  @ITL@ tool = it == null ? null : it.getTool();
  if (tool != null && tool.getSpecs() != null) {
    @ITS@[] sp = tool.getSpecs();
    gts = new String[sp.length]; qs = new int[sp.length]; pws = new float[sp.length];
    for (int i = 0; i < sp.length; i++) { gts[i] = sp[i].getGatherType(); qs[i] = sp[i].getQuality(); pws[i] = sp[i].getPower(); }
  } else if (it == null || it.getWeapon() == null) {
    note = " (no tool: the unarmed spec of each gather type applies)";
    String[] u = new String[] { "OreIron", "Rocks", "OreAdamantite" };
    gts = new String[3]; qs = new int[3]; pws = new float[3];
    for (int i = 0; i < 3; i++) {
      gts[i] = u[i];
      try {
        Object o = @ITS@.getAssetMap().getAsset(u[i]);
        if (o instanceof @ITS@) { qs[i] = ((@ITS@) o).getQuality(); pws[i] = ((@ITS@) o).getPower(); } else gts[i] = null;
      } catch (Throwable t) { gts[i] = null; }
    }
  }
  tell(pr, "P6 with " + hid + note + ":");
  tell(pr, "  " + blockLine(P6ORE, gts, qs, pws));
  tell(pr, "  " + blockLine(P6ROCK, gts, qs, pws));
  tell(pr, "  vanilla " + blockLine("Ore_Iron_Stone", gts, qs, pws));
  tell(pr, "  vanilla " + blockLine("Ore_Adamantite_Magma", gts, qs, pws));
  tell(pr, "Now hit both probe ores with it: REFUSED should do nothing (no cracks kept, no drops, a 'can't break' sound) - say what you see.");
}""")
M(cmds, r"""
public static void trees(@PR@ pr, @REF@ ref, @ST@ store, @WLD@ w, int r) {
  try {
    @TRC@ tc = (@TRC@) store.getComponent(ref, @TRC@.getComponentType());
    @V3D@ pos = tc == null ? null : tc.getPosition();
    if (pos == null) { tell(pr, "No position found."); return; }
    int px = (int) Math.floor(pos.x), pz = (int) Math.floor(pos.z);
    java.util.ArrayList lines = @PKG@.GpTrees.scan(w, px, pz, r);
    for (int i = 0; i < lines.size(); i++) tell(pr, (String) lines.get(i));
  } catch (Throwable t) { @PKG@.GpLog.warn("trees failed: " + t); tell(pr, "Tree count failed: " + t); }
}""")
M(cmds, r"""
public static int number(String s, int dflt, int lo, int hi) {
  int n = dflt;
  try { n = Integer.parseInt(s == null ? "" : s.trim()); } catch (Throwable t) { n = dflt; }
  if (n < lo) n = lo;
  if (n > hi) n = hi;
  return n;
}""")
# one entry point for the two usage variants: what = probe word, arg = second word or null
M(cmds, r"""
public static void run(@REF@ ref, @ST@ store, @PR@ pr, @WLD@ w, String what, String arg) {
  String t = what == null ? "" : what.trim().toLowerCase(java.util.Locale.ROOT);
  @PLA@ p = player(store, ref);
  @PKG@.GpLog.info(pr.getUsername() + " ran /gprobe " + t + (arg == null ? "" : " " + arg));
  if (t.equals("kit")) { kit(pr, p); return; }
  if (t.equals("p1")) { p1(pr, p); return; }
  if (t.equals("p2")) { p2(pr, p); return; }
  if (t.equals("learn") || t.equals("forget")) {
    if (arg == null) { doLearn(pr, ref, store, t.equals("learn")); return; }
    learnLater(pr, w, t.equals("learn"), number(arg, 10, 1, 120));
    return;
  }
  if (t.equals("p3")) { p3(pr); return; }
  if (t.equals("p4")) { p4(pr, p); return; }
  if (t.equals("p5")) { p5(pr, p); return; }
  if (t.equals("p6")) { p6(pr, p); return; }
  if (t.equals("trees")) { trees(pr, ref, store, w, number(arg, 96, 16, 384)); return; }
  help(pr);
}""")
# GpTask.run (after GpCmds exists: javassist compiles calls only against existing methods)
M(task, r"""
public void run() {
  try {
    if (!this.onWorld) {
      this.onWorld = true;
      if (this.world != null) this.world.execute(this);
      return;
    }
    @REF@ r = this.pr == null ? null : this.pr.getReference();
    if (r == null || !r.isValid()) return;
    @PKG@.GpCmds.doLearn(this.pr, r, r.getStore(), this.learn);
  } catch (Throwable t) { @PKG@.GpLog.warn("delayed learn / forget failed: " + t); }
}""")

EXEC = "protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world)"
# ---- /gprobe <what> <value>  (admin: requirePermission + no permission groups)
cmd2 = mk("GProbeArg2Cmd", T["APC"])
F(cmd2, "public @RA@ whatArg;")
F(cmd2, "public @RA@ valArg;")
C(cmd2, r"""
public GProbeArg2Cmd() {
  super("(admin) /gprobe trees <radius>, /gprobe learn <seconds>, /gprobe forget <seconds>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("probe", "trees, learn or forget", @ATY@.STRING);
  this.valArg = withRequiredArg("value", "radius in blocks, or a delay in seconds", @ATY@.STRING);
}""")
M(cmd2, EXEC + r""" {
  String a = null, v = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); v = String.valueOf(ctx.get(this.valArg)); }
  catch (Throwable t) { @PKG@.GpLog.tell(pr, "Usage: /gprobe trees <radius> | learn <seconds> | forget <seconds>"); return; }
  @PKG@.GpCmds.run(ref, store, pr, world, a, v);
}""")
# ---- /gprobe <what>
cmd1 = mk("GProbeArgCmd", T["APC"])
F(cmd1, "public @RA@ whatArg;")
C(cmd1, r"""
public GProbeArgCmd() {
  super("(admin) /gprobe <kit, p1, p2, learn, forget, p3, p4, p5, p6, trees>");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  this.whatArg = withRequiredArg("probe", "kit, p1, p2, learn, forget, p3, p4, p5, p6 or trees", @ATY@.STRING);
}""")
M(cmd1, EXEC + r""" {
  String a = null;
  try { a = String.valueOf(ctx.get(this.whatArg)); }
  catch (Throwable t) { @PKG@.GpLog.tell(pr, "Usage: /gprobe <kit, p1, p2, learn, forget, p3, p4, p5, p6, trees>"); return; }
  @PKG@.GpCmds.run(ref, store, pr, world, a, null);
}""")
# ---- /gprobe (alias /gatherprobe): the help list
cmd = mk("GProbeCmd", T["APC"])
C(cmd, r"""
public GProbeCmd() {
  super("gprobe", "(admin) Gathering probes P1-P6 + tree count (throwaway dev pack): /gprobe lists them");
  requirePermission("@NODE@");
  setPermissionGroups(new String[0]);
  addAliases(new String[] { "gatherprobe" });
  addUsageVariant(new @PKG@.GProbeArgCmd());
  addUsageVariant(new @PKG@.GProbeArg2Cmd());
}""")
M(cmd, EXEC + r""" {
  @PKG@.GpCmds.help(pr);
}""")

# ---- plugin A
pl = mk("SkyyGatherProbePlugin", T["JP"])
C(pl, "public SkyyGatherProbePlugin(@JPI@ init) { super(init); }")
M(pl, r"""
public void setup() {
  @PKG@.GpLog.LOG = getLogger();
  getCommandRegistry().registerCommand(new @PKG@.GProbeCmd());
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyGatherProbe] @VERSION@ ready - /gprobe (admin): probes P1-P6 + tree count (throwaway dev pack, remove after the test session)");
}""")
M(pl, r"""
protected void shutdown() {
  super.shutdown();
}""")

ALL = [log, lg, tr, task, cmds, cmd2, cmd1, cmd, pl]
for c in ALL:
    c.writeFile(OUT)

# ---- plugin B (jar B): publishes gprobe:b on the bridge so /gprobe p3 can tell it loaded
plb = mk("SkyyGatherProbeBPlugin", T["JP"], PKG_B)
C(plb, "public SkyyGatherProbeBPlugin(@JPI@ init) { super(init); }")
M(plb, r"""
public void setup() {
  try {
    synchronized (java.lang.System.class) {
      Object o = System.getProperties().get("skyy.bridge");
      if (o == null) { o = new java.util.concurrent.ConcurrentHashMap(); System.getProperties().put("skyy.bridge", o); }
      ((java.util.Map) o).put("gprobe:b", "SkyyGatherProbeB @VERSION@");
    }
  } catch (Throwable t) { }
  getLogger().at(java.util.logging.Level.INFO).log("[SkyyGatherProbeB] @VERSION@ ready - second copy of the P3 twin item only");
}""")
plb.writeFile(OUT_B)
print("classes written: %d (+1 in jar B)" % len(ALL))

jar_b = os.path.join(HERE, "SkyyGatherProbeB-%s.jar" % VERSION)
man_b = B.manifest("SkyyGatherProbeB", VERSION, "SkyWynn THROWAWAY dev pack, part B: a second copy of the SkyyGatherProbe P3 twin item (probe P3: two jars define the same item). Remove with SkyyGatherProbe after the test session.", PKG_B + ".SkyyGatherProbeBPlugin")
B.assemble(jar_b, man_b, OUT_B, FILES_B)
jar = os.path.join(HERE, "SkyyGatherProbe-%s.jar" % VERSION)
man = B.manifest("SkyyGatherProbe", VERSION, "SkyWynn THROWAWAY dev pack: gathering probes P1-P6 + an island tree count (/gprobe, admin only). Pinned for one test session, then removed.", PKG + ".SkyyGatherProbePlugin")
B.assemble(jar, man, OUT, files)
