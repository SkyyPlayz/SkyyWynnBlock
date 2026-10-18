"""Derive SkyySkills/build_skyyskills_0.4.49.py from the GENERATED SkyySkills 0.4.48 (build_skyyskills_0.4.48.py = the tools/deploy_set.py SET
pin; 0.4.48 came from 0.4.47 by tools/skills_0_4_48_patch.py, ... 0.4.6 from Skyy's EDITED 0.4.5 - commit ab75b6c; never re-run
skills_0_4_5 or older patches). rep(old, new) with asserted single anchors; at the end every change is undone on a copy and compared with
0.4.48 (nothing else changed); 0.4.48 stays untouched, its line endings are kept (tools/soundpass_gen.Patch).
Run:  python tools/skills_0_4_49_patch.py   then   python SkyySkills/build_skyyskills_0.4.49.py   (never --deploy)
      then  python SkyySkills/test_skyyskills_0.4.49.py
"""
import os, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import soundpass_gen as G

NOTE = '''0.4.49 (2026-10-17) = round ores01 (research/Zone-Ores-Alloys-Spec.md section 5 + 7 B5), the SkyySkills half: Mining XP for the zone ores and
  Smithing XP for their ingots and the alloys. Skyy 2026-10-17: "Yes - start the zone ores + alloys + Furnace Charm round right after the
  current set deploys." + popup "Yes, build with defaults (Recommended)". Item ids are the spec's (SkyyWorldGen 0.7.3 makes them; the build
  checks the ids against that jar when it is in the folder, else the spec list is the source).
  1. MINING XP (xp.properties prefix rows; the longest matching start wins over Ore_ 5, so the ore BLOCKS Ore_<Metal>_<Host>_SkyWynn and the raw
     ores pay the same): prefix.Ore_Lead=Mining:18, prefix.Ore_Chromium=Mining:15, prefix.Ore_Slag=Mining:30, prefix.Ore_Titanium=Mining:25 =
     the zone partner's XP (Thorium 18, Cobalt 15, Adamantite 30, Mithril 25).
  2. SMITHING XP (smithing.xp.<id>, paid per finished smelt: the placed Furnace and the /craft Furnace tab): the 4 ingots = their partner's
     bar XP - Ingredient_Bar_Lead_SkyWynn 18, _Chromium_ 15, _Slag_ 30, _Titanium_ 25; the alloys = (A + B) x 1.25 of the two bars' XP,
     rounded half up - Ingredient_Bar_Bronze (vanilla, Copper + Iron) 16, Dusk (Thorium + Lead) 45, Azurvane (Cobalt + Chromium) 38,
     Cinder (Adamantite + Slag) 75, Lumen (Mithril + Titanium) 63, Electrum (Gold + Silver, spec section 8) 28. An alloy therefore pays a little more than its two ingots' smelts
     together at the same coin value (Smithing XP only; no coins - the Bazaar half closes the coin side).
  3. MIGRATION Zo49Mig (PROJECT-RULES 4; KillXpMig's reviewed block-append machinery): ONCE on an EXISTING xp.properties (setup, right after
     Fm48Mig, before SkillCfg.load): ONE block appended after the last line in the file's own line ending = the marker + ONLY the 14 lines
     the file lacks (an admin's own line for one of these keys is kept untouched, never doubled); no existing line changes (Properties
     check); config-history copy first (CfgHist.snapshot + HealMig.mgSaved); the kit's atomicWrite; one INFO line; a failure = WARN, file
     untouched, retried next start. A fresh default file carries the same lines in its Mining / Smithing sections + the marker.
  No saved player data change, no new command / system. ROLLBACK to 0.4.48: harmless - 0.4.48 reads the 14 lines as ordinary rules (the
  prefix rows match nothing but the new blocks; smithing.xp rows for items that do not exist are ignored); the zone ores simply pay the
  generic Ore_ 5 again if the lines are removed.
'''
ZO_MARK_ID = "SkyySkills 0.4.49 zone ores"
ZO_MARK = "# SkyySkills 0.4.49 zone ores + alloys: Mining XP for Lead / Chromium / Slag / Titanium ore, Smithing XP for their ingots and the alloys."
# (key, value) in file order; Smithing values = the spec's section 3 table / the partner bar's SMITH_XP
ZO_MINING = [("Lead", 18), ("Chromium", 15), ("Slag", 30), ("Titanium", 25)]
ZO_SMITH = [("Ingredient_Bar_Lead_SkyWynn", 18), ("Ingredient_Bar_Chromium_SkyWynn", 15), ("Ingredient_Bar_Slag_SkyWynn", 30),
            ("Ingredient_Bar_Titanium_SkyWynn", 25), ("Ingredient_Bar_Bronze", 16), ("Ingredient_Bar_Dusk_SkyWynn", 45),
            ("Ingredient_Bar_Azurvane_SkyWynn", 38), ("Ingredient_Bar_Cinder_SkyWynn", 75), ("Ingredient_Bar_Lumen_SkyWynn", 63),
            ("Ingredient_Bar_Electrum_SkyWynn", 28)]
_PARTNER = {"Gold": 12, "Silver": 10, "Lead": 18, "Chromium": 15, "Slag": 30, "Titanium": 25, "Copper": 5, "Iron": 8, "Thorium": 18, "Cobalt": 15, "Adamantite": 30, "Mithril": 25}
# the alloy XP rule of the spec: (A + B) x 1.25, rounded half up
for _n, _a, _b, _x in (("Bronze", "Copper", "Iron", 16), ("Dusk", "Thorium", "Lead", 45), ("Azurvane", "Cobalt", "Chromium", 38),
                       ("Cinder", "Adamantite", "Slag", 75), ("Lumen", "Mithril", "Titanium", 63), ("Electrum", "Gold", "Silver", 28)):
    assert int((_PARTNER[_a] + _PARTNER[_b]) * 1.25 + 0.5) == _x, (_n, _x)
ZO_LINES = [("prefix.Ore_%s" % _k, "Mining:%d" % _x) for _k, _x in ZO_MINING] + [("smithing.xp.%s" % _i, str(_x)) for _i, _x in ZO_SMITH]
assert len(ZO_LINES) == 14
ZO_IDS = ["Ore_%s_SkyWynn" % _k for _k, _x in ZO_MINING] + [_i for _i, _x in ZO_SMITH if _i != "Ingredient_Bar_Bronze"]

P = G.Patch(os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.48.py"), os.path.join(ROOT, "SkyySkills", "build_skyyskills_0.4.49.py"))
assert P.has('VERSION = "0.4.48"') and P.has("Fm48Mig") and not P.has("Zo49Mig"), "not the generated SkyySkills 0.4.48 script"
REG0, SYS0 = P.s.count("registerCommand("), P.s.count("registerSystem(")

# ================================================================================================ docstring + version
P.rep('''"""SkyySkills 0.4.48 - build script (derived from the generated 0.4.47 by tools/skills_0_4_48_patch.py - edit the patch, not this file;
''', '''"""SkyySkills 0.4.49 - build script (derived from the generated 0.4.48 by tools/skills_0_4_49_patch.py - edit the patch, not this file;
''' + NOTE + '''  CHECKED: SkyySkills/test_skyyskills_0.4.49.py.
0.4.48 was derived from the generated 0.4.47 by tools/skills_0_4_48_patch.py;
''')
P.rep('VERSION = "0.4.48"', 'VERSION = "0.4.49"')

# ================================================================================================ the ids (SkyyWorldGen 0.7.3 makes them)
P.rep('''    ITEM_IDS = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
''', '''    ITEM_IDS = set(os.path.basename(n)[:-5] for n in z.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
# 0.4.49 (round ores01): SkyyWorldGen 0.7.3's zone ores + ingots + alloys are not in Assets.zip - their ids are the spec's (FINAL); a
# SkyyWorldGen jar that carries them is CHECKED, none built yet = the spec list is the source
ZO_IDS = ''' + json.dumps(ZO_IDS) + '''
ZO_JAR = None
for _jn in sorted(os.listdir(os.path.join(HERE, "..", "SkyyWorldGen"))):
    if _jn.startswith("SkyyWorldGen-") and _jn.endswith(".jar"):
        with zipfile.ZipFile(os.path.join(HERE, "..", "SkyyWorldGen", _jn)) as _zj:
            _have = set(os.path.basename(n)[:-5] for n in _zj.namelist() if n.startswith("Server/Item/Items/") and n.endswith(".json"))
        if "Ore_Lead_SkyWynn" in _have:
            ZO_JAR = _jn
            assert not [i for i in ZO_IDS if i not in _have and i != "Ingredient_Bar_Electrum_SkyWynn"], "0.4.49: %s misses zone metal ids the spec lists: %s" % (_jn, [i for i in ZO_IDS if i not in _have])
ITEM_IDS |= set(ZO_IDS)
print("0.4.49: %d zone metal ids (%s)" % (len(ZO_IDS), ("checked against " + ZO_JAR) if ZO_JAR else "SkyyWorldGen 0.7.3 not built yet - the spec list is the source"))
''')

# ================================================================================================ the default file: Mining rows + SMITH_XP rows + the marker
P.rep('''    L.append("prefix.%s=Mining:%d" % (must_prefix("Ore_" + ore), xp))
''', '''    L.append("prefix.%s=Mining:%d" % (must_prefix("Ore_" + ore), xp))
for ore, xp in ''' + repr(ZO_MINING) + ''':   # 0.4.49: the zone ores = their partner's XP (the ore blocks Ore_<Metal>_<Host>_SkyWynn share the prefix)
    L.append("prefix.%s=Mining:%d" % (must_prefix("Ore_" + ore), xp))
''')
P.rep('''            ("Ingredient_Bar_Onyxium", 40), ("Ingredient_Bar_Prisma", 50), ("Potion_Empty", 2), ("Ingredient_Charcoal", 0)]''',
      '''            ("Ingredient_Bar_Onyxium", 40), ("Ingredient_Bar_Prisma", 50)] + ''' + repr(ZO_SMITH) + ''' + [("Potion_Empty", 2), ("Ingredient_Charcoal", 0)]   # 0.4.49: + the zone ingots + alloys''')
ZO_BLOCK_HEAD = ["# ---------- " + ZO_MARK_ID + " (round ores01) ----------", ZO_MARK,
                 "# Mining XP: the longest matching start wins over Ore_ (5), so the ore blocks and the raw ores of each zone metal pay alike.",
                 "# Smithing XP per finished smelt (placed Furnace and the /craft Furnace tab): an ingot = its partner bar's XP, an alloy = (A + B) x 1.25."]
P.rep('''SMITH_L.append("smithing.oreFactor=1.0")
''', '''SMITH_L.append("smithing.oreFactor=1.0")
ZO_MARK_ID = "''' + ZO_MARK_ID + '''"
ZO_MARK = "''' + ZO_MARK + '''"
assert "=" not in ZO_MARK and ":" in ZO_MARK and len(ZO_MARK) <= 140 and all(ord(_ch) < 128 for _ch in ZO_MARK)
SMITH_L.append(ZO_MARK)   # 0.4.49: Zo49Mig's run-once marker (a fresh file is never migrated; its lines are in the Mining / Smithing sections above)
''')
P.rep('''assert DEFAULTS.count(FM48_MARK_ID) == 1 and _dp.get("perk.fortuneMax") == "0" and _dp.get("perk.fortuneGuard") == "100"   # 0.4.48
''', '''assert DEFAULTS.count(FM48_MARK_ID) == 1 and _dp.get("perk.fortuneMax") == "0" and _dp.get("perk.fortuneGuard") == "100"   # 0.4.48
assert DEFAULTS.count(ZO_MARK_ID) == 1 and all(_dp.get(_k) == _v for _k, _v in ''' + repr(ZO_LINES) + '''), "0.4.49: the default file holds the 14 zone lines + the marker"
''')

# ================================================================================================ Zo49Mig
P.rep('''fm48 = pool.makeClass(PKG + ".Fm48Mig")        # 0.4.48: the one-time perk.fortuneMax 2.0 -> 0 (no cap) update of an existing xp.properties
''', '''fm48 = pool.makeClass(PKG + ".Fm48Mig")        # 0.4.48: the one-time perk.fortuneMax 2.0 -> 0 (no cap) update of an existing xp.properties
zo49 = pool.makeClass(PKG + ".Zo49Mig")        # 0.4.49: the one-time zone ores + alloys XP lines appended to an existing xp.properties
''')
ZO_JAVA = '''
# ---- Zo49Mig (0.4.49, PROJECT-RULES section 4; KillXpMig's block-append machinery): ONCE on an EXISTING xp.properties, setup() right after
# Fm48Mig.run, BEFORE SkillCfg.load. Nothing to do = no file or a comment line holding MARK_ID (a fresh default file carries it). Else ONE
# block appended after the last line in the file's own line ending: the header (marker) + ONLY the 14 zone ore / ingot / alloy XP lines the
# file lacks (a key the file already holds, in any value, is kept as it is). No existing line changes (Properties check), config-history copy
# first, the kit's atomicWrite, one INFO line. A failure = WARN, file untouched, retried next start.
zo49.addField(CtField.make("public static final String MARK_ID = %s;" % json.dumps(ZO_MARK_ID), zo49))
zo49.addField(CtField.make("public static final String HEAD = %s;" % json.dumps("\\n".join(ZO_BLOCK_HEAD) + "\\n"), zo49))
zo49.addField(CtField.make("public static final String[] KEYS = %s;" % jarr([_k for _k, _v in ZO_LINES]), zo49))
zo49.addField(CtField.make("public static final String[] VALS = %s;" % jarr([_v for _k, _v in ZO_LINES]), zo49))
zo49.addField(CtField.make('public static final String WHO = "SkyySkills 0.4.49";', zo49))
assert all(("\\n" + _k + "=" + _v + "\\n") in ("\\n" + DEFAULTS) for _k, _v in ZO_LINES), "0.4.49: a Zo49Mig line is not the default file's"
# pure text step. null = nothing to do; else { new text, String[] added keys }
zo49.addMethod(CtNewMethod.make(J14(r"""
public static Object[] plan(String text) {
  if (text == null) return null;
  java.util.Properties p = new java.util.Properties();
  try { p.load(new java.io.StringReader(text)); } catch (Throwable t) { return null; }
  String[] raw = text.split("\\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) {
      if (s.indexOf(MARK_ID) >= 0) return null;
      k++;
      continue;
    }
    k = @PKG@.CfgFile.end(l, k) + 1;
  }
  StringBuilder blk = new StringBuilder(HEAD);
  java.util.ArrayList add = new java.util.ArrayList();
  for (int i = 0; i < KEYS.length; i++) {
    if (p.getProperty(KEYS[i]) != null) continue;
    blk.append(KEYS[i]).append('=').append(VALS[i]).append('\\n');
    add.add(KEYS[i]);
  }
  boolean crlf = text.indexOf("\\r\\n") >= 0;
  String nl = crlf ? "\\r\\n" : "\\n";
  String b = blk.toString();
  if (crlf) b = b.replace("\\n", "\\r\\n");
  String pre = (text.length() == 0 || text.endsWith("\\n")) ? nl : nl + nl;
  String last = text.endsWith("\\n") ? text.substring(0, text.length() - 1) : text;
  if (last.endsWith("\\r")) last = last.substring(0, last.length() - 1);
  int bs = 0;
  for (int i = last.length() - 1; i >= 0 && last.charAt(i) == '\\\\'; i--) bs++;
  if (bs % 2 == 1 && text.endsWith("\\n")) pre = pre + nl;
  return new Object[] { text + pre + b, (String[]) add.toArray(new String[0]) };
}"""), zo49))
zo49.addMethod(CtNewMethod.make(J14(r"""
public static int idx(String k) {
  for (int i = 0; i < KEYS.length; i++) if (KEYS[i].equals(k)) return i;
  return -1;
}"""), zo49))
# only the planned keys may be new, every old key keeps its value, every new key holds exactly the planned value
zo49.addMethod(CtNewMethod.make(J14(r"""
public static boolean sameAfter(byte[] old, byte[] nb, String[] added) {
  try {
    java.util.Properties a = new java.util.Properties();
    java.util.Properties n = new java.util.Properties();
    a.load(new java.io.ByteArrayInputStream(old));
    n.load(new java.io.ByteArrayInputStream(nb));
    if (n.size() != a.size() + added.length) return false;
    java.util.Iterator it = a.stringPropertyNames().iterator();
    while (it.hasNext()) {
      String k = (String) it.next();
      String got = n.getProperty(k);
      if (got == null || !got.equals(a.getProperty(k))) return false;
    }
    for (int i = 0; i < added.length; i++) {
      int x = idx(added[i]);
      if (x < 0 || a.getProperty(added[i]) != null || !VALS[x].equals(n.getProperty(added[i]))) return false;
    }
    return true;
  } catch (Throwable t) { return false; }
}"""), zo49))
zo49.addMethod(CtNewMethod.make(J14(r"""
public static synchronized String run() {
  java.nio.file.Path f = @PKG@.SkillCfg.FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = plan(new String(old, "ISO-8859-1"));
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    String[] added = (String[]) r[1];
    if (!sameAfter(old, data, added)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.49 (zone ores + alloys XP): the update would change another setting (the file is used as it is; the next start tries again)");
      return "";
    }
    int fi = @PKG@.HealMig.fileIdx();
    if (fi < 0) return "";
    @PKG@.HealMig.mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(fi, old, @PKG@.CfgHist.stamp(), WHO, "before the 0.4.49 zone ores XP update");
    if (!@PKG@.HealMig.mgSaved(fi, old)) {
      @PKG@.SkillCfg.warn("xp.properties NOT updated for 0.4.49 (zone ores + alloys XP): the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String what = added.length == 0 ? "no setting added (every line was already there) - 0.4.49 marker added" : "added " + added.length + " line(s) (Mining XP for the zone ores, Smithing XP for their ingots and the alloys)";
    String msg = "xp.properties updated for 0.4.49: " + what + " - nothing else changed; the old file is in config-history";
    @PKG@.SkillCfg.info(msg);
    return msg;
  } catch (Throwable t) {
    @PKG@.SkillCfg.warn("could not update xp.properties for 0.4.49 (zone ores + alloys XP; the file is used as it is): " + t);
    return "";
  }
}"""), zo49))
'''.replace("ZO_BLOCK_HEAD", repr(ZO_BLOCK_HEAD)).replace("ZO_LINES", repr(ZO_LINES))
P.rep('''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''', ZO_JAVA + '''
# ================= SkillIO.run (0.4.32 C): the SkyySkills-IO jobs''')
P.rep('''  {PKG}.Fm48Mig.run();        // 0.4.48: untouched perk.fortuneMax 2.0 -> 0 (tool Fortune uncapped), once; History first
''', '''  {PKG}.Fm48Mig.run();        // 0.4.48: untouched perk.fortuneMax 2.0 -> 0 (tool Fortune uncapped), once; History first
  {PKG}.Zo49Mig.run();        // 0.4.49: the zone ores + alloys XP lines into an existing xp.properties, once; History first
''')
P.rep('''          rbcm, snd39, rbs39, pd44, fm48,
          hubb, hopen, fort42, ftask42, hpr43, hprfn43, even43):   # 0.4.48: + Fm48Mig;''', '''          rbcm, snd39, rbs39, pd44, fm48, zo49,
          hubb, hopen, fort42, ftask42, hpr43, hprfn43, even43):   # 0.4.49: + Zo49Mig; 0.4.48: + Fm48Mig;''')

assert P.s.count("registerCommand(") == REG0 and P.s.count("registerSystem(") == SYS0, "command / system registrations changed"
P.finish()
