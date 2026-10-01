"""Derive SkyyAccessories/build_skyyaccessories_0.5.2.py from the GENERATED 0.5.1 script (build_skyyaccessories_0.5.1.py = the
tools/deploy_set.py SET pin, itself written by tools/acc_0_5_1_patch.py; same style: rep(old, new) with asserted anchors; the 0.5.1 script
stays untouched - never re-run acc_0_5_1_patch.py on top of this).
Run:  python tools/acc_0_5_2_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.5.2.py   (never --deploy from an agent)
Test: python SkyyAccessories/test_skyyaccessories_0.5.2.py   (every 0.5.1 check + W the Workbench tab + Y compare with 0.5.1)

0.5.2 = ONE CHANGE: THE WORKBENCH TAB "Accessories & Bags". Skyy 2026-10-01 (at the vanilla Workbench, accessory recipes mixed into its
Crafting tab), verbatim: "make a new tab for accessories, and sacks. list them in the order you would craft them. low levels first. with
legendries and omnis at the bottom."
 - Every SkyyAccessories recipe (47: the 46 Workbench recipes + the pocket Accessory Bag) and every SkyySacks recipe (21, SkyySacks
   0.7.10) sits in ONE new Workbench tab, id Workbench_SkyyAccessories, name "Accessories & Bags" (the items' own words: "... Accessory",
   "Accessory Bag", "... Bag"), icon = the bag icon every one of those items uses. The vanilla tabs lose those recipes; nothing else moves.
 - Ingredients, outputs, quality, bench tier (none set = any Workbench tier) and KnowledgeRequired stay byte-identical; only the
   BenchRequirement Categories change: Workbench recipes ["Workbench_Crafting"] -> ["Workbench_SkyyAccessories"].
 - The Accessory Bag stays POCKET-CRAFTABLE: its requirements become [{Crafting, Fieldcraft, [Tools]}, {Crafting, Workbench,
   [Workbench_SkyyAccessories]}] - the vanilla two-requirement pattern (28 vanilla recipes, e.g. Bench_Campfire, Tool_Pickaxe_Crude:
   Fieldcraft/Tools + Workbench/Workbench_*): it shows in pocket crafting AND at the top of the new tab. CraftingManager accepts a recipe
   when ANY requirement matches the bench, so it is never harder to get. /craft (SkyySacks) dedupes recipe ids (TreeSet): no double entry.
 - THE TAB ITSELF is added at RUNTIME (tools/skyywbtab.py = the one source for both mods; engine proof there and in WB.probe, which stops
   this build when any of it changes): no asset can inherit from Bench_WorkBench (an asset that is its own parent fails to load) and a full
   Bench_WorkBench.json override collides with other mods that override it (one winner; the loser's tab and recipes vanish). start()
   appends the category to every Workbench CraftingBench (copy-on-write array), a LoadedAssetsEvent listener (BlockType + CraftingRecipe)
   re-applies it after an asset reload. SkyyAccessories is the OWNER: it always ends with its own entry (it replaces SkyySacks' fallback
   entry in place) and its own order, so the result is the same whichever mod starts first; SkyySacks 0.7.10 alone adds the same tab
   for its bags (never invisible).
 - THE ORDER (owner only, WbRank): the server sends the tab's recipes as a TreeSet in crafting progression - Accessory Bag, the Normal
   bags, then tier by tier Normal -> Unique -> Rare -> Legendary (inside a tier: stat accessories Health, Stamina, Mana, Regeneration,
   Speed; bench accessories in the mod's bench order, numeral up; then that tier's bags Mining, Foraging, Farming, Combat, Smithing), the
   Omni Accessory next to last and the Mythic Omni Bag last. Whether the CLIENT keeps the order the server sends is UNVERIFIED (native
   client; the window data is an ordered JSON array, nothing in assets or packets is a sort field).
Also: VERSION 0.5.2 (jar name, manifest, kit header, ready line); server.lang + the tab name (2 lines); the icon PNG (copied from Assets.zip
at build time into Common/Icons/CraftingCategories/SkyyAccessories/). Unchanged on purpose: every class but the plugin, every other asset.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.1.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.5.2.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.5.1"
s = raw.decode("utf8").replace("\r\n", "\n")
OLD = s
LF = "\n"


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


assert 'VERSION = "0.5.1"\n' in s and "skyywbtab" not in s, "the source must be the generated 0.5.1 script"
REG0 = s.count("registerCommand(")

# ---------------------------------------------------------------------------------------------------------------- header + version
rep('''"""SkyyAccessories 0.5.1 - build script (derived from the generated build_skyyaccessories_0.5.py by tools/acc_0_5_1_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.1.py            -> SkyyAccessories/SkyyAccessories-0.5.1.jar
       python build_skyyaccessories_0.5.1.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.1.py             (bare JVM -Xverify:all: every 0.5 check + the hidden flags + the 0.5.1 update)
''', '''"""SkyyAccessories 0.5.2 - build script (derived from the generated build_skyyaccessories_0.5.1.py by tools/acc_0_5_2_patch.py - edit
the patch, not this file)
Run:   python build_skyyaccessories_0.5.2.py            -> SkyyAccessories/SkyyAccessories-0.5.2.jar
       python build_skyyaccessories_0.5.2.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
Test:  python test_skyyaccessories_0.5.2.py             (bare JVM -Xverify:all: every 0.5.1 check + the Workbench tab + compare with 0.5.1)
0.5.2: THE WORKBENCH TAB "Accessories & Bags" (Skyy 2026-10-01: "make a new tab for accessories, and sacks. list them in the order you
     would craft them. low levels first. with legendries and omnis at the bottom."; full notes in tools/acc_0_5_2_patch.py, engine proof
     in tools/skyywbtab.py): every accessory recipe (Workbench requirement Categories ["Workbench_Crafting"] -> ["Workbench_SkyyAccessories"];
     the pocket Accessory Bag keeps Fieldcraft/Tools and ALSO lists in the tab) and every SkyySacks 0.7.10 bag recipe in one new Workbench
     tab, added at runtime to every Workbench (start() + an asset reload listener; this mod OWNS the tab and its order, SkyySacks carries a
     fallback copy). Order sent by the server: Accessory Bag, Normal bags, then Normal -> Unique -> Rare -> Legendary (stat accessories,
     bench accessories, bags), Omni Accessory, Mythic Omni Bag last (client side UNVERIFIED). Ingredients, outputs and tiers unchanged.
''')
rep('VERSION = "0.5.1"\n', 'VERSION = "0.5.2"\n')
rep('''import skyyui as SUI    # 0.4.5: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
''', '''import skyyui as SUI    # 0.4.5: the ONE shared vanilla UI kit (research/Vanilla-UI-Style-Guide.md); not "as UI"
import skyywbtab as WB  # 0.5.2: the Workbench tab "Accessories & Bags" (one source with SkyySacks 0.7.10; this mod is the OWNER)
''')

# ---------------------------------------------------------------------------------------------------------------- the runtime part
rep('''# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
''', '''# ================= 0.5.2: the Workbench tab (tools/skyywbtab.py; WB.probe stops the build when an engine fact it relies on changed)
print(WB.probe(pool))
assert tuple(b[0] for b in ACTIVE) == WB.BENCHES and dict((b[0], b[3]) for b in ACTIVE) == WB.BENCH_TIERS, \\
    "0.5.2: the bench table changed - update BENCHES / BENCH_TIERS in tools/skyywbtab.py (the tab order)"
WB_CLASSES = WB.emit(pool, CtField, CtNewMethod, CtNewConstructor, PKG, True, "SkyyAccessories")   # OWNER

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
''')
rep('''  getEntityStoreRegistry().registerSystem(new @PKG@.AccEffects());
  @PKG@.MoveSync.checkProto("SkyyAccessories");
''', '''  getEntityStoreRegistry().registerSystem(new @PKG@.AccEffects());
  @PKG@.MoveSync.checkProto("SkyyAccessories");
''' + "@WBSETUP@")
rep('''  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());   // 0.4.4: config:def / config:fn:SkyyAccessories - LAST, after the config load
}""".replace("@READY@", jlit(_READY)))
''', '''  @PKG@.CfgPub.start(getDataDirectory().getParent(), getLogger());   // 0.4.4: config:def / config:fn:SkyyAccessories - LAST, after the config load
}""".replace("@READY@", jlit(_READY)).replace("@WBSETUP@", WB.setup_java(PKG)))
pl.addMethod(CtNewMethod.make(WB.start_java(PKG), pl))   # 0.5.2: the Workbench tab once every asset pack is loaded
''')
rep('''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear):
    c.writeFile(OUT)
''', '''for c in (dfs, st_, cfg_, fn, page, fac, rcmd, cmd, tick, eff, pl, mvs_, lcmd, gcmd, tcmd, adm, gtk, gfn, rtk, note, gear):
    c.writeFile(OUT)
for c in WB_CLASSES:   # 0.5.2: WbRank, WbTab, WbAssetL
    c.writeFile(OUT)
''')

# ---------------------------------------------------------------------------------------------------------------- the recipes
rep('''WB_REQ = [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}]
''', '''WB_REQ = [{"Type": "Crafting", "Id": "Workbench", "Categories": [WB.TAB_ID]}]   # 0.5.2: the new tab (was the vanilla Crafting tab)
''')
rep('''FIELD_REQ = [{"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["Tools"]}]
''', '''FIELD_REQ = [{"Type": "Crafting", "Id": "Fieldcraft", "Categories": ["Tools"]}]
BAG_REQ = FIELD_REQ + WB_REQ   # 0.5.2: the Accessory Bag stays pocket crafting AND lists first in the Workbench tab (vanilla two-requirement pattern)
''')
rep('''    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], FIELD_REQ, "SkyyAccBag"), indent=2)
''', '''    [{"ResourceTypeId": "Wood_Trunk", "Quantity": 4}, {"ItemId": "Ingredient_Fabric_Scrap_Cotton", "Quantity": 4}], BAG_REQ, "SkyyAccBag"), indent=2)
''')
rep('''files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"
print("accessory items:", count, "retired (no recipe):", retired_count)
''', '''lang.extend(WB.LANG_LINES)   # 0.5.2: the tab name (benchCategories.workbench.skyyaccessories + the server. twin)
files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"
# 0.5.2: the tab icon = Assets.zip's Utility_Bag_Seed.png (the Accessory Bag's own icon), copied into the jar where tab icons live
files["Common/" + WB.icon_path("SkyyAccessories")] = WB.icon_png(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
print("accessory items:", count, "retired (no recipe):", retired_count)


def _wbtab_checks():
    """0.5.2 build checks: every recipe of this mod in the new tab and nowhere else, the Accessory Bag still pocket crafting, the full
    in-tab order (both mods) printed and asserted, ingredients / outputs untouched (only BenchRequirement differs from 0.5.1's rule)"""
    own = [i for i in WB.EXPECTED if i.startswith(("Skyy_Accessory_", "Skyy_Talisman_"))]
    got = WB.recipe_checks(files, own, bag_req_id=BAG)
    assert len(got) == 47 and got[BAG][0] == FIELD_REQ[0], len(got)
    lmap = dict(l.split("=", 1) for l in lang if "=" in l)
    names = WB.default_names()
    for i in own:
        names[i] = lmap["server.items.%s.name" % i]
    for l in WB.LANG_LINES:
        assert l in lang, l
    WB.order_print(names, ("Skyy_Accessory_", "Skyy_Talisman_"))
    print("Workbench tab: %d recipes of this mod in '%s' (Accessory Bag also in pocket crafting), none in a vanilla tab; tab protocol %s"
          % (len(got), WB.TAB_TEXT, WB.WB_VERSION))


_wbtab_checks()
''')

# ---------------------------------------------------------------------------------------------------------------- final checks
assert s.count("registerCommand(") == REG0, "command registrations changed"
assert s.count("registerSystem(") == 1, "one registerSystem per class (AccEffects only)"
assert 'VERSION = "0.5.2"' in s and s.count("WB.emit(") == 1 and s.count("@WBSETUP@") == 2 and '"Categories": ["Workbench_Crafting"]' not in s
for _a, _b in (("WB_CLASSES = WB.emit(", "public void setup() {"), ("public void setup() {", "WB.start_java(PKG)"),
               ("lang.extend(WB.LANG_LINES)", 'files["Server/Languages/en-US/server.lang"] = "\\n".join(lang)'),
               ("BAG_REQ = FIELD_REQ + WB_REQ", "BAG_REQ, \"SkyyAccBag\")")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:40], _b[:40])
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.5.1
print("wrote", dst, "(%d lines; 0.5.1 had %d)" % (s.count(LF), OLD.count(LF)))
