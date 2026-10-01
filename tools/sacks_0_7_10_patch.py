"""Derive SkyySacks/build_skyysacks_0.7.10.py from the SET pin 0.7.9 (edit THIS file, then regenerate: python tools/sacks_0_7_10_patch.py).
0.7.10 = TWO CHANGES, both Skyy 2026-10-01:
 A. CHARCOAL GOES IN THE SMITHING BAG. Skyy (screenshot: Charcoal x8 staying in the hotbar), verbatim: "charcoal should go in the smithing
    bag." Charcoal's real id is Ingredient_Charcoal (Assets.zip Server/Item/Items/Ingredient/Ingredient_Charcoal.json: ResourceTypes
    [Fuel], FuelQuality 6, the vanilla Furnace makes it). It stayed out because SackDefs.homeOf matched no rule for it (it is not a
    Rubble_ id). It joins SMITH_EXACT (the exact-id part of the Smithing rule, next to the leather strap and iron stud), so it flows through
    SMITH_JAVA -> homeOf -> catOf: auto-pickup (the 2 s sweep) and Deposit all put it in a Smithing bag of any rarity or the Mythic Omni Bag;
    without one it stays in the inventory; withdraw / Pick up all take it out like any stored item; benches and /craft use it from the bag
    as they use every pooled item (the /craft Furnace fuel list already reads bags - "logs, planks, sticks and charcoal burn"). The
    Smithing bag text (item descriptions + the bag view) says "... iron studs and charcoal". Nothing else re-routes (harness C: every other
    id of Assets.zip classifies exactly as in 0.7.9). Nothing to migrate: charcoal was never pooled.
    REPORT ONLY (not added, for Skyy): the other smelting / fuel items are NOT in the Smithing bag - Ingredient_Stick (FuelQuality 4),
    Ingredient_Fibre (2), Ingredient_Tree_Bark (3), Ingredient_Tree_Sap (6) and the Wood_* logs / planks are in the Foraging bag; vanilla
    has no coal, flux or slag item (the harness prints every FuelQuality item with its bag).
 B. THE WORKBENCH TAB "Accessories & Bags" (Skyy: "make a new tab for accessories, and sacks. list them in the order you would craft them.
    low levels first. with legendries and omnis at the bottom."): the 21 bag recipes (20 tiered bags + the Mythic Omni Bag) move from the
    vanilla Workbench Crafting tab to the new tab Workbench_SkyyAccessories, with every SkyyAccessories 0.5.2 recipe. Ingredients,
    outputs, quality and KnowledgeRequired unchanged; only BenchRequirement Categories ["Workbench_Crafting"] -> ["Workbench_SkyyAccessories"].
    The tab is added at runtime (tools/skyywbtab.py, the one source both mods import; engine proof there). SkyyAccessories OWNS the tab and
    its order; this mod carries a FALLBACK copy (OWNER = false): it adds the tab only when no tab with that id is there yet and sorts it
    only when nobody sorted it, so with both mods the result is SkyyAccessories' whichever starts first, and with SkyySacks alone the
    bags still show in the tab (never invisible). start() (new) applies it once every asset pack is loaded; a LoadedAssetsEvent listener
    (BlockType + CraftingRecipe) re-applies it after an asset reload. The tab icon (Assets.zip Utility_Bag_Seed.png, every bag's own icon)
    is copied into the jar at Common/Icons/CraftingCategories/SkyySacks/AccessoriesBags.png. /craft never reads categories: unchanged.
Also VERSION 0.7.10 (jar, manifest, kit header, ready line). Unchanged: everything else (class compare in the harness, section I).
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.9.py")
dst = os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.7.10.py")
raw = open(src, encoding="utf8", newline="").read()
CR = chr(13)
LF = chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)


def rep(old, new, count=1):
    global s
    assert s.count(old) >= 1, "anchor missing: " + old[:90]
    assert count != 1 or s.count(old) == 1, "anchor not unique: " + old[:90]
    s = s.replace(old, new, count)


assert 'VERSION = "0.7.9"' in s and "skyywbtab" not in s and "Ingredient_Charcoal" not in s, "the source must be the generated 0.7.9 script"
REG0 = s.count("registerCommand(")
SYS0 = s.count("registerSystem(")

# ================= docstring + version =================
rep('"""SkyySacks 0.7.9 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.9.py            -> SkyySacks/SkyySacks-0.7.9.jar' + LF
    + '       python build_skyysacks_0.7.8.py --deploy   -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world' + LF,
    '"""SkyySacks 0.7.10 - build script (javassist via jpype).' + LF
    + 'Run:   python build_skyysacks_0.7.10.py           -> SkyySacks/SkyySacks-0.7.10.jar' + LF
    + '       python build_skyysacks_0.7.10.py --deploy  -> also copies to Mods/SkyySacks.jar and enables it in the HUD mod world' + LF)
rep('differing SkyyCooking default (NOTE only); it fails when SkyyCooking stops publishing what the live line reads. Nothing else changed.' + LF + '"""' + LF,
    'differing SkyyCooking default (NOTE only); it fails when SkyyCooking stops publishing what the live line reads. Nothing else changed.' + LF
    + '0.7.10 (derived from 0.7.9 by tools/sacks_0_7_10_patch.py - edit the patch, not this file; both Skyy 2026-10-01): (A) "charcoal should go' + LF
    + 'in the smithing bag." -> Ingredient_Charcoal joins SMITH_EXACT: auto-pickup / Deposit all put it in a Smithing bag or the Mythic Omni' + LF
    + 'Bag, withdraw takes it out, nothing else re-routes; the Smithing bag text names charcoal. (B) "make a new tab for accessories, and' + LF
    + 'sacks ..." -> the 21 bag recipes move to the Workbench tab "Accessories & Bags" (Workbench_SkyyAccessories, tools/skyywbtab.py; added at' + LF
    + 'runtime by start() + an asset reload listener; SkyyAccessories 0.5.2 owns the tab and its order, this mod is the fallback copy so the' + LF
    + 'bags never vanish without it). Ingredients, outputs and KnowledgeRequired unchanged.' + LF
    + '"""' + LF)
rep('VERSION = "0.7.9"', 'VERSION = "0.7.10"')
rep('import skyycfg as CFG   # 0.7.6: the admin config kit (research/Server-Setup-Spec.md 4.12, tools/CONFIG-CONTRACT.md)' + LF,
    'import skyycfg as CFG   # 0.7.6: the admin config kit (research/Server-Setup-Spec.md 4.12, tools/CONFIG-CONTRACT.md)' + LF
    + 'import skyywbtab as WB  # 0.7.10: the Workbench tab "Accessories & Bags" (one source with SkyyAccessories 0.5.2, the owner)' + LF)

# ================= A. charcoal -> Smithing =================
rep('''             "Smithing": "bars and ingots, leather, hides, cloth bolts, fabric scraps, leather straps and iron studs"}''',
    '''             "Smithing": "bars and ingots, leather, hides, cloth bolts, fabric scraps, leather straps, iron studs and charcoal"}''')
rep('''SMITH_EXACT = ("Ingredient_Strap_Leather", "Ingredient_Stud_Iron")''',
    '''# 0.7.10 (Skyy 2026-10-01: "charcoal should go in the smithing bag."): Ingredient_Charcoal (the vanilla Furnace's fuel product, ResourceTypes
# [Fuel]) - it matched no rule before (not a Rubble_ id) and stayed in the inventory. _bag_ids_check verifies the id exists in Assets.zip.
SMITH_EXACT = ("Ingredient_Strap_Leather", "Ingredient_Stud_Iron", "Ingredient_Charcoal")''')

# ================= B. the Workbench tab: runtime part =================
rep('''# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
''', '''# ================= 0.7.10: the Workbench tab (tools/skyywbtab.py; WB.probe stops the build when an engine fact it relies on changed)
print(WB.probe(pool))
WB_CLASSES = WB.emit(pool, CtField, CtNewMethod, CtNewConstructor, PKG, False, "SkyySacks")   # FALLBACK copy (SkyyAccessories owns it)

# ================= plugin =================
pl.addField(CtField.make("public java.util.concurrent.ScheduledFuture ticker;", pl))
''')
rep('''  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());
}}""", pl))
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{''', '''  @WBSETUP@
  {PKG}.CfgPub.start(getDataDirectory().getParent(), getLogger());
}}""".replace("  @WBSETUP@\\n", WB.setup_java(PKG)), pl))
pl.addMethod(CtNewMethod.make(WB.start_java(PKG), pl))   # 0.7.10: the Workbench tab once every asset pack is loaded
pl.addMethod(CtNewMethod.make(f"""
protected void shutdown() {{''')
rep('''for c in (defs, sp, scfg, ksync, snot, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, pl):
    c.writeFile(OUT)
''', '''for c in (defs, sp, scfg, ksync, snot, pjob, pben, pst, swp, tick, sav, cmp, page, cmd, fac, mir, clt, ctk, rcmp, clog, cpg, ccmd, cfac, ptk, ptick, pl):
    c.writeFile(OUT)
for c in WB_CLASSES:   # 0.7.10: WbRank, WbTab, WbAssetL
    c.writeFile(OUT)
''')

# ================= B. the Workbench tab: recipes, lang, icon, checks =================
rep('''      "Recipe": {"Input": recipe_in, "BenchRequirement": [{"Type": "Crafting", "Id": "Workbench", "Categories": ["Workbench_Crafting"]}],''',
    '''      "Recipe": {"Input": recipe_in, "BenchRequirement": [{"Type": "Crafting", "Id": "Workbench", "Categories": [WB.TAB_ID]}],   # 0.7.10''')
rep('''files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"  # key items.<Id>.name in server.lang (pattern from Tamework)
''', '''lang.extend(WB.LANG_LINES)   # 0.7.10: the Workbench tab name (the same two lines SkyyAccessories 0.5.2 ships)
files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"  # key items.<Id>.name in server.lang (pattern from Tamework)
# 0.7.10: the tab icon of this mod's fallback copy = Assets.zip Utility_Bag_Seed.png (every bag's own icon), where tab icons live
files["Common/" + WB.icon_path("SkyySacks")] = WB.icon_png(os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip"))
''')
rep('''_bag_assets_check()
print("bag table: %s x %s + %s | caps %s | qualities %s" % (''', '''_bag_assets_check()


def _wbtab_checks():
    """0.7.10 build checks: the 21 bag recipes in the new tab and nowhere else, the full in-tab order (both mods) printed and asserted,
    the newest SkyyAccessories build script uses the same tab module (else its tab differs and the bags show in this mod's copy)"""
    import glob, re
    own = [i for i in WB.EXPECTED if i.startswith("Skyy_Sack_")]
    got = WB.recipe_checks(files, own)
    assert len(got) == 21 and sorted(got) == sorted(MANAGED_IDS + [BAG_OMNI])
    lmap = dict(l.split("=", 1) for l in lang if "=" in l)
    names = WB.default_names()
    for i in own:
        names[i] = lmap["server.items.%s.name" % i]
        assert names[i] == WB.default_names()[i], (i, names[i])
    for l in WB.LANG_LINES:
        assert l in lang, l
    WB.order_print(names, ("Skyy_Sack_",))
    def _v(p):
        m = re.search(r"_(\\d+(?:\\.\\d+)*)\\.py$", p)
        return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)
    acc = sorted(glob.glob(os.path.join(HERE, "..", "SkyyAccessories", "build_skyyaccessories_*.py")), key=_v)
    if acc and "import skyywbtab as WB" in open(acc[-1], encoding="utf8", errors="replace").read() and "WB.emit(pool, CtField, CtNewMethod, CtNewConstructor, PKG, True," in open(acc[-1], encoding="utf8", errors="replace").read():
        print("Workbench tab: %s owns the same tab (tools/skyywbtab.py protocol %s); this mod's copy is the fallback" % (os.path.basename(acc[-1]), WB.WB_VERSION))
    else:
        print("NOTE: the newest SkyyAccessories build script (%s) does not own the Workbench tab - the bags show in this mod's copy of it"
              % (os.path.basename(acc[-1]) if acc else "none"))
    print("Workbench tab: %d bag recipes in '%s', none in a vanilla tab" % (len(got), WB.TAB_TEXT))


_wbtab_checks()
print("bag table: %s x %s + %s | caps %s | qualities %s" % (''')

# ================= self-checks =================
assert 'VERSION = "0.7.10"' in s and s.count('WB.emit(pool, CtField, CtNewMethod, CtNewConstructor, PKG, False, "SkyySacks")') == 1 and s.count("@WBSETUP@") == 2
assert '"Categories": ["Workbench_Crafting"]' not in s and s.count('SMITH_EXACT = ("Ingredient_Strap_Leather", "Ingredient_Stud_Iron", "Ingredient_Charcoal")') == 1
assert s.count("registerCommand(") == REG0 and s.count("registerSystem(") == SYS0
for _a, _b in (("WB_CLASSES = WB.emit(", "public void setup() {{"), ("public void setup() {{", "WB.start_java(PKG)"),
               ("lang.extend(WB.LANG_LINES)", 'files["Server/Languages/en-US/server.lang"] = "\\n".join(lang)'),
               ("SMITH_EXACT = (", "SMITH_JAVA = ")):
    assert 0 <= s.find(_a) < s.find(_b), "order: %s before %s" % (_a[:40], _b[:40])
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
