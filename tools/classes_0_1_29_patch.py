"""Derive SkyyClasses/build_skyyclasses_0.1.29.py from the GENERATED SkyyClasses 0.1.28 (build_skyyclasses_0.1.28.py = the
tools/deploy_set.py SET pin; the EDITED lineage: Skyy's hand-edited 0.1.6 (commit ab75b6c) -> classes_0_1_7_patch.py -> ... ->
classes_0_1_28_patch.py -> 0.1.28). Never re-run an older patch, never edit a generated script - edit this patch. Every anchor is asserted;
at the end every change is undone on a copy and compared with 0.1.28 (nothing else changed). Line endings kept.
Run:  python tools/classes_0_1_29_patch.py   then   python SkyyClasses/build_skyyclasses_0.1.29.py   (never --deploy)
      then  python SkyyClasses/test_skyyclasses_0.1.29.py

0.1.29 (2026-10-15) = THE ASSASSIN KIT GETS A CRUDE KUNAI. Skyy 2026-10-15: "kunai doesnt seem to do damage when thrown (my friend is playing
  assassin and its not workinf got him)" - the log: 'Level too low | Kunai needs Assassination 22 - you are 3' (the vanilla Weapon_Kunai,
  SkyyGear's Kunai row 20-27); the Assassin kit gave only Weapon_Daggers_Crude:1. Popup "Kunai are a main Assassin weapon, but the starter
  kit only gives Crude Daggers. Should Assassins also start with Crude Kunai (level 1, works right away)?" -> "Yes, add Crude Kunai
  (Recommended)".
    (1) kit.Assassin default = Weapon_Daggers_Crude:1,Weapon_Kunai_Crude:1. Weapon_Kunai_Crude = SkyyArmory 0.1.6+ (the SET pin 0.1.27):
      ONE reusable kunai - the throw spawns a projectile only, nothing leaves the inventory (tap = throw, hold 0.6 s = throw + teleport,
      hold right click 0.4 s = the return ring), so ONE is the whole weapon. It is a MAIN-HAND item (Primary = the throw, no Utility block,
      stack 1), so it goes the normal kit way: the hotbar, next to the daggers (not the utility slot - that takes Utility.Usable items only,
      and the off-hand step is for Weapon_Shield_ only). SkyyGear 0.2.8+ bands it as Crude = level 1-13 (an unstamped item reads its band
      start: Lv 1, level.gateFloor makes skill 0 count as 1) - usable at Assassination 1. The build reads the item from the SET-pinned
      SkyyArmory jar (Assets.zip has no such id): reusable main-hand throw, an Assassin weapon (the "Weapon_Kunai" rule). Without SkyyArmory
      on a server the kit skips the unknown id (KitCfg.knownOnly, as before).
    (2) ONE-TIME CONFIG UPDATE ClassCfg.migrate0129 (the migrate0110 machinery: mgUpdate is now mgUpdateT with its table as arguments,
      byte-for-byte the same result for 0.1.10's table): a kit.Assassin line still holding EXACTLY the 0.1.28 default
      Weapon_Daggers_Crude:1 gets the new default (value text only - key, separator, CR / LF kept); any other value is kept + one INFO
      line; a missing line stays missing (the loader's default is the new kit). The old file first becomes a config-history version
      (verified by mgSaved before the rewrite), one config-changes.log line (Server Setup -> Changes -> Undo), runs once (marker comment
      "SkyyClasses 0.1.29 defaults", also in a fresh default file right above kit.Assassin). setup(): migrate0110 -> migrate0129 -> load.
    (3) EXISTING ASSASSIN PROFILES get the Crude Kunai ONCE (Kit.topTick in the 2 s ClassTick -> Kit.topConsider): the ACTIVE profile of
      an online player, not loading (profile:busy absent), class Assassin, the live kit.Assassin lists Weapon_Kunai_Crude (q of it), the
      item is known (SkyyArmory loaded), kits on. ClassStore.topupKey (one synchronized write): the profile file's kit record is the
      Assassin's (kitClass), given (no in-flight record) or owed, and has no marker kitTopup0129 -> marker + kit=owed + kitOwed/kitItems
      += Weapon_Kunai_Crude:q in ONE save; a record that already lists the kunai gets the marker only. Delivery = the existing owed-claim
      path (Kit.owedLater -> KitTask mode 2 -> Kit.claim quiet: the hotbar only, crash-safe kitClaimBegin before anything moves). Hotbar
      full -> one chat line per session ("make room - it comes at your next login or world change - or /class kit now: hotbar, then
      storage"), retried at every world arrival / login. The SkyySacks Void cannot take it: the Void stores only its six material
      categories and SkyySacks publishes no add-an-item bridge (sacks:fn:put only refunds a take, sacks:fn:deposit only moves a hotbar
      stack). Never a second copy: the marker is written before anything moves, and a re-login / profile switch / restart reads it.
      A profile whose class is not known yet (file not readable yet, class not published at the first tick, no class picked) is looked at
      again at the next tick (review fix); only a real other class ends the looking for the session.
      Other classes, kits never handed out (pending = the new kit itself, old / off = no kit), a hand-edited kit.Assassin without the
      kunai, a server without SkyyArmory: nothing (the marker is not written, so it is looked at again next session).
    (4) Kit.claim takes the owed list from kitClaimBegin's own read (the list it really moved to the in-flight record) - a top-up that
      joined kitOwed between the claim's first read and kitClaimBegin can never be dropped by kitEnd. A claim that hands out the Crude
      Kunai adds one tip line (tap to throw, hold to throw and teleport).
    No command, permission, bridge key or page changes. ROLLBACK to 0.1.28: safe - the config line keeps the kunai (0.1.28 hands out what
    the file says), the profile markers are ignored, an owed kunai is still collected by 0.1.28's claim.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.28.py")
dst = os.path.join(ROOT, "SkyyClasses", "build_skyyclasses_0.1.29.py")
raw = open(src, encoding="utf8", newline="").read()
CR, LF = chr(13), chr(10)
NL = CR + LF if (CR + LF) in raw else LF
s = raw.replace(CR + LF, LF)
OLD = s
assert 'VERSION = "0.1.28"' in s and s.startswith('"""SkyyClasses 0.1.28 - build script') and "migrate0129" not in s, "not the generated 0.1.28 script"
REG0 = s.count("registerCommand(")
CHANGES = []


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:160])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


HEAD = open(__file__, encoding="utf8").read().split('"""')[1]
NOTE = HEAD[HEAD.index("0.1.29 (2026-10-15)"):].rstrip() + "\n"

# ================================================================================================ docstring + version
rep('''"""SkyyClasses 0.1.28 - build script (javassist via jpype). GENERATED by tools/classes_0_1_28_patch.py from the generated 0.1.27 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_27_patch.py -> 0.1.27) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''', '''"""SkyyClasses 0.1.29 - build script (javassist via jpype). GENERATED by tools/classes_0_1_29_patch.py from the generated 0.1.28 (the
EDITED lineage: Skyy's edited 0.1.6 -> classes_0_1_7_patch.py -> 0.1.7 -> ... -> classes_0_1_28_patch.py -> 0.1.28) - edit the patch, not
this file; classes_0_1_6_patch.py is never re-run. Wynncraft-style classes for SkyWynn.
''' + NOTE)
rep('VERSION = "0.1.28"', 'VERSION = "0.1.29"')

# ================================================================================================ (1) the Assassin kit default
rep('''     "weapon_text": "Daggers / Kunai", "kit": "Weapon_Daggers_Crude:1"},''',
    '''     # 0.1.29 (Skyy 2026-10-15 popup "Yes, add Crude Kunai"): + ONE Crude Kunai (SkyyArmory; reusable - the throw uses no item)
     "weapon_text": "Daggers / Kunai", "kit": "Weapon_Daggers_Crude:1,Weapon_Kunai_Crude:1"},''')

# ================================================================================================ (2) the update table + the top-up constants
rep('''assert "=" not in MG_MARK and MG_MARK.startswith("# ") and MG_MARK_ID in MG_MARK, "the marker must be a doc comment"
''', '''assert "=" not in MG_MARK and MG_MARK.startswith("# ") and MG_MARK_ID in MG_MARK, "the marker must be a doc comment"
# 0.1.29 (Skyy 2026-10-15, popup "Should Assassins also start with Crude Kunai (level 1, works right away)?" -> "Yes, add Crude Kunai
# (Recommended)"): the second one-time update (ClassCfg.migrate0129, the migrate0110 machinery through mgUpdateT). Only a kit.Assassin line
# still holding EXACTLY the 0.1.28 default changes; a hand-edited value is kept (+ an INFO line).
MG29_DEFAULTS = [("kit.Assassin", "Weapon_Daggers_Crude:1", "Weapon_Daggers_Crude:1,Weapon_Kunai_Crude:1", "Assassins also start with a Crude Kunai")]
MG29_MARK_ID = "SkyyClasses 0.1.29 defaults"
MG29_MARK = ("# %s (Skyy 2026-10-15): the Assassin kit also has a Crude Kunai (kit.Assassin Weapon_Daggers_Crude:1,Weapon_Kunai_Crude:1)"
             % MG29_MARK_ID)
MG29_WHO = "SkyyClasses 0.1.29"
assert all(32 <= ord(_c) < 127 for _c in MG29_MARK + "".join("".join(_t) for _t in MG29_DEFAULTS)), "the update texts must be plain ASCII"
assert "=" not in MG29_MARK and MG29_MARK.startswith("# ") and MG29_MARK_ID in MG29_MARK, "the marker must be a doc comment"
assert MG_MARK_ID not in MG29_MARK and MG29_MARK_ID not in MG_MARK, "the two update markers must not find each other"
# 0.1.29: the per-profile top-up (Kit.topConsider): an Assassin profile whose kit was handed out before the kunai joined it gets it ONCE
# (marker TOP_MARK in its class file, written in the same save that makes the kunai owed)
TOP_CLASS, TOP_ITEM, TOP_MARK = "Assassin", "Weapon_Kunai_Crude", "kitTopup0129"
TOP_TIP = "Assassin kits now include a Crude Kunai: tap to throw it, hold to throw it and teleport where it lands."
TOP_WAIT = ("Your Crude Kunai is waiting, but your hotbar is full. Make room - it comes at your next login or world change - "
            "or type /class kit now (hotbar, then storage).")
''')

# ================================================================================================ (1) the build check: kit items from SkyyArmory too
rep('''print("class kits (defaults):")
for _ci, _c in enumerate(CLASSES):
    for _iid, _q in kit_entries(_c["kit"]):
        assert _iid in _ITEMS, "kit item %s of %s is not in Assets.zip" % (_iid, _c["name"])
''', '''# 0.1.29: a default kit item may also be one of these SkyyArmory items (no vanilla id - checked), read from the SET-pinned SkyyArmory jar
# (read only): a reusable main-hand throw (the 0.1.6 kunai: Primary = its throw root, no Utility block, stack 1) and an Assassin weapon
ARMORY_KIT_IDS = ["Weapon_Kunai_Crude"]
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
import deploy_set as _DS29
_ARMV29 = dict(_DS29.SET).get("SkyyArmory")
_ARMJ29 = os.path.join(os.path.dirname(HERE), "SkyyArmory", "SkyyArmory-%s.jar" % _ARMV29)
assert not [i for i in ARMORY_KIT_IDS if i in _ITEMS], "Hytale now has a SkyyArmory kit id - SkyyArmory would override it"
if os.path.isfile(_ARMJ29):
    _ak29 = {}
    with zipfile.ZipFile(_ARMJ29) as _az29:
        for _n in _az29.namelist():
            if _n.startswith("Server/Item/Items/") and _n.endswith(".json") and os.path.basename(_n)[:-5] in ARMORY_KIT_IDS:
                _ak29[os.path.basename(_n)[:-5]] = json.loads(_az29.read(_n).decode("utf-8-sig"))
    assert sorted(_ak29) == sorted(ARMORY_KIT_IDS), "SkyyArmory %s lacks a kit item: %s" % (_ARMV29, sorted(set(ARMORY_KIT_IDS) - set(_ak29)))
    _kc29 = _ak29["Weapon_Kunai_Crude"]
    assert "Utility" not in _kc29 and "MaxStack" not in _kc29 and _kc29.get("Interactions", {}).get("Primary") == "SkyyArmory_Kunai_Primary_Crude" \\
        and _kc29.get("Tags", {}).get("Family") == ["Kunai"], "0.1.29: the Crude Kunai must be SkyyArmory's reusable main-hand throw: %s" % _kc29.get("Interactions")
    print("0.1.29: SkyyArmory %s jar: %s - a reusable main-hand throw (hotbar, not the utility slot)" % (_ARMV29, ", ".join(ARMORY_KIT_IDS)))
else:
    print("0.1.29: NOTE - SkyyArmory/SkyyArmory-%s.jar not built here; %s checked from the table only" % (_ARMV29, ", ".join(ARMORY_KIT_IDS)))
print("class kits (defaults):")
for _ci, _c in enumerate(CLASSES):
    for _iid, _q in kit_entries(_c["kit"]):
        assert _iid in _ITEMS or _iid in ARMORY_KIT_IDS, "kit item %s of %s is not in Assets.zip (nor a SkyyArmory kit id)" % (_iid, _c["name"])
''')
rep('''assert MG_DEFAULTS[1][1] == "50" and MG_DEFAULTS[1][2] == str(DEF_HEAL_SELF_PCT), "the self-heal update table"
''', '''assert MG_DEFAULTS[1][1] == "50" and MG_DEFAULTS[1][2] == str(DEF_HEAL_SELF_PCT), "the self-heal update table"
# 0.1.29: the Assassin kit = the update's new default = the old default + ONE Crude Kunai; the kunai is the top-up item, an Assassin weapon,
# not an off-hand id (it goes into the hotbar)
_ASN29 = [c for c in CLASSES if c["name"] == TOP_CLASS][0]
assert _ASN29["kit"] == MG29_DEFAULTS[0][2] == MG29_DEFAULTS[0][1] + "," + TOP_ITEM + ":1" and MG29_DEFAULTS[0][0] == "kit." + TOP_CLASS, \\
    "the Assassin kit default and the 0.1.29 update table disagree"
assert dict(kit_entries(_ASN29["kit"])).get(TOP_ITEM) == 1 and not TOP_ITEM.startswith(OFFHAND_PREFIX) and _ASN29["enabled"]
assert classify(TOP_ITEM)[0] == [i for i, c in enumerate(CLASSES) if c["name"] == TOP_CLASS][0], "the Crude Kunai must be an Assassin weapon"
''')

# ================================================================================================ (2) the fresh default file carries the 0.1.29 marker
rep('''] + [_l for _c in CLASSES for _l in (([MG_MARK] if _c["name"] == "Warrior" else []) + ["kit.%s=%s" % (_c["name"], _c["kit"])])] + [''',
    '''] + [_l for _c in CLASSES for _l in (([MG_MARK] if _c["name"] == "Warrior" else []) + ([MG29_MARK] if _c["name"] == TOP_CLASS else [])   # 0.1.29
                                        + ["kit.%s=%s" % (_c["name"], _c["kit"])])] + [''')

# the config kit checks every row default against the known item ids (Assets.zip): + the SkyyArmory kit ids (build-time check only)
rep('''               HOLDERS=2)   # 0.1.25: the row arrays live in CfgRows1 + CfgRows2''',
    '''               ITEMS=set(_ITEMS) | set(ARMORY_KIT_IDS),   # 0.1.29: Assets.zip + the SkyyArmory kit ids (the Crude Kunai)
               HOLDERS=2)   # 0.1.25: the row arrays live in CfgRows1 + CfgRows2''')

# ================================================================================================ (2) ClassCfg: mgUpdateT (the table as arguments) + migrate0129
rep('''F(cfg, "public static final String MG_WHO = %s;" % jstr(MG_WHO))
''', '''F(cfg, "public static final String MG_WHO = %s;" % jstr(MG_WHO))
# 0.1.29: the second update's table (migrate0129)
F(cfg, "public static final String[] MG29_KEY = %s;" % jarr([t[0] for t in MG29_DEFAULTS]))
F(cfg, "public static final String[] MG29_OLD = %s;" % jarr([t[1] for t in MG29_DEFAULTS]))
F(cfg, "public static final String[] MG29_NEW = %s;" % jarr([t[2] for t in MG29_DEFAULTS]))
F(cfg, "public static final String[] MG29_WHY = %s;" % jarr([t[3] for t in MG29_DEFAULTS]))
F(cfg, "public static final String MG29_MARK = %s;" % jstr(MG29_MARK))
F(cfg, "public static final String MG29_MARK_ID = %s;" % jstr(MG29_MARK_ID))
F(cfg, "public static final String MG29_WHO = %s;" % jstr(MG29_WHO))
''')
_a = s.index('M(cfg, r"""\npublic static Object[] mgUpdate(String text) {')
_b = s.index('}""")\n', _a) + len('}""")\n')
OLD_MGU = s[_a:_b]
GEN = OLD_MGU
for _o, _n, _c in (('public static Object[] mgUpdate(String text) {',
                    'public static Object[] mgUpdateT(String text, String[] K, String[] O, String[] N, String[] W, String mark, String markId, String ver) {', 1),
                   ("MG_MARK_ID", "markId", 1), ("MG_MARK", "mark", 2), ("MG_KEY", "K", 4), ("MG_OLD", "O", 4), ("MG_NEW", "N", 5), ("MG_WHY", "W", 1),
                   ("mgIdx(", "mgIdxT(K, ", 2), ('" kept (custom) - the 0.1.10 default is "', '" kept (custom) - the " + ver + " default is "', 1)):
    assert GEN.count(_o) == _c, "mgUpdate: %r found %d times, expected %d" % (_o, GEN.count(_o), _c)
    GEN = GEN.replace(_o, _n)
assert "MG_" not in GEN and "0.1.10" not in GEN
rep(OLD_MGU, '''# 0.1.29: mgIdx over a given key table
M(cfg, r"""
public static int mgIdxT(String[] K, String k) {
  if (k == null) return -1;
  for (int i = 0; i < K.length; i++) if (K[i].equals(k)) return i;
  return -1;
}""")
# 0.1.29: 0.1.10's mgUpdate with its table as arguments (keys, old texts, new texts, reasons, the marker line, the marker id, the version
# named in the kept notes) - every step exactly 0.1.10's
''' + GEN + '''# 0.1.10's own update = mgUpdateT with 0.1.10's table (the same result, byte for byte)
M(cfg, r"""
public static Object[] mgUpdate(String text) {
  return mgUpdateT(text, MG_KEY, MG_OLD, MG_NEW, MG_WHY, MG_MARK, MG_MARK_ID, "0.1.10");
}""")
''')
rep('''public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\\t" + MG_WHO + "\\t-\\tupdate\\t" + @PKG@.CfgRows.oneLine(k) + "\\t" + o + "\\t" + n + "\\tok";
}""")
''', '''public static String mgLog(String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\\t" + MG_WHO + "\\t-\\tupdate\\t" + @PKG@.CfgRows.oneLine(k) + "\\t" + o + "\\t" + n + "\\tok";
}""")
# 0.1.29: the same line under another update's name
M(cfg, r"""
public static String mgLogT(String who, String k, String o, String n) {
  return @PKG@.CfgLog.now() + "\\t" + who + "\\t-\\tupdate\\t" + @PKG@.CfgRows.oneLine(k) + "\\t" + o + "\\t" + n + "\\tok";
}""")
''')
rep('''    warn("could not update config.properties to the 0.1.10 defaults (the file is used as it is): " + t);
    return "";
  }
}""")
''', '''    warn("could not update config.properties to the 0.1.10 defaults (the file is used as it is): " + t);
    return "";
  }
}""")
# 0.1.29 (Skyy 2026-10-15): the Assassin kit gains a Crude Kunai - migrate0110's steps with the 0.1.29 table, right after migrate0110 and
# before ClassCfg.load. "" = nothing done (no file - load() writes the 0.1.29 default with both markers -, marker already there, a failure)
M(cfg, r"""
public static synchronized String migrate0129() {
  java.nio.file.Path f = FILE;
  if (f == null) return "";
  try {
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) return "";
    byte[] old = java.nio.file.Files.readAllBytes(f);
    Object[] r = mgUpdateT(new String(old, "ISO-8859-1"), MG29_KEY, MG29_OLD, MG29_NEW, MG29_WHY, MG29_MARK, MG29_MARK_ID, "0.1.29");
    if (r == null) return "";
    byte[] data = ((String) r[0]).getBytes("ISO-8859-1");
    mgKit(f.toAbsolutePath().getParent());
    @PKG@.CfgHist.snapshot(0, old, @PKG@.CfgHist.stamp(), MG29_WHO, "before the 0.1.29 defaults update");
    if (!mgSaved(old)) {
      warn("config.properties NOT updated to the 0.1.29 defaults: the old file could not be kept in " + @PKG@.CfgHist.DIR + " (the file is used as it is; the next start tries again)");
      return "";
    }
    @PKG@.CfgRows.atomicWrite(f, data);
    String[] rows = (String[]) r[3];
    for (int i = 0; i + 2 < rows.length; i += 3) @PKG@.CfgLog.enqueue(mgLogT(MG29_WHO, rows[i], rows[i + 1], rows[i + 2]));
    if (rows.length > 0) @PKG@.CfgLog.flush();
    String chg = (String) r[1];
    String[] kept = (String[]) r[2];
    String msg = null;
    if (chg.length() > 0) msg = "config.properties updated to the 0.1.29 defaults: " + chg + " (the old file is in config-history; Server Setup -> Changes can undo it)";
    else msg = "config.properties: the kit.Assassin line no longer had its 0.1.28 default - nothing changed (0.1.29 defaults marker added)";
    info(msg);
    StringBuilder all = new StringBuilder(msg);
    for (int i = 0; i < kept.length; i++) { info(kept[i]); all.append('\\n').append(kept[i]); }
    return all.toString();
  } catch (Throwable t) {
    warn("could not update config.properties to the 0.1.29 defaults (the file is used as it is): " + t);
    return "";
  }
}""")
''')

# ================================================================================================ (3) KitCfg.amountOf
rep('''public static int total(int[] qs) {
  int n = 0;
  for (int i = 0; i < qs.length; i++) if (qs[i] > 0) n = n + qs[i];
  return n;
}""")
''', '''public static int total(int[] qs) {
  int n = 0;
  for (int i = 0; i < qs.length; i++) if (qs[i] > 0) n = n + qs[i];
  return n;
}""")
# 0.1.29: how many of item id an "id:amount,..." list holds (0 = not listed)
M(kcfg, r"""
public static int amountOf(String text, String id) {
  if (id == null) return 0;
  Object[] k = parse(text, null, 1000);
  String[] ids = (String[]) k[0];
  int[] qs = (int[]) k[1];
  int n = 0;
  for (int i = 0; i < ids.length && i < qs.length; i++) if (id.equals(ids[i])) n = n + qs[i];
  return n;
}""")
''')

# ================================================================================================ (3) ClassStore.topupKey (one synchronized save)
rep('''# a claim starts: owed -> given (kitOwed stays as the in-flight record until kitEnd); returns the owed list, null = nothing owed / not saved''',
    '''# 0.1.29: the one-time top-up of profile k (Kit.topConsider): -1 = the file could not be read / written (retried), 0 = not this record
# (another class's kit, no kit handed out - pending / old / off / none -, or a give / claim in flight), 1 = the record already lists the item
# (marker only), 2 = marker + the item owed (kit=owed, kitOwed and kitItems += item:q) in ONE save, 3 = the marker was already there
M(st_, r"""
public static synchronized int topupKey(String k, String cls, String item, int q, String mark) {
  java.util.Properties old = loadKey(k);
  if (DATA.get(k) != old) return -1;
  if (old.getProperty(mark) != null) return 3;
  String ks = old.getProperty("kit");
  boolean given = "given".equals(ks);
  if (cls == null || !cls.equals(old.getProperty("kitClass")) || (!given && !"owed".equals(ks))) return 0;
  String ow = old.getProperty("kitOwed", "");
  if (given && ow.length() > 0) return 0;
  String items = old.getProperty("kitItems", "");
  boolean had = @PKG@.KitCfg.amountOf(items, item) > 0 || @PKG@.KitCfg.amountOf(ow, item) > 0;
  String e = item + ":" + q;
  java.util.Properties p = new java.util.Properties();
  p.putAll(old);
  long now = System.currentTimeMillis();
  if (had) {
    p.setProperty(mark, now + " had");
  } else {
    p.setProperty(mark, now + " owed " + e);
    p.setProperty("kit", "owed");
    p.setProperty("kitOwed", ow.length() == 0 ? e : ow + "," + e);
    p.setProperty("kitItems", items.length() == 0 ? e : items + "," + e);
  }
  DATA.put(k, p);
  if (!saveKey(k)) { DATA.put(k, old); return -1; }
  if (!had) KITQ.put(k, "owed");
  return had ? 1 : 2;
}""")
# a claim starts: owed -> given (kitOwed stays as the in-flight record until kitEnd); returns the owed list, null = nothing owed / not saved''')

# ================================================================================================ (3) Kit: constants, the waiting line, the claim, the top-up
rep('''F(kit_, "public static final String OFFHAND = %s;" % jstr(OFFHAND_PREFIX))   # 0.1.10: kit ids that go into an empty off-hand
''', '''F(kit_, "public static final String OFFHAND = %s;" % jstr(OFFHAND_PREFIX))   # 0.1.10: kit ids that go into an empty off-hand
# 0.1.29: the one-time top-up (class, item, the profile-file marker, the two chat lines) + pkey -> TRUE: looked at this session / the
# hotbar-full line told this session (both dropped at quit, so a re-login looks again - the marker in the file decides)
F(kit_, "public static final String TOP_CLASS = %s;" % jstr(TOP_CLASS))
F(kit_, "public static final String TOP_ITEM = %s;" % jstr(TOP_ITEM))
F(kit_, "public static final String TOP_MARK = %s;" % jstr(TOP_MARK))
F(kit_, "public static final String TOP_TIP = %s;" % jstr(TOP_TIP))
F(kit_, "public static final String TOP_WAIT = %s;" % jstr(TOP_WAIT))
F(kit_, "public static final java.util.concurrent.ConcurrentHashMap TOPDONE = new java.util.concurrent.ConcurrentHashMap();")
F(kit_, "public static final java.util.concurrent.ConcurrentHashMap TOPTOLD = new java.util.concurrent.ConcurrentHashMap();")
''')
rep('''# collect owed kit items of the ACTIVE profile k (world thread). quiet = the retry at a world arrival (only a success is told)
M(kit_, r"""''', '''# 0.1.29: an automatic (arrival) claim found no room and the owed list holds the Crude Kunai: one chat line per session and profile
M(kit_, r"""
public static void topWait(@PR@ pr, String k, String[] ids) {
  boolean has = false;
  for (int i = 0; i < ids.length; i++) if (TOP_ITEM.equals(ids[i])) has = true;
  if (!has || k == null || TOPTOLD.putIfAbsent(k, Boolean.TRUE) != null) return;
  tell(pr, TOP_WAIT, true);
}""")
# collect owed kit items of the ACTIVE profile k (world thread). quiet = the retry at a world arrival (only a success is told)
M(kit_, r"""''')
rep('''    if (!quiet) tell(pr, "Your hotbar and storage are full - make room for your kit items (" + @PKG@.KitCfg.listText(ids, qs) + "), then type /class kit again.", true);
    return;
  }
  String owed = @PKG@.ClassStore.kitClaimBegin(k);
  if (owed == null) { if (!quiet) tell(pr, "Your kit record could not be saved - try again in a moment.", true); return; }
  int[] got = put(p, where, ids, qs);''', '''    if (!quiet) tell(pr, "Your hotbar and storage are full - make room for your kit items (" + @PKG@.KitCfg.listText(ids, qs) + "), then type /class kit again.", true);
    else topWait(pr, k, ids);   // 0.1.29: the Crude Kunai top-up says why it has not arrived (once per session)
    return;
  }
  String owed = @PKG@.ClassStore.kitClaimBegin(k);
  if (owed == null) { if (!quiet) tell(pr, "Your kit record could not be saved - try again in a moment.", true); return; }
  // 0.1.29: the list kitClaimBegin really moved to the in-flight record (a top-up may have joined kitOwed since the read above)
  Object[] ow2 = @PKG@.KitCfg.parse(owed, "kitOwed of " + k, 1000);
  ids = (String[]) ow2[0];
  qs = (int[]) ow2[1];
  int[] got = put(p, where, ids, qs);''')
rep('''  if (g > 0) tell(pr, "Collected " + g + (g == 1 ? " kit item: " : " kit items: ") + @PKG@.KitCfg.listText(ids, got) + ".", false);
''', '''  if (g > 0) tell(pr, "Collected " + g + (g == 1 ? " kit item: " : " kit items: ") + @PKG@.KitCfg.listText(ids, got) + ".", false);
  if (@PKG@.KitCfg.amountOf(@PKG@.KitCfg.join(ids, got), TOP_ITEM) > 0) tell(pr, TOP_TIP, false);   // 0.1.29
''')
rep('''M(kit_, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  String us = u.toString();
  java.util.Iterator it = INFLIGHT.keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); if (k != null && k.startsWith(us)) it.remove(); }
}""")''', '''# 0.1.29: the one-time Crude Kunai top-up of the ACTIVE profile (scheduler thread, from topTick; the file write is ClassStore.topupKey,
# the delivery the owed claim at the next world-thread task). Nothing happens for another class, a kit without the kunai (a hand edit),
# an unknown kunai (no SkyyArmory) or a loading profile - and only a written marker (topupKey 1 / 2 / 3) ends the looking for this pkey.
M(kit_, r"""
public static int topConsider(@PR@ pr) {
  java.util.UUID u = pr.getUuid();
  if (u == null) return -1;
  String k = @PKG@.ClassCfg.pkey(u);
  if (k == null || TOPDONE.containsKey(k)) return -1;
  if (busy(u)) return -1;
  int ci = @PKG@.ClassStore.classIndex(u);
  if (ci < 0) return -1;   // no class known yet (file not readable yet / class not published / no class picked): looked at again next tick
  if (!TOP_CLASS.equals(@PKG@.ClassDefs.NAMES[ci])) { TOPDONE.put(k, Boolean.TRUE); return 0; }
  int q = @PKG@.KitCfg.amountOf(@PKG@.KitCfg.textOf(ci), TOP_ITEM);
  if (q <= 0 || !@PKG@.KitCfg.known(TOP_ITEM)) { TOPDONE.put(k, Boolean.TRUE); return 0; }
  int r = @PKG@.ClassStore.topupKey(k, TOP_CLASS, TOP_ITEM, q, TOP_MARK);
  if (r < 0) return -1;
  TOPDONE.put(k, Boolean.TRUE);
  if (r != 2) return r;
  @PKG@.ClassCfg.info("class kit top-up (0.1.29): " + pr.getUsername() + " (" + k + ") is owed " + TOP_ITEM + ":" + q + " - the Assassin kit gained a Crude Kunai after this profile got its kit (once per profile)");
  owedLater(pr);
  return r;
}""")
# 0.1.29: every online player, from the 2 s ClassTick (only while kits are on; TOPDONE makes a looked-at profile cost one map lookup)
M(kit_, r"""
public static void topTick() {
  if (!@PKG@.KitCfg.ON) return;
  java.util.Iterator it = @UNI@.get().getPlayers().iterator();
  while (it.hasNext()) {
    @PR@ pr = (@PR@) it.next();
    if (pr == null || !pr.isValid()) continue;
    try { topConsider(pr); } catch (Throwable t) { @PKG@.ClassCfg.warnLimited("class kit top-up check failed: " + t); }
  }
}""")
# 0.1.29: drop the pkeys of one player from a pkey map
M(kit_, r"""
public static void dropKeys(java.util.Map m, String us) {
  java.util.Iterator it = m.keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); if (k != null && k.startsWith(us)) it.remove(); }
}""")
M(kit_, r"""
public static void forget(java.util.UUID u) {
  if (u == null) return;
  String us = u.toString();
  java.util.Iterator it = INFLIGHT.keySet().iterator();
  while (it.hasNext()) { String k = (String) it.next(); if (k != null && k.startsWith(us)) it.remove(); }
  dropKeys(TOPDONE, us);   // 0.1.29: a re-login looks at the top-up again (the file's marker decides)
  dropKeys(TOPTOLD, us);
}""")''')

# ================================================================================================ (3) ClassTick + setup
rep('''  try { @PKG@.Kit.tick(); } catch (Throwable t0) { if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("class kit tick failed: " + t0); } }
''', '''  try { @PKG@.Kit.tick(); } catch (Throwable t0) { if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("class kit tick failed: " + t0); } }
  try { @PKG@.Kit.topTick(); } catch (Throwable t4) { if (FAILS < 5) { FAILS++; @PKG@.ClassCfg.warn("class kit top-up tick failed: " + t4); } }   // 0.1.29
''')
rep('''  @PKG@.ClassCfg.migrate0110();   // 0.1.10: an untouched kit.Warrior / priestHeal.selfPercent line -> the new default (once; History first)
''', '''  @PKG@.ClassCfg.migrate0110();   // 0.1.10: an untouched kit.Warrior / priestHeal.selfPercent line -> the new default (once; History first)
  @PKG@.ClassCfg.migrate0129();   // 0.1.29: an untouched kit.Assassin line -> + the Crude Kunai (once; History first)
''')

# ================================================================================================ checks on the result
assert s.count("registerCommand(") == REG0, "command registrations changed"
_i = s.index
assert _i("public static int mgIdxT(") < _i("public static Object[] mgUpdateT(") < _i("public static Object[] mgUpdate(String text)") \
    < _i("public static String mgLogT(") < _i("public static synchronized String migrate0110()") < _i("public static synchronized String migrate0129()")
assert _i("public static int amountOf(") < _i("public static synchronized int topupKey(") < _i("public static void topWait(") \
    < _i("public static void claim(") < _i("public static void owedLater(") < _i("public static int topConsider(") < _i("public static void topTick(") \
    < _i("public static void dropKeys(") < _i("public static void forget(java.util.UUID u) {\n  if (u == null) return;\n  String us")
assert _i("@PKG@.ClassCfg.migrate0110();") < _i("@PKG@.ClassCfg.migrate0129();") < _i("String cfgText = @PKG@.ClassCfg.load();")
assert s.count("@PKG@.Kit.topTick()") == 1 and s.count("topWait(pr, k, ids)") == 1 and s.count("ClassStore.topupKey(") == 1
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.1.28 outside the recorded changes"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", dst, "(%d lines; 0.1.28 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
