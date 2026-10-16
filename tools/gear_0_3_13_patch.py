"""Derive SkyyGear/build_skyygear_0.3.13.py from the LIVE 0.3.12 (build_skyygear_0.3.12.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_3_12_patch.py). Edit THIS file, never the generated script; every anchor is asserted and every change is undone at the end to
prove nothing else changed. Run:
    python tools/gear_0_3_13_patch.py      then      python SkyyGear/build_skyygear_0.3.13.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.3.13.py

0.3.13 (2026-10-16, round "tools01", ULTRACODE size; Skyy 2026-10-16 "since we have a ton of forever tools, disable the normal verson everywhere.
so you cant make them, you dont seem them in the crafting, and you dont get them from chests, lost treasure bags or drops." + popups "All
lifelong kinds (Recommended),Pack mod tools too" and (owned ones) "Remove them"; + "make enchanted sticks too, and require them in the later
tool upgrades."; docs/answered/gear.md 2026-10-16 NORMAL TOOLS OFF EVERYWHERE + ENCHANTED STICKS):
1. NORMAL TOOLS OFF (Server Setup normal.off, on). A NORMAL tool = a pickaxe, hatchet, hoe or sickle of any metal (GearTool families 1 / 3 / 4 /
   5 by id: Tool_Pickaxe_*, Tool_Hatchet_*, Tool_Hoe_*, Tool_Sickle_* - the vanilla Wood / Scrap / Rusty ones too), a fishing rod
   (SkyyFishing_Rod_*), a watering can (vanilla Tool_Watering_Can*, our Tool_WaterCan_*) or an item id starting with a normal.extraIds entry
   (pack mods' tools by id - none of the packed mods has one today: The Armory's only tool-like item Hepta_Axe is a weapon; Multitools stays)
   that does NOT carry a lifelong stamp (the SkyyGear document's ll=1; unreadable / newer gear data counts as stamped = never touched).
   NEVER a shovel, the multitool (Tool_Hatchet_Pickaxe_Multitool_*), the Harvester (Tool_Sickle_Harvester_*), a lifelong (stamped) tool
   (any profile, retired ones too) or a lifelong tier-up (those are Anvil ladders, no recipes). GearLL.normKind(id) is the one rule.
   (a) NO RECIPE WORKS: GearLL.noCraft adds normKind -> GearCraftPreSys cancels CraftRecipeEvent$Pre (bench / pocket crafting; Creative
       still crafts), the chat line names the lifelong command.
   (b) NOT LISTED: every CraftingRecipe whose output is a normal tool (not the fishing rods: SkyyFishing's bench rod recipes ARE the lifelong
       pole's tier-up path; SkyyFishing already locks the Wooden rod) is REMOVED from the CraftingRecipe store at runtime
       (CraftingRecipe.getAssetStore().removeAssets - the way GearMulti removes a capped salvage recipe; CraftingPlugin.onRecipeRemove drops
       it from every bench registry, VERIFIED bytecode 2026-10-16), again after every Item / CraftingRecipe asset reload (the engine
       regenerates an item's recipe). Vanilla bench lists, SkyySacks' /craft (reads the store at run time), our Smithing page and the
       upgrade-cost reader all lose them. No vanilla or pack file is overridden. Switching normal.off off brings them back at the next restart.
   (c) NEVER FROM LOOT: every ItemDropList that can yield a normal tool (ItemDropContainer.getAllDrops) gets a GearNormDrop around its
       container (ItemDropList.container by reflection - GearStick's way; inside a GearStick when the list has one) that strips normal-tool
       ItemDrops from every roll. Every roll goes through a list's container: chests (StashPlugin.stash), NPC death drops
       (NPCDamageSystems$DropDeathItems), block drops (BlockHarvestUtils.getDrops), SkyyExploration's Lost Loot / supply drops
       (ItemModule.getRandomItemDrops), objectives' GiveItems, coops - VERIFIED callers 2026-10-16. Pack mods' lists the same way (memory
       only; The Armory's Armory_Zone1_Loot names the vanilla Rusty Sickle). Re-checked every 30 s on block breaks (an asset reload makes
       new list objects) and after every reload event. So SkyyMobs and SkyyExploration need no change.
   (d) CHESTS ALREADY ROLLED / PLACED: any block container (world loot chests, player chests, island chests) is stripped of normal tools when
       it is opened (UseBlockEvent$Pre, before the window shows) or broken (BreakBlockEvent, before it drops) - GearChestOpen's hook points,
       even while part.chests is off. Each stack is logged (NORMOFF-CHEST in gear.log).
   (e) OWNED ONES ARE REMOVED ONCE PER PROFILE (normal.removeOwned, on; PROJECT-RULES 4 one-time rules): at the first lifelong look after the
       profile's kits are done (migrated=1, the pole kit + the can kit given), on the world thread: a verified History copy of the
       profile's lifelong registry file first (Skyy_SkyyGear/normoff/history/), the journal normOff.pend on disk, then every normal stack in
       the hotbar / storage / backpack / armor / utility / tools sections is removed (count-checked; a Requip-stamped one is reported used up
       to SkyyWardrobe: wardrobe:fn:gone) and every normal tool id in the Magic Bags (sacks:fn:all / take / commit), each logged
       (gear.log NORMOFF-REMOVE + the per-profile undo record normoff/<profile>.log, metadata kept), then the run-once marker normOff=1.
       The Requip pool (IN entries: wardrobe:fn:list all -> fetch -> removed -> gone) once more: marker normOffRq=1. Nothing is given back.
       Not reachable (follow-ups): the Vault (SkyyVault has lifelong-only bridges), Auction House listings, items on the ground.
       UNDO (admin): /gear normoff undo <player> (online) - at that player's next inventory look every recorded stack comes back (Requip
       stamp removed), the markers become 'undone' (never removed again). /gear normoff = the counters.
2. ENCHANTED STICKS IN THE LATER TIER-UPS (lifelong.stickCost, default 0,0,0,2,4,8,16,32 = Crude .. Onyxium): a lifelong tool tier-up
   (pickaxe, hatchet, hoe, sickle, watering can, Harvester, multitool; not the pole - SkyyFishing's bench tiers it) INTO Thorium costs 2
   Enchanted Sticks on top of its ladder cost, Cobalt 4, Adamantite 8, Mithril 16, Onyxium 32 (GearUp.cost: one reader for the Tools tab,
   the Upgrade tab and the Anvil; have / need / payment from inventory + bags as every other material). The Enchanted Stick item is
   SkyyCollections 0.2.20's (tools/skyyench.py row "Stick"); without it loaded no stick is asked (one WARN).
3. GREAT SHIELD TWIN (coordinator addition, same round): SkyyArmory 0.1.29's Weapon_GreatShield_<Metal> (Copper .. Onyxium, the Spellblade
   Great Shield; its hits = a share of the same-metal longsword swing H) would get its own "GreatShield" family whose base is the Iron shield
   = the documented 0.2.8 / 0.2.9 trap (a constant fraction of the intended hit). GearBase.kunaiTwin now maps Weapon_GreatShield_<Metal> to
   Weapon_Longsword_<Metal> (that longsword's K: ratio + family base divisor; no longsword of that metal = the id itself); the build asserts no
   vanilla id starts with Weapon_GreatShield_ and every metal's longsword exists. Levels already band by the metal word (= the longsword's).
(1e note: a profile with no normal tool in the inventory / bags gets only the marker - no History copy, no journal.)
FIX ROUND (tools01 critics, 2026-10-16): B2 STRAGGLERS - after the markers, every lifelong look (inventory change) runs a cheap inventory check
and removes a normal tool that turns up later (Vault, AH, a pre-update item) the same way (record + NORMOFF-STRAGGLER log; Creative and
'undone' profiles skipped); B3 GearNorm.tick re-runs the recipes when the recipe store changed size since the last run (a reload missed while
busy); A1 /gear normoff undo with nothing recorded for the target's active profile says so and queues nothing; A2 the chest strip also writes
the opener's undo record and never strips an 'undone' profile's own opens; A3 /lifelong's re-pick RETIRES the old tool (lrt=1) instead of
making it plain while normal tools are off; A4 rods / cans count as normal only while their kit is handed out (lifelong.poleKit,
part.can + lifelong.canKit) - nobody is left without a tool of a kind.
SAVED DATA: per-profile registry keys normOff / normOffAt / normOffN / normOff.pend / normOffRq / normOffRqAt (lifelong/<pk>.properties);
Skyy_SkyyGear/normoff/<pk>.log (the undo record) + normoff/history/. New Server Setup rows (absent = default; no one-time config update):
normal.off, normal.removeOwned, normal.extraIds, lifelong.stickCost.
ROLLBACK 0.3.13 -> 0.3.12: item-safe (removed tools stay removed; 0.3.12 ignores the new keys); normal tools become craftable / droppable again.
"""
import os
import re
import sys
import ast

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.12.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.3.13.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.3.12"' in s and "GENERATED by tools/gear_0_3_12_patch.py" in s and "0.3.13" not in s, "not the generated 0.3.12 script"
assert "GearNorm" not in s and "normKind" not in s and "stickCost" not in s
CHANGES = []


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)
    CHANGES.append((new, old, count))


def before(anchor, text):
    rep(anchor, text + anchor)


def after(anchor, text):
    rep(anchor, anchor + text)


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyGear") != "0.3.12":
    print("NOTE: tools/deploy_set.py SET pins SkyyGear %s, this patch derives from 0.3.12" % _set.get("SkyyGear"))

STICK_ID = "Skyy_Ench_Stick"
STICK_DEF = "0,0,0,2,4,8,16,32"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import skyyench as _EN
assert STICK_ID in _EN.IDS, "tools/skyyench.py has no Enchanted Stick row"

# ================================================================================================================ docstring + version
rep('''"""SkyyGear 0.3.12 - build script (javassist via jpype). GENERATED by tools/gear_0_3_12_patch.py from the LIVE 0.3.11 (itself GENERATED by
tools/gear_0_3_11_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.12.py -> SkyyGear/SkyyGear-0.3.12.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.12.py
''', '''"""SkyyGear 0.3.13 - build script (javassist via jpype). GENERATED by tools/gear_0_3_13_patch.py from the LIVE 0.3.12 (itself GENERATED by
tools/gear_0_3_12_patch.py) - edit the patch, never this file. Run: python SkyyGear/build_skyygear_0.3.13.py -> SkyyGear/SkyyGear-0.3.13.jar
(never --deploy). Harness: python SkyyGear/test_skyygear_0.3.13.py

0.3.13 = NORMAL TOOLS OFF EVERYWHERE + ENCHANTED STICKS (notes: tools/gear_0_3_13_patch.py): normal (not lifelong) pickaxes, hatchets, hoes,
sickles, fishing rods and watering cans are never crafted, listed, looted or dropped (recipes removed at runtime, drop lists filtered, chests
stripped on open / break) and the ones players own are removed once per profile (logged, admin undo /gear normoff undo); lifelong tier-ups
into Thorium and up also cost Enchanted Sticks (lifelong.stickCost).

--- 0.3.12 notes ---
''')
rep('VERSION = "0.3.12"\n', 'VERSION = "0.3.13"\n')

# ================================================================================================================ Server Setup rows + GearCfg
after('''    ("harvester.ladders", "Harvester tier-up costs", "lifelong", "text", HARV_LAD_DEF, "0", "2000", "", "", "live,danger",
     "Harvester tiers on the Anvil, like lifelong.ladders: A>B(Id*25), ladders joined by commas.", "field:GearCfg.HARV_LADDERS;check=GearUp.checkLadders"),
''', '''    # 0.3.13 NORMAL TOOLS OFF + ENCHANTED STICKS (tools/gear_0_3_13_patch.py)
    ("normal.off", "Normal tools off", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "No normal pickaxe, hatchet, hoe, sickle, rod or can to craft, loot or drop. Off: restart (recipes).", "field:GearCfg.NORM_ON;after=GearNorm.refresh"),
    ("normal.removeOwned", "Remove owned normal tools", "lifelong", "bool", "true", "", "", "", "", "live,danger",
     "Once per profile: normal tools in the inventory, bags and Requip go (logged; /gear normoff undo).", "field:GearCfg.NORM_OWNED"),
    ("normal.extraIds", "More normal tool ids", "lifelong", "text", "", "0", "500", "", "", "live,danger",
     "Item id starts (pack mods' tools) that count as normal tools too, joined by commas. Empty = none.", "field:GearCfg.NORM_EXTRA;after=GearNorm.refresh"),
    ("lifelong.stickCost", "Enchanted Sticks per tier-up", "lifelong", "text", "%s", "1", "60", "", "", "live,danger",
     "Crude to Onyxium: Enchanted Sticks a tool tier-up INTO that tier costs extra (8 numbers 0-999).", "field:GearCfg.LL_STICKS;check=GearUp.checkSticks"),
''' % STICK_DEF)
rep('''           "part.harvester", "harvester.rebirthGate", "harvester.ladders"}''', '''           "part.harvester", "harvester.rebirthGate", "harvester.ladders",
           # 0.3.13: normal tools off (item supply = economy; the owned ones are removed) + the Enchanted Stick tier-up cost
           "normal.off", "normal.removeOwned", "normal.extraIds", "lifelong.stickCost"}''')
after('''assert all(32 <= ord(_c) < 127 for _c in G312_HEAD) and "=" not in G312_HEAD
''', '''G313_HEAD = "# ---- normal tools off, Enchanted Sticks in the later tier-ups (SkyyGear 0.3.13) ----"
G313_ROWK = ["normal.off", "normal.removeOwned", "normal.extraIds", "lifelong.stickCost"]
assert all(32 <= ord(_c) < 127 for _c in G313_HEAD) and "=" not in G313_HEAD
''')
after('''    L += ["", G312_HEAD]        # 0.3.12: the new rows (no one-time update adds them; absent = the default)
    for k in G312_ROWK:
        scal(k)
''', '''    L += ["", G313_HEAD]        # 0.3.13: the new rows (no one-time update adds them; absent = the default)
    for k in G313_ROWK:
        scal(k)
''')
rep('''              ("HARV_LADDERS", "String", jstr(HARV_LAD_DEF))]''', '''              ("HARV_LADDERS", "String", jstr(HARV_LAD_DEF)),
              # 0.3.13 normal tools off + the Enchanted Stick tier-up cost
              ("NORM_ON", "boolean", "true"), ("NORM_OWNED", "boolean", "true"), ("NORM_EXTRA", "String", jstr("")),
              ("LL_STICKS", "String", jstr("%s"))]''' % STICK_DEF)
_hl = re.findall(r'\n(  HARV_LADDERS = ptext\(p, "harvester\.ladders", "[^"\n]*"\)\.trim\(\);\n)', s)
assert len(_hl) == 1, _hl
after(_hl[0], '''  // 0.3.13 (HARNESS SEAM ONLY: -Dskyy.harness.noNormOff=true = the 0.3.12 flow the older harness children were written for)
  NORM_ON = pbool(p, "normal.off", true) && !Boolean.getBoolean("skyy.harness.noNormOff");
  NORM_OWNED = pbool(p, "normal.removeOwned", true) && !Boolean.getBoolean("skyy.harness.noNormOff");
  NORM_EXTRA = ptext(p, "normal.extraIds", "").trim();
  LL_STICKS = Boolean.getBoolean("skyy.harness.noNormOff") ? "0,0,0,0,0,0,0,0" : ptext(p, "lifelong.stickCost", "%s").trim();
''' % STICK_DEF)

# ================================================================================================================ 1a: the one rule + no recipe works
rep(r'''M(gll, "public static boolean noCraft(String id) { return @PKG@.GearCfg.LL_ON && ((@PKG@.GearCfg.LL_NOCRAFT && kOf(id) >= 0) || (@PKG@.GearCfg.CAN_ON && @PKG@.GearCfg.CAN_NOVAN && \"Tool_Watering_Can\".equals(id))); }")          # 0.3.12: + the vanilla can (can.noVanilla)''',
    r'''# 0.3.13 NORMAL TOOLS OFF (tools/gear_0_3_13_patch.py 1): the one rule - is this item id a NORMAL tool kind? (pickaxe / hatchet / hoe / sickle of any
# metal, a fishing rod, a watering can, a normal.extraIds start); never the multitool or the Harvester; the stamp is checked by GearNorm.normal
F(gll, "public static volatile String NX_SRC = null;")
F(gll, "public static volatile String[] NX = new String[0];")
M(gll, r"""
public static String[] normExtra() {
  String v = @PKG@.GearCfg.NORM_EXTRA;
  if (v == null) v = "";
  if (!v.equals(NX_SRC)) {
    java.util.ArrayList l = new java.util.ArrayList();
    String[] p = v.split(",");
    for (int i = 0; i < p.length && l.size() < 64; i++) {
      String t = p[i].trim();
      if (t.length() >= 3) l.add(t);
    }
    String[] a = new String[l.size()];
    for (int i = 0; i < a.length; i++) a[i] = (String) l.get(i);
    NX = a;
    NX_SRC = v;
  }
  return NX;
}""")
M(gll, r"""
public static boolean normKind(String id) {
  if (id == null || id.length() == 0) return false;
  if (@PKG@.GearData.multiId(id) || id.startsWith(HARV_PRE)) return false;          // never the multitool, never the Harvester
  // critic A4: a rod / a can is only normal while that lifelong kind is handed out (never leave a player with no tool of a kind)
  if (@PKG@.GearData.pole(id)) return @PKG@.GearCfg.LL_POLEKIT;
  if (@PKG@.GearData.can(id) || id.startsWith("Tool_Watering_Can")) return @PKG@.GearCfg.CAN_ON && @PKG@.GearCfg.CAN_KIT;
  int f = @PKG@.GearData.toolFam(id);
  if (f == 1 || f == 3 || f == 4 || f == 5) return true;          // pickaxe, hatchet, hoe, sickle (2 = the shovel stays)
  String[] x = normExtra();
  for (int i = 0; i < x.length; i++) if (id.startsWith(x[i])) return true;
  return false;
}""")
M(gll, "public static boolean noCraft(String id) { return @PKG@.GearCfg.LL_ON && ((@PKG@.GearCfg.LL_NOCRAFT && kOf(id) >= 0) || (@PKG@.GearCfg.CAN_ON && @PKG@.GearCfg.CAN_NOVAN && \"Tool_Watering_Can\".equals(id)) || (@PKG@.GearCfg.NORM_ON && normKind(id))); }")          # 0.3.12: + the vanilla can (can.noVanilla); 0.3.13: + every normal tool (normal.off)''')
rep('''        int k0 = @PKG@.GearLL.kOf(id0);
        if (k0 < 0) k0 = @PKG@.GearLL.CAN;          // 0.3.12: the vanilla Iron Watering Can (can.noVanilla) -> "one can for life ... /can"
        if (pr0 != null) pr0.sendMessage(@MSG@.raw("[Gear] Tools are not crafted any more - you keep one " + @PKG@.GearLL.KIND[k0] + " for life. Tier it up on the Anvil (/smithing); lost it? /" + @PKG@.GearLL.KIND[k0]).color(@PKG@.GearDefs.C_BAD));''',
    '''        int k0 = @PKG@.GearLL.kOf(id0);
        if (k0 < 0 && id0.startsWith("Tool_Watering_Can")) k0 = @PKG@.GearLL.CAN;          // 0.3.12: the vanilla Iron Watering Can (can.noVanilla) -> "one can for life ... /can"
        if (pr0 != null && k0 >= 0) pr0.sendMessage(@MSG@.raw("[Gear] Tools are not crafted any more - you keep one " + @PKG@.GearLL.KIND[k0] + " for life. Tier it up on the Anvil (/smithing); lost it? /" + @PKG@.GearLL.KIND[k0]).color(@PKG@.GearDefs.C_BAD));
        else if (pr0 != null) pr0.sendMessage(@MSG@.raw("[Gear] Normal tools are switched off here - your lifelong tools do the job: /pickaxe /hatchet /hoe /sickle /pole /can").color(@PKG@.GearDefs.C_BAD));          // 0.3.13: a normal.extraIds tool''')

# ================================================================================================================ 1d: the chest hook points also run while part.chests is off
rep('''    if (!@PKG@.GearCfg.PART_CHESTS) return;
    @VECI@ tb = e.getTargetBlock();
    if (tb == null) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;''', '''    if (!@PKG@.GearCfg.PART_CHESTS && !(@PKG@.GearCfg.LL_ON && @PKG@.GearCfg.NORM_ON)) return;          // 0.3.13: the normal-tool strip runs in process()
    @VECI@ tb = e.getTargetBlock();
    if (tb == null) return;
    @REF@ r = chunk.getReferenceTo(idx);
    if (r == null) return;
    @PR@ pr = (@PR@) st.getComponent(r, @PR@.getComponentType());
    if (pr == null) return;''')
rep('''    if (e.isCancelled() || !@PKG@.GearCfg.PART_CHESTS) return;''',
    '''    if (e.isCancelled() || (!@PKG@.GearCfg.PART_CHESTS && !(@PKG@.GearCfg.LL_ON && @PKG@.GearCfg.NORM_ON))) return;          // 0.3.13: + the normal-tool strip''')

# ================================================================================================================ 2: Enchanted Sticks in the later tier-ups (GearUp.cost)
rep('''public static Object[] cost(String from, String to) {
  if (from == null || to == null) return null;
  Object[] wr = written(from, to);          // a row cost "A>B(Id*N+...)" wins''', '''public static Object[] cost0(String from, String to) {
  if (from == null || to == null) return null;
  Object[] wr = written(from, to);          // a row cost "A>B(Id*N+...)" wins''')
before('''M(gup, r"""
public static String costText(Object[] c) {''', r'''# 0.3.13 ENCHANTED STICKS (Skyy 2026-10-16 "make enchanted sticks too, and require them in the later tool upgrades."; lifelong.stickCost = 8
# numbers Crude .. Onyxium): a lifelong tool tier-up INTO tier t costs STK[t] Enchanted Sticks on top of its ladder / recipe cost - the pickaxe,
# hatchet, hoe, sickle, watering can, Harvester and multitool (never the pole: SkyyFishing's bench tiers it). cost() is the one reader (Tools tab,
# Upgrade tab, Anvil: have / need / payment). No stick item loaded (SkyyCollections < 0.2.20) = no stick asked.
F(gup, "public static volatile String STICK_ID = %s;" % jstr("Skyy_Ench_Stick"))          # a field only so a harness can point it at another item
F(gup, "public static volatile String STK_SRC = null;")
F(gup, "public static volatile int[] STK = new int[] { 0, 0, 0, 2, 4, 8, 16, 32 };")
F(gup, "public static final long[] SN = new long[2];")          # 0 tier-up costs with sticks added, 1 asked without the stick item
M(gup, r"""
public static int[] parseSticks(String v) {
  if (v == null) return null;
  String[] p = v.split(",");
  if (p.length != 8) return null;
  int[] a = new int[8];
  for (int i = 0; i < 8; i++) {
    try { a[i] = Integer.parseInt(p[i].trim()); } catch (Throwable t) { return null; }
    if (a[i] < 0 || a[i] > 999) return null;
  }
  return a;
}""")
M(gup, r"""
public static String checkSticks(String key, String value) {
  return parseSticks(value) == null ? "Enchanted Sticks per tier-up: 8 whole numbers from 0 to 999 (Crude, Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium), joined by commas." : null;
}""")
M(gup, r"""
public static int[] sticks() {
  String v = @PKG@.GearCfg.LL_STICKS;
  if (v != null && !v.equals(STK_SRC)) {
    int[] a = parseSticks(v);
    if (a == null) @PKG@.Gear.warnOnce("stickcost:" + v.hashCode(), "config.properties: lifelong.stickCost '" + v + "' is not 8 numbers 0-999 - the default 0,0,0,2,4,8,16,32 applies");
    STK = a == null ? new int[] { 0, 0, 0, 2, 4, 8, 16, 32 } : a;
    STK_SRC = v;
  }
  return STK;
}""")
# the Enchanted Sticks the step from -> to costs (0 = none): a lifelong kind's tool (not the pole) or a multitool, by the NEW tier
M(gup, r"""
public static int stickFor(String from, String to) {
  if (!@PKG@.GearCfg.LL_ON || to == null || from == null) return 0;
  boolean tool = (@PKG@.GearLL.kOf(to) >= 0 && !@PKG@.GearLL.isPole(to)) || @PKG@.GearData.multiId(to);
  if (!tool) return 0;
  int t = @PKG@.GearLL.tier(to);
  int[] a = sticks();
  if (t < 0 || t >= a.length) return 0;
  return a[t];
}""")
M(gup, r"""
public static Object[] cost(String from, String to) {
  Object[] c = cost0(from, to);
  if (c == null) return null;
  int n = stickFor(from, to);
  if (n <= 0) return c;
  String sid = STICK_ID;
  if (sid == null || @PKG@.Gear.item(sid) == null) {
    SN[1] = SN[1] + 1L;
    @PKG@.Gear.warnOnce("nostick", "lifelong.stickCost asks Enchanted Sticks but the item " + sid + " is not loaded (SkyyCollections 0.2.20+) - tier-ups cost no sticks until it is");
    return c;
  }
  String[] ids = (String[]) c[0];
  int[] q = (int[]) c[1];
  int j = -1;
  for (int i = 0; i < ids.length; i++) if (sid.equals(ids[i])) j = i;
  String[] ni = new String[j >= 0 ? ids.length : ids.length + 1];
  int[] nq = new int[ni.length];
  for (int i = 0; i < ids.length; i++) { ni[i] = ids[i]; nq[i] = q[i]; }
  if (j >= 0) nq[j] = nq[j] + n;
  else { ni[ids.length] = sid; nq[ids.length] = n; }
  SN[0] = SN[0] + 1L;
  return new Object[] { ni, nq, c.length > 2 ? c[2] : "row" };
}""")
''')

# ================================================================================================================ 3: the great shield twin (coordinator, same round)
# SkyyArmory 0.1.29 (Skyy-approved Spellblade Great Shield) adds Weapon_GreatShield_<Metal> (Copper .. Onyxium) whose hits are a share of the
# SAME-METAL LONGSWORD swing (H, SkyyArmory GS_H). GearBase.family would give them their own "GreatShield" family whose base is the Iron shield =
# the 0.2.8 / 0.2.9 trap (a constant fraction of the intended hit). Fix = the 0.2.9 twin rule: kunaiTwin maps Weapon_GreatShield_<Metal> to
# Weapon_Longsword_<Metal> (that longsword's K: ratio + family base divisor) -> shield hit / longsword hit at the same level = the Armory's share.
rep('''# 0.2.9: the Monk weapon twin (SkyyArmory 0.1.7): these prefixes + a metal (wraps: a cloth -> its metal column) take Weapon_Sword_<metal>'s K
TWIN_PRE = ["Weapon_Fist_Gauntlets_", "Weapon_Fist_Wraps_", "Weapon_Bo_"]''', """# 0.3.13: the great shield twin (SkyyArmory 0.1.29): Weapon_GreatShield_<Metal> takes Weapon_Longsword_<Metal>'s K (asserted: no vanilla id
# uses the prefix, every metal's longsword exists)
GS_TWIN_PRE = "Weapon_GreatShield_"
assert not [i for i in AZ_ITEMS if i.startswith(GS_TWIN_PRE)], "a vanilla id starts with Weapon_GreatShield_ - the twin would move it"
for _m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"):
    assert ("Weapon_Longsword_" + _m) in AZ_ITEMS, "no vanilla Weapon_Longsword_" + _m
# 0.2.9: the Monk weapon twin (SkyyArmory 0.1.7): these prefixes + a metal (wraps: a cloth -> its metal column) take Weapon_Sword_<metal>'s K
TWIN_PRE = ["Weapon_Fist_Gauntlets_", "Weapon_Fist_Wraps_", "Weapon_Bo_"]""")
rep('''  String mm = monkMetal(id);          // 0.2.9: a Monk weapon scales like the same-metal sword
  if (mm == null) return id;''', '''  if (id.length() > 19 && id.startsWith("Weapon_GreatShield_")) {          // 0.3.13: a great shield scales like the same-metal longsword
    String ls = "Weapon_Longsword_" + id.substring(19);
    return @PKG@.Gear.item(ls) == null ? id : ls;
  }
  String mm = monkMetal(id);          // 0.2.9: a Monk weapon scales like the same-metal sword
  if (mm == null) return id;''')

# ================================================================================================================ critic A3: /lifelong re-pick retires, never plain
rep('''public static boolean demote(@IC@ c, int i, @IS@ x, @BD@ d, java.util.UUID u) {
  @BD@ nd = d.clone();
  nd.remove("ll");''', """public static boolean demote(@IC@ c, int i, @IS@ x, @BD@ d, java.util.UUID u) {
  if (@PKG@.GearCfg.LL_ON && @PKG@.GearCfg.NORM_ON) {          // 0.3.13 critic A3: normal tools are off - the re-picked-away tool is RETIRED, never plain
    @BD@ rd = d.clone();
    rd.put("lrt", new org.bson.BsonInt32(1));
    rd.remove("lrp");
    rd.remove("lrpT");
    if (!put(c, i, x, rd, u)) return false;
    N[5] = N[5] + 1L;
    @PKG@.GearLog.line("LL-RETIRE " + u + " " + x.getItemId() + " " + @PKG@.GearLL.uid(d) + " (the tool /lifelong re-picked away from - retired, normal tools are off)");
    return true;
  }
  @BD@ nd = d.clone();
  nd.remove("ll");""")

# ================================================================================================================ /gear normoff (admin): the class + its constructor early, the body late
after('''subc = dict((s[0], mk(s[1], APC)) for s in SUBS)
''', '''gnc = mk("GearNormCmd", APC)          # 0.3.13: /gear normoff [status | undo <player>] (admin; body in the 0.3.13 block)
''')
before('''C(subc["loot"], r"""
public GearLootCmd() {''', r'''C(gnc, r"""
public GearNormCmd() {
  super("normoff", "Normal tools off: the counters, or give a player's removed normal tools back: /gear normoff [undo <player>]");
  requirePermission("skyygear.admin");
  setPermissionGroups(new String[0]);
  setAllowsExtraArguments(true);
}""")
''')
rep('''  addSubCommand(new @PKG@.GearUtCmd());
}""")''', '''  addSubCommand(new @PKG@.GearUtCmd());
  addSubCommand(new @PKG@.GearNormCmd());          // 0.3.13
}""")''')
rep('''bq.remove("gear:fn:poleRule");''', '''bq.remove("gear:fn:poleRule"); bq.remove("gear:fn:normalTool");''')

# ================================================================================================================ the 0.3.13 block (late: everything it calls exists)
G313 = r'''# ####################################################################################################################################
# 0.3.13 (tools/gear_0_3_13_patch.py): GearNorm (normal tools off: the recipes, the drop lists, the chest strip, the one-time removal per
# profile, the undo, the status), GearNormDrop (the drop-list filter), GearNormL (the asset reload listener), GearNormFn (gear:fn:normalTool),
# the /gear normoff body. Hooks: GearLife.sweep0 (after), GearChestOpen.process (before), GearSickle.tick, GearCfg.apply, GearBoxL, the plugin.
# ####################################################################################################################################
for _c, _m in ((CRR, "getAssetStore"), (CRR, "getAssetMap"), (CRR, "getPrimaryOutput"), (CRR, "getOutputs"), (CRR, "getId"),
               (MULTI_ENGINE["ASTO"], "removeAssets"), (G311["IDL"], "getAssetMap"), (G311["IDL"], "getContainer"), (G311["IDC"], "getAllDrops"),
               (G311["IDC"], "getWeight"), (G311["IDR"], "getItemId"), (IC, "removeItemStackFromSlot"), (IC, "getItemStack"), (IC, "getCapacity"),
               (IS, "getDurability"), (IS, "getMaxDurability"), (IS, "withDurability"), (IS, "getMetadata")):
    B.probe(pool, _c, _m)
_rmv = [str(_m.getSignature()) for _m in pool.get(MULTI_ENGINE["ASTO"]).getDeclaredMethods() if str(_m.getName()) == "removeAssets"]
assert any(_x.startswith("(Ljava/util/Collection;)") for _x in _rmv), "AssetStore.removeAssets(Collection) changed: %s" % _rmv
# the engine facts (VERIFIED bytecode 2026-10-16, Hytale 0.7.2; re-checked here so a game update that moves them stops the build):
# CraftingPlugin.onRecipeRemove takes a removed recipe out of every BenchRecipeRegistry; every drop roll reads ItemDropList.getContainer()
_orr = _calls("com.hypixel.hytale.builtin.crafting.CraftingPlugin", "onRecipeRemove")
assert "BenchRecipeRegistry.removeRecipe" in _orr and "RemovedAssetsEvent.getRemovedAssets" in _orr, "CraftingPlugin.onRecipeRemove no longer drops a removed recipe from the benches"
_grd = _calls("com.hypixel.hytale.server.core.modules.item.ItemModule", "getRandomItemDrops")
assert "ItemDropList.getContainer" in _grd and "ItemDropContainer.populateDrops" in _grd, "ItemModule.getRandomItemDrops no longer rolls the list's container"
gnorm = mk("GearNorm")
gndrop = mk("GearNormDrop", G311["IDC"])
gnorml = mk("GearNormL")
gnfn = mk("GearNormFn")
G313_CLASSES = [gnorm, gndrop, gnorml, gnfn, gnc]
# ---- GearNorm: fields first
for _f in ("public static final long[] N = new long[16];",          # 14 stragglers removed after the pass
           # 0 recipes removed, 1 drop lists filtered now, 2 (unused), 3 chest stacks stripped, 4 profiles cleaned, 5 inventory stacks removed,
           # 6 bag items removed, 7 Requip entries removed, 8 removals the engine refused, 9 stacks given back (undo), 10 ensure runs,
           # 11 recipe runs, 12 Requip passes that waited for room, 13 profiles undone
           "public static final java.util.concurrent.ConcurrentHashMap GONE = new java.util.concurrent.ConcurrentHashMap();",     # recipe id -> output id
           "public static final java.util.concurrent.ConcurrentHashMap WR = new java.util.concurrent.ConcurrentHashMap();",       # drop list id -> GearNormDrop
           "public static final java.util.concurrent.ConcurrentHashMap SEEN = new java.util.concurrent.ConcurrentHashMap();",     # drop list id -> { container, Boolean }
           "public static final java.util.concurrent.ConcurrentHashMap LASTRUN = new java.util.concurrent.ConcurrentHashMap();",  # UUID -> Long (next look not before)
           "public static final java.util.concurrent.ConcurrentHashMap UNDO = new java.util.concurrent.ConcurrentHashMap();",     # UUID -> admin name
           "public static volatile String SEEN_SRC = null;", "public static volatile String RCP = \"not run yet\";", "public static volatile int RCP_N = -1;",
           "public static volatile boolean WRAP_BAD = false;", "public static volatile boolean STARTED = false;", "public static volatile long ENS = 0L;",
           "public static final java.util.concurrent.atomic.AtomicBoolean BUSY = new java.util.concurrent.atomic.AtomicBoolean(false);",
           "public static volatile int CRASH_AT = 0;"):          # CRASH_AT: HARNESS SEAM ONLY (1 = a crash right after the first removal)
    F(gnorm, _f)
M(gnorm, "public static boolean on() { return @PKG@.GearCfg.LL_ON && @PKG@.GearCfg.NORM_ON; }")
# a NORMAL tool stack: a normal kind without a lifelong stamp (unreadable / newer gear data counts as stamped: never removed)
M(gnorm, r"""
public static boolean normal(@IS@ s) {
  if (s == null || s.isEmpty() || !@PKG@.GearLL.normKind(s.getItemId())) return false;
  @BD@ md = s.getMetadata();
  int st = @PKG@.GearData.state(md);
  if (st == 3 || st == 4) return false;
  @BD@ d = null;
  try { d = @PKG@.GearData.gearDoc(md); } catch (Throwable t) { return false; }
  return !@PKG@.GearLL.isLL(d);
}""")
# ---- GearNormDrop: a drop list's container without the normal-tool drops (GearStick's shape)
F(gndrop, "public @IDC@ inner;")
F(gndrop, "public String lid;")
F(gndrop, "public static final long[] N = new long[2];")          # 0 rolls, 1 normal-tool drops stripped
C(gndrop, r"""
public GearNormDrop(@IDC@ in, String lid) {
  super(in == null ? 0.0 : in.getWeight());
  this.inner = in;
  this.lid = lid;
}""")
M(gndrop, r"""
protected void populateDrops(java.util.List out, java.util.function.DoubleSupplier ds, java.util.Set seen) {
  if (this.inner == null || out == null) return;
  int n0 = out.size();
  this.inner.populateDrops(out, ds, this.lid);
  N[0] = N[0] + 1L;
  if (!@PKG@.GearCfg.LL_ON || !@PKG@.GearCfg.NORM_ON) return;
  for (int i = out.size() - 1; i >= n0; i--) {
    Object o = out.get(i);
    if (o instanceof @IDR@ && @PKG@.GearLL.normKind(((@IDR@) o).getItemId())) { out.remove(i); N[1] = N[1] + 1L; }
  }
}""")
M(gndrop, r"""
public java.util.List getAllDrops(java.util.List out) {
  if (this.inner == null) return out;
  if (!@PKG@.GearCfg.LL_ON || !@PKG@.GearCfg.NORM_ON) return this.inner.getAllDrops(out);
  java.util.List all = this.inner.getAllDrops(new java.util.ArrayList());
  for (int i = 0; all != null && i < all.size(); i++) {
    Object o = all.get(i);
    if (o instanceof @IDR@ && @PKG@.GearLL.normKind(((@IDR@) o).getItemId())) continue;
    out.add(o);
  }
  return out;
}""")
M(gndrop, 'public String toString() { return "GearNormDrop{" + this.lid + ", no normal tools from " + this.inner + "}"; }')
# ---- the drop lists: every list whose container can yield a normal tool gets a GearNormDrop (inside its GearStick when it has one)
M(gnorm, r"""
public static java.lang.reflect.Field field() {
  try {
    java.lang.reflect.Field f = @IDL@.class.getDeclaredField("container");
    f.setAccessible(true);
    return f;
  } catch (Throwable t) {
    if (!WRAP_BAD) { WRAP_BAD = true; @PKG@.Gear.warn("normal tools: ItemDropList.container cannot be set (" + t + ") - chests and drops still roll normal tools (opened chests are stripped)"); }
    return null;
  }
}""")
M(gnorm, r"""
public static boolean needs(String id, @IDC@ raw) {
  if (raw == null) return false;
  Object[] sn = (Object[]) SEEN.get(id);
  if (sn != null && sn[0] == raw) return ((Boolean) sn[1]).booleanValue();
  boolean y = false;
  try {
    java.util.List l = raw.getAllDrops(new java.util.ArrayList());
    for (int i = 0; l != null && i < l.size() && !y; i++) {
      Object o = l.get(i);
      if (o instanceof @IDR@ && @PKG@.GearLL.normKind(((@IDR@) o).getItemId())) y = true;
    }
  } catch (Throwable t) { y = false; }
  SEEN.put(id, new Object[] { raw, Boolean.valueOf(y) });
  return y;
}""")
M(gnorm, r"""
public static synchronized int drops(boolean on) {
  java.lang.reflect.Field f = field();
  if (f == null) return -1;
  String ex = @PKG@.GearCfg.NORM_EXTRA == null ? "" : @PKG@.GearCfg.NORM_EXTRA;
  if (!ex.equals(SEEN_SRC)) { SEEN.clear(); SEEN_SRC = ex; }
  java.util.Map m = null;
  try { m = @IDL@.getAssetMap().getAssetMap(); } catch (Throwable t) { m = null; }
  if (m == null) return -1;
  java.util.ArrayList es = new java.util.ArrayList(m.entrySet());
  java.util.HashSet ids = new java.util.HashSet();
  int n = 0;
  for (int i = 0; i < es.size(); i++) {
    java.util.Map.Entry e = (java.util.Map.Entry) es.get(i);
    Object o = e.getValue();
    if (!(o instanceof @IDL@)) continue;
    @IDL@ l = (@IDL@) o;
    String id = String.valueOf(e.getKey());
    ids.add(id);
    try {
      @IDC@ c = l.getContainer();
      if (c == null) continue;
      if (c instanceof @PKG@.GearNormDrop) {
        @PKG@.GearNormDrop g = (@PKG@.GearNormDrop) c;
        if (!on || !needs(id, g.inner)) { f.set(l, g.inner); WR.remove(id); continue; }
        WR.put(id, g);
        n++;
        continue;
      }
      if (c instanceof @PKG@.GearStick) {
        @PKG@.GearStick gs = (@PKG@.GearStick) c;
        @IDC@ in = gs.inner;
        if (in instanceof @PKG@.GearNormDrop) {
          @PKG@.GearNormDrop g2 = (@PKG@.GearNormDrop) in;
          if (!on || !needs(id, g2.inner)) { gs.inner = g2.inner; WR.remove(id); continue; }
          WR.put(id, g2);
          n++;
          continue;
        }
        if (on && in != null && needs(id, in)) {
          @PKG@.GearNormDrop g3 = new @PKG@.GearNormDrop(in, id);
          gs.inner = g3;
          WR.put(id, g3);
          n++;
        }
        continue;
      }
      if (on && needs(id, c)) {
        @PKG@.GearNormDrop g4 = new @PKG@.GearNormDrop(c, id);
        f.set(l, g4);
        WR.put(id, g4);
        n++;
      }
    } catch (Throwable t2) { @PKG@.Gear.warnOnce("normdrop:" + id, "normal tools: the drop list " + id + " could not be filtered: " + t2); }
  }
  WR.keySet().retainAll(ids);
  N[1] = (long) n;
  return n;
}""")
# ---- the recipes: every recipe whose output is a normal tool (not a fishing rod: SkyyFishing's bench rods are the pole's tier-up path) leaves
# the CraftingRecipe store (the benches + every reader); idempotent; a restart with normal.off off brings them back
M(gnorm, "public static boolean recipeKind(String id) { return @PKG@.GearLL.normKind(id) && !@PKG@.GearData.pole(id); }")
M(gnorm, r"""
public static String normOut(@CRR@ rc) {
  if (rc == null) return null;
  @MQ@ po = rc.getPrimaryOutput();
  String id = po == null ? null : po.getItemId();
  if (id != null && recipeKind(id)) return id;
  @MQ@[] outs = rc.getOutputs();
  for (int i = 0; outs != null && i < outs.length; i++) {
    if (outs[i] != null && outs[i].getItemId() != null && recipeKind(outs[i].getItemId())) return outs[i].getItemId();
  }
  return null;
}""")
M(gnorm, r"""
public static synchronized String recipes() {
  N[11] = N[11] + 1L;
  if (!on()) { RCP = "normal tools allowed (normal.off is off)" + (GONE.isEmpty() ? "" : " - the " + GONE.size() + " recipe(s) removed earlier come back after a restart"); return RCP; }
  java.util.Map m = null;
  try { m = @CRR@.getAssetMap().getAssetMap(); } catch (Throwable t) { m = null; }
  if (m == null) { RCP = "the recipe store could not be read"; return RCP; }
  java.util.ArrayList drop = new java.util.ArrayList();
  java.util.ArrayList outs = new java.util.ArrayList();
  java.util.ArrayList vs = new java.util.ArrayList(m.values());
  for (int i = 0; i < vs.size(); i++) {
    Object o = vs.get(i);
    if (!(o instanceof @CRR@)) continue;
    @CRR@ rc = (@CRR@) o;
    String out = normOut(rc);
    if (out == null || rc.getId() == null) continue;
    drop.add(rc.getId());
    outs.add(out);
  }
  if (!drop.isEmpty()) {
    try { @CRR@.getAssetStore().removeAssets(drop); }
    catch (Throwable t2) { @PKG@.Gear.warn("normal tools: the " + drop.size() + " normal tool recipe(s) could not be removed (" + t2 + ") - crafting them is still refused"); RCP = "recipe removal FAILED (" + t2 + ")"; return RCP; }
    for (int i = 0; i < drop.size(); i++) GONE.put(drop.get(i), outs.get(i));
    N[0] = N[0] + (long) drop.size();
    if (STARTED) @PKG@.GearLog.line("NORMOFF-RECIPES removed " + drop.size() + ": " + drop);
  }
  try { RCP_N = @CRR@.getAssetMap().getAssetMap().size(); } catch (Throwable t3) { RCP_N = -1; }
  RCP = GONE.size() + " normal tool recipe(s) removed from every bench (" + drop.size() + " this run)";
  return RCP;
}""")
M(gnorm, r"""
public static void ensure0(boolean rc) {
  if (!STARTED || !BUSY.compareAndSet(false, true)) return;
  try {
    N[10] = N[10] + 1L;
    drops(on());
    if (rc && on()) recipes();
    ENS = System.currentTimeMillis();
  } catch (Throwable t) { @PKG@.Gear.warnOnce("normensure", "normal tools: the setup failed: " + t); }
  finally { BUSY.set(false); }
}""")
M(gnorm, "public static void ensure() { ensure0(true); }")
M(gnorm, "public static void refresh(String key) { ensure0(true); }")          # Server Setup after= hook (normal.off, normal.extraIds)
M(gnorm, r"""
public static void tick() {
  long now = System.currentTimeMillis();
  if (now - ENS > 30000L || now < ENS) {
    boolean rc = false;          // critic B3: a reload missed while BUSY - the recipe store changed size since the last recipe run
    try { rc = on() && @CRR@.getAssetMap().getAssetMap().size() != RCP_N; } catch (Throwable t) { rc = false; }
    ensure0(rc);          // an asset hot-reload makes new list objects: the next look filters those
  }
}""")
M(gnorm, "public static void onLoaded(Object e) { if (STARTED) ensure0(true); }")
M(gnorm, r"""
public static void unwrapAll() {
  try { drops(false); } catch (Throwable t) { }
  WR.clear();
}""")
# ---- the undo record (Skyy_SkyyGear/normoff/<profile>.log): REMOVED <rid> <where> <id> <qty> <durability or -> <metadata JSON base64 or ->,
# GIVEN <rid>; appended + fsync, one line at a time
M(gnorm, r"""
public static java.nio.file.Path recFile(String pk) {
  java.nio.file.Path d = @PKG@.GearCfg.DIR;
  if (d == null || pk == null) return null;
  return d.resolve("normoff").resolve(@PKG@.GearLL.safeKey(pk) + ".log");
}""")
M(gnorm, r"""
public static boolean rec(java.nio.file.Path f, String line) {
  if (f == null || line == null) return false;
  try {
    java.nio.file.Files.createDirectories(f.getParent(), new java.nio.file.attribute.FileAttribute[0]);
    java.io.FileOutputStream out = new java.io.FileOutputStream(f.toFile(), true);
    try {
      out.write((line.replace('\n', ' ') + "\n").getBytes("UTF-8"));
      out.flush();
      out.getFD().sync();
    } finally { out.close(); }
    return true;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("normrec:" + f, "normal tools: the undo record " + f + " could not be written: " + t); return false; }
}""")
M(gnorm, r"""
public static String line(String rid, String where, @IS@ s) {
  String meta = "-";
  try {
    @BD@ md = s.getMetadata();
    if (md != null && !md.isEmpty()) meta = java.util.Base64.getEncoder().encodeToString(md.toJson().getBytes("UTF-8"));
  } catch (Throwable t) { meta = "-"; }
  String dur = "-";
  try { if (s.getMaxDurability() > 0.0) dur = String.valueOf(s.getDurability()); } catch (Throwable t2) { dur = "-"; }
  return "REMOVED\t" + rid + "\t" + where + "\t" + s.getItemId() + "\t" + s.getQuantity() + "\t" + dur + "\t" + meta;
}""")
# ---- the chest strip (any block container, on open / break, world thread): normal stacks out, each logged
M(gnorm, r"""
public static int strip(@IC@ c, String where, java.nio.file.Path rf) {
  if (c == null) return 0;
  int n = 0;
  for (int i = 0; i < c.getCapacity(); i++) {
    @IS@ s = c.getItemStack((short) i);
    if (!normal(s)) continue;
    Object tx = null;
    Throwable ex = null;
    try { tx = c.removeItemStackFromSlot((short) i); } catch (Throwable t) { ex = t; }
    @IS@ now = c.getItemStack((short) i);
    if (ex == null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) && (now == null || now.isEmpty())) {
      n++;
      N[3] = N[3] + 1L;
      @PKG@.GearLog.line("NORMOFF-CHEST " + where + " slot " + i + " " + s.getItemId() + " x" + s.getQuantity() + " " + @PKG@.GearMerge.json(s) + " removed");
      if (rf != null) rec(rf, line("c" + System.nanoTime(), "chest:" + where.replace('\t', ' ') + ":" + i, s));          // critic A2: the opener's undo record
    } else {
      N[8] = N[8] + 1L;
      @PKG@.Gear.warnOnce("normchest:" + where, "normal tools: a " + s.getItemId() + " in the container at " + where + " could not be removed (" + (ex != null ? String.valueOf(ex) : "the container refused it") + ")");
    }
  }
  return n;
}""")
M(gnorm, r"""
public static int chestAt(@WLD@ w, int x, int y, int z, java.util.UUID who, String name, String how) {
  if (!on() || w == null) return 0;
  try {
    java.nio.file.Path rf = null;
    if (who != null) {          // critic A2: an undone profile's own opens are not stripped; else the opener's record gets every stack
      String pk = @PKG@.Gear.pkey(who);
      java.util.Properties P = @PKG@.GearLL.reg(pk);
      if (!@PKG@.GearLL.bad(P) && "undone".equals(P.getProperty("normOff"))) return 0;
      rf = recFile(pk);
    }
    @REF@ be = @BMOD@.getBlockEntity(w, x, y, z);
    @ICB@ icb = @PKG@.GearChestOpen.icbOf(be);
    int px = x;
    int py = y;
    int pz = z;
    if (icb == null) {
      int[] o = @PKG@.GearChestOpen.origin(w, x, y, z);
      if (o == null) return 0;
      px = o[0];
      py = o[1];
      pz = o[2];
      icb = @PKG@.GearChestOpen.icbOf(@BMOD@.getBlockEntity(w, px, py, pz));
      if (icb == null) return 0;
    }
    return strip(icb.getItemContainer(), w.getName() + " " + px + " " + py + " " + pz + " (" + how + " by " + name + ")", rf);
  } catch (Throwable t) { @PKG@.Gear.warnOnce("normchestat", "normal tools: a container could not be checked: " + t); return 0; }
}""")
# the verified History copy of the profile's lifelong registry file (normoff/history/<pk>.properties.<stamp>.bak); true = copied (or no file yet)
M(gnorm, r"""
public static boolean backup(String pk, String stamp) {
  try {
    java.nio.file.Path f = @PKG@.GearLL.file(pk);
    if (f == null) return false;
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return true;
    byte[] b = java.nio.file.Files.readAllBytes(f);
    java.nio.file.Path h = @PKG@.GearCfg.DIR.resolve("normoff").resolve("history");
    java.nio.file.Files.createDirectories(h, new java.nio.file.attribute.FileAttribute[0]);
    java.nio.file.Path c = h.resolve(@PKG@.GearLL.safeKey(pk) + ".properties." + stamp + ".bak");
    java.nio.file.Files.write(c, b, new java.nio.file.OpenOption[0]);
    byte[] r = java.nio.file.Files.readAllBytes(c);
    if (!java.util.Arrays.equals(b, r)) { @PKG@.Gear.warn("normal tools: the History copy of lifelong/" + pk + ".properties did not verify - nothing removed for that profile"); return false; }
    return true;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("normbak:" + pk, "normal tools: the History copy of lifelong/" + pk + ".properties failed (" + t + ") - nothing removed for that profile yet"); return false; }
}""")
M(gnorm, r"""
public static void rqGone(java.util.UUID u, String eid) {
  java.util.function.Function g = @PKG@.Gear.fn("wardrobe:fn:gone");
  if (g == null || eid == null) return;
  try { g.apply(new Object[] { u, eid, "normal tool removed (SkyyGear 0.3.13)" }); } catch (Throwable t) { @PKG@.Gear.warnOnce("normrqgone", "wardrobe:fn:gone failed: " + t); }
}""")
# one stack out of an inventory slot, recorded (true = gone and recorded / logged)
M(gnorm, r"""
public static boolean takeOut(@PR@ pr, @IC@ c, int i, @IS@ s, String where, String rid, java.nio.file.Path rf) {
  Object tx = null;
  Throwable ex = null;
  try { tx = c.removeItemStackFromSlot((short) i); } catch (Throwable t) { ex = t; }
  @IS@ now = c.getItemStack((short) i);
  boolean gone = ex == null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded()) && (now == null || now.isEmpty());
  if (!gone) {
    N[8] = N[8] + 1L;
    @PKG@.GearLog.line("NORMOFF-REFUSED " + pr.getUuid() + " " + where + " " + s.getItemId() + " (" + (ex != null ? String.valueOf(ex) : "the inventory refused it") + ")");
    return false;
  }
  rec(rf, line(rid, where, s));
  @PKG@.GearLog.line("NORMOFF-REMOVE " + pr.getUsername() + " " + pr.getUuid() + " " + where + " " + s.getItemId() + " x" + s.getQuantity() + " " + @PKG@.GearMerge.json(s) + " (rid " + rid + ")");
  return true;
}""")
# the kits first (a plain tool may still become this profile's lifelong one), no lifelong journal open
M(gnorm, r"""
public static boolean ready(java.util.Properties P) {
  if (!"1".equals(P.getProperty("migrated"))) return false;
  if (@PKG@.GearCfg.LL_POLEKIT && !"1".equals(P.getProperty("poleKit"))) return false;
  if (@PKG@.GearCfg.CAN_ON && @PKG@.GearCfg.CAN_KIT && !"1".equals(P.getProperty("canKit"))) return false;
  if (P.getProperty("harv.pend") != null) return false;
  for (int k = 0; k < @PKG@.GearLL.KIND.length; k++) if (P.getProperty(@PKG@.GearLL.KIND[k] + ".pend") != null) return false;
  return true;
}""")
# is there any normal tool in the inventory sections or the bags?
M(gnorm, r"""
public static boolean anyNormal(@INV@ inv, java.util.UUID u) {
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) if (normal(c.getItemStack((short) i))) return true;
  }
  java.util.HashMap bags = @PKG@.GearSmith.bagAll(u);
  if (bags == null) return false;
  java.util.Iterator it = bags.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    if (e.getKey() instanceof String && @PKG@.GearLL.normKind((String) e.getKey()) && e.getValue() instanceof Number && ((Number) e.getValue()).longValue() > 0L) return true;
  }
  return false;
}""")
# THE INVENTORY + BAGS PASS (once per profile; world thread): History copy -> journal on disk -> every normal stack out (recorded) -> the bags ->
# marker normOff=1. A crash in between: the journal makes the next look run it again (what is gone is not found twice, nothing is given)
M(gnorm, r"""
public static void invPass(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  java.util.UUID u = pr.getUuid();
  String stamp = P.getProperty("normOff.pend");
  if (stamp == null && !anyNormal(inv, u)) {          // nothing to remove (every new profile): the marker alone, no History copy / journal
    P.setProperty("normOff", "1");
    P.setProperty("normOffAt", String.valueOf(System.currentTimeMillis()));
    P.setProperty("normOffN", String.valueOf(@PKG@.GearLL.getl(P, "normOffN", 0L)));
    if (!@PKG@.GearLL.save(pk, P)) { P.remove("normOff"); LASTRUN.put(u, Long.valueOf(System.currentTimeMillis() + 30000L)); return; }
    @PKG@.GearLog.line("NORMOFF-DONE " + pr.getUsername() + " " + u + " " + pk + ": no normal tool in the inventory or the bags");
    return;
  }
  if (stamp == null) {
    stamp = String.valueOf(System.currentTimeMillis());
    if (!backup(pk, stamp)) { LASTRUN.put(u, Long.valueOf(System.currentTimeMillis() + 30000L)); return; }
    P.setProperty("normOff.pend", stamp);
    if (!@PKG@.GearLL.save(pk, P)) { P.remove("normOff.pend"); LASTRUN.put(u, Long.valueOf(System.currentTimeMillis() + 30000L)); return; }
    @PKG@.GearLog.line("NORMOFF-BEGIN " + pr.getUsername() + " " + u + " " + pk + " (stamp " + stamp + ")");
  } else @PKG@.GearLog.line("NORMOFF-RESUME " + pr.getUsername() + " " + u + " " + pk + " (stamp " + stamp + ")");
  java.nio.file.Path rf = recFile(pk);
  int n = 0;
  int bad = 0;
  long seq = System.nanoTime();
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    int sec = @PKG@.GearStamp.SCAN[a];
    @IC@ c = @PKG@.GearStamp.section(inv, sec);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ s = c.getItemStack((short) i);
      if (!normal(s)) continue;
      String eid = @PKG@.GearData.eidOf(s);
      seq++;
      if (!takeOut(pr, c, i, s, "inv:" + sec + ":" + i, stamp + "-" + seq, rf)) { bad++; continue; }
      n++;
      N[5] = N[5] + 1L;
      if (eid != null) rqGone(u, eid);
      if (CRASH_AT == 1) throw new IllegalStateException("harness: a crash right after a normal tool left");
    }
  }
  // the Magic Bags (no metadata there): every normal tool id they hold, taken and committed, one record line per item
  java.util.HashMap bags = @PKG@.GearSmith.bagAll(u);
  if (bags != null) {
    java.util.function.Function tk = @PKG@.Gear.fn("sacks:fn:take");
    java.util.function.Function cm = @PKG@.Gear.fn("sacks:fn:commit");
    java.util.ArrayList ks = new java.util.ArrayList(bags.keySet());
    for (int i = 0; i < ks.size() && tk != null; i++) {
      Object k = ks.get(i);
      if (!(k instanceof String) || !@PKG@.GearLL.normKind((String) k)) continue;
      Object v = bags.get(k);
      long q = v instanceof Number ? ((Number) v).longValue() : 0L;
      if (q <= 0L) continue;
      long got = 0L;
      try { Object r = tk.apply(new Object[] { u, k, Long.valueOf(q) }); if (r instanceof Number) got = ((Number) r).longValue(); } catch (Throwable t) { got = 0L; }
      if (got <= 0L) { bad++; continue; }
      try { if (cm != null) cm.apply(new Object[] { u, k, Long.valueOf(got) }); } catch (Throwable t2) { @PKG@.Gear.warnOnce("normbagcommit", "sacks:fn:commit failed: " + t2); }
      for (long j = 0L; j < got && j < 1000L; j++) { seq++; rec(rf, "REMOVED\t" + stamp + "-" + seq + "\tbag\t" + k + "\t1\t-\t-"); }
      @PKG@.GearLog.line("NORMOFF-REMOVE " + pr.getUsername() + " " + u + " bags " + k + " x" + got);
      N[6] = N[6] + got;
      n++;
    }
  }
  if (bad > 0) {
    LASTRUN.put(u, Long.valueOf(System.currentTimeMillis() + 30000L));
    @PKG@.Gear.warnOnce("normbad:" + pk, "normal tools: " + bad + " normal tool(s) of " + pr.getUsername() + " could not be removed yet - tried again in 30 s (gear.log NORMOFF-REFUSED)");
    if (n > 0) @PKG@.GearLife.tellOnce(pr, "normoff", "Normal tools are switched off on SkyWynn - your lifelong tools do the job (/pickaxe /hatchet /hoe /sickle /pole /can). " + n + " normal tool(s) were removed.", 10000L);
    return;
  }
  long had = @PKG@.GearLL.getl(P, "normOffN", 0L);
  P.setProperty("normOff", "1");
  P.setProperty("normOffAt", String.valueOf(System.currentTimeMillis()));
  P.setProperty("normOffN", String.valueOf(had + (long) n));
  P.remove("normOff.pend");
  if (!@PKG@.GearLL.save(pk, P)) {
    P.remove("normOff");
    P.setProperty("normOff.pend", stamp);
    LASTRUN.put(u, Long.valueOf(System.currentTimeMillis() + 30000L));
    return;
  }
  N[4] = N[4] + 1L;
  @PKG@.GearLog.line("NORMOFF-DONE " + pr.getUsername() + " " + u + " " + pk + ": " + n + " normal tool stack(s) removed (inventory + bags; record normoff/" + @PKG@.GearLL.safeKey(pk) + ".log) - UNDO: /gear normoff undo " + pr.getUsername());
  if (n > 0) @PKG@.GearLife.tellOnce(pr, "normoff", "Normal tools are switched off on SkyWynn - your lifelong tools do the job (/pickaxe /hatchet /hoe /sickle /pole /can). " + n + " normal tool(s) were removed from your inventory and bags.", 10000L);
}""")
# THE REQUIP PASS (once per profile, after the inventory pass): a Requip-stamped normal tool that is OUT (in the inventory) goes; every IN one
# is fetched (wardrobe:fn:fetch -> the inventory), taken out and reported used up (wardrobe:fn:gone). No room = asked again later.
M(gnorm, r"""
public static int[] findEid(@INV@ inv, String eid) {
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ s = c.getItemStack((short) i);
      if (s != null && !s.isEmpty() && eid.equals(@PKG@.GearData.eidOf(s))) return new int[] { @PKG@.GearStamp.SCAN[a], i };
    }
  }
  return null;
}""")
M(gnorm, r"""
public static void rqPass(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  java.util.UUID u = pr.getUuid();
  java.util.function.Function fl = @PKG@.Gear.fn("wardrobe:fn:list");
  if (fl == null) return;          // no SkyyWardrobe now: asked again at a later look (cheap)
  Object r = null;
  try { r = fl.apply(new Object[] { u, "all" }); } catch (Throwable t) { r = null; }
  if (!(r instanceof Object[])) return;
  Object[] rows = (Object[]) r;
  java.util.ArrayList want = new java.util.ArrayList();
  for (int i = 0; i < rows.length; i++) {
    if (!(rows[i] instanceof Object[])) continue;
    Object[] e = (Object[]) rows[i];
    if (e.length < 3 || !(e[0] instanceof String) || !(e[1] instanceof String) || !@PKG@.GearLL.normKind((String) e[1])) continue;
    @BD@ md = e[2] instanceof @BD@ ? (@BD@) e[2] : null;
    int st = @PKG@.GearData.state(md);
    if (st == 3 || st == 4) continue;
    @BD@ d = null;
    try { d = @PKG@.GearData.gearDoc(md); } catch (Throwable t2) { continue; }
    if (@PKG@.GearLL.isLL(d)) continue;
    want.add(e[0]);
  }
  java.nio.file.Path rf = recFile(pk);
  long seq = System.nanoTime();
  String stamp = String.valueOf(System.currentTimeMillis());
  if (!want.isEmpty()) {
    java.util.function.Function ff = @PKG@.Gear.fn("wardrobe:fn:fetch");
    if (ff == null) return;
    for (int i = 0; i < want.size(); i++) {
      String eid = (String) want.get(i);
      Object fr = null;
      try { fr = ff.apply(new Object[] { u, eid }); } catch (Throwable t3) { fr = null; }
      if (!"ok".equals(fr)) {
        N[12] = N[12] + 1L;
        LASTRUN.put(u, Long.valueOf(System.currentTimeMillis() + 30000L));
        @PKG@.GearLife.tellOnce(pr, "normrq", "Normal tools are switched off - free one inventory slot so the normal tools in your Requip can be cleared.", 60000L);
        return;
      }
      int[] at = findEid(inv, eid);
      if (at == null) { LASTRUN.put(u, Long.valueOf(System.currentTimeMillis() + 30000L)); return; }
      @IC@ c = @PKG@.GearStamp.section(inv, at[0]);
      @IS@ s = c.getItemStack((short) at[1]);
      seq++;
      if (!takeOut(pr, c, at[1], s, "requip:" + eid, stamp + "-" + seq, rf)) { LASTRUN.put(u, Long.valueOf(System.currentTimeMillis() + 30000L)); return; }
      rqGone(u, eid);
      N[7] = N[7] + 1L;
    }
  }
  P.setProperty("normOffRq", "1");
  P.setProperty("normOffRqAt", stamp);
  if (!@PKG@.GearLL.save(pk, P)) { P.remove("normOffRq"); P.remove("normOffRqAt"); return; }
  @PKG@.GearLog.line("NORMOFF-REQUIP " + pr.getUsername() + " " + u + " " + pk + ": " + want.size() + " normal tool(s) out of Requip - UNDO: /gear normoff undo " + pr.getUsername());
  if (want.size() > 0) @PKG@.GearLife.tellOnce(pr, "normrqdone", want.size() + " normal tool(s) were cleared out of your Requip (normal tools are switched off).", 10000L);
}""")
# critic A1: the REMOVED rows of a profile's record not given back yet (0 = nothing to undo; -1 = unreadable)
M(gnorm, r"""
public static int pending(String pk) {
  java.nio.file.Path rf = recFile(pk);
  try {
    if (rf == null || !java.nio.file.Files.exists(rf, new java.nio.file.LinkOption[0])) return 0;
    java.util.List ls = java.nio.file.Files.readAllLines(rf, java.nio.charset.StandardCharsets.UTF_8);
    java.util.HashSet given = new java.util.HashSet();
    java.util.HashSet rem = new java.util.HashSet();
    for (int i = 0; i < ls.size(); i++) {
      String[] p = ((String) ls.get(i)).split("\t", -1);
      if (p.length >= 2 && "GIVEN".equals(p[0])) given.add(p[1]);
      else if (p.length >= 5 && "REMOVED".equals(p[0])) rem.add(p[1]);
    }
    rem.removeAll(given);
    return rem.size();
  } catch (Throwable t) { return -1; }
}""")
# THE UNDO (an admin queued it: /gear normoff undo <player>): every recorded stack not given yet comes back (storage first; the Requip stamp
# dropped), each one marked GIVEN; all back -> the markers read 'undone' (never removed again for this profile)
M(gnorm, r"""
public static @IS@ rebuild(String[] p) {
  try {
    String id = p[3];
    if (@PKG@.Gear.item(id) == null) return null;
    int q = Integer.parseInt(p[4]);
    if (q < 1) q = 1;
    @BD@ md = null;
    if (p.length > 6 && !"-".equals(p[6])) md = @BD@.parse(new String(java.util.Base64.getDecoder().decode(p[6]), "UTF-8"));
    if (md != null) md.remove(@PKG@.GearData.stampKey());
    @IS@ s = md == null || md.isEmpty() ? new @IS@(id, q) : new @IS@(id, q, md);
    if (p.length > 5 && !"-".equals(p[5])) s = s.withDurability(Double.parseDouble(p[5]));
    return s;
  } catch (Throwable t) { return null; }
}""")
M(gnorm, r"""
public static void undo(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  java.util.UUID u = pr.getUuid();
  java.nio.file.Path rf = recFile(pk);
  java.util.ArrayList rows = new java.util.ArrayList();
  java.util.HashSet given = new java.util.HashSet();
  try {
    if (rf != null && java.nio.file.Files.exists(rf, new java.nio.file.LinkOption[0])) {
      java.util.List ls = java.nio.file.Files.readAllLines(rf, java.nio.charset.StandardCharsets.UTF_8);
      for (int i = 0; i < ls.size(); i++) {
        String[] p = ((String) ls.get(i)).split("\t", -1);
        if (p.length >= 2 && "GIVEN".equals(p[0])) given.add(p[1]);
        else if (p.length >= 5 && "REMOVED".equals(p[0])) rows.add(p);
      }
    }
  } catch (Throwable t) { @PKG@.Gear.warn("normal tools: the undo record of " + pk + " could not be read (" + t + ") - nothing given back"); UNDO.remove(u); return; }
  int n = 0;
  int left = 0;
  for (int i = 0; i < rows.size(); i++) {
    String[] p = (String[]) rows.get(i);
    if (given.contains(p[1])) continue;
    @IS@ s = rebuild(p);
    if (s == null) { rec(rf, "GIVEN\t" + p[1] + "\tunknown item " + p[3]); @PKG@.GearLog.line("NORMOFF-UNDO-SKIP " + u + " " + p[3] + " (no such item now)"); continue; }
    if (!@PKG@.GearAdmin.give(inv, s)) { left++; continue; }
    rec(rf, "GIVEN\t" + p[1]);
    n++;
    N[9] = N[9] + 1L;
    @PKG@.GearLog.line("NORMOFF-UNDO-GIVE " + pr.getUsername() + " " + u + " " + p[3] + " x" + p[4] + " (rid " + p[1] + ")");
  }
  if (left > 0) {
    @PKG@.GearLife.tellOnce(pr, "normundo", "An admin is giving your removed normal tools back - free " + left + " inventory slot(s) for the rest.", 30000L);
    return;
  }
  P.setProperty("normOff", "undone");
  P.setProperty("normOffRq", "undone");
  P.remove("normOff.pend");
  P.setProperty("normOffUndoAt", String.valueOf(System.currentTimeMillis()));
  if (!@PKG@.GearLL.save(pk, P)) return;
  Object who = UNDO.remove(u);
  N[13] = N[13] + 1L;
  @PKG@.GearLog.line("NORMOFF-UNDO " + pr.getUsername() + " " + u + " " + pk + ": " + n + " stack(s) given back (asked by " + who + "); never removed again for this profile");
  @PKG@.GearLife.tellOnce(pr, "normundone", n + " removed normal tool(s) were given back to you.", 5000L);
}""")
# critic B2: STRAGGLERS after the one-time pass (a normal tool back from the Vault, an AH listing, a pre-update item): removed the same way
M(gnorm, r"""
public static boolean creative(@PR@ pr) {
  try {
    @REF@ r = pr.getReference();
    if (r == null || !r.isValid()) return false;
    @ST@ st = r.getStore();
    @PLA@ p = (@PLA@) st.getComponent(r, @PLA@.getComponentType());
    return p != null && p.getGameMode() == @GM@.Creative;
  } catch (Throwable t) { return false; }
}""")
M(gnorm, r"""
public static boolean anyInv(@INV@ inv) {
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[a]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) if (normal(c.getItemStack((short) i))) return true;
  }
  return false;
}""")
M(gnorm, r"""
public static int straggle(@PR@ pr, @INV@ inv, String pk, java.util.Properties P) {
  java.util.UUID u = pr.getUuid();
  java.nio.file.Path rf = recFile(pk);
  int n = 0;
  for (int a = 0; a < @PKG@.GearStamp.SCAN.length; a++) {
    int sec = @PKG@.GearStamp.SCAN[a];
    @IC@ c = @PKG@.GearStamp.section(inv, sec);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ s = c.getItemStack((short) i);
      if (!normal(s)) continue;
      String eid = @PKG@.GearData.eidOf(s);
      if (!takeOut(pr, c, i, s, "straggler:inv:" + sec + ":" + i, "s" + System.nanoTime(), rf)) continue;
      n++;
      N[14] = N[14] + 1L;
      if (eid != null) rqGone(u, eid);
    }
  }
  if (n <= 0) return 0;
  P.setProperty("normOffN", String.valueOf(@PKG@.GearLL.getl(P, "normOffN", 0L) + (long) n));
  @PKG@.GearLL.save(pk, P);
  @PKG@.GearLog.line("NORMOFF-STRAGGLER " + pr.getUsername() + " " + u + " " + pk + ": " + n + " normal tool(s) that turned up later removed - UNDO: /gear normoff undo " + pr.getUsername());
  @PKG@.GearLife.tellOnce(pr, "normstraggle", "Normal tools are switched off on SkyWynn - " + n + " normal tool(s) that turned up were removed. Your lifelong tools: /pickaxe /hatchet /hoe /sickle /pole /can", 30000L);
  return n;
}""")
# THE HOOK (GearLife.sweep0, after; every lifelong look ~ every 400 ms while the inventory changes + every join): cheap when done
M(gnorm, r"""
public static void sweepHook(@PR@ pr, @INV@ inv) {
  if (pr == null || inv == null || !@PKG@.GearCfg.LL_ON) return;
  java.util.UUID u = pr.getUuid();
  if (u == null || @PKG@.Gear.busy(u)) return;
  boolean und = UNDO.containsKey(u);
  if (!und && (!@PKG@.GearCfg.NORM_ON || !@PKG@.GearCfg.NORM_OWNED)) return;
  String pk = @PKG@.Gear.pkey(u);
  if (@PKG@.GearLL.failing(pk)) return;
  java.util.Properties P = @PKG@.GearLL.reg(pk);
  if (@PKG@.GearLL.bad(P)) return;
  long now = System.currentTimeMillis();
  Object l = LASTRUN.get(u);
  if (l instanceof Long && now < ((Long) l).longValue()) return;
  if (und) { LASTRUN.put(u, Long.valueOf(now + 2000L)); undo(pr, inv, pk, P); return; }
  boolean d1 = P.getProperty("normOff") != null && P.getProperty("normOff.pend") == null;
  boolean d2 = P.getProperty("normOffRq") != null;
  if (d1 && d2) {
    if ("undone".equals(P.getProperty("normOff")) || creative(pr) || !anyInv(inv)) return;          // critic B2: a cheap look; Creative + undone skip
    LASTRUN.put(u, Long.valueOf(now + 2000L));
    straggle(pr, inv, pk, P);
    return;
  }
  if (!ready(P)) return;
  LASTRUN.put(u, Long.valueOf(now + 2000L));
  if (!d1) invPass(pr, inv, pk, P);
  if (P.getProperty("normOff") != null && P.getProperty("normOff.pend") == null && P.getProperty("normOffRq") == null) rqPass(pr, inv, pk, P);
}""")
M(gnorm, "public static void forget(java.util.UUID u) { if (u != null) LASTRUN.remove(u); }")
M(gnorm, r"""
public static String statusText() {
  return "normal tools " + (on() ? "OFF everywhere" : "allowed (normal.off off" + (@PKG@.GearCfg.LL_ON ? "" : ", or part.lifelong off") + ")") + ": " + RCP + "; " + WR.size() + " drop lists filtered (" + @PKG@.GearNormDrop.N[1] + " normal tool drops stripped of " + @PKG@.GearNormDrop.N[0] + " rolls); chests stripped " + N[3] + " stack(s); stragglers " + N[14] + "; owned ones " + (@PKG@.GearCfg.NORM_OWNED ? "removed once per profile" : "kept (normal.removeOwned off)") + " - " + N[4] + " profile(s) cleaned this start, " + N[5] + " inventory stack(s), " + N[6] + " bag item(s), " + N[7] + " Requip item(s), " + N[8] + " refused, " + N[9] + " given back by undo" + (@PKG@.GearCfg.NORM_EXTRA != null && @PKG@.GearCfg.NORM_EXTRA.length() > 0 ? "; extra ids " + @PKG@.GearCfg.NORM_EXTRA : "") + "; Enchanted Sticks per tier-up " + @PKG@.GearCfg.LL_STICKS + " (" + (@PKG@.Gear.item(@PKG@.GearUp.STICK_ID) != null ? "item loaded" : "item NOT loaded - no stick asked") + ", " + @PKG@.GearUp.SN[0] + " costs with sticks)";
}""")
# ---- GearNormL: LoadedAssetsEvent(ItemDropList / CraftingRecipe) -> ensure (the Item reload comes through GearBoxL)
gnorml.addInterface(pool.get("java.util.function.Consumer"))
C(gnorml, "public GearNormL() { }")
M(gnorml, r"""
public void accept(Object e) {
  try { @PKG@.GearNorm.onLoaded(e); } catch (Throwable t) { @PKG@.Gear.warnOnce("normlistener", "normal tools: the reload listener failed: " + t); }
}""")
# ---- GearNormFn: gear:fn:normalTool (String item id -> Boolean: a normal tool kind while normal tools are off) for the other mods
gnfn.addInterface(pool.get("java.util.function.Function"))
C(gnfn, "public GearNormFn() { }")
M(gnfn, r"""
public Object apply(Object o) {
  try {
    if (o instanceof String) return Boolean.valueOf(@PKG@.GearNorm.on() && @PKG@.GearLL.normKind((String) o));
    if (o instanceof @IS@) return Boolean.valueOf(@PKG@.GearNorm.on() && @PKG@.GearNorm.normal((@IS@) o));
  } catch (Throwable t) { }
  return Boolean.FALSE;
}""")
# ---- /gear normoff (admin)
M(gnc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    String rest = @PKG@.GearAdmin.rest(ctx, "normoff").trim();
    String[] a = rest.length() == 0 ? new String[0] : rest.split("\\s+");
    if (a.length == 0 || a[0].equalsIgnoreCase("status")) { @PKG@.GearAdmin.msg(pr, @PKG@.GearNorm.statusText()); return; }
    if (a[0].equalsIgnoreCase("undo") && a.length >= 2) {
      @PR@ target = null;
      java.util.Iterator it = @UNI@.get().getPlayers().iterator();
      while (it.hasNext()) {
        Object o = it.next();
        if (o instanceof @PR@ && ((@PR@) o).getUsername() != null && ((@PR@) o).getUsername().equalsIgnoreCase(a[1])) { target = (@PR@) o; break; }
      }
      if (target == null) { @PKG@.GearAdmin.msg(pr, "no online player called " + a[1] + " (the undo runs on an online player)"); return; }
      String tpk = @PKG@.Gear.pkey(target.getUuid());
      int pend = @PKG@.GearNorm.pending(tpk);
      if (pend == 0) { @PKG@.GearAdmin.msg(pr, "no record for " + target.getUsername() + "'s active profile (" + tpk + ") - nothing to give back; its markers are left as they are"); return; }          // critic A1
      @PKG@.GearNorm.UNDO.put(target.getUuid(), pr.getUsername());
      @PKG@.GearNorm.LASTRUN.remove(target.getUuid());
      @PKG@.GearLog.line("ADMIN " + pr.getUsername() + " normoff undo " + target.getUsername() + " " + target.getUuid());
      @PKG@.GearAdmin.msg(pr, "queued: " + target.getUsername() + "'s removed normal tools come back at their next inventory change (their active profile; free slots needed). Their profile is never cleaned again.");
      return;
    }
    @PKG@.GearAdmin.msg(pr, "usage: /gear normoff  (the counters)  |  /gear normoff undo <player>");
  } catch (Throwable t) {
    @PKG@.Gear.warn("/gear normoff failed: " + t);
    pr.sendMessage(@MSG@.raw("[Gear] That did not work - the server log has the details."));
  }
}""")
# ---- the hooks
glf.getDeclaredMethod("sweep0").insertAfter(J("{ try { @PKG@.GearNorm.sweepHook($1, $2); } catch (Throwable tnh) { @PKG@.Gear.warnOnce(\"normsweep\", \"normal tools: the look failed: \" + tnh); } }"))
_prc = [m for m in gcho.getDeclaredMethods() if str(m.getName()) == "process"]
assert len(_prc) == 1 and str(_prc[0].getSignature()).startswith("(Lcom/hypixel/hytale/server/core/universe/world/World;IIILjava/util/UUID;Ljava/lang/String;Ljava/lang/String;)"), [str(m.getSignature()) for m in _prc]
_prc[0].insertBefore(J("{ try { @PKG@.GearNorm.chestAt($1, $2, $3, $4, $5, $6, $7); } catch (Throwable tnc) { } }"))
gsck.getDeclaredMethod("tick").insertBefore(J("{ try { @PKG@.GearNorm.tick(); } catch (Throwable tnt) { } }"))
_ldM[0].insertAfter(J("{ try { @PKG@.GearNorm.ensure(); } catch (Throwable tne) { } }"))          # every config FILE apply
_bxa = [m for m in gboxl.getDeclaredMethods() if str(m.getName()) == "accept"]
assert len(_bxa) == 1
_bxa[0].insertAfter(J("{ try { @PKG@.GearNorm.onLoaded($1); } catch (Throwable tnb) { } }"))          # an Item reload regenerates its recipe
pl.getDeclaredMethod("setup").insertAfter(J("""{
  try { getEventRegistry().register(@EPRI@.LAST, @LAE@.class, @IDL@.class, new @PKG@.GearNormL()); getEventRegistry().register(@EPRI@.LAST, @LAE@.class, @CRR@.class, new @PKG@.GearNormL()); }
  catch (Throwable tnl) { @PKG@.Gear.warn("normal tools: the asset reload listener could not be registered (" + tnl + ") - a reloaded drop list / recipe is filtered at the next 30 s look"); }
}"""))
pl.getDeclaredMethod("start").insertAfter(J("""{
  try {
    @PKG@.GearNorm.STARTED = true;
    @PKG@.GearNorm.ENS = 0L;
    @PKG@.GearNorm.ensure();
    try { @PKG@.Gear.bridge().put("gear:fn:normalTool", new @PKG@.GearNormFn()); } catch (Throwable tbr) { }
    @PKG@.Gear.info("[SkyyGear] 0.3.13: " + @PKG@.GearNorm.statusText());
  } catch (Throwable tns) { @PKG@.Gear.warn("normal tools setup failed: " + tns); }
}"""))
pl.getDeclaredMethod("shutdown").insertBefore(J("{ try { @PKG@.GearNorm.unwrapAll(); } catch (Throwable tnd) { } }"))
for _m in _byeM:
    _m.insertBefore(J("{ try { if ($1 instanceof @PDE@) @PKG@.GearNorm.forget(((@PDE@) $1).getPlayerRef().getUuid()); } catch (Throwable tnf) { } }".replace("@PDE@", PDE)))
print("0.3.13 normal tools off: GearNorm / GearNormDrop / GearNormL / GearNormFn / GearNormCmd; hooks in sweep0, GearChestOpen.process, GearSickle.tick, GearCfg.apply, GearBoxL, setup / start / shutdown")
'''
after('''print("0.3.12 watering can: GearCan / GearCanWater (SkyyGearCan) / GearCanSup, /can, /harvester, the Harvester merge on the Tools tab")
''', G313)

# ================================================================================================================ the manifest, the class list
rep('''Gear's Health regen runs through SkyySkills' skill:fn:hpregen; Server Setup -> Gear. Replaces SkyyRolls.''',
    '''Gear's Health regen runs through SkyySkills' skill:fn:hpregen; NORMAL TOOLS ARE OFF: normal (not lifelong) pickaxes, hatchets, hoes, sickles, fishing rods and watering cans are never crafted, listed at a bench, looted from chests, Lost Loot or drops, and the ones players own are removed once per profile (logged; /gear normoff undo); lifelong tier-ups into Thorium and up also cost Enchanted Sticks; Server Setup -> Gear. Replaces SkyyRolls.''')
rep('''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES + G311_CLASSES + G312_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''',
    '''+ LIFE_CLASSES + G34_CLASSES + G36_CLASSES + G311_CLASSES + G312_CLASSES + G313_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')

# ================================================================================================================ checks on the result
assert s.index("public static boolean normKind(String id) {") < s.index("public static boolean noCraft(String id)")
assert s.index("public static Object[] cost0(String from, String to) {") < s.index("public static Object[] cost(String from, String to) {") < s.index("public static String costText(Object[] c) {")
assert s.index('C(gnc, r"""') < s.index('C(gcm, r"""') and s.index('gnc = mk("GearNormCmd", APC)') < s.index('C(gnc, r"""')
assert s.index("_byeM = [m for m in pool.get(PKG") < s.index("gnorm = mk(\"GearNorm\")") < s.index("0.3.10 ALWAYS ANSWER (tools") < s.index("ALL = [gu, gdf, gcf")
assert s.index("_ldM = [m for m in gcf.getDeclaredMethods()") < s.index("gnorm = mk(\"GearNorm\")")
assert s.count("addSubCommand(new @PKG@.GearNormCmd())") == 1
_u = s
for _new, _old, _cnt in reversed(CHANGES):
    assert _u.count(_new) == _cnt, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old)
assert _u == OLD, "the generated script differs from 0.3.12 outside the recorded changes"
compile(s, DST, "exec")
open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(DST, ROOT), "(%d lines; 0.3.12 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
