"""Derive SkyyGear/build_skyygear_0.2.18.py from the LIVE 0.2.17 (build_skyygear_0.2.17.py = the tools/deploy_set.py SET pin, itself GENERATED
by tools/gear_0_2_17_patch.py). Edit THIS file, never the generated script; every anchor is asserted. Run:
    python tools/gear_0_2_18_patch.py      then      python SkyyGear/build_skyygear_0.2.18.py      (never --deploy)
Harness: python SkyyGear/test_skyygear_0.2.18.py

0.2.18 = MULTITOOLS (Skyy 2026-10-10, CurseForge screenshot of "Multitools" by InkBlindCat, MIT, Multitools-1.2.9.jar in Skyy's Mods folder:
"this is one of my favoriet mods, but it ruins the normal tools, id like to use it in the pack, BUT make it cost a pickaxe, a hatchet and a
shovel of the same tier to craft. AND the tradeoff is, its slightly slower mining and chopping than the normal tool of that kind, AND you get
less fortune. BUT you get both kinds on the same tool." + "and tools should be reforge able too."; docs/answered/gear.md LOCKED 2026-10-10
MULTITOOLS line). CREDIT: the multitool items, models, textures, recipes and the Multitool_Attack interaction are InkBlindCat's Multitools
(IBC:Multitools 1.2.9, MIT licence; https://www.curseforge.com/hytale/mods - search "Multitools"). SkyyGear ships NONE of its files: it reads
the mod's item ids at runtime and changes two recipes in memory (MIT allows modification; the credit + licence notice live in PACK.md).
  1. THE RECIPE (GearMulti, runtime, no asset file): when the Multitools jar is loaded, each Tool_Hatchet_Pickaxe_Multitool_<Tier> (Crude,
     Copper, Iron, Thorium, Cobalt, Adamantite, Mithril, Onyxium) costs exactly 1 Tool_Pickaxe_<Tier> + 1 Tool_Hatchet_<Tier> + 1
     Tool_Shovel_<Tier>, at the SAME bench / tab / time its own recipe uses (everything but the input list is kept). The engine generates an
     item's recipe as <ItemId>_Recipe_Generated_0 in pack "Hytale:Hytale" (CraftingPlugin.onItemAssetLoad -> CraftingRecipe.getAssetStore()
     .loadAssets("Hytale:Hytale", list), VERIFIED bytecode); GearMulti builds the same object the engine does (the CraftingRecipe copy
     constructor, the id, applyOutputExclusions) with our input and loads it the same way, so the bench lists, the client recipe packets and
     every reader see one recipe under the same id. Runs at start() (every pack loaded) and on every LoadedAssetsEvent(Item) that carries a
     multitool (GearBoxL, LAST priority = after the engine regenerated it); idempotent (an input already ours is left alone). Without the jar
     nothing happens (no item -> no recipe -> no change, one INFO line). SHOVEL RULE (decision, see the report): vanilla Hytale has a
     craftable shovel only in Iron (Crude / Copper / Thorium / Cobalt shovels exist but no recipe makes them; Adamantite / Mithril / Onyxium
     have no shovel at all), so the shovel is required when that tier's shovel exists AND some loaded recipe makes it (Iron today; any pack or
     Hytale update that adds a shovel recipe turns it on at the next start); other tiers cost the pickaxe + the hatchet.
  2. SALVAGE CAP (no dupe, no XP loop): every recipe whose ONLY input is a multitool (its Salvagebench recipe) may give back at most, per
     output item, the sum of what the required tools' own one-input recipes (their salvage) give back. Over it = clamped in memory (the same
     id, loaded the same way); nothing left = the salvage recipe is removed (Onyxium: its pickaxe / hatchet salvage to nothing in vanilla).
     Assembling a multitool pays NO Smithing craft XP (0.2.17's bars-in rule: the craft consumes no bars - the three tools already paid
     theirs), so a craft -> salvage lap can never pay more XP per bar than the single tools do.
  3. STATS (GearTool family 6 = multitool; it was a hatchet to 0.2.17 because of its Tool_Hatchet_ prefix): Mining Power from the pickaxe
     table on rock / ore and Chopping Power from the hatchet table on logs, each x multi.speedPct % (Server Setup -> Gear -> Tools, default
     85); Mining Fortune (pickaxe) + Foraging Fortune (hatchet) x multi.fortunePct % (default 70), both posted to SkyySkills (dd.mining with
     the pickaxe's rock / ore filter + dd.foraging); Wisdom from its modifiers in full. Rarity boost + modifiers work like 0.2.17 tools (the
     whole stat is scaled). The speed share also applies under level (the bonus goes, the trade-off stays: never faster than a single tool),
     so its multiplier may be below 1 (x0.85 = a little slower than a plain pickaxe / hatchet). Worn Mining Sets count on it like on a
     pickaxe. Its own base powers equal the same-tier pickaxe (rock / ore) and hatchet (wood) - asserted against the jar at build when this
     PC has it.
  4. LEVEL GATE: needs Mining AND Foraging at the item's level (one level: its material band, the same as the same-tier pickaxe / hatchet);
     the tooltip says "Requires Mining + Foraging N" and "(you: M)" shows the LOWER of your two levels; a craft stamps the level from the lower
     of the two skills.
  5. RARITY / REFORGE / MODIFIERS: crafted multitools roll a rarity like 0.2.17 tools; modifier pool = the pickaxe pool + the hatchet pool
     (Mining Power, Chopping Power, Mining Fortune, Foraging Fortune, Mining Wisdom, Foraging Wisdom); reforge / level up / identify like tools.
     Multitools made under 0.2.17 (rolled as hatchets: Chopping Power / Foraging Fortune / Foraging Wisdom) keep their rolls - all valid keys.
  6. TOOLTIP: both stat sets + "Multitool: slightly slower and less Fortune than a single tool".
  7. THE MULTITOOLS PLUGIN (com.inkblindcat.multitools.Multitools, read in memory): its setup() only calls super.setup() - no system, no
     event, no command; its Multitool_Attack is a BlockCondition (Tag Wood -> Hatchet_Attack, else Pickaxe_Attack) whose block damage goes
     through the normal DamageBlockEvent that GearTool scales once. Nothing double-applies.
CONFIG (PROJECT-RULES 4): ONE-TIME UPDATE migrate0218 = pure ADDITION (the 0.2.17 shape): heading, marker, the 3 rows with their help lines at the
END of the file, only the keys the file lacks (kept + noted); verified History copy first, atomic write, ISO-8859-1 bytes, run-once marker.
ROLLBACK (for tools/deploy_set.py, reported, not edited here): 0.2.18 -> 0.2.17 is safe: no saved data changes (multitool documents keep their
rolls; 0.2.17 reads them as hatchets); the multitool recipes go back to the Multitools mod's own at that start.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.17.py")
DST = os.path.join(ROOT, "SkyyGear", "build_skyygear_0.2.18.py")
raw = open(SRC, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
assert 'VERSION = "0.2.17"' in s and s.startswith('"""SkyyGear 0.2.17 - build script'), "build_skyygear_0.2.17.py is not the live 0.2.17"
assert "GearMulti" not in s and "MULTI_PRE" not in s, "0.2.17 already has the 0.2.18 parts"


def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, "anchor count %d (want %d): %s" % (n, count, old[:160])
    s = s.replace(old, new)


# ================================================================================================================ header + version
HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
rep('''"""SkyyGear 0.2.17 - build script (javassist via jpype). GENERATED by tools/gear_0_2_17_patch.py from the LIVE 0.2.16 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.17.py -> SkyyGear/SkyyGear-0.2.17.jar (never --deploy).

0.2.17 = ''', '''"""SkyyGear 0.2.18 - build script (javassist via jpype). GENERATED by tools/gear_0_2_18_patch.py from the LIVE 0.2.17 - edit the patch,
never this file. Run: python SkyyGear/build_skyygear_0.2.18.py -> SkyyGear/SkyyGear-0.2.18.jar (never --deploy).

''' + HEAD[HEAD.index("0.2.18 = "):].strip() + '''

0.2.17 (the base, everything below is still true unless 0.2.18 above says otherwise):
0.2.17 = ''')
rep('VERSION = "0.2.17"', 'VERSION = "0.2.18"')

# ================================================================================================================ 1. Python tables + build checks
rep('''TOOL_FAMS = ["Tool_Pickaxe_", "Tool_Shovel_", "Tool_Hatchet_", "Tool_Hoe_", "Tool_Sickle_"]   # GearTool.fam 1..5''',
    '''TOOL_FAMS = ["Tool_Pickaxe_", "Tool_Shovel_", "Tool_Hatchet_", "Tool_Hoe_", "Tool_Sickle_"]   # GearTool.fam 1..5
# 0.2.18 MULTITOOLS (InkBlindCat's Multitools, IBC:Multitools 1.2.9, MIT - credit in PACK.md; SkyyGear ships none of its files): GearTool.fam 6
MULTI_PRE = "Tool_Hatchet_Pickaxe_Multitool_"
MULTI_TIERS = ["Crude", "Copper", "Iron", "Thorium", "Cobalt", "Adamantite", "Mithril", "Onyxium"]
MULTI_KEYS = ["mpow", "cpow", "mfort", "ffort", "mwis", "fwis"]          # the pickaxe pool + the hatchet pool
MULTI_SPD_DEF, MULTI_FORT_DEF = 85, 70''')
rep('''assert len(_TOOL_AZ_IDS) >= 30 and not _TOOL_NOTIER, "vanilla tools without a material tier: %s" % _TOOL_NOTIER''',
    '''assert len(_TOOL_AZ_IDS) >= 30 and not _TOOL_NOTIER, "vanilla tools without a material tier: %s" % _TOOL_NOTIER
# 0.2.18: every multitool tier has a vanilla pickaxe + hatchet of that tier and a GearTool tier word; the shovel is optional (runtime rule)
for _t in MULTI_TIERS:
    assert ("Tool_Pickaxe_" + _t) in _TOOL_AZ_IDS and ("Tool_Hatchet_" + _t) in _TOOL_AZ_IDS, "no vanilla pickaxe / hatchet for multitool tier " + _t
    assert _tool_tier(MULTI_PRE + _t) is not None, "multitool tier word " + _t
MULTI_SHOVELS = [_t for _t in MULTI_TIERS if ("Tool_Shovel_" + _t) in _TOOL_AZ_IDS]
MULTI_SHOVEL_RECIPE = [_t for _t in MULTI_SHOVELS if isinstance((_AZ_JSON.get("Tool_Shovel_" + _t) or {}).get("Recipe"), dict)]
assert MULTI_SHOVELS == ["Crude", "Copper", "Iron", "Thorium", "Cobalt"] and MULTI_SHOVEL_RECIPE == ["Iron"], (MULTI_SHOVELS, MULTI_SHOVEL_RECIPE)
print("0.2.18 multitools: vanilla shovels %s, craftable %s (the shovel is required only where a loaded recipe makes it)" % (MULTI_SHOVELS, MULTI_SHOVEL_RECIPE))
# the Multitools jar (read only, in memory) when this PC has it: its 8 ids exist and its base powers equal the same-tier pickaxe (rock / ore)
# and hatchet (wood) - GearTool's x speed share relies on it; no jar = a note (the build does not need it)
MULTI_JAR = os.path.join(B.MODS_DIR, "Multitools-1.2.9.jar")
if os.path.isfile(MULTI_JAR):
    with zipfile.ZipFile(MULTI_JAR) as _mz:
        _MJ = {}
        for _n in _mz.namelist():
            if _n.startswith("Server/Item/Items/") and _n.endswith(".json"):
                _MJ[os.path.basename(_n)[:-5]] = json.loads(_mz.read(_n).decode("utf-8-sig"))

    def _mres(d, i):
        x = dict(d[i])
        if x.get("Parent") in d:
            p = _mres(d, x.pop("Parent"))
            p.update(x)
            x = p
        return x

    def _mspec(d, i):
        return dict((sp["GatherType"], float(sp.get("Power", 0))) for sp in (_mres(d, i).get("Tool") or {}).get("Specs", []) if isinstance(sp, dict))
    assert sorted(_MJ) == sorted(MULTI_PRE + _t for _t in MULTI_TIERS), "the Multitools jar's item ids changed: %s" % sorted(_MJ)
    for _t in MULTI_TIERS:
        _m, _p, _h = _mspec(_MJ, MULTI_PRE + _t), _mspec(_AZ_JSON, "Tool_Pickaxe_" + _t), _mspec(_AZ_JSON, "Tool_Hatchet_" + _t)
        assert _m.get("Woods") == _h.get("Woods") and all(_m.get(_g) == _p.get(_g) for _g in _p if _g == "Rocks" or _g.startswith("Ore")), (_t, _m, _p, _h)
    print("0.2.18 multitools: Multitools-1.2.9.jar read (in memory): 8 ids, base powers = the same-tier pickaxe / hatchet")
else:
    print("note: Multitools-1.2.9.jar not on this PC - its ids / powers were not re-checked at build (the runtime needs nothing from it)")''')
rep('''TOOL_ONLY = ["", "Rock_,Rubble_,Ore_", "Soil_", "", "", ""]''',
    '''TOOL_ONLY = ["", "Rock_,Rubble_,Ore_", "Soil_", "", "", "", "Rock_,Rubble_,Ore_"]      # 0.2.18: [6] = a multitool's Mining row''')

# ================================================================================================================ 2. config rows + the 0.2.18 block
rep('''    ("tool.xpCraft", "Tool craft Smithing XP", "tools", "int", str(TOOL_XPC_DEF), "0", "1000", "", "%", "live,danger",
     "Crafted tools pay this % of the craft Smithing XP (xp.craft x tier)." + PH, "field:GearCfg.TOOL_XPC"),''',
    '''    ("tool.xpCraft", "Tool craft Smithing XP", "tools", "int", str(TOOL_XPC_DEF), "0", "1000", "", "%", "live,danger",
     "Crafted tools pay this % of the craft Smithing XP (xp.craft x tier)." + PH, "field:GearCfg.TOOL_XPC"),
    # 0.2.18 MULTITOOLS (Skyy 2026-10-10 "make it cost a pickaxe, a hatchet and a shovel of the same tier ... slightly slower ... less fortune")
    ("part.multitool", "Multitools", "tools", "bool", "true", "", "", "", "", "live,part,danger",
     "Cost pickaxe + hatchet (+ shovel if craftable), both tools. Off: hatchet stats; recipe at restart.", "field:GearCfg.MULTI_ON"),
    ("multi.speedPct", "Multitool speed", "tools", "int", str(MULTI_SPD_DEF), "1", "100", "", "%", "live,danger",
     "Mining / Chopping Power = this % of a same-tier pickaxe / hatchet." + PH, "field:GearCfg.MULTI_SPD"),
    ("multi.fortunePct", "Multitool Fortune", "tools", "int", str(MULTI_FORT_DEF), "0", "100", "", "%", "live,danger",
     "Mining / Foraging Fortune = this % of a same-tier pickaxe / hatchet." + PH, "field:GearCfg.MULTI_FORT"),''')
rep('''           "part.toolRarity", "tool.rarityBoost", "tool.spareSlotBoost", "tool.spareSlotMax", "tool.wisdom.cap", "tool.xpCraft"}''',
    '''           "part.toolRarity", "tool.rarityBoost", "tool.spareSlotBoost", "tool.spareSlotMax", "tool.wisdom.cap", "tool.xpCraft",
           # 0.2.18: multitools (recipes, gathering speed / Fortune = economy) - confirm in Server Setup
           "part.multitool", "multi.speedPct", "multi.fortunePct"}''')
rep('''              ("TOOL_SPAREMAX", "double", repr(TOOL_SPAREMAX_DEF)), ("TOOL_WCAP", "double", repr(TOOL_WCAP_DEF)), ("TOOL_XPC", "int", str(TOOL_XPC_DEF))]''',
    '''              ("TOOL_SPAREMAX", "double", repr(TOOL_SPAREMAX_DEF)), ("TOOL_WCAP", "double", repr(TOOL_WCAP_DEF)), ("TOOL_XPC", "int", str(TOOL_XPC_DEF)),
              # 0.2.18 multitools
              ("MULTI_ON", "boolean", "true"), ("MULTI_SPD", "int", str(MULTI_SPD_DEF)), ("MULTI_FORT", "int", str(MULTI_FORT_DEF))]''')
rep('''assert len(set(TR_LINES)) == len(TR_LINES) and len(TR_GROUPS) == len(TR_SCAL) + len(TOOL_KEYS)''',
    '''assert len(set(TR_LINES)) == len(TR_LINES) and len(TR_GROUPS) == len(TR_SCAL) + len(TOOL_KEYS)


# 0.2.18: the multitool block at the very end of a fresh file (migrate0218 appends the missing keys of it, group by group, to an older one)
MT_MARK_ID = "SkyyGear 0.2.18 multitools"
MT_WHO = "SkyyGear 0.2.18"
MT_HEAD = "# ---- Multitools: the Multitools mod's multitools cost a pickaxe + hatchet (+ shovel) and count as both (SkyyGear 0.2.18) ----"
MT_MARK = ("# %s (Skyy 2026-10-10): a multitool (Multitools by InkBlindCat, MIT) costs a pickaxe and a hatchet of its tier (+ its shovel where "
           "a recipe makes one) and gets a pickaxe's and a hatchet's stats, a bit lower" % MT_MARK_ID)
MT_SCAL = ["part.multitool", "multi.speedPct", "multi.fortunePct"]
MT_GROUPS = [("# %s: %s" % (_trr[_k][1], _trr[_k][10]), ["%s=%s" % (_k, _trr[_k][4])]) for _k in MT_SCAL]
MT_LINES = [MT_HEAD, MT_MARK] + [_x for _c, _ls in MT_GROUPS for _x in [_c] + _ls]
assert all(all(32 <= ord(_c) < 127 for _c in _x) for _x in MT_LINES) and all("=" not in _x for _x in (MT_HEAD, MT_MARK))
assert len(set(MT_LINES)) == len(MT_LINES) and len(MT_GROUPS) == 3''')
rep('''    L += [""] + TR_LINES       # 0.2.17: the tool rarity block (migrate0217 adds the missing lines of it to an older file)
    return "\\n".join(L) + "\\n"''', '''    L += [""] + TR_LINES       # 0.2.17: the tool rarity block (migrate0217 adds the missing lines of it to an older file)
    L += [""] + MT_LINES       # 0.2.18: the multitool block (migrate0218 adds the missing lines of it to an older file)
    return "\\n".join(L) + "\\n"''')
rep('''_NT = len(TR_LINES) + 1          # 0.2.17: the tool rarity block (+ its blank line) now ends the file''',
    '''_NM = len(MT_LINES) + 1          # 0.2.18: the multitool block (+ its blank line) now ends the file
_NT = len(TR_LINES) + 1 + _NM    # 0.2.17: the tool rarity block (+ its blank line) right before it''')
rep('''assert _DL[-len(TR_LINES) - 1:] == TR_LINES + [""] and all(_DL.count(_x) == 1 for _x in TR_LINES) and DEFAULT_TEXT.count(TR_MARK_ID) == 1''',
    '''assert _DL[-len(TR_LINES) - 1 - _NM:-_NM] == TR_LINES + [""] and all(_DL.count(_x) == 1 for _x in TR_LINES) and DEFAULT_TEXT.count(TR_MARK_ID) == 1
# 0.2.18: the multitool block once, at the very end, every line unique; the rows read back
assert _DL[-len(MT_LINES) - 1:] == MT_LINES + [""] and all(_DL.count(_x) == 1 for _x in MT_LINES) and DEFAULT_TEXT.count(MT_MARK_ID) == 1
assert _dp.get("part.multitool") == "true" and _dp.get("multi.speedPct") == str(MULTI_SPD_DEF) and _dp.get("multi.fortunePct") == str(MULTI_FORT_DEF)''')

# ================================================================================================================ 3. Java fields
rep('''F(gdf, "public static final String[] T_FAM = %s;" % jarr(TOOL_FAMS))''',
    '''F(gdf, "public static final String[] T_FAM = %s;" % jarr(TOOL_FAMS))
F(gdf, "public static final String MULTI_PRE = %s;" % jstr(MULTI_PRE))          # 0.2.18: GearTool family 6
# fix round: only the 8 tiers GearMulti knows (a 9th multitool from another pack, e.g. Skyys-Modpack's Firetine, stays a hatchet)
F(gdf, "public static final String[] MULTI_T = %s;" % jarr(MULTI_TIERS))''')
rep('''F(gdf, "public static final int[] S_TMASK = %s;" % jints([sum(1 << _f for _f in TOOL_STAT_FAM.get(s[0], ())) for s in STATS]))''',
    '''F(gdf, "public static final int[] S_TMASK = %s;" % jints([sum(1 << _f for _f in TOOL_STAT_FAM.get(s[0], ())) + (1 << 6 if s[0] in MULTI_KEYS else 0)
                                                           for s in STATS]))          # 0.2.18: bit 6 = the multitool pool''')
rep('''F(gcf, "public static final String[] TR_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in TR_GROUPS for _x in _ls]))''',
    '''F(gcf, "public static final String[] TR_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in TR_GROUPS for _x in _ls]))
# 0.2.18: the multitool block (migrate0218)
F(gcf, "public static final String MT_MARK = %s;" % jstr(MT_MARK))
# fix round: true once GearMulti put our pickaxe + hatchet recipe in (stays until a restart, like the recipe itself)
F(gcf, "public static volatile boolean MULTI_SWAP = false;")
F(gcf, "public static final String MT_MARK_ID = %s;" % jstr(MT_MARK_ID))
F(gcf, "public static final String MT_WHO = %s;" % jstr(MT_WHO))
F(gcf, "public static final String MT_HEAD = %s;" % jstr(MT_HEAD))
F(gcf, "public static final String[] MT_GC = %s;" % jarr([_c for _c, _ls in MT_GROUPS]))
F(gcf, "public static final int[] MT_GS = %s;" % jints([len(_ls) for _c, _ls in MT_GROUPS]))
F(gcf, "public static final String[] MT_GL = %s;" % jarr([_x for _c, _ls in MT_GROUPS for _x in _ls]))
F(gcf, "public static final String[] MT_GK = %s;" % jarr([_x.split("=", 1)[0] for _c, _ls in MT_GROUPS for _x in _ls]))''')

# ================================================================================================================ 4. GearCfg: loader + the update
rep('''  TOOL_XPC = (int) plong(p, "tool.xpCraft", 100L, 0L, 1000L);''', '''  TOOL_XPC = (int) plong(p, "tool.xpCraft", 100L, 0L, 1000L);
  // 0.2.18 multitools (Server Setup -> Gear -> Tools)
  MULTI_ON = pbool(p, "part.multitool", true);
  MULTI_SPD = (int) plong(p, "multi.speedPct", 85L, 1L, 100L);
  MULTI_FORT = (int) plong(p, "multi.fortunePct", 70L, 0L, 100L);''')
rep(r'''# setup(), right after migrate0214 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one INFO''',
    r'''# ---- 0.2.18 ONE-TIME UPDATE migrate0218 (PROJECT-RULES section 4): a pure ADDITION, the 0.2.17 shape. null = the marker is already in a comment
# line (a fresh 0.2.18 file carries it); else { new text, String[] notes (keys already there - kept), "part.multitool, ..." (what was added) }
M(gcf, r"""
public static Object[] mtUpdate(String text) {
  String[] raw = text.split("\n", -1);
  java.util.ArrayList l = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) {
    String s0 = raw[i];
    if (s0.endsWith("\r")) s0 = s0.substring(0, s0.length() - 1);
    l.add(s0);
  }
  for (int i = 0; i < l.size(); i++) {
    String t0 = ((String) l.get(i)).trim();
    if ((t0.startsWith("#") || t0.startsWith("!")) && t0.indexOf(MT_MARK_ID) >= 0) return null;
  }
  java.util.Properties pp = new java.util.Properties();
  try { pp.load(new java.io.StringReader(text)); } catch (Throwable x) { }
  int tail = -1;
  int k = 0;
  while (k < l.size()) {
    String s = (String) l.get(k);
    if (@PKG@.CfgFile.isComment(s)) { k++; continue; }
    int e = @PKG@.CfgFile.end(l, k);
    if (e == l.size() - 1) tail = k;
    k = e + 1;
  }
  java.util.ArrayList notes = new java.util.ArrayList();
  StringBuilder added = new StringBuilder();
  java.util.ArrayList blk = new java.util.ArrayList();
  blk.add("");
  blk.add(MT_HEAD);
  blk.add(MT_MARK);
  int at = 0;
  for (int g = 0; g < MT_GC.length; g++) {
    boolean first = true;
    for (int j = 0; j < MT_GS[g]; j++) {
      int x = at + j;
      if (pp.getProperty(MT_GK[x]) != null) { notes.add(MT_GK[x] + " is already in the file - kept"); continue; }
      if (first) { blk.add(MT_GC[g]); first = false; }
      blk.add(MT_GL[x]);
      if (added.length() > 0) added.append(", ");
      added.append(MT_GK[x]);
    }
    at = at + MT_GS[g];
  }
  String crDef = text.indexOf("\r\n") >= 0 ? "\r" : "";
  java.util.ArrayList out = new java.util.ArrayList();
  for (int i = 0; i < raw.length; i++) out.add(raw[i]);
  chPut(out, chEnd(l, tail, raw), blk, crDef);
  StringBuilder sb = new StringBuilder(text.length() + 2048);
  for (int i = 0; i < out.size(); i++) { if (i > 0) sb.append('\n'); sb.append((String) out.get(i)); }
  return new Object[] { sb.toString(), (String[]) notes.toArray(new String[0]), added.toString() };
}""")
M(gcf, r"""
public static synchronized String migrate0218() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    String otext = new String(old, "ISO-8859-1");
    Object[] r = mtUpdate(otext);
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    lvKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), MT_WHO, "before the 0.2.18 multitool update");
    if (!lvSaved(old)) {
      @PKG@.Gear.warn("config.properties NOT updated with the 0.2.18 multitool rows: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the rows still work at their defaults; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] notes = (String[]) r[1];
    String add = (String) r[2];
    int n = add.length() == 0 ? 0 : add.split(", ").length;
    String msg = "config.properties: the 0.2.18 multitool rows were added at the end (" + n + " lines: the switch, the speed share, the Fortune share); no value changed; the old file is kept in config-history";
    @PKG@.Gear.info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < notes.length; i++) { @PKG@.Gear.info(notes[i]); all.append('\n').append(notes[i]); }
    @PKG@.GearLog.line("CONFIG 0.2.18 multitools: added " + n + " keys" + (notes.length > 0 ? "; " + notes.length + " notes" : ""));
    return all.toString();
  } catch (Throwable t) {
    @PKG@.Gear.warn("could not add the 0.2.18 multitool rows to config.properties (the file is used as it is; every row works at its default): " + t);
    return "";
  }
}""")
# setup(), right after migrate0214 and BEFORE load() + CfgPub.start: History copy verified first (lvSaved), atomic write (ISO-8859-1 bytes), one INFO''')
rep('''  @PKG@.GearCfg.migrate0217();
  @PKG@.GearCfg.load();''', '''  @PKG@.GearCfg.migrate0217();
  @PKG@.GearCfg.migrate0218();
  @PKG@.GearCfg.load();''')

# ================================================================================================================ 5. GearData: family 6
rep('''M(gdt, "public static boolean isTool(String id) { return id != null && id.startsWith(\\"Tool_\\") && !skyyItem(id); }")''',
    '''M(gdt, "public static boolean isTool(String id) { return id != null && id.startsWith(\\"Tool_\\") && !skyyItem(id); }")
# 0.2.18: a multitool of the Multitools mod (Tool_Hatchet_Pickaxe_Multitool_<Tier>) while part.multitool is on (off = a hatchet, the 0.2.17 view)
M(gdt, r"""
public static boolean multiId(String id) {
  if (id == null || !id.startsWith(@PKG@.GearDefs.MULTI_PRE) || !isTool(id)) return false;
  String t = id.substring(@PKG@.GearDefs.MULTI_PRE.length());
  for (int i = 0; i < @PKG@.GearDefs.MULTI_T.length; i++) if (@PKG@.GearDefs.MULTI_T[i].equals(t)) return true;
  return false;
}""")
M(gdt, "public static boolean isMulti(String id) { return @PKG@.GearCfg.MULTI_ON && multiId(id); }")''')
rep('''  if (id == null || !isTool(id)) return 0;
  for (int i = 0; i < @PKG@.GearDefs.T_FAM.length; i++) if (id.startsWith(@PKG@.GearDefs.T_FAM[i])) return i + 1;''',
    '''  if (id == null || !isTool(id)) return 0;
  if (isMulti(id)) return 6;          // 0.2.18: the multitool family (before its Tool_Hatchet_ prefix)
  for (int i = 0; i < @PKG@.GearDefs.T_FAM.length; i++) if (id.startsWith(@PKG@.GearDefs.T_FAM[i])) return i + 1;''')

# ================================================================================================================ 6. GearGate: Mining AND Foraging
rep(r'''# Object[] { Boolean ok, String skill (label), Integer need, Integer have, Boolean enforced, Integer state }''',
    r'''# 0.2.18: a multitool needs Mining AND Foraging: the LOWER of the two levels (-2 = no SkyySkills)
M(ggt, r"""
public static int haveBoth(java.util.UUID u) {
  int a = have(u, "Mining");
  int b = have(u, "Foraging");
  if (a == -2 || b == -2) return -2;
  if (a < 0) a = 0;
  if (b < 0) b = 0;
  return a < b ? a : b;
}""")
# 0.2.18: check() for a multitool (a gathering gate: never enforced, the tool works like a plain one under level); label "Mining + Foraging"
M(ggt, r"""
public static Object[] checkMulti(java.util.UUID u, int need) {
  String label = "Mining + Foraging";
  int fl = @PKG@.GearLevel.floor(0);
  if (u == null) return new Object[] { Boolean.TRUE, label, Integer.valueOf(need), Integer.valueOf(-1), Boolean.FALSE, Integer.valueOf(4) };
  if (!@PKG@.GearCfg.PART_GATE) return new Object[] { Boolean.TRUE, label, Integer.valueOf(need), Integer.valueOf(-1), Boolean.FALSE, Integer.valueOf(5) };
  int h = skillsOn() ? haveBoth(u) : -2;
  if (h == -2) {
    boolean pass = !"block".equals(@PKG@.GearCfg.NO_SKILLS) || need <= fl;
    return new Object[] { Boolean.valueOf(pass), label, Integer.valueOf(need), Integer.valueOf(-2), Boolean.FALSE, Integer.valueOf(2) };
  }
  return new Object[] { Boolean.valueOf(@PKG@.GearLevel.floor(h) >= need), label, Integer.valueOf(need), Integer.valueOf(h), Boolean.FALSE, Integer.valueOf(0) };
}""")
# Object[] { Boolean ok, String skill (label), Integer need, Integer have, Boolean enforced, Integer state }''')
rep('''  if (@PKG@.GearMine.isPiece(id)) { gate = "Mining"; enforced = true; }''',
    '''  if (@PKG@.GearMine.isPiece(id)) { gate = "Mining"; enforced = true; }
  if (@PKG@.GearData.isMulti(id)) return checkMulti(u, need);          // 0.2.18: Mining AND Foraging''')

# ================================================================================================================ 7. GearRoll: craft level + XP
rep('''public static int craftHave(String id, java.util.UUID u) {
  if (u == null) return -1;''', '''public static int craftHave(String id, java.util.UUID u) {
  if (u == null) return -1;
  if (@PKG@.GearData.isMulti(id)) { int hb = @PKG@.GearGate.haveBoth(u); return hb == -2 ? -1 : hb; }          // 0.2.18: the lower of Mining / Foraging''')
rep('''public static String craftLabel(String id, java.util.UUID u) {''', '''public static String craftLabel(String id, java.util.UUID u) {
  if (@PKG@.GearData.isMulti(id)) return "Mining + Foraging";          // 0.2.18''')
rep('''public static int toolXpPct(String id) {
  if (id == null) return 100;''', '''public static int toolXpPct(String id) {
  if (id == null) return 100;
  if (@PKG@.GearCfg.MULTI_SWAP && @PKG@.GearData.multiId(id)) return 0;          // 0.2.18: our recipe uses no bars - its tools already paid (fix round: also after part.multitool goes off, until the restart)''')

# ================================================================================================================ 8. GearMulti: the recipe + the salvage cap
rep('''gboxl.addInterface(pool.get("java.util.function.Consumer"))''', r'''# ================================================================= 0.2.18 GearMulti: THE MULTITOOL RECIPE + THE SALVAGE CAP (see the header)
# Multitools by InkBlindCat (IBC:Multitools, MIT) - nothing of it is shipped; its item ids are read at runtime. The engine makes an item's recipe
# <ItemId>_Recipe_Generated_0 in pack "Hytale:Hytale" (CraftingPlugin.onItemAssetLoad, VERIFIED bytecode: new CraftingRecipe(copy), outputs /
# primaryOutput, applyOutputExclusions(), id = generateIdFromItemRecipe(item, 0), then CraftingRecipe.getAssetStore().loadAssets("Hytale:Hytale",
# list)). GearMulti builds the very same object with our input list and loads it the same way (onRecipeLoad then swaps it in every bench
# registry; clients get it with the recipe packets). id / input / outputs / primaryOutput are protected fields and applyOutputExclusions is
# package-private: reached once by reflection (asserted at build), WARN + "their recipe stays" when that ever fails.
MULTI_ENGINE = {"ASTO": "com.hypixel.hytale.assetstore.AssetStore", "DAMQ": "com.hypixel.hytale.assetstore.map.DefaultAssetMap"}
for _k in MULTI_ENGINE:
    assert _k not in T, "0.2.18 token clashes: " + _k
T.update(MULTI_ENGINE)
for c, m in ((CRR, "getAssetStore"), (CRR, "getAssetMap"), (CRR, "generateIdFromItemRecipe"), (CRR, "getInput"), (CRR, "getOutputs"),
             (CRR, "getPrimaryOutput"), (CRR, "getId"), (MULTI_ENGINE["ASTO"], "loadAssets"), (MULTI_ENGINE["ASTO"], "removeAssets"),
             (MULTI_ENGINE["DAMQ"], "getAsset"), (MULTI_ENGINE["DAMQ"], "getAssetMap"), (MQ, "clone"), (MQ, "getItemId"), (MQ, "getQuantity")):
    B.probe(pool, c, m)
_crr = pool.get(CRR)
for _f in ("id", "input", "outputs", "primaryOutput"):
    assert str(_crr.getDeclaredField(_f).getType().getName()) in ("java.lang.String", MQ, MQ + "[]"), "CraftingRecipe." + _f
assert len(_crr.getDeclaredMethod("applyOutputExclusions").getParameterTypes()) == 0, "CraftingRecipe.applyOutputExclusions()"
assert any(len(_c.getParameterTypes()) == 1 and str(_c.getParameterTypes()[0].getName()) == CRR and J0["Modifier"].isPublic(_c.getModifiers())
           for _c in _crr.getDeclaredConstructors()), "the public CraftingRecipe copy constructor"
assert any([str(_p.getName()) for _p in _c.getParameterTypes()] == ["java.lang.String", "java.lang.String", "java.lang.String", "int", BD]
           and J0["Modifier"].isPublic(_c.getModifiers()) for _c in pool.get(MQ).getDeclaredConstructors()), "new MaterialQuantity(item, res, tag, qty, meta)"
_gcr = _crr.getDeclaredMethod("generateIdFromItemRecipe")
assert J0["Modifier"].isStatic(_gcr.getModifiers()) and [str(_p.getName()) for _p in _gcr.getParameterTypes()] == [ITM, "int"], "generateIdFromItemRecipe(Item, int)"
gmulti = mk("GearMulti")
F(gmulti, "public static final String[] TW = %s;" % jarr(MULTI_TIERS))
F(gmulti, 'public static final String PACK = "Hytale:Hytale";')
# recipe id -> what it costs now ("Tool_Pickaxe_Copper + Tool_Hatchet_Copper"), salvage recipe id -> "capped" / "removed"
F(gmulti, "public static final java.util.concurrent.ConcurrentHashMap DONE = new java.util.concurrent.ConcurrentHashMap();")
F(gmulti, "public static final java.util.concurrent.ConcurrentHashMap SALV = new java.util.concurrent.ConcurrentHashMap();")
F(gmulti, 'public static volatile String LAST = "not run yet";')
F(gmulti, "public static volatile boolean STARTED = false;")
F(gmulti, "public static volatile java.lang.reflect.Field FID = null;")
F(gmulti, "public static volatile java.lang.reflect.Field FIN = null;")
F(gmulti, "public static volatile java.lang.reflect.Field FOUT = null;")
F(gmulti, "public static volatile java.lang.reflect.Field FPO = null;")
F(gmulti, "public static volatile java.lang.reflect.Method MEX = null;")
F(gmulti, "public static final long[] N = new long[4];")          # 0 recipes replaced, 1 salvage capped, 2 salvage removed, 3 runs
M(gmulti, r"""
public static synchronized boolean refl() {
  if (FID != null && FIN != null && FOUT != null && FPO != null && MEX != null) return true;
  try {
    Class c = @CRR@.class;
    java.lang.reflect.Field a = c.getDeclaredField("id");
    java.lang.reflect.Field b = c.getDeclaredField("input");
    java.lang.reflect.Field o = c.getDeclaredField("outputs");
    java.lang.reflect.Field p = c.getDeclaredField("primaryOutput");
    java.lang.reflect.Method m = c.getDeclaredMethod("applyOutputExclusions", new Class[0]);
    a.setAccessible(true);
    b.setAccessible(true);
    o.setAccessible(true);
    p.setAccessible(true);
    m.setAccessible(true);
    FID = a;
    FIN = b;
    FOUT = o;
    FPO = p;
    MEX = m;
    return true;
  } catch (Throwable t) {
    @PKG@.Gear.warnOnce("multirefl", "Multitools: the engine's recipe fields could not be reached (" + t + ") - the Multitools mod's own recipes stay");
    return false;
  }
}""")
M(gmulti, "public static String mid(int i) { return @PKG@.GearDefs.MULTI_PRE + TW[i]; }")
# every item id some loaded recipe makes (primary output + outputs)
M(gmulti, r"""
public static java.util.HashSet made(java.util.Collection rs) {
  java.util.HashSet out = new java.util.HashSet();
  java.util.Iterator it = rs.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @CRR@)) continue;
    @CRR@ r = (@CRR@) o;
    @MQ@ po = r.getPrimaryOutput();
    if (po != null && po.getItemId() != null) out.add(po.getItemId());
    @MQ@[] os = r.getOutputs();
    if (os != null) for (int i = 0; i < os.length; i++) if (os[i] != null && os[i].getItemId() != null) out.add(os[i].getItemId());
  }
  return out;
}""")
# the input ids tier i's multitool costs: its pickaxe + hatchet, + its shovel when that item exists AND a loaded recipe makes it (vanilla: Iron
# only); null = the pickaxe or the hatchet of that tier is missing (the Multitools mod's own recipe then stays)
M(gmulti, r"""
public static String[] want(int i, java.util.HashSet made) {
  String p = "Tool_Pickaxe_" + TW[i];
  String h = "Tool_Hatchet_" + TW[i];
  String v = "Tool_Shovel_" + TW[i];
  if (@PKG@.Gear.item(p) == null || @PKG@.Gear.item(h) == null) return null;
  if (@PKG@.Gear.item(v) != null && made != null && made.contains(v)) return new String[] { p, h, v };
  return new String[] { p, h };
}""")
M(gmulti, r"""
public static boolean same(@MQ@[] in, String[] w) {
  if (in == null || w == null || in.length != w.length) return false;
  for (int k = 0; k < w.length; k++) {
    if (in[k] == null || !w[k].equals(in[k].getItemId()) || in[k].getQuantity() != 1 || in[k].getResourceTypeId() != null) return false;
  }
  return true;
}""")
M(gmulti, r"""
public static String text(String[] w) {
  StringBuilder sb = new StringBuilder();
  for (int k = 0; k < w.length; k++) { if (k > 0) sb.append(" + "); sb.append(w[k]); }
  return sb.toString();
}""")
# the engine's own recipe object (copy constructor) with our input list; the id, outputs, bench, time, knowledge kept
M(gmulti, r"""
public static @CRR@ withInput(@CRR@ r, String[] w) throws Exception {
  @CRR@ c = new @CRR@(r);
  @MQ@[] in = new @MQ@[w.length];
  for (int k = 0; k < w.length; k++) in[k] = new @MQ@(w[k], null, null, 1, null);
  FIN.set(c, in);
  FID.set(c, r.getId());
  MEX.invoke(c, new Object[0]);
  return c;
}""")
# a copy with other outputs (the salvage cap); the primary output = the kept entry of the same item, else the first one
M(gmulti, r"""
public static @CRR@ withOutputs(@CRR@ r, @MQ@[] outs) throws Exception {
  @CRR@ c = new @CRR@(r);
  @MQ@ po = r.getPrimaryOutput();
  @MQ@ np = outs.length > 0 ? outs[0] : null;
  if (po != null && po.getItemId() != null) for (int k = 0; k < outs.length; k++) if (po.getItemId().equals(outs[k].getItemId())) { np = outs[k]; break; }
  FOUT.set(c, outs);
  FPO.set(c, np);
  FID.set(c, r.getId());
  MEX.invoke(c, new Object[0]);
  return c;
}""")
# recipes with exactly one item input, by that item id (salvage recipes; a tool's one-input recipes = what it salvages to)
M(gmulti, r"""
public static java.util.HashMap byInput(java.util.Collection rs) {
  java.util.HashMap out = new java.util.HashMap();
  java.util.Iterator it = rs.iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (!(o instanceof @CRR@)) continue;
    @MQ@[] in = ((@CRR@) o).getInput();
    if (in == null || in.length != 1 || in[0] == null || in[0].getItemId() == null) continue;
    java.util.ArrayList l = (java.util.ArrayList) out.get(in[0].getItemId());
    if (l == null) { l = new java.util.ArrayList(); out.put(in[0].getItemId(), l); }
    l.add(o);
  }
  return out;
}""")
M(gmulti, r"""
public static int qtyOf(@MQ@[] outs, String item) {
  if (outs == null || item == null) return 0;
  int n = 0;
  for (int k = 0; k < outs.length; k++) if (outs[k] != null && item.equals(outs[k].getItemId())) n = n + outs[k].getQuantity();
  return n;
}""")
# what the required tools give back of one item: per tool the most any of its one-input recipes gives, summed
M(gmulti, r"""
public static int allowed(java.util.HashMap by, String[] w, String item) {
  int sum = 0;
  for (int k = 0; k < w.length; k++) {
    java.util.ArrayList l = (java.util.ArrayList) by.get(w[k]);
    if (l == null) continue;
    int best = 0;
    for (int j = 0; j < l.size(); j++) {
      int q = qtyOf(((@CRR@) l.get(j)).getOutputs(), item);
      if (q > best) best = q;
    }
    sum = sum + best;
  }
  return sum;
}""")
# the capped output list of a multitool salvage recipe; null = nothing over the cap (unchanged)
M(gmulti, r"""
public static @MQ@[] capped(@CRR@ s, java.util.HashMap by, String[] w) {
  @MQ@[] outs = s.getOutputs();
  if (outs == null) return null;
  java.util.HashMap rem = new java.util.HashMap();
  java.util.ArrayList keep = new java.util.ArrayList();
  boolean changed = false;
  for (int k = 0; k < outs.length; k++) {
    @MQ@ o = outs[k];
    if (o == null) { changed = true; continue; }
    String item = o.getItemId();
    if (item == null) { keep.add(o); continue; }          // a resource-type output (none today) is kept as it is
    Integer r0 = (Integer) rem.get(item);
    int left = r0 == null ? allowed(by, w, item) : r0.intValue();
    int q = o.getQuantity();
    if (q <= left) { keep.add(o); rem.put(item, Integer.valueOf(left - q)); continue; }
    changed = true;
    if (left > 0) keep.add(o.clone(left));
    rem.put(item, Integer.valueOf(0));
  }
  if (!changed) return null;
  return (@MQ@[]) keep.toArray(new @MQ@[0]);
}""")
M(gmulti, r"""
public static synchronized String salvage(java.util.Collection all, java.util.HashSet made) {
  java.util.HashMap by = byInput(all);
  java.util.ArrayList put = new java.util.ArrayList();
  java.util.ArrayList drop = new java.util.ArrayList();
  int seen = 0;
  for (int i = 0; i < TW.length; i++) {
    if (@PKG@.Gear.item(mid(i)) == null) continue;
    String[] w = want(i, made);
    java.util.ArrayList ms = (java.util.ArrayList) by.get(mid(i));
    if (w == null || ms == null) continue;
    for (int j = 0; j < ms.size(); j++) {
      @CRR@ sr = (@CRR@) ms.get(j);
      seen++;
      @MQ@[] nc = capped(sr, by, w);
      if (nc == null) continue;
      if (!refl()) return "salvage cap OFF (engine fields unreachable)";
      try {
        if (nc.length == 0) { drop.add(sr.getId()); SALV.put(sr.getId(), "removed"); }
        else { put.add(withOutputs(sr, nc)); SALV.put(sr.getId(), "capped"); }
      } catch (Throwable t) { @PKG@.Gear.warnOnce("multisalv:" + sr.getId(), "Multitools: could not cap the salvage recipe " + sr.getId() + " (" + t + ")"); }
    }
  }
  if (!put.isEmpty()) { @CRR@.getAssetStore().loadAssets(PACK, put); N[1] = N[1] + (long) put.size(); }
  if (!drop.isEmpty()) { @CRR@.getAssetStore().removeAssets(drop); N[2] = N[2] + (long) drop.size(); }
  return seen + " salvage recipe(s) checked, " + put.size() + " capped, " + drop.size() + " removed (a multitool gives back at most what its tools do)";
}""")
# one tier: 0 = no multitool item, 1 = already ours, 2 = added to list, 3 = left as it was (no recipe / no pickaxe or hatchet / engine fields)
M(gmulti, r"""
public static int one(int i, java.util.HashSet made, java.util.ArrayList list, StringBuilder two) throws Exception {
  @ITM@ it = @PKG@.Gear.item(mid(i));
  if (it == null) return 0;
  String rid = @CRR@.generateIdFromItemRecipe(it, 0);
  Object o = @CRR@.getAssetMap().getAsset(rid);
  if (!(o instanceof @CRR@)) return 3;
  String[] w = want(i, made);
  if (w == null) {
    @PKG@.Gear.warnOnce("multiwant:" + TW[i], "Multitools: no vanilla pickaxe / hatchet for " + TW[i] + " - the " + mid(i) + " recipe stays the Multitools mod's own");
    return 3;
  }
  if (w.length == 2) { if (two.length() > 0) two.append(", "); two.append(TW[i]); }
  @CRR@ r = (@CRR@) o;
  DONE.put(rid, text(w));
  if (same(r.getInput(), w)) return 1;
  if (!refl()) return 3;
  list.add(withInput(r, w));
  return 2;
}""")
# THE ENTRY (start() + the LoadedAssetsEvent(Item) hook): idempotent; without the Multitools jar = nothing to do
M(gmulti, r"""
public static synchronized String replaceAll() {
  N[3] = N[3] + 1L;
  if (!@PKG@.GearCfg.MULTI_ON) { LAST = "multitools OFF (part.multitool) - the Multitools mod's own recipes"; return LAST; }
  int[] c = new int[4];
  java.util.ArrayList list = new java.util.ArrayList();
  StringBuilder two = new StringBuilder();
  java.util.HashSet mk = null;
  String err = null;
  try {
    mk = made(new java.util.ArrayList(@CRR@.getAssetMap().getAssetMap().values()));
    for (int i = 0; i < TW.length; i++) { int k = one(i, mk, list, two); c[k] = c[k] + 1; }
    if (!list.isEmpty()) { @CRR@.getAssetStore().loadAssets(PACK, list); N[0] = N[0] + (long) list.size(); }
    if (c[1] + c[2] > 0) @PKG@.GearCfg.MULTI_SWAP = true;          // fix round: our recipe is live (no craft XP for a multitool until a restart)
  } catch (Throwable t) { err = "" + t; }
  if (err != null) {
    @PKG@.Gear.warn("Multitools: the multitool recipes could not be changed (" + err + ") - the Multitools mod's own recipes stay");
    LAST = "multitools: recipe change FAILED (" + err + ")";
    return LAST;
  }
  int found = c[1] + c[2] + c[3];
  if (found == 0) { LAST = "multitools: the Multitools mod is not loaded - nothing to change"; return LAST; }
  String sv = "";
  try { sv = salvage(new java.util.ArrayList(@CRR@.getAssetMap().getAssetMap().values()), mk); }
  catch (Throwable t2) { sv = "salvage cap FAILED (" + t2 + ")"; @PKG@.Gear.warn("Multitools: the salvage cap failed (" + t2 + ") - their salvage recipes stay"); }
  LAST = "multitools: " + found + " found, " + c[2] + " recipe(s) set to pickaxe + hatchet (+ shovel) of their tier, " + c[1] + " already set" + (c[3] > 0 ? ", " + c[3] + " left as they were" : "") + (two.length() > 0 ? "; no craftable shovel for " + two.toString() + " (pickaxe + hatchet)" : "") + "; " + sv + "; speed " + @PKG@.GearCfg.MULTI_SPD + "%, Fortune " + @PKG@.GearCfg.MULTI_FORT + "% of a single tool";
  return LAST;
}""")
# LoadedAssetsEvent(Item) (GearBoxL, LAST priority: after CraftingPlugin regenerated the item's recipe): a reloaded multitool gets ours again
M(gmulti, r"""
public static int onLoaded(Object e) {
  if (!@PKG@.GearCfg.MULTI_ON || !(e instanceof @LAE@)) return 0;
  java.util.Map m = ((@LAE@) e).getLoadedAssets();
  if (m == null || m.isEmpty()) return 0;
  boolean any = false;
  java.util.Iterator it = new java.util.ArrayList(m.values()).iterator();
  while (it.hasNext()) {
    Object o = it.next();
    if (o instanceof @ITM@ && @PKG@.GearData.isMulti(((@ITM@) o).getId())) { any = true; break; }
  }
  if (!any) return 0;
  String r = replaceAll();
  if (STARTED) @PKG@.Gear.info("reloaded multitools: " + r);
  return 1;
}""")
M(gmulti, r"""
public static String start() {
  STARTED = true;
  return replaceAll();
}""")
TOOL_MULTI_CLASSES = [gmulti]
gboxl.addInterface(pool.get("java.util.function.Consumer"))''')
rep('''  try { @PKG@.GearABox.onLoaded(e); }''', '''  // 0.2.18: a reloaded multitool (the engine just regenerated its recipe) gets the pickaxe + hatchet (+ shovel) recipe again
  try { @PKG@.GearMulti.onLoaded(e); }
  catch (Throwable t3) { @PKG@.Gear.warnOnce("multilistener", "multitool recipe listener failed (" + t3 + ") - a reloaded multitool keeps the Multitools recipe until a restart"); }
  try { @PKG@.GearABox.onLoaded(e); }''')
rep('''  try { @PKG@.Gear.info(@PKG@.GearCrit.startCheck()); }''', '''  try { @PKG@.Gear.info(@PKG@.GearMulti.start()); } catch (Throwable tm) { @PKG@.Gear.warn("multitools: " + tm); }      // 0.2.18
  try { @PKG@.Gear.info(@PKG@.GearCrit.startCheck()); }''')
rep('''+ G1_CLASSES + GM_CLASSES + UB_CLASSES''', '''+ G1_CLASSES + GM_CLASSES + UB_CLASSES + TOOL_MULTI_CLASSES''')

# ================================================================================================================ 9. GearTool: family 6
rep('''# 1 pickaxe, 2 shovel, 3 hatchet, 4 hoe, 5 sickle; 0 = not a gathering tool (Skyy* items and Bark Scrapers never)
M(gtool, r"""
public static int fam(String id) {
  if (id == null || !@PKG@.GearData.isTool(id)) return 0;''', '''# 1 pickaxe, 2 shovel, 3 hatchet, 4 hoe, 5 sickle, 6 multitool (0.2.18); 0 = not a gathering tool (Skyy* items and Bark Scrapers never)
M(gtool, r"""
public static int fam(String id) {
  if (id == null || !@PKG@.GearData.isTool(id)) return 0;
  if (@PKG@.GearData.isMulti(id)) return 6;''')
rep('''  if (f == 1 || f == 2) return 0;''', '''  if (f == 1 || f == 2 || f == 6) return 0;          // 0.2.18: a multitool's first row is Mining (it posts Foraging too)''')
rep('''  int h = @PKG@.GearGate.have(u, skill(f));''', '''  int h = f == 6 ? @PKG@.GearGate.haveBoth(u) : @PKG@.GearGate.have(u, skill(f));          // 0.2.18: Mining AND Foraging''')
rep(r'''# double[] { fam, row, eff level, active 1/0, power factor, Fortune, need, tier, Wisdom % (0.2.17) } for a stack; null = not a gathering tool''',
    r'''# 0.2.18: one decimal (the Fortune numbers)
M(gtool, "public static double r1(double x) { return (double) Math.round(x * 10.0) / 10.0; }")
# 0.2.18 a MULTITOOL: double[] { 6, 0, eff level, active, Mining power, Mining Fortune, need, tier, Mining Wisdom, Chopping power, Foraging
# Fortune, Foraging Wisdom }. Each side = the same-tier pickaxe / hatchet (eff: level, rarity boost, ITS modifiers, caps) x multi.speedPct /
# multi.fortunePct; under level the bonus goes but the speed share stays (never faster than a single tool); part.tools off = plain (1.0)
M(gtool, r"""
public static double[] mstats(java.util.UUID u, String id, @BD@ d) {
  int[] g = gate(u, 6, id, d);
  int t = tier(id);
  boolean on = g[2] != 0 && @PKG@.GearCfg.PART_TOOLS;
  double sp = @PKG@.GearCfg.PART_TOOLS ? (double) @PKG@.GearCfg.MULTI_SPD / 100.0 : 1.0;
  double fp = (double) @PKG@.GearCfg.MULTI_FORT / 100.0;
  double pm = sp;
  double pc = sp;
  double fm = 0.0;
  double fc = 0.0;
  double wm = 0.0;
  double wc = 0.0;
  if (on) {
    double[] a = eff(1, g[1], t, d);
    double[] b = eff(3, g[1], t, d);
    pm = a[0] * sp;
    pc = b[0] * sp;
    fm = r1(a[1] * fp);
    fc = r1(b[1] * fp);
    wm = a[2];
    wc = b[2];
  }
  return new double[] { 6.0, 0.0, (double) g[1], on ? 1.0 : 0.0, pm, fm, (double) g[0], (double) t, wm, pc, fc, wc };
}""")
# double[] { fam, row, eff level, active 1/0, power factor, Fortune, need, tier, Wisdom % (0.2.17) } for a stack; null = not a gathering tool''')
rep('''  try { d = @PKG@.GearData.gearDoc(s.getMetadata()); } catch (Throwable t0) { d = null; }''',
    '''  try { d = @PKG@.GearData.gearDoc(s.getMetadata()); } catch (Throwable t0) { d = null; }
  if (f == 6) return mstats(u, id, d);          // 0.2.18: both stat sets''')
rep(r'''# the held stack (GearHandSys every tick, GearToolHitSys every block hit)''',
    r'''# 0.2.18: a multitool posts BOTH rows in the "gear" source: dd.mining (its Mining Fortune + the worn mining armor's, with the pickaxe's rock /
# ore filter) + xp.mining, dd.foraging + xp.foraging; nothing to post (or profile:busy) = our source removed
M(gtool, r"""
public static void mpost(java.util.UUID u, double[] st) {
  if (u == null || st == null || st.length < 12) return;
  try {
    double[] ma = @PKG@.GearMine.bonus(u);
    boolean on = st[3] != 0.0;
    double fm = (on ? st[5] : 0.0) + (ma == null ? 0.0 : ma[0]);
    double wm = (on ? st[8] : 0.0) + (ma == null ? 0.0 : ma[1]);
    double fc = on ? st[10] : 0.0;
    double wc = on ? st[11] : 0.0;
    java.util.Map b = @PKG@.Gear.bridge();
    String key = "skill:bonus:" + u.toString();
    Object o = b.get(key);
    java.util.HashMap m = new java.util.HashMap();
    if (fm > 0.0) { m.put("dd.mining", Double.valueOf(fm / 100.0)); m.put("only.mining", ONLY[6]); }
    if (wm > 0.0) m.put("xp.mining", Double.valueOf(wm / 100.0));
    if (fc > 0.0) m.put("dd.foraging", Double.valueOf(fc / 100.0));
    if (wc > 0.0) m.put("xp.foraging", Double.valueOf(wc / 100.0));
    if (m.isEmpty() || @PKG@.Gear.busy(u)) {
      if (o instanceof java.util.Map && ((java.util.Map) o).remove(SRC) != null) N[4] = N[4] + 1L;
      return;
    }
    java.util.Map src = null;
    if (o instanceof java.util.Map) src = (java.util.Map) o;
    else {
      java.util.concurrent.ConcurrentHashMap n = new java.util.concurrent.ConcurrentHashMap();
      Object prev = b.putIfAbsent(key, n);
      src = prev instanceof java.util.Map ? (java.util.Map) prev : n;
    }
    if (m.equals(src.get(SRC))) return;
    src.put(SRC, java.util.Collections.unmodifiableMap(m));
    N[3] = N[3] + 1L;
  } catch (Throwable t) { @PKG@.Gear.warnOnce("toolpostm", "multitool Fortune bridge post failed: " + t); }
}""")
# the held stack (GearHandSys every tick, GearToolHitSys every block hit)''')
rep('''  LAST.put(u, new Object[] { s, Long.valueOf(now), st });''', '''  LAST.put(u, new Object[] { s, Long.valueOf(now), st });
  if (st != null && st[0] == 6.0) { mpost(u, st); return st; }          // 0.2.18: a multitool posts both rows''')
rep(r'''# a block hit (DamageBlockEvent, synchronous)''', r'''# 0.2.18 a multitool's block hit: rock / ore = its Mining power (x the worn Mining Sets' Mining Power), logs = its Chopping power; any other
# block vanilla. The factor may be below 1 (the speed share: a bit slower than a single tool), never below x0.05
M(gtool, r"""
public static float mdamage(java.util.UUID u, double[] st, @TBTY@ bt, float dmg) {
  boolean mine = onType(1, bt);
  boolean chop = !mine && onType(3, bt);
  if ((!mine && !chop) || !(dmg > 0.0f)) { N[1] = N[1] + 1L; return dmg; }
  double m = mine ? st[4] : st[9];
  if (mine) {
    double[] ma = @PKG@.GearMine.bonus(u);
    if (ma != null && ma[2] > 0.0) m = m * (1.0 + ma[2] / 100.0);
  }
  if (Double.isNaN(m) || !(m > 0.0)) m = 1.0;
  if (m < 0.05) m = 0.05;
  if (m > 100.0) m = 100.0;
  if (m == 1.0) { N[1] = N[1] + 1L; return dmg; }
  if (st[3] == 0.0) N[2] = N[2] + 1L;
  else N[0] = N[0] + 1L;
  return (float) ((double) dmg * m);
}""")
# a block hit (DamageBlockEvent, synchronous)''')
rep('''    int f = (int) st[0];''', '''    int f = (int) st[0];
    if (f == 6) return mdamage(u, st, bt, dmg);          // 0.2.18''')
rep(r'''# tooltip lines under the gate line''', r'''# 0.2.18: one power line of a multitool ("Mining Power -15%: 3 hits per stone (plain pickaxe 3)"); the sign is shown (below x1 = slower)
M(gtool, r"""
public static void mpowLine(java.util.ArrayList txt, java.util.ArrayList col, String name, double pw, double rp, String blk, String tool, String on) {
  int pc = (int) Math.round((pw - 1.0) * 100.0);
  String pct = name + " " + (pc >= 0 ? "+" : "") + pc + "%";
  int h = hits(rp, pw);
  int v = hits(rp, 1.0);
  if (h > 0 && v > 0) txt.add(pct + ": " + h + (h == 1 ? " hit" : " hits") + " per " + blk + " (plain " + tool + " " + v + ")");
  else txt.add(pct + " on " + on);
  col.add(null);
}""")
# 0.2.18: the multitool's lines (both stat sets, the trade-off line); the tier word = the id's last word
M(gtool, r"""
public static void mlines(java.util.UUID owner, String id, @BD@ d, int t, java.util.ArrayList txt, java.util.ArrayList col) {
  int[] g = gate(owner, 6, id, d);
  int lv = g[0];
  double sp = (double) @PKG@.GearCfg.MULTI_SPD / 100.0;
  double fp = (double) @PKG@.GearCfg.MULTI_FORT / 100.0;
  double[] a = eff(1, lv, t, d);
  double[] b = eff(3, lv, t, d);
  String tw = id.substring(id.lastIndexOf('_') + 1);
  mpowLine(txt, col, "Mining Power", a[0] * sp, refPower("Tool_Pickaxe_" + tw), "stone", "pickaxe", "rock and ore");
  mpowLine(txt, col, "Chopping Power", b[0] * sp, refPower("Tool_Hatchet_" + tw), "log", "hatchet", "logs");
  double fm = r1(a[1] * fp);
  double fc = r1(b[1] * fp);
  txt.add("Mining Fortune +" + @PKG@.Gear.fnum(fm) + " (" + @PKG@.Gear.fnum(fm) + "% extra rock / ore chance)");
  col.add(null);
  txt.add("Foraging Fortune +" + @PKG@.Gear.fnum(fc) + " (" + @PKG@.Gear.fnum(fc) + "% extra log chance)");
  col.add(null);
  if (a[2] > 0.0) { txt.add("Mining Wisdom +" + @PKG@.Gear.fnum(a[2]) + "% (more Mining XP)"); col.add(null); }
  if (b[2] > 0.0) { txt.add("Foraging Wisdom +" + @PKG@.Gear.fnum(b[2]) + "% (more Foraging XP)"); col.add(null); }
  if (owner != null && g[2] == 0) {
    txt.add("No bonus until Mining + Foraging " + lv);
    col.add(@PKG@.GearDefs.C_BAD);
  }
  txt.add("Multitool: slightly slower and less Fortune than a single tool");
  col.add(@PKG@.GearDefs.C_GRAY);
  txt.add("Tree Feller unlocks in the Foraging tree");
  col.add(@PKG@.GearDefs.C_GRAY);
}""")
# tooltip lines under the gate line''')
rep('''  int t = tier(id);
  int[] g = gate(owner, f, id, d);''', '''  int t = tier(id);
  if (f == 6) { mlines(owner, id, d, t, txt, col); return; }          // 0.2.18: a multitool
  int[] g = gate(owner, f, id, d);''')
rep(r'''"%, craft XP " + @PKG@.GearCfg.TOOL_XPC + "%)" : "OFF (part.toolRarity)");''',
    r'''"%, craft XP " + @PKG@.GearCfg.TOOL_XPC + "%)" : "OFF (part.toolRarity)") + "; multitools " + (@PKG@.GearCfg.MULTI_ON ? "on (speed " + @PKG@.GearCfg.MULTI_SPD + "%, Fortune " + @PKG@.GearCfg.MULTI_FORT + "% of a single tool, Mining + Foraging gate)" : "OFF (part.multitool)");''')

# ================================================================================================================ 10. GearMine: a multitool is a pickaxe for the armor
rep('''  return st[0] == 1.0 || st[0] == 2.0;''', '''  return st[0] == 1.0 || st[0] == 2.0 || st[0] == 6.0;          // 0.2.18: + a multitool''')

# ================================================================================================================ 11. manifest
rep(r'''reforge like gear and pay Smithing XP;''',
    r'''reforge like gear and pay Smithing XP; multitools of the Multitools mod (by InkBlindCat, MIT) cost a pickaxe + hatchet (+ shovel) of their tier and count as both tools, a bit slower and with less Fortune (Mining + Foraging gate);''')

open(DST, "w", encoding="utf8", newline="").write(s.replace(LF, NL))
print("wrote", DST)
