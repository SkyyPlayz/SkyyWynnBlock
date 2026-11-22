"""Derive SkyySacks/build_skyysacks_0.8.41.py from the SET pin 0.8.40 (the GENERATED build_skyysacks_0.8.40.py; edit THIS file, then
regenerate: python tools/sacks_0_8_41_patch.py; never re-run sacks_0_8_40_patch.py on top of it). Every anchor is asserted once; at the end
every change is undone on a copy and compared with 0.8.40 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_41_patch.py   then   python SkyySacks/build_skyysacks_0.8.41.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.41.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.41 (2026-11-22, round rar3) = COLOUR-CODED ITEM TEXTS (rarity + tooltip pass part 3, looks only). Skyy 2026-10-24: "make that the global
  default. if it has a rarity, it gets color coded. if it has flavor text, the text is well laid out, well organized, clear, readable, and
  color coded." + Skyy 2026-10-18 (research/Vanilla-UI-Style-Guide.md section 15): "make all the flavor text use a slightly bigger font, and
  color code everything. so you can see what stats it gives at a glance".
  1. The 21 old Magic Bag descriptions + the Pocket Dimension's (items.<id>.description and the server. twin) get the Style Guide 15 spans:
     minor info dim #7f93a6 ("Old Magic Bag"), the Void rarity in its own colour (the Skyy_Bag_Void quality = the Mythic #cc66cc), actions /
     commands yellow #ffcc00 (right-click, /pd, /pocket), progress gold #e8c25a ("level up as you collect"), what it costs you red #ff7a7a
     ("can't be dropped, stored or sold"). The words are unchanged: every text without its spans = the 0.8.40 text byte for byte (build check).
  2. Names, qualities (rarity frame + title colour), ids and recipes are unchanged; no saved data, no config row, no class.
  3. (review fix 1) THE /pd VOID PAGE: every item cell, the selected item's icon and the upgrade cost icons get the kit icon_cell(icon_bg=) rarity
     square (the item's engine quality colour at 0.4; no rarity = the faint grey - the SkyyBazaar 0.2.3 look and table), and the selected item's
     name is drawn in its rarity colour (white without one). SacksPage.qHex / qBg / qName read the quality at run time (Item.getQualityIndex ->
     ItemQuality id), cached per id. Display only.
  ROLLBACK to 0.8.40: safe alone (plain texts again).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.40.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.41.py"))
if "--out" in sys.argv:
    P.dst = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
assert P.has('VERSION = "0.8.40"\n') and P.has("furnList") and not P.has("_C841"), "not the live generated SkyySacks 0.8.40"
SYS0, CMD0, CLS0 = P.s.count("registerSystem("), P.s.count("registerCommand("), P.s.count("makeClass(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.41 (2026-11-22"):].rstrip() + "\n"

P.rep('''  system / command. ROLLBACK to 0.8.39: safe alone (the two keys disappear; SkyyMenu 0.3.56 then opens the pack's own Furnace / Tannery
  pages as 0.3.55 did - the queues are the same file).
''', '''  system / command. ROLLBACK to 0.8.39: safe alone (the two keys disappear; SkyyMenu 0.3.56 then opens the pack's own Furnace / Tannery
  pages as 0.3.55 did - the queues are the same file).
''' + NOTE)
P.rep('VERSION = "0.8.40"\n', 'VERSION = "0.8.41"\n')

# ---- 1. the old bag text
P.rep('''_OLD_DESC = ("Old Magic Bag - it turns into Void rarity (or is refunded) when you pick it up. Everything that was in it is in the Void: "
             "type /pd.")
''', '''_OLD_DESC = ("Old Magic Bag - it turns into Void rarity (or is refunded) when you pick it up. Everything that was in it is in the Void: "
             "type /pd.")
# 0.8.41 (rar3, Style Guide 15; tools/sacks_0_8_41_patch.py): the same words with the colour spans - minor info dim, the Void rarity in its
# quality colour (Skyy_Bag_Void = the Mythic row's colour), actions / commands yellow, progress gold, what it costs you red
_C841 = {"dim": SUI.COLOR["rowSub"], "void": [r for r in BAG_RARITY if r[1] == "Mythic"][0][2], "act": "#ffcc00", "prog": "#e8c25a",
         "cost": "#ff7a7a"}          # ui-data: the Style Guide 15 hexes (the kit has no token for act / prog / cost yet)
assert _C841["dim"] == "#7f93a6" and _C841["void"] == "#cc66cc", _C841


def _c841(kind, text):
    return '<color is="%s">%s</color>' % (_C841[kind], text)


def _plain841(t):
    import re as _re
    return _re.sub(r"</?color[^>]*>", "", t)


_OLD_DESC0 = _OLD_DESC
_OLD_DESC = (_c841("dim", "Old Magic Bag") + " - it turns into " + _c841("void", "Void rarity") + " (or is refunded) when you pick it up. "
             "Everything that was in it is in the Void: type " + _c841("act", "/pd") + ".")
assert _plain841(_OLD_DESC) == _OLD_DESC0 and _OLD_DESC.isascii(), "0.8.41: the old bag text keeps its words"
''')

# ---- 2. the Pocket Dimension text
P.rep('''_PDESC = ("SkyyVoid - right-click (or type /pd) to open the Void: one storage for everything you gather, six categories that level up as "
          "you collect. This is only the opener and it stays with you: it can't be dropped, stored or sold - /pocket gives a new one if it is ever missing.")
''', '''_PDESC = ("SkyyVoid - right-click (or type /pd) to open the Void: one storage for everything you gather, six categories that level up as "
          "you collect. This is only the opener and it stays with you: it can't be dropped, stored or sold - /pocket gives a new one if it is ever missing.")
_PDESC0 = _PDESC          # 0.8.41 (rar3): the same words, colour coded (Style Guide 15)
_PDESC = (_c841("void", "SkyyVoid") + " - " + _c841("act", "right-click") + " (or type " + _c841("act", "/pd") + ") to open the Void: one storage for "
          "everything you gather, six categories that " + _c841("prog", "level up as you collect") + ". This is only the opener and it stays with you: "
          "it " + _c841("cost", "can't be dropped, stored or sold") + " - " + _c841("act", "/pocket") + " gives a new one if it is ever missing.")
assert _plain841(_PDESC) == _PDESC0 and _PDESC.isascii(), "0.8.41: the Pocket text keeps its words"
''')

# ---- 3. build check: every description line of the jar is coloured, its words = 0.8.40, spans balanced and never nested
P.rep('''files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"  # key items.<Id>.name in server.lang (pattern from Tamework)
''', '''files["Server/Languages/en-US/server.lang"] = "\\n".join(lang) + "\\n"  # key items.<Id>.name in server.lang (pattern from Tamework)
# 0.8.41 (rar3): the 44 description lines carry the spans (balanced, never nested, Style Guide 15 hexes only); names / labels stay plain
import re as _re841
_d841 = [l for l in lang if ".description=" in l.split("=", 1)[0] + "="]
assert len(_d841) == 44 and all("<color is=" in l for l in _d841), "0.8.41: every description is colour coded"
for _l in _d841:
    _v = _l.split("=", 1)[1]
    assert _re841.fullmatch(r'(?:[^<]|<color is="#[0-9a-f]{6}">[^<]*</color>)*', _v), "0.8.41: spans balanced / not nested: " + _l
    assert set(_re841.findall(r'#[0-9a-f]{6}', _v)) <= set(_C841.values()), "0.8.41: only the Style Guide 15 hexes: " + _l
    assert _plain841(_v) in (_OLD_DESC0, _PDESC0), "0.8.41: the words are 0.8.40's: " + _l
assert not [l for l in lang if ".description=" not in l and "<" in l], "0.8.41: names / quality labels stay plain"
''')

# ---- 4. (rar3 fix 1, review: "the Sacks /pd Void page cells still have no rarity frame") the /pd Void page: every item cell (#SkyyVCell<n>), the
# selected item's icon (#SkyyVSelIc) and the upgrade cost icons (#SkyyVCost<n>) get the kit icon_cell(icon_bg=) rarity square (the item's
# engine quality colour at 0.4, the SkyyBazaar 0.2.3 / SkyyPets 0.4.18 look; no rarity = the faint grey), and the selected item's name
# (#SkyyVSelName, the side panel's title) is drawn in that rarity colour (white without one). The quality is read at run time from the item
# asset (Item.getQualityIndex -> ItemQuality id), so pack-mod items get theirs too; the colour table = SkyyBazaar 0.2.3's (SUI.QUALITY Common ..
# Legendary, SUI.RARITY Mythic, Skyy_Enchanted = Epic as tools/skyyench.py stamps it). Display only: no count, id or saved data is read or written.
P.rep('''page.addMethod(CtNewMethod.make("""
public static String safe(String t) {''', '''# 0.8.41 (rar3 fix 1, tools/sacks_0_8_41_patch.py): the item's rarity colour for the /pd Void page (display only; "" = none). Cached per id
# once the item asset answered (a missing asset is asked again); the table = SkyyBazaar 0.2.3's colours
_Q841 = [("Common", SUI.QUALITY["Common"]), ("Uncommon", SUI.QUALITY["Uncommon"]), ("Rare", SUI.QUALITY["Rare"]), ("Epic", SUI.QUALITY["Epic"]),
         ("Legendary", SUI.QUALITY["Legendary"]), ("Mythic", SUI.RARITY["Mythic"]), ("Skyy_Enchanted", SUI.QUALITY["Epic"])]
_QBG_A, _QBG_NONE = "0.4", SUI.COLOR["disabled"] + "(0.15)"          # = SkyyBazaar 0.2.3 BZ_RBG_ALPHA / BZ_RBG_NONE (SkyyPets 0.4.18)
assert all(len(_h) == 7 and _h.startswith("#") for _q, _h in _Q841) and _QBG_NONE == "#797b7c(0.15)", _Q841
_jarr841 = lambda xs: "new String[] { %s }" % ", ".join('"%s"' % x for x in xs)
_JT["IQL"] = "com.hypixel.hytale.server.core.asset.type.item.config.ItemQuality"
for _c, _m in ((_JT["IQL"], "getAssetMap"), (_JT["IQL"], "getId"), (_JT["ITM"], "getQualityIndex"), (_JT["ITM"], "getAssetMap")):
    B.probe(pool, _c, _m)
page.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap QHEX = new java.util.concurrent.ConcurrentHashMap();", page))
page.addField(CtField.make("public static final String[] QN = %s;" % _jarr841([_q for _q, _h in _Q841]), page))
page.addField(CtField.make("public static final String[] QC = %s;" % _jarr841([_h for _q, _h in _Q841]), page))
page.addField(CtField.make('public static final String QBG_NONE = "%s";' % _QBG_NONE, page))
page.addField(CtField.make('public static final String QBG_A = "(%s)";' % _QBG_A, page))
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String qCol(String qn) {
  if (qn == null) return "";
  for (int i = 0; i < QN.length; i++) if (QN[i].equals(qn)) return QC[i];
  return "";
}\'\'\'), page))
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String qHex(String id) {
  if (id == null || id.length() == 0) return "";
  Object c = QHEX.get(id);
  if (c instanceof String) return (String) c;
  String h = "";
  boolean ok = false;
  try {
    Object o = @ITM@.getAssetMap().getAsset(id);
    if (o instanceof @ITM@) {
      ok = true;
      Object q = @IQL@.getAssetMap().getAsset(((@ITM@) o).getQualityIndex());
      if (q instanceof @IQL@) h = qCol(String.valueOf(((@IQL@) q).getId()));
    }
  } catch (Throwable t) { h = ""; ok = false; }
  if (ok && QHEX.size() < 4096) QHEX.put(id, h);
  return h;
}\'\'\'), page))
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String qBg(String id) {
  String h = qHex(id);
  return h.length() == 0 ? QBG_NONE : h + QBG_A;
}\'\'\'), page))
page.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String qName(String id, String dflt) {
  String h = qHex(id);
  return h.length() == 0 ? dflt : h;
}\'\'\'), page))
page.addMethod(CtNewMethod.make("""
public static String safe(String t) {''')
P.rep('''                       SUI.icon_cell("SkyyVCell" + J_("idx"), item=J_("safe(cid)", "Ore_Copper"), size=74, state="selected", qty=True),
                       SUI.icon_cell("SkyyVCell" + J_("idx"), item=J_("safe(cid)", "Ore_Copper"), size=74, state="normal", qty=True)),''',
      '''                       SUI.icon_cell("SkyyVCell" + J_("idx"), item=J_("safe(cid)", "Ore_Copper"), size=74, state="selected", qty=True,
                                     icon_bg=J_("vbg", SUI.QUALITY["Common"] + "(0.4)")),          # 0.8.41 (rar3 fix 1): the rarity square
                       SUI.icon_cell("SkyyVCell" + J_("idx"), item=J_("safe(cid)", "Ore_Copper"), size=74, state="normal", qty=True,
                                     icon_bg=J_("vbg", SUI.QUALITY["Common"] + "(0.4)"))),''')
P.rep('''    "selic": SUI.choose("sel != null", SUI.icon_cell("SkyyVSelIc", item=J_("safe(sel)", "Ore_Copper"), size=66, state="static", look="plain"),''',
      '''    "selic": SUI.choose("sel != null", SUI.icon_cell("SkyyVSelIc", item=J_("safe(sel)", "Ore_Copper"), size=66, state="static", look="plain",
                                                     icon_bg=J_("sbg", SUI.QUALITY["Common"] + "(0.4)")),          # 0.8.41 (rar3 fix 1)''')
P.rep('''    "selname": SUI.label("SkyyVSelName", "", "strong", w=V_SIDE_W - 76, h=30, size=17),''',
      '''    "selname": SUI.label("SkyyVSelName", "", "strong", w=V_SIDE_W - 76, h=30, size=17, col=J_("sncol", "#ffffff")),          # 0.8.41: rarity colour''')
P.rep('''    "costic": SUI.icon_cell("SkyyVCost" + J_("cx"), item=J_("safe(cid2)", "Ore_Iron"), size=32, state="static", look="plain"),''',
      '''    "costic": SUI.icon_cell("SkyyVCost" + J_("cx"), item=J_("safe(cid2)", "Ore_Iron"), size=32, state="static", look="plain",
                            icon_bg=J_("cbg", SUI.QUALITY["Common"] + "(0.4)")),          # 0.8.41 (rar3 fix 1): the rarity square''')
P.rep('''      b.appendInline("#SkyyVCostR" + cr, @@costic@@);''',
      '''      String cbg = qBg(cid2);          // 0.8.41 (rar3 fix 1): the cost item's rarity square
      b.appendInline("#SkyyVCostR" + cr, @@costic@@);''')
P.rep('''        b.appendInline("#SkyyVRow" + r, @@cell@@);''',
      '''        String vbg = qBg(cid);          // 0.8.41 (rar3 fix 1): the cell's rarity square
        b.appendInline("#SkyyVRow" + r, @@cell@@);''')
P.rep('''  b.appendInline("#SkyyVSelRow", @@selic@@);''',
      '''  String sbg = sel == null ? QBG_NONE : qBg(sel);          // 0.8.41 (rar3 fix 1): the selected item's rarity square + name colour
  String sncol = sel == null ? "#ffffff" : qName(sel, "#ffffff");
  b.appendInline("#SkyyVSelRow", @@selic@@);''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0 and P.s.count("makeClass(") == CLS0, "0.8.41: no class / system / command"
assert P.s.index("public static String qBg(String id)") < P.s.index("public static String safe(String t)") < P.s.index("String vbg = qBg(cid);"), "0.8.41: qBg before the page uses it"
assert P.s.index("_OLD_DESC = (_c841(") < P.s.index('lang.append("items.%s.description=%s" % (iid, _OLD_DESC))'), "0.8.41: the text is ready before the bags use it"
P.finish()
