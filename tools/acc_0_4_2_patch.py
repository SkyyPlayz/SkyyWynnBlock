"""Derive SkyyAccessories/build_skyyaccessories_0.4.2.py from 0.4.1 (same style as acc_0_4_1_patch.py: rep(old, new) with asserted
anchors, newline-agnostic; 0.4.1 stays untouched, its line endings are preserved).
0.4.2 (Skyy's focus call 2026-09-23 "Alchemy + Cooking are table-only"; research/Smithing-Smelting-Spec.md section 6; orchestrator
decision 4 = the Campfire accessory goes too, because all 3 Campfire recipes are cooked food): RETIRE the Alchemy Bench T1-T4, Cooking
Bench and Campfire bench accessories (6 item ids).
 1. The three rows STAY in BENCHES, so their item assets are still generated: owned copies stay valid items (never "unknown item").
    RETIRED = those bench ids, ACTIVE = every other row (10 benches, 24 accessory ids).
 2. Item assets of retired rows: built as before, then del node["Recipe"] (the 0.4 legacy-talisman precedent) - nothing can craft a
    new one, and they are no longer upgrade inputs for each other. Name "<Name> Accessory <Roman> (retired)", description says it is
    retired, why (Alchemy / Cooking are skills at the real tables, which draw from the Magic Bags; the Campfire's recipes are all
    cooked food) and that it does nothing. A build-time check fails if any generated recipe still takes a retired accessory.
 3. Java AccDefs.BENCH_IDS / BENCH_NAMES / BENCH_MAX come from ACTIVE only, so the Omni's synthetic max-tier grants in benchList no
    longer include them. New AccDefs.RETIRED / RETIRED_NAMES / RETIRED_COLOR, isRetired(id) (= benchOf(id) is a retired bench id,
    case-insensitive; never a talisman or the Omni), retiredWhy(id) (one-line page refusal) and retiredChat(id) (longer chat line).
 4. AccDefs.benchList skips retired ids: an already-equipped old copy drops out of acc:has:<uuid>, so SkyySacks (any version, 0.7.2
    included) shows no Alchemy tab and no Cooking Bench / Campfire recipes for it. AccStore.has returns false for retired ids, so
    acc:fn:has answers false too.
 5. Equip refusal: the bag page checks isRetired BEFORE canEquipK - page line "Retired - ..." plus one chat line with the full reason;
    the item never leaves the inventory. Store guards (canEquipK false, equipK null) back it up. Unequip is unchanged, so an equipped
    copy can still be taken out (it frees the bag slot).
 6. Bag page: pretty(id) = "<Name> <Roman> - retired" ("<Name> - retired" for the single-tier Cooking Bench / Campfire - review fix:
    the numeral is only shown when the bench has more than one tier, like the item names; the same fix applies to the active
    single-tier benches, e.g. "Arcane Bench" instead of "Arcane Bench I"); the rarity column reads "DOES NOTHING", both in grey (rarityName/rarityColor);
    rarityOf returns 0, so a retired item never counts toward future accessory power. The inventory list puts retired accessories
    AFTER usable ones, so they never push a usable accessory out of the 6 Equip rows.
 7. Omni: recipe = the 10 ACTIVE top-tier accessories (was 13), description generated from ACTIVE plus a note that the retired three
    are not covered. Existing Omni items keep working and cover the 10 active benches at max tier.
 8. Ready log counts 24 active bench accessories (+6 retired); manifest mentions the retirement.
 9. Everything else - every 0.4.1 per-profile behaviour (pkey, one key per click, epoch republish, profile:busy / unknown-profile move
    block, page-key check), talismans, the movement protocol - is untouched.
Deliberately NOT done (spec 6.4 defaults): no refund recipes (the plan says owned copies "stay as items but do nothing"; a standalone
refund recipe in a mod jar is also UNVERIFIED), item Quality left as before (only the page shows it as retired).
Run:  python tools/acc_0_4_2_patch.py   then   python SkyyAccessories/build_skyyaccessories_0.4.2.py   (never --deploy from an agent)
"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.1.py")
dst = os.path.join(ROOT, "SkyyAccessories", "build_skyyaccessories_0.4.2.py")
raw = open(src, "rb").read()
NL = "\r\n" if b"\r\n" in raw else "\n"
assert NL == "\n" or raw.count(b"\r\n") == raw.count(b"\n"), "mixed line endings in 0.4.1"
s = raw.decode("utf8").replace("\r\n", "\n")


def rep(old, new, count=1):
    global s
    assert old in s, "anchor missing: " + old[:80]
    assert s.count(old) == count, "anchor count %d != %d: %s" % (s.count(old), count, old[:80])
    s = s.replace(old, new)


# ---------------------------------------------------------------- header / version
rep('''"""SkyyAccessories 0.4.1 - build script (derived from 0.4 by tools/acc_0_4_1_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.1.py            -> SkyyAccessories/SkyyAccessories-0.4.1.jar
       python build_skyyaccessories_0.4.1.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.1: per-profile storage''', '''"""SkyyAccessories 0.4.2 - build script (derived from 0.4.1 by tools/acc_0_4_2_patch.py - edit the patch, not this file)
Run:   python build_skyyaccessories_0.4.2.py            -> SkyyAccessories/SkyyAccessories-0.4.2.jar
       python build_skyyaccessories_0.4.2.py --deploy   -> also copies to Mods/SkyyAccessories.jar and enables it in the HUD mod world
0.4.2: RETIRED bench accessories (Skyy: Alchemy + Cooking are table-only; research/Smithing-Smelting-Spec.md section 6; the Campfire
     goes too - its 3 recipes are all cooked food). Full notes in tools/acc_0_4_2_patch.py:
     - Skyy_Accessory_Alchemybench_T1..T4, Skyy_Accessory_Cookingbench_T1, Skyy_Accessory_Campfire_T1 keep their item assets (owned
       copies stay valid items) but have NO recipe, say "(retired)" and why in name + description, and do nothing.
     - Equip refuses them (page line + chat line, the item stays in the inventory); Unequip still takes an equipped copy out.
     - An equipped copy is filtered out of acc:has:<uuid> (AccDefs.benchList) and acc:fn:has (AccStore.has), so it unlocks no /craft
       recipes; rarityOf = 0 (never counts toward accessory power); the page shows it grey as "- retired" / "DOES NOTHING".
     - Omni: recipe = the 10 active top-tier bench accessories (was 13) and it no longer covers the retired three.
     - Every 0.4.1 per-profile behaviour is unchanged.
0.4.1 notes:
0.4.1: per-profile storage''')
rep('VERSION = "0.4.1"\n', 'VERSION = "0.4.2"\n')

# ---------------------------------------------------------------- RETIRED / ACTIVE (python side)
rep('''ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII"]
''', '''ROMAN = ["", "I", "II", "III", "IV", "V", "VI", "VII"]
# 0.4.2 RETIRED bench accessories (Smithing-Smelting spec section 6; the Campfire goes with them - its whole recipe list is 3 cooked
# foods). Their rows stay in BENCHES so the item assets are still generated (owned copies stay valid items), but they get no recipe,
# Equip refuses them, acc:has / acc:fn:has leave them out, the Omni does not cover them and they never count for rarity/power.
# AccDefs.retiredWhy / retiredChat name these three ids literally - keep them in sync.
RETIRED = ["Alchemybench", "Cookingbench", "Campfire"]
assert RETIRED == ["Alchemybench", "Cookingbench", "Campfire"], "AccDefs.retiredWhy / retiredChat and RETIRED_DESC name these literally"
ACTIVE = [b for b in BENCHES if b[0] not in RETIRED]
assert all(any(b[0] == r for b in BENCHES) for r in RETIRED), RETIRED
assert len(ACTIVE) == len(BENCHES) - len(RETIRED) == 10, [b[0] for b in ACTIVE]
RETIRED_NAMES = [[b[2] for b in BENCHES if b[0] == r][0] for r in RETIRED]
RETIRED_MAX = [[b[3] for b in BENCHES if b[0] == r][0] for r in RETIRED]   # tier count per retired bench (pretty: numeral only if > 1)
assert RETIRED_MAX == [4, 1, 1], RETIRED_MAX
''')

# ---------------------------------------------------------------- AccDefs arrays from ACTIVE + RETIRED arrays
rep('''bench_ids = ", ".join('"%s"' % b[0] for b in BENCHES)
bench_names = ", ".join('"%s"' % b[2] for b in BENCHES)''', '''bench_ids = ", ".join('"%s"' % b[0] for b in ACTIVE)     # 0.4.2: ACTIVE benches only (the Omni's synthetic grants)
bench_names = ", ".join('"%s"' % b[2] for b in ACTIVE)''')
rep('''dfs.addField(CtField.make('public static final int[] BENCH_MAX = new int[] { %s };' % ", ".join(str(b[3]) for b in BENCHES), dfs))''',
    '''dfs.addField(CtField.make('public static final int[] BENCH_MAX = new int[] { %s };' % ", ".join(str(b[3]) for b in ACTIVE), dfs))
# 0.4.2: retired bench ids + display names (same index) and the grey used for them on the bag page
dfs.addField(CtField.make('public static final String[] RETIRED = new String[] { %s };' % ", ".join('"%s"' % r for r in RETIRED), dfs))
dfs.addField(CtField.make('public static final String[] RETIRED_NAMES = new String[] { %s };' % ", ".join('"%s"' % n for n in RETIRED_NAMES), dfs))
dfs.addField(CtField.make('public static final int[] RETIRED_MAX = new int[] { %s };' % ", ".join(str(m) for m in RETIRED_MAX), dfs))
dfs.addField(CtField.make('public static final String RETIRED_COLOR = "#8a97a3";', dfs))''')

# ---------------------------------------------------------------- AccDefs.isRetired / retiredWhy / retiredChat (right after benchOf)
rep('''  return tail;
}""", dfs))''', '''  return tail;
}""", dfs))
# 0.4.2: a retired bench accessory (Alchemy Bench T1-T4, Cooking Bench, Campfire): kept as an item, does nothing
dfs.addMethod(CtNewMethod.make("""
public static boolean isRetired(String id) {
  if (id == null || isTalisman(id) || OMNI.equals(id)) return false;
  String b = benchOf(id);
  if (b == null) return false;
  for (int i = 0; i < RETIRED.length; i++) if (RETIRED[i].equalsIgnoreCase(b)) return true;
  return false;
}""", dfs))
# 0.4.2: Equip refusal on the page (one line, no commas / colons / parentheses) and the longer chat explanation
dfs.addMethod(CtNewMethod.make("""
public static String retiredWhy(String id) {
  String b = benchOf(id);
  if ("Alchemybench".equalsIgnoreCase(b)) return "Retired - brew at a real Alchemy Bench now - it takes ingredients from your Magic Bags";
  if ("Cookingbench".equalsIgnoreCase(b)) return "Retired - cook at a real Cooking Bench now - it takes ingredients from your Magic Bags";
  return "Retired - cooked food is table-only now - cook at a real Cooking Bench or Campfire";
}""", dfs))
dfs.addMethod(CtNewMethod.make("""
public static String retiredChat(String id) {
  String b = benchOf(id);
  String tail = " This accessory does nothing any more and cannot be equipped. If one is still in your Accessory Bag, Unequip takes it out.";
  if ("Alchemybench".equalsIgnoreCase(b)) return "The Alchemy Bench accessory is retired: Alchemy is a skill now. Brew at a real Alchemy Bench - it takes ingredients straight from your Magic Bags." + tail;
  if ("Cookingbench".equalsIgnoreCase(b)) return "The Cooking Bench accessory is retired: Cooking is a skill now. Cook at a real Cooking Bench - it takes ingredients straight from your Magic Bags." + tail;
  return "The Campfire accessory is retired: its recipes are all cooked food, and cooking is table-only now. Cook at a real Cooking Bench or Campfire." + tail;
}""", dfs))''')

# ---------------------------------------------------------------- rarity: retired = 0 (no power), page column "Does nothing" in grey
rep('''public static int rarityOf(String id) {
  if (!isAccessory(id)) return 0;
  if (OMNI.equals(id)) return 5;''', '''public static int rarityOf(String id) {
  if (!isAccessory(id)) return 0;
  if (isRetired(id)) return 0;   // 0.4.2: retired - never counts (future accessory power reads rarityOf)
  if (OMNI.equals(id)) return 5;''')
rep('''  return RARITY[rarityOf(id)];''', '''  if (isRetired(id)) return "Does nothing";   // 0.4.2: the page's rarity column for a retired accessory
  return RARITY[rarityOf(id)];''')
rep('''  return RARITY_COLOR[rarityOf(id)];''', '''  if (isRetired(id)) return RETIRED_COLOR;   // 0.4.2
  return RARITY_COLOR[rarityOf(id)];''')

# ---------------------------------------------------------------- pretty: "<Name> <Roman> - retired"
rep('''  if (OMNI.equals(id)) return "Omni Accessory";
  String b = benchOf(id);
  if (b == null) return id == null ? "?" : id;''', '''  if (OMNI.equals(id)) return "Omni Accessory";
  String b = benchOf(id);
  if (b == null) return id == null ? "?" : id;
  if (isRetired(id)) {   // 0.4.2 (BENCH_NAMES holds only the active benches); no parentheses in inline page text; numeral only for multi-tier benches
    for (int j = 0; j < RETIRED.length; j++) if (RETIRED[j].equalsIgnoreCase(b)) return RETIRED_NAMES[j] + (RETIRED_MAX[j] > 1 ? " " + roman(tierOf(id)) : "") + " - retired";
  }''')
# 0.4.2 review fix: active single-tier benches (Arcane Bench, Furniture Bench, ...) drop the " I" on the bag page too, like their item names
rep('''  for (int i = 0; i < BENCH_IDS.length; i++) if (BENCH_IDS[i].equals(b)) return BENCH_NAMES[i] + " " + roman(tierOf(id));''',
    '''  for (int i = 0; i < BENCH_IDS.length; i++) if (BENCH_IDS[i].equals(b)) return BENCH_MAX[i] > 1 ? BENCH_NAMES[i] + " " + roman(tierOf(id)) : BENCH_NAMES[i];''')

# ---------------------------------------------------------------- benchList: retired ids never reach acc:has
rep('''# keys = bench id of out[k] (same index), best[k] = its tier; at most s.length + BENCH_IDS.length entries.''',
    '''# keys = bench id of out[k] (same index), best[k] = its tier; at most s.length + BENCH_IDS.length entries.
# 0.4.2: a retired bench accessory is skipped (an equipped old copy unlocks nothing), and BENCH_IDS holds only the ACTIVE benches, so
# the Omni does not grant the retired ones either.''')
rep('''    String bn = benchOf(id);
    if (bn == null) continue;
''', '''    String bn = benchOf(id);
    if (bn == null) continue;
    if (isRetired(id)) continue;   // 0.4.2
''')

# ---------------------------------------------------------------- AccStore: has / canEquipK / equipK guards
rep('''public static boolean has(java.util.UUID u, String id) {{
  if (u == null || id == null) return false;''', '''public static boolean has(java.util.UUID u, String id) {{
  if (u == null || id == null) return false;
  if ({PKG}.AccDefs.isRetired(id)) return false;   // 0.4.2: acc:fn:has never answers true for a retired accessory''')
rep('''public static boolean canEquipK(java.util.UUID u, String k, String id) {{
  synchronized (lock(u)) {{''', '''public static boolean canEquipK(java.util.UUID u, String k, String id) {{
  if ({PKG}.AccDefs.isRetired(id)) return false;   // 0.4.2: never equipped (the page refuses first, with the reason)
  synchronized (lock(u)) {{''')
rep('''public static String equipK(java.util.UUID u, String k, String id) {{
  synchronized (lock(u)) {{''', '''public static String equipK(java.util.UUID u, String k, String id) {{
  if ({PKG}.AccDefs.isRetired(id)) return null;   // 0.4.2
  synchronized (lock(u)) {{''')

# ---------------------------------------------------------------- AccPage.carried: retired accessories listed last
rep('''public static java.util.ArrayList carried({PLA} p) {{
  java.util.ArrayList out = new java.util.ArrayList();''', '''public static java.util.ArrayList carried({PLA} p) {{
  java.util.ArrayList out = new java.util.ArrayList();
  java.util.ArrayList old = new java.util.ArrayList();   // 0.4.2: retired accessories, appended after the usable ones''')
rep('''      String id = it.getItemId();
      if ({PKG}.AccDefs.isAccessory(id) && !out.contains(id)) out.add(id);
    }}
  }}
  return out;''', '''      String id = it.getItemId();
      if (!{PKG}.AccDefs.isAccessory(id)) continue;
      if ({PKG}.AccDefs.isRetired(id)) {{ if (!old.contains(id)) old.add(id); }}
      else if (!out.contains(id)) out.add(id);
    }}
  }}
  out.addAll(old);   // 0.4.2: so they never push a usable accessory out of the Equip rows
  return out;''')

# ---------------------------------------------------------------- AccPage: Equip refuses a retired accessory (item stays in the inventory)
rep('''      String id = this.invIds[i];
''', '''      String id = this.invIds[i];
      if ({PKG}.AccDefs.isRetired(id)) {{   // 0.4.2: retired - refused with the reason, nothing is moved
        this.info = {PKG}.AccDefs.retiredWhy(id);
        try {{ this.playerRef.sendMessage({MSG}.raw("[Accessories] " + {PKG}.AccDefs.retiredChat(id))); }} catch (Throwable t2) {{ }}
        rebuild(); return;
      }}
''')

# ---------------------------------------------------------------- item assets: retired rows keep the asset, lose the recipe
rep('''count = 0
for bench_id, bench_item, name, tiers, ups in BENCHES:''', '''count = 0
retired_count = 0
# 0.4.2: descriptions of the retired bench accessories (asset kept, no recipe)
RETIRED_TAIL = " This accessory does nothing and cannot be equipped; if one is still in your Accessory Bag, Unequip takes it out."
RETIRED_DESC = {
    "Alchemybench": "Retired. Alchemy is a skill now: brew at a real Alchemy Bench, which takes ingredients straight from your Magic Bags." + RETIRED_TAIL,
    "Cookingbench": "Retired. Cooking is a skill now: cook at a real Cooking Bench, which takes ingredients straight from your Magic Bags." + RETIRED_TAIL,
    "Campfire": "Retired. Its recipes are all cooked food, and cooking is table-only now: cook at a real Cooking Bench or a placed Campfire." + RETIRED_TAIL,
}
assert sorted(RETIRED_DESC) == sorted(RETIRED)
for bench_id, bench_item, name, tiers, ups in BENCHES:''')
rep('''        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(item(iid, icon, QUAL[min(t, 7)], rin, WB_REQ), indent=2)
        disp = "%s Accessory %s" % (name, ROMAN[t]) if tiers > 1 else "%s Accessory" % name
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        d = "Put it in your Accessory Bag to craft %s recipes%s from your inventory with /craft.%s" % (
            name, (" up to tier %s" % ROMAN[t]) if tiers > 1 else "",
            (" Upgrade it with the same materials the bench needs for tier %s." % ROMAN[t + 1]) if t < tiers else "")
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        count += 1''', '''        node = item(iid, icon, QUAL[min(t, 7)], rin, WB_REQ)
        disp = "%s Accessory %s" % (name, ROMAN[t]) if tiers > 1 else "%s Accessory" % name
        d = "Put it in your Accessory Bag to craft %s recipes%s from your inventory with /craft.%s" % (
            name, (" up to tier %s" % ROMAN[t]) if tiers > 1 else "",
            (" Upgrade it with the same materials the bench needs for tier %s." % ROMAN[t + 1]) if t < tiers else "")
        if bench_id in RETIRED:   # 0.4.2: asset kept so owned copies still load and render, NO recipe (legacy talisman precedent)
            del node["Recipe"]
            disp += " (retired)"
            d = RETIRED_DESC[bench_id]
            retired_count += 1
        files["Server/Item/Items/Utility/%s.json" % iid] = json.dumps(node, indent=2)
        lang.append("items.%s.name=%s" % (iid, disp)); lang.append("server.items.%s.name=%s" % (iid, disp))
        lang.append("items.%s.description=%s" % (iid, d)); lang.append("server.items.%s.description=%s" % (iid, d))
        count += 1''')

# ---------------------------------------------------------------- Omni: 10 active inputs, does not cover the retired three
rep('''omni_in = []
for bench_id, bench_item, name, tiers, ups in BENCHES:''', '''omni_in = []
for bench_id, bench_item, name, tiers, ups in ACTIVE:   # 0.4.2: the retired three are not inputs any more (13 -> 10)''')
rep('''assert len(omni_in) == 13''', '''assert len(omni_in) == len(ACTIVE) == 10''')
rep('''     "top-tier bench accessories.") % (", ".join(("%s %s" % (b[2], ROMAN[b[3]])) if b[3] > 1 else b[2] for b in BENCHES), len(BENCHES))''',
    '''     "top-tier bench accessories. Alchemy and Cooking are table-only, so the retired Alchemy Bench, Cooking Bench and Campfire "
     "accessories are not part of it and are not covered.") % (", ".join(("%s %s" % (b[2], ROMAN[b[3]])) if b[3] > 1 else b[2] for b in ACTIVE), len(ACTIVE))''')
rep('''print("accessory items:", count)''', '''print("accessory items:", count, "retired (no recipe):", retired_count)
# 0.4.2 build check: no generated recipe takes a retired bench accessory, and no retired accessory has a recipe
_RET_IDS = set("Skyy_Accessory_%s_T%d" % (b[0], t) for b in BENCHES if b[0] in RETIRED for t in range(1, b[3] + 1))
assert retired_count == len(_RET_IDS) == 6, (retired_count, sorted(_RET_IDS))
for _fn, _body in files.items():
    if not _fn.endswith(".json"):
        continue
    _node = json.loads(_body)
    _iid = os.path.basename(_fn)[:-5]
    if _iid in _RET_IDS:
        assert "Recipe" not in _node, "retired accessory still has a recipe: " + _iid
    for _inp in (_node.get("Recipe") or {}).get("Input", []):
        assert _inp.get("ItemId") not in _RET_IDS, "%s still takes the retired %s" % (_iid, _inp.get("ItemId"))''')

# ---------------------------------------------------------------- log line + manifest
rep('''%d bench accessories + Omni, %d talismans in 5 rarities (percent layer on), one bag per profile when SkyyProfiles runs" );
}}""" % (sum(b[3] for b in BENCHES), len(TALISMANS) * 5), pl))''', '''%d bench accessories + Omni (%d retired kept as items that do nothing - Alchemy Bench, Cooking Bench, Campfire), %d talismans in 5 rarities (percent layer on), one bag per profile when SkyyProfiles runs" );
}}""" % (sum(b[3] for b in ACTIVE), sum(b[3] for b in BENCHES if b[0] in RETIRED), len(TALISMANS) * 5), pl))''')
rep('''one bag per SkyyProfiles profile when that mod is installed. Zero dependencies."''',
    '''one bag per SkyyProfiles profile when that mod is installed; the Alchemy Bench, Cooking Bench and Campfire accessories are retired (Alchemy and Cooking are table-only). Zero dependencies."''')

assert 'VERSION = "0.4.2"' in s
assert "assert len(omni_in) == 13" not in s
assert "for b in BENCHES), dfs))" not in s, "a Java bench array still built from BENCHES"
assert s.count("isRetired(id)") >= 8
open(dst, "w", encoding="utf8", newline=NL).write(s)   # keep the line endings of 0.4.1
print("wrote", dst)
