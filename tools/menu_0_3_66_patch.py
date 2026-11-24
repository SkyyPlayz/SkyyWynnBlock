"""Derive SkyyMenu/build_skyymenu_0.3.66.py + SkyyMenu/test_skyymenu_0.3.66.py from the SET pin SkyyMenu 0.3.65 (generated - never re-run
its patch). Run:  python tools/menu_0_3_66_patch.py   then   python SkyyMenu/build_skyymenu_0.3.66.py   (never --deploy)
Check: python SkyyMenu/test_skyymenu_0.3.66.py
Edit THIS patch, never the generated files. Every anchor is asserted once. Line endings kept. --out <build path> [--test-out <test path>]
writes elsewhere (the harness re-run).

0.3.66 (2026-11-22, round furn2) = FIXES FROM SKYY'S 11-22 TEST OF THE NEW INVENTORY. Skyy's words (docs/answered/ui.md 2026-11-22):
  "i want a normal easy way to access this besides the right now tab." (the Furnace panel) / "the tool tips look funny, they losty all the
  color coding" / "and it doesnt show the legendary color in the new inventory" / "i dont see Beastmaster in the side bar." / "the deposit
  button isnt working" / "when everything is in the new system id like to disable the old menu compleatly, so instead of adding things like
  the full tree button, just build it all into the new system" (so: no new Full page / old-page link in this round).
  1. FURNACE + TANNING TABS. ROOT CAUSE: the bench tab row was cut at 8 tabs (InvData.BMAX) and the Furnace / Tanning tabs were added LAST
     (and only with the SkyySacks craft bridges) - with Crafting + 7 recipe benches (Armor, Furniture, Arcane, Salvage, Farming, Weapon,
     Builders) they were always the ones cut. FIX: Crafting first, the recipe benches, then Furnace + Tanning ALWAYS (pinned at the right end,
     never cut); when the row has no room (it fits 8 tabs of 60 px on the craft panel, 7 on the Furnace panel) the middle benches page with a
     "More" button (cycles, wraps) - Crafting / Furnace / Tanning never page away; no tab is narrower than today's 60 px (no overlap at
     1080p). Both rows (craft panel + Furnace panel) draw through ONE method (benchRow). Furnace / Tanning open the SAME panel 'f' as
     Right now > Go (0.3.56; without SkyySacks' furnace bridge: the pack's own page, as before).
  2. TOOLTIP COLOURS. ROOT CAUSE: InvPage.slot() copies a stack's ItemDisplayMetadata (the SkyyGear / pack tooltip: name + description as
     coloured Message spans) into the ItemGridSlot through flat(), which keeps only the raw text - every colour / bold / italic span was
     dropped, and a translation key came out as "[server.items...]". FIX: mark() turns the Message tree into the client's tooltip markup
     (<color is="#hex">, <b>, <i> - the same tags the deployed menu tooltips and TheArmoryMod's slot descriptions use) and resolves keys to
     their English text (InvCraft.tr) - every grid that shows a real stack (bag, hotbar, armour, off-hand, the skill page's worn armour)
     goes through slot(), so every tab screen is fixed at once.
  3. RARITY COLOUR ON SLOTS. ROOT CAUSE: the grid copy must be a NEW stack (HANDOFF 2: a QualityOverride in a grid slot disconnects the
     client), so a stack-stamped rarity (SkyyGear rolled gear: QualityOverride = its Skyy_Gear_* quality; SkyyAccessories charms) reached
     the client as the base item's quality - no frame, a plain title. FIX (only when the stack's quality differs from the item's own; the
     client still draws an item's OWN quality itself): the slot's Background = that quality's colour (the engine ItemQuality TextColor,
     read-only - the existing rarity source) mixed 35 % into the Skyglass slot colour, the vanilla quality background skipped for it, and
     the tooltip TITLE wears the colour (the name's own colour when the metadata name has one, else the quality colour). A white / grey
     (Common) quality gets no colour. Server Setup switch menu.inventory.rarity (default ON, live) turns BOTH the slot colour and the
     coloured title off at once (the description colours stay - they are proven).
  4. BEASTMASTERY in the Skills tab's SKILLS side bar (13 skills, 7 rows) and in the inventory's skill grid (13 cells, a 5th row).
     ROOT CAUSE: both lists were fixed at 12 (SkillData ORDER had no Beastmastery; the inventory grid = skill:fn:prog's class + 11 skills,
     which has no Beastmastery line). FIX: Beastmastery appended (its tree = SkyyTrees' Beastmastery tree, no tool, no shard); its level
     falls back to skill:fn:level {UUID, "Beastmastery"} when skill:<uuid> / skill:fn:prog do not carry it (SkyySkills 0.4.73: neither
     does); its cell shows the level (no XP bar: no into / need source) and opens its skill page.
  5. POCKET DEPOSIT. FINDINGS: Skyy's live player file (copied to scratch, read only) holds the seed bags as PLAIN stacks (no metadata) -
     metadata was not the cause. sacks:fn:pocket "dep" deposits the PICKED item only; with none of the picked item carried it answers
     "You carry none of it (plain stacks only)" and nothing moves - the panel showed seed bags the player carried (Carrot / Lettuce / Wheat:
     x100 / x85 / x10) while another item was picked, and nothing on the panel could put THEM in. FIX (Menu only, SkyySacks unchanged): the
     panel counts what you carry (storage, hotbar, backpack - SkyySacks' Deposit containers) before calling: the picked item carried =
     the same call as before; not carried (or nothing picked) = a clear one-line reason, and when you carry other items of THIS pocket
     (sacks:fn:catOf) a second Deposit click within 10 s puts each of them in through the Void's own Deposit (sacks:fn:pocket dep, one call
     per item, its rules: plain stacks only, counted removal, category room); stacks with extra data (enchants / wear / an owner) are never
     sent and the reason says so.
  No new class, command, system, saved data, picture or lang key; one new Server Setup row (menu.inventory.rarity, a NEW key - absent =
  ON, so no migration). ROLLBACK to 0.3.65: safe alone (nothing saved; the row's key stays in config.properties and is ignored).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

MOD = os.path.join(ROOT, "SkyyMenu")
P = G.Patch(os.path.join(MOD, "build_skyymenu_0.3.65.py"), os.path.join(MOD, "build_skyymenu_0.3.66.py"))
T = G.Patch(os.path.join(MOD, "test_skyymenu_0.3.65.py"), os.path.join(MOD, "test_skyymenu_0.3.66.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
    T.dst = os.path.abspath(sys.argv[sys.argv.index("--test-out") + 1]) if "--test-out" in sys.argv else None
assert P.has('VERSION = "0.3.65"\n') and P.has("tools/menu_0_3_65_patch.py") and P.has("SkyyInvDrop")
assert not P.has("benchRow"), "not the generated SkyyMenu 0.3.65 script"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")

# ======================================================================= the BUILD script
P.rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.65: DROPPING FROM THE NEW INVENTORY''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.66: SKYY'S 11-22 INVENTORY FIXES: Furnace + Tanning bench tabs always shown (pinned; the middle benches page with More); tooltips keep
       their colours (Message spans -> markup); rolled gear / charms show their rarity colour on the slot + the title (Server Setup
       menu.inventory.rarity); Beastmastery in the Skills side bar + the inventory skill grid; the pocket Deposit says why and offers what
       you carry for that pocket (notes: tools/menu_0_3_66_patch.py). CHECKED: see SkyyMenu/test_skyymenu_0.3.66.py.
0.3.65: DROPPING FROM THE NEW INVENTORY''')
P.rep('VERSION = "0.3.65"\n', 'VERSION = "0.3.66"\n')

# ---------- engine tokens (2, 3)
P.rep('''    "I18N": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
}''', '''    "I18N": "com.hypixel.hytale.server.core.modules.i18n.I18nModule",
    # 0.3.66: the slot's rarity colour + the tooltip markup (read only)
    "IQL":  "com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality",
    "PCOL": "com.hypixel.hytale.protocol.Color",
    "FMSG": "com.hypixel.hytale.protocol.FormattedMessage",
    "PSTY": "com.hypixel.hytale.server.core.ui.PatchStyle",
    "UVAL": "com.hypixel.hytale.server.core.ui.Value",
}''')
P.rep('''print("0.3.52 crafting: every engine member probed (CraftingManager.craftItem's steps, the events, giveOutput's container pick)")
''', '''print("0.3.52 crafting: every engine member probed (CraftingManager.craftItem's steps, the events, giveOutput's container pick)")
# 0.3.66: every engine member the slot colour + tooltip markup use (ItemGridSlot Background / SkipItemQualityBackground = its own codec keys)
for c, m in ((T["IGS"], "setBackground"), (T["IGS"], "setSkipItemQualityBackground"), (T["PSTY"], "setColor"), (T["UVAL"], "of"),
             (T["IS"], "getQualityIndex"), (T["ITEM"], "getQualityIndex"), (T["IQL"], "getAssetMap"), (T["IQL"], "getTextColor"),
             (T["PCOL"], "red"), (T["PCOL"], "green"), (T["PCOL"], "blue"), (T["MSG"], "getColor"), (T["MSG"], "getFormattedMessage"),
             (T["FMSG"], "bold"), (T["FMSG"], "italic"), ("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap", "getAsset")):
    B.probe(pool, c, m)
assert "(Lcom/hypixel/hytale/server/core/ui/Value;)Lcom/hypixel/hytale/server/core/ui/ItemGridSlot;" in _isig(T["IGS"], "setBackground"), "0.3.66: ItemGridSlot.setBackground(Value)"
assert "(Lcom/hypixel/hytale/server/core/ui/Value;)Lcom/hypixel/hytale/server/core/ui/PatchStyle;" in _isig(T["PSTY"], "setColor"), "0.3.66: PatchStyle.setColor(Value)"
print("0.3.66 slot colour: every engine member probed (ItemGridSlot.setBackground, PatchStyle.setColor, ItemQuality.getTextColor, Message spans)")
''')

# ---------- (1) the bench row: Furnace + Tanning pinned, the middle pages (sizes; one run-time More button)
P.rep('''IV_BMAX = 8
''', '''IV_BMAX = 8
IV_TABMIN, IV_NAVW = 60, 64   # 0.3.66: no bench tab narrower than today's 8-tab width (60 px); the More button
''')
P.rep('''for _mk in (IV_BENCH_BTN.replace("{I}", "0").replace("{W}", "90").replace("{S}", IV_ST_TAB), IV_NOW_ROW.replace("{I}", "0"), IV_NOW_EMPTY):
    SUI.check_markup(_mk, prefix=IV, kit_paths=True)
    assert "@" not in _mk and "\\n" not in _mk, "0.3.52: a runtime markup line Java can hold"
''', '''for _mk in (IV_BENCH_BTN.replace("{I}", "0").replace("{W}", "90").replace("{S}", IV_ST_TAB), IV_NOW_ROW.replace("{I}", "0"), IV_NOW_EMPTY):
    SUI.check_markup(_mk, prefix=IV, kit_paths=True)
    assert "@" not in _mk and "\\n" not in _mk, "0.3.52: a runtime markup line Java can hold"
IV_BENCH_NAV = IV_BENCH_BTN.replace("{I}", "M").replace("{W}", str(IV_NAVW)).replace("{S}", IV_ST_TAB)   # 0.3.66: the bench row's More button
SUI.check_markup(IV_BENCH_NAV, prefix=IV, kit_paths=True)
assert "@" not in IV_BENCH_NAV and "\\n" not in IV_BENCH_NAV and SUI.text_width("More", 14, bold=True) <= IV_NAVW - 12, "0.3.66: the More button"
''')
P.rep('''IV_RUNTIME_MAX += IV_SKN + 1   # 0.3.56: the skill XP bar fills + the class XP bar fill
''', '''IV_RUNTIME_MAX += IV_SKN + 1   # 0.3.56: the skill XP bar fills + the class XP bar fill
IV_RUNTIME_MAX += 1            # 0.3.66: the bench row's More button (the tabs stay <= IV_BMAX)
''')
P.rep('''               ("VCN", IV_VCN), ("BW_ALL", IV_BW_ALL[0])):
    F(idat, "public static final int %s = %d;" % (_n, _v))
''', '''               ("VCN", IV_VCN), ("BW_ALL", IV_BW_ALL[0]), ("TABMIN", IV_TABMIN), ("NAVW", IV_NAVW)):   # 0.3.66: + TABMIN, NAVW
    F(idat, "public static final int %s = %d;" % (_n, _v))
F(idat, "public static final String BENCH_NAV = %s;" % jstr(IV_BENCH_NAV))   # 0.3.66
# 0.3.66: the bench rows' capacity (BW_ALL craft panel, FX_BW Furnace panel): all tabs at >= TABMIN, else Crafting + a page + More + the 2 pinned
for _w in (IV_BW_ALL[0], IV_FX_BW[0]):
    assert (_w + 4) // (IV_TABMIN + 4) <= IV_BMAX and (_w - IV_NAVW - 4) // (IV_TABMIN + 4) >= 4, ("0.3.66: a bench row pages at least 1 bench", _w)
''')
# the bench list: Crafting, the recipe benches (never a processing bench), then Furnace + Tannery ALWAYS (pinned last); the row = benchRow
P.rep('''  java.util.ArrayList bs = new java.util.ArrayList();
  bs.add("Crafting");
  for (int i = 0; i < all.size(); i++) {
    String bk = @PKG@.InvCraft.benchKey(@PKG@.InvCraft.recipe((String) all.get(i)));
    if (bk != null && !bs.contains(bk)) bs.add(bk);
  }
  if (@PKG@.InvCraft.voidMode()) { if (!bs.contains("Furnace")) bs.add("Furnace"); if (!bs.contains("Tannery")) bs.add("Tannery"); }
  while (bs.size() > @PKG@.InvData.BMAX) bs.remove(bs.size() - 1);
  if (!bs.contains(this.cbench) || @PKG@.InvCraft.processing(this.cbench)) this.cbench = "Crafting";
  this.cbenches = bs;
  int bw = (@PKG@.InvData.BW_ALL - 4 * bs.size()) / bs.size();
  if (bw > 120) bw = 120;
  for (int i = 0; i < bs.size(); i++) {
    String bk = (String) bs.get(i);
    b.appendInline("#SkyyInvCfB", @PKG@.InvData.BENCH_BTN.replace("{I}", String.valueOf(i)).replace("{W}", String.valueOf(bw)).replace("{S}", bk.equals(this.cbench) ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvBt" + i + ".Text", @PKG@.InvCraft.benchLabel(bk));
    ev.addEventBinding(@BT@.Activating, "#SkyyInvBt" + i, @EVD@.of("a", "cb:" + i));
  }
''', '''  java.util.ArrayList bs = new java.util.ArrayList();
  bs.add("Crafting");
  for (int i = 0; i < all.size() && bs.size() < 40; i++) {
    String bk = @PKG@.InvCraft.benchKey(@PKG@.InvCraft.recipe((String) all.get(i)));
    if (bk != null && !bs.contains(bk) && !@PKG@.InvCraft.processing(bk)) bs.add(bk);
  }
  bs.add("Furnace");   // 0.3.66 (Skyy 11-22 "a normal easy way to access this"): ALWAYS, pinned last - never cut, never paged away
  bs.add("Tannery");
  if (!bs.contains(this.cbench) || @PKG@.InvCraft.processing(this.cbench)) this.cbench = "Crafting";
  this.cbenches = bs;
  benchRow(b, ev, "#SkyyInvCfB", @PKG@.InvData.BW_ALL, this.cbench);
''')
P.rep('''  if (bs == null || bs.size() == 0) { bs = new java.util.ArrayList(); bs.add("Crafting"); bs.add(this.fbench); this.cbenches = bs; }
  int bw = (@PKG@.InvData.FX_BW - 4 * bs.size()) / bs.size();
  if (bw > 120) bw = 120;
  for (int i = 0; i < bs.size(); i++) {
    String bk = (String) bs.get(i);
    b.appendInline("#SkyyInvFxB", @PKG@.InvData.BENCH_BTN.replace("{I}", String.valueOf(i)).replace("{W}", String.valueOf(bw)).replace("{S}", bk.equals(this.fbench) ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvBt" + i + ".Text", @PKG@.InvCraft.benchLabel(bk));
    ev.addEventBinding(@BT@.Activating, "#SkyyInvBt" + i, @EVD@.of("a", "cb:" + i));
  }
''', '''  if (bs == null || bs.size() < 3) { bs = new java.util.ArrayList(); bs.add("Crafting"); bs.add("Furnace"); bs.add("Tannery"); this.cbenches = bs; }   // 0.3.66: both pinned
  benchRow(b, ev, "#SkyyInvFxB", @PKG@.InvData.FX_BW, this.fbench);
''')
P.rep('''# the craft panel: bench tabs (run time), the filtered recipe page (tier, then name), the page number, the info line, the toggle, the detail
''', '''# ---- 0.3.66: THE BENCH ROW (craft panel + Furnace panel): every tab when they fit at >= TABMIN px; else Crafting, a page of the middle
# benches, More (next page, wraps), then Furnace + Tannery (the list's last two - pinned, never paged away). Tab ids = the bench's index in
# cbenches (cb:<i> = bench(i), unchanged); at most BMAX tabs + More are drawn.
F(ipg, "public int cboff;")
F(ipg, "public int cbk;")
F(ipg, "public static volatile int MORES = 0;")
M(ipg, r"""
public void benchRow(@UCB@ b, @UEB@ ev, String parent, int rowW, String sel) {
  java.util.ArrayList bs = this.cbenches;
  int n = bs == null ? 0 : bs.size();
  if (n == 0) return;
  int[] vis = new int[n + 1];
  int nv = 0;
  boolean more = false;
  int cap = (rowW + 4) / (@PKG@.InvData.TABMIN + 4);
  if (n <= cap || n < 4) {
    for (int i = 0; i < n; i++) { vis[nv] = i; nv = nv + 1; }
  } else {
    int t = (rowW - @PKG@.InvData.NAVW - 4) / (@PKG@.InvData.TABMIN + 4);
    int k = t - 3;
    if (k < 1) k = 1;
    int mid = n - 3;
    if (this.cboff < 0 || this.cboff >= mid) this.cboff = 0;
    this.cbk = k;
    vis[nv] = 0; nv = nv + 1;
    for (int j = this.cboff; j < this.cboff + k && j < mid; j++) { vis[nv] = 1 + j; nv = nv + 1; }
    vis[nv] = n - 2; nv = nv + 1;
    vis[nv] = n - 1; nv = nv + 1;
    more = true;
  }
  int bw = more ? (rowW - @PKG@.InvData.NAVW - 4) / nv - 4 : (rowW - 4 * nv) / nv;
  if (bw > 120) bw = 120;
  for (int q = 0; q < nv; q++) {
    if (more && q == nv - 2) {
      b.appendInline(parent, @PKG@.InvData.BENCH_NAV);
      b.set("#SkyyInvBtM.Text", "More");
      ev.addEventBinding(@BT@.Activating, "#SkyyInvBtM", @EVD@.of("a", "cbm"));
    }
    int i = vis[q];
    String bk = (String) bs.get(i);
    b.appendInline(parent, @PKG@.InvData.BENCH_BTN.replace("{I}", String.valueOf(i)).replace("{W}", String.valueOf(bw)).replace("{S}", bk.equals(sel) ? @PKG@.InvData.ST_TABSEL : @PKG@.InvData.ST_TAB));
    b.set("#SkyyInvBt" + i + ".Text", @PKG@.InvCraft.benchLabel(bk));
    ev.addEventBinding(@BT@.Activating, "#SkyyInvBt" + i, @EVD@.of("a", "cb:" + i));
  }
}""")
# the craft panel: bench tabs (run time), the filtered recipe page (tier, then name), the page number, the info line, the toggle, the detail
''')
P.rep('''  this.mode = "c";   // 0.3.56: the Crafting / a bench tab from the Furnace panel = the craft panel again
  this.cbench = bk;
  this.cpage = 0;
  this.csel = null;
  this.cnote = "";
  redraw();
}""")
''', '''  this.mode = "c";   // 0.3.56: the Crafting / a bench tab from the Furnace panel = the craft panel again
  this.cbench = bk;
  this.cpage = 0;
  this.csel = null;
  this.cnote = "";
  redraw();
}""")
# 0.3.66: More = the next page of the middle bench tabs (wraps to the first); the panel shown stays
M(ipg, r"""
public void benchMore() {
  int n = this.cbenches == null ? 0 : this.cbenches.size();
  int mid = n - 3;
  MORES = MORES + 1;
  this.cboff = this.cboff + (this.cbk < 1 ? 1 : this.cbk);
  if (mid <= 0 || this.cboff >= mid) this.cboff = 0;
  redraw();
}""")
''')
P.rep('''    if (a.startsWith("cb:")) { int w = -1; try { w = Integer.parseInt(a.substring(3)); } catch (Throwable t) { w = -1; } bench(w); return; }
''', '''    if (a.startsWith("cb:")) { int w = -1; try { w = Integer.parseInt(a.substring(3)); } catch (Throwable t) { w = -1; } bench(w); return; }
    if (a.equals("cbm")) { benchMore(); return; }   // 0.3.66: the bench row's More
''')

# ---------- (2) + (3) the grid copy keeps the tooltip colours; a stack-stamped rarity = the slot colour + the coloured title
P.rep('''# HANDOFF 2: the grid copy carries NO metadata AND no quality override (a NEW stack; the client has no QualityOverride / metadata codec);
''', '''# ---- 0.3.66 (Skyy 11-22 "the tool tips look funny, they losty all the color coding"): a Message tree -> the client's tooltip markup
# (<color is="#hex">, <b>, <i> - the tags the menu tooltips and TheArmoryMod's slot descriptions use); a key -> its English text
M(ipg, r"""
public static String mark(@MSG@ m, int depth) {
  if (m == null || depth > 24) return "";
  StringBuilder sb = new StringBuilder();
  String r = m.getRawText();
  java.util.List c = m.getChildren();
  if (r != null) sb.append(r);
  else if (m.getMessageId() != null && (c == null || c.isEmpty())) {
    String tr = @PKG@.InvCraft.tr(m.getMessageId());
    sb.append(tr != null ? tr : "[" + m.getMessageId() + "]");
  }
  for (int i = 0; c != null && i < c.size(); i++) {
    Object o = c.get(i);
    if (o instanceof @MSG@) sb.append(mark((@MSG@) o, depth + 1));
  }
  if (sb.length() == 0) return "";
  String col = null;
  boolean bo = false;
  boolean it = false;
  try {
    col = m.getColor();
    @FMSG@ f = m.getFormattedMessage();
    if (f != null) {
      bo = f.bold != null && f.bold.booleanValue();
      it = f.italic != null && f.italic.booleanValue();
    }
  } catch (Throwable t) { }
  String s = sb.toString();
  if (it) s = "<i>" + s + "</i>";
  if (bo) s = "<b>" + s + "</b>";
  if (col != null && col.length() == 7 && col.charAt(0) == '#') s = "<color is=" + String.valueOf((char) 34) + col + String.valueOf((char) 34) + ">" + s + "</color>";
  return s;
}""")
# 0.3.66 (Skyy 11-22 "it doesnt show the legendary color in the new inventory"): the colour of a quality the STACK carries (QualityOverride:
# SkyyGear rolled gear, SkyyAccessories charms) - "" when the stack has the item's own quality (the client draws that itself), no such
# quality, or a white / grey (Common) one. The engine ItemQuality TextColor = the rarity colour every mod already uses (read only).
M(ipg, r"""
public static String hex2(int v) {
  String h = Integer.toHexString(v & 255);
  return h.length() < 2 ? "0" + h : h;
}""")
M(ipg, r"""
public static String qualHex(Object q) {
  if (!(q instanceof @IQL@)) return "";
  @PCOL@ c = ((@IQL@) q).getTextColor();
  if (c == null) return "";
  int r = c.red & 255;
  int g = c.green & 255;
  int b = c.blue & 255;
  if (r >= 192 && g >= 192 && b >= 192) return "";
  return "#" + hex2(r) + hex2(g) + hex2(b);
}""")
M(ipg, r"""
public static String rarHex(@IS@ s) {
  try {
    if (s == null || s.isEmpty()) return "";
    int q = s.getQualityIndex();
    @ITEM@ it = s.getItem();
    if (it != null && q == it.getQualityIndex()) return "";
    return qualHex(@IQL@.getAssetMap().getAsset(q));
  } catch (Throwable t) { return ""; }
}""")
# the slot background: the rarity colour 35 % over the Skyglass slot colour (#0f1a2c), opaque (no alpha syntax in a value)
M(ipg, r"""
public static String tint(String hex) {
  int base = 0x0f1a2c;
  int c = Integer.parseInt(hex.substring(1), 16);
  int r = (((c >> 16) & 255) * 35 + ((base >> 16) & 255) * 65) / 100;
  int g = (((c >> 8) & 255) * 35 + ((base >> 8) & 255) * 65) / 100;
  int b = ((c & 255) * 35 + (base & 255) * 65) / 100;
  return "#" + hex2(r) + hex2(g) + hex2(b);
}""")
F(ipg, "public static volatile int RARS = 0;")   # 0.3.66: slots drawn with a rarity colour (the harness counts them)
# HANDOFF 2: the grid copy carries NO metadata AND no quality override (a NEW stack; the client has no QualityOverride / metadata codec);
''')
P.rep('''  g.setItemStack(new @IS@(s.getItemId(), s.getQuantity(), s.getDurability(), s.getMaxDurability(), (@BSON@) null));
  try {
    Object o = s.getFromMetadataOrNull(@IDM@.KEYED_CODEC);
    if (o != null) {
      @IDM@ d = (@IDM@) o;
      String n = flat(d.getName());
      String de = flat(d.getDescription());
      if (n.length() > 0) g.setName(n);
      if (de.length() > 0) g.setDescription(de);
    }
  } catch (Throwable t) { }
  return g;
}""")''', '''  g.setItemStack(new @IS@(s.getItemId(), s.getQuantity(), s.getDurability(), s.getMaxDurability(), (@BSON@) null));
  boolean rar = @PKG@.MenuCfg.INV_RARITY;   // 0.3.66: Server Setup menu.inventory.rarity (the slot colour + the coloured title)
  String hx = rar ? rarHex(s) : "";
  String n = "";
  try {
    Object o = s.getFromMetadataOrNull(@IDM@.KEYED_CODEC);
    if (o != null) {
      @IDM@ d = (@IDM@) o;
      n = rar ? mark(d.getName(), 0) : flat(d.getName());   // 0.3.66: the colours stay (was flat(): raw text only)
      String de = mark(d.getDescription(), 0);
      if (de.length() > 0) g.setDescription(de);
    }
  } catch (Throwable t) { n = ""; }
  if (hx.length() > 0) {
    if (n.length() == 0) n = "<color is=" + String.valueOf((char) 34) + hx + String.valueOf((char) 34) + ">" + @PKG@.InvCraft.name(s.getItemId()) + "</color>";
    else if (n.indexOf("color is=") < 0) n = "<color is=" + String.valueOf((char) 34) + hx + String.valueOf((char) 34) + ">" + n + "</color>";
    try {
      g.setBackground(@UVAL@.of(new @PSTY@().setColor(@UVAL@.of(tint(hx)))));
      g.setSkipItemQualityBackground(true);
      RARS = RARS + 1;
    } catch (Throwable t) { }
  }
  if (n.length() > 0) g.setName(n);
  return g;
}""")''')

# ---------- (3) Server Setup: menu.inventory.rarity (a NEW key; absent = ON - no migration)
P.rep('''     "field:MenuCfg.INV_REPLACE@config.properties:inventoryReplace"),
''', '''     "field:MenuCfg.INV_REPLACE@config.properties:inventoryReplace"),
    # 0.3.66 (Skyy 11-22 "it doesnt show the legendary color in the new inventory"): the off switch of the slot colour + coloured title
    ("menu.inventory.rarity", "Rarity colours on inventory slots", "menu", "bool", "true", "", "", "", "", "live",
     "Rolled gear and charms show their rarity colour on the slot and the tooltip title. Off: plain slots.",
     "field:MenuCfg.INV_RARITY@config.properties:inventoryRarity"),
''')
P.rep('''    "# inventoryReplace = the inventory key (Tab) opens the SkyWynn inventory screen (true or false). false = the vanilla inventory.",
    "inventoryReplace=true",
''', '''    "# inventoryReplace = the inventory key (Tab) opens the SkyWynn inventory screen (true or false). false = the vanilla inventory.",
    "inventoryReplace=true",
    "",
    "# inventoryRarity = rolled gear and charms show their rarity colour on the inventory screen's slots and in the tooltip title (true or",
    "# false). false = plain slots (the tooltip text keeps its colours).",
    "inventoryRarity=true",
''')
P.rep('''F(mcfg, "public static volatile boolean INV_REPLACE = true;")                           # 0.3.50: Server Setup (menu.inventory.replace)
''', '''F(mcfg, "public static volatile boolean INV_REPLACE = true;")                           # 0.3.50: Server Setup (menu.inventory.replace)
F(mcfg, "public static volatile boolean INV_RARITY = true;")                            # 0.3.66: Server Setup (menu.inventory.rarity)
''')
P.rep('''WALK_KEY = true; WALK_COOLDOWN_MS = 400L; INV_REPLACE = true; return; }''',
      '''WALK_KEY = true; WALK_COOLDOWN_MS = 400L; INV_REPLACE = true; INV_RARITY = true; return; }''')
P.rep('''    INV_REPLACE = flag(p, "inventoryReplace", true);                      // 0.3.50
''', '''    INV_REPLACE = flag(p, "inventoryReplace", true);                      // 0.3.50
    INV_RARITY = flag(p, "inventoryRarity", true);                        // 0.3.66
''')

# ---------- (4) Beastmastery: the Skills tab's side bar (13 skills, 7 rows) + the inventory skill grid (13 cells, 5 rows)
P.rep('''SK_STN, SK_TRN, SK_GN, SK_ZN, SK_ZK = 27, 8, 12, 6, 3
''', '''SK_STN, SK_TRN, SK_GN, SK_ZN, SK_ZK = 27, 8, 13, 6, 3   # 0.3.66: 13 skills (+ Beastmastery)
SK_GR = (SK_GN + 1) // 2                                   # 0.3.66: the SKILLS rows (2 a row)
SK_SHI = 132                                               # 0.3.66: the shard picture (was 150) - the 7th SKILLS row's room
''')
P.rep('''             ("Orchard", "", "Orchard", False)]
''', '''             ("Orchard", "", "Orchard", False),
             ("Beastmastery", "", "Beastmastery", False)]   # 0.3.66 (Skyy 11-22 "i dont see Beastmaster in the side bar."): SkyyTrees' tree
''')
P.rep('''    sk_h = 20 + 24 + 6 + (SK_GN // 2) * 64
''', '''    sk_h = 20 + 24 + 6 + SK_GR * 64
''')
P.rep('''    for r_ in range(SK_GN // 2):
        ap.append(("#" + skp, G_.glass_group(SK + "Gr%d" % r_, SK_RI, 64, layout="Left", anchor={"top": 6} if r_ == 0 else None)))
    sh_h = IV_BODY_H - sk_h - 10
''', '''    for r_ in range(SK_GR):
        ap.append(("#" + skp, G_.glass_group(SK + "Gr%d" % r_, SK_RI, 64, layout="Left", anchor={"top": 6} if r_ == 0 else None)))
    sh_h = IV_BODY_H - sk_h - 10
''')
# the shard card gives the 7th skill row its room: the shard picture 150 -> 132 px (the 0.3.57 fit assert below, with the new size)
P.rep('''    ap.append(("#" + sh, G_.glass_group(shp, SK_RI, 150, layout="Left", anchor={"top": 6})))
    ap.append(("#" + shp, "Group { Anchor: (Width: %d); }" % ((SK_RI - 150) // 2)))
    ap.append(("#" + shp, G_.glass_grid(SK + "ShI", 1, 1, drag=False, slot=150, icon=120)))
''', '''    ap.append(("#" + sh, G_.glass_group(shp, SK_RI, SK_SHI, layout="Left", anchor={"top": 6})))   # 0.3.66: SK_SHI (was 150)
    ap.append(("#" + shp, "Group { Anchor: (Width: %d); }" % ((SK_RI - SK_SHI) // 2)))
    ap.append(("#" + shp, G_.glass_grid(SK + "ShI", 1, 1, drag=False, slot=SK_SHI, icon=SK_SHI - 28)))
''')
P.rep('''    assert 20 + 24 + 156 + 30 + 20 + 14 + 46 + 44 <= sh_h, ("0.3.57: the shard card fits", sh_h)
''', '''    assert 20 + 24 + SK_SHI + 6 + 30 + 20 + 14 + 46 + 44 <= sh_h, ("0.3.57: the shard card fits", sh_h)
    assert sh_h >= 20 + 24 + SK_SHI + 6 + 30 + 20 + 14 + 46 + 44 and SK_GR == 7, ("0.3.66: the shard card still fits under 7 skill rows", sh_h)
''')
P.rep('''["Gr%d" % k_ for k_ in range(SK_GN // 2)]''', '''["Gr%d" % k_ for k_ in range(SK_GR)]''')
P.rep('''IV_SKN, IV_NOWN, IV_TPN, IV_VCN = 12, 8, 8, 6
''', '''IV_SKN, IV_NOWN, IV_TPN, IV_VCN = 13, 8, 8, 6   # 0.3.66: 13 skill cells (+ Beastmastery)
IV_SKR = (IV_SKN + 2) // 3                       # 0.3.66: 5 rows of 3
''')
P.rep('''    sk_h = 24 + 26 + 4 * 40 + 4
''', '''    sk_h = 24 + 26 + IV_SKR * 40 + 4   # 0.3.66: 5 rows
''')
P.rep('''    for r_ in range(4):
        rw = IV + "SkR%d" % r_
        ap.append(("#" + sk, G_.glass_group(rw, riw, 36, layout="Left", anchor={"top": 4})))
        for c_ in range(3):
            k_ = 3 * r_ + c_
''', '''    for r_ in range(IV_SKR):
        rw = IV + "SkR%d" % r_
        ap.append(("#" + sk, G_.glass_group(rw, riw, 36, layout="Left", anchor={"top": 4})))
        for c_ in range(3):
            k_ = 3 * r_ + c_
            if k_ >= IV_SKN:
                continue   # 0.3.66: the last row holds what is left
''')
# the inventory skill grid: the Beastmastery cell after skill:fn:prog's lines (SkyySkills 0.4.73 has no Beastmastery line)
P.rep('''          if (i == 0 && cls.length() > 0 && cls.equals(f[0])) {
            b.set("#SkyyInvCxpT.Text", "CLASS XP - " + nm);
            b.set("#SkyyInvCxpN.Text", need > 0L ? (@PKG@.MenuUtil.fmt(into) + " / " + @PKG@.MenuUtil.fmt(need)) : "MAX LEVEL");
            int cw = barW(into, need, @PKG@.InvData.CXBW);
            if (cw > 0) b.appendInline("#SkyyInvCxpB", @PKG@.InvData.XP_FILL.replace("{W}", String.valueOf(cw)));
          }
        }
      }
''', '''          if (i == 0 && cls.length() > 0 && cls.equals(f[0])) {
            b.set("#SkyyInvCxpT.Text", "CLASS XP - " + nm);
            b.set("#SkyyInvCxpN.Text", need > 0L ? (@PKG@.MenuUtil.fmt(into) + " / " + @PKG@.MenuUtil.fmt(need)) : "MAX LEVEL");
            int cw = barW(into, need, @PKG@.InvData.CXBW);
            if (cw > 0) b.appendInline("#SkyyInvCxpB", @PKG@.InvData.XP_FILL.replace("{W}", String.valueOf(cw)));
          }
        }
      } else if (i == pl.length - 1 && !progHas(pl, "Beastmastery")) {   // 0.3.66: Beastmastery (its level from skill:fn:level)
        int bl = skillLevel(u, "Beastmastery");
        this.skn[i] = "Beastmastery";
        if (known("Ingredient_Hide_Medium")) g.setItemStack(new @IS@("Ingredient_Hide_Medium", 1));
        g.setName("Beastmastery" + (bl >= 0 ? " - Lv " + bl : ""));
        g.setDescription("Levels up from the XP your pets gain");
        tx = bl >= 0 ? "Lv " + bl : "Lv -";
      }
''')
P.rep('''M(ipg, r"""
public void fillProg(@UCB@ b, @REF@ ref, @ST@ st) {''', '''M(ipg, r"""
public static boolean progHas(String[] pl, String label) {
  for (int i = 1; pl != null && i < pl.length; i++) { if (pl[i].startsWith(label + "|")) return true; }
  return false;
}""")
M(ipg, r"""
public void fillProg(@UCB@ b, @REF@ ref, @ST@ st) {''')
# a skill the Skills tab lists but skill:<uuid> does not carry (Beastmastery) = skill:fn:level {UUID, label}
P.rep('''    for (int i = 0; i < ps.size(); i++) {
      String[] e = (String[]) ps.get(i);
      if (e[0].equalsIgnoreCase(skill)) return Integer.parseInt(e[1]);
    }
  } catch (Throwable t) { }
  return -1;
}""")''', '''    for (int i = 0; i < ps.size(); i++) {
      String[] e = (String[]) ps.get(i);
      if (e[0].equalsIgnoreCase(skill)) return Integer.parseInt(e[1]);
    }
  } catch (Throwable t) { }
  try {   // 0.3.66: a Skills-tab skill skill:<uuid> does not carry (Beastmastery) -> skill:fn:level {UUID, label}
    boolean listed = false;
    for (int i = 0; i < @PKG@.SkillData.ORDER.length; i++) { if (!"Combat".equals(@PKG@.SkillData.ORDER[i]) && @PKG@.SkillData.ORDER[i].equalsIgnoreCase(skill)) listed = true; }
    Object f = listed ? @PKG@.MenuUtil.bridge().get("skill:fn:level") : null;
    if (f instanceof java.util.function.Function) {
      Object r = ((java.util.function.Function) f).apply(new Object[] { u, skill });
      if (r instanceof Number) return ((Number) r).intValue();
    }
  } catch (Throwable t) { }
  return -1;
}""")''')

# ---------- (5) the pocket Deposit: count what you carry first; a clear reason; a second click = this pocket's carried items
IV_PD_TXT = {
    "pdMeta": "Yours have extra data - the Void takes plain only",
    "pdNone": "You carry none of it, nor other %s items",
    "pdNoneP": "Nothing picked - you carry no %s items",
    "pdOffer": "None carried - click again: %d other %s items",
    "pdOfferP": "Nothing picked - click again: %d %s items",
}
P.rep('''M(ipg, r"""
public void pocketAct(String op, String amt) {''', '''# 0.3.66 (Skyy 11-22 "the deposit button isnt working"): what you carry for a pocket - storage, hotbar, backpack (SkyySacks' Deposit
# containers): "id|count" per carried PLAIN item of that pocket (sacks:fn:catOf), in slot order; mine[0] / mine[1] = the picked item's plain /
# extra-data amount (a SkyyFishing whole fish counts as plain: the Void takes it with its entry)
F(ipg, "public long pdAt;")
F(ipg, "public String pdKey;")
F(ipg, "public static volatile int PDALL = 0;")
M(ipg, r"""
public java.util.ArrayList pocketCarry(String cat, String id, int[] mine) {
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.HashMap cnt = new java.util.HashMap();
  java.util.HashMap cats = new java.util.HashMap();
  java.util.function.Function f = @PKG@.InvCraft.fn("sacks:fn:catOf");
  @PLA@ p = null;
  try { p = (@PLA@) this.pst.getComponent(this.pref, @PLA@.getComponentType()); } catch (Throwable t) { p = null; }
  if (p == null || p.getInventory() == null) return out;
  @IC@[] cs = new @IC@[] { p.getInventory().getStorage(), p.getInventory().getHotbar(), p.getInventory().getBackpack() };
  for (int c = 0; c < cs.length; c++) {
    if (cs[c] == null) continue;
    int n = cs[c].getCapacity();
    for (int i = 0; i < n; i++) {
      @IS@ s = cs[c].getItemStack((short) i);
      if (s == null || s.isEmpty()) continue;
      String sid = s.getItemId();
      @BSON@ md = s.getMetadata();
      boolean plain = sid.startsWith("SkyyFishing_Fish_") || md == null || md.isEmpty();
      if (sid.equals(id)) { if (plain) mine[0] = mine[0] + s.getQuantity(); else mine[1] = mine[1] + s.getQuantity(); }
      if (!plain || f == null || cat == null) continue;
      Object k = cats.get(sid);
      if (k == null) {
        Object r = null;
        try { r = f.apply(sid); } catch (Throwable t) { r = null; }
        k = (r instanceof String) ? r : "";
        cats.put(sid, k);
      }
      if (!cat.equals(k)) continue;
      Long was = (Long) cnt.get(sid);
      if (was == null) { out.add(sid); was = Long.valueOf(0L); }
      cnt.put(sid, Long.valueOf(was.longValue() + (long) s.getQuantity()));
    }
  }
  for (int i = 0; i < out.size(); i++) { String sid = (String) out.get(i); out.set(i, sid + "|" + String.valueOf(cnt.get(sid))); }
  return out;
}""")
M(ipg, r"""
public String pocketCall(String op, String id, String a) {
  Object o = call("sacks:fn:pocket", this.pkey == null ? new Object[] { this.playerRef.getUuid(), op, id, a } : new Object[] { this.playerRef.getUuid(), op, id, a, this.pkey });
  return o == null ? null : String.valueOf(o);
}""")
M(ipg, r"""
public void pocketDep(String a) {
  String id = this.psel;
  int[] mine = new int[2];
  java.util.ArrayList carry = pocketCarry(this.pcat, id, mine);
  if (id != null && carry.size() > 0) {   // the picked item itself is not offered twice
    for (int i = carry.size() - 1; i >= 0; i--) { if (((String) carry.get(i)).startsWith(id + "|")) carry.remove(i); }
  }
  if (id != null && mine[0] > 0) {   // the picked item carried = the Void's own Deposit, as before
    this.pdAt = 0L;
    String r = pocketCall("dep", id, a);
    this.pnote = r == null ? "The pockets are not on this server right now - nothing moved" : bare(r);
    if (r != null && r.startsWith("-Your profile changed")) this.psel = null;
    redraw();
    return;
  }
  String key = this.pcat + ">" + (id == null ? "" : id);
  long now = System.currentTimeMillis();
  if (carry.size() > 0 && this.pdAt > 0L && now - this.pdAt >= 0L && now - this.pdAt <= 10000L && key.equals(this.pdKey)) {
    this.pdAt = 0L;
    PDALL = PDALL + 1;
    int done = 0;
    long items = 0L;
    String stop = null;
    for (int i = 0; i < carry.size() && i < 36; i++) {
      String e = (String) carry.get(i);
      String cid = e.substring(0, e.lastIndexOf('|'));
      String r = pocketCall("dep", cid, "");
      if (r == null) { stop = "The pockets are not on this server right now"; break; }
      if (r.startsWith("+")) {
        done = done + 1;
        int sp = r.indexOf(' ', 5);
        try { items = items + Long.parseLong(r.substring(5, sp).replace(",", "")); } catch (Throwable t) { }
        continue;
      }
      if (r.startsWith("-Your profile changed")) { this.psel = null; stop = bare(r); break; }
      if (r.startsWith("-This category is full") || r.startsWith("-The Void is paused")) { stop = bare(r); break; }
    }
    if (done > 0) this.pnote = "Put in " + done + (done == 1 ? " kind" : " kinds") + (items > 0L ? " (" + @PKG@.MenuUtil.fmt(items) + " items)" : "") + (stop != null ? " - then: " + stop : "");
    else this.pnote = stop != null ? stop : "Nothing went in - the Void refused each one";
    redraw();
    return;
  }
  if (carry.size() > 0 && mine[1] == 0) {   // the offer (never armed beside an extra-data answer: that line says why, nothing else)
    this.pdAt = now;
    this.pdKey = key;
    this.pnote = (id == null ? @PKG@.InvData.PD_OFFERP : @PKG@.InvData.PD_OFFER).replace("{N}", String.valueOf(carry.size())).replace("{C}", this.pcat);
    redraw();
    return;
  }
  this.pdAt = 0L;
  this.pnote = id == null ? @PKG@.InvData.PD_NONEP.replace("{C}", this.pcat)
      : (mine[1] > 0 ? @PKG@.InvData.PD_META : @PKG@.InvData.PD_NONE.replace("{C}", this.pcat));
  redraw();
}""")
M(ipg, r"""
public void pocketAct(String op, String amt) {''')
P.rep('''  this.pamt = a;
  if (this.psel == null) { this.pnote = "Pick an item in the grid first"; redraw(); return; }
''', '''  this.pamt = a;
  if ("dep".equals(op)) { pocketDep(a); return; }   // 0.3.66: Deposit counts what you carry first
  if (this.psel == null) { this.pnote = "Pick an item in the grid first"; redraw(); return; }
''')
P.rep('''F(idat, "public static final String XP_FILL = %s;" % jstr(IV_FILL))
''', '''F(idat, "public static final String XP_FILL = %s;" % jstr(IV_FILL))
# 0.3.66: the pocket Deposit lines ({N} a number, {C} the pocket's name - at most 8 letters); one line of the result label
''' + "IV_PD_TXT = %r\n" % IV_PD_TXT + '''for _n, _k in (("PD_META", "pdMeta"), ("PD_NONE", "pdNone"), ("PD_NONEP", "pdNoneP"), ("PD_OFFER", "pdOffer"), ("PD_OFFERP", "pdOfferP")):
    _v = IV_PD_TXT[_k].replace("%d", "{N}").replace("%s", "{C}")
    _w = IV_PD_TXT[_k].replace("%d", "99").replace("%s", "Smithing")
    assert all(32 <= ord(c_) < 127 for c_ in _v) and '"' not in _v and SUI.text_width(_w, 12) <= 290, ("0.3.66: a pocket line fits one line", _w)
    F(idat, "public static final String %s = %s;" % (_n, jstr(_v)))
assert max(len(c_) for c_ in IV_PCATS) <= 8, "0.3.66: a pocket name fits the Deposit lines"
''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "0.3.66: no new system / command"
_i = P.s.index
assert _i("public void benchRow(") < _i("public void fillCraft(") < _i("public void fillFurn(") and _i('F(ipg, "public int cboff;")') < _i("public void benchRow(")
assert _i("public void bench(int i)") < _i("public void benchMore()") < _i('if (a.equals("cbm")) { benchMore(); return; }')
assert _i("public static String mark(") < _i("public static @IGS@ slot(@IS@ s)") and _i("public static String rarHex(") < _i("public static @IGS@ slot(@IS@ s)")
assert _i("public static String tint(") < _i("public static @IGS@ slot(@IS@ s)") and _i('F(mcfg, "public static volatile boolean INV_RARITY') < _i("public static @IGS@ slot(@IS@ s)")
assert _i("public static String tr(String key)") < _i("public static String mark(")
assert _i("public static boolean progHas(") < _i("public void fillProg(") and _i("public static int skillLevel(") < _i("public void fillProg(")
assert _i("public Object call(String key, Object arg)") < _i("public String pocketCall(") < _i("public void pocketDep(") < _i("public void pocketAct(String op")
assert _i('F(ipg, "public long pdAt;")') < _i("public void pocketDep(") and _i("public static String bare(String r)") < _i("public void pocketDep(")
P.finish()


# ---- the harness blocks (FURN2)
EXPECT_66 = '''EXPECT = {   # 0.3.66: the bench row + pocket Deposit + slot colour (InvPage), the skill list (SkillData / SkillPage), the config row (MenuCfg ...)
    "InvData": ["+f BENCH_NAV", "+f NAVW", "+f PD_META", "+f PD_NONE", "+f PD_NONEP", "+f PD_OFFER", "+f PD_OFFERP", "+f TABMIN", "~<clinit>"],
    "InvPage": ["+f MORES", "+f PDALL", "+f RARS", "+f cbk", "+f cboff", "+f pdAt", "+f pdKey", "+m benchMore", "+m benchRow", "+m hex2", "+m mark",
                "+m pocketCall", "+m pocketCarry", "+m pocketDep", "+m progHas", "+m qualHex", "+m rarHex", "+m tint", "~<clinit>", "~m build",
                "~m fillCraft", "~m fillFurn", "~m fillProg", "~m handleDataEvent", "~m pocketAct", "~m skillLevel", "~m slot"],
    "MenuCfg": ["+f INV_RARITY", "~<clinit>", "~m init", "~m load"],   # the Server Setup row menu.inventory.rarity
    "CfgFile": ["~<clinit>"], "CfgRows": ["~<clinit>", "~m header"], "CfgFn": ["~m opExport"],   # the config kit with the new row
    "SkillData": ["~<clinit>"], "SkillPage": ["~m build", "~m fillCells"],   # Beastmastery (13 skills, 7 rows)
    "SkyyMenuPlugin": ["~m setup"], "OpsPage": ["~<clinit>"], "MenuData": ["~<clinit>"],   # the version string + the Mods list
}
'''
HARNESS_TIP = r'''    # ---- FURN2 TIP (0.3.66; Skyy 11-22 "the tool tips look funny, they losty all the color coding")
    de_ = str(E.jf(IGSc.class_, "description").get(sl))
    K.eq(de_, 'T3 Iron - Sword\n<color is="#7ee08a">Damage +5</color>', "FURN2 TIP the description keeps its colour spans as markup (was flat text)")
    _m = lambda m_: str(PG.mark(m_, 0))
    K.eq([_m(MSGc.raw("x").bold(True)), _m(MSGc.raw("y").italic(True)), _m(MSGc.raw("z").color("#123456").bold(True)),
          _m(MSGc.join(_JA(MSGc)([MSGc.raw("a"), MSGc.raw("b").color("#abcdef")])).color("#000000")), _m(MSGc.translation("server.x.y")), _m(None)],
         ["<b>x</b>", "<i>y</i>", '<color is="#123456"><b>z</b></color>', '<color is="#000000">a<color is="#abcdef">b</color></color>', "[server.x.y]", ""],
         "FURN2 TIP mark(): bold, italic, colour + bold, nested colours, a key without English text = [key], null = ''")
    # ---- FURN2 RAR (0.3.66; Skyy 11-22 "it doesnt show the legendary color in the new inventory"): a stand-in ItemQuality table
    IQLc = JClass(PH + "server.core.asset.type.item.config.ItemQuality")
    PCOLc = JClass(PH + "protocol.Color")
    ILTc = JClass("com.hypixel.hytale.assetstore.map.IndexedLookupTableAssetMap")
    JAWMc = JClass("com.hypixel.hytale.assetstore.map.JsonAssetWithMap")
    qarr_ = JClass("java.lang.reflect.Array").newInstance(JAWMc.class_, 8)
    BYTEc = JClass("java.lang.Byte")
    for qi_, qn_, rgb_ in ((1, "Common", (0xc9, 0xd2, 0xdd)), (3, "Skyy_Gear_legendary", (0x55, 0xff, 0xff)), (4, "Epic", (0x8b, 0x33, 0x9e))):
        q_ = Ucls.allocateInstance(IQLc.class_)
        E.jf(IQLc.class_, "id").set(q_, qn_)
        c_ = Ucls.allocateInstance(PCOLc.class_)
        for f_, v_ in zip(("red", "green", "blue"), rgb_):
            E.jf(PCOLc.class_, f_).setByte(c_, BYTEc(v_ if v_ < 128 else v_ - 256).byteValue())
        E.jf(IQLc.class_, "textColor").set(q_, c_)
        JClass("java.lang.reflect.Array").set(qarr_, qi_, q_)
    qm_ = Ucls.allocateInstance(ILTc.class_)
    E.jf(ILTc.class_, "array").set(qm_, qarr_)
    qst_ = Ucls.allocateInstance(JClass("com.hypixel.hytale.server.core.asset.HytaleAssetStore").class_)
    E.jf(JClass("com.hypixel.hytale.assetstore.AssetStore").class_, "assetMap").set(qst_, qm_)
    E.jf(IQLc.class_, "ASSET_STORE").set(None, qst_)
    tint_ = lambda h_: "#" + "".join("%02x" % ((int(h_[1 + 2 * k_:3 + 2 * k_], 16) * 35 + b_ * 65) // 100) for k_, b_ in enumerate((0x0f, 0x1a, 0x2c)))
    K.eq([str(PG.tint("#55ffff")), str(PG.qualHex(JClass("java.lang.reflect.Array").get(qarr_, 3))), str(PG.qualHex(JClass("java.lang.reflect.Array").get(qarr_, 1))), str(PG.qualHex(None))],
         [tint_("#55ffff"), "#55ffff", "", ""], "FURN2 RAR tint = 35 % of the colour over the slot colour #0f1a2c; a quality's hex; white / grey (Common) = none; nothing = none")
    PSTYc = JClass(PH + "server.core.ui.PatchStyle")
    bg_ = lambda g_: E.jf(IGSc.class_, "background").get(g_)
    bgc_ = lambda g_: (None if bg_(g_) is None else str(E.jf(PSTYc.class_, "color").get(bg_(g_).getValue()).getValue()))
    skp_ = lambda g_: bool(E.jf(IGSc.class_, "skipItemQualityBackground").get(g_))
    nm_ = lambda g_: (None if E.jf(IGSc.class_, "name").get(g_) is None else str(E.jf(IGSc.class_, "name").get(g_)))
    r0_ = int(PG.RARS)
    sl3_ = PG.slot(real)
    se4_ = PG.slot(ISc("Rock_Stone", 5).withQuality(4))
    sc1_ = PG.slot(ISc("Rock_Stone", 5).withQuality(1))
    so_ = PG.slot(ISc("Rock_Stone", 5))
    s7_ = PG.slot(ISc("Rock_Stone", 5).withQuality(7))
    K.check(bgc_(sl3_) == tint_("#55ffff") and skp_(sl3_) and nm_(sl3_) == '<color is="#ff5555">Rolled Iron Sword</color>' and int(PG.RARS) == r0_ + 2,
            "FURN2 RAR the legendary-stamped sword: the slot Background = its quality colour tint, the vanilla quality background skipped, the title keeps the name's own colour (%s %s)" % (bgc_(sl3_), nm_(sl3_)))
    K.check(bgc_(se4_) == tint_("#8b339e") and skp_(se4_) and str(nm_(se4_)).startswith('<color is="#8b339e">') and str(nm_(se4_)).endswith("</color>")
            and "Rock" in str(nm_(se4_)), "FURN2 RAR an Epic-stamped plain stack: the Epic tint + its name in the Epic colour (%s)" % nm_(se4_))
    K.check(bg_(sc1_) is None and not skp_(sc1_) and nm_(sc1_) is None and bg_(so_) is None and nm_(so_) is None and bg_(s7_) is None and nm_(s7_) is None,
            "FURN2 RAR a Common (white / grey) stamp, the item's own quality and an unknown quality index = no colour, no name override")
    K.check(E.jf(IGSc.class_, "itemStack").get(sl3_).getMetadata() is None and int(_qf.get(E.jf(IGSc.class_, "itemStack").get(sl3_))) == int(_qf.get(plain))
            and int(_qf.get(E.jf(IGSc.class_, "itemStack").get(se4_))) == int(_qf.get(plain)), "FURN2 RAR the grid copies still carry NO metadata and NO quality override")
    CFG.INV_RARITY = False
    sx_ = PG.slot(real)
    K.check(bg_(sx_) is None and not skp_(sx_) and nm_(sx_) == "Rolled Iron Sword" and "<color" in str(E.jf(IGSc.class_, "description").get(sx_))
            and bg_(PG.slot(ISc("Rock_Stone", 5).withQuality(4))) is None, "FURN2 RAR Server Setup menu.inventory.rarity OFF: plain slots + a plain title; the description keeps its colours")
    CFG.INV_RARITY = True
'''
HARNESS_POCKET = r'''    # ---- FURN2 POCKET (0.3.66; Skyy 11-22 "the deposit button isnt working"): Deposit counts what you carry first
    PDF = {"full": None}

    def f_pdep(o):
        PTOK.append(str(o[4]) if len(o) > 4 else None)
        POCK.append((str(o[1]), str(o[2]), str(o[3])))
        if str(o[1]) != "dep":
            return "+Took 64 Copper Ore"
        if PDF["full"] == str(o[2]):
            return "-This category is full - level it up or upgrade its rarity"
        return "+Put %d %s into the Void" % (E.count(PK, str(o[2])), str(o[2]))
    BR.put("sacks:fn:pocket", Fn(f_pdep))
    BR.put("sacks:fn:catOf", Fn(lambda o: "Mining" if str(o) in ("Ore_Copper", "Skyy_Ench_Iron") else ("Farming" if str(o) == "Plant_Fruit_Apple" else None)))
    pr_ = lambda p_: sval(cmap(p_), "#SkyyInvPr.Text") or ""
    PDT = dict((k_, str(getattr(DATA, k_))) for k_ in ("PD_META", "PD_NONE", "PD_NONEP", "PD_OFFER", "PD_OFFERP"))
    fr_ = [i_ for i_ in range(36) if at(PK, "storage", i_) is None][:3]
    hf_ = [i_ for i_ in range(9) if at(PK, "hotbar", i_) is None][0]
    K.check(len(fr_) == 3 and E.count(PK, "Ore_Copper") == 0 and E.count(PK, "Skyy_Ench_Iron") == 0, "FURN2 POCKET the stand-in player carries no Mining item yet")
    n0_ = len(POCK)
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit, nothing of the pocket carried")
    K.check(len(POCK) == n0_ and pr_(p_) == PDT["PD_NONE"].replace("{C}", "Mining"), "FURN2 POCKET nothing carried = the reason, NO call (%s)" % pr_(p_))
    put(PK, "storage", fr_[0], ISc("Ore_Copper", 5))
    p_ = one(ev(PK, {"a": "po:dep", "@A": "2"}), "FURN2 POCKET Deposit the picked item")
    K.check(len(POCK) == n0_ + 1 and POCK[-1] == ("dep", "Ore_Copper", "2") and PTOK[-1] == "k1" and pr_(p_) == "Put 5 Ore_Copper into the Void",
            "FURN2 POCKET the picked item carried = ONE sacks:fn:pocket dep (the amount, the list's token), its answer shown (%s)" % pr_(p_))
    inv(PK, "storage").removeItemStackFromSlot(JShort(fr_[0]))
    put(PK, "storage", fr_[1], ISc("Skyy_Ench_Iron", 4))
    put(PK, "hotbar", hf_, ISc("Skyy_Ench_Iron", 2))
    put(PK, "storage", fr_[2], ISc("Plant_Fruit_Apple", 7))
    n0_ = len(POCK)
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit, the picked item not carried")
    K.check(len(POCK) == n0_ and pr_(p_) == PDT["PD_OFFER"].replace("{N}", "1").replace("{C}", "Mining") and int(pg.pdAt) > 0,
            "FURN2 POCKET the picked item not carried = a clear line offering the 1 other Mining item you carry (not the Farming apple), NO call (%s)" % pr_(p_))
    pa0_ = int(PG.PDALL)
    p_ = one(ev(PK, {"a": "po:dep", "@A": "9"}), "FURN2 POCKET Deposit again")
    K.check(POCK[n0_:] == [("dep", "Skyy_Ench_Iron", "")] and PTOK[-1] == "k1" and int(PG.PDALL) == pa0_ + 1 and pr_(p_) == "Put in 1 kind (6 items)"
            and int(pg.pdAt) == 0, "FURN2 POCKET the second click = ONE dep per carried item of THIS pocket (storage + hotbar counted, all of it, the token) (%s %s)" % (POCK[n0_:], pr_(p_)))
    n0_ = len(POCK)
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit after the run")
    K.check(len(POCK) == n0_ and "click again" in pr_(p_), "FURN2 POCKET a third click = the offer again (the run used it up) (%s)" % pr_(p_))
    pg.pdAt = int(pg.pdAt) - 11000
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit 11 s later")
    K.check(len(POCK) == n0_ and "click again" in pr_(p_), "FURN2 POCKET a click over 10 s after the offer = the offer again, NO call (%s)" % pr_(p_))
    PDF["full"] = "Skyy_Ench_Iron"
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit into a full category")
    K.check(POCK[n0_:] == [("dep", "Skyy_Ench_Iron", "")] and pr_(p_) == "This category is full - level it up or upgrade its rarity",
            "FURN2 POCKET a full category = the Void's own reason, the run stops (%s)" % pr_(p_))
    PDF["full"] = None
    put(PK, "storage", fr_[0], ISc("Ore_Copper", 3).withMetadata(IDMc.KEYED_CODEC, IDMc(MSGc.raw("Odd Ore"), MSGc.raw("odd"))))
    n0_ = len(POCK)
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit, the picked item only with extra data")
    K.check(len(POCK) == n0_ and pr_(p_) == PDT["PD_META"] and int(pg.pdAt) == 0, "FURN2 POCKET the picked item only as an extra-data stack = says so, NO call, no offer armed (%s)" % pr_(p_))
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit again after the extra-data line")
    K.check(len(POCK) == n0_, "FURN2 POCKET ... and a second click still moves nothing")
    inv(PK, "storage").removeItemStackFromSlot(JShort(fr_[0]))
    sp_ = pg.psel
    pg.psel = None
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit with nothing picked")
    K.check(len(POCK) == n0_ and pr_(p_) == PDT["PD_OFFERP"].replace("{N}", "1").replace("{C}", "Mining"), "FURN2 POCKET nothing picked + Mining items carried = the offer (%s)" % pr_(p_))
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit again with nothing picked")
    K.check(POCK[n0_:] == [("dep", "Skyy_Ench_Iron", "")], "FURN2 POCKET ... the second click deposits them (%s)" % POCK[n0_:])
    for f_, s_ in (("storage", fr_[1]), ("hotbar", hf_), ("storage", fr_[2])):
        if at(PK, f_, s_) is not None:
            inv(PK, f_).removeItemStackFromSlot(JShort(s_))
    p_ = one(ev(PK, {"a": "po:dep", "@A": ""}), "FURN2 POCKET Deposit, nothing picked, nothing carried")
    K.check(len(POCK) == n0_ + 1 and pr_(p_) == PDT["PD_NONEP"].replace("{C}", "Mining"), "FURN2 POCKET nothing picked + nothing carried = the reason, NO call (%s)" % pr_(p_))
    pg.psel = sp_
    BR.put("sacks:fn:pocket", Fn(f_pact))
    BR.remove("sacks:fn:catOf")
    pg.pdAt = 0
'''
HARNESS_BENCH = r'''    # ---- FURN2 BENCH (0.3.66; Skyy 11-22 "i want a normal easy way to access this besides the right now tab."): the pinned tabs + paging
    def wid_(p_, i_):
        m_ = re.search(r"Width: (\d+)", mk_of(p_, "SkyyInvBt%s" % i_))
        return int(m_.group(1)) if m_ else -1
    bk0_ = [str(x_) for x_ in list(pgF.cbenches)]
    K.check(bk0_[-2:] == ["Furnace", "Tannery"] and bk0_[0] == "Crafting", "FURN2 BENCH Crafting first, Furnace + Tannery pinned last (%s)" % bk0_)
    AL = JClass("java.util.ArrayList")
    ten_ = AL()
    for n_ in ["Crafting", "Armor_Bench", "Furniture_Bench", "Arcane_Bench", "Salvagebench", "Farming_Bench", "Weapon_Bench", "Builders_Bench", "Furnace", "Tannery"]:
        ten_.add(n_)
    pgF.cbenches = ten_
    pgF.cboff = 0
    fbw_ = int(DATA.FX_BW)
    kF_ = (fbw_ - int(DATA.NAVW) - 4) // (int(DATA.TABMIN) + 4) - 3
    p_ = one(ev(PK, {"a": "fq", "@F": ""}), "FURN2 BENCH 10 benches on the Furnace panel")
    cm = cmap(p_) if p_ else {}
    shown_ = [k_ for k_ in range(10) if ("#SkyyInvBt%d.Text" % k_) in cm]
    K.check(shown_ == [0] + list(range(1, 1 + kF_)) + [8, 9] and sval(cm, "#SkyyInvBtM.Text") == "More" and ("Activating", "#SkyyInvBtM") in [b_[:2] for b_ in binds_of(p_)]
            and sval(cm, "#SkyyInvBt8.Text") == "Furnace" and sval(cm, "#SkyyInvBt9.Text") == "Tanning" and TSEL_ in mk_of(p_, "SkyyInvBt8")
            and min(wid_(p_, k_) for k_ in shown_) >= 60 and len(shown_) <= 8 and kF_ >= 1,
            "FURN2 BENCH the Furnace panel: Crafting + %d benches + More + Furnace (selected) + Tanning, every tab >= 60 px, at most 8 (%s %s)" % (kF_, shown_, [wid_(p_, k_) for k_ in shown_]))
    K.check(mk_of(p_, "SkyyInvBtM").find("Width: %d" % int(DATA.NAVW)) > 0 and sum(wid_(p_, k_) + 4 for k_ in shown_) + int(DATA.NAVW) + 4 <= fbw_ + 4,
            "FURN2 BENCH the Furnace row fits its width (no overlap at 1080p)")
    seen_ = set(shown_)
    m0_ = int(PG.MORES)
    for r_ in range(4):
        p_ = one(ev(PK, {"a": "cbm"}), "FURN2 BENCH More %d" % r_)
        cm = cmap(p_) if p_ else {}
        sh_ = [k_ for k_ in range(10) if ("#SkyyInvBt%d.Text" % k_) in cm]
        K.check(sh_[0] == 0 and sh_[-2:] == [8, 9] and str(pgF.mode) == "f", "FURN2 BENCH More keeps Crafting, Furnace, Tanning and the Furnace panel (%s)" % sh_)
        seen_ |= set(sh_)
    K.check(seen_ == set(range(10)) and int(PG.MORES) == m0_ + 4, "FURN2 BENCH More pages through every bench and wraps")
    pgF.cboff = 0
    p_ = one(ev(PK, {"a": "cb:9"}), "FURN2 BENCH the pinned Tanning tab")
    K.check(str(pgF.fbench) == "Tannery" and str(pgF.mode) == "f", "FURN2 BENCH the pinned Tanning tab (index 9) opens the Tanning panel")
    one(ev(PK, {"a": "cb:8"}), "FURN2 BENCH back to the Furnace")
    rs_ = AL()
    for n_ in bk0_:
        rs_.add(n_)
    pgF.cbenches = rs_
    # the craft panel with more benches from the recipe list (7 more bench recipes), then without them
    XB = [recipe("Skyy_Test_XB%d" % k_, [("Rock_Stone", 1)], "Plant_Fruit_Apple", 1, b_) for k_, b_ in
          enumerate(["Armor_Bench", "Furniture_Bench", "Arcane_Bench", "Farming_Bench", "Builders_Bench", "Alchemy_Bench", "Cooking_Bench"])]
    LIST.extend(XB)
    p_ = one(ev(PK, {"a": "cb:0"}), "FURN2 BENCH the craft panel with more benches")
    cm = cmap(p_) if p_ else {}
    bks_ = [str(x_) for x_ in list(pgF.cbenches)]
    nB_ = len(bks_)
    kC_ = (int(DATA.BW_ALL) - int(DATA.NAVW) - 4) // (int(DATA.TABMIN) + 4) - 3
    sh_ = [k_ for k_ in range(nB_) if ("#SkyyInvBt%d.Text" % k_) in cm]
    K.check(nB_ >= 10 and bks_[-2:] == ["Furnace", "Tannery"] and sh_ == [0] + list(range(1, 1 + kC_)) + [nB_ - 2, nB_ - 1] and sval(cm, "#SkyyInvBtM.Text") == "More"
            and min(wid_(p_, k_) for k_ in sh_) >= 60 and len(sh_) <= 8 and TSEL_ in mk_of(p_, "SkyyInvBt0")
            and sum(wid_(p_, k_) + 4 for k_ in sh_) + int(DATA.NAVW) + 4 <= int(DATA.BW_ALL) + 4,
            "FURN2 BENCH the craft panel: Crafting (selected) + %d benches + More + Furnace + Tanning, >= 60 px each, fits the row (%s %s)" % (kC_, bks_, sh_))
    p_ = one(ev(PK, {"a": "cbm"}), "FURN2 BENCH More on the craft panel")
    sh2_ = [k_ for k_ in range(nB_) if ("#SkyyInvBt%d.Text" % k_) in cmap(p_)]
    K.check(str(pgF.mode) == "c" and sh2_[0] == 0 and sh2_[-2:] == [nB_ - 2, nB_ - 1] and sh2_[1] == 1 + kC_, "FURN2 BENCH More on the craft panel = the next benches (%s)" % sh2_)
    xi_ = sh2_[1]
    p_ = one(ev(PK, {"a": "cb:%d" % xi_}), "FURN2 BENCH a paged bench tab")
    K.check(str(pgF.cbench) == bks_[xi_] and TSEL_ in mk_of(p_, "SkyyInvBt%d" % xi_), "FURN2 BENCH a paged tab opens ITS bench (cb:<index>), selected, its page kept (%s)" % bks_[xi_])
    for x_ in XB:
        LIST.remove(x_)
        ramap.remove(x_)
    pgF.cboff = 0
    p_ = one(ev(PK, {"a": "cb:0"}), "FURN2 BENCH the craft panel again")
    K.check("#SkyyInvBtM.Text" not in cmap(p_) and [str(x_) for x_ in list(pgF.cbenches)][-2:] == ["Furnace", "Tannery"], "FURN2 BENCH fewer benches = every tab, no More")
    one(ev(PK, {"a": "cb:%d" % [str(x_) for x_ in list(pgF.cbenches)].index("Furnace")}), "FURN2 BENCH back to the Furnace panel")
'''
HARNESS_SKILL = r'''    # ---- FURN2 SKILL (0.3.66; Skyy 11-22 "i dont see Beastmaster in the side bar."): the 13th skill
    BR.put("skill:fn:level", Fn(lambda o: INTc(7) if str(o[1]) == "Beastmastery" else INTc(0)))
    K.check(int(SKD.GN) == 13 and str(SKD.ORDER[12]) == "Beastmastery" and str(SKD.TREE[12]) == "Beastmastery" and not bool(SKD.SHARD[12]) and str(SKD.TOOLP[12]) == "",
            "FURN2 SKILL Beastmastery = the 13th Skills-tab skill (SkyyTrees' Beastmastery tree, no tool, no shard)")
    K.eq(int(PG.skillLevel(PK.pr.getUuid(), "Beastmastery")), 7, "FURN2 SKILL its level = skill:fn:level (skill:<uuid> does not carry it)")
    K.eq(int(PG.skillLevel(PK.pr.getUuid(), "Archer")), -1, "FURN2 SKILL ... only for a Skills-tab skill (a class label not in skill:<uuid> stays -1)")
    p_ = sk_ev({"a": "sk:12"}, "FURN2 SKILL the Beastmastery cell")
    cm = cmap(p_) if p_ else {}
    K.check(str(SP.skill) == "Beastmastery" and sval(cm, "#SkyySkpCb12.Text") == "Beastmastery" and sval(cm, "#SkyySkpCl12.Text") == "Lv 7"
            and sval(cm, "#SkyySkpHdT.Text") == "BEASTMASTERY" and "#SkyySkpGr6" in "".join(str(c_.selector or "") for c_ in cmds_of(p_)),
            "FURN2 SKILL the side bar lists Beastmastery (row 7), Lv 7, its page opens (%s)" % sval(cm, "#SkyySkpHdT.Text"))
    BR.remove("skill:fn:level")
'''



# ======================================================================= the HARNESS (derived from the 0.3.65 harness: every 0.3.65 check
# runs again on the 0.3.66 jar, plus FURN2)
def cut(t, start, end):
    i = t.index(start)
    j = t.index(end, i)
    return t[i:j]


T.rep('''"""Harness for SkyyMenu 0.3.65 (dropping from the new inventory; tools/menu_0_3_65_patch.py, round drop1).
GENERATED by tools/menu_0_3_65_patch.py from the 0.3.64 harness (edit the patch, not this file): every 0.3.64 check runs again on the
0.3.65 jar''', '''"""Harness for SkyyMenu 0.3.66 (Skyy's 11-22 inventory fixes; tools/menu_0_3_66_patch.py, round furn2).
GENERATED by tools/menu_0_3_66_patch.py from the 0.3.65 harness (edit the patch, not this file): every 0.3.65 check runs again on the
0.3.66 jar (the inventory page has 4 more bindings: Furnace + Tanning tabs, the 13th skill cell; the grid copy's name keeps its colour), plus
  FURN2 (EXECUTED on the stand-in players / bridges):
       BENCH   Furnace + Tanning always shown (no SkyySacks too), pinned last; 10 benches on the craft panel and on the Furnace panel =
               Crafting + a page + More + Furnace + Tanning (no tab under 60 px, at most 8 tabs, the row fits), More pages and wraps; a
               tab keeps its bench index (cb:<i> opens that bench); fewer benches = no More
       TIP     the grid copy keeps every colour / bold / italic span as markup; a key without English text stays [key]
       RAR     a stack-stamped quality (QualityOverride) = the slot Background (the quality colour 35 % over the slot colour) + the vanilla
               quality background skipped + the coloured title (the metadata name's own colour wins); the item's own quality, a white /
               grey quality or an unknown index = nothing; Server Setup menu.inventory.rarity OFF = plain slot + plain title (the
               description keeps its colours); the page packet carries it; still no metadata / QualityOverride in any grid
       SKILL   Beastmastery = the 13th skill (Skills side bar + its page; the inventory's next cell from skill:fn:level)
       POCKET  Deposit: the picked item carried = ONE sacks:fn:pocket dep (as before); not carried / nothing picked = a clear line and NO
               call; a second click within 10 s = one dep per carried item of THIS pocket (sacks:fn:catOf), hotbar counted; an
               extra-data stack is never offered; after 10 s = the offer again; a full category stops the run
The 0.3.65 harness text follows:
Harness for SkyyMenu 0.3.65 (dropping from the new inventory; tools/menu_0_3_65_patch.py, round drop1).
GENERATED by tools/menu_0_3_65_patch.py from the 0.3.64 harness (edit the patch, not this file): every 0.3.64 check runs again on the
0.3.65 jar''')
T.rep('VERSION = "0.3.65"\nJAR', 'VERSION = "0.3.66"\nJAR')
T.rep('OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.64.jar")', 'OLD_JAR = os.path.join(HERE, "SkyyMenu-0.3.65.jar")')
T.rep('GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.64.py")', 'GEN_OLD = os.path.join(HERE, "build_skyymenu_0.3.65.py")')
T.rep('PATCH = os.path.join(ROOT, "tools", "menu_0_3_65_patch.py")', 'PATCH = os.path.join(ROOT, "tools", "menu_0_3_66_patch.py")')
T.rep('"scratch", "drop1", "menu"', '"scratch", "furn2", "menu"')
T.rep('ADDED = []   # 0.3.65: no new class\n', 'ADDED = []   # 0.3.66: no new class\n')
T.rep(cut(T.s, 'EXPECT = {   # 0.3.65:', 'if "--expect-dump" in sys.argv:'), EXPECT_66)
T.rep('''    K.check(g.count('VERSION = "0.3.65"') == 1, "S VERSION")''', '''    K.check(g.count('VERSION = "0.3.66"') == 1, "S VERSION")
    # 0.3.66: the bench rows page at least one bench, the More markup, the pocket lines fit one line, the shard card fits 7 skill rows
    K.check("0.3.66: a bench row pages at least 1 bench" in g and "0.3.66: the More button" in g and "0.3.66: a pocket line fits one line" in g
            and "0.3.66: the shard card still fits under 7 skill rows" in g and '("menu.inventory.rarity", "Rarity colours on inventory slots"' in g
            and "inventoryRarity=true" in g, "FURN2 STATIC the build asserts the bench rows, the More button, the pocket lines and the 7-row SKILLS fit; the Server Setup row + file line")''')
# the grid copy's name keeps its colour (the switch is ON by default)
T.rep('''    K.eq(str(E.jf(IGSc.class_, "name").get(sl)), "Rolled Iron Sword", "COPY: the name travels as text")
    K.check("Damage +5" in str(E.jf(IGSc.class_, "description").get(sl)), "COPY: the description travels as text")
''', '''    K.eq(str(E.jf(IGSc.class_, "name").get(sl)), '<color is="#ff5555">Rolled Iron Sword</color>', "COPY: the name travels as text (0.3.66: with its colour)")
    K.check("Damage +5" in str(E.jf(IGSc.class_, "description").get(sl)), "COPY: the description travels as text")
''' + HARNESS_TIP)
T.rep('''    K.check("Wood_Oak_Trunk" in sd and "Rolled Iron Sword" in sd and "ItemDisplay" not in sd and "QualityOverride" not in sd and "qualityIndex" not in sd,
            "PAGE: storage Slots = the real items; the sword's name travels, its metadata / quality override do not")
''', '''    K.check("Wood_Oak_Trunk" in sd and "Rolled Iron Sword" in sd and "ItemDisplay" not in sd and "QualityOverride" not in sd and "qualityIndex" not in sd,
            "PAGE: storage Slots = the real items; the sword's name travels, its metadata / quality override do not")
    K.check('"Background"' in sd and tint_("#55ffff") in sd and '"SkipItemQualityBackground":true' in sd.replace(" ", "") and sd.count('"Background"') == 1,
            "FURN2 RAR the page packet: the sword's slot (only) carries its rarity Background + skips the vanilla quality background (%s)" % sd[:200])
''')
T.rep('''    K.check("Crafting" == sval(cm, "#SkyyInvBt0.Text") and "#SkyyInvBt1.Text" not in cm, "PAGE (0.3.52): no SkyySacks here = the plain pocket mode, one bench tab (Crafting)")''',
      '''    K.check([sval(cm, "#SkyyInvBt%d.Text" % k_) for k_ in range(4)] == ["Crafting", "Furnace", "Tanning", None] and "#SkyyInvBtM.Text" not in cm,
            "PAGE (0.3.52): no SkyySacks here = the plain pocket mode; FURN2 BENCH (0.3.66): Crafting + Furnace + Tanning ALWAYS (no More)")''')
T.rep('''    K.eq(len(bl), 7 + 8 + 7 + 4 * 4 + 1 + 5 + 2 + 1 + 2 + 12 + 12 - 1 + 2, "PAGE: 74 bindings (0.3.65:''',
      '''    K.eq(len(bl), 7 + 8 + 7 + 4 * 4 + 1 + 5 + 2 + 1 + 2 + 12 + 12 - 1 + 2 + 2 + 2, "PAGE: 78 bindings (0.3.66: + the Furnace + Tanning tabs, + the 13th skill cell's icon + Lv button; 0.3.65:''')
# INV7: the Beastmastery cell after skill:fn:prog's 3 lines (no skill:fn:level = Lv -)
T.rep('''    K.eq([sval(cm, "#SkyyInvSk%d.Text" % k_) for k_ in range(4)], ["Lv 23", "Lv 31", "Lv 100", ""], "INV7 PROG the cells say Lv N (class first)")''',
      '''    K.eq([sval(cm, "#SkyyInvSk%d.Text" % k_) for k_ in range(5)], ["Lv 23", "Lv 31", "Lv 100", "Lv -", ""], "INV7 PROG the cells say Lv N (class first; FURN2: then Beastmastery, Lv - without skill:fn:level)")''')
T.rep('''    K.check("#SkyyInvStl.Text" in cm, "INV7 PROG the stats line is drawn (%s)" % sval(cm, "#SkyyInvStl.Text"))
''', '''    K.check("#SkyyInvStl.Text" in cm, "INV7 PROG the stats line is drawn (%s)" % sval(cm, "#SkyyInvStl.Text"))
    BR.put("skill:fn:level", Fn(lambda o: JClass("java.lang.Integer")(9) if str(o[1]) == "Beastmastery" else JClass("java.lang.Integer")(0)))
    p_ = one(ev(PK, {"a": "cb:0"}), "FURN2 SKILL the inventory's Beastmastery cell")
    cm = cmap(p_) if p_ else {}
    K.check(sval(cm, "#SkyyInvSk3.Text") == "Lv 9" and "Beastmastery - Lv 9" in cm.get("#SkyyInvSkI3.Slots", "") and str(pgF.skn[3]) == "Beastmastery"
            and "#SkyyInvSb3" not in cm and "#SkyyInvSk12.Text" in cm, "FURN2 SKILL the inventory grid's next cell = Beastmastery (skill:fn:level, no XP bar; 13 cells)")
    BR.remove("skill:fn:level")
''')
# INV4: Deposit now counts what you carry first (FURN2 POCKET); wd / sell / unpack unchanged
T.rep('''    for op_, amt_ in (("wd", "64"), ("sell", "10"), ("dep", ""), ("unpack", "all")):''',
      '''    for op_, amt_ in (("wd", "64"), ("sell", "10"), ("unpack", "all")):   # 0.3.66: Deposit = FURN2 POCKET''')
T.rep('''    PKT["t"] = "k2"
    p_ = one(ev(PK, {"a": "ppn"}), "INV4 FIX a redraw after a profile switch")''', HARNESS_POCKET + '''    PKT["t"] = "k2"
    p_ = one(ev(PK, {"a": "ppn"}), "INV4 FIX a redraw after a profile switch")''')
T.rep('''    one(ev(PK, {"a": "fq", "@F": ""}), "INV7 FURN clear the search")
''', '''    one(ev(PK, {"a": "fq", "@F": ""}), "INV7 FURN clear the search")
''' + HARNESS_BENCH)
T.rep('''    K.check(SP is not None and str(SP.skill) == "Mining", "TAB1 OPEN the inventory's Mining icon = the Mining page")
''', '''    K.check(SP is not None and str(SP.skill) == "Mining", "TAB1 OPEN the inventory's Mining icon = the Mining page")
''' + HARNESS_SKILL)
T.rep('''    K.eq(ORD, ["Combat", "Mining", "Foraging", "Farming", "Fishing", "Smithing", "Alchemy", "Cooking", "Acrobatics", "Exploration", "Ranching", "Orchard"],
         "TAB1 the 12 skills, Combat (= your class, Skyy 'class is combat.') first")''', '''    K.eq(ORD, ["Combat", "Mining", "Foraging", "Farming", "Fishing", "Smithing", "Alchemy", "Cooking", "Acrobatics", "Exploration", "Ranching", "Orchard", "Beastmastery"],
         "TAB1 the 13 skills (0.3.66: + Beastmastery), Combat (= your class, Skyy 'class is combat.') first")''')
T.rep('''all(("#SkyyInvSk%d" % k_, "skc:%d" % k_) in eb_ for k_ in range(12))
            and all([x_ for x_ in lb_ if x_.startswith("TextButton #SkyyInvSk%d " % k_)] for k_ in range(12)),''',
      '''all(("#SkyyInvSk%d" % k_, "skc:%d" % k_) in eb_ for k_ in range(13))
            and all([x_ for x_ in lb_ if x_.startswith("TextButton #SkyyInvSk%d " % k_)] for k_ in range(13)),''')
if T.dst:
    T.finish()
