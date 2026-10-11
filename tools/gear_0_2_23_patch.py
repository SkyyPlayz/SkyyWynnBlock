"""Derive SkyyGear/build_skyygear_0.2.23.py from the LIVE 0.2.22 (build_skyygear_0.2.22.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_22_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_23_patch.py      then      python SkyyGear/build_skyygear_0.2.23.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.23.py

0.2.23 = THE /smithing HUB (round R3 of research/Requip-Smithing-Spec.md; Skyy 2026-10-10, docs/answered/gear.md LOCKED lines "one command,
one location. we could maybe even make a /smithing that have crafting, reforging and upgrading. (and make it pull from and craft to that
loadout storage ...) in the crafting, we could show the armor sorted into sets you click to open. (maybe use a bigger size than a item
slot, and show the whole set like its on a player. ... (we should give this, and the crafting thing a filter by class. so it only shows
things your class can use" + the popup answers "Needs the accessory (Recommended)" and "Into Requip (Recommended)").
  1. ONE PAGE, FOUR TABS: the 0.2.22 Reforge frame (1100 x 880, title "Smithing") with the tab row Craft | Reforge | Upgrade | Multitool
     (Primary = active, Secondary the rest, 5 px apart; Craft shows while part.smithing is on, Upgrade / Multitool as in 0.2.22).
     /smithing (alias /smith) opens Craft; /reforge, /upgrade, /multitool open their tab (their 0.2.21 / 0.2.22 pages, now titled
     "Smithing"). A tab click opens the other tab through its command (the 0.2.22 pattern - one page object per tab).
  2. CRAFT TAB (SmithPage + GearSmith): left column = the categories Combat armor / Gathering armor / Weapons / Tools / Multitools, the
     class filter (My class / Show all) and where crafted gear goes (Requip / Inventory); right = SET CARDS 266 x 300, 3 per row, 2 rows
     per page: armor = the whole set as a figure (64 px icon cells: Head top centre, Hands left of Chest, Legs bottom centre; metadata-free
     ItemIcon ids only), "Lv A-B - Heavy / Light / Cloth" (gathering: "Mining"), the set's base Health + Resistance added up at the level
     YOU would make it (GearBase.armorTarget), the full-set bonus (a Mining Set's set.<id> row; combat sets: none) and a state word
     ("2/4 craftable", "Locked - needs Armor Bench II accessory", "Level too low", "Browse only - needs SkyySacks 0.7.17"); weapons /
     tools / multitools = one card per FAMILY (its tier ladder as up to 8 icons). Click a card -> the piece page: a big figure / the
     ladder, the stats, how the rarity rolls, then one row per piece / tier (icon, name + level band, every material have / need - white
     enough, gold short - and Craft, greyed with the reason) and "Craft every missing piece" (each piece not already in your inventory or
     Requip that you can afford and are allowed to make; one transaction per piece; stops at the first refusal).
  3. RECIPES = the LIVE CraftingRecipe store (re-read when its size or the config changes): every recipe whose primary output (quantity 1)
     is a craftable SkyyGear item (GearRoll.craftable: weapons, armor, rolling tools, multitools; never Untiered / Mythic ids), that has a
     Crafting-type bench requirement (Fieldcraft or a bench that has a Skyy bench accessory - all benches when SkyyAccessories is not
     loaded; never the retired Alchemy / Cooking / Campfire, never a Processing (timed) bench, never Diagram / Structural crafting = the
     look recipes), and that takes no gear item as an input (alterations and the Soul Cage tier-ups = the Upgrade tab). One recipe per
     output (the lowest recipe id).
  4. THE ACCESSORY RULE (Skyy: "Needs the accessory"): which recipes may be crafted here comes ONLY from SkyySacks' sacks:fn:craftList
     (Object[] { UUID, "smith" } -> String[] recipe ids - the /craft rule: bench accessory tier, knowledge, not table-only). No SkyySacks
     0.7.17 bridge = the tab browses, every Craft button refuses with that note. Level gate = GearRoll.blockWhy (craft.belowBand), as at
     the bench. have / need from sacks:fn:craftHave (inventory + bags), else counted here (inventory only, for the display).
  5. THE TRANSACTION (GearSmith.craft, world thread, one click): gates (part.smithing, the bridge, the recipe still listed and allowed,
     the level gate) -> ROOM checked FIRST (a free Inventory / Backpack slot, or Requip says canDeposit) -> the document is rolled in memory
     exactly like a bench craft (GearRoll.craftLevel + craftDoc: the craft odds + the Smithing step-up; part.craft off = a plain item, as a
     bench gives) -> CRAFT-BEGIN in gear.log (recipe, the rolled document, the material counts before) FLUSHED -> sacks:fn:craftPay
     (inventory first, then bags; paid < 1 = craftRefund + refused) -> DELIVER: "Crafted gear to: Requip" on and Requip accepts ->
     wardrobe:fn:deposit (the stack, never put in a slot first, + the evidence of what the payment took - FIXER 2); Requip refusing / off /
     absent / nothing provable -> a free inventory slot (re-checked after the pay; "Requip: <why>" in the message); delivery failed completely ->
     craftRefund + CRAFT-FAILED; made -> craftCommit, Smithing XP paid ONCE per item through GearRoll.payCraft (the bench / /craft path:
     the 0.2.17 anti-loop tool scaling and the 0.2.18 multitool 0 XP included), CRAFT-DONE, the bench's below / above-band chat line. A
     crash between pay and deliver can only LOSE the materials (CRAFT-BEGIN lists them), never copy an item. Page guards: profile:busy,
     the profile epoch, a click token (a second click of an old page is refused), 1 s between crafts per player.
  6. CLASS FILTER (GearSmith.shows; "My class" on by default, "Show all" = the player switch gear.smithShowAll): weapons whose id matches
     SkyyClasses' class:weapons:<your class> or class:weapons:free prefixes; combat armor of your class's armor type (Server Setup row
     smith.classArmor, default Warrior / Berserker Heavy, Archer / Assassin / Monk Light, Mage / Priest Cloth; a class not listed = all
     types; the type = the piece's vanilla sound set: Cloth / Leather (Light) / else Heavy, the 0.2.11 loot-bag rule); gathering armor,
     tools and multitools always; no class picked = everything. Published as gear:fn:classShow (Object[] { UUID, String itemId } ->
     Boolean, the same rule incl. the player's Show all switch) for the SkyySacks 0.7.17 /craft Smithing tab.
  7. F1 (spec section 1): /upgrade and the /multitool merge now COPY every metadata key that is not SkyyGear's own (SkyyGear, SkyyGearView,
     SkyyRolls(+View), SkyyUnid, the item display) from the source stack onto the new one (GearData.carry): Upgrade = from the item, Merge
     = from the PICKAXE (the multitool keeps the pickaxe's Requip entry), and the hatchet's Requip eid is reported used up
     (wardrobe:fn:gone { UUID, eid, "merged" }). Reforge / level up / identify already write onto the same stack (F2).
  8. UPGRADE MATERIALS FROM THE BAGS TOO: the Upgrade tab takes what the inventory lacks from the Magic Bags (sacks:fn:count / take, put
     back with sacks:fn:put on every failure, sacks:fn:commit after success); have / need and "You need N more" count inventory + bags;
     the UPGRADE-BEGIN plan lists the bag part.
  9. REQUIP ITEMS IN THE LISTS: the Reforge and Upgrade lists also show your IN Requip gear (wardrobe:fn:list, tag "Requip"); a click
     FETCHES it (wardrobe:fn:fetch: it becomes OUT, its stamp and every loadout pick stay) and puts it on the anvil; "Return to Requip"
     (wardrobe:fn:depositSlot) puts the item on the anvil back. Nothing here when SkyyWardrobe 0.2 is not loaded.
  10. BRIDGES (new, published in setup): gear:fn:smithing (Object[] { UUID, String tab craft|reforge|upgrade|multitool } -> Boolean: runs
     that tab's command for the online player) and gear:fn:classShow. Read: wardrobe:fn:canDeposit / depositSlot / deposit / list /
     fetch / gone, requip:stampKey, sacks:fn:craftList / craftHave / craftPay / craftRefund / craftCommit / count / take / put / commit,
     class:<uuid>, class:list, class:weapons:*, settings:fn:get / set. Every one missing = that part greyed with a note.
SAVED DATA: nothing new on items (crafted items carry the ordinary gear document; copied foreign keys are the other mod's own). Two new
config rows (absent = default, no one-time update): part.smithing, smith.classArmor (a fresh file gets a 0.2.23 block). Two player switches
(SkyyMenu settings, memory only without SkyyMenu): gear.smithShowAll (off), gear.smithToRequip (on).
ROLLBACK (for tools/deploy_set.py, reported, not edited here): 0.2.23 -> 0.2.22 is safe: the hub goes; crafted items are plain gear
documents; carried foreign keys are ignored by 0.2.22; the two config lines are ignored. BUT only while SkyyWardrobe 0.2 (Requip) is NOT
live: 0.2.22's Upgrade / Multitool merge build a fresh stack without GearData.carry and strip the SkyyRequip stamp (the Requip entry reads
NOT WITH YOU, its loadout picks break; nothing is lost or copied). Once Requip 0.2 has run, the SkyyGear rollback FLOOR is 0.2.23
(record it next to the Wardrobe 0.2 floor when pinning).
REVIEW FIXES (fixer pass 2026-10-10): (a) the craft re-checks its reserved slot AFTER sacks:fn:craftPay (SkyySacks' giveSurplus may put
surplus materials into that very slot) and picks another / goes to Requip / refunds - never writes over a stack; (b) have / need is
cached per recipe inside one page build (cards + piece rows) and the Craft tab's navigation clicks are coalesced (NAV_MS 150 ms); the
Reforge / Upgrade lists' Requip rows are re-read at most once a second per page (RQ_MS) and right after a fetch / Return to Requip;
(c) a greyed piece row's button names the short reason and a gold line above the rows gives the full one (the accessory sentence);
(d) more than 4 materials: the 4th line lists every remaining material (have / need) instead of "+N more".
FIXER 2 (2026-10-10): (e) crafting into Requip uses wardrobe:fn:deposit WITH evidence every time (no more item-in-a-slot + depositSlot:
that journal step carries no evidence, so an engine rollback after a crash would have brought the materials back AND kept the pooled
item). The evidence is MEASURED (GearSmith.paidEvidence): the ids whose counts the payment lowered, before-counts read the way SkyyWardrobe
0.2's matsBack reads them (Hotbar + Storage + Backpack + Armor; bags = sacks:fn:count), so resource-type inputs ("Any wood") are covered;
the inventory part only when the inventory paid anything, else the bag part; nothing measured = no Requip for that craft (inventory,
CRAFT-NOPROOF). A Requip refusal falls back to a free inventory slot (it may have opened up during the pay), else refund. (f) Re-identify
carries the item's foreign keys (GearData.carry) - the SkyyRequip stamp survives. (g) Refresh drops the shared recipe cache at most once
per 5 s for the whole server (GearSmith.forceRecipes).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.22.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.23.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.22"' in s and s.startswith('"""SkyyGear 0.2.22 - build script'), "build_skyygear_0.2.22.py is not the live 0.2.22"
assert "GearSmith" not in s and "SmithPage" not in s and "SMITH_ON" not in s, "0.2.22 already has the 0.2.23 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.22 - build script (javassist via jpype). GENERATED by tools/gear_0_2_22_patch.py from the LIVE 0.2.21 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.22.py -> SkyyGear/SkyyGear-0.2.22.jar (never --deploy).

''', '''"""SkyyGear 0.2.23 - build script (javassist via jpype). GENERATED by tools/gear_0_2_23_patch.py from the LIVE 0.2.22 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.23.py -> SkyyGear/SkyyGear-0.2.23.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.23 = "):].strip() + '''

0.2.22 (the base, everything below is still true unless 0.2.23 above says otherwise):
''')
rep('VERSION = "0.2.22"', 'VERSION = "0.2.23"')

# ================================================================================================================ 1. config rows
rep('''            ("upgrade", "Upgrades")]             # 0.2.22''', '''            ("upgrade", "Upgrades"),             # 0.2.22
            ("smithing", "Smithing")]            # 0.2.23
# 0.2.23: the class -> armor type table of the Smithing class filter (LOCKED armor types 2026-10-05)
SMITH_ARM_DEF = "Warrior:Heavy,Berserker:Heavy,Archer:Light,Assassin:Light,Monk:Light,Mage:Cloth,Priest:Cloth"
assert len(SMITH_ARM_DEF) < 500 and all(32 <= ord(_c) < 127 for _c in SMITH_ARM_DEF)''')
rep('''    ("view.levelInName", "Level in item names", "general", "bool", "true", "", "", "", "", "live",
     "Item names end with their level, e.g. Copper Pickaxe [Lv 12] (bags: [Lv 5-9]).", "field:GearCfg.NAME_LV"),''',
    '''    ("view.levelInName", "Level in item names", "general", "bool", "true", "", "", "", "", "live",
     "Item names end with their level, e.g. Copper Pickaxe [Lv 12] (bags: [Lv 5-9]).", "field:GearCfg.NAME_LV"),
    # 0.2.23 (Skyy 2026-10-10 "one command, one location"): the /smithing Craft tab + its class filter
    ("part.smithing", "Smithing Craft tab (/smithing)", "smithing", "bool", "true", "", "", "", "", "live,part,danger",
     "Craft gear from set cards on the Smithing page (bench accessory rule, like /craft).", "field:GearCfg.SMITH_ON"),
    ("smith.classArmor", "Class armor types", "smithing", "text", SMITH_ARM_DEF, "0", "500", "", "", "live",
     "Class:Heavy|Light|Cloth, joined by commas (the Craft tab's My class filter).",
     "field:GearCfg.SMITH_ARM;check=GearSmith.checkClassArmor"),''')
rep('''           "part.upgrade", "upgrade.ladders"}''',
    '''           "part.upgrade", "upgrade.ladders",
           # 0.2.23: crafting on the Smithing page (item supply = economy) - confirm in Server Setup
           "part.smithing"}''')
rep('''              ("UP_ON", "boolean", "true"), ("UP_LADDERS", "String", jstr(UP_LADDER_DEF)), ("NAME_LV", "boolean", "true")]''',
    '''              ("UP_ON", "boolean", "true"), ("UP_LADDERS", "String", jstr(UP_LADDER_DEF)), ("NAME_LV", "boolean", "true"),
              # 0.2.23 the Smithing Craft tab
              ("SMITH_ON", "boolean", "true"), ("SMITH_ARM", "String", jstr(SMITH_ARM_DEF))]''')
rep('''  NAME_LV = pbool(p, "view.levelInName", true);''',
    '''  NAME_LV = pbool(p, "view.levelInName", true);
  // 0.2.23 the Smithing Craft tab + the class filter's armor types (checked where they are read - a bad entry = that class sees all)
  SMITH_ON = pbool(p, "part.smithing", true);
  SMITH_ARM = ptext(p, "smith.classArmor", "@SMITHARM@").trim();''')
rep('''.replace("@UPLADDEF@", UP_LADDER_DEF))''', '''.replace("@UPLADDEF@", UP_LADDER_DEF).replace("@SMITHARM@", SMITH_ARM_DEF))''')
rep('''UG_ROWK = ["part.upgrade", "upgrade.ladders", "view.levelInName"]''', '''UG_ROWK = ["part.upgrade", "upgrade.ladders", "view.levelInName"]
# 0.2.23: the Smithing rows of a fresh file (an existing file gets each the first time it is changed in Server Setup)
SMH_HEAD = "# ---- smithing hub (/smithing Craft tab) + its class filter (SkyyGear 0.2.23) ----"
SMH_ROWK = ["part.smithing", "smith.classArmor"]
assert all(32 <= ord(_c) < 127 for _c in SMH_HEAD) and "=" not in SMH_HEAD''')
rep('''    L += ["", UG_HEAD]         # 0.2.22: the upgrade + name rows (no one-time update adds them; absent = the default)
    for k in UG_ROWK:
        scal(k)
''', '''    L += ["", UG_HEAD]         # 0.2.22: the upgrade + name rows (no one-time update adds them; absent = the default)
    for k in UG_ROWK:
        scal(k)
    L += ["", SMH_HEAD]         # 0.2.23: the smithing rows (no one-time update adds them; absent = the default)
    for k in SMH_ROWK:
        scal(k)
''')
rep('''assert _DL[_DL.index(UG_HEAD) - 2] == "tool.fortune.cap=%s" % dict((r[0], r[4]) for r in CFG_ROWS)["tool.fortune.cap"], "the 0.2.22 block follows the 0.2.12 rows"''',
    '''assert _DL[_DL.index(UG_HEAD) - 2] == "tool.fortune.cap=%s" % dict((r[0], r[4]) for r in CFG_ROWS)["tool.fortune.cap"], "the 0.2.22 block follows the 0.2.12 rows"
# 0.2.23: the block once, right after the 0.2.22 block; the rows read back
assert DEFAULT_TEXT.count(SMH_HEAD) == 1 and _dp.get("part.smithing") == "true" and _dp.get("smith.classArmor") == SMITH_ARM_DEF
assert _DL[_DL.index(SMH_HEAD) - 2] == "view.levelInName=true", "the 0.2.23 block follows the 0.2.22 rows"''')

# ================================================================================================================ 2. the tab row: Craft first
rep(r'''# 0.2.22 the tab row: 0 Reforge, 1 Upgrade (part.upgrade on), 2 Multitool (multiTab); EventData a = "mode:<n>"; returns how many tabs show
M(gui, r"""
public static int tabs(@UCB@ b, @UEB@ ev, String parent, int sel, int w, String title) {
  boolean up = @PKG@.GearCfg.UP_ON;
  boolean mt = multiTab();
  int n = 1 + (up ? 1 : 0) + (mt ? 1 : 0);''', r'''# 0.2.22 the tab row: 0 Reforge, 1 Upgrade (part.upgrade on), 2 Multitool (multiTab); EventData a = "mode:<n>"; returns how many tabs show
# 0.2.23: + 3 Craft (part.smithing on), shown FIRST: Craft | Reforge | Upgrade | Multitool
M(gui, r"""
public static int tabs(@UCB@ b, @UEB@ ev, String parent, int sel, int w, String title) {
  boolean cr = @PKG@.GearCfg.SMITH_ON;
  boolean up = @PKG@.GearCfg.UP_ON;
  boolean mt = multiTab();
  int n = 1 + (cr ? 1 : 0) + (up ? 1 : 0) + (mt ? 1 : 0);''')
rep(r'''  int tw = (w - 5 * (n - 1)) / n;
  int k = 0;
  for (int m = 0; m < 3; m++) {
    if (m == 1 && !up) continue;
    if (m == 2 && !mt) continue;
    if (k > 0) b.appendInline("#SkyyGTabs", "Group { Anchor: (Width: 5); }");
    String nm = m == 0 ? "Reforge" : (m == 1 ? "Upgrade" : "Multitool");''', r'''  int tw = (w - 5 * (n - 1)) / n;
  int k = 0;
  int[] order = new int[] { 3, 0, 1, 2 };
  for (int j = 0; j < order.length; j++) {
    int m = order[j];
    if (m == 3 && !cr) continue;
    if (m == 1 && !up) continue;
    if (m == 2 && !mt) continue;
    if (k > 0) b.appendInline("#SkyyGTabs", "Group { Anchor: (Width: 5); }");
    String nm = m == 3 ? "Craft" : (m == 0 ? "Reforge" : (m == 1 ? "Upgrade" : "Multitool"));''')
# one page title for every tab (spec 4.1: "Title Smithing")
rep('''  @PKG@.GearUi.frame(b, "Reforge", 1100, 880);
  b.appendInline("#SkyyGBody", "Label #SkyyGSub { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Pick a weapon, armor piece or tool.''', '''  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  b.appendInline("#SkyyGBody", "Label #SkyyGSub { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Pick a weapon, armor piece or tool.''')
rep('''  @PKG@.GearUi.frame(b, "Reforge", 1100, 880);
  b.appendInline("#SkyyGBody", "Label #SkyyGSub { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Upgrade: pick an item''', '''  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  b.appendInline("#SkyyGBody", "Label #SkyyGSub { Anchor: (Height: 28); Text: \\"\\"; Style: (FontSize: 16, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGSub.Text", "Upgrade: pick an item''')
rep('''  @PKG@.GearUi.frame(b, "Multitool", 1100, 880);''', '''  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);''')

# ================================================================================================================ 3. F1: carry foreign keys
rep('''gmerge = mk("GearMerge")
mpg = mk("MultiPage", PAGE)
mtc = mk("MultiCmd", APC)''', r'''# 0.2.23 F1 (research/Requip-Smithing-Spec.md section 1): a NEW stack made from an old one (upgrade, merge) keeps every metadata key that is
# not SkyyGear's own - SkyyWardrobe 0.2's SkyyRequip stamp, any other mod's data. Ours: SkyyGear, SkyyGearView, SkyyRolls(+View), SkyyUnid and
# the item display (GearData.put writes a fresh one). The fresh stack's own keys win.
M(gdt, r"""
public static @IS@ carry(@IS@ fresh, @IS@ src) {
  if (fresh == null || src == null || src.isEmpty()) return fresh;
  @BD@ md = src.getMetadata();
  if (md == null || md.isEmpty()) return fresh;
  @BD@ c = (@BD@) md.clone();
  c.remove(@PKG@.GearDefs.DOC_KEY);
  c.remove(@PKG@.GearDefs.VIEW_KEY);
  c.remove(@PKG@.GearDefs.ROLLS_KEY);
  c.remove(@PKG@.GearDefs.ROLLS_VIEW);
  c.remove(@PKG@.GearUnid.KEY);
  c.remove(@IDM@.KEY);
  if (c.isEmpty()) return fresh;
  @BD@ f = fresh.getMetadata();
  if (f != null) {
    java.util.Iterator it = f.keySet().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      c.put(k, f.get(k));
    }
  }
  return fresh.withMetadata(c);
}""")
# the Requip stamp key (requip:stampKey, default SkyyRequip) and the entry id a stack carries in it (null = none)
M(gdt, r"""
public static String stampKey() {
  Object k = @PKG@.Gear.bget("requip:stampKey");
  return k instanceof String && ((String) k).length() > 0 ? (String) k : "SkyyRequip";
}""")
M(gdt, r"""
public static String eidOf(@IS@ s) {
  try {
    if (s == null || s.isEmpty()) return null;
    @BD@ md = s.getMetadata();
    @BV@ v = md == null ? null : md.get(stampKey());
    if (v == null || !v.isDocument()) return null;
    @BV@ e = v.asDocument().get("e");
    if (e == null || !e.isString()) return null;
    String x = e.asString().getValue();
    return x.length() == 0 ? null : x;
  } catch (Throwable t) { return null; }
}""")
gmerge = mk("GearMerge")
mpg = mk("MultiPage", PAGE)
mtc = mk("MultiCmd", APC)''')
rep('''    ms = @PKG@.GearData.put(new @IS@(mid, 1), nd, u);''', '''    ms = @PKG@.GearData.put(@PKG@.GearData.carry(new @IS@(mid, 1), p), nd, u);          // 0.2.23 F1: the pickaxe's other keys''')
# the hatchet's Requip entry is used up (it went into the multitool)
rep(r'''# THE WRITE (header 4). Object[] { Integer code (1 made, 0 refused - nothing moved, -1 failed - see the message), String message, IS the
# multitool, BD its document }''', r'''# 0.2.23 F1: a merged-away hatchet that came from Requip is reported used up (wardrobe:fn:gone; no SkyyWardrobe = nothing)
M(gmerge, r"""
public static void rqGone(@IS@ h, java.util.UUID u, String who) {
  String e = @PKG@.GearData.eidOf(h);
  if (e == null || u == null) return;
  java.util.function.Function f = @PKG@.Gear.fn("wardrobe:fn:gone");
  if (f == null) return;
  Object r = null;
  try { r = f.apply(new Object[] { u, e, "merged" }); } catch (Throwable t) { r = null; @PKG@.Gear.warnOnce("rqgone", "wardrobe:fn:gone failed: " + t); }
  @PKG@.GearLog.line("MERGE-REQUIP-GONE " + who + " " + u + " " + e + " -> " + r);
}""")
# THE WRITE (header 4). Object[] { Integer code (1 made, 0 refused - nothing moved, -1 failed - see the message), String message, IS the
# multitool, BD its document }''')
rep('''  try { after(all, pid, hid, mid, bp, bh, bm, who, u, nd, info, ps, pslot); } catch (Throwable xa) { }
  return new Object[] { Integer.valueOf(1), "Made!", ms, nd };''', '''  try { after(all, pid, hid, mid, bp, bh, bm, who, u, nd, info, ps, pslot); } catch (Throwable xa) { }
  try { rqGone(h, u, who); } catch (Throwable xg) { }          // 0.2.23 F1
  return new Object[] { Integer.valueOf(1), "Made!", ms, nd };''')
rep('''    ns = @PKG@.GearData.put(new @IS@(to, 1), nd, u);''', '''    ns = @PKG@.GearData.put(@PKG@.GearData.carry(new @IS@(to, 1), it), nd, u);          // 0.2.23 F1: the item's other keys''')
# 0.2.23 FIXER 2 (critic 2 finding 2): RE-IDENTIFY builds a new stack too (GearUnid.reroll -> GearData.put(new IS)) - carry the item's
# other keys (the SkyyRequip stamp: the same Requip entry survives; F2 holds for re-identify as well). First identify of a bag needs none:
# Requip refuses unidentified bags.
rep('''    got = @PKG@.GearUnid.reroll(d, u, id, @PKG@.GearLoot.lean(u));          // fix round (ut02 review): Untiered -> another Untiered item
    if (got == null) throw new IllegalStateException("no item fits any more");
    tx = c.setItemStackForSlot((short) slot, (@IS@) got[3]);''', '''    got = @PKG@.GearUnid.reroll(d, u, id, @PKG@.GearLoot.lean(u));          // fix round (ut02 review): Untiered -> another Untiered item
    if (got == null) throw new IllegalStateException("no item fits any more");
    got[3] = @PKG@.GearData.carry((@IS@) got[3], it);          // 0.2.23 FIXER 2: the SkyyRequip stamp (any foreign key) survives a re-identify
    tx = c.setItemStackForSlot((short) slot, (@IS@) got[3]);''')

# ================================================================================================================ 4. upgrade materials from the bags
rep(r'''# the first material that is short, in words (null = enough of everything)
M(gup, r"""''', r'''# 0.2.23: what the Magic Bags hold of id (sacks:fn:count; -1 / missing = 0)
M(gup, r"""
public static int bagHave(java.util.UUID u, String id) {
  if (u == null || id == null) return 0;
  java.util.function.Function f = @PKG@.Gear.fn("sacks:fn:count");
  if (f == null) return 0;
  try {
    Object r = f.apply(new Object[] { u, id });
    if (r instanceof Number) {
      long v = ((Number) r).longValue();
      if (v <= 0L) return 0;
      return v > 1000000L ? 1000000 : (int) v;
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("bagcount", "sacks:fn:count failed: " + t); }
  return 0;
}""")
# 0.2.23: put bag takes back (got[k] of mids[k]); returns what could NOT go back ("" = all)
M(gup, r"""
public static String bagBack(java.util.UUID u, String[] mids, long[] got) {
  StringBuilder bad = new StringBuilder();
  java.util.function.Function f = null;
  for (int k = 0; k < mids.length; k++) {
    if (got[k] <= 0L) continue;
    if (f == null) f = @PKG@.Gear.fn("sacks:fn:put");
    long back = 0L;
    try { Object r = f == null ? null : f.apply(new Object[] { u, mids[k], Long.valueOf(got[k]) }); if (r instanceof Number) back = ((Number) r).longValue(); } catch (Throwable t) { back = 0L; }
    if (back < got[k]) {
      if (bad.length() > 0) bad.append(", ");
      bad.append(mids[k]).append(" x").append(got[k] - back).append(" @bags");
    }
  }
  return bad.toString();
}""")
M(gup, r"""
public static void bagCommit(java.util.UUID u, String[] mids, long[] got) {
  java.util.function.Function f = null;
  for (int k = 0; k < mids.length; k++) {
    if (got[k] <= 0L) continue;
    if (f == null) f = @PKG@.Gear.fn("sacks:fn:commit");
    try { if (f != null) f.apply(new Object[] { u, mids[k], Long.valueOf(got[k]) }); } catch (Throwable t) { @PKG@.Gear.warnOnce("bagcommit", "sacks:fn:commit failed: " + t); }
  }
}""")
# 0.2.23: the first material that is short counting the inventory AND the bags (null = enough of everything)
M(gup, r"""
public static String shortOfU(@INV@ inv, java.util.UUID u, Object[] c) {
  if (c == null) return "No recipe for this upgrade.";
  String[] ids = (String[]) c[0];
  int[] q = (int[]) c[1];
  for (int i = 0; i < ids.length; i++) {
    int h = have(inv, ids[i]) + bagHave(u, ids[i]);
    if (h < q[i]) return "You need " + (q[i] - h) + " more " + @PKG@.Gear.itemName(ids[i]) + " (you have " + h + " of " + q[i] + ", inventory + bags).";
  }
  return null;
}""")
# the first material that is short, in words (null = enough of everything)
M(gup, r"""''')
rep('''  String sh = shortOf(inv, cost);
  if (sh != null) return new Object[] { Integer.valueOf(0), sh, null, null };''', '''  String sh = shortOfU(inv, u, cost);          // 0.2.23: inventory + bags
  if (sh != null) return new Object[] { Integer.valueOf(0), sh, null, null };''')
rep('''  java.util.ArrayList plan = new java.util.ArrayList();
  StringBuilder pt = new StringBuilder();
  for (int k = 0; k < mids.length; k++) {''', '''  java.util.ArrayList plan = new java.util.ArrayList();
  StringBuilder pt = new StringBuilder();
  int[] bagNeed = new int[mids.length];          // 0.2.23: the part the inventory lacks comes from the Magic Bags
  for (int k = 0; k < mids.length; k++) {''')
rep('''    if (left > 0) return new Object[] { Integer.valueOf(0), "You need " + left + " more " + @PKG@.Gear.itemName(mids[k]) + ".", null, null };
  }''', '''    if (left > 0) {
      if (bagHave(u, mids[k]) < left) return new Object[] { Integer.valueOf(0), "You need " + left + " more " + @PKG@.Gear.itemName(mids[k]) + ".", null, null };
      bagNeed[k] = left;
      if (pt.length() > 0) pt.append(", ");
      pt.append(mids[k]).append(" x").append(left).append(" @bags");
    }
  }
  int[] mqInv = new int[mids.length];
  for (int k = 0; k < mids.length; k++) mqInv[k] = mq[k] - bagNeed[k];''')
rep('''  if (CRASH_AT == 1) throw new IllegalStateException("harness: a crash right after the materials left");''',
    '''  // 0.2.23: the bag part, after the inventory part left (a refusal = everything back, nothing used)
  long[] bagGot = new long[mids.length];
  String whyB = null;
  java.util.function.Function tk = null;
  for (int k = 0; k < mids.length && whyB == null; k++) {
    if (bagNeed[k] <= 0) continue;
    if (tk == null) tk = @PKG@.Gear.fn("sacks:fn:take");
    long g = 0L;
    try { Object r = tk == null ? null : tk.apply(new Object[] { u, mids[k], Long.valueOf((long) bagNeed[k]) }); if (r instanceof Number) g = ((Number) r).longValue(); } catch (Throwable xt) { g = 0L; }
    bagGot[k] = g < 0L ? 0L : g;
    if (bagGot[k] < (long) bagNeed[k]) whyB = "the bags gave " + bagGot[k] + " of " + bagNeed[k] + " " + mids[k];
  }
  if (whyB != null) {
    String bb = bagBack(u, mids, bagGot);
    String rb0 = restore(plan, plan.size(), secs);
    if (bb.length() > 0 || rb0.length() > 0) {
      @PKG@.Gear.warn("UPGRADE: the materials of " + who + " (" + u + ") could not all be put back - they are in gear.log (UPGRADE-RESTORE-FAILED)");
      @PKG@.GearLog.line("UPGRADE-RESTORE-FAILED " + who + " " + u + " materials not back: " + rb0 + (bb.length() > 0 ? " " + bb : "") + " (" + whyB + ")");
      return new Object[] { Integer.valueOf(-1), "Something went wrong and some materials could not be put back - an admin can find them in the server log.", null, null };
    }
    @PKG@.GearLog.line("UPGRADE-FAILED " + who + " " + u + " (" + whyB + ") - RESTORED, nothing used");
    return new Object[] { Integer.valueOf(-1), "Your bags could not give the rest of the materials - nothing was used.", null, null };
  }
  if (CRASH_AT == 1) throw new IllegalStateException("harness: a crash right after the materials left");''')
rep('''    String rb2 = restore(plan, plan.size(), secs);
    if (!kept || rb2.length() > 0) {''', '''    String rb2 = restore(plan, plan.size(), secs);
    String bb2 = bagBack(u, mids, bagGot);          // 0.2.23
    if (bb2.length() > 0) rb2 = rb2 + (rb2.length() > 0 ? ", " : "") + bb2;
    if (!kept || rb2.length() > 0) {''')
rep('''  try { after(all, id, to, mids, mq, bf, bt, bm, who, u, nd, info, s, slot); } catch (Throwable xa) { }
  return new Object[] { Integer.valueOf(1), "Upgraded!", ns, nd };''', '''  try { bagCommit(u, mids, bagGot); } catch (Throwable xc) { }          // 0.2.23: the bag part is final
  try { after(all, id, to, mids, mqInv, bf, bt, bm, who, u, nd, info, s, slot); } catch (Throwable xa) { }
  return new Object[] { Integer.valueOf(1), "Upgraded!", ns, nd };''')
rep('''    int h = @PKG@.GearUp.have(inv, ids[i]);''', '''    int h = @PKG@.GearUp.have(inv, ids[i]) + @PKG@.GearUp.bagHave(this.playerRef.getUuid(), ids[i]);          // 0.2.23: + bags''')
rep('''"Materials - have / need (inventory, backpack, hotbar)"''', '''"Materials - have / need (inventory, then bags)"''')
rep('''    if (why == null) why = @PKG@.GearUp.shortOf(inv, cost);''', '''    if (why == null) why = @PKG@.GearUp.shortOfU(inv, u, cost);          // 0.2.23: + bags''')

# ================================================================================================================ 5. GearSmith + SmithPage + SmithCmd + SmithFn
SMITH_PY = r'''# ####################################################################################################################################
# 0.2.23 THE /smithing HUB (tools/gear_0_2_23_patch.py header): GearSmith (recipes, cards, class filter, the craft transaction), SmithPage
# (the Craft tab), SmithCmd (/smithing, /smith), SmithFn (gear:fn:smithing + gear:fn:classShow); the Reforge page's Requip rows + tab hook
# (ReforgePage.rq*, hooked AFTER list / upList and in front of handleDataEvent) and the /multitool page's Craft tab. Placed after /upgrade:
# it calls GearUp, GearMerge, GearForge, GearStamp, GearRoll, GearLevel, GearView, GearUi, GearBase, GearMine, GearSet and ReforgePage.
# ####################################################################################################################################
BRQ = "com.hypixel.hytale.protocol.BenchRequirement"
BTP = "com.hypixel.hytale.protocol.BenchType"
ISS = "com.hypixel.hytale.server.core.asset.type.itemsound.config.ItemSoundSet"
T.update({"BRQ": BRQ, "BTP": BTP, "ISS": ISS})
for _c, _m in ((CRR, "getBenchRequirement"), (CRR, "getInput"), (CRR, "getPrimaryOutput"), (CRR, "getId"), (CRR, "getAssetMap"),
               (MQ, "getItemId"), (MQ, "getQuantity"), (MQ, "getResourceTypeId"), (ITM, "getItemSoundSetIndex"), (ISS, "getAssetMap"),
               (ISS, "getId"), ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset"), (AC, "addAliases"),
               (IC, "setItemStackForSlot"), (IC, "removeItemStackFromSlot"), (IC, "getItemStack"), (UNI, "getPlayer"), (CMGR, "handleCommand")):
    B.probe(pool, _c, _m)
for _f in ("id", "type", "requiredTierLevel"):
    assert pool.get(BRQ).getField(_f) is not None
for _f in ("Crafting", "Processing"):
    assert pool.get(BTP).getField(_f) is not None
gsm = mk("GearSmith")
spg = mk("SmithPage", PAGE)
smc = mk("SmithCmd", APC)
sfn = mk("SmithFn")
SMITH_CLASSES = [gsm, spg, smc, sfn]
F(gsm, 'public static final String[] SLOT = new String[] { "Head", "Chest", "Hands", "Legs" };')
F(gsm, 'public static final String[] T_NAME = new String[] { "-", "Heavy", "Light", "Cloth" };')
F(gsm, 'public static final String[] CAT_NAME = new String[] { "Combat armor", "Gathering armor", "Weapons", "Tools", "Multitools" };')
F(gsm, 'public static final String[] ROMAN = new String[] { "", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX" };')
F(gsm, 'public static final String[] SEC = new String[] { "hotbar", "storage", "backpack", "armor", "utility", "tools" };')
F(gsm, "public static volatile Object[] REC = null;")             # { Integer store size, Long cfg epoch, ArrayList rows Object[] { rid, out, CRR } }
F(gsm, "public static final java.util.concurrent.ConcurrentHashMap PREF = new java.util.concurrent.ConcurrentHashMap();")   # "uuid|key" -> Boolean
F(gsm, "public static final java.util.concurrent.ConcurrentHashMap LAST = new java.util.concurrent.ConcurrentHashMap();")   # uuid -> Long last craft
F(gsm, "public static volatile int CRASH_AT = 0;")                 # harness only: 1 = throw right after the materials were paid (a crash)
F(gsm, "public static final long GAP_MS = 1000L;")
F(gsm, "public static volatile long NAV_MS = 150L;")       # review fix: Craft tab navigation clicks closer than this are dropped (harness may set 0)
F(gsm, "public static volatile long RQ_MS = 1000L;")       # review fix: the Requip rows of a Reforge / Upgrade page are re-read at most this often
M(gsm, r"""
public static String last(String id) {
  if (id == null) return "";
  int i = id.lastIndexOf('_');
  return i < 0 ? "" : id.substring(i + 1);
}""")
# the armor slot of an id by its last word: 0 Head, 1 Chest, 2 Hands, 3 Legs, -1 none
M(gsm, r"""
public static int slotIx(String id) {
  String w = last(id);
  for (int i = 0; i < SLOT.length; i++) if (SLOT[i].equals(w)) return i;
  return -1;
}""")
M(gsm, r"""
public static String setKey(String id) {
  int s = slotIx(id);
  if (s < 0) return id;
  return id.substring(0, id.length() - SLOT[s].length() - 1);
}""")
# a weapon / tool family: Weapon_<Kind> (Weapon_Fist_<Kind>), the tool family prefix, "Multitool"
M(gsm, r"""
public static String famKey(String id) {
  if (id == null) return "";
  if (@PKG@.GearData.multiId(id)) return "Multitool";
  if (id.startsWith("Tool_")) {
    for (int i = 0; i < @PKG@.GearDefs.T_FAM.length; i++) if (id.startsWith(@PKG@.GearDefs.T_FAM[i])) return @PKG@.GearDefs.T_FAM[i];
  }
  String[] p = id.split("_");
  if (p.length > 2 && p[1].equals("Fist")) return p[0] + "_" + p[1] + "_" + p[2];
  if (p.length > 1) return p[0] + "_" + p[1];
  return id;
}""")
# 0 combat armor, 1 gathering armor, 2 weapons, 3 tools, 4 multitools, -1 not on the page
M(gsm, r"""
public static int cat(String id) {
  if (id == null) return -1;
  if (@PKG@.GearData.multiId(id)) return 4;
  int s = @PKG@.GearData.slotOf(id);
  if (s == 2) return (@PKG@.GearMine.isPiece(id) || @PKG@.GearMine.setFor(id) != null) ? 1 : 0;
  if (s == 0 || s == 1) return 2;
  if (s == 3) return 3;
  return -1;
}""")
# the armor type of a piece by its vanilla sound set (the 0.2.11 bag rule): 3 Cloth, 2 Light (Leather), 1 Heavy
M(gsm, r"""
public static int armorType(String id) {
  try {
    @ITM@ it = @PKG@.Gear.item(id);
    if (it == null) return 1;
    Object o = @ISS@.getAssetMap().getAsset(it.getItemSoundSetIndex());
    String n = o instanceof @ISS@ ? String.valueOf(((@ISS@) o).getId()) : "";
    if (n.indexOf("Cloth") >= 0) return 3;
    if (n.indexOf("Leather") >= 0) return 2;
  } catch (Throwable t) { }
  return 1;
}""")
M(gsm, r"""
public static int typeIx(String t) {
  if (t == null) return -1;
  for (int k = 1; k < T_NAME.length; k++) if (T_NAME[k].equalsIgnoreCase(t.trim())) return k;
  return -1;
}""")
# the player's enabled class (class:<uuid>, listed in class:list), null = none
M(gsm, r"""
public static String classOf(java.util.UUID u) {
  try {
    if (u == null) return null;
    Object c = @PKG@.Gear.bget("class:" + u);
    if (!(c instanceof String) || ((String) c).trim().length() == 0) return null;
    String cn = ((String) c).trim();
    Object list = @PKG@.Gear.bget("class:list");
    if (list instanceof String && ("," + ((String) list).replace(" ", "") + ",").indexOf("," + cn + ":") < 0) return null;
    return cn;
  } catch (Throwable t) { return null; }
}""")
# smith.classArmor: the armor type of a class (1-3), 0 = not listed (= every type)
M(gsm, r"""
public static int armorFor(String cls) {
  if (cls == null) return 0;
  String s = @PKG@.GearCfg.SMITH_ARM;
  if (s == null) return 0;
  String[] es = s.split(",");
  for (int i = 0; i < es.length; i++) {
    String e = es[i].trim();
    int c = e.indexOf(':');
    if (c <= 0 || !e.substring(0, c).trim().equalsIgnoreCase(cls)) continue;
    int t = typeIx(e.substring(c + 1));
    return t < 1 ? 0 : t;
  }
  return 0;
}""")
# Server Setup check of smith.classArmor
M(gsm, r"""
public static String checkClassArmor(String key, String value) {
  if (value == null) return null;
  String[] es = value.split(",");
  for (int i = 0; i < es.length; i++) {
    String e = es[i].trim();
    if (e.length() == 0) continue;
    int c = e.indexOf(':');
    if (c <= 0) return "Write Class:Heavy|Light|Cloth joined by commas, e.g. Warrior:Heavy,Mage:Cloth.";
    String n = e.substring(0, c).trim();
    for (int k = 0; k < n.length(); k++) if (!Character.isLetterOrDigit(n.charAt(k))) return "'" + n + "' is not a class name (letters and digits).";
    if (typeIx(e.substring(c + 1)) < 1) return "'" + e + "': the armor type must be Heavy, Light or Cloth.";
  }
  return null;
}""")
# THE CLASS FILTER (header 6). all = Show all / no filter
M(gsm, r"""
public static boolean shows(java.util.UUID u, String id, boolean all) {
  if (all || id == null) return true;
  String cls = classOf(u);
  if (cls == null) return true;
  int c = cat(id);
  if (c == 0) {
    int t = armorFor(cls);
    return t <= 0 || armorType(id) == t;
  }
  if (c == 2) {
    Object mine = @PKG@.Gear.bget("class:weapons:" + cls);
    Object free = @PKG@.Gear.bget("class:weapons:free");
    if (!(mine instanceof String) && !(free instanceof String)) return true;
    int m = @PKG@.GearView.prefixLen(mine, id);
    int f = @PKG@.GearView.prefixLen(free, id);
    if (m <= 0 && f <= 0) return false;
    // the longest matching prefix wins (GearView.classReq's rule): Weapon_Staff_Bo_ is the Monk's, not the Mage's Weapon_Staff_
    int o = 0;
    Object list = @PKG@.Gear.bget("class:list");
    if (list instanceof String) {
      String[] es = ((String) list).split(",");
      for (int i = 0; i < es.length; i++) {
        String e = es[i].trim();
        int k = e.indexOf(':');
        String nm = k >= 0 ? e.substring(0, k).trim() : e;
        if (nm.length() == 0 || nm.equalsIgnoreCase(cls)) continue;
        int n = @PKG@.GearView.prefixLen(@PKG@.Gear.bget("class:weapons:" + nm), id);
        if (n > o) o = n;
      }
    }
    return (m > 0 && m >= o) || (f > 0 && f >= o);
  }
  return true;
}""")
# the player switches (SkyyMenu settings; memory only without it)
M(gsm, r"""
public static boolean pref(java.util.UUID u, String key, boolean def) {
  if (u == null) return def;
  try {
    java.util.function.Function f = @PKG@.Gear.fn("settings:fn:get");
    if (f != null) {
      Object r = f.apply(new Object[] { u, key });
      if (r instanceof Boolean) return ((Boolean) r).booleanValue();
    }
  } catch (Throwable t) { }
  Object m = PREF.get(u + "|" + key);
  if (m instanceof Boolean) return ((Boolean) m).booleanValue();
  return def;
}""")
M(gsm, r"""
public static void setPref(java.util.UUID u, String key, boolean v) {
  if (u == null) return;
  PREF.put(u + "|" + key, Boolean.valueOf(v));
  try {
    java.util.function.Function f = @PKG@.Gear.fn("settings:fn:set");
    if (f != null) f.apply(new Object[] { u, key, Boolean.valueOf(v) });
  } catch (Throwable t) { }
}""")
M(gsm, 'public static boolean showAll(java.util.UUID u) { return pref(u, "gear.smithShowAll", false); }')
M(gsm, 'public static boolean toRequip(java.util.UUID u) { return pref(u, "gear.smithToRequip", true); }')
M(gsm, r"""
public static boolean retired(String b) {
  return b != null && (b.equalsIgnoreCase("Alchemybench") || b.equalsIgnoreCase("Cookingbench") || b.equalsIgnoreCase("Campfire"));
}""")
M(gsm, r"""
public static boolean anyAcc() {
  return @PKG@.Gear.item("Skyy_Accessory_Workbench_T1") != null || @PKG@.Gear.item("Skyy_Accessory_Omni") != null || @PKG@.Gear.item("Skyy_Accessory_Bag") != null;
}""")
M(gsm, r"""
public static boolean accExists(String bench) {
  if (bench == null) return false;
  if (bench.equalsIgnoreCase("Fieldcraft")) return true;
  if (!anyAcc()) return true;
  return @PKG@.Gear.item("Skyy_Accessory_" + bench + "_T1") != null || @PKG@.Gear.item("Skyy_Accessory_" + bench) != null;
}""")
# a recipe shown on the Craft tab (header 3)
M(gsm, r"""
public static boolean usable(@CRR@ rc) {
  if (rc == null) return false;
  @MQ@ po = rc.getPrimaryOutput();
  if (po == null || po.getItemId() == null || po.getQuantity() != 1) return false;
  String out = po.getItemId();
  if (!@PKG@.GearRoll.craftable(out) || cat(out) < 0 || @PKG@.GearUtFx.mythicId(out)) return false;
  @MQ@[] in = rc.getInput();
  if (in == null || in.length == 0) return false;
  for (int i = 0; i < in.length; i++) {
    if (in[i] == null) continue;
    String iid = in[i].getItemId();
    if (iid != null && @PKG@.GearData.isGear(iid)) return false;
  }
  @BRQ@[] br = rc.getBenchRequirement();
  if (br == null) return false;
  boolean ok = false;
  for (int i = 0; i < br.length; i++) {
    if (br[i] == null || br[i].id == null || br[i].type != @BTP@.Crafting || retired(br[i].id)) continue;
    if (accExists(br[i].id)) ok = true;
  }
  return ok;
}""")
# every shown recipe, one per output (the lowest recipe id): ArrayList of Object[] { String rid, String out, CRR } (cached per store size + config)
M(gsm, r"""
public static java.util.ArrayList recipes() {
  java.util.Map m = null;
  int ni = 0;
  try { m = @CRR@.getAssetMap().getAssetMap(); ni = @ITM@.getAssetMap().getAssetMap().size(); } catch (Throwable t) { m = null; }
  if (m == null) return new java.util.ArrayList();
  int n = m.size() * 31 + ni;          // the recipe AND item store sizes (an item pack loaded later changes what is gear)
  long ep = @PKG@.GearCfg.cfgEpoch();
  Object[] c = REC;
  if (c != null && ((Integer) c[0]).intValue() == n && ((Long) c[1]).longValue() == ep) return (java.util.ArrayList) c[2];
  java.util.TreeMap by = new java.util.TreeMap();
  try {
    java.util.Iterator it = new java.util.ArrayList(m.values()).iterator();
    while (it.hasNext()) {
      Object o = it.next();
      if (!(o instanceof @CRR@)) continue;
      @CRR@ rc = (@CRR@) o;
      if (!usable(rc)) continue;
      String out = rc.getPrimaryOutput().getItemId();
      String rid = rc.getId() == null ? "" : rc.getId();
      Object[] prev = (Object[]) by.get(out);
      if (prev == null || rid.compareTo((String) prev[0]) < 0) by.put(out, new Object[] { rid, out, rc });
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("smithrec", "Smithing: the crafting recipes could not be read: " + t); }
  java.util.ArrayList rows = new java.util.ArrayList(by.values());
  REC = new Object[] { Integer.valueOf(n), Long.valueOf(ep), rows };
  return rows;
}""")
F(gsm, "public static volatile long REC_FORCED = 0L;")          # FIXER 2: the last Refresh that dropped the recipe cache (any player)
# Refresh drops the cache at most once per 5 s for the WHOLE server (the cache already follows the store sizes + the config epoch)
M(gsm, r"""
public static boolean forceRecipes(long now) {
  long l = REC_FORCED;
  if (now >= l && now - l < 5000L) return false;
  REC_FORCED = now;
  REC = null;
  return true;
}""")
M(gsm, r"""
public static Object[] byRid(String rid) {
  if (rid == null) return null;
  java.util.ArrayList rs = recipes();
  for (int i = 0; i < rs.size(); i++) {
    Object[] r = (Object[]) rs.get(i);
    if (rid.equals(r[0])) return r;
  }
  return null;
}""")
M(gsm, r"""
public static String benchName(String b) {
  if (b == null) return "bench";
  if (b.equalsIgnoreCase("Workbench")) return "Workbench";
  String s = b.replace('_', ' ').trim();
  String lo = s.toLowerCase();
  if (lo.endsWith("bench") && s.length() > 5 && s.charAt(s.length() - 6) != ' ') s = s.substring(0, s.length() - 5) + " Bench";
  return s;
}""")
M(gsm, "public static String roman(int t) { return t >= 0 && t < ROMAN.length ? ROMAN[t] : String.valueOf(t); }")
# the bench a recipe needs: Object[] { String bench id, Integer tier } (the first Crafting bench with an accessory), null = none
M(gsm, r"""
public static Object[] bench(@CRR@ rc) {
  if (rc == null) return null;
  @BRQ@[] br = rc.getBenchRequirement();
  if (br == null) return null;
  Object[] any = null;
  for (int i = 0; i < br.length; i++) {
    if (br[i] == null || br[i].id == null || br[i].type != @BTP@.Crafting || retired(br[i].id)) continue;
    int t = br[i].requiredTierLevel;
    if (t <= 0) t = 1;
    Object[] x = new Object[] { br[i].id, Integer.valueOf(t) };
    if (accExists(br[i].id)) return x;
    if (any == null) any = x;
  }
  return any;
}""")
# why a recipe is not allowed here (the accessory rule), long (rows / chat) or short (cards)
M(gsm, r"""
public static String lockWhy(@CRR@ rc, boolean shortText) {
  Object[] b = bench(rc);
  if (b == null) return shortText ? "Locked" : "Not unlocked for you yet (a recipe you have not learned).";
  String bn = benchName((String) b[0]);
  int t = ((Integer) b[1]).intValue();
  if (((String) b[0]).equalsIgnoreCase("Fieldcraft")) return shortText ? "Locked - not learned yet" : "Not unlocked for you yet (a recipe you have not learned).";
  if (shortText) return "Locked - needs " + bn + " " + roman(t) + " accessory";
  return "Needs the " + bn + " " + roman(t) + " accessory in your Accessory Bag - or craft it at a " + bn + (t > 1 ? " (tier " + t + ")" : "") + ".";
}""")
# the recipe ids SkyySacks allows this player to craft here (sacks:fn:craftList, group "smith"); null = no bridge
M(gsm, r"""
public static java.util.HashSet allowed(java.util.UUID u) {
  java.util.function.Function f = @PKG@.Gear.fn("sacks:fn:craftList");
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(new Object[] { u, "smith" });
    java.util.HashSet s = new java.util.HashSet();
    if (r instanceof Object[]) {
      Object[] a = (Object[]) r;
      for (int i = 0; i < a.length; i++) if (a[i] instanceof String) s.add(a[i]);
    } else if (r instanceof java.util.Collection) {
      java.util.Iterator it = ((java.util.Collection) r).iterator();
      while (it.hasNext()) { Object x = it.next(); if (x instanceof String) s.add(x); }
    } else return null;
    return s;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("craftlist", "sacks:fn:craftList failed: " + t); return null; }
}""")
M(gsm, r"""
public static long lnum(Object o) {
  return o instanceof Number ? ((Number) o).longValue() : -1L;
}""")
# have / need of one recipe: Object[] { Long times, String[] ids (a resource type = "#<type>"), long[] have (-1 = unknown), long[] need }.
# From sacks:fn:craftHave (inventory + bags), else counted here (inventory only)
M(gsm, r"""
public static Object[] have(java.util.UUID u, @INV@ inv, String rid, @CRR@ rc) {
  java.util.function.Function f = @PKG@.Gear.fn("sacks:fn:craftHave");
  if (f != null && u != null) {
    try {
      Object r = f.apply(new Object[] { u, rid });
      if (r instanceof Object[] && ((Object[]) r).length >= 4 && ((Object[]) r)[1] instanceof String[] && ((Object[]) r)[2] instanceof Object[] && ((Object[]) r)[3] instanceof Object[]) {
        Object[] a = (Object[]) r;
        String[] ids0 = (String[]) a[1];
        Object[] h0 = (Object[]) a[2];
        Object[] nd0 = (Object[]) a[3];
        int n0 = ids0.length;
        if (h0.length >= n0 && nd0.length >= n0) {
          long[] hv0 = new long[n0];
          long[] ne0 = new long[n0];
          for (int i0 = 0; i0 < n0; i0++) { hv0[i0] = lnum(h0[i0]); ne0[i0] = lnum(nd0[i0]); }
          long t0 = lnum(a[0]);
          return new Object[] { Long.valueOf(t0 < 0L ? 0L : t0), ids0, hv0, ne0 };
        }
      }
    } catch (Throwable t2) { @PKG@.Gear.warnOnce("crafthave", "sacks:fn:craftHave failed: " + t2); }
  }
  if (rc == null) return new Object[] { Long.valueOf(0L), new String[0], new long[0], new long[0] };
  @MQ@[] in = rc.getInput();
  if (in == null) return new Object[] { Long.valueOf(0L), new String[0], new long[0], new long[0] };
  java.util.ArrayList ids = new java.util.ArrayList();
  java.util.ArrayList qs = new java.util.ArrayList();
  for (int i = 0; i < in.length; i++) {
    if (in[i] == null || in[i].getQuantity() < 1) continue;
    String id = in[i].getItemId();
    if (id == null) id = "#" + String.valueOf(in[i].getResourceTypeId());
    int j = ids.indexOf(id);
    if (j >= 0) qs.set(j, Long.valueOf(((Long) qs.get(j)).longValue() + (long) in[i].getQuantity()));
    else { ids.add(id); qs.add(Long.valueOf((long) in[i].getQuantity())); }
  }
  int n = ids.size();
  String[] ia = new String[n];
  long[] hv = new long[n];
  long[] ne = new long[n];
  long times = n == 0 ? 0L : Long.MAX_VALUE;
  for (int i = 0; i < n; i++) {
    ia[i] = (String) ids.get(i);
    ne[i] = ((Long) qs.get(i)).longValue();
    hv[i] = ia[i].startsWith("#") ? -1L : (long) @PKG@.GearUp.have(inv, ia[i]);
    long tt = hv[i] < 0L ? 0L : hv[i] / ne[i];
    if (tt < times) times = tt;
  }
  return new Object[] { Long.valueOf(times), ia, hv, ne };
}""")
# review fix: one have() per recipe per page build (cards + piece rows share it); c == null = uncached
M(gsm, r"""
public static Object[] haveC(java.util.HashMap c, java.util.UUID u, @INV@ inv, String rid, @CRR@ rc) {
  if (c == null || rid == null) return have(u, inv, rid, rc);
  Object o = c.get(rid);
  if (o instanceof Object[]) return (Object[]) o;
  Object[] r = have(u, inv, rid, rc);
  c.put(rid, r);
  return r;
}""")
M(gsm, r"""
public static String matName(String id) {
  if (id == null) return "?";
  if (id.startsWith("#")) return "Any " + id.substring(1).replace('_', ' ');
  if (id.startsWith("res:")) return "Any " + id.substring(4).replace('_', ' ');
  return @PKG@.Gear.itemName(id);
}""")
# the evidence a deposit journal / CRAFT-BEGIN carries (the SkyyWardrobe 0.2 shape): the material counts BEFORE the craft paid,
# {"recipe":"<rid>","inv":{"<id>":<every live stack of id>},"bags":{"<id>":<sacks:fn:count>}} - item inputs only (a resource type has no id)
M(gsm, r"""
public static String evidence(String rid, java.util.UUID u, @INV@ inv, @CRR@ rc) {
  java.util.ArrayList ids = new java.util.ArrayList();
  @MQ@[] in = null;
  if (rc != null) in = rc.getInput();
  for (int i = 0; in != null && i < in.length; i++) {
    if (in[i] == null || in[i].getItemId() == null || ids.contains(in[i].getItemId())) continue;
    ids.add(in[i].getItemId());
  }
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  StringBuilder si = new StringBuilder();
  StringBuilder sg = new StringBuilder();
  for (int i = 0; i < ids.size(); i++) {
    String id = (String) ids.get(i);
    String q = id.replace('"', '_');
    if (i > 0) { si.append(','); sg.append(','); }
    si.append('"').append(q).append("\":").append(@PKG@.GearStamp.countId(all, id));
    sg.append('"').append(q).append("\":").append(@PKG@.GearUp.bagHave(u, id));
  }
  return "{\"recipe\":\"" + (rid == null ? "" : rid.replace('"', '_')) + "\",\"inv\":{" + si.toString() + "},\"bags\":{" + sg.toString() + "}}";
}""")
# FIXER 2 (critic 2 finding 1): the evidence a craft deposit carries is what the payment ACTUALLY took, measured the way SkyyWardrobe 0.2's
# matsBack reads it back: the inventory = Hotbar + Storage + Backpack + Armor (WdInv.countId over every stack of the id), the bags =
# sacks:fn:count. The ids are found by DIFF (before / after the pay), so a resource-type input ("Any wood") is listed by the real items
# it took. Only the inventory part is listed when the inventory paid anything (matsBack is AND: listing only that part means "the engine
# rolled the inventory back" undoes the craft - a crash may lose the bag part, never copy the item); the bags only when the inventory paid
# nothing. null = nothing provable -> no Requip deposit for this craft (it goes to the inventory, where it shares the engine's save).
M(gsm, r"""
public static java.util.HashMap invCounts(@INV@ inv) {
  java.util.HashMap m = new java.util.HashMap();
  if (inv == null) return m;
  int[] secs = new int[] { 0, 1, 2, 3 };
  for (int k = 0; k < secs.length; k++) {
    @IC@ c = @PKG@.GearStamp.section(inv, secs[k]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x == null || x.isEmpty() || x.getItemId() == null) continue;
      Object o = m.get(x.getItemId());
      long v = o == null ? 0L : ((Long) o).longValue();
      m.put(x.getItemId(), Long.valueOf(v + (long) x.getQuantity()));
    }
  }
  return m;
}""")
M(gsm, r"""
public static java.util.HashMap bagAll(java.util.UUID u) {
  java.util.function.Function f = @PKG@.Gear.fn("sacks:fn:all");
  if (f == null || u == null) return null;
  try {
    Object r = f.apply(u);
    if (!(r instanceof java.util.Map)) return null;
    return new java.util.HashMap((java.util.Map) r);
  } catch (Throwable t) { return null; }
}""")
M(gsm, r"""
public static String paidEvidence(String rid, java.util.UUID u, @INV@ inv, java.util.HashMap invB, java.util.HashMap bagB) {
  if (invB == null) return null;
  java.util.HashMap invA = invCounts(inv);
  StringBuilder si = new StringBuilder();
  int ni = 0;
  java.util.Iterator it = new java.util.TreeSet(invB.keySet()).iterator();
  while (it.hasNext()) {
    String id = (String) it.next();
    long b = ((Long) invB.get(id)).longValue();
    Object ao = invA.get(id);
    long a = ao == null ? 0L : ((Long) ao).longValue();
    if (a >= b) continue;
    if (ni > 0) si.append(',');
    si.append('"').append(id.replace('"', '_')).append("\":").append(b);
    ni++;
  }
  String head = "{\"recipe\":\"" + (rid == null ? "" : rid.replace('"', '_')) + "\",\"paid\":true,\"inv\":{";
  if (ni > 0) return head + si.toString() + "},\"bags\":{}}";
  java.util.function.Function fc = @PKG@.Gear.fn("sacks:fn:count");
  java.util.HashMap bagA = bagAll(u);
  if (bagB == null || bagA == null || fc == null) return null;
  StringBuilder sb = new StringBuilder();
  int nb = 0;
  java.util.Iterator ib = new java.util.TreeSet(bagB.keySet()).iterator();
  while (ib.hasNext()) {
    Object ko = ib.next();
    if (!(ko instanceof String)) continue;
    String id = (String) ko;
    long b = lnum(bagB.get(id));
    long a = bagA.containsKey(id) ? lnum(bagA.get(id)) : 0L;
    if (b < 0L || a < 0L || a >= b) continue;
    long now = -1L;
    try { now = lnum(fc.apply(new Object[] { u, id })); } catch (Throwable t) { now = -1L; }
    if (now < 0L) return null;
    if (nb > 0) sb.append(',');
    sb.append('"').append(id.replace('"', '_')).append("\":").append(now + (b - a));
    nb++;
  }
  if (nb == 0) return null;
  return head + "},\"bags\":{" + sb.toString() + "}}";
}""")
M(gsm, r"""
public static int freeSlot(@IC@ c) {
  if (c == null) return -1;
  for (int i = 0; i < c.getCapacity(); i++) {
    @IS@ x = c.getItemStack((short) i);
    if (x == null || x.isEmpty()) return i;
  }
  return -1;
}""")
M(gsm, "public static String secName(int s) { return s >= 0 && s < SEC.length ? SEC[s] : \"storage\"; }")
M(gsm, r"""
public static int[] findEid(@INV@ inv, String eid) {
  if (inv == null || eid == null) return null;
  for (int k = 0; k < @PKG@.GearStamp.SCAN.length; k++) {
    @IC@ c = @PKG@.GearStamp.section(inv, @PKG@.GearStamp.SCAN[k]);
    if (c == null) continue;
    for (int i = 0; i < c.getCapacity(); i++) {
      @IS@ x = c.getItemStack((short) i);
      if (x != null && !x.isEmpty() && eid.equals(@PKG@.GearData.eidOf(x))) return new int[] { @PKG@.GearStamp.SCAN[k], i };
    }
  }
  return null;
}""")
# a Requip space as Object[] { String eid, String itemId, BD metadata copy } rows (wardrobe:fn:list; empty without SkyyWardrobe 0.2)
M(gsm, r"""
public static java.util.ArrayList rqList(java.util.UUID u, String space) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.function.Function f = @PKG@.Gear.fn("wardrobe:fn:list");
  if (f == null || u == null) return out;
  Object r = null;
  try { r = f.apply(new Object[] { u, space }); } catch (Throwable t) { r = null; @PKG@.Gear.warnOnce("rqlist", "wardrobe:fn:list failed: " + t); }
  if (!(r instanceof Object[])) return out;
  Object[] a = (Object[]) r;
  for (int i = 0; i < a.length; i++) {
    if (!(a[i] instanceof Object[])) continue;
    Object[] e = (Object[]) a[i];
    if (e.length < 2 || !(e[0] instanceof String) || !(e[1] instanceof String)) continue;
    Object md = null;
    if (e.length > 2 && e[2] instanceof @BD@) md = e[2];
    out.add(new Object[] { e[0], e[1], md });
  }
  return out;
}""")
M(gsm, "public static boolean requip() { return @PKG@.Gear.fn(\"wardrobe:fn:canDeposit\") != null; }")
M(gsm, "public static boolean sacks() { return @PKG@.Gear.fn(\"sacks:fn:craftList\") != null && @PKG@.Gear.fn(\"sacks:fn:craftPay\") != null && @PKG@.Gear.fn(\"sacks:fn:craftRefund\") != null && @PKG@.Gear.fn(\"sacks:fn:craftCommit\") != null; }")
M(gsm, r"""
public static Object[] r0(String why) {
  return new Object[] { Integer.valueOf(0), why, null, null, null };
}""")
M(gsm, r"""
public static boolean due(java.util.UUID u, long now) {
  Object l = LAST.get(u);
  return !(l instanceof Long) || now - ((Long) l).longValue() >= GAP_MS || now < ((Long) l).longValue();
}""")
# THE CRAFT (header 5). Object[] { Integer code (1 made, 0 refused - nothing moved, -1 failed - see the message), String message, IS the
# item, BD its document, String where ("Requip" / "inventory") }
M(gsm, r"""
public static Object[] craft(@INV@ inv, java.util.UUID u, String who, String rid, boolean toRq) {
  if (!@PKG@.GearCfg.SMITH_ON) return r0("Crafting on the Smithing page is switched off on this server.");
  if (inv == null || u == null || rid == null) return r0("No player found.");
  Object[] row = byRid(rid);
  if (row == null) return r0("That recipe is not here any more - click Refresh.");
  String out = (String) row[1];
  @CRR@ rc = (@CRR@) row[2];
  java.util.function.Function pay = @PKG@.Gear.fn("sacks:fn:craftPay");
  java.util.function.Function ref = @PKG@.Gear.fn("sacks:fn:craftRefund");
  java.util.function.Function com = @PKG@.Gear.fn("sacks:fn:craftCommit");
  java.util.HashSet al = allowed(u);
  if (al == null || pay == null || ref == null || com == null) return r0("Crafting here needs SkyySacks 0.7.17 (the bench accessory rule) - craft it at a bench for now.");
  if (!al.contains(rid)) return r0(lockWhy(rc, false));
  String bw = @PKG@.GearRoll.blockWhy(out, u);
  if (bw != null) return r0(bw);
  // ROOM FIRST: a free Inventory / Backpack slot, or Requip takes it straight in
  @IC@[] give = @PKG@.GearStamp.giveOf(inv);
  @IC@ fc = null;
  int fs = -1;
  int fsec = -1;
  for (int k = 0; k < give.length && fc == null; k++) {
    int sl = freeSlot(give[k]);
    if (sl >= 0) { fc = give[k]; fs = sl; fsec = k == 0 ? 1 : 2; }
  }
  java.util.function.Function cd = @PKG@.Gear.fn("wardrobe:fn:canDeposit");
  java.util.function.Function dep = @PKG@.Gear.fn("wardrobe:fn:deposit");
  boolean rq = false;
  String rqWhy = null;
  if (toRq && cd != null) {
    try {
      Object w = cd.apply(new Object[] { u, out, Integer.valueOf(1) });
      rq = w == null;
      if (w != null) rqWhy = String.valueOf(w);
    } catch (Throwable tc) { rqWhy = "Requip did not answer"; }
  }
  if (fc == null && !(rq && dep != null)) return r0("No room - free a slot in your inventory" + (rqWhy != null ? " (Requip: " + rqWhy + ")" : "") + ". Nothing was used.");
  // the roll: exactly a bench craft (craft level + craft odds + the Smithing step-up; part.craft off = plain, as a bench gives)
  int lvl = @PKG@.GearRoll.craftLevel(out, u);
  @BD@ d = null;
  @IS@ s = null;
  try {
    if (@PKG@.GearCfg.PART_CRAFT) {
      d = @PKG@.GearRoll.craftDoc(out, u, lvl);
      s = @PKG@.GearData.put(new @IS@(out, 1), d, u);
    } else s = new @IS@(out, 1);
  } catch (Throwable t0) { s = null; @PKG@.Gear.warn("smithing: the item could not be made for " + who + ": " + t0); }
  if (s == null || s.isEmpty() || !out.equals(s.getItemId())) return r0("The item could not be made - nothing was used.");
  String rar = d == null ? "plain" : @PKG@.GearDefs.R_ID[@PKG@.GearData.rarity(d)];
  String ev = evidence(rid, u, inv, rc);
  @PKG@.GearLog.line("CRAFT-BEGIN " + who + " " + u + " smithing " + rid + " -> " + out + " " + rar + " lv" + lvl + " " + (d == null ? "plain" : d.toJson()) + " before " + ev + " to " + (rq && dep != null ? "Requip" + (fc != null ? " (else inventory " + secName(fsec) + " " + (fs + 1) + ")" : "") : "inventory " + secName(fsec) + " " + (fs + 1)));
  try { @PKG@.GearLog.flush(); } catch (Throwable xf) { }          // CRAFT-BEGIN is ON DISK before anything moves
  // FIXER 2: the counts the deposit evidence is measured against (only when the item may go straight into Requip)
  java.util.HashMap invB = null;
  java.util.HashMap bagB = null;
  if (rq && dep != null) { invB = invCounts(inv); bagB = bagAll(u); }
  // the materials: inventory first, then the bags (SkyySacks, the /craft order)
  long paid = 0L;
  String receipt = null;
  String payWhy = null;
  try {
    Object pr = pay.apply(new Object[] { u, rid, Integer.valueOf(1) });
    if (pr instanceof Object[] && ((Object[]) pr).length >= 2) {
      Object[] pa = (Object[]) pr;
      paid = lnum(pa[0]);
      if (pa[1] instanceof String) receipt = (String) pa[1];
      if (pa.length > 2 && pa[2] instanceof String) payWhy = (String) pa[2];
    }
  } catch (Throwable tp) { paid = 0L; @PKG@.Gear.warnOnce("craftpay", "sacks:fn:craftPay failed: " + tp); }
  if (paid < 1L) {
    long back1 = 0L;
    if (receipt != null) { try { back1 = lnum(ref.apply(new Object[] { u, receipt })); } catch (Throwable tr) { back1 = -1L; } }
    @PKG@.GearLog.line("CRAFT-REFUSED " + who + " " + u + " " + rid + " (not paid: " + paid + " " + payWhy + ", receipt " + receipt + " refund " + back1 + ")");
    return r0(payWhy == null || payWhy.indexOf("not enough") >= 0 ? "You do not have all the materials (inventory + bags)." : "Not crafted: " + payWhy + ".");
  }
  if (CRASH_AT == 1) throw new IllegalStateException("harness: a crash right after the materials were paid");
  // DELIVER (FIXER 2, critic 2 finding 1): Requip takes the item straight in with wardrobe:fn:deposit + the evidence of what this payment
  // took - the item is never in an inventory slot first (a depositSlot journal has no evidence: an engine rollback would bring the
  // materials back AND keep the pooled item). Requip refusing / nothing provable -> a free inventory slot; none -> refund.
  String where = null;
  String fail = null;
  if (rq && dep != null) {
    String pev = paidEvidence(rid, u, inv, invB, bagB);
    if (pev == null) {
      rqWhy = "this craft could not be proven to Requip, so it stays with you";
      @PKG@.GearLog.line("CRAFT-NOPROOF " + who + " " + u + " " + rid + " - no material change measured, delivered to the inventory");
    } else {
      String rs2 = null;
      try { Object o2 = dep.apply(new Object[] { u, s, "smithing", pev }); rs2 = o2 == null ? null : String.valueOf(o2); } catch (Throwable xd2) { rs2 = "refused:" + xd2; }
      if (rs2 != null && (rs2.startsWith("eid:") || rs2.startsWith("kind:"))) where = "Requip";
      else {
        rqWhy = rs2 == null ? "Requip did not answer" : (rs2.startsWith("refused:") ? rs2.substring(8) : rs2);
        fail = "Requip refused it (" + rqWhy + ")";
      }
    }
  } else if (toRq && rqWhy == null && cd == null) rqWhy = "Requip is not loaded";
  if (where == null) {
    // review fix (FX1): the payment may have put SURPLUS materials back into the inventory (SkyySacks giveSurplus -> addItemStack) -
    // possibly into the very slot reserved above; it may also have emptied slots. Use the reserved slot only while it is still empty.
    if (fc != null) {
      @IS@ cur = fc.getItemStack((short) fs);
      if (cur != null && !cur.isEmpty()) {
        String was = secName(fsec) + " " + (fs + 1);
        fc = null; fs = -1; fsec = -1;
        @PKG@.GearLog.line("CRAFT-SLOT " + who + " " + u + " " + rid + " the reserved slot " + was + " was filled by the payment's surplus");
      }
    }
    for (int k2 = 0; k2 < give.length && fc == null; k2++) {
      int sl2 = freeSlot(give[k2]);
      if (sl2 >= 0) { fc = give[k2]; fs = sl2; fsec = k2 == 0 ? 1 : 2; }
    }
    if (fc == null) fail = (fail != null ? fail + " and " : "") + "no free slot left after the materials were taken";
    else {
      Object t1 = null;
      Throwable e1 = null;
      try { t1 = fc.setItemStackForSlot((short) fs, s); } catch (Throwable x1) { e1 = x1; }
      @IS@ now = fc.getItemStack((short) fs);
      boolean put = e1 == null && !(t1 instanceof @TXN@ && !((@TXN@) t1).succeeded()) && now != null && !now.isEmpty() && out.equals(now.getItemId());
      if (put) { where = "inventory"; fail = null; }
      else {
        fail = (fail != null ? fail + " and " : "") + (e1 != null ? String.valueOf(e1) : "the inventory refused it");
        @IS@ chk = fc.getItemStack((short) fs);
        if (chk != null && !chk.isEmpty() && out.equals(chk.getItemId())) {
          try { fc.removeItemStackFromSlot((short) fs); } catch (Throwable xr) { }
          chk = fc.getItemStack((short) fs);
          if (chk != null && !chk.isEmpty() && out.equals(chk.getItemId())) { where = "inventory"; fail = null; }
        }
      }
    }
  }
  if (where == null) {
    long back2 = 0L;
    try { back2 = lnum(ref.apply(new Object[] { u, receipt })); } catch (Throwable xr2) { back2 = -1L; }
    @PKG@.GearLog.line("CRAFT-FAILED " + who + " " + u + " " + rid + " -> " + out + " (" + fail + ") refund " + receipt + " -> " + back2);
    if (back2 <= 0L) @PKG@.Gear.warn("SMITHING CRAFT FAILED for " + who + " (" + u + ") and the materials could not be given back - they are in gear.log (CRAFT-BEGIN / CRAFT-FAILED)");
    try { @PKG@.GearLog.flush(); } catch (Throwable xf2) { }
    return new Object[] { Integer.valueOf(-1), "The item could not be delivered - " + (back2 > 0L ? "your materials were given back." : "an admin can find your materials in the server log."), null, null, null };
  }
  try { com.apply(new Object[] { u, receipt }); } catch (Throwable xc) { @PKG@.Gear.warnOnce("craftcommit", "sacks:fn:craftCommit failed: " + xc); }
  LAST.put(u, Long.valueOf(System.currentTimeMillis()));
  long[] xp = new long[] { 0L, 0L, 0L };
  try { xp = @PKG@.GearRoll.payCraft(u, out, d == null ? "" : " " + rar, "/smithing"); } catch (Throwable xx) { }
  @PKG@.GearLog.line("CRAFT-DONE " + who + " " + u + " smithing " + rid + " -> " + out + " " + rar + " lv" + lvl + " -> " + where + (rqWhy != null && "inventory".equals(where) ? " (Requip: " + rqWhy + ")" : "") + " receipt " + receipt + " xp " + xp[1]);
  try {
    String note = @PKG@.GearRoll.craftNote(out, u);
    if (note != null && @PKG@.GearRoll.noteDue(u, out, System.currentTimeMillis())) @PKG@.Gear.tell(u, "[Gear] " + note, @PKG@.GearDefs.C_LABEL);
  } catch (Throwable xn) { }
  String nm = d == null ? @PKG@.Gear.itemName(out) : @PKG@.GearView.nameText(out, d);
  String rn = d == null ? "plain" : @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(d)];
  String to = "Requip".equals(where) ? "Requip" : "your inventory" + (toRq && rqWhy != null ? " (Requip: " + rqWhy + ")" : "");
  return new Object[] { Integer.valueOf(1), "Made: " + nm + " (" + rn + ") -> " + to, s, d, where };
}""")
# the item ids a player already has (every inventory section + both Requip spaces)
M(gsm, r"""
public static java.util.HashSet owned(java.util.UUID u, @INV@ inv) {
  java.util.HashSet s = new java.util.HashSet();
  @IC@[] all = @PKG@.GearStamp.allOf(inv);
  for (int k = 0; k < all.length; k++) {
    if (all[k] == null) continue;
    for (int i = 0; i < all[k].getCapacity(); i++) {
      @IS@ x = all[k].getItemStack((short) i);
      if (x != null && !x.isEmpty()) s.add(x.getItemId());
    }
  }
  String[] sp = new String[] { "armor", "items" };
  for (int k = 0; k < sp.length; k++) {
    java.util.ArrayList l = rqList(u, sp[k]);
    for (int i = 0; i < l.size(); i++) s.add(((Object[]) l.get(i))[1]);
  }
  return s;
}""")
# "Craft every missing piece": Object[] { Integer made, String message } - one transaction per piece, stops at the first refusal
M(gsm, r"""
public static Object[] craftAll(@INV@ inv, java.util.UUID u, String who, String[] rids, String[] outs, boolean toRq) {
  java.util.HashSet al = allowed(u);
  if (al == null || !sacks()) return new Object[] { Integer.valueOf(0), "Crafting here needs SkyySacks 0.7.17 (the bench accessory rule) - craft it at a bench for now." };
  java.util.HashSet own = owned(u, inv);
  int made = 0;
  int skipped = 0;
  String stop = null;
  StringBuilder got = new StringBuilder();
  for (int i = 0; i < rids.length; i++) {
    if (own.contains(outs[i])) continue;
    Object[] row = byRid(rids[i]);
    if (row == null || !al.contains(rids[i]) || @PKG@.GearRoll.blockWhy(outs[i], u) != null) { skipped++; continue; }
    Object[] hv = have(u, inv, rids[i], (@CRR@) row[2]);
    if (((Long) hv[0]).longValue() < 1L) { skipped++; continue; }
    Object[] r = craft(inv, u, who, rids[i], toRq);
    if (((Integer) r[0]).intValue() != 1) { stop = (String) r[1]; break; }
    made++;
    @BD@ d = (@BD@) r[3];
    if (got.length() > 0) got.append(", ");
    got.append(@PKG@.Gear.itemName(outs[i])).append(d == null ? "" : " (" + @PKG@.GearDefs.R_NAME[@PKG@.GearData.rarity(d)] + ")");
  }
  if (made == 0 && stop == null) return new Object[] { Integer.valueOf(0), skipped > 0 ? "Nothing to craft: the missing pieces are locked or you lack their materials." : "You already have every piece." };
  String m = made > 0 ? "Made " + made + ": " + got : "";
  if (stop != null) m = m + (m.length() > 0 ? " - then stopped: " : "") + stop;
  return new Object[] { Integer.valueOf(made), m };
}""")
M(gsm, r"""
public static String plural(String s) {
  if (s.endsWith("s")) return s;
  return s + "s";
}""")
M(gsm, r"""
public static String groupName(String key, int c) {
  if (c == 4) return "Multitools";
  String s = key;
  if (s.startsWith("Armor_")) s = s.substring(6);
  else if (s.startsWith("Weapon_")) s = s.substring(7);
  else if (s.startsWith("Tool_")) s = s.substring(5);
  if (s.endsWith("_")) s = s.substring(0, s.length() - 1);
  s = s.replace('_', ' ').trim();
  if (s.length() == 0) s = key;
  if (c == 0 || c == 1) return s + " Set";
  return plural(s);
}""")
# sort helper: a[] by key[] ascending, then by name
M(gsm, r"""
public static void sortBy(Object[] a, int[] key, String[] tie) {
  for (int i = 1; i < a.length; i++) {
    int j = i;
    while (j > 0 && (key[j - 1] > key[j] || (key[j - 1] == key[j] && tie[j - 1].compareTo(tie[j]) > 0))) {
      Object x = a[j]; a[j] = a[j - 1]; a[j - 1] = x;
      int y = key[j]; key[j] = key[j - 1]; key[j - 1] = y;
      String z = tie[j]; tie[j] = tie[j - 1]; tie[j - 1] = z;
      j--;
    }
  }
}""")
# THE CARDS of category c: ArrayList of Object[] { String key, String[] outs, String[] rids, Integer lo, Integer hi, Integer cat }
M(gsm, r"""
public static java.util.ArrayList groups(java.util.UUID u, int c, boolean all) {
  java.util.ArrayList rs = recipes();
  java.util.LinkedHashMap g = new java.util.LinkedHashMap();
  for (int i = 0; i < rs.size(); i++) {
    Object[] r = (Object[]) rs.get(i);
    String out = (String) r[1];
    if (cat(out) != c || !shows(u, out, all)) continue;
    String k = (c == 0 || c == 1) ? setKey(out) : famKey(out);
    java.util.ArrayList l = (java.util.ArrayList) g.get(k);
    if (l == null) { l = new java.util.ArrayList(); g.put(k, l); }
    l.add(r);
  }
  java.util.ArrayList res = new java.util.ArrayList();
  java.util.Iterator it = g.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    Object[] a = ((java.util.ArrayList) e.getValue()).toArray();
    int[] key = new int[a.length];
    String[] tie = new String[a.length];
    int lo = 9999;
    int hi = 0;
    for (int i = 0; i < a.length; i++) {
      String out = (String) ((Object[]) a[i])[1];
      int[] b = @PKG@.GearLevel.band(out);
      if (b[0] < lo) lo = b[0];
      if (b[1] > hi) hi = b[1];
      int si = slotIx(out);
      key[i] = (c == 0 || c == 1) ? (si < 0 ? 4 : si) : b[0];
      tie[i] = out;
    }
    sortBy(a, key, tie);
    String[] outs = new String[a.length];
    String[] rids = new String[a.length];
    for (int i = 0; i < a.length; i++) { outs[i] = (String) ((Object[]) a[i])[1]; rids[i] = (String) ((Object[]) a[i])[0]; }
    res.add(new Object[] { e.getKey(), outs, rids, Integer.valueOf(lo), Integer.valueOf(hi), Integer.valueOf(c) });
  }
  Object[] ga = res.toArray();
  int[] gk = new int[ga.length];
  String[] gt = new String[ga.length];
  for (int i = 0; i < ga.length; i++) { gk[i] = ((Integer) ((Object[]) ga[i])[3]).intValue(); gt[i] = (String) ((Object[]) ga[i])[0]; }
  sortBy(ga, gk, gt);
  java.util.ArrayList sorted = new java.util.ArrayList();
  for (int i = 0; i < ga.length; i++) sorted.add(ga[i]);
  return sorted;
}""")
# a document to preview an item at the level the player would make it (no lines)
M(gsm, r"""
public static @BD@ prevDoc(String id, java.util.UUID u) {
  @BD@ d = @PKG@.GearData.base(@PKG@.GearData.kindFor(id), 0, true, "preview");
  int lv = @PKG@.GearRoll.craftLevel(id, u);
  if (lv >= 0) d.put("lvl", new org.bson.BsonInt32(@PKG@.GearLevel.clamp(lv)));
  return d;
}""")
# a set's base stats added up at the player's craft level: "Health +48  Resist +12%" ("" = none)
M(gsm, r"""
public static String setStats(String[] outs, java.util.UUID u) {
  double h = 0.0;
  double r = 0.0;
  boolean any = false;
  for (int i = 0; i < outs.length; i++) {
    float[] t = null;
    try { t = @PKG@.GearBase.armorTarget(outs[i], prevDoc(outs[i], u)); } catch (Throwable x) { t = null; }
    if (t == null) continue;
    any = true;
    h = h + (double) t[0];
    r = r + (double) t[1];
  }
  if (!any) return "";
  return "Health +" + Math.round(h) + "   Resist +" + @PKG@.Gear.fnum(Math.round(r * 1000.0) / 10.0) + "%";
}""")
# the full-set bonus words of a set card ("" = no set)
M(gsm, r"""
public static String setBonus(String[] outs) {
  try {
    for (int i = 0; i < outs.length; i++) {
      String sid = @PKG@.GearMine.setFor(outs[i]);
      if (sid == null) continue;
      Object[] t = @PKG@.GearCfg.STAB;
      int k = @PKG@.GearSet.idx(t, sid);
      if (k < 0) return "Full set: " + sid + " (not set up)";
      return "Full set (" + @PKG@.GearSet.pieces(t, k) + "): " + @PKG@.GearSet.bonusText(t, k);
    }
  } catch (Throwable x) { }
  return "";
}""")
M(gsm, r"""
public static String typeWord(String[] outs, int c) {
  if (c == 1) return "Mining";
  if (c != 0 || outs.length == 0) return "";
  return T_NAME[armorType(outs[0])];
}""")
# a card's state: Object[] { Integer craftable now, Integer allowed, Integer total, String word, String colour }
M(gsm, r"""
public static Object[] state(java.util.UUID u, @INV@ inv, Object[] g, java.util.HashSet al, java.util.HashMap hc) {
  String[] outs = (String[]) g[1];
  String[] rids = (String[]) g[2];
  int n = outs.length;
  if (al == null) return new Object[] { Integer.valueOf(0), Integer.valueOf(0), Integer.valueOf(n), "Browse only - needs SkyySacks 0.7.17", @PKG@.GearDefs.C_GRAY };
  int ok = 0;
  int allow = 0;
  int lvl = 0;
  String lock = null;
  for (int i = 0; i < n; i++) {
    Object[] row = byRid(rids[i]);
    if (row == null) continue;
    if (!al.contains(rids[i])) { if (lock == null) lock = lockWhy((@CRR@) row[2], true); continue; }
    allow++;
    if (@PKG@.GearRoll.blockWhy(outs[i], u) != null) { lvl++; continue; }
    Object[] hv = haveC(hc, u, inv, rids[i], (@CRR@) row[2]);
    if (((Long) hv[0]).longValue() >= 1L) ok++;
  }
  if (allow == 0) return new Object[] { Integer.valueOf(0), Integer.valueOf(0), Integer.valueOf(n), lock == null ? "Locked" : lock, @PKG@.GearDefs.C_GOLD };
  if (lvl == allow) return new Object[] { Integer.valueOf(0), Integer.valueOf(allow), Integer.valueOf(n), "Level too low", @PKG@.GearDefs.C_GOLD };
  return new Object[] { Integer.valueOf(ok), Integer.valueOf(allow), Integer.valueOf(n), ok + "/" + n + " craftable", ok > 0 ? "#ffffff" : @PKG@.GearDefs.C_LABEL };
}""")
M(gsm, r"""
public static Object[] state(java.util.UUID u, @INV@ inv, Object[] g, java.util.HashSet al) {
  return state(u, inv, g, al, null);
}""")
M(gsm, r"""
public static String statusText() {
  return "smithing hub " + (@PKG@.GearCfg.SMITH_ON ? "on (/smithing Craft tab: crafts through SkyySacks 0.7.17's craft bridge, into Requip when SkyyWardrobe 0.2 is loaded)" : "Craft tab OFF (part.smithing)");
}""")
# the live state for /gear-style checks and the harness (the bridges of other mods are published after our setup)
M(gsm, r"""
public static String liveText() {
  return recipes().size() + " gear recipe(s); crafting " + (sacks() ? "via SkyySacks" : "waits for SkyySacks 0.7.17") + "; Requip " + (requip() ? "on" : "not loaded");
}""")
# the Craft tab click on another tab's page (mode:3) -> /smithing
M(gsm, r"""
public static boolean craftTab(String data, @PR@ pr) {
  if (data == null) return false;
  if (!"mode:3".equals(@PKG@.Gear.jsonStr(data, "a"))) return false;
  if (@PKG@.GearCfg.SMITH_ON && pr != null) {
    try { @CMGR@.get().handleCommand(pr, "smithing"); } catch (Throwable t) { @PKG@.Gear.warn("the Craft tab could not open /smithing: " + t); }
  }
  return true;
}""")
M(gui, r"""
public static String cardStyle(boolean on) {
  if (on) return "Style: ButtonStyle(Default: (Background: #000000(0.45)), Hovered: (Background: #000000(0.45)), Pressed: (Background: #000000(0.5)));";
  return "Style: ButtonStyle(Default: (Background: #000000(0.25)), Hovered: (Background: #000000(0.4)), Pressed: (Background: #000000(0.5)));";
}""")
M(gui, r"""
public static String cell(int sz, String id) {
  String ic = id == null ? "" : " ItemIcon { Anchor: (Width: " + (sz - 8) + ", Height: " + (sz - 8) + ", Left: 4, Top: 4); ItemId: \"" + @PKG@.Gear.safe(id) + "\"; }";
  return "Group { Anchor: (Width: " + sz + ", Height: " + sz + "); Background: #000000(0.3);" + ic + " }";
}""")
M(gui, 'public static String gap(int w) { return "Group { Anchor: (Width: " + w + "); }"; }')

# ================================================================= SmithPage: the Craft tab (header 2)
for _f in ("public int cat;", "public int view;", "public String gkey;", "public int pageNo;", "public int rowPage;", "public String info;",
           "public String epoch;", "public long lastClick;", "public int token;", "public java.util.ArrayList cards;", "public Object[] grp;",
           "public java.util.HashSet al;", "public boolean picked;",
           "public java.util.HashMap hc;", "public long lastNav;", "public String why1;"):          # review fix: have cache, click coalescing, the row reason
    F(spg, _f)
C(spg, r"""
public SmithPage(@PR@ pr) {
  super(pr, @LIFE@.CanDismiss);
  this.cat = 0; this.view = 0; this.gkey = null; this.pageNo = 0; this.rowPage = 0;
  this.info = ""; this.lastClick = 0L; this.token = 1; this.cards = new java.util.ArrayList(); this.grp = null; this.al = null;
  this.epoch = @PKG@.Gear.epoch(pr.getUuid());
}""")
# the figure of a set (64 px cells: Head top centre, Hands left of Chest, Legs bottom centre) or the tier ladder (up to 8 icons) into a group
M(spg, r"""
public static void figure(@UCB@ b, String gid, Object[] g, int sz, int w) {
  String[] outs = (String[]) g[1];
  int c = ((Integer) g[5]).intValue();
  if (c == 0 || c == 1) {
    String[] at = new String[4];
    for (int i = 0; i < outs.length; i++) { int s = @PKG@.GearSmith.slotIx(outs[i]); if (s >= 0 && at[s] == null) at[s] = outs[i]; }
    if (at[0] == null && at[1] == null && at[2] == null && at[3] == null && outs.length > 0) at[1] = outs[0];
    int mid = (w - sz) / 2;
    int left = mid - sz < 0 ? 0 : mid - sz;
    b.appendInline(gid, "Group { Anchor: (Height: " + sz + "); LayoutMode: Left; " + @PKG@.GearUi.gap(mid) + " " + @PKG@.GearUi.cell(sz, at[0]) + " }");
    b.appendInline(gid, "Group { Anchor: (Height: " + sz + "); LayoutMode: Left; " + @PKG@.GearUi.gap(left) + " " + @PKG@.GearUi.cell(sz, at[2]) + " " + @PKG@.GearUi.cell(sz, at[1]) + " }");
    b.appendInline(gid, "Group { Anchor: (Height: " + sz + "); LayoutMode: Left; " + @PKG@.GearUi.gap(mid) + " " + @PKG@.GearUi.cell(sz, at[3]) + " }");
    return;
  }
  int per = 4;
  int cs = sz - 8;
  int pad = (w - per * cs - (per - 1) * 6) / 2;
  if (pad < 0) pad = 0;
  for (int r = 0; r < 2; r++) {
    StringBuilder sb = new StringBuilder("Group { Anchor: (Height: " + (cs + 8) + "); LayoutMode: Left; Padding: (Top: 4); " + @PKG@.GearUi.gap(pad));
    for (int k = 0; k < per; k++) {
      int i = r * per + k;
      if (i >= outs.length) break;
      if (k > 0) sb.append(" ").append(@PKG@.GearUi.gap(6));
      sb.append(" ").append(@PKG@.GearUi.cell(cs, outs[i]));
    }
    sb.append(" }");
    b.appendInline(gid, sb.toString());
  }
  if (outs.length > 8) {
    b.appendInline(gid, "Label { Anchor: (Height: 22); Text: \"\"; }");
  }
}""")
M(spg, r"""
public void left(@UCB@ b, @UEB@ ev, java.util.UUID u, boolean all) {
  b.appendInline("#SkyyGMain", "Group #SkyyGLeft { Anchor: (Width: 220); LayoutMode: Top; }");
  b.appendInline("#SkyyGLeft", "Label #SkyyGCatH { Anchor: (Height: 28); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.set("#SkyyGCatH.Text", "Craft");
  boolean mt = @PKG@.GearUi.multiTab();
  for (int c = 0; c < @PKG@.GearSmith.CAT_NAME.length; c++) {
    if (c == 4 && !mt) continue;
    b.appendInline("#SkyyGLeft", "TextButton #SkyyGCat" + c + " { Anchor: (Height: 40); Text: \"" + @PKG@.GearSmith.CAT_NAME[c] + "\"; " + @PKG@.GearUi.btn(c == this.cat ? 0 : 1) + " }");
    b.appendInline("#SkyyGLeft", "Group { Anchor: (Height: 6); }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGCat" + c, @EVD@.of("a", "cat:" + c));
  }
  b.appendInline("#SkyyGLeft", "Group { Anchor: (Height: 10); }");
  String cls = @PKG@.GearSmith.classOf(u);
  b.appendInline("#SkyyGLeft", "Label #SkyyGCls { Anchor: (Height: 26); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.set("#SkyyGCls.Text", cls == null ? "Class: none picked" : "Class: " + cls);
  b.appendInline("#SkyyGLeft", "Label #SkyyGClsA { Anchor: (Height: 22); Text: \"\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  int at = @PKG@.GearSmith.armorFor(cls);
  b.set("#SkyyGClsA.Text", cls == null ? "Everything is shown." : (at > 0 ? @PKG@.GearSmith.T_NAME[at] + " armor, your weapons" : "Any armor, your weapons"));
  b.appendInline("#SkyyGLeft", "TextButton #SkyyGFltMine { Anchor: (Height: 40); Text: \"My class\"; " + @PKG@.GearUi.btn(all ? 1 : 0) + " }");
  b.appendInline("#SkyyGLeft", "Group { Anchor: (Height: 6); }");
  b.appendInline("#SkyyGLeft", "TextButton #SkyyGFltAll { Anchor: (Height: 40); Text: \"Show all\"; " + @PKG@.GearUi.btn(all ? 0 : 1) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGFltMine", @EVD@.of("a", "flt:0"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGFltAll", @EVD@.of("a", "flt:1"));
  b.appendInline("#SkyyGLeft", "Group { Anchor: (Height: 10); }");
  boolean rq = @PKG@.GearSmith.requip();
  boolean to = @PKG@.GearSmith.toRequip(u);
  b.appendInline("#SkyyGLeft", "Label #SkyyGDestH { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.set("#SkyyGDestH.Text", "Crafted gear goes to");
  b.appendInline("#SkyyGLeft", "TextButton #SkyyGDestRq { Anchor: (Height: 40); Text: \"Requip\"; " + @PKG@.GearUi.btn(!rq ? 3 : (to ? 0 : 1)) + " }");
  b.appendInline("#SkyyGLeft", "Group { Anchor: (Height: 6); }");
  b.appendInline("#SkyyGLeft", "TextButton #SkyyGDestInv { Anchor: (Height: 40); Text: \"Inventory\"; " + @PKG@.GearUi.btn(rq && to ? 1 : 0) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGDestRq", @EVD@.of("a", "dest:1"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGDestInv", @EVD@.of("a", "dest:0"));
}""")
# one set / family card (266 x 300: 6 + name 24 + sub 18 + figure 192 + stats 18 + bonus 18 + state 18 + 6)
M(spg, r"""
public void card(@UCB@ b, @UEB@ ev, String parent, int i, Object[] g, java.util.UUID u, @INV@ inv) {
  String cid = "#SkyyGCard" + i;
  int c = ((Integer) g[5]).intValue();
  String[] outs = (String[]) g[1];
  b.appendInline(parent, "Button " + cid + " { Anchor: (Width: 266, Height: 300); LayoutMode: Top; Padding: (Full: 6); " + @PKG@.GearUi.cardStyle(false) + " }");
  b.appendInline(cid, "Label " + cid + "N { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.appendInline(cid, "Label " + cid + "S { Anchor: (Height: 18); Text: \"\"; Style: (FontSize: 13, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 10); }");
  b.appendInline(cid, "Group " + cid + "F { Anchor: (Height: 192); LayoutMode: Top; }");
  b.appendInline(cid, "Label " + cid + "A { Anchor: (Height: 18); Text: \"\"; Style: (FontSize: 13, TextColor: #ffffff, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 10); }");
  b.appendInline(cid, "Label " + cid + "B { Anchor: (Height: 18); Text: \"\"; Style: (FontSize: 13, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 9); }");
  Object[] stt = @PKG@.GearSmith.state(u, inv, g, this.al, this.hc);
  b.appendInline(cid, "Label " + cid + "C { Anchor: (Height: 18); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: " + (String) stt[4] + ", HorizontalAlignment: Center, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 10); }");
  int lo = ((Integer) g[3]).intValue();
  int hi = ((Integer) g[4]).intValue();
  String tw = @PKG@.GearSmith.typeWord(outs, c);
  b.set(cid + "N.Text", @PKG@.GearSmith.groupName((String) g[0], c));
  b.set(cid + "S.Text", "Lv " + lo + (hi > lo ? "-" + hi : "") + (tw.length() > 0 ? " - " + tw : "") + (c >= 2 ? " - " + outs.length + (outs.length == 1 ? " tier" : " tiers") : ""));
  figure(b, cid + "F", g, 64, 254);
  String a;
  String bo;
  if (c == 0 || c == 1) {
    a = @PKG@.GearSmith.setStats(outs, u);
    bo = @PKG@.GearSmith.setBonus(outs);
    if (bo.length() == 0) bo = "Full set: no bonus";
  } else {
    a = outs.length > 8 ? "+" + (outs.length - 8) + " more tiers" : "";
    String cr = c == 2 ? @PKG@.GearView.classReq(outs[0]) : null;
    bo = c == 2 ? (cr == null ? "Any class" : "Class: " + cr) : (c == 4 ? "Mining + Foraging" : "Every class");
  }
  b.set(cid + "A.Text", a);
  b.set(cid + "B.Text", bo);
  b.set(cid + "C.Text", (String) stt[3]);
  ev.addEventBinding(@BT@.Activating, cid, @EVD@.of("a", "card:" + i));
}""")
M(spg, r"""
public void cardsArea(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv) {
  b.appendInline("#SkyyGMain", "Group #SkyyGCards { Anchor: (Width: 830); LayoutMode: Top; }");
  int per = 6;
  int n = this.cards.size();
  int pages = (n + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.pageNo >= pages) this.pageNo = pages - 1;
  if (this.pageNo < 0) this.pageNo = 0;
  int start = this.pageNo * per;
  if (n == 0) {
    b.appendInline("#SkyyGCards", "Label #SkyyGNone1 { Anchor: (Height: 60); Text: \"\"; Style: (FontSize: 17, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    boolean any = !@PKG@.GearSmith.groups(u, this.cat, true).isEmpty();
    b.set("#SkyyGNone1.Text", any ? "Nothing here for your class - click Show all." : "Nothing in " + @PKG@.GearSmith.CAT_NAME[this.cat] + " can be crafted on this server yet.");
  }
  for (int r = 0; r < 2; r++) {
    if (start + r * 3 >= n) break;
    String rid = "#SkyyGCardRow" + r;
    if (r > 0) b.appendInline("#SkyyGCards", "Group { Anchor: (Height: 12); }");
    b.appendInline("#SkyyGCards", "Group " + rid + " { Anchor: (Height: 300); LayoutMode: Left; }");
    for (int k = 0; k < 3; k++) {
      int i = start + r * 3 + k;
      if (i >= n) break;
      if (k > 0) b.appendInline(rid, @PKG@.GearUi.gap(16));
      card(b, ev, rid, i, (Object[]) this.cards.get(i), u, inv);
    }
  }
  b.appendInline("#SkyyGCards", "Group { Anchor: (Height: " + (n <= start + 3 ? 312 : 0) + "); }");
  b.appendInline("#SkyyGCards", "Group #SkyyGPager { Anchor: (Height: 40); LayoutMode: Left; Padding: (Top: 4); }");
  b.appendInline("#SkyyGPager", "TextButton #SkyyGBtnPrev { Anchor: (Width: 140, Height: 36); Text: \"Prev\"; " + @PKG@.GearUi.btn(this.pageNo > 0 ? 1 : 3) + " }");
  b.appendInline("#SkyyGPager", "Label #SkyyGPageTxt { Anchor: (Width: 550, Height: 36); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
  b.set("#SkyyGPageTxt.Text", @PKG@.GearSmith.CAT_NAME[this.cat] + " - page " + (this.pageNo + 1) + " / " + pages + " (" + n + (this.cat <= 1 ? " sets" : " families") + ")");
  b.appendInline("#SkyyGPager", "TextButton #SkyyGBtnNext { Anchor: (Width: 140, Height: 36); Text: \"Next\"; " + @PKG@.GearUi.btn(this.pageNo + 1 < pages ? 1 : 3) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnPrev", @EVD@.of("a", "prev"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnNext", @EVD@.of("a", "next"));
}""")
# one piece / tier row (height 74): icon | name + band + materials (2 lines of 2) | Craft
M(spg, r"""
public void pieceRow(@UCB@ b, @UEB@ ev, int i, String rid, String out, java.util.UUID u, @INV@ inv) {
  String gid = "#SkyyGPc" + i;
  Object[] row = @PKG@.GearSmith.byRid(rid);
  @CRR@ rc = row == null ? null : (@CRR@) row[2];
  b.appendInline("#SkyyGRows", "Group " + gid + " { Anchor: (Height: 74); LayoutMode: Left; Padding: (Top: 4); }");
  b.appendInline(gid, @PKG@.GearUi.cell(56, out));
  b.appendInline(gid, @PKG@.GearUi.gap(8));
  b.appendInline(gid, "Group " + gid + "T { Anchor: (Width: 330); LayoutMode: Top; }");
  int[] bd = @PKG@.GearLevel.band(out);
  b.appendInline(gid + "T", "Label " + gid + "N { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set(gid + "N.Text", @PKG@.Gear.itemName(out) + "  [Lv " + bd[0] + (bd[1] > bd[0] ? "-" + bd[1] : "") + "]");
  Object[] hv = @PKG@.GearSmith.haveC(this.hc, u, inv, rid, rc);
  String[] ids = (String[]) hv[1];
  long[] h = (long[]) hv[2];
  long[] nd = (long[]) hv[3];
  for (int ln = 0; ln < 2; ln++) {
    String lid = gid + "M" + ln;
    b.appendInline(gid + "T", "Group " + lid + " { Anchor: (Height: 22); LayoutMode: Left; }");
    for (int k = 0; k < 2; k++) {
      int m = ln * 2 + k;
      if (m >= ids.length) break;
      boolean more = m == 3 && ids.length > 4;
      boolean ok = h[m] >= nd[m];
      String mt = @PKG@.GearSmith.matName(ids[m]) + " " + (h[m] < 0L ? "?" : String.valueOf(h[m])) + "/" + nd[m];
      if (more) {          // review fix: 5+ materials -> the 4th line lists every remaining one (have / need), gold when any is short
        StringBuilder mb = new StringBuilder();
        for (int q = 3; q < ids.length; q++) {
          if (q > 3) mb.append(", ");
          mb.append(@PKG@.GearSmith.matName(ids[q])).append(" ").append(h[q] < 0L ? "?" : String.valueOf(h[q])).append("/").append(nd[q]);
          if (h[q] < nd[q]) ok = false;
        }
        mt = mb.toString();
      }
      b.appendInline(lid, "Label " + lid + "L" + k + " { Anchor: (Width: 165); Text: \"\"; Style: (FontSize: 13, TextColor: " + (ok ? "#ffffff" : @PKG@.GearDefs.C_GOLD) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: " + (more ? 8 : 10) + "); }");
      b.set(lid + "L" + k + ".Text", mt);
    }
  }
  // review fix (spec 4.3 "greyed with the reason"): the button names the short reason; the first full reason goes to the gold line
  String why = null;
  String full = null;
  String bw = null;
  if (this.al == null) { why = "No SkyySacks"; full = "Crafting here needs SkyySacks 0.7.17 (the bench accessory rule) - craft it at a bench for now."; }
  else if (rc == null || !this.al.contains(rid)) { why = "Locked"; full = rc == null ? "That recipe is not here any more - click Refresh." : @PKG@.GearSmith.lockWhy(rc, false); }
  else {
    bw = @PKG@.GearRoll.blockWhy(out, u);
    if (bw != null) { why = "Level too low"; full = bw; }
    else if (((Long) hv[0]).longValue() < 1L) why = "No materials";
  }
  if (full != null && this.why1 == null) this.why1 = @PKG@.Gear.itemName(out) + ": " + full;
  b.appendInline(gid, @PKG@.GearUi.gap(8));
  b.appendInline(gid, "Group " + gid + "B { Anchor: (Width: 160); LayoutMode: Top; Padding: (Top: 12); }");
  b.appendInline(gid + "B", "TextButton " + gid + "Go { Anchor: (Height: 40); Text: \"" + (why == null ? "Craft" : why) + "\"; " + @PKG@.GearUi.btn(why == null ? 0 : 3) + " }");
  ev.addEventBinding(@BT@.Activating, gid + "Go", @EVD@.of("a", "craft:" + i + ":" + this.token));
}""")
M(spg, r"""
public void piecesArea(@UCB@ b, @UEB@ ev, java.util.UUID u, @INV@ inv) {
  Object[] g = this.grp;
  int c = ((Integer) g[5]).intValue();
  String[] outs = (String[]) g[1];
  String[] rids = (String[]) g[2];
  b.appendInline("#SkyyGMain", "Group #SkyyGPieces { Anchor: (Width: 830); LayoutMode: Top; }");
  b.appendInline("#SkyyGPieces", "Group #SkyyGPHead { Anchor: (Height: 44); LayoutMode: Left; }");
  b.appendInline("#SkyyGPHead", "TextButton #SkyyGBtnPBack { Anchor: (Width: 120, Height: 40); Text: \"Back\"; " + @PKG@.GearUi.btn(1) + " }");
  b.appendInline("#SkyyGPHead", "Label #SkyyGPTitle { Anchor: (Width: 700, Height: 40); Padding: (Horizontal: 14); Text: \"\"; Style: (FontSize: 19, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center, RenderUppercase: true, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 12); }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnPBack", @EVD@.of("a", "pback"));
  int lo = ((Integer) g[3]).intValue();
  int hi = ((Integer) g[4]).intValue();
  String tw = @PKG@.GearSmith.typeWord(outs, c);
  b.set("#SkyyGPTitle.Text", @PKG@.GearSmith.groupName((String) g[0], c) + "  (" + (tw.length() > 0 ? tw + ", " : "") + "Lv " + lo + (hi > lo ? "-" + hi : "") + ")");
  b.appendInline("#SkyyGPieces", "Group #SkyyGPBody { Anchor: (Height: 600); LayoutMode: Left; Padding: (Top: 6); }");
  b.appendInline("#SkyyGPBody", "Group #SkyyGPFig { Anchor: (Width: 250); LayoutMode: Top; }");
  figure(b, "#SkyyGPFig", g, (c == 0 || c == 1) ? 80 : 64, 250);
  b.appendInline("#SkyyGPFig", "Group { Anchor: (Height: 10); }");
  String st = (c == 0 || c == 1) ? @PKG@.GearSmith.setStats(outs, u) : "";
  String bo = (c == 0 || c == 1) ? @PKG@.GearSmith.setBonus(outs) : (c == 2 ? (@PKG@.GearView.classReq(outs[0]) == null ? "Any class can use these." : "Class: " + @PKG@.GearView.classReq(outs[0])) : "Every class gathers.");
  b.appendInline("#SkyyGPFig", "Label #SkyyGPStat { Anchor: (Height: 24); Text: \"\"; Style: (FontSize: 14, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 10); }");
  b.set("#SkyyGPStat.Text", st.length() > 0 ? st + " (at your level)" : "");
  b.appendInline("#SkyyGPFig", "Label #SkyyGPBonus { Anchor: (Height: 66); Text: \"\"; Style: (FontSize: 14, TextColor: #96a9be, VerticalAlignment: Top, Wrap: true); }");
  b.set("#SkyyGPBonus.Text", bo.length() > 0 ? bo : "Full set: no bonus.");
  b.appendInline("#SkyyGPFig", "Label #SkyyGPRoll { Anchor: (Height: 88); Text: \"\"; Style: (FontSize: 14, TextColor: #878e9c, VerticalAlignment: Top, Wrap: true); }");
  int lv = outs.length > 0 ? @PKG@.GearRoll.craftLevel(outs[0], u) : -1;
  String how = c == 1 ? "Each piece is a Mining Set piece (fixed mining lines, like a bench craft)" : "Each craft rolls a rarity like a bench craft (your Smithing step-up " + @PKG@.Gear.fnum(@PKG@.GearRoll.smithChance(u)) + "%)";
  b.set("#SkyyGPRoll.Text", how + (lv >= 0 ? " and is made at your level (Lv " + lv + " here)." : ".") + " Materials: inventory first, then your bags.");
  b.appendInline("#SkyyGPBody", @PKG@.GearUi.gap(12));
  b.appendInline("#SkyyGPBody", "Group #SkyyGPRight { Anchor: (Width: 568); LayoutMode: Top; }");
  b.appendInline("#SkyyGPRight", "Label #SkyyGPWhy { Anchor: (Height: 40); Text: \"\"; Style: (FontSize: 14, TextColor: " + @PKG@.GearDefs.C_GOLD + ", VerticalAlignment: Center, Wrap: true); }");
  b.appendInline("#SkyyGPRight", "Group #SkyyGRows { Anchor: (Height: 444); LayoutMode: Top; }");
  this.why1 = null;
  int per = 6;
  int pages = (outs.length + per - 1) / per;
  if (pages < 1) pages = 1;
  if (this.rowPage >= pages) this.rowPage = pages - 1;
  if (this.rowPage < 0) this.rowPage = 0;
  int start = this.rowPage * per;
  for (int i = start; i < outs.length && i < start + per; i++) pieceRow(b, ev, i, rids[i], outs[i], u, inv);
  b.set("#SkyyGPWhy.Text", this.why1 == null ? "" : this.why1);
  if (c == 0 || c == 1) {          // a whole SET at once (a weapon / tool family is one tier at a time)
    b.appendInline("#SkyyGPRight", "Group #SkyyGPAll { Anchor: (Height: 56); LayoutMode: Left; Padding: (Top: 8); }");
    b.appendInline("#SkyyGPAll", "TextButton #SkyyGBtnAll { Anchor: (Width: 330, Height: 44); Text: \"Craft every missing piece\"; " + @PKG@.GearUi.btn(this.al == null ? 3 : 0) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnAll", @EVD@.of("a", "craftall:" + this.token));
  }
  if (pages > 1) {
    b.appendInline("#SkyyGPRight", "Group #SkyyGRPager { Anchor: (Height: 44); LayoutMode: Left; Padding: (Top: 4); }");
    b.appendInline("#SkyyGRPager", "TextButton #SkyyGBtnRPrev { Anchor: (Width: 140, Height: 36); Text: \"Prev\"; " + @PKG@.GearUi.btn(1) + " }");
    b.appendInline("#SkyyGRPager", "Label #SkyyGRPageTxt { Anchor: (Width: 280, Height: 36); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, HorizontalAlignment: Center, VerticalAlignment: Center); }");
    b.set("#SkyyGRPageTxt.Text", "Tiers " + (start + 1) + "-" + (start + per > outs.length ? outs.length : start + per) + " of " + outs.length);
    b.appendInline("#SkyyGRPager", "TextButton #SkyyGBtnRNext { Anchor: (Width: 140, Height: 36); Text: \"Next\"; " + @PKG@.GearUi.btn(1) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRPrev", @EVD@.of("a", "rprev"));
    ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRNext", @EVD@.of("a", "rnext"));
  }
}""")
# find the open group again by its key (filters / recipes may have changed): null = gone
M(spg, r"""
public Object[] findGroup(String key) {
  if (key == null || this.cards == null) return null;
  for (int i = 0; i < this.cards.size(); i++) {
    Object[] g = (Object[]) this.cards.get(i);
    if (key.equals(g[0])) return g;
  }
  return null;
}""")
# height budget of the body (808 = 880 - 38 title - 34 padding): tabs 48 + main 662 + footer 30 + bar 58 = 798
M(spg, r"""
public void build(@REF@ ref, @UCB@ b, @UEB@ ev, @ST@ st) {
  java.util.UUID u = this.playerRef.getUuid();
  @PLA@ p = null;
  try { p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  @INV@ inv = p == null ? null : p.getInventory();
  boolean all = @PKG@.GearSmith.showAll(u);
  if (this.cat == 4 && !@PKG@.GearUi.multiTab()) this.cat = 0;
  this.al = @PKG@.GearSmith.allowed(u);
  this.hc = new java.util.HashMap();          // review fix: one have() per recipe per build
  this.cards = @PKG@.GearSmith.groups(u, this.cat, all);
  // until the player picks a category, open on the first one that has something to craft (vanilla has no craftable combat armor yet)
  for (int c = 0; c < @PKG@.GearSmith.CAT_NAME.length && this.cards.isEmpty() && !this.picked; c++) {
    if (c == 4 && !@PKG@.GearUi.multiTab()) continue;
    java.util.ArrayList g = @PKG@.GearSmith.groups(u, c, all);
    if (!g.isEmpty()) { this.cat = c; this.cards = g; }
  }
  if (this.view == 1) {
    this.grp = findGroup(this.gkey);
    if (this.grp == null) { this.view = 0; this.gkey = null; }
  }
  @PKG@.GearUi.frame(b, "Smithing", 1100, 880);
  @PKG@.GearUi.tabs(b, ev, "#SkyyGBody", 3, 1066, "Craft");
  b.appendInline("#SkyyGBody", "Group #SkyyGMain { Anchor: (Height: 662); LayoutMode: Left; Padding: (Top: 6); }");
  left(b, ev, u, all);
  b.appendInline("#SkyyGMain", @PKG@.GearUi.gap(16));
  if (this.view == 1) piecesArea(b, ev, u, inv);
  else cardsArea(b, ev, u, inv);
  boolean rq = @PKG@.GearSmith.requip();
  boolean to = @PKG@.GearSmith.toRequip(u);
  b.appendInline("#SkyyGBody", "Label #SkyyGFoot { Anchor: (Height: 30); Text: \"\"; Style: (FontSize: 15, TextColor: #96a9be, VerticalAlignment: Center); }");
  b.set("#SkyyGFoot.Text", "Crafted gear goes to: " + (rq ? (to ? "Requip (inventory if it is full)" : "your inventory") : "your inventory (Requip is not loaded)") + "   -   Materials: inventory, then your bags" + (this.al == null ? "   -   crafting waits for SkyySacks 0.7.17" : ""));
  boolean menu = @PKG@.Gear.bget("config:def:SkyyMenu") != null;
  b.appendInline("#SkyyGBody", "Group #SkyyGBar { Anchor: (Height: 58); LayoutMode: Left; Padding: (Top: 10); }");
  b.appendInline("#SkyyGBar", "Label #SkyyGInfo { Anchor: (Width: 700, Height: 44); Text: \"\"; Style: (FontSize: 16, RenderBold: true, TextColor: " + @PKG@.GearUi.infoColor(this.info) + ", VerticalAlignment: Center, ShrinkTextToFit: true, MinShrinkTextToFitFontSize: 11); }");
  b.set("#SkyyGInfo.Text", @PKG@.GearUi.infoText(this.info));
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnRefresh { Anchor: (Width: 170, Height: 44); Text: \"Refresh\"; " + @PKG@.GearUi.btn(1) + " }");
  b.appendInline("#SkyyGBar", "Label { Anchor: (Width: 12, Height: 44); Text: \"\"; }");
  b.appendInline("#SkyyGBar", "TextButton #SkyyGBtnBack { Anchor: (Width: 170, Height: 44); Text: \"" + (menu ? "Back" : "Close") + "\"; " + @PKG@.GearUi.btn(2) + " }");
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnRefresh", @EVD@.of("a", "refresh"));
  ev.addEventBinding(@BT@.Activating, "#SkyyGBtnBack", @EVD@.of("a", "back"));
}""")
# the shared click guards: false = refused (this.info says why)
M(spg, r"""
public boolean guard(java.util.UUID u, String tok) {
  long now = System.currentTimeMillis();
  if (now - this.lastClick < @PKG@.GearSmith.GAP_MS && now >= this.lastClick) { this.info = "-Wait a moment between crafts."; return false; }
  if (tok == null || !tok.equals(String.valueOf(this.token))) { this.info = "-The page changed - check it and click again."; return false; }
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - nothing was crafted. Try again in a moment."; return false; }
  String ep = @PKG@.Gear.epoch(u);
  if (!ep.equals(this.epoch)) { this.epoch = ep; this.view = 0; this.info = "-Your profile changed - pick the item again."; return false; }
  if (!@PKG@.GearSmith.due(u, now)) { this.info = "-Wait a moment between crafts."; return false; }
  this.lastClick = now;
  this.token = this.token + 1;
  return true;
}""")
M(spg, r"""
public void handleDataEvent(@REF@ ref, @ST@ st, String data) {
  try {
    if (data == null) return;
    String a = @PKG@.Gear.jsonStr(data, "a");
    if (a.length() == 0) return;
    java.util.UUID u = this.playerRef.getUuid();
    if (a.startsWith("mode:")) {
      String c = a.equals("mode:0") ? "reforge" : (a.equals("mode:1") && @PKG@.GearCfg.UP_ON ? "upgrade" : (a.equals("mode:2") && @PKG@.GearUi.multiTab() ? "multitool" : null));
      if (c != null) {
        try { @CMGR@.get().handleCommand(this.playerRef, c); } catch (Throwable t1) { @PKG@.Gear.warn("smithing page: the " + c + " tab failed: " + t1); }
      }
      return;
    }
    // review fix: navigation clicks rebuild the page (have / need for every card); ones closer than NAV_MS to the last are dropped
    if (a.equals("refresh") || a.equals("prev") || a.equals("next") || a.equals("rprev") || a.equals("rnext") || a.equals("pback")
        || a.startsWith("cat:") || a.startsWith("card:") || a.startsWith("flt:") || a.startsWith("dest:")) {
      long nw = System.currentTimeMillis();
      if (nw - this.lastNav < @PKG@.GearSmith.NAV_MS && nw >= this.lastNav) return;
      this.lastNav = nw;
    }
    if (a.equals("refresh")) { this.info = ""; @PKG@.GearSmith.forceRecipes(System.currentTimeMillis()); rebuild(); return; }
    if (a.equals("back")) {
      if (@PKG@.Gear.bget("config:def:SkyyMenu") != null) {
        try { @CMGR@.get().handleCommand(this.playerRef, "skymenu"); return; } catch (Throwable t2) { }
      }
      close();
      return;
    }
    if (a.startsWith("cat:")) {
      int cc = -1;
      try { cc = Integer.parseInt(a.substring(4)); } catch (Throwable t3) { cc = -1; }
      if (cc >= 0 && cc < @PKG@.GearSmith.CAT_NAME.length && (cc != 4 || @PKG@.GearUi.multiTab())) { this.picked = true; this.cat = cc; this.view = 0; this.gkey = null; this.pageNo = 0; this.info = ""; }
      rebuild();
      return;
    }
    if (a.equals("prev")) { this.pageNo--; rebuild(); return; }
    if (a.equals("next")) { this.pageNo++; rebuild(); return; }
    if (a.equals("rprev")) { this.rowPage--; rebuild(); return; }
    if (a.equals("rnext")) { this.rowPage++; rebuild(); return; }
    if (a.equals("pback")) { this.view = 0; this.gkey = null; rebuild(); return; }
    if (a.startsWith("flt:")) { @PKG@.GearSmith.setPref(u, "gear.smithShowAll", a.equals("flt:1")); this.pageNo = 0; rebuild(); return; }
    if (a.startsWith("dest:")) {
      if (a.equals("dest:1") && !@PKG@.GearSmith.requip()) this.info = "-Requip is not loaded on this server - crafted gear goes to your inventory.";
      else { @PKG@.GearSmith.setPref(u, "gear.smithToRequip", a.equals("dest:1")); this.info = "=Crafted gear goes to " + (a.equals("dest:1") ? "Requip." : "your inventory."); }
      rebuild();
      return;
    }
    if (a.startsWith("card:")) {
      int ci = -1;
      try { ci = Integer.parseInt(a.substring(5)); } catch (Throwable t4) { ci = -1; }
      if (ci >= 0 && this.cards != null && ci < this.cards.size()) {
        Object[] g = (Object[]) this.cards.get(ci);
        this.grp = g; this.gkey = (String) g[0]; this.view = 1; this.rowPage = 0; this.info = "";
      }
      rebuild();
      return;
    }
    @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
    @INV@ inv = p == null ? null : p.getInventory();
    if (inv == null) return;
    if (a.startsWith("craft:") || a.startsWith("craftall:")) {
      if (this.view != 1 || this.grp == null) { this.info = "-Open a set first."; rebuild(); return; }
      String[] outs = (String[]) this.grp[1];
      String[] rids = (String[]) this.grp[2];
      boolean to = @PKG@.GearSmith.toRequip(u);
      if (a.startsWith("craftall:")) {
        int gc = ((Integer) this.grp[5]).intValue();
        if (gc > 1) { this.info = "-Craft every missing piece is for armor sets - craft one tier at a time."; rebuild(); return; }
        if (!guard(u, a.substring(9))) { rebuild(); return; }
        Object[] ra = @PKG@.GearSmith.craftAll(inv, u, this.playerRef.getUsername(), rids, outs, to);
        int made = ((Integer) ra[0]).intValue();
        this.info = (made > 0 ? "+" : "-") + (String) ra[1];
        rebuild();
        return;
      }
      String[] ps = a.split(":");
      int pi = -1;
      try { pi = Integer.parseInt(ps[1]); } catch (Throwable t5) { pi = -1; }
      if (pi < 0 || pi >= rids.length || ps.length < 3) { rebuild(); return; }
      if (!guard(u, ps[2])) { rebuild(); return; }
      Object[] r = @PKG@.GearSmith.craft(inv, u, this.playerRef.getUsername(), rids[pi], to);
      int code = ((Integer) r[0]).intValue();
      this.info = (code == 1 ? "+" : "-") + (String) r[1];
      rebuild();
      return;
    }
  } catch (Throwable t) { @PKG@.Gear.warn("smithing page click failed: " + t); }
}""")
# ================================================================= /smithing (alias /smith): the hub on its Craft tab
C(smc, r"""
public SmithCmd() {
  super("smithing", "Open the Smithing page: craft gear from set cards, reforge, upgrade and merge multitools");
  setPermissionGroups(new String[] { "hytale:Adventurer" });
  addAliases(new String[] { "smith" });
}""")
M(smc, r"""
protected void execute(@CTX@ ctx, @ST@ store, @REF@ ref, @PR@ pr, @WLD@ world) {
  try {
    if (!@PKG@.GearCfg.SMITH_ON) {
      pr.sendMessage(@MSG@.raw("[Smithing] The Craft tab is switched off on this server - opening Reforge.").color(@PKG@.GearDefs.C_GOLD));
      try { @CMGR@.get().handleCommand(pr, "reforge"); } catch (Throwable t2) { }
      return;
    }
    @PLA@ p = (@PLA@) store.getComponent(ref, @PLA@.getComponentType());
    if (p == null) { pr.sendMessage(@MSG@.raw("[Smithing] no player found")); return; }
    @PKG@.GearStamp.scan(pr, p.getInventory());
    @PKG@.SmithPage page = new @PKG@.SmithPage(pr);
    p.getPageManager().openCustomPage(ref, store, page);
  } catch (Throwable t) {
    @PKG@.Gear.warn("/smithing failed: " + t);
    pr.sendMessage(@MSG@.raw("[Smithing] could not open the Smithing page - the server log has the details"));
  }
}""")
# ================================================================= SmithFn: gear:fn:smithing (mode 0) + gear:fn:classShow (mode 1)
sfn.addInterface(pool.get("java.util.function.Function"))
F(sfn, "public int mode;")
C(sfn, "public SmithFn(int mode) { this.mode = mode; }")
M(sfn, r"""
public static Object open(Object o) {
  if (!(o instanceof Object[]) || ((Object[]) o).length < 1 || !(((Object[]) o)[0] instanceof java.util.UUID)) return null;
  Object[] a = (Object[]) o;
  String tab = a.length > 1 && a[1] instanceof String ? ((String) a[1]).trim().toLowerCase() : "craft";
  String c = tab.equals("reforge") ? "reforge" : (tab.equals("upgrade") ? "upgrade" : (tab.equals("multitool") ? "multitool" : "smithing"));
  @PR@ pr = null;
  try { pr = @UNI@.get().getPlayer((java.util.UUID) a[0]); } catch (Throwable t) { pr = null; }
  if (pr == null) return Boolean.FALSE;
  try { @CMGR@.get().handleCommand(pr, c); return Boolean.TRUE; } catch (Throwable t2) { @PKG@.Gear.warnOnce("smithfn", "gear:fn:smithing could not open /" + c + ": " + t2); return Boolean.FALSE; }
}""")
M(sfn, r"""
public Object apply(Object o) {
  try {
    if (this.mode == 0) return open(o);
    if (this.mode == 1) {
      if (!(o instanceof Object[]) || ((Object[]) o).length < 2 || !(((Object[]) o)[1] instanceof String)) return null;
      Object[] a = (Object[]) o;
      java.util.UUID u = a[0] instanceof java.util.UUID ? (java.util.UUID) a[0] : null;
      return Boolean.valueOf(@PKG@.GearSmith.shows(u, (String) a[1], u == null || @PKG@.GearSmith.showAll(u)));
    }
  } catch (Throwable t) { @PKG@.Gear.warnOnce("smithfn" + this.mode, "smithing bridge function " + this.mode + " failed: " + t); }
  return null;
}""")

# ================================================================= the Reforge / Upgrade lists: IN Requip gear (header 9) + the Craft tab
F(rpg, "public java.util.ArrayList rq;")
F(rpg, "public long rqAt;")          # review fix: when this.rq was read (0 = read again)
F(rpg, "public int rqMode;")
# the Requip rows a mode may use: Object[] { eid, itemId, BD } (Reforge: forgeable; Upgrade: has a next tier), at most 60
M(rpg, r"""
public static java.util.ArrayList rqRows(java.util.UUID u, int mode) {
  java.util.ArrayList out = new java.util.ArrayList();
  String[] sp = new String[] { "armor", "items" };
  for (int k = 0; k < sp.length; k++) {
    java.util.ArrayList l = @PKG@.GearSmith.rqList(u, sp[k]);
    for (int i = 0; i < l.size() && out.size() < 60; i++) {
      Object[] e = (Object[]) l.get(i);
      String id = (String) e[1];
      boolean fit = mode == 1 ? @PKG@.GearUp.next(id) != null : @PKG@.GearData.forgeable(id);
      if (fit) out.add(e);
    }
  }
  return out;
}""")
M(rpg, r"""
public boolean rqBackable(@INV@ inv) {
  if (this.selSec < 0 || @PKG@.Gear.fn("wardrobe:fn:depositSlot") == null) return false;
  @IS@ it = @PKG@.GearStamp.at(inv, this.selSec, this.selSlot);
  return @PKG@.GearForge.same(it, this.selId, this.selFp) && @PKG@.GearData.eidOf(it) != null;
}""")
# appended to the list's own group after its inventory rows (hooked AFTER list / upList)
M(rpg, r"""
public void rqAppend(@UCB@ b, @UEB@ ev, @INV@ inv, int mode) {
  java.util.UUID u = this.playerRef.getUuid();
  long nw = System.currentTimeMillis();
  if (this.rq == null || this.rqMode != mode || nw - this.rqAt >= @PKG@.GearSmith.RQ_MS || nw < this.rqAt) {
    this.rq = rqRows(u, mode);          // review fix: wardrobe:fn:list (2 spaces) at most once per RQ_MS per page; the rows a click indexes = the rows shown
    this.rqAt = nw;
    this.rqMode = mode;
  }
  boolean back = rqBackable(inv);
  if (this.rq.isEmpty() && !back) return;
  boolean t = @PKG@.GearUi.tex();
  b.appendInline("#SkyyGList", "Label #SkyyGRqH { Anchor: (Height: 34); Padding: (Top: 6); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: #ffffff, VerticalAlignment: Center); }");
  b.set("#SkyyGRqH.Text", "In Requip (" + this.rq.size() + ") - click one to take it out");
  if (back) {
    b.appendInline("#SkyyGList", "TextButton #SkyyGRqBack { Anchor: (Height: 40); Text: \"Return to Requip\"; " + @PKG@.GearUi.btn(1) + " }");
    ev.addEventBinding(@BT@.Activating, "#SkyyGRqBack", @EVD@.of("a", "rqback"));
  }
  int max = t ? 60 : 3;
  for (int i = 0; i < this.rq.size() && i < max; i++) {
    Object[] e = (Object[]) this.rq.get(i);
    String id = (String) e[1];
    @BD@ d = null;
    try { d = @PKG@.GearData.effective(id, (@BD@) e[2]); } catch (Throwable x) { d = null; }
    int r = d == null ? 0 : @PKG@.GearData.rarity(d);
    String rid = "#SkyyGRq" + i;
    b.appendInline("#SkyyGList", "Button " + rid + " { Anchor: (Height: 44); LayoutMode: Left; Padding: (Full: 6); " + @PKG@.GearUi.rowStyle(false) + " ItemIcon { Anchor: (Width: 32, Height: 32); ItemId: \"" + @PKG@.Gear.safe(id) + "\"; } Label #SkyyGRqName" + i + " { Anchor: (Width: 262); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 15, RenderBold: true, TextColor: " + rarHex(r) + ", VerticalAlignment: Center); } Label #SkyyGRqSub" + i + " { Anchor: (Width: 140); Padding: (Horizontal: 10, Vertical: 5); Text: \"\"; Style: (FontSize: 14, TextColor: #ffffff(0.6), HorizontalAlignment: End, VerticalAlignment: Center); } }");
    b.set("#SkyyGRqName" + i + ".Text", d == null ? @PKG@.Gear.itemName(id) : @PKG@.GearView.nameText(id, d));
    b.set("#SkyyGRqSub" + i + ".Text", "Requip - Lv " + @PKG@.GearLevel.level(id, d));
    b.appendInline("#SkyyGList", "Group { Anchor: (Height: 2); Background: #ffffff(0.6); }");
    ev.addEventBinding(@BT@.Activating, rid, @EVD@.of("a", "rq:" + i));
  }
}""")
# the Requip clicks + the Craft tab (in front of the 0.2.22 tab / upgrade hook); true = handled
M(rpg, r"""
public boolean rqEvent(@REF@ ref, @ST@ st, String data) {
  if (data == null) return false;
  String a = @PKG@.Gear.jsonStr(data, "a");
  if (a.equals("mode:3")) return @PKG@.GearSmith.craftTab(data, this.playerRef);
  if (!a.startsWith("rq:") && !a.equals("rqback")) return false;
  @PLA@ p = (@PLA@) st.getComponent(ref, @PLA@.getComponentType());
  @INV@ inv = p == null ? null : p.getInventory();
  if (inv == null) return true;
  java.util.UUID u = this.playerRef.getUuid();
  if (@PKG@.Gear.busy(u)) { this.info = "-Your profile is still loading - try again in a moment."; rebuild(); return true; }
  if (a.equals("rqback")) {
    if (!rqBackable(inv)) { this.info = "-Nothing from Requip is on the anvil."; rebuild(); return true; }
    String nm = @PKG@.Gear.itemName(this.selId);
    Object r1 = null;
    try { r1 = @PKG@.Gear.fn("wardrobe:fn:depositSlot").apply(new Object[] { u, @PKG@.GearSmith.secName(this.selSec), Integer.valueOf(this.selSlot) }); } catch (Throwable t) { r1 = "refused:" + t; }
    String rs = r1 == null ? "refused:no answer" : String.valueOf(r1);
    if (rs.startsWith("eid:") || rs.startsWith("kind:")) { clearSel(); this.upMade = null; this.upMadeId = null; this.rqAt = 0L; this.info = "+" + nm + " went back into Requip."; }
    else this.info = "-Requip did not take it: " + (rs.startsWith("refused:") ? rs.substring(8) : rs);
    rebuild();
    return true;
  }
  int i = -1;
  try { i = Integer.parseInt(a.substring(3)); } catch (Throwable t2) { i = -1; }
  if (i < 0 || this.rq == null || i >= this.rq.size()) return true;
  Object[] e = (Object[]) this.rq.get(i);
  String eid = (String) e[0];
  String id = (String) e[1];
  java.util.function.Function f = @PKG@.Gear.fn("wardrobe:fn:fetch");
  if (f == null) { this.info = "-Requip is not loaded on this server."; rebuild(); return true; }
  Object r = null;
  try { r = f.apply(new Object[] { u, eid }); } catch (Throwable t3) { r = "Requip did not answer (" + t3 + ")"; }
  this.rqAt = 0L;
  if (!"ok".equals(r)) { this.info = "-" + (r == null ? "Requip did not answer." : String.valueOf(r)); rebuild(); return true; }
  int[] at = @PKG@.GearSmith.findEid(inv, eid);
  boolean on = false;
  if (at != null) on = this.mode == 1 ? upPick(inv, at[0], at[1]) : pick(inv, at[0], at[1]);
  this.info = "=" + @PKG@.Gear.itemName(id) + " was taken out of Requip" + (on ? " and is on the anvil (your loadouts still point at it)." : " - it is in your inventory.");
  rebuild();
  return true;
}""")
rpg.getDeclaredMethod("list").insertAfter(J("{ try { rqAppend($1, $2, $3, 0); } catch (Throwable tq) { @PKG@.Gear.warnOnce(\"rqrows\", \"the Requip rows of the Reforge list failed: \" + tq); } }"))
rpg.getDeclaredMethod("upList").insertAfter(J("{ try { rqAppend($1, $2, $3, 1); } catch (Throwable tq) { @PKG@.Gear.warnOnce(\"rqrows\", \"the Requip rows of the Upgrade list failed: \" + tq); } }"))
rpg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ try { if (rqEvent($1, $2, $3)) return; } catch (Throwable tr) { @PKG@.Gear.warn(\"reforge page Requip / Craft click failed: \" + tr); return; } }"))
mpg.getDeclaredMethod("handleDataEvent").insertBefore(J("{ if (@PKG@.GearSmith.craftTab($3, this.playerRef)) return; }"))
# build check: the Craft tab's height budget (spec 4.2: tabs 48 + main 662 + footer 30 + bar 58 inside the 808 px body of the 880 frame;
# the card rows 2 x 300 + 12 + pager 40 = 652 of the main's 656; the left column; the piece page) and the card / figure widths
_BODY_H = 880 - 38 - 2 * 17
assert 48 + 662 + 30 + 58 <= _BODY_H, "Craft tab body %d > %d" % (48 + 662 + 30 + 58, _BODY_H)
assert 2 * 300 + 12 + 40 <= 662 - 6 and 44 + 600 <= 662 - 6 and 40 + 444 + 56 + 44 <= 600 - 6, "Craft tab: cards / piece page do not fit"
assert 3 * 266 + 2 * 16 == 830 and 220 + 16 + 830 == 1100 - 2 * 17, "Craft tab widths"
assert 6 + 24 + 18 + 192 + 18 + 18 + 18 + 6 == 300 and 3 * 64 == 192, "card 266 x 300"
assert 28 + 4 * 46 + 46 + 10 + 26 + 22 + 40 + 6 + 40 + 10 + 24 + 40 + 6 + 40 <= 656, "Craft tab left column"
assert 56 + 8 + 330 + 8 + 160 <= 568 and 250 + 12 + 568 <= 830, "piece rows"
print("0.2.23 smithing hub: Craft tab body %d of %d px, cards 3 x 2 of 266 x 300, piece page 6 rows of 74 px" % (48 + 662 + 30 + 58, _BODY_H))

'''
rep('''# ####################################################################################################################################
# PART B (2/2): /identify (spec 5.7, pages 5.8).''', SMITH_PY + '''# ####################################################################################################################################
# PART B (2/2): /identify (spec 5.7, pages 5.8).''')

# ================================================================================================================ 6. setup + ready line + class list
rep('''  getCommandRegistry().registerCommand(new @PKG@.UpCmd());             // 0.2.22: /upgrade = the Reforge page on its Upgrade tab''',
    '''  getCommandRegistry().registerCommand(new @PKG@.UpCmd());             // 0.2.22: /upgrade = the Reforge page on its Upgrade tab
  getCommandRegistry().registerCommand(new @PKG@.SmithCmd());          // 0.2.23: /smithing (/smith) = the hub on its Craft tab''')
rep('''  br.put("gear:tiers", @PKG@.GearDefs.TIERS);''', '''  br.put("gear:tiers", @PKG@.GearDefs.TIERS);
  br.put("gear:fn:smithing", new @PKG@.SmithFn(0));        // 0.2.23: open the hub on a tab (SkyyMenu's Smithing tile)
  br.put("gear:fn:classShow", new @PKG@.SmithFn(1));       // 0.2.23: the Craft tab's class filter (SkyySacks /craft Smithing tab)''')
rep('''  @PKG@.Gear.regSetting("gear.critFx", "Crit effects", "combat", true, "CRIT! popup, sparks and the red number on your critical hits");''',
    '''  @PKG@.Gear.regSetting("gear.critFx", "Crit effects", "combat", true, "CRIT! popup, sparks and the red number on your critical hits");
  @PKG@.Gear.regSetting("gear.smithShowAll", "Smithing: show every class", "combat", false, "The Smithing Craft tab shows gear for every class, not only yours");
  @PKG@.Gear.regSetting("gear.smithToRequip", "Smithing: craft into Requip", "combat", true, "Gear crafted on the Smithing page goes into Requip (else your inventory)");''')
rep('''log("[SkyyGear] @VER@ ready - /reforge, /identify, /multitool, /upgrade, /gear (admin:''', '''log("[SkyyGear] @VER@ ready - /smithing, /reforge, /identify, /multitool, /upgrade, /gear (admin:''')
rep('''+ @PKG@.GearUp.statusText() + "; gear:fn:curve,''', '''+ @PKG@.GearUp.statusText() + "; " + @PKG@.GearSmith.statusText() + "; gear:fn:curve,''')
rep('''gear:fn:tradeable, gear:fn:utfx; wand / staff''', '''gear:fn:tradeable, gear:fn:utfx, gear:fn:smithing, gear:fn:classShow; wand / staff''')
rep('''+ UB_CLASSES + TOOL_MULTI_CLASSES + MERGE_CLASSES + UP_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''',
    '''+ UB_CLASSES + TOOL_MULTI_CLASSES + MERGE_CLASSES + UP_CLASSES + SMITH_CLASSES
assert len(set(str(c.getName()) for c in ALL)) == len(ALL), "a class is listed twice"''')

# ================================================================================================================ 7. manifest
rep('''the Reforge page's Upgrade tab (/upgrade) turns an item into its next tier (Soul Cages) with the same rarity and lines; item names end with their level''',
    '''the Reforge page's Upgrade tab (/upgrade) turns an item into its next tier (Soul Cages) with the same rarity and lines; item names end with their level; /smithing = one page with Craft (set cards, class filter, crafts into Requip), Reforge, Upgrade and Multitool tabs''')

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", DST)
