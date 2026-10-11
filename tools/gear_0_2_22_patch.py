"""Derive SkyyGear/build_skyygear_0.2.22.py from the LIVE 0.2.21 (build_skyygear_0.2.21.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_21_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_22_patch.py      then      python SkyyGear/build_skyygear_0.2.22.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.22.py

0.2.22 = UPGRADE INSIDE THE REFORGE PAGE + THE LEVEL IN ITEM NAMES (Skyy 2026-10-10; docs/answered/gear.md LOCKED 2026-10-10 lines "an
update page where it keeps the rarity sounds pretty cool, should we do that with the soul cages too?", "we can probbly combind the upgrade
into the reforge we already have." and "Can we add the items level to the name of the item? Like Copper pickaxe [lvl 12]").
WHY NOT THE BENCH (engine fact, 0.2.21 header, VERIFIED bytecode): a bench craft only takes inputs whose metadata equals the recipe input's
(none), so a rolled item (every crafted / stamped gear item carries a SkyyGear document) is NEVER a bench ingredient. SkyyArmory 0.1.20's
Soul Cage tier-up recipes (each cage = the cage before + bars + essence) therefore never accept a rolled cage from a player's inventory.
  1. ONE PAGE, TABS: the Reforge page (/reforge) gets a vanilla tab row on top of its right column (the EntitySpawnPage tab look: the
     active tab = the Primary button, the others Secondary, 5 px apart) - "Reforge" | "Upgrade" | "Multitool". Upgrade shows only while
     part.upgrade is on; Multitool only while part.multitool is on and a Multitools item is loaded; with one tab left the old "Anvil" title
     comes back. Reforge <-> Upgrade switch IN the page (the item on the anvil stays when it fits the other mode, the list changes to
     "Your gear" / "Upgradable items"); the Multitool tab opens the 0.2.21 /multitool page (its two-pick layout does not fit one anvil),
     which shows the same tab row (its Reforge / Upgrade tabs open the Reforge page in that mode). /upgrade = a shortcut that opens the
     Reforge page on the Upgrade tab with the held item on the anvil; /reforge and /multitool unchanged.
     Upgrade mode: left = every item you carry (hotbar, inventory, backpack, armor, utility, tools) that has a next tier; right = the item,
     "Next tier: <name>", the materials with have / need (white = enough, gold = short), the result (same rarity, same lines, the new
     level - or "plain: it rolls a rarity like a crafted <next>"), its lines, and the "Upgrade" button. After an upgrade the new item stays
     on the anvil ("Made: ..." + its lines; the button reads "Upgraded" and a further click is refused - fix round); click it in the list
     to see (and pay) its next step. /upgrade while holding an item that is not on any ladder (Mythic / Set / Untiered, a mystery bag, a
     sword) opens the empty anvil with the reason in the gold info line (fix round).
  2. THE LADDER TABLE (data, Server Setup -> Gear -> Upgrades, upgrade.ladders): rows joined by ","; a row = item ids joined by ">" (each
     step = one upgrade). A step's cost is read from the LIVE CraftingRecipe store by default (the recipe whose primary output is the next
     item, quantity 1, and whose inputs hold the item, quantity 1: its OTHER inputs are the cost - SkyyArmory's bars + essence for the
     cages), or written on the row right after the item it upgrades INTO: "A>B(Ingredient_Bar_Iron*6+Some_Drop*1)" (for later boss-drop
     upgrades no recipe makes). Each item has at most one next tier; bad ids, an item in two rows, a loop, a cost on the first item and
     ids / materials no item has are refused in Server Setup; a hand-edited bad part is skipped with one WARN. Internally every step is a
     row {kind, from, to, cost-or-recipe}; kind "up" is the only one built - a later "convert" kind (A~B: change an item's TYPE keeping its
     rolls, e.g. Dragon Cloth -> Heavy) is reserved and refused today ("not built yet"). Later ladders (gathering armor sets, tools,
     multitools, metal weapons, Mythic boss-drop upgrades) are new rows - nothing else changes.
     Default = the Soul Cage ladder Weapon_Wand_SoulOrb > ..._SoulCage_Copper > Iron > Thorium > Cobalt > Adamantite > Mithril > Onyxium,
     costs from SkyyArmory's recipes. A recipe with a resource-type / tag input, or none at all, = "No recipe makes <next> from <item>"
     (refused). Cached per store size. No bench, no knowledge, no coins. Build check: SkyyArmory/SkyyArmory-0.1.20.jar's 7 cage recipes
     are read and must match the ladder (printed: Copper 4 bars + 15 Life ... Onyxium 6 bars + 10 Light); a built-in cost table is NOT
     needed (the live read works - the harness reads the real recipes of the 0.1.20 jar).
  3. THE UPGRADED DOCUMENT (GearUp.docI): a copy of the item's document - SAME rarity, SAME lines, reforge name / count, speed tier, every
     other field - with: level = the next tier's craft level (GearRoll.craftLevel: your skill moved into its band, like a bench craft);
     each line re-levelled = value x levelFactor(new) / levelFactor(old) (rounded; never below its old value; at most the fresh-roll cap of
     its rarity at the new level unless it was already above it - then it keeps its old value); kind / gate = the next tier's; bought
     level ups (lvU / lvl0) are NOT carried (made at your level - the page warns when it had some, or when the new level is lower); a
     mystery-bag origin ("box") is dropped (re-identify of the upgraded item would otherwise pick a lower item from the old bag range).
     A PLAIN item (no SkyyGear document, or a legacy Normal stamp with no lines - GearMerge.plain) = the normal craft roll of the next tier
     (GearRoll.craftDoc: rarity from the craft odds + the Smithing step-up, lines rolled for that rarity), exactly what a bench craft of
     the next tier gives - the page says so before the click. No Smithing XP for any upgrade (like /multitool).
  4. REFUSED (gold line, nothing moves): upgrading off (part.upgrade), no next tier, a stack of more than one, Mythic / Set / Untiered (incl.
     gear.mythicItems and Untiered-table ids, and a next tier that is one), unidentified, unreadable / newer data, next tier not loaded, no
     recipe / a material not loaded, materials short ("You need 3 more Iron Bar (you have 3 of 6)"), craft.belowBand block, profile
     loading / changed.
  5. DUPE / LOSS SAFETY (GearUp.upgrade, world thread, one click, the GearMerge 0.2.21 pattern): the item is re-checked by fingerprint; the
     materials are planned storage first (Inventory, Backpack, then Hotbar; only stacks without a SkyyGear / bag document); UPGRADE-BEGIN
     in gear.log with the item's full document, the new document and every planned material slot, FLUSHED to disk; (a) the materials
     leave slot by slot (each checked); a failure = every touched slot put back (UPGRADE-FAILED ... RESTORED, or UPGRADE-RESTORE-FAILED for
     an admin); (b) the item's OWN slot gets the upgraded item (setItemStackForSlot, checked) - never a second copy; (b) failing = the old
     item and every material put back. A crash between (a) and (b) can only LOSE the materials (listed in UPGRADE-BEGIN), never copy
     anything. After: the counts are checked (item -1, next tier +1, each material -need; else UPGRADE-COUNT + a WARN). A second click
     with the old fingerprint is refused. A full inventory does not matter (nothing new needs a free slot). Fix round: GearLog.flush now
     takes the queue INSIDE WLOCK, so "flushed" really means on disk even when the scheduler had just taken the line (0.2.21's /multitool
     merge gets the same fix). CARRIED DATA: the upgraded stack is a NEW stack of the next tier (a fresh stack, like a bench craft)
     with the SkyyGear document only - any other mod's metadata on the old stack is NOT carried (the same as /multitool, identify and
     /gear give). SkyyArmory 0.1.20's cages carry none; a later ladder whose items carry another mod's data must copy those keys first.
  6. LEVEL IN NAMES (view.levelInName, Server Setup -> Gear -> General, default ON): every name SkyyGear writes on an item ends with
     " [Lv N]" - weapons, armor, tools, multitools (rarity colour + reforge prefix kept; an unidentified ITEM has one fixed level, so it
     shows that level); a mystery bag (the unidentified loot) shows its range " [Lv A-B]" (" [Lv A]" when A = B). The tooltip signature
     (GearView.sig) carries the switch, so every stack re-renders ONCE at its next scan (and again when the switch changes); bags re-render
     at the stamp scan too (GearUnid.reView, hooked in front of GearStamp.stampStack - only the display changes, never the bag's data).
     Pages keep the bare name (they show the level beside it).
SAVED DATA: an upgraded item carries an ordinary gear document (its own fields + the new lvl / kind). New config rows (absent = default, no
one-time update): part.upgrade, upgrade.ladders, view.levelInName (a fresh file gets a 0.2.22 block). Nothing else is stored.
ROLLBACK (for tools/deploy_set.py, reported, not edited here): 0.2.22 -> 0.2.21 is safe: upgraded items are plain gear documents 0.2.21
reads; names lose the [Lv N] at the next scan (the sig differs again); the three new config lines are ignored; /upgrade and the tabs go
away. Bags keep the " [Lv A-B]" name until they are opened (0.2.21 never re-renders a bag).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.21.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.22.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.21"' in s and s.startswith('"""SkyyGear 0.2.21 - build script'), "build_skyygear_0.2.21.py is not the live 0.2.21"
assert "GearUp" not in s and "UpPage" not in s and "levelInName" not in s, "0.2.21 already has the 0.2.22 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.21 - build script (javassist via jpype). GENERATED by tools/gear_0_2_21_patch.py from the LIVE 0.2.20 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.21.py -> SkyyGear/SkyyGear-0.2.21.jar (never --deploy).

''', '''"""SkyyGear 0.2.22 - build script (javassist via jpype). GENERATED by tools/gear_0_2_22_patch.py from the LIVE 0.2.21 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.22.py -> SkyyGear/SkyyGear-0.2.22.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.22 = "):].strip() + '''

0.2.21 (the base, everything below is still true unless 0.2.22 above says otherwise):
''')
rep('VERSION = "0.2.21"', 'VERSION = "0.2.22"')

# ================================================================================================================ 1. config rows
# the default ladder: SkyyArmory 0.1.20's Soul Orb -> Soul Cages (SOUL_IDS of build_skyyarmory_0.1.20.py)
rep('''CFG_CATS = [("general", "General"), ("rarity", "Rarity"), ("levels", "Levels"), ("base", "Level stats"), ("stats", "Stats"),
            ("costs", "Costs"), ("drops", "Drops + craft"), ("loot", "Loot"), ("tools", "Tools"), ("combat", "Combat"), ("migrate", "Migration"),
            ("garmor", "Gathering armor")]       # 0.2.15''',
    '''CFG_CATS = [("general", "General"), ("rarity", "Rarity"), ("levels", "Levels"), ("base", "Level stats"), ("stats", "Stats"),
            ("costs", "Costs"), ("drops", "Drops + craft"), ("loot", "Loot"), ("tools", "Tools"), ("combat", "Combat"), ("migrate", "Migration"),
            ("garmor", "Gathering armor"),       # 0.2.15
            ("upgrade", "Upgrades")]             # 0.2.22
# 0.2.22: the Soul Cage ladder (SkyyArmory 0.1.20 SOUL_IDS); the costs are read from the live recipes (GearUp.cost)
UP_SOUL = ["Weapon_Wand_SoulOrb"] + ["Weapon_Wand_SoulCage_%s" % _m for _m in ("Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium")]
UP_LADDER_DEF = ">".join(UP_SOUL)
assert len(UP_LADDER_DEF) < 500 and all(32 <= ord(_c) < 127 for _c in UP_LADDER_DEF)''')
rep('''    ("multi.fortunePct", "Multitool Fortune", "tools", "int", str(MULTI_FORT_DEF), "0", "100", "", "%", "live,danger",
     "Mining / Foraging Fortune = this % of a same-tier pickaxe / hatchet." + PH, "field:GearCfg.MULTI_FORT"),''',
    '''    ("multi.fortunePct", "Multitool Fortune", "tools", "int", str(MULTI_FORT_DEF), "0", "100", "", "%", "live,danger",
     "Mining / Foraging Fortune = this % of a same-tier pickaxe / hatchet." + PH, "field:GearCfg.MULTI_FORT"),
    # 0.2.22 (Skyy 2026-10-10 "an update page where it keeps the rarity"): /upgrade + its ladders; the item level in names
    ("part.upgrade", "Upgrade tab (/upgrade)", "upgrade", "bool", "true", "", "", "", "", "live,part,danger",
     "Reforge Upgrade tab: an item becomes its next tier, same rarity and lines, made at your level.", "field:GearCfg.UP_ON"),
    ("upgrade.ladders", "Upgrade ladders", "upgrade", "text", UP_LADDER_DEF, "0", "2000", "", "", "live,danger",
     "Ids joined by > (one ladder), ladders by commas. Cost = the recipe minus the item, or A>B(Id*6+Id).",
     "field:GearCfg.UP_LADDERS;check=GearUp.checkLadders"),
    ("view.levelInName", "Level in item names", "general", "bool", "true", "", "", "", "", "live",
     "Item names end with their level, e.g. Copper Pickaxe [Lv 12] (bags: [Lv 5-9]).", "field:GearCfg.NAME_LV"),''')
rep('''           "part.multitool", "multi.speedPct", "multi.fortunePct"}''',
    '''           "part.multitool", "multi.speedPct", "multi.fortunePct",
           # 0.2.22: the upgrade switch + its ladders (item tiers = economy) - confirm in Server Setup
           "part.upgrade", "upgrade.ladders"}''')
rep('''              ("MULTI_ON", "boolean", "true"), ("MULTI_SPD", "int", str(MULTI_SPD_DEF)), ("MULTI_FORT", "int", str(MULTI_FORT_DEF))]''',
    '''              ("MULTI_ON", "boolean", "true"), ("MULTI_SPD", "int", str(MULTI_SPD_DEF)), ("MULTI_FORT", "int", str(MULTI_FORT_DEF)),
              # 0.2.22 the upgrade page + the level in names
              ("UP_ON", "boolean", "true"), ("UP_LADDERS", "String", jstr(UP_LADDER_DEF)), ("NAME_LV", "boolean", "true")]''')
rep('''  MULTI_FORT = (int) plong(p, "multi.fortunePct", 70L, 0L, 100L);''',
    '''  MULTI_FORT = (int) plong(p, "multi.fortunePct", 70L, 0L, 100L);
  // 0.2.22 the upgrade page (ladders checked where they are used - GearUp.tab skips a bad part with one WARN) + the level in names
  UP_ON = pbool(p, "part.upgrade", true);
  UP_LADDERS = ptext(p, "upgrade.ladders", "@UPLADDEF@").trim();
  NAME_LV = pbool(p, "view.levelInName", true);''')
rep('''.replace("@MYTHDEF@", MYTHIC_ITEMS_DEF))''', '''.replace("@MYTHDEF@", MYTHIC_ITEMS_DEF).replace("@UPLADDEF@", UP_LADDER_DEF))''')
# the fresh file: a 0.2.22 block right after the 0.2.12 tool rows (the 0.2.14+ blocks are asserted from the END of the file, unchanged)
rep('''TL_ROWK = ["part.tools", "tool.power.pickaxe",''', '''# 0.2.22: the upgrade + name rows of a fresh file (an existing file gets each the first time it is changed in Server Setup)
UG_HEAD = "# ---- upgrade (Reforge page Upgrade tab, /upgrade) + the level in item names (SkyyGear 0.2.22) ----"
UG_ROWK = ["part.upgrade", "upgrade.ladders", "view.levelInName"]
assert all(32 <= ord(_c) < 127 for _c in UG_HEAD) and "=" not in UG_HEAD
TL_ROWK = ["part.tools", "tool.power.pickaxe",''')
rep('''    L += ["", TL_HEAD]         # 0.2.12: the tool rows at the very end of a fresh file (no one-time update adds them)
    for k in TL_ROWK:
        scal(k)
''', '''    L += ["", TL_HEAD]         # 0.2.12: the tool rows at the very end of a fresh file (no one-time update adds them)
    for k in TL_ROWK:
        scal(k)
    L += ["", UG_HEAD]         # 0.2.22: the upgrade + name rows (no one-time update adds them; absent = the default)
    for k in UG_ROWK:
        scal(k)
''')
rep('''assert _dp.get("part.multitool") == "true" and _dp.get("multi.speedPct") == str(MULTI_SPD_DEF) and _dp.get("multi.fortunePct") == str(MULTI_FORT_DEF)''',
    '''assert _dp.get("part.multitool") == "true" and _dp.get("multi.speedPct") == str(MULTI_SPD_DEF) and _dp.get("multi.fortunePct") == str(MULTI_FORT_DEF)
# 0.2.22: the block once, right after the 0.2.12 tool rows; the rows read back
assert DEFAULT_TEXT.count(UG_HEAD) == 1 and _dp.get("upgrade.ladders") == UP_LADDER_DEF and _dp.get("part.upgrade") == "true" and _dp.get("view.levelInName") == "true"
assert _DL[_DL.index(UG_HEAD) - 2] == "tool.fortune.cap=%s" % dict((r[0], r[4]) for r in CFG_ROWS)["tool.fortune.cap"], "the 0.2.22 block follows the 0.2.12 rows"''')

# ================================================================================================================ 2. the level in names
rep('''# Name: one raw coloured line; if the en-US name is missing or has {params} the item's translation Message is inserted (SkyyRolls)
M(gvw, r"""
public static @MSG@ nameMsg(String id, @BD@ d, String col) {
  String base = null;
  @ITM@ it = @PKG@.Gear.item(id);
  try { if (it != null) base = @PKG@.Gear.tr(it.getTranslationKey()); } catch (Throwable t) { base = null; }
  if (base != null && base.indexOf(123) < 0) return @MSG@.raw(nameText(id, d).replace(@PKG@.Gear.itemName(id), base)).color(col);''',
    '''# 0.2.22 (Skyy 2026-10-10 "Like Copper pickaxe [lvl 12]"): the level at the end of the item's name ("" = view.levelInName off)
M(gvw, r"""
public static String lvTag(String id, @BD@ d) {
  if (!@PKG@.GearCfg.NAME_LV || id == null || d == null) return "";
  return " [Lv " + @PKG@.GearLevel.level(id, d) + "]";
}""")
# Name: one raw coloured line; if the en-US name is missing or has {params} the item's translation Message is inserted (SkyyRolls)
M(gvw, r"""
public static @MSG@ nameMsg(String id, @BD@ d, String col) {
  String base = null;
  String tag = lvTag(id, d);
  @ITM@ it = @PKG@.Gear.item(id);
  try { if (it != null) base = @PKG@.Gear.tr(it.getTranslationKey()); } catch (Throwable t) { base = null; }
  if (base != null && base.indexOf(123) < 0) return @MSG@.raw(nameText(id, d).replace(@PKG@.Gear.itemName(id), base) + tag).color(col);''')
rep('''  try { m.insert(it.getTranslationMessage().color(col)); } catch (Throwable t) { m.insert(@MSG@.raw(@PKG@.Gear.pretty(id)).color(col)); }
  return m;
}""")''', '''  try { m.insert(it.getTranslationMessage().color(col)); } catch (Throwable t) { m.insert(@MSG@.raw(@PKG@.Gear.pretty(id)).color(col)); }
  if (tag.length() > 0) m.insert(@MSG@.raw(tag).color(col));
  return m;
}""")''')
# the sig carries the switch: the new name format re-renders every stack once (and again when the switch changes)
rep('''+ Integer.toHexString(sb.toString().hashCode()) + ":" + @PKG@.GearLevel.level(id, d) + ":" + @PKG@.GearCfg.cfgEpoch() + ":" + (hasDesc(id) ? 1 : 0);''',
    '''+ Integer.toHexString(sb.toString().hashCode()) + ":" + @PKG@.GearLevel.level(id, d) + ":" + @PKG@.GearCfg.cfgEpoch() + ":" + (hasDesc(id) ? 1 : 0)
    + (@PKG@.GearCfg.NAME_LV ? ":n1" : ":n0");          // 0.2.22: the level in the name''')
# mystery bags: the range in the name
rep('''M(gunid, r"""
public static @IS@ view(@IS@ s, @BD@ d) {
  int r = rar(d);
  return s.withMetadata(@IDM@.KEYED_CODEC, new @IDM@(@MSG@.raw(title(d)).color(@PKG@.GearDefs.R_HEX[r]), descMsg(d)));
}""")''', '''# 0.2.22: the level range at the end of a bag's name (" [Lv 5-9]", " [Lv 5]" when lo = hi; "" = view.levelInName off)
M(gunid, r"""
public static String lvTag(@BD@ d) {
  if (!@PKG@.GearCfg.NAME_LV || d == null) return "";
  int lo = lo(d);
  int hi = hi(d);
  return lo == hi ? " [Lv " + lo + "]" : " [Lv " + lo + "-" + hi + "]";
}""")
M(gunid, r"""
public static @IS@ view(@IS@ s, @BD@ d) {
  int r = rar(d);
  return s.withMetadata(@IDM@.KEYED_CODEC, new @IDM@(@MSG@.raw(title(d) + lvTag(d)).color(@PKG@.GearDefs.R_HEX[r]), descMsg(d)));
}""")''')

# ================================================================================================================ 3. the tab row (GearUi)
# the vanilla tab row (EntitySpawnPage: Secondary buttons 5 px apart, the active one Primary) at the top of the right column of the Reforge
# page and of the /multitool page; placed in front of ReforgePage (its anvil calls it). One tab left -> the old column title instead.
rep(r'''# ================================================================= ReforgePage (spec 5.4 + 5.8): the vanilla item-repair page look''',
    r'''# 0.2.22: the Multitool tab shows while multitools are on and a multitool item is loaded (= GearMerge.loaded, which is defined later)
M(gui, r"""
public static boolean multiTab() {
  if (!@PKG@.GearCfg.MULTI_ON) return false;
  for (int i = 0; i < @PKG@.GearMulti.TW.length; i++) if (@PKG@.Gear.item(@PKG@.GearMulti.mid(i)) != null) return true;
  return false;
}""")
# 0.2.22 the tab row: 0 Reforge, 1 Upgrade (part.upgrade on), 2 Multitool (multiTab); EventData a = "mode:<n>"; returns how many tabs show
M(gui, r"""
public static int tabs(@UCB@ b, @UEB@ ev, String parent, int sel, int w, String title) {
  boolean up = @PKG@.GearCfg.UP_ON;
  boolean mt = multiTab();
  int n = 1 + (up ? 1 : 0) + (mt ? 1 : 0);
  if (n < 2) {
    b.appendInline(parent, "Label #SkyyGAnvilT { Anchor: (Height: 35); Padding: (Horizontal: 8); Text: \"\"; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }");
    b.set("#SkyyGAnvilT.Text", title);
    return 1;
  }
  b.appendInline(parent, "Group #SkyyGTabs { Anchor: (Height: 48); LayoutMode: Left; Padding: (Bottom: 4); }");
  int tw = (w - 5 * (n - 1)) / n;
  int k = 0;
  for (int m = 0; m < 3; m++) {
    if (m == 1 && !up) continue;
    if (m == 2 && !mt) continue;
    if (k > 0) b.appendInline("#SkyyGTabs", "Group { Anchor: (Width: 5); }");
    String nm = m == 0 ? "Reforge" : (m == 1 ? "Upgrade" : "Multitool");
    b.appendInline("#SkyyGTabs", "TextButton #SkyyGTab" + m + " { Anchor: (Width: " + tw + ", Height: 44); Text: \"" + nm + "\"; " + btn(m == sel ? 0 : 1) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGTab" + m, @EVD@.of("a", "mode:" + m));
    k++;
  }
  return n;
}""")
# ================================================================= ReforgePage (spec 5.4 + 5.8): the vanilla item-repair page look''')
# the Reforge anvil and the /multitool bench: the tab row replaces the column title
rep(r'''  b.appendInline("#SkyyGAnvil", "Label #SkyyGAnvilT { Anchor: (Height: 35); Padding: (Horizontal: 8); Text: \"\"; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }");
  b.set("#SkyyGAnvilT.Text", "Anvil");''', r'''  @PKG@.GearUi.tabs(b, ev, "#SkyyGAnvil", 0, 562, "Anvil");          // 0.2.22: Reforge | Upgrade | Multitool''')
rep(r'''  b.appendInline("#SkyyGAnvil", "Label #SkyyGAnvilT { Anchor: (Height: 35); Padding: (Horizontal: 8); Text: \"\"; Style: (RenderBold: true, VerticalAlignment: Center, FontSize: 15, TextColor: #afc2c3); }");
  b.set("#SkyyGAnvilT.Text", "Merge");''', r'''  @PKG@.GearUi.tabs(b, ev, "#SkyyGAnvil", 2, 562, "Merge");          // 0.2.22: Reforge | Upgrade | Multitool''')

# ================================================================================================================ 3b. GearLog.flush (fix round)
# critic 1 (inherited from 0.2.21): flush() took the queue OUTSIDE WLOCK, so when the scheduler's run() had just taken the BEGIN line and was
# about to write it, a world thread's flush() found nothing and returned before the line was on disk - the materials / hatchet could move
# first. Now take() runs INSIDE WLOCK (for the scheduler and for flush alike): whoever took a line holds WLOCK until it is written, so a
# flush() that finds the queue empty has waited for every write in flight. Lock order is always WLOCK -> class monitor (take); line() /
# kick() take only the class monitor, never WLOCK - no deadlock.
rep(r'''public static void flush() {
  String text = take();
  java.nio.file.Path f = FILE;
  if (f == null || text.length() == 0) return;
  synchronized (WLOCK) { write(f, text); }
}""")''', r'''public static void flush() {
  synchronized (WLOCK) { flushLocked(); }
}""")''')
rep(r'''# ================================================================= GearLog: gear.log (spec 8.2), queued, written on the scheduler''',
    r'''# ================================================================= GearLog: gear.log (spec 8.2), queued, written on the scheduler
# 0.2.22 fix round: flush() runs take + write under WLOCK (flushLocked, defined before flush)''')
rep(r'''M(glg, r"""
public static void flush() {''', r'''M(glg, r"""
public static void flushLocked() {
  String text = take();
  java.nio.file.Path f = FILE;
  if (f == null || text.length() == 0) return;
  write(f, text);
}""")
M(glg, r"""
public static void flush() {''')

# ================================================================================================================ 4. GearUp + the Upgrade tab + /upgrade
UP_PY = r'''# ####################################################################################################################################
# 0.2.22 UPGRADE INSIDE THE REFORGE PAGE (tools/gear_0_2_22_patch.py header): GearUp (the ladder table, costs from the live recipes or the
# row, the upgraded document, the write), the Reforge page's Upgrade mode (ReforgePage.up*, hooked in front of build / handleDataEvent), the
# /multitool page's tab clicks, UpCmd (/upgrade = Reforge on the Upgrade tab); + GearUnid.reView (bags re-render their name at the stamp
# scan). Placed after /multitool: it calls GearMerge (plain, inDoc, json, empty), GearForge, GearStamp, GearRoll, GearLevel, GearView, GearUi.
# ####################################################################################################################################
for _c, _m in ((CRR, "getInput"), (CRR, "getPrimaryOutput"), (CRR, "getId"), (MQ, "getItemId"), (MQ, "getQuantity"), (IC, "removeItemStackFromSlot"),
               (IC, "setItemStackForSlot"), (IS, "withQuantity")):
    B.probe(pool, _c, _m)
gup = mk("GearUp")
upc = mk("UpCmd", APC)
UP_CLASSES = [gup, upc]
# THE LADDER TABLE: one row per step - kind ("up"; "convert" reserved), from, to, xc (a written cost Object[] { String[] ids, int[] qty,
# "row" }, or null = read the recipe). Fix round (critic 2): ONE immutable snapshot TAB = Object[] { String[] from, String[] to, Object[]
# xc, String[] kind, String source text } published through ONE volatile field; every reader takes it once into a local (tab()), so a live
# Server Setup edit on one world thread can never pair a row index of the new table with a "to" / cost of the old one on another.
F(gup, "public static volatile Object[] TAB = new Object[] { new String[0], new String[0], new Object[0], new String[0], null };")
F(gup, "public static final java.util.concurrent.ConcurrentHashMap COST = new java.util.concurrent.ConcurrentHashMap();")   # "from>to" -> Object[] or FALSE
F(gup, "public static volatile int COST_N = -1;")
F(gup, "public static volatile int CRASH_AT = 0;")                 # harness only: 1 = throw right after the materials left (a crash)
F(gup, "public static volatile boolean AFTER_THROWS = false;")     # harness only: the post-swap bookkeeping throws
F(gup, 'public static final String SEP = ">";')
M(gup, r"""
public static boolean okId(String a) {
  if (a == null || a.length() < 1 || a.length() > 120) return false;
  for (int i = 0; i < a.length(); i++) {
    char c = a.charAt(i);
    if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || c == '-')) return false;
  }
  return true;
}""")
# a written cost "Id*6+Id2*1" (no * = 1): Object[] { String[] ids, int[] qty, "row" }, or a String = the problem
M(gup, r"""
public static Object parseCost(String c, String from, String to) {
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList qs = new java.util.ArrayList();
  String[] ps = (c == null ? "" : c).split("[+]", -1);
  for (int i = 0; i < ps.length; i++) {
    String p = ps[i].trim();
    if (p.length() == 0) return "an empty material in (" + c + ")";
    int st = p.lastIndexOf('*');
    String id = st < 0 ? p : p.substring(0, st).trim();
    int q = 1;
    if (st >= 0) {
      try { q = Integer.parseInt(p.substring(st + 1).trim()); } catch (Throwable t) { return "'" + p + "' needs a whole number after *"; }
    }
    if (!okId(id)) return "'" + id + "' is not an item id";
    if (q < 1 || q > 9999) return "'" + p + "': the amount must be 1 to 9999";
    if (id.equals(from) || id.equals(to)) return id + " cannot pay for its own upgrade";
    int j = ids.indexOf(id);
    if (j >= 0) qs.set(j, Integer.valueOf(((Integer) qs.get(j)).intValue() + q));
    else { ids.add(id); qs.add(Integer.valueOf(q)); }
  }
  String[] ia = new String[ids.size()];
  int[] qa = new int[ids.size()];
  for (int i = 0; i < ia.length; i++) { ia[i] = (String) ids.get(i); qa[i] = ((Integer) qs.get(i)).intValue(); }
  return new Object[] { ia, qa, "row" };
}""")
# THE TABLE TEXT -> Object[] { String[] from, String[] to, String first problem (null = none), Object[] written costs, String[] kinds }; a
# bad part is skipped, the rest is kept. A row "A>B>C" = two "up" steps; "B(Id*N+...)" = the written cost of the step INTO B; "A~B" = a
# convert row (reserved, refused)
M(gup, r"""
public static Object[] parse(String s) {
  java.util.ArrayList f = new java.util.ArrayList();
  java.util.ArrayList t = new java.util.ArrayList();
  java.util.ArrayList x = new java.util.ArrayList();
  String err = null;
  String[] ls = (s == null ? "" : s).split(",");
  for (int i = 0; i < ls.length; i++) {
    String l = ls[i].trim();
    if (l.length() == 0) continue;
    if (l.indexOf('~') >= 0) { if (err == null) err = "'" + l + "' is a convert row (~) - converting an item's type is not built yet"; continue; }
    String[] el = l.split(SEP, -1);
    if (el.length < 2) { if (err == null) err = "'" + l + "' needs at least two item ids joined by " + SEP; continue; }
    String[] ids = new String[el.length];
    Object[] cs = new Object[el.length];
    for (int k = 0; k < el.length; k++) {
      String e = el[k].trim();
      String c = null;
      int o = e.indexOf('(');
      if (o >= 0) {
        if (!e.endsWith(")")) { if (err == null) err = "'" + e + "' needs a closing )"; continue; }
        c = e.substring(o + 1, e.length() - 1);
        e = e.substring(0, o).trim();
      }
      if (!okId(e)) { if (err == null) err = "'" + e + "' is not an item id"; continue; }
      ids[k] = e;
      if (c == null) continue;
      if (k == 0) { if (err == null) err = "'" + e + "' starts its row - a cost belongs to the item it upgrades INTO"; cs[k] = Boolean.FALSE; continue; }
      Object pc = parseCost(c, ids[k - 1] == null ? "" : ids[k - 1], e);
      if (pc instanceof String) { if (err == null) err = (String) pc; cs[k] = Boolean.FALSE; }
      else cs[k] = pc;
    }
    for (int k = 0; k + 1 < ids.length; k++) {
      String a = ids[k];
      String b = ids[k + 1];
      if (a == null || b == null || cs[k + 1] instanceof Boolean) continue;
      if (a.equals(b)) { if (err == null) err = a + " cannot upgrade into itself"; continue; }
      if (f.contains(a)) { if (err == null) err = a + " is in two ladders (an item has one next tier)"; continue; }
      f.add(a);
      t.add(b);
      x.add(cs[k + 1]);
    }
  }
  for (int i = 0; i < f.size() && err == null; i++) {
    String start = (String) f.get(i);
    String cur = (String) t.get(i);
    for (int n = 0; n <= f.size() && cur != null; n++) {
      if (cur.equals(start)) { err = start + " comes back to itself (a loop)"; break; }
      int j = f.indexOf(cur);
      cur = j < 0 ? null : (String) t.get(j);
    }
  }
  String[] fa = new String[f.size()];
  String[] ta = new String[t.size()];
  Object[] xa = new Object[x.size()];
  String[] ka = new String[f.size()];
  for (int i = 0; i < fa.length; i++) { fa[i] = (String) f.get(i); ta[i] = (String) t.get(i); xa[i] = x.get(i); ka[i] = "up"; }
  return new Object[] { fa, ta, err, xa, ka };
}""")
# the live table (GearCfg.UP_LADDERS, parsed again only when the text changed); a loop found here drops the whole text (one WARN). Returns
# the snapshot (TAB) the caller must use for the whole lookup.
M(gup, r"""
public static Object[] tab() {
  String s = @PKG@.GearCfg.UP_LADDERS;
  if (s == null) s = "";
  Object[] cur = TAB;
  if (s.equals(cur[4])) return cur;
  Object[] p = parse(s);
  String[] f = (String[]) p[0];
  String[] t = (String[]) p[1];
  Object[] x = (Object[]) p[3];
  String[] k = (String[]) p[4];
  if (p[2] != null) {
    @PKG@.Gear.warnOnce("upl:" + s.hashCode(), "config.properties: upgrade.ladders: " + p[2] + " - that part is skipped");
    if (((String) p[2]).indexOf("(a loop)") >= 0) { f = new String[0]; t = new String[0]; x = new Object[0]; k = new String[0]; }
  }
  Object[] nt = new Object[] { f, t, x, k, s };
  TAB = nt;
  return nt;
}""")
# the step from id in one snapshot: its row (-1 = none)
M(gup, r"""
public static int rowIn(Object[] tb, String id) {
  if (id == null) return -1;
  String[] f = (String[]) tb[0];
  for (int i = 0; i < f.length; i++) if (f[i].equals(id)) return i;
  return -1;
}""")
M(gup, "public static int row(String id) { return rowIn(tab(), id); }")
M(gup, r"""
public static String next(String id) {
  Object[] tb = tab();
  int i = rowIn(tb, id);
  String[] t = (String[]) tb[1];
  return i < 0 || i >= t.length ? null : t[i];
}""")
# the step's kind ("up"; null = no step)
M(gup, r"""
public static String kind(String id) {
  Object[] tb = tab();
  int i = rowIn(tb, id);
  String[] k = (String[]) tb[3];
  return i < 0 || i >= k.length ? null : k[i];
}""")
# the written cost of the step from -> to (null = read the recipe)
M(gup, r"""
public static Object[] written(String from, String to) {
  Object[] tb = tab();
  int i = rowIn(tb, from);
  String[] t = (String[]) tb[1];
  Object[] x = (Object[]) tb[2];
  if (i < 0 || i >= t.length || i >= x.length || to == null || !t[i].equals(to)) return null;
  if (!(x[i] instanceof Object[])) return null;
  return (Object[]) x[i];
}""")
M(gup, "public static int steps() { return ((String[]) tab()[0]).length; }")
M(gup, r"""
public static int writtenSteps() {
  Object[] x = (Object[]) tab()[2];
  int n = 0;
  for (int i = 0; i < x.length; i++) if (x[i] instanceof Object[]) n++;
  return n;
}""")
# Server Setup check= (key, value) -> null = fine, else the reason (every item and written material must exist on this server)
M(gup, r"""
public static String checkLadders(String key, String value) {
  Object[] p = parse(value);
  if (p[2] != null) return "Upgrade ladders: " + p[2] + ".";
  String[] f = (String[]) p[0];
  String[] t = (String[]) p[1];
  Object[] x = (Object[]) p[3];
  for (int i = 0; i < f.length; i++) {
    if (@PKG@.Gear.item(f[i]) == null) return "Upgrade ladders: there is no item " + f[i] + " on this server.";
    if (@PKG@.Gear.item(t[i]) == null) return "Upgrade ladders: there is no item " + t[i] + " on this server.";
    if (x[i] instanceof Object[]) {
      String[] m = (String[]) ((Object[]) x[i])[0];
      for (int j = 0; j < m.length; j++) if (@PKG@.Gear.item(m[j]) == null) return "Upgrade ladders: there is no item " + m[j] + " on this server (a material of " + t[i] + ").";
    }
  }
  return null;
}""")
# one recipe -> the cost of from -> to: Object[] { String[] ids, int[] qty, String recipe id } or null (not this step / not payable here)
M(gup, r"""
public static Object[] fromRecipe(@CRR@ rc, String from, String to) {
  if (rc == null) return null;
  @MQ@ po = rc.getPrimaryOutput();
  if (po == null || !to.equals(po.getItemId()) || po.getQuantity() != 1) return null;
  @MQ@[] in = rc.getInput();
  if (in == null) return null;
  boolean has = false;
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList qs = new java.util.ArrayList();
  for (int i = 0; i < in.length; i++) {
    @MQ@ q = in[i];
    if (q == null) continue;
    String iid = q.getItemId();
    if (iid == null) return null;
    if (iid.equals(from) && !has && q.getQuantity() == 1) { has = true; continue; }
    if (iid.equals(from) || iid.equals(to)) return null;
    if (q.getQuantity() < 1) continue;
    int j = ids.indexOf(iid);
    if (j >= 0) qs.set(j, Integer.valueOf(((Integer) qs.get(j)).intValue() + q.getQuantity()));
    else { ids.add(iid); qs.add(Integer.valueOf(q.getQuantity())); }
  }
  if (!has) return null;
  String[] ia = new String[ids.size()];
  int[] qa = new int[ids.size()];
  for (int i = 0; i < ia.length; i++) { ia[i] = (String) ids.get(i); qa[i] = ((Integer) qs.get(i)).intValue(); }
  return new Object[] { ia, qa, rc.getId() };
}""")
# the cost of from -> to read from the LIVE CraftingRecipe store (cached until the store's size changes); null = no recipe makes it
M(gup, r"""
public static Object[] cost(String from, String to) {
  if (from == null || to == null) return null;
  Object[] wr = written(from, to);          // a row cost "A>B(Id*N+...)" wins
  if (wr != null) return wr;
  java.util.Map m = null;
  try { m = @CRR@.getAssetMap().getAssetMap(); } catch (Throwable t) { m = null; }
  if (m == null) return null;
  int n = m.size();
  if (n != COST_N) { COST.clear(); COST_N = n; }
  String k = from + SEP + to;
  Object c = COST.get(k);
  if (c instanceof Object[]) return (Object[]) c;
  if (c != null) return null;
  Object[] best = null;
  String bid = null;
  try {
    java.util.Iterator it = new java.util.ArrayList(m.values()).iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @CRR@)) continue;
      Object[] r = fromRecipe((@CRR@) o, from, to);
      if (r == null) continue;
      String rid = (String) r[2];
      if (best == null || (rid != null && (bid == null || rid.compareTo(bid) < 0))) { best = r; bid = rid; }
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("upcost", "could not read the crafting recipes for the upgrade costs: " + t); return null; }
  COST.put(k, best == null ? (Object) Boolean.FALSE : (Object) best);
  return best;
}""")
M(gup, r"""
public static String costText(Object[] c) {
  if (c == null) return "no recipe";
  String[] ids = (String[]) c[0];
  int[] q = (int[]) c[1];
  StringBuilder sb = new StringBuilder();
  for (int i = 0; i < ids.length; i++) {
    if (sb.length() > 0) sb.append(", ");
    sb.append(ids[i]).append(" x").append(q[i]);
  }
  return sb.length() == 0 ? "nothing" : sb.toString();
}""")
M(gup, r"""
public static String special(String id) {
  return @PKG@.Gear.itemName(id) + " is a special item (Mythic, Set or Untiered) - it keeps its own powers and never upgrades.";
}""")
# Object[] { String why (null = it can be upgraded), String next id, Object[] cost }
M(gup, r"""
public static Object[] check(@IS@ s, java.util.UUID u) {
  if (!@PKG@.GearCfg.UP_ON) return new Object[] { "Upgrading is switched off on this server.", null, null };
  if (s == null || s.isEmpty()) return new Object[] { "Pick an item from the list.", null, null };
  String id = s.getItemId();
  String to = next(id);
  if (to == null) return new Object[] { @PKG@.Gear.itemName(id) + " has no next tier.", null, null };
  if (s.getQuantity() != 1) return new Object[] { "That item is a stack of " + s.getQuantity() + " - split it first.", to, null };
  if (@PKG@.GearUt.has(id) || @PKG@.GearUtFx.mythicId(id)) return new Object[] { special(id), to, null };
  int st = @PKG@.GearData.state(s.getMetadata());
  if (st == 3) return new Object[] { "The gear data on that item is unreadable - an admin can check it with /gear read.", to, null };
  if (st == 4) return new Object[] { "That item comes from a newer SkyyGear - it cannot be upgraded here.", to, null };
  @BD@ d = @PKG@.GearMerge.inDoc(s);
  if (st != 0 && d == null) return new Object[] { "The gear data on that item is unreadable - an admin can check it with /gear read.", to, null };
  if (d != null) {
    if (!@PKG@.GearData.identified(d)) return new Object[] { "Identify that item first" + @PKG@.GearCfg.idHow() + ".", to, null };
    if (@PKG@.GearData.rarity(d) > 4 || @PKG@.GearSet.of(d) != null) return new Object[] { special(id), to, null };
  }
  if (@PKG@.Gear.item(to) == null) return new Object[] { "There is no " + to + " on this server (its mod is not loaded).", to, null };
  if (@PKG@.GearUt.has(to) || @PKG@.GearUtFx.mythicId(to)) return new Object[] { @PKG@.Gear.itemName(to) + " is a special item - nothing upgrades into it.", to, null };
  Object[] c = cost(id, to);
  if (c == null) return new Object[] { "No recipe makes " + @PKG@.Gear.itemName(to) + " from " + @PKG@.Gear.itemName(id) + " - an admin can check Server Setup -> Gear -> Upgrades.", to, null };
  String[] mi = (String[]) c[0];
  for (int i = 0; i < mi.length; i++) if (@PKG@.Gear.item(mi[i]) == null) return new Object[] { "There is no " + mi[i] + " on this server (a material of this upgrade) - an admin can check Server Setup -> Gear -> Upgrades.", to, null };
  String bw = @PKG@.GearRoll.blockWhy(to, u);
  if (bw != null) return new Object[] { bw, to, c };
  return new Object[] { null, to, c };
}""")
# the most a fresh roll of stat si at rarity r and level L can be on item id (its own pool's spare-slot boost included - tools only)
M(gup, r"""
public static int capOf(int si, String id, int r, int L) {
  int slot = @PKG@.GearData.slotOf(id);
  int ps = @PKG@.GearRoll.pool(slot, id).length;
  double b = @PKG@.GearRoll.spare(slot, r, ps);
  int[] bb = b > 0.0 ? @PKG@.GearRoll.boundsX(si, r, L, 1.0 + b / 100.0) : @PKG@.GearRoll.bounds(si, r, L);
  return bb[1];
}""")
# one line value re-levelled from level a to level b (header 3): x factor(b) / factor(a), never below v, at most the cap unless v was above it;
# info[1]++ when the cap lowered the scaled value
M(gup, r"""
public static int relevel(int v, int si, String to, int r, int a, int b, int[] info) {
  double fa = @PKG@.GearLevel.factor(a);
  double fb = @PKG@.GearLevel.factor(b);
  long x = fa > 0.0 ? Math.round((double) v * fb / fa) : (long) v;
  if (x < (long) v) x = (long) v;
  int hi = capOf(si, to, r, b);
  long lim = hi > v ? (long) hi : (long) v;
  if (x > lim) { x = lim; info[1]++; }
  if (x < 1L) x = 1L;
  return (int) x;
}""")
# THE UPGRADED DOCUMENT (header 3); lvl = the next tier's craft level (-1 = no stamp). info: [1] lines lowered to the cap, [2] the old level,
# [3] the new level, [4] bought level ups not carried
M(gup, r"""
public static @BD@ docI(@IS@ s, String to, java.util.UUID u, int lvl, int[] info) {
  @BD@ d = @PKG@.GearMerge.inDoc(s);
  if (@PKG@.GearMerge.plain(d)) return @PKG@.GearRoll.craftDoc(to, u, lvl);
  String id = s.getItemId();
  int a = @PKG@.GearLevel.level(id, d);
  info[2] = a;
  info[4] = @PKG@.GearData.num(d, "lvU", 0);
  @BD@ nd = d.clone();
  nd.remove("lvU");
  nd.remove("lvl0");
  nd.remove("box");
  String kind = @PKG@.GearData.kindFor(to);
  nd.put("kind", new org.bson.BsonString(kind));
  if (nd.containsKey("gate")) nd.put("gate", new org.bson.BsonString(@PKG@.GearDefs.kindGate(kind)));
  if (lvl >= 0) nd.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.clamp(lvl)));
  else nd.remove("lvl");
  int b = @PKG@.GearLevel.level(to, nd);
  info[3] = b;
  int r = @PKG@.GearData.rarity(nd);
  @BA@ ms = @PKG@.GearData.mods(d);
  @BA@ out = new @BA@();
  for (int k = 0; k < ms.size(); k++) {
    @BV@ v = ms.get(k);
    if (v == null) continue;
    if (!v.isDocument()) { out.add(v); continue; }
    @BD@ m = v.asDocument().clone();
    int si = @PKG@.GearDefs.sIndex(@PKG@.GearData.str(m, "s", null));
    int val = @PKG@.GearData.num(m, "v", 0);
    if (si >= 0 && val > 0) m.put("v", new org.bson.BsonInt32(relevel(val, si, to, r, a, b, info)));
    out.add(m);
  }
  nd.put("mods", out);
  return nd;
}""")
M(gup, r"""
public static String lossText(int[] info) {
  String w = "";
  if (info[3] < info[2]) w = "it becomes Lv " + info[3] + " (it is Lv " + info[2] + " now)";
  if (info[4] > 0) w = w + (w.length() > 0 ? "; " : "") + "its " + info[4] + " bought level up" + (info[4] == 1 ? " does" : "s do") + " not carry over (made at your level)";
  if (info[1] > 0) w = w + (w.length() > 0 ? "; " : "") + info[1] + (info[1] == 1 ? " line stops" : " lines stop") + " at the new tier's limit";
  return w.length() > 0 ? "Note: " + w + "." : "";
}""")
# the material sections, storage first: Inventory, Backpack, Hotbar (never armor / utility / tools)
M(gup, r"""
public static @IC@[] matSecs(@INV@ inv) {
  if (inv == null) return new @IC@[0];
  return new @IC@[] { inv.getStorage(), inv.getBackpack(), inv.getHotbar() };
}""")
M(gup, r"""
public static boolean usable(@IS@ x, String id) {
  return x != null && !x.isEmpty() && id.equals(x.getItemId()) && !@PKG@.GearData.hasAnyDoc(x.getMetadata());
}""")
M(gup, r"""
public static int have(@INV@ inv, String id) {
  @IC@[] cs = matSecs(inv);
  int n = 0;
  for (int k = 0; k < cs.length; k++) {
    @IC@ c = cs[k];
    if (c == null) continue;
    boolean dup = false;
    for (int j = 0; j < k; j++) if (cs[j] == c) dup = true;
    if (dup) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (usable(x, id)) n = n + x.getQuantity();
    }
  }
  return n;
}""")
# the first material that is short, in words (null = enough of everything)
M(gup, r"""
public static String shortOf(@INV@ inv, Object[] c) {
  if (c == null) return "No recipe for this upgrade.";
  String[] ids = (String[]) c[0];
  int[] q = (int[]) c[1];
  for (int i = 0; i < ids.length; i++) {
    int h = have(inv, ids[i]);
    if (h < q[i]) return "You need " + (q[i] - h) + " more " + @PKG@.Gear.itemName(ids[i]) + " (you have " + h + " of " + q[i] + ").";
  }
  return null;
}""")
# Object[] { String why, String next id, BD preview (null = plain: it rolls on upgrade), Boolean plain, Integer level, String note, Object[] cost }
M(gup, r"""
public static Object[] preview(@IS@ s, java.util.UUID u) {
  Object[] c = check(s, u);
  if (c[0] != null) return new Object[] { c[0], c[1], null, Boolean.FALSE, Integer.valueOf(-1), "", c[2] };
  String to = (String) c[1];
  int lvl = @PKG@.GearRoll.craftLevel(to, u);
  boolean pl = @PKG@.GearMerge.plain(@PKG@.GearMerge.inDoc(s));
  int[] info = new int[5];
  @BD@ d = pl ? null : docI(s, to, u, lvl, info);
  return new Object[] { null, to, d, Boolean.valueOf(pl), Integer.valueOf(lvl), pl ? "" : lossText(info), c[2] };
}""")
# every item on a ladder the player carries: int[] { section, slot }
M(gup, r"""
public static java.util.ArrayList rows(@INV@ inv) {
  java.util.ArrayList out = new java.util.ArrayList();
  if (inv == null) return out;
  for (int k = 0; k < @PKG@.GearStamp.SCAN.length; k++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ it = c.getItemStack((short) i);
      if (it == null || it.isEmpty() || next(it.getItemId()) == null) continue;
      out.add(new int[] { @PKG@.GearStamp.SCAN[k], i });
    }
  }
  return out;
}""")
M(gup, r"""
public static String where(@IC@[] secs, @IC@ c, int slot) {
  String n = "Hotbar";
  if (secs.length > 0 && c == secs[0]) n = "Inventory";
  else if (secs.length > 1 && c == secs[1]) n = "Backpack";
  return n + " " + (slot + 1);
}""")
# put planned material slots 0..n-1 back (each = Object[] { IC, Integer slot, IS before, IS after }); returns what could NOT be put back ("" = all)
M(gup, r"""
public static String restore(java.util.ArrayList plan, int n, @IC@[] secs) {
  StringBuilder bad = new StringBuilder();
  for (int p = 0; p < n && p < plan.size(); p++) {
    Object[] e = (Object[]) plan.get(p);
    @IC@ c = (@IC@) e[0];
    int sl = ((Integer) e[1]).intValue();
    @IS@ before = (@IS@) e[2];
    @IS@ now = c.getItemStack((short) sl);
    if (now != null && !now.isEmpty() && before.getItemId().equals(now.getItemId()) && now.getQuantity() == before.getQuantity()) continue;
    try { c.setItemStackForSlot((short) sl, before); } catch (Throwable x) { }
    @IS@ chk = c.getItemStack((short) sl);
    if (chk == null || chk.isEmpty() || !before.getItemId().equals(chk.getItemId()) || chk.getQuantity() != before.getQuantity()) {
      if (bad.length() > 0) bad.append(", ");
      bad.append(before.getItemId()).append(" x").append(before.getQuantity()).append(" @").append(where(secs, c, sl));
    }
  }
  return bad.toString();
}""")
M(gup, r"""
public static void after(@IC@[] all, String id, String to, String[] mids, int[] mq, int bf, int bt, int[] bm, String who, java.util.UUID u, @BD@ nd, int[] info, int s, int slot) {
  if (AFTER_THROWS) throw new IllegalStateException("harness: after() throws");
  int af = @PKG@.GearStamp.countId(all, id);
  int at = @PKG@.GearStamp.countId(all, to);
  StringBuilder bad = new StringBuilder();
  if (af != bf - 1 || at != bt + 1) bad.append(id).append(' ').append(bf).append("->").append(af).append(' ').append(to).append(' ').append(bt).append("->").append(at);
  for (int k = 0; k < mids.length; k++) {
    int am = @PKG@.GearStamp.countId(all, mids[k]);
    if (am != bm[k] - mq[k]) bad.append(' ').append(mids[k]).append(' ').append(bm[k]).append("->").append(am).append(" (-").append(mq[k]).append(')');
  }
  if (bad.length() > 0) {
    @PKG@.Gear.warn("UPGRADE COUNT MISMATCH for " + who + ": " + bad);
    @PKG@.GearLog.line("UPGRADE-COUNT " + who + " " + u + " " + bad);
  }
  @PKG@.GearLog.line("UPGRADE " + who + " " + u + " " + id + " -> " + to + " " + @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(nd)] + " lv" + @PKG@.GearLevel.level(to, nd) + " [" + @PKG@.GearView.modSummary(nd) + "] lowered " + info[1] + " @" + @PKG@.GearForge.where(s, slot));
}""")
# THE WRITE (header 5). Object[] { Integer code (1 made, 0 refused - nothing moved, -1 failed - see the message), String message, IS the
# upgraded item, BD its document }
M(gup, r"""
public static Object[] upgrade(@INV@ inv, int s, int slot, String id, String fp, java.util.UUID u, String who) {
  @IC@ ic = @PKG@.GearStamp.section(inv, s);
  if (ic == null) return new Object[] { Integer.valueOf(0), "The item moved or changed - pick it again.", null, null };
  @IS@ it = @PKG@.GearStamp.at(inv, s, slot);
  if (!@PKG@.GearForge.same(it, id, fp)) return new Object[] { Integer.valueOf(0), "The item moved or changed - pick it again.", null, null };
  Object[] c = check(it, u);
  if (c[0] != null) return new Object[] { Integer.valueOf(0), (String) c[0], null, null };
  String to = (String) c[1];
  Object[] cost = (Object[]) c[2];
  String sh = shortOf(inv, cost);
  if (sh != null) return new Object[] { Integer.valueOf(0), sh, null, null };
  String[] mids = (String[]) cost[0];
  int[] mq = (int[]) cost[1];
  int lvl = @PKG@.GearRoll.craftLevel(to, u);
  int[] info = new int[5];
  @BD@ nd = null;
  @IS@ ns = null;
  try {
    nd = docI(it, to, u, lvl, info);
    ns = @PKG@.GearData.put(new @IS@(to, 1), nd, u);
  } catch (Throwable t0) { nd = null; ns = null; @PKG@.Gear.warn("upgrade: the document could not be made for " + who + ": " + t0); }
  if (nd == null || ns == null || ns.isEmpty() || !to.equals(ns.getItemId())) return new Object[] { Integer.valueOf(0), "The upgraded item could not be made - nothing was used.", null, null };
  // the plan: storage first, only material stacks without a document, never the item's own slot
  @IC@[] secs = matSecs(inv);
  java.util.ArrayList plan = new java.util.ArrayList();
  StringBuilder pt = new StringBuilder();
  for (int k = 0; k < mids.length; k++) {
    int left = mq[k];
    for (int j = 0; j < secs.length && left > 0; j++) {
      @IC@ mc = secs[j];
      if (mc == null) continue;
      boolean dup = false;
      for (int q = 0; q < j; q++) if (secs[q] == mc) dup = true;
      if (dup) continue;
      for (int i = 0; i < mc.getCapacity() && left > 0; i++) {
        if (mc == ic && i == slot) continue;
        @IS@ x = mc.getItemStack((short) i);
        if (!usable(x, mids[k])) continue;
        int take = x.getQuantity() < left ? x.getQuantity() : left;
        @IS@ rest = take >= x.getQuantity() ? null : x.withQuantity(x.getQuantity() - take);
        plan.add(new Object[] { mc, Integer.valueOf(i), x, rest });
        left = left - take;
        if (pt.length() > 0) pt.append(", ");
        pt.append(mids[k]).append(" x").append(take).append(" @").append(where(secs, mc, i));
      }
    }
    if (left > 0) return new Object[] { Integer.valueOf(0), "You need " + left + " more " + @PKG@.Gear.itemName(mids[k]) + ".", null, null };
  }
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  int bf = @PKG@.GearStamp.countId(all, id);
  int bt = @PKG@.GearStamp.countId(all, to);
  int[] bm = new int[mids.length];
  for (int k = 0; k < mids.length; k++) bm[k] = @PKG@.GearStamp.countId(all, mids[k]);
  @PKG@.GearLog.line("UPGRADE-BEGIN " + who + " " + u + " " + id + " @" + @PKG@.GearForge.where(s, slot) + " " + @PKG@.GearMerge.json(it) + " -> " + to + " " + nd.toJson() + " cost [" + costText(cost) + "] from [" + pt + "]");
  try { @PKG@.GearLog.flush(); } catch (Throwable xf) { }      // UPGRADE-BEGIN is ON DISK before anything moves
  // (a) the materials leave, slot by slot
  String why1 = null;
  int done = 0;
  for (int p = 0; p < plan.size(); p++) {
    Object[] e = (Object[]) plan.get(p);
    @IC@ mc = (@IC@) e[0];
    int sl = ((Integer) e[1]).intValue();
    @IS@ rest = (@IS@) e[3];
    Object tx = null;
    Throwable ex = null;
    try { tx = rest == null ? mc.removeItemStackFromSlot((short) sl) : mc.setItemStackForSlot((short) sl, rest); } catch (Throwable x) { ex = x; }
    @IS@ now = mc.getItemStack((short) sl);
    boolean ok = ex == null && !(tx instanceof @TXN@ && !((@TXN@) tx).succeeded())
      && (rest == null ? (now == null || now.isEmpty()) : (now != null && !now.isEmpty() && rest.getItemId().equals(now.getItemId()) && now.getQuantity() == rest.getQuantity()));
    done = p + 1;
    if (!ok) { why1 = ex != null ? String.valueOf(ex) : "the inventory refused it"; break; }
  }
  if (why1 != null) {
    String rb = restore(plan, done, secs);
    if (rb.length() > 0) {
      @PKG@.Gear.warn("UPGRADE: the materials of " + who + " (" + u + ") could not all be put back - they are in gear.log (UPGRADE-RESTORE-FAILED)");
      @PKG@.GearLog.line("UPGRADE-RESTORE-FAILED " + who + " " + u + " materials not back: " + rb + " (" + why1 + ")");
      return new Object[] { Integer.valueOf(-1), "Something went wrong and some materials could not be put back - an admin can find them in the server log.", null, null };
    }
    @PKG@.GearLog.line("UPGRADE-FAILED " + who + " " + u + " (materials not taken: " + why1 + ") - RESTORED, nothing used");
    return new Object[] { Integer.valueOf(-1), "The inventory refused the change - nothing was used.", null, null };
  }
  if (CRASH_AT == 1) throw new IllegalStateException("harness: a crash right after the materials left");
  // (b) the item's own slot gets the upgraded item
  Object t2 = null;
  Throwable e2 = null;
  try { t2 = ic.setItemStackForSlot((short) slot, ns); } catch (Throwable x2) { e2 = x2; }
  @IS@ now2 = ic.getItemStack((short) slot);
  boolean put = e2 == null && !(t2 instanceof @TXN@ && !((@TXN@) t2).succeeded()) && now2 != null && !now2.isEmpty() && to.equals(now2.getItemId());
  if (!put) {
    String why2 = e2 != null ? String.valueOf(e2) : "the inventory refused it";
    boolean kept = @PKG@.GearForge.same(now2, id, fp);
    if (!kept) {
      try { ic.setItemStackForSlot((short) slot, it); } catch (Throwable xr) { }
      kept = @PKG@.GearForge.same(ic.getItemStack((short) slot), id, fp);
    }
    String rb2 = restore(plan, plan.size(), secs);
    if (!kept || rb2.length() > 0) {
      @PKG@.Gear.warn("UPGRADE FAILED for " + who + " (" + u + "): " + why2 + (kept ? "" : " - the item could not be put back") + (rb2.length() > 0 ? " - materials not back: " + rb2 : "") + "; everything is in gear.log");
      @PKG@.GearLog.line("UPGRADE-RESTORE-FAILED " + who + " " + u + " " + id + " " + @PKG@.GearMerge.json(it) + " (item back " + kept + ") materials not back: [" + rb2 + "]: " + why2);
      return new Object[] { Integer.valueOf(-1), "Something went wrong - an admin can find your item and materials in the server log.", null, null };
    }
    @PKG@.GearLog.line("UPGRADE-FAILED " + who + " " + u + " (upgraded item not written: " + why2 + ") - RESTORED, nothing used");
    return new Object[] { Integer.valueOf(-1), "The inventory refused the upgraded item - nothing was used.", null, null };
  }
  try { after(all, id, to, mids, mq, bf, bt, bm, who, u, nd, info, s, slot); } catch (Throwable xa) { }
  return new Object[] { Integer.valueOf(1), "Upgraded!", ns, nd };
}""")
M(gup, r"""
public static String statusText() {
  int n = steps();
  int w = writtenSteps();
  return "upgrade " + (@PKG@.GearCfg.UP_ON ? "on (Reforge page Upgrade tab + /upgrade, " + n + " step(s): " + (n - w) + " cost(s) from the recipes, " + w + " written)" : "OFF (part.upgrade)") + "; item names " + (@PKG@.GearCfg.NAME_LV ? "end with [Lv N]" : "without the level (view.levelInName off)");
}""")

# ================================================================= GearUnid.reView: a bag's name follows the switch (hooked into the stamp scan)
M(gunid, r"""
public static @IS@ reView(@IS@ s) {
  try {
    @BD@ d = doc(s);
    if (d == null) return s;
    @IS@ v = view(s, d);
    String a = @PKG@.GearView.dispHash(s);
    String b = @PKG@.GearView.dispHash(v);
    if (b == null || b.equals(a)) return s;
    return v;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("bagview", "a mystery bag's name could not be re-rendered: " + t); return s; }
}""")
gsp.getDeclaredMethod("stampStack").insertBefore(J("{ if ($1 != null && !$1.isEmpty() && @PKG@.GearUnid.isBox($1.getItemId())) return @PKG@.GearUnid.reView($1); }"))

# ================================================================= the Reforge page's UPGRADE mode (mode 1; 0 = Reforge). Same page object, same
# anvil selection (selSec / selSlot / selId / selFp / epoch / lastForge), same frame and bottom bar; build / handleDataEvent are hooked
# (insertBefore) so the Reforge code itself is untouched.
for _f in ("public int mode;", "public @BD@ upMade;", "public String upMadeId;"):
    F(rpg, _f)
# one column of lines with a line limit (the last shown line says how many more)
M(rpg, r"""
public static void upCol(@UCB@ b, String parent, String cid, String head, String id, @BD@ d, int w, int max) {
  b.appendInline(parent, "Group " + cid + " { Anchor: (Width: " + w + "); LayoutMode: Top; }");
  b.appendInline(cid, "Label " + cid + "H { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.set(cid + "H.Text", head);
  java.util.ArrayList txt = new java.util.ArrayList();
  java.util.ArrayList col = new java.util.ArrayList();
  if (d != null && @PKG@.GearData.identified(d)) @PKG@.GearView.statLines(id, d, txt, col);
  if (txt.isEmpty()) { txt.add("No modifiers."); col.add(@PKG@.GearDefs.C_GRAY); }
  int n = txt.size();
  for (int i = 0; i < n && i < max; i++) {
    String c = (String) col.get(i);
    String s = (String) txt.get(i);
    if (i == max - 1 && n > max) { s = "... and " + (n - max + 1) + " more line(s) - see the item's tooltip"; c = @PKG@.GearDefs.C_GRAY; }
    b.appendInline(cid, "Label " + cid + "L" + i + " { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: " + (c == null ? "#ffffff" : c) + ", VerticalAlignment: Center); }");
    b.set(cid + "L" + i + ".Text", s);
  }
}""")
# why a held item is not on the Upgrade list (fix round): special first, then a bag / unidentified, else no next tier
M(rpg, r"""
public static String upWhyNot(@IS@ it) {
  String id = it.getItemId();
  if (@PKG@.GearUt.has(id) || @PKG@.GearUtFx.mythicId(id)) return @PKG@.GearUp.special(id);
  @BD@ d = null;
  try { d = @PKG@.GearMerge.inDoc(it); } catch (Throwable t) { d = null; }
  if (d != null && (@PKG@.GearData.rarity(d) > 4 || @PKG@.GearSet.of(d) != null)) return @PKG@.GearUp.special(id);
  if (@PKG@.GearUnid.isBox(id)) return @PKG@.Gear.itemName(id) + " is unidentified loot - open it first; it cannot be upgraded.";
  return @PKG@.Gear.itemName(id) + " has no next tier - it cannot be upgraded.";
}""")
M(rpg, r"""
public boolean upPick(@INV@ inv, int s, int sl) {
  @IS@ it = @PKG@.GearStamp.at(inv, s, sl);
  if (it == null || it.isEmpty() || @PKG@.GearUp.next(it.getItemId()) == null) return false;
  this.selSec = s; this.selSlot = sl; this.selId = it.getItemId(); this.selFp = @PKG@.GearForge.fp(it);
  this.fresh = false; this.before = null; this.after = null; this.upMade = null; this.upMadeId = null;
  this.epoch = @PKG@.Gear.epoch(this.playerRef.getUuid());
  this.info = "=" + @PKG@.Gear.itemName(it.getItemId()) + " is on the anvil.";
  return true;
}""")
M(rpg, r"""
public void upPreselect(@INV@ inv) {
  try {
    if (inv == null) return;
    int s = inv.usingToolsItem() ? 5 : 0;
    int sl = inv.usingToolsItem() ? (int) inv.getActiveToolsSlot() : (int) inv.getActiveHotbarSlot();
    if (upPick(inv, s, sl)) return;
    // fix round (critic 3): the held item has no next tier (a Mythic / Set / Untiered item, a mystery bag, any item off the ladders) -
    // say so in the info bar instead of an unexplained empty anvil (an empty hand = no message)
    @IS@ it = @PKG@.GearStamp.at(inv, s, sl);
    if (it != null && !it.isEmpty()) this.info = "-" + upWhyNot(it);
  } catch (Throwable t) { }
}""")
# a tab switch keeps the item on the anvil when it fits the new mode (Reforge: forgeable; Upgrade: has a next tier)
M(rpg, r"""
public void setMode(int m, @INV@ inv) {
  if (m == this.mode) return;
  this.mode = m;
  this.pageNo = 0;
  this.fresh = false; this.before = null; this.after = null; this.upMade = null; this.upMadeId = null;
  this.info = "";
  if (this.selSec < 0) return;
  @IS@ it = @PKG@.GearStamp.at(inv, this.selSec, this.selSlot);
  boolean same = @PKG@.GearForge.same(it, this.selId, this.selFp);
  boolean fits = same && (m == 1 ? @PKG@.GearUp.next(this.selId) != null : @PKG@.GearData.forgeable(this.selId));
  if (fits) return;
  String n = @PKG@.Gear.itemName(this.selId);
  clearSel();
  if (same) this.info = "=" + n + (m == 1 ? " has no next tier - pick an item from the list." : " cannot be reforged - pick an item from the list.");
}""")
# the materials with have / need (white = enough, gold = short); at most 3 rows (the header says when there are more)
M(rpg, r"""
public void upMats(@UCB@ b, @INV@ inv, Object[] cost, boolean used) {
  b.appendInline("#SkyyGAnvil", "Label #SkyyGMatH { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGMats { Anchor: (Height: 114); LayoutMode: Top; }");
  if (used) { b.set("#SkyyGMatH.Text", "Materials: used up"); return; }
  if (cost == null) { b.set("#SkyyGMatH.Text", "Materials: -"); return; }
  String[] ids = (String[]) cost[0];
  int[] q = (int[]) cost[1];
  b.set("#SkyyGMatH.Text", ids.length == 0 ? "Materials: none" : (ids.length > 3 ? "Materials (3 of " + ids.length + " shown) - have / need" : "Materials - have / need (inventory, backpack, hotbar)"));
  for (int i = 0; i < ids.length && i < 3; i++) {
    int h = @PKG@.GearUp.have(inv, ids[i]);
    String g = "#SkyyGMat" + i;
    b.appendInline("#SkyyGMats", "Group " + g + " { Anchor: (Height: 38); LayoutMode: Left; Padding: (Top: 3); }");
    b.appendInline(g, "ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \"" + @PKG@.Gear.safe(ids[i]) + "\"; }");
    b.appendInline(g, "Label " + g + "N { Anchor: (Width: 360); Padding: (Horizontal: 10); Text: \"\"; Style: (FontSize: 15, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.appendInline(g, "Label " + g + "Q { Anchor: (Width: 160); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + (h >= q[i] ? "#ffffff" : @PKG@.GearDefs.C_GOLD) + ", HorizontalAlignment: End, VerticalAlignment: Center); }");
    b.set(g + "N.Text", @PKG@.Gear.itemName(ids[i]));
    b.set(g + "Q.Text", h + " / " + q[i]);
  }
}""")
# the right column in Upgrade mode (height budget 664 of 674: tabs 48, 1, item 92, 1, next tier 30, materials 26 + 114, lines 240, why 56, button 56)
M(rpg, r"""
public void upAnvil(@UCB@ b, @UEB@ ev, java.util.UUID u, @IS@ sel, @INV@ inv) {
  b.appendInline("#SkyyGMain", "Group #SkyyGAnvil { Anchor: (Width: 562); LayoutMode: Top; }");
  @PKG@.GearUi.tabs(b, ev, "#SkyyGAnvil", 1, 562, "Upgrade");
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #393426(0.5); }");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGSel { Anchor: (Height: 92); LayoutMode: Left; Padding: (Top: 12); }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelIcon { Anchor: (Width: 72, Height: 72); Background: #000000(0.25); }");
  if (sel != null) b.appendInline("#SkyyGSelIcon", "ItemIcon { Anchor: (Width: 64, Height: 64, Left: 4, Top: 4); ItemId: \"" + @PKG@.Gear.safe(sel.getItemId()) + "\"; }");
  b.appendInline("#SkyyGSel", "Label { Anchor: (Width: 14, Height: 72); Text: \"\"; }");
  b.appendInline("#SkyyGSel", "Group #SkyyGSelTxt { Anchor: (Width: 470, Height: 76); LayoutMode: Top; }");
  if (sel == null) {
    b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
    b.set("#SkyyGSelName.Text", "The anvil is empty");
    b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
    b.set("#SkyyGSelSub.Text", "Pick an item that has a next tier - it stays in its own slot.");
    b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #2b3542; }");
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow1 { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow1.Text", "Upgrade: the item becomes its next tier - the SAME rarity and lines.");
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow2 { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow2.Text", "It is made at your level. Cost: the next tier's materials, no coins.");
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow3 { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow3.Text", "A plain item rolls a rarity like a crafted one.");
    b.appendInline("#SkyyGAnvil", "Label #SkyyGHow4 { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, VerticalAlignment: Center); }");
    b.set("#SkyyGHow4.Text", "Tip: hold the item when you type /upgrade to put it on the anvil.");
    return;
  }
  String id = sel.getItemId();
  @BD@ d = @PKG@.GearMerge.inDoc(sel);
  boolean plain = @PKG@.GearMerge.plain(d);
  int r = d == null ? 0 : @PKG@.GearData.rarity(d);
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelName { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 20, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGSelName.Text", d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelSub { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGSelSub.Text", (plain ? "PLAIN" : @PKG@.GearDefs.R_NAME[r].toUpperCase()) + " " + @PKG@.GearView.slotWord(id) + "   -   Level " + @PKG@.GearLevel.level(id, d));
  b.appendInline("#SkyyGSelTxt", "Label #SkyyGSelWhere { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), VerticalAlignment: Center); }");
  b.set("#SkyyGSelWhere.Text", "In your " + @PKG@.GearForge.where(this.selSec, this.selSlot) + (sel.getQuantity() > 1 ? " - a stack of " + sel.getQuantity() + ": split it first." : " - it stays there while you upgrade it."));
  b.appendInline("#SkyyGAnvil", "Group { Anchor: (Height: 1); Background: #2b3542; }");
  boolean made = this.upMade != null && id.equals(this.upMadeId);
  String why = null;
  String note = "";
  Object[] cost = null;
  String resT;
  String resC = "#ffffff";
  @BD@ show = null;
  String showId = null;
  String showHead = null;
  boolean rolls = false;
  if (made) {
    resT = "Upgraded - it is in the same slot.";
    show = this.upMade;
    showId = id;
    showHead = "Its lines";
  } else {
    Object[] pv = @PKG@.GearUp.preview(sel, u);
    why = (String) pv[0];
    cost = (Object[]) pv[6];
    String to = (String) pv[1];
    if (why != null) resT = to == null ? "Next tier: none" : "Next tier: " + @PKG@.Gear.itemName(to);
    else if (((Boolean) pv[3]).booleanValue()) {
      int lv = ((Integer) pv[4]).intValue();
      resT = "Next tier: " + @PKG@.Gear.itemName(to) + " - rolls a rarity" + (lv >= 0 ? ", Lv " + lv : "");
      note = "Your item is plain: it rolls a rarity and lines like a crafted " + @PKG@.Gear.itemName(to) + ".";
      rolls = true;
    } else {
      @BD@ nd = (@BD@) pv[2];
      int r2 = @PKG@.GearData.rarity(nd);
      resC = rarHex(r2);
      resT = "Next tier: " + @PKG@.GearView.nameText(to, nd) + " - " + @PKG@.GearDefs.R_NAME[r2].toUpperCase() + ", Lv " + @PKG@.GearLevel.level(to, nd);
      note = (String) pv[5];
      show = nd;
      showId = to;
      showHead = "It will have (the same rarity and lines, made at your level)";
    }
    if (why == null) why = @PKG@.GearUp.shortOf(inv, cost);
  }
  b.appendInline("#SkyyGAnvil", "Label #SkyyGResN { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 17, RenderBold: true, TextColor: " + resC + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGResN.Text", resT);
  upMats(b, inv, cost, made);
  b.appendInline("#SkyyGAnvil", "Group #SkyyGCols { Anchor: (Height: 240); LayoutMode: Left; Padding: (Top: 4); }");
  if (show != null) upCol(b, "#SkyyGCols", "#SkyyGColU", showHead, showId, show, 562, 8);
  else if (rolls) {
    b.appendInline("#SkyyGCols", "Label #SkyyGColRoll { Anchor: (Width: 562, Height: 28); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Top); }");
    b.set("#SkyyGColRoll.Text", "It rolls new lines for its rarity, like a bench craft.");
  }
  b.appendInline("#SkyyGAnvil", "Label #SkyyGWhy { Anchor: (Height: 56); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + @PKG@.GearDefs.C_GOLD + ", VerticalAlignment: Center, Wrap: true); }");
  b.set("#SkyyGWhy.Text", made ? "Click it in the list to see its next tier." : (why == null ? "The materials are used up. No coins." + (note.length() > 0 ? " " + note : "") : why));
  boolean off = why != null || made;
  String lbl = made ? "Upgraded" : (off ? "Cannot upgrade" : "Upgrade");
  b.appendInline("#SkyyGAnvil", "Group #SkyyGGo { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
  b.appendInline("#SkyyGGo", "TextButton #SkyyGBtnUp { Anchor: (Width: 270, Height: 44); Text: \"" + lbl + "\"; " + @PKG@.GearUi.btn(off ? 3 : 0) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnUp", @EVD@.of("a", "up"));
}""")
M(rpg, r"""
public void upList(@UCB@ b, @UEB@ ev, @INV@ inv) {
  boolean t = @PKG@.GearUi.tex();
  b.appendInline("#SkyyGMain", "Group #SkyyGListBox { Anchor: (Width: 470); LayoutMode: Top; }");
  b.appendInline("#SkyyGListBox", "Group #SkyyGListHead { Anchor: (Height: 30); LayoutMode: Left; Padding: (Right: 15, Bottom: 5); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadItem { Anchor: (Width: 300); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.appendInline("#SkyyGListHead", "Label #SkyyGHeadRar { Anchor: (Width: 150); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: End, VerticalAlignment: Center); }");
  b.set("#SkyyGHeadItem.Text", "Upgradable items (" + this.rows.size() + ")");
  b.set("#SkyyGHeadRar.Text", "Rarity - Level");
  int per = t ? 200 : 12;
  int pages = (this.rows.size() + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  if (t) b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 634); LayoutMode: TopScrolling; " + @PKG@.GearUi.scroll() + " }");
  else b.appendInline("#SkyyGListBox", "Group #SkyyGList { Anchor: (Height: 590); LayoutMode: Top; }");
  if (this.rows.isEmpty()) {
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty1 { Anchor: (Height: 40); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty1.Text", "Nothing on you has a next tier.");
    b.appendInline("#SkyyGList", "Label #SkyyGEmpty2 { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #878e9c, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGEmpty2.Text", "Carry one (e.g. a Soul Orb or Soul Cage) and click Refresh.");
  }
  for (int i = start; i < this.rows.size() && i < start + per; i++) {
    int[] rw = (int[]) this.rows.get(i);
    @IS@ it = @PKG@.GearStamp.at(inv, rw[0], rw[1]);
    if (it == null || it.isEmpty()) continue;
    String id = it.getItemId();
    @BD@ d = @PKG@.GearMerge.inDoc(it);
    int r = d == null ? 0 : @PKG@.GearData.rarity(d);
    boolean on = rw[0] == this.selSec && rw[1] == this.selSlot;
    String rid = "#SkyyGRow" + i;
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(on) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \"" + @PKG@.Gear.safe(id) + "\"; } Label #SkyyGRowName" + i + " { Anchor: (Width: 262); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); } Label #SkyyGRowSub" + i + " { Anchor: (Width: 140); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), HorizontalAlignment: End, VerticalAlignment: Center); } }");
    b.set("#SkyyGRowName" + i + ".Text", (d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d)) + (it.getQuantity() > 1 ? " x" + it.getQuantity() : "") + (on ? "  (on the anvil)" : ""));
    b.set("#SkyyGRowSub" + i + ".Text", (@PKG@.GearMerge.plain(d) ? "Plain" : @PKG@.GearDefs.R_NAME[r]) + " - Lv " + @PKG@.GearLevel.level(id, d));
    b.appendInline("#SkyyGList", "Group { Anchor: (Height: 2); Background: #ffffff(0.6); }");
    ev.addEventBinding(@BT@.Activating, rid, @EVD@.of("a", "sel:" + i));
  }
  if (!t && pages > 1) {
    b.appendInline("#SkyyGListBox", "Group #SkyyGNav { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnPrev { Anchor: (Width: 140, Height: 36); Text: \"Prev\"; " + @PKG@.GearUi.btn(1) + " }");
    b.appendInline("#SkyyGNav", "Label #SkyyGPageTxt { Anchor: (Width: 170, Height: 36); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGPageTxt.Text", "Page " + (this.pageNo + 1) + " / " + pages);
    b.appendInline("#SkyyGNav", "TextButton #SkyyGBtnNext { Anchor: (Width: 140, Height: 36); Text: \"Next\"; " + @PKG@.GearUi.btn(1) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnPrev", @EVD@.of("a", "prev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnNext", @EVD@.of("a", "next"));
  }
}""")
# the page in Upgrade mode (false = upgrading is off: back to Reforge mode, the normal build runs)
M(rpg, r"""
public boolean upBuild(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  if (!@PKG@.GearCfg.UP_ON) { this.mode = 0; this.upMade = null; this.upMadeId = null; return false; }
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  @INV@ inv = p == null ? null : p.getInventory();
  @IS@ sel = null;
  if (this.selSec >= 0) {
    sel = @PKG@.GearStamp.at(inv, this.selSec, this.selSlot);
    if (!@PKG@.GearForge.same(sel, this.selId, this.selFp)) {
      sel = null;
      clearSel();
      this.upMade = null; this.upMadeId = null;
      if (this.info == null || this.info.length() == 0 || this.info.charAt(0) != '-') this.info = "-The item on the anvil moved or changed - pick it again.";
    }
  }
  this.rows = @PKG@.GearUp.rows(inv);
  @PKG@.GearUi.frame(b, "Reforge", 1100, 880);
  b.appendInline("#SkyyGBody", "Label #SkyyGSub { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Upgrade: pick an item - it becomes its next tier with the SAME rarity and lines, made at your level.");
  b.appendInline("#SkyyGBody", "Group #SkyyGMain { Anchor: (Height: 680); LayoutMode: Left; Padding: (Top: 6); }");
  upList(b, ev, inv);
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  b.appendInline("#SkyyGMain", @PKG@.GearUi.vsep());
  b.appendInline("#SkyyGMain", "Label { Anchor: (Width: 14); Text: \"\"; }");
  upAnvil(b, ev, u, sel, inv);
  boolean menu = @PKG@.Gear.bget("config:def:SkyyMenu") != null;
  b.appendInline("#SkyyGBody", "Group #SkyyGBar { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 10); }");
  b.appendInline("#SkyyGBar", "Label #SkyyGInfo { Anchor: (Width: 700, Height: 44); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.GearUi.infoColor(this.info) + ", VerticalAlignment: Center); }");
  b.set("#SkyyGInfo.Text", @PKG@.GearUi.infoText(this.info));
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnRefresh { Anchor: (Width: 170, Height: 44); Text: \"Refresh\"; " + @PKG@.GearUi.btn(1) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 12, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnBack { Anchor: (Width: 170, Height: 44); Text: \"" + (menu ? "Back" : "Close") + "\"; " + @PKG@.GearUi.btn(2) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnBack", @EVD@.of("a", "back"));
  return true;
}""")
# the Upgrade click: the forge() guards (double click, profile:busy, selection, epoch) -> GearUp.upgrade; the new item stays on the anvil
M(rpg, r"""
public void upDo(@INV@ inv) {
  long now = System.currentTimeMillis();
  if (now - this.lastForge < 400L) return;
  this.lastForge = now;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was upgraded. Try again in a moment."; return; }
  if (this.selSec < 0) { this.info = "-Pick an item from the list first."; return; }
  String ep = @PKG@.Gear.epoch(u);
  if (!ep.equals(this.epoch)) { clearSel(); this.epoch = ep; this.info = "-Your profile changed - pick the item again."; return; }
  // fix round (critic 1): the item just made stays on the anvil in the Made state - a second / late click never upgrades it again (it would
  // take the NEXT tier's materials unasked); the player clicks it in the list (upPick clears the Made state) to see and pay its next step
  if (this.upMade != null && this.selId != null && this.selId.equals(this.upMadeId)) { this.info = "-Already upgraded - click it in the list to see its next tier first."; return; }
  Object[] res = @PKG@.GearUp.upgrade(inv, this.selSec, this.selSlot, this.selId, this.selFp, u, this.playerRef.getUsername());
  int code = ((Integer) res[0]).intValue();
  if (code == 1) {
    @BD@ d = (@BD@) res[3];
    @IS@ ns = (@IS@) res[2];
    String to = ns.getItemId();
    @IS@ back = @PKG@.GearStamp.at(inv, this.selSec, this.selSlot);
    this.selId = to;
    this.selFp = @PKG@.GearForge.fp(back != null && !back.isEmpty() ? back : ns);
    this.upMade = d;
    this.upMadeId = to;
    this.info = "+Upgraded to a " + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(d)] + " " + @PKG@.Gear.itemName(to) + " (Lv " + @PKG@.GearLevel.level(to, d) + ")!";
    return;
  }
  String msg = (String) res[1];
  if (msg != null && msg.startsWith("The item moved")) clearSel();
  this.info = "-" + msg;
}""")
# the tab clicks (any mode) and the Upgrade-mode clicks; true = handled (the Reforge code does not run). prev / next / back fall through to
# the Reforge code (same page fields). A stale Reforge click in Upgrade mode and a stale Upgrade click in Reforge mode do nothing.
M(rpg, r"""
public boolean upEvent(@REF@ ref, @ST@ st, String data) {
  if (data == null) return false;
  String a = @PKG@.Gear.jsonStr(data, "a");
  if (a.startsWith("mode:")) {
    int m = -1;
    try { m = Integer.parseInt(a.substring(5)); } catch (Throwable t) { m = -1; }
    if (m == 2) {
      if (@PKG@.GearUi.multiTab()) {
        try { @CMGR@.get().handleCommand(this.playerRef, "multitool"); } catch (Throwable t1) { @PKG@.Gear.warn("reforge page: the Multitool tab could not open /multitool: " + t1); }
      }
      return true;
    }
    if (m != 0 && m != 1) return true;
    if (m == 1 && !@PKG@.GearCfg.UP_ON) { this.info = "-Upgrading is switched off on this server."; rebuild(); return true; }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    setMode(m, p == null ? null : p.getInventory());
    rebuild();
    return true;
  }
  if (this.mode != 1) return a.equals("up");
  if (a.equals("forge") || a.equals("lvl")) return true;
  if (a.equals("refresh")) { this.info = ""; this.upMade = null; this.upMadeId = null; rebuild(); return true; }
  if (!a.equals("up") && !a.startsWith("sel:")) return false;
  @PLA@ p2 = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  @INV@ inv = p2 == null ? null : p2.getInventory();
  if (inv == null) return true;
  if (a.equals("up")) { upDo(inv); rebuild(); return true; }
  int i = -1;
  try { i = Integer.parseInt(a.substring(4)); } catch (Throwable t2) { i = -1; }
  if (i < 0 || this.rows == null || i >= this.rows.size()) return true;
  int[] r = (int[]) this.rows.get(i);
  if (!upPick(inv, r[0], r[1])) this.info = "-That item is not there any more.";
  rebuild();
  return true;
}""")
rpg.getDeclaredMethod("build").insertBefore(J("{ if (this.mode == 1 && upBuild($1, $2, $3, $4)) return; }"))
rpg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ try { if (upEvent($1, $2, $3)) return; } catch (Throwable tu) { @PKG@.Gear.warn(\"reforge page tab / upgrade click failed: \" + tu); return; } }"))
# the /multitool page's tab row: Reforge / Upgrade open the Reforge page in that mode (the commands do the opening, like Back -> /skymenu)
M(mpg, r"""
public boolean tabEvent(String data) {
  if (data == null) return false;
  String a = @PKG@.Gear.jsonStr(data, "a");
  if (!a.startsWith("mode:")) return false;
  String c = a.equals("mode:0") ? "reforge" : (a.equals("mode:1") && @PKG@.GearCfg.UP_ON ? "upgrade" : null);
  if (c != null) {
    try { @CMGR@.get().handleCommand(this.playerRef, c); } catch (Throwable t) { @PKG@.Gear.warn("multitool page: the " + c + " tab failed: " + t); }
  }
  return true;
}""")
mpg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (tabEvent($3)) return; }"))
# ================================================================= /upgrade (player command) = the Reforge page on its Upgrade tab
C(upc, r"""
public UpCmd() {
  super("upgrade", "Open the Reforge page on its Upgrade tab: turn an item into its next tier and keep its rarity and lines");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
}""")
M(upc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!@PKG@.GearCfg.UP_ON) { pr.sendMessage(@MSG@.raw("[Upgrade] Upgrading is switched off on this server.").color(@PKG@.GearDefs.C_GOLD)); return; }
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Upgrade] no player found")); return; }
    @PKG@.GearStamp.scan(pr, p.getInventory());
    @PKG@.ReforgePage page = new @PKG@.ReforgePage(pr);
    page.mode = 1;
    page.upPreselect(p.getInventory());
    p.getPageManager().openCustomPage(ref, store, page);
  } catch (Throwable t) {
    @PKG@.Gear.warn("/upgrade failed: " + t);
    pr.sendMessage(@MSG@.raw("[Upgrade] could not open the Reforge page - the server log has the details"));
  }
}""")
# build check: SkyyArmory 0.1.20's cage recipes (when its jar is in the repo) are exactly one step of the default ladder each, payable here
_AJ = os.path.join(os.path.dirname(HERE), "SkyyArmory", "SkyyArmory-0.1.20.jar")
if os.path.isfile(_AJ):
    import zipfile as _zf
    with _zf.ZipFile(_AJ) as _z:
        _ar = {}
        for _n in _z.namelist():
            if _n.startswith("Server/Item/Items/") and _n.endswith(".json") and os.path.basename(_n)[:-5] in UP_SOUL:
                _ar[os.path.basename(_n)[:-5]] = json.loads(_z.read(_n).decode("utf-8")).get("Recipe")
    _steps = []
    for _i in range(1, len(UP_SOUL)):
        _r = _ar.get(UP_SOUL[_i])
        assert _r and len([_x for _x in _r["Input"] if _x["ItemId"] == UP_SOUL[_i - 1] and int(_x["Quantity"]) == 1]) == 1, \
            "SkyyArmory 0.1.20: %s is not made from %s" % (UP_SOUL[_i], UP_SOUL[_i - 1])
        _oth = [(_x["ItemId"], int(_x["Quantity"])) for _x in _r["Input"] if _x["ItemId"] != UP_SOUL[_i - 1]]
        assert len(_oth) == 2 and all(_q > 0 for _i2, _q in _oth), _oth
        _steps.append("%s %s" % (UP_SOUL[_i].rsplit("_", 1)[1], " + ".join("%d %s" % (_q, _i2.replace("Ingredient_", "").replace("SkyyArmory_", "")) for _i2, _q in _oth)))
    UP_ARMORY = "; ".join(_steps)
    print("0.2.22 upgrade costs (SkyyArmory 0.1.20 recipes, read live in game): " + UP_ARMORY)
else:
    UP_ARMORY = None
    print("note: SkyyArmory/SkyyArmory-0.1.20.jar not in the repo - the ladder / recipe build check was skipped")

'''
rep('''# ####################################################################################################################################
# PART B (2/2): /identify (spec 5.7, pages 5.8).''', UP_PY + '''# ####################################################################################################################################
# PART B (2/2): /identify (spec 5.7, pages 5.8).''')

# ================================================================================================================ 5. setup + ready line + class list
rep('''  getCommandRegistry().registerCommand(new @PKG@.MultiCmd());          // 0.2.21: merge rolled pickaxes / hatchets into a multitool''',
    '''  getCommandRegistry().registerCommand(new @PKG@.MultiCmd());          // 0.2.21: merge rolled pickaxes / hatchets into a multitool
  getCommandRegistry().registerCommand(new @PKG@.UpCmd());             // 0.2.22: /upgrade = the Reforge page on its Upgrade tab''')
rep('''log("[SkyyGear] @VER@ ready - /reforge, /identify, /multitool, /gear (admin:''', '''log("[SkyyGear] @VER@ ready - /reforge, /identify, /multitool, /upgrade, /gear (admin:''')
rep('''+ @PKG@.GearMine.statusText() + "; gear:fn:curve,''', '''+ @PKG@.GearMine.statusText() + "; " + @PKG@.GearUp.statusText() + "; gear:fn:curve,''')
rep('''+ UB_CLASSES + TOOL_MULTI_CLASSES + MERGE_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''',
    '''+ UB_CLASSES + TOOL_MULTI_CLASSES + MERGE_CLASSES + UP_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')

# ================================================================================================================ 6. manifest
rep('''(/multitool merges rolled ones: the better rarity, both tools' lines)''',
    '''(/multitool merges rolled ones: the better rarity, both tools' lines); the Reforge page's Upgrade tab (/upgrade) turns an item into its next tier (Soul Cages) with the same rarity and lines; item names end with their level''')

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", DST)
