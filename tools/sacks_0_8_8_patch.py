"""Derive SkyySacks/build_skyysacks_0.8.8.py from the SET pin 0.8.7 (the GENERATED build_skyysacks_0.8.7.py; edit THIS file, then
regenerate: python tools/sacks_0_8_8_patch.py; never re-run sacks_0_8_7_patch.py on top of it). Every anchor is asserted; at the end every
change is undone on a copy and compared with 0.8.7 (nothing else changed). Line endings kept.
Run:  python tools/sacks_0_8_8_patch.py   then   python SkyySacks/build_skyysacks_0.8.8.py   (never --deploy from an agent)
Test: python SkyySacks/test_skyysacks_0.8.8.py [--dir <folder inside tools/dev/scratch/>] [--keep]

0.8.8 = FURNACE FUEL + TIER LOGS + /craft TIER ORDER AND NAMES (lean round sacks088, 2026-10-15).
A. FURNACE FUEL (Skyy, on a /craft Furnace screenshot "Furnace I - needs no fuel", no Load fuel row: "where did the add fule section go?").
   ROOT CAUSE: ProcBench.config(bench) took the FIRST BlockType whose ProcessingBench id equals the bench name. Dynamic Seasons 7.0.2
   (BlueOrbit:DynamicSeasons, enabled in the pack) adds Bench_Lightning_Rod, a Processing bench whose Id is also "Furnace" but with NO
   Fuel list (and 0.0 tier speed, no charcoal ExtraOutput). When the asset map hands that one out first, benchNeedsFuel("Furnace") is
   false -> the page draws no Load fuel row / Unload fuel button, the header says "needs no fuel" and the pocket Furnace smelts for free.
   (Proven offline: the real BlockType store, vanilla pack loaded, holds Bench_Furnace + its states with Fuel = 1 slot; Tannery and
   Salvagebench have none, Campfire has one.)
   FIX: config() ranks every BlockType whose ProcessingBench id matches: + 4 the block id is Bench_<bench> (the vanilla block, or a mod's
   override of it), + 2 it comes from the base pack Hytale:Hytale, + 1 it is not a state variant; the highest wins, ties by block id
   (no more map-order luck). When more than one block shares the bench id, one INFO line names the one used and the ones skipped. The
   Furnace gets its Fuel slot, its tier speed (Furnace II = 30 percent faster) and its charcoal byproduct back; the Tannery (no Fuel in
   vanilla) and the Salvagebench stay "needs no fuel".
   A queue that was smelting fuel-free when 0.8.8 lands: ProcBench.advance re-reads needsFuel (true now), no fuel is loaded -> it PAUSES
   ("OUT OF FUEL - load fuel to continue"; progress and queued inputs kept, nothing lost) until fuel is loaded. needsFuel was never saved.
B. TIER LOGS (Skyy, on the SkyyVoid Foraging 'Upgrade to Unique (x1.5)' box needing 138 / 500 Oak logs: "id make the bag upgrade count all
   wood types of the right tier, not just oak.").
   A log id in a Void upgrade cost now stands for EVERY log of its wood tier - research/Gathering-Progression-Spec.md 2.2 (the 5 zone
   tiers; the key logs Oak / Maple / Gumboab / Redwood / Sallow are the ids the Foraging costs name). The LOCKED economy price tiers
   (docs/answered/economy.md 3 / 8 / 20 / 48 / 128) group the logs differently (e.g. Fir / Cedar / Dry / Jungle at 3 with Oak, Sallow with
   Maple at 8); the cost lines follow the Gathering-Progression tiers. The Orchard side group (Apple, Amber, Frostwood, Stormbark,
   Windwillow, Wild Wisteria, Palm) and logs in neither table (Ice, Sadwillow) belong to no tier: they count only as themselves.
     T1 Oak Birch Beech Ash Aspen | T2 Maple Azure | T3 Gumboab Dry Bottletree Palo | T4 Redwood Fir Cedar Poisoned Spiral |
     T5 Sallow Burnt Petrified Bamboo Camphor Banyan Jungle Blue Fig Fire Crystal   (Wood_<name>_Trunk; the _Full / _Half / _Stairs blocks
     are crafted building blocks, not logs, and no stripped trunk exists - so one id per wood)
   The upgrade box shows such a line as "Oak-tier logs" over "138 / 500" (named by the group's first wood, never a tier number - the
   pack's tier numbering is changing, research/Tier-Tags-Plan.md; the icon stays the cost's own log), counting the Void + plain
   inventory stacks of every log of the tier. The upgrade checks the tier total (two lines of one tier add up), then takes each line from
   the log ids the player has most of first (each: the Void first, then plain inventory stacks), never more than the cost; any failure
   part-way rolls the whole payment back (slots restored, Void re-credited - the 0.8.0 all-or-nothing take).
   Other categories unchanged. The cost settings keep their text (no migration); their help line says a log id counts its whole tier.
C. /craft TIER ORDER + REAL NAMES (Skyy, on the Artifacts tab listing 'Skyy Accessory Arcanebench T1', 'Skyy Accessory Armor Bench T1/T2/T3',
   'Skyy Accessory Bag' ... alphabetically with ingredients 'Bench Arcane 0/1', 'Ingredient Bar Copper 5/4', 'Wood_Trunk 6/4': "make sure this
   is sorted by tier too").
   ORDER (every /craft recipe list - Crafting, Artifacts, Smithing, Farming, search, the bench / Campfire tabs - one comparator): craftable
   first (as before), then the TIER, then the item's ItemLevel (SkyyAccessories 0.5.15 numbers its accessories 1..51 in its Workbench tab
   order: tier, then cheapest first; vanilla items carry their own), then the display name, then the id. The tier of an item id: a _T<n>
   suffix = n; a rarity suffix _Common / _Uncommon / _Rare / _Epic / _Legendary / _Mythic = 1..6 (the talisman lines; SkyyAccessories' Epic
   = its 4th tier, beside the T4 bench accessories); the Omni accessory (Skyy_Acc*_Omni) = after every tier; anything else = the material
   ladder the list already used (Crude / none 0, Copper 1, Bronze 2, Iron 3 ... Onyxium 8) - so items without a tier (the Accessory Bag)
   come first. Before, the tier was the material ladder only and the tie-break the raw id (hence the alphabetical Artifacts tab).
   NAMES: a row title, the ingredient line, the fuel buttons and messages and the Furnace / Tannery queue text show the item's translated
   name (its TranslationProperties key through the server's I18nModule, en-US - the lookup PickGive.name has used for pickup cards since
   0.8.3: 'Copper Ingot', 'Arcanist's Workbench', 'Arcane Bench Accessory'); a resource-type ingredient shows its resourceType.<id>.name
   ('Wood_Trunk' -> 'Any Tree Log', 'Fuel' -> 'Any Fuel'). No translation -> the old prettified id. Hits are cached (8192 max).
D. No saved-data change, no new command / system / bridge key. ROLLBACK to 0.8.7: safe (the Furnace may show "needs no fuel" again;
   costs count only the named log again; /craft lists go back to material order + id names).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G   # only its generic Patch helper (anchors asserted once, undo-compare, line endings kept)

P = G.Patch(os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.7.py"), os.path.join(ROOT, "SkyySacks", "build_skyysacks_0.8.8.py"))
assert P.has('VERSION = "0.8.7"\n') and P.has("A:art") and not P.has("benchScore"), "not the live generated SkyySacks 0.8.7"
SYS0, CMD0 = P.s.count("registerSystem("), P.s.count("registerCommand(")
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.8.8 = FURNACE FUEL"):].rstrip() + "\n"

# the wood tiers (Gathering-Progression-Spec 2.2), key log first
LOG_TIERS = (("Oak", "Birch", "Beech", "Ash", "Aspen"),
             ("Maple", "Azure"),
             ("Gumboab", "Dry", "Bottletree", "Palo"),
             ("Redwood", "Fir", "Cedar", "Poisoned", "Spiral"),
             ("Sallow", "Burnt", "Petrified", "Bamboo", "Camphor", "Banyan", "Jungle", "Fig_Blue", "Fire", "Crystal"))

# ---------- header + version
P.rep('''4. No saved-data change, no new command / system / setting / bridge key. ROLLBACK to 0.8.6: safe (the accessory recipes show in Crafting
   again).
"""
''', '''4. No saved-data change, no new command / system / setting / bridge key. ROLLBACK to 0.8.6: safe (the accessory recipes show in Crafting
   again).
''' + NOTE + '''"""
''')
P.rep('VERSION = "0.8.7"\n', 'VERSION = "0.8.8"\n')

# ---------- B. the log tier table (after PD_COST) + its Assets check
P.rep('''assert sorted(PD_COST) == sorted((c, r) for c in PD_CATS for r in (1, 2, 3)) and all(1 <= len(v) <= 6 for v in PD_COST.values())
''', '''assert sorted(PD_COST) == sorted((c, r) for c in PD_CATS for r in (1, 2, 3)) and all(1 <= len(v) <= 6 for v in PD_COST.values())
# 0.8.8 TIER LOGS (Skyy "id make the bag upgrade count all wood types of the right tier, not just oak."): a log id in an upgrade cost counts
# every log of its wood tier (research/Gathering-Progression-Spec.md 2.2, key log first). One id per wood (no stripped trunk exists; the
# _Full / _Half / _Stairs blocks are crafted building blocks, not logs).
LOG_TIERS = %r
LOG_IDS = [["Wood_%%s_Trunk" %% w for w in t] for t in LOG_TIERS]
_flat = [i for t in LOG_IDS for i in t]
assert len(_flat) == len(set(_flat)) == 26 and [t[0] for t in LOG_IDS] == ["Wood_Oak_Trunk", "Wood_Maple_Trunk", "Wood_Gumboab_Trunk",
                                                                          "Wood_Redwood_Trunk", "Wood_Sallow_Trunk"]
# every log the Foraging costs name is the key log of a tier (so each cost line = one tier)
assert all(i in [t[0] for t in LOG_IDS] for r in (1, 2, 3) for i, _q in PD_COST[("Foraging", r)] if i.startswith("Wood_"))
def _log_ids_check():
    import zipfile
    za = os.path.join(B.HYTALE, "install", "release", "package", "game", "latest", "Assets.zip")
    if not os.path.isfile(za):
        print("note: Assets.zip not found - tier log ids not cross-checked")
        return
    with zipfile.ZipFile(za) as z:
        ids = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
    bad = [i for i in _flat if i not in ids]
    if bad:
        raise SystemExit("0.8.8: tier log id(s) not in Assets.zip: " + ", ".join(bad))
    print("tier logs: %%d ids in %%d tiers - all in Assets.zip" %% (len(_flat), len(LOG_IDS)))
_log_ids_check()
''' % (LOG_TIERS,))

# ---------- B. SackDefs: the tier table + lookups (before CATS users compile - defs is compiled first)
P.rep('''defs.addField(CtField.make("public static final String[] CATS = " + _jarr(PD_CATS) + ";", defs))
''', '''defs.addField(CtField.make("public static final String[] CATS = " + _jarr(PD_CATS) + ";", defs))
# 0.8.8 TIER LOGS: LOGT_IDS[i] is a log of wood tier LOGT_TIER[i] (1..5), each tier key log first
defs.addField(CtField.make("public static final String[] LOGT_IDS = " + _jarr(_flat) + ";", defs))
defs.addField(CtField.make("public static final int[] LOGT_TIER = new int[] { " + ", ".join(str(n + 1) for n, t in enumerate(LOG_IDS) for _i in t) + " };", defs))
# the label of each group = its first (key) wood: "Oak-tier logs" (coordinator 2026-10-15: no tier number - the T1..T5 names are changing)
defs.addField(CtField.make("public static final String[] LOGT_KEY = " + _jarr([t[0].replace("_", " ") for t in LOG_TIERS]) + ";", defs))
defs.addMethod(CtNewMethod.make("""
public static int logTier(String id) {
  if (id == null) return 0;
  for (int i = 0; i < LOGT_IDS.length; i++) if (LOGT_IDS[i].equals(id)) return LOGT_TIER[i];
  return 0;
}""", defs))
# the ids a cost line counts: every log of the tier (table order), or just the id itself
defs.addMethod(CtNewMethod.make("""
public static String[] members(String id) {
  int t = logTier(id);
  if (t <= 0) return new String[] { id };
  int n = 0;
  for (int i = 0; i < LOGT_TIER.length; i++) if (LOGT_TIER[i] == t) n++;
  String[] out = new String[n];
  int j = 0;
  for (int i = 0; i < LOGT_TIER.length; i++) if (LOGT_TIER[i] == t) { out[j] = LOGT_IDS[i]; j++; }
  return out;
}""", defs))
# "<key wood>-tier logs" (e.g. "Oak-tier logs") for a tier log, else null (the page then shows the plain count)
defs.addMethod(CtNewMethod.make("""
public static String unitName(String id) {
  int t = logTier(id);
  return (t <= 0 || t > LOGT_KEY.length) ? null : LOGT_KEY[t - 1] + "-tier logs";
}""", defs))
# what two cost lines share: the tier for a log ("logs:T1"), else the id
defs.addMethod(CtNewMethod.make("""
public static String unitKey(String id) {
  int t = logTier(id);
  return t <= 0 ? id : "logs:T" + t;
}""", defs))
# 0.8.8 /craft names (Skyy "make sure this is sorted by tier too" round): the translated text of a key (en-US, the PickGive.name lookup:
# the key, then without "server."); null when there is none (or the module returns the key itself)
defs.addField(CtField.make("public static final java.util.concurrent.ConcurrentHashMap DNAMES = new java.util.concurrent.ConcurrentHashMap();", defs))
defs.addMethod(CtNewMethod.make("""
public static String tr(String key) {
  if (key == null) return null;
  try {
    com.hypixel.hytale.server.core.modules.i18n.I18nModule m = com.hypixel.hytale.server.core.modules.i18n.I18nModule.get();
    if (m == null) return null;
    String n = m.getMessage("en-US", key);
    if ((n == null || n.length() == 0) && key.startsWith("server.")) n = m.getMessage("en-US", key.substring(7));
    if (n == null) return null;
    n = n.trim();
    if (n.length() == 0 || (n.indexOf('.') > 0 && n.indexOf(' ') < 0)) return null;
    return n;
  } catch (Throwable t) { return null; }
}""", defs))
# the item's display name as the player sees it, or null (no item / no translation); hits cached
defs.addMethod(CtNewMethod.make("""
public static String dname(String id) {
  if (id == null) return null;
  Object c = DNAMES.get(id);
  if (c instanceof String) return (String) c;
  String n = null;
  try {
    Object o = com.hypixel.hytale.server.core.asset.type.item.config.Item.getAssetMap().getAsset(id);
    if (o instanceof com.hypixel.hytale.server.core.asset.type.item.config.Item) n = tr(((com.hypixel.hytale.server.core.asset.type.item.config.Item) o).getTranslationKey());
  } catch (Throwable t) { n = null; }
  if (n != null && DNAMES.size() < 8192) DNAMES.put(id, n);
  return n;
}""", defs))
# a resource-type ingredient: resourceType.<id>.name ("Wood_Trunk" -> "Any Tree Log"), else the id with spaces
defs.addMethod(CtNewMethod.make("""
public static String rtName(String rt) {
  if (rt == null) return "?";
  Object c = DNAMES.get("res:" + rt);
  if (c instanceof String) return (String) c;
  String n = tr("server.resourceType." + rt + ".name");
  if (n == null) return rt.replace('_', ' ');
  if (DNAMES.size() < 8192) DNAMES.put("res:" + rt, n);
  return n;
}""", defs))
''')

# ---------- A. probes for the bench ranking
P.rep('''for c, m in ((CRR, "getTimeSeconds"), (PB, "getExtraOutput"), (PB, "getFuel"),''',
      '''# 0.8.8: the bench ranking (block id, base pack, state variant)
for c, m in ((BLT, "isState"), (BLT, "getId"), ("com.hypixel.hytale.assetstore.AssetMap", "getAssetPack"), (BLT, "getAssetMap")):
    B.probe(pool, c, m)
# 0.8.8 /craft order + names: ItemLevel, the translation key, the I18n lookup
for c, m in ((ITM, "getItemLevel"), (ITM, "getTranslationKey"), ("com.hypixel.hytale.server.core.modules.i18n.I18nModule", "getMessage"),
             ("com.hypixel.hytale.server.core.modules.i18n.I18nModule", "get")):
    B.probe(pool, c, m)
for c, m in ((CRR, "getTimeSeconds"), (PB, "getExtraOutput"), (PB, "getFuel"),''')

# ---------- A. config(): rank the candidates instead of taking the first one
P.rep('''# the vanilla ProcessingBench config (Bench_Furnace.json / Bench_Tannery.json BlockType.Bench), found by Bench.Id.
# Only a hit is cached for good; a miss or a failed scan is remembered for 30s only (review fix), so a lookup made before the
# BlockType assets finished loading heals by itself instead of disabling fuel and tier speed until the next restart.
pben.addMethod(CtNewMethod.make(f"""
public static {PB} config(String bench) {{''', '''# the vanilla ProcessingBench config (Bench_Furnace.json / Bench_Tannery.json BlockType.Bench), found by Bench.Id.
# Only a hit is cached for good; a miss or a failed scan is remembered for 30s only (review fix), so a lookup made before the
# BlockType assets finished loading heals by itself instead of disabling fuel and tier speed until the next restart.
# 0.8.8 (Skyy "where did the add fule section go?"): another mod's block may reuse the bench id (Dynamic Seasons' Bench_Lightning_Rod is a
# Processing bench "Furnace" with no Fuel) - rank the candidates: + 4 block id Bench_<bench>, + 2 the base pack Hytale:Hytale, + 1 not a
# state variant; the highest wins, ties by block id (never the asset map's order).
pben.addMethod(CtNewMethod.make(f"""
public static int benchScore(String bench, {BLT} bt) {{
  if (bt == null) return -1;
  String id = String.valueOf(bt.getId());
  int s = 0;
  if (!bt.isState() && !id.startsWith("*")) s += 1;
  String pack = null;
  try {{ pack = {BLT}.getAssetMap().getAssetPack(bt.getId()); }} catch (Throwable t) {{ pack = null; }}
  if ("Hytale:Hytale".equals(pack)) s += 2;
  if (bench != null && id.equalsIgnoreCase("Bench_" + bench)) s += 4;
  return s;
}}""", pben))
pben.addMethod(CtNewMethod.make(f"""
public static {PB} config(String bench) {{''')
P.rep('''  {PB} found = null;
  try {{
    java.util.Iterator it = {BLT}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      Object o = it.next();
      if (!(o instanceof {BLT})) continue;
      {BEN} b = (({BLT}) o).getBench();
      if (b == null || !(b instanceof {PB})) continue;
      String bid = b.getId();
      if (bid != null && bid.equalsIgnoreCase(bench)) {{ found = ({PB}) b; break; }}
    }}
  }} catch (Throwable t) {{''', '''  {PB} found = null;
  int best = -1;
  String bestId = null;
  StringBuilder others = new StringBuilder();
  try {{
    java.util.Iterator it = {BLT}.getAssetMap().getAssetMap().values().iterator();
    while (it.hasNext()) {{
      Object o = it.next();
      if (!(o instanceof {BLT})) continue;
      {BLT} bt = ({BLT}) o;
      {BEN} b = bt.getBench();
      if (b == null || !(b instanceof {PB})) continue;
      String bid = b.getId();
      if (bid == null || !bid.equalsIgnoreCase(bench)) continue;
      String tid = String.valueOf(bt.getId());
      int sc = benchScore(bench, bt);
      if (found == null || sc > best || (sc == best && tid.compareTo(bestId) < 0)) {{
        if (bestId != null && !bestId.startsWith("*")) others.append(others.length() > 0 ? ", " : "").append(bestId);
        found = ({PB}) b; best = sc; bestId = tid;
      }} else if (!tid.startsWith("*")) others.append(others.length() > 0 ? ", " : "").append(tid);
    }}
    if (found != null && others.length() > 0) {{
      try {{ if ({PKG}.SackPool.LOG != null) {PKG}.SackPool.LOG.at(java.util.logging.Level.INFO).log("[SkyySacks] processing: " + bench + " settings from " + bestId + " (other blocks with the same bench id, skipped: " + others + ")"); }} catch (Throwable t2) {{ }}
    }}
  }} catch (Throwable t) {{''')

# ---------- B. VoidStore: the tier count + take order (before upgrade)
P.rep('''vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String upgrade(@PLA@ p, java.util.UUID u, String k, int ci, int from) {''', '''# 0.8.8 TIER LOGS: what a cost line has = the Void + plain inventory stacks of every id it counts (SackDefs.members)
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static long haveOf(String k, @INV@ inv, String id) {
  String[] m = @PKG@.SackDefs.members(id);
  long h = 0L;
  for (int i = 0; i < m.length; i++) h += @PKG@.SackPool.get(k, m[i]) + (long) countIn(inv, m[i], true);
  return h;
}\'\'\'), vst))
# the ids of a cost line, the one the player has most of first (ties: the tier table order, key log first)
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String[] takeOrder(String k, @INV@ inv, String id) {
  String[] m = @PKG@.SackDefs.members(id);
  long[] h = new long[m.length];
  for (int i = 0; i < m.length; i++) h[i] = @PKG@.SackPool.get(k, m[i]) + (long) countIn(inv, m[i], true);
  for (int i = 1; i < m.length; i++) {
    String x = m[i]; long hx = h[i];
    int j = i - 1;
    while (j >= 0 && h[j] < hx) { m[j + 1] = m[j]; h[j + 1] = h[j]; j--; }
    m[j + 1] = x; h[j + 1] = hx;
  }
  return m;
}\'\'\'), vst))
vst.addMethod(CtNewMethod.make(jt(r\'\'\'
public static String upgrade(@PLA@ p, java.util.UUID u, String k, int ci, int from) {''')
P.rep('''  @PKG@.BagMirror.beforeTake(k);
  java.util.Iterator it = cost.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String id = (String) e.getKey();
    long need = ((Long) e.getValue()).longValue();
    long have = @PKG@.SackPool.get(k, id) + (long) countIn(inv, id, true);
    if (have < need) return "-Not enough " + id + " (" + have + " / " + need + ")";
  }''', '''  @PKG@.BagMirror.beforeTake(k);
  // 0.8.8: a tier log line counts every log of its tier; two lines of one tier add up
  java.util.HashMap needU = new java.util.HashMap();
  java.util.Iterator it = cost.entrySet().iterator();
  while (it.hasNext()) {
    java.util.Map.Entry e = (java.util.Map.Entry) it.next();
    String id = (String) e.getKey();
    String uk = @PKG@.SackDefs.unitKey(id);
    Long pn = (Long) needU.get(uk);
    long need = ((Long) e.getValue()).longValue() + (pn == null ? 0L : pn.longValue());
    needU.put(uk, Long.valueOf(need));
    long have = haveOf(k, inv, id);
    String un = @PKG@.SackDefs.unitName(id);
    if (have < need) return "-Not enough " + (un == null ? id : un) + " (" + have + " / " + need + ")";
  }''')
P.rep('''      String id = (String) e.getKey();
      long need = ((Long) e.getValue()).longValue();
      long pp = @PKG@.SackPool.get(k, id);
      long tp = pp < need ? pp : need;
      if (tp > 0L) { @PKG@.SackPool.add(k, id, -tp); fromPool.put(id, Long.valueOf(tp)); }
      long rest = need - tp;
      if (rest > 0L) {
        long got = takePlain(cs, id, rest);
        if (got > 0L) fromInv.put(id, Long.valueOf(got));
        if (got < rest) bad = "-Not enough " + id + " any more - nothing was taken";
      }''', '''      String id = (String) e.getKey();
      long rest = ((Long) e.getValue()).longValue();
      // 0.8.8: the ids of the line, most held first; each: the Void first, then plain inventory stacks; never more than the line
      String[] ord = takeOrder(k, inv, id);
      for (int m = 0; m < ord.length && rest > 0L; m++) {
        String mid = ord[m];
        long pp = @PKG@.SackPool.get(k, mid);
        long tp = pp < rest ? pp : rest;
        if (tp > 0L) {
          @PKG@.SackPool.add(k, mid, -tp);
          Long pv = (Long) fromPool.get(mid);
          fromPool.put(mid, Long.valueOf(tp + (pv == null ? 0L : pv.longValue())));
          rest -= tp;
        }
        if (rest > 0L) {
          long ic = (long) countIn(inv, mid, true);
          long ti = ic < rest ? ic : rest;
          if (ti > 0L) {
            long got = takePlain(cs, mid, ti);
            if (got > 0L) {
              Long iv = (Long) fromInv.get(mid);
              fromInv.put(mid, Long.valueOf(got + (iv == null ? 0L : iv.longValue())));
              rest -= got;
            }
          }
        }
      }
      String un = @PKG@.SackDefs.unitName(id);
      if (rest > 0L) bad = "-Not enough " + (un == null ? id : un) + " any more - nothing was taken";''')

# ---------- B. the upgrade box: "Oak-tier logs" over the count for a tier log line
P.rep('''    "costt": SUI.label("SkyyVCostT" + J_("cx"), "", "default", w=130, h=32, size=13, col=J_("ccol", "#3d913f"), anchor={"left": 4}),
''', '''    "costt": SUI.label("SkyyVCostT" + J_("cx"), "", "default", w=130, h=32, size=13, col=J_("ccol", "#3d913f"), anchor={"left": 4}),
    # 0.8.8 TIER LOGS: a tier log line = "Oak-tier logs" (12) over the count (13), the same 130 x 32 cell
    "costg": SUI.group("SkyyVCostG" + J_("cx"), "Top", w=130, h=32, anchor={"left": 4}),
    "costgn": SUI.label("SkyyVCostN" + J_("cx"), "", "default", w=130, h=14, size=12, col=J_("ccol", "#3d913f")),
    "costgt": SUI.label("SkyyVCostT" + J_("cx"), "", "default", w=130, h=18, size=13, col=J_("ccol", "#3d913f")),
''')
P.rep('''      long have = @PKG@.SackPool.get(k, cid2) + (long) @PKG@.VoidStore.countIn(inv, cid2, true);
      boolean ok = have >= need;
      if (!ok) ready = false;
      String ccol = ok ? "@C:have@" : "@C:out@";
      b.appendInline("#SkyyVCostR" + cr, @@costic@@);
      b.appendInline("#SkyyVCostR" + cr, @@costt@@);''', '''      long have = @PKG@.VoidStore.haveOf(k, inv, cid2);   // 0.8.8: a tier log line counts every log of the tier
      // 0.8.8 review fix: lines of one group need their running SUM (as VoidStore.upgrade checks) - the cell shows that sum
      String uk = @PKG@.SackDefs.unitKey(cid2);
      Long pn = (Long) needU.get(uk);
      if (pn != null) need = need + pn.longValue();
      needU.put(uk, Long.valueOf(need));
      boolean ok = have >= need;
      if (!ok) ready = false;
      String ccol = ok ? "@C:have@" : "@C:out@";
      String un = @PKG@.SackDefs.unitName(cid2);
      b.appendInline("#SkyyVCostR" + cr, @@costic@@);
      if (un == null) b.appendInline("#SkyyVCostR" + cr, @@costt@@);
      else {
        b.appendInline("#SkyyVCostR" + cr, @@costg@@);
        b.appendInline("#SkyyVCostG" + cx, @@costgn@@);
        b.appendInline("#SkyyVCostG" + cx, @@costgt@@);
        b.set("#SkyyVCostN" + cx + ".Text", un);
      }''')

P.rep('''  java.util.ArrayList ce = cost == null ? new java.util.ArrayList() : new java.util.ArrayList(cost.entrySet());
''', '''  java.util.ArrayList ce = cost == null ? new java.util.ArrayList() : new java.util.ArrayList(cost.entrySet());
  java.util.HashMap needU = new java.util.HashMap();   // 0.8.8 review fix: group key -> the need so far (VoidStore.upgrade's rule)
''')

# ---------- B. the cost settings' help line
P.rep('''"live,adv", "Items this upgrade takes - itemId:amount pairs, commas between. Unknown ids are refused.",''',
      '''"live,adv", "Items it takes - itemId:amount pairs, commas between. A log id counts its whole wood tier.",''')

# ---------- C. /craft names: the queue text (ProcBench.outName)
P.rep('''    if (o instanceof {CRR}) {{ {MQ} q = (({CRR}) o).getPrimaryOutput(); if (q != null && q.getItemId() != null) return nm(q.getItemId()); }}''',
      '''    if (o instanceof {CRR}) {{
      {MQ} q = (({CRR}) o).getPrimaryOutput();
      if (q != null && q.getItemId() != null) {{ String dn = {PKG}.SackDefs.dname(q.getItemId()); return dn != null ? dn : nm(q.getItemId()); }}   // 0.8.8: the real name
    }}''')

# ---------- C. /craft order: tier key + sort helpers (RecipeCmp; compare() unchanged - x[2] = tier x 1,000,000 + ItemLevel, x[3] = name + id)
P.rep('''rcmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {''', '''# 0.8.8 (Skyy "make sure this is sorted by tier too"): the tier of an item id - _T<n> = n; _Common .. _Mythic = 1..6; the Omni accessory
# after every tier; else the material ladder (tierOf: none / Crude 0 .. Onyxium 8)
rcmp.addMethod(CtNewMethod.make("""
public static int tierKey(String id) {
  if (id == null) return 0;
  if (id.startsWith("Skyy_Acc") && id.endsWith("_Omni")) return 99;
  int u = id.lastIndexOf("_T");
  if (u >= 0 && u + 2 < id.length() && id.length() - u <= 5) {
    boolean dig = true;
    for (int i = u + 2; i < id.length(); i++) if (!Character.isDigit(id.charAt(i))) dig = false;
    if (dig) return Integer.parseInt(id.substring(u + 2));
  }
  String[] w = new String[] { "_Common", "_Uncommon", "_Rare", "_Epic", "_Legendary", "_Mythic" };
  for (int i = 0; i < w.length; i++) if (id.endsWith(w[i])) return i + 1;
  return tierOf(id);
}""", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public static int level(String id) {
  if (id == null) return 0;
  try {
    Object o = com.hypixel.hytale.server.core.asset.type.item.config.Item.getAssetMap().getAsset(id);
    if (o instanceof com.hypixel.hytale.server.core.asset.type.item.config.Item) {
      int l = ((com.hypixel.hytale.server.core.asset.type.item.config.Item) o).getItemLevel();
      return l < 0 ? 0 : (l > 999999 ? 999999 : l);
    }
  } catch (Throwable t) { }
  return 0;
}""", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public static int sortKey(String id) { return tierKey(id) * 1000000 + level(id); }""", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public static String sortName(String id) {
  if (id == null) return "";
  String n = com.skyy.sacks.SackDefs.dname(id);
  if (n == null) n = id.replace('_', ' ');
  return n.toLowerCase() + " " + id;
}""", rcmp))
rcmp.addMethod(CtNewMethod.make("""
public int compare(Object a, Object b) {''')
_ENT0 = '''    ent.add(new Object[] {{ r0, Integer.valueOf(l0), Integer.valueOf({PKG}.RecipeCmp.tierOf(id0)), id0 == null ? "" : id0 }});'''
_ENT1 = '''    ent.add(new Object[] {{ r0, Integer.valueOf(l0), Integer.valueOf({PKG}.RecipeCmp.sortKey(id0)), {PKG}.RecipeCmp.sortName(id0) }});   // 0.8.8: tier, ItemLevel, name'''
_LOOP = '''  boolean only = Boolean.TRUE.equals(ONLY.get(u));
  java.util.ArrayList ent = new java.util.ArrayList();
  for (int i = 0; i < raw.size(); i++) {{
    {CRR} r0 = ({CRR}) raw.get(i);
    int l0 = limit(r0, mats);
    if (only && l0 <= 0) continue;
    {MQ} o0 = r0.getPrimaryOutput();
    String id0 = o0 == null ? String.valueOf(r0.getId()) : o0.getItemId();
'''
P.rep("  }}\n" + _LOOP + _ENT0, "  }}\n" + _LOOP + _ENT1)
P.rep("  {CIC} mats = viewMats(p, k, wantedOf(raw));\n" + _LOOP + _ENT0, "  {CIC} mats = viewMats(p, k, wantedOf(raw));\n" + _LOOP + _ENT1)
# ---------- C. /craft names: the ingredient line (both row builders) + every CraftPage.pretty
_ING0 = '''      String nm = in[k].getItemId() != null ? pretty(in[k].getItemId()) : (in[k].getResourceTypeId() != null ? in[k].getResourceTypeId() : "?");'''
_ING1 = '''      String nm = in[k].getItemId() != null ? pretty(in[k].getItemId()) : (in[k].getResourceTypeId() != null ? {PKG}.SackDefs.rtName(in[k].getResourceTypeId()) : "?");   // 0.8.8: Any Tree Log'''
_NEED = '''    StringBuilder need = new StringBuilder();
    {MQ}[] in = r.getInput();
    for (int k = 0; in != null && k < in.length; k++) {{
      if (need.length() > 0) need.append("   ");
'''
P.rep("    int allN = lim < room ? lim : room;\n" + _NEED + _ING0, "    int allN = lim < room ? lim : room;\n" + _NEED + _ING1)
P.rep('    String cnote = campTab ? campRowNote(p, u, k, r) : "";\n' + _NEED + _ING0, '    String cnote = campTab ? campRowNote(p, u, k, r) : "";\n' + _NEED + _ING1)
P.rep('''  String bn = com.skyy.sacks.SackDefs.bagName(id);
  if (bn != null) return bn;
  String s = id.replace('_', ' ');''', '''  String bn = com.skyy.sacks.SackDefs.bagName(id);
  if (bn != null) return bn;
  // 0.8.8: the item's real (translated) name when the server has one
  String dn = com.skyy.sacks.SackDefs.dname(id);
  if (dn != null) return dn;
  String s = id.replace('_', ' ');''')

assert P.s.count("registerSystem(") == SYS0 and P.s.count("registerCommand(") == CMD0, "no system / command added"
_i = P.s.index
assert _i("public static int benchScore(") < _i("public static {PB} config(String bench)") < _i("public static boolean benchNeedsFuel(")
assert _i("public static int logTier(String id)") < _i("public static String[] members(String id)") < _i("public static String unitName(") \
    < _i("public static long haveOf(") < _i("public static String[] takeOrder(") < _i("public static String upgrade(@PLA@ p")
P.finish()
