"""Derive SkyyRolls/build_skyyrolls_0.1.2.py from 0.1.1.
0.1.2 (Skyy 2026-09-23 test: "/roll kinda worked, kinda didnt"):
 - "/rolls give mithril bow" failed with wrongNumberRequiredParameters (Expected: 0, actual: 2): give had a 0-arg form and a 1-arg
   usage variant, and the engine picks a form by token count. Now give has NO variant and setAllowsExtraArguments(true)
   (AbstractCommand.acceptCall0: with allowsExtraArguments only "fewer tokens than required" fails), and reads the words after
   "give" from ctx.getInputString() itself.
 - "/rolls give Weapon_shortbow_mithril" gave an "Invalid Item" (item ids are case-sensitive: Weapon_Shortbow_Mithril) because the id
   was never checked. Now every id goes through Rolls.resolve(): exact id -> case-insensitive id (spaces = underscores) -> an item whose
   id contains every typed word (weapons preferred) -> otherwise nothing is given and up to 8 matching ids are suggested.
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyRolls", "build_skyyrolls_0.1.1.py")
dst = os.path.join(ROOT, "SkyyRolls", "build_skyyrolls_0.1.2.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
TQ = chr(34) * 3
BS = chr(92)


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:100])
    s = s.replace(old, new, 1)


rep('VERSION = "0.1.1"', 'VERSION = "0.1.2"')
rep("0.1.1: positional arguments fixed.",
    "0.1.2: /rolls give takes a plain name or any-case id (\"/rolls give mithril bow\", \"/rolls give weapon_shortbow_mithril\") and never" + LF +
    "  gives an unknown id (it suggests matches instead) - notes in tools/rolls_0_1_2_patch.py." + LF +
    "0.1.1: positional arguments fixed.")
rep('BV  = "org.bson.BsonValue"', 'BV  = "org.bson.BsonValue"' + LF + 'ITM = "com.hypixel.hytale.server.core.asset.type.item.config.Item"')
rep('             (AC, "addSubCommand"), (AC, "addUsageVariant"), (AC, "withRequiredArg"), (AC, "withOptionalArg")):',
    '             (AC, "addSubCommand"), (AC, "addUsageVariant"), (AC, "withRequiredArg"), (AC, "withOptionalArg"),' + LF +
    '             (AC, "setAllowsExtraArguments"), (CTX, "getInputString"), (ITM, "getAssetMap")):')

RESOLVE = LF.join([
    "# 0.1.2: item name -> real item id (or null + suggestions)",
    "rl.addMethod(CtNewMethod.make(f" + TQ,
    "public static String resolve(String q, StringBuilder sugg) {{",
    "  if (q == null) return null;",
    "  String t = q.trim();",
    "  if (t.length() == 0) return null;",
    "  try {{ if ({ITM}.getAssetMap().getAsset(t) != null) return t; }} catch (Throwable e) {{ }}",
    "  String norm = t.toLowerCase().replace(' ', '_');",
    "  String[] words = t.toLowerCase().replace('_', ' ').trim().split(\" \");",
    "  java.util.ArrayList hits = new java.util.ArrayList();",
    "  java.util.ArrayList weapons = new java.util.ArrayList();",
    "  try {{",
    "    java.util.Iterator it = {ITM}.getAssetMap().getAssetMap().keySet().iterator();",
    "    while (it.hasNext()) {{",
    "      String id = String.valueOf(it.next());",
    "      if (id.length() == 0 || id.charAt(0) == '*') continue;",
    "      String low = id.toLowerCase();",
    "      if (low.equals(norm)) return id;",
    "      boolean all = true;",
    "      for (int i = 0; i < words.length; i++) {{ if (words[i].length() > 0 && low.indexOf(words[i]) < 0) {{ all = false; break; }} }}",
    "      if (all) {{ hits.add(id); if (id.startsWith(\"Weapon_\")) weapons.add(id); }}",
    "    }}",
    "  }} catch (Throwable e) {{ warn(\"item lookup failed: \" + e); return null; }}",
    "  if (hits.size() == 1) return (String) hits.get(0);",
    "  if (weapons.size() == 1) return (String) weapons.get(0);",
    "  java.util.Collections.sort(hits);",
    "  for (int i = 0; i < hits.size() && i < 8; i++) {{ if (sugg.length() > 0) sugg.append(\", \"); sugg.append((String) hits.get(i)); }}",
    "  if (hits.size() > 8) sugg.append(\" ... (\" + hits.size() + \" matches)\");",
    "  return null;",
    "}}" + TQ + ", rl))",
    "",
])
anchor = "# The three actions, moved out of the 0.1 RollsCmd.execute unchanged"
rep(anchor, RESOLVE + anchor)
rep("""public static void give({PR} pr, {INV} inv, String id) {{
  {IS} it = applyRolls(new {IS}(id, 1));""",
    """public static void give({PR} pr, {INV} inv, String q) {{
  StringBuilder sugg = new StringBuilder();
  String id = resolve(q, sugg);
  if (id == null) {{
    pr.sendMessage({MSG}.raw("[Rolls] no item matches '" + q + "'" + (sugg.length() > 0 ? ". Did you mean: " + sugg : " - use an item id like Weapon_Shortbow_Mithril")));
    return;
  }}
  {IS} it = applyRolls(new {IS}(id, 1));""")

# give: no usage variant, extra words allowed, parse the rest of the line ourselves
rep("""  super("give", "Give an item with random rolls: /rolls give [itemId] (default Weapon_Longsword_Copper)");
  addUsageVariant(new {PKG}.RollsGiveVariantCmd());""",
    """  super("give", "Give an item with random rolls: /rolls give [item name or id] (default Weapon_Longsword_Copper)");
  setAllowsExtraArguments(true);""")
rep("""{EXEC}
  {PKG}.Rolls.run(store, ref, pr, "give", {PKG}.Rolls.DEFAULT_ITEM);
}}\"\"\", gvr))""",
    """{EXEC}
  String line = "";
  try {{ line = ctx.getInputString(); }} catch (Throwable t) {{ line = ""; }}
  if (line == null) line = "";
  String q = line.trim();
  String low = q.toLowerCase();
  int at = low.indexOf("give ");
  if (at >= 0) q = q.substring(at + 5).trim();
  else if (low.equals("give") || low.endsWith(" give")) q = "";
  if (q.length() == 0) q = {PKG}.Rolls.DEFAULT_ITEM;
  {PKG}.Rolls.run(store, ref, pr, "give", q);
}}\"\"\", gvr))""")

open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", dst)
