"""Derive SkyyMenu/build_skyymenu_0.3.14.py from the LIVE SkyyMenu 0.3.13 (python tools/menu_0_3_14_patch.py, then build the result).
Edit THIS patch, never the generated build script. The chain: ... -> menu_0_3_13_patch.py -> 0.3.13 (= the tools/deploy_set.py SET pin,
generated - never re-run its patch, never re-build it) -> this patch -> 0.3.14. 0.3.13's files stay untouched. The harness
SkyyMenu/test_skyymenu_0.3.14.py is its own file (it runs test_skyymenu_0.3.13.py's checks on the new jar next to a control run = every
old check carried forward, plus the new sections).

0.3.14 = THE PETS TILE IN THE TOP BAR. Skyy's own words (2026-10-10): "add pets to the top bar of the menu by profile. (like everything
else, pets are per profile. they dont transfer.)"
  1. TILE: main slot 5 = right of Your Profile (slot 4) in the top row; action cmdc:pets = the Accessory Bag pattern (MenuPage.runCmd:
     /pets runs AS THE PLAYER with the menu still open - SkyyPets' page replaces the menu, the grid is emptied first; never a close
     before the page). HIDDEN (slot left empty, nothing else moves) unless SkyyPets is loaded: its bridge function pets:fn:onxp (SkyyPets
     0.1+ puts it in setup, takes it off at shutdown) AND a /pets command. Another mod's /pets alone never shows the tile.
  2. PER PROFILE (pets never transfer): the hover text is read from SkyyPets' OWN per-profile record, the file
     <mods>/Skyy_SkyyPets/pets/<storage key>.properties - the storage key = profile:fn:key (tools/PROFILES-CONTRACT.md, Given.key: <uuid>
     for profile 1 / no SkyyProfiles, <uuid>-p<N> for profile N). READ ONLY (never written, never locked: NIO opens with share-delete so
     SkyyPets' atomic replace still works), cached by (modified time, size), a file over 1 MB / without v=1 / unreadable = "could not be
     read". SkyyPets publishes no bridge key with the slotted pet (only pets:stats:<uuid> = numbers), so the record is the only per-profile
     source; it is the same file SkyyPets reads at join / profile switch (XP + level are flushed every pets.xp.flushSeconds = 30 s, slot
     changes at once).
     Title: "Pets - <pet name> Lv N" (the pet-slot pet: its pet.<id>.name if set, else the kind's display name "Void Eye"); "Pets" with
     no pet in the slot / no file / a bad file. Body (short lines, StatsCalc.LINE_MAX): "Your pets on this profile (<profile name>)",
     Pet slot, Summon slot (only when filled), Pets owned, "Pets stay on this profile", the command.
  3. ICON: the pet-slot pet's kind when we have its art: the 15 launch pet icons art/pets/.../SkyyPets_Pet_<Pet>.png (ART-RESUME Done #7,
     Skyy "Yes, the pets look good, commit them") ship as OUR icon-only items Skyy_Menu_Icon_Pet_<Pet> (the 0.3.11 ICON_ITEMS mechanism,
     hidden from the creative library) at Icons/ItemsGenerated/SkyyMenu_Pet_<Pet>.png - our own path, never SkyyPets' proposed
     SkyyPets_Pet_* ids / files. Any other kind, no pet, a bad file = the vanilla dog collar Farming_Collar. art/pets/manifest.json has no
     sha256: icon_item_png finds the manifest entry by the art file's path in its folder (same result for the bag) and checks bytes + the
     sha256 this patch pins from the committed files (ICON_SHA).
  4. ROUND_PINS = {} (deploys on its own; the 0.3.13 round is pinned in SET now - the Mods list version catch-up stays a later round).
  5. No saved data, no setting, no other tile moves (slot 5 was empty).
Every change below is recorded (CHANGES) and undone at the end to prove the generated script is 0.3.13 outside them, byte for byte.
"""
import os
import re
import ast
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.13.py")
dst = os.path.join(ROOT, "SkyyMenu", "build_skyymenu_0.3.14.py")
CR, LF = chr(13), chr(10)


def load(p):
    raw = open(p, encoding="utf8", newline="").read()
    return raw.replace(CR + LF, LF), (CR + LF if (CR + LF) in raw else LF)


s, NL = load(src)
OLD = s
assert 'VERSION = "0.3.13"' in s and "0.3.13: THE MONK SKILL IS ZEN" in s and "PetTile" not in s, "not the generated 0.3.13 script"
CHANGES = []            # (new text, old text) of every change, in order: undone at the end


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, "anchor count %d: %s" % (n, old[:120])
    s = s.replace(old, new, 1)
    CHANGES.append((new, old))


_set = None
for _n in ast.parse(open(os.path.join(ROOT, "tools", "deploy_set.py"), encoding="utf-8").read()).body:
    if isinstance(_n, ast.Assign) and any(isinstance(_t, ast.Name) and _t.id == "SET" for _t in _n.targets):
        _set = dict(ast.literal_eval(_n.value))
if _set is not None and _set.get("SkyyMenu") != "0.3.13":
    print("NOTE: tools/deploy_set.py SET pins SkyyMenu %s, this patch derives from 0.3.13" % _set.get("SkyyMenu"))
if _set is not None and _set.get("SkyyPets") != "0.2":
    print("NOTE: tools/deploy_set.py SET pins SkyyPets %s, this patch was checked against SkyyPets 0.2" % _set.get("SkyyPets"))

# ---- what the tile reads comes from SkyyPets 0.2 (the SET pin): fail the patch if that script stops working this way
_pt = open(os.path.join(ROOT, "SkyyPets", "build_skyypets_0.2.py"), encoding="utf8").read()
for _need in ('java.nio.file.Path mods = getDataDirectory().getParent();', '@PKG@.PetStore.ROOT = mods.resolve("Skyy_SkyyPets");',
              '@PKG@.PetStore.DIR = @PKG@.PetStore.ROOT.resolve("pets");', 'return DIR.resolve(key + ".properties");',
              '@PKG@.PetsLog.bridge().put("pets:fn:onxp", new @PKG@.PetXpFn());', 'super("pets", ', 'addAliases(new String[] { "pet" });',
              'String v = this.p.getProperty("active." + slot, "").trim();', 'this.p.getProperty(\\"pet.\\" + id + \\".kind\\")',
              'lv(\\"pet.\\" + id + \\".level\\", 1L)', 'long r = lv("pet." + id + ".rarity", 1L);', 'String n = r.get("pet." + id + ".name");',
              'else if (!v.trim().equals("1")) { r.bad = true;', 'F(pm, "public static final int MAX_LEVEL = 100;")',
              'RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]',
              'if (i > 0 && Character.isUpperCase(c) && Character.isLowerCase(id.charAt(i - 1))) b.append(\' \');'):
    assert _need in _pt, "SkyyPets 0.2 changed: %s" % _need
_kinds = re.findall(r'^\s*\("([A-Za-z]+)", "(?:Farming|Mining|Foraging|Combat|Exploration)", "', _pt, re.M)
assert len(_kinds) == 30 and "VoidEye" in _kinds, "the SkyyPets 0.2 roster: %s" % _kinds

# ---- the 15 launch pet icons (art/pets, committed; ART-RESUME Done #7)
PET_ART = ["Bear", "Boar", "Camel", "Chicken", "Goat", "Hawk", "Horse", "Mouflon", "Rabbit", "Ram", "Skrill", "Turkey", "Tusker",
           "Warthog", "Wolf"]
assert all(p in _kinds for p in PET_ART), "every pet icon is a SkyyPets kind"
ICON_SHA = {}
for _p in PET_ART:
    _f = os.path.join(ROOT, "art", "pets", "Common", "Icons", "ItemsGenerated", "SkyyPets_Pet_%s.png" % _p)
    ICON_SHA["Skyy_Menu_Icon_Pet_" + _p] = hashlib.sha256(open(_f, "rb").read()).hexdigest()

# ================================================================================================ docstring + version
rep('''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.13: THE MONK SKILL IS ZEN''', '''"""SkyyMenu 0.1 - build script (javassist via jpype).
0.3.14: THE PETS TILE IN THE TOP BAR (notes: tools/menu_0_3_14_patch.py; Skyy 2026-10-10 "add pets to the top bar of the menu by profile.
       (like everything else, pets are per profile. they dont transfer.)"): main slot 5 (right of Your Profile) runs /pets as the player
       (the Accessory Bag pattern); hidden unless SkyyPets is loaded (pets:fn:onxp + /pets). Hover "Pets - <pet> Lv N" + the pet slot,
       summon slot, pets owned - read from SkyyPets' own per-PROFILE record Skyy_SkyyPets/pets/<storage key>.properties (read only,
       cached by modified time + size). Icon = the pet-slot pet's art (15 launch pets, our icon items Skyy_Menu_Icon_Pet_<Pet>) else the
       vanilla Farming_Collar. ROUND_PINS = {}. No saved data, no other tile moves.
  CHECKED: see SkyyMenu/test_skyymenu_0.3.14.py (every 0.3.13 check carried forward + CC 0.3.13 -> 0.3.14 + PT the Pets tile flows).
0.3.13: THE MONK SKILL IS ZEN''')
rep('VERSION = "0.3.13"\n', 'VERSION = "0.3.14"\n')

# ================================================================================================ the pet icons (icon-only items)
rep('''ICON_BAG = "Skyy_Menu_Icon_AccessoryBag"      # 0.3.11: the Accessory Bag tile (Skyy 2026-10-08: "Yes, the bag icon looks good, commit it")
''', '''ICON_BAG = "Skyy_Menu_Icon_AccessoryBag"      # 0.3.11: the Accessory Bag tile (Skyy 2026-10-08: "Yes, the bag icon looks good, commit it")
# 0.3.14: THE PETS TILE's icons. The 15 launch pet icons (art/pets, ART-RESUME Done #7, Skyy "Yes, the pets look good, commit them") as OUR
# icon-only items Skyy_Menu_Icon_Pet_<Pet>, shipped under our own file name (never SkyyPets' proposed SkyyPets_Pet_* ids / files). The tile
# shows the pet-slot pet's kind; a kind without art, no pet or an unreadable pet file = ICON_PETS (the vanilla dog collar).
PET_ART = %s
ICON_SHA = %s     # art/pets/manifest.json has no sha256: pinned by tools/menu_0_3_14_patch.py from the committed files
for _p in PET_ART:
    ICON_ITEMS["Skyy_Menu_Icon_Pet_" + _p] = ("art/pets/Common/Icons/ItemsGenerated/SkyyPets_Pet_%%s.png" %% _p,
                                              "Icons/ItemsGenerated/SkyyMenu_Pet_%%s.png" %% _p, "art/pets/manifest.json", _p, "Farming_Collar")
ICON_PETS = "Farming_Collar"                  # 0.3.14: the Pets tile without a pet icon (vanilla Deco_Dog_Collar picture)
''' % (repr(PET_ART), repr(ICON_SHA)))
rep('''def icon_item_png(iid):
    """0.3.11: the icon item's PNG, checked: = its art manifest (sha256 + bytes), a 64 x 64 RGBA8 PNG"""
    import hashlib, struct
    art, rel, man, _nm, _look = ICON_ITEMS[iid]
    data = open(os.path.join(HERE, "..", *art.split("/")), "rb").read()
    ent = [f for f in json.load(open(os.path.join(HERE, "..", *man.split("/")), encoding="utf8"))["files"] if f["path"] == "Common/" + rel]
    assert len(ent) == 1 and hashlib.sha256(data).hexdigest() == ent[0]["sha256"] and len(data) == ent[0]["bytes"], \\
        "icon item %s: %s is not the art manifest's file" % (iid, art)''', '''def icon_item_png(iid):
    """0.3.11: the icon item's PNG, checked: = its art manifest (sha256 + bytes), a 64 x 64 RGBA8 PNG
    0.3.14: the manifest entry is the art file's path inside the manifest's folder (the bag: = Common/<rel>, as before; the pet icons
    ship under our own name); a manifest entry without sha256 (art/pets) is checked against ICON_SHA"""
    import hashlib, struct
    art, rel, man, _nm, _look = ICON_ITEMS[iid]
    data = open(os.path.join(HERE, "..", *art.split("/")), "rb").read()
    _mdir = man.rsplit("/", 1)[0] + "/"
    assert art.startswith(_mdir), "icon item %s: %s is not in its manifest's folder" % (iid, art)
    ent = [f for f in json.load(open(os.path.join(HERE, "..", *man.split("/")), encoding="utf8"))["files"] if f["path"] == art[len(_mdir):]]
    _sha = (ent[0].get("sha256") or ICON_SHA.get(iid)) if len(ent) == 1 else None
    assert len(ent) == 1 and _sha and hashlib.sha256(data).hexdigest() == _sha and len(data) == ent[0]["bytes"], \\
        "icon item %s: %s is not the art manifest's file" % (iid, art)''')

# ================================================================================================ the tile (main slot 5)
rep('''    ("main", 4,  "Armor_Iron_Head", "Your Profile", ["All your stats: health, mana, strength, crit, fortune, skills and more."],
        "Click to open your Stats page", "profile"),
''', '''    ("main", 4,  "Armor_Iron_Head", "Your Profile", ["All your stats: health, mana, strength, crit, fortune, skills and more."],
        "Click to open your Stats page", "profile"),
    # 0.3.14: Pets right of Your Profile (Skyy 2026-10-10 "add pets to the top bar of the menu by profile"). Drawn ONLY while SkyyPets is
    # loaded (PetTile.installed); name / text / icon come from the active PROFILE's pet record (PetTile) - this text is the fallback.
    ("main", 5,  ICON_PETS, "Pets", ["Your pets on this profile: the pet slot, the summon slot and every pet you own.",
                                     "Pets stay on this profile - every profile has its own.", "Command: /pets (or /pet)"],
        "Click to open!", "cmdc:pets"),
''')
rep('''assert [e[2] for e in ENTRIES if e[0] == "main" and e[1] == 12] == [ICON_BAG], "0.3.11: the Accessory Bag tile uses our icon item"
''', '''assert [e[2] for e in ENTRIES if e[0] == "main" and e[1] == 12] == [ICON_BAG], "0.3.11: the Accessory Bag tile uses our icon item"
# 0.3.14: the Pets tile right of Your Profile in the top row, /pets; every pet icon item shipped
assert [(e[3], e[6]) for e in ENTRIES if e[0] == "main" and e[1] in (4, 5)] == [("Your Profile", "profile"), ("Pets", "cmdc:pets")], "0.3.14: Pets at main 5"
assert all(("Skyy_Menu_Icon_Pet_" + _p) in ICON_ITEMS for _p in PET_ART) and len(ICON_ITEMS) == 1 + len(PET_ART), "0.3.14: the pet icon items"
assert all(files["Common/Icons/ItemsGenerated/SkyyMenu_Pet_%s.png" % _p] for _p in PET_ART), "0.3.14: the pet icons are in the jar"
''')

# ================================================================================================ MenuData: the kind -> icon table
rep('''F(dat, "public static final String[] E_ICON = %s;" % jarr(E_ICON))
''', '''F(dat, "public static final String[] E_ICON = %s;" % jarr(E_ICON))
# 0.3.14: the Pets tile - SkyyPets kind id -> our icon item, and the icon without one
F(dat, "public static final String[] PET_KIND = %s;" % jarr(PET_ART))
F(dat, "public static final String[] PET_ICON = %s;" % jarr(["Skyy_Menu_Icon_Pet_" + _p for _p in PET_ART]))
F(dat, "public static final String ICON_PETS = %s;" % jstr(ICON_PETS))
''')

# ================================================================================================ PetTile (new class)
rep('''stc  = mk("StatsCmd", T["APC"])
''', '''stc  = mk("StatsCmd", T["APC"])
pet  = mk("PetTile")        # 0.3.14: the Pets tile's name / text / icon from the active profile's SkyyPets record (read only)
''')
rep('''         scl, stp, sta, stc, pl)
''', '''         scl, stp, sta, stc, pet, pl)
''')
rep('''# ================= MenuPage (inline page; views switched with rebuild()) =================
''', '''# ================= PetTile (0.3.14): the Pets tile of the main menu =================
# Pets are per PROFILE and never transfer (Skyy 2026-10-10). SkyyPets 0.1+ keeps each profile's pets in <mods>/Skyy_SkyyPets/pets/<storage
# key>.properties (Properties text, v=1, active.1 / active.2 = pet ids, pet.<id>.kind / name / level / rarity); the storage key is
# profile:fn:key (Given.key). We only READ it (never write, never hold it open: NIO shares delete, SkyyPets' atomic replace works), on the
# menu's build, cached per key by (modified time, size). Result (String[10]): state ("ok" / "none" = no file / "bad" = unreadable, over
# 1 MB, no v=1 - SkyyPets refuses such a file too), pet slot kind / name / level / rarity, summon slot kind / name / level / rarity, owned.
F(pet, "public static volatile java.nio.file.Path DIR;")
F(pet, "public static final java.util.concurrent.ConcurrentHashMap CACHE = new java.util.concurrent.ConcurrentHashMap();")
F(pet, "public static final String[] RARITY = %s;" % jarr(["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic"]))
F(pet, "public static volatile long READS = 0L;")
M(pet, r"""
public static String[] empty(String state) {
  String[] a = new String[10];
  for (int i = 0; i < a.length; i++) a[i] = "";
  a[0] = state;
  a[9] = "0";
  return a;
}""")
# = SkyyPets' PetKind.display ("VoidEye" -> "Void Eye", "_" -> space), made safe for the tooltip
M(pet, r"""
public static String display(String id) {
  if (id == null) return "";
  StringBuilder b = new StringBuilder();
  for (int i = 0; i < id.length() && i < 40; i++) {
    char c = id.charAt(i);
    if (c == '_') { b.append(' '); continue; }
    if (i > 0 && Character.isUpperCase(c) && Character.isLowerCase(id.charAt(i - 1))) b.append(' ');
    b.append(c);
  }
  return @PKG@.MenuUtil.safe(b.toString()).trim();
}""")
# = SkyyPets' PetRec.lv (Long.parseLong of the trimmed text, else the default), clamped
M(pet, r"""
public static long num(java.util.Properties p, String k, long d, long lo, long hi) {
  long v = d;
  String s = p.getProperty(k);
  if (s != null) { try { v = Long.parseLong(s.trim()); } catch (Throwable t) { v = d; } }
  if (v < lo) v = lo;
  if (v > hi) v = hi;
  return v;
}""")
# one slot -> out[at] kind, out[at + 1] name (its own name if set, cut to 24 like SkyyPets' nameplate, else the kind's), [at + 2] level,
# [at + 3] rarity name. An id without a kind = an empty slot (SkyyPets' PetRec.active does the same).
M(pet, r"""
public static void fill(String[] out, int at, java.util.Properties p, String id0) {
  String id = id0 == null ? "" : id0.trim();
  if (id.length() == 0) return;
  String kind = p.getProperty("pet." + id + ".kind");
  if (kind == null || kind.trim().length() == 0) return;
  kind = kind.trim();
  String nm = p.getProperty("pet." + id + ".name");
  nm = nm == null ? "" : @PKG@.MenuUtil.safe(nm.trim()).trim();
  if (nm.length() > 24) nm = nm.substring(0, 24).trim();
  if (nm.length() == 0) nm = display(kind);
  out[at] = kind;
  out[at + 1] = nm;
  out[at + 2] = String.valueOf(num(p, "pet." + id + ".level", 1L, 1L, 100L));
  out[at + 3] = RARITY[(int) num(p, "pet." + id + ".rarity", 1L, 1L, 6L) - 1];
}""")
M(pet, r"""
public static String[] parse(java.util.Properties p) {
  String[] out = empty("ok");
  int n = 0;
  java.util.Iterator it = p.stringPropertyNames().iterator();
  while (it.hasNext()) {
    String k = (String) it.next();
    if (k.startsWith("pet.") && k.endsWith(".kind") && k.length() > 9) n++;
  }
  out[9] = String.valueOf(n);
  fill(out, 1, p, p.getProperty("active.1", ""));
  fill(out, 5, p, p.getProperty("active.2", ""));
  return out;
}""")
M(pet, r"""
public static String[] read(String key) {
  java.nio.file.Path d = DIR;
  if (d == null || !@PKG@.Given.validKey(key)) return empty("none");
  try {
    java.nio.file.Path f = d.resolve(key + ".properties");
    if (!java.nio.file.Files.exists(f, new java.nio.file.LinkOption[0])) { CACHE.remove(key); return empty("none"); }
    if (!java.nio.file.Files.isRegularFile(f, new java.nio.file.LinkOption[0])) return empty("bad");
    long mt = java.nio.file.Files.getLastModifiedTime(f, new java.nio.file.LinkOption[0]).toMillis();
    long sz = java.nio.file.Files.size(f);
    Object[] c = (Object[]) CACHE.get(key);
    if (c != null && ((Long) c[0]).longValue() == mt && ((Long) c[1]).longValue() == sz) return (String[]) c[2];
    String[] out;
    if (sz > 1048576L) out = empty("bad");
    else {
      byte[] b = java.nio.file.Files.readAllBytes(f);
      READS = READS + 1L;
      java.util.Properties p = new java.util.Properties();
      p.load(new java.io.ByteArrayInputStream(b));
      String v = p.getProperty("v");
      out = (v == null || !v.trim().equals("1")) ? empty("bad") : parse(p);
    }
    if (CACHE.size() > 2000) CACHE.clear();
    CACHE.put(key, new Object[] { Long.valueOf(mt), Long.valueOf(sz), out });
    return out;
  } catch (Throwable t) { return empty("bad"); }
}""")
# the ACTIVE profile's record (never the account: the storage key changes with the profile)
M(pet, r"""
public static String[] of(java.util.UUID u) {
  if (u == null) return empty("none");
  return read(@PKG@.Given.key(u));
}""")
# SkyyPets is loaded: its bridge function (setup .. shutdown) AND a /pets command (another mod's /pets alone never shows the tile)
M(pet, r"""
public static boolean installed() {
  try { return @PKG@.MenuUtil.bridge().get("pets:fn:onxp") != null && @PKG@.MenuUtil.cmd("pets") != null; }
  catch (Throwable t) { return false; }
}""")
M(pet, r"""
public static boolean has(String[] pi) {
  return pi != null && pi.length == 10 && "ok".equals(pi[0]) && pi[1].length() > 0;
}""")
M(pet, r"""
public static String title(String[] pi) {
  return has(pi) ? "Pets - " + pi[2] + " Lv " + pi[3] : "Pets";
}""")
M(pet, r"""
public static String icon(String[] pi) {
  if (!has(pi)) return @PKG@.MenuData.ICON_PETS;
  for (int i = 0; i < @PKG@.MenuData.PET_KIND.length; i++) if (@PKG@.MenuData.PET_KIND[i].equals(pi[1])) return @PKG@.MenuData.PET_ICON[i];
  return @PKG@.MenuData.ICON_PETS;
}""")
M(pet, r"""
public static String slotText(String[] pi, int at) {
  if (pi[at].length() == 0) return "empty";
  String kd = display(pi[at]);
  if (pi[at + 1].equals(kd)) return pi[at + 3] + " " + kd + " Lv " + pi[at + 2];
  return pi[at + 1] + " (" + pi[at + 3] + " " + kd + ") Lv " + pi[at + 2];
}""")
M(pet, r"""
public static String body(java.util.UUID u, String[] pi) {
  int max = @PKG@.StatsCalc.LINE_MAX;
  String pn = "";
  try {
    Object o = u == null ? null : @PKG@.MenuUtil.bridge().get("profile:name:" + u.toString());
    if (o instanceof String) pn = @PKG@.MenuUtil.safe((String) o).trim();
  } catch (Throwable t) { pn = ""; }
  if (pn.length() > 24) pn = pn.substring(0, 24).trim();
  StringBuilder sb = new StringBuilder();
  sb.append(@PKG@.MenuUtil.clip("Your pets on this profile" + (pn.length() > 0 ? " (" + pn + ")" : "") + ". Click to see them all.", max));
  if (pi == null || pi.length != 10 || "bad".equals(pi[0])) sb.append("\\nYour pet file could not be read. Ask an admin.");
  else {
    sb.append("\\n").append(@PKG@.MenuUtil.clip("Pet slot: " + slotText(pi, 1), max));
    if (pi[5].length() > 0) sb.append("\\n").append(@PKG@.MenuUtil.clip("Summon slot: " + slotText(pi, 5), max));
    sb.append("\\n").append(@PKG@.MenuUtil.clip("Pets owned: " + pi[9], max));
  }
  sb.append("\\nPets stay on this profile - every profile has its own.");
  sb.append("\\nCommand: /pets (or /pet)");
  return sb.toString();
}""")

# ================= MenuPage (inline page; views switched with rebuild()) =================
''')

# ================================================================================================ MenuPage.fillStatic: the tile
rep('''    String name = @PKG@.MenuData.E_NAME[i];
    String body = @PKG@.MenuData.E_BODY[i];
    if ("profile".equals(act)) body = profileBody();
''', '''    String name = @PKG@.MenuData.E_NAME[i];
    String body = @PKG@.MenuData.E_BODY[i];
    String icon = @PKG@.MenuData.E_ICON[i];
    if ("profile".equals(act)) body = profileBody();
    if ("cmdc:pets".equals(act)) {
      if (!@PKG@.PetTile.installed()) continue;
      String[] pi = @PKG@.PetTile.of(me);
      name = @PKG@.PetTile.title(pi);
      body = @PKG@.PetTile.body(me, pi);
      icon = @PKG@.PetTile.icon(pi);
    }
''')
rep('''      put(slots, @PKG@.MenuData.E_SLOT[i], @PKG@.MenuData.E_ICON[i], name + " (update needed)", body''',
    '''      put(slots, @PKG@.MenuData.E_SLOT[i], icon, name + " (update needed)", body''')
rep('''    put(slots, @PKG@.MenuData.E_SLOT[i], @PKG@.MenuData.E_ICON[i], name + (dim ? " (not installed)" : ""), body,''',
    '''    put(slots, @PKG@.MenuData.E_SLOT[i], icon, name + (dim ? " (not installed)" : ""), body,''')

# ================================================================================================ plugin setup: SkyyPets' record folder
rep('''  @PKG@.Tips.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("notips");
''', '''  @PKG@.Tips.DIR = getDataDirectory().resolveSibling("Skyy_SkyyMenu").resolve("notips");
  @PKG@.PetTile.DIR = getDataDirectory().resolveSibling("Skyy_SkyyPets").resolve("pets");
''')

# ================================================================================================ ROUND_PINS + the patch name
rep('''# tools/menu_0_3_13_patch.py ROUND). If one of them does not ship, set its MODS_VERSIONS entry back and drop it here.
ROUND_PINS = {'SkyyClasses': ('0.1.14', '0.1.15'), 'SkyyProfiles': ('0.1.7', '0.1.8'), 'SkyySkills': ('0.4.26', '0.4.27'), 'SkyyTrees': ('0.3.4', '0.3.5')}
''', '''# tools/menu_0_3_13_patch.py ROUND). If one of them does not ship, set its MODS_VERSIONS entry back and drop it here.
# 0.3.14: EMPTY - deploys on its own (the Pets tile reads SkyyPets 0.2's records, already the SET pin). 0.3.13's round is pinned in SET now.
ROUND_PINS = {}
''')
rep('_PATCH = "tools/menu_0_3_13_patch.py"', '_PATCH = "tools/menu_0_3_14_patch.py"')

# ================================================================================================ checks on the result
assert "@@" not in s, "a @@ token is left in the generated script"
_u = s
for _new, _old in reversed(CHANGES):
    assert _u.count(_new) == 1, "a change is not unique any more: %s" % _new[:80]
    _u = _u.replace(_new, _old, 1)
assert _u == OLD, "the generated script differs from 0.3.13 outside the recorded changes"
assert s.index('pet  = mk("PetTile")') < s.index("public static String[] empty(String state)") < s.index("public static String body(java.util.UUID u, String[] pi)") \
    < s.index("public void fillStatic(java.util.ArrayList slots)") < s.index("@PKG@.PetTile.DIR = "), "methods before callers"
assert s.index("F(scl, \"public static final int LINE_MAX") < s.index("public static String body(java.util.UUID u, String[] pi)"), "LINE_MAX first"
assert s.index("ICON_ITEMS = {") < s.index("for _p in PET_ART:") < s.index("def icon_item_png(iid):"), "the icon items before their check"
compile(s, dst, "exec")
open(dst, "w", encoding="utf8", newline="").write(s.replace(LF, NL) if NL != LF else s)
print("wrote", os.path.relpath(dst, ROOT), "(%d lines; 0.3.13 had %d; %d changes)" % (s.count(LF), OLD.count(LF), len(CHANGES)))
